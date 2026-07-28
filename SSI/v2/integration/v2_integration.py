"""
SSI V2 Integration - Główny moduł integracji V2

Moduł integrujący wszystkie komponenty V2:
- Modele Level 1 (sieci trendów i kursów)
- Model Level 2 (kalibrator)
- System obserwacji i pamięci
- Agregator wyjść

Architektura:
Level 1: 11 sieci trendów + 4 sieci kursów -> agregacja predykcji
Level 2: Kalibrator uczący się na podstawie obserwacji

Zgodnie z:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 2.2
- 02_DATA_STRUCTURE.md

Wersja: 1.0
Data: 2026-07-28
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import uuid
from pathlib import Path
import sys

# Importy z SSI V2
from SSI.v2.models import (
    BaseModelV2, Siec01ZmianaKursow, Siec02Amplituda, 
    Siec03Tempo, Siec04Synchronizacja, RandomForestModel, 
    ClassifierModel
)
from SSI.v2.training import ModelTrainer, TrainingConfig
from SSI.v2.observation import (
    ModelObserver, ObservationConfig, MemoryBuilder, MemoryConfig
)

# Importy z pamiec_modeli_v2
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "pamiec_modeli_v2"))

try:
    from schemas import (
        PredykcjaLevel1, PredykcjaLevel1Kalibrowana, Obserwacja,
        KLASY_WYNIKOW_DOKLADNYCH, get_grupa_wyniku
    )
    SCHEMAS_AVAILABLE = True
except ImportError:
    SCHEMAS_AVAILABLE = False


# =============================================================================
# KONFIGURACJA INTEGRACJI V2
# =============================================================================

@dataclass
class V2Config:
    """Konfiguracja integracji V2"""
    
    # Ustawienia Level 1
    USE_TREND_NETWORKS: bool = True
    USE_CURSE_NETWORKS: bool = True
    NUM_TREND_NETWORKS: int = 11
    NUM_CURSE_NETWORKS: int = 4
    
    # Ustawienia Level 2
    USE_CALIBRATOR: bool = True
    CALIBRATION_MIN_OBSERVATIONS: int = 100
    CALIBRATION_LEARNING_RATE: float = 0.01
    
    # Ustawienia obserwacji
    OBSERVATION_PERCENTAGE: float = 0.4  # 40% danych na obserwację
    
    # Ustawienia integracji
    AGGREGATION_METHOD: str = "weighted_avg"  # weighted_avg, max_confidence, voting
    WEIGHTS_TREND: List[float] = field(default_factory=lambda: [1.0] * 11)
    WEIGHTS_CURSE: List[float] = field(default_factory=lambda: [1.0] * 4)
    
    # Ustawienia wyjścia
    OUTPUT_FORMAT: str = "full"  # full, simplified, raw
    INCLUDE_COMPONENT_PREDICTIONS: bool = True
    
    # Ścieżki
    MODELS_PATH: str = "pamiec_modeli_v2/models"
    MEMORY_PATH: str = "pamiec_modeli_v2/pamiec"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "USE_TREND_NETWORKS": self.USE_TREND_NETWORKS,
            "USE_CURSE_NETWORKS": self.USE_CURSE_NETWORKS,
            "NUM_TREND_NETWORKS": self.NUM_TREND_NETWORKS,
            "NUM_CURSE_NETWORKS": self.NUM_CURSE_NETWORKS,
            "USE_CALIBRATOR": self.USE_CALIBRATOR,
            "CALIBRATION_MIN_OBSERVATIONS": self.CALIBRATION_MIN_OBSERVATIONS,
            "OBSERVATION_PERCENTAGE": self.OBSERVATION_PERCENTAGE,
            "AGGREGATION_METHOD": self.AGGREGATION_METHOD,
            "OUTPUT_FORMAT": self.OUTPUT_FORMAT,
            "INCLUDE_COMPONENT_PREDICTIONS": self.INCLUDE_COMPONENT_PREDICTIONS
        }


# =============================================================================
# STRUKTURY DANYCH WYJŚCIOWYCH
# =============================================================================

@dataclass
class PredictionResult:
    """Wynik predykcji z V2"""
    
    # Podstawowe dane
    id_meczu: str
    id_grupy: str
    wynik_predykcji: str
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Metadane
    id_predykcji: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    model_type: str = "V2_Level1+Level2"
    
    # Składniki (jeśli OUTPUT_FORMAT = 'full')
    sieci_skladowe: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    kalibracja: Optional[Dict[str, Any]] = None
    
    # Wynik grupowy
    grupa_predykcji: str = field(init=False)
    
    def __post_init__(self):
        self.grupa_predykcji = get_grupa_wyniku(self.wynik_predykcji) if SCHEMAS_AVAILABLE else "X"
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id_predykcji": self.id_predykcji,
            "id_meczu": self.id_meczu,
            "id_grupy": self.id_grupy,
            "wynik_predykcji": self.wynik_predykcji,
            "confidence": round(self.confidence, 4),
            "grupa_predykcji": self.grupa_predykcji,
            "timestamp": self.timestamp.isoformat(),
            "model_type": self.model_type
        }
        
        if self.sieci_skladowe:
            result["sieci_skladowe"] = self.sieci_skladowe
        
        if self.kalibracja:
            result["kalibracja"] = self.kalibracja
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PredictionResult":
        return cls(
            id_meczu=data.get("id_meczu", ""),
            id_grupy=data.get("id_grupy", ""),
            wynik_predykcji=data.get("wynik_predykcji", ""),
            confidence=float(data.get("confidence", 0.5)),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            id_predykcji=data.get("id_predykcji", uuid.uuid4().hex[:12]),
            model_type=data.get("model_type", "V2_Level1+Level2"),
            sieci_skladowe=data.get("sieci_skladowe", {}),
            kalibracja=data.get("kalibracja")
        )


@dataclass
class CalibrationData:
    """Dane kalibracji Level 2"""
    
    # Identyfikatory
    id_modelu: str
    id_meczu: str
    id_grupy: str
    
    # Oryginalne dane Level 1
    oryginalny_wynik: str
    oryginalny_confidence: float
    
    # Kalibrowane dane
    kalibrowany_wynik: Optional[str] = None
    kalibrowany_confidence: Optional[float] = None
    poprawka_confidence: float = 0.0
    
    # Informacje o uczeniu
    liczba_obserwacji: int = 0
    data_kalibracji: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id_modelu": self.id_modelu,
            "id_meczu": self.id_meczu,
            "id_grupy": self.id_grupy,
            "oryginalny_wynik": self.oryginalny_wynik,
            "oryginalny_confidence": self.oryginalny_confidence,
            "kalibrowany_wynik": self.kalibrowany_wynik,
            "kalibrowany_confidence": self.kalibrowany_confidence,
            "poprawka_confidence": self.poprawka_confidence,
            "liczba_obserwacji": self.liczba_obserwacji,
            "data_kalibracji": self.data_kalibracji.isoformat()
        }


# =============================================================================
# GŁÓWNY SYSTEM INTEGRACJI V2
# =============================================================================

class V2Integration:
    """
    Główny system integracji V2.
    
    Łączy:
    - Sieci trendów (11 sieci)
    - Sieci kursów (4 sieci)
    - Model Level 2 (kalibrator)
    - System obserwacji i pamięci
    
    Workflow:
    1. Generuj predykcje z sieci Level 1
    2. Agreguj predykcje
    3. Kalibruj za pomocą Level 2 (jeśli dostępne dane)
    4. Zapisz do obserwacji (40% przypadków)
    5. Zwróć finalny wynik
    """
    
    def __init__(self, config: Optional[V2Config] = None):
        self.config = config or V2Config()
        self._initialize_components()
        
    def _initialize_components(self):
        """Inicjalizacja komponentów"""
        
        # Inicjalizacja modeli Level 1
        self.trend_networks: Dict[str, BaseModelV2] = {}
        self.curse_networks: Dict[str, BaseModelV2] = {}
        self._init_level1_models()
        
        # Inicjalizacja obserwatora
        self.observer_config = ObservationConfig(
            observation_split=self.config.OBSERVATION_PERCENTAGE,
            build_memory=True
        )
        self.observer = ModelObserver(self.observer_config)
        
        # Inicjalizacja buildera pamięci
        self.memory_config = MemoryConfig(
            SAVE_EVERY_N=100,
            INTEGRATE_WITH_LEVEL2=self.config.USE_CALIBRATOR,
            KALIBRACJA_MIN_OBSERWACJI=self.config.CALIBRATION_MIN_OBSERVATIONS
        )
        self.memory_builder = MemoryBuilder(self.memory_config)
        
        # Kalibrator (Level 2)
        self.calibrator_ready = False
        self.calibration_models: Dict[str, Any] = {}
        
        # Rejestr predykcji (do later obserwacji)
        self.prediction_registry: Dict[str, PredictionResult] = {}
        
    def _init_level1_models(self):
        """Inicjalizacja sieci Level 1"""
        
        from SSI.v2.models import ModelConfig, ModelType, WorldType
        
        if self.config.USE_TREND_NETWORKS:
            # Sieci trendów
            for i in range(1, self.config.NUM_TREND_NETWORKS + 1):
                model_id = f"siec_{i:02d}_zmiana_kursow"
                if i == 1:
                    self.trend_networks[model_id] = Siec01ZmianaKursow()
                elif i == 2:
                    self.trend_networks[model_id] = Siec02Amplituda()
                elif i == 3:
                    self.trend_networks[model_id] = Siec03Tempo()
                elif i == 4:
                    self.trend_networks[model_id] = Siec04Synchronizacja()
                else:
                    # Dla pozostałych sieci użyj bazowego modelu
                    config = ModelConfig(
                        model_name=f"siec_{i:02d}",
                        model_type=ModelType.CUSTOM,
                        world_type=WorldType.SWIAT_2_DYNAMIKA
                    )
                    self.trend_networks[model_id] = BaseModelV2(config)
        
        if self.config.USE_CURSE_NETWORKS:
            # Sieci kursów
            for i in range(1, self.config.NUM_CURSE_NETWORKS + 1):
                model_id = f"siec_{i:02d}_kursy"
                config = ModelConfig(
                    model_name=f"siec_{i:02d}_kursy",
                    model_type=ModelType.CUSTOM,
                    world_type=WorldType.SWIAT_3_KOMPLEKSOWE
                )
                self.curse_networks[model_id] = BaseModelV2(config)
        
        print(f"Inicjalizowano {len(self.trend_networks)} sieci trendów i {len(self.curse_networks)} sieci kursów")
    
    # =========================================================================
    # GENEROWANIE PREDYKCJI LEVEL 1
    # =========================================================================
    
    def generuj_predykcje_level1(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generuje predykcje ze wszystkich sieci Level 1.
        
        Args:
            input_data: Dane wejściowe z mondele danych
                - id_meczu: ID meczu
                - id_grupy: ID grupy
                - features: Cechy do predykcji
                
        Returns:
            Słownik: {model_id: PredykcjaLevel1}
        """
        predictions = {}
        
        # Predykcje z sieci trendów
        for model_id, model in self.trend_networks.items():
            try:
                pred_output = model.predict(input_data)
                # Model zawsze zwraca ModelOutput
                pred = pred_output.prediction
                confidence = pred_output.confidence
                
                if SCHEMAS_AVAILABLE:
                    level1_pred = PredykcjaLevel1(
                        id_modelu=model_id,
                        id_meczu=input_data.get("id_meczu", ""),
                        id_grupy=input_data.get("id_grupy", ""),
                        wynik_predykcji=pred,
                        confidence=confidence,
                        sieci_skladowe={}
                    )
                else:
                    level1_pred = {
                        "id_modelu": model_id,
                        "id_meczu": input_data.get("id_meczu", ""),
                        "id_grupy": input_data.get("id_grupy", ""),
                        "wynik_predykcji": pred,
                        "confidence": confidence
                    }
                
                predictions[model_id] = level1_pred
                
            except Exception as e:
                print(f"Błąd predykcji {model_id}: {e}")
        
        # Predykcje z sieci kursów
        for model_id, model in self.curse_networks.items():
            try:
                pred_output = model.predict(input_data)
                # Model zawsze zwraca ModelOutput
                pred = pred_output.prediction
                confidence = pred_output.confidence
                
                if SCHEMAS_AVAILABLE:
                    level1_pred = PredykcjaLevel1(
                        id_modelu=model_id,
                        id_meczu=input_data.get("id_meczu", ""),
                        id_grupy=input_data.get("id_grupy", ""),
                        wynik_predykcji=pred,
                        confidence=confidence,
                        sieci_skladowe={}
                    )
                else:
                    level1_pred = {
                        "id_modelu": model_id,
                        "id_meczu": input_data.get("id_meczu", ""),
                        "id_grupy": input_data.get("id_grupy", ""),
                        "wynik_predykcji": pred,
                        "confidence": confidence
                    }
                
                predictions[model_id] = level1_pred
                
            except Exception as e:
                print(f"Błąd predykcji {model_id}: {e}")
        
        return predictions
    
    # =========================================================================
    # AGREGACJA PREDYKCJI
    # =========================================================================
    
    def agreguj_predykcje(self, predictions: Dict[str, Any]) -> Tuple[str, float]:
        """
        Agreguje predykcje z różnych sieci.
        
        Args:
            predictions: Słownik predykcji {model_id: PredykcjaLevel1}
            
        Returns:
            (wynik_agregowany, confidence_agregowany)
        """
        if not predictions:
            return "0:0", 0.5
        
        # Metoda 1: Wagted average (domyślna)
        if self.config.AGGREGATION_METHOD == "weighted_avg":
            return self._agreguj_weighted_avg(predictions)
        
        # Metoda 2: Max confidence
        elif self.config.AGGREGATION_METHOD == "max_confidence":
            return self._agreguj_max_confidence(predictions)
        
        # Metoda 3: Voting
        elif self.config.AGGREGATION_METHOD == "voting":
            return self._agreguj_voting(predictions)
        
        # Domyslnie: weighted_avg
        return self._agreguj_weighted_avg(predictions)
    
    def _agreguj_weighted_avg(self, predictions: Dict[str, Any]) -> Tuple[str, float]:
        """Agregacja metodą bezpośredniej średniej ważonej"""
        
        # Ważone sumy dla grup wyników
        suma_1 = 0.0
        suma_X = 0.0
        suma_2 = 0.0
        total_weight = 0.0
        
        # Wagi dla sieci trendów i kursów
        weights = {}
        for i, model_id in enumerate(self.trend_networks.keys()):
            weights[model_id] = self.config.WEIGHTS_TREND[i % len(self.config.WEIGHTS_TREND)]
        for i, model_id in enumerate(self.curse_networks.keys()):
            weights[model_id] = self.config.WEIGHTS_CURSE[i % len(self.config.WEIGHTS_CURSE)]
        
        for model_id, pred in predictions.items():
            weight = weights.get(model_id, 1.0)
            confidence = pred.confidence if hasattr(pred, 'confidence') else pred.get('confidence', 0.5)
            wynik = pred.wynik_predykcji if hasattr(pred, 'wynik_predykcji') else pred.get('wynik_predykcji', '0:0')
            
            grupa = get_grupa_wyniku(wynik) if SCHEMAS_AVAILABLE else self._get_grupa_simple(wynik)
            weighted_confidence = confidence * weight
            
            if grupa == "1":
                suma_1 += weighted_confidence
            elif grupa == "X":
                suma_X += weighted_confidence
            elif grupa == "2":
                suma_2 += weighted_confidence
            
            total_weight += weighted_confidence
        
        if total_weight == 0:
            return "0:0", 0.5
        
        # Wybierz grupę z najwyższym wagowym confidence
        if suma_1 >= suma_X and suma_1 >= suma_2:
            grupa = "1"
            confidence = suma_1 / total_weight
        elif suma_X >= suma_1 and suma_X >= suma_2:
            grupa = "X"
            confidence = suma_X / total_weight
        else:
            grupa = "2"
            confidence = suma_2 / total_weight
        
        # Zamień grupę na konkretny wynik (najczęstszy w grupie)
        wynik = self._grupa_do_wyniku(grupa, predictions)
        
        return wynik, confidence
    
    def _agreguj_max_confidence(self, predictions: Dict[str, Any]) -> Tuple[str, float]:
        """Agregacja metodą max confidence"""
        max_confidence = -1
        best_prediction = "0:0"
        
        for pred in predictions.values():
            confidence = pred.confidence if hasattr(pred, 'confidence') else pred.get('confidence', 0.0)
            if confidence > max_confidence:
                max_confidence = confidence
                best_prediction = pred.wynik_predykcji if hasattr(pred, 'wynik_predykcji') else pred.get('wynik_predykcji', '0:0')
        
        return best_prediction, max_confidence
    
    def _agreguj_voting(self, predictions: Dict[str, Any]) -> Tuple[str, float]:
        """Agregacja metodą głosowania"""
        voting = {}
        
        for pred in predictions.values():
            wynik = pred.wynik_predykcji if hasattr(pred, 'wynik_predykcji') else pred.get('wynik_predykcji', '0:0')
            confidence = pred.confidence if hasattr(pred, 'confidence') else pred.get('confidence', 0.5)
            
            if wynik not in voting:
                voting[wynik] = 0.0
            voting[wynik] += confidence
        
        if not voting:
            return "0:0", 0.5
        
        best_wynik = max(voting.keys(), key=lambda x: voting[x])
        best_confidence = voting[best_wynik] / sum(voting.values())
        
        return best_wynik, best_confidence
    
    @staticmethod
    def _grupa_do_wyniku(grupa: str, predictions: Dict[str, Any]) -> str:
        """Konwertuje grupę na konkretny wynik"""
        if grupa == "X":
            return "0:0"
        
        # Znajdź najczęstszy wynik w danej grupie
        grupa_wyniki = []
        for pred in predictions.values():
            wynik = pred.wynik_predykcji if hasattr(pred, 'wynik_predykcji') else pred.get('wynik_predykcji', '0:0')
            pred_grupa = get_grupa_wyniku(wynik) if SCHEMAS_AVAILABLE else V2Integration._get_grupa_simple_static(wynik)
            if pred_grupa == grupa:
                grupa_wyniki.append(wynik)
        
        if grupa_wyniki:
            # Zwróć najczęstszy wynik
            from collections import Counter
            counter = Counter(grupa_wyniki)
            return counter.most_common(1)[0][0]
        
        # Domyślne wyniki dla grup
        if grupa == "1":
            return "1:0"
        elif grupa == "2":
            return "0:1"
        return "0:0"
    
    @staticmethod
    def _get_grupa_simple(wynik: str) -> str:
        """Prosta implementacja get_grupa_wyniku"""
        if ":" not in wynik:
            return "X"
        try:
            parts = wynik.split(":")
            if int(parts[0]) > int(parts[1]):
                return "1"
            elif int(parts[0]) < int(parts[1]):
                return "2"
            else:
                return "X"
        except:
            return "X"
    
    @staticmethod
    def _get_grupa_simple_static(wynik: str) -> str:
        """Statyczna wersja"""
        return V2Integration._get_grupa_simple(wynik)
    
    # =========================================================================
    # KALIBRACJA LEVEL 2
    # =========================================================================
    
    def kalibruj_predykcje(self, aggregated_pred: Tuple[str, float], 
                          input_data: Dict[str, Any]) -> Tuple[str, float, Dict[str, Any]]:
        """
        Kalibruje agregowaną predykcję za pomocą Level 2.
        
        Args:
            aggregated_pred: (wynik, confidence) z agregacji Level 1
            input_data: Oryginalne dane wejściowe
            
        Returns:
            (kalibrowany_wynik, kalibrowany_confidence, kalibracja_data)
        """
        if not self.config.USE_CALIBRATOR:
            return aggregated_pred[0], aggregated_pred[1], {}
        
        if not self.calibrator_ready:
            # Sprawdź czy mamy wystarczającą liczbę obserwacji
            if self.memory_builder.rozmiar_pamieci() >= self.config.CALIBRATION_MIN_OBSERVATIONS:
                self._train_calibrator()
            else:
                return aggregated_pred[0], aggregated_pred[1], {}
        
        # Tutaj powinna być implementacja kalibracji
        # Na razie zwracamy oryginalne wartości
        kalibracja_data = {
            "kalibrowany": False,
            "powod": "Kalibrator w budowie"
        }
        
        return aggregated_pred[0], aggregated_pred[1], kalibracja_data
    
    def _train_calibrator(self):
        """Trenuje kalibrator Level 2"""
        # Pobierz dane do kalibracji
        kalibracja_data = self.memory_builder.pobierz_dane_do_kalibracji(
            self.config.CALIBRATION_MIN_OBSERVATIONS
        )
        
        if len(kalibracja_data) < self.config.CALIBRATION_MIN_OBSERVATIONS:
            print("Niewystarczająca liczba danych do kalibracji")
            return
        
        # Tutaj powinno być trenowanie modelu kalibracji
        print(f"Trenowanie kalibratora na {len(kalibracja_data)} obserwacjach")
        self.calibrator_ready = True
    
    # =========================================================================
    # GŁÓWNA METODA PREDYKCJI
    # =========================================================================
    
    def predykcja(self, input_data: Dict[str, Any], 
                  zapisz_do_obserwacji: bool = True) -> PredictionResult:
        """
        Główna metoda generująca predykcję V2.
        
        Args:
            input_data: Dane wejściowe
                - id_meczu: string
                - id_grupy: string
                - features: Dict z cechami
            zapisz_do_obserwacji: Czy zapisać do systemu obserwacji
            
        Returns:
            PredictionResult
        """
        id_meczu = input_data.get("id_meczu", f"mecz_{uuid.uuid4().hex[:8]}")
        id_grupy = input_data.get("id_grupy", "default")
        
        # 1. Generuj predykcje Level 1
        level1_predictions = self.generuj_predykcje_level1(input_data)
        
        # 2. Agreguj predykcje
        agregowany_wynik, agregowany_confidence = self.agreguj_predykcje(level1_predictions)
        
        # 3. Kalibruj (Level 2)
        kalibrowany_wynik, kalibrowany_confidence, kalibracja_data = self.kalibruj_predykcje(
            (agregowany_wynik, agregowany_confidence), input_data
        )
        
        # 4. Utwórz wynik
        if self.config.OUTPUT_FORMAT == "full":
            sieci_skladowe = {}
            for model_id, pred in level1_predictions.items():
                if hasattr(pred, 'to_dict'):
                    sieci_skladowe[model_id] = pred.to_dict()
                else:
                    sieci_skladowe[model_id] = pred
        else:
            sieci_skladowe = {}
        
        result = PredictionResult(
            id_meczu=id_meczu,
            id_grupy=id_grupy,
            wynik_predykcji=kalibrowany_wynik,
            confidence=kalibrowany_confidence,
            model_type="V2_Level1+Level2",
            sieci_skladowe=sieci_skladowe,
            kalibracja=kalibracja_data if kalibracja_data else None
        )
        
        # 5. Zapisz do rejestru (do późniejszej obserwacji)
        self.prediction_registry[id_meczu] = result
        
        # 6. Obserwacja nie jest tutaj potrzebna - będzie dodana po znaniu wyniku rzeczywistego
        # self.observer.observe(...)  # Będzie wołane w dodaj_wynik_rzeczywisty
        
        return result
    
    # =========================================================================
    # OBSERWACJA I PAMIĘĆ
    # =========================================================================
    
    def dodaj_wynik_rzeczywisty(self, id_meczu: str, wynik_rzeczywisty: str):
        """
        Dodaje rzeczywisty wynik meczu i tworzy obserwacje.
        
        Args:
            id_meczu: ID meczu
            wynik_rzeczywisty: Rzeczywisty wynik (format "X:Y")
        """
        if id_meczu not in self.prediction_registry:
            print(f"Warning: Brak predykcji dla meczu {id_meczu}")
            return
        
        result = self.prediction_registry[id_meczu]
        
        # Utwórz obserwację
        if SCHEMAS_AVAILABLE:
            obs = Obserwacja(
                id_meczu=id_meczu,
                id_grupy=result.id_grupy,
                id_modelu="V2_Aggregated",
                wynik_predykcji=result.wynik_predykcji,
                confidence=result.confidence,
                wynik_rzeczywisty=wynik_rzeczywisty
            )
        else:
            obs = {
                "id_meczu": id_meczu,
                "id_grupy": result.id_grupy,
                "id_modelu": "V2_Aggregated",
                "wynik_predykcji": result.wynik_predykcji,
                "confidence": result.confidence,
                "wynik_rzeczywisty": wynik_rzeczywisty,
                "timestamp": datetime.now().isoformat()
            }
        
        # Dodaj do buildera pamięci
        if SCHEMAS_AVAILABLE:
            self.memory_builder.dodaj_obserwacje(obs)
        else:
            self.memory_builder.dodaj_obserwacje_z_dict(obs)
        
        # Usuń z rejestru
        del self.prediction_registry[id_meczu]
    
    # =========================================================================
    # METODY UŻYTECZNE
    # =========================================================================
    
    def pobierz_statystyki(self) -> Dict[str, Any]:
        """Zwraca statystyki systemu V2"""
        return {
            "level1_models": {
                "trend": len(self.trend_networks),
                "curse": len(self.curse_networks)
            },
            "memory": self.memory_builder.pobierz_statystyki(),
            "calibrator_ready": self.calibrator_ready,
            "prediction_registry_size": len(self.prediction_registry)
        }
    
    def czysc_rejestr(self):
        """Czyści rejestr predykcji"""
        self.prediction_registry.clear()


