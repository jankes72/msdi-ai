"""
SSI V5 - LLM Queue Configuration
Konfiguracja kolejki modeli LLM

Zgodnie z dokumentacja:
- 06_AI_LAB_REQUEST_PIPELINE.md Sekcja 6.1, 6.2
- 01_SYSTEM_SIGNAL_ARCHITECTURE.md (Ograniczenia sprzetowe)

ZASADA: Tylko 1 aktywny model LLM na raz
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
import os
import platform
try:
    import psutil
except ImportError:
    psutil = None


class QueueMode(Enum):
    """Tryby pracy kolejki."""
    STRICT = "strict"          # Tylko 1 model na raz, kolejka FIFO
    PRIORITY = "priority"      # 1 model na raz, kolejka z priorytetami
    EMERGENCY = "emergency"    # Przerwanie biezacego modelu dla CRITICAL
    

class MemoryCleanupStrategy(Enum):
    """Strategie czyszczenia pamieci."""
    NONE = "none"              # Brak czyszczenia
    BASIC = "basic"            # clear_cache() po kazdym modelu
    AGGRESSIVE = "aggressive"  # restart Python process (ekstremalny)
    AUTO = "auto"              # Automatyczne na podstawie dostepnej pamieci


@dataclass
class HardwareConstraints:
    """Ograniczenia sprzetowe dla kolejki LLM."""
    
    # Ogolne
    max_active_models: int = 1  # ZASADA: Tylko 1 model na raz
    max_concurrent_requests: int = 1
    
    # Pamiec
    min_memory_gb: float = 2.0       # Minimalna wolna pamiac do uruchomienia modelu
    max_memory_usage_percent: float = 85.0  # Maksymalne uzycie pamieci
    cleanup_strategy: MemoryCleanupStrategy = MemoryCleanupStrategy.BASIC
    
    # GPU (jesli dostepne)
    gpu_available: bool = False
    max_gpu_memory_gb: float = 0.0
    gpu_memory_buffer_gb: float = 1.0
    
    # Timeouty
    model_start_timeout: float = 30.0     # sekundy
    model_work_timeout: float = 300.0    # 5 minut
    model_stop_timeout: float = 10.0     # sekundy
    save_memory_timeout: float = 15.0    # sekundy
    
    # Buckety (dla statystyk)
    queue_width: int = 100  # Maksymalna dlugosc kolejki
    
    def detect_hardware(self) -> None:
        """Automatyczne wykrywanie sprzetu."""
        try:
            # Pamiec RAM
            if psutil:
                total_memory = psutil.virtual_memory()
                self.max_memory_usage_percent = min(85.0, self.max_memory_usage_percent)
            
            # GPU
            try:
                import torch
                if torch.cuda.is_available():
                    self.gpu_available = True
                    gpu_mem = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                    self.max_gpu_memory_gb = gpu_mem * 0.85  # 85% dostepnej pamieci GPU
                    self.gpu_memory_buffer_gb = 1.0
            except ImportError:
                self.gpu_available = False
                
            # System operacyjny
            if platform.system() == "Windows":
                # Windows ma mniejsze buffery
                self.gpu_memory_buffer_gb = max(0.5, self.gpu_memory_buffer_gb)
                
        except ImportError:
            # psutil nie jest dostepne
            pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        return {
            "max_active_models": self.max_active_models,
            "max_concurrent_requests": self.max_concurrent_requests,
            "min_memory_gb": self.min_memory_gb,
            "max_memory_usage_percent": self.max_memory_usage_percent,
            "cleanup_strategy": self.cleanup_strategy.value,
            "gpu_available": self.gpu_available,
            "max_gpu_memory_gb": self.max_gpu_memory_gb,
            "gpu_memory_buffer_gb": self.gpu_memory_buffer_gb,
            "model_start_timeout": self.model_start_timeout,
            "model_work_timeout": self.model_work_timeout,
            "model_stop_timeout": self.model_stop_timeout,
            "save_memory_timeout": self.save_memory_timeout,
            "queue_width": self.queue_width
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HardwareConstraints':
        """Tworzenie z slownika."""
        return cls(
            max_active_models=data.get("max_active_models", 1),
            max_concurrent_requests=data.get("max_concurrent_requests", 1),
            min_memory_gb=data.get("min_memory_gb", 2.0),
            max_memory_usage_percent=data.get("max_memory_usage_percent", 85.0),
            cleanup_strategy=MemoryCleanupStrategy(data.get("cleanup_strategy", "basic")),
            gpu_available=data.get("gpu_available", False),
            max_gpu_memory_gb=data.get("max_gpu_memory_gb", 0.0),
            gpu_memory_buffer_gb=data.get("gpu_memory_buffer_gb", 1.0),
            model_start_timeout=data.get("model_start_timeout", 30.0),
            model_work_timeout=data.get("model_work_timeout", 300.0),
            model_stop_timeout=data.get("model_stop_timeout", 10.0),
            save_memory_timeout=data.get("save_memory_timeout", 15.0),
            queue_width=data.get("queue_width", 100)
        )


@dataclass
class ModelLimits:
    """Limity dla poszczegolnych modeli LLM."""
    
    # Ogolne limity
    default: Dict[str, float] = field(default_factory=lambda: {
        "timeout": 300.0,
        "memory_gb": 8.0,
        "tokens": 4096
    })
    
    # Limity per model (nadpisuja default)
    per_model: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Limity dla poszczegolnych typow zadan
    task_type_limits: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    def get_limits(self, model_name: str, task_type: Optional[str] = None) -> Dict[str, float]:
        """Pobranie limitow dla modelu i typu zadania."""
        limits = self.per_model.get(model_name, self.default).copy()
        
        if task_type:
            task_limits = self.task_type_limits.get(task_type, {})
            for key, value in task_limits.items():
                if key in limits:
                    # Uzyj wiekszej wartosci (bardziej restrykcyjny limit)
                    if value < limits[key]:
                        limits[key] = value
        
        return limits


@dataclass
class LLMQueueSettings:
    """Ustawienia kolejki LLM."""
    
    # Tryb pracy
    mode: QueueMode = QueueMode.PRIORITY
    
    # Ograniczenia sprzetowe
    hardware: HardwareConstraints = field(default_factory=HardwareConstraints)
    
    # Limity modeli
    limits: ModelLimits = field(default_factory=ModelLimits)
    
    # Logging
    log_queue_operations: bool = True
    log_model_operations: bool = True
    log_memory_usage: bool = True
    
    # Debug
    debug_mode: bool = False
    
    # Statystyki
    enable_statistics: bool = True
    stats_retention_days: int = 30
    
    def __post_init__(self):
        """Inicjalizacja po utworzeniu."""
        # Wykryj sprzet
        self.hardware.detect_hardware()
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        return {
            "mode": self.mode.value,
            "hardware": self.hardware.to_dict(),
            "log_queue_operations": self.log_queue_operations,
            "log_model_operations": self.log_model_operations,
            "log_memory_usage": self.log_memory_usage,
            "debug_mode": self.debug_mode,
            "enable_statistics": self.enable_statistics,
            "stats_retention_days": self.stats_retention_days
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMQueueSettings':
        """Tworzenie z slownika."""
        settings = cls(
            mode=QueueMode(data.get("mode", "priority")),
            hardware=HardwareConstraints.from_dict(data.get("hardware", {})),
            log_queue_operations=data.get("log_queue_operations", True),
            log_model_operations=data.get("log_model_operations", True),
            log_memory_usage=data.get("log_memory_usage", True),
            debug_mode=data.get("debug_mode", False),
            enable_statistics=data.get("enable_statistics", True),
            stats_retention_days=data.get("stats_retention_days", 30)
        )
        # Ustaw limity (nie sa seriazlizowane do dict)
        settings.limits = ModelLimits()
        return settings


def create_default_queue_config() -> LLMQueueSettings:
    """Tworzenie domyslnej konfiguracji kolejki."""
    return LLMQueueSettings()
