import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.chaos.nihde import NIHDE


def test_von_neumann_output_is_a_byte():
    engine = NIHDE(use_live_qrng=False)

    for _ in range(16):
        value = engine.decide()
        assert isinstance(value, int)
        assert 0 <= value <= 255


def test_live_entropy_mode_reseeds_automatically():
    engine = NIHDE(use_live_qrng=True, reseed_interval=2)
    initial_reseed_count = engine.reseed_count

    engine.decide_raw()
    engine.decide_raw()
    engine.decide_raw()

    assert engine.reseed_count > initial_reseed_count
    assert engine.profile()["use_live_qrng"] is True
    assert engine.profile()["postprocessing"] == "von_neumann"