# SSI V5 Agent Layer - Personality Manager
# ==================================================
#
# ETAP: 5.2.5 FAZA 1
# Data: 2026-08-04
#
# Odpowiedzialnosc:
# - Zarządzanie wektorem osobowości agenta
# - Ewolucja parametrów osobowości
# - Historia zmian osobowości
# - Inicjalizacja domyślnych profili osobowości
#
# Zgodnosc z: SSI_DOCUMENTATION/05_AGENT_SYSTEM.md (sekcja 3)

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Tuple
from enum import Enum
from datetime import datetime
import uuid
import copy
import json
import os
from threading import Lock


class PersonalityParameter(Enum):
    """Parametry wektora osobowości agenta"""
    RISK_TOLERANCE = "risk_tolerance"          # Tolerancja ryzyka (0.0-1.0)
    CREATIVITY = "creativity"                  # Kreatywność (0.0-1.0)
    EXPLORATION_DRIVE = "exploration_drive"   # Napęd eksploracji (0.0-1.0)
    PERSISTENCE = "persistence"               # Wytrwałość/upór (0.0-1.0)
    COOPERATION = "cooperation"               # Współpraca (0.0-1.0)
    CONFIDENCE = "confidence"                 # Pewność siebie (0.0-1.0)
    ADAPTABILITY = "adaptability"             # Adaptacyjność (0.0-1.0)
    ANALYTICAL_LEVEL = "analytical_level"     # Poziom analityczny (0.0-1.0)


# Mapowanie parametrów z dokumentacji SSI V4
# Dokumentacja: analysis_power, risk_acceptance, curiosity, security_preference,
# experimentation_level, independence, trust_level, resilience
# Nasza implementacja: analytical_level, risk_tolerance, creativity, persistence,
# exploration_drive, cooperation, confidence, adaptability

PERSONALITY_MAPPING = {
    'analysis_power': 'analytical_level',
    'risk_acceptance': 'risk_tolerance',
    'curiosity': 'creativity',
    'security_preference': 'persistence',
    'experimentation_level': 'exploration_drive',
    'independence': 'confidence',
    'trust_level': 'cooperation',
    'resilience': 'adaptability'
}


