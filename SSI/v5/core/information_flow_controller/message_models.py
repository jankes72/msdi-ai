"""
SSI V5 - Message Models

Modul zawiera modele wiadomosci uzywanych w Information Flow Controller.
Kazda wiadomosc w systemie SSI V5 musi dziedziczyc z SSIMessage.

Wersja: 2.0.0
Data: 2026-08-01
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union
import uuid


class MessageStatus(Enum):
    """Status wiadomosci w systemie."""
    CREATED = "created"           # Utworzona, nie wyslana
    QUEUED = "queued"            # W kolejce do wyslania
    SENT = "sent"                # Wyslana
    DELIVERED = "delivered"       # Doreczona do celu
    PROCESSED = "processed"       # Przetworzona
    FAILED = "failed"            # Blad podczas przetwarzania
    RETRYING = "retrying"        # Ponawiana
    EXPIRED = "expired"          # Przeterminowana


class PriorityLevel(Enum):
    """Poziom priorytetu wiadomosci."""
    CRITICAL = 0     # Krytyczna, natychmiastowa obsluga
    HIGH = 1        # Wysoki priorytet
    NORMAL = 2      # Normalny priorytet (domyslny)
    LOW = 3         # Niski priorytet
    BACKGROUND = 4  # Tlo, moze czekac


class ProcessType(Enum):
    """Typ procesu powiazany z wiadomoscia."""
    # Systemowe
    SYSTEM_INIT = "system_init"
    SYSTEM_SHUTDOWN = "system_shutdown"
    SYSTEM_HEARTBEAT = "system_heartbeat"
    SYSTEM_STATUS = "system_status"
    
    # Agentowe
    AGENT_ACTION = "agent_action"
    AGENT_DECISION = "agent_decision"
    AGENT_REQUEST = "agent_request"
    AGENT_RESPONSE = "agent_response"
    AGENT_ERROR = "agent_error"
    
    # Teacher Engine
    TEACHER_OBSERVATION = "teacher_observation"
    TEACHER_ANALYSIS = "teacher_analysis"
    TEACHER_RECOMMENDATION = "teacher_recommendation"
    TEACHER_EVALUATION = "teacher_evaluation"
    
    # Runtime
    RUNTIME_COMMAND = "runtime_command"
    RUNTIME_STATUS = "runtime_status"
    RUNTIME_CYCLE_START = "runtime_cycle_start"
    RUNTIME_CYCLE_END = "runtime_cycle_end"
    
    # LLM Queue
    LLM_REQUEST = "llm_request"
    LLM_RESPONSE = "llm_response"
    LLM_STATUS = "llm_status"
    
    # Memory
    MEMORY_READ = "memory_read"
    MEMORY_WRITE = "memory_write"
    MEMORY_UPDATE = "memory_update"
    MEMORY_DELETE = "memory_delete"
    
    # Strategy Laboratory
    STRATEGY_CREATE = "strategy_create"
    STRATEGY_TEST = "strategy_test"
    STRATEGY_UPDATE = "strategy_update"
    STRATEGY_RANKING = "strategy_ranking"
    
    # Decision Layer
    DECISION_REQUEST = "decision_request"
    DECISION_ANALYSIS = "decision_analysis"
    DECISION_SELECTION = "decision_selection"
    DECISION_RECORD = "decision_record"
    
    # Developer Interface
    DEVELOPER_COMMAND = "developer_command"
    DEVELOPER_ANALYSIS = "developer_analysis"
    DEVELOPER_REPORT = "developer_report"
    DEVELOPER_TEST = "developer_test"
    DEVELOPER_MODULE = "developer_module"


@dataclass
class SystemStateSnapshot:
    """
    Migawka stanu systemu na moment wyslania wiadomosci.
    Umozliwia sledzenie kontekstu czasowego.
    """
    timestamp: datetime = field(default_factory=datetime.now)
    system_version: str = "2.0.0"
    phase: str = "2"
    
    # Stan Runtime
    runtime_status: str = "running"
    cycle_count: int = 0
    total_cycles: int = 0
    total_iterations: int = 0
    
    # Stan LLM Queue
    active_model: Optional[str] = None
    queue_length: int = 0
    models_in_queue: int = 0
    
    # Stan pamieci
    memory_status: Dict[str, Any] = field(default_factory=dict)
    
    # Dodatkowe metadane
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'system_version': self.system_version,
            'phase': self.phase,
            'runtime_status': self.runtime_status,
            'cycle_count': self.cycle_count,
            'total_cycles': self.total_cycles,
            'total_iterations': self.total_iterations,
            'active_model': self.active_model,
            'queue_length': self.queue_length,
            'models_in_queue': self.models_in_queue,
            'memory_status': self.memory_status,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemStateSnapshot':
        """Tworzenie z slownika."""
        return cls(
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
            system_version=data.get('system_version', '2.0.0'),
            phase=data.get('phase', '2'),
            runtime_status=data.get('runtime_status', 'running'),
            cycle_count=data.get('cycle_count', 0),
            total_cycles=data.get('total_cycles', 0),
            total_iterations=data.get('total_iterations', 0),
            active_model=data.get('active_model'),
            queue_length=data.get('queue_length', 0),
            models_in_queue=data.get('models_in_queue', 0),
            memory_status=data.get('memory_status', {}),
            metadata=data.get('metadata', {})
        )


@dataclass
class ModuleIdentifier:
    """Identyfikator modulu w systemie SSI V5."""
    module_name: str
    module_type: str = "system"
    version: str = "1.0.0"
    module_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        if not self.module_id:
            self.module_id = str(uuid.uuid4())
    
    def __str__(self) -> str:
        return f"{self.module_type}://{self.module_name}@{self.version}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'module_name': self.module_name,
            'module_type': self.module_type,
            'version': self.version,
            'module_id': self.module_id
        }
    
    @classmethod
    def from_string(cls, identifier: str) -> 'ModuleIdentifier':
        """Parsowanie identyfikatora z stringa."""
        # Format: module_type://module_name@version
        parts = identifier.split("://")
        if len(parts) != 2:
            return cls(module_name=identifier)
        
        module_info = parts[1].split("@")
        module_name = module_info[0]
        version = module_info[1] if len(module_info) > 1 else "1.0.0"
        
        return cls(
            module_name=module_name,
            module_type=parts[0],
            version=version
        )


@dataclass
class MessageResponse:
    """Odpowiedz na wiadomosc."""
    message_id: str
    status: MessageStatus = MessageStatus.CREATED
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    processing_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'message_id': self.message_id,
            'status': self.status.value,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data,
            'error': self.error,
            'processing_time_ms': self.processing_time_ms
        }
    
    @classmethod
    def success(cls, message_id: str, data: Dict[str, Any] = None, processing_time_ms: float = 0.0) -> 'MessageResponse':
        """Tworzenie pozytywnej odpowiedzi."""
        return cls(
            message_id=message_id,
            status=MessageStatus.PROCESSED,
            data=data or {},
            processing_time_ms=processing_time_ms
        )
    
    @classmethod
    def error(cls, message_id: str, error: str, processing_time_ms: float = 0.0) -> 'MessageResponse':
        """Tworzenie odpowiedzi z bledem."""
        return cls(
            message_id=message_id,
            status=MessageStatus.FAILED,
            error=error,
            processing_time_ms=processing_time_ms
        )


@dataclass
class SSIMessage:
    """
    Glowna klasa wiadomosci systemu SSI V5.
    
    Kazda wiadomosc w systemie musi posiadac:
    - message_id: Unikalny identyfikator
    - source: Modul zrodlowy
    - target: Modul docelowy
    - timestamp: Data utworzenia
    - system_state: Stan systemu w momencie wyslania
    - session_id: Identyfikator sesji
    - cycle_id: Identyfikator cyklu
    - correlation_id: Identyfikator korelacji (dla lancuchow wiadomosci)
    - process_type: Typ procesu
    - payload: Dane wiadomosci
    - priority: Priorytet
    - retry_count: Licznik powtorzen
    """
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source: Union[ModuleIdentifier, str] = field(default_factory=ModuleIdentifier)
    target: Union[ModuleIdentifier, str] = field(default_factory=ModuleIdentifier)
    timestamp: datetime = field(default_factory=datetime.now)
    system_state: SystemStateSnapshot = field(default_factory=SystemStateSnapshot)
    session_id: str = "default"
    cycle_id: str = "default"
    correlation_id: Optional[str] = None
    process_type: ProcessType = ProcessType.SYSTEM_INIT
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: PriorityLevel = PriorityLevel.NORMAL
    retry_count: int = 0
    
    def __post_init__(self):
        # Rozpoznawanie typu source i target
        if isinstance(self.source, str):
            self.source = ModuleIdentifier.from_string(self.source)
        if isinstance(self.target, str):
            self.target = ModuleIdentifier.from_string(self.target)
        
        # Ustawienie domyslnego correlation_id
        if self.correlation_id is None:
            self.correlation_id = self.message_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        return {
            'message_id': self.message_id,
            'source': self.source.to_dict() if hasattr(self.source, 'to_dict') else str(self.source),
            'target': self.target.to_dict() if hasattr(self.target, 'to_dict') else str(self.target),
            'timestamp': self.timestamp.isoformat(),
            'system_state': self.system_state.to_dict(),
            'session_id': self.session_id,
            'cycle_id': self.cycle_id,
            'correlation_id': self.correlation_id,
            'process_type': self.process_type.value,
            'payload': self.payload,
            'priority': self.priority.value,
            'retry_count': self.retry_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SSIMessage':
        """Tworzenie z slownika."""
        source = data.get('source', {})
        if isinstance(source, dict):
            source = ModuleIdentifier(**source)
        
        target = data.get('target', {})
        if isinstance(target, dict):
            target = ModuleIdentifier(**target)
        
        system_state = data.get('system_state', {})
        if isinstance(system_state, dict):
            system_state = SystemStateSnapshot.from_dict(system_state)
        
        process_type = data.get('process_type', 'system_init')
        if isinstance(process_type, str):
            process_type = ProcessType(process_type)
        
        priority = data.get('priority', 'normal')
        if isinstance(priority, str):
            priority = PriorityLevel(priority)
        
        return cls(
            message_id=data.get('message_id', str(uuid.uuid4())),
            source=source,
            target=target,
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
            system_state=system_state,
            session_id=data.get('session_id', 'default'),
            cycle_id=data.get('cycle_id', 'default'),
            correlation_id=data.get('correlation_id'),
            process_type=process_type,
            payload=data.get('payload', {}),
            priority=priority,
            retry_count=data.get('retry_count', 0)
        )
    
    def clone(self, **kwargs) -> 'SSIMessage':
        """Klonowanie wiadomosci z mozliwoscia nadpisania pol."""
        message_dict = self.to_dict()
        message_dict.update(kwargs)
        return SSIMessage.from_dict(message_dict)
    
    def is_valid(self) -> bool:
        """Sprawdzenie czy wiadomosc jest poprawna."""
        if not self.message_id:
            return False
        if not self.source or not self.target:
            return False
        if not self.timestamp:
            return False
        if not self.process_type:
            return False
        return True
