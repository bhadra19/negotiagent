from negotiation.engine import NegotiationEngine


def test_batch_inputs_can_be_evaluated_without_an_llm_or_payment_provider():
    engine = NegotiationEngine()
    cases = [("within-budget", 1, 100), ("too-low", 1, 50)]
    outcomes = {case_id: engine.run(quantity, budget).selected_offer for case_id, quantity, budget in cases}

    assert outcomes["within-budget"] is not None
    assert outcomes["too-low"] is None
