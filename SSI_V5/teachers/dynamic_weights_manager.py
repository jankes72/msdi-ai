# SSI V5 Teacher Layer - Dynamic Weights Manager
# ====================================================
#
# Zarządza dynamicznymi wagami świata dla SSI V5.
#
# Źródło: SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py:48092-48180
# Data migracji: 2026-08-03
# ETAP: 5.2.4 FAZA 3
#
# Wagi są obliczane przed każdym treningiem na podstawie:
# - ilości przykładów
# - skuteczności świata
# - stabilności korelacji
# - zgodności Dixon-Coles
#
# Zasada: Nie zmieniamy algorytmów, zachowujemy pełną zgodność z oryginałem


class DynamicWeightsManager:
    """
    Zarządza dynamicznymi wagami świata.
    
    Wagi są obliczane przed każdym treningiem na podstawie:
    - ilości przykładów
    - skuteczności świata
    - stabilności korelacji
    - zgodność Dixon-Coles
    
    Źródło: SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py:48092-48180
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
        
        Args:
            poziom: Poziom świata (poziom1, poziom2, poziom3)
            ilosc_przypadkow: Liczba przypadków w świecie
            procent_gospodarze: Procent zwycięstw gospodarzy (0-1)
            procent_remis: Procent remisów (0-1)
            procent_goscie: Procent zwycięstw gości (0-1)
            korelacje_stabilnosc: Stabilność korelacji (0-1)
            dc_accuracy: Dokładność Dixon-Coles (0-1)
        
        Returns:
            float: Waga świata (0-1)
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
        
        Args:
            procent_gospodarze: Procent zwycięstw gospodarzy (0-1)
            procent_remis: Procent remisów (0-1)
            procent_goscie: Procent zwycięstw gości (0-1)
            waga_swiata: Waga świata (0-1)
        
        Returns:
            dict: Wagi klas {"gospodarze": waga, "remis": waga, "goscie": waga}
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
        
        Args:
            waga_swiata: Waga świata (0-1)
        
        Returns:
            dict: {"waga_swiata": waga, "waga_modelu": waga}
        """
        waga_modelu = round(1.0 - waga_swiata, 4)
        return {
            "waga_swiata": round(waga_swiata, 4),
            "waga_modelu": waga_modelu
        }


# ============================================================================
# TESTY MODUŁU
# ============================================================================


def test_dynamic_weights_manager():
    """
    Test podstawowych funkcjonalności DynamicWeightsManager.
    """
    print("\n" + "="*60)
    print("TEST: DynamicWeightsManager")
    print("="*60)
    
    try:
        manager = DynamicWeightsManager()
        
        # Sprawdź inicjalizację
        assert hasattr(manager, 'weight_history')
        assert isinstance(manager.weight_history, dict)
        
        print("[OK] Test inicjalizacji - zaliczony")
        
        # Test oblicz_wage_swiata
        waga = manager.oblicz_wage_swiata(
            poziom="poziom3",
            ilosc_przypadkow=5000,
            procent_gospodarze=0.6,
            procent_remis=0.2,
            procent_goscie=0.2,
            korelacje_stabilnosc=0.8,
            dc_accuracy=0.9
        )
        
        assert isinstance(waga, float)
        assert 0 <= waga <= 1.0
        
        print(f"[OK] Test oblicz_wage_swiata - zaliczony (waga: {waga})")
        
        # Test oblicz_wagi_klas
        wagi_klas = manager.oblicz_wagi_klas(
            procent_gospodarze=0.6,
            procent_remis=0.2,
            procent_goscie=0.2,
            waga_swiata=0.8
        )
        
        assert isinstance(wagi_klas, dict)
        assert "gospodarze" in wagi_klas
        assert "remis" in wagi_klas
        assert "goscie" in wagi_klas
        
        # Sprawdź, czy suma wag jest równa waga_swiata
        suma_wag = wagi_klas["gospodarze"] + wagi_klas["remis"] + wagi_klas["goscie"]
        assert abs(suma_wag - 0.8) < 0.01  # Tolerancja dla zaokrągleń
        
        print(f"[OK] Test oblicz_wagi_klas - zaliczony (wagi: {wagi_klas})")
        
        # Test oblicz_wagi_modelu_i_swiata
        wagi = manager.oblicz_wagi_modelu_i_swiata(0.7)
        
        assert isinstance(wagi, dict)
        assert "waga_swiata" in wagi
        assert "waga_modelu" in wagi
        assert wagi["waga_swiata"] == 0.7
        assert wagi["waga_modelu"] == 0.3
        
        print(f"[OK] Test oblicz_wagi_modelu_i_swiata - zaliczony (wagi: {wagi})")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Test DynamicWeightsManager - błąd: {e}")
        return False


def test_edge_cases():
    """
    Test przypadków brzegowych.
    """
    try:
        manager = DynamicWeightsManager()
        
        # Test z zerową ilością przypadków
        waga = manager.oblicz_wage_swiata(
            poziom="poziom1",
            ilosc_przypadkow=0,
            procent_gospodarze=0.3,
            procent_remis=0.3,
            procent_goscie=0.3,
            korelacje_stabilnosc=0.5,
            dc_accuracy=0.5
        )
        assert waga >= 0
        print("[OK] Test zerowej ilości przypadków - zaliczony")
        
        # Test z równym rozkładem
        wagi_klas = manager.oblicz_wagi_klas(
            procent_gospodarze=0.333,
            procent_remis=0.333,
            procent_goscie=0.334,
            waga_swiata=1.0
        )
        assert wagi_klas["gospodarze"] > 0
        assert wagi_klas["remis"] > 0
        assert wagi_klas["goscie"] > 0
        print("[OK] Test równomiernego rozkładu - zaliczony")
        
        # Test z zerową wagą świata
        wagi = manager.oblicz_wagi_modelu_i_swiata(0.0)
        assert wagi["waga_swiata"] == 0.0
        assert wagi["waga_modelu"] == 1.0
        print("[OK] Test zerowej wagi świata - zaliczony")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Test edge cases - błąd: {e}")
        return False


if __name__ == "__main__":
    test_dynamic_weights_manager()
    test_edge_cases()
    print("\nDynamicWeightsManager - Testy wykonane")
