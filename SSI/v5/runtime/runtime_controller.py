"""
SSI V5 - Runtime Controller
Główny kontroler systemu runtime

Zgodnie z dokumentacja Sprint 11.5:
- Runtime Controller
- Agent Runtime Foundation
- Memory Observation System

Odpowiedzialnosc:
- Inicjalizacja systemu
- Zarządzanie cyklem pracy
- Kontrola agentów
- Integracja z collectorami
- Zapis stanu systemu
"""

import os
import sys
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Union

# Dodanie sciezki do SSI do sys.path
SSI_PATH = "D:\\sts\\aplikacjaTyperBetAi\\SSI"
if SSI_PATH not in sys.path:
    sys.path.insert(0, SSI_PATH)

from .runtime_config import (
    RuntimeConfig, RuntimeStatus, RuntimeMode, RuntimeConfigManager,
    create_default_runtime_config
)
from .state_manager import (
    StateManager, StateType, RuntimeState, AgentState, MemoryState, CollectorState,
    create_state_manager
)
from .scheduler import (
    Scheduler, ScheduledTask, TaskPriority, TaskStatus, SchedulerMode,
    create_scheduler, CycleConfig
)

# ETAP 5.3: Cycle Controller - Warstwa swiadomosci cyklu
from .cycle_controller import (
    CyclePhase, CycleState, ExecutionContext, CycleController,
    PhaseDetector, create_cycle_controller
)

# FAZA 1 Modules - LLM Queue Manager
from .llm_queue import (
    LLMQueueManager, LLMQueueSettings, LLMQueueConfig,
    HardwareConstraints, ModelLimits, MemoryCleanupStrategy,
    QueueMode, ModelContext, ModelRequest, ModelResult,
    ModelType, ModelStatus, ModelPriority,
    create_llm_queue_manager, create_default_queue_config
)

# FAZA 1 Modules - Model Memory Ecosystem
from ..memory import (
    ModelMemoryStore, ModelMemoryType,
    TrainingMemory, ObservationMemory, BehaviorMemory,
    AgentAnalysisMemory, DecisionMemory,
    TrainingPhase, ObservationScope, BehaviorType, AnalysisType,
    create_model_memory_store, get_model_memory_store
)

# FAZA 1 Modules - Teacher Engine
from ..teacher import (
    TeacherEngine, TeacherConfig, TeacherMode,
    TeachingStrategy, TeacherStatus, ObservationStatus,
    create_teacher_engine, get_teacher_engine
)


