"""
SSI V5 - Schema Validator

Modul odpowiedzialny za walidacje schematow wiadomosci.
Umozliwia definicje i walidacje zlozonych struktur danych.

Wersja: 2.0.0
Data: 2026-08-01
"""

import re
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from SSI.v5.core.information_flow_controller.message_models import (
    SSIMessage,
    ProcessType,
    PriorityLevel
)
from SSI.v5.core.validation.message_validator import (
    ValidationError,
    ValidationReport,
    ValidationLevel
)

# Konfiguracja logowania
logger = logging.getLogger(__name__)


class SchemaType(Enum):
    """Typy schematów."""
    OBJECT = "object"           # Obiekt (slownik)
    ARRAY = "array"            # Tablica (lista)
    STRING = "string"          # Lancuch znaków
    NUMBER = "number"          # Liczba (int lub float)
    INTEGER = "integer"        # Liczba calkowita
    FLOAT = "float"            # Liczba zmiennoprzecinkowa
    BOOLEAN = "boolean"        # Wartosc logiczna
    NULL = "null"              # Null
    ANY = "any"                # Dowolny typ
    DATETIME = "datetime"      # Data i czas
    DATE = "date"              # Data
    TIME = "time"              # Czas
    UUID = "uuid"              # UUID
    ENUM = "enum"              # Wyliczeniowa lista wartosci
    PATTERN = "pattern"        # Wzorc (regex)


