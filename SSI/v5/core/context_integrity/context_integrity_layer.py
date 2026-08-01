"""
SSI V5 - Context Integrity Layer

Glowny modul warstwy integralnosci kontekstu.
Laczy wszystkie elementy zwiazane z zapewnieniem spójnosci i poprawnosci kontekstu.

Zasady:
- Brak kontekstu = NIE wykonuj dzialania
- Najpierw: korekta kontekstu -> walidacja -> wykonanie

Wersja: 2.0.0
Data: 2026-08-01
"""

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from SSI.v5.core.information_flow_controller.message_models import (
    SSIMessage,
    SystemStateSnapshot,
    ProcessType,
    PriorityLevel
)
from SSI.v5.core.information_flow_controller.context_manager import (
    ContextManager,
    ContextSnapshot,
    get_context_manager
)

from SSI.v5.core.validation.message_validator import (
    MessageValidator,
    ValidationConfig,
    ValidationReport,
    ValidationLevel
)
from SSI.v5.core.validation.context_validator import (
    ContextValidator,
    ContextValidationConfig,
    ContextValidationReport,
    ContextValidationLevel
)
from SSI.v5.core.context_integrity.dynamic_context_correction import (
    DynamicContextCorrection,
    CorrectionConfig,
    CorrectionResult,
    CorrectionAction,
    CorrectionStrategy
)

# Konfiguracja logowania
logger = logging.getLogger(__name__)


class IntegrityCheckLevel(Enum):
    """Poziomy sprawdzania integralnosci."""
    STRICT = "strict"          # Calkowite sprawdzanie
    STANDARD = "standard"      # Standardowe sprawdzanie (domyslne)
    BASIC = "basic"            # Podstawowe sprawdzanie
    MINIMAL = "minimal"        # Minimalne sprawdzanie


class IntegrityStatus(Enum):
    """Status integralnosci."""
    COMPLETE = "complete"      # Pelna integralnosc
    PARTIAL = "partial"        # Czescowa integralnosc (moze byc akceptowalne)
    INCOMPLETE = "incomplete"  # Niekompletna integralnosc
    CORRUPTED = "corrupted"    # Uszkodzona integralnosc
    CRITICAL = "critical"      # Krytyczny problem z integralnoscia


@dataclass
class IntegrityCheckResult:
    """Wynik sprawdzania integralnosci."""
    message_id: str
    is_integral: bool = True
    check_level: IntegrityCheckLevel = IntegrityCheckLevel.STANDARD
    status: IntegrityStatus = IntegrityStatus.COMPLETE
    
    # Wyniki poszczególnych sprawdzen
    message_validation: Optional[ValidationReport] = None
    context_validation: Optional[ContextValidationReport] = None
    correction_result: Optional[CorrectionResult] = None
    
    # Zagregowane informacje
    errors: List[Any] = field(default_factory=list)
    warnings: List[Any] = field(default_factory=list)
    integrity_score: float = 1.0  # 0.0 - 1.0, ocena integralnosci
    
    processing_time_ms: float = 0.0
    checked_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        return {
            'message_id': self.message_id,
            'is_integral': self.is_integral,
            'check_level': self.check_level.value,
            'status': self.status.value,
            'integrity_score': self.integrity_score,
            'errors_count': len(self.errors),
            'warnings_count': len(self.warnings),
            'processing_time_ms': self.processing_time_ms,
            'checked_at': self.checked_at.isoformat(),
            'message_validation': self.message_validation.to_dict() if self.message_validation else None,
            'context_validation': self.context_validation.to_dict() if self.context_validation else None,
            'correction_result': self.correction_result.to_dict() if self.correction_result else None
        }
    
    def get_error_messages(self) -> List[str]:
        """Pobranie listy komunikatow o bledach."""
        error_messages = []
        
        if self.message_validation:
            error_messages.extend(self.message_validation.get_error_messages())
        
        if self.context_validation:
            error_messages.extend(self.context_validation.get_error_messages())
        
        return error_messages
    
    def get_warning_messages(self) -> List[str]:
        """Pobranie listy ostrzezen."""
        warning_messages = []
        
        if self.message_validation:
            warning_messages.extend(self.message_validation.get_warning_messages())
        
        if self.context_validation:
            warning_messages.extend(self.context_validation.get_warning_messages())
        
        return warning_messages
    
    def __str__(self) -> str:
        status = "INTEGRAL" if self.is_integral else self.status.value.upper()
        return f"IntegrityCheckResult({self.message_id}): {status} | Score: {self.integrity_score:.2f}"


