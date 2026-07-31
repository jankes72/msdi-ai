"""
SSI V5 - External Input Layer
Warstwa zewnetrznych zrodel danych dla SSI V5

Odpowiedzialnosc:
- Zbieranie danych od programisty
- Zbieranie danych z laboratoriow
- Zbieranie danych od agentow
- Zbieranie danych systemowych

Struktura:
external/
├── source_types.py - Typy zrodel i statusy
├── external_models.py - Modele danych (FAZA 2)
├── external_collector.py - Glowny kolektor (FAZA 4)
├── sources/ - Handlery zrodel (FAZA 3)
│   ├── developer_source.py
│   ├── laboratory_source.py
│   ├── agent_source.py
│   └── system_source.py
└── validators/ - Walidatory (FAZA 3)
    ├── developer_validator.py
    ├── laboratory_validator.py
    ├── agent_validator.py
    └── system_validator.py

Wersja: 1.0
Data: 2026-07-31
"""

# FAZA 1: Podstawowe typy
from .source_types import (
    SourceType,
    LaboratoryType,
    ExternalStatus,
    SOURCE_TYPE_MAP,
    LABORATORY_TYPE_MAP,
    STATUS_MAP,
    get_source_type_from_string,
    get_laboratory_type_from_string
)

# FAZA 2: Modele danych
from .external_models import (
    # Developer
    DeveloperCommand,
    Requirement,
    ArchitectureDecision,
    DeveloperInput,
    # Laboratory
    ExperimentResult,
    DiscoveryRecord,
    LaboratoryData,
    # Agent
    MessageType,
    EventType,
    AgentMessage,
    AgentEvent,
    AgentInputData,
    # System
    LogLevel,
    SystemStatusType,
    SystemEvent,
    SystemStatus,
    SystemMessages,
    # Package
    ExternalDataPackage,
    # Fabryki
    create_developer_command,
    create_requirement,
    create_architecture_decision,
    create_experiment_result,
    create_discovery_record,
    create_agent_message,
    create_agent_event,
    create_system_event,
    create_system_status,
    create_external_package
)

# FAZA 3: Source Handlers
from .sources import (
    DeveloperSource,
    LaboratorySource,
    AgentSource,
    SystemSource
)

# FAZA 4: Kolektor
from .external_collector import ExternalKnowledgeCollector

__all__ = [
    # Typy zrodel
    'SourceType',
    'LaboratoryType', 
    'ExternalStatus',
    # Mapy
    'SOURCE_TYPE_MAP',
    'LABORATORY_TYPE_MAP',
    'STATUS_MAP',
    # Funkcje pomocnicze
    'get_source_type_from_string',
    'get_laboratory_type_from_string',
    # Modele Developer
    'DeveloperCommand',
    'Requirement',
    'ArchitectureDecision',
    'DeveloperInput',
    # Modele Laboratory
    'ExperimentResult',
    'DiscoveryRecord',
    'LaboratoryData',
    # Modele Agent
    'MessageType',
    'EventType',
    'AgentMessage',
    'AgentEvent',
    'AgentInputData',
    # Modele System
    'LogLevel',
    'SystemStatusType',
    'SystemEvent',
    'SystemStatus',
    'SystemMessages',
    # Pakiet
    'ExternalDataPackage',
    # Fabryki
    'create_developer_command',
    'create_requirement',
    'create_architecture_decision',
    'create_experiment_result',
    'create_discovery_record',
    'create_agent_message',
    'create_agent_event',
    'create_system_event',
    'create_system_status',
    'create_external_package',
    # FAZA 3: Source Handlers
    'DeveloperSource',
    'LaboratorySource',
    'AgentSource',
    'SystemSource',
    # FAZA 4: Kolektor
    'ExternalKnowledgeCollector'
]
