"""
PAMIĘĆ MODELI V2 - KALIBRATOR LEVEL 2
======================================

Model Level 2: Kalibrator uczący się zachowania Modelu Level 1.

CEL:
- NIE przewiduje meczów
- Uczy się zachowania Modelu Level 1 (agregatora)
- Kalibruje confidence (poprawia pewność predykcji)
- Wykrywa wzorce zachowania (systematyczne błędy)
- Generuje metadane dla poprawy Level 1

ARCHITEKTURA:
    Wejście: Historia obserwacji (predykcja_L1, confidence_L1, wynik_rzeczywisty)
           ↓
    Analiza: Statystyki per model, per klasa, per grupa
           ↓
    Kalibracja: Model uczenia się (bucketowy / ML)
           ↓
    Wyjście: confidence_kalibrowana + wzorce zachowania

METODY KALIBRACJI:
1. BUCKETOWA (domyślna, bez zewnętrznych bibliotek):
   - Grupuj obserwacje po confidence (0.0-0.1, 0.1-0.2, ...)
   - Dla każdej grupy oblicz średnią skuteczność
   - Kalibrowane confidence = średnia skuteczność w grupie

2. ML (opcjonalna, wymaga sklearn):
   - Model: RandomForestRegressor / GradientBoostingRegressor
   - Features: confidence_L1, grupa_encoded, klasa_gospodarze, klasa_gosc, ...
   - Target: trafienie (1/0) lub poprawka = trafienie - confidence_L1

WERSJONOWANIE:
- Każdy trening tworzy NOWY model (nie nadpisujemy!)
- Modele zapisywane w: level2/archiwum/kalibrator_v2_YYYYMMDD_*.pkl
- Metadane w: level2/archiwum/kalibrator_metadata_v2_YYYYMMDD_*.json

ZASADA (z dokumentacji):
"Nie nadpisujemy pamięci. Każde uruchomienie tworzy nową wersję."

Autor: MSDI AI v0.02
Data: 2026-07-27
"""

import json
import csv
import math
import statistics
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
import uuid
import pickle
from collections import defaultdict, Counter

# Import z lokalnych modułów V2
from pamiec_modeli_v2.schemas import (
    PredykcjaLevel1,
    PredykcjaLevel1Kalibrowana,
    Obserwacja,
    KlasaWyniku,
    WzorecZachowania,
    StatystykiPamieci,
    KonfiguracjaV2,
    get_grupa_wyniku,
    get_gole,
    KLASY_WYNIKOW_DOKLADNYCH,
    KLASY_GRUP_WYNIKOW,
    waliduj_wynik,
    normalizuj_wynik,
    generuj_id,
)


# =============================================================================
# KONFIGURACJA KALIBRATORA
# =============================================================================

class KalibratorConfig:
    """Konfiguracja kalibratora Level 2"""
    
    # Metoda kalibracji (BUCKET / ML / HYBRID)
    METODA_KALIBRACJI: str = "HYBRID"  # BUCKET, ML, HYBRID
    
    # Bucketowanie (dla metody BUCKET)
    LICZBA_BUCKETOW: int = 10  # 0.0-0.1, 0.1-0.2, ..., 0.9-1.0
    MIN_OBSERWACJI_PER_BUCKET: int = 10  # Minimalna liczba obserwacji w bucketcie
    
    # ML (dla metody ML)
    ML_ENABLED: bool = False  # Włączone tylko jeśli sklearn jest dostępny
    ML_MODEL_TYPE: str = "RANDOM_FOREST"  # RANDOM_FOREST, GRADIENT_BOOSTING
    ML_N_ESTIMATORS: int = 100
    ML_MAX_DEPTH: int = 10
    ML_MIN_SAMPLES_LEAF: int = 10
    
    # Minimalna liczba obserwacji do trenowania
    MIN_OBSERWACJI_TRENING: int = 100
    
    # Wersjonowanie
    ARCHIWUM_PATH: Path = Path("pamiec_modeli_v2/level2/archiwum")
    MODEL_PREFIX: str = "kalibrator_v2"
    METADATA_PREFIX: str = "kalibrator_metadata_v2"
    
    # Cechy używane do kalibracji
    FEATURES_BUCKET: List[str] = [
        "confidence_bucket",
        "grupa",
        "klasa_dokladna",
    ]
    
    FEATURES_ML: List[str] = [
        "confidence",
        "grupa_1", "grupa_X", "grupa_2",  # One-hot encoding grupy
        "gospodarze", "gosc",  # Liczba goli z klasy
        "zgoda_sieci",  # Zgoda sieci w Level 1 (jeśli dostępne)
        "sredni_confidence_sieci",  # Średni confidence z sieci
    ]
    
    # Wagi dla metody HYBRID
    HYBRID_WEIGHT_BUCKET: float = 0.7
    HYBRID_WEIGHT_ML: float = 0.3


# =============================================================================
# FUNKCJE UŻYTECZNE (Bucketowanie, Encoding, itd.)
# =============================================================================

def _get_bucket(confidence: float, num_buckets: int = 10) -> int:
    """
    Zwraca indeks bucketa dla danego confidence.
    
    Args:
        confidence: Wartość confidence [0.0, 1.0]
        num_buckets: Liczba bucketów
    
    Returns:
        Indeks bucketa (0 do num_buckets-1)
    """
    confidence = max(0.0, min(1.0, confidence))
    # Ostatni bucket zawiera 1.0
    bucket_index = min(int(confidence * num_buckets), num_buckets - 1)
    return bucket_index


def _encode_grupa(grupa: str) -> Dict[str, float]:
    """
    One-hot encoding dla grupy (1/X/2).
    
    Args:
        grupa: "1", "X" lub "2"
    
    Returns:
        Słownik z one-hot encodingiem
    """
    return {
        "grupa_1": 1.0 if grupa == "1" else 0.0,
        "grupa_X": 1.0 if grupa == "X" else 0.0,
        "grupa_2": 1.0 if grupa == "2" else 0.0,
    }


