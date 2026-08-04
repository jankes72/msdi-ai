# SSI V5 Runtime Tests - RecoveryManager
# ==================================================
#
# ETAP: 5.2.4 FAZA 3.3.3
# Data: 2026-08-03
#
# Testy dla RecoveryManager - mechanizm recovery

import unittest
import json
import tempfile
import os
from pathlib import Path
import shutil
from datetime import datetime

# Dodanie sciezki do SSI_V5
import sys
project_root = Path(__file__).parent.parent.parent.parent
ssi_path = str(project_root)
if ssi_path not in sys.path:
    sys.path.insert(0, ssi_path)

runtime_path = str(Path(__file__).parent.parent)
if runtime_path not in sys.path:
    sys.path.insert(0, runtime_path)

from SSI_V5.runtime.start_ssi import RecoveryManager, CONFIG_PRODUCTION


class TestRecoveryManager(unittest.TestCase):
    """Testy dla RecoveryManager - mechanizm odzysku."""
    
    def setUp(self):
        """Inicjalizacja przed kazdym testem."""
        # Tworzenie tymczasowego katalogu
        self.temp_dir = tempfile.mkdtemp(prefix="ssi_recovery_test_")
        self.test_config = {
            **CONFIG_PRODUCTION,
            "output_dir": self.temp_dir,
            "files": {
                "runtime_state": "runtime_state.json",
                "last_cycle": "last_cycle.json",
                "cycle_history": "cycle_history.json",
                "event_log": "event_log.json",
                "recovery_info": "recovery_info.json"
            }
        }
        self.recovery_manager = RecoveryManager(
            base_dir=self.temp_dir,
            config=self.test_config
        )
    
    def tearDown(self):
        """Czyszczenie po kazdym teście."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test inicjalizacji RecoveryManager."""
        self.assertIsNotNone(self.recovery_manager)
        self.assertIsInstance(self.recovery_manager.base_dir, Path)
        self.assertIsNotNone(self.recovery_manager.config)
    
    def test_check_for_recovery_no_files(self):
        """Test sprawdzania recovery gdy nie ma plikow."""
        # Brak plikow recovery
        has_recovery = self.recovery_manager.check_for_recovery()
        self.assertFalse(has_recovery)
    
    def test_check_for_recovery_with_file(self):
        """Test sprawdzania recovery gdy jest plik recovery_info.json."""
        # Utworzenie pliku recovery_info.json
        recovery_info = {
            "session_id": "TEST_SESSION_001",
            "start_time": datetime.now().isoformat(),
            "cycle_count": 10
        }
        
        recovery_file = self.recovery_manager.base_dir / self.test_config["files"]["recovery_info"]
        with open(recovery_file, 'w', encoding='utf-8') as f:
            json.dump(recovery_info, f, indent=2)
        
        # Powinien znalezc plik
        has_recovery = self.recovery_manager.check_for_recovery()
        self.assertTrue(has_recovery)
    
    def test_load_recovery_info(self):
        """Test ladowania informacji o recovery."""
        # Utworzenie pliku recovery_info.json
        expected_info = {
            "session_id": "TEST_SESSION_002",
            "start_time": "2026-08-03T15:00:00",
            "cycle_count": 25,
            "last_update": "2026-08-03T16:00:00"
        }
        
        recovery_file = self.recovery_manager.base_dir / self.test_config["files"]["recovery_info"]
        with open(recovery_file, 'w', encoding='utf-8') as f:
            json.dump(expected_info, f, indent=2)
        
        # Ladowanie
        loaded_info = self.recovery_manager.load_recovery_info()
        
        self.assertIsNotNone(loaded_info)
        self.assertEqual(loaded_info["session_id"], "TEST_SESSION_002")
        self.assertEqual(loaded_info["cycle_count"], 25)
    
    def test_load_recovery_info_no_file(self):
        """Test ladowania gdy nie ma pliku recovery_info."""
        # Brak pliku
        loaded_info = self.recovery_manager.load_recovery_info()
        self.assertEqual(loaded_info, {})
    
    def test_load_all_state(self):
        """Test ladowania wszystkich plikow stanu."""
        # Utworzenie wszystkich pl전이 stanu
        recovery_info = {"session_id": "SESS_001", "cycle_count": 5}
        runtime_state = {"mode": "PRODUCTION", "status": "running"}
        last_cycle = {"cycle_id": "CYCLE_005", "status": "complete"}
        
        # Zapis pliów
        recovery_file = self.recovery_manager.base_dir / self.test_config["files"]["recovery_info"]
        with open(recovery_file, 'w', encoding='utf-8') as f:
            json.dump(recovery_info, f)
        
        runtime_file = self.recovery_manager.base_dir / self.test_config["files"]["runtime_state"]
        with open(runtime_file, 'w', encoding='utf-8') as f:
            json.dump(runtime_state, f)
        
        last_cycle_file = self.recovery_manager.base_dir / self.test_config["files"]["last_cycle"]
        with open(last_cycle_file, 'w', encoding='utf-8') as f:
            json.dump(last_cycle, f)
        
        # Ladowanie wszystkich
        all_state = self.recovery_manager.load_all_state()
        
        self.assertIn('recovery_info', all_state)
        self.assertIn('runtime_state', all_state)
        self.assertIn('last_cycle', all_state)
        
        self.assertEqual(all_state['recovery_info']["session_id"], "SESS_001")
        self.assertEqual(all_state['runtime_state']["mode"], "PRODUCTION")
        self.assertEqual(all_state['last_cycle']["cycle_id"], "CYCLE_005")
    
    def test_get_last_cycle_metadata(self):
        """Test pobierania metadanych ostatniego cyklu."""
        # Utworzenie pliku last_cycle
        last_cycle = {"cycle_id": "CYCLE_999", "status": "complete", "duration": 1.5}
        
        last_cycle_file = self.recovery_manager.base_dir / self.test_config["files"]["last_cycle"]
        with open(last_cycle_file, 'w', encoding='utf-8') as f:
            json.dump(last_cycle, f)
        
        # Pobranie metadanych
        metadata = self.recovery_manager.get_last_cycle_metadata()
        
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata["cycle_id"], "CYCLE_999")
        self.assertEqual(metadata["status"], "complete")
    
    def test_get_last_cycle_metadata_none(self):
        """Test get_last_cycle_metadata gdy nie ma pliku."""
        metadata = self.recovery_manager.get_last_cycle_metadata()
        self.assertIsNone(metadata)
    
    def test_get_recovery_start_data(self):
        """Test pobierania danych startowych dla recovery."""
        # Utworzenie plaków stanu
        recovery_info = {
            "session_id": "PREV_SESSION_001",
            "start_time": "2026-08-03T14:00:00",
            "cycle_count": 15
        }
        
        runtime_state = {
            "mode": "PRODUCTION",
            "pipeline_status": {"current_status": "COMPLETE", "total_cycles": 15}
        }
        
        # Zapis
        recovery_file = self.recovery_manager.base_dir / self.test_config["files"]["recovery_info"]
        with open(recovery_file, 'w', encoding='utf-8') as f:
            json.dump(recovery_info, f)
        
        runtime_file = self.recovery_manager.base_dir / self.test_config["files"]["runtime_state"]
        with open(runtime_file, 'w', encoding='utf-8') as f:
            json.dump(runtime_state, f)
        
        # Pobranie danych startowych
        start_data = self.recovery_manager.get_recovery_start_data()
        
        self.assertTrue(start_data["recovery_mode"])
        self.assertIn("previous_session", start_data)
        self.assertIn("restart_timestamp", start_data)
        self.assertIn("message", start_data)
        self.assertEqual(start_data["previous_session"], "PREV_SESSION_001")
        self.assertIn("Recovery mode", start_data["message"])
    
    def test_save_recovery_info(self):
        """Test zapisywania informacji o recovery."""
        recovery_info = {
            "session_id": "NEW_SESSION_001",
            "start_time": datetime.now().isoformat(),
            "cycle_count": 0,
            "mode": "PRODUCTION",
            "launcher": "start_ssi.py"
        }
        
        # Zapis
        save_result = self.recovery_manager.save_recovery_info(recovery_info)
        self.assertTrue(save_result)
        
        # Sprawdzenie czy plik istnieje
        recovery_file = self.recovery_manager.base_dir / self.test_config["files"]["recovery_info"]
        self.assertTrue(recovery_file.exists())
        
        # Sprawdzenie zawartosci
        with open(recovery_file, 'r', encoding='utf-8') as f:
            saved_info = json.load(f)
        
        self.assertEqual(saved_info["session_id"], "NEW_SESSION_001")
        self.assertEqual(saved_info["cycle_count"], 0)


