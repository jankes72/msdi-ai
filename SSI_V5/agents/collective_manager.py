# SSI V5 Agent Layer - Collective Manager
# ==================================================
#
# ETAP: 5.2.4 FAZA 3.4
# Data: 2026-08-04
#
# Odpowiedzialnosc:
# - Zarządzanie grupą 6 agentów
# - Zbieranie wyników agentów
# - Porównywanie decyzji
# - Tworzenie konsensusu
# - Przekazywanie informacji do pamięci kolektywnej
#
# ArchTekstura:
# Agent_01 -> Agent_06
#     ↓
# CollectiveManager
#     ↓
# Collective Memory
#     ↓
# Master Teacher

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from datetime import datetime
import uuid
import copy
from threading import Lock


class ConsensusType(Enum):
    """Typy konsensusu"""
    UNANIMOUS = "unanimous"          # Jednogłośny
    MAJORITY = "majority"           # Większościowy
    WEIGHTED = "weighted"           # Wagowy (na podstawie wagi agentów)
    PLURALITY = "plurality"          # Największa liczba głosów
    AVERAGE = "average"             # Średnia (dla wartości liczbowych)


class DecisionStatus(Enum):
    """Statusy decyzji kolektywnej"""
    PENDING = "pending"              # Oczekuje na decyzje agentów
    COLLECTING = "collecting"       # Zbieranie decyzji
    ANALYZING = "analyzing"         # Analiza decyzji
    CONSENSUS = "consensus"         # Konsensus osiągnięty
    CONFLICT = "conflict"           # Konflikt decyzji
    COMPLETE = "complete"           # Decyzja kolektywna gotowa


@dataclass
class CollectiveDecision:
    """Decyzja kolektywna z wielu agentów"""
    decision_id: str
    cycle_id: str
    world_name: str
    agents_participated: List[str] = field(default_factory=list)
    individual_decisions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    consensus_type: ConsensusType = ConsensusType.MAJORITY
    consensus_result: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    status: DecisionStatus = DecisionStatus.PENDING
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            'decision_id': self.decision_id,
            'cycle_id': self.cycle_id,
            'world_name': self.world_name,
            'agents_participated': copy.deepcopy(self.agents_participated),
            'individual_decisions': copy.deepcopy(self.individual_decisions),
            'consensus_type': self.consensus_type.value,
            'consensus_result': copy.deepcopy(self.consensus_result),
            'confidence_score': self.confidence_score,
            'status': self.status.value,
            'timestamp': self.timestamp.isoformat(),
            'metadata': copy.deepcopy(self.metadata)
        }
    
    def add_decision(self, agent_id: str, decision: Dict[str, Any]) -> None:
        """Dodanie decyzji pojedynczego agenta"""
        if agent_id not in self.individual_decisions:
            self.individual_decisions[agent_id] = decision
            self.agents_participated.append(agent_id)


@dataclass
class CollectiveObservation:
    """Obserwacja kolektywna z wielu agentów"""
    observation_id: str
    cycle_id: str
    world_name: str
    agents_participated: List[str] = field(default_factory=list)
    individual_observations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    combined_observation: Dict[str, Any] = field(default_factory=dict)
    importance_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            'observation_id': self.observation_id,
            'cycle_id': self.cycle_id,
            'world_name': self.world_name,
            'agents_participated': copy.deepcopy(self.agents_participated),
            'individual_observations': copy.deepcopy(self.individual_observations),
            'combined_observation': copy.deepcopy(self.combined_observation),
            'importance_score': self.importance_score,
            'timestamp': self.timestamp.isoformat()
        }
    
    def add_observation(self, agent_id: str, observation: Dict[str, Any]) -> None:
        """Dodanie obserwacji pojedynczego agenta"""
        if agent_id not in self.individual_observations:
            self.individual_observations[agent_id] = observation
            self.agents_participated.append(agent_id)


