"""
SSI Configuration Module
Moduł konfiguracji systemu SSI

Wersja: 1.0
Data: 2026-07-28
"""

from .settings import SSISettings, get_settings, reset_settings
from .parameters import SSIParameters, get_parameters, reset_parameters
from .paths import SSIPaths, get_paths, reset_paths

__all__ = [
    'SSISettings', 'get_settings', 'reset_settings',
    'SSIParameters', 'get_parameters', 'reset_parameters',
    'SSIPaths', 'get_paths', 'reset_paths'
]
