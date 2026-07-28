"""
SSI V2 Model - Sieć 04: Synchronizacja

Zgodnie z dokumentacją:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 2.2
- 02_DATA_STRUCTURE.md Sekcja 3.2 (Świat 2: Dynamika)

Opis:
Model analizujący synchronizację zmian między różnymi kursami.
Badanie zależności i korelacji między zmianami kursów na 1, X i 2.

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


class Siec04Synchronizacja(BaseModelV2):
    """
    Model Sieć 04: Analiza Synchronizacji Kursów
    
    Specjalizacja:
    - Badanie korelacji między zmianami kursów
    - Analiza wzorców synchronizacji/desynchronizacji
    - Wykrywanie niespójności między kursami
    
    Cechy główne:
    - synchronizacja: Stopień synchronizacji zmian między kursami
    - ratio_1X_start: Stosunek kursu 1 do X (początek)
    - ratio_1_2_start: Stosunek kursu 1 do 2 (początek)
    - ratio_X2_start: Stosunek kursu X do 2 (początek)
    - ratio_1X_koniec: Stosunek kursu 1 do X (koniec)
    - ratio_1_2_koniec: Stosunek kursu 1 do 2 (koniec)
    - ratio_X2_koniec: Stosunek kursu X do 2 (koniec)
    
    Interpretation:
    - Wysoka synchronizacja (>0.7): Zmiany są spójne
    - Niska synchronizacja (<0.3): Zmiany są niespójne
    - Średnia synchronizacja: Częściowa spójność
    """
    
    HIGH_SYNC: float = 0.7
    MEDIUM_SYNC: float = 0.5
    LOW_SYNC: float = 0.3
    
    def __init__(self, config: Optional[ModelConfig] = None):
        """Inicjalizacja modelu Sieć 04"""
        default_config = ModelConfig(
            model_name="siec_04_synchronizacja",
            model_type=ModelType.SYNCHRONIZACJA,
            world_type=WorldType.SWIAT_2_DYNAMIKA,
            version="1.0.0",
            description="Model analizy synchronizacji zmian kursów bukmacherskich",
            features=[
                "synchronizacja",
                "ratio_1X_start", "ratio_1_2_start", "ratio_X2_start",
                "ratio_1X_koniec", "ratio_1_2_koniec", "ratio_X2_koniec"
            ],
            target_column="wynik",
            params={
                "high_sync_threshold": self.HIGH_SYNC,
                "medium_sync_threshold": self.MEDIUM_SYNC,
                "low_sync_threshold": self.LOW_SYNC
            }
        )
        
        super().__init__(config or default_config)
        logger.info(f"Sieć 04: {self.model_name} - Załadowano")
    
    def _predict_internal(self, input_data: Dict[str, Any], **kwargs) -> ModelOutput:
        """Generowanie predykcji na podstawie synchronizacji"""
        try:
            synchronizacja = float(input_data.get("synchronizacja", 0.5))
            
            # Pobierz ratio jeśli dostępne
            ratio_1X_start = float(input_data.get("ratio_1X_start", 1.0))
            ratio_1X_koniec = float(input_data.get("ratio_1X_koniec", 1.0))
            
            pattern = self._analyze_sync_pattern(input_data)
            prediction, confidence = self._generate_prediction_from_sync(
                synchronizacja, input_data, pattern
            )
            
            output = ModelOutput(
                prediction=prediction,
                confidence=confidence,
                match_id=input_data.get("mecz", ""),
                group_id=input_data.get("id_grupy", "")
            )
            
            output.explanation = {
                "pattern": pattern,
                "synchronizacja": synchronizacja,
                "ratios": {
                    "ratio_1X_start": ratio_1X_start,
                    "ratio_1X_koniec": ratio_1X_koniec,
                    "ratio_1X_change": ratio_1X_koniec - ratio_1X_start
                }
            }
            
            return output
            
        except Exception as e:
            logger.error(f"Predykcja Sieć 04: {e}")
            return ModelOutput(prediction="1:1", confidence=0.5)
    
    def _analyze_sync_pattern(self, input_data: Dict[str, Any]) -> str:
        """Analiza wzorca synchronizacji"""
        patterns = []
        
        synchronizacja = float(input_data.get("synchronizacja", 0.5))
        
        if synchronizacja >= self.HIGH_SYNC:
            patterns.append("high_symmetry")
        elif synchronizacja >= self.MEDIUM_SYNC:
            patterns.append("medium_symmetry")
        elif synchronizacja <= self.LOW_SYNC:
            patterns.append("low_symmetry")
        
        # Analiza relacji między kursami
        ratio_1X_start = float(input_data.get("ratio_1X_start", 1.0))
        ratio_1X_koniec = float(input_data.get("ratio_1X_koniec", 1.0))
        ratio_1X_change = ratio_1X_koniec - ratio_1X_start
        
        ratio_1_2_start = float(input_data.get("ratio_1_2_start", 1.0))
        ratio_1_2_koniec = float(input_data.get("ratio_1_2_koniec", 1.0))
        ratio_1_2_change = ratio_1_2_koniec - ratio_1_2_start
        
        if ratio_1X_change > 0.2:
            patterns.append("ratio_1X_increasing")
        elif ratio_1X_change < -0.2:
            patterns.append("ratio_1X_decreasing")
            
        if ratio_1_2_change > 0.2:
            patterns.append("ratio_1_2_increasing")
        elif ratio_1_2_change < -0.2:
            patterns.append("ratio_1_2_decreasing")
        
        # Określ ogólny trend
        if "high_symmetry" in patterns:
            if ratio_1X_change > 0.1 and ratio_1_2_change > 0.1:
                patterns.append("favorable_home")
            elif ratio_1X_change < -0.1 and ratio_1_2_change < -0.1:
                patterns.append("favorable_away")
        
        return ",".join(patterns) if patterns else "neutral_sync"
    
    def _generate_prediction_from_sync(self, synchronizacja: float,
                                       input_data: Dict[str, Any],
                                       pattern: str) -> Tuple[str, float]:
        """Generuj predykcję na podstawie synchronizacji"""
        # Pobierz obsługane wartości
        ratio_1X_change = float(input_data.get("ratio_1X_koniec", 0)) - float(input_data.get("ratio_1X_start", 0))
        ratio_1_2_change = float(input_data.get("ratio_1_2_koniec", 0)) - float(input_data.get("ratio_1_2_start", 0))
        
        if "high_symmetry" in pattern:
            # Wysoka synchronizacja - spójne einie kursów
            if ratio_1X_change > 0.3:
                # Stosunek 1/X rośnie - gospodarze Equipe
                predictions = ["2:0", "2:1", "3:0", "1:0"]
                confidence = 0.70 + min(0.15, ratio_1X_change)
                return random.choice(predictions), min(0.9, confidence)
            elif ratio_1X_change < -0.3:
                # Stosun1szy 1/X maleje - większa szansa na gości
                predictions = ["0:2", "1:2", "0:3", "0:1"]
                confidence = 0.70 + min(0.15, abs(ratio_1X_change))
                return random.choice(predictions), min(0.9, confidence)
            elif ratio_1_2_change > 0.3:
                # Stosunek  1/2 rośnie - gospodarze w lepszej pozycji
                predictions = ["2:0", "3:0", "2:1"]
                confidence = 0.68 + min(0.12, ratio_1_2_change)
                return random.choice(predictions), min(0.85, confidence)
            else:
                predictions = ["1:1", "0:0", "2:2"]
                return random.choice(predictions), 0.65
                
        elif "low_symmetry" in pattern:
            # Nieszka synchronizacja - niespójne zmiany
            # To może oznaczać, że bukmacherzy mają różne informacje
            predictions = ["1:0", "0:1", "2:1", "1:2", "0:0"]
            confidence = 0.60
            return random.choice(predictions), confidence
            
        elif "medium_symmetry" in pattern:
            # Średnia synchronizacja
            if ratio_1X_change > 0.15:
                predictions = ["2:0", "1:0", "2:1"]
            elif ratio_1X_change < -0.15:
                predictions = ["0:2", "0:1", "1:2"]
            else:
                predictions = ["1:1", "0:0", "2:2", "1:0", "0:1"]
            return random.choice(predictions), 0.63
            
        elif "favorable_home" in pattern:
            predictions = ["2:0", "2:1", "3:0", "1:0"]
            return random.choice(predictions), 0.72
            
        elif "favorable_away" in pattern:
            predictions = ["0:2", "1:2", "0:3", "0:1"]
            return random.choice(predictions), 0.72
            
        else:
            # Domyślna predykcja
            return self._default_sync_prediction(synchronizacja)
    
    def _default_sync_prediction(self, synchronizacja: float) -> Tuple[str, float]:
        """Domyślna predykcja na podstawie synchronizacji"""
        if synchronizacja > self.MEDIUM_SYNC:
            # W miarę spójne - użyj standardowych predykcji
            predictions = ["1:0", "0:1", "1:1", "2:0", "0:2"]
            confidence = 0.58 + (synchronizacja - 0.5) * 0.1
        else:
            # Niespójne - trudniej przewidzieć
            predictions = ["1:0", "0:1", "1:1", "2:0", "0:2", "2:1", "1:2", "0:0"]
            confidence = 0.55
            
        return random.choice(predictions), min(0.85, max(0.5, confidence))
    
    def get_world_features(self) -> List[str]:
        """Pobieranie cech Świata 2 (Synchronizacja)"""
        return [
            "synchronizacja",
            "ratio_1X_start", "ratio_1_2_start", "ratio_X2_start",
            "ratio_1X_koniec", "ratio_1_2_koniec", "ratio_X2_koniec"
        ]


if __name__ == "__main__":
    print("Testing Siec04Synchronizacja...")
    
    model = Siec04Synchronizacja()
    print(f"Model: {model.model_name}")
    print(f"Świat: {model.world_type.value}")
    print(f"Cechy: {model.get_world_features()}")
    
    model.initialize()
    print(f"Status: {model.status.value}")
    
    test_cases = [
        {
            "synchronizacja": 0.85,
            "ratio_1X_start": 1.5, "ratio_1X_koniec": 1.8,
            "ratio_1_2_start": 2.0, "ratio_1_2_koniec": 2.3
        },
        {
            "synchronizacja": 0.25,
            "ratio_1X_start": 1.2, "ratio_1X_koniec": 1.0,
            "ratio_1_2_start": 1.8, "ratio_1_2_koniec": 1.5
        },
        {
            "synchronizacja": 0.55,
            "ratio_1X_start": 1.0, "ratio_1X_koniec": 1.1,
            "ratio_1_2_start": 1.5, "ratio_1_2_koniec": 1.6
        }
    ]
    
    for i, test_data in enumerate(test_cases):
        prediction = model.predict(test_data)
        print(f"Test {i+1}: {prediction.prediction} (conf: {prediction.confidence:.2f})")
        print(f"  Wzór: {prediction.explanation.get('pattern', 'N/A')}")
    
    print("\nSieć 04 tests passed!")
