from security.trust import trust_score


def test_trust_score_is_bounded_and_verification_helps():
    assert trust_score(1000, 0, True) == 100
    assert trust_score(0, 20, False) == 0
    assert trust_score(4, 0, True) > trust_score(4, 0, False)

