import os
import json
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from collections import Counter, defaultdict
import scipy.stats as stats

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.utils import to_categorical

# KONFIGURACJA

PLIK_PREDYKCJI = (
    "dane/dataBase_futbol_trend.csv"
)

PLIK_TRENING = (
    "dane/kod_dataBase_futbol_trend.csv"
)

KATALOG_MODELE = (
    "modele_dataBase_futbol_trend"
)

os.makedirs(
    KATALOG_MODELE,
    exist_ok=True
)

# KLASY WYNIKÓW

WYNIKI = [
    "1:0",
    "2:0",
    "3:0",
    "2:1",
    "3:1",
    "3:2",
    "0:1",
    "0:2",
    "0:3",
    "1:2",
    "1:3",
    "2:3",
    "0:0",
    "1:1",
    "2:2"
]

MAPA_KLAS = {
    wynik: index
    for index, wynik
    in enumerate(WYNIKI)
}

# SPOJRZENIA ŚWIATA

SPOJRZENIA = {
    "dataBase_futbol_trend": [
        "zmiana_1", "zmiana_X", "zmiana_2", "amplituda_1", "amplituda_X", "amplituda_2",
        "tempo_1", "tempo_X", "tempo_2", "max_wahanie_1", "max_wahanie_X", "max_wahanie_2",
        "start_1_raw", "start_X_raw", "start_2_raw", "koniec_1_raw", "koniec_X_raw",
        "koniec_2_raw", "log_start_1", "log_start_X", "log_start_2", "log_koniec_1",
        "log_koniec_X", "log_koniec_2", "ratio_1X_start", "ratio_1_2_start", "ratio_X2_start",
        "ratio_1X_koniec", "ratio_1_2_koniec", "ratio_X2_koniec", "mean_1", "mean_X", "mean_2"
    ]
}

# ============================================================================
# PAMIĘĆ ŚWIATÓW - KONFIGURACJA
# ============================================================================

WORLD_DATA_PATH = "WORLD/aktualny/WORLD_MATCH_DATABASE.json"
WORLD_LEVEL_1_PATH = "WORLD/aktualny/WORLD_LEVEL_1_ANALYSIS.json"
WORLD_LEVEL_2_PATH = "WORLD/aktualny/WORLD_LEVEL_2_ANALYSIS.json"
WORLD_FULL_GROUP_PATH = "WORLD/aktualny/WORLD_FULL_GROUP_ANALYSIS.json"

MIN_SAMPLES_LEVEL_1 = 100    # Minimalna liczba przykładów dla poziomu 1
MIN_SAMPLES_LEVEL_2 = 50     # Minimalna liczba przykładów dla poziomu 2
MIN_SAMPLES_LEVEL_3 = 20     # Minimalna liczba przykładów dla poziomu 3

# ============================================================================
# KLASY WYNIKÓW DO KLASYFIKACJI
# ============================================================================

KLASA_WYGRANA_GOSPODARZE = ["1:0", "2:0", "3:0", "2:1", "3:1", "3:2"]
KLASA_REMIS = ["0:0", "1:1", "2:2"]
KLASA_WYGRANA_GOSCIE = ["0:1", "0:2", "0:3", "1:2", "1:3", "2:3"]

# ============================================================================
# WORLD HIERARCHY MANAGER
# ============================================================================

class WorldHierarchyManager:
    """
    Zarządza hierarchiczną pamięcią światów.
    
    Hierarchia:
    - POZIOM 1: szeroki świat (np. "poziom30") - najszerszy
    - POZIOM 2: średni świat (np. "poziom30poziom25") 
    - POZIOM 3: pełny świat (np. "poziom30poziom25poziom2") - najmniejszy
    
    Wybiera najlepszy poziom doświadczenia na podstawie ilości danych.
    """
    
    def __init__(self, world_match_db_path=WORLD_DATA_PATH, 
                 level_1_path=WORLD_LEVEL_1_PATH,
                 level_2_path=WORLD_LEVEL_2_PATH):
        self.world_match_db_path = world_match_db_path
        self.level_1_path = level_1_path
        self.level_2_path = level_2_path
        self.world_data = {}
        self.level_1_data = {}
        self.level_2_data = {}
        self._load_world_data()
    
    def _load_world_data(self):
        """Wczytaj dane światów z plików JSON"""
        print("  [TEACHER] Wczytano pamięć poznawczą")
        
        # Wczytaj WORLD_MATCH_DATABASE
        if os.path.exists(self.world_match_db_path):
            try:
                with open(self.world_match_db_path, 'r', encoding='utf-8') as f:
                    self.world_data = json.load(f)
                print(f"  [TEACHER] Wczytano WORLD_MATCH_DATABASE ({len(self.world_data)} mecze)")
            except Exception as e:
                print(f"  [TEACHER] Błąd wczytywania WORLD_MATCH_DATABASE: {e}")
        
        # Wczytaj WORLD_LEVEL_1_ANALYSIS
        if os.path.exists(self.level_1_path):
            try:
                with open(self.level_1_path, 'r', encoding='utf-8') as f:
                    self.level_1_data = json.load(f)
                print(f"  [TEACHER] Wczytano WORLD_LEVEL_1_ANALYSIS ({len(self.level_1_data)} grupy)")
            except Exception as e:
                print(f"  [TEACHER] Błąd wczytywania WORLD_LEVEL_1_ANALYSIS: {e}")
        
        # Wczytaj WORLD_LEVEL_2_ANALYSIS
        if os.path.exists(self.level_2_path):
            try:
                with open(self.level_2_path, 'r', encoding='utf-8') as f:
                    self.level_2_data = json.load(f)
                print(f"  [TEACHER] Wczytano WORLD_LEVEL_2_ANALYSIS ({len(self.level_2_data)} grupy)")
            except Exception as e:
                print(f"  [TEACHER] Błąd wczytywania WORLD_LEVEL_2_ANALYSIS: {e}")
    
    def get_world_levels(self, world_key):
        """
        Pobierz dostępne poziomy świata dla danego klucza.
        Zwraca dict z poziomami i ich statystykami.
        """
        if world_key not in self.world_data:
            return {}
        
        match_data = self.world_data.get(world_key, {})
        identyfikacja = match_data.get("identyfikacja", {})
        
        levels = {}
        
        # Poziom 3 - Pełny świat (najbardziej dokładny)
        full_key = identyfikacja.get("full", world_key)
        if full_key in self.world_data:
            levels["poziom3"] = self._extract_world_stats(self.world_data[full_key])
        
        # Poziom 2 - Średni świat
        level2_key = identyfikacja.get("level_2", "")
        if level2_key and level2_key in self.level_2_data:
            levels["poziom2"] = self._extract_level_stats(self.level_2_data[level2_key])
        
        # Poziom 1 - Szeroki świat
        level1_key = identyfikacja.get("level_1", "")
        if level1_key and level1_key in self.level_1_data:
            levels["poziom1"] = self._extract_level_stats(self.level_1_data[level1_key])
        
        return levels
    
    def _extract_world_stats(self, world_data):
        """Wydobądź statystyki z danych pojedynczego świata"""
        analiza = world_data.get("world_analysis", {})
        full_analysis = world_data.get("world_full_analysis", {})
        
        # Spróbuj dostać się do statystyk z różnych poziomów
        for level in ["full", "level_3", "level_2", "level_1"]:
            level_data = analiza.get(level, {})
            if level_data and "analiza" in level_data:
                stats = level_data["analiza"]
                return self._parse_world_stats(stats)
        
        # Fallback - spróbuj bezpośrednio z analiza
        if "analiza" in world_data:
            return self._parse_world_stats(world_data["analiza"])
        
        return {"ilosc_przypadkow": 0}
    
    def _extract_level_stats(self, level_data):
        """Wydobądź statystyki z danych poziomu"""
        analiza = level_data.get("analiza", {})
        return self._parse_world_stats(analiza)
    
    def _parse_world_stats(self, stats):
        """Przetwórz surowe statystyki świata"""
        ilosc_przypadkow = stats.get("ilosc_przypadkow", 0)
        wyniki_docelowe = stats.get("wyniki_docelowe", {})
        profil_meczu = stats.get("profil_meczu_1X2", {})
        
        # Oblicz rozkład 1X2
        gospodarz_pct = profil_meczu.get("gospodarze", {}).get("procent", 0)
        remis_pct = profil_meczu.get("remis", {}).get("procent", 0)
        goscie_pct = profil_meczu.get("goscie", {}).get("procent", 0)
        
        # Oblicz średnie gole
        srednie_gole = self._oblicz_srednie_gole(wyniki_docelowe)
        
        return {
            "ilosc_przypadkow": ilosc_przypadkow,
            "procent_gospodarze": gospodarz_pct / 100 if gospodarz_pct > 0 else 0,
            "procent_remis": remis_pct / 100 if remis_pct > 0 else 0,
            "procent_goscie": goscie_pct / 100 if goscie_pct > 0 else 0,
            "srednie_gole": srednie_gole,
            "wyniki_docelowe": wyniki_docelowe
        }
    
    def _oblicz_srednie_gole(self, wyniki_docelowe):
        """Oblicz średnią liczbę goli z rozkładu wyników"""
        if not wyniki_docelowe:
            return {"gospodarze": 0, "goscie": 0, "suma": 0}
        
        total_gospodarze = 0
        total_goscie = 0
        total_matches = 0
        
        for wynik_str, data in wyniki_docelowe.items():
            ilosc = data.get("ilosc", 0)
            if ilosc > 0:
                try:
                    gole_dom, gole_wyj = map(int, wynik_str.split(":"))
                    total_gospodarze += gole_dom * ilosc
                    total_goscie += gole_wyj * ilosc
                    total_matches += ilosc
                except:
                    pass
        
        if total_matches > 0:
            return {
                "gospodarze": round(total_gospodarze / total_matches, 2),
                "goscie": round(total_goscie / total_matches, 2),
                "suma": round((total_gospodarze + total_goscie) / total_matches, 2)
            }
        return {"gospodarze": 0, "goscie": 0, "suma": 0}
    
    def wybierz_najlepszy_poziom(self, world_key, min_samples=MIN_SAMPLES_LEVEL_1):
        """
        Wybierz najlepszy poziom świata dla danego klucza.
        
        Algorytm:
        1. Sprawdź pełny świat (poziom3) - jeśli wystarczająco duża próbka, użyj
        2. Jeśli nie, przejdź do poziomu 2
        3. Jeśli nadal za mało, użyj poziomu 1
        
        Zwraca: (poziom, nazwa_poziomu, statystyki)
        """
        levels = self.get_world_levels(world_key)
        
        if not levels:
            return None, None, {}
        
        # Hierarchia: najpierw spróbuj poziom3 (pełny), potem poziom2, potem poziom1
        for poziom in ["poziom3", "poziom2", "poziom1"]:
            if poziom in levels:
                stats = levels[poziom]
                if stats.get("ilosc_przypadkow", 0) >= min_samples:
                    poziom_nazwa = list(levels.keys())[list(levels.keys()).index(poziom)]
                    return poziom, poziom_nazwa, stats
        
        # Jeśli żaden nie spełnia minimum, zwróć ten z największą liczbą przypadków
        best_poziom = None
        best_count = 0
        for poziom, stats in levels.items():
            if stats.get("ilosc_przypadkow", 0) > best_count:
                best_count = stats.get("ilosc_przypadkow", 0)
                best_poziom = poziom
        
        if best_poziom:
            return best_poziom, best_poziom, levels[best_poziom]
        
        return None, None, {}


