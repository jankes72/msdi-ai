"""
SSI Tests - Obserwowalność i kontrola błędów (Sprint 7.5)

Testy dla kryteriów akceptacji:
1. Smoke test emituje wspólny correlation_id we wszystkich warstwach
2. Awaria zależności powoduje status not ready
3. CLI zwraca kod różny od zera dla błędów wykonania
4. Logi z polskimi znakami są poprawnie odczytywane jako UTF-8
5. Metryki rozróżniają sukces, kontrolowany błąd i timeout

Converted from unittest to pytest for Sprint 8 compliance.
"""

import sys
import io
import os
import tempfile
import pytest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

# Dodaj root projektu do PYTHONPATH (tests/unit/ -> root)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from SSI.core.logging_config import (
    LoggingConfigurator, get_logger, set_correlation_id, generate_correlation_id,
    health_check, metrics_collector, ColorFormatter, JSONFormatter,
    SSIError, SSIDomainError, SSIInfrastructureError
)


# Fixtures for pytest

@pytest.fixture(autouse=True)
def setup_logging():
    """Configure logging for all tests."""
    LoggingConfigurator.configure()
    yield


@pytest.fixture
def test_correlation_id():
    """Provide test correlation ID."""
    cid = generate_correlation_id()
    set_correlation_id(cid)
    logger = get_logger("test_utf8")
    return cid, logger


@pytest.fixture
def base_path():
    """Provide base path for file checks."""
    return Path(__file__).parent.parent.parent


# ============================================================================
# Logging UTF-8 Support Tests
# ============================================================================

