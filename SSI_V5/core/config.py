# SSI V5 Core Configuration
# Centralne źródło konfiguracji dla systemu SSI V5
# 
# Zasada: Tylko tekstowe wartości konfiguracyjne, bez logiki
# Wszystkie jądre wartości z SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py
# 
# Data: 2026-08-03
# Status: Centralna konfiguracja - ETAP 5.2.2

import os
from pathlib import Path

# =============================================================================
# KONFIGURACJA ŚCIEŻEK - PATHS CONFIGURATION
# =============================================================================

class PathConfig:
    """
    Centralna konfiguracja ścieżek plików i katalogów.
    Wszystkie ścieżki są względne do głównego katalogu projektu.
    """
    
    # Główne katalogi
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR = os.path.join(BASE_DIR, "dane")
    MODELS_DIR = os.path.join(BASE_DIR, "modele_kursy_przygotowane")
    MODELE_DATA_BASE_DIR = os.path.join(BASE_DIR, "modele_dataBase_futbol_trend")
    WORLD_DIR = os.path.join(BASE_DIR, "WORLD")
    MEMORY_DIR = os.path.join(BASE_DIR, "memory_backup")
    SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
    
    # Pliki danych
    PLIK_TRENING = os.path.join(DATA_DIR, "mozg_kursy_przygotowane.csv")
    PLIK_PREDYKCJI = os.path.join(DATA_DIR, "kursy_przygotowane.csv")
    PLIK_DATA_BASE_TREND = os.path.join(DATA_DIR, "dataBase_futbol_trend.csv")
    PLIK_KOD_DATA_BASE_TREND = os.path.join(DATA_DIR, "kod_dataBase_futbol_trend.csv")
    
    # Pliki wyjściowe
    OUTPUT = os.path.join(DATA_DIR, "ranking_cech_kursy_przygotowane.csv")
    PLIK_CECHY = os.path.join(DATA_DIR, "cechy.csv")
    PLIK_WYNIK = os.path.join(DATA_DIR, "wyniki.csv")
    PLIK_GRUPY = os.path.join(DATA_DIR, "grupy.csv")
    PLIK_JSON = os.path.join(DATA_DIR, "dane.json")
    
    # Pliki pamięci świata
    WORLD_LEVEL_1_FILE = os.path.join(WORLD_DIR, "poziom1.json")
    WORLD_LEVEL_2_FILE = os.path.join(WORLD_DIR, "poziom2.json")
    WORLD_FULL_FILE = os.path.join(WORLD_DIR, "poziom3.json")
    WORLD_MATCH_DATABASE_FILE = os.path.join(WORLD_DIR, "world_match_database.json")
    PAMIEC_SWIATOW_FILE = os.path.join(BASE_DIR, "pamiec_swiatow.json")
    LABORATORIUM_UCZENIA_FILE = os.path.join(BASE_DIR, "laboratorium_uczenia.json")
    
    # katalogi modeli
    KATALOG_MODELI = MODELS_DIR
    KATALOG_MODELU = MODELE_DATA_BASE_DIR
    
    # katalogi obserwacji (względne do katalogu modeli)
    KATALOG_OBSERWACJI = os.path.join(MODELE_DATA_BASE_DIR, "obserwacja")
    KATALOG_PREDYKCJI = os.path.join(MODELE_DATA_BASE_DIR, "predykcja")
    KATALOG_LABORATORIUM = os.path.join(MODELE_DATA_BASE_DIR, "laboratorium")

# =============================================================================
# KONFIGURACJA PARAMETRÓW STATYSTYCZNYCH - STATISTICAL PARAMETERS
# =============================================================================

class StatisticalConfig:
    """
    Parametry dla modeli statystycznych (Poisson, Dixon-Coles).
    """
    
    # Parametry Poissona
    MAX_GOLE = 8
    RHO_DIXON = -0.1
    
    # Parametry syntezy danych
    LICZBA_SYNTH = 3
    KROK = 0.02
    
    # Próg podobieństwa
    PROG = 0.03

