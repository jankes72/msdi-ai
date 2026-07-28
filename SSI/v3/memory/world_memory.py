"""
SSI V3 World Memory - Pamięć światów

Specjalizowana pamięć dla światów danych systemu SSI.

Zgodnie z:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 3.2 (Światy)
- 02_DATA_STRUCTURE.md Sekcja 4.2

Odpowiedzialność:
- Przechowywanie definicji światów
- Organizacja obserwacji, wzorców, metadanych w światy
- Hierarchia światów
- pobieranie i aktywowanie światów

Typy światów (z dokumentacji):
- Świat 1: Zmiany kursów (11 sieci trendów)
- Świat 2: Dynamika/Amplituda (Sieci 2-4)
- Świat 3: Złożone wzorce
- Świat 4: Relacje i synchronizacje

Wersja: 1.0
Data: 2026-07-28
"""

# Ten moduł jest zintegrowany z MemoryManager
# Funkcjonalność światów jest obsługiwana przez:
# - MemoryManager.add_world()
# - MemoryManager.get_world()
# - MemoryManager.list_worlds()
# - WorldMemory (klasa w memory_manager.py)

# Import dla spójności
from .memory_manager import WorldMemory

__all__ = ['WorldMemory']
