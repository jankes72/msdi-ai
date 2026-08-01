"""
SSI V5 - Message Validator

Modul odpowiedzialny za walidacje struktur wiadomosci SSIMessage.
Walidacja jest pierwszym krokiem w papierze przetwarzania wiadomosci.

Zasady:
- Walidacja zawsze pierwsza
- Brak walidacji = NIE wykonuj dzialania
- Najpierw: korekta kontekstu -> walidacja -> wykonanie

Wersja: 2.0.0
Data: 2026-08-01
"""

import re
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from SSI.v5.core.information_flow_controller.message_models import (
    SSIMessage,
    MessageStatus,
    PriorityLevel,
    ProcessType,
    ModuleIdentifier,
    SystemStateSnapshot
)

# Konfiguracja logowania
logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Poziomy walidacji."""
    STRICT = "strict"          # Calkowita walidacja, wszystkie polQiowiza
    STANDARD = "standard"      # Standardowa walidacja (domyslna)
    BASIC = "basic"            # Podstawowa walidacja (tylko wymagane pola)
    MINIMAL = "minimal"        # Minimalna walidacja (tylko struktura)


class ValidationResult(Enum):
    """Wynik walidacji."""
    VALID = "valid"            # Walidacja zakonczona sukcesem
    INVALID = "invalid"        # Walidacja nie powiodla sie
    WARNING = "warning"        # Walidacja z ostrzezeniami (moze byc akceptowalne)
    CRITICAL = "critical"      # Krytyczny blad walidacji


@dataclass
class ValidationError:
    """Blad walidacji."""
    error_code: str
    error_type: str
    field_name: str
    message: str
    severity: str = "error"  # error, warning, critical
    suggested_fix: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        return {
            'error_code': self.error_code,
            'error_type': self.error_type,
            'field_name': self.field_name,
            'message': self.message,
            'severity': self.severity,
            'suggested_fix': self.suggested_fix
        }
    
    def __str__(self) -> str:
        return f"[{self.error_code}] {self.field_name}: {self.message}"


@dataclass
class ValidationReport:
    """Raport z walidacji wiadomosci."""
    message_id: str
    is_valid: bool = True
    validation_level: ValidationLevel = ValidationLevel.STANDARD
    result: ValidationResult = ValidationResult.VALID
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    processing_time_ms: float = 0.0
    validated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        return {
            'message_id': self.message_id,
            'is_valid': self.is_valid,
            'validation_level': self.validation_level.value,
            'result': self.result.value,
            'errors': [e.to_dict() for e in self.errors],
            'warnings': [w.to_dict() for w in self.warnings],
            'processing_time_ms': self.processing_time_ms,
            'validated_at': self.validated_at.isoformat(),
            'error_count': len(self.errors),
            'warning_count': len(self.warnings)
        }
    
    def add_error(self, error: ValidationError) -> None:
        """Dodanie bledy do raportu."""
        self.errors.append(error)
        self.is_valid = False
        if error.severity == "critical":
            self.result = ValidationResult.CRITICAL
        elif self.result != ValidationResult.CRITICAL:
            self.result = ValidationResult.INVALID
    
    def add_warning(self, warning: ValidationError) -> None:
        """Dodanie ostrzezenia do raportu."""
        self.warnings.append(warning)
        if self.result == ValidationResult.VALID:
            self.result = ValidationResult.WARNING
    
    def get_critical_errors(self) -> List[ValidationError]:
        """Pobranie krytycznych bledow."""
        return [e for e in self.errors if e.severity == "critical"]
    
    def get_error_messages(self) -> List[str]:
        """Pobranie listy komunikatow o bledach."""
        return [str(e) for e in self.errors]
    
    def get_warning_messages(self) -> List[str]:
        """Pobranie listy ostrzezen."""
        return [str(w) for w in self.warnings]
    
    def __str__(self) -> str:
        status = "VALID" if self.is_valid else "INVALID"
        return f"ValidationReport({self.message_id}): {status} | Errors: {len(self.errors)} | Warnings: {len(self.warnings)}"


@dataclass
class ValidationConfig:
    """Konfiguracja walidatora."""
    # Poziom walidacji
    validation_level: ValidationLevel = ValidationLevel.STANDARD
    
    # Ograniczenia czasowe
    max_message_age_seconds: int = 3600  # Max wiek wiadomosci w sekundach
    min_timestamp: Optional[datetime] = None
    max_timestamp: Optional[datetime] = None
    
    # Ograniczenia rozmiaru
    max_payload_size_kb: int = 1024  # Max rozmiar payload w KB
    max_metadata_size_kb: int = 256   # Max rozmiar metadanych w KB
    
    # Wymagane pola
    require_correlation_id: bool = False
    require_session_id: bool = True
    require_cycle_id: bool = True
    
    # Sprawdzanie konsystencji
    check_source_target_patterns: bool = True
    check_timestamp_consistency: bool = True
    check_system_state_validity: bool = True
    
    # Dopuszczalne wartosci
    allowed_process_types: Optional[Set[str]] = None
    allowed_priority_levels: Optional[Set[str]] = None
    allowed_module_types: Set[str] = field(default_factory=lambda: {"system", "runtime", "agent", "teacher", "memory", "developer"})
    
    # Zasady walidacji
    strict_mode: bool = False  # Czy przerwac walidacje przy pierwszym bledzie
    
    @classmethod
    def strict(cls) -> 'ValidationConfig':
        """Konfiguracja strict."""
        return cls(
            validation_level=ValidationLevel.STRICT,
            strict_mode=True,
            require_correlation_id=True,
            check_source_target_patterns=True,
            check_timestamp_consistency=True,
            check_system_state_validity=True
        )
    
    @classmethod
    def minimal(cls) -> 'ValidationConfig':
        """Konfiguracja minimalna."""
        return cls(
            validation_level=ValidationLevel.MINIMAL,
            strict_mode=False,
            require_correlation_id=False,
            require_session_id=False,
            require_cycle_id=False,
            check_source_target_patterns=False
        )


class MessageValidator:
    """
    Walidator wiadomosci SSIMessage.
    
    Odpowiedzialnosc:
    - Walidacja struktury SSIMessage
    - Sprawdzanie wymaganych pol
    - Kontrola source/target
    - Kontrola timestamp
    - Kontrola correlation_id
    - Kontrola wersji komunikatu
    - Obsluga blednych komunikatow
    
    Zasady:
    1. Walidacja zawsze pierwsza
    2. Brak walidacji = NIE wykonuj dzialania
    3. Najpierw: korekta kontekstu -> walidacja -> wykonanie
    """
    
    # Zbiory do walidacji
    RESERVED_MESSAGE_IDS: Set[str] = {"default", "none", "null", ""}
    RESERVED_SESSION_IDS: Set[str] = {"default", "system", "global"}
    RESERVED_CYCLE_IDS: Set[str] = {"default", "system", "init", "shutdown"}
    
    # Wzorce dla identyfikatorow
    MESSAGE_ID_PATTERN: re.Pattern = re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', re.IGNORECASE)
    SESSION_ID_PATTERN: re.Pattern = re.compile(r'^[a-zA-Z0-9_-]{1,64}$')
    CYCLE_ID_PATTERN: re.Pattern = re.compile(r'^[a-zA-Z0-9_-]{1,64}$')
    MODULE_NAME_PATTERN: re.Pattern = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]{0,63}$')
    
    # domyslna konfiguracja
    _default_config: ValidationConfig = ValidationConfig()
    
    def __init__(self, config: ValidationConfig = None):
        """
        Inicjalizacja walidatora.
        
        Args:
            config: Konfiguracja walidatora (opcjonalnie)
        """
        self.config = config or self._default_config
        self._validation_hooks: List[Callable[[SSIMessage, ValidationReport], None]] = []
        self._initialized = True
        logger.info(f"MessageValidator zainicjalizowany z poziomem walidacji: {self.config.validation_level.value}")
    
    @classmethod
    def get_instance(cls, config: ValidationConfig = None) -> 'MessageValidator':
        """Pobranie instancji walidatora (singleton)."""
        # Prosty singleton - w przyszlosci moze byc rozbudowany
        if not hasattr(cls, '_instance'):
            cls._instance = cls(config)
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset instancji singleton."""
        if hasattr(cls, '_instance'):
            del cls._instance
    
    def set_config(self, config: ValidationConfig) -> None:
        """Ustawienie konfiguracji walidatora."""
        self.config = config
        logger.info(f"Zmieniono konfiguracje walidatora na: {config.validation_level.value}")
    
    def register_validation_hook(
        self, 
        hook: Callable[[SSIMessage, ValidationReport], None]
    ) -> None:
        """Rejestracja hooka walidacyjnego."""
        self._validation_hooks.append(hook)
        logger.debug(f"Zarejestrowano hook walidacyjny: {hook.__name__}")
    
    def validate(
        self, 
        message: SSIMessage, 
        config: ValidationConfig = None
    ) -> ValidationReport:
        """
        Glowna metoda walidacji wiadomosci.
        
        Args:
            message: Wiadomosc do zwalidowania
            config: Konfiguracja walidacji (opcjonalnie, nadpisuje domyslna)
            
        Returns:
            ValidationReport: Raport z walidacji
        """
        import time
        start_time = time.time()
        
        # Uzycie konfiguracji podanej lub domyslnej
        validation_config = config or self.config
        
        # Utworzenie raportu
        report = ValidationReport(
            message_id=message.message_id,
            validation_level=validation_config.validation_level,
            is_valid=True
        )
        
        try:
            # Walidacjaructury
            if validation_config.validation_level in [ValidationLevel.STRICT, ValidationLevel.STANDARD, ValidationLevel.BASIC]:
                self._validate_structure(message, report, validation_config)
            
            # Walidacja pol wymaganych
            if validation_config.validation_level in [ValidationLevel.STRICT, ValidationLevel.STANDARD]:
                self._validate_required_fields(message, report, validation_config)
            
            # Walidacja timestamp
            if validation_config.validation_level in [ValidationLevel.STRICT, ValidationLevel.STANDARD]:
                self._validate_timestamp(message, report, validation_config)
            
            # Walidacja source/target
            if validation_config.validation_level in [ValidationLevel.STRICT, ValidationLevel.STANDARD]:
                self._validate_source_target(message, report, validation_config)
            
            # Walidacja system_state
            if validation_config.validation_level in [ValidationLevel.STRICT, ValidationLevel.STANDARD]:
                self._validate_system_state(message, report, validation_config)
            
            # Walidacja identyfikatorow
            if validation_config.validation_level in [ValidationLevel.STRICT, ValidationLevel.STANDARD]:
                self._validate_identifiers(message, report, validation_config)
            
            # Walidacja process_type
            if validation_config.validation_level in [ValidationLevel.STRICT, ValidationLevel.STANDARD]:
                self._validate_process_type(message, report, validation_config)
            
            # Walidacja priority
            if validation_config.validation_level in [ValidationLevel.STRICT, ValidationLevel.STANDARD]:
                self._validate_priority(message, report, validation_config)
            
            # Walidacja payload
            if validation_config.validation_level == ValidationLevel.STRICT:
                self._validate_payload(message, report, validation_config)
            
            # Walidacja konsystencji
            if validation_config.validation_level in [ValidationLevel.STRICT, ValidationLevel.STANDARD]:
                self._validate_consistency(message, report, validation_config)
            
            # Wywolanie hookow
            for hook in self._validation_hooks:
                try:
                    hook(message, report)
                except Exception as e:
                    report.add_error(ValidationError(
                        error_code="HOOK_ERROR",
                        error_type="validation_hook_failed",
                        field_name="hooks",
                        message=f"Hook walidacyjny zaliczony: {e}",
                        severity="warning"
                    ))
            
            # Jeśli strict_mode i sa błędy, przerwij
            if validation_config.strict_mode and not report.is_valid:
                logger.warning(f"Walidacja przerwana (strict mode) dla wiadomosci: {message.message_id}")
                return report
            
        except Exception as e:
            report.add_error(ValidationError(
                error_code="VALIDATION_ERROR",
                error_type="unexpected_error",
                field_name="message",
                message=f"Nieoczekiwany blad podczas walidacji: {e}",
                severity="critical"
            ))
        
        # Czas przetwarzania
        report.processing_time_ms = (time.time() - start_time) * 1000
        
        # Logowanie
        if report.is_valid:
            logger.debug(f"Walidacja powiodla sie: {message.message_id}")
        elif report.result == ValidationResult.CRITICAL:
            logger.error(f"Krytyczny blad walidacji: {message.message_id} - {report.get_error_messages()}")
        elif report.result == ValidationResult.INVALID:
            logger.warning(f"Walidacja nie powiodla sie: {message.message_id} - {report.get_error_messages()}")
        else:
            logger.info(f"Walidacja z ostrzezeniami: {message.message_id} - {report.get_warning_messages()}")
        
        return report
    
    def validate_batch(
        self, 
        messages: List[SSIMessage], 
        config: ValidationConfig = None
    ) -> Dict[str, ValidationReport]:
        """
        Walidacja wsadu wiadomosci.
        
        Args:
            messages: Lista wiadomosci do zwalidowania
            config: Konfiguracja walidacji (opcjonalnie)
            
        Returns:
            Dict[str, ValidationReport]: Raporty walidacji dla kazdej wiadomosci
        """
        reports = {}
        for message in messages:
            reports[message.message_id] = self.validate(message, config)
        return reports
    
    def is_valid(self, message: SSIMessage) -> bool:
        """
        Szybka walidacja - zwraca True/False.
        
        Args:
            message: Wiadomosc do zwalidowania
            
        Returns:
            bool: Czy wiadomosc jest poprawna
        """
        return self.validate(message).is_valid
    
    def _validate_structure(
        self, 
        message: SSIMessage, 
        report: ValidationReport, 
        config: ValidationConfig
    ) -> None:
        """Walidacja struktury wiadomosci."""
        # Sprawdzenie czy message jest instancja SSIMessage
        if not isinstance(message, SSIMessage):
            report.add_error(ValidationError(
                error_code="STRUCTURE_001",
                error_type="invalid_type",
                field_name="message",
                message=f"Wiadomosc nie jest instancja SSIMessage: {type(message)}",
                severity="critical",
                suggested_fix="Uzyj SSIMessage z message_factory"
            ))
            return
        
        # Sprawdzenie pola message_id
        if not hasattr(message, 'message_id') or not message.message_id:
            report.add_error(ValidationError(
                error_code="STRUCTURE_002",
                error_type="missing_field",
                field_name="message_id",
                message="Brak identyfikatora wiadomosci",
                severity="critical",
                suggested_fix="Ustaw message_id lub uzyj domyslnego UUID"
            ))
        elif message.message_id in self.RESERVED_MESSAGE_IDS:
            report.add_error(ValidationError(
                error_code="STRUCTURE_003",
                error_type="reserved_id",
                field_name="message_id",
                message=f"Zastrzezony identyfikator wiadomosci: {message.message_id}",
                severity="error",
                suggested_fix="Uzyj unikalnego ID (UUID)"
            ))
        
        # Sprawdzenie formatu message_id
        if message.message_id and not self.MESSAGE_ID_PATTERN.match(message.message_id):
            # Akceptujemy rowniez proste stringi (nie UUID)
            if len(message.message_id) < 1 or len(message.message_id) > 64:
                report.add_warning(ValidationError(
                    error_code="STRUCTURE_004",
                    error_type="invalid_format",
                    field_name="message_id",
                    message=f"Nietypowy format message_id: {message.message_id}",
                    severity="warning",
                    suggested_fix="Uzyj standardowego UUID"
                ))
    
    def _validate_required_fields(
        self, 
        message: SSIMessage, 
        report: ValidationReport, 
        config: ValidationConfig
    ) -> None:
        """Walidacja pol wymaganych."""
        # Sprawdzenie source
        if not hasattr(message, 'source') or not message.source:
            report.add_error(ValidationError(
                error_code="REQUIRED_001",
                error_type="missing_field",
                field_name="source",
                message="Brak zrodla wiadomosci",
                severity="critical",
                suggested_fix="Ustaw source jako ModuleIdentifier"
            ))
        
        # Sprawdzenie target
        if not hasattr(message, 'target') or not message.target:
            report.add_error(ValidationError(
                error_code="REQUIRED_002",
                error_type="missing_field",
                field_name="target",
                message="Brak celu wiadomosci",
                severity="critical",
                suggested_fix="Ustaw target jako ModuleIdentifier"
            ))
        
        # Sprawdzenie timestamp
        if not hasattr(message, 'timestamp') or not message.timestamp:
            report.add_error(ValidationError(
                error_code="REQUIRED_003",
                error_type="missing_field",
                field_name="timestamp",
                message="Brak timestamp wiadomosci",
                severity="critical",
                suggested_fix="Ustaw timestamp lub uzyj automatycznej wartosci"
            ))
        
        # Sprawdzenie process_type
        if not hasattr(message, 'process_type') or not message.process_type:
            report.add_error(ValidationError(
                error_code="REQUIRED_004",
                error_type="missing_field",
                field_name="process_type",
                message="Brak process_type wiadomosci",
                severity="critical",
                suggested_fix="Ustaw process_type (np. ProcessType.SYSTEM_INIT)"
            ))
        
        # Sprawdzenie payload
        if not hasattr(message, 'payload'):
            report.add_warning(ValidationError(
                error_code="REQUIRED_005",
                error_type="missing_field",
                field_name="payload",
                message="Brak payload wiadomosci",
                severity="warning",
                suggested_fix="Ustaw payload jako pusta nie Sosow {}"
            ))
        
        # Sprawdzenie session_id
        if config.require_session_id:
            if not hasattr(message, 'session_id') or not message.session_id:
                report.add_error(ValidationError(
                    error_code="REQUIRED_006",
                    error_type="missing_field",
                    field_name="session_id",
                    message="Brak session_id wiadomosci",
                    severity="error",
                    suggested_fix="Ustaw session_id"
                ))
        
        # Sprawdzenie cycle_id
        if config.require_cycle_id:
            if not hasattr(message, 'cycle_id') or not message.cycle_id:
                report.add_error(ValidationError(
                    error_code="REQUIRED_007",
                    error_type="missing_field",
                    field_name="cycle_id",
                    message="Brak cycle_id wiadomosci",
                    severity="error",
                    suggested_fix="Ustaw cycle_id"
                ))
        
        # Sprawdzenie correlation_id
        if config.require_correlation_id:
            if not hasattr(message, 'correlation_id') or not message.correlation_id:
                report.add_error(ValidationError(
                    error_code="REQUIRED_008",
                    error_type="missing_field",
                    field_name="correlation_id",
                    message="Brak correlation_id wiadomosci",
                    severity="error",
                    suggested_fix="Ustaw correlation_id"
                ))
        
        # Sprawdzenie system_state
        if not hasattr(message, 'system_state') or not message.system_state:
            report.add_error(ValidationError(
                error_code="REQUIRED_009",
                error_type="missing_field",
                field_name="system_state",
                message="Brak system_state wiadomosci",
                severity="error",
                suggested_fix="Ustaw system_state (SystemStateSnapshot)"
            ))
    
    def _validate_timestamp(
        self, 
        message: SSIMessage, 
        report: ValidationReport, 
        config: ValidationConfig
    ) -> None:
        """Walidacja timestamp."""
        if not message.timestamp:
            return
        
        current_time = datetime.now()
        
        # Sprawdzenie czy timestamp nie jest w przyszlosci
        if message.timestamp > current_time + timedelta(seconds=30):  # 30 sekund tolerancji
            report.add_warning(ValidationError(
                error_code="TIMESTAMP_001",
                error_type="future_timestamp",
                field_name="timestamp",
                message=f"Timestamp jest z przyszlosci: {message.timestamp.isoformat()}",
                severity="warning",
                suggested_fix="Skontroluj zegar systemowy"
            ))
        
        # Sprawdzenie czy timestamp nie jest za stary
        max_age = timedelta(seconds=config.max_message_age_seconds)
        if message.timestamp < current_time - max_age:
            report.add_error(ValidationError(
                error_code="TIMESTAMP_002",
                error_type="expired_message",
                field_name="timestamp",
                message=f"Wiadomosc jest za stara: {message.timestamp.isoformat()} (max: {config.max_message_age_seconds} seconds)",
                severity="error",
                suggested_fix="Uzyj nowszej wiadomosci lub zwieksz max_message_age_seconds"
            ))
        
        # Sprawdzenie min timestamp
        if config.min_timestamp and message.timestamp < config.min_timestamp:
            report.add_error(ValidationError(
                error_code="TIMESTAMP_003",
                error_type="too_early",
                field_name="timestamp",
                message=f"Timestamp jest za wczesny: {message.timestamp.isoformat()}",
                severity="error"
            ))
        
        # Sprawdzenie max timestamp
        if config.max_timestamp and message.timestamp > config.max_timestamp:
            report.add_error(ValidationError(
                error_code="TIMESTAMP_004",
                error_type="too_late",
                field_name="timestamp",
                message=f"Timestamp jest za pozny: {message.timestamp.isoformat()}",
                severity="error"
            ))
    
    def _validate_source_target(
        self, 
        message: SSIMessage, 
        report: ValidationReport, 
        config: ValidationConfig
    ) -> None:
        """Walidacja source i target."""
        # Sprawdzenie source
        if message.source:
            if isinstance(message.source, str):
                # Powinien byc ModuleIdentifier
                report.add_warning(ValidationError(
                    error_code="SOURCE_001",
                    error_type="wrong_type",
                    field_name="source",
                    message=f"Source powinien byc ModuleIdentifier, jest: {type(message.source)}",
                    severity="warning",
                    suggested_fix="Uzyj ModuleIdentifier zamiast string"
                ))
            elif isinstance(message.source, ModuleIdentifier):
                # Walidacja ModuleIdentifier
                self._validate_module_identifier(message.source, "source", report, config)
        
        # Sprawdzenie target
        if message.target:
            if isinstance(message.target, str):
                report.add_warning(ValidationError(
                    error_code="TARGET_001",
                    error_type="wrong_type",
                    field_name="target",
                    message=f"Target powinien byc ModuleIdentifier, jest: {type(message.target)}",
                    severity="warning",
                    suggested_fix="Uzyj ModuleIdentifier zamiast string"
                ))
            elif isinstance(message.target, ModuleIdentifier):
                self._validate_module_identifier(message.target, "target", report, config)
    
    def _validate_module_identifier(
        self, 
        identifier: ModuleIdentifier, 
        field_name: str,
        report: ValidationReport, 
        config: ValidationConfig
    ) -> None:
        """Walidacja ModuleIdentifier."""
        if not identifier.module_name:
            report.add_error(ValidationError(
                error_code=f"{field_name.upper()}_002",
                error_type="empty_module_name",
                field_name=f"{field_name}.module_name",
                message="Pusta nazwa modulu",
                severity="error"
            ))
        elif not self.MODULE_NAME_PATTERN.match(identifier.module_name):
            report.add_warning(ValidationError(
                error_code=f"{field_name.upper()}_003",
                error_type="invalid_module_name",
                field_name=f"{field_name}.module_name",
                message=f"Nieprawidlowy format nazwy modulu: {identifier.module_name}",
                severity="warning",
                suggested_fix="Nazwa powinna zaczynac sie od litery i zawierac tylko alfanumeryczne znaki i _"
            ))
        
        if identifier.module_type and identifier.module_type not in config.allowed_module_types:
            report.add_warning(ValidationError(
                error_code=f"{field_name.upper()}_004",
                error_type="unknown_module_type",
                field_name=f"{field_name}.module_type",
                message=f"Nieznany typ modulu: {identifier.module_type}",
                severity="warning",
                suggested_fix=f"Uzyj jednego z: {', '.join(config.allowed_module_types)}"
            ))
        
        # Walidacja wersji
        if identifier.version:
            version_pattern = re.compile(r'^\d+\.\d+\.\d+$')
            if not version_pattern.match(identifier.version):
                report.add_warning(ValidationError(
                    error_code=f"{field_name.upper()}_005",
                    error_type="invalid_version",
                    field_name=f"{field_name}.version",
                    message=f"Nieprawidlowy format wersji: {identifier.version}",
                    severity="warning",
                    suggested_fix="Uzyj formatu X.Y.Z (np. 1.0.0)"
                ))
    
    def _validate_system_state(
        self, 
        message: SSIMessage, 
        report: ValidationReport, 
        config: ValidationConfig
    ) -> None:
        """Walidacja system_state."""
        if not message.system_state:
            return
        
        if not isinstance(message.system_state, SystemStateSnapshot):
            report.add_error(ValidationError(
                error_code="SYSTEM_STATE_001",
                error_type="invalid_type",
                field_name="system_state",
                message=f"system_state powinien byc SystemStateSnapshot, jest: {type(message.system_state)}",
                severity="error"
            ))
            return
        
        system_state = message.system_state
        
        # Walidacja timestamp w system_state
        if system_state.timestamp:
            if system_state.timestamp > datetime.now() + timedelta(seconds=30):
                report.add_warning(ValidationError(
                    error_code="SYSTEM_STATE_002",
                    error_type="future_timestamp",
                    field_name="system_state.timestamp",
                    message="System state timestamp jest z przyszlosci",
                    severity="warning"
                ))
        
        # Walidacja system_version
        if system_state.system_version:
            version_pattern = re.compile(r'^\d+\.\d+\.\d+$')
            if not version_pattern.match(system_state.system_version):
                report.add_warning(ValidationError(
                    error_code="SYSTEM_STATE_003",
                    error_type="invalid_version",
                    field_name="system_state.system_version",
                    message=f"Nieprawidlowy format wersji systemu: {system_state.system_version}",
                    severity="warning"
                ))
        
        # Walidacja phase
        if system_state.phase:
            phase_pattern = re.compile(r'^\d+(\.\d+)?$')
            if not phase_pattern.match(system_state.phase):
                report.add_warning(ValidationError(
                    error_code="SYSTEM_STATE_004",
                    error_type="invalid_phase",
                    field_name="system_state.phase",
                    message=f"Nieprawidlowy format fazy: {system_state.phase}",
                    severity="warning"
                ))
    
    def _validate_identifiers(
        self, 
        message: SSIMessage, 
        report: ValidationReport, 
        config: ValidationConfig
    ) -> None:
        """Walidacja identyfikatorow."""
        # session_id
        if message.session_id:
            if message.session_id in self.RESERVED_SESSION_IDS:
                if message.session_id == "default":
                    report.add_warning(ValidationError(
                        error_code="IDENTIFIER_001",
                        error_type="default_session",
                        field_name="session_id",
                        message="Uzyto domyslnego session_id",
                        severity="warning",
                        suggested_fix="Ustaw konkretny session_id"
                    ))
                else:
                    report.add_error(ValidationError(
                        error_code="IDENTIFIER_002",
                        error_type="reserved_session",
                        field_name="session_id",
                        message=f"Zastrzezony session_id: {message.session_id}",
                        severity="error"
                    ))
            elif not self.SESSION_ID_PATTERN.match(message.session_id):
                report.add_warning(ValidationError(
                    error_code="IDENTIFIER_003",
                    error_type="invalid_session_id",
                    field_name="session_id",
                    message=f"Nieprawidlowy format session_id: {message.session_id}",
                    severity="warning"
                ))
        
        # cycle_id
        if message.cycle_id:
            if message.cycle_id in self.RESERVED_CYCLE_IDS:
                if message.cycle_id == "default":
                    report.add_warning(ValidationError(
                        error_code="IDENTIFIER_004",
                        error_type="default_cycle",
                        field_name="cycle_id",
                        message="Uzyto domyslnego cycle_id",
                        severity="warning",
                        suggested_fix="Ustaw konkretny cycle_id"
                    ))
                else:
                    report.add_error(ValidationError(
                        error_code="IDENTIFIER_005",
                        error_type="reserved_cycle",
                        field_name="cycle_id",
                        message=f"Zastrzezony cycle_id: {message.cycle_id}",
                        severity="error"
                    ))
            elif not self.CYCLE_ID_PATTERN.match(message.cycle_id):
                report.add_warning(ValidationError(
                    error_code="IDENTIFIER_006",
                    error_type="invalid_cycle_id",
                    field_name="cycle_id",
                    message=f"Nieprawidlowy format cycle_id: {message.cycle_id}",
                    severity="warning"
                ))
        
        # correlation_id
        if message.correlation_id:
            if not isinstance(message.correlation_id, str) or len(message.correlation_id) < 1:
                report.add_error(ValidationError(
                    error_code="IDENTIFIER_007",
                    error_type="invalid_correlation_id",
                    field_name="correlation_id",
                    message="Nieprawidlowy correlation_id",
                    severity="error"
                ))
    
    def _validate_process_type(
        self, 
        message: SSIMessage, 
        report: ValidationReport, 
        config: ValidationConfig
    ) -> None:
        """Walidacja process_type."""
        if not message.process_type:
            return
        
        # Sprawdzenie czy jest ProcessType
        if isinstance(message.process_type, ProcessType):
            process_type_value = message.process_type.value
        elif isinstance(message.process_type, str):
            process_type_value = message.process_type
        else:
            report.add_error(ValidationError(
                error_code="PROCESS_TYPE_001",
                error_type="invalid_type",
                field_name="process_type",
                message=f"process_type powinien byc ProcessType lub string, jest: {type(message.process_type)}",
                severity="error"
            ))
            return
        
        # Sprawdzenie czy typ jest znany
        all_process_types = {pt.value for pt in ProcessType}
        if config.allowed_process_types:
            allowed = config.allowed_process_types
        else:
            allowed = all_process_types
        
        if process_type_value not in allowed:
            report.add_warning(ValidationError(
                error_code="PROCESS_TYPE_002",
                error_type="unknown_process_type",
                field_name="process_type",
                message=f"Nieznany typ procesu: {process_type_value}",
                severity="warning",
                suggested_fix=f"Uzyj jednego z: {', '.join(sorted(all_process_types))}"
            ))
    
    def _validate_priority(
        self, 
        message: SSIMessage, 
        report: ValidationReport, 
        config: ValidationConfig
    ) -> None:
        """Walidacja priority."""
        if not message.priority:
            # Domyslna wartosc jest OK
            return
        
        # Sprawdzenie czy jest PriorityLevel
        if isinstance(message.priority, PriorityLevel):
            priority_value = message.priority
        elif isinstance(message.priority, int):
            #Akceptujemy rowniez wartosci Clubs
            priority_value = message.priority
        else:
            report.add_warning(ValidationError(
                error_code="PRIORITY_001",
                error_type="wrong_type",
                field_name="priority",
                message=f"priority powinien byc PriorityLevel lub int, jest: {type(message.priority)}",
                severity="warning"
            ))
            return
        
        # Sprawdzenie czy priorytet jest znany
        all_priorities = {str(p.value) for p in PriorityLevel}
        if config.allowed_priority_levels:
            allowed = config.allowed_priority_levels
        else:
            allowed = all_priorities
        
        priority_str = str(priority_value)
        if priority_str not in allowed and priority_value not in allowed:
            report.add_warning(ValidationError(
                error_code="PRIORITY_002",
                error_type="unknown_priority",
                field_name="priority",
                message=f"Nieznany poziom priorytetu: {priority_str}",
                severity="warning",
                suggested_fix=f"Uzyj jednego z: {', '.join(sorted(all_priorities))}"
            ))
    
    def _validate_payload(
        self, 
        message: SSIMessage, 
        report: ValidationReport, 
        config: ValidationConfig
    ) -> None:
        """Walidacja payload."""
        if not message.payload:
            return
        
        if not isinstance(message.payload, dict):
            report.add_error(ValidationError(
                error_code="PAYLOAD_001",
                error_type="invalid_type",
                field_name="payload",
                message=f"payload powinien byc slownikiem, jest: {type(message.payload)}",
                severity="error"
            ))
            return
        
        # Sprawdzenie rozmiaru payload
        try:
            import json
            payload_size = len(json.dumps(message.payload))
            max_size = config.max_payload_size_kb * 1024
            
            if payload_size > max_size:
                report.add_error(ValidationError(
                    error_code="PAYLOAD_002",
                    error_type="too_large",
                    field_name="payload",
                    message=f"Payload jest za duzy: {payload_size} B (max: {max_size} B)",
                    severity="error",
                    suggested_fix=f"Zmniejsz payload lub zwieksz max_payload_size_kb (aktualnie: {config.max_payload_size_kb} KB)"
                ))
        except Exception:
            # Nie mozna oszacowac rozmiaru
            pass
        
        # Sprawdzenie kluczy payload
        for key, value in message.payload.items():
            if not isinstance(key, str):
                report.add_warning(ValidationError(
                    error_code="PAYLOAD_003",
                    error_type="non_string_key",
                    field_name=f"payload.{key}",
                    message=f"Nieprawidlowy typ klucza w payload: {type(key)}",
                    severity="warning"
                ))
    
    def _validate_consistency(
        self, 
        message: SSIMessage, 
        report: ValidationReport, 
        config: ValidationConfig
    ) -> None:
        """Walidacja konsystencji wiadomosci."""
        # Sprawdzenie czy message_id jest unikalny (w obrebie sesji)
        # To bedzie sprawdzane na poziomie systemu, tutaj tylko format
        
        # Sprawdzenie czy correlation_id jest powalezany z message_id
        if (message.correlation_id and 
            message.correlation_id != message.message_id and
            not self.MESSAGE_ID_PATTERN.match(message.correlation_id)):
            report.add_warning(ValidationError(
                error_code="CONSISTENCY_001",
                error_type="correlation_id_mismatch",
                field_name="correlation_id",
                message=f"correlation_id nie jest spójny z message_id: {message.correlation_id}",
                severity="warning"
            ))
        
        # Sprawdzenie czy timestamp wiadomosci jest spójny z system_state
        if (message.timestamp and 
            message.system_state and 
            message.system_state.timestamp and
            abs((message.timestamp - message.system_state.timestamp).total_seconds()) > 60):  # 1 minuta tolerancji
            report.add_warning(ValidationError(
                error_code="CONSISTENCY_002",
                error_type="timestamp_mismatch",
                field_name="timestamp",
                message="Timestamp wiadomosci i system_state sa niezgodne",
                severity="warning",
                suggested_fix="Uzyj tej samej bazy czasowej"
            ))


