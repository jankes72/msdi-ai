# SSI V5 - IFC Registry
# ETAP 1.2.7.3: Infrastructure Communication Fabric

"""
IFCRegistry -中央 (centralny) rejestr komponentów układu nerwowego SSI V5.

Odpowiada za:
- Rejestrację komponentów systemowych
- Zarządzanie cyklem życia komponentów
- Udostępnianie komponentów innym modułom
- Utrzymywanie metadanych komponentów

Architektura:
    ┌─────────────┐     ┌─────────────┐
    │  Component A │────▶│   IFCRegistry│
    └─────────────┘     └─────────────┘
                          │
                          ▼
    ┌─────────────┐     ┌─────────────┐
    │  Component B │◀────│   IFCRouter  │
    └─────────────┘     └─────────────┘

Użycie:
    # Rejestracja komponentu
    ifc = IFCRegistry()
    ifc.register("memory_ecosystem", memory_ecosystem)
    
    # Pobranie komponentu
    memory = ifc.get("memory_ecosystem")
    
    # Wysłanie wiadomości
    ifc.send("pipeline", "memory_ecosystem", payload=data)

Zależności:
    - ifc.message: IFCMessage
    - ifc.router: IFCRouter
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from .message import IFCMessage
from .router import IFCRouter, RouteResult


@dataclass
class ComponentMetadata:
    """Metadane zarejestrowanego komponentu."""
    component_type: str = "unknown"      # Typ komponentu (memory, agent, pipeline, etc.)
    version: str = "1.0.0"              # Wersja komponentu
    description: str = ""               # Opis komponentu
    dependencies: List[str] = field(default_factory=list)  # Zależności
    status: str = "registered"           # Status (registered, active, inactive, error)
    registered_at: str = ""             # Data rejestracji
    last_accessed: Optional[str] = None  # Ostatni dostęp
    access_count: int = 0              # Liczba dostępów


class IFCRegistry:
    """
    Centralny rejestr komponentów IFC.
    
    Jest układem nerwowym SSI V5 - wszyscy komponenci komunikują się
    przez niego, bez bezpośredniej wiedzy o sobie nawzajem.
    """
    
    def __init__(self):
        """Inicjalizacja rejestru."""
        # Rejestr komponentów: nazwa -> komponent
        self._components: Dict[str, Any] = {}
        
        # Metadane komponentów: nazwa -> ComponentMetadata
        self._metadata: Dict[str, ComponentMetadata] = {}
        
        # Router wiadomości
        self._router: Optional[IFCRouter] = None
        
        # Historia operacji
        self._operation_history: List[Dict[str, Any]] = []
        
        # Callbacki dla eventów
        self._registration_callbacks: List[Callable] = []
        self._unregistration_callbacks: List[Callable] = []
        
        # Logowanie
        self._verbose_logging: bool = False
    
    def register(
        self,
        name: str,
        component: Any,
        metadata: Optional[Dict[str, Any]] = None,
        component_type: str = "unknown",
        version: str = "1.0.0",
        description: str = "",
        dependencies: Optional[List[str]] = None
    ) -> bool:
        """
        Rejestracja komponentu w rejestrze.
        
        Args:
            name:        Unikalna nazwa komponentu
            component:   Obiekt komponentu
            metadata:    Dodatkowe metadane (opcjonalne)
            component_type: Typ komponentu
            version:     Wersja komponentu
            description: Opis komponentu
            dependencies: Lista zależności
            
        Returns:
            True jeśli rejestracja się powiodła
            
        Raises:
            ValueError: Jeśli komponent o podanej nazwie już istnieje
        """
        if name in self._components:
            raise ValueError(f"Component '{name}' already registered in IFC")
        
        # Zapis komponentu
        self._components[name] = component
        
        # Zapis metadanych
        self._metadata[name] = ComponentMetadata(
            component_type=component_type,
            version=version,
            description=description,
            dependencies=dependencies or [],
            status="registered",
            registered_at=self._get_current_timestamp()
        )
        
        # Dodatkowe metadane
        if metadata:
            for key, value in metadata.items():
                setattr(self._metadata[name], key, value)
        
        # Logowanie
        self._log_operation("register", name, success=True)
        
        if self._verbose_logging:
            print(f"[IFC] Registered: {name} ({component_type})")
        
        # Wywołanie callbacków rejestracji
        for callback in self._registration_callbacks:
            callback(name, component)
        
        return True
    
    def get(self, name: str) -> Optional[Any]:
        """
        Pobranie komponentu z rejestru.
        
        Args:
            name: Nazwa komponentu
            
        Returns:
            Komponent lub None jeśli nie znaleziono
        """
        if name not in self._components:
            self._log_operation("get", name, success=False, error="Component not found")
            return None
        
        # Aktualizacja statystyk dostępu
        self._metadata[name].access_count += 1
        self._metadata[name].last_accessed = self._get_current_timestamp()
        
        self._log_operation("get", name, success=True)
        return self._components[name]
    
    def exists(self, name: str) -> bool:
        """
        Sprawdzenie czy komponent istnieje w rejestrze.
        
        Args:
            name: Nazwa komponentu
            
        Returns:
            True jeśli komponent istnieje
        """
        return name in self._components
    
    def unregister(self, name: str) -> bool:
        """
        Usunięcie komponentu z rejestru.
        
        Args:
            name: Nazwa komponentu
            
        Returns:
            True jeśli usunięcie się powiodło
        """
        if name not in self._components:
            self._log_operation("unregister", name, success=False, error="Component not found")
            return False
        
        del self._components[name]
        del self._metadata[name]
        
        self._log_operation("unregister", name, success=True)
        
        # Wywołanie callbacków usunięcia
        for callback in self._unregistration_callbacks:
            callback(name)
        
        if self._verbose_logging:
            print(f"[IFC] Unregistered: {name}")
        
        return True
    
    def list_components(self) -> List[str]:
        """
        Lista wszystkich zarejestrowanych komponentów.
        
        Returns:
            Lista nazw komponentów
        """
        return list(self._components.keys())
    
    def get_metadata(self, name: str) -> Optional[ComponentMetadata]:
        """
        Pobranie metadanych komponentu.
        
        Args:
            name: Nazwa komponentu
            
        Returns:
            ComponentMetadata lub None
        """
        return self._metadata.get(name)
    
    def list_components_by_type(self, component_type: str) -> List[str]:
        """
        Lista komponentów danego typu.
        
        Args:
            component_type: Typ komponentu
            
        Returns:
            Lista nazw komponentów danego typu
        """
        return [
            name for name, metadata in self._metadata.items()
            if metadata.component_type == component_type
        ]
    
    def get_all_metadata(self) -> Dict[str, ComponentMetadata]:
        """
        Pobranie wszystkich metadanych.
        
        Returns:
            Słownik: nazwa -> ComponentMetadata
        """
        return self._metadata.copy()
    
    # ==================== MESSAGE ROUTING ====================
    
    @property
    def router(self) -> IFCRouter:
        """
        Leniwe tworzenie routera wiadomości.
        
        Returns:
            IFCRouter
        """
        if self._router is None:
            self._router = IFCRouter(registry=self)
        return self._router
    
    def send(
        self,
        source: str,
        target: str,
        message_type: str = "command",
        payload: Any = None,
        metadata: Optional[Dict] = None
    ) -> RouteResult:
        """
        Wysłanie wiadomości pomiędzy komponentami.
        
        Args:
            source:      Nazwa komponentu źródłowego
            target:      Nazwa komponentu docelowego
            message_type: Typ wiadomości
            payload:     Dane wiadomości
            metadata:   Metadane wiadomości
            
        Returns:
            RouteResult z wyniku routingu
        """
        return self.router.send(source, target, message_type, payload, metadata)
    
    def route(self, message: IFCMessage) -> RouteResult:
        """
        Routing wiadomości IFCMessage.
        
        Args:
            message: Wiadomość IFC
            
        Returns:
            RouteResult z wyniku routingu
        """
        return self.router.route(message)
    
    # ==================== CALLBACKS ====================
    
    def on_register(self, callback: Callable) -> None:
        """
        Rejestracja callbacka wywoływanego przy rejestracji komponentu.
        
        Args:
            callback: Funkcja (name: str, component: Any) -> None
        """
        self._registration_callbacks.append(callback)
    
    def on_unregister(self, callback: Callable) -> None:
        """
        Rejestracja callbacka wywoływanego przy usunięciu komponentu.
        
        Args:
            callback: Funkcja (name: str) -> None
        """
        self._unregistration_callbacks.append(callback)
    
    # ==================== STATISTICS & LOGGING ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Pobranie statystyk rejestru.
        
        Returns:
            Słownik ze statystykami
        """
        return {
            'total_components': len(self._components),
            'total_operations': len(self._operation_history),
            'message_stats': self.router.get_statistics() if self._router else {}
        }
    
    def get_operation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Pobranie historii operacji.
        
        Args:
            limit: Maksymalna liczba operacji
            
        Returns:
            Lista operacji
        """
        return self._operation_history[-limit:] if limit else self._operation_history.copy()
    
    def clear_operation_history(self) -> None:
        """Wyczyszczenie historii operacji."""
        self._operation_history.clear()
    
    def set_verbose_logging(self, enabled: bool) -> None:
        """
        Włączanie/wyłączanie szczegółowego logowania.
        
        Args:
            enabled: True aby włączyć
        """
        self._verbose_logging = enabled
    
    def _log_operation(
        self,
        operation: str,
        component: str,
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """
        Logowanie operacji (wewnętrzne).
        
        Args:
            operation: Typ operacji
            component:  Nazwa komponentu
            success:    Czy operacja się powiodła
            error:      Błąd (opcjonalny)
        """
        entry = {
            'timestamp': self._get_current_timestamp(),
            'operation': operation,
            'component': component,
            'success': success,
            'error': error
        }
        self._operation_history.append(entry)
        
        # Ograniczenie historii do ostatnich 1000 operacji
        if len(self._operation_history) > 1000:
            self._operation_history = self._operation_history[-1000:]
    
    def _get_current_timestamp(self) -> str:
        """Pobranie aktualnego timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    # ==================== CLEANUP ====================
    
    def clear(self) -> None:
        """Wyczyszczenie rejestru."""
        self._components.clear()
        self._metadata.clear()
        self._operation_history.clear()
        self._registration_callbacks.clear()
        self._unregistration_callbacks.clear()
        
        if self._router:
            self._router.clear_message_history()
        
        self._router = None
        
        if self._verbose_logging:
            print("[IFC] Registry cleared")
    
    def shutdown(self) -> None:
        """Zamknięcie rejestru i zwolnienie zasobów."""
        self.clear()
        if self._verbose_logging:
            print("[IFC] Registry shutdown")
