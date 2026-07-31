"""
SSI Core Logging Configuration - Centralna konfiguracja logowania

Odpowiedzialność:
- Konfiguracja formatu logów (strukturalny, UTF-8)
- Hierarchia loggerów (root, domain, infrastructure)
- Filtrowanie sekretów i wrażliwych danych
- Obsługa correlation_id
- Metryki logowania

Zgodnie z:
- Sprint 7.5: Obserwowalność i kontrola błędów
- Wymagania:
  - Logi muszą być zapisane w UTF-8
  - Logi muszą mieć format strukturalny
  - Log nie może zawierać sekretów ani pełnych danych wejściowych użytkownika

Architektura:
┌─────────────────────────────────────────────────────────────┐
│              SSI LOGGING SYSTEM                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐      ┌─────────────────┐                 │
│  │  LoggingConfig  │      │  CorrelationID  │                 │
│  │  - Format JSON  │      │  - Generator   │                 │
│  │  - UTF-8        │      │  - Contextvar  │                 │
│  │  - Filtry       │      └─────────────────┘                 │
│  └─────────────────┘          ↓                               │
│         ↓                    ↓                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    FORMAT LOGU                          │  │
│  │  {                                                          │  │
│  │    "timestamp": "2026-07-31T12:00:00.000Z",              │  │
│  │    "level": "INFO",                                        │  │
│  │    "logger": "SSI.v4.agent_core",                        │  │
│  │    "correlation_id": "abc-123-def",                       │  │
│  │    "message": "Agent decided",                             │  │
│  │    "context": { "agent_id": "agent_1" },                  │  │
│  │    "tags": ["decision", "success"],                      │  │
│  │    "metrics": { "duration_ms": 150 }                       │  │
│  │  }                                                          │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  Hierarchia loggerów:                                          │
│  - SSI (root)                                                 │
│    - SSI.core                                                 │
│    - SSI.v2                                                   │
│    - SSI.v3                                                   │
│    - SSI.v4                                                   │
│    - SSI.data                                                 │
│    - SSI.contracts                                            │
│    - SSI.workflows                                            │
└─────────────────────────────────────────────────────────────┘

Wersja: 1.0
Data: 2026-07-31
"""

import logging
import json
import os
import sys
import uuid
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from contextvars import ContextVar
from functools import wraps
import threading


# ==========================================================================
# KONFIGURACJA GŁÓWNA
# ==========================================================================

class LogConfig:
    """Centralna konfiguracja logowania."""
    
    # Poziomy logowania
    LEVEL_DEBUG = logging.DEBUG
    LEVEL_INFO = logging.INFO
    LEVEL_WARNING = logging.WARNING
    LEVEL_ERROR = logging.ERROR
    LEVEL_CRITICAL = logging.CRITICAL
    
    # Domyślny poziom logowania
    DEFAULT_LEVEL = LEVEL_INFO
    
    # Format daty
    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    
    # Nazwa głównego logera
    ROOT_LOGGER_NAME = "SSI"
    
    # Ścieżka do pliku logów (opcjonalnie)
    LOG_FILE_PATH = None  # Jeśli None, loguje tylko na stdout
    
    # Maksymalny rozmiar pliku logów (w bajtach)
    MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    
    # Liczba kopii zapasowych plików logów
    LOG_FILE_BACKUP_COUNT = 5
    
    # Czy używać kolorów w konsoli
    USE_COLORS = True
    
    # Czy używać formatu JSON
    USE_JSON_FORMAT = True
    
    # Listy tagów dla filtrów
    SENSITIVE_KEYS = [
        "password", "secret", "token", "api_key", "private_key",
        "authorization", "auth", "credential", "access_token",
        "refresh_token", "session_id", "cookie"
    ]
    
    # Wzorce do filtrowania (regex)
    SENSITIVE_PATTERNS = [
        r'\bpassword\b', r'\bsecret\b', r'\btoken\b',
        r'\bapi[_-]?key\b', r'\bprivate[_-]?key\b'
    ]


# ==========================================================================
# CORRELATION ID
# ==========================================================================

# ContextVar dla correlation_id (thread-safe)
_correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


def generate_correlation_id() -> str:
    """Generuje unikalny correlation_id."""
    return f"{uuid.uuid4().hex[:8]}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"


