"""
SyncAgent - background asyncio task managing backbone federation.
Uploads: POST /fl/upload  (backbone weights + n_k, gzip+JSON)
Downloads: GET  /fl/model?since={version}

Upload triggers (FR-4.3):
  - n_k >= N_interactions  OR  elapsed >= T_seconds
  - On app launch: check for newer backbone
  - On graceful close: final upload attempt

Local head is NEVER included in any payload (FR-4.5, NFR-5).
"""
from __future__ import annotations

import asyncio
import logging
import time
import base64
import gzip
import json
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from rl.model_manager import ModelManager
    from storage.interaction_logger import InteractionLogger

log = logging.getLogger("fedrl.sync")

BACKOFF_SEQUENCE = [5, 15, 30, 60, 120]  # seconds (FR-4.6)


class SyncAgent:
    def __init__(
        self,
        server_url: str,
        client_id: str,
        model_manager: "ModelManager",
        interaction_logger: "InteractionLogger",
        n_interactions_threshold: int = 10,
        t_seconds_threshold: int = 300,
    ):
        self.server_url = server_url.rstrip("/")
        self.client_id = client_id
        self.model_manager = model_manager
        self.interaction_logger = interaction_logger
        self.n_interactions_threshold = n_interactions_threshold
        self.t_seconds_threshold = t_seconds_threshold
        self.last_sync_time: float | None = None
        self._uploading = False

    # Public API
    async def run_loop(self):
        """Background poll loop - runs for the lifetime of the app."""
        log.info("Sync agent started (N=%d, T=%ds)", self.n_interactions_threshold, self.t_seconds_threshold)
        while True:
            await asyncio.sleep(5)
            await self.maybe_trigger_upload()

    async def maybe_trigger_upload(self):
        if self._uploading:
            return
        n_k = self.interaction_logger.count_since_last_sync()
        elapsed = (time.time() - self.last_sync_time) if self.last_sync_time else float("inf")
        if n_k >= self.n_interactions_threshold or elapsed >= self.t_seconds_threshold:
            await self.upload_backbone(reason="threshold_reached")

    async def check_for_newer_backbone(self):
        """Called on app launch (FR-4.4)."""
        local_version = self.model_manager.backbone_version
        url = f"{self.server_url}/fl/model?since={local_version}"
        try:
            log.info("Checking for newer backbone at %s", url)
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    server_version = data.get("version", 0)
                    if server_version != local_version:
                        log.info("Newer backbone available: %s → %s", local_version, server_version)
                        log.info(data)
                        payload_weights_compressed = base64.b64decode(data["backbone_weights"]) 
                        payload_weights = gzip.decompress(payload_weights_compressed)
                        weights_dict = json.loads(payload_weights.decode("utf-8"))
                        self.model_manager.load_global_backbone(weights_dict, server_version)
                elif resp.status_code == 304:
                    log.info("Backbone up to date (version %s)", local_version)
        except Exception as exc:
            log.warning("Could not check backbone version: %s", exc)

    async def upload_backbone(self, reason: str = "trigger"):
        """POST backbone weights to server with exponential backoff."""
        self._uploading = True
        n_k = self.interaction_logger.count_since_last_sync()
        payload = self.model_manager.backbone_payload(n_k, self.client_id)

        for attempt, backoff in enumerate(BACKOFF_SEQUENCE + [None]):
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    resp = await client.post(
                        f"{self.server_url}/fl/upload",
                        content=payload,
                        headers={
                            "Content-Type": "application/octet-stream",
                            "X-Client-ID": self.client_id,
                            "X-Backbone-Version": self.model_manager.backbone_version,
                            "X-Reason": reason,
                        },
                    )
                    resp.raise_for_status()
                    self.last_sync_time = time.time()
                    self.interaction_logger.mark_synced()
                    log.info("Backbone uploaded (n_k=%d, reason=%s)", n_k, reason)
                    # After upload, check if server has a newer aggregated model
                    await self.check_for_newer_backbone()
                    break
            except Exception as exc:
                log.warning("Upload failed (attempt %d): %s", attempt + 1, exc)
                if backoff is None:
                    log.error("Upload abandoned after %d attempts", len(BACKOFF_SEQUENCE) + 1)
                    break
                await asyncio.sleep(backoff)
        self._uploading = False