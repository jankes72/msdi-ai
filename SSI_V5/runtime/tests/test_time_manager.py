# SSI V5 Runtime Tests - TimeManager
# ==================================================
#
# ETAP: 5.2.4 FAZA 3.3.3
# Data: 2026-08-03
#
# Testy dla TimeManager - zarzadzanie czasem pracy

import unittest
import time
from datetime import datetime, timedelta

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


class TestTimeManager(unittest.TestCase):
    """Testy dla TimeManager - zarzadzanie czasem pracy."""
    
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
    
    def test_initialize_with_default_time(self):
        """Test inicjalizacji z domyslny erwartem startu (now)."""
        before_init = datetime.now()
        self.time_manager.initialize()
        after_init = datetime.now()
        
        self.assertIsNotNone(self.time_manager.start_time)
        self.assertTrue(before_init <= self.time_manager.start_time <= after_init)
        self.assertIsNotNone(self.time_manager.end_time)
    
    def test_get_remaining_time(self):
        """Test pobierania pozostalego czasu."""
        start_time = datetime(2026, 8, 3, 15, 0, 0)
        self.time_manager.initialize(start_time=start_time)
        
        # Ustalony czas testowy
        test_time = start_time + timedelta(hours=2, minutes=30)
        
        # mock datetime.now
        import unittest.mock
        with unittest.mock.patch('datetime.datetime') as mock_datetime:
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
        
        # Ustalony czas testowy
        test_time = start_time + timedelta(minutes=60)  # 1 godzina pozniej
        
        import unittest.mock
        with unittest.mock.patch('datetime.datetime') as mock_datetime:
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
        # bufor to 5 minut, wiec powinno zwrocic True
        test_time = start_time + timedelta(hours=4, minutes=55)
        
        import unittest.mock
        with unittest.mock.patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = test_time
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            should_continue = self.time_manager.should_continue()
            self.assertTrue(should_continue)
    
    def test_should_continue_false(self):
        """Test should_continue gdy pozostalo mniej niz bufor."""
        start_time = datetime(2026, 8, 3, 15, 0, 0)
        self.time_manager.initialize(start_time=start_time)
        
        # Ustalony czas testowy - 4 godziny 59 minut po starcie
        # bufor to 5 minut, wiec powinno zwrocic False
        test_time = start_time + timedelta(hours=4, minutes=59)
        
        import unittest.mock
        with unittest.mock.patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = test_time
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            should_continue = self.time_manager.should_continue()
            self.assertFalse(should_continue)
    
    def test_should_continue_at_exact_buffer(self):
        """Test should_continue na granicy bufora."""
        start_time = datetime(2026, 8, 3, 15, 0, 0)
        self.time_manager.initialize(start_time=start_time)
        
        # Ustalony czas testowy - 4 godziny 55 minut po starcie
        # bufor to 5 minut, wiec powinno zwrocic False (> buffer, nie >=)
        test_time = start_time + timedelta(hours=4, minutes=55)
        
        import unittest.mock
        with unittest.mock.patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = test_time
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # buffer_seconds = 5 * 60 = 300
            # remaining_seconds = 5 * 60 = 300
            # 300 > 300 = False
            should_continue = self.time_manager.should_continue()
            self.assertFalse(should_continue)
    
    def test_get_time_summary(self):
        """Test pobierania podsumowania czasu."""
        start_time = datetime(2026, 8, 3, 15, 0, 0)
        self.time_manager.initialize(start_time=start_time)
        
        # Ustalony czas testowy
        test_time = start_time + timedelta(minutes=30)
        
        import unittest.mock
        with unittest.mock.patch('datetime.datetime') as mock_datetime:
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
    
    def test_get_time_summary_no_init(self):
        """Test get_time_summary bez inicjalizacji."""
        # Bez inicjalizacji
        summary = self.time_manager.get_time_summary()
        
        self.assertIsNone(summary['start_time'])
        self.assertIsNone(summary['end_time'])
        self.assertEqual(summary['elapsed_seconds'], 0)
        self.assertEqual(summary['remaining_seconds'], 0)


class TestTimeManagerEdgeCases(unittest.TestCase):
    """Testy przypadkow brzegowych TimeManager."""
    
    def test_zero_time_buffer(self):
        """Test z zero buffer time."""
        time_manager = TimeManager(
            max_runtime_hours=1,
            time_buffer_minutes=0
        )
        
        start_time = datetime(2026, 8, 3, 15, 0, 0)
        time_manager.initialize(start_time=start_time)
        
        # Jesli remaining > 0, powinno zwrocic True
        test_time = start_time + timedelta(minutes=30)
        
        import unittest.mock
        with unittest.mock.patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = test_time
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            should_continue = time_manager.should_continue()
            self.assertTrue(should_continue)
    
    def test_end_time_passed(self):
        """Test gdy end_time juz minie."""
        time_manager = TimeManager(
            max_runtime_hours=1,
            time_buffer_minutes=5
        )
        
        start_time = datetime(2026, 8, 3, 15, 0, 0)
        time_manager.initialize(start_time=start_time)
        
        # Czas po end_time
        test_time = start_time + timedelta(hours=2)
        
        import unittest.mock
        with unittest.mock.patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = test_time
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            remaining_time = time_manager.get_remaining_time()
            self.assertEqual(remaining_time, timedelta(0))
            
            remaining_seconds = time_manager.get_remaining_seconds()
            self.assertEqual(remaining_seconds, 0)
            
            should_continue = time_manager.should_continue()
            self.assertFalse(should_continue)
    
    def test_very_short_runtime(self):
        """Test z bardzo krotkim czasem pracy."""
        time_manager = TimeManager(
            max_runtime_hours=0.1,  # 6 minut
            time_buffer_minutes=1
        )
        
        start_time = datetime(2026, 8, 3, 15, 0, 0)
        time_manager.initialize(start_time=start_time)
        
        # 5 minut po starcie - powinno zwrocic False (bufor 1 minuta)
        test_time = start_time + timedelta(minutes=5)
        
        import unittest.mock
        with unittest.mock.patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = test_time
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            should_continue = time_manager.should_continue()
            self.assertFalse(should_continue)


if __name__ == "__main__":
    unittest.main()
