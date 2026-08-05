# SSI V5 Agent Layer - Agent Runtime
# ==================================================
#
# ETAP: 5.2.4 FAZA 4
# Data: 2026-08-03
# 
# Odpowiedzialnosc:
# - Zarządzanie własną pętlą agenta
# - Zarządzanie własnym stanem
# - Zarządzanie własnymi zadaniami
# - Komunikacja z Pipeline
# - Odbiór danych z Teacher Layer
# - Zapis obserwacji
#
# ZASADA: Agent Riceve jedynie kontrakt danych, nie czyta zmiennych globalnych

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Callable
from enum import Enum
from datetime import datetime
import uuid
import copy
import time
import json
import logging
from queue import Queue
from threading import Lock

# Konfiguracja logowania
logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Statusy agenta"""
    IDLE = "idle"                    # Agent gotowy do wykonania
    INITIALIZING = "initializing"    # Inicjalizacja agenta
    PROCESSING = "processing"        # W trakcie przetwarzania
    WAITING = "waiting"              # Oczekuje na dane
    COMPLETE = "complete"            # Zakończył wykonywanie
    ERROR = "error"                  # Błąd w czasie wykonania
    SHUTDOWN = "shutdown"            # Agent zamknięty


class AgentMode(Enum):
    """Tryby pracy agenta"""
    AUTO = "auto"                    # Automatyczne wykonywanie
    MANUAL = "manual"                # Ręczne sterowanie
    TEST = "test"                    # Tryb testowy


@dataclass
class AgentTask:
    """Zadanie dla agenta"""
    task_id: str
    task_type: str
    data: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            'task_id': self.task_id,
            'task_type': self.task_type,
            'data': copy.deepcopy(self.data),
            'priority': self.priority,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status,
            'result': copy.deepcopy(self.result) if self.result else None
        }


@dataclass
class AgentMemory:
    """Pamięć agenta"""
    agent_id: str
    short_term_memory: Dict[str, Any] = field(default_factory=dict)
    long_term_memory: Dict[str, Any] = field(default_factory=dict)
    observations: List[Dict[str, Any]] = field(default_factory=list)
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_observation(self, observation: Dict[str, Any], timestamp: Optional[datetime] = None) -> str:
        """Dodanie obserwacji do pamięci"""
        obs_id = f"obs_{len(self.observations) + 1}_{uuid.uuid4().hex[:8]}"
        observation_record = {
            'observation_id': obs_id,
            'agent_id': self.agent_id,
            'data': copy.deepcopy(observation),
            'timestamp': (timestamp or datetime.now()).isoformat()
        }
        self.observations.append(observation_record)
        self.updated_at = datetime.now()
        return obs_id
    
    def add_decision(self, decision: Dict[str, Any], timestamp: Optional[datetime] = None) -> str:
        """Dodanie decyzji do pamięci"""
        decision_id = f"dec_{len(self.decisions) + 1}_{uuid.uuid4().hex[:8]}"
        decision_record = {
            'decision_id': decision_id,
            'agent_id': self.agent_id,
            'data': copy.deepcopy(decision),
            'timestamp': (timestamp or datetime.now()).isoformat()
        }
        self.decisions.append(decision_record)
        self.updated_at = datetime.now()
        return decision_id
    
    def store_in_short_term(self, key: str, value: Any) -> None:
        """Zapisanie do pamięci krótkoterminowej"""
        self.short_term_memory[key] = copy.deepcopy(value)
        self.updated_at = datetime.now()
    
    def store_in_long_term(self, key: str, value: Any) -> None:
        """Zapisanie do pamięci długoterminowej"""
        self.long_term_memory[key] = copy.deepcopy(value)
        self.updated_at = datetime.now()
    
    def get_observations(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Pobranie obserwacji"""
        if limit is None:
            return copy.deepcopy(self.observations)
        else:
            return copy.deepcopy(self.observations[-limit:])
    
    def get_decisions(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Pobranie decyzji"""
        if limit is None:
            return copy.deepcopy(self.decisions)
        else:
            return copy.deepcopy(self.decisions[-limit:])
    
    def clear_short_term(self) -> None:
        """Wyczyszczenie pamięci krótkoterminowej"""
        self.short_term_memory.clear()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            'agent_id': self.agent_id,
            'short_term_memory': copy.deepcopy(self.short_term_memory),
            'long_term_memory': copy.deepcopy(self.long_term_memory),
            'observations': copy.deepcopy(self.observations),
            'decisions': copy.deepcopy(self.decisions),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class AgentState:
    """Stan agenta"""
    agent_id: str
    name: str
    status: AgentStatus = AgentStatus.IDLE
    mode: AgentMode = AgentMode.AUTO
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    cycle_count: int = 0
    task_queue: Queue = field(default_factory=Queue)
    current_task: Optional[AgentTask] = None
    error_count: int = 0
    success_count: int = 0
    
    def update_status(self, new_status: AgentStatus) -> None:
        """Aktualizacja statusu"""
        self.status = new_status
        self.last_activity = datetime.now()
    
    def add_to_queue(self, task: AgentTask) -> None:
        """Dodanie zadania do kolejki"""
        self.task_queue.put(task)
        self.last_activity = datetime.now()
    
    def get_next_task(self) -> Optional[AgentTask]:
        """Pobranie następnego zadania z kolejki"""
        if not self.task_queue.empty():
            task = self.task_queue.get()
            self.current_task = task
            self.last_activity = datetime.now()
            return task
        return None
    
    def complete_current_task(self, result: Dict[str, Any]) -> None:
        """Zakończenie bieżącego zadania"""
        if self.current_task:
            self.current_task.status = "completed"
            self.current_task.result = result
            self.success_count += 1
            self.cycle_count += 1
            self.current_task = None
            self.last_activity = datetime.now()
    
    def fail_current_task(self, error: str) -> None:
        """Niepowodzenie bieżącego zadania"""
        if self.current_task:
            self.current_task.status = "failed"
            self.current_task.result = {'error': error}
            self.error_count += 1
            self.current_task = None
            self.last_activity = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'status': self.status.value,
            'mode': self.mode.value,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'cycle_count': self.cycle_count,
            'error_count': self.error_count,
            'success_count': self.success_count,
            'tasks_in_queue': self.task_queue.qsize(),
            'current_task': self.current_task.to_dict() if self.current_task else None
        }


@dataclass
class AgentContract:
    """Kontrakt danych dla agenta - odbierany od Teacher Layer"""
    contract_id: str
    cycle_id: str
    world_name: str
    world_data: Dict[str, Any] = field(default_factory=dict)
    model_evaluation: Dict[str, Any] = field(default_factory=dict)
    current_weights: Dict[str, Any] = field(default_factory=dict)
    world_memory: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    # ETAP 5.3.2: Execution Context
    execution_context: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            'contract_id': self.contract_id,
            'cycle_id': self.cycle_id,
            'world_name': self.world_name,
            'world_data': copy.deepcopy(self.world_data),
            'model_evaluation': copy.deepcopy(self.model_evaluation),
            'current_weights': copy.deepcopy(self.current_weights),
            'world_memory': copy.deepcopy(self.world_memory),
            'recommendations': copy.deepcopy(self.recommendations),
            'metadata': copy.deepcopy(self.metadata),
            'timestamp': self.timestamp.isoformat(),
            # ETAP 5.3.2: Execution Context
            'execution_context': copy.deepcopy(self.execution_context) if self.execution_context else None
        }
    
    @classmethod
    def from_world_engine_output(cls, world_output: Any, cycle_id: str, world_name: str) -> 'AgentContract':
        """Tworzenie kontraktu z WorldEngineOutput"""
        contract = cls(
            contract_id=f"agent_contract_{uuid.uuid4().hex[:8]}",
            cycle_id=cycle_id,
            world_name=world_name,
            world_data=world_output.to_dict() if hasattr(world_output, 'to_dict') else world_output,
            metadata={'source': 'world_engine', 'created_at': datetime.now().isoformat()}
        )
        return contract
    
    @classmethod
    def from_teacher_data(cls, teacher_data: Dict[str, Any], cycle_id: str, world_name: str) -> 'AgentContract':
        """Tworzenie kontraktu z danych od Teacher Layer"""
        contract = cls(
            contract_id=f"agent_contract_{uuid.uuid4().hex[:8]}",
            cycle_id=cycle_id,
            world_name=world_name,
            model_evaluation=teacher_data.get('model_evaluation', {}),
            current_weights=teacher_data.get('current_weights', {}),
            world_memory=teacher_data.get('world_memory', {}),
            recommendations=teacher_data.get('recommendations', []),
            metadata={'source': 'teacher_layer', 'created_at': datetime.now().isoformat()}
        )
        return contract


class AgentRuntime:
    """
    Główna klasa Agent Runtime - zarządza własną pętlą, stanem i zadaniami.
    
    Odpowiedzialność:
    - Własna pętla agenta
    - Własny stan
    - Własne zadania
    - Komunikacja z Pipeline
    - Odbiór danych z Teacher Layer
    - Zapis obserwacji
    
    Agent Riceve jedynie kontrakt danych, nie czyta zmiennych globalnych.
    """
    
    def __init__(self, agent_id: str, name: str, mode: AgentMode = AgentMode.AUTO,
                 pipeline_reference: Optional[str] = None):
        """
        Inicjalizacja Agent Runtime.
        
        Args:
            agent_id: Unikalny identyfikator agenta
            name: Nazwa agenta
            mode: Tryb pracy (AUTO, MANUAL, TEST)
            pipeline_reference: Referencja do Pipeline (opcjonalna)
        """
        self.agent_id = agent_id
        self.name = name
        self.mode = mode
        self.pipeline_reference = pipeline_reference
        
        # Stan agenta
        self.state = AgentState(
            agent_id=agent_id,
            name=name,
            mode=mode
        )
        
        # Pamięć agenta
        self.memory = AgentMemory(agent_id=agent_id)
        
        # Strategia i decyzje
        self.strategy_manager = None
        self.decision_engine = None
        
        # Obserwacje
        self.observation_manager = None
        
        # Personality Manager
        self.personality_state = None
        
        # Trust Manager (referencja do globalnego TrustManager)
        self.trust_manager = None
        self.agent_trust_state = None
        
        # ETAP 0 KROK 1 & 2: Memory Integration
        # Referencja do MemoryIntegrationLayer (z AgentRuntimeManager)
        self.memory_integration_layer = None
        # Referencja do DecisionMemoryContextBuilder
        self.memory_context_builder = None
        
        # Flagi integracji z pamięcią
        self._memory_integration_enabled = False
        
        # Komunikacja
        self._communication_lock = Lock()
        self._contracts_received: List[AgentContract] = []
        self._responses_sent: List[Dict[str, Any]] = []
        
        # Rejestry callbacków
        self._on_contract_callbacks: List[Callable] = []
        self._on_decision_callbacks: List[Callable] = []
        
        # Flagi
        self._initializing = False
        self._shutdown_requested = False
        
        # Inicjalizacja komponentów
        self._initialize_components()
    
    def _initialize_components(self) -> None:
        """Inicjalizacja komponentów agenta"""
        # Import lokalny, aby unikać zależności cyklicznych
        from .strategy_manager import StrategyManager
        from .decision_engine import DecisionEngine
        from .observation_manager import ObservationManager
        from .personality_manager import PersonalityManager, AgentPersonalityState
        
        self.strategy_manager = StrategyManager(agent_id=self.agent_id)
        self.decision_engine = DecisionEngine(agent_id=self.agent_id)
        self.observation_manager = ObservationManager(agent_id=self.agent_id)
        
        # Połącz komponenty z pamięcią
        self.observation_manager.memory = self.memory
        self.decision_engine.memory = self.memory
        self.strategy_manager.memory = self.memory
        
        # Inicjalizacja osobowości agenta
        self._initialize_personality()
    
    def _initialize_personality(self) -> None:
        """Inicjalizacja osobowości agenta"""
        from .personality_manager import PersonalityVector, AgentPersonalityState
        
        try:
            # Utwórz wektor osobowości z domyślnego profilu lub domyślnych wartości
            personality = PersonalityVector.from_profile(self.name)
        except ValueError:
            # Jeśli profil nie istnieje, użyj domyślnych wartości
            personality = PersonalityVector.default()
        
        # Utwórz stan osobowości
        self.personality_state = AgentPersonalityState(
            agent_id=self.agent_id,
            name=self.name,
            current_personality=personality,
            initial_personality=copy.deepcopy(personality)
        )
    
    def set_trust_manager_reference(self, trust_manager: Any) -> None:
        """Ustawienie referencji do TrustManager"""
        self.trust_manager = trust_manager
        if trust_manager and not self.agent_trust_state:
            # Inicjalizuj stan zaufania dla tego agenta
            self.agent_trust_state = trust_manager.initialize_agent_trust(
                self.agent_id, self.name
            )
    
    def set_memory_integration_reference(self, memory_integration_layer: Any = None) -> None:
        """
        Ustawienie referencji do MemoryIntegrationLayer (ETAP 0 KROK 3).
        
        Args:
            memory_integration_layer: Instancja MemoryIntegrationLayer
        """
        self.memory_integration_layer = memory_integration_layer
        
        if memory_integration_layer:
            # Utwórz DecisionMemoryContextBuilder
            from .decision_memory_context import DecisionMemoryContextBuilder
            self.memory_context_builder = DecisionMemoryContextBuilder(memory_integration_layer)
            self._memory_integration_enabled = True
            logger.info(f"Memory integration enabled for agent {self.agent_id}")
        else:
            self._memory_integration_enabled = False
            logger.warning(f"Memory integration disabled for agent {self.agent_id}")
    
    def is_memory_integration_enabled(self) -> bool:
        """Czy integracja z pamięcią jest włączona?"""
        return self._memory_integration_enabled and self.memory_integration_layer is not None
    
    def initialize(self) -> Dict[str, Any]:
        """
        Inicjalizacja agenta.
        
        Returns:
            Status inicjalizacji
        """
        if self._initializing:
            return {
                'status': 'error',
                'message': 'Initialization already in progress',
                'agent_id': self.agent_id,
                'timestamp': datetime.now().isoformat()
            }
        
        self._initializing = True
        self.state.update_status(AgentStatus.INITIALIZING)
        
        try:
            # Inicjalizacja komponentów
            self.strategy_manager.initialize()
            self.decision_engine.initialize()
            self.observation_manager.initialize()
            
            # Inicjalizacja osobowości (już zrobione w __init__, ale sprawdź)
            if self.personality_state is None:
                self._initialize_personality()
            
            self.state.update_status(AgentStatus.IDLE)
            self._initializing = False
            
            # Dodaj informację o osobowości do wyniku
            personality_info = {}
            if self.personality_state:
                personality_info = {
                    'personality_vector': self.personality_state.current_personality.to_dict(),
                    'personality_initialized': True
                }
            
            return {
                'status': 'success',
                'message': f'Agent {self.name} initialized',
                'agent_id': self.agent_id,
                'name': self.name,
                'mode': self.mode.value,
                'components': {
                    'strategy_manager': 'initialized',
                    'decision_engine': 'initialized',
                    'observation_manager': 'initialized',
                    'memory': 'initialized',
                    'personality': personality_info
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.state.update_status(AgentStatus.ERROR)
            self._initializing = False
            return {
                'status': 'error',
                'message': f'Initialization failed: {str(e)}',
                'agent_id': self.agent_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def receive_contract(self, contract_data: Union[AgentContract, Dict[str, Any]],
                        cycle_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Odbiór kontraktu danych od Pipeline/Teacher Layer.
        
        Agent Riceve jedynie kontrakt danych, nie czyta zmiennych globalnych.
        
        Args:
            contract_data: Kontrakt danych (AgentContract lub dict)
            cycle_id: ID cyklu (opcjonalny)
            
        Returns:
            Status odbioru
        """
        with self._communication_lock:
            try:
                # Konwersja do AgentContract, jeśli to dict
                if isinstance(contract_data, dict):
                    contract = AgentContract(
                        contract_id=contract_data.get('contract_id', f"contract_{uuid.uuid4().hex[:8]}"),
                        cycle_id=contract_data.get('cycle_id', cycle_id or ''),
                        world_name=contract_data.get('world_name', self.state.name),
                        world_data=contract_data.get('world_data', {}),
                        model_evaluation=contract_data.get('model_evaluation', {}),
                        current_weights=contract_data.get('current_weights', {}),
                        world_memory=contract_data.get('world_memory', {}),
                        recommendations=contract_data.get('recommendations', []),
                        metadata=contract_data.get('metadata', {}),
                        timestamp=datetime.fromisoformat(contract_data.get('timestamp')) 
                            if contract_data.get('timestamp') else datetime.now(),
                        # ETAP 5.3.2: Execution Context
                        execution_context=contract_data.get('execution_context')
                    )
                else:
                    contract = contract_data
                
                # Zapisanie kontraktu
                self._contracts_received.append(contract)
                self.memory.store_in_short_term(f"contract_{contract.contract_id}", contract.to_dict())
                
                # Aktualizacja stanu
                self.state.update_status(AgentStatus.PROCESSING)
                
                # Przetworzenie kontraktu
                self._process_contract(contract)
                
                return {
                    'status': 'success',
                    'message': f'Contract {contract.contract_id} received',
                    'agent_id': self.agent_id,
                    'contract_id': contract.contract_id,
                    'cycle_id': contract.cycle_id,
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                self.state.update_status(AgentStatus.ERROR)
                return {
                    'status': 'error',
                    'message': f'Failed to receive contract: {str(e)}',
                    'agent_id': self.agent_id,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
    
    def _process_contract(self, contract: AgentContract) -> None:
        """Przetworzenie odebranego kontraktu (ETAP 5.3.2: z ExecutionContext)"""
        try:
            # ETAP 5.3.2: Zapisanie ExecutionContext w pamięci agenta
            if contract.execution_context:
                self.memory.store_in_short_term("execution_context", contract.execution_context)
                self._apply_execution_context(contract.execution_context)
            
            # Przekazanie do Observation Manager
            self.observation_manager.receive_world_data(
                world_data=contract.world_data,
                cycle_id=contract.cycle_id,
                world_name=contract.world_name
            )
            
            # Przekazanie do Strategy Manager (rozszerzone o ExecutionContext)
            self.strategy_manager.receive_context(
                model_evaluation=contract.model_evaluation,
                current_weights=contract.current_weights,
                world_memory=contract.world_memory,
                recommendations=contract.recommendations,
                execution_context=contract.execution_context,  # ETAP 5.3.2
                world_data=contract.world_data  # ETAP 0: Kompatybilność world_data/world_state
            )
            
            # ETAP 0 KROK 3: Pobranie kontekstu pamieci PRZED podjeciem decyzji
            memory_context = self._retrieve_memory_context_for_contract(contract)
            enhanced_context = self._enhance_decision_context(contract, memory_context)
            
            # Przekazanie do Decision Engine (z rozszerzonym kontekstem)
            self.decision_engine.receive_contract(contract, memory_context=enhanced_context)
            
            # Generowanie obserwacji
            self._generate_observations(contract)
            
            # Wykonanie decyzji
            decision = self._execute_decision(contract)
            
            # ETAP 0 KROK 3: Zapis decyzji do pamieci kolektywnej
            self._record_decision_to_collective_memory(decision, contract)
            
            # Zapisanie rezultatów
            self._record_decision_and_observation(decision, contract)
            
        except Exception as e:
            self.state.fail_current_task(str(e))
            raise
    
    def _generate_observations(self, contract: AgentContract) -> Dict[str, Any]:
        """Generowanie obserwacji na podstawie kontraktu"""
        observation = {
            'contract_id': contract.contract_id,
            'cycle_id': contract.cycle_id,
            'world_name': contract.world_name,
            'observation_type': 'world_analysis',
            'data': {
                'world_data_keys': list(contract.world_data.keys()) if contract.world_data else [],
                'model_evaluation_keys': list(contract.model_evaluation.keys()) if contract.model_evaluation else [],
                'weights_keys': list(contract.current_weights.keys()) if contract.current_weights else [],
                'recommendations_count': len(contract.recommendations),
                'world_memory_keys': list(contract.world_memory.keys()) if contract.world_memory else []
            },
            'agent_id': self.agent_id,
            'timestamp': datetime.now().isoformat()
        }
        
        observation_id = self.memory.add_observation(observation)
        self.observation_manager.add_observation(observation)
        
        return observation
    
    def _apply_execution_context(self, execution_context: Dict[str, Any]) -> None:
        """
        Zastosowanie ExecutionContext do agenta (ETAP 5.3.2).
        
        Args:
            execution_context: Kontekst wykonania z CycleController
        """
        # Zapisanie informacji o fazie
        phase = execution_context.get('phase', 'unknown')
        goal = execution_context.get('goal', '')
        allowed_actions = execution_context.get('allowed_actions', [])
        forbidden_actions = execution_context.get('forbidden_actions', [])
        available_memory = execution_context.get('available_memory', [])
        priority = execution_context.get('priority', 'medium')
        
        # Zapisanie w pamięci agenta
        self.memory.add_observation({
            'type': 'execution_context',
            'phase': phase,
            'goal': goal,
            'allowed_actions': allowed_actions,
            'forbidden_actions': forbidden_actions,
            'available_memory': available_memory,
            'priority': priority,
            'timestamp': datetime.now().isoformat()
        })
        
        # Zaktualizowanie stanu agenta na podstawie fazy
        if phase == 'prediction_window':
            self.state.update_status(AgentStatus.PROCESSING)
            self._log_event("PHASE_PREDICTION_WINDOW", {
                'goal': goal,
                'available_memory': available_memory
            })
        elif phase == 'result_analysis':
            self.state.update_status(AgentStatus.PROCESSING)
            self._log_event("PHASE_RESULT_ANALYSIS", {
                'goal': goal,
                'allowed_actions': allowed_actions
            })
        elif phase in ['strategy_evolution', 'optimization']:
            self.state.update_status(AgentStatus.PROCESSING)
            self._log_event("PHASE_EVOLUTION_OPTIMIZATION", {
                'goal': goal,
                'parameters': execution_context.get('parameters', {})
            })
        elif phase == 'waiting':
            self.state.update_status(AgentStatus.WAITING)
            self._log_event("PHASE_WAITING", {
                'goal': goal
            })
    
    def _execute_decision(self, contract: AgentContract) -> Dict[str, Any]:
        """Wykonywanie decyzji na podstawie kontraktu"""
        # Wykorzystanie Decision Engine
        decision = self.decision_engine.make_decision(
            world_context=contract.world_data,
            model_info=contract.model_evaluation,
            weights=contract.current_weights,
            recommendations=contract.recommendations
        )
        
        return decision
    
    # ============================================================================
    # ETAP 0 KROK 3: Memory Integration Methods
    # ============================================================================
    
    def _retrieve_memory_context_for_contract(
        self, 
        contract: AgentContract
    ) -> Any:
        """
        Pobranie kontekstu pamięci dla danego kontraktu (ETAP 0 KROK 3).
        
        Args:
            contract: Kontrakt agenta
            
        Returns:
            MemoryContext lub None jeśli integracja jest wyłączona
        """
        if not self.is_memory_integration_enabled():
            logger.warning(f"Memory integration disabled for agent {self.agent_id}")
            return None
        
        try:
            # Prepared current situation from contract
            current_situation = self._extract_situation_from_contract(contract)
            
            # Pobranie kontekstu pamięci
            memory_context = self.memory_context_builder.build_memory_context(
                agent_id=self.agent_id,
                current_situation=current_situation,
                top_k=5,
                min_similarity=0.6
            )
            
            logger.debug(f"Retrieved memory context for agent {self.agent_id}: {memory_context.memory_stats}")
            return memory_context
            
        except Exception as e:
            logger.error(f"Error retrieving memory context for agent {self.agent_id}: {str(e)}")
            return None
    
    def _extract_situation_from_contract(self, contract: AgentContract) -> Dict[str, Any]:
        """
        Wyekstrahowanie bieżącej sytuacji z kontraktu dla celów wyszukiwania w pamięci.
        
        Args:
            contract: Kontrakt agenta
            
        Returns:
            Słownik opisujący bieżącą sytuację
        """
        situation = {
            'world_name': contract.world_name,
            'cycle_id': contract.cycle_id,
            'timestamp': contract.timestamp.isoformat() if hasattr(contract.timestamp, 'isoformat') else str(contract.timestamp),
            'world_data_keys': list(contract.world_data.keys()) if contract.world_data else [],
            'model_evaluation_keys': list(contract.model_evaluation.keys()) if contract.model_evaluation else [],
            'weights_keys': list(contract.current_weights.keys()) if contract.current_weights else [],
            'recommendations_count': len(contract.recommendations) if contract.recommendations else 0,
            'world_memory_keys': list(contract.world_memory.keys()) if contract.world_memory else [],
        }
        
        # Dodanie ExecutionContext jeśli dostępny
        if contract.execution_context:
            situation['phase'] = contract.execution_context.get('phase', 'unknown')
            situation['goal'] = contract.execution_context.get('goal', '')
            situation['allowed_actions'] = contract.execution_context.get('allowed_actions', [])
            situation['forbidden_actions'] = contract.execution_context.get('forbidden_actions', [])
        
        return situation
    
    def _enhance_decision_context(
        self, 
        contract: AgentContract, 
        memory_context: Any = None
    ) -> Any:
        """
        Rozszerzenie DecisionContext o kontekst pamięci (ETAP 0 KROK 3).
        
        Args:
            contract: Kontrakt agenta
            memory_context: MemoryContext (jeśli None, zostanie zbudowany)
            
        Returns:
            EnhancedDecisionContext z rozszerzonym kontekstem
        """
        if not self.is_memory_integration_enabled():
            logger.warning(f"Memory integration disabled, returning original context")
            from .decision_engine import DecisionContext
            return DecisionContext(
                world_data=contract.world_data,
                model_info=contract.model_evaluation,
                weights=contract.current_weights,
                recommendations=contract.recommendations
            )
        
        try:
            # Jeśli MemoryContext nie został podany, zbuduj go
            if memory_context is None:
                memory_context = self._retrieve_memory_context_for_contract(contract)
            
            # Utworzenie oryginalnego DecisionContext
            from .decision_engine import DecisionContext
            original_context = DecisionContext(
                world_data=contract.world_data,
                model_info=contract.model_evaluation,
                weights=contract.current_weights,
                recommendations=contract.recommendations,
                risk_factors=contract.world_data.get('risk_factors', {}),
                constraints=contract.world_data.get('constraints', {})
            )
            
            # Rozszerzenie kontekstu
            enhanced_context = self.memory_context_builder.enhance_decision_context(
                original_context=original_context,
                memory_context=memory_context
            )
            
            logger.debug(f"Enhanced decision context for agent {self.agent_id}")
            return enhanced_context
            
        except Exception as e:
            logger.error(f"Error enhancing decision context for agent {self.agent_id}: {str(e)}")
            from .decision_engine import DecisionContext
            return DecisionContext(
                world_data=contract.world_data,
                model_info=contract.model_evaluation,
                weights=contract.current_weights,
                recommendations=contract.recommendations
            )
    
    def _record_decision_to_collective_memory(
        self, 
        decision: Dict[str, Any], 
        contract: AgentContract
    ) -> Dict[str, Any]:
        """
        Zapis decyzji do pamięci kolektywnej (ETAP 0 KROK 3).
        
        Args:
            decision: Decyzja do zapisu
            contract: Powiązany kontrakt
            
        Returns:
            Status operacji
        """
        if not self.is_memory_integration_enabled():
            logger.warning(f"Memory integration disabled, skipping collective memory storage")
            return {'status': 'skipped', 'reason': 'memory_integration_disabled'}
        
        try:
            # Przygotowanie danych pozostałej do zapisu
            decision_data = {
                'decision_id': decision.get('decision_id', f"dec_{uuid.uuid4().hex[:12]}"),
                'decision_type': decision.get('decision_type', 'unknown'),
                'agent_id': self.agent_id,
                'parameters': decision.get('parameters', {}),
                'context': decision.get('context', {}),
                'confidence': decision.get('confidence', 0.0),
                'priority': decision.get('priority', 0),
                'status': decision.get('status', 'executed'),
                'timestamp': decision.get('created_at', datetime.now().isoformat())
            }
            
            # Dodanie danych z kontraktu
            contract_data = {
                'contract_id': contract.contract_id,
                'cycle_id': contract.cycle_id,
                'world_name': contract.world_name,
                'world_data_keys': list(contract.world_data.keys()) if contract.world_data else [],
                'execution_context': contract.execution_context if contract.execution_context else {}
            }
            
            # Zapis decyzji do pamięci kolektywnej
            result = self.memory_integration_layer.store_decision(
                agent_id=self.agent_id,
                decision_data=decision_data,
                contract=contract_data
            )
            
            logger.debug(f"Stored decision to collective memory: {result.get('decision_id')}")
            return result
            
        except Exception as e:
            logger.error(f"Error storing decision to collective memory: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def _store_experience_to_collective_memory(
        self,
        experience_data: Dict[str, Any],
        decision: Dict[str, Any],
        contract: AgentContract
    ) -> Dict[str, Any]:
        """
        Zapis doświadczenia do pamięci kolektywnej (ETAP 0 KROK 3).
        
        Args:
            experience_data: Dane doświadczenia
            decision: Powiązana decyzja
            contract: Powiązany kontrakt
            
        Returns:
            Status operacji
        """
        if not self.is_memory_integration_enabled():
            logger.warning(f"Memory integration disabled, skipping collective memory storage")
            return {'status': 'skipped', 'reason': 'memory_integration_disabled'}
        
        try:
            # Przygotowanie doświadczenia do zapisu
            experience = {
                'experience_id': f"exp_{uuid.uuid4().hex[:12]}",
                'type': 'decision_experience',
                'agent_id': self.agent_id,
                'action': decision.get('decision_type', 'unknown'),
                'result': experience_data.get('result', {}),
                'outcome': experience_data.get('outcome', 'unknown'),
                'confidence': decision.get('confidence', 0.0),
                'context': {
                    'contract_id': contract.contract_id,
                    'cycle_id': contract.cycle_id,
                    'world_name': contract.world_name,
                    'decision_id': decision.get('decision_id', 'unknown')
                },
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'decision_type': decision.get('decision_type', 'unknown'),
                    'agent_id': self.agent_id
                }
            }
            
            # Zapis doświadczenia do pamięci kolektywnej
            result = self.memory_integration_layer.store_experience(
                agent_id=self.agent_id,
                experience_data=experience,
                experience_type='decision_experience',
                context={'contract_id': contract.contract_id}
            )
            
            logger.debug(f"Stored experience to collective memory: {result.get('experience_id')}")
            return result
            
        except Exception as e:
            logger.error(f"Error storing experience to collective memory: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def _record_decision_and_observation(self, decision: Dict[str, Any], contract: AgentContract) -> None:
        """Zapisanie decyzji i obserwacji"""
        # Zapisanie decyzji
        self.memory.add_decision(decision)
        self.decision_engine.record_decision(decision)
        
        # Zapisanie obserwacji zwrotnej
        feedback_observation = {
            'contract_id': contract.contract_id,
            'decision_id': decision.get('decision_id', ''),
            'agent_id': self.agent_id,
            'decision_type': decision.get('decision_type', 'unknown'),
            'outcome': 'executed',
            'timestamp': datetime.now().isoformat()
        }
        self.memory.add_observation(feedback_observation)
        
        # Aktualizacja stanu
        self.state.complete_current_task({
            'decision_id': decision.get('decision_id'),
            'decision_type': decision.get('decision_type'),
            'observation_count': len(self.memory.observations),
            'decision_count': len(self.memory.decisions)
        })
        
        self.state.update_status(AgentStatus.IDLE)
    
    def execute_task(self, task: Union[AgentTask, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Wykonywanie pojedynczego zadania.
        
        Args:
            task: Zadanie do wykonania (AgentTask lub dict)
            
        Returns:
            Wynik wykonania zadania
        """
        # Konwersja do AgentTask, jeśli to dict
        if isinstance(task, dict):
            task = AgentTask(
                task_id=task.get('task_id', f"task_{uuid.uuid4().hex[:8]}"),
                task_type=task.get('task_type', 'default'),
                data=task.get('data', {}),
                priority=task.get('priority', 0)
            )
        
        # Dodanie zadania do stanu
        self.state.add_to_queue(task)
        
        # Uruchomienie zadania
        self.state.update_status(AgentStatus.PROCESSING)
        
        try:
            # Realizacja w zależności od typu zadania
            if task.task_type == 'process_contract':
                contract_data = task.data.get('contract', {})
                result = self.receive_contract(contract_data, task.data.get('cycle_id'))
                task.status = result['status']
                task.result = result
                
            elif task.task_type == 'make_decision':
                decision_data = task.data.get('decision_input', {})
                decision = self.decision_engine.make_decision(**decision_data)
                task.status = 'completed'
                task.result = decision
                
            elif task.task_type == 'observe':
                observation_data = task.data.get('data', {})
                obs_id = self.observation_manager.add_observation(observation_data)
                task.status = 'completed'
                task.result = {'observation_id': obs_id, 'status': 'recorded'}
                
            else:
                # Domyślna obsługa
                task.status = 'completed'
                task.result = {'message': f'Task {task.task_type} executed'}
            
            self.state.complete_current_task(task.result)
            self.state.update_status(AgentStatus.IDLE)
            
            return {
                'status': 'success',
                'task_id': task.task_id,
                'task_type': task.task_type,
                'result': copy.deepcopy(task.result),
                'agent_id': self.agent_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.state.fail_current_task(str(e))
            task.status = 'failed'
            task.result = {'error': str(e)}
            self.state.update_status(AgentStatus.ERROR)
            
            return {
                'status': 'error',
                'task_id': task.task_id,
                'task_type': task.task_type,
                'error': str(e),
                'agent_id': self.agent_id,
                'timestamp': datetime.now().isoformat()
            }
    
    def execute_cycle(self, cycle_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Wykonywanie pojedynczego cyklu (dla integracji z Pipeline - ETAP 5.3.2).
        
        Args:
            cycle_data: Dane cyklu z Pipeline (zawiera execution_context)
            
        Returns:
            Wynik wykonania cyklu
        """
        cycle_id = cycle_data.get('cycle_id', f"cycle_{uuid.uuid4().hex[:8]}")
        
        # ETAP 5.3.2: Pobranie ExecutionContext z danych cyklu
        execution_context = cycle_data.get('execution_context')
        
        try:
            # Tworzenie kontraktu z danych cyklu
            if 'contract_data' in cycle_data:
                contract = AgentContract(
                    contract_id=f"agent_contract_{uuid.uuid4().hex[:8]}",
                    cycle_id=cycle_id,
                    world_name=cycle_data.get('world_name', self.state.name),
                    world_data=cycle_data['contract_data'].get('results', {}),
                    model_evaluation=cycle_data['contract_data'].get('models', {}),
                    current_weights=cycle_data['contract_data'].get('weights', {}),
                    world_memory=cycle_data['contract_data'].get('observations', {}),
                    metadata={'source': 'pipeline', 'pipeline_reference': self.pipeline_reference},
                    # ETAP 5.3.2: Przekazanie ExecutionContext
                    execution_context=execution_context
                )
            else:
                contract = AgentContract(
                    contract_id=f"agent_contract_{uuid.uuid4().hex[:8]}",
                    cycle_id=cycle_id,
                    world_name=cycle_data.get('world_name', self.state.name),
                    world_data=cycle_data.get('world_data', {}),
                    metadata={'source': 'pipeline', 'pipeline_reference': self.pipeline_reference},
                    # ETAP 5.3.2: Przekazanie ExecutionContext
                    execution_context=execution_context
                )
            
            # Odbiór i przetworzenie kontraktu
            result = self.receive_contract(contract, cycle_id)
            
            if result['status'] == 'success':
                # Zwrotka dozorowania
                return {
                    'status': 'success',
                    'message': f'Agent {self.name} cycle {cycle_id} executed',
                    'cycle_id': cycle_id,
                    'agent_id': self.agent_id,
                    'agents_active': 1,
                    'execution_time': 0.1,
                    'contract_processed': True,
                    'observations_count': len(self.memory.observations),
                    'decisions_count': len(self.memory.decisions),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Agent {self.name} cycle failed',
                    'cycle_id': cycle_id,
                    'agent_id': self.agent_id,
                    'error': result.get('error', 'Unknown error'),
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Agent cycle error: {str(e)}',
                'cycle_id': cycle_id,
                'agent_id': self.agent_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def observe(self, observation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obserwacja wyników cyklu (dla integracji z Pipeline).
        
        Args:
            observation_data: Dane do obserwacji
            
        Returns:
            Wynik obserwacji
        """
        try:
            # Przekazanie do Observation Manager
            self.observation_manager.add_observation(observation_data)
            
            # Zapisanie w pamięci
            self.memory.add_observation(observation_data)
            
            return {
                'status': 'success',
                'message': 'Observation completed',
                'observations': observation_data,
                'agent_id': self.agent_id,
                'observation_count': len(self.memory.observations),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Observation failed: {str(e)}',
                'agent_id': self.agent_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_state(self) -> Dict[str, Any]:
        """Pobranie aktualnego stanu agenta"""
        return self.state.to_dict()
    
    def get_memory(self) -> Dict[str, Any]:
        """Pobranie pamięci agenta"""
        return self.memory.to_dict()
    
    def get_contracts(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Pobranie odebranych kontraktów"""
        if limit is None:
            return [c.to_dict() for c in self._contracts_received]
        else:
            return [c.to_dict() for c in self._contracts_received[-limit:]]
    
    def shutdown(self) -> Dict[str, Any]:
        """
        Zamknięcie agenta.
        
        Returns:
            Status zamknięcia
        """
        self._shutdown_requested = True
        self.state.update_status(AgentStatus.SHUTDOWN)
        
        # Wyczyszczenie kolejek
        while not self.state.task_queue.empty():
            try:
                self.state.task_queue.get_nowait()
            except:
                break
        
        return {
            'status': 'success',
            'message': f'Agent {self.name} shutdown completed',
            'agent_id': self.agent_id,
            'total_cycles_executed': self.state.cycle_count,
            'total_observations': len(self.memory.observations),
            'total_decisions': len(self.memory.decisions),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_personality(self) -> Optional[Dict[str, Any]]:
        """Pobranie stanu osobowości agenta"""
        if self.personality_state:
            return self.personality_state.to_dict()
        return None
    
    def get_personality_vector(self) -> Optional[Dict[str, float]]:
        """Pobranie wektora osobowości agenta"""
        if self.personality_state:
            return self.personality_state.get_personality_vector().to_dict()
        return None
    
    def get_personality_parameter(self, param_name: str) -> Optional[float]:
        """Pobranie konkretnego parametru osobowości"""
        if self.personality_state:
            from .personality_manager import PersonalityParameter
            param = getattr(PersonalityParameter, param_name.upper(), None)
            if param:
                return self.personality_state.get_parameter(param)
        return None
    
    def update_personality_from_decision(self, outcome: str, 
                                        confidence: float = 0.5,
                                        collaboration: float = 0.5,
                                        cycle_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Aktualizacja osobowości na podstawie wyniku decyzji.
        
        Args:
            outcome: Wynik decyzji ('correct', 'incorrect', 'partial', 'neutral')
            confidence: Pewność decyzji (0.0-1.0)
            collaboration: Stopień współpracy (0.0-1.0)
            cycle_id: ID cyklu
            
        Returns:
            Rekord zmiany osobowości
        """
        if self.personality_state:
            from .trust_manager import DecisionOutcome
            
            # Konwersja outcome na DecisionOutcome
            if outcome == 'correct':
                decision_outcome = DecisionOutcome.CORRECT
            elif outcome == 'incorrect':
                decision_outcome = DecisionOutcome.INCORRECT
            elif outcome == 'partial':
                decision_outcome = DecisionOutcome.PARTIAL
            else:
                decision_outcome = DecisionOutcome.NEUTRAL
            
            # Oblicz statystyki dla ewolucji
            success_rate = 1.0 if decision_outcome == DecisionOutcome.CORRECT else (
                0.5 if decision_outcome == DecisionOutcome.PARTIAL else 0.0
            )
            
            # Zastosuj ewolucję
            change = self.personality_state.apply_evolution(
                success_rate=success_rate,
                decision_quality=confidence,
                collaboration_score=collaboration,
                cycle_id=cycle_id
            )
            
            return change.to_dict() if change else None
        return None
    
    def update_trust_from_decision(self, target_agent_id: Optional[str] = None,
                                  outcome: str = 'neutral',
                                  confidence: float = 0.5,
                                  cycle_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Aktualizacja zaufania na podstawie wyniku decyzji.
        
        Args:
            target_agent_id: ID agenta, którego zaufanie jest aktualizowane (domyślnie self)
            outcome: Wynik decyzji ('correct', 'incorrect', 'partial', 'neutral')
            confidence: Pewność decyzji (0.0-1.0)
            cycle_id: ID cyklu
            
        Returns:
            Rekord aktualizacji zaufania
        """
        from .trust_manager import DecisionOutcome
        
        # Konwersja outcome na DecisionOutcome
        if outcome == 'correct':
            decision_outcome = DecisionOutcome.CORRECT
        elif outcome == 'incorrect':
            decision_outcome = DecisionOutcome.INCORRECT
        elif outcome == 'partial':
            decision_outcome = DecisionOutcome.PARTIAL
        else:
            decision_outcome = DecisionOutcome.NEUTRAL
        
        target = target_agent_id or self.agent_id
        
        # Aktualizuj zaufanie w TrustManager
        if self.trust_manager and target != self.agent_id:
            update = self.trust_manager.update_trust_from_feedback(
                from_agent_id=self.agent_id,
                to_agent_id=target,
                outcome=decision_outcome,
                confidence=confidence,
                cycle_id=cycle_id
            )
            return update.to_dict() if update else None
        
        # Aktualizuj własną reputację
        if self.agent_trust_state:
            self.agent_trust_state.update_reputation_from_decision(
                decision_outcome, confidence, collaboration=0.5, cycle_id=cycle_id
            )
            return {'status': 'success', 'message': 'Reputation updated'}
        
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Pobranie statystyk agenta"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'status': self.state.status.value,
            'mode': self.state.mode.value,
            'cycle_count': self.state.cycle_count,
            'success_count': self.state.success_count,
            'error_count': self.state.error_count,
            'observations_count': len(self.memory.observations),
            'decisions_count': len(self.memory.decisions),
            'contracts_received': len(self._contracts_received),
            'tasks_in_queue': self.state.task_queue.qsize(),
            'short_term_memory_size': len(self.memory.short_term_memory),
            'long_term_memory_size': len(self.memory.long_term_memory),
            'created_at': self.state.created_at.isoformat(),
            'last_activity': self.state.last_activity.isoformat()
        }
    
    # Obsługa callbacków
    def on_contract_received(self, callback: Callable) -> None:
        """Rejestracja callbacka na odebranie kontraktu"""
        self._on_contract_callbacks.append(callback)
    
    def on_decision_made(self, callback: Callable) -> None:
        """Rejestracja callbacka na podjęcie decyzji"""
        self._on_decision_callbacks.append(callback)
    
    def _notify_contract_callbacks(self, contract: AgentContract) -> None:
        """Powiadomienie callbacków o odebraniu kontraktu"""
        for callback in self._on_contract_callbacks:
            try:
                callback(contract, self)
            except Exception:
                pass
    
    def _notify_decision_callbacks(self, decision: Dict[str, Any]) -> None:
        """Powiadomienie callbacków o podjęciu decyzji"""
        for callback in self._on_decision_callbacks:
            try:
                callback(decision, self)
            except Exception:
                pass


class AgentRuntimeManager:
    """
    Menadżer Agent Runtime - zastępuje AgentRuntimeInterface w Pipeline.
    
    Odpowiedzialność:
    - Uruchamianie agentów
    - Przekazywanie im kontekstu świata
    - Odbieranie decyzji
    - Zapis obserwacji
    """
    
    def __init__(self, pipeline_reference: Optional[str] = None,
                 number_of_agents: int = 6,
                 world_name: str = "SSI_V5_WORLD"):
        """
        Inicjalizacja AgentRuntimeManager.
        
        Args:
            pipeline_reference: Referencja do Pipeline
            number_of_agents: Liczba agentów do utworzenia (domyślnie 6)
            world_name: Nazwa świata
        """
        self.pipeline_reference = pipeline_reference
        self.world_name = world_name
        self.agents: Dict[str, AgentRuntime] = {}
        self.agent_names = [f"Agent_{i:02d}" for i in range(1, number_of_agents + 1)]
        self._initialized = False
        self.cycle_count = 0
        self._lock = Lock()
        
        # Statystyki
        self.total_contracts_sent = 0
        self.total_decisions_received = 0
        self.total_observations_recorded = 0
        
        # Zdarzenia
        self._event_log: List[Dict[str, Any]] = []
        
        # Historia decyzji i obserwacji wszystkich agentów
        self.decision_history: List[Dict[str, Any]] = []
        self.observation_history: List[Dict[str, Any]] = []
        
        # Pamięć kolektywna - referencja do CollectiveManager (opcjonalna)
        self.collective_manager = None
        
        # ETAP 0 KROK 1: Memory Integration Layer
        self.memory_integration_layer = None
        
        # Referencja do MemoryManager z Teacher Layer (opcjonalna)
        self.memory_manager = None
        
        # Personality Manager
        self.personality_manager = None
        
        # Trust Manager
        self.trust_manager = None
    
    def initialize(self) -> Dict[str, Any]:
        """
        Inicjalizacja menadżera i wszystkich agentów.
        
        Returns:
            Status inicjalizacji
        """
        self._log_event("AGENT_MANAGER_INITIALIZATION_START")
        
        initialization_result = {
            'status': 'success',
            'message': 'AgentRuntimeManager initialization started',
            'agents_initialized': 0,
            'agents_failed': 0,
            'agent_details': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Tworzenie agentów
            for agent_name in self.agent_names:
                agent_id = f"agent_{agent_name.lower()}"
                
                # Generacja unikalnego ID
                unique_id = f"{agent_name}_{uuid.uuid4().hex[:8]}"
                
                # Tworzenie agenta
                agent = AgentRuntime(
                    agent_id=unique_id,
                    name=agent_name,
                    mode=AgentMode.AUTO,
                    pipeline_reference=self.pipeline_reference
                )
                
                # Inicjalizacja agenta
                init_result = agent.initialize()
                
                if init_result['status'] == 'success':
                    self.agents[unique_id] = agent
                    initialization_result['agents_initialized'] += 1
                    initialization_result['agent_details'].append({
                        'agent_id': unique_id,
                        'name': agent_name,
                        'status': init_result['status']
                    })
                else:
                    initialization_result['agents_failed'] += 1
                    initialization_result['agent_details'].append({
                        'agent_id': unique_id,
                        'name': agent_name,
                        'status': init_result['status'],
                        'error': init_result.get('error', 'Unknown error')
                    })
            
            self._initialized = initialization_result['agents_initialized'] > 0
            self._log_event("AGENT_MANAGER_INITIALIZATION_COMPLETE", {
                'agents_initialized': initialization_result['agents_initialized'],
                'agents_failed': initialization_result['agents_failed']
            })
            
            # ETAP 0 KROK 3: Setup memory integration for all agents
            self._setup_memory_integration()
            
            return initialization_result
            
        except Exception as e:
            initialization_result['status'] = 'error'
            initialization_result['error'] = str(e)
            self._log_event("AGENT_MANAGER_INITIALIZATION_ERROR", {
                'error': str(e)
            }, level="ERROR")
            return initialization_result
    
    def _setup_memory_integration(self) -> None:
        """
        Setup memory integration for all agents (ETAP 0 KROK 3).
        
        Tworzy MemoryIntegrationLayer i przypisuje go do wszystkich agentów.
        """
        if self.collective_manager is None:
            logger.warning("collective_manager not set, memory integration will be disabled")
            return
        
        try:
            # Import tutaj, aby unikać zależności cyklicznych
            from ..memory.memory_integration import MemoryIntegrationLayer
            
            # Tworzenie warstwy integracji pamięci
            self.memory_integration_layer = MemoryIntegrationLayer(self.collective_manager)
            
            # Inicjalizacja warstwy
            init_result = self.memory_integration_layer.initialize()
            if init_result.get('status') == 'success':
                logger.info("MemoryIntegrationLayer initialized for AgentRuntimeManager")
                
                # Przypisanie warstwy do wszystkich agentów
                for agent_id, agent in self.agents.items():
                    agent.set_memory_integration_reference(self.memory_integration_layer)
                    logger.debug(f"Memory integration enabled for agent {agent_id}")
            else:
                logger.error(f"Failed to initialize MemoryIntegrationLayer: {init_result.get('error', 'Unknown')}")
                
        except Exception as e:
            logger.error(f"Error setting up memory integration: {str(e)}")
    
    def set_collective_manager_reference(self, collective_manager: Any) -> None:
        """
        Ustawienie referencji do CollectiveManager (ETAP 0 KROK 3).
        
        Args:
            collective_manager: Instancja CollectiveMemoryManager
        """
        self.collective_manager = collective_manager
        logger.info("CollectiveMemoryManager reference set for AgentRuntimeManager")
        
        # Jeśli agenci są już zainicjalizowani, uaktualnij integrację pamięci
        if self._initialized and self.agents:
            self._setup_memory_integration()
            # Ponowne przypisanie referencji do agentów
            for agent_id, agent in self.agents.items():
                if self.memory_integration_layer:
                    agent.set_memory_integration_reference(self.memory_integration_layer)
    
    def execute_cycle(self, cycle_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Wykonywanie jednego cyklu przez wszystkich agentów.
        
        Args:
            cycle_data: Dane cyklu z Pipeline
            
        Returns:
            Wynik wykonania cyklu
        """
        if not self._initialized or not self.agents:
            return {
                'status': 'error',
                'error': 'AgentRuntimeManager not initialized or no agents available',
                'timestamp': datetime.now().isoformat()
            }
        
        self.cycle_count += 1
        cycle_id = cycle_data.get('cycle_id', f"cycle_{self.cycle_count}")
        
        execution_result = {
            'status': 'success',
            'message': f'Agent cycle {self.cycle_count} executed',
            'cycle_id': cycle_id,
            'agents_active': len(self.agents),
            'execution_time': 0.0,
            'agent_results': [],
            'timestamp': datetime.now().isoformat()
        }
        
        start_time = time.time()
        
        try:
            # Przekazanie kontraktu do wszystkich agentów
            for agent_id, agent in self.agents.items():
                try:
                    agent_result = agent.execute_cycle(cycle_data)
                    execution_result['agent_results'].append(agent_result)
                    self.total_contracts_sent += 1
                    
                except Exception as e:
                    execution_result['agent_results'].append({
                        'status': 'error',
                        'agent_id': agent_id,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
            
            execution_result['execution_time'] = time.time() - start_time
            execution_result['contracts_sent'] = self.total_contracts_sent
            
            # Zbieranie wszystkich decyzji od agentów
            all_decisions = {}
            for agent_id, agent in self.agents.items():
                decisions = agent.memory.get_decisions()
                if decisions:
                    all_decisions[agent_id] = [d for d in decisions if isinstance(d, dict)]
            
            if all_decisions:
                execution_result['decisions'] = all_decisions
            
            self._log_event("AGENT_CYCLE_EXECUTION_COMPLETE", {
                'cycle_id': cycle_id,
                'duration': execution_result['execution_time'],
                'agents_active': len(self.agents),
                'status': 'success'
            })
            
            return execution_result
            
        except Exception as e:
            execution_result['status'] = 'error'
            execution_result['error'] = str(e)
            execution_result['execution_time'] = time.time() - start_time
            
            self._log_event("AGENT_CYCLE_EXECUTION_ERROR", {
                'cycle_id': cycle_id,
                'error': str(e),
                'duration': execution_result['execution_time']
            }, level="ERROR")
            
            return execution_result
    
    def observe(self, observation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obserwacja wyników cyklu przez wszystkich agentów.
        
        Args:
            observation_data: Dane do obserwacji
            
        Returns:
            Wynik obserwacji
        """
        observation_result = {
            'status': 'success',
            'message': 'Observation completed',
            'observations': observation_data,
            'agents_notified': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            for agent_id, agent in self.agents.items():
                try:
                    obs_result = agent.observe(observation_data)
                    if obs_result['status'] == 'success':
                        observation_result['agents_notified'] += 1
                        self.total_observations_recorded += 1
                        
                except Exception as e:
                    # Kontynuuj z następnymi agentami
                    continue
            
            self._log_event("OBSERVATION_COMPLETE", {
                'agents_notified': observation_result['agents_notified'],
                'total_observations': self.total_observations_recorded
            })
            
            return observation_result
            
        except Exception as e:
            observation_result['status'] = 'error'
            observation_result['error'] = str(e)
            self._log_event("OBSERVATION_ERROR", {
                'error': str(e)
            }, level="ERROR")
            return observation_result
    
    def get_agent(self, agent_id: str) -> Optional[AgentRuntime]:
        """Pobranie konkretnego agenta"""
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> Dict[str, AgentRuntime]:
        """Pobranie wszystkich agentów"""
        return copy.deepcopy(self.agents)
    
    def get_agent_statistics(self) -> List[Dict[str, Any]]:
        """Pobranie statystyk wszystkich agentów"""
        statistics = []
        for agent_id, agent in self.agents.items():
            stats = agent.get_statistics()
            statistics.append(stats)
        return statistics
    
    def shutdown(self) -> Dict[str, Any]:
        """
        Zamknięcie menadżera i wszystkich agentów.
        
        Returns:
            Status zamknięcia
        """
        self._log_event("AGENT_MANAGER_SHUTDOWN_START")
        
        shutdown_result = {
            'status': 'success',
            'message': 'AgentRuntimeManager shutdown completed',
            'total_cycles_executed': self.cycle_count,
            'total_contracts_sent': self.total_contracts_sent,
            'total_observations_recorded': self.total_observations_recorded,
            'agents_shutdown': 0,
            'agent_details': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            for agent_id, agent in self.agents.items():
                try:
                    agent_shutdown = agent.shutdown()
                    shutdown_result['agent_details'].append(agent_shutdown)
                    shutdown_result['agents_shutdown'] += 1
                except Exception as e:
                    shutdown_result['agent_details'].append({
                        'status': 'error',
                        'agent_id': agent_id,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
            
            self.agents.clear()
            self._initialized = False
            self._log_event("AGENT_MANAGER_SHUTDOWN_COMPLETE", {
                'agents_shutdown': shutdown_result['agents_shutdown'],
                'total_cycles': self.cycle_count
            })
            
            return shutdown_result
            
        except Exception as e:
            shutdown_result['status'] = 'error'
            shutdown_result['error'] = str(e)
            self._log_event("AGENT_MANAGER_SHUTDOWN_ERROR", {
                'error': str(e)
            }, level="ERROR")
            return shutdown_result
    
    def add_agent(self, agent_config: Dict[str, Any]) -> str:
        """
        Dodanie nowego agenta.
        
        Args:
            agent_config: Konfiguracja agenta
            
        Returns:
            Identifikator nowego agenta
        """
        agent_name = agent_config.get('name', f"Agent_{len(self.agents) + 1}")
        agent_id = f"{agent_name}_{uuid.uuid4().hex[:8]}"
        
        agent = AgentRuntime(
            agent_id=agent_id,
            name=agent_name,
            mode=AgentMode(agent_config.get('mode', 'AUTO')),
            pipeline_reference=self.pipeline_reference
        )
        
        init_result = agent.initialize()
        
        if init_result['status'] == 'success':
            self.agents[agent_id] = agent
            return agent_id
        else:
            raise Exception(f"Failed to initialize new agent: {init_result.get('error', 'Unknown error')}")
    
    def remove_agent(self, agent_id: str) -> bool:
        """Usunięcie agenta"""
        if agent_id in self.agents:
            try:
                self.agents[agent_id].shutdown()
                del self.agents[agent_id]
                return True
            except Exception:
                return False
        return False
    
    def _log_event(self, event_type: str, data: Optional[Dict[str, Any]] = None, 
                   level: str = "INFO") -> None:
        """Logowanie zdarzenia"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'pipeline_reference': self.pipeline_reference,
            'data': data or {}
        }
        self._event_log.append(event)
    
    def get_event_log(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Pobranie dziennika zdarzeń"""
        if limit is None:
            return copy.deepcopy(self._event_log)
        else:
            return copy.deepcopy(self._event_log[-limit:])
    
    def set_collective_manager_reference(self, collective_manager: Any) -> None:
        """Ustawienie referencji do CollectiveManager"""
        self.collective_manager = collective_manager
        self._log_event("COLLECTIVE_MANAGER_REFERENCE_SET")
    
    def set_memory_manager_reference(self, memory_manager: Any) -> None:
        """Ustawienie referencji do MemoryManager z Teacher Layer"""
        self.memory_manager = memory_manager
        self._log_event("MEMORY_MANAGER_REFERENCE_SET")
    
    def set_personality_manager_reference(self, personality_manager: Any) -> None:
        """Ustawienie referencji do PersonalityManager"""
        self.personality_manager = personality_manager
        self._log_event("PERSONALITY_MANAGER_REFERENCE_SET")
    
    def set_trust_manager_reference(self, trust_manager: Any) -> None:
        """Ustawienie referencji do TrustManager"""
        self.trust_manager = trust_manager
        
        # Przekaż referencję TrustManager do wszystkich agentów
        # TrustManager jest odporny na podwójną inicjalizację (mechanizm idempotencji)
        if trust_manager:
            agent_names = {agent_id: agent.name for agent_id, agent in self.agents.items()}
            trust_manager.initialize_all_trust(list(self.agents.keys()), agent_names)
            
            # Przekaż referencję do każdego agenta
            for agent_id, agent in self.agents.items():
                agent.set_trust_manager_reference(trust_manager)
        
        self._log_event("TRUST_MANAGER_REFERENCE_SET")
    
    def initialize_personality_states(self) -> None:
        """Inicjalizacja stanów osobowości wszystkich agentów"""
        if self.personality_manager:
            for agent_id, agent in self.agents.items():
                # Jeśli agent nie ma jeszcze stanu osobowości, utwórz go
                if not agent.personality_state:
                    agent._initialize_personality()
                    
                # Zarejestruj stan w PersonalityManager
                if agent.personality_state:
                    # Personality state jest już utworzony w __init__ agenta
                    pass
        else:
            # Utwórz lokalny PersonalityManager
            from .personality_manager import PersonalityManager
            self.personality_manager = PersonalityManager(world_name=self.world_name)
            
            # Inicjalizuj stany dla wszystkich agentów
            for agent_id, agent in self.agents.items():
                if not agent.personality_state:
                    agent._initialize_personality()
    
    def get_all_personality_states(self) -> Dict[str, Any]:
        """Pobranie wszystkich stanów osobowości agentów"""
        if self.personality_manager:
            return self.personality_manager.get_personality_summary()
        else:
            # Zbierz informacje bezpośrednio z agentów
            summary = {'total_agents': len(self.agents), 'agents': {}}
            for agent_id, agent in self.agents.items():
                if agent.personality_state:
                    summary['agents'][agent_id] = agent.personality_state.to_dict()
            return summary
    
    def get_all_trust_states(self) -> Optional[Dict[str, Any]]:
        """Pobranie wszystkich stanów zaufania"""
        if self.trust_manager:
            return self.trust_manager.get_trust_summary()
        return None
    
    def update_all_trust_from_cycle(self, cycle_id: str, 
                                     decisions: Dict[str, Dict[str, Any]]) -> None:
        """
        Aktualizacja zaufania i reputacji na podstawie wyników cyklu.
        
        Args:
            cycle_id: ID cyklu
            decisions: Słownik {agent_id: decision_data}
        """
        from .trust_manager import DecisionOutcome
        
        if not self.trust_manager:
            return
        
        # Dla każdej decyzji, zaktualizuj trust i personality
        for agent_id, decision_data in decisions.items():
            agent = self.agents.get(agent_id)
            if not agent:
                continue
            
            # Pobierz wynik decyzji
            outcome = decision_data.get('outcome', 'neutral')
            confidence = decision_data.get('confidence', 0.5)
            
            # Konwersja outcome
            if outcome == 'correct':
                decision_outcome = DecisionOutcome.CORRECT
            elif outcome == 'incorrect':
                decision_outcome = DecisionOutcome.INCORRECT
            elif outcome == 'partial':
                decision_outcome = DecisionOutcome.PARTIAL
            else:
                decision_outcome = DecisionOutcome.NEUTRAL
            
            # Aktualizuj reputację agenta
            self.trust_manager.update_reputation_from_decision(
                agent_id=agent_id,
                outcome=decision_outcome,
                confidence=confidence,
                collaboration=0.5,  # Domyślnie
                cycle_id=cycle_id
            )
            
            # Aktualizuj osobowość agenta
            if agent.personality_state:
                success_rate = 1.0 if decision_outcome == DecisionOutcome.CORRECT else (
                    0.5 if decision_outcome == DecisionOutcome.PARTIAL else 0.0
                )
                agent.personality_state.apply_evolution(
                    success_rate=success_rate,
                    decision_quality=confidence,
                    collaboration_score=0.5,
                    cycle_id=cycle_id
                )
    
    def get_decision_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Pobranie historii decyzji wszystkich agentów"""
        if limit is None:
            return copy.deepcopy(self.decision_history)
        else:
            return copy.deepcopy(self.decision_history[-limit:])
    
    def get_observation_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Pobranie historii obserwacji wszystkich agentów"""
        if limit is None:
            return copy.deepcopy(self.observation_history)
        else:
            return copy.deepcopy(self.observation_history[-limit:])
    
    def get_all_agents_decisions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Pobranie wszystkich decyzji od wszystkich agentów"""
        all_decisions = {}
        for agent_id, agent in self.agents.items():
            agent_decisions = agent.get_statistics().get('decisions_count', 0)
            all_decisions[agent_id] = [
                d for d in agent.memory.get_decisions() 
                if isinstance(d, dict)
            ]
        return all_decisions
    
    def get_all_agents_observations(self) -> Dict[str, List[Dict[str, Any]]]:
        """Pobranie wszystkich obserwacji od wszystkich agentów"""
        all_observations = {}
        for agent_id, agent in self.agents.items():
            all_observations[agent_id] = [
                o for o in agent.memory.get_observations() 
                if isinstance(o, dict)
            ]
        return all_observations


# Eksportowane funkcje i klasy
__all__ = [
    'AgentStatus',
    'AgentMode', 
    'AgentTask',
    'AgentMemory',
    'AgentState',
    'AgentContract',
    'AgentRuntime',
    'AgentRuntimeManager'
]