# ============================================================================
# DYNAMIC WEIGHTS MANAGER
# ============================================================================

class DynamicWeightsManager:
    """
    Zarządza dynamicznymi wagami świata.
    
    Wagi są obliczane przed każdym treningiem na podstawie:
    - ilości przykładów
    - skuteczności świata
    - stabilności korelacji
    - zgodność Dixon-Coles
    """
    
    def __init__(self):
        self.weight_history = {}
    
    def oblicz_wage_swiata(self, poziom, ilosc_przypadkow, procent_gospodarze, 
                          procent_remis, procent_goscie, 
                          korelacje_stabilnosc=1.0, dc_accuracy=1.0):
        """
        Oblicz wagę świata na podstawie różnych czynników.
        
        Wzór: waga = (ilosc_normalized * 0.4) + (skutecznosc_normalized * 0.3) + 
                     (stabilnosc_normalized * 0.2) + (dc_normalized * 0.1)
        """
        # Normalizuj ilość przypadków (0-1, zakładamy max 10000)
        ilosc_norm = min(ilosc_przypadkow / 10000.0, 1.0)
        
        # Skuteczność - na podstawie rozkładu 1X2 (im bardziej zdeterminowany, tym lepiej)
        max_procent = max(procent_gospodarze, procent_remis, procent_goscie)
        skutecznosc_norm = max_procent  # 0-1
        
        # Stabilność korelacji (0-1)
        stabilnosc_norm = korelacje_stabilnosc
        
        # Zgodność Dixon-Coles (0-1)
        dc_norm = dc_accuracy
        
        # Oblicz wagę
        waga_swiata = (0.4 * ilosc_norm + 
                      0.3 * skutecznosc_norm + 
                      0.2 * stabilnosc_norm + 
                      0.1 * dc_norm)
        
        return round(waga_swiata, 4)
    
    def oblicz_wagi_klas(self, procent_gospodarze, procent_remis, procent_goscie,
                        waga_swiata=1.0):
        """
        Oblicz dynamiczne wagi dla klas wyników.
        
        Wagi klas są proporcjonalne do rozkładu, ale modyfikowane przez wagę świata.
        """
        suma = procent_gospodarze + procent_remis + procent_goscie
        
        if suma > 0:
            # Normalizuj proporcje
            waga_gospodarze = (procent_gospodarze / suma) * waga_swiata
            waga_remis = (procent_remis / suma) * waga_swiata
            waga_goscie = (procent_goscie / suma) * waga_swiata
        else:
            waga_gospodarze = waga_remis = waga_goscie = 1.0 / 3.0
        
        # Znormalizuj tak, aby suma wag = waga_swiata
        total_waga = waga_gospodarze + waga_remis + waga_goscie
        if total_waga > 0:
            waga_gospodarze = round(waga_gospodarze / total_waga * waga_swiata, 4)
            waga_remis = round(waga_remis / total_waga * waga_swiata, 4)
            waga_goscie = round(waga_goscie / total_waga * waga_swiata, 4)
        
        return {
            "gospodarze": waga_gospodarze,
            "remis": waga_remis,
            "goscie": waga_goscie
        }
    
    def oblicz_wagi_modelu_i_swiata(self, waga_swiata):
        """
        Oblicz wagę modelu i wagę świata.
        
        Waga modelu = 1 - waga_swiata
        """
        waga_modelu = round(1.0 - waga_swiata, 4)
        return {
            "waga_swiata": round(waga_swiata, 4),
            "waga_modelu": waga_modelu
        }


# ============================================================================
# MODEL POZNAWCZY (TEACHER NETWORK)
# ============================================================================

