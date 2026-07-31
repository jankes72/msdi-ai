"""
SSI V5 - Agent Memory Store
Przechowywanie i zarzadzanie pamiecia agentow

Zgodnie z dokumentacja Sprint 11.5:
- Memory Observation System
- Agent Runtime Foundation
"""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from enum import Enum


class MemoryType(Enum):
    """Typy pamieci agenta."""
    PERSONALITY = "personality"
    BEHAVIOR = "behavior"
    STRATEGY = "strategy"
    HISTORY = "history"
    RELATIONSHIP = "relationship"
    PROMPT = "prompt"
    
    @classmethod
    def from_string(cls, value: str) -> Optional['MemoryType']:
        """Konwersja stringa na MemoryType enum.
        
        Args:
            value: Stringowy typ pamieci (np. "personality", "behavior")
        Returns:
            MemoryType enum lub None jeśli nie znaleziono
        """
        try:
            return cls(value)
        except ValueError:
            # Próba dopasowania bez względu na wielkość liter
            value_lower = value.lower()
            for member in cls:
                if member.value.lower() == value_lower:
                    return member
            return None


@dataclass
class MemoryEntry:
    """Ogolny wpis w pamieci."""
    
    # Pola wymagane
    entry_id: str
    created_at: str
    updated_at: str
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Pola z domyslnymi wartosciami
    memory_type: MemoryType = MemoryType.PERSONALITY
    tags: List[str] = field(default_factory=list)
    priority: int = 1
    expiration: Optional[str] = None  # Data waznosci
    
    # Aktywne
    active: bool = True
    validated: bool = False


@dataclass
class PersonalityMemoryEntry(MemoryEntry):
    """Wpis w pamieci osobowosci."""
    
    # Wagi - pola wymagane
    risk: float = 0.5
    analysis: float = 0.5
    creativity: float = 0.5
    trust_v2: float = 0.8
    trust_v3: float = 0.8
    trust_v4: float = 0.8
    trust_external: float = 0.6
    
    # Cechy
    traits: Dict[str, float] = field(default_factory=dict)
    
    # Opis
    description: str = ""
    agent_type: str = "balanced"
    
    # Priorytety
    priorities: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.memory_type = MemoryType.PERSONALITY


@dataclass
class BehaviorMemoryEntry(MemoryEntry):
    """Wpis w pamieci zachowan."""
    
    # Zachowanie
    action: str = ""
    behavior_type: str = "decision"
    description: str = ""
    
    # Kontekst
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Wykorzystane dane
    data_sources: List[str] = field(default_factory=list)
    
    # Skutecznosc
    effectiveness: float = 0.0
    success_rate: float = 0.0
    
    # Historia uzycia
    usage_count: int = 0
    first_used: str = ""
    last_used: str = ""
    
    # Bledy
    errors: List[str] = field(default_factory=list)
    corrections: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.memory_type = MemoryType.BEHAVIOR


@dataclass
class StrategyMemoryEntry(MemoryEntry):
    """Wpis w pamieci strategii."""
    
    # Strategia
    strategy_name: str = ""
    strategy_type: str = ""
    
    # Opis
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Historia uzycia
    times_used: int = 0
    times_successful: int = 0
    first_used: str = ""
    last_used: str = ""
    
    # Wyniki
    avg_confidence: float = 0.0
    avg_effective: float = 0.0
    success_rate: float = 0.0
    
    # Konteksty zastosowania
    contexts: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        self.memory_type = MemoryType.STRATEGY


@dataclass
class HistoryMemoryEntry(MemoryEntry):
    """Wpis w pamieci historii."""
    
    # Zdarzenie
    event_type: str = ""
    description: str = ""
    
    # Kategorizacja
    categories: List[str] = field(default_factory=list)
    
    # Powiazania
    related_agent_id: Optional[str] = None
    related_decision_id: Optional[str] = None
    related_strategy_id: Optional[str] = None
    
    # Wyniki
    outcome: Dict[str, Any] = field(default_factory=dict)
    success: Optional[bool] = None
    
    # Ocena
    evaluation: float = 0.0
    confidence: float = 0.0
    
    def __post_init__(self):
        self.memory_type = MemoryType.HISTORY


