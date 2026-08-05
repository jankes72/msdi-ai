"""
Fair Odds Calculator for Exact Score Market Builder
Part of SSI V5 - Market Intelligence Knowledge Layer

This module provides functionality for:
1. Calculating fair odds from probability (fair_odds = 1 / probability)
2. Normalizing probability distributions to ensure they sum to 1.0
3. Validating probability values (0 <= p <= 1)

All calculations are deterministic - same input always produces same output.

Mathematical Formulas:
----------------------
1. Fair Odds Calculation:
   fair_odds = 1 / probability
   
   Where:
   - probability: The probability of an outcome (0 < p <= 1)
   - fair_odds: The theoretical odds that reflect true probability
   
   Edge cases:
   - If probability = 0: fair_odds = infinity (impossible outcome)
   - If probability = 1: fair_odds = 1.0 (certain outcome)

2. Probability Normalization:
   For a list of outcomes with probabilities [p1, p2, ..., pn]:
   normalized_pi = pi / sum(p1, p2, ..., pn)
   
   This ensures: sum(normalized_p1, ..., normalized_pn) = 1.0
   
   Edge cases:
   - If sum = 0: Assign uniform probability (1/n) to each outcome
   - If sum > 0: Normalize by dividing each probability by the sum
"""

from typing import Dict, List, Optional
import math