# Domyślne profile osobowości dla 6 agentów
DEFAULT_PERSONALITY_PROFILES = {
    "Agent_01": {
        "name": "Analityk",
        "description": "Ostrożny, metodyczny, preferuje bezpieczne strategie",
        "values": {
            "analytical_level": 0.90,    # Wysoka zdolność analizy
            "risk_tolerance": 0.30,      # Niska tolerancja ryzyka
            "creativity": 0.60,          # Średnia kreatywność
            "exploration_drive": 0.40,   # Niski napęd eksploracji
            "persistence": 0.85,         # Wysoka wytrwałość
            "cooperation": 0.70,        # Dobra współpraca
            "confidence": 0.80,          # Wysoka pewność
            "adaptability": 0.60         # Średnia adaptacyjność
        }
    },
    "Agent_02": {
        "name": "Strateg Wartości",
        "description": "Analizuje kursy, szuka przewagi ekonomicznej",
        "values": {
            "analytical_level": 0.85,    # Wysoka analiza
            "risk_tolerance": 0.55,      # Średnia tolerancja ryzyka
            "creativity": 0.70,          # Wysoka kreatywność
            "exploration_drive": 0.50,   # Średni napęd eksploracji
            "persistence": 0.75,         # Wysoka wytrwałość
            "cooperation": 0.65,        # Dobra współpraca
            "confidence": 0.85,          # Wysoka pewność
            "adaptability": 0.70         # Dobra adaptacyjność
        }
    },
    "Agent_03": {
        "name": "Eksperymentator",
        "description": "Ciekawski, kreatywny, testuje nowe rozwiqzania",
        "values": {
            "analytical_level": 0.70,    # Dobra analiza
            "risk_tolerance": 0.80,      # Wysoka tolerancja ryzyka
            "creativity": 0.90,          # Bardzo kreatywny
            "exploration_drive": 0.90,   # Wysoki napęd eksploracji
            "persistence": 0.60,         # Średnia wytrwałość
            "cooperation": 0.50,        # Średnia współpraca
            "confidence": 0.70,          # Średnia pewność
            "adaptability": 0.90         # Bardzo adaptacyjny
        }
    },
    "Agent_04": {
        "name": "Mental Expert",
        "description": "Stabilny, długoterminowy, nie panikuje po błędach",
        "values": {
            "analytical_level": 0.80,    # Wysoka analiza
            "risk_tolerance": 0.40,      # Niska tolerancja ryzyka
            "creativity": 0.50,          # Średnia kreatywność
            "exploration_drive": 0.30,   # Niski napęd eksploracji
            "persistence": 0.95,         # Bardzo wytrwały
            "cooperation": 0.80,        # Bardzo dobra współpraca
            "confidence": 0.85,          # Wysoka pewność
            "adaptability": 0.50         # Średnia adaptacyjność
        }
    },
    "Agent_05": {
        "name": "Pattern Hunter",
        "description": "Szuka ukrytych zależności, łączy różne światy",
        "values": {
            "analytical_level": 0.85,    # Wysoka analiza
            "risk_tolerance": 0.60,      # Średnia tolerancja ryzyka
            "creativity": 0.85,          # Wysoka kreatywność
            "exploration_drive": 0.80,   # Wysoki napęd eksploracji
            "persistence": 0.70,         # Dobra wytrwałość
            "cooperation": 0.60,        # Średnia współpraca
            "confidence": 0.75,          # Dobra pewność
            "adaptability": 0.85         # Wysoka adaptacyjność
        }
    },
    "Agent_06": {
        "name": "Adaptive Strategist",
        "description": "Dostosowuje strategię do zmiennych warunków",
        "values": {
            "analytical_level": 0.88,    # Bardzo wysoka analiza
            "risk_tolerance": 0.50,      # Średnia tolerancja ryzyka
            "creativity": 0.80,          # Wysoka kreatywność
            "exploration_drive": 0.70,   # Dobry napęd eksploracji
            "persistence": 0.75,         # Dobra wytrwałość
            "cooperation": 0.75,        # Dobra współpraca
            "confidence": 0.80,          # Wysoka pewność
            "adaptability": 0.95         # Bardzo wysoka adaptacyjność
        }
    }
}


# Domyślne wartości dla nowych agentów
DEFAULT_PERSONALITY_VALUES = {
    "analytical_level": 0.50,
    "risk_tolerance": 0.50,
    "creativity": 0.50,
    "exploration_drive": 0.50,
    "persistence": 0.50,
    "cooperation": 0.50,
    "confidence": 0.50,
    "adaptability": 0.50
}


