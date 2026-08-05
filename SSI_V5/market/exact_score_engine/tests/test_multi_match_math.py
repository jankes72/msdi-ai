"""
Test suite for MultiMatchMathEngine module
Part of SSI V5 - Market Intelligence Knowledge Layer

Tests cover:
- Combined probability calculation (product of probabilities)
- Confidence decay (product, geometric mean, harmonic mean)
- Risk accumulation (sum of risks)
- Expected value calculation
- MultiMatchResult dataclass
- Edge cases and boundary conditions
"""

import pytest
from typing import Dict, List
from SSI_V5.market.exact_score_engine.multi_match_math import (
    MultiMatchMathEngine,
    MultiMatchResult
)


class TestCombinedProbability:
    """Tests for combined probability calculation"""
    
    def setup_method(self):
        self.engine = MultiMatchMathEngine()
    
    def test_combined_probability_basic(self):
        """Test basic combined probability: P(A AND B) = P(A) * P(B)"""
        result = self.engine.calculate_combined_probability([0.5, 0.5])
        assert result == 0.25
    
    def test_combined_probability_multiple(self):
        """Test with multiple probabilities"""
        result = self.engine.calculate_combined_probability([0.1, 0.2, 0.5])
        assert result == pytest.approx(0.01)  # 0.1 * 0.2 * 0.5 = 0.01
    
    def test_combined_probability_empty(self):
        """Test with empty list returns 1.0 (identity for multiplication)"""
        result = self.engine.calculate_combined_probability([])
        assert result == 1.0
    
    def test_combined_probability_single(self):
        """Test with single probability"""
        result = self.engine.calculate_combined_probability([0.75])
        assert result == 0.75
    
    def test_combined_probability_zero(self):
        """Test that any zero probability results in zero combined"""
        result = self.engine.calculate_combined_probability([0.5, 0.0, 0.5])
        assert result == 0.0
    
    def test_combined_probability_one(self):
        """Test that multiplying by 1 has no effect"""
        result = self.engine.calculate_combined_probability([0.5, 1.0, 0.5])
        assert result == 0.25  # 0.5 * 1.0 * 0.5 = 0.25
    
    def test_combined_probability_very_small(self):
        """Test with very small probabilities"""
        result = self.engine.calculate_combined_probability([0.1, 0.1, 0.1])
        assert result == pytest.approx(0.001)


class TestConfidenceDecayProduct:
    """Tests for confidence decay using product method"""
    
    def setup_method(self):
        self.engine = MultiMatchMathEngine()
    
    def test_confidence_product_basic(self):
        """Test basic product confidence: c1 * c2 * ... * cn"""
        result = self.engine.calculate_combined_confidence_product([0.9, 0.9])
        assert result == 0.81
    
    def test_confidence_product_empty(self):
        """Test empty list returns 1.0"""
        result = self.engine.calculate_combined_confidence_product([])
        assert result == 1.0
    
    def test_confidence_product_single(self):
        """Test single confidence value"""
        result = self.engine.calculate_combined_confidence_product([0.75])
        assert result == 0.75
    
    def test_confidence_product_zero(self):
        """Test that any zero confidence results in zero"""
        result = self.engine.calculate_combined_confidence_product([0.9, 0.0, 0.9])
        assert result == 0.0
    
    def test_confidence_product_all_ones(self):
        """Test all ones remains one"""
        result = self.engine.calculate_combined_confidence_product([1.0, 1.0, 1.0])
        assert result == 1.0
    
    def test_confidence_product_conservative(self):
        """Test that product is conservative (all must be correct)"""
        # Even with high confidences, product can get small quickly
        result = self.engine.calculate_combined_confidence_product([0.9, 0.9, 0.9])
        assert result == pytest.approx(0.729)  # 0.9^3