@dataclass
class RelationshipMemoryEntry(MemoryEntry):
    """Wpis w pamieci relacji."""
    
    # Relacja
    other_agent_id: str = ""
    relationship_type: str = "neutral"  # trust, conflict, collaboration, competition, neutral
    
    # Wartość
    trust_score: float = 0.0  # -1 to +1
    collaboration_score: float = 0.0  # 0 to 1
    conflict_score: float = 0.0  # 0 to 1
    
    # Historia
    interactions: int = 0
    positive_interactions: int = 0
    negative_interactions: int = 0
    neutral_interactions: int = 0
    
    # Ostatnia interakcja
    last_interaction: str = ""
    last_interaction_type: str = ""
    last_interaction_result: str = ""
    
    # Wymiana informacji
    information_shared: int = 0
    information_received: int = 0
    information_quality: float = 0.0
    
    def __post_init__(self):
        self.memory_type = MemoryType.RELATIONSHIP


@dataclass
class PromptMemoryEntry(MemoryEntry):
    """Wpis w pamieci promptow (dla modeli jezykowych)."""
    
    # Prompt
    prompt_text: str = ""
    prompt_type: str = "system"  # system, user, assistant, context
    
    # Kontekst
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Uzycie
    times_used: int = 0
    avg_response_quality: float = 0.0
    avg_confidence: float = 0.0
    
    # Powiazania
    related_data: List[str] = field(default_factory=list)
    
    # Wygenerowane wyniki
    generated_results: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        self.memory_type = MemoryType.PROMPT


