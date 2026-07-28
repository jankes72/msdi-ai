"""
SSI V3 Worlds - System Światów

Moduł odpowiedzialny za:
- Zarządzanie światami danych
- Budowanie i analizę światów
- Organizację pamięci w światy
- Hierarchię i zależności między światami

Zgodnie z dokumentacją:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 3.2
- 02_DATA_STRUCTURE.md Sekcja 4.2

Typy światów (z dokumentacji):
- Świat 1: Zmiany kursów (11 sieci trendów z V2)
- Świat 2: Dynamika/Amplituda (Sieci 2-4 z V2)
- Świat 3: Złożone wzorce (Analiza puissance)
- Świat 4: Relacje i synchronizacje (powiązania między danymi)

Wersja: 1.0
Data: 2026-07-28
"""

from .world_manager import (
    WorldManager,
    WorldAccess, tworz_world_manager
)
from .world import World, WorldConfig, WorldType, WorldStatus
from .world_knowledge_engine import (
    WorldKnowledgeEngine, WorldKnowledgeConfig, WorldSource,
    PatternType, EconomicMetric,
    WorldCreator, PatternDetector, EconomicAnalyzer, EVCalculator,
    tworz_world_knowledge_engine
)

__all__ = [
    # Main Components
    'WorldManager', 'WorldConfig', 'World',
    'WorldAccess',
    
    # Enums and Types
    'WorldType', 'WorldStatus',
    
    # Factory
    'tworz_world_manager',
    
    # World Knowledge Engine
    'WorldKnowledgeEngine', 'WorldKnowledgeConfig', 'WorldSource',
    'PatternType', 'EconomicMetric',
    'WorldCreator', 'PatternDetector', 'EconomicAnalyzer', 'EVCalculator',
    'tworz_world_knowledge_engine'
]
