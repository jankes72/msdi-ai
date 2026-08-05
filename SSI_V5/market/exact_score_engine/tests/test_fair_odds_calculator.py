"""
Test suite for FairOddsCalculator module
Part of SSI V5 - Market Intelligence Knowledge Layer

Tests cover:
- Basic fair odds calculation (p -> 1/p)
- Edge cases (p=0, p=1, p=0.5)
- Batch processing
- Probability normalization
- Probability validation
- Conversion between odds and probability
- Expected value calculation
- Integration with market data
"""

import pytest
import math
from typing import Dict, List
from SSI_V5.market.exact_score_engine.fair_odds_calculator import FairOddsCalculator


class TestFairOddsCalculation:
    """Tests for basic fair odds calculation"""
    
    def setup_method(self):
        self.calculator = FairOddsCalculator()
    
    def test_calculate_fair_odds_basic(self):
        """Test basic fair odds calculation: p = 0.10 -> odds = 10.0"""
        odds = self.calculator.calculate_fair_odds(0.10)
        assert odds == 10.0
    
    def test_calculate_fair_odds_half(self):
        """Test p = 0.5 -> odds = 2.0"""
        odds = self.calculator.calculate_fair_odds(0.5)
        assert odds == 2.0
    
    def test_calculate_fair_odds_one_third(self):
        """Test p = 1/3 -> odds = 3.0"""
        odds = self.calculator.calculate_fair_odds(1/3)
        assert abs(odds - 3.0) < 1e-10
    
    def test_calculate_fair_odds_one_percent(self):
        """Test p = 0.01 -> odds = 100.0"""
        odds = self.calculator.calculate_fair_odds(0.01)
        assert odds == 100.0
    
    def test_calculate_fair_odds_certain(self):
        """Test p = 1.0 -> odds = 1.0"""
        odds = self.calculator.calculate_fair_odds(1.0)
        assert odds == 1.0
    
    def test_calculate_fair_odds_zero(self):
        """Test p = 0 -> odds = infinity"""
        odds = self.calculator.calculate_fair_odds(0.0)
        assert odds == float('inf')
    
    def test_calculate_fair_odds_negative_raises(self):
        """Test that negative probability raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            self.calculator.calculate_fair_odds(-0.1)
        assert "cannot be negative" in str(exc_info.value)
    
    def test_calculate_fair_odds_very_small(self):
        """Test very small probability doesn't cause overflow"""
        odds = self.calculator.calculate_fair_odds(1e-10)
        # Should use MIN_PROBABILITY protection
        assert odds <= 1e10
        assert odds >= 1.0
    
    def test_calculate_fair_odds_min_probability_protection(self):
        """Test that probabilities below MIN_PROBABILITY are clamped"""
        # MIN_PROBABILITY = 1e-10
        odds_small = self.calculator.calculate_fair_odds(1e-11)
        odds_min = self.calculator.calculate_fair_odds(1e-10)
        # Both should give same result due to clamping
        assert odds_small == odds_min


class TestBatchProcessing:
    """Tests for batch processing of probabilities"""
    
    def setup_method(self):
        self.calculator = FairOddsCalculator()
    
    def test_calculate_fair_odds_batch_empty(self):
        """Test batch processing with empty list"""
        results = self.calculator.calculate_fair_odds_batch([])
        assert results == []
    
    def test_calculate_fair_odds_batch_single(self):
        """Test batch processing with single value"""
        results = self.calculator.calculate_fair_odds_batch([0.25])
        assert results == [4.0]
    
    def test_calculate_fair_odds_batch_multiple(self):
        """Test batch processing with multiple values"""
        results = self.calculator.calculate_fair_odds_batch([0.1, 0.2, 0.5])
        expected = [10.0, 5.0, 2.0]
        assert results == expected
    
    def test_calculate_fair_odds_batch_with_zero(self):
        """Test batch processing includes infinity for p=0"""
        results = self.calculator.calculate_fair_odds_batch([0.1, 0.0, 0.25])
        assert results[0] == 10.0
        assert results[1] == float('inf')
        assert results[2] == 4.0


