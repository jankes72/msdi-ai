# SSI V5 Runtime Tests - FileManager
# ==================================================
#
# ETAP: 5.2.4 FAZA 3.3.3
# Data: 2026-08-03
#
# Testy dla FileManager - zarzadzanie plikami stanu

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

from SSI_V5.runtime.start_ssi_test import FileManager, CONFIG_TEST


class TestFileManager(unittest.TestCase):
    """Testy dla FileManager - zarzadzanie plikami stanu."""
    
    def setUp(self):
        """Inicjalizacja przed kazdym testem."""
        # Tworzenie tymczasowego katalogu
        self.temp_dir = tempfile.mkdtemp(prefix="ssi_test_")
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
        self.file_manager = FileManager(
            base_dir=self.temp_dir,
            config=self.test_config
        )
    
    def tearDown(self):
        """Czyszczenie po kazdym teście."""
        # Usuniecie tymczasowego katalogu
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test inicjalizacji FileManager."""
        self.assertIsNotNone(self.file_manager)
        self.assertIsInstance(self.file_manager.base_dir, Path)
        self.assertIsNotNone(self.file_manager.config)
    
    def test_base_dir_creation(self):
        """Test tworzenia bazowego katalogu."""
        self.assertTrue(self.file_manager.base_dir.exists())
        self.assertTrue(self.file_manager.base_dir.is_dir())
    
    def test_get_file_path(self):
        """Test pobierania pelnej sciezki do pliku."""
        file_path = self.file_manager.get_file_path("test.json")
        self.assertIsInstance(file_path, Path)
        self.assertIn("test.json", str(file_path))
    
    def test_save_and_load_runtime_state(self):
        """Test zapisywania i odczytywania stanu runtime."""
        # Testowe dane
        runtime_state = {
            "mode": "TEST",
            "start_time": datetime.now().isoformat(),
            "end_time": datetime.now().isoformat(),
            "pipeline_status": {"current_status": "IDLE"},
            "system_info": {"test": True}
        }
        
        # Zapis
        save_result = self.file_manager.save_runtime_state(runtime_state)
        self.assertTrue(save_result)
        
        # Sprawdzenie czy plik istnieje
        runtime_file = self.file_manager.base_dir / self.test_config["files"]["runtime_state"]
        self.assertTrue(runtime_file.exists())
        
        # Odczyt
        loaded_state = self.file_manager.load_runtime_state()
        self.assertIsNotNone(loaded_state)
        self.assertEqual(loaded_state["mode"], "TEST")
        self.assertEqual(loaded_state["system_info"]["test"], True)
    
    def test_save_and_load_last_cycle(self):
        """Test zapisywania i odczytywania ostatniego cyklu."""
        # Testowe dane
        last_cycle = {
            "cycle_id": "TEST_CYCLE_001",
            "start_time": datetime.now().isoformat(),
            "end_time": datetime.now().isoformat(),
            "status": "COMPLETE",
            "duration": 1.5
        }
        
        # Zapis
        save_result = self.file_manager.save_last_cycle(last_cycle)
        self.assertTrue(save_result)
        
        # Odczyt
        loaded_cycle = self.file_manager.load_last_cycle()
        self.assertIsNotNone(loaded_cycle)
        self.assertEqual(loaded_cycle["cycle_id"], "TEST_CYCLE_001")
        self.assertEqual(loaded_cycle["status"], "COMPLETE")
    
    def test_save_and_load_cycle_history(self):
        """Test zapisywania i odczytywania historii cykli."""
        # Testowe dane
        history = [
            {"cycle_id": "CYCLE_001", "status": "success"},
            {"cycle_id": "CYCLE_002", "status": "success"},
            {"cycle_id": "CYCLE_003", "status": "error"}
        ]
        
        # Zapis
        save_result = self.file_manager.save_cycle_history(history)
        self.assertTrue(save_result)
        
        # Odczyt
        loaded_history = []
        loaded_file = self.file_manager.base_dir / self.test_config["files"]["cycle_history"]
        if loaded_file.exists():
            with open(loaded_file, 'r', encoding='utf-8') as f:
                loaded_history = json.load(f)
        
        self.assertEqual(len(loaded_history), 3)
        self.assertEqual(loaded_history[0]["cycle_id"], "CYCLE_001")
        self.assertEqual(loaded_history[2]["status"], "error")
    
    def test_save_and_load_event_log(self):
        """Test zapisywania i odczytywania dziennika zdarzen."""
        # Testowe dane
        event_log = [
            {"timestamp": datetime.now().isoformat(), "event_type": "INIT", "data": {}},
            {"timestamp": datetime.now().isoformat(), "event_type": "CYCLE_START", "data": {}},
            {"timestamp": datetime.now().isoformat(), "event_type": "CYCLE_COMPLETE", "data": {}}
        ]
        
        # Zapis
        save_result = self.file_manager.save_event_log(event_log)
        self.assertTrue(save_result)
        
        # Odczyt
        loaded_log = []
        loaded_file = self.file_manager.base_dir / self.test_config["files"]["event_log"]
        if loaded_file.exists():
            with open(loaded_file, 'r', encoding='utf-8') as f:
                loaded_log = json.load(f)
        
        self.assertEqual(len(loaded_log), 3)
        self.assertEqual(loaded_log[0]["event_type"], "INIT")
    
    def test_empty_file_handling(self):
        """Test obslugi pustych plikow."""
        # Sprawdzenie odczytu z nieistniejacych plikow
        empty_manager = FileManager(
            base_dir=self.temp_dir,
            config=self.test_config
        )
        
        # Odczyt nieistniejacego runtime_state
        runtime_state = empty_manager.load_runtime_state()
        self.assertEqual(runtime_state, {})
        
        # Odczyt nieistniejacego last_cycle
        last_cycle = empty_manager.load_last_cycle()
        self.assertEqual(last_cycle, {})
    
    def test_special_characters_in_data(self):
        """Test obslugi specjalnych znakow w JSON."""
        runtime_state = {
            "mode": "TEST",
            "description": "Test z polskimi znakami: ąćęłńóśżź",
            "emoji_test": "Test z emoji: 🎯⚽",
            "timestamp": datetime.now().isoformat()
        }
        
        # Zapis
        save_result = self.file_manager.save_runtime_state(runtime_state)
        self.assertTrue(save_result)
        
        # Odczyt
        loaded_state = self.file_manager.load_runtime_state()
        self.assertEqual(loaded_state["description"], "Test z polskimi znakami: ąćęłńóśżź")
        # Emoji moze byc rozny w zaleznosci od systemu
        self.assertIn("emoji_test", loaded_state)


class TestFileManagerErrorHandling(unittest.TestCase):
    """Testy obslugi bledow w FileManager."""
    
    def setUp(self):
        """Inicjalizacja."""
        self.temp_dir = tempfile.mkdtemp(prefix="ssi_error_test_")
        self.test_config = {
            **CONFIG_TEST,
            "output_dir": self.temp_dir,
            "files": CONFIG_TEST["files"]
        }
    
    def tearDown(self):
        """Czyszczenie."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_permission_error_handling(self):
        """Test obslugi bledow uprawnien."""
        # Tworzenie katalogu bez uprawnien do zapisu
        if os.name == 'nt':  # Windows
            # Na Windows trudno symulowac bledy uprawnien
            # Pomijamy ten test
            self.skipTest("Skipped on Windows")
        else:
            # Na Unix - tworzymy katalog bez uprawnien
            restricted_dir = os.path.join(self.temp_dir, "restricted")
            os.makedirs(restricted_dir, mode=0o000)
            
            file_manager = FileManager(
                base_dir=restricted_dir,
                config=self.test_config
            )
            
            # Próba zapisu powinna sie nie powiesc
            runtime_state = {"test": True}
            save_result = file_manager.save_runtime_state(runtime_state)
            self.assertFalse(save_result)
            
            # Restore permissions for cleanup
            os.chmod(restricted_dir, 0o755)


if __name__ == "__main__":
    unittest.main()
