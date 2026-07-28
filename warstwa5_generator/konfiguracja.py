"""
Konfiguracja Warstwy 5 - Generator Rozszerzonego Swiata Obserwacji

Definiuje ścieżki, parametry i ustawienia dla modułów Warstwy 5.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class SciezkiConfig:
    """Konfiguracja ścieżek do plików i katalogów."""
    
    # Katalog główny projektu
    ROOT_DIR: str = "D:\\sts\\aplikacjaTyperBetAi"
    
    # Katalogi V2 (źródło danych)
    V2_MODELE_TREND: str = os.path.join(ROOT_DIR, "modele_dataBase_futbol_trend")
    V2_MODELE_KURSY: str = os.path.join(ROOT_DIR, "modele_kursy_przygotowane")
    V2_PAMIEC: str = os.path.join(ROOT_DIR, "pamiec_modeli_v2")
    
    # Katalogi Warstwy 5 (docelowe)
    WARSTWA5_DIR: str = os.path.join(ROOT_DIR, "warstwa5_generator")
    WARSTWA5_DANE: str = os.path.join(WARSTWA5_DIR, "dane")
    WARSTWA5_EXPORTS: str = os.path.join(WARSTWA5_DANE, "exports")
    WARSTWA5_LOGS: str = os.path.join(WARSTWA5_DANE, "logs")
    
    # Pliki wyjściowe
    ROZSZERZONY_SWIAT_FILE: str = os.path.join(WARSTWA5_EXPORTS, "rozszerzony_swiat_obserwacji.json")
    METADANE_CECH_FILE: str = os.path.join(WARSTWA5_EXPORTS, "metadane_cech.json")
    EWOLUCJA_PAMIECI_FILE: str = os.path.join(WARSTWA5_EXPORTS, "ewolucja_pamieci.json")
    PODSUMOWANIE_FILE: str = os.path.join(WARSTWA5_EXPORTS, "podsumowanie_analizy.json")
    
    # Pliki logów
    LOG_KOLEKTOR: str = os.path.join(WARSTWA5_LOGS, "kolektor.log")
    LOG_GENERATOR: str = os.path.join(WARSTWA5_LOGS, "generator.log")
    LOG_ANALIZATOR: str = os.path.join(WARSTWA5_LOGS, "analizator.log")
    
    def __post_init__(self):
        """Utwórz brakujące katalogi."""
        for path in [self.WARSTWA5_EXPORTS, self.WARSTWA5_LOGS]:
            os.makedirs(path, exist_ok=True)


@dataclass
class ParametryAnalizy:
    """Parametry analizy ewolucji pamięci."""
    
    # Progi dla klasyfikacji stabilności
    PROG_STABILNOSCI_WYSOKA: float = 0.95
    PROG_STABILNOSCI_SREDNIA: float = 0.80
    PROG_STABILNOSCI_NISKA: float = 0.60
    
    # Progi dla trendów pewności
    PROG_TREND_ROSNACY: float = 0.05  # Minimalny wzrost pewności
    PROG_TREND_MALEJACY: float = -0.05  # Maksymalny spadek pewności
    
    # Minimalna liczba obserwacji do analizy
    MIN_OBSERWACJI_DO_ANALIZY: int = 3
    
    # Okno czasowe dla analizy trendów (w dniach)
    OKNO_CZASOWE_DNI: int = 30
    
    # Liczba najlepszych/worst modeli do raportu
    TOP_N_MODELI: int = 5
    
    # Klassyfikacja skuteczności
    SKUTECZNOSC_WYSOKA: float = 0.30
    SKUTECZNOSC_SREDNIA: float = 0.20
    SKUTECZNOSC_NISKA: float = 0.10


@dataclass
class UstawieniaEksportu:
    """Ustawienia eksportu danych."""
    
    # Format daty
    FORMAT_DATY: str = "%Y-%m-%d %H:%M:%S"
    
    # Precyzja liczb zmiennoprzecinkowych
    PRECYZJA_FLOAT: int = 8
    
    # Czy eksportować pełną historię
    EXPORT_PELNA_HISTORIA: bool = True
    
    # Czy eksportować statystyki podsumowujące
    EXPORT_STATYSTYKI: bool = True
    
    # Czy kompresować pliki wyjściowe
    KOMPRESUJ_WYJSCIE: bool = False


@dataclass
class Config:
    """Główna klasa konfiguracji Warstwy 5."""
    
    sciezki: SciezkiConfig = field(default_factory=SciezkiConfig)
    parametry: ParametryAnalizy = field(default_factory=ParametryAnalizy)
    eksport: UstawieniaEksportu = field(default_factory=UstawieniaEksportu)
    
    # Typy plików do zbierania z V2
    PLIKI_DO_ZBIORU: List[str] = field(default_factory=lambda: [
        "pamiec_obserwacji.json",
        "ocena.json",
        "historia.json",
        "klasy.json",
        "metadata.json"
    ])
    
    # Listy sieci V2
    SIECI_TREND: List[str] = field(default_factory=lambda: [
        "siec_01_zmiana_kursow",
        "siec_02_amplituda",
        "siec_03_tempo",
        "siec_04_max_wahanie",
        "siec_05_start_raw",
        "siec_06_koniec_raw",
        "siec_07_log_start",
        "siec_08_log_koniec",
        "siec_09_ratio_start",
        "siec_10_ratio_koniec",
        "siec_11_statystyka"
    ])
    
    SIECI_KURSY: List[str] = field(default_factory=lambda: [
        "siec_01_start_kursow",
        "siec_02_koniec_kursow",
        "siec_03_zmiana_kursow",
        "siec_04_procent_kursow"
    ])
    
    #Mapowanie grup wyników
    GRUPY_WYNIKOW: Dict[str, str] = field(default_factory=lambda: {
        "1:0": "1", "2:0": "1", "3:0": "1", "4:0": "1", "5:0": "1", "6:0": "1", "7:0": "1",
        "0:1": "2", "0:2": "2", "0:3": "2", "0:4": "2", "0:5": "2", "0:6": "2", "0:7": "2",
        "1:1": "X", "2:2": "X", "3:3": "X", "4:4": "X", "0:0": "X",
        "1:2": "2", "2:1": "1", "3:1": "1", "1:3": "2", "4:1": "1", "1:4": "2",
        "3:2": "1", "2:3": "2", "4:2": "1", "2:4": "2", "5:1": "1", "1:5": "2"
    })
    
    def __post_init__(self):
        """Inicjalizacja konfiguracji."""
        self.sciezki.__post_init__()


# Instancja globalnej konfiguracji
config = Config()


def get_config() -> Config:
    """Zwraca globalną konfigurację."""
    return config


def reload_config() -> Config:
    """Przeładowuje konfigurację."""
    global config
    config = Config()
    return config