class TestConfidenceDecayGeometricMean:
    """Tests for confidence decay using geometric mean"""
    
    def setup_method(self):
        self.engine = MultiMatchMathEngine()
    
    def test_geometric_mean_basic(self):
        """Test basic geometric mean: (c1 * c2)^(1/2)"""
        result = self.engine.calculate_combined_confidence_geometric_mean([0.81, 0.81])
        assert abs(result - 0.81) < 1e-10  # sqrt(0.81 * 0.81) = 0.81
    
    def test_geometric_mean_different(self):
        """Test geometric mean with different values"""
        result = self.engine.calculate_combined_confidence_geometric_mean([0.64, 0.81])
        expected = (0.64 * 0.81) ** 0.5
        assert abs(result - expected) < 1e-10
    
    def test_geometric_mean_empty(self):
        """Test empty list returns 0.0"""
        result = self.engine.calculate_combined_confidence_geometric_mean([])
        assert result == 0.0
    
    def test_geometric_mean_single(self):
        """Test single value geometric mean"""
        result = self.engine.calculate_combined_confidence_geometric_mean([0.64])
        assert result == 0.64
    
    def test_geometric_mean_zero(self):
        """Test geometric mean with zero"""
        result = self.engine.calculate_combined_confidence_geometric_mean([0.9, 0.0])
        assert result == 0.0
    
    def test_geometric_mean_wless_conservative_than_product(self):
        """Test that geometric mean is less conservative than product"""
        confidences = [0.9, 0.9, 0.9]
        product = self.engine.calculate_combined_confidence_product(confidences)
        geometric = self.engine.calculate_combined_confidence_geometric_mean(confidences)
        
        # For n > 1, geometric mean > product when all c < 1
        assert geometric > product


class TestConfidenceDecayHarmonicMean:
    """Tests for confidence decay using harmonic mean"""
    
    def setup_method(self):
        self.engine = MultiMatchMathEngine()
    
    def test_harmonic_mean_basic(self):
        """Test basic harmonic mean: n / (1/c1 + 1/c2 + ...)"""
        result = self.engine.calculate_combined_confidence_harmonic_mean([0.5, 0.5])
        expected = 2.0 / (1/0.5 + 1/0.5)  # 2 / (2 + 2) = 2/4 = 0.5
        assert abs(result - expected) < 1e-10
    
    def test_harmonic_mean_empty(self):
        """Test empty list returns 0.0"""
        result = self.engine.calculate_combined_confidence_harmonic_mean([])
        assert result == 0.0
    
    def test_harmonic_mean_single(self):
        """Test single value harmonic mean"""
        result = self.engine.calculate_combined_confidence_harmonic_mean([0.75])
        assert result == 0.75
    
    def test_harmonic_mean_zero(self):
        """Test harmonic mean with zero"""
        result = self.engine.calculate_combined_confidence_harmonic_mean([0.5, 0.0, 0.5])
        # With zero in the list, zeros are filtered out but n is still 3
        # non_zero = [0.5, 0.5], sum_of_reciprocals = 1/0.5 + 1/0.5 = 4
        # result = 3 / 4 = 0.75
        assert result == pytest.approx(0.75)
    
    def test_harmonic_mean_gives_less_weight_to_low_values(self):
        """Test that harmonic mean gives more weight to lower values"""
        # Harmonic mean is more sensitive to small values than arithmetic mean
        confidences = [0.1, 0.9]
        result = self.engine.calculate_combined_confidence_harmonic_mean(confidences)
        
        # Harmonic mean should be closer to 0.1 than to 0.9
        # HM = 2 / (10 + 1/0.9) = 2 / 11.111... ≈ 0.18
        assert result < 0.2


