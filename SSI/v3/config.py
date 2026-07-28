"""
SSI V3 Configuration - Centralna konfiguracja systemu V3

Moduł odpowiedzialny za:
- Centralne zarządzanie konfiguracją V3
- Walidację ustawień konfiguracyjnych
- Integrację z innymi warstwami systemu

Zgodnie z:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 3 (V3 World System)
- 10_IMPLEMENTATION_MAP.md Etap 3C (Integration)
- PROJECT_RULES.md (Zasady tworzenia modułów)

Architektura:
V3Config jest centralnym punktem konfiguracji dla:
- World Integration (V2 → V3)
- V3 to V4 Bridge (V3 → V4)
- Memory System
- World System

Wymagania:
- Wszystkie wartości jako dataclass (PROJECT_RULES.md)
- Walidacja konfiguracji
- Obsługa domyślnych wartości

Wersja: 1.0
Data: 2026-07-28
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import logging
import warnings

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMY KONFIGURACYJNE
# =============================================================================

class LogLevel(Enum):
    """Dozwolone poziomy logowania"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ValidationMode(Enum):
    """Tryby walidacji konfiguracji"""
    STRICT = "strict"      # Rygorystyczna walidacja (błędy)
    WARNING = "warning"    # Walidacja z ostrzeżeniami
    PERMISSIVE = "permissive"  # Pominichelnie błędów


# =============================================================================
# KONFIGURACJA INTEGRACJI (World Integration)
# =============================================================================

@dataclass
class IntegrationConfig:
    """
    Konfiguracja integracyjna V3.
    
    Odpowiedzialność:
    - Ustawienia przetwarzania partii danych
    - Walidacja i transformacja danych
    - Integracja z V2 i V4
    
    Zgodnie z WorldIntegrationConfig z world_integration.py
    """
    
    # Ustawienia przetwarzania
    BATCH_SIZE: int = 100
    PROCESSING_TIMEOUT: float = 30.0
    MAX_RETRIES: int = 3
    
    # Ustawienia walidacji
    VALIDATE_DATA: bool = True
    MIN_FIELDS: int = 5
    REQUIRED_FIELDS: List[str] = field(default_factory=lambda: [
        "mecz_id", "confidence", "predykcja"
    ])
    
    # Ustawienia transformacji
    NORMALIZE_VALUES: bool = True
    FILTER_DUPLICATES: bool = True
    
    # Ustawienia integracji
    AUTO_INTEGRATE: bool = True
    SAVE_TO_MEMORY: bool = True
    SEND_TO_V4: bool = False  # Domyślnie wyłączone - włącz w Sprint 5
    
    # Ustawienia logowania
    LOG_LEVEL: str = "INFO"
    TRACK_STATISTICS: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje konfigurację do dict"""
        return {
            "BATCH_SIZE": self.BATCH_SIZE,
            "PROCESSING_TIMEOUT": self.PROCESSING_TIMEOUT,
            "MAX_RETRIES": self.MAX_RETRIES,
            "VALIDATE_DATA": self.VALIDATE_DATA,
            "MIN_FIELDS": self.MIN_FIELDS,
            "REQUIRED_FIELDS": self.REQUIRED_FIELDS,
            "NORMALIZE_VALUES": self.NORMALIZE_VALUES,
            "FILTER_DUPLICATES": self.FILTER_DUPLICATES,
            "AUTO_INTEGRATE": self.AUTO_INTEGRATE,
            "SAVE_TO_MEMORY": self.SAVE_TO_MEMORY,
            "SEND_TO_V4": self.SEND_TO_V4,
            "LOG_LEVEL": self.LOG_LEVEL,
            "TRACK_STATISTICS": self.TRACK_STATISTICS
        }


# =============================================================================
# KONFIGURACJA MOSTU V3 → V4
# =============================================================================

@dataclass
class V4BridgeConfig:
    """
    Konfiguracja mostu V3 → V4.
    
    Odpowiedzialność:
    - Transfer wiedzy do agentów V4
    - Subskrypcje agentów
    - Filtrowanie danych dla V4
    
    Zgodnie z V3ToV4BridgeConfig z v3_to_v4_bridge.py
    """
    
    # Ustawienia transferu
    AUTO_SEND: bool = False
    BATCH_SIZE: int = 50
    
    # Ustawienia filtrów
    MIN_CONFIDENCE: float = 0.0
    FILTER_WORLD_TYPES: List[str] = field(default_factory=list)
    
    # Ustawienia subskrypcji
    MAX_AGENTS: int = 100
    
    # Ustawienia logowania
    LOG_LEVEL: str = "INFO"
    TRACK_STATISTICS: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje konfigurację do dict"""
        return {
            "AUTO_SEND": self.AUTO_SEND,
            "BATCH_SIZE": self.BATCH_SIZE,
            "MIN_CONFIDENCE": self.MIN_CONFIDENCE,
            "FILTER_WORLD_TYPES": self.FILTER_WORLD_TYPES,
            "MAX_AGENTS": self.MAX_AGENTS,
            "LOG_LEVEL": self.LOG_LEVEL,
            "TRACK_STATISTICS": self.TRACK_STATISTICS
        }


