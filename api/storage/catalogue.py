"""
Catalogue - fetches the food catalogue from server at session start,
caches to disk for degraded-mode operation (FR-1.7).
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from datetime import datetime, timezone

import httpx

from storage.models import FoodCategory, FoodItem, SubstitutionGroup

log = logging.getLogger("fedrl.catalogue")

SNAPSHOT_PATH = Path("/app/data/catalogue_snapshot.json")


class Catalogue:
    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip("/")
        self.version: str = "1970-01-01T00:00:00Z"
        self._items: dict[str, FoodItem] = {}                           # id → item
        self._categories: dict[str, FoodCategory] = {}                  # id → category
        self._substitution_groups: dict[str, SubstitutionGroup] = {}    # id → substitution group

    # Public entrypoint: ensure we have an up-to-date catalogue snapshot.
    async def fetch(self, fallback_to_cache: bool = True):
        log.info("Checking catalogue version at %s/catalogue/version", self.server_url)
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                server_version = await self._fetch_server_version(client)

                if self._is_server_newer(server_version):
                    await self._refresh_from_server(client, server_version)
                else:
                    self._load_from_cache_if_available()
        except Exception as exc:
            log.warning("Catalogue fetch failed: %s", exc)
            if fallback_to_cache and SNAPSHOT_PATH.exists():
                snapshot = json.loads(SNAPSHOT_PATH.read_text())
                self._ingest(snapshot)
                log.info("Using cached catalogue: %d items (v%s)", len(self._items), self.version)
            else:
                log.error("No catalogue available - degraded mode with empty catalogue")

    # Fetch catalogue version string from server.
    async def _fetch_server_version(self, client: httpx.AsyncClient) -> str:
        resp = await client.get(f"{self.server_url}/catalogue/version")
        resp.raise_for_status()
        return str(resp.json().get("version", self.version))

    # Returns True if server catalogue version is newer than local.
    def _is_server_newer(self, server_version: str) -> bool:
        local_ts = self._parse_iso(self.version)
        server_ts = self._parse_iso(server_version)
        return server_ts > local_ts

    # Fetch fresh snapshot from server and persist it.
    async def _refresh_from_server(self, client: httpx.AsyncClient, server_version: str) -> None:
        log.info(
            "Newer catalogue available: local v%s → server v%s",
            self.version,
            server_version,
        )
        snap_resp = await client.get(f"{self.server_url}/catalogue/snapshot")
        snap_resp.raise_for_status()
        snapshot = snap_resp.json()
        self._ingest(snapshot)
        SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
        SNAPSHOT_PATH.write_text(json.dumps(snapshot))
        log.info("Catalogue fetched: %d items (v%s)", len(self._items), self.version)

    # Load catalogue from local snapshot file if present.
    def _load_from_cache_if_available(self) -> None:
        log.info("Catalogue up to date (v%s) — using cached snapshot", self.version)
        if SNAPSHOT_PATH.exists():
            snapshot = json.loads(SNAPSHOT_PATH.read_text())
            self._ingest(snapshot)
        else:
            log.warning("No cached snapshot found; catalogue remains as is")

    # Ingest the catalogue snapshot into the catalogue object
    def _ingest(self, snapshot: dict):
        self.version = snapshot["version"]

        for cat in snapshot["categories"]:
            self._categories[cat["id"]] = FoodCategory(**cat)
        for item in snapshot["items"]:
            self._items[item["id"]] = FoodItem(**{k: v for k, v in item.items() if k in FoodItem.__dataclass_fields__})
        for sg in snapshot["substitution_groups"]:
            g = sg["group"]
            items = sg.get("items", [])
            self._substitution_groups[g["id"]] = SubstitutionGroup(
                id=g["id"],
                code=g["code"],
                name=g["name"],
                items=items,
                description=g.get("description"),
            )

    # Returns the version of the catalogue snapshot
    def get_version(self) -> str:
        return self.version

    # Returns a list of all FoodItems
    def get_all_items(self) -> list[FoodItem]:
        return list(self._items.values())

    # Returns a FoodItem by its id
    def get_item(self, item_id: str) -> FoodItem:
        return self._items[item_id]

    # Returns a list of all FoodCategories
    def get_all_categories(self) -> list[FoodCategory]:
        return list(self._categories.values())

    # Returns a list of FoodItems that belong to the given category
    def get_category_items(self, category_id: int) -> list[FoodItem]:
        return [item for item in self._items.values() if item.category_id == category_id] if category_id in self._categories else []

    # Returns a list of all SubstitutionGroups
    def get_all_substitution_groups(self) -> list[SubstitutionGroup]:
        return list(self._substitution_groups.values())

    # Returns a list of FoodItems that are substitutes for the given item.
    def get_substitutes(self, item_id: str) -> list[FoodItem]:
        substitutes: list[FoodItem] = []
        for group in self._substitution_groups.values():
            if item_id in group.items:
                substitutes += [
                    self._items[id] for id in group.items
                    if id != item_id and id in self._items
                ]
        return substitutes

    # Util: Parse ISO 8601 timestamp, handling 'Z' suffix as UTC.
    def _parse_iso(self, ts: str) -> datetime:
        if ts.endswith("Z"):
            ts = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(ts)