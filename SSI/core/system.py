"""
SSI System - Główny system zarządzania SSI

Klasa SSISystem jest sercem całego ekosystemu. Odpowiada za:
- Inicjalizację wszystkich modułów
- Zarządzanie zależnościami między modułami
- Koordynację przepływu danych
- Monitorowanie stanu systemu

Wersja: 1.0
Data: 2026-07-28

Zgodność z dokumentacją: 01_SYSTEM_ARCHITECTURE.md
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class SystemStatus(Enum):
    """Status systemu SSI"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class SystemPhase(Enum):
    """Fazy implementacji systemu"""
    DATA_LAYER = "data_layer"
    MODEL_LABORATORY = "model_laboratory"
    WORLD_MEMORY = "world_memory"
    AGENT_EVOLUTION = "agent_evolution"
    STRATEGY_SYSTEM = "strategy_system"
    LABORATORIES = "laboratories"
    FEEDBACK_LOOP = "feedback_loop"
    DECISION_ENGINE = "decision_engine"


@dataclass
class SystemMetadata:
    """Metadane systemu SSI"""
    version: str = "1.0.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    author: str = "SSI System"
    description: str = "Self Learning Intelligence Ecosystem"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "author": self.author,
            "description": self.description
        }


@dataclass
class ModuleInfo:
    """Informacje o module"""
    module_name: str
    module_type: str
    version: str
    dependencies: List[str] = field(default_factory=list)
    status: str = "uninitialized"
    priority: int = 0
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "module_name": self.module_name,
            "module_type": self.module_type,
            "version": self.version,
            "dependencies": self.dependencies,
            "status": self.status,
            "priority": self.priority,
            "description": self.description
        }


class SSISystem:
    """
    Główny system zarządzania SSI
    
    Odpowiada za integrację wszystkich modułów i podsystemów.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.metadata = SystemMetadata()
        self.modules: Dict[str, ModuleInfo] = {}
        self.components: Dict[str, Any] = {}
        self.status = SystemStatus.UNINITIALIZED
        self.phase = SystemPhase.DATA_LAYER
        self.config = config or {}
        self._setup_logging()
        logger.info(f"SSI System zainicjowany. Wersja: {self.metadata.version}")
    
    def _setup_logging(self) -> None:
        # Użyj centralnej konfiguracji logowania
        from SSI.core.logging_config import setup_logging
        setup_logging(level=logging.INFO, json_format=False)
    
    def register_module(self, module_name: str, module_type: str, version: str, 
                       dependencies: List[str] = None, priority: int = 0,
                       description: str = "") -> None:
        if dependencies is None:
            dependencies = []
        self.modules[module_name] = ModuleInfo(
            module_name=module_name, module_type=module_type,
            version=version, dependencies=dependencies,
            priority=priority, description=description
        )
        logger.info(f"Zarejestrowano moduł: {module_name}")
    
    def register_component(self, component_name: str, component: Any) -> None:
        self.components[component_name] = component
        logger.info(f"Zarejestrowano komponent: {component_name}")
    
    def get_module(self, module_name: str) -> Optional[Any]:
        return self.components.get(module_name)
    
    def get_system_status(self) -> Dict[str, Any]:
        return {
            "system_status": self.status.value,
            "current_phase": self.phase.value,
            "metadata": self.metadata.to_dict(),
            "modules": {name: info.to_dict() for name, info in self.modules.items()},
            "components": list(self.components.keys())
        }
    
    def set_implementation_phase(self, phase: SystemPhase) -> None:
        self.phase = phase
        logger.info(f"Ustawiono fazę: {phase.value}")
    
    def __str__(self) -> str:
        return f"SSISystem(v{self.metadata.version}, status={self.status.value}, phase={self.phase.value})"
    
    def to_json(self) -> str:
        return json.dumps(self.get_system_status(), indent=2, ensure_ascii=False)