# =============================================================================
# KONFIGURACJA PAMIĘCI (Memory System)
# =============================================================================

@dataclass
class MemoryConfig:
    """
    Konfiguracja systemu pamięci V3.
    
    Odpowiedzialność:
    - Rozmiary pamięci
    - Strategie zapisu
    - Zarządzanie historią
    """
    
    # Ustawienia pamięci
    MAX_OBSERVATIONS: int = 10000
    MAX_PATTERNS: int = 1000
    MAX_METADATA: int = 5000
    MAX_RELATIONSHIPS: int = 2000
    MAX_WORLDS: int = 100
    
    # Ustawienia zapisu
    AUTO_SAVE: bool = True
    SAVE_INTERVAL: int = 100  # Co ile zmian zapisywać
    COMPRESSION: bool = True  # Kompresja danych
    
    # Ustawienia cache
    ENABLE_CACHE: bool = True
    CACHE_SIZE: int = 1000
    CACHE_TTL: float = 3600.0  # Czas życia cache (sekundy)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje konfigurację do dict"""
        return {
            "MAX_OBSERVATIONS": self.MAX_OBSERVATIONS,
            "MAX_PATTERNS": self.MAX_PATTERNS,
            "MAX_METADATA": self.MAX_METADATA,
            "MAX_RELATIONSHIPS": self.MAX_RELATIONSHIPS,
            "MAX_WORLDS": self.MAX_WORLDS,
            "AUTO_SAVE": self.AUTO_SAVE,
            "SAVE_INTERVAL": self.SAVE_INTERVAL,
            "COMPRESSION": self.COMPRESSION,
            "ENABLE_CACHE": self.ENABLE_CACHE,
            "CACHE_SIZE": self.CACHE_SIZE,
            "CACHE_TTL": self.CACHE_TTL
        }


# =============================================================================
# KONFIGURACJA ŚWIATÓW (World System)
# =============================================================================

