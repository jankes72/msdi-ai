"""
SSI V5 - Context Manager

Centralne zarządzanie kontekstem systemowym dla Information Flow Controller.
Zapewnia spójny kontekst dla wszystkich wiadomosci przechodzacych przez IFC.

Wersja: 2.0.0
Data: 2026-08-01
"""

import threading
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from SSI.v5.core.information_flow_controller.message_models import (
    SystemStateSnapshot,
    ModuleIdentifier
)


# Konfiguracja logowania
logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """Tryby wykonania systemu."""
    NORMAL = "normal"
    TEST = "test"
    DEBUG = "debug"
    PRODUCTION = "production"
    MAINTENANCE = "maintenance"


class SystemStatus(Enum):
    """Status systemu."""
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    SHUTDOWN = "shutdown"


@dataclass
class OperationRecord:
    """Rekord ostatniej operacji."""
    operation_id: str
    operation_type: str
    timestamp: datetime
    source: str
    target: str
    process_type: str
    status: str
    duration_ms: float = 0.0
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextSnapshot:
    """
    Migawka kontekstu systemowego w danym momencie.
    Uzywany do przekazywania kontekstu wraz z wiadomosciami.
    """
    # Podstawowy kontekst systemowy
    system_state: SystemStateSnapshot = field(default_factory=SystemStateSnapshot)
    
    # Identyfikatory
    session_id: str = "default"
    cycle_id: str = "default"
    correlation_id: Optional[str] = None
    
    # Aktywne elementy
    active_agent: Optional[str] = None
    active_model: Optional[str] = None
    
    # Tryb i status
    execution_mode: ExecutionMode = ExecutionMode.NORMAL
    system_status: SystemStatus = SystemStatus.INITIALIZING
    
    # Informacje o procesie
    current_process_type: Optional[str] = None
    process_chain: List[str] = field(default_factory=list)
    
    # Stan pamieci
    memory_state: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_operation_at: Optional[datetime] = None
    
    # Ostatnie operacje
    last_operations: List[OperationRecord] = field(default_factory=list)
    operation_count: int = 0
    error_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        return {
            'system_state': self.system_state.to_dict(),
            'session_id': self.session_id,
            'cycle_id': self.cycle_id,
            'correlation_id': self.correlation_id,
            'active_agent': self.active_agent,
            'active_model': self.active_model,
            'execution_mode': self.execution_mode.value,
            'system_status': self.system_status.value,
            'current_process_type': self.current_process_type,
            'process_chain': self.process_chain,
            'memory_state': self.memory_state,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_operation_at': self.last_operation_at.isoformat() if self.last_operation_at else None,
            'last_operations': [op.to_dict() for op in self.last_operations],
            'operation_count': self.operation_count,
            'error_count': self.error_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContextSnapshot':
        """Tworzenie z slownika."""
        system_state_data = data.get('system_state', {})
        system_state = SystemStateSnapshot.from_dict(system_state_data)
        
        last_operations = []
        for op_data in data.get('last_operations', []):
            last_operations.append(OperationRecord(**op_data))
        
        return cls(
            system_state=system_state,
            session_id=data.get('session_id', 'default'),
            cycle_id=data.get('cycle_id', 'default'),
            correlation_id=data.get('correlation_id'),
            active_agent=data.get('active_agent'),
            active_model=data.get('active_model'),
            execution_mode=ExecutionMode(data.get('execution_mode', 'normal')),
            system_status=SystemStatus(data.get('system_status', 'initializing')),
            current_process_type=data.get('current_process_type'),
            process_chain=data.get('process_chain', []),
            memory_state=data.get('memory_state', {}),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat())),
            last_operation_at=datetime.fromisoformat(data['last_operation_at']) if data.get('last_operation_at') else None,
            last_operations=last_operations,
            operation_count=data.get('operation_count', 0),
            error_count=data.get('error_count', 0)
        )
    
    def clone(self) -> 'ContextSnapshot':
        """Klonowanie kontekstu."""
        return ContextSnapshot(
            system_state=self.system_state.clone() if hasattr(self.system_state, 'clone') else self.system_state,
            session_id=self.session_id,
            cycle_id=self.cycle_id,
            correlation_id=self.correlation_id,
            active_agent=self.active_agent,
            active_model=self.active_model,
            execution_mode=self.execution_mode,
            system_status=self.system_status,
            current_process_type=self.current_process_type,
            process_chain=self.process_chain.copy(),
            memory_state=self.memory_state.copy(),
            created_at=self.created_at,
            updated_at=datetime.now(),
            last_operation_at=self.last_operation_at,
            last_operations=self.last_operations.copy(),
            operation_count=self.operation_count,
            error_count=self.error_count
        )


