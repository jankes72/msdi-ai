"""
SSI Module - Klasa bazowa dla modułów SSI

Moduły w SSI:
- V2 Model Laboratory
- V3 World Memory System
- V4 Agent Evolution
- Strategy Intelligence Engine
- Decision Laboratories
- Feedback Loop

Wersja: 1.0
Data: 2026-07-28
"""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class ModuleStatus(Enum):
    """Status modułu"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class ModuleType(Enum):
    """Typy modułów SSI"""
    DATA_LAYER = "data_layer"
    MODEL_LABORATORY = "model_laboratory"
    WORLD_MEMORY = "world_memory"
    AGENT_EVOLUTION = "agent_evolution"
    STRATEGY_ENGINE = "strategy_engine"
    LABORATORIES = "laboratories"
    FEEDBACK_LOOP = "feedback_loop"
    DECISION_ENGINE = "decision_engine"


@dataclass
class ModuleConfig:
    """Konfiguracja modułu"""
    module_name: str
    module_type: str
    version: str = "1.0.0"
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    priority: int = 0
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "module_name": self.module_name,
            "module_type": self.module_type,
            "version": self.version,
            "description": self.description,
            "dependencies": self.dependencies,
            "priority": self.priority,
            "enabled": self.enabled
        }


class SSIModule(ABC):
    """Abstraktna klasa bazowa dla modułów SSI"""
    
    def __init__(self, config: ModuleConfig):
        self.config = config
        self.status = ModuleStatus.UNINITIALIZED
        self.dependencies = config.dependencies or []
        self.created_at = datetime.now()
        self.initialized_at: Optional[datetime] = None
        self.errors: List[str] = []
        logger.info(f"Utworzono moduł: {config.module_name}")
    
    @abstractmethod
    def initialize(self) -> bool:
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        pass
    
    def set_status(self, status: ModuleStatus) -> None:
        self.status = status
        logger.info(f"Moduł {self.config.module_name}: {status.value}")
    
    def add_error(self, error: str) -> None:
        self.errors.append(error)
        logger.error(f"Moduł {self.config.module_name}: {error}")
    
    def get_status_report(self) -> Dict[str, Any]:
        return {
            "module_name": self.config.module_name,
            "module_type": self.config.module_type,
            "status": self.status.value,
            "version": self.config.version,
            "created_at": self.created_at.isoformat(),
            "errors_count": len(self.errors)
        }
    
    def is_ready(self) -> bool:
        return self.status in [ModuleStatus.READY, ModuleStatus.RUNNING]
    
    def to_json(self) -> str:
        return json.dumps(self.get_status_report(), indent=2, ensure_ascii=False)


class BaseModule(SSIModule):
    """Bazowa implementacja modułu SSI"""
    
    def initialize(self) -> bool:
        if self.status != ModuleStatus.UNINITIALIZED:
            return False
        try:
            self.set_status(ModuleStatus.INITIALIZING)
            if not self._initialize_internal():
                self.set_status(ModuleStatus.ERROR)
                return False
            self.initialized_at = datetime.now()
            self.set_status(ModuleStatus.READY)
            return True
        except Exception as e:
            self.add_error(str(e))
            self.set_status(ModuleStatus.ERROR)
            return False
    
    def _initialize_internal(self) -> bool:
        return True
    
    def shutdown(self) -> bool:
        try:
            self.set_status(ModuleStatus.SHUTDOWN)
            return True
        except Exception as e:
            self.add_error(str(e))
            return False
