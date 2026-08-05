"""
Tests for market_models.py
Part of SSI V5 - Exact Score Market Builder
"""

import pytest
import json
import sys
sys.path.insert(0, 'D:/sts/aplikacjaTyperBetAi')

from SSI_V5.market.exact_score_engine.market_models import (
    ExactScore,
    ScoreGroup,
    MultiMatchMath,
    ExactScoreMarketKnowledge,
    FusionWeights
)


class TestExactScore:
    """Tests for ExactScore dataclass"""
    
    def test_create_exact_score_basic(self):
        """Test basic ExactScore creation"""
        score = ExactScore(
            score="1:0",
            probability=0.14,
            fair_odds=7.14,
            confidence=0.86
        )
        assert score.score == "1:0"
        assert score.probability == 0.14
        assert score.fair_odds == pytest.approx(7.14)
        assert score.confidence == 0.86
    
    def test_create_exact_score_full(self):
        """Test ExactScore with all optional fields"""
        score = ExactScore(
            score="2:1",
            probability=0.12,
            fair_odds=8.33,
            confidence=0.82,
            market_value=0.26,
            risk=0.15,
            world_probability=0.10,
            market_probability=0.14,
            poisson_probability=0.16,
            sample_strength=0.75,
            value_score=0.22
        )
        assert score.market_value == 0.26
        assert score.world_probability == 0.10
        assert score.sample_strength == 0.75
    
    def test_exact_score_to_dict(self):
        """Test ExactScore serialization to dict"""
        score = ExactScore(
            score="1:0",
            probability=0.14,
            fair_odds=7.14,
            confidence=0.86
        )
        d = score.to_dict()
        assert d["score"] == "1:0"
        assert d["probability"] == 0.14
        assert "world_probability" not in d  # None values excluded
    
    def test_exact_score_to_json(self):
        """Test ExactScore serialization to JSON"""
        score = ExactScore(
            score="1:0",
            probability=0.14,
            fair_odds=7.14,
            confidence=0.86
        )
        json_str = score.to_json()
        assert "1:0" in json_str
        assert "0.14" in json_str
    
    def test_exact_score_from_dict(self):
        """Test ExactScore deserialization from dict"""
        data = {
            "score": "2:0",
            "probability": 0.12,
            "fair_odds": 8.33,
            "confidence": 0.82
        }
        score = ExactScore.from_dict(data)
        assert score.score == "2:0"
        assert score.probability == 0.12
        assert score.fair_odds == pytest.approx(8.33)


class TestScoreGroup:
    """Tests for ScoreGroup dataclass"""
    
    def test_create_score_group(self):
        """Test ScoreGroup creation"""
        group = ScoreGroup(
            name="HOME_NARROW_WIN",
            scores=["1:0", "2:0", "2:1"],
            probability=0.36,
            fair_odds=2.77,
            confidence=0.82
        )
        assert group.name == "HOME_NARROW_WIN"
        assert len(group.scores) == 3
        assert group.probability == pytest.approx(0.36)
        assert group.fair_odds == pytest.approx(2.77)
    
    def test_score_group_to_dict(self):
        """Test ScoreGroup serialization"""
        group = ScoreGroup(
            name="DRAW",
            scores=["0:0", "1:1", "2:2"],
            probability=0.42,
            fair_odds=2.38,
            confidence=0.88
        )
        d = group.to_dict()
        assert d["name"] == "DRAW"
        assert d["probability"] == pytest.approx(0.42)
        assert len(d["scores"]) == 3
    
    def test_score_group_to_json(self):
        """Test ScoreGroup JSON serialization"""
        group = ScoreGroup(
            name="TEST",
            scores=["1:0"],
            probability=0.5,
            fair_odds=2.0,
            confidence=0.9
        )
        json_str = group.to_json()
        assert "TEST" in json_str
        assert "1:0" in json_str
    
    def test_score_group_from_dict(self):
        """Test ScoreGroup deserialization"""
        data = {
            "name": "AWAY_WIN",
            "scores": ["0:1", "0:2"],
            "probability": 0.21,
            "fair_odds": 4.76,
            "confidence": 0.75
        }
        group = ScoreGroup.from_dict(data)
        assert group.name == "AWAY_WIN"
        assert group.fair_odds == pytest.approx(4.76)


