"""
ModelManager - coordinates backbone + local heads, handles save/load.
The serialiser only ever exports backbone weights (never local head).
"""
from __future__ import annotations

import gzip
import json
import logging
from pathlib import Path

import numpy as np
import torch

from rl.backbone import BackboneEncoder
from rl.local_head import ItemHead, PriceHead, NudgeHead

log = logging.getLogger("fedrl.model")

CONTEXT_DIM = 28  # Must match ContextExtractor output length


class ModelManager:
    def __init__(
        self,
        backbone_dim: int = 32,
        algorithm: str = "thompson_sampling",
        weights_dir: str = "/app/data",
        cold_start_recs: int = 8,
    ):
        self.backbone_dim = backbone_dim
        self.algorithm = algorithm
        self.weights_dir = Path(weights_dir)
        self.backbone_version: str = "0"

        self.backbone = BackboneEncoder(input_dim=CONTEXT_DIM, latent_dim=backbone_dim)
        self.item_head = ItemHead(latent_dim=backbone_dim)
        self.price_head = PriceHead()
        self.nudge_head = NudgeHead(cold_start_recs=cold_start_recs)

        self._load_from_disk()

    # Inference
    def recommend(
        self, context_vec: list[float], alternatives: list[dict]
    ) -> dict | None:
        """
        Given a context vector and candidate alternatives, return the best
        (alternative, nudge_type) action tuple.
        """
        if not alternatives:
            return None

        embedding = self.backbone.encode(context_vec).numpy()
        nudge = self.nudge_head.select_nudge()
        price_offset = 0.0

        best_item = None
        best_score = float("-inf")

        for alt in alternatives:
            score = self.item_head.sample_score(alt["id"], embedding)
            # Price sensitivity offset
            price_delta = alt.get("price", 0.0) - context_vec[3] if len(context_vec) > 3 else 0.0
            p_offset = self.price_head.price_offset(price_delta)
            total = score + p_offset
            if total > best_score:
                best_score = total
                best_item = alt
                price_offset = p_offset

        return {
            "alternative": best_item,
            "nudge_type": nudge,
            "score": best_score,
        }

    # Update
    def update(
        self,
        context_vec: list[float],
        chosen_item_id: str,
        nudge_type: str,
        reward: float,
    ):
        embedding = self.backbone.encode(context_vec).numpy()
        price_delta = context_vec[3] if len(context_vec) > 3 else 0.0

        self.item_head.update(chosen_item_id, embedding, reward)
        self.price_head.update(price_delta, reward)
        self.nudge_head.update(nudge_type, reward)
        self._save_local_head()

    # Serialisation (backbone only — for federation)
    def backbone_payload(self, n_k: int, client_id: str) -> bytes:
        """
        Serialise ONLY backbone weights + interaction count to gzip+JSON bytes.
        Local head is NEVER included. (FR-4.5, NFR-5)
        """
        state = {k: v.tolist() for k, v in self.backbone.state_dict().items()}
        payload = {
            "client_id": client_id,
            "backbone_version": self.backbone_version,
            "interaction_count": n_k,
            "algorithm": self.algorithm,
            "backbone_weights": state,
        }
        return gzip.compress(json.dumps(payload).encode())

    def load_global_backbone(self, data: bytes, new_version: str):
        """Replace backbone weights from server payload. Local head untouched."""
        payload = json.loads(gzip.decompress(data))
        state = {k: torch.tensor(v) for k, v in payload["backbone_weights"].items()}
        self.backbone.load_state_dict(state)
        self.backbone_version = new_version
        self._save_backbone()
        log.info("Loaded global backbone version %s", new_version)

    # Persistence
    def _save_backbone(self):
        path = self.weights_dir / "backbone.pt"
        torch.save({
            "version": self.backbone_version,
            "state_dict": self.backbone.state_dict(),
        }, path)

    def _save_local_head(self):
        path = self.weights_dir / "local_head.json"
        data = {
            "item_head": self.item_head.state_dict(),
            "price_head": self.price_head.state_dict(),
            "nudge_head": self.nudge_head.state_dict(),
        }
        path.write_text(json.dumps(data))

    def _load_from_disk(self):
        backbone_path = self.weights_dir / "backbone.pt"
        if backbone_path.exists():
            ckpt = torch.load(backbone_path, map_location="cpu")
            self.backbone.load_state_dict(ckpt["state_dict"])
            self.backbone_version = ckpt.get("version", "0")
            log.info("Loaded backbone version %s", self.backbone_version)

        local_head_path = self.weights_dir / "local_head.json"
        if local_head_path.exists():
            data = json.loads(local_head_path.read_text())
            self.item_head.load_state_dict(data["item_head"])
            self.price_head.load_state_dict(data["price_head"])
            self.nudge_head.load_state_dict(data["nudge_head"])
            log.info("Loaded local head from disk")

