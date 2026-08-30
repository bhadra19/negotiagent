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
            connection.execute("CREATE TABLE IF NOT EXISTS payment_attempts (id INTEGER PRIMARY KEY AUTOINCREMENT, negotiation_id TEXT NOT NULL, idempotency_key TEXT NOT NULL UNIQUE, attempt_number INTEGER NOT NULL, status TEXT NOT NULL, order_id TEXT, amount_subunits INTEGER, currency TEXT, failure_reason TEXT)")

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

    def start_payment_attempt(self, negotiation_id: str, idempotency_key: str) -> dict[str, Any]:
        with self._connection() as connection:
            existing = connection.execute("SELECT attempt_number, status, order_id, amount_subunits, currency FROM payment_attempts WHERE idempotency_key = ?", (idempotency_key,)).fetchone()
            if existing:
                return {"created": False, "attempt_number": existing[0], "status": existing[1], "order_id": existing[2], "amount_subunits": existing[3], "currency": existing[4]}
            attempt_number = connection.execute("SELECT COALESCE(MAX(attempt_number), 0) + 1 FROM payment_attempts WHERE negotiation_id = ?", (negotiation_id,)).fetchone()[0]
            connection.execute("INSERT INTO payment_attempts (negotiation_id, idempotency_key, attempt_number, status) VALUES (?, ?, ?, ?)", (negotiation_id, idempotency_key, attempt_number, "pending"))
        self.log(negotiation_id, "payment_attempt_started", {"attempt_number": attempt_number})
        return {"created": True, "attempt_number": attempt_number, "status": "pending", "order_id": None, "amount_subunits": None, "currency": None}

    def complete_payment_attempt(self, idempotency_key: str, order_id: str, amount_subunits: int, currency: str) -> None:
        with self._connection() as connection:
            connection.execute("UPDATE payment_attempts SET status = ?, order_id = ?, amount_subunits = ?, currency = ? WHERE idempotency_key = ?", ("created", order_id, amount_subunits, currency, idempotency_key))

    def fail_payment_attempt(self, idempotency_key: str, reason: str) -> None:
        with self._connection() as connection:
            connection.execute("UPDATE payment_attempts SET status = ?, failure_reason = ? WHERE idempotency_key = ?", ("failed", reason, idempotency_key))

    def list_payment_attempts(self, negotiation_id: str) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute("SELECT attempt_number, status, order_id, amount_subunits, currency, failure_reason FROM payment_attempts WHERE negotiation_id = ? ORDER BY attempt_number", (negotiation_id,)).fetchall()
        return [{"attempt_number": row[0], "status": row[1], "order_id": row[2], "amount_subunits": row[3], "currency": row[4], "failure_reason": row[5]} for row in rows]
