"""
SSI Data Policies - Polityki zarządzania danymi

Wersja: 1.0
Data: 2026-07-31

Zawiera:
- DataSplitPolicy: Polityka podziału danych na train/validation/observation
- DataQualityPolicy: Polityka jakości danych
- DataRetentionPolicy: Polityka przechowywania danych
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Callable
from enum import Enum, auto
import random
import numpy as np
from collections import defaultdict
from datetime import datetime, timedelta
import sys

# Re-export z SSI.contracts.policies dla spójności
from SSI.contracts.policies import (
    DataSplitPolicy,
    SplitRatio,
    SplitResult,
    DataSplitter,
    standard_split,
    validate_split_result,
)

# Dodatkowe definicje specyficzne dla modułu data

class DataQualityLevel(Enum):
    """Poziomy jakości danych."""
    EXCELLENT = auto()    # Dane pełne, zwalidowane, wysoka jakość
    GOOD = auto()         # Dane z drobnymi lukami, zwalidowane
    FAIR = auto()         # Dane z lukami, częściowo zwalidowane
    POOR = auto()         # Dane niepełne, niezwalidowane
    UNKNOWN = auto()      # Jakość nieznana


@dataclass
class DataQualityPolicy:
    """
    Polityka jakości danych.
    
    Definiuje wymagania jakościowe dla różnych typów danych.
    """
    # Minimalna jakość dla różnych zastosowań
    min_quality_for_training: DataQualityLevel = DataQualityLevel.GOOD
    min_quality_for_validation: DataQualityLevel = DataQualityLevel.GOOD
    min_quality_for_observation: DataQualityLevel = DataQualityLevel.FAIR
    min_quality_for_production: DataQualityLevel = DataQualityLevel.EXCELLENT
    
    # Wymagania dla pól
    required_fields: List[str] = field(default_factory=list)
    optional_fields: List[str] = field(default_factory=list)
    
    # Walidatory dla pól
    field_validators: Dict[str, Callable] = field(default_factory=dict)
    
    def validate_data(self, data: Dict[str, Any]) -> Tuple[bool, DataQualityLevel, List[str]]:
        """
        Waliduje pojedynczy rekord danych.
        
        Args:
            data: Rekord danych do walidacji
            
        Returns:
            Tuple: (is_valid, quality_level, errors)
        """
        errors = []
        quality_score = 0
        
        # Sprawdź wymagane pola
        for field_name in self.required_fields:
            if field_name not in data or data[field_name] is None:
                errors.append(f"Brak wymaganego pola: {field_name}")
            else:
                quality_score += 1
        
        # Uruchom walidatory
        for field_name, validator in self.field_validators.items():
            if field_name in data:
                try:
                    is_valid = validator(data[field_name])
                    if is_valid:
                        quality_score += 1
                    else:
                        errors.append(f"Nieprawidłowa wartość pola: {field_name}")
                except Exception as e:
                    errors.append(f"Błąd walidacji pola {field_name}: {e}")
        
        # Oblicz poziom jakości
        total_checks = len(self.required_fields) + len(self.field_validators)
        if total_checks == 0:
            quality_level = DataQualityLevel.UNKNOWN
        else:
            quality_ratio = quality_score / total_checks
            if quality_ratio >= 0.9:
                quality_level = DataQualityLevel.EXCELLENT
            elif quality_ratio >= 0.7:
                quality_level = DataQualityLevel.GOOD
            elif quality_ratio >= 0.5:
                quality_level = DataQualityLevel.FAIR
            else:
                quality_level = DataQualityLevel.POOR
        
        return len(errors) == 0, quality_level, errors
    
    def filter_by_quality(
        self, 
        data: List[Dict[str, Any]], 
        min_level: DataQualityLevel
    ) -> List[Dict[str, Any]]:
        """
        Filtrowanie danych po minimalnym poziomie jakości.
        
        Args:
            data: Lista rekordów danych
            min_level: Minimalny poziom jakości
            
        Returns:
            Lista zfiltrowanych rekordów
        """
        level_values = {
            DataQualityLevel.EXCELLENT: 5,
            DataQualityLevel.GOOD: 4,
            DataQualityLevel.FAIR: 3,
            DataQualityLevel.POOR: 2,
            DataQualityLevel.UNKNOWN: 1
        }
        
        min_value = level_values[min_level]
        filtered = []
        
        for record in data:
            _, quality, _ = self.validate_data(record)
            if level_values.get(quality, 0) >= min_value:
                filtered.append(record)
        
        return filtered


class RetentionPeriod(Enum):
    """Okresy przechowywania danych."""
    ONE_DAY = timedelta(days=1)
    ONE_WEEK = timedelta(days=7)
    ONE_MONTH = timedelta(days=30)
    THREE_MONTHS = timedelta(days=90)
    SIX_MONTHS = timedelta(days=180)
    ONE_YEAR = timedelta(days=365)
    FOREVER = None


@dataclass
class DataRetentionPolicy:
    """
    Polityka przechowywania danych.
    
    Definiuje jak długo różne typy danych powinny być przechowywane.
    """
    # Okresy Retencji dla różnych typów danych
    retention_periods: Dict[str, Optional[timedelta]] = field(default_factory=dict)
    
    # Domyślny okres retencji
    default_retention: Optional[timedelta] = RetentionPeriod.ONE_YEAR.value
    
    # Czy automatycznie usuwać przeterminowane dane
    auto_purge: bool = False
    
    def should_retain(self, data_type: str, created_at: datetime) -> bool:
        """
        Sprawdza czy dane powinny zostać zachowane.
        
        Args:
            data_type: Typ danych
            created_at: Data utworzenia
            
        Returns:
            True jeśli dane powinny zostać zachowane
        """
        retention_period = self.retention_periods.get(data_type, self.default_retention)
        
        if retention_period is None:
            return True  # Przechowuj wiecznie
        
        age = datetime.now() - created_at
        return age <= retention_period
    
    def get_expired_data(
        self, 
        data_records: List[Dict[str, Any]],
        data_type: str
    ) -> List[Dict[str, Any]]:
        """
        Zwraca listę rekordów, które powinny zostać usunięte.
        
        Args:
            data_records: Lista rekordów danych
            data_type: Typ danych
            
        Returns:
            Lista rekordów do usunięcia
        """
        expired = []
        for record in data_records:
            created_at_str = record.get("created_at", record.get("timestamp", ""))
            try:
                created_at = datetime.fromisoformat(created_at_str)
                if not self.should_retain(data_type, created_at):
                    expired.append(record)
            except (ValueError, TypeError):
                # Jeśli data nie może zostać sparsowana, nie usuwamy
                pass
        return expired


@dataclass
class DataAccessPolicy:
    """
    Polityka dostępu do danych.
    
    Definiuje kto może dostępować jakie dane.
    """
    # Uprawnienia: role -> lista typów danych
    permissions: Dict[str, List[str]] = field(default_factory=dict)
    
    # Domyślne uprawnienia
    default_permissions: List[str] = field(default_factory=list)
    
    def can_access(
        self, 
        role: str, 
        data_type: str
    ) -> bool:
        """
        Sprawdza czy rola ma dostęp do danego typu danych.
        
        Args:
            role: Rola użytkownika
            data_type: Typ danych
            
        Returns:
            True jeśli dostęp jest dozwolony
        """
        if role in self.permissions:
            return data_type in self.permissions[role]
        
        return data_type in self.default_permissions
    
    def get_accessible_types(self, role: str) -> List[str]:
        """
        Zwraca listę typów danych dostępnych dla roli.
        
        Args:
            role: Rola użytkownika
            
        Returns:
            Lista dostępnych typów danych
        """
        if role in self.permissions:
            return self.permissions[role]
        return self.default_permissions


# =============================================================================
# FABRYKI I FUNKCJE WYGODNE
# =============================================================================

def create_standard_data_policies() -> Tuple[
    DataSplitPolicy, 
    DataQualityPolicy, 
    DataRetentionPolicy,
    DataAccessPolicy
]:
    """
    Tworzy zestaw standardowych polityk danych.
    
    Returns:
        Tuple: (DataSplitPolicy, DataQualityPolicy, DataRetentionPolicy, DataAccessPolicy)
    """
    # Polityka podziału
    split_policy = DataSplitPolicy.standard_50_10_40()
    
    # Polityka jakości
    quality_policy = DataQualityPolicy(
        required_fields=["id", "timestamp"],
        field_validators={
            "confidence": lambda x: 0.0 <= float(x) <= 1.0,
            "accuracy": lambda x: 0.0 <= float(x) <= 1.0,
        }
    )
    
    # Polityka retencji
    retention_policy = DataRetentionPolicy(
        retention_periods={
            "raw": RetentionPeriod.ONE_MONTH.value,
            "processed": RetentionPeriod.ONE_YEAR.value,
            "train": RetentionPeriod.FOREVER.value,
            "validation": RetentionPeriod.FOREVER.value,
            "observation": RetentionPeriod.SIX_MONTHS.value,
            "logs": RetentionPeriod.ONE_MONTH.value,
            "temp": RetentionPeriod.ONE_DAY.value,
        },
        default_retention=RetentionPeriod.ONE_YEAR.value,
        auto_purge=False
    )
    
    # Polityka dostępu
    access_policy = DataAccessPolicy(
        permissions={
            "admin": ["raw", "processed", "train", "validation", "observation", "logs"],
            "researcher": ["processed", "train", "validation", "observation"],
            "analyst": ["processed", "train", "validation"],
            "user": ["processed", "train"],
        },
        default_permissions=["processed"]
    )
    
    return split_policy, quality_policy, retention_policy, access_policy


# =============================================================================
# TESTY
# =============================================================================

if __name__ == "__main__":
    import logging
    from SSI.core.logging_config import (
        setup_logging, get_logger, set_correlation_id, generate_correlation_id
    )
    
    # Skonfiguruj logging
    setup_logging(level=logging.INFO, json_format=False)
    logger = get_logger(__name__)
    
    # Ustaw correlation_id
    correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)
    
    logger.info("Testing SSI Data Policies...", extra={"correlation_id": correlation_id})
    
    # Test polityki podziału
    logger.info("[1] Testing DataSplitPolicy:", extra={"correlation_id": correlation_id})
    policy = DataSplitPolicy.standard_50_10_40()
    logger.info(f"   Policy: {policy.policy_name}", extra={"correlation_id": correlation_id})
    logger.info(f"   Ratios: Train={policy.train_ratio}, Validation={policy.validation_ratio}, Observation={policy.observation_ratio}",
                extra={"correlation_id": correlation_id})
    
    # Test splittera
    data = list(range(100))
    splitter = DataSplitter(policy)
    result = splitter.split_data(data, seed=42)
    logger.info(f"   Split result: Train={len(result.train_data)}, Validation={len(result.validation_data)}, Observation={len(result.observation_data)}",
                extra={"correlation_id": correlation_id})
    
    # Walidacja
    try:
        validate_split_result(result, policy)
        logger.info("   ✓ Split validation passed", extra={"correlation_id": correlation_id})
    except ValueError as e:
        logger.error(f"   ✗ Split validation failed: {e}", extra={"correlation_id": correlation_id})
    
    # Test standard_split
    result2 = standard_split(data, seed=42)
    logger.info(f"   Standard split: Train={len(result2.train_data)}, Validation={len(result2.validation_data)}, Observation={len(result2.observation_data)}",
                extra={"correlation_id": correlation_id})
    
    # Test polityki jakości
    logger.info("[2] Testing DataQualityPolicy:", extra={"correlation_id": correlation_id})
    quality_policy = DataQualityPolicy(
        required_fields=["id", "value"],
        field_validators={"value": lambda x: 0 <= x <= 100}
    )
    
    test_data = {"id": "test1", "value": 50, "extra": "field"}
    is_valid, quality, errors = quality_policy.validate_data(test_data)
    logger.info(f"   Valid: {is_valid}, Quality: {quality.name}, Errors: {errors}",
                extra={"correlation_id": correlation_id})
    
    # Test polityki retencji
    logger.info("[3] Testing DataRetentionPolicy:", extra={"correlation_id": correlation_id})
    retention_policy = DataRetentionPolicy(
        retention_periods={
            "temp": RetentionPeriod.ONE_DAY.value,
            "log": RetentionPeriod.ONE_WEEK.value
        },
        default_retention=RetentionPeriod.ONE_MONTH.value
    )
    
    old_date = datetime.now() - RetentionPeriod.TWO_WEEKS.value
    new_date = datetime.now() - RetentionPeriod.ONE_DAY.value
    
    logger.info(f"   Temp data (old): should_retain={retention_policy.should_retain('temp', old_date)}",
                extra={"correlation_id": correlation_id})
    logger.info(f"   Temp data (new): should_retain={retention_policy.should_retain('temp', new_date)}",
                extra={"correlation_id": correlation_id})
    logger.info(f"   Log data (old): should_retain={retention_policy.should_retain('log', old_date)}",
                extra={"correlation_id": correlation_id})
    
    # Sprawdź, czy były błędy w testach
    test_failed = not is_valid or errors
    
    if test_failed:
        logger.error("Some Data Policies tests FAILED!",
                      extra={"correlation_id": correlation_id})
        sys.exit(1)
    
    logger.info("✓ All tests passed!", extra={"correlation_id": correlation_id})
