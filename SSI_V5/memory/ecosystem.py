# SSI V5 - Memory Ecosystem
# ETAP 1.2.7.3: Adaptive Knowledge Ecosystem

"""
MemoryEcosystem - Orkiestrator systemu pamięci SSI V5.

NIE JEST magazynem rekordów.
JEST orkiestratorem, który:
- Zarządza cyklem życia MemoryStores
- Routuje rekordy do odpowiednich Store'ów (na podstawie typu)
- Udostępnia wspólne API dla całego systemu pamięci
- Publikuje zdarzenia domenowe przez IFC
- Utrzymuje zdrowie i spójność pamięci

Architektura:
                    MemoryEcosystem
                           |
        ┌──────────────────┼──────────────────┐
        |                  |                  |
        ▼                  ▼                  ▼
 ModelMemoryStore   AgentMemoryStore   ExperimentMemoryStore

Kontrakt API:
    register_store(store_name: str, store: BaseMemoryStore) -> bool
    save(record: MemoryRecord) -> str
    get(memory_id: str) -> Optional[MemoryRecord]
    find(query: MemoryQuery) -> List[MemoryRecord]
    delete(memory_id: str) -> bool
    get_store(store_name: str) -> Optional[BaseMemoryStore]
    list_stores() -> List[str]
    statistics() -> Dict[str, Any]
    health() -> Dict[str, Any]

Zdarzenia IFC:
    memory_saved      - Nowy rekord zapisany
    memory_retrieved - Rekord pobrany
    memory_deleted   - Rekord usunięty
    store_registered - Nowy Store zarejestrowany
"""

from typing import Any, Callable, Dict, List, Optional, Type, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

# Importy lokalne (unikanie circular imports)
from .stores.base_store import BaseMemoryStore, MemoryRecord, MemoryQuery


class MemoryEcosystemStatus(Enum):
    """Status ekosystemu pamięci."""
    INITIALIZING = "initializing"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    ERROR = "error"
    SHUTDOWN = "shutdown"


@dataclass
class MemoryEcosystemConfig:
    """Konfiguracja ekosystemu pamięci."""
    auto_register_stores: bool = True  # Czy auto-rejestrować domyślne Store'y
    publish_events: bool = True        # Czy publikować zdarzenia przez IFC
    enable_health_checks: bool = True  # Czy monitorować zdrowie Store'ów
    default_store_type: str = "base"  # Domyślny typ dla rekordów bez typu


