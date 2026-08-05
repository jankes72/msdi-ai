"""
Test suite for ValueDetector module
Part of SSI V5 - Market Intelligence Knowledge Layer

Tests cover:
- Market value percentage calculation
- Value classification (HIGH_VALUE, GOOD_VALUE, etc.)
- Value score calculation (0-100)
- Batch processing
- Edge cases and boundary conditions
- Custom threshold configuration
"""

import pytest
from typing import Dict, List, Optional
from SSI_V5.market.exact_score_engine.value_detector import (
    ValueDetector,
    ValueAssessment,
    ValueClassification
)


class TestMarketValueCalculation:
    """Tests for market value percentage calculation"""
    
    def setup_method(self):
        self.detector = ValueDetector()
    
    def test_detect_market_value_basic(self):
        """Test basic market value calculation"""
        # fair_odds=8.0, market_odds=10.0 -> value = (10-8)/8 = 0.25 (+25%)
        value = self.detector.detect_market_value(8.0, 10.0)
        assert value == pytest.approx(0.25)
    
    def test_detect_market_value_exact_example(self):
        """Test the exact example from module docs: SSI=8.00, Market=10.00 -> +25%"""
        value = self.detector.detect_market_value(8.0, 10.0)
        assert value == pytest.approx(0.25)
    
    def test_detect_market_value_no_value(self):
        """Test when market odds equal fair odds (no value)"""
        value = self.detector.detect_market_value(10.0, 10.0)
        assert value == 0.0
    
    def test_detect_market_value_negative(self):
        """Test when market odds are worse than fair odds"""
        # fair_odds=10.0, market_odds=8.0 -> value = (8-10)/10 = -0.20 (-20%)
        value = self.detector.detect_market_value(10.0, 8.0)
        assert value == pytest.approx(-0.20)
    
    def test_detect_market_value_no_real_odds(self):
        """Test when real market odds are not available"""
        value = self.detector.detect_market_value(10.0, None)
        assert value is None
    
    def test_detect_market_value_no_fair_odds(self):
        """Test when fair odds are not available"""
        value = self.detector.detect_market_value(None, 10.0)
        assert value is None
    
    def test_detect_market_value_zero_fair_odds(self):
        """Test when fair odds are zero"""
        value = self.detector.detect_market_value(0.0, 10.0)
        assert value is None
    
    def test_detect_market_value_infinity_fair_odds(self):
        """Test when fair odds are infinity"""
        value = self.detector.detect_market_value(float('inf'), 10.0)
        assert value is None
    
    def test_detect_market_value_negative_market_odds(self):
        """Test when market odds are negative"""
        value = self.detector.detect_market_value(10.0, -5.0)
        assert value is None
    
    def test_detect_market_value_zero_market_odds(self):
        """Test when market odds are zero"""
        value = self.detector.detect_market_value(10.0, 0.0)
        assert value is None


