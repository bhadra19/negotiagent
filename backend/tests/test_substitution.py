from negotiation.substitution import find_substitutions


def test_substitutions_are_filtered_to_the_budget():
    options = find_substitutions("ergonomic chair", quantity=2, budget=160)
    assert [option.substitute_item for option in options] == ["lumbar support chair"]


def test_unknown_item_has_no_invented_substitutions():
    assert find_substitutions("server rack", quantity=1, budget=1000) == []