@dataclass
class CollectiveMemory:
    """Pamięć kolektywna wszystkich agentów"""
    memory_id: str
    world_name: str
    decisions: List[CollectiveDecision] = field(default_factory=list)
    observations: List[CollectiveObservation] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_decision(self, decision: CollectiveDecision) -> str:
        """Dodanie decyzji kolektywnej"""
        self.decisions.append(decision)
        self.updated_at = datetime.now()
        self._update_statistics()
        return decision.decision_id
    
    def add_observation(self, observation: CollectiveObservation) -> str:
        """Dodanie obserwacji kolektywnej"""
        self.observations.append(observation)
        self.updated_at = datetime.now()
        self._update_statistics()
        return observation.observation_id
    
    def _update_statistics(self) -> None:
        """Aktualizacja statystyk"""
        self.statistics = {
            'total_decisions': len(self.decisions),
            'total_observations': len(self.observations),
            'total_agents_participated': len(set(
                agent for decision in self.decisions 
                for agent in decision.agents_participated
            )),
            'last_updated': self.updated_at.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            'memory_id': self.memory_id,
            'world_name': self.world_name,
            'decisions': [d.to_dict() for d in self.decisions],
            'observations': [o.to_dict() for o in self.observations],
            'statistics': copy.deepcopy(self.statistics),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class CollectiveManager:
    """
    Menadżer Kolektywu - zarządza grupą agentów i tworzy decyzje konsensusowe.
    
    Odpowiedzialność:
    - Zarządzanie grupą 6 agentów
    - Zbieranie wyników agentów
    - Porównywanie decyzji
    - Tworzenie konsensusu
    - Przekazywanie informacji do pamięci kolektywnej
    
    Arch Tekstura:
    Agent_01 -> Agent_06
        ↓
    CollectiveManager
        ↓
    Collective Memory
        ↓
    Master Teacher
    """
    
    # Domyslna liczba agentow
    DEFAULT_AGENT_COUNT = 6
    DEFAULT_AGENT_NAMES = [f"Agent_{i:02d}" for i in range(1, 7)]
    
    def __init__(self, world_name: str = "SSI_V5_WORLD",
                 agent_names: Optional[List[str]] = None,
                 consensus_type: ConsensusType = ConsensusType.MAJORITY,
                 pipeline_reference: Optional[str] = None):
        """
        Inicjalizacja CollectiveManager.
        
        Args:
            world_name: Nazwa świata
            agent_names: Lista nazw agentów (domyślnie 6: Agent_01 do Agent_06)
            consensus_type: Typ konsensusu (domyślnie MAJORITY)
            pipeline_reference: Referencja do Pipeline
        """
        self.world_name = world_name
        self.agent_names = agent_names or self.DEFAULT_AGENT_NAMES
        self.consensus_type = consensus_type
        self.pipeline_reference = pipeline_reference
        
        # StanagentManager
        self._initialized = False
        self._active = False
        self._lock = Lock()
        
        # Pamięć kolektywna
        self.collective_memory = CollectiveMemory(
            memory_id=f"collective_memory_{uuid.uuid4().hex[:8]}",
            world_name=world_name
        )
        
        # Bieżący cykl
        self._current_cycle_id: Optional[str] = None
        self._current_decisions: Dict[str, Dict[str, Any]] = {}
        self._current_observations: Dict[str, Dict[str, Any]] = {}
        
        # Statystyki
        self.total_cycles = 0
        self.total_collective_decisions = 0
        self.total_conflicts = 0
        self.total_consensus_reached = 0
        
        # Zdarzenia
        self._event_log: List[Dict[str, Any]] = []
        
        # Referencje (będą ustawiane z zewnątrz)
        self.agent_runtime_manager = None
        self.memory_manager = None
        
    def initialize(self) -> Dict[str, Any]:
        """
        Inicjalizacja CollectiveManager.
        
        Returns:
            Status inicjalizacji
        """
        self._log_event("COLLECTIVE_MANAGER_INITIALIZATION_START")
        
        result = {
            'status': 'success',
            'message': 'CollectiveManager initialized',
            'world_name': self.world_name,
            'agent_names': copy.deepcopy(self.agent_names),
            'consensus_type': self.consensus_type.value,
            'collective_memory_id': self.collective_memory.memory_id,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            self._initialized = True
            self._active = True
            self._log_event("COLLECTIVE_MANAGER_INITIALIZATION_COMPLETE", result)
            return result
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            self._log_event("COLLECTIVE_MANAGER_INITIALIZATION_ERROR", {
                'error': str(e)
            }, level="ERROR")
            return result
    
    def start_cycle(self, cycle_id: str) -> Dict[str, Any]:
        """
        Rozpoczęcie nowego cyklu kolektywnego.
        
        Args:
            cycle_id: ID cyklu
            
        Returns:
            Status rozpoczęcia
        """
        with self._lock:
            self._current_cycle_id = cycle_id
            self._current_decisions.clear()
            self._current_observations.clear()
            self.total_cycles += 1
        
        self._log_event("COLLECTIVE_CYCLE_START", {
            'cycle_id': cycle_id,
            'total_cycles': self.total_cycles
        })
        
        return {
            'status': 'success',
            'message': f'Collective cycle {cycle_id} started',
            'cycle_id': cycle_id,
            'timestamp': datetime.now().isoformat()
        }
    
    def collect_agent_decision(self, agent_id: str, decision: Dict[str, Any],
                               cycle_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Zebranie decyzji od pojedynczego agenta.
        
        Args:
            agent_id: ID agenta
            decision: Decyzja od agenta
            cycle_id: ID cyklu (opcjonalny, uzywa bieżącego jeśli None)
            
        Returns:
            Status zebrania
        """
        actual_cycle_id = cycle_id or self._current_cycle_id
        
        if actual_cycle_id is None:
            return {
                'status': 'error',
                'error': 'No active cycle - call start_cycle() first',
                'agent_id': agent_id,
                'timestamp': datetime.now().isoformat()
            }
        
        with self._lock:
            self._current_decisions[agent_id] = decision
        
        self._log_event("AGENT_DECISION_COLLECTED", {
            'cycle_id': actual_cycle_id,
            'agent_id': agent_id,
            'decision_type': decision.get('decision_type', 'unknown'),
            'total_collected': len(self._current_decisions)
        })
        
        return {
            'status': 'success',
            'message': f'Decision collected from {agent_id}',
            'agent_id': agent_id,
            'cycle_id': actual_cycle_id,
            'decisions_collected': len(self._current_decisions),
            'total_agents': len(self.agent_names),
            'timestamp': datetime.now().isoformat()
        }
    
    def collect_agent_observation(self, agent_id: str, observation: Dict[str, Any],
                                  cycle_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Zebranie obserwacji od pojedynczego agenta.
        
        Args:
            agent_id: ID agenta
            observation: Obserwacja od agenta
            cycle_id: ID cyklu (opcjonalny)
            
        Returns:
            Status zebrania
        """
        actual_cycle_id = cycle_id or self._current_cycle_id
        
        if actual_cycle_id is None:
            return {
                'status': 'error',
                'error': 'No active cycle - call start_cycle() first',
                'agent_id': agent_id,
                'timestamp': datetime.now().isoformat()
            }
        
        with self._lock:
            self._current_observations[agent_id] = observation
        
        self._log_event("AGENT_OBSERVATION_COLLECTED", {
            'cycle_id': actual_cycle_id,
            'agent_id': agent_id,
            'observation_type': observation.get('observation_type', 'unknown'),
            'total_collected': len(self._current_observations)
        })
        
        return {
            'status': 'success',
            'message': f'Observation collected from {agent_id}',
            'agent_id': agent_id,
            'cycle_id': actual_cycle_id,
            'observations_collected': len(self._current_observations),
            'timestamp': datetime.now().isoformat()
        }
    
    def build_consensus(self, cycle_id: Optional[str] = None) -> CollectiveDecision:
        """
        Budowanie konsensusu z zebranych decyzji agentów.
        
        Args:
            cycle_id: ID cyklu (opcjonalny, uzywa bieżącego jeśli None)
            
        Returns:
            CollectiveDecision z konsensusem
        """
        actual_cycle_id = cycle_id or self._current_cycle_id
        
        if actual_cycle_id is None:
            raise ValueError("No active cycle - call start_cycle() first")
        
        if not self._current_decisions:
            raise ValueError("No decisions collected - call collect_agent_decision() first")
        
        decision_id = f"collective_decision_{uuid.uuid4().hex[:8]}"
        collective_decision = CollectiveDecision(
            decision_id=decision_id,
            cycle_id=actual_cycle_id,
            world_name=self.world_name,
            consensus_type=self.consensus_type
        )
        
        # Dodanie wszystkich zebranych decyzji
        for agent_id, decision in self._current_decisions.items():
            collective_decision.add_decision(agent_id, decision)
        
        # Budowanie konsensusu w zależności od typu
        if self.consensus_type == ConsensusType.UNANIMOUS:
            result, confidence = self._build_unanimous_consensus(collective_decision)
        elif self.consensus_type == ConsensusType.MAJORITY:
            result, confidence = self._build_majority_consensus(collective_decision)
        elif self.consensus_type == ConsensusType.WEIGHTED:
            result, confidence = self._build_weighted_consensus(collective_decision)
        elif self.consensus_type == ConsensusType.PLURALITY:
            result, confidence = self._build_plurality_consensus(collective_decision)
        elif self.consensus_type == ConsensusType.AVERAGE:
            result, confidence = self._build_average_consensus(collective_decision)
        else:
            # Domyślny: większościowy
            result, confidence = self._build_majority_consensus(collective_decision)
        
        collective_decision.consensus_result = result
        collective_decision.confidence_score = confidence
        collective_decision.status = DecisionStatus.CONSENSUS
        
        # Dodanie do pamięci kolektywnej
        self.collective_memory.add_decision(collective_decision)
        self.total_collective_decisions += 1
        self.total_consensus_reached += 1
        
        self._log_event("CONSENSUS_BUILT", {
            'decision_id': decision_id,
            'cycle_id': actual_cycle_id,
            'consensus_type': self.consensus_type.value,
            'confidence_score': confidence,
            'agents_participated': len(collective_decision.agents_participated)
        })
        
        return collective_decision
    
    def _build_unanimous_consensus(self, collective_decision: CollectiveDecision) -> tuple:
        """Budowanie konsensusu jednogłośnego"""
        decisions = collective_decision.individual_decisions
        
        if not decisions:
            return {}, 0.0
        
        # Sprawdź czy wszystkie decyzje są identyczne
        first_decision = next(iter(decisions.values()))
        all_same = all(
            decision.get('decision_type') == first_decision.get('decision_type') and
            decision.get('action') == first_decision.get('action')
            for decision in decisions.values()
        )
        
        if all_same:
            return copy.deepcopy(first_decision), 1.0
        else:
            # Zwróć maioria jako fallback
            return self._build_majority_consensus(collective_decision)
    
    def _build_majority_consensus(self, collective_decision: CollectiveDecision) -> tuple:
        """Budowanie konsensusu większościowego"""
        decisions = collective_decision.individual_decisions
        
        if not decisions:
            return {}, 0.0
        
        # Zliczanie głosów na poszczególne typy decyzji
        decision_counts: Dict[str, int] = {}
        decision_templates: Dict[str, Dict[str, Any]] = {}
        
        for agent_id, decision in decisions.items():
            decision_type = decision.get('decision_type', 'unknown')
            decision_key = decision.get('action') or decision.get('decision_type')
            
            if decision_key not in decision_counts:
                decision_counts[decision_key] = 0
                decision_templates[decision_key] = decision
            
            decision_counts[decision_key] += 1
        
        if not decision_counts:
            return {}, 0.0
        
        # Znajdź decyzję z największą liczbą głosów
        winner_key = max(decision_counts.keys(), key=lambda k: decision_counts[k])
        winner_count = decision_counts[winner_key]
        total_votes = sum(decision_counts.values())
        
        confidence = winner_count / total_votes
        
        # Dodaj informację o głosowaniu
        result = copy.deepcopy(decision_templates[winner_key])
        result['_consensus_info'] = {
            'type': 'majority',
            'votes_for': winner_count,
            'total_votes': total_votes,
            'all_votes': decision_counts
        }
        
        return result, confidence
    
    def _build_weighted_consensus(self, collective_decision: CollectiveDecision) -> tuple:
        """Budowanie konsensusu wagowego (na podstawie wagi agentów)"""
        # Uproszczona wersja: użyj większościowego z wagami
        # W rzeczywistości wagi dla każdego agenta mogą pochodzić z memory_manager
        decisions = collective_decision.individual_decisions
        
        if not decisions:
            return {}, 0.0
        
        # Jezeli nie ma ustawionych wag, użyj równych wag
        return self._build_majority_consensus(collective_decision)
    
    def _build_plurality_consensus(self, collective_decision: CollectiveDecision) -> tuple:
        """Budowanie konsensusu dzięki wielkości (plurality)"""
        # Podobne do większościowego, ale nie wymaga większości bezwzględnej
        return self._build_majority_consensus(collective_decision)
    
    def _build_average_consensus(self, collective_decision: CollectiveDecision) -> tuple:
        """Budowanie konsensusu średnią (dla wartości liczbowych)"""
        decisions = collective_decision.individual_decisions
        
        if not decisions:
            return {}, 0.0
        
        # Zebranie wszystkich wartości liczbowych
        numeric_values = []
        for decision in decisions.values():
            value = decision.get('value') or decision.get('confidence', 0)
            if isinstance(value, (int, float)):
                numeric_values.append(value)
        
        if not numeric_values:
            return self._build_majority_consensus(collective_decision)
        
        avg_value = sum(numeric_values) / len(numeric_values)
        
        # Stworzenie ogólnej decyzji z średnią
        result = {
            'decision_type': 'average',
            'value': avg_value,
            'agents_count': len(decisions),
            'values': numeric_values
        }
        
        return result, 1.0
    
    def build_collective_observation(self, cycle_id: Optional[str] = None) -> CollectiveObservation:
        """
        Budowanie kolektywnej obserwacji z zebranych obserwacji agentów.
        
        Args:
            cycle_id: ID cyklu (opcjonalny)
            
        Returns:
            CollectiveObservation
        """
        actual_cycle_id = cycle_id or self._current_cycle_id
        
        if actual_cycle_id is None:
            raise ValueError("No active cycle - call start_cycle() first")
        
        if not self._current_observations:
            raise ValueError("No observations collected - call collect_agent_observation() first")
        
        observation_id = f"collective_observation_{uuid.uuid4().hex[:8]}"
        collective_observation = CollectiveObservation(
            observation_id=observation_id,
            cycle_id=actual_cycle_id,
            world_name=self.world_name
        )
        
        # Dodanie wszystkich zebranych obserwacji
        for agent_id, observation in self._current_observations.items():
            collective_observation.add_observation(agent_id, observation)
        
        # Budowanie połączonej obserwacji
        combined = self._combine_observations(collective_observation.individual_observations)
        collective_observation.combined_observation = combined
        collective_observation.importance_score = self._calculate_importance_score(combined)
        
        # Dodanie do pamięci kolektywnej
        self.collective_memory.add_observation(collective_observation)
        
        self._log_event("COLLECTIVE_OBSERVATION_BUILT", {
            'observation_id': observation_id,
            'cycle_id': actual_cycle_id,
            'agents_participated': len(collective_observation.agents_participated),
            'importance_score': collective_observation.importance_score
        })
        
        return collective_observation
    
    def _combine_observations(self, observations: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Połączenie obserwacji z wielu agentów"""
        combined = {
            'timestamp': datetime.now().isoformat(),
            'agents_count': len(observations),
            'observation_types': list(set(
                obs.get('observation_type', 'unknown') 
                for obs in observations.values()
            )),
            'data': {}
        }
        
        # Połączenie danych
        for agent_id, observation in observations.items():
            for key, value in observation.get('data', {}).items():
                if key not in combined['data']:
                    combined['data'][key] = []
                combined['data'][key].append(value)
        
        return combined
    
    def _calculate_importance_score(self, observation: Dict[str, Any]) -> float:
        """Obliczanie wskaźnika ważności obserwacji"""
        # Uproszczony algorytm: im więcej agentów potwierdza, tym wyższa ważność
        agents_count = observation.get('agents_count', 1)
        normalized = min(agents_count / len(self.agent_names), 1.0)
        return round(normalized * 100, 2)
    
    def end_cycle(self, cycle_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Zakończenie cyklu kolektywnego.
        
        Args:
            cycle_id: ID cyklu (opcjonalny)
            
        Returns:
            Podsumowanie cyklu
        """
        actual_cycle_id = cycle_id or self._current_cycle_id
        
        if actual_cycle_id is None:
            return {
                'status': 'error',
                'error': 'No active cycle',
                'timestamp': datetime.now().isoformat()
            }
        
        # Zapisz liczbę zebranych decyzji i obserwacji przed wyczyszczeniem
        decisions_count = len(self._current_decisions)
        observations_count = len(self._current_observations)
        
        # Budowanie konsensusu i obserwacji - obsługuj oddzielnie
        collective_decision = None
        collective_observation = None
        
        try:
            if decisions_count > 0:
                collective_decision = self.build_consensus(actual_cycle_id)
        except ValueError:
            # Nie ma wystarczających decyzji
            collective_decision = None
        
        try:
            if observations_count > 0:
                collective_observation = self.build_collective_observation(actual_cycle_id)
        except ValueError:
            # Nie ma wystarczających obserwacji
            collective_observation = None
        
        with self._lock:
            self._current_cycle_id = None
        
        result = {
            'status': 'success',
            'message': f'Collective cycle {actual_cycle_id} ended',
            'cycle_id': actual_cycle_id,
            'decisions_collected': decisions_count,
            'observations_collected': observations_count,
            'collective_decision_id': collective_decision.decision_id if collective_decision else None,
            'collective_observation_id': collective_observation.observation_id if collective_observation else None,
            'consensus_reached': collective_decision is not None,
            'total_collective_decisions': self.total_collective_decisions,
            'timestamp': datetime.now().isoformat()
        }
        
        self._log_event("COLLECTIVE_CYCLE_END", result)
        
        return result
    
    def get_collective_memory(self) -> Dict[str, Any]:
        """Pobranie pełnej pamięci kolektywnej"""
        return self.collective_memory.to_dict()
    
    def get_cycle_summary(self, cycle_id: str) -> Dict[str, Any]:
        """Pobranie podsumowania dla konkretnego cyklu"""
        decisions = [
            d.to_dict() for d in self.collective_memory.decisions 
            if d.cycle_id == cycle_id
        ]
        observations = [
            o.to_dict() for o in self.collective_memory.observations 
            if o.cycle_id == cycle_id
        ]
        
        return {
            'cycle_id': cycle_id,
            'decisions': decisions,
            'observations': observations,
            'total_agents_participated': len(set(
                agent for d in self.collective_memory.decisions 
                if d.cycle_id == cycle_id 
                for agent in d.agents_participated
            ))
        }
    
    def set_agent_runtime_manager_reference(self, agent_runtime_manager: Any) -> None:
        """Ustawienie referencji do AgentRuntimeManager"""
        self.agent_runtime_manager = agent_runtime_manager
        self._log_event("AGENT_RUNTIME_MANAGER_REFERENCE_SET")
    
    def set_memory_manager_reference(self, memory_manager: Any) -> None:
        """Ustawienie referencji do MemoryManager"""
        self.memory_manager = memory_manager
        self._log_event("MEMORY_MANAGER_REFERENCE_SET")
    
    def shutdown(self) -> Dict[str, Any]:
        """Zamknięcie CollectiveManager"""
        self._log_event("COLLECTIVE_MANAGER_SHUTDOWN_START")
        
        result = {
            'status': 'success',
            'message': 'CollectiveManager shutdown completed',
            'total_cycles': self.total_cycles,
            'total_collective_decisions': self.total_collective_decisions,
            'total_conflicts': self.total_conflicts,
            'total_consensus_reached': self.total_consensus_reached,
            'collective_memory_stats': self.collective_memory.statistics,
            'timestamp': datetime.now().isoformat()
        }
        
        self._initialized = False
        self._active = False
        self._current_cycle_id = None
        
        self._log_event("COLLECTIVE_MANAGER_SHUTDOWN_COMPLETE", result)
        
        return result
    
    def _log_event(self, event_type: str, data: Optional[Dict[str, Any]] = None,
                   level: str = "INFO") -> None:
        """Logowanie zdarzenia"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'pipeline_reference': self.pipeline_reference,
            'world_name': self.world_name,
            'data': data or {},
            'level': level
        }
        with self._lock:
            self._event_log.append(event)
    
    def get_event_log(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Pobranie dziennika zdarzeń"""
        if limit is None:
            return copy.deepcopy(self._event_log)
        else:
            return copy.deepcopy(self._event_log[-limit:])


# Eksportowane klasy
__all__ = [
    'ConsensusType',
    'DecisionStatus',
    'CollectiveDecision',
    'CollectiveObservation',
    'CollectiveMemory',
    'CollectiveManager'
]