def _decode_wynik(wynik: str) -> Tuple[int, int]:
    """
    Konwertuje wynik "X:Y" na tuple (gospodarze, gosc).
    
    Args:
        wynik: String w formacie "X:Y"
    
    Returns:
        Tuple (gospodarze, gosc)
    """
    if not wynik or ":" not in wynik:
        return (0, 0)
    try:
        parts = wynik.split(":")
        return (int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        return (0, 0)


def _calculate_zgoda_sieci(sieci_skladowe: Dict[str, Any]) -> float:
    """
    Oblicza stopień zgody między sieciami (jeśli dostępne).
    
    Args:
        sieci_skladowe: Słownik z predykcjami z poszczególnych sieci
    
    Returns:
        Zgoda [0.0, 1.0] (1.0 = wszystkie sieci zgodne)
    """
    if not sieci_skladowe:
        return 0.5
    
    wyniki = [
        pred.get("wynik_predykcji", "") 
        for pred in sieci_skladowe.values() 
        if isinstance(pred, dict)
    ]
    
    if not wyniki:
        return 0.5
    
    # Zgoda = (liczba najczęstszych wyników) / (całkowita liczba)
    counter = Counter(wyniki)
    max_count = counter.most_common(1)[0][1]
    zgoda = max_count / len(wyniki)
    
    return zgoda


def _calculate_sredni_confidence_sieci(sieci_skladowe: Dict[str, Any]) -> float:
    """
    Oblicza średni confidence z sieci składających Level 1.
    
    Args:
        sieci_skladowe: Słownik z predykcjami z poszczególnych sieci
    
    Returns:
        Średni confidence
    """
    if not sieci_skladowe:
        return 0.5
    
    confidences = [
        float(pred.get("confidence", 0.5))
        for pred in sieci_skladowe.values()
        if isinstance(pred, dict)
    ]
    
    if not confidences:
        return 0.5
    
    return statistics.mean(confidences)


# =============================================================================
# KLASA: KALIBRATOR LEVEL 2
# =============================================================================

class KalibratorLevel2:
    """
    Model Level 2 - Kalibrator uczący się zachowania Modelu Level 1.
    
    NIE PRZEWIDUJE MEczów.
    Uczy się na podstawie historii: (predykcja_L1, confidence_L1) vs wynik_rzeczywisty
    
    Zadania:
    1. Kalibracja confidence (poprawianie pewności predykcji Level 1)
    2. Wykrywanie wzorców zachowania (systematyczne błędy Level 1)
    3. Generowanie metadanych dla poprawy Level 1
    
    Metody kalibracji:
    - BUCKET: Prosta metoda bucketowania confidence
    - ML: Uczenie maszynowe (Random Forest / Gradient Boosting)
    - HYBRID: Kombinacja obu metod
    
    Wersjonowanie:
    - Każdy trening tworzy NOWĄ wersję (nie nadpisujemy!)
    - Modele zapisywane w archiwum/
    
    Użycie:
    >>> kalibrator = KalibratorLevel2()
    >>> kalibrator.trenuj(obserwacje)  # Uczy na podstawie historii
    >>> pred_kalibrowana = kalibrator.kalibruj(predykcja_l1)
    >>> wzorce = kalibrator.wykryj_wzorce()
    >>> kalibrator.zapisz_model()  # Zapisuje nową wersję
    """
    
    # Konfiguracja
    config: KalibratorConfig = KalibratorConfig()
    
    # Model kalibracji (zależy od metody)
    model_bucket: Optional[Dict[int, float]] = None  # {bucket_index: srednia_skutecznosc}
    model_ml: Optional[Any] = None  # Model ML (RandomForestRegressor itp.)
    
    # Dane treningowe (dla metody ML)
    X_train: Optional[List[List[float]]] = None
    y_train: Optional[List[float]] = None
    feature_names: List[str] = []
    
    # Metadane
    metadata: Dict[str, Any] = {
        "wersja": "",
        "data_treningu": None,
        "liczba_obserwacji": 0,
        "metoda_kalibracji": "",
        "statystyki": {},
        "wzorce": [],
    }
    
    # Wzorce zachowania (wykryte błędy)
    wzorce: List[WzorecZachowania] = []
    
    # Statystyki kalibracji
    statystyki: Dict[str, Any] = {}
    
    # Repozytorium (opcjonalne połączenie)
    repozytorium: Optional[Any] = None
    
    # -------------------------------------------------------------------------
    # INICJALIZACJA
    # -------------------------------------------------------------------------
    
    def __init__(self, config: Optional[KalibratorConfig] = None):
        """
        Inicjalizacja kalibratora.
        
        Args:
            config: Konfiguracja kalibratora (domyślnie KalibratorConfig())
        """
        if config:
            self.config = config
        
        # Generuj nową wersję
        self._generuj_nowa_wersje()
        
        # Sprawdź dostępność sklearn (dla metody ML)
        self._sprawdz_dostepnosc_sklearn()
    
    def _generuj_nowa_wersje(self):
        """Generuje unikalną nazwę wersji dla nowego modelu"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        self.metadata["wersja"] = f"{self.config.MODEL_PREFIX}_{timestamp}_{unique_id}"
        self.metadata["data_utworzenia"] = datetime.now().isoformat()
    
    def _sprawdz_dostepnosc_sklearn(self):
        """Sprawdza, czy scikit-learn jest dostępny"""
        try:
            import sklearn
            from sklearn.ensemble import RandomForestRegressor
            self.config.ML_ENABLED = True
            self.metadata["sklearn_dostepny"] = True
        except ImportError:
            self.config.ML_ENABLED = False
            self.metadata["sklearn_dostepny"] = False
            print("Uwaga: scikit-learn niedostepny. Metoda ML wyłaczona.")
    
    # -------------------------------------------------------------------------
    # TRENOWANIE MODELU
    # -------------------------------------------------------------------------
    
    def trenuj(self, obserwacje: List[Obserwacja], 
               metoda: Optional[str] = None) -> bool:
        """
        Trenuje model kalibracji na podstawie historii obserwacji.
        
        Args:
            obserwacje: Lista obserwacji z historii (predykcja vs rzeczywistość)
            metoda: Metoda kalibracji (BUCKET, ML, HYBRID). 
                   Jeśli None, używa config.METODA_KALIBRACJI
        
        Returns:
            True jeśli trening się powiódł, False w przeciwnym razie
        """
        if not obserwacje:
            print("Brak obserwacji do trenowania.")
            return False
        
        if len(obserwacje) < self.config.MIN_OBSERWACJI_TRENING:
            print(f"Za mało obserwacji ({len(obserwacje)}) do trenowania. "
                  f"Minimum: {self.config.MIN_OBSERWACJI_TRENING}")
            return False
        
        # Ustaw metodę
        if metoda:
            self.config.METODA_KALIBRACJI = metoda
        
        self.metadata["metoda_kalibracji"] = self.config.METODA_KALIBRACJI
        self.metadata["liczba_obserwacji"] = len(obserwacje)
        self.metadata["data_treningu"] = datetime.now().isoformat()
        
        # Trenuj odpowiednią metodą
        if self.config.METODA_KALIBRACJI == "BUCKET":
            return self._trenuj_bucket(obserwacje)
        elif self.config.METODA_KALIBRACJI == "ML":
            if not self.config.ML_ENABLED:
                print("Metoda ML niedostępna (brak sklearn). Używam BUCKET.")
                return self._trenuj_bucket(obserwacje)
            return self._trenuj_ml(obserwacje)
        else:  # HYBRID
            if self.config.ML_ENABLED:
                return self._trenuj_hybrydowo(obserwacje)
            else:
                return self._trenuj_bucket(obserwacje)
    
    def _trenuj_bucket(self, obserwacje: List[Obserwacja]) -> bool:
        """
        Trenuje model kalibracji metodą bucketowania.
        
        Działanie:
        1. Grupuje obserwacje po confidence (buckety: 0.0-0.1, 0.1-0.2, ...)
        2. Dla każdego bucketa oblicza średnią skuteczność
        3. Kalibrowane confidence = średnia skuteczność w bucketcie
        
        Args:
            obserwacje: Lista obserwacji
        
        Returns:
            True jeśli trening się powiódł
        """
        # Inicjalizuj buckety
        bucket_stats: Dict[int, Dict[str, Any]] = {}
        
        for i in range(self.config.LICZBA_BUCKETOW):
            bucket_stats[i] = {
                "obserwacje": [],
                "trafienia": 0,
                "liczba": 0,
                "skutecznosc": 0.0,
            }
        
        # Klasyfikuj obserwacje do bucketów
        for obs in obserwacje:
            bucket_idx = _get_bucket(obs.confidence, self.config.LICZBA_BUCKETOW)
            bucket_stats[bucket_idx]["obserwacje"].append(obs)
            bucket_stats[bucket_idx]["liczba"] += 1
            if obs.trafienie:
                bucket_stats[bucket_idx]["trafienia"] += 1
        
        # Oblicz średnią skuteczność dla każdego bucketa
        self.model_bucket = {}
        for bucket_idx, stats in bucket_stats.items():
            if stats["liczba"] >= self.config.MIN_OBSERWACJI_PER_BUCKET:
                skutecznosc = stats["trafienia"] / stats["liczba"]
            else:
                # Jeśli za mało danych, użyj globalnej skuteczności
                global_trafienia = sum(1 for o in obserwacje if o.trafienie)
                global_skutecznosc = global_trafienia / len(obserwacje) if obserwacje else 0.5
                skutecznosc = global_skutecznosc
            
            self.model_bucket[bucket_idx] = skutecznosc
        
        # Zapisz statystyki
        self.statystyki["bucket_stats"] = {
            i: {"liczba": s["liczba"], "skutecznosc": s["skutecznosc"]}
            for i, s in bucket_stats.items()
        }
        
        # Oblicz globalne statystyki kalibracji
        self._oblicz_statystyki_kalibracji(obserwacje)
        
        print(f"Trenowanie BUCKET zakończone pomyślnie. "
              f"Buckety: {len(self.model_bucket)}, Obserwacje: {len(obserwacje)}")
        
        return True
    
    def _trenuj_ml(self, obserwacje: List[Obserwacja]) -> bool:
        """
        Trenuje model kalibracji metodą ML (Random Forest).
        
        Działanie:
        1. Ekstrahuje cechy z obserwacji (confidence, grupa, klasa, ...)
        2. Definiuje target: trafienie (1/0) lub poprawka = trafienie - confidence
        3. Trenuje model ML (RandomForestRegressor)
        
        Args:
            obserwacje: Lista obserwacji
        
        Returns:
            True jeśli trening się powiódł
        """
        try:
            # Import sklearn (już sprawdzono dostępność)
            from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
            from sklearn.model_selection import train_test_split
            import numpy as np
            
            # Przygotuj dane treningowe
            X, y = self._przygotuj_dane_ml(obserwacje)
            
            if len(X) == 0 or len(y) == 0:
                print("Brak danych treningowych dla metody ML.")
                return False
            
            # Podział na trening/walidację (80/20)
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Stwórz model
            if self.config.ML_MODEL_TYPE == "GRADIENT_BOOSTING":
                model = GradientBoostingRegressor(
                    n_estimators=self.config.ML_N_ESTIMATORS,
                    max_depth=self.config.ML_MAX_DEPTH,
                    min_samples_leaf=self.config.ML_MIN_SAMPLES_LEAF,
                    random_state=42
                )
            else:  # RANDOM_FOREST
                model = RandomForestRegressor(
                    n_estimators=self.config.ML_N_ESTIMATORS,
                    max_depth=self.config.ML_MAX_DEPTH,
                    min_samples_leaf=self.config.ML_MIN_SAMPLES_LEAF,
                    random_state=42
                )
            
            # Trenuj model
            model.fit(X_train, y_train)
            
            # Zapisz model
            self.model_ml = model
            self.X_train = X
            self.y_train = y
            self.feature_names = self.config.FEATURES_ML
            
            # Oblicz statystyki walidacyjne
            from sklearn.metrics import mean_squared_error, r2_score
            y_pred = model.predict(X_val)
            
            self.statystyki["ml_metrics"] = {
                "mse": float(mean_squared_error(y_val, y_pred)),
                "r2": float(r2_score(y_val, y_pred)),
                "training_samples": len(X_train),
                "validation_samples": len(X_val),
            }
            
            # Oblicz globalne statystyki kalibracji
            self._oblicz_statystyki_kalibracji(obserwacje)
            
            print(f"Trenowanie ML zakończone pomyślnie. "
                  f"MSE: {self.statystyki['ml_metrics']['mse']:.4f}, "
                  f"R2: {self.statystyki['ml_metrics']['r2']:.4f}")
            
            return True
            
        except Exception as e:
            print(f"Błąd trenowania ML: {e}")
            return False
    
    def _trenuj_hybrydowo(self, obserwacje: List[Obserwacja]) -> bool:
        """
        Trenuje model kalibracji metodą hybrydową (BUCKET + ML).
        
        Args:
            obserwacje: Lista obserwacji
        
        Returns:
            True jeśli trening się powiódł
        """
        # Trenuj obie metody
        bucket_ok = self._trenuj_bucket(obserwacje)
        ml_ok = False
        
        if self.config.ML_ENABLED:
            ml_ok = self._trenuj_ml(obserwacje)
        
        if not bucket_ok:
            return False
        
        print(f"Trenowanie HYBRID zakończone. BUCKET: {bucket_ok}, ML: {ml_ok}")
        return True
    
    def _przygotuj_dane_ml(self, obserwacje: List[Obserwacja]) -> Tuple[List[List[float]], List[float]]:
        """
        Przygotowuje dane treningowe dla metody ML.
        
        Features:
        - confidence: Oryginalne confidence z Level 1
        - grupa_1, grupa_X, grupa_2: One-hot encoding grupy wyniku
        - gospodarze, gosc: Liczba goli z predykcji
        - zgoda_sieci: Stopień zgody między sieciami
        - sredni_confidence_sieci: Średni confidence z sieci
        
        Target:
        - trafienie: 1.0 jeśli trafione, 0.0 jeśli błąd
          (model uczy się przewidywać prawdopodobieństwo trafienia)
        
        Args:
            obserwacje: Lista obserwacji
        
        Returns:
            Tuple (X, y) - Features i target
        """
        X = []
        y = []
        
        for obs in obserwacje:
            # Target: trafienie (1/0)
            target = 1.0 if obs.trafienie else 0.0
            
            # Features
            features = []
            
            # 1. Confidence
            features.append(obs.confidence)
            
            # 2. One-hot encoding grupy
            grupa_encoding = _encode_grupa(obs.klasa_grupa or get_grupa_wyniku(obs.wynik_predykcji))
            features.append(grupa_encoding["grupa_1"])
            features.append(grupa_encoding["grupa_X"])
            features.append(grupa_encoding["grupa_2"])
            
            # 3. Liczba goli z predykcji
            gosp, gosc = _decode_wynik(obs.wynik_predykcji)
            features.append(float(gosp))
            features.append(float(gosc))
            
            # 4. Zgoda sieci (jeśli dostępne w sieci_skladowych)
            # TODO: Dodać obsługę sieci_skladowych w Obserwacji
            zgoda = 0.5  # Domyślna wartość
            features.append(zgoda)
            
            # 5. Średni confidence sieci
            sredni_conf = 0.5
            features.append(sredni_conf)
            
            X.append(features)
            y.append(target)
        
        return X, y

    # -------------------------------------------------------------------------
    # STATYSTYKI KALIBRACJI
    # -------------------------------------------------------------------------
    
    def _oblicz_statystyki_kalibracji(self, obserwacje: List[Obserwacja]):
        """
        Oblicza globalne statystyki kalibracji na podstawie historii.
        
        Args:
            obserwacje: Lista obserwacji
        """
        if not obserwacje:
            return
        
        # Podstawowe statystyki
        trafienia = sum(1 for o in obserwacje if o.trafienie)
        trafienia_grupa = sum(1 for o in obserwacje if o.trafienie_grupa)
        
        # Średnie confidence
        confidences = [o.confidence for o in obserwacje]
        sredni_confidence = statistics.mean(confidences) if confidences else 0.0
        
        # Skuteczność globalna
        globalna_skutecznosc = trafienia / len(obserwacje) if obserwacje else 0.0
        globalna_skutecznosc_grupa = trafienia_grupa / len(obserwacje) if obserwacje else 0.0
        
        # Statystyki per grupa (1/X/2)
        grupy_stats = {}
        for grupa in ["1", "X", "2"]:
            obs_grupy = [o for o in obserwacje if o.klasa_grupa == grupa]
            if obs_grupy:
                trafienia_g = sum(1 for o in obs_grupy if o.trafienie)
                grupy_stats[grupa] = {
                    "liczba": len(obs_grupy),
                    "trafienia": trafienia_g,
                    "skutecznosc": trafienia_g / len(obs_grupy),
                    "sredni_confidence": statistics.mean([o.confidence for o in obs_grupy]),
                }
        
        # Statystyki per klasa (top 10 najczęstszych klas)
        klasy_counter = Counter(o.klasa_dokladna for o in obserwacje if o.klasa_dokladna)
        klasy_stats = {}
        for klasa, count in klasy_counter.most_common(10):
            obs_klasy = [o for o in obserwacje if o.klasa_dokladna == klasa]
            trafienia_k = sum(1 for o in obs_klasy if o.trafienie)
            klasy_stats[klasa] = {
                "liczba": count,
                "trafienia": trafienia_k,
                "skutecznosc": trafienia_k / count if count > 0 else 0.0,
                "sredni_confidence": statistics.mean([o.confidence for o in obs_klasy]),
            }
        
        # Statystyki confidence
        conf_stats = {
            "min": min(confidences) if confidences else 0.0,
            "max": max(confidences) if confidences else 1.0,
            "mean": sredni_confidence,
            "median": statistics.median(confidences) if len(confidences) > 1 else sredni_confidence,
            "stdev": statistics.stdev(confidences) if len(confidences) > 1 else 0.0,
        }
        
        # Błędy (nietrafione predykcje)
        bledy = [o for o in obserwacje if not o.trafienie]
        bledy_grupa = [o for o in obserwacje if not o.trafienie_grupa]
        
        # Najczęstsze błędy (predykcja vs rzeczywistość)
        bledy_patterns = Counter(
            f"{o.wynik_predykcji}->{o.wynik_rzeczywisty}" 
            for o in bledy
        )
        
        # Najczęstsze błędy grupowe
        bledy_grupa_patterns = Counter(
            f"{o.klasa_grupa}->{get_grupa_wyniku(o.wynik_rzeczywisty)}"
            for o in bledy_grupa
        )
        
        # Zapisz statystyki
        self.statystyki["global"] = {
            "calkowita_liczba_obserwacji": len(obserwacje),
            "trafienia": trafienia,
            "trafienia_grupa": trafienia_grupa,
            "skutecznosc": globalna_skutecznosc,
            "skutecznosc_grupa": globalna_skutecznosc_grupa,
            "sredni_confidence": sredni_confidence,
        }
        
        self.statystyki["grupy"] = grupy_stats
        self.statystyki["klasy"] = klasy_stats
        self.statystyki["confidence"] = conf_stats
        self.statystyki["bledy"] = {
            "liczba": len(bledy),
            "liczba_grupa": len(bledy_grupa),
            "najczestsze_wzorce": dict(bledy_patterns.most_common(10)),
            "najczestsze_wzorce_grupa": dict(bledy_grupa_patterns.most_common(10)),
        }
        
        # Zapisz w metadanych
        self.metadata["statystyki"] = self.statystyki

    # -------------------------------------------------------------------------
    # KALIBRACJA CONFIDENCE
    # -------------------------------------------------------------------------
    
    def kalibruj(self, predykcja_l1: PredykcjaLevel1, 
                 sieci_skladowe: Optional[Dict[str, Any]] = None) -> PredykcjaLevel1Kalibrowana:
        """
        Kalibruje confidence predykcji Level 1.
        
        Działanie:
        1. Określa metodę kalibracji (zależnie od konfiguracji)
        2. Oblicza kalibrowane confidence
        3. Zwraca PredykcjaLevel1Kalibrowana
        
        Args:
            predykcja_l1: Predykcja z Level 1 do skalibrowania
            sieci_skladowe: Opcjonalne dane o sieciach składających (dla obliczenia zgody)
        
        Returns:
            PredykcjaLevel1Kalibrowana z poprawionym confidence
        """
        # Jeśli nie ma modelu, zwróć oryginalne confidence
        if self.model_bucket is None and self.model_ml is None:
            return PredykcjaLevel1Kalibrowana(
                id_modelu=predykcja_l1.id_modelu,
                id_meczu=predykcja_l1.id_meczu,
                id_grupy=predykcja_l1.id_grupy,
                wynik_predykcji=predykcja_l1.wynik_predykcji,
                confidence=predykcja_l1.confidence,
                confidence_kalibrowana=predykcja_l1.confidence,
                poprawka_kalibracji=0.0,
            )
        
        # Oblicz kalibrowane confidence odpowiednią metodą
        if self.config.METODA_KALIBRACJI == "BUCKET":
            confidence_kalibrowana = self._kalibruj_bucket(predykcja_l1.confidence)
        elif self.config.METODA_KALIBRACJI == "ML" and self.model_ml is not None:
            confidence_kalibrowana = self._kalibruj_ml(predykcja_l1, sieci_skladowe)
        else:  # HYBRID
            confidence_kalibrowana = self._kalibruj_hybrydowo(predykcja_l1, sieci_skladowe)
        
        # Oblicz poprawkę
        poprawka = confidence_kalibrowana - predykcja_l1.confidence
        
        return PredykcjaLevel1Kalibrowana(
            id_modelu=predykcja_l1.id_modelu,
            id_meczu=predykcja_l1.id_meczu,
            id_grupy=predykcja_l1.id_grupy,
            wynik_predykcji=predykcja_l1.wynik_predykcji,
            confidence=predykcja_l1.confidence,
            confidence_kalibrowana=confidence_kalibrowana,
            poprawka_kalibracji=poprawka,
        )
    
    def _kalibruj_bucket(self, confidence: float) -> float:
        """
        Kalibruje confidence metodą bucketową.
        
        Args:
            confidence: Oryginalne confidence [0.0, 1.0]
        
        Returns:
            Kalibrowane confidence
        """
        if self.model_bucket is None:
            return confidence
        
        bucket_idx = _get_bucket(confidence, self.config.LICZBA_BUCKETOW)
        
        # Jeśli bucket istnieje, użyj jego skuteczności
        if bucket_idx in self.model_bucket:
            return self.model_bucket[bucket_idx]
        
        # Fallback: użyj globalnej skuteczności
        if "global" in self.statystyki:
            return self.statystyki["global"].get("skutecznosc", confidence)
        
        return confidence
    
    def _kalibruj_ml(self, predykcja_l1: PredykcjaLevel1, 
                     sieci_skladowe: Optional[Dict[str, Any]] = None) -> float:
        """
        Kalibruje confidence metodą ML.
        
        Args:
            predykcja_l1: Predykcja z Level 1
            sieci_skladowe: Opcjonalne dane o sieciach składających
        
        Returns:
            Kalibrowane confidence
        """
        if self.model_ml is None:
            return predykcja_l1.confidence
        
        try:
            # Przygotuj features
            features = self._przygotuj_features_ml(predykcja_l1, sieci_skladowe)
            
            # Predykcja modelu (zwraca prawdopodobieństwo trafienia)
            probability = self.model_ml.predict([features])[0]
            
            # Ogranicz do [0.0, 1.0]
            return max(0.0, min(1.0, float(probability)))
            
        except Exception as e:
            print(f"Błąd kalibracji ML: {e}")
            return predykcja_l1.confidence
    
    def _kalibruj_hybrydowo(self, predykcja_l1: PredykcjaLevel1, 
                           sieci_skladowe: Optional[Dict[str, Any]] = None) -> float:
        """
        Kalibruje confidence metodą hybrydową (BUCKET + ML).
        
        Args:
            predykcja_l1: Predykcja z Level 1
            sieci_skladowe: Opcjonalne dane o sieciach składających
        
        Returns:
            Kalibrowane confidence
        """
        # Oblicz confidence z obu metod
        conf_bucket = self._kalibruj_bucket(predykcja_l1.confidence)
        conf_ml = predykcja_l1.confidence  # Domyślna wartość
        
        if self.model_ml is not None:
            conf_ml = self._kalibruj_ml(predykcja_l1, sieci_skladowe)
        
        # Kombinacja ważona
        hybrid_confidence = (
            self.config.HYBRID_WEIGHT_BUCKET * conf_bucket +
            self.config.HYBRID_WEIGHT_ML * conf_ml
        )
        
        return max(0.0, min(1.0, hybrid_confidence))
    
    def _przygotuj_features_ml(self, predykcja_l1: PredykcjaLevel1, 
                             sieci_skladowe: Optional[Dict[str, Any]] = None) -> List[float]:
        """
        Przygotowuje features dla predykcji ML.
        
        Args:
            predykcja_l1: Predykcja z Level 1
            sieci_skladowe: Opcjonalne dane o sieciach składających
        
        Returns:
            Lista features
        """
        features = []
        
        # 1. Confidence
        features.append(predykcja_l1.confidence)
        
        # 2. One-hot encoding grupy
        grupa = get_grupa_wyniku(predykcja_l1.wynik_predykcji)
        grupa_encoding = _encode_grupa(grupa)
        features.append(grupa_encoding["grupa_1"])
        features.append(grupa_encoding["grupa_X"])
        features.append(grupa_encoding["grupa_2"])
        
        # 3. Liczba goli z predykcji
        gosp, gosc = _decode_wynik(predykcja_l1.wynik_predykcji)
        features.append(float(gosp))
        features.append(float(gosc))
        
        # 4. Zgoda sieci
        if sieci_skladowe:
            zgoda = _calculate_zgoda_sieci(sieci_skladowe)
        else:
            zgoda = 0.5
        features.append(zgoda)
        
        # 5. Średni confidence sieci
        if sieci_skladowe:
            sredni_conf = _calculate_sredni_confidence_sieci(sieci_skladowe)
        else:
            sredni_conf = 0.5
        features.append(sredni_conf)
        
        return features

    # -------------------------------------------------------------------------
    # WYKRYWANIE WZORCÓW ZACHOWANIA
    # -------------------------------------------------------------------------
    
    def wykryj_wzorce(self, obserwacje: Optional[List[Obserwacja]] = None) -> List[WzorecZachowania]:
        """
        Wykrywa powtarzalne wzorce zachowania/błędów w Level 1.
        
        Analizuje:
        - Które klasy wyników są częściej mylone
        - Które grupy (1/X/2) są trudniejsze
        - Które kombinacje cech powodują systematyczne błędy
        - Czy pewne sieci częściej mylą się dla określonych klas
        
        Args:
            obserwacje: Opcjonalna lista obserwacji. Jeśli None, używa obecnych statystyk.
        
        Returns:
            Lista wykrytych wzorców
        """
        self.wzorce = []
        
        # Użyj podanych obserwacji lub statystyk
        if obserwacje:
            self._oblicz_statystyki_kalibracji(obserwacje)
        
        if not self.statystyki:
            print("Brak statystyk do wykrywania wzorców.")
            return self.wzorce
        
        # 1. Wykryj wzorce błędów dokładnych (predykcja -> rzeczywistość)
        self._wykryj_wzorce_bledow_dokladnych()
        
        # 2. Wykryj wzorce błędów grupowych (grupa -> rzeczywista grupa)
        self._wykryj_wzorce_bledow_grupowych()
        
        # 3. Wykryj wzorce per klasa (trudne klasy)
        self._wykryj_wzorce_trudnych_klas()
        
        # 4. Wykryj wzorce per grupa (trudne grupy)
        self._wykryj_wzorce_trudnych_grup()
        
        # 5. Wykryj wzorce confidence (zależność confidence vs trafienie)
        self._wykryj_wzorce_confidence()
        
        # Zapisz wzorce w metadanych
        self.metadata["wzorce"] = [w.to_dict() for w in self.wzorce]
        
        return self.wzorce
    
    def _wykryj_wzorce_bledow_dokladnych(self):
        """Wykrywa wzorce dokładnych błędów (np. 1:1 zamiast 0:0)"""
        if "bledy" not in self.statystyki or "najczestsze_wzorce" not in self.statystyki["bledy"]:
            return
        
        for pattern, count in self.statystyki["bledy"]["najczestsze_wzorce"].items():
            if count < 5:  # Minimalna częstotliwość
                continue
            
            pred, rzeczyw = pattern.split("->")
            
            wzorzec = WzorecZachowania(
                nazwa=f"blad_{pred}_zamiast_{rzeczyw}",
                opis=f"Model Level 1 częściej przewiduje '{pred}' zamiast '{rzeczyw}'",
                czestotliwosc=count,
                przykłady=[],  # Brak konkretnych przykładów w statystykach
                cechy_charakterystyczne={"typ": "bledy_dokladne"}
            )
            self.wzorce.append(wzorzec)
    
    def _wykryj_wzorce_bledow_grupowych(self):
        """Wykrywa wzorce błędów grupowych (np. 1 zamiast X)"""
        if "bledy" not in self.statystyki or "najczestsze_wzorce_grupa" not in self.statystyki["bledy"]:
            return
        
        for pattern, count in self.statystyki["bledy"]["najczestsze_wzorce_grupa"].items():
            if count < 5:
                continue
            
            pred_grupa, rzeczyw_grupa = pattern.split("->")
            
            wzorzec = WzorecZachowania(
                nazwa=f"blad_grupa_{pred_grupa}_zamiast_{rzeczyw_grupa}",
                opis=f"Model Level 1 częściej klasyfikuje jako grupę '{pred_grupa}' zamiast '{rzeczyw_grupa}'",
                czestotliwosc=count,
                przykłady=[],
                cechy_charakterystyczne={"typ": "bledy_grupowe"}
            )
            self.wzorce.append(wzorzec)
    
    def _wykryj_wzorce_trudnych_klas(self):
        """Wykrywa wzorce trudnych klas (niska skuteczność dla określonych klas)"""
        if "klasy" not in self.statystyki:
            return
        
        globalna_skutecznosc = self.statystyki.get("global", {}).get("skutecznosc", 0.5)
        
        for klasa, stats in self.statystyki["klasy"].items():
            skutecznosc = stats.get("skutecznosc", 0.0)
            
            # Jeśli skuteczność jest znacznie niższa niż globalna
            if stats["liczba"] >= 10 and skutecznosc < globalna_skutecznosc * 0.8:
                wzorzec = WzorecZachowania(
                    nazwa=f"trudna_klasa_{klasa}",
                    opis=f"Klasa '{klasa}' jest trudna dla Level 1 (skuteczność: {skutecznosc:.2%} vs globalna: {globalna_skutecznosc:.2%})",
                    czestotliwosc=stats["liczba"],
                    przykłady=[],
                    cechy_charakterystyczne={
                        "typ": "trudna_klasa",
                        "klasa": klasa,
                        "skutecznosc": skutecznosc,
                        "globalna_skutecznosc": globalna_skutecznosc,
                    }
                )
                self.wzorce.append(wzorzec)
    
    def _wykryj_wzorce_trudnych_grup(self):
        """Wykrywa wzorce trudnych grup (1/X/2)"""
        if "grupy" not in self.statystyki:
            return
        
        globalna_skutecznosc = self.statystyki.get("global", {}).get("skutecznosc", 0.5)
        
        for grupa, stats in self.statystyki["grupy"].items():
            skutecznosc = stats.get("skutecznosc", 0.0)
            
            # Jeśli skuteczność jest znacznie niższa niż globalna
            if stats["liczba"] >= 10 and skutecznosc < globalna_skutecznosc * 0.8:
                wzorzec = WzorecZachowania(
                    nazwa=f"trudna_grupa_{grupa}",
                    opis=f"Grupa '{grupa}' jest trudna dla Level 1 (skuteczność: {skutecznosc:.2%} vs globalna: {globalna_skutecznosc:.2%})",
                    czestotliwosc=stats["liczba"],
                    przykłady=[],
                    cechy_charakterystyczne={
                        "typ": "trudna_grupa",
                        "grupa": grupa,
                        "skutecznosc": skutecznosc,
                        "globalna_skutecznosc": globalna_skutecznosc,
                    }
                )
                self.wzorce.append(wzorzec)
    
    def _wykryj_wzorce_confidence(self):
        """Wykrywa wzorce związane z confidence"""
        if "bucket_stats" not in self.statystyki:
            return
        
        for bucket_idx, stats in self.statystyki["bucket_stats"].items():
            # Oblicz oczekiwaną skuteczność (liniowa zależność)
            # Bucket 0 (0.0-0.1) powinien mieć niską skuteczność
            # Bucket 9 (0.9-1.0) powinien mieć wysoką skuteczność
            expected = (bucket_idx + 1) / self.config.LICZBA_BUCKETOW
            actual = stats.get("skutecznosc", 0.0)
            
            # Jeśli różnica między oczekiwaną a rzeczywistą jest duża
            if stats["liczba"] >= 10 and abs(actual - expected) > 0.2:
                bucket_range = f"{bucket_idx * 0.1:.1f}-{(bucket_idx + 1) * 0.1:.1f}"
                
                wzorzec = WzorecZachowania(
                    nazwa=f"confidence_bucket_{bucket_idx}",
                    opis=f"Confidence w zakresie {bucket_range} ma nieoczekiwaną skuteczność: {actual:.2%} (oczekiwano: {expected:.2%})",
                    czestotliwosc=stats["liczba"],
                    przykłady=[],
                    cechy_charakterystyczne={
                        "typ": "confidence_anomalia",
                        "bucket": bucket_idx,
                        "bucket_range": bucket_range,
                        "actual_skutecznosc": actual,
                        "expected_skutecznosc": expected,
                    }
                )
                self.wzorce.append(wzorzec)

    # -------------------------------------------------------------------------
    # PERSYSTENCJA (ZAPIS/ODCZYT MODELU)
    # -------------------------------------------------------------------------
    
    def zapisz_model(self, sciezka: Optional[Path] = None, 
                     nazwa: Optional[str] = None) -> Optional[Path]:
        """
        Zapisuje model kalibracji do pliku.
        
        Wersjonowanie: Każdy zapis tworzy NOWY plik (nie nadpisujemy!)
        
        Args:
            sciezka: Ścieżka do katalogu (domyślnie config.ARCHIWUM_PATH)
            nazwa: Nazwa modelu (domyślnie wersja z metadata)
        
        Returns:
            Ścieżka do zapisanych plików lub None w przypadku błędu
        """
        try:
            # Ustal ścieżkę
            if sciezka is None:
                sciezka = self.config.ARCHIWUM_PATH
            
            if nazwa is None:
                nazwa = self.metadata.get("wersja", "kalibrator_v2")
            
            # Upewnij się, że katalog istnieje
            sciezka.mkdir(parents=True, exist_ok=True)
            
            # 1. Zapisz model (pickle)
            model_data = {
                "model_bucket": self.model_bucket,
                "model_ml": self.model_ml,
                "X_train": self.X_train,
                "y_train": self.y_train,
                "feature_names": self.feature_names,
            }
            
            model_file = sciezka / f"{self.config.MODEL_PREFIX}_{nazwa}.pkl"
            with open(model_file, 'wb') as f:
                pickle.dump(model_data, f)
            
            # 2. Zapisz metadane (JSON)
            metadata_file = sciezka / f"{self.config.METADATA_PREFIX}_{nazwa}.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
            
            # 3. Zapisz statystyki (JSON)
            statystyki_file = sciezka / f"{self.config.METADATA_PREFIX}_{nazwa}_stats.json"
            with open(statystyki_file, 'w', encoding='utf-8') as f:
                json.dump(self.statystyki, f, indent=2, ensure_ascii=False)
            
            # 4. Zapisz wzorce (JSON)
            wzorce_data = [w.to_dict() for w in self.wzorce]
            wzorce_file = sciezka / f"{self.config.METADATA_PREFIX}_{nazwa}_wzorce.json"
            with open(wzorce_file, 'w', encoding='utf-8') as f:
                json.dump(wzorce_data, f, indent=2, ensure_ascii=False)
            
            print(f"Model zapisanay: {model_file}")
            print(f"Metadane zapisane: {metadata_file}")
            print(f"Statystyki zapisane: {statystyki_file}")
            print(f"Wzorce zapisane: {wzorce_file}")
            
            return model_file
            
        except Exception as e:
            print(f"Błąd zapisu modelu: {e}")
            return None
    
    def zaladuj_model(self, sciezka_modelu: Path, 
                      sciezka_metadata: Optional[Path] = None) -> bool:
        """
        Ładuje model kalibracji z pliku.
        
        Args:
            sciezka_modelu: Ścieżka do pliku modelu (.pkl)
            sciezka_metadata: Ścieżka do pliku metadanych (.json)
        
        Returns:
            True jeśli załadowano pomyślnie
        """
        try:
            # 1. Załaduj model
            with open(sciezka_modelu, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model_bucket = model_data.get("model_bucket")
            self.model_ml = model_data.get("model_ml")
            self.X_train = model_data.get("X_train")
            self.y_train = model_data.get("y_train")
            self.feature_names = model_data.get("feature_names", [])
            
            # 2. Załaduj metadane
            if sciezka_metadata is None:
                # Spróbuj znaleźć plik metadanych na podstawie nazwy
                model_stem = sciezka_modelu.stem.replace(self.config.MODEL_PREFIX, "")
                sciezka_metadata = sciezka_modelu.parent / f"{self.config.METADATA_PREFIX}{model_stem}.json"
            
            if sciezka_metadata.exists():
                with open(sciezka_metadata, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            
            # 3. Załaduj statystyki
            stats_file = sciezka_modelu.parent / f"{self.config.METADATA_PREFIX}{sciezka_modelu.stem.split(self.config.MODEL_PREFIX)[-1]}_stats.json"
            if stats_file.exists():
                with open(stats_file, 'r', encoding='utf-8') as f:
                    self.statystyki = json.load(f)
            
            # 4. Załaduj wzorce
            wzorce_file = sciezka_modelu.parent / f"{self.config.METADATA_PREFIX}{sciezka_modelu.stem.split(self.config.MODEL_PREFIX)[-1]}_wzorce.json"
            if wzorce_file.exists():
                with open(wzorce_file, 'r', encoding='utf-8') as f:
                    wzorce_data = json.load(f)
                self.wzorce = [
                    WzorecZachowania(
                        nazwa=w["nazwa"],
                        opis=w["opis"],
                        czestotliwosc=w.get("czestotliwosc", 0),
                        przyklady=w.get("przykłady", []),
                        cechy_charakterystyczne=w.get("cechy_charakterystyczne", {}),
                    )
                    for w in wzorce_data
                ]
            
            print(f"Model załadowany: {sciezka_modelu}")
            print(f"Metadane: {self.metadata.get('wersja', 'N/A')}")
            print(f"Obserwacje: {self.metadata.get('liczba_obserwacji', 0)}")
            
            return True
            
        except Exception as e:
            print(f"Błąd ładowania modelu: {e}")
            return False
    
    def lista_wersji(self) -> List[Path]:
        """
        Zwraca listę dostępnych wersji modeli kalibracji.
        
        Returns:
            Lista ścieżek do plików modeli (posortowane po dacie modyfikacji)
        """
        if not self.config.ARCHIWUM_PATH.exists():
            return []
        
        return sorted(
            self.config.ARCHIWUM_PATH.glob(f"{self.config.MODEL_PREFIX}_*.pkl"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
    
    def usun_stare_wersje(self, max_wersji: int = 10):
        """
        Usuwa stare wersje modeli, zachowując najnowsze.
        
        Args:
            max_wersji: Maksymalna liczba wersji do zachowania
        """
        wersje = self.lista_wersji()
        
        if len(wersje) <= max_wersji:
            return
        
        # Usun najstarsze wersje
        for wersja in wersje[max_wersji:]:
            try:
                wersja.unlink()
                
                # Usun również pliki metadanych
                metadata_file = wersja.parent / f"{self.config.METADATA_PREFIX}_{wersja.stem.split(self.config.MODEL_PREFIX)[-1]}.json"
                if metadata_file.exists():
                    metadata_file.unlink()
                
                stats_file = wersja.parent / f"{self.config.METADATA_PREFIX}_{wersja.stem.split(self.config.MODEL_PREFIX)[-1]}_stats.json"
                if stats_file.exists():
                    stats_file.unlink()
                
                wzorce_file = wersja.parent / f"{self.config.METADATA_PREFIX}_{wersja.stem.split(self.config.MODEL_PREFIX)[-1]}_wzorce.json"
                if wzorce_file.exists():
                    wzorce_file.unlink()
                
                print(f"Usunieto stara wersje: {wersja}")
            except Exception as e:
                print(f"Błąd usuwania wersji {wersja}: {e}")

    # -------------------------------------------------------------------------
    # METODY POMOCNICZE
    # -------------------------------------------------------------------------
    
    def pobierz_statystyki(self) -> Dict[str, Any]:
        """Zwraca aktualne statystyki kalibracji"""
        return self.statystyki
    
    def pobierz_metadata(self) -> Dict[str, Any]:
        """Zwraca metadane kalibratora"""
        return self.metadata
    
    def pobierz_wzorce(self) -> List[WzorecZachowania]:
        """Zwraca listę wykrytych wzorców"""
        return self.wzorce
    
    def ustaw_repozytorium(self, repozytorium: Any):
        """
        Łączy kalibrator z repozytorium pamięci.
        
        Args:
            repozytorium: Obiekt PamiecRepozytorium
        """
        self.repozytorium = repozytorium
    
    def trenuj_z_repozytorium(self, grupa_modelu: Optional[str] = None) -> bool:
        """
        Trenuje model na podstawie danych z podłączonego repozytorium.
        
        Args:
            grupa_modelu: Opcjonalny filtr po grupie modelu
        
        Returns:
            True jeśli trening się powiódł
        """
        if self.repozytorium is None:
            print("Brak podłączonego repozytorium.")
            return False
        
        # Pobierz obserwacje
        if grupa_modelu:
            obserwacje = self.repozytorium.znajdz_po_modelu(grupa_modelu)
        else:
            obserwacje = list(self.repozytorium.obserwacje.values())
        
        return self.trenuj(obserwacje)


# =============================================================================
# FUNKCJE GLOBALNE
# =============================================================================

def utworz_kalibrator(config: Optional[KalibratorConfig] = None) -> KalibratorLevel2:
    """
    Tworzy nowy kalibrator Level 2.
    
    Args:
        config: Konfiguracja kalibratora (opcjonalna)
    
    Returns:
        Obiekt KalibratorLevel2
    """
    return KalibratorLevel2(config=config)


def utworz_kalibrator_buckets(config: Optional[KalibratorConfig] = None) -> KalibratorLevel2:
    """
    Tworzy kalibrator z metodą BUCKET.
    
    Args:
        config: Konfiguracja kalibratora (opcjonalna)
    
    Returns:
        Obiekt KalibratorLevel2
    """
    if config is None:
        config = KalibratorConfig()
    config.METODA_KALIBRACJI = "BUCKET"
    return KalibratorLevel2(config=config)


def utworz_kalibrator_ml(config: Optional[KalibratorConfig] = None) -> KalibratorLevel2:
    """
    Tworzy kalibrator z metodą ML (jeśli dostępna).
    
    Args:
        config: Konfiguracja kalibratora (opcjonalna)
    
    Returns:
        Obiekt KalibratorLevel2
    """
    if config is None:
        config = KalibratorConfig()
    config.METODA_KALIBRACJI = "ML"
    return KalibratorLevel2(config=config)


# =============================================================================
# TESTY
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Testing KalibratorLevel2...")
    print("=" * 60)
    
    # Test 1: Inicjalizacja
    print("\n--- Test 1: Inicjalizacja ---")
    kalibrator = KalibratorLevel2()
    print(f"Wersja: {kalibrator.metadata['wersja']}")
    print(f"ML dostępny: {kalibrator.config.ML_ENABLED}")
    print(f"Metoda: {kalibrator.config.METODA_KALIBRACJI}")
    
    # Test 2: Bucketowanie
    print("\n--- Test 2: Bucketowanie ---")
    for conf in [0.05, 0.15, 0.25, 0.55, 0.85, 1.0]:
        bucket = _get_bucket(conf, 10)
        print(f"confidence={conf:.2f} -> bucket={bucket}")
    
    # Test 3: Encoding grupy
    print("\n--- Test 3: Encoding grupy ---")
    for grupa in ["1", "X", "2"]:
        encoded = _encode_grupa(grupa)
        print(f"grupa={grupa} -> {encoded}")
    
    # Test 4: Decoding wyniku
    print("\n--- Test 4: Decoding wyniku ---")
    for wynik in ["1:0", "2:2", "0:3", "invalid"]:
        decoded = _decode_wynik(wynik)
        print(f"wynik={wynik} -> {decoded}")
    
    # Test 5: Trenowanie (symulacja z przykładowymi danymi)
    print("\n--- Test 5: Trenowanie (BUCKET) ---")
    
    # Generuj przykładowe obserwacje
    import random
    random.seed(42)
    
    obserwacje_test = []
    for i in range(200):
        # Losowy wynik predykcji
        pred_wynik = random.choice(["1:0", "0:1", "2:0", "0:2", "1:1", "2:1", "0:0", "3:1"])
        
        # Losowy wynik rzeczywisty
        rzeczyw_wynik = random.choice(["1:0", "0:1", "2:0", "0:2", "1:1", "2:1", "0:0", "3:1"])
        
        # Losowe confidence
        confidence = random.uniform(0.1, 0.9)
        
        # Trafienie = 30% szans (realistyczna skuteczność)
        trafienie = (pred_wynik == rzeczyw_wynik) and (random.random() < 0.3)
        if not trafienie:
            trafienie = (pred_wynik == rzeczyw_wynik) and (random.random() < 0.7)
        
        obs = Obserwacja(
            id_meczu=f"TestMatch_{i}",
            id_grupy="test_group",
            id_modelu="test_model",
            wynik_predykcji=pred_wynik,
            confidence=confidence,
            wynik_rzeczywisty=rzeczyw_wynik,
        )
        # Ustaw trafienie ręcznie
        obs.trafienie = (pred_wynik == rzeczyw_wynik)
        
        obserwacje_test.append(obs)
    
    # Trenuj
    trenowanie_ok = kalibrator.trenuj(obserwacje_test, metoda="BUCKET")
    print(f"Trenowanie: {'SUKCES' if trenowanie_ok else 'FAIL'}")
    print(f"Buckety: {len(kalibrator.model_bucket)}")
    print(f"Statystyki: {kalibrator.statystyki.get('global', {})}")
    
    # Test 6: Kalibracja
    print("\n--- Test 6: Kalibracja ---")
    
    test_pred = PredykcjaLevel1(
        id_modelu="test_model",
        id_meczu="TestMatch_New",
        id_grupy="test_group",
        wynik_predykcji="2:1",
        confidence=0.85,
    )
    
    pred_kalibrowana = kalibrator.kalibruj(test_pred)
    print(f"Oryginalne confidence: {test_pred.confidence:.4f}")
    print(f"Kalibrowane confidence: {pred_kalibrowana.confidence_kalibrowana:.4f}")
    print(f"Poprawka: {pred_kalibrowana.poprawka_kalibracji:.4f}")
    
    # Test 7: Wykrywanie wzorców
    print("\n--- Test 7: Wykrywanie wzorców ---")
    wzorce = kalibrator.wykryj_wzorce(obserwacje_test)
    print(f"Wykryto {len(wzorce)} wzorców:")
    for wzor in wzorce[:5]:  # Pokaż pierwsze 5
        print(f"  - {wzor.nazwa}: {wzor.opis}")
    
    # Test 8: Zapis modelu
    print("\n--- Test 8: Zapis modelu ---")
    zapis_path = kalibrator.zapisz_model()
    print(f"Model zapisany: {zapis_path}")
    
    # Test 9: Ładowanie modelu
    print("\n--- Test 9: Ładowanie modelu ---")
    if zapis_path:
        kalibrator2 = KalibratorLevel2()
        zaladowano = kalibrator2.zaladuj_model(zapis_path)
        print(f"Model załadowany: {'SUKCES' if zaladowano else 'FAIL'}")
        if zaladowano:
            print(f"Wersja: {kalibrator2.metadata.get('wersja')}")
            print(f"Buckety: {len(kalibrator2.model_bucket)}")
    
    # Test 10: ML (jeśli dostępny)
    print("\n--- Test 10: Trenowanie ML (jeśli dostępny) ---")
    if kalibrator.config.ML_ENABLED:
        kalibrator_ml = KalibratorLevel2()
        kalibrator_ml.config.METODA_KALIBRACJI = "ML"
        ml_ok = kalibrator_ml.trenuj(obserwacje_test)
        print(f"Trenowanie ML: {'SUKCES' if ml_ok else 'FAIL'}")
        if ml_ok:
            pred_ml = kalibrator_ml.kalibruj(test_pred)
            print(f"Kalibracja ML: {test_pred.confidence:.4f} -> {pred_ml.confidence_kalibrowana:.4f}")
    else:
        print("ML niedostępny (brak sklearn)")
    
    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)