class SSIRuntimeController:
    """Główny kontroler runtime systemu SSI V5.
    
    Funkcje:
    - initialize()
    - start_cycle()
    - run_cycle()
    - save_state()
    - load_previous_state()
    - shutdown()
    - get_status()
    """
    
    def __init__(self, config: Optional[RuntimeConfig] = None):
        """Inicjalizacja kontrolera."""
        self.config = config or create_default_runtime_config()
        self._initialized = False
        self._running = False
        self._shutdown_requested = False
        
        # Komponenty
        self.config_manager: Optional[RuntimeConfigManager] = None
        self.state_manager: Optional[StateManager] = None
        self.scheduler: Optional[Scheduler] = None
        
        # FAZA 1 Components - LLM Queue Manager
        self.llm_queue_manager: Optional[LLMQueueManager] = None
        self.llm_queue_settings: Optional[LLMQueueSettings] = None
        self.llm_queue_config: Optional[LLMQueueConfig] = None
        
        # FAZA 1 Components - Model Memory Ecosystem
        self.model_memory_store: Optional[ModelMemoryStore] = None
        
        # FAZA 1 Components - Teacher Engine
        self.teacher_engine: Optional[TeacherEngine] = None
        
        # Agenci - zachowaj Kolejnosc 01-06
        self.agents: Dict[str, Any] = {}
        self._agent_execution_order = ["01", "02", "03", "04", "05", "06"]
        self.agent_manager: Optional[Any] = None
        
        # Collectory
        self.v2_collector: Optional[Any] = None
        self.v3_collector: Optional[Any] = None
        self.v4_collector: Optional[Any] = None
        self.external_collector: Optional[Any] = None
        
        # ETAP 5.3: Cycle Controller - Warstwa swiadomosci cyklu
        self.cycle_controller: Optional[CycleController] = None
        
        # Logging
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Sciezki
        self._runtime_path = self.config.runtime_path
        self._agents_path = self.config.agents_path
        self._memory_path = self.config.memory_path
        
    def initialize(self) -> bool:
        """Inicjalizacja systemu runtime."""
        try:
            self.logger.info("Initializing SSI V5 Runtime Controller...")
            
            # Inicjalizacja konfiguracji
            self.config_manager = RuntimeConfigManager(self.config)
            
            # Inicjalizacja managera stanu
            self.state_manager = create_state_manager(self.config)
            self.state_manager.initialize()
            
            # Ustawienie trybu testowego w stanie
            runtime_state = self.state_manager.get_runtime_state()
            runtime_state.test_mode = self.config.test_mode
            
            # FAZA 1: Inicjalizacja LLM Queue Manager
            self._initialize_llm_queue_manager()
            
            # FAZA 1: Inicjalizacja Model Memory Ecosystem
            self._initialize_model_memory_store()
            
            # FAZA 1: Inicjalizacja Teacher Engine
            self._initialize_teacher_engine()
            
            # ETAP 5.3: Inicjalizacja Cycle Controller
            self._initialize_cycle_controller()
            
            # Inicjalizacja schedulera
            self.scheduler = create_scheduler(self.config, self.state_manager)
            self.scheduler.initialize()
            
            # Inicjalizacja agentow
            self._initialize_agents()
            
            # Inicjalizacja collectorow
            self._initialize_collectors()
            
            # Po polaczeniu wszystkich komponentow - integracja FAZA 1
            self._integrate_faza1_components()
            
            # Ustawienie flag
            self._initialized = True
            runtime_state.status = RuntimeStatus.READY.value
            runtime_state.next_agent_id = self._agent_execution_order[0]  # Pierwszy agent
            
            self.logger.info("SSI V5 Runtime Controller with FAZA 1 modules initialized successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing runtime controller: {e}")
            if self.state_manager:
                self.state_manager.set_error(str(e))
            return False
            
    def _initialize_agents(self) -> None:
        """Inicjalizacja agentow."""
        try:
            from ..agents import agent_manager
            
            # Tworzenie agent manager
            self.agent_manager = agent_manager.create_agent_manager(self.config)
            
            # Tworzenie 6 agentow
            for i in range(1, 7):
                agent_id = f"0{i}"
                agent_config = self.config_manager.get_agent_config(agent_id)
                
                agent = self.agent_manager.create_agent(agent_config)
                self.agents[agent_id] = agent
                
                # Aktualizacja stanu
                if self.state_manager:
                    self.state_manager.update_agent_state(
                        agent_id,
                        status="initialized"
                    )
                    
            self.logger.info(f"Initialized {len(self.agents)} agents")
            
        except Exception as e:
            self.logger.error(f"Error initializing agents: {e}")
            raise
            
    def _initialize_collectors(self) -> None:
        """Inicjalizacja collectorow."""
        try:
            # Import collectorow z input_layer
            from ...v5.input_layer import v2_collector, external
            
            # V2 Collector
            if self.config.enable_v2_collector:
                self.v2_collector = v2_collector.V2DataCollector()
                self.state_manager.update_collector_status(
                    "v2", "initialized"
                )
                self.logger.info("V2 Collector initialized")
                
            # V3 Collector
            if self.config.enable_v3_collector:
                try:
                    from ...v5.input_layer import v3_collector
                    self.v3_collector = v3_collector.V3KnowledgeCollector()
                    self.state_manager.update_collector_status(
                        "v3", "initialized"
                    )
                    self.logger.info("V3 Collector initialized")
                except ImportError:
                    self.logger.warning("V3 Collector not available")
                    
            # V4 Collector
            if self.config.enable_v4_collector:
                try:
                    from ...v5.input_layer import v4_collector
                    self.v4_collector = v4_collector.V4AgentsCollector()
                    self.state_manager.update_collector_status(
                        "v4", "initialized"
                    )
                    self.logger.info("V4 Collector initialized")
                except ImportError:
                    self.logger.warning("V4 Collector not available")
                    
            # External Collector
            if self.config.enable_external_collector:
                self.external_collector = external.ExternalKnowledgeCollector()
                self.state_manager.update_collector_status(
                    "external", "initialized"
                )
                self.logger.info("External Collector initialized")
                
        except Exception as e:
            self.logger.error(f"Error initializing collectors: {e}")
            raise
    
    # ==================== FAZA 1: LLM QUEUE MANAGER ====================
    
    def _initialize_llm_queue_manager(self) -> None:
        """Inicjalizacja LLM Queue Manager - FAZA 1."""
        try:
            # Tworzenie ustawien kolejki
            self.llm_queue_settings = create_default_queue_config()
            
            # Tworzenie konfiguracji kolejki
            self.llm_queue_config = LLMQueueConfig.from_settings(self.llm_queue_settings)
            
            # Tworzenie managera kolejki (nie uruchamiany automatycznie)
            self.llm_queue_manager = create_llm_queue_manager(
                settings=self.llm_queue_settings,
                auto_start=False  # Uruchomimy recznie w start_cycle
            )
            
            self.logger.info("LLM Queue Manager initialized (FAZA 1)")
        except Exception as e:
            self.logger.error(f"Error initializing LLM Queue Manager: {e}")
            raise
    
    # ==================== FAZA 1: MODEL MEMORY ECOSYSTEM ====================
    
    def _initialize_model_memory_store(self) -> None:
        """Inicjalizacja Model Memory Store - FAZA 1."""
        try:
            # Sciezka do pamieci modeli
            memory_base_path = os.path.join(self._memory_path, "model_memory")
            
            # Tworzenie storagu pamieci modeli
            self.model_memory_store = create_model_memory_store(
                base_path=memory_base_path
            )
            
            self.logger.info(f"Model Memory Store initialized at {memory_base_path} (FAZA 1)")
        except Exception as e:
            self.logger.error(f"Error initializing Model Memory Store: {e}")
            raise
    
    # ==================== FAZA 1: TEACHER ENGINE ====================
    
    def _initialize_teacher_engine(self) -> None:
        """Inicjalizacja Teacher Engine - FAZA 1."""
        try:
            # Tworzenie konfiguracji Teacher Engine
            teacher_config = TeacherConfig()
            
            # Tworzenie silnika nauczyciela (nie uruchamiany automatycznie)
            self.teacher_engine = create_teacher_engine(
                config=teacher_config,
                auto_start=False  # Uruchomimy recznie w start_cycle
            )
            
            # Rejestracja agentow w Teacher Engine (jesli agenci sa juz zarejestrowani)
            if self.agent_manager and self.agents:
                self.teacher_engine.register_agents(self.agents)
            
            self.logger.info("Teacher Engine initialized (FAZA 1)")
        except Exception as e:
            self.logger.error(f"Error initializing Teacher Engine: {e}")
            raise
    
    # ==================== ETAP 5.3: CYCLE CONTROLLER ====================
    
    def _initialize_cycle_controller(self) -> None:
        """Inicjalizacja Cycle Controller - warstwa swiadomosci cyklu."""
        try:
            # Utworzenie kontrolera cyklu
            cycle_state_path = os.path.join(self._runtime_path, "cycle_state.json")
            self.cycle_controller = create_cycle_controller(
                state_path=cycle_state_path,
                logger=self.logger
            )
            
            self.logger.info("Cycle Controller initialized (ETAP 5.3) - Cycle Awareness Layer")
            
        except Exception as e:
            self.logger.error(f"Error initializing Cycle Controller: {e}")
            # To nie jest krytyczny blad - system moze dzialac dalej
            self.logger.warning("Cycle Controller will not be available, but system can continue")
    
    # ==================== FAZA 1: INTEGRACJA KOMPONENTOW ====================
    
    def _integrate_faza1_components(self) -> None:
        """Integracja komponentow FAZA 1: LLM Queue -> Model Memory -> Teacher Engine."""
        try:
            # Polacz Teacher Engine z Model Memory Store
            if self.teacher_engine and self.model_memory_store:
                self.teacher_engine.set_model_memory_store(self.model_memory_store)
                self.logger.info("Teacher Engine connected to Model Memory Store")
            
            # Polacz Teacher Engine z LLM Queue Manager (opcjonalnie)
            if self.teacher_engine and self.llm_queue_manager:
                # Teacher Engine moze korzystac z kolejki LLM do Wysylania zadan
                self.logger.info("Teacher Engine and LLM Queue Manager ready for integration")
            
            # Zarejestruj componente w runtime state
            if self.state_manager:
                runtime_state = self.state_manager.get_runtime_state()
                # Dodaj informacje o FAZA 1 do metadata
                runtime_state.metadata["faza1_enabled"] = True
                runtime_state.metadata["faza1_components"] = {
                    "llm_queue": "initialized" if self.llm_queue_manager else "disabled",
                    "model_memory": "initialized" if self.model_memory_store else "disabled", 
                    "teacher_engine": "initialized" if self.teacher_engine else "disabled"
                }
            
            self.logger.info("FAZA 1 components integrated successfully")
            
        except Exception as e:
            self.logger.error(f"Error integrating FAZA 1 components: {e}")
            # To nie jest krytyczny blad - system moze dzialac dalej
            if self.state_manager:
                self.state_manager.set_warning(f"FAZA 1 integration warning: {e}")
    
    def start_cycle(self) -> bool:
        """Rozpoczecie nowego cyklu pracy systemu."""
        if not self._initialized:
            self.logger.error("Runtime not initialized. Call initialize() first.")
            return False
            
        if self._running:
            self.logger.warning("Cycle already running.")
            return False
            
        try:
            self.logger.info("Starting SSI V5 cycle...")
            self._running = True
            self._shutdown_requested = False
            
            # ETAP 5.3: Detekcja fazy cyklu na podstawie stanu swiata
            if self.cycle_controller:
                world_state = self._get_world_state_for_cycle_detection()
                current_phase = self.cycle_controller.detect_current_phase(world_state)
                execution_context = self.cycle_controller.get_execution_context()
                self.logger.info(
                    f"Cycle Controller: Phase={current_phase.value}, "
                    f"Goal={execution_context.goal}"
                )
            else:
                self.logger.warning("Cycle Controller not available - running without phase awareness")
            
            # FAZA 1: Start LLM Queue Manager
            if self.llm_queue_manager:
                self.llm_queue_manager.start()
                self.logger.info("LLM Queue Manager started (FAZA 1)")
            
            # FAZA 1: Start Teacher Engine
            if self.teacher_engine:
                self.teacher_engine.start()
                self.logger.info("Teacher Engine started (FAZA 1)")
            
            # Start schedulera
            self.scheduler.start()
            
            # Rozpoczecie cyklu w state manager
            self.state_manager.start_cycle()
            
            # Ustawienie czasu rozpoczęcia
            now = datetime.now().isoformat()
            self.state_manager.get_runtime_state().start_time = now
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting cycle: {e}")
            self.state_manager.set_error(str(e))
            return False
            
    def run_cycle(self) -> bool:
        """Wykonywanie pojedynczego cyklu (dla wstecznej kompatybilnosci)."""
        if not self._initialized:
            self.logger.error("Runtime not initialized. Call initialize() first.")
            return False
            
        try:
            self.logger.info("Running single SSI V5 cycle...")
            
            # 1. Start cyklu
            self.state_manager.start_cycle()
            
            # 2. Uruchomienie collectorow
            self._run_collectors()
            
            # 3. Uruchomienie agentow
            self._run_agents_single_pass()
            
            # 4. Zapis stanu
            self.save_state()
            
            # 5. Zakonczenie cyklu
            self.state_manager.end_cycle()
            
            self.logger.info("Single SSI V5 cycle completed!")
            return True
            
        except Exception as e:
            self.logger.error(f"Error running single cycle: {e}")
            self.state_manager.set_error(str(e))
            return False
            
    def run_loop(self) -> bool:
        """GLOWNA METODA: Wykonywanie ciągłej pętli runtime (do 5 godzin).
        
        NOWY MODEL ARCHITEKTURY (Sprint 11.5 v2.0):
        - Ciągła pętla while runtime_active
        - W każdej iteracji: Kazdy agent (01-06) -> Zapis doswiadczenia -> Aktualizacja pamieci
        - Wielokrotne wykonywanie agentow podczas jednego uruchomienia systemu
        """
        if not self._initialized:
            self.logger.error("Runtime not initialized. Call initialize() first.")
            return False
            
        try:
            self.logger.info("Starting SSI V5 Runtime Continuous Loop...")
            
            # Ustawienie flag
            self._running = True
            self._shutdown_requested = False
            
            runtime_state = self.state_manager.get_runtime_state()
            runtime_state.start_time = datetime.now().isoformat()
            runtime_state.cycle_count = 0
            runtime_state.current_test_cycle = 0
            runtime_state.last_agent_id = None
            
            # Ustal limit cykli na podstawie trybu
            if self.config.test_mode:
                max_cycles = self.config.test_cycles
                self.logger.info(f"TEST MODE: Running {max_cycles} cycles")
            else:
                max_cycles = float('inf')
            
            # Rozpoczecie pierwszego cyklu
            self.state_manager.start_cycle()
            
            # LOGOWANIE STARTU
            print("SSI STARTED")
            print()
            print("Runtime:")
            print("ACTIVE")
            print()
            
            # GLowna petla - CIAGLY CYKL AGENTOW
            cycle_count = 0
            iteration_count = 0
            
            while (self._running and 
                   not self._shutdown_requested and
                   cycle_count < max_cycles):
                
                cycle_count += 1
                runtime_state.cycle_count = cycle_count
                runtime_state.current_test_cycle = cycle_count
                
                # Pobierz aktualny kontekst swiata
                world_context = self._get_current_world_context()
                
                # WYKONAJ AGENTOW W USTALONEJ KOLEJNOSCI 01-06
                for agent_id in self._agent_execution_order:
                    if not self._running or self._shutdown_requested:
                        break
                        
                    agent = self.agents.get(agent_id)
                    if not agent:
                        continue
                    
                    try:
                        # Wykonanie pojedynczego cyklu agenta
                        result = self._run_single_agent_cycle(agent, world_context, cycle_count)
                        
                        iteration_count += 1
                        
                        # Aktualizacja stanu agenta
                        self.state_manager.update_agent_state(
                            agent_id,
                            last_activity_time=datetime.now().isoformat(),
                            status="completed",
                            decisions_made=1
                        )
                        
                        # Ustaw ostatni wykonany agent
                        runtime_state.last_agent_id = agent_id
                        
                        # Zapis pamieci agenta po kazdym cyklu
                        if self.config.memory_persistence and hasattr(agent, 'save_memory'):
                            agent.save_memory()
                        
                        self.logger.info(f"Agent_{agent_id}: Cycle {cycle_count} Iteration {iteration_count} completed")
                        
                    except Exception as e:
                        self.logger.error(f"Error running Agent_{agent_id}: {e}")
                        self.state_manager.update_agent_state(
                            agent_id,
                            errors_made=1,
                            status="error"
                        )
                        
                # Aktualizacja wspolnej pamieci (przyszle implementacje)
                self._update_shared_memory()
                
                # Zakonczenie biezacego cyklu
                self.state_manager.end_cycle()
                
                # Rozpoczecie nowego cyklu
                self.state_manager.start_cycle()
                
                # Okresowy zapis stanu - teraz po kazdym cyklu w trybie testowym
                if self.config.auto_save:
                    if self.config.test_mode or cycle_count % 10 == 0:
                        self.save_state()
                    
                # Maly sleep miedzy cyklami - mniejszy w trybie testowym
                sleep_time = 0.1 if self.config.test_mode else 1.0
                time.sleep(sleep_time)
                
            # Koniec petli - finalizacja
            runtime_state.stop_time = datetime.now().isoformat()
            runtime_state.total_cycles = cycle_count
            runtime_state.metadata["total_iterations"] = iteration_count
            
            self._finalize_runtime_loop()
            
            self.logger.info(f"SSI V5 Runtime Loop completed! Cycles: {cycle_count}, Iterations: {iteration_count}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in runtime loop: {e}")
            self.state_manager.set_error(str(e))
            return False
            
    def _run_collectors(self) -> bool:
        """Uruchomienie wszystkich collectorow."""
        try:
            self.logger.info("Running collectors...")
            
            collectors = []
            if self.v2_collector:
                collectors.append(("v2", self.v2_collector))
            if self.v3_collector:
                collectors.append(("v3", self.v3_collector))
            if self.v4_collector:
                collectors.append(("v4", self.v4_collector))
            if self.external_collector:
                collectors.append(("external", self.external_collector))
                
            for name, collector in collectors:
                try:
                    self.logger.info(f"Running {name} collector...")
                    result = collector.collect()
                    
                    if result:
                        self.state_manager.update_collector_status(
                            name, "completed", datetime.now().isoformat()
                        )
                        self.logger.info(f"{name} collector completed")
                    else:
                        self.state_manager.update_collector_status(
                            name, "failed", datetime.now().isoformat()
                        )
                        self.logger.warning(f"{name} collector returned no data")
                        
                except Exception as e:
                    self.logger.error(f"Error running {name} collector: {e}")
                    self.state_manager.update_collector_status(
                        name, "error", datetime.now().isoformat()
                    )
                    
            # Utworzenie UnifiedInputPackage
            self._create_unified_input_package()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in _run_collectors: {e}")
            return False
            
    def _update_shared_memory(self) -> None:
        """Aktualizacja wspolnej pamieci (przygotowanie pod przyszle implementacje)."""
        # W przyszlosci: synchronizacja pamieci miedzy agentami
        pass
        
    def _finalize_runtime_loop(self) -> None:
        """Finalizacja pętli runtime."""
        # Zapis stanu
        if self.config.auto_save:
            self.save_state()
            
        # Zakonczenie cyklu
        self.state_manager.end_cycle()
        
        # Status shutdown
        print("SSI SHUTDOWN")
        print()
        print(f"State saved:")
        print(f"runtime_state.json")
        
        self.logger.info("Runtime loop finalized")
        
    def _create_unified_input_package(self) -> bool:
        """Utworzenie UnifiedInputPackage z danych wszystkich collectorow."""
        try:
            from ...v5.input_layer.collector_manager import CollectorManager
            
            # Utworzenie UnifiedInputPackage
            data = {}
            
            if self.v2_collector:
                data["v2"] = self.v2_collector.get_latest_data()
            if self.v3_collector:
                data["v3"] = self.v3_collector.get_latest_data()
            if self.v4_collector:
                data["v4"] = self.v4_collector.get_latest_data()
            if self.external_collector:
                data["external"] = self.external_collector.get_latest_data()
                
            # Zapisanie pakietu
            package = {
                "timestamp": datetime.now().isoformat(),
                "data": data,
                "version": "1.0.0"
            }
            
            # Oznaczenie w state manager
            self.state_manager.set_unified_package_created()
            
            self.logger.info("UnifiedInputPackage created")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating unified package: {e}")
            return False
            
    def _run_agents(self) -> bool:
        """Uruchomienie wszystkich agentow."""
        try:
            self.logger.info("Running agents...")
            
            for agent_id, agent in self.agents.items():
                try:
                    self.logger.info(f"Running agent {agent_id}...")
                    
                    # Uruchomienie cyklu agenta
                    result = agent.run_cycle()
                    
                    # Aktualizacja stanu
                    self.state_manager.update_agent_state(
                        agent_id,
                        last_activity_time=datetime.now().isoformat()
                    )
                    
                    self.logger.info(f"Agent {agent_id} completed: {result}")
                    
                except Exception as e:
                    self.logger.error(f"Error running agent {agent_id}: {e}")
                    self.state_manager.update_agent_state(
                        agent_id,
                        errors_made=1,
                        status="error"
                    )
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Error in _run_agents: {e}")
            return False
            
    def _run_agents_single_pass(self) -> bool:
        """Wykonywanie pojedynczego przebiegu wszystkich agentow (dla wstecznej kompatybilnosci)."""
        try:
            for agent_id, agent in self.agents.items():
                collector_data = self._collect_current_data()
                world_context = self._get_current_world_context()
                
                result = agent.run_cycle(collector_data, world_context, 1)
                
                self.logger.info(f"Agent {agent_id} completed: {result}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error in single agent pass: {e}")
            return False
            
    def _run_single_agent_cycle(self, agent, world_context: Dict[str, Any], 
                               cycle_count: int) -> Dict[str, Any]:
        """Wykonywanie pojedynczego cyklu dla jednego agenta.
        
        CYKL AGENTA (zgodnie z Sprint 11.5 v2.0):
        1. Wczytaj pamięć
        2. Pobierz dane (V2, V3, V4, External)
        3. Porównaj: STARA WIEDZA + NOWE DANE
        4. Analiza
        5. Decyzja
        6. Zapis doświadczenia
        7. Aktualizacja historii
        """
        try:
            # 1. Wczytaj pamiec
            agent.load_memory()
            
            # 2. Pobierz dane
            collector_data = self._collect_current_data()
            
            # 3. Wykonanie cyklu agenta
            result = agent.run_cycle(collector_data, world_context, cycle_count)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Agent cycle error: {e}")
            return {"error": str(e), "success": False}
            
    def _collect_current_data(self) -> Dict[str, Any]:
        """Pobranie aktualnych danych z wszystkich collectorow."""
        data = {}
        
        if self.v2_collector:
            try:
                data["v2"] = self.v2_collector.get_latest_data()
            except:
                data["v2"] = None
                
        if self.v3_collector:
            try:
                data["v3"] = self.v3_collector.get_latest_data()
            except:
                data["v3"] = None
                
        if self.v4_collector:
            try:
                data["v4"] = self.v4_collector.get_latest_data()
            except:
                data["v4"] = None
                
        if self.external_collector:
            try:
                data["external"] = self.external_collector.get_latest_data()
            except:
                data["external"] = None
                
        return data
        
    def _get_current_world_context(self) -> Dict[str, Any]:
        """Pobranie aktualnego kontekstu świata."""
        return {
            "timestamp": datetime.now().isoformat(),
            "cycle_count": self.state_manager.get_runtime_state().cycle_count,
            "runtime_status": self.state_manager.get_runtime_state().status,
            "active_agents": len([a for a in self.agents.values() if a.is_active() if hasattr(a, 'is_active')])
        }
            
    def save_state(self, state_type: StateType = StateType.FULL,
                   custom_path: Optional[str] = None) -> bool:
        """Zapis stanu systemu."""
        try:
            if not self.state_manager:
                self.logger.error("State manager not initialized")
                return False
                
            self.logger.info("Saving system state...")
            
            # Zapis stanu runtime
            self.state_manager.get_runtime_state().last_save_time = datetime.now().isoformat()
            
            result = self.state_manager.save_state(state_type, custom_path)
            
            if result:
                self.logger.info(f"State saved: {state_type.value}")
                return True
            else:
                self.logger.error("Failed to save state")
                return False
                
        except Exception as e:
            self.logger.error(f"Error saving state: {e}")
            return False
            
    def load_previous_state(self, state_type: StateType = StateType.FULL,
                           custom_path: Optional[str] = None) -> bool:
        """Zaladowanie poprzeniego stanu systemu."""
        try:
            if not self.state_manager:
                self.logger.error("State manager not initialized")
                return False
                
            self.logger.info("Loading previous state...")
            
            result = self.state_manager.load_state(state_type, custom_path)
            
            if result:
                self.logger.info(f"State loaded: {state_type.value}")
                return True
            else:
                self.logger.warning(f"No previous state found: {state_type.value}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error loading state: {e}")
            return False
            
    def shutdown(self) -> bool:
        """Wylaczenie systemu runtime."""
        try:
            self.logger.info("Shutting down SSI V5 Runtime Controller...")
            
            self._shutdown_requested = True
            self._running = False
            
            # FAZA 1: Stop Teacher Engine
            if self.teacher_engine:
                self.teacher_engine.stop()
                self.logger.info("Teacher Engine stopped (FAZA 1)")
                
            # FAZA 1: Stop LLM Queue Manager
            if self.llm_queue_manager:
                self.llm_queue_manager.stop()
                self.logger.info("LLM Queue Manager stopped (FAZA 1)")
                
            # Zapis stanu Model Memory
            if self.model_memory_store:
                self.model_memory_store.save_all()
                self.logger.info("Model Memory saved (FAZA 1)")
            
            # ETAP 5.3: Zapis stanu cyklu
            if self.cycle_controller:
                self.cycle_controller.save_cycle_state()
                self.logger.info("Cycle state saved (ETAP 5.3)")
                
            # Zatrzymanie schedulera
            if self.scheduler:
                self.scheduler.shutdown()
                
            # Zatrzymanie agentow
            if self.agent_manager:
                self.agent_manager.shutdown()
                
            # Zapis stanu
            if self.config.auto_save:
                self.save_state()
                
            # Aktualizacja stanu
            if self.state_manager:
                self.state_manager.shutdown()
                
            self._initialized = False
            
            self.logger.info("SSI V5 Runtime Controller shut down!")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            return False
            
    def get_status(self) -> Dict[str, Any]:
        """Pobranie statusu systemu."""
        status = {
            "runtime": {
                "initialized": self._initialized,
                "running": self._running,
                "shutdown_requested": self._shutdown_requested
            },
            "config": {
                "name": self.config.name,
                "version": self.config.version,
                "cycle_duration_hours": self.config.cycle_duration_hours,
                "agents_count": self.config.agent_count
            },
            "agents": {
                agent_id: "active" if agent else "inactive"
                for agent_id, agent in self.agents.items()
            },
            "collectors": {
                "v2": "active" if self.v2_collector else "inactive",
                "v3": "active" if self.v3_collector else "inactive",
                "v4": "active" if self.v4_collector else "inactive",
                "external": "active" if self.external_collector else "inactive"
            },
            # FAZA 1 Components status
            "faza1_components": {
                "llm_queue": "active" if (self.llm_queue_manager and self.llm_queue_manager._running) else "inactive",
                "model_memory": "active" if self.model_memory_store else "inactive", 
                "teacher_engine": "active" if (self.teacher_engine and self.teacher_engine._running) else "inactive"
            }
        }
        
        # FAZA 1: Dodaj status LLM Queue Manager
        if self.llm_queue_manager:
            try:
                queue_status = self.llm_queue_manager.get_status()
                status["llm_queue"] = {
                    "running": queue_status.get("running", False),
                    "queue_size": queue_status.get("queue_size", 0),
                    "is_executing": queue_status.get("is_executing", False),
                    "current_model": queue_status.get("current_model", None)
                }
            except:
                pass
        
        # FAZA 1: Dodaj status Teacher Engine
        if self.teacher_engine:
            try:
                teacher_status = self.teacher_engine.get_statistics()
                status["teacher_engine"] = {
                    "status": teacher_status.get("status", "UNKNOWN"),
                    "running": teacher_status.get("running", False),
                    "agents_monitored": teacher_status.get("agents_monitored", 0)
                }
            except:
                pass
                
        # FAZA 1: Dodaj status Model Memory
        if self.model_memory_store:
            try:
                memory_stats = self.model_memory_store.get_statistics()
                status["model_memory"] = {
                    "entry_count": memory_stats.get("entry_count", 0),
                    "initialized": memory_stats.get("initialized", False),
                    "by_type": memory_stats.get("by_type", {})
                }
            except:
                pass
        
        # ETAP 5.3: Dodaj status Cycle Controller
        if self.cycle_controller:
            try:
                cycle_state = self.cycle_controller.get_cycle_state()
                if cycle_state:
                    status["cycle_controller"] = {
                        "current_phase": cycle_state.current_phase.value if cycle_state.current_phase else "unknown",
                        "cycle_id": cycle_state.cycle_id,
                        "completed_phases": cycle_state.completed_phases,
                        "started_at": cycle_state.started_at,
                        "last_update": cycle_state.last_update
                    }
            except:
                pass
        
        # Dodanie stanu z state manager
        if self.state_manager:
            runtime_state = self.state_manager.get_runtime_state()
            status["runtime_state"] = {
                "status": runtime_state.status,
                "cycle_count": runtime_state.cycle_count,
                "total_cycles": runtime_state.total_cycles,
                "total_iterations": runtime_state.metadata.get("total_iterations", 0),
                "start_time": runtime_state.start_time,
                "last_save": runtime_state.last_save_time
            }
            
        return status
        
    def print_status(self) -> None:
        """Wyswietlenie statusu systemu."""
        status = self.get_status()
        
        print("=" * 50)
        print("SSI V5 Runtime Controller Status")
        print("=" * 50)
        print(f"Runtime: {'ACTIVE' if self._initialized and self._running else 'INACTIVE'}")
        print(f"Name: {status['config']['name']}")
        print(f"Version: {status['config']['version']}")
        print(f"Cycle Duration: {status['config']['cycle_duration_hours']} hours")
        print()
        print("Agents:")
        for agent_id, agent_status in status['agents'].items():
            print(f"  [OK] {agent_id}: {agent_status}")
        print()
        print("Collectors:")
        for collector_name, collector_status in status['collectors'].items():
            print(f"  [OK] {collector_name}: {collector_status}")
        print()
        if 'runtime_state' in status:
            rs = status['runtime_state']
            print("Runtime State:")
            print(f"  Status: {rs['status']}")
            print(f"  Cycle Count: {rs['cycle_count']}")
            print(f"  Total Cycles: {rs.get('total_cycles', 0)}")
            print(f"  Total Iterations: {rs.get('total_iterations', 0)}")
            print(f"  Start Time: {rs['start_time']}")
            print(f"  Last Save: {rs['last_save']}")
        
        if 'cycle_controller' in status:
            cc = status['cycle_controller']
            print()
            print("Cycle Controller (ETAP 5.3):")
            print(f"  Current Phase: {cc['current_phase']}")
            print(f"  Cycle ID: {cc['cycle_id']}")
            print(f"  Completed Phases: {cc['completed_phases']}")
        print("=" * 50)
    
    def _get_world_state_for_cycle_detection(self) -> Dict[str, Any]:
        """
        Pobranie stanu swiata do detekcji fazy cyklu.
        
        Zwraca slownik ze stanem swiata, bazy danych, wynikow i kursow.
        Uzywane przez Cycle Controller do okre patient fazy.
        
        Returns:
            Dict: Stan swiata dla detekcji fazy
        """
        world_state = {
            'is_ready': False, 'status': 'UNKNOWN', 'timestamp': None,
            'database_status': 'UNKNOWN', 'database_version': None, 'database_timestamp': None,
            'new_results_available': False, 'results_processed': False,
            'odds_available': False, 'odds_timestamp': None,
            'prediction_cycle_completed': False
        }
        
        if self.v2_collector:
            try:
                v2_data = self.v2_collector.get_latest_data()
                if v2_data:
                    world_state.update({
                        'is_ready': v2_data.get('is_ready', False),
                        'status': v2_data.get('status', 'UNKNOWN'),
                        'timestamp': v2_data.get('timestamp')
                    })
            except: pass
        
        if self.state_manager:
            runtime_state = self.state_manager.get_runtime_state()
            world_state['prediction_cycle_completed'] = runtime_state.metadata.get('prediction_cycle_completed', False)
        
        return world_state


def create_runtime_controller(config: Optional[RuntimeConfig] = None) -> SSIRuntimeController:
    """Tworzenie kontrolera runtime."""
    return SSIRuntimeController(config)


if __name__ == "__main__":
    import logging
    
    # Konfiguracja logowania
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Testing SSI V5 Runtime Controller...")
    
    try:
        # Utworzenie kontrolera
        controller = create_runtime_controller()
        
        # Inicjalizacja
        if controller.initialize():
            print("✓ Runtime Controller initialized")
        else:
            print("✗ Failed to initialize Runtime Controller")
            sys.exit(1)
            
        # Status
        controller.print_status()
        
        # Test cykli
        print("\nTesting cycle...")
        if controller.start_cycle():
            print("✓ Cycle started")
        else:
            print("✗ Failed to start cycle")
            
        # Wykonywanie through
        controller.run_cycle()
        
        # Zapis stanu
        if controller.save_state():
            print("✓ State saved")
        else:
            print("✗ Failed to save state")
            
        # Zatrzymanie
        if controller.shutdown():
            print("✓ Runtime shut down")
        else:
            print("✗ Failed to shut down")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
    print("\nRuntime Controller test completed!")