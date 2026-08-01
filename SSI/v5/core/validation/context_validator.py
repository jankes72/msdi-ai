"""
SSI V5 - Context Validator

Modul odpowiedzialny za walidacje kompatybilnosci kontekstu wiadomosci.
Sprawdza spojnosc i kompletnosc danych kontekstowych.

Zasady:
- Brak kontekstu = NIE wykonuj dzialania
- Najpierw: korekta kontekstu -> walidacja -> wykonanie

Wersja: 2.0.0
Data: 2026-08-01
"""

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from SSI.v5.core.information_flow_controller.message_models import (
    SSIMessage,
    SystemStateSnapshot,
    ModuleIdentifier
)
from SSI.v5.core.information_flow_controller.context_manager import (
    ContextManager,
    ContextSnapshot,
    get_context_manager
)

# Konfiguracja logowania
logger = logging.getLogger(__name__)


class ContextValidationLevel(Enum):
    """Poziomy walidacji kontekstu."""
    STRICT = "strict"          # Calkowita walidacja, wszystkie sprawdzenia
    STANDARD = "standard"      # Standardowa walidacja (domyslna)
    BASIC = "basic"            # Podstawowa walidacja
    MINIMAL = "minimal"        # Minimalna walidacja


class ContextValidationResult(Enum):
    """Wynik walidacji kontekstu."""
    COMPLETE = "complete"      # Kontekst komletny i sprawdzony
    PARTIAL = "partial"        # Kontekst czesciowo poprawny (moze byc akceptowalny)
    INCOMPLETE = "incomplete"  # Kontekst niekompletny
    CORRUPTED = "corrupted"    # Kontekst uszkodzony lub niespójny
    INVALID = "invalid"        # Kontekst niewazny


