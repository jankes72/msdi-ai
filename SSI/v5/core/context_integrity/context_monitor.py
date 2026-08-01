"""
SSI V5 - Context Monitor

Modul odpowiedzialny za monitorowanie kontekstu systemowego.
Sledzi zmiany kontekstu, wykrywa anomalie i generuje alerty.

Wersja: 2.0.0
Data: 2026-08-01
"""

import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from queue import Queue

from SSI.v5.core.information_flow_controller.message_models import (
    SSIMessage,
    SystemStateSnapshot
)
from SSI.v5.core.information_flow_controller.context_manager import (
    ContextManager,
    ContextSnapshot,
    get_context_manager
)

# Konfiguracja logowania
logger = logging.getLogger(__name__)


class ContextEventType(Enum):
    """Typy zdarzen kontekstowych."""
    SESSION_STARTED = "session_started"          # Rozpoczeta sesja
    SESSION_ENDED = "session_ended"              # Zakonczona sesja
    SESSION_CHANGED = "session_changed"          # Zmiana aktywnej sesji
    CYCLE_STARTED = "cycle_started"              # Rozpoczety cykl
    CYCLE_ENDED = "cycle_ended"                  # Zakonczony cykl
    CYCLE_CHANGED = "cycle_changed"              # Zmiana aktywnego cyklu
    AGENT_ACTIVE = "agent_active"                 # Aktywny agent
    AGENT_CHANGED = "agent_changed"              # Zmiana aktywnego agenta
    MODEL_ACTIVE = "model_active"                 # Aktywny model
    MODEL_CHANGED = "model_changed"              # Zmiana aktywnego modelu
    SYSTEM_STATUS_CHANGED = "system_status_changed"  # Zmiana stanu systemu
    CONTENT_LOSS_DETECTED = "content_loss_detected"  # Wykryto utre kontekstu
    INTEGRITY_VIOLATION = "integrity_violation"  # Naruszenie integralnosci
    ANOMALY_DETECTED = "anomaly_detected"        # Wykryto anomalie


class MonitorStatus(Enum):
    """Status monitora."""
    ACTIVE = "active"            # Monitor aktywny
    PAUSED = "paused"            # Monitor wstrzymany
    STOPPED = "stopped"          # Monitor zatrzymany


@dataclass
class ContextEvent:
    """Zdarzenie kontekstowe."""
    event_type: ContextEventType
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: Optional[str] = None
    cycle_id: Optional[str] = None
    agent_id: Optional[str] = None
    model_id: Optional[str] = None
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    severity: str = "info"  # info, warning, error, critical
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        return {
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'session_id': self.session_id,
            'cycle_id': self.cycle_id,
            'agent_id': self.agent_id,
            'model_id': self.model_id,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'severity': self.severity,
            'message': self.message,
            'metadata': self.metadata
        }
    
    def __str__(self) -> str:
        return f"[{self.event_type.value}] {self.message} (severity: {self.severity})"


@dataclass
class ContextAnomaly:
    """Anomalia kontekstowa."""
    anomaly_id: str
    anomaly_type: str
    description: str
    severity: str = "warning"  # warning, error, critical
    detected_at: datetime = field(default_factory=datetime.now)
    context_snapshot: Optional[ContextSnapshot] = None
    related_messages: List[str] = field(default_factory=list)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolution: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        return {
            'anomaly_id': self.anomaly_id,
            'anomaly_type': self.anomaly_type,
            'description': self.description,
            'severity': self.severity,
            'detected_at': self.detected_at.isoformat(),
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolution': self.resolution,
            'related_messages': self.related_messages
        }
    
    def mark_resolved(self, resolution: str = "") -> None:
        """Oznaczenie anomalii jako rozwiiazanej."""
        self.resolved = True
        self.resolved_at = datetime.now()
        self.resolution = resolution