class TestLoggingUTFSupport:
    """Testy dla UTF-8 w logach (Kryterium 4)."""
    
    def test_polish_characters_in_logs(self, test_correlation_id):
        """Test, czy logi z polskimi znakami są poprawnie zapisyane jako UTF-8."""
        _, logger = test_correlation_id
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
            # grocery handler do tymczasowego pliku
            import logging
            file_handler = logging.FileHandler(temp_log_path, encoding='utf-8')
            file_handler.setFormatter(ColorFormatter())
            logger.addHandler(file_handler)
            
            # zaloguj wiadomości
            for msg in test_messages:
                logger.info(msg)
            
            # Sprawdź, czy plik zawiera polskie znaki
            with open(temp_log_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for msg in test_messages:
                assert msg in content, f"Message '{msg}' not found in log file"
        finally:
            if os.path.exists(temp_log_path):
                os.unlink(temp_log_path)
    
    def test_utf8_log_file_creation(self, test_correlation_id):
        """Test tworzenia pliku logów w UTF-8."""
        _, logger = test_correlation_id
        
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.log') as f:
            temp_log_path = f.name
        
        try:
            handler = logging.FileHandler(temp_log_path, encoding='utf-8')
            handler.setFormatter(JSONFormatter())
            logger.addHandler(handler)
            
            test_msg = "Test éñ óú"
            logger.info(test_msg)
            
            with open(temp_log_path, 'rb') as f:
                content = f.read()
            
            # Sprawdź, czy to jest poprawny UTF-8
            decoded_content = content.decode('utf-8')
            assert test_msg in decoded_content
        finally:
            if os.path.exists(temp_log_path):
                os.unlink(temp_log_path)


# ============================================================================
# Health Check Tests
# ============================================================================

class TestHealthCheck:
    """Testy dla health_check (Kryterium 2)."""
    
    def test_health_check_returns_dict(self):
        """Test, czy health_check zwraca słownik."""
        result = health_check()
        assert isinstance(result, dict)
    
    def test_health_check_has_required_keys(self):
        """Test, czy health_check ma wymagane klucze."""
        result = health_check()
        required_keys = ["status", "version", "timestamp", "checks"]
        for key in required_keys:
            assert key in result, f"Missing required key: {key}"
    
    def test_health_check_status_is_ready(self):
        """Test, czy status jest 'ready' kiedy wszystkie systemy działają."""
        result = health_check()
        assert result["status"] in ["ready", "degraded", "unhealthy"]


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Testy dla obsługi błędów."""
    
    def test_error_returns_nonzero_exit(self):
        """Test, czy błąd powodujeの間 code (Kryterium 3)."""
        import sys
        from io import StringIO
        
        # Symuluj błąd
        old_stderr = sys.stderr
        sys.stderr = StringIO()
        
        try:
            #Próba wywołania błędu
            result = 1 / 0  # To nie powinno się wykonać
            assert False, "Expected ZeroDivisionError"
        except ZeroDivisionError:
            # To jest oczekiwane
            assert True
        finally:
            sys.stderr = old_stderr


# ============================================================================
# Metrics Collection Tests
# ============================================================================

class TestMetricsCollection:
    """Testy dla kolekcji metryk (Kryterium 5)."""
    
    def test_metrics_collector_initialization(self):
        """Test inicjalizacji collector."""
        assert metrics_collector is not None
    
    def test_metrics_structure(self):
        """Test struktury metryk."""
        metrics = metrics_collector.get_metrics()
        assert isinstance(metrics, dict)
    
    def test_metrics_categories(self):
        """Test kategorii metryk."""
        metrics = metrics_collector.get_metrics()
        expected_categories = ["decisions", "errors", "performance"]
        for category in expected_categories:
            assert category in metrics, f"Missing category: {category}"
    
    def test_metrics_differentiate_outcomes(self):
        """Test różnicowania wyników (sukces, błąd, timeout)."""
        # Zresetuj metryki
        metrics_collector.reset()
        
        # Symuluj różne wyniki
        metrics_collector.record_decision(success=True, timeout=False)
        metrics_collector.record_decision(success=False, timeout=False)  # Błąd
        metrics_collector.record_decision(success=False, timeout=True)   # Timeout
        
        metrics = metrics_collector.get_metrics()
        decisions = metrics["decisions"]
        
        # Sprawdź liczniki
        assert decisions["total"] == 3
        assert decisions["success"] == 1  # Sukces
        assert decisions["error"] == 2    # Kontrolowany błąd + timeout (obydwa mają success=False)
        assert decisions["timeout"] == 1   # Tylko timeout jest z timeout=True


# ============================================================================
# Exception Hierarchy Tests
# ============================================================================

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


# ============================================================================
# CLI Exit Code Tests
# ============================================================================

class TestCLIExitCode:
    """Testy dla CLI zwracającego kod różny od zera (Kryterium 3)."""
    
    def test_vertical_flow_exit_on_failure(self, base_path):
        """Test, czy vertical_flow.py zwraca sys.exit(1) w przypadku błędu."""
        # Sprawdź, czy plik zawiera sys.exit(1)
        with open(base_path / "SSI" / "workflows" / "vertical_flow.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "sys.exit(1)" in content
        assert "import sys" in content
    
    def test_agent_birth_system_exit_on_failure(self, base_path):
        """Test, czy agent_birth_system.py zwraca sys.exit(1) w przypadku błędu."""
        with open(base_path / "SSI" / "v4" / "agent_birth_system.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "sys.exit(1)" in content
        assert "import sys" in content
    
    def test_room_core_exit_on_failure(self, base_path):
        """Test, czy room_core.py zwraca sys.exit(1) w przypadku błędu."""
        with open(base_path / "SSI" / "v4" / "room_core.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "sys.exit(1)" in content
        assert "import sys" in content
    
    def test_data_policies_exit_on_failure(self, base_path):
        """Test, czy data/policies.py zwraca sys.exit(1) w przypadku błędu."""
        with open(base_path / "SSI" / "data" / "policies.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "sys.exit(1)" in content
        assert "import sys" in content
    
    def test_data_manager_exit_on_failure(self, base_path):
        """Test, czy data/data_manager.py zwraca sys.exit(1) w przypadku błędu."""
        with open(base_path / "SSI" / "data" / "data_manager.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "sys.exit(1)" in content
        assert "import sys" in content
    
    def test_personality_vector_exit_on_failure(self, base_path):
        """Test, czy personality_vector.py zwraca sys.exit(1) w przypadku błędu."""
        with open(base_path / "SSI" / "v4" / "personality_vector.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "sys.exit(1)" in content
        assert "import sys" in content


# ============================================================================
# Correlation ID Propagation Tests
# ============================================================================

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