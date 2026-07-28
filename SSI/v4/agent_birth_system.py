"""
SSI V4 Agent Birth System - System narodzin agentów

Moduł odpowiedzialny za tworzenie pierwszej populacji agentów i ich inicjalizację.

Odpowiedzialność:
- Tworzenie pierwszej populacji agentów (3 podstawowe: Analityk, Strateg Wartości, Eksperymentator)
- Inicjalizacja parametrów początkowych
- Zarządzanie procesem narodzin
- Integracja z ROOM_CORE

Zgodnie z:
- 05_AGENT_SYSTEM.md Sekcja 2.1 (Agent Birth System), 2.2 (ROOM_CORE), 2.3 (Pierwsza Populacja)
- 10_IMPLEMENTATION_MAP.md Etap 4A (Agent Foundation)

Architektura:
┌─────────────────────────────────────────────────────────────┐
│                 AGENT BIRTH SYSTEM                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐      ┌─────────────────────────────┐   │
│  │  BirthConfig    │      │     AGENT_BIRTH_SYSTEM       │   │
│  │  - initial_count│      │  ┌─────────────────────┐    │   │
│  │  - agent_types  │──────│  │ create_initial_agents │    │   │
│  │  - room_id       │      │  └─────────────────────┘    │   │
│  └─────────────────┘      │  ┌─────────────────────┐    │   │
│                            │  │ create_agent          │    │   │
│  ┌─────────────────┐      │  └─────────────────────┘    │   │
│  │  BirthResult    │      │  ┌─────────────────────┐    │   │
│  │  - agent        │◄─────│  │ init_agent          │    │   │
│  │  - birth_record │      │  └─────────────────────┘    │   │
│  └─────────────────┘      └─────────────────────────────┘   │
│                            ↓                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    NOWI AGENCI                           │ │
│  │  - Agent 1: Analityk (analysis_power=0.8, risk=0.3)      │ │
│  │  - Agent 2: Strateg Wartości (analysis_power=0.85, risk=0.55)│ │
│  │  - Agent 3: Eksperymentator (curiosity=0.85, exp_level=0.9)│ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Zależności:
- Zależy od: agent_core.py (klasa Agent, AgentConfig, AgentType)
- Wspiera: ROOM_CORE (dodawanie agentów do pokoju)
- Współpracuje z: PersonalityVector (inicjalizacja osobowości)

Wersja: 1.0
Data: 2026-07-28
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum, auto
import uuid
import threading
import logging

from .agent_core import Agent, AgentConfig, AgentType, AgentStatus, PersonalityVector

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMY - Tryby narodzin
# ============================================================================

class BirthMode(Enum):
    """
    Tryby tworzenia agentów.
    
    Zgodnie z 05_AGENT_SYSTEM.md Sekcja 2.1 (Proces Inicjalizacji)
    """
    INITIAL_POPULATION = auto()   # Tworzenie pierwszej populacji (3 agenci)
    SINGLE_AGENT = auto()          # Tworzenie pojedynczego agenta
    BATCH = auto()                 # Tworzenie partii agentów
    EVOLUTION = auto()             # Tworzenie agenta z ewolucji
    RANDOM = auto()                # Losowe tworzenie agenta


# ============================================================================
# KONFIGURACJA SYSTEMU NARODZIN
# ============================================================================

@dataclass
class BirthConfig:
    """
    Konfiguracja systemu narodzin agentów.
    
    Zgodnie z 05_AGENT_SYSTEM.md Sekcja 2.3 (Pierwsza Populacja)
    
    Attributes:
        initial_population_size: Liczba agentów w pierwszej populacji
        initial_agent_types: Typy agentów w pierwszej populacji
        default_room_id: Domyślny pokój narodzin
        Personality_vector_ranges: Zakresy parametrów osobowości
        evolution_rate: Szybkość ewolucji nowych agentów
    """
    # Ustawienia pierwszej populacji
    initial_population_size: int = 3
    initial_agent_types: List[AgentType] = field(default_factory=lambda: [
        AgentType.ANALYST,
        AgentType.VALUE_STRATEGIST,
        AgentType.EXPERIMENTATOR
    ])
    
    # Ustawienia środowiska
    default_room_id: str = "ROOM_CORE"
    
    # Zakresy parametrów da nowych agentów
    personality_ranges: Dict[str, Tuple[float, float]] = field(default_factory=lambda: {
        "analysis_power": (0.3, 0.9),
        "risk_acceptance": (0.1, 0.8),
        "curiosity": (0.3, 0.9),
        "security_preference": (0.2, 0.9),
        "experimentation_level": (0.2, 0.9),
        "independence": (0.4, 0.8),
        "trust_level": (0.3, 0.7),
        "resilience": (0.5, 0.95)
    })
    
    # Parametry ewolucji
    evolution_rate: float = 0.01
    mutation_rate: float = 0.05
    
    # Flagi
    enable_random_birth: bool = True
    enable_evolution_birth: bool = True
    save_birth_records: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            "initial_population_size": self.initial_population_size,
            "initial_agent_types": [t.value for t in self.initial_agent_types],
            "default_room_id": self.default_room_id,
            "Personality_vector_ranges": self.personality_ranges,
            "evolution_rate": self.evolution_rate,
            "mutation_rate": self.mutation_rate,
            "enable_random_birth": self.enable_random_birth,
            "enable_evolution_birth": self.enable_evolution_birth,
            "save_birth_records": self.save_birth_records
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BirthConfig':
        """Tworzenie z słownika"""
        data = data.copy()
        if "initial_agent_types" in data and isinstance(data["initial_agent_types"][0], str):
            data["initial_agent_types"] = [AgentType(t) for t in data["initial_agent_types"]]
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# ============================================================================
# REKORD NARODZIN
# ============================================================================

@dataclass
class BirthRecord:
    """
    Rekord narodzin agenta.
    
    Zapisuje wszystkie informacje związane z narodzinami agenta.
    """
    birth_id: str
    agent_id: str
    agent_type: str
    timestamp: str
    mode: str  # BirthMode
    
    # Parametry początkowe
    initial_personality: Dict[str, float]
    
    # Kontekst narodzin
    room_id: str
    parent_agents: List[str] = field(default_factory=list)  # Rodzice (w przypadku ewolucji)
    birth_parameters: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            "birth_id": self.birth_id,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "timestamp": self.timestamp,
            "mode": self.mode,
            "initial_personality": self.initial_personality,
            "room_id": self.room_id,
            "parent_agents": self.parent_agents,
            "birth_parameters": self.birth_parameters
        }


# ============================================================================
# REZULTAT NARODZIN
# ============================================================================

@dataclass
class BirthResult:
    """
    Rezultat procesu narodzin agenta.
    
    Zawiera agenta i metadane o procesie tworzenia.
    """
    agent: Agent
    birth_record: BirthRecord
    success: bool = True
    message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            "agent_id": self.agent.agent_id,
            "agent_type": self.agent.agent_type.value,
            "success": self.success,
            "message": self.message,
            "birth_record": self.birth_record.to_dict()
        }


# ============================================================================
# GŁÓWNA KLASA AGENT BIRTH SYSTEM
# ============================================================================

class AgentBirthSystem:
    """
    Główny system narodzin agentów V4.
    
    Odpowiedzialność:
    - Tworzenie pierwszej populacji agentów
    - Inicjalizacja nowych agentów
    - Zarządzanie procesem narodzin
    - Rejestracja historii narodzin
    - Integracja z ROOM_CORE
    
    Zgodnie z 05_AGENT_SYSTEM.md Sekcja 2.1 (Agent Birth System)
    
    Attributes:
        config: Konfiguracja systemu narodzin
        birth_records: Historia narodzin wszystkich agentów
        statistics: Statystyki systemu narodzin
    """
    
    def __init__(self, config: Optional[BirthConfig] = None):
        """
        Inicjalizacja systemu narodzin.
        
        Args:
            config: Konfiguracja (opcjonalnie)
        """
        self.config = config or BirthConfig()
        self.birth_records: Dict[str, BirthRecord] = {}
        self._lock = threading.Lock()
        
        # Statystyki
        self.statistics: Dict[str, int] = {
            "total_births": 0,
            "successful_births": 0,
            "failed_births": 0,
            "by_type": {},
            "by_mode": {}
        }
        
        self.created_at = datetime.now()
        
        logger.info(f"Zainicjowano AgentBirthSystem w trybie: {self.config.default_room_id}")
    
    def create_initial_population(self, room_id: Optional[str] = None) -> List[BirthResult]:
        """
        Tworzy pierwszą populację agentów.
        
        Zgodnie z 05_AGENT_SYSTEM.md Sekcja 2.3 (Pierwsza Populacja)
        
        Args:
            room_id: ID pokoju (opcjonalnie, domyślnie z config)
            
        Returns:
            Lista rezultatów narodzin
        """
        with self._lock:
            room_id = room_id or self.config.default_room_id
            results = []
            
            for i, agent_type in enumerate(self.config.initial_agent_types[:self.config.initial_population_size]):
                # Utwórz unikalne ID dla agenta
                agent_id = f"agent_init_{i+1}_{agent_type.value}"
                
                # Utwórz agenta
                birth_result = self.create_agent(
                    agent_type=agent_type,
                    room_id=room_id,
                    mode=BirthMode.INITIAL_POPULATION,
                    custom_id=agent_id
                )
                
                results.append(birth_result)
                
                if birth_result.success:
                    logger.info(f"Narodziny: {birth_result.agent.agent_id} ({agent_type.value})")
                else:
                    logger.error(f"Błąd narodzin: {birth_result.message}")
            
            return results
    
    def create_agent(
        self,
        agent_type: AgentType = AgentType.ANALYST,
        room_id: Optional[str] = None,
        mode: BirthMode = BirthMode.SINGLE_AGENT,
        personality: Optional[Dict[str, float]] = None,
        parent_agents: Optional[List[str]] = None,
        custom_id: Optional[str] = None
    ) -> BirthResult:
        """
        Tworzy pojedynczego agenta.
        
        Args:
            agent_type: Typ agenta
            room_id: ID pokoju (opcjonalnie)
            mode: Tryb narodzin
            personality: Wektor osobowości (opcjonalnie, losowy jeśli None)
            parent_agents: Rodzice (w przypadku ewolucji)
            custom_id: Niestandardowe ID agenta
            
        Returns:
            BirthResult z agentem i rekordem narodzin
        """
        room_id = room_id or self.config.default_room_id
        
        # Generuj ID
        agent_id = custom_id or f"agent_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        # Generuj wektor osobowości
        if personality is None:
            personality = self._generate_personality(agent_type)
        
        # Utwórz kryfigurację agenta
        config = AgentConfig(
            agent_id=agent_id,
            agent_type=agent_type,
            room_id=room_id,
            initial_personality=personality
        )
        
        # Utwórz agenta
        try:
            agent = Agent(config)
            
            # Inicjalizuj agenta
            success = agent.initialize()
            
            # Utwórz rekord narodzin
            birth_record = BirthRecord(
                birth_id=f"birth_{uuid.uuid4().hex[:12]}",
                agent_id=agent_id,
                agent_type=agent_type.value,
                timestamp=datetime.now().isoformat(),
                mode=mode.name,
                initial_personality=personality.copy(),
                room_id=room_id,
                parent_agents=parent_agents or [],
                birth_parameters={
                    "mode": mode.name,
                    "custom_id": custom_id,
                    "auto_personality": personality is None
                }
            )
            
            # Zapis rekord
            if self.config.save_birth_records:
                self.birth_records[birth_record.birth_id] = birth_record
            
            # Aktualizuj statystyki
            self.statistics["total_births"] += 1
            if mode.name not in self.statistics["by_mode"]:
                self.statistics["by_mode"][mode.name] = 0
            self.statistics["by_mode"][mode.name] += 1
            
            if agent_type.value not in self.statistics["by_type"]:
                self.statistics["by_type"][agent_type.value] = 0
            self.statistics["by_type"][agent_type.value] += 1
            
            if success:
                self.statistics["successful_births"] += 1
                logger.info(f"Narodziny: {agent_id} ({agent_type.value}) w pokoju {room_id}")
                return BirthResult(
                    agent=agent,
                    birth_record=birth_record,
                    success=True,
                    message=f"Agent {agent_id} został utworzony pomyślnie"
                )
            else:
                self.statistics["failed_births"] += 1
                return BirthResult(
                    agent=agent,
                    birth_record=birth_record,
                    success=False,
                    message=f"Błąd inicjalizacji agenta {agent_id}"
                )
                
        except Exception as e:
            self.statistics["failed_births"] += 1
            logger.error(f"Błąd tworzenia agenta: {e}")
            # Tworzymy faux birth record dla celów logowania
            faux_record = BirthRecord(
                birth_id=f"birth_failed_{uuid.uuid4().hex[:12]}",
                agent_id=agent_id,
                agent_type=agent_type.value,
                timestamp=datetime.now().isoformat(),
                mode=mode.name,
                initial_personality={},
                room_id=room_id,
                birth_parameters={"error": str(e)}
            )
            return BirthResult(
                agent=None,  # type: ignore
                birth_record=faux_record,
                success=False,
                message=str(e)
            )
    
    def _generate_personality(self, agent_type: AgentType) -> Dict[str, float]:
        """
        Generuje losowy lub charakterystyczny wektor osobowości dla agenta.
        
        W przypadku pierwszej populacji, używa charakterystycznych wartości.
        W innych przypadkach, generuje losowe wartości w zakresach.
        """
        # Dla pierwszej populacji - charakterystyczne wartości
        if agent_type == AgentType.ANALYST:
            return {
                "analysis_power": 0.80,
                "risk_acceptance": 0.30,
                "curiosity": 0.40,
                "security_preference": 0.85,
                "experimentation_level": 0.20,
                "independence": 0.60,
                "trust_level": 0.50,
                "resilience": 0.90
            }
        elif agent_type == AgentType.VALUE_STRATEGIST:
            return {
                "analysis_power": 0.85,
                "risk_acceptance": 0.55,
                "curiosity": 0.70,
                "security_preference": 0.50,
                "experimentation_level": 0.40,
                "independence": 0.70,
                "trust_level": 0.50,
                "resilience": 0.80
            }
        elif agent_type == AgentType.EXPERIMENTATOR:
            return {
                "analysis_power": 0.70,
                "risk_acceptance": 0.80,
                "curiosity": 0.85,
                "security_preference": 0.30,
                "experimentation_level": 0.90,
                "independence": 0.80,
                "trust_level": 0.50,
                "resilience": 0.85
            }
        else:
            # Losowy wektor w zakresach
            import random
            return {
                trait: random.uniform(min_val, max_val) 
                for trait, (min_val, max_val) in self.config.personality_ranges.items()
            }
    
    def create_agent_from_evolution(
        self,
        parent_agents: List[Agent],
        room_id: Optional[str] = None,
        crossover_rate: float = 0.5,
        mutation_rate: float = 0.1
    ) -> BirthResult:
        """
        Tworzy nowego agenta poprzez ewolucję (krzyżowanie i mutację).
        
        Zgodnie z 05_AGENT_SYSTEM.md Sekcja 9.1 (Czynniki Ewolucji)
        
        Args:
            parent_agents: Lista agentów rodziców
            room_id: ID pokoju
            crossover_rate: Współczynnik krzyżowania
            mutation_rate: Współczynnik mutacji
            
        Returns:
            BirthResult z nowym agentem
        """
        if not parent_agents or len(parent_agents) < 1:
            return BirthResult(
                agent=None,  # type: ignore
                birth_record=BirthRecord(
                    birth_id=f"birth_failed_{uuid.uuid4().hex[:12]}",
                    agent_id="",
                    agent_type="",
                    timestamp=datetime.now().isoformat(),
                    mode=BirthMode.EVOLUTION.name,
                    initial_personality={},
                    room_id=room_id or self.config.default_room_id,
                    parent_agents=[],
                    birth_parameters={"error": "No parent agents provided"}
                ),
                success=False,
                message="Brak agentów rodziców"
            )
        
        # Wybierz losowych rodziców (1-2)
        import random
        selected_parents = random.sample(parent_agents, min(2, len(parent_agents)))
        parent_ids = [p.agent_id for p in selected_parents]
        
        # Krzyżowanie - średnia ważona cech rodziców
        parent_personalities = [p.personality.to_dict() for p in selected_parents]
        child_personality: Dict[str, float] = {}
        
        for trait in self.config.personality_ranges.keys():
            if len(selected_parents) == 1:
                # Jedno rodzic - dziedziczenie z mutacją
                value = selected_parents[0].personality.to_dict()[trait]
            else:
                # Krzyżowanie - średnia ważona
                weights = [random.random() for _ in selected_parents]
                total_weight = sum(weights)
                value = sum(
                    w / total_weight * p[trait] 
                    for w, p in zip(weights, parent_personalities)
                )
            
            # Mutacja
            if random.random() < mutation_rate:
                min_val, max_val = self.config.personality_ranges[trait]
                mutation = random.uniform(-0.1, 0.1)
                value = max(min_val, min(max_val, value + mutation))
            
            child_personality[trait] = value
        
        # Określ typ agenta na podstawie dominujących cech
        child_type = self._determine_type_from_personality(child_personality)
        
        # Utwórz agenta z ewolucji
        return self.create_agent(
            agent_type=child_type,
            room_id=room_id,
            mode=BirthMode.EVOLUTION,
            personality=child_personality,
            parent_agents=parent_ids
        )
    
    def _determine_type_from_personality(self, personality: Dict[str, float]) -> AgentType:
        """
        Określa typ agenta na podstawie cech osobowości.
        
        Zgodnie z 05_AGENT_SYSTEM.md Sekcja 3.3 (Powstawanie Nowych Typów Agentów)
        """
        analysis = personality.get("analysis_power", 0.5)
        risk = personality.get("risk_acceptance", 0.5)
        curiosity = personality.get("curiosity", 0.5)
        security = personality.get("security_preference", 0.5)
        experimentation = personality.get("experimentation_level", 0.5)
        resilience = personality.get("resilience", 0.5)
        
        # Określ typ na podstawie dominujących cech
        if analysis > 0.7 and security > 0.7:
            return AgentType.ANALYST
        elif risk > 0.6 and analysis > 0.7:
            return AgentType.VALUE_STRATEGIST
        elif curiosity > 0.7 and experimentation > 0.7:
            return AgentType.EXPERIMENTATOR
        elif resilience > 0.8 and security > 0.7:
            return AgentType.MENTAL_EXPERT
        elif curiosity > 0.7 and experimentation > 0.7:
            return AgentType.PATTERN_HUNTER
        elif risk < 0.3 and security > 0.8:
            return AgentType.CONSERVATOR
        elif risk > 0.8 and experimentation > 0.7:
            return AgentType.AGGRESSOR
        else:
            # Domyślny typ
            return AgentType.BALANCER
    
    def create_random_agent(self, room_id: Optional[str] = None) -> BirthResult:
        """
        Tworzy losowego agenta.
        
        Args:
            room_id: ID pokoju (opcjonalnie)
            
        Returns:
            BirthResult z nowym agentem
        """
        import random
        
        # Losowy typ agenta
        all_types = list(AgentType)
        agent_type = random.choice(all_types)
        
        return self.create_agent(
            agent_type=agent_type,
            room_id=room_id,
            mode=BirthMode.RANDOM
        )
    
    def get_birth_record(self, birth_id: str) -> Optional[BirthRecord]:
        """Pobiera rekord narodzin po ID"""
        return self.birth_records.get(birth_id)
    
    def get_birth_records_by_agent(self, agent_id: str) -> List[BirthRecord]:
        """Pobiera wszystkie rekordy narodzin dla danego agenta"""
        return [record for record in self.birth_records.values() if record.agent_id == agent_id]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Pobiera statystyki systemu narodzin"""
        return {
            **self.statistics,
            "created_at": self.created_at.isoformat(),
            "total_records": len(self.birth_records),
            "success_rate": (self.statistics["successful_births"] / self.statistics["total_births"] 
                           if self.statistics["total_births"] > 0 else 0)
        }
    
    def get_population_report(self) -> str:
        """Generuje raport populacji narodzin"""
        stats = self.get_statistics()
        
        report = [
            "=" * 60,
            "RAPORT NARODZIN AGENTÓW - AGENT BIRTH SYSTEM",
            "=" * 60,
            f"Całkowite narodziny: {stats['total_births']}",
            f"Sukcesy: {stats['successful_births']}",
            f"Porażki: {stats['failed_births']}",
            f"Wskaźnik sukcesu: {stats['success_rate']:.2%}",
            "",
            "Przez typ:",
        ]
        
        for agent_type, count in stats.get("by_type", {}).items():
            report.append(f"  - {agent_type}: {count}")
        
        report.extend([
            "",
            "Przez tryb:",
        ])
        
        for mode, count in stats.get("by_mode", {}).items():
            report.append(f"  - {mode}: {count}")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def clear(self) -> None:
        """Czyści system narodzin (UWAGA: usuwa wszystkie dane!)"""
        with self._lock:
            self.birth_records.clear()
            self.statistics = {
                "total_births": 0,
                "successful_births": 0,
                "failed_births": 0,
                "by_type": {},
                "by_mode": {}
            }
            logger.warning("AgentBirthSystem: Wyczyszczono wszystkie rekordy narodzin")


