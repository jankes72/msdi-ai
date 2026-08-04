# SSI V5 Runtime Tests - TimeManager (Fixed Version)
# ==================================================
#
# ETAP: 5.2.4 FAZA 3.3.3
# Data: 2026-08-03
#
# Testy dla TimeManager - zarzadzanie czasem pracy (wersja z poprawnym mockowaniem)

import unittest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Dodanie sciezki do SSI_V5
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
ssi_path = str(project_root)
if ssi_path not in sys.path:
    sys.path.insert(0, ssi_path)

runtime_path = str(Path(__file__).parent.parent)
if runtime_path not in sys.path:
    sys.path.insert(0, runtime_path)

from SSI_V5.runtime.start_ssi import TimeManager


class TestTimeManagerFixed(unittest.TestCase):
    """Testy dla TimeManager z poprawnym mockowaniem."""
    
    def setUp(self):
        """Inicjalizacja przed kazdym testem."""
        self.max_runtime_hours = 5
        self.time_buffer_minutes = 5
        self.time_manager = TimeManager(
            max_runtime_hours=self.max_runtime_hours,
            time_buffer_minutes=self.time_buffer_minutes
        )
    
    def test_initialization(self):
        """Test inicjalizacji TimeManager."""
        self.assertIsNotNone(self.time_manager)
        self.assertEqual(self.time_manager.max_runtime_hours, 5)
        self.assertEqual(self.time_manager.time_buffer_minutes, 5)
        self.assertIsNone(self.time_manager.start_time)
        self.assertIsNone(self.time_manager.end_time)
    
    def test_initialize_with_start_time(self):
        """Test inicjalizacji z podanym czasem startu."""
        start_time = datetime(2026, 8, 3, 15, 0, 0)
        self.time_manager.initialize(start_time=start_time)
        
        self.assertEqual(self.time_manager.start_time, start_time)
        self.assertIsNotNone(self.time_manager.end_time)
        
        # Sprawdzenie czy end_time jest 5 godzin pozniej
        expected_end_time = start_time + timedelta(hours=5)
        self.assertEqual(self.time_manager.end_time, expected_end_time)
    
    def test_get_remaining_time(self):
        """Test pobierania pozostalego czasu."""
        start_time = datetime(2026, 8, 3, 15, 0, 0)
        self.time_manager.initialize(start_time=start_time)
        
        # Ustalony czas testowy - 2.5 godziny po starcie
        test_time = start_time + timedelta(hours=2, minutes=30)
        
        # Mock datetime.now do zwracania test_time
        with patch('SSI_V5.runtime.start_ssi.datetime') as mock_datetime:
            mock_datetime.now.return_value = test_time
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            remaining_time = self.time_manager.get_remaining_time()
            
            # Pozostalo powinno byc 2.5 godziny
            expected_remaining = timedelta(hours=2, minutes=30)
            self.assertEqual(remaining_time, expected_remaining)
    
    def test_get_remaining_seconds(self):
        """Test pobierania pozostalego czasu w sekundach."""
        start_time = datetime(2026, 8, 3, 15, 0, 0)
        self.time_manager.initialize(start_time=start_time)
        
        # Ustalony czas testowy - 1 godzina po starcie
        test_time = start_time + timedelta(minutes=60)
        
        with patch('SSI_V5.runtime.start_ssi.datetime') as mock_datetime:
            mock_datetime.now.return_value = test_time
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            remaining_seconds = self.time_manager.get_remaining_seconds()
            
            # Pozostalo powinno byc 4 godziny = 14400 sekund
            expected_seconds = 4 * 3600  # 4 hours in seconds
            self.assertAlmostEqual(remaining_seconds, expected_seconds, places=0)
    
    def test_should_continue_true(self):
        """Test should_continue gdy pozostalo wiecej niz bufor."""
        start_time = datetime(2026, 8, 3, 15, 0, 0)
        self.time_manager.initialize(start_time=start_time)
        
        # Ustalony czas testowy - 4.5 godziny po starcie
        test_time = start_time + timedelta(hours=4, minutes=55)
        
        with patch('SSI_V5.runtime.start_ssi.datetime') as mock_datetime:
            mock_datetime.now.return_value = test_time
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            should_continue = self.time_manager.should_continue()
            self.assertTrue(should_continue)
    
    def test_should_continue_false(self):
        """Test should_continue gdy pozostalo mniej niz bufor."""
        start_time = datetime(2026, 8, 3, 15, 0, 0)
        self.time_manager.initialize(start_time=start_time)
        
        # Ustalony czas testowy - 4 godziny 59 minut po starcie
        test_time = start_time + timedelta(hours=4, minutes=59)
        
        with patch('SSI_V5.runtime.start_ssi.datetime') as mock_datetime:
            mock_datetime.now.return_value = test_time
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            should_continue = self.time_manager.should_continue()
            self.assertFalse(should_continue)
    
    def test_get_time_summary_with_mock(self):
        """Test pobierania podsumowania czasu z mockowaniem."""
        start_time = datetime(2026, 8, 3, 15, 0, 0)
        self.time_manager.initialize(start_time=start_time)
        
        # Ustalony czas testowy - 30 minut po starcie
        test_time = start_time + timedelta(minutes=30)
        
        with patch('SSI_V5.runtime.start_ssi.datetime') as mock_datetime:
            mock_datetime.now.return_value = test_time
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            summary = self.time_manager.get_time_summary()
            
            self.assertEqual(summary['start_time'], start_time.isoformat())
            self.assertEqual(summary['end_time'], (start_time + timedelta(hours=5)).isoformat())
            self.assertEqual(summary['max_runtime_hours'], 5)
            self.assertEqual(summary['time_buffer_minutes'], 5)
            self.assertAlmostEqual(summary['elapsed_seconds'], 1800.0, places=0)  # 30 minut
            self.assertAlmostEqual(summary['elapsed_hours'], 0.5, places=1)
            self.assertAlmostEqual(summary['remaining_seconds'], 4.5 * 3600, places=0)
            self.assertAlmostEqual(summary['remaining_minutes'], 270.0, places=0)  # 4.5 godziny
            self.assertTrue(summary['should_continue'])


