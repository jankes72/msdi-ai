"""
SSI V3 Pattern Memory - Pamięć wzorców zachowań

Specjalizowana pamięć dla wzorców zachowań wykrytych w systemie.

Zgodnie z:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 3.1
- 02_DATA_STRUCTURE.md Sekcja 4.1

Odpowiedzialność:
- Przechowywanie wykrytych wzorców
- Klasyfikacja wzorców (normal, anomaly, trend, cycle)
- Statystyki występowania wzorców
- Integracja z PatternDetector

Wersja: 1.0
Data: 2026-07-28
"""

# Ten moduł jest zintegrowany z MemoryManager
# Funkcjonalność wzorców jest obsługiwana przez:
# - MemoryManager.add_pattern()
# - MemoryManager.get_pattern()
# - MemoryManager.find_patterns()
# - PatternMemory (klasa w memory_manager.py)

# Import dla spójności
from .memory_manager import PatternMemory

__all__ = ['PatternMemory']
