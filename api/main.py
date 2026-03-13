"""
FedRL Client — FastAPI backend
Serves JSON endpoints only; Vue frontend handles all rendering.
"""
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from dataclasses import asdict

import uvicorn
import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dataclasses import dataclass, field

from rl.model_manager import ModelManager
from rl.context import ContextExtractor
from rl.reward import compute_reward
from rl.candidates import CandidateGenerator
from nudges.nudge_renderer import NudgeRenderer
from storage.catalogue import Catalogue
from storage.models import FoodCategory, FoodItem, SubstitutionGroup
from storage.interaction_logger import InteractionLogger
from sync.sync_agent import SyncAgent

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s %(message)s")
log = logging.getLogger("fedrl.api")

# Config
with open("/app/config/client.yaml") as f:
    cfg = yaml.safe_load(f)

CLIENT_ID: str = cfg["client_id"]
API_VERSION: str = cfg.get("api_version", "v1")
SERVER_URL: str = cfg["server_url"] + "/api/" + API_VERSION
ALGORITHM: str = cfg.get("algorithm", "thompson_sampling")
COLD_START_RECS: int = cfg.get("model", {}).get("cold_start_recs", 8)
BACKBONE_DIM: int = cfg.get("model", {}).get("backbone_dim", 32)


# Singletons
catalogue = Catalogue(server_url=SERVER_URL)
logger_db = InteractionLogger(db_path="/app/data/interactions.db")
model_mgr = ModelManager(
    backbone_dim=BACKBONE_DIM,
    algorithm=ALGORITHM,
    weights_dir="/app/data",
    cold_start_recs=COLD_START_RECS,
)
context_extractor = ContextExtractor(catalogue)
n_candidate_generator = CandidateGenerator(catalogue)
nudge_renderer = NudgeRenderer()
sync_agent = SyncAgent(
    server_url=SERVER_URL,
    client_id=CLIENT_ID,
    model_manager=model_mgr,
    interaction_logger=logger_db,
    min_n_interactions_threshold=cfg.get("sync", {}).get("min_n_interactions", 1),
    n_interactions_threshold=cfg.get("sync", {}).get("n_interactions", 10),
    t_seconds_threshold=cfg.get("sync", {}).get("t_seconds", 300),
)


# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting client %s (algorithm=%s)", CLIENT_ID, ALGORITHM)
    await catalogue.fetch(fallback_to_cache=True)
    await sync_agent.check_for_newer_backbone()
    asyncio.create_task(sync_agent.run_loop())
    yield
    log.info("Shutting down — attempting final backbone upload")
    await sync_agent.upload_backbone(reason="graceful_shutdown")


# App
app = FastAPI(title=f"FedRL Client {CLIENT_ID}", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Schemas
@dataclass
class InteractionBody:
    item_id: str
    substitute_id: str
    nudge_type: str  # N1 | N2 | N3 | N4
    action: str      # accept | dismiss | ignore

@dataclass
class CartItem:
    item: FoodItem
    quantity: int

@dataclass
class AddItemBody:
    item_id: str
    quantity: int = 1


# In-memory cart (per session)
_cart: list[CartItem] = []


def _build_cart_item(item_id: str, quantity: int) -> CartItem:
    item = catalogue.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id!r} not found")
    return CartItem(item=item, quantity=quantity)


@app.on_event("startup")
async def prepopulate_cart():
    """Pre-populate cart with a fixed item set if configured."""
    global _cart
    if cfg.get("ui", {}).get("session_prepopulate", True):
        seed_ids = cfg.get("ui", {}).get("seed_item_ids", [])
        # Fallback: take first 5 catalogue items
        if not seed_ids:
            all_items = catalogue.get_all_items()
            seed_ids = [item["id"] for item in all_items[:5]]
        _cart = [CartItem(item=catalogue.get_item(iid), quantity=1) for iid in seed_ids if catalogue.get_item(iid) is not None]
        log.info("Cart pre-populated with %d items", len(_cart))