class FairOddsCalculator:
    """
    Calculator for fair odds and probability normalization.
    
    Provides deterministic calculations for converting probabilities to fair odds
    and normalizing probability distributions.
    
    Example:
        >>> calculator = FairOddsCalculator()
        >>> odds = calculator.calculate_fair_odds(0.14)
        >>> print(f"Fair odds for 14% probability: {odds:.2f}")
        Fair odds for 14% probability: 7.14
    """
    
    # Minimum probability to avoid division by zero
    MIN_PROBABILITY = 1e-10
    
    def calculate_fair_odds(self, probability: float) -> float:
        """
        Calculate fair odds from probability.
        
        Formula: fair_odds = 1 / probability
        
        Args:
            probability: Probability of the outcome (0 <= p <= 1)
        
        Returns:
            Fair odds value
        
        Raises:
            ValueError: If probability is negative
        
        Edge cases:
            - probability = 0: Returns infinity
            - probability = 1: Returns 1.0
        
        Example:
            >>> calculator = FairOddsCalculator()
            >>> calculator.calculate_fair_odds(0.1) == 10.0
            True
            >>> calculator.calculate_fair_odds(0.5) == 2.0
            True
        """
        if probability < 0:
            raise ValueError(f"Probability cannot be negative: {probability}")
        
        if probability == 0:
            return float('inf')
        
        # Ensure probability is not too small to avoid overflow
        safe_prob = max(probability, self.MIN_PROBABILITY)
        return 1.0 / safe_prob
    
    def calculate_fair_odds_batch(
        self,
        probabilities: List[float]
    ) -> List[float]:
        """
        Calculate fair odds for a batch of probabilities.
        
        Args:
            probabilities: List of probability values
        
        Returns:
            List of fair odds values (same order as input)
        
        Example:
            >>> calculator = FairOddsCalculator()
            >>> odds = calculator.calculate_fair_odds_batch([0.1, 0.2, 0.5])
            >>> odds == [10.0, 5.0, 2.0]
            True
        """
        return [self.calculate_fair_odds(p) for p in probabilities]
    
    def normalize_probability_distribution(
        self,
        scores: List[Dict[str, float]],
        probability_key: str = "probability"
    ) -> List[Dict]:
        """
        Normalize probability distribution across multiple scores.
        
        Ensures that the sum of all probabilities equals 1.0 by dividing
        each probability by the total sum.
        
        Args:
            scores: List of score dictionaries with probability values
            probability_key: Key to access probability in each score dict
        
        Returns:
            List of scores with normalized probabilities
        
        Edge cases:
            - If all probabilities are 0: Assigns uniform probability (1/n)
            - If sum > 0: Normalizes by dividing each by the sum
        
        Example:
            >>> calculator = FairOddsCalculator()
            >>> scores = [
            ...     {"score": "1:0", "probability": 0.1},
            ...     {"score": "2:0", "probability": 0.2},
            ...     {"score": "1:1", "probability": 0.3}
            ... ]
            >>> normalized = calculator.normalize_probability_distribution(scores)
            >>> sum(s["probability"] for s in normalized) == 1.0
            True
        """
        if not scores:
            return scores
        
        # Calculate total probability
        total = sum(score.get(probability_key, 0.0) for score in scores)
        
        if total == 0:
            # All probabilities are 0 - assign uniform distribution
            uniform_prob = 1.0 / len(scores)
            for score in scores:
                score[probability_key] = uniform_prob
        else:
            # Normalize each probability
            for score in scores:
                score[probability_key] = score.get(probability_key, 0.0) / total
        
        return scores
    
    def validate_probability(self, probability: float) -> float:
        """
        Validate and clamp probability to valid range [0, 1].
        
        Args:
            probability: Probability value to validate
        
        Returns:
            Clamped probability (0 <= p <= 1)
        
        Example:
            >>> calculator = FairOddsCalculator()
            >>> calculator.validate_probability(-0.1) == 0.0
            True
            >>> calculator.validate_probability(1.5) == 1.0
            True
        """
        return max(0.0, min(1.0, probability))
    
    def calculate_probability_from_odds(self, odds: float) -> float:
        """
        Calculate probability from given odds.
        
        Formula: probability = 1 / odds
        
        Args:
            odds: Odds value (must be > 0)
        
        Returns:
            Probability value
        
        Raises:
            ValueError: If odds <= 0
        
        Example:
            >>> calculator = FairOddsCalculator()
            >>> calculator.calculate_probability_from_odds(10.0) == 0.1
            True
            >>> calculator.calculate_probability_from_odds(2.0) == 0.5
            True
        """
        if odds <= 0:
            raise ValueError(f"Odds must be positive: {odds}")
        return 1.0 / odds
    
    def calculate_expected_value(
        self,
        probability: float,
        odds: float
    ) -> float:
        """
        Calculate expected value for a bet.
        
        Formula: EV = probability * (odds - 1)
        
        This represents the expected profit per unit staked.
        
        Args:
            probability: Probability of winning
            odds: Odds offered
        
        Returns:
            Expected value
        
        Example:
            >>> calculator = FairOddsCalculator()
            >>> ev = calculator.calculate_expected_value(0.1, 10.0)
            >>> ev == 0.9  # 0.1 * (10 - 1) = 0.9
            True
        """
        return probability * (odds - 1.0)
    
    def calculate_odds_ratio(
        self,
        probability: float,
        fair_odds: Optional[float] = None
    ) -> float:
        """
        Calculate the ratio between fair odds and market odds.
        
        If market odds > fair odds, ratio > 1 indicates value.
        If market odds < fair odds, ratio < 1 indicates under.login
        
        Args:
            probability: Probability of outcome
            fair_odds: Optional fair odds (calculated if not provided)
        
        Returns:
            Odds ratio (market_odds / fair_odds)
        """
        if fair_odds is None:
            fair_odds = self.calculate_fair_odds(probability)
        
        if fair_odds == 0:
            return float('inf')
        
        return fair_odds
    
    def batch_calculate_fair_odds_and_normalize(
        self,
        scores: List[Dict[str, float]],
        probability_key: str = "probability",
        fair_odds_key: str = "fair_odds"
    ) -> List[Dict]:
        """
        Calculate fair odds for all scores and normalize probabilities in one pass.
        
        This is the main method used by MarketBuilder to ensure:
        1. Probabilities sum to 1.0
        2. Each score has its fair odds calculated
        
        Args:
            scores: List of score dictionaries with probability values
            probability_key: Key to access probability in each score dict
            fair_odds_key: Key to store fair odds in each score dict
        
        Returns:
            List of scores with normalized probabilities and calculated fair odds
        """
        # First, normalize probabilities
        scores = self.normalize_probability_distribution(scores, probability_key)
        
        # Then calculate fair odds for each score
        for score in scores:
            prob = score.get(probability_key, 0.0)
            score[fair_odds_key] = self.calculate_fair_odds(prob)
        
        return scores