# Funkcje helper

def get_validator(config: ValidationConfig = None) -> MessageValidator:
    """Pobranie instancji walidatora."""
    return MessageValidator.get_instance(config)


def validate_message(
    message: SSIMessage, 
    config: ValidationConfig = None
) -> ValidationReport:
    """
    Szybka walidacja wiadomosci.
    
    Args:
        message: Wiadomosc do zwalidowania
        config: Konfiguracja walidacji (opcjonalnie)
        
    Returns:
        ValidationReport: Raport z walidacji
    """
    validator = get_validator(config)
    return validator.validate(message, config)


def is_message_valid(
    message: SSIMessage, 
    config: ValidationConfig = None
) -> bool:
    """
    Szybkie sprawdzenie czy wiadomosc jest poprawna.
    
    Args:
        message: Wiadomosc do sprawdzenia
        config: Konfiguracja walidacji (opcjonalnie)
        
    Returns:
        bool: Czy wiadomosc jest poprawna
    """
    return validate_message(message, config).is_valid


def validate_and_fix(
    message: SSIMessage, 
    config: ValidationConfig = None
) -> Tuple[SSIMessage, ValidationReport]:
    """
    Walidacja z automatyczna naprawa (jeśli możliwa).
    
    Args:
        message: Wiadomosc do zwalidowania i naprawy
        config: Konfiguracja walidacji (opcjonalnie)
        
    Returns:
        Tuple[SSIMessage, ValidationReport]: Naprawiona wiadomosc i raport
    """
    report = validate_message(message, config)
    
    # Naprawa (tylko proste przypadki)
    fixed_message = message
    
    if not report.is_valid:
        # Auto-generacja message_id
        if any(e.field_name == "message_id" and e.error_type == "missing_field" for e in report.errors):
            fixed_message = message.clone(message_id=str(uuid.uuid4()))
        
        # Auto-generacja timestamp
        if any(e.field_name == "timestamp" and e.error_type == "missing_field" for e in report.errors):
            fixed_message = fixed_message.clone(timestamp=datetime.now())
        
        # Auto-generacja system_state
        if any(e.field_name == "system_state" and e.error_type == "missing_field" for e in report.errors):
            fixed_message = fixed_message.clone(system_state=SystemStateSnapshot())
    
    return fixed_message, report
