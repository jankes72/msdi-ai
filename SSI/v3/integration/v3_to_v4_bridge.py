"""
SSI V3 to V4 Bridge - Most między systemami V3 i V4

Moduł odpowiedzialny za:
- Konwersję wiedzy z V3 do formatu zrozumiałego przez V4
- Transfer światów i pamięci z V3 do V4
- Synchronizację wiedzy między systemami
- Zarządzanie subskrypcjami agentów V4

Zgodnie z:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 3.3, 4.1
- 10_IMPLEMENTATION_MAP.md Etap 4A, Sprint 4

Architektura:
V3 (World Memory, Pattern Memory, Metadata) ←Bridge→ V4 (Agents, Decisions)

Wymagania:
- Bridge NIE zawiera logiki agentów (tylko transfer danych)
- Zachować luźne sprzężenie (V3 i V4 są niezależne)
- Obsługa wielu agentów V4

Wersja: 1.0 (Placeholder - do implementacji w Sprint 4)
Data: 2026-07-28
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum, auto
import uuid
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# KONFIGURACJA MOSTU V3-V4
# =============================================================================

@dataclass
class V3ToV4BridgeConfig:
    """
    Konfiguracja mostu V3-V4.
    
    Odpowiedzialność:
    - Ustawienia transferu wiedzy
    - Filtrowanie danych
    - Obsługa subskrypcji agentów
    """
    
    # Ustawienia transferu
    AUTO_SEND: bool = False  # Automatyczne wysyłanie zmian do V4
    BATCH_SIZE: int = 50     # Liczba zmian w partii
    
    # Ustawienia filtrów
    MIN_CONFIDENCE: float = 0.0  # Minimalny poziom pewności do transferu
    FILTER_WORLD_TYPES: List[str] = field(default_factory=list)  # Filtrowanie po typach światów
    
    # Ustawienia subskrypcji
    MAX_AGENTS: int = 100     # Maksymalna liczba subskrybowanych agentów
    
    # Ustawienia logowania
    LOG_LEVEL: str = "INFO"  # Poziom logowania
    TRACK_STATISTICS: bool = True  # Śledzenie statystyk transferu
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje konfigurację do dict"""
        return {
            "AUTO_SEND": self.AUTO_SEND,
            "BATCH_SIZE": self.BATCH_SIZE,
            "MIN_CONFIDENCE": self.MIN_CONFIDENCE,
            "FILTER_WORLD_TYPES": self.FILTER_WORLD_TYPES,
            "MAX_AGENTS": self.MAX_AGENTS,
            "LOG_LEVEL": self.LOG_LEVEL,
            "TRACK_STATISTICS": self.TRACK_STATISTICS
        }


# =============================================================================
# STRUKTURA DANYCH DLA TRANSFERU V3 → V4
# =============================================================================

