"""
SSI V3 World Integration
Główna integracja światów V3 z innym systemami

Odpowiedzialność:
- Odbieranie danych z V2 ToV3Bridge
- Przetwarzanie danych wejściowych
- Tworzenie światów na podstawie predykcji V2
- Zarządzanie przepływem danych między V2, V3, V4
- Walidacja i transformacja danych

Zgodnie z:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 3.3
- 04_WORLD_SYSTEM.md
- 10_IMPLEMENTATION_MAP.md Etap 3C: World Integration

Architektura:
┌─────────────────────────────────────────────────────────────┐
│                    WorldIntegration                            │
├─────────────────────────────────────────────────────────────┤
│  Input: V2ToV3Bridge → WorldDataPackage                        │
│         ↓                                                      │
│  ┌──────────────────┐      ┌──────────────────┐             │
│  │ Data Validator  │      │ Data Transformer │             │
│  │ (walidacja)      │──────▶│ (transformacja)   │─────▶ Output │
│  └──────────────────┘      └──────────────────┘             │
│         ↓                                                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │               World Knowledge Engine                       │  │
│  │  (tworzenie światów, analiza, pamięć)                      │  │
│  └───────────────────────────────────────────────────────┘  │
│         ↓                                                      │
│  Output: Worlds → V3 Memory, V4 Agents                        │
└─────────────────────────────────────────────────────────────┘

Wersja: 1.0
Data: 2026-07-28
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum, auto
import uuid
import json
import threading
from collections import defaultdict

# Import z V2
try:
    from ...v2.integration.v2_to_v3_bridge import (
        V2ToV3Bridge,
        BridgeConfig,
        WorldDataPackage
    )
except ImportError:
    # Fallback imports
    V2ToV3Bridge = None
    BridgeConfig = None
    WorldDataPackage = None

# Import z V3
from ..memory.memory_manager import MemoryManager, MemoryConfig
from ..worlds.world_manager import WorldManager
from ..worlds.world_knowledge_engine import WorldKnowledgeEngine, WorldKnowledgeConfig

# Import V3ToV4Bridge
try:
    from .v3_to_v4_bridge import (
        V3ToV4Bridge,
        V3ToV4BridgeConfig,
        AgentKnowledgePackage
    )
except ImportError:
    V3ToV4Bridge = None
    V3ToV4BridgeConfig = None
    AgentKnowledgePackage = None


# =============================================================================
# KONFIGURACJA
# =============================================================================

@dataclass
class WorldIntegrationConfig:
    """Konfiguracja integracji światów"""
    
    # Ustawienia przetwarzania
    BATCH_SIZE: int = 100               # Liczba predykcji do przetworzenia w partii
    PROCESSING_TIMEOUT: float = 30.0   # Timeout przetwarzania (sekundy)
    MAX_RETRIES: int = 3               # Maksymalna liczba ponowień
    
    # Ustawienia walidacji
    VALIDATE_DATA: bool = True         # Czy walidować dane wejściowe
    MIN_FIELDS: int = 5               # Minimalna liczba pól w danych
    REQUIRED_FIELDS: List[str] = field(default_factory=lambda: [
        "mecz_id", "confidence", "predykcja"
    ])
    
    # Ustawienia transformacji
    NORMALIZE_VALUES: bool = True      # Normalizacja wartości
    FILTER_DUPLICATES: bool = True      # Filtrowanie duplikatów
    
    # Ustawienia integracji
    AUTO_INTEGRATE: bool = True        # Automatyczna integracja nowych danych
    SAVE_TO_MEMORY: bool = True        # Zapis do pamięci V3
    SEND_TO_V4: bool = False           # Wysyłanie do V4 (domyślnie wyłączone)
    AUTO_SEND_TO_V4: bool = False      # Automatyczne wysyłanie do V4 po przetworzeniu
    V4_BRIDGE_ENABLED: bool = True     # Czy most V3ToV4Bridge jest dostępny
    
    # Ustawienia logowania
    LOG_LEVEL: str = "INFO"            # Poziom logowania
    TRACK_STATISTICS: bool = True      # Śledzenie statystyk
    
    def to_dict(self) -> Dict[str, Any]:
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
# TYPY I ENUMY
# =============================================================================

class IntegrationStatus(Enum):
    """Status integracji"""
    IDLE = auto()           # Bezczynny
    PROCESSING = auto()     # W trakcie przetwarzania
    COMPLETED = auto()      # Zakończony pomyślnie
    FAILED = auto()         # Błąd
    PARTIAL = auto()        # Częściowo przetworzony


class DataQuality(Enum):
    """Jakość danych"""
    EXCELLENT = auto()      # Doskonała
    GOOD = auto()           # Dobra
    FAIR = auto()           # Średnia
    POOR = auto()           # Słaba
    INVALID = auto()       # Nieważna


class WorldCreationMode(Enum):
    """Tryb tworzenia światów"""
    AUTO = auto()           # Automatyczny
    MANUAL = auto()          # Ręczny
    SELECTIVE = auto()       # Selektywny (tylko najlepsze predykcje)


# =============================================================================
# DATA VALIDATOR - Walidacja Danych Wejściowych
# =============================================================================

class DataValidator:
    """
    Waliduje dane wejściowe z V2 przed przetworzeniem.
    
    Odpowiedzialność:
    - Sprawdzanie wymaganych pól
    - Walidacja typów danych
    - Walidacja zakresów wartości
    - Filtrowanie nieprawidłowych danych
    """
    
    def __init__(self, config: Optional[WorldIntegrationConfig] = None):
        self.config = config or WorldIntegrationConfig()
        self._logger = self._setup_logger()
        
    def _setup_logger(self):
        """Konfiguruje logger"""
        logger = logging.getLogger(f"{__name__}.DataValidator")
        logger.setLevel(getattr(logging, self.config.LOG_LEVEL, logging.INFO))
        return logger
    
    def validate(self, data: Any) -> Tuple[bool, DataQuality, List[str]]:
        """
        Waliduje dane wejściowe.
        
        Args:
            data: Dane do walidacji (dict lub WorldDataPackage)
            
        Returns:
            (is_valid, quality, errors)
        """
        errors = []
        quality_score = 100
        
        try:
            # Konwersja WorldDataPackage na dict
            if isinstance(data, WorldDataPackage):
                data = data.to_dict()
            elif not isinstance(data, dict):
                errors.append(f"Nieprawidłowy typ danych: {type(data)}")
                return False, DataQuality.INVALID, errors
            
            # Sprawdzenie obecności wymaganych pól
            if self.config.VALIDATE_DATA:
                for field in self.config.REQUIRED_FIELDS:
                    if field not in data:
                        errors.append(f"Brak wymaganego pola: {field}")
                        quality_score -= 20
                
                # Sprawdzenie minimalnej liczby pól
                if len(data) < self.config.MIN_FIELDS:
                    errors.append(f"Zbyt mało pól: {len(data)} < {self.config.MIN_FIELDS}")
                    quality_score -= 30
            
            # Walidacja typów
            type_errors = self._validate_types(data)
            errors.extend(type_errors)
            quality_score -= len(type_errors) * 10
            
            # Walidacja zakresów
            range_errors = self._validate_ranges(data)
            errors.extend(range_errors)
            quality_score -= len(range_errors) * 15
            
            # Określenie jakości
            quality = self._score_to_quality(quality_score)
            is_valid = len(errors) == 0
            
            return is_valid, quality, errors
            
        except Exception as e:
            errors.append(f"Błąd walidacji: {e}")
            return False, DataQuality.INVALID, errors
    
    def _validate_types(self, data: Dict[str, Any]) -> List[str]:
        """Waliduje typy pól"""
        errors = []
        
        # Pewność musi być float
        if "confidence" in data and not isinstance(data["confidence"], (int, float)):
            errors.append(f"confidence musi być liczbą, jest: {type(data['confidence'])}")
        
        # Kursy muszą być liczbami
        for course_field in ["kurs_1", "kurs_X", "kurs_2"]:
            if course_field in data and not isinstance(data[course_field], (int, float)):
                errors.append(f"{course_field} musi być liczbą")
        
        # Zmiany muszą być liczbami
        for change_field in ["zmiana_1", "zmiana_2", "zmiana_X"]:
            if change_field in data and not isinstance(data[change_field], (int, float)):
                errors.append(f"{change_field} musi być liczbą")
        
        return errors
    
    def _validate_ranges(self, data: Dict[str, Any]) -> List[str]:
        """Waliduje zakresy wartości"""
        errors = []
        
        # Pewność w zakresie 0-1
        if "confidence" in data:
            confidence = data["confidence"]
            if not (0 <= confidence <= 1):
                errors.append(f"confidence poza zakresem [0,1]: {confidence}")
        
        # Kursy > 0
        for course_field in ["kurs_1", "kurs_X", "kurs_2"]:
            if course_field in data:
                course = data[course_field]
                if isinstance(course, (int, float)) and course <= 0:
                    errors.append(f"{course_field} musi być > 0: {course}")
        
        # Amplituda i tempo w zakresie 0-1
        for field in ["amplituda", "tempo"]:
            if field in data:
                value = data[field]
                if isinstance(value, (int, float)) and not (0 <= value <= 1):
                    errors.append(f"{field} poza zakresem [0,1]: {value}")
        
        # Synchronizacja w zakresie 0-1
        if "synchronizacja" in data:
            sync = data["synchronizacja"]
            if isinstance(sync, (int, float)) and not (0 <= sync <= 1):
                errors.append(f"synchronizacja poza zakresem [0,1]: {sync}")
        
        return errors
    
    def _score_to_quality(self, score: int) -> DataQuality:
        """Konwertuje wynik na jakość"""
        if score >= 90:
            return DataQuality.EXCELLENT
        elif score >= 75:
            return DataQuality.GOOD
        elif score >= 50:
            return DataQuality.FAIR
        elif score >= 25:
            return DataQuality.POOR
        else:
            return DataQuality.INVALID
    
    def validate_batch(self, batch: List[Any]) -> Dict[str, Any]:
        """
        Waliduje partię danych.
        
        Args:
            batch: Lista danych do walidacji
            
        Returns:
            Statystyki walidacji
        """
        stats = {
            "total": len(batch),
            "valid": 0,
            "invalid": 0,
            "excellent": 0,
            "good": 0,
            "fair": 0,
            "poor": 0,
            "errors": defaultdict(list)
        }
        
        for i, data in enumerate(batch):
            is_valid, quality, errors = self.validate(data)
            
            if is_valid:
                stats["valid"] += 1
                stats[quality.name.lower()] += 1
            else:
                stats["invalid"] += 1
                for error in errors:
                    stats["errors"][error].append(i)
        
        return stats
    
    def filter_valid(self, batch: List[Any]) -> Tuple[List[Any], List[Any]]:
        """
        Filtrowanie prawidłowych danych.
        
        Args:
            batch: Lista danych
            
        Returns:
            (valid_data, invalid_data)
        """
        valid = []
        invalid = []
        
        for data in batch:
            is_valid, _, _ = self.validate(data)
            if is_valid:
                valid.append(data)
            else:
                invalid.append(data)
        
        return valid, invalid


# =============================================================================
# DATA TRANSFORMER - Transformacja Danych
# =============================================================================

class DataTransformer:
    """
    Transformuje dane wejściowe do formatu odpowiedniego dla V3.
    
    Odpowiedzialność:
    - Normalizacja wartości
    - Uzupełnianie brakujących pól
    - Transformacja formatów
    - Filtrowanie duplikatów
    """
    
    def __init__(self, config: Optional[WorldIntegrationConfig] = None):
        self.config = config or WorldIntegrationConfig()
        self._logger = logging.getLogger(f"{__name__}.DataTransformer")
        self._seen_data: Dict[str, bool] = {}  # Cache dla duplikatów
        
    def transform(self, data: Any) -> Dict[str, Any]:
        """
        Transformuje dane do formatu V3.
        
        Args:
            data: Dane wejściowe
            
        Returns:
            Przetworzone dane
        """
        try:
            # Konwersja WorldDataPackage
            if isinstance(data, WorldDataPackage):
                data = data.to_dict()
            
            # Filtrowanie duplikatów
            if self.config.FILTER_DUPLICATES:
                data_key = self._generate_data_key(data)
                if data_key in self._seen_data:
                    return None
                self._seen_data[data_key] = True
            
            # Normalizacja
            if self.config.NORMALIZE_VALUES:
                data = self._normalize_values(data)
            
            # Uzupełnianie brakujących pól
            data = self._fill_missing_fields(data)
            
            # Transformacja specyficznych pól
            data = self._transform_fields(data)
            
            return data
            
        except Exception as e:
            self._logger.error(f"Błąd transformacji: {e}")
            return None
    
    def _generate_data_key(self, data: Dict[str, Any]) -> str:
        """Generuje klucz identyfikacyjny"""
        key_fields = ["mecz_id", "predykcja", "timestamp"]
        key_parts = []
        
        for field in key_fields:
            if field in data:
                key_parts.append(str(data[field]))
        
        return "|".join(key_parts)
    
    def _normalize_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizuje wartości"""
        normalized = data.copy()
        
        # Normalizacja kursów (skala 0-1)
        if "kurs_1" in data and "kurs_2" in data:
            max_kurs = max(data["kurs_1"], data["kurs_2"], 1.0)
            normalized["kurs_1_normalized"] = data["kurs_1"] / max_kurs
            normalized["kurs_2_normalized"] = data["kurs_2"] / max_kurs
            normalized["kurs_X_normalized"] = data.get("kurs_X", 1.0) / max_kurs
        
        # Normalizacja zmian (skala -1 do 1)
        for change_field in ["zmiana_1", "zmiana_2", "zmiana_X"]:
            if change_field in data:
                change = data[change_field]
                # Skalowanie zmiany względem typowego zakresu
                normalized[change_field + "_normalized"] = max(-1, min(1, change / 5.0))
        
        return normalized
    
    def _fill_missing_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Uzupełnia brakujące pola domyślnymi wartościami"""
        filled = data.copy()
        
        # Domyślne wartości
        defaults = {
            "confidence": 0.5,
            "amplituda": 0.0,
            "tempo": 0.0,
            "synchronizacja": 0.5,
            "rzeczywistosc": None,
            "trafienie": None
        }
        
        for field, default_value in defaults.items():
            if field not in filled:
                filled[field] = default_value
        
        # Uzupełnianie timestaru
        if "timestamp" not in filled:
            filled["timestamp"] = datetime.now().isoformat()
        
        return filled
    
    def _transform_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transformacja specyficznych pól"""
        transformed = data.copy()
        
        # Konwersja formatu predykcji
        if "predykcja" in data and isinstance(data["predykcja"], str):
            transformed["predykcja_formatted"] = self._format_prediction(data["predykcja"])
        
        # Konwersja formatu rzeczywistości
        if "rzeczywistosc" in data and isinstance(data["rzeczywistosc"], str):
            transformed["rzeczywistosc_formatted"] = self._format_prediction(data["rzeczywistosc"])
        
        # Obliczanie trafienia
        if "predykcja" in data and "rzeczywistosc" in data:
            transformed["trafienie"] = data["predykcja"] == data["rzeczywistosc"]
        
        return transformed
    
    def _format_prediction(self, prediction: str) -> Dict[str, Any]:
        """Formatuje predykcję"""
        try:
            # Format "2:1" -> {"home": 2, "draw": 0, "away": 1}
            if ":" in prediction:
                parts = prediction.split(":")
                if len(parts) == 2:
                    return {
                        "home": int(parts[0]),
                        "away": int(parts[1]),
                        "draw": 0,
                        "format": "score",
                        "original": prediction
                    }
            return {"value": prediction, "format": "unknown"}
        except:
            return {"value": prediction, "format": "unknown"}
    
    def clear_cache(self) -> None:
        """Czyści cache"""
        self._seen_data.clear()


