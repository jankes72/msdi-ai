"""
SSI V2 Model Observer - Obserwator modeli

Zgodnie z dokumentacją:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 2.2 (40% obserwacja)
- 02_DATA_STRUCTURE.md

Odpowiedzialność:
- Obserwacja modeli na 40% danych
- Zapis obserwacji (predykcja vs rzeczywistość)
- Analiza zachowania modelu
- Statystyki obserwacji

Wersja: 1.0
Data: 2026-07-28
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ObservationConfig:
    """
    Konfiguracja obserwacji
    
    Zgodnie z zasadą 60/40:
    - 60% na trening
    - 40% na obserwację (nie uczy modelu, tylko obserwuje)
    """
    observation_split: float = 0.4  # 40% na obserwację
    min_observations_per_model: int = 100
    
    # Co zapisywać
    save_predictions: bool = True
    save_confidence: bool = True
    save_explanations: bool = True
    
    # Flagi
    track_accuracy: bool = True
    track_group_accuracy: bool = True
    detect_patterns: bool = True
    build_memory: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "observation_split": self.observation_split,
            "min_observations_per_model": self.min_observations_per_model,
            "save_predictions": self.save_predictions,
            "save_confidence": self.save_confidence,
            "track_accuracy": self.track_accuracy,
            "track_group_accuracy": self.track_group_accuracy,
            "detect_patterns": self.detect_patterns,
            "build_memory": self.build_memory
        }


@dataclass
class ObservationResult:
    """Wynik obserwacji"""
    model_id: str
    model_name: str
    
    # Dane
    observation_count: int = 0
    correct_predictions: int = 0
    correct_group_predictions: int = 0
    
    # Metryki
    accuracy: float = 0.0
    group_accuracy: float = 0.0
    avg_confidence: float = 0.0
    
    # Wzorce
    patterns_detected: int = 0
    anomalies_detected: int = 0
    
    # Wykryte zachowania
    behaviors: Dict[str, int] = field(default_factory=dict)
    
    # Obszar czasowy
    observation_period_start: Optional[datetime] = None
    observation_period_end: Optional[datetime] = None
    
    # Wszystkie obs
    all_observations: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "model_name": self.model_name,
            "observation_count": self.observation_count,
            "correct_predictions": self.correct_predictions,
            "correct_group_predictions": self.correct_group_predictions,
            "accuracy": round(self.accuracy, 4),
            "group_accuracy": round(self.group_accuracy, 4),
            "avg_confidence": round(self.avg_confidence, 4),
            "patterns_detected": self.patterns_detected,
            "anomalies_detected": self.anomalies_detected,
            "behaviors": self.behaviors
        }


@dataclass
class BehaviorPattern:
    """Wykryty wzorzec zachowania"""
    pattern_name: str
    pattern_type: str = "normal"  # normal, anomaly, trend, cycle
    
    frequency: int = 0
    first_observed: Optional[datetime] = None
    last_observed: Optional[datetime] = None
    
    characteristics: Dict[str, Any] = field(default_factory=dict)
    examples: List[str] = field(default_factory=list)  # match_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_name": self.pattern_name,
            "pattern_type": self.pattern_type,
            "frequency": self.frequency,
            "characteristics": self.characteristics,
            "examples_count": len(self.examples)
        }


class ModelObserver:
    """
    Obserwator modeli V2
    
    Odpowiedzialność:
    - Obserwacja predykcji vs rzeczywistości
    - Zapis i analiza obserwacji
    - Wykrywanie wzorców zachowania
    - Statystyki dokładności
    
    Zgodnie z:
    - 01_SYSTEM_ARCHITECTURE.md Sekcja 2.2 (40% obserwacja)
    """
    
    def __init__(self, config: Optional[ObservationConfig] = None):
        """
        Inicjalizacja obserwatora
        
        Args:
            config: Opcjonalna konfiguracja
        """
        self.config = config or ObservationConfig()
        self.observation_results: Dict[str, ObservationResult] = {}
        self.behavior_patterns: Dict[str, BehaviorPattern] = {}
        
        # Obszar statystyk
        self.total_observations: int = 0
        self.total_correct: int = 0
        self.total_group_correct: int = 0
        
        logger.info("ModelObserver zainicjowany")
    
    def observe(self, model: Any, input_data: Dict[str, Any], 
                actual_result: str, **kwargs) -> bool:
        """
        Zarejestrowanie jednej obserwacji
        
        Args:
            model: Model którego predykcję obserwujemy
            input_data: Dane wejściowe
            actual_result: Rzeczywisty wynik
            **kwargs: Dodatkowe parametry
            
        Returns:
            bool: Czy obserwacja została zapisana
        """
        try:
            # Generuj predykcję
            prediction = model.predict(input_data)
            timestamp = datetime.now()
            
            # Utwórz rekord obserwacji
            observation = {
                "model_id": model.model_id,
                "model_name": model.model_name,
                "model_type": model.model_type.value,
                "timestamp": timestamp.isoformat(),
                "input_data": input_data,
                "prediction": prediction.prediction,
                "prediction_group": prediction.prediction_group,
                "confidence": prediction.confidence,
                "actual_result": actual_result,
                "actual_group": self._get_group(actual_result),
                "correct": prediction.prediction == actual_result,
                "correct_group": prediction.prediction_group == self._get_group(actual_result),
                "match_id": input_data.get("mecz", ""),
                "group_id": input_data.get("id_grupy", ""),
                "explanation": prediction.explanation if self.config.save_explanations else None
            }
            
            # Aktualizuj statystyki modelu
            model.observe(input_data, actual_result)
            
            # Zapisz obserwację
            self._save_observation(model.model_id, observation)
            
            # Zaktualizuj statystyki globalne
            self._update_statistics(observation)
            
            # Wykryj wzorce
            if self.config.detect_patterns:
                self._detect_behavior_patterns(model, observation)
            
            logger.debug(f"Obserwacja: {model.model_name} -> "
                        f"Predykcja={prediction.prediction}, Rzeczywisty={actual_result}")
            
            return True
            
        except Exception as e:
            logger.error(f"Błąd obserwacji: {e}")
            return False
    
    def observe_batch(self, model: Any, observations: List[Tuple[Dict[str, Any], str]], **kwargs) -> int:
        """
        Obserwacja wsadowa (wiele meczy naraz)
        
        Args:
            model: Model
            observations: Lista (input_data, actual_result)
            **kwargs: Dodatkowe parametry
            
        Returns:
            int: Liczba zarejestrowanych obserwacji
        """
        count = 0
        for input_data, actual_result in observations:
            if self.observe(model, input_data, actual_result, **kwargs):
                count += 1
        return count
    
    def observe_multiple_models(self, models: List[Any], input_data: Dict[str, Any],
                                actual_result: str, **kwargs) -> Dict[str, bool]:
        """
        Obserwuj predykcje wielu modeli na tych samych danych
        
        Args:
            models: Lista modeli
            input_data: Dane wejściowe
            actual_result: Rzeczywisty wynik
            **kwargs: Dodatkowe parametry
            
        Returns:
            Dict[str, bool]: Wynik obserwacji dla każdego modelu
        """
        results = {}
        for model in models:
            results[model.model_id] = self.observe(model, input_data, actual_result, **kwargs)
        return results
    
    def _save_observation(self, model_id: str, observation: Dict[str, Any]) -> None:
        """Zapisanie pojedynczej obserwacji"""
        # Utwórz oder zaktualizuj wynik obserwacji
        if model_id not in self.observation_results:
            self.observation_results[model_id] = ObservationResult(
                model_id=model_id,
                model_name=observation["model_name"]
            )
        
        result = self.observation_results[model_id]
        
        # Zaktualizu you standard
        result.observation_count += 1
        result.all_observations.append(observation)
        
        if observation.get("correct"):
            result.correct_predictions += 1
        if observation.get("correct_group"):
            result.correct_group_predictions += 1
        
        # Zaktualizuj średnią confidence
        total_count = result.observation_count
        if total_count > 0:
            result.avg_confidence = (
                result.avg_confidence * (total_count - 1) + observation.get("confidence", 0.5)
            ) / total_count
        
        # Zaktualizuj accuracy
        if total_count > 0:
            result.accuracy = result.correct_predictions / total_count
            result.group_accuracy = result.correct_group_predictions / total_count
        
        # Zaktualizuj period
        timestamp = datetime.fromisoformat(observation.get("timestamp", ""))
        if result.observation_period_start is None or timestamp < result.observation_period_start:
            result.observation_period_start = timestamp
        if result.observation_period_end is None or timestamp > result.observation_period_end:
            result.observation_period_end = timestamp
    
    def _update_statistics(self, observation: Dict[str, Any]) -> None:
        """Aktualizacja statystyk globalnych"""
        self.total_observations += 1
        
        if observation.get("correct"):
            self.total_correct += 1
        if observation.get("correct_group"):
            self.total_group_correct += 1
    
    def _get_group(self, result: str) -> str:
        """Pobieranie grupy wyniku"""
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
    
    def _detect_behavior_patterns(self, model: Any, observation: Dict[str, Any]) -> None:
        """Wykrywanie wzorców zachowania"""
        try:
            # Analiza cech wejściowych
            input_data = observation.get("input_data", {})
            prediction = observation.get("prediction", "")
            actual = observation.get("actual_result", "")
            correct = observation.get("correct", False)
            
            # Określ typ wzorca
            pattern_name = self._classify_observation(model, input_data, prediction, actual, correct)
            
            # Zaktualizuj lub utwórz wzorcec
            if pattern_name not in self.behavior_patterns:
                self.behavior_patterns[pattern_name] = BehaviorPattern(
                    pattern_name=pattern_name,
                    first_observed=datetime.fromisoformat(observation.get("timestamp", ""))
                )
            
            pattern = self.behavior_patterns[pattern_name]
            pattern.frequency += 1
            pattern.last_observed = datetime.fromisoformat(observation.get("timestamp", ""))
            
            # Zapisz match_id jako przykład
            match_id = observation.get("match_id", "")
            if match_id and match_id not in pattern.examples:
                pattern.examples.append(match_id)
                if len(pattern.examples) > 10:  # Ogranicz do 10
                    pattern.examples = pattern.examples[-10:]
            
            # Zapisz cechy charakterystyczne
            for key, value in input_data.items():
                pattern.characteristics[key] = pattern.characteristics.get(key, 0) + float(value)
            
            logger.debug(f"Wykryto wzorzec: {pattern_name}")
            
        except Exception as e:
            logger.warning(f"Wykrywanie wzorców: {e}")
    
    def _classify_observation(self, model: Any, input_data: Dict[str, Any],
                             prediction: str, actual: str, correct: bool) -> str:
        """Klasyfikacja obserwacji do wzorca"""
        patterns = []
        
        # 1. Na podstawie poprawności
        if correct:
            patterns.append("correct_prediction")
        else:
            patterns.append("incorrect_prediction")
            
            # Sprawdź czy trafił grupowo
            pred_group = self._get_group(prediction)
            actual_group = self._get_group(actual)
            if pred_group == actual_group:
                patterns.append("correct_group_wrong_exact")
            else:
                patterns.append("wrong_group")
        
        # 2. Na podstawie cech
        zmiana_1 = float(input_data.get("zmiana_1", 0.0))
        synchronizacja = float(input_data.get("synchronizacja", 0.5))
        
        if abs(zmiana_1) > 0.5:
            patterns.append("high_change")
        elif abs(zmiana_1) > 0.2:
            patterns.append("medium_change")
        
        if synchronizacja > 0.7:
            patterns.append("high_sync")
        elif synchronizacja < 0.3:
            patterns.append("low_sync")
        
        # 3. Na podstawie confidence
        confidence = float(input_data.get("confidence", 0.5))
        if confidence > 0.8:
            patterns.append("high_confidence")
        elif confidence < 0.5:
            patterns.append("low_confidence")
        
        # Połączenie
        return "_".join(patterns) if patterns else "unknown"
    
    def get_observation_result(self, model_id: str) -> Optional[ObservationResult]:
        """Pobieranie wyniku obserwacji dla modelu"""
        return self.observation_results.get(model_id)
    
    def get_all_results(self) -> Dict[str, ObservationResult]:
        """Pobieranie wszystkich wyników obserwacji"""
        return self.observation_results
    
    def get_behavior_patterns(self) -> Dict[str, BehaviorPattern]:
        """Pobieranie wykrytych wzorców zachowania"""
        return self.behavior_patterns
    
    def get_pattern(self, pattern_name: str) -> Optional[BehaviorPattern]:
        """Pobieranie konkretnego wzorca"""
        return self.behavior_patterns.get(pattern_name)
    
    def get_summary(self) -> Dict[str, Any]:
        """Pobieranie podsumowania obserwacji"""
        return {
            "total_observations": self.total_observations,
            "total_correct": self.total_correct,
            "total_group_correct": self.total_group_correct,
            "overall_accuracy": round(self.total_correct / self.total_observations, 4) if self.total_observations > 0 else 0.0,
            "overall_group_accuracy": round(self.total_group_correct / self.total_observations, 4) if self.total_observations > 0 else 0.0,
            "models_observed": len(self.observation_results),
            "patterns_detected": len(self.behavior_patterns),
            "observation_results": {k: v.to_dict() for k, v in self.observation_results.items()},
            "behavior_patterns": {k: v.to_dict() for k, v in self.behavior_patterns.items()}
        }
    
    def clear_observations(self) -> None:
        """Czyszczenie obserwacji"""
        self.observation_results = {}
        self.total_observations = 0
        self.total_correct = 0
        self.total_group_correct = 0
        logger.info("Obserwacje wyczyszczone")


if __name__ == "__main__":
    print("Testing ModelObserver...")
    
    # Test 1: Tworzenie obserwatora
    from SSI.v2.models import Siec01ZmianaKursow
    observer = ModelObserver()
    print(f"Obserwator utworzony")
    
    # Test 2: Tworzenie modelu
    model = Siec01ZmianaKursow()
    model.initialize()
    
    # Test 3: Symulacja obserwacji
    test_cases = [
        ({"zmiana_1": -0.5, "zmiana_X": 0.1, "zmiana_2": 0.3, "mecz": "Test1"}, "2:0"),
        ({"zmiana_1": 0.2, "zmiana_X": -0.4, "zmiana_2": -0.1, "mecz": "Test2"}, "0:1"),
        ({"zmiana_1": 0.0, "zmiana_X": -0.3, "zmiana_2": 0.0, "mecz": "Test3"}, "1:1"),
    ]
    
    count = observer.observe_batch(model, test_cases)
    print(f"Zarejestrowano {count} obserwacji")
    
    # Podsumowanie
    summary = observer.get_summary()
    print(f"Podsumowanie: {summary['total_observations']} obserwacji, "
          f"accuracy: {summary['overall_accuracy']:.2f}")
    
    print("\nModelObserver tests passed!")
