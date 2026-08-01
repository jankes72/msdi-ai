"""
SSI V5 - Information Flow Controller

Główny kontroler Information Flow Controller.
Wszystkie wiadomosci systemowe przechodza przez ten modul.

Zasada: Żaden moduł nie komunikuje się bezpośrednio z innym modułem.
Wszystko przez IFC.

Wersja: 2.0.0
Data: 2026-08-01
"""

import threading
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from SSI.v5.core.information_flow_controller.message_models import (
    SSIMessage,
    MessageResponse,
    MessageStatus,
    PriorityLevel,
    ProcessType,
    ModuleIdentifier
)

from SSI.v5.core.information_flow_controller.message_factory import MessageFactory
from SSI.v5.core.information_flow_controller.message_router import MessageRouter, get_router
from SSI.v5.core.information_flow_controller.message_history import MessageHistory, get_history
from SSI.v5.core.information_flow_controller.context_manager import (
    ContextManager,
    get_context_manager,
    ContextSnapshot,
    ContextUpdate
)

# Integracja z walidacja (lazy loading)
_validation_layer_initialized = False
_message_validator = None
_context_validator = None
_integrity_layer = None


# Konfiguracja logowania
logger = logging.getLogger(__name__)


@dataclass
class IFCConfig:
    """Konfiguracja Information Flow Controller."""
    enable_validation: bool = True
    enable_context_correction: bool = True
    enable_history: bool = True
    enable_integrity_layer: bool = True  # NOWE: Wlacz warstwe integralnosci
    max_retry_attempts: int = 3
    default_timeout_seconds: float = 30.0
    high_priority_timeout_seconds: float = 10.0
    critical_priority_timeout_seconds: float = 5.0


@dataclass
class IFCTStatistics:
    """Statystyki IFC."""
    messages_received: int = 0
    messages_sent: int = 0
    messages_failed: int = 0
    messages_retrying: int = 0
    messages_by_priority: Dict[str, int] = field(default_factory=dict)
    messages_by_type: Dict[str, int] = field(default_factory=dict)
    registered_modules: int = 0
    processing_time_total_ms: float = 0.0
    processing_time_avg_ms: float = 0.0
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'messages_received': self.messages_received,
            'messages_sent': self.messages_sent,
            'messages_failed': self.messages_failed,
            'messages_retrying': self.messages_retrying,
            'messages_by_priority': self.messages_by_priority,
            'messages_by_type': self.messages_by_type,
            'registered_modules': self.registered_modules,
            'processing_time_total_ms': self.processing_time_total_ms,
            'processing_time_avg_ms': self.processing_time_avg_ms,
            'errors_count': len(self.errors),
            'last_errors': self.errors[-10:]  # Ostatnie 10 bledow
        }


