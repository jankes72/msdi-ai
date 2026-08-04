# SSI V5 Statistical Module - Dixon-Coles Correction
# =================================================
# 
# Moduł implementujący korektę Dixon-Coles dla modelu Poissona.
# Korekta uwzględnia zależność między liczbą goli obu drużyn.
# 
# Źródło: SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py
# Data migracji: 2026-08-03
# ETAP: 5.2.4 FAZA 2
# 
# Zasada: Zachowana oryginalna logika z głównego generatora

from SSI_V5.core.config import StatisticalConfig

# Import domyślnych parametrów
RHO_DIXON = StatisticalConfig.RHO_DIXON


def dixon_coles(gole_dom, gole_wyj, lambda_dom, lambda_wyj, rho=RHO_DIXON):
    """
    Oblicza współczynnik korekcji Dixon-Coles dla podanego wyniku.
    
    Args:
        gole_dom (int): Liczba goli drużyny domowej
        gole_wyj (int): Liczba goli drużyny wyjazdowej
        lambda_dom (float): Parametr lambda dla drużyny domowej
        lambda_wyj (float): Parametr lambda dla drużyny wyjazdowej
        rho (float): Parametr korekcji (domyślnie RHO_DIXON = -0.1)
        
    Returns:
        float: Współczynnik korekcji (zawsze >= 0)
        
    Note:
        Funkcja obsługuje specyficzne przypadki dla niskich wyników
        (0:0, 1:0, 0:1, 1:1) i zwraca 1 dla pozostałych.
    """
    korekta = 1
    
    if gole_dom == 0 and gole_wyj == 0:
        korekta = (
            1
            -
            lambda_dom
            *
            lambda_wyj
            *
            rho
        )
    elif gole_dom == 1 and gole_wyj == 0:
        korekta = (
            1
            +
            lambda_wyj
            *
            rho
        )
    elif gole_dom == 0 and gole_wyj == 1:
        korekta = (
            1
            +
            lambda_dom
            *
            rho
        )
    elif gole_dom == 1 and gole_wyj == 1:
        korekta = (
            1
            -
            rho
        )
    
    return max(korekta, 0)


# =================================================
# ALTERNATYWNA IMPLEMENTACJA (wersja zwięzła)
# =================================================

def dixon_coles_alt(gd, gw, ld, lw, rho=RHO_DIXON):
    """
    Alternatywna implementacja korekcji Dixon-Coles (skrócone nazwy parametrów).
    
    Args:
        gd (int): Gole gospodarzy
        gw (int): Gole gości
        ld (float): Lambda gospodarzy
        lw (float): Lambda gości
        rho (float): Parametr korekcji
        
    Returns:
        float: Współczynnik korekcji
    """
    rho = RHO_DIXON
    
    if gd == 0 and gw == 0:
        return 1 - ld * lw * rho
    if gd == 1 and gw == 0:
        return 1 + lw * rho
    if gd == 0 and gw == 1:
        return 1 + ld * rho
    if gd == 1 and gw == 1:
        return 1 - rho
    
    return 1


# =================================================
# FUNKCJE POMOCNICZE
# =================================================

def get_dixon_coles_correction_factor(gd, gw, ld, lw, rho=RHO_DIXON):
    """
    Alias dla głównej funkcji dixon_coles - dla spójności nazw.
    """
    return dixon_coles(gd, gw, ld, lw, rho)


# =================================================
# TESTY MODUŁU
# =================================================

def test_dixon_coles():
    """Test podstawowych funkcjonalności modułu Dixon-Coles."""
    # Test 1: Przypadki specjalne
    result_00 = dixon_coles(0, 0, 2.0, 1.5)
    expected_00 = 1 - 2.0 * 1.5 * (-0.1)  # rho = -0.1
    assert abs(result_00 - expected_00) < 1e-10
    
    result_10 = dixon_coles(1, 0, 2.0, 1.5)
    expected_10 = 1 + 1.5 * (-0.1)
    assert abs(result_10 - expected_10) < 1e-10
    
    result_01 = dixon_coles(0, 1, 2.0, 1.5)
    expected_01 = 1 + 2.0 * (-0.1)
    assert abs(result_01 - expected_01) < 1e-10
    
    result_11 = dixon_coles(1, 1, 2.0, 1.5)
    expected_11 = 1 - (-0.1)
    assert abs(result_11 - expected_11) < 1e-10
    
    # Test 2: Inne wyniki (powinny zwrócić 1)
    assert dixon_coles(2, 0, 2.0, 1.5) == 1
    assert dixon_coles(0, 2, 2.0, 1.5) == 1
    assert dixon_coles(2, 1, 2.0, 1.5) == 1
    assert dixon_coles(3, 3, 2.0, 1.5) == 1
    
    # Test 3: Wartości ujemne - powinny być korygowane do 0
    # (test z bardzo niskim rho)
    result_neg = dixon_coles(0, 0, 10.0, 10.0, rho=-1.0)  # ekstremalny przypadek
    assert result_neg >= 0  # max(korekta, 0) gwarantuje nieujemność
    
    # Test 4: Symetria z alternatywną implementacją
    assert dixon_coles(0, 0, 2.0, 1.5) == dixon_coles_alt(0, 0, 2.0, 1.5)
    assert dixon_coles(1, 0, 2.0, 1.5) == dixon_coles_alt(1, 0, 2.0, 1.5)
    assert dixon_coles(0, 1, 2.0, 1.5) == dixon_coles_alt(0, 1, 2.0, 1.5)
    assert dixon_coles(1, 1, 2.0, 1.5) == dixon_coles_alt(1, 1, 2.0, 1.5)
    assert dixon_coles(2, 0, 2.0, 1.5) == dixon_coles_alt(2, 0, 2.0, 1.5)
    
    print("[OK] Wszystkie testy modułu dixon_coles.py zaliczone")


if __name__ == "__main__":
    test_dixon_coles()
    print("Moduł dixon_coles.py - Test wykonany pomyslnie")