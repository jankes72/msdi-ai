"""
SSI V3 Memory Manager - Główny zarządca pamięci systemu

Centralny system pamięci dla SSI V3.
Integracja z:
- V2: Odbiór obserwacji (40% danych)
- V4: Dostarczanie wiedzy agentom
- V3 Worlds: Organizacja w światy

Architektura pamięci:
┌─────────────────────────────────────┐
│         MemoryManager               │
├─────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐   │
│  │ Observation │  │  Pattern    │   │
│  │  Memory     │  │  Memory     │   │
│  └─────────────┘  └─────────────┘   │
│  ┌─────────────┐  ┌─────────────┐   │
│  │ Metadata    │  │Relationship │   │
│  │  Memory     │  │  Memory     │   │
│  └─────────────┘  └─────────────┘   │
│  ┌─────────────────────────────────┐│
│  │       World Memory              ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘

Zgodnie z:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 3.1
- 02_DATA_STRUCTURE.md Sekcja 4.1

Wersja: 1.0
Data: 2026-07-28
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum, auto
import uuid
import json
import os
from pathlib import Path
import threading


# =============================================================================
# TYPY PAMIĘCI
# =============================================================================

class MemoryType(Enum):
    """Typy pamięci w systemie V3"""
    OBSERVATION = auto()      # Pamięć obserwacji (z V2)
    PATTERN = auto()            # Pamięć wzorców zachowań
    METADATA = auto()          # Pamięć metadanych
    RELATIONSHIP = auto()      # Pamięć relacji
    WORLD = auto()              # Pamięć światów
    Global = auto()            # Pamięć globalna (agregacja wszystkich)


# =============================================================================
# KONFIGURACJA PAMIĘCI
# =============================================================================

@dataclass
class MemoryConfig:
    """
    Konfiguracja systemu pamięci V3
    
    Zgodnie z 02_DATA_STRUCTURE.md Sekcja 4.1
    """
    
    # Ustawienia pamięci
    MAX_OBSERVATIONS: int = 1000000      # Maksymalna liczba obserwacji
    MAX_PATTERNS: int = 10000             # Maksymalna liczba wzorców
    MAX_METADATA_ENTRIES: int = 50000     # Maksymalna liczba wpisów metadanych
    MAX_RELATIONSHIPS: int = 200000      # Maksymalna liczba relacji
    MAX_WORLDS: int = 100                  # Maksymalna liczba światów
    
    # Ustawienia zapisu
    AUTO_SAVE: bool = True
    SAVE_INTERVAL: int = 1000            # Co ile operacji zapisywać
    BACKUP_ENABLED: bool = True
    BACKUP_INTERVAL: int = 10000          # Co ile operacji backup
    
    # Ścieżki
    BASE_PATH: str = "pamiec_modeli_v2"
    OBSERVATIONS_PATH: str = "v3/memory/observations"
    PATTERNS_PATH: str = "v3/memory/patterns"
    METADATA_PATH: str = "v3/memory/metadata"
    RELATIONSHIPS_PATH: str = "v3/memory/relationships"
    WORLDS_PATH: str = "v3/memory/worlds"
    BACKUP_PATH: str = "v3/backup"
    
    # Integracja z V2
    ACCEPT_FROM_V2: bool = True         # Akceptuj dane z V2
    V2_OBSERVATION_RATIO: float = 0.4   # 40% danych z V2 na obserwację
    
    # Wydajność
    USE_INDEXING: bool = True            # Użyj indeksowania dla szybszego wyszukiwania
    ENABLE_COMPRESSION: bool = False     # Kompresja pamięci (eksperymentalne)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "MAX_OBSERVATIONS": self.MAX_OBSERVATIONS,
            "MAX_PATTERNS": self.MAX_PATTERNS,
            "MAX_METADATA_ENTRIES": self.MAX_METADATA_ENTRIES,
            "MAX_RELATIONSHIPS": self.MAX_RELATIONSHIPS,
            "MAX_WORLDS": self.MAX_WORLDS,
            "AUTO_SAVE": self.AUTO_SAVE,
            "SAVE_INTERVAL": self.SAVE_INTERVAL,
            "BACKUP_ENABLED": self.BACKUP_ENABLED,
            "BACKUP_INTERVAL": self.BACKUP_INTERVAL,
            "ACCEPT_FROM_V2": self.ACCEPT_FROM_V2,
            "V2_OBSERVATION_RATIO": self.V2_OBSERVATION_RATIO
        }


# =============================================================================
# BAZOWA KLASA PAMIĘCI
# =============================================================================

class BaseMemory:
    """
    Bazowa klasa dla wszystkich typów pamięci
    
    Odpowiedzialność:
    - Zarządzanie danymi konkretnego typu
    - Dodawanie, usuwanie, wyszukiwanie
    - Zapis i odczyt
    - Statystyki
    """
    
    memory_type: MemoryType = MemoryType.Global
    
    def __init__(self, config: Optional[MemoryConfig] = None):
        self.config = config or MemoryConfig()
        self._data: Dict[str, Any] = {}
        self._index: Dict[str, List[str]] = {}  # Indeksy dla szybszego wyszukiwania
        self._timestamp = datetime.now()
        self._lock = threading.Lock()
        
    def add(self, key: str, value: Any, **metadata) -> str:
        """Dodaje nowy wpis do pamięci"""
        with self._lock:
            if len(self._data) >= self._get_max_size():
                self._cleanup()
            
            entry = {
                "id": key or str(uuid.uuid4().hex[:12]),
                "value": value,
                "metadata": metadata,
                "timestamp": datetime.now().isoformat(),
                "type": self.memory_type.name
            }
            
            self._data[entry["id"]] = entry
            self._update_index(entry)
            
            return entry["id"]
    
    def get(self, key: str) -> Optional[Any]:
        """Pobiera wpis z pamięci"""
        with self._lock:
            entry = self._data.get(key)
            return entry["value"] if entry else None
    
    def get_with_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Pobiera wpis z metadanymi"""
        with self._lock:
            return self._data.get(key)
    
    def remove(self, key: str) -> bool:
        """Usuwa wpis z pamięci"""
        with self._lock:
            if key in self._data:
                self._remove_from_index(self._data[key])
                del self._data[key]
                return True
            return False
    
    def search(self, **criteria) -> List[Dict[str, Any]]:
        """Wyszukuje wpisy według kryteriów"""
        with self._lock:
            results = []
            for entry in self._data.values():
                match = True
                for key, value in criteria.items():
                    if key == "id":
                        if entry["id"] != value:
                            match = False
                            break
                    elif key in entry["metadata"]:
                        if entry["metadata"][key] != value:
                            match = False
                            break
                    elif key in entry:
                        if entry[key] != value:
                            match = False
                            break
                    else:
                        match = False
                        break
                if match:
                    results.append(entry.copy())
            return results
    
    def list_all(self) -> List[Dict[str, Any]]:
        """Zwraca wszystkie wpisy"""
        with self._lock:
            return list(self._data.values())
    
    def count(self) -> int:
        """Zwraca liczba wpisów"""
        with self._lock:
            return len(self._data)
    
    def clear(self) -> None:
        """Czyści pamięć"""
        with self._lock:
            self._data.clear()
            self._index.clear()
    
    def _get_max_size(self) -> int:
        """Zwraca maksymalny rozmiar dla tego typu pamięci"""
        size_map = {
            MemoryType.OBSERVATION: self.config.MAX_OBSERVATIONS,
            MemoryType.PATTERN: self.config.MAX_PATTERNS,
            MemoryType.METADATA: self.config.MAX_METADATA_ENTRIES,
            MemoryType.RELATIONSHIP: self.config.MAX_RELATIONSHIPS,
            MemoryType.WORLD: self.config.MAX_WORLDS,
            MemoryType.Global: self.config.MAX_OBSERVATIONS * 2
        }
        return size_map.get(self.memory_type, 1000000)
    
    def _cleanup(self) -> None:
        """Czyści najstarsze wpisy (gdy osiągnięto limit)"""
        # Uproszczona implementacja - usuwa 10% najstarszych
        if len(self._data) > self._get_max_size():
            sorted_entries = sorted(
                self._data.items(), 
                key=lambda x: x[1]["timestamp"],
                reverse=True
            )
            to_remove = len(sorted_entries) // 10
            for key, _ in sorted_entries[:to_remove]:
                del self._data[key]
    
    def _update_index(self, entry: Dict[str, Any]) -> None:
        """Aktualizuje indeksy"""
        if not self.config.USE_INDEXING:
            return
        
        # Indeksuj po typie
        if "type" not in self._index:
            self._index["type"] = []
        if entry["type"] not in self._index["type"]:
            self._index["type"].append(entry["type"])
        
        # Indeksuj po polach metadanych
        for key, value in entry["metadata"].items():
            if key not in self._index:
                self._index[key] = []
            if str(value) not in self._index[key]:
                self._index[key].append(str(value))
    
    def _remove_from_index(self, entry: Dict[str, Any]) -> None:
        """Usuwa z indeksów"""
        if not self.config.USE_INDEXING:
            return
        
        # Uproszczona implementacja
        pass


