"""
SSI V2 Integration - Agregator wyjść modeli

Moduł odpowiedzialny za:
- Agregację predykcji z różnych modeli/sieci
- Różne strategie agregacji
- Normalizację i standaryzację wyjść

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
from collections import Counter, defaultdict
import numpy as np


# =============================================================================
# KONFIGURACJA AGREGATORA
# =============================================================================

@dataclass
class AggregationConfig:
    """Konfiguracja agregatora"""
    
    # Metoda agregacji
    METHOD: str = "weighted_avg"  # weighted_avg, max_confidence, voting, consensus
    
    # Wagi dla różnych typów modeli
    WEIGHTS_TREND: float = 1.0
    WEIGHTS_CURSE: float = 1.0
    WEIGHTS_CLASSIFIER: float = 1.2
    WEIGHTS_RANDOM_FOREST: float = 1.1
    
    # Ustawienia głosowania
    VOTING_THRESHOLD: float = 0.5  # Minimalny próg do akceptacji wynik
    CONSENSUS_THRESHOLD: float = 0.6  # Poziom konsensusu
    
    # Ustawienia normalizacji
    NORMALIZE_CONFIDENCE: bool = True
    
    # Ustawienia zaawansowane
    USE_GROUP_AGGREGATION: bool = True  # Agreguj najpierw w grupach, potem między grupami
    CONSIDER_VARIANCE: bool = False  # Uwzględniaj wariancję w agregacji
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "METHOD": self.METHOD,
            "WEIGHTS_TREND": self.WEIGHTS_TREND,
            "WEIGHTS_CURSE": self.WEIGHTS_CURSE,
            "WEIGHTS_CLASSIFIER": self.WEIGHTS_CLASSIFIER,
            "WEIGHTS_RANDOM_FOREST": self.WEIGHTS_RANDOM_FOREST,
            "VOTING_THRESHOLD": self.VOTING_THRESHOLD,
            "CONSENSUS_THRESHOLD": self.CONSENSUS_THRESHOLD,
            "NORMALIZE_CONFIDENCE": self.NORMALIZE_CONFIDENCE,
            "USE_GROUP_AGGREGATION": self.USE_GROUP_AGGREGATION,
            "CONSIDER_VARIANCE": self.CONSIDER_VARIANCE
        }


# =============================================================================
# AGREGOWANY WYNIK
# =============================================================================

@dataclass
class AggregatedPrediction:
    """Agregowany wynik predykcji"""
    
    # Wynik końcowy
    wynik_agregowany: str
    confidence_agregowany: float
    
    # Metadane
    id_agregacji: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    metoda_agregacji: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Składniki
    predykcje_skladowe: Dict[str, Any] = field(default_factory=dict)
    rozklad_grup: Dict[str, float] = field(default_factory=dict)  # {grupa: suma_confidence}
    rozklad_wynikow: Dict[str, float] = field(default_factory=dict)  # {wynik: suma_confidence}
    
    # Statystyki
    licznosc_predykcji: int = 0
    sredni_confidence: float = 0.0
    wariancja_confidence: float = 0.0
    konsensus: float = 0.0  # [0, 1] - poziom zgody między modelami
    
    # Grupa wyniku
    grupa_agregowana: str = field(init=False)
    
    def __post_init__(self):
        self.grupa_agregowana = self._get_grupa(self.wynik_agregowany)
    
    @staticmethod
    def _get_grupa(wynik: str) -> str:
        """Pobierz grupę wyniku"""
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
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id_agregacji": self.id_agregacji,
            "wynik_agregowany": self.wynik_agregowany,
            "confidence_agregowany": round(self.confidence_agregowany, 4),
            "grupa_agregowana": self.grupa_agregowana,
            "metoda_agregacji": self.metoda_agregacji,
            "licznosc_predykcji": self.licznosc_predykcji,
            "sredni_confidence": round(self.sredni_confidence, 4),
            "konsensus": round(self.konsensus, 4),
            "rozklad_grup": {k: round(v, 4) for k, v in self.rozklad_grup.items()},
            "rozklad_wynikow": {k: round(v, 4) for k, v in self.rozklad_wynikow.items()},
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AggregatedPrediction":
        return cls(
            wynik_agregowany=data.get("wynik_agregowany", "0:0"),
            confidence_agregowany=float(data.get("confidence_agregowany", 0.5)),
            metoda_agregacji=data.get("metoda_agregacji", ""),
            predykcje_skladowe=data.get("predykcje_skladowe", {}),
            rozklad_grup=data.get("rozklad_grup", {}),
            rozklad_wynikow=data.get("rozklad_wynikow", {}),
            licznosc_predykcji=data.get("licznosc_predykcji", 0),
            sredni_confidence=float(data.get("sredni_confidence", 0.0)),
            wariancja_confidence=float(data.get("wariancja_confidence", 0.0)),
            konsensus=float(data.get("konsensus", 0.0))
        )


# =============================================================================
# AGREGATOR WYJŚĆ MODELI
# =============================================================================

class ModelOutputAggregator:
    """
    Agregator wyjść z różnych modeli/sieci.
    
    Obsługuje:
    - Agregację ważoną
    - Głosowanie
    - Konsensus
    - Agregację w grupach wyników
    """
    
    def __init__(self, config: Optional[AggregationConfig] = None):
        self.config = config or AggregationConfig()
    
    # =========================================================================
    # GŁÓWNA METODA AGREGACJI
    # =========================================================================
    
    def agreguj(self, predictions: List[Dict[str, Any]] | Dict[str, Any],
                model_types: Optional[Dict[str, str]] = None) -> AggregatedPrediction:
        """
        Agreguje predykcje z różnych modeli.
        
        Args:
            predictions: Lista predykcji lub słownik {model_id: predykcja}
                Każda predykcja powinna mieć:
                - wynik_predykcji: string (format "X:Y")
                - confidence: float [0, 1]
                - (opcjonalnie) model_type: string
            model_types: Opcjonalny słownik typów modeli
                {model_id: model_type} where model_type in ["trend", "curse", "classifier", "random_forest"]
        
        Returns:
            AggregatedPrediction
        """
        # Normalizuj wejście
        if isinstance(predictions, dict):
            predictions = list(predictions.values())
        
        if not predictions:
            return AggregatedPrediction(
                wynik_agregowany="0:0",
                confidence_agregowany=0.5,
                metoda_agregacji=self.config.METHOD
            )
        
        # Określ typy modeli (jeśli nie podano)
        if model_types is None:
            model_types = {}
            for pred in predictions:
                model_id = pred.get("id_modelu", "")
                model_type = pred.get("model_type", "")
                if model_type:
                    model_types[model_id] = model_type
        
        # Wybierz metodę agregacji
        if self.config.METHOD == "weighted_avg":
            return self._agreguj_weighted_avg(predictions, model_types)
        elif self.config.METHOD == "max_confidence":
            return self._agreguj_max_confidence(predictions)
        elif self.config.METHOD == "voting":
            return self._agreguj_voting(predictions)
        elif self.config.METHOD == "consensus":
            return self._agreguj_consensus(predictions)
        else:
            return self._agreguj_weighted_avg(predictions, model_types)
    
    # =========================================================================
    # METODY AGREGACJI
    # =========================================================================
    
    def _agreguj_weighted_avg(self, predictions: List[Dict[str, Any]],
                             model_types: Dict[str, str]) -> AggregatedPrediction:
        """Agregacja metodą średniej ważonej"""
        
        # Wagi modeli
        weights = {
            "trend": self.config.WEIGHTS_TREND,
            "curse": self.config.WEIGHTS_CURSE,
            "classifier": self.config.WEIGHTS_CLASSIFIER,
            "random_forest": self.config.WEIGHTS_RANDOM_FOREST
        }
        
        # Inicjalizacja rozkładów
        rozklad_grup = defaultdict(float)
        rozklad_wynikow = defaultdict(float)
        total_weighted_confidence = 0.0
        
        # Agregacja
        for pred in predictions:
            model_id = pred.get("id_modelu", "")
            model_type = model_types.get(model_id, model_types.get("", "trend"))
            weight = weights.get(model_type.lower(), 1.0)
            
            wynik = pred.get("wynik_predykcji", "0:0")
            confidence = float(pred.get("confidence", 0.5))
            
            if self.config.NORMALIZE_CONFIDENCE:
                confidence = self._normalize_confidence(confidence)
            
            weighted_confidence = confidence * weight
            grupa = self._get_grupa(wynik)
            
            rozklad_grup[grupa] += weighted_confidence
            rozklad_wynikow[wynik] += weighted_confidence
            total_weighted_confidence += weighted_confidence
        
        if total_weighted_confidence == 0:
            return AggregatedPrediction(
                wynik_agregowany="0:0",
                confidence_agregowany=0.5,
                metoda_agregacji="weighted_avg",
                rozklad_grup=dict(rozklad_grup),
                rozklad_wynikow=dict(rozklad_wynikow),
                licznosc_predykcji=len(predictions)
            )
        
        # Wybierz najlepszy wynik
        if self.config.USE_GROUP_AGGREGATION:
            # Agregacja najpierw w grupach
            grupa_wynik = max(rozklad_grup.items(), key=lambda x: x[1])[0]
            # Znajdź najlepszy wynik w grupie
            grupowe_wyniki = {k: v for k, v in rozklad_wynikow.items() 
                             if self._get_grupa(k) == grupa_wynik}
            if grupowe_wyniki:
                najlepszy_wynik = max(grupowe_wyniki.items(), key=lambda x: x[1])[0]
            else:
                najlepszy_wynik = "1:0" if grupa_wynik == "1" else ("0:1" if grupa_wynik == "2" else "0:0")
            
            confidence = rozklad_grup[grupa_wynik] / total_weighted_confidence
        else:
            # Agregacja bezpośrednia
            najlepszy_wynik = max(rozklad_wynikow.items(), key=lambda x: x[1])[0]
            confidence = rozklad_wynikow[najlepszy_wynik] / total_weighted_confidence
        
        # Oblicz statystyki
        confidences = [float(p.get("confidence", 0.5)) for p in predictions]
        sredni_conf = np.mean(confidences) if confidences else 0.0
        konsensus = self._oblicz_konsensus(predictions)
        
        return AggregatedPrediction(
            wynik_agregowany=najlepszy_wynik,
            confidence_agregowany=confidence,
            metoda_agregacji="weighted_avg",
            predykcje_skladowe={p.get("id_modelu", str(i)): p for i, p in enumerate(predictions)},
            rozklad_grup=dict(rozklad_grup),
            rozklad_wynikow=dict(rozklad_wynikow),
            licznosc_predykcji=len(predictions),
            sredni_confidence=float(sredni_conf),
            konsensus=float(konsensus)
        )
    
    def _agreguj_max_confidence(self, predictions: List[Dict[str, Any]]) -> AggregatedPrediction:
        """Agregacja metodą max confidence"""
        
        max_confidence = -1
        best_prediction = None
        
        for pred in predictions:
            confidence = float(pred.get("confidence", 0.0))
            if confidence > max_confidence:
                max_confidence = confidence
                best_prediction = pred
        
        if best_prediction is None:
            return AggregatedPrediction(
                wynik_agregowany="0:0",
                confidence_agregowany=0.5,
                metoda_agregacji="max_confidence"
            )
        
        wynik = best_prediction.get("wynik_predykcji", "0:0")
        grupa = self._get_grupa(wynik)
        
        return AggregatedPrediction(
            wynik_agregowany=wynik,
            confidence_agregowany=max_confidence,
            metoda_agregacji="max_confidence",
            predykcje_skladowe={p.get("id_modelu", str(i)): p for i, p in enumerate(predictions)},
            rozklad_grup={grupa: 1.0},
            rozklad_wynikow={wynik: max_confidence},
            licznosc_predykcji=len(predictions),
            sredni_confidence=float(np.mean([float(p.get("confidence", 0.5)) for p in predictions])),
            konsensus=1.0 if len(predictions) == 1 else 0.0
        )
    
    def _agreguj_voting(self, predictions: List[Dict[str, Any]]) -> AggregatedPrediction:
        """Agregacja metodą głosowania"""
        
        voting_wynikow = Counter()
        voting_grup = Counter()
        
        for pred in predictions:
            wynik = pred.get("wynik_predykcji", "0:0")
            confidence = float(pred.get("confidence", 0.5))
            grupa = self._get_grupa(wynik)
            
            # Głosowanie z wagą (confidence)
            voting_wynikow[wynik] += confidence
            voting_grup[grupa] += confidence
        
        if not voting_wynikow:
            return AggregatedPrediction(
                wynik_agregowany="0:0",
                confidence_agregowany=0.5,
                metoda_agregacji="voting"
            )
        
        # Znajdź najlepszy wynik
        najlepszy_wynik = voting_wynikow.most_common(1)[0][0]
        najlepsza_grupa = voting_grup.most_common(1)[0][0]
        
        roduch_votes = sum(voting_wynikow.values())
        confidence = voting_wynikow[najlepszy_wynik] / roduch_votes
        
        # Sprawdź próg głosowania
        if confidence < self.config.VOTING_THRESHOLD:
            # Jeśli nie osiągnięto progu, użyj result grupy
            najlepszy_wynik = "1:0" if najlepsza_grupa == "1" else ("0:1" if najlepsza_grupa == "2" else "0:0")
        
        confidences = [float(p.get("confidence", 0.5)) for p in predictions]
        sredni_conf = np.mean(confidences) if confidences else 0.0
        konsensus = voting_wynikow.most_common(1)[0][1] / roduch_votes
        
        return AggregatedPrediction(
            wynik_agregowany=najlepszy_wynik,
            confidence_agregowany=confidence,
            metoda_agregacji="voting",
            predykcje_skladowe={p.get("id_modelu", str(i)): p for i, p in enumerate(predictions)},
            rozklad_grup=dict(voting_grup),
            rozklad_wynikow=dict(voting_wynikow),
            licznosc_predykcji=len(predictions),
            sredni_confidence=float(sredni_conf),
            konsensus=float(konsensus)
        )
    
    def _agreguj_consensus(self, predictions: List[Dict[str, Any]]) -> AggregatedPrediction:
        """Agregacja metodą konsensusu"""
        
        # Tworzenie rozkładu
        voting = Counter()
        for pred in predictions:
            wynik = pred.get("wynik_predykcji", "0:0")
            confidence = float(pred.get("confidence", 0.5))
            voting[wynik] += confidence
        
        if not voting:
            return AggregatedPrediction(
                wynik_agregowany="0:0",
                confidence_agregowany=0.5,
                metoda_agregacji="consensus"
            )
        
        total_votes = sum(voting.values())
        
        # Sprawdź konsensus
        mamks_votes = voting.most_common(1)[0][1]
        consensus_level = mamks_votes / total_votes
        
        if consensus_level >= self.config.CONSENSUS_THRESHOLD:
            # Konsensus osiągnięty
            najlepszy_wynik = voting.most_common(1)[0][0]
            confidence = consensus_level
        else:
            # Brak konsensusu - szukaj konsensusu w grupach
            voting_grup = Counter()
            for wynik, votes in voting.items():
                grupa = self._get_grupa(wynik)
                voting_grup[grupa] += votes
            
            max_grupa_votes = voting_grup.most_common(1)[0][1]
            grupa_consensus = voting_grup.most_common(1)[0][0]
            grupa_consensus_level = max_grupa_votes / total_votes
            
            if grupa_consensus_level >= self.config.CONSENSUS_THRESHOLD:
                # Konsensus na poziomie grupy
                najlepszy_wynik = self._get_default_for_grupa(grupa_consensus)
                confidence = grupa_consensus_level
            else:
                # Brak konsensusu - użyj średniej ważonej
                result = self._agreguj_weighted_avg(predictions, {})
                return AggregatedPrediction(
                    wynik_agregowany=result.wynik_agregowany,
                    confidence_agregowany=result.confidence_agregowany * 0.8,  # penalizacja za brak konsensusu
                    metoda_agregacji="consensus_fallback",
                    predykcje_skladowe=result.predykcje_skladowe,
                    rozklad_grup=result.rozklad_grup,
                    rozklad_wynikow=result.rozklad_wynikow,
                    licznosc_predykcji=result.licznosc_predykcji,
                    sredni_confidence=result.sredni_confidence,
                    konsensus=consensus_level
                )
        
        confidences = [float(p.get("confidence", 0.5)) for p in predictions]
        sredni_conf = np.mean(confidences) if confidences else 0.0
        
        return AggregatedPrediction(
            wynik_agregowany=najlepszy_wynik,
            confidence_agregowany=confidence,
            metoda_agregacji="consensus",
            predykcje_skladowe={p.get("id_modelu", str(i)): p for i, p in enumerate(predictions)},
            rozklad_grup={self._get_grupa(w): v for w, v in voting.items()},
            rozklad_wynikow=dict(voting),
            licznosc_predykcji=len(predictions),
            sredni_confidence=float(sredni_conf),
            konsensus=float(consensus_level)
        )
    
    # =========================================================================
    # METODY POMOCNICZE
    # =========================================================================
    
    @staticmethod
    def _get_grupa(wynik: str) -> str:
        """Pobierz grupę wyniku"""
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
    def _get_default_for_grupa(grupa: str) -> str:
        """Zwraca domyślny wynik dla grupy"""
        if grupa == "1":
            return "1:0"
        elif grupa == "2":
            return "0:1"
        else:
            return "0:0"
    
    @staticmethod
    def _normalize_confidence(confidence: float) -> float:
        """Normalizuje confidence do zakresu [0, 1]"""
        return max(0.0, min(1.0, confidence))
    
    def _oblicz_konsensus(self, predictions: List[Dict[str, Any]]) -> float:
        """Oblicza poziom konsensusu między predykcjami"""
        if len(predictions) <= 1:
            return 1.0
        
        # Oblicz zgodność par
        agreements = 0
        total_pairs = 0
        
        for i in range(len(predictions)):
            for j in range(i + 1, len(predictions)):
                wynik_i = predictions[i].get("wynik_predykcji", "0:0")
                wynik_j = predictions[j].get("wynik_predykcji", "0:0")
                
                # Porównaj grupy
                grupa_i = self._get_grupa(wynik_i)
                grupa_j = self._get_grupa(wynik_j)
                
                if grupa_i == grupa_j:
                    agreements += 1
                
                total_pairs += 1
        
        if total_pairs == 0:
            return 0.0
        
        return agreements / total_pairs
    
    # =========================================================================
    # AGREGACJA W CZASIE (dla wielu predykcji tego samego meczu)
    # =========================================================================
    
    def agreguj_w_czasie(self, predictions_sequence: List[Dict[str, Any]]) -> AggregatedPrediction:
        """
        Agreguje wielokrotne predykcje tego samego meczu w czasie.
        
        Args:
            predictions_sequence: Sekwencja predykcji dla jednego meczu
                (np. z różnych momentów czasu)
        
        Returns:
            AggregatedPrediction
        """
        if not predictions_sequence:
            return AggregatedPrediction(
                wynik_agregowany="0:0",
                confidence_agregowany=0.5,
                metoda_agregacji="temporal"
            )
        
        # Agregacja temporalna - średnia ważona z uwzględnieniem czasu
        temporal_weights = self._oblicz_wagi_temporalne(predictions_sequence)
        
        weighted_votes = Counter()
        total_weight = 0.0
        
        for i, pred in enumerate(predictions_sequence):
            weight = temporal_weights[i]
            wynik = pred.get("wynik_predykcji", "0:0")
            confidence = float(pred.get("confidence", 0.5))
            
            weighted_votes[wynik] += confidence * weight
            total_weight += weight
        
        if total_weight == 0:
            return AggregatedPrediction(
                wynik_agregowany="0:0",
                confidence_agregowany=0.5,
                metoda_agregacji="temporal"
            )
        
        # Normalizuj wagi
        for w in weighted_votes:
            weighted_votes[w] /= total_weight
        
        najlepszy_wynik = weighted_votes.most_common(1)[0][0]
        najlepszy_confidence = weighted_votes[najlepszy_wynik]
        
        return AggregatedPrediction(
            wynik_agregowany=najlepszy_wynik,
            confidence_agregowany=najlepszy_confidence,
            metoda_agregacji="temporal",
            predykcje_skladowe={str(i): p for i, p in enumerate(predictions_sequence)},
            licznosc_predykcji=len(predictions_sequence),
            sredni_confidence=float(np.mean([float(p.get("confidence", 0.5)) for p in predictions_sequence]))
        )
    
    def _oblicz_wagi_temporalne(self, predictions_sequence: List[Dict[str, Any]]) -> List[float]:
        """Oblicza wagi temporalne (im nowsza predykcja, tym większa waga)"""
        if not predictions_sequence:
            return []
        
        if len(predictions_sequence) == 1:
            return [1.0]
        
        # Spróbuj pobrać timestamps
        timestamps = []
        for pred in predictions_sequence:
            ts_str = pred.get("timestamp", "")
            if ts_str:
                try:
                    if isinstance(ts_str, str):
                        from datetime import datetime
                        ts = datetime.fromisoformat(ts_str)
                    else:
                        ts = ts_str
                    timestamps.append(ts)
                except:
                    timestamps.append(None)
            else:
                timestamps.append(None)
        
        if all(ts is None for ts in timestamps):
            # Brak timestamps - równe wagi
            return [1.0] * len(predictions_sequence)
        
        # Uzupełnij brakujące timestamps
        for i, ts in enumerate(timestamps):
            if ts is None:
                timestamps[i] = datetime.now()
        
        # Najnowsza prediccja ma największą wagę
        max_ts = max(timestamps)
        min_ts = min(timestamps)
        
        if max_ts == min_ts:
            return [1.0] * len(timestamps)
        
        # Wagi liniowe wg odstępu od najnowszej
        weights = []
        for ts in timestamps:
            diff = (max_ts - ts).total_seconds()
            max_diff = (max_ts - min_ts).total_seconds()
            weight = 1.0 - (diff / max_diff) * 0.5  # Od 0.5 do 1.0
            weights.append(max(0.1, weight))  # Minimum 0.1
        
        return weights


# =============================================================================
# FABRYKA
# =============================================================================

def tworz_agregator(config: Optional[Dict[str, Any]] = None) -> ModelOutputAggregator:
    """
    Fabryka tworzących agregator.
    
    Args:
        config: Opcjonalna konfiguracja (dict lub AggregationConfig)
        
    Returns:
        ModelOutputAggregator
    """
    if isinstance(config, dict):
        config_obj = AggregationConfig(**config)
    elif isinstance(config, AggregationConfig):
        config_obj = config
    else:
        config_obj = AggregationConfig()
    
    return ModelOutputAggregator(config_obj)


# =============================================================================
# TESTY
# =============================================================================

if __name__ == "__main__":
    print("Testing ModelOutputAggregator...")
    
    # Tworzenie agregatora
    aggregator = tworz_agregator()
    
    # Testowe predykcje
    predictions = [
        {"id_modelu": "siec_01", "wynik_predykcji": "2:1", "confidence": 0.8, "model_type": "trend"},
        {"id_modelu": "siec_02", "wynik_predykcji": "1:0", "confidence": 0.7, "model_type": "trend"},
        {"id_modelu": "siec_03", "wynik_predykcji": "2:1", "confidence": 0.9, "model_type": "curse"},
        {"id_modelu": "siec_04", "wynik_predykcji": "3:1", "confidence": 0.6, "model_type": "classifier"},
        {"id_modelu": "siec_05", "wynik_predykcji": "2:0", "confidence": 0.85, "model_type": "random_forest"}
    ]
    
    # Testowie różnych metod
    methods = ["weighted_avg", "max_confidence", "voting", "consensus"]
    
    for method in methods:
        config = AggregationConfig(METHOD=method)
        agg = ModelOutputAggregator(config)
        result = agg.agreguj(predictions)
        print(f"{method}: {result.wynik_agregowany} (conf: {result.confidence_agregowany:.3f}, konsensus: {result.konsensus:.3f})")
    
    print("\nAll ModelOutputAggregator tests passed!")
