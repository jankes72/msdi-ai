"""
Probability Fusion Engine for Exact Score Market Builder
Part of SSI V5 - Market Intelligence Knowledge Layer

This module implements dynamic probability fusion from multiple sources:
- WORLD database
- MARKET data
- POISSON/DIXON-COLES model

The fusion uses dynamic weights calculated as:
  final_weight = base_weight * confidence * sample_strength

This ensures that:
- High-confidence, large-sample predictions have more influence
- Small samples or low confidence have reduced impact
- Missing sources are handled gracefully with fallback to neutral values
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from .market_models import FusionWeights


@dataclass
class ProbabilitySource:
    """
    Container for probability values from different sources.
    
    Attributes:
        world: Probability from WORLD database
        market: Probability from MARKET data
        poisson: Probability from POISSON/DIXON-COLES model
    """
    world: Optional[float] = None
    market: Optional[float] = None
    poisson: Optional[float] = None


class ProbabilityFusionEngine:
    """
    Engine for fusing probabilities from multiple sources using dynamic weights.
    
    The dynamic weight formula is:
        weight = base_weight * confidence * sample_strength
    
    This ensures that predictions backed by strong evidence (high confidence,
    large sample size) have greater influence on the final probability.
    
    Example:
        WORLD: base_weight=0.4, confidence=0.9, sample_strength=0.8
        -> effective_weight = 0.4 * 0.9 * 0.8 = 0.288
        
        MARKET: base_weight=0.3, confidence=0.7, sample_strength=0.6
        -> effective_weight = 0.3 * 0.7 * 0.6 = 0.126
    """
    
    # Neutral probability fallback when no sources are available
    # For 15 possible scores, each gets 1/15 probability
    NEUTRAL_PROBABILITY = 1.0 / 15.0
    
    def __init__(self, weights: Optional[FusionWeights] = None):
        """
        Initialize the fusion engine with configurable weights.
        
        Args:
            weights: FusionWeights object with base weights for each source.
                     Defaults to WORLD=0.4, MARKET=0.3, POISSON=0.3
        """
        self.weights = weights or FusionWeights()
    
    def calculate_dynamic_weight(
        self,
        confidence: float,
        sample_strength: float,
        base_weight: float
    ) -> float:
        """
        Calculate dynamic weight for a source.
        
        Formula:
            dynamic_weight = base_weight * confidence * sample_strength
        
        Args:
            confidence: Confidence score (0.0 to 1.0)
            sample_strength: Sample strength (0.0 to 1.0)
            base_weight: Base weight for the source (e.g., 0.4 for WORLD)
        
        Returns:
            Dynamic weight for this source
        """
        return base_weight * confidence * sample_strength
    
    def fuse_probabilities(
        self,
        world_prob: Optional[float] = None,
        market_prob: Optional[float] = None,
        poisson_prob: Optional[float] = None,
        confidence: float = 0.5,
        sample_strength: float = 0.5,
    ) -> float:
        """
        Fuse probabilities from multiple sources using dynamic weights.
        
        For each available source, calculate its dynamic weight and use it
        to compute a weighted average of the probabilities.
        
        Missing sources are skipped. If no sources are available, returns
        the neutral probability (1/15).
        
        Args:
            world_prob: Probability from WORLD database
            market_prob: Probability from MARKET data
            poisson_prob: Probability from POISSON model
            confidence: Confidence score for the prediction (0.0 to 1.0)
            sample_strength: Sample strength (0.0 to 1.0)
        
        Returns:
            Fused probability value
        
        Example:
            >>> engine = ProbabilityFusionEngine()
            >>> prob = engine.fuse_probabilities(
            ...     world_prob=0.14,
            ...     market_prob=0.12,
            ...     poisson_prob=0.16,
            ...     confidence=0.9,
            ...     sample_strength=0.8
            ... )
            >>> 0.1 < prob < 0.2  # Weighted average
        """
        total_weight = 0.0
        weighted_sum = 0.0
        
        # WORLD source
        if world_prob is not None:
            w = self.calculate_dynamic_weight(
                confidence, sample_strength, self.weights.world_base
            )
            weighted_sum += world_prob * w
            total_weight += w
        
        # MARKET source
        if market_prob is not None:
            w = self.calculate_dynamic_weight(
                confidence, sample_strength, self.weights.market_base
            )
            weighted_sum += market_prob * w
            total_weight += w
        
        # POISSON source
        if poisson_prob is not None:
            w = self.calculate_dynamic_weight(
                confidence, sample_strength, self.weights.poisson_base
            )
            weighted_sum += poisson_prob * w
            total_weight += w
        
        # Handle edge cases
        if total_weight == 0:
            # No sources available - return neutral probability
            return self.NEUTRAL_PROBABILITY
        
        # Calculate weighted average
        fused_prob = weighted_sum / total_weight
        
        # Ensure probability is valid (0 <= p <= 1)
        return max(0.0, min(1.0, fused_prob))
    
    def normalize_probabilities(
        self,
        scores: List[Dict[str, Optional[float]]],
        probability_key: str = "probability"
    ) -> List[Dict]:
        """
        Normalize a list of scores so their probabilities sum to 1.0.
        
        If all probabilities are 0 or missing, assigns uniform probability
        (1/n) to each score.
        
        Args:
            scores: List of score dictionaries with probability_key
            probability_key: Key to use for probability values
        
        Returns:
            List of scores with normalized probabilities
        
        Example:
            >>> engine = ProbabilityFusionEngine()
            >>> scores = [{"score": "1:0", "probability": 0.1},
            ...           {"score": "2:0", "probability": 0.2},
            ...           {"score": "1:1", "probability": 0.3}]
            >>> normalized = engine.normalize_probabilities(scores)
            >>> sum(s["probability"] for s in normalized) == 1.0
        """
        # Calculate total probability
        total = sum(score.get(probability_key, 0.0) for score in scores)
        
        if total == 0 or len(scores) == 0:
            # Assign uniform probability
            uniform_prob = 1.0 / len(scores) if len(scores) > 0 else 0.0
            for score in scores:
                score[probability_key] = uniform_prob
        else:
            # Normalize probabilities
            for score in scores:
                score[probability_key] = score.get(probability_key, 0.0) / total
        
        return scores
    
    def fuse_scores(
        self,
        scores: List[Dict[str, Optional[float]]],
        confidence_key: str = "confidence_score",
        sample_strength_key: str = "sample_strength",
        world_prob_key: str = "world_probability",
        market_prob_key: str = "market_probability",
        poisson_prob_key: str = "poisson_probability",
        output_prob_key: str = "combined_probability"
    ) -> List[Dict]:
        """
        Fuse probabilities for a list of scores from ExactScoreRanker output.
        
        For each score, fuses the available probability sources using
        dynamic weights based on confidence and sample strength.
        
        Args:
            scores: List of score dictionaries from ExactScoreRanker
            confidence_key: Key for confidence score
            sample_strength_key: Key for sample strength
            world_prob_key: Key for WORLD probability
            market_prob_key: Key for MARKET probability
            poisson_prob_key: Key for POISSON probability
            output_prob_key: Key to store fused probability
        
        Returns:
            List of scores with fused probabilities added
        """
        for score in scores:
            confidence = score.get(confidence_key, 0.5)
            sample_strength = score.get(sample_strength_key, 0.5)
            
            fused_prob = self.fuse_probabilities(
                world_prob=score.get(world_prob_key),
                market_prob=score.get(market_prob_key),
                poisson_prob=score.get(poisson_prob_key),
                confidence=confidence,
                sample_strength=sample_strength
            )
            
            score[output_prob_key] = fused_prob
        
        return scores
    
    def get_weights(self) -> FusionWeights:
        """Get current fusion weights"""
        return self.weights
    
    def set_weights(self, weights: FusionWeights) -> None:
        """Set fusion weights"""
        self.weights = weights
    
    def add_data_source(
        self,
        source_name: str,
        base_weight: float
    ) -> None:
        """
        Add a new data source with configurable base weight.
        
        This allows extending the fusion engine to handle new probability
        sources without modifying the core architecture.
        
        Note: This is a placeholder for future extensibility.
        Actual implementation would require modifying the FusionWeights dataclass.
        
        Args:
            source_name: Name of the new source
            base_weight: Base weight for the new source
        """
        # In a future version, this would dynamically add the source
        # For now, we just document the intent
        pass