class AgentMemoryStore:
    """Przechowalnia pamieci agenta."""
    
    def __init__(self, agent_id: str, base_path: str = ""):
        self.agent_id = agent_id
        self.base_path = base_path
        
        # Inicjalizacja pamieci
        self._personality_memory: Dict[str, PersonalityMemoryEntry] = {}
        self._behavior_memory: Dict[str, BehaviorMemoryEntry] = {}
        self._strategy_memory: Dict[str, StrategyMemoryEntry] = {}
        self._history_memory: Dict[str, HistoryMemoryEntry] = {}
        self._relationship_memory: Dict[str, RelationshipMemoryEntry] = {}
        self._prompt_memory: Dict[str, PromptMemoryEntry] = {}
        
        # Indeksy
        self._indexes: Dict[MemoryType, Dict[str, List[str]]] = {
            MemoryType.PERSONALITY: {},
            MemoryType.BEHAVIOR: {},
            MemoryType.STRATEGY: {},
            MemoryType.HISTORY: {},
            MemoryType.RELATIONSHIP: {},
            MemoryType.PROMPT: {}
        }
        
        # Statystyki
        self._stats: Dict[MemoryType, Dict[str, Any]] = {
            MemoryType.PERSONALITY: {"count": 0, "size": 0},
            MemoryType.BEHAVIOR: {"count": 0, "size": 0},
            MemoryType.STRATEGY: {"count": 0, "size": 0},
            MemoryType.HISTORY: {"count": 0, "size": 0},
            MemoryType.RELATIONSHIP: {"count": 0, "size": 0},
            MemoryType.PROMPT: {"count": 0, "size": 0}
        }
        
    def initialize(self) -> None:
        """Inicjalizacja pamieci."""
        if self.base_path and not os.path.exists(self.base_path):
            os.makedirs(self.base_path, exist_ok=True)
            
    def add_entry(self, entry: MemoryEntry) -> str:
        """Dodanie nowego wpisu do pamieci."""
        entry_id = entry.entry_id
        memory_type = entry.memory_type
        
        # Wybor pamieci
        if memory_type == MemoryType.PERSONALITY:
            self._personality_memory[entry_id] = entry
            self._indexes[memory_type]["all"] = self._indexes[memory_type].get("all", []) + [entry_id]
            
        elif memory_type == MemoryType.BEHAVIOR:
            self._behavior_memory[entry_id] = entry
            self._indexes[memory_type]["all"] = self._indexes[memory_type].get("all", []) + [entry_id]
            
            # Indeksy po typie zachowania
            behavior_type = entry.behavior_type if hasattr(entry, 'behavior_type') else ""
            if behavior_type:
                self._indexes[memory_type][f"type:{behavior_type}"] = (
                    self._indexes[memory_type].get(f"type:{behavior_type}", []) + [entry_id]
                )
                
        elif memory_type == MemoryType.STRATEGY:
            self._strategy_memory[entry_id] = entry
            self._indexes[memory_type]["all"] = self._indexes[memory_type].get("all", []) + [entry_id]
            
            # Indeksy po nazwie strategii
            strategy_name = entry.strategy_name if hasattr(entry, 'strategy_name') else ""
            if strategy_name:
                self._indexes[memory_type][f"name:{strategy_name}"] = (
                    self._indexes[memory_type].get(f"name:{strategy_name}", []) + [entry_id]
                )
                
        elif memory_type == MemoryType.HISTORY:
            self._history_memory[entry_id] = entry
            self._indexes[memory_type]["all"] = self._indexes[memory_type].get("all", []) + [entry_id]
            
            # Indeksy po typie zdarzenia
            event_type = entry.event_type if hasattr(entry, 'event_type') else ""
            if event_type:
                self._indexes[memory_type][f"type:{event_type}"] = (
                    self._indexes[memory_type].get(f"type:{event_type}", []) + [entry_id]
                )
                
            # Indeksy po kategorii
            categories = entry.categories if hasattr(entry, 'categories') else []
            for category in categories:
                self._indexes[memory_type][f"category:{category}"] = (
                    self._indexes[memory_type].get(f"category:{category}", []) + [entry_id]
                )
                
        elif memory_type == MemoryType.RELATIONSHIP:
            self._relationship_memory[entry_id] = entry
            self._indexes[memory_type]["all"] = self._indexes[memory_type].get("all", []) + [entry_id]
            
            # Indeksy po agencie
            other_agent = entry.other_agent_id if hasattr(entry, 'other_agent_id') else ""
            if other_agent:
                self._indexes[memory_type][f"agent:{other_agent}"] = (
                    self._indexes[memory_type].get(f"agent:{other_agent}", []) + [entry_id]
                )
                
            # Indeksy po typie relacji
            rel_type = entry.relationship_type if hasattr(entry, 'relationship_type') else ""
            if rel_type:
                self._indexes[memory_type][f"type:{rel_type}"] = (
                    self._indexes[memory_type].get(f"type:{rel_type}", []) + [entry_id]
                )
                
        elif memory_type == MemoryType.PROMPT:
            self._prompt_memory[entry_id] = entry
            self._indexes[memory_type]["all"] = self._indexes[memory_type].get("all", []) + [entry_id]
            
            # Indeksy po typie promptu
            prompt_type = entry.prompt_type if hasattr(entry, 'prompt_type') else ""
            if prompt_type:
                self._indexes[memory_type][f"type:{prompt_type}"] = (
                    self._indexes[memory_type].get(f"type:{prompt_type}", []) + [entry_id]
                )
                
        # Aktualizacja statystyk
        self._stats[memory_type]["count"] += 1
        
        return entry_id
        
    def get_entry(self, entry_id: str, memory_type: Optional[Union[MemoryType, str]] = None) -> Optional[MemoryEntry]:
        """Pobranie wpisu o podanym ID.
        
        Args:
            entry_id: ID wpisu
            memory_type: MemoryType enum lub string (np. "personality"), opcjonalnie
        """
        # Obsluga stringa jako MemoryType
        if isinstance(memory_type, str):
            mem_type_enum = MemoryType.from_string(memory_type)
            if mem_type_enum is not None:
                memory_type = mem_type_enum
        
        if memory_type is None:
            # Szukanie we wszystkich typach pamieci
            for mem_type in self._get_all_entries().keys():
                entry = self.get_entry(entry_id, mem_type)
                if entry:
                    return entry
            return None
            
        if memory_type == MemoryType.PERSONALITY:
            return self._personality_memory.get(entry_id)
        elif memory_type == MemoryType.BEHAVIOR:
            return self._behavior_memory.get(entry_id)
        elif memory_type == MemoryType.STRATEGY:
            return self._strategy_memory.get(entry_id)
        elif memory_type == MemoryType.HISTORY:
            return self._history_memory.get(entry_id)
        elif memory_type == MemoryType.RELATIONSHIP:
            return self._relationship_memory.get(entry_id)
        elif memory_type == MemoryType.PROMPT:
            return self._prompt_memory.get(entry_id)
            
        return None
        
    def update_entry(self, entry_id: str, updates: Dict[str, Any], 
                    memory_type: Optional[Union[MemoryType, str]] = None) -> bool:
        """Aktualizacja wpisu.
        
        Args:
            entry_id: ID wpisu
            updates: Słownik z aktualizacjami
            memory_type: MemoryType enum lub string, opcjonalnie
        """
        entry = self.get_entry(entry_id, memory_type)
        if not entry:
            return False
            
        for key, value in updates.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
                
        entry.updated_at = datetime.now().isoformat()
        return True
        
    def delete_entry(self, entry_id: str, memory_type: Optional[Union[MemoryType, str]] = None) -> bool:
        """Usuniecie wpisu.
        
        Args:
            entry_id: ID wpisu
            memory_type: MemoryType enum lub string, opcjonalnie
        """
        entry = self.get_entry(entry_id, memory_type)
        if not entry:
            return False
            
        # Usuniecie z pamieci
        if memory_type == MemoryType.PERSONALITY:
            del self._personality_memory[entry_id]
        elif memory_type == MemoryType.BEHAVIOR:
            del self._behavior_memory[entry_id]
        elif memory_type == MemoryType.STRATEGY:
            del self._strategy_memory[entry_id]
        elif memory_type == MemoryType.HISTORY:
            del self._history_memory[entry_id]
        elif memory_type == MemoryType.RELATIONSHIP:
            del self._relationship_memory[entry_id]
        elif memory_type == MemoryType.PROMPT:
            del self._prompt_memory[entry_id]
        
        # Usuniecie z indeksow
        if memory_type:
            for index_key, entry_ids in self._indexes[memory_type].items():
                if entry_id in entry_ids:
                    entry_ids.remove(entry_id)
                    
        # Aktualizacja statystyk
        if memory_type:
            self._stats[memory_type]["count"] -= 1
            
        return True
        
    def query_entries(self, memory_type: Union[MemoryType, str], **filters) -> List[MemoryEntry]:
        """Zapytanie o wpisy z filtrowaniem.
        
        Args:
            memory_type: MemoryType enum lub string (np. "strategy")
        """
        # Obsluga stringa jako MemoryType
        if isinstance(memory_type, str):
            mem_type_enum = MemoryType.from_string(memory_type)
            if mem_type_enum is None:
                raise ValueError(f"Unknown memory type: {memory_type}")
            memory_type = mem_type_enum
        
        entries = list(self._get_memory(memory_type).values())
        
        # Filtrowanie
        for key, value in filters.items():
            if key == "tags":
                entries = [e for e in entries if any(tag in e.tags for tag in value)]
            elif key == "active":
                entries = [e for e in entries if e.active == value]
            elif hasattr(entries[0], key) if entries else False:
                entries = [e for e in entries if getattr(e, key) == value]
                
        return entries
        
    def query_by_index(self, memory_type: MemoryType, index_key: str) -> List[MemoryEntry]:
        """Zapytanie po indeksie."""
        entry_ids = self._indexes[memory_type].get(index_key, [])
        return [self.get_entry(eid, memory_type) for eid in entry_ids if self.get_entry(eid, memory_type)]
        
    def get_all_entries(self, memory_type: Optional[MemoryType] = None) -> Dict[str, List[MemoryEntry]]:
        """Pobranie wszystkich wpisow."""
        if memory_type:
            return {memory_type.value: list(self._get_memory(memory_type).values())}
        else:
            return {
                MemoryType.PERSONALITY.value: list(self._personality_memory.values()),
                MemoryType.BEHAVIOR.value: list(self._behavior_memory.values()),
                MemoryType.STRATEGY.value: list(self._strategy_memory.values()),
                MemoryType.HISTORY.value: list(self._history_memory.values()),
                MemoryType.RELATIONSHIP.value: list(self._relationship_memory.values()),
                MemoryType.PROMPT.value: list(self._prompt_memory.values())
            }
        
    def get_statistics(self, memory_type: Optional[Union[MemoryType, str]] = None) -> Dict[str, Any]:
        """Pobranie statystyk.
        
        Args:
            memory_type: MemoryType enum lub string (np. "personality", "behavior")
        """
        if memory_type:
            # Obsluga stringa jako MemoryType
            if isinstance(memory_type, str):
                try:
                    mem_type_enum = MemoryType(memory_type)
                    return self._stats[mem_type_enum]
                except ValueError:
                    # Jeśli string nie pasuje do enum, szukaj bezpośrednio w _stats
                    for mt in self._stats.keys():
                        if isinstance(mt, MemoryType) and mt.value == memory_type:
                            return self._stats[mt]
                    return {"count": 0, "size": 0}
            return self._stats[memory_type]
        else:
            result = {}
            for mt, stats in self._stats.items():
                # mt moze byc MemoryType lub string
                key = mt.value if isinstance(mt, MemoryType) else mt
                result[key] = stats
            return result
        
    def clear_memory(self, memory_type: Optional[MemoryType] = None) -> None:
        """Wyczyszczenie pamieci."""
        if memory_type is None:
            # Wyczyszczenie wszystkiego
            self._personality_memory.clear()
            self._behavior_memory.clear()
            self._strategy_memory.clear()
            self._history_memory.clear()
            self._relationship_memory.clear()
            self._prompt_memory.clear()
            
            self._indexes = {
                MemoryType.PERSONALITY: {},
                MemoryType.BEHAVIOR: {},
                MemoryType.STRATEGY: {},
                MemoryType.HISTORY: {},
                MemoryType.RELATIONSHIP: {},
                MemoryType.PROMPT: {}
            }
            
            for mt in self._stats.keys():
                self._stats[mt]["count"] = 0
                self._stats[mt]["size"] = 0
                
        else:
            # Wyczyszczenie pojedynczego typu
            self._get_memory(memory_type).clear()
            self._indexes[memory_type] = {}
            self._stats[memory_type]["count"] = 0
            self._stats[memory_type]["size"] = 0
            
    def _get_memory(self, memory_type: MemoryType) -> Dict[str, MemoryEntry]:
        """Pobranie odpowiedniej pamieci."""
        if memory_type == MemoryType.PERSONALITY:
            return self._personality_memory
        elif memory_type == MemoryType.BEHAVIOR:
            return self._behavior_memory
        elif memory_type == MemoryType.STRATEGY:
            return self._strategy_memory
        elif memory_type == MemoryType.HISTORY:
            return self._history_memory
        elif memory_type == MemoryType.RELATIONSHIP:
            return self._relationship_memory
        elif memory_type == MemoryType.PROMPT:
            return self._prompt_memory
            
    def save_to_disk(self) -> bool:
        """Zapis pamieci do pliku."""
        if not self.base_path:
            return False
            
        try:
            os.makedirs(self.base_path, exist_ok=True)
            
            # Zapis kazdego typu pamieci
            for mem_type in [MemoryType.PERSONALITY, MemoryType.BEHAVIOR, MemoryType.STRATEGY,
                            MemoryType.HISTORY, MemoryType.RELATIONSHIP, MemoryType.PROMPT]:
                
                mem_name = mem_type.value
                mem_data = list(self._get_memory(mem_type).values())
                
                if mem_data:
                    # Konwersja do serializowalnego formatu
                    serializable_data = []
                    for entry in mem_data:
                        entry_dict = asdict(entry)
                        # Konwersja enumow
                        if 'memory_type' in entry_dict:
                            # Upewnij sie ze memory_type to enum
                            mem_type_val = entry_dict['memory_type']
                            if isinstance(mem_type_val, MemoryType):
                                entry_dict['memory_type'] = mem_type_val.value
                            elif isinstance(mem_type_val, str):
                                entry_dict['memory_type'] = mem_type_val
                        serializable_data.append(entry_dict)
                        
                    # Zapis
                    filepath = os.path.join(self.base_path, f"{mem_name}.json")
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(serializable_data, f, indent=4, ensure_ascii=False)
                        
            # Zapis indeksow
            indexes_path = os.path.join(self.base_path, "indexes.json")
            with open(indexes_path, 'w', encoding='utf-8') as f:
                json.dump(self._indexes, f, indent=4, ensure_ascii=False)
                
            # Zapis statystyk
            stats_path = os.path.join(self.base_path, "stats.json")
            with open(stats_path, 'w', encoding='utf-8') as f:
                json.dump(self._stats, f, indent=4, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"Error saving memory to disk: {e}")
            return False
            
    def load_from_disk(self) -> bool:
        """Zaladowanie pamieci z dysku."""
        if not self.base_path or not os.path.exists(self.base_path):
            return False
            
        try:
            # Odczyt kazdego typu pamieci
            for mem_type in [MemoryType.PERSONALITY, MemoryType.BEHAVIOR, MemoryType.STRATEGY,
                            MemoryType.HISTORY, MemoryType.RELATIONSHIP, MemoryType.PROMPT]:
                
                mem_name = mem_type.value
                filepath = os.path.join(self.base_path, f"{mem_name}.json")
                
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    for entry_data in data:
                        # Upewnij sie ze pole 'data' istnieje
                        if 'data' not in entry_data:
                            entry_data['data'] = {}
                        
                        # Usuwamy pole memory_type z entry_data, poniewaz jest ustawiane w __post_init__
                        # i klasy dziedzicza po MemoryType
                        entry_data_copy = entry_data.copy()
                        entry_data_copy.pop('memory_type', None)
                        
                        # Obsluga pol wymaganych - dodaj domyslne wartosci jeśli brakuje
                        if 'entry_id' not in entry_data_copy:
                            entry_data_copy['entry_id'] = f"{mem_type.value}_default"
                        if 'created_at' not in entry_data_copy:
                            entry_data_copy['created_at'] = datetime.now().isoformat()
                        if 'updated_at' not in entry_data_copy:
                            entry_data_copy['updated_at'] = datetime.now().isoformat()
                            
                        # Tworzenie wpisu
                        entry_class = self._get_entry_class(mem_type)
                        try:
                            entry = entry_class(**entry_data_copy)
                            self.add_entry(entry)
                        except TypeError as e:
                            # Dodatkowa obsluga - moze byc problem z brakujacymi polami
                            error_msg = str(e)
                            if 'missing' in error_msg.lower() or 'required' in error_msg.lower():
                                # Wyciagnij nazwe brakujacego pola
                                import re
                                match = re.search(r"missing.*?['\"](\w+)['\"]", error_msg)
                                if match:
                                    missing_field = match.group(1)
                                    entry_data_copy[missing_field] = {}
                                    try:
                                        entry = entry_class(**entry_data_copy)
                                        self.add_entry(entry)
                                    except Exception as e2:
                                        print(f"Error creating entry for {mem_type.value} after fix: {e2}")
                                        print(f"Entry data: {entry_data_copy}")
                                        continue
                            print(f"Error creating entry for {mem_type.value}: {e}")
                            print(f"Entry data: {entry_data_copy}")
                            continue
                        except Exception as e:
                            print(f"Error creating entry for {mem_type.value}: {e}")
                            print(f"Entry data: {entry_data_copy}")
                            continue
                        
            # Odczyt indeksow
            indexes_path = os.path.join(self.base_path, "indexes.json")
            if os.path.exists(indexes_path):
                with open(indexes_path, 'r', encoding='utf-8') as f:
                    self._indexes = json.load(f)
                    
            # Odczyt statystyk
            stats_path = os.path.join(self.base_path, "stats.json")
            if os.path.exists(stats_path):
                with open(stats_path, 'r', encoding='utf-8') as f:
                    self._stats = json.load(f)
                    
            return True
            
        except Exception as e:
            print(f"Error loading memory from disk: {e}")
            return False
            
    def _get_entry_class(self, memory_type: MemoryType) -> type:
        """Pobranie klasy wpisu dla danego typu pamieci."""
        mapping = {
            MemoryType.PERSONALITY: PersonalityMemoryEntry,
            MemoryType.BEHAVIOR: BehaviorMemoryEntry,
            MemoryType.STRATEGY: StrategyMemoryEntry,
            MemoryType.HISTORY: HistoryMemoryEntry,
            MemoryType.RELATIONSHIP: RelationshipMemoryEntry,
            MemoryType.PROMPT: PromptMemoryEntry
        }
        return mapping.get(memory_type, MemoryEntry)


