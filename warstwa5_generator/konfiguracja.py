"""
Konfiguracja Warstwy 5 - Generator Rozszerzonego Swiata Obserwacji

Definiuje ścieżki, parametry i ustawienia dla modułów Warstwy 5.

UWAGA: Ten moduł NIE powinien wykonywać operacji I/O podczas importu.
Ścieżki są obliczane leniwie (lazy) przy pierwszym użyciu.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """
    Zwraca główny katalog projektu w sposób przenośny.
    
    Kolejność priorytetów:
    1. Zmienna środowiskowa PROJECT_ROOT
    2. Zmienna środowiskowa SSI_ROOT  
    3. Ścieżka względna od tego pliku (warstwa5_generator/konfiguracja.py -> ../../)
    
    Returns:
        Path: Absolutna ścieżka do katalogu głównego projektu
    """
    # 1. Spróbuj PROJECT_ROOT
    project_root = os.environ.get('PROJECT_ROOT')
    if project_root:
        return Path(project_root).resolve()
    
    # 2. Spróbuj SSI_ROOT
    ssi_root = os.environ.get('SSI_ROOT')
    if ssi_root:
        return Path(ssi_root).resolve()
    
    # 3. Domyślna - od tego pliku (warstwa5_generator/konfiguracja.py)
    # zum ../../, um vom warstwa5_generator zum Projektroot zu gelangen
    return Path(__file__).parent.parent.resolve()


@dataclass
class SciezkiConfig:
    """Konfiguracja ścieżek do plików i katalogów.
    
    UWAGA: Wszystkie ścieżki są typem Path, nie str.
    Kastalogi i pliki są obliczane wzgledem ROOT_DIR wartosci leniwie.
    """
    
    # Nie przechowujemy ROOT_DIR jako string, ale wyliczamy go dynamicznie
    # Uzywamy lazy property, aby nie wykonywać operacji I/O podczas importu
    
    # Flaga czy struktura katalogów została utworzona
    _directories_created: bool = False
    
    @property
    def ROOT_DIR(self) -> Path:
        """Główny katalog projektu - wyliczany dynamicznie."""
        return get_project_root()
    
    @property
    def V2_MODELE_TREND(self) -> Path:
        """Katalog modeli trend V2."""
        return self.ROOT_DIR / "modele_dataBase_futbol_trend"
    
    @property
    def V2_MODELE_KURSY(self) -> Path:
        """Katalog modeli kursów V2."""
        return self.ROOT_DIR / "modele_kursy_przygotowane"
    
    @property
    def V2_PAMIEC(self) -> Path:
        """Katalog pamięci V2."""
        return self.ROOT_DIR / "pamiec_modeli_v2"
    
    @property
    def WARSTWA5_DIR(self) -> Path:
        """Katalog Warstwy 5."""
        return self.ROOT_DIR / "warstwa5_generator"
    
    @property
    def WARSTWA5_DANE(self) -> Path:
        """Katalog danych Warstwy 5."""
        return self.WARSTWA5_DIR / "dane"
    
    @property
    def WARSTWA5_EXPORTS(self) -> Path:
        """Katalog eksportów Warstwy 5."""
        return self.WARSTWA5_DANE / "exports"
    
    @property
    def WARSTWA5_LOGS(self) -> Path:
        """Katalog logów Warstwy 5."""
        return self.WARSTWA5_DANE / "logs"
    
    @property
    def ROZSZERZONY_SWIAT_FILE(self) -> Path:
        """Plik rozszerzonego świata obserwacji."""
        return self.WARSTWA5_EXPORTS / "rozszerzony_swiat_obserwacji.json"
    
    @property
    def METADANE_CECH_FILE(self) -> Path:
        """Plik metadanych cech."""
        return self.WARSTWA5_EXPORTS / "metadane_cech.json"
    
    @property
    def EWOLUCJA_PAMIECI_FILE(self) -> Path:
        """Plik ewolucji pamięci."""
        return self.WARSTWA5_EXPORTS / "ewolucja_pamieci.json"
    
    @property
    def PODSUMOWANIE_FILE(self) -> Path:
        """Plik podsumowania analizy."""
        return self.WARSTWA5_EXPORTS / "podsumowanie_analizy.json"
    
    @property
    def LOG_KOLEKTOR(self) -> Path:
        """Plik logu kolektora."""
        return self.WARSTWA5_LOGS / "kolektor.log"
    
    @property
    def LOG_GENERATOR(self) -> Path:
        """Plik logu generatora."""
        return self.WARSTWA5_LOGS / "generator.log"
    
    @property
    def LOG_ANALIZATOR(self) -> Path:
        """Plik logu analizatora."""
        return self.WARSTWA5_LOGS / "analizator.log"
    
    def ensure_directories_exist(self) -> bool:
        """
        Zapewnia, że wymagane katalogi istnieją.
        
        UWAGA: Ta metoda powinna być wywoływana JAWNIE, a nie podczas importu.
        
        Returns:
            True jeśli wszystkie katalogi zostały utworzone
        """
        if self._directories_created:
            return True
        
        try:
            directories = [self.WARSTWA5_EXPORTS, self.WARSTWA5_LOGS]
            for path in directories:
                path.mkdir(parents=True, exist_ok=True)
            
            self._directories_created = True
            logger.info("Required directories created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create directories: {e}")
            return False
    
    def __post_init__(self):
        """
        NIE tworzy katalogów podczas importu!
        Zamiast tego, wywołaj ensure_directories_exist() jawnie.
        """
        # Nie robimy nic podczas __post_init__ - lazily initialization
        pass


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
    
    def ensure_directories(self) -> bool:
        """
        Zapewnia, że wszystkie wymagane katalogi istnieją.
        
        UWAGA: Wywołaj tę metodę JAWNIE, a nie podczas importu.
        
        Returns:
            True jeśli katalogi zostały utworzone
        """
        return self.sciezki.ensure_directories_exist()
    
    def __post_init__(self):
        """Inicjalizacja konfiguracji - NIE wykonuje operacji I/O!"""
        # Nie wywołujemy __post_init__ SciezkiConfig, ponieważ to robiłoby I/O
        # Zamiast tego, użytkownik powinien wywołać ensure_directories() jawnie
        pass


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