@dataclass
class ContextUpdate:
    """Aktualizacja kontekstu."""
    session_id: Optional[str] = None
    cycle_id: Optional[str] = None
    correlation_id: Optional[str] = None
    active_agent: Optional[str] = None
    active_model: Optional[str] = None
    execution_mode: Optional[ExecutionMode] = None
    system_status: Optional[SystemStatus] = None
    current_process_type: Optional[str] = None
    memory_state: Optional[Dict[str, Any]] = None
    add_process_to_chain: Optional[str] = None
    add_operation: Optional[OperationRecord] = None
    increment_operation_count: bool = False
    increment_error_count: bool = False


class ContextManager:
    """
    Centralny menedzer kontekstu dla SSI V5 IFC.
    
    Odpowiedzialnosc:
    - Przechowywanie i zarządzanie stanem kontekstu systemowego
    - Zapewnienie thread-safety
    - Dostarczanie kontekstu dla wiadomosci
    - Integracja z Dynamic Context Correction (przygotowanie)
    - Monitorowanie aktywnosci systemu
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._context = ContextSnapshot()
        self._context_lock = threading.RLock()
        self._initialized = True
        
        logger.info("ContextManager zainicjalizowany")
    
    @classmethod
    def get_instance(cls) -> 'ContextManager':
        """Pobranie instancji singleton."""
        return cls()
    
    def get_context(self) -> ContextSnapshot:
        """Pobranie aktualnego kontekstu."""
        with self._context_lock:
            return self._context.clone()
    
    def get_system_state(self) -> SystemStateSnapshot:
        """Pobranie aktualnego stanu systemu."""
        with self._context_lock:
            return self._context.system_state
    
    def update_context(self, update: ContextUpdate) -> ContextSnapshot:
        """
        Aktualizacja kontekstu.
        
        Args:
            update: Obiekt ContextUpdate z polami do zaktualizowania
        
        Returns:
            ContextSnapshot: Zaktualizowany kontekst
        """
        with self._context_lock:
            if update.session_id is not None:
                self._context.session_id = update.session_id
            
            if update.cycle_id is not None:
                self._context.cycle_id = update.cycle_id
            
            if update.correlation_id is not None:
                self._context.correlation_id = update.correlation_id
            
            if update.active_agent is not None:
                self._context.active_agent = update.active_agent
            
            if update.active_model is not None:
                self._context.active_model = update.active_model
            
            if update.execution_mode is not None:
                self._context.execution_mode = update.execution_mode
            
            if update.system_status is not None:
                self._context.system_status = update.system_status
            
            if update.current_process_type is not None:
                self._context.current_process_type = update.current_process_type
            
            if update.memory_state is not None:
                self._context.memory_state.update(update.memory_state)
            
            if update.add_process_to_chain is not None:
                self._context.process_chain.append(update.add_process_to_chain)
            
            if update.add_operation is not None:
                self._context.last_operations.append(update.add_operation)
                # Zostawić ostatnie 100 operacji
                if len(self._context.last_operations) > 100:
                    self._context.last_operations = self._context.last_operations[-100:]
            
            if update.increment_operation_count:
                self._context.operation_count += 1
            
            if update.increment_error_count:
                self._context.error_count += 1
            
            self._context.updated_at = datetime.now()
            
            logger.debug(f"Zaktualizowano kontekst: {update}")
            return self._context.clone()
    
    def reset_context(self) -> ContextSnapshot:
        """Reset kontekstu do stanu poczatkowego."""
        with self._context_lock:
            self._context = ContextSnapshot()
            logger.info("Zresetowano kontekst systemowy")
            return self._context.clone()
    
    def start_session(self, session_id: str) -> ContextSnapshot:
        """Rozpoczecie nowej sesji."""
        with self._context_lock:
            update = ContextUpdate(
                session_id=session_id,
                cycle_id=f"{session_id}_cycle_001",
                add_operation=OperationRecord(
                    operation_id=f"session_start_{session_id}",
                    operation_type="session_start",
                    timestamp=datetime.now(),
                    source="system",
                    target="all",
                    process_type="system_init",
                    status="started"
                ),
                increment_operation_count=True
            )
            return self.update_context(update)
    
    def end_session(self, session_id: str) -> ContextSnapshot:
        """Zakonczenie sesji."""
        with self._context_lock:
            update = ContextUpdate(
                session_id="default",
                cycle_id="default",
                active_agent=None,
                active_model=None,
                add_operation=OperationRecord(
                    operation_id=f"session_end_{session_id}",
                    operation_type="session_end",
                    timestamp=datetime.now(),
                    source="system",
                    target="all",
                    process_type="system_shutdown",
                    status="completed"
                ),
                increment_operation_count=True
            )
            return self.update_context(update)
    
    def start_cycle(self, cycle_id: str, agent_id: Optional[str] = None) -> ContextSnapshot:
        """Rozpoczecie nowego cyklu."""
        with self._context_lock:
            update = ContextUpdate(
                cycle_id=cycle_id,
                active_agent=agent_id,
                add_process_to_chain=f"cycle_start_{cycle_id}",
                add_operation=OperationRecord(
                    operation_id=f"cycle_start_{cycle_id}",
                    operation_type="cycle_start",
                    timestamp=datetime.now(),
                    source="runtime_controller",
                    target=agent_id or "unknown",
                    process_type="runtime_cycle_start",
                    status="started"
                ),
                increment_operation_count=True
            )
            return self.update_context(update)
    
    def end_cycle(self, cycle_id: str) -> ContextSnapshot:
        """Zakonczenie cyklu."""
        with self._context_lock:
            update = ContextUpdate(
                cycle_id=f"{cycle_id}_completed",
                active_agent=None,
                add_process_to_chain=f"cycle_end_{cycle_id}",
                add_operation=OperationRecord(
                    operation_id=f"cycle_end_{cycle_id}",
                    operation_type="cycle_end",
                    timestamp=datetime.now(),
                    source="runtime_controller",
                    target="all",
                    process_type="runtime_cycle_end",
                    status="completed"
                ),
                increment_operation_count=True
            )
            return self.update_context(update)
    
    def set_active_model(self, model_name: str) -> ContextSnapshot:
        """Ustawienie aktywnego modelu LLM."""
        with self._context_lock:
            # Zgodnie z zasada: JEDEN MODEL LLM NARAZ
            update = ContextUpdate(
                active_model=model_name,
                add_operation=OperationRecord(
                    operation_id=f"model_activate_{model_name}",
                    operation_type="model_activation",
                    timestamp=datetime.now(),
                    source="llm_queue_manager",
                    target="system",
                    process_type="llm_request",
                    status="activated"
                ),
                increment_operation_count=True
            )
            return self.update_context(update)
    
    def clear_active_model(self) -> ContextSnapshot:
        """Wyczyszczenie aktywnego modelu LLM."""
        with self._context_lock:
            update = ContextUpdate(
                active_model=None,
                add_operation=OperationRecord(
                    operation_id="model_deactivate",
                    operation_type="model_deactivation",
                    timestamp=datetime.now(),
                    source="llm_queue_manager",
                    target="system",
                    process_type="llm_status",
                    status="deactivated"
                ),
                increment_operation_count=True
            )
            return self.update_context(update)
    
    def set_active_agent(self, agent_id: str) -> ContextSnapshot:
        """Ustawienie aktywnego agenta."""
        with self._context_lock:
            update = ContextUpdate(
                active_agent=agent_id,
                add_operation=OperationRecord(
                    operation_id=f"agent_activate_{agent_id}",
                    operation_type="agent_activation",
                    timestamp=datetime.now(),
                    source="agent_manager",
                    target=agent_id,
                    process_type="agent_action",
                    status="activated"
                ),
                increment_operation_count=True
            )
            return self.update_context(update)
    
    def clear_active_agent(self) -> ContextSnapshot:
        """Wyczyszczenie aktywnego agenta."""
        with self._context_lock:
            current_agent = self._context.active_agent
            if current_agent:
                update = ContextUpdate(
                    active_agent=None,
                    add_operation=OperationRecord(
                        operation_id=f"agent_deactivate_{current_agent}",
                        operation_type="agent_deactivation",
                        timestamp=datetime.now(),
                        source="agent_manager",
                        target=current_agent,
                        process_type="agent_action",
                        status="deactivated"
                    ),
                    increment_operation_count=True
                )
                return self.update_context(update)
            return self._context.clone()
    
    def set_execution_mode(self, mode: ExecutionMode) -> ContextSnapshot:
        """Ustawienie trybu wykonania."""
        with self._context_lock:
            update = ContextUpdate(
                execution_mode=mode,
                add_operation=OperationRecord(
                    operation_id=f"mode_change_{mode.value}",
                    operation_type="mode_change",
                    timestamp=datetime.now(),
                    source="system",
                    target="all",
                    process_type="system_command",
                    status="changed"
                ),
                increment_operation_count=True
            )
            return self.update_context(update)
    
    def set_system_status(self, status: Union[SystemStatus, str]) -> ContextSnapshot:
        """Ustawienie statusu systemu."""
        with self._context_lock:
            # Konwersja stringa na enum
            if isinstance(status, str):
                status_enum = SystemStatus(status.lower())
            else:
                status_enum = status
            
            update = ContextUpdate(
                system_status=status_enum,
                add_operation=OperationRecord(
                    operation_id=f"status_change_{status_enum.value}",
                    operation_type="status_change",
                    timestamp=datetime.now(),
                    source="system",
                    target="all",
                    process_type="system_status",
                    status=status_enum.value
                ),
                increment_operation_count=True
            )
            return self.update_context(update)
    
    def update_system_state(self, state_data: Dict[str, Any]) -> ContextSnapshot:
        """Aktualizacja stanu systemu."""
        with self._context_lock:
            # Zmergowanie nowych danych ze stanem
            if 'runtime_status' in state_data:
                self._context.system_state.runtime_status = state_data['runtime_status']
            if 'cycle_count' in state_data:
                self._context.system_state.cycle_count = state_data['cycle_count']
            if 'total_cycles' in state_data:
                self._context.system_state.total_cycles = state_data['total_cycles']
            if 'total_iterations' in state_data:
                self._context.system_state.total_iterations = state_data['total_iterations']
            if 'active_model' in state_data:
                self._context.system_state.active_model = state_data['active_model']
            if 'queue_length' in state_data:
                self._context.system_state.queue_length = state_data['queue_length']
            if 'models_in_queue' in state_data:
                self._context.system_state.models_in_queue = state_data['models_in_queue']
            
            # Aktualizacja metadata
            if 'metadata' in state_data:
                self._context.system_state.metadata.update(state_data['metadata'])
            
            self._context.system_state.timestamp = datetime.now()
            self._context.updated_at = datetime.now()
            
            logger.debug(f"Zaktualizowano stan systemu: {state_data}")
            return self._context.clone()
    
    def update_memory_state(self, memory_data: Dict[str, Any]) -> ContextSnapshot:
        """Aktualizacja stanu pamieci."""
        with self._context_lock:
            update = ContextUpdate(
                memory_state=memory_data,
                add_operation=OperationRecord(
                    operation_id="memory_update",
                    operation_type="memory_update",
                    timestamp=datetime.now(),
                    source="memory_manager",
                    target="system",
                    process_type="memory_update",
                    status="updated",
                    data={"memory_state": memory_data}
                ),
                increment_operation_count=True
            )
            return self.update_context(update)
    
    def record_error(self, error: str, source: str = "unknown") -> ContextSnapshot:
        """Zarejestrowanie błędu."""
        with self._context_lock:
            update = ContextUpdate(
                add_operation=OperationRecord(
                    operation_id=f"error_{datetime.now().timestamp()}",
                    operation_type="error",
                    timestamp=datetime.now(),
                    source=source,
                    target="system",
                    process_type="system_error",
                    status="error",
                    data={"error": error}
                ),
                increment_operation_count=True,
                increment_error_count=True
            )
            return self.update_context(update)
    
    def get_context_for_message(self) -> Dict[str, Any]:
        """
        Pobranie kontekstu gotowego do użycia w wiadomosci.
        
        Returns:
            Dict: Slownik z polami kontekstu gotowymi do użycia w SSIMessage
        """
        with self._context_lock:
            context = self._context
            return {
                'system_state': context.system_state,
                'session_id': context.session_id,
                'cycle_id': context.cycle_id,
                'correlation_id': context.correlation_id,
                'active_agent': context.active_agent,
                'active_model': context.active_model,
                'execution_mode': context.execution_mode.value,
                'system_status': context.system_status.value
            }
    
    def get_full_context_snapshot(self) -> Dict[str, Any]:
        """Pobranie pełnego snapshota kontekstu."""
        with self._context_lock:
            return self._context.to_dict()


# Funkcje helper

def get_context_manager() -> ContextManager:
    """Pobranie instancji ContextManager."""
    return ContextManager.get_instance()


def get_current_context() -> ContextSnapshot:
    """Pobranie aktualnego kontekstu."""
    return get_context_manager().get_context()


def update_current_context(update_data: Dict[str, Any]) -> ContextSnapshot:
    """Aktualizacja aktualnego kontekstu."""
    # Konwersja dict na ContextUpdate
    update = ContextUpdate()
    for key, value in update_data.items():
        if hasattr(update, key):
            setattr(update, key, value)
    
    return get_context_manager().update_context(update)