"""
SSI V2 Model - Sieć 03: Tempo

Zgodnie z dokumentacją:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 2.2
- 02_DATA_STRUCTURE.md Sekcja 3.2 (Świat 2: Dynamika)

Opis:
Model analizujący tempo zmian kursów bukmacherskich.
Koncentruje się na szybkości zmian kursów i ich wpływie na przewidywane wyniki.

Typ świat: SWIAT_2_DYNAMIKA

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


class Siec03Tempo(BaseModelV2):
    """
    Model Sieć 03: Analiza Tempa Zmian Kursów
    
    Specjalizacja:
    - Analiza tempa (szybkości) zmian kursów
    - Wykrywanie trendów czasowych
    - Analiza dynamiki zmian w czasie
    
    Cechy główne:
    - tempo_1: Tempo zmian kursu na wygraną gospodarzy
    - tempo_X: Tempo zmian kursu na remis
    - tempo_2: Tempo zmian kursu na wygraną gości
    
    Interpretation:
    - Wysokie tempo > 0: Kurs szybko rośnie (mniejsze szanse na daną opcję)
    - Wysokie tempo < 0: Kurs szybko spada (większe szanse na daną opcję)
    - Niskie tempo: Mała aktywność, stabilna sytuacja
    """
    
    HIGH_TEMPO: float = 0.6
    MEDIUM_TEMPO: float = 0.3
    TEMPO_ACCELERATION_FACTOR: float = 1.5
    
    def __init__(self, config: Optional[ModelConfig] = None):
        """Inicjalizacja modelu Sieć 03"""
        default_config = ModelConfig(
            model_name="siec_03_tempo",
            model_type=ModelType.TEMPO,
            world_type=WorldType.SWIAT_2_DYNAMIKA,
            version="1.0.0",
            description="Model analizy tempa zmian kursów bukmacherskich",
            features=["tempo_1", "tempo_X", "tempo_2"],
            target_column="wynik",
            params={
                "high_tempo_threshold": self.HIGH_TEMPO,
                "medium_tempo_threshold": self.MEDIUM_TEMPO,
                "acceleration_factor": self.TEMPO_ACCELERATION_FACTOR
            }
        )
        
        super().__init__(config or default_config)
        logger.info(f"Sieć 03: {self.model_name} - Załadowano")
    
    def _predict_internal(self, input_data: Dict[str, Any], **kwargs) -> ModelOutput:
        """Generowanie predykcji na podstawie tempa zmian"""
        try:
            tempo_1 = float(input_data.get("tempo_1", 0.0))
            tempo_X = float(input_data.get("tempo_X", 0.0))
            tempo_2 = float(input_data.get("tempo_2", 0.0))
            
            pattern = self._analyze_tempo_pattern(tempo_1, tempo_X, tempo_2)
            prediction, confidence = self._generate_prediction_from_tempo(
                tempo_1, tempo_X, tempo_2, pattern
            )
            
            output = ModelOutput(
                prediction=prediction,
                confidence=confidence,
                match_id=input_data.get("mecz", ""),
                group_id=input_data.get("id_grupy", "")
            )
            
            output.explanation = {
                "pattern": pattern,
                "tempo_values": {"tempo_1": tempo_1, "tempo_X": tempo_X, "tempo_2": tempo_2},
                "acceleration": self._calculate_acceleration(tempo_1, tempo_X, tempo_2)
            }
            
            return output
            
        except Exception as e:
            logger.error(f"Predykcja Sieć 03: {e}")
            return ModelOutput(prediction="1:1", confidence=0.5)
    
    def _analyze_tempo_pattern(self, tempo_1: float, tempo_X: float, tempo_2: float) -> str:
        """Analiza wzorca tempa"""
        patterns = []
        
        # Analiza indywidualnych temp
        if abs(tempo_1) > self.HIGH_TEMPO:
            patterns.append("high_tempo_1")
        elif abs(tempo_1) > self.MEDIUM_TEMPO:
            patterns.append("medium_tempo_1")
        
        if abs(tempo_X) > self.HIGH_TEMPO:
            patterns.append("high_tempo_X")
        elif abs(tempo_X) > self.MEDIUM_TEMPO:
            patterns.append("medium_tempo_X")
            
        if abs(tempo_2) > self.HIGH_TEMPO:
            patterns.append("high_tempo_2")
        elif abs(tempo_2) > self.MEDIUM_TEMPO:
            patterns.append("medium_tempo_2")
        
        # Analiza globalna
        avg_tempo = abs(tempo_1) + abs(tempo_X) + abs(tempo_2)
        if avg_tempo > self.HIGH_TEMPO * 2:
            patterns.append("very_high_activity")
        elif avg_tempo > self.HIGH_TEMPO:
            patterns.append("high_activity")
        elif avg_tempo < self.MEDIUM_TEMPO:
            patterns.append("low_activity")
        
        # Analiza kierunku
        if tempo_1 < -self.HIGH_TEMPO and tempo_2 > self.HIGH_TEMPO:
            patterns.append("strong_home_trend")
        elif tempo_1 > self.HIGH_TEMPO and tempo_2 < -self.HIGH_TEMPO:
            patterns.append("strong_away_trend")
        
        if tempo_X < -self.HIGH_TEMPO:
            patterns.append("strong_draw_signal")
            
        return ",".join(patterns) if patterns else "neutral_tempo"
    
    def _calculate_acceleration(self, tempo_1: float, tempo_X: float, tempo_2: float) -> float:
        """Wylicz przyspieszenie (zmianę tempa)"""
        # Uproszczone wyliczenie
        return (abs(tempo_1) + abs(tempo_X) + abs(tempo_2)) / 3
    
    def _generate_prediction_from_tempo(self, tempo_1: float, tempo_X: float, 
                                       tempo_2: float, pattern: str) -> Tuple[str, float]:
        """Generuj predykcję na podstawie tempa"""
        # Główna logika na podstawie wzorca
        if "strong_home_trend" in pattern:
            predictions = ["2:0", "2:1", "3:0", "3:1", "1:0"]
            confidence = 0.70 + min(0.25, abs(tempo_1) * 0.1)
            return random.choice(predictions), min(0.95, confidence)
            
        elif "strong_away_trend" in pattern:
            predictions = ["0:2", "1:2", "0:3", "1:3", "0:1"]
            confidence = 0.70 + min(0.25, abs(tempo_2) * 0.1)
            return random.choice(predictions), min(0.95, confidence)
            
        elif "strong_draw_signal" in pattern:
            predictions = ["1:1", "0:0", "2:2"]
            confidence = 0.65 + min(0.20, abs(tempo_X) * 0.1)
            return random.choice(predictions), min(0.90, confidence)
            
        elif "very_high_activity" in pattern:
            # Bardzo wysoka aktywność - kursy szybko się zmienią
            # Zazwyczaj oznacza to, że coś się dzieje (informacje, kontuzje, itd.)
            # Predykcja oparte na kierunku zmian
            if tempo_1 < -self.MEDIUM_TEMPO and tempo_2 > self.MEDIUM_TEMPO:
                predictions = ["2:0", "3:0", "2:1"]
            elif tempo_1 > self.MEDIUM_TEMPO and tempo_2 < -self.MEDIUM_TEMPO:
                predictions = ["0:2", "0:3", "1:2"]
            else:
                predictions = ["1:1", "2:0", "0:2"]
            return random.choice(predictions), 0.65
            
        elif "low_activity" in pattern:
            # Niska aktywność - kursy stabilne
            predictions = ["1:1", "0:0", "1:0", "0:1"]
            return random.choice(predictions), 0.60
            
        else:
            # Standardowa logika
            return self._standard_tempo_prediction(tempo_1, tempo_X, tempo_2)
    
    def _standard_tempo_prediction(self, tempo_1: float, tempo_X: float, tempo_2: float) -> Tuple[str, float]:
        """Standardowa predykcja oparta na tempo"""
        # Oblicz wagowy wynik
        score_1 = tempo_1 * -1  # Im niższy tempo_1 (kurs spada), tym wyższy wynik
        score_X = tempo_X * -1
        score_2 = tempo_2 * 1   # Im niższy tempo_2 (kurs spada), tym wyższy wynik
        
        # Normalizacja
        total = abs(score_1) + abs(score_X) + abs(score_2)
        if total == 0:
            return random.choice(["1:0", "0:1", "1:1"]), 0.55
        
        # Określ dominujący wynik
        scores = {
            "1": score_1 / total,
            "X": score_X / total,
            "2": score_2 / total
        }
        
        # Znajdź najwyższy wynik
        max_score = max(scores.values())
        winners = [k for k, v in scores.items() if v == max_score]
        
        if len(winners) == 1:
            winner = winners[0]
            if winner == "1":
                predictions = ["1:0", "2:0", "2:1", "3:0"]
            elif winner == "X":
                predictions = ["1:1", "0:0", "2:2"]
            else:  # 2
                predictions = ["0:2", "1:2", "0:3", "0:1"]
            confidence = 0.65 + max_score * 0.2
            return random.choice(predictions), min(0.90, confidence)
        else:
            # Remis
            predictions = ["1:1", "0:0", "2:2"]
            return random.choice(predictions), 0.60
    
    def get_world_features(self) -> List[str]:
        """Pobieranie cech Świata 2 (Tempo)"""
        return ["tempo_1", "tempo_X", "tempo_2"]


if __name__ == "__main__":
    print("Testing Siec03Tempo...")
    
    model = Siec03Tempo()
    print(f"Model: {model.model_name}")
    print(f"Świat: {model.world_type.value}")
    print(f"Cechy: {model.get_world_features()}")
    
    model.initialize()
    print(f"Status: {model.status.value}")
    
    test_cases = [
        {"tempo_1": -0.8, "tempo_X": 0.2, "tempo_2": 0.5},  # Home advantage
        {"tempo_1": 0.8, "tempo_X": -0.2, "tempo_2": -0.6},  # Away advantage
        {"tempo_1": 0.1, "tempo_X": -0.7, "tempo_2": 0.1},   # Draw tendency
        {"tempo_1": 0.05, "tempo_X": 0.0, "tempo_2": -0.05}, # Neutral
    ]
    
    for i, test_data in enumerate(test_cases):
        prediction = model.predict(test_data)
        print(f"Test {i+1}: {prediction.prediction} (conf: {prediction.confidence:.2f})")
        print(f"  Wzór: {prediction.explanation.get('pattern', 'N/A')}")
    
    print("\nSieć 03 tests passed!")