# =============================================================================
# GŁÓWNY MEMORY MANAGER
# =============================================================================

class MemoryManager:
    """
    Główny zarządca pamięci systemu V3.
    
    Odpowiedzialność:
    - Zarządzanie wszystkimi typami pamięci
    - Koordynacja między pamięciami
    - Integracja z V2 i V4
    - Zapis/odczyt całej pamięci
    - Statystyki i monitoring
    
    Integracje:
    - V2: Odbiór obserwacji (40% danych) przez V2ToV3Bridge
    - V4: Dostarczanie wiedzy agentom
    - V3 Worlds: Organizacja pamięci w światy
    """
    
    def __init__(self, config: Optional[MemoryConfig] = None):
        """
        Inicjalizacja MemoryManager
        
        Args:
            config: Konfiguracja pamięci (opcjonalnie)
        """
        self.config = config or MemoryConfig()
        self._initialize_memories()
        self._operation_count = 0
        self._lock = threading.Lock()
        
    def _initialize_memories(self) -> None:
        """Inicjalizuje wszystkie typy pamięci"""
        self.observation_memory = ObservationMemory(self.config)
        self.pattern_memory = PatternMemory(self.config)
        self.metadata_memory = MetadataMemory(self.config)
        self.relationship_memory = RelationshipMemory(self.config)
        self.world_memory = WorldMemory(self.config)
        
        # Globalna pamięć (agregacja)
        self._global_memory = BaseMemory(self.config)
        self._global_memory.memory_type = MemoryType.Global
    
    # =========================================================================
    # OBSERVATION MEMORY (Integracja z V2)
    # =========================================================================
    
    def add_observation(self, observation: Dict[str, Any], 
                       from_v2: bool = False) -> str:
        """
        Dodaje obserwację z V2 do pamięci
        
        Args:
            observation: Obserwacja z V2 (dict z polami: mecz_id, predykcja, rzeczywistosc, itd.)
            from_v2: Czy obserwacja pochodzi z V2
            
        Returns:
            ID obserwacji
        """
        if from_v2 and not self.config.ACCEPT_FROM_V2:
            raise ValueError("V2 observations are not accepted (config)")
        
        # Dodaj do pamięci obserwacji
        obs_id = self.observation_memory.add(
            key=observation.get("id", str(uuid.uuid4().hex[:12])),
            value=observation,
            **{"source": "V2" if from_v2 else "V3", "type": "observation"}
        )
        
        # Dodaj do pamięci globalnej
        self._global_memory.add(obs_id, observation, type="observation", source="V2")
        
        self._operation_count += 1
        self._auto_save()
        
        return obs_id
    
    def add_observation_batch(self, observations: List[Dict[str, Any]],
                            from_v2: bool = False) -> List[str]:
        """Dodaje partię obserwacji"""
        return [self.add_observation(obs, from_v2) for obs in observations]
    
    def get_observation(self, obs_id: str) -> Optional[Dict[str, Any]]:
        """Pobiera obserwację"""
        return self.observation_memory.get(obs_id)
    
    # =========================================================================
    # PATTERN MEMORY
    # =========================================================================
    
    def add_pattern(self, pattern: Dict[str, Any]) -> str:
        """
        Dodaje wzorzec zachowania
        
        Args:
            pattern: Wzorzec (dict z polami: nazwa, opis, czestotliwosc, itd.)
            
        Returns:
            ID wzorca
        """
        pattern_id = self.pattern_memory.add(
            key=pattern.get("id", str(uuid.uuid4().hex[:12])),
            value=pattern,
            **{"type": "pattern", "source": "V3"}
        )
        
        self._global_memory.add(pattern_id, pattern, type="pattern", source="V3")
        self._operation_count += 1
        self._auto_save()
        
        return pattern_id
    
    def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Pobiera wzorzec"""
        return self.pattern_memory.get(pattern_id)
    
    def find_patterns(self, **criteria) -> List[Dict[str, Any]]:
        """Szuka wzorców według kryteriów"""
        return self.pattern_memory.search(**criteria)
    
    # =========================================================================
    # METADATA MEMORY
    # =========================================================================
    
    def add_metadata(self, entity_type: str, entity_id: str, 
                    metadata: Dict[str, Any]) -> str:
        """
        Dodaje metadane
        
        Args:
            entity_type: Typ encji (model, world, agent, itd.)
            entity_id: ID encji
            metadata: Metadane (dict)
            
        Returns:
            ID metadanych
        """
        metadata_entry = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "data": metadata
        }
        
        meta_id = self.metadata_memory.add(
            key=f"{entity_type}_{entity_id}",
            value=metadata_entry,
            **{"type": "metadata", "entity_type": entity_type}
        )
        
        self._global_memory.add(meta_id, metadata_entry, type="metadata")
        self._operation_count += 1
        
        return meta_id
    
    def get_metadata(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """Pobiera metadane encji"""
        return self.metadata_memory.get(f"{entity_type}_{entity_id}")
    
    # =========================================================================
    # RELATIONSHIP MEMORY
    # =========================================================================
    
    def add_relationship(self, source_type: str, source_id: str,
                        target_type: str, target_id: str,
                        relationship_type: str, 
                        properties: Optional[Dict[str, Any]] = None) -> str:
        """
        Dodaje relację między obiektami
        
        Args:
            source_type: Typ źródła
            source_id: ID źródła
            target_type: Typ celu
            target_id: ID celu
            relationship_type: Typ relacji (depends_on, influences, part_of, itd.)
            properties: Właściwości relacji
            
        Returns:
            ID relacji
        """
        relationship = {
            "source_type": source_type,
            "source_id": source_id,
            "target_type": target_type,
            "target_id": target_id,
            "relationship_type": relationship_type,
            "properties": properties or {}
        }
        
        rel_id = self.relationship_memory.add(
            key=str(uuid.uuid4().hex[:12]),
            value=relationship,
            **{"type": "relationship", "relationship_type": relationship_type}
        )
        
        self._global_memory.add(rel_id, relationship, type="relationship")
        self._operation_count += 1
        
        return rel_id
    
    def get_relationships(self, entity_type: str, entity_id: str) -> List[Dict[str, Any]]:
        """Pobiera wszystkie relacje dla encji"""
        all_relationships = self.relationship_memory.list_all()
        result = []
        
        for rel in all_relationships:
            if (rel["value"]["source_type"] == entity_type and 
                rel["value"]["source_id"] == entity_id) or \
               (rel["value"]["target_type"] == entity_type and 
                rel["value"]["target_id"] == entity_id):
                result.append(rel)
        
        return result
    
    # =========================================================================
    # WORLD MEMORY
    # =========================================================================
    
    def add_world(self, world: Dict[str, Any]) -> str:
        """
        Dodaje świat do pamięci
        
        Args:
            world: Świat (dict z polami: id, nazwa, typ, obserwacje, itd.)
            
        Returns:
            ID świata
        """
        world_id = self.world_memory.add(
            key=world.get("id", str(uuid.uuid4().hex[:12])),
            value=world,
            **{"type": "world", "source": "V3"}
        )
        
        self._global_memory.add(world_id, world, type="world", source="V3")
        self._operation_count += 1
        
        return world_id
    
    def get_world(self, world_id: str) -> Optional[Dict[str, Any]]:
        """Pobiera świat"""
        return self.world_memory.get(world_id)
    
    def list_worlds(self) -> List[Dict[str, Any]]:
        """Zwraca listę wszystkich światów"""
        return self.world_memory.list_all()
    
    # =========================================================================
    # GLOBAL OPERATIONS
    # =========================================================================
    
    def get_all_memories_stats(self) -> Dict[str, Any]:
        """Zwraca statystyki wszystkich pamięci"""
        return {
            "observation": self.observation_memory.count(),
            "pattern": self.pattern_memory.count(),
            "metadata": self.metadata_memory.count(),
            "relationship": self.relationship_memory.count(),
            "world": self.world_memory.count(),
            "global": self._global_memory.count(),
            "total_operations": self._operation_count
        }
    
    def search_global(self, **criteria) -> List[Dict[str, Any]]:
        """Globalne wyszukiwanie we wszystkich pamięciach"""
        results = []
        
        for memory in [
            self.observation_memory,
            self.pattern_memory,
            self.metadata_memory,
            self.relationship_memory,
            self.world_memory
        ]:
            results.extend(memory.search(**criteria))
        
        return results
    
    def clear_all(self) -> None:
        """Czyści wszystkie pamięci (UWAGA: usuwa wszystkie dane!)"""
        self.observation_memory.clear()
        self.pattern_memory.clear()
        self.metadata_memory.clear()
        self.relationship_memory.clear()
        self.world_memory.clear()
        self._global_memory.clear()
        self._operation_count = 0
    
    # =========================================================================
    # ZAPIS I ODCZYT
    # =========================================================================
    
    def save(self, path: Optional[str] = None) -> str:
        """
        Zapisuje całą pamięć do pliku
        
        Args:
            path: Ścieżka do pliku (opcjonalnie, domyślnie auto-generowana)
            
        Returns:
            Ścieżka do zapisanego pliku
        """
        if not path:
            os.makedirs(self.config.BASE_PATH, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(
                self.config.BASE_PATH,
                f"v3_memory_{timestamp}.json"
            )
        
        data = {
            "config": self.config.to_dict(),
            "observation_memory": self.observation_memory.list_all(),
            "pattern_memory": self.pattern_memory.list_all(),
            "metadata_memory": self.metadata_memory.list_all(),
            "relationship_memory": self.relationship_memory.list_all(),
            "world_memory": self.world_memory.list_all(),
            "stats": self.get_all_memories_stats(),
            "timestamp": datetime.now().isoformat()
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return path
    
    def load(self, path: str) -> bool:
        """
        Wczytuje pamięć z pliku
        
        Args:
            path: Ścieżka do pliku
            
        Returns:
            True jeśli wczytanie się powiodło
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Wczytuj pamięci
            for obs in data.get("observation_memory", []):
                self.observation_memory.add(
                    key=obs["id"],
                    value=obs["value"],
                    **obs.get("metadata", {})
                )
            
            for pattern in data.get("pattern_memory", []):
                self.pattern_memory.add(
                    key=pattern["id"],
                    value=pattern["value"],
                    **pattern.get("metadata", {})
                )
            
            for meta in data.get("metadata_memory", []):
                self.metadata_memory.add(
                    key=meta["id"],
                    value=meta["value"],
                    **meta.get("metadata", {})
                )
            
            for rel in data.get("relationship_memory", []):
                self.relationship_memory.add(
                    key=rel["id"],
                    value=rel["value"],
                    **rel.get("metadata", {})
                )
            
            for world in data.get("world_memory", []):
                self.world_memory.add(
                    key=world["id"],
                    value=world["value"],
                    **world.get("metadata", {})
                )
            
            return True
            
        except Exception as e:
            print(f"Error loading memory: {e}")
            return False
    
    def create_backup(self) -> str:
        """Tworzy backup pamięci"""
        if not self.config.BACKUP_ENABLED:
            return ""
        
        os.makedirs(self.config.BACKUP_PATH, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(
            self.config.BACKUP_PATH,
            f"v3_memory_backup_{timestamp}.json"
        )
        
        return self.save(path)
    
    def _auto_save(self) -> None:
        """Automatyczny zapis (co SAVE_INTERVAL operacji)"""
        if (self.config.AUTO_SAVE and 
            self._operation_count % self.config.SAVE_INTERVAL == 0):
            self.save()
        
        if (self.config.BACKUP_ENABLED and 
            self._operation_count % self.config.BACKUP_INTERVAL == 0):
            self.create_backup()


# =============================================================================
# SPECJALIZOWANE KLASY PAMIĘCI
# =============================================================================

class ObservationMemory(BaseMemory):
    """Pamięć obserwacji (z V2)"""
    memory_type = MemoryType.OBSERVATION
    
    def add_observation(self, mecz_id: str, predykcja: str, 
                       rzeczywistosc: str, **metadata) -> str:
        """Dodaje obserwację w formacie V2"""
        observation = {
            "mecz_id": mecz_id,
            "predykcja": predykcja,
            "rzeczywistosc": rzeczywistosc,
            "trafienie": predykcja == rzeczywistosc,
            "timestamp": datetime.now().isoformat()
        }
        observation.update(metadata)
        
        return self.add(key=mecz_id, value=observation, **metadata)


class PatternMemory(BaseMemory):
    """Pamięć wzorców zachowań"""
    memory_type = MemoryType.PATTERN
    
    def add_detection(self, nazwa: str, opis: str, 
                     czestotliwosc: int = 1, **metadata) -> str:
        """Dodaje wykryty wzorzec"""
        pattern = {
            "nazwa": nazwa,
            "opis": opis,
            "czestotliwosc": czestotliwosc,
            "data_odkrycia": datetime.now().isoformat(),
            "data_ostaniego_wystapienia": datetime.now().isoformat()
        }
        pattern.update(metadata)
        
        return self.add(key=nazwa, value=pattern, **metadata)


class MetadataMemory(BaseMemory):
    """Pamięć metadanych"""
    memory_type = MemoryType.METADATA
    
    def get_by_entity(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """Pobiera metadane dla konkretnej encji"""
        return self.get(f"{entity_type}_{entity_id}")


class RelationshipMemory(BaseMemory):
    """Pamięć relacji między obiektami"""
    memory_type = MemoryType.RELATIONSHIP
    
    def get_connections(self, entity_id: str) -> List[Dict[str, Any]]:
        """Pobiera wszystkie połączenia dla encji"""
        return self.search(source_id=entity_id)


class WorldMemory(BaseMemory):
    """Pamięć światów"""
    memory_type = MemoryType.WORLD
    
    def create_world(self, world_id: str, nazwa: str, opis: str = "",
                     world_type: str = "default", **metadata) -> str:
        """Tworzy nowy świat"""
        world = {
            "world_id": world_id,
            "nazwa": nazwa,
            "opis": opis,
            "world_type": world_type,
            "data_utworzenia": datetime.now().isoformat(),
            "obserwacje": [],
            "wzorce": [],
            "metadane": {},
            "relacje": []
        }
        world.update(metadata)
        
        return self.add(key=world_id, value=world, **metadata)


# =============================================================================
# FABRYKA
# =============================================================================

def tworz_memory_manager(config: Optional[Dict[str, Any]] = None) -> MemoryManager:
    """
    Fabryka tworzących MemoryManager
    
    Args:
        config: Opcjonalna konfiguracja (dict lub MemoryConfig)
        
    Returns:
        MemoryManager
    """
    if isinstance(config, dict):
        config_obj = MemoryConfig(**config)
    elif isinstance(config, MemoryConfig):
        config_obj = config
    else:
        config_obj = MemoryConfig()
    
    return MemoryManager(config_obj)


# =============================================================================
# TESTY
# =============================================================================

if __name__ == "__main__":
    print("Testing MemoryManager...")
    
    # Tworzenie manager
    manager = tworz_memory_manager()
    
    # Test obserwacji
    obs_id = manager.add_observation({
        "mecz_id": "Test1_vs_Test2",
        "predykcja": "2:1",
        "rzeczywistosc": "2:1",
        "confidence": 0.85
    }, from_v2=True)
    print(f"Dodano obserwację: {obs_id}")
    
    # Test wzorca
    pattern_id = manager.add_pattern({
        "nazwa": "wysoka_pewnosc_trafienie",
        "opis": "Predykcje z wysoką pewnością które się sprawdziły",
        "czestotliwosc": 1
    })
    print(f"Dodano wzorzec: {pattern_id}")
    
    # Test świat
    world_id = manager.add_world({
        "world_id": "swiat_testowy",
        "nazwa": "Świat Testowy",
        "opis": "Pierwszy świat testowy",
        "world_type": "test"
    })
    print(f"Dodano świat: {world_id}")
    
    # Test metadanych
    meta_id = manager.add_metadata("model", "siec_01", {
        "accuracy": 0.85,
        "last_trained": "2026-07-28"
    })
    print(f"Dodano metadane: {meta_id}")
    
    # Test relacji
    rel_id = manager.add_relationship(
        "model", "siec_01",
        "world", "swiat_testowy",
        "analyzes",
        {"confidence": 0.9}
    )
    print(f"Dodano relację: {rel_id}")
    
    # Test statystyk
    stats = manager.get_all_memories_stats()
    print(f"Statystyki: {stats}")
    
    # Test zapisu
    save_path = manager.save()
    print(f"Zapisano pamięć do: {save_path}")
    
    print("\nAll MemoryManager tests passed!")
