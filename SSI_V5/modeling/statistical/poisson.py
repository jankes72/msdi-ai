# SSI V5 Statistical Module - Poisson Distribution
# =================================================
# 
# Moduł implementujący rozkład Poissona dla modelowania 
# liczby goli w-na mecze piłki nożnej.
# 
# Źródło: SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py
# Data migracji: 2026-08-03
# ETAP: 5.2.4 FAZA 2
# 
# Zasada: Zachowana oryginalna logika z głównego generatora

import math


def poisson(k, lam):
    """
    Oblicza prawdopodobieństwo wystąpienia k zdarzeń 
    przy urbaine średniej lambda (rozkład Poissona).
    
    Args:
        k (int): Liczba zdarzeń (goli)
        lam (float): Średnia liczba zdarzeń (lambda)
        
    Returns:
        float: Prawdopodobieństwo P(X=k) dla rozkładu Poissona
        
    Note:
        Zwraca 0 jeśli lam <= 0 lub wystąpi błąd obliczeniowy
    """
    if lam <= 0:
        return 0
        
    try:
        return (
            math.exp(-lam)
            * (lam ** k)
            / math.factorial(k)
        )
    except:
        return 0


# =================================================
# ALTERNATYWNA IMPLEMENTACJA (wersja uproszczona)
# =================================================

def poisson_simple(k, lam):
    """
    Uproszczona wersja rozkładu Poissona bez obsługi błędów.
    
    Args:
        k (int): Liczba zdarzeń (goli)
        lam (float): Średnia liczba zdarzeń (lambda)
        
    Returns:
        float: Prawdopodobieństwo P(X=k)
    """
    if lam <= 0:
        return 0
        
    return (
        math.exp(-lam)
        * lam**k
        / math.factorial(k)
    )


# =================================================
# FUNKCJE POMOCNICZE
# =================================================

def poisson_probability_matrix(max_goals, lambda_value):
    """
    Generuje macierz prawdopodobieństw Poissona dla zakresu goli.
    
    Args:
        max_goals (int): Maksymalna liczba goli do obliczenia
        lambda_value (float): Parametr lambda
        
    Returns:
        list: Lista prawdopodobieństw dla k=0 do max_goals
    """
    return [poisson(k, lambda_value) for k in range(max_goals + 1)]


# =================================================
# TESTY MODUŁU
# =================================================

def test_poisson():
    """Test podstawowych funkcjonalności modułu Poisson."""
    # Test 1: lam <= 0
    assert poisson(5, 0) == 0
    assert poisson(5, -1) == 0
    
    # Test 2: Podstawowe obliczenia
    result_0 = poisson(0, 1)
    expected_0 = math.exp(-1)
    assert abs(result_0 - expected_0) < 1e-10
    
    result_1 = poisson(1, 1)
    expected_1 = math.exp(-1) * 1 / math.factorial(1)
    assert abs(result_1 - expected_1) < 1e-10
    
    result_2 = poisson(2, 1)
    expected_2 = math.exp(-1) * (1**2) / math.factorial(2)
    assert abs(result_2 - expected_2) < 1e-10
    
    # Test 3: Symetria
    assert poisson(0, 1) == poisson_simple(0, 1)
    
    print("[OK] Wszystkie testy modułu poisson.py zaliczone")


if __name__ == "__main__":
    test_poisson()
    print("Moduł poisson.py - Test wykonany pomyslnie")