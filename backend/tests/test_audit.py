from audit.logger import AuditLogger
from agents.vendor_agents import Offer


def test_audit_events_are_persisted_in_order(tmp_path):
    logger = AuditLogger(str(tmp_path / "audit.db"))
    logger.log("neg-1", "started", {"quantity": 2})
    logger.log("neg-1", "completed", {"selected": "atlas-office"})
    events = logger.list_events("neg-1")
    assert [event["event_type"] for event in events] == ["started", "completed"]
    assert events[0]["payload"]["quantity"] == 2


def test_approved_offer_can_be_retrieved_for_payment_validation(tmp_path):
    logger = AuditLogger(str(tmp_path / "audit.db"))
    logger.save_approved_offer("neg-1", Offer("atlas-office", 96, 2, 4))
    offer = logger.get_approved_offer("neg-1")
    assert offer == {"vendor_id": "atlas-office", "unit_price": 96, "quantity": 2, "total_price": 192, "currency": "INR"}