class CognitiveTeacher:
    """
    Model Poznawczy - analiza historycznych danych i generowanie wiedzy
    dla modelu docelowego.
    
    Korzysta WYŁĄCZNIE z rzeczywistych wyników (Y).
    Nie używa predykcji, danych przyszłych ani mieszania zbiorów.
    """
    
    def __init__(self, df, cechy, siec_name="dataBase_futbol_trend", use_rf=True):
        self.df = df
        self.cechy = cechy
        self.siec_name = siec_name
        self.pamiec_path = os.path.join(KATALOG_MODELE, siec_name, "PAMIEC_MODEL_POZNAWCZY.json")
        self.wiedza_path = os.path.join(KATALOG_MODELE, siec_name, "WIEDZA_DLA_MODELU_DOCELOWEGO.json")
        self.use_rf = use_rf  # Opcja włączania/wyłączania Random Forest
        
        # Inicjalizacja managerów
        self.world_hierarchy = WorldHierarchyManager()
        self.weights_manager = DynamicWeightsManager()
        
        # Historia do pamięci
        self.historia_uczenia = []
        self.wszystkie_wnioski = []
        
        # Pamięć doświadczeń świata (nowa struktura)
        self.swiat_doswiadczenia = {}
        
        # Wczytanie istniejących pamięci
        self.wczytaj_pamiec()
        self.wczytaj_wiedze()
        
    def parse_wynik(self, wynik_str):
        """Rozbij wynik na [gole_gospodarza, gole_gościa, suma_goli]"""
        try:
            gole_dom, gole_wyj = map(int, wynik_str.split(':'))
            return [gole_dom, gole_wyj, gole_dom + gole_wyj]
        except:
            return [0, 0, 0]
    
    def prepare_teacher_targets(self):
        """Przygotuj Y_teacher = [gole_dom, gole_wyj, suma]"""
        if "wynik" not in self.df.columns:
            raise ValueError("Brak kolumny 'wynik' w DataFrame")
        
        y_teacher = []
        for wynik in self.df["wynik"]:
            y_teacher.append(self.parse_wynik(wynik))
        
        return np.array(y_teacher)
    
    def oblicz_korelacje(self, X, y_teacher):
        """Oblicz korelacje Pearsona między cechami a celami"""
        korelacje = {}
        
        for i, cecha in enumerate(self.cechy):
            cecha_values = X[:, i]
            
            korelacje[cecha] = {
                "gole_dom": round(float(stats.pearsonr(cecha_values, y_teacher[:, 0])[0]), 4),
                "gole_wyj": round(float(stats.pearsonr(cecha_values, y_teacher[:, 1])[0]), 4),
                "suma": round(float(stats.pearsonr(cecha_values, y_teacher[:, 2])[0]), 4)
            }
        
        return korelacje
    
    def oblicz_random_forest_importance(self, X, y_teacher):
        """Oblicz Random Forest feature importance dla każdego celu"""
        rf_importance = {}
        
        # Zoptymalizowane parametry RF - mniejsze drzewa, mniej powtórzeń
        rf_params = {
            'n_estimators': 50,     # Zmniejszono z 100 na 50
            'random_state': 42,
            'n_jobs': -1,
            'max_depth': 10,        # Ograniczenie głębokości
            'min_samples_leaf': 5,  # Minimum samples per leaf
            'max_samples': 0.5      # Użyj 50% danych (bagging)
        }
        
        for target_idx, target_name in enumerate(["gole_dom", "gole_wyj", "suma"]):
            print(f"  [TEACHER]rf Fitting RF for {target_name}...")
            rf = RandomForestRegressor(**rf_params)
            rf.fit(X, y_teacher[:, target_idx])
            
            # Standard feature importance
            feature_importance = rf.feature_importances_
            
            # Permutation importance - reduced repeats
            try:
                print(f"  [TEACHER]rf Calculating permutation importance for {target_name}...")
                result = permutation_importance(
                    rf, X, y_teacher[:, target_idx], 
                    n_repeats=5,  # Zmniejszono z 10 na 5
                    random_state=42
                )
                perm_importance = result.importances_mean
            except Exception as e:
                print(f"  [TEACHER]rf Permutation importance failed for {target_name}: {str(e)}")
                perm_importance = feature_importance
            
            for i, cecha in enumerate(self.cechy):
                if cecha not in rf_importance:
                    rf_importance[cecha] = {}
                rf_importance[cecha][f"RF_{target_name}"] = round(float(feature_importance[i]), 4)
                rf_importance[cecha][f"PI_{target_name}"] = round(float(perm_importance[i]), 4)
        
        return rf_importance
    
    def oblicz_dixon_coles(self, X, y_teacher):
        """Oblicz Dixon-Coles style feature strength"""
        # Uproszczona wersja Dixon-Coles - używamy standaryzowanej siły cechy
        dc_stength = {}
        
        # Standaryzuj cechy
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        for i, cecha in enumerate(self.cechy):
            cecha_values = X_scaled[:, i]
            
            # Dixon-Coles inspired: combined effect on all targets
            dc_scores = []
            for target_idx in range(3):  # gole_dom, gole_wyj, suma
                # Normalized correlation-like score
                corr = abs(stats.pearsonr(cecha_values, y_teacher[:, target_idx])[0])
                dc_scores.append(corr)
            
            # Average DC score
            dc_stength[cecha] = round(float(np.mean(dc_scores)), 4)
        
        return dc_stength
    
    def oblicz_sile_cechy(self, korelacje, rf_importance, dc_stength):
        """Oblicz łączną siłę cechy (waga korelacji, RF, DC)"""
        sila_cech = {}
        
        # Zabezpieczenie na wypadek None
        if dc_stength is None:
            dc_stength = {}
        if rf_importance is None:
            rf_importance = {}
        
        for cecha in self.cechy:
            k = korelacje.get(cecha, {})
            rf = rf_importance.get(cecha, {})
            dc = dc_stength.get(cecha, 0) if isinstance(dc_stength, dict) else 0
            
            # Średnia z absolutnych wartości korelacji
            avg_korelacja = (abs(k.get("gole_dom", 0)) + 
                           abs(k.get("gole_wyj", 0)) + 
                           abs(k.get("suma", 0))) / 3
            
            # Średnia z RF importance
            rf_values = [v for k, v in rf.items() if k.startswith("RF_")]
            avg_rf = np.mean(rf_values) if rf_values else 0
            
            # Łączna siła (Weighted average)
            sila = 0.4 * avg_korelacja + 0.4 * avg_rf + 0.2 * dc
            sila_cech[cecha] = round(float(sila), 4)
        
        return sila_cech
    
    def ranking_cech(self, sila_cech, korelacje, rf_importance, dc_stength):
        """Stwórz ranking cech według siły"""
        ranking = []
        
        for cecha in self.cechy:
            k = korelacje.get(cecha, {})
            rf = rf_importance.get(cecha, {})
            
            ranking.append({
                "cecha": cecha,
                "korelacja": {
                    "gole_dom": k.get("gole_dom", 0),
                    "gole_wyj": k.get("gole_wyj", 0),
                    "suma": k.get("suma", 0)
                },
                "RF": rf.get("RF_gole_dom", 0) if rf else 0,
                "DC": dc_stength.get(cecha, 0) if dc_stength else 0,
                "sila": sila_cech.get(cecha, 0)
            })
        
        # Sortuj po sile (malejąco)
        ranking.sort(key=lambda x: x["sila"], reverse=True)
        
        return ranking
    
    def generuj_wnioski(self, ranking, top_n=10):
        """Generuj wnioski z analizy"""
        wnioski = []
        top_cechy = ranking[:top_n]
        
        for cecha_info in top_cechy:
            cecha = cecha_info["cecha"]
            k = cecha_info["korelacja"]
            sila = cecha_info["sila"]
            
            # Określ typ wpływu
            if k["gole_dom"] >= 0.5:
                wnioski.append(f"{cecha} silnie wpływa na gole gospodarza (korelacja: {k['gole_dom']})")
            if k["gole_dom"] <= -0.5:
                wnioski.append(f"{cecha} negatywnie wpływa na gole gospodarza (korelacja: {k['gole_dom']})")
            
            if k["gole_wyj"] >= 0.5:
                wnioski.append(f"{cecha} silnie wpływa na gole gości (korelacja: {k['gole_wyj']})")
            if k["gole_wyj"] <= -0.5:
                wnioski.append(f"{cecha} negatywnie wpływa na gole gości (korelacja: {k['gole_wyj']})")
            
            if k["suma"] >= 0.5:
                wnioski.append(f"{cecha} silnie wpływa na sumę goli (korelacja: {k['suma']})")
            if k["suma"] <= -0.5:
                wnioski.append(f"{cecha} negatywnie wpływa na sumę goli (korelacja: {k['suma']})")
        
        return wnioski
    
    def generuj_reguly(self, ranking, top_n=5):
        """Generuj reguły dla modelu docelowego"""
        reguly = []
        
        for cecha_info in ranking[:top_n]:
            cecha = cecha_info["cecha"]
            k = cecha_info["korelacja"]
            sila = cecha_info["sila"]
            
            # Określ typ reguły na podstawie korelacji
            # Obniżono próg z 0.3 do 0.1, aby generować reguły również dla słabszych korelacji
            if abs(k["gole_dom"]) >= abs(k["gole_wyj"]) and abs(k["gole_dom"]) >= 0.1:
                warunek = {"cecha": cecha, "typ": "wysokie" if k["gole_dom"] > 0 else "niskie"}
                konsekwencja = {"gole_gospodarzy": "częściej zwiększone" if k["gole_dom"] > 0 else "częściej zmniejszone"}
                reguly.append({
                    "warunek": warunek,
                    "konsekwencja": konsekwencja,
                    "pewnosc": min(sila, 0.99)
                })
            
            elif abs(k["gole_wyj"]) >= 0.1:
                warunek = {"cecha": cecha, "typ": "wysokie" if k["gole_wyj"] > 0 else "niskie"}
                konsekwencja = {"gole_gości": "częściej zwiększone" if k["gole_wyj"] > 0 else "częściej zmniejszone"}
                reguly.append({
                    "warunek": warunek,
                    "konsekwencja": konsekwencja,
                    "pewnosc": min(sila, 0.99)
                })
        
        return reguly
    
    def analiza_zmian(self, nowy_ranking, stara_pamiec=None):
        """Porównaj nowy ranking z poprzednią pamięcią"""
        zmiany = {
            "nowe_zaleznosci": [],
            "utracone_zaleznosci": [],
            "poprawione_zaleznosci": []
        }
        
        # Jeśli istnieje stara pamięć, porównaj
        if stara_pamiec and "historia_uczenia" in stara_pamiec:
            ostatnia_historia = stara_pamiec["historia_uczenia"][-1] if stara_pamiec["historia_uczenia"] else None
            if ostatnia_historia and "najwazniejsze_cechy" in ostatnia_historia:
                stare_cechy = {c["cecha"]: c["sila"] for c in ostatnia_historia["najwazniejsze_cechy"]}
                nowe_cechy = {c["cecha"]: c["sila"] for c in nowy_ranking[:10]}
                
                # Nowe zależności (w nowym top 10, nie w starym)
                for cecha, sila in nowe_cechy.items():
                    if cecha not in stare_cechy:
                        zmiany["nowe_zaleznosci"].append({"cecha": cecha, "sila": sila})
                    elif sila > stare_cechy[cecha] + 0.1:  # Wzrost o > 0.1
                        zmiany["poprawione_zaleznosci"].append({
                            "cecha": cecha,
                            "stara_sila": stare_cechy[cecha],
                            "nowa_sila": sila
                        })
                
                # Utracone zależności (w starym top 10, nie w nowym)
                for cecha, sila in stare_cechy.items():
                    if cecha not in nowe_cechy:
                        zmiany["utracone_zaleznosci"].append({"cecha": cecha, "sila": sila})
        
        return zmiany
    
    def zapisz_pamiec(self, ranking, wnioski, zmiany, liczba_meczow):
        """Zapisz pamięć modelu poznawczego"""
        nowa_historia = {
            "liczba_meczow": liczba_meczow,
            "data_analizy": None,  # Nie zapisujemy dat
            "najwazniejsze_cechy": ranking[:20],  # Top 20 cech
            "wnioski": wnioski,
            "zmiany": zmiany
        }
        
        self.historia_uczenia.append(nowa_historia)
        
        pamiec = {
            "wersja": 1,
            "sieć": self.siec_name,
            "historia_uczenia": self.historia_uczenia,
            "wszystkie_wnioski": self.wszystkie_wnioski + wnioski
        }
        
        os.makedirs(os.path.dirname(self.pamiec_path), exist_ok=True)
        with open(self.pamiec_path, "w", encoding="utf-8") as f:
            json.dump(pamiec, f, indent=4, ensure_ascii=False)
        
        return pamiec
    
    def zapisz_wiedze(self, reguly, wagi_info=None):
        """
        Zapisz wiedzę dla modelu docelowego (nowa struktura zgodna z promptem).
        
        Format zgodny z punktem 3 promptu:
        - rekomendowana klasa
        - prawdopodobieństwo
        - dynamiczne wagi
        - najważniejsze cechy
        - poziom pewności
        - wybrany świat
        """
        # Wyznacz rekomendowaną klasę na podstawie rozkładu
        if wagi_info:
            wagi_klas = wagi_info.get("wagi_klas", {})
            # Rekomendacja to klasa z najwyższą wagą
            max_waga = max(wagi_klas.get("gospodarze", 0), 
                          wagi_klas.get("remis", 0), 
                          wagi_klas.get("goscie", 0))
            
            if max_waga == wagi_klas.get("gospodarze", 0):
                rekomendacja = "WYGRANA_GOSPODARZE"
                pewnosc = wagi_klas.get("gospodarze", 0)
            elif max_waga == wagi_klas.get("remis", 0):
                rekomendacja = "REMIS"
                pewnosc = wagi_klas.get("remis", 0)
            else:
                rekomendacja = "WYGRANA_GOSCIE"
                pewnosc = wagi_klas.get("goscie", 0)
        else:
            rekomendacja = "BRAK_DECYZJI"
            pewnosc = 0.0
        
        # Stablicz poziom pewności (0-1)
        pewnosc = round(min(pewnosc, 1.0), 4)
        
        wiedza = {
            "wersja": 2,
            "sieć": self.siec_name,
            "data_generowania": None,
            "teacher": {
                "rekomendacja": rekomendacja,
                "pewnosc": pewnosc
            },
            "wagi": wagi_info.get("wagi_klas", {}) if wagi_info else {},
            "swiat": {
                "uzyty": wagi_info.get("nazwa_poziomu", "") if wagi_info else "",
                "poziom": wagi_info.get("poziom_swiata", "") if wagi_info else "",
                "ilosc_przykladow": wagi_info.get("ilosc_przykladow", 0) if wagi_info else 0
            },
            "reguly": reguly
        }
        
        os.makedirs(os.path.dirname(self.wiedza_path), exist_ok=True)
        with open(self.wiedza_path, "w", encoding="utf-8") as f:
            json.dump(wiedza, f, indent=4, ensure_ascii=False)
        
        return wiedza
    
    def wczytaj_pamiec(self):
        """Wczytaj poprzednią pamięć"""
        if os.path.exists(self.pamiec_path):
            with open(self.pamiec_path, "r", encoding="utf-8") as f:
                pamiec = json.load(f)
                self.historia_uczenia = pamiec.get("historia_uczenia", [])
                self.wszystkie_wnioski = pamiec.get("wszystkie_wnioski", [])
                self.swiat_doswiadczenia = pamiec.get("doswiadczenie_swiata", {})
                return pamiec
        return None
    
    def wczytaj_wiedze(self):
        """Wczytaj poprzednią wiedzę dla modelu docelowego"""
        if os.path.exists(self.wiedza_path):
            try:
                with open(self.wiedza_path, "r", encoding="utf-8") as f:
                    wiedza = json.load(f)
                return wiedza
            except Exception as e:
                print(f"  [TEACHER] Błąd wczytywania wiedzy: {e}")
        return None
    
    def uruchom_analyse(self):
        """Główna metoda - wykonaj pełną analizę"""
        print("  [TEACHER] Wczytano pamięć poznawczą")
        print("  [TEACHER] Wczytano wiedzę dla modelu docelowego")
        
        # 1. Wczytaj poprzednią pamięć
        stara_pamiec = self.wczytaj_pamiec()
        
        # 2. Przygotuj dane
        print("  [TEACHER] 2/7 Przygotowanie danych X i Y...")
        X = self.df[self.cechy].values
        y_teacher = self.prepare_teacher_targets()
        
        # 3. Oblicz wszystkie miary
        print("  [TEACHER] 3/7 Obliczanie korelacji Pearsona...")
        korelacje = self.oblicz_korelacje(X, y_teacher)
        
        print("  [TEACHER] 4/7 Obliczanie Random Forest Importance (to może chwilę potrwać)...")
        if self.use_rf:
            rf_importance = self.oblicz_random_forest_importance(X, y_teacher)
        else:
            print("  [TEACHER]rf Random Forest wyłączony - używam tylko korelacji")
            rf_importance = {cecha: {} for cecha in self.cechy}
        
        print("  [TEACHER] 5/7 Obliczanie Dixon-Coles Strength...")
        dc_stength = self.oblicz_dixon_coles(X, y_teacher)
        
        print("  [TEACHER] 6/7 Obliczanie siły cech i tworzenie rankingu...")
        sila_cech = self.oblicz_sile_cechy(korelacje, rf_importance, dc_stength)
        ranking = self.ranking_cech(sila_cech, korelacje, rf_importance, dc_stength)
        
        # 4. ANALIZA HIERARCHICZNA ŚWIATÓW
        print("  [TEACHER] Wybrano poziom świata")
        swiat_info = self.analizuj_hierarchie_swiatow(X, y_teacher, korelacje, rf_importance, dc_stength)
        
        # 5. OBLICZ DYNAMICZNE WAGI
        print("  [TEACHER] Obliczono korelacje cech")
        print("  [TEACHER] Obliczono Dixon-Coles")
        wagi_info = self.oblicz_dynamiczne_wagi(swiat_info, korelacje, dc_stength)
        
        # 6. Generuj wnioski i reguły
        print("  [TEACHER] 7/7 Generowanie wniosków, reguł i zapis...")
        wnioski = self.generuj_wnioski(ranking)
        reguly = self.generuj_reguly(ranking)
        
        # 7. Analiza zmian
        zmiany = self.analiza_zmian(ranking, stara_pamiec)
        
        # 8. Zapisz pamięć i wiedzę (nowa struktura)
        pamiec = self.zapisz_pamiec(ranking, wnioski, zmiany, len(self.df))
        wiedza = self.zapisz_wiedze(reguly, wagi_info)
        
        # 9. Zapisz doświadczenie świata
        self.zapisz_doswiadczenie_swiata(swiat_info, wagi_info, ranking)
        
        return {
            "pamiec": pamiec,
            "wiedza": wiedza,
            "ranking": ranking,
            "wnioski": wnioski,
            "reguly": reguly,
            "zmiany": zmiany,
            "swiat": swiat_info,
            "wagi": wagi_info
        }
    
    def analizuj_hierarchie_swiatow(self, X, y_teacher, korelacje, rf_importance, dc_stength):
        """
        Analizuj hierarchię światów dla meczy w DataFrame.
        Wybiera najlepszy poziom świata dla każdego meczu.
        """
        print("  [TEACHER] Analiza hierarchii światów...")
        
        # Inicjalizuj strukturę doświadczenia świata
        swiat_analiza = {
            "mecze": {},
            "statystyki_globalne": {
                "ilosc_meczow": len(self.df),
                "poziomy_wyboru": {"poziom1": 0, "poziom2": 0, "poziom3": 0},
                "srednie_wagi": {}
            }
        }
        
        # Jeśli mamy kolumnę id_meczu i dane światów, analizuj indywidualnie
        if "id_meczu" in self.df.columns:
            for idx, row in self.df.iterrows():
                mecz_id = str(row["id_meczu"])
                
                # Wybierz najlepszy poziom świata dla tego meczu
                poziom, poziom_nazwa, stats = self.world_hierarchy.wybierz_najlepszy_poziom(mecz_id)
                
                if poziom and stats and stats.get("ilosc_przypadkow", 0) > 0:
                    swiat_analiza["mecze"][mecz_id] = {
                        "poziom": poziom,
                        "nazwa_poziomu": poziom_nazwa,
                        "ilosc_przypadkow": stats.get("ilosc_przypadkow", 0),
                        "procent_gospodarze": stats.get("procent_gospodarze", 0),
                        "procent_remis": stats.get("procent_remis", 0),
                        "procent_goscie": stats.get("procent_goscie", 0),
                        "srednie_gole": stats.get("srednie_gole", {})
                    }
                    swiat_analiza["statystyki_globalne"]["poziomy_wyboru"][poziom] += 1
        else:
            # Jeśli nie ma id_meczu, traktuj wszystkie mecze jako jedną grupę
            # Użyj domyślnego świata
            poziom, poziom_nazwa, stats = self.world_hierarchy.wybierz_najlepszy_poziom("default")
            if poziom and stats:
                swiat_analiza["statystyki_globalne"]["domyslny_poziom"] = {
                    "poziom": poziom,
                    "nazwa_poziomu": poziom_nazwa,
                    "ilosc_przypadkow": stats.get("ilosc_przypadkow", 0),
                    "procent_gospodarze": stats.get("procent_gospodarze", 0),
                    "procent_remis": stats.get("procent_remis", 0),
                    "procent_goscie": stats.get("procent_goscie", 0)
                }
        
        return swiat_analiza
    
    def oblicz_dynamiczne_wagi(self, swiat_info, korelacje, dc_stength):
        """
        Oblicz dynamiczne wagi dla świata i cech.
        """
        print("  [TEACHER] Obliczanie dynamicznych wag...")
        
        # Pobierz statystyki globalne
        global_stats = swiat_info.get("statystyki_globalne", {})
        domyslny = global_stats.get("domyslny_poziom", {})
        
        if domyslny:
            ilosc = domyslny.get("ilosc_przypadkow", 0)
            pct_gosp = domyslny.get("procent_gospodarze", 0)
            pct_remis = domyslny.get("procent_remis", 0)
            pct_goscie = domyslny.get("procent_goscie", 0)
        else:
            # Domyślne wartości
            ilosc = len(self.df)
            pct_gosp = pct_remis = pct_goscie = 1.0 / 3.0
        
        # Oblicz średnią stabilność korelacji
        korelacja_values = []
        for cecha, k in korelacje.items():
            korelacja_values.extend([abs(v) for v in k.values()])
        korelacje_stabilnosc = round(np.mean(korelacja_values), 4) if korelacja_values else 1.0
        
        # Oblicz średnią DC strength
        dc_values = list(dc_stength.values()) if dc_stength else []
        dc_accuracy = round(np.mean(dc_values), 4) if dc_values else 1.0
        
        # Oblicz wagę świata
        poziom = domyslny.get("poziom", "poziom1")
        waga_swiata = self.weights_manager.oblicz_wage_swiata(
            poziom, ilosc, pct_gosp, pct_remis, pct_goscie,
            korelacje_stabilnosc, dc_accuracy
        )
        
        # Oblicz wagi klas
        wagi_klas = self.weights_manager.oblicz_wagi_klas(
            pct_gosp, pct_remis, pct_goscie, waga_swiata
        )
        
        # Oblicz wagi modelu i świata
        wagi_model_swiat = self.weights_manager.oblicz_wagi_modelu_i_swiata(waga_swiata)
        
        # Informacje o cechach (ranking cech według siły)
        sila_cech = self.oblicz_sile_cechy(korelacje, {}, dc_stength)
        ranking_cech = sorted(sila_cech.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "waga_swiata": wagi_model_swiat["waga_swiata"],
            "waga_modelu": wagi_model_swiat["waga_modelu"],
            "wagi_klas": wagi_klas,
            "poziom_swiata": poziom,
            "ilosc_przykladow": ilosc,
            "korelacje_stabilnosc": korelacje_stabilnosc,
            "dc_accuracy": dc_accuracy,
            "nazwa_poziomu": domyslny.get("nazwa_poziomu", ""),
            "najwazniejsze_cechy": [{"cecha": c, "sila": s} for c, s in ranking_cech]
        }
    
    def zapisz_doswiadczenie_swiata(self, swiat_info, wagi_info, ranking):
        """
        Zapisz doświadczenie świata do pamięci (nowa struktura zgodna z promptem).
        """
        print("  [TEACHER] Zaktualizowano pamięć")
        
        # âgée do przechowywania pojedynczego doświadczenia
        doswiadczenie = {}
        
        # Dla poszczególnych meczy
        for mecz_id, info in swiat_info.get("mecze", {}).items():
            doswiadczenie[mecz_id] = {
                "id_meczu": mecz_id,
                "swiat": {
                    "poziom": info.get("poziom", ""),
                    "uzyty": info.get("nazwa_poziomu", ""),
                    "ilosc_przypadkow": info.get("ilosc_przypadkow", 0)
                },
                "cechy": {},
                "wyniki": {
                    "gospodarze": info.get("procent_gospodarze", 0),
                    "remis": info.get("procent_remis", 0),
                    "goscie": info.get("procent_goscie", 0)
                }
            }
            
            # Dodaj cechy z rankingu
            for cecha_info in ranking[:10]:  # Top 10 cech
                cecha = cecha_info.get("cecha", "")
                korelacja = cecha_info.get("korelacja", {})
                rf = cecha_info.get("RF", 0)
                dc = cecha_info.get("DC", 0)
                sila = cecha_info.get("sila", 0)
                
                doswiadczenie[mecz_id]["cechy"][cecha] = {
                    "korelacja": korelacja,
                    "RF": rf,
                    "DC": dc,
                    "sila": sila
                }
        
        # Zaktualizuj globalne doświadczenie
        if "statystyki_globalne" in swiat_info:
            globalne = swiat_info["statystyki_globalne"]
            self.swiat_doswiadczenia = {
                "aktualny_swiat": {
                    "nazwa": globalne.get("domyslny_poziom", {}).get("nazwa_poziomu", ""),
                    "poziom": globalne.get("domyslny_poziom", {}).get("poziom", ""),
                    "ilosc_przypadkow": globalne.get("domyslny_poziom", {}).get("ilosc_przypadkow", 0)
                },
                "wagi": wagi_info,
                "mecze": doswiadczenie
            }
        
        # Zapisz do pliku (nowa struktura)
        self._zapisz_nowa_pamiec_swiata()
    
    def _zapisz_nowa_pamiec_swiata(self):
        """Zapisz nową strukturę pamięci do pliku"""
        # Scal stare dane z nowymi
        nowa_pamiec = {
            "wersja": 2,
            "sieć": self.siec_name,
            "historia_uczenia": self.historia_uczenia,
            "wszystkie_wnioski": self.wszystkie_wnioski,
            "doswiadczenie_swiata": self.swiat_doswiadczenia
        }
        
        os.makedirs(os.path.dirname(self.pamiec_path), exist_ok=True)
        with open(self.pamiec_path, "w", encoding="utf-8") as f:
            json.dump(nowa_pamiec, f, indent=4, ensure_ascii=False)