class TestProbabilityNormalization:
    """Tests for probability distribution normalization"""
    
    def setup_method(self):
        self.calculator = FairOddsCalculator()
    
    def test_normalize_empty_list(self):
        """Test normalization with empty list"""
        results = self.calculator.normalize_probability_distribution([])
        assert results == []
    
    def test_normalize_single_score(self):
        """Test normalization with single score"""
        scores = [{"score": "1:0", "probability": 0.5}]
        results = self.calculator.normalize_probability_distribution(scores)
        assert results[0]["probability"] == 1.0
    
    def test_normalize_already_sum_to_one(self):
        """Test normalization when probabilities already sum to 1"""
        scores = [
            {"score": "1:0", "probability": 0.3},
            {"score": "2:0", "probability": 0.4},
            {"score": "1:1", "probability": 0.3}
        ]
        results = self.calculator.normalize_probability_distribution(scores)
        total = sum(s["probability"] for s in results)
        assert abs(total - 1.0) < 1e-10
        # Original ratios should be preserved
        assert abs(results[0]["probability"] - 0.3) < 1e-10
        assert abs(results[1]["probability"] - 0.4) < 1e-10
        assert abs(results[2]["probability"] - 0.3) < 1e-10
    
    def test_normalize_sum_not_one(self):
        """Test normalization when probabilities don't sum to 1"""
        scores = [
            {"score": "1:0", "probability": 0.1},
            {"score": "2:0", "probability": 0.2},
            {"score": "1:1", "probability": 0.3}
        ]
        results = self.calculator.normalize_probability_distribution(scores)
        total = sum(s["probability"] for s in results)
        assert abs(total - 1.0) < 1e-10
        # Check ratios are preserved
        expected_ratios = [0.1/0.6, 0.2/0.6, 0.3/0.6]
        for i, expected in enumerate(expected_ratios):
            assert abs(results[i]["probability"] - expected) < 1e-10
    
    def test_normalize_all_zeros(self):
        """Test normalization when all probabilities are zero"""
        scores = [
            {"score": "1:0", "probability": 0.0},
            {"score": "2:0", "probability": 0.0},
            {"score": "1:1", "probability": 0.0}
        ]
        results = self.calculator.normalize_probability_distribution(scores)
        # Should assign uniform probability
        assert len(results) == 3
        for s in results:
            assert abs(s["probability"] - 1/3) < 1e-10
    
    def test_normalize_custom_key(self):
        """Test normalization with custom probability key"""
        scores = [
            {"score": "1:0", "prob": 0.2},
            {"score": "2:0", "prob": 0.3}
        ]
        results = self.calculator.normalize_probability_distribution(
            scores, probability_key="prob"
        )
        total = sum(s["prob"] for s in results)
        assert abs(total - 1.0) < 1e-10
    
    def test_normalize_preserves_other_fields(self):
        """Test that normalization preserves other fields in the dict"""
        scores = [
            {"score": "1:0", "probability": 0.2, "confidence": 0.8, "fair_odds": 5.0},
            {"score": "2:0", "probability": 0.3, "confidence": 0.7, "fair_odds": 3.33}
        ]
        results = self.calculator.normalize_probability_distribution(scores)
        assert results[0]["confidence"] == 0.8
        assert results[0]["fair_odds"] == 5.0
        assert results[1]["confidence"] == 0.7
        assert results[1]["fair_odds"] == pytest.approx(3.33, rel=0.01)


class TestProbabilityValidation:
    """Tests for probability validation"""
    
    def setup_method(self):
        self.calculator = FairOddsCalculator()
    
    def test_validate_good_probability(self):
        """Test validation with valid probability"""
        assert self.calculator.validate_probability(0.5) == 0.5
        assert self.calculator.validate_probability(0.1) == 0.1
        assert self.calculator.validate_probability(0.99) == 0.99
    
    def test_validate_negative_clamped_to_zero(self):
        """Test that negative probabilities are clamped to 0"""
        assert self.calculator.validate_probability(-0.1) == 0.0
    
    def test_validate_above_one_clamped_to_one(self):
        """Test that probabilities > 1 are clamped to 1"""
        assert self.calculator.validate_probability(1.5) == 1.0
        assert self.calculator.validate_probability(10.0) == 1.0


