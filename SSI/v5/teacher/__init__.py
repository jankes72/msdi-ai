"""
SSI V5 - Teacher Engine
Silnik nauczyciel - uczenie i obserwacja agentow

Zgodnie z dokumentacja:
- 04_AGENT_MEMORY_BEHAVIOR_EVOLUTION.md (Agent Memory & Behavior Evolution)
- 02_DEVELOPER_INPUT_ARCHITECTURE.md (Zasady uczenia)

Moduly:
- teacher_engine.py: Glowny silnik nauczyciela
- teacher_config.py: Konfiguracja
"""

from .teacher_config import (
    TeacherConfig,
    TeacherMode,
    TeachingStrategy,
    TeacherStatus,
    ObservationStatus
)

from .teacher_engine import (
    TeacherEngine,
    create_teacher_engine,
    get_teacher_engine
)

__all__ = [
    'TeacherConfig',
    'TeacherMode', 
    'TeachingStrategy',
    'TeacherStatus',
    'ObservationStatus',
    'TeacherEngine',
    'create_teacher_engine',
    'get_teacher_engine'
]
