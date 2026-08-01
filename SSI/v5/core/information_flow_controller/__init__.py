"""
SSI V5 - Information Flow Controller Module

Modul odpowiada za centralny przeplyw informacji w systemie SSI V5.
Zasada: Zaden modul nie komunikuje sie bezposrednio z innym modulami.
Wszystkie wiadomosci przechodza przez IFC.

Składniki:
- message_models.py: Modele wiadomosci (SSIMessage, MessageResponse)
- message_factory.py: Fabryka tworzenia wiadomosci
- message_router.py: Router wiadomosci do celow
- message_history.py: Historia komunikacji
- context_manager.py: Zarządzanie kontekstem systemowym
- ifc_controller.py: Glowny kontroler IFC

Wersja: 2.0.0
Data: 2026-08-01
"""

from SSI.v5.core.information_flow_controller.message_models import (
    SSIMessage,
    MessageResponse,
    MessageStatus,
    PriorityLevel,
    ProcessType,
    SystemStateSnapshot,
    ModuleIdentifier
)

from SSI.v5.core.information_flow_controller.message_factory import (
    MessageFactory
)

from SSI.v5.core.information_flow_controller.message_router import (
    MessageRouter,
    get_router
)

from SSI.v5.core.information_flow_controller.message_history import (
    MessageHistory,
    MessageRecord,
    HistoryConfig,
    get_history
)

from SSI.v5.core.information_flow_controller.context_manager import (
    ContextManager,
    ContextSnapshot,
    ContextUpdate,
    ExecutionMode,
    SystemStatus,
    get_context_manager,
    get_current_context
)

from SSI.v5.core.information_flow_controller.ifc_controller import (
    InformationFlowController,
    IFCConfig,
    IFCTStatistics,
    get_ifc,
    send_message,
    receive_message
)

__all__ = [
    # Message Models
    'SSIMessage',
    'MessageResponse',
    'MessageStatus',
    'PriorityLevel',
    'ProcessType',
    'SystemStateSnapshot',
    'ModuleIdentifier',
    
    # Message Factory
    'MessageFactory',
    
    # Message Router
    'MessageRouter',
    'get_router',
    
    # Message History
    'MessageHistory',
    'MessageRecord',
    'HistoryConfig',
    'get_history',
    
    # Context Manager
    'ContextManager',
    'ContextSnapshot',
    'ContextUpdate',
    'ExecutionMode',
    'SystemStatus',
    'get_context_manager',
    'get_current_context',
    
    # IFC Controller
    'InformationFlowController',
    'IFCConfig',
    'IFCTStatistics',
    'get_ifc',
    'send_message',
    'receive_message'
]

__version__ = "2.0.0"