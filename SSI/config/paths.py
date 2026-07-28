"""
SSI Paths - Ścieżki systemu SSI

Wersja: 1.0
Data: 2026-07-28
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import os
import logging

logger = logging.getLogger(__name__)


@dataclass
class SSIPaths:
    """Główna klasa ścieżek systemu SSI"""
    root_path: str = "."
    ssi_root: str = "SSI"
    
    # Moduły
    v2_path: str = "SSI/v2"
    v3_path: str = "SSI/v3"
    v4_path: str = "SSI/v4"
    strategy_path: str = "SSI/strategy"
    laboratories_path: str = "SSI/laboratories"
    feedback_path: str = "SSI/feedback"
    decision_path: str = "SSI/decision"
    evolution_path: str = "SSI/evolution"
    
    # Dane
    data_root: str = "SSI/data"
    raw_data_path: str = "SSI/data/raw"
    processed_data_path: str = "SSI/data/processed"
    worlds_data_path: str = "SSI/data/worlds"
    results_data_path: str = "SSI/data/results"
    
    # Konfiguracja
    config_path: str = "SSI/config"
    utils_path: str = "SSI/utils"
    tests_path: str = "SSI/tests"
    
    # Pliki wejściowe
    input_courses_file: str = "kursy_przygotowane.csv"
    
    def get_absolute_path(self, relative_path: str) -> str:
        return os.path.join(self.root_path, self.ssi_root, relative_path.lstrip('/\\'))
    
    def create_directory_structure(self) -> bool:
        directories = [
            self.ssi_root, self.data_root, self.raw_data_path, self.processed_data_path,
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
            logger.error(f"Błąd tworzenia katalogów: {e}")
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