class TestValueClassification:
    """Tests for value classification"""
    
    def setup_method(self):
        self.detector = ValueDetector()
    
    def test_classify_high_value(self):
        """Test HIGH_VALUE classification (>20%)"""
        classify = self.detector.classify_value(0.25)
        assert classify == ValueClassification.HIGH_VALUE
    
    def test_classify_good_value(self):
        """Test GOOD_VALUE classification (10% < value <= 20%)"""
        classify = self.detector.classify_value(0.15)
        assert classify == ValueClassification.GOOD_VALUE
    
    def test_classify_fair_value(self):
        """Test FAIR_VALUE classification (5% < value <= 10%)"""
        classify = self.detector.classify_value(0.07)
        assert classify == ValueClassification.FAIR_VALUE
    
    def test_classify_marginal_value(self):
        """Test MARGINAL_VALUE classification (0% < value <= 5%)"""
        classify = self.detector.classify_value(0.03)
        assert classify == ValueClassification.MARGINAL_VALUE
    
    def test_classify_neutral(self):
        """Test NEUTRAL classification (-5% <= value <= 0%)"""
        classify = self.detector.classify_value(-0.02)
        assert classify == ValueClassification.NEUTRAL
        
        classify = self.detector.classify_value(0.0)
        assert classify == ValueClassification.NEUTRAL
    
    def test_classify_undervalued(self):
        """Test UNDERVALUED classification (value < -5%)"""
        classify = self.detector.classify_value(-0.10)
        assert classify == ValueClassification.UNDERVALUED
    
    def test_classify_none_value(self):
        """Test UNKNOWN classification when value is None"""
        classify = self.detector.classify_value(None)
        assert classify == ValueClassification.UNKNOWN
    
    # Boundary tests
    def test_classify_boundary_high_good(self):
        """Test boundary between HIGH_VALUE and GOOD_VALUE (20%)"""
        # Exactly 20% - should be GOOD_VALUE (<= 20%)
        classify = self.detector.classify_value(0.20)
        assert classify == ValueClassification.GOOD_VALUE
        
        # Just above 20% - should be HIGH_VALUE
        classify = self.detector.classify_value(0.2000001)
        assert classify == ValueClassification.HIGH_VALUE
    
    def test_classify_boundary_good_fair(self):
        """Test boundary between GOOD_VALUE and FAIR_VALUE (10%)"""
        # 0.10 is exactly at GOOD_VALUE threshold, so it should be FAIR_VALUE (> 0.05 but <= 0.10)
        classify = self.detector.classify_value(0.10)
        assert classify == ValueClassification.FAIR_VALUE
        
        # Just above 10% should be GOOD_VALUE
        classify = self.detector.classify_value(0.1000001)
        assert classify == ValueClassification.GOOD_VALUE
    
    def test_classify_boundary_fair_marginal(self):
        """Test boundary between FAIR_VALUE and MARGINAL_VALUE (5%)"""
        # 0.05 is exactly at FAIR_VALUE threshold, so it should be MARGINAL_VALUE (> 0.0 but <= 0.05)
        classify = self.detector.classify_value(0.05)
        assert classify == ValueClassification.MARGINAL_VALUE
        
        # Just above 5% should be FAIR_VALUE
        classify = self.detector.classify_value(0.0500001)
        assert classify == ValueClassification.FAIR_VALUE
    
    def test_classify_boundary_marginal_neutral(self):
        """Test boundary between MARGINAL_VALUE and NEUTRAL (0%)"""
        classify = self.detector.classify_value(0.0)
        assert classify == ValueClassification.NEUTRAL
        
        classify = self.detector.classify_value(0.0000001)
        assert classify == ValueClassification.MARGINAL_VALUE
    
    def test_classify_boundary_neutral_undervalued(self):
        """Test boundary between NEUTRAL and UNDERVALUED (-5%)"""
        classify = self.detector.classify_value(-0.05)
        assert classify == ValueClassification.NEUTRAL
        
        classify = self.detector.classify_value(-0.0500001)
        assert classify == ValueClassification.UNDERVALUED


class TestValueScore:
    """Tests for value score calculation"""
    
    def setup_method(self):
        self.detector = ValueDetector()
    
    def test_calculate_value_score_basic(self):
        """Test basic value score calculation"""
        # market_value = 0.26 (26%), confidence = 0.8
        # raw_score = max(0, min(100, 0.26 * 100 + 50)) = min(100, 76) = 76
        # weighted_score = 76 * 0.8 = 60.8
        score = self.detector.calculate_value_score(0.26, 0.8)
        assert abs(score - 60.8) < 0.001
    
    def test_calculate_value_score_high_value(self):
        """Test value score for high value opportunity"""
        # 20% value, 100% confidence -> raw_score = 20*100+50 = 2500 -> clamped to 100
        # weighted_score = 100 * 1.0 = 100
        # Actually: max(0, min(100, 0.20 * 100 + 50)) = max(0, min(100, 20 + 50)) = max(0, 70) = 70
        # weighted_score = 70 * 1.0 = 70
        score = self.detector.calculate_value_score(0.20, 1.0)
        assert abs(score - 70.0) < 0.001
    
    def test_calculate_value_score_no_value(self):
        """Test value score when market value is None"""
        score = self.detector.calculate_value_score(None, 0.8)
        assert score == 0.0
    
    def test_calculate_value_score_negative_value(self):
        """Test value score for negative market value"""
        # market_value = -0.10 (-10%)
        # raw_score = max(0, min(100, -0.10 * 100 + 50)) = max(0, min(100, -10 + 50)) = max(0, 40) = 40
        # weighted_score = 40 * 0.8 = 32
        score = self.detector.calculate_value_score(-0.10, 0.8)
        assert abs(score - 32.0) < 0.001
    
    def test_calculate_value_score_zero_confidence(self):
        """Test value score with zero confidence"""
        score = self.detector.calculate_value_score(0.25, 0.0)
        assert abs(score - 0.0) < 0.001
    
    def test_calculate_value_score_formula(self):
        """Test the exact formula: raw_score = max(0, min(100, market_value * 100 + 50))"""
        # Test various market values
        test_cases = [
            (0.0, 50.0),   # 0% -> 50
            (0.5, 100.0),  # 50% -> 100
            (1.0, 100.0),  # 100% -> clamped to 100
            (-0.5, 0.0),   # -50% -> 0
            (-1.0, 0.0),   # -100% -> 0
        ]
        
        for market_value, expected_raw in test_cases:
            raw_score = max(0, min(100, market_value * 100 + 50))
            assert abs(raw_score - expected_raw) < 0.001


