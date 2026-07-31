"""
SSI V5 - External Input Layer - Source Types
Typy zrodel danych dla External Knowledge Collector

Odpowiedzialnosc:
- Definicja typow zrodel danych zewnetrznych
- Statusy zbierania danych
- Typy laboratoriow

Wersja: 1.0
Data: 2026-07-31
"""

from enum import Enum, auto
from typing import List, Dict, Any


class SourceType(Enum):
    """
    Typy zrodel danych zewnetrznych dla SSI V5.
    
    DEVELOPER - Dane od programisty (polecenia, wymagania, decyzje)
    LABORATORIES - Dane z laboratoriow (eksperymenty, odkrycia, wyniki)
    AGENTS - Dane od agentow (komunikaty, zdarzenia, wspolpraca)
    SYSTEM - Dane systemowe (logi, statusy, zdarzenia)
    """
    DEVELOPER = auto()
    LABORATORIES = auto()
    AGENTS = auto()
    SYSTEM = auto()
    
    def __str__(self) -> str:
        return self.name
    
    @classmethod
    def get_all_types(cls) -> List['SourceType']:
        """Zwraca liste wszystkich typow zrodel."""
        return list(cls)
    
    @classmethod
    def from_string(cls, source_name: str) -> 'SourceType':
        """
        Konwertuje nazwe string na SourceType.
        
        Args:
            source_name: Nazwa zrodla jako string
            
        Returns:
            SourceType odpowiadajacy nazwie
            
        Raises:
            ValueError: Jesli nazwa nie odpowiada zadnemu typowi
        """
        try:
            return cls[source_name.upper()]
        except KeyError:
            raise ValueError(f"Unknown source type: {source_name}")


class LaboratoryType(Enum):
    """
    Typy laboratoriow w systemie SSI V5.
    
    WORLD_LAB - Laboratorium Swiata (badania swiatow)
    TYPE_LAB - Laboratorium Typow (typy, kategorie, klasyfikacje)
    GROUP_LAB - Laboratorium Grup (grupy, kupony, strategie grupowe)
    COUPON_LAB - Laboratorium Kuponow (kupony, kombinacje, analiza ryzyka)
    """
    WORLD_LAB = "world_lab"
    TYPE_LAB = "type_lab"
    GROUP_LAB = "group_lab"
    COUPON_LAB = "coupon_lab"
    
    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def get_all_types(cls) -> List['LaboratoryType']:
        """Zwraca liste wszystkich typow laboratoriow."""
        return list(cls)
    
    @classmethod
    def from_string(cls, lab_name: str) -> 'LaboratoryType':
        """
        Konwertuje nazwe string na LaboratoryType.
        
        Args:
            lab_name: Nazwa laboratorium jako string
            
        Returns:
            LaboratoryType odpowiadajacy nazwie
            
        Raises:
            ValueError: Jesli nazwa nie odpowiada zadnemu typowi
        """
        for lab_type in cls:
            if lab_type.value == lab_name.lower():
                return lab_type
        raise ValueError(f"Unknown laboratory type: {lab_name}")


class ExternalStatus(Enum):
    """
    Statusy zbierania danych zewnetrznych.
    
    PENDING - Oczekuje na zebranie
    READY - Gotowy do zbierania (po inicjalizacji)
    COLLECTING - Trwa zbieranie danych
    COMPLETED - Zebranie zakonczone sukcesem
    FAILED - Zebranie zakonczone bledem
    VALIDATING - Trwa walidacja danych
    VALIDATED - Walidacja zakonczona sukcesem
    INVALID - Dane nieprawidlowe
    """
    PENDING = auto()
    READY = auto()
    COLLECTING = auto()
    COMPLETED = auto()
    FAILED = auto()
    VALIDATING = auto()
    VALIDATED = auto()
    INVALID = auto()
    
    def __str__(self) -> str:
        return self.name
    
    @classmethod
    def get_all_statuses(cls) -> List['ExternalStatus']:
        """Zwraca liste wszystkich statusow."""
        return list(cls)
    
    def is_successful(self) -> bool:
        """Czy status oznacza sukces?"""
        return self in [ExternalStatus.COMPLETED, ExternalStatus.VALIDATED]
    
    def is_failed(self) -> bool:
        """Czy status oznacza porazke?"""
        return self in [ExternalStatus.FAILED, ExternalStatus.INVALID]
    
    def is_in_progress(self) -> bool:
        """Czy status oznacza trwajacy proces?"""
        return self in [ExternalStatus.COLLECTING, ExternalStatus.VALIDATING]


# Mapy typow dla wygody
SOURCE_TYPE_MAP: Dict[str, SourceType] = {
    "developer": SourceType.DEVELOPER,
    "laboratories": SourceType.LABORATORIES,
    "agents": SourceType.AGENTS,
    "system": SourceType.SYSTEM
}

LABORATORY_TYPE_MAP: Dict[str, LaboratoryType] = {
    "world_lab": LaboratoryType.WORLD_LAB,
    "type_lab": LaboratoryType.TYPE_LAB,
    "group_lab": LaboratoryType.GROUP_LAB,
    "coupon_lab": LaboratoryType.COUPON_LAB
}

STATUS_MAP: Dict[str, ExternalStatus] = {
    "pending": ExternalStatus.PENDING,
    "collecting": ExternalStatus.COLLECTING,
    "completed": ExternalStatus.COMPLETED,
    "failed": ExternalStatus.FAILED,
    "validating": ExternalStatus.VALIDATING,
    "validated": ExternalStatus.VALIDATED,
    "invalid": ExternalStatus.INVALID
}


def get_source_type_from_string(source_str: str) -> SourceType:
    """
    Pomocnicza funkcja do konwersji stringa na SourceType.
    
    Args:
        source_str: String reprezentujacy typ zrodla
        
    Returns:
        SourceType
        
    Raises:
        ValueError: Jesli string nie odpowiada zadnemu typowi
    """
    return SOURCE_TYPE_MAP.get(source_str.lower(), None) or SourceType.from_string(source_str)


def get_laboratory_type_from_string(lab_str: str) -> LaboratoryType:
    """
    Pomocnicza funkcja do konwersji stringa na LaboratoryType.
    
    Args:
        lab_str: String reprezentujacy typ laboratorium
        
    Returns:
        LaboratoryType
        
    Raises:
        ValueError: Jesli string nie odpowiada zadnemu typowi
    """
    return LABORATORY_TYPE_MAP.get(lab_str.lower(), None) or LaboratoryType.from_string(lab_str)
