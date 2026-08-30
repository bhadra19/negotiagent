from audit.logger import AuditLogger


def test_audit_events_are_persisted_in_order(tmp_path):
    logger = AuditLogger(str(tmp_path / "audit.db"))
    logger.log("neg-1", "started", {"quantity": 2})
    logger.log("neg-1", "completed", {"selected": "atlas-office"})
    events = logger.list_events("neg-1")
    assert [event["event_type"] for event in events] == ["started", "completed"]
    assert events[0]["payload"]["quantity"] == 2

