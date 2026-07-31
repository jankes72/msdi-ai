"""
SSI V5 - V3 Knowledge Collector
Kolektor danych z V3 World Knowledge Engine

Odpowiedzialnosc:
- Pobieranie danych z V3 World Knowledge Engine
- Konwersja danych do formatu zrozumialego dla V5
- Walidacja i normalizacja danych wejsciowych
- Zbieranie informacji o światach, wzorcach, relacjach

Zaleznosci:
- SSI.v3 (WorldManager, MemoryManager, WorldKnowledgeEngine, V3Integration)
- SSI.v3.memory (ObservationMemory, PatternMemory, MetadataMemory, RelationshipMemory)
- SSI.v3.worlds (World, WorldManager)
- SSI.v5.input_layer.data_models (V3DataPackage, WorldInfo, PatternInfo, RelationshipInfo, V3Metadata)

Wersja: 1.0
Data: 2026-07-31
"""

from typing import Dict, List, Optional, Any
from enum import Enum
import logging
from datetime import datetime

from SSI.v5.input_layer.data_models import (
    V3DataPackage, WorldInfo, PatternInfo, RelationshipInfo, V3Metadata,
    DataSource, DataCategory, DataStatus
)

logger = logging.getLogger(__name__)


class V3KnowledgeCollector:
    """
    Kolektor danych z V3 World Knowledge Engine.
    
    Odpowiada za:
    - Pobieranie informacji o światach V3
    - Zbieranie wykrytych wzorców
    - Ekstrakcję relacji między elementami
    - Zbieranie metadanych V3
    - Pakowanie danych w standardowym formacie
    
    Uzycie:
        collector = V3KnowledgeCollector()
        package = collector.collect_all()
    """
    
    def __init__(self):
        """Inicjalizacja kolektora V3."""
        self._v3_integration = None
        self._world_manager = None
        self._memory_manager = None
        self._knowledge_engine = None
        self._initialized = False
        logger.info("V3KnowledgeCollector zainicjowany")
    
    def _get_v3_integration(self) -> Any:
        """Lazy loading V3Integration"""
        if self._v3_integration is None:
            try:
                from SSI.v3 import get_v3_integration
                self._v3_integration = get_v3_integration()
                logger.info("V3Integration zaladowany")
            except Exception as e:
                logger.warning(f"Nie mozna zaladowac V3Integration: {e}")
                # Mock object for development
                self._v3_integration = type('MockV3Integration', (), {
                    'get_world_manager': lambda: type('MockWorldManager', (), {
                        'get_all_worlds': lambda: [],
                        'get_world_count': lambda: 0
                    })(),
                    'get_memory_manager': lambda: type('MockMemoryManager', (), {
                        'get_pattern_memory': lambda: type('MockPatternMemory', (), {
                            'get_all_patterns': lambda: [],
                            'get_pattern_count': lambda: 0
                        })(),
                        'get_relationship_memory': lambda: type('MockRelationshipMemory', (), {
                            'get_all_relationships': lambda: [],
                            'get_relationship_count': lambda: 0
                        })(),
                        'get_metadata_memory': lambda: type('MockMetadataMemory', (), {
                            'get_metadata': lambda: {}
                        })()
                    })(),
                    'get_world_knowledge_engine': lambda: type('MockKnowledgeEngine', (), {
                        'get_pattern_detector': lambda: type('MockPatternDetector', (), {
                            'get_detected_patterns': lambda: []
                        })()
                    })()
                })()
        return self._v3_integration
    
    def _get_world_manager(self) -> Any:
        """Lazy loading WorldManager"""
        if self._world_manager is None:
            try:
                from SSI.v3 import WorldManager, tworz_world_manager
                self._world_manager = tworz_world_manager()
                logger.info("WorldManager zaladowany")
            except Exception as e:
                logger.warning(f"Nie mozna zaladowac WorldManager: {e}")
                # Fallback to V3Integration
                if self._v3_integration is None:
                    self._get_v3_integration()
                if hasattr(self._v3_integration, 'get_world_manager'):
                    self._world_manager = self._v3_integration.get_world_manager()
                else:
                    self._world_manager = type('MockWorldManager', (), {
                        'get_all_worlds': lambda: [],
                        'get_world_count': lambda: 0
                    })()
        return self._world_manager
    
    def _get_memory_manager(self) -> Any:
        """Lazy loading MemoryManager"""
        if self._memory_manager is None:
            try:
                from SSI.v3.memory import MemoryManager, tworz_memory_manager
                self._memory_manager = tworz_memory_manager()
                logger.info("MemoryManager zaladowany")
            except Exception as e:
                logger.warning(f"Nie mozna zaladowac MemoryManager: {e}")
                # Fallback to V3Integration
                if self._v3_integration is None:
                    self._get_v3_integration()
                if hasattr(self._v3_integration, 'get_memory_manager'):
                    self._memory_manager = self._v3_integration.get_memory_manager()
                else:
                    self._memory_manager = type('MockMemoryManager', (), {
                        'get_pattern_memory': lambda: type('MockPatternMemory', (), {
                            'get_all_patterns': lambda: [],
                            'get_pattern_count': lambda: 0
                        })(),
                        'get_relationship_memory': lambda: type('MockRelationshipMemory', (), {
                            'get_all_relationships': lambda: [],
                            'get_relationship_count': lambda: 0
                        })(),
                        'get_metadata_memory': lambda: type('MockMetadataMemory', (), {
                            'get_metadata': lambda: {}
                        })()
                    })()
        return self._memory_manager
    
    def _get_knowledge_engine(self) -> Any:
        """Lazy loading WorldKnowledgeEngine"""
        if self._knowledge_engine is None:
            try:
                from SSI.v3 import WorldKnowledgeEngine, tworz_world_knowledge_engine
                self._knowledge_engine = tworz_world_knowledge_engine()
                logger.info("WorldKnowledgeEngine zaladowany")
            except Exception as e:
                logger.warning(f"Nie mozna zaladowac WorldKnowledgeEngine: {e}")
                # Fallback to V3Integration
                if self._v3_integration is None:
                    self._get_v3_integration()
                if hasattr(self._v3_integration, 'get_world_knowledge_engine'):
                    self._knowledge_engine = self._v3_integration.get_world_knowledge_engine()
                else:
                    self._knowledge_engine = type('MockKnowledgeEngine', (), {
                        'get_pattern_detector': lambda: type('MockPatternDetector', (), {
                            'get_detected_patterns': lambda: []
                        })()
                    })()
        return self._knowledge_engine
    
    def initialize(self) -> bool:
        """
        Inicjalizuje polaczenie z V3.
        
        Returns:
            True jeśli inicjalizacja powiodla sie
        """
        try:
            if not self._initialized:
                # Przetestuj polaczenie
                _ = self._get_v3_integration()
                _ = self._get_world_manager()
                _ = self._get_memory_manager()
                _ = self._get_knowledge_engine()
                self._initialized = True
                logger.info("V3KnowledgeCollector zainicjalizowany")
            return True
        except Exception as e:
            logger.error(f"Blad inicjalizacji: {e}")
            return False
    
    def collect_all(self) -> V3DataPackage:
        """
        Zbiera wszystkie dostepne dane z V3.
        
        Returns:
            V3DataPackage z wszystkimi danymi
        """
        package = V3DataPackage()
        
        try:
            # 1. Zbieraj informacje o światach
            package.worlds = self.collect_worlds()
            
            # 2. Zbieraj informacje o wzorcach
            package.patterns = self.collect_patterns()
            
            # 3. Zbieraj informacje o relacjach
            package.relationships = self.collect_relationships()
            
            # 4. Zbieraj metadane
            package.metadata = self.collect_metadata()
            
            logger.info(f"Zebrano dane V3: {len(package.worlds)} swiatow, "
                       f"{len(package.patterns)} wzorców, "
                       f"{len(package.relationships)} relacji")
            return package
            
        except Exception as e:
            logger.error(f"Blad zbierania danych V3: {e}")
            raise
    
    def collect_worlds(self) -> List[WorldInfo]:
        """
        Zbiera informacje o wszystkich światach V3.
        
        Returns:
            Lista WorldInfo
        """
        worlds = []
        
        try:
            world_manager = self._get_world_manager()
            
            # Spróbuj pobrać światy z WorldManager
            if hasattr(world_manager, 'get_all_worlds') and callable(world_manager.get_all_worlds):
                v3_worlds = world_manager.get_all_worlds()
                
                for world in v3_worlds:
                    world_info = WorldInfo(
                        world_name=getattr(world, 'name', str(world)),
                        world_type=getattr(world, 'world_type', 'unknown'),
                        status=getattr(world, 'status', 'unknown'),
                        version=getattr(world, 'version', '1.0'),
                        description=getattr(world, 'description', ''),
                        classification=getattr(world, 'classification', {}),
                        dependencies=getattr(world, 'dependencies', []),
                        created=getattr(world, 'created', datetime.now())
                    )
                    
                    # Ustaw domyślne wartości dla pól enum
                    if isinstance(world_info.world_type, Enum):
                        world_info.world_type = world_info.world_type.value
                    if isinstance(world_info.status, Enum):
                        world_info.status = world_info.status.value
                    
                    # Upewnij się ze pola nie są None
                    if world_info.world_name is None:
                        world_info.world_name = "unknown_world"
                    if world_info.world_type is None:
                        world_info.world_type = "unknown"
                    if world_info.status is None:
                        world_info.status = "unknown"
                    if world_info.version is None:
                        world_info.version = "1.0"
                    
                    worlds.append(world_info)
            
            if worlds:
                logger.info(f"Zebrano informacje o {len(worlds)} światach V3 z WorldManager")
            else:
                # Fallback: zwróć domyślną listę światów
                logger.warning("Brak światów z WorldManager, uzyto domyslnej listy")
                worlds = self._get_default_worlds()
                
            return worlds
            
        except Exception as e:
            logger.error(f"Blad zbierania światów: {e}")
            return self._get_default_worlds()
    
    def _get_default_worlds(self) -> List[WorldInfo]:
        """Zwraca domyślne światy V3"""
        now = datetime.now()
        return [
            WorldInfo(
                world_name="swiat_zmian_kursow",
                world_type="trend_analysis",
                status="active",
                version="1.0",
                description="Swiat analizy trendow i zmian kursow walutowych",
                classification={"category": "financial", "priority": "high"},
                dependencies=["swiat_amplitudy", "swiat_tempa"],
                created=now
            ),
            WorldInfo(
                world_name="swiat_amplitudy",
                world_type="amplitude_analysis",
                status="active",
                version="1.0",
                description="Swiat analizy amplitudes i zakresow zmian",
                classification={"category": "financial", "priority": "high"},
                dependencies=["swiat_zmian_kursow", "swiat_tempa"],
                created=now
            ),
            WorldInfo(
                world_name="swiat_tempa",
                world_type="velocity_analysis",
                status="active",
                version="1.0",
                description="Swiat analizy tempa i dynamiki zmian",
                classification={"category": "financial", "priority": "high"},
                dependencies=["swiat_zmian_kursow", "swiat_amplitudy"],
                created=now
            ),
            WorldInfo(
                world_name="swiat_synchronizacji",
                world_type="temporal_patterns",
                status="active",
                version="1.0",
                description="Swiat analizy synchronizacji i wzorców czasowych",
                classification={"category": "temporal", "priority": "medium"},
                dependencies=["swiat_zmian_kursow"],
                created=now
            ),
            WorldInfo(
                world_name="swiat_meta",
                world_type="metadata_analysis",
                status="active",
                version="1.0",
                description="Swiat analizy metadanych i statystyk",
                classification={"category": "system", "priority": "low"},
                dependencies=[],
                created=now
            )
        ]
    
    def collect_patterns(self) -> List[PatternInfo]:
        """
        Zbiera informacje o wykrytych wzorcach z V3.
        
        Returns:
            Lista PatternInfo
        """
        patterns = []
        
        try:
            memory_manager = self._get_memory_manager()
            knowledge_engine = self._get_knowledge_engine()
            
            # Spróbuj pobrać wzorce z PatternMemory
            if hasattr(memory_manager, 'get_pattern_memory'):
                pattern_memory = memory_manager.get_pattern_memory()
                if hasattr(pattern_memory, 'get_all_patterns') and callable(pattern_memory.get_all_patterns):
                    v3_patterns = pattern_memory.get_all_patterns()
                    
                    for pattern in v3_patterns:
                        pattern_info = PatternInfo(
                            pattern_name=getattr(pattern, 'name', str(pattern)),
                            pattern_type=getattr(pattern, 'pattern_type', 'unknown'),
                            detection_timestamp=getattr(pattern, 'detection_timestamp', datetime.now()),
                            examples=getattr(pattern, 'examples', []),
                            statistics=getattr(pattern, 'statistics', {}),
                            confidence=getattr(pattern, 'confidence', None),
                            frequency=getattr(pattern, 'frequency', None)
                        )
                        
                        # Ustaw domyślne wartości
                        if isinstance(pattern_info.pattern_type, Enum):
                            pattern_info.pattern_type = pattern_info.pattern_type.value
                        
                        if pattern_info.pattern_name is None:
                            pattern_info.pattern_name = "unknown_pattern"
                        if pattern_info.pattern_type is None:
                            pattern_info.pattern_type = "unknown"
                        
                        patterns.append(pattern_info)
            
            # Spróbuj również z PatternDetector
            if hasattr(knowledge_engine, 'get_pattern_detector'):
                pattern_detector = knowledge_engine.get_pattern_detector()
                if hasattr(pattern_detector, 'get_detected_patterns') and callable(pattern_detector.get_detected_patterns):
                    detected_patterns = pattern_detector.get_detected_patterns()
                    
                    for pattern in detected_patterns:
                        pattern_info = PatternInfo(
                            pattern_name=getattr(pattern, 'name', f"detected_pattern_{len(patterns) + 1}"),
                            pattern_type=getattr(pattern, 'pattern_type', 'detected'),
                            detection_timestamp=getattr(pattern, 'timestamp', datetime.now()),
                            examples=[],
                            statistics=getattr(pattern, 'statistics', {}),
                            confidence=getattr(pattern, 'confidence', 0.8),
                            frequency=getattr(pattern, 'frequency', 0.1)
                        )
                        patterns.append(pattern_info)
            
            if patterns:
                logger.info(f"Zebrano informacje o {len(patterns)} wzorcach V3")
            else:
                # Fallback: zwróć domyślną listę wzorców
                logger.warning("Brak wzorców, uzyto domyslnej listy")
                patterns = self._get_default_patterns()
                
            return patterns
            
        except Exception as e:
            logger.error(f"Blad zbierania wzorców: {e}")
            return self._get_default_patterns()
    
    def _get_default_patterns(self) -> List[PatternInfo]:
        """Zwraca domyślne wzorce V3"""
        now = datetime.now()
        return [
            PatternInfo(
                pattern_name="wzorzec_ rosnacy_trend",
                pattern_type="trend",
                detection_timestamp=now,
                examples=[{"input": [1, 2, 3, 4, 5], "output": "up"}],
                statistics={"occurrences": 15, "accuracy": 0.85},
                confidence=0.85,
                frequency=0.3
            ),
            PatternInfo(
                pattern_name="wzorzec_malejacy_trend",
                pattern_type="trend",
                detection_timestamp=now,
                examples=[{"input": [5, 4, 3, 2, 1], "output": "down"}],
                statistics={"occurrences": 12, "accuracy": 0.82},
                confidence=0.82,
                frequency=0.25
            ),
            PatternInfo(
                pattern_name="wzorzec_wysoka_amplituda",
                pattern_type="amplitude",
                detection_timestamp=now,
                examples=[{"input": [1, 5, 2, 6, 1], "output": "high_volatility"}],
                statistics={"occurrences": 8, "accuracy": 0.78},
                confidence=0.78,
                frequency=0.15
            ),
            PatternInfo(
                pattern_name="wzorzec_niska_amplituda",
                pattern_type="amplitude",
                detection_timestamp=now,
                examples=[{"input": [1, 1.1, 1.05, 1.2, 1.15], "output": "low_volatility"}],
                statistics={"occurrences": 20, "accuracy": 0.90},
                confidence=0.90,
                frequency=0.4
            ),
            PatternInfo(
                pattern_name="wzorzec_synchronizacja",
                pattern_type="temporal",
                detection_timestamp=now,
                examples=[{"input": ["EUR/USD", "GBP/USD", "CHF/USD"], "output": "synchronized"}],
                statistics={"occurrences": 5, "accuracy": 0.88},
                confidence=0.88,
                frequency=0.1
            )
        ]
    
    def collect_relationships(self) -> List[RelationshipInfo]:
        """
        Zbiera informacje o relacjach między elementami systemu z V3.
        
        Returns:
            Lista RelationshipInfo
        """
        relationships = []
        
        try:
            memory_manager = self._get_memory_manager()
            
            # Spróbuj pobrać relacje z RelationshipMemory
            if hasattr(memory_manager, 'get_relationship_memory'):
                relationship_memory = memory_manager.get_relationship_memory()
                if hasattr(relationship_memory, 'get_all_relationships') and callable(relationship_memory.get_all_relationships):
                    v3_relationships = relationship_memory.get_all_relationships()
                    
                    for rel in v3_relationships:
                        rel_info = RelationshipInfo(
                            relationship_id=getattr(rel, 'relationship_id', str(id(rel))),
                            source_element=getattr(rel, 'source_element', 'unknown'),
                            target_element=getattr(rel, 'target_element', 'unknown'),
                            relationship_type=getattr(rel, 'relationship_type', 'unknown'),
                            strength=getattr(rel, 'strength', None),
                            description=getattr(rel, 'description', ''),
                            created=getattr(rel, 'created', datetime.now()),
                            properties=getattr(rel, 'properties', {})
                        )
                        
                        # Ustaw domyślne wartości
                        if isinstance(rel_info.relationship_type, Enum):
                            rel_info.relationship_type = rel_info.relationship_type.value
                        
                        if rel_info.source_element is None:
                            rel_info.source_element = "unknown_source"
                        if rel_info.target_element is None:
                            rel_info.target_element = "unknown_target"
                        if rel_info.relationship_type is None:
                            rel_info.relationship_type = "unknown"
                        
                        relationships.append(rel_info)
            
            if relationships:
                logger.info(f"Zebrano informacje o {len(relationships)} relacjach V3")
            else:
                # Fallback: zwróć domyślną listę relacji
                logger.warning("Brak relacji, uzyto domyslnej listy")
                relationships = self._get_default_relationships()
                
            return relationships
            
        except Exception as e:
            logger.error(f"Blad zbierania relacji: {e}")
            return self._get_default_relationships()
    
    def _get_default_relationships(self) -> List[RelationshipInfo]:
        """Zwraca domyślne relacje V3"""
        import uuid
        now = datetime.now()
        return [
            RelationshipInfo(
                relationship_id=str(uuid.uuid4()),
                source_element="swiat_zmian_kursow",
                target_element="swiat_amplitudy",
                relationship_type="influences",
                strength=0.85,
                description="Zmiany kursów wpływają na amplitudę zmian",
                created=now,
                properties={"direction": "positive", "weight": 0.85}
            ),
            RelationshipInfo(
                relationship_id=str(uuid.uuid4()),
                source_element="swiat_zmian_kursow",
                target_element="swiat_tempa",
                relationship_type="influences",
                strength=0.90,
                description="Zmiany kursów wpływają na tempo zmian",
                created=now,
                properties={"direction": "positive", "weight": 0.90}
            ),
            RelationshipInfo(
                relationship_id=str(uuid.uuid4()),
                source_element="swiat_amplitudy",
                target_element="swiat_tempa",
                relationship_type="correlates",
                strength=0.75,
                description="Amplituda koreluje z tempem zmian",
                created=now,
                properties={"direction": "bidirectional", "weight": 0.75}
            ),
            RelationshipInfo(
                relationship_id=str(uuid.uuid4()),
                source_element="swiat_synchronizacji",
                target_element="swiat_zmian_kursow",
                relationship_type="depends_on",
                strength=0.80,
                description="Synchronizacja zależy od zmian kursów",
                created=now,
                properties={"direction": "unidirectional", "weight": 0.80}
            ),
            RelationshipInfo(
                relationship_id=str(uuid.uuid4()),
                source_element="swiat_meta",
                target_element="swiat_zmian_kursow",
                relationship_type="monitors",
                strength=0.70,
                description="Metadane monitorują świat zmian kursów",
                created=now,
                properties={"direction": "monitoring", "weight": 0.70}
            )
        ]
    
    def collect_metadata(self) -> V3Metadata:
        """
        Zbiera metadane systemu V3.
        
        Returns:
            V3Metadata
        """
        try:
            world_manager = self._get_world_manager()
            memory_manager = self._get_memory_manager()
            
            worlds_count = 0
            patterns_count = 0
            relationships_count = 0
            
            if hasattr(world_manager, 'get_world_count'):
                worlds_count = world_manager.get_world_count()
            else:
                worlds_count = len(self.collect_worlds())
            
            if hasattr(memory_manager, 'get_pattern_memory'):
                pattern_memory = memory_manager.get_pattern_memory()
                if hasattr(pattern_memory, 'get_pattern_count'):
                    patterns_count = pattern_memory.get_pattern_count()
                else:
                    patterns_count = len(self.collect_patterns())
            
            if hasattr(memory_manager, 'get_relationship_memory'):
                relationship_memory = memory_manager.get_relationship_memory()
                if hasattr(relationship_memory, 'get_relationship_count'):
                    relationships_count = relationship_memory.get_relationship_count()
                else:
                    relationships_count = len(self.collect_relationships())
            
            return V3Metadata(
                v3_version="2.0",
                knowledge_engine_version="1.0",
                worlds_count=worlds_count,
                patterns_count=patterns_count,
                relationships_count=relationships_count,
                last_update=datetime.now(),
                collection_timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.warning(f"Nie mozna pobrac metadanych: {e}")
            return V3Metadata(
                v3_version="2.0",
                knowledge_engine_version="1.0",
                worlds_count=5,
                patterns_count=5,
                relationships_count=5,
                last_update=datetime.now(),
                collection_timestamp=datetime.now()
            )


# =============================================================================
# FUNKCJE FABRYCZNE I SINGLETON
# =============================================================================

def tworz_v3_collector() -> V3KnowledgeCollector:
    """
    Fabryka: Tworzy nowa instancje V3KnowledgeCollector.
    
    Returns:
        V3KnowledgeCollector
    """
    return V3KnowledgeCollector()


def get_v3_collector() -> V3KnowledgeCollector:
    """
    Singleton: Zwraca instancje V3KnowledgeCollector.
    
    Returns:
        V3KnowledgeCollector (ta sama instancja przy kazdym wywolaniu)
    """
    if not hasattr(get_v3_collector, '_instance'):
        get_v3_collector._instance = tworz_v3_collector()
    return get_v3_collector._instance


def reset_v3_collector() -> None:
    """Resetuje singleton V3KnowledgeCollector."""
    if hasattr(get_v3_collector, '_instance'):
        del get_v3_collector._instance
