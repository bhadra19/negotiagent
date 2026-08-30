from audit.logger import AuditLogger


def test_failed_payment_can_be_retried_with_a_new_idempotency_key(tmp_path):
    logger = AuditLogger(str(tmp_path / "audit.db"))
    first = logger.start_payment_attempt("neg-1", "attempt-one")
    logger.fail_payment_attempt("attempt-one", "payment provider error")
    second = logger.start_payment_attempt("neg-1", "attempt-two")
    logger.complete_payment_attempt("attempt-two", "order_test_123", 18400, "INR")

    assert first["attempt_number"] == 1
    assert second["attempt_number"] == 2
    assert logger.list_payment_attempts("neg-1") == [
        {"attempt_number": 1, "status": "failed", "order_id": None, "amount_subunits": None, "currency": None, "failure_reason": "payment provider error"},
        {"attempt_number": 2, "status": "created", "order_id": "order_test_123", "amount_subunits": 18400, "currency": "INR", "failure_reason": None},
    ]


def test_reusing_an_idempotency_key_does_not_create_a_second_attempt(tmp_path):
    logger = AuditLogger(str(tmp_path / "audit.db"))
    logger.start_payment_attempt("neg-1", "attempt-one")
    replay = logger.start_payment_attempt("neg-1", "attempt-one")

    assert not replay["created"]
    assert replay["attempt_number"] == 1