@dataclass
class IntegrityConfig:
    """Konfiguracja warstwy integralnosci."""
    # Poziom sprawdzania
    check_level: IntegrityCheckLevel = IntegrityCheckLevel.STANDARD
    
    # Konfiguracje podsystemów
    validation_config: Optional[ValidationConfig] = None
    context_validation_config: Optional[ContextValidationConfig] = None
    correction_config: Optional[CorrectionConfig] = None
    
    # Opije sprawdzania
    enable_message_validation: bool = True
    enable_context_validation: bool = True
    enable_context_correction: bool = True
    
    # Zasady
    strict_mode: bool = False  # Czy przerwac przy pierwszym bledzie
    reject_corrupted: bool = True  # Czy odrzucac uszkodzone wiadomosci
    
    @classmethod
    def strict(cls) -> 'IntegrityConfig':
        """Konfiguracja strict."""
        return cls(
            check_level=IntegrityCheckLevel.STRICT,
            strict_mode=True,
            reject_corrupted=True,
            enable_message_validation=True,
            enable_context_validation=True,
            enable_context_correction=True
        )
    
    @classmethod
    def minimal(cls) -> 'IntegrityConfig':
        """Konfiguracja minimalna."""
        return cls(
            check_level=IntegrityCheckLevel.MINIMAL,
            strict_mode=False,
            reject_corrupted=False,
            enable_message_validation=True,
            enable_context_validation=False,
            enable_context_correction=True
        )


