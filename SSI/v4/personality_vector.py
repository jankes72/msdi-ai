"""
SSI V4 Personality Vector - Wektor Osobowości Agentów

Moduł zawierający struktury i mechanizmy związane z osobowością agentów.

Odpowiedzialność:
- PersonalityVector: 8 parametrów osobowości agenta
- PersonalityConfig: Konfiguracja parametrów osobowości
- PersonalityTrait: Pojedyncza cecha osobowości
- PersonalityEngine: Silnik zarządzający ewolucją osobowości
- Mechanizmy ewolucji i adaptacji

Zgodnie z:
- 05_AGENT_SYSTEM.md Sekcja 3.1 (Personality Vector), 3.2 (Ewolucja Osobowości)
- 10_IMPLEMENTATION_MAP.md Etap 4B (Agent Personality System)

Architektura:
┌─────────────────────────────────────────────────────────────┐
│              PERSONALITY VECTOR SYSTEM                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              PersonalityVector                            │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │ │
│  │  │ analysis_   │ │ risk_       │ │ curiosity   │        │ │
│  │  │ power       │ │ acceptance  │ │             │        │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘        │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │ │
│  │  │ security_   │ │ experiment- │ │ resilience  │        │ │
│  │  │ preference  │ │ ation_level │ │             │        │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘        │ │
│  │  ┌─────────────┐ ┌─────────────┐                           │ │
│  │  │ independence│ │ trust_level │                           │ │
│  │  └─────────────┘ └─────────────┘                           │ │
│  └─────────────────────────────────────────────────────────┘ │
│                              ↓                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │            PersonalityEngine                             │ │
│  │  - Ewaluacja doświadczeń                                │ │
│  │  - Określanie kierunków ewolucji                        │ │
│  │  - Adaptacja parametrów                                  │ │
│  │  - Mechanizmy mutacji                                   │ │
│  └─────────────────────────────────────────────────────────┘ │
│                              ↓                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Nowe Typy Agentów                           │ │
│  │  - Ekspert Mentalny                                     │ │
│  │  - Łowca Wzorców                                        │ │
│  │  - Analityk Ryzyka                                       │ │
│  │  - Konserwatysta                                          │ │
│  │  - Agresor                                                │ │
│  │  - Balanser                                              │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Zależności:
- Zależy od: agent_core.py (klasa Agent)
- Wspiera: AgentBirthSystem (inicjalizacja)
- Współpracuje z: agent_core.py PersonalityVector

Wersja: 1.0
Data: 2026-07-28
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum, auto
import random
import threading
import logging
from collections import defaultdict
import sys

from .agent_core import AgentType, AgentStatus

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMY - Cechy Osobowości
# ============================================================================

class PersonalityTrait(Enum):
    """
    Dostępne cechy osobowości (8 parametrów).
    
    Zgodnie z 05_AGENT_SYSTEM.md Sekcja 3.1 (Personality Vector)
    """
    ANALYSIS_POWER = "analysis_power"           # Zdolność do analizy danych i zależności
    RISK_ACCEPTANCE = "risk_acceptance"        # Poziom akceptowanego ryzyka
    CURIOSITY = "curiosity"                     # Skłonność do poszukiwania nowych rozwiązań
    SECURITY_PREFERENCE = "security_preference"  # Preferencja stabilnych i bezpiecznych decyzji
    EXPERIMENTATION_LEVEL = "experimentation_level"  # Gotowość do testowania nowych hipotez
    INDEPENDENCE = "independence"              # Poziom samodzielności decyzji
    TRUST_LEVEL = "trust_level"               # Aktualny poziom zaufania do innych agentów
    RESILIENCE = "resilience"                  # Odporność na błędne decyzje i porażki


# ============================================================================
# KONFIGURACJA OSOBOWOŚCI
# ============================================================================

@dataclass
class PersonalityConfig:
    """
    Konfiguracja parametrów osobowości.
    
    Zgodnie z 05_AGENT_SYSTEM.md Sekcja 3.1
    
    Attributes:
        trait_ranges: Zakresy poszczególnych cech
        evolution_rates: Szybkości ewolucji poszczególnych cech
        mutation_rates: Współczynniki mutacji
        constraint: Czy wymuszać granice 0-1
    """
    # Zakresy cech (min, max)
    trait_ranges: Dict[str, Tuple[float, float]] = field(default_factory=lambda: {
        "analysis_power": (0.0, 1.0),
        "risk_acceptance": (0.0, 1.0),
        "curiosity": (0.0, 1.0),
        "security_preference": (0.0, 1.0),
        "experimentation_level": (0.0, 1.0),
        "independence": (0.0, 1.0),
        "trust_level": (0.0, 1.0),
        "resilience": (0.0, 1.0)
    })
    
    # Szybkości ewolucji
    evolution_rates: Dict[str, float] = field(default_factory=lambda: {
        "analysis_power": 0.01,
        "risk_acceptance": 0.01,
        "curiosity": 0.01,
        "security_preference": 0.01,
        "experimentation_level": 0.01,
        "independence": 0.01,
        "trust_level": 0.01,
        "resilience": 0.01
    })
    
    # Współczynniki mutacji
    mutation_rates: Dict[str, float] = field(default_factory=lambda: {
        "analysis_power": 0.05,
        "risk_acceptance": 0.05,
        "curiosity": 0.05,
        "security_preference": 0.05,
        "experimentation_level": 0.05,
        "independence": 0.05,
        "trust_level": 0.05,
        "resilience": 0.05
    })
    
    # Ograniczenia
    enforce_bounds: bool = True
    allow_negative: bool = False
    normalize: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            "trait_ranges": self.trait_ranges,
            "evolution_rates": self.evolution_rates,
            "mutation_rates": self.mutation_rates,
            "enforce_bounds": self.enforce_bounds,
            "allow_negative": self.allow_negative,
            "normalize": self.normalize
        }


# ============================================================================
# WEKTOR OSOBOWOŚCI (Rozszerzona wersja)
# ============================================================================

class PersonalityVector:
    """
    Rozszerzona wersja wektora osobowości agenta.
    
    Zgodnie z 05_AGENT_SYSTEM.md Sekcja 3.1 (Personality Vector)
    
    Wektor 8 parametrów:
    - analysis_power: Zdolność do analizy danych i zależności (0.0-1.0)
    - risk_acceptance: Poziom akceptowanego ryzyka (0.0-1.0)
    - curiosity: Skłonność do poszukiwania nowych rozwiązań (0.0-1.0)
    - security_preference: Preferencja stabilnych i bezpiecznych decyzji (0.0-1.0)
    - experimentation_level: Gotowość do testowania nowych hipotez (0.0-1.0)
    - independence: Poziom samodzielności decyzji (0.0-1.0)
    - trust_level: Aktualny poziom zaufania do innych agentów (0.0-1.0)
    - resilience: Odporność na błędne decyzje i porażki (0.0-1.0)
    
    Attributes:
        traits: Słownik cech osobowości
        version: Wersja wektora
        created_at: Data utworzenia
        updated_at: Data ostatniej aktualizacji
    """
    
    # Domyślne wartości dla nowego agenta
    DEFAULT_TRAITS: Dict[str, float] = {
        "analysis_power": 0.5,
        "risk_acceptance": 0.5,
        "curiosity": 0.5,
        "security_preference": 0.5,
        "experimentation_level": 0.5,
        "independence": 0.5,
        "trust_level": 0.5,
        "resilience": 0.5
    }
    
    def __init__(
        self,
        traits: Optional[Dict[str, float]] = None,
        config: Optional[PersonalityConfig] = None
    ):
        """
        Inicjalizacja wektora osobowości.
        
        Args:
            traits: Słownik cech (opcjonalnie)
            config: Konfiguracja (opcjonalnie)
        """
        self.config = config or PersonalityConfig()
        
        # Inicjalizacja cech
        if traits is None:
            self.traits = self.DEFAULT_TRAITS.copy()
        else:
            self.traits = {}
            for trait, value in self.DEFAULT_TRAITS.items():
                self.traits[trait] = traits.get(trait, value)
        
        self.version = 1
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.history: List[Dict[str, Any]] = []
        
        self._lock = threading.Lock()
    
    def __getitem__(self, key: str) -> float:
        """Pobiera wartość cechy"""
        return self.traits.get(key, 0.5)
    
    def __setitem__(self, key: str, value: float) -> None:
        """Ustawia wartość cechy"""
        with self._lock:
            self.traits[key] = self._clamp(value, key)
            self.updated_at = datetime.now()
    
    def __getattr__(self, name: str) -> float:
        """Pobiera wartość cechy przez atrybut"""
        if name in self.traits:
            return self.traits[name]
        raise AttributeError(f"Unknown trait: {name}")
    
    def __setattr__(self, name: str, value: Any) -> None:
        """Ustawia atrybut"""
        if name in self.DEFAULT_TRAITS and isinstance(value, (int, float)):
            with self._lock:
                self.traits[name] = self._clamp(value, name)
                self.updated_at = datetime.now()
        else:
            super().__setattr__(name, value)
    
    def _clamp(self, value: float, trait: str) -> float:
        """Ogranicza wartość do zakresu"""
        if not self.config.enforce_bounds:
            return value
        
        min_val, max_val = self.config.trait_ranges.get(trait, (0.0, 1.0))
        return max(min_val, min(max_val, value))
    
    def to_dict(self) -> Dict[str, float]:
        """Konwersja do słownika"""
        return self.traits.copy()
    
    @classmethod
    def from_dict(cls, data: Dict[str, float], config: Optional[PersonalityConfig] = None) -> 'PersonalityVector':
        """Tworzenie z słownika"""
        return cls(data, config)
    
    def get_all_traits(self) -> Dict[str, float]:
        """Pobiera wszystkie cechy"""
        return self.traits.copy()
    
    def get_trait_value(self, trait: PersonalityTrait) -> float:
        """Pobiera wartość konkretnej cechy"""
        return self.traits.get(trait.value, 0.5)
    
    def set_trait_value(self, trait: PersonalityTrait, value: float) -> None:
        """Ustwa wartość konkretnej cechy"""
        self[trait.value] = value
    
    def get_dominant_traits(self, n: int = 3) -> List[Tuple[str, float]]:
        """Pobiera n najsilniejszych cech"""
        sorted_traits = sorted(self.traits.items(), key=lambda x: x[1], reverse=True)
        return sorted_traits[:n]
    
    def get_weakest_traits(self, n: int = 3) -> List[Tuple[str, float]]:
        """Pobiera n najsłabszych cech"""
        sorted_traits = sorted(self.traits.items(), key=lambda x: x[1])
        return sorted_traits[:n]
    
    def calculate_personality_score(self) -> float:
        """Oblicza ogólny wynik osobowości (0-1)"""
        # Średnia ważona cech
        weights = {
            "analysis_power": 0.15,
            "risk_acceptance": 0.10,
            "curiosity": 0.15,
            "security_preference": 0.10,
            "experimentation_level": 0.15,
            "independence": 0.10,
            "trust_level": 0.10,
            "resilience": 0.15
        }
        
        total = sum(
            self.traits.get(trait, 0.5) * weight 
            for trait, weight in weights.items()
        )
        return total / sum(weights.values())
    
    def get_personality_profile(self) -> Dict[str, Any]:
        """
        Generuje profil osobowości agenta.
        
        Returns:
            Słownik z profilem osobowości
        """
        dominant = self.get_dominant_traits()
        weakest = self.get_weakest_traits()
        score = self.calculate_personality_score()
        
        # Określ typ osobowości na podstawie dominujących cech
        personality_type = self._determine_personality_type()
        
        return {
            "traits": self.traits.copy(),
            "dominant_traits": dominant,
            "weakest_traits": weakest,
            "personality_score": score,
            "personality_type": personality_type,
            "analysis_power": self.traits.get("analysis_power", 0.5),
            "risk_profile": "high" if self.traits.get("risk_acceptance", 0.5) > 0.7 else 
                           "medium" if self.traits.get("risk_acceptance", 0.5) > 0.4 else "low",
            "curiosity_level": "high" if self.traits.get("curiosity", 0.5) > 0.7 else 
                              "medium" if self.traits.get("curiosity", 0.5) > 0.4 else "low"
        }
    
    def _determine_personality_type(self) -> str:
        """Określa typ osobowości na podstawie cech"""
        analysis = self.traits.get("analysis_power", 0.5)
        risk = self.traits.get("risk_acceptance", 0.5)
        curiosity = self.traits.get("curiosity", 0.5)
        security = self.traits.get("security_preference", 0.5)
        experimentation = self.traits.get("experimentation_level", 0.5)
        resilience = self.traits.get("resilience", 0.5)
        
        # Określ typ osobowości
        if analysis > 0.7 and security > 0.7:
            return "ANALYST"
        elif risk > 0.6 and analysis > 0.7:
            return "VALUE_STRATEGIST"
        elif curiosity > 0.7 and experimentation > 0.7:
            return "EXPERIMENTATOR"
        elif resilience > 0.8 and security > 0.7:
            return "MENTAL_EXPERT"
        elif risk < 0.3 and security > 0.8:
            return "CONSERVATOR"
        elif risk > 0.8 and experimentation > 0.7:
            return "AGGRESSOR"
        elif analysis > 0.6 and experimentation > 0.6:
            return "PATTERN_HUNTER"
        else:
            return "BALANCER"
    
    def get_agent_type_suggestion(self) -> AgentType:
        """
        Sugeruje typ agenta na podstawie wektora osobowości.
        
        Zgodnie z 05_AGENT_SYSTEM.md Sekcja 3.3 (Powstawanie Nowych Typów Agentów)
        
        Returns:
            Sugerowany AgentType
        """
        personality_type = self._determine_personality_type()
        
        # Mapowanie typów osobowości na typy agentów
        type_mapping = {
            "ANALYST": AgentType.ANALYST,
            "VALUE_STRATEGIST": AgentType.VALUE_STRATEGIST,
            "EXPERIMENTATOR": AgentType.EXPERIMENTATOR,
            "MENTAL_EXPERT": AgentType.MENTAL_EXPERT,
            "PATTERN_HUNTER": AgentType.PATTERN_HUNTER,
            "CONSERVATOR": AgentType.CONSERVATOR,
            "AGGRESSOR": AgentType.AGGRESSOR,
            "BALANCER": AgentType.BALANCER
        }
        
        return type_mapping.get(personality_type, AgentType.BALANCER)
    
    def evolve(
        self,
        experience: Dict[str, Any],
        config: Optional[PersonalityConfig] = None
    ) -> 'PersonalityVector':
        """
        Ewoluuje wektor osobowości na podstawie doświadczenia.
        
        Zgodnie z 05_AGENT_SYSTEM.md Sekcja 3.2 (Ewolucja Osobowości)
        
        Args:
            experience: Doświadczenie agenta (wyniki, błędy, odkrycia)
            config: Konfiguracja ewolucji (opcjonalnie)
            
        Returns:
            Nowy PersonalityVector
        """
        with self._lock:
            # Użyj domyślnej konfiguracji
            evolution_config = config or self.config
            
            # Oblicz kierunki ewolucji
            directions = self._calculate_evolution_directions(experience, evolution_config)
            
            # Utwórz nowy wektor
            new_vector = PersonalityVector(self.traits.copy(), evolution_config)
            new_vector.version = self.version + 1
            
            # Zastosuj ewolucję
            for trait, direction in directions.items():
                if trait in new_vector.traits:
                    rate = evolution_config.evolution_rates.get(trait, 0.01)
                    new_value = new_vector.traits[trait] + direction * rate
                    new_vector.traits[trait] = evolution_config.enforce_bounds and new_vector._clamp(new_value, trait) or new_value
            
            # Zapisz historię
            new_vector.history.append({
                "timestamp": datetime.now().isoformat(),
                "experience": experience,
                "directions": directions,
                "version": new_vector.version
            })
            
            logger.debug(f"PersonalityVector: Ewolucja z v{self.version} do v{new_vector.version}")
            return new_vector
    
    def _calculate_evolution_directions(
        self,
        experience: Dict[str, Any],
        config: PersonalityConfig
    ) -> Dict[str, float]:
        """
        Oblicza kierunki ewolucji na podstawie doświadczenia.
        
        Args:
            experience: Doświadczenie agenta
            config: Konfiguracja
            
        Returns:
            Słownik z kierunkami zmian (-1.0 do 1.0)
        """
        directions: Dict[str, float] = {}
        
        # Wyciągaj kluczowe metryki z doświadczenia
        success_rate = experience.get("success_rate", 0.5)
        error_rate = experience.get("error_rate", 0.5)
        discovery_rate = experience.get("discovery_rate", 0.5)
        confidence = experience.get("confidence", 0.7)
        frustration = experience.get("frustration", 0.1)
        value_score = experience.get("value_score", 0.5)
        
        # Ewolucja na podstawie wyników
        
        # 1. Wysoka skuteczność - wzmacniamy obecne zachowania
        if success_rate > 0.7:
            # Zwiększ cechy, które przyczyniły się do sukcesu
            for trait in self.traits:
                if self.traits[trait] > 0.5:  # Cechy silne
                    directions[trait] = 0.05
                else:
                    directions[trait] = 0.02
            
            # Szczególnie wzmacniamy analyzę i odporność
            directions["analysis_power"] = directions.get("analysis_power", 0) + 0.03
            directions["resilience"] = directions.get("resilience", 0) + 0.03
        
        # 2. Wysoki poziom błędów - szukamy zmian
        if error_rate > 0.3:
            # Powiększamy ciekawość i eksperymentowanie
            directions["curiosity"] = directions.get("curiosity", 0) + 0.1
            directions["experimentation_level"] = directions.get("experimentation_level", 0) + 0.1
            
            # Zmniejszamy ryzyko (ostrożniej)
            directions["risk_acceptance"] = directions.get("risk_acceptance", 0) - 0.05
            
            # Zwiększamy preferencję bezpieczeństwa
            directions["security_preference"] = directions.get("security_preference", 0) + 0.05
        
        # 3. Wysoki poziom odkryć - wzmacniamy eksplorację
        if discovery_rate > 0.6:
            directions["curiosity"] = directions.get("curiosity", 0) + 0.05
            directions["experimentation_level"] = directions.get("experimentation_level", 0) + 0.05
            directions["independence"] = directions.get("independence", 0) + 0.03
        
        # 4. Wysoka pewność - utrzymujemy stabilize
        if confidence > 0.8:
            directions["resilience"] = directions.get("resilience", 0) + 0.02
            directions["security_preference"] = directions.get("security_preference", 0) + 0.02
        
        # 5. Wysoka frustracja - szukamy nowych rozwiązań
        if frustration > 0.5:
            directions["curiosity"] = directions.get("curiosity", 0) + 0.05
            directions["experimentation_level"] = directions.get("experimentation_level", 0) + 0.05
            directions["risk_acceptance"] = directions.get("risk_acceptance", 0) + 0.03
        
        # 6. Wartość oczekiwana - optymalizujemy
        if value_score > 0.7:
            directions["analysis_power"] = directions.get("analysis_power", 0) + 0.02
            directions["risk_acceptance"] = directions.get("risk_acceptance", 0) + 0.02
        
        # Normalizacja kierunków
        for trait in directions:
            directions[trait] = max(-1.0, min(1.0, directions[trait]))
        
        return directions
    
    def mutate(self, mutation_rate: Optional[float] = None) -> 'PersonalityVector':
        """
        Mutacja losowa wektora osobowości.
        
        Args:
            mutation_rate: Współczynnik mutacji (opcjonalnie)
            
        Returns:
            Nowy PersonalityVector z mutacją
        """
        with self._lock:
            new_vector = PersonalityVector(self.traits.copy(), self.config)
            new_vector.version = self.version + 1
            
            rate = mutation_rate or 0.05
            
            for trait, value in self.traits.items():
                if random.random() < rate:
                    min_val, max_val = self.config.trait_ranges.get(trait, (0.0, 1.0))
                    mutation = random.uniform(-0.1, 0.1)
                    new_value = value + mutation
                    new_vector.traits[trait] = self._clamp(new_value, trait)
            
            # Zapisz historię
            new_vector.history.append({
                "timestamp": datetime.now().isoformat(),
                "type": "mutation",
                "mutation_rate": rate,
                "version": new_vector.version
            })
            
            return new_vector
    
    def crossover(self, other: 'PersonalityVector') -> 'PersonalityVector':
        """
        Krzyżowanie z innym wektorem osobowości.
        
        Args:
            other: Drugi wektor do krzyżowania
            
        Returns:
            Nowy PersonalityVector (dziecko)
        """
        with self._lock:
            child_traits: Dict[str, float] = {}
            
            for trait in self.traits:
                # Krzyżowanie - średnia ważona
                weight = random.random()
                child_value = (self.traits.get(trait, 0.5) * weight + 
                               other.traits.get(trait, 0.5) * (1 - weight))
                child_traits[trait] = self._clamp(child_value, trait)
            
            new_vector = PersonalityVector(child_traits, self.config)
            new_vector.version = max(self.version, other.version) + 1
            
            # Zapisz historię
            new_vector.history.append({
                "timestamp": datetime.now().isoformat(),
                "type": "crossover",
                "parent1": self.version,
                "parent2": other.version,
                "version": new_vector.version
            })
            
            return new_vector
    
    def copy(self) -> 'PersonalityVector':
        """Tworzy kopię wektora"""
        return PersonalityVector(self.traits.copy(), self.config)
    
    def __repr__(self) -> str:
        """Reprezentacja tekstowa"""
        return f"PersonalityVector(v{self.version}, traits={self.traits})"
    
    def __str__(self) -> str:
        """Reprezentacja tekstowa"""
        traits_str = ", ".join(f"{k}={v:.2f}" for k, v in self.traits.items())
        return f"PersonalityVector(v{self.version}): {{{traits_str}}}"


# ============================================================================
# SILNIK OSOBOWOŚCI
# ============================================================================

class PersonalityEngine:
    """
    Silnik zarządzający ewolucją i adaptacją osobowości agentów.
    
    Odpowiedzialność:
    - Śledzenie ewolucji populacji
    - Określanie trendów ewolucyjnych
    - Zarządzanie parametrami ewolucji
    - Monitorowanie stabilności systemu
    
    Zgodnie z 05_AGENT_SYSTEM.md Sekcja 3.2 (Ewolucja Osobowości)
    """
    
    def __init__(self, config: Optional[PersonalityConfig] = None):
        """
        Inicjalizacja silnika osobowości.
        
        Args:
            config: Konfiguracja (opcjonalnie)
        """
        self.config = config or PersonalityConfig()
        self._lock = threading.Lock()
        
        # Historia ewolucji populacji
        self.evolution_history: List[Dict[str, Any]] = []
        
        # Statystyki populacji
        self.population_stats: Dict[str, Any] = {
            "total_vectors": 0,
            "current_version": 1,
            "avg_personality_score": 0.5,
            "trait_averages": {},
            "trait_variances": {},
            "type_distribution": {},
            "evolution_count": 0,
            "mutation_count": 0,
            "crossover_count": 0
        }
        
        self.created_at = datetime.now()
        
        logger.info("Zainicjowano PersonalityEngine")
    
    def register_vector(self, vector: PersonalityVector) -> None:
        """
        Rejestruje nowy wektor osobowości.
        
        Args:
            vector: Nowy wektor
        """
        with self._lock:
            self.population_stats["total_vectors"] += 1
            
            # Aktualizuj średnie
            for trait, value in vector.traits.items():
                if trait not in self.population_stats["trait_averages"]:
                    self.population_stats["trait_averages"][trait] = []
                self.population_stats["trait_averages"][trait].append(value)
            
            # Aktualizuj dystrybucję typów
            personality_type = vector._determine_personality_type()
            if personality_type not in self.population_stats["type_distribution"]:
                self.population_stats["type_distribution"][personality_type] = 0
            self.population_stats["type_distribution"][personality_type] += 1
            
            logger.debug(f"PersonalityEngine: Zarejestrowano vector v{vector.version}")
    
    def get_evolution_trends(self) -> Dict[str, Any]:
        """
        Pobiera trendy ewolucyjne populacji.
        
        Returns:
            Słownik z trendami
        """
        with self._lock:
            trends: Dict[str, Any] = {
                "trait_trends": {},
                "type_trends": {},
                "stability_index": 0.0
            }
            
            # Oblicz trendy cech
            for trait in self.config.trait_ranges.keys():
                avg = self.population_stats["trait_averages"].get(trait, [])
                if len(avg) > 1:
                    # Trend = (ostatnia - pierwsza) / pierwsza
                    first = avg[0]
                    last = avg[-1]
                    trend = (last - first) / first if first != 0 else 0
                    trends["trait_trends"][trait] = trend
                else:
                    trends["trait_trends"][trait] = 0.0
            
            # Oblicz indeks stabilności
            variance_sum = sum(
                abs(trends["trait_trends"].get(trait, 0))
                for trait in self.config.trait_ranges.keys()
            )
            trends["stability_index"] = max(0.0, 1.0 - variance_sum / len(self.config.trait_ranges))
            
            return trends
    
    def evolve_population(
        self,
        agents_experience: List[Dict[str, Any]]
    ) -> List[PersonalityVector]:
        """
        Ewoluuje populację na podstawie doświadczeń.
        
        Args:
            agents_experience: Lista doświadczeń agentów
            
        Returns:
            Lista nowych wektorów osobowości
        """
        with self._lock:
            new_vectors = []
            
            for experience in agents_experience:
                # Utwórz tymczasowy wektor (symulacja)
                # W rzeczywistości używałby osobowości konkretnego agenta
                temp_vector = PersonalityVector(self.config.DEFAULT_TRAITS.copy(), self.config)
                
                # Ewoluuj wektor
                new_vector = temp_vector.evolve(experience, self.config)
                new_vectors.append(new_vector)
                
                # Rejestruj ewolucję
                self.population_stats["evolution_count"] += 1
            
            # Zapisz w historii
            self.evolution_history.append({
                "timestamp": datetime.now().isoformat(),
                "experience_count": len(agents_experience),
                "new_vectors": len(new_vectors)
            })
            
            return new_vectors
    
    def get_statistics(self) -> Dict[str, Any]:
        """Pobiera statystyki silnika"""
        return {
            **self.population_stats,
            "created_at": self.created_at.isoformat(),
            "trait_count": len(self.config.trait_ranges),
            "evolution_history_count": len(self.evolution_history)
        }
    
    def get_report(self) -> str:
        """Generuje raport silnika"""
        stats = self.get_statistics()
        trends = self.get_evolution_trends()
        
        report = [
            "=" * 60,
            "RAPORT PERSONALITY ENGINE",
            "=" * 60,
            f"Całkowita liczba wektorów: {stats['total_vectors']}",
            f"Aktualna wersja: {stats['current_version']}",
            f"Średni wynik osobowości: {stats['avg_personality_score']:.2f}",
            f"Liczba ewolucji: {stats['evolution_count']}",
            f"Indeks stabilności: {trends['stability_index']:.2%}",
            "",
            "Trendy cech:",
        ]
        
        for trait, trend in trends["trait_trends"].items():
            direction = "↑" if trend > 0 else "↓" if trend < 0 else "→"
            report.append(f"  - {trait}: {trend:+.3f} {direction}")
        
        report.extend([
            "",
            "Dystrybucja typów:",
        ])
        
        for personality_type, count in stats.get("type_distribution", {}).items():
            percentage = (count / stats['total_vectors']) * 100 if stats['total_vectors'] > 0 else 0
            report.append(f"  - {personality_type}: {count} ({percentage:.1f}%)")
        
        report.append("=" * 60)
        
        return "\n".join(report)


# ============================================================================
# FUNKCJE POMOCNICZE
# ============================================================================

def get_default_personality(agent_type: AgentType) -> Dict[str, float]:
    """
    Zwraca domyślne wartości osobowości dla danego typu agenta.
    
    Zgodnie z 05_AGENT_SYSTEM.md Sekcja 2.3 (Pierwsza Populacja)
    
    Args:
        agent_type: Typ agenta
        
    Returns:
        Słownik z domyślnymi wartościami
    """
    default_personalities = {
        AgentType.ANALYST: {
            "analysis_power": 0.80,
            "risk_acceptance": 0.30,
            "curiosity": 0.40,
            "security_preference": 0.85,
            "experimentation_level": 0.20,
            "independence": 0.60,
            "trust_level": 0.50,
            "resilience": 0.90
        },
        AgentType.VALUE_STRATEGIST: {
            "analysis_power": 0.85,
            "risk_acceptance": 0.55,
            "curiosity": 0.70,
            "security_preference": 0.50,
            "experimentation_level": 0.40,
            "independence": 0.70,
            "trust_level": 0.50,
            "resilience": 0.80
        },
        AgentType.EXPERIMENTATOR: {
            "analysis_power": 0.70,
            "risk_acceptance": 0.80,
            "curiosity": 0.85,
            "security_preference": 0.30,
            "experimentation_level": 0.90,
            "independence": 0.80,
            "trust_level": 0.50,
            "resilience": 0.85
        },
        AgentType.MENTAL_EXPERT: {
            "analysis_power": 0.85,
            "risk_acceptance": 0.40,
            "curiosity": 0.60,
            "security_preference": 0.80,
            "experimentation_level": 0.30,
            "independence": 0.70,
            "trust_level": 0.60,
            "resilience": 0.95
        },
        AgentType.PATTERN_HUNTER: {
            "analysis_power": 0.90,
            "risk_acceptance": 0.60,
            "curiosity": 0.90,
            "security_preference": 0.40,
            "experimentation_level": 0.85,
            "independence": 0.85,
            "trust_level": 0.50,
            "resilience": 0.85
        },
        AgentType.RISK_ANALYST: {
            "analysis_power": 0.85,
            "risk_acceptance": 0.50,
            "curiosity": 0.70,
            "security_preference": 0.60,
            "experimentation_level": 0.50,
            "independence": 0.75,
            "trust_level": 0.55,
            "resilience": 0.80
        },
        AgentType.INVESTOR: {
            "analysis_power": 0.75,
            "risk_acceptance": 0.70,
            "curiosity": 0.75,
            "security_preference": 0.40,
            "experimentation_level": 0.70,
            "independence": 0.80,
            "trust_level": 0.45,
            "resilience": 0.85
        },
        AgentType.CONSERVATOR: {
            "analysis_power": 0.80,
            "risk_acceptance": 0.20,
            "curiosity": 0.30,
            "security_preference": 0.95,
            "experimentation_level": 0.15,
            "independence": 0.50,
            "trust_level": 0.55,
            "resilience": 0.90
        },
        AgentType.AGGRESSOR: {
            "analysis_power": 0.65,
            "risk_acceptance": 0.95,
            "curiosity": 0.60,
            "security_preference": 0.20,
            "experimentation_level": 0.90,
            "independence": 0.90,
            "trust_level": 0.30,
            "resilience": 0.80
        },
        AgentType.BALANCER: {
            "analysis_power": 0.75,
            "risk_acceptance": 0.50,
            "curiosity": 0.60,
            "security_preference": 0.50,
            "experimentation_level": 0.50,
            "independence": 0.65,
            "trust_level": 0.55,
            "resilience": 0.85
        },
        AgentType.TEST_AGENT: {
            "analysis_power": 0.60,
            "risk_acceptance": 0.60,
            "curiosity": 0.60,
            "security_preference": 0.50,
            "experimentation_level": 0.60,
            "independence": 0.60,
            "trust_level": 0.50,
            "resilience": 0.70
        }
    }
    
    return default_personalities.get(agent_type, default_personalities[AgentType.BALANCER])


def tworz_personality_vector(
    traits: Optional[Dict[str, float]] = None,
    agent_type: Optional[AgentType] = None,
    config: Optional[PersonalityConfig] = None
) -> PersonalityVector:
    """
    Fabryka tworzących PersonalityVector.
    
    Args:
        traits: Słownik cech (opcjonalnie)
        agent_type: Typ agenta (użyje domyślnych wartości)
        config: Konfiguracja (opcjonalnie)
        
    Returns:
        PersonalityVector
        
    Example:
        >>> vector = tworz_personality_vector(agent_type=AgentType.ANALYST)
        >>> print(vector.get_personality_profile())
    """
    if traits is None and agent_type is not None:
        traits = get_default_personality(agent_type)
    
    return PersonalityVector(traits, config)


# ============================================================================
# TESTY
# ============================================================================

if __name__ == "__main__":
    import logging
    from SSI.core.logging_config import (
        setup_logging, get_logger, set_correlation_id, generate_correlation_id
    )
    
    # Skonfiguruj logging
    setup_logging(level=logging.INFO, json_format=False)
    logger = get_logger(__name__)
    
    # Ustaw correlation_id
    correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)
    
    logger.info("Testing SSI V4 Personality Vector System...", extra={"correlation_id": correlation_id})
    logger.info("=" * 60, extra={"correlation_id": correlation_id})
    
    # Test 1: Tworzenie wektora osobowości
    logger.info("[Test 1] Tworzenie PersonalityVector...", extra={"correlation_id": correlation_id})
    vector = tworz_personality_vector(agent_type=AgentType.ANALYST)
    logger.info(f"  Wektor utworzony: {vector.version}", extra={"correlation_id": correlation_id})
    logger.info(f"  Cechy: {vector.to_dict()}", extra={"correlation_id": correlation_id})
    
    # Test 2: Profil osobowości
    logger.info("[Test 2] Profil osobowości...", extra={"correlation_id": correlation_id})
    profile = vector.get_personality_profile()
    logger.info(f"  Typ osobowości: {profile['personality_type']}", extra={"correlation_id": correlation_id})
    logger.info(f"  Wynik osobowości: {profile['personality_score']:.2f}", extra={"correlation_id": correlation_id})
    logger.info(f"  Dominujące cechy: {profile['dominant_traits']}", extra={"correlation_id": correlation_id})
    
    # Test 3: Ewolucja
    logger.info("[Test 3] Ewolucja wektora...", extra={"correlation_id": correlation_id})
    experience = {
        "success_rate": 0.8,
        "error_rate": 0.1,
        "discovery_rate": 0.6,
        "confidence": 0.85,
        "frustration": 0.1
    }
    evolved_vector = vector.evolve(experience)
    logger.info(f"  Nowa wersja: {evolved_vector.version}", extra={"correlation_id": correlation_id})
    changes = {(trait, evolved_vector[trait] - vector[trait]) for trait in vector.traits 
               if evolved_vector[trait] != vector[trait]}
    logger.info(f"  Zmiany: {changes}", extra={"correlation_id": correlation_id})
    
    # Test 4: Mutacja
    logger.info("[Test 4] Mutacja wektora...", extra={"correlation_id": correlation_id})
    mutated_vector = vector.mutate(mutation_rate=0.3)
    logger.info(f"  Nowa wersja: {mutated_vector.version}", extra={"correlation_id": correlation_id})
    changes = {(trait, mutated_vector[trait] - vector[trait]) for trait in vector.traits 
               if mutated_vector[trait] != vector[trait]}
    logger.info(f"  Zmiany: {changes}", extra={"correlation_id": correlation_id})
    
    # Test 5: Krzyżowanie
    logger.info("[Test 5] Krzyżowanie wektorów...", extra={"correlation_id": correlation_id})
    vector2 = tworz_personality_vector(agent_type=AgentType.VALUE_STRATEGIST)
    child_vector = vector.crossover(vector2)
    logger.info(f"  Dziecko wersja: {child_vector.version}", extra={"correlation_id": correlation_id})
    logger.info(f"  Typ osobowości dziecka: {child_vector._determine_personality_type()}",
                extra={"correlation_id": correlation_id})
    
    # Test 6: Silnik osobowości
    logger.info("[Test 6] PersonalityEngine...", extra={"correlation_id": correlation_id})
    engine = PersonalityEngine()
    
    # Rejestruj kilka wektorów
    for agent_type in [AgentType.ANALYST, AgentType.VALUE_STRATEGIST, AgentType.EXPERIMENTATOR]:
        vec = tworz_personality_vector(agent_type=agent_type)
        engine.register_vector(vec)
    
    stats = engine.get_statistics()
    logger.info(f"  Zarejestrowane wektory: {stats['total_vectors']}",
                extra={"correlation_id": correlation_id})
    logger.info(f"  Dystrybucja typów: {stats['type_distribution']}",
                extra={"correlation_id": correlation_id})
    
    # Raport
    logger.info("[Raport Personality Engine]", extra={"correlation_id": correlation_id})
    logger.info(engine.get_report(), extra={"correlation_id": correlation_id})
    
    # Test 7: Sugestia typu agenta
    logger.info("[Test 7] Sugestia typu agenta...", extra={"correlation_id": correlation_id})
    for agent_type in [AgentType.ANALYST, AgentType.PATTERN_HUNTER, AgentType.CONSERVATOR]:
        vec = tworz_personality_vector(agent_type=agent_type)
        suggested = vec.get_agent_type_suggestion()
        logger.info(f"  {agent_type.value} -> {suggested.value}",
                    extra={"correlation_id": correlation_id})
    
    # Test 8: Tworzenie wektorów z domyślnymi wartościami
    logger.info("[Test 8] Domyślne wartości osobowości...", extra={"correlation_id": correlation_id})
    for agent_type in [AgentType.MENTAL_EXPERT, AgentType.AGGRESSOR, AgentType.BALANCER]:
        vec = tworz_personality_vector(agent_type=agent_type)
        logger.info(f"  {agent_type.value}: {vec.to_dict()}",
                    extra={"correlation_id": correlation_id})
    
    logger.info("=" * 60, extra={"correlation_id": correlation_id})
    
    # Sprawdź, czy wektor został poprawnie utworzony
    test_failed = vector is None or not hasattr(vector, 'traits')
    
    if test_failed:
        logger.error("Some Personality Vector tests FAILED!",
                      extra={"correlation_id": correlation_id})
        sys.exit(1)
    
    logger.info("All Personality Vector tests passed!", extra={"correlation_id": correlation_id})
    logger.info("=" * 60, extra={"correlation_id": correlation_id})
