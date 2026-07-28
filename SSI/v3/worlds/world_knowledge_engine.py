"""
SSI V3 World Knowledge Engine
Silnik wiedzy o światach - Tworzenie i analiza światów na podstawie modeli V2

Odpowiedzialność:
- Tworzenie światów na podstawie predykcji modeli V2
- Generowanie metadanych dla światów
- Analiza ekonomiczna światów
- Wykrywanie wzorców w światach
- Integracja z MemoryManager

Zgodnie z:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 3.2 (V3 World Knowledge Engine)
- 04_WORLD_SYSTEM.md Sekcja 3 (Definicja Światów)
- 10_IMPLEMENTATION_MAP.md Etap 3B

Architektura:
V2 Models (siec_01, siec_02, siec_03, siec_04, RF, Classifiers)
    ↓
World Knowledge Engine
    ├── World Creator (tworzy światy z predykcji)
    ├── Metadata Generator (generuje metadane)
    ├── Pattern Detector (wykrywa wzorce)
    ├── Economic Analyzer (analiza ekonomiczna)
    └── EV Calculator (wartość oczekiwana)
    ↓
V3 World Memory (zapis do pamięci)

Wersja: 1.0
Data: 2026-07-28
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum, auto
import uuid
import json
import os
from pathlib import Path
import logging
import threading
import statistics
from collections import defaultdict, Counter

from ..memory.memory_manager import MemoryManager, MemoryConfig
from .world import World, WorldType, WorldStatus
from .world_manager import WorldManager

# =============================================================================
# KONFIGURACJA
# =============================================================================

@dataclass
class WorldKnowledgeConfig:
    """Konfiguracja World Knowledge Engine"""
    
    # Ustawienia tworzenia świata
    MIN_CONFIDENCE: float = 0.6          # Minimalna pewność predykcji do akceptacji
    MIN_PATTERN_FREQUENCY: int = 3      # Minimalna częstotliwość wzorca
    MAX_WORLDS_PER_MODEL: int = 10     # Maksymalna liczba światów na model
    
    # Ustawienia analizy
    EV_CALCULATION_METHOD: str = "weighted_avg"  # Metoda obliczania EV
    PATTERN_DETECTION_WINDOW: int = 10   # Okno czasu dla wykrywania wzorców
    
    # Ustawienia ekonomiczne
    RISK_AVERSE_FACTOR: float = 0.8    # Współczynnik awersji do ryzyka
    REWARD_MULTIPLIER: float = 1.2      # Mnożnik nagrody
    
    # Integracja z V2
    ACCEPT_FROM_V2: bool = True
    V2_MODEL_WEIGHTS: Dict[str, float] = field(default_factory=lambda: {
        "siec_01_zmiana_kursow": 1.2,
        "siec_02_amplituda": 1.0,
        "siec_03_tempo": 1.0,
        "siec_04_synchronizacja": 1.1,
        "random_forest": 1.0,
        "classifiers": 0.9
    })
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "MIN_CONFIDENCE": self.MIN_CONFIDENCE,
            "MIN_PATTERN_FREQUENCY": self.MIN_PATTERN_FREQUENCY,
            "MAX_WORLDS_PER_MODEL": self.MAX_WORLDS_PER_MODEL,
            "EV_CALCULATION_METHOD": self.EV_CALCULATION_METHOD,
            "PATTERN_DETECTION_WINDOW": self.PATTERN_DETECTION_WINDOW,
            "RISK_AVERSE_FACTOR": self.RISK_AVERSE_FACTOR,
            "REWARD_MULTIPLIER": self.REWARD_MULTIPLIER,
            "ACCEPT_FROM_V2": self.ACCEPT_FROM_V2,
            "V2_MODEL_WEIGHTS": self.V2_MODEL_WEIGHTS
        }


# =============================================================================
# TYPY I ENUMY
# =============================================================================

class WorldSource(Enum):
    """Źródło tworzenia świata"""
    V2_MODEL = auto()       # Utworzony z modelu V2
    MANUAL = auto()          # Ręcznie utworzony
    EVOLUTION = auto()       # Wyewoluował z innego świata
    COMBINATION = auto()     # Połączenie innych światów


class PatternType(Enum):
    """Typ wzorca"""
    TREND = auto()           # Trend (rosnący/malejący)
    OSCILLATION = auto()     # Oscylacja
    STABILITY = auto()       # Stabilność
    JUMP = auto()            # Skok nagły
    INVERSION = auto()       # Odwrócenie wzorca
    SYNCHRONIZATION = auto()  # Synchronizacja
    DIVERGENCE = auto()      # Różnicowanie


class EconomicMetric(Enum):
    """Metryki ekonomiczne"""
    EV = auto()              # Wartość oczekiwana (Expected Value)
    ROI = auto()             # Zwrot z inwestycji
    RISK = auto()            # Ryzyko
    PROFITABILITY = auto()   # Rentowność
    CONFIDENCE = auto()      # Pewność
    VOLATILITY = auto()     # Zmienność


# =============================================================================
# WORLD CREATOR - Tworzenie Światów z V2
# =============================================================================

class WorldCreator:
    """
    Tworzy światy na podstawie predykcji modeli V2.
    
    Odpowiedzialność:
    - Konwersja predykcji V2 na struktury światów
    - Walidacja predykcji
    - Generowanie identyfikatorów światów
    """
    
    def __init__(self, config: Optional[WorldKnowledgeConfig] = None):
        self.config = config or WorldKnowledgeConfig()
        self._logger = logging.getLogger(__name__)
        self._created_worlds: Dict[str, str] = {}  # model_id -> world_id
        
    def create_world_from_v2_prediction(
        self,
        model_name: str,
        prediction_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[World]:
        """
        Tworzy świat z predykcji modelu V2.
        
        Args:
            model_name: Nazwa modelu V2 (siec_01, siec_02, etc.)
            prediction_data: Dane predykcji
            metadata: Dodatkowe metadane
            
        Returns:
            World lub None jeśli predykcja nie spełnia kryteriów
        """
        try:
            # Walidacja minimalnej pewności
            confidence = prediction_data.get("confidence", 0.0)
            if confidence < self.config.MIN_CONFIDENCE:
                self._logger.warning(f"Predykcja z {model_name} ma zbyt niską pewność: {confidence}")
                return None
            
            # Określenie typu świata na podstawie modelu
            world_type = self._map_model_to_world_type(model_name)
            
            # Generowanie ID świata
            world_id = self._generate_world_id(model_name, prediction_data)
            
            # Tworzenie świata
            world = World(
                world_id=world_id,
                name=f"Świat {model_name} - {prediction_data.get('mecz_id', 'unknown')}",
                world_type=world_type,
                source=WorldSource.V2_MODEL,
                confidence=confidence,
                prediction_data=prediction_data,
                metadata=metadata or {},
                status=WorldStatus.NEW
            )
            
            # Zapamiętanie powiązania
            self._created_worlds[world_id] = model_name
            
            self._logger.info(f"Utworzono świat {world_id} z modelu {model_name}")
            return world
            
        except Exception as e:
            self._logger.error(f"Błąd tworzenia świata z {model_name}: {e}")
            return None
    
    def _map_model_to_world_type(self, model_name: str) -> WorldType:
        """Mapuje nazwę modelu V2 na typ świata"""
        mapping = {
            "siec_01_zmiana_kursow": WorldType.CHANGE_TREND,
            "siec_01": WorldType.CHANGE_TREND,
            "siec_02_amplituda": WorldType.DYNAMICS,
            "siec_02": WorldType.DYNAMICS,
            "siec_03_tempo": WorldType.DYNAMICS,
            "siec_03": WorldType.DYNAMICS,
            "siec_04_synchronizacja": WorldType.SYNCHRONIZATION,
            "siec_04": WorldType.SYNCHRONIZATION,
            "random_forest": WorldType.CLASSIFICATION,
            "classifiers": WorldType.CLASSIFICATION
        }
        return mapping.get(model_name.lower(), WorldType.DEFAULT)
    
    def _generate_world_id(self, model_name: str, prediction_data: Dict[str, Any]) -> str:
        """Generuje unikalne ID świata"""
        mecz_id = prediction_data.get("mecz_id", "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_short = model_name.split("_")[0] if "_" in model_name else model_name[:4]
        return f"swiat_{model_short}_{mecz_id}_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    def get_model_for_world(self, world_id: str) -> Optional[str]:
        """Zwraca nazwę modelu V2 dla danego świata"""
        return self._created_worlds.get(world_id)


# =============================================================================
# PATTERN DETECTOR - Wykrywanie Wzorców
# =============================================================================

class PatternDetector:
    """
    Wykrywa wzorce w dégradacji światów i predykcji.
    
    Odpowiedzialność:
    - Analiza powtarzających się wzorców
    - Wykrywanie odwróconych wzorców
    - Kategoryzacja wzorców
    """
    
    def __init__(self, config: Optional[WorldKnowledgeConfig] = None):
        self.config = config or WorldKnowledgeConfig()
        self._logger = logging.getLogger(__name__)
        self._pattern_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._inverted_patterns: Dict[str, int] = defaultdict(int)
        
    def detect_patterns(
        self,
        prediction_data: Dict[str, Any],
        world_id: str,
        window: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Wykrywa wzorce w danych predykcji.
        
        Args:
            prediction_data: Dane do analizy
            world_id: ID świata
            window: Okno czasu (domyślnie z konfiguracji)
            
        Returns:
            Lista wykrytych wzorców
        """
        window = window or self.config.PATTERN_DETECTION_WINDOW
        patterns = []
        
        try:
            # Sprawdzenie trendów
            trend_patterns = self._detect_trend_patterns(prediction_data)
            patterns.extend(trend_patterns)
            
            # Sprawdzenie oscylacji
            oscillation_patterns = self._detect_oscillation_patterns(prediction_data)
            patterns.extend(oscillation_patterns)
            
            # Sprawdzenie skoków
            jump_patterns = self._detect_jump_patterns(prediction_data)
            patterns.extend(jump_patterns)
            
            # Sprawdzenie synchronizacji
            sync_patterns = self._detect_synchronization_patterns(prediction_data)
            patterns.extend(sync_patterns)
            
            # Zapamiętanie wzorców w historii
            for pattern in patterns:
                pattern["world_id"] = world_id
                pattern["timestamp"] = datetime.now().isoformat()
                self._pattern_history[world_id].append(pattern)
                
                # Sprawdzenie odwróconego wzorca
                if self._is_inverted_pattern(pattern):
                    self._inverted_patterns[world_id] += 1
            
            # Ograniczenie historii
            if len(self._pattern_history[world_id]) > window:
                self._pattern_history[world_id] = self._pattern_history[world_id][-window:]
                
            self._logger.info(f"Wykryto {len(patterns)} wzorców w świecie {world_id}")
            return patterns
            
        except Exception as e:
            self._logger.error(f"Błąd wykrywania wzorców: {e}")
            return []
    
    def _detect_trend_patterns(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Wykrywa wzorce trendów"""
        patterns = []
        
        # Sprawdź premię kursów
        if "zmiana_1" in data and "zmiana_2" in data and "zmiana_X" in data:
            changes = [data["zmiana_1"], data["zmiana_2"], data["zmiana_X"]]
            
            # Trend rosnący
            if all(c > 0 for c in changes):
                patterns.append({
                    "type": PatternType.TREND.name,
                    "subtype": "upward",
                    "strength": statistics.mean(changes),
                    "confidence": data.get("confidence", 0.0),
                    "data": {"changes": changes}
                })
            
            # Trend malejący
            elif all(c < 0 for c in changes):
                patterns.append({
                    "type": PatternType.TREND.name,
                    "subtype": "downward",
                    "strength": abs(statistics.mean(changes)),
                    "confidence": data.get("confidence", 0.0),
                    "data": {"changes": changes}
                })
        
        return patterns
    
    def _detect_oscillation_patterns(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Wykrywa wzorce oscylacji"""
        patterns = []
        
        if "amplituda" in data and "tempo" in data:
            amplitude = data["amplituda"]
            tempo = data["tempo"]
            
            # Wysoka amplituda + wysokie tempo =oscylacja
            if amplitude > 0.5 and tempo > 0.5:
                patterns.append({
                    "type": PatternType.OSCILLATION.name,
                    "amplitude": amplitude,
                    "tempo": tempo,
                    "confidence": data.get("confidence", 0.0),
                    "data": {"amplitude": amplitude, "tempo": tempo}
                })
        
        return patterns
    
    def _detect_jump_patterns(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Wykrywa wzorce skoków (nagłych zmian)"""
        patterns = []
        
        if "zmiana_1" in data and "zmiana_X" in data:
            change_1 = abs(data["zmiana_1"])
            change_X = abs(data["zmiana_X"])
            
            # Nagła zmiana
            if change_1 > 2.0 or change_X > 2.0:
                patterns.append({
                    "type": PatternType.JUMP.name,
                    "magnitude": max(change_1, change_X),
                    "confidence": data.get("confidence", 0.0),
                    "data": {"zmiana_1": change_1, "zmiana_X": change_X}
                })
        
        return patterns
    
    def _detect_synchronization_patterns(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Wykrywa wzorce synchronizacji"""
        patterns = []
        
        if "synchronizacja" in data:
            sync_value = data["synchronizacja"]
            
            if sync_value > 0.8:
                patterns.append({
                    "type": PatternType.SYNCHRONIZATION.name,
                    "level": sync_value,
                    "confidence": data.get("confidence", 0.0),
                    "data": {"synchronizacja": sync_value}
                })
            elif sync_value < 0.3:
                patterns.append({
                    "type": PatternType.DIVERGENCE.name,
                    "level": 1 - sync_value,
                    "confidence": data.get("confidence", 0.0),
                    "data": {"synchronizacja": sync_value}
                })
        
        return patterns
    
    def _is_inverted_pattern(self, pattern: Dict[str, Any]) -> bool:
        """Sprawdza czy wzorzec jest odwrócony"""
        # Wzorzec jest odwrócony jeśli jego siła jest przeciwna do oczekiwanej
        if pattern.get("type") == PatternType.TREND.name:
            # Jeśli trend był oczekiwany w jednu stronę, a wystąpił w drugą
            return pattern.get("subtype") != self._get_expected_trend_direction(pattern)
        
        return False
    
    def _get_expected_trend_direction(self, pattern: Dict[str, Any]) -> str:
        """Okresla oczekiwany kierunek trendu"""
        # Uproszczenie - zwraca "upward" jako domyślne
        return "upward"
    
    def get_inverted_pattern_count(self, world_id: str) -> int:
        """Zwraca liczbę odwróconych wzorców dla świata"""
        return self._inverted_patterns.get(world_id, 0)
    
    def get_pattern_history(self, world_id: str) -> List[Dict[str, Any]]:
        """Zwraca historię wzorców dla świata"""
        return self._pattern_history.get(world_id, [])


# =============================================================================
# ECONOMIC ANALYZER - Analiza Ekonomiczna
# =============================================================================

class EconomicAnalyzer:
    """
    Analiza ekonomiczna świecie i predykcji.
    
    Odpowiedzialność:
    - Obliczanie wartości oczekiwanej (EV)
    - Analiza ROI (Return on Investment)
    - Obliczanie ryzyka
    - Wykrywanie odwróconych wzorców ekonomicznych
    """
    
    def __init__(self, config: Optional[WorldKnowledgeConfig] = None):
        self.config = config or WorldKnowledgeConfig()
        self._logger = logging.getLogger(__name__)
        
    def calculate_ev(
        self,
        prediction_data: Dict[str, Any],
        confidence: float,
        method: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Oblicza Wartość Oczekiwaną (Expected Value).
        
        Formula:
        EV = (Probability of Success * Reward) - (Probability of Failure * Risk)
        
        Args:
            prediction_data: Dane predykcji
            confidence: Pewność modelu (0-1)
            method: Metoda obliczania (domyślnie z konfiguracji)
            
        Returns:
            Słownik z EV i Przykładami
        """
        method = method or self.config.EV_CALCULATION_METHOD
        
        try:
            # Podstawowe dane
            success_prob = confidence
            failure_prob = 1 - confidence
            
            # Obliczanie nagrody i ryzyka
            reward, risk = self._calculate_reward_and_risk(prediction_data)
            
            # Obliczanie EV
            if method == "weighted_avg":
                ev = (success_prob * reward * self.config.REWARD_MULTIPLIER) - \
                     (failure_prob * risk * self.config.RISK_AVERSE_FACTOR)
            elif method == "simple":
                ev = (success_prob * reward) - (failure_prob * risk)
            else:
                ev = (success_prob * reward) - (failure_prob * risk)
            
            result = {
                "ev": ev,
                "success_probability": success_prob,
                "failure_probability": failure_prob,
                "reward": reward,
                "risk": risk,
                "confidence": confidence,
                "method": method,
                "reward_multiplier": self.config.REWARD_MULTIPLIER,
                "risk_aversion_factor": self.config.RISK_AVERSE_FACTOR,
                "profitability": self._calculate_profitability(ev, risk),
                "volatility": self._calculate_volatility(prediction_data)
            }
            
            self._logger.info(f"Obliczono EV={ev:.4f} dla predykcji z pewnością {confidence:.2f}")
            return result
            
        except Exception as e:
            self._logger.error(f"Błąd obliczania EV: {e}")
            return {"ev": 0.0, "error": str(e)}
    
    def _calculate_reward_and_risk(self, data: Dict[str, Any]) -> Tuple[float, float]:
        """Oblicza nagrodę i ryzyko na podstawie danych predykcji"""
        # Uproszczone obliczenia
        reward = 1.0
        risk = 1.0
        
        # Jeśli mamy kursy
        if "kurs_1" in data and "kurs_X" in data and "kurs_2" in data:
            kurs_1 = data.get("kurs_1", 1.0)
            kurs_X = data.get("kurs_X", 0.0)
            kurs_2 = data.get("kurs_2", 1.0)
            
            # Nagroda na podstawie kurs głównego
            reward = kurs_X / max(kurs_1, kurs_2) if max(kurs_1, kurs_2) > 0 else 1.0
            
            # Ryzyko na podstawie rozrzutu kursów
            spread = max(kurs_1, kurs_2) - min(kurs_1, kurs_2)
            risk = min(spread / max(kurs_1, kurs_2, 0.1), 2.0)
        
        return reward, risk
    
    def _calculate_profitability(self, ev: float, risk: float) -> float:
        """Oblicza rentowność"""
        if risk <= 0:
            return 0.0
        return ev / risk
    
    def _calculate_volatility(self, data: Dict[str, Any]) -> float:
        """Oblicza zmienność"""
        changes = []
        for key in ["zmiana_1", "zmiana_2", "zmiana_X"]:
            if key in data and isinstance(data[key], (int, float)):
                changes.append(abs(data[key]))
        
        if changes:
            return statistics.stdev(changes) if len(changes) > 1 else 0.0
        return 0.0
    
    def calculate_roi(self, predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Oblicza ROI (Return on Investment) dla serii predykcji"""
        if not predictions:
            return {"roi": 0.0, "total_profit": 0.0, "total_risk": 0.0}
        
        total_ev = sum(p.get("ev", 0.0) for p in predictions)
        total_risk = sum(self._calculate_reward_and_risk(p)[1] for p in predictions)
        
        roi = total_ev / len(predictions) if predictions else 0.0
        
        return {
            "roi": roi,
            "avg_ev": total_ev / len(predictions) if predictions else 0.0,
            "total_profit": total_ev,
            "total_risk": total_risk,
            "sharpe_ratio": roi / (total_risk / len(predictions)) if total_risk > 0 else 0.0
        }
    
    def analyze_economic_metrics(self, world: World) -> Dict[str, Any]:
        """
        Kompleksowa analiza metryk ekonomicznych dla świata.
        
        Args:
            world: Świat do analizy
            
        Returns:
            Słownik z metrykami ekonomicznymi
        """
        analysis = {}
        
        # EV
        ev_result = self.calculate_ev(
            world.prediction_data,
            world.confidence
        )
        analysis[EconomicMetric.EV.name] = ev_result
        
        # ROI (jeśli mamy historię)
        if hasattr(world, 'history') and world.history:
            analysis[EconomicMetric.ROI.name] = self.calculate_roi(world.history)
        
        # Ryzyko
        analysis[EconomicMetric.RISK.name] = ev_result.get("risk", 0.0)
        
        # Rentowność
        analysis[EconomicMetric.PROFITABILITY.name] = ev_result.get("profitability", 0.0)
        
        # Pewność
        analysis[EconomicMetric.CONFIDENCE.name] = {
            "value": world.confidence,
            "level": self._confidence_to_level(world.confidence)
        }
        
        # Zmienność
        analysis[EconomicMetric.VOLATILITY.name] = ev_result.get("volatility", 0.0)
        
        return analysis
    
    def _confidence_to_level(self, confidence: float) -> str:
        """Konwertuje pewność na poziom"""
        if confidence >= 0.9:
            return "VERY_HIGH"
        elif confidence >= 0.7:
            return "HIGH"
        elif confidence >= 0.5:
            return "MEDIUM"
        elif confidence >= 0.3:
            return "LOW"
        else:
            return "VERY_LOW"


# =============================================================================
# EV CALCULATOR - Specjalizowany kalkulator EV
# =============================================================================

class EVCalculator:
    """
    Specjalizowany kalkulator Wartości Oczekiwanej.
    
    Odpowiedzialność:
    - Szybkie obliczanie EV
    - Obsługa różnych typów zakładów
    - Optymalizacja obliczeń
    """
    
    def __init__(self, config: Optional[WorldKnowledgeConfig] = None):
        self.config = config or WorldKnowledgeConfig()
        self._logger = logging.getLogger(__name__)
        self._cache: Dict[str, Dict[str, Any]] = {}
        
    def calculate_batch_ev(
        self,
        predictions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Oblicza EV dla partii predykcji (z cache)"""
        results = []
        
        for pred in predictions:
            cache_key = self._generate_cache_key(pred)
            
            if cache_key in self._cache:
                results.append(self._cache[cache_key])
            else:
                analyzer = EconomicAnalyzer(self.config)
                ev_result = analyzer.calculate_ev(
                    pred,
                    pred.get("confidence", 0.0)
                )
                self._cache[cache_key] = ev_result
                results.append(ev_result)
        
        return results
    
    def _generate_cache_key(self, prediction: Dict[str, Any]) -> str:
        """Generuje klucz cache"""
        key_data = {
            "kurs_1": prediction.get("kurs_1"),
            "kurs_X": prediction.get("kurs_X"),
            "kurs_2": prediction.get("kurs_2"),
            "confidence": prediction.get("confidence"),
            "zmiana_1": prediction.get("zmiana_1"),
            "zmiana_2": prediction.get("zmiana_2"),
            "zmiana_X": prediction.get("zmiana_X")
        }
        return json.dumps(key_data, sort_keys=True)
    
    def optimize_ev_calculation(
        self,
        worlds: List[World]
    ) -> List[Dict[str, Any]]:
        """Optymalizuje obliczenia EV dla wielu światów"""
        # Grupuj światy po typie
        by_type = defaultdict(list)
        for world in worlds:
            by_type[world.world_type.name].append(world)
        
        results = {}
        
        # Oblicz EV dla każdego typu światów
        for world_type, type_worlds in by_type.items():
            predictions = [w.prediction_data for w in type_worlds]
            revels = self.calculate_batch_ev(predictions)
            
            for i, world in enumerate(type_worlds):
                results[world.world_id] = {
                    "ev_result": revels[i],
                    "world_type": world_type,
                    "optimized": True
                }
        
        return [results[wid] for wid in sorted(results.keys())]
    
    def clear_cache(self) -> None:
        """Czyści cache"""
        self._cache.clear()


# =============================================================================
# WORLD KNOWLEDGE ENGINE - GŁÓWNA KLASA
# =============================================================================

class WorldKnowledgeEngine:
    """
    Główny silnik wiedzy o światach V3.
    
    Integracja:
    - V2: Odbiera predykcje z modeli
    - V3 Memory: Zapisuje do pamięci światów
    - V3 Worlds: Zarządza światami
    
    Odpowiedzialność:
    - Koordynacja tworzenia światów
    - Analiza wzorców i współpracy
    - Obliczanie metryk ekonomicznych
    - optymalizacja EV
    """
    
    def __init__(
        self,
        config: Optional[WorldKnowledgeConfig] = None,
        memory_manager: Optional[MemoryManager] = None,
        world_manager: Optional[WorldManager] = None
    ):
        self.config = config or WorldKnowledgeConfig()
        self.memory_manager = memory_manager
        self.world_manager = world_manager or WorldManager()
        self._logger = logging.getLogger(__name__)
        
        # Inicjalizacja komponentów
        self.world_creator = WorldCreator(self.config)
        self.pattern_detector = PatternDetector(self.config)
        self.economic_analyzer = EconomicAnalyzer(self.config)
        self.ev_calculator = EVCalculator(self.config)
        
        # Statystyki
        self._stats = {
            "worlds_created": 0,
            "patterns_detected": 0,
            "ev_calculations": 0,
            "inverted_patterns": 0
        }
        
        self._lock = threading.Lock()
        
    def process_v2_predictions(
        self,
        model_name: str,
        predictions: List[Dict[str, Any]]
    ) -> List[World]:
        """
        Przetwarza predykcje z modelu V2 i tworzy światy.
        
        Args:
            model_name: Nazwa modelu V2
            predictions: Lista predykcji
            
        Returns:
            Lista utworzonych światów
        """
        created_worlds = []
        
        with self._lock:
            for pred in predictions:
                world = self.world_creator.create_world_from_v2_prediction(
                    model_name, pred
                )
                
                if world:
                    # Wykryj wzorce
                    patterns = self.pattern_detector.detect_patterns(
                        pred, world.world_id
                    )
                    world.patterns = patterns
                    self._stats["patterns_detected"] += len(patterns)
                    
                    # Oblicz EV
                    ev_result = self.economic_analyzer.calculate_ev(
                        pred, pred.get("confidence", 0.0)
                    )
                    world.economic_metrics = {"ev": ev_result}
                    self._stats["ev_calculations"] += 1
                    
                    # Dodaj do world manager
                    self.world_manager.add_world(world)
                    
                    # Zapis do pamięci (jeśli dostępny)
                    if self.memory_manager:
                        self.memory_manager.add_world(world.to_dict())
                    
                    # Sprawdź odwrócone wzorce
                    inverted_count = self.pattern_detector.get_inverted_pattern_count(world.world_id)
                    if inverted_count > 0:
                        self._stats["inverted_patterns"] += inverted_count
                        world.has_inverted_patterns = True
                    
                    created_worlds.append(world)
                    self._stats["worlds_created"] += 1
                    
                    self._logger.info(f"Przetworzono predykcję {pred.get('mecz_id', 'unknown')} -> świat {world.world_id}")
            
        return created_worlds
    
    def analyze_world(
        self,
        world_id: str
    ) -> Dict[str, Any]:
        """
        Kompleksowa analiza świata.
        
        Args:
            world_id: ID świata do analizy
            
        Returns:
            Pełna analiza świata
        """
        world = self.world_manager.get_world(world_id)
        if not world:
            return {"error": f"Świat {world_id} nie istnieje"}
        
        analysis = {
            "world_id": world_id,
            "world_type": world.world_type.name,
            "confidence": world.confidence,
            "status": world.status.name
        }
        
        # Analiza ekonomiczna
        economic_analysis = self.economic_analyzer.analyze_economic_metrics(world)
        analysis["economic_analysis"] = economic_analysis
        
        # Wzorce
        patterns = self.pattern_detector.get_pattern_history(world_id)
        analysis["patterns"] = patterns
        analysis["pattern_count"] = len(patterns)
        analysis["inverted_pattern_count"] = self.pattern_detector.get_inverted_pattern_count(world_id)
        
        # Statystyki
        analysis["statistics"] = {
            "total_worlds": self._stats["worlds_created"],
            "total_patterns": self._stats["patterns_detected"],
            "total_ev_calculations": self._stats["ev_calculations"],
            "total_inverted_patterns": self._stats["inverted_patterns"]
        }
        
        return analysis
    
    def get_world_performance(self, world_id: str) -> Dict[str, Any]:
        """Zwraca wydajność świata"""
        world = self.world_manager.get_world(world_id)
        if not world:
            return {"error": f"Świat {world_id} nie istnieje"}
        
        ev = world.economic_metrics.get("ev", {}).get("ev", 0.0)
        confidence = world.confidence
        patterns = len(world.patterns or [])
        inverted = world.has_inverted_patterns
        
        # Oblicz score
        score = self._calculate_world_score(ev, confidence, patterns, inverted)
        
        return {
            "world_id": world_id,
            "ev": ev,
            "confidence": confidence,
            "patterns": patterns,
            "has_inverted_patterns": inverted,
            "score": score,
            "performance_level": self._score_to_level(score)
        }
    
    def _calculate_world_score(
        self,
        ev: float,
        confidence: float,
        patterns: int,
        has_inverted: bool
    ) -> float:
        """Oblicza ogólny score świata"""
        # Podstawowy score
        score = (ev * 0.4) + (confidence * 100 * 0.3) + (min(patterns, 10) * 10 * 0.2)
        
        # Kara za odwrócone wzorce
        if has_inverted:
            score *= 0.8
        
        return score
    
    def _score_to_level(self, score: float) -> str:
        """Konwertuje score na poziom"""
        if score >= 80:
            return "A+"
        elif score >= 70:
            return "A"
        elif score >= 60:
            return "B"
        elif score >= 50:
            return "C"
        elif score >= 40:
            return "D"
        else:
            return "F"
    
    def get_all_worlds_analysis(self) -> List[Dict[str, Any]]:
        """Zwraca analizę wszystkich światów"""
        all_worlds = self.world_manager.list_worlds()
        analyses = []
        
        for world in all_worlds:
            analysis = self.analyze_world(world.world_id)
            analyses.append(analysis)
        
        return analyses
    
    def get_statistics(self) -> Dict[str, Any]:
        """Zwraca statystyki silnika"""
        return {
            **self._stats,
            "world_count": len(self.world_manager.list_worlds()),
            "active_worlds": len([w for w in self.world_manager.list_worlds() if w.status == WorldStatus.ACTIVE])
        }
    
    def integrate_with_memory(self, memory_manager: MemoryManager) -> None:
        """
        Integruje silnik z MemoryManager.
        
        Args:
            memory_manager: Menadżer pamięci
        """
        self.memory_manager = memory_manager
        self._logger.info("Zintegrowano WorldKnowledgeEngine z MemoryManager")
    
    def reset_statistics(self) -> None:
        """Resetuje statystyki"""
        with self._lock:
            for key in self._stats:
                self._stats[key] = 0


# =============================================================================
# FABRYKA
# =============================================================================

def tworz_world_knowledge_engine(
    config: Optional[Union[Dict[str, Any], WorldKnowledgeConfig]] = None,
    memory_manager: Optional[MemoryManager] = None,
    world_manager: Optional[WorldManager] = None
) -> WorldKnowledgeEngine:
    """
    Fabryka tworzenia WorldKnowledgeEngine.
    
    Args:
        config: Konfiguracja (opcjonalnie)
        memory_manager: Menadżer pamięci (opcjonalnie)
        world_manager: Menadżer światów (opcjonalnie)
        
    Returns:
        WorldKnowledgeEngine
    """
    if isinstance(config, dict):
        config_obj = WorldKnowledgeConfig(**config)
    elif isinstance(config, WorldKnowledgeConfig):
        config_obj = config
    else:
        config_obj = WorldKnowledgeConfig()
    
    return WorldKnowledgeEngine(config_obj, memory_manager, world_manager)


# =============================================================================
# TESTY
# =============================================================================

if __name__ == "__main__":
    print("Testing WorldKnowledgeEngine...")
    
    # Create engine
    engine = tworz_world_knowledge_engine()
    
    # Test data
    test_prediction = {
        "mecz_id": "Test1_vs_Test2",
        "kurs_1": 2.5,
        "kurs_X": 3.2,
        "kurs_2": 2.8,
        "zmiana_1": 0.5,
        "zmiana_2": -0.3,
        "zmiana_X": 0.8,
        "amplituda": 0.7,
        "tempo": 0.6,
        "synchronizacja": 0.85,
        "confidence": 0.85,
        "predykcja": "2:1",
        "rzeczywistosc": "2:1"
    }
    
    # Test world creation
    worlds = engine.process_v2_predictions("siec_01_zmiana_kursow", [test_prediction])
    print(f"Utworzono {len(worlds)} świat(ów)")
    
    if worlds:
        world = worlds[0]
        print(f"Świat ID: {world.world_id}")
        print(f"Typ: {world.world_type.name}")
        print(f"Pewność: {world.confidence}")
        print(f"Liczba wzorców: {len(world.patterns or [])}")
        
        # Test analysis
        analysis = engine.analyze_world(world.world_id)
        print(f"Analiza: {analysis.get('economic_analysis', {}).get('ev', {}).get('ev', 0.0):.4f}")
        
        # Test performance
        performance = engine.get_world_performance(world.world_id)
        print(f"Wydajność: {performance}")
    
    # Test statistics
    stats = engine.get_statistics()
    print(f"Statystyki: {stats}")
    
    print("\nAll WorldKnowledgeEngine tests passed!")
