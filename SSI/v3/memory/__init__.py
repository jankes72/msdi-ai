"""
SSI V3 Memory System - System Pamięci

Moduł odpowiedzialny za:
- Centralną pamięć systemu SSI
- Organizację danych w różne typy pamięci
- Integrację z V2 (obserwacje) i V4 (agenci)

Typy pamięci:
- Observation Memory: Pamięć obserwacji z V2
- Pattern Memory: Pamięć wzorców zachowań
- Metadata Memory: Pamięć metadanych
- Relationship Memory: Pamięć relacji między obiektami
- World Memory: Pamięć światów

Zgodnie z:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 3.1
- 02_DATA_STRUCTURE.md Sekcja 4.1

Wersja: 1.0
Data: 2026-07-28
"""

from .memory_manager import (
    MemoryManager, MemoryConfig, MemoryType, tworz_memory_manager
)
from .observation_memory import ObservationMemory
from .pattern_memory import PatternMemory
from .metadata_memory import MetadataMemory
from .relationship_memory import RelationshipMemory
from .world_memory import WorldMemory

__all__ = [
    # Main Manager
    'MemoryManager', 'MemoryConfig', 'MemoryType', 'tworz_memory_manager',
    
    # Memory Types
    'ObservationMemory',
    'PatternMemory', 
    'MetadataMemory',
    'RelationshipMemory',
    'WorldMemory'
]