class ContextIntegrityLayer:
    """
    Glowna warstwa integralnosci kontekstu.
    
    Odpowiedzialnosc:
    - Zachowanie ogólnej integralnosci systemu
    - Koordynacja miedzy: Message Validator, Context Validator, Dynamic Context Correction
    - Zapewnienie spójnosci i poprawnosci kontekstu
    - Obsluga bledów integralnosci
    
    Zasady:
    1. Brak kontekstu = NIE wykonuj dzialania
    2. Najpierw: korekta kontekstu -> walidacja -> wykonanie
    3. Wszystko przez IFC
    """
    
    def __init__(self, config: IntegrityConfig = None):
        """
        Inicjalizacja warstwy integralnosci.
        
        Args:
            config: Konfiguracja warstwy (opcjonalnie)
        """
        self.config = config or IntegrityConfig()
        self._message_validator: Optional[MessageValidator] = None
        self._context_validator: Optional[ContextValidator] = None
        self._context_corrector: Optional[DynamicContextCorrection] = None
        self._context_manager: Optional[ContextManager] = None
        
        self._check_hooks: List[Callable[[SSIMessage, IntegrityCheckResult], None]] = []
        self._lock = threading.RLock()
        self._initialized = False
        
        self._initialize()
        logger.info(f"ContextIntegrityLayer zainicjalizowany z poziomem: {self.config.check_level.value}")
    
    def _initialize(self) -> None:
        """Inicjalizacja warstwy."""
        if self._initialized:
            return
        
        # Inicjalizacja podsystemów
        try:
            self._message_validator = MessageValidator(self.config.validation_config)
            logger.debug("ContextIntegrityLayer: MessageValidator zainicjalizowany")
        except Exception as e:
            logger.error(f"Blad podczas inicjalizacji MessageValidator: {e}")
        
        try:
            self._context_validator = ContextValidator(self.config.context_validation_config)
            logger.debug("ContextIntegrityLayer: ContextValidator zainicjalizowany")
        except Exception as e:
            logger.error(f"Blad podczas inicjalizacji ContextValidator: {e}")
        
        try:
            self._context_corrector = DynamicContextCorrection(self.config.correction_config)
            logger.debug("ContextIntegrityLayer: DynamicContextCorrection zainicjalizowany")
        except Exception as e:
            logger.error(f"Blad podczas inicjalizacji DynamicContextCorrection: {e}")
        
        try:
            self._context_manager = get_context_manager()
            logger.debug("ContextIntegrityLayer: polaczony z ContextManager")
        except Exception as e:
            logger.warning(f"Nie mozna polaczyc z ContextManager: {e}")
        
        self._initialized = True
    
    @classmethod
    def get_instance(cls, config: IntegrityConfig = None) -> 'ContextIntegrityLayer':
        """Pobranie instancji warstwy (singleton)."""
        if not hasattr(cls, '_instance'):
            cls._instance = cls(config)
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset instancji singleton."""
        if hasattr(cls, '_instance'):
            del cls._instance
    
    def set_config(self, config: IntegrityConfig) -> None:
        """Ustawienie konfiguracji warstwy."""
        self.config = config
        logger.info(f"Zmieniono konfiguracje ContextIntegrityLayer na: {config.check_level.value}")
    
    def register_check_hook(
        self, 
        hook: Callable[[SSIMessage, IntegrityCheckResult], None]
    ) -> None:
        """Rejestracja hooka sprawdzajacego."""
        self._check_hooks.append(hook)
        logger.debug(f"Zarejestrowano integrity check hook: {hook.__name__}")
    
    def check_integrity(
        self, 
        message: SSIMessage, 
        config: IntegrityConfig = None
    ) -> Tuple[SSIMessage, IntegrityCheckResult]:
        """
        Glowna metoda sprawdzania integralnosci wiadomosci.
        
        Przeplyw:
        1. Auto-korekta kontekstu (opcjonalnie)
        2. Walidacja wiadomosci
        3. Walidacja kontekstu
        4. Ocena ogólnej integralnosci
        
        Args:
            message: Wiadomosc do sprawdzenia
            config: Konfiguracja sprawdzania (opcjonalnie)
            
        Returns:
            Tuple[SSIMessage, IntegrityCheckResult]: Skorygowana wiadomosc i wynik sprawdzania
        """
        import time
        start_time = time.time()
        
        # Uzycie konfiguracji podanej lub domyslnej
        check_config = config or self.config
        
        # Utworzenie wyniku
        result = IntegrityCheckResult(
            message_id=message.message_id,
            check_level=check_config.check_level,
            is_integral=True,
            status=IntegrityStatus.COMPLETE
        )
        
        try:
            with self._lock:
                corrected_message = message
                
                # Krok 1: Auto-korekta kontekstu (opcjonalnie)
                if check_config.enable_context_correction and self._context_corrector:
                    corrected_message, correction_result = self._context_corrector.correct(corrected_message)
                    result.correction_result = correction_result
                    result.warnings.extend([
                        f"Auto-korekta: {action.value}" 
                        for action in correction_result.actions_performed
                    ])
                
                # Krok 2: Walidacja wiadomosci
                if check_config.enable_message_validation and self._message_validator:
                    message_validation = self._message_validator.validate(corrected_message)
                    result.message_validation = message_validation
                    
                    if not message_validation.is_valid:
                        result.is_integral = False
                        result.errors.extend(message_validation.errors)
                        if message_validation.result.value == "critical":
                            result.status = IntegrityStatus.CRITICAL
                        else:
                            result.status = IntegrityStatus.INCOMPLETE
                
                # Krok 3: Walidacja kontekstu
                if check_config.enable_context_validation and self._context_validator:
                    context_validation = self._context_validator.validate(corrected_message)
                    result.context_validation = context_validation
                    
                    if not context_validation.is_complete:
                        result.is_integral = False
                        if context_validation.result.value == "corrupted":
                            result.status = IntegrityStatus.CORRUPTED
                        elif result.status != IntegrityStatus.CRITICAL:
                            result.status = IntegrityStatus.INCOMPLETE
                
                # Krok 4: Ocena ogólna
                self._evaluate_overall_integrity(result)
                
                # Wywolanie hookow
                for hook in self._check_hooks:
                    try:
                        hook(corrected_message, result)
                    except Exception as e:
                        logger.warning(f"Hook sprawdzania integralnosci zaliczony: {e}")
                
                # Decyzja na podstawieक्ति
                if check_config.reject_corrupted and result.status in [IntegrityStatus.CRITICAL, IntegrityStatus.CORRUPTED]:
                    result.is_integral = False
        
        except Exception as e:
            logger.error(f"Blad podczas sprawdzania integralnosci: {e}")
            result.is_integral = False
            result.status = IntegrityStatus.CRITICAL
            result.errors.append({
                'error_code': 'INTEGRITY_ERROR',
                'error_type': 'unexpected_error',
                'message': str(e)
            })
        
        # Czas przetwarzania
        result.processing_time_ms = (time.time() - start_time) * 1000
        
        # Logowanie
        if result.is_integral:
            logger.debug(f"Sprawdzenie integralnosci powiodlo sie: {message.message_id}")
        elif result.status == IntegrityStatus.CRITICAL:
            logger.error(f"Krytyczny problem z integralnoscia: {message.message_id}")
        elif result.status == IntegrityStatus.CORRUPTED:
            logger.error(f"Uszkodzona integralnosc: {message.message_id}")
        elif result.status == IntegrityStatus.INCOMPLETE:
            logger.warning(f"Niekompletna integralnosc: {message.message_id}")
        else:
            logger.info(f"Czesciowa integralnosc: {message.message_id}")
        
        return corrected_message, result
    
    def check_and_fix(
        self, 
        message: SSIMessage, 
        config: IntegrityConfig = None
    ) -> Tuple[SSIMessage, IntegrityCheckResult]:
        """
        Sprawdzenie i naprawa integralnosci.
        
        Args:
            message: Wiadomosc do sprawdzenia i naprawy
            config: Konfiguracja (opcjonalnie)
            
        Returns:
            Tuple[SSIMessage, IntegrityCheckResult]: Skorygowana wiadomosc i wynik
        """
        # Ustawienie konfiguracji z auto-korekta
        if config:
            new_config = IntegrityConfig(
                check_level=config.check_level,
                validation_config=config.validation_config,
                context_validation_config=config.context_validation_config,
                correction_config=config.correction_config,
                enable_message_validation=config.enable_message_validation,
                enable_context_validation=config.enable_context_validation,
                enable_context_correction=True,  # Wymuszamy auto-korekte
                strict_mode=config.strict_mode,
                reject_corrupted=config.reject_corrupted
            )
        else:
            new_config = IntegrityConfig(
                check_level=self.config.check_level,
                validation_config=self.config.validation_config,
                context_validation_config=self.config.context_validation_config,
                correction_config=self.config.correction_config,
                enable_message_validation=self.config.enable_message_validation,
                enable_context_validation=self.config.enable_context_validation,
                enable_context_correction=True,
                strict_mode=self.config.strict_mode,
                reject_corrupted=self.config.reject_corrupted
            )
        
        return self.check_integrity(message, new_config)
    
    def is_integral(self, message: SSIMessage) -> bool:
        """
        Szybkie sprawdzenie integralnosci.
        
        Args:
            message: Wiadomosc do sprawdzenia
            
        Returns:
            bool: Czy wiadomosc ma pelna integralnosc
        """
        _, result = self.check_integrity(message)
        return result.is_integral
    
    def get_integrity_score(self, message: SSIMessage) -> float:
        """
        Pobranie oceny integralnosci.
        
        Args:
            message: Wiadomosc do oceny
            
        Returns:
            float: Ocena integralnosci (0.0 - 1.0)
        """
        _, result = self.check_integrity(message)
        return result.integrity_score
    
    def ensure_integrity(self, message: SSIMessage) -> SSIMessage:
        """
        Zapewnienie integralnosci wiadomosci.
        
        Args:
            message: Wiadomosc
            
        Returns:
            SSIMessage: Wiadomosc z zapewniona integralnoscia
        """
        corrected, _ = self.check_and_fix(message)
        return corrected
    
    def _evaluate_overall_integrity(self, result: IntegrityCheckResult) -> None:
        """Ocena ogólnej integralnosci."""
        # Obliczenie integrity_score
        score = 1.0
        
        # Walidacja wiadomosci
        if result.message_validation:
            if not result.message_validation.is_valid:
                score -= 0.4  # Duza waga
            score -= len(result.message_validation.warnings) * 0.05
        
        # Walidacja kontekstu
        if result.context_validation:
            if not result.context_validation.is_complete:
                score -= 0.3  # Duza waga
            score -= (1.0 - result.context_validation.context_score) * 0.3
        
        # Korekta
        if result.correction_result:
            score += result.correction_result.correction_score * 0.1
        
        # Ograniczanie do zakresu 0.0 - 1.0
        result.integrity_score = max(0.0, min(1.0, score))
        
        # Aktualizacja statusu
        if score >= 0.9:
            result.status = IntegrityStatus.COMPLETE
        elif score >= 0.7:
            result.status = IntegrityStatus.PARTIAL
        elif score >= 0.4:
            result.status = IntegrityStatus.INCOMPLETE
        elif score >= 0.1:
            result.status = IntegrityStatus.CORRUPTED
        else:
            result.status = IntegrityStatus.CRITICAL


# Funkcje helper

def get_integrity_layer(config: IntegrityConfig = None) -> ContextIntegrityLayer:
    """Pobranie instancji warstwy integralnosci."""
    return ContextIntegrityLayer.get_instance(config)


def check_integrity(
    message: SSIMessage, 
    config: IntegrityConfig = None
) -> Tuple[SSIMessage, IntegrityCheckResult]:
    """
    Sprawdzenie integralnosci wiadomosci.
    
    Args:
        message: Wiadomosc do sprawdzenia
        config: Konfiguracja (opcjonalnie)
        
    Returns:
        Tuple[SSIMessage, IntegrityCheckResult]: Skorygowana wiadomosc i wynik
    """
    layer = get_integrity_layer(config)
    return layer.check_integrity(message, config)


def check_and_fix_integrity(
    message: SSIMessage, 
    config: IntegrityConfig = None
) -> Tuple[SSIMessage, IntegrityCheckResult]:
    """
    Sprawdzenie i naprawa integralnosci.
    
    Args:
        message: Wiadomosc do sprawdzenia i naprawy
        config: Konfiguracja (opcjonalnie)
        
    Returns:
        Tuple[SSIMessage, IntegrityCheckResult]: Skorygowana wiadomosc i wynik
    """
    layer = get_integrity_layer(config)
    return layer.check_and_fix(message, config)


def is_integral(
    message: SSIMessage, 
    config: IntegrityConfig = None
) -> bool:
    """
    Szybkie sprawdzenie integralnosci.
    
    Args:
        message: Wiadomosc do sprawdzenia
        config: Konfiguracja (opcjonalnie)
        
    Returns:
        bool: Czy wiadomosc ma pelna integralnosc
    """
    layer = get_integrity_layer(config)
    return layer.is_integral(message)


def ensure_integrity(
    message: SSIMessage, 
    config: IntegrityConfig = None
) -> SSIMessage:
    """
    Zapewnienie integralnosci wiadomosci.
    
    Args:
        message: Wiadomosc
        config: Konfiguracja (opcjonalnie)
        
    Returns:
        SSIMessage: Wiadomosc z zapewniona integralnoscia
    """
    layer = get_integrity_layer(config)
    return layer.ensure_integrity(message)


# Inicjalizacja modulu
import threading
