"""
SSI V5 - Validation Layer

Modul walidacji wiadomosci i kontekstu.

Struktura:
- message_validator.py: Walidacja struktury wiadomosci SSIMessage
- context_validator.py: Walidacja kontekstu wiadomosci
- schema_validator.py: Walidacja schematów i struktur danych
- validation_rules.py: Silnik zasad walidacji

Zasady:
1. Walidacja zawsze pierwsza
2. Brak walidacji = NIE wykonuj dzialania
3. Najpierw: korekta kontekstu -> walidacja -> wykonanie

Wersja: 2.0.0
Data: 2026-08-01
"""

from SSI.v5.core.validation.message_validator import (
    MessageValidator,
    ValidationConfig,
    ValidationError,
    ValidationLevel,
    ValidationReport,
    ValidationResult,
    get_validator,
    validate_message,
    is_message_valid,
    validate_and_fix
)

from SSI.v5.core.validation.context_validator import (
    ContextValidator,
    ContextValidationConfig,
    ContextValidationError,
    ContextValidationLevel,
    ContextValidationResult,
    ContextValidationReport,
    get_context_validator,
    validate_context,
    is_context_complete,
    detect_context_loss
)

from SSI.v5.core.validation.schema_validator import (
    SchemaValidator,
    SchemaType,
    SchemaField,
    MessageSchema,
    get_schema_validator,
    reset_schema_validator,
    # Funkcje tworzenia pól
    string_field,
    integer_field,
    float_field,
    boolean_field,
    enum_field,
    object_field,
    array_field
)

from SSI.v5.core.validation.validation_rules import (
    ValidationRulesEngine,
    RuleType,
    RuleSeverity,
    ValidationRule,
    get_rules_engine,
    reset_rules_engine,
    # Funkcje tworzenia zasad
    create_required_field_rule,
    create_field_type_rule,
    create_field_value_rule,
    create_pattern_rule,
    create_conditional_rule,
    create_custom_rule
)

# Eksport klas i funkcji
__all__ = [
    # Message Validator
    'MessageValidator',
    'ValidationConfig',
    'ValidationError',
    'ValidationLevel',
    'ValidationReport',
    'ValidationResult',
    'get_validator',
    'validate_message',
    'is_message_valid',
    'validate_and_fix',
    
    # Context Validator
    'ContextValidator',
    'ContextValidationConfig',
    'ContextValidationError',
    'ContextValidationLevel',
    'ContextValidationResult',
    'ContextValidationReport',
    'get_context_validator',
    'validate_context',
    'is_context_complete',
    'detect_context_loss',
    
    # Schema Validator
    'SchemaValidator',
    'SchemaType',
    'SchemaField',
    'MessageSchema',
    'get_schema_validator',
    'reset_schema_validator',
    'string_field',
    'integer_field',
    'float_field',
    'boolean_field',
    'enum_field',
    'object_field',
    'array_field',
    
    # Validation Rules
    'ValidationRulesEngine',
    'RuleType',
    'RuleSeverity',
    'ValidationRule',
    'get_rules_engine',
    'reset_rules_engine',
    'create_required_field_rule',
    'create_field_type_rule',
    'create_field_value_rule',
    'create_pattern_rule',
    'create_conditional_rule',
    'create_custom_rule'
]


def init_validation_layer() -> bool:
    """
    Inicjalizacja warstwy walidacji.
    
    Returns:
        bool: True jeśli inicjalizacja powiodła się
    """
    try:
        # Inicjalizacja walidatorów (lazy loading)
        get_validator()
        get_context_validator()
        get_schema_validator()
        get_rules_engine()
        
        return True
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Blad podczas inicjalizacji warstwy walidacji: {e}")
        return False
