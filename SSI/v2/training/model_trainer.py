"""
SSI V2 Model Trainer - Trenowanie modeli V2

Zgodnie z dokumentacją:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 2.2 (Podział 60/40)
- 02_DATA_STRUCTURE.md Sekcja 3.1

Odpowiedzialność:
- Trenowanie modeli na 60% danych
- Walidacja modeli
- Cross-validation
- Zarządzanie procesem trenowania

Wersja: 1.0
Data: 2026-07-28
"""

from typing import Dict, List, Optional, Any, Tuple, Protocol
from dataclasses import dataclass, field
from datetime import datetime
import logging
import random
import time

logger = logging.getLogger(__name__)


@dataclass
class TrainingConfig:
    """
    Konfiguracja procesu trenowania
    
    Zgodnie z zasadą 60/40:
    - 60% danych na trening
    - 40% na obserwację (nie uczy modelu)
    """
    # Proporcje danych
    train_split: float = 0.6  # 60% na trening
    validation_split: float = 0.4  # 40% z 60% na walidację = 24% total
    test_size: float = 0.4  # 40% na obserwację (niezmienione)
    
    # Parametry trenowania
    epochs: int = 100
    batch_size: int = 32
    learning_rate: float = 0.01
    
    # Cross-validation
    cross_validation_folds: int = 5
    
    # Random state
    random_state: int = 42
    
    # Flagi
    shuffle: bool = True
    stratify: bool = True
    early_stopping: bool = True
    early_stopping_patience: int = 10
    
    # Metryki
    metrics: List[str] = field(default_factory=lambda: ["accuracy", "f1", "precision", "recall"])
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "train_split": self.train_split,
            "validation_split": self.validation_split,
            "test_size": self.test_size,
            "epochs": self.epochs,
            "batch_size": self.batch_size,
            "learning_rate": self.learning_rate,
            "cross_validation_folds": self.cross_validation_folds,
            "random_state": self.random_state,
            "shuffle": self.shuffle,
            "early_stopping": self.early_stopping,
            "early_stopping_patience": self.early_stopping_patience,
            "metrics": self.metrics
        }


@dataclass
class TrainingResult:
    """Wynik procesu trenowania"""
    model_name: str
    training_time: float = 0.0
    samples_trained: int = 0
    
    # Metryki
    train_accuracy: float = 0.0
    train_loss: float = 0.0
    val_accuracy: float = 0.0
    val_loss: float = 0.0
    
    # Cross-validation
    cv_scores: List[float] = field(default_factory=list)
    mean_cv_score: float = 0.0
    std_cv_score: float = 0.0
    
    # Status
    completed: bool = False
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "training_time": round(self.training_time, 2),
            "samples_trained": self.samples_trained,
            "train_accuracy": round(self.train_accuracy, 4),
            "train_loss": round(self.train_loss, 4),
            "val_accuracy": round(self.val_accuracy, 4),
            "val_loss": round(self.val_loss, 4),
            "mean_cv_score": round(self.mean_cv_score, 4),
            "std_cv_score": round(self.std_cv_score, 4),
            "completed": self.completed,
            "error": self.error
        }


@dataclass
class ValidationResult:
    """Wynik walidacji modelu"""
    model_name: str
    validation_samples: int = 0
    
    # Metryki
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    
    # Błędy
    errors: List[Dict[str, Any]] = field(default_factory=list)
    
    # Matryca pomyłek
    confusion_matrix: Dict[str, Dict[str, int]] = field(default_factory=dict)
    
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "validation_samples": self.validation_samples,
            "accuracy": round(self.accuracy, 4),
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1_score": round(self.f1_score, 4)
        }


@dataclass
class CrossValidationConfig:
    """Konfiguracja cross-validation"""
    n_folds: int = 5
    shuffle: bool = True
    random_state: int = 42
    stratify: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "n_folds": self.n_folds,
            "shuffle": self.shuffle,
            "random_state": self.random_state,
            "stratify": self.stratify
        }


