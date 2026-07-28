"""
SSI CSV Loader - Ładowanie plików CSV

Zgodnie z dokumentacją 02_DATA_STRUCTURE.md:
- kursy_przygotowane.csv: główne źródło danych
- Format: mecz;kurs_1_start;kurs_X_start;kurs_2_start;kurs_1_koniec;kurs_X_koniec;kurs_2_koniec;zmiana_kurs_1;zmiana_kurs_X;zmiana_kurs_2;procent_kurs_1;procent_kurs_X;procent_kurs_2

Wersja: 1.0
Data: 2026-07-28
"""

from typing import Dict, List, Optional, Any
import csv
import logging
from pathlib import Path
from dataclasses import dataclass, field

from .data_structures import CourseData, DataMetadata, DataQualityReport

logger = logging.getLogger(__name__)


class CSVLoader:
    """Bazowa klasa do ładowania plików CSV"""
    
    def __init__(self, file_path: str, delimiter: str = ";"):
        self.file_path = file_path
        self.delimiter = delimiter
        self.headers: List[str] = []
        self.data: List[Dict[str, Any]] = []
        self.metadata: Optional[DataMetadata] = None
        
    def load(self) -> bool:
        """Ładowanie pliku CSV"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=self.delimiter)
                self.headers = reader.fieldnames or []
                self.data = [row for row in reader]
                
                self.metadata = DataMetadata(
                    source_file=self.file_path,
                    data_type="raw",
                    total_records=len(self.data)
                )
                
                logger.info(f"Załadowano {len(self.data)} rekordów z {self.file_path}")
                return True
        except Exception as e:
            logger.error(f"Błąd ładowania pliku {self.file_path}: {e}")
            return False
    
    def get_headers(self) -> List[str]:
        """Pobieranie nagłówków"""
        return self.headers
    
    def get_data(self) -> List[Dict[str, Any]]:
        """Pobieranie danych"""
        return self.data
    
    def get_metadata(self) -> Optional[DataMetadata]:
        """Pobieranie metadanych"""
        return self.metadata
    
    def validate_required_columns(self, required_columns: List[str]) -> bool:
        """Sprawdzenie czy wymagane kolumny istnieją"""
        for col in required_columns:
            if col not in self.headers:
                logger.error(f"Brak wymaganej kolumny: {col}")
                return False
        return True


class CourseCSVLoader(CSVLoader):
    """
    Specjalizowana klasa do ładowania kursy_przygotowane.csv
    
    Zgodnie z 02_DATA_STRUCTURE.md Sekcja 2.2
    """
    
    REQUIRED_COLUMNS = [
        "mecz", "kurs_1_start", "kurs_X_start", "kurs_2_start",
        "kurs_1_koniec", "kurs_X_koniec", "kurs_2_koniec"
    ]
    
    OPTIONAL_COLUMNS = [
        "zmiana_kurs_1", "zmiana_kurs_X", "zmiana_kurs_2",
        "procent_kurs_1", "procent_kurs_X", "procent_kurs_2"
    ]
    
    def __init__(self, file_path: str = "kursy_przygotowane.csv", delimiter: str = ";"):
        super().__init__(file_path, delimiter)
    
    def load_courses(self) -> List[CourseData]:
        """Ładowanie i konwersja do obiektów CourseData"""
        if not self.data:
            if not self.load():
                return []
        
        courses = []
        for row in self.data:
            try:
                course = CourseData(
                    mecz=row.get("mecz", ""),
                    kurs_1_start=float(row.get("kurs_1_start", 0)),
                    kurs_X_start=float(row.get("kurs_X_start", 0)),
                    kurs_2_start=float(row.get("kurs_2_start", 0)),
                    kurs_1_koniec=float(row.get("kurs_1_koniec", 0)),
                    kurs_X_koniec=float(row.get("kurs_X_koniec", 0)),
                    kurs_2_koniec=float(row.get("kurs_2_koniec", 0)),
                    zmiana_kurs_1=float(row.get("zmiana_kurs_1", 0)),
                    zmiana_kurs_X=float(row.get("zmiana_kurs_X", 0)),
                    zmiana_kurs_2=float(row.get("zmiana_kurs_2", 0)),
                    procent_kurs_1=float(row.get("procent_kurs_1", 0)),
                    procent_kurs_X=float(row.get("procent_kurs_X", 0)),
                    procent_kurs_2=float(row.get("procent_kurs_2", 0))
                )
                courses.append(course)
            except (ValueError, TypeError) as e:
                logger.warning(f"Błąd konwersji rekordu: {row}. Błąd: {e}")
                continue
        
        logger.info(f"Skonwertowano {len(courses)} rekordów na obiekty CourseData")
        return courses
    
    def validate_file(self) -> DataQualityReport:
        """Walidacja pliku i generowanie raportu jakości"""
        report = DataQualityReport(data_checked=self.file_path)
        
        if not self.data and not self.load():
            report.quality_score = 0.0
            report.issues.append("Nie można załadować pliku")
            return report
        
        report.total_records = len(self.data)
        
        for row in self.data:
            missing = []
            for col in self.REQUIRED_COLUMNS:
                if col not in row or not row[col]:
                    missing.append(col)
            
            if missing:
                report.missing_count += 1
                for col in missing:
                    report.issues.append(f"Brak wartości w kolumnie {col}")
            else:
                report.complete_records += 1
        
        if report.total_records > 0:
            report.quality_score = report.complete_records / report.total_records
        
        return report
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Pobieranie statystyk podsumowujących"""
        if not self.data:
            return {}
        
        courses = self.load_courses()
        if not courses:
            return {}
        
        stats = {
            "total_matches": len(courses),
            "avg_start_courses": {
                "1": 0.0, "X": 0.0, "2": 0.0
            },
            "avg_end_courses": {
                "1": 0.0, "X": 0.0, "2": 0.0
            },
            "avg_changes": {
                "1": 0.0, "X": 0.0, "2": 0.0
            }
        }
        
        sum_start = {"1": 0.0, "X": 0.0, "2": 0.0}
        sum_end = {"1": 0.0, "X": 0.0, "2": 0.0}
        sum_changes = {"1": 0.0, "X": 0.0, "2": 0.0}
        
        for course in courses:
            sum_start["1"] += course.kurs_1_start
            sum_start["X"] += course.kurs_X_start
            sum_start["2"] += course.kurs_2_start
            
            sum_end["1"] += course.kurs_1_koniec
            sum_end["X"] += course.kurs_X_koniec
            sum_end["2"] += course.kurs_2_koniec
            
            sum_changes["1"] += course.zmiana_kurs_1
            sum_changes["X"] += course.zmiana_kurs_X
            sum_changes["2"] += course.zmiana_kurs_2
        
        count = len(courses)
        for key in ["1", "X", "2"]:
            stats["avg_start_courses"][key] = sum_start[key] / count if count > 0 else 0.0
            stats["avg_end_courses"][key] = sum_end[key] / count if count > 0 else 0.0
            stats["avg_changes"][key] = sum_changes[key] / count if count > 0 else 0.0
        
        return stats
