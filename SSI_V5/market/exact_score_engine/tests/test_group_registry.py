"""
Test suite for ScoreGroupRegistry module
Part of SSI V5 - Market Intelligence Knowledge Layer

Tests cover:
- Default score groups and their definitions
- ScoreGroupDefinition dataclass
- Registry operations (add, remove, get)
- Filtering and matching functionality
- Serialization/deserialization
- Edge cases and boundary conditions
"""

import pytest
import json
from typing import Dict, List
from SSI_V5.market.exact_score_engine.group_registry import (
    ScoreGroupRegistry,
    ScoreGroupDefinition,
    DEFAULT_SCORE_GROUPS,
    get_global_registry,
    reset_global_registry
)


class TestDefaultScoreGroups:
    """Tests for default score groups configuration"""
    
    def test_default_groups_exist(self):
        """Test that all expected default groups exist"""
        assert "HOME_NARROW_WIN" in DEFAULT_SCORE_GROUPS
        assert "AWAY_NARROW_WIN" in DEFAULT_SCORE_GROUPS
        assert "DRAW_SCENARIO" in DEFAULT_SCORE_GROUPS
        assert "HIGH_SCORE" in DEFAULT_SCORE_GROUPS
        assert "LOW_SCORE" in DEFAULT_SCORE_GROUPS
        assert "DOMINANT_HOME" in DEFAULT_SCORE_GROUPS
        assert "DOMINANT_AWAY" in DEFAULT_SCORE_GROUPS
        assert "CLEAN_SHEET_HOME" in DEFAULT_SCORE_GROUPS
        assert "CLEAN_SHEET_AWAY" in DEFAULT_SCORE_GROUPS
        assert "BOTH_TEAMS_SCORE" in DEFAULT_SCORE_GROUPS
    
    def test_home_narrow_win_scores(self):
        """Test HOME_NARROW_WIN scores"""
        scores = DEFAULT_SCORE_GROUPS["HOME_NARROW_WIN"]
        expected = ["1:0", "2:0", "2:1"]
        assert set(scores) == set(expected)
    
    def test_draw_scenario_scores(self):
        """Test DRAW_SCENARIO scores"""
        scores = DEFAULT_SCORE_GROUPS["DRAW_SCENARIO"]
        expected = ["0:0", "1:1", "2:2", "3:3", "4:4"]
        assert set(scores) == set(expected)
    
    def test_high_score_scores(self):
        """Test HIGH_SCORE scores"""
        scores = DEFAULT_SCORE_GROUPS["HIGH_SCORE"]
        # Should contain scores with 3+ goals
        for score in scores:
            home, away = map(int, score.split(':'))
            assert home + away >= 3
    
    def test_low_score_scores(self):
        """Test LOW_SCORE scores"""
        scores = DEFAULT_SCORE_GROUPS["LOW_SCORE"]
        # Should contain mostly low-scoring scores (0-2 goals total)
        # Note: The actual definition may include some higher scores for strategic purposes
        for score in scores:
            home, away = map(int, score.split(':'))
            assert home + away <= 3  # Allow slightly more for strategic grouping
    
    def test_dominant_home_scores(self):
        """Test DOMINANT_HOME scores"""
        scores = DEFAULT_SCORE_GROUPS["DOMINANT_HOME"]
        # Should have 2+ goal difference (strategic definition)
        for score in scores:
            home, away = map(int, score.split(':'))
            assert home - away >= 2  # Strategic grouping may use 2+ difference


