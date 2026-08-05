"""
Multi-Match Mathematics Engine for Exact Score Market Builder
Part of SSI V5 - Market Intelligence Knowledge Layer

This module provides mathematical operations for combining probabilities,
confidences, and risk scores across multiple matches. It does NOT generate
cupons or bets - it only provides the mathematical foundation for
Strategy Laboratory to use.

Mathematical Formulas:
----------------------
1. Combined Probability:
   For independent events A and B:
   P(A AND B) = P(A) * P(B)
   
   For n events: P(A1 AND A2 AND ... AND An) = P(A1) * P(A2) * ... * P(An)

2. Confidence Decay:
   When combining multiple predictions, confidence decreases (decays).
   
   Formula: combined_confidence = c1 * c2 * ... * cn
   
   This is a conservative approach (product) that assumes all predictions
   must be correct for the combination to be correct.
   
   Alternative: geometric mean = (c1 * c2 * ... * cn)^(1/n)
   or harmonic mean for different decay models.

3. Risk Accumulation:
   When combining multiple outcomes, risks add up.
   
   Formula: combined_risk = r1 + r2 + ... + rn
   
   This assumes risks are additive and independent.

4. Expected Value:
   For a combination of outcomes:
   EV = combined_probability * (combined_fair_odds - 1)
   
   Where combined_fair_odds = odds1 * odds2 * ... * oddsn

Key Principles:
--------------
- All calculations are deterministic
- Assumes independence between matches (standard assumption in sports betting)
- Does not generate bets or cupons - only provides mathematical data
- Designed to be used by Strategy Laboratory for decision making
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math


@dataclass
class MultiMatchResult:
    """
    Result of multi-match mathematical calculations.
    
    Attributes:
        combined_probability: Product of individual probabilities
        combined_fair_odds: Product of individual fair odds
        combined_confidence: Product of individual confidences (confidence decay)
        combined_risk: Sum of individual risk scores (risk accumulation)
        expected_value: Expected value of the combination
        num_matches: Number of matches in the combination
    """
    combined_probability: float
    combined_fair_odds: float
    combined_confidence: float
    combined_risk: float
    expected_value: float
    num_matches: int

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "combined_probability": self.combined_probability,
            "combined_fair_odds": self.combined_fair_odds,
            "combined_confidence": self.combined_confidence,
            "combined_risk": self.combined_risk,
            "expected_value": self.expected_value,
            "num_matches": self.num_matches
        }


class MultiMatchMathEngine:
    """
    Engine for multi-match probability mathematics.
    
    Provides methods to:
    - Calculate combined probability of multiple independent events
    - Calculate confidence decay when combining predictions
    - Calculate risk accumulation across multiple outcomes
    - Calculate expected value for combinations
    
    All calculations assume independence between events.
    
    Example:
        >>> engine = MultiMatchMathEngine()
        >>> probs = [0.15, 0.12, 0.10]
        >>> confs = [0.85, 0.80, 0.90]
        >>> risks = [0.15, 0.20, 0.10]
        >>> odds = [6.67, 8.33, 10.0]
        >>> result = engine.calculate_combination(probs, confs, risks, odds)
        >>> print(f"Combined probability: {result.combined_probability:.4f}")
        Combined probability: 0.0018
    """
    
    def calculate_combined_probability(
        self,
        probabilities: List[float]
    ) -> float:
        """
        Calculate the combined probability of multiple independent events.
        
        Formula: P(A AND B AND ...) = P(A) * P(B) * ...
        
        Args:
            probabilities: List of individual probabilities (0 <= p <= 1)
        
        Returns:
            Combined probability (product of all probabilities)
        
        Edge cases:
            - Empty list: Returns 1.0 (identity element for multiplication)
            - Any probability = 0: Returns 0
            - Any probability = 1: Has no effect on the product
        
        Example:
            >>> engine = MultiMatchMathEngine()
            >>> engine.calculate_combined_probability([0.1, 0.2, 0.5])
            0.01
        """
        if not probabilities:
            return 1.0
        
        result = 1.0
        for p in probabilities:
            result *= p
        
        return result
    
    def calculate_combined_confidence_product(
        self,
        confidences: List[float]
    ) -> float:
        """
        Calculate combined confidence using product (conservative decay).
        
        Formula: combined_confidence = c1 * c2 * ... * cn
        
        This assumes all predictions must be correct for the combination
        to be valid (most conservative approach).
        
        Args:
            confidences: List of individual confidences (0 <= c <= 1)
        
        Returns:
            Combined confidence (0 <= result <= 1)
        
        Edge cases:
            - Empty list: Returns 1.0
            - Any confidence = 0: Returns 0
            - All confidences = 1: Returns 1
        """
        if not confidences:
            return 1.0
        
        result = 1.0
        for c in confidences:
            result *= c
        
        return result
    
    def calculate_combined_confidence_geometric_mean(
        self,
        confidences: List[float]
    ) -> float:
        """
        Calculate combined confidence using geometric mean (moderate decay).
        
        Formula: combined_confidence = (c1 * c2 * ... * cn)^(1/n)
        
        This is less aggressive than product decay but still conservative.
        
        Args:
            confidences: List of individual confidences (0 <= c <= 1)
        
        Returns:
            Combined confidence as geometric mean
        
        Edge cases:
            - Empty list: Returns 0.0
            - Any confidence = 0: Returns 0
        """
        if not confidences:
            return 0.0
        
        product = 1.0
        for c in confidences:
            product *= c
        
        n = len(confidences)
        return product ** (1.0 / n)
    
    def calculate_combined_confidence_harmonic_mean(
        self,
        confidences: List[float]
    ) -> float:
        """
        Calculate combined confidence using harmonic mean (aggressive decay).
        
        Formula: combined_confidence = n / (1/c1 + 1/c2 + ... + 1/cn)
        
        This gives more weight to lower confidences.
        
        Args:
            confidences: List of individual confidences (0 < c <= 1)
        
        Returns:
            Combined confidence as harmonic mean
        
        Edge cases:
            - Empty list: Returns 0.0
            - Any confidence = 0: Returns 0
        """
        if not confidences:
            return 0.0
        
        # Filter out zeros to avoid division by zero
        non_zero = [c for c in confidences if c > 0]
        
        if not non_zero:
            return 0.0
        
        n = len(confidences)
        sum_of_reciprocals = sum(1.0 / c for c in non_zero)
        
        if sum_of_reciprocals == 0:
            return 0.0
        
        return n / sum_of_reciprocals
    
    def calculate_combined_confidence(
        self,
        confidences: List[float],
        method: str = "product"
    ) -> float:
        """
        Calculate combined confidence using specified method.
        
        Args:
            confidences: List of individual confidences
            method: Method to use ("product", "geometric_mean", "harmonic_mean")
        
        Returns:
            Combined confidence using the specified method
        """
        if method == "product":
            return self.calculate_combined_confidence_product(confidences)
        elif method == "geometric_mean":
            return self.calculate_combined_confidence_geometric_mean(confidences)
        elif method == "harmonic_mean":
            return self.calculate_combined_confidence_harmonic_mean(confidences)
        else:
            raise ValueError(f"Unknown confidence method: {method}")
    
    def calculate_combined_risk(
        self,
        risk_scores: List[float]
    ) -> float:
        """
        Calculate combined risk by summing individual risk scores.
        
        Formula: combined_risk = r1 + r2 + ... + rn
        
        This assumes risks are additive and independent.
        
        Args:
            risk_scores: List of individual risk scores (>= 0)
        
        Returns:
            Combined risk (sum of all risk scores)
        
        Edge cases:
            - Empty list: Returns 0.0
            - Negative risks: Clamped to 0
        """
        if not risk_scores:
            return 0.0
        
        # Ensure all risks are non-negative
        safe_risks = [max(0.0, r) for r in risk_scores]
        return sum(safe_risks)
    
    def calculate_expected_value(
        self,
        probability: float,
        odds: float
    ) -> float:
        """
        Calculate expected value for a single bet.
        
        Formula: EV = probability * (odds - 1)
        
        This represents the expected profit per unit staked.
        
        Args:
            probability: Probability of the outcome
            odds: Odds offered (decimal format)
        
        Returns:
            Expected value
        
        Example:
            >>> engine = MultiMatchMathEngine()
            >>> engine.calculate_expected_value(0.1, 10.0)
            0.9
        """
        return probability * (odds - 1.0)
    
    def calculate_combined_fair_odds(
        self,
        fair_odds_list: List[float]
    ) -> float:
        """
        Calculate combined fair odds for multiple independent events.
        
        Formula: combined_odds = odds1 * odds2 * ... * oddsn
        
        Args:
            fair_odds_list: List of individual fair odds values
        
        Returns:
            Combined fair odds (product of all odds)
        
        Edge cases:
            - Empty list: Returns 1.0
            - Any odds = 0: Returns 0
        """
        if not fair_odds_list:
            return 1.0
        
        result = 1.0
        for odds in fair_odds_list:
            result *= odds
        
        return result
    
    def calculate_combination(
        self,
        probabilities: List[float],
        confidences: List[float],
        risk_scores: List[float],
        fair_odds_list: List[float],
        confidence_method: str = "product"
    ) -> MultiMatchResult:
        """
        Calculate all multi-match metrics for a combination of outcomes.
        
        This is the main method for Strategy Laboratory to get complete
        mathematical data for any combination of matches.
        
        Args:
            probabilities: List of individual probabilities
            confidences: List of individual confidences
            risk_scores: List of individual risk scores
            fair_odds_list: List of individual fair odds
            confidence_method: Method for confidence calculation
                          ("product", "geometric_mean", "harmonic_mean")
        
        Returns:
            MultiMatchResult with all calculated values
        
        Example:
            >>> engine = MultiMatchMathEngine()
            >>> result = engine.calculate_combination(
            ...     probabilities=[0.15, 0.12],
            ...     confidences=[0.85, 0.80],
            ...     risk_scores=[0.15, 0.20],
            ...     fair_odds_list=[6.67, 8.33]
            ... )
            >>> print(f"Combined probability: {result.combined_probability:.4f}")
            Combined probability: 0.0180
        """
        combined_prob = self.calculate_combined_probability(probabilities)
        combined_fair_odds = self.calculate_combined_fair_odds(fair_odds_list)
        combined_conf = self.calculate_combined_confidence(confidences, confidence_method)
        combined_risk = self.calculate_combined_risk(risk_scores)
        expected_value = self.calculate_expected_value(combined_prob, combined_fair_odds)
        
        return MultiMatchResult(
            combined_probability=combined_prob,
            combined_fair_odds=combined_fair_odds,
            combined_confidence=combined_conf,
            combined_risk=combined_risk,
            expected_value=expected_value,
            num_matches=len(probabilities)
        )
    
    def calculate_pairwise_combinations(
        self,
        scores_list: List[List[Dict]]
    ) -> List[Dict]:
        """
        Calculate multi-match metrics for all pairwise combinations of scores.
        
        This generates combinations by taking one score from each match.
        
        Args:
            scores_list: List of lists, where each sublist contains scores for one match
                        Each score dict should have: probability, fair_odds, confidence, risk
        
        Returns:
            List of combination results, each with:
            - scores: List of score strings in the combination
            - combined_probability
            - combined_fair_odds
            - combined_confidence
            - combined_risk
            - expected_value
        
        Example:
            >>> engine = MultiMatchMathEngine()
            >>> match1_scores = [
            ...     {"score": "1:0", "probability": 0.15, "fair_odds": 6.67, "confidence": 0.85, "risk": 0.15},
            ...     {"score": "2:0", "probability": 0.12, "fair_odds": 8.33, "confidence": 0.80, "risk": 0.20}
            ... ]
            >>> match2_scores = [
            ...     {"score": "1:0", "probability": 0.10, "fair_odds": 10.0, "confidence": 0.90, "risk": 0.10}
            ... ]
            >>> combinations = engine.calculate_pairwise_combinations([match1_scores, match2_scores])
        """
        from itertools import product
        
        if not scores_list:
            return []
        
        results = []
        
        # Generate all combinations (one score from each match)
        for combination in product(*scores_list):
            probs = [s["probability"] for s in combination]
            confs = [s["confidence"] for s in combination]
            risks = [s["risk"] for s in combination]
            odds = [s["fair_odds"] for s in combination]
            score_strs = [s["score"] for s in combination]
            
            result = self.calculate_combination(probs, confs, risks, odds)
            
            results.append({
                "scores": score_strs,
                "combined_probability": result.combined_probability,
                "combined_fair_odds": result.combined_fair_odds,
                "combined_confidence": result.combined_confidence,
                "combined_risk": result.combined_risk,
                "expected_value": result.expected_value,
                "num_matches": result.num_matches
            })
        
        return results
    
    def calculate_cumulative_metrics(
        self,
        matches_data: List[Dict]
    ) -> Dict:
        """
        Calculate cumulative metrics for a list of matches.
        
        This provides aggregate statistics across multiple matches,
        useful for portfolio-level analysis.
        
        Args:
            matches_data: List of match dictionaries, each with:
                         - probability: Match probability
                         - fair_odds: Match fair odds
                         - confidence: Match confidence
                         - risk: Match risk
        
        Returns:
            Dictionary with cumulative metrics:
            - total_matches
            - total_probability (sum)
            - total_fair_odds (product)
            - avg_confidence
            - total_risk
            - avg_expected_value
        """
        if not matches_data:
            return {
                "total_matches": 0,
                "total_probability": 0.0,
                "total_fair_odds": 1.0,
                "avg_confidence": 0.0,
                "total_risk": 0.0,
                "avg_expected_value": 0.0
            }
        
        total_matches = len(matches_data)
        total_prob = sum(m["probability"] for m in matches_data)
        total_fair_odds = self.calculate_combined_fair_odds(
            [m["fair_odds"] for m in matches_data]
        )
        avg_confidence = sum(m["confidence"] for m in matches_data) / total_matches
        total_risk = sum(m.get("risk", 0.0) for m in matches_data)
        expected_values = [
            self.calculate_expected_value(m["probability"], m["fair_odds"])
            for m in matches_data
        ]
        avg_expected_value = sum(expected_values) / total_matches if expected_values else 0.0
        
        return {
            "total_matches": total_matches,
            "total_probability": total_prob,
            "total_fair_odds": total_fair_odds,
            "avg_confidence": avg_confidence,
            "total_risk": total_risk,
            "avg_expected_value": avg_expected_value
        }