# ============================================================================
# FUNKCJE PAMIĘCI ŚWIATÓW I ANALIZY WZORCÓW
# ============================================================================

def wyodrebnij_grupe_kursowa(mecz_id):
    """Wyodrębnij grupę kursową z identyfikatora meczu."""
    if pd.isna(mecz_id):
        return "nieznana"
    
    mecz_str = str(mecz_id)
    
    if "kurs" in mecz_str.lower():
        parts = mecz_str.replace("-", "_").split("_")
        for i, part in enumerate(parts):
            if "kurs" in part.lower():
                if i + 1 < len(parts):
                    return "_".join(parts[i:i+3])
    
    return mecz_str.replace("-", "_").replace(":", "_").replace("/", "_")


def analiza_rozkładu_wynikow(y_true_indices, y_pred_indices, wszystkie_wyniki=WYNIKI):
    """Analizuj rozkład wyników dla grupy."""
    true_results = [wszystkie_wyniki[i] for i in y_true_indices]
    pred_results = [wszystkie_wyniki[i] for i in y_pred_indices]
    
    true_counter = Counter(true_results)
    pred_counter = Counter(pred_results)
    
    true_dominujace = true_counter.most_common(3)
    pred_dominujace = pred_counter.most_common(3)
    
    trend_analiza = {}
    for wynik, true_count in true_counter.items():
        pred_count = pred_counter.get(wynik, 0)
        if true_count > 0:
            trend_analiza[wynik] = {
                "rzeczywiste": true_count,
                "przewidywane": pred_count,
                "stosunek": round(pred_count / true_count, 4) if true_count > 0 else 0
            }
    
    najczestszy_true = true_counter.most_common(1)[0][0] if true_counter else None
    najczestszy_pred = pred_counter.most_common(1)[0][0] if pred_counter else None
    
    remisy_true = sum(true_counter.get(w, 0) for w in ["0:0", "1:1", "2:2"])
    remisy_pred = sum(pred_counter.get(w, 0) for w in ["0:0", "1:1", "2:2"])
    total_true = len(true_results)
    total_pred = len(pred_results)
    
    return {
        "rozkład_rzeczywisty": dict(true_counter),
        "rozkład_przewidywany": dict(pred_counter),
        "dominujące_rzeczywiste": [w for w, c in true_dominujace],
        "dominujące_przewidywane": [w for w, c in pred_dominujace],
        "najczestszy_rzeczywisty": najczestszy_true,
        "najczestszy_przewidywany": najczestszy_pred,
        "procent_remisow_rzeczywisty": round(remisy_true / total_true, 4) if total_true > 0 else 0,
        "procent_remisow_przewidywany": round(remisy_pred / total_pred, 4) if total_pred > 0 else 0,
        "trend_analiza": trend_analiza
    }


