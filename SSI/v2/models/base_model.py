"""
SSI V2 Base Model - Bazowa klasa dla wszystkich modeli V2

Zgodnie z dokumentacją:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 2.2
- 02_DATA_STRUCTURE.md Sekcja 3

Każdy model V2:
- Jest trenowany na 60% danych
- Tworzy własny świat interpretacji
- Dostarcza predykcje w formacie "X:Y"
- Ma zdefiniowany typ świata (Świat 1, 2, 3, 4)

Wersja: 1.0
Data: 2026-07-28
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Typy modeli V2"""
    ZMIANA_KURSOW = "siec_01_zmiana_kursow"
    AMPLITUDA = "siec_02_amplituda"
    TEMPO = "siec_03_tempo"
    SYNCHRONIZACJA = "siec_04_synchronizacja"
    RANDOM_FOREST = "random_forest"
    CLASSIFIER = "classifier"
    CUSTOM = "custom"


class ModelStatus(Enum):
    """Status modelu"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    TRAINING = "training"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    RETRAINING = "retraining"


class WorldType(Enum):
    """Typy światów dla modeli V2 (zgodnie z 02_DATA_STRUCTURE.md)"""
    SWIAT_1_ZMIANY_KURSOW = "swiat_1_zmiany_kursow"
    SWIAT_2_DYNAMIKA = "swiat_2_dynamika"
    SWIAT_3_KOMPLEKSOWE = "swiat_3_kompleksowe"
    SWIAT_4_RELACJE = "swiat_4_relacje"


@dataclass
class ModelConfig:
    """
    Konfiguracja modelu V2
    
    Zgodnie z 02_DATA_STRUCTURE.md Sekcja 3.2
    """
    model_name: str
    model_type: ModelType = ModelType.CUSTOM
    world_type: WorldType = WorldType.SWIAT_1_ZMIANY_KURSOW
    version: str = "1.0.0"
    description: str = ""
    
    # Parametry trenowania
    features: List[str] = field(default_factory=list)
    target_column: str = "wynik"
    test_size: float = 0.4  # 40% na obserwację
    validation_size: float = 0.1  # 10% z 60% na walidację
    random_state: int = 42
    
    # Parametry modelu
    params: Dict[str, Any] = field(default_factory=dict)
    
    # Ścieżki
    model_path: str = ""
    training_data_path: str = ""
    observation_data_path: str = ""
    
    # Flagi
    enabled: bool = True
    save_model: bool = True
    use_cache: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "model_type": self.model_type.value,
            "world_type": self.world_type.value,
            "version": self.version,
            "description": self.description,
            "features": self.features,
            "target_column": self.target_column,
            "test_size": self.test_size,
            "validation_size": self.validation_size,
            "random_state": self.random_state,
            "params": self.params,
            "enabled": self.enabled
        }


@dataclass
class ModelOutput:
    """
    Wyjście modelu V2 - predykcja
    
    Format zgodny z istniejącym systemem SSI
    """
    model_id: str
    model_name: str
    model_type: str
    world_type: str
    
    # Dane wejściowe
    input_data: Dict[str, Any] = field(default_factory=dict)
    
    # Predykcja
    prediction: str = ""  # Format "X:Y" np. "2:1", "0:0"
    prediction_group: str = "X"  # 1, X lub 2
    confidence: float = 0.5
    
    # Metadane
    match_id: str = ""
    group_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    prediction_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    
    # Dodatkowe informacje
    features_used: List[str] = field(default_factory=list)
    explanation: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        # Walidacja confidence
        self.confidence = max(0.0, min(1.0, self.confidence))
        
        # Ustal grupę predykcji
        if self.prediction and ":" in self.prediction:
            try:
                home, away = map(int, self.prediction.split(":"))
                if home > away:
                    self.prediction_group = "1"
                elif home < away:
                    self.prediction_group = "2"
                else:
                    self.prediction_group = "X"
            except (ValueError, AttributeError):
                self.prediction_group = "X"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "model_name": self.model_name,
            "model_type": self.model_type,
            "world_type": self.world_type,
            "match_id": self.match_id,
            "group_id": self.group_id,
            "prediction": self.prediction,
            "prediction_group": self.prediction_group,
            "confidence": round(self.confidence, 4),
            "timestamp": self.timestamp.isoformat(),
            "prediction_id": self.prediction_id,
            "features_used": self.features_used,
            "input_data": self.input_data
        }


@dataclass
class TrainingMetrics:
    """Metryki trenowania modelu"""
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    
    training_loss: float = 0.0
    validation_loss: float = 0.0
    
    training_accuracy: float = 0.0
    validation_accuracy: float = 0.0
    
    samples_count: int = 0
    features_count: int = 0
    training_time: float = 0.0  # w sekundach
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "accuracy": round(self.accuracy, 4),
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1_score": round(self.f1_score, 4),
            "training_loss": round(self.training_loss, 4),
            "validation_loss": round(self.validation_loss, 4),
            "training_accuracy": round(self.training_accuracy, 4),
            "validation_accuracy": round(self.validation_accuracy, 4),
            "samples_count": self.samples_count,
            "features_count": self.features_count,
            "training_time": round(self.training_time, 2)
        }


@dataclass
class ObservationMetrics:
    """Metryki z fazy obserwacji"""
    observation_count: int = 0
    correct_predictions: int = 0
    correct_group_predictions: int = 0
    
    accuracy: float = 0.0
    group_accuracy: float = 0.0
    
    avg_confidence: float = 0.0
    confidence_std: float = 0.0
    
    patterns_detected: int = 0
    anomalies_detected: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "observation_count": self.observation_count,
            "correct_predictions": self.correct_predictions,
            "correct_group_predictions": self.correct_group_predictions,
            "accuracy": round(self.accuracy, 4),
            "group_accuracy": round(self.group_accuracy, 4),
            "avg_confidence": round(self.avg_confidence, 4),
            "confidence_std": round(self.confidence_std, 4),
            "patterns_detected": self.patterns_detected,
            "anomalies_detected": self.anomalies_detected
        }


class BaseModelV2:
    """
    Bazowa klasa dla wszystkich modeli V2
    
    Odpowiedzialność:
    - Trenowanie na 60% danych
    - Predykcja na nowych danych
    - Integracja z DataWorldManager
    - Tworzenie wyjścia w standardowym formacie
    
    Zgodnie z:
    - 01_SYSTEM_ARCHITECTURE.md Sekcja 2.2
    - 02_DATA_STRUCTURE.md Sekcja 3
    """
    
    # Identyfikatory
    model_id: str
    model_name: str
    model_type: ModelType
    world_type: WorldType
    
    # Konfiguracja
    config: ModelConfig
    
    # Status
    status: ModelStatus = ModelStatus.UNINITIALIZED
    
    # Metryki
    training_metrics: TrainingMetrics = field(default_factory=TrainingMetrics)
    observation_metrics: ObservationMetrics = field(default_factory=ObservationMetrics)
    
    # Dane
    training_data: List[Dict[str, Any]] = field(default_factory=list)
    validation_data: List[Dict[str, Any]] = field(default_factory=list)
    observation_data: List[Dict[str, Any]] = field(default_factory=list)
    
    # Model (jeśli odnosi się do zewnętrznej biblioteki)
    _model: Optional[Any] = None
    
    def __init__(self, config: ModelConfig):
        """
        Inicjalizacja modelu
        
        Args:
            config: Konfiguracja modelu
        """
        self.model_id = f"v2_{config.model_name}_{uuid.uuid4().hex[:8]}"
        self.model_name = config.model_name
        self.model_type = config.model_type
        self.world_type = config.world_type
        self.config = config
        
        logger.info(f"Utworzono model V2: {self.model_name} ({self.model_type.value})")
    
    def initialize(self) -> bool:
        """
        Inicjalizacja modelu
        
        Returns:
            bool: Czy inicjalizacja się powiodła
        """
        try:
            self.status = ModelStatus.INITIALIZING
            
            if not self._initialize_internal():
                self.status = ModelStatus.ERROR
                return False
            
            self.status = ModelStatus.READY
            logger.info(f"Model {self.model_name} zainicjalizowany")
            return True
            
        except Exception as e:
            logger.error(f"Błąd inicjalizacji modelu {self.model_name}: {e}")
            self.status = ModelStatus.ERROR
            return False
    
    def _initialize_internal(self) -> bool:
        """Wewnętrzna inicjalizacja (do nadpisania przez klasy pochodne)"""
        return True
    
    def train(self, training_data: List[Dict[str, Any]], 
             validation_data: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        Trenowanie modelu
        
        Args:
            training_data: Dane treningowe (60%)
            validation_data: Dane walidacyjne (opcjonalne)
            
        Returns:
            bool: Czy trenowanie się powiodło
        """
        try:
            self.status = ModelStatus.TRAINING
            self.training_data = training_data
            self.validation_data = validation_data or []
            
            start_time = datetime.now()
            
            if not self._train_internal(training_data, validation_data):
                self.status = ModelStatus.ERROR
                return False
            
            training_time = (datetime.now() - start_time).total_seconds()
            self.training_metrics.training_time = training_time
            
            self.status = ModelStatus.READY
            logger.info(f"Model {self.model_name} wytrenowany w {training_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Błąd trenowania modelu {self.model_name}: {e}")
            self.status = ModelStatus.ERROR
            return False
    
    def _train_internal(self, training_data: List[Dict[str, Any]], 
                        validation_data: Optional[List[Dict[str, Any]]]) -> bool:
        """Wewnętrzne trenowanie (do nadpisania)"""
        # Domyślna implementacja - nic nie robi
        return True
    
    def predict(self, input_data: Dict[str, Any], **kwargs) -> ModelOutput:
        """
        Generowanie predykcji
        
        Args:
            input_data: Dane wejściowe
            **kwargs: Dodatkowe parametry
            
        Returns:
            ModelOutput: Predykcja
        """
        try:
            prediction = self._predict_internal(input_data, **kwargs)
            
            # Uzupełnienie metadanych
            prediction.model_id = self.model_id
            prediction.model_name = self.model_name
            prediction.model_type = self.model_type.value
            prediction.world_type = self.world_type.value
            prediction.input_data = input_data
            prediction.features_used = self.config.features
            
            return prediction
            
        except Exception as e:
            logger.error(f"Błąd predykcji modelu {self.model_name}: {e}")
            # Zwróć domyślną predykcję
            return ModelOutput(
                model_id=self.model_id,
                model_name=self.model_name,
                model_type=self.model_type.value,
                world_type=self.world_type.value,
                prediction="0:0",
                confidence=0.5
            )
    
    def _predict_internal(self, input_data: Dict[str, Any], **kwargs) -> ModelOutput:
        """Wewnętrzna predykcja (do nadpisania)"""
        # Domyślna implementacja - losowa predykcja
        import random
        predictions = ["1:0", "0:1", "2:0", "0:2", "1:1", "2:1", "1:2", "3:0", "0:3"]
        prediction = random.choice(predictions)
        confidence = random.uniform(0.5, 0.9)
        
        return ModelOutput(
            prediction=prediction,
            confidence=confidence
        )
    
    def observe(self, input_data: Dict[str, Any], actual_result: str, **kwargs) -> bool:
        """
        Obserwacja - porównanie predykcji z rzeczywistością
        
        Args:
            input_data: Dane wejściowe
            actual_result: Rzeczywisty wynik (format "X:Y")
            **kwargs: Dodatkowe parametry
            
        Returns:
            bool: Czy obserwacja się powiodła
        """
        try:
            # Generuj predykcję
            prediction = self.predict(input_data)
            
            # Zapisz obserwację
            observation = {
                "model_id": self.model_id,
                "model_name": self.model_name,
                "timestamp": datetime.now().isoformat(),
                "input_data": input_data,
                "prediction": prediction.prediction,
                "prediction_group": prediction.prediction_group,
                "confidence": prediction.confidence,
                "actual_result": actual_result,
                "correct": prediction.prediction == actual_result,
                "correct_group": self._get_group(actual_result) == prediction.prediction_group
            }
            
            self.observation_data.append(observation)
            
            # Aktualizuj metryki
            self._update_observation_metrics(observation)
            
            logger.debug(f"Obserwacja modelu {self.model_name}: "
                        f"Predykcja={prediction.prediction}, Rzeczywisty={actual_result}")
            return True
            
        except Exception as e:
            logger.error(f"Błąd obserwacji modelu {self.model_name}: {e}")
            return False
    
    def _get_group(self, result: str) -> str:
        """Pobieranie grupy wyniku (1, X, 2)"""
        if ":" not in result:
            return "X"
        try:
            home, away = map(int, result.split(":"))
            if home > away:
                return "1"
            elif home < away:
                return "2"
            else:
                return "X"
        except (ValueError, AttributeError):
            return "X"
    
    def _update_observation_metrics(self, observation: Dict[str, Any]) -> None:
        """Aktualizacja metryk obserwacji"""
        self.observation_metrics.observation_count += 1
        
        if observation.get("correct"):
            self.observation_metrics.correct_predictions += 1
        if observation.get("correct_group"):
            self.observation_metrics.correct_group_predictions += 1
        
        # Aktualizuj średnią confidence
        total_count = self.observation_metrics.observation_count
        total_confidence = self.observation_metrics.avg_confidence * (total_count - 1)
        total_confidence += observation.get("confidence", 0.5)
        self.observation_metrics.avg_confidence = total_confidence / total_count
        
        # Aktualizuj accuracy
        if total_count > 0:
            self.observation_metrics.accuracy = (self.observation_metrics.correct_predictions / total_count)
            self.observation_metrics.group_accuracy = (self.observation_metrics.correct_group_predictions / total_count)
    
    def evaluate(self, data: List[Dict[str, Any]]) -> TrainingMetrics:
        """
        Otwarta ewidencja modelu na danych
        
        Args:
            data: Dane do ewidencji
            
        Returns:
            TrainingMetrics: Metryki ewidencji
        """
        # Domyślna implementacja - zwraca zera
        return TrainingMetrics()
    
    def save(self, path: str) -> bool:
        """
        Zapisz model do pliku
        
        Args:
            path: Ścieżka zapisu
            
        Returns:
            bool: Czy zapis się powiódł
        """
        # Domyślna implementacja - nie robi nic
        return False
    
    def load(self, path: str) -> bool:
        """
        Wczytaj model z pliku
        
        Args:
            path: Ścieżka pliku
            
        Returns:
            bool: Czy wczytanie się powiodło
        """
        # Domyślna implementacja - nie robi nic
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Pobieranie statusu modelu"""
        return {
            "model_id": self.model_id,
            "model_name": self.model_name,
            "model_type": self.model_type.value,
            "world_type": self.world_type.value,
            "status": self.status.value,
            "training_samples": len(self.training_data),
            "validation_samples": len(self.validation_data),
            "observation_samples": len(self.observation_data),
            "training_metrics": self.training_metrics.to_dict(),
            "observation_metrics": self.observation_metrics.to_dict()
        }
    
    def get_world_features(self) -> List[str]:
        """
        Pobieranie cech charakterystycznych dla świata modelu
        
        Returns:
            List[str]: Lista cech
        """
        return self.config.features
    
    def get_model_info(self) -> Dict[str, Any]:
        """Pobieranie informacji o modelu"""
        return {
            "model_id": self.model_id,
            "model_name": self.model_name,
            "model_type": self.model_type.value,
            "world_type": self.world_type.value,
            "version": self.config.version,
            "description": self.config.description,
            "enabled": self.config.enabled,
            "features": self.config.features,
            "target_column": self.config.target_column
        }


if __name__ == "__main__":
    # Testy
    print("Testing BaseModelV2...")
    
    # Tworzenie konfiguracji
    config = ModelConfig(
        model_name="test_model",
        model_type=ModelType.CUSTOM,
        world_type=WorldType.SWIAT_1_ZMIANY_KURSOW,
        features=["zmiana_1", "zmiana_X", "zmiana_2"]
    )
    
    # Tworzenie modelu
    model = BaseModelV2(config)
    print(f"Model utworzony: {model.model_name}")
    
    # Inicjalizacja
    model.initialize()
    print(f"Status: {model.status}")
    
    # Predykcja
    test_data = {
        "zmiana_1": 0.5,
        "zmiana_X": 0.3,
        "zmiana_2": -0.2
    }
    prediction = model.predict(test_data)
    print(f"Predykcja: {prediction.prediction} (grupa: {prediction.prediction_group}, confidence: {prediction.confidence})")
    
    # Obserwacja
    model.observe(test_data, "2:1")
    print(f"Obserwacje: {len(model.observation_data)}")
    
    print("\nAll tests passed!")
