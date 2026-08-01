"""
SSI V5 - Model Memory Store
Glowny storage pamieci modeli

Zgodnie z dokumentacja:
- 04_AGENT_MEMORY_BEHAVIOR_EVOLUTION.md Sekcja: Model Memory Ecosystem
- 01_SYSTEM_SIGNAL_ARCHITECTURE.md (Information Flow)

System przechowuje 5 typow pamieci:
1. Training Memory: Pamiec tresowania i uczenia
2. Observation Memory: Pamiec obserwacji systemu i agentow
3. Behavior Memory: Pamiec zachowan i wzorcow
4. Agent Analysis Memory: Pamiec analiz agentow
5. Decision Layer Memory: Pamiec podejmowanych decyzji

Kazdy typ pamieci jest sprawdzony w oddzielnym pliku JSON.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Union, Type, TypeVar
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
import threading
import uuid

# Dodanie sciezki do SSI do sys.path
SSI_PATH = "D:\\sts\\aplikacjaTyperBetAi\\SSI"
if SSI_PATH not in sys.path:
    sys.path.insert(0, SSI_PATH)

from .memory_types import (
    TrainingMemory,
    ObservationMemory,
    BehaviorMemory,
    AgentAnalysisMemory,
    DecisionMemory,
    TrainingPhase,
    ObservationScope,
    BehaviorType,
    AnalysisType
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ModelMemoryType(Enum):
    """Typy pamieci modeli."""
    TRAINING = auto()       # Pamiec tresowania
    OBSERVATION = auto()    # Pamiec obserwacji
    BEHAVIOR = auto()       # Pamiec zachowan
    AGENT_ANALYSIS = auto() # Pamiec analiz agentow
    DECISION = auto()       # Pamiec decyzji
    
    @property
    def filename(self) -> str:
        """Nazwa pliku dla danego typu pamieci."""
        return f"{self.name.lower()}_memory.json"
    
    @property
    def class_type(self) -> Type:
        """Klasa odpowiadajaca typowi pamieci."""
        mapping = {
            ModelMemoryType.TRAINING: TrainingMemory,
            ModelMemoryType.OBSERVATION: ObservationMemory,
            ModelMemoryType.BEHAVIOR: BehaviorMemory,
            ModelMemoryType.AGENT_ANALYSIS: AgentAnalysisMemory,
            ModelMemoryType.DECISION: DecisionMemory
        }
        return mapping.get(self, TrainingMemory)


@dataclass
class MemoryStatistics:
    """Statystyki pamieci modeli."""
    
    # Liczniki
    entry_count: int = 0
    
    # Per typ pamieci
    by_type: Dict[str, int] = field(default_factory=dict)
    
    # Czas
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    last_accessed: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Rozmiar
    total_size_bytes: int = 0
    by_type_size: Dict[str, int] = field(default_factory=dict)
    
    # Wersje
    version: str = "1.0.0"


class ModelMemoryStore:
    """Glowny storage pamieci modeli.
    
    Odpowiedzialnosc:
    - Przechowywanie 5 typow pamieci
    - Zapis i odczyt z plikow JSON
    - Zarzadzanie wersjami
    - Statystyki uzycia
    
    Uzycie:
        store = create_model_memory_store(base_path="./memory")
        store.initialize()
        
        # Dodawanie
        store.add_training_memory(training_session)
        store.add_observation_memory(observation)
        
        # Pobieranie
        trainings = store.get_all_training_memory()
        observations = store.get_observations_by_agent("01")
        
        # Zapis
        store.save_all()
    """
    
    def __init__(self, base_path: str):
        """Inicjalizacja storage."""
        self.base_path = os.path.abspath(base_path)
        os.makedirs(self.base_path, exist_ok=True)
        
        # Pamiec podzielona na typy
        self._training_memory: Dict[str, TrainingMemory] = {}
        self._observation_memory: Dict[str, ObservationMemory] = {}
        self._behavior_memory: Dict[str, BehaviorMemory] = {}
        self._agent_analysis_memory: Dict[str, AgentAnalysisMemory] = {}
        self._decision_memory: Dict[str, DecisionMemory] = {}
        
        # Statystyki
        self._statistics = MemoryStatistics()
        
        # Locki dla thread-safety
        self._lock = threading.RLock()
        self._file_lock = threading.RLock()
        
        # Flag
        self._initialized = False
        self._loaded = False
        
        # Sciezki do plikow
        self._file_paths = {
            ModelMemoryType.TRAINING: os.path.join(self.base_path, ModelMemoryType.TRAINING.filename),
            ModelMemoryType.OBSERVATION: os.path.join(self.base_path, ModelMemoryType.OBSERVATION.filename),
            ModelMemoryType.BEHAVIOR: os.path.join(self.base_path, ModelMemoryType.BEHAVIOR.filename),
            ModelMemoryType.AGENT_ANALYSIS: os.path.join(self.base_path, ModelMemoryType.AGENT_ANALYSIS.filename),
            ModelMemoryType.DECISION: os.path.join(self.base_path, ModelMemoryType.DECISION.filename)
        }
    
    def initialize(self) -> bool:
        """Inicjalizacja storage."""
        try:
            with self._lock:
                # Zaladowanie istniejacych danych
                self._load_all()
                self._initialized = True
                self._loaded = True
                
                logger.info(f"Model Memory Store initialized at {self.base_path}")
                return True
        except Exception as e:
            logger.error(f"Error initializing ModelMemoryStore: {e}")
            return False
    
    def _load_all(self) -> None:
        """Zaladowanie wszystkich typow pamieci z plikow."""
        with self._file_lock:
            for mem_type in ModelMemoryType:
                self._load_memory_type(mem_type)
    
    def _load_memory_type(self, mem_type: ModelMemoryType) -> None:
        """Zaladowanie konkretnego typu pamieci."""
        file_path = self._file_paths[mem_type]
        
        if not os.path.exists(file_path):
            logger.debug(f"No {mem_type.name} memory file found at {file_path}")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            entries = data.get("entries", {})
            cls = mem_type.class_type
            
            for entry_id, entry_data in entries.items():
                try:
                    entry = cls.from_dict(entry_data)
                    self._add_entry_to_memory(mem_type, entry_id, entry)
                except Exception as e:
                    logger.warning(f"Error loading {mem_type.name} entry {entry_id}: {e}")
            
            # Statystyki
            self._statistics.by_type[mem_type.name.lower()] = len(entries)
            self._statistics.entry_count += len(entries)
            self._statistics.last_updated = data.get("updated_at", datetime.now().isoformat())
            
            logger.info(f"Loaded {len(entries)} {mem_type.name} memory entries")
            
        except Exception as e:
            logger.error(f"Error loading {mem_type.name} memory from {file_path}: {e}")
    
    def _add_entry_to_memory(self, mem_type: ModelMemoryType, entry_id: str, entry) -> None:
        """Dodanie wpisu do odpowiedniego typu pamieci."""
        if mem_type == ModelMemoryType.TRAINING:
            self._training_memory[entry_id] = entry
        elif mem_type == ModelMemoryType.OBSERVATION:
            self._observation_memory[entry_id] = entry
        elif mem_type == ModelMemoryType.BEHAVIOR:
            self._behavior_memory[entry_id] = entry
        elif mem_type == ModelMemoryType.AGENT_ANALYSIS:
            self._agent_analysis_memory[entry_id] = entry
        elif mem_type == ModelMemoryType.DECISION:
            self._decision_memory[entry_id] = entry
        
        # Aktualizacja statystyk
        self._statistics.by_type[mem_type.name.lower()] = \
            self._statistics.by_type.get(mem_type.name.lower(), 0) + 1
        self._statistics.entry_count += 1
        self._statistics.last_updated = datetime.now().isoformat()
        self._statistics.last_accessed = datetime.now().isoformat()
    
    def save_all(self) -> bool:
        """Zapisanie wszystkich typow pamieci do plikow."""
        with self._file_lock:
            success = True
            for mem_type in ModelMemoryType:
                if not self._save_memory_type(mem_type):
                    success = False
            
            if success:
                logger.info("All model memory saved")
            else:
                logger.error("Some model memory failed to save")
            
            return success
    
    def _save_memory_type(self, mem_type: ModelMemoryType) -> bool:
        """Zapisanie konkretnego typu pamieci."""
        file_path = self._file_paths[mem_type]
        
        try:
            # Pobranie wpisow
            entries = self._get_entries_for_type(mem_type)
            
            # Serializacja
            data = {
                "version": "1.0.0",
                "type": mem_type.name,
                "updated_at": datetime.now().isoformat(),
                "created_at": self._statistics.created_at,
                "entry_count": len(entries),
                "entries": {}
            }
            
            for entry_id, entry in entries.items():
                try:
                    data["entries"][entry_id] = entry.to_dict()
                except Exception as e:
                    logger.warning(f"Error serializing {mem_type.name} entry {entry_id}: {e}")
            
            # Zapis
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(entries)} {mem_type.name} memory entries to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving {mem_type.name} memory to {file_path}: {e}")
            return False
    
    def _get_entries_for_type(self, mem_type: ModelMemoryType) -> Dict[str, Any]:
        """Pobranie wpisow dla danego typu pamieci."""
        if mem_type == ModelMemoryType.TRAINING:
            return self._training_memory
        elif mem_type == ModelMemoryType.OBSERVATION:
            return self._observation_memory
        elif mem_type == ModelMemoryType.BEHAVIOR:
            return self._behavior_memory
        elif mem_type == ModelMemoryType.AGENT_ANALYSIS:
            return self._agent_analysis_memory
        elif mem_type == ModelMemoryType.DECISION:
            return self._decision_memory
        return {}
    
    # ==================== TRAINING MEMORY ====================
    
    def add_training_memory(self, entry: TrainingMemory) -> str:
        """Dodanie wpisu pamieci tresowania."""
        with self._lock:
            if not self._initialized:
                self.initialize()
            
            entry_id = entry.session_id
            self._training_memory[entry_id] = entry
            self._statistics.by_type["training"] = self._statistics.by_type.get("training", 0) + 1
            self._statistics.entry_count += 1
            self._statistics.last_updated = datetime.now().isoformat()
            
            logger.info(f"Added training memory: {entry_id}")
            return entry_id
    
    def get_training_memory(self, session_id: str) -> Optional[TrainingMemory]:
        """Pobranie konkretnego wpisu tresowania."""
        with self._lock:
            self._statistics.last_accessed = datetime.now().isoformat()
            return self._training_memory.get(session_id)
    
    def get_all_training_memory(self) -> Dict[str, TrainingMemory]:
        """Pobranie wszystkich wpisow tresowania."""
        with self._lock:
            self._statistics.last_accessed = datetime.now().isoformat()
            return self._training_memory.copy()
    
    def get_training_sessions_by_model(self, model_name: str) -> Dict[str, TrainingMemory]:
        """Pobranie sesji tresowania dla konkretnego modelu."""
        with self._lock:
            self._statistics.last_accessed = datetime.now().isoformat()
            return {k: v for k, v in self._training_memory.items() if v.model_name == model_name}
    
    def update_training_memory(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Aktualizacja wpisu tresowania."""
        with self._lock:
            if session_id not in self._training_memory:
                return False
            
            entry = self._training_memory[session_id]
            for key, value in updates.items():
                if hasattr(entry, key):
                    setattr(entry, key, value)
            
            entry.updated_at = datetime.now().isoformat()
            self._statistics.last_updated = datetime.now().isoformat()
            logger.info(f"Updated training memory: {session_id}")
            return True
    
    # ==================== OBSERVATION MEMORY ====================
    
    def add_observation_memory(self, entry: ObservationMemory) -> str:
        """Dodanie wpisu pamieci obserwacji."""
        with self._lock:
            if not self._initialized:
                self.initialize()
            
            entry_id = entry.observation_id
            self._observation_memory[entry_id] = entry
            self._statistics.by_type["observation"] = self._statistics.by_type.get("observation", 0) + 1
            self._statistics.entry_count += 1
            self._statistics.last_updated = datetime.now().isoformat()
            
            logger.info(f"Added observation memory: {entry_id}")
            return entry_id
    
    def get_observation_memory(self, observation_id: str) -> Optional[ObservationMemory]:
        """Pobranie konkretnej obserwacji."""
        with self._lock:
            self._statistics.last_accessed = datetime.now().isoformat()
            return self._observation_memory.get(observation_id)
    
    def get_all_observation_memory(self) -> Dict[str, ObservationMemory]:
        """Pobranie wszystkich obserwacji."""
        with self._lock:
            self._statistics.last_accessed = datetime.now().isoformat()
            return self._observation_memory.copy()
    
    def get_observations_by_agent(self, agent_id: str) -> Dict[str, ObservationMemory]:
        """Pobranie obserwacji dla konkretnego agenta."""
        with self._lock:
            self._statistics.last_accessed = datetime.now().isoformat()
            return {k: v for k, v in self._observation_memory.items() if v.target_id == agent_id}
    
    def get_observations_by_scope(self, scope: ObservationScope) -> Dict[str, ObservationMemory]:
        """Pobranie obserwacji według zakresu."""
        with self._lock:
            self._statistics.last_accessed = datetime.now().isoformat()
            return {k: v for k, v in self._observation_memory.items() if v.scope == scope}
    
    def get_recent_observations(self, hours: int = 24) -> Dict[str, ObservationMemory]:
        """Pobranie niedawnych obserwacji."""
        from datetime import timedelta
        with self._lock:
            self._statistics.last_accessed = datetime.now().isoformat()
            cutoff = datetime.now() - timedelta(hours=hours)
            return {k: v for k, v in self._observation_memory.items() 
                    if datetime.fromisoformat(v.timestamp) >= cutoff}
    
    # ==================== BEHAVIOR MEMORY ====================
    
    def add_behavior_memory(self, entry: BehaviorMemory) -> str:
        """Dodanie wpisu pamieci zachowan."""
        with self._lock:
            if not self._initialized:
                self.initialize()
            
            entry_id = entry.behavior_id
            self._behavior_memory[entry_id] = entry
            self._statistics.by_type["behavior"] = self._statistics.by_type.get("behavior", 0) + 1
            self._statistics.entry_count += 1
            self._statistics.last_updated = datetime.now().isoformat()
            
            logger.info(f"Added behavior memory: {entry_id}")
            return entry_id
    
    def get_behavior_memory(self, behavior_id: str) -> Optional[BehaviorMemory]:
        """Pobranie konkretnego zachowania."""
        with self._lock:
            self._statistics.last_accessed = datetime.now().isoformat()
            return self._behavior_memory.get(behavior_id)
    
    def get_all_behavior_memory(self) -> Dict[str, BehaviorMemory]:
        """Pobranie wszystkich zachowan."""
        with self._lock:
            self._statistics.last_accessed = datetime.now().isoformat()
            return self._behavior_memory.copy()
    
    def get_behaviors_by_agent(self, agent_id: str) -> Dict[str, BehaviorMemory]:
        """Pobranie zachowan dla konkretnego agenta."""
        with self._lock:
            self._statistics.last_accessed = datetime.now().isoformat()
            return {k: v for k, v in self._behavior_memory.items() if agent_id in v.agent_ids}
    
    def get_behaviors_by_type(self, behavior_type: BehaviorType) -> Dict[str, BehaviorMemory]:
        """Pobranie zachowan według typu."""
        with self._lock:
            self._statistics.last_accessed = datetime.now().isoformat()
            return {k: v for k, v in self._behavior_memory.items() if v.behavior_type == behavior_type}
    
    def get_stable_behaviors(self) -> Dict[str, BehaviorMemory]:
        """Pobranie stabilnych zachowan."""
        with self._lock:
            self._statistics.last_accessed = datetime.now().isoformat()
            return {k: v for k, v in self._behavior_memory.items() if v.is_stable}
    
    # ==================== AGENT ANALYSIS MEMORY ====================
    
    def add_agent_analysis_memory(self, entry: AgentAnalysisMemory) -> str:
        """Dodanie wpisu pamieci analiz agentow."""
        with self._lock:
            if not self._initialized:
                self.initialize()
            
            entry_id = entry.analysis_id
            self._agent_analysis_memory[entry_id] = entry
            self._statistics.by_type["agent_analysis"] = self._statistics.by_type.get("agent_analysis", 0) + 1
            self._statistics.entry_count += 1
            self._statistics.last_updated = datetime.now().isoformat()
            
            logger.info(f"Added agent analysis memory: {entry_id}")
            return entry_id
    
    def get_agent_analysis_memory(self, analysis_id: str) -> Optional[AgentAnalysisMemory]:
        """Pobranie konkretnej analizy agenta."""
        with self._lock:
            self._statistics.last_accessed = datetime.now().isoformat()
            return self._agent_analysis_memory.get(analysis_id)
    
    def get_all_agent_analysis_memory(self) -> Dict[str, AgentAnalysisMemory]:
        """Pobranie wszystkich analiz agentow."""
        with self._lock:
            self._statistics.last_accessed = datetime.now().isoformat()
            return self._agent_analysis_memory.copy()
    
    def get_analyses_by_agent(self, agent_id: str) -> Dict[str, AgentAnalysisMemory]:
        """Pobranie analiz dla konkretnego agenta."""
        with self._lock:
            self._statistics.last_accessed = datetime.now().isoformat()
            return {k: v for k, v in self._agent_analysis_memory.items() if v.agent_id == agent_id}
    
    def get_recent_analyses(self, agent_id: str, count: int = 5) -> List[AgentAnalysisMemory]:
        """Pobranie niedawnych analiz dla agenta."""
        with self._lock:
            self._statistics.last_accessed = datetime.now().isoformat()
            analyses = [v for v in self._agent_analysis_memory.values() if v.agent_id == agent_id]
            analyses.sort(key=lambda x: x.analysis_timestamp, reverse=True)
            return analyses[:count]
    
    def get_agent_ranking(self, agent_id: str, analysis_type: AnalysisType) -> Dict[str, float]:
        """Pobranie rankingu agenta."""
        with self._lock:
            self._statistics.last_accessed = datetime.now().isoformat()
            analyses = [v for v in self._agent_analysis_memory.values() 
                       if v.agent_id == agent_id and v.analysis_type == analysis_type]
            
            if analyses:
                return analyses[-1].ranking  # Najnowsza analiza
            return {}
    
    # ==================== DECISION MEMORY ====================
    
    def add_decision_memory(self, entry: DecisionMemory) -> str:
        """Dodanie wpisu pamieci decyzji."""
        with self._lock:
            if not self._initialized:
                self.initialize()
            
            entry_id = entry.decision_id
            self._decision_memory[entry_id] = entry
            self._statistics.by_type["decision"] = self._statistics.by_type.get("decision", 0) + 1
            self._statistics.entry_count += 1
            self._statistics.last_updated = datetime.now().isoformat()
            
            logger.info(f"Added decision memory: {entry_id}")
            return entry_id
    
    def get_decision_memory(self, decision_id: str) -> Optional[DecisionMemory]:
        """Pobranie konkretnej decyzji."""
        with self._lock:
            self._statistics.last_accessed = datetime.now().isoformat()
            return self._decision_memory.get(decision_id)
    
    def get_all_decision_memory(self) -> Dict[str, DecisionMemory]:
        """Pobranie wszystkich decyzji."""
        with self._lock:
            self._statistics.last_accessed = datetime.now().isoformat()
            return self._decision_memory.copy()
    
    def get_decisions_by_agent(self, agent_id: str) -> Dict[str, DecisionMemory]:
        """Pobranie decyzji dla konkretnego agenta."""
        with self._lock:
            self._statistics.last_accessed = datetime.now().isoformat()
            return {k: v for k, v in self._decision_memory.items() if v.agent_id == agent_id}
    
    def get_decisions_by_cycle(self, cycle_number: int) -> Dict[str, DecisionMemory]:
        """Pobranie decyzji dla konkretnego cyklu."""
        with self._lock:
            self._statistics.last_accessed = datetime.now().isoformat()
            return {k: v for k, v in self._decision_memory.items() if v.cycle_number == cycle_number}
    
    def get_successful_decisions(self, agent_id: Optional[str] = None) -> List[DecisionMemory]:
        """Pobranie powodzonych decyzji."""
        with self._lock:
            self._statistics.last_accessed = datetime.now().isoformat()
            decisions = list(self._decision_memory.values())
            
            if agent_id:
                decisions = [d for d in decisions if d.agent_id == agent_id]
            
            return [d for d in decisions if d.success]
    
    def get_decision_outcome_accuracy(self, agent_id: str) -> float:
        """Pobranie sredniej dokladnosci przewidywanych skutkow dla agenta."""
        with self._lock:
            self._statistics.last_accessed = datetime.now().isoformat()
            decisions = [v for v in self._decision_memory.values() 
                        if v.agent_id == agent_id and v.expected_outcomes and v.actual_outcomes]
            
            if not decisions:
                return 0.0
            
            accuracies = [d.outcome_accuracy for d in decisions]
            return sum(accuracies) / len(accuracies)
    
    # ==================== GENERIC METHODS ====================
    
    def add_entry(self, mem_type: ModelMemoryType, entry) -> str:
        """Dodanie wpisu dowolnego typu pamieci."""
        methods = {
            ModelMemoryType.TRAINING: self.add_training_memory,
            ModelMemoryType.OBSERVATION: self.add_observation_memory,
            ModelMemoryType.BEHAVIOR: self.add_behavior_memory,
            ModelMemoryType.AGENT_ANALYSIS: self.add_agent_analysis_memory,
            ModelMemoryType.DECISION: self.add_decision_memory
        }
        
        method = methods.get(mem_type)
        if method:
            return method(entry)
        raise ValueError(f"Unknown memory type: {mem_type}")
    
    def get_entry(self, mem_type: ModelMemoryType, entry_id: str):
        """Pobranie wpisu dowolnego typu pamieci."""
        methods = {
            ModelMemoryType.TRAINING: self.get_training_memory,
            ModelMemoryType.OBSERVATION: self.get_observation_memory,
            ModelMemoryType.BEHAVIOR: self.get_behavior_memory,
            ModelMemoryType.AGENT_ANALYSIS: self.get_agent_analysis_memory,
            ModelMemoryType.DECISION: self.get_decision_memory
        }
        
        method = methods.get(mem_type)
        if method:
            return method(entry_id)
        raise ValueError(f"Unknown memory type: {mem_type}")
    
    def get_all_entries(self, mem_type: ModelMemoryType) -> Dict[str, Any]:
        """Pobranie wszystkich wpisow danego typu pamieci."""
        methods = {
            ModelMemoryType.TRAINING: self.get_all_training_memory,
            ModelMemoryType.OBSERVATION: self.get_all_observation_memory,
            ModelMemoryType.BEHAVIOR: self.get_all_behavior_memory,
            ModelMemoryType.AGENT_ANALYSIS: self.get_all_agent_analysis_memory,
            ModelMemoryType.DECISION: self.get_all_decision_memory
        }
        
        method = methods.get(mem_type)
        if method:
            return method()
        raise ValueError(f"Unknown memory type: {mem_type}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Pobranie statystyk pamieci."""
        with self._lock:
            return {
                "entry_count": self._statistics.entry_count,
                "by_type": self._statistics.by_type,
                "created_at": self._statistics.created_at,
                "last_updated": self._statistics.last_updated,
                "last_accessed": self._statistics.last_accessed,
                "initialized": self._initialized,
                "loaded": self._loaded
            }
    
    def clear_memory(self, mem_type: Optional[ModelMemoryType] = None) -> None:
        """Wyczyszczenie pamieci."""
        with self._lock:
            if mem_type is None:
                # Wyczyszczenie wszystkiego
                self._training_memory.clear()
                self._observation_memory.clear()
                self._behavior_memory.clear()
                self._agent_analysis_memory.clear()
                self._decision_memory.clear()
                self._statistics = MemoryStatistics()
            else:
                # Wyczyszczenie konkretnego typu
                if mem_type == ModelMemoryType.TRAINING:
                    self._training_memory.clear()
                elif mem_type == ModelMemoryType.OBSERVATION:
                    self._observation_memory.clear()
                elif mem_type == ModelMemoryType.BEHAVIOR:
                    self._behavior_memory.clear()
                elif mem_type == ModelMemoryType.AGENT_ANALYSIS:
                    self._agent_analysis_memory.clear()
                elif mem_type == ModelMemoryType.DECISION:
                    self._decision_memory.clear()
                
                self._statistics.by_type[mem_type.name.lower()] = 0
                self._statistics.entry_count = sum(self._statistics.by_type.values())
            
            logger.info(f"Cleared {'all' if mem_type is None else mem_type.name} memory")
    
    def search(self, query: str, mem_type: Optional[ModelMemoryType] = None) -> Dict[str, Any]:
        """Wyszukiwanie w pamieci.
        
        Uproszczone wyszukiwanie po ID, nazwie, opisie itp.
        """
        results = {}
        query_lower = query.lower()
        
        with self._lock:
            entries_to_search = []
            
            if mem_type is None:
                entries_to_search.extend(self._training_memory.items())
                entries_to_search.extend(self._observation_memory.items())
                entries_to_search.extend(self._behavior_memory.items())
                entries_to_search.extend(self._agent_analysis_memory.items())
                entries_to_search.extend(self._decision_memory.items())
            else:
                entries = self.get_all_entries(mem_type)
                entries_to_search = list(entries.items())
            
            for entry_id, entry in entries_to_search:
                entry_dict = entry.to_dict()
                for key, value in entry_dict.items():
                    if isinstance(value, str) and query_lower in value.lower():
                        results[entry_id] = entry
                        break
        
        return results


# Singletony i fabryki

_default_store: Optional[ModelMemoryStore] = None
default_store_lock = threading.Lock()


def create_model_memory_store(base_path: str = "data/model_memory") -> ModelMemoryStore:
    """Tworzenie nowego storagu pamieci modeli.
    
    Args:
        base_path: Sciezka bazowa do plikow pamieci
        
    Returns:
        ModelMemoryStore
    """
    store = ModelMemoryStore(base_path=base_path)
    store.initialize()
    return store


def get_model_memory_store(base_path: str = "data/model_memory") -> ModelMemoryStore:
    """Pobranie instancji storagu (singleton).
    
    Args:
        base_path: Sciezka bazowa do plikow pamieci
        
    Returns:
        ModelMemoryStore (singleton)
    """
    global _default_store
    
    with default_store_lock:
        if _default_store is None:
            _default_store = create_model_memory_store(base_path)
        return _default_store


# Typy danych pamieci (dla kompatybilnosci z agent_memory_store)

@dataclass
class TrainingMemoryEntry:
    """Wpis pamieci tresowania (kompatybilnosc)."""
    entry_id: str = field(default_factory=lambda: f"training_{uuid.uuid4().hex[:12]}")
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Training-specific
    session_id: str = ""
    phase: str = "continuous"
    model_name: str = ""
    metrics: Dict[str, float] = field(default_factory=dict)
    
    def to_training_memory(self) -> TrainingMemory:
        """Konwersja do TrainingMemory."""
        return TrainingMemory(
            session_id=self.session_id or self.entry_id,
            start_time=self.created_at,
            end_time=None,
            phase=TrainingPhase[self.phase.upper()] if self.phase else TrainingPhase.CONTINUOUS,
            model_name=self.model_name,
            metrics=self.metrics,
            context=self.data
        )


@dataclass
class ObservationMemoryEntry:
    """Wpis pamieci obserwacji (kompatybilnosc)."""
    entry_id: str = field(default_factory=lambda: f"obs_{uuid.uuid4().hex[:12]}")
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Observation-specific
    observation_type: str = "behavior"
    scope: str = "system"
    target_id: str = ""
    patterns: List[str] = field(default_factory=list)
    anomalies: List[str] = field(default_factory=list)
    
    def to_observation_memory(self) -> ObservationMemory:
        """Konwersja do ObservationMemory."""
        return ObservationMemory(
            observation_id=self.entry_id,
            timestamp=self.created_at,
            scope=ObservationScope[self.scope.upper()] if self.scope else ObservationScope.SYSTEM,
            target_id=self.target_id,
            observation_type=self.observation_type,
            data=self.data,
            patterns_detected=self.patterns,
            anomalies_detected=self.anomalies
        )


@dataclass
class BehaviorMemoryEntry:
    """Wpis pamieci zachowan (kompatybilnosc)."""
    entry_id: str = field(default_factory=lambda: f"behavior_{uuid.uuid4().hex[:12]}")
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Behavior-specific
    behavior_type: str = "decision"
    agent_ids: List[str] = field(default_factory=list)
    trigger_conditions: List[Dict[str, Any]] = field(default_factory=list)
    success_rate: float = 0.0
    
    def to_behavior_memory(self) -> BehaviorMemory:
        """Konwersja do BehaviorMemory."""
        return BehaviorMemory(
            behavior_id=self.entry_id,
            behavior_type=BehaviorType[self.behavior_type.upper()] if self.behavior_type else BehaviorType.DECISION,
            agent_ids=self.agent_ids,
            trigger_conditions=self.trigger_conditions,
            success_rate=self.success_rate,
            context=self.data
        )


@dataclass
class AgentAnalysisMemoryEntry:
    """Wpis pamieci analiz agentow (kompatybilnosc)."""
    entry_id: str = field(default_factory=lambda: f"analysis_{uuid.uuid4().hex[:12]}")
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Analysis-specific
    agent_id: str = ""
    analysis_type: str = "performance"
    scores: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    
    def to_agent_analysis_memory(self) -> AgentAnalysisMemory:
        """Konwersja do AgentAnalysisMemory."""
        return AgentAnalysisMemory(
            analysis_id=self.entry_id,
            agent_id=self.agent_id,
            analysis_type=AnalysisType[self.analysis_type.upper()] if self.analysis_type else AnalysisType.PERFORMANCE,
            scores=self.scores,
            recommendations=self.recommendations,
            context=self.data
        )


@dataclass
class DecisionMemoryEntry:
    """Wpis pamieci decyzji (kompatybilnosc)."""
    entry_id: str = field(default_factory=lambda: f"decision_{uuid.uuid4().hex[:12]}")
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Decision-specific
    decision_type: str = "strategy_selection"
    agent_id: str = ""
    success: bool = True
    confidence: float = 0.0
    
    def to_decision_memory(self) -> DecisionMemory:
        """Konwersja do DecisionMemory."""
        return DecisionMemory(
            decision_id=self.entry_id,
            decision_type=self.decision_type,
            made_at=self.created_at,
            context=self.data,
            agent_id=self.agent_id,
            success=self.success,
            confidence=self.confidence
        )
