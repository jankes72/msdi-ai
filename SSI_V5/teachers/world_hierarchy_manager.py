# SSI V5 Teacher Layer - World Hierarchy Manager
# ========================================================
#
# Zarządza hierarchiczną pamięcią światów dla SSI V5.
#
# Źródło: SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py:47896-48090
# Data migracji: 2026-08-03
# ETAP: 5.2.4 FAZA 3
#
# Hierarchia:
# - POZIOM 1: szeroki świat (np. "poziom30") - najszerszy
# - POZIOM 2: średni świat (np. "poziom30poziom25")
# - POZIOM 3: pełny świat (np. "poziom30poziom25poziom2") - najmniejszy
#
# Zasada: Nie zmieniamy algorytmów, zachowujemy pełną zgodność z oryginałem

import os
import json


# ============================================================================
# KONFIGURACJA ŚCIEŻEK (będą importowane z config.py lub zdefiniowane globalnie)
# ============================================================================

WORLD_DATA_PATH = None
WORLD_LEVEL_1_PATH = None
WORLD_LEVEL_2_PATH = None
MIN_SAMPLES_LEVEL_1 = 100


def configure_paths(
    world_match_db_path=None,
    world_level_1_path=None,
    world_level_2_path=None,
    min_samples_level_1=100
):
    """
    Konfiguruje ścieżki dla WorldHierarchyManager.
    
    Args:
        world_match_db_path: Ścieżka do WORLD_MATCH_DATABASE.json
        world_level_1_path: Ścieżka do WORLD_LEVEL_1_ANALYSIS.json
        world_level_2_path: Ścieżka do WORLD_LEVEL_2_ANALYSIS.json
        min_samples_level_1: Minimalna liczba próbek dla poziomu 1
    """
    global WORLD_DATA_PATH, WORLD_LEVEL_1_PATH, WORLD_LEVEL_2_PATH, MIN_SAMPLES_LEVEL_1
    
    WORLD_DATA_PATH = world_match_db_path or WORLD_DATA_PATH
    WORLD_LEVEL_1_PATH = world_level_1_path or WORLD_LEVEL_1_PATH
    WORLD_LEVEL_2_PATH = world_level_2_path or WORLD_LEVEL_2_PATH
    MIN_SAMPLES_LEVEL_1 = min_samples_level_1


class WorldHierarchyManager:
    """
    Zarządza hierarchiczną pamięcią światów.
    
    Hierarchia:
    - POZIOM 1: szeroki świat (np. "poziom30") - najszerszy
    - POZIOM 2: średni świat (np. "poziom30poziom25") 
    - POZIOM 3: pełny świat (np. "poziom30poziom25poziom2") - najmniejszy
    
    Wybiera najlepszy poziom doświadczenia na podstawie ilości danych.
    
    Źródło: SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py:47896-48090
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
        if self.world_match_db_path and os.path.exists(self.world_match_db_path):
            try:
                with open(self.world_match_db_path, 'r', encoding='utf-8') as f:
                    self.world_data = json.load(f)
                print(f"  [TEACHER] Wczytano WORLD_MATCH_DATABASE ({len(self.world_data)} mecze)")
            except Exception as e:
                print(f"  [TEACHER] Błąd wczytywania WORLD_MATCH_DATABASE: {e}")
        
        # Wczytaj WORLD_LEVEL_1_ANALYSIS
        if self.level_1_path and os.path.exists(self.level_1_path):
            try:
                with open(self.level_1_path, 'r', encoding='utf-8') as f:
                    self.level_1_data = json.load(f)
                print(f"  [TEACHER] Wczytano WORLD_LEVEL_1_ANALYSIS ({len(self.level_1_data)} grupy)")
            except Exception as e:
                print(f"  [TEACHER] Błąd wczytywania WORLD_LEVEL_1_ANALYSIS: {e}")
        
        # Wczytaj WORLD_LEVEL_2_ANALYSIS
        if self.level_2_path and os.path.exists(self.level_2_path):
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
# TESTY MODUŁU
# ============================================================================


def test_world_hierarchy_manager():
    """
    Test podstawowych funkcjonalności WorldHierarchyManager.
    """
    print("\n" + "="*60)
    print("TEST: WorldHierarchyManager")
    print("="*60)
    
    # Test inicjalizacji
    try:
        manager = WorldHierarchyManager(
            world_match_db_path=None,
            level_1_path=None,
            level_2_path=None
        )
        
        # Sprawdź, czy obiekty zostały zainicjowane
        assert hasattr(manager, 'world_data')
        assert hasattr(manager, 'level_1_data')
        assert hasattr(manager, 'level_2_data')
        
        print("[OK] Test inicjalizacji - zaliczony")
        
        # Test z pustymi danymi
        result = manager.get_world_levels("test_key")
        assert isinstance(result, dict)
        
        print("[OK] Test get_world_levels z pustymi danymi - zaliczony")
        
        # Test wybierz_najlepszy_poziom z pustymi danymi
        poziom, nazwa, stats = manager.wybierz_najlepszy_poziom("test_key")
        assert poziom is None
        assert nazwa is None
        assert stats == {}
        
        print("[OK] Test wybierz_najlepszy_poziom z pustymi danymi - zaliczony")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Test WorldHierarchyManager - błąd: {e}")
        return False


def test_parse_world_stats():
    """
    Test _parse_world_stats i _oblicz_srednie_gole.
    """
    try:
        manager = WorldHierarchyManager()
        
        # Test _oblicz_srednie_gole
        wyniki = {
            "2:1": {"ilosc": 10},
            "0:0": {"ilosc": 5},
            "3:2": {"ilosc": 3}
        }
        
        srednie = manager._oblicz_srednie_gole(wyniki)
        
        assert isinstance(srednie, dict)
        assert "gospodarze" in srednie
        assert "goscie" in srednie
        assert "suma" in srednie
        
        print("[OK] Test _oblicz_srednie_gole - zaliczony")
        
        # Test _parse_world_stats
        stats = {
            "ilosc_przypadkow": 18,
            "wyniki_docelowe": wyniki,
            "profil_meczu_1X2": {
                "gospodarze": {"procent": 60},
                "remis": {"procent": 20},
                "goscie": {"procent": 20}
            }
        }
        
        parsed = manager._parse_world_stats(stats)
        
        assert parsed["ilosc_przypadkow"] == 18
        assert parsed["procent_gospodarze"] == 0.6
        assert parsed["procent_remis"] == 0.2
        assert parsed["procent_goscie"] == 0.2
        
        print("[OK] Test _parse_world_stats - zaliczony")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Test parse functions - błąd: {e}")
        return False


if __name__ == "__main__":
    test_world_hierarchy_manager()
    test_parse_world_stats()
    print("\nWorldHierarchyManager - Testy wykonane")
