"""
SSI V5 - Message Router

Router wiadomosci odpowiedzialny za dostarczanie wiadomosci do odpowiednich modułow.
Implementuje mechanizm routingu opartego na identyfikatorach modułow i typach procesow.

Wersja: 2.0.0
Data: 2026-08-01
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field

from SSI.v5.core.information_flow_controller.message_models import (
    SSIMessage,
    MessageResponse,
    MessageStatus,
    ModuleIdentifier
)


# Konfiguracja logowania
logger = logging.getLogger(__name__)


@dataclass
class RouteEntry:
    """Wpis w tablicy routingu."""
    module_identifier: ModuleIdentifier
    handler: Callable[[SSIMessage], MessageResponse]
    supported_process_types: List[str] = field(default_factory=list)
    priority: int = 0
    is_active: bool = True
    
    def matches(self, message: SSIMessage) -> bool:
        """Sprawdzenie czy wpis pasuje do wiadomosci."""
        if not self.is_active:
            return False
            
        # Sprawdzenie zagadnienia docelowego
        target_match = False
        if isinstance(message.target, str):
            target_match = (self.module_identifier.module_name == message.target or
                          str(self.module_identifier) == message.target)
        else:
            target_match = (self.module_identifier.module_name == message.target.module_name)
        
        if not target_match:
            return False
        
        # Sprawdzenie typu procesu (jesli zdefiniowane)
        if self.supported_process_types:
            process_type = message.process_type.value if hasattr(message.process_type, 'value') else message.process_type
            return process_type in self.supported_process_types
        
        return True


class MessageRouter:
    """
    Router wiadomosci SSI V5.
    
    Odpowiedzialnosc:
    - Rejestracja modułów i ich handlerow
    - Routing wiadomosci do odpowiednich celow
    - Zarządzanie tablica routingu
    - Obsługa błędów routingu
    """
    
    def __init__(self):
        self._routing_table: Dict[str, List[RouteEntry]] = {}
        self._module_handlers: Dict[str, Callable] = {}
        self._default_handler: Optional[Callable] = None
        self._fallback_handler: Optional[Callable] = None
        
    def register_module(
        self,
        module_identifier: Union[str, ModuleIdentifier],
        handler: Callable[[SSIMessage], MessageResponse],
        supported_process_types: List[str] = None,
        priority: int = 0
    ) -> bool:
        """
        Rejestracja nowego modułu w routerze.
        
        Args:
            module_identifier: Identyfikator modułu
            handler: Funkcja obsługująca wiadomości
            supported_process_types: Lista obsługiwanych typów procesów
            priority: Priorytet routingu
        
        Returns:
            bool: True jeśli rejestracja powiodła się
        """
        if isinstance(module_identifier, str):
            module_identifier = ModuleIdentifier.from_string(module_identifier)
        
        # Utworzenie wpisu w tablicy routingu
        route_entry = RouteEntry(
            module_identifier=module_identifier,
            handler=handler,
            supported_process_types=supported_process_types or [],
            priority=priority
        )
        
        # Dodanie do tablicy routingu
        module_key = str(module_identifier)
        if module_key not in self._routing_table:
            self._routing_table[module_key] = []
        
        self._routing_table[module_key].append(route_entry)
        self._routing_table[module_key].sort(key=lambda x: x.priority, reverse=True)
        
        # Zapamiętanie głównego handlera
        self._module_handlers[module_key] = handler
        
        logger.info(f"Zarejestrowano modul: {module_key}")
        return True
    
    def unregister_module(self, module_identifier: Union[str, ModuleIdentifier]) -> bool:
        """
        Wyrejestrowanie modułu z routera.
        
        Args:
            module_identifier: Identyfikator modułu
        
        Returns:
            bool: True jeśli wyrejestrowanie powiodło się
        """
        if isinstance(module_identifier, str):
            module_identifier = ModuleIdentifier.from_string(module_identifier)
        
        module_key = str(module_identifier)
        
        if module_key in self._routing_table:
            del self._routing_table[module_key]
        
        if module_key in self._module_handlers:
            del self._module_handlers[module_key]
        
        logger.info(f"Wyrejestrowano modul: {module_key}")
        return True
    
    def route_message(self, message: SSIMessage) -> MessageResponse:
        """
        Przekierowanie wiadomosci do odpowiedniego modułu.
        
        Args:
            message: Wiadomosc do przekierowania
        
        Returns:
            MessageResponse: Odpowiedź z modułu docelowego
        """
        import time
        start_time = time.time()
        
        # Sprawdzenie poprawnosci wiadomosci
        if not message.is_valid():
            error_msg = f"Invalid message: {message.message_id}"
            logger.error(error_msg)
            return MessageResponse.error(
                message_id=message.message_id,
                error=error_msg,
                processing_time_ms=(time.time() - start_time) * 1000
            )
        
        # Znalezienie odpowiedniego handlera
        target_key = str(message.target)
        handler = self._find_handler(message)
        
        if handler is None:
            error_msg = f"No handler found for target: {target_key}"
            logger.warning(error_msg)
            
            #-Próba użycia fallback handlera
            if self._fallback_handler:
                return self._execute_handler(self._fallback_handler, message, start_time)
            
            return MessageResponse.error(
                message_id=message.message_id,
                error=error_msg,
                processing_time_ms=(time.time() - start_time) * 1000
            )
        
        return self._execute_handler(handler, message, start_time)
    
    def _find_handler(self, message: SSIMessage) -> Optional[Callable]:
        """Znalezienie handlera dla wiadomosci."""
        target_key = str(message.target)
        
        # Szukanie w tablicy routingu
        if target_key in self._routing_table:
            for route_entry in self._routing_table[target_key]:
                if route_entry.matches(message):
                    return route_entry.handler
        
        # Szukanie w handlerach modułowych
        if target_key in self._module_handlers:
            return self._module_handlers[target_key]
        
        # Spróbowanie dopasowania po nazwie modułu
        target_name = message.target.module_name if isinstance(message.target, ModuleIdentifier) else message.target
        if target_name in self._module_handlers:
            return self._module_handlers[target_name]
        
        return None
    
    def _execute_handler(
        self,
        handler: Callable,
        message: SSIMessage,
        start_time: float
    ) -> MessageResponse:
        """Wykonywanie handlera z obsługą błędów."""
        try:
            response = handler(message)
            if isinstance(response, MessageResponse):
                return response
            else:
                # Konwersja na MessageResponse
                return MessageResponse.success(
                    message_id=message.message_id,
                    data={"result": response},
                    processing_time_ms=(time.time() - start_time) * 1000
                )
        except Exception as e:
            error_msg = f"Handler error for message {message.message_id}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return MessageResponse.error(
                message_id=message.message_id,
                error=error_msg,
                processing_time_ms=(time.time() - start_time) * 1000
            )
    
    def get_route_table(self) -> Dict[str, List[str]]:
        """Pobranie tablicy routingu."""
        result = {}
        for module_key, entries in self._routing_table.items():
            result[module_key] = [
                {
                    'module': str(entry.module_identifier),
                    'process_types': entry.supported_process_types,
                    'priority': entry.priority,
                    'active': entry.is_active
                }
                for entry in entries
            ]
        return result
    
    def get_registered_modules(self) -> List[str]:
        """Lista zarejestrowanych modułów."""
        return list(self._module_handlers.keys())
    
    def set_default_handler(self, handler: Callable[[SSIMessage], MessageResponse]):
        """Ustawienie domyślnego handlera."""
        self._default_handler = handler
        logger.info("Ustawiono domyslny handler")
    
    def set_fallback_handler(self, handler: Callable[[SSIMessage], MessageResponse]):
        """Ustawienie handlera fallback (dla nieznalezionych routów)."""
        self._fallback_handler = handler
        logger.info("Ustawiono fallback handler")
    
    def has_route(self, target: Union[str, ModuleIdentifier]) -> bool:
        """Sprawdzenie czy istnieje route dla danego celu."""
        target_key = str(target)
        return target_key in self._routing_table or target_key in self._module_handlers
    
    def get_handler_for(self, target: Union[str, ModuleIdentifier]) -> Optional[Callable]:
        """Pobranie handlera dla danego celu."""
        target_key = str(target)
        return self._module_handlers.get(target_key)
    
    def clear_routing(self) -> None:
        """Wyczyszczenie tablicy routingu."""
        self._routing_table.clear()
        self._module_handlers.clear()
        logger.info("Wyczyszczono tablice routingu")


# Instancja globalna
message_router = MessageRouter()


def get_router() -> MessageRouter:
    """Pobranie globalnej instancji routera."""
    return message_router