# =============================================================================
# KONFIGURACJA SIECI NEURONOWYCH - NEURAL NETWORK PARAMETERS
# =============================================================================

class NeuralConfig:
    """
    Parametry dla sieci neuronowych.
    """
    
    # Standardowe parametry treningu
    RANDOM_STATE = 42
    EPOCHS = 200
    BATCH_SIZE = 32
    
    # Podział danych (proporcje)
    TEST_SIZE_OBSERWACJA = 0.40  # 40% na obserwację
    TEST_SIZE_WALIDACJA = 0.166666  # ~16.67% na walidację (1/6)
    TEST_SIZE_TRENING = 0.50  # 50% na trening

# =============================================================================
# KONFIGURACJA MODELI - MODEL PARAMETERS
# =============================================================================

class ModelConfig:
    """
    Ogólne parametry modeli.
    """
    
    # Nazwy baz данных
    NAZWA_BAZY = "dataBase_futbol_trend"
    
    # Ustawienia domyślne dla modeli
    DEFAULT_MODEL_NAME = "ssi_v5_default"

# =============================================================================
# KONFIGURACJA PAMIĘCI - MEMORY PARAMETERS
# =============================================================================

class MemoryConfig:
    """
    Parametry związane z systemem pamięci.
    """
    
    # Ustawienia pamięci światów
    WORLD_LEVELS = ["poziom1", "poziom2", "poziom3"]
    WORLD_HIERARCHY_ENABLED = True
    
    # Ustawienia backup
    BACKUP_DIR = PathConfig.MEMORY_DIR
    BACKUP_ENABLED = True

# =============================================================================
# KONFIGURACJA TEACHERÓW - TEACHER PARAMETERS
# =============================================================================

class TeacherConfig:
    """
    Parametry dla systemów poznawczych (Teacher).
    """
    
    # Wagi domyślne
    DEFAULT_WEIGHTS = {
        "ilosc_danych": 0.4,
        "skutecznosc": 0.3,
        "stabilnosc": 0.2,
        "dixon_coles": 0.1
    }
    
    # Ustawienia uczenia
    TEACHER_USE_RF = True  # Używanie Random Forest w Teacher
    TEACHER_LEARNING_ENABLED = True

# =============================================================================
# KONFIGURACJA AGENTÓW - AGENT PARAMETERS
# =============================================================================

class AgentConfig:
    """
    Parametry dla agentów predykcyjnych.
    """
    
    # Harmonogram pracy agentów
    AGENT_CYCLES_PER_DAY = 4
    AGENT_WORK_HOURS_PER_CYCLE = 5
    
    # Czas pracy dziennej
    DAILY_OPERATION_HOURS = 20
    
    # Cykle godzinowe
    CYCLE_TIMES = ["08:00", "13:00", "18:00", "23:00"]

# =============================================================================
# KONFIGURACJA LOGOWANIA I MONITORINGU - LOGGING CONFIGURATION
# =============================================================================

class LoggingConfig:
    """
    Parametry logowania i monitoringu.
    """
    
    # Ustawienia logów
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"
    LOG_FILE = os.path.join(PathConfig.BASE_DIR, "ssi_v5.log")
    
    # Monitoring SSI
    SSI_EVENT_LOGGING = True
    SSI_STAGE_TRACKING = True

# =============================================================================
# KONFIGURACJA PLIKÓW WEJŚCIOWYCH - INPUT FILES CONFIGURATION
# =============================================================================

class InputFilesConfig:
    """
    Konfiguracja plików wejściowych z różnych części systemu.
    """
    
    # czesc1 - Pliki kursów
    CZESC1_PLIK_KURSOW = os.path.join(PathConfig.DATA_DIR, "kursy.csv")
    
    # czesc2 - Pliki analizy trendów
    CZESC2_PLIK_PREDYKCJI = os.path.join(PathConfig.DATA_DIR, "dataBase_futbol_trend.csv")
    CZESC2_PLIK_HISTORIA = os.path.join(PathConfig.DATA_DIR, "kod_dataBase_futbol_trend.csv")
    
    # czesc3 - Pliki modeli
    CZESC3_PLIK_PREDYKCJI = os.path.join(PathConfig.DATA_DIR, "kursy_przygotowane.csv")
    CZESC3_PLIK_TRENING = os.path.join(PathConfig.DATA_DIR, "mozg_kursy_przygotowane.csv")

