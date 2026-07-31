"""
SSI (Self Learning Intelligence Ecosystem)
Main module for SSI - Self Learning Intelligence

This module provides structure for autonomous ecosystem of learning agents
that analyzes, understands and makes decisions in intelligent and adaptive way.

Architecture:
- V2 Model Laboratory: Models interpreting the world
- V3 World Memory System: Knowledge map of worlds and patterns
- V4 Agent Evolution: Autonomous decision units
- Strategy Intelligence Engine: System for creation and evolution of strategies
- Decision Laboratories: Experimental environments
- Feedback Loop: System for continuous improvement

Version: 1.1
Date: 2026-07-31
"""

# Inicjalizacja centralnego logowania
from .core.logging_config import setup_logging, get_logger
setup_logging(level=None, json_format=False)  # Domyślna konfiguracja

from .core import SSISystem, SSIModule, SSIComponent
from .config import SSIConfig
from .config.settings import get_settings
from .config.validator import validate_config, ConfigValidationError
from . import data
from . import v2
# Temporarily commented to allow V4 development
# from . import v3
from . import v4

# Walidacja konfiguracji podczas startu systemu
# Wywołuje się przy pierwszym imporcie SSI
try:
    validate_config()
    _CONFIG_VALID = True
except ConfigValidationError as e:
    import warnings
    warnings.warn(f"Configuration validation warning: {e}", RuntimeWarning)
    _CONFIG_VALID = False
except Exception as e:
    import warnings
    warnings.warn(f"Configuration validation failed: {e}", RuntimeWarning)
    _CONFIG_VALID = False

__version__ = "1.1.0"
__author__ = "SSI System"

# Export of main classes
__all__ = [
    'SSISystem',
    'SSIModule', 
    'SSIComponent',
    'SSIConfig',
    'data',
    'v2',
    'v3',
    'v4',
    '__version__',
    '__author__'
]