class TestCombinedConfidenceMethod:
    """Tests for the combined confidence method selection"""
    
    def setup_method(self):
        self.engine = MultiMatchMathEngine()
    
    def test_combined_confidence_product_method(self):
        """Test product method selection"""
        result = self.engine.calculate_combined_confidence(
            [0.5, 0.5], method="product"
        )
        assert result == 0.25
    
    def test_combined_confidence_geometric_method(self):
        """Test geometric mean method selection"""
        result = self.engine.calculate_combined_confidence(
            [0.64, 0.81], method="geometric_mean"
        )
        expected = (0.64 * 0.81) ** 0.5
        assert abs(result - expected) < 1e-10
    
    def test_combined_confidence_harmonic_method(self):
        """Test harmonic mean method selection"""
        result = self.engine.calculate_combined_confidence(
            [0.5, 0.5], method="harmonic_mean"
        )
        assert abs(result - 0.5) < 1e-10
    
    def test_combined_confidence_unknown_method(self):
        """Test that unknown method raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            self.engine.calculate_combined_confidence([0.5, 0.5], method="unknown")
        assert "Unknown confidence method" in str(exc_info.value)
    
    def test_combined_confidence_default_is_product(self):
        """Test that default method is product"""
        result = self.engine.calculate_combined_confidence([0.5, 0.5])
        assert result == 0.25  # Same as product


class TestRiskAccumulation:
    """Tests for risk accumulation (sum)"""
    
    def setup_method(self):
        self.engine = MultiMatchMathEngine()
    
    def test_combined_risk_basic(self):
        """Test basic risk accumulation: r1 + r2 + ... + rn"""
        result = self.engine.calculate_combined_risk([0.1, 0.2, 0.3])
        assert result == 0.6
    
    def test_combined_risk_empty(self):
        """Test empty list returns 0.0"""
        result = self.engine.calculate_combined_risk([])
        assert result == 0.0
    
    def test_combined_risk_single(self):
        """Test single risk value"""
        result = self.engine.calculate_combined_risk([0.25])
        assert result == 0.25
    
    def test_combined_risk_negative_clamped(self):
        """Test that negative risks are clamped to 0"""
        result = self.engine.calculate_combined_risk([0.1, -0.1, 0.2])
        assert result == pytest.approx(0.3)  # -0.1 clamped to 0
    
    def test_combined_risk_all_negative(self):
        """Test that all negative risks result in 0"""
        result = self.engine.calculate_combined_risk([-0.1, -0.2, -0.3])
        assert result == 0.0
    
    def test_combined_risk_zero(self):
        """Test that zero risks don't affect sum"""
        result = self.engine.calculate_combined_risk([0.1, 0.0, 0.2])
        assert result == pytest.approx(0.3)


class TestExpectedValue:
    """Tests for expected value calculation"""
    
    def setup_method(self):
        self.engine = MultiMatchMathEngine()
    
    def test_expected_value_basic(self):
        """Test basic expected value: EV = probability * (odds - 1)"""
        ev = self.engine.calculate_expected_value(0.1, 10.0)
        assert ev == 0.9  # 0.1 * (10 - 1) = 0.9
    
    def test_expected_value_at_fair_odds(self):
        """Test EV at fair odds: EV = p * (1/p - 1) = 1 - p"""
        p, odds = 0.25, 4.0
        ev = self.engine.calculate_expected_value(p, odds)
        assert ev == pytest.approx(0.75)  # 0.25 * (4 - 1) = 0.75
    
    def test_expected_value_zero_probability(self):
        """Test EV with zero probability"""
        ev = self.engine.calculate_expected_value(0.0, 10.0)
        assert ev == 0.0
    
    def test_expected_value_very_low_probability(self):
        """Test EV with very low probability"""
        ev = self.engine.calculate_expected_value(0.01, 100.0)
        assert ev == pytest.approx(0.99)  # 0.01 * (100 - 1) = 0.99
    
    def test_expected_value_high_probability(self):
        """Test EV with high probability and low odds"""
        ev = self.engine.calculate_expected_value(0.9, 1.111)  # 1.111 ≈ 1/0.9
        assert abs(ev - 0.1) < 0.001  # 0.9 * (1.111 - 1) ≈ 0.1


