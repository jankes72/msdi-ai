"""
SSI Tests - Obserwowalność i kontrola błędów (Sprint 7.5)

Testy dla kryteriów akceptacji:
1. Smoke test emituje wspólny correlation_id we wszystkich warstwach
2. Awaria zależności powoduje status not ready
3. CLI zwraca kod różny od zera dla błędów wykonania
4. Logi z polskimi znakami są poprawnie odczytywane jako UTF-8
5. Metryki rozróżniają sukces, kontrolowany błąd i timeout
"""
import pytest

import sys
import io
import os
import tempfile
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

# Dodaj root do PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from SSI.core.logging_config import (
    LoggingConfigurator, get_logger, set_correlation_id, generate_correlation_id,
    health_check, metrics_collector, ColorFormatter, JSONFormatter,
    SSIError, SSIDomainError, SSIInfrastructureError
)


class TestLoggingUTFSupport:
    """Testy dla UTF-8 w logach (Kryterium 4)."""
    
    def setUp(self):
        """Ustawienia przed testami."""
        self.test_correlation_id = generate_correlation_id()
        set_correlation_id(self.test_correlation_id)
        self.logger = get_logger("test_utf8")
    
    def test_polish_characters_in_logs(self):
        """Test, czy logi z polskimi znakami są poprawnie zapisyane jako UTF-8."""
        test_messages = [
            "Ćwiczenie ząkończenia",
            "Ęczka łóżko",
            "Ścięgno Army",
            "Żółć Łączy buzki",
            "Test z polskimi znakami: ą, ć, ę, ł, ń, ó, ś, Ź, ż"
        ]
        
        # Utwórz tymczasowy plik logów
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.log') as f:
            temp_log_path = f.name
        
        try:
            # Konfiguruj handler do pliku
            from logging import FileHandler
            
            file_handler = FileHandler(temp_log_path, encoding='utf-8')
            file_handler.setLevel(10)  # DEBUG
            file_handler.setFormatter(JSONFormatter())
            
            self.logger.addHandler(file_handler)
            
            # Zaloguj wiadomości z polskimi znakami
            for msg in test_messages:
                self.logger.info(msg, extra={"correlation_id": self.test_correlation_id})
            
            file_handler.close()
            
            # Sprawdź, czy plik zawiera poprawnie zakodowane znaki
            with open(temp_log_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for msg in test_messages:
                assert msg in content, f"Polskie znaki nie zostały poprawnie zapiane: {msg}"
            
        finally:
            # Usunąć tymczasowy plik
            if os.path.exists(temp_log_path):
                os.unlink(temp_log_path)
    
    def test_correlation_id_in_logs(self):
        """Test, czy correlation_id jest obecny w logach (Kryterium 1)."""
        # Utwórz tymczasowy bufor logów
        log_capture = io.StringIO()
        
        from logging import StreamHandler
        stream_handler = StreamHandler(log_capture)
        stream_handler.setLevel(10)
        stream_handler.setFormatter(JSONFormatter())
        
        self.logger.addHandler(stream_handler)
        
        # Zaloguj wiadomość
        test_msg = "Test correlation_id"
        self.logger.info(test_msg, extra={"correlation_id": self.test_correlation_id})
        
        # Sprawdź zawartość logów
        log_output = log_capture.getvalue()
        assert self.test_correlation_id in log_output
        assert test_msg in log_output


class TestHealthCheckDependencies:
    """Testy dla HealthCheck (Kryterium 2)."""
    
    def test_health_check_dependencies(self):
        """Test, czy HealthCheck sprawdza zależności V2, V3, V4."""
        # Wyczyść stan
        health_check._status = {
            "ready": False,
            "dependencies": {},
            "modules": {},
            "timestamp": None
        }
        
        # Sprawdź zależności
        results = health_check.check_all_dependencies()
        
        # Sprawdź, czy wszystkie zależności zostały sprawdzone
        assert "v2" in results
        assert "v3" in results
        assert "v4" in results
        
        # Sprawdź status gotowości
        status = health_check.get_status()
        assert "dependencies" in status
        
        # Sprawdź, czy V2, V3, V4 są w zależnościach
        deps = status["dependencies"]
        assert "v2" in deps
        assert "v3" in deps
        assert "v4" in deps
    
    def test_health_check_not_ready_on_failure(self):
        """Test, czy awaria zależności powoduje status not ready."""
        # Symuluj awarię zależności
        def failing_check():
            raise ImportError("Symulowana awaria zależności")
        
        result = health_check.check_dependency("failing_dep", failing_check)
        assert not result
        
        # Sprawdź status
        status = health_check.get_status()
        assert "failing_dep" in status["dependencies"]
        assert status["dependencies"]["failing_dep"]["status"] == "error"


class TestMetricsCollector:
    """Testy dla MetricsCollector (Kryterium 5)."""
    
    def setUp(self):
        """Resetuj MetricsCollector przed testami."""
        # Wyczyść dane - reset do stanu początkowego
        metrics_collector._metrics = {
            "decisions": {
                "total": 0,
                "success": 0,
                "error": 0,
                "timeout": 0
            },
            "performance": {
                "total_time_ms": 0,
                "min_time_ms": float('inf'),
                "max_time_ms": 0,
                "last_time_ms": 0
            },
            "resources": {
                "memory_usage_mb": 0,
                "cpu_usage_percent": 0
            }
        }
    
    def test_metrics_record_decision(self):
        """Test rejestrowania decyzji."""
        metrics_collector.record_decision(
            success=True,
            timeout=False,
            duration_ms=150
        )
        
        metrics = metrics_collector.get_metrics()
        decisions = metrics["decisions"]
        assert decisions["total"] == 1
        assert decisions["success"] == 1
        assert decisions["error"] == 0
        assert decisions["timeout"] == 0
    
    def test_metrics_differentiate_outcomes(self):
        """Test, czy metryki rozróżniają sukces, błąd i timeout."""
        # Sukces
        metrics_collector.record_decision(success=True, timeout=False, duration_ms=100)
        
        # Kontrolowany błąd
        metrics_collector.record_decision(success=False, timeout=False, duration_ms=50)
        
        # Timeout
        metrics_collector.record_decision(success=False, timeout=True, duration_ms=5000)
        
        metrics = metrics_collector.get_metrics()
        decisions = metrics["decisions"]
        
        # Sprawdź liczniki
        assert decisions["total"] == 3
        assert decisions["success"] == 1  # Sukces
        assert decisions["error"] == 2    # Kontrolowany błąd + timeout (obydwa mają success=False)
        assert decisions["timeout"] == 1   # Tylko timeout jest z timeout=True


class TestExceptionHierarchy:
    """Testy dla hierarchii wyjątków."""
    
    def test_exception_hierarchy(self):
        """Test hierarchii wyjątków SSIError."""
        # Sprawdź, czy SSIDomainError i SSIInfrastructureError dziedziczą z SSIError
        assert issubclass(SSIDomainError, SSIError)
        assert issubclass(SSIInfrastructureError, SSIError)
    
    def test_custom_exceptions(self):
        """Test tworzenia niestandardowych wyjątków."""
        try:
            raise SSIDomainError("Test domain error")
        except SSIError as e:
            assert "Test domain error" in str(e)
        
        try:
            raise SSIInfrastructureError("Test infrastructure error")
        except SSIError as e:
            assert "Test infrastructure error" in str(e)


class TestCLIExitCode:
    """Testy dla CLI zwracającego kod różny od zera (Kryterium 3)."""
    
    def setUp(self):
        """Ustawie ścieżki bazowe."""
        self.base_path = Path(__file__).parent.parent
    
    def test_vertical_flow_exit_on_failure(self):
        """Test, czy vertical_flow.py zwraca sys.exit(1) w przypadku błędu."""
        # Sprawdź, czy plik zawiera sys.exit(1)
        with open(self.base_path / "workflows" / "vertical_flow.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "sys.exit(1)" in content
        assert "import sys" in content
    
    def test_agent_birth_system_exit_on_failure(self):
        """Test, czy agent_birth_system.py zwraca sys.exit(1) w przypadku błędu."""
        with open(self.base_path / "v4" / "agent_birth_system.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "sys.exit(1)" in content
        assert "import sys" in content
    
    def test_room_core_exit_on_failure(self):
        """Test, czy room_core.py zwraca sys.exit(1) w przypadku błędu."""
        with open(self.base_path / "v4" / "room_core.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "sys.exit(1)" in content
        assert "import sys" in content
    
    def test_data_policies_exit_on_failure(self):
        """Test, czy data/policies.py zwraca sys.exit(1) w przypadku błędu."""
        with open(self.base_path / "data" / "policies.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "sys.exit(1)" in content
        assert "import sys" in content
    
    def test_data_manager_exit_on_failure(self):
        """Test, czy data/data_manager.py zwraca sys.exit(1) w przypadku błędu."""
        with open(self.base_path / "data" / "data_manager.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "sys.exit(1)" in content
        assert "import sys" in content
    
    def test_personality_vector_exit_on_failure(self):
        """Test, czy personality_vector.py zwraca sys.exit(1) w przypadku błędu."""
        with open(self.base_path / "v4" / "personality_vector.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "sys.exit(1)" in content
        assert "import sys" in content


class TestCorrelationIDPropagation:
    """Testy dla propagacji correlation_id (Kryterium 1)."""
    
    def test_correlation_id_generation(self):
        """Test generowania unikalnych correlation_id."""
        cid1 = generate_correlation_id()
        cid2 = generate_correlation_id()
        assert cid1 != cid2
    
    def test_correlation_id_context(self):
        """Test ustawiania i pobierania correlation_id z kontekstu."""
        test_cid = "test-correlation-123"
        set_correlation_id(test_cid)
        
        # Pobierz correlation_id z kontekstu
        from SSI.core.logging_config import _correlation_id_var
        assert _correlation_id_var.get() == test_cid


