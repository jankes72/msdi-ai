# SSI V5 Runtime Tests - Launchers Integration
# ==================================================
#
# ETAP: 5.2.4 FAZA 3.3.3
# Data: 2026-08-03
#
# Testy integracyjne dla TestLauncher i ProductionLauncher

import unittest
import tempfile
import os
from pathlib import Path
import shutil
from datetime import datetime
import sys

# Dodanie sciezki do SSI_V5
project_root = Path(__file__).parent.parent.parent.parent
ssi_path = str(project_root)
if ssi_path not in sys.path:
    sys.path.insert(0, ssi_path)

runtime_path = str(Path(__file__).parent.parent)
if runtime_path not in sys.path:
    sys.path.insert(0, runtime_path)

from SSI_V5.runtime.start_ssi_test import TestLauncher, CONFIG_TEST
from SSI_V5.runtime.start_ssi import ProductionLauncher, CONFIG_PRODUCTION
from SSI_V5.core.pipeline import PipelineMode


class TestTestLauncher(unittest.TestCase):
    """Testy dla TestLauncher."""
    
    def setUp(self):
        """Inicjalizacja przed kazdym testem."""
        # Tworzenie tymczasowego katalogu
        self.temp_dir = tempfile.mkdtemp(prefix="ssi_test_launcher_")
        self.test_config = {
            **CONFIG_TEST,
            "output_dir": self.temp_dir,
            "files": {
                "runtime_state": "runtime_state.json",
                "last_cycle": "last_cycle.json",
                "cycle_history": "cycle_history.json",
                "event_log": "event_log.json"
            }
        }
        self.launcher = TestLauncher(config=self.test_config)
    
    def tearDown(self):
        """Czyszczenie po kazdym teście."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test inicjalizacji TestLauncher."""
        self.assertIsNotNone(self.launcher)
        self.assertIsNotNone(self.launcher.config)
        self.assertIsNone(self.launcher.pipeline)
        self.assertIsNone(self.launcher.file_manager)
    
    def test_initialize_success(self):
        """Test udanej inicjalizacji."""
        init_result = self.launcher.initialize()
        
        self.assertEqual(init_result["status"], "success")
        self.assertIn("message", init_result)
        self.assertIn("pipeline_status", init_result)
        self.assertIn("timestamp", init_result)
        
        # Sprawdzenie czy pipeline zostal zainicjalizowany
        self.assertIsNotNone(self.launcher.pipeline)
        self.assertTrue(self.launcher.pipeline._initialized)
        
        # Sprawdzenie czy file_manager znosta zainicjalizowany
        self.assertIsNotNone(self.launcher.file_manager)
    
    def test_initialize_with_pipeline_mode(self):
        """Test inicjalizacji z trybem TEST."""
        init_result = self.launcher.initialize()
        
        self.assertEqual(init_result["status"], "success")
        self.assertEqual(self.launcher.pipeline.mode, PipelineMode.TEST)
    
    def test_run_test_cycles(self):
        """Test wykonania cykli testowych."""
        # Inicjalizacja
        init_result = self.launcher.initialize()
        self.assertEqual(init_result["status"], "success")
        
        # Wykonanie cykli - przyblizone (maksymalnie 3 cyklu aby nie trwalo za dlugo)
        self.launcher.config["num_cycles"] = 3
        cycle_result = self.launcher.run_test_cycles()
        
        self.assertEqual(cycle_result["status"], "success")
        self.assertEqual(cycle_result["total_cycles"], 3)
        self.assertIn("launcher_config", cycle_result)
        self.assertIn("cycle_results", cycle_result)
    
    def test_save_state(self):
        """Test zapisywania stanu."""
        # Inicjalizacja
        init_result = self.launcher.initialize()
        self.assertEqual(init_result["status"], "success")
        
        # Wykonanie cykli
        self.launcher.config["num_cycles"] = 2
        self.launcher.run_test_cycles()
        
        # Zapis stanu
        state_result = self.launcher.save_state()
        
        self.assertEqual(state_result["status"], "success")
        self.assertIn("files_saved", state_result)
        
        # Sprawdzenie czy pliki zostaly utworzone
        for filename in ["runtime_state.json", "last_cycle.json", "cycle_history.json", "event_log.json"]:
            file_path = Path(self.temp_dir) / filename
            self.assertTrue(file_path.exists(), f"Plik {filename} nie zostal utworzony")
    
    def test_full_run(self):
        """Test pelnego przebiegu testowego."""
        # Uruchomienie pelnego przebiegu
        self.launcher.config["num_cycles"] = 2  # Tylko 2 cykle aby nie trwalo za dlugo
        result = self.launcher.run()
        
        self.assertIn("status", result)
        self.assertIn("steps", result)
        self.assertIn("summary", result)
        self.assertIn("timestamp", result)
        
        # Sprawdzenie krokow
        steps = result["steps"]
        self.assertIn("initialization", steps)
        self.assertIn("cycle_execution", steps)
        self.assertIn("state_saving", steps)
        self.assertIn("shutdown", steps)
        
        # Sprawdzenie podsumowania
        summary = result["summary"]
        self.assertIn("total_cycles", summary)
        self.assertIn("successful_cycles", summary)
        self.assertIn("failed_cycles", summary)