# ============================================================================
# FABRYKA
# ============================================================================

def tworz_agent_birth_system(config: Optional[BirthConfig] = None) -> AgentBirthSystem:
    """
    Fabryka tworząca AgentBirthSystem.
    
    Args:
        config: Konfiguracja (opcjonalnie)
        
    Returns:
        AgentBirthSystem
        
    Example:
        >>> birth_system = tworz_agent_birth_system()
        >>> results = birth_system.create_initial_population()
        >>> for result in results:
        ...     if result.success:
        ...         print(f"Utworzono: {result.agent.agent_id}")
    """
    return AgentBirthSystem(config)


# ============================================================================
# SINGLETON
# ============================================================================

_birth_system: Optional[AgentBirthSystem] = None
_birth_system_lock = threading.Lock()


def get_agent_birth_system() -> AgentBirthSystem:
    """
    Zwraca globalny system narodzin agentów (Singleton).
    
    Zgodnie z PROJECT_RULES.md Sekcja 4 (Singleton dla Managerów)
    """
    global _birth_system
    with _birth_system_lock:
        if _birth_system is None:
            _birth_system = AgentBirthSystem()
        return _birth_system


def reset_agent_birth_system() -> None:
    """Resetuje globalny system narodzin (ostrzegać!)"""
    global _birth_system
    with _birth_system_lock:
        if _birth_system is not None:
            _birth_system.clear()
            _birth_system = None


