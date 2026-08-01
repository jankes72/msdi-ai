"""
SSI V5 - Message Factory

Fabryka wiadomosci odpowiedzialna za tworzenie i wstępne przetwarzanie wiadomosci.
Zapewnia automatyczne uzupelnianie brakujacych pol i walidacje podstawowa.

Wersja: 2.0.0
Data: 2026-08-01
"""

from datetime import datetime
from typing import Any, Callable, Dict, Optional, Union
import uuid

from SSI.v5.core.information_flow_controller.message_models import (
    SSIMessage,
    SystemStateSnapshot,
    ModuleIdentifier,
    ProcessType,
    PriorityLevel
)


class MessageFactory:
    """
    Fabryka wiadomosci SSI V5.
    
    Odpowiedzialnosc:
    - Tworzenie wiadomosci z roznymi parametrami
    - Automatyczne uzupelnianie brakujacych pol
    - Wstępna walidacja struktury wiadomosci
    - Konwersja typow i formatow
    """
    
    # Funkcje callback do uzyskiwania stanu systemu
    _system_state_provider: Optional[Callable[[], SystemStateSnapshot]] = None
    _session_provider: Optional[Callable[[], str]] = None
    _cycle_provider: Optional[Callable[[], str]] = None
    
    @classmethod
    def set_system_state_provider(cls, provider: Callable[[], SystemStateSnapshot]):
        """Ustawienie funkcji dostarczajacej stan systemu."""
        cls._system_state_provider = provider
    
    @classmethod
    def set_session_provider(cls, provider: Callable[[], str]):
        """Ustawienie funkcji dostarczajacej wysokosc sesji."""
        cls._session_provider = provider
    
    @classmethod
    def set_cycle_provider(cls, provider: Callable[[], str]):
        """Ustawienie funkcji dostarczajacej identyfikator cyklu."""
        cls._cycle_provider = provider
    
    @classmethod
    def get_current_system_state(cls) -> SystemStateSnapshot:
        """Pobranie bieżącego stanu systemu."""
        if cls._system_state_provider:
            return cls._system_state_provider()
        return SystemStateSnapshot()
    
    @classmethod
    def get_current_session(cls) -> str:
        """Pobranie bieżącej sesji."""
        if cls._session_provider:
            return cls._session_provider()
        return "default"
    
    @classmethod
    def get_current_cycle(cls) -> str:
        """Pobranie bieżącego cyklu."""
        if cls._cycle_provider:
            return cls._cycle_provider()
        return "default"
    
    @classmethod
    def create_message(
        cls,
        source: Union[str, ModuleIdentifier],
        target: Union[str, ModuleIdentifier],
        process_type: Union[str, ProcessType],
        payload: Dict[str, Any] = None,
        **kwargs
    ) -> SSIMessage:
        """
        Tworzenie wiadomosci z automatycznym uzupelnieniem brakujacych pol.
        
        Args:
            source: Modul zrodlowy
            target: Modul docelowy
            process_type: Typ procesu
            payload: Dane wiadomosci
            **kwargs: Dodatkowe parametry (message_id, correlation_id, itp.)
        
        Returns:
            SSIMessage: Gotowa wiadomosc
        """
        # Konwersja typow
        if isinstance(process_type, str):
            process_type = ProcessType(process_type)
        
        # Automatyczne uzupelnianie brakujacych parametrow
        message_params = {
            'message_id': kwargs.get('message_id', str(uuid.uuid4())),
            'source': source,
            'target': target,
            'process_type': process_type,
            'payload': payload or {},
            'timestamp': kwargs.get('timestamp', datetime.now()),
            'system_state': kwargs.get('system_state', cls.get_current_system_state()),
            'session_id': kwargs.get('session_id', cls.get_current_session()),
            'cycle_id': kwargs.get('cycle_id', cls.get_current_cycle()),
            'correlation_id': kwargs.get('correlation_id'),
            'priority': kwargs.get('priority', PriorityLevel.NORMAL),
            'retry_count': kwargs.get('retry_count', 0)
        }
        
        # Usuniecie None'ow
        message_params = {k: v for k, v in message_params.items() if v is not None}
        
        return SSIMessage(**message_params)
    
    @classmethod
    def create_response_message(
        cls,
        original_message: SSIMessage,
        payload: Dict[str, Any] = None,
        process_type: Optional[Union[str, ProcessType]] = None,
        **kwargs
    ) -> SSIMessage:
        """
        Tworzenie wiadomosci odpowiedzi na podstawie oryginalnej wiadomosci.
        
        Args:
            original_message: Oryginalna wiadomosc
            payload: Nowe dane odpowiedzi
            process_type: Typ procesu (domyslnie RESPONSE)
            **kwargs: Dodatkowe parametry
        
        Returns:
            SSIMessage: Wiadomosc odpowiedzi
        """
        if process_type is None:
            # Automaskie ustalenie typu odpowiedzi
            if hasattr(original_message.process_type, 'value'):
                base_type = original_message.process_type.value
                process_type = f"{base_type}_response"
            else:
                process_type = ProcessType.AGENT_RESPONSE
        
        return cls.create_message(
            source=original_message.target,
            target=original_message.source,
            process_type=process_type,
            payload=payload or {},
            correlation_id=original_message.message_id,  # Powiazanie z oryginalna
            session_id=original_message.session_id,
            cycle_id=original_message.cycle_id,
            **kwargs
        )
    
    @classmethod
    def create_system_message(
        cls,
        process_type: Union[str, ProcessType],
        payload: Dict[str, Any] = None,
        target: Union[str, ModuleIdentifier] = "system",
        **kwargs
    ) -> SSIMessage:
        """
        Tworzenie wiadomosci systemowej.
        
        Args:
            process_type: Typ procesu systemowego
            payload: Dane wiadomosci
            target: Modul docelowy (domyslnie system)
            **kwargs: Dodatkowe parametry
        
        Returns:
            SSIMessage: Wiadomosc systemowa
        """
        return cls.create_message(
            source=ModuleIdentifier(module_name="system", module_type="system"),
            target=target,
            process_type=process_type,
            payload=payload or {},
            priority=kwargs.get('priority', PriorityLevel.HIGH),
            **kwargs
        )
    
    @classmethod
    def create_error_message(
        cls,
        original_message: SSIMessage,
        error: str,
        error_details: Dict[str, Any] = None
    ) -> SSIMessage:
        """
        Tworzenie wiadomosci o bledzie.
        
        Args:
            original_message: Oryginalna wiadomosc
            error: Treść błędu
            error_details: Szczegóły błędu
        
        Returns:
            SSIMessage: Wiadomosc o bledzie
        """
        return cls.create_response_message(
            original_message=original_message,
            process_type=ProcessType.AGENT_ERROR,
            payload={
                'error': error,
                'error_details': error_details or {},
                'original_message_id': original_message.message_id,
                'original_process_type': original_message.process_type.value
            },
            priority=PriorityLevel.HIGH
        )
    
    @classmethod
    def create_batch_messages(
        cls,
        source: Union[str, ModuleIdentifier],
        targets: list,
        process_type: Union[str, ProcessType],
        payload: Dict[str, Any] = None,
        **kwargs
    ) -> list:
        """
        Tworzenie wsadowe wielu wiadomosci do roznych celow.
        
        Args:
            source: Modul zrodlowy
            targets: Lista modulow docelowych
            process_type: Typ procesu
            payload: Dane wiadomosci (wspolne dla wszystkich)
            **kwargs: Dodatkowe parametry
        
        Returns:
            list: Lista wiadomosci
        """
        messages = []
        correlation_id = kwargs.get('correlation_id', str(uuid.uuid4()))
        
        for target in targets:
            message = cls.create_message(
                source=source,
                target=target,
                process_type=process_type,
                payload=payload,
                correlation_id=correlation_id,
                **kwargs
            )
            messages.append(message)
        
        return messages
    
    @classmethod
    def validate_message_structure(cls, message: SSIMessage) -> Dict[str, Any]:
        """
        Walidacja struktury wiadomosci.
        
        Args:
            message: Wiadomosc do zwalidowania
        
        Returns:
            Dict: Slownik z bledami (pusty jeśli OK)
        """
        errors = {}
        
        if not message.message_id:
            errors['message_id'] = "Message ID is required"
        
        if not message.source:
            errors['source'] = "Source is required"
        elif isinstance(message.source, ModuleIdentifier):
            if not message.source.module_name:
                errors['source'] = "Source module name is required"
        
        if not message.target:
            errors['target'] = "Target is required"
        elif isinstance(message.target, ModuleIdentifier):
            if not message.target.module_name:
                errors['target'] = "Target module name is required"
        
        if not message.timestamp:
            errors['timestamp'] = "Timestamp is required"
        
        if not message.process_type:
            errors['process_type'] = "Process type is required"
        
        if not isinstance(message.payload, dict):
            errors['payload'] = "Payload must be a dictionary"
        
        return errors
    
    @classmethod
    def enrich_message_context(
        cls,
        message: SSIMessage,
        system_state: SystemStateSnapshot = None,
        session_id: str = None,
        cycle_id: str = None
    ) -> SSIMessage:
        """
        Wzbogacanie wiadomosci o kontekst systemowy.
        
        Args:
            message: Wiadomosc do wzbogacenia
            system_state: Stan systemu (opcjonalnie)
            session_id: ID sesji (opcjonalnie)
            cycle_id: ID cyklu (opcjonalnie)
        
        Returns:
            SSIMessage: Wzbogacona wiadomosc
        """
        return message.clone(
            system_state=system_state or message.system_state,
            session_id=session_id or message.session_id,
            cycle_id=cycle_id or message.cycle_id
        )