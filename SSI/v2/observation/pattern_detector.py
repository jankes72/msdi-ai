"""
SSI V2 Pattern Detector - Wykrywanie wzorców

Odpowiedzialność:
- Identyfikacja powtarzających się wzorców w zachowaniu modeli
- Klasyfikacja wzorców
- Analiza tendencji

Wersja: 1.0
Data: 2026-07-28
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class PatternDetectionConfig:
    """Konfiguracja wykrywania wzorców"""
    min_occurrences: int = 5  # Minimalna liczba wystąpień
    max_pattern_count: int = 50  # Maksymalna liczba zapamiętanych wzorców
    
    trend_window: int = 100  # Okno do analizy tendencji
    anomaly_threshold: float = 0.3  # Próg anomalii
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "min_occurrences": self.min_occurrences,
            "max_pattern_count": self.max_pattern_count,
            "trend_window": self.trend_window,
            "anomaly_threshold": self.anomaly_threshold
        }


@dataclass
class DetectedPattern:
    """Wykryty wzorzec"""
    pattern_id: str
    pattern_name: str
    pattern_type: str  # trend, cycle, cluster, anomaly, stable
    
    occurrences: int = 0
    accuracy: float = 0.0
    confidence: float = 0.0
    
    first_detected: datetime = field(default_factory=datetime.now)
    last_detected: datetime = field(default_factory=datetime.now)
    
    # Charakterystyka wzorca
    characteristic_features: Dict[str, float] = field(default_factory=dict)
    match_ids: List[str] = field(default_factory=list)
    
    # Statystyki
    avg_confidence: float = 0.0
    std_confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "pattern_name": self.pattern_name,
            "pattern_type": self.pattern_type,
            "occurrences": self.occurrences,
            "accuracy": round(self.accuracy, 4),
            "confidence": round(self.confidence, 4),
            "avg_confidence": round(self.avg_confidence, 4),
            "first_detected": self.first_detected.isoformat(),
            "last_detected": self.last_detected.isoformat(),
            "example_matches": self.match_ids[:5]  # Ograniczone do 5
        }


@dataclass
class Anomaly:
    """Wykryta anomalia"""
    anomaly_id: str
    anomaly_type: str  # model, feature, prediction, pattern
    
    description: str
    severity: float = 0.0  # 0-1
    
    detection_time: datetime = field(default_factory=datetime.now)
    match_id: str = ""
    model_id: str = ""
    
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "anomaly_id": self.anomaly_id,
            "anomaly_type": self.anomaly_type,
            "description": self.description,
            "severity": round(self.severity, 4),
            "detection_time": self.detection_time.isoformat(),
            "match_id": self.match_id,
            "model_id": self.model_id
        }


class PatternDetector:
    """
    Detektor wzorców w zachowaniu modeli
    
    Odpowiedzialność:
    - Wykrywanie powtarzających się wzorców
    - Identyfikacja anomalii
    - Analiza trendów
    - Klasyfikacja wzorców
    """
    
    PATTERN_TYPES = [
        "trend_up", "trend_down", "trend_stable",
        "cycle_daily", "cycle_weekly", "cycle_monthly",
        "cluster_high_performance", "cluster_low_performance",
        "anomaly_extreme", "anomaly_outlier", "anomaly_change",
        "pattern_consistent", "pattern_variable"
    ]
    
    def __init__(self, config: Optional[PatternDetectionConfig] = None):
        """Inicjalizacja detektora"""
        self.config = config or PatternDetectionConfig()
        self.patterns: Dict[str, DetectedPattern] = {}
        self.anomalies: List[Anomaly] = []
        self.trends: Dict[str, List[float]] = {}  # trendy dla modeli
        logger.info("PatternDetector zainicjowany")
    
    def add_observation(self, observation: Dict[str, Any]) -> None:
        """
        Dodawanie obserwacji do anality
        
        Args:
            observation: Rekord obserwacji
        """
        try:
            model_id = observation.get("model_id", "")
            model_name = observation.get("model_name", "")
            prediction = observation.get("prediction", "")
            actual = observation.get("actual_result", "")
            correct = observation.get("correct", False)
            confidence = observation.get("confidence", 0.5)
            input_data = observation.get("input_data", {})
            
            # Analiza wzorców
            self._analyze_patterns(model_id, model_name, observation)
            
            # Analiza anomalii
            self._detect_anomalies(observation)
            
            # Aktualizuj trendy
            self._update_trends(model_id, correct, confidence)
            
        except Exception as e:
            logger.warning(f"Analiza obserwacji: {e}")
    
    def _analyze_patterns(self, model_id: str, model_name: str, observation: Dict[str, Any]) -> None:
        """Analiza wzorców"""
        try:
            # Określ charakterystyczne cechy tej obserwacji
            features = self._extract_features(observation)
            
            # Generuj sygnaturę wzorca
            pattern_signature = self._generate_pattern_signature(model_id, features, observation)
            
            # Zaktualizuj wzorzec
            if pattern_signature not in self.patterns:
                self._create_pattern(pattern_signature, model_id, model_name, observation)
            else:
                self._update_pattern(pattern_signature, observation)
            
            # Ogranicz liczbę wzorców
            if len(self.patterns) > self.config.max_pattern_count:
                self._cleanup_patterns()
                
        except Exception as e:
            logger.warning(f"Analiza wzorców: {e}")
    
    def _extract_features(self, observation: Dict[str, Any]) -> Dict[str, float]:
        """Ekstrakcja cech z obserwacji"""
        features = {}
        
        input_data = observation.get("input_data", {})
        for key, value in input_data.items():
            try:
                features[key] = float(value)
            except (ValueError, TypeError):
                pass
        
        # Dodaj cechy wynikowe
        features["correct"] = 1.0 if observation.get("correct", False) else 0.0
        features["correct_group"] = 1.0 if observation.get("correct_group", False) else 0.0
        features["confidence"] = float(observation.get("confidence", 0.5))
        
        return features
    
    def _generate_pattern_signature(self, model_id: str, features: Dict[str, float],
                                   observation: Dict[str, Any]) -> str:
        """Generuj unikalną sygnaturę wzorca"""
        try:
            # Podstawowe informacje
            parts = [
                f"model_{model_id}",
                f"correct_{int(features.get('correct', 0))}",
            ]
            
            # Analiza dwóch głównych cech
            important_features = ["zmiana_1", "amplituda_1", "tempo_1", "synchronizacja"]
            for feature in important_features:
                if feature in features:
                    value = features[feature]
                    # Określ przedział
                    if value > 0.5:
                        parts.append(f"{feature}_high")
                    elif value > 0.1:
                        parts.append(f"{feature}_medium")
                    elif value < -0.5:
                        parts.append(f"{feature}_low")
                    elif value < -0.1:
                        parts.append(f"{feature}_medium_neg")
            
            # Analiza confidence
            confidence = features.get("confidence", 0.5)
            if confidence > 0.8:
                parts.append("conf_high")
            elif confidence < 0.5:
                parts.append("conf_low")
            
            # Tworzenie sygnatury
            signature = "|".join(sorted(parts))
            return f"pattern_{abs(hash(signature)) % 10000:04d}"
            
        except Exception as e:
            logger.warning(f"Generowanie sygnatury: {e}")
            return "pattern_unknown"
    
    def _create_pattern(self, pattern_id: str, model_id: str, model_name: str,
                       observation: Dict[str, Any]) -> None:
        """Tworzenie nowego wzorca"""
        try:
            pattern_name = f"{model_name}_pattern_{len(self.patterns) + 1}"
            
            pattern = DetectedPattern(
                pattern_id=pattern_id,
                pattern_name=pattern_name,
                pattern_type=self._classify_pattern_type(observation)
            )
            
            self._update_pattern(pattern_id, observation, pattern)
            logger.info(f"Nowy wzorzec: {pattern_name}")
            
        except Exception as e:
            logger.warning(f"Tworzenie wzorca: {e}")
    
    def _update_pattern(self, pattern_id: str, observation: Dict[str, Any],
                       pattern: Optional[DetectedPattern] = None) -> None:
        """Aktualizacja wzorca"""
        target_pattern = pattern or self.patterns.get(pattern_id)
        if target_pattern is None:
            return
        
        # Zaktualizuj statystyki
        target_pattern.occurrences += 1
        target_pattern.last_detected = datetime.fromisoformat(
            observation.get("timestamp", datetime.now().isoformat())
        )
        
        # Zaktualizuj jakosć
        if observation.get("correct", False):
            current_acc = target_pattern.accuracy
            new_acc = ((current_acc * (target_pattern.occurrences - 1)) + 1) / target_pattern.occurrences
            target_pattern.accuracy = new_acc
        
        # Zaktualizuj confidence
        confidence = observation.get("confidence", 0.5)
        current_conf = target_pattern.avg_confidence
        target_pattern.avg_confidence = (
            (current_conf * (target_pattern.occurrences - 1)) + confidence
        ) / target_pattern.occurrences
        
        # Zapisz match_id
        match_id = observation.get("match_id", "")
        if match_id and match_id not in target_pattern.match_ids:
            target_pattern.match_ids.append(match_id)
            if len(target_pattern.match_ids) > 10:
                target_pattern.match_ids = target_pattern.match_ids[-10:]
        
        # Zapisz cechy
        input_data = observation.get("input_data", {})
        for key, value in input_data.items():
            try:
                target_pattern.characteristic_features[key] = (
                    target_pattern.characteristic_features.get(key, 0) * (target_pattern.occurrences - 1) + float(value)
                ) / target_pattern.occurrences
            except (ValueError, TypeError):
                pass
        
        # Zapisz wzorzec
        if pattern_id not in self.patterns:
            self.patterns[pattern_id] = target_pattern
    
    def _classify_pattern_type(self, observation: Dict[str, Any]) -> str:
        """Klasyfikacja typu wzorca"""
        correct = observation.get("correct", False)
        correct_group = observation.get("correct_group", False)
        confidence = observation.get("confidence", 0.5)
        
        if not correct:
            if not correct_group:
                return "anomaly_outlier"
            else:
                return "pattern_variable"
        
        if confidence > 0.8:
            return "pattern_consistent"
        else:
            return "trend_stable"
    
    def _detect_anomalies(self, observation: Dict[str, Any]) -> None:
        """Wykrywanie anomalii"""
        try:
            model_id = observation.get("model_id", "")
            model_name = observation.get("model_name", "")
            match_id = observation.get("match_id", "")
            
            # Anomalie: Brak poprawności + niskie confidence
            if (not observation.get("correct", True) and 
                not observation.get("correct_group", True) and
                observation.get("confidence", 0) < 0.3):
                
                anomaly = Anomaly(
                    anomaly_id=f"anomaly_{len(self.anomalies):04d}",
                    anomaly_type="prediction_error",
                    description=f"Całkowicie błędna predykcja modelu {model_name} z niskim confidence",
                    severity=0.9,
                    match_id=match_id,
                    model_id=model_id,
                    details={
                        "prediction": observation.get("prediction", ""),
                        "actual": observation.get("actual_result", ""),
                        "confidence": observation.get("confidence", 0)
                    }
                )
                self.anomalies.append(anomaly)
                logger.warning(f"Wykryto anomalię: {anomaly.description}")
            
            # Anomalie cechy: Ekstremalne wartości cech
            input_data = observation.get("input_data", {})
            for feature, value in input_data.items():
                try:
                    float_value = float(value)
                    if abs(float_value) > 10:  # Ekstremalnie wysoka wartość
                        anomaly = Anomaly(
                            anomaly_id=f"anomaly_{len(self.anomalies):04d}",
                            anomaly_type="feature_extreme",
                            description=f"Ekstremalna wartość cechy {feature}: {float_value}",
                            severity=min(1.0, abs(float_value) / 100),
                            match_id=match_id,
                            model_id=model_id,
                            details={"feature": feature, "value": float_value}
                        )
                        self.anomalies.append(anomaly)
                        logger.warning(f"Wykryto anomalię cechy: {feature}={float_value}")
                except (ValueError, TypeError):
                    pass
            
        except Exception as e:
            logger.warning(f"Wykrywanie anomalii: {e}")
    
    def _update_trends(self, model_id: str, correct: bool, confidence: float) -> None:
        """Aktualizacja trendów"""
        if model_id not in self.trends:
            self.trends[model_id] = []
        
        # Zapisuj wyniki
        self.trends[model_id].append(correct)
        
        # Ogranicz rozmiar
        if len(self.trends[model_id]) > self.config.trend_window:
            self.trends[model_id] = self.trends[model_id][-self.config.trend_window:]
    
    def detect_trends(self) -> Dict[str, Dict[str, Any]]:
        """Wykryj trendy w poprawności modeli"""
        trends = {}
        
        for model_id, results in self.trends.items():
            if len(results) >= 10:  # Minimalna liczba do analizy
                recent_hits = sum(results[-10:])
                recent_accuracy = recent_hits / 10
                
                older_hits = sum(results[:max(0, len(results) - 10)])
                older_accuracy = older_hits / max(len(results) - 10, 1) if len(results) > 10 else 0
                
                trend_direction = "up" if recent_accuracy > older_accuracy else "down"
                trend_strength = abs(recent_accuracy - older_accuracy)
                
                trends[model_id] = {
                    "recent_accuracy": round(recent_accuracy, 4),
                    "older_accuracy": round(older_accuracy, 4),
                    "direction": trend_direction,
                    "strength": round(trend_strength, 4),
                    "samples": len(results)
                }
        
        return trends
    
    def get_pattern(self, pattern_id: str) -> Optional[DetectedPattern]:
        """Pobieranie wzorca"""
        return self.patterns.get(pattern_id)
    
    def get_all_patterns(self) -> Dict[str, DetectedPattern]:
        """Pobieranie wszystkich wzorców"""
        return self.patterns
    
    def get_anomalies(self) -> List[Anomaly]:
        """Pobieranie wszystkich anomalii"""
        return self.anomalies
    
    def get_summary(self) -> Dict[str, Any]:
        """Pobieranie podsumowania"""
        return {
            "patterns_detected": len(self.patterns),
            "anomalies_detected": len(self.anomalies),
            "models_tracked": len(self.trends),
            "trends": self.detect_trends(),
            "patterns": {k: v.to_dict() for k, v in self.patterns.items()},
            "recent_anomalies": [a.to_dict() for a in self.anomalies[-10:]]
        }
    
    def _cleanup_patterns(self) -> None:
        """Czyszczenie starych wzorców"""
        if len(self.patterns) <= self.config.max_pattern_count:
            return
        
        # Usuń wzorce z najmniejszą liczbą wystąpień
        sorted_patterns = sorted(
            self.patterns.items(),
            key=lambda x: (x[1].occurrences, x[1].last_detected)
        )
        
        # Usuń 10% wzorców
        to_remove = max(1, len(sorted_patterns) // 10)
        for pattern_id, _ in sorted_patterns[:to_remove]:
            del self.patterns[pattern_id]
        
        logger.info(f"Usunięto {to_remove} wzorców")
    
    def clear(self) -> None:
        """Czyszczenie detektora"""
        self.patterns = {}
        self.anomalies = []
        self.trends = {}
        logger.info("PatternDetector wyczyszczony")


if __name__ == "__main__":
    print("Testing PatternDetector...")
    
    # Test 1: Tworzenie detektora
    detector = PatternDetector()
    print(f"Detektor utworzony")
    
    # Test 2: Dodawanie obserwacji
    observations = [
        {
            "model_id": "model_001",
            "model_name": "siec_01",
            "match_id": f"match_{i}",
            "prediction": "2:0",
            "actual_result": "2:0",
            "correct": True,
            "correct_group": True,
            "confidence": 0.85 + i * 0.01,
            "timestamp": "2026-07-28T12:00:00",
            "input_data": {
                "zmiana_1": -0.3 - i * 0.01,
                "amplituda_1": 0.5 + i * 0.01
            }
        }
        for i in range(20)
    ]
    
    for obs in observations:
        detector.add_observation(obs)
    
    # Podsumowanie
    summary = detector.get_summary()
    print(f"Podsumowanie: {summary['patterns_detected']} wzorców, "
          f"{summary['anomalies_detected']} anomalii")
    
    print("\nPatternDetector tests passed!")