@dataclass
class SchemaField:
    """
    Definicja pojedynczego pola w schemacie.
    """
    name: str
    schema_type: SchemaType
    description: str = ""
    required: bool = False
    default: Optional[Any] = None
    
    # Dla typów liczbowych
    minimum: Optional[Union[int, float]] = None
    maximum: Optional[Union[int, float]] = None
    exclusive_minimum: bool = False
    exclusive_maximum: bool = False
    
    # Dla lancuchów znaków
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    
    # Dla enum
    allowed_values: Optional[Set[Any]] = None
    
    # Dla obiektów
    properties: Optional[Dict[str, 'SchemaField']] = None
    additional_properties: bool = True
    
    # Dla tablic
    items: Optional['SchemaField'] = None
    min_items: Optional[int] = None
    max_items: Optional[int] = None
    unique_items: bool = False
    
    # Metadane
    read_only: bool = False
    write_only: bool = False
    deprecated: bool = False
    
    def __post_init__(self):
        """Inicjalizacja po utworzeniu."""
        # Kompilacja wzorca jeśli dostepny
        if self.pattern:
            self._compiled_pattern = re.compile(self.pattern)
        else:
            self._compiled_pattern = None
    
    def validate(self, value: Any, path: str = "") -> Optional[ValidationError]:
        """
        Walidacja wartosci wg schematu.
        
        Args:
            value: Wartosc do walidacji
            path: Sciezka do pola (dla komunikatów o bledach)
            
        Returns:
            Optional[ValidationError]: Blad walidacji lub None
        """
        full_path = f"{path}.{self.name}" if path else self.name
        
        # Sprawdzenie wymaganego pola
        if self.required and value is None:
            return ValidationError(
                error_code="SCHEMA_REQ_001",
                error_type="required_field",
                field_name=full_path,
                message=f"Pole {full_path} jest wymagane",
                severity="error"
            )
        
        # Uzycie domyslnej wartosci
        if value is None:
            value = self.default
        
        # Sprawdzenie typu
        if not self._validate_type(value, full_path):
            return ValidationError(
                error_code="SCHEMA_TYPE_001",
                error_type="wrong_type",
                field_name=full_path,
                message=f"Pole {full_path} powinno byc typu {self.schema_type.value}, jest: {type(value).__name__}",
                severity="error"
            )
        
        # Walidacja specyficzna dla typu
        return self._validate_type_specific(value, full_path)
    
    def _validate_type(self, value: Any, path: str) -> bool:
        """Sprawdzenie typu wartosci."""
        if value is None:
            return True  # Null jest akceptowalne dla wszystkich typów
        
        if self.schema_type == SchemaType.ANY:
            return True
        
        if self.schema_type == SchemaType.OBJECT:
            return isinstance(value, dict)
        
        if self.schema_type == SchemaType.ARRAY:
            return isinstance(value, (list, tuple, set))
        
        if self.schema_type == SchemaType.STRING:
            return isinstance(value, str)
        
        if self.schema_type == SchemaType.NUMBER:
            return isinstance(value, (int, float))
        
        if self.schema_type == SchemaType.INTEGER:
            return isinstance(value, int) and not isinstance(value, bool)
        
        if self.schema_type == SchemaType.FLOAT:
            return isinstance(value, float)
        
        if self.schema_type == SchemaType.BOOLEAN:
            return isinstance(value, bool)
        
        if self.schema_type == SchemaType.NULL:
            return value is None
        
        if self.schema_type == SchemaType.DATETIME:
            return isinstance(value, datetime)
        
        if self.schema_type == SchemaType.DATE:
            if isinstance(value, datetime):
                return True
            try:
                from dateutil.parser import parse
                parse(str(value))
                return True
            except Exception:
                return False
        
        if self.schema_type == SchemaType.UUID:
            if isinstance(value, str):
                uuid_pattern = re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', re.IGNORECASE)
                return bool(uuid_pattern.match(value))
            return False
        
        return True
    
    def _validate_type_specific(self, value: Any, path: str) -> Optional[ValidationError]:
        """Walidacja specyficzna dla typu."""
        if value is None:
            return None
        
        # Walidacja liczb
        if self.schema_type in [SchemaType.NUMBER, SchemaType.INTEGER, SchemaType.FLOAT]:
            if self.minimum is not None:
                if (self.exclusive_minimum and value <= self.minimum) or \
                   (not self.exclusive_minimum and value < self.minimum):
                    return ValidationError(
                        error_code="SCHEMA_RNG_001",
                        error_type="below_minimum",
                        field_name=path,
                        message=f"Pole {path} jest mniejsze niz minimum: {self.minimum}",
                        severity="error"
                    )
            
            if self.maximum is not None:
                if (self.exclusive_maximum and value >= self.maximum) or \
                   (not self.exclusive_maximum and value > self.maximum):
                    return ValidationError(
                        error_code="SCHEMA_RNG_002",
                        error_type="above_maxium",
                        field_name=path,
                        message=f"Pole {path} jest wieksze niz maximum: {self.maximum}",
                        severity="error"
                    )
        
        # Walidacja lancuchów
        if self.schema_type == SchemaType.STRING:
            if self.min_length is not None and len(value) < self.min_length:
                return ValidationError(
                    error_code="SCHEMA_STR_001",
                    error_type="too_short",
                    field_name=path,
                    message=f"Pole {path} jest za krótki (min: {self.min_length}, aktualnie: {len(value)})",
                    severity="error"
                )
            
            if self.max_length is not None and len(value) > self.max_length:
                return ValidationError(
                    error_code="SCHEMA_STR_002",
                    error_type="too_long",
                    field_name=path,
                    message=f"Pole {path} jest za dlugi (max: {self.max_length}, aktualnie: {len(value)})",
                    severity="error"
                )
            
            if self._compiled_pattern and not self._compiled_pattern.match(value):
                return ValidationError(
                    error_code="SCHEMA_STR_003",
                    error_type="pattern_mismatch",
                    field_name=path,
                    message=f"Pole {path} nie pasuje do wzorca: {self.pattern}",
                    severity="error"
                )
        
        # Walidacja enum
        if self.schema_type == SchemaType.ENUM and self.allowed_values:
            if value not in self.allowed_values:
                return ValidationError(
                    error_code="SCHEMA_ENUM_001",
                    error_type="value_not_allowed",
                    field_name=path,
                    message=f"Pole {path} ma niedozwolona wartosc: {value}",
                    severity="error",
                    suggested_fix=f"Dozwolone wartosci: {self.allowed_values}"
                )
        
        # Walidacja obiektów
        if self.schema_type == SchemaType.OBJECT:
            if not isinstance(value, dict):
                return None
            
            # Sprawdzenie insulin wlasciwosci
            if not self.additional_properties:
                extra_fields = set(value.keys()) - set(self.properties.keys() if self.properties else [])
                if extra_fields:
                    return ValidationError(
                        error_code="SCHEMA_OBJ_001",
                        error_type="additional_properties",
                        field_name=path,
                        message=f"Pole {path} ma nieoczekiwane pole: {', '.join(extra_fields)}",
                        severity="error"
                    )
            
            # Walidacja wlasciwosci
            if self.properties:
                for prop_name, prop_schema in self.properties.items():
                    prop_value = value.get(prop_name)
                    error = prop_schema.validate(prop_value, path)
                    if error:
                        return error
        
        # Walidacja tablic
        if self.schema_type == SchemaType.ARRAY:
            if not isinstance(value, (list, tuple)):
                return None
            
            if self.min_items is not None and len(value) < self.min_items:
                return ValidationError(
                    error_code="SCHEMA_ARR_001",
                    error_type="too_few_items",
                    field_name=path,
                    message=f"Pole {path} ma zbyt malo elementów (min: {self.min_items}, aktualnie: {len(value)})",
                    severity="error"
                )
            
            if self.max_items is not None and len(value) > self.max_items:
                return ValidationError(
                    error_code="SCHEMA_ARR_002",
                    error_type="too_many_items",
                    field_name=path,
                    message=f"Pole {path} ma zbyt duzo elementów (max: {self.max_items}, aktualnie: {len(value)})",
                    severity="error"
                )
            
            if self.unique_items and len(value) != len(set(value)):
                return ValidationError(
                    error_code="SCHEMA_ARR_003",
                    error_type="duplicate_items",
                    field_name=path,
                    message=f"Pole {path} zawiera duplikaty",
                    severity="error"
                )
            
            # Walidacja elementów
            if self.items:
                for i, item in enumerate(value):
                    error = self.items.validate(item, f"{path}[{i}]")
                    if error:
                        return error
        
        return None


