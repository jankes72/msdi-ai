"""
SSI Parameters - Parametry systemu SSI

Wersja: 1.0
Data: 2026-07-28
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class EconomicParameters:
    accuracy_weight: float = 0.4
    odds_weight: float = 0.3
    risk_weight: float = -0.3
    min_odds_threshold: float = 1.5
    max_risk_threshold: float = 0.3
    
    def calculate_value(self, accuracy: float, odds: float, risk: float) -> float:
        return accuracy * self.accuracy_weight + odds * self.odds_weight + risk * self.risk_weight


@dataclass
class LearningParameters:
    base_learning_rate: float = 0.01
    adaptation_rate: float = 0.05
    memory_retention: float = 0.9


@dataclass
class StrategyParameters:
    ranking_a_plus: float = 0.85
    ranking_a: float = 0.75
    ranking_b: float = 0.60
    ranking_c: float = 0.40


@dataclass
class SSIParameters:
    economic: EconomicParameters = field(default_factory=EconomicParameters)
    learning: LearningParameters = field(default_factory=LearningParameters)
    strategy: StrategyParameters = field(default_factory=StrategyParameters)


parameters_instance: Optional[SSIParameters] = None


def get_parameters() -> SSIParameters:
    global parameters_instance
    if parameters_instance is None:
        parameters_instance = SSIParameters()
    return parameters_instance


def reset_parameters() -> None:
    global parameters_instance
    parameters_instance = None
