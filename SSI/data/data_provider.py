"""
SSI Data Provider - Implementacja interfejsu DataProvider

Implementuje interfejs DataProvider z SSI Core dla warstwy Data World.
Dostarcza dane do V2 Model Laboratory i innych modułów.

Wersja: 1.0
Data: 2026-07-28

Zgodność z dokumentacją: 01_SYSTEM_ARCHITECTURE.md
"""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import logging

from SSI.core.interfaces import DataProvider

logger = logging.getLogger(__name__)


class CSVDataProvider(DataProvider):
    """
    Implementacja DataProvider dla plików CSV
    
    Dostarcza dane z kursy_przygotowane.csv i innych plików CSV.
    """
    
    def __init__(self, csv_loader: Any):
        """
        Inicjalizacja z CSVLoader
        
        Args:
            csv_loader: Obiekt klasy CSVLoader lub dziedziczącej
        """
        self.csv_loader = csv_loader
        self.available_data_types = ["raw_courses", "course_data", "match_data", "trend_data"]
        logger.info("CSVDataProvider zainicjowany")
    
    def get_data(self, data_type: str, **kwargs) -> Any:
        """
        Pobieranie danych określonego typu
        
        Args:
            data_type: Typ danych
            **kwargs: Dodatkowe parametry
            
        Returns:
            Dane lub None
        """
        if data_type == "raw_courses":
            return self.csv_loader.get_data()
        elif data_type == "course_data":
            return self.csv_loader.load_courses()
        elif data_type == "match_data":
            # TODO: Zaimplementować ładowanie danych meczowych
            return None
        elif data_type == "trend_data":
            # TODO: Zaimplementować ładowanie danych trendów
            return None
        else:
            logger.error(f"Nieobsługiwany typ danych: {data_type}")
            return None
    
    def get_available_data_types(self) -> List[str]:
        """Pobieranie listy dostępnych typów danych"""
        return self.available_data_types
    
    def validate_data(self, data: Any, data_type: str) -> bool:
        """
        Walidacja danych
        
        Args:
            data: Dane do walidacji
            data_type: Typ danych
            
        Returns:
            bool: Czy dane są ważne
        """
        if not data:
            logger.error("Dane są puste")
            return False
        
        if data_type == "course_data" and isinstance(data, list):
            # Walidacja listy CourseData
            for item in data:
                if not hasattr(item, 'mecz') or not hasattr(item, 'kurs_1_start'):
                    logger.error("Nieprawidłowy format CourseData")
                    return False
            return True
        
        return True


class DataWorldProvider(DataProvider):
    """
    Główny dostawca danych dla systemu SSI
    
    Integruje wszystkie źródła danych i dostarcza je innym modułom.
    """
    
    def __init__(self):
        self.data_sources: Dict[str, DataProvider] = {}
        self.available_data_types: List[str] = []
        logger.info("DataWorldProvider zainicjowany")
    
    def register_source(self, source_name: str, provider: DataProvider) -> None:
        """
        Rejestrowanie nowego źródła danych
        
        Args:
            source_name: Nazwa źródła
            provider: Obiekt implementujący DataProvider
        """
        self.data_sources[source_name] = provider
        self.available_data_types.extend(provider.get_available_data_types())
        logger.info(f"Zarejestrowano źródło: {source_name}")
    
    def get_data(self, data_type: str, source: str = None, **kwargs) -> Any:
        """
        Pobieranie danych
        
        Args:
            data_type: Typ danych
            source: Konkretne źródło (opcjonalnie)
            **kwargs: Dodatkowe parametry
            
        Returns:
            Dane lub None
        """
        if source and source in self.data_sources:
            return self.data_sources[source].get_data(data_type, **kwargs)
        
        # Szukaj danych we wszystkich źródłach
        for name, provider in self.data_sources.items():
            if data_type in provider.get_available_data_types():
                return provider.get_data(data_type, **kwargs)
        
        logger.error(f"Nie można znaleźć danych typu: {data_type}")
        return None
    
    def get_available_data_types(self) -> List[str]:
        """Pobieranie listy dostępnych typów danych"""
        return list(set(self.available_data_types))
    
    def validate_data(self, data: Any, data_type: str) -> bool:
        """Walidacja danych"""
        for provider in self.data_sources.values():
            if data_type in provider.get_available_data_types():
                return provider.validate_data(data, data_type)
        return False
    
    def get_data_sources(self) -> Dict[str, DataProvider]:
        """Pobieranie zarejestrowanych źródeł"""
        return self.data_sources
    
    def has_source(self, source_name: str) -> bool:
        """Sprawdzenie czy źródło jest zarejestrowane"""
        return source_name in self.data_sources