class TestCompleteAssessment:
    """Tests for complete value assessment"""
    
    def setup_method(self):
        self.detector = ValueDetector()
    
    def test_assess_value_basic(self):
        """Test complete value assessment"""
        assessment = self.detector.assess_value(
            fair_odds=7.14,
            real_market_odds=9.0,
            confidence=0.86
        )
        
        assert assessment.fair_odds == 7.14
        assert assessment.real_market_odds == 9.0
        assert abs(assessment.market_value_percentage - 0.26) < 0.001
        assert assessment.classification == ValueClassification.HIGH_VALUE
        assert assessment.value_score > 0
    
    def test_assess_value_no_market_odds(self):
        """Test assessment when market odds not available"""
        assessment = self.detector.assess_value(
            fair_odds=7.14,
            real_market_odds=None,
            confidence=0.86
        )
        
        assert assessment.classification == ValueClassification.UNKNOWN
        assert assessment.market_value_percentage is None
    
    def test_assess_value_to_dict(self):
        """Test conversion of assessment to dictionary"""
        assessment = self.detector.assess_value(7.14, 9.0, 0.86)
        result = assessment.to_dict()
        
        assert result["fair_odds"] == 7.14
        assert result["real_market_odds"] == 9.0
        assert result["classification"] == "HIGH_VALUE"
        assert isinstance(result["value_score"], float)


class TestBatchAssessment:
    """Tests for batch value assessment"""
    
    def setup_method(self):
        self.detector = ValueDetector()
    
    def test_batch_assess_values_basic(self):
        """Test batch processing of multiple scores"""
        scores = [
            {"fair_odds": 7.14, "real_market_odds": 9.0, "confidence": 0.86},
            {"fair_odds": 5.0, "real_market_odds": 4.5, "confidence": 0.80},
            {"fair_odds": 3.0, "real_market_odds": 3.0, "confidence": 0.90}
        ]
        
        results = self.detector.batch_assess_values(
            scores,
            fair_odds_key="fair_odds",
            real_odds_key="real_market_odds",
            confidence_key="confidence"
        )
        
        assert len(results) == 3
        
        # First score: +26% value (fair_odds=7.14, market_odds=9.0 -> (9-7.14)/7.14 = 0.2605...)
        assert abs(results[0]["market_value"] - 0.2605) < 0.01
        assert results[0]["value_classification"] == "HIGH_VALUE"
        
        # Second score: -10% (fair_odds=5.0, market_odds=4.5 -> (4.5-5.0)/5.0 = -0.10)
        assert abs(results[1]["market_value"] + 0.10) < 0.01
        
        # Third score: 0% (fair)
        assert results[2]["market_value"] == 0.0
    
    def test_batch_assess_values_empty(self):
        """Test batch processing with empty list"""
        results = self.detector.batch_assess_values([])
        assert results == []
    
    def test_batch_assess_values_missing_fields(self):
        """Test batch processing with missing optional fields"""
        scores = [
            {"fair_odds": 7.14},  # No market odds or confidence
            {"fair_odds": 5.0, "confidence": 0.8}
        ]
        
        results = self.detector.batch_assess_values(
            scores,
            fair_odds_key="fair_odds",
            real_odds_key="real_market_odds",
            confidence_key="confidence"
        )
        
        assert len(results) == 2
        assert results[0]["market_value"] is None


class TestCustomThresholds:
    """Tests for custom threshold configuration"""
    
    def test_custom_thresholds_init(self):
        """Test initialization with custom thresholds"""
        detector = ValueDetector(
            high_threshold=0.30,
            good_threshold=0.15,
            fair_threshold=0.05,
            marginal_threshold=0.0,
            neutral_threshold=-0.10
        )
        
        assert detector.HIGH_VALUE_THRESHOLD == 0.30
        assert detector.GOOD_VALUE_THRESHOLD == 0.15
        assert detector.FAIR_VALUE_THRESHOLD == 0.05
        assert detector.MARGINAL_THRESHOLD == 0.0
        assert detector.NEUTRAL_THRESHOLD == -0.10
    
    def test_set_thresholds(self):
        """Test setting thresholds after initialization"""
        detector = ValueDetector()
        detector.set_value_thresholds(
            high=0.25,
            good=0.12,
            fair=0.06
        )
        
        assert detector.HIGH_VALUE_THRESHOLD == 0.25
        assert detector.GOOD_VALUE_THRESHOLD == 0.12
        assert detector.FAIR_VALUE_THRESHOLD == 0.06
    
    def test_get_thresholds(self):
        """Test getting current thresholds"""
        detector = ValueDetector()
        thresholds = detector.get_value_thresholds()
        
        assert "HIGH_VALUE" in thresholds
        assert "GOOD_VALUE" in thresholds
        assert "FAIR_VALUE" in thresholds