class InformationFlowController:
    """
    Główny kontroler Information Flow Controller SSI V5.
    
    Odpowiedzialnosc:
    - Centralny punkt komunikacji wszystkich modułów
    - Zarządzanie przeplywem wiadomosci
    - Koordynacja miedzy: Message Factory, Context Manager, Message Router, Message History
    - Obsluga błędów i retry
    - Monitorowanie i statystyki
    
    ZASADY PRACY:
    1. IFC przekazuje informacje, NIE podejmuje decyzji biznesowych
    2. IFC NIE steruje agentami
    3. IFC NIE zmienia pamięci modeli
    4. Wszystko przez IFC - żadna bezpośrednia komunikacja
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, config: IFCConfig = None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config: IFCConfig = None):
        if self._initialized:
            return
        
        self.config = config or IFCConfig()
        self._router = get_router()
        self._history = get_history()
        self._context_manager = get_context_manager()
        self._factory = MessageFactory
        
        self._statistics = IFCTStatistics()
        self._statistics_lock = threading.RLock()
        
        self._registered_modules: Dict[str, ModuleIdentifier] = {}
        self._subscribers: Dict[str, List[Callable]] = {}
        
        self._running = False
        self._initialized = True
        
        # Inicjalizacja podsystemow
        self._initialize_subsystems()
        
        logger.info("InformationFlowController zainicjalizowany")
    
    def _initialize_subsystems(self) -> None:
        """Inicjalizacja podsystemów."""
        # Ustawienie providerów dla MessageFactory
        MessageFactory.set_system_state_provider(self.get_system_state)
        MessageFactory.set_session_provider(self.get_current_session_id)
        MessageFactory.set_cycle_provider(self.get_current_cycle_id)
        
        # Inicjalizacja historii
        self._history.initialize()
        
        # Rejestracja wchodnych modułów systemowych (będzie rozbudowana)
        self._register_builtin_modules()
        
        # Inicjalizacja warstwy walidacji (lazy)
        self._initialize_validation_layer()
    
    def _register_builtin_modules(self) -> None:
        """Rejestracja wbudowanych modułów systemowych."""
        # Te moduły będą mogły odbierać wiadomości
        builtin_modules = [
            ModuleIdentifier(module_name="system", module_type="system"),
            ModuleIdentifier(module_name="runtime_controller", module_type="runtime"),
            ModuleIdentifier(module_name="llm_queue_manager", module_type="runtime"),
            ModuleIdentifier(module_name="teacher_engine", module_type="teacher"),
            ModuleIdentifier(module_name="agent_manager", module_type="agents"),
        ]
        
        for module in builtin_modules:
            self._registered_modules[str(module)] = module
        
        logger.debug(f"Zarejestrowano {len(builtin_modules)} wbudowanych modułów")
    
    def _initialize_validation_layer(self) -> None:
        """Inicjalizacja warstwy walidacji."""
        global _validation_layer_initialized, _message_validator, _context_validator, _integrity_layer
        
        if _validation_layer_initialized:
            return
        
        try:
            # Lazowe ladowanie walidatorów
            from SSI.v5.core.validation.message_validator import get_validator
            from SSI.v5.core.validation.context_validator import get_context_validator
            from SSI.v5.core.context_integrity import get_integrity_layer
            
            _message_validator = get_validator()
            _context_validator = get_context_validator()
            _integrity_layer = get_integrity_layer()
            
            _validation_layer_initialized = True
            logger.info("Warstwa walidacji i integralnosci zainicjalizowana")
        except Exception as e:
            logger.warning(f"Nie mozna zainicjowac warstwy walidacji: {e}")
            _validation_layer_initialized = False
    
    @classmethod
    def get_instance(cls) -> 'InformationFlowController':
        """Pobranie instancji singleton."""
        return cls()
    
    def start(self) -> bool:
        """Uruchomienie IFC."""
        with self._statistics_lock:
            self._running = True
        
        logger.info("IFC uruchomiony")
        self._context_manager.set_system_status("RUNNING")
        return True
    
    def stop(self) -> bool:
        """Zatrzymanie IFC."""
        with self._statistics_lock:
            self._running = False
        
        logger.info("IFC zatrzymany")
        self._context_manager.set_system_status("SHUTDOWN")
        return True
    
    def is_running(self) -> bool:
        """Sprawdzenie czy IFC jest uruchomiony."""
        return self._running
    
    # ==================== REJESTRACJA MODUŁÓW ====================
    
    def register_module(
        self,
        module_identifier: Union[str, ModuleIdentifier],
        handler: Callable[[SSIMessage], MessageResponse] = None,
        supported_process_types: List[str] = None,
        priority: int = 0
    ) -> bool:
        """
        Rejestracja nowego modułu w systemie IFC.
        
        Args:
            module_identifier: Identyfikator modułu
            handler: Funkcja obsługująca wiadomości (opcjonalnie)
            supported_process_types: Obsługiwane typy procesów (opcjonalnie)
            priority: Priorytet (opcjonalnie)
        
        Returns:
            bool: True jeśli rejestracja powiodła się
        """
        if isinstance(module_identifier, str):
            module_identifier = ModuleIdentifier.from_string(module_identifier)
        
        module_key = str(module_identifier)
        
        # Rejestracja w module routera
        if handler is not None:
            self._router.register_module(
                module_identifier=module_identifier,
                handler=handler,
                supported_process_types=supported_process_types,
                priority=priority
            )
        
        # Zapamiętanie modułu
        self._registered_modules[module_key] = module_identifier
        
        # Aktualizacja statystyk
        with self._statistics_lock:
            self._statistics.registered_modules = len(self._registered_modules)
        
        logger.info(f"Zarejestrowano modul: {module_key}")
        return True
    
    def unregister_module(self, module_identifier: Union[str, ModuleIdentifier]) -> bool:
        """Wyrejestrowanie modułu."""
        if isinstance(module_identifier, str):
            module_identifier = ModuleIdentifier.from_string(module_identifier)
        
        module_key = str(module_identifier)
        
        # Wyrejestrowanie z routera
        self._router.unregister_module(module_identifier)
        
        # Usuniecie z rejestru
        if module_key in self._registered_modules:
            del self._registered_modules[module_key]
        
        # Aktualizacja statystyk
        with self._statistics_lock:
            self._statistics.registered_modules = len(self._registered_modules)
        
        logger.info(f"Wyrejestrowano modul: {module_key}")
        return True
    
    def get_registered_modules(self) -> List[str]:
        """Pobranie listy zarejestrowanych modułów."""
        return [str(module) for module in self._registered_modules.values()]
    
    # ==================== SUBSCRYPCJA ZDARZEŃ ====================
    
    def subscribe(
        self,
        event_type: str,
        callback: Callable[[SSIMessage], Any],
        module_identifier: Optional[str] = None
    ) -> bool:
        """
        Subskrypcja zdarzeń o danym typie.
        
        Args:
            event_type: Typ zdarzenia (process_type lub customowy)
            callback: Funkcja wywoływana przy zdarzeniu
            module_identifier: Identyfikator modułu subskrybujacego
        
        Returns:
            bool: True jeśli subskrypcja powiodła się
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(callback)
        
        logger.debug(f"Subskrypcja {module_identifier} na zdarzenie: {event_type}")
        return True
    
    def unsubscribe(
        self,
        event_type: str,
        callback: Callable[[SSIMessage], Any]
    ) -> bool:
        """Wyrejestrowanie z subskrypcji."""
        if event_type in self._subscribers:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
        
        logger.debug(f"Wyrejestrowano subskrypcje na: {event_type}")
        return True
    
    def _notify_subscribers(self, message: SSIMessage) -> None:
        """Powiadomienie subskrybentów o wiadomosci."""
        process_type = message.process_type.value if hasattr(message.process_type, 'value') else message.process_type
        
        # Powiadomienie subskrybentów dla danego typu procesu
        if process_type in self._subscribers:
            for callback in self._subscribers[process_type]:
                try:
                    callback(message)
                except Exception as e:
                    logger.error(f"Blad w callback subskrypcji dla {process_type}: {e}")
        
        # Powiadomienie subskrybentów dla wszystkich typów
        if "*" in self._subscribers:
            for callback in self._subscribers["*"]:
                try:
                    callback(message)
                except Exception as e:
                    logger.error(f"Blad w callback subskrypcji dla *: {e}")
    
    # ==================== GŁÓWNE METODY IFC ====================
    
    def send_message(
        self,
        message: SSIMessage,
        timeout: Optional[float] = None
    ) -> MessageResponse:
        """
        Wysłanie wiadomosci przez IFC.
        Główna metoda komunikacji w systemie.
        
        Przepływ:
        1. Walidacja wiadomosci
        2. Wzbogacenie kontekstem
        3. Zapisyanie w historii (przed wyslaniem)
        4. Routing wiadomosci
        5. Zapisyanie w historii (po przetworzeniu)
        6. Powiadomienie subskrybentów
        
        Args:
            message: Wiadomosc do wyslania
            timeout: Maksymalny czas oczekiwania na odpowiedź (opcjonalnie)
        
        Returns:
            MessageResponse: Odpowiedź z systemu
        """
        start_time = time.time()
        
        # Sprawdzenie czy IFC jest uruchomiony
        if not self._running:
            error_msg = "IFC is not running"
            logger.error(error_msg)
            with self._statistics_lock:
                self._statistics.messages_failed += 1
                self._statistics.errors.append(error_msg)
            return MessageResponse.error(message.message_id, error_msg)
        
        # Krok 1: Pełna walidacja i korekta kontekstu
        # Zasada: Najpierw korekta kontekstu -> walidacja -> wykonanie
        corrected_message, integrity_result = self._validate_and_correct_message(message)
        
        if not integrity_result.is_integral:
            error_msg = f"Integrity check failed: {integrity_result.get_error_messages()}"
            logger.warning(error_msg)
            with self._statistics_lock:
                self._statistics.messages_failed += 1
                self._statistics.errors.append(error_msg)
            return MessageResponse.error(message.message_id, error_msg)
        
        # Krok 2: Wzbogacenie kontekstem (dodatkowa ochrona)
        message = self._enrich_message_context(corrected_message)
        
        # Krok 3: Zapisyanie w historii (przed)
        if self.config.enable_history:
            self._history.store_message(
                message=message,
                status=MessageStatus.QUEUED,
                metadata={"source": "ifc_controller", "action": "send_message"}
            )
        
        # Krok 4: Routing wiadomosci
        response = self._router.route_message(message)
        
        # Krok 5: Zapisyanie w historii (po)
        if self.config.enable_history and response:
            status = response.status if isinstance(response.status, MessageStatus) else MessageStatus.PROCESSED
            self._history.store_message(
                message=message,
                status=status,
                processed_at=datetime.now(),
                processing_time_ms=response.processing_time_ms,
                error=response.error,
                metadata={"source": "ifc_controller", "action": "route_complete"}
            )
        
        # Krok 6: Powiadomienie subskrybentów
        self._notify_subscribers(message)
        
        # Aktualizacja statystyk
        self._update_statistics(message, response, start_time)
        
        return response
    
    def receive_message(self, message: SSIMessage) -> MessageResponse:
        """
        Odbiór wiadomosci przez IFC.
        Uzywane przez moduły, które odebragung wiadomosc z systemu zewnetrznego.
        
        Args:
            message: Odebrana wiadomosc
        
        Returns:
            MessageResponse: Odpowiedź potwierdzajaca odebranie
        """
        start_time = time.time()
        
        if not self._running:
            error_msg = "IFC is not running"
            logger.error(error_msg)
            return MessageResponse.error(message.message_id, error_msg)
        
        # Walidacja
        if not self._validate_message_basic(message):
            error_msg = f"Invalid received message: {message.message_id}"
            logger.warning(error_msg)
            return MessageResponse.error(message.message_id, error_msg)
        
        # Powiadomienie subskrybentów o odebraniu
        self._notify_subscribers(message)
        
        # Zapis w historii
        if self.config.enable_history:
            self._history.store_message(
                message=message,
                status=MessageStatus.DELIVERED,
                metadata={"source": "external", "action": "receive_message"}
            )
        
        # Aktualizacja statystyk
        with self._statistics_lock:
            self._statistics.messages_received += 1
        
        return MessageResponse.success(
            message_id=message.message_id,
            processing_time_ms=(time.time() - start_time) * 1000
        )
    
    def route_message(self, message: SSIMessage) -> MessageResponse:
        """
        Przekierowanie istniejacej wiadomosci (bez dodatkowej obrobki).
        
        Args:
            message: Wiadomosc do przekierowania
        
        Returns:
            MessageResponse: Odpowiedź z routingu
        """
        return self._router.route_message(message)
    
    # ==================== KONTEKST ====================
    
    def get_context(self) -> ContextSnapshot:
        """Pobranie aktualnego kontekstu systemowego."""
        return self._context_manager.get_context()
    
    def get_system_state(self) -> Any:
        """Pobranie aktualnego stanu systemu."""
        return self._context_manager.get_system_state()
    
    def update_context(self, update: ContextUpdate) -> ContextSnapshot:
        """Aktualizacja kontekstu."""
        return self._context_manager.update_context(update)
    
    def get_current_session_id(self) -> str:
        """Pobranie aktualnego ID sesji."""
        return self.get_context().session_id
    
    def get_current_cycle_id(self) -> str:
        """Pobranie aktualnego ID cyklu."""
        return self.get_context().cycle_id
    
    def start_session(self, session_id: str) -> ContextSnapshot:
        """Rozpoczecie nowej sesji."""
        return self._context_manager.start_session(session_id)
    
    def end_session(self, session_id: str) -> ContextSnapshot:
        """Zakonczenie sesji."""
        return self._context_manager.end_session(session_id)
    
    def start_cycle(self, cycle_id: str, agent_id: str = None) -> ContextSnapshot:
        """Rozpoczecie nowego cyklu."""
        return self._context_manager.start_cycle(cycle_id, agent_id)
    
    def end_cycle(self, cycle_id: str) -> ContextSnapshot:
        """Zakonczenie cyklu."""
        return self._context_manager.end_cycle(cycle_id)
    
    # ==================== HISTORIA ====================
    
    def get_message_history(self, **kwargs) -> List[Any]:
        """Pobranie historii wiadomosci."""
        return self._history.query_messages(**kwargs)
    
    def get_message(self, message_id: str) -> Any:
        """Pobranie pojedynczej wiadomosci z historii."""
        return self._history.get_message(message_id)
    
    def get_conversation(self, correlation_id: str) -> List[Any]:
        """Pobranie konwersacji po correlation_id."""
        return self._history.get_conversation(correlation_id)
    
    def clear_history(self) -> None:
        """Wyczyszczenie historii wiadomosci."""
        self._history.clear_history()
    
    def get_history_statistics(self) -> Dict[str, Any]:
        """Pobranie statystyk historii."""
        return self._history.get_statistics()
    
    # ==================== STATYSTYKI ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Pobranie statystyk IFC."""
        with self._statistics_lock:
            return self._statistics.to_dict()
    
    def _update_statistics(
        self,
        message: SSIMessage,
        response: MessageResponse,
        start_time: float
    ) -> None:
        """Aktualizacja statystyk po przetworzeniu wiadomosci."""
        with self._statistics_lock:
            self._statistics.messages_sent += 1
            
            # Statystyki po priorytecie
            priority = message.priority.value if hasattr(message.priority, 'value') else message.priority.name
            self._statistics.messages_by_priority[priority] = \
                self._statistics.messages_by_priority.get(priority, 0) + 1
            
            # Statystyki po typie
            process_type = message.process_type.value if hasattr(message.process_type, 'value') else message.process_type
            self._statistics.messages_by_type[process_type] = \
                self._statistics.messages_by_type.get(process_type, 0) + 1
            
            # Czas przetwarzania
            processing_time = (time.time() - start_time) * 1000
            self._statistics.processing_time_total_ms += processing_time
            self._statistics.processing_time_avg_ms = \
                self._statistics.processing_time_total_ms / max(self._statistics.messages_sent, 1)
            
            # Błędy
            if response.status == MessageStatus.FAILED:
                self._statistics.messages_failed += 1
                if response.error:
                    self._statistics.errors.append(response.error)
    
    def reset_statistics(self) -> None:
        """Reset statystyk."""
        with self._statistics_lock:
            self._statistics = IFCTStatistics()
        logger.info("Zresetowano statystyki IFC")
    
    # ==================== WALIDACJA ====================
    
    def _validate_message_basic(self, message: SSIMessage) -> bool:
        """Podstawowa walidacja struktury wiadomosci."""
        if not message.is_valid():
            return False
        
        # Sprawdzenie czy źródło jest zarejestrowane
        source_key = str(message.source)
        if source_key not in self._registered_modules:
            logger.debug(f"Niezarejestrowane zrodlo: {source_key}")
            # To nie jest błąd - nowy moduł może wysłać pierwszą wiadomosc
        
        return True
    
    def _validate_and_correct_message(
        self, 
        message: SSIMessage
    ) -> Tuple[SSIMessage, Any]:
        """
        Walidacja i korekta wiadomosci z uzyciem warstwy integralnosci.
        
        Returns:
            Tuple[SSIMessage, IntegrityCheckResult]: Skorygowana wiadomosc i wynik walidacji
        """
        global _integrity_layer
        
        # Bezpieczne ladowanie warstwy integralnosci
        if not _validation_layer_initialized:
            self._initialize_validation_layer()
        
        # Uzycie warstwy integralnosci (jesli dostepna)
        if _integrity_layer and self.config.enable_validation:
            try:
                corrected, result = _integrity_layer.check_and_fix(message)
                return corrected, result
            except Exception as e:
                logger.warning(f"Blad podczas sprawdzania integralnosci: {e}")
                # W razie bledu, uzyj basic validation
                return message, self._basic_integrity_check(message)
        else:
            # Fallback do basic validation
            return message, self._basic_integrity_check(message)
    
    def _basic_integrity_check(self, message: SSIMessage) -> Any:
        """
        Podstawowa walidacja wiadomosci (fallback).
        
        Returns:
            Mock integrity result
        """
        from dataclasses import dataclass
        
        @dataclass
        class MockIntegrityResult:
            is_integral: bool
            get_error_messages: Any = None
            
            def __init__(self, is_integral: bool):
                self.is_integral = is_integral
                self._errors = [] if is_integral else ["Basic validation failed"]
            
            def get_error_messages(self) -> List[str]:
                return self._errors
        
        # Uzycie oryginalnej metody
        if self._validate_message_basic(message):
            return MockIntegrityResult(True)
        else:
            return MockIntegrityResult(False)
    
    def _enrich_message_context(self, message: SSIMessage) -> SSIMessage:
        """Wzbogacenie wiadomosci o aktualny kontekst."""
        if not self.config.enable_context_correction:
            return message
        
        try:
            # Pobranie aktualnego kontekstu
            context_data = self._context_manager.get_context_for_message()
            
            # Zaktualizowanie danych wiadomosci
            if message.system_state.timestamp < context_data['system_state'].timestamp:
                message.system_state = context_data['system_state']
            
            if message.session_id == "default":
                message.session_id = context_data['session_id']
            
            if message.cycle_id == "default":
                message.cycle_id = context_data['cycle_id']
            
            # Jeśli nie ma correlation_id, moze być powiązany z aktualnym
            if message.correlation_id is None:
                current_correlation = context_data['correlation_id']
                if current_correlation:
                    message.correlation_id = current_correlation
            
            return message
            
        except Exception as e:
            logger.warning(f"Blad podczas wzbogacania kontekstu: {e}")
            return message
    
    # ==================== SERVICE METODY ====================
    
    def create_message(
        self,
        source: Union[str, ModuleIdentifier],
        target: Union[str, ModuleIdentifier],
        process_type: Union[str, ProcessType],
        payload: Dict[str, Any] = None,
        **kwargs
    ) -> SSIMessage:
        """Utworzenie nowej wiadomosci."""
        return MessageFactory.create_message(
            source=source,
            target=target,
            process_type=process_type,
            payload=payload or {},
            **kwargs
        )
    
    def create_response(
        self,
        original_message: SSIMessage,
        payload: Dict[str, Any] = None,
        process_type: Union[str, ProcessType] = None
    ) -> SSIMessage:
        """Utworzenie wiadomosci odpowiedzi."""
        return MessageFactory.create_response_message(
            original_message=original_message,
            payload=payload or {},
            process_type=process_type
        )
    
    def status(self) -> Dict[str, Any]:
        """Pobranie stanu IFC."""
        return {
            'running': self._running,
            'statistics': self.get_statistics(),
            'registered_modules': len(self.get_registered_modules()),
            'context': self.get_context().to_dict(),
            'history_stats': self.get_history_statistics()
        }


