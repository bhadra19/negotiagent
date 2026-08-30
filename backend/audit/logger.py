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

    def _connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)

    def log(self, negotiation_id: str, event_type: str, payload: dict[str, Any]) -> None:
        with self._connection() as connection:
            connection.execute("INSERT INTO audit_events (created_at, event_type, negotiation_id, payload_json) VALUES (?, ?, ?, ?)", (datetime.now(timezone.utc).isoformat(), event_type, negotiation_id, json.dumps(payload, sort_keys=True)))

    def list_events(self, negotiation_id: str) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute("SELECT created_at, event_type, payload_json FROM audit_events WHERE negotiation_id = ? ORDER BY id", (negotiation_id,)).fetchall()
        return [{"created_at": row[0], "event_type": row[1], "payload": json.loads(row[2])} for row in rows]