class TestCombinedFairOdds:
    """Tests for combined fair odds calculation"""
    
    def setup_method(self):
        self.engine = MultiMatchMathEngine()
    
    def test_combined_fair_odds_basic(self):
        """Test combined fair odds: odds1 * odds2 * ... * oddsn"""
        result = self.engine.calculate_combined_fair_odds([2.0, 3.0, 5.0])
        assert result == 30.0  # 2 * 3 * 5 = 30
    
    def test_combined_fair_odds_empty(self):
        """Test empty list returns 1.0"""
        result = self.engine.calculate_combined_fair_odds([])
        assert result == 1.0
    
    def test_combined_fair_odds_single(self):
        """Test single odds value"""
        result = self.engine.calculate_combined_fair_odds([10.0])
        assert result == 10.0
    
    def test_combined_fair_odds_with_zero(self):
        """Test that any zero odds results in zero combined"""
        result = self.engine.calculate_combined_fair_odds([2.0, 0.0, 3.0])
        assert result == 0.0
    
    def test_combined_fair_odds_with_infinity(self):
        """Test with infinity odds"""
        result = self.engine.calculate_combined_fair_odds([2.0, float('inf')])
        assert result == float('inf')


class TestCalculateCombination:
    """Tests for the main calculate_combination method"""
    
    def setup_method(self):
        self.engine = MultiMatchMathEngine()
    
    def test_calculate_combination_basic(self):
        """Test basic combination calculation"""
        result = self.engine.calculate_combination(
            probabilities=[0.15, 0.12],
            confidences=[0.85, 0.80],
            risk_scores=[0.15, 0.20],
            fair_odds_list=[6.67, 8.33]
        )
        
        assert result.combined_probability == pytest.approx(0.018)  # 0.15 * 0.12
        assert result.combined_confidence == pytest.approx(0.68)    # 0.85 * 0.80
        assert result.combined_risk == pytest.approx(0.35)           # 0.15 + 0.20
        assert result.combined_fair_odds == pytest.approx(6.67 * 8.33, rel=1e-3)  # 6.67 * 8.33
        assert result.num_matches == 2
    
    def test_calculate_combination_with_different_confidence_method(self):
        """Test combination with geometric mean confidence"""
        result = self.engine.calculate_combination(
            probabilities=[0.5, 0.5],
            confidences=[0.64, 0.81],
            risk_scores=[0.1, 0.1],
            fair_odds_list=[2.0, 2.0],
            confidence_method="geometric_mean"
        )
        
        expected_conf = (0.64 * 0.81) ** 0.5
        assert abs(result.combined_confidence - expected_conf) < 1e-10
    
    def test_calculate_combination_to_dict(self):
        """Test MultiMatchResult to_dict method"""
        result = self.engine.calculate_combination(
            probabilities=[0.5],
            confidences=[0.8],
            risk_scores=[0.2],
            fair_odds_list=[2.0]
        )
        
        data = result.to_dict()
        assert "combined_probability" in data
        assert "combined_confidence" in data
        assert "combined_risk" in data
        assert "combined_fair_odds" in data
        assert "expected_value" in data
        assert "num_matches" in data


class TestMultiMatchResultDataclass:
    """Tests for MultiMatchResult dataclass"""
    
    def test_multimatch_result_defaults(self):
        """Test MultiMatchResult with all required fields"""
        result = MultiMatchResult(
            combined_probability=0.1,
            combined_fair_odds=10.0,
            combined_confidence=0.8,
            combined_risk=0.2,
            expected_value=0.9,
            num_matches=2
        )
        
        assert result.combined_probability == 0.1
        assert result.combined_fair_odds == 10.0
        assert result.combined_confidence == 0.8
        assert result.combined_risk == 0.2
        assert result.expected_value == 0.9
        assert result.num_matches == 2