def get_correlation_id() -> Optional[str]:
    """Pobiera bieżący correlation_id z kontekstu."""
    return _correlation_id_var.get()


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """
    Ustawia correlation_id w kontekście.
    
    Args:
        correlation_id: Identyfikator korelacji (jeśli None, wygeneruje nowy)
        
    Returns:
        Ustawiony correlation_id
    """
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    _correlation_id_var.set(correlation_id)
    return correlation_id


# ==========================================================================
# FORMATER JSON
# ==========================================================================

class JSONFormatter(logging.Formatter):
    """
    Formater logów w formacie JSON.
    
    Generuje logi w formacie:
    {
        "timestamp": "2026-07-31T12:00:00.000Z",
        "level": "INFO",
        "logger": "SSI.v4.agent_core",
        "correlation_id": "abc-123",
        "message": "Agent decided",
        "context": { ... },
        "tags": ["decision"],
        "metrics": { ... }
    }
    """
    
    def __init__(self, datefmt: Optional[str] = None):
        super().__init__(datefmt=datefmt)
        self._datefmt = datefmt or LogConfig.DATE_FORMAT
    
    def format(self, record: logging.LogRecord) -> str:
        """Formatuje rekord logu do JSON."""
        log_data = self._extract_log_data(record)
        return json.dumps(log_data, ensure_ascii=False, default=str)
    
    def _extract_log_data(self, record: logging.LogRecord) -> Dict[str, Any]:
        """Wyciąga dane z rekordu logu."""
        # Podstawowe pola
        log_data = {
            "timestamp": datetime.now(timezone.utc).strftime(self._datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "thread": record.threadName,
            "process": record.processName,
        }
        
        # Dodaj correlation_id
        correlation_id = get_correlation_id()
        if correlation_id:
            log_data["correlation_id"] = correlation_id
        
        # Dodaj kontekst (extra fields)
        context = {}
        for key, value in record.__dict__.items():
            if key not in (
                'name', 'msg', 'args', 'created', 'filename', 'funcName',
                'levelname', 'levelno', 'lineno', 'module', 'msecs',
                'pathname', 'process', 'processName', 'relativeCreated',
                'stack_info', 'exc_info', 'exc_text', 'thread', 'threadName',
                'getMessage', 'message'
            ):
                try:
                    # Filtruj sekrety
                    filtered_value = self._filter_sensitive_data(key, value)
                    if filtered_value is not None:
                        context[key] = filtered_value
                except Exception:
                    context[key] = "<unserializable>"
        
        if context:
            log_data["context"] = context
        
        # Dodaj informacje o błędzie
        if record.exc_info:
            log_data["error"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
            }
        
        # Dodaj tagi (z poziomu logowania)
        tags = []
        if record.levelno >= logging.ERROR:
            tags.append("error")
        elif record.levelno >= logging.WARNING:
            tags.append("warning")
        elif record.levelno >= logging.INFO:
            tags.append("info")
        
        if tags:
            log_data["tags"] = tags
        
        return log_data
    
    def _filter_sensitive_data(self, key: str, value: Any) -> Any:
        """Filtruje wrażliwe dane z logów."""
        # Sprawdź, czy klucz jest wrażliwy
        if any(keyword in key.lower() for keyword in LogConfig.SENSITIVE_KEYS):
            return "<REDACTED>"
        
        # Sprawdź wzorce regex
        key_lower = str(key).lower()
        for pattern in LogConfig.SENSITIVE_PATTERNS:
            if re.search(pattern, key_lower, re.IGNORECASE):
                return "<REDACTED>"
        
        # Jeśli value jest stringiem, sprawdź, czy zawiera wrażliwe dane
        if isinstance(value, str):
            for pattern in LogConfig.SENSITIVE_PATTERNS:
                if re.search(pattern, value, re.IGNORECASE):
                    return "<REDACTED>"
        
        # Zwróć oryginalną wartość
        return value


# ==========================================================================
# FORMATER KOLOROWY (dla konsoli)
# ==========================================================================

class ColorFormatter(logging.Formatter):
    """Formater logów z kolorami dla konsoli."""
    
    # Kody kolorów ANSI
    COLORS = {
        logging.DEBUG: '\033[36m',    # Cyan
        logging.INFO: '\033[32m',     # Zielony
        logging.WARNING: '\033[33m',  # Żółty
        logging.ERROR: '\033[31m',    # Czerwony
        logging.CRITICAL: '\033[35;1m', # Purpurowy + bold
    }
    
    RESET = '\033[0m'
    
    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None):
        super().__init__(fmt, datefmt)
    
    def format(self, record: logging.LogRecord) -> str:
        """Formatuje rekord logu z kolorami."""
        # Dodaj correlation_id do rekordu
        correlation_id = get_correlation_id()
        if correlation_id:
            record.correlation_id = correlation_id
        
        # Formatuj message
        message = super().format(record)
        
        # Dodaj kolor
        color = self.COLORS.get(record.levelno, '')
        reset = self.RESET
        
        return f"{color}{message}{reset}"


