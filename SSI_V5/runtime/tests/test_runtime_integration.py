# SSI V5 Runtime Tests - Integration Tests
# ==================================================
#
# ETAP: 5.2.4 FAZA 3.3.3
# Data: 2026-08-03
#
# Testy integracyjne sprawdzajace glowna funkcjonalnosc runtime layer

import unittest
import tempfile
import os
from pathlib import Path
import shutil
import json

# Dodanie sciezki do SSI_V5
import sys
project_root = Path(__file__).parent.parent.parent.parent
ssi_path = str(project_root)
if ssi_path not in sys.path:
    sys.path.insert(0, ssi_path)

runtime_path = str(Path(__file__).parent.parent)
if runtime_path not in sys.path:
    sys.path.insert(0, runtime_path)


class TestRuntimeImport(unittest.TestCase):
    """Testy importowania wszystkich komponentow runtime."""
    
    def test_import_all_components(self):
        """Test importowania wszystkich kluczowych komponentow."""
        # Test Launcher components
        from SSI_V5.runtime.start_ssi_test import TestLauncher, FileManager, CONFIG_TEST
        self.assertTrue(callable(TestLauncher))
        self.assertTrue(callable(FileManager))
        self.assertTrue(isinstance(CONFIG_TEST, dict))
        
        # Production Launcher components
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
        self.assertTrue(isinstance(CONFIG_PRODUCTION, dict))
    
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


class TestFileManagerIntegration(unittest.TestCase):
    """Testy integracyjne dla FileManager."""
    
    def setUp(self):
        """Inicjalizacja."""
        self.temp_dir = tempfile.mkdtemp(prefix="ssi_integration_test_")
    
    def tearDown(self):
        """Czyszczenie."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_file_manager_operations(self):
        """Test podstawowych operacji FileManager."""
        from SSI_V5.runtime.start_ssi_test import FileManager, CONFIG_TEST
        
        config = {
            **CONFIG_TEST,
            "output_dir": self.temp_dir,
            "files": CONFIG_TEST["files"]
        }
        
        file_manager = FileManager(base_dir=self.temp_dir, config=config)
        
        # Test zapisywania i odczytu
        test_data = {"test": "data", "timestamp": "2026-08-03T15:00:00"}
        
        # Zapis runtime_state
        result1 = file_manager.save_runtime_state(test_data)
        self.assertTrue(result1)
        
        # Odczyt runtime_state
        loaded = file_manager.load_runtime_state()
        self.assertEqual(loaded["test"], "data")
        
        # Zapis last_cycle
        cycle_data = {"cycle_id": "TEST_001", "status": "complete"}
        result2 = file_manager.save_last_cycle(cycle_data)
        self.assertTrue(result2)
        
        # Odczyt last_cycle
        loaded_cycle = file_manager.load_last_cycle()
        self.assertEqual(loaded_cycle["cycle_id"], "TEST_001")
        
        # Sprawdzenie ze pliki istnieja
        runtime_file = Path(self.temp_dir) / "runtime_state.json"
        last_cycle_file = Path(self.temp_dir) / "last_cycle.json"
        
        self.assertTrue(runtime_file.exists())
        self.assertTrue(last_cycle_file.exists())


class TestTimeManagerIntegration(unittest.TestCase):
    """Testy integracyjne dla TimeManager."""
    
    def test_time_manager_basic(self):
        """Test podstawowych funkcji TimeManager."""
        from SSI_V5.runtime.start_ssi import TimeManager
        
        time_manager = TimeManager(max_runtime_hours=5, time_buffer_minutes=5)
        
        # Inicjalizacja
        time_manager.initialize()
        
        self.assertIsNotNone(time_manager.start_time)
        self.assertIsNotNone(time_manager.end_time)
        
        # Test get_time_summary
        summary = time_manager.get_time_summary()
        self.assertIn('start_time', summary)
        self.assertIn('end_time', summary)
        self.assertIn('elapsed_seconds', summary)
        self.assertIn('remaining_seconds', summary)
    
    def test_time_manager_should_continue(self):
        """Test funkcji should_continue."""
        from SSI_V5.runtime.start_ssi import TimeManager
        from datetime import datetime, timedelta
        
        # Ustawiamy start_time na 1 godzine temu
        start_time = datetime.now() - timedelta(hours=1)
        
        time_manager = TimeManager(max_runtime_hours=2, time_buffer_minutes=10)
        time_manager.initialize(start_time=start_time)
        
        # Powinien kontynuowac (masz 1 godzine pracy i bufor 10 minut)
        result = time_manager.should_continue()
        self.assertIsInstance(result, bool)


class TestRecoveryManagerIntegration(unittest.TestCase):
    """Testy integracyjne dla RecoveryManager."""
    
    def setUp(self):
        """Inicjalizacja."""
        self.temp_dir = tempfile.mkdtemp(prefix="ssi_recovery_integration_test_")
    
    def tearDown(self):
        """Czyszczenie."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_recovery_manager_operations(self):
        """Test podstawowych operacji RecoveryManager."""
        from SSI_V5.runtime.start_ssi import RecoveryManager, CONFIG_PRODUCTION
        
        config = {
            **CONFIG_PRODUCTION,
            "output_dir": self.temp_dir,
            "files": CONFIG_PRODUCTION["files"]
        }
        
        recovery_manager = RecoveryManager(base_dir=self.temp_dir, config=config)
        
        # Poczatkowo nie ma recovery
        has_recovery = recovery_manager.check_for_recovery()
        self.assertFalse(has_recovery)
        
        # Zapis recovery_info
        recovery_info = {
            "session_id": "TEST_SESSION_001",
            "start_time": "2026-08-03T15:00:00",
            "cycle_count": 5
        }
        
        result = recovery_manager.save_recovery_info(recovery_info)
        self.assertTrue(result)
        
        # Teraz powinno byc recovery
        has_recovery = recovery_manager.check_for_recovery()
        self.assertTrue(has_recovery)
        
        # Odczyt recovery_info
        loaded_info = recovery_manager.load_recovery_info()
        self.assertEqual(loaded_info["session_id"], "TEST_SESSION_001")
        self.assertEqual(loaded_info["cycle_count"], 5)