class TestPairwiseCombinations:
    """Tests for pairwise combination generation"""
    
    def setup_method(self):
        self.engine = MultiMatchMathEngine()
    
    def test_pairwise_combinations_empty(self):
        """Test with empty input"""
        result = self.engine.calculate_pairwise_combinations([])
        assert result == []
    
    def test_pairwise_combinations_single_match(self):
        """Test with single match (no combinations possible)"""
        match1_scores = [
            {"score": "1:0", "probability": 0.5, "fair_odds": 2.0, "confidence": 0.8, "risk": 0.2}
        ]
        result = self.engine.calculate_pairwise_combinations([match1_scores])
        
        # Should have 1 combination with 1 score
        assert len(result) == 1
        assert result[0]["scores"] == ["1:0"]
        assert result[0]["num_matches"] == 1
    
    def test_pairwise_combinations_two_matches(self):
        """Test with two matches"""
        match1_scores = [
            {"score": "1:0", "probability": 0.5, "fair_odds": 2.0, "confidence": 0.8, "risk": 0.2}
        ]
        match2_scores = [
            {"score": "1:0", "probability": 0.5, "fair_odds": 2.0, "confidence": 0.8, "risk": 0.2}
        ]
        
        result = self.engine.calculate_pairwise_combinations([match1_scores, match2_scores])
        
        # Should have 1 * 1 = 1 combination
        assert len(result) == 1
        assert result[0]["scores"] == ["1:0", "1:0"]
        assert result[0]["num_matches"] == 2
    
    def test_pairwise_combinations_multiple_per_match(self):
        """Test with multiple scores per match"""
        match1_scores = [
            {"score": "1:0", "probability": 0.5, "fair_odds": 2.0, "confidence": 0.8, "risk": 0.2},
            {"score": "2:0", "probability": 0.3, "fair_odds": 3.33, "confidence": 0.7, "risk": 0.3}
        ]
        match2_scores = [
            {"score": "0:0", "probability": 0.4, "fair_odds": 2.5, "confidence": 0.9, "risk": 0.1}
        ]
        
        result = self.engine.calculate_pairwise_combinations([match1_scores, match2_scores])
        
        # Should have 2 * 1 = 2 combinations
        assert len(result) == 2
        assert result[0]["scores"] == ["1:0", "0:0"]
        assert result[1]["scores"] == ["2:0", "0:0"]


class TestCumulativeMetrics:
    """Tests for cumulative metrics calculation"""
    
    def setup_method(self):
        self.engine = MultiMatchMathEngine()
    
    def test_cumulative_metrics_empty(self):
        """Test cumulative metrics with empty data"""
        result = self.engine.calculate_cumulative_metrics([])
        
        assert result["total_matches"] == 0
        assert result["total_probability"] == 0.0
        assert result["total_fair_odds"] == 1.0
        assert result["avg_confidence"] == 0.0
        assert result["total_risk"] == 0.0
        assert result["avg_expected_value"] == 0.0
    
    def test_cumulative_metrics_single(self):
        """Test cumulative metrics with single match"""
        data = [
            {"probability": 0.5, "fair_odds": 2.0, "confidence": 0.8, "risk": 0.2}
        ]
        result = self.engine.calculate_cumulative_metrics(data)
        
        assert result["total_matches"] == 1
        assert result["total_probability"] == 0.5
        assert result["total_fair_odds"] == pytest.approx(2.0)
        assert result["avg_confidence"] == 0.8
        assert result["total_risk"] == 0.2
    
    def test_cumulative_metrics_multiple(self):
        """Test cumulative metrics with multiple matches"""
        data = [
            {"probability": 0.5, "fair_odds": 2.0, "confidence": 0.8, "risk": 0.2},
            {"probability": 0.3, "fair_odds": 3.33, "confidence": 0.7, "risk": 0.3}
        ]
        result = self.engine.calculate_cumulative_metrics(data)
        
        assert result["total_matches"] == 2
        assert result["total_probability"] == pytest.approx(0.8)
        assert result["total_fair_odds"] == pytest.approx(2.0 * 3.33)
        assert result["avg_confidence"] == pytest.approx(0.75)
        assert result["total_risk"] == pytest.approx(0.5)