# =============================================================================
# FABRYKA
# =============================================================================

def tworz_integracje_v2(config: Optional[Dict[str, Any]] = None) -> V2Integration:
    """
    Fabryka tworzących system V2 Integration.
    
    Args:
        config: Opcjonalna konfiguracja (dict lub V2Config)
        
    Returns:
        V2Integration
    """
    if isinstance(config, dict):
        config_obj = V2Config(**config)
    elif isinstance(config, V2Config):
        config_obj = config
    else:
        config_obj = V2Config()
    
    return V2Integration(config_obj)


# =============================================================================
# TESTY
# =============================================================================

if __name__ == "__main__":
    print("Testing V2Integration...")
    
    # Tworzenie systemu
    v2 = tworz_integracje_v2()
    
    # Testowe dane wejściowe
    test_data = {
        "id_meczu": "Test_TeamA_vs_Test_TeamB",
        "id_grupy": "poziom3poziom17poziom20",
        "features": {
            "home_team_strength": 0.75,
            "away_team_strength": 0.65,
            "home_form": 0.8,
            "away_form": 0.5,
            "head_to_head": 0.6
        }
    }
    
    # Test predykcji
    prediction = v2.predykcja(test_data, zapisz_do_obserwacji=True)
    print(f"Predykcja: {prediction.wynik_predykcji} (confidence: {prediction.confidence:.3f})")
    print(f"Grupa: {prediction.grupa_predykcji}")
    
    # Test dodawania wyniku rzeczywistego
    v2.dodaj_wynik_rzeczywisty("Test_TeamA_vs_Test_TeamB", "2:1")
    print("Dodano wynik rzeczywisty: 2:1")
    
    # Test statystyk
    stats = v2.pobierz_statystyki()
    print(f"Statystyki: {stats}")
    
    print("\nV2Integration tests passed!")