@dataclass
class ContextValidationError:
    """Blad walidacji kontekstu."""
    error_code: str
    error_type: str
    context_field: str
    message: str
    severity: str = "error"  # error, warning, critical
    suggested_fix: Optional[str] = None
    expected_value: Optional[Any] = None
    actual_value: Optional[Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        return {
            'error_code': self.error_code,
            'error_type': self.error_type,
            'context_field': self.context_field,
            'message': self.message,
            'severity': self.severity,
            'suggested_fix': self.suggested_fix,
            'expected_value': self.expected_value,
            'actual_value': self.actual_value
        }
    
    def __str__(self) -> str:
        return f"[{self.error_code}] {self.context_field}: {self.message}"


@dataclass
class ContextValidationReport:
    """Raport z walidacji kontekstu."""
    message_id: str
    session_id: Optional[str] = None
    cycle_id: Optional[str] = None
    correlation_id: Optional[str] = None
    
    is_complete: bool = True
    validation_level: ContextValidationLevel = ContextValidationLevel.STANDARD
    result: ContextValidationResult = ContextValidationResult.COMPLETE
    
    errors: List[ContextValidationError] = field(default_factory=list)
    warnings: List[ContextValidationError] = field(default_factory=list)
    
    context_score: float = 1.0  # 0.0 - 1.0, ocena kompletnosci kontekstu
    processing_time_ms: float = 0.0
    validated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        return {
            'message_id': self.message_id,
            'session_id': self.session_id,
            'cycle_id': self.cycle_id,
            'correlation_id': self.correlation_id,
            'is_complete': self.is_complete,
            'validation_level': self.validation_level.value,
            'result': self.result.value,
            'context_score': self.context_score,
            'errors': [e.to_dict() for e in self.errors],
            'warnings': [w.to_dict() for w in self.warnings],
            'processing_time_ms': self.processing_time_ms,
            'validated_at': self.validated_at.isoformat(),
            'error_count': len(self.errors),
            'warning_count': len(self.warnings)
        }
    
    def add_error(self, error: ContextValidationError) -> None:
        """Dodanie bledy do raportu."""
        self.errors.append(error)
        self.is_complete = False
        if error.severity == "critical":
            self.result = ContextValidationResult.CORRUPTED
        elif self.result != ContextValidationResult.CORRUPTED:
            self.result = ContextValidationResult.INCOMPLETE
        
        # Aktualizacja context_score
        self._update_score()
    
    def add_warning(self, warning: ContextValidationError) -> None:
        """Dodanie ostrzezenia do raportu."""
        self.warnings.append(warning)
        if self.result == ContextValidationResult.COMPLETE:
            self.result = ContextValidationResult.PARTIAL
        
        # Aktualizacja context-score
        self._update_score()
    
    def _update_score(self) -> None:
        """Aktualizacja oceny kontekstu."""
        error_penalty = len(self.errors) * 0.2
        warning_penalty = len(self.warnings) * 0.05
        self.context_score = max(0.0, 1.0 - error_penalty - warning_penalty)
    
    def get_critical_errors(self) -> List[ContextValidationError]:
        """Pobranie krytycznych bledow."""
        return [e for e in self.errors if e.severity == "critical"]
    
    def get_error_messages(self) -> List[str]:
        """Pobranie listy komunikatow o bledach."""
        return [str(e) for e in self.errors]
    
    def get_warning_messages(self) -> List[str]:
        """Pobranie listy ostrzezen."""
        return [str(w) for w in self.warnings]
    
    def __str__(self) -> str:
        status = "COMPLETE" if self.is_complete else self.result.value.upper()
        return f"ContextValidationReport({self.message_id}): {status} | Score: {self.context_score:.2f} | Errors: {len(self.errors)} | Warnings: {len(self.warnings)}"


@dataclass
class ContextValidationConfig:
    """Konfiguracja walidatora kontekstu."""
    # Poziom walidacji
    validation_level: ContextValidationLevel = ContextValidationLevel.STANDARD
    
    # Wymagania dla sesji
    require_session_id: bool = True
    require_active_session: bool = True
    max_session_age_seconds: int = 86400  # 24 godziny
    
    # Wymagania dla cyklu
    require_cycle_id: bool = True
    require_active_cycle: bool = True
    max_cycle_age_seconds: int = 3600  # 1 godzina
    
    # Wymagania dla agenta
    require_active_agent: bool = False  # Opcjonalnie
    require_active_model: bool = False   # Opcjonalnie
    
    # Sprawdzanie spójnosci
    check_session_cycle_consistency: bool = True
    check_context_state_sync: bool = True
    check_correlation_chain: bool = True
    
    # Dopuszczalne wartosci
    allowed_session_prefixes: Set[str] = field(default_factory=lambda: {"session", "user", "agent", "system"})
    allowed_cycle_prefixes: Set[str] = field(default_factory=lambda: {"cycle", "iteration", "phase", "step"})
    
    # Zasady walidacji
    strict_mode: bool = False
    auto_correct: bool = True  # Czy próbowac automatycznie korekcje
    
    @classmethod
    def strict(cls) -> 'ContextValidationConfig':
        """Konfiguracja strict."""
        return cls(
            validation_level=ContextValidationLevel.STRICT,
            strict_mode=True,
            auto_correct=False,
            require_session_id=True,
            require_cycle_id=True,
            require_active_session=True,
            require_active_cycle=True,
            check_session_cycle_consistency=True,
            check_context_state_sync=True,
            check_correlation_chain=True
        )
    
    @classmethod
    def minimal(cls) -> 'ContextValidationConfig':
        """Konfiguracja minimalna."""
        return cls(
            validation_level=ContextValidationLevel.MINIMAL,
            strict_mode=False,
            auto_correct=True,
            require_session_id=False,
            require_cycle_id=False,
            check_session_cycle_consistency=False
        )


class ContextValidator:
    """
    Walidator kontekstu wiadomosci SSIMessage.
    
    Odpowiedzialnosc:
    - Sprawdzanie kompletnosci kontekstu
    - Wykrywanie utraty informacji
    - Kontrola zgodnosci system_state
    - Kontrola session_id
    - Kontrola cycle_id
    - Kontrola active_agent
    - Kontrola active_model
    - Wspólpraca z Dynamic Context Correction
    
    Zasady:
    1. Brak kontekstu = NIE wykonuj dzialania
    2. Najpierw: korekta kontekstu -> walidacja -> wykonanie
    """
    
    def __init__(self, config: ContextValidationConfig = None):
        """
        Inicjalizacja walidatora kontekutu.
        
        Args:
            config: Konfiguracja walidatora (opcjonalnie)
        """
        self.config = config or ContextValidationConfig()
        self._context_manager: Optional[ContextManager] = None
        self._validation_hooks: List[Callable[[SSIMessage, ContextValidationReport], None]] = []
        self._lock = threading.RLock()
        self._initialized = False
        
        self._initialize()
        logger.info(f"ContextValidator zainicjalizowany z poziomem walidacji: {self.config.validation_level.value}")
    
    def _initialize(self) -> None:
        """Inicjalizacja walidatora."""
        if self._initialized:
            return
        
        # Pobranie context manager
        try:
            self._context_manager = get_context_manager()
            logger.debug("ContextValidator polaczony z ContextManager")
        except Exception as e:
            logger.warning(f"Nie mozna polaczyc z ContextManager: {e}")
        
        self._initialized = True
    
    @classmethod
    def get_instance(cls, config: ContextValidationConfig = None) -> 'ContextValidator':
        """Pobranie instancji walidatora (singleton)."""
        if not hasattr(cls, '_instance'):
            cls._instance = cls(config)
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset instancji singleton."""
        if hasattr(cls, '_instance'):
            del cls._instance
    
    def set_config(self, config: ContextValidationConfig) -> None:
        """Ustawienie konfiguracji walidatora."""
        self.config = config
        logger.info(f"Zmieniono konfiguracje ContextValidator na: {config.validation_level.value}")
    
    def set_context_manager(self, context_manager: ContextManager) -> None:
        """Ustawienie ContextManager."""
        self._context_manager = context_manager
        logger.info("ContextValidator: ustawiono ContextManager")
    
    def register_validation_hook(
        self, 
        hook: Callable[[SSIMessage, ContextValidationReport], None]
    ) -> None:
        """Rejestracja hooka walidacyjnego."""
        self._validation_hooks.append(hook)
        logger.debug(f"Zarejestrowano context validation hook: {hook.__name__}")
    
    def validate(
        self, 
        message: SSIMessage, 
        config: ContextValidationConfig = None
    ) -> ContextValidationReport:
        """
        Glowna metoda walidacji kontekstu wiadomosci.
        
        Args:
            message: Wiadomosc do zwalidowania
            config: Konfiguracja walidacji (opcjonalnie, nadpisuje domyslna)
            
        Returns:
            ContextValidationReport: Raport z walidacji kontekstu
        """
        import time
        start_time = time.time()
        
        # Uzycie konfiguracji podanej lub domyslnej
        validation_config = config or self.config
        
        # Utworzenie raportu
        report = ContextValidationReport(
            message_id=message.message_id,
            session_id=message.session_id,
            cycle_id=message.cycle_id,
            correlation_id=message.correlation_id,
            validation_level=validation_config.validation_level,
            is_complete=True
        )
        
        try:
            with self._lock:
                # Walidacja sesji
                if validation_config.validation_level in [ContextValidationLevel.STRICT, ContextValidationLevel.STANDARD]:
                    self._validate_session(message, report, validation_config)
                
                # Walidacja cyklu
                if validation_config.validation_level in [ContextValidationLevel.STRICT, ContextValidationLevel.STANDARD]:
                    self._validate_cycle(message, report, validation_config)
                
                # Walidacja powiazania sesja-cykl
                if validation_config.validation_level in [ContextValidationLevel.STRICT, ContextValidationLevel.STANDARD]:
                    self._validate_session_cycle_consistency(message, report, validation_config)
                
                # Walidacja system_state
                if validation_config.validation_level in [ContextValidationLevel.STRICT, ContextValidationLevel.STANDARD, ContextValidationLevel.BASIC]:
                    self._validate_system_state(message, report, validation_config)
                
                # Walidacja active_agent i active_model
                if validation_config.validation_level in [ContextValidationLevel.STRICT, ContextValidationLevel.STANDARD]:
                    self._validate_active_components(message, report, validation_config)
                
                # Walidacja correlation
                if validation_config.validation_level in [ContextValidationLevel.STRICT, ContextValidationLevel.STANDARD]:
                    self._validate_correlation(message, report, validation_config)
                
                # Walidacja spójnosci czasowej
                if validation_config.validation_level == ContextValidationLevel.STRICT:
                    self._validate_temporal_consistency(message, report, validation_config)
                
                # Wywolanie hookow
                for hook in self._validation_hooks:
                    try:
                        hook(message, report)
                    except Exception as e:
                        report.add_error(ContextValidationError(
                            error_code="HOOK_ERROR",
                            error_type="validation_hook_failed",
                            context_field="hooks",
                            message=f"Hook walidacyjny zaliczony: {e}",
                            severity="warning"
                        ))
        except Exception as e:
            report.add_error(ContextValidationError(
                error_code="CONTEXT_VALIDATION_ERROR",
                error_type="unexpected_error",
                context_field="context",
                message=f"Nieoczekiwany blad podczas walidacji kontekstu: {e}",
                severity="critical"
            ))
        
        # Czas przetwarzania
        report.processing_time_ms = (time.time() - start_time) * 1000
        
        # Logowanie
        if report.is_complete:
            logger.debug(f"Walidacja kontekstu powiodla sie: {message.message_id}")
        elif report.result == ContextValidationResult.CORRUPTED:
            logger.error(f"Krytyczny blad walidacji kontekstu: {message.message_id} - {report.get_error_messages()}")
        elif report.result == ContextValidationResult.INCOMPLETE:
            logger.warning(f"Walidacja kontekstu nie powiodla sie: {message.message_id} - {report.get_error_messages()}")
        else:
            logger.info(f"Walidacja kontekstu z ostrzezeniami: {message.message_id} - {report.get_warning_messages()}")
        
        return report
    
    def is_context_complete(self, message: SSIMessage) -> bool:
        """
        Szybka walidacja - zwraca True/False.
        
        Args:
            message: Wiadomosc do zwalidowania
            
        Returns:
            bool: Czy kontekst jest komletny
        """
        return self.validate(message).is_complete
    
    def get_context_score(self, message: SSIMessage) -> float:
        """
        Pobranie oceny kompletnosci kontekstu.
        
        Args:
            message: Wiadomosc do oceny
            
        Returns:
            float: Ocena kompletnosci (0.0 - 1.0)
        """
        return self.validate(message).context_score
    
    def detect_context_loss(
        self, 
        message: SSIMessage, 
        previous_message: Optional[SSIMessage] = None
    ) -> List[ContextValidationError]:
        """
        Wykrywanie utraty informacji kontekstowych.
        
        Args:
            message: Aktualna wiadomosc
            previous_message: Poprzednia wiadomosc (opcjonalnie)
            
        Returns:
            List[ContextValidationError]: Lista wykrytych problemów
        """
        errors = []
        
        # Sprawdzenie czy session_id zostal utracony
        if message.session_id == "default" or not message.session_id:
            errors.append(ContextValidationError(
                error_code="CTX_LOSS_001",
                error_type="session_loss",
                context_field="session_id",
                message="Utracono informacje o sesji",
                severity="error",
                suggested_fix="Ustaw poprawny session_id"
            ))
        
        # Sprawdzenie czy cycle_id zostal utracony
        if message.cycle_id == "default" or not message.cycle_id:
            errors.append(ContextValidationError(
                error_code="CTX_LOSS_002",
                error_type="cycle_loss",
                context_field="cycle_id",
                message="Utracono informacje o cykli",
                severity="error",
                suggested_fix="Ustaw poprawny cycle_id"
            ))
        
        # Porównanie z poprzednia wiadomoscia (jeśli dostepna)
        if previous_message:
            if (previous_message.session_id != message.session_id and 
                previous_message.session_id != "default"):
                errors.append(ContextValidationError(
                    error_code="CTX_LOSS_003",
                    error_type="session_change",
                    context_field="session_id",
                    message=f"Zmiana sesji z {previous_message.session_id} na {message.session_id}",
                    severity="warning",
                    expected_value=previous_message.session_id,
                    actual_value=message.session_id
                ))
            
            if (previous_message.cycle_id != message.cycle_id and 
                previous_message.cycle_id != "default"):
                errors.append(ContextValidationError(
                    error_code="CTX_LOSS_004",
                    error_type="cycle_change",
                    context_field="cycle_id",
                    message=f"Zmiana cyklu z {previous_message.cycle_id} na {message.cycle_id}",
                    severity="warning",
                    expected_value=previous_message.cycle_id,
                    actual_value=message.cycle_id
                ))
        
        return errors
    
    def _validate_session(
        self, 
        message: SSIMessage, 
        report: ContextValidationReport, 
        config: ContextValidationConfig
    ) -> None:
        """Walidacja sesji."""
        # Sprawdzenie wymaganego session_id
        if not message.session_id:
            if config.require_session_id:
                report.add_error(ContextValidationError(
                    error_code="SESSION_001",
                    error_type="missing_session_id",
                    context_field="session_id",
                    message="Brak identyfikatora sesji",
                    severity="error",
                    suggested_fix="Ustaw session_id"
                ))
            return
        
        # Sprawdzenie czy sesja nie jest zastrzezona
        if message.session_id == "default":
            report.add_warning(ContextValidationError(
                error_code="SESSION_002",
                error_type="default_session",
                context_field="session_id",
                message="Uzyto domyslnego identyfikatora sesji",
                severity="warning",
                suggested_fix="Ustaw konkretny session_id"
            ))
        
        # Sprawdzenie prefiksu sesji
        if config.allowed_session_prefixes:
            has_valid_prefix = any(
                message.session_id.startswith(prefix + "_") or 
                message.session_id == prefix
                for prefix in config.allowed_session_prefixes
            )
            if not has_valid_prefix:
                report.add_warning(ContextValidationError(
                    error_code="SESSION_003",
                    error_type="invalid_prefix",
                    context_field="session_id",
                    message=f"Nieprawidlowy prefiks sesji: {message.session_id}",
                    severity="warning",
                    suggested_fix=f"Uzyj jednego z prefiksów: {', '.join(config.allowed_session_prefixes)}"
                ))
        
        # Sprawdzenie aktywnej sesji
        if config.require_active_session and self._context_manager:
            try:
                current_context = self._context_manager.get_context()
                if (current_context.session_id and 
                    current_context.session_id != message.session_id):
                    report.add_warning(ContextValidationError(
                        error_code="SESSION_004",
                        error_type="session_mismatch",
                        context_field="session_id",
                        message=f"Sesja wiadomosci ({message.session_id}) nie zgadza sie z aktywna sesja ({current_context.session_id})",
                        severity="warning",
                        expected_value=current_context.session_id,
                        actual_value=message.session_id
                    ))
            except Exception as e:
                logger.debug(f"Nie mozna sprawdzic aktywnej sesji: {e}")
        
        # Sprawdzenie czy sesja nie jest za stara (jeśli dostepny timestamp)
        if message.system_state and message.system_state.timestamp:
            max_age = timedelta(seconds=config.max_session_age_seconds)
            current_time = datetime.now()
            if message.system_state.timestamp < current_time - max_age:
                report.add_warning(ContextValidationError(
                    error_code="SESSION_005",
                    error_type="expired_session",
                    context_field="session_id",
                    message=f"Sesja jest za stara: system_state.timestamp = {message.system_state.timestamp.isoformat()}",
                    severity="warning",
                    suggested_fix="Uzyj nowszej sesji"
                ))
    
    def _validate_cycle(
        self, 
        message: SSIMessage, 
        report: ContextValidationReport, 
        config: ContextValidationConfig
    ) -> None:
        """Walidacja cyklu."""
        # Sprawdzenie wymaganego cycle_id
        if not message.cycle_id:
            if config.require_cycle_id:
                report.add_error(ContextValidationError(
                    error_code="CYCLE_001",
                    error_type="missing_cycle_id",
                    context_field="cycle_id",
                    message="Brak identyfikatora cyklu",
                    severity="error",
                    suggested_fix="Ustaw cycle_id"
                ))
            return
        
        # Sprawdzenie czy cykl nie jest zastrzezony
        if message.cycle_id == "default":
            report.add_warning(ContextValidationError(
                error_code="CYCLE_002",
                error_type="default_cycle",
                context_field="cycle_id",
                message="Uzyto domyslnego identyfikatora cyklu",
                severity="warning",
                suggested_fix="Ustaw konkretny cycle_id"
            ))
        
        # Sprawdzenie prefiksu cyklu
        if config.allowed_cycle_prefixes:
            has_valid_prefix = any(
                message.cycle_id.startswith(prefix + "_") or 
                message.cycle_id == prefix
                for prefix in config.allowed_cycle_prefixes
            )
            if not has_valid_prefix:
                report.add_warning(ContextValidationError(
                    error_code="CYCLE_003",
                    error_type="invalid_prefix",
                    context_field="cycle_id",
                    message=f"Nieprawidlowy prefiks cyklu: {message.cycle_id}",
                    severity="warning",
                    suggested_fix=f"Uzyj jednego z prefiksów: {', '.join(config.allowed_cycle_prefixes)}"
                ))
        
        # Sprawdzenie aktywnego cyklu
        if config.require_active_cycle and self._context_manager:
            try:
                current_context = self._context_manager.get_context()
                if (current_context.cycle_id and 
                    current_context.cycle_id != message.cycle_id):
                    report.add_warning(ContextValidationError(
                        error_code="CYCLE_004",
                        error_type="cycle_mismatch",
                        context_field="cycle_id",
                        message=f"Cykl wiadomosci ({message.cycle_id}) nie zgadza sie z aktywnym cyklem ({current_context.cycle_id})",
                        severity="warning",
                        expected_value=current_context.cycle_id,
                        actual_value=message.cycle_id
                    ))
            except Exception as e:
                logger.debug(f"Nie mozna sprawdzic aktywnego cyklu: {e}")
        
        # Sprawdzenie czy cykl nie jest za stary
        if message.system_state and message.system_state.timestamp:
            max_age = timedelta(seconds=config.max_cycle_age_seconds)
            current_time = datetime.now()
            if message.system_state.timestamp < current_time - max_age:
                report.add_error(ContextValidationError(
                    error_code="CYCLE_005",
                    error_type="expired_cycle",
                    context_field="cycle_id",
                    message=f"Cykl jest za stary: system_state.timestamp = {message.system_state.timestamp.isoformat()}",
                    severity="error",
                    suggested_fix="Rozpocznij nowy cykl"
                ))
    
    def _validate_session_cycle_consistency(
        self, 
        message: SSIMessage, 
        report: ContextValidationReport, 
        config: ContextValidationConfig
    ) -> None:
        """Walidacja spójnosci sesja-cykl."""
        if not config.check_session_cycle_consistency:
            return
        
        # Sesja i cykl powinny byc powiazane semanty藏
        # Na bazie nazwy moga zawierac te same elementy
        if message.session_id and message.session_id != "default":
            if message.cycle_id and message.cycle_id != "default":
                # Sprawdzenie czy cycle_id zawiera czesc session_id lub vice versa
                session_parts = message.session_id.split("_")
                cycle_parts = message.cycle_id.split("_")
                
                common_parts = set(session_parts) & set(cycle_parts)
                if not common_parts and not any(p in message.cycle_id for p in session_parts):
                    report.add_warning(ContextValidationError(
                        error_code="CONSISTENCY_001",
                        error_type="session_cycle_mismatch",
                        context_field="session_cycle",
                        message=f"Brak powiazania miedzy sesja ({message.session_id}) a cyklem ({message.cycle_id})",
                        severity="warning",
                        suggested_fix="Uzyj spójnych identyfikatorów sesji i cyklu"
                    ))
    
    def _validate_system_state(
        self, 
        message: SSIMessage, 
        report: ContextValidationReport, 
        config: ContextValidationConfig
    ) -> None:
        """Walidacja system_state."""
        if not message.system_state:
            report.add_error(ContextValidationError(
                error_code="SYSTEM_STATE_001",
                error_type="missing_system_state",
                context_field="system_state",
                message="Brak stanu systemu w wiadomosci",
                severity="error",
                suggested_fix="Ustaw system_state"
            ))
            return
        
        system_state = message.system_state
        
        # Sprawdzenie co najmniej podstawowych pol
        if not system_state.system_version:
            report.add_warning(ContextValidationError(
                error_code="SYSTEM_STATE_002",
                error_type="missing_system_version",
                context_field="system_state.system_version",
                message="Brak wersji systemu w system_state",
                severity="warning",
                suggested_fix="Ustaw system_version"
            ))
        
        if not system_state.phase:
            report.add_warning(ContextValidationError(
                error_code="SYSTEM_STATE_003",
                error_type="missing_phase",
                context_field="system_state.phase",
                message="Brak fazy w system_state",
                severity="warning",
                suggested_fix="Ustaw phase"
            ))
        
        # Sprawdzenie zgodnosci z aktualnym stanem systemu
        if config.check_context_state_sync and self._context_manager:
            try:
                current_system_state = self._context_manager.get_system_state()
                if current_system_state:
                    # Porównanie wersji
                    if (current_system_state.system_version and 
                        system_state.system_version and
                        current_system_state.system_version != system_state.system_version):
                        report.add_warning(ContextValidationError(
                            error_code="SYSTEM_STATE_004",
                            error_type="version_mismatch",
                            context_field="system_state.system_version",
                            message=f"Wersja systemu w wiadomosci ({system_state.system_version}) nie zgadza sie z aktualna ({current_system_state.system_version})",
                            severity="warning",
                            expected_value=current_system_state.system_version,
                            actual_value=system_state.system_version
                        ))
            except Exception as e:
                logger.debug(f"Nie mozna sprawdzic stanu systemu: {e}")
        
        # Sprawdzenie active_model (tylko jeden model LLM naraz)
        if system_state.active_model:
            # To bedzie sprawdzane na poziomie Runtime Controller
            pass
    
    def _validate_active_components(
        self, 
        message: SSIMessage, 
        report: ContextValidationReport, 
        config: ContextValidationConfig
    ) -> None:
        """Walidacja aktywnych komponentow."""
        # Sprawdzenie active_agent (jeśli wymagane)
        if config.require_active_agent:
            if (message.system_state and 
                not message.system_state.active_model):
                report.add_warning(ContextValidationError(
                    error_code="AGENT_001",
                    error_type="missing_active_agent",
                    context_field="system_state.active_agent",
                    message="Brak aktywnego agenta w system_state",
                    severity="warning"
                ))
        
        # Sprawdzenie active_model (tylko jeden model LLM naraz)
        if config.require_active_model:
            if (message.system_state and 
                not message.system_state.active_model):
                report.add_warning(ContextValidationError(
                    error_code="MODEL_001",
                    error_type="missing_active_model",
                    context_field="system_state.active_model",
                    message="Brak aktywnego modelu w system_state",
                    severity="warning"
                ))
        
        # Sprawdzenie czy tylko jeden model jest aktywny
        if (message.system_state and 
            message.system_state.active_model and
            message.system_state.models_in_queue > 0):
            report.add_warning(ContextValidationError(
                error_code="MODEL_002",
                error_type="multiple_models",
                context_field="system_state",
                message=f"Aktywny model: {message.system_state.active_model}, ale modeli w kolejce: {message.system_state.models_in_queue}",
                severity="warning",
                suggested_fix="Zachowaj zasade: TYLKO JEDEN MODEL LLM AKTYWNY W DANYM MOMENCIE"
            ))
    
    def _validate_correlation(
        self, 
        message: SSIMessage, 
        report: ContextValidationReport, 
        config: ContextValidationConfig
    ) -> None:
        """Walidacja korelacji."""
        if not message.correlation_id:
            report.add_warning(ContextValidationError(
                error_code="CORRELATION_001",
                error_type="missing_correlation_id",
                context_field="correlation_id",
                message="Brak identyfikatora korelacji",
                severity="warning",
                suggested_fix="Ustaw correlation_id (np. pokrywający z message_id)"
            ))
            return
        
        # Sprawdzenie czy correlation_id jest spójny
        if message.correlation_id != message.message_id:
            # To jest OK - correlation_id moze byc roznY od message_id
            # dla lancuchow wiadomosci
            pass
    
    def _validate_temporal_consistency(
        self, 
        message: SSIMessage, 
        report: ContextValidationReport, 
        config: ContextValidationConfig
    ) -> None:
        """Walidacja spójnosci czasowej."""
        # Sprawdzenie czy timestamp wiadomosci jest spójny z system_state
        if (message.timestamp and 
            message.system_state and 
            message.system_state.timestamp):
            time_diff = abs((message.timestamp - message.system_state.timestamp).total_seconds())
            if time_diff > 60:  # 1 minuta tolerancji
                report.add_warning(ContextValidationError(
                    error_code="TEMPORAL_001",
                    error_type="timestamp_mismatch",
                    context_field="timestamp",
                    message=f"Roznica czasowa miedzy wiadomoscia a system_state: {time_diff}s",
                    severity="warning",
                    suggested_fix="Uzyj tej samej bazy czasowej"
                ))


# Funkcje helper

def get_context_validator(config: ContextValidationConfig = None) -> ContextValidator:
    """Pobranie instancji walidatora kontekstu."""
    return ContextValidator.get_instance(config)


def validate_context(
    message: SSIMessage, 
    config: ContextValidationConfig = None
) -> ContextValidationReport:
    """
    Szybka walidacja kontekstu wiadomosci.
    
    Args:
        message: Wiadomosc do zwalidowania
        config: Konfiguracja walidacji (opcjonalnie)
        
    Returns:
        ContextValidationReport: Raport z walidacji kontekstu
    """
    validator = get_context_validator(config)
    return validator.validate(message, config)


def is_context_complete(
    message: SSIMessage, 
    config: ContextValidationConfig = None
) -> bool:
    """
    Szybkie sprawdzenie czy kontekst jest komletny.
    
    Args:
        message: Wiadomosc do sprawdzenia
        config: Konfiguracja walidacji (opcjonalnie)
        
    Returns:
        bool: Czy kontekst jest komletny
    """
    return validate_context(message, config).is_complete


def detect_context_loss(
    message: SSIMessage, 
    previous_message: Optional[SSIMessage] = None
) -> List[ContextValidationError]:
    """
    Wykrywanie utraty informacji kontekstowych.
    
    Args:
        message: Aktualna wiadomosc
        previous_message: Poprzednia wiadomosc (opcjonalnie)
        
    Returns:
        List[ContextValidationError]: Lista wykrytych problemów
    """
    validator = get_context_validator()
    return validator.detect_context_loss(message, previous_message)
