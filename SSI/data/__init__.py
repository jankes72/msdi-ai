"""
SSI Data World Foundation
Warstwa danych systemu SSI

Ten moduł dostarcza:
- Zarządzanie danymi wejściowymi
- Ładowanie i przetwarzanie plików CSV
- Podział 60/40 (trening/obserwacja) dla V2
- Interfejs DataProvider
- Struktury danych zgodne z dokumentacją

Zgodność z dokumentacją:
- 01_SYSTEM_ARCHITECTURE.md (Data Intelligence Layer)
- 02_DATA_STRUCTURE.md (Dane Pierwotne)

Wersja: 1.0
Data: 2026-07-28
"""

from .data_manager import (
    DataWorldManager, DataSourceConfig, DataPartition,
    create_data_world_manager, get_data_world_manager, set_data_world_manager
)
from .data_provider import CSVDataProvider, DataWorldProvider
from .data_structures import (
    CourseData, MatchData, TrendData, DataMetadata,
    DataQualityReport, DataSplitConfig
)
from .csv_loader import CSVLoader, CourseCSVLoader

__all__ = [
    # Manager
    'DataWorldManager', 'DataSourceConfig', 'DataPartition',
    'create_data_world_manager', 'get_data_world_manager', 'set_data_world_manager',
    # Provider
    'CSVDataProvider', 'DataWorldProvider',
    # Struktury danych
    'CourseData', 'MatchData', 'TrendData', 'DataMetadata',
    'DataQualityReport', 'DataSplitConfig',
    # Loader
    'CSVLoader', 'CourseCSVLoader'
]
