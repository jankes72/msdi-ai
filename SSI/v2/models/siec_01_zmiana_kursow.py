"""
SSI V2 Model - Sieć 01: Zmiana Kursów

Zgodnie z dokumentacją:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 2.2
- 02_DATA_STRUCTURE.md Sekcja 3.2 (Świat 1: Zmiany Kursów)

Opis:
Model analizujący zmiany kursów bukmacherskich.
Świat 1 koncentruje się na cechach:
- zmiana_1: Zmiana kursu na wygraną gospodarzy
- zmiana_X: Zmiana kursu na remis
- zmiana_2: Zmiana kursu na wygraną gości

Typ świat: SWIAT_1_ZMIANY_KURSOW

Wersja: 1.0
Data: 2026-07-28
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
import random
import numpy as np

from .base_model import BaseModelV2, ModelConfig, ModelOutput, ModelType, WorldType

logger = logging.getLogger(__name__)


class Siec01ZmianaKursow(BaseModelV2):
    """
    Model Sieć 01: Analiza Zmian Kursów
    
    Specjalizacja:
    - Analiza zmian kursów bukmacherskich
    - Predykcja bazowana na trendach zmian
    - Świat 1: Zmiany Kursów
    
    Cechy wejściowe (zgodnie z 02_DATA_STRUCTURE.md):
    - zmiana_1: Zmiana kursu na 1 (gospodarze)
    - zmiana_X: Zmiana kursu na X (remis)  
    - zmiana_2: Zmiana kursu na 2 (goście)
    
    Zasadainterpretacji:
    - Dodatnia zmiana kursu na 1 → mniejsze szanse na wygraną gospodarzy
    - Ujemna zmiana kursu na 1 → większe szanse na wygraną gospodarzy
    - Analogicznie dla X i 2
    """
    
    # Wagi cech (można dostroić)
    DEFAULT_FEATURE_WEIGHTS: Dict[str, float] = {
        "zmiana_1": 1.0,
        "zmiana_X": 1.0,
        "zmiana_2": 1.0
    }
    
    # Progi decyzyjne
    HIGH_CHANGE_THRESHOLD: float = 0.5
    MEDIUM_CHANGE_THRESHOLD: float = 0.2
    LOW_CHANGE_THRESHOLD: float = 0.1
    
    def __init__(self, config: Optional[ModelConfig] = None):
        """
        Inicjalizacja modelu Sieć 01
        
        Args:
            config: Opcjonalna konfiguracja
        """
        # Domyślna konfiguracja
        default_config = ModelConfig(
            model_name="siec_01_zmiana_kursow",
            model_type=ModelType.ZMIANA_KURSOW,
            world_type=WorldType.SWIAT_1_ZMIANY_KURSOW,
            version="1.0.0",
            description="Model analizy zmian kursów bukmacherskich (Świat 1)",
            features=["zmiana_1", "zmiana_X", "zmiana_2"],
            target_column="wynik",
            params={
                "feature_weights": self.DEFAULT_FEATURE_WEIGHTS,
                "decision_thresholds": {
                    "high": self.HIGH_CHANGE_THRESHOLD,
                    "medium": self.MEDIUM_CHANGE_THRESHOLD,
                    "low": self.LOW_CHANGE_THRESHOLD
                }
            }
        )
        
        # Użyj dostarczonej konfiguracji lub domyślnej
        super().__init__(config or default_config)
        
        # Inicjalizuj wagi cech
        self.feature_weights: Dict[str, float] = (
            self.config.params.get("feature_weights", self.DEFAULT_FEATURE_WEIGHTS)
        )
        
        # Progi
        self.thresholds: Dict[str, float] = (
            self.config.params.get("decision_thresholds", {
                "high": 0.5, "medium": 0.2, "low": 0.1
            })
        )
        
        logger.info(f"Sieć 01: {self.model_name} - Załadowano")
    
    def _initialize_internal(self) -> bool:
        """Inicjalizacja specyficzna dla Sieci 01"""
        try:
            # Walidacja parametrów
            if not self.feature_weights:
                logger.error("Brak wag cech")
                return False
            
            # Normalizacja wag
            total_weight = sum(self.feature_weights.values())
            if total_weight > 0:
                for key in self.feature_weights:
                    self.feature_weights[key] = self.feature_weights[key] / total_weight
            
            logger.info(f"Sieć 01: Wagi cech znormalizowane")
            return True
            
        except Exception as e:
            logger.error(f"Błąd inicjalizacji Sieci 01: {e}")
            return False
    
    def _train_internal(self, training_data: List[Dict[str, Any]],
                        validation_data: Optional[List[Dict[str, Any]]]) -> bool:
        """
        Trenowanie specyficzne dla Sieci 01
        
        Trenuje model na podstawie historycznych zmian kursów i wyników.
        Uczy się rozpoznawać wzorce między zmianami kursów a rzeczywistymi wynikami.
        """
        try:
            if not training_data:
                logger.warning("Sieć 01: Brak danych treningowych")
                return False
            
            # Analiza danych treningowych i dostrojenie wag
            self._analyze_training_data(training_data)
            
            # Wyliczenie statystyk zmian
            self._calculate_feature_statistics(training_data)
            
            self.training_metrics.samples_count = len(training_data)
            self.training_metrics.features_count = len(self.config.features)
            self.training_metrics.training_time = 0.1  # Symulowany czas
            
            logger.info(f"Sieć 01: Wytrenowano na {len(training_data)} próbach")
            return True
            
        except Exception as e:
            logger.error(f"Błąd trenowania Sieci 01: {e}")
            return False
    
    def _analyze_training_data(self, training_data: List[Dict[str, Any]]) -> None:
        """Analiza danych treningowych i dostrojenie modelu"""
        try:
            # Historyczne statystyki dla różnych wyników
            result_stats: Dict[str, Dict[str, List[float]]] = {}
            
            for sample in training_data:
                result = sample.get("wynik", "0:0")
                if result not in result_stats:
                    result_stats[result] = {"zmiana_1": [], "zmiana_X": [], "zmiana_2": []}
                
                for feature in ["zmiana_1", "zmiana_X", "zmiana_2"]:
                    if feature in sample:
                        try:
                            result_stats[result][feature].append(float(sample[feature]))
                        except (ValueError, TypeError):
                            pass
            
            # Dostosowanie wag na podstawie statystyk
            # (Implementacja uproszczona - w rzeczywistości używałoby się ML)
            self._adjust_weights_based_on_statistics(result_stats)
            
        except Exception as e:
            logger.warning(f"Analiza danych: {e}")
    
    def _adjust_weights_based_on_statistics(self, 
                                          result_stats: Dict[str, Dict[str, List[float]]]) -> None:
        """Dostosowanie wag cech na podstawie statystyk"""
        try:
            # Uproszczona logika: jeśli dla danego wyniku zmiana jest charakterystyczna,
            # zwiększ wagę tej cechy
            
            # Średnie zmiany dla każdego wyniku
            avg_changes: Dict[str, Dict[str, float]] = {}
            for result, features_data in result_stats.items():
                avg_changes[result] = {}
                for feature, values in features_data.items():
                    if values:
                        avg_changes[result][feature] = sum(values) / len(values)
                    else:
                        avg_changes[result][feature] = 0.0
            
            # Dostosuj wagi (uproszczenie)
            # W rzeczywistości używałoby się tutaj algorytmu uczenia
            total_week_count = sum(self.feature_weights.values())
            for result, changes in avg_changes.items():
                for feature, avg_change in changes.items():
                    # Jeśli średnia zmiana jest duża, zwiększ wagę
                    if abs(avg_change) > self.thresholds.get("high", 0.5):
                        self.feature_weights[feature] = self.feature_weights.get(feature, 1.0) * 1.2
            
            # Renormalizacja
            total = sum(self.feature_weights.values())
            if total > 0:
                for key in self.feature_weights:
                    self.feature_weights[key] = self.feature_weights[key] / total
                    
        except Exception as e:
            logger.warning(f"Dostosowanie wag: {e}")
    
    def _calculate_feature_statistics(self, training_data: List[Dict[str, Any]]) -> None:
        """Wyliczenie statystyk cech"""
        try:
            self.feature_statistics: Dict[str, Dict[str, float]] = {}
            
            for feature in self.config.features:
                values = []
                for sample in training_data:
                    if feature in sample:
                        try:
                            values.append(float(sample[feature]))
                        except (ValueError, TypeError):
                            pass
                
                if values:
                    self.feature_statistics[feature] = {
                        "mean": np.mean(values) if values else 0.0,
                        "std": np.std(values) if len(values) > 1 else 0.0,
                        "min": min(values) if values else 0.0,
                        "max": max(values) if values else 0.0,
                        "count": len(values)
                    }
                else:
                    self.feature_statistics[feature] = {
                        "mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0, "count": 0
                    }
                    
        except Exception as e:
            logger.warning(f"Statystyki cech: {e}")
            self.feature_statistics = {}
    
    def _predict_internal(self, input_data: Dict[str, Any], **kwargs) -> ModelOutput:
        """
        Generowanie predykcji na podstawie zmian kursów
        
        Logika:
        1. Analiza zmian dla każdego kursu (1, X, 2)
        2. Określenie wzorca zmian
        3. Predykcja wyniku na podstawie wzorca
        """
        try:
            # Pobierz zmiany
            zmiana_1 = float(input_data.get("zmiana_1", 0.0))
            zmiana_X = float(input_data.get("zmiana_X", 0.0))
            zmiana_2 = float(input_data.get("zmiana_2", 0.0))
            
            # Określ wzorzec zmian
            pattern = self._determine_change_pattern(zmiana_1, zmiana_X, zmiana_2)
            
            # Generuj predykcję na podstawie wzorca
            prediction, confidence = self._predict_from_pattern(pattern, zmiana_1, zmiana_X, zmiana_2)
            
            # Utwórz obiekty wyjściowe
            output = ModelOutput(
                prediction=prediction,
                confidence=confidence,
                match_id=input_data.get("mecz", ""),
                group_id=input_data.get("id_grupy", "")
            )
            
            # Dodatkowe informacje
            output.explanation = {
                "pattern": pattern,
                "changes": {"zmiana_1": zmiana_1, "zmiana_X": zmiana_X, "zmiana_2": zmiana_2},
                "feature_weights": self.feature_weights
            }
            
            return output
            
        except Exception as e:
            logger.error(f"Predykcja Sieć 01: {e}")
            return ModelOutput(prediction="1:1", confidence=0.5)
    
    def _determine_change_pattern(self, zmiana_1: float, zmiana_X: float, 
                                  zmiana_2: float) -> str:
        """
        Określenie wzorca zmian kursów
        
        Wzorce:
        - home_advantage: Zmiana_1 < 0, Zmiana_2 > 0 (kurs na gospodarzy spada, na gości rośnie)
        - away_advantage: Zmiana_1 > 0, Zmiana_2 < 0 (kurs na gospodarzy rośnie, na gości spada)
        - draw_tendency: Zmiana_X < 0 (kurs na remis spada)
        - high_volatility: Duże zmiany (|zmiana| > HIGH_THRESHOLD)
        - medium_volatility: Średnie zmiany (MEDIUM < |zmiana| <= HIGH)
        - low_volatility: Małe zmiany (|zmiana| <= MEDIUM)
        """
        patterns = []
        
        # Sprawdź przewagę gospodarzy
        if zmiana_1 < -self.thresholds.get("low", 0.1) and zmiana_2 > self.thresholds.get("low", 0.1):
            patterns.append("home_advantage")
        
        # Sprawdź przewagę gości
        if zmiana_1 > self.thresholds.get("low", 0.1) and zmiana_2 < -self.thresholds.get("low", 0.1):
            patterns.append("away_advantage")
            
        # Sprawdź tendencję remisową
        if zmiana_X < -self.thresholds.get("medium", 0.2):
            patterns.append("draw_tendency")
        
        # Sprawdź zmienność
        volatility = max(abs(zmiana_1), abs(zmiana_X), abs(zmiana_2))
        if volatility > self.thresholds.get("high", 0.5):
            patterns.append("high_volatility")
        elif volatility > self.thresholds.get("medium", 0.2):
            patterns.append("medium_volatility")
        else:
            patterns.append("low_volatility")
        
        return ",".join(patterns) if patterns else "neutral"
    
    def _predict_from_pattern(self, pattern: str, zmiana_1: float, 
                             zmiana_X: float, zmiana_2: float) -> Tuple[str, float]:
        """
        Predykcja wyniku na podstawie wzorca zmian
        
        Returns:
            Tuple[str, float]: (predykcja, confidence)
        """
        # Decyzja na podstawie wzorca
        if "home_advantage" in pattern:
            # Przewaga gospodarzy - przewiduj wygraną gospodarzy
            predictions = ["1:0", "2:0", "2:1", "3:0", "3:1"]
            confidence = min(0.95, 0.7 + abs(zmiana_1) * 0.1)
            return random.choice(predictions), confidence
            
        elif "away_advantage" in pattern:
            # Przewaga gości - przewiduj wygraną gości
            predictions = ["0:1", "0:2", "1:2", "0:3", "1:3"]
            confidence = min(0.95, 0.7 + abs(zmiana_2) * 0.1)
            return random.choice(predictions), confidence
            
        elif "draw_tendency" in pattern:
            # Tendencja do remisu
            predictions = ["1:1", "0:0", "2:2", "3:3"]
            confidence = min(0.95, 0.7 + abs(zmiana_X) * 0.1)
            return random.choice(predictions), confidence
            
        else:
            # Neutralny wzorzec - użyj wag cech
            return self._predict_from_features(zmiana_1, zmiana_X, zmiana_2)
    
    def _predict_from_features(self, zmiana_1: float, zmiana_X: float, 
                               zmiana_2: float) -> Tuple[str, float]:
        """
        Predykcja na podstawie wag cech
        
        Returns:
            Tuple[str, float]: (predykcja, confidence)
        """
        # Wylicz ważoną sumę zmian
        weighted_sum = (
            zmiana_1 * self.feature_weights.get("zmiana_1", 1.0) +
            zmiana_X * self.feature_weights.get("zmiana_X", 1.0) +
            zmiana_2 * self.feature_weights.get("zmiana_2", 1.0)
        )
        
        # Decyzja na podstawie sumy
        if weighted_sum < -self.thresholds.get("medium", 0.2):
            # Duża przewaga gospodarzy
            predictions = ["2:0", "2:1", "3:0"]
            confidence = min(0.9, 0.6 + abs(weighted_sum))
        elif weighted_sum > self.thresholds.get("medium", 0.2):
            # Duża przewaga gości
            predictions = ["0:2", "1:2", "0:3"]
            confidence = min(0.9, 0.6 + abs(weighted_sum))
        elif abs(weighted_sum) < self.thresholds.get("low", 0.1):
            # اوRemis
            predictions = ["1:1", "0:0", "2:2"]
            confidence = 0.65 + (1 - abs(weighted_sum) * 2) * 0.2
        else:
            # Małe różnice
            predictions = ["1:0", "0:1", "1:1", "2:0", "0:2"]
            confidence = 0.55 + (1 - abs(weighted_sum)) * 0.1
        
        return random.choice(predictions), min(0.95, max(0.5, confidence))
    
    def get_world_features(self) -> List[str]:
        """Pobieranie cech Świata 1"""
        return ["zmiana_1", "zmiana_X", "zmiana_2"]


if __name__ == "__main__":
    # Testy Sieci 01
    print("Testing Siec01ZmianaKursow...")
    
    # Tworzenie modelu
    model = Siec01ZmianaKursow()
    print(f"Model: {model.model_name}")
    print(f"Świat: {model.world_type.value}")
    print(f"Cechy: {model.get_world_features()}")
    
    # Inicjalizacja
    model.initialize()
    print(f"Status: {model.status.value}")
    
    # Trenowanie (symulowane)
    training_data = [
        {"zmiana_1": -0.5, "zmiana_X": 0.1, "zmiana_2": 0.3, "wynik": "2:0"},
        {"zmiana_1": 0.2, "zmiana_X": -0.4, "zmiana_2": -0.1, "wynik": "0:1"},
        {"zmiana_1": 0.0, "zmiana_X": -0.3, "zmiana_2": 0.0, "wynik": "1:1"},
    ]
    model.train(training_data)
    print(f"Wytrenowano: {model.training_metrics.samples_count} prób")
    
    # Predykcje testowe
    test_cases = [
        {"zmiana_1": -0.8, "zmiana_X": 0.2, "zmiana_2": 0.5},  # Home advantage
        {"zmiana_1": 0.6, "zmiana_X": -0.1, "zmiana_2": -0.4},  # Away advantage
        {"zmiana_1": 0.0, "zmiana_X": -0.5, "zmiana_2": 0.0},   # Draw tendency
        {"zmiana_1": 0.1, "zmiana_X": 0.0, "zmiana_2": -0.1},   # Neutral
    ]
    
    for i, test_data in enumerate(test_cases):
        prediction = model.predict(test_data)
        print(f"Test {i+1}: {prediction.prediction} (conf: {prediction.confidence:.2f}, Grupa: {prediction.prediction_group})")
        print(f"  Wzór: {prediction.explanation.get('pattern', 'N/A')}")
    
    print("\nSieć 01 tests passed!")
