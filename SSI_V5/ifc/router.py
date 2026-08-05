# SSI V5 - IFC Router
# ETAP 1.2.7.3: Infrastructure Communication Fabric

"""
IFCRouter - Moduł routingu wiadomości.

Odpowiada za:
- Routing wiadomości pomiędzy komponentami
- Obsługę błędów routingu
- Logowanie przepływu wiadomości

Architektura:
    Component A --> IFCRouter --> Component B
    
    Router korzysta z IFCRegistry w celu znalezienia komponentu docelowego.
"""

from typing import Any, Dict, Optional, Callable
from dataclasses import dataclass, field
from .message import IFCMessage


@dataclass
class RouteResult:
    """Wynik routingu wiadomości."""
    success: bool
    response: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[IFCMessage] = None
    routed_via: str = "direct"  # direct, callback, queue


class IFCRouter:
    """Router wiadomości IFC."""
    
    def __init__(self, registry: Optional['IFCRegistry'] = None):
        """
        Inicjalizacja routera.
        
        Args:
            registry: Referencja do IFCRegistry (opcjonalna)
        """
        self.registry = registry
        self._message_log: list = []
        self._route_handlers: Dict[str, Callable] = {}
        self._fallback_handler: Optional[Callable] = None
    
    def set_registry(self, registry: 'IFCRegistry') -> None:
        """Ustawienie referencji do rejestru."""
        self.registry = registry
    
    def route(self, message: IFCMessage) -> RouteResult:
        """
        Routing wiadomości do komponentu docelowego.
        
        Args:
            message: Wiadomość IFC do przekazania
            
        Returns:
            RouteResult z wyniku routingu
        """
        # Logowanie wiadomości
        self._log_message(message)
        
        # Sprawdzenie czy target istnieje
        if not self.registry:
            return RouteResult(
                success=False,
                error="IFCRegistry not set in router",
                message=message
            )
        
        target_component = self.registry.get(message.target)
        
        if target_component is None:
            return RouteResult(
                success=False,
                error=f"Target component '{message.target}' not found in registry",
                message=message
            )
        
        # Przekazanie wiadomości do komponentu docelowego
        try:
            if hasattr(target_component, 'receive_message'):
                # Preferowana metoda: receive_message
                response = target_component.receive_message(message)
                return RouteResult(
                    success=True,
                    response=response,
                    message=message,
                    routed_via="receive_message"
                )
            elif hasattr(target_component, 'process_message'):
                # Alternatywna metoda: process_message
                response = target_component.process_message(message)
                return RouteResult(
                    success=True,
                    response=response,
                    message=message,
                    routed_via="process_message"
                )
            else:
                # Brak metody obsługi - zwróć błąd
                return RouteResult(
                    success=False,
                    error=f"Component '{message.target}' has no message handler (receive_message/process_message)",
                    message=message
                )
        except Exception as e:
            return RouteResult(
                success=False,
                error=f"Error routing message to '{message.target}': {str(e)}",
                message=message
            )
    
    def send(self, source: str, target: str, message_type: str = "command", 
             payload: Any = None, metadata: Optional[Dict] = None) -> RouteResult:
        """
        Wysyłanie wiadomości (skrócona metoda).
        
        Args:
            source: Nazwa komponentu źródłowego
            target: Nazwa komponentu docelowego
            message_type: Typ wiadomości
            payload: Dane wiadomości
            metadata: Metadane wiadomości
            
        Returns:
            RouteResult z wyniku routingu
        """
        message = IFCMessage(
            source=source,
            target=target,
            message_type=message_type,
            payload=payload,
            metadata=metadata or {}
        )
        return self.route(message)
    
    def register_handler(self, message_type: str, handler: Callable) -> None:
        """
        Rejestracjaniestandardowego handlera dla typu wiadomości.
        
        Args:
            message_type: Typ wiadomości
            handler: Funkcja obsługi (message: IFCMessage) -> Any
        """
        self._route_handlers[message_type] = handler
    
    def set_fallback_handler(self, handler: Callable) -> None:
        """
        Ustawienie handlera domyślnego (fallback).
        
        Args:
            handler: Funkcja obsługi wiadomości bez docelowego komponentu
        """
        self._fallback_handler = handler
    
    def _log_message(self, message: IFCMessage) -> None:
        """Logowanie wiadomości (do historii)."""
        log_entry = {
            'timestamp': message.metadata.get('timestamp'),
            'message_id': message.metadata.get('message_id'),
            'source': message.source,
            'target': message.target,
            'type': message.message_type,
            'priority': message.metadata.get('priority', 'normal')
        }
        self._message_log.append(log_entry)
        
        # Ograniczenie historii do ostatnich 1000 wiadomości
        if len(self._message_log) > 1000:
            self._message_log = self._message_log[-1000:]
    
    def get_message_history(self, limit: int = 100) -> list:
        """Pobranie historii wiadomości."""
        return self._message_log[-limit:] if limit else self._message_log.copy()
    
    def clear_message_history(self) -> None:
        """Wyczyszczenie historii wiadomości."""
        self._message_log.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Pobranie statystyk routingu."""
        return {
            'total_messages': len(self._message_log),
            'registered_handlers': len(self._route_handlers),
            'has_fallback': self._fallback_handler is not None,
            'registry_connected': self.registry is not None
        }