@dataclass
class WorldConfig:
    """
    Konfiguracja systemu światów V3.
    
    Odpowiedzialność:
    - Typy światów
    - Strategie tworzenia światów
    - Zarządzanie hierarchią
    """
    
    # Ustawienia światów
    MAX_WORLDS: int = 100
    DEFAULT_WORLD_TYPE: str = "SWIAT_1_ZMIANY_KURSOW"
    AUTO_CREATE: bool = True
    
    # Ustawienia analizy
    ENABLE_ANALYSIS: bool = True
    ANALYSIS_DEPTH: int = 3  # Głębia analizy wzorców
    
    # Ustawienia ekonomiczne
    CALCULATE_EV: bool = True  # Obliczanie Expected Value
    CALCULATE_RISK: bool = True  # Obliczanie ryzyka
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje konfigurację do dict"""
        return {
            "MAX_WORLDS": self.MAX_WORLDS,
            "DEFAULT_WORLD_TYPE": self.DEFAULT_WORLD_TYPE,
            "AUTO_CREATE": self.AUTO_CREATE,
            "ENABLE_ANALYSIS": self.ENABLE_ANALYSIS,
            "ANALYSIS_DEPTH": self.ANALYSIS_DEPTH,
            "CALCULATE_EV": self.CALCULATE_EV,
            "CALCULATE_RISK": self.CALCULATE_RISK
        }


# =============================================================================
# GŁÓWNA KLASA KONFIGURACJI V3
# =============================================================================

@dataclass
class V3Config:
    """
    Centralna konfiguracja systemu V3 World Knowledge Engine.
    
    Odpowiedzialność:
    - Agregacja wszystkich konfiguracji V3
    - Walidacja ustawień
    - Zarządzanie domyślnymi wartościami
    - Integracja z innymi warstwami
    
    Zgodnie z:
    - PROJECT_RULES.md Sekcja 5.1 (Nowy Moduł Musi Mieć)
    - 10_IMPLEMENTATION_MAP.md (Sprint 2)
    
    Sposób użycia:
        # Użycie domyślne
        config = V3Config()
        
        # Użycie z customowymi wartościami
        config = V3Config(
            integration=IntegrationConfig(BATCH_SIZE=200),
            v4_bridge=V4BridgeConfig(AUTO_SEND=True),
            memory=MemoryConfig(MAX_OBSERVATIONS=20000)
        )
        
        # Walidacja
        if config.validate():
            print("Konfiguracja poprawna")
        
        # Eksport do dict
        config_dict = config.to_dict()
    """
    
    # Podmoduły konfiguracyjne
    integration: IntegrationConfig = field(default_factory=IntegrationConfig)
    v4_bridge: V4BridgeConfig = field(default_factory=V4BridgeConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    world: WorldConfig = field(default_factory=WorldConfig)
    
    # Ustawienia globalne
    SYSTEM_NAME: str = "V3_WORLD_KNOWLEDGE_ENGINE"
    VERSION: str = "1.0"
    ENVIRONMENT: str = "production"  # production, development, testing
    
    # Ustawienia debug
    DEBUG_MODE: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Ustawienia bezpieczeństwa
    MAX_THREADS: int = 10
    TIMEOUT: float = 60.0
    
    def __post_init__(self) -> None:
        """Inicjalizacja po utworzeniu (walidacja typów)"""
        # Konwersja stringów log level na enumy
        if isinstance(self.LOG_LEVEL, str):
            self.LOG_LEVEL = self.LOG_LEVEL.upper()
        
        if isinstance(self.integration.LOG_LEVEL, str):
            self.integration.LOG_LEVEL = self.integration.LOG_LEVEL.upper()
        
        if isinstance(self.v4_bridge.LOG_LEVEL, str):
            self.v4_bridge.LOG_LEVEL = self.v4_bridge.LOG_LEVEL.upper()
    
    def validate(self, mode: ValidationMode = ValidationMode.STRICT) -> bool:
        """
        Waliduje konfigurację V3.
        
        Args:
            mode: Tryb walidacji (STRICT, WARNING, PERMISSIVE)
            
        Returns:
            True jeśli konfiguracja jest poprawna
        """
        errors: List[str] = []
        warnings_list: List[str] = []
        
        # Walidacja IntegrationConfig
        if self.integration.BATCH_SIZE <= 0:
            errors.append(f"BATCH_SIZE ({self.integration.BATCH_SIZE}) musi być > 0")
        
        if self.integration.PROCESSING_TIMEOUT <= 0:
            errors.append(f"PROCESSING_TIMEOUT ({self.integration.PROCESSING_TIMEOUT}) musi być > 0")
        
        if self.integration.MAX_RETRIES < 0:
            warnings_list.append(f"MAX_RETRIES ({self.integration.MAX_RETRIES}) powinien być >= 0")
        
        if self.integration.MIN_FIELDS <= 0:
            errors.append(f"MIN_FIELDS ({self.integration.MIN_FIELDS}) musi być > 0")
        
        if not self.integration.REQUIRED_FIELDS:
            warnings_list.append("REQUIRED_FIELDS jest pusty - zaleca się zdefiniowanie")
        
        # Walidacja V4BridgeConfig
        if self.v4_bridge.MAX_AGENTS <= 0:
            errors.append(f"MAX_AGENTS ({self.v4_bridge.MAX_AGENTS}) musi być > 0")
        
        if self.v4_bridge.MIN_CONFIDENCE < 0 or self.v4_bridge.MIN_CONFIDENCE > 1:
            errors.append(f"MIN_CONFIDENCE ({self.v4_bridge.MIN_CONFIDENCE}) musi być w [0,1]")
        
        # Walidacja MemoryConfig
        if self.memory.MAX_OBSERVATIONS <= 0:
            errors.append(f"MAX_OBSERVATIONS ({self.memory.MAX_OBSERVATIONS}) musi być > 0")
        
        if self.memory.MAX_PATTERNS <= 0:
            errors.append(f"MAX_PATTERNS ({self.memory.MAX_PATTERNS}) musi być > 0")
        
        if self.memory.SAVE_INTERVAL <= 0:
            warnings_list.append(f"SAVE_INTERVAL ({self.memory.SAVE_INTERVAL}) powinien być > 0")
        
        # Walidacja WorldConfig
        if self.world.MAX_WORLDS <= 0:
            errors.append(f"MAX_WORLDS ({self.world.MAX_WORLDS}) musi być > 0")
        
        if self.world.ANALYSIS_DEPTH < 0:
            warnings_list.append(f"ANALYSIS_DEPTH ({self.world.ANALYSIS_DEPTH}) powinien być >= 0")
        
        # Walidacja globalna
        if self.MAX_THREADS <= 0:
            errors.append(f"MAX_THREADS ({self.MAX_THREADS}) musi być > 0")
        
        if self.TIMEOUT <= 0:
            errors.append(f"TIMEOUT ({self.TIMEOUT}) musi być > 0")
        
        # Walidacja poziomów logowania
        valid_log_levels = {level.value for level in LogLevel}
        if self.LOG_LEVEL not in valid_log_levels:
            warnings_list.append(f"LOG_LEVEL ({self.LOG_LEVEL}) nie jest standardowym poziomem")
        
        if self.integration.LOG_LEVEL not in valid_log_levels:
            warnings_list.append(f"integration.LOG_LEVEL ({self.integration.LOG_LEVEL}) nie jest standardowym poziomem")
        
        if self.v4_bridge.LOG_LEVEL not in valid_log_levels:
            warnings_list.append(f"v4_bridge.LOG_LEVEL ({self.v4_bridge.LOG_LEVEL}) nie jest standardowym poziomem")
        
        # Obsługa błędów i ostrzeżeń
        if errors:
            if mode == ValidationMode.STRICT:
                raise ValueError(f"Błędy walidacji: {errors}")
            elif mode == ValidationMode.WARNING:
                for error in errors:
                    warnings.warn(f"Błąd konfiguracji: {error}", RuntimeWarning)
        
        if warnings_list and mode != ValidationMode.PERMISSIVE:
            for warning in warnings_list:
                warnings.warn(f"Ostrzeżenie konfiguracji: {warning}", UserWarning)
        
        return len(errors) == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Konwertuje całą konfigurację V3 do dict.
        
        Returns:
            Dict ze wszystkimi ustawieniami
        """
        return {
            "SYSTEM_NAME": self.SYSTEM_NAME,
            "VERSION": self.VERSION,
            "ENVIRONMENT": self.ENVIRONMENT,
            "DEBUG_MODE": self.DEBUG_MODE,
            "LOG_LEVEL": self.LOG_LEVEL,
            "MAX_THREADS": self.MAX_THREADS,
            "TIMEOUT": self.TIMEOUT,
            "integration": self.integration.to_dict(),
            "v4_bridge": self.v4_bridge.to_dict(),
            "memory": self.memory.to_dict(),
            "world": self.world.to_dict()
        }
    
    def from_dict(cls, data: Dict[str, Any]) -> "V3Config":
        """
        Tworzy V3Config z dict.
        
        Args:
            data: Dict z konfiguracją
            
        Returns:
            V3Config
        """
        # Pobierz podmoduły
        integration_data = data.get("integration", {})
        v4_bridge_data = data.get("v4_bridge", {})
        memory_data = data.get("memory", {})
        world_data = data.get("world", {})
        
        return cls(
            SYSTEM_NAME=data.get("SYSTEM_NAME", "V3_WORLD_KNOWLEDGE_ENGINE"),
            VERSION=data.get("VERSION", "1.0"),
            ENVIRONMENT=data.get("ENVIRONMENT", "production"),
            DEBUG_MODE=data.get("DEBUG_MODE", False),
            LOG_LEVEL=data.get("LOG_LEVEL", "INFO"),
            MAX_THREADS=data.get("MAX_THREADS", 10),
            TIMEOUT=data.get("TIMEOUT", 60.0),
            integration=IntegrationConfig(**integration_data),
            v4_bridge=V4BridgeConfig(**v4_bridge_data),
            memory=MemoryConfig(**memory_data),
            world=WorldConfig(**world_data)
        )
    
    def save_to_json(self, path: str) -> None:
        """
        Zapisuje konfigurację do pliku JSON.
        
        Args:
            path: Ścieżka do pliku
        """
        import json
        import os
        
        # Upewnij się, że katalog istnieje
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Konfiguracja V3 zapisana do {path}")
    
    @classmethod
    def load_from_json(cls, path: str) -> "V3Config":
        """
        Ładowanie konfiguracji z pliku JSON.
        
        Args:
            path: Ścieżka do pliku
            
        Returns:
            V3Config
        """
        import json
        
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        config = cls.from_dict(data)
        logger.info(f"Konfiguracja V3 wczytana z {path}")
        return config


