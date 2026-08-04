# SSI V5 Teacher Layer - Cognitive Teacher
# ==================================================
#
# Model Poznawczy - analiza historycznych danych i generowanie wiedzy
# dla modelu docelowego.
#
# Źródło: SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py:48187-48823
# Data migracji: 2026-08-03
# ETAP: 5.2.4 FAZA 3.1
#
# Zasada: Nie zmieniamy algorytmów, zachowujemy pełną zgodność z oryginałem
# Korzysta WYŁĄCZNIE z rzeczywistych wyników (Y).
# Nie używa predykcji, danych przyszłych ani mieszania zbiorów.
#

import os
import json
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.preprocessing import StandardScaler
import scipy.stats as stats

# Import managerów z SSI_V5.teachers
from .world_hierarchy_manager import WorldHierarchyManager
from .dynamic_weights_manager import DynamicWeightsManager


class CognitiveTeacher:
    """
    Model Poznawczy - analiza historycznych danych i generowanie wiedzy
    dla modelu docelowego.
    
    Korzysta WYŁĄCZNIE z rzeczywistych wyników (Y).
    Nie używa predykcji, danych przyszłych ani mieszania zbiorów.
    
    Źródło: SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py:48187-48823
    """
    
    def __init__(self, df, cechy, siec_name="dataBase_futbol_trend", use_rf=True, models_dir=None):
        """
        Inicjalizacja CognitiveTeacher.
        
        Args:
            df: DataFrame z danymi
            cechy: lista cech do analizy
            siec_name: nazwa sieci/modelu
            use_rf: czy używać Random Forest (domyślnie True)
            models_dir: katalog modeli (opcjonalny, domyślnie używa KATALOG_MODELE z config)
        """
        self.df = df
        self.cechy = cechy
        self.siec_name = siec_name
        
        # Ustaw katalog modeli
        if models_dir is None:
            from ..core.config import PathConfig
            models_dir = PathConfig.MODELE_DATA_BASE_DIR
        
        self.pamiec_path = os.path.join(models_dir, siec_name, "PAMIEC_MODEL_POZNAWCZY.json")
        self.wiedza_path = os.path.join(models_dir, siec_name, "WIEDZA_DLA_MODELU_DOCELOWEGO.json")
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
        
        # 3. Oblicz所有 miary
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
        
        # Structure do przechowywania pojedynczego doświadczenia
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