class TestLauncherIntegration(unittest.TestCase):
    """Testy integracyjne dla launcherow."""
    
    def setUp(self):
        """Inicjalizacja."""
        self.temp_dir = tempfile.mkdtemp(prefix="ssi_launcher_integration_test_")
    
    def tearDown(self):
        """Czyszczenie."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_test_launcher_initialization(self):
        """Test inicjalizacji TestLauncher."""
        from SSI_V5.runtime.start_ssi_test import TestLauncher, CONFIG_TEST
        
        config = {
            **CONFIG_TEST,
            "output_dir": self.temp_dir,
            "num_cycles": 1,  # Tylko 1 cykl dla testu
            "files": CONFIG_TEST["files"]
        }
        
        launcher = TestLauncher(config=config)
        init_result = launcher.initialize()
        
        self.assertEqual(init_result["status"], "success")
        self.assertIsNotNone(launcher.pipeline)
        self.assertTrue(launcher.pipeline._initialized)
    
    def test_production_launcher_initialization(self):
        """Test inicjalizacji ProductionLauncher."""
        from SSI_V5.runtime.start_ssi import ProductionLauncher, CONFIG_PRODUCTION
        from SSI_V5.core.pipeline import PipelineMode
        
        config = {
            **CONFIG_PRODUCTION,
            "output_dir": self.temp_dir,
            "max_runtime_hours": 0.1,  # 6 minut
            "files": CONFIG_PRODUCTION["files"]
        }
        
        launcher = ProductionLauncher(config=config)
        init_result = launcher.initialize()
        
        self.assertEqual(init_result["status"], "success")
        self.assertIsNotNone(launcher.pipeline)
        self.assertEqual(launcher.pipeline.mode, PipelineMode.PRODUCTION)
        self.assertIsNotNone(launcher.session_id)
        self.assertIsNotNone(launcher.time_manager)
        self.assertIsNotNone(launcher.recovery_manager)
        self.assertIsNotNone(launcher.state_manager)
    
    def test_test_launcher_cycle_execution(self):
        """Test wykonania cykli przez TestLauncher."""
        from SSI_V5.runtime.start_ssi_test import TestLauncher, CONFIG_TEST
        
        config = {
            **CONFIG_TEST,
            "output_dir": self.temp_dir,
            "num_cycles": 1,  # Tylko 1 cykl
            "files": CONFIG_TEST["files"]
        }
        
        launcher = TestLauncher(config=config)
        init_result = launcher.initialize()
        self.assertEqual(init_result["status"], "success")
        
        # Wykonanie 1 cyklu
        cycle_result = launcher.run_test_cycles()
        
        self.assertEqual(cycle_result["status"], "success")
        self.assertEqual(cycle_result["total_cycles"], 1)
    
    def test_launcher_state_saving(self):
        """Test zapisywania stanu przez launcher."""
        from SSI_V5.runtime.start_ssi_test import TestLauncher, CONFIG_TEST
        
        # Użyj state directory jako bazowego
        state_dir = Path(self.temp_dir) / "state"
        state_dir.mkdir(exist_ok=True)
        
        config = {
            **CONFIG_TEST,
            "output_dir": "state",
            "num_cycles": 1,
            "files": CONFIG_TEST["files"]
        }
        
        # Zmien working directory
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            
            launcher = TestLauncher(config=config)
            init_result = launcher.initialize()
            self.assertEqual(init_result["status"], "success")
            
            # Wykonanie cykli
            launcher.run_test_cycles()
            
            # Zapis stanu
            state_result = launcher.save_state()
            self.assertEqual(state_result["status"], "success")
            
            # Sprawdzenie czy pliki zostaly utworzone
            for filename in ["runtime_state.json", "last_cycle.json", "cycle_history.json", "event_log.json"]:
                file_path = state_dir / filename
                self.assertTrue(file_path.exists(), f"Plik {filename} nie zostal utworzony")
        finally:
            os.chdir(original_cwd)


class TestStateFilesFormat(unittest.TestCase):
    """Testy formatu plikow stanu."""
    
    def setUp(self):
        """Inicjalizacja."""
        self.temp_dir = tempfile.mkdtemp(prefix="ssi_state_format_test_")
    
    def tearDown(self):
        """Czyszczenie."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_state_files_are_valid_json(self):
        """Test czy pliki stanu sa poprawnym JSON."""
        from SSI_V5.runtime.start_ssi_test import TestLauncher, CONFIG_TEST
        
        # Użyj state directory jako bazowego
        state_dir = Path(self.temp_dir) / "state"
        state_dir.mkdir(exist_ok=True)
        
        config = {
            **CONFIG_TEST,
            "output_dir": "state",
            "num_cycles": 1,
            "files": CONFIG_TEST["files"]
        }
        
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            
            launcher = TestLauncher(config=config)
            launcher.initialize()
            launcher.run_test_cycles()
            launcher.save_state()
            
            # Sprawdzenie wszystkie pliki JSON
            for filename in ["runtime_state.json", "last_cycle.json", "cycle_history.json", "event_log.json"]:
                file_path = state_dir / filename
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.assertIsInstance(data, (dict, list))
        finally:
            os.chdir(original_cwd)
    
    def test_runtime_state_structure(self):
        """Test struktury runtime_state.json."""
        from SSI_V5.runtime.start_ssi_test import TestLauncher, CONFIG_TEST
        
        # Użyj state directory jako bazowego
        state_dir = Path(self.temp_dir) / "state"
        state_dir.mkdir(exist_ok=True)
        
        config = {
            **CONFIG_TEST,
            "output_dir": "state",
            "num_cycles": 1,
            "files": CONFIG_TEST["files"]
        }
        
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            
            launcher = TestLauncher(config=config)
            launcher.initialize()
            launcher.run_test_cycles()
            launcher.save_state()
            
            # Odczyt runtime_state.json
            runtime_file = state_dir / "runtime_state.json"
            with open(runtime_file, 'r', encoding='utf-8') as f:
                runtime_state = json.load(f)
            
            # Sprawdzenie kluczowych pol
            self.assertIn("mode", runtime_state)
            self.assertIn("start_time", runtime_state)
            self.assertIn("end_time", runtime_state)
            self.assertIn("pipeline_status", runtime_state)
            self.assertIn("system_info", runtime_state)
            
            # Sprawdzenie system_info
            self.assertEqual(runtime_state["system_info"]["launcher"], "start_ssi_test.py")
            self.assertEqual(runtime_state["system_info"]["etap"], "5.2.4")
            self.assertEqual(runtime_state["system_info"]["faza"], "3.3.3")
        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()
