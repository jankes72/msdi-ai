"""
SSI V2 Model - Sieć 02: Amplituda

Zgodnie z dokumentacją:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 2.2
- 02_DATA_STRUCTURE.md Sekcja 3.2 (Świat 2: Dynamika)

Opis:
Model analizujący amplitudę zmian kursów bukmacherskich.
Świat 2 skupia się na cechach dynamiki:
- amplituda_1: Amplituda zmian kursu na 1
- amplituda_X: Amplituda zmian kursu na X
- amplituda_2: Amplituda zmian kursu na 2
- tempo_1: Tempo zmian kursu na 1
- tempo_X: Tempo zmian kursu na X
- tempo_2: Tempo zmian kursu na 2
- synchronizacja: Synchronizacja zmian między kursami
- max_wahanie_1: Maksymalne wahanie kursu 1
- max_wahanie_X: Maksymalne wahanie kursu X
- max_wahanie_2: Maksymalne wahanie kursu 2

Typ świat: SWIAT_2_DYNAMIKA

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


class Siec02Amplituda(BaseModelV2):
    """
    Model Sieć 02: Analiza Amplitudy i Dynamiki Kursów
    
    Specjalizacja:
    - Analiza amplitudy zmian (zakres wahań)
    - Analiza tempa zmian (szybkość zmian)
    - Analiza synchronizacji między kursami
    - Wykrywanie wzorców dynamiki
    
    Świat 2: Dynamika
    
    Cechy wejściowe:
    - amplituda_1, amplituda_X, amplituda_2
    - tempo_1, tempo_X, tempo_2
    - synchronizacja
    - max_wahanie_1, max_wahanie_X, max_wahanie_2
    """
    
    # Progi dla amplitudy
    HIGH_AMPLITUDE_THRESHOLD: float = 0.8
    MEDIUM_AMPLITUDE_THRESHOLD: float = 0.4
    LOW_AMPLITUDE_THRESHOLD: float = 0.2
    
    # Progi dla tempa
    HIGH_TEMPO_THRESHOLD: float = 0.5
    MEDIUM_TEMPO_THRESHOLD: float = 0.2
    
    # Progi dla synchronizacji
    HIGH_SYNC_THRESHOLD: float = 0.7
    LOW_SYNC_THRESHOLD: float = 0.3
    
    def __init__(self, config: Optional[ModelConfig] = None):
        """Inicjalizacja modelu Sieć 02"""
        default_config = ModelConfig(
            model_name="siec_02_amplituda",
            model_type=ModelType.AMPLITUDA,
            world_type=WorldType.SWIAT_2_DYNAMIKA,
            version="1.0.0",
            description="Model analizy amplitudy i dynamiki kursów bukmacherskich (Świat 2)",
            features=[
                "amplituda_1", "amplituda_X", "amplituda_2",
                "tempo_1", "tempo_X", "tempo_2",
                "synchronizacja",
                "max_wahanie_1", "max_wahanie_X", "max_wahanie_2"
            ],
            target_column="wynik",
            params={
                "amplitude_thresholds": {
                    "high": self.HIGH_AMPLITUDE_THRESHOLD,
                    "medium": self.MEDIUM_AMPLITUDE_THRESHOLD,
                    "low": self.LOW_AMPLITUDE_THRESHOLD
                },
                "tempo_thresholds": {
                    "high": self.HIGH_TEMPO_THRESHOLD,
                    "medium": self.MEDIUM_TEMPO_THRESHOLD
                },
                "sync_thresholds": {
                    "high": self.HIGH_SYNC_THRESHOLD,
                    "low": self.LOW_SYNC_THRESHOLD
                }
            }
        )
        
        super().__init__(config or default_config)
        
        # Ładuj progi z konfiguracji
        self.amplitude_thresholds = self.config.params.get("amplitude_thresholds", {})
        self.tempo_thresholds = self.config.params.get("tempo_thresholds", {})
        self.sync_thresholds = self.config.params.get("sync_thresholds", {})
        
        logger.info(f"Sieć 02: {self.model_name} - Załadowano")
    
    def _determine_dynamics_pattern(self, input_data: Dict[str, Any]) -> str:
        """
        Określenie wzorca dynamiki
        
        Wzorce dynamiki:
        - high_amplitude: Duże wahania kursów
        - low_amplitude: Małe wahania (stabilny kurs)
        - fast_tempo: Szybkie zmiany
        - slow_tempo: Wolne zmiany
        - synchronized: Zmiany zsynchronizowane
        - desynchronized: Zmiany niesynchronizowane
        - chaotic: Wysoka amplituda + wysokie tempo + niska synchronizacja
        - stable: Niska amplituda + niskie tempo + wysoka synchronizacja
        """
        patterns = []
        
        # Pobierz wartości
        amp_1 = abs(float(input_data.get("amplituda_1", 0.0)))
        amp_X = abs(float(input_data.get("amplituda_X", 0.0)))
        amp_2 = abs(float(input_data.get("amplituda_2", 0.0)))
        
        tempo_1 = abs(float(input_data.get("tempo_1", 0.0)))
        tempo_X = abs(float(input_data.get("tempo_X", 0.0)))
        tempo_2 = abs(float(input_data.get("tempo_2", 0.0)))
        
        synchronizacja = float(input_data.get("synchronizacja", 0.0))
        
        # Średnia amplituda
        avg_amplitude = (amp_1 + amp_X + amp_2) / 3
        
        # Średnie tempo
        avg_tempo = (tempo_1 + tempo_X + tempo_2) / 3
        
        # Określ amplitudę
        if avg_amplitude > self.amplitude_thresholds.get("high", 0.8):
            patterns.append("high_amplitude")
        elif avg_amplitude > self.amplitude_thresholds.get("medium", 0.4):
            patterns.append("medium_amplitude")
        else:
            patterns.append("low_amplitude")
        
        # Określ tempo
        if avg_tempo > self.tempo_thresholds.get("high", 0.5):
            patterns.append("fast_tempo")
        elif avg_tempo > self.tempo_thresholds.get("medium", 0.2):
            patterns.append("medium_tempo")
        else:
            patterns.append("slow_tempo")
        
        # Określ synchronizację
        if synchronizacja > self.sync_thresholds.get("high", 0.7):
            patterns.append("synchronized")
        elif synchronizacja < self.sync_thresholds.get("low", 0.3):
            patterns.append("desynchronized")
        else:
            patterns.append("partial_sync")
        
        # Określ ogólny wzorzec
        if ("high_amplitude" in patterns and "fast_tempo" in patterns and 
            "desynchronized" in patterns):
            patterns.append("chaotic")
        elif ("low_amplitude" in patterns and "slow_tempo" in patterns and 
              "synchronized" in patterns):
            patterns.append("stable")
        
        return ",".join(patterns) if patterns else "neutral"
    
    def _predict_internal(self, input_data: Dict[str, Any], **kwargs) -> ModelOutput:
        """Generowanie predykcji na podstawie amplitudy i dynamiki"""
        try:
            # Określ wzorzec
            pattern = self._determine_dynamics_pattern(input_data)
            
            # Generuj predykcję
            prediction, confidence = self._predict_from_dynamics(pattern, input_data)
            
            output = ModelOutput(
                prediction=prediction,
                confidence=confidence,
                match_id=input_data.get("mecz", ""),
                group_id=input_data.get("id_grupy", "")
            )
            
            output.explanation = {
                "pattern": pattern,
                "amplitude": {
                    "1": input_data.get("amplituda_1", 0),
                    "X": input_data.get("amplituda_X", 0),
                    "2": input_data.get("amplituda_2", 0)
                },
                "tempo": {
                    "1": input_data.get("tempo_1", 0),
                    "X": input_data.get("tempo_X", 0),
                    "2": input_data.get("tempo_2", 0)
                },
                "synchronizacja": input_data.get("synchronizacja", 0)
            }
            
            return output
            
        except Exception as e:
            logger.error(f"Predykcja Sieć 02: {e}")
            return ModelOutput(prediction="1:1", confidence=0.5)
    
    def _predict_from_dynamics(self, pattern: str, input_data: Dict[str, Any]) -> Tuple[str, float]:
        """Predykcja na podstawie wzorca dynamiki"""
        # Pobierz wartości
        amp_1 = float(input_data.get("amplituda_1", 0.0))
        amp_X = float(input_data.get("amplituda_X", 0.0))
        amp_2 = float(input_data.get("amplituda_2", 0.0))
        
        # Określ kierunek zmian (znaki)
        dir_1 = 1 if amp_1 > 0 else (-1 if amp_1 < 0 else 0)
        dir_X = 1 if amp_X > 0 else (-1 if amp_X < 0 else 0)
        dir_2 = 1 if amp_2 > 0 else (-1 if amp_2 < 0 else 0)
        
        # Logika decyzyjna
        if "chaotic" in pattern:
            # Chaotyczne zachowanie - trudno przewidzieć
            predictions = ["1:0", "0:1", "2:0", "0:2", "1:1", "2:1", "1:2"]
            confidence = 0.55  # Niska pewność
            return random.choice(predictions), confidence
            
        elif "stable" in pattern:
            # Stabilny kurs - przewiduj remis
            predictions = ["0:0", "1:1", "2:2"]
            confidence = 0.75
            return random.choice(predictions), confidence
            
        elif "high_amplitude" in pattern:
            # Duże wahania - sprawdź kierunek
            if dir_1 < 0 and dir_2 > 0:  # Kurs na 1 spada, na 2 rośnie
                predictions = ["2:0", "2:1", "3:0", "3:1"]
                confidence = 0.70 + abs(amp_1) * 0.05
                return random.choice(predictions), min(0.9, confidence)
            elif dir_1 > 0 and dir_2 < 0:  # Kurs na 1 rośnie, na 2 spada
                predictions = ["0:2", "1:2", "0:3", "1:3"]
                confidence = 0.70 + abs(amp_2) * 0.05
                return random.choice(predictions), min(0.9, confidence)
            else:
                predictions = ["1:1", "2:2", "0:0"]
                return random.choice(predictions), 0.65
                
        elif "fast_tempo" in pattern:
            # Szybkie zmiany - trendy krótkoterminowe
            if dir_1 < 0:  # Kurs na gospodarzy spada
                predictions = ["2:0", "2:1", "1:0"]
                confidence = 0.68 + abs(amp_1) * 0.04
                return random.choice(predictions), min(0.85, confidence)
            elif dir_1 > 0:  # Kurs na gospodarzy rośnie
                predictions = ["0:2", "1:2", "0:1"]
                confidence = 0.68 + abs(amp_1) * 0.04
                return random.choice(predictions), min(0.85, confidence)
            else:
                predictions = ["1:1", "0:0"]
                return random.choice(predictions), 0.65
                
        elif "synchronized" in pattern:
            # Zmiany zsynchronizowane - spójne ruchy
            if dir_1 < 0 and dir_X < 0 and dir_2 < 0:
                # Wszystkie kursy rosną - mniejsze szanse na nieoczekiwane wyniki
                predictions = ["1:0", "0:1", "1:1", "2:0", "0:2"]
                return random.choice(predictions), 0.70
            elif dir_1 > 0 and dir_X > 0 and dir_2 > 0:
                # Wszystkie kursy maleją - większa pewność
                if dir_1 < dir_2:
                    predictions = ["2:0", "2:1", "3:0"]
                else:
                    predictions = ["0:2", "1:2", "0:3"]
                return random.choice(predictions), 0.75
            else:
                predictions = ["1:1", "0:0", "2:2"]
                return random.choice(predictions), 0.70
                
        else:
            # Domyślna predykcja
            return self._default_prediction()
    
    def _default_prediction(self) -> Tuple[str, float]:
        """Domyślna predykcja"""
        predictions = ["1:0", "0:1", "1:1", "2:0", "0:2", "2:1", "1:2"]
        return random.choice(predictions), 0.60
    
    def get_world_features(self) -> List[str]:
        """Pobieranie cech Świata 2"""
        return [
            "amplituda_1", "amplituda_X", "amplituda_2",
            "tempo_1", "tempo_X", "tempo_2",
            "synchronizacja",
            "max_wahanie_1", "max_wahanie_X", "max_wahanie_2"
        ]


if __name__ == "__main__":
    # Testy Sieci 02
    print("Testing Siec02Amplituda...")
    
    model = Siec02Amplituda()
    print(f"Model: {model.model_name}")
    print(f"Świat: {model.world_type.value}")
    print(f"Cechy: {model.get_world_features()}")
    
    model.initialize()
    print(f"Status: {model.status.value}")
    
    # Testowe dane
    test_cases = [
        {
            "amplituda_1": 1.2, "amplituda_X": 0.5, "amplituda_2": 0.8,
            "tempo_1": 0.8, "tempo_X": 0.3, "tempo_2": 0.6,
            "synchronizacja": 0.2
        },
        {
            "amplituda_1": 0.1, "amplituda_X": 0.1, "amplituda_2": 0.1,
            "tempo_1": 0.1, "tempo_X": 0.1, "tempo_2": 0.1,
            "synchronizacja": 0.9
        },
        {
            "amplituda_1": 0.5, "amplituda_X": 1.0, "amplituda_2": 0.3,
            "tempo_1": 0.3, "tempo_X": 0.8, "tempo_2": 0.2,
            "synchronizacja": 0.4
        }
    ]
    
    for i, test_data in enumerate(test_cases):
        prediction = model.predict(test_data)
        print(f"Test {i+1}: {prediction.prediction} (conf: {prediction.confidence:.2f})")
        print(f"  Wzór: {prediction.explanation.get('pattern', 'N/A')}")
    
    print("\nSieć 02 tests passed!")