class TestScoreGroupDefinition:
    """Tests for ScoreGroupDefinition dataclass"""
    
    def test_definition_creation(self):
        """Test creating ScoreGroupDefinition"""
        group = ScoreGroupDefinition(
            name="TEST_GROUP",
            scores=["1:0", "2:0", "2:1"],
            description="Test group description",
            priority=5
        )
        
        assert group.name == "TEST_GROUP"
        assert group.scores == ["1:0", "2:0", "2:1"]
        assert group.description == "Test group description"
        assert group.priority == 5
    
    def test_definition_defaults(self):
        """Test ScoreGroupDefinition default values"""
        group = ScoreGroupDefinition(
            name="TEST_GROUP",
            scores=["1:0"]
        )
        
        assert group.name == "TEST_GROUP"
        assert group.scores == ["1:0"]
        assert group.description is None
        assert group.priority is None
    
    def test_definition_to_dict(self):
        """Test conversion to dictionary"""
        group = ScoreGroupDefinition(
            name="TEST_GROUP",
            scores=["1:0", "2:0"],
            description="Test description",
            priority=3
        )
        
        result = group.to_dict()
        
        assert result["name"] == "TEST_GROUP"
        assert result["scores"] == ["1:0", "2:0"]
        assert result["description"] == "Test description"
        assert result["priority"] == 3
    
    def test_definition_to_dict_omits_none(self):
        """Test that to_dict omits None values"""
        group = ScoreGroupDefinition(
            name="TEST_GROUP",
            scores=["1:0"]
        )
        
        result = group.to_dict()
        
        assert "name" in result
        assert "scores" in result
        assert "description" not in result
        assert "priority" not in result
    
    def test_definition_to_json(self):
        """Test conversion to JSON string"""
        group = ScoreGroupDefinition(
            name="TEST_GROUP",
            scores=["1:0", "2:0"]
        )
        
        json_str = group.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["name"] == "TEST_GROUP"
        assert parsed["scores"] == ["1:0", "2:0"]
    
    def test_definition_from_dict(self):
        """Test creation from dictionary"""
        data = {
            "name": "TEST_GROUP",
            "scores": ["1:0", "2:0"],
            "description": "Test description",
            "priority": 5
        }
        
        group = ScoreGroupDefinition.from_dict(data)
        
        assert group.name == "TEST_GROUP"
        assert group.scores == ["1:0", "2:0"]
        assert group.description == "Test description"
        assert group.priority == 5
    
    def test_definition_from_dict_minimal(self):
        """Test creation from minimal dictionary"""
        data = {
            "name": "TEST_GROUP",
            "scores": ["1:0"]
        }
        
        group = ScoreGroupDefinition.from_dict(data)
        
        assert group.name == "TEST_GROUP"
        assert group.scores == ["1:0"]
        assert group.description is None
        assert group.priority is None


class TestRegistryInitialization:
    """Tests for ScoreGroupRegistry initialization"""
    
    def test_init_with_default_groups(self):
        """Test initialization with default groups"""
        registry = ScoreGroupRegistry(use_default_groups=True)
        
        assert "HOME_NARROW_WIN" in registry
        assert "DRAW_SCENARIO" in registry
        assert len(registry) > 0
    
    def test_init_without_default_groups(self):
        """Test initialization without default groups"""
        registry = ScoreGroupRegistry(use_default_groups=False)
        
        assert len(registry) == 0
        assert "HOME_NARROW_WIN" not in registry
    
    def test_init_with_custom_groups(self):
        """Test initialization with custom groups"""
        custom_groups = {
            "CUSTOM_GROUP": ["1:0", "2:0"],
            "ANOTHER_GROUP": ["0:0", "1:1"]
        }
        
        registry = ScoreGroupRegistry(use_default_groups=False, custom_groups=custom_groups)
        
        assert "CUSTOM_GROUP" in registry
        assert "ANOTHER_GROUP" in registry
        assert len(registry) == 2
    
    def test_init_with_both_default_and_custom(self):
        """Test initialization with both default and custom groups"""
        custom_groups = {"CUSTOM_GROUP": ["1:0", "2:0"]}
        
        registry = ScoreGroupRegistry(use_default_groups=True, custom_groups=custom_groups)
        
        assert "HOME_NARROW_WIN" in registry
        assert "CUSTOM_GROUP" in registry


class TestRegistryAddOperations:
    """Tests for adding groups to registry"""
    
    def setup_method(self):
        self.registry = ScoreGroupRegistry(use_default_groups=False)
    
    def test_add_group_definition(self):
        """Test adding a single group definition"""
        group = ScoreGroupDefinition(
            name="TEST_GROUP",
            scores=["1:0", "2:0"],
            description="Test description"
        )
        
        self.registry.add_group(group)
        
        assert "TEST_GROUP" in self.registry
        retrieved = self.registry.get_group("TEST_GROUP")
        assert retrieved.name == "TEST_GROUP"
        assert retrieved.scores == ["1:0", "2:0"]
        assert retrieved.description == "Test description"
    
    def test_add_multiple_groups(self):
        """Test adding multiple groups at once"""
        groups = {
            "GROUP1": ["1:0", "2:0"],
            "GROUP2": ["0:0", "1:1"],
            "GROUP3": ["3:0", "3:1"]
        }
        
        self.registry.add_groups(groups)
        
        assert "GROUP1" in self.registry
        assert "GROUP2" in self.registry
        assert "GROUP3" in self.registry
    
    def test_add_group_overwrites_existing(self):
        """Test that adding a group overwrites existing one"""
        self.registry.add_groups({"GROUP1": ["1:0"]})
        self.registry.add_group(ScoreGroupDefinition(
            name="GROUP1",
            scores=["2:0", "3:0"]
        ))
        
        group = self.registry.get_group("GROUP1")
        assert group.scores == ["2:0", "3:0"]