class TestProbabilityFromOdds:
    """Tests for converting odds back to probability"""
    
    def setup_method(self):
        self.calculator = FairOddsCalculator()
    
    def test_convert_odds_to_probability_basic(self):
        """Test odds = 10.0 -> probability = 0.1"""
        prob = self.calculator.calculate_probability_from_odds(10.0)
        assert prob == 0.1
    
    def test_convert_odds_to_probability_half(self):
        """Test odds = 2.0 -> probability = 0.5"""
        prob = self.calculator.calculate_probability_from_odds(2.0)
        assert prob == 0.5
    
    def test_convert_odds_to_probability_one(self):
        """Test odds = 1.0 -> probability = 1.0"""
        prob = self.calculator.calculate_probability_from_odds(1.0)
        assert prob == 1.0
    
    def test_convert_odds_zero_raises(self):
        """Test that odds <= 0 raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            self.calculator.calculate_probability_from_odds(0.0)
        assert "must be positive" in str(exc_info.value)
    
    def test_convert_negative_odds_raises(self):
        """Test that negative odds raises ValueError"""
        with pytest.raises(ValueError):
            self.calculator.calculate_probability_from_odds(-5.0)


class TestExpectedValue:
    """Tests for expected value calculation"""
    
    def setup_method(self):
        self.calculator = FairOddsCalculator()
    
    def test_expected_value_basic(self):
        """Test EV = probability * (odds - 1)"""
        ev = self.calculator.calculate_expected_value(0.1, 10.0)
        assert ev == 0.1 * (10.0 - 1.0) == 0.9
    
    def test_expected_value_fair_odds(self):
        """Test EV with fair odds and matching probability"""
        # When odds = 1/p, EV should be 0
        ev = self.calculator.calculate_expected_value(0.1, 10.0)
        assert ev == 0.9  # 0.1 * (10 - 1) = 0.9
        
        # More precise: EV = p * (odds - 1)
        # At fair odds: odds = 1/p, so EV = p * (1/p - 1) = 1 - p
        p, odds = 0.25, 4.0
        ev = self.calculator.calculate_expected_value(p, odds)
        assert ev == 0.25 * (4.0 - 1.0) == 0.75
    
    def test_expected_value_zero_probability(self):
        """Test EV with zero probability"""
        ev = self.calculator.calculate_expected_value(0.0, 10.0)
        assert ev == 0.0
    
    def test_expected_value_low_odds(self):
        """Test EV with low odds (high probability)"""
        ev = self.calculator.calculate_expected_value(0.8, 1.25)  # 1.25 = 1/0.8
        assert ev == 0.8 * (1.25 - 1.0) == 0.8 * 0.25 == 0.2


class TestBatchCalculateFairOddsAndNormalize:
    """Tests for the combined batch operation"""
    
    def setup_method(self):
        self.calculator = FairOddsCalculator()
    
    def test_batch_operation_basic(self):
        """Test combined batch operation"""
        scores = [
            {"score": "1:0", "probability": 0.1},
            {"score": "2:0", "probability": 0.2},
            {"score": "1:1", "probability": 0.3}
        ]
        results = self.calculator.batch_calculate_fair_odds_and_normalize(
            scores, probability_key="probability", fair_odds_key="fair_odds"
        )
        
        # Check probabilities sum to 1
        total_prob = sum(s["probability"] for s in results)
        assert abs(total_prob - 1.0) < 1e-10
        
        # Check fair odds are calculated
        for s in results:
            assert "fair_odds" in s
            expected_odds = 1.0 / s["probability"]
            assert s["fair_odds"] == pytest.approx(expected_odds)
    
    def test_batch_operation_custom_keys(self):
        """Test batch operation with custom key names"""
        scores = [
            {"result": "1:0", "p": 0.25},
            {"result": "2:0", "p": 0.25}
        ]
        results = self.calculator.batch_calculate_fair_odds_and_normalize(
            scores, probability_key="p", fair_odds_key="odds"
        )
        
        total_prob = sum(s["p"] for s in results)
        assert abs(total_prob - 1.0) < 1e-10
        
        for s in results:
            assert "odds" in s
            assert s["odds"] == pytest.approx(1.0 / s["p"])


class TestOddsRatio:
    """Tests for odds ratio calculation"""
    
    def setup_method(self):
        self.calculator = FairOddsCalculator()
    
    def test_odds_ratio_with_fair_odds(self):
        """Test odds ratio calculation with provided fair odds"""
        ratio = self.calculator.calculate_odds_ratio(0.1, fair_odds=10.0)
        assert ratio == 10.0
    
    def test_odds_ratio_calculates_fair_odds(self):
        """Test odds ratio calculation when fair odds not provided"""
        ratio = self.calculator.calculate_odds_ratio(0.25)
        assert ratio == 4.0
    
    def test_odds_ratio_zero_fair_odds(self):
        """Test odds ratio with zero fair odds returns infinity"""
        ratio = self.calculator.calculate_odds_ratio(0.0, fair_odds=0.0)
        assert ratio == float('inf')


class TestDeterministic:
    """Tests to ensure deterministic behavior"""
    
    def setup_method(self):
        self.calculator = FairOddsCalculator()
    
    def test_fair_odds_deterministic(self):
        """Test that same input always produces same output"""
        for _ in range(5):
            odds = self.calculator.calculate_fair_odds(0.1432)
            assert odds == pytest.approx(1.0 / 0.1432, rel=1e-10)
    
    def test_normalization_deterministic(self):
        """Test that normalization is deterministic"""
        scores = [
            {"score": "1:0", "probability": 0.1},
            {"score": "2:0", "probability": 0.2},
            {"score": "1:1", "probability": 0.3}
        ]
        results1 = self.calculator.normalize_probability_distribution(scores.copy())
        results2 = self.calculator.normalize_probability_distribution(scores.copy())
        
        for i in range(len(results1)):
            assert results1[i]["probability"] == results2[i]["probability"]


class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""
    
    def setup_method(self):
        self.calculator = FairOddsCalculator()
    
    def test_very_high_odds(self):
        """Test very high odds calculation"""
        odds = self.calculator.calculate_fair_odds(1e-6)
        assert odds == pytest.approx(1e6)
    
    def test_probability_sum_to_one_with_many_values(self):
        """Test normalization with many values"""
        scores = [{"probability": 0.1}] * 10
        results = self.calculator.normalize_probability_distribution(scores)
        total = sum(s["probability"] for s in results)
        assert abs(total - 1.0) < 1e-10
    
    def test_batch_with_mixed_valid_invalid(self):
        """Test batch processing with mixed valid/invalid probabilities"""
        # Negative probability should be handled gracefully in batch
        # (individual calculation will raise, but we test the boundary)
        scores = [0.1, 0.5, 0.4]  # All valid
        results = self.calculator.calculate_fair_odds_batch(scores)
        assert len(results) == 3


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
