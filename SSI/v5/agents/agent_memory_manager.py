"""
SSI V5 - Agent Memory Manager
Zarzadzanie pamiecia agentow

Zgodnie z dokumentacja Sprint 11.5 v2.0:
- Memory Observation System
- Agent Runtime Foundation

Odpowiedzialnosc:
- Koordynacja pamieci miedzy agentami
- Synchronizacja pamieci
- Zarządzanie wspolnym kontekstem
- Integracja z Collectorami
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

# Dodanie sciezki do SSI do sys.path
SSI_PATH = "D:\\sts\\aplikacjaTyperBetAi\\SSI"
if SSI_PATH not in sys.path:
    sys.path.insert(0, SSI_PATH)

from .agents_config import AgentConfig
from .agent_memory_store import AgentMemoryStore, MemoryType, create_agent_memory_store
from .agent_runtime import AgentRuntime


class AgentMemoryManager:
    """Manager pamieci agentow.
    
    Odpowiedzialnosc:
    - Synchronizacja pamieci miedzy agentami
    - Wspolny kontekst wiedzy
    - Zarzadzanie*(Historyczna pamieci)System
    """
    
    def __init__(self, agents: Optional[Dict[str, AgentRuntime]] = None):
        """Inicjalizacja managera pamieci."""
        self.agents = agents or {}
        self._shared_memory: Dict[str, Any] = {}
        self._initialized = False
        
        # Logging
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Sciezki
        self._memory_base_path = "D:\\sts\\aplikacjaTyperBetAi\\SSI\\memory"
        self._shared_memory_path = os.path.join(self._memory_base_path, "shared")
        
    def initialize(self, agents: Optional[Dict[str, AgentRuntime]] = None) -> bool:
        """Inicjalizacja managera pamieci."""
        try:
            if agents:
                self.agents = agents
                
            # Utworzenie folderow
            os.makedirs(self._memory_base_path, exist_ok=True)
            os.makedirs(self._shared_memory_path, exist_ok=True)
            
            # Inicjalizacja pamieci wspolnej
            self._shared_memory = {
                "agents": {},
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            }
            
            self._initialized = True
            self.logger.info("Agent Memory Manager initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing memory manager: {e}")
            return False
            
    def sync_agent_memory(self, agent_id: str) -> bool:
        """Synchronizacja pamieci pojedynczego agenta z pamiecia wspolna."""
        try:
            if agent_id not in self.agents:
                return False
                
            agent = self.agents[agent_id]
            
            # Pobranie świeżych danych agenta
            if agent.memory_store:
                entries = agent.memory_store.get_all_entries()
                
                # Aktualizacja pamieci wspolnej
                self._shared_memory["agents"][agent_id] = {
                    "last_sync": datetime.now().isoformat(),
                    "memory_stats": agent.memory_store.get_statistics(),
                    "agent_type": agent.type.value if hasattr(agent.type, 'value') else str(agent.type),
                    "status": agent.get_status().value if hasattr(agent.get_status(), 'value') else str(agent.get_status())
                }
                
                # Zapis pamieci wspolnej
                self._save_shared_memory()
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error syncing Agent_{agent_id} memory: {e}")
            return False
            
    def sync_all_agents(self) -> bool:
        """Synchronizacja pamieci wszystkich agentow."""
        try:
            success_count = 0
            error_count = 0
            
            for agent_id, agent in self.agents.items():
                if self.sync_agent_memory(agent_id):
                    success_count += 1
                else:
                    error_count += 1
                    
            self.logger.info(f"Sync all agents: {success_count} success, {error_count} errors")
            return error_count == 0
            
        except Exception as e:
            self.logger.error(f"Error syncing all agents: {e}")
            return False
            
    def update_shared_knowledge(self, source: str, data: Any) -> bool:
        """Aktualizacja wspolnej wiedzy z nowych danych."""
        try:
            if not self._shared_memory:
                self._shared_memory = {}
                
            if "knowledge" not in self._shared_memory:
                self._shared_memory["knowledge"] = {}
                
            self._shared_memory["knowledge"][source] = {
                "data": data,
                "timestamp": datetime.now().isoformat(),
                "source": source
            }
            
            self._save_shared_memory()
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating shared knowledge: {e}")
            return False
            
    def get_shared_knowledge(self, source: Optional[str] = None) -> Any:
        """Pobranie wspolnej wiedzy."""
        if not self._shared_memory:
            return {}
            
        if source:
            return self._shared_memory.get("knowledge", {}).get(source)
        else:
            return self._shared_memory.get("knowledge", {})
            
    def update_agent_experience(self, agent_id: str, experience: Any) -> bool:
        """Aktualizacja doświadczenia agenta w pamieci wspolnej."""
        try:
            if agent_id not in self._shared_memory["agents"]:
                self._shared_memory["agents"][agent_id] = {}
                
            if "experience" not in self._shared_memory["agents"][agent_id]:
                self._shared_memory["agents"][agent_id]["experience"] = []
                
            self._shared_memory["agents"][agent_id]["experience"].append(experience)
            self._shared_memory["agents"][agent_id]["last_update"] = datetime.now().isoformat()
            
            self._save_shared_memory()
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating agent experience: {e}")
            return False
            
    def _save_shared_memory(self) -> bool:
        """Zapis pamieci wspolnej do pliku."""
        try:
            filepath = os.path.join(self._shared_memory_path, "shared_memory.json")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self._shared_memory, f, indent=4, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving shared memory: {e}")
            return False
            
    def load_shared_memory(self) -> bool:
        """Zaladowanie pamieci wspolnej z pliku."""
        try:
            filepath = os.path.join(self._shared_memory_path, "shared_memory.json")
            
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    self._shared_memory = json.load(f)
                    
                return True
            else:
                # Utworz pusta pamiec
                self._shared_memory = {
                    "agents": {},
                    "timestamp": datetime.now().isoformat(),
                    "version": "1.0.0"
                }
                return True
                
        except Exception as e:
            self.logger.error(f"Error loading shared memory: {e}")
            return False
            
    def get_agent_memory_stats(self) -> Dict[str, Any]:
        """Pobranie statystyk pamieci wszystkich agentow."""
        stats = {}
        
        try:
            for agent_id, agent in self.agents.items():
                if agent.memory_store:
                    agent_stats = agent.memory_store.get_statistics()
                    stats[agent_id] = {
                        "personality": agent_stats[MemoryType.PERSONALITY]["count"],
                        "behavior": agent_stats[MemoryType.BEHAVIOR]["count"],
                        "strategy": agent_stats[MemoryType.STRATEGY]["count"],
                        "history": agent_stats[MemoryType.HISTORY]["count"],
                        "relationship": agent_stats[MemoryType.RELATIONSHIP]["count"],
                        "prompt": agent_stats[MemoryType.PROMPT]["count"]
                    }
                else:
                    stats[agent_id] = {"error": "no memory store"}
                    
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting memory stats: {e}")
            return {}
            
    def get_status(self) -> Dict[str, Any]:
        """Pobranie statusu managera pamieci."""
        return {
            "initialized": self._initialized,
            "memory_base_path": self._memory_base_path,
            "shared_memory_path": self._shared_memory_path,
            "agents_count": len(self.agents),
            "shared_memory_entries": len(self._shared_memory.get("agents", {}))
        }
        
    def shutdown(self) -> bool:
        """Wylaczenie managera pamieci."""
        try:
            # Zapis pamieci wspolnej
            self._save_shared_memory()
            
            self._initialized = False
            self.logger.info("Agent Memory Manager shut down")
            return True
            
        except Exception as e:
            self.logger.error(f"Error shutting down memory manager: {e}")
            return False


def create_agent_memory_manager(agents: Optional[Dict[str, AgentRuntime]] = None) -> AgentMemoryManager:
    """Tworzenie managera pamieci agentow."""
    return AgentMemoryManager(agents)


if __name__ == "__main__":
    import logging
    
    # Konfiguracja logowania
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Testing Agent Memory Manager...")
    
    try:
        # Utworzenie managera (pusty - test)
        manager = create_agent_memory_manager()
        
        # Inicjalizacja
        if manager.initialize():
            print("✓ Memory Manager initialized")
        else:
            print("✗ Failed to initialize Memory Manager")
            sys.exit(1)
            
        # Test pamieci wspolnej
        test_data = {"test": "value"}
        if manager.update_shared_knowledge("test_source", test_data):
            print("✓ Shared knowledge updated")
            
        knowledge = manager.get_shared_knowledge()
        print(f"✓ Shared knowledge loaded: {len(knowledge)} entries")
        
        # Zapis i odczyt
        if manager._save_shared_memory():
            print("✓ Shared memory saved")
            
        if manager.load_shared_memory():
            print("✓ Shared memory loaded")
            
        # Status
        status = manager.get_status()
        print(f"Status: {status}")
        
        # Zatrzymanie
        if manager.shutdown():
            print("✓ Memory Manager shut down")
        else:
            print("✗ Failed to shut down Memory Manager")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
    print("\nAgent Memory Manager test completed!")