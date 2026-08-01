"""
SSI V5 - Teacher Engine Configuration
Konfiguracja silnika nauczyciela

Zgodnie z dokumentacja:
- 04_AGENT_MEMORY_BEHAVIOR_EVOLUTION.md
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum, auto


class TeacherMode(Enum):
    """Tryby pracy nauczyciela."""
    PASSIVE = auto()      # Tylko obserwacja, bez ingerencji
    ACTIVE = auto()       # Obserwacja + aktywne uczenie
    STRICT = auto()       # Obserwacja + ingerencja w przypadku bledow
    AUTONOMOUS = auto()   # Pelna autonomia - nauczyciel podejmuje decyzje


class TeachingStrategy(Enum):
    """Strategie nauczania."""
    OBSERVE_ONLY = auto()     # Tylko obserwacja
    GUIDE = auto()            # Prowadzenie (rekomendacje)
    CORRECT = auto()          # Korygowanie bledow
    DEMONSTRATE = auto()      # Demonstrowanie
    REINFORCE = auto()        # Wzmacnianie
    PUNISH = auto()           # Karanie
    COMBINED = auto()         # Kombinacja wszystkich


class TeacherStatus(Enum):
    """Status nauczyciela."""
    IDLE = auto()             # Bezczynny
    OBSERVING = auto()        # Obserwuje agentow
    ANALYZING = auto()         # Analizuje zachowania
    TEACHING = auto()         # Uczy agenta
    EVALUATING = auto()       # Ocenia wyniki
    SLEEPING = auto()         # Uspiony
    ERROR = auto()            # Blad


class ObservationStatus(Enum):
    """Status obserwacji."""
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()


@dataclass
class TeacherConfig:
    """Konfiguracja Teacher Engine."""
    
    # Ogolne
    name: str = "SSI_V5_Teacher_Engine"
    version: str = "1.0.0"
    description: str = "Teacher Engine for SSI V5 - Learning and observation system"
    
    # Tryb pracy
    mode: TeacherMode = TeacherMode.ACTIVE
    strategy: TeachingStrategy = TeachingStrategy.COMBINED
    
    # Cykle
    observation_interval_seconds: float = 60.0
    analysis_interval_seconds: float = 300.0
    teaching_interval_seconds: float = 600.0
    evaluation_interval_seconds: float = 1800.0
    
    # Agenci
    monitor_all_agents: bool = True
    monitored_agent_ids: List[str] = field(default_factory=list)
    
    # Obszar obserwacji
    observe_decisions: bool = True
    observe_strategies: bool = True
    observe_behaviors: bool = True
    observe_interactions: bool = True
    observe_learning: bool = True
    
    # Parametry uczenia
    learning_rate: float = 0.1
    correction_strength: float = 0.5
    reinforcement_factor: float = 1.2
    punishment_factor: float = 0.8
    
    # Progi
    success_threshold: float = 0.7
    failure_threshold: float = 0.3
    improvement_threshold: float = 0.1
    degradation_threshold: float = -0.1
    
    # Pamiec
    enable_memory_logging: bool = True
    memory_retention_days: int = 30
    
    # Integracja
    integrate_with_model_memory: bool = True
    integrate_with_agent_memory: bool = True
    integrate_with_llm_queue: bool = True
    
    # Logging
    log_observations: bool = True
    log_analysis: bool = True
    log_teaching: bool = True
    log_evaluations: bool = True
    log_errors: bool = True
    
    # Debug
    debug_mode: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        return {
            "name": self.name,
            "version": self.version,
            "mode": self.mode.name,
            "strategy": self.strategy.name
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TeacherConfig':
        """Tworzenie z slownika."""
        return cls(
            name=data.get("name", "SSI_V5_Teacher_Engine"),
            version=data.get("version", "1.0.0"),
            mode=TeacherMode[data.get("mode", "ACTIVE")],
            strategy=TeachingStrategy[data.get("strategy", "COMBINED")]
        )