class ModelTrainer:
    """
    Trenowanie modeli V2
    
    Odpowiedzialność:
    - Trenowanie pojedynczych modeli
    - Walidacja krzyżowa
    - Optymalizacja hiperparametrów
    - Zarządzanie procesem trenowania
    """
    
    def __init__(self, config: Optional[TrainingConfig] = None):
        """
        Inicjalizacja trainsera
        
        Args:
            config: Opcjonalna konfiguracja
        """
        self.config = config or TrainingConfig()
        self.training_results: Dict[str, TrainingResult] = {}
        self.validation_results: Dict[str, ValidationResult] = {}
        logger.info("ModelTrainer zainicjowany")
    
    def train_model(self, model: Any, training_data: List[Dict[str, Any]],
                    validation_data: Optional[List[Dict[str, Any]]] = None) -> TrainingResult:
        """
        Trenowanie pojedynczego modelu
        
        Args:
            model: Model do wytrenowania
            training_data: Dane treningowe
            validation_data: Dane walidacyjne (opcjonalne)
            
        Returns:
            TrainingResult: Wynik trenowania
        """
        start_time = time.time()
        
        try:
            # Inicjalizacja modelu
            if not model.initialize():
                return TrainingResult(
                    model_name=model.model_name,
                    completed=False,
                    error="Błąd inicjalizacji modelu"
                )
            
            # Trenowanie
            if not model.train(training_data, validation_data):
                return TrainingResult(
                    model_name=model.model_name,
                    completed=False,
                    error="Błąd trenowania modelu"
                )
            
            #Oblicz czas trenowania
            training_time = time.time() - start_time
            
            # Ewaluacja na danych walidacyjnych
            val_accuracy = 0.0
            if validation_data:
                validation_result = self.validate_model(model, validation_data)
                val_accuracy = validation_result.accuracy
                self.validation_results[model.model_id] = validation_result
            
            # Utwórz wynik
            result = TrainingResult(
                model_name=model.model_name,
                training_time=training_time,
                samples_trained=len(training_data),
                train_accuracy=model.training_metrics.training_accuracy,
                train_loss=model.training_metrics.training_loss,
                val_accuracy=val_accuracy,
                val_loss=model.training_metrics.validation_loss,
                completed=True
            )
            
            self.training_results[model.model_id] = result
            logger.info(f"Model {model.model_name} wytrenowany w {training_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Błąd trenowania modelu {model.model_name}: {e}")
            return TrainingResult(
                model_name=model.model_name,
                completed=False,
                error=str(e)
            )
    
    def train_multiple_models(self, models: List[Any], training_data: List[Dict[str, Any]],
                              validation_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, TrainingResult]:
        """
        Trenowanie wielu modeli
        
        Args:
            models: Lista modeli do wytrenowania
            training_data: Dane treningowe
            validation_data: Dane walidacyjne
            
        Returns:
            Dict[str, TrainingResult]: Wyniki trenowania
        """
        results = {}
        
        for model in models:
            result = self.train_model(model, training_data, validation_data)
            results[model.model_id] = result
        
        logger.info(f"Wytrenowano {len(results)} modeli")
        return results
    
    def validate_model(self, model: Any, validation_data: List[Dict[str, Any]]) -> ValidationResult:
        """
        Walidacja modelu na danych walidacyjnych
        
        Args:
            model: Wytrenowany model
            validation_data: Dane do walidacji
            
        Returns:
            ValidationResult: Wynik walidacji
        """
        try:
            if not validation_data:
                return ValidationResult(
                    model_name=model.model_name,
                    validation_samples=0,
                    error="Brak danych walidacyjnych"
                )
            
            correct_predictions = 0
            predictions_by_class: Dict[str, int] = {}
            actual_by_class: Dict[str, int] = {}
            confusion_matrix: Dict[str, Dict[str, int]] = {}
            
            # Walidacja na każdej próbce
            for sample in validation_data:
                # Generuj predykcję
                input_data = {k: v for k, v in sample.items() if k != "wynik"}
                prediction = model.predict(input_data)
                actual = sample.get("wynik", "0:0")
                
                # Sprawdź czy poprawna
                if prediction.prediction == actual:
                    correct_predictions += 1
                
                # Klasyfikacja grupowa
                pred_group = self._get_group(prediction.prediction)
                actual_group = self._get_group(actual)
                
                if pred_group == actual_group:
                    correct_predictions += 0.5  # Częściowa poprawność
                
                # Aktualizuj statystyki
                predictions_by_class[prediction.prediction] = predictions_by_class.get(prediction.prediction, 0) + 1
                actual_by_class[actual] = actual_by_class.get(actual, 0) + 1
                
                # Matryca pomyłek
                if actual not in confusion_matrix:
                    confusion_matrix[actual] = {}
                confusion_matrix[actual][prediction.prediction] = confusion_matrix[actual].get(prediction.prediction, 0) + 1
            
            # Oblicz metryki
            total_samples = len(validation_data)
            accuracy = correct_predictions / total_samples if total_samples > 0 else 0.0
            
            result = ValidationResult(
                model_name=model.model_name,
                validation_samples=total_samples,
                accuracy=accuracy,
                confusion_matrix=confusion_matrix
            )
            
            logger.info(f"Walidacja modelu {model.model_name}: accuracy={accuracy:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"Błąd walidacji modelu {model.model_name}: {e}")
            return ValidationResult(
                model_name=model.model_name,
                validation_samples=0,
                error=str(e)
            )
    
    def cross_validate(self, model: Any, data: List[Dict[str, Any]],
                       config: Optional[CrossValidationConfig] = None) -> TrainingResult:
        """
        Cross-validation modelu
        
        Args:
            model: Model do zwalidowania
            data: Dane do cross-validation
            config: Konfiguracja CV
            
        Returns:
            TrainingResult: Wynik z cross-validation
        """
        cv_config = config or CrossValidationConfig(
            n_folds=5,
            random_state=self.config.random_state
        )
        
        try:
            if not data or cv_config.n_folds <= 1:
                return TrainingResult(
                    model_name=model.model_name,
                    completed=False,
                    error="Niewłaściwa konfiguracja CV"
                )
            
            # Uproszczona symulacja cross-validation
            fold_size = len(data) // cv_config.n_folds
            cv_scores = []
            
            for fold in range(cv_config.n_folds):
                # Podział na foldy
                start = fold * fold_size
                end = (fold + 1) * fold_size if fold < cv_config.n_folds - 1 else len(data)
                
                # Zwieważone fold
                val_data = data[start:end]
                train_data = data[:start] + data[end:]
                
                # Trenuj i waliduj
                model_copy = self._clone_model(model)
                self.train_model(model_copy, train_data, val_data)
                
                # Walidacja
                val_result = self.validate_model(model_copy, val_data)
                cv_scores.append(val_result.accuracy)
            
            # Oblicz średnie
            mean_score = sum(cv_scores) / len(cv_scores) if cv_scores else 0.0
            std_score = (sum((s - mean_score) ** 2 for s in cv_scores) / len(cv_scores)) ** 0.5 if len(cv_scores) > 1 else 0.0
            
            result = TrainingResult(
                model_name=model.model_name,
                training_time=0.0,  # Całkowity czas
                samples_trained=len(data),
                mean_cv_score=mean_score,
                std_cv_score=std_score,
                cv_scores=cv_scores,
                completed=True
            )
            
            logger.info(f"CV modelu {model.model_name}: mean={mean_score:.4f}, std={std_score:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"Błąd CV modelu {model.model_name}: {e}")
            return TrainingResult(
                model_name=model.model_name,
                completed=False,
                error=str(e)
            )
    
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
    
    def _clone_model(self, model: Any) -> Any:
        """
        Klonowanie modelu (uproszczone)
        
        W rzeczywistości trzeba by zaimplementować deep copy
        """
        # Uproszczenie: zwróć nową instancję z tą samą konfiguracją
        from copy import deepcopy
        return deepcopy(model)
    
    def get_summary(self) -> Dict[str, Any]:
        """Pobieranie podsumowania trenowania"""
        return {
            "training_results": {k: v.to_dict() for k, v in self.training_results.items()},
            "validation_results": {k: v.to_dict() for k, v in self.validation_results.items()},
            "total_models_trained": len(self.training_results),
            "total_models_validated": len(self.validation_results)
        }
    
    def clear_results(self) -> None:
        """Czyszczenie wyników"""
        self.training_results = {}
        self.validation_results = {}
        logger.info("Wyniki wyczyszczone")


if __name__ == "__main__":
    print("Testing ModelTrainer...")
    
    # Test 1: Tworzenie trainer
    trainer = ModelTrainer()
    print(f"Trainer utworzony")
    
    # Test 2: Podsumowanie
    summary = trainer.get_summary()
    print(f"Podsumowanie: {summary}")
    
    print("\nModelTrainer tests passed!")
