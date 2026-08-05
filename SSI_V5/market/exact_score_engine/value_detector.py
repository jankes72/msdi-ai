"""
Value Detector for Exact Score Market Builder
Part of SSI V5 - Market Intelligence Knowledge Layer

This module compares calculated fair odds with real market odds to detect
value opportunities. It identifies when the market is offering better odds
than the theoretical fair odds, indicating potential value.

Mathematical Formulas:
----------------------
1. Market Value Calculation:
   market_value_percentage = (real_market_odds - fair_odds) / fair_odds * 100
   
   Where:
   - real_market_odds: Odds from bookmakers/market
   - fair_odds: Theoretically calculated fair odds
   - market_value_percentage: Percentage difference (positive = value)
   
   Interpretation:
   - +20%: Market odds are 20% better than fair odds (VALUE)
   - -10%: Market odds are 10% worse than fair odds (UNDERVALUED)
   - 0%: Market odds match fair odds (FAIR)

2. Value Classification:
   - HIGH_VALUE: market_value > 20%
   - GOOD_VALUE: 10% < market_value <= 20%
   - FAIR_VALUE: 5% < market_value <= 10%
   - MARGINAL_VALUE: 0% < market_value <= 5%
   - NEUTRAL: -5% <= market_value <= 0%
   - UNDERVALUED: market_value < -5%
   - UNKNOWN: No market odds available

3. Value Score (0-100):
   A normalized score representing the quality of the value opportunity.
   Higher scores indicate better value.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ValueClassification(Enum):
    """Classification categories for market value"""
    HIGH_VALUE = "HIGH_VALUE"        # market_value > 20%
    GOOD_VALUE = "GOOD_VALUE"        # 10% < market_value <= 20%
    FAIR_VALUE = "FAIR_VALUE"        # 5% < market_value <= 10%
    MARGINAL_VALUE = "MARGINAL_VALUE"  # 0% < market_value <= 5%
    NEUTRAL = "NEUTRAL"              # -5% <= market_value <= 0%
    UNDERVALUED = "UNDERVALUED"      # market_value < -5%
    UNKNOWN = "UNKNOWN"              # No market odds available


# Value classification thresholds (configurable)
VALUE_THRESHOLDS = {
    "HIGH_VALUE": 0.20,
    "GOOD_VALUE": 0.10,
    "FAIR_VALUE": 0.05,
    "MARGINAL_VALUE": 0.0,
    "NEUTRAL": -0.05,
}


@dataclass
class ValueAssessment:
    """
    Complete value assessment for a single score.
    
    Attributes:
        fair_odds: Calculated fair odds
        real_market_odds: Actual market odds (if available)
        market_value_percentage: Percentage difference between market and fair odds
        classification: Value classification category
        value_score: Normalized score (0-100) representing value quality
    """
    fair_odds: float
    real_market_odds: Optional[float] = None
    market_value_percentage: Optional[float] = None
    classification: ValueClassification = ValueClassification.UNKNOWN
    value_score: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "fair_odds": self.fair_odds,
            "real_market_odds": self.real_market_odds,
            "market_value_percentage": self.market_value_percentage,
            "classification": self.classification.value,
            "value_score": self.value_score
        }


class ValueDetector:
    """
    Detects value opportunities by comparing fair odds with market odds.
    
    Provides methods to:
    - Calculate market value percentage
    - Classify value opportunities
    - Calculate normalized value scores
    - Batch process multiple scores
    
    Example:
        >>> detector = ValueDetector()
        >>> assessment = detector.detect_value(fair_odds=7.14, real_market_odds=9.0)
        >>> print(f"Market value: {assessment.market_value_percentage:.1%}")
        Market value: +26.0%
        >>> print(f"Classification: {assessment.classification}")
        Classification: ValueClassification.HIGH_VALUE
    """
    
    # Thresholds for value classification (configurable)
    HIGH_VALUE_THRESHOLD = 0.20   # >20%
    GOOD_VALUE_THRESHOLD = 0.10    # >10%
    FAIR_VALUE_THRESHOLD = 0.05    # >5%
    MARGINAL_THRESHOLD = 0.0       # >0%
    NEUTRAL_THRESHOLD = -0.05      # >-5%
    
    def __init__(
        self,
        high_threshold: float = HIGH_VALUE_THRESHOLD,
        good_threshold: float = GOOD_VALUE_THRESHOLD,
        fair_threshold: float = FAIR_VALUE_THRESHOLD,
        marginal_threshold: float = MARGINAL_THRESHOLD,
        neutral_threshold: float = NEUTRAL_THRESHOLD
    ):
        """
        Initialize with configurable thresholds.
        
        Args:
            high_threshold: Minimum percentage for HIGH_VALUE
            good_threshold: Minimum percentage for GOOD_VALUE
            fair_threshold: Minimum percentage for FAIR_VALUE
            marginal_threshold: Minimum percentage for MARGINAL_VALUE
            neutral_threshold: Maximum percentage for NEUTRAL
        """
        self.HIGH_VALUE_THRESHOLD = high_threshold
        self.GOOD_VALUE_THRESHOLD = good_threshold
        self.FAIR_VALUE_THRESHOLD = fair_threshold
        self.MARGINAL_THRESHOLD = marginal_threshold
        self.NEUTRAL_THRESHOLD = neutral_threshold
    
    def detect_market_value(
        self,
        fair_odds: float,
        real_market_odds: Optional[float] = None
    ) -> Optional[float]:
        """
        Calculate the market value percentage.
        
        Formula:
            market_value = (real_market_odds - fair_odds) / fair_odds
        
        Args:
            fair_odds: Calculated fair odds
            real_market_odds: Actual market odds (if available)
        
        Returns:
            Market value as a percentage (e.g., 0.26 = 26%), or None if
            real_market_odds is not available or fair_odds is 0/infinity.
        
        Example:
            >>> detector = ValueDetector()
            >>> detector.detect_market_value(7.14, 9.0) == pytest.approx(0.26)
            True
        """
        if real_market_odds is None or fair_odds is None:
            return None
        
        if fair_odds == 0 or fair_odds == float('inf'):
            return None
        
        if real_market_odds <= 0:
            return None
        
        market_value = (real_market_odds - fair_odds) / fair_odds
        return market_value
    
    def classify_value(
        self,
        market_value_percentage: Optional[float]
    ) -> ValueClassification:
        """
        Classify the market value into a category.
        
        Args:
            market_value_percentage: Market value percentage (from detect_market_value)
        
        Returns:
            ValueClassification category
        
        Classification thresholds:
            - HIGH_VALUE: > 20%
            - GOOD_VALUE: > 10% and <= 20%
            - FAIR_VALUE: > 5% and <= 10%
            - MARGINAL_VALUE: > 0% and <= 5%
            - NEUTRAL: >= -5% and <= 0%
            - UNDERVALUED: < -5%
            - UNKNOWN: None or invalid
        """
        if market_value_percentage is None:
            return ValueClassification.UNKNOWN
        
        if market_value_percentage > self.HIGH_VALUE_THRESHOLD:
            return ValueClassification.HIGH_VALUE
        elif market_value_percentage > self.GOOD_VALUE_THRESHOLD:
            return ValueClassification.GOOD_VALUE
        elif market_value_percentage > self.FAIR_VALUE_THRESHOLD:
            return ValueClassification.FAIR_VALUE
        elif market_value_percentage > self.MARGINAL_THRESHOLD:
            return ValueClassification.MARGINAL_VALUE
        elif market_value_percentage >= self.NEUTRAL_THRESHOLD:
            return ValueClassification.NEUTRAL
        else:
            return ValueClassification.UNDERVALUED
    
    def calculate_value_score(
        self,
        market_value_percentage: Optional[float],
        confidence: float = 1.0
    ) -> float:
        """
        Calculate a normalized value score (0-100) for a given market value.
        
        The score combines:
        - Market value percentage (higher is better)
        - Confidence in the prediction (higher confidence = more reliable score)
        
        Formula:
            raw_score = max(0, min(100, market_value * 100 + 50))
            weighted_score = raw_score * confidence
        
        Args:
            market_value_percentage: Market value percentage
            confidence: Confidence in the prediction (0.0 to 1.0)
        
        Returns:
            Value score (0-100)
        
        Example:
            >>> detector = ValueDetector()
            >>> detector.calculate_value_score(0.26, 0.8)  # 26% value, 80% confidence
            71.0  # (26 * 100 + 50) * 0.8 = 71.0
        """
        if market_value_percentage is None:
            return 0.0
        
        # Normalize market value to 0-100 scale
        # +20% -> 100, 0% -> 50, -20% -> 0
        raw_score = max(0, min(100, market_value_percentage * 100 + 50))
        
        # Weight by confidence
        weighted_score = raw_score * confidence
        
        return weighted_score
    
    def assess_value(
        self,
        fair_odds: float,
        real_market_odds: Optional[float] = None,
        confidence: float = 1.0
    ) -> ValueAssessment:
        """
        Perform complete value assessment for a single score.
        
        Args:
            fair_odds: Calculated fair odds
            real_market_odds: Actual market odds (if available)
            confidence: Confidence in the prediction
        
        Returns:
            ValueAssessment with all calculated values
        
        Example:
            >>> detector = ValueDetector()
            >>> assessment = detector.assess_value(7.14, 9.0, 0.86)
            >>> assessment.market_value_percentage == pytest.approx(0.26)
            True
            >>> assessment.classification == ValueClassification.HIGH_VALUE
            True
        """
        market_value = self.detect_market_value(fair_odds, real_market_odds)
        classification = self.classify_value(market_value)
        value_score = self.calculate_value_score(market_value, confidence)
        
        return ValueAssessment(
            fair_odds=fair_odds,
            real_market_odds=real_market_odds,
            market_value_percentage=market_value,
            classification=classification,
            value_score=value_score
        )
    
    def batch_assess_values(
        self,
        scores: List[Dict],
        fair_odds_key: str = "fair_odds",
        real_odds_key: str = "real_market_odds",
        confidence_key: str = "confidence",
        market_value_key: str = "market_value",
        classification_key: str = "value_classification"
    ) -> List[Dict]:
        """
        Batch process multiple scores to add value assessments.
        
        Args:
            scores: List of score dictionaries
            fair_odds_key: Key to access fair odds
            real_odds_key: Key to access real market odds
            confidence_key: Key to access confidence
            market_value_key: Key to store market value percentage
            classification_key: Key to store classification
        
        Returns:
            List of scores with value assessment fields added
        """
        for score in scores:
            fair_odds = score.get(fair_odds_key)
            real_odds = score.get(real_odds_key)
            confidence = score.get(confidence_key, 1.0)
            
            assessment = self.assess_value(fair_odds, real_odds, confidence)
            
            score[market_value_key] = assessment.market_value_percentage
            score[classification_key] = assessment.classification.value
            score[f"{market_value_key}_score"] = assessment.value_score
        
        return scores
    
    def get_value_thresholds(self) -> Dict[str, float]:
        """Get current value classification thresholds"""
        return {
            "HIGH_VALUE": self.HIGH_VALUE_THRESHOLD,
            "GOOD_VALUE": self.GOOD_VALUE_THRESHOLD,
            "FAIR_VALUE": self.FAIR_VALUE_THRESHOLD,
            "MARGINAL_THRESHOLD": self.MARGINAL_THRESHOLD,
            "NEUTRAL_THRESHOLD": self.NEUTRAL_THRESHOLD
        }
    
    def set_value_thresholds(
        self,
        high: Optional[float] = None,
        good: Optional[float] = None,
        fair: Optional[float] = None,
        marginal: Optional[float] = None,
        neutral: Optional[float] = None
    ) -> None:
        """Set value classification thresholds"""
        if high is not None:
            self.HIGH_VALUE_THRESHOLD = high
        if good is not None:
            self.GOOD_VALUE_THRESHOLD = good
        if fair is not None:
            self.FAIR_VALUE_THRESHOLD = fair
        if marginal is not None:
            self.MARGINAL_THRESHOLD = marginal
        if neutral is not None:
            self.NEUTRAL_THRESHOLD = neutral
