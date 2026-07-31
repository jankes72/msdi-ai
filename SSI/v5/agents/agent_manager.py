"""
SSI V5 - Agent Manager
Centralny manager agentow

Zgodnie z dokumentacja Sprint 11.5 v2.0:
- Agent Runtime Foundation
- Memory Observation System

Odpowiedzialnosc:
- Tworzenie i zarzadzanie agentami
- Koordynacja pracy agentow
- Integracja z Runtime Controller
- Zarzadzanie stanem wszystkich agentow
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

# Dodanie sciezki do SSI do sys.path
SSI_PATH = "D:\\sts\\aplikacjaTyperBetAi\\SSI"
if SSI_PATH not in sys.path:
    sys.path.insert(0, SSI_PATH)

from .agents_config import (
    AgentConfig, AgentStatus, AgentType, create_all_agent_configs,
    create_agent_config, AgentRuntimeConfig
)
from .agent_runtime import AgentRuntime, create_agent
from .agent_state import AgentStateManager, create_agent_state_manager


class AgentManager:
    """Centralny manager agentow.
    
    Zarzadza:
    - Tworzeniem agentow
    - ich cyklem zycia
    - Koordynacja pracy
    - Integracja z runtime
    """
    
    def __init__(self, runtime_config: Optional[AgentRuntimeConfig] = None):
        """Inicjalizacja managera agentow."""
        self.runtime_config = runtime_config
        self.agents: Dict[str, AgentRuntime] = {}
        self._initialized = False
        self._running = False
        
        # Logging
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Konfiguracja bazowych sciezek
        self._memory_base_path = "D:\\sts\\aplikacjaTyperBetAi\\SSI\\memory\\agents"
        
    def initialize(self, agent_count: int = 6) -> bool:
        """Inicjalizacja wszystkich agentow."""
        try:
            self.logger.info("Initializing Agent Manager...")
            
            # Tworzenie konfiguracji dla wszystkich agentow
            agent_configs = create_all_agent_configs(self._memory_base_path)
            
            # Tworzenie agentow
            for agent_id, config in agent_configs.items():
                agent = create_agent(config)
                self.agents[agent_id] = agent
                self.logger.info(f"Created Agent_{agent_id}: {config.name}")
                
            self._initialized = True
            self.logger.info(f"Agent Manager initialized with {len(self.agents)} agents")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing agents: {e}")
            return False
            
    def create_agent(self, config: AgentConfig) -> AgentRuntime:
        """Tworzenie pojedynczego agenta."""
        try:
            agent = create_agent(config)
            self.agents[config.agent_id] = agent
            self.logger.info(f"Created Agent_{config.agent_id}: {config.name}")
            return agent
            
        except Exception as e:
            self.logger.error(f"Error creating agent: {e}")
            raise
            
    def get_agent(self, agent_id: str) -> Optional[AgentRuntime]:
        """Pobranie agenta po ID."""
        return self.agents.get(agent_id)
        
    def get_all_agents(self) -> Dict[str, AgentRuntime]:
        """Pobranie wszystkich agentow."""
        return self.agents
        
    def get_active_agents(self) -> List[AgentRuntime]:
        """Pobranie aktywnych agentow."""
        return [agent for agent in self.agents.values() if agent.is_active()]
        
    def start_all(self) -> bool:
        """Uruchomienie wszystkich agentow."""
        try:
            self._running = True
            
            for agent_id, agent in self.agents.items():
                try:
                    # Wczytaj pamiec agenta
                    agent.load_memory()
                    agent.set_status(AgentStatus.READY)
                    self.logger.info(f"Agent_{agent_id} started and ready")
                    
                except Exception as e:
                    self.logger.error(f"Error starting Agent_{agent_id}: {e}")
                    agent.set_status(AgentStatus.ERROR)
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting all agents: {e}")
            return False
            
    def stop_all(self) -> bool:
        """Zatrzymanie wszystkich agentow."""
        try:
            self._running = False
            
            for agent_id, agent in self.agents.items():
                try:
                    agent.shutdown()
                    self.logger.info(f"Agent_{agent_id} stopped")
                    
                except Exception as e:
                    self.logger.error(f"Error stopping Agent_{agent_id}: {e}")
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping all agents: {e}")
            return False
            
    def shutdown(self) -> bool:
        """Wylaczenie managera i wszystkich agentow."""
        try:
            self.logger.info("Shutting down Agent Manager...")
            
            # Zatrzymanie wszystkich agentow
            self.stop_all()
            
            self._initialized = False
            self._running = False
            
            self.logger.info("Agent Manager and all agents shut down")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            return False
            
    def run_all_cycles(self, collector_data: Dict[str, Any], 
                      world_context: Dict[str, Any], 
                      cycle_count: int) -> Dict[str, Any]:
        """Wykonywanie cykli dla wszystkich agentow.
        
        Ta metoda byla uzywana w starym modelu (pojedyncze wykonanie).
        W nowym modelu kazdy agent jest wykonywany indywidualnie.
        """
        results = {}
        
        try:
            for agent_id, agent in self.agents.items():
                try:
                    result = agent.run_cycle(collector_data, world_context, cycle_count)
                    results[agent_id] = result
                    
                except Exception as e:
                    self.logger.error(f"Error running Agent_{agent_id} cycle: {e}")
                    results[agent_id] = {"error": str(e), "success": False}
                    
            return results
            
        except Exception as e:
            self.logger.error(f"Error in run_all_cycles: {e}")
            return {"error": str(e), "success": False}
            
    def get_status(self) -> Dict[str, Any]:
        """Pobranie statusu wszystkich agentow."""
        status = {
            "manager": {
                "initialized": self._initialized,
                "running": self._running,
                "total_agents": len(self.agents),
                "active_agents": len(self.get_active_agents())
            },
            "agents": {}
        }
        
        for agent_id, agent in self.agents.items():
            status["agents"][agent_id] = {
                "name": agent.name,
                "type": agent.type.value if hasattr(agent.type, 'value') else str(agent.type),
                "status": agent.get_status().value if hasattr(agent.get_status(), 'value') else str(agent.get_status()),
                "active": agent.is_active()
            }
            
        return status
        
    def print_status(self) -> None:
        """Wyswietlenie statusu agentow."""
        status = self.get_status()
        
        print("Agents:")
        for agent_id, agent_info in status["agents"].items():
            active_str = "active" if agent_info["active"] else "inactive"
            print(f"  [OK] {agent_id}: {active_str}")
            
    def save_all_memory(self) -> bool:
        """Zapis pamieci wszystkich agentow."""
        try:
            success_count = 0
            error_count = 0
            
            for agent_id, agent in self.agents.items():
                try:
                    if agent.save_memory():
                        success_count += 1
                    else:
                        error_count += 1
                        
                except Exception as e:
                    self.logger.error(f"Error saving Agent_{agent_id} memory: {e}")
                    error_count += 1
                    
            self.logger.info(f"Saved memory: {success_count} success, {error_count} errors")
            return error_count == 0
            
        except Exception as e:
            self.logger.error(f"Error in save_all_memory: {e}")
            return False
            
    def load_all_memory(self) -> bool:
        """Zaladowanie pamieci wszystkich agentow."""
        try:
            success_count = 0
            error_count = 0
            
            for agent_id, agent in self.agents.items():
                try:
                    if agent.load_memory():
                        success_count += 1
                    else:
                        error_count += 1
                        
                except Exception as e:
                    self.logger.error(f"Error loading Agent_{agent_id} memory: {e}")
                    error_count += 1
                    
            self.logger.info(f"Loaded memory: {success_count} success, {error_count} errors")
            return error_count == 0
            
        except Exception as e:
            self.logger.error(f"Error in load_all_memory: {e}")
            return False


def create_agent_manager(runtime_config: Optional[AgentRuntimeConfig] = None) -> AgentManager:
    """Tworzenie managera agentow."""
    return AgentManager(runtime_config)


if __name__ == "__main__":
    import logging
    
    # Konfiguracja logowania
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Testing Agent Manager...")
    
    try:
        # Utworzenie managera
        manager = create_agent_manager()
        
        # Inicjalizacja
        if manager.initialize():
            print("✓ Agent Manager initialized")
        else:
            print("✗ Failed to initialize Agent Manager")
            sys.exit(1)
            
        # Uruchomienie agentow
        if manager.start_all():
            print("✓ All agents started")
        else:
            print("✗ Failed to start all agents")
            
        # Status
        status = manager.get_status()
        print(f"Total agents: {status['manager']['total_agents']}")
        print(f"Active agents: {status['manager']['active_agents']}")
        
        manager.print_status()
        
        # Test cykli
        test_data = {"v2": {"test": "data"}, "v3": {"test": "data"}}
        test_context = {"timestamp": datetime.now().isoformat(), "cycle_count": 1}
        
        results = manager.run_all_cycles(test_data, test_context, 1)
        
        for agent_id, result in results.items():
            if result.get("success"):
                print(f"✓ Agent_{agent_id}: {result.get('decision', {}).get('choice')}")
            else:
                print(f"✗ Agent_{agent_id}: Error - {result.get('error', 'Unknown')}")
                
        # Zapis pamieci
        if manager.save_all_memory():
            print("✓ All agent memory saved")
            
        # Zatrzymanie
        if manager.shutdown():
            print("✓ Agent Manager shut down")
        else:
            print("✗ Failed to shut down Agent Manager")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
    print("\nAgent Manager test completed!")