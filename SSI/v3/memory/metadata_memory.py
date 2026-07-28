"""
SSI V3 Metadata Memory - Pamięć metadanych

Specjalizowana pamięć dla metadanych systemu.

Zgodnie z:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 3.1
- 02_DATA_STRUCTURE.md Sekcja 4.1

Odpowiedzialność:
- Przechowywanie metadanych encji (modele, światy, agenci itd.)
- Indeksowanie po typach encji
- Wersjonowanie metadanych
- Historia zmian

Wersja: 1.0
Data: 2026-07-28
"""

# Ten moduł jest zintegrowany z MemoryManager
# Funkcjonalność metadanych jest obsługiwana przez:
# - MemoryManager.add_metadata()
# - MemoryManager.get_metadata()
# - MetadataMemory (klasa w memory_manager.py)

# Import dla spójności
from .memory_manager import MetadataMemory

__all__ = ['MetadataMemory']