class MemoryEcosystem:
    """
    Orkiestrator systemu pamięci SSI V5.
    
    Odpowiedzialność:
    - Routing rekordów do odpowiednich Store'ów
    - Zarządzanie cyklem życia Store'ów
    - Publikacja zdarzeń domenowych
    - Monitorowanie zdrowia systemu
    """
    
    # Mapa typów rekordów na nazwy Store'ów
    # Umożliwia automatyczne routowanie na podstawie record.type
    # 
    # UWAGA: system_memory i knowledge_record nie mają jeszcze dedykowanych Store'ów
    # Tymczasowo są mapowane do experiment_store (ETAP 1.2.7.3)
    # Docelowo (przyszłe etapy) będą miały swoje Store'y: SystemMemoryStore, KnowledgeStore
    TYPE_TO_STORE_MAP = {
        "model_memory": "model_store",
        "agent_memory": "agent_store",
        "experiment_memory": "experiment_store",
        "system_memory": "experiment_store",  # Tymczasowo
        "knowledge_record": "experiment_store",  # Tymczasowo
        "collective_memory": "collective_store",  # Przyszłe
    }
    
    def __init__(
        self,
        ifc: Optional[Any] = None,
        config: Optional[MemoryEcosystemConfig] = None
    ):
        """
        Inicjalizacja MemoryEcosystem.
        
        Args:
            ifc: Referencja do IFCRegistry (opcjonalna)
            config: Konfiguracja ekosystemu
        """
        self._ifc = ifc
        self._config = config or MemoryEcosystemConfig()
        self._status = MemoryEcosystemStatus.INITIALIZING
        
        # Rejestr Store'ów: nazwa -> BaseMemoryStore
        self._stores: Dict[str, BaseMemoryStore] = {}
        
        # Rejestr typów rekordów -> nazwa Store'a
        self._record_type_mapping: Dict[str, str] = {}
        
        # Callbacki na zdarzenia
        self._event_callbacks: Dict[str, List[Callable]] = {}
        
        # Historia operacji
        self._operation_history: List[Dict[str, Any]] = []
        
        # Inicjalizacja
        self._initialize()
    
    def _initialize(self) -> None:
        """Inicjalizacja ekosystemu."""
        # Jeśli auto_register_stores, zarejestruj domyślne Store'y
        if self._config.auto_register_stores:
            # Import dynamiczny aby uniknąć circular imports
            from .stores.model_store import ModelMemoryStore
            from .stores.agent_store import AgentMemoryStore
            from .stores.experiment_store import ExperimentMemoryStore
            
            # Rejestracja domyślnych Store'ów
            self.register_store("model_store", ModelMemoryStore())
            self.register_store("agent_store", AgentMemoryStore())
            self.register_store("experiment_store", ExperimentMemoryStore())
        
        # Ustaw status na HEALTHY (jeśli są Store'y)
        if self._stores:
            self._status = MemoryEcosystemStatus.HEALTHY
        else:
            self._status = MemoryEcosystemStatus.DEGRADED
    
    # ==================== STORE MANAGEMENT ====================
    
    def register_store(
        self,
        store_name: str,
        store: BaseMemoryStore,
        record_types: Optional[List[str]] = None
    ) -> bool:
        """
        Rejestracja nowego Store'a w ekosystemie.
        
        Args:
            store_name: Unikalna nazwa Store'a
            store: Instancja BaseMemoryStore
            record_types: Lista typów rekordów obsługiwanych przez ten Store
                         (jeśli None, używa store._get_memory_type())
        
        Returns:
            True jeśli rejestracja się powiodła
        """
        if store_name in self._stores:
            return False  # Store o tej nazwie już istnieje
        
        # Zapis Store'a
        self._stores[store_name] = store
        
        # Rejestracja typów rekordów
        if record_types is None:
            # Pobierz typ z Store'a
            record_types = [store._get_memory_type()]
        
        for record_type in record_types:
            self._record_type_mapping[record_type] = store_name
        
        # Logowanie operacji
        self._log_operation("store_registered", {"store": store_name, "types": record_types})
        
        # Publikacja zdarzenia IFC
        if self._config.publish_events and self._ifc:
            self._publish_event("store_registered", {
                "store_name": store_name,
                "record_types": record_types
            })
        
        # Wywołanie callbacków
        self._trigger_event_callbacks("store_registered", store_name, store)
        
        return True
    
    def unregister_store(self, store_name: str) -> bool:
        """
        Usunięcie Store'a z ekosystemu.
        
        Args:
            store_name: Nazwa Store'a
            
        Returns:
            True jeśli usunięcie się powiodło
        """
        if store_name not in self._stores:
            return False
        
        store = self._stores[store_name]
        
        # Usunięcie mapowania typów
        store_type = store._get_memory_type()
        if store_type in self._record_type_mapping:
            del self._record_type_mapping[store_type]
        
        # Usunięcie Store'a
        del self._stores[store_name]
        
        # Logowanie operacji
        self._log_operation("store_unregistered", {"store": store_name})
        
        # Publikacja zdarzenia IFC
        if self._config.publish_events and self._ifc:
            self._publish_event("store_unregistered", {"store_name": store_name})
        
        return True
    
    def get_store(self, store_name: str) -> Optional[BaseMemoryStore]:
        """
        Pobranie Store'a po nazwie.
        
        Args:
            store_name: Nazwa Store'a
            
        Returns:
            BaseMemoryStore lub None
        """
        return self._stores.get(store_name)
    
    def list_stores(self) -> List[str]:
        """
        Lista wszystkich zarejestrowanych Store'ów.
        
        Returns:
            Lista nazw Store'ów
        """
        return list(self._stores.keys())
    
    # ==================== RECORD ROUTING ====================
    
    def _get_store_for_record(self, record: MemoryRecord) -> Optional[BaseMemoryStore]:
        """
        Znajdź Store dla danego rekordu (na podstawie record.type).
        
        Args:
            record: MemoryRecord
            
        Returns:
            BaseMemoryStore lub None
        """
        # 1. Spróbuj znaleźć Store po typie rekordu
        store_name = self._record_type_mapping.get(record.type)
        if store_name and store_name in self._stores:
            return self._stores[store_name]
        
        # 2. Spróbuj znaleźć Store po mapie TYPE_TO_STORE_MAP
        store_name = self.TYPE_TO_STORE_MAP.get(record.type)
        if store_name and store_name in self._stores:
            return self._stores[store_name]
        
        # 3. Jeśli nie znaleziono, zwróć pierwszy dostępny Store (tylko w trybie awaryjnym)
        if self._stores:
            first_store = list(self._stores.values())[0]
            return first_store
        
        return None
    
    def save(self, record: Union[MemoryRecord, Dict[str, Any]]) -> str:
        """
        Zapis rekordu do odpowiedniego Store'a.
        
        Args:
            record: MemoryRecord lub słownik
            
        Returns:
            memory_id zapisanego rekordu
            
        Raises:
            ValueError: Jeśli nie znaleziono odpowiedniego Store'a
        """
        # Konwersja ze słownika
        if isinstance(record, dict):
            record = MemoryRecord.from_dict(record)
        
        # Znalezienie Store'a
        store = self._get_store_for_record(record)
        if store is None:
            error_msg = f"No store found for record type: {record.type}. Available stores: {self.list_stores()}"
            self._log_operation("save_failed", {"error": error_msg, "record_type": record.type})
            raise ValueError(error_msg)
        
        # Zapis do Store'a
        memory_id = store.save(record)
        
        # Logowanie operacji
        self._log_operation("record_saved", {
            "memory_id": memory_id,
            "record_type": record.type,
            "store": store.store_type
        })
        
        # Publikacja zdarzenia IFC
        if self._config.publish_events and self._ifc:
            self._publish_event("memory_saved", {
                "memory_id": memory_id,
                "record_type": record.type,
                "source": record.source,
                "timestamp": record.timestamp,
                "store": store.store_type
            })
        
        # Wywołanie callbacków
        self._trigger_event_callbacks("memory_saved", memory_id, record)
        
        return memory_id
    
    def get(self, memory_id: str) -> Optional[MemoryRecord]:
        """
        Pobranie rekordu z dowolnego Store'a.
        
        Args:
            memory_id: ID rekordu
            
        Returns:
            MemoryRecord lub None jeśli nie znaleziono
        """
        # Szukamy we wszystkich Store'ach
        for store in self._stores.values():
            record = store.get(memory_id)
            if record is not None:
                # Logowanie operacji
                self._log_operation("record_retrieved", {
                    "memory_id": memory_id,
                    "store": store.store_type
                })
                
                # Publikacja zdarzenia IFC
                if self._config.publish_events and self._ifc:
                    self._publish_event("memory_retrieved", {
                        "memory_id": memory_id,
                        "record_type": record.type,
                        "store": store.store_type
                    })
                
                # Wywołanie callbacków
                self._trigger_event_callbacks("memory_retrieved", memory_id, record)
                
                return record
        
        # Nie znaleziono
        self._log_operation("get_failed", {"memory_id": memory_id})
        return None
    
    def delete(self, memory_id: str) -> bool:
        """
        Usunięcie rekordu z ekosystemu.
        
        Args:
            memory_id: ID rekordu
            
        Returns:
            True jeśli usunięto, False jeśli nie znaleziono
        """
        # Szukamy i usuwamy z odpowiedniego Store'a
        for store in self._stores.values():
            if store.get(memory_id) is not None:
                deleted = store.delete(memory_id)
                
                if deleted:
                    # Logowanie operacji
                    self._log_operation("record_deleted", {
                        "memory_id": memory_id,
                        "store": store.store_type
                    })
                    
                    # Publikacja zdarzenia IFC
                    if self._config.publish_events and self._ifc:
                        self._publish_event("memory_deleted", {
                            "memory_id": memory_id,
                            "store": store.store_type
                        })
                    
                    # Wywołanie callbacków
                    self._trigger_event_callbacks("memory_deleted", memory_id, None)
                
                return deleted
        
        # Nie znaleziono
        self._log_operation("delete_failed", {"memory_id": memory_id})
        return False
    
    def find(self, query: Union[MemoryQuery, Dict[str, Any]] = None) -> List[MemoryRecord]:
        """
        Wyszukiwanie rekordów we wszystkich Store'ach.
        
        Args:
            query: MemoryQuery lub słownik
            
        Returns:
            Lista pasujących MemoryRecord
        """
        if query is None:
            query = MemoryQuery()
        
        if isinstance(query, dict):
            query = MemoryQuery(**query)
        
        # Wyszukiwanie we wszystkich Store'ach
        results = []
        for store in self._stores.values():
            store_results = store.find(query)
            results.extend(store_results)
        
        # Logowanie operacji
        self._log_operation("records_found", {
            "query": query.to_dict(),
            "count": len(results)
        })
        
        return results
    
    # ==================== EVENTS & CALLBACKS ====================
    
    def on(self, event_name: str, callback: Callable) -> None:
        """
        Rejestracja callbacka na zdarzenie.
        
        Args:
            event_name: Nazwa zdarzenia
            callback: Funkcja callback
        """
        if event_name not in self._event_callbacks:
            self._event_callbacks[event_name] = []
        self._event_callbacks[event_name].append(callback)
    
    def _trigger_event_callbacks(
        self,
        event_name: str,
        *args,
        **kwargs
    ) -> None:
        """Wywołanie callbacków dla zdarzenia."""
        for callback in self._event_callbacks.get(event_name, []):
            try:
                callback(*args, **kwargs)
            except Exception:
                pass  # Nie przerywamy innych callbacków
    
    def _publish_event(self, event_name: str, data: Dict[str, Any]) -> None:
        """
        Publikacja zdarzenia przez IFC.
        
        Args:
            event_name: Nazwa zdarzenia
            data: Dane zdarzenia
        """
        if not self._ifc:
            return
        
        try:
            # Tworzymy wiadomość IFC
            from ..ifc.message import IFCMessage, MessageType
            
            message = IFCMessage(
                source="memory_ecosystem",
                target="ifc_broadcast",
                message_type=MessageType.EVENT,
                payload={
                    "event": event_name,
                    "data": data,
                    "timestamp": message.metadata.get("timestamp", "")
                }
            )
            
            # Wysyłanie wiadomości
            self._ifc.route(message)
        except Exception:
            pass  # Nie przerywamy działania systemu
    
    # ==================== STATISTICS & HEALTH ====================
    
    def statistics(self) -> Dict[str, Any]:
        """
        Pobranie statystyk ekosystemu.
        
        Returns:
            Słownik ze statystykami
        """
        stats = {
            "status": self._status.value,
            "total_stores": len(self._stores),
            "store_names": self.list_stores(),
            "total_operations": len(self._operation_history),
            "stores": {}
        }
        
        # Statystyki poszczególnych Store'ów
        for store_name, store in self._stores.items():
            stats["stores"][store_name] = store.get_statistics()
        
        return stats
    
    def health(self) -> Dict[str, Any]:
        """
        Sprawdzenie zdrowia ekosystemu.
        
        Returns:
            Słownik ze statusem zdrowia
        """
        health_report = {
            "status": self._status.value,
            "stores": {}
        }
        
        # Sprawdzanie zdrowia każdego Store'a
        all_healthy = True
        for store_name, store in self._stores.items():
            try:
                store_stats = store.get_statistics()
                health_report["stores"][store_name] = {
                    "status": "healthy",
                    "records": store_stats.get("total_records", 0)
                }
            except Exception as e:
                health_report["stores"][store_name] = {
                    "status": "error",
                    "error": str(e)
                }
                all_healthy = False
        
        # Aktualizacja statusu
        if all_healthy and len(self._stores) > 0:
            self._status = MemoryEcosystemStatus.HEALTHY
        elif len(self._stores) == 0:
            self._status = MemoryEcosystemStatus.DEGRADED
        else:
            self._status = MemoryEcosystemStatus.DEGRADED
        
        health_report["status"] = self._status.value
        return health_report
    
    # ==================== UTILITY METHODS ====================
    
    def _log_operation(self, operation: str, data: Dict[str, Any]) -> None:
        """
        Logowanie operacji (wewnętrzne).
        
        Args:
            operation: Nazwa operacji
            data: Dane operacji
        """
        entry = {
            "timestamp": self._get_current_timestamp(),
            "operation": operation,
            "data": data.copy() if data else {}
        }
        self._operation_history.append(entry)
        
        # Ograniczenie historii
        if len(self._operation_history) > 10000:
            self._operation_history = self._operation_history[-10000:]
    
    def _get_current_timestamp(self) -> str:
        """Pobranie aktualnego timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def clear(self) -> None:
        """
        Wyczyszczenie wszystkich Store'ów.
        """
        for store in self._stores.values():
            store.clear()
        
        self._operation_history.clear()
        self._log_operation("system_cleared", {})
    
    def shutdown(self) -> None:
        """
        Zamknięcie ekosystemu.
        """
        self._status = MemoryEcosystemStatus.SHUTDOWN
        
        # Wyczyszczenie
        self.clear()
        
        # Usunięcie Store'ów
        self._stores.clear()
        self._record_type_mapping.clear()
        self._event_callbacks.clear()
    
    # ==================== CONVENIENCE METHODS ====================
    
    def save_model_experience(self, **kwargs) -> str:
        """
        Skrócona metoda do zapisywania doświadczenia modelu.
        
        Args:
            **kwargs: Argumenty dla ModelMemoryStore.save_model_experience()
            
        Returns:
            memory_id
        """
        store = self.get_store("model_store")
        if store and hasattr(store, "save_model_experience"):
            return store.save_model_experience(**kwargs)
        
        # Fallback: utworzenie rekordu ręcznie
        record = MemoryRecord.create(
            content=kwargs,
            memory_type="model_memory",
            source="memory_ecosystem"
        )
        return self.save(record)
    
    def save_agent_experience(self, **kwargs) -> str:
        """
        Skrócona metoda do zapisywania doświadczenia agenta.
        
        Args:
            **kwargs: Argumenty dla AgentMemoryStore.save_agent_experience()
            
        Returns:
            memory_id
        """
        store = self.get_store("agent_store")
        if store and hasattr(store, "save_agent_experience"):
            return store.save_agent_experience(**kwargs)
        
        # Fallback: utworzenie rekordu ręcznie
        record = MemoryRecord.create(
            content=kwargs,
            memory_type="agent_memory",
            source="memory_ecosystem"
        )
        return self.save(record)
    
    def save_experiment_result(self, **kwargs) -> str:
        """
        Skrócona metoda do zapisywania wyniku eksperymentu.
        
        Args:
            **kwargs: Argumenty dla ExperimentMemoryStore.save_experiment_result()
            
        Returns:
            memory_id
        """
        store = self.get_store("experiment_store")
        if store and hasattr(store, "save_experiment_result"):
            return store.save_experiment_result(**kwargs)
        
        # Fallback: utworzenie rekordu ręcznie
        record = MemoryRecord.create(
            content=kwargs,
            memory_type="experiment_memory",
            source="memory_ecosystem"
        )
        return self.save(record)
