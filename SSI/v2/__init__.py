"""
SSI V2 Model Laboratory
Warstwa modeli interpretujących świat

Zgodnie z dokumentacją:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 2.2 (V2 Model Laboratory)
- 02_DATA_STRUCTURE.md Sekcja 3 (Struktury Danych V2)

Odpowiedzialność:
- Trenowanie modeli na 60% danych
- Niezależna obserwacja na 40% danych
- Tworzenie światów interpretacji przez każdy model
- Podział: 60% trening+walidacja, 40% obserwacja

Modele V2:
- siec_01_zmiana_kursow (Świat zmian kursów)
- siec_02_amplituda (Świat amplitudy)
- siec_03_tempo (Świat tempa/dynamiki)
- siec_04_synchronizacja (Świat synchronizacji)
- RandomForest (Klasyfikator)
- Klasyfikatory (Inne modele)

Wersja: 1.0
Data: 2026-07-28
"""

from .models import (
    BaseModelV2, ModelType, ModelStatus, ModelConfig,
    Siec01ZmianaKursow, Siec02Amplituda, Siec03Tempo, Siec04Synchronizacja,
    RandomForestModel, ClassifierModel
)
from .training import (
    ModelTrainer, TrainingConfig, TrainingResult,
    ValidationResult, CrossValidationConfig
)
from .observation import (
    ModelObserver, ObservationConfig, ObservationResult,
    PatternDetector, MemoryBuilder, MemoryConfig, tworz_memory_builder
)
from .integration import (
    V2Integration, V2Config, PredictionResult, CalibrationData, tworz_integracje_v2,
    ModelOutputAggregator, AggregationConfig, AggregatedPrediction, tworz_agregator,
    V2ToV3Bridge, BridgeConfig, WorldDataPackage, tworz_bridge_v2_v3
)

__all__ = [
    # Models
    'BaseModelV2', 'ModelType', 'ModelStatus', 'ModelConfig',
    'Siec01ZmianaKursow', 'Siec02Amplituda', 'Siec03Tempo', 'Siec04Synchronizacja',
    'RandomForestModel', 'ClassifierModel',
    # Training
    'ModelTrainer', 'TrainingConfig', 'TrainingResult',
    'ValidationResult', 'CrossValidationConfig',
    # Observation
    'ModelObserver', 'ObservationConfig', 'ObservationResult',
    'PatternDetector', 'MemoryBuilder', 'MemoryConfig', 'tworz_memory_builder',
    # Integration
    'V2Integration', 'V2Config', 'PredictionResult', 'CalibrationData', 'tworz_integracje_v2',
    'ModelOutputAggregator', 'AggregationConfig', 'AggregatedPrediction', 'tworz_agregator',
    'V2ToV3Bridge', 'BridgeConfig', 'WorldDataPackage', 'tworz_bridge_v2_v3'
]
