"""
SSI V3 Integration - Główna klasa integracyjna V3

Moduł odpowiedzialny za:
- Główny punkt wejścia integracji V3
- Połączenie MemoryManager, WorldManager i WorldKnowledgeEngine
- Koordynację wszystkich komponentów V3
- Integrację z V2 i V4

Zgodnie z:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 3 (V3 World System)
- 10_IMPLEMENTATION_MAP.md Etap 3C (World Integration)
- SPRINTY.md Sprint 3 (V3Integration)
- PROJECT_RULES.md (Zasady tworzenia modułów)

Architektura:
┌─────────────────────────────────────────────────────────────┐
│                    V3Integration                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ MemoryManager   │  │ WorldManager   │  │ WorldKnowledge │  │
│  │ (Pamięć V3)    │  │ (Światy V3)    │  │ Engine         │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │
│           │                  │                   │            │
│           └──────────────────┼───────────────────┘            │
│                          ↓  │                                   │
│               ┌─────────────────────────┐                      │
│               │   Integracyjne API      │                      │
│               │   - receive_from_v2()    │                      │
│               │   - process_data()      │                      │
│               │   - send_to_v4()        │                      │
│               │   - get_knowledge()     │                      │
│               └─────────────────────────┘                      │
└─────────────────────────────────────────────────────────────┘

Wymagania:
- Zachować architekturę warstwową (PROJECT_RULES.md)
- Połączyć istniejące komponenty (nie przebudowywać)
- Obsługiwać V3Config
- Być głównym punktem dostępu do V3

Wersja: 1.0
Data: 2026-07-28
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum, auto
import uuid
import logging
import threading
from collections import defaultdict

# Importy z V3
from .memory.memory_manager import MemoryManager, MemoryConfig
from .worlds.world_manager import WorldManager, tworz_world_manager
from .worlds.world import WorldConfig
from .worlds.world_knowledge_engine import WorldKnowledgeEngine, WorldKnowledgeConfig
from .config import V3Config, IntegrationConfig, get_v3_config

logger = logging.getLogger(__name__)


# =============================================================================
# STATUS INTEGRACJI
# =============================================================================

class IntegrationStatus(Enum):
    """
    Status integracji V3.
    
    Zgodnie z 10_IMPLEMENTATION_MAP.md
    """
    IDLE = auto()           # Bezczynny
    INITIALIZING = auto()   # Inicjalizacja komponentów
    READY = auto()          # Gotowy do pracy
    PROCESSING = auto()     # W trakcie przetwarzania
    ERROR = auto()          # Błąd
    SHUTTING_DOWN = auto()  # Wyłączanie
    DISCONNECTED = auto()   # Rołączony


class ComponentStatus(Enum):
    """Status poszczególnych komponentów"""
    NOT_INITIALIZED = auto()
    INITIALIZED = auto()
    CONNECTED = auto()
    ACTIVE = auto()
    ERROR = auto()
    DISABLED = auto()


# =============================================================================
# KONFIGURACJA INTEGRACJI
# =============================================================================

@dataclass
class V3IntegrationConfig:
    """
    Konfiguracja głównej integracji V3.
    
    Odpowiedzialność:
    - Ustawienia połączeń między komponentami
    - Konfiguracja automatycznej integracji
    - Zarządzanie zależnościami
    """
    
    # Ustawienia komponentów
    INIT_MEMORY_MANAGER: bool = True
    INIT_WORLD_MANAGER: bool = True
    INIT_KNOWLEDGE_ENGINE: bool = True
    
    # Ustawienia automatycznej integracji
    AUTO_CONNECT: bool = True
    AUTO_PROCESS: bool = True
    
    # Ustawienia logowania
    LOG_LEVEL: str = "INFO"
    TRACK_OPERATIONS: bool = True
    
    # Ustawienia Bezpieczeństwa
    MAX_CONCURRENT_OPERATIONS: int = 10
    OPERATION_TIMEOUT: float = 60.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje do dict"""
        return {
            "INIT_MEMORY_MANAGER": self.INIT_MEMORY_MANAGER,
            "INIT_WORLD_MANAGER": self.INIT_WORLD_MANAGER,
            "INIT_KNOWLEDGE_ENGINE": self.INIT_KNOWLEDGE_ENGINE,
            "AUTO_CONNECT": self.AUTO_CONNECT,
            "AUTO_PROCESS": self.AUTO_PROCESS,
            "LOG_LEVEL": self.LOG_LEVEL,
            "TRACK_OPERATIONS": self.TRACK_OPERATIONS,
            "MAX_CONCURRENT_OPERATIONS": self.MAX_CONCURRENT_OPERATIONS,
            "OPERATION_TIMEOUT": self.OPERATION_TIMEOUT
        }


