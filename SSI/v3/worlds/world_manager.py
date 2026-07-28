"""
SSI V3 World Manager - Centralny zarzadca swiatow

Modul odpowiedzialny za:
- Zarzadzanie kolekcja swiatow V3
- Budowanie nowych swiatow
- Koordynacje miedzy swiatami
- Integracje z V2 (dane) i V4 (agenci)

Zgodnie z:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 3.2
- 02_DATA_STRUCTURE.md Sekcja 4.2
- 10_IMPLEMENTATION_MAP.md Sekcja 3.3

Odpowiedzialnosc:
- Tworzenie i usuwanie swiatow
- Zarzadzanie cyklem zycia swiatow
- Koordynacja pamieci miedzy swiatami
- Dostarczanie interfejsu dostepu do swiatow dla V4

Zaleznosci:
- Zalezy od: SSI.v3.worlds.world (klasa World)
- Wspiera: V4 Agent System
- Korzysta z: V2 Model Laboratory (dane obserwacyjne)

Wersja: 1.0
Data: 2026-07-28
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Set, Callable, Protocol
from enum import Enum, auto
import uuid
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)


# =============================================================================
# PROTOCOLS (INTERFEJSY)
# =============================================================================

class WorldAccess(Protocol):
    """Interfejs dostepu do swiatow - dla agentow V4"""
    
    def get_world(self, world_id: str) -> Optional[Any]:
        """Pobiera swiat po ID"""
        ...
    
    def get_worlds_by_type(self, world_type: Any) -> List[Any]:
        """Pobiera swiaty po typie"""
        ...
    
    def search_worlds(self, **filters) -> List[Any]:
        """Szukaj swiatow wedlug filtrow"""
        ...


# =============================================================================
# WORLD MANAGER - GLOWNA KLASA
# =============================================================================

class WorldManager:
    """
    Centralny zarzadca swiatow V3.
    
    Odpowiedzialnosc:
    - Zarzadzanie kolekcja swiatow
    - Tworzenie i usuwanie swiatow
    - Koordynacja miedzy swiatami
    - Integracja z V2 (dane) i V4 (agenci)
    - Monitorowanie stanu i zdrowia swiatow
    
    Singleton - jedna instancja dla calego systemu
    """
    
    _instance: Optional["WorldManager"] = None
    
    @classmethod
    def get_instance(cls, config: Optional[Any] = None) -> "WorldManager":
        if cls._instance is None:
            cls._instance = cls(config)
            logger.info(f"WorldManager initialized: {cls._instance.manager_id}")
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None
    
    def __init__(self, config: Optional[Any] = None):
        from .world import World, WorldConfig, WorldType, WorldStatus
        self.World = World
        self.WorldConfig = WorldConfig
        self.WorldType = WorldType
        self.WorldStatus = WorldStatus
        
        self.manager_id = str(uuid.uuid4().hex[:12])
        self._worlds: Dict[str, Any] = {}
        self._world_index: Dict[str, Set[str]] = {}
        self._stats: Dict[str, Any] = {
            "total_worlds": 0,
            "active_worlds": 0,
            "total_observations": 0
        }
        self._ensure_directories()
        logger.info(f"WorldManager {self.manager_id} ready")


def tworz_world_manager(config: Optional[Any] = None) -> WorldManager:
    """Fabryka tworząca WorldManager (Singleton)."""
    return WorldManager.get_instance(config)
    
    def create_world(self, nazwa: str, world_type: Optional[Any] = None, **kwargs) -> Any:
        if len(self._worlds) >= 100:
            raise ValueError("Max worlds reached")
        
        config = self.WorldConfig(
            world_id=str(uuid.uuid4().hex[:12]),
            nazwa=nazwa,
            world_type=world_type or self.WorldType.SWIAT_1_ZMIANY_KURSOW
        )
        world = self.World(config=config, nazwa=nazwa)
        world.world_id = config.world_id
        world.status = self.WorldStatus.UNINITIALIZED
        
        self._worlds[world.world_id] = world
        self._index_world(world)
        self._stats["total_worlds"] += 1
        logger.info(f"World created: {world.world_id} ({nazwa})")
        return world
    
    def get_world(self, world_id: str) -> Optional[Any]:
        return self._worlds.get(world_id)
    
    def get_worlds_by_type(self, world_type: Any) -> List[Any]:
        return [w for w in self._worlds.values() if w.config.world_type == world_type]
    
    def get_active_worlds(self) -> List[Any]:
        return [w for w in self._worlds.values() if w.status == self.WorldStatus.ACTIVE]
    
    def build_world(self, world_id: str, data: Optional[List[Dict[str, Any]]] = None) -> bool:
        if world_id not in self._worlds:
            return False
        world = self._worlds[world_id]
        try:
            world.status = self.WorldStatus.BUILDING
            if data:
                for observation in data:
                    world.dodaj_obserwacje(observation)
            world.status = self.WorldStatus.ACTIVE
            self._stats["active_worlds"] += 1
            logger.info(f"World built: {world_id}")
            return True
        except Exception as e:
            world.status = self.WorldStatus.ERROR
            logger.error(f"Build error: {e}")
            return False
    
    def destroy_world(self, world_id: str) -> bool:
        if world_id not in self._worlds:
            return False
        world = self._worlds[world_id]
        if world.status == self.WorldStatus.ACTIVE:
            world.status = self.WorldStatus.ARCHIVED
        self._deindex_world(world)
        del self._worlds[world_id]
        self._stats["total_worlds"] -= 1
        logger.info(f"World destroyed: {world_id}")
        return True
    
    def _index_world(self, world: Any) -> None:
        pass
    
    def _deindex_world(self, world: Any) -> None:
        pass
    
    def _ensure_directories(self) -> None:
        Path("data/v3/worlds/").parent.mkdir(parents=True, exist_ok=True)
    
    def get_stats(self) -> Dict[str, Any]:
        return dict(self._stats)


__all__ = [
    'WorldManager',
    'tworz_world_manager',
    'WorldManager.get_instance',
    'WorldManager.reset_instance'
]
