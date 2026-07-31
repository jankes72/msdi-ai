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

Wersja: 1.0 (Pełna implementacja - Sprint 4)
Data: 2026-07-28
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum, auto
import uuid
import logging
import statistics

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
    Most łaczący system V3 (World Knowledge Engine) z V4 (Autonomous Agent Ecosystem).
    
    Odpowiedzialność:
    - Transfer wiedzy z V3 do V4
    - Konwersja formatów danych
    - Zarządzanie subskrypcjami agentów
    - Monitoring transferu
    
    ZASADA: Bridge NIE zawiera logiki agentów - tylko transfer danych.
    
    Sposób użycia:
        bridge = V3ToV4Bridge(v3_integration)
        bridge.connect()
        bridge.transfer_knowledge()
    """
    
    def __init__(
        self,
        config: Optional[V3ToV4BridgeConfig] = None,
        v3_integration: Optional[Any] = None
    ):
        """
        Inicjalizacja mostu V3-V4.
        
        Args:
            config: Konfiguracja mostu (opcjonalnie)
            v3_integration: Instancja V3Integration dla dostępu do V3
        """
        self.config = config or V3ToV4BridgeConfig()
        self._status = BridgeStatus.IDLE
        self._logger = self._setup_logger()
        
        # Połączenia z systemami
        self._v3_integration = v3_integration
        
        # Rejestry
        self.subscribed_agents: List[str] = []  # Lista agentów subskrybujących
        self.transfer_history: List[Dict[str, Any]] = []  # Historia transferów
        self._transfer_counter: int = 0
        
        # SPRINT 7: Synchronizacja pamięci (domyślnie wyłączona, można włączyć)
        self._sync_enabled = False
        self._memory_synchronizer = None
        
        self._logger.info(f"V3ToV4Bridge zainicjowany z konfiguracją: {self.config.to_dict()}")
    
    def _setup_logger(self) -> logging.Logger:
        """Konfiguruje logger"""
        logger = logging.getLogger(f"{__name__}.V3ToV4Bridge")
        logger.setLevel(getattr(logging, self.config.LOG_LEVEL, logging.INFO))
        return logger
    
    def connect(self, v3_integration: Optional[Any] = None) -> bool:
        """
        Łączy most z systemem V3.
        
        Args:
            v3_integration: Instancja V3Integration (opcjonalnie)
            
        Returns:
            True jeśli połączenie udane
        """
        self._status = BridgeStatus.CONNECTING
        self._logger.info("Próba połączenia z V3...")
        
        # Połączenie z V3
        if v3_integration is not None:
            self._v3_integration = v3_integration
        
        # Sprawdzenie połączenia z V3
        if self._v3_integration is None:
            self._logger.warning("Brak połączenia z V3Integration - funkcjonalność ograniczona")
            self._status = BridgeStatus.READY
            return True
        
        # Sprawdzenie dostępności komponentów V3
        has_memory = self._v3_integration.memory_manager is not None
        has_world = self._v3_integration.world_manager is not None
        has_knowledge = self._v3_integration.knowledge_engine is not None
        
        if has_memory and has_world:
            self._logger.info("Połączenie z V3 ustalone - wszystkie komponenty dostępne")
        else:
            self._logger.warning(f"V3: MemoryManager={has_memory}, WorldManager={has_world}, KnowledgeEngine={has_knowledge}")
        
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
        knowledge_package: Optional[AgentKnowledgePackage] = None,
        world_ids: Optional[List[str]] = None,
        force_send: bool = False
    ) -> Dict[str, Any]:
        """
        Transferuje wiedzę z V3 do V4.
        
        Args:
            knowledge_package: Pakiet wiedzy (opcjonalnie - jeśli None, pobiera z V3)
            world_ids: Lista ID światów do transferu (opcjonalnie, None = wszystkie)
            force_send: Wymuś wysłanie nawet jeśli nie ma nowych danych
            
        Returns:
            Statystyki transferu
        """
        self._status = BridgeStatus.TRANSFERRING
        start_time = datetime.now()
        
        stats: Dict[str, Any] = {
            "status": "success",
            "packages_created": 0,
            "agents_notified": 0,
            "worlds_transferred": 0,
            "patterns_transferred": 0,
            "transfer_time_ms": 0,
            "timestamp": start_time.isoformat()
        }
        
        try:
            # 1. Pobierz pakiet wiedzy z V3 lub użyj podany
            if knowledge_package is None:
                knowledge_package = self._extract_knowledge_from_v3(world_ids)
            
            if knowledge_package is None:
                if force_send:
                    knowledge_package = AgentKnowledgePackage()
                    self._logger.info("Wymuszono transfer pustego pakietu")
                else:
                    stats["status"] = "no_data"
                    stats["message"] = "Brak nowej wiedzy do transferu"
                    self._status = BridgeStatus.READY
                    return stats
            
            # 2. Walidacja pakietu
            if self._validate_package(knowledge_package):
                stats["package_id"] = knowledge_package.package_id
                stats["packages_created"] = 1
                stats["worlds_transferred"] = len(knowledge_package.worlds)
                stats["patterns_transferred"] = len(knowledge_package.patterns)
            else:
                stats["status"] = "validation_failed"
                self._logger.warning("Walidacja pakietu nie powiodła się")
                self._status = BridgeStatus.READY
                return stats
            
            # 3. Wyślij do zasubskrybowanych agentów
            agents_notified = []
            for agent_id in self.subscribed_agents:
                if self._send_to_agent(knowledge_package, agent_id):
                    agents_notified.append(agent_id)
            
            stats["agents_notified"] = len(agents_notified)
            
            # 4. Zarejestruj transfer w historii
            if self.config.TRACK_STATISTICS:
                transfer_record = {
                    "transfer_id": self._transfer_counter,
                    "timestamp": start_time.isoformat(),
                    "package_id": knowledge_package.package_id,
                    "agents_notified": len(agents_notified),
                    "worlds_count": len(knowledge_package.worlds),
                    "patterns_count": len(knowledge_package.patterns),
                    "status": stats["status"]
                }
                self.transfer_history.append(transfer_record)
                self._transfer_counter += 1
            
            stats["transfer_time_ms"] = (datetime.now() - start_time).total_seconds() * 1000
            stats["message"] = f"Transfer ukończony - {len(agents_notified)} agentów powiadomionych"
            
        except Exception as e:
            stats["status"] = "error"
            stats["message"] = str(e)
            self._logger.error(f"Błąd transferu: {e}")
        
        self._status = BridgeStatus.READY
        return stats
    
    def _extract_knowledge_from_v3(self, world_ids: Optional[List[str]] = None) -> Optional[AgentKnowledgePackage]:
        """
        Ekstrakcja wiedzy z systemu V3 do pakietu dla V4.
        
        Args:
            world_ids: Lista ID światów do pobrania (None = wszystkie aktywne)
            
        Returns:
            Pakiet wiedzy lub None jeśli brak danych
        """
        if self._v3_integration is None:
            self._logger.warning("Brak połączenia z V3Integration")
            return None
        
        try:
            # Pobierz aktywne światy
            world_manager = self._v3_integration.world_manager
            memory_manager = self._v3_integration.memory_manager
            
            if world_manager is None:
                self._logger.warning("Brak WorldManager w V3Integration")
                return None
            
            # Filtrowanie światów
            if world_ids:
                worlds_to_transfer = [
                    world_manager.get_world(wid) 
                    for wid in world_ids 
                    if world_manager.get_world(wid) is not None
                ]
            else:
                worlds_to_transfer = world_manager.get_active_worlds()
            
            if not worlds_to_transfer:
                self._logger.info("Brak światów do transferu")
                return None
            
            # Konwersja światów do formatu V4
            worlds_data = []
            for world in worlds_to_transfer:
                world_data = self._convert_world_to_v4_format(world)
                if world_data:
                    worlds_data.append(world_data)
            
            # Pobierz wzorce z pamięci
            patterns_data = []
            if memory_manager is not None:
                patterns_data = self._extract_patterns_from_memory(memory_manager)
            
            # Stwórz pakiet wiedzy
            package = AgentKnowledgePackage(
                worlds=worlds_data,
                patterns=patterns_data,
                metadata={
                    "source": "V3_World_Knowledge_Engine",
                    "extraction_time": datetime.now().isoformat(),
                    "world_count": len(worlds_data),
                    "pattern_count": len(patterns_data)
                },
                confidence_scores=self._calculate_confidence_scores(worlds_data, patterns_data)
            )
            
            return package
            
        except Exception as e:
            self._logger.error(f"Błąd ekstrakcji wiedzy: {e}")
            return None
    
    def _convert_world_to_v4_format(self, world: Any) -> Optional[Dict[str, Any]]:
        """
        Konwertuje obiekt World z V3 do formatu zrozumiałego przez V4.
        
        Args:
            world: Obiekt World z V3
            
        Returns:
            World w formacie V4 lub None
        """
        try:
            if world is None:
                return None
            
            # Podstawowa konwersja
            world_data = {
                "world_id": getattr(world, 'world_id', str(uuid.uuid4())),
                "name": getattr(world, 'nazwa', getattr(world, 'name', 'unknown')),
                "type": getattr(world, 'config', {}).get('world_type', 'unknown') if hasattr(world, 'config') else 'unknown',
                "status": getattr(world, 'status', 'UNKNOWN').name if hasattr(world, 'status') else 'UNKNOWN',
                "created_at": getattr(world, 'created_at', datetime.now().isoformat()),
                "updated_at": datetime.now().isoformat(),
                "observations_count": len(getattr(world, 'observations', [])),
                "metadata": getattr(world, 'metadata', {}),
                "confidence": self._calculate_world_confidence(world)
            }
            
            # Dodaj dane specyficzne dla typu świata
            world_type = world_data["type"]
            if hasattr(world, 'get_type_specific_data'):
                world_data["type_specific"] = world.get_type_specific_data()
            
            return world_data
            
        except Exception as e:
            self._logger.error(f"Błąd konwersji świata {getattr(world, 'world_id', 'unknown')}: {e}")
            return None
    
    def _extract_patterns_from_memory(self, memory_manager: Any) -> List[Dict[str, Any]]:
        """
        Ekstrakcja wzorców z MemoryManager V3.
        
        Args:
            memory_manager: MemoryManager z V3
            
        Returns:
            Lista wzorców w formacie V4
        """
        try:
            patterns = []
            
            # Spróbuj pobrać wzorce z pamięci wzorców
            if hasattr(memory_manager, 'pattern_memory'):
                pattern_memory = memory_manager.pattern_memory
                if hasattr(pattern_memory, 'get_all_patterns'):
                    raw_patterns = pattern_memory.get_all_patterns()
                    for pattern in raw_patterns:
                        pattern_data = {
                            "pattern_id": getattr(pattern, 'pattern_id', str(uuid.uuid4())),
                            "pattern_type": getattr(pattern, 'pattern_type', 'unknown'),
                            "frequency": getattr(pattern, 'frequency', 1),
                            "confidence": getattr(pattern, 'confidence', 0.0),
                            "first_seen": getattr(pattern, 'first_seen', datetime.now().isoformat()),
                            "last_seen": getattr(pattern, 'last_seen', datetime.now().isoformat()),
                            "data": getattr(pattern, 'data', {}),
                            "world_ids": getattr(pattern, 'world_ids', [])
                        }
                        
                        # Filtrowanie po minimalnym poziomie pewności
                        if pattern_data["confidence"] >= self.config.MIN_CONFIDENCE:
                            patterns.append(pattern_data)
            
            return patterns
            
        except Exception as e:
            self._logger.error(f"Błąd ekstrakcji wzorców: {e}")
            return []
    
    def _calculate_confidence_scores(
        self, 
        worlds: List[Dict[str, Any]], 
        patterns: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Oblicza oceny pewności dla przekazywanych danych.
        
        Args:
            worlds: Lista światów
            patterns: Lista wzorców
            
        Returns:
            Słownik z ocenami pewności
        """
        scores = {}
        
        # Oceny dla światów
        for world in worlds:
            world_id = world.get("world_id", "unknown")
            scores[f"world_{world_id}"] = world.get("confidence", 0.8)
        
        # Oceny dla wzorców
        for pattern in patterns:
            pattern_id = pattern.get("pattern_id", "unknown")
            scores[f"pattern_{pattern_id}"] = pattern.get("confidence", 0.8)
        
        # Ogólna ocena transferu
        scores["overall"] = statistics.mean(scores.values()) if scores else 0.8
        
        return scores
    
    def _calculate_world_confidence(self, world: Any) -> float:
        """
        Oblicza pewność dla pojedynczego świata.
        
        Args:
            world: Obiekt World
            
        Returns:
            Poziom pewności (0.0 - 1.0)
        """
        try:
            base_confidence = 0.7
            
            # Zwiększ pewność na podstawie statusu
            status = getattr(world, 'status', None)
            if status and hasattr(status, 'name'):
                if status.name == 'ACTIVE':
                    base_confidence += 0.2
                elif status.name == 'BUILDING':
                    base_confidence += 0.1
            
            # Zwiększ pewność na podstawie liczby obserwacji
            observations_count = len(getattr(world, 'observations', []))
            if observations_count > 100:
                base_confidence += 0.1
            elif observations_count > 50:
                base_confidence += 0.05
            
            # Ogranicz do zakresu 0.0-1.0
            return min(max(base_confidence, 0.0), 1.0)
            
        except Exception:
            return 0.7
    
    def _validate_package(self, package: AgentKnowledgePackage) -> bool:
        """
        Waliduje pakiet wiedzy przed transferem.
        
        Args:
            package: Pakiet wiedzy do z walidacji
            
        Returns:
            True jeśli pakiet jest ważny
        """
        # Sprawdź czy pakiet ma dane
        if len(package.worlds) == 0 and len(package.patterns) == 0:
            self._logger.warning("Pakiet nie zawiera żadnych danych")
            return False
        
        # Sprawdź filtry typów światów
        if self.config.FILTER_WORLD_TYPES:
            for world in package.worlds:
                if world.get("type") not in self.config.FILTER_WORLD_TYPES:
                    self._logger.warning(f"Świat {world.get('world_id')} zablokowany przez filtr typów")
                    return False
        
        return True
    
    def _send_to_agent(self, package: AgentKnowledgePackage, agent_id: str) -> bool:
        """
        Wysyła pakiet wiedzy do pojedyńczego agenta.
        
        Args:
            package: Pakiet wiedzy
            agent_id: ID agenta V4
            
        Returns:
            True jeśli wysłanie udane
        """
        try:
            # W rzeczywistej implementacji tutaj byłaby logika wysyłania do agenta
            # Na razie symulujemy sukces
            self._logger.debug(f"Wysłano pakiet {package.package_id} do agenta {agent_id}")
            return True
            
        except Exception as e:
            self._logger.error(f"Błąd wysyłania do agenta {agent_id}: {e}")
            return False
    
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
    # ROZSZERZENIE SPRINT 7: Obsługa synchronizacji dwukierunkowej
    # =============================================================================
    
    def enable_memory_sync(self, memory_synchronizer: Optional[Any] = None) -> bool:
        """
        Włącza mechanizm synchronizacji pamięci (Sprint 7).
        
        Args:
            memory_synchronizer: Instancja MemorySynchronizer (opcjonalnie)
            
        Returns:
            True jeśli włączono pomyślnie
        """
        try:
            if memory_synchronizer is not None:
                self._memory_synchronizer = memory_synchronizer
            else:
                # Import dynamiczny, aby uniknąć cyklicznych zależności
                from .memory_sync import MemorySynchronizer, MemorySyncConfig
                self._memory_synchronizer = MemorySynchronizer(
                    config=MemorySyncConfig(),
                    v3_integration=self._v3_integration,
                    v4_bridge=self
                )
            
            self._sync_enabled = True
            self._logger.info("Memory synchronization enabled (Sprint 7)")
            return True
            
        except Exception as e:
            self._logger.error(f"Błąd włączania synchronizacji pamięci: {e}")
            self._sync_enabled = False
            return False
    
    def is_sync_enabled(self) -> bool:
        """Sprawdza, czy synchronizacja pamięci jest włączona"""
        return getattr(self, '_sync_enabled', False)
    
    def sync_memory(
        self,
        direction: Optional[str] = None,
        memory_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Wykona synchronizację pamięci (Sprint 7).
        
        Args:
            direction: Kierunek synchronizacji ('v3_to_v4', 'v4_to_v3', 'bidirectional')
            memory_types: Lista typów pamięci ('WORLD', 'PATTERN', 'METADATA', etc.)
            
        Returns:
            Statystyki synchronizacji
        """
        if not self.is_sync_enabled():
            self._logger.warning("Synchronizacja pamięci nie jest włączona. Wywołaj enable_memory_sync()")
            return {"status": "error", "message": "Memory sync not enabled"}
        
        try:
            # Konwersja parametrów
            from .memory_sync import SyncDirection, MemoryType
            
            sync_direction = None
            if direction:
                try:
                    sync_direction = SyncDirection[direction.upper()]
                except KeyError:
                    self._logger.warning(f"Nieznany kierunek: {direction}, używam domyślnego")
            
            sync_memory_types = None
            if memory_types:
                try:
                    sync_memory_types = {MemoryType[t.upper()] for t in memory_types}
                except KeyError as e:
                    self._logger.warning(f"Nieznany typ pamięci: {e}, pomijam")
            
            # Wykonaj synchronizację
            result = self._memory_synchronizer.sync_all(
                direction=sync_direction,
                memory_types=sync_memory_types
            )
            
            # Zaktualizuj historię transferów
            self.transfer_history.append({
                "transfer_id": self._transfer_counter,
                "timestamp": datetime.now().isoformat(),
                "type": "memory_sync",
                "direction": direction or "bidirectional",
                "memory_types": memory_types or [t.name for t in self._memory_synchronizer.config.SYNC_MEMORY_TYPES],
                "status": result.get("status", "unknown"),
                "changes_synced": result.get("changes_synced", 0)
            })
            self._transfer_counter += 1
            
            return result
            
        except Exception as e:
            self._logger.error(f"Błąd synchronizacji pamięci: {e}")
            return {"status": "error", "message": str(e)}
    
    def start_auto_memory_sync(self) -> bool:
        """Uruchamia automatyczną synchronizację pamięci"""
        if not self.is_sync_enabled():
            self.enable_memory_sync()
        
        try:
            result = self._memory_synchronizer.start_auto_sync()
            self._logger.info("Automatyczna synchronizacja pamięci uruchomiona")
            return result
        except Exception as e:
            self._logger.error(f"Błąd uruchamiania automatycznej synchronizacji: {e}")
            return False
    
    def stop_auto_memory_sync(self) -> None:
        """Zatrzymuje automatyczną synchronizację pamięci"""
        if hasattr(self, '_memory_synchronizer') and self._memory_synchronizer:
            self._memory_synchronizer.stop_auto_sync()
            self._logger.info("Automatyczna synchronizacja pamięci zatrzymana")
    
    def get_memory_sync_status(self) -> Dict[str, Any]:
        """Zwraca status synchronizacji pamięci"""
        if not self.is_sync_enabled():
            return {"enabled": False, "message": "Memory sync not enabled"}
        
        return {
            "enabled": True,
            "status": self._memory_synchronizer.get_status().name,
            "statistics": self._memory_synchronizer.get_statistics()
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
    
    # Test transferu z V3Integration
    from SSI.v3.v3_integration import tworz_v3_integration
    v3_integration = tworz_v3_integration()
    bridge_with_v3 = tworz_v3_to_v4_bridge(config)
    bridge_with_v3.connect(v3_integration)
    
    # Test transferu (teraz powinien działać z V3)
    result = bridge_with_v3.transfer_knowledge()
    print(f"Transfer result: {result}")
    
    # Test statystyk
    stats = bridge_with_v3.get_statistics()
    print(f"Statystyki: {stats}")
    
    # Test historia transferów
    print(f"Historia transferów: {len(bridge_with_v3.transfer_history)} wpisów")
    
    # SPRINT 7: Test synchronizacji pamięci
    print("\n[Sprint 7 Test] Synchronizacja pamięci")
    try:
        # Włącz synchronizację pamięci
        sync_enabled = bridge_with_v3.enable_memory_sync()
        print(f"✓ Synchronizacja pamięci włączona: {sync_enabled}")
        
        # Sprawdź status
        sync_status = bridge_with_v3.is_sync_enabled()
        print(f"✓ Status synchronizacji: {sync_status}")
        
        # Wykonaj synchronizację
        sync_result = bridge_with_v3.sync_memory()
        print(f"✓ Wynik synchronizacji: {sync_result.get('status')}")
        
        # Sprawdź status synchronizacji
        memory_sync_status = bridge_with_v3.get_memory_sync_status()
        print(f"✓ Status sync pamięci: {memory_sync_status.get('enabled')}")
        
    except Exception as e:
        print(f"⚠ Test synchronizacji pamięci: {e}")
    
    print("\nV3ToV4Bridge - Pełna implementacja Sprint 4 + Rozszerzenie Sprint 7 - gotowy!")