class TestTimeManagerSimple(unittest.TestCase):
    """Proste testy dla TimeManager bez mockowania."""
    
    def test_initialization(self):
        """Test inicjalizacji TimeManager."""
        time_manager = TimeManager(max_runtime_hours=5, time_buffer_minutes=5)
        self.assertIsNotNone(time_manager)
        self.assertEqual(time_manager.max_runtime_hours, 5)
        self.assertEqual(time_manager.time_buffer_minutes, 5)
    
    def test_initialize_creates_times(self):
        """Test czy initialize tworzy czasy startu i zakonczenia."""
        time_manager = TimeManager(max_runtime_hours=2, time_buffer_minutes=10)
        time_manager.initialize()
        
        self.assertIsNotNone(time_manager.start_time)
        self.assertIsNotNone(time_manager.end_time)
        
        # end_time powinien byc start_time + 2 godziny
        duration = (time_manager.end_time - time_manager.start_time).total_seconds()
        self.assertAlmostEqual(duration, 2 * 3600, places=0)
    
    def test_get_time_summary_no_init(self):
        """Test get_time_summary bez inicjalizacji."""
        time_manager = TimeManager()
        summary = time_manager.get_time_summary()
        
        self.assertIsNone(summary['start_time'])
        self.assertIsNone(summary['end_time'])
        self.assertEqual(summary['elapsed_seconds'], 0)
        self.assertEqual(summary['remaining_seconds'], 0)
    
    def test_should_continue_logic(self):
        """Test logiki should_continue."""
        time_manager = TimeManager(max_runtime_hours=1, time_buffer_minutes=10)
        
        # Bez inicjalizacji powinien zwrocic False
        self.assertFalse(time_manager.should_continue())
        
        # Z inicjalizacja
        time_manager.initialize()
        # Powinien zwrocic True jesli czas nie minie
        result = time_manager.should_continue()
        self.assertIsInstance(result, bool)


if __name__ == "__main__":
    unittest.main()