class AnomalyDetectionStrategy:
    """Strategia wykrywania anomalii."""
    
    @staticmethod
    def detect_frequent_session_changes(events: List[ContextEvent]) -> List[ContextAnomaly]:
        """Wykrywanie czestych zmian sesji."""
        anomalies = []
        
        session_changes = [e for e in events if e.event_type == ContextEventType.SESSION_CHANGED]
        
        if len(session_changes) > 10:  # Wiecej niz 10 zmian sesji
            # Grupowanie po session_id
            session_counts = {}
            for event in session_changes:
                if event.new_value:
                    session_counts[event.new_value] = session_counts.get(event.new_value, 0) + 1
            
            for session_id, count in session_counts.items():
                if count > 5:
                    anomalies.append(ContextAnomaly(
                        anomaly_id=f"ANOMALY_SESSION_{session_id}",
                        anomaly_type="frequent_session_switch",
                        description=f"Czeste przełączanie na sesje {session_id}: {count} razy",
                        severity="warning",
                        related_messages=[e.message for e in session_changes if e.new_value == session_id]
                    ))
        
        return anomalies
    
    @staticmethod
    def detect_frequent_cycle_changes(events: List[ContextEvent]) -> List[ContextAnomaly]:
        """Wykrywanie czestych zmian cyklu."""
        anomalies = []
        
        cycle_changes = [e for e in events if e.event_type == ContextEventType.CYCLE_CHANGED]
        
        if len(cycle_changes) > 20:  # Wiecej niz 20 zmian cyklu
            anomalies.append(ContextAnomaly(
                anomaly_id="ANOMALY_CYCLE_FREQUENT",
                anomaly_type="frequent_cycle_switch",
                description=f"Czeste zmiany cyklu: {len(cycle_changes)} razy",
                severity="warning"
            ))
        
        return anomalies
    
    @staticmethod
    def detect_simultaneous_models(events: List[ContextEvent]) -> List[ContextAnomaly]:
        """Wykrywanie wieloch aktywnych modeli (naruszenie zasady: TYLKO JEDEN MODEL naraz)."""
        anomalies = []
        
        model_events = [e for e in events if e.event_type in [ContextEventType.MODEL_ACTIVE, ContextEventType.MODEL_CHANGED]]
        
        active_models = set()
        model_timestamps = {}
        
        for event in sorted(model_events, key=lambda x: x.timestamp):
            if event.new_value:
                active_models.add(event.new_value)
                model_timestamps[event.new_value] = event.timestamp
            
            if event.event_type == ContextEventType.MODEL_CHANGED:
                if event.old_value:
                    active_models.discard(event.old_value)
        
        if len(active_models) > 1:
            # Wiecej niz jeden aktywny model - naruszenie zasady!
            models_list = ", ".join(active_models)
            anomalies.append(ContextAnomaly(
                anomaly_id="ANOMALY_MULTI_MODELS",
                anomaly_type="multiple_active_models",
                description=f"Naruszenie zasady: Aktywne modele: {models_list}",
                severity="critical",
                related_messages=[f"Model: {m} od {model_timestamps.get(m, 'N/A')}" for m in active_models]
            ))
        
        return anomalies


class AnomalyDetector:
    """Wykrywacz anomalii kontekstowych."""
    
    def __init__(self):
        """Inicjalizacja wykrywacza."""
        self._strategies: List[AnomalyDetectionStrategy] = []
        self._detected_anomalies: Dict[str, ContextAnomaly] = {}
        self._lock = threading.RLock()
        logger.info("AnomalyDetector zainicjalizowany")
    
    def register_strategy(self, strategy: AnomalyDetectionStrategy) -> None:
        """Rejestracja nowej strategii wykrywania."""
        self._strategies.append(strategy)
        logger.debug(f"Zarejestrowano strategie wykrywania anomalii: {strategy.__class__.__name__}")
    
    def detect_anomalies(self, events: List[ContextEvent]) -> List[ContextAnomaly]:
        """
        Wykrywanie anomalii w zdarzeniach.
        
        Args:
            events: Lista zdarzen doanalizy
            
        Returns:
            List[ContextAnomaly]: Lista wykrytych anomalii
        """
        anomalies = []
        
        with self._lock:
            # Uzycie wszystkich strategii
            for strategy in self._strategies:
                try:
                    strategy_anomalies = strategy.detect(events)
                    anomalies.extend(strategy_anomalies)
                except Exception as e:
                    logger.error(f"Blad podczas wykrywania anomalii strategia {strategy.__class__.__name__}: {e}")
            
            # Dedyplikacja
            unique_anomalies = {}
            for anomaly in anomalies:
                if anomaly.anomaly_id not in unique_anomalies:
                    unique_anomalies[anomaly.anomaly_id] = anomaly
            
            # Zapisanie wykrytych anomalii
            for anomaly_id, anomaly in unique_anomalies.items():
                self._detected_anomalies[anomaly_id] = anomaly
            
            return list(unique_anomalies.values())
    
    def get_anomaly(self, anomaly_id: str) -> Optional[ContextAnomaly]:
        """Pobranie anomalii po ID."""
        with self._lock:
            return self._detected_anomalies.get(anomaly_id)
    
    def get_all_anomalies(self) -> List[ContextAnomaly]:
        """Pobranie wszystkich anomalii."""
        with self._lock:
            return list(self._detected_anomalies.values())
    
    def get_unresolved_anomalies(self) -> List[ContextAnomaly]:
        """Pobranie nierozwiazanych anomalii."""
        with self._lock:
            return [a for a in self._detected_anomalies.values() if not a.resolved]
    
    def resolve_anomaly(self, anomaly_id: str, resolution: str = "") -> bool:
        """Rozwiazanie anomalii."""
        with self._lock:
            if anomaly_id in self._detected_anomalies:
                self._detected_anomalies[anomaly_id].mark_resolved(resolution)
                logger.info(f"Rozwiazano anomalie: {anomaly_id} - {resolution}")
                return True
            return False
    
    def clear_anomalies(self) -> None:
        """Wyczyszczenie wszystkich anomalii."""
        with self._lock:
            self._detected_anomalies.clear()
            logger.info("Wyczyszczono wszystkie anomalii")


