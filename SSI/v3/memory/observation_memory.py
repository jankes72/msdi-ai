"""
SSI V3 Observation Memory - Pamięć obserwacji

Specjalizowana pamięć dla obserwacji z systemu V2.

Zgodnie z:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 3.1
- 02_DATA_STRUCTURE.md Sekcja 4.1

Odpowiedzialność:
- Przechowywanie obserwacji (predykcja vs rzeczywistość)
- Indeksowanie po meczach, modelach, grupach
- Statystyki trafności
- Integracja z MemoryManager

Wersja: 1.0
Data: 2026-07-28
"""

# Ten moduł jest zintegrowany z MemoryManager
# Funkcjonalność obserwacji jest obsługiwana przez:
# - MemoryManager.add_observation()
# - MemoryManager.get_observation()
# - ObservationMemory (klasa w memory_manager.py)

# Import dla spójności
from .memory_manager import ObservationMemory

__all__ = ['ObservationMemory']