class TestMultiMatchMath:
    """Tests for MultiMatchMath dataclass"""
    
    def test_create_multi_match_math(self):
        """Test MultiMatchMath creation"""
        math = MultiMatchMath(
            combined_probability=0.018,
            combined_confidence=0.68,
            combined_risk=0.25,
            expected_value=1.5
        )
        assert math.combined_probability == pytest.approx(0.018)
        assert math.combined_confidence == pytest.approx(0.68)
        assert math.expected_value == pytest.approx(1.5)
    
    def test_multi_match_math_partial(self):
        """Test MultiMatchMath with only some fields"""
        math = MultiMatchMath(
            combined_probability=0.01,
            combined_risk=0.25
        )
        assert math.combined_probability == pytest.approx(0.01)
        assert math.combined_confidence is None
    
    def test_multi_match_math_to_dict(self):
        """Test serialization excluding None values"""
        math = MultiMatchMath(
            combined_probability=0.02,
            combined_confidence=None,
            combined_risk=0.3
        )
        d = math.to_dict()
        assert "combined_probability" in d
        assert "combined_confidence" not in d  # None excluded
        assert d["combined_risk"] == pytest.approx(0.3)
    
    def test_multi_match_math_to_json(self):
        """Test JSON serialization"""
        math = MultiMatchMath(
            combined_probability=0.05,
            combined_confidence=0.75
        )
        json_str = math.to_json()
        assert "combined_probability" in json_str
        assert "0.05" in json_str
    
    def test_multi_match_math_from_dict(self):
        """Test deserialization"""
        data = {
            "combined_probability": 0.03,
            "combined_fair_odds": 33.33,
            "expected_value": 1.0
        }
        math = MultiMatchMath.from_dict(data)
        assert math.combined_probability == pytest.approx(0.03)
        assert math.expected_value == pytest.approx(1.0)


class TestExactScoreMarketKnowledge:
    """Tests for ExactScoreMarketKnowledge dataclass"""
    
    def test_create_market_knowledge(self):
        """Test basic market knowledge creation"""
        score1 = ExactScore("1:0", 0.14, 7.14, 0.86)
        score2 = ExactScore("2:0", 0.12, 8.33, 0.82)
        
        group1 = ScoreGroup("HOME", ["1:0", "2:0"], 0.26, 3.85, 0.84)
        
        knowledge = ExactScoreMarketKnowledge(
            match_id="BAR_RMA",
            scores=[score1, score2],
            groups=[group1]
        )
        assert knowledge.match_id == "BAR_RMA"
        assert len(knowledge.scores) == 2
        assert len(knowledge.groups) == 1
    
    def test_market_knowledge_with_combination_math(self):
        """Test with combination math"""
        score = ExactScore("1:0", 0.14, 7.14, 0.86)
        math = MultiMatchMath(combined_probability=0.02, combined_confidence=0.7)
        
        knowledge = ExactScoreMarketKnowledge(
            match_id="TEST",
            scores=[score],
            groups=[],
            combination_math=math
        )
        assert knowledge.combination_math is not None
        assert knowledge.combination_math.combined_probability == pytest.approx(0.02)
    
    def test_market_knowledge_to_dict(self):
        """Test nested serialization"""
        score = ExactScore("1:0", 0.14, 7.14, 0.86, market_value=0.26)
        group = ScoreGroup("DRAW", ["1:1"], 0.18, 5.55, 0.88)
        
        knowledge = ExactScoreMarketKnowledge(
            match_id="BAR_RMA",
            scores=[score],
            groups=[group],
            metadata={"custom": "value"}
        )
        
        d = knowledge.to_dict()
        assert d["match_id"] == "BAR_RMA"
        assert len(d["scores"]) == 1
        assert d["scores"][0]["score"] == "1:0"
        assert d["scores"][0]["market_value"] == pytest.approx(0.26)
        assert d["groups"][0]["name"] == "DRAW"
        assert "source" in d["metadata"]
    
    def test_market_knowledge_to_json(self):
        """Test JSON serialization with indentation"""
        score = ExactScore("1:0", 0.14, 7.14, 0.86)
        knowledge = ExactScoreMarketKnowledge(
            match_id="TEST",
            scores=[score],
            groups=[]
        )
        
        json_str = knowledge.to_json(indent=2)
        assert "TEST" in json_str
        assert "1:0" in json_str
        assert "\n" in json_str  # Has indentation
    
    def test_market_knowledge_from_dict(self):
        """Test deserialization from dict"""
        data = {
            "match_id": "TEST_MATCH",
            "scores": [
                {"score": "1:0", "probability": 0.14, "fair_odds": 7.14, "confidence": 0.86},
                {"score": "2:0", "probability": 0.12, "fair_odds": 8.33, "confidence": 0.82}
            ],
            "groups": [
                {"name": "HOME", "scores": ["1:0", "2:0"], "probability": 0.26, "fair_odds": 3.85, "confidence": 0.84}
            ]
        }
        
        knowledge = ExactScoreMarketKnowledge.from_dict(data)
        assert knowledge.match_id == "TEST_MATCH"
        assert len(knowledge.scores) == 2
        assert knowledge.scores[0].score == "1:0"
        assert knowledge.groups[0].name == "HOME"


