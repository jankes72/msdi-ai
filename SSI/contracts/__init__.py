"""
SSI Contracts Module

Wersjonowane kontrakty danych pomiedzy V2, V3 i V4

Wersja: 1.0
Data: 2026-07-31
"""

from .data_contracts import (
    V2ToV3Contract,
    V3ToV4Contract,
    DataContract,
    ContractValidationError,
    ContractVersion,
    ContractMetadata,
)

from .version_identifiers import (
    DataVersion,
    ModelVersion,
    ConfigVersion,
    ResultVersion,
    LineageInfo,
)

from .policies import (
    DataSplitPolicy,
    SplitRatio,
    SplitResult,
    DataSplitter,
    standard_split,
    validate_split_result,
)

from .validation import (
    validate_contract,
    ContractValidator,
    VersionCompatibilityChecker,
)
from .migration import (
    CompatibilityLevel,
    MigrationStrategy,
    CompatibilityRule,
    CompatibilityPolicy,
    MigrationPolicy,
    create_default_compatibility_policy,
    create_default_migration_policy,
)

__all__ = [
    # Kontrakty danych
    'V2ToV3Contract',
    'V3ToV4Contract', 
    'DataContract',
    'ContractValidationError',
    'ContractVersion',
    'ContractMetadata',
    
    # Identyfikatory wersji
    'DataVersion',
    'ModelVersion',
    'ConfigVersion',
    'ResultVersion',
    'LineageInfo',
    
    # Polityki
    'DataSplitPolicy',
    'SplitRatio',
    'SplitResult',
    'DataSplitter',
    'standard_split',
    'validate_split_result',
    
    # Walidacja
    'validate_contract',
    'ContractValidator',
    'VersionCompatibilityChecker',
    
    # Migracja
    'CompatibilityLevel',
    'MigrationStrategy',
    'CompatibilityRule',
    'CompatibilityPolicy',
    'MigrationPolicy',
    'create_default_compatibility_policy',
    'create_default_migration_policy',
]