class TestTestLauncherShutdown(unittest.TestCase):
    """Testy zamkniecia TestLauncher."""
    
    def setUp(self):
        """Inicjalizacja."""
        self.temp_dir = tempfile.mkdtemp(prefix="ssi_shutdown_test_")
        self.test_config = {
            **CONFIG_TEST,
            "output_dir": self.temp_dir,
            "files": CONFIG_TEST["files"]
        }
        self.launcher = TestLauncher(config=self.test_config)
    
    def tearDown(self):
        """Czyszczenie."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_shutdown(self):
        """Test graceful shutdown."""
        # Inicjalizacja
        init_result = self.launcher.initialize()
        self.assertEqual(init_result["status"], "success")
        
        # Shutdown
        shutdown_result = self.launcher.shutdown()
        
        self.assertIn("status", shutdown_result)
        self.assertIn("start_time", shutdown_result)
        self.assertIn("end_time", shutdown_result)
        self.assertIn("duration", shutdown_result)
        self.assertIn("pipeline_shutdown", shutdown_result)
        
        # Sprawdzenie ze pipeline zostal zamkniety
        self.assertFalse(self.launcher.pipeline._initialized)


class TestProductionLauncher(unittest.TestCase):
    """Testy dla ProductionLauncher."""
    
    def setUp(self):
        """Inicjalizacja przed kazdym testem."""
        self.temp_dir = tempfile.mkdtemp(prefix="ssi_prod_launcher_test_")
        self.test_config = {
            **CONFIG_PRODUCTION,
            "max_runtime_hours": 0.1,  # 6 minut - skrocony czas dla testow
            "time_buffer_minutes": 1,  # 1 minuta buforu
            "check_interval_seconds": 0.01,  # Bardzo krotki interval
            "output_dir": self.temp_dir,
            "files": {
                "runtime_state": "runtime_state.json",
                "last_cycle": "last_cycle.json",
                "cycle_history": "cycle_history.json",
                "event_log": "event_log.json",
                "recovery_info": "recovery_info.json"
            }
        }
        self.launcher = ProductionLauncher(config=self.test_config)
    
    def tearDown(self):
        """Czyszczenie po kazdym teście."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test inicjalizacji ProductionLauncher."""
        init_result = self.launcher.initialize()
        
        self.assertEqual(init_result["status"], "success")
        self.assertIn("session_id", init_result)
        self.assertIn("recovery_mode", init_result)
        
        # Sprawdzenie czy wszystkie managery zostaly zainicjalizowane
        self.assertIsNotNone(self.launcher.pipeline)
        self.assertIsNotNone(self.launcher.time_manager)
        self.assertIsNotNone(self.launcher.state_manager)
        self.assertIsNotNone(self.launcher.recovery_manager)
        self.assertIsNotNone(self.launcher.session_id)
    
    def test_pipeline_mode_production(self):
        """Test trybu PRODUCTION."""
        init_result = self.launcher.initialize()
        self.assertEqual(init_result["status"], "success")
        
        self.assertEqual(self.launcher.pipeline.mode, PipelineMode.PRODUCTION)
    
    def test_time_manager_initialization(self):
        """Test inicjalizacji TimeManager."""
        init_result = self.launcher.initialize()
        self.assertEqual(init_result["status"], "success")
        
        self.assertIsNotNone(self.launcher.time_manager.start_time)
        self.assertIsNotNone(self.launcher.time_manager.end_time)
        
        # Sprawdzenie czy end_time jest max_runtime_hours pozniej
        expected_duration = self.test_config["max_runtime_hours"]
        actual_duration = (self.launcher.time_manager.end_time - self.launcher.time_manager.start_time).total_seconds() / 3600
        self.assertAlmostEqual(actual_duration, expected_duration, places=1)
    
    def test_recovery_manager_detection(self):
        """Test wykrywania stanu recovery."""
        # Inicjalizacja bez pliku recovery
        init_result = self.launcher.initialize()
        self.assertEqual(init_result["status"], "success")
        
        # Powinien byc False (brak pliku recovery)
        self.assertFalse(init_result["recovery_mode"])
    
    def test_launchers_with_existing_recovery_files(self):
        """Test inicjalizacji z istniejacymi plikami recovery."""
        # Utworzenie pliku recovery_info.json
        recovery_info = {
            "session_id": "PREV_SESSION_001",
            "start_time": "2026-08-03T14:00:00",
            "cycle_count": 10
        }
        
        recovery_file = Path(self.temp_dir) / "recovery_info.json"
        with open(recovery_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(recovery_info, f)
        
        # Inicjalizacja - powinna wykryc recovery
        init_result = self.launcher.initialize()
        
        # Powinien byc True - recovery wykryte
        self.assertTrue(init_result["recovery_mode"])
    
    def test_production_cycle_execution(self):
        """Test wykonania pojedynczego cyklu produkcyjnego."""
        init_result = self.launcher.initialize()
        self.assertEqual(init_result["status"], "success")
        
        # Wykonanie pojedynczego cyklu
        cycle_result = self.launcher.run_production_cycle()
        
        self.assertIn("status", cycle_result)
        self.assertIn("cycle_id", cycle_result)
        self.assertIn("timestamp", cycle_result)
    
    def test_save_intermediate_state(self):
        """Test zapisu posredniego stanu."""
        init_result = self.launcher.initialize()
        self.assertEqual(init_result["status"], "success")
        
        # Wykonanie cyklu
        self.launcher.run_production_cycle()
        
        # Zapis stanu
        save_result = self.launcher._save_intermediate_state()
        
        self.assertTrue(save_result)
        
        # Sprawdzenie czy pliki zostaly utworzone
        for filename in ["runtime_state.json", "recovery_info.json"]:
            file_path = Path(self.temp_dir) / filename
            self.assertTrue(file_path.exists(), f"Plik {filename} nie zostal utworzony")


class TestProductionLauncherShutdown(unittest.TestCase):
    """Testy zamkniecia ProductionLauncher."""
    
    def setUp(self):
        """Inicjalizacja."""
        self.temp_dir = tempfile.mkdtemp(prefix="ssi_prod_shutdown_test_")
        self.test_config = {
            **CONFIG_PRODUCTION,
            "max_runtime_hours": 0.1,
            "time_buffer_minutes": 1,
            "output_dir": self.temp_dir,
            "files": CONFIG_PRODUCTION["files"]
        }
        self.launcher = ProductionLauncher(config=self.test_config)
    
    def tearDown(self):
        """Czyszczenie."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_shutdown(self):
        """Test graceful shutdown ProductionLauncher."""
        # Inicjalizacja
        init_result = self.launcher.initialize()
        self.assertEqual(init_result["status"], "success")
        
        # Shutdown
        shutdown_result = self.launcher.shutdown()
        
        self.assertIn("status", shutdown_result)
        self.assertIn("session_id", shutdown_result)
        self.assertIn("start_time", shutdown_result)
        self.assertIn("end_time", shutdown_result)
        self.assertIn("duration", shutdown_result)
        
        # Sprawdzenie ze pipeline zostal zamkniety
        self.assertFalse(self.launcher.running)


class TestLauncherImport(unittest.TestCase):
    """Testy importowania komponentow."""
    
    def test_import_test_launcher(self):
        """Test importowania TestLauncher."""
        from SSI_V5.runtime.start_ssi_test import TestLauncher, FileManager, CONFIG_TEST
        self.assertTrue(callable(TestLauncher))
        self.assertTrue(callable(FileManager))
    
    def test_import_production_launcher(self):
        """Test importowania ProductionLauncher."""
        from SSI_V5.runtime.start_ssi import (
            ProductionLauncher, 
            RecoveryManager, 
            TimeManager, 
            StateManager,
            CONFIG_PRODUCTION
        )
        self.assertTrue(callable(ProductionLauncher))
        self.assertTrue(callable(RecoveryManager))
        self.assertTrue(callable(TimeManager))
        self.assertTrue(callable(StateManager))
    
    def test_import_from_runtime_namespace(self):
        """Test importowania z namespace runtime."""
        from SSI_V5.runtime import (
            TestLauncher,
            FileManager,
            ProductionLauncher,
            RecoveryManager,
            TimeManager,
            StateManager
        )
        self.assertTrue(callable(TestLauncher))
        self.assertTrue(callable(FileManager))
        self.assertTrue(callable(ProductionLauncher))
        self.assertTrue(callable(RecoveryManager))
        self.assertTrue(callable(TimeManager))
        self.assertTrue(callable(StateManager))


if __name__ == "__main__":
    unittest.main()
