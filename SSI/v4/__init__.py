"""
SSI V4 - Autonomous Agent Ecosystem
Warstwa agentów - Ewolucyjny system autonomicznych agentów

Odpowiedzialność:
- Narodziny i ewolucja agentów
- System osobowości i emocji
- System zaufania między agentami
- Pamięć agentów
- Podejmowanie decyzji przez agenty

Zgodnie z:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 4 (V4 Agent System)
- 05_AGENT_SYSTEM.md
- 10_IMPLEMENTATION_MAP.md Fazy 4-7

Architektura V4:
┌─────────────────────────────────────────────────────────────┐
│                    V4 AGENT ECOSYSTEM                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐      ┌─────────────────┐                 │
│  │   ROOM CORE     │      │ AGENT BIRTH     │                 │
│  │  (Pokój Narodzin)│      │   SYSTEM        │                 │
│  └────────┬────────┘      └────────┬────────┘                 │
│           │                       │                             │
│           └───────────────────────┬─────────────────────────┘  │
│                               ↓                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    AGENCI                             │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │ │
│  │  │   Agent    │  │ Personality│  │  Memory    │       │ │
│  │  │   Core    │  │  Vector   │  │  System    │       │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │ │
│  │                                                       │ │
│  │  ┌─────────────┐  ┌─────────────┐                         │ │
│  │  │Emotional    │  │ Trust &     │                         │ │
│  │  │System       │  │ Reputation  │                         │ │
│  │  └─────────────┘  └─────────────┘                         │ │
│  └─────────────────────────────────────────────────────────┘ │
│                              ↓                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │               POPULACJA AGENTÓW                           │ │
│  │  - Multi-Agent Decision Making                           │ │
│  │  - Współpraca i rywalizacja                               │ │
│  │  - Ewolucja i adaptacja                                   │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Zależności:
- Zależy od: V3 World Memory System (dane wejściowe)
- Wspiera: Strategy System, Laboratories, Decision Engine

Wersja: 1.0
Data: 2026-07-28
"""

# Agent Core
from .agent_core import (
    Agent,
    AgentStatus,
    AgentType,
    AgentConfig,
    AgentManager,
    tworz_agent
)

# Agent Birth System
from .agent_birth_system import (
    AgentBirthSystem,
    BirthConfig,
    BirthMode,
    BirthResult,
    tworz_agent_birth_system
)

# Room Core
from .room_core import (
    RoomCore,
    RoomConfig,
    RoomType,
    RoomStatus,
    tworz_room_core
)

# Personality Vector
from .personality_vector import (
    PersonalityVector as V4PersonalityVector,
    PersonalityConfig,
    PersonalityTrait,
    PersonalityEngine,
    tworz_personality_vector
)

__all__ = [
    # Agent Core
    'Agent',
    'AgentStatus',
    'AgentType',
    'AgentConfig',
    'AgentManager',
    'tworz_agent',
    
    # Agent Birth System (Etap 4A)
    'AgentBirthSystem',
    'BirthConfig',
    'BirthMode',
    'BirthResult',
    'tworz_agent_birth_system',
    
    # Room Core (Etap 4A)
    'RoomCore',
    'RoomConfig',
    'RoomType',
    'RoomStatus',
    'tworz_room_core',
    
    # Personality Vector (Etap 4B)
    'V4PersonalityVector',
    'PersonalityConfig',
    'PersonalityTrait',
    'PersonalityEngine',
    'tworz_personality_vector'
]
