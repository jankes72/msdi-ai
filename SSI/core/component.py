"""
SSI Component - Klasa bazowa dla komponentów SSI

Komponenty w SSI:
- Agenci (V4)
- Świecie (V3)  
- Strategie
- Pamięci
- Laboratoria

Wersja: 1.0
Data: 2026-07-28
"""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
import logging
import json
import uuid

logger = logging.getLogger(__name__)


class ComponentStatus(Enum):
    CREATED = "created"
    INITIALIZED = "initialized"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    ARCHIVED = "archived"


class ComponentType(Enum):
    WORLD = "world"
    AGENT = "agent"
    STRATEGY = "strategy"
    MEMORY = "memory"
    LABORATORY = "laboratory"
    MODEL = "model"
    DATA_PROVIDER = "data_provider"


@dataclass
class ComponentConfig:
    component_name: str
    component_type: str
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_name": self.component_name,
            "component_type": self.component_type,
            "description": self.description,
            "parameters": self.parameters,
            "enabled": self.enabled
        }


class SSIComponent(ABC):
    """Abstraktna klasa bazowa dla komponentów SSI"""
    
    def __init__(self, config: ComponentConfig):
        self.component_id = str(uuid.uuid4())
        self.config = config
        self.status = ComponentStatus.CREATED
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.errors: List[str] = []
        self.metadata: Dict[str, Any] = {}
        logger.info(f"Utworzono komponent: {config.component_name}")
    
    @abstractmethod
    def initialize(self) -> bool:
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        pass
    
    def set_status(self, status: ComponentStatus) -> None:
        self.status = status
        self.updated_at = datetime.now()
    
    def add_error(self, error: str) -> None:
        self.errors.append(f"[{datetime.now().isoformat()}] {error}")
    
    def get_status_report(self) -> Dict[str, Any]:
        return {
            "component_id": self.component_id,
            "component_name": self.config.component_name,
            "component_type": self.config.component_type,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "errors_count": len(self.errors)
        }
    
    def is_active(self) -> bool:
        return self.status in [ComponentStatus.ACTIVE, ComponentStatus.INITIALIZED]
    
    def to_json(self) -> str:
        return json.dumps(self.get_status_report(), indent=2, ensure_ascii=False)


class BaseComponent(SSIComponent):
    """Bazowa implementacja komponentu SSI"""
    
    def initialize(self) -> bool:
        if self.status != ComponentStatus.CREATED:
            return False
        try:
            self.set_status(ComponentStatus.INITIALIZED)
            return True
        except Exception as e:
            self.add_error(str(e))
            self.set_status(ComponentStatus.ERROR)
            return False
    
    def validate(self) -> bool:
        return self.status != ComponentStatus.ERROR
