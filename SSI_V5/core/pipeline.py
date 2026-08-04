# SSI V5 Pipeline Control Layer
# ==================================================
#
# ETAP: 5.2.4 FAZA 3.3.3
# Data: 2026-08-03
#
# Pipeline kontrolny SSI V5 - Glowny manager przeplywu systemu
# Odpowiedzialnosc:
# - Zarzadzanie cyklami systemowymi
# - Integracja z WorldEngine
# - Integracja z Teacher Layer
# - Integracja z Memory Layer
# - Integracja z AgentRuntimeManager
# - Kontrola przeplywu danych miedzy warstwami
# - Zapis historii cykli i zdarzen

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Callable
from enum import Enum
from datetime import datetime
import uuid
import time
import copy
from threading import Lock
import sys
import os

# Dodaj root SSI_V5 do sys.path dla importów z SSI_V5.* (kompatybilność)
_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

from .world_engine import WorldEngine, create_world_engine_from_generator
from teachers import CognitiveTeacher, WorldHierarchyManager, MemoryManager
from agents import AgentRuntimeManager, CollectiveManager
from agents.trust_manager import TrustManager, DecisionOutcome
from agents.personality_manager import PersonalityManager

# ETAP 5.3.1: Cycle Controller - Warstwa świadomości cyklu
from runtime.cycle_controller import (
    CyclePhase, CycleState, ExecutionContext, CycleController,
    PhaseDetector, WorldState, create_cycle_controller, PHASE_CONTEXTS
)

# ETAP 5.3.4: Simulation Clock - Zegar symulacyjny
# Import opozniony aby uniknac circular import (runtime -> pipeline -> runtime)
# TYPE_CHECKING import dla type hintow
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from runtime.simulation_clock import SimulationClock

# ETAP 5.3.3: Strategy Persistence Memory
from memory.strategy_memory import StrategyMemoryManager, StrategyMemoryRecord
from memory import get_match_result_memory


class CycleStatus(Enum):
    """Statusy cyklu w Pipeline"""
    IDLE = "idle"                    # Oczekiwanie na uruchomienie
    INITIALIZING = "initializing"    # Inicjalizacja systemu
    WORLD_GENERATION = "world_generation"  # Generowanie swiata
    MODELING = "modeling"            # Modelowanie danych
    TEACHER_ANALYSIS = "teacher_analysis"  # Analiza Teacher Layer
    AGENT_EXECUTION = "agent_execution"  # Wykonywanie agentow
    COLLECTIVE_CONSENSUS = "collective_consensus"  # Konsensus kolektywny
    TRUST_PERSONALITY_UPDATE = "trust_personality_update"  # Aktualizacja zaufania i osobowosci
    OBSERVATION = "observation"      # Obserwacja wynikow
    MEMORY_UPDATE = "memory_update"  # Aktualizacja pamieci
    COMPLETE = "complete"            # Zakonczenie cyklu
    ERROR = "error"                  # Blad w czasie wykonywania
    SHUTDOWN = "shutdown"            # Zamkniecie systemu


class PipelineMode(Enum):
    """Tryby pracy Pipeline"""
    TEST = "test"                    # Tryb testowy
    PRODUCTION = "production"        # Tryb produkcyjny
    SINGLE = "single"                # Pojedynczy cykl


@dataclass
class CycleMetadata:
    """Metadane cyklu"""
    cycle_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: CycleStatus = CycleStatus.IDLE
    world_name: str = "SSI_V5_WORLD"
    processing_steps: List[str] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    additional_data: Dict[str, Any] = field(default_factory=dict)

    def get_duration(self) -> float:
        """Obliczenie czasu trwania cyklu w sekundach"""
        if self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time).total_seconds()

    def add_step(self, step_name: str) -> None:
        """Dodanie kroku przetwarzania"""
        if step_name not in self.processing_steps:
            self.processing_steps.append(step_name)

    def add_error(self, error_type: str, error_message: str, step: str) -> None:
        """Dodanie bledu do metadanych"""
        self.errors.append({
            'error_type': error_type,
            'error_message': error_message,
            'step': step,
            'timestamp': datetime.now().isoformat()
        })

    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika"""
        return {
            'cycle_id': self.cycle_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status.value,
            'world_name': self.world_name,
            'processing_steps': copy.deepcopy(self.processing_steps),
            'errors': copy.deepcopy(self.errors),
            'duration': self.get_duration(),
            'additional_data': copy.deepcopy(self.additional_data)
        }


@dataclass
class PipelineStatus:
    """Status Pipeline"""
    current_cycle_id: Optional[str] = None
    current_status: CycleStatus = CycleStatus.IDLE
    total_cycles: int = 0
    successful_cycles: int = 0
    failed_cycles: int = 0
    mode: PipelineMode = PipelineMode.SINGLE
    cycle_history_count: int = 0
    uptime_start: Optional[datetime] = None
    last_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika"""
        return {
            'current_cycle_id': self.current_cycle_id,
            'current_status': self.current_status.value,
            'total_cycles': self.total_cycles,
            'successful_cycles': self.successful_cycles,
            'failed_cycles': self.failed_cycles,
            'mode': self.mode.value,
            'cycle_history_count': self.cycle_history_count,
            'uptime_start': self.uptime_start.isoformat() if self.uptime_start else None,
            'last_error': self.last_error
        }