def sprawdz_wzorce_grupowe(grupa_data, y_true, y_pred, wszystkie_wyniki=WYNIKI):
    """Sprawdź wzorce dla konkretnej grupy."""
    analiza = {
        "grupa": grupa_data.get("identyfikator", "nieznana"),
        "ilość_przykladow": grupa_data.get("ilość", 0),
        "poprawne_predykcje": 0,
        "błędy": [],
        "wymaga_doszkolenia": False,
        "stabilność": 1.0
    }
    
    if len(y_true) == 0 or len(y_pred) == 0:
        return analiza
    
    correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    total = len(y_true)
    accuracy = correct / total if total > 0 else 0
    analiza["poprawne_predykcje"] = correct
    analiza["dokładność_grupy"] = round(accuracy, 4)
    
    bledy = []
    for true_idx, pred_idx in zip(y_true, y_pred):
        if true_idx != pred_idx:
            bledy.append({
                "rzeczywisty": wszystkie_wyniki[true_idx],
                "przewidywany": wszystkie_wyniki[pred_idx]
            })
    analiza["błędy"] = bledy
    
    result_analysis = analiza_rozkładu_wynikow(y_true, y_pred, wszystkie_wyniki)
    analiza["rozkład"] = result_analysis
    
    if len(bledy) > 0:
        error_counter = Counter()
        for error in bledy:
            error_key = f"{error['rzeczywisty']}->{error['przewidywany']}"
            error_counter[error_key] += 1
        
        najczestszy_blad = error_counter.most_common(1)[0] if error_counter else None
        if najczestszy_blad and najczestszy_blad[1] >= max(3, len(bledy) * 0.5):
            analiza["systematyczny_błąd"] = najczestszy_blad[0]
            analiza["wymaga_doszkolenia"] = True
    
    if (result_analysis["procent_remisow_przewidywany"] > result_analysis["procent_remisow_rzeczywisty"] * 1.5 and
        result_analysis["procent_remisow_rzeczywisty"] < 0.3):
        analiza["zawyżone_remisy"] = True
        analiza["wymaga_doszkolenia"] = True
    
    if total > 5:
        analiza["stabilność"] = round(accuracy, 4)
    
    if result_analysis["najczestszy_przewidywany"] != result_analysis["najczestszy_rzeczywisty"]:
        analiza["zmiana_wzorca"] = {
            "model_preferuje": result_analysis["najczestszy_przewidywany"],
            "rzeczywistość_preferuje": result_analysis["najczestszy_rzeczywisty"]
        }
        analiza["wymaga_doszkolenia"] = True
    
    return analiza


