"""
SSI V5 - Input Layer - Knowledge Metadata
Metadane pakietu wiedzy

Odpowiedzialnosc:
- Definicja struktury metadanych pakietu wiedzy
- Zarzadzanie identyfikatorami, timestampami, wersjami
- Informacje o zrodlach i walidacji

Wersja: 1.0
Data: 2026-07-31
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import hashlib

from .data_models import DataSource

logger = logging.getLogger(__name__)


class PackageStatus(Enum):
    """Status pakietu wiedzy"""
    PENDING = "pending"       # Oczekuje na zebranie danych
    PARTIAL = "partial"       # Czesciowo zebrane dane
    COMPLETE = "complete"     # Wszystkie dane zebrane
    VALIDATED = "validated"   # Dane zwalidowane
    INVALID = "invalid"       # Dane nieprawidlowe
    PROCESSED = "processed"   # Dane przeworzony
    
    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def get_all_statuses(cls) -> List['PackageStatus']:
        """Zwraca liste wszystkich statusow"""
        return list(cls)


@dataclass
class KnowledgeMetadata:
    """
    Metadane pakietu wiedzy.
    
    Odpowiada za:
    - Identyfikacje pakietu
    - Informacje o zrodlach danych
    - Timestampy i wersje
    - Informacje o walidacji
    
    Uzycie:
        metadata = KnowledgeMetadata(package_id="pkg_001")
        metadata.add_source(DataSource.V2_MODELS, collected=True)
        metadata.mark_source_collected(DataSource.V3_KNOWLEDGE)
        metadata.set_validation_result(True, [])
    """
    package_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    version: str = "1.0"
    system: str = "SSI_V5"
    
    # Informacje o zrodlach
    source_types: List[DataSource] = field(default_factory=list)
    collected_sources: Dict[str, bool] = field(default_factory=dict)
    
    # Walidacja
    is_valid: bool = True
    validation_errors: List[str] = field(default_factory=list)
    validation_timestamp: Optional[datetime] = None
    
    # Statystyki
    total_items: int = 0
    data_volume: int = 0  # rozmiar w bajtach
    checksum: str = ""
    
    # Dodatkowe metadane ( rozgrywka dla przyszlych rozszerzen)
    additional_info: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Inicjalizacja po utworzeniu"""
        if not self.package_id:
            self.package_id = self.generate_package_id()
        if not self.checksum:
            self.checksum = self.generate_checksum()
    
    def generate_package_id(self) -> str:
        """Generuje unikalny identyfikator pakietu"""
        return f"knowledge_package_{self.timestamp.strftime('%Y%m%d%H%M%S%f')}"
    
    def generate_checksum(self) -> str:
        """Generuje checksum dla identyfikacji pakietu"""
        data_str = f"{self.package_id}{self.timestamp.isoformat()}{self.version}"
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def add_source(self, source_type: DataSource, collected: bool = False) -> None:
        """
        Dodaje informacje o zrodle.
        
        Args:
            source_type: Typ zrodla
            collected: Czy zrodlo zostalo zebrane
        """
        if source_type not in self.source_types:
            self.source_types.append(source_type)
        self.collected_sources[source_type.name] = collected
        logger.debug(f"Dodano zrodlo {source_type.name} do metadanych")
    
    def mark_source_collected(self, source_type: DataSource) -> None:
        """
        Oznacza zrodlo jako zebrane.
        
        Args:
            source_type: Typ zrodla
        """
        self.add_source(source_type, collected=True)
        logger.debug(f"Oznaczono zrodlo {source_type.name} jako zebrane")
    
    def mark_source_not_collected(self, source_type: DataSource) -> None:
        """
        Oznacza zrodlo jako nie zebrane.
        
        Args:
            source_type: Typ zrodla
        """
        self.add_source(source_type, collected=False)
    
    def set_validation_result(self, is_valid: bool, errors: List[str] = None) -> None:
        """
        Ustawia rezultat walidacji.
        
        Args:
            is_valid: Czy dane sa poprawne
            errors: Lista bledow (jeśli nieprawidlowe)
        """
        self.is_valid = is_valid
        self.validation_timestamp = datetime.now()
        if errors:
            self.validation_errors.extend(errors)
        
        if is_valid:
            logger.info("Walidacja metadanych zakonczona sukcesem")
        else:
            for error in errors or []:
                logger.error(f"Blad walidacji: {error}")
    
    def add_validation_error(self, error: str) -> None:
        """
        Dodaje pojedynczy blad walidacji.
        
        Args:
            error: Opis bledu
        """
        self.validation_errors.append(error)
        self.is_valid = False
        logger.warning(f"Dodano blad walidacji: {error}")
    
    def clear_validation_errors(self) -> None:
        """Czyści liste bledow walidacji"""
        self.validation_errors.clear()
        self.is_valid = True
    
    def get_collected_sources(self) -> List[DataSource]:
        """Zwraca liste zebranych zrodel"""
        return [
            st for st in self.source_types 
            if self.collected_sources.get(st.name, False)
        ]
    
    def get_missing_sources(self) -> List[DataSource]:
        """Zwraca liste nie zebranych zrodel"""
        return [
            st for st in self.source_types 
            if not self.collected_sources.get(st.name, False)
        ]
    
    def has_source(self, source_type: DataSource) -> bool:
        """Czy w metadanych jest informacja o zrodle?"""
        return source_type in self.source_types
    
    def is_source_collected(self, source_type: DataSource) -> bool:
        """Czy zrodlo zostalo zebrane?"""
        return self.collected_sources.get(source_type.name, False)
    
    def get_collected_count(self) -> int:
        """Zwraca liczbe zebranych zrodel"""
        return sum(1 for collected in self.collected_sources.values() if collected)
    
    def get_total_source_count(self) -> int:
        """Zwraca liczbe wszystkich zrodel (zebranych i nie)"""
        return len(self.source_types)
    
    # =========================================================================
    # METODY KONWERSJI
    # =========================================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Konwersja do slovika.
        
        Returns:
            Slownik z metadanymi
        """
        result = asdict(self)
        result["timestamp"] = self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else str(self.timestamp)
        if isinstance(self.validation_timestamp, datetime):
            result["validation_timestamp"] = self.validation_timestamp.isoformat()
        
        # Konwersja enumow do stringow
        result["source_types"] = [st.name for st in self.source_types]
        
        # χειρισμός additional_info jeśli to nie serializowalne
        if isinstance(result.get("additional_info"), dict):
            result["additional_info"] = {
                str(k): str(v) for k, v in result["additional_info"].items()
            }
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeMetadata":
        """
        Konwersja ze slovika.
        
        Args:
            data: Slownik z metadanymi
            
        Returns:
            Nowy KnowledgeMetadata
        """
        data_copy = data.copy()
        
        # Konwersja timestampow
        if isinstance(data_copy.get("timestamp"), str):
            try:
                data_copy["timestamp"] = datetime.fromisoformat(data_copy["timestamp"])
            except ValueError:
                data_copy["timestamp"] = datetime.now()
        
        if data_copy.get("validation_timestamp") and isinstance(data_copy["validation_timestamp"], str):
            try:
                data_copy["validation_timestamp"] = datetime.fromisoformat(
                    data_copy["validation_timestamp"]
                )
            except ValueError:
                data_copy["validation_timestamp"] = None
        
        # Konwersja source_types ze stringow na DataSource
        if "source_types" in data_copy and isinstance(data_copy["source_types"], list):
            data_copy["source_types"] = [
                DataSource[st] if isinstance(st, str) and hasattr(DataSource, st) else st
                for st in data_copy["source_types"]
            ]
        
        # Usuwamy timestamp i validation_timestamp z data_copy, bo byly juz przetworzone
        if "timestamp" in data_copy:
            del data_copy["timestamp"]
        if "validation_timestamp" in data_copy:
            del data_copy["validation_timestamp"]
        
        return cls(**data_copy)
    
    def to_json(self, indent: int = 2) -> str:
        """
        Konwersja do JSON.
        
        Args:
            indent: Wciecie JSON
            
        Returns:
            String JSON
        """
        import json
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False, default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> "KnowledgeMetadata":
        """
        Tworzenie z JSON.
        
        Args:
            json_str: String JSON
            
        Returns:
            Nowy KnowledgeMetadata
        """
        import json
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        """Reprezentacja tekstowa"""
        return f'KnowledgeMetadata("{self.package_id}", sources: {len(self.source_types)}, collected: {self.get_collected_count()}, valid: {self.is_valid})'
    
    def display(self) -> None:
        """Wyswietla metadane w czytelnej formie"""
        print("=" * 60)
        print("KNOWLEDGE METADATA")
        print("=" * 60)
        print(f"Package ID: {self.package_id}")
        print(f"Timestamp: {self.timestamp}")
        print(f"Version: {self.version}")
        print(f"System: {self.system}")
        print(f"Total Items: {self.total_items}")
        print(f"Data Volume: {self.data_volume} bytes")
        print(f"Checksum: {self.checksum}")
        print()
        print("SOURCES:")
        for source in self.source_types:
            collected = self.collected_sources.get(source.name, False)
            status = "COLLECTED" if collected else "PENDING"
            print(f"  {source.name}: {status}")
        print()
        print("VALIDATION:")
        print(f"  Valid: {self.is_valid}")
        if self.validation_errors:
            print(f"  Errors: {self.validation_errors}")
        if self.validation_timestamp:
            print(f"  Timestamp: {self.validation_timestamp}")
        print("=" * 60)


# =============================================================================
# FUNKCJE UZYTECZNE
# =============================================================================


def create_metadata(
    package_id: str = None,
    version: str = "1.0",
    system: str = "SSI_V5"
) -> KnowledgeMetadata:
    """
    Funkcja fabryczna do tworzenia metadanych.
    
    Args:
        package_id: Identyfikator pakietu (opcjonalny, generowany automatycznie)
        version: Wersja pakietu
        system: Nazwa systemu
        
    Returns:
        Nowy KnowledgeMetadata
    """
    if package_id:
        return KnowledgeMetadata(
            package_id=package_id,
            version=version,
            system=system
        )
    else:
        return KnowledgeMetadata(version=version, system=system)