# Endpoints
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "client_id": CLIENT_ID,
        "algorithm": ALGORITHM,
        "catalogue_version": catalogue.version,
        "catalogue_size": len(catalogue.get_all_items()),
    }


@app.get("/cart")
async def get_cart():
    enriched = []
    if not _cart:
        return {"items": enriched, "client_id": CLIENT_ID}

    # For now, compute a recommendation for only one cart item.
    # If the first item has no eligible substitutes, fall back to the next, etc.
    recommended_idx: int | None = None
    widget_for_idx: dict | None = None

    for idx, cart_item in enumerate(_cart):
        candidates = n_candidate_generator.generate(cart_item.item.id)
        if not candidates:
            continue

        candidate_ids = [cid for cid, _ in candidates]
        contexts = [
            context_extractor.build(cart_item.item.id, cid, _cart, similarity_score=score)
            for cid, score in candidates
        ]
        rec = model_mgr.recommend(contexts, candidate_ids)
        if not rec:
            continue

        widget_for_idx = nudge_renderer.render(rec, cart_item.item, catalogue)
        recommended_idx = idx
        break

    for idx, cart_item in enumerate(_cart):
        item_dict = asdict(cart_item.item)
        widget = widget_for_idx if recommended_idx is not None and idx == recommended_idx else None
        enriched.append({**item_dict, "quantity": cart_item.quantity, "recommendation": widget})
    return {"items": enriched, "client_id": CLIENT_ID}


@app.post("/cart/add")
async def add_to_cart(body: AddItemBody):
    global _cart
    existing = next((i for i in _cart if i.item.id == body.item_id), None)
    if existing:
        existing.quantity += body.quantity
    else:
        _cart.append(_build_cart_item(body.item_id, body.quantity))
    return {"ok": True, "cart_size": len(_cart)}


@app.delete("/cart/{item_id}")
async def remove_from_cart(item_id: str):
    global _cart
    _cart = [i for i in _cart if i.item.id != item_id]
    return {"ok": True}


@app.get("/catalogue")
async def get_catalogue(category_id: str | None = None):
    items = catalogue.get_all_items()
    if category_id:
        items = [i for i in items if i.category_id == category_id]
    return {"items": items, "version": catalogue.version}


@app.get("/catalogue/categories")
async def get_categories():
    # Use the new Catalogue API to expose full category objects
    categories = catalogue.get_all_categories()
    # Convert dataclasses to plain dicts for JSON response
    payload = [
        {
            "id": c.id,
            "code": c.code,
            "name": c.name,
        }
        for c in categories
    ]
    return {"categories": payload, "version": catalogue.version}


@app.post("/interact")
async def record_interaction(body: InteractionBody):
    ctx = context_extractor.build(body.item_id, _cart)
    reward = compute_reward(body.action)
    model_mgr.update(ctx, body.substitute_id, body.nudge_type, reward)
    context_extractor.record_outcome(body.action, reward)
    logger_db.log(
        context=ctx,
        item_id=body.item_id,
        alternative_id=body.substitute_id,
        nudge_type=body.nudge_type,
        action=body.action,
        reward=reward,
    )

    # If action was accept — swap item in cart
    if body.action == "accept":
        for ci in _cart:
            if ci["id"] == body.item_id:
                replacement = catalogue.get_item(body.substitute_id)
                if replacement:
                    ci.update({**replacement, "quantity": ci["quantity"]})
                break

    await sync_agent.maybe_trigger_upload()
    return {"ok": True, "reward": reward}


@app.get("/stats")
async def get_stats():
    return {
        "interactions_total": logger_db.total_count(),
        "interactions_since_sync": logger_db.count_since_last_sync(),
        "last_sync": sync_agent.last_sync_time,
        "backbone_version": model_mgr.backbone_version,
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)