"""
SSI Data Structures - Struktury danych warstwy Data World

Zgodnie z dokumentacją 02_DATA_STRUCTURE.md:
- kursy_przygotowane.csv z polami: mecz, kurs_1_start, kurs_X_start, kurs_2_start, itd.
- Podział na dane pierwotne, cechy modelowe, światy

Wersja: 1.0
Data: 2026-07-28
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class CourseData:
    """
    Struktura danych kursowych z kursy_przygotowane.csv
    
    Zgodnie z 02_DATA_STRUCTURE.md Sekcja 2.2:
    kursy_przygotowane.csv zawiera:
    - mecz
    - kurs_1_start, kurs_X_start, kurs_2_start
    - kurs_1_koniec, kurs_X_koniec, kurs_2_koniec
    - zmiana_kurs_1, zmiana_kurs_X, zmiana_kurs_2
    - procent_kurs_1, procent_kurs_X, procent_kurs_2
    """
    mecz: str
    kurs_1_start: float
    kurs_X_start: float
    kurs_2_start: float
    kurs_1_koniec: float
    kurs_X_koniec: float
    kurs_2_koniec: float
    zmiana_kurs_1: float = 0.0
    zmiana_kurs_X: float = 0.0
    zmiana_kurs_2: float = 0.0
    procent_kurs_1: float = 0.0
    procent_kurs_X: float = 0.0
    procent_kurs_2: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "mecz": self.mecz,
            "kurs_1_start": self.kurs_1_start,
            "kurs_X_start": self.kurs_X_start,
            "kurs_2_start": self.kurs_2_start,
            "kurs_1_koniec": self.kurs_1_koniec,
            "kurs_X_koniec": self.kurs_X_koniec,
            "kurs_2_koniec": self.kurs_2_koniec,
            "zmiana_kurs_1": self.zmiana_kurs_1,
            "zmiana_kurs_X": self.zmiana_kurs_X,
            "zmiana_kurs_2": self.zmiana_kurs_2,
            "procent_kurs_1": self.procent_kurs_1,
            "procent_kurs_X": self.procent_kurs_X,
            "procent_kurs_2": self.procent_kurs_2
        }
    
    def get_changes(self) -> Dict[str, float]:
        """Pobieranie zmian kursów"""
        return {
            "zmiana_1": self.zmiana_kurs_1,
            "zmiana_X": self.zmiana_kurs_X,
            "zmiana_2": self.zmiana_kurs_2
        }
    
    def get_percent_changes(self) -> Dict[str, float]:
        """Pobieranie procentowych zmian kursów"""
        return {
            "procent_1": self.procent_kurs_1,
            "procent_X": self.procent_kurs_X,
            "procent_2": self.procent_kurs_2
        }
    
    def get_start_courses(self) -> Dict[str, float]:
        """Pobieranie kursów początkowych"""
        return {
            "kurs_1_start": self.kurs_1_start,
            "kurs_X_start": self.kurs_X_start,
            "kurs_2_start": self.kurs_2_start
        }
    
    def get_end_courses(self) -> Dict[str, float]:
        """Pobieranie kursów końcowych"""
        return {
            "kurs_1_koniec": self.kurs_1_koniec,
            "kurs_X_koniec": self.kurs_X_koniec,
            "kurs_2_koniec": self.kurs_2_koniec
        }


@dataclass
class MatchData:
    """Dane meczu z wynikiem"""
    mecz: str
    wynik: Optional[str] = None  # np. "1:0", "2:1", "X"
    data_meczu: Optional[str] = None
    source: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "mecz": self.mecz,
            "wynik": self.wynik,
            "data_meczu": self.data_meczu,
            "source": self.source
        }


@dataclass
class TrendData:
    """
    Dane trendów wyliczone z kursów
    Zgodnie z 02_DATA_STRUCTURE.md Sekcja 3.2
    """
    # Zmiany kursów (Świat 1)
    zmiana_1: float = 0.0
    zmiana_X: float = 0.0
    zmiana_2: float = 0.0
    
    # Amplituda (Świat 2)
    amplituda_1: float = 0.0
    amplituda_X: float = 0.0
    amplituda_2: float = 0.0
    
    # Tempo (Świat 2)
    tempo_1: float = 0.0
    tempo_X: float = 0.0
    tempo_2: float = 0.0
    
    # Synchronizacja (Świat 2)
    synchronizacja: float = 0.0
    
    # Maksymalne wahania (Świat 2)
    max_wahanie_1: float = 0.0
    max_wahanie_X: float = 0.0
    max_wahanie_2: float = 0.0
    
    # Statystyki
    mean_1: float = 0.0
    mean_X: float = 0.0
    mean_2: float = 0.0
    median_1: float = 0.0
    median_X: float = 0.0
    median_2: float = 0.0
    stdev_1: float = 0.0
    stdev_X: float = 0.0
    stdev_2: float = 0.0
    
    # Czas
    czas_h: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "zmiana_1": self.zmiana_1, "zmiana_X": self.zmiana_X, "zmiana_2": self.zmiana_2,
            "amplituda_1": self.amplituda_1, "amplituda_X": self.amplituda_X, "amplituda_2": self.amplituda_2,
            "tempo_1": self.tempo_1, "tempo_X": self.tempo_X, "tempo_2": self.tempo_2,
            "synchronizacja": self.synchronizacja,
            "max_wahanie_1": self.max_wahanie_1, "max_wahanie_X": self.max_wahanie_X, "max_wahanie_2": self.max_wahanie_2,
            "mean_1": self.mean_1, "mean_X": self.mean_X, "mean_2": self.mean_2,
            "median_1": self.median_1, "median_X": self.median_X, "median_2": self.median_2,
            "stdev_1": self.stdev_1, "stdev_X": self.stdev_X, "stdev_2": self.stdev_2,
            "czas_h": self.czas_h
        }
    
    def get_world_1_features(self) -> Dict[str, float]:
        """Pobieranie cech Świata 1 (Zmiany Kursów)"""
        return {"zmiana_1": self.zmiana_1, "zmiana_X": self.zmiana_X, "zmiana_2": self.zmiana_2}
    
    def get_world_2_features(self) -> Dict[str, float]:
        """Pobieranie cech Świata 2 (Dynamika)"""
        return {
            "amplituda_1": self.amplituda_1, "amplituda_X": self.amplituda_X, "amplituda_2": self.amplituda_2,
            "tempo_1": self.tempo_1, "tempo_X": self.tempo_X, "tempo_2": self.tempo_2,
            "synchronizacja": self.synchronizacja,
            "max_wahanie_1": self.max_wahanie_1, "max_wahanie_X": self.max_wahanie_X, "max_wahanie_2": self.max_wahanie_2
        }


@dataclass
class DataMetadata:
    """Metadane danych"""
    source_file: str
    data_type: str  # "raw", "processed", "features", "observation"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    total_records: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    missing_values: Dict[str, int] = field(default_factory=dict)
    data_quality_score: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_file": self.source_file,
            "data_type": self.data_type,
            "timestamp": self.timestamp,
            "total_records": self.total_records,
            "valid_records": self.valid_records,
            "invalid_records": self.invalid_records,
            "missing_values": self.missing_values,
            "data_quality_score": self.data_quality_score
        }


@dataclass
class DataSplitConfig:
    """
    Konfiguracja podziału danych zgodnie z zasadą 60/40
    
    Zgodnie z 01_SYSTEM_ARCHITECTURE.md i 02_DATA_STRUCTURE.md:
    - 60% dane: trening + walidacja
    - 40% dane: niezależna obserwacja
    """
    training_split: float = 0.6    # 60% na trening
    validation_split: float = 0.4  # 40% na walidację (w ramach 60%)
    observation_split: float = 0.4 # 40% na obserwację
    test_split: float = 0.0        # Opcjonalne
    shuffle: bool = True
    random_state: int = 42
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "training_split": self.training_split,
            "validation_split": self.validation_split,
            "observation_split": self.observation_split,
            "test_split": self.test_split,
            "shuffle": self.shuffle,
            "random_state": self.random_state
        }


@dataclass
class DataQualityReport:
    """Raport jakości danych"""
    data_checked: str
    total_records: int = 0
    complete_records: int = 0
    missing_count: int = 0
    invalid_count: int = 0
    duplicates_count: int = 0
    quality_score: float = 1.0
    issues: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "data_checked": self.data_checked,
            "total_records": self.total_records,
            "complete_records": self.complete_records,
            "missing_count": self.missing_count,
            "invalid_count": self.invalid_count,
            "duplicates_count": self.duplicates_count,
            "quality_score": self.quality_score,
            "issues": self.issues
        }
