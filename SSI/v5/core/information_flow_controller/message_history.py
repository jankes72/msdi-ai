"""
SSI V5 - Message History

Modul odpowiedzialny za przechowywanie i zarządzanie historia wiadomosci.
Zapewnia persystencje, indeksowanie i wyszukiwanie wiadomosci.

Wersja: 2.0.0
Data: 2026-08-01
"""

import json
import os
import threading
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path

from SSI.v5.core.information_flow_controller.message_models import (
    SSIMessage,
    MessageStatus,
    ModuleIdentifier
)


# Konfiguracja logowania
logger = logging.getLogger(__name__)


@dataclass
class HistoryConfig:
    """Konfiguracja historii wiadomosci."""
    storage_dir: str = "SSI/v5/core/information_flow_controller/history"
    max_messages: int = 100000  # Maksymalna liczba wiadomosci w pamięci
    max_file_size_mb: int = 100  # Maksymalny rozmiar pliku w MB
    retention_days: int = 30  # Okres przechowywania wiadomosci (dni)
    enable_persistence: bool = True  # Wlacz zapisy na dysk
    auto_cleanup: bool = True  # Automatyczne czyszczenie starych wiadomosci
    
    def ensure_storage_dir(self) -> None:
        """Upewnienie sie ze katalog na historia istnieje."""
        Path(self.storage_dir).mkdir(parents=True, exist_ok=True)