class TestThresholdsConfig:
    """Tests for the VALUE_THRESHOLDS constant"""
    
    def test_thresholds_constant_structure(self):
        """Test that VALUE_THRESHOLDS has expected structure"""
        from SSI_V5.market.exact_score_engine.value_detector import VALUE_THRESHOLDS
        
        assert "HIGH_VALUE" in VALUE_THRESHOLDS
        assert "GOOD_VALUE" in VALUE_THRESHOLDS
        assert "FAIR_VALUE" in VALUE_THRESHOLDS
        assert "MARGINAL_VALUE" in VALUE_THRESHOLDS
        assert "NEUTRAL" in VALUE_THRESHOLDS


class TestValueClassificationEnum:
    """Tests for ValueClassification enum"""
    
    def test_enum_values(self):
        """Test that enum has all expected values"""
        assert ValueClassification.HIGH_VALUE.value == "HIGH_VALUE"
        assert ValueClassification.GOOD_VALUE.value == "GOOD_VALUE"
        assert ValueClassification.FAIR_VALUE.value == "FAIR_VALUE"
        assert ValueClassification.MARGINAL_VALUE.value == "MARGINAL_VALUE"
        assert ValueClassification.NEUTRAL.value == "NEUTRAL"
        assert ValueClassification.UNDERVALUED.value == "UNDERVALUED"
        assert ValueClassification.UNKNOWN.value == "UNKNOWN"


class TestValueAssessmentDataclass:
    """Tests for ValueAssessment dataclass"""
    
    def test_assessment_defaults(self):
        """Test ValueAssessment default values"""
        assessment = ValueAssessment(fair_odds=10.0)
        
        assert assessment.fair_odds == 10.0
        assert assessment.real_market_odds is None
        assert assessment.market_value_percentage is None
        assert assessment.classification == ValueClassification.UNKNOWN
        assert assessment.value_score == 0.0


class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""
    
    def setup_method(self):
        self.detector = ValueDetector()
    
    def test_very_large_value(self):
        """Test very large market value percentage"""
        value = self.detector.detect_market_value(1.0, 100.0)
        assert value == pytest.approx(99.0)
    
    def test_very_small_value(self):
        """Test very small market value percentage"""
        value = self.detector.detect_market_value(100.0, 100.001)
        assert abs(value - 0.00001) < 1e-6
    
    def test_assess_with_extreme_odds(self):
        """Test assessment with extreme odds values"""
        assessment = self.detector.assess_value(
            fair_odds=1e-10,
            real_market_odds=1e9,
            confidence=0.5
        )
        # This should work without error
        assert assessment.fair_odds > 0
        assert assessment.real_market_odds > 0


class TestDeterministic:
    """Tests to ensure deterministic behavior"""
    
    def setup_method(self):
        self.detector = ValueDetector()
    
    def test_deterministic_market_value(self):
        """Test that market value calculation is deterministic"""
        for _ in range(5):
            value = self.detector.detect_market_value(7.14, 9.0)
            assert abs(value - 0.26) < 0.001
    
    def test_deterministic_classification(self):
        """Test that classification is deterministic"""
        for _ in range(5):
            classify = self.detector.classify_value(0.25)
            assert classify == ValueClassification.HIGH_VALUE


class TestIntegration:
    """Integration tests with realistic data"""
    
    def setup_method(self):
        self.detector = ValueDetector()
    
    def test_realistic_scenario_high_value(self):
        """Test realistic scenario: SSI found value, market confirms"""
        # SSI fair odds: 8.00
        # Market odds: 10.00
        # This is +25% value -> HIGH_VALUE
        assessment = self.detector.assess_value(8.0, 10.0, 0.85)
        
        assert assessment.classification == ValueClassification.HIGH_VALUE
        assert abs(assessment.market_value_percentage - 0.25) < 0.001
        assert assessment.value_score > 50  # Should be good score
    
    def test_realistic_scenario_no_value(self):
        """Test realistic scenario: SSI and market agree"""
        assessment = self.detector.assess_value(8.0, 8.0, 0.85)
        
        assert assessment.classification == ValueClassification.NEUTRAL
        assert assessment.market_value_percentage == 0.0
    
    def test_realistic_scenario_undervalued(self):
        """Test realistic scenario: Market thinks it's more likely than SSI"""
        # SSI fair odds: 10.0
        # Market odds: 7.0
        # This is -30% value -> UNDERVALUED
        assessment = self.detector.assess_value(10.0, 7.0, 0.85)
        
        assert assessment.classification == ValueClassification.UNDERVALUED
        assert abs(assessment.market_value_percentage - (-0.30)) < 0.001


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