# =============================================================================
# ALIASY DLA KOMPATYBILNOŚCI WSTECZNEJ
# =============================================================================

# Alias dla istniejącej WorldIntegrationConfig
WorldIntegrationConfig = IntegrationConfig


# =============================================================================
# FABRYKA I INSTANCJE DOMYŚLNE
# =============================================================================

def tworz_v3_config(
    integration: Optional[IntegrationConfig] = None,
    v4_bridge: Optional[V4BridgeConfig] = None,
    memory: Optional[MemoryConfig] = None,
    world: Optional[WorldConfig] = None,
    **kwargs: Any
) -> V3Config:
    """
    Fabryka tworząca konfigurację V3.
    
    Args:
        integration: Konfiguracja integracyjna (opcjonalnie)
        v4_bridge: Konfiguracja mostu V4 (opcjonalnie)
        memory: Konfiguracja pamięci (opcjonalnie)
        world: Konfiguracja światów (opcjonalnie)
        **kwargs: Dodatkowe parametry globalne
        
    Returns:
        V3Config
    """
    return V3Config(
        integration=integration or IntegrationConfig(),
        v4_bridge=v4_bridge or V4BridgeConfig(),
        memory=memory or MemoryConfig(),
        world=world or WorldConfig(),
        **{k: v for k, v in kwargs.items() if k in ["SYSTEM_NAME", "VERSION", "ENVIRONMENT", "DEBUG_MODE", "LOG_LEVEL", "MAX_THREADS", "TIMEOUT"]}
    )


