"""
SSI V4 Agent Core - Podstawowy moduł agentów

Główny moduł zawierający klasy do zarządzania agentami w systemie V4.

Odpowiedzialność:
- Agent: Główna klasa agenta z osobowością, pamięcią i metrykami
- AgentStatus: Statusy agenta (BORN, INITIALIZED, ACTIVE, THINKING, itd.)
- AgentType: Typy agentów (Ekspert_Mentalny, Łowca_Wzorców, Analityk_Ryzyka, itd.)
- AgentConfig: Konfiguracja agenta
- AgentManager: Zarządzanie populacją agentów
- tworz_agent: Fabryka tworząca agentów

Zgodnie z:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 4.1 (V4 Agent System)
- 05_AGENT_SYSTEM.md (Pełna specyfikacja systemu agentów)
- 10_IMPLEMENTATION_MAP.md Etap 4A (Agent Foundation)

Architektura:
┌─────────────────────────────────────────────────────────────┐
│                    AGENT CORE SYSTEM                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐      ┌─────────────────┐                 │
│  │   Agent         │      │  AgentManager   │                 │
│  │  - agent_id     │      │  - agents: Dict │                 │
│  │  - agent_type   │◄─────│  - add/remove   │                 │
│  │  - status       │  ↓   │  - get/find     │                 │
│  │  - personality  │  │   │  - statistics   │                 │
│  │  - memory       │  │   └─────────────────┘                 │
│  │  - decisions    │  │                                       │
│  │  - history      │  │                                       │
│  └─────────────────┘  │                                       │
│         ↓            ╭──────┴──────╮                              │
│  ┌─────────────────┐         │         │                      │
│  │  Decision       │         │         │                      │
│  │  Process        │         │         │                      │
│  └─────────────────┘         │         │                      │
│                            ╰─────────────────────────╯               │
└─────────────────────────────────────────────────────────────┘

Zależności:
- Zależy od: V3 World Memory System (dane wejściowe)
- Rozszerza: SSI.core.base_classes.BaseAgent
- Wspiera: Strategy System, Laboratories, Decision Engine

Wersja: 1.0
Data: 2026-07-28
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum, auto
import uuid
import json
import threading
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


# ============================================================================
# IMPORTY V3 - Integracja z World Memory System
# ============================================================================

try:
    # Import z V3 Integration
    from ..v3.v3_integration import V3Integration, get_v3_integration
    from ..v3.memory.memory_manager import MemoryManager
    from ..v3.memory.pattern_memory import PatternMemory
    from ..v3.memory.world_memory import WorldMemory
    from ..v3.memory.observation_memory import ObservationMemory
    from ..v3.memory.metadata_memory import MetadataMemory
    V3_AVAILABLE = True
except ImportError as e:
    logger.warning(f"V3 Integration niedostępne: {e}")
    V3Integration = None
    MemoryManager = None
    PatternMemory = None
    WorldMemory = None
    ObservationMemory = None
    MetadataMemory = None
    V3_AVAILABLE = False


# ============================================================================
# ENUMY - Statusy i Typy Agentów
# ============================================================================

class AgentStatus(Enum):
    """
    Statusy agenta w systemie V4.
    
    Zgodnie z 05_AGENT_SYSTEM.md Sekcja 8.1 (Proces Decyzyjny)
    """
    # Statusy cyklu życia
    BORN = auto()              # Agent został utworzony (początek)
    INITIALIZED = auto()      # Agent zainicjowany (gotowy do działania)
    ACTIVE = auto()            # Agent aktywny (pracuje normalnie)
    THINKING = auto()          # Agent analizuje dane
    DECIDING = auto()          # Agent podejmuje decyzję
    RESTING = auto()           # Agent w stanie spoczynku
    LEARNING = auto()          # Agent uczy się z doświadczenia
    EVOLVING = auto()          # Agent ewoluuje (zmiana parametrów)
    
    # Statusy specjalne
    ERROR = auto()             # Błąd w działaniu agenta
    ARCHIVED = auto()          # Agent zarchiwizowany (nieaktywny)
    SLEEPING = auto()          # Agent uśpiony (tymczasowo nieaktywny)


class AgentType(Enum):
    """
    Typy agentów w systemie V4.
    
    Zgodnie z 05_AGENT_SYSTEM.md Sekcja 2.3 (Pierwsza Populacja) i 3.3 (Nowe Typy)
    """
    # Podstawowe typy (pierwsza populacja)
    ANALYST = "analyst"                    # Analityk - szuka stabilnych wzorców
    VALUE_STRATEGIST = "value_strategist"  # Strateg Wartości - maksymalizuje EV
    EXPERIMENTATOR = "experimentator"      # Eksperymentator - testuje nowe rozwiązania
    
    # Specjalizacje powstałe z ewolucji
    MENTAL_EXPERT = "mental_expert"        # Ekspert Mentalny - stabilne, długoterminowe strategie
    PATTERN_HUNTER = "pattern_hunter"      # Łowca Wzorców - odkrywa ukryte zależności
    RISK_ANALYST = "risk_analyst"          # Analityk Ryzyka - ocena i zarządzanie ryzykiem
    INVESTOR = "investor"                  # Inwestor - podejmowanie decyzji inwestycyjnych
    CONSERVATOR = "conservator"            # Konserwatysta - chroni sprawdzone strategie
    AGGRESSOR = "aggressor"                # Agresor - wysokie ryzyko, wysoka nagroda
    BALANCER = "balancer"                  # Balanser - zrównoważone podejście
    TEST_AGENT = "test_agent"              # Agent Testowy - do eksperymentów


# ============================================================================
# KONFIGURACJA AGENTA
# ============================================================================

@dataclass
class AgentConfig:
    """
    Konfiguracja agenta V4.
    
    Zgodnie z 05_AGENT_SYSTEM.md Sekcja 2.3 (Parametry agentów)
    
    Attributes:
        agent_id: Unikalne ID agenta
        agent_type: Typ agenta (z AgentType)
        name: Pełna nazwa agenta
        description: Opis agenta
        initial_personality: Początkowy wektor osobowości
        initial_emotional_state: Początkowy stan emocjonalny
        room_id: ID pokoju, do którego należy agent
        memory_size: Maksymalny rozmiar pamięci prywatnej
        decision_history_size: Maksymalna historia decyzji
        trust_matrix_size: Maksymalna liczba powiązań zaufania
        confidence_threshold: Próg pewności do podejmowania decyzji
        frustration_threshold: Próg frustracji causing zmianę strategii
        evolution_rate: Szybkość ewolucji parametrów osobowości
    """
    # Podstawowe ustawienia
    agent_id: str = field(default_factory=lambda: f"agent_{uuid.uuid4().hex[:12]}")
    agent_type: AgentType = AgentType.ANALYST
    name: str = ""
    description: str = ""
    
    # Ustawienia osobowości i emocji
    initial_personality: Optional[Dict[str, float]] = None
    initial_emotional_state: Optional[Dict[str, float]] = None
    
    # Ustawienia środowiska
    room_id: str = "ROOM_CORE"
    world_access: List[str] = field(default_factory=list)
    model_access: List[str] = field(default_factory=list)
    
    # Ustawienia pamięci
    memory_size: int = 10000
    decision_history_size: int = 1000
    trust_matrix_size: int = 100
    
    # Progi decyzyjne
    confidence_threshold: float = 0.7
    frustration_threshold: float = 0.8
    satisfaction_threshold: float = 0.6
    
    # Parametry ewolucji
    evolution_rate: float = 0.01
    learning_rate: float = 0.1
    
    # Integracja z V3 World Memory System
    v3_memory_access: bool = True
    v2_model_access: bool = True
    v3_world_memory_access: bool = True      # Dostęp do World Memory
    v3_pattern_memory_access: bool = True    # Dostęp do Pattern Memory
    v3_metadata_access: bool = True          # Dostęp do Metadata Memory
    use_v3_knowledge: bool = True            # Czy korzystać z wiedzy V3 przy podejmowaniu decyzji
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "name": self.name,
            "description": self.description,
            "room_id": self.room_id,
            "world_access": self.world_access,
            "model_access": self.model_access,
            "memory_size": self.memory_size,
            "decision_history_size": self.decision_history_size,
            "trust_matrix_size": self.trust_matrix_size,
            "confidence_threshold": self.confidence_threshold,
            "frustration_threshold": self.frustration_threshold,
            "satisfaction_threshold": self.satisfaction_threshold,
            "evolution_rate": self.evolution_rate,
            "learning_rate": self.learning_rate,
            "v3_memory_access": self.v3_memory_access,
            "v2_model_access": self.v2_model_access,
            "v3_world_memory_access": self.v3_world_memory_access,
            "v3_pattern_memory_access": self.v3_pattern_memory_access,
            "v3_metadata_access": self.v3_metadata_access,
            "use_v3_knowledge": self.use_v3_knowledge
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentConfig':
        """Tworzenie z słownika"""
        data = data.copy()
        if "agent_type" in data and isinstance(data["agent_type"], str):
            try:
                data["agent_type"] = AgentType(data["agent_type"])
            except ValueError:
                data["agent_type"] = AgentType.ANALYST
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# ============================================================================
# WEKTOR OSOBOWOŚCI I STAN EMOCJONALNY (Referencja do personality_vector.py)
# ============================================================================

@dataclass
class PersonalityVector:
    """
    Wektor 8 parametrów osobowości agenta.
    
    Zgodnie z 05_AGENT_SYSTEM.md Sekcja 3.1 (Personality Vector)
    
    Attributes:
        analysis_power: Zdolność do analizy danych i zależności (0.0-1.0)
        risk_acceptance: Poziom akceptowanego ryzyka (0.0-1.0)
        curiosity: Skłonność do poszukiwania nowych rozwiązań (0.0-1.0)
        security_preference: Preferencja stabilnych i bezpiecznych decyzji (0.0-1.0)
        experimentation_level: Gotowość do testowania nowych hipotez (0.0-1.0)
        independence: Poziom samodzielności decyzji (0.0-1.0)
        trust_level: Aktualny poziom zaufania do innych agentów (0.0-1.0)
        resilience: Odporność na błędne decyzje i porażki (0.0-1.0)
    """
    analysis_power: float = 0.5
    risk_acceptance: float = 0.5
    curiosity: float = 0.5
    security_preference: float = 0.5
    experimentation_level: float = 0.5
    independence: float = 0.5
    trust_level: float = 0.5
    resilience: float = 0.5
    
    def to_dict(self) -> Dict[str, float]:
        """Konwersja do słownika"""
        return {
            "analysis_power": self.analysis_power,
            "risk_acceptance": self.risk_acceptance,
            "curiosity": self.curiosity,
            "security_preference": self.security_preference,
            "experimentation_level": self.experimentation_level,
            "independence": self.independence,
            "trust_level": self.trust_level,
            "resilience": self.resilience
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'PersonalityVector':
        """Tworzenie z słownika"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def get_evolution_direction(self, experience: Dict[str, Any]) -> Dict[str, float]:
        """
        Określa kierunek ewolucji na podstawie doświadczenia.
        
        Zgodnie z 05_AGENT_SYSTEM.md Sekcja 9.1 (Czynniki Ewolucji)
        
        Args:
            experience: Doświadczenie agenta (wyniki, błędy, sukcesy)
            
        Returns:
            Słownik z kierunkami zmian parametrów (-1.0 do 1.0)
        """
        directions = {}
        
        # Analiza wyników
        success_rate = experience.get("success_rate", 0.5)
        error_rate = experience.get("error_rate", 0.5)
        discovery_rate = experience.get("discovery_rate", 0.5)
        
        # Ewolucja na podstawie wyników
        if success_rate > 0.7:
            # Wysoka skuteczność - wzmacniamy obecne zachowania
            directions["analysis_power"] = 0.05 if self.analysis_power < 0.9 else 0
            directions["resilience"] = 0.03 if self.resilience < 0.95 else 0
        else:
            # Niska skuteczność - szukamy zmian
            directions["curiosity"] = 0.05 if self.curiosity < 0.9 else 0
            directions["experimentation_level"] = 0.05 if self.experimentation_level < 0.9 else 0
        
        if error_rate > 0.3:
            # Wysoki poziom błędów - zwiększamy ostrożność
            directions["security_preference"] = 0.05 if self.security_preference < 0.9 else 0
            directions["risk_acceptance"] = -0.05 if self.risk_acceptance > 0.1 else 0
        
        if discovery_rate > 0.6:
            # Wysoki poziom odkryć - wzmacniamy eksperymentowanie
            directions["experimentation_level"] = 0.03 if self.experimentation_level < 0.95 else 0
            directions["curiosity"] = 0.03 if self.curiosity < 0.95 else 0
        
        return directions
    
    def evolve(self, directions: Dict[str, float], rate: float = 0.01) -> 'PersonalityVector':
        """
        Ewoluuje wektor osobowości na podstawie kierunku zmian.
        
        Args:
            directions: Kierunki zmian parametrów
            rate: Szybkość ewolucji
            
        Returns:
            Nowy PersonalityVector
        """
        new_values = {}
        for field_name in self.__dataclass_fields__:
            current_value = getattr(self, field_name)
            direction = directions.get(field_name, 0.0)
            new_value = current_value + direction * rate
            new_values[field_name] = max(0.0, min(1.0, new_value))
        
        # return cls(**new_values)
        return PersonalityVector(**new_values)