def generuj_pamiec_swiatow(df, y_obserwacja, klasy_40, nazwa_sieci, wszystkie_wyniki=WYNIKI):
    """Generuj pamięć światów na podstawie analizy grup."""
    pamiec = {
        "sieć": nazwa_sieci,
        "data_generowania": None,
        "grupy": {},
        "statystyki_globalne": {
            "ilość_grup": 0,
            "ilość_obserwacji": len(y_obserwacja),
            "poprawne_interpretacje": 0,
            "błędne_grupy": 0,
            "grupy_wymagajace_doszkolenia": []
        }
    }
    
    obs_start_idx = len(df) - len(y_obserwacja)
    
    if "id_meczu" in df.columns:
        grupa_do_indeksow = defaultdict(list)
        for local_idx, global_idx in enumerate(range(obs_start_idx, len(df))):
            grupa = wyodrebnij_grupe_kursowa(df.iloc[global_idx]["id_meczu"])
            grupa_do_indeksow[grupa].append(local_idx)
        
        global_poprawne = 0
        global_bledne_grupy = 0
        
        for grupa, local_indices in grupa_do_indeksow.items():
            group_y_true = [y_obserwacja[i] for i in local_indices]
            group_y_pred = [klasy_40[i] for i in local_indices]
            
            if len(group_y_true) > 0:
                grupa_analiza = sprawdz_wzorce_grupowe(
                    {"identyfikator": grupa, "ilość": len(group_y_true)},
                    group_y_true,
                    group_y_pred,
                    wszystkie_wyniki
                )
                
                pamiec["grupy"][grupa] = grupa_analiza
                
                if grupa_analiza["wymaga_doszkolenia"]:
                    pamiec["statystyki_globalne"]["grupy_wymagajace_doszkolenia"].append(grupa)
                    global_bledne_grupy += 1
                
                global_poprawne += grupa_analiza["poprawne_predykcje"]
        
        pamiec["statystyki_globalne"]["ilość_grup"] = len(grupa_do_indeksow)
        pamiec["statystyki_globalne"]["poprawne_interpretacje"] = global_poprawne
        pamiec["statystyki_globalne"]["błędne_grupy"] = global_bledne_grupy
    else:
        grupa_analiza = sprawdz_wzorce_grupowe(
            {"identyfikator": "calosc", "ilość": len(y_obserwacja)},
            list(y_obserwacja),
            list(klasy_40),
            wszystkie_wyniki
        )
        pamiec["grupy"]["calosc"] = grupa_analiza
        pamiec["statystyki_globalne"]["ilość_grup"] = 1
        pamiec["statystyki_globalne"]["poprawne_interpretacje"] = grupa_analiza["poprawne_predykcje"]
        pamiec["statystyki_globalne"]["błędne_grupy"] = 1 if grupa_analiza["wymaga_doszkolenia"] else 0
        if grupa_analiza["wymaga_doszkolenia"]:
            pamiec["statystyki_globalne"]["grupy_wymagajace_doszkolenia"].append("calosc")
    
    return pamiec