# Domyślna instancja konfiguracji
_default_config: Optional[V3Config] = None


def get_v3_config() -> V3Config:
    """
    Zwraca domyślną konfigurację V3 (Singleton).
    
    Returns:
        V3Config
    """
    global _default_config
    if _default_config is None:
        _default_config = tworz_v3_config()
    return _default_config


def reset_v3_config() -> None:
    """Resetuje domyślną konfigurację V3"""
    global _default_config
    _default_config = None


# =============================================================================
# TESTY
# =============================================================================

if __name__ == "__main__":
    print("Testing V3Config...")
    
    # Test 1: Tworzenie domyślne
    config = tworz_v3_config()
    print(f"✓ Test 1: Domyślna konfiguracja utworzona")
    
    # Test 2: Walidacja
    is_valid = config.validate()
    print(f"✓ Test 2: Walidacja: {'OK' if is_valid else 'FAILED'}")
    
    # Test 3: Konwersja do dict
    config_dict = config.to_dict()
    print(f"✓ Test 3: Konwersja do dict: {len(config_dict)} kluczy")
    
    # Test 4: Tworzenie z dict
    config_from_dict = V3Config.from_dict(config_dict)
    print(f"✓ Test 4: Tworzenie z dict: SUCCESS")
    
    # Test 5: Customowa konfiguracja
    custom_config = tworz_v3_config(
        integration=IntegrationConfig(BATCH_SIZE=200, SEND_TO_V4=True),
        v4_bridge=V4BridgeConfig(AUTO_SEND=True, MAX_AGENTS=50),
        ENVIRONMENT="development",
        DEBUG_MODE=True
    )
    print(f"✓ Test 5: Customowa konfiguracja utworzona")
    print(f"  - Integration BATCH_SIZE: {custom_config.integration.BATCH_SIZE}")
    print(f"  - V4 Bridge AUTO_SEND: {custom_config.v4_bridge.AUTO_SEND}")
    print(f"  - Environment: {custom_config.ENVIRONMENT}")
    
    # Test 6: Singleton
    default_config1 = get_v3_config()
    default_config2 = get_v3_config()
    print(f"✓ Test 6: Singleton: {default_config1 is default_config2}")
    
    # Test 7: Walidacja z błędami (STRICT mode)
    try:
        invalid_config = V3Config(
            integration=IntegrationConfig(BATCH_SIZE=0),
            memory=MemoryConfig(MAX_OBSERVATIONS=0)
        )
        invalid_config.validate(ValidationMode.STRICT)
        print(f"✗ Test 7: Walidacja STRICT powinna rzucić błąd")
    except ValueError as e:
        print(f"✓ Test 7: Walidacja STRICT działa: {len(str(e))} znaki błędu")
    
    # Test 8: Walidacja z ostrzeżeniami
    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        warning_config = V3Config(
            integration=IntegrationConfig(MAX_RETRIES=-1),
            memory=MemoryConfig(SAVE_INTERVAL=0)
        )
        warning_config.validate(ValidationMode.WARNING)
        print(f"✓ Test 8: Walidacja WARNING: {len(w)} ostrzeżeń")
    
    print("\n" + "="*50)
    print("All V3Config tests passed!")
    print("="*50)
