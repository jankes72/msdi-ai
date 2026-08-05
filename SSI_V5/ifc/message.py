# SSI V5 - IFC Message Structure
# ETAP 1.2.7.3: Infrastructure Communication Fabric

"""
IFCMessage - Uniwersalna struktura wiadomości dla układu nerwowego.

Kontrakt wiadomości:
- source:      Kto wysyła (component_name)
- target:      Do kogo (component_name)
- message_type: Typ wiadomości (command, data, event, request, response)
- payload:     Dane wiadomości
- metadata:    Metadane (timestamp, priority, correlation_id)

Przyszłe typy wiadomości:
- ETAP 1.2.7.3: memory_update, experiment_result, phase_transition
- ETAP 1.5:     agent_message, tutor_response, knowledge_proposal
- ETAP 2.0:    evolution_proposal, validation_request, deployment_command
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime
import uuid


@dataclass
class IFCMessage:
    """Uniwersalna struktura wiadomości IFC."""
    
    source: str                       # Nazwa komponentu źródłowego
    target: str                       # Nazwa komponentu docelowego
    message_type: str = "command"    # Typ wiadomości: command, data, event, request, response
    payload: Any = None               # Dane wiadomości
    metadata: Dict[str, Any] = field(default_factory=dict)  # Metadane
    
    def __post_init__(self):
        """Inicjalizacja domyślnych metadanych."""
        if not self.metadata:
            self.metadata = {}
        
        # Ustaw domyślne metadane jeśli nie istnieją
        if 'timestamp' not in self.metadata:
            self.metadata['timestamp'] = datetime.now().isoformat()
        if 'message_id' not in self.metadata:
            self.metadata['message_id'] = str(uuid.uuid4())
        if 'priority' not in self.metadata:
            self.metadata['priority'] = "normal"
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika."""
        return {
            'source': self.source,
            'target': self.target,
            'message_type': self.message_type,
            'payload': self.payload,
            'metadata': self.metadata.copy()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IFCMessage':
        """Tworzenie z słownika."""
        return cls(
            source=data.get('source', 'unknown'),
            target=data.get('target', 'unknown'),
            message_type=data.get('message_type', 'command'),
            payload=data.get('payload'),
            metadata=data.get('metadata', {})
        )
    
    def set_correlation_id(self, correlation_id: str) -> None:
        """Ustawienie ID korelacji (dla śledzenia konwersacji)."""
        self.metadata['correlation_id'] = correlation_id
    
    def get_correlation_id(self) -> Optional[str]:
        """Pobranie ID korelacji."""
        return self.metadata.get('correlation_id')
    
    def set_priority(self, priority: str) -> None:
        """Ustawienie priorytetu (low, normal, high, critical)."""
        valid_priorities = ['low', 'normal', 'high', 'critical']
        if priority.lower() in valid_priorities:
            self.metadata['priority'] = priority.lower()


# Predefiniowane typy wiadomości dla ETAP 1.2.7.3
class MessageType:
    """Typy wiadomości IFC."""
    
    # Podstawowe typy
    COMMAND = "command"
    DATA = "data"
    EVENT = "event"
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    
    # Specyficzne dla ETAP 1.2.7.3 (MemoryEcosystem)
    MEMORY_UPDATE = "memory_update"
    EXPERIMENT_RESULT = "experiment_result"
    PHASE_TRANSITION = "phase_transition"
    KNOWLEDGE_RECORD = "knowledge_record"
    
    # Specyficzne dla ETAP 1.5 (przyszłe)
    AGENT_MESSAGE = "agent_message"
    TUTOR_RESPONSE = "tutor_response"
    COLLECTIVE_DISCUSSION = "collective_discussion"
    
    # Specyficzne dla ETAP 2.0 (przyszłe)
    EVOLUTION_PROPOSAL = "evolution_proposal"
    VALIDATION_REQUEST = "validation_request"
    DEPLOYMENT_COMMAND = "deployment_command"
