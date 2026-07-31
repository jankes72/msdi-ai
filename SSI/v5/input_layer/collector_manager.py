"""
SSI V5 - Input Layer - Collector Manager
Manager zarzadzajacy wszystkimi kolektorami danych

Odpowiedzialnosc:
- Rejestracja i zarzadzanie kolektorami
- Zbieranie danych ze wszystkich zrodel
- Agregacja danych w SSIKnowledgePackage
- Koordynacja procesu zbierania

Wersja: 1.0
Data: 2026-07-31
"""

import logging
from typing import Dict, List, Optional, Any, Type, TypeVar, Set
from datetime import datetime
from enum import Enum

from .data_models import DataSource, DataCategory, DataStatus
from .knowledge_package import SSIKnowledgePackage, create_knowledge_package
from .knowledge_metadata import KnowledgeMetadata, PackageStatus

logger = logging.getLogger(__name__)


class CollectorType(Enum):
    """Typy kolektorow"""
    V2 = "v2"            # Kolektor V2
    V3 = "v3"            # Kolektor V3
    V4 = "v4"            # Kolektor V4
    EXTERNAL = "external" # Kolektor zewnetrzny
    ALL = "all"          # Wszystkie kolektory


class CollectionStrategy(Enum):
    """Strategie zbierania danych"""
    SEQUENTIAL = "sequential"      # Kolejne (V2 -> V3 -> V4 -> External)
    PARALLEL = "parallel"          # Rownolegle (wszystkie naraz)
    PRIORITY = "priority"          # Według priorytetu
    CUSTOM = "custom"              # Niestandardowa kolejność


class CollectorStatus(Enum):
    """Status kolektora"""
    PENDING = "pending"       # Oczekuje
    READY = "ready"           # Gotowy
    COLLECTING = "collecting" # Zbiera dane
    COMPLETED = "completed"   # Zebranie zakonczone
    FAILED = "failed"         # Blad
    DISABLED = "disabled"     # Wylączony


T = TypeVar('T', bound='BaseCollector')


class CollectorInfo:
    """Informacje o zarejestrowanym kolektorze"""
    
    def __init__(
        self,
        collector_type: CollectorType,
        collector_class: Type,
        source_type: DataSource,
        name: str,
        priority: int = 0,
        is_enabled: bool = True
    ):
        self.collector_type = collector_type
        self.collector_class = collector_class
        self.source_type = source_type
        self.name = name
        self.priority = priority
        self.is_enabled = is_enabled
        self.instance: Optional[Any] = None
        self.status: CollectorStatus = CollectorStatus.PENDING
    
    def __repr__(self) -> str:
        return f"CollectorInfo({self.name}, {self.collector_type.value}, {self.status.value})"


class CollectionResult:
    """Wynik zebrania danych z kolektora"""
    
    def __init__(
        self,
        collector_type: CollectorType,
        source_type: DataSource,
        data: Any = None,
        success: bool = True,
        error: Optional[str] = None,
        items_collected: int = 0,
        collection_time: float = 0.0
    ):
        self.collector_type = collector_type
        self.source_type = source_type
        self.data = data
        self.success = success
        self.error = error
        self.items_collected = items_collected
        self.collection_time = collection_time
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "collector_type": self.collector_type.value,
            "source_type": self.source_type.name,
            "success": self.success,
            "error": self.error,
            "items_collected": self.items_collected,
            "collection_time": self.collection_time,
            "timestamp": self.timestamp.isoformat()
        }