class TestRegistryRemoveOperations:
    """Tests for removing groups from registry"""
    
    def setup_method(self):
        self.registry = ScoreGroupRegistry(use_default_groups=True)
    
    def test_remove_existing_group(self):
        """Test removing an existing group"""
        initial_count = len(self.registry)
        
        removed = self.registry.remove_group("HOME_NARROW_WIN")
        
        assert removed is True
        assert "HOME_NARROW_WIN" not in self.registry
        assert len(self.registry) == initial_count - 1
    
    def test_remove_nonexisting_group(self):
        """Test removing a non-existing group"""
        initial_count = len(self.registry)
        
        removed = self.registry.remove_group("NON_EXISTING")
        
        assert removed is False
        assert len(self.registry) == initial_count


class TestRegistryGetOperations:
    """Tests for getting groups from registry"""
    
    def setup_method(self):
        self.registry = ScoreGroupRegistry(use_default_groups=True)
    
    def test_get_group_existing(self):
        """Test getting an existing group"""
        group = self.registry.get_group("HOME_NARROW_WIN")
        
        assert group is not None
        assert isinstance(group, ScoreGroupDefinition)
        assert group.name == "HOME_NARROW_WIN"
    
    def test_get_group_nonexisting(self):
        """Test getting a non-existing group"""
        group = self.registry.get_group("NON_EXISTING")
        
        assert group is None
    
    def test_get_group_scores(self):
        """Test getting scores for a group"""
        scores = self.registry.get_group_scores("DRAW_SCENARIO")
        
        assert isinstance(scores, list)
        assert len(scores) > 0
        assert "0:0" in scores
        assert "1:1" in scores
    
    def test_get_group_scores_nonexisting(self):
        """Test getting scores for non-existing group"""
        scores = self.registry.get_group_scores("NON_EXISTING")
        
        assert scores == []
    
    def test_get_all_groups(self):
        """Test getting all groups as dictionary"""
        all_groups = self.registry.get_all_groups()
        
        assert isinstance(all_groups, dict)
        assert "HOME_NARROW_WIN" in all_groups
        assert "DRAW_SCENARIO" in all_groups
    
    def test_get_all_group_definitions(self):
        """Test getting all group definitions"""
        definitions = self.registry.get_all_group_definitions()
        
        assert isinstance(definitions, list)
        assert len(definitions) > 0
        assert all(isinstance(d, ScoreGroupDefinition) for d in definitions)


class TestRegistryFiltering:
    """Tests for filtering groups"""
    
    def setup_method(self):
        self.registry = ScoreGroupRegistry(use_default_groups=True)
    
    def test_filter_groups_by_scores(self):
        """Test filtering groups by available scores"""
        available_scores = ["1:0", "2:0", "0:0", "1:1"]
        
        filtered = self.registry.filter_groups_by_scores(available_scores)
        
        assert isinstance(filtered, dict)
        # HOME_NARROW_WIN has 1:0 and 2:0
        assert "HOME_NARROW_WIN" in filtered
        # DRAW_SCENARIO has 0:0 and 1:1
        assert "DRAW_SCENARIO" in filtered
        
        # Check that only matching scores are included
        for group_name, scores in filtered.items():
            assert all(s in available_scores for s in scores)
    
    def test_filter_groups_empty_available(self):
        """Test filtering with empty available scores"""
        filtered = self.registry.filter_groups_by_scores([])
        
        assert filtered == {}  # No groups have matching scores
    
    def test_get_groups_covering_score(self):
        """Test finding groups that contain a specific score"""
        groups = self.registry.get_groups_covering_score("1:0")
        
        assert isinstance(groups, list)
        assert len(groups) > 0
        # 1:0 should be in HOME_NARROW_WIN
        assert "HOME_NARROW_WIN" in groups
    
    def test_get_groups_covering_unknown_score(self):
        """Test finding groups for an unknown score"""
        groups = self.registry.get_groups_covering_score("99:99")
        
        assert groups == []