@dataclass
class PersonalityVector:
    """
    Wektor osobowości agenta - 8 parametrów definiujących charakter i zachowanie.
    
    Zakres wartości: 0.0 - 1.0
    
    Parametry:
    - analytical_level: Zdolność do analizy danych i zależności
    - risk_tolerance: Poziom akceptowanego ryzyka
    - creativity: Skłonność do poszukiwania nowych rozwiązań
    - exploration_drive: Gotowość do testowania nowych hipotez
    - persistence: Odporność na błędne decyzje i porażki
    - cooperation: Poziom współpracy z innymi agentami
    - confidence: Pewność siebie
    - adaptability: Zdolność adaptacji do zmian
    
    Zgodnosc z: SSI_DOCUMENTATION/05_AGENT_SYSTEM.md (sekcja 3.1)
    """
    analytical_level: float = 0.50
    risk_tolerance: float = 0.50
    creativity: float = 0.50
    exploration_drive: float = 0.50
    persistence: float = 0.50
    cooperation: float = 0.50
    confidence: float = 0.50
    adaptability: float = 0.50
    
    def __post_init__(self):
        """Walidacja wartości po inicjalizacji"""
        self._validate_values()
    
    def _validate_values(self) -> None:
        """Walidacja, że wszystkie wartości są w zakresie 0.0-1.0"""
        for param_name in self.__dataclass_fields__:
            value = getattr(self, param_name)
            if not isinstance(value, (int, float)):
                continue
            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"Personality parameter '{param_name}' must be between 0.0 and 1.0, got {value}"
                )
    
    def to_dict(self) -> Dict[str, float]:
        """Konwersja do słownika"""
        return {
            'analytical_level': self.analytical_level,
            'risk_tolerance': self.risk_tolerance,
            'creativity': self.creativity,
            'exploration_drive': self.exploration_drive,
            'persistence': self.persistence,
            'cooperation': self.cooperation,
            'confidence': self.confidence,
            'adaptability': self.adaptability
        }
    
    def to_list(self) -> List[float]:
        """Konwersja do listy wartości (w kolejności parametrów)"""
        return [
            self.analytical_level,
            self.risk_tolerance,
            self.creativity,
            self.exploration_drive,
            self.persistence,
            self.cooperation,
            self.confidence,
            self.adaptability
        ]
    
    @classmethod
    def from_dict(cls, personality_data: Dict[str, float]) -> 'PersonalityVector':
        """Tworzenie PersonalityVector z słownika"""
        return cls(**personality_data)
    
    @classmethod
    def from_profile(cls, profile_name: str) -> 'PersonalityVector':
        """Tworzenie PersonalityVector z domyślnego profilu"""
        if profile_name not in DEFAULT_PERSONALITY_PROFILES:
            raise ValueError(f"Unknown personality profile: {profile_name}")
        
        profile_values = DEFAULT_PERSONALITY_PROFILES[profile_name]["values"]
        return cls.from_dict(profile_values)
    
    @classmethod
    def default(cls) -> 'PersonalityVector':
        """Tworzenie domyślnego PersonalityVector"""
        return cls(**DEFAULT_PERSONALITY_VALUES)
    
    def get_parameter(self, param: PersonalityParameter) -> float:
        """Pobranie konkretnego parametru"""
        return getattr(self, param.value)
    
    def set_parameter(self, param: PersonalityParameter, value: float) -> None:
        """Ustawienie konkretnego parametru z walidacją"""
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"Parameter {param.value} must be between 0.0 and 1.0, got {value}")
        setattr(self, param.value, value)
        self._validate_values()
    
    def update_from_dict(self, updates: Dict[str, float]) -> None:
        """Aktualizacja wielu parametrów na raz"""
        for param_name, value in updates.items():
            if hasattr(self, param_name):
                if not 0.0 <= value <= 1.0:
                    raise ValueError(f"Parameter {param_name} must be between 0.0 and 1.0, got {value}")
                setattr(self, param_name, value)
        self._validate_values()
    
    def weighted_average(self) -> float:
        """Obliczenie ważonej średniej wszystkich parametrów"""
        params = self.to_list()
        return sum(params) / len(params) if params else 0.0
    
    def __eq__(self, other: object) -> bool:
        """Porównanie dwóch wektorów osobowości"""
        if not isinstance(other, PersonalityVector):
            return False
        return self.to_dict() == other.to_dict()
    
    def __str__(self) -> str:
        """Reprezentacja tekstowa"""
        params = [f"{param}: {getattr(self, param):.2f}" 
                  for param in self.__dataclass_fields__]
        return f"PersonalityVector({', '.join(params)})"