class ContextMonitor:
    """
    Monitor kontekstu systemowego.
    
    Odpowiedzialnosc:
    - Sledzenie zmian kontekstu
    - Wykrywanie anomalii
    - Generowanie alertów
    - Monitorowanie stanu systemu
    
    Zasady:
    - reacción na zmiany w systemie
    - Sledzenie faktów i trendów
    """
    
    def __init__(self):
        """Inicjalizacja monitora."""
        self._status = MonitorStatus.STOPPED
        self._event_queue: Queue = Queue()
        self._events: List[ContextEvent] = []
        self._event_listeners: Dict[ContextEventType, List[Callable[[ContextEvent], None]]] = {}
        self._anomaly_detector = AnomalyDetector()
        self._context_manager: Optional[ContextManager] = None
        
        self._lock = threading.RLock()
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        self._stats = {
            'events_processed': 0,
            'anomalies_detected': 0,
            'anomalies_resolved': 0
        }
        
        logger.info("ContextMonitor zainicjalizowany")
    
    def start(self) -> bool:
        """Uruchomienie monitora."""
        if self._status == MonitorStatus.ACTIVE:
            return True
        
        try:
            # Polaczenie z ContextManager
            self._context_manager = get_context_manager()
            
            # Uruchomienie watku monitorujacego
            self._stop_event.clear()
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()
            
            self._status = MonitorStatus.ACTIVE
            logger.info("ContextMonitor uruchomiony")
            return True
        except Exception as e:
            logger.error(f"Blad podczas uruchamiania ContextMonitor: {e}")
            return False
    
    def stop(self) -> bool:
        """Zatrzymanie monitora."""
        if self._status == MonitorStatus.STOPPED:
            return True
        
        try:
            self._stop_event.set()
            if self._monitor_thread:
                self._monitor_thread.join(timeout=5.0)
            
            self._status = MonitorStatus.STOPPED
            logger.info("ContextMonitor zatrzymany")
            return True
        except Exception as e:
            logger.error(f"Blad podczas zatrzymywania ContextMonitor: {e}")
            return False
    
    def pause(self) -> bool:
        """Wstrzymanie monitora."""
        if self._status != MonitorStatus.ACTIVE:
            return False
        
        self._status = MonitorStatus.PAUSED
        logger.info("ContextMonitor wstrzymany")
        return True
    
    def resume(self) -> bool:
        """Wznowienie monitora."""
        if self._status != MonitorStatus.PAUSED:
            return False
        
        self._status = MonitorStatus.ACTIVE
        logger.info("ContextMonitor wznowiony")
        return True
    
    def get_status(self) -> MonitorStatus:
        """Pobranie statusu monitora."""
        return self._status
    
    def register_listener(
        self, 
        event_type: ContextEventType, 
        listener: Callable[[ContextEvent], None]
    ) -> None:
        """Rejestracja listenera dla zdarzen."""
        with self._lock:
            if event_type not in self._event_listeners:
                self._event_listeners[event_type] = []
            
            if listener not in self._event_listeners[event_type]:
                self._event_listeners[event_type].append(listener)
            
            logger.debug(f"Zarejestrowano listener dla {event_type.value}")
    
    def unregister_listener(
        self, 
        event_type: ContextEventType, 
        listener: Callable[[ContextEvent], None]
    ) -> bool:
        """Wyrejestrowanie listenera."""
        with self._lock:
            if event_type in self._event_listeners:
                if listener in self._event_listeners[event_type]:
                    self._event_listeners[event_type].remove(listener)
                    logger.debug(f"Wyrejestrowano listener dla {event_type.value}")
                    return True
        return False
    
    def emit_event(self, event: ContextEvent) -> None:
        """Wygenerowanie zdarzenia."""
        with self._lock:
            # Zapisanie zdarzenia
            self._events.append(event)
            self._event_queue.put(event)
            
            # Powiadomienie listenerów
            if event.event_type in self._event_listeners:
                for listener in self._event_listeners[event.event_type]:
                    try:
                        listener(event)
                    except Exception as e:
                        logger.error(f"Blad w listenerze dla {event.event_type.value}: {e}")
            
            # Statystyki
            self._stats['events_processed'] += 1
            
            # Logowanie
            logger.debug(f"Zdarzenie: {event}")
    
    def get_events(
        self, 
        event_type: Optional[ContextEventType] = None,
        limit: Optional[int] = None,
        from_timestamp: Optional[datetime] = None,
        to_timestamp: Optional[datetime] = None
    ) -> List[ContextEvent]:
        """Pobranie zdarzen z filtrowaniem."""
        with self._lock:
            filtered_events = self._events
            
            # Filtr wedlug typu
            if event_type:
                filtered_events = [e for e in filtered_events if e.event_type == event_type]
            
            # Filtr wedlug czasu
            if from_timestamp:
                filtered_events = [e for e in filtered_events if e.timestamp >= from_timestamp]
            
            if to_timestamp:
                filtered_events = [e for e in filtered_events if e.timestamp <= to_timestamp]
            
            # Limit
            if limit:
                filtered_events = filtered_events[-limit:]
            
            return filtered_events
    
    def get_statistics(self) -> Dict[str, Any]:
        """Pobranie statystyk monitora."""
        with self._lock:
            return {
                **self._stats,
                'status': self._status.value,
                'events_count': len(self._events),
                'anomalies_count': len(self._anomaly_detector.get_all_anomalies()),
                'anomalies_unresolved': len(self._anomaly_detector.get_unresolved_anomalies())
            }
    
    def monitor_message(self, message: SSIMessage) -> List[ContextEvent]:
        """
        Monitorowanie wiadomosci pod katem zmian kontekstu.
        
        Args:
            message: Wiadomosc do monitorowania
            
        Returns:
            List[ContextEvent]: Lista wykrytych zdarzen
        """
        events = []
        
        # Porównanie z aktualnym kontekstem
        if self._context_manager:
            try:
                current_context = self._context_manager.get_context()
                
                # Sprawdzenie zmiany sesji
                if (message.session_id and message.session_id != "default" and
                    current_context.session_id and current_context.session_id != "default" and
                    message.session_id != current_context.session_id):
                    
                    events.append(ContextEvent(
                        event_type=ContextEventType.SESSION_CHANGED,
                        session_id=message.session_id,
                        old_value=current_context.session_id,
                        new_value=message.session_id,
                        severity="info",
                        message=f"Zmiana sesji z {current_context.session_id} na {message.session_id}",
                        metadata={'source': 'message', 'message_id': message.message_id}
                    ))
                
                # Sprawdzenie zmiany cyklu
                if (message.cycle_id and message.cycle_id != "default" and
                    current_context.cycle_id and current_context.cycle_id != "default" and
                    message.cycle_id != current_context.cycle_id):
                    
                    events.append(ContextEvent(
                        event_type=ContextEventType.CYCLE_CHANGED,
                        cycle_id=message.cycle_id,
                        old_value=current_context.cycle_id,
                        new_value=message.cycle_id,
                        severity="info",
                        message=f"Zmiana cyklu z {current_context.cycle_id} na {message.cycle_id}",
                        metadata={'source': 'message', 'message_id': message.message_id}
                    ))
                
                # Sprawdzenie aktywnego modelu
                if message.system_state and message.system_state.active_model:
                    if (current_context.active_model and 
                        message.system_state.active_model != current_context.active_model):
                        
                        # Zmiana modelu - sprawdzenie czy nie narusza zasady
                        existing_events = self.get_events(
                            event_type=ContextEventType.MODEL_ACTIVE,
                            limit=5
                        )
                        
                        active_models = set()
                        for event in existing_events:
                            if event.new_value:
                                active_models.add(event.new_value)
                        
                        if message.system_state.active_model in active_models:
                            # Model juz byl aktywny - moze to byc problem!
                            events.append(ContextEvent(
                                event_type=ContextEventType.MODEL_CHANGED,
                                model_id=message.system_state.active_model,
                                old_value=current_context.active_model,
                                new_value=message.system_state.active_model,
                                severity="warning",
                                message=f"Ponowna aktywacja modelu: {message.system_state.active_model}",
                                metadata={'source': 'message', 'message_id': message.message_id}
                            ))
                        else:
                            events.append(ContextEvent(
                                event_type=ContextEventType.MODEL_ACTIVE,
                                model_id=message.system_state.active_model,
                                new_value=message.system_state.active_model,
                                severity="info",
                                message=f"Aktywny model: {message.system_state.active_model}",
                                metadata={'source': 'message', 'message_id': message.message_id}
                            ))
                
            except Exception as e:
                logger.debug(f"Blad podczas monitorowania wiadomosci: {e}")
        
        # Wygenerowanie zdarzen
        for event in events:
            self.emit_event(event)
        
        return events
    
    def check_for_anomalies(self) -> List[ContextAnomaly]:
        """Sprawdzenie czy sa anomalie w ostatnich zdarzeniach."""
        # Pobranie ostatnich zdarzen
        recent_events = self.get_events(limit=100)
        
        # Wykrywanie anomalii
        anomalies = self._anomaly_detector.detect_anomalies(recent_events)
        
        # Aktualizacja statystyk
        with self._lock:
            self._stats['anomalies_detected'] += len(anomalies)
        
        return anomalies
    
    def _monitor_loop(self) -> None:
        """Glowna petla monitorujaca."""
        logger.info("Monitoring loop uruchomiony")
        
        while not self._stop_event.is_set():
            try:
                if self._status == MonitorStatus.ACTIVE:
                    # Sprawdzenie nowych zdarzen
                    while not self._event_queue.empty():
                        event = self._event_queue.get(timeout=0.1)
                        # Zdarzenie zostalo juz przetworzone w emit_event
                        self._event_queue.task_done()
                    
                    # Okresowe sprawdzenie anomalii
                    time.sleep(1.0)
                    
                    # Co 30 sekund sprawdzamy anomalie
                    if self._stats['events_processed'] % 30 == 0:
                        anomalies = self.check_for_anomalies()
                        if anomalies:
                            logger.warning(f"Wykryto {len(anomalies)} anomalii kontekstowych")
                
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Blad w monitoring loop: {e}")
                time.sleep(1.0)
        
        logger.info("Monitoring loop zakonczony")
    
    def get_anomaly_detector(self) -> AnomalyDetector:
        """Pobranie wykrywacza anomalii."""
        return self._anomaly_detector


# Funkcje helper

def get_monitor() -> ContextMonitor:
    """Pobranie instancji monitora."""
    if not hasattr(get_monitor, '_instance'):
        get_monitor._instance = ContextMonitor()
    return get_monitor._instance


def start_monitoring() -> bool:
    """Uruchomienie monitorowania kontekstu."""
    monitor = get_monitor()
    return monitor.start()


def stop_monitoring() -> bool:
    """Zatrzymanie monitorowania kontekstu."""
    monitor = get_monitor()
    return monitor.stop()


def emit_context_event(event: ContextEvent) -> None:
    """Wygenerowanie zdarzenia kontekstowego."""
    monitor = get_monitor()
    monitor.emit_event(event)


def check_for_context_anomalies() -> List[ContextAnomaly]:
    """Sprawdzenie czy sa anomalie kontekstowe."""
    monitor = get_monitor()
    return monitor.check_for_anomalies()


def monitor_message(message: SSIMessage) -> List[ContextEvent]:
    """Monitorowanie wiadomosci."""
    monitor = get_monitor()
    if monitor.get_status() == MonitorStatus.ACTIVE:
        return monitor.monitor_message(message)
    return []


# Inicjalizacja modulu
import threading
