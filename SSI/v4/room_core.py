"""
SSI V4 Room Core - Pokój Narodzin Agentów

Moduł odpowiedzialny za pokój narodzin i zarządzanie populacją agentów.

Odpowiedzialność:
- Zarządzanie pokojem narodzin (ROOM_CORE)
- Rejestracja i organizacja agentów
- Środowisko do pierwszych interakcji
- Współpraca z AgentBirthSystem

Zgodnie z:
- 05_AGENT_SYSTEM.md Sekcja 2.2 (ROOM_CORE), 2.3 (Pierwsza Populacja)
- 10_IMPLEMENTATION_MAP.md Etap 4A (Agent Foundation)

Architektura:
┌─────────────────────────────────────────────────────────────┐
│                      ROOM CORE                                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    ROOM CORE                              │ │
│  │  ┌─────────────────┐  ┌─────────────────────────────┐    │ │
│  │  │  RoomConfig     │  │  RoomType, RoomStatus       │    │ │
│  │  └─────────────────┘  └─────────────────────────────┘    │ │
│  │                                                         │ │
│  │  ┌─────────────────────────────────────────────────┐   │ │
│  │  │                AGENCI w POKOJU                     │   │ │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐           │   │ │
│  │  │  │ Agent 1 │ │ Agent 2 │ │ Agent 3 │           │   │ │
│  │  │  │ (Analityk│ │(Strateg │ │(Eksperym│           │   │ │
│  │  │  └──────────┘ └──────────┘ └──────────┘           │   │ │
│  │  └─────────────────────────────────────────────────┘   │ │
│  │                                                         │ │
│  │  Proces w ROOM_CORE:                                   │ │
│  │  1. Agent zostaje utworzony                          │ │
│  │  2. Otrzymuje osobowość startową                    │ │
│  │  3. Przedstawia swoje parametry                      │ │
│  │  4. Poznaje inne jednostki                          │ │
│  │  5. Rozpoczyna wymianę informacji                    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Zależności:
- Zależy od: agent_core.py (klasa Agent)
- Wspiera: AgentBirthSystem (dodawanie nowych agentów)
- Integracja z: V3 (dostęp do światów i pamięci)

Wersja: 1.0
Data: 2026-07-28
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from enum import Enum, auto
import uuid
import threading
import logging

from .agent_core import Agent, AgentConfig, AgentType, AgentStatus

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMY - Typ i Status Pokoju
# ============================================================================

class RoomType(Enum):
    """
    Typy pokoi w systemie V4.
    
    Zgodnie z 05_AGENT_SYSTEM.md Sekcja 2.2 (ROOM_CORE)
    """
    BIRTH_ROOM = auto()           # Pokój narodzin (ROOM_CORE)
    MEETING_ROOM = auto()         # Pokój spotkań agentów
    DECISION_ROOM = auto()        # Pokój decyzyjny
    REST_ROOM = auto()            # Pokój odpoczynku
    ARCHIVE_ROOM = auto()         # Pokój archiwalny


class RoomStatus(Enum):
    """
    Statusy pokoju.
    """
    EMPTY = auto()                # Pusty
    ACTIVE = auto()                # Aktywny (są agenci)
    FULL = auto()                 # Pełny
    LOCKED = auto()                # Zablokowany
    MAINTENANCE = auto()          # W konserwacji


# ============================================================================
# KONFIGURACJA POKOJU
# ============================================================================

@dataclass
class RoomConfig:
    """
    Konfiguracja pokoju agentów.
    
    Attributes:
        room_id: Unikalne ID pokoju
        room_type: Typ pokoju
        name: Nazwa pokoju
        max_agents: Maksymalna liczba agentów w pokoju
        allow_new_agents: Czy zezwalać na nowych agentów
        shared_memory: Czy agenci dzielą pamięć
    """
    room_id: str = "ROOM_CORE"
    room_type: RoomType = RoomType.BIRTH_ROOM
    name: str = "Pokój Narodzin"
    max_agents: int = 1000
    allow_new_agents: bool = True
    shared_memory: bool = False
    description: str = "Główny pokój narodzin agentów"
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            "room_id": self.room_id,
            "room_type": self.room_type.name,
            "name": self.name,
            "max_agents": self.max_agents,
            "allow_new_agents": self.allow_new_agents,
            "shared_memory": self.shared_memory,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RoomConfig':
        """Tworzenie z słownika"""
        data = data.copy()
        if "room_type" in data and isinstance(data["room_type"], str):
            try:
                data["room_type"] = RoomType[data["room_type"]]
            except KeyError:
                data["room_type"] = RoomType.BIRTH_ROOM
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# ============================================================================
# GŁÓWNA KLASA ROOM CORE
# ============================================================================

class RoomCore:
    """
    Główny pokój narodzin agentów (ROOM_CORE).
    
    Odpowiedzialność:
    - Zarządzanie agentami w pokoju
    - Rejestracja nowych agentów
    - Śledzenie stanu agentów
    - Umożliwianie interakcji między agentami
    - Monitorowanie aktywności
    
    Zgodnie z 05_AGENT_SYSTEM.md Sekcja 2.2 (ROOM_CORE)
    
    Attributes:
        config: Konfiguracja pokoju
        agents: Słownik agentów w pokoju
        status: Aktualny status pokoju
    """
    
    def __init__(self, config: Optional[RoomConfig] = None):
        """
        Inicjalizacja pokoju narodzin.
        
        Args:
            config: Konfiguracja pokoju (opcjonalnie)
        """
        self.config = config or RoomConfig()
        self.agents: Dict[str, Agent] = {}
        self._lock = threading.Lock()
        
        self.status = RoomStatus.EMPTY
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Statystyki
        self.statistics: Dict[str, Any] = {
            "total_agents_ever": 0,
            "current_agents": 0,
            "by_type": {},
            "by_status": {},
            "total_interactions": 0
        }
        
        logger.info(f"Zainicjowano RoomCore: {self.config.room_id}")
    
    def add_agent(self, agent: Agent, force: bool = False) -> bool:
        """
        Dodaje agenta do pokoju.
        
        Zgodnie z 05_AGENT_SYSTEM.md Sekcja 2.2 (Proces w ROOM_core)
        
        Args:
            agent: Agent do dodania
            force: Czy Miejscowo zablokowanie max_agents
            
        Returns:
            True jeśli agent został dodany
        """
        with self._lock:
            # Sprawdź limit
            if not force and len(self.agents) >= self.config.max_agents:
                logger.warning(f"RoomCore: Pokój {self.config.room_id} jest pełny")
                return False
            
            # Sprawdź, czy agent już jest w pokoju
            if agent.agent_id in self.agents:
                logger.warning(f"RoomCore: Agent {agent.agent_id} już jest w pokoju")
                return False
            
            # Sprawdź, czy pokój akceptuje nowych agentów
            if not self.config.allow_new_agents:
                logger.warning(f"RoomCore: Pokój {self.config.room_id} nie akceptuje nowych agentów")
                return False
            
            # Dodaj agenta
            self.agents[agent.agent_id] = agent
            
            # Aktualizuj agenta (ustaw room_id)
            agent.room_id = self.config.room_id
            
            # Aktualizuj status pokoju
            self._update_room_status()
            
            # Aktualizuj statystyki
            self.statistics["total_agents_ever"] += 1
            self.statistics["current_agents"] = len(self.agents)
            
            agent_type = agent.agent_type.value
            if agent_type not in self.statistics["by_type"]:
                self.statistics["by_type"][agent_type] = 0
            self.statistics["by_type"][agent_type] += 1
            
            agent_status = agent.status.name
            if agent_status not in self.statistics["by_status"]:
                self.statistics["by_status"][agent_status] = 0
            self.statistics["by_status"][agent_status] += 1
            
            self.updated_at = datetime.now()
            
            logger.info(f"RoomCore: Dodano agenta {agent.agent_id} do pokoju {self.config.room_id}")
            
            # Agent przedstawia się (symulacja)
            self._agent_introduction(agent)
            
            return True
    
    def remove_agent(self, agent_id: str, archive: bool = False) -> bool:
        """
        Usuwa agenta z pokoju.
        
        Args:
            agent_id: ID agenta do usunięcia
            archive: Czy archiwizować zamiast usuwać
            
        Returns:
            True jeśli agent został usunięty
        """
        with self._lock:
            if agent_id not in self.agents:
                return False
            
            agent = self.agents[agent_id]
            
            if archive:
                agent.set_status(AgentStatus.ARCHIVED)
                logger.info(f"RoomCore: Zarchiwizowano agenta {agent_id}")
            else:
                del self.agents[agent_id]
                self.statistics["current_agents"] = len(self.agents)
                logger.info(f"RoomCore: Usunięto agenta {agent_id}")
            
            self._update_room_status()
            self.updated_at = datetime.now()
            
            return True
    
    def _agent_introduction(self, agent: Agent) -> None:
        """
        Symuluje przedstawienie się agenta w pokoju.
        
        Zgodnie z 05_AGENT_SYSTEM.md Sekcja 2.2 (Dane Przekazywané przez Agentów)
        """
        # Agent przedstawia swoje parametry innym agentom w pokoju
        introduction_data = {
            "agent_id": agent.agent_id,
            "agent_type": agent.agent_type.value,
            "personality": agent.personality.to_dict(),
            "message": f"Cześć, jestem {agent.agent_id}, {self._get_agent_description(agent)}"
        }
        
        # Roześlij informację do innych agentów (symulacja)
        for other_agent in self.agents.values():
            if other_agent.agent_id != agent.agent_id:
                # Inni agenci dowiadują się o nowym agencie
                other_agent.memory.private_notebook[f"intro_{agent.agent_id}"] = introduction_data
                self.statistics["total_interactions"] += 1
        
        logger.debug(f"RoomCore: {agent.agent_id} przedstawił się w pokoju {self.config.room_id}")
    
    def _get_agent_description(self, agent: Agent) -> str:
        """Generuje opis agenta na podstawie jego cech"""
        desc_parts = []
        
        if agent.agent_type == AgentType.ANALYST:
            desc_parts.append("Analityk - szukam stabilnych wzorców")
        elif agent.agent_type == AgentType.VALUE_STRATEGIST:
            desc_parts.append("Strateg Wartości - maksymalizuję wartosć oczekiwaną")
        elif agent.agent_type == AgentType.EXPERIMENTATOR:
            desc_parts.append("Eksperymentator - testuję nowe rozwiązania")
        else:
            desc_parts.append(f"{agent.agent_type.value} - autonomiczny agent decyzyjny")
        
        # Dodaj informacje o preferencjach
        if agent.personality.risk_acceptance > 0.7:
            desc_parts.append("akceptuje wysokie ryzyko")
        elif agent.personality.risk_acceptance < 0.3:
            desc_parts.append("preferuje bezpieczeństwo")
        
        if agent.personality.curiosity > 0.7:
            desc_parts.append("ciekawski i kreatywny")
        
        return "; ".join(desc_parts)
    
    def _update_room_status(self) -> None:
        """Aktualizuje status pokoju na podstawie liczby agentów"""
        agent_count = len(self.agents)
        
        if agent_count == 0:
            self.status = RoomStatus.EMPTY
        elif agent_count >= self.config.max_agents:
            self.status = RoomStatus.FULL
        else:
            self.status = RoomStatus.ACTIVE
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Pobiera agenta z pokoju po ID"""
        return self.agents.get(agent_id)
    
    def get_agents_by_type(self, agent_type: AgentType) -> List[Agent]:
        """Pobiera agentów danego typu"""
        return [agent for agent in self.agents.values() if agent.agent_type == agent_type]
    
    def find_agents(self, **criteria) -> List[Agent]:
        """Znajduje agentów według kryteriów"""
        results = []
        for agent in self.agents.values():
            match = True
            for key, value in criteria.items():
                if key == "agent_type":
                    if agent.agent_type.value != value:
                        match = False
                        break
                elif key == "status":
                    if agent.status.name != value:
                        match = False
                        break
                elif hasattr(agent, key):
                    if getattr(agent, key) != value:
                        match = False
                        break
            if match:
                results.append(agent)
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Pobiera statystyki pokoju"""
        return {
            **self.statistics,
            "room_id": self.config.room_id,
            "room_type": self.config.room_type.name,
            "status": self.status.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def get_room_report(self) -> str:
        """Generuje raport pokoju"""
        stats = self.get_statistics()
        
        report = [
            "=" * 60,
            f"RAPORT POKOJU - {self.config.name}",
            "=" * 60,
            f"ID Pokoju: {self.config.room_id}",
            f"Typ: {self.config.room_type.name}",
            f"Status: {self.status.name}",
            f"Liczba agentów: {stats['current_agents']}/{self.config.max_agents}",
            f"Całkowita liczba agentów: {stats['total_agents_ever']}",
            f"Interakcje: {stats['total_interactions']}",
            "",
            "Agenci przez typ:",
        ]
        
        for agent_type, count in stats.get("by_type", {}).items():
            report.append(f"  - {agent_type}: {count}")
        
        report.extend([
            "",
            "Agenci przez status:",
        ])
        
        for status, count in stats.get("by_status", {}).items():
            report.append(f"  - {status}: {count}")
        
        # Lista agentów
        if self.agents:
            report.extend([
                "",
                "Lista agentów:",
            ])
            for agent in self.agents.values():
                report.append(f"  - {agent.agent_id} ({agent.agent_type.value}, status: {agent.status.name})")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def enable_new_agents(self, enable: bool = True) -> None:
        """Zezwala lub blokuje dodawanie nowych agentów"""
        self.config.allow_new_agents = enable
        logger.info(f"RoomCore: Nowi agenci {'włączoni' if enable else 'wyłączoni'} w pokoju {self.config.room_id}")
    
    def set_max_agents(self, max_agents: int) -> None:
        """Ustawia maksymalną liczbę agentów w pokoju"""
        self.config.max_agents = max_agents
        self._update_room_status()
        logger.info(f"RoomCore: Nowy limit agentów: {max_agents} w pokoju {self.config.room_id}")
    
    def broadcast_message(self, sender_id: str, message: Dict[str, Any]) -> int:
        """
        Rozesyła wiadomość do wszystkich agentów w pokoju.
        
        Args:
            sender_id: ID nadawcy
            message: Wiadomość do przekazania
            
        Returns:
            Liczba agentów, którzy odebrali wiadomość
        """
        with self._lock:
            received_count = 0
            for agent in self.agents.values():
                if agent.agent_id != sender_id:
                    # Symulacja odbioru wiadomości
                    if "messages" not in agent.memory.private_notebook:
                        agent.memory.private_notebook["messages"] = []
                    agent.memory.private_notebook["messages"].append({
                        "sender": sender_id,
                        "message": message,
                        "timestamp": datetime.now().isoformat()
                    })
                    received_count += 1
                    self.statistics["total_interactions"] += 1
            
            logger.info(f"RoomCore: Wiadomość od {sender_id} odebrana przez {received_count} agentów")
            return received_count
    
    def clear(self) -> None:
        """Czyści pokój (UWAGA: usuwa všechny agenty!)"""
        with self._lock:
            self.agents.clear()
            self.statistics["current_agents"] = 0
            self._update_room_status()
            logger.warning(f"RoomCore: Wyczyszczono pokój {self.config.room_id}")


# ============================================================================
# FABRYKA
# ============================================================================

def tworz_room_core(config: Optional[RoomConfig] = None) -> RoomCore:
    """
    Fabryka tworzących RoomCore.
    
    Args:
        config: Konfiguracja pokoju (opcjonalnie)
        
    Returns:
        RoomCore
        
    Example:
        >>> room = tworz_room_core()
        >>> room.add_agent(agent)
        >>> print(room.get_room_report())
    """
    return RoomCore(config)


# ============================================================================
# SINGLETON
# ============================================================================

_room_core: Optional[RoomCore] = None
_room_core_lock = threading.Lock()


def get_room_core() -> RoomCore:
    """
    Zwraca globalny pokój narodzin (Singleton ROOM_CORE).
    
    Zgodnie z PROJECT_RULES.md Sekcja 4 (Singleton dla Managerów)
    i 05_AGENT_SYSTEM.md Sekcja 2.2 (ROOM_CORE)
    """
    global _room_core
    with _room_core_lock:
        if _room_core is None:
            _room_core = RoomCore(RoomConfig(
                room_id="ROOM_CORE",
                room_type=RoomType.BIRTH_ROOM,
                name="Pokój Narodzin",
                description="Główny pokój narodzin agentów V4"
            ))
        return _room_core


def reset_room_core() -> None:
    """Resetuje globalny pokój narodzin (ostrzegać!)"""
    global _room_core
    with _room_core_lock:
        if _room_core is not None:
            _room_core.clear()
            _room_core = None


# ============================================================================
# TESTY
# ============================================================================

if __name__ == "__main__":
    print("Testing SSI V4 Room Core...")
    print("=" * 60)
    
    # Test 1: Tworzenie pokoju
    print("\n[Test 1] Tworzenie RoomCore...")
    room = tworz_room_core()
    print(f"  Pokój utworzony: {room.config.room_id}")
    print(f"  Typ: {room.config.room_type.name}")
    print(f"  Status: {room.status.name}")
    
    # Test 2: Tworzenie agentów i dodawanie do pokoju
    print("\n[Test 2] Dodawanie agentów do pokoju...")
    from .agent_core import tworz_agent, AgentType
    
    agents = []
    for i, agent_type in enumerate([AgentType.ANALYST, AgentType.VALUE_STRATEGIST, AgentType.EXPERIMENTATOR]):
        agent = tworz_agent(agent_type, agent_id=f"agent_test_{i+1}")
        agent.initialize()
        success = room.add_agent(agent)
        agents.append(agent)
        print(f"  {'✓' if success else '✗'} {agent.agent_id} ({agent_type.value}) dodany do pokoju")
    
    # Test 3: Statystyki pokoju
    print("\n[Test 3] Statystyki pokoju...")
    stats = room.get_statistics()
    print(f"  Bieżąca liczba agentów: {stats['current_agents']}")
    print(f"  Całkowita liczba agentów: {stats['total_agents_ever']}")
    
    # Raport
    print("\n[Raport Pokoju]")
    print(room.get_room_report())
    
    # Test 4: Wyszukiwanie agentów
    print("\n[Test 4] Wyszukiwanie agentów...")
    analysts = room.get_agents_by_type(AgentType.ANALYST)
    print(f"  Znaleziono {len(analysts)} Analityków")
    
    # Test 5: Rozesłanie wiadomości
    print("\n[Test 5] Rozesłanie wiadomości...")
    if agents:
        count = room.broadcast_message(
            agents[0].agent_id,
            {"type": "greeting", "content": "Cześć wszystkim!", "sender": agents[0].agent_id}
        )
        print(f"  Wiadomość odebrana przez {count} agentów")
        
        # Sprawdź, czy inni agenci odebrali wiadomość
        if len(agents) > 1:
            messages = agents[1].memory.private_notebook.get("messages", [])
            print(f"  Agent {agents[1].agent_id} ma {len(messages)} wiadomości")
    
    # Test 6: Singleton
    print("\n[Test 6] Singleton RoomCore...")
    room2 = get_room_core()
    print(f"  Czy ten sam pokój? {room2.config.room_id == 'ROOM_CORE'}")
    
    # Test 7: Usuwanie agentów
    print("\n[Test 7] Usuwanie agentów...")
    if agents:
        success = room.remove_agent(agents[0].agent_id)
        print(f"  {'✓' if success else '✗'} Usunięto agenta {agents[0].agent_id}")
        print(f"  Nowa liczba agentów: {len(room.agents)}")
    
    print("\n" + "=" * 60)
    print("All Room Core tests passed!")
    print("=" * 60)
