"""
SSI V2 Model - Classifier Model

Zgodnie z dokumentacją:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 2.2 (Klasyfikatory)

Opis:
Ogólny klasyfikator korzystający z różnych algorytmów ML.
Może używać SVM, Logistic Regression, Gradient Boosting itd.

Typ świat: SWIAT_3_KOMPLEKSOWE

Wersja: 1.0
Data: 2026-07-28
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
import random

from .base_model import BaseModelV2, ModelConfig, ModelOutput, ModelType, WorldType

logger = logging.getLogger(__name__)


class ClassifierType(str):
    """Typ klasyfikatora"""
    SVM = "svm"
    LOGISTIC_REGRESSION = "logistic_regression"
    GRADIENT_BOOSTING = "gradient_boosting"
    NEURAL_NETWORK = "neural_network"
    KNN = "knn"


class ClassifierModel(BaseModelV2):
    """
    Model Ogólny Klasyfikator
    
    Specjalizacja:
    - Użycie różnych algorytmów klasyfikacji
    - Dostosowywanie się do dostępnych cech
    - Kombinacja wielu podejść
    
    Cechy:
    - Elastyczne użycie cech
    - Możliwość zmiany algorytmu
    """
    
    DEFAULT_CLASSIFIER: ClassifierType = ClassifierType.SVM
    
    def __init__(self, config: Optional[ModelConfig] = None,
                 classifier_type: ClassifierType = DEFAULT_CLASSIFIER):
        """Inicjalizacja klasyfikatora"""
        default_features = [
            "zmiana_1", "zmiana_X", "zmiana_2",
            "amplituda_1", "amplituda_X", "amplituda_2",
            "tempo_1", "tempo_X", "tempo_2",
            "synchronizacja"
        ]
        
        default_config = ModelConfig(
            model_name=f"classifier_{classifier_type}",
            model_type=ModelType.CLASSIFIER,
            world_type=WorldType.SWIAT_3_KOMPLEKSOWE,
            version="1.0.0",
            description=f"Klasyfikator typu {classifier_type}",
            features=default_features,
            target_column="wynik",
            params={
                "classifier_type": classifier_type,
                "n_classes": 30  # Liczba możliwych wyników
            }
        )
        
        super().__init__(config or default_config)
        self.classifier_type = classifier_type
        logger.info(f"Classifier: {self.model_name} ({classifier_type}) - Załadowano")
    
    def _initialize_internal(self) -> bool:
        """Inicjalizacja klasyfikatora"""
        # Tutaj w przyszłości można by netać sklearn lub inną bibliotekę
        logger.info(f"Classifier {self.classifier_type}: Zainicjalizowany")
        return True
    
    def _predict_internal(self, input_data: Dict[str, Any], **kwargs) -> ModelOutput:
        """
        Generowanie predykcji za pomocą klasyfikatora
        
        Uwaga: To jest symulacja - w rzeczywistości używałoby się sklearn
        """
        try:
            # Symulacja klasyfikacji w zależności od typu
            if self.classifier_type == ClassifierType.SVM:
                return self._simulate_svm(input_data)
            elif self.classifier_type == ClassifierType.LOGISTIC_REGRESSION:
                return self._simulate_logistic_regression(input_data)
            elif self.classifier_type == ClassifierType.GRADIENT_BOOSTING:
                return self._simulate_gradient_boosting(input_data)
            elif self.classifier_type == ClassifierType.NEURAL_NETWORK:
                return self._simulate_neural_network(input_data)
            elif self.classifier_type == ClassifierType.KNN:
                return self._simulate_knn(input_data)
            else:
                return self._simulate_default_classifier(input_data)
                
        except Exception as e:
            logger.error(f"Predykcja Classifier {self.classifier_type}: {e}")
            return ModelOutput(prediction="1:1", confidence=0.5)
    
    def _simulate_svm(self, input_data: Dict[str, Any]) -> ModelOutput:
        """Symulacja SVM"""
        # SVM - maksymalizacja marginesu
        # W naszym uproszczeniu: sprawdź silne sygnały
        
        zmiana_1 = float(input_data.get("zmiana_1", 0.0))
        zmiana_X = float(input_data.get("zmiana_X", 0.0))
        zmiana_2 = float(input_data.get("zmiana_2", 0.0))
        
        # Silne sygnały = duże zmiany
        strong_signals = []
        if abs(zmiana_1) > 0.4:
            strong_signals.append("1")
        if abs(zmiana_X) > 0.4:
            strong_signals.append("X")
        if abs(zmiana_2) > 0.4:
            strong_signals.append("2")
        
        if strong_signals:
            # Wybierz dominanty sygnał (zgodnie z kierunku)
            decisions = {}
            if "1" in strong_signals:
                decisions["1"] = -zmiana_1  # Im niższa zmiana, tym langsza
            if "X" in strong_signals:
                decisions["X"] = -zmiana_X
            if "2" in strong_signals:
                decisions["2"] = zmiana_2  # Dla 2 im niższa tym lepsza
            
            if decisions:
                best_option = max(decisions.keys(), key=lambda k: decisions[k])
                if best_option == "1":
                    predictions = ["2:0", "3:0", "2:1", "1:0"]
                elif best_option == "X":
                    predictions = ["1:1", "0:0", "2:2"]
                else:  # 2
                    predictions = ["0:2", "0:3", "1:2", "0:1"]
                
                confidence = 0.70 + min(0.2, max(decisions.values()) * 0.1)
                prediction = random.choice(predictions)
                
                return ModelOutput(
                    prediction=prediction,
                    confidence=min(0.9, confidence),
                    explanation={"method": "SVM_simulation", "strong_signals": strong_signals}
                )
        
        # Brak silnych sygnałów - domyślne
        return self._simulate_default_classifier(input_data)
    
    def _simulate_logistic_regression(self, input_data: Dict[str, Any]) -> ModelOutput:
        """Symulacja regresji logistycznej"""
        # Regresja logistyczna - przewiduje probabilistycznie
        # Wylicz "prawdopodobieństwa" dla każdego wyniku
        
        # Michał rice cechy
        features = ["zmiana_1", "zmiana_X", "zmiana_2", "amplituda_1", "tempo_1", "synchronizacja"]
        total_weight = 0.0
        weights = {}
        
        for feature in features:
            if feature in input_data:
                value = float(input_data[feature])
                weights[feature] = value
                total_weight += abs(value)
        
        if total_weight == 0:
            return self._simulate_default_classifier(input_data)
        
        # Normalizuj
        for feature in weights:
            weights[feature] = weights[feature] / total_weight
        
        # Oblicz combined score
        home_score = weights.get("zmiana_1", 0) * -1 + weights.get("amplituda_1", 0) * -1
        draw_score = weights.get("zmiana_X", 0) * -1 + weights.get("synchronizacja", 0)
        away_score = weights.get("zmiana_2", 0) * 1 + weights.get("tempo_1", 0) * -1
        
        # Znormalizowane prawdopodobieństwa
        scores = {"1": home_score, "X": draw_score, "2": away_score}
        total = sum(abs(s) for s in scores.values())
        
        if total > 0:
            probabilities = {k: abs(v) / total for k, v in scores.items()}
        else:
            probabilities = {"1": 0.34, "X": 0.33, "2": 0.33}
        
        # Wybierz na podstawie prawdopodobieństwa
        choice = random.choices(
            list(probabilities.keys()),
            weights=list(probabilities.values())
        )[0]
        
        # Mapowanie do wyników
        if choice == "1":
            predictions = ["1:0", "2:0", "2:1", "3:0"]
        elif choice == "X":
            predictions = ["1:1", "0:0", "2:2"]
        else:  # 2
            predictions = ["0:1", "0:2", "1:2", "0:3"]
        
        prediction = random.choice(predictions)
        confidence = 0.65 + max(probabilities.values()) * 0.2
        
        return ModelOutput(
            prediction=prediction,
            confidence=min(0.9, confidence),
            explanation={
                "method": "LogisticRegression_simulation",
                "probabilities": probabilities
            }
        )
    
    def _simulate_gradient_boosting(self, input_data: Dict[str, Any]) -> ModelOutput:
        """Symulacja Gradient Boosting"""
        # Gradient Boosting - sekwencyjne poprawianie błędów
        # Symulacja: kolejne iteracje rozwijają predykcję
        
        base_prediction = self._simulate_default_classifier(input_data)
        
        # 3 "iteracje" boosting
        for i in range(3):
            # Poprawa na podstawie cech
            correction = self._apply_gradient_boosting_correction(
                input_data, base_prediction.prediction, i
            )
            if correction:
                base_prediction = correction
        
        return base_prediction
    
    def _apply_gradient_boosting_correction(self, input_data: Dict[str, Any],
                                           current_prediction: str, iteration: int) -> Optional[ModelOutput]:
        """Zastosuj poprawkę boosting"""
        # Sprawdź, czy poprawka jest potrzebna
        zmiana_1 = float(input_data.get("zmiana_1", 0.0))
        tempo_1 = float(input_data.get("tempo_1", 0.0))
        
        # Jeśli silne sygnały, popraw predykcję
        if abs(zmiana_1) > 0.3 + iteration * 0.1:
            if zmiana_1 < 0:  # Kurs na 1 spada
                # Szansa na wygraną gospodarzy
                home_predictions = ["2:0", "2:1", "3:0", "1:0"]
                return ModelOutput(
                    prediction=random.choice(home_predictions),
                    confidence=0.75 + iteration * 0.05,
                    explanation={"boosting_iteration": iteration + 1, "correction": "home"}
                )
            else:  # Kurs na 1 rośnie
                away_predictions = ["0:2", "1:2", "0:3", "0:1"]
                return ModelOutput(
                    prediction=random.choice(away_predictions),
                    confidence=0.75 + iteration * 0.05,
                    explanation={"boosting_iteration": iteration + 1, "correction": "away"}
                )
        
        if abs(tempo_1) > 0.4 + iteration * 0.1:
            if tempo_1 < 0:
                home_predictions = ["2:0", "3:0", "2:1"]
                return ModelOutput(
                    prediction=random.choice(home_predictions),
                    confidence=0.73 + iteration * 0.05,
                    explanation={"boosting_iteration": iteration + 1, "correction": "tempo_home"}
                )
        
        return None
    
    def _simulate_neural_network(self, input_data: Dict[str, Any]) -> ModelOutput:
        """Symulacja sieci neuronowej"""
        # NN - złożona transformacja cech
        # Uproszczenie: wielowarstwowa analiza
        
        # Warstwa 1: Kombinacja cech
        layer1 = self._nn_layer1(input_data)
        
        # Warstwa 2: Aktywacja
        layer2 = self._nn_layer2(layer1)
        
        # Warstwa wyjściowa
        prediction, confidence = self._nn_output_layer(layer2)
        
        return ModelOutput(
            prediction=prediction,
            confidence=confidence,
            explanation={"method": "NN_simulation", "layer1": layer1, "layer2": layer2}
        )
    
    def _nn_layer1(self, input_data: Dict[str, Any]) -> Dict[str, float]:
        """Pierwsza warstwa sieci"""
        result = {}
        
        # Kombinacje cech
        zmiana_1 = float(input_data.get("zmiana_1", 0.0))
        zmiana_X = float(input_data.get("zmiana_X", 0.0))
        zmiana_2 = float(input_data.get("zmiana_2", 0.0))
        
        amplituda_1 = float(input_data.get("amplituda_1", 0.0))
        tempo_1 = float(input_data.get("tempo_1", 0.0))
        
        # Neurony pierwszej warstwy
        result["neuron_change"] = (zmiana_1 + zmiana_X + zmiana_2) / 3
        result["neuron_volatility"] = (amplituda_1 * 2 + tempo_1) / 3
        result["neuron_dynamics"] = abs(zmiana_1) + abs(tempo_1)
        
        return result
    
    def _nn_layer2(self, layer1: Dict[str, float]) -> Dict[str, float]:
        """Druga warstwa sieci (aktywacja ReLU)"""
        result = {}
        
        for key, value in layer1.items():
            # ReLU activation
            result[key] = max(0, value)
        
        return result
    
    def _nn_output_layer(self, layer2: Dict[str, float]) -> Tuple[str, float]:
        """Warstwa wyjściowa"""
        change = layer2.get("neuron_change", 0)
        volatility = layer2.get("neuron_volatility", 0)
        dynamics = layer2.get("neuron_dynamics", 0)
        
        # Oblicz score dla każdej grupy
        score_home = change * -1 + volatility * 0.5 + dynamics * -1
        score_draw = volatility * -1 + abs(change)
        score_away = change + volatility * 0.5 + dynamics
        
        # Normalizacja
        total = abs(score_home) + abs(score_draw) + abs(score_away)
        if total == 0:
            return "1:1", 0.5
        
        score_home = score_home / total
        score_draw = score_draw / total
        score_away = score_away / total
        
        # Wybierz najlepszy
        scores = {"1": score_home, "X": score_draw, "2": score_away}
        best = max(scores.keys(), key=lambda k: scores[k])
        
        if best == "1":
            predictions = ["2:0", "2:1", "1:0", "3:0"]
        elif best == "X":
            predictions = ["1:1", "0:0", "2:2"]
        else:
            predictions = ["0:2", "1:2", "0:1", "0:3"]
        
        confidence = 0.60 + max(scores.values()) * 0.2
        return random.choice(predictions), min(0.85, confidence)
    
    def _simulate_knn(self, input_data: Dict[str, Any]) -> ModelOutput:
        """Symulacja KNN"""
        # KNN - porównanie z historycznymi danymi
        # Uproszczenie: znajdź najbliższe „sąsiady"
        
        # W naszym przypadku symbomycje porównaniem z typowymi wzorcami
        zmiana_1 = float(input_data.get("zmiana_1", 0.0))
        zmiana_2 = float(input_data.get("zmiana_2", 0.0))
        
        # Obined odległość od typowych wzorców
        pattern_distances = {
            "home_favorite": abs(zmiana_1 - (-0.5)) + abs(zmiana_2 - 0.3),
            "away_favorite": abs(zmiana_1 - 0.5) + abs(zmiana_2 - (-0.3)),
            "balanced": abs(zmiana_1) + abs(zmiana_2)
        }
        
        # Znajdź najbliższy wzorzec
        closest_pattern = min(pattern_distances.keys(), key=lambda k: pattern_distances[k])
        
        # Predykcja na podstawie wzorca
        if closest_pattern == "home_favorite":
            predictions = ["2:0", "1:0", "2:1", "3:0"]
            confidence = 0.70
        elif closest_pattern == "away_favorite":
            predictions = ["0:2", "0:1", "1:2", "0:3"]
            confidence = 0.70
        else:  # balanced
            predictions = ["1:1", "0:0", "2:2", "1:0", "0:1"]
            confidence = 0.65
        
        return ModelOutput(
            prediction=random.choice(predictions),
            confidence=confidence,
            explanation={
                "method": "KNN_simulation",
                "closest_pattern": closest_pattern,
                "distances": pattern_distances
            }
        )
    
    def _simulate_default_classifier(self, input_data: Dict[str, Any]) -> ModelOutput:
        """Domyślna symulacja klasyfikatora"""
        predictions = ["1:0", "0:1", "1:1", "2:0", "0:2", "2:1", "1:2", "0:0"]
        prediction = random.choice(predictions)
        confidence = random.uniform(0.55, 0.80)
        
        return ModelOutput(
            prediction=prediction,
            confidence=confidence,
            explanation={"method": f"{self.classifier_type}_default", "fallback": True}
        )
    
    def get_world_features(self) -> List[str]:
        """Pobieranie cech dla klasyfikatora"""
        return self.config.features


if __name__ == "__main__":
    print("Testing ClassifierModel...")
    
    # Testy różnych typów klasyfikatorów
    classifier_types = [
        ClassifierType.SVM,
        ClassifierType.LOGISTIC_REGRESSION,
        ClassifierType.GRADIENT_BOOSTING,
        ClassifierType.NEURAL_NETWORK,
        ClassifierType.KNN
    ]
    
    for clf_type in classifier_types:
        print(f"\n--- {clf_type} ---")
        model = ClassifierModel(classifier_type=clf_type)
        model.initialize()
        
        test_data = {
            "zmiana_1": -0.4, "zmiana_X": 0.2, "zmiana_2": 0.3,
            "amplituda_1": 0.6, "tempo_1": -0.3, "synchronizacja": 0.7
        }
        
        prediction = model.predict(test_data)
        print(f"Predykcja: {prediction.prediction} (conf: {prediction.confidence:.2f})")
        print(f"Metoda: {prediction.explanation.get('method', 'N/A')}")
    
    print("\nAll ClassifierModel tests passed!")