# ==========================================================================
# FILTR SEKRETÓW
# ==========================================================================

class SensitiveDataFilter(logging.Filter):
    """Filtr, który usuwa wrażliwe dane z logów."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filtruje rekord logu, usunąc wrażliwe dane.
        
        Zwraca True, jeśli rekord powinien być zalogowany.
        """
        # Zawsze zwracaj True (filtruj dane w formatterze)
        return True


# ==========================================================================
# KONFIGURACJA LOGGINGU
# ==========================================================================

class LoggingConfigurator:
    """Konfigurator systemu logowania."""
    
    _configured = False
    _lock = threading.Lock()
    
    @classmethod
    def configure(cls, level: int = None, json_format: bool = None) -> None:
        """
        Konfiguruje system logowania.
        
        Args:
            level: Poziom logowania (domyślny: LogConfig.DEFAULT_LEVEL)
            json_format: Czy używać formatu JSON (domyślny: LogConfig.USE_JSON_FORMAT)
        """
        with cls._lock:
            if cls._configured:
                return
            
            # Ustaw poziom logowania
            level = level or LogConfig.DEFAULT_LEVEL
            
            # Ustaw format
            json_format = json_format if json_format is not None else LogConfig.USE_JSON_FORMAT
            
            # Pobierz root logera
            root_logger = logging.getLogger()
            
            # Ustaw poziom
            root_logger.setLevel(level)
            
            # Wyczyść istniejące handlery
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
            
            # Utwórz formatter
            if json_format:
                formatter = JSONFormatter(datefmt=LogConfig.DATE_FORMAT)
            else:
                fmt = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                if LogConfig.USE_COLORS:
                    formatter = ColorFormatter(fmt, LogConfig.DATE_FORMAT)
                else:
                    formatter = logging.Formatter(fmt, LogConfig.DATE_FORMAT)
            
            # Dodaj handler dla konsoli (stdout)
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            console_handler.addFilter(SensitiveDataFilter())
            root_logger.addHandler(console_handler)
            
            # Dodaj handler dla pliku (jeśli zdefiniowano ścieżkę)
            if LogConfig.LOG_FILE_PATH:
                try:
                    from logging.handlers import RotatingFileHandler
                    file_handler = RotatingFileHandler(
                        LogConfig.LOG_FILE_PATH,
                        maxBytes=LogConfig.MAX_LOG_FILE_SIZE,
                        backupCount=LogConfig.LOG_FILE_BACKUP_COUNT,
                        encoding='utf-8'  # UTF-8 dla poprawnego zapisu polskich znaków
                    )
                    file_handler.setLevel(level)
                    file_handler.setFormatter(formatter)
                    file_handler.addFilter(SensitiveDataFilter())
                    root_logger.addHandler(file_handler)
                except ImportError:
                    # RotatingFileHandler niedostępny (starsze Python)
                    file_handler = logging.FileHandler(
                        LogConfig.LOG_FILE_PATH,
                        encoding='utf-8'
                    )
                    file_handler.setLevel(level)
                    file_handler.setFormatter(formatter)
                    file_handler.addFilter(SensitiveDataFilter())
                    root_logger.addHandler(file_handler)
            
            # Skonfiguruj ostatnio
            cls._configured = True
            
            # Ustaw propagation dla SSI loggerów
            logging.getLogger(LogConfig.ROOT_LOGGER_NAME).propagate = True
    
    @classmethod
    def get_logger(cls, name: str, level: int = None) -> logging.Logger:
        """
        Zwraca loggera o podanej nazwie.
        
        Args:
            name: Nazwa logera (np. "SSI.v4.agent_core")
            level: Poziom logowania (domyślny: dziedziczy od root)
            
        Returns:
            Logger
        """
        # Upewnij się, że logging jest skonfigurowany
        cls.configure()
        
        logger = logging.getLogger(name)
        if level is not None:
            logger.setLevel(level)
        
        return logger
    
    @classmethod
    def reset(cls) -> None:
        """Resetuje konfigurację logowania."""
        with cls._lock:
            cls._configured = False