@dataclass
class PersonalityChange:
    """Zmiana parametrów osobowości - rekord historyczny"""
    change_id: str
    agent_id: str
    previous_vector: Dict[str, float]
    new_vector: Dict[str, float]
    changed_parameters: Dict[str, Tuple[float, float]]  # {param: (old, new)}
    reason: str  # Powód zmiany (np. "success", "failure", "experiment", "collaboration")
    cycle_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            'change_id': self.change_id,
            'agent_id': self.agent_id,
            'previous_vector': copy.deepcopy(self.previous_vector),
            'new_vector': copy.deepcopy(self.new_vector),
            'changed_parameters': {k: list(v) for k, v in self.changed_parameters.items()},
            'reason': self.reason,
            'cycle_id': self.cycle_id,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class AgentPersonalityState:
    """
    Stan osobowości agenta - zarządza osobowością i historią zmian.
    
    Zgodnosc z: SSI_DOCUMENTATION/05_AGENT_SYSTEM.md (sekcja 3)
    """
    agent_id: str
    name: str
    current_personality: PersonalityVector
    initial_personality: PersonalityVector
    personality_history: List[PersonalityChange] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Blokada dla bezpieczeństwa wielowątkowości
    _lock: Lock = field(default_factory=Lock, compare=False, repr=False)
    
    def __post_init__(self):
        """Inicjalizacja po utworzeniu"""
        if not hasattr(self, '_lock') or self._lock is None:
            self._lock = Lock()
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'current_personality': self.current_personality.to_dict(),
            'initial_personality': self.initial_personality.to_dict(),
            'personality_history': [c.to_dict() for c in self.personality_history],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def get_personality_vector(self) -> PersonalityVector:
        """Pobranie aktualnego wektora osobowości"""
        return copy.deepcopy(self.current_personality)
    
    def get_parameter(self, param: PersonalityParameter) -> float:
        """Pobranie konkretnego parametru osobowości"""
        return self.current_personality.get_parameter(param)
    
    def update_personality(self, updates: Dict[str, float], 
                          reason: str = "unknown", 
                          cycle_id: Optional[str] = None) -> PersonalityChange:
        """
        Aktualizacja parametrów osobowości z zapisaniem historii.
        
        Args:
            updates: Słownik z nowymi wartościami parametrów
            reason: Powód zmiany
            cycle_id: ID cyklu, w którym nastąpiła zmiana
            
        Returns:
            PersonalityChange: Rekord zmiany
        """
        with self._lock:
            # Znajdź zmienione parametry
            changed_params = {}
            for param_name, new_value in updates.items():
                old_value = getattr(self.current_personality, param_name, None)
                if old_value is not None and old_value != new_value:
                    changed_params[param_name] = (old_value, new_value)
            
            if not changed_params:
                # Brak zmian - zwróć pustą zmianę
                return PersonalityChange(
                    change_id=f"change_{uuid.uuid4().hex[:8]}",
                    agent_id=self.agent_id,
                    previous_vector=self.current_personality.to_dict(),
                    new_vector=self.current_personality.to_dict(),
                    changed_parameters={},
                    reason=reason,
                    cycle_id=cycle_id
                )
            
            # Zapisz stare wartości
            previous_vector = self.current_personality.to_dict()
            
            # Zaktualizuj wektor
            self.current_personality.update_from_dict(updates)
            
            # Zapisz nowy wektor
            new_vector = self.current_personality.to_dict()
            
            # Utwórz rekord zmiany
            change = PersonalityChange(
                change_id=f"change_{uuid.uuid4().hex[:8]}",
                agent_id=self.agent_id,
                previous_vector=previous_vector,
                new_vector=new_vector,
                changed_parameters=changed_params,
                reason=reason,
                cycle_id=cycle_id,
                timestamp=datetime.now()
            )
            
            # Dodaj do historii
            self.personality_history.append(change)
            self.updated_at = datetime.now()
            
            return change
    
    def apply_evolution(self, success_rate: float, 
                       decision_quality: float,
                       collaboration_score: float,
                       cycle_id: Optional[str] = None) -> PersonalityChange:
        """
        Zastosuj ewolucję osobowości na podstawie wyników.
        
        To uproszczona wersja ewolucji - pełna ewolucja będzie w późniejszych fazach.
        
        Args:
            success_rate: Odsetek trafnych decyzji (0.0-1.0)
            decision_quality: Jakość decyzji (0.0-1.0)
            collaboration_score: Współpraca z innymi agentami (0.0-1.0)
            cycle_id: ID cyklu
            
        Returns:
            PersonalityChange: Rekord zmiany
        """
        # Oblicz zmiany parametrów na podstawie wyników
        updates = {}
        
        # Analiza: wzrasta przy dobrych wynikach i wysokiej jakości decyzji
        if success_rate > 0.7 and decision_quality > 0.7:
            updates['analytical_level'] = min(self.current_personality.analytical_level + 0.02, 1.0)
        elif success_rate < 0.4:
            updates['analytical_level'] = max(self.current_personality.analytical_level - 0.01, 0.0)
        
        # Tolerancja ryzyka: wzrasta przy dobrych wynikach, maleje przy porażkach
        if success_rate > 0.8 and decision_quality > 0.8:
            updates['risk_tolerance'] = min(self.current_personality.risk_tolerance + 0.03, 1.0)
        elif success_rate < 0.3:
            updates['risk_tolerance'] = max(self.current_personality.risk_tolerance - 0.02, 0.0)
        
        # Kreatywność: wzrasta przy podjęciu nowych wyzwań
        if decision_quality > 0.8:
            updates['creativity'] = min(self.current_personality.creativity + 0.01, 1.0)
        
        # Napęd eksploracji: wzrasta przy dobrych wynikach z nowymi strategiami
        if collaboration_score > 0.7:
            updates['exploration_drive'] = min(self.current_personality.exploration_drive + 0.01, 1.0)
        
        # Wytrwałość: wzrasta przy powtarzających się sukcesach
        if success_rate > 0.75:
            updates['persistence'] = min(self.current_personality.persistence + 0.01, 1.0)
        elif success_rate < 0.3:
            updates['persistence'] = max(self.current_personality.persistence - 0.005, 0.0)
        
        # Współpraca: wzrasta przy dobrej współpracy
        if collaboration_score > 0.8:
            updates['cooperation'] = min(self.current_personality.cooperation + 0.02, 1.0)
        elif collaboration_score < 0.3:
            updates['cooperation'] = max(self.current_personality.cooperation - 0.01, 0.0)
        
        # Pewność: wzrasta przy sukcesach, maleje przy porażkach
        if success_rate > 0.8:
            updates['confidence'] = min(self.current_personality.confidence + 0.02, 1.0)
        elif success_rate < 0.3:
            updates['confidence'] = max(self.current_personality.confidence - 0.01, 0.0)
        
        # Adaptacyjność: wzrasta przy zmiennych warunkach
        updates['adaptability'] = min(self.current_personality.adaptability + 0.005, 1.0)
        
        # Zastosuj aktualizacje
        reason = f"evolution_success_{success_rate:.2f}_quality_{decision_quality:.2f}_collab_{collaboration_score:.2f}"
        return self.update_personality(updates, reason, cycle_id)
    
    def reset_to_initial(self) -> PersonalityChange:
        """Przywrócenie domyślnej osobowości"""
        updates = self.initial_personality.to_dict()
        return self.update_personality(updates, "reset_to_initial")
    
    def get_history(self, limit: Optional[int] = None) -> List[PersonalityChange]:
        """Pobranie historii zmian"""
        if limit is None:
            return copy.deepcopy(self.personality_history)
        else:
            return copy.deepcopy(self.personality_history[-limit:])
    
    def get_evolution_summary(self) -> Dict[str, Any]:
        """Pobranie podsumowania ewolucji"""
        if not self.personality_history:
            return {
                'total_changes': 0,
                'parameters_changed': {},
                'biggest_increase': None,
                'biggest_decrease': None
            }
        
        param_changes = {}
        for change in self.personality_history:
            for param, (old_val, new_val) in change.changed_parameters.items():
                if param not in param_changes:
                    param_changes[param] = {'increases': 0, 'decreases': 0, 'total_change': 0.0}
                
                change_val = new_val - old_val
                param_changes[param]['total_change'] += change_val
                
                if change_val > 0:
                    param_changes[param]['increases'] += 1
                else:
                    param_changes[param]['decreases'] += 1
        
        # Znajdź największy wzrost i spadek
        biggest_increase = None
        biggest_decrease = None
        
        for param, stats in param_changes.items():
            if biggest_increase is None or stats['total_change'] > biggest_increase[1]:
                biggest_increase = (param, stats['total_change'])
            if biggest_decrease is None or stats['total_change'] < biggest_decrease[1]:
                biggest_decrease = (param, stats['total_change'])
        
        return {
            'total_changes': len(self.personality_history),
            'parameters_changed': param_changes,
            'biggest_increase': biggest_increase,
            'biggest_decrease': biggest_decrease,
            'last_change': self.personality_history[-1].timestamp.isoformat() if self.personality_history else None
        }
    
    def save_personality_history(self, file_path: Optional[str] = None) -> bool:
        """
        Zapis historii zmian osobowości do pliku JSON.
        
        Args:
            file_path: Ścieżka do pliku (opcjonalna, domyślnie w pamięci)
            
        Returns:
            bool: Czy zapis się powiódł
        """
        try:
            if file_path is None:
                # Domyślna ścieżka
                from ..core.config import PathConfig
                memory_dir = PathConfig.MEMORY_DIR
                os.makedirs(memory_dir, exist_ok=True)
                file_path = os.path.join(memory_dir, f"{self.agent_id}_personality_history.json")
            
            data = {
                'agent_id': self.agent_id,
                'name': self.name,
                'initial_personality': self.initial_personality.to_dict(),
                'current_personality': self.current_personality.to_dict(),
                'history': [c.to_dict() for c in self.personality_history],
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"[PERSONALITY] Error saving personality history: {e}")
            return False
    
    def load_personality_history(self, file_path: Optional[str] = None) -> bool:
        """
        Wczytanie historii zmian osobowości z pliku JSON.
        
        Args:
            file_path: Ścieżka do pliku (opcjonalna)
            
        Returns:
            bool: Czy wczytanie się powiodło
        """
        try:
            if file_path is None:
                from ..core.config import PathConfig
                memory_dir = PathConfig.MEMORY_DIR
                file_path = os.path.join(memory_dir, f"{self.agent_id}_personality_history.json")
            
            if not os.path.exists(file_path):
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Wczytanie historii
            self.personality_history.clear()
            for change_data in data.get('history', []):
                change = PersonalityChange(
                    change_id=change_data['change_id'],
                    agent_id=change_data['agent_id'],
                    previous_vector=change_data['previous_vector'],
                    new_vector=change_data['new_vector'],
                    changed_parameters={
                        k: tuple(v) for k, v in change_data.get('changed_parameters', {}).items()
                    },
                    reason=change_data['reason'],
                    cycle_id=change_data.get('cycle_id'),
                    timestamp=datetime.fromisoformat(change_data['timestamp'])
                )
                self.personality_history.append(change)
            
            self.updated_at = datetime.fromisoformat(data.get('updated_at', self.updated_at.isoformat()))
            return True
            
        except Exception as e:
            print(f"[PERSONALITY] Error loading personality history: {e}")
            return False