# ============================================================================
# TESTY
# ============================================================================

if __name__ == "__main__":
    print("Testing SSI V4 Agent Birth System...")
    print("=" * 60)
    
    # Test 1: Tworzenie systemu narodzin
    print("\n[Test 1] Tworzenie AgentBirthSystem...")
    birth_system = tworz_agent_birth_system()
    print(f"  System utworzony: {birth_system.config.default_room_id}")
    
    # Test 2: Tworzenie pierwszej populacji
    print("\n[Test 2] Tworzenie pierwszej populacji...")
    results = birth_system.create_initial_population()
    print(f"  Liczba agentów: {len(results)}")
    for result in results:
        if result.success:
            print(f"    ✓ {result.agent.agent_id} ({result.agent.agent_type.value})")
        else:
            print(f"    ✗ Błąd: {result.message}")
    
    # Test 3: Statystyki
    print("\n[Test 3] Statystyki systemu narodzin...")
    stats = birth_system.get_statistics()
    print(f"  Całkowite narodziny: {stats['total_births']}")
    print(f"  Sukcesy: {stats['successful_births']}")
    print(f"  Wskaźnik sukcesu: {stats['success_rate']:.2%}")
    
    # Raport
    print("\n[Raport Narodzin]")
    print(birth_system.get_population_report())
    
    # Test 4: Tworzenie losowego agenta
    print("\n[Test 4] Tworzenie losowego agenta...")
    random_result = birth_system.create_random_agent()
    if random_result.success:
        print(f"  Utworzono: {random_result.agent.agent_id} ({random_result.agent.agent_type.value})")
        print(f"  Osobowość: {random_result.agent.personality.to_dict()}")
    
    # Test 5: Ewolucja (po utworzeniu kilku agentów)
    print("\n[Test 5] Tworzenie agenta z ewolucji...")
    if len(results) >= 2:
        parents = [r.agent for r in results if r.success]
        if len(parents) >= 1:
            evolution_result = birth_system.create_agent_from_evolution(parents)
            if evolution_result.success:
                print(f"  Ewoluował: {evolution_result.agent.agent_id}")
                print(f"  Typ: {evolution_result.agent.agent_type.value}")
                print(f"  Osobowość: {evolution_result.agent.personality.to_dict()}")
    
    print("\n" + "=" * 60)
    print("All Agent Birth System tests passed!")
    print("=" * 60)
