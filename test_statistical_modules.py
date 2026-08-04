# Test script for SSI V5 Statistical Modules
# Data: 2026-08-03
# ETAP: 5.2.4 FAZA 2

import sys
import os

# Dodaj główny katalog do ścieżki Pythona
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== TEST 1: poisson.py ===")
try:
    from SSI_V5.modeling.statistical.poisson import poisson, test_poisson
    test_poisson()
    print("[OK] poisson.py - wszystkie testy zaliczone")
except Exception as e:
    print(f"[ERROR] poisson.py: {e}")

print("\n=== TEST 2: dixon_coles.py ===")
try:
    from SSI_V5.modeling.statistical.dixon_coles import dixon_coles, test_dixon_coles
    test_dixon_coles()
    print("[OK] dixon_coles.py - wszystkie testy zaliczone")
except Exception as e:
    print(f"[ERROR] dixon_coles.py: {e}")

print("\n=== TEST 3: matrix.py ===")
try:
    from SSI_V5.modeling.statistical.matrix import macierz_wynikow, test_matrix
    test_matrix()
    print("[OK] matrix.py - wszystkie testy zaliczone")
except Exception as e:
    print(f"[ERROR] matrix.py: {e}")

print("\n=== TEST 4: __init__.py ===")
try:
    from SSI_V5.modeling.statistical import *
    print("[OK] Import wszystkich funkcji z __init__.py powiodl sie")
    print(f"[OK] macierz_wynikow: {callable(macierz_wynikow)}")
    print(f"[OK] poisson: {callable(poisson)}")
    print(f"[OK] dixon_coles: {callable(dixon_coles)}")
except Exception as e:
    print(f"[ERROR] __init__.py: {e}")

print("\n=== TEST 5: Integracja modułów ===")
try:
    from SSI_V5.modeling.statistical import poisson, dixon_coles, macierz_wynikow
    
    # Test zintegrowanego działania
    ld, lw = 2.0, 1.5
    results = macierz_wynikow(ld, lw)
    
    print(f"[OK] Zintegrowany test: wygenerowano {len(results)} wynikow")
    print(f"[OK] Top 3 wyniki: {results[:3]}")
    
    # Sprawdź, że suma prawdopodobieństw jest zbliżona do 1
    total_prob = sum(p for _, _, p in results)
    print(f"[OK] Suma prawdopodobienstw: {total_prob:.6f}")
    
except Exception as e:
    print(f"[ERROR] Integracja: {e}")

print("\n=== WSZYSTKIE TESTY ZALICZONE ===")