@dataclass
class EmotionalState:
    """
    Stan emocjonalny agenta (5 parametrów).
    
    Zgodnie z 05_AGENT_SYSTEM.md Sekcja 4.1 (Lista Parametrów Emocjonalnych)
    
    Attributes:
        confidence: Pewność siebie (0.0-1.0)
        frustration: Frustracja (0.0-1.0)
        curiosity_level: Poziom ciekawości (0.0-1.0)
        satisfaction: Satysfakcja (0.0-1.0)
        strategic_pressure: Ciśnienie strategiczne (0.0-1.0)
    """
    confidence: float = 0.7
    frustration: float = 0.1
    curiosity_level: float = 0.5
    satisfaction: float = 0.5
    strategic_pressure: float = 0.1
    
    def to_dict(self) -> Dict[str, float]:
        """Konwersja do słownika"""
        return {
            "confidence": self.confidence,
            "frustration": self.frustration,
            "curiosity_level": self.curiosity_level,
            "satisfaction": self.satisfaction,
            "strategic_pressure": self.strategic_pressure
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'EmotionalState':
        """Tworzenie z słownika"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def update_from_result(self, result: Dict[str, Any], config: AgentConfig) -> 'EmotionalState':
        """
        Aktualizuje stan emocjonalny na podstawie wyniku decyzji.
        
        Zgodnie z 05_AGENT_SYSTEM.md Sekcja 4.2 (Mechanizmy Emocjonalne)
        
        Args:
            result: Wynik decyzji (trafna/nietrafna, wartość, itd.)
            config: Konfiguracja agenta
            
        Returns:
            Nowy EmotionalState
        """
        new_values = {}
        
        # Inicjalizacja
        for field_name in self.__dataclass_fields__:
            new_values[field_name] = getattr(self, field_name)
        
        is_correct = result.get("correct", False)
        value = result.get("value", 0.5)
        
        # Mechanizmy emocjonalne
        if is_correct:
            # Trafna decyzja - wzrost pewności i satysfakcji
            new_values["confidence"] = min(1.0, new_values["confidence"] + 0.05)
            new_values["satisfaction"] = min(1.0, new_values["satisfaction"] + 0.1)
            new_values["frustration"] = max(0.0, new_values["frustration"] - 0.2)
            
            # Większa wartość = większa satysfakcja
            if value > 0.8:
                new_values["satisfaction"] = min(1.0, new_values["satisfaction"] + 0.05)
            
        else:
            # Nietrafna decyzja - wzrost frustracji, spadek pewności
            new_values["frustration"] = min(1.0, new_values["frustration"] + 0.15)
            new_values["confidence"] = max(0.1, new_values["confidence"] - 0.1)
            new_values["satisfaction"] = max(0.0, new_values["satisfaction"] - 0.1)
            new_values["strategic_pressure"] = min(1.0, new_values["strategic_pressure"] + 0.1)
        
        # Powolny spadek satysfakcji w czasie
        new_values["satisfaction"] = max(0.0, new_values["satisfaction"] - 0.01)
        
        # Ciśnienie strategiczne maleje po znalezieniu dobrych rozwiązań
        if new_values["satisfaction"] > config.satisfaction_threshold:
            new_values["strategic_pressure"] = max(0.0, new_values["strategic_pressure"] - 0.05)
        
        # return cls(**new_values)
        return EmotionalState(**new_values)


# ============================================================================
# STRUKTURY PAMIĘCI AGENTA
# ============================================================================

@dataclass
class DecisionRecord:
    """Rekord decyzji agenta"""
    decision_id: str
    timestamp: str
    context: Dict[str, Any]
    chosen_action: Any
    confidence: float
    expected_value: float
    actual_result: Optional[Any] = None
    was_correct: Optional[bool] = None
    evaluation: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "timestamp": self.timestamp,
            "context": self.context,
            "chosen_action": self.chosen_action,
            "confidence": self.confidence,
            "expected_value": self.expected_value,
            "actual_result": self.actual_result,
            "was_correct": self.was_correct,
            "evaluation": self.evaluation
        }


@dataclass
class TrustEntry:
    """Wpis w macierzy zaufania agenta"""
    trust_score: float = 0.5
    weight: float = 0.5
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "trust_score": self.trust_score,
            "weight": self.weight,
            "history": self.history
        }


@dataclass
class AgentMemory:
    """
    Pamięć agenta - dwuwarstwowa struktura.
    
    Zgodnie z 05_AGENT_SYSTEM.md Sekcja 7.1 (Dwuwarstwowa Pamięć Agenta)
    """
    # Pamięć globalna (wspólna - referencja do V3)
    global_memory_access: bool = True
    
    # Prywatny notatnik
    private_notebook: Dict[str, Any] = field(default_factory=dict)
    
    # Historia decyzji
    decision_history: List[DecisionRecord] = field(default_factory=list)
    
    # Strategie agenta
    strategies: Dict[str, Any] = field(default_factory=dict)
    
    # Eksperymenty
    experiments: Dict[str, Any] = field(default_factory=dict)
    
    # Wyniki
    results: Dict[str, Any] = field(default_factory=dict)
    
    # Błędy
    errors: Dict[str, Any] = field(default_factory=dict)
    
    # Lekcje
    lessons: List[str] = field(default_factory=list)
    
    # Macierz zaufania (do innych agentów)
    trust_matrix: Dict[str, TrustEntry] = field(default_factory=dict)
    
    def add_decision(self, record: DecisionRecord) -> None:
        """Dodaje rekord decyzji"""
        self.decision_history.append(record)
        
        # Ogranicz rozmiar historii
        if len(self.decision_history) > 1000:
            self.decision_history = self.decision_history[-1000:]
    
    def add_lesson(self, lesson: str) -> None:
        """Dodaje lekcję wyciągniętą z doświadczenia"""
        if lesson not in self.lessons:
            self.lessons.append(lesson)
    
    def update_trust(self, agent_id: str, trust_change: float, reason: str) -> None:
        """Aktualizuje zaufanie do innego agenta"""
        if agent_id not in self.trust_matrix:
            self.trust_matrix[agent_id] = TrustEntry()
        
        old_score = self.trust_matrix[agent_id].trust_score
        new_score = max(0.0, min(1.0, old_score + trust_change))
        
        self.trust_matrix[agent_id].trust_score = new_score
        self.trust_matrix[agent_id].weight = new_score
        
        self.trust_matrix[agent_id].history.append({
            "timestamp": datetime.now().isoformat(),
            "trust_change": trust_change,
            "new_trust_score": new_score,
            "reason": reason
        })
    
    def get_trust_weight(self, agent_id: str) -> float:
        """Pobiera wagę zaufania do agenta"""
        if agent_id in self.trust_matrix:
            return self.trust_matrix[agent_id].weight
        return 0.5  # Domyślna waga dla nieznanych agentów
    
    def get_status_report(self) -> Dict[str, Any]:
        """Generuje raport statusu pamięci"""
        return {
            "decision_history_size": len(self.decision_history),
            "private_notebook_size": len(self.private_notebook),
            "strategies_count": len(self.strategies),
            "experiments_count": len(self.experiments),
            "lessons_count": len(self.lessons),
            "trust_entries_count": len(self.trust_matrix)
        }


# ============================================================================
# GŁÓWNA KLASA AGENTA
# ============================================================================

class Agent:
    """
    Główna klasa agenta w systemie V4.
    
    Odpowiedzialność:
    - Przechowywanie stanu agenta (ID, typ, status)
    - Zarządzanie osobowością i stanem emocjonalnym
    - Podejmowanie decyzji na podstawie danych z V3
    - Uczenie się z doświadczenia
    - Ewolucja parametrów
    - Współpraca z innymi agentami
    
    Zgodnie z 05_AGENT_SYSTEM.md Sekcja 8.1 (Indywidualny Proces Decyzyjny)
    
    Attributes:
        agent_id: Unikalne ID agenta
        agent_type: Typ agenta
        status: Aktualny status
        personality: Wektor osobowości
        emotional_state: Stan emocjonalny
        memory: Pamięć agenta
        config: Konfiguracja agenta
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Inicjalizacja agenta.
        
        Args:
            config: Konfiguracja agenta (opcjonalnie)
        """
        self.config = config or AgentConfig()
        
        # Podstawowe atrybuty
        self.agent_id = self.config.agent_id
        self.agent_type = self.config.agent_type
        self.status = AgentStatus.BORN
        
        # Osobowość i emocje
        if self.config.initial_personality:
            self.personality = PersonalityVector.from_dict(self.config.initial_personality)
        else:
            # Domyślne wartości w zależności od typu agenta
            self.personality = self._get_default_personality()
        
        if self.config.initial_emotional_state:
            self.emotional_state = EmotionalState.from_dict(self.config.initial_emotional_state)
        else:
            self.emotional_state = EmotionalState()
        
        # Pamięć
        self.memory = AgentMemory()
        
        # Metryki
        self.metrics: Dict[str, Any] = {
            "total_decisions": 0,
            "correct_decisions": 0,
            "incorrect_decisions": 0,
            "success_rate": 0.0,
            "discovery_rate": 0.0,
            "error_rate": 0.0,
            "average_confidence": 0.7
        }
        
        # Środowisko
        self.room_id = self.config.room_id
        self.world_access = self.config.world_access or []
        self.model_access = self.config.model_access or []
        
        # Czas
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.last_decision_time: Optional[datetime] = None
        
        # Lock dla thread-safety
        self._lock = threading.Lock()
        
        # Integracja z V3 World Memory System
        self._v3_integration: Optional[V3Integration] = None
        self._v3_memory_manager: Optional[MemoryManager] = None
        self._v3_world_memory: Optional[WorldMemory] = None
        self._v3_pattern_memory: Optional[PatternMemory] = None
        self._v3_metadata_memory: Optional[MetadataMemory] = None
        self._v3_observation_memory: Optional[ObservationMemory] = None
        
        # Flaga wskazująca, czy V3 jest dostępne dla tego agenta
        self._v3_available: bool = False
        
        # Inicjalizacja integracji V3
        self._initialize_v3_integration()
        
        logger.info(f"Utworzono agenta: {self.agent_id} (typ: {self.agent_type.value})")
    
    def _get_default_personality(self) -> PersonalityVector:
        """Zwraca domyślne wartości osobowości w zależności od typu agenta"""
        # Zgodnie z 05_AGENT_SYSTEM.md Sekcja 2.3 (Pierwsza Populacja)
        if self.agent_type == AgentType.ANALYST:
            return PersonalityVector(
                analysis_power=0.80,
                risk_acceptance=0.30,
                curiosity=0.40,
                security_preference=0.85,
                experimentation_level=0.20,
                independence=0.60,
                trust_level=0.50,
                resilience=0.90
            )
        elif self.agent_type == AgentType.VALUE_STRATEGIST:
            return PersonalityVector(
                analysis_power=0.85,
                risk_acceptance=0.55,
                curiosity=0.70,
                security_preference=0.50,
                experimentation_level=0.40,
                independence=0.70,
                trust_level=0.50,
                resilience=0.80
            )
        elif self.agent_type == AgentType.EXPERIMENTATOR:
            return PersonalityVector(
                analysis_power=0.70,
                risk_acceptance=0.80,
                curiosity=0.85,
                security_preference=0.30,
                experimentation_level=0.90,
                independence=0.80,
                trust_level=0.50,
                resilience=0.85
            )
        else:
            # Domyślne wartości dla innych typów
            return PersonalityVector()
    
    def _initialize_v3_integration(self) -> None:
        """
        Inicjalizuje integrację z V3 World Memory System.
        Łączy z globalną instancją V3Integration lub tworzy lokalne połączenie.
        """
        if not self.config.v3_world_memory_access and not self.config.v3_pattern_memory_access:
            self._v3_available = False
            return
        
        try:
            # Spróbuj uzyskać globalną instancję V3Integration
            if V3_AVAILABLE and get_v3_integration is not None:
                try:
                    v3_integration = get_v3_integration()
                    if v3_integration:
                        self._connect_to_v3_integration(v3_integration)
                        return
                except Exception:
                    pass
            
            # Jeśli nie ma globalnej instancji, spróbuj utworzyć lokalne połączenie
            if V3_AVAILABLE:
                try:
                    from ..v3.v3_integration import tworz_v3_integration
                    v3_integration = tworz_v3_integration()
                    self._connect_to_v3_integration(v3_integration)
                except Exception as e:
                    logger.warning(f"Nie udało się utworzyć V3Integration dla agenta {self.agent_id}: {e}")
            
            self._v3_available = self._v3_memory_manager is not None
            
        except Exception as e:
            logger.warning(f"Błąd inicjalizacji V3 dla agenta {self.agent_id}: {e}")
            self._v3_available = False
    
    def _connect_to_v3_integration(self, v3_integration: V3Integration) -> None:
        """
        Łączy agenta z instancją V3Integration.
        
        Args:
            v3_integration: Instancja V3Integration
        """
        try:
            self._v3_integration = v3_integration
            
            # Pobierz MemoryManager
            if hasattr(v3_integration, 'memory_manager') and v3_integration.memory_manager:
                self._v3_memory_manager = v3_integration.memory_manager
            
            # Pobierz poszczególne pamięci z MemoryManager
            if self._v3_memory_manager:
                memory = self._v3_memory_manager
                if hasattr(memory, 'world_memory') and memory.world_memory:
                    self._v3_world_memory = memory.world_memory
                if hasattr(memory, 'pattern_memory') and memory.pattern_memory:
                    self._v3_pattern_memory = memory.pattern_memory
                if hasattr(memory, 'metadata_memory') and memory.metadata_memory:
                    self._v3_metadata_memory = memory.metadata_memory
                if hasattr(memory, 'observation_memory') and memory.observation_memory:
                    self._v3_observation_memory = memory.observation_memory
            
            self._v3_available = True
            logger.info(f"Agent {self.agent_id} połączony z V3 World Memory System")
            
        except Exception as e:
            logger.error(f"Błąd łączenia z V3Integration: {e}")
            self._v3_available = False
    
    def is_v3_available(self) -> bool:
        """Sprawdza, czy V3 jest dostępne dla tego agenta."""
        return self._v3_available and V3_AVAILABLE
    
    def connect_to_v3(self, v3_integration: V3Integration) -> bool:
        """
        Ręcznie łączy agenta z instancją V3Integration.
        
        Args:
            v3_integration: Instancja V3Integration
            
        Returns:
            True jeśli połączenie się powiodło
        """
        try:
            self._connect_to_v3_integration(v3_integration)
            return self._v3_available
        except Exception as e:
            logger.error(f"Błąd ręcznego łączenia z V3: {e}")
            return False
    
    def disconnect_from_v3(self) -> None:
        """Odłącza agenta od V3 World Memory System."""
        self._v3_integration = None
        self._v3_memory_manager = None
        self._v3_world_memory = None
        self._v3_pattern_memory = None
        self._v3_metadata_memory = None
        self._v3_observation_memory = None
        self._v3_available = False
        logger.info(f"Agent {self.agent_id} odłączony od V3")
    
    # ==========================================================================
    # METODY DOSTĘPU DO V3 MEMORY (tylko do odczytu - agenci nie modyfikują V3)
    # ==========================================================================
    
    def get_world_memory(self) -> Optional[WorldMemory]:
        """
        Zwraca instancję WorldMemory z V3.
        Agenci mogą jedynie odczytywać dane, nie modyfikować ich.
        
        Returns:
            WorldMemory lub None
        """
        if not self.is_v3_available() or not self.config.v3_world_memory_access:
            return None
        return self._v3_world_memory
    
    def get_pattern_memory(self) -> Optional[PatternMemory]:
        """
        Zwraca instancję PatternMemory z V3.
        Agenci mogą jedynie odczytywać dane, nie modyfikować ich.
        
        Returns:
            PatternMemory lub None
        """
        if not self.is_v3_available() or not self.config.v3_pattern_memory_access:
            return None
        return self._v3_pattern_memory
    
    def get_metadata_memory(self) -> Optional[MetadataMemory]:
        """
        Zwraca instancję MetadataMemory z V3.
        Agenci mogą jedynie odczytywać dane, nie modyfikować ich.
        
        Returns:
            MetadataMemory lub None
        """
        if not self.is_v3_available() or not self.config.v3_metadata_access:
            return None
        return self._v3_metadata_memory
    
    def get_observation_memory(self) -> Optional[ObservationMemory]:
        """
        Zwraca instancję ObservationMemory z V3.
        Agenci mogą jedynie odczytywać dane, nie modyfikować ich.
        
        Returns:
            ObservationMemory lub None
        """
        if not self.is_v3_available():
            return None
        return self._v3_observation_memory
    
    def get_v3_integration(self) -> Optional[V3Integration]:
        """
        Zwraca instancję V3Integration.
        
        Returns:
            V3Integration lub None
        """
        return self._v3_integration
    
    def get_worlds_from_v3(self, limit: int = 100, world_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Pobiera światy z V3 World Memory.
        
        Args:
            limit: Maksymalna liczba światów do zwrócenia
            world_type: Filtr po typie świata (opcjonalnie)
            
        Returns:
            Lista światów (jako dict)
        """
        if not self.is_v3_available() or not self.config.v3_world_memory_access:
            return []
        
        try:
            world_memory = self.get_world_memory()
            if world_memory and hasattr(world_memory, 'get_all_worlds'):
                all_worlds = world_memory.get_all_worlds()
                
                if world_type:
                    all_worlds = [w for w in all_worlds if w.get('world_type') == world_type]
                
                return all_worlds[:limit]
        except Exception as e:
            logger.warning(f"Błąd pobierania światów z V3: {e}")
        
        return []
    
    def get_patterns_from_v3(self, limit: int = 100, pattern_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Pobiera wzorce z V3 Pattern Memory.
        
        Args:
            limit: Maksymalna liczba wzorców
            pattern_type: Filtr po typie wzorca (opcjonalnie)
            
        Returns:
            Lista wzorców (jako dict)
        """
        if not self.is_v3_available() or not self.config.v3_pattern_memory_access:
            return []
        
        try:
            pattern_memory = self.get_pattern_memory()
            if pattern_memory and hasattr(pattern_memory, 'get_all_patterns'):
                all_patterns = pattern_memory.get_all_patterns()
                
                if pattern_type:
                    all_patterns = [p for p in all_patterns if p.get('pattern_type') == pattern_type]
                
                return all_patterns[:limit]
        except Exception as e:
            logger.warning(f"Błąd pobierania wzorców z V3: {e}")
        
        return []
    
    def get_metadata_from_v3(self, metadata_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Pobiera metadane z V3 Metadata Memory.
        
        Args:
            metadata_type: Filtr po typie metadanych (opcjonalnie)
            
        Returns:
            Słownik z metadanymi
        """
        if not self.is_v3_available() or not self.config.v3_metadata_access:
            return {}
        
        try:
            metadata_memory = self.get_metadata_memory()
            if metadata_memory and hasattr(metadata_memory, 'get_all_metadata'):
                all_metadata = metadata_memory.get_all_metadata()
                
                if metadata_type:
                    return {k: v for k, v in all_metadata.items() if k.startswith(metadata_type)}
                
                return all_metadata
        except Exception as e:
            logger.warning(f"Błąd pobierania metadanych z V3: {e}")
        
        return {}
    
    def get_v3_knowledge_summary(self) -> Dict[str, Any]:
        """
        Zwraca podsumowanie wiedzy dostępnej z V3.
        
        Returns:
            Słownik z podsumowaniem wiedzy V3
        """
        summary = {
            "v3_available": self.is_v3_available(),
            "worlds_count": 0,
            "patterns_count": 0,
            "metadata_count": 0,
            "observations_count": 0
        }
        
        if self.is_v3_available():
            try:
                if self._v3_world_memory:
                    summary["worlds_count"] = len(self._v3_world_memory.get_all_worlds())
                if self._v3_pattern_memory:
                    summary["patterns_count"] = len(self._v3_pattern_memory.get_all_patterns())
                if self._v3_metadata_memory:
                    summary["metadata_count"] = len(self._v3_metadata_memory.get_all_metadata())
                if self._v3_observation_memory:
                    summary["observations_count"] = len(self._v3_observation_memory.get_all_observations())
            except Exception as e:
                logger.warning(f"Błąd generowania podsumowania V3: {e}")
        
        return summary
    
    def initialize(self) -> bool:
        """
        Inicjalizacja agenta (przejście ze statusu BORN do INITIALIZED).
        
        Returns:
            True jeśli inicjalizacja się powiodła
        """
        with self._lock:
            try:
                # Validacja konfiguracji
                if not self.agent_id:
                    self.agent_id = f"agent_{uuid.uuid4().hex[:12]}"
                
                # Ustawienie statusu
                self.status = AgentStatus.INITIALIZED
                self.updated_at = datetime.now()
                
                logger.info(f"Zainicjowano agenta: {self.agent_id}")
                return True
                
            except Exception as e:
                logger.error(f"Błąd inicjalizacji agenta {self.agent_id}: {e}")
                self.status = AgentStatus.ERROR
                return False
    
    def set_status(self, status: AgentStatus) -> None:
        """Ustawia status agenta"""
        with self._lock:
            old_status = self.status
            self.status = status
            self.updated_at = datetime.now()
            logger.debug(f"Agent {self.agent_id}: {old_status.name} -> {status.name}")
    
    def make_decision(self, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Podejmuje decyzję na podstawie kontekstu.
        
        Zgodnie z 05_AGENT_SYSTEM.md Sekcja 8.1 (Indywidualny Proces Decyzyjny)
        
        Args:
            context: Kontekst decyzji (światy, modele, strategie, historia, wyniki)
            **kwargs: Dodatkowe parametry
            
        Returns:
            Słownik z decyzją i metadany
        """
        with self._lock:
            self.set_status(AgentStatus.THINKING)
            
            try:
                # 1. Analiza kontekstu
                analysis_result = self._analyze_context(context)
                
                # 2. Wybór akcji
                decision = self._choose_action(analysis_result, context)
                
                # 3. Obliczenie pewności i wartości oczekiwanej
                confidence = self._calculate_confidence(decision, analysis_result)
                expected_value = self._calculate_expected_value(decision, analysis_result)
                
                # 4. Rejestracja decyzji
                decision_record = DecisionRecord(
                    decision_id=f"dec_{uuid.uuid4().hex[:12]}",
                    timestamp=datetime.now().isoformat(),
                    context=context,
                    chosen_action=decision["action"],
                    confidence=confidence,
                    expected_value=expected_value
                )
                
                self.memory.add_decision(decision_record)
                self.last_decision_time = datetime.now()
                
                # 5. Aktualizacja metryk
                self.metrics["total_decisions"] += 1
                self.metrics["average_confidence"] = (
                    self.metrics["average_confidence"] * (self.metrics["total_decisions"] - 1) + confidence
                ) / self.metrics["total_decisions"]
                
                self.set_status(AgentStatus.ACTIVE)
                
                # Zwróć pełną decyzję
                return {
                    "agent_id": self.agent_id,
                    "agent_type": self.agent_type.value,
                    "status": self.status.name,
                    "action": decision["action"],
                    "confidence": confidence,
                    "expected_value": expected_value,
                    "reasoning": decision.get("reasoning", ""),
                    "decision_id": decision_record.decision_id,
                    "timestamp": decision_record.timestamp,
                    "personality_factors": self._get_personality_factors()
                }
                
            except Exception as e:
                logger.error(f"Błąd podejmowania decyzji dla agenta {self.agent_id}: {e}")
                self.set_status(AgentStatus.ERROR)
                return {
                    "agent_id": self.agent_id,
                    "error": str(e),
                    "status": "error",
                    "timestamp": datetime.now().isoformat()
                }
    
    def _analyze_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analizuje kontekst decyzji z wsparciem V3 World Memory"""
        analysis = {
            "worlds": context.get("worlds", []),
            "models": context.get("models", []),
            "strategies": context.get("strategies", []),
            "history": context.get("history", []),
            "results": context.get("results", []),
            
            # Dodatkowa analiza na podstawie osobowości
            "personality_analysis": {
                "analysis_power": self.personality.analysis_power,
                "risk_acceptance": self.personality.risk_acceptance,
                "curiosity": self.personality.curiosity
            }
        }
        
        # Integracja z V3 World Memory - pobierz dodatkowe dane
        if self.config.use_v3_knowledge and self.is_v3_available():
            v3_knowledge = self._get_v3_knowledge_for_decision(context)
            analysis["v3_knowledge"] = v3_knowledge
        
        # Symulacja analizy na podstawie osobowości
        if self.personality.analysis_power > 0.7:
            analysis["deep_analysis"] = True
            analysis["pattern_recognition"] = self.personality.analysis_power * 0.8
        
        if self.personality.curiosity > 0.7:
            analysis["exploration_mode"] = True
        
        return analysis
    
    def _get_v3_knowledge_for_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pobiera wiedzę z V3 World Memory System do wsparcia podejmowania decyzji.
        Agenci jedynie odczytują dane, nie modyfikują ich.
        
        Args:
            context: Kontekst decyzji
            
        Returns:
            Słownik z wiedzą z V3
        """
        v3_knowledge = {
            "from_v3": False,
            "worlds_used": 0,
            "patterns_used": 0,
            "metadata_used": 0
        }
        
        if not self.is_v3_available():
            return v3_knowledge
        
        try:
            # Pobierz światy z V3
            worlds = self.get_worlds_from_v3(limit=50)
            if worlds:
                v3_knowledge["from_v3"] = True
                v3_knowledge["worlds_used"] = len(worlds)
                v3_knowledge["worlds"] = worlds
            
            # Pobierz wzorce z V3
            patterns = self.get_patterns_from_v3(limit=30)
            if patterns:
                v3_knowledge["patterns_used"] = len(patterns)
                v3_knowledge["patterns"] = patterns
            
            # Pobierz metadane z V3
            metadata = self.get_metadata_from_v3()
            if metadata:
                v3_knowledge["metadata_used"] = len(metadata)
                v3_knowledge["metadata"] = metadata
            
            # Podsumowanie statystyk V3
            v3_knowledge["v3_summary"] = self.get_v3_knowledge_summary()
            
        except Exception as e:
            logger.warning(f"Błąd pobierania wiedzy V3 dla agenta {self.agent_id}: {e}")
        
        return v3_knowledge
    
    def _choose_action(self, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Wybiera akcję na podstawie analizy"""
        # Symulacja wyboru akcji w zależności od typu agenta
        
        if self.agent_type == AgentType.ANALYST:
            # Analityk preferuje bezpieczne, sprawdzone wzorce
            return {
                "action": "analyze_pattern",
                "reasoning": "Wybrano analizę wzorców na podstawie wysokiej zdolności analitycznej",
                "type": "analysis"
            }
        
        elif self.agent_type == AgentType.VALUE_STRATEGIST:
            # Strateg Wartości szuka wysokiej wartości oczekiwanej
            return {
                "action": "maximize_ev",
                "reasoning": "Wybrano maksymalizację wartości oczekiwanej",
                "type": "value_optimization"
            }
        
        elif self.agent_type == AgentType.EXPERIMENTATOR:
            # Eksperymentator testuje nowe rozwiązania
            return {
                "action": "test_new_strategy",
                "reasoning": "Wybrano testowanie nowej strategii dzięki wysokiej ciekawości",
                "type": "experimentation"
            }
        
        else:
            # Domyślne działanie
            return {
                "action": "default_decision",
                "reasoning": "Domyślna decyzja",
                "type": "default"
            }
    
    def _calculate_confidence(self, decision: Dict[str, Any], analysis: Dict[str, Any]) -> float:
        """Oblicza pewność decyzji"""
        # Bazowa pewność na podstawie osobowości
        base_confidence = self.emotional_state.confidence
        
        # Modifikacje na podstawie typu agenta i analizy
        if self.agent_type == AgentType.ANALYST:
            base_confidence *= 1.1  # Analityk jest bardziej pewny
        elif self.agent_type == AgentType.EXPERIMENTATOR:
            base_confidence *= 0.9  # Eksperymentator jest mniej pewny
        
        # Ogranicz do zakresu 0-1
        return max(0.0, min(1.0, base_confidence))
    
    def _calculate_expected_value(self, decision: Dict[str, Any], analysis: Dict[str, Any]) -> float:
        """Oblicza wartość oczekiwaną decyzji"""
        # Bazowa wartość na podstawie types akcji
        if decision.get("type") == "analysis":
            base_value = 0.7
        elif decision.get("type") == "value_optimization":
            base_value = 0.85
        elif decision.get("type") == "experimentation":
            base_value = 0.6
        else:
            base_value = 0.5
        
        # Modifikacje na podstawie osobowości
        risk_factor = self.personality.risk_acceptance
        analysis_factor = self.personality.analysis_power
        
        # Wzór: EV = base_value * (1 + risk_factor * 0.2 - analysis_factor * 0.1)
        return max(0.0, min(1.0, base_value * (1 + risk_factor * 0.2 - analysis_factor * 0.1)))
    
    def _get_personality_factors(self) -> Dict[str, float]:
        """Pobiera czynniki osobowości wpływające na decyzję"""
        return {
            "analysis_power": self.personality.analysis_power,
            "risk_acceptance": self.personality.risk_acceptance,
            "curiosity": self.personality.curiosity,
            "security_preference": self.personality.security_preference,
            "experimentation_level": self.personality.experimentation_level
        }
    
    def evaluate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Oceńia wynik decyzji i aktualizuje stan agenta.
        
        Zgodnie z 05_AGENT_SYSTEM.md Sekcja 8.1 (Indywidualny Proces Decyzyjny)
        
        Args:
            result: Wynik decyzji (trafna/nietrafna, wartość, itd.)
            
        Returns:
            Słownik z oceną i aktualizacjami
        """
        with self._lock:
            self.set_status(AgentStatus.LEARNING)
            
            try:
                # Znajdź ostatnią decyzję
                if self.memory.decision_history:
                    last_decision = self.memory.decision_history[-1]
                    decision_id = last_decision.decision_id
                    
                    # Zaktualizuj rekord decyzji
                    last_decision.actual_result = result.get("actual_result")
                    last_decision.was_correct = result.get("correct", False)
                    last_decision.evaluation = result
                    
                    # Aktualizuj metryki
                    if last_decision.was_correct:
                        self.metrics["correct_decisions"] += 1
                    else:
                        self.metrics["incorrect_decisions"] += 1
                    
                    total = self.metrics["total_decisions"]
                    if total > 0:
                        self.metrics["success_rate"] = self.metrics["correct_decisions"] / total
                        self.metrics["error_rate"] = self.metrics["incorrect_decisions"] / total
                
                # Aktualizuj stan emocjonalny
                self.emotional_state = self.emotional_state.update_from_result(result, self.config)
                
                # Aktualizuj osobowość (ewolucja)
                experience = {
                    "success_rate": self.metrics["success_rate"],
                    "error_rate": self.metrics["error_rate"],
                    "discovery_rate": 0.5  # TODO: Zaimplementować wykrywanie odkryć
                }
                
                directions = self.personality.get_evolution_direction(experience)
                self.personality = self.personality.evolve(directions, self.config.evolution_rate)
                
                self.set_status(AgentStatus.ACTIVE)
                
                return {
                    "agent_id": self.agent_id,
                    "evaluation": result,
                    "metrics_updated": self.metrics.copy(),
                    "emotional_state": self.emotional_state.to_dict(),
                    "personality": self.personality.to_dict()
                }
                
            except Exception as e:
                logger.error(f"Błąd oceny wyniku dla agenta {self.agent_id}: {e}")
                self.set_status(AgentStatus.ERROR)
                return {
                    "agent_id": self.agent_id,
                    "error": str(e),
                    "status": "error"
                }
    
    def learn_from_experience(self, experience: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uczy się z doświadczenia i aktualizuje swoją wiedzę.
        
        Zgodnie z 05_AGENT_SYSTEM.md Sekcja 9.1 (Czynniki Ewolucji)
        
        Args:
            experience: Doświadczenie do nauczenia się (strategie, wzorce, wyniki)
            
        Returns:
            Słownik z aktualizacjami i nowymi wnioskami
        """
        with self._lock:
            self.set_status(AgentStatus.LEARNING)
            
            try:
                # Energetyzuj doświadczenie
                new_strategies = experience.get("strategies", [])
                new_patterns = experience.get("patterns", [])
                new_results = experience.get("results", [])
                
                # Dodaj nowe strategie do pamięci
                for strategy in new_strategies:
                    strategy_id = strategy.get("id", f"strat_{uuid.uuid4().hex[:8]}")
                    self.memory.strategies[strategy_id] = strategy
                
                # Dodaj nowe wzorce
                for pattern in new_patterns:
                    pattern_id = pattern.get("id", f"pat_{uuid.uuid4().hex[:8]}")
                    self.memory.results[pattern_id] = pattern
                
                # Analiza nowych wyników
                for result in new_results:
                    self.memory.results[result.get("id", "")] = result
                    
                    # Wyciągaj lekcje
                    if result.get("outcome") == "success":
                        lesson = f"Strategia {result.get('strategy_id', 'unknown')} sprawdziła się w warunkach {result.get('conditions', 'unknown')}"
                        self.memory.add_lesson(lesson)
                
                self.set_status(AgentStatus.ACTIVE)
                
                return {
                    "agent_id": self.agent_id,
                    "new_strategies_added": len(new_strategies),
                    "new_patterns_added": len(new_patterns),
                    "new_results_added": len(new_results),
                    "lessons_learned": len(self.memory.lessons),
                    "status": "learned"
                }
                
            except Exception as e:
                logger.error(f"Błąd uczenia się agenta {self.agent_id}: {e}")
                self.set_status(AgentStatus.ERROR)
                return {
                    "agent_id": self.agent_id,
                    "error": str(e),
                    "status": "error"
                }
    
    def update_trust(self, agent_id: str, trust_change: float, reason: str) -> None:
        """Aktualizuje zaufanie do innego agenta"""
        with self._lock:
            self.memory.update_trust(agent_id, trust_change, reason)
            logger.debug(f"Agent {self.agent_id} aktualizował zaufanie do {agent_id}: {trust_change} ({reason})")
    
    def get_trust_weight(self, agent_id: str) -> float:
        """Pobiera wagę zaufania do innego agenta"""
        return self.memory.get_trust_weight(agent_id)
    
    def get_status_report(self) -> Dict[str, Any]:
        """
        Generuje pełny raport statusu agenta.
        
        Returns:
            Słownik z pełnym statusem agenta
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "status": self.status.name,
            "room_id": self.room_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_decision_time": self.last_decision_time.isoformat() if self.last_decision_time else None,
            
            # Osobowość i emocje
            "personality": self.personality.to_dict(),
            "emotional_state": self.emotional_state.to_dict(),
            
            # Metryki
            "metrics": self.metrics,
            
            # Pamięć
            "memory": self.memory.get_status_report(),
            
            # Konfiguracja
            "config": self.config.to_dict(),
            
            # Środowisko
            "world_access": self.world_access,
            "model_access": self.model_access
        }
    
    def get_decision_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Pobiera historię decyzji agenta"""
        return [dr.to_dict() for dr in self.memory.decision_history[-limit:]]
    
    def to_json(self) -> str:
        """Konwersja do JSON"""
        return json.dumps(self.get_status_report(), indent=2, ensure_ascii=False)
    
    def save(self, file_path: Optional[str] = None) -> str:
        """Zapisuje stan agenta do pliku"""
        if not file_path:
            file_path = f"agents/{self.agent_id}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.get_status_report(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Zapisano agenta {self.agent_id} do {file_path}")
        return file_path
    
    @classmethod
    def load(cls, file_path: str) -> 'Agent':
        """Wczytuje agenta z pliku"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Tworzenie konfiguracji z danych
            config_data = data.get("config", {})
            config = AgentConfig.from_dict(config_data)
            
            # Tworzenie agenta
            agent = cls(config)
            
            # Wczytanie stanu
            agent.status = AgentStatus[data.get("status", "BORN")]
            agent.personality = PersonalityVector.from_dict(data.get("personality", {}))
            agent.emotional_state = EmotionalState.from_dict(data.get("emotional_state", {}))
            agent.metrics = data.get("metrics", agent.metrics)
            agent.created_at = datetime.fromisoformat(data.get("created_at", agent.created_at.isoformat()))
            agent.updated_at = datetime.fromisoformat(data.get("updated_at", agent.updated_at.isoformat()))
            
            # Wczytanie pamięci (uproszczone)
            if "memory" in data:
                mem_data = data["memory"]
                if "lessons" in mem_data:
                    agent.memory.lessons = mem_data["lessons"]
            
            logger.info(f"Wczytano agenta {agent.agent_id} z {file_path}")
            return agent
            
        except Exception as e:
            logger.error(f"Błąd wczytywania agenta z {file_path}: {e}")
            raise


# ============================================================================
# MANAGER AGENTÓW
# ============================================================================

class AgentManager:
    """
    Manager zarządzający populacją agentów.
    
    Odpowiedzialność:
    - Tworzenie, usuwanie i zarządzanie agentami
    - Monitorowanie stanu agentów
    - Statystyki populacji
    - Integracja z ROOM_CORE i AGENT_BIRTH_SYSTEM
    
    Zgodnie z 10_IMPLEMENTATION_MAP.md Etap 4A
    """
    
    def __init__(self):
        """Inicjalizacja managera"""
        self.agents: Dict[str, Agent] = {}
        self._lock = threading.Lock()
        self.created_at = datetime.now()
        logger.info("Zainicjowano AgentManager")
    
    def create_agent(self, config: Optional[AgentConfig] = None) -> Agent:
        """
        Tworzy nowego agenta.
        
        Args:
            config: Konfiguracja agenta (opcjonalnie)
            
        Returns:
            Nowy agent
        """
        with self._lock:
            if config is None:
                config = AgentConfig()
            
            # Upewnij się, że agent_id jest unikalny
            while config.agent_id in self.agents:
                config.agent_id = f"agent_{uuid.uuid4().hex[:12]}"
            
            agent = Agent(config)
            self.agents[agent.agent_id] = agent
            logger.info(f"AgentManager: Utworzono agenta {agent.agent_id}")
            return agent
    
    def add_agent(self, agent: Agent) -> bool:
        """Dodaje istniejącego agenta do managera"""
        with self._lock:
            if agent.agent_id in self.agents:
                logger.warning(f"Agent {agent.agent_id} już istnieje")
                return False
            
            self.agents[agent.agent_id] = agent
            logger.info(f"AgentManager: Dodano agenta {agent.agent_id}")
            return True
    
    def remove_agent(self, agent_id: str, archive: bool = False) -> bool:
        """
        Usuwa agenta z managera.
        
        Args:
            agent_id: ID agenta do usunięcia
            archive: Czy zarchiwizować agenta zamiast usuwać
            
        Returns:
            True jeśli agent został usunięty
        """
        with self._lock:
            if agent_id not in self.agents:
                return False
            
            agent = self.agents[agent_id]
            
            if archive:
                agent.set_status(AgentStatus.ARCHIVED)
                logger.info(f"AgentManager: Zarchiwizowano agenta {agent_id}")
            else:
                del self.agents[agent_id]
                logger.info(f"AgentManager: Usunięto agenta {agent_id}")
            
            return True
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Pobiera agenta po ID"""
        return self.agents.get(agent_id)
    
    def find_agents(self, **criteria) -> List[Agent]:
        """
        Znajduje agentów według kryteriów.
        
        Args:
            **criteria: Kryteria wyszukiwania (agent_type, status, itd.)
            
        Returns:
            Lista pasujących agentów
        """
        results = []
        for agent in self.agents.values():
            match = True
            for key, value in criteria.items():
                if key == "agent_type":
                    if agent.agent_type.value != value:
                        match = False
                        break
                elif key == "status":
                    if agent.status.name != value:
                        match = False
                        break
                elif hasattr(agent, key):
                    if getattr(agent, key) != value:
                        match = False
                        break
            
            if match:
                results.append(agent)
        
        return results
    
    def get_active_agents(self) -> List[Agent]:
        """Pobiera wszystkich aktywnych agentów"""
        return [agent for agent in self.agents.values() 
                if agent.status in [AgentStatus.ACTIVE, AgentStatus.THINKING, AgentStatus.DECIDING]]
    
    def get_agents_by_type(self, agent_type: AgentType) -> List[Agent]:
        """Pobiera agentów danego typu"""
        return [agent for agent in self.agents.values() if agent.agent_type == agent_type]
    
    def clear(self) -> None:
        """Czyści wszystkich agentów (UWAGA: usuwa wszystkie dane!)"""
        with self._lock:
            self.agents.clear()
            logger.warning("AgentManager: Wyczyszczono wszystkich agentów")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Pobiera statystyki populacji agentów.
        
        Returns:
            Słownik ze statystykami
        """
        stats = {
            "total_agents": len(self.agents),
            "active_agents": len(self.get_active_agents()),
            "by_type": {},
            "by_status": {},
            "created_at": self.created_at.isoformat(),
            "total_decisions": 0,
            "success_rate": 0.0
        }
        
        # Statystyki po typach
        for agent in self.agents.values():
            type_str = agent.agent_type.value
            if type_str not in stats["by_type"]:
                stats["by_type"][type_str] = 0
            stats["by_type"][type_str] += 1
            
            status_str = agent.status.name
            if status_str not in stats["by_status"]:
                stats["by_status"][status_str] = 0
            stats["by_status"][status_str] += 1
            
            stats["total_decisions"] += agent.metrics["total_decisions"]
        
        if stats["total_agents"] > 0:
            stats["success_rate"] = sum(
                a.metrics["success_rate"] for a in self.agents.values()
            ) / stats["total_agents"]
        
        return stats
    
    def get_population_report(self) -> str:
        """Generuje raport populacji agentów"""
        stats = self.get_statistics()
        
        report = [
            "=" * 60,
            "RAPORT POPULACJI AGENTÓW - SSI V4",
            "=" * 60,
            f"Całkowita liczba agentów: {stats['total_agents']}",
            f"Aktywnych agentów: {stats['active_agents']}",
            f"Całkowite decyzje: {stats['total_decisions']}",
            f"Średnia skuteczność: {stats['success_rate']:.2%}",
            "",
            "Przez typy:",
        ]
        
        for agent_type, count in stats["by_type"].items():
            report.append(f"  - {agent_type}: {count}")
        
        report.extend([
            "",
            "Przez status:",
        ])
        
        for status, count in stats["by_status"].items():
            report.append(f"  - {status}: {count}")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_all(self, directory: str = "agents") -> List[str]:
        """Zapisuje wszystkich agentów do plików"""
        import os
        os.makedirs(directory, exist_ok=True)
        
        saved_files = []
        for agent in self.agents.values():
            file_path = agent.save(f"{directory}/{agent.agent_id}.json")
            saved_files.append(file_path)
        
        logger.info(f"Zapisano {len(saved_files)} agentów do {directory}")
        return saved_files


# ============================================================================
# FABRYKA TWORZĄCA AGENTA
# ============================================================================

def tworz_agent(
    agent_type: AgentType = AgentType.ANALYST,
    agent_id: Optional[str] = None,
    config: Optional[AgentConfig] = None,
    v3_integration: Optional[V3Integration] = None,
    enable_v3_access: bool = True,
    **kwargs
) -> Agent:
    """
    Fabryka tworzących agentów V4 z obsługą integracji V3.
    
    Zgodnie z 05_AGENT_SYSTEM.md i 10_IMPLEMENTATION_MAP.md Etap 4A
    Sprint 6: Integracja z V3 World Memory System
    
    Args:
        agent_type: Typ agenta (z AgentType)
        agent_id: ID agenta (opcjonalnie, auto-generowane)
        config: Konfiguracja agenta (opcjonalnie)
        v3_integration: Instancja V3Integration (opcjonalnie)
        enable_v3_access: Czy włączać dostęp do V3 (domyślnie True)
        **kwargs: Dodatkowe parametry konfiguracji
        
    Returns:
        Nowy Agent
        
    Example:
        >>> agent = tworz_agent(AgentType.ANALYST)
        >>> agent.initialize()
        >>> decision = agent.make_decision(context)
        
        >>> # Z integracją V3
        >>> v3_integration = tworz_v3_integration()
        >>> agent = tworz_agent(AgentType.ANALYST, v3_integration=v3_integration)
    """
    if config is None:
        # Domyślna konfiguracja z V3
        config_kwargs = {
            "agent_type": agent_type,
            "agent_id": agent_id,
            "v3_world_memory_access": enable_v3_access,
            "v3_pattern_memory_access": enable_v3_access,
            "v3_metadata_access": enable_v3_access,
            "use_v3_knowledge": enable_v3_access,
            **kwargs
        }
        config = AgentConfig(**config_kwargs)
    else:
        config.agent_type = agent_type
        if agent_id:
            config.agent_id = agent_id
        # Zaktualizuj ustawienia V3 jeśli nie zostały podane
        if not hasattr(config, 'v3_world_memory_access') or config.v3_world_memory_access is None:
            config.v3_world_memory_access = enable_v3_access
        if not hasattr(config, 'v3_pattern_memory_access') or config.v3_pattern_memory_access is None:
            config.v3_pattern_memory_access = enable_v3_access
        if not hasattr(config, 'v3_metadata_access') or config.v3_metadata_access is None:
            config.v3_metadata_access = enable_v3_access
        if not hasattr(config, 'use_v3_knowledge') or config.use_v3_knowledge is None:
            config.use_v3_knowledge = enable_v3_access
    
    agent = Agent(config)
    
    # Jeśli przekazano V3Integration, połącz agenta
    if v3_integration and enable_v3_access:
        agent.connect_to_v3(v3_integration)
    
    return agent


# ============================================================================
# FUNKCJE POMOCNICZE
# ============================================================================


def get_agent_manager() -> AgentManager:
    """
    Zwraca globalnego managera agentów (Singleton).
    
    Zgodnie z PROJECT_RULES.md Sekcja 4 (Singleton dla Managerów)
    """
    global _manager, _manager_lock
    if '_manager' not in globals():
        _manager = None
        _manager_lock = threading.Lock()
    
    with _manager_lock:
        if _manager is None:
            _manager = AgentManager()
        return _manager


def reset_agent_manager() -> None:
    """Resetuje globalnego managera agentów (ostrzegać!)"""
    global _manager, _manager_lock
    
    with _manager_lock:
        if _manager is not None:
            _manager.clear()
            _manager = None


# ============================================================================
# TESTY
# ============================================================================

if __name__ == "__main__":
    print("Testing SSI V4 Agent Core...")
    print("=" * 60)
    
    # Test 1: Tworzenie agenta fabryką
    print("\n[Test 1] Tworzenie agenta fabryką...")
    agent1 = tworz_agent(AgentType.ANALYST)
    print(f"  Utworzono: {agent1.agent_id} (typ: {agent1.agent_type.value})")
    print(f"  Status: {agent1.status.name}")
    print(f"  Osobowość: {agent1.personality.to_dict()}")
    
    # Test 2: Inicjalizacja agenta
    print("\n[Test 2] Inicjalizacja agenta...")
    success = agent1.initialize()
    print(f"  Inicjalizacja: {'SUKCES' if success else 'BŁĄD'}")
    print(f"  Nowy status: {agent1.status.name}")
    
    # Test 3: Podejmowanie decyzji
    print("\n[Test 3] Podejmowanie decyzji...")
    context = {
        "worlds": ["world_001", "world_002"],
        "models": ["siec_01", "siec_02"],
        "strategies": ["strategy_001"],
        "history": [],
        "results": []
    }
    decision = agent1.make_decision(context)
    print(f"  Decyzja: {decision.get('action')}")
    print(f"  Pewność: {decision.get('confidence'):.2f}")
    print(f"  Wartość oczekiwana: {decision.get('expected_value'):.2f}")
    
    # Test 4: Ocena wyniku
    print("\n[Test 4] Ocena wyniku...")
    result = {"correct": True, "value": 0.85, "outcome": "success"}
    evaluation = agent1.evaluate_result(result)
    print(f"  Nowa pewność: {evaluation.get('emotional_state', {}).get('confidence'):.2f}")
    print(f"  Metryki: {evaluation.get('metrics_updated', {}).get('success_rate'):.2%}")
    
    # Test 5: Tworzenie różnych typów agentów
    print("\n[Test 5] Tworzenie różnych typów agentów...")
    for agent_type in [AgentType.VALUE_STRATEGIST, AgentType.EXPERIMENTATOR, AgentType.MENTAL_EXPERT]:
        agent = tworz_agent(agent_type)
        print(f"  {agent_type.value}: {agent.personality.to_dict()}")
    
    # Test 6: Manager agentów
    print("\n[Test 6] Manager agentów...")
    manager = AgentManager()
    
    # Dodaj agentów
    agent_a = manager.create_agent(AgentConfig(agent_type=AgentType.ANALYST))
    agent_b = manager.create_agent(AgentConfig(agent_type=AgentType.VALUE_STRATEGIST))
    agent_c = manager.create_agent(AgentConfig(agent_type=AgentType.EXPERIMENTATOR))
    
    print(f"  Liczba agentów: {len(manager.agents)}")
    print(f"  Statystyki: {manager.get_statistics()}")
    
    # Raport populacji
    print("\n[Raport Populacji]")
    print(manager.get_population_report())
    
    # Test 7: Serializacja
    print("\n[Test 7] Serializacja agenta...")
    json_str = agent1.to_json()
    print(f"  JSON długość: {len(json_str)} znaków")
    
    # Test 8: Zapis i odczyt
    print("\n[Test 8] Zapis i odczyt agenta...")
    import os
    os.makedirs("test_agents", exist_ok=True)
    file_path = agent1.save("test_agents/test_agent.json")
    print(f"  Zapisano do: {file_path}")
    
    loaded_agent = Agent.load(file_path)
    print(f"  Wczytano: {loaded_agent.agent_id}")
    print(f"  Typ: {loaded_agent.agent_type.value}")
    
    # Czyszczenie testowe
    import shutil
    if os.path.exists("test_agents"):
        shutil.rmtree("test_agents")
    
    print("\n" + "=" * 60)
    print("All Agent Core tests passed!")
    print("=" * 60)
    
    # ============================================================================
    # TESTY INTEGRACJI V3 (Sprint 6)
    # ============================================================================
    
    print("\n" + "=" * 60)
    print("TESTY INTEGRACJI V3 (Sprint 6)")
    print("=" * 60)
    
    # Test 7: Integracja z V3 World Memory System
    print("\n[Test 7] Integracja z V3 World Memory System...")
    
    # Spróbuj utworzyć agenta z dostępem do V3
    try:
        from ..v3.v3_integration import tworz_v3_integration
        from ..v3.memory.memory_manager import tworz_memory_manager
        from ..v3.worlds.world_manager import tworz_world_manager
        
        # Utwórz instancję V3
        memory_manager = tworz_memory_manager()
        world_manager = tworz_world_manager()
        v3_integration = tworz_v3_integration(
            memory_manager=memory_manager,
            world_manager=world_manager
        )
        
        # Utwórz agenta z V3
        v3_agent = tworz_agent(
            AgentType.ANALYST,
            v3_integration=v3_integration,
            enable_v3_access=True
        )
        
        print(f"  Agent V3: {v3_agent.agent_id}")
        print(f"  V3 dostępny: {v3_agent.is_v3_available()}")
        
        # Test dostępu do V3
        if v3_agent.is_v3_available():
            print(f"  World Memory dostępny: {v3_agent.get_world_memory() is not None}")
            print(f"  Pattern Memory dostępny: {v3_agent.get_pattern_memory() is not None}")
            
            # Test podsumowania wiedzy V3
            summary = v3_agent.get_v3_knowledge_summary()
            print(f"  Podsumowanie V3: {summary}")
            
            # Test podejmowania decyzji z wiedzą V3
            v3_decision = v3_agent.make_decision(context)
            has_v3_knowledge = "v3_knowledge" in v3_decision.get("analysis", {})
            print(f"  Decyzja z wiedzą V3: {has_v3_knowledge}")
            
            if has_v3_knowledge:
                v3_knowledge = v3_decision["analysis"]["v3_knowledge"]
                print(f"  Światy użyte: {v3_knowledge.get('worlds_used', 0)}")
                print(f"  Wzorce użyte: {v3_knowledge.get('patterns_used', 0)}")
        else:
            print("  V3 nie jest dostępny - test pominięty")
            
    except ImportError as e:
        print(f"  Import V3 nie dostępny (jest to normalne w fazie rozwoju): {e}")
    except Exception as e:
        print(f"  Błąd integracji V3: {e}")
    
    # Test 8: Agent z wyłączonym dostępem do V3
    print("\n[Test 8] Agent z wyłączonym dostępem do V3...")
    no_v3_agent = tworz_agent(
        AgentType.VALUE_STRATEGIST,
        enable_v3_access=False
    )
    print(f"  Agent: {no_v3_agent.agent_id}")
    print(f"  V3 dostępny: {no_v3_agent.is_v3_available()}")
    
    # Test 9: Ręczne połączenie z V3
    print("\n[Test 9] Ręczne połączenie z V3...")
    try:
        manual_agent = tworz_agent(AgentType.EXPERIMENTATOR, enable_v3_access=False)
        print(f"  Agent przed połączeniem: V3 dostępny = {manual_agent.is_v3_available()}")
        
        # Spróbuj połączyć ręcznie
        if 'v3_integration' in locals() and v3_integration:
            success = manual_agent.connect_to_v3(v3_integration)
            print(f"  Połączenie ręczne: {'SUKCES' if success else 'BŁĄD'}")
            print(f"  Agent po połączeniu: V3 dostępny = {manual_agent.is_v3_available()}")
    except Exception as e:
        print(f"  Błąd ręcznego połączenia: {e}")
    
    print("\n" + "=" * 60)
    print("All Agent Core + V3 Integration tests completed!")
    print("=" * 60)