@dataclass
class AgentKnowledgePackage:
    """
    Pakiet wiedzy do transferu z V3 do V4.
    
    Zawiera:
    - Światy z V3 (z pamięcią i metadanymi)
    - Wzorce zachowań
    - Relacje między obiektami
    - Metryki i oceny pewności
    """
    
    # Identyfikatory
    package_id: str = field(default_factory=lambda: f"pkg_{uuid.uuid4().hex[:12]}")
    agent_id: Optional[str] = None  # Docelowy agent (opcjonalnie)
    
    # Dane
    worlds: List[Dict[str, Any]] = field(default_factory=list)
    patterns: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metryki
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Metadane transferu
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "V3_To_V4_Bridge"
    format: str = "full"
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje pakiet do dict"""
        return {
            "package_id": self.package_id,
            "agent_id": self.agent_id,
            "worlds": self.worlds,
            "patterns": self.patterns,
            "metadata": self.metadata,
            "relationships": self.relationships,
            "confidence_scores": self.confidence_scores,
            "quality_metrics": self.quality_metrics,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "format": self.format
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentKnowledgePackage":
        """Tworzy pakiet z dict"""
        return cls(
            package_id=data.get("package_id", f"pkg_{uuid.uuid4().hex[:12]}"),
            agent_id=data.get("agent_id"),
            worlds=data.get("worlds", []),
            patterns=data.get("patterns", []),
            metadata=data.get("metadata", {}),
            relationships=data.get("relationships", []),
            confidence_scores=data.get("confidence_scores", {}),
            quality_metrics=data.get("quality_metrics", {}),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            source=data.get("source", "V3_To_V4_Bridge"),
            format=data.get("format", "full")
        )


# =============================================================================
# STATUS MOSTU
# =============================================================================

class BridgeStatus(Enum):
    """Status mostu V3-V4"""
    IDLE = auto()           # Bezczynny
    CONNECTING = auto()     # Łączenie z V3/V4
    READY = auto()          # Gotowy do transferu
    TRANSFERRING = auto()   # W trakcie transferu
    ERROR = auto()          # Błąd
    DISCONNECTED = auto()   # Rołączony


# =============================================================================
# PLACEHOLDER - GŁÓWNA KLASA MOSTU (Do zaimplementowania w Sprint 4)
# =============================================================================

class V3ToV4Bridge:
    """
    Most łączący system V3 (World Knowledge Engine) z V4 (Autonomous Agent Ecosystem).
    
    Odpowiedzialność:
    - Transfer wiedzy z V3 do V4
    - Konwersja formatów danych
    - Zarządzanie subskrypcjami agentów
    - Monitoring transferu
    
    ZASADA: Bridge NIE zawiera logiki agentów - tylko transfer danych.
    
    Sposób użycia:
        bridge = V3ToV4Bridge(v3_memory_manager, v4_agent_manager)
        bridge.connect()
        bridge.transfer_knowledge()
    """
    
    def __init__(
        self,
        config: Optional[V3ToV4BridgeConfig] = None
    ):
        """
        Inicjalizacja mostu V3-V4.
        
        Args:
            config: Konfiguracja mostu (opcjonalnie)
        """
        self.config = config or V3ToV4BridgeConfig()
        self._status = BridgeStatus.IDLE
        self._logger = self._setup_logger()
        
        # Rejestry
        self.subscribed_agents: List[str] = []  # Lista agentów subskrybujących
        self.transfer_history: List[Dict[str, Any]] = []  # Historia transferów
        
        self._logger.info(f"V3ToV4Bridge zainicjowany z konfiguracją: {self.config.to_dict()}")
    
    def _setup_logger(self) -> logging.Logger:
        """Konfiguruje logger"""
        logger = logging.getLogger(f"{__name__}.V3ToV4Bridge")
        logger.setLevel(getattr(logging, self.config.LOG_LEVEL, logging.INFO))
        return logger
    
    def connect(self) -> bool:
        """
        Łączy most z systemami V3 i V4.
        
        Returns:
            True jeśli połączenie udane
        """
        self._status = BridgeStatus.CONNECTING
        self._logger.info("Próba połączenia z V3 i V4...")
        
        # TODO: Implementacja w Sprint 4
        # 1. Połączenie z V3 Memory Manager
        # 2. Połączenie z V4 Agent Manager
        # 3. Rejestracja callbacków
        
        self._status = BridgeStatus.READY
        self._logger.info("Połączenie ustalone - most gotowy")
        return True
    
    def disconnect(self) -> None:
        """Rozłącza most"""
        self._status = BridgeStatus.DISCONNECTED
        self._logger.info("Most rozłączony")
    
    def subscribe_agent(self, agent_id: str) -> bool:
        """
        Subskrybuje agenta do odbioru wiedzy.
        
        Args:
            agent_id: ID agenta V4
            
        Returns:
            True jeśli subskrypcja udana
        """
        if len(self.subscribed_agents) >= self.config.MAX_AGENTS:
            self._logger.warning(f"Osiągnięto limit agentów ({self.config.MAX_AGENTS})")
            return False
        
        if agent_id not in self.subscribed_agents:
            self.subscribed_agents.append(agent_id)
            self._logger.info(f"Zasubskrybowano agenta: {agent_id}")
            return True
        
        return False
    
    def unsubscribe_agent(self, agent_id: str) -> bool:
        """
        Wypisuje agenta z subskrypcji.
        
        Args:
            agent_id: ID agenta V4
            
        Returns:
            True jeśli wypisanie udane
        """
        if agent_id in self.subscribed_agents:
            self.subscribed_agents.remove(agent_id)
            self._logger.info(f"Wypisano agenta: {agent_id}")
            return True
        return False
    
    def transfer_knowledge(
        self,
        knowledge_package: Optional[AgentKnowledgePackage] = None
    ) -> Dict[str, Any]:
        """
        Transferuje wiedzę z V3 do V4.
        
        Args:
            knowledge_package: Pakiet wiedzy (opcjonalnie - jeśli None, pobiera z V3)
            
        Returns:
            Statystyki transferu
        """
        self._status = BridgeStatus.TRANSFERRING
        
        # TODO: Implementacja w Sprint 4
        # 1. Pobierz dane z V3 Memory Manager
        # 2. Skonwertuj do formatu V4
        # 3. Wyślij do zasubskrybowanych agentów
        # 4. Zarejestruj transfer w historii
        
        stats = {
            "status": "placeholder",
            "message": "Transfer wiedzy V3→V4 - do implementacji w Sprint 4",
            "agents_notified": len(self.subscribed_agents)
        }
        
        self._status = BridgeStatus.READY
        return stats
    
    def get_status(self) -> BridgeStatus:
        """Zwraca aktualny status mostu"""
        return self._status
    
    def get_statistics(self) -> Dict[str, Any]:
        """Zwraca statystyki mostu"""
        return {
            "status": self._status.name,
            "subscribed_agents": len(self.subscribed_agents),
            "transfer_history_count": len(self.transfer_history),
            "config": self.config.to_dict()
        }


# =============================================================================
# FABRYKA (Placeholder)
# =============================================================================

def tworz_v3_to_v4_bridge(
    config: Optional[Union[Dict[str, Any], V3ToV4BridgeConfig]] = None
) -> V3ToV4Bridge:
    """
    Fabryka tworzącą most V3-V4.
    
    Args:
        config: Konfiguracja (opcjonalnie)
        
    Returns:
        V3ToV4Bridge
    """
    if isinstance(config, dict):
        config_obj = V3ToV4BridgeConfig(**config)
    elif isinstance(config, V3ToV4BridgeConfig):
        config_obj = config
    else:
        config_obj = V3ToV4BridgeConfig()
    
    return V3ToV4Bridge(config_obj)


# =============================================================================
# TESTY (Placeholder)
# =============================================================================

if __name__ == "__main__":
    print("Testing V3ToV4Bridge placeholder...")
    
    # Test konfiguracji
    config = V3ToV4BridgeConfig(AUTO_SEND=True, BATCH_SIZE=25)
    print(f"Konfiguracja: {config.to_dict()}")
    
    # Test mostu
    bridge = tworz_v3_to_v4_bridge(config)
    print(f"Status: {bridge.get_status().name}")
    
    # Test subskrypcji
    bridge.subscribe_agent("agent_001")
    bridge.subscribe_agent("agent_002")
    print(f"Subskrybowani agenci: {bridge.subscribed_agents}")
    
    # Test transferu (placeholder)
    result = bridge.transfer_knowledge()
    print(f" Transfer result: {result}")
    
    # Test statystyk
    stats = bridge.get_statistics()
    print(f"Statystyki: {stats}")
    
    print("\nV3ToV4Bridge placeholder - gotowy do implementacji w Sprint 4")