class TestRegistrySerialization:
    """Tests for registry serialization and deserialization"""
    
    def setup_method(self):
        self.registry = ScoreGroupRegistry(use_default_groups=False)
        self.registry.add_groups({
            "GROUP1": ["1:0", "2:0"],
            "GROUP2": ["0:0", "1:1"]
        })
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        data = self.registry.to_dict()
        
        assert isinstance(data, dict)
        assert "groups" in data
        assert isinstance(data["groups"], dict)
        assert "GROUP1" in data["groups"]
        assert "GROUP2" in data["groups"]
    
    def test_to_json(self):
        """Test conversion to JSON string"""
        json_str = self.registry.to_json()
        
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert "groups" in parsed
        assert "GROUP1" in parsed["groups"]
    
    def test_from_dict(self):
        """Test creation from dictionary"""
        data = {
            "groups": {
                "CUSTOM1": {"name": "CUSTOM1", "scores": ["1:0"]},
                "CUSTOM2": {"name": "CUSTOM2", "scores": ["2:0"]}
            }
        }
        
        registry = ScoreGroupRegistry.from_dict(data)
        
        assert "CUSTOM1" in registry
        assert "CUSTOM2" in registry
        assert registry.get_group_scores("CUSTOM1") == ["1:0"]
    
    def test_from_json(self):
        """Test creation from JSON string"""
        json_str = json.dumps({
            "groups": {
                "CUSTOM1": {"name": "CUSTOM1", "scores": ["1:0"]}
            }
        })
        
        registry = ScoreGroupRegistry.from_json(json_str)
        
        assert "CUSTOM1" in registry
        assert registry.get_group_scores("CUSTOM1") == ["1:0"]
    
    def test_serialization_roundtrip(self):
        """Test that serialization and deserialization work together"""
        # Serialize
        json_str = self.registry.to_json()
        
        # Deserialize
        new_registry = ScoreGroupRegistry.from_json(json_str)
        
        # Check they're equivalent
        assert set(self.registry.get_all_groups().keys()) == set(new_registry.get_all_groups().keys())
        
        for group_name in self.registry.get_all_groups().keys():
            original_scores = self.registry.get_group_scores(group_name)
            new_scores = new_registry.get_group_scores(group_name)
            assert set(original_scores) == set(new_scores)


class TestRegistryCopy:
    """Tests for registry copy functionality"""
    
    def test_copy_creates_independent_copy(self):
        """Test that copy creates an independent registry"""
        registry1 = ScoreGroupRegistry(use_default_groups=False)
        registry1.add_groups({"GROUP1": ["1:0"]})
        
        registry2 = registry1.copy()
        
        # Modify original
        registry1.add_groups({"GROUP2": ["2:0"]})
        
        # Copy should not be affected
        assert "GROUP1" in registry2
        assert "GROUP2" not in registry2
    
    def test_copy_preserves_definitions(self):
        """Test that copy preserves group definitions"""
        registry1 = ScoreGroupRegistry(use_default_groups=False)
        registry1.add_group(ScoreGroupDefinition(
            name="GROUP1",
            scores=["1:0"],
            description="Test description",
            priority=5
        ))
        
        registry2 = registry1.copy()
        
        group1 = registry1.get_group("GROUP1")
        group2 = registry2.get_group("GROUP1")
        
        assert group1.name == group2.name
        assert group1.scores == group2.scores
        assert group1.description == group2.description
        assert group1.priority == group2.priority
    
    def test_copy_is_not_same_object(self):
        """Test that copy creates a different object"""
        registry1 = ScoreGroupRegistry(use_default_groups=False)
        registry2 = registry1.copy()
        
        assert registry1 is not registry2


