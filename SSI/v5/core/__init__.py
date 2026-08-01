"""
SSI V5 Core Layer

Core layer zawiera fundamentalne systemy SSI V5 Fazy 2:
- Information Flow Controller (IFC) - Centralny system komunikacji
- Message Validation - Walidacja i integralność wiadomości
- Context Integrity - Zarządzanie i korekta kontekstu
- Decision Layer - Warstwa decyzji
- Developer Interface - Interfejs programisty

Wersja: 2.0.0
Data: 2026-08-01

NOTE: Tylko Information Flow Controller jest dostępny w tej chwili.
Pozostałe moduły (Validation, Context Integrity, Decision Layer, Developer Interface)
będą dodawane w kolejnych etapach Fazy 2.
"""

# Information Flow Controller - ETAP 2.1 (Gotowy)
from SSI.v5.core.information_flow_controller import (
    ifc_controller,
    message_models,
    message_factory,
    message_router,
    message_history,
    context_manager
)

# Validation - ETAP 2.2 (W przygotowaniu)
# from SSI.v5.core.validation import (
#     message_validator,
#     context_validator,
#     schema_validator,
#     validation_rules
# )

# Context Integrity - ETAP 2.2 (W przygotowaniu)
# from SSI.v5.core.context_integrity import (
#     context_integrity_layer,
#     dynamic_context_correction,
#     context_monitor
# )

# Decision Layer - ETAP 2.4 (W przygotowaniu)
# from SSI.v5.core.decision_layer import (
#     decision_engine,
#     decision_analyzer,
#     decision_comparator,
#     decision_selector,
#     decision_store,
#     decision_models
# )

# Developer Interface - ETAP 2.5 (W przygotowaniu)
# from SSI.v5.core.developer_interface import (
#     developer_input_controller,
#     command_parser,
#     command_executor,
#     report_generator,
#     test_manager,
#     module_loader,
#     developer_models
# )

__all__ = [
    # Information Flow Controller - ETAP 2.1
    'ifc_controller',
    'message_models', 
    'message_factory',
    'message_router',
    'message_history',
    'context_manager',
    
    # Validation - ETAP 2.2 (do dodania późnoej)
    # 'message_validator',
    # 'context_validator',
    # 'schema_validator',
    # 'validation_rules',
    
    # Context Integrity - ETAP 2.2 (do dodania późnoej)
    # 'context_integrity_layer',
    # 'dynamic_context_correction',
    # 'context_monitor',
    
    # Decision Layer - ETAP 2.4 (do dodania późnoej)
    # 'decision_engine',
    # 'decision_analyzer',
    # 'decision_comparator',
    # 'decision_selector',
    # 'decision_store',
    # 'decision_models',
    
    # Developer Interface - ETAP 2.5 (do dodania późnoej)
    # 'developer_input_controller',
    # 'command_parser',
    # 'command_executor',
    # 'report_generator',
    # 'test_manager',
    # 'module_loader',
    # 'developer_models'
]

__version__ = "2.0.0"
__author__ = "MSDI AI / SSI System"
__phase__ = "2"