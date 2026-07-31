"""
SSI Data Manager - Główny zarządca danymi warstwy Data World

Zgodnie z dokumentacją:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 2.1 (Data Intelligence Layer)
- 02_DATA_STRUCTURE.md Sekcja 2 (Dane Pierwotne) i 3 (Podział 60/40)

Odpowiedzialność:
- Centralne zarządzanie danymi wejściowymi (kursy_przygotowane.csv, wyniki)
- Inicjalizacja i konfiguracja źródeł danych
- Podział danych na trening (60%) i obserwacja (40%)
- Integracja z CSVLoader i DataProvider
- Dostarczanie danych do V2 Model Laboratory

Wersja: 1.0
Data: 2026-07-28
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import logging
import random
import hashlib
from pathlib import Path
import sys

from .data_structures import (
    CourseData, MatchData, TrendData, DataMetadata,
    DataQualityReport, DataSplitConfig
)
from .csv_loader import CSVLoader, CourseCSVLoader
from .data_provider import CSVDataProvider, DataWorldProvider

logger = logging.getLogger(__name__)


@dataclass
class DataSourceConfig:
    """
    Konfiguracja pojedynczego źródła danych
    
    Przechowuje informacje o źródle danych i jego parametrach.
    """
    name: str
    file_path: str
    data_type: str  # "courses", "matches", "results", "trends"
    delimiter: str = ";"
    is_primary: bool = False
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "file_path": self.file_path,
            "data_type": self.data_type,
            "delimiter": self.delimiter,
            "is_primary": self.is_primary,
            "enabled": self.enabled
        }


@dataclass
class DataPartition:
    """
    Reprezentuje podział danych na trening i obserwację
    
    Zgodnie z zasadą 60/40:
    - 60% na trening + walidację
    - 40% na niezależną obserwację
    """
    training_data: List[Any] = field(default_factory=list)
    validation_data: List[Any] = field(default_factory=list)
    observation_data: List[Any] = field(default_factory=list)
    split_config: DataSplitConfig = field(default_factory=DataSplitConfig)
    
    @property
    def training_count(self) -> int:
        return len(self.training_data)
    
    @property
    def validation_count(self) -> int:
        return len(self.validation_data)
    
    @property
    def observation_count(self) -> int:
        return len(self.observation_data)
    
    @property
    def total_count(self) -> int:
        return self.training_count + self.validation_count + self.observation_count
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "training_count": self.training_count,
            "validation_count": self.validation_count,
            "observation_count": self.observation_count,
            "total_count": self.total_count,
            "split_config": self.split_config.to_dict()
        }


class DataWorldManager:
    """
    Główny zarządca danymi systemu SSI - Data World Foundation
    
    Kluczowe funkcjonalności:
    - Inicjalizacja źródeł danych (CSV, inne)
    - Ładowanie i walidacja danych wejściowych
    - Podział danych zgodnie z zasadą 60/40
    - Zarządzanie dostępem do danych dla innych modułów
    - Integracja z V2 Model Laboratory
    
    Zgodność z:
    - 01_SYSTEM_ARCHITECTURE.md Sekcja 2.1
    - 02_DATA_STRUCTURE.md Sekcje 2, 3.1, 3.2
    """
    
    # Konfiguracja domyślna
    DEFAULT_COURSES_FILE = "kursy_przygotowane.csv"
    DEFAULT_RESULTS_FILE = "wyniki.csv"
    DEFAULT_TRENDS_FILE = "trendy.csv"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicjalizacja DataWorldManager
        
        Args:
            config: Opcjonalna konfiguracja (może zawierać ścieżki do plików, itp.)
        """
        self.config = config or {}
        self.initialized = False
        
        # Konfiguracja źródeł danych
        self.data_sources: Dict[str, DataSourceConfig] = {}
        
        # Załadowane dane
        self.raw_courses: List[CourseData] = []
        self.match_results: List[MatchData] = []
        self.trend_data: List[TrendData] = []
        
        # Podział danych
        self.partitions: Dict[str, DataPartition] = {}
        
        # Dostawcy danych
        self.csv_loader: Optional[CourseCSVLoader] = None
        self.data_provider: Optional[DataWorldProvider] = None
        
        # Metadane
        self.metadata: Dict[str, DataMetadata] = {}
        self.quality_reports: Dict[str, DataQualityReport] = {}
        
        logger.info("DataWorldManager utworzony")
    
    def initialize(self, courses_file: str = DEFAULT_COURSES_FILE,
                  results_file: str = DEFAULT_RESULTS_FILE) -> bool:
        """
        Inicjalizacja menedżera z domyślnymi źródłami danych
        
        Args:
            courses_file: Ścieżka do pliku kursy_przygotowane.csv
            results_file: Ścieżka do pliku z wynikami meczów
            
        Returns:
            bool: Czy inicjalizacja się powiodła
        """
        try:
            # 1. Konfiguracja źródeł danych
            self._configure_data_sources(courses_file, results_file)
            
            # 2. Inicjalizacja loaderów
            if not self._initialize_loaders():
                return False
            
            # 3. Inicjalizacja dostawców
            if not self._initialize_providers():
                return False
            
            # 4. Ładowanie danych
            if not self.load_all_data():
                return False
            
            # 5. Podział danych
            if not self.split_data():
                return False
            
            self.initialized = True
            logger.info("DataWorldManager zainicjalizowany pomyślnie")
            return True
            
        except Exception as e:
            logger.error(f"Błąd inicjalizacji DataWorldManager: {e}")
            return False
    
    def _configure_data_sources(self, courses_file: str, results_file: str) -> None:
        """Konfiguracja źródeł danych"""
        self.data_sources = {
            "courses": DataSourceConfig(
                name="courses",
                file_path=courses_file,
                data_type="courses",
                delimiter=";",
                is_primary=True,
                enabled=True
            ),
            "results": DataSourceConfig(
                name="results",
                file_path=results_file,
                data_type="matches",
                delimiter=";",
                is_primary=False,
                enabled=True
            )
        }
        logger.info(f"Skonfigurowano {len(self.data_sources)} źródeł danych")
    
    def _initialize_loaders(self) -> bool:
        """Inicjalizacja loaderów CSV"""
        try:
            courses_config = self.data_sources.get("courses")
            if courses_config and courses_config.enabled:
                self.csv_loader = CourseCSVLoader(
                    file_path=courses_config.file_path,
                    delimiter=courses_config.delimiter
                )
                
                # Walidacja pliku
                report = self.csv_loader.validate_file()
                self.quality_reports["courses"] = report
                
                if report.quality_score < 0.5:
                    logger.warning(f"Niska jakość danych kursowych: {report.quality_score}")
                    return False
            
            logger.info("CSV Loader zainicjalizowany")
            return True
            
        except Exception as e:
            logger.error(f"Błąd inicjalizacji loaderów: {e}")
            return False
    
    def _initialize_providers(self) -> bool:
        """Inicjalizacja dostawców danych"""
        try:
            if self.csv_loader:
                # Tworzenie CSVDataProvider
                csv_provider = CSVDataProvider(self.csv_loader)
                
                # Tworzenie głównego DataWorldProvider
                self.data_provider = DataWorldProvider()
                self.data_provider.register_source("csv", csv_provider)
                
                logger.info("Data providers zainicjalizowani")
                return True
            else:
                logger.error("BrakCSV Loader - nie można zainicjalizować providerów")
                return False
                
        except Exception as e:
            logger.error(f"Błąd inicjalizacji providerów: {e}")
            return False
    
    def load_all_data(self) -> bool:
        """
        Ładowanie wszystkich danych z ببر Erwerdeł
        
        Returns:
            bool: Czy ładowanie się powiodło
        """
        try:
            # 1. Ładowanie danych kursowych
            if self.csv_loader:
                self.raw_courses = self.csv_loader.load_courses()
                logger.info(f"Załadowano {len(self.raw_courses)} rekordów kursowych")
                
                # Metadane
                self.metadata["courses"] = DataMetadata(
                    source_file=self.data_sources["courses"].file_path,
                    data_type="processed",
                    total_records=len(self.raw_courses),
                    valid_records=len([c for c in self.raw_courses if c.mecz])
                )
            
            # 2. Ładowanie wyników meczów (jeśli dostępne)
            results_config = self.data_sources.get("results")
            if results_config and results_config.enabled:
                self._load_match_results(results_config.file_path)
            
            logger.info(f"Załadowano wszystkie dane: {len(self.raw_courses)} kursy, "
                       f"{len(self.match_results)} wyniki")
            return True
            
        except Exception as e:
            logger.error(f"Błąd ładowania danych: {e}")
            return False
    
    def _load_match_results(self, file_path: str) -> None:
        """Ładowanie wyników meczów"""
        try:
            results_loader = CSVLoader(file_path)
            if results_loader.load():
                data = results_loader.get_data()
                for row in data:
                    try:
                        match = MatchData(
                            mecz=row.get("mecz", ""),
                            wynik=row.get("wynik"),
                            data_meczu=row.get("data"),
                            source=file_path
                        )
                        self.match_results.append(match)
                    except Exception as e:
                        logger.warning(f"Błąd konwersji wyniku: {e}")
                        continue
                
                logger.info(f"Załadowano {len(self.match_results)} wyników meczów")
                
        except Exception as e:
            logger.error(f"Błąd ładowania wyników: {e}")
    
    def split_data(self, split_config: Optional[DataSplitConfig] = None) -> bool:
        """
        Podział danych zgodnie z zasadą 60/40
        
        Zasada podziału:
        - 60% na trening + walidację
        - 40% na niezależną obserwację
        
        Args:
            split_config: Opcjonalna konfiguracja podziału
            
        Returns:
            bool: Czy podział się powiodł
        """
        try:
            if not self.raw_courses:
                logger.error("Brak danych do podziału")
                return False
            
            config = split_config or self._get_default_split_config()
            
            # Mieszanie danych (opcjonalnie)
            if config.shuffle:
                random.seed(config.random_state)
                shuffled_data = self.raw_courses.copy()
                random.shuffle(shuffled_data)
            else:
                shuffled_data = self.raw_courses
            
            total_count = len(shuffled_data)
            
            # 60% na trening + walidację
            train_val_count = int(total_count * config.training_split)
            
            # W ramach 60%: podział na trening i walidację
            train_count = int(train_val_count * config.training_split)
            val_count = train_val_count - train_count
            
            # 40% na obserwację
            obs_count = total_count - train_val_count
            
            # Tworzenie partiji
            self.partitions["courses"] = DataPartition(
                training_data=shuffled_data[:train_count],
                validation_data=shuffled_data[train_count:train_val_count],
                observation_data=shuffled_data[train_val_count:],
                split_config=config
            )
            
            logger.info(
                f"Podział danych: "
                f"Trening={train_count}, "
                f"Walidacja={val_count}, "
                f"Obserwacja={obs_count}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Błąd podziału danych: {e}")
            return False
    
    def _get_default_split_config(self) -> DataSplitConfig:
        """Pobieranie domyślnej konfiguracji podziału"""
        return DataSplitConfig(
            training_split=0.6,
            validation_split=0.4,
            observation_split=0.4,
            shuffle=True,
            random_state=42
        )
    
    def get_training_data(self, data_type: str = "courses") -> List[Any]:
        """
        Pobieranie danych treningowych
        
        Args:
            data_type: Typ danych ("courses", "matches", itd.)
            
        Returns:
            List[Any]: Dane treningowe
        """
        partition = self.partitions.get(data_type)
        if partition:
            return partition.training_data
        return []
    
    def get_validation_data(self, data_type: str = "courses") -> List[Any]:
        """
        Pobieranie danych walidacyjnych
        
        Args:
            data_type: Typ danych
            
        Returns:
            List[Any]: Dane walidacyjne
        """
        partition = self.partitions.get(data_type)
        if partition:
            return partition.validation_data
        return []
    
    def get_observation_data(self, data_type: str = "courses") -> List[Any]:
        """
        Pobieranie danych obserwacyjnych (40%)
        
        Args:
            data_type: Typ danych
            
        Returns:
            List[Any]: Dane obserwacyjne
        """
        partition = self.partitions.get(data_type)
        if partition:
            return partition.observation_data
        return []
    
    def get_partition(self, data_type: str = "courses") -> Optional[DataPartition]:
        """
        Pobieranie pełnego podziału dla danego typu danych
        
        Args:
            data_type: Typ danych
            
        Returns:
            DataPartition lub None
        """
        return self.partitions.get(data_type)
    
    def get_data_provider(self) -> Optional[DataWorldProvider]:
        """
        Pobieranie głównego dostawcy danych
        
        Returns:
            DataWorldProvider lub None
        """
        return self.data_provider
    
    def get_data_by_type(self, data_type: str, **kwargs) -> Any:
        """
        Pobieranie danych określonego typu z danych provider
        
        Args:
            data_type: Typ danych
            **kwargs: Dodatkowe parametry
            
        Returns:
            Dane lub None
        """
        if self.data_provider:
            return self.data_provider.get_data(data_type, **kwargs)
        return None
    
    def get_course_data(self) -> List[CourseData]:
        """Pobieranie Raw KursyDanych"""
        return self.raw_courses
    
    def get_match_results(self) -> List[MatchData]:
        """Pobieranie wyników meczów"""
        return self.match_results
    
    def get_metadata(self, source: str = "courses") -> Optional[DataMetadata]:
        """Pobieranie metadanych dla źródła"""
        return self.metadata.get(source)
    
    def get_quality_report(self, source: str = "courses") -> Optional[DataQualityReport]:
        """Pobieranie raportu jakości dla źródła"""
        return self.quality_reports.get(source)
    
    def add_data_source(self, name: str, config: DataSourceConfig) -> None:
        """
        Dodawanie nowego źródła danych
        
        Args:
            name: Nazwa źródła
            config: Konfiguracja źródła
        """
        self.data_sources[name] = config
        logger.info(f"Dodano źródło danych: {name}")
    
    def remove_data_source(self, name: str) -> bool:
        """
        Usuwanie źródła danych
        
        Args:
            name: Nazwa źródła
            
        Returns:
            bool: Czy usunięcie się powiodło
        """
        if name in self.data_sources:
            del self.data_sources[name]
            logger.info(f"Usunięto źródło danych: {name}")
            return True
        return False
    
    def enable_data_source(self, name: str, enabled: bool = True) -> bool:
        """
        Włączanie/wyłączanie źródła danych
        
        Args:
            name: Nazwa źródła
            enabled: Czy włączyć (True) czy wyłączyć (False)
            
        Returns:
            bool: Czy operacja się powiodła
        """
        if name in self.data_sources:
            self.data_sources[name].enabled = enabled
            logger.info(f"źródło {name} {'włączone' if enabled else 'wyłączone'}")
            return True
        return False
    
    def reload_data(self, source: str = "courses") -> bool:
        """
        Przeładowanie danych z określonego źródła
        
        Args:
            source: Nazwa źródła
            
        Returns:
            bool: Czy przeładowanie się powiodło
        """
        try:
            if source == "courses" and self.csv_loader:
                self.raw_courses = self.csv_loader.load_courses()
                
                # Ponowny podział
                self.split_data()
                
                logger.info(f"Przeładowano dane kursowe: {len(self.raw_courses)} rekordów")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Błąd przeładowania danych: {e}")
            return False
    
    def clear_cache(self) -> None:
        """Czyszczenie pamięci podręcznej"""
        self.raw_courses = []
        self.match_results = []
        self.trend_data = []
        self.partitions = {}
        self.metadata = {}
        self.quality_reports = {}
        logger.info("Pamięć podręczna wyczyszczona")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Pobieranie podsumowania stanu menedżera
        
        Returns:
            Dict[str, Any]: Podsumowanie
        """
        return {
            "initialized": self.initialized,
            "data_sources": list(self.data_sources.keys()),
            "raw_courses_count": len(self.raw_courses),
            "match_results_count": len(self.match_results),
            "partitions": {k: v.to_dict() for k, v in self.partitions.items()},
            "metadata": {k: v.to_dict() for k, v in self.metadata.items()},
            "quality_reports": {k: v.to_dict() for k, v in self.quality_reports.items()}
        }
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """
        Walidacja integralności danych
        
        Returns:
            Dict[str, Any]: Raport walidacji
        """
        report = {
            "valid": True,
            "issues": [],
            "checks": {}
        }
        
        # 1. Sprawdzenie danych kursowych
        if not self.raw_courses:
            report["valid"] = False
            report["issues"].append("Brak danych kursowych")
        else:
            report["checks"]["courses_count"] = len(self.raw_courses)
        
        # 2. Sprawdzenie podziału
        courses_partition = self.partitions.get("courses")
        if courses_partition:
            total = courses_partition.total_count
            expected_total = len(self.raw_courses)
            if total != expected_total:
                report["valid"] = False
                report["issues"].append(
                    f"Niezgodność liczby rekordów: {total} vs {expected_total}"
                )
        
        # 3. Sprawdzenie jakości
        for source, q_report in self.quality_reports.items():
            if q_report.quality_score < 0.8:
                report["valid"] = False
                report["issues"].append(
                    f"Niska jakość danych {source}: {q_report.quality_score}"
                )
        
        return report
    
    def generate_data_hash(self, data_type: str = "courses") -> str:
        """
        Generowanie hasha danych dla sprawdzenia zmian
        
        Args:
            data_type: Typ danych
            
        Returns:
            str: Hash danych
        """
        import json
        
        if data_type == "courses":
            data = [c.to_dict() for c in self.raw_courses]
            data_str = json.dumps(data, sort_keys=True)
            return hashlib.md5(data_str.encode()).hexdigest()
        
        return ""


# Fabryka menedżerów danych
def create_data_world_manager(
    courses_file: str = DataWorldManager.DEFAULT_COURSES_FILE,
    results_file: str = DataWorldManager.DEFAULT_RESULTS_FILE,
    auto_initialize: bool = True
) -> DataWorldManager:
    """
    Fabryka tworząca i opcjonalnie inicjalizująca DataWorldManager
    
    Args:
        courses_file: Ścieżka do pliku kursowego
        results_file: Ścieżka do pliku wyników
        auto_initialize: Czy automatycznie zainicjalizować
        
    Returns:
        DataWorldManager
    """
    manager = DataWorldManager()
    
    if auto_initialize:
        if not manager.initialize(courses_file, results_file):
            logger.error("Błąd inicjalizacji DataWorldManager")
    
    return manager


# Singletone dla globalnego dostępu
_class_data_world_manager: Optional[DataWorldManager] = None


def get_data_world_manager() -> DataWorldManager:
    """
    Pobieranie globalnego instancji DataWorldManager (singleton)
    
    Returns:
        DataWorldManager
    """
    global _class_data_world_manager
    
    if _class_data_world_manager is None:
        _class_data_world_manager = create_data_world_manager(auto_initialize=False)
    
    return _class_data_world_manager


def set_data_world_manager(manager: DataWorldManager) -> None:
    """
    Ustawianie globalnego instancji DataWorldManager
    
    Args:
        manager: Instancja DataWorldManager
    """
    global _class_data_world_manager
    _class_data_world_manager = manager


if __name__ == "__main__":
    import logging
    from SSI.core.logging_config import (
        setup_logging, get_logger, set_correlation_id, generate_correlation_id
    )
    
    # Skonfiguruj logging
    setup_logging(level=logging.INFO, json_format=False)
    logger = get_logger(__name__)
    
    # Ustaw correlation_id
    correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)
    
    # Testy
    logger.info("Testing DataWorldManager...", extra={"correlation_id": correlation_id})
    
    # Test 1: Tworzenie i inicjalizacja
    manager = create_data_world_manager(
        courses_file="kursy_przygotowane.csv",
        auto_initialize=False
    )
    
    logger.info(f"Manager utworzony: {manager.initialized}",
                extra={"correlation_id": correlation_id})
    
    # Test 2: Podsumowanie
    summary = manager.get_summary()
    logger.info(f"Podsumowanie: {summary}", extra={"correlation_id": correlation_id})
    
    # Test 3: Walidacja bez danych
    validation = manager.validate_data_integrity()
    logger.info(f"Walidacja: {validation}", extra={"correlation_id": correlation_id})
    
    # Sprawdź, czy manager jest zainicjalizowany i walidacja przebiegła pomyślnie
    test_failed = not manager.initialized or not validation.get("valid", False)
    
    if test_failed:
        logger.error("Some Data Manager tests FAILED!",
                      extra={"correlation_id": correlation_id})
        sys.exit(1)
    
    logger.info("All basic tests passed!", extra={"correlation_id": correlation_id})
