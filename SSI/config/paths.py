"""
SSI Paths - Sciezki systemu SSI

Wersja: 2.0
Data: 2026-07-31
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
import os
import logging

logger = logging.getLogger(__name__)


@dataclass
class SSIPaths:
    """Glowna klasa sciezek systemu SSI"""
    root_path: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent.resolve())
    
    # Moduly - sciezki wzgledne od root_path
    v2_path: str = "v2"
    v3_path: str = "v3"
    v4_path: str = "v4"
    strategy_path: str = "strategy"
    laboratories_path: str = "laboratories"
    feedback_path: str = "feedback"
    decision_path: str = "decision"
    evolution_path: str = "evolution"
    
    # Dane - sciezki wzgledne od root_path
    data_root: str = "data"
    raw_data_path: str = "data/raw"
    processed_data_path: str = "data/processed"
    worlds_data_path: str = "data/worlds"
    results_data_path: str = "data/results"
    
    # Konfiguracja - sciezki wzgledne od root_path
    config_path: str = "config"
    utils_path: str = "utils"
    tests_path: str = "tests"
    
    # Pliki wejsciowe
    input_courses_file: str = "kursy_przygotowane.csv"
    
    def get_absolute_path(self, relative_path: str) -> Path:
        """
        Zwraca bezwzgledna sciezke na podstawie sciezki wzglednej.
        
        Args:
            relative_path: Sciezka wzgledna wzgledem root_path
            
        Returns:
            Bezwzgledna sciezka jako Path
        """
        return (self.root_path / relative_path).resolve()
    
    def create_directory_structure(self) -> bool:
        """
        Tworzy strukture katalogow SSI.
        Uwaga: Ta metoda NIE powinna byc wywolywana podczas importu.
        """
        directories = [
            self.data_root, self.raw_data_path, self.processed_data_path,
            self.worlds_data_path, self.results_data_path, self.v2_path, self.v3_path,
            self.v4_path, self.strategy_path, self.laboratories_path, self.feedback_path,
            self.decision_path, self.evolution_path, self.config_path, self.utils_path, self.tests_path
        ]
        try:
            for directory in directories:
                full_path = self.get_absolute_path(directory)
                os.makedirs(full_path, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Blad tworzenia katalogow: {e}")
            return False


paths_instance: Optional[SSIPaths] = None


def get_paths() -> SSIPaths:
    global paths_instance
    if paths_instance is None:
        paths_instance = SSIPaths()
    return paths_instance


def reset_paths() -> None:
    global paths_instance
    paths_instance = None
