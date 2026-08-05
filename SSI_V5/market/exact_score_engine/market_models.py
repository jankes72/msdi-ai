"""
Market Models for Exact Score Market Builder
Part of SSI V5 - Market Intelligence Knowledge Layer

This module defines the core data structures for the Exact Score Market Builder.
All models are fully serializable to JSON for compatibility with Strategy Laboratory and Agents.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import json


@dataclass
class ExactScore:
    """
    Represents a single exact score with all calculated market intelligence data.
    
    Attributes:
        score: The score string (e.g., "1:0", "2:1")
        probability: Fused probability from all sources (WORLD + MARKET + POISSON)
        fair_odds: Calculated fair odds (1 / probability)
        confidence: Confidence score for this prediction
        market_value: Value percentage vs real market odds (None if not available)
        risk: Risk score for this outcome
        world_probability: Probability from WORLD database
        market_probability: Probability from MARKET data
        poisson_probability: Probability from POISSON/DIXON-COLES model
        sample_strength: Strength of the sample size for this prediction
        value_score: Internal value score from ExactScoreRanker
    """
    score: str
    probability: float
    fair_odds: float
    confidence: float
    market_value: Optional[float] = None
    risk: Optional[float] = None
    world_probability: Optional[float] = None
    market_probability: Optional[float] = None
    poisson_probability: Optional[float] = None
    sample_strength: Optional[float] = None
    value_score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        return {k: v for k, v in asdict(self).items() if v is not None}

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExactScore":
        """Create ExactScore from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ScoreGroup:
    """
    Represents a group of related scores (e.g., "HOME_NARROW_WIN", "DRAW_SCENARIO").
    
    Attributes:
        name: Group name (e.g., "HOME_NARROW_WIN")
        scores: List of score strings included in this group
        probability: Combined probability of all scores in the group
        fair_odds: Fair odds for the group (1 / probability)
        confidence: Average confidence of scores in the group
    """
    name: str
    scores: List[str]
    probability: float
    fair_odds: float
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScoreGroup":
        """Create ScoreGroup from dictionary"""
        return cls(**data)


@dataclass
class MultiMatchMath:
    """
    Represents multi-match probability mathematics for combination scenarios.
    
    Attributes:
        combined_probability: Product of individual probabilities
        combined_confidence: Product of individual confidences (confidence decay)
        combined_risk: Sum of individual risk scores (risk accumulation)
        expected_value: Expected value calculation (probability * (odds - 1))
    """
    combined_probability: Optional[float] = None
    combined_confidence: Optional[float] = None
    combined_risk: Optional[float] = None
    expected_value: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        return {k: v for k, v in asdict(self).items() if v is not None}

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MultiMatchMath":
        """Create MultiMatchMath from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ExactScoreMarketKnowledge:
    """
    Main output structure for Exact Score Market Builder.
    Contains all market intelligence data for a single match.
    
    This is the primary interface between Market Intelligence Layer and Strategy Laboratory.
    
    Attributes:
        match_id: Unique identifier for the match
        scores: List of ExactScore objects for all possible outcomes
        groups: List of ScoreGroup objects for grouped scenarios
        combination_math: Optional MultiMatchMath for combination scenarios
        metadata: Additional metadata (source, version, etc.)
    """
    match_id: str
    scores: List[ExactScore]
    groups: List[ScoreGroup]
    combination_math: Optional[MultiMatchMath] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with nested serialization"""
        # Merge custom metadata with defaults
        default_metadata = {"source": "ExactScoreMarketBuilder", "version": "5.2.9.x"}
        final_metadata = {**default_metadata, **(self.metadata or {})}
        
        return {
            "match_id": self.match_id,
            "scores": [s.to_dict() for s in self.scores],
            "groups": [g.to_dict() for g in self.groups],
            "combination_math": self.combination_math.to_dict() if self.combination_math else {},
            "metadata": final_metadata
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to pretty-printed JSON string"""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExactScoreMarketKnowledge":
        """Create ExactScoreMarketKnowledge from dictionary"""
        scores = [ExactScore.from_dict(s) for s in data.get("scores", [])]
        groups = [ScoreGroup.from_dict(g) for g in data.get("groups", [])]
        combination_math = MultiMatchMath.from_dict(data.get("combination_math", {})) if data.get("combination_math") else None
        
        return cls(
            match_id=data.get("match_id", ""),
            scores=scores,
            groups=groups,
            combination_math=combination_math,
            metadata=data.get("metadata", {"source": "ExactScoreMarketBuilder", "version": "5.2.9.x"})
        )


@dataclass
class FusionWeights:
    """
    Configurable weights for probability fusion engine.
    
    Attributes:
        world_base: Base weight for WORLD database (default: 0.4)
        market_base: Base weight for MARKET data (default: 0.3)
        poisson_base: Base weight for POISSON model (default: 0.3)
    """
    world_base: float = 0.4
    market_base: float = 0.3
    poisson_base: float = 0.3

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "FusionWeights":
        """Create FusionWeights from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
