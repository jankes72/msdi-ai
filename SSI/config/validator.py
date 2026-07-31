"""
SSI Config Validator - Walidacja konfiguracji systemu SSI

Wersja: 1.0
Data: 2026-07-31
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from .settings import SSISettings, get_settings
from .paths import SSIPaths, get_paths

logger = logging.getLogger(__name__)


class ConfigValidationError(Exception):
    """Wyjątek walidacji konfiguracji."""
    
    def __init__(self, field_name: str, field_value: Any, message: str):
        self.field_name = field_name
        self.field_value = field_value
        self.message = message
        super().__init__(f"{field_name}={field_value}: {message}")


class SSIConfigValidator:
    """Walidator konfiguracji SSI."""
    
    def __init__(self, settings: Optional[SSISettings] = None, paths: Optional[SSIPaths] = None):
        self.settings = settings or get_settings()
        self.paths = paths or get_paths()
        self.errors: List[ConfigValidationError] = []
    
    def validate(self) -> bool:
        """
        Waliduje konfiguracje.
        
        Returns:
            True jeśli konfiguracja jest poprawna, False w przeciwnym wypadku
        """
        self.errors.clear()
        
        try:
            self._validate_path_existence()
            self._validate_feature_flags()
            self._validate_path_format()
            
            if self.errors:
                for error in self.errors:
                    logger.error(str(error))
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error during config validation: {e}")
            return False
    
    def _validate_path_existence(self) -> None:
        """Waliduje istnienie wymaganych katalogów."""
        # Jeśli v2 jest włączone, sprawdź katalog v2
        if self.settings.v2_enabled:
            v2_path = self.paths.get_absolute_path(self.paths.v2_path)
            if not v2_path.exists():
                logger.warning(f" Directory does not exist (will be created on demand): {v2_path}")
        
        # Jeśli v3 jest włączone, sprawdź katalog v3
        if self.settings.v3_enabled:
            v3_path = self.paths.get_absolute_path(self.paths.v3_path)
            if not v3_path.exists():
                logger.warning(f" Directory does not exist (will be created on demand): {v3_path}")
        
        # Jeśli v4 jest włączone, sprawdź katalog v4
        if self.settings.v4_enabled:
            v4_path = self.paths.get_absolute_path(self.paths.v4_path)
            if not v4_path.exists():
                logger.warning(f" Directory does not exist (will be created on demand): {v4_path}")
        
        # Sprawdź catalogi danych
        data_path = self.paths.get_absolute_path(self.paths.data_root)
        if not data_path.exists():
            logger.warning(f" Data directory does not exist (will be created on demand): {data_path}")
    
    def _validate_feature_flags(self) -> None:
        """Waliduje flagi funkcji."""
        # Sprawdź czy niezaimplementowane moduły są wyłączone
        if self.settings.strategy_enabled:
            self.errors.append(
                ConfigValidationError(
                    field_name="strategy_enabled",
                    field_value=self.settings.strategy_enabled,
                    message="Module strategy not implemented, should be disabled"
                )
            )
        
        if self.settings.labs_enabled:
            self.errors.append(
                ConfigValidationError(
                    field_name="labs_enabled",
                    field_value=self.settings.labs_enabled,
                    message="Module laboratories not implemented, should be disabled"
                )
            )
        
        if self.settings.feedback_enabled:
            self.errors.append(
                ConfigValidationError(
                    field_name="feedback_enabled",
                    field_value=self.settings.feedback_enabled,
                    message="Module feedback not implemented, should be disabled"
                )
            )
        
        if self.settings.decision_engine_enabled:
            self.errors.append(
                ConfigValidationError(
                    field_name="decision_engine_enabled",
                    field_value=self.settings.decision_engine_enabled,
                    message="Module decision_engine not implemented, should be disabled"
                )
            )
    
    def _validate_path_format(self) -> None:
        """Waliduje format ścieżek - sprawdza podwójne prefiksy."""
        # Sprawdź czy ścieżki nie zawierają podwójnego prefiksu SSI/SSI
        all_paths = [
            self.paths.v2_path, self.paths.v3_path, self.paths.v4_path,
            self.paths.strategy_path, self.paths.laboratories_path,
            self.paths.feedback_path, self.paths.decision_path,
            self.paths.evolution_path, self.paths.data_root,
            self.paths.raw_data_path, self.paths.processed_data_path,
            self.paths.worlds_data_path, self.paths.results_data_path,
            self.paths.config_path, self.paths.utils_path, self.paths.tests_path
        ]
        
        for path in all_paths:
            # path może być Path lub str, konwertujemy na str
            path_str = str(path)
            if "SSI/SSI" in path_str or "SSI\\SSI" in path_str:
                self.errors.append(
                    ConfigValidationError(
                        field_name=f"path_{path_str}",
                        field_value=path_str,
                        message=f"Path contains double SSI prefix: {path_str}"
                    )
                )
    
    def validate_path_no_ssi_ssi(self, path_str: str) -> bool:
        """
        Check if a path does NOT contain double SSI prefix.
        
        Args:
            path_str: Path to check
            
        Returns:
            True if path is valid (no SSI/SSI)
        """
        return "SSI/SSI" not in path_str and "SSI\\SSI" not in path_str
    
    def get_errors(self) -> List[ConfigValidationError]:
        """Returns list of validation errors."""
        return self.errors


def validate_config() -> bool:
    """
    Convenience function - validates system configuration.
    
    Returns:
        True if configuration is valid
        
    Raises:
        ConfigValidationError: If validation fails
    """
    validator = SSIConfigValidator()
    if not validator.validate():
        errors = validator.get_errors()
        error_messages = "\n".join(str(e) for e in errors)
        raise ConfigValidationError(
            field_name="configuration",
            field_value="full_config",
            message=f"Config validation failed:\n{error_messages}"
        )
    return True


def validate_paths() -> bool:
    """
    Convenience function - validates paths for double prefixes.
    
    Returns:
        True if all paths are valid
    """
    validator = SSIConfigValidator()
    validator._validate_path_format()
    
    if validator.errors:
        error_messages = "\n".join(str(e) for e in validator.errors)
        raise ConfigValidationError(
            field_name="paths",
            field_value="all_paths",
            message=f"Paths contain double prefixes:\n{error_messages}"
        )
    return True
