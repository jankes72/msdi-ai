"""
SSI V3 Relationship Memory - Pamięć relacji

Specjalizowana pamięć dla relacji między obiektami systemu.

Zgodnie z:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 3.1
- 02_DATA_STRUCTURE.md Sekcja 4.1

Odpowiedzialność:
- Przechowywanie relacji między obiektami
- Typy relacji (depends_on, influences, part_of, contains, etc.)
- Graf relacji
- Wyszukiwanie połączeń

Wersja: 1.0
Data: 2026-07-28
"""

# Ten moduł jest zintegrowany z MemoryManager
# Funkcjonalność relacji jest obsługiwana przez:
# - MemoryManager.add_relationship()
# - MemoryManager.get_relationships()
# - RelationshipMemory (klasa w memory_manager.py)

# Import dla spójności
from .memory_manager import RelationshipMemory

__all__ = ['RelationshipMemory']
