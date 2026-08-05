"""
Score Group Registry for Exact Score Market Builder
Part of SSI V5 - Market Intelligence Knowledge Layer

This module provides a registry of predefined score groups and the ability
to define custom groups. Groups allow categorizing scores into meaningful
strategic categories for agents to use.

Default Groups:
--------------
- HOME_NARROW_WIN: Close home victories (1:0, 2:0, 2:1)
- HOME_WIN_LOW_SCORE: Low-scoring home victories
- AWAY_NARROW_WIN: Close away victories
- DRAW_SCENARIO: All draw outcomes
- BOTH_TEAMS_CLOSE: Outcomes where teams score similar amounts
- HIGH_SCORE: High-scoring matches (3+ goals)
- LOW_SCORE: Low-scoring matches (0-2 goals total)
- DOMINANT_HOME: Dominant home victories (3+ goal difference)
- DOMINANT_AWAY: Dominant away victories (3+ goal difference)

Custom groups can be added by Strategy Laboratory or other modules.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
import json


# Default score groups definition
DEFAULT_SCORE_GROUPS: Dict[str, List[str]] = {
    "HOME_NARROW_WIN": ["1:0", "2:0", "2:1"],
    "HOME_WIN_LOW_SCORE": ["1:0", "2:0", "3:0", "2:1", "3:1"],
    "AWAY_NARROW_WIN": ["0:1", "0:2", "1:2"],
    "AWAY_WIN_LOW_SCORE": ["0:1", "0:2", "1:2", "0:3", "1:3"],
    "DRAW_SCENARIO": ["0:0", "1:1", "2:2", "3:3", "4:4"],
    "BOTH_TEAMS_CLOSE": ["1:0", "0:1", "1:1", "2:1", "1:2"],
    "HIGH_SCORE": [
        "3:0", "0:3", "3:1", "1:3", "3:2", "2:3",
        "4:0", "0:4", "4:1", "1:4", "4:2", "2:4",
        "5:0", "0:5", "5:1", "1:5", "5:2", "2:5",
        "3:3", "4:4", "5:5"
    ],
    "LOW_SCORE": ["0:0", "1:0", "0:1", "1:1", "2:0", "0:2", "2:1", "1:2"],
    "DOMINANT_HOME": ["3:0", "4:0", "5:0", "6:0", "3:1", "4:1", "5:1", "6:1", "4:2", "5:2"],
    "DOMINANT_AWAY": ["0:3", "0:4", "0:5", "0:6", "1:3", "1:4", "1:5", "2:4", "2:5"],
    "CLEAN_SHEET_HOME": ["1:0", "2:0", "3:0", "4:0", "5:0", "6:0"],
    "CLEAN_SHEET_AWAY": ["0:1", "0:2", "0:3", "0:4", "0:5", "0:6"],
    "BOTH_TEAMS_SCORE": [
        "1:1", "2:1", "1:2", "2:2", "3:1", "1:3", "3:2", "2:3",
        "3:3", "4:1", "1:4", "4:2", "2:4", "4:3", "3:4"
    ],
    "ONE_GOAL_MARGIN": ["1:0", "0:1", "2:1", "1:2", "3:2", "2:3", "4:3", "3:4"],
    "TWO_GOAL_MARGIN": ["2:0", "0:2", "3:1", "1:3", "4:2", "2:4", "5:3", "3:5"],
    "THREE_PLUS_GOAL_MARGIN": ["3:0", "0:3", "4:0", "0:4", "5:0", "0:5", "4:1", "1:4", "5:1", "1:5"],
}


@dataclass
class ScoreGroupDefinition:
    """
    Definition of a custom score group.
    
    Attributes:
        name: Unique name for the group
        scores: List of score strings in the group
        description: Optional description of the group
        priority: Optional priority (higher = more important)
    """
    name: str
    scores: List[str]
    description: Optional[str] = None
    priority: Optional[int] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = {
            "name": self.name,
            "scores": self.scores
        }
        if self.description:
            result["description"] = self.description
        if self.priority is not None:
            result["priority"] = self.priority
        return result

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict) -> "ScoreGroupDefinition":
        """Create from dictionary"""
        return cls(
            name=data["name"],
            scores=data["scores"],
            description=data.get("description"),
            priority=data.get("priority")
        )


class ScoreGroupRegistry:
    """
    Registry for managing score groups.
    
    Provides:
    - Access to default score groups
    - Ability to add custom groups
    - Methods to filter groups based on available scores
    - Serialization/deserialization for custom groups
    
    Example:
        >>> registry = ScoreGroupRegistry()
        >>> groups = registry.get_all_groups()
        >>> print(f"Available groups: {list(groups.keys())}")
        Available groups: ['HOME_NARROW_WIN', 'DRAW_SCENARIO', ...]
        
        >>> custom_groups = {"MY_CUSTOM_GROUP": ["1:0", "2:0"]}
        >>> registry.add_groups(custom_groups)
    """
    
    def __init__(
        self,
        use_default_groups: bool = True,
        custom_groups: Optional[Dict[str, List[str]]] = None
    ):
        """
        Initialize the registry.
        
        Args:
            use_default_groups: Whether to include default groups
            custom_groups: Optional dictionary of custom groups to add
        """
        self._groups: Dict[str, ScoreGroupDefinition] = {}
        
        if use_default_groups:
            self._load_default_groups()
        
        if custom_groups:
            self.add_groups(custom_groups)
    
    def _load_default_groups(self) -> None:
        """Load default score groups into the registry"""
        for name, scores in DEFAULT_SCORE_GROUPS.items():
            self._groups[name] = ScoreGroupDefinition(
                name=name,
                scores=scores,
                description=self._get_group_description(name),
                priority=self._get_group_priority(name)
            )
    
    def _get_group_description(self, group_name: str) -> str:
        """Get description for a default group"""
        descriptions = {
            "HOME_NARROW_WIN": "Close home victories (1 goal margin)",
            "HOME_WIN_LOW_SCORE": "Low-scoring home victories",
            "AWAY_NARROW_WIN": "Close away victories (1 goal margin)",
            "AWAY_WIN_LOW_SCORE": "Low-scoring away victories",
            "DRAW_SCENARIO": "All possible draw outcomes",
            "BOTH_TEAMS_CLOSE": "Outcomes where teams score similar amounts",
            "HIGH_SCORE": "High-scoring matches (3+ goals)",
            "LOW_SCORE": "Low-scoring matches (0-2 goals total)",
            "DOMINANT_HOME": "Dominant home victories (3+ goal difference)",
            "DOMINANT_AWAY": "Dominant away victories (3+ goal difference)",
            "CLEAN_SHEET_HOME": "Home team keeps clean sheet",
            "CLEAN_SHEET_AWAY": "Away team keeps clean sheet",
            "BOTH_TEAMS_SCORE": "Both teams score at least one goal",
            "ONE_GOAL_MARGIN": "Matches decided by one goal",
            "TWO_GOAL_MARGIN": "Matches decided by two goals",
            "THREE_PLUS_GOAL_MARGIN": "Matches decided by three or more goals",
        }
        return descriptions.get(group_name, "")
    
    def _get_group_priority(self, group_name: str) -> int:
        """Get priority for a default group (lower = higher priority)"""
        priorities = {
            "DRAW_SCENARIO": 1,
            "HOME_NARROW_WIN": 2,
            "AWAY_NARROW_WIN": 2,
            "LOW_SCORE": 3,
            "HIGH_SCORE": 4,
            "BOTH_TEAMS_SCORE": 5,
            "HOME_WIN_LOW_SCORE": 6,
            "AWAY_WIN_LOW_SCORE": 6,
            "DOMINANT_HOME": 7,
            "DOMINANT_AWAY": 7,
            "CLEAN_SHEET_HOME": 8,
            "CLEAN_SHEET_AWAY": 8,
        }
        return priorities.get(group_name, 100)
    
    def add_group(
        self,
        group_definition: ScoreGroupDefinition
    ) -> None:
        """
        Add a single custom group to the registry.
        
        Args:
            group_definition: ScoreGroupDefinition to add
        """
        self._groups[group_definition.name] = group_definition
    
    def add_groups(
        self,
        groups: Dict[str, List[str]]
    ) -> None:
        """
        Add multiple custom groups to the registry.
        
        Args:
            groups: Dictionary of {group_name: [score_list]}
        """
        for name, scores in groups.items():
            self._groups[name] = ScoreGroupDefinition(
                name=name,
                scores=scores
            )
    
    def remove_group(self, group_name: str) -> bool:
        """
        Remove a group from the registry.
        
        Args:
            group_name: Name of the group to remove
        
        Returns:
            True if group was removed, False if it didn't exist
        """
        if group_name in self._groups:
            del self._groups[group_name]
            return True
        return False
    
    def get_group(self, group_name: str) -> Optional[ScoreGroupDefinition]:
        """
        Get a specific group definition.
        
        Args:
            group_name: Name of the group
        
        Returns:
            ScoreGroupDefinition or None if not found
        """
        return self._groups.get(group_name)
    
    def get_group_scores(self, group_name: str) -> List[str]:
        """
        Get the list of scores for a specific group.
        
        Args:
            group_name: Name of the group
        
        Returns:
            List of score strings, or empty list if group not found
        """
        group = self.get_group(group_name)
        return group.scores if group else []
    
    def get_all_groups(self) -> Dict[str, List[str]]:
        """
        Get all registered groups as a dictionary.
        
        Returns:
            Dictionary of {group_name: [score_list]}
        """
        return {name: group.scores for name, group in self._groups.items()}
    
    def get_all_group_definitions(self) -> List[ScoreGroupDefinition]:
        """
        Get all group definitions.
        
        Returns:
            List of ScoreGroupDefinition objects
        """
        return list(self._groups.values())
    
    def filter_groups_by_scores(
        self,
        available_scores: List[str]
    ) -> Dict[str, List[str]]:
        """
        Filter groups to only include those with at least one available score.
        
        Args:
            available_scores: List of score strings that are available
        
        Returns:
            Dictionary of {group_name: [matching_scores]}
            Only includes groups that have at least one matching score
        """
        result = {}
        for name, group in self._groups.items():
            matching_scores = [s for s in group.scores if s in available_scores]
            if matching_scores:
                result[name] = matching_scores
        return result
    
    def get_groups_covering_score(
        self,
        score: str
    ) -> List[str]:
        """
        Get all groups that contain a specific score.
        
        Args:
            score: Score string to find groups for
        
        Returns:
            List of group names that contain this score
        """
        return [
            name for name, group in self._groups.items()
            if score in group.scores
        ]
    
    def to_dict(self) -> Dict:
        """
        Convert entire registry to dictionary.
        
        Returns:
            Dictionary representation of the registry
        """
        return {
            "groups": {name: group.to_dict() for name, group in self._groups.items()}
        }
    
    def to_json(self, indent: int = 2) -> str:
        """
        Convert entire registry to JSON string.
        
        Args:
            indent: Indentation level for pretty printing
        
        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ScoreGroupRegistry":
        """
        Create registry from dictionary.
        
        Args:
            data: Dictionary with "groups" key containing group definitions
        
        Returns:
            ScoreGroupRegistry instance
        """
        registry = cls(use_default_groups=False)
        for name, group_data in data.get("groups", {}).items():
            registry.add_group(ScoreGroupDefinition.from_dict(group_data))
        return registry
    
    @classmethod
    def from_json(cls, json_str: str) -> "ScoreGroupRegistry":
        """
        Create registry from JSON string.
        
        Args:
            json_str: JSON string representation
        
        Returns:
            ScoreGroupRegistry instance
        """
        return cls.from_dict(json.loads(json_str))
    
    def copy(self) -> "ScoreGroupRegistry":
        """
        Create a copy of this registry.
        
        Returns:
            New ScoreGroupRegistry instance with same groups
        """
        new_registry = ScoreGroupRegistry(use_default_groups=False)
        for group in self._groups.values():
            new_registry.add_group(
                ScoreGroupDefinition(
                    name=group.name,
                    scores=group.scores.copy(),
                    description=group.description,
                    priority=group.priority
                )
            )
        return new_registry
    
    def __len__(self) -> int:
        """Number of registered groups"""
        return len(self._groups)
    
    def __contains__(self, group_name: str) -> bool:
        """Check if group exists in registry"""
        return group_name in self._groups
    
    def __iter__(self):
        """Iterate over group names"""
        return iter(self._groups.keys())


# Global registry instance (optional singleton pattern)
_global_registry: Optional[ScoreGroupRegistry] = None


def get_global_registry() -> ScoreGroupRegistry:
    """
    Get the global score group registry instance.
    
    Returns:
        Shared ScoreGroupRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ScoreGroupRegistry()
    return _global_registry


def reset_global_registry() -> None:
    """Reset the global registry (useful for testing)"""
    global _global_registry
    _global_registry = None