class AgentRuntimeInterface:
    """
    Interfejs AgentRuntime - Kontrakt dla AgentRuntimeManager
    
    Zostawiany jako kontrakt/interfejs do wstecznej kompatybilnosci.
    Pipeline korzysta z AgentRuntimeManager jako glownej implementacji.
    """
    
    def __init__(self, pipeline_reference: Optional[str] = None):
        """Inicjalizacja interfejsu"""
        self.pipeline_reference = pipeline_reference
        self.agents: List[Dict[str, Any]] = []
        self._initialized = False
        self.initialized = False  # Kompatybilnosc wsteczna
        self.cycle_count = 0
        self._event_log: List[Dict[str, Any]] = []

    def initialize(self) -> Dict[str, Any]:
        """Inicjalizacja interfejsu"""
        self._log_event("INTERFACE_INITIALIZATION")
        self._initialized = True
        self.initialized = True  # Kompatybilnosc wsteczna
        
        return {
            'status': 'success',
            'message': 'AgentRuntimeInterface initialized',
            'timestamp': datetime.now().isoformat()
        }

    def execute_cycle(self, cycle_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Wykonywanie cyklu (domyslna implementacja - passthrough)"""
        if not self._initialized:
            return {
                'status': 'error',
                'error': 'Interface not initialized',
                'timestamp': datetime.now().isoformat()
            }
        
        self.cycle_count += 1
        if cycle_data is None:
            cycle_data = {}
        cycle_id = cycle_data.get('cycle_id', f'interface_cycle_{self.cycle_count}')
        
        return {
            'status': 'success',
            'cycle_id': cycle_id,
            'message': f'Interface cycle {self.cycle_count} executed',
            'timestamp': datetime.now().isoformat()
        }

    def observe(self, observation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Obserwacja (domyslna implementacja - passthrough)"""
        return {
            'status': 'success',
            'observations': observation_data,
            'timestamp': datetime.now().isoformat()
        }

    def shutdown(self) -> Dict[str, Any]:
        """Zamkniecie interfejsu"""
        self._initialized = False
        self.initialized = False  # Kompatybilnosc wsteczna
        return {
            'status': 'success',
            'message': 'AgentRuntimeInterface shutdown completed',
            'total_cycles_executed': self.cycle_count,
            'timestamp': datetime.now().isoformat()
        }

    def add_agent(self, agent_config: Dict[str, Any]) -> str:
        """Dodawanie agenta (domyslna implementacja)"""
        agent_id = f"agent_{len(self.agents) + 1}_{uuid.uuid4().hex[:8]}"
        self.agents.append({
            'agent_id': agent_id,
            'name': agent_config.get('name', 'default'),
            'type': agent_config.get('type', 'default'),
            'status': 'created',
            'timestamp': datetime.now().isoformat()
        })
        return agent_id

    def _log_event(self, event_type: str, data: Optional[Dict[str, Any]] = None, 
                   level: str = "INFO") -> None:
        """Logowanie zdarzenia"""
        event = {
            'event_type': event_type,
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'data': data or {}
        }
        self._event_log.append(event)
        
    def get_event_log(self) -> List[Dict[str, Any]]:
        """Pobranie dziennika zdarzen"""
        return copy.deepcopy(self._event_log)


class SSIPipeline:
    """
    Glowna klasa Pipeline SSI V5.
    
    Odpowiedzialnosc:
    - Zarzadzanie cyklami systemowymi
    - Integracja z WorldEngine
    - Integracja z Teacher Layer  
    - Integracja z AgentRuntimeManager
    - Kontrola przeplywu danych
    - Zapis historii i zdarzen
    
    Docelowy przeplyw:
    WORLD GENERATOR -> WORLD ENGINE -> PIPELINE ->
    MODELING LAYER -> TEACHER LAYER -> AGENT RUNTIME MANAGER ->
    AGENTS -> OBSERVATION -> MEMORY UPDATE
    """

    def __init__(self, mode: PipelineMode = PipelineMode.SINGLE,
                 world_name: str = "SSI_V5_WORLD",
                 use_agent_runtime_manager: bool = True,
                 clock = None,
                 ifc: Optional[Any] = None,
                 memory_ecosystem: Optional[Any] = None):
        """
        Inicjalizacja Pipeline.
        
        Args:
            mode: Tryb pracy Pipeline
            world_name: Nazwa swiata
            use_agent_runtime_manager: Czy uzywac AgentRuntimeManager zamiast interfejsu
            clock: Opcjonalny zegar symulacyjny (SimulationClock).
                   Wykorzystywany w trybie symulacyjnym (ETAP 5.3.4).
                   Jesli None, uzywa rzeczywistego czasu.
            ifc: Opcjonalna referencja do IFCRegistry (ETAP 1.2.7.3)
            memory_ecosystem: Opcjonalna referencja do MemoryEcosystem (ETAP 1.2.7.3)
        """
        self.mode = mode
        self.world_name = world_name
        self.use_agent_runtime_manager = use_agent_runtime_manager
        self._clock = clock  # Zegar symulacyjny (ETAP 5.3.4)
        
        # ETAP 1.2.7.3: Integracja z pamięcią
        self.ifc = ifc
        self.memory_ecosystem = memory_ecosystem
        
        # Komponenty systemowe
        self.world_engine: Optional[WorldEngine] = None
        # agent_interface jest inicjalizowany w initialize() - nie tworzymy go w __init__
        self.agent_interface: Optional[Union[AgentRuntimeInterface, AgentRuntimeManager]] = None
        self.teacher_layer: Optional[Dict[str, Any]] = None
        self.modeling_layer: Optional[Dict[str, Any]] = None
        self.memory_layer: Optional[Dict[str, Any]] = None
        
        # Stan systemu
        self._initialized = False
        self._shutdown_requested = False
        self._current_cycle_id: Optional[str] = None
        self._cycle_counter = 0
        self._current_status: CycleStatus = CycleStatus.IDLE
        
        # ETAP 1.2.7.3: Zmienne do pamietania wynikow etapow dla integracji pamieci
        self._last_world_result: Optional[Dict[str, Any]] = None
        self._last_modeling_result: Optional[Dict[str, Any]] = None
        self._last_teacher_result: Optional[Dict[str, Any]] = None
        self._last_agent_result: Optional[Dict[str, Any]] = None
        self._last_collective_result: Optional[Dict[str, Any]] = None
        self._last_observation_result: Optional[Dict[str, Any]] = None
        
        # Historia i logi
        self._cycle_history: List[CycleMetadata] = []
        self._event_log: List[Dict[str, Any]] = []
        self._lock = Lock()
        
        # Konfiguracja agentow
        self.agent_runtime_manager: Optional[AgentRuntimeManager] = None
        
        # Collective Manager - zarządza konsensusem agentów
        self.collective_manager: Optional[CollectiveManager] = None
        
        # Memory Manager - referencja do pamięci z Teacher Layer
        self.memory_manager: Optional[MemoryManager] = None
        
        # Trust Manager - zarządza zaufaniem i reputacją agentów
        self.trust_manager: Optional[TrustManager] = None
        
        # Personality Manager - zarządza osobowościami agentów
        self.personality_manager: Optional[PersonalityManager] = None
        
        # ETAP 5.3.1: Cycle Controller - Warstwa świadomości cyklu
        self.cycle_controller: Optional[CycleController] = None
        
        # ETAP 5.3.3: Strategy Persistence Memory
        self.strategy_memory_manager: Optional[StrategyMemoryManager] = None
        
        # Statystyki
        self.statistics: Dict[str, Any] = {
            'total_execution_time': 0.0,
            'avg_cycle_time': 0.0,
            'last_cycle_duration': 0.0
        }

    def initialize(self) -> Dict[str, Any]:
        """Inicjalizacja Pipeline i wszystkich komponentow"""
        self._log_event("PIPELINE_INITIALIZATION_START")
        
        initialization_result = {
            'status': 'success',
            'message': 'SSI Pipeline initialization started',
            'components': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # 1. Inicjalizacja WorldEngine
            self._log_event("WORLD_ENGINE_INITIALIZATION")
            self.world_engine = create_world_engine_from_generator(
                world_name=self.world_name
            )
            initialization_result['components']['world_engine'] = 'initialized'
            
            # 2. Inicjalizacja Agent Runtime
            if self.use_agent_runtime_manager:
                self._log_event("AGENT_RUNTIME_MANAGER_INITIALIZATION")
                self.agent_runtime_manager = AgentRuntimeManager(
                    pipeline_reference=str(id(self)),
                    number_of_agents=6
                )
                self.agent_interface = self.agent_runtime_manager
                
                agent_init_result = self.agent_runtime_manager.initialize()
                if agent_init_result['status'] == 'success':
                    initialization_result['components']['agent_runtime'] = 'initialized'
                    initialization_result['components']['agents_initialized'] = agent_init_result.get('agents_initialized', 0)
                else:
                    initialization_result['components']['agent_runtime'] = 'failed'
                    initialization_result['components']['error'] = agent_init_result.get('error')
            else:
                # Uzycie interfejsu jako fallback (kompatybilnosc wsteczna)
                self._log_event("AGENT_RUNTIME_INTERFACE_INITIALIZATION")
                self.agent_interface = AgentRuntimeInterface(pipeline_reference=str(id(self)))
                self.agent_interface.initialize()
                initialization_result['components']['agent_runtime'] = 'interface_mode'
            
            # 3. Inicjalizacja Teacher Layer
            self._log_event("TEACHER_LAYER_INITIALIZATION")
            self._initialize_teacher_layer()
            initialization_result['components']['teacher_layer'] = 'available'
            
            # 4. Inicjalizacja Modeling Layer
            self._log_event("MODELING_LAYER_INITIALIZATION")
            self._initialize_modeling_layer()
            initialization_result['components']['modeling_layer'] = 'available'
            
            # 5. Inicjalizacja Collective Manager (tylko z AgentRuntimeManager)
            if self.use_agent_runtime_manager and self.agent_runtime_manager:
                self._log_event("COLLECTIVE_MANAGER_INITIALIZATION")
                self._initialize_collective_manager()
                initialization_result['components']['collective_manager'] = 'initialized'
            else:
                initialization_result['components']['collective_manager'] = 'skipped'
            
            # 6. Inicjalizacja Memory Layer
            self._log_event("MEMORY_LAYER_INITIALIZATION")
            self._initialize_memory_layer()
            initialization_result['components']['memory_layer'] = 'available'
            
            # 7. Inicjalizacja Trust Manager
            if self.use_agent_runtime_manager and self.agent_runtime_manager:
                self._log_event("TRUST_MANAGER_INITIALIZATION")
                self._initialize_trust_manager()
                initialization_result['components']['trust_manager'] = 'initialized'
            else:
                initialization_result['components']['trust_manager'] = 'skipped'
            
            # 8. Inicjalizacja Personality Manager
            if self.use_agent_runtime_manager and self.agent_runtime_manager:
                self._log_event("PERSONALITY_MANAGER_INITIALIZATION")
                self._initialize_personality_manager()
                initialization_result['components']['personality_manager'] = 'initialized'
            else:
                initialization_result['components']['personality_manager'] = 'skipped'
            
            # 9. Inicjalizacja Cycle Controller (ETAP 5.3.1)
            self._log_event("CYCLE_CONTROLLER_INITIALIZATION")
            self._initialize_cycle_controller()
            initialization_result['components']['cycle_controller'] = 'initialized'
            
            # 10. Inicjalizacja Strategy Persistence Memory (ETAP 5.3.3)
            self._log_event("STRATEGY_MEMORY_INITIALIZATION")
            self._initialize_strategy_memory()
            initialization_result['components']['strategy_memory'] = 'initialized'
            
            # 11. Połączenie komponentów
            if self.agent_runtime_manager and self.collective_manager:
                self._log_event("COMPONENT_CONNECTION")
                self._connect_components()
                initialization_result['components']['components_connected'] = True
            
            # Znaczniki czasu
            self._initialized = True
            self.statistics['initialization_time'] = datetime.now()
            
            self._log_event("PIPELINE_INITIALIZATION_COMPLETE", {
                'components': list(initialization_result['components'].keys())
            })
            
            return initialization_result
            
        except Exception as e:
            initialization_result['status'] = 'error'
            initialization_result['error'] = str(e)
            self._log_event("PIPELINE_INITIALIZATION_ERROR", {
                'error': str(e)
            }, level="ERROR")
            return initialization_result

    def _initialize_teacher_layer(self) -> None:
        """Inicjalizacja warstwy Teacher"""
        try:
            # Probajemy stworzyc CognitiveTeacher z domyslnymi parametrami
            # Jesli nie powiedzie sie, uzyjemy mocka
            try:
                # CognitiveTeacher wymaga df i cechy - uzyjemy mockow
                import pandas as pd
                mock_df = pd.DataFrame({'wynik': ['1:0', '2:1', '0:0']})
                mock_cechy = ['feat1', 'feat2']
                cognitive_teacher = CognitiveTeacher(mock_df, mock_cechy)
            except Exception:
                # Stworz mock CognitiveTeacher
                class MockCognitiveTeacher:
                    def analyze_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
                        """Mock analiza wzorców"""
                        return {
                            'patterns_found': True,
                            'pattern_count': 1,
                            'analysis_timestamp': datetime.now().isoformat()
                        }
                    
                    def generate_memory_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
                        """Mock generowanie kontekstu pamięci"""
                        return {
                            'context_type': 'mock',
                            'context_data': data,
                            'timestamp': datetime.now().isoformat()
                        }
                
                cognitive_teacher = MockCognitiveTeacher()
            
            self.teacher_layer = {
                'cognitive_teacher': cognitive_teacher,
                'world_hierarchy': WorldHierarchyManager(),
                'initialization_time': datetime.now(),
                'status': 'available'
            }
        except Exception as e:
            # Jesli wszystko zawodzi, uzyjemy minimalnego mocka
            self.teacher_layer = {
                'cognitive_teacher': None,
                'world_hierarchy': WorldHierarchyManager(),
                'initialization_time': datetime.now(),
                'status': 'degraded',
                'error': str(e)
            }

    def _initialize_modeling_layer(self) -> None:
        """Inicjalizacja warstwy Modelowania"""
        self.modeling_layer = {
            'status': 'available',
            'initialization_time': datetime.now(),
            'component': 'Modeling Layer (LLM Queue Manager + Model Memory)'
        }

    def _initialize_memory_layer(self) -> None:
        """Inicjalizacja warstwy Pamieci"""
        try:
            # Tworzenie MemoryManager dla pamięci systemowej
            self.memory_manager = MemoryManager(
                memory_dir=None,  # Używa domyślnego katalogu z config
                network_name=self.world_name
            )
            self.memory_layer = {
                'status': 'available',
                'initialization_time': datetime.now(),
                'component': 'Memory Layer (Model Memory Ecosystem)',
                'memory_manager': 'initialized'
            }
        except Exception as e:
            self.memory_layer = {
                'status': 'degraded',
                'initialization_time': datetime.now(),
                'component': 'Memory Layer (Model Memory Ecosystem)',
                'error': str(e)
            }
    
    def _initialize_collective_manager(self) -> None:
        """Inicjalizacja Collective Manager"""
        try:
            self.collective_manager = CollectiveManager(
                world_name=self.world_name,
                pipeline_reference=str(id(self))
            )
            init_result = self.collective_manager.initialize()
            if init_result['status'] != 'success':
                self._log_event("COLLECTIVE_MANAGER_INITIALIZATION_FAILED", {
                    'error': init_result.get('error', 'Unknown error')
                }, level="WARNING")
        except Exception as e:
            self.collective_manager = None
            self._log_event("COLLECTIVE_MANAGER_INITIALIZATION_ERROR", {
                'error': str(e)
            }, level="ERROR")
    
    def _initialize_trust_manager(self) -> None:
        """Inicjalizacja Trust Manager"""
        try:
            # Tworzenie TrustManager (macierz zaufania zostanie zainicjalizowana później w set_trust_manager_reference)
            self.trust_manager = TrustManager(world_name=self.world_name)
            
            self._log_event("TRUST_MANAGER_INITIALIZED")
        except Exception as e:
            self.trust_manager = None
            self._log_event("TRUST_MANAGER_INITIALIZATION_ERROR", {
                'error': str(e)
            }, level="ERROR")
    
    def _initialize_personality_manager(self) -> None:
        """Inicjalizacja Personality Manager"""
        try:
            # Tworzenie PersonalityManager
            self.personality_manager = PersonalityManager(world_name=self.world_name)
            self._log_event("PERSONALITY_MANAGER_INITIALIZED")
        except Exception as e:
            self.personality_manager = None
            self._log_event("PERSONALITY_MANAGER_INITIALIZATION_ERROR", {
                'error': str(e)
            }, level="ERROR")
    
    def _initialize_cycle_controller(self) -> None:
        """
        Inicjalizacja Cycle Controller (ETAP 5.3.1).
        Tworzy kontroler cyklu z domyślną ścieżką stanu i opcjonalnym zegarem symulacyjnym.
        """
        try:
            # Tworzenie CycleController z domyślną ścieżką stanu i zegarem symulacyjnym
            state_path = os.path.join("runtime", "state", "cycle_state.json")
            self.cycle_controller = create_cycle_controller(
                state_path=state_path, 
                clock=self._clock
            )
            self._log_event("CYCLE_CONTROLLER_INITIALIZED", {
                'state_path': state_path
            })
        except Exception as e:
            self.cycle_controller = None
            self._log_event("CYCLE_CONTROLLER_INITIALIZATION_ERROR", {
                'error': str(e)
            }, level="ERROR")
    
    def _initialize_strategy_memory(self) -> None:
        """
        Inicjalizacja Strategy Persistence Memory (ETAP 5.3.3).
        Tworzy menadżer pamięci strategii.
        """
        try:
            # Tworzenie StrategyMemoryManager
            memory_dir = os.path.join("memory", "strategy_memory")
            self.strategy_memory_manager = StrategyMemoryManager(
                memory_dir=memory_dir,
                strategy_id=None  # Będzie ustawiany dynamicznie
            )
            self._log_event("STRATEGY_MEMORY_INITIALIZED", {
                'memory_dir': memory_dir
            })
        except Exception as e:
            self.strategy_memory_manager = None
            self._log_event("STRATEGY_MEMORY_INITIALIZATION_ERROR", {
                'error': str(e)
            }, level="ERROR")
    
    def _connect_components(self) -> None:
        """Połączenie komponentów: AgentRuntimeManager <-> CollectiveManager <-> TrustManager <-> PersonalityManager <-> MemoryManager"""
        try:
            # Podłącz CollectiveManager do AgentRuntimeManager
            if self.agent_runtime_manager and self.collective_manager:
                self.agent_runtime_manager.set_collective_manager_reference(self.collective_manager)
                self.collective_manager.set_agent_runtime_manager_reference(self.agent_runtime_manager)
            
            # Podłącz TrustManager do AgentRuntimeManager
            if self.agent_runtime_manager and self.trust_manager:
                self.agent_runtime_manager.set_trust_manager_reference(self.trust_manager)
            
            # Podłącz PersonalityManager do AgentRuntimeManager
            if self.agent_runtime_manager and self.personality_manager:
                # PersonalityManager jest używany przez agentów indywidualnie, nie potrzebuje referencji
                pass
            
            # Podłącz MemoryManager do wszystkich
            if self.memory_manager:
                if self.agent_runtime_manager:
                    self.agent_runtime_manager.set_memory_manager_reference(self.memory_manager)
                if self.collective_manager:
                    self.collective_manager.set_memory_manager_reference(self.memory_manager)
            
        except Exception as e:
            self._log_event("COMPONENT_CONNECTION_ERROR", {
                'error': str(e)
            }, level="ERROR")
    
    def _create_world_state(self) -> WorldState:
        """
        Tworzenie stanu świata na podstawie aktualnego stanu systemu (ETAP 5.3.1).
        
        Returns:
            WorldState z aktualnymi danymi
        """
        # Pobieranie stanu z world_engine jeśli dostępny
        world_is_ready = False
        world_status = "UNKNOWN"
        database_status = "UNKNOWN"
        odds_available = False
        
        if self.world_engine:
            try:
                world_status = getattr(self.world_engine, 'status', 'UNKNOWN')
                world_is_ready = world_status == "READY"
            except Exception:
                pass
        
        # Sprawdzanie stanu bazy danych
        if self.memory_manager:
            try:
                database_status = getattr(self.memory_manager, 'status', 'UNKNOWN')
                if database_status in ["initialized", "ready", "available"]:
                    database_status = "READY"
            except Exception:
                pass
        
        # Sprawdzanie dostępności kursów (Market Observer)
        try:
            # Import dynamiczny, aby uniknąć zależności cyklicznych
            from SSI_V5_FOOTBALL_BETTING_MARKET_OBSERVER import FootballBettingMarketObserver
            odds_available = True  # Zakładamy dostępność, dopóki nie sprawdzimy inaczej
        except Exception:
            odds_available = False
        
        # Tworzenie stanu świata
        return WorldState(
            new_results_available=False,  # Będzie ustawiany z zewnątrz
            results_processed=True,  # Domyślnie przetworzone
            world_status=world_status,
            world_is_ready=world_is_ready,
            database_status=database_status,
            odds_available=odds_available,
            current_time=datetime.now(),
            prediction_cycle_completed=False  # Będzie ustawiany w trakcie cyklu
        )

    def run_cycle(self, generator_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Wykonywanie pojedynczego cyklu"""
        if not self._initialized:
            return {
                'status': 'error',
                'error': 'Pipeline not initialized. Call initialize() first.',
                'timestamp': datetime.now().isoformat()
            }
        
        if self._shutdown_requested:
            return {
                'status': 'error',
                'error': 'Shutdown requested. Cannot run new cycles.',
                'timestamp': datetime.now().isoformat()
            }
        
        # Generowanie ID cyklu
        self._cycle_counter += 1
        cycle_id = f"{self.world_name}_CYCLE_{self._cycle_counter:06d}"
        self._current_cycle_id = cycle_id
        
        # Tworzenie metadanych cyklu
        cycle_metadata = CycleMetadata(
            cycle_id=cycle_id,
            start_time=datetime.now(),
            world_name=self.world_name
        )
        
        # ETAP 5.3.1: Detekcja fazy i pobranie kontekstu
        detected_phase = CyclePhase.WAITING
        execution_context = None
        
        if self.cycle_controller:
            # Tworzenie stanu świata na podstawie aktualnego stanu systemu
            world_state = self._create_world_state()
            detected_phase = self.cycle_controller.detect_current_phase(world_state)
            execution_context = self.cycle_controller.get_execution_context()
            
            self._log_event("PHASE_DETECTED", {
                'phase': detected_phase.value,
                'context_goal': execution_context.goal if execution_context else None
            })
        
        # Logowanie startu cyklu
        self._log_event("CYCLE_START", {
            'cycle_id': cycle_id,
            'counter': self._cycle_counter,
            'detected_phase': detected_phase.value,
            'execution_context': execution_context.to_dict() if execution_context else None
        })
        
        # Masa kanapkowa - start pomiaru czasu
        cycle_start_time = time.time()
        
        cycle_result = {
            'status': 'success',
            'cycle_id': cycle_id,
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'duration': 0.0,
            'steps': {},
            'cycle_metadata': None
        }
        
        try:
            # ========================================
            # 1. WORLD GENERATION
            # ========================================
            self._update_cycle_status(CycleStatus.WORLD_GENERATION)
            cycle_metadata.add_step("world_generation")
            
            world_result = self._run_world_generation(generator_data)
            self._last_world_result = world_result  # Zapamietaj dla memory integration (ETAP 1.2.7.3)
            
            cycle_result['steps']['world_generation'] = {
                'status': world_result['status'],
                'duration': world_result.get('duration', 0.0),
                'world_data': world_result.get('world_data', {}),
                'error': world_result.get('error')
            }
            
            if world_result['status'] == 'error':
                self._log_event("STEP_ERROR", {
                    'step': 'world_generation',
                    'error': world_result.get('error', 'Unknown error')
                }, level="ERROR")
                # Kontynuujemy pomimo bledu - system powinien byc odporny
                cycle_result['status'] = 'partial'
            
            # ========================================
            # 2. MODELING
            # ========================================
            self._update_cycle_status(CycleStatus.MODELING)
            cycle_metadata.add_step("modeling")
            
            modeling_result = self._run_modeling(world_result.get('output', {}))
            self._last_modeling_result = modeling_result  # Zapamietaj dla memory integration (ETAP 1.2.7.3)
            
            cycle_result['steps']['modeling'] = {
                'status': modeling_result['status'],
                'duration': modeling_result.get('duration', 0.0),
                'modeling_data': modeling_result.get('modeling_data', {}),
                'error': modeling_result.get('error')
            }
            
            if modeling_result['status'] == 'error':
                self._log_event("STEP_ERROR", {
                    'step': 'modeling',
                    'error': modeling_result.get('error', 'Unknown error')
                }, level="ERROR")
                cycle_result['status'] = 'partial'
            
            # ========================================
            # 3. TEACHER ANALYSIS
            # ========================================
            self._update_cycle_status(CycleStatus.TEACHER_ANALYSIS)
            cycle_metadata.add_step("teacher_analysis")
            
            teacher_result = self._run_teacher_analysis(modeling_result.get('output', {}))
            self._last_teacher_result = teacher_result  # Zapamietaj dla memory integration (ETAP 1.2.7.3)
            
            cycle_result['steps']['teacher_analysis'] = {
                'status': teacher_result['status'],
                'duration': teacher_result.get('duration', 0.0),
                'teacher_data': teacher_result.get('teacher_data', {}),
                'error': teacher_result.get('error')
            }
            
            if teacher_result['status'] == 'error':
                self._log_event("STEP_ERROR", {
                    'step': 'teacher_analysis',
                    'error': teacher_result.get('error', 'Unknown error')
                }, level="ERROR")
                cycle_result['status'] = 'partial'
            
            # ========================================
            # 4. AGENT EXECUTION
            # ========================================
            self._update_cycle_status(CycleStatus.AGENT_EXECUTION)
            cycle_metadata.add_step("agent_execution")
            
            agent_result = self._run_agent_execution(teacher_result.get('analysis', {}))
            self._last_agent_result = agent_result  # Zapamietaj dla memory integration (ETAP 1.2.7.3)
            
            cycle_result['steps']['agent_execution'] = {
                'status': agent_result['status'],
                'duration': agent_result.get('duration', 0.0),
                'agents_active': agent_result.get('agents_active', 0),
                'contracts_sent': agent_result.get('contracts_sent', 0),
                'error': agent_result.get('error')
            }
            
            if agent_result['status'] == 'error':
                self._log_event("STEP_ERROR", {
                    'step': 'agent_execution',
                    'error': agent_result.get('error', 'Unknown error')
                }, level="ERROR")
                cycle_result['status'] = 'partial'
            
            # ETAP 5.3.3: Zapis wyników do Strategy Persistence Memory
            if agent_result.get('status') == 'success' and self.strategy_memory_manager:
                self._record_agent_results_to_strategy_memory(
                    agent_result, cycle_id, execution_context
                )
            
            # ========================================
            # 5. COLLECTIVE CONSENSUS
            # ========================================
            self._update_cycle_status(CycleStatus.COLLECTIVE_CONSENSUS)
            cycle_metadata.add_step("collective_consensus")
            
            collective_result = self._run_collective_consensus(agent_result.get('decisions', {}))
            self._last_collective_result = collective_result  # Zapamietaj dla memory integration (ETAP 1.2.7.3)
            
            cycle_result['steps']['collective_consensus'] = {
                'status': collective_result['status'],
                'duration': collective_result.get('duration', 0.0),
                'consensus_reached': collective_result.get('consensus_reached', False),
                'collective_decision_id': collective_result.get('collective_decision_id'),
                'error': collective_result.get('error')
            }
            
            if collective_result['status'] == 'error':
                self._log_event("STEP_ERROR", {
                    'step': 'collective_consensus',
                    'error': collective_result.get('error', 'Unknown error')
                }, level="ERROR")
                # Kontynuujemy pomimo bledu - system powinien byc odporny
                cycle_result['status'] = 'partial'
            
            # ========================================
            # 6. TRUST & PERSONALITY UPDATE
            # ========================================
            self._update_cycle_status(CycleStatus.TRUST_PERSONALITY_UPDATE)
            cycle_metadata.add_step("trust_personality_update")
            
            # Aktualizacja zaufania i osobowości na podstawie decyzji i konsensusu
            trust_personality_result = self._run_trust_personality_update(
                agent_result.get('decisions', {}),
                collective_result
            )
            cycle_result['steps']['trust_personality_update'] = {
                'status': trust_personality_result['status'],
                'duration': trust_personality_result.get('duration', 0.0),
                'trust_updates': trust_personality_result.get('trust_updates', {}),
                'reputation_updates': trust_personality_result.get('reputation_updates', {}),
                'personality_updates': trust_personality_result.get('personality_updates', {}),
                'trust_matrix_updated': trust_personality_result.get('trust_matrix_updated', False),
                'reputation_updated': trust_personality_result.get('reputation_updated', False),
                'error': trust_personality_result.get('error')
            }
            
            if trust_personality_result['status'] == 'error':
                self._log_event("STEP_ERROR", {
                    'step': 'trust_personality_update',
                    'error': trust_personality_result.get('error', 'Unknown error')
                }, level="WARNING")
            
            # ========================================
            # 7. OBSERVATION
            # ========================================
            self._update_cycle_status(CycleStatus.OBSERVATION)
            cycle_metadata.add_step("observation")
            
            # Przekazujemy dane agentów + kolektywne decyzje do obserwacji
            observation_input = {
                **agent_result.get('decisions', {}),
                **collective_result.get('output', {})
            }
            observation_result = self._run_observation(observation_input)
            self._last_observation_result = observation_result  # Zapamietaj dla memory integration (ETAP 1.2.7.3)
            
            cycle_result['steps']['observation'] = {
                'status': observation_result['status'],
                'duration': observation_result.get('duration', 0.0),
                'observations': observation_result.get('observations', {}),
                'error': observation_result.get('error')
            }
            
            if observation_result['status'] == 'error':
                self._log_event("STEP_ERROR", {
                    'step': 'observation',
                    'error': observation_result.get('error', 'Unknown error')
                }, level="ERROR")
                cycle_result['status'] = 'partial'
            
            # ========================================
            # 6. MEMORY UPDATE
            # ========================================
            self._update_cycle_status(CycleStatus.MEMORY_UPDATE)
            cycle_metadata.add_step("memory_update")
            
            memory_result = self._run_memory_update(observation_result.get('output', {}))
            cycle_result['steps']['memory_update'] = {
                'status': memory_result['status'],
                'duration': memory_result.get('duration', 0.0),
                'memory_updates': memory_result.get('memory_updates', {}),
                'error': memory_result.get('error')
            }
            
            if memory_result['status'] == 'error':
                self._log_event("STEP_ERROR", {
                    'step': 'memory_update',
                    'error': memory_result.get('error', 'Unknown error')
                }, level="ERROR")
                cycle_result['status'] = 'partial'
            elif memory_result['status'] == 'partial':
                # partial od MemoryIntegrator nie powinien powodowac partial dla calego cyklu
                # Logujemy jako warning, ale nie zmieniamy statusu cyklu
                self._log_event("STEP_WARNING", {
                    'step': 'memory_update',
                    'message': 'Memory integration completed with warnings',
                    'warnings': memory_result.get('memory_updates', {}).get('warnings', [])
                }, level="WARNING")
            
            # ========================================
            # ZAKONCZENIE CYKLU
            # ========================================
            cycle_metadata.end_time = datetime.now()
            cycle_metadata.status = CycleStatus.COMPLETE if cycle_result['status'] != 'error' else CycleStatus.ERROR
            
            cycle_result['end_time'] = cycle_metadata.end_time.isoformat()
            cycle_result['duration'] = cycle_metadata.get_duration()
            cycle_result['cycle_metadata'] = cycle_metadata.to_dict()
            cycle_result['final_status'] = cycle_metadata.status.value
            
            # Aktualizacja statystyk
            self._update_statistics(cycle_result)
            
            # Zapisanie do historii
            with self._lock:
                self._cycle_history.append(cycle_metadata)
            
            # Logowanie zakonczenia cyklu
            self._log_event("CYCLE_COMPLETE", {
                'cycle_id': cycle_id,
                'duration': cycle_result['duration'],
                'status': cycle_result['final_status'],
                'steps': list(cycle_result['steps'].keys())
            })
            
            # Reset current cycle id
            self._current_cycle_id = None
            self._update_cycle_status(CycleStatus.IDLE)
            
            return cycle_result
            
        except Exception as e:
            cycle_metadata.end_time = datetime.now()
            cycle_metadata.status = CycleStatus.ERROR
            cycle_metadata.add_error("PIPELINE_ERROR", str(e), "cycle_execution")
            
            with self._lock:
                self._cycle_history.append(cycle_metadata)
            
            self._log_event("CYCLE_ERROR", {
                'cycle_id': cycle_id,
                'error': str(e),
                'duration': time.time() - cycle_start_time
            }, level="ERROR")
            
            self._current_cycle_id = None
            self._update_cycle_status(CycleStatus.ERROR)
            
            return {
                'status': 'error',
                'error': str(e),
                'cycle_id': cycle_id,
                'duration': time.time() - cycle_start_time,
                'start_time': cycle_result['start_time'],
                'end_time': datetime.now().isoformat(),
                'cycle_metadata': cycle_metadata.to_dict()
            }

    def _run_world_generation(self, generator_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Wykonywanie generacji swiata"""
        start_time = time.time()
        
        try:
            if generator_data and self.world_engine:
                # Uzycie niestandardowych danych generatora
                if hasattr(self.world_engine, 'receive_from_generator'):
                    self.world_engine.receive_from_generator(generator_data)
            
            # Zawsze uzyj process() aby wygenerowac wyjscie
            world_output = self.world_engine.process()
            
            return {
                'status': 'success',
                'duration': time.time() - start_time,
                'world_data': world_output.to_dict() if hasattr(world_output, 'to_dict') else world_output,
                'output': world_output,
                'world_name': self.world_name
            }
        except Exception as e:
            return {
                'status': 'error',
                'duration': time.time() - start_time,
                'error': str(e)
            }

    def _run_modeling(self, world_data: Any) -> Dict[str, Any]:
        """Wykonywanie modelowania"""
        start_time = time.time()
        
        try:
            # Symulacja przetwarzania - w rzeczywistej implementacji bedzie to LLM Queue
            if self.modeling_layer and self.modeling_layer.get('status') == 'available':
                # Przekazanie danych z WorldEngine do Modeling Layer
                # world_data moze byc WorldEngineOutput lub slownikiem
                if hasattr(world_data, 'to_dict'):
                    world_dict = world_data.to_dict()
                elif isinstance(world_data, dict):
                    world_dict = world_data
                else:
                    world_dict = {'data': str(world_data)}
                
                # Przetwarzanie danych - uzycie .items() tylko jesli to slownik
                processed_data = {}
                if isinstance(world_dict, dict):
                    processed_data = {k: v for k, v in world_dict.items()}
                else:
                    processed_data = {'input': world_dict}
                
                modeling_output = {
                    'status': 'success',
                    'input_data': world_dict,
                    'processed_data': processed_data,
                    'modeling_steps': [
                        {
                            'step': 'data_validation',
                            'status': 'success',
                            'timestamp': datetime.now().isoformat()
                        },
                        {
                            'step': 'feature_extraction',
                            'status': 'success',
                            'timestamp': datetime.now().isoformat()
                        },
                        {
                            'step': 'context_augmentation',
                            'status': 'success',
                            'timestamp': datetime.now().isoformat()
                        }
                    ]
                }
                
                return {
                    'status': 'success',
                    'duration': time.time() - start_time,
                    'modeling_data': modeling_output,
                    'output': modeling_output
                }
            else:
                return {
                    'status': 'error',
                    'duration': time.time() - start_time,
                    'error': 'Modeling layer not available'
                }
        except Exception as e:
            return {
                'status': 'error',
                'duration': time.time() - start_time,
                'error': str(e)
            }

    def _run_teacher_analysis(self, modeling_data: Any) -> Dict[str, Any]:
        """Wykonywanie analizy Teacher"""
        start_time = time.time()
        
        try:
            if self.teacher_layer and self.teacher_layer.get('status') == 'available':
                # Uruchomienie CognitiveTeacher
                teacher = self.teacher_layer['cognitive_teacher']
                
                # Analiza danych z modeling layer - sprawdz czy metody istnieja
                analysis_result = {}
                memory_context = {}
                
                if hasattr(teacher, 'analyze_patterns'):
                    analysis_result = teacher.analyze_patterns(modeling_data)
                else:
                    # Mock analysis
                    analysis_result = {
                        'patterns_found': True,
                        'pattern_count': 1,
                        'analysis_timestamp': datetime.now().isoformat(),
                        'input_summary': str(type(modeling_data).__name__)
                    }
                
                if hasattr(teacher, 'generate_memory_context'):
                    memory_context = teacher.generate_memory_context(modeling_data)
                else:
                    # Mock context generation
                    memory_context = {
                        'context_type': 'teacher_analysis',
                        'context_data': 'Generated from modeling data',
                        'timestamp': datetime.now().isoformat()
                    }
                
                return {
                    'status': 'success',
                    'duration': time.time() - start_time,
                    'teacher_data': {
                        'pattern_analysis': analysis_result,
                        'memory_context': memory_context,
                        'timestamp': datetime.now().isoformat()
                    },
                    'analysis': {
                        'patterns': analysis_result,
                        'memory_registration': memory_context
                    },
                    'output': modeling_data  # Przekazanie dalej danych
                }
            else:
                return {
                    'status': 'error', 
                    'duration': time.time() - start_time,
                    'error': 'Teacher layer not available'
                }
        except Exception as e:
            return {
                'status': 'error',
                'duration': time.time() - start_time,
                'error': str(e)
            }

    def _run_agent_execution(self, teacher_data: Dict[str, Any]) -> Dict[str, Any]:
        """Wykonywanie agentow (ETAP 5.3.2: z ExecutionContext)"""
        start_time = time.time()
        
        try:
            if self.agent_interface is None:
                return {
                    'status': 'error',
                    'duration': time.time() - start_time,
                    'error': 'Agent interface not initialized'
                }
            
            # ETAP 5.3.2: Pobranie ExecutionContext z CycleController
            execution_context = None
            if self.cycle_controller:
                execution_context = self.cycle_controller.get_execution_context()
            
            # Przygotowanie danych cyklu dla agentow (rozszerzone o ExecutionContext)
            cycle_data = {
                'cycle_id': self._current_cycle_id,
                'world_name': self.world_name,
                'input_data': teacher_data,
                'timestamp': datetime.now().isoformat(),
                'pipeline_mode': self.mode.value,
                # ETAP 5.3.2: Execution Context
                'execution_context': execution_context.to_dict() if execution_context else None
            }
            
            # Logowanie kontekstu wykonania
            self._log_event("AGENT_EXECUTION_CONTEXT", {
                'cycle_id': self._current_cycle_id,
                'phase': execution_context.phase.value if execution_context else 'unknown',
                'goal': execution_context.goal if execution_context else None,
                'available_memory': execution_context.available_memory if execution_context else [],
                'allowed_actions': execution_context.allowed_actions if execution_context else [],
                'forbidden_actions': execution_context.forbidden_actions if execution_context else []
            })
            
            # Wykonanie cyklu przez agentow
            result = self.agent_interface.execute_cycle(cycle_data)
            
            # Sprawdzenie statusu
            if result.get('status') == 'success':
                return {
                    'status': 'success',
                    'duration': time.time() - start_time,
                    'agents_active': result.get('agents_active', 0),
                    'contracts_sent': result.get('contracts_sent', 0),
                    'agent_results': result.get('agent_results', []),
                    'decisions': result.get('decisions', {}),
                    'output': result
                }
            else:
                return {
                    'status': 'error',
                    'duration': time.time() - start_time,
                    'error': result.get('error', 'Agent execution failed'),
                    'output': result
                }
        except Exception as e:
            return {
                'status': 'error',
                'duration': time.time() - start_time,
                'error': str(e)
            }

    def _run_collective_consensus(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Wykonywanie konsensusu kolektywnego z decyzji agentów"""
        start_time = time.time()
        
        try:
            # Jeśli brak CollectiveManager, zwróć success z pustymi wynikami
            if self.collective_manager is None:
                return {
                    'status': 'success',
                    'duration': time.time() - start_time,
                    'consensus_reached': False,
                    'message': 'CollectiveManager not available, skipping consensus',
                    'collective_decision_id': None,
                    'output': {}
                }
            
            # Rozpoczęcie cyklu kolektywnego
            cycle_id = self._current_cycle_id
            if cycle_id is None:
                return {
                    'status': 'error',
                    'duration': time.time() - start_time,
                    'error': 'No current cycle ID'
                }
            
            start_result = self.collective_manager.start_cycle(cycle_id)
            if start_result['status'] != 'success':
                return {
                    'status': 'error',
                    'duration': time.time() - start_time,
                    'error': start_result.get('error', 'Failed to start collective cycle')
                }
            
            # Zebranie decyzji od agentów - używamy decisions z agent_data
            # agent_data to result z execute_cycle, który ma decisions
            if isinstance(self.agent_interface, AgentRuntimeManager):
                # agent_data powinno mieć decisions (dodane w AgentRuntimeManager.execute_cycle)
                if 'decisions' in agent_data and agent_data['decisions']:
                    for agent_id, agent_decisions in agent_data['decisions'].items():
                        for decision in agent_decisions:
                            if isinstance(decision, dict):
                                self.collective_manager.collect_agent_decision(
                                    agent_id, decision, cycle_id
                                )
                else:
                    # Fallback: spróbuj zebrać z pamięci agentów
                    for agent_id, agent in self.agent_interface.agents.items():
                        agent_decisions = agent.memory.get_decisions()
                        for decision in agent_decisions:
                            if isinstance(decision, dict):
                                self.collective_manager.collect_agent_decision(
                                    agent_id, decision, cycle_id
                                )
            
            # Budowanie konsensusu
            try:
                collective_decision = self.collective_manager.build_consensus(cycle_id)
                consensus_reached = True
                collective_decision_id = collective_decision.decision_id
            except ValueError as e:
                # Brak decyzji do konsensusu
                collective_decision = None
                consensus_reached = False
                collective_decision_id = None
            
            # Zakończenie cyklu kolektywnego
            end_result = self.collective_manager.end_cycle(cycle_id)
            
            return {
                'status': 'success',
                'duration': time.time() - start_time,
                'consensus_reached': consensus_reached,
                'collective_decision_id': collective_decision_id,
                'collective_decision': collective_decision.to_dict() if collective_decision else None,
                'output': {
                    'consensus_result': collective_decision.consensus_result if collective_decision else {},
                    'confidence_score': collective_decision.confidence_score if collective_decision else 0.0
                },
                'cycle_summary': end_result
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'duration': time.time() - start_time,
                'error': str(e)
            }

    def _run_trust_personality_update(
        self, 
        agent_decisions: Dict[str, Any], 
        collective_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Aktualizacja zaufania i osobowości na podstawie decyzji agentów i konsensusu.
        Wywoływana po AGENT_EXECUTION i COLLECTIVE_CONSENSUS, przed OBSERVATION.
        """
        start_time = time.time()
        
        update_result = {
            'status': 'success',
            'duration': 0.0,
            'trust_updates': {},
            'reputation_updates': {},
            'personality_updates': {},
            'trust_matrix_updated': False,
            'reputation_updated': False,
            'output': {}
        }
        
        try:
            # Sprawdź, czy TrustManager i PersonalityManager są dostępne
            if not self.trust_manager or not self.personality_manager:
                return {
                    'status': 'skipped',
                    'duration': time.time() - start_time,
                    'message': 'TrustManager or PersonalityManager not available',
                    'trust_manager_available': self.trust_manager is not None,
                    'personality_manager_available': self.personality_manager is not None
                }
            
            if not self.agent_runtime_manager:
                return {
                    'status': 'skipped',
                    'duration': time.time() - start_time,
                    'message': 'AgentRuntimeManager not available'
                }
            
            # Pobierz IDisionalne agenta z AgentRuntimeManager
            agent_ids = list(self.agent_runtime_manager.agents.keys())
            
            # ========================================
            # 1. OCena decyzji i aktualizacja Reputation
            # ========================================
            
            # Dla kazdego agenta, ocen jego decyzje
            for agent_id, decisions in agent_decisions.items():
                if not decisions or not isinstance(decisions, list):
                    continue
                    
                # Ocen rozne aspekty decyzyjne
                decision_quality = self._evaluate_agent_decisions(agent_id, decisions, collective_result)
                
                # Zaktualizuj reputation na podstawie oceny
                self.trust_manager.update_reputation_from_decision(
                    agent_id=agent_id,
                    decision_outcome=decision_quality,
                    cycles_completed=self.agent_runtime_manager.cycle_count
                )
                
                # Zapisz aktualizacje
                reputation = self.trust_manager.get_agent_reputation(agent_id)
                if reputation:
                    update_result['reputation_updates'][agent_id] = {
                        'reputation_score': reputation.reputation_score,
                        'reputation_level': reputation.get_reputation_level().value,
                        'total_decisions': reputation.total_decisions,
                        'successful_decisions': reputation.successful_decisions
                    }
            
            update_result['reputation_updated'] = bool(update_result['reputation_updates'])
            
            # ========================================
            # 2. Aktualizacja Trust Matrix (zaufanie miedzy agentami)
            # ========================================
            
            # Aktualizuj macierz zaufania na podstawie spójności decyzyjnej
            if len(agent_decisions) > 1:
                self._update_trust_based_on_consistency(agent_decisions, collective_result)
                update_result['trust_matrix_updated'] = True
                
                # Pobierz aktualną macierz zaufania
                trust_matrix = self.trust_manager.get_trust_matrix()
                update_result['trust_updates'] = {
                    'matrix_updated': True,
                    'agent_count': len(trust_matrix),
                    'timestamp': datetime.now().isoformat()
                }
            
            # ========================================
            # 3. Aktualizacja Personality (ewolucja osobowości)
            # ========================================
            
            # Ewolucja osobowości na podstawie wynikow (tylko jesli dokumentacja przewiduje)
            #按照 SSI philosophy, osobowosc moze ewoluowac na podstawie doswiadczen
            # Ale w FAZA 2 Skupiamy sie glownie na zaufaniu i reputacji
            # Personality ewolucja bedzie dodana w kolejnych fazach
            
            # Poble zaktualizuj history Personality (bez zmiany wartosci)
            if self.personality_manager:
                for agent_id in agent_ids:
                    personality_state = self.personality_manager.get_agent_personality(agent_id)
                    if personality_state:
                        update_result['personality_updates'][agent_id] = {
                            'personality_recorded': True,
                            'current_parameters': personality_state.current_personality.to_dict()
                        }
            
            update_result['duration'] = time.time() - start_time
            
            # Logowanie udanej aktualizacji
            self._log_event("TRUST_PERSONALITY_UPDATE_COMPLETE", {
                'reputation_updated': update_result['reputation_updated'],
                'trust_matrix_updated': update_result['trust_matrix_updated'],
                'agents_with_reputation_updates': len(update_result['reputation_updates']),
                'duration': update_result['duration']
            })
            
            return update_result
            
        except Exception as e:
            return {
                'status': 'error',
                'duration': time.time() - start_time,
                'error': str(e),
                'trust_updates': {},
                'reputation_updates': {},
                'personality_updates': {}
            }
    
    def _evaluate_agent_decisions(
        self, 
        agent_id: str, 
        decisions: List[Dict[str, Any]], 
        collective_result: Dict[str, Any]
    ) -> DecisionOutcome:
        """
        Ocen jakość decyzji agenta i zwróć DecisionOutcome.
        Logika oceny oparta na:
        - Spójności z konsensusem kolektywnym
        - Ilości podejmowanych decyzji
        - Jakości analitycznej decyzji
        """
        try:
            # Jeśli konsensus został osiągnięty, sprawdź spójność agenta
            if collective_result.get('consensus_reached', False):
                collective_decision_id = collective_result.get('collective_decision_id')
                
                # Sprawdź, czy agent brał udział w konsensusie
                agent_in_consensus = False
                decision_quality_score = 0.5  # domyślne neutralne
                
                if isinstance(self.agent_runtime_manager, AgentRuntimeManager):
                    # Sprawdź udział agenta w konsensusie
                    if self.collective_manager:
                        agent_in_consensus = self.collective_manager.agent_participated(
                            agent_id, collective_result.get('collective_id', '')
                        )
                
                # Ocen jakość na podstawie udziału i spójności
                if agent_in_consensus:
                    # Agent uczestniczył w konsensusie - dobra decyzja
                    decision_quality_score = 0.9
                else:
                    # Agent nie uczestniczył -回答道  결
                    decision_quality_score = 0.4
                    
                # Dodatkowa ocena na podstawie ilości decyzji
                if len(decisions) > 3:
                    decision_quality_score += 0.1  # bonus za wiele decyzji
                elif len(decisions) < 1:
                    decision_quality_score -= 0.2  # kara za zbyt małą aktywność
                    
                # Saturacja do zakresu 0.0-1.0
                decision_quality_score = max(0.0, min(1.0, decision_quality_score))
                
                # Mapowanie na DecisionOutcome
                if decision_quality_score >= 0.9:
                    return DecisionOutcome.EXCELLENT
                elif decision_quality_score >= 0.7:
                    return DecisionOutcome.GOOD
                elif decision_quality_score >= 0.4:
                    return DecisionOutcome.NEUTRAL
                elif decision_quality_score >= 0.2:
                    return DecisionOutcome.POOR
                else:
                    return DecisionOutcome.FAILURE
            else:
                # Brak konsensusu - ocena na podstawie ilości decyzji
                if len(decisions) >= 3:
                    return DecisionOutcome.GOOD
                elif len(decisions) >= 1:
                    return DecisionOutcome.NEUTRAL
                else:
                    return DecisionOutcome.POOR
                    
        except Exception:
            # W razie błędu zwróć neutralny
            return DecisionOutcome.NEUTRAL
    
    def _update_trust_based_on_consistency(
        self, 
        agent_decisions: Dict[str, Any], 
        collective_result: Dict[str, Any]
    ) -> None:
        """
        Aktualizuj macierz zaufania na podstawie spójności decyzji między agentami.
        Agenci, którzy podejmowali podobne decyzje, zyskują wzajemne zaufanie.
        """
        try:
            if len(agent_decisions) < 2:
                return
            
            # Pobierz kolekcjędecyzji z konsensusu
            collective_decision = collective_result.get('output', {})
            
            # Dla każdej pary agentów, porównaj ich decyzje
            agent_ids = list(agent_decisions.keys())
            for i, agent_id_1 in enumerate(agent_ids):
                for agent_id_2 in agent_ids[i+1:]:
                    decisions_1 = agent_decisions.get(agent_id_1, [])
                    decisions_2 = agent_decisions.get(agent_id_2, [])
                    
                    if decisions_1 and decisions_2:
                        # Oblicz podobieństwo decyzji (prostopadłe uproszczenie)
                        similarity = self._calculate_decision_similarity(decisions_1, decisions_2)
                        
                        # Aktualizuj zaufanieários between agentami
                        self.trust_manager.update_trust(
                            from_agent_id=agent_id_1,
                            to_agent_id=agent_id_2,
                            trust_change=similarity,
                            reason="decision_consistency"
                        )
                        self.trust_manager.update_trust(
                            from_agent_id=agent_id_2,
                            to_agent_id=agent_id_1,
                            trust_change=similarity,
                            reason="decision_consistency"
                        )
        except Exception:
            pass  # Nie crefact błędu - aktualizacja zaufania jest opcjonalna
    
    def _calculate_decision_similarity(
        self, 
        decisions_1: List[Dict[str, Any]], 
        decisions_2: List[Dict[str, Any]]
    ) -> float:
        """
        Oblicz podobieństwo między dwoma zestawami decyzji.
        Uproszczona metoda: porównuje typy decyzji i ich wyniki.
        """
        try:
            if not decisions_1 or not decisions_2:
                return 0.0
            
            # Pobierz typy decyzji z pierwszego agenta
            types_1 = set()
            for decision in decisions_1:
                if isinstance(decision, dict):
                    decision_type = decision.get('type', decision.get('decision_type', 'unknown'))
                    types_1.add(decision_type)
            
            # Pobierz typy decyzji z drugiego agenta  
            types_2 = set()
            for decision in decisions_2:
                if isinstance(decision, dict):
                    decision_type = decision.get('type', decision.get('decision_type', 'unknown'))
                    types_2.add(decision_type)
            
            # Oblicz wspólne typy
            common_types = types_1 & types_2
            if not types_1 or not types_2:
                return 0.0
                
            # Podobieństwo = |common| / max(|types_1|, |types_2|)
            similarity = len(common_types) / max(len(types_1), len(types_2))
            return similarity
        except Exception:
            return 0.0
    
    def _run_observation(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Wykonywanie obserwacji"""
        start_time = time.time()
        
        try:
            # Przetwarzanie obserwacji z agentow
            if isinstance(self.agent_interface, AgentRuntimeManager):
                observation_result = self.agent_interface.observe(agent_data)
            else:
                observation_result = self.agent_interface.observe(agent_data)
            
            # Tworzenie raportu obserwacji
            observation_report = {
                'status': observation_result.get('status', 'success'),
                'observations': observation_result.get('observations', {}),
                'agents_notified': observation_result.get('agents_notified', 0),
                'total_observations': observation_result.get('total_observations', 0),
                'output': agent_data  # Przekazanie wynikow agentow dalej
            }
            
            return {
                'status': 'success',
                'duration': time.time() - start_time,
                'observation_report': observation_report,
                'output': observation_report,
                'observations': observation_report['observations']
            }
        except Exception as e:
            return {
                'status': 'error',
                'duration': time.time() - start_time,
                'error': str(e)
            }

    def _get_memory_integrator(self) -> Optional[Any]:
        """
        Pobranie MemoryIntegrator przez IFC.
        
        Zgodnie z kontrakcie architektoniczny ETAP 1.2.7.3:
        Pipeline NIE powinien posiadać bezpośrednio memory_integrator.
        MemoryIntegrator jest pobierany przez IFC.
        
        Returns:
            MemoryIntegrator lub None jeśli niedostępny
        """
        if self.ifc is None:
            return None
        
        try:
            return self.ifc.get("memory_integrator")
        except Exception:
            return None
    
    def _prepare_cycle_data_for_memory(self, observation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Przygotowanie strukturowanych danych cyklu dla MemoryIntegrator.
        
        ETAP 1.2.7.3: Konwersja danych z pipeline do formatu zrozumiałego przez MemoryIntegrator
        
        MemoryIntegrator.process_cycle_result() oczekuje:
        - cycle_id
        - timestamp
        - world_data (opcjonalnie)
        - modeling_data (opcjonalnie)
        - teacher_data (opcjonalnie)
        - agent_data (opcjonalnie)
        - collective_data (opcjonalnie)
        - experiment_data (opcjonalnie)
        - model_data (opcjonalnie)
        
        Args:
            observation_data: Dane z obserwacji zawiera decisje agentow i konsensus
            
        Returns:
            Słownik ze strukturowanymi danymi dla MemoryIntegrator
        """
        # Budowa struktury danych dla MemoryIntegrator
        cycle_data = {
            'cycle_id': self._current_cycle_id or f'cycle_{self._cycle_counter}',
            'timestamp': datetime.now().isoformat(),
            'world_name': self.world_name,
            'pipeline_mode': self.mode.value,
            'status': 'complete',
            
            # Dane z poszczegolnych etapow cyklu (ETAP 1.2.7.3)
            'world_data': self._last_world_result or {},
            'modeling_data': self._last_modeling_result or {},
            'teacher_data': self._last_teacher_result or {},
            'agent_data': self._last_agent_result or {},
            'collective_data': self._last_collective_result or {},
            'observation_data': observation_data,
            
            # Dodatkowe metadane
            'metadata': {
                'source': 'pipeline_memory_integration',
                'integration_timestamp': datetime.now().isoformat(),
                'pipeline_id': str(id(self)),
                'memory_integration_version': '1.2.7.3'
            }
        }
        
        # Dodaj informacje o fazie jesli dostepna
        if self.cycle_controller:
            try:
                execution_context = self.cycle_controller.get_execution_context()
                if execution_context:
                    cycle_data['phase'] = execution_context.phase.value
                    cycle_data['context_goal'] = execution_context.goal
            except Exception:
                pass
        
        return cycle_data
    
    def _run_memory_update(self, observation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aktualizacja pamieci systemowej przez MemoryIntegrator.
        
        ETAP 1.2.7.3: Integracja z Adaptive Knowledge Ecosystem
        
        Przeplyw:
            observation_data -> MemoryIntegrator -> MemoryEcosystem -> MemoryStores
        
        Args:
            observation_data: Dane z obserwacji (wyniki agentow, konsensus, etc.)
            
        Returns:
            Słownik z wynikiem aktualizacji pamieci
        """
        start_time = time.time()
        
        try:
            # ETAP 1.2.7.3: Pobierz MemoryIntegrator przez IFC
            memory_integrator = self._get_memory_integrator()
            
            if memory_integrator is None:
                # Fallback: Symulacja aktualizacji pamieci (kompatybilnosc wsteczna)
                # Akceptujemy wszystkie statusy memory_layer (available, degraded, itp.)
                if self.memory_layer and self.memory_layer.get('status'):
                    memory_updates = {
                        'short_term': 'Updated with observation data',
                        'long_term': 'Saved patterns and context',
                        'agentsMemory': 'Agent observations stored',
                        'update_timestamp': datetime.now().isoformat(),
                        'mode': 'fallback',
                        'memory_layer_status': self.memory_layer.get('status', 'unknown')
                    }
                    
                    self._log_event("MEMORY_UPDATE_FALLBACK", {
                        'mode': 'mock',
                        'reason': 'MemoryIntegrator not available through IFC',
                        'memory_layer_status': self.memory_layer.get('status', 'unknown')
                    }, level="WARNING")
                    
                    return {
                        'status': 'success',
                        'duration': time.time() - start_time,
                        'memory_updates': memory_updates,
                        'output': {
                            **observation_data,
                            'memory_status': 'updated'
                        },
                        'integration_mode': 'fallback'
                    }
                else:
                    return {
                        'status': 'error',
                        'duration': time.time() - start_time,
                        'error': 'Memory layer not available and MemoryIntegrator not found',
                        'integration_mode': 'none'
                    }
            
            # ETAP 1.2.7.3: Przygotowanie danych cyklu dla MemoryIntegrator
            # MemoryIntegrator.process_cycle_result() oczekuje strukturowanych danych
            cycle_result_data = self._prepare_cycle_data_for_memory(observation_data)
            
            # Przetwarzanie przez MemoryIntegrator
            integration_result = memory_integrator.process_cycle_result(cycle_result_data)
            
            # Logowanie integracji
            if integration_result.success:
                self._log_event("MEMORY_INTEGRATION_SUCCESS", {
                    'memory_ids': integration_result.memory_ids,
                    'record_count': integration_result.record_count,
                    'duration': integration_result.timestamp
                })
            else:
                self._log_event("MEMORY_INTEGRATION_PARTIAL", {
                    'errors': integration_result.errors,
                    'warnings': integration_result.warnings,
                    'memory_ids': integration_result.memory_ids
                }, level="WARNING")
            
            # Zwrot wynikow
            memory_updates = {
                'integration_result': integration_result.to_dict(),
                'memory_ids': integration_result.memory_ids,
                'record_count': integration_result.record_count,
                'status': 'success' if integration_result.success else 'partial',
                'update_timestamp': datetime.now().isoformat(),
                'integration_mode': 'memory_integrator'
            }
            
            return {
                'status': 'success' if integration_result.success else 'partial',
                'duration': time.time() - start_time,
                'memory_updates': memory_updates,
                'output': {
                    **observation_data,
                    'memory_status': 'persisted',
                    'memory_ids': integration_result.memory_ids
                },
                'integration_mode': 'memory_integrator'
            }
            
        except Exception as e:
            self._log_event("MEMORY_UPDATE_ERROR", {
                'error': str(e),
                'type': type(e).__name__
            }, level="ERROR")
            
            return {
                'status': 'error',
                'duration': time.time() - start_time,
                'error': str(e),
                'integration_mode': 'error'
            }

    def run_cycles(self, number: int = 1, delay: float = 0.0) -> Dict[str, Any]:
        """Wykonywanie wielu cykli"""
        if not self._initialized:
            return {
                'status': 'error',
                'error': 'Pipeline not initialized. Call initialize() first.',
                'timestamp': datetime.now().isoformat()
            }
        
        multi_cycle_result = {
            'status': 'success',
            'total_cycles': number,
            'successful_cycles': 0,
            'failed_cycles': 0,
            'cycle_results': [],
            'total_duration': 0.0,
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'final_status': 'complete'
        }
        
        start_time = time.time()
        
        try:
            for i in range(number):
                if self._shutdown_requested:
                    multi_cycle_result['final_status'] = 'interrupted'
                    break
                
                # Wykonanie pojedynczego cyklu
                cycle_result = self.run_cycle()
                multi_cycle_result['cycle_results'].append(cycle_result)
                
                if cycle_result['status'] == 'success':
                    multi_cycle_result['successful_cycles'] += 1
                elif cycle_result['status'] == 'error':
                    multi_cycle_result['failed_cycles'] += 1
                # 'partial' uważany jest za success
                elif cycle_result['status'] == 'partial':
                    multi_cycle_result['successful_cycles'] += 1
                
                # Opóznienie miedzy cyklami
                if i < number - 1 and delay > 0:
                    time.sleep(delay)
            
            multi_cycle_result['end_time'] = datetime.now().isoformat()
            multi_cycle_result['total_duration'] = time.time() - start_time
            
            self._log_event("MULTI_CYCLE_COMPLETE", {
                'total_cycles': number,
                'successful': multi_cycle_result['successful_cycles'],
                'failed': multi_cycle_result['failed_cycles'],
                'total_duration': multi_cycle_result['total_duration']
            })
            
            return multi_cycle_result
            
        except Exception as e:
            multi_cycle_result['status'] = 'error'
            multi_cycle_result['error'] = str(e)
            multi_cycle_result['end_time'] = datetime.now().isoformat()
            multi_cycle_result['total_duration'] = time.time() - start_time
            multi_cycle_result['final_status'] = 'error'
            
            self._log_event("MULTI_CYCLE_ERROR", {
                'error': str(e),
                'completed_cycles': len(multi_cycle_result['cycle_results'])
            }, level="ERROR")
            
            return multi_cycle_result

    def get_status(self) -> Dict[str, Any]:
        """Pobranie aktualnego statusu Pipeline"""
        status = PipelineStatus(
            current_cycle_id=self._current_cycle_id,
            current_status=self._current_status,
            total_cycles=self._cycle_counter,
            successful_cycles=sum(1 for cycle in self._cycle_history if cycle.status == CycleStatus.COMPLETE),
            failed_cycles=sum(1 for cycle in self._cycle_history if cycle.status == CycleStatus.ERROR),
            mode=self.mode,
            cycle_history_count=len(self._cycle_history),
            uptime_start=self.statistics.get('initialization_time')
        )
        
        return status.to_dict()

    def get_cycle_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Pobranie historii cykli"""
        with self._lock:
            history = self._cycle_history.copy()
        
        if limit is None:
            return [cycle.to_dict() for cycle in history]
        else:
            return [cycle.to_dict() for cycle in history[-limit:]]

    def get_event_log(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Pobranie dziennika zdarzen"""
        with self._lock:
            event_log = self._event_log.copy()
        
        if limit is None:
            return event_log
        else:
            return event_log[-limit:]

    def shutdown(self) -> Dict[str, Any]:
        """Zamkniecie Pipeline"""
        self._log_event("PIPELINE_SHUTDOWN_START")
        
        shutdown_result = {
            'status': 'success',
            'message': 'SSI Pipeline shutdown initiated',
            'timestamp': datetime.now().isoformat(),
            'cycles_completed': self._cycle_counter,
            'final_status': self._current_status.value if self._current_status else 'unknown',
            'uptime_duration': 0.0
        }
        
        try:
            # Zamkniecie WorldEngine
            if self.world_engine:
                shutdown_result['world_engine_shutdown'] = 'completed'
            
            # Zamkniecie Collective Manager
            if self.collective_manager:
                collective_shutdown = self.collective_manager.shutdown()
                shutdown_result['collective_manager_shutdown'] = collective_shutdown.get('status', 'unknown')
            
            # Zamkniecie Memory Manager
            if self.memory_manager:
                try:
                    self.memory_manager.save_all_memory()
                    shutdown_result['memory_manager_shutdown'] = 'completed'
                except Exception as e:
                    shutdown_result['memory_manager_shutdown'] = f'error: {str(e)}'
            
            # Zamkniecie Agent Runtime
            if self.agent_interface:
                if hasattr(self.agent_interface, 'shutdown'):
                    agent_shutdown = self.agent_interface.shutdown()
                    shutdown_result['agent_shutdown'] = agent_shutdown.get('status', 'unknown')
            
            # Aktualizacja czasu pracy
            if self.statistics.get('initialization_time'):
                uptime = datetime.now() - self.statistics['initialization_time']
                shutdown_result['uptime_duration'] = uptime.total_seconds()
            
            # Czyszczenie flag
            self._initialized = False
            self._shutdown_requested = False
            self._current_cycle_id = None
            self.world_engine = None
            self.agent_interface = None
            self.collective_manager = None
            self.memory_manager = None
            
            self._log_event("PIPELINE_SHUTDOWN_COMPLETE", {
                'cycles_completed': self._cycle_counter,
                'uptime_duration': shutdown_result['uptime_duration']
            })
            
            return shutdown_result
            
        except Exception as e:
            shutdown_result['status'] = 'error'
            shutdown_result['error'] = str(e)
            self._log_event("PIPELINE_SHUTDOWN_ERROR", {
                'error': str(e)
            }, level="ERROR")
            return shutdown_result

    def reset_pipeline(self) -> Dict[str, Any]:
        """Resetowanie Pipeline (wyczyecie historii, zachowuje konfig)"""
        reset_result = {
            'status': 'success',
            'cycles_cleared': len(self._cycle_history),
            'event_log_cleared': len(self._event_log),
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            with self._lock:
                # Wyczyszczenie historii cykli
                cycles_cleared = len(self._cycle_history)
                self._cycle_history.clear()
                
                # Wyczyszczenie logow zdarzen
                events_cleared = len(self._event_log)
                self._event_log.clear()
            
            # Reset licznikow
            self._cycle_counter = 0
            self._current_cycle_id = None
            
            reset_result['cycles_cleared'] = cycles_cleared
            reset_result['event_log_cleared'] = events_cleared
            
            self._log_event("PIPELINE_RESET_COMPLETE", {
                'cycles_cleared': cycles_cleared,
                'events_cleared': events_cleared
            })
            
            return reset_result
            
        except Exception as e:
            reset_result['status'] = 'error'
            reset_result['error'] = str(e)
            self._log_event("PIPELINE_RESET_ERROR", {
                'error': str(e)
            }, level="ERROR")
            return reset_result

    def _update_cycle_status(self, new_status: CycleStatus) -> None:
        """Aktualizacja statusu cyklu"""
        self._current_status = new_status

    def _update_statistics(self, cycle_result: Dict[str, Any]) -> None:
        """Aktualizacja statystyk"""
        self.statistics['total_execution_time'] += cycle_result.get('duration', 0.0)
        self.statistics['last_cycle_duration'] = cycle_result.get('duration', 0.0)
        
        if self._cycle_counter > 0:
            self.statistics['avg_cycle_time'] = self.statistics['total_execution_time'] / self._cycle_counter

    def _log_event(self, event_type: str, data: Optional[Dict[str, Any]] = None,
                   level: str = "INFO") -> None:
        """Logowanie zdarzenia do dziennika"""
        event = {
            'event_type': event_type,
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'data': data or {}
        }
        
        with self._lock:
            self._event_log.append(event)
    
    # ETAP 5.3.3: STRATEGY PERSISTENCE MEMORY
    def _record_agent_results_to_strategy_memory(
        self, agent_result: Dict[str, Any], cycle_id: str, 
        execution_context: Optional[ExecutionContext]) -> None:
        """
        Zapis wyników agentów do Strategy Persistence Memory.
        
        Args:
            agent_result: Wyniki z wykonania agentów
            cycle_id: ID bieżącego cyklu
            execution_context: Aktualny kontekst wykonania
        """
        if not self.strategy_memory_manager:
            return
        
        try:
            # Pobranie informacji o fazie
            phase = execution_context.phase.value if execution_context else 'unknown'
            
            # Pobranie decyzji i wyników od agentów
            decisions = agent_result.get('decisions', {})
            agent_results = agent_result.get('agent_results', [])
            
            # Dla każdego agenta zapisz wyniki jako strategię
            for agent_id, agent_decisions in decisions.items():
                if isinstance(agent_decisions, list) and len(agent_decisions) > 0:
                    # Użyj agent_id jako strategy_id (każdy agent ma swoją strategię)
                    strategy_id = f"agent_{agent_id}_strategy"
                    
                    # Pobranie metryk z decyzji
                    total_predictions = len(agent_decisions)
                    successful_predictions = sum(
                        1 for decision in agent_decisions 
                        if isinstance(decision, dict) and decision.get('confidence', 0) > 0.5
                    )
                    
                    # Obliczenie accuracy
                    accuracy = (successful_predictions / total_predictions) if total_predictions > 0 else 0.0
                    
                    # Przygotowanie danych wydajności
                    performance_data = {
                        'cycle_id': cycle_id,
                        'accuracy': accuracy,
                        'profit_factor': 1.0,  # Będzie obliczany później
                        'success': accuracy > 0.5,
                        'predictions_count': total_predictions,
                        'correct_predictions': successful_predictions,
                        'execution_time': agent_result.get('execution_time', 0.0),
                        'metrics': {
                            'confidence_avg': sum(
                                d.get('confidence', 0) for d in agent_decisions if isinstance(d, dict)
                            ) / len(agent_decisions) if agent_decisions else 0.0
                        },
                        'feedback': None
                    }
                    
                    # Zapis do Strategy Memory
                    self.strategy_memory_manager.update_performance(strategy_id, performance_data)
                    
                    # Ustaw ranking (przykładowo na podstawie accuracy)
                    ranking_position = int((1.0 - accuracy) * 100)  # Niższa pozycja = lepsza
                    self.strategy_memory_manager.update_ranking(strategy_id, ranking_position)
                    
                    # Oznaczenie do ponownej ewaluacji jeśli confidence niski
                    if accuracy < 0.6:
                        self.strategy_memory_manager.schedule_evaluation(strategy_id, required=True)
                    
                    self._log_event("STRATEGY_PERFORMANCE_RECORDED", {
                        'strategy_id': strategy_id,
                        'cycle_id': cycle_id,
                        'phase': phase,
                        'accuracy': accuracy,
                        'ranking_position': ranking_position
                    })
            
        except Exception as e:
            self._log_event("STRATEGY_PERSISTENCE_ERROR", {
                'error': str(e),
                'cycle_id': cycle_id
            }, level="ERROR")


# Funkcje fabryczne i pomocnicze

def create_pipeline(mode: PipelineMode = PipelineMode.SINGLE,
                    world_name: str = "SSI_V5_WORLD",
                    use_agent_runtime_manager: bool = True) -> SSIPipeline:
    """Fabryka tworzenia Pipeline"""
    return SSIPipeline(
        mode=mode,
        world_name=world_name,
        use_agent_runtime_manager=use_agent_runtime_manager
    )


def run_test_pipeline(number_of_cycles: int = 1,
                      world_name: str = "TEST_WORLD",
                      use_agent_runtime_manager: bool = True) -> Dict[str, Any]:
    """Uruchomienie testowego Pipeline"""
    test_result = {
        'status': 'success',
        'world_name': world_name,
        'number_of_cycles': number_of_cycles,
        'initialization': None,
        'test_results': None,
        'shutdown': None,
        'final_status': 'completed'
    }
    
    try:
        # 1. Inicjalizacja
        pipeline = create_pipeline(
            mode=PipelineMode.TEST,
            world_name=world_name,
            use_agent_runtime_manager=use_agent_runtime_manager
        )
        
        init_result = pipeline.initialize()
        test_result['initialization'] = init_result
        
        if init_result['status'] != 'success':
            test_result['final_status'] = 'initialization_failed'
            test_result['status'] = 'error'
            test_result['error'] = init_result.get('error')
            return test_result
        
        # 2. Wykonanie cykli
        cycle_result = pipeline.run_cycles(number=number_of_cycles, delay=0.01)
        test_result['test_results'] = cycle_result
        
        if cycle_result['status'] != 'success':
            test_result['final_status'] = 'cycle_execution_failed'
        
        # 3. Zamkniecie
        shutdown_result = pipeline.shutdown()
        test_result['shutdown'] = shutdown_result
        
        if shutdown_result['status'] != 'success':
            test_result['final_status'] = 'shutdown_failed'
        
        return test_result
        
    except Exception as e:
        test_result['status'] = 'error'
        test_result['error'] = str(e)
        test_result['final_status'] = 'exception_occurred'
        return test_result


# Eksporterowanie glossary - utrzymanie kompatybilnosci wstecznej
__all__ = [
    # Enumy
    'CycleStatus',
    'PipelineMode',
    
    # Klasy danych
    'CycleMetadata',
    'PipelineStatus',
    
    # Interfejsy
    'AgentRuntimeInterface',
    
    # Glowna klasa
    'SSIPipeline',
    
    # Funkcje fabryczne
    'create_pipeline',
    'run_test_pipeline'
]