# ==========================================================================
# DEKORATORY
# ==========================================================================

def with_correlation_id(func):
    """
    Dekorator, który automatycznie ustawia correlation_id dla funkcji.
    
    Użycie:
        @with_correlation_id
        def make_decision(self, context):
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Wygeneruj lub pobierz correlation_id
        correlation_id = kwargs.pop('correlation_id', None)
        if correlation_id is None:
            correlation_id = get_correlation_id() or generate_correlation_id()
        
        # Ustaw correlation_id w kontekście
        set_correlation_id(correlation_id)
        
        try:
            return func(*args, **kwargs)
        finally:
            # Nie czyszcz correlation_id (może być potrzebny w wyżej_angle funkcjach)
            pass
    
    return wrapper


def with_logging(func):
    """
    Dekorator, który automatycznie loguje wejście/wyjście z funkcji.
    
    Użycie:
        @with_logging
        def make_decision(self, context):
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        
        # Loguj wejście
        logger.debug(f"Entering {func.__name__}")
        
        start_time = datetime.now(timezone.utc)
        try:
            result = func(*args, **kwargs)
            
            # Loguj wyjście (tylko dla trybu debug)
            elapsed_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            logger.debug(f"Exiting {func.__name__} in {elapsed_ms:.2f}ms")
            
            return result
        except Exception as e:
            elapsed_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            logger.error(f"Error in {func.__name__} after {elapsed_ms:.2f}ms: {e}")
            raise
    
    return wrapper


# ==========================================================================
# HIERARCHIA WYJĄTKÓW
# ==========================================================================