@dataclass
class MessageSchema:
    """
    Schemat wiadomosci SSIMessage.
    
    Odpowiedzialnosc:
    - Definicja schematu dla konkretnego typu wiadomosci
    - Walidacja wiadomosci wg schematu
    """
    schema_id: str
    description: str
    process_type: Optional[str] = None  # Typ procesu dla którego schemat sie stosuje
    
    # Definicja pól
    fields: Dict[str, SchemaField] = field(default_factory=dict)
    
    # Wymagane pola
    required_fields: Set[str] = field(default_factory=set)
    
    # Pola only read
    read_only_fields: Set[str] = field(default_factory=set)
    
    # Zaleznosci miedzy polami
    dependencies: Dict[str, Set[str]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Inicjalizacja po utworzeniu."""
        # Uaktualnienie required w SchemaField
        for field_name in self.required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
    
    def validate(self, message: SSIMessage) -> ValidationReport:
        """
        Walidacja wiadomosci wg schematu.
        
        Args:
            message: Wiadomosc do zwalidowania
            
        Returns:
            ValidationReport: Raport z walidacji
        """
        report = ValidationReport(
            message_id=message.message_id,
            is_valid=True,
            validation_level=ValidationLevel.STANDARD
        )
        
        # Sprawdzenie czy schemat dotyczy tej wiadomosci
        if self.process_type:
            process_type = message.process_type.value if hasattr(message.process_type, 'value') else str(message.process_type)
            if process_type != self.process_type:
                # Schemat nie dotyczy tej wiadomosci
                return report
        
        # Sprawdzenie pol wymaganych
        for field_name in self.required_fields:
            if not hasattr(message, field_name) or getattr(message, field_name) is None:
                report.add_error(ValidationError(
                    error_code="SCHEMA_REQ_002",
                    error_type="missing_required_field",
                    field_name=field_name,
                    message=f"Brak wymaganego pola: {field_name}",
                    severity="error"
                ))
        
        # Walidacja pól payload
        if message.payload:
            self._validate_payload(message.payload, "payload", report)
        
        # Walidacja zaleznosci
        self._validate_dependencies(message, report)
        
        return report
    
    def _validate_payload(
        self, 
        payload: Dict[str, Any], 
        path: str, 
        report: ValidationReport
    ) -> None:
        """Walidacja payload wg schematu."""
        for field_name, field_schema in self.fields.items():
            if field_name in payload:
                error = field_schema.validate(payload[field_name], f"{path}.{field_name}")
                if error:
                    report.add_error(error)
            elif field_schema.required:
                report.add_error(ValidationError(
                    error_code="SCHEMA_REQ_003",
                    error_type="missing_field",
                    field_name=f"{path}.{field_name}",
                    message=f"Brak wymaganego pola w payload: {field_name}",
                    severity="error"
                ))
        
        # Sprawdzenie dodatkowych pól
        allowed_fields = set(self.fields.keys())
        if payload:
            extra_fields = set(payload.keys()) - allowed_fields
            if extra_fields and not any(f.additional_properties for f in self.fields.values()):
                for field_name in extra_fields:
                    report.add_warning(ValidationError(
                        error_code="SCHEMA_EXTRA_001",
                        error_type="extra_field",
                        field_name=f"{path}.{field_name}",
                        message=f"N Linienoczekiwane pole w payload: {field_name}",
                        severity="warning"
                    ))
    
    def _validate_dependencies(
        self, 
        message: SSIMessage, 
        report: ValidationReport
    ) -> None:
        """Walidacja zaleznosci miedzy polami."""
        for field_name, dependencies in self.dependencies.items():
            if hasattr(message, field_name) and getattr(message, field_name) is not None:
                for dep_field in dependencies:
                    if not hasattr(message, dep_field) or getattr(message, dep_field) is None:
                        report.add_error(ValidationError(
                            error_code="SCHEMA_DEP_001",
                            error_type="missing_dependency",
                            field_name=dep_field,
                            message=f"Pole {field_name} wymaga pola {dep_field}",
                            severity="error"
                        ))


class SchemaValidator:
    """
    Walidator schematow wiadomosci.
    
    Odpowiedzialnosc:
    - Zarzadzanie schematami wiadomosci
    - Rejestracja i usuwanie schematów
    - Walidacja wiadomosci z uzyciem zarejestrowanych schematów
    """
    
    def __init__(self):
        """Inicjalizacja walidatora schematow."""
        self._schemas: Dict[str, MessageSchema] = {}
        self._schemas_by_process_type: Dict[str, List[str]] = {}
        self._lock = threading.RLock()
        logger.info("SchemaValidator zainicjalizowany")
    
    def register_schema(self, schema: MessageSchema) -> str:
        """
        Rejestracja nowego schematu.
        
        Args:
            schema: Schemat do zarejestrowania
            
        Returns:
            str: ID zarejestrowanego schematu
        """
        with self._lock:
            if schema.schema_id in self._schemas:
                logger.warning(f"Schemat o ID {schema.schema_id} zostanie nadpisany")
            
            self._schemas[schema.schema_id] = schema
            
            # Indeksowanie wedlug typu procesu
            if schema.process_type:
                if schema.process_type not in self._schemas_by_process_type:
                    self._schemas_by_process_type[schema.process_type] = []
                if schema.schema_id not in self._schemas_by_process_type[schema.process_type]:
                    self._schemas_by_process_type[schema.process_type].append(schema.schema_id)
            
            logger.debug(f"Zarejestrowano schemat: {schema.schema_id}")
            return schema.schema_id
    
    def register_schemas(self, schemas: List[MessageSchema]) -> List[str]:
        """
        Rejestracja wielu schematów.
        
        Args:
            schemas: Lista schematów do zarejestrowania
            
        Returns:
            List[str]: Lista ID zarejestrowanych schematów
        """
        return [self.register_schema(schema) for schema in schemas]
    
    def unregister_schema(self, schema_id: str) -> bool:
        """
        Wyrejestrowanie schematu.
        
        Args:
            schema_id: ID schematu do wyrejestrowania
            
        Returns:
            bool: Czy wyrejestrowano pomyślnie
        """
        with self._lock:
            if schema_id not in self._schemas:
                return False
            
            # Usuniecie z indeksów
            schema = self._schemas[schema_id]
            if schema.process_type and schema.process_type in self._schemas_by_process_type:
                if schema_id in self._schemas_by_process_type[schema.process_type]:
                    self._schemas_by_process_type[schema.process_type].remove(schema_id)
            
            del self._schemas[schema_id]
            logger.debug(f"Wyrejestrowano schemat: {schema_id}")
            return True
    
    def get_schema(self, schema_id: str) -> Optional[MessageSchema]:
        """
        Pobranie schematu po ID.
        
        Args:
            schema_id: ID schematu
            
        Returns:
            Optional[MessageSchema]: Schemat lub None
        """
        with self._lock:
            return self._schemas.get(schema_id)
    
    def get_schemas_by_process_type(self, process_type: str) -> List[MessageSchema]:
        """
        Pobranie schematów dla danego typu procesu.
        
        Args:
            process_type: Typ procesu
            
        Returns:
            List[MessageSchema]: Lista schematów
        """
        with self._lock:
            schema_ids = self._schemas_by_process_type.get(process_type, [])
            return [self._schemas[sid] for sid in schema_ids if sid in self._schemas]
    
    def get_all_schemas(self) -> List[MessageSchema]:
        """
        Pobranie wszystkich schematów.
        
        Returns:
            List[MessageSchema]: Lista wszystkich schematów
        """
        with self._lock:
            return list(self._schemas.values())
    
    def clear_schemas(self) -> None:
        """Wyczyszczenie wszystkich schematów."""
        with self._lock:
            self._schemas.clear()
            self._schemas_by_process_type.clear()
            logger.info("Wyczyszczono wszystkie schematy")
    
    def validate(
        self, 
        message: SSIMessage, 
        schema_id: Optional[str] = None
    ) -> ValidationReport:
        """
        Walidacja wiadomosci z uzyciem schematu.
        
        Args:
            message: Wiadomosc do zwalidowania
            schema_id: ID schematu do uzycia (opcjonalnie, auto-wybór jeśli None)
            
        Returns:
            ValidationReport: Raport z walidacji
        """
        with self._lock:
            # Wybór schematu
            if schema_id:
                schema = self._schemas.get(schema_id)
                if not schema:
                    return ValidationReport(
                        message_id=message.message_id,
                        is_valid=False,
                        validation_level=ValidationLevel.STANDARD,
                        result=ValidationReport.ValidationResult.INVALID
                    )
            else:
                # Auto-wybór schematu na podstawie process_type
                process_type = message.process_type.value if hasattr(message.process_type, 'value') else str(message.process_type)
                schemas = self._schemas_by_process_type.get(process_type, [])
                
                if not schemas:
                    # Brak schematu dla tego typu procesu - walidacja pominieta
                    return ValidationReport(
                        message_id=message.message_id,
                        is_valid=True,
                        validation_level=ValidationLevel.STANDARD,
                        result=ValidationReport.ValidationResult.VALID
                    )
                
                schema = self._schemas.get(schemas[0])
            
            if not schema:
                return ValidationReport(
                    message_id=message.message_id,
                    is_valid=True,
                    validation_level=ValidationLevel.STANDARD,
                    result=ValidationReport.ValidationResult.VALID
                )
            
            return schema.validate(message)
    
    def add_schema_to_message_type(
        self, 
        schema: MessageSchema, 
        process_type: str
    ) -> str:
        """
        Dodanie schematu do konkretnego typu procesu.
        
        Args:
            schema: Schemat
            process_type: Typ procesu
            
        Returns:
            str: ID schematu
        """
        schema.process_type = process_type
        return self.register_schema(schema)


# Funkcje helper

def get_schema_validator() -> SchemaValidator:
    """Pobranie instancji walidatora schematów."""
    if not hasattr(get_schema_validator, '_instance'):
        get_schema_validator._instance = SchemaValidator()
    return get_schema_validator._instance


def reset_schema_validator() -> None:
    """Reset instancji walidatora schematów."""
    if hasattr(get_schema_validator, '_instance'):
        get_schema_validator._instance.clear_schemas()
        del get_schema_validator._instance


# Funkcje do tworzenia pól schematu

def string_field(
    name: str,
    description: str = "",
    required: bool = False,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    pattern: Optional[str] = None,
    default: Optional[str] = None
) -> SchemaField:
    """Utworzenie pola typu string."""
    return SchemaField(
        name=name,
        schema_type=SchemaType.STRING,
        description=description,
        required=required,
        min_length=min_length,
        max_length=max_length,
        pattern=pattern,
        default=default
    )


def integer_field(
    name: str,
    description: str = "",
    required: bool = False,
    minimum: Optional[int] = None,
    maximum: Optional[int] = None,
    default: Optional[int] = None
) -> SchemaField:
    """Utworzenie pola typu integer."""
    return SchemaField(
        name=name,
        schema_type=SchemaType.INTEGER,
        description=description,
        required=required,
        minimum=minimum,
        maximum=maximum,
        default=default
    )


def float_field(
    name: str,
    description: str = "",
    required: bool = False,
    minimum: Optional[float] = None,
    maximum: Optional[float] = None,
    default: Optional[float] = None
) -> SchemaField:
    """Utworzenie pola typu float."""
    return SchemaField(
        name=name,
        schema_type=SchemaType.FLOAT,
        description=description,
        required=required,
        minimum=minimum,
        maximum=maximum,
        default=default
    )


def boolean_field(
    name: str,
    description: str = "",
    required: bool = False,
    default: Optional[bool] = None
) -> SchemaField:
    """Utworzenie pola typu boolean."""
    return SchemaField(
        name=name,
        schema_type=SchemaType.BOOLEAN,
        description=description,
        required=required,
        default=default
    )


def enum_field(
    name: str,
    allowed_values: Set[Any],
    description: str = "",
    required: bool = False,
    default: Optional[Any] = None
) -> SchemaField:
    """Utworzenie pola typu enum."""
    return SchemaField(
        name=name,
        schema_type=SchemaType.ENUM,
        description=description,
        required=required,
        allowed_values=allowed_values,
        default=default
    )


def object_field(
    name: str,
    properties: Dict[str, SchemaField],
    description: str = "",
    required: bool = False,
    default: Optional[Dict[str, Any]] = None,
    additional_properties: bool = True
) -> SchemaField:
    """Utworzenie pola typu object."""
    return SchemaField(
        name=name,
        schema_type=SchemaType.OBJECT,
        description=description,
        required=required,
        properties=properties,
        default=default,
        additional_properties=additional_properties
    )


def array_field(
    name: str,
    items: SchemaField,
    description: str = "",
    required: bool = False,
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    unique_items: bool = False,
    default: Optional[List[Any]] = None
) -> SchemaField:
    """Utworzenie pola typu array."""
    return SchemaField(
        name=name,
        schema_type=SchemaType.ARRAY,
        description=description,
        required=required,
        items=items,
        min_items=min_items,
        max_items=max_items,
        unique_items=unique_items,
        default=default
    )


# Import threading for the lock
import threading
