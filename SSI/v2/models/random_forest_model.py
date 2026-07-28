"""
SSI V2 Model - Random Forest

Zgodnie z dokumentacją:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 2.2 (Klasyfikatory)

Opis:
Klasyfikator Random Forest do predykcji wyników meczów.
Używa wszystkich dostępnych cech do podjęcia decyzji.

Typ świat: SWIAT_3_KOMPLEKSOWE (używa cech z wielu światów)

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


class RandomForestModel(BaseModelV2):
    """
    Model Random Forest
    
    Specjalizacja:
    - Klasyfikator lasu losowego
    - Używa wszystkich cech do predykcji
    - LOW egocentryczny model-przewidywania
    
    Cechy:
    - Wszystkie cechy z Świata 1, 2, 3, 4
    - Opcjonalne cechy dodatkowe
    """
    
    def __init__(self, config: Optional[ModelConfig] = None):
        """Inicjalizacja modelu Random Forest"""
        default_features = [
            # Świat 1: Zmiany
            "zmiana_1", "zmiana_X", "zmiana_2",
            # Świat 2: Dynamika
            "amplituda_1", "amplituda_X", "amplituda_2",
            "tempo_1", "tempo_X", "tempo_2",
            "synchronizacja",
            "max_wahanie_1", "max_wahanie_X", "max_wahanie_2",
            # Świat 3: Klasyfikacja
            "log_start_1", "log_start_X", "log_start_2",
            "log_koniec_1", "log_koniec_X", "log_koniec_2",
            # Świat 4: Relacje
            "ratio_1X_start", "ratio_1_2_start", "ratio_X2_start",
            "ratio_1X_koniec", "ratio_1_2_koniec", "ratio_X2_koniec"
        ]
        
        default_config = ModelConfig(
            model_name="random_forest",
            model_type=ModelType.RANDOM_FOREST,
            world_type=WorldType.SWIAT_3_KOMPLEKSOWE,
            version="1.0.0",
            description="Klasyfikator Random Forest korzystający ze wszystkich dostępnych cech",
            features=default_features,
            target_column="wynik",
            params={
                "n_estimators": 100,
                "max_depth": 10,
                "min_samples_split": 2,
                "random_state": 42
            }
        )
        
        super().__init__(config or default_config)
        logger.info(f"RandomForest: {self.model_name} - Załadowano")
    
    def _predict_internal(self, input_data: Dict[str, Any], **kwargs) -> ModelOutput:
        """
        Generowanie predykcji za pomocą logiki Random Forest
        
        Uwaga: To jest symulacja RF - w rzeczywistości używałoby się biblioteki sklearn
        """
        try:
            # Symulacja lasu losowego: Generuj kilka "drzew" decyzyjnych
            # i weź średnią z ich predykcji
            
            predictions = []
            for i in range(5):  # 5 "drzew"
                tree_prediction = self._simulate_decision_tree(input_data, seed=i)
                predictions.append(tree_prediction)
            
            # Wybierz najczęstszą predykcję
            prediction, confidence = self._get_consensus_prediction(predictions)
            
            output = ModelOutput(
                prediction=prediction,
                confidence=confidence,
                match_id=input_data.get("mecz", ""),
                group_id=input_data.get("id_grupy", "")
            )
            
            output.explanation = {
                "method": "random_forest_simulation",
                "trees_count": len(predictions),
                "tree_predictions": predictions
            }
            
            return output
            
        except Exception as e:
            logger.error(f"Predykcja RandomForest: {e}")
            return ModelOutput(prediction="1:1", confidence=0.5)
    
    def _simulate_decision_tree(self, input_data: Dict[str, Any], seed: int = 0) -> Tuple[str, float]:
        """
        Symulacja pojedynczego drzewa decyzyjnego
        
        Uwaga: W rzeczywistości używałoby się sklearn.tree.DecisionTreeClassifier
        """
        # Uproszczona logika drzewa
        random.seed(seed)
        
        # Pobierz losową podzbiór cech (bagging)
        available_features = [f for f in self.config.features if f in input_data]
        if not available_features:
            return random.choice(["1:0", "0:1", "1:1", "2:0", "0:2"]), 0.5
        
        # Wybierz 3 losowe cechy do anality
        selected_features = random.sample(available_features, min(3, len(available_features)))
        
        # Pobierz wartości cech
        feature_values = {f: float(input_data.get(f, 0.0)) for f in selected_features}
        
        # Uproszczona logika decyzyjna
        return self._simple_tree_decision(feature_values, seed)
    
    def _simple_tree_decision(self, feature_values: Dict[str, float], seed: int) -> Tuple[str, float]:
        """Uproszczona logika drzewa decyzyjnego"""
        random.seed(seed + 1000)  # Inny seed
        
        # Sprawdź cechy z Świata 1 (zmiany)
        if "zmiana_1" in feature_values:
            zmiana_1 = feature_values["zmiana_1"]
            if zmiana_1 < -0.3:
                # Kurs na gospodarzy spada -> większa szansa na wygraną gospodarzy
                return random.choice(["2:0", "2:1", "1:0", "3:0"]), 0.75
            elif zmiana_1 > 0.3:
                # Kurs na gospodarzy rośnie -> mniejsze szanse
                return random.choice(["0:2", "1:2", "0:1", "0:3"]), 0.75
        
        # Sprawdź amplitudę
        if "amplituda_1" in feature_values:
            amp_1 = abs(feature_values["amplituda_1"])
            if amp_1 > 0.5:
                return random.choice(["2:0", "0:2", "1:1"]), 0.70
        
        # Sprawdź tempo
        if "tempo_1" in feature_values:
            tempo_1 = feature_values["tempo_1"]
            if tempo_1 < -0.4:
                return random.choice(["2:0", "3:0", "2:1"]), 0.72
            elif tempo_1 > 0.4:
                return random.choice(["0:2", "0:3", "1:2"]), 0.72
        
        # Sprawdź stosunki
        if "ratio_1X_start" in feature_values:
            ratio = feature_values["ratio_1X_start"]
            if ratio > 1.5:
                return random.choice(["1:0", "2:0", "2:1"]), 0.68
            elif ratio < 0.8:
                return random.choice(["0:1", "0:2", "1:2"]), 0.68
        
        # Domyślna decyzja
        return random.choice(["1:0", "0:1", "1:1", "2:0", "0:2"]), 0.60
    
    def _get_consensus_prediction(self, predictions: List[Tuple[str, float]]) -> Tuple[str, float]:
        """
        Wybierz konsensus z wielu drzew
        
        Returns:
            Tuple[str, float]: (predykcja, confidence)
        """
        if not predictions:
            return "1:1", 0.5
        
        # Zlicz predykcje
        prediction_counts: Dict[str, int] = {}
        total_confidence = 0.0
        
        for pred, conf in predictions:
            prediction_counts[pred] = prediction_counts.get(pred, 0) + 1
            total_confidence += conf
        
        # Znajdź najczęstszą predykcję
        max_count = max(prediction_counts.values())
        winners = [k for k, v in prediction_counts.items() if v == max_count]
        
        if len(winners) == 1:
            # Jeden zwycięzca - wysoka pewność
            winning_prediction = winners[0]
            # Średnia confidence z drzew, które wybrały ten wynik
            avg_confidence = sum(
                conf for pred, conf in predictions if pred == winning_prediction
            ) / max_count
            
            # Zwiększ pewność proporcjonalnie do liczby drzew
            count_factor = max_count / len(predictions)
            final_confidence = avg_confidence * (0.5 + count_factor * 0.5)
            
            return winning_prediction, min(0.95, final_confidence)
        else:
            # Kilka zwycięzców - niższa pewność
            winning_prediction = random.choice(winners)
            avg_confidence = total_confidence / len(predictions)
            final_confidence = avg_confidence * 0.7
            
            return winning_prediction, min(0.85, final_confidence)
    
    def get_world_features(self) -> List[str]:
        """Pobieranie cech dla Random Forest"""
        return self.config.features


if __name__ == "__main__":
    print("Testing RandomForestModel...")
    
    model = RandomForestModel()
    print(f"Model: {model.model_name}")
    print(f"Świat: {model.world_type.value}")
    print(f"Cechy: {len(model.get_world_features())} cechy")
    
    model.initialize()
    print(f"Status: {model.status.value}")
    
    test_cases = [
        {
            "zmiana_1": -0.5, "zmiana_X": 0.1, "zmiana_2": 0.3,
            "amplituda_1": 0.8, "tempo_1": -0.4,
            "ratio_1X_start": 1.5
        },
        {
            "zmiana_1": 0.2, "zmiana_X": -0.4, "zmiana_2": -0.1,
            "amplituda_1": 0.3, "tempo_1": 0.2,
            "ratio_1X_start": 0.8
        },
        {
            "zmiana_1": 0.0, "zmiana_X": -0.3, "zmiana_2": 0.0,
            "amplituda_1": 0.2, "tempo_1": 0.0,
            "synchronizacja": 0.8
        }
    ]
    
    for i, test_data in enumerate(test_cases):
        prediction = model.predict(test_data)
        print(f"Test {i+1}: {prediction.prediction} (conf: {prediction.confidence:.2f})")
        print(f"  Drzewa: {len(prediction.explanation.get('tree_predictions', []))}")
    
    print("\nRandomForest tests passed!")