def generuj_laboratorium_uczenia(wszystkie_wyniki, eksperyment_num=1):
    """Generuj raport laboratorium uczenia."""
    total_dane = 0
    total_grupy = 0
    total_poprawne = 0
    total_bledne = 0
    total_korekty = 0
    zmiany_zachowania = []
    
    for siec_result in wszystkie_wyniki:
        if isinstance(siec_result, dict) and "pamięć" in siec_result:
            pamiec = siec_result["pamięć"]
            stats = pamiec.get("statystyki_globalne", {})
            
            total_dane += stats.get("ilość_obserwacji", 0)
            total_grupy += stats.get("ilość_grup", 0)
            total_poprawne += stats.get("poprawne_interpretacje", 0)
            total_bledne += stats.get("błędne_grupy", 0)
            total_korekty += len(stats.get("grupy_wymagajace_doszkolenia", []))
            
            for grupa, analiza in pamiec.get("grupy", {}).items():
                if "zmiana_wzorca" in analiza:
                    zmiany_zachowania.append({
                        "grupa": grupa,
                        "ze": analiza["zmiana_wzorca"]["model_preferuje"],
                        "na": analiza["zmiana_wzorca"]["rzeczywistość_preferuje"]
                    })
    
    najwieksze_zmiany = sorted(
        zmiany_zachowania, 
        key=lambda x: (x["ze"], x["na"]),
        reverse=True
    )[:5]
    
    return {
        "numer_eksperymentu": eksperyment_num,
        "ilość_danych": total_dane,
        "ilość_grup": total_grupy,
        "ilość_poprawnych_interpretacji": total_poprawne,
        "ilość_błędnych_grup": total_bledne,
        "ilość_korekt": total_korekty,
        "największe_zmiany_zachowania": [
            {"grupa": z["grupa"], "ze": z["ze"], "na": z["na"]}
            for z in najwieksze_zmiany
        ],
        "informacje_o_procesie_uczenia": {
            "typ_podziału": "chronologiczny",
            "procent_treningu": "60%",
            "procent_walidacji": "20%", 
            "procent_obserwacji": "20%",
            "użyto_pamięci_światów": True,
            "użyto_analizy_wzorców": True,
            "użyto_modelu_poznawczego": True
        }
    }


# ============================================================================
# FUNKCJA PODZIAŁU DANYCH CHRONOLOGICZNEGO
# ============================================================================

def podziel_dane_chronologicznie(
    X,
    y,
    train_ratio=0.60,
    val_ratio=0.20
):
    """
    Chronologiczny podział danych bez mieszania.
    
    STARE DANE ------------------------------ NOWE DANE
    |---------------|---------------|---------------|
        trening        walidacja       obserwacja
    """
    total_samples = len(X)
    
    train_end = int(total_samples * train_ratio)
    val_end = int(total_samples * (train_ratio + val_ratio))
    
    X_train = X[:train_end]
    X_val = X[train_end:val_end]
    X_obserwacja = X[val_end:]
    
    y_train = y[:train_end]
    y_val = y[train_end:val_end]
    y_obserwacja = y[val_end:]
    
    return (
        X_train,
        X_val,
        X_obserwacja,
        y_train,
        y_val,
        y_obserwacja
    )


def podziel_dane(
    X,
    y
):
    """Oryginalna funkcja podziału z losowym mieszaniem - zachowana dla referencji."""
    X_temp, X_obserwacja, y_temp, y_obserwacja = train_test_split(
        X,
        y,
        test_size=0.40,
        random_state=42,
        stratify=y
    )

    X_train, X_val, y_train, y_val = train_test_split(
        X_temp,
        y_temp,
        test_size=0.166666,
        random_state=42,
        stratify=y_temp
    )
    
    return (
        X_train,
        X_val,
        X_obserwacja,
        y_train,
        y_val,
        y_obserwacja
    )


# WCZYTANIE SCHEMATU KOLUMN

print(
    "Wczytywanie nagłówków..."
)

predykcja = pd.read_csv(
    PLIK_PREDYKCJI,
    sep=";",
    encoding="utf-8"
)

NAGLOWKI = list(
    predykcja.columns
)

print(
    "Kolumny:",
    len(NAGLOWKI)
)

# WCZYTANIE HISTORII BEZ NAGŁÓWKA

print(
    "Wczytywanie treningu..."
)

df = pd.read_csv(
    PLIK_TRENING,
    sep=";",
    encoding="utf-8",
    header=None
)

df.columns = NAGLOWKI + [
    "wynik"
]

print(
    "Rekordów:",
    len(df)
)

# FILTR POPRAWNYCH WYNIKÓW

df = df[
    df["wynik"].isin(WYNIKI)
].copy()

print(
    "Po filtrze:",
    len(df)
)

# IDENTYFIKACJA KLASY

df["klasa"] = (
    df["wynik"]
    .map(MAPA_KLAS)
)

# ============================================================================
# BUDOWA SIECI Z INTEGRACJĄ MODELU POZNAWCZEGO
# ============================================================================