class TestFusionWeights:
    """Tests for FusionWeights dataclass"""
    
    def test_default_weights(self):
        """Test default fusion weights"""
        weights = FusionWeights()
        assert weights.world_base == 0.4
        assert weights.market_base == 0.3
        assert weights.poisson_base == 0.3
    
    def test_custom_weights(self):
        """Test custom fusion weights"""
        weights = FusionWeights(
            world_base=0.5,
            market_base=0.25,
            poisson_base=0.25
        )
        assert weights.world_base == 0.5
        assert weights.market_base == 0.25
    
    def test_weights_to_dict(self):
        """Test weights serialization"""
        weights = FusionWeights()
        d = weights.to_dict()
        assert d["world_base"] == 0.4
        assert d["market_base"] == 0.3
        assert d["poisson_base"] == 0.3
    
    def test_weights_from_dict(self):
        """Test weights deserialization"""
        data = {"world_base": 0.6, "market_base": 0.2, "poisson_base": 0.2}
        weights = FusionWeights.from_dict(data)
        assert weights.world_base == 0.6
        assert weights.market_base == 0.2


class TestEdgeCases:
    """Edge case tests for all models"""
    
    def test_exact_score_with_none_values(self):
        """Test ExactScore with None optional values"""
        score = ExactScore(
            score="0:0",
            probability=0.1,
            fair_odds=10.0,
            confidence=0.5
        )
        d = score.to_dict()
        assert "score" in d
        assert "world_probability" not in d
        assert "market_value" not in d
    
    def test_empty_score_group(self):
        """Test ScoreGroup with empty scores list"""
        group = ScoreGroup("EMPTY", [], 0.0, float('inf'), 0.0)
        assert group.name == "EMPTY"
        assert len(group.scores) == 0
    
    def test_multi_match_math_all_none(self):
        """Test MultiMatchMath with all None values"""
        math = MultiMatchMath()
        d = math.to_dict()
        assert len(d) == 0  # All None values excluded
    
    def test_market_knowledge_empty(self):
        """Test market knowledge with empty lists"""
        knowledge = ExactScoreMarketKnowledge(
            match_id="EMPTY",
            scores=[],
            groups=[]
        )
        assert knowledge.match_id == "EMPTY"
        assert len(knowledge.scores) == 0
        assert len(knowledge.groups) == 0


class TestSerializationRoundtrip:
    """Test that serialization and deserialization preserves data"""
    
    def test_exact_score_roundtrip(self):
        """Test ExactScore serialization roundtrip"""
        original = ExactScore(
            score="3:1",
            probability=0.08,
            fair_odds=12.5,
            confidence=0.75,
            market_value=0.15,
            risk=0.2
        )
        d = original.to_dict()
        restored = ExactScore.from_dict(d)
        
        assert restored.score == original.score
        assert restored.probability == original.probability
        assert restored.fair_odds == original.fair_odds
        assert restored.confidence == original.confidence
        assert restored.market_value == original.market_value
    
    def test_market_knowledge_roundtrip(self):
        """Test full market knowledge serialization roundtrip"""
        score1 = ExactScore("1:0", 0.14, 7.14, 0.86, market_value=0.26)
        score2 = ExactScore("2:0", 0.12, 8.33, 0.82)
        
        group1 = ScoreGroup("HOME", ["1:0", "2:0"], 0.26, 3.85, 0.84)
        group2 = ScoreGroup("DRAW", ["1:1"], 0.18, 5.55, 0.88)
        
        original = ExactScoreMarketKnowledge(
            match_id="BAR_RMA",
            scores=[score1, score2],
            groups=[group1, group2],
            metadata={"version": "5.2.9.x"}
        )
        
        json_str = original.to_json()
        data = json.loads(json_str)
        restored = ExactScoreMarketKnowledge.from_dict(data)
        
        assert restored.match_id == original.match_id
        assert len(restored.scores) == len(original.scores)
        assert len(restored.groups) == len(original.groups)
        assert restored.scores[0].score == original.scores[0].score
        assert restored.groups[1].name == original.groups[1].name


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
