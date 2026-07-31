"""
SSI Data Module

Wersja: 1.0
Data: 2026-07-31
"""

from .policies import (
    DataSplitPolicy,
    SplitRatio,
    SplitResult,
    DataSplitter,
    DataQualityPolicy,
    DataQualityLevel,
    DataRetentionPolicy,
    RetentionPeriod,
    DataAccessPolicy,
    standard_split,
    validate_split_result,
    create_standard_data_policies,
)

__all__ = [
    'DataSplitPolicy',
    'SplitRatio',
    'SplitResult',
    'DataSplitter',
    'DataQualityPolicy',
    'DataQualityLevel',
    'DataRetentionPolicy',
    'RetentionPeriod',
    'DataAccessPolicy',
    'standard_split',
    'validate_split_result',
    'create_standard_data_policies',
]
