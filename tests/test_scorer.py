import pytest
from core.scorer import Scorer

def test_kelly_fraction_positive_edge():
    # p = 0.6, market_price = 0.5 (b = 1.0)
    # f* = (1.0 * 0.6 - 0.4) / 1.0 = 0.2
    # Quarter Kelly = 0.05
    f = Scorer.kelly_fraction(0.6, 1.0)
    assert f == pytest.approx(0.05)

def test_kelly_fraction_no_edge_returns_zero():
    # p = 0.4, market_price = 0.5 (b = 1.0)
    # f* = (1.0 * 0.4 - 0.6) / 1.0 = -0.2
    f = Scorer.kelly_fraction(0.4, 1.0)
    assert f == 0.0

def test_edge_score_calculation():
    # our_prob = 0.7, market_prob = 0.5
    edge = Scorer.edge_score(0.7, 0.5)
    assert edge == pytest.approx(0.2)

def test_rank_edges_by_confidence():
    edges = [
        {"edge": 0.1, "confidence": 0.5}, # weighted = 0.05
        {"edge": 0.05, "confidence": 0.9}, # weighted = 0.045
        {"edge": 0.2, "confidence": 0.8}, # weighted = 0.16
    ]
    ranked = Scorer.rank_edges(edges)
    assert ranked[0]["edge"] == 0.2
    assert ranked[1]["edge"] == 0.1
    assert ranked[2]["edge"] == 0.05

def test_simulate_pnl_empty():
    res = Scorer.simulate_pnl([])
    assert res["expected_value"] == 0
    assert res["sharpe_ratio"] == 0