@dataclass
class MessageRecord:
    """Rekord wiadomosci w historii."""
    message: SSIMessage
    status: MessageStatus = MessageStatus.CREATED
    received_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    processing_time_ms: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        return {
            'message': self.message.to_dict(),
            'status': self.status.value,
            'received_at': self.received_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'processing_time_ms': self.processing_time_ms,
            'error': self.error,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MessageRecord':
        """Tworzenie z slownika."""
        message_data = data.get('message', {})
        message = SSIMessage.from_dict(message_data)
        
        return cls(
            message=message,
            status=MessageStatus(data.get('status', 'created')),
            received_at=datetime.fromisoformat(data.get('received_at', datetime.now().isoformat())),
            processed_at=datetime.fromisoformat(data['processed_at']) if data.get('processed_at') else None,
            processing_time_ms=data.get('processing_time_ms', 0.0),
            error=data.get('error'),
            metadata=data.get('metadata', {})
        )


class MessageHistory:
    """
    Historia wiadomosci SSI V5.
    
    Odpowiedzialnosc:
    - Przechowywanie wiadomosci w pamięci
    - Persystencja na dysku
    - Indeksowanie i wyszukiwanie
    - Zarządzanie cyklem zycia wiadomosci
    """
    
    def __init__(self, config: HistoryConfig = None):
        self.config = config or HistoryConfig()
        self._messages: Dict[str, MessageRecord] = {}  # message_id -> MessageRecord
        self._session_index: Dict[str, List[str]] = {}  # session_id -> [message_ids]
        self._cycle_index: Dict[str, List[str]] = {}  # cycle_id -> [message_ids]
        self._correlation_index: Dict[str, List[str]] = {}  # correlation_id -> [message_ids]
        self._source_index: Dict[str, List[str]] = {}  # source -> [message_ids]
        self._target_index: Dict[str, List[str]] = {}  # target -> [message_ids]
        self._type_index: Dict[str, List[str]] = {}  # process_type -> [message_ids]
        self._time_index: Dict[str, List[str]] = {}  # data (YYYY-MM-DD) -> [message_ids]
        
        self._lock = threading.RLock()
        self._initialized = False
        
        # Inicjalizacja
        if self.config.enable_persistence:
            self.config.ensure_storage_dir()
        
    def initialize(self) -> None:
        """Inicjalizacja historii (zaladowanie z dysku)."""
        if self._initialized:
            return
        
        self._initialized = True
        
        if self.config.enable_persistence:
            self._load_from_disk()
        
        logger.info("MessageHistory zainicjalizowany")
    
    def store_message(
        self,
        message: SSIMessage,
        status: MessageStatus = MessageStatus.CREATED,
        processed_at: datetime = None,
        processing_time_ms: float = 0.0,
        error: str = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Zapisanie wiadomosci w historii.
        
        Args:
            message: Wiadomosc do zapisania
            status: Status wiadomosci
            processed_at: Data przetworzenia
            processing_time_ms: Czas przetwarzania w ms
            error: Blad (jesli wystapil)
            metadata: Dodatkowe metadane
        
        Returns:
            str: ID zapisanej wiadomosci
        """
        with self._lock:
            message_id = message.message_id
            
            # Utworzenie rekordu
            record = MessageRecord(
                message=message,
                status=status,
                received_at=datetime.now(),
                processed_at=processed_at,
                processing_time_ms=processing_time_ms,
                error=error,
                metadata=metadata or {}
            )
            
            # Zapisanie w glownym storage
            self._messages[message_id] = record
            
            # Indeksowanie
            self._index_message(record)
            
            # Persystencja
            if self.config.enable_persistence:
                self._save_to_disk(record)
            
            # Kontrola rozmiaru
            self._check_size_limits()
            
            logger.debug(f"Zapisano wiadomosc: {message_id}")
            return message_id
    
    def _index_message(self, record: MessageRecord) -> None:
        """Indeksowanie wiadomosci."""
        message = record.message
        message_id = message.message_id
        
        # Indeksy sesji i cyklu
        if message.session_id not in self._session_index:
            self._session_index[message.session_id] = []
        self._session_index[message.session_id].append(message_id)
        
        if message.cycle_id not in self._cycle_index:
            self._cycle_index[message.cycle_id] = []
        self._cycle_index[message.cycle_id].append(message_id)
        
        # Indeks korelacji
        if message.correlation_id:
            if message.correlation_id not in self._correlation_index:
                self._correlation_index[message.correlation_id] = []
            self._correlation_index[message.correlation_id].append(message_id)
        
        # Indeksy source i target
        source_key = str(message.source)
        if source_key not in self._source_index:
            self._source_index[source_key] = []
        self._source_index[source_key].append(message_id)
        
        target_key = str(message.target)
        if target_key not in self._target_index:
            self._target_index[target_key] = []
        self._target_index[target_key].append(message_id)
        
        # Indeks typu procesu
        process_type = message.process_type.value if hasattr(message.process_type, 'value') else message.process_type
        if process_type not in self._type_index:
            self._type_index[process_type] = []
        self._type_index[process_type].append(message_id)
        
        # Indeks czasowy
        date_key = message.timestamp.strftime('%Y-%m-%d')
        if date_key not in self._time_index:
            self._time_index[date_key] = []
        self._time_index[date_key].append(message_id)
    
    def get_message(self, message_id: str) -> Optional[MessageRecord]:
        """Pobranie wiadomosci po ID."""
        with self._lock:
            return self._messages.get(message_id)
    
    def get_messages_by_session(self, session_id: str) -> List[MessageRecord]:
        """Pobranie wiadomosci po session_id."""
        with self._lock:
            message_ids = self._session_index.get(session_id, [])
            return [self._messages[msg_id] for msg_id in message_ids if msg_id in self._messages]
    
    def get_messages_by_cycle(self, cycle_id: str) -> List[MessageRecord]:
        """Pobranie wiadomosci po cycle_id."""
        with self._lock:
            message_ids = self._cycle_index.get(cycle_id, [])
            return [self._messages[msg_id] for msg_id in message_ids if msg_id in self._messages]
    
    def get_messages_by_correlation(self, correlation_id: str) -> List[MessageRecord]:
        """Pobranie wiadomosci powiazanych korelacja."""
        with self._lock:
            message_ids = self._correlation_index.get(correlation_id, [])
            return [self._messages[msg_id] for msg_id in message_ids if msg_id in self._messages]
    
    def get_conversation(self, correlation_id: str) -> List[MessageRecord]:
        """Pobranie calej konwersacji (lancuch wiadomosci)."""
        return self.get_messages_by_correlation(correlation_id)
    
    def query_messages(
        self,
        source: str = None,
        target: str = None,
        process_type: str = None,
        session_id: str = None,
        cycle_id: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        status: MessageStatus = None,
        limit: int = 1000
    ) -> List[MessageRecord]:
        """
        Wyszukiwanie wiadomosci po krytyeriach.
        
        Args:
            source: Zrodlo wiadomosci
            target: Cel wiadomosci
            process_type: Typ procesu
            session_id: ID sesji
            cycle_id: ID cyklu
            start_date: Data poczatkowa
            end_date: Data koncowa
            status: Status wiadomosci
            limit: Maksymalna liczba wynikow
        
        Returns:
            List[MessageRecord]: Lista pasujacych wiadomosci
        """
        with self._lock:
            candidate_ids = set()
            
            # Filtr po source
            if source:
                source_ids = set(self._source_index.get(source, []))
                candidate_ids = candidate_ids.intersection(source_ids) if candidate_ids else source_ids
            
            # Filtr po target
            if target:
                target_ids = set(self._target_index.get(target, []))
                candidate_ids = candidate_ids.intersection(target_ids) if candidate_ids else target_ids
            
            # Filtr po process_type
            if process_type:
                type_ids = set(self._type_index.get(process_type, []))
                candidate_ids = candidate_ids.intersection(type_ids) if candidate_ids else type_ids
            
            # Filtr po session_id
            if session_id:
                session_ids = set(self._session_index.get(session_id, []))
                candidate_ids = candidate_ids.intersection(session_ids) if candidate_ids else session_ids
            
            # Filtr po cycle_id
            if cycle_id:
                cycle_ids = set(self._cycle_index.get(cycle_id, []))
                candidate_ids = candidate_ids.intersection(cycle_ids) if candidate_ids else cycle_ids
            
            # Filtr po dacie
            if start_date or end_date:
                date_filter_ids = set()
                if start_date and end_date:
                    for date_key, ids in self._time_index.items():
                        try:
                            date = datetime.strptime(date_key, '%Y-%m-%d')
                            if start_date <= date <= end_date:
                                date_filter_ids.update(ids)
                        except ValueError:
                            pass
                elif start_date:
                    for date_key, ids in self._time_index.items():
                        try:
                            date = datetime.strptime(date_key, '%Y-%m-%d')
                            if date >= start_date:
                                date_filter_ids.update(ids)
                        except ValueError:
                            pass
                elif end_date:
                    for date_key, ids in self._time_index.items():
                        try:
                            date = datetime.strptime(date_key, '%Y-%m-%d')
                            if date <= end_date:
                                date_filter_ids.update(ids)
                        except ValueError:
                            pass
                
                candidate_ids = candidate_ids.intersection(date_filter_ids) if candidate_ids else date_filter_ids
            
            # Filtr po statusie (wymaga sprawdzenia każdej wiadomosci)
            if status:
                filtered_records = []
                for msg_id in candidate_ids:
                    if msg_id in self._messages:
                        record = self._messages[msg_id]
                        if record.status == status:
                            filtered_records.append(record)
                return filtered_records[:limit]
            
            # Zwracanie wynikow
            results = []
            for msg_id in candidate_ids:
                if msg_id in self._messages:
                    results.append(self._messages[msg_id])
            
            return results[:limit]
    
    def get_message_count(self) -> int:
        """Pobranie liczby wiadomosci w historii."""
        with self._lock:
            return len(self._messages)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Pobranie statystyk historii."""
        with self._lock:
            return {
                'total_messages': len(self._messages),
                'sessions_count': len(self._session_index),
                'cycles_count': len(self._cycle_index),
                'correlations_count': len(self._correlation_index),
                'unique_sources': len(self._source_index),
                'unique_targets': len(self._target_index),
                'unique_types': len(self._type_index),
                'date_range': self._get_date_range()
            }
    
    def _get_date_range(self) -> Dict[str, str]:
        """Pobranie zakresu dat."""
        dates = []
        for date_str in self._time_index.keys():
            try:
                dates.append(datetime.strptime(date_str, '%Y-%m-%d'))
            except ValueError:
                pass
        
        if not dates:
            return {'first': None, 'last': None}
        
        return {
            'first': min(dates).strftime('%Y-%m-%d'),
            'last': max(dates).strftime('%Y-%m-%d')
        }
    
    def _save_to_disk(self, record: MessageRecord) -> None:
        """Zapisanie rekordu na dysk."""
        try:
            file_path = self._get_message_file_path(record.message.message_id)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(record.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Blad zapisu wiadomosci {record.message.message_id} na dysk: {e}")
    
    def _load_from_disk(self) -> None:
        """Zaladowanie wiadomosci z dysku."""
        try:
            storage_path = Path(self.config.storage_dir)
            if not storage_path.exists():
                return
            
            for file_path in storage_path.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        record = MessageRecord.from_dict(data)
                        self._messages[record.message.message_id] = record
                        self._index_message(record)
                except Exception as e:
                    logger.error(f"Blad ladowania wiadomosci z {file_path}: {e}")
        except Exception as e:
            logger.error(f"Blad ladowania historii z dysku: {e}")
    
    def _get_message_file_path(self, message_id: str) -> str:
        """Generowanie sciezki do pliku wiadomosci."""
        # Uzycie pierwszych 2 znakow jako podkatalogu
        prefix = message_id[:2]
        prefix_dir = Path(self.config.storage_dir) / prefix
        prefix_dir.mkdir(parents=True, exist_ok=True)
        return str(prefix_dir / f"{message_id}.json")
    
    def _check_size_limits(self) -> None:
        """Sprawdzenie limitow rozmiaru."""
        with self._lock:
            # Sprawdzenie limitu wiadomosci w pamięci
            if len(self._messages) > self.config.max_messages:
                self._cleanup_old_messages()
    
    def _cleanup_old_messages(self) -> None:
        """Czyszczenie starych wiadomosci."""
        with self._lock:
            if not self.config.auto_cleanup:
                return
            
            # Usuwanie starych wiadomosci
            cutoff_date = datetime.now() - timedelta(days=self.config.retention_days)
            messages_to_remove = []
            
            for message_id, record in self._messages.items():
                if record.received_at < cutoff_date:
                    messages_to_remove.append(message_id)
            
            for message_id in messages_to_remove:
                self._remove_from_indexes(message_id)
                
                # Usuniecie pliku
                if self.config.enable_persistence:
                    try:
                        file_path = self._get_message_file_path(message_id)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                    except Exception as e:
                        logger.error(f"Blad usuwania pliku wiadomosci {message_id}: {e}")
            
            logger.info(f"Usunieto {len(messages_to_remove)} starych wiadomosci")
    
    def _remove_from_indexes(self, message_id: str) -> None:
        """Usuniecie wiadomosci z indeksow."""
        if message_id not in self._messages:
            return
        
        message = self._messages[message_id].message
        
        # Usuniecie z indeksow
        if message.session_id in self._session_index:
            if message_id in self._session_index[message.session_id]:
                self._session_index[message.session_id].remove(message_id)
        
        if message.cycle_id in self._cycle_index:
            if message_id in self._cycle_index[message.cycle_id]:
                self._cycle_index[message.cycle_id].remove(message_id)
        
        if message.correlation_id in self._correlation_index:
            if message_id in self._correlation_index[message.correlation_id]:
                self._correlation_index[message.correlation_id].remove(message_id)
        
        source_key = str(message.source)
        if source_key in self._source_index:
            if message_id in self._source_index[source_key]:
                self._source_index[source_key].remove(message_id)
        
        target_key = str(message.target)
        if target_key in self._target_index:
            if message_id in self._target_index[target_key]:
                self._target_index[target_key].remove(message_id)
        
        process_type = message.process_type.value if hasattr(message.process_type, 'value') else message.process_type
        if process_type in self._type_index:
            if message_id in self._type_index[process_type]:
                self._type_index[process_type].remove(message_id)
        
        date_key = message.timestamp.strftime('%Y-%m-%d')
        if date_key in self._time_index:
            if message_id in self._time_index[date_key]:
                self._time_index[date_key].remove(message_id)
        
        # Usuniecie z glównego storage
        if message_id in self._messages:
            del self._messages[message_id]
    
    def clear_history(self) -> None:
        """Wyczyszczenie calej historii."""
        with self._lock:
            self._messages.clear()
            self._session_index.clear()
            self._cycle_index.clear()
            self._correlation_index.clear()
            self._source_index.clear()
            self._target_index.clear()
            self._type_index.clear()
            self._time_index.clear()
            
            # Usuniecie plikow
            if self.config.enable_persistence:
                try:
                    storage_path = Path(self.config.storage_dir)
                    if storage_path.exists():
                        for file_path in storage_path.glob("*.json"):
                            file_path.unlink()
                except Exception as e:
                    logger.error(f"Blad usuwania plikow historii: {e}")
        
        logger.info("Wyczyszczono cala historia wiadomosci")


# Instancja globalna
message_history = MessageHistory()


def get_history() -> MessageHistory:
    """Pobranie globalnej instancji historii."""
    return message_history