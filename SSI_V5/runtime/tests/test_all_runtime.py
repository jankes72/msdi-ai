# SSI V5 Runtime Tests - All Tests Suite
# ==================================================
#
# ETAP: 5.2.4 FAZA 3.3.3
# Data: 2026-08-03
#
# Glowny modul testowy uruchamiajacy wszystkie testy runtime layer

import unittest
import sys
import os
from pathlib import Path

# Dodanie sciezki do SSI_V5
project_root = Path(__file__).parent.parent.parent.parent
ssi_path = str(project_root)
if ssi_path not in sys.path:
    sys.path.insert(0, ssi_path)

# Dodanie sciezki do runtime
runtime_path = str(Path(__file__).parent.parent)
if runtime_path not in sys.path:
    sys.path.insert(0, runtime_path)

# Teraz moga byc importowane
from SSI_V5.runtime.tests.test_file_manager import TestFileManager, TestFileManagerErrorHandling
from SSI_V5.runtime.tests.test_time_manager import TestTimeManager, TestTimeManagerEdgeCases
from SSI_V5.runtime.tests.test_recovery_manager import TestRecoveryManager, TestRecoveryManagerEdgeCases
from SSI_V5.runtime.tests.test_launchers import (
    TestTestLauncher,
    TestTestLauncherShutdown,
    TestProductionLauncher,
    TestProductionLauncherShutdown,
    TestLauncherImport
)


def create_test_suite():
    """
    Utworzenie considérés test suite z wszystkich testow.
    
    Returns:
        unittest.TestSuite z wszystkimi testami
    """
    # Utworzenie test suite
    test_suite = unittest.TestSuite()
    
    # Dodawanie wszystkich klas testowych
    
    # FileManager tests (9 testow)
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestFileManager))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestFileManagerErrorHandling))
    
    # TimeManager tests (12 testow)
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestTimeManager))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestTimeManagerEdgeCases))
    
    # RecoveryManager tests (14 testow)
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestRecoveryManager))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestRecoveryManagerEdgeCases))
    
    # Launcher tests (17 testow)
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestTestLauncher))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestTestLauncherShutdown))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestProductionLauncher))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestProductionLauncherShutdown))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestLauncherImport))
    
    return test_suite


def run_all_tests():
    """
    Uruchomienie wszystkich testow z raportem.
    
    Returns:
        Wynik uruchomienia testow
    """
    print("\n" + "=" * 80)
    print("SSI V5 RUNTIME TESTS - ETAP 5.2.4 FAZA 3.3.3")
    print("Running all runtime layer tests...")
    print("=" * 80 + "\n")
    
    # Utworzenie test runner
    test_runner = unittest.TextTestRunner(
        verbosity=2,  # Pokazuje nazwy testow
        stream=sys.stdout
    )
    
    # Utworzenie i uruchomienie test suite
    test_suite = create_test_suite()
    result = test_runner.run(test_suite)
    
    # Podsumowanie
    print("\n" + "=" * 80)
    print("RUNTIME LAYER TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / max(result.testsRun, 1) * 100):.1f}%")
    print("=" * 80 + "\n")
    
    return result


def get_test_count():
    """
    Pobranie liczby dostepnych testow.
    
    Returns:
        Liczba testow
    """
    test_suite = create_test_suite()
    return test_suite.countTestCases()


if __name__ == "__main__":
    # Uruchomienie wszystkich testow
    result = run_all_tests()
    
    # Zwroc kod wyjscia
    # 0 - wszystkie testy przejsly
    # 1 - byly bledy lub failury
    sys.exit(0 if result.wasSuccessful() else 1)