# =============================================================================
# INDEKSY I MAPOWANIA - INDICES AND MAPPINGS
# =============================================================================

class IndexConfig:
    """
    Indeksy kolumn i mapowania używane w systemie.
    """
    
    # Indeksy klasyfikatora (6 cech do porównania)
    LOG_INDEXY_KLASYFIKATOR = [1, 2, 3, 4, 5, 6]
    
    # Mapowanie klas wyników
    ID_NA_WYNIK = {
        0: "0:0", 1: "1:0", 2: "0:1", 3: "1:1", 4: "2:0",
        5: "0:2", 6: "2:1", 7: "1:2", 8: "2:2", 9: "3:0",
        10: "0:3", 11: "3:1", 12: "1:3", 13: "3:2", 14: "2:3",
        15: "0:4", 16: "4:0", 17: "1:4", 18: "4:1", 19: "2:4",
        20: "4:2", 21: "3:3", 22: "3:4", 23: "4:3", 24: "0:5",
        25: "5:0", 26: "1:5", 27: "5:1", 28: "2:5", 29: "5:2",
        30: "3:5", 31: "4:4", 32: "4:5", 33: "5:3", 34: "5:4",
        35: "0:6", 36: "6:0", 37: "1:6", 38: "6:1", 39: "2:6"
    }

# =============================================================================
# GŁÓWNY OBJEKT KONFIGURACJI
# =============================================================================

class SSIConfig:
    """
    Główny obiekt konfiguracji integrujący wszystkie ustawienia.
    Umożliwia dostęp do wszystkich parametrów przez jeden punkt wejścia.
    """
    
    paths = PathConfig()
    statistical = StatisticalConfig()
    neural = NeuralConfig()
    model = ModelConfig()
    memory = MemoryConfig()
    teacher = TeacherConfig()
    agent = AgentConfig()
    logging = LoggingConfig()
    input_files = InputFilesConfig()
    indices = IndexConfig()

# =============================================================================
# EKSPORT DO UŻYCIA BEZPOŚREDNIEGO
# =============================================================================

# Eksport głównych klas konfiguracyjnych
__all__ = [
    'SSIConfig',
    'PathConfig',
    'StatisticalConfig', 
    'NeuralConfig',
    'ModelConfig',
    'MemoryConfig',
    'TeacherConfig',
    'AgentConfig',
    'LoggingConfig',
    'InputFilesConfig',
    'IndexConfig',
    # Eksport instancji głównej
    'config'
]

# Utwórz instancję główną dla wygody
config = SSIConfig()

# =============================================================================
# DODATKOWE FUNKCJE UŻYTECZNE
# =============================================================================

def get_config():
    """Zwraca główną instancję konfiguracji."""
    return config

def get_path_config():
    """Zwraca konfigurację ścieżek."""
    return config.paths

def get_statistical_config():
    """Zwraca konfigurację statystyczną."""
    return config.statistical

def get_neural_config():
    """Zwraca konfigurację sieci neuronowych."""
    return config.neural

# =============================================================================
# INFORMACJE DIAGNOSTYCZNE
# =============================================================================

if __name__ == "__main__":
    print("SSI V5 Configuration Module")
    print("=" * 40)
    print(f"Base Directory: {config.paths.BASE_DIR}")
    print(f"Data Directory: {config.paths.DATA_DIR}")
    print(f"Models Directory: {config.paths.MODELS_DIR}")
    print(f"Max Goals: {config.statistical.MAX_GOLE}")
    print(f"Rho Dixon: {config.statistical.RHO_DIXON}")
    print(f"Random State: {config.neural.RANDOM_STATE}")
    print(f"Epochs: {config.neural.EPOCHS}")
    print(f"Batch Size: {config.neural.BATCH_SIZE}")
    print("Configuration loaded successfully!")
