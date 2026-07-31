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
        
        # Agenci - zachowaj Kolejnosc 01-06
        self.agents: Dict[str, Any] = {}
        self._agent_execution_order = ["01", "02", "03", "04", "05", "06"]
        self.agent_manager: Optional[Any] = None
        
        # Collectory
        self.v2_collector: Optional[Any] = None
        self.v3_collector: Optional[Any] = None
        self.v4_collector: Optional[Any] = None
        self.external_collector: Optional[Any] = None
        
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
            
            # Inicjalizacja schedulera
            self.scheduler = create_scheduler(self.config, self.state_manager)
            self.scheduler.initialize()
            
            # Inicjalizacja agentow
            self._initialize_agents()
            
            # Inicjalizacja collectorow
            self._initialize_collectors()
            
            # Ustawienie flag
            self._initialized = True
            runtime_state.status = RuntimeStatus.READY.value
            runtime_state.next_agent_id = self._agent_execution_order[0]  # Pierwszy agent
            
            self.logger.info("SSI V5 Runtime Controller initialized successfully!")
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
            }
        }
        
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
        print("=" * 50)


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