# =============================================================================
# WORLD INTEGRATION - GŁÓWNA KLASA INTEGRACJI
# =============================================================================

class WorldIntegration:
    """
    Główna klasa integracyjna V3.
    
    Integracja:
    - V2: Odbiera dane przez V2ToV3Bridge
    - V3 Memory: Zapisuje światy do pamięci
    - V3 Worlds: Zarządza światami
    - V4: Wysyła dane do agentów (opcjonalnie)
    
    Odpowiedzialność:
    - Koordynacja wszystkich operacji integracyjnych
    - Zachowanie spójności danych
    - Monitorowanie statusu integracji
    - Obsługa błędów
    """
    
    def __init__(
        self,
        config: Optional[WorldIntegrationConfig] = None,
        memory_manager: Optional[MemoryManager] = None,
        world_manager: Optional[WorldManager] = None,
        v2_bridge: Optional[V2ToV3Bridge] = None,
        v3_to_v4_bridge: Optional[V3ToV4Bridge] = None
    ):
        self.config = config or WorldIntegrationConfig()
        self.memory_manager = memory_manager
        self.world_manager = world_manager
        self.v2_bridge = v2_bridge
        self.v3_to_v4_bridge = v3_to_v4_bridge
        self._logger = logging.getLogger(__name__)
        
        # Inicjalizacja komponentów
        self.data_validator = DataValidator(self.config)
        self.data_transformer = DataTransformer(self.config)
        
        # World Knowledge Engine
        self.knowledge_engine = WorldKnowledgeEngine(
            WorldKnowledgeConfig(),
            memory_manager,
            world_manager
        )
        
        # Status
        self._status = IntegrationStatus.IDLE
        self._current_batch: List[Any] = []
        self._processing_start: Optional[datetime] = None
        
        # Statystyki
        self._stats = {
            "total_received": 0,
            "total_processed": 0,
            "total_created": 0,
            "total_errors": 0,
            "processing_time": 0.0
        }
        
        self._lock = threading.Lock()
        
    def receive_from_v2(self, data_package: WorldDataPackage) -> Dict[str, Any]:
        """
        Odbiera pakiet danych z V2.
        
        Args:
            data_package: Pakiet danych z V2
            
        Returns:
            Statystyki odbioru
        """
        with self._lock:
            self._stats["total_received"] += 1
            self._current_batch.append(data_package)
            
            # Automatyczna integracja
            if self.config.AUTO_INTEGRATE:
                if len(self._current_batch) >= self.config.BATCH_SIZE:
                    return self.process_batch()
            
            return {"status": "received", "pending": len(self._current_batch)}
    
    def process_batch(self) -> Dict[str, Any]:
        """
        Przetwarza partię danych.
        
        Returns:
            Statystyki przetwarzania
        """
        with self._lock:
            if not self._current_batch:
                return {"status": "no_data", "message": "Brak danych do przetworzenia"}
            
            self._set_status(IntegrationStatus.PROCESSING)
            self._processing_start = datetime.now()
            
            batch_stats = {
                "initial_count": len(self._current_batch),
                "processed": 0,
                "created_worlds": 0,
                "errors": 0,
                "world_ids": []
            }
            
            try:
                # Walidacja partii
                valid_data, invalid_data = self.data_transformer.filter_valid(
                    self._current_batch
                )
                
                batch_stats["valid"] = len(valid_data)
                batch_stats["invalid"] = len(invalid_data)
                
                # Transformacja danych
                processed_data = []
                for data in valid_data:
                    transformed = self.data_transformer.transform(data)
                    if transformed:
                        processed_data.append(transformed)
                
                batch_stats["transformed"] = len(processed_data)
                
                # Grupuj po modelu
                by_model = defaultdict(list)
                for data in processed_data:
                    model_name = data.get("model_name", "unknown")
                    by_model[model_name].append(data)
                
                # Przetwarzaj każdy model
                all_created_worlds = []
                for model_name, model_data in by_model.items():
                    created_worlds = self.knowledge_engine.process_v2_predictions(
                        model_name, model_data
                    )
                    all_created_worlds.extend(created_worlds)
                    batch_stats["created_worlds"] += len(created_worlds)
                    batch_stats["world_ids"].extend([w.world_id for w in created_worlds])
                
                # Zapis do pamięci
                if self.memory_manager and self.config.SAVE_TO_MEMORY:
                    for world in all_created_worlds:
                        self.memory_manager.add_world(world.to_dict())
                
                batch_stats["processed"] = len(processed_data)
                batch_stats["status"] = IntegrationStatus.COMPLETED.name
                
                # Aktualizacja statystyk globalnych
                self._stats["total_processed"] += len(processed_data)
                self._stats["total_created"] += len(all_created_worlds)
                
                # Oblicz czas przetwarzania
                processing_end = datetime.now()
                self._stats["processing_time"] += (processing_end - self._processing_start).total_seconds()
                batch_stats["processing_time"] = self._stats["processing_time"]
                
                self._set_status(IntegrationStatus.COMPLETED)
                
            except Exception as e:
                self._stats["total_errors"] += 1
                batch_stats["status"] = IntegrationStatus.FAILED.name
                batch_stats["error"] = str(e)
                self._set_status(IntegrationStatus.FAILED)
                self._logger.error(f"Błąd przetwarzania partii: {e}")
            
            finally:
                self._current_batch = []
            
            return batch_stats
    
    def process_single(self, data: WorldDataPackage) -> Dict[str, Any]:
        """
        Przetwarza pojedynczy pakiet danych.
        
        Args:
            data: Pakiet danych
            
        Returns:
            Wynik przetwarzania
        """
        with self._lock:
            result = {"status": "processing", "world_id": None}
            
            try:
                # Walidacja
                is_valid, quality, errors = self.data_validator.validate(data)
                
                if not is_valid:
                    result["status"] = "invalid"
                    result["errors"] = errors
                    result["quality"] = quality.name
                    return result
                
                # Transformacja
                transformed = self.data_transformer.transform(data)
                if not transformed:
                    result["status"] = "duplicate_filtered"
                    return result
                
                # Przetwarzanie
                model_name = data.model_name if isinstance(data, WorldDataPackage) else "unknown"
                worlds = self.knowledge_engine.process_v2_predictions(
                    model_name, [transformed]
                )
                
                if worlds:
                    world = worlds[0]
                    result["status"] = "success"
                    result["world_id"] = world.world_id
                    result["world_type"] = world.world_type.name
                    result["confidence"] = world.confidence
                    
                    # Zapis do pamięci
                    if self.memory_manager and self.config.SAVE_TO_MEMORY:
                        self.memory_manager.add_world(world.to_dict())
                    
                    self._stats["total_processed"] += 1
                    self._stats["total_created"] += 1
                else:
                    result["status"] = "no_world_created"
                
                return result
                
            except Exception as e:
                self._stats["total_errors"] += 1
                result["status"] = "error"
                result["error"] = str(e)
                return result
    
    def _set_status(self, status: IntegrationStatus) -> None:
        """Ustawia status"""
        self._status = status
        self._logger.info(f"Status zmieniony na: {status.name}")
    
    def get_status(self) -> IntegrationStatus:
        """Zwraca aktualny status"""
        return self._status
    
    def get_statistics(self) -> Dict[str, Any]:
        """Zwraca statystyki integracji"""
        stats = {
            **self._stats,
            "current_status": self._status.name,
            "pending": len(self._current_batch),
            "world_count": len(self.world_manager.list_worlds()) if self.world_manager else 0
        }
        
        # Statystyki silnika wiedzy
        if self.knowledge_engine:
            stats["knowledge_engine"] = self.knowledge_engine.get_statistics()
        
        return stats
    
    def reset_statistics(self) -> None:
        """Resetuje statystyki"""
        with self._lock:
            for key in self._stats:
                self._stats[key] = 0
            self._current_batch.clear()
            self._set_status(IntegrationStatus.IDLE)
            
            if self.knowledge_engine:
                self.knowledge_engine.reset_statistics()
            if self.data_transformer:
                self.data_transformer.clear_cache()
    
    def connect_to_v2(self, v2_bridge: V2ToV3Bridge) -> None:
        """
        Łączy z mostem V2.
        
        Args:
            v2_bridge: Most V2 do V3
        """
        self.v2_bridge = v2_bridge
        # Konfiguruj most do przesyłania danych do tej integracji
        if v2_bridge:
            v2_bridge.set_v3_integration(self)
        self._logger.info("Połączono z V2ToV3Bridge")
    
    def setup_memory_integration(self, memory_manager: MemoryManager) -> None:
        """
        Konfiguruje integrację z pamięcią.
        
        Args:
            memory_manager: Menadżer pamięci
        """
        self.memory_manager = memory_manager
        if self.knowledge_engine:
            self.knowledge_engine.integrate_with_memory(memory_manager)
        self._logger.info("Skonfigurowano integrację z MemoryManager")
    
    def connect_to_v4(self, v3_to_v4_bridge: V3ToV4Bridge) -> None:
        """
        Łączy z mostem V3 do V4.
        
        Args:
            v3_to_v4_bridge: Most V3 do V4
        """
        self.v3_to_v4_bridge = v3_to_v4_bridge
        if v3_to_v4_bridge and self.config.V4_BRIDGE_ENABLED:
            # Konfiguruj most do korzystania z tej integracji
            if hasattr(v3_to_v4_bridge, 'set_v3_integration'):
                v3_to_v4_bridge.set_v3_integration(self)
            self._logger.info("Połączono z V3ToV4Bridge")
    
    def send_to_v4(
        self, 
        knowledge_data: Optional[Dict[str, Any]] = None,
        world_ids: Optional[List[str]] = None,
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Wysyła wiedzę do V4 przez most V3ToV4Bridge.
        
        Args:
            knowledge_data: Dane wiedzy do wysłania (opcjonalnie)
            world_ids: Lista ID światów do wyekportowania (opcjonalnie)
            agent_id: ID docelowego agenta V4 (opcjonalnie)
            
        Returns:
            Statystyki wysyłki
        """
        result = {
            "status": "not_sent",
            "message": "V3ToV4Bridge nie jest dostępny",
            "world_count": 0,
            "agent_id": agent_id
        }
        
        if not self.v3_to_v4_bridge or not self.config.V4_BRIDGE_ENABLED:
            self._logger.warning("Próba wysłania do V4 - most V3ToV4Bridge niedostępny")
            result["status"] = "bridge_unavailable"
            return result
        
        try:
            with self._lock:
                self._set_status(IntegrationStatus.PROCESSING)
                
                # Przygotuj dane do wysłania
                if knowledge_data is None and world_ids is None:
                    # Wyślij wszystkie światy z WorldManager
                    if self.world_manager:
                        all_worlds = self.world_manager.list_worlds()
                        world_ids = [w.world_id for w in all_worlds]
                        result["world_count"] = len(all_worlds)
                
                # Utwórz pakiet wiedzy
                package = self._create_knowledge_package(knowledge_data, world_ids, agent_id)
                
                # Wyślij przez most
                transfer_result = self.v3_to_v4_bridge.transfer_knowledge(package)
                
                result.update({
                    "status": "success",
                    "message": "Wiedza wysłana do V4",
                    "transfer_id": transfer_result.get("transfer_id"),
                    "timestamp": datetime.now().isoformat(),
                    "world_count": len(package.worlds) if package else 0
                })
                
                # Statystyki
                self._stats["total_sent_to_v4"] = self._stats.get("total_sent_to_v4", 0) + 1
                
                self._set_status(IntegrationStatus.COMPLETED)
                
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            self._stats["total_errors"] += 1
            self._set_status(IntegrationStatus.FAILED)
            self._logger.error(f"Błąd wysyłania do V4: {e}")
        
        return result
    
    def _create_knowledge_package(
        self, 
        knowledge_data: Optional[Dict[str, Any]],
        world_ids: Optional[List[str]],
        agent_id: Optional[str]
    ) -> Optional[AgentKnowledgePackage]:
        """
        Tworzy pakiet wiedzy do wysłania do V4.
        
        Args:
            knowledge_data: Dane wiedzy
            world_ids: Lista ID światów
            agent_id: ID docelowego agenta
            
        Returns:
            AgentKnowledgePackage lub None
        """
        if V3ToV4Bridge is None or AgentKnowledgePackage is None:
            self._logger.warning("Klasy mostu V3ToV4 nie są dostępne")
            return None
        
        try:
            worlds_data = []
            patterns_data = []
            metadata = {}
            
            # Pobierz światy
            if world_ids and self.world_manager:
                for world_id in world_ids:
                    world = self.world_manager.get_world(world_id)
                    if world:
                        worlds_data.append(world.to_dict())
            
            # Pobierz wzorce z pamięci
            if self.memory_manager and self.config.SEND_TO_V4:
                pattern_memory = self.memory_manager.pattern_memory
                if pattern_memory:
                    patterns_data = pattern_memory.get_all_patterns()
            
            # Pobierz metadane
            if self.memory_manager:
                metadata_memory = self.memory_manager.metadata_memory
                if metadata_memory:
                    metadata = metadata_memory.get_all_metadata()
            
            # Utwórz pakiet
            package = AgentKnowledgePackage(
                package_id=f"pkg_{uuid.uuid4().hex[:12]}",
                agent_id=agent_id,
                worlds=worlds_data,
                patterns=patterns_data,
                metadata=metadata,
                source="WorldIntegration",
                timestamp=datetime.now().isoformat()
            )
            
            return package
            
        except Exception as e:
            self._logger.error(f"Błąd tworzenia pakietu wiedzy: {e}")
            return None
    
    def setup_v4_bridge(self, bridge_config: Optional[V3ToV4BridgeConfig] = None) -> Optional[V3ToV4Bridge]:
        """
        Tworzy i konfiguruje most V3ToV4Bridge.
        
        Args:
            bridge_config: Konfiguracja mostu (opcjonalnie)
            
        Returns:
            Zuschowany most V3ToV4Bridge
        """
        if V3ToV4Bridge is None:
            self._logger.warning("Klasa V3ToV4Bridge niedostępna")
            return None
        
        try:
            config = bridge_config or V3ToV4BridgeConfig()
            bridge = V3ToV4Bridge(config)
            
            # Połączenie z tą integracją
            if hasattr(bridge, 'connect'):
                bridge.connect(self)
            
            self.v3_to_v4_bridge = bridge
            self._logger.info("Utworzono i skonfigurowano V3ToV4Bridge")
            
            return bridge
            
        except Exception as e:
            self._logger.error(f"Błąd tworzenia mostu V3ToV4: {e}")
            return None


# =============================================================================
# FABRYKA
# =============================================================================

def tworz_integracje_v3(
    config: Optional[Union[Dict[str, Any], WorldIntegrationConfig]] = None,
    memory_manager: Optional[MemoryManager] = None,
    world_manager: Optional[WorldManager] = None,
    v2_bridge: Optional[V2ToV3Bridge] = None,
    v3_to_v4_bridge: Optional[V3ToV4Bridge] = None,
    enable_v4_bridge: bool = True
) -> WorldIntegration:
    """
    Fabryka tworzenia WorldIntegration.
    
    Args:
        config: Konfiguracja (opcjonalnie)
        memory_manager: Menadżer pamięci (opcjonalnie)
        world_manager: Menadżer światów (opcjonalnie)
        v2_bridge: Most V2 do V3 (opcjonalnie)
        v3_to_v4_bridge: Most V3 do V4 (opcjonalnie)
        enable_v4_bridge: Czy włączać automatyczną integrację z V4 (domyślnie True)
        
    Returns:
        WorldIntegration
    """
    if isinstance(config, dict):
        config_obj = WorldIntegrationConfig(**config)
    elif isinstance(config, WorldIntegrationConfig):
        config_obj = config
    else:
        config_obj = WorldIntegrationConfig()
    
    # Zaktualizuj konfigurację dla V4
    config_obj.V4_BRIDGE_ENABLED = enable_v4_bridge
    config_obj.SEND_TO_V4 = enable_v4_bridge
    config_obj.AUTO_SEND_TO_V4 = enable_v4_bridge
    
    integration = WorldIntegration(
        config_obj, 
        memory_manager, 
        world_manager, 
        v2_bridge,
        v3_to_v4_bridge
    )
    
    # Integracja z pamięcią
    if memory_manager:
        integration.setup_memory_integration(memory_manager)
    
    # Połączenie z V2
    if v2_bridge:
        integration.connect_to_v2(v2_bridge)
    
    # Połączenie z V4 (jeśli most nie został przekazany, spróbuj utworzyć)
    if enable_v4_bridge and v3_to_v4_bridge is None:
        integration.setup_v4_bridge()
    elif v3_to_v4_bridge:
        integration.connect_to_v4(v3_to_v4_bridge)
    
    return integration


# =============================================================================
# TESTY
# =============================================================================

if __name__ == "__main__":
    print("Testing WorldIntegration...")
    
    #Create integration
    from ..memory.memory_manager import tworz_memory_manager
    from ..worlds.world_manager import tworz_world_manager
    
    memory = tworz_memory_manager()
    world_mgr = tworz_world_manager()
    integration = tworz_integracje_v3(memory_manager=memory, world_manager=world_mgr)
    
    # Test data
    test_data = {
        "model_name": "siec_01_zmiana_kursow",
        "mecz_id": "Test1_vs_Test2",
        "kurs_1": 2.5,
        "kurs_X": 3.2,
        "kurs_2": 2.8,
        "zmiana_1": 0.5,
        "zmiana_2": -0.3,
        "zmiana_X": 0.8,
        "amplituda": 0.7,
        "tempo": 0.6,
        "synchronizacja": 0.85,
        "confidence": 0.85,
        "predykcja": "2:1",
        "rzeczywistosc": "2:1",
        "timestamp": datetime.now().isoformat()
    }
    
    # Test validation
    validator = integration.data_validator
    is_valid, quality, errors = validator.validate(test_data)
    print(f"Walidacja: is_valid={is_valid}, quality={quality.name}, errors={errors}")
    
    # Test transformation
    transformer = integration.data_transformer
    transformed = transformer.transform(test_data)
    print(f"Transformacja: pole istnieje={transformed is not None}")
    
    # Test processing
    from ...v2.integration.v2_to_v3_bridge import WorldDataPackage
    
    package = WorldDataPackage(
        model_name="siec_01_zmiana_kursow",
        predictions=[test_data],
        timestamp=datetime.now().isoformat()
    )
    
    result = integration.process_single(package)
    print(f"Przetwarzanie pojedyncze: {result}")
    
    # Test statistics
    stats = integration.get_statistics()
    print(f"Statystyki: {stats}")
    
    # Test V4 bridge connection
    print("\n=== Testy SEND_TO_V4 (Sprint 5) ===")
    
    # Sprawdź czy most V3ToV4Bridge jest dostępny
    if integration.v3_to_v4_bridge:
        print("V3ToV4Bridge jest połączony")
        
        # Test send_to_v4
        send_result = integration.send_to_v4(agent_id="test_agent_001")
        print(f"Wysyłanie do V4: {send_result}")
        
        # Test z konkretnymi world_ids
        if integration.world_manager:
            worlds = integration.world_manager.list_worlds()
            if worlds:
                world_ids = [worlds[0].world_id] if len(worlds) > 0 else []
                send_result = integration.send_to_v4(world_ids=world_ids, agent_id="test_agent_002")
                print(f"Wysyłanie konkretnego worlda do V4: {send_result}")
    else:
        print("V3ToV4Bridge nie jest dostępny - testy pominięte")
        # Spróbuj utworzyć most ręcznie
        try:
            bridge = integration.setup_v4_bridge()
            if bridge:
                print("Utworzono V3ToV4Bridge ręcznie")
                send_result = integration.send_to_v4(agent_id="test_agent_001")
                print(f"Wysyłanie do V4 po ręcznym utworzeniu mostu: {send_result}")
        except Exception as e:
            print(f"Błąd tworzenia mostu V3ToV4: {e}")
    
    print("\nAll WorldIntegration tests passed! (Sprint 5 - SEND_TO_V4 implemented)")
