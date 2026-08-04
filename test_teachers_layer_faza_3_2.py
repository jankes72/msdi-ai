#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST: ETAP 5.2.4 FAZA 3.2
Implementacja Teacher Layer - MemoryManager i ModelEvaluator
"""

import sys
import os

# Dodaj głównego katalogu SSI_V5 do path
sys.path.insert(0, 'D:/sts/aplikacjaTyperBetAi')

def test_import_all_teachers():
    """Test importu wszystkich modułów Teacher Layer"""
    print("=" * 60)
    print("TEST 1: Import all Teachers Layer modules")
    print("=" * 60)
    
    try:
        from SSI_V5.teachers import (
            CognitiveTeacher,
            WorldHierarchyManager,
            DynamicWeightsManager,
            MemoryManager,
            ModelEvaluator
        )
        
        print("SUCCESS: All Teachers Layer modules imported successfully")
        print(f"   - CognitiveTeacher: {CognitiveTeacher}")
        print(f"   - WorldHierarchyManager: {WorldHierarchyManager}")
        print(f"   - DynamicWeightsManager: {DynamicWeightsManager}")
        print(f"   - MemoryManager: {MemoryManager}")
        print(f"   - ModelEvaluator: {ModelEvaluator}")
        return True
    except Exception as e:
        print(f"FAILED: Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_manager():
    """Test MemoryManager"""
    print("\n" + "=" * 60)
    print("TEST 2: MemoryManager functionality")
    print("=" * 60)
    
    try:
        import tempfile
        import shutil
        from SSI_V5.teachers.memory_manager import MemoryManager
        
        # Tworzymy tymczasowy katalog
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Test inicjalizacji
            manager = MemoryManager(memory_dir=temp_dir, network_name="test")
            print("   - Initialization: OK")
            
            # Test pamięci świata
            manager.save_world_memory({"level": "poziom3"}, "test_world")
            world_data = manager.get_world_memory("test_world")
            assert world_data.get("level") == "poziom3"
            print("   - World memory: OK")
            
            # Test pamięci modelu
            manager.save_model_memory({"accuracy": 0.95}, "test_model")
            model_data = manager.get_model_memory("test_model")
            assert model_data.get("accuracy") == 0.95
            print("   - Model memory: OK")
            
            # Test pamięci obserwacji
            manager.save_observation_memory({"prediction": "2:1"}, "obs_1")
            obs_data = manager.get_observation_memory("obs_1")
            assert obs_data.get("prediction") == "2:1"
            print("   - Observation memory: OK")
            
            # Test historii doświadczeń
            manager.add_experience_record({"type": "test"})
            history = manager.get_experience_history()
            assert len(history) == 1
            print("   - Experience history: OK")
            
            # Test statystyk
            stats = manager.get_memory_statistics()
            assert "world_memory" in stats
            print("   - Memory statistics: OK")
            
            print("SUCCESS: MemoryManager all tests passed")
            return True
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except Exception as e:
        print(f"FAILED: MemoryManager error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_evaluator():
    """Test ModelEvaluator"""
    print("\n" + "=" * 60)
    print("TEST 3: ModelEvaluator functionality")
    print("=" * 60)
    
    try:
        import tempfile
        import shutil
        import numpy as np
        from SSI_V5.teachers.model_evaluator import ModelEvaluator
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Test inicjalizacji
            evaluator = ModelEvaluator(evaluation_dir=temp_dir, network_name="test")
            print("   - Initialization: OK")
            
            # Test oceny modelu
            y_true = [0, 1, 1, 0, 1, 1]
            y_pred = [0, 1, 0, 0, 1, 1]
            result = evaluator.evaluate_model("test_model", y_true, y_pred)
            assert result["accuracy"] > 0
            assert result["model_name"] == "test_model"
            print("   - Model evaluation: OK")
            
            # Test porównania modeli
            evaluator.evaluate_model("model_1", y_true, y_pred)
            evaluator.evaluate_model("model_2", y_true, [0, 0, 1, 0, 1, 1])
            comparison = evaluator.compare_models(["model_1", "model_2"], "accuracy")
            assert "models" in comparison
            print("   - Model comparison: OK")
            
            # Test analizy trendu
            trend = evaluator.analyze_performance_trend("test_model")
            assert "model_name" in trend
            print("   - Performance trend analysis: OK")
            
            # Test generowania raportu
            report = evaluator.generate_performance_report()
            assert "models" in report
            print("   - Performance report generation: OK")
            
            # Test statystyk
            stats = evaluator.get_evaluation_statistics()
            assert "total_evaluations" in stats
            print("   - Evaluation statistics: OK")
            
            print("SUCCESS: ModelEvaluator all tests passed")
            return True
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except Exception as e:
        print(f"FAILED: ModelEvaluator error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_teacher_layer_integration():
    """Test integracji warstwy Teacher Layer"""
    print("\n" + "=" * 60)
    print("TEST 4: Teacher Layer integration")
    print("=" * 60)
    
    try:
        import tempfile
        import shutil
        import pandas as pd
        import numpy as np
        from SSI_V5.teachers import (
            CognitiveTeacher,
            MemoryManager,
            ModelEvaluator
        )
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Tworzymy testowe dane
            test_data = {
                'cecha1': np.random.rand(10) * 10,
                'cecha2': np.random.rand(10) * 5,
                'cecha3': np.random.rand(10) * 3,
                'wynik': ['1:0', '2:1', '3:0', '1:1', '2:2', '0:0', '3:1', '1:2', '2:0', '1:1']
            }
            df = pd.DataFrame(test_data)
            cechy = ['cecha1', 'cecha2', 'cecha3']
            
            # Inicjalizacja components
            teacher = CognitiveTeacher(
                df=df,
                cechy=cechy,
                siec_name="test_network",
                use_rf=False
            )
            
            memory_manager = MemoryManager(memory_dir=temp_dir, network_name="test_network")
            model_evaluator = ModelEvaluator(evaluation_dir=temp_dir, network_name="test_network")
            
            print("   - Component initialization: OK")
            
            # Test uruchom_analyse z CognitiveTeacher
            teacher_result = teacher.uruchom_analyse()
            assert "ranking" in teacher_result
            assert "wnioski" in teacher_result
            print("   - CognitiveTeacher analysis: OK")
            
            # Integracja MemoryManager z teacher result
            prepared_memory = memory_manager.prepare_memory_for_next_cycle(teacher_result)
            assert "world_data" in prepared_memory
            assert "ranking" in prepared_memory
            print("   - MemoryManager integration: OK")
            
            # Integracja ModelEvaluator z teacher result
            teacher_eval = model_evaluator.evaluate_teacher_performance(teacher_result)
            assert "teacher_analysis" in teacher_eval
            print("   - ModelEvaluator integration: OK")
            
            print("SUCCESS: Teacher Layer integration tests passed")
            return True
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except Exception as e:
        print(f"FAILED: Teacher Layer integration error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_compatibility():
    """Test kompatybilności wszystkich modułów"""
    print("\n" + "=" * 60)
    print("TEST 5: Teacher Layer compatibility check")
    print("=" * 60)
    
    try:
        from SSI_V5.teachers import (
            CognitiveTeacher,
            WorldHierarchyManager,
            DynamicWeightsManager,
            MemoryManager,
            ModelEvaluator
        )
        
        # Sprawdź, czy wszystkie klasy mają wymagane metody
        required_methods = {
            CognitiveTeacher: ['__init__', 'uruchom_analyse', 'parse_wynik', 'prepare_teacher_targets'],
            WorldHierarchyManager: ['__init__', 'wybierz_najlepszy_poziom', 'get_world_levels'],
            DynamicWeightsManager: ['__init__', 'oblicz_wage_swiata', 'oblicz_wagi_klas', 'oblicz_wagi_modelu_i_swiata'],
            MemoryManager: ['__init__', 'save_world_memory', 'get_world_memory', 'save_model_memory'],
            ModelEvaluator: ['__init__', 'evaluate_model', 'compare_models', 'generate_performance_report']
        }
        
        for cls, methods in required_methods.items():
            for method in methods:
                assert hasattr(cls, method), f"Missing method {method} in {cls.__name__}"
            print(f"   - {cls.__name__}: All required methods present")
        
        print("SUCCESS: All modules have required methods")
        return True
        
    except Exception as e:
        print(f"FAILED: Compatibility check error: {e}")
        return False

def main():
    """Główna funkcja testowa"""
    print("SSI V5 - ETAP 5.2.4 FAZA 3.2")
    print("Testing Teacher Layer Implementation")
    print("=" * 60)
    
    tests = [
        test_import_all_teachers,
        test_memory_manager,
        test_model_evaluator,
        test_teacher_layer_integration,
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
        print("\nALL TESTS PASSED! Teacher Layer implementation successful.")
        print("\nImplementated modules:")
        print("  - MemoryManager (SSI_V5/teachers/memory_manager.py)")
        print("  - ModelEvaluator (SSI_V5/teachers/model_evaluator.py)")
        print("\nAvailable modules:")
        print("  - CognitiveTeacher")
        print("  - WorldHierarchyManager")
        print("  - DynamicWeightsManager")
        print("  - MemoryManager")
        print("  - ModelEvaluator")
        return 0
    else:
        print(f"\n{total - passed} test(s) failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())