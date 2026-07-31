"""
SSI V5 Input Layer
Warstwa wejścia danych dla modelu językowego V5

Odpowiedzialność:
- Pobieranie danych z V2, V3, V4
- Odbiór informacji od agentów, laboratoriów, programisty
- Normalizacja i pakowanie danych wejściowych

Wersja: 1.0
Data: 2026-07-31
"""

# Importy będą dodawane w kolejnych sprintach
# Sprint 11.1: V2 Collector
from .v2_collector import V2DataCollector, V2DataPackage, ModelInfo

# Sprint 11.2: V3 Collector
from .v3_collector import V3KnowledgeCollector, V3DataPackage

# Sprint 11.3: V4 Collector
from .v4_collector import V4AgentsCollector, V4DataPackage

# Sprint 11.4: External Input
# from .agents_input import AgentsInputCollector
# from .labs_input import LabsInputCollector
# from .dev_input import DevInputCollector

# Sprint 11.5: Integration
# from .input_manager import InputManager

__all__ = [
    # Sprint 11.1
    'V2DataCollector', 'V2DataPackage', 'ModelInfo',
    # Sprint 11.2
    'V3KnowledgeCollector', 'V3DataPackage',
    # Sprint 11.3
    'V4AgentsCollector', 'V4DataPackage'
]