def create_agent_memory_store(agent_id: str, base_path: str = "") -> AgentMemoryStore:
    """Tworzenie pamieci agenta."""
    return AgentMemoryStore(agent_id, base_path)


if __name__ == "__main__":
    # Test pamieci agenta
    print("Testing Agent Memory Store...")
    
    store = create_agent_memory_store("01", "D:\\sts\\aplikacjaTyperBetAi\\SSI\\memory\\agents\\agent_01")
    store.initialize()
    
    # dodawanie nowej osobnosci
    personality = PersonalityMemoryEntry(
        entry_id="personality_001",
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        risk=0.5,
        analysis=0.8,
        creativity=0.5,
        trust_v2=0.8,
        trust_v3=0.8,
        trust_v4=0.8,
        trust_external=0.6,
        agent_type="balanced",
        description="Initial personality configuration"
    )
    
    store.add_entry(personality)
    print(f"Added personality entry. Total: {store.get_statistics(MemoryType.PERSONALITY)['count']}")
    
    # dodawanie strategii
    strategy = StrategyMemoryEntry(
        entry_id="strategy_001",
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        strategy_name="analytical",
        strategy_type="analytical",
        description="Analytical strategy for data-driven decisions",
        times_used=0,
        times_successful=0
    )
    
    store.add_entry(strategy)
    print(f"Added strategy entry. Total: {store.get_statistics(MemoryType.STRATEGY)['count']}")
    
    # compositions
    entries = store.get_all_entries()
    print(f"Total entries across all memory types: {sum(len(v) for v in entries.values())}")
    
    # Test zapisu i odczytu
    if store.save_to_disk():
        print("✓ Memory saved to disk")
    
    new_store = create_agent_memory_store("01", "D:\\sts\\aplikacjaTyperBetAi\\SSI\\memory\\agents\\agent_01")
    if new_store.load_from_disk():
        print("✓ Memory loaded from disk")
        stats = new_store.get_statistics()
        print(f"Loaded statistics: {stats}")
    
    print("Agent Memory Store test completed!")