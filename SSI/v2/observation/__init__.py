"""
SSI V2 Observation - Obserwacja modeli

Moduł odpowiedzialny za:
- Niezależną obserwację na 40% danych
- Tworzenie pamięci modeli
- Wykrywanie wzorców
- Monitorowanie zachowania modeli

Zgodnie z dokumentacją:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 2.2 (40% obserwacja)
- 02_DATA_STRUCTURE.md

Wersja: 1.0
Data: 2026-07-28
"""

from .model_observer import ModelObserver, ObservationConfig, ObservationResult
from .pattern_detector import PatternDetector
from .memory_builder import MemoryBuilder, MemoryConfig, tworzenie_memory_builder as tworz_memory_builder

__all__ = [
    'ModelObserver', 'ObservationConfig', 'ObservationResult',
    'PatternDetector', 'MemoryBuilder', 'MemoryConfig', 'tworz_memory_builder'
]
