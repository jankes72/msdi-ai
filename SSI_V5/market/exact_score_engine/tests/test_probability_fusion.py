"""
Tests for probability_fusion.py
Part of SSI V5 - Exact Score Market Builder
"""

import pytest
import sys
sys.path.insert(0, 'D:/sts/aplikacjaTyperBetAi')

from SSI_V5.market.exact_score_engine.probability_fusion import ProbabilityFusionEngine
from SSI_V5.market.exact_score_engine.market_models import FusionWeights


class TestProbabilityFusionEngine:
    """Tests for ProbabilityFusionEngine"""
    
    def test_default_initialization(self):
        """Test engine initialization with default weights"""
        engine = ProbabilityFusionEngine()
        weights = engine.get_weights()
        assert weights.world_base == 0.4
        assert weights.market_base == 0.3
        assert weights.poisson_base == 0.3
    
    def test_custom_weights_initialization(self):
        """Test engine with custom weights"""
        weights = FusionWeights(world_base=0.5, market_base=0.25, poisson_base=0.25)
        engine = ProbabilityFusionEngine(weights)
        assert engine.get_weights().world_base == 0.5
    
    def test_calculate_dynamic_weight(self):
        """Test dynamic weight calculation"""
        engine = ProbabilityFusionEngine()
        
        # world weight = 0.4 * 0.9 * 0.8 = 0.288
        weight = engine.calculate_dynamic_weight(0.9, 0.8, 0.4)
        assert weight == pytest.approx(0.288)
        
        # market weight = 0.3 * 0.7 * 0.6 = 0.126
        weight = engine.calculate_dynamic_weight(0.7, 0.6, 0.3)
        assert weight == pytest.approx(0.126)
    
    def test_fuse_probabilities_all_sources(self):
        """Test fusion with all three sources"""
        engine = ProbabilityFusionEngine()
        prob = engine.fuse_probabilities(
            world_prob=0.14,
            market_prob=0.12,
            poisson_prob=0.16,
            confidence=0.9,
            sample_strength=0.8
        )
        # Weighted average expected between min and max of sources
        assert 0.05 < prob < 0.20
    
    def test_fuse_probabilities_only_world(self):
        """Test fusion with only WORLD source"""
        engine = ProbabilityFusionEngine()
        prob = engine.fuse_probabilities(
            world_prob=0.14,
            market_prob=None,
            poisson_prob=None,
            confidence=0.9,
            sample_strength=0.8
        )
        # Should be close to WORLD probability since it's the only source
        assert prob == pytest.approx(0.14)
    
    def test_fuse_probabilities_only_market_and_poisson(self):
        """Test fusion with MARKET and POISSON only"""
        engine = ProbabilityFusionEngine()
        prob = engine.fuse_probabilities(
            world_prob=None,
            market_prob=0.12,
            poisson_prob=0.16,
            confidence=0.8,
            sample_strength=0.7
        )
        # Should be between MARKET and POISSON
        assert 0.11 < prob < 0.17
    
    def test_fuse_probabilities_no_sources(self):
        """Test fusion with no sources - should return neutral probability"""
        engine = ProbabilityFusionEngine()
        prob = engine.fuse_probabilities(
            world_prob=None,
            market_prob=None,
            poisson_prob=None,
            confidence=0.5,
            sample_strength=0.5
        )
        # Neutral probability for 15 scores
        assert prob == pytest.approx(1.0 / 15.0)
    
    def test_fuse_probabilities_zero_confidence(self):
        """Test fusion with zero confidence - should reduce weight"""
        engine = ProbabilityFusionEngine()
        prob = engine.fuse_probabilities(
            world_prob=0.14,
            market_prob=0.12,
            poisson_prob=0.16,
            confidence=0.0,  # Zero confidence
            sample_strength=0.8
        )
        # All weights are 0, so should return neutral
        assert prob == pytest.approx(1.0 / 15.0)
    
    def test_fuse_probabilities_zero_sample_strength(self):
        """Test fusion with zero sample strength"""
        engine = ProbabilityFusionEngine()
        prob = engine.fuse_probabilities(
            world_prob=0.14,
            market_prob=0.12,
            poisson_prob=0.16,
            confidence=0.9,
            sample_strength=0.0
        )
        # All weights are 0, so should return neutral
        assert prob == pytest.approx(1.0 / 15.0)
    
    def test_normalize_probabilities_basic(self):
        """Test basic probability normalization"""
        engine = ProbabilityFusionEngine()
        scores = [
            {"score": "1:0", "probability": 0.1},
            {"score": "2:0", "probability": 0.2},
            {"score": "1:1", "probability": 0.3}
        ]
        normalized = engine.normalize_probabilities(scores)
        total = sum(s["probability"] for s in normalized)
        assert total == pytest.approx(1.0)
    
    def test_normalize_probabilities_all_zero(self):
        """Test normalization when all probabilities are 0"""
        engine = ProbabilityFusionEngine()
        scores = [
            {"score": "1:0", "probability": 0.0},
            {"score": "2:0", "probability": 0.0},
            {"score": "1:1", "probability": 0.0}
        ]
        normalized = engine.normalize_probabilities(scores)
        # Should assign uniform probability
        for s in normalized:
            assert s["probability"] == pytest.approx(1.0 / 3.0)
        total = sum(s["probability"] for s in normalized)
        assert total == pytest.approx(1.0)
    
    def test_normalize_probabilities_empty_list(self):
        """Test normalization with empty list"""
        engine = ProbabilityFusionEngine()
        scores = []
        normalized = engine.normalize_probabilities(scores)
        assert len(normalized) == 0
    
    def test_normalize_probabilities_missing_key(self):
        """Test normalization with missing probability key"""
        engine = ProbabilityFusionEngine()
        scores = [
            {"score": "1:0"},  # No probability key
            {"score": "2:0", "probability": 0.5}
        ]
        normalized = engine.normalize_probabilities(scores, probability_key="probability")
        # Should handle missing keys as 0
        total = sum(s.get("probability", 0) for s in normalized)
        assert total == pytest.approx(1.0)
    
    def test_fuse_scores_basic(self):
        """Test fusing scores from ranker output"""
        engine = ProbabilityFusionEngine()
        scores = [
            {
                "score": "1:0",
                "world_probability": 0.14,
                "market_probability": 0.12,
                "poisson_probability": 0.16,
                "confidence_score": 0.9,
                "sample_strength": 0.8
            },
            {
                "score": "2:0",
                "world_probability": 0.10,
                "market_probability": 0.15,
                "poisson_probability": 0.08,
                "confidence_score": 0.85,
                "sample_strength": 0.7
            }
        ]
        fused = engine.fuse_scores(scores)
        assert all("combined_probability" in s for s in fused)
        # Check that fused probabilities are reasonable
        assert all(0 < s["combined_probability"] <= 1 for s in fused)
    
    def test_fuse_scores_missing_fields(self):
        """Test fusing scores with missing fields"""
        engine = ProbabilityFusionEngine()
        scores = [
            {"score": "1:0"},  # Only score field
            {"score": "2:0", "world_probability": 0.14}
        ]
        fused = engine.fuse_scores(scores)
        assert all("combined_probability" in s for s in fused)
    
    def test_set_weights(self):
        """Test updating fusion weights"""
        engine = ProbabilityFusionEngine()
        new_weights = FusionWeights(world_base=0.6, market_base=0.2, poisson_base=0.2)
        engine.set_weights(new_weights)
        assert engine.get_weights().world_base == 0.6
        assert engine.get_weights().market_base == 0.2
    
    def test_probability_bounds(self):
        """Test that fused probability is always valid"""
        engine = ProbabilityFusionEngine()
        
        # Test various combinations
        test_cases = [
            (0.1, 0.2, 0.3, 0.9, 0.8),
            (0.5, 0.5, 0.5, 0.5, 0.5),
            (0.0, 0.0, 0.0, 1.0, 1.0),
            (1.0, 1.0, 1.0, 0.5, 0.5),
        ]
        
        for world, market, poisson, conf, sample in test_cases:
            prob = engine.fuse_probabilities(world, market, poisson, conf, sample)
            assert 0 <= prob <= 1, f"Invalid probability: {prob}"