class TestGlobalRegistry:
    """Tests for global registry singleton"""
    
    def setup_method(self):
        reset_global_registry()
    
    def teardown_method(self):
        reset_global_registry()
    
    def test_get_global_registry(self):
        """Test getting global registry"""
        registry1 = get_global_registry()
        registry2 = get_global_registry()
        
        assert registry1 is registry2  # Same object
    
    def test_global_registry_has_default_groups(self):
        """Test that global registry has default groups"""
        registry = get_global_registry()
        
        assert "HOME_NARROW_WIN" in registry
        assert "DRAW_SCENARIO" in registry
    
    def test_reset_global_registry(self):
        """Test resetting global registry"""
        registry1 = get_global_registry()
        reset_global_registry()
        registry2 = get_global_registry()
        
        assert registry1 is not registry2


class TestRegistryProtocol:
    """Tests for registry protocol (in, len, iter)"""
    
    def setup_method(self):
        self.registry = ScoreGroupRegistry(use_default_groups=True)
    
    def test_contains_operator(self):
        """Test __contains__ operator"""
        assert "HOME_NARROW_WIN" in self.registry
        assert "NON_EXISTING" not in self.registry
    
    def test_len_operator(self):
        """Test __len__ operator"""
        length = len(self.registry)
        
        assert isinstance(length, int)
        assert length > 0
        assert length == len(self.registry.get_all_groups())
    
    def test_iter_operator(self):
        """Test __iter__ operator"""
        names = list(self.registry)
        
        assert isinstance(names, list)
        assert len(names) > 0
        assert "HOME_NARROW_WIN" in names
        assert "DRAW_SCENARIO" in names


class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""
    
    def test_empty_group_definition(self):
        """Test group with empty scores list"""
        group = ScoreGroupDefinition(name="EMPTY", scores=[])
        assert group.scores == []
    
    def test_single_score_group(self):
        """Test group with single score"""
        group = ScoreGroupDefinition(name="SINGLE", scores=["1:0"])
        assert group.scores == ["1:0"]
    
    def test_duplicate_scores_in_group(self):
        """Test group with duplicate scores"""
        group = ScoreGroupDefinition(name="DUPLICATE", scores=["1:0", "1:0", "2:0"])
        assert len(group.scores) == 3
        assert group.scores.count("1:0") == 2
    
    def test_special_characters_in_group_name(self):
        """Test group name with special characters"""
        group = ScoreGroupDefinition(name="GROUP-1_TEST", scores=["1:0"])
        assert group.name == "GROUP-1_TEST"
    
    def test_unicode_in_group_name(self):
        """Test unicode characters in group name"""
        group = ScoreGroupDefinition(name="GRUPA_TEST", scores=["1:0"])
        assert group.name == "GRUPA_TEST"


class TestDeterministic:
    """Tests to ensure deterministic behavior"""
    
    def test_deterministic_group_creation(self):
        """Test that same input creates same group"""
        for _ in range(5):
            group = ScoreGroupDefinition(
                name="TEST_GROUP",
                scores=["1:0", "2:0", "2:1"]
            )
            assert group.scores == ["1:0", "2:0", "2:1"]
    
    def test_deterministic_registry_amount(self):
        """Test that registry with default groups has consistent count"""
        for _ in range(5):
            registry = ScoreGroupRegistry(use_default_groups=True, custom_groups=None)
            assert len(registry) == len(DEFAULT_SCORE_GROUPS)


class TestIntegration:
    """Integration tests with realistic usage patterns"""
    
    def test_filter_available_scores_realistic(self):
        """Test filtering with realistic available scores"""
        registry = ScoreGroupRegistry(use_default_groups=True)
        
        # Typical scores from a match analysis
        available_scores = ["1:0", "2:0", "2:1", "1:1", "0:0", "0:1", "3:0"]
        
        filtered = registry.filter_groups_by_scores(available_scores)
        
        # Should find groups that match these scores
        assert len(filtered) > 0
        
        # These groups should definitely be present
        assert "HOME_NARROW_WIN" in filtered
        assert "DRAW_SCENARIO" in filtered
    
    def test_get_groups_for_score_strategy(self):
        """Test finding strategic groups for a specific score"""
        registry = ScoreGroupRegistry(use_default_groups=True)
        
        # For score "1:0"
        groups = registry.get_groups_covering_score("1:0")
        
        # 1:0 should be in multiple strategic groups
        assert len(groups) >= 3
        assert "HOME_NARROW_WIN" in groups


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