class TestRecoveryManagerEdgeCases(unittest.TestCase):
    """Testy przypadkow brzegowych RecoveryManager."""
    
    def setUp(self):
        """Inicjalizacja."""
        self.temp_dir = tempfile.mkdtemp(prefix="ssi_recovery_edge_test_")
        self.test_config = {
            **CONFIG_PRODUCTION,
            "output_dir": self.temp_dir,
            "files": CONFIG_PRODUCTION["files"]
        }
    
    def tearDown(self):
        """Czyszczenie."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_corrupted_json_file(self):
        """Test obslugi zepsutego pliku JSON."""
        # Utworzenie zepsutego pliku JSON
        recovery_file = Path(self.temp_dir) / "recovery_info.json"
        with open(recovery_file, 'w', encoding='utf-8') as f:
            f.write("{ invalid json }")
        
        recovery_manager = RecoveryManager(
            base_dir=self.temp_dir,
            config=self.test_config
        )
        
        # Powinien zwrocic pusty slownik
        loaded_info = recovery_manager.load_recovery_info()
        self.assertEqual(loaded_info, {})
    
    def test_empty_json_file(self):
        """Test obslugi pustego pliku JSON."""
        # Utworzenie pustego pliku
        recovery_file = Path(self.temp_dir) / "recovery_info.json"
        with open(recovery_file, 'w', encoding='utf-8') as f:
            f.write("")
        
        recovery_manager = RecoveryManager(
            base_dir=self.temp_dir,
            config=self.test_config
        )
        
        # Powinien zwrocic pusty slownik
        loaded_info = recovery_manager.load_recovery_info()
        self.assertEqual(loaded_info, {})
    
    def test_nested_directory_creation(self):
        """Test tworzenia zagniezdzonych katalogow."""
        nested_dir = Path(self.temp_dir) / "nested" / "deep" / "path"
        
        recovery_manager = RecoveryManager(
            base_dir=nested_dir,
            config=self.test_config
        )
        
        # Katalog powinien byc utworzony
        self.assertTrue(nested_dir.exists())
        self.assertTrue(nested_dir.is_dir())


if __name__ == "__main__":
    unittest.main()
