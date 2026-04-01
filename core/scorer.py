import numpy as np
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class Scorer:
    @staticmethod
    def kelly_fraction(p: float, b: float = 1.0) -> float:
        """
        Kelly criterion: f* = (bp - q) / b
        p = our probability
        q = 1 - p
        b = net odds (if $1 bet returns $b in profit, plus the $1 stake)
            In binary markets, b = (1 - market_price) / market_price
        """
        if p <= 0 or b <= 0:
            return 0.0
        
        q = 1 - p
        f_star = (b * p - q) / b
        
        # We apply a fractional Kelly (e.g., quarter Kelly) to reduce risk
        fractional_kelly = 0.25 * f_star
        
        # Clamp between 0 and 0.1 (max 10% of bankroll)
        return max(0.0, min(0.1, fractional_kelly))

    @staticmethod
    def edge_score(our_prob: float, market_prob: float) -> float:
        """
        Raw edge in percentage points.
        """
        return our_prob - market_prob

    @staticmethod
    def confidence_weighted_edge(edge: float, confidence: float) -> float:
        """
        Weight the edge by the agent's confidence.
        """
        return edge * confidence

    @staticmethod
    def rank_edges(edges_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort edges by confidence-weighted edge descending.
        """
        return sorted(
            edges_list, 
            key=lambda x: x.get("edge", 0) * x.get("confidence", 0), 
            reverse=True
        )

    @staticmethod
    def simulate_pnl(edges_list: List[Dict[str, Any]], bankroll: float = 1000.0) -> Dict[str, Any]:
        """
        Simulate P&L if all edges played at Kelly sizing.
        Returns expected_value, variance, sharpe_ratio.
        """
        if not edges_list:
            return {"expected_value": 0, "variance": 0, "sharpe_ratio": 0}
        
        returns = []
        for edge in edges_list:
            p = edge.get("our_probability", 0.5)
            f = edge.get("kelly_fraction", 0.0)
            # In binary markets, outcome is either (1-price)/price profit or loss of stake
            # Here we simplify: win is edge, loss is -f*bankroll
            # Simplified return calculation for simulation
            expected_return = f * edge.get("edge", 0) * bankroll
            returns.append(expected_return)
        
        expected_value = sum(returns)
        variance = np.var(returns) if len(returns) > 1 else 0
        sharpe_ratio = (np.mean(returns) / np.std(returns)) if len(returns) > 1 and np.std(returns) > 0 else 0
        
        return {
            "expected_value": expected_value,
            "variance": variance,
            "sharpe_ratio": sharpe_ratio
        }

scorer = Scorer()
