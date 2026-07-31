"""
SSI Pytest Configuration - conftest.py

Globalna konfiguracja dla wszystkich testów:
- Fixtures (Setup/Teardown)
- Hooks (Przed/po testach)
- Konfiguracja logowania
- Handle pytest options

Zgodnie z PROJECT_RULES.md:
- Testy muszą być deterministyczne
- Testy muszą być niezależne od sieci i danych produkcyjnych
- Brak testów nie może być raportowany jako sukces
"""

import sys
import os
from pathlib import Path
import logging

# Dodaj root projektu do PYTHONPATH (dla importów SSI)
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Wyłącz logowanie do konsoli podczas testów (opcjonalnie)
logging.disable(logging.CRITICAL)


# =============================================================================
# Pytest Hooks
# =============================================================================

def pytest_configure(config):
    """Konfiguracja pytest przed uruchomieniem testów."""
    # Ustaw zmienną środowiskową dla testów
    os.environ["SSI_TESTING"] = "1"
    os.environ["PYTHONPATH"] = str(PROJECT_ROOT)


def pytest_collection_modifyitems(items, config):
    """
    Modyfikacja kolekcji testów.
    
    Można tutaj:
    - Pomijać powolne testy (jeśli --skip-slow)
    - Dodawać markery
    - Filtrować testy
    """
    pass


# =============================================================================
# Fixtures (Setup/Teardown)
# =============================================================================

import pytest


@pytest.fixture(autouse=True)
def setup_test_environment():
    """
    Fixture uruchamiana automatycznie przed każdym testem.
    Ustawia środowisko testowe.
    """
    # Ustaw zmienną środowiskową dla testów
    os.environ["SSI_TEST_MODE"] = "1"
    yield
    # Czyść po teście (opcjonalnie)
    del os.environ["SSI_TEST_MODE"]


@pytest.fixture
def ssi_root_path():
    """Zwraca ścieżkę do root projektu SSI."""
    return PROJECT_ROOT


@pytest.fixture
def ssi_data_dir():
    """Zwraca ścieżkę do folderu z danymi testowymi."""
    data_dir = PROJECT_ROOT / "test_data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


@pytest.fixture
def mock_correlation_id():
    """Ustawia mock correlation_id dla testów."""
    from SSI.core.logging_config import set_correlation_id
    test_cid = "test-correlation-123"
    set_correlation_id(test_cid)
    yield test_cid


@pytest.fixture
def reset_health_check():
    """Resetuje HealthCheck przed testami."""
    from SSI.core.logging_config import health_check
    original_status = health_check.get_status().copy()
    health_check._status = {
        "ready": False,
        "dependencies": {},
        "modules": {},
        "timestamp": None
    }
    yield
    # Przywróć oryginalny status (opcjonalnie)
    health_check._status = original_status


@pytest.fixture
def reset_metrics():
    """Resetuje MetricsCollector przed testami."""
    from SSI.core.logging_config import metrics_collector
    original_metrics = metrics_collector.get_metrics().copy()
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
    yield
    # Przywróć oryginalne metryki (opcjonalnie)
    metrics_collector._metrics = original_metrics


# =============================================================================
# Markery pytest
# =============================================================================

# Rejestracja nowych markerów (jeśli potrzebne)
pytest.register_assert_rewrite("SSI.tests.helpers")

# Markery dla testów
pytest.mark.slow = pytest.mark.mark("slow", help="Astempowuje powolne testy")
pytest.mark.smoke = pytest.mark.mark("smoke", help="Testy smoke")
pytest.mark.integration = pytest.mark.mark("integration", help="Testy integracyjne")
pytest.mark.unit = pytest.mark.mark("unit", help="Testy jednostkowe")
pytest.mark.contracts = pytest.mark.mark("contracts", help="Testy kontraktów")
pytest.mark.cli = pytest.mark.mark("cli", help="Testy CLI")
