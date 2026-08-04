# SSI V5 Statistical Module - Result Matrix Generator
# =================================================
# 
# Moduł generujący macierz wyników na podstawie modelu Poisson + Dixon-Coles.
# Tworzy zestaw wszystkich możliwych wyników z ich prawdopodobieństwami.
# 
# Źródło: SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py
# Data migracji: 2026-08-03
# ETAP: 5.2.4 FAZA 2
# 
# Zasada: Zachowana oryginalna logika z głównego generatora

from SSI_V5.core.config import StatisticalConfig

# Import domyślnych parametrów
MAX_GOLE = StatisticalConfig.MAX_GOLE
RHO_DIXON = StatisticalConfig.RHO_DIXON

# Import zależnych modułów
from SSI_V5.modeling.statistical.poisson import poisson
from SSI_V5.modeling.statistical.dixon_coles import dixon_coles, dixon_coles_alt


def macierz_wynikow(ld, lw):
    """
    Generuje macierz wszystkich możliwych wyników meczu z ich prawdopodobieństwami.
    
    Args:
        ld (float): Lambda dla drużyny domowej (średnia liczba goli)
        lw (float): Lambda dla drużyny wyjazdowej (średnia liczba goli)
        
    Returns:
        list: Posortowana lista tupli (gole_dom, gole_wyj, prawdopodobieństwo)
              posortowana malejąco według prawdopodobieństwa
    """
    wyniki = []
    
    for gd in range(MAX_GOLE + 1):
        for gw in range(MAX_GOLE + 1):
            p = (
                poisson(gd, ld)
                *
                poisson(gw, lw)
                *
                dixon_coles(
                    gd,
                    gw,
                    ld,
                    lw
                )
            )
            
            wyniki.append(
                (
                    gd,
                    gw,
                    p
                )
            )
    
    return sorted(
        wyniki,
        key=lambda x: x[2],
        reverse=True
    )


# =================================================
# ALTERNATYWNA IMPLEMENTACJA (z alternatywną Dixon-Coles)
# =================================================

def macierz_wynikow_alt(ld, lw):
    """
    Alternatywna implementacja macierzy wyników z użyciem dixon_coles_alt.
    
    Args:
        ld (float): Lambda dla drużyny domowej
        lw (float): Lambda dla drużyny wyjazdowej
        
    Returns:
        list: Posortowana lista tupli (gole_dom, gole_wyj, prawdopodobieństwo)
    """
    wyniki = []
    
    for gd in range(MAX_GOLE + 1):
        for gw in range(MAX_GOLE + 1):
            p = (
                poisson(gd, ld)
                *
                poisson(gw, lw)
                *
                dixon_coles_alt(
                    gd,
                    gw,
                    ld,
                    lw
                )
            )
            
            wyniki.append(
                (
                    gd,
                    gw,
                    p
                )
            )
    
    return sorted(
        wyniki,
        key=lambda x: x[2],
        reverse=True
    )


# =================================================
# FUNKCJE POMOCNICZE
# =================================================

def get_result_matrix(ld, lw, max_goals=None):
    """
    Generuje macierz wyników z opcjonalną zmianą parametru MAX_GOLE.
    
    Args:
        ld (float): Lambda dla drużyny domowej
        lw (float): Lambda dla drużyn wyjazdowej
        max_goals (int, optional): Maksymalna liczba goli. Jeśli None, używa MAX_GOLE z configu.
        
    Returns:
        list: Posortowana lista wyników z prawdopodobieństwami
    """
    if max_goals is None:
        max_goals = MAX_GOLE
    
    wyniki = []
    
    for gd in range(max_goals + 1):
        for gw in range(max_goals + 1):
            p = (
                poisson(gd, ld)
                *
                poisson(gw, lw)
                *
                dixon_coles(gd, gw, ld, lw)
            )
            
            wyniki.append((gd, gw, p))
    
    return sorted(wyniki, key=lambda x: x[2], reverse=True)


def get_top_results(ld, lw, top_n=5):
    """
    Zwraca N najbardziej prawdopodobnych wyników.
    
    Args:
        ld (float): Lambda dla drużyny domowej
        lw (float): Lambda dla drużyny wyjazdowej
        top_n (int): Liczba top wyników do zwrócenia
        
    Returns:
        list: Lista top N wyników z prawdopodobieństwami
    """
    all_results = macierz_wynikow(ld, lw)
    return all_results[:top_n]


def get_result_probability(gd, gw, ld, lw):
    """
    Zwraca prawdopodobieństwo dla konkretnego wyniku.
    
    Args:
        gd (int): Gole drużyny domowej
        gw (int): Gole drużyny wyjazdowej
        ld (float): Lambda dla drużyny domowej
        lw (float): Lambda dla drużyny wyjazdowej
        
    Returns:
        float: Prawdopodobieństwo danego wyniku
    """
    return (
        poisson(gd, ld)
        *
        poisson(gw, lw)
        *
        dixon_coles(gd, gw, ld, lw)
    )


# =================================================
# TESTY MODUŁU
# =================================================

def test_matrix():
    """Test podstawowych funkcjonalności modułu matrix.py."""
    # Test 1: Podstawowa macierz wyników
    results = macierz_wynikow(2.0, 1.5)
    
    # Sprawdź, czy lista nie jest pusta
    assert len(results) > 0
    
    # Sprawdź, czy wszystkie elementy mają poprawną strukturę
    for result in results:
        assert len(result) == 3
        gd, gw, p = result
        assert isinstance(gd, int)
        assert isinstance(gw, int)
        assert isinstance(p, float)
        assert gd >= 0 and gw >= 0
        assert p >= 0
    
    # Test 2: Posortowanie malejące
    for i in range(len(results) - 1):
        assert results[i][2] >= results[i + 1][2]
    
    # Test 3: Sprawdź, czy najwyższe prawdopodobieństwo jest pozytywne
    assert results[0][2] > 0
    
    # Test 4: Test z zerowymi lambda
    results_zero = macierz_wynikow(0, 0)
    assert len(results_zero) > 0
    # Wszystkie powinny mieć prawdopodobieństwo 0 (poisson(*,0)=0)
    # lub bardzo małe dla (0,0)
    
    # Test 5: Test top_results
    top_5 = get_top_results(2.0, 1.5, top_n=5)
    assert len(top_5) == 5
    
    # Test 6: Test get_result_probability
    prob = get_result_probability(1, 0, 2.0, 1.5)
    assert isinstance(prob, float)
    assert prob >= 0
    
    # Test 7: Symetria z alternatywną implementacją
    results_main = macierz_wynikow(2.0, 1.5)
    results_alt = macierz_wynikow_alt(2.0, 1.5)
    
    # Porównaj top 10 wyników
    for i in range(min(10, len(results_main))):
        main_gd, main_gw, main_p = results_main[i]
        alt_gd, alt_gw, alt_p = results_alt[i]
        assert main_gd == alt_gd
        assert main_gw == alt_gw
        assert abs(main_p - alt_p) < 1e-10
    
    print("[OK] Wszystkie testy modułu matrix.py zaliczone")


if __name__ == "__main__":
    test_matrix()
    print("Moduł matrix.py - Test wykonany pomyslnie")