class KnowledgeCollectorManager:
    """
    Glowny manager kolektorow wiedzy.
    
    Odpowiada za:
    - Rejestracje i zarzadzanie kolektorami
    - Zbieranie danych ze wszystkich lub wybranych zrodel
    - Agregacje danych w jeden pakiet wiedzy
    - monitorowanie statusu kolektorow
    
    Uzycie:
        manager = KnowledgeCollectorManager()
        
        # Rejestracja kolektorow
        manager.register_collector(V2DataCollector, DataSource.V2_MODELS)
        manager.register_collector(V3KnowledgeCollector, DataSource.V3_KNOWLEDGE)
        manager.register_collector(V4AgentsCollector, DataSource.V4_AGENTS)
        manager.register_collector(ExternalKnowledgeCollector, DataSource.AGENTS)
        
        # Zbieranie wszystkich danych
        package = manager.collect_all()
        
        # Zbieranie specyficznych zrodel
        package = manager.collect_specific([DataSource.V2_MODELS, DataSource.V3_KNOWLEDGE])
    """
    
    def __init__(self):
        """Inicjalizacja managera"""
        self._collectors: Dict[CollectorType, CollectorInfo] = {}
        self._initialized: bool = False
        self._status: CollectorStatus = CollectorStatus.PENDING
        
        # Rejestr zebran (do statystyk)
        self._collection_history: List[CollectionResult] = []
        
        # Ustawienia
        self._strategy: CollectionStrategy = CollectionStrategy.SEQUENTIAL
        self._collect_on_init: bool = False
        
        logger.info("KnowledgeCollectorManager zainicjowany")
    
    def initialize(self) -> bool:
        """
        Inicjalizuje managera i wszystkie zarejestrowane kolektory.
        
        Returns:
            True jeśli inicjalizacja sie powiodla
        """
        try:
            logger.info("Inicjalizacja KnowledgeCollectorManager...")
            
            # Inicjalizuj wszystkie zarejestrowane kolektory
            for collector_type, info in self._collectors.items():
                if info.is_enabled and collector_type != CollectorType.ALL:
                    info.instance = info.collector_class()
                    init_result = getattr(info.instance, 'initialize', lambda: True)()
                    
                    if init_result:
                        info.status = CollectorStatus.READY
                        logger.info(f"Kolektor {info.name} zainicjalizowany")
                    else:
                        info.status = CollectorStatus.FAILED
                        logger.error(f"Blad inicjalizacji kolektora {info.name}")
                        return False
            
            self._initialized = True
            self._status = CollectorStatus.READY
            logger.info("KnowledgeCollectorManager gotowy")
            return True
            
        except Exception as e:
            logger.error(f"Blad inicializacji KnowledgeCollectorManager: {e}")
            self._status = CollectorStatus.FAILED
            return False
    
    def is_initialized(self) -> bool:
        """Czy manager jest zainicjalizowany?"""
        return self._initialized
    
    def get_status(self) -> CollectorStatus:
        """Zwraca aktualny status managera"""
        return self._status
    
    # =========================================================================
    # REJESTRACJA KOLEKTOROW
    # =========================================================================
    
    def register_collector(
        self,
        collector_class: Type,
        source_type: DataSource,
        collector_type: CollectorType = None,
        name: str = None,
        priority: int = 0,
        is_enabled: bool = True
    ) -> CollectorType:
        """
        Rejestruje nowy kolektor.
        
        Args:
            collector_class: Klasa kolektora
            source_type: Typ zrodla (V2_MODELS, V3_KNOWLEDGE, V4_AGENTS, AGENTS)
            collector_type: Typ kolektora (opcjonalny, domyslnie odgadniety)
            name: Nazwa kolektora (opcjonalna)
            priority: Priorytet zebrania
            is_enabled: Czy kolektor jest wlaczony
            
        Returns:
            CollectorType przypisany do kolektora
        """
        if collector_type is None:
            # Odgadnij CollectorType na podstawie DataSource
            type_map = {
                DataSource.V2_MODELS: CollectorType.V2,
                DataSource.V3_KNOWLEDGE: CollectorType.V3,
                DataSource.V4_AGENTS: CollectorType.V4,
                DataSource.AGENTS: CollectorType.EXTERNAL,
                DataSource.LABORATORIES: CollectorType.EXTERNAL,
                DataSource.DEVELOPER: CollectorType.EXTERNAL,
                DataSource.SYSTEM: CollectorType.EXTERNAL
            }
            collector_type = type_map.get(source_type, CollectorType.CUSTOM)
        
        if name is None:
            name = collector_class.__name__
        
        info = CollectorInfo(
            collector_type=collector_type,
            collector_class=collector_class,
            source_type=source_type,
            name=name,
            priority=priority,
            is_enabled=is_enabled
        )
        
        self._collectors[collector_type] = info
        logger.info(f"Zarejestrowano kolektor: {name} ({collector_type.value})")
        
        return collector_type
    
    def register_v2_collector(self, collector_class: Type) -> CollectorType:
        """Rejestruje kolektor V2"""
        return self.register_collector(
            collector_class=collector_class,
            source_type=DataSource.V2_MODELS,
            collector_type=CollectorType.V2
        )
    
    def register_v3_collector(self, collector_class: Type) -> CollectorType:
        """Rejestruje kolektor V3"""
        return self.register_collector(
            collector_class=collector_class,
            source_type=DataSource.V3_KNOWLEDGE,
            collector_type=CollectorType.V3
        )
    
    def register_v4_collector(self, collector_class: Type) -> CollectorType:
        """Rejestruje kolektor V4"""
        return self.register_collector(
            collector_class=collector_class,
            source_type=DataSource.V4_AGENTS,
            collector_type=CollectorType.V4
        )
    
    def register_external_collector(self, collector_class: Type) -> CollectorType:
        """Rejestruje kolektor External"""
        return self.register_collector(
            collector_class=collector_class,
            source_type=DataSource.AGENTS,
            collector_type=CollectorType.EXTERNAL
        )
    
    def unregister_collector(self, collector_type: CollectorType) -> bool:
        """
        Rejestruje kolektor.
        
        Args:
            collector_type: Typ kolektora do usuniecia
            
        Returns:
            True jeśli usuniecie sie powiodlo
        """
        if collector_type in self._collectors:
            del self._collectors[collector_type]
            logger.info(f"Usunieto kolektor: {collector_type.value}")
            return True
        logger.warning(f"Kolektor {collector_type.value} nie istnieje")
        return False
    
    def get_collector(self, collector_type: CollectorType) -> Optional[Any]:
        """Zwraca instancje kolektora"""
        info = self._collectors.get(collector_type)
        if info and info.instance:
            return info.instance
        return None
    
    def get_collector_info(self, collector_type: CollectorType) -> Optional[CollectorInfo]:
        """Zwraca informacje o kolektorze"""
        return self._collectors.get(collector_type)
    
    def get_all_collectors(self) -> Dict[CollectorType, CollectorInfo]:
        """Zwraca wszystkie zarejestrowane kolektory"""
        return self._collectors.copy()
    
    def get_enabled_collectors(self) -> List[CollectorType]:
        """Zwraca Typy wlaczonych kolektorow"""
        return [
            ctype for ctype, info in self._collectors.items()
            if info.is_enabled
        ]
    
    def enable_collector(self, collector_type: CollectorType) -> None:
        """Wlacza kolektor"""
        if collector_type in self._collectors:
            self._collectors[collector_type].is_enabled = True
            logger.info(f"Wlaczono kolektor: {collector_type.value}")
    
    def disable_collector(self, collector_type: CollectorType) -> None:
        """Wylacza kolektor"""
        if collector_type in self._collectors:
            self._collectors[collector_type].is_enabled = False
            logger.info(f"Wylaczono kolektor: {collector_type.value}")
    
    # ========================================================================= maho
    # ZBIERANIE DANYCH
    # =========================================================================
    
    def collect_all(self) -> SSIKnowledgePackage:
        """
        Zbiera dane ze wszystkich zarejestrowanych kolektorow.
        
        Returns:
            SSIKnowledgePackage z zebranymi danymi
        """
        if not self._initialized:
            if not self.initialize():
                raise RuntimeError("Nie mozna zebrac danych - inicjalizacja nieudana")
        
        logger.info("Rozpoczynanie zebrania wszystkich danych...")
        self._status = CollectorStatus.COLLECTING
        
        package = create_knowledge_package()
        results: List[CollectionResult] = []
        
        # Zbieraj wg strategii
        if self._strategy == CollectionStrategy.SEQUENTIAL:
            results = self._collect_sequential()
        elif self._strategy == CollectionStrategy.PARALLEL:
            results = self._collect_parallel()
        else:
            results = self._collect_sequential()
        
        # Agreguj wyniki
        for result in results:
            if result.success and result.data:
                package.add_source_data(result.source_type, result.data)
                logger.info(f"Zebrano {result.items_collected} elementow z {result.source_type.name}")
            else:
                logger.error(f"Blad zebrania danych z {result.source_type.name}: {result.error}")
        
        # Waliduj pakiet
        package_Valid = package.validate()
        if package_Valid:
            self._status = CollectorStatus.COMPLETED
            logger.info("Zebranie wszystkich danych zakonczone sukcesem")
        else:
            self._status = CollectorStatus.FAILED
            logger.error("Walidacja pakietu nieudana")
        
        # Zapisz do historii
        self._collection_history.extend(results)
        
        return package
    
    def collect_specific(self, source_types: List[DataSource]) -> SSIKnowledgePackage:
        """
        Zbiera dane tylko z okreslonych typow zrodel.
        
        Args:
            source_types: Lista typow zrodel do zebrania
            
        Returns:
            SSIKnowledgePackage z zebranymi danymi
        """
        if not self._initialized:
            if not self.initialize():
                raise RuntimeError("Nie mozna zebrac danych - inicjalizacja nieudana")
        
        logger.info(f"Zbieranie danych z wybranych zrodel: {[st.name for st in source_types]}")
        self._status = CollectorStatus.COLLECTING
        
        package = create_knowledge_package()
        results: List[CollectionResult] = []
        
        for source_type in source_types:
            collector_type = self._get_collector_type_for_source(source_type)
            if collector_type and collector_type in self._collectors:
                result = self._collect_from_collector(collector_type)
                results.append(result)
                
                if result.success and result.data:
                    package.add_source_data(source_type, result.data)
        
        # Waliduj pakiet
        package_Valid = package.validate()
        self._status = CollectorStatus.COMPLETED if package_Valid else CollectorStatus.FAILED
        self._collection_history.extend(results)
        
        return package
    
    def _get_collector_type_for_source(self, source_type: DataSource) -> Optional[CollectorType]:
        """Mapuje DataSource na CollectorType"""
        mapping = {
            DataSource.V2_MODELS: CollectorType.V2,
            DataSource.V3_KNOWLEDGE: CollectorType.V3,
            DataSource.V4_AGENTS: CollectorType.V4,
            DataSource.AGENTS: CollectorType.EXTERNAL,
            DataSource.LABORATORIES: CollectorType.EXTERNAL,
            DataSource.DEVELOPER: CollectorType.EXTERNAL,
            DataSource.SYSTEM: CollectorType.EXTERNAL
        }
        return mapping.get(source_type)
    
    def _collect_sequential(self) -> List[CollectionResult]:
        """Zbiera dane sekwencyjnie"""
        results = []
        
        # Kolejnosc zebrania wg priorytetu
        sorted_collectors = sorted(
            self._collectors.items(),
            key=lambda x: x[1].priority,
            reverse=True
        )
        
        for collector_type, info in sorted_collectors:
            if info.is_enabled:
                result = self._collect_from_collector(collector_type)
                results.append(result)
        
        return results
    
    def _collect_parallel(self) -> List[CollectionResult]:
        """Zbiera dane rownolegle (z symulacja)"""
        # Na razie sekwencyjnie, w przyszosci z threading
        return self._collect_sequential()
    
    def _collect_from_collector(self, collector_type: CollectorType) -> CollectionResult:
        """Zbiera dane z pojedynczego kolektora"""
        import time
        
        info = self._collectors.get(collector_type)
        if not info or not info.instance:
            return CollectionResult(
                collector_type=collector_type,
                source_type=info.source_type if info else DataSource.V2_MODELS,
                success=False,
                error=f"Kolektor {collector_type.value} nie jest dostepny",
                items_collected=0,
                collection_time=0.0
            )
        
        start_time = time.time()
        
        try:
            # Wywolaj metode collect na kolektorze
            collect_method = getattr(info.instance, 'collect_all', None)
            if collect_method:
                data = collect_method()
                items = self._count_items(data, info.source_type)
            else:
                # Spróbuj z collect
                collect_method = getattr(info.instance, 'collect', None)
                if collect_method:
                    data = collect_method()
                    items = self._count_items(data, info.source_type)
                else:
                    data = None
                    items = 0
            
            collection_time = time.time() - start_time
            
            return CollectionResult(
                collector_type=collector_type,
                source_type=info.source_type,
                data=data,
                success=data is not None,
                error=None,
                items_collected=items,
                collection_time=collection_time
            )
            
        except Exception as e:
            collection_time = time.time() - start_time
            return CollectionResult(
                collector_type=collector_type,
                source_type=info.source_type,
                data=None,
                success=False,
                error=str(e),
                items_collected=0,
                collection_time=collection_time
            )
    
    def _count_items(self, data: Any, source_type: DataSource) -> int:
        """Liczy elementy w zebranych danych"""
        if source_type == DataSource.V2_MODELS:
            return len(getattr(data, 'models', [])) if data else 0
        elif source_type == DataSource.V3_KNOWLEDGE:
            return len(getattr(data, 'worlds', [])) if data else 0
        elif source_type == DataSource.V4_AGENTS:
            return len(getattr(data, 'agents', [])) if data else 0
        elif source_type in [DataSource.AGENTS, DataSource.LABORATORIES, DataSource.DEVELOPER, DataSource.SYSTEM]:
            # ExternalDataPackage
            if data:
                count = 0
                if hasattr(data, 'developer_data') and data.developer_data:
                    count += len(getattr(data.developer_data, 'commands', []))
                if hasattr(data, 'laboratory_data') and data.laboratory_data:
                    count += len(data.laboratory_data)
                if hasattr(data, 'agent_data') and data.agent_data:
                    count += len(data.agent_data)
                return count
            return 0
        return 0
    
    # =========================================================================
    # STATYSTYKI I MONITOROWANIE
    # =========================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Zwraca statystyki zebran"""
        total_collections = len(self._collection_history)
        successful_collections = sum(1 for r in self._collection_history if r.success)
        total_items = sum(r.items_collected for r in self._collection_history)
        total_time = sum(r.collection_time for r in self._collection_history)
        
        return {
            "total_collections": total_collections,
            "successful_collections": successful_collections,
            "total_items_collected": total_items,
            "total_collection_time": total_time,
            "registered_collectors": len(self._collectors),
            "enabled_collectors": len(self.get_enabled_collectors()),
            "status": self._status.value
        }
    
    def get_collection_history(self) -> List[CollectionResult]:
        """Zwraca historie zebran"""
        return self._collection_history.copy()
    
    def get_last_collection_result(self, collector_type: CollectorType) -> Optional[CollectionResult]:
        """Zwraca ostatni wynik zebrania dla kolektora"""
        for result in reversed(self._collection_history):
            if result.collector_type == collector_type:
                return result
        return None
    
    def clear_history(self) -> None:
        """Czyści historie zebran"""
        self._collection_history.clear()
        logger.info("Wyczyszczono historie zebran")
    
    # =========================================================================
    # KONFIGURACJA
    # =========================================================================
    
    def set_collection_strategy(self, strategy: CollectionStrategy) -> None:
        """Ustawia strategie zebrania"""
        self._strategy = strategy
        logger.info(f"Ustawiono strategie zebrania: {strategy.value}")
    
    def get_collection_strategy(self) -> CollectionStrategy:
        """Zwraca aktualna strategie zebrania"""
        return self._strategy
    
    def set_collect_on_init(self, collect: bool) -> None:
        """Ustawia czy zbierac dane automatycznie po inicjalizacji"""
        self._collect_on_init = collect
    
    # =========================================================================
    # METODY UZYTECZNE
    # =========================================================================
    
    def reset(self) -> None:
        """Resetuje manager i wszystkie kolektory"""
        self._status = CollectorStatus.PENDING
        self._collection_history.clear()
        
        for info in self._collectors.values():
            reset_method = getattr(info.instance, 'reset', None)
            if reset_method:
                reset_method()
            info.status = CollectorStatus.PENDING
        
        logger.info("KnowledgeCollectorManager zresetowany")
    
    def clear(self) -> None:
        """Czyści wszystkie zebrane dane"""
        self.reset()
        for info in self._collectors.values():
            clear_method = getattr(info.instance, 'clear_all', None)
            if clear_method:
                clear_method()
        logger.info("Wyczyszczono wszystkie dane")
    
    def display(self) -> None:
        """Wyswietla informacje o managerze"""
        print("=" * 60)
        print("KNOWLEDGE COLLECTOR MANAGER")
        print("=" * 60)
        print(f"Status: {self._status.value}")
        print(f"Zarejestrowane kolektory: {len(self._collectors)}")
        print(f"Strategia: {self._strategy.value}")
        print()
        
        for ctype, info in self._collectors.items():
            status = info.status.value if info.instance else "NOT_INITIALIZED"
            print(f"  {info.name} ({ctype.value}): {status}")
        
        print()
        stats = self.get_statistics()
        print("STATYSTYKI:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        print("=" * 60)


class GlobalCollectorManager:
    """
    Singletonowa wersja KnowledgeCollectorManager.
    Umożliwia globalny dostęp do managera kolektorów.
    """
    
    _instance: Optional[KnowledgeCollectorManager] = None
    
    @classmethod
    def get_instance(cls) -> KnowledgeCollectorManager:
        """Zwraca instancje singletona"""
        if cls._instance is None:
            cls._instance = KnowledgeCollectorManager()
            cls._instance._is_singleton = True
        return cls._instance
    
    @classmethod
    def register_all(cls) -> KnowledgeCollectorManager:
        """
        Rejestruje wszystkie dostepne kolektory i zwraca instancje.
        
        Uzycie:
            manager = GlobalCollectorManager.register_all()
        """
        manager = cls.get_instance()
        
        # Importuj kolektory (jesli dostepne)
        try:
            from .v2_collector import V2DataCollector
            manager.register_v2_collector(V2DataCollector)
        except ImportError:
            logger.warning("V2DataCollector niedostepny")
        
        try:
            from .v3_collector import V3KnowledgeCollector
            manager.register_v3_collector(V3KnowledgeCollector)
        except ImportError:
            logger.warning("V3KnowledgeCollector niedostepny")
        
        try:
            from .v4_collector import V4AgentsCollector
            manager.register_v4_collector(V4AgentsCollector)
        except ImportError:
            logger.warning("V4AgentsCollector niedostepny")
        
        try:
            from .external import ExternalKnowledgeCollector
            manager.register_external_collector(ExternalKnowledgeCollector)
        except ImportError:
            logger.warning("ExternalKnowledgeCollector niedostepny")
        
        return manager


# Alien globalna instancja (opcjonalne uzycie)
collector_manager: Optional[KnowledgeCollectorManager] = None


def get_collector_manager() -> KnowledgeCollectorManager:
    """Zwraca globalna instancje managera (lub tworzy nowa)"""
    global collector_manager
    if collector_manager is None:
        collector_manager = GlobalCollectorManager.get_instance()
    return collector_manager
