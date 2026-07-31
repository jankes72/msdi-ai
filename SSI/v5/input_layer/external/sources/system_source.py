"""
SSI V5 - External Input Layer - System Source
Handler zrodla danych systemowych

Odpowiedzialnosc:
- Zbieranie komunikatow systemowych
- Monitorowanie statusow systemu
- Pakowanie danych w SystemMessages

Wersja: 1.0
Data: 2026-07-31
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..source_types import SourceType, ExternalStatus
from ..external_models import (
    SystemMessages, SystemEvent, SystemStatus,
    LogLevel, SystemStatusType,
    create_system_event, create_system_status
)

logger = logging.getLogger(__name__)


class SystemSource:
    """
    Handler zrodla danych systemowych.
    
    Odpowiada za:
    - Zbieranie zdarzen systemowych
    - Monitorowanie statusow systemu
    - Zbieranie logow systemowych
    - Pakowanie danych w SystemMessages
    - Walidacja zebranych danych
    """
    
    def __init__(self, source_name: str = "system"):
        """
        Inicjalizacja zrodla systemowego.
        
        Args:
            source_name: Nazwa zrodla (dla logow)
        """
        self.source_name = source_name
        self.source_type = SourceType.SYSTEM
        
        self._events: List[SystemEvent] = []
        self._statuses: List[SystemStatus] = []
        self._logs: List[Dict[str, Any]] = []
        self._status = ExternalStatus.PENDING
        self._timestamp = None
        self._metadata: Dict[str, Any] = {}
        
        logger.info(f"SystemSource zainicjowany: {self.source_name}")
    
    def add_event(
        self,
        event_id: str,
        event_type: str,
        component: str,
        message: str,
        log_level: LogLevel = LogLevel.INFO,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SystemEvent:
        """
        Dodaje zdarzenie systemowe.
        
        Args:
            event_id: Unikalny identyfikator zdarzenia
            event_type: Typ zdarzenia
            component: Komponent systemu
            message: Tresc zdarzenia
            log_level: Poziom logu
            timestamp: Data zdarzenia (domyslnie teraz)
            metadata: Dodatkowe metadane
            
        Returns:
            Utworzony SystemEvent
        """
        event = create_system_event(
            event_id, event_type, component, message, log_level
        )
        if timestamp:
            event.timestamp = timestamp
        if metadata:
            event.metadata.update(metadata)
        
        self._events.append(event)
        logger.debug(f"Dodano zdarzenie systemowe: {event_type} - {component}: {message[:50]}...")
        return event
    
    def add_status(
        self,
        status_id: str,
        status_type: SystemStatusType,
        message: str = "",
        component: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SystemStatus:
        """
        Dodaje status systemowy.
        
        Args:
            status_id: Unikalny identyfikator statusu
            status_type: Typ statusu
            message: Tresc statusu
            component: Komponent (opcjonalnie)
            timestamp: Data statusu (domyslnie teraz)
            metadata: Dodatkowe metadane
            
        Returns:
            Utworzony SystemStatus
        """
        status = create_system_status(
            status_id, status_type, message, component
        )
        if timestamp:
            status.timestamp = timestamp
        if metadata:
            status.metadata.update(metadata)
        
        self._statuses.append(status)
        logger.debug(f"Dodano status systemowy: {status_type.value} - {message[:50]}...")
        return status
    
    def add_log(
        self,
        log: Dict[str, Any]
    ) -> None:
        """
        Dodaje log systemowy.
        
        Args:
            log: Slownik z danymi logu
        """
        self._logs.append(log)
        log_level = log.get("level", "unknown")
        log_message = log.get("message", "")
        logger.debug(f"Dodano log systemowy: [{log_level}] {log_message[:50]}...")
    
    def add_info_event(
        self,
        event_id: str,
        event_type: str,
        component: str,
        message: str,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SystemEvent:
        """
        Dodaje zdarzenie informacyjne (skrot do add_event z LogLevel.INFO).
        
        Args:
            event_id: Unikalny identyfikator zdarzenia
            event_type: Typ zdarzenia
            component: Komponent systemu
            message: Tresc zdarzenia
            timestamp: Data zdarzenia (domyslnie teraz)
            metadata: Dodatkowe metadane
            
        Returns:
            Utworzony SystemEvent
        """
        return self.add_event(
            event_id, event_type, component, message,
            LogLevel.INFO, timestamp, metadata
        )
    
    def add_warning_event(
        self,
        event_id: str,
        event_type: str,
        component: str,
        message: str,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SystemEvent:
        """
        Dodaje zdarzenie ostrzegawcze (skrot do add_event z LogLevel.WARNING).
        
        Args:
            event_id: Unikalny identyfikator zdarzenia
            event_type: Typ zdarzenia
            component: Komponent systemu
            message: Tresc zdarzenia
            timestamp: Data zdarzenia (domyslnie teraz)
            metadata: Dodatkowe metadane
            
        Returns:
            Utworzony SystemEvent
        """
        return self.add_event(
            event_id, event_type, component, message,
            LogLevel.WARNING, timestamp, metadata
        )
    
    def add_error_event(
        self,
        event_id: str,
        event_type: str,
        component: str,
        message: str,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SystemEvent:
        """
        Dodaje zdarzenie bledne (skrot do add_event z LogLevel.ERROR).
        
        Args:
            event_id: Unikalny identyfikator zdarzenia
            event_type: Typ zdarzenia
            component: Komponent systemu
            message: Tresc zdarzenia
            timestamp: Data zdarzenia (domyslnie teraz)
            metadata: Dodatkowe metadane
            
        Returns:
            Utworzony SystemEvent
        """
        return self.add_event(
            event_id, event_type, component, message,
            LogLevel.ERROR, timestamp, metadata
        )
    
    def add_critical_event(
        self,
        event_id: str,
        event_type: str,
        component: str,
        message: str,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SystemEvent:
        """
        Dodaje zdarzenie krytyczne (skrot do add_event z LogLevel.CRITICAL).
        
        Args:
            event_id: Unikalny identyfikator zdarzenia
            event_type: Typ zdarzenia
            component: Komponent systemu
            message: Tresc zdarzenia
            timestamp: Data zdarzenia (domyslnie teraz)
            metadata: Dodatkowe metadane
            
        Returns:
            Utworzony SystemEvent
        """
        return self.add_event(
            event_id, event_type, component, message,
            LogLevel.CRITICAL, timestamp, metadata
        )
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Ustawia metadane.
        
        Args:
            key: Klucz metadanych
            value: Wartosc metadanych
        """
        self._metadata[key] = value
    
    def collect(self) -> SystemMessages:
        """
        Zbiera wszystkie zebrane dane i zwraca je jako SystemMessages.
        
        Returns:
            SystemMessages zawierajacy wszystkie zebrane dane
        """
        self._timestamp = datetime.now()
        self._status = ExternalStatus.COMPLETED
        
        sys_msgs = SystemMessages(
            source_type=SourceType.SYSTEM,
            events=self._events.copy(),
            statuses=self._statuses.copy(),
            logs=self._logs.copy(),
            timestamp=self._timestamp,
            status=self._status,
            metadata=self._metadata.copy()
        )
        
        logger.info(f"Zebrano dane systemowe: {len(sys_msgs.events)} zdarzen, "
                    f"{len(sys_msgs.statuses)} statusow, "
                    f"{len(sys_msgs.logs)} logow")
        
        return sys_msgs
    
    def clear(self) -> None:
        """Czysci zebrane dane."""
        self._events.clear()
        self._statuses.clear()
        self._logs.clear()
        self._status = ExternalStatus.PENDING
        self._timestamp = None
        self._metadata.clear()
        logger.info(f"Wyczyszczono dane systemowe: {self.source_name}")
    
    def get_status(self) -> ExternalStatus:
        """Zwraca aktualny status zrodla."""
        return self._status
    
    def set_status(self, status: ExternalStatus) -> None:
        """Ustawia status zrodla."""
        self._status = status
        logger.debug(f"Status SystemSource ustawiony na: {status}")
    
    def get_data_count(self) -> Dict[str, int]:
        """
        Zwraca liczbe zebranych elementow.
        
        Returns:
            Slownik z liczbami elementow
        """
        return {
            "events": len(self._events),
            "statuses": len(self._statuses),
            "logs": len(self._logs)
        }
    
    @property
    def has_data(self) -> bool:
        """Czy zrodlo ma jakiekolwiek dane?"""
        return bool(
            self._events or
            self._statuses or
            self._logs
        )
    
    def get_errors(self) -> List[SystemEvent]:
        """
        Zwraca bledy i zdarzenia krytyczne.
        
        Returns:
            Lista zdarzen blednych i krytycznych
        """
        return [
            evt for evt in self._events
            if evt.log_level in [LogLevel.ERROR, LogLevel.CRITICAL]
        ]
    
    def get_warnings(self) -> List[SystemEvent]:
        """
        Zwraca zdarzenia ostrzegawcze.
        
        Returns:
            Lista zdarzen ostrzegawczych
        """
        return [
            evt for evt in self._events
            if evt.log_level == LogLevel.WARNING
        ]
    
    def get_events_by_component(self, component: str) -> List[SystemEvent]:
        """
        Zwraca zdarzenia z konkretnego komponentu.
        
        Args:
            component: Nazwa komponentu
            
        Returns:
            Lista zdarzen z komponentu
        """
        return [evt for evt in self._events if evt.component == component]
    
    def get_events_by_type(self, event_type: str) -> List[SystemEvent]:
        """
        Zwraca zdarzenia danego typu.
        
        Args:
            event_type: Typ zdarzenia
            
        Returns:
            Lista zdarzen danego typu
        """
        return [evt for evt in self._events if evt.event_type == event_type]
    
    def get_current_status(self, component: Optional[str] = None) -> Optional[SystemStatus]:
        """
        Zwraca najnowszy status dla komponentu.
        
        Args:
            component: Nazwa komponentu (opcjonalnie)
            
        Returns:
            Najnowszy status lub None
        """
        if component:
            component_statuses = [
                st for st in self._statuses if st.component == component
            ]
        else:
            component_statuses = self._statuses
        
        if not component_statuses:
            return None
        
        # Zwróc status z najnowsza data
        return max(component_statuses, key=lambda x: x.timestamp)
    
    def validate(self) -> bool:
        """
        Waliduje zebrane dane.
        
        Returns:
            True jeśli dane sa poprawne
        """
        # Sprawdz czy sa jakies dane
        if not self.has_data:
            logger.warning(f"Brak danych systemowych: {self.source_name}")
            self._status = ExternalStatus.INVALID
            return False
        
        # Sprawdz poprawnosc zdarzen
        for evt in self._events:
            if not evt.event_id:
                logger.error("Zdarzenie bez event_id")
                self._status = ExternalStatus.INVALID
                return False
            if not evt.event_type:
                logger.error(f"Zdarzenie bez event_type: {evt.event_id}")
                self._status = ExternalStatus.INVALID
                return False
            if not evt.component:
                logger.error(f"Zdarzenie bez component: {evt.event_id}")
                self._status = ExternalStatus.INVALID
                return False
            if not evt.message:
                logger.error(f"Zdarzenie bez message: {evt.event_id}")
                self._status = ExternalStatus.INVALID
                return False
        
        # Sprawdz poprawnosc statusow
        for st in self._statuses:
            if not st.status_id:
                logger.error("Status bez status_id")
                self._status = ExternalStatus.INVALID
                return False
        
        self._status = ExternalStatus.VALIDATED
        return True
    
    def get_component_stats(self) -> Dict[str, Dict[str, int]]:
        """
        Zwraca statystyki dla kazdego komponentu.
        
        Returns:
            Slownik ze statystykami na komponent:
            {
                component: {
                    "events": int,
                    "errors": int,
                    "warnings": int,
                    "status_changes": int
                }
            }
        """
        stats = {}
        
        #group events by component
        for evt in self._events:
            if evt.component not in stats:
                stats[evt.component] = {
                    "events": 0,
                    "errors": 0,
                    "warnings": 0,
                    "status_changes": 0
                }
            stats[evt.component]["events"] += 1
            
            if evt.log_level in [LogLevel.ERROR, LogLevel.CRITICAL]:
                stats[evt.component]["errors"] += 1
            elif evt.log_level == LogLevel.WARNING:
                stats[evt.component]["warnings"] += 1
        
        return stats
    
    def __repr__(self) -> str:
        counts = self.get_data_count()
        return (f"SystemSource(name='{self.source_name}', "
                f"events={counts['events']}, "
                f"statuses={counts['statuses']}, "
                f"logs={counts['logs']})")
