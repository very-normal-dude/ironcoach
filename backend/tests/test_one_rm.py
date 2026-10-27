import pytest

from app.services.one_rm import estimate_1rm


def test_single_rep_is_the_weight_itself():
    assert estimate_1rm(100, 1) == 100


def test_epley_known_value():
    # 100 kg x 10 reps -> 100 * (1 + 10/30) = 133.3
    assert estimate_1rm(100, 10, "epley") == 133.3


def test_brzycki_known_value():
    # 100 kg x 10 reps -> 100 * 36 / 27 = 133.3
    assert estimate_1rm(100, 10, "brzycki") == 133.3


def test_invalid_inputs():
    with pytest.raises(ValueError):
        estimate_1rm(0, 5)
    with pytest.raises(ValueError):
        estimate_1rm(100, 0)
    with pytest.raises(ValueError):
        estimate_1rm(100, 5, "made_up")
