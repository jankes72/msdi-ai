"""
SSI Settings - Ustawienia systemu SSI

Wersja: 1.0
Data: 2026-07-28
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class SSISettings:
    """Główna klasa ustawień systemu SSI"""
    system_name: str = "Self Learning Intelligence Ecosystem"
    version: str = "1.0.0"
    debug: bool = True
    logging_level: str = "INFO"
    
    v2_enabled: bool = True
    v2_training_split: float = 0.6
    
    v3_enabled: bool = True
    v3_world_cache_size: int = 100
    
    v4_enabled: bool = True
    v4_initial_population: int = 3
    
    # Modules not implemented - disabled by default
    strategy_enabled: bool = False
    labs_enabled: bool = False
    feedback_enabled: bool = False
    decision_engine_enabled: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "system_name": self.system_name,
            "version": self.version,
            "debug": self.debug,
            "logging_level": self.logging_level,
            "v2_enabled": self.v2_enabled,
            "v3_enabled": self.v3_enabled,
            "v4_enabled": self.v4_enabled,
            "strategy_enabled": self.strategy_enabled,
            "labs_enabled": self.labs_enabled,
            "feedback_enabled": self.feedback_enabled,
            "decision_engine_enabled": self.decision_engine_enabled
        }
    
    def load_from_file(self, file_path: str) -> bool:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                settings_dict = json.load(f)
                for key, value in settings_dict.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
            return True
        except Exception as e:
            logger.error(f"Błąd ładowania ustawień: {e}")
            return False
    
    def save_to_file(self, file_path: str) -> bool:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Błąd zapisu ustawień: {e}")
            return False


settings_instance: Optional[SSISettings] = None


def get_settings() -> SSISettings:
    global settings_instance
    if settings_instance is None:
        settings_instance = SSISettings()
    return settings_instance


def reset_settings() -> None:
    global settings_instance
    settings_instance = None
