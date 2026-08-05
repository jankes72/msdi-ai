# SSI V5 - Base Memory Store
# ETAP 1.2.7.3: Adaptive Knowledge Ecosystem

"""
BaseMemoryStore - Abstrakcyjna klasa bazowa dla wszystkich składowych pamięci.

Odpowiada za:
- Definiowanie interfejsu MemoryStore
- Wspólną strukturę rekordów (MemoryRecord)
- Podstawowe operacje CRUD
- Wyszukiwanie i filtrowanie

Kontrakt implementacji:
    1. Każdy konkretny Store dziedziczy z BaseMemoryStore
    2. Implementuje _validate_record() dla walidacji specyficznej
    3. Może rozszerzać funkcjonalność o specyficzne metody

Architektura:
    BaseMemoryStore
        |
        +-- ModelMemoryStore
        +-- AgentMemoryStore
        +-- ExperimentMemoryStore
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import uuid
import json
from pathlib import Path


@dataclass
class MemoryRecord:
    """
    Uniwersalna struktura rekordu pamięci.
    
    Wspólny format dla wszystkich typów pamięci:
    - ModelMemoryStore
    - AgentMemoryStore
    - ExperimentMemoryStore
    """
    memory_id: str                          # Unikalny identyfikator rekordu
    type: str                               # Typ rekordu (model_memory, agent_memory, experiment)
    timestamp: str                          # Data utworzenia (ISO format)
    source: str                             # Źródło rekordu (np. "agent_runtime", "pipeline")
    metadata: Dict[str, Any] = field(default_factory=dict)  # Metadane
    content: Dict[str, Any] = field(default_factory=dict)  # Treść rekordu
    
    def __post_init__(self):
        """Walidacja i ustawienie domyślnych wartości."""
        if not self.metadata:
            self.metadata = {}
        if not self.content:
            self.content = {}
    
    @classmethod
    def create(
        cls,
        content: Dict[str, Any],
        memory_type: str,
        source: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'MemoryRecord':
        """
        Fabryka tworzenia rekordu z automatycznym ID i timestamp.
        
        Args:
            content: Treść rekordu
            memory_type: Typ pamięci
            source: Źródło rekordu
            metadata: Metadane (opcjonalne)
            
        Returns:
            MemoryRecord
        """
        return cls(
            memory_id=str(uuid.uuid4()),
            type=memory_type,
            timestamp=datetime.now().isoformat(),
            source=source,
            metadata=metadata or {},
            content=content
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika."""
        return {
            'memory_id': self.memory_id,
            'type': self.type,
            'timestamp': self.timestamp,
            'source': self.source,
            'metadata': self.metadata.copy(),
            'content': self.content.copy()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryRecord':
        """Tworzenie z słownika."""
        return cls(**data)
    
    def to_json(self) -> str:
        """Konwersja do JSON."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False, default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MemoryRecord':
        """Tworzenie z JSON."""
        return cls.from_dict(json.loads(json_str))


@dataclass
class MemoryQuery:
    """
    Kwerenda wyszukiwania w pamięci.
    
    Umożliwia filtrowanie rekordów po różnych kryteriach.
    """
    memory_type: Optional[str] = None       # Typ rekordu
    source: Optional[str] = None            # Źródło
    min_timestamp: Optional[str] = None     # Minimalna data
    max_timestamp: Optional[str] = None     # Maksymalna data
    content_key: Optional[str] = None       # Klucz w treści
    content_value: Optional[Any] = None      # Wartość w treści
    metadata_key: Optional[str] = None       # Klucz w metadanych
    metadata_value: Optional[Any] = None     # Wartość w metadanych
    limit: Optional[int] = None             # Limit wyników
    offset: Optional[int] = None            # Przesunięcie
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika."""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                result[key] = value
        return result


class BaseMemoryStore(ABC):
    """
    Abstrakcyjna klasa bazowa dla wszystkich składowych pamięci.
    
    Interfejs:
        save(record: MemoryRecord) -> str
        get(memory_id: str) -> Optional[MemoryRecord]
        find(query: MemoryQuery) -> List[MemoryRecord]
        delete(memory_id: str) -> bool
        all() -> List[MemoryRecord]
        count() -> int
        clear() -> None
    """
    
    def __init__(self, store_type: str = "base"):
        """
        Inicjalizacja składowej pamięci.
        
        Args:
            store_type: Typ składowej (model, agent, experiment)
        """
        self.store_type = store_type
        self._records: Dict[str, MemoryRecord] = {}  # memory_id -> MemoryRecord
        self._indexes: Dict[str, Dict[str, List[str]]] = {}  # index_name -> value -> [memory_ids]
        
        # Tworzenie indeksów
        self._init_indexes()
    
    def _init_indexes(self) -> None:
        """Inicjalizacja indeksów dla wydajnego wyszukiwania."""
        # Indeks po typie rekordu
        self._indexes['type'] = {}
        # Indeks po źródle
        self._indexes['source'] = {}
        # Indeks po dacie (tylko rok-miesiąc-dzień)
        self._indexes['date'] = {}
    
    def _add_to_indexes(self, record: MemoryRecord) -> None:
        """Dodanie rekordu do indeksów."""
        # Indeks po typie
        if record.type not in self._indexes['type']:
            self._indexes['type'][record.type] = []
        self._indexes['type'][record.type].append(record.memory_id)
        
        # Indeks po źródle
        if record.source not in self._indexes['source']:
            self._indexes['source'][record.source] = []
        self._indexes['source'][record.source].append(record.memory_id)
        
        # Indeks po dacie (tylko data bez czasu)
        date_key = record.timestamp.split('T')[0]
        if date_key not in self._indexes['date']:
            self._indexes['date'][date_key] = []
        self._indexes['date'][date_key].append(record.memory_id)
    
    def _remove_from_indexes(self, record: MemoryRecord) -> None:
        """Usunięcie rekordu z indeksów."""
        # Indeks po typie
        if record.type in self._indexes['type']:
            if record.memory_id in self._indexes['type'][record.type]:
                self._indexes['type'][record.type].remove(record.memory_id)
        
        # Indeks po źródle
        if record.source in self._indexes['source']:
            if record.memory_id in self._indexes['source'][record.source]:
                self._indexes['source'][record.source].remove(record.memory_id)
        
        # Indeks po dacie
        date_key = record.timestamp.split('T')[0]
        if date_key in self._indexes['date']:
            if record.memory_id in self._indexes['date'][date_key]:
                self._indexes['date'][date_key].remove(record.memory_id)
    
    @abstractmethod
    def _validate_record(self, record: MemoryRecord) -> bool:
        """
        Walidacja specyficzna dla danego typu składowej.
        
        Args:
            record: Rekord do walidacji
            
        Returns:
            True jeśli rekord jest poprawny
        """
        pass
    
    @abstractmethod
    def _get_memory_type(self) -> str:
        """
        Pobranie typu pamięci dla tej składowej.
        
        Returns:
            Typ pamięci (np. "model_memory", "agent_memory", "experiment_memory")
        """
        pass
    
    def save(self, record: Union[MemoryRecord, Dict[str, Any]]) -> str:
        """
        Zapis rekordu do pamięci.
        
        Args:
            record: MemoryRecord lub słownik
            
        Returns:
            memory_id zapisanego rekordu
            
        Raises:
            ValueError: Jeśli rekord jest niepoprawny
        """
        # Konwersja ze słownika jeśli potrzeba
        if isinstance(record, dict):
            record = MemoryRecord.from_dict(record)
        
        # Walidacja typu
        if not isinstance(record, MemoryRecord):
            raise ValueError(f"Record must be MemoryRecord or dict, got {type(record)}")
        
        # Ustawienie typu pamięci - TYLKO jeśli nie jest już ustawiony
        # to ważne dla rekordów system_memory, knowledge_record itp.
        # które są routowane do experiment_store, ale chcą zachować swój typ
        if not record.type or record.type == "":
            record.type = self._get_memory_type()
        
        # Walidacja specyficzna
        if not self._validate_record(record):
            raise ValueError(f"Record validation failed for {self.store_type} store")
        
        # Zapis
        self._records[record.memory_id] = record
        self._add_to_indexes(record)
        
        return record.memory_id
    
    def get(self, memory_id: str) -> Optional[MemoryRecord]:
        """
        Pobranie rekordu po ID.
        
        Args:
            memory_id: ID rekordu
            
        Returns:
            MemoryRecord lub None jeśli nie znaleziono
        """
        return self._records.get(memory_id)
    
    def find(self, query: Union[MemoryQuery, Dict[str, Any]] = None) -> List[MemoryRecord]:
        """
        Wyszukiwanie rekordów według kwerendy.
        
        Args:
            query: MemoryQuery lub słownik
            
        Returns:
            Lista pasujących MemoryRecord
        """
        if query is None:
            return list(self._records.values())
        
        # Konwersja ze słownika
        if isinstance(query, dict):
            query = MemoryQuery(**query)
        
        # Filtrowanie
        results = []
        for record in self._records.values():
            if self._matches_query(record, query):
                results.append(record)
        
        # Limit i offset
        if query.limit is not None:
            start = query.offset or 0
            end = start + query.limit
            results = results[start:end]
        
        return results
    
    def _matches_query(self, record: MemoryRecord, query: MemoryQuery) -> bool:
        """
        Sprawdzenie czy rekord pasuje do kwerendy.
        
        Args:
            record: Rekord do sprawdzenia
            query: Kwerenda
            
        Returns:
            True jeśli rekord pasuje
        """
        # Filtrowanie po typie
        if query.memory_type is not None and record.type != query.memory_type:
            return False
        
        # Filtrowanie po źródle
        if query.source is not None and record.source != query.source:
            return False
        
        # Filtrowanie po dacie (minimalna)
        if query.min_timestamp is not None:
            if record.timestamp < query.min_timestamp:
                return False
        
        # Filtrowanie po dacie (maksymalna)
        if query.max_timestamp is not None:
            if record.timestamp > query.max_timestamp:
                return False
        
        # Filtrowanie po kluczu w treści
        if query.content_key is not None:
            if query.content_key not in record.content:
                return False
            if query.content_value is not None and record.content[query.content_key] != query.content_value:
                return False
        
        # Filtrowanie po kluczu w metadanych
        if query.metadata_key is not None:
            if query.metadata_key not in record.metadata:
                return False
            if query.metadata_value is not None and record.metadata[query.metadata_key] != query.metadata_value:
                return False
        
        return True
    
    def delete(self, memory_id: str) -> bool:
        """
        Usunięcie rekordu z pamięci.
        
        Args:
            memory_id: ID rekordu
            
        Returns:
            True jeśli usunięto, False jeśli nie znaleziono
        """
        if memory_id not in self._records:
            return False
        
        record = self._records[memory_id]
        self._remove_from_indexes(record)
        del self._records[memory_id]
        
        return True
    
    def all(self) -> List[MemoryRecord]:
        """
        Pobranie wszystkich rekordów.
        
        Returns:
            Lista wszystkich MemoryRecord
        """
        return list(self._records.values())
    
    def count(self) -> int:
        """
        Liczba rekordów w pamięci.
        
        Returns:
            Liczba rekordów
        """
        return len(self._records)
    
    def clear(self) -> None:
        """Wyczyszczenie pamięci."""
        self._records.clear()
        self._init_indexes()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Pobranie statystyk pamięci.
        
        Returns:
            Słownik ze statystykami
        """
        return {
            'store_type': self.store_type,
            'total_records': self.count(),
            'types': {k: len(v) for k, v in self._indexes.get('type', {}).items()},
            'sources': {k: len(v) for k, v in self._indexes.get('source', {}).items()},
            'dates': list(self._indexes.get('date', {}).keys())
        }
    
    def get_by_type(self, memory_type: str) -> List[MemoryRecord]:
        """
        Pobranie rekordów danego typu.
        
        Args:
            memory_type: Typ rekordu
            
        Returns:
            Lista rekordów
        """
        memory_ids = self._indexes.get('type', {}).get(memory_type, [])
        return [self._records[mid] for mid in memory_ids if mid in self._records]
    
    def get_by_source(self, source: str) -> List[MemoryRecord]:
        """
        Pobranie rekordów z danego źródła.
        
        Args:
            source: Źródło
            
        Returns:
            Lista rekordów
        """
        memory_ids = self._indexes.get('source', {}).get(source, [])
        return [self._records[mid] for mid in memory_ids if mid in self._records]
    
    def get_by_date(self, date_str: str) -> List[MemoryRecord]:
        """
        Pobranie rekordów z danego dnia.
        
        Args:
            date_str: Data w formacie YYYY-MM-DD
            
        Returns:
            Lista rekordów
        """
        memory_ids = self._indexes.get('date', {}).get(date_str, [])
        return [self._records[mid] for mid in memory_ids if mid in self._records]
    
    def save_batch(self, records: List[Union[MemoryRecord, Dict[str, Any]]]) -> List[str]:
        """
        Zapis wielu rekordów naraz.
        
        Args:
            records: Lista rekordów
            
        Returns:
            Lista memory_id zapisanych rekordów
        """
        saved_ids = []
        for record in records:
            try:
                memory_id = self.save(record)
                saved_ids.append(memory_id)
            except Exception:
                continue
        return saved_ids
    
    def export_to_list(self) -> List[Dict[str, Any]]:
        """
        Eksport wszystkich rekordów do listy słowników.
        
        Returns:
            Lista rekordów jako słowników
        """
        return [record.to_dict() for record in self._records.values()]
    
    def import_from_list(self, data: List[Dict[str, Any]]) -> List[str]:
        """
        Import rekordów z listy słowników.
        
        Args:
            data: Lista rekordów jako słowników
            
        Returns:
            Lista memory_id zaimportowanych rekordów
        """
        return self.save_batch([MemoryRecord.from_dict(d) for d in data])