class SSIError(Exception):
    """Bazowa klasa wyjątków dla systemu SSI."""
    
    def __init__(self, message: str, code: Optional[str] = None, 
                 correlation_id: Optional[str] = None, **kwargs):
        super().__init__(message)
        self.message = message
        self.code = code or "SSI_ERROR"
        self.correlation_id = correlation_id or get_correlation_id()
        self.context = kwargs
        self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje wyjątek do słownika (dla logów)."""
        return {
            "error": {
                "type": self.__class__.__name__,
                "code": self.code,
                "message": self.message,
                "correlation_id": self.correlation_id,
                "timestamp": self.timestamp,
                "context": self.context
            }
        }
    
    def __str__(self) -> str:
        return f"[{self.code}] {self.message} (correlation_id: {self.correlation_id})"


class SSIDomainError(SSIError):
    """Wyjątek domenowy (błędy biznesowe)."""
    pass


class SSIInfrastructureError(SSIError):
    """Wyjątek infrastrukturalny (błędy techniczne)."""
    pass


class SSIValidationError(SSIDomainError):
    """Błąd walidacji danych."""
    pass


class SSIConfigurationError(SSIInfrastructureError):
    """Błąd konfiguracji."""
    pass


class SSITimeoutError(SSIInfrastructureError):
    """Błąd timeoutu."""
    pass


class SSIConnectionError(SSIInfrastructureError):
    """Błąd połączenia."""
    pass


class SSINotReadyError(SSIInfrastructureError):
    """Moduł nie jest gotowy do pracy."""
    pass


# ==========================================================================
# METRYKI
# ==========================================================================

class MetricsCollector:
    """
    Kolektor metryk dla systemu SSI.
    
    Zapewnia:
    - Liczenie sukcesów, błędów, timeoutów
    - Pomiar czasu wykonania
    - Liczenie zużycia zasobów
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._metrics = {
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
        self._initialized = True
    
    def record_decision(self, success: bool = True, timeout: bool = False, 
                       duration_ms: float = 0) -> None:
        """Rejestruje decyzję."""
        with self._lock:
            self._metrics["decisions"]["total"] += 1
            
            if success:
                self._metrics["decisions"]["success"] += 1
            else:
                self._metrics["decisions"]["error"] += 1
            
            if timeout:
                self._metrics["decisions"]["timeout"] += 1
            
            # Aktualizuj metryki czasu
            self._metrics["performance"]["total_time_ms"] += duration_ms
            self._metrics["performance"]["min_time_ms"] = min(
                self._metrics["performance"]["min_time_ms"], duration_ms
            )
            self._metrics["performance"]["max_time_ms"] = max(
                self._metrics["performance"]["max_time_ms"], duration_ms
            )
            self._metrics["performance"]["last_time_ms"] = duration_ms
    
    def get_metrics(self) -> Dict[str, Any]:
        """Zwraca aktualne metryki."""
        with self._lock:
            return {
                "decisions": self._metrics["decisions"].copy(),
                "performance": self._metrics["performance"].copy(),
                "resources": self._metrics["resources"].copy()
            }
    
    def reset(self) -> None:
        """Resetuje metryki."""
        with self._lock:
            self._metrics = {
                "decisions": {"total": 0, "success": 0, "error": 0, "timeout": 0},
                "performance": {
                    "total_time_ms": 0,
                    "min_time_ms": float('inf'),
                    "max_time_ms": 0,
                    "last_time_ms": 0
                },
                "resources": {"memory_usage_mb": 0, "cpu_usage_percent": 0}
            }


# ==========================================================================
# HEALTH CHECK I READINESS CHECK
# ==========================================================================

class HealthCheck:
    """
    Komponent health check dla systemu SSI.
    
    Sprawdza:
    - Czy moduły są załadowane
    - Czy zależności są dostępne
    - Czy system jest gotowy do pracy
    """
    
    def __init__(self):
        self._status = {
            "ready": False,
            "dependencies": {},
            "modules": {},
            "timestamp": None
        }
        self._lock = threading.Lock()
    
    def check_dependency(self, name: str, check_func) -> bool:
        """
        Sprawdza zależność.
        
        Args:
            name: Nazwa zależności
            check_func: Funkcja sprawdzająca (zwraca True jeśli OK)
            
        Returns:
            True jeśli zależność jest dostępna
        """
        try:
            result = check_func()
            with self._lock:
                self._status["dependencies"][name] = {
                    "status": "ready" if result else "not_ready",
                    "checked_at": datetime.now(timezone.utc).isoformat()
                }
            return result
        except Exception as e:
            with self._lock:
                self._status["dependencies"][name] = {
                    "status": "error",
                    "error": str(e),
                    "checked_at": datetime.now(timezone.utc).isoformat()
                }
            return False
    
    def check_module(self, name: str, check_func) -> bool:
        """
        Sprawdza moduł.
        
        Args:
            name: Nazwa modułu
            check_func: Funkcja sprawdzająca (zwraca True jeśli OK)
            
        Returns:
            True jeśli moduł jest gotowy
        """
        try:
            result = check_func()
            with self._lock:
                self._status["modules"][name] = {
                    "status": "ready" if result else "not_ready",
                    "checked_at": datetime.now(timezone.utc).isoformat()
                }
            return result
        except Exception as e:
            with self._lock:
                self._status["modules"][name] = {
                    "status": "error",
                    "error": str(e),
                    "checked_at": datetime.now(timezone.utc).isoformat()
                }
            return False
    
    def set_ready(self, ready: bool = True) -> None:
        """Ustawia status gotowości systemu."""
        with self._lock:
            self._status["ready"] = ready
            self._status["timestamp"] = datetime.now(timezone.utc).isoformat()
    
    def is_ready(self) -> bool:
        """Sprawdza, czy system jest gotowy."""
        with self._lock:
            return self._status["ready"]
    
    def check_all_dependencies(self) -> Dict[str, bool]:
        """
        Sprawdza wszystkie zależności systemu (V2, V3, V4).
        
        Returns:
            Słownik z wynikami sprawdzania dla każdej zależności
        """
        results = {}
        
        # Sprawdź V2
        try:
            from ..v2 import V2Integration, tworz_integracje_v2
            results["v2"] = self.check_dependency(
                "v2", 
                lambda: True  # V2 jest dostępny, jeśli import się powiódł
            )
        except ImportError as e:
            results["v2"] = self.check_dependency("v2", lambda: False)
        
        # Sprawdź V3
        try:
            from ..v3 import V3Integration, tworz_v3_integration
            results["v3"] = self.check_dependency(
                "v3",
                lambda: True  # V3 jest dostępny, jeśli import się powiódł
            )
        except ImportError as e:
            results["v3"] = self.check_dependency("v3", lambda: False)
        
        # Sprawdź V4
        try:
            from ..v4 import AgentBirthSystem, RoomCore, Agent
            results["v4"] = self.check_dependency(
                "v4",
                lambda: True  # V4 jest dostępny, jeśli import się powiódł
            )
        except ImportError as e:
            results["v4"] = self.check_dependency("v4", lambda: False)
        
        # Ustaw status gotowości na podstawie zależności
        all_dependencies_ok = all(results.values())
        self.set_ready(all_dependencies_ok)
        
        return results
    
    def check_all_modules(self) -> Dict[str, bool]:
        """
        Sprawdza wszystkie moduły systemu (core, data, contracts, workflows).
        
        Returns:
            Słownik z wynikami sprawdzania dla każdego modułu
        """
        results = {}
        
        # Sprawdź core
        try:
            from ..core import system, logging_config
            results["core"] = self.check_module(
                "core",
                lambda: True
            )
        except ImportError:
            results["core"] = self.check_module("core", lambda: False)
        
        # Sprawdź data
        try:
            from ..data import data_manager, policies
            results["data"] = self.check_module(
                "data",
                lambda: True
            )
        except ImportError:
            results["data"] = self.check_module("data", lambda: False)
        
        # Sprawdź contracts
        try:
            from ..contracts import contract_manager
            results["contracts"] = self.check_module(
                "contracts",
                lambda: True
            )
        except ImportError:
            results["contracts"] = self.check_module("contracts", lambda: False)
        
        # Sprawdź workflows
        try:
            from ..workflows import vertical_flow
            results["workflows"] = self.check_module(
                "workflows",
                lambda: True
            )
        except ImportError:
            results["workflows"] = self.check_module("workflows", lambda: False)
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca aktualny status."""
        with self._lock:
            return {
                "ready": self._status["ready"],
                "dependencies": self._status["dependencies"].copy(),
                "modules": self._status["modules"].copy(),
                "timestamp": self._status["timestamp"]
            }


# ==========================================================================
# INICJALIZACJA
# ==========================================================================

# Skonfiguruj logging przy imporcie
LoggingConfigurator.configure()

# Utwórz globalne instancje
metrics_collector = MetricsCollector()
health_check = HealthCheck()

# Automatyczne sprawdzenie zależności i modułów przy starcie
def _initialize_health_check():
    """Inicjalizuje HealthCheck z automatycznym sprawdzaniem zależności."""
    health_check.check_all_dependencies()
    health_check.check_all_modules()

# Wywołaj inicjalizację
_initialize_health_check()


# ==========================================================================
# FUNKCJE POMOCNICZE
# ==========================================================================

def setup_logging(level: int = None, json_format: bool = None) -> None:
    """
    Inicjalizuje system logowania.
    
    Args:
        level: Poziom logowania
        json_format: Czy używać formatu JSON
    """
    LoggingConfigurator.configure(level, json_format)


def get_logger(name: str) -> logging.Logger:
    """
    Zwraca loggera o podanej nazwie.
    
    Args:
        name: Nazwa logera
        
    Returns:
        Logger
    """
    return LoggingConfigurator.get_logger(name)


def log_exception(logger: logging.Logger, exc: Exception, 
                  context: Dict[str, Any] = None) -> None:
    """
    Loguje wyjątek z pełnym tracebackiem.
    
    Args:
        logger: Logger do użycia
        exc: Wyjątek do zalogowania
        context: Dodatkowy kontekst
    """
    context = context or {}
    context["correlation_id"] = get_correlation_id()
    
    if isinstance(exc, SSIError):
        logger.error(
            exc.message,
            extra={
                "error_code": exc.code,
                "correlation_id": exc.correlation_id,
                "context": exc.context,
                "exc_info": True
            }
        )
    else:
        logger.error(
            str(exc),
            extra={
                "error_type": type(exc).__name__,
                "correlation_id": get_correlation_id(),
                "context": context,
                "exc_info": True
            }
        )


# ==========================================================================
# INICJALIZACJA AUTOMATYCZNA
# ==========================================================================

# Automatycznie skonfiguruj logging dla głównego modułu
if __name__ != "__main__":
    # Jeśli ten moduł jest importowany, skonfiguruj logging
    setup_logging()