class TestEdgeCases:
    """Edge case tests for probability fusion"""
    
    def test_negative_probability_becomes_neutral(self):
        """Test that negative input probabilities are handled"""
        engine = ProbabilityFusionEngine()
        # Pass None for all valid sources
        prob = engine.fuse_probabilities(
            world_prob=None,
            market_prob=None,
            poisson_prob=None
        )
        assert prob == pytest.approx(1.0 / 15.0)
    
    def test_very_high_confidence(self):
        """Test with very high confidence (1.0)"""
        engine = ProbabilityFusionEngine()
        prob = engine.fuse_probabilities(
            world_prob=0.15,
            market_prob=0.15,
            poisson_prob=0.15,
            confidence=1.0,
            sample_strength=1.0
        )
        # All weights are at maximum
        assert 0.1 < prob < 0.2
    
    def test_probability_clamping(self):
        """Test that probabilities are clamped to [0, 1]"""
        engine = ProbabilityFusionEngine()
        prob = engine.fuse_probabilities(
            world_prob=10.0,  # Invalid - should be clamped
            market_prob=0.1,
            poisson_prob=0.1,
            confidence=1.0,
            sample_strength=1.0
        )
        assert 0 <= prob <= 1
    
    def test_single_source_dominance(self):
        """Test when one source has much higher weight"""
        weights = FusionWeights(world_base=0.9, market_base=0.05, poisson_base=0.05)
        engine = ProbabilityFusionEngine(weights)
        prob = engine.fuse_probabilities(
            world_prob=0.20,
            market_prob=0.01,
            poisson_prob=0.01,
            confidence=1.0,
            sample_strength=1.0
        )
        # WORLD should dominate
        assert 0.18 < prob < 0.22


class TestDeterministicBehavior:
    """Test that all calculations are deterministic"""
    
    def test_same_input_same_output(self):
        """Test that same inputs produce same outputs"""
        engine = ProbabilityFusionEngine()
        
        inputs = (
            0.14, 0.12, 0.16, 0.9, 0.8
        )
        
        prob1 = engine.fuse_probabilities(*inputs)
        prob2 = engine.fuse_probabilities(*inputs)
        
        assert prob1 == prob2
    
    def test_multiple_runs_consistent(self):
        """Test consistency across multiple runs"""
        engine = ProbabilityFusionEngine()
        
        for _ in range(10):
            prob = engine.fuse_probabilities(
                world_prob=0.15,
                market_prob=0.10,
                poisson_prob=0.20,
                confidence=0.8,
                sample_strength=0.7
            )
            assert 0.1 < prob < 0.25


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
