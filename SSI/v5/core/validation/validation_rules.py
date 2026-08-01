"""
SSI V5 - Validation Rules Engine

Modul odpowiedzialny za zarzadzanie zasadami walidacji.
Umozliwia definicje niestandardowych zasad walidacji dla róznych typów wiadomosci.

Wersja: 2.0.0
Data: 2026-08-01
"""

import re
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union

from SSI.v5.core.information_flow_controller.message_models import (
    SSIMessage,
    ProcessType,
    PriorityLevel
)
from SSI.v5.core.validation.message_validator import (
    ValidationError,
    ValidationReport,
    ValidationConfig,
    ValidationLevel
)

# Konfiguracja logowania
logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Typy zasad walidacji."""
    FIELD_REQUIRED = "field_required"           # Pole jest wymagane
    FIELD_TYPE = "field_type"                   # Typ pola
    FIELD_VALUE = "field_value"                 # Dopuszczalna wartosc pola
    FIELD_PATTERN = "field_pattern"             # Wzorc pola (regex)
    FIELD_RANGE = "field_range"                 # Zakres wartosci (min/max)
    FIELD_SIZE = "field_size"                   # Rozmiar pola
    CONDITIONAL = "conditional"                 # Zasada warunkowa
    DEPENDENCY = "dependency"                  # Zaleznosc miedzy polami
    CUSTOM = "custom"                           # Niestandardowa zasada


class RuleSeverity(Enum):
    """Poziom waznosci zasady."""
    CRITICAL = "critical"                        # Krytyczna - musza byc spelnione
    HIGH = "high"                              # Wysoka - powinny byc spelnione
    MEDIUM = "medium"                          # Srednia
    LOW = "low"                                # Niska - zalecane


@dataclass
class ValidationRule:
    """
    Zasada walidacji.
    
    Odpowiedzialnosc:
    - Definicja pojedynczej zasady walidacji
    - Sprawdzanie czy wiadomosc spenia zasade
    """
    rule_id: str
    rule_type: RuleType
    description: str
    severity: RuleSeverity = RuleSeverity.MEDIUM
    
    # Parametry zasady (zalezne od typu)
    field_name: Optional[str] = None
    required: Optional[bool] = None
    expected_type: Optional[type] = None
    expected_value: Optional[Any] = None
    allowed_values: Optional[Set[Any]] = None
    pattern: Optional[str] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    min_size: Optional[int] = None
    max_size: Optional[int] = None
    
    # Dla zasad warunkowych
    condition: Optional[Callable[[SSIMessage], bool]] = None
    dependent_fields: Optional[List[str]] = None
    dependent_values: Optional[Dict[str, Any]] = None
    
    # Dla zasad niestandardowych
    custom_validator: Optional[Callable[[SSIMessage], Optional[ValidationError]]] = None
    
    # Metadane
    applies_to_process_types: Optional[Set[str]] = None  # Dla jakich typów procesów
    applies_to_priority: Optional[Set[Union[PriorityLevel, str]]] = None  # Dla jakich priorytetów
    
    def __post_init__(self):
        """Inicjalizacja po utworzeniu."""
        # Kompilacja wzorca regex jeśli dostepny
        if self.pattern:
            self._compiled_pattern = re.compile(self.pattern)
        else:
            self._compiled_pattern = None
    
    def applies_to(self, message: SSIMessage) -> bool:
        """
        Sprawdzenie czy zasada dotyczy danej wiadomosci.
        
        Args:
            message: Wiadomosc do sprawdzenia
            
        Returns:
            bool: Czy zasada dotyczy wiadomosci
        """
        # Sprawdzenie typu procesu
        if self.applies_to_process_types:
            process_type = message.process_type.value if hasattr(message.process_type, 'value') else str(message.process_type)
            if process_type not in self.applies_to_process_types:
                return False
        
        # Sprawdzenie priorytetu
        if self.applies_to_priority:
            priority = message.priority.value if hasattr(message.priority, 'value') else str(message.priority)
            if priority not in self.applies_to_priority:
                return False
        
        return True
    
    def validate(self, message: SSIMessage) -> Optional[ValidationError]:
        """
        Sprawdzenie czy wiadomosc spenia zasade.
        
        Args:
            message: Wiadomosc do sprawdzenia
            
        Returns:
            Optional[ValidationError]: Blad walidacji lub None jeśli OK
        """
        if not self.applies_to(message):
            return None
        
        try:
            # Pole wymagane
            if self.rule_type == RuleType.FIELD_REQUIRED:
                return self._validate_field_required(message)
            
            # Typ pola
            if self.rule_type == RuleType.FIELD_TYPE:
                return self._validate_field_type(message)
            
            # Wartosc pola
            if self.rule_type == RuleType.FIELD_VALUE:
                return self._validate_field_value(message)
            
            # Wzorc pola
            if self.rule_type == RuleType.FIELD_PATTERN:
                return self._validate_field_pattern(message)
            
            # Zakres wartosci
            if self.rule_type == RuleType.FIELD_RANGE:
                return self._validate_field_range(message)
            
            # Rozmiar pola
            if self.rule_type == RuleType.FIELD_SIZE:
                return self._validate_field_size(message)
            
            # Zasada warunkowa
            if self.rule_type == RuleType.CONDITIONAL:
                return self._validate_conditional(message)
            
            # Zaleznosc miedzy polami
            if self.rule_type == RuleType.DEPENDENCY:
                return self._validate_dependency(message)
            
            # Niestandardowa zasada
            if self.rule_type == RuleType.CUSTOM:
                return self._validate_custom(message)
            
        except Exception as e:
            return ValidationError(
                error_code=f"RULE_ERROR_{self.rule_id}",
                error_type="rule_execution_error",
                field_name=self.field_name or "unknown",
                message=f"Blad podczas wykonywania zasady {self.rule_id}: {e}",
                severity="error"
            )
        
        return None
    
    def _validate_field_required(self, message: SSIMessage) -> Optional[ValidationError]:
        """Sprawdzenie czy pole jest wymagane."""
        if not self.field_name:
            return None
        
        value = getattr(message, self.field_name, None)
        if value is None or value == "" or (isinstance(value, list) and len(value) == 0):
            return ValidationError(
                error_code=f"RULE_REQ_{self.rule_id}",
                error_type="field_required",
                field_name=self.field_name,
                message=f"Pole {self.field_name} jest wymagane",
                severity=self.severity.value
            )
        return None
    
    def _validate_field_type(self, message: SSIMessage) -> Optional[ValidationError]:
        """Sprawdzenie typu pola."""
        if not self.field_name or not self.expected_type:
            return None
        
        value = getattr(message, self.field_name, None)
        if value is None:
            return None  # Nie sprawdzamy typu jeśli pole nie istnieje
        
        if not isinstance(value, self.expected_type):
            return ValidationError(
                error_code=f"RULE_TYPE_{self.rule_id}",
                error_type="wrong_type",
                field_name=self.field_name,
                message=f"Pole {self.field_name} powinno byc typu {self.expected_type.__name__}, jest: {type(value).__name__}",
                severity=self.severity.value
            )
        return None
    
    def _validate_field_value(self, message: SSIMessage) -> Optional[ValidationError]:
        """Sprawdzenie wartosci pola."""
        if not self.field_name:
            return None
        
        value = getattr(message, self.field_name, None)
        if value is None:
            return None
        
        # Sprawdzenie pojedynczej wartosci
        if self.expected_value is not None:
            if value != self.expected_value:
                return ValidationError(
                    error_code=f"RULE_VAL_{self.rule_id}",
                    error_type="wrong_value",
                    field_name=self.field_name,
                    message=f"Pole {self.field_name} powinno miec wartosc {self.expected_value}, ma: {value}",
                    severity=self.severity.value
                )
        
        # Sprawdzenie dozwolonych wartosci
        if self.allowed_values is not None:
            if value not in self.allowed_values:
                return ValidationError(
                    error_code=f"RULE_VAL_{self.rule_id}",
                    error_type="value_not_allowed",
                    field_name=self.field_name,
                    message=f"Pole {self.field_name} ma niedozwolona wartosc: {value}",
                    severity=self.severity.value,
                    suggested_fix=f"Dozwolone wartosci: {self.allowed_values}"
                )
        
        return None
    
    def _validate_field_pattern(self, message: SSIMessage) -> Optional[ValidationError]:
        """Sprawdzenie wzorca pola."""
        if not self.field_name or not self._compiled_pattern:
            return None
        
        value = getattr(message, self.field_name, None)
        if value is None:
            return None
        
        if not self._compiled_pattern.match(str(value)):
            return ValidationError(
                error_code=f"RULE_PAT_{self.rule_id}",
                error_type="pattern_mismatch",
                field_name=self.field_name,
                message=f"Pole {self.field_name} nie pasuje do wzorca: {self.pattern}",
                severity=self.severity.value
            )
        return None
    
    def _validate_field_range(self, message: SSIMessage) -> Optional[ValidationError]:
        """Sprawdzenie zakresu wartosci."""
        if not self.field_name:
            return None
        
        value = getattr(message, self.field_name, None)
        if value is None:
            return None
        
        if self.min_value is not None and value < self.min_value:
            return ValidationError(
                error_code=f"RULE_RNG_{self.rule_id}",
                error_type="below_minimum",
                field_name=self.field_name,
                message=f"Pole {self.field_name} jest mniejsze niz minimum: {self.min_value}",
                severity=self.severity.value
            )
        
        if self.max_value is not None and value > self.max_value:
            return ValidationError(
                error_code=f"RULE_RNG_{self.rule_id}",
                error_type="above_maximum",
                field_name=self.field_name,
                message=f"Pole {self.field_name} jest wieksze niz maximum: {self.max_value}",
                severity=self.severity.value
            )
        
        return None
    
    def _validate_field_size(self, message: SSIMessage) -> Optional[ValidationError]:
        """Sprawdzenie rozmiaru pola."""
        if not self.field_name:
            return None
        
        value = getattr(message, self.field_name, None)
        if value is None:
            return None
        
        try:
            size = len(value)
        except Exception:
            return None
        
        if self.min_size is not None and size < self.min_size:
            return ValidationError(
                error_code=f"RULE_SIZ_{self.rule_id}",
                error_type="too_small",
                field_name=self.field_name,
                message=f"Pole {self.field_name} jest za male (min: {self.min_size}, aktualnie: {size})",
                severity=self.severity.value
            )
        
        if self.max_size is not None and size > self.max_size:
            return ValidationError(
                error_code=f"RULE_SIZ_{self.rule_id}",
                error_type="too_large",
                field_name=self.field_name,
                message=f"Pole {self.field_name} jest za duze (max: {self.max_size}, aktualnie: {size})",
                severity=self.severity.value
            )
        
        return None
    
    def _validate_conditional(self, message: SSIMessage) -> Optional[ValidationError]:
        """Sprawdzenie zasady warunkowej."""
        if not self.condition:
            return None
        
        try:
            if not self.condition(message):
                return ValidationError(
                    error_code=f"RULE_COND_{self.rule_id}",
                    error_type="condition_not_met",
                    field_name=self.field_name or "condition",
                    message=f"Warunek nie zostal spelniony: {self.description}",
                    severity=self.severity.value
                )
        except Exception as e:
            return ValidationError(
                error_code=f"RULE_COND_{self.rule_id}",
                error_type="condition_error",
                field_name=self.field_name or "condition",
                message=f"Blad podczas sprawdzania warunku: {e}",
                severity="error"
            )
        
        return None
    
    def _validate_dependency(self, message: SSIMessage) -> Optional[ValidationError]:
        """Sprawdzenie zaleznosci miedzy polami."""
        if not self.dependent_fields or not self.dependent_values:
            return None
        
        # Sprawdzenie czy pole glówne istnieje
        if self.field_name:
            main_value = getattr(message, self.field_name, None)
            if main_value is None:
                return None
        
        # Sprawdzenie zaleznosci
        for dep_field, dep_value in self.dependent_values.items():
            actual_value = getattr(message, dep_field, None)
            if actual_value != dep_value:
                return ValidationError(
                    error_code=f"RULE_DEP_{self.rule_id}",
                    error_type="dependency_violation",
                    field_name=dep_field,
                    message=f"Pole {dep_field} powinno miec wartosc {dep_value} gdy {self.field_name} = {main_value}",
                    severity=self.severity.value
                )
        
        return None
    
    def _validate_custom(self, message: SSIMessage) -> Optional[ValidationError]:
        """Sprawdzenie niestandardowej zasady."""
        if not self.custom_validator:
            return None
        
        return self.custom_validator(message)


class ValidationRulesEngine:
    """
    Silnik zasad walidacji.
    
    Odpowiedzialnosc:
    - Zarzadzanie zbiorem zasad walidacji
    - Rejestracja i usuwanie zasad
    - Walidacja wiadomosci z uzyciem zarejestrowanych zasad
    - Grupowanie zasad wedlug typów procesów
    """
    
    def __init__(self):
        """Inicjalizacja silnika zasad."""
        self._rules: Dict[str, ValidationRule] = {}
        self._rules_by_process_type: Dict[str, List[str]] = {}
        self._rule_groups: Dict[str, List[str]] = {}
        self._lock = threading.RLock()
        logger.info("ValidationRulesEngine zainicjalizowany")
    
    def register_rule(self, rule: ValidationRule) -> str:
        """
        Rejestracja nowej zasady.
        
        Args:
            rule: Zasada do zarejestrowania
            
        Returns:
            str: ID zarejestrowanej zasady
        """
        with self._lock:
            if rule.rule_id in self._rules:
                logger.warning(f"Zasada o ID {rule.rule_id} zostanie nadpisana")
            
            self._rules[rule.rule_id] = rule
            
            # Indeksowanie wedlug typu procesu
            if rule.applies_to_process_types:
                for process_type in rule.applies_to_process_types:
                    if process_type not in self._rules_by_process_type:
                        self._rules_by_process_type[process_type] = []
                    if rule.rule_id not in self._rules_by_process_type[process_type]:
                        self._rules_by_process_type[process_type].append(rule.rule_id)
            
            logger.debug(f"Zarejestrowano zasade: {rule.rule_id}")
            return rule.rule_id
    
    def register_rules(self, rules: List[ValidationRule]) -> List[str]:
        """
        Rejestracja wielu zasad.
        
        Args:
            rules: Lista zasad do zarejestrowania
            
        Returns:
            List[str]: Lista ID zarejestrowanych zasad
        """
        return [self.register_rule(rule) for rule in rules]
    
    def unregister_rule(self, rule_id: str) -> bool:
        """
        Wyrejestrowanie zasady.
        
        Args:
            rule_id: ID zasady do wyrejestrowania
            
        Returns:
            bool: Czy wyrejestrowano pomyślnie
        """
        with self._lock:
            if rule_id not in self._rules:
                return False
            
            # Usuniecie z indeksów
            rule = self._rules[rule_id]
            if rule.applies_to_process_types:
                for process_type in rule.applies_to_process_types:
                    if process_type in self._rules_by_process_type:
                        if rule_id in self._rules_by_process_type[process_type]:
                            self._rules_by_process_type[process_type].remove(rule_id)
            
            del self._rules[rule_id]
            logger.debug(f"Wyrejestrowano zasade: {rule_id}")
            return True
    
    def get_rule(self, rule_id: str) -> Optional[ValidationRule]:
        """
        Pobranie zasady po ID.
        
        Args:
            rule_id: ID zasady
            
        Returns:
            Optional[ValidationRule]: Zasada lub None
        """
        with self._lock:
            return self._rules.get(rule_id)
    
    def get_rules_by_process_type(self, process_type: str) -> List[ValidationRule]:
        """
        Pobranie zasad dla danego typu procesu.
        
        Args:
            process_type: Typ procesu
            
        Returns:
            List[ValidationRule]: Lista zasad
        """
        with self._lock:
            rule_ids = self._rules_by_process_type.get(process_type, [])
            return [self._rules[rid] for rid in rule_ids if rid in self._rules]
    
    def get_all_rules(self) -> List[ValidationRule]:
        """
        Pobranie wszystkich zasad.
        
        Returns:
            List[ValidationRule]: Lista wszystkich zasad
        """
        with self._lock:
            return list(self._rules.values())
    
    def clear_rules(self) -> None:
        """Wyczyszczenie wszystkich zasad."""
        with self._lock:
            self._rules.clear()
            self._rules_by_process_type.clear()
            logger.info("Wyczyszczono wszystkie zasady walidacji")
    
    def validate(
        self, 
        message: SSIMessage, 
        rule_ids: Optional[List[str]] = None
    ) -> List[ValidationError]:
        """
        Walidacja wiadomosci z uzyciem zasad.
        
        Args:
            message: Wiadomosc do zwalidowania
            rule_ids: Lista ID zasad do uzycia (opcjonalnie, wszystkie jeśli None)
            
        Returns:
            List[ValidationError]: Lista bledów walidacji
        """
        errors = []
        
        with self._lock:
            # Wybór zasad do sprawdzenia
            if rule_ids:
                rules_to_check = [self._rules[rid] for rid in rule_ids if rid in self._rules]
            else:
                rules_to_check = list(self._rules.values())
            
            # Sprawdzenie kazdej zasady
            for rule in rules_to_check:
                error = rule.validate(message)
                if error:
                    errors.append(error)
        
        return errors
    
    def validate_with_report(
        self, 
        message: SSIMessage, 
        rule_ids: Optional[List[str]] = None
    ) -> ValidationReport:
        """
        Walidacja wiadomosci z uzyciem zasad i zwrócenie raportu.
        
        Args:
            message: Wiadomosc do zwalidowania
            rule_ids: Lista ID zasad do uzycia (opcjonalnie)
            
        Returns:
            ValidationReport: Raport z walidacji
        """
        errors = self.validate(message, rule_ids)
        
        report = ValidationReport(
            message_id=message.message_id,
            is_valid=len(errors) == 0,
            validation_level=ValidationLevel.STANDARD,
            result=ValidationReport.ValidationResult.VALID if len(errors) == 0 else ValidationReport.ValidationResult.INVALID
        )
        
        for error in errors:
            report.add_error(error)
        
        return report


# Funkcje helper

def create_required_field_rule(
    rule_id: str,
    field_name: str,
    description: str,
    severity: RuleSeverity = RuleSeverity.HIGH,
    applies_to_process_types: Optional[Set[str]] = None
) -> ValidationRule:
    """Utworzenie zasady wymaganego pola."""
    return ValidationRule(
        rule_id=rule_id,
        rule_type=RuleType.FIELD_REQUIRED,
        field_name=field_name,
        required=True,
        description=description,
        severity=severity,
        applies_to_process_types=applies_to_process_types
    )


def create_field_type_rule(
    rule_id: str,
    field_name: str,
    expected_type: type,
    description: str,
    severity: RuleSeverity = RuleSeverity.HIGH,
    applies_to_process_types: Optional[Set[str]] = None
) -> ValidationRule:
    """Utworzenie zasady typu pola."""
    return ValidationRule(
        rule_id=rule_id,
        rule_type=RuleType.FIELD_TYPE,
        field_name=field_name,
        expected_type=expected_type,
        description=description,
        severity=severity,
        applies_to_process_types=applies_to_process_types
    )


def create_field_value_rule(
    rule_id: str,
    field_name: str,
    allowed_values: Set[Any],
    description: str,
    severity: RuleSeverity = RuleSeverity.MEDIUM,
    applies_to_process_types: Optional[Set[str]] = None
) -> ValidationRule:
    """Utworzenie zasady dopuszczalnych wartosci pola."""
    return ValidationRule(
        rule_id=rule_id,
        rule_type=RuleType.FIELD_VALUE,
        field_name=field_name,
        allowed_values=allowed_values,
        description=description,
        severity=severity,
        applies_to_process_types=applies_to_process_types
    )


def create_pattern_rule(
    rule_id: str,
    field_name: str,
    pattern: str,
    description: str,
    severity: RuleSeverity = RuleSeverity.MEDIUM,
    applies_to_process_types: Optional[Set[str]] = None
) -> ValidationRule:
    """Utworzenie zasady wzorca pola."""
    return ValidationRule(
        rule_id=rule_id,
        rule_type=RuleType.FIELD_PATTERN,
        field_name=field_name,
        pattern=pattern,
        description=description,
        severity=severity,
        applies_to_process_types=applies_to_process_types
    )


def create_conditional_rule(
    rule_id: str,
    condition: Callable[[SSIMessage], bool],
    description: str,
    severity: RuleSeverity = RuleSeverity.HIGH,
    applies_to_process_types: Optional[Set[str]] = None
) -> ValidationRule:
    """Utworzenie zasady warunkowej."""
    return ValidationRule(
        rule_id=rule_id,
        rule_type=RuleType.CONDITIONAL,
        condition=condition,
        description=description,
        severity=severity,
        applies_to_process_types=applies_to_process_types
    )


def create_custom_rule(
    rule_id: str,
    custom_validator: Callable[[SSIMessage], Optional[ValidationError]],
    description: str,
    severity: RuleSeverity = RuleSeverity.MEDIUM,
    applies_to_process_types: Optional[Set[str]] = None
) -> ValidationRule:
    """Utworzenie niestandardowej zasady."""
    return ValidationRule(
        rule_id=rule_id,
        rule_type=RuleType.CUSTOM,
        custom_validator=custom_validator,
        description=description,
        severity=severity,
        applies_to_process_types=applies_to_process_types
    )


# Silnik globalny
_rules_engine: Optional[ValidationRulesEngine] = None


def get_rules_engine() -> ValidationRulesEngine:
    """Pobranie globalnego silnika zasad."""
    global _rules_engine
    if _rules_engine is None:
        _rules_engine = ValidationRulesEngine()
    return _rules_engine


def reset_rules_engine() -> None:
    """Reset globalnego silnika zasad."""
    global _rules_engine
    if _rules_engine is not None:
        _rules_engine.clear_rules()
        _rules_engine = None


# Import threading for the lock
import threading
