"""
SSI Paths - Sciezki systemu SSI

Wersja: 2.1
Data: 2026-07-31
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
import os
import logging

logger = logging.getLogger(__name__)


def get_root_path() -> Path:
    """
    Zwraca główną ścieżkę projektu SSI.
    
    Kolejność priorytetów:
    1. Zmienna środowiskowa SSI_ROOT
    2. Zmienna środowiskowa PROJECT_ROOT
    3. Ścieżka względna od pliku __file__ (SSI/config/paths.py -> ../../..)
    
    Returns:
        Path: ABSOLUTE path to project root
    """
    # 1. Spróbuj SSI_ROOT
    ssi_root = os.environ.get('SSI_ROOT')
    if ssi_root:
        return Path(ssi_root).resolve()
    
    # 2. Spróbuj PROJECT_ROOT
    project_root = os.environ.get('PROJECT_ROOT')
    if project_root:
        return Path(project_root).resolve()
    
    # 3. Domyślna ścieżka względna od tego pliku
    # paths.py jest w SSI/config/paths.py
    # root to ../../ (od SSI/config do D:/sts/aplikacjaTyperBetAi)
    return Path(__file__).parent.parent.parent.resolve()


@dataclass
class SSIPaths:
    """Glowna klasa sciezek systemu SSI.
    
    Wszystkie sciezki sa Path, na wszystkich platformach.
    root_path jest wyliczany lazily dla Kazdej instancji.
    """
    # Uzywamy default_factory, aby root_path byl obliczany dla kazdej instancji
    root_path: Path = field(default_factory=get_root_path)
    
    # Moduly - sciezki wzgledne od root_path (Path, nie str)
    v2_path: Path = field(default=Path("v2"))
    v3_path: Path = field(default=Path("v3"))
    v4_path: Path = field(default=Path("v4"))
    strategy_path: Path = field(default=Path("strategy"))
    laboratories_path: Path = field(default=Path("laboratories"))
    feedback_path: Path = field(default=Path("feedback"))
    decision_path: Path = field(default=Path("decision"))
    evolution_path: Path = field(default=Path("evolution"))
    
    # Dane - sciezki wzgledne od root_path
    data_root: Path = field(default=Path("data"))
    raw_data_path: Path = field(default=Path("data/raw"))
    processed_data_path: Path = field(default=Path("data/processed"))
    worlds_data_path: Path = field(default=Path("data/worlds"))
    results_data_path: Path = field(default=Path("data/results"))
    
    # Konfiguracja - sciezki wzgledne od root_path
    config_path: Path = field(default=Path("config"))
    utils_path: Path = field(default=Path("utils"))
    tests_path: Path = field(default=Path("tests"))
    
    # Pliki wejsciowe
    input_courses_file: Path = field(default=Path("kursy_przygotowane.csv"))
    
    def get_absolute_path(self, relative_path: Optional[Path] = None) -> Path:
        """
        Zwraca bezwzgledna sciezke na podstawie sciezki wzglednej.
        
        Args:
            relative_path: Sciezka wzgledna wzgledem root_path (Path lub str).
                          Jeśli None, zwraca root_path.
            
        Returns:
            Bezwzgledna sciezka jako Path
            
        Raises:
            TypeError: Jeśli relative_path nie jest Path ani str
        """
        if relative_path is None:
            return self.root_path.resolve()
        
        if isinstance(relative_path, str):
            relative_path = Path(relative_path)
        elif not isinstance(relative_path, Path):
            raise TypeError(f"relative_path must be Path or str, got {type(relative_path)}")
        
        return (self.root_path / relative_path).resolve()
    
    def create_directory_structure(self) -> bool:
        """
        Tworzy strukture katalogow SSI.
        
        UWAGA: Ta metoda NIE powinna być wywoływana podczas importu.
        Wywołaj ją jawnie, jeśli chcesz utworzyć struktury katalogów.
        
        Returns:
            True jeśli wszystkie katalogi zostały utworzone lub istniały
            False jeśli wystąpił błąd
        """
        # Lista ścieżek względnych do utworzenia
        directories = [
            self.v2_path, self.v3_path, self.v4_path,
            self.strategy_path, self.laboratories_path, self.feedback_path,
            self.decision_path, self.evolution_path,
            self.data_root, self.raw_data_path, self.processed_data_path,
            self.worlds_data_path, self.results_data_path,
            self.config_path, self.utils_path, self.tests_path
        ]
        
        try:
            for directory in directories:
                # directory jest Path, get_absolute_path akceptuje Path
                full_path = self.get_absolute_path(directory)
                # Upewnij się, że full_path jest Path
                full_path = Path(full_path) if not isinstance(full_path, Path) else full_path
                full_path.mkdir(parents=True, exist_ok=True)
            
            logger.info("Directory structure created successfully")
            return True
        except Exception as e:
            logger.error(f"Blad tworzenia katalogow: {e}")
            return False
    
    def ensure_directory_exists(self, relative_path: Optional[Path] = None) -> Path:
        """
        Zapewnia, że katalog istnieje (tworzy go jeśli nie istnieje).
        
        Args:
            relative_path: Ścieżka względna (Path lub str). Jeśli None, używa root_path.
            
        Returns:
            Utworzona lub istniejaca ścieżka (Path)
        """
        full_path = self.get_absolute_path(relative_path)
        full_path = Path(full_path) if not isinstance(full_path, Path) else full_path
        full_path.mkdir(parents=True, exist_ok=True)
        return full_path


paths_instance: Optional[SSIPaths] = None


def get_paths() -> SSIPaths:
    global paths_instance
    if paths_instance is None:
        paths_instance = SSIPaths()
    return paths_instance


def reset_paths() -> None:
    global paths_instance
    paths_instance = None
