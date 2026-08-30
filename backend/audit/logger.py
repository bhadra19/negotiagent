import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class AuditLogger:
    def __init__(self, database_path: str):
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        self.database_path = database_path
        with self._connection() as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS audit_events (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, event_type TEXT NOT NULL, negotiation_id TEXT NOT NULL, payload_json TEXT NOT NULL)")
            connection.execute("CREATE TABLE IF NOT EXISTS approved_offers (negotiation_id TEXT PRIMARY KEY, vendor_id TEXT NOT NULL, unit_price REAL NOT NULL, quantity INTEGER NOT NULL, total_price REAL NOT NULL, currency TEXT NOT NULL)")

    def _connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)

    def log(self, negotiation_id: str, event_type: str, payload: dict[str, Any]) -> None:
        with self._connection() as connection:
            connection.execute("INSERT INTO audit_events (created_at, event_type, negotiation_id, payload_json) VALUES (?, ?, ?, ?)", (datetime.now(timezone.utc).isoformat(), event_type, negotiation_id, json.dumps(payload, sort_keys=True)))

    def list_events(self, negotiation_id: str) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute("SELECT created_at, event_type, payload_json FROM audit_events WHERE negotiation_id = ? ORDER BY id", (negotiation_id,)).fetchall()
        return [{"created_at": row[0], "event_type": row[1], "payload": json.loads(row[2])} for row in rows]

    def save_approved_offer(self, negotiation_id: str, offer: Any) -> None:
        with self._connection() as connection:
            connection.execute("INSERT OR REPLACE INTO approved_offers (negotiation_id, vendor_id, unit_price, quantity, total_price, currency) VALUES (?, ?, ?, ?, ?, ?)", (negotiation_id, offer.vendor_id, offer.unit_price, offer.quantity, offer.total_price, offer.currency))

    def get_approved_offer(self, negotiation_id: str) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute("SELECT vendor_id, unit_price, quantity, total_price, currency FROM approved_offers WHERE negotiation_id = ?", (negotiation_id,)).fetchone()
        if row is None:
            return None
        return {"vendor_id": row[0], "unit_price": row[1], "quantity": row[2], "total_price": row[3], "currency": row[4]}
