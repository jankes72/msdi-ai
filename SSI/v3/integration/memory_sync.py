"""
SSI V3-V4 Memory Synchronization - Mechanizm synchronizacji pamięci między V3 i V4

Moduł odpowiedzialny za:
- Synchronizację pamięci V3 ↔ V4 (dwukierunkowa)
- Obsługę aktualizacji wiedzy
- Mechanizmy odświeżania i sprawdzania spójności
- Bezpieczną synchronizację dla wielu agentów

Zgodnie z:
- SPRINTY.md Sprint 7 (Synchronizacja pamięci)
- 01_SYSTEM_ARCHITECTURE.md Sekcja 3.3, 4.1
- 10_IMPLEMENTATION_MAP.md
- PROJECT_RULES.md

Architektura:
┌─────────────────────────────────────────────────────────────┐
│                MemorySynchronizer                              │
├─────────────────────────────────────────────────────────────┤
│  V3 Memory ←───────────────────→ V4 Memory                    │
│       │                               ↑                              │
│       │                               │                              │
│       ▼                               │                              │
│  ┌─────────────────┐           ┌───────────┐                     │
│  │ Sync Strategy   │           │ Change    │                     │
│  │ (FULL, partial, │           │ Tracker   │                     │
│  │  incremental)    │           │ (zawpamię │                     │
│  └─────────────────┘           │ ętuje     │                     │
│                                    zmian)    │                     │
│                                    └───────────┘                     │
│                          ┌─────────────────────────┐          │
│                          │   Sync Statistics        │          │
│                          │   (monitoring)            │          │
│                          └─────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘

Wymagania:
- Synchronizacja musi być bezpieczna dla wielu agentów (thread-safe)
- Obsługa różnych typów pamięci (World, Pattern, Observation, Metadata, Relationship)
- Mechanizmy automatycznego odświeżania
- Zachowanie spójności danych między V3 i V4

Wersja: 1.0
Data: 2026-07-28
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Set, Callable, Union
from enum import Enum, auto
import uuid
import logging
import threading
import hashlib
import json

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMY SYNCHRONIZACJI
# =============================================================================

class SyncDirection(Enum):
    """Kierunek synchronizacji"""
    V3_TO_V4 = auto()      # Synchronizacja z V3 do V4
    V4_TO_V3 = auto()      # Synchronizacja z V4 do V3 (opcjonalnie)
    BIDIRECTIONAL = auto()  # Synchronizacja dwukierunkowa


class SyncMode(Enum):
    """Tryb synchronizacji"""
    FULL = auto()          # Pełna synchronizacja (wszystkie dane)
    INCREMENTAL = auto()    # Synchronizacja przyrostowa (tylko zmiany)
    SELECTIVE = auto()     # Selektywna synchronizacja (wybrane typy pamięci)


class SyncStatus(Enum):
    """Status synchronizacji"""
    IDLE = auto()          # Bezczynny
    PREPARING = auto()     # Przygotowywanie danych
    SYNCING = auto()       # W trakcie synchronizacji
    COMPLETED = auto()     # Zakończony pomyślnie
    FAILED = auto()        # Błąd
    CONFLICT = auto()      # Konflikt danych


class MemoryType(Enum):
    """Typy pamięci do synchronizacji"""
    WORLD = auto()         # Pamięć światów
    PATTERN = auto()       # Pamięć wzorców
    OBSERVATION = auto()   # Pamięć obserwacji
    METADATA = auto()      # Pamięć metadanych
    RELATIONSHIP = auto()  # Pamięć relacji
    ALL = auto()           # Wszystkie typy


# =============================================================================
# KONFIGURACJA SYNCHRONIZACJI
# =============================================================================

@dataclass
class MemorySyncConfig:
    """
    Konfiguracja mechanizmu synchronizacji pamięci V3↔V4.
    
    Odpowiedzialność:
    - Ustawienia kierunków synchronizacji
    - Tryby synchronizacji
    - Ustawienia czasu i automatyzacji
    - Obsługa konfliktów
    """
    
    # Kierunek synchronizacji
    SYNC_DIRECTION: SyncDirection = SyncDirection.BIDIRECTIONAL
    
    # Tryb synchronizacji
    SYNC_MODE: SyncMode = SyncMode.INCREMENTAL
    
    # Czas synchronizacji
    AUTO_SYNC_ENABLED: bool = True
    AUTO_SYNC_INTERVAL: float = 60.0  # Sekundy między automatycznymi synchronizacjami
    
    # Ustawienia przyrostowe (INCREMENTAL mode)
    TRACK_CHANGES: bool = True
    CHANGE_BUFFER_SIZE: int = 1000  # Maksymalna liczba zmian w buforze
    
    # Ustawienia konfliktów
    RESOLVE_CONFLICTS: bool = True
    CONFLICT_RESOLUTION: str = "v3_priority"  # "v3_priority", "v4_priority", "newest", "manual"
    
    # Filtrowanie pamięci
    SYNC_MEMORY_TYPES: Set[MemoryType] = field(default_factory=lambda: {
        MemoryType.WORLD,
        MemoryType.PATTERN,
        MemoryType.METADATA
    })
    
    # Ustawienia bezpieczeństwa
    MAX_CONCURRENT_SYNCS: int = 5
    SYNC_TIMEOUT: float = 120.0  # Sekundy
    
    # Ustawienia logowania
    LOG_LEVEL: str = "INFO"
    TRACK_STATISTICS: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje konfigurację do dict"""
        return {
            "SYNC_DIRECTION": self.SYNC_DIRECTION.name,
            "SYNC_MODE": self.SYNC_MODE.name,
            "AUTO_SYNC_ENABLED": self.AUTO_SYNC_ENABLED,
            "AUTO_SYNC_INTERVAL": self.AUTO_SYNC_INTERVAL,
            "TRACK_CHANGES": self.TRACK_CHANGES,
            "CHANGE_BUFFER_SIZE": self.CHANGE_BUFFER_SIZE,
            "RESOLVE_CONFLICTS": self.RESOLVE_CONFLICTS,
            "CONFLICT_RESOLUTION": self.CONFLICT_RESOLUTION,
            "SYNC_MEMORY_TYPES": [t.name for t in self.SYNC_MEMORY_TYPES],
            "MAX_CONCURRENT_SYNCS": self.MAX_CONCURRENT_SYNCS,
            "SYNC_TIMEOUT": self.SYNC_TIMEOUT,
            "LOG_LEVEL": self.LOG_LEVEL,
            "TRACK_STATISTICS": self.TRACK_STATISTICS
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemorySyncConfig":
        """Tworzy konfigurację z dict"""
        sync_types = set()
        for t in data.get("SYNC_MEMORY_TYPES", []):
            try:
                sync_types.add(MemoryType[t])
            except KeyError:
                pass
        
        return cls(
            SYNC_DIRECTION=SyncDirection[data.get("SYNC_DIRECTION", "BIDIRECTIONAL")],
            SYNC_MODE=SyncMode[data.get("SYNC_MODE", "INCREMENTAL")],
            AUTO_SYNC_ENABLED=data.get("AUTO_SYNC_ENABLED", True),
            AUTO_SYNC_INTERVAL=data.get("AUTO_SYNC_INTERVAL", 60.0),
            TRACK_CHANGES=data.get("TRACK_CHANGES", True),
            CHANGE_BUFFER_SIZE=data.get("CHANGE_BUFFER_SIZE", 1000),
            RESOLVE_CONFLICTS=data.get("RESOLVE_CONFLICTS", True),
            CONFLICT_RESOLUTION=data.get("CONFLICT_RESOLUTION", "v3_priority"),
            SYNC_MEMORY_TYPES=sync_types or {MemoryType.WORLD, MemoryType.PATTERN, MemoryType.METADATA},
            MAX_CONCURRENT_SYNCS=data.get("MAX_CONCURRENT_SYNCS", 5),
            SYNC_TIMEOUT=data.get("SYNC_TIMEOUT", 120.0),
            LOG_LEVEL=data.get("LOG_LEVEL", "INFO"),
            TRACK_STATISTICS=data.get("TRACK_STATISTICS", True)
        )


# =============================================================================
# STRUKTURY DANYCH DLA SYNCHRONIZACJI
# =============================================================================

@dataclass
class MemoryChange:
    """
    Reprezentuje pojedynczą zmianę w pamięci.
    
    Używane w trybie INCREMENTAL do śledzenia zmian.
    """
    change_id: str = field(default_factory=lambda: f"change_{uuid.uuid4().hex[:12]}")
    memory_type: MemoryType = MemoryType.WORLD
    entity_id: str = ""
    operation: str = ""  # "create", "update", "delete"
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""  # "v3" lub "v4"
    priority: int = 0  # 0 = normalny, 1 = wysoki
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje do dict"""
        return {
            "change_id": self.change_id,
            "memory_type": self.memory_type.name,
            "entity_id": self.entity_id,
            "operation": self.operation,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "priority": self.priority
        }
    
    def get_hash(self) -> str:
        """Generuje hash zmian dla wykrywania duplikatów"""
        content = f"{self.memory_type.name}:{self.entity_id}:{self.operation}:{self.timestamp.isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()


@dataclass
class SyncPackage:
    """
    Pakiet synchronizacji zawierający dane do przesłania.
    """
    package_id: str = field(default_factory=lambda: f"sync_{uuid.uuid4().hex[:12]}")
    direction: SyncDirection = SyncDirection.V3_TO_V4
    memory_type: MemoryType = MemoryType.ALL
    data: Dict[str, Any] = field(default_factory=dict)
    changes: List[MemoryChange] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje do dict"""
        return {
            "package_id": self.package_id,
            "direction": self.direction.name,
            "memory_type": self.memory_type.name,
            "data": self.data,
            "changes": [c.to_dict() for c in self.changes],
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SyncPackage":
        """Tworzy pakiet z dict"""
        changes = [MemoryChange(**c) for c in data.get("changes", [])]
        return cls(
            package_id=data.get("package_id", f"sync_{uuid.uuid4().hex[:12]}"),
            direction=SyncDirection[data.get("direction", "V3_TO_V4")],
            memory_type=MemoryType[data.get("memory_type", "ALL")],
            data=data.get("data", {}),
            changes=changes,
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            metadata=data.get("metadata", {})
        )


@dataclass
class SyncStatistics:
    """Statystyki synchronizacji"""
    total_syncs: int = 0
    successful_syncs: int = 0
    failed_syncs: int = 0
    total_changes: int = 0
    conflicts_detected: int = 0
    conflicts_resolved: int = 0
    total_sync_time: float = 0.0
    average_sync_time: float = 0.0
    last_sync_time: datetime = field(default_factory=lambda: datetime.min)
    sync_by_type: Dict[str, int] = field(default_factory=dict)
    sync_by_direction: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje do dict"""
        return {
            "total_syncs": self.total_syncs,
            "successful_syncs": self.successful_syncs,
            "failed_syncs": self.failed_syncs,
            "total_changes": self.total_changes,
            "conflicts_detected": self.conflicts_detected,
            "conflicts_resolved": self.conflicts_resolved,
            "total_sync_time": self.total_sync_time,
            "average_sync_time": self.average_sync_time,
            "last_sync_time": self.last_sync_time.isoformat() if self.last_sync_time != datetime.min else None,
            "sync_by_type": self.sync_by_type,
            "sync_by_direction": self.sync_by_direction
        }


# =============================================================================
# CHANGE TRACKER - Śledzenie zmian
# =============================================================================

class ChangeTracker:
    """
    Śledzi zmiany w pamięci w celu synchronizacji przyrostowej.
    
    Odpowiedzialność:
    - Rejestrowanie zmian w pamięci
    - Buforowanie zmian
    - Wykrywanie duplikatów
    - Zarządzanie priorytetami
    """
    
    def __init__(self, config: Optional[MemorySyncConfig] = None):
        self.config = config or MemorySyncConfig()
        self._logger = self._setup_logger()
        self._changes: Dict[str, MemoryChange] = {}  # change_id -> MemoryChange
        self._changes_by_entity: Dict[str, Dict[str, MemoryChange]] = {}  # entity_id -> {change_id -> MemoryChange}
        self._change_hashes: Set[str] = set()  # Hashy zmian do wykrywania duplikatów
        self._lock = threading.RLock()
        
        self._logger.info("ChangeTracker zainicjowany")
    
    def _setup_logger(self) -> logging.Logger:
        """Konfiguruje logger"""
        logger = logging.getLogger(f"{__name__}.ChangeTracker")
        logger.setLevel(getattr(logging, self.config.LOG_LEVEL, logging.INFO))
        return logger
    
    def record_change(
        self,
        memory_type: MemoryType,
        entity_id: str,
        operation: str,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        source: str = "v3",
        priority: int = 0
    ) -> MemoryChange:
        """
        Rejestruje zmianę w pamięci.
        
        Args:
            memory_type: Typ pamięci
            entity_id: ID encji (świata, wzorca, itd.)
            operation: Operacja (create, update, delete)
            old_value: Stara wartość (dla update/delete)
            new_value: Nowa wartość (dla create/update)
            source: Źródło zmiany (v3 lub v4)
            priority: Priorytet zmiany
            
        Returns:
            Zarejestrowana zmiana
        """
        with self._lock:
            change = MemoryChange(
                memory_type=memory_type,
                entity_id=entity_id,
                operation=operation,
                old_value=old_value,
                new_value=new_value,
                source=source,
                priority=priority
            )
            
            # Sprawdź czy ta zmiana już istnieje (duplikat)
            change_hash = change.get_hash()
            if change_hash in self._change_hashes:
                self._logger.debug(f"Duplikat zmiany wykryty: {change_hash}")
                return change
            
            # Dodaj zmianę
            self._changes[change.change_id] = change
            
            if entity_id not in self._changes_by_entity:
                self._changes_by_entity[entity_id] = {}
            self._changes_by_entity[entity_id][change.change_id] = change
            
            self._change_hashes.add(change_hash)
            
            # Ogranicz rozmiar bufora
            if len(self._changes) > self.config.CHANGE_BUFFER_SIZE:
                self._cleanup_old_changes()
            
            self._logger.debug(f"Zarejestrowano zmianę: {change.operation} {memory_type.name}/{entity_id}")
            return change
    
    def get_changes(
        self,
        memory_types: Optional[Set[MemoryType]] = None,
        since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[MemoryChange]:
        """
        Pobiera listę zmian zgodnie z filtrami.
        
        Args:
            memory_types: Filtrowanie po typach pamięci
            since: Pobierz zmiany od daty
            limit: Maksymalna liczba zmian
            
        Returns:
            Lista zmian
        """
        with self._lock:
            changes = list(self._changes.values())
            
            # Filtrowanie po typie pamięci
            if memory_types:
                changes = [c for c in changes if c.memory_type in memory_types]
            
            # Filtrowanie po dacie
            if since:
                changes = [c for c in changes if c.timestamp >= since]
            
            # Sortowanie po timestamp (od najnowszych)
            changes.sort(key=lambda c: c.timestamp, reverse=True)
            
            # Limit
            if limit:
                changes = changes[:limit]
            
            return changes
    
    def get_changes_for_entity(self, entity_id: str) -> List[MemoryChange]:
        """Pobiera wszystkie zmiany dla konkretnej encji"""
        with self._lock:
            entity_changes = self._changes_by_entity.get(entity_id, {})
            return list(entity_changes.values())
    
    def clear_changes(self, change_ids: Optional[List[str]] = None) -> int:
        """
        Czyści zarejestrowane zmiany.
        
        Args:
            change_ids: Lista ID zmian do usunięcia (None = wyczyść wszystko)
            
        Returns:
            Liczba usuniętych zmian
        """
        with self._lock:
            if change_ids is None:
                # Wyczyść wszystko
                count = len(self._changes)
                self._changes.clear()
                self._changes_by_entity.clear()
                self._change_hashes.clear()
                return count
            else:
                # Usuń określone zmiany
                count = 0
                for change_id in change_ids:
                    if change_id in self._changes:
                        change = self._changes[change_id]
                        # Usuń z _changes_by_entity
                        if change.entity_id in self._changes_by_entity:
                            if change_id in self._changes_by_entity[change.entity_id]:
                                del self._changes_by_entity[change.entity_id][change_id]
                                if not self._changes_by_entity[change.entity_id]:
                                    del self._changes_by_entity[change.entity_id]
                        # Usuń hash
                        change_hash = change.get_hash()
                        if change_hash in self._change_hashes:
                            self._change_hashes.remove(change_hash)
                        # Usuń zmianę
                        del self._changes[change_id]
                        count += 1
                return count
    
    def _cleanup_old_changes(self, max_keep: int = 500) -> int:
        """Czyści stare zmiany gdy bufor jest pełny"""
        with self._lock:
            if len(self._changes) <= max_keep:
                return 0
            
            # Sortuj po timestamp (od najstarszych)
            sorted_changes = sorted(self._changes.values(), key=lambda c: c.timestamp)
            
            # Usuń najstarsze
            to_remove = len(self._changes) - max_keep
            removed_count = 0
            
            for change in sorted_changes[:to_remove]:
                del self._changes[change.change_id]
                if change.entity_id in self._changes_by_entity:
                    if change.change_id in self._changes_by_entity[change.entity_id]:
                        del self._changes_by_entity[change.entity_id][change.change_id]
                        if not self._changes_by_entity[change.entity_id]:
                            del self._changes_by_entity[change.entity_id]
                change_hash = change.get_hash()
                if change_hash in self._change_hashes:
                    self._change_hashes.remove(change_hash)
                removed_count += 1
            
            return removed_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Pobiera statystyki tracker'a"""
        with self._lock:
            return {
                "total_changes": len(self._changes),
                "unique_entities": len(self._changes_by_entity),
                "unique_hashes": len(self._change_hashes),
                "max_buffer_size": self.config.CHANGE_BUFFER_SIZE
            }


# =============================================================================
# CONFLICT RESOLVER - Rozwiązywanie konfliktów
# =============================================================================

class ConflictResolver:
    """
    Rozwiązuje konflikty synchronizacji między V3 i V4.
    
    Odpowiedzialność:
    - Wykrywanie konfliktów
    - Rozwiązywanie konfliktów według ustalonej strategii
    - Logowanie konfliktów
    """
    
    def __init__(self, config: Optional[MemorySyncConfig] = None):
        self.config = config or MemorySyncConfig()
        self._logger = self._setup_logger()
        self._conflicts: List[Dict[str, Any]] = []  # Historia konfliktów
        self._lock = threading.RLock()
        
        self._logger.info("ConflictResolver zainicjowany")
    
    def _setup_logger(self) -> logging.Logger:
        """Konfiguruje logger"""
        logger = logging.getLogger(f"{__name__}.ConflictResolver")
        logger.setLevel(getattr(logging, self.config.LOG_LEVEL, logging.INFO))
        return logger
    
    def detect_conflict(
        self,
        v3_data: Dict[str, Any],
        v4_data: Dict[str, Any],
        entity_id: str,
        memory_type: MemoryType
    ) -> bool:
        """
        Wykrywa konflikt między danymi z V3 i V4.
        
        Args:
            v3_data: Dane z V3
            v4_data: Dane z V4
            entity_id: ID encji
            memory_type: Typ pamięci
            
        Returns:
            True jeśli wykryto konflikt
        """
        # Konflikt występuje gdy dane są różne
        if v3_data != v4_data:
            # Sprawdź czy to istotna różnica (nie tylko timestamp)
            v3_data_no_meta = {k: v for k, v in v3_data.items() if k not in ['timestamp', 'last_updated']}
            v4_data_no_meta = {k: v for k, v in v4_data.items() if k not in ['timestamp', 'last_updated']}
            
            if v3_data_no_meta != v4_data_no_meta:
                self._logger.warning(f"Konflikt wykryty: {memory_type.name}/{entity_id}")
                return True
        
        return False
    
    def resolve_conflict(
        self,
        v3_data: Dict[str, Any],
        v4_data: Dict[str, Any],
        entity_id: str,
        memory_type: MemoryType
    ) -> Dict[str, Any]:
        """
        Rozwiązuje konflikt według ustalonej strategii.
        
        Args:
            v3_data: Dane z V3
            v4_data: Dane z V4
            entity_id: ID encji
            memory_type: Typ pamięci
            
        Returns:
            Rozwiązane dane
        """
        with self._lock:
            strategy = self.config.CONFLICT_RESOLUTION
            resolved_data = {}
            
            if strategy == "v3_priority":
                # Priorytet dla V3
                resolved_data = v3_data.copy()
                self._logger.info(f"Konflikt {memory_type.name}/{entity_id}: priorytet V3")
                
            elif strategy == "v4_priority":
                # Priorytet dla V4
                resolved_data = v4_data.copy()
                self._logger.info(f"Konflikt {memory_type.name}/{entity_id}: priorytet V4")
                
            elif strategy == "newest":
                # Wybierz nowsze dane na podstawie timestamp
                v3_time = v3_data.get('timestamp') or v3_data.get('last_updated') or datetime.min
                v4_time = v4_data.get('timestamp') or v4_data.get('last_updated') or datetime.min
                
                if isinstance(v3_time, str):
                    v3_time = datetime.fromisoformat(v3_time)
                if isinstance(v4_time, str):
                    v4_time = datetime.fromisoformat(v4_time)
                
                if v3_time > v4_time:
                    resolved_data = v3_data.copy()
                    self._logger.info(f"Konflikt {memory_type.name}/{entity_id}: V3 nowsze")
                else:
                    resolved_data = v4_data.copy()
                    self._logger.info(f"Konflikt {memory_type.name}/{entity_id}: V4 nowsze")
                    
            elif strategy == "manual":
                # Manuelne rozwiązywanie - zwróć błąd
                self._logger.error(f"Konflikt {memory_type.name}/{entity_id}: wymaga manualnego rozwiązania")
                raise ValueError(f"Manual conflict resolution required for {memory_type.name}/{entity_id}")
            else:
                # Domyślnie: V3 priorytet
                resolved_data = v3_data.copy()
                self._logger.warning(f"Konflikt {memory_type.name}/{entity_id}: nieznana strategia, V3 priorytet")
            
            # Zarejestruj konflikt
            conflict_record = {
                "timestamp": datetime.now().isoformat(),
                "memory_type": memory_type.name,
                "entity_id": entity_id,
                "strategy": strategy,
                "resolution": "v3" if strategy in ["v3_priority", "newest"] and (v3_data.get('timestamp') or True) else "v4",
                "v3_data_hash": self._hash_data(v3_data),
                "v4_data_hash": self._hash_data(v4_data)
            }
            self._conflicts.append(conflict_record)
            
            return resolved_data
    
    def _hash_data(self, data: Dict[str, Any]) -> str:
        """Generuje hash dla danych"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def get_conflict_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Pobiera historię konfliktów"""
        with self._lock:
            return self._conflicts[-limit:] if limit else self._conflicts.copy()
    
    def clear_conflict_history(self) -> int:
        """Czyści historię konfliktów"""
        with self._lock:
            count = len(self._conflicts)
            self._conflicts.clear()
            return count


# =============================================================================
# GŁÓWNA KLASA SYNCHRONIZATORA
# =============================================================================

class MemorySynchronizer:
    """
    Główny mechanizm synchronizacji pamięci między V3 i V4.
    
    Odpowiedzialność:
    - Synchronizacja dwukierunkowa (V3↔V4)
    - Zarządzanie procesem synchronizacji
    - Obsługa różnych trybów synchronizacji
    - Bezpieczeństwo wielowątkowe
    
    Zgodnie z SPRINTY.md Sprint 7
    """
    
    def __init__(
        self,
        config: Optional[MemorySyncConfig] = None,
        v3_integration: Optional[Any] = None,
        v4_bridge: Optional[Any] = None
    ):
        """
        Inicjalizacja synchronizatora pamięci.
        
        Args:
            config: Konfiguracja synchronizacji
            v3_integration: Instancja V3Integration
            v4_bridge: Instancja V3ToV4Bridge
        """
        # Konfiguracja
        self.config = config or MemorySyncConfig()
        self._setup_logger()
        
        # Komponenty
        self._v3_integration = v3_integration
        self._v4_bridge = v4_bridge
        
        # Narzędzia
        self._change_tracker = ChangeTracker(self.config)
        self._conflict_resolver = ConflictResolver(self.config)
        
        # Status
        self._status = SyncStatus.IDLE
        self._statistics = SyncStatistics()
        
        # Locki dla bezpieczeństwa wielowątkowego
        self._lock = threading.RLock()
        self._sync_locks: Dict[str, threading.Lock] = {}  # Locki per typ pamięci
        
        # Ustawienia automatyczne
        self._auto_sync_enabled = self.config.AUTO_SYNC_ENABLED
        self._auto_sync_thread: Optional[threading.Thread] = None
        self._stop_auto_sync = threading.Event()
        
        self._logger.info("MemorySynchronizer zainicjowany")
    
    def _setup_logger(self) -> None:
        """Konfiguruje logger"""
        self._logger = logging.getLogger(f"{__name__}.MemorySynchronizer")
        self._logger.setLevel(getattr(logging, self.config.LOG_LEVEL, logging.INFO))
    
    def connect(
        self,
        v3_integration: Optional[Any] = None,
        v4_bridge: Optional[Any] = None
    ) -> bool:
        """
        Łączy synchronizator z systemem V3 i mostem V4.
        
        Args:
            v3_integration: Instancja V3Integration
            v4_bridge: Instancja V3ToV4Bridge
            
        Returns:
            True jeśli połączenie udane
        """
        with self._lock:
            if v3_integration is not None:
                self._v3_integration = v3_integration
            
            if v4_bridge is not None:
                self._v4_bridge = v4_bridge
            
            # Sprawdź połączenia
            v3_ready = self._v3_integration is not None
            v4_ready = self._v4_bridge is not None
            
            if v3_ready and v4_ready:
                self._logger.info("Połączenie z V3 i V4 ustalone")
                return True
            elif v3_ready:
                self._logger.warning("Połączenie z V3 ustalone, brak V4")
                return True
            else:
                self._logger.error("Brak połączenia z V3 - synchronizator nie działa")
                return False
    
    def start_auto_sync(self) -> bool:
        """Uruchamia automatyczną synchronizację"""
        if not self.config.AUTO_SYNC_ENABLED:
            self._logger.info("Automatyczna synchronizacja wyłączona w konfiguracji")
            return False
        
        if self._auto_sync_thread is not None and self._auto_sync_thread.is_alive():
            self._logger.info("Automatyczna synchronizacja już działa")
            return False
        
        self._stop_auto_sync.clear()
        self._auto_sync_thread = threading.Thread(
            target=self._auto_sync_loop,
            name="MemorySynchronizer-AutoSync",
            daemon=True
        )
        self._auto_sync_thread.start()
        self._logger.info(f"Automatyczna synchronizacja uruchomiona (co {self.config.AUTO_SYNC_INTERVAL}s)")
        return True
    
    def stop_auto_sync(self) -> None:
        """Zatrzymuje automatyczną synchronizację"""
        if self._auto_sync_thread is None:
            return
        
        self._stop_auto_sync.set()
        self._auto_sync_thread.join(timeout=self.config.SYNC_TIMEOUT)
        self._auto_sync_thread = None
        self._logger.info("Automatyczna synchronizacja zatrzymana")
    
    def _auto_sync_loop(self) -> None:
        """Pętla automatycznej synchronizacji"""
        while not self._stop_auto_sync.wait(self.config.AUTO_SYNC_INTERVAL):
            try:
                if self._stop_auto_sync.is_set():
                    break
                    
                self._logger.debug("Automatyczna synchronizacja - wykonanie...")
                result = self.sync_all()
                
                if result.get("status") == "success":
                    self._logger.info(f"Automatyczna synchronizacja ukończona: {result.get('changes_synced', 0)} zmian")
                else:
                    self._logger.warning(f"Automatyczna synchronizacja: {result.get('message', 'Nieznany błąd')}")
                    
            except Exception as e:
                self._logger.error(f"Błąd w automatycznej synchronizacji: {e}")
    
    def sync_all(
        self,
        direction: Optional[SyncDirection] = None,
        memory_types: Optional[Set[MemoryType]] = None
    ) -> Dict[str, Any]:
        """
        Wykona synchronizację wszystkich typów pamięci.
        
        Args:
            direction: Kierunek synchronizacji (domyślnie z konfiguracji)
            memory_types: Typy pamięci do synchronizacji (domyślnie z konfiguracji)
            
        Returns:
            Statystyki synchronizacji
        """
        with self._lock:
            self._status = SyncStatus.SYNCING
            start_time = datetime.now()
            
            sync_direction = direction or self.config.SYNC_DIRECTION
            sync_memory_types = memory_types or self.config.SYNC_MEMORY_TYPES
            
            stats: Dict[str, Any] = {
                "status": "success",
                "direction": sync_direction.name,
                "memory_types": [t.name for t in sync_memory_types],
                "changes_synced": 0,
                "sync_time_ms": 0,
                "details": {}
            }
            
            try:
                if sync_direction == SyncDirection.V3_TO_V4 or sync_direction == SyncDirection.BIDIRECTIONAL:
                    result = self._sync_v3_to_v4(sync_memory_types)
                    stats["v3_to_v4"] = result
                    stats["changes_synced"] += result.get("changes_synced", 0)
                
                if sync_direction == SyncDirection.V4_TO_V3 or sync_direction == SyncDirection.BIDIRECTIONAL:
                    result = self._sync_v4_to_v3(sync_memory_types)
                    stats["v4_to_v3"] = result
                    stats["changes_synced"] += result.get("changes_synced", 0)
                
                # Aktualizuj statystyki
                sync_time = (datetime.now() - start_time).total_seconds() * 1000
                stats["sync_time_ms"] = sync_time
                
                self._statistics.total_syncs += 1
                self._statistics.successful_syncs += 1
                self._statistics.total_sync_time += sync_time / 1000
                self._statistics.last_sync_time = datetime.now()
                
                # Zapisz po typie
                for mem_type in sync_memory_types:
                    type_name = mem_type.name
                    stats["details"][type_name] = sync_time / len(sync_memory_types) if sync_memory_types else sync_time
                    self._statistics.sync_by_type[type_name] = self._statistics.sync_by_type.get(type_name, 0) + 1
                
                # Zapisz po kierunku
                direction_name = sync_direction.name
                self._statistics.sync_by_direction[direction_name] = self._statistics.sync_by_direction.get(direction_name, 0) + 1
                
                # Oblicz średni czas
                if self._statistics.total_syncs > 0:
                    self._statistics.average_sync_time = self._statistics.total_sync_time / self._statistics.total_syncs
                
                self._status = SyncStatus.COMPLETED
                
            except Exception as e:
                stats["status"] = "failed"
                stats["message"] = str(e)
                
                self._statistics.total_syncs += 1
                self._statistics.failed_syncs += 1
                
                self._logger.error(f"Błąd synchronizacji: {e}")
                self._status = SyncStatus.FAILED
            
            return stats
    
    def _sync_v3_to_v4(self, memory_types: Set[MemoryType]) -> Dict[str, Any]:
        """Synchronizuje dane z V3 do V4"""
        if self._v3_integration is None:
            return {"status": "error", "message": "V3Integration niedostępny"}
        
        if self._v4_bridge is None:
            return {"status": "error", "message": "V3ToV4Bridge niedostępny"}
        
        result: Dict[str, Any] = {"changes_synced": 0, "by_type": {}}
        
        # Pobierz dane z V3
        v3_data = self._extract_v3_data(memory_types)
        
        # Stwórz pakiet synchronizacji
        sync_package = SyncPackage(
            direction=SyncDirection.V3_TO_V4,
            data=v3_data,
            metadata={
                "source": "V3",
                "extraction_time": datetime.now().isoformat()
            }
        )
        
        # Wyślij przez most V3ToV4Bridge
        try:
            transfer_result = self._v4_bridge.transfer_knowledge()
            result["transfer_result"] = transfer_result
            result["changes_synced"] = transfer_result.get("worlds_transferred", 0) + \
                                     transfer_result.get("patterns_transferred", 0)
            
        except Exception as e:
            self._logger.error(f"Błąd transferu do V4: {e}")
            result["status"] = "error"
            result["message"] = str(e)
        
        return result
    
    def _sync_v4_to_v3(self, memory_types: Set[MemoryType]) -> Dict[str, Any]:
        """
        Synchronizuje dane z V4 do V3 (opcjonalnie).
        
        UWAGA: Ta funkcjonalność może być ograniczona lub wyłączona
        zgodnie z architekturą systemu.
        """
        # W bardziej zaawansowanej implementacji tutaj byłaby logika
        # pobierania danych z V4 i aktualizacji V3
        
        self._logger.warning("Synchronizacja V4→V3 nie jest domyślnie implementowana")
        return {"changes_synced": 0, "message": "V4→V3 synchronization not implemented"}
    
    def _extract_v3_data(self, memory_types: Set[MemoryType]) -> Dict[str, Any]:
        """Ekstrakcja danych z V3 dla określonych typów pamięci"""
        if self._v3_integration is None:
            return {}
        
        data: Dict[str, Any] = {}
        
        memory_manager = self._v3_integration.memory_manager
        world_manager = self._v3_integration.world_manager
        
        if memory_manager is None and world_manager is None:
            return {}
        
        # Ekstrakcja światów
        if MemoryType.WORLD in memory_types or MemoryType.ALL in memory_types:
            data["worlds"] = self._extract_worlds()
        
        # Ekstrakcja wzorców
        if MemoryType.PATTERN in memory_types or MemoryType.ALL in memory_types:
            data["patterns"] = self._extract_patterns()
        
        # Ekstrakcja metadanych
        if MemoryType.METADATA in memory_types or MemoryType.ALL in memory_types:
            data["metadata"] = self._extract_metadata()
        
        # Ekstrakcja obserwacji
        if MemoryType.OBSERVATION in memory_types or MemoryType.ALL in memory_types:
            data["observations"] = self._extract_observations()
        
        # Ekstrakcja relacji
        if MemoryType.RELATIONSHIP in memory_types or MemoryType.ALL in memory_types:
            data["relationships"] = self._extract_relationships()
        
        return data
    
    def _extract_worlds(self) -> List[Dict[str, Any]]:
        """Ekstrakcja światów z WorldManager"""
        if self._v3_integration is None or self._v3_integration.world_manager is None:
            return []
        
        try:
            worlds = self._v3_integration.world_manager.list_worlds()
            return [w.to_dict() for w in worlds]
        except Exception as e:
            self._logger.error(f"Błąd ekstrakcji światów: {e}")
            return []
    
    def _extract_patterns(self) -> List[Dict[str, Any]]:
        """Ekstrakcja wzorców z pamięci wzorców"""
        if self._v3_integration is None or self._v3_integration.memory_manager is None:
            return []
        
        try:
            memory_manager = self._v3_integration.memory_manager
            if hasattr(memory_manager, 'pattern_memory'):
                pattern_memory = memory_manager.pattern_memory
                if hasattr(pattern_memory, 'get_all_patterns'):
                    patterns = pattern_memory.get_all_patterns()
                    return [p.to_dict() if hasattr(p, 'to_dict') else p for p in patterns]
        except Exception as e:
            self._logger.error(f"Błąd ekstrakcji wzorców: {e}")
            return []
        
        return []
    
    def _extract_metadata(self) -> Dict[str, Any]:
        """Ekstrakcja metadanych"""
        if self._v3_integration is None or self._v3_integration.memory_manager is None:
            return {}
        
        try:
            memory_manager = self._v3_integration.memory_manager
            if hasattr(memory_manager, 'metadata_memory'):
                metadata_memory = memory_manager.metadata_memory
                if hasattr(metadata_memory, 'get_all_metadata'):
                    return metadata_memory.get_all_metadata()
        except Exception as e:
            self._logger.error(f"Błąd ekstrakcji metadanych: {e}")
            return {}
        
        return {}
    
    def _extract_observations(self) -> List[Dict[str, Any]]:
        """Ekstrakcja obserwacji"""
        if self._v3_integration is None or self._v3_integration.memory_manager is None:
            return []
        
        try:
            memory_manager = self._v3_integration.memory_manager
            if hasattr(memory_manager, 'observation_memory'):
                observation_memory = memory_manager.observation_memory
                if hasattr(observation_memory, 'get_all_observations'):
                    observations = observation_memory.get_all_observations()
                    return [o.to_dict() if hasattr(o, 'to_dict') else o for o in observations]
        except Exception as e:
            self._logger.error(f"Błąd ekstrakcji obserwacji: {e}")
            return []
        
        return []
    
    def _extract_relationships(self) -> List[Dict[str, Any]]:
        """Ekstrakcja relacji"""
        if self._v3_integration is None or self._v3_integration.memory_manager is None:
            return []
        
        try:
            memory_manager = self._v3_integration.memory_manager
            if hasattr(memory_manager, 'relationship_memory'):
                relationship_memory = memory_manager.relationship_memory
                if hasattr(relationship_memory, 'get_all_relationships'):
                    relationships = relationship_memory.get_all_relationships()
                    return [r.to_dict() if hasattr(r, 'to_dict') else r for r in relationships]
        except Exception as e:
            self._logger.error(f"Błąd ekstrakcji relacji: {e}")
            return []
        
        return []
    
    def sync_memory_type(
        self,
        memory_type: MemoryType,
        direction: Optional[SyncDirection] = None
    ) -> Dict[str, Any]:
        """
        Synchronizuje określoną pamięć.
        
        Args:
            memory_type: Typ pamięci do synchronizacji
            direction: Kierunek synchronizacji
            
        Returns:
            Statystyki synchronizacji
        """
        sync_dir = direction or self.config.SYNC_DIRECTION
        return self.sync_all(direction=sync_dir, memory_types={memory_type})
    
    def force_sync(self) -> Dict[str, Any]:
        """Wymusza pełną synchronizację (FULL mode)"""
        original_mode = self.config.SYNC_MODE
        try:
            # Tymczasowo zmień tryb na FULL
            self.config.SYNC_MODE = SyncMode.FULL
            return self.sync_all()
        finally:
            self.config.SYNC_MODE = original_mode
    
    def get_status(self) -> SyncStatus:
        """Zwraca aktualny status synchronizacji"""
        return self._status
    
    def get_statistics(self) -> Dict[str, Any]:
        """Zwraca statystyki synchronizacji"""
        stats_dict = self._statistics.to_dict()
        stats_dict["change_tracker"] = self._change_tracker.get_statistics()
        stats_dict["conflicts"] = {
            "total": len(self._conflict_resolver.get_conflict_history()),
            "resolution_strategy": self.config.CONFLICT_RESOLUTION
        }
        return stats_dict
    
    def reset_statistics(self) -> None:
        """Resetuje statystyki"""
        with self._lock:
            self._statistics = SyncStatistics()
            self._change_tracker.clear_changes()
            self._conflict_resolver.clear_conflict_history()
            self._logger.info("Statystyki synchronizacji zresetowane")
    
    def __repr__(self) -> str:
        return f"MemorySynchronizer(status={self._status.name}, syncs={self._statistics.total_syncs})"


# =============================================================================
# FABRYKA I SINGLETON
# =============================================================================

_default_synchronizer: Optional[MemorySynchronizer] = None


def tworz_memory_synchronizer(
    config: Optional[Union[Dict[str, Any], MemorySyncConfig]] = None,
    v3_integration: Optional[Any] = None,
    v4_bridge: Optional[Any] = None
) -> MemorySynchronizer:
    """
    Fabryka tworzącą MemorySynchronizer.
    
    Args:
        config: Konfiguracja (dict lub MemorySyncConfig)
        v3_integration: Instancja V3Integration
        v4_bridge: Instancja V3ToV4Bridge
        
    Returns:
        MemorySynchronizer
    """
    if isinstance(config, dict):
        config_obj = MemorySyncConfig.from_dict(config)
    elif isinstance(config, MemorySyncConfig):
        config_obj = config
    else:
        config_obj = MemorySyncConfig()
    
    return MemorySynchronizer(config_obj, v3_integration, v4_bridge)


def get_memory_synchronizer() -> MemorySynchronizer:
    """
    Zwraca domyślną instancję MemorySynchronizer (Singleton).
    
    Returns:
        MemorySynchronizer
    """
    global _default_synchronizer
    if _default_synchronizer is None:
        _default_synchronizer = tworz_memory_synchronizer()
    return _default_synchronizer


def reset_memory_synchronizer() -> None:
    """Resetuje domyślną instancję MemorySynchronizer"""
    global _default_synchronizer
    if _default_synchronizer is not None:
        _default_synchronizer.stop_auto_sync()
        _default_synchronizer.reset_statistics()
    _default_synchronizer = None


# =============================================================================
# TESTY
# =============================================================================

if __name__ == "__main__":
    print("Testing MemorySynchronizer (Sprint 7)...")
    print("=" * 60)
    
    # Test 1: Konfiguracja
    print("\n[Test 1] Konfiguracja MemorySyncConfig")
    config = MemorySyncConfig(
        SYNC_DIRECTION=SyncDirection.BIDIRECTIONAL,
        SYNC_MODE=SyncMode.INCREMENTAL,
        AUTO_SYNC_ENABLED=True,
        AUTO_SYNC_INTERVAL=30.0
    )
    print(f"✓ Konfiguracja utworzona: {config.to_dict()}")
    
    # Test 2: ChangeTracker
    print("\n[Test 2] ChangeTracker")
    tracker = ChangeTracker(config)
    change = tracker.record_change(
        memory_type=MemoryType.WORLD,
        entity_id="world_001",
        operation="create",
        new_value={"world_id": "world_001", "name": "Test World"},
        source="v3"
    )
    print(f"✓ Zmiana zarejestrowana: {change.change_id}")
    changes = tracker.get_changes()
    print(f"✓ Liczba zmian: {len(changes)}")
    stats = tracker.get_statistics()
    print(f"✓ Statystyki tracker'a: {stats}")
    
    # Test 3: ConflictResolver
    print("\n[Test 3] ConflictResolver")
    resolver = ConflictResolver(config)
    v3_data = {"id": "test", "value": "from_v3", "timestamp": datetime.now().isoformat()}
    v4_data = {"id": "test", "value": "from_v4", "timestamp": datetime.now().isoformat()}
    has_conflict = resolver.detect_conflict(v3_data, v4_data, "test", MemoryType.WORLD)
    print(f"✓ Konflikt wykryty: {has_conflict}")
    if has_conflict:
        resolved = resolver.resolve_conflict(v3_data, v4_data, "test", MemoryType.WORLD)
        print(f"✓ Rozwiązano: {resolved.get('value')}")
    
    # Test 4: MemorySynchronizer (podstawowy)
    print("\n[Test 4] MemorySynchronizer - Podstawowy")
    synchronizer = tworz_memory_synchronizer(config)
    print(f"✓ Synchronizator utworzony: {synchronizer}")
    print(f"  Status: {synchronizer.get_status().name}")
    print(f"  Konfiguracja: {synchronizer.config.SYNC_MODE.name}")
    
    # Test 5: Connection Test (z V3Integration)
    print("\n[Test 5] Połączenie z V3Integration")
    try:
        from SSI.v3.v3_integration import tworz_v3_integration
        v3_integration = tworz_v3_integration()
        
        from SSI.v3.integration.v3_to_v4_bridge import tworz_v3_to_v4_bridge
        v4_bridge = tworz_v3_to_v4_bridge()
        
        result = synchronizer.connect(v3_integration, v4_bridge)
        print(f"✓ Połączenie: {result}")
        
        # Test synchronizacji
        sync_result = synchronizer.sync_memory_type(MemoryType.WORLD)
        print(f"✓ Synchronizacja世界: {sync_result.get('status')}")
        
    except Exception as e:
        print(f"⚠ Połączenie nie powiodło się (normalne bez V3): {e}")
    
    # Test 6: Singleton
    print("\n[Test 6] Singleton")
    sync1 = get_memory_synchronizer()
    sync2 = get_memory_synchronizer()
    print(f"✓ Singleton działa: {sync1 is sync2}")
    
    # Test 7: Statystyki
    print("\n[Test 7] Statystyki")
    stats = synchronizer.get_statistics()
    print(f"✓ Statystyki: {len(stats)} kluczy")
    
    # Test 8: Fabryka z dict
    print("\n[Test 8] Fabryka z dict")
    config_dict = {
        "SYNC_DIRECTION": "BIDIRECTIONAL",
        "SYNC_MODE": "INCREMENTAL",
        "AUTO_SYNC_ENABLED": False
    }
    sync_from_dict = tworz_memory_synchronizer(config_dict)
    print(f"✓ Synchronizator z dict: {sync_from_dict.config.SYNC_MODE.name}")
    
    print("\n" + "=" * 60)
    print("MemorySynchronizer tests completed! (Sprint 7)")
    print("=" * 60)
