"""
InteractionLogger - on-device SQLite store for interaction tuples.
Raw data NEVER leaves the device (NFR-4).
Only n_k (interaction count) is transmitted for FedAvg weighting.
"""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path


class InteractionLogger:
    def __init__(self, db_path: str = "/app/data/interactions.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts REAL NOT NULL,
                    context TEXT NOT NULL,
                    item_id TEXT NOT NULL,
                    alternative_id TEXT NOT NULL,
                    nudge_type TEXT NOT NULL,
                    action TEXT NOT NULL,
                    reward REAL NOT NULL,
                    synced INTEGER DEFAULT 0
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_synced ON interactions(synced)")

    def log(
        self,
        context: list[float],
        item_id: str,
        alternative_id: str,
        nudge_type: str,
        action: str,
        reward: float,
    ):
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO interactions
                  (ts, context, item_id, alternative_id, nudge_type, action, reward)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    time.time(),
                    json.dumps(context),
                    item_id,
                    alternative_id,
                    nudge_type,
                    action,
                    reward,
                ),
            )

    def count_since_last_sync(self) -> int:
        with self._conn() as conn:
            row = conn.execute("SELECT COUNT(*) FROM interactions WHERE synced=0").fetchone()
            return row[0]

    def total_count(self) -> int:
        with self._conn() as conn:
            row = conn.execute("SELECT COUNT(*) FROM interactions").fetchone()
            return row[0]

    def mark_synced(self):
        with self._conn() as conn:
            conn.execute("UPDATE interactions SET synced=1 WHERE synced=0")

    def training_tuples(self, limit: int = 500) -> list[dict]:
        """Provide recent tuples for local model training (never transmitted)."""
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT context, item_id, alternative_id, nudge_type, action, reward
                FROM interactions
                ORDER BY ts DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            {
                "context": json.loads(r[0]),
                "item_id": r[1],
                "alternative_id": r[2],
                "nudge_type": r[3],
                "action": r[4],
                "reward": r[5],
            }
            for r in rows
        ]