# Funkcje helper

def get_ifc() -> InformationFlowController:
    """Pobranie instancji InformationFlowController."""
    return InformationFlowController.get_instance()


def send_message(
    source: Union[str, ModuleIdentifier],
    target: Union[str, ModuleIdentifier],
    process_type: Union[str, ProcessType],
    payload: Dict[str, Any] = None,
    **kwargs
) -> MessageResponse:
    """
    Wygodna funkcja do wysylania wiadomosci przez IFC.
    
    Args:
        source: Modul zrodlowy
        target: Modul docelowy
        process_type: Typ procesu
        payload: Dane wiadomosci
        **kwargs: Dodatkowe parametry
    
    Returns:
        MessageResponse: Odpowiedź z IFC
    """
    ifc = get_ifc()
    message = ifc.create_message(
        source=source,
        target=target,
        process_type=process_type,
        payload=payload,
        **kwargs
    )
    return ifc.send_message(message)


def receive_message(
    source: Union[str, ModuleIdentifier],
    process_type: Union[str, ProcessType],
    payload: Dict[str, Any] = None,
    **kwargs
) -> MessageResponse:
    """
    Wygodna funkcja do odbierania wiadomosci przez IFC.
    
    Args:
        source: Modul zrodlowy (po stronie odbierajacej jest to target)
        process_type: Typ procesu
        payload: Dane wiadomosci
        **kwargs: Dodatkowe parametry
    
    Returns:
        MessageResponse: Odpowiedź z IFC
    """
    # Dla odbierania, source staje sie targetem w systemie
    # Trzeba ustalic kto jest nadawca (zwykle system lub zewnetrzny)
    ifc = get_ifc()
    message = ifc.create_message(
        source="external",
        target=source,
        process_type=process_type,
        payload=payload,
        **kwargs
    )
    return ifc.receive_message(message)