class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""
    
    def setup_method(self):
        self.engine = MultiMatchMathEngine()
    
    def test_very_small_probabilities(self):
        """Test with very small probability values"""
        probs = [0.001, 0.001, 0.001]
        result = self.engine.calculate_combined_probability(probs)
        assert result == pytest.approx(1e-9)
    
    def test_very_large_odds(self):
        """Test with very large odds values"""
        odds = [1000.0, 1000.0]
        result = self.engine.calculate_combined_fair_odds(odds)
        assert result == pytest.approx(1e6)
    
    def test_zero_risk_values(self):
        """Test with zero risk values"""
        risks = [0.0, 0.0, 0.0]
        result = self.engine.calculate_combined_risk(risks)
        assert result == 0.0
    
    def test_one_confidence_values(self):
        """Test with all confidence = 1.0"""
        confs = [1.0, 1.0, 1.0]
        result_product = self.engine.calculate_combined_confidence_product(confs)
        result_geometric = self.engine.calculate_combined_confidence_geometric_mean(confs)
        result_harmonic = self.engine.calculate_combined_confidence_harmonic_mean(confs)
        
        assert result_product == 1.0
        assert result_geometric == 1.0
        assert result_harmonic == 1.0
    
    def test_negative_probability_handling(self):
        """Test handling of negative probabilities in combined calculation"""
        # The method doesn't validate, but negative probs still multiply
        result = self.engine.calculate_combined_probability([0.5, -0.5, 0.5])
        assert result < 0  # 0.5 * -0.5 * 0.5 = -0.125


class TestDeterministic:
    """Tests to ensure deterministic behavior"""
    
    def setup_method(self):
        self.engine = MultiMatchMathEngine()
    
    def test_deterministic_combined_probability(self):
        """Test that combined probability is deterministic"""
        probs = [0.1432, 0.2864, 0.5108]
        for _ in range(5):
            result = self.engine.calculate_combined_probability(probs)
            assert result == pytest.approx(0.1432 * 0.2864 * 0.5108)
    
    def test_deterministic_combined_fair_odds(self):
        """Test that combined odds is deterministic"""
        odds = [2.5, 3.5, 4.5]
        for _ in range(5):
            result = self.engine.calculate_combined_fair_odds(odds)
            expected = 2.5 * 3.5 * 4.5
            assert result == pytest.approx(expected)


class TestMathematicalIdentities:
    """Tests for mathematical identities and properties"""
    
    def setup_method(self):
        self.engine = MultiMatchMathEngine()
    
    def test_probability_identity(self):
        """Test that multiplying by 1 doesn't change result"""
        result1 = self.engine.calculate_combined_probability([0.5, 0.5])
        result2 = self.engine.calculate_combined_probability([0.5, 1.0, 0.5])
        assert result1 == pytest.approx(result2)
    
    def test_commutative_property(self):
        """Test that probability multiplication is commutative"""
        result1 = self.engine.calculate_combined_probability([0.1, 0.2, 0.3])
        result2 = self.engine.calculate_combined_probability([0.3, 0.2, 0.1])
        assert result1 == pytest.approx(result2)
    
    def test_associative_property(self):
        """Test that probability multiplication is associative"""
        # (a * b) * c = a * (b * c)
        probs1 = [0.1 * 0.2, 0.3]  # (0.1 * 0.2) * 0.3
        probs2 = [0.1, 0.2 * 0.3]  # 0.1 * (0.2 * 0.3)
        
        result1 = self.engine.calculate_combined_probability(probs1)
        result2 = self.engine.calculate_combined_probability(probs2)
        
        assert result1 == pytest.approx(result2)


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
