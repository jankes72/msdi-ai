"""
Exact Score Market Builder
Part of SSI V5 - Market Intelligence Knowledge Layer

This is the main module that builds the ExactScoreMarketKnowledge from
ExactScoreRanker output and other sources. It integrates all components:
- Probability Fusion Engine
- Fair Odds Calculator
- Value Detector
- Multi-Match Mathematics
- Score Group Registry

It does NOT:
- Generate coupons/bets
- Make betting decisions
- Modify existing modules

It DOES:
- Build market intelligence data
- Fuse probabilities from multiple sources
- Calculate fair odds and market values
- Organize scores into strategic groups
- Provide data for Strategy Laboratory
"""

from typing import Dict, List, Optional, Any
from dataclasses import asdict

from .market_models import (
    ExactScore,
    ScoreGroup,
    ExactScoreMarketKnowledge,
    MultiMatchMath,
    FusionWeights
)
from .probability_fusion import ProbabilityFusionEngine
from .fair_odds_calculator import FairOddsCalculator
from .value_detector import ValueDetector
from .multi_match_math import MultiMatchMathEngine
from .group_registry import ScoreGroupRegistry


class ExactScoreMarketBuilder:
    """
    Main builder class for creating ExactScoreMarketKnowledge.
    
    Integrates all components to transform ExactScoreRanker output
    into a complete market intelligence structure.
    
    Example:
        >>> builder = ExactScoreMarketBuilder()
        >>> ranker_output = [
        ...     {"score": "1:0", "combined_probability": 0.14, "confidence_score": 0.86},
        ...     {"score": "2:0", "combined_probability": 0.12, "confidence_score": 0.82}
        ... ]
        >>> knowledge = builder.build_market(ranker_output, "BAR_RMA")
        >>> print(knowledge.to_json())
    """
    
    def __init__(
        self,
        fusion_engine: Optional[ProbabilityFusionEngine] = None,
        fair_odds_calculator: Optional[FairOddsCalculator] = None,
        value_detector: Optional[ValueDetector] = None,
        multi_match_math: Optional[MultiMatchMathEngine] = None,
        group_registry: Optional[ScoreGroupRegistry] = None,
        fusion_weights: Optional[FusionWeights] = None
    ):
        """
        Initialize the builder with optional component overrides.
        
        Args:
            fusion_engine: ProbabilityFusionEngine instance
            fair_odds_calculator: FairOddsCalculator instance
            value_detector: ValueDetector instance
            multi_match_math: MultiMatchMathEngine instance
            group_registry: ScoreGroupRegistry instance
            fusion_weights: FusionWeights for probability fusion
        """
        self.fusion_engine = fusion_engine or ProbabilityFusionEngine(fusion_weights)
        self.fair_odds_calculator = fair_odds_calculator or FairOddsCalculator()
        self.value_detector = value_detector or ValueDetector()
        self.multi_match_math = multi_match_math or MultiMatchMathEngine()
        self.group_registry = group_registry or ScoreGroupRegistry()
    
    def _process_single_score(
        self,
        score_data: Dict[str, Any],
        real_market_odds: Optional[Dict[str, float]] = None
    ) -> ExactScore:
        """
        Process a single score from ExactScoreRanker output.
        
        Fuses probabilities, calculates fair odds, and detects market value.
        
        Args:
            score_data: Dictionary from ExactScoreRanker with keys:
                       - score: str
                       - world_probability: Optional[float]
                       - market_probability: Optional[float]
                       - poisson_probability: Optional[float]
                       - combined_probability: Optional[float]
                       - confidence_score: Optional[float]
                       - sample_strength: Optional[float]
                       - risk_score: Optional[float]
                       - value_score: Optional[float]
            real_market_odds: Optional dict of {score: market_odds}
        
        Returns:
            ExactScore object with all calculated values
        """
        # Extract all fields with safe defaults
        score_str = score_data.get("score", "0:0")
        
        # Probability sources
        world_prob = score_data.get("world_probability")
        market_prob = score_data.get("market_probability")
        poisson_prob = score_data.get("poisson_probability")
        combined_prob = score_data.get("combined_probability")
        
        # Metadata
        confidence = score_data.get("confidence_score", 0.5)
        sample_strength = score_data.get("sample_strength", 0.5)
        risk = score_data.get("risk_score")
        value_score = score_data.get("value_score")
        
        # Step 1: Fuse probability if not already provided
        if combined_prob is None:
            probability = self.fusion_engine.fuse_probabilities(
                world_prob=world_prob,
                market_prob=market_prob,
                poisson_prob=poisson_prob,
                confidence=confidence,
                sample_strength=sample_strength
            )
        else:
            probability = combined_prob
        
        # Step 2: Calculate fair odds
        fair_odds = self.fair_odds_calculator.calculate_fair_odds(probability)
        
        # Step 3: Detect market value (if real odds are available)
        market_value = None
        if real_market_odds and score_str in real_market_odds:
            market_value = self.value_detector.detect_market_value(
                fair_odds, real_market_odds[score_str]
            )
        
        return ExactScore(
            score=score_str,
            probability=probability,
            fair_odds=fair_odds,
            confidence=confidence,
            market_value=market_value,
            risk=risk,
            world_probability=world_prob,
            market_probability=market_prob,
            poisson_probability=poisson_prob,
            sample_strength=sample_strength,
            value_score=value_score
        )
    
    def _build_score_groups(
        self,
        scores: List[ExactScore],
        custom_groups: Optional[Dict[str, List[str]]] = None
    ) -> List[ScoreGroup]:
        """
        Build score groups from available scores.
        
        Args:
            scores: List of ExactScore objects
            custom_groups: Optional custom group definitions
        
        Returns:
            List of ScoreGroup objects
        """
        # Get available score strings
        available_scores = {s.score for s in scores}
        
        # Use custom groups or default registry
        if custom_groups:
            registry = ScoreGroupRegistry(use_default_groups=False)
            registry.add_groups(custom_groups)
        else:
            registry = self.group_registry
        
        groups = []
        
        # Build groups that have at least one available score
        for group_name, group_scores in registry.get_all_groups().items():
            matching_scores = [s for s in group_scores if s in available_scores]
            
            if not matching_scores:
                continue
            
            # Calculate group probability (sum of individual probabilities)
            group_prob = sum(
                s.probability for s in scores if s.score in matching_scores
            )
            
            if group_prob == 0:
                continue
            
            # Calculate group fair odds
            group_fair_odds = 1.0 / group_prob
            
            # Calculate group confidence (average of individual confidences)
            group_conf = sum(
                s.confidence for s in scores if s.score in matching_scores
            ) / len(matching_scores)
            
            groups.append(ScoreGroup(
                name=group_name,
                scores=matching_scores,
                probability=group_prob,
                fair_odds=group_fair_odds,
                confidence=group_conf
            ))
        
        return groups
    
    def _calculate_multi_match_math(
        self,
        scores: List[ExactScore]
    ) -> Optional[MultiMatchMath]:
        """
        Calculate multi-match mathematics for demonstration purposes.
        
        This uses the top 2 scores as an example combination.
        Strategy Laboratory can calculate arbitrary combinations.
        
        Args:
            scores: List of ExactScore objects
        
        Returns:
            MultiMatchMath for the top 2 scores, or None if not enough scores
        """
        if len(scores) < 2:
            return None
        
        # Take top 2 scores by probability
        top_scores = sorted(scores, key=lambda s: s.probability, reverse=True)[:2]
        
        probs = [s.probability for s in top_scores]
        confs = [s.confidence for s in top_scores]
        risks = [s.risk or 0.0 for s in top_scores]
        odds = [s.fair_odds for s in top_scores]
        
        result = self.multi_match_math.calculate_combination(
            probabilities=probs,
            confidences=confs,
            risk_scores=risks,
            fair_odds_list=odds,
            confidence_method="product"
        )
        
        return MultiMatchMath(
            combined_probability=result.combined_probability,
            combined_confidence=result.combined_confidence,
            combined_risk=result.combined_risk,
            expected_value=result.expected_value
        )
    
    def _normalize_and_recalculate_odds(
        self,
        scores: List[ExactScore]
    ) -> List[ExactScore]:
        """
        Normalize probabilities to sum to 1.0 and recalculate fair odds.
        
        This ensures all scores have valid probabilities and odds.
        
        Args:
            scores: List of ExactScore objects
        
        Returns:
            List of ExactScore objects with normalized probabilities and updated fair odds
        """
        # Calculate total probability
        total_prob = sum(s.probability for s in scores)
        
        # Handle edge case (total = 0)
        if total_prob == 0:
            uniform_prob = 1.0 / len(scores) if scores else 0.0
            for s in scores:
                s.probability = uniform_prob
                s.fair_odds = self.fair_odds_calculator.calculate_fair_odds(uniform_prob)
            return scores
        
        # Normalize probabilities and recalculate fair odds
        for s in scores:
            s.probability = s.probability / total_prob
            s.fair_odds = self.fair_odds_calculator.calculate_fair_odds(s.probability)
        
        return scores
    
    def build_market(
        self,
        ranker_output: List[Dict[str, Any]],
        match_id: str,
        real_market_odds: Optional[Dict[str, float]] = None,
        custom_groups: Optional[Dict[str, List[str]]] = None,
        calculate_combination_math: bool = True
    ) -> ExactScoreMarketKnowledge:
        """
        Build ExactScoreMarketKnowledge from ExactScoreRanker output.
        
        This is the main method that creates the complete market intelligence
        structure for a single match.
        
        Args:
            ranker_output: List of score dictionaries from ExactScoreRanker
            match_id: Unique identifier for the match
            real_market_odds: Optional dict of {score: market_odds} for value detection
            custom_groups: Optional custom group definitions
            calculate_combination_math: Whether to calculate multi-match math
        
        Returns:
            ExactScoreMarketKnowledge with all calculated data
        
        Example:
            >>> builder = ExactScoreMarketBuilder()
            >>> output = [
            ...     {"score": "1:0", "combined_probability": 0.14, "confidence_score": 0.86},
            ...     {"score": "2:0", "combined_probability": 0.12, "confidence_score": 0.82},
            ...     {"score": "1:1", "combined_probability": 0.18, "confidence_score": 0.88}
            ... ]
            >>> knowledge = builder.build_market(output, "BAR_RMA")
            >>> print(f"Market has {len(knowledge.scores)} scores")
        """
        # Step 1: Process all scores from ranker output
        scores = []
        for score_data in ranker_output:
            exact_score = self._process_single_score(score_data, real_market_odds)
            scores.append(exact_score)
        
        # Step 2: Normalize probabilities and recalculate fair odds
        scores = self._normalize_and_recalculate_odds(scores)
        
        # Step 3: Build score groups
        groups = self._build_score_groups(scores, custom_groups)
        
        # Step 4: Calculate multi-match math (optional)
        combination_math = None
        if calculate_combination_math:
            combination_math = self._calculate_multi_match_math(scores)
        
        # Step 5: Create final knowledge structure
        return ExactScoreMarketKnowledge(
            match_id=match_id,
            scores=scores,
            groups=groups,
            combination_math=combination_math,
            metadata={
                "source": "ExactScoreMarketBuilder",
                "version": "5.2.9.x",
                "num_scores": len(scores),
                "num_groups": len(groups)
            }
        )
    
    def build_batch(
        self,
        match_data_list: List[Dict[str, Any]],
        calculate_combination_math: bool = True
    ) -> List[ExactScoreMarketKnowledge]:
        """
        Build market knowledge for multiple matches.
        
        Args:
            match_data_list: List of dicts containing:
                            - match_id: str
                            - ranker_output: List of score dicts
                            - real_market_odds: Optional dict
                            - custom_groups: Optional dict
            calculate_combination_math: Whether to calculate multi-match math
        
        Returns:
            List of ExactScoreMarketKnowledge objects
        """
        results = []
        
        for match_data in match_data_list:
            knowledge = self.build_market(
                ranker_output=match_data.get("ranker_output", []),
                match_id=match_data.get("match_id", ""),
                real_market_odds=match_data.get("real_market_odds"),
                custom_groups=match_data.get("custom_groups"),
                calculate_combination_math=calculate_combination_math
            )
            results.append(knowledge)
        
        return results
    
    def get_components(self) -> Dict[str, Any]:
        """Get all component instances for external access"""
        return {
            "fusion_engine": self.fusion_engine,
            "fair_odds_calculator": self.fair_odds_calculator,
            "value_detector": self.value_detector,
            "multi_match_math": self.multi_match_math,
            "group_registry": self.group_registry
        }
    
    def set_fusion_weights(self, weights: FusionWeights) -> None:
        """Update fusion weights"""
        self.fusion_engine.set_weights(weights)


# Singleton instance for convenience
_default_builder: Optional[ExactScoreMarketBuilder] = None


def get_default_builder() -> ExactScoreMarketBuilder:
    """Get the default market builder instance"""
    global _default_builder
    if _default_builder is None:
        _default_builder = ExactScoreMarketBuilder()
    return _default_builder


def reset_default_builder() -> None:
    """Reset the default builder (useful for testing)"""
    global _default_builder
    _default_builder = None