def buduj_siec(
    nazwa,
    cechy,
    df_global
):

    print("\\n===============================")
    print(
        "START:",
        nazwa
    )
    print(
        "CECHY:",
        cechy
    )

    katalog = os.path.join(
        KATALOG_MODELE,
        nazwa
    )

    os.makedirs(
        katalog,
        exist_ok=True
    )

    # ========================================================================
    # MODEL POZNAWCZY (TEACHER) - ANALIZA PRZED TRENINGIEM
    # ========================================================================
    print("  [TEACHER] Uruchamianie Modelu Poznawczego...")
    print(f"  [TEACHER] Liczba meczów do analizy: {len(df_global)}")
    print(f"  [TEACHER] Liczba cech: {len(cechy)}")
    
    # Na początek wyłączamy RF dla dużych zbiorów dla wydajności
    use_rf_flag = len(df_global) < 10000  # Wyłącz RF dla dużych zbiorów 
    if len(df_global) >= 10000:
        print(f"  [TEACHER] UWAGA: Duży zbiór ({len(df_global)} rekordów) - Random Forest wyłączony dla wydajności")
    
    teacher = CognitiveTeacher(df_global, cechy, nazwa, use_rf=use_rf_flag)
    teacher_result = teacher.uruchom_analyse()
    
    print(f"  [TEACHER] Zanalizowano {len(df_global)} meczów")
    print(f"  [TEACHER] Top 3 cechy: {teacher_result['ranking'][:3]}")
    print(f"  [TEACHER] Liczba wniosków: {len(teacher_result['wnioski'])}")
    print(f"  [TEACHER] Liczba reguł: {len(teacher_result['reguly'])}")
    
    # ----------------------------------
    # DANE DLA KONKRETNEJ SIECI
    # ----------------------------------

    X = df_global[cechy].values
    y = df_global["klasa"].values

    # ----------------------------------
    # PODZIAŁ CHRONOLOGICZNY 60 / 20 / 20
    # ----------------------------------

    (
        X_train,
        X_val,
        X_obserwacja,
        y_train,
        y_val,
        y_obserwacja
    ) = podziel_dane_chronologicznie(
        X,
        y,
        train_ratio=0.60,
        val_ratio=0.20
    )

    # ----------------------------------
    # NORMALIZACJA
    # ----------------------------------

    scaler = StandardScaler()

    X_train = scaler.fit_transform(
        X_train
    )

    X_val = scaler.transform(
        X_val
    )

    X_obserwacja = scaler.transform(
        X_obserwacja
    )

    # ----------------------------------
    # KATEGORIE
    # ----------------------------------

    y_train_cat = to_categorical(
        y_train,
        len(WYNIKI)
    )

    y_val_cat = to_categorical(
        y_val,
        len(WYNIKI)
    )

    # ----------------------------------
    # MODEL
    # ----------------------------------

    model = Sequential()

    model.add(
        Input(
            shape=(len(cechy),)
        )
    )

    model.add(
        Dense(
            32,
            activation="relu"
        )
    )

    model.add(
        Dense(
            64,
            activation="relu"
        )
    )

    model.add(
        Dropout(
            0.2
        )
    )

    model.add(
        Dense(
            len(WYNIKI),
            activation="softmax"
        )
    )

    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    stop = EarlyStopping(
        patience=20,
        restore_best_weights=True
    )

    # ----------------------------------
    # SZKOLENIE
    # ----------------------------------

    historia = model.fit(
        X_train,
        y_train_cat,
        validation_data=(
            X_val,
            y_val_cat
        ),
        epochs=200,
        batch_size=32,
        callbacks=[stop],
        verbose=1
    )

    # ----------------------------------
    # TEST WALIDACYJNY
    # ----------------------------------

    pred_val = model.predict(
        X_val
    )

    klasy_val = np.argmax(
        pred_val,
        axis=1
    )

    acc = accuracy_score(
        y_val,
        klasy_val
    )

    print(
        "Dokładność",
        nazwa,
        acc
    )

    # ======================================================
    # DODATKOWE 20% - OBSERWACJA
    # ======================================================

    pred_40 = model.predict(
        X_obserwacja
    )

    klasy_40 = np.argmax(
        pred_40,
        axis=1
    )

    prawdopodobienstwo = np.max(
        pred_40,
        axis=1
    )

    wynik_pred = [
        WYNIKI[x]
        for x in klasy_40
    ]

    wynik_realny = [
        WYNIKI[x]
        for x in y_obserwacja
    ]

    # ----------------------------------
    # ZAPIS WARSTWY OBSERWACJI
    # ----------------------------------

    # mapowanie indeksów obserwacji z powrotem do oryginalnego DataFrame
    obs_start_idx = len(df_global) - len(y_obserwacja)
    obs_indices = list(range(obs_start_idx, len(df_global)))
    
    # Używamy iloc zamiast loc - pracujemy na pozycjach, nie etykietach
    tabela_40 = df_global.iloc[obs_indices].copy()
    tabela_40 = tabela_40.reset_index(drop=True)
    
    # zabezpieczenie zgodności długości
    tabela_40 = tabela_40.iloc[:len(klasy_40)]

    tabela_40["model"] = nazwa
    tabela_40["klasa_predykcji"] = klasy_40
    tabela_40["wynik_predykcji"] = wynik_pred
    tabela_40["prawdopodobienstwo"] = prawdopodobienstwo

    # wynik zawsze ostatni
    if "wynik" in tabela_40.columns:
        wynik_koniec = tabela_40["wynik"]
        tabela_40 = tabela_40.drop(
            columns=["wynik"]
        )
        tabela_40["wynik"] = wynik_koniec

    tabela_40.to_csv(
        os.path.join(
            katalog,
            "walidacja_40_procent.csv"
        ),
        sep=";",
        index=False,
        encoding="utf-8"
    )

    # ----------------------------------
    # ZAPIS MODELU
    # ----------------------------------

    model.save(
        os.path.join(
            katalog,
            "model.h5"
        )
    )

    with open(
        os.path.join(
            katalog,
            "klasy.json"
        ),
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            MAPA_KLAS,
            f,
            indent=4,
            ensure_ascii=False
        )

    with open(
        os.path.join(
            katalog,
            "metadata.json"
        ),
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            {
                "nazwa": nazwa,
                "cechy": cechy,
                "dokladnosc": float(acc),
                "podzial": {
                    "trening": "60%",
                    "walidacja": "20%",
                    "obserwacja": "20%",
                    "typ": "chronologiczny",
                    "informacja": "STARE_DANE-trening|walidacja-NOWE_DANE-obserwacja"
                }
            },
            f,
            indent=4,
            ensure_ascii=False
        )

    with open(
        os.path.join(
            katalog,
            "historia.json"
        ),
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            historia.history,
            f,
            indent=4
        )
        
    # ========================================================================
    # GENEROWANIE PAMIĘCI ŚWIATÓW
    # ========================================================================
    
    pamiec_swiatow = generuj_pamiec_swiatow(
        df_global,
        y_obserwacja,
        klasy_40,
        nazwa,
        WYNIKI
    )
    
    with open(
        "pamiec_swiatow.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            pamiec_swiatow,
            f,
            indent=4,
            ensure_ascii=False
        )
    
    # Zwróć informacje o sieci
    return {
        "nazwa": nazwa,
        "dokladnosc": float(acc),
        "pamięć": pamiec_swiatow,
        "teacher": teacher_result
    }


# START WSZYSTKICH SIECI

print("\\n===============================")
print("URUCHAMIANIE SYSTEMU Z MODELEM POZNAWCZYM")
print("===============================")

# Collect results for laboratorium
all_results = []

for nazwa, cechy in SPOJRZENIA.items():

    brak = [
        x for x in cechy
        if x not in df.columns
    ]

    if brak:

        print(
            "POMINIĘTO:",
            nazwa,
            brak
        )
        continue

    result = buduj_siec(
        nazwa,
        cechy,
        df
    )
    
    all_results.append(result)


# Generuj laboratorium uczenia
laboratorium = generuj_laboratorium_uczenia(all_results, eksperyment_num=1)

with open(
    "laboratorium_uczenia.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        laboratorium,
        f,
        indent=4,
        ensure_ascii=False
    )

print()
print(
    "==============================="
)

print(
    "SYSTEM SZKOLENIA + MODEL POZNAWCZY + PAMIĘĆ ŚWIATÓW + LABORATORIUM GOTOWE"
)

print(
    "==============================="
)