# =============================================================================
# STATYSTYKI INTEGRACJI
# =============================================================================

@dataclass
class IntegrationStatistics:
    """Statystyki integracji V3"""
    
    # Liczniki operacji
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    
    # Liczniki danych
    total_data_received: int = 0
    total_worlds_created: int = 0
    total_patterns_detected: int = 0
    total_memory_entries: int = 0
    
    # Czas operacji
    total_processing_time: float = 0.0
    average_processing_time: float = 0.0
    last_operation_time: float = 0.0
    
    # Statusy komponentów
    component_statuses: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje do dict"""
        return {
            "total_operations": self.total_operations,
            "successful_operations": self.successful_operations,
            "failed_operations": self.failed_operations,
            "total_data_received": self.total_data_received,
            "total_worlds_created": self.total_worlds_created,
            "total_patterns_detected": self.total_patterns_detected,
            "total_memory_entries": self.total_memory_entries,
            "total_processing_time": self.total_processing_time,
            "average_processing_time": self.average_processing_time,
            "last_operation_time": self.last_operation_time,
            "component_statuses": self.component_statuses
        }


# =============================================================================
# GŁÓWNA KLASA INTEGRACJI V3
# =============================================================================

class V3Integration:
    """
    Główna klasa integracyjna systemu V3 World Knowledge Engine.
    
    Odpowiedzialność:
    - Główny punkt wejścia do systemu V3
    - Koordynacja wszystkich komponentów V3
    - Połączenie z V2 (przez V2ToV3Bridge)
    - Połączenie z V4 (przez V3ToV4Bridge)
    - Zarządzanie przepływem danych między warstwami
    
    Zgodnie z:
    - 01_SYSTEM_ARCHITECTURE.md Sekcja 3.3
    - 10_IMPLEMENTATION_MAP.md Etap 3C
    - SPRINTY.md Sprint 3
    
    Sposób użycia:
        # Inicjalizacja z domyślną konfiguracją
        v3_integration = V3Integration()
        
        # Inicjalizacja z customową konfiguracją
        config = V3Config()
        v3_integration = V3Integration(config)
        
        # Połączenie z V2
        v3_integration.connect_to_v2(v2_bridge)
        
        # Lokalizacja z V4
        v3_integration.connect_to_v4(v3_to_v4_bridge)
        
        # Przetwarzanie danych z V2
        v3_integration.process_from_v2(data_package)
        
        # Pobieranie wiedzy dla V4
        knowledge = v3_integration.get_knowledge_for_v4()
    """
    
    def __init__(
        self,
        config: Optional[Union[V3Config, Dict[str, Any]]] = None,
        integration_config: Optional[V3IntegrationConfig] = None,
        memory_manager: Optional[MemoryManager] = None,
        world_manager: Optional[WorldManager] = None,
        knowledge_engine: Optional[WorldKnowledgeEngine] = None
    ):
        """
        Inicjalizacja głównej integracji V3.
        
        Args:
            config: Główna konfiguracja V3 (V3Config lub dict)
            integration_config: Konfiguracja integracyjna (opcjonalnie)
            memory_manager: Zewnętrzny MemoryManager (opcjonalnie)
            world_manager: Zewnętrzny WorldManager (opcjonalnie)
            knowledge_engine: Zewnętrzny WorldKnowledgeEngine (opcjonalnie)
        """
        # Konfiguracja
        self.v3_config = self._load_config(config)
        self.integration_config = integration_config or V3IntegrationConfig()
        
        # Komponenty V3
        self._memory_manager: Optional[MemoryManager] = memory_manager
        self._world_manager: Optional[WorldManager] = world_manager
        self._knowledge_engine: Optional[WorldKnowledgeEngine] = knowledge_engine
        
        # Status
        self._status = IntegrationStatus.IDLE
        self._component_statuses: Dict[str, ComponentStatus] = {}
        
        # Statystyki
        self._statistics = IntegrationStatistics()
        
        # Locki dla bezpieczeństwa wielowątkowego
        self._lock = threading.RLock()
        
        # Logger
        self._logger = self._setup_logger()
        
        # Inicjalizacja komponentów
        self._initialize_components()
        
        self._logger.info(f"V3Integration zainicjowany ze statusem: {self._status.name}")
    
    def _setup_logger(self) -> logging.Logger:
        """Konfiguruje logger"""
        logger = logging.getLogger(f"{__name__}.V3Integration")
        logger.setLevel(getattr(logging, self.integration_config.LOG_LEVEL, logging.INFO))
        return logger
    
    def _load_config(self, config: Optional[Union[V3Config, Dict[str, Any]]]) -> V3Config:
        """Ładowanie konfiguracji"""
        if isinstance(config, V3Config):
            return config
        elif isinstance(config, dict):
            return V3Config.from_dict(config)
        else:
            return get_v3_config()
    
    def _initialize_components(self) -> None:
        """
        Inicjalizuje komponenty V3 zgodnie z konfiguracją.
        
        Colejność inicjalizacji:
        1. MemoryManager (pamięć)
        2. WorldManager (światy)
        3. WorldKnowledgeEngine (wiedza)
        """
        self._status = IntegrationStatus.INITIALIZING
        
        try:
            # Inicjalizacja MemoryManager
            if self.integration_config.INIT_MEMORY_MANAGER and self._memory_manager is None:
                self._logger.info("Inicjalizacja MemoryManager...")
                self._memory_manager = MemoryManager(self.v3_config.memory)
                self._component_statuses["memory_manager"] = ComponentStatus.INITIALIZED
                self._logger.info("MemoryManager gotowy")
            elif self._memory_manager is not None:
                self._component_statuses["memory_manager"] = ComponentStatus.INITIALIZED
                self._logger.info("MemoryManager podany z zewnątrz")
            
            # Inicjalizacja WorldManager
            if self.integration_config.INIT_WORLD_MANAGER and self._world_manager is None:
                self._logger.info("Inicjalizacja WorldManager...")
                try:
                    self._world_manager = tworz_world_manager(self.v3_config.world)
                    self._component_statuses["world_manager"] = ComponentStatus.INITIALIZED
                    self._logger.info("WorldManager zainicjowany automatycznie")
                except Exception as e:
                    self._logger.error(f"Błąd inicjalizacji WorldManager: {e}")
                    self._component_statuses["world_manager"] = ComponentStatus.ERROR
            elif self._world_manager is not None:
                self._component_statuses["world_manager"] = ComponentStatus.INITIALIZED
                self._logger.info("WorldManager podany z zewnątrz")
            
            # Inicjalizacja WorldKnowledgeEngine - Wymaga WorldManager
            if self._world_manager is not None and self.integration_config.INIT_KNOWLEDGE_ENGINE and self._knowledge_engine is None:
                self._logger.info("Inicjalizacja WorldKnowledgeEngine...")
                self._knowledge_engine = WorldKnowledgeEngine(
                    self.v3_config.world,
                    self._memory_manager,
                    self._world_manager
                )
                self._component_statuses["knowledge_engine"] = ComponentStatus.INITIALIZED
                self._logger.info("WorldKnowledgeEngine gotowy")
            elif self._knowledge_engine is not None:
                self._component_statuses["knowledge_engine"] = ComponentStatus.INITIALIZED
                self._logger.info("WorldKnowledgeEngine podany z zewnątrz")
            else:
                self._logger.warning("WorldKnowledgeEngine nie został zainicjowany - brak WorldManager")
                self._component_statuses["knowledge_engine"] = ComponentStatus.NOT_INITIALIZED
            
            # Połączenie komponentów
            self._connect_components()
            
            # Ustaw status gotowości (tylko jeśli wszystkie kluczowe komponenty są gotowe)
            if self._memory_manager is not None:
                self._status = IntegrationStatus.READY
                self._logger.info("V3Integration gotowy do pracy (ograniczony tryb)")
            else:
                self._status = IntegrationStatus.ERROR
                self._logger.error("V3Integration nie gotowy - brak MemoryManager")
            
        except Exception as e:
            self._status = IntegrationStatus.ERROR
            self._logger.error(f"Błąd inicjalizacji: {e}")
            raise RuntimeError(f"Nie udało się zainicjować V3Integration: {e}") from e
    
    def _connect_components(self) -> None:
        """Łączy komponenty V3 ze sobą"""
        try:
            # Połączenie MemoryManager z WorldManager
            if self._memory_manager and self._world_manager:
                # MemoryManager i WorldManager mogą być powiązane
                pass
            
            # Połączenie KnowledgeEngine z MemoryManager i WorldManager
            if self._knowledge_engine and self._memory_manager:
                self._knowledge_engine.integrate_with_memory(self._memory_manager)
                self._component_statuses["knowledge_engine"] = ComponentStatus.CONNECTED
            
            if self._knowledge_engine and self._world_manager:
                # WorldKnowledgeEngine używa WorldManager poprzez konstruktor
                #Integracja jest już ustawiona w __init__ WorldKnowledgeEngine
                self._component_statuses["knowledge_engine"] = ComponentStatus.CONNECTED
            
            self._logger.info("Komponenty V3 połączone")
            
        except Exception as e:
            self._logger.error(f"Błąd łączenia komponentów: {e}")
    
    # =========================================================================
    # PROPERTY - Dostęp do komponentów
    # =========================================================================
    
    @property
    def memory_manager(self) -> Optional[MemoryManager]:
        """Zwraca MemoryManager"""
        return self._memory_manager
    
    @property
    def world_manager(self) -> Optional[WorldManager]:
        """Zwraca WorldManager"""
        return self._world_manager
    
    @property
    def knowledge_engine(self) -> Optional[WorldKnowledgeEngine]:
        """Zwraca WorldKnowledgeEngine"""
        return self._knowledge_engine
    
    @property
    def config(self) -> V3Config:
        """Zwraca konfigurację V3"""
        return self.v3_config
    
    # =========================================================================
    # GŁÓWNE METODY INTEGRACYJNE
    # =========================================================================
    
    def connect_to_v2(self, v2_bridge: Any) -> bool:
        """
        Łączy V3Integration z mostem V2 (V2ToV3Bridge).
        
        Args:
            v2_bridge: Instancja V2ToV3Bridge
            
        Returns:
            True jeśli połączenie udane
        """
        with self._lock:
            try:
                # Rejestracja callbacku w V2
                if hasattr(v2_bridge, 'set_v3_integration'):
                    v2_bridge.set_v3_integration(self)
                    self._component_statuses["v2_bridge"] = ComponentStatus.CONNECTED
                    self._logger.info("Połączono z V2ToV3Bridge")
                    return True
                else:
                    self._logger.warning("V2ToV3Bridge nie ma metody set_v3_integration")
                    return False
            except Exception as e:
                self._logger.error(f"Błąd połączenia z V2: {e}")
                return False
    
    def connect_to_v4(self, v3_to_v4_bridge: Any) -> bool:
        """
        Łączy V3Integration z mostem V4 (V3ToV4Bridge).
        
        Args:
            v3_to_v4_bridge: Instancja V3ToV4Bridge
            
        Returns:
            True jeśli połączenie udane
        """
        with self._lock:
            try:
                # Zapamiętanie mostu V3→V4
                self._v3_to_v4_bridge = v3_to_v4_bridge
                self._component_statuses["v4_bridge"] = ComponentStatus.CONNECTED
                self._logger.info("Połączono z V3ToV4Bridge")
                return True
            except Exception as e:
                self._logger.error(f"Błąd połączenia z V4: {e}")
                return False
    
    def receive_from_v2(self, data_package: Any, source: str = "V2") -> Dict[str, Any]:
        """
        Odbiera pakiet danych z V2 i przekazuje do przetwarzania.
        
        Args:
            data_package: Pakiet danych z V2 (WorldDataPackage lub dict)
            source: Źródło danych (domyślnie "V2")
            
        Returns:
            Statystyki przetwarzania
        """
        with self._lock:
            self._statistics.total_data_received += 1
            
            try:
                # Logowanie odbioru
                self._logger.info(f"Odebrano dane z {source}: {type(data_package).__name__}")
                
                # Przetwarzanie przez WorldKnowledgeEngine
                if self._knowledge_engine:
                    worlds = self._knowledge_engine.process_v2_predictions(
                        getattr(data_package, 'model_name', 'unknown'),
                        getattr(data_package, 'predictions', data_package)
                    )
                    
                    # Zapis do pamięci
                    if self._memory_manager and self.v3_config.integration.SAVE_TO_MEMORY:
                        for world in worlds:
                            self._memory_manager.add_world(world.to_dict())
                            self._statistics.total_worlds_created += 1
                    
                    # Wygenerowanie wzorców (opatcjonalnie)
                    if self._knowledge_engine:
                        patterns = self._knowledge_engine.detect_patterns()
                        self._statistics.total_patterns_detected += len(patterns)
                    
                    # Statystyki
                    self._statistics.total_operations += 1
                    self._statistics.successful_operations += 1
                    
                    return {
                        "status": "success",
                        "worlds_created": len(worlds),
                        "patterns_detected": len(patterns) if 'patterns' in locals() else 0,
                        "data_stored": True
                    }
                else:
                    self._logger.warning("WorldKnowledgeEngine nie jest dostępny")
                    return {"status": "error", "message": "WorldKnowledgeEngine not available"}
                    
            except Exception as e:
                self._statistics.total_operations += 1
                self._statistics.failed_operations += 1
                self._logger.error(f"Błąd przetwarzania danych z V2: {e}")
                return {"status": "error", "message": str(e)}
    
    def process_batch(self, data_batch: List[Any]) -> Dict[str, Any]:
        """
        Przetwarza partię danych.
        
        Args:
            data_batch: Lista pakietów danych
            
        Returns:
            Statystyki przetwarzania partii
        """
        batch_stats = {
            "total_received": len(data_batch),
            "processed": 0,
            "failed": 0,
            "worlds_created": 0,
            "patterns_detected": 0
        }
        
        for data in data_batch:
            result = self.receive_from_v2(data)
            if result.get("status") == "success":
                batch_stats["processed"] += 1
                batch_stats["worlds_created"] += result.get("worlds_created", 0)
                batch_stats["patterns_detected"] += result.get("patterns_detected", 0)
            else:
                batch_stats["failed"] += 1
        
        return batch_stats
    
    def get_knowledge_for_v4(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Pobiera wiedzę z V3 i przygotowuje ją dla V4.
        
        Args:
            agent_id: Opcjonalny ID agenta (do filtrowania)
            
        Returns:
            Pakiet wiedzy dla V4
        """
        knowledge_package = {
            "worlds": [],
            "patterns": [],
            "metadata": {},
            "statistics": {}
        }
        
        try:
            if self._world_manager:
                worlds = self._world_manager.list_worlds()
                knowledge_package["worlds"] = [w.to_dict() for w in worlds]
            
            if self._knowledge_engine:
                patterns = self._knowledge_engine.get_detected_patterns()
                knowledge_package["patterns"] = patterns
                
                metadata = self._knowledge_engine.get_metadata()
                knowledge_package["metadata"] = metadata
            
            if self._memory_manager:
                stats = self._memory_manager.get_statistics()
                knowledge_package["statistics"]["memory"] = stats
            
            knowledge_package["statistics"]["v3"] = self.get_statistics()
            
            self._logger.info(f"Przygotowano pakiet wiedzy dla V4 (agent: {agent_id})")
            
            return knowledge_package
            
        except Exception as e:
            self._logger.error(f"Błąd przygotowywania wiedzy dla V4: {e}")
            return {"error": str(e)}
    
    def send_to_v4(self, knowledge_package: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Wysyła wiedzę do V4 przez V3ToV4Bridge.
        
        Args:
            knowledge_package: Pakiet wiedzy (opcjonalnie - jeśli None, pobiera z V3)
            
        Returns:
            Statystyki wysyłki
        """
        if not hasattr(self, '_v3_to_v4_bridge') or self._v3_to_v4_bridge is None:
            self._logger.warning("Brak połączenia z V3ToV4Bridge")
            return {"status": "error", "message": "V3ToV4Bridge not connected"}
        
        try:
            # Pobierz lub użyj podany pakiet
            if knowledge_package is None:
                knowledge_package = self.get_knowledge_for_v4()
            
            # Wyślij przez most
            result = self._v3_to_v4_bridge.transfer_knowledge(knowledge_package)
            self._statistics.total_operations += 1
            self._statistics.successful_operations += 1
            
            self._logger.info("Wiedza wysłana do V4")
            return {"status": "success", **result}
            
        except Exception as e:
            self._statistics.total_operations += 1
            self._statistics.failed_operations += 1
            self._logger.error(f"Błąd wysyłania do V4: {e}")
            return {"status": "error", "message": str(e)}
    
    # =========================================================================
    # METODY POMOCNICZE
    # =========================================================================
    
    def get_status(self) -> IntegrationStatus:
        """Zwraca aktualny status integracji"""
        return self._status
    
    def get_component_status(self, component_name: str) -> Optional[ComponentStatus]:
        """Zwraca status konkretnego komponentu"""
        return self._component_statuses.get(component_name)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Zwraca statystyki integracji"""
        stats_dict = self._statistics.to_dict()
        stats_dict["current_status"] = self._status.name
        stats_dict["components"] = {k: v.name for k, v in self._component_statuses.items()}
        return stats_dict
    
    def is_ready(self) -> bool:
        """Sprawdza, czy integracja jest gotowa do pracy"""
        return self._status == IntegrationStatus.READY
    
    def reset_statistics(self) -> None:
        """Resetuje statystyki"""
        with self._lock:
            self._statistics = IntegrationStatistics()
            self._logger.info("Statystyki zresetowane")
    
    def shutdown(self) -> None:
        """Wyłącza integrację"""
        self._status = IntegrationStatus.SHUTTING_DOWN
        self._logger.info("Wyłączanie V3Integration...")
        
        # W przyszłości: cleanup komponentów
        # Na razie: ustaw status na DISCONNECTED
        self._status = IntegrationStatus.DISCONNECTED
        self._logger.info("V3Integration wyłączony")
    
    def __repr__(self) -> str:
        return f"V3Integration(status={self._status.name}, components={len(self._component_statuses)})"


# =============================================================================
# FABRYKA
# =============================================================================

def tworz_v3_integration(
    config: Optional[Union[V3Config, Dict[str, Any]]] = None,
    integration_config: Optional[V3IntegrationConfig] = None,
    memory_manager: Optional[MemoryManager] = None,
    world_manager: Optional[WorldManager] = None,
    knowledge_engine: Optional[WorldKnowledgeEngine] = None
) -> V3Integration:
    """
    Fabryka tworzącą główną integrację V3.
    
    Args:
        config: Główna konfiguracja V3
        integration_config: Konfiguracja integracyjna
        memory_manager: Zewnętrzny MemoryManager
        world_manager: Zewnętrzny WorldManager
        knowledge_engine: Zewnętrzny WorldKnowledgeEngine
        
    Returns:
        V3Integration
    """
    return V3Integration(
        config=config,
        integration_config=integration_config,
        memory_manager=memory_manager,
        world_manager=world_manager,
        knowledge_engine=knowledge_engine
    )


# =============================================================================
# SINGLETON - Domyślna instancja
# =============================================================================

_default_integration: Optional[V3Integration] = None


def get_v3_integration() -> V3Integration:
    """
    Zwraca domyślną instancję V3Integration (Singleton).
    
    Returns:
        V3Integration
    """
    global _default_integration
    if _default_integration is None:
        _default_integration = tworz_v3_integration()
    return _default_integration


def reset_v3_integration() -> None:
    """Resetuje domyślną instancję V3Integration"""
    global _default_integration
    if _default_integration is not None:
        _default_integration.shutdown()
    _default_integration = None


# =============================================================================
# TESTY
# =============================================================================

if __name__ == "__main__":
    print("Testing V3Integration...")
    
    # Test 1: Tworzenie domyślne
    try:
        integration = tworz_v3_integration()
        print(f"✓ Test 1: V3Integration utworzony")
        print(f"  Status: {integration.get_status().name}")
    except Exception as e:
        print(f"✗ Test 1 FAILED: {e}")
    
    # Test 2: Sprawdź dostęp do komponentów
    try:
        has_memory = integration.memory_manager is not None
        has_world = integration.world_manager is not None
        has_knowledge = integration.knowledge_engine is not None
        print(f"✓ Test 2: Komponenty: Memory={has_memory}, World={has_world}, Knowledge={has_knowledge}")
    except Exception as e:
        print(f"✗ Test 2 FAILED: {e}")
    
    # Test 3: Sprawdź status
    try:
        is_ready = integration.is_ready()
        print(f"✓ Test 3: Gotowość: {is_ready}")
    except Exception as e:
        print(f"✗ Test 3 FAILED: {e}")
    
    # Test 4: Pobierz statystyki
    try:
        stats = integration.get_statistics()
        print(f"✓ Test 4: Statystyki: {len(stats)} kluczy")
    except Exception as e:
        print(f"✗ Test 4 FAILED: {e}")
    
    # Test 5: Singleton
    try:
        integration1 = get_v3_integration()
        integration2 = get_v3_integration()
        print(f"✓ Test 5: Singleton: {integration1 is integration2}")
    except Exception as e:
        print(f"✗ Test 5 FAILED: {e}")
    
    # Test 6: Konfiguracja
    try:
        config = integration.config
        print(f"✓ Test 6: Konfiguracja: SYSTEM_NAME={config.SYSTEM_NAME}")
    except Exception as e:
        print(f"✗ Test 6 FAILED: {e}")
    
    # Test 7: Wiedza dla V4
    try:
        knowledge = integration.get_knowledge_for_v4()
        print(f"✓ Test 7: Wiedza dla V4: {len(knowledge)} kluczy")
    except Exception as e:
        print(f"✗ Test 7 FAILED: {e}")
    
    print("\n" + "="*50)
    print("V3Integration tests completed!")
    print("="*50)