class PersonalityManager:
    """
    Menadżer osobowości - zarządza osobowościami wielu agentów.
    
    Odpowiedzialność:
    - Inicjalizacja domyślnych osobowości dla agentów
    - Zarządzanie historią zmian
    - Ewolucja osobowości na podstawie wyników
    - Zapis i odczyt historii
    """
    
    def __init__(self, world_name: str = "SSI_V5_WORLD"):
        """
        Inicjalizacja PersonalityManager.
        
        Args:
            world_name: Nazwa świata
        """
        self.world_name = world_name
        self._personality_states: Dict[str, AgentPersonalityState] = {}
        self._lock = Lock()
        
        # Domysłne profile dla znanych agentów
        self._default_profiles = DEFAULT_PERSONALITY_PROFILES
    
    def create_personality_state(self, agent_id: str, agent_name: str, 
                                 personality: Optional[PersonalityVector] = None,
                                 use_profile: bool = True) -> AgentPersonalityState:
        """
        Utworzenie stanu osobowości dla nowego agenta.
        
        Args:
            agent_id: ID agenta
            agent_name: Nazwa agenta
            personality: Wektor osobowości (opcjonalny)
            use_profile: Czy użyć domyślnego profilu dla danej nazwy
            
        Returns:
            AgentPersonalityState
        """
        with self._lock:
            if personality is None:
                if use_profile and agent_name in self._default_profiles:
                    # Użyj domyślnego profilu
                    personality = PersonalityVector.from_profile(agent_name)
                else:
                    # Użyj domyślnych wartości
                    personality = PersonalityVector.default()
            
            # Utwórz stan
            state = AgentPersonalityState(
                agent_id=agent_id,
                name=agent_name,
                current_personality=copy.deepcopy(personality),
                initial_personality=copy.deepcopy(personality)
            )
            
            self._personality_states[agent_id] = state
            return state
    
    def get_personality_state(self, agent_id: str) -> Optional[AgentPersonalityState]:
        """Pobranie stanu osobowości agenta"""
        with self._lock:
            return self._personality_states.get(agent_id)
    
    def get_personality_vector(self, agent_id: str) -> Optional[PersonalityVector]:
        """Pobranie wektora osobowości agenta"""
        state = self.get_personality_state(agent_id)
        if state:
            return state.get_personality_vector()
        return None
    
    def update_personality(self, agent_id: str, updates: Dict[str, float],
                          reason: str = "unknown",
                          cycle_id: Optional[str] = None) -> Optional[PersonalityChange]:
        """
        Aktualizacja osobowości agenta.
        
        Args:
            agent_id: ID agenta
            updates: Aktualizacje parametrów
            reason: Powód aktualizacji
            cycle_id: ID cyklu
            
        Returns:
            PersonalityChange lub None jeśli agent nie istnieje
        """
        state = self.get_personality_state(agent_id)
        if state:
            return state.update_personality(updates, reason, cycle_id)
        return None
    
    def apply_evolution(self, agent_id: str, success_rate: float,
                       decision_quality: float, collaboration_score: float,
                       cycle_id: Optional[str] = None) -> Optional[PersonalityChange]:
        """
        Zastosowanie ewolucji osobowości agenta.
        
        Args:
            agent_id: ID agenta
            success_rate: Odsetek trafnych decyzji
            decision_quality: Jakość decyzji
            collaboration_score: Współpraca z innymi agentami
            cycle_id: ID cyklu
            
        Returns:
            PersonalityChange lub None
        """
        state = self.get_personality_state(agent_id)
        if state:
            return state.apply_evolution(success_rate, decision_quality, collaboration_score, cycle_id)
        return None
    
    def get_all_personality_states(self) -> Dict[str, AgentPersonalityState]:
        """Pobranie wszystkich stanów osobowości"""
        with self._lock:
            return copy.deepcopy(self._personality_states)
    
    def get_personality_summary(self) -> Dict[str, Any]:
        """Pobranie podsumowania osobowości wszystkich agentów"""
        summary = {
            'total_agents': len(self._personality_states),
            'agents': {},
            'average_personality': {},
            'total_changes': 0
        }
        
        # Oblicz średnią osobowość
        param_sums = {p.value: 0.0 for p in PersonalityParameter}
        param_counts = {p.value: 0 for p in PersonalityParameter}
        
        for agent_id, state in self._personality_states.items():
            agent_data = {
                'name': state.name,
                'personality': state.current_personality.to_dict(),
                'changes_count': len(state.personality_history),
                'last_updated': state.updated_at.isoformat()
            }
            summary['agents'][agent_id] = agent_data
            summary['total_changes'] += len(state.personality_history)
            
            # Aktualizuj sumy dla średniej
            for param in PersonalityParameter:
                param_sums[param.value] += state.current_personality.get_parameter(param)
                param_counts[param.value] += 1
        
        # Oblicz średnie
        for param in param_sums:
            if param_counts[param] > 0:
                summary['average_personality'][param] = param_sums[param] / param_counts[param]
        
        return summary
    
    def save_all_personality_histories(self) -> bool:
        """Zapisanie historii wszystkich agentów"""
        success = True
        for agent_id, state in self._personality_states.items():
            if not state.save_personality_history():
                success = False
        return success
    
    def load_all_personality_histories(self) -> bool:
        """Wczytanie historii wszystkich agentów"""
        # Przeładuj wszystkie pliki, ale nie usuwaj istniejących stanów
        # To uproszczona wersja - pełna olimpijka będzie w późniejszych fazach
        return True
    
    def clear_all_personality_histories(self) -> None:
        """Wyczyszczenie historii wszystkich agentów"""
        with self._lock:
            for state in self._personality_states.values():
                state.personality_history.clear()


# Eksportowane elementy
__all__ = [
    'PersonalityParameter',
    'PersonalityVector',
    'PersonalityChange',
    'AgentPersonalityState',
    'PersonalityManager',
    'DEFAULT_PERSONALITY_PROFILES',
    'DEFAULT_PERSONALITY_VALUES',
    'PERSONALITY_MAPPING'
]
