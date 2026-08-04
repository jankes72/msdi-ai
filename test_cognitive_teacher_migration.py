#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST: Migracja CognitiveTeacher do SSI_V5/teachers/cognitive_teacher.py
ETAP 5.2.4 FAZA 3.1
"""

import sys
import os

# Dodaj głównego katalogu SSI_V5 do path
sys.path.insert(0, 'D:/sts/aplikacjaTyperBetAi')

def test_import():
    """Test 1: Import CognitiveTeacher"""
    print("=" * 60)
    print("TEST 1: Import CognitiveTeacher")
    print("=" * 60)
    
    try:
        from SSI_V5.teachers.cognitive_teacher import CognitiveTeacher
        print("SUCCESS: CognitiveTeacher imported successfully")
        return True
    except Exception as e:
        print(f"FAILED: Import error: {e}")
        return False

def test_import_from_teachers():
    """Test 2: Import z SSI_V5.teachers"""
    print("\n" + "=" * 60)
    print("TEST 2: Import from SSI_V5.teachers")
    print("=" * 60)
    
    try:
        from SSI_V5.teachers import CognitiveTeacher, WorldHierarchyManager, DynamicWeightsManager
        print("SUCCESS: All teachers imported successfully")
        print(f"   - CognitiveTeacher: {CognitiveTeacher}")
        print(f"   - WorldHierarchyManager: {WorldHierarchyManager}")
        print(f"   - DynamicWeightsManager: {DynamicWeightsManager}")
        return True
    except Exception as e:
        print(f"FAILED: Import error: {e}")
        return False

def test_initialization():
    """Test 3: Inicjalizacja klasy CognitiveTeacher"""
    print("\n" + "=" * 60)
    print("TEST 3: CognitiveTeacher initialization")
    print("=" * 60)
    
    try:
        import pandas as pd
        import numpy as np
        from SSI_V5.teachers.cognitive_teacher import CognitiveTeacher
        
        # Stwórz testowy DataFrame
        test_data = {
            'cecha1': [1.0, 2.0, 3.0, 4.0, 5.0],
            'cecha2': [0.5, 1.5, 2.5, 3.5, 4.5],
            'cecha3': [0.1, 0.2, 0.3, 0.4, 0.5],
            'wynik': ['1:0', '2:1', '3:0', '1:1', '2:2']
        }
        df = pd.DataFrame(test_data)
        cechy = ['cecha1', 'cecha2', 'cecha3']
        
        # Inicjalizacja
        teacher = CognitiveTeacher(
            df=df,
            cechy=cechy,
            siec_name="test_network",
            use_rf=False  # Wyłącz RF dla szybszego testu
        )
        
        print("SUCCESS: CognitiveTeacher initialized successfully")
        print(f"   - df shape: {teacher.df.shape}")
        print(f"   - cechy: {teacher.cechy}")
        print(f"   - siec_name: {teacher.siec_name}")
        print(f"   - use_rf: {teacher.use_rf}")
        print(f"   - world_hierarchy: {type(teacher.world_hierarchy).__name__}")
        print(f"   - weights_manager: {type(teacher.weights_manager).__name__}")
        return True
    except Exception as e:
        print(f"FAILED: Initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_methods():
    """Test 4: Test istniejących metod"""
    print("\n" + "=" * 60)
    print("TEST 4: Testing CognitiveTeacher methods")
    print("=" * 60)
    
    try:
        import pandas as pd
        import numpy as np
        from SSI_V5.teachers.cognitive_teacher import CognitiveTeacher
        
        # Stwórz testowy DataFrame
        test_data = {
            'cecha1': [1.0, 2.0, 3.0, 4.0, 5.0],
            'cecha2': [0.5, 1.5, 2.5, 3.5, 4.5],
            'cecha3': [0.1, 0.2, 0.3, 0.4, 0.5],
            'wynik': ['1:0', '2:1', '3:0', '1:1', '2:2']
        }
        df = pd.DataFrame(test_data)
        cechy = ['cecha1', 'cecha2', 'cecha3']
        
        teacher = CognitiveTeacher(
            df=df,
            cechy=cechy,
            siec_name="test_network",
            use_rf=False  # Wyłącz RF dla szybszego testu
        )
        
        # Test parse_wynik
        wynik_parsed = teacher.parse_wynik("2:1")
        print(f"   - parse_wynik('2:1'): {wynik_parsed}")
        assert wynik_parsed == [2, 1, 3], "parse_wynik failed"
        
        # Test prepare_teacher_targets
        y_teacher = teacher.prepare_teacher_targets()
        print(f"   - prepare_teacher_targets shape: {y_teacher.shape}")
        assert y_teacher.shape == (5, 3), "prepare_teacher_targets failed"
        
        # Test oblicz_korelacje
        X = df[cechy].values
        korelacje = teacher.oblicz_korelacje(X, y_teacher)
        print(f"   - oblicz_korelacje: {list(korelacje.keys())}")
        assert len(korelacje) == 3, "oblicz_korelacje failed"
        
        # Test oblicz_dixon_coles
        dc_stength = teacher.oblicz_dixon_coles(X, y_teacher)
        print(f"   - oblicz_dixon_coles: {dc_stength}")
        assert len(dc_stength) == 3, "oblicz_dixon_coles failed"
        
        # Test oblicz_sile_cechy
        rf_importance = {cecha: {} for cecha in cechy}
        sila_cech = teacher.oblicz_sile_cechy(korelacje, rf_importance, dc_stength)
        print(f"   - oblicz_sile_cechy: {sila_cech}")
        assert len(sila_cech) == 3, "oblicz_sile_cechy failed"
        
        # Test ranking_cech
        ranking = teacher.ranking_cech(sila_cech, korelacje, rf_importance, dc_stength)
        print(f"   - ranking_cech: {len(ranking)} features ranked")
        assert len(ranking) == 3, "ranking_cech failed"
        assert ranking[0]['sila'] >= ranking[1]['sila'], "ranking not sorted correctly"
        
        # Test generuj_wnioski
        wnioski = teacher.generuj_wnioski(ranking)
        print(f"   - generuj_wnioski: {len(wnioski)} conclusions")
        
        # Test generuj_reguly
        reguly = teacher.generuj_reguly(ranking)
        print(f"   - generuj_reguly: {len(reguly)} rules")
        
        # Test analiza_zmian
        zmiany = teacher.analiza_zmian(ranking)
        print(f"   - analiza_zmian: {zmiany}")
        
        print("SUCCESS: All methods tested successfully")
        return True
    except Exception as e:
        print(f"FAILED: Method testing error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_uruchom_analyse():
    """Test 5: Test głównej metody uruchom_analyse"""
    print("\n" + "=" * 60)
    print("TEST 5: Testing uruchom_analyse method")
    print("=" * 60)
    
    try:
        import pandas as pd
        import numpy as np
        from SSI_V5.teachers.cognitive_teacher import CognitiveTeacher
        
        # Stwórz większy testowy DataFrame
        np.random.seed(42)
        n_samples = 20
        test_data = {
            'cecha1': np.random.rand(n_samples) * 10,
            'cecha2': np.random.rand(n_samples) * 5,
            'cecha3': np.random.rand(n_samples) * 2,
            'cecha4': np.random.rand(n_samples) * 8,
            'cecha5': np.random.rand(n_samples) * 3,
            'wynik': ['1:0', '2:1', '3:0', '1:1', '2:2', '0:0', '3:1', '1:2', '2:0', '1:1'] * 2
        }
        df = pd.DataFrame(test_data)
        cechy = ['cecha1', 'cecha2', 'cecha3', 'cecha4', 'cecha5']
        
        teacher = CognitiveTeacher(
            df=df,
            cechy=cechy,
            siec_name="test_network_full",
            use_rf=False  # Wyłącz RF dla szybszego testu
        )
        
        # Uruchom pełną analizę
        result = teacher.uruchom_analyse()
        
        # Sprawdź struktury wyniku
        expected_keys = ['pamiec', 'wiedza', 'ranking', 'wnioski', 'reguly', 'zmiany', 'swiat', 'wagi']
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"
            print(f"   - {key}: OK")
        
        # Sprawdź zawartość
        assert len(result['ranking']) > 0, "Empty ranking"
        assert len(result['wnioski']) >= 0, "Empty wnioski"
        assert len(result['reguly']) >= 0, "Empty reguly"
        assert isinstance(result['pamiec'], dict), "pamiec should be dict"
        assert isinstance(result['wiedza'], dict), "wiedza should be dict"
        
        print("SUCCESS: uruchom_analyse method tested successfully")
        return True
    except Exception as e:
        print(f"FAILED: uruchom_analyse testing error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_compatibility():
    """Test 6: Porównanie zachowania z oryginalną klasą w generatorze"""
    print("\n" + "=" * 60)
    print("TEST 6: Compatibility check")
    print("=" * 60)
    
    try:
        import pandas as pd
        import numpy as np
        from SSI_V5.teachers.cognitive_teacher import CognitiveTeacher
        
        # Stwórz testowy DataFrame
        test_data = {
            'cecha1': [1.0, 2.0, 3.0, 4.0, 5.0],
            'cecha2': [0.5, 1.5, 2.5, 3.5, 4.5],
            'wynik': ['1:0', '2:1', '3:0', '1:1', '2:2']
        }
        df = pd.DataFrame(test_data)
        cechy = ['cecha1', 'cecha2']
        
        # Test ze użyciem nowej klasy
        teacher_new = CognitiveTeacher(df, cechy, "test_network", use_rf=False)
        
        # Sprawdź, czy klasa ma wszystkie wymagane atrybuty
        required_attrs = [
            'df', 'cechy', 'siec_name', 'use_rf', 'world_hierarchy', 'weights_manager',
            'historia_uczenia', 'wszystkie_wnioski', 'swiat_doswiadczenia',
            'parse_wynik', 'prepare_teacher_targets', 'oblicz_korelacje',
            'oblicz_random_forest_importance', 'oblicz_dixon_coles', 'oblicz_sile_cechy',
            'ranking_cech', 'generuj_wnioski', 'generuj_reguly', 'analiza_zmian',
            'zapisz_pamiec', 'zapisz_wiedze', 'wczytaj_pamiec', 'wczytaj_wiedze',
            'uruchom_analyse', 'analizuj_hierarchie_swiatow', 'oblicz_dynamiczne_wagi',
            'zapisz_doswiadczenie_swiata'
        ]
        
        for attr in required_attrs:
            assert hasattr(teacher_new, attr), f"Missing attribute/method: {attr}"
        
        print("SUCCESS: All required attributes and methods present")
        print(f"   - Found {len(required_attrs)} required attributes/methods")
        return True
    except Exception as e:
        print(f"FAILED: Compatibility check error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Główna funkcja testowa"""
    print("SSI V5 - ETAP 5.2.4 FAZA 3.1")
    print("Testing CognitiveTeacher Migration")
    print("=" * 60)
    
    tests = [
        test_import,
        test_import_from_teachers,
        test_initialization,
        test_methods,
        test_uruchom_analyse,
        test_compatibility
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results), 1):
        status = "PASS" if result else "FAIL"
        print(f"{i}. {test.__name__}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nALL TESTS PASSED! CognitiveTeacher migration successful.")
        return 0
    else:
        print(f"\n{total - passed} test(s) failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())