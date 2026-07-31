"""
SSI V5 - Input Layer - Collector Registry
Rejestr kolektorow danych (Factory + Registry Pattern)

Odpowiedzialnosc:
- Automatyczne odkrywanie kolektorow
- Rejestracja kolektorow w centralnym rejestrze
- Tworzenie instancji kolektorow
- Zarzadzanie zyciem kolektorow

Wersja: 1.0
Data: 2026-07-31
"""

import logging
import importlib
import pkgutil
from typing import Dict, List, Optional, Any, Type, TypeVar, Callable
from dataclasses import dataclass
from enum import Enum

from .data_models import DataSource, DataCategory, DataStatus
from .collector_manager import CollectorType, KnowledgeCollectorManager
from .knowledge_package import SSIKnowledgePackage

logger = logging.getLogger(__name__)


class RegistryStatus(Enum):
    """Status rejestru"""
    PENDING = "pending"       # Oczekuje na skanowanie
    SCANNING = "scanning"     # Trwa skanowanie
    READY = "ready"           # Gotowy
    FAILED = "failed"         # Blad


@dataclass
class CollectorRegistration:
    """Informacje o zarejestrowanym kolektorze"""
    name: str
    module_path: str
    class_name: str
    collector_type: CollectorType
    source_type: DataSource
    class_reference: Optional[Type] = None
    priority: int = 0
    is_enabled: bool = True
    
    def get_class(self) -> Optional[Type]:
        """Zwraca referencje do klasy"""
        return self.class_reference
    
    def __repr__(self) -> str:
        return f"CollectorRegistration({self.name}, {self.collector_type.value}, {self.source_type.name})"


class CollectorRegistry:
    """
    Rejestr kolektorow danych.
    
    Odpowiada za:
    - Automatyczne odkrywanie kolektorow w pakiecie
    - Rejestracje kolektorow programowo
    - Zarzadzanie dostepnymi kolektorami
    - Integracje z KnowledgeCollectorManager
    
    Uzycie:
        registry = CollectorRegistry()
        
        # Automatyczne odkrywanie
        registry.auto_discover()
        
        # Manualna rejestracja
        registry.register(V2DataCollector, CollectorType.V2, SourceType.V2)
        
        # Pobieranie informacji
        collectors = registry.get_registered_collectors()
        v2_collector = registry.get_collector(CollectorType.V2)
        
        # Integracja z managerem
        manager = registry.create_manager()
    """
    
    def __init__(self):
        """Inicjalizacja rejestru"""
        self._registry: Dict[CollectorType, CollectorRegistration] = {}
        self._module_cache: Dict[str, Any] = {}
        self._status: RegistryStatus = RegistryStatus.PENDING
        self._discovered: bool = False
        
        logger.info("CollectorRegistry zainicjowany")
    
    def get_status(self) -> RegistryStatus:
        """Zwraca aktualny status rejestru"""
        return self._status
    
    def is_discovered(self) -> bool:
        """Czy rejestr zostal juz przeskanowany?"""
        return self._discovered
    
    # =========================================================================
    # AUTOMATYCZNE ODKRYWANIE
    # =========================================================================
    
    def auto_discover(self, package_name: str = "SSI.v5.input_layer") -> int:
        """
        Automatycznie odkrywa i rejestruje kolektory w podanym pakiecie.
        
        Args:
            package_name: Nazwa pakietu do przeszukania
            
        Returns:
            Liczba znalezionych kolektorow
        """
        self._status = RegistryStatus.SCANNING
        logger.info(f"Skanowanie pakietu {package_name} w poszukiwaniu kolektorow...")
        
        count = 0
        
        try:
            # Importuj pakiet
            package = importlib.import_module(package_name)
            
            # Przeszukaj wszystkie moduly w pakiecie
            for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
                if not is_pkg:  # Pomijamy pakiety
                    full_module_name = f"{package.__name__}.{module_name}"
                    
                    # Spróbuj zaimportowac modul
                    try:
                        module = importlib.import_module(full_module_name)
                        self._module_cache[full_module_name] = module
                        
                        # Szukaj klas kolektorow
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            
                            # Sprawdz czy to klasa i czy jest kolektorem
                            if (isinstance(attr, type) and 
                                not attr_name.startswith('_') and
                                self._is_collector_class(attr)):
                                
                                # Zarejestruj kolektor
                                collector_type = self._determine_collector_type(attr_name)
                                source_type = self._determine_source_type(attr_name)
                                
                                if collector_type and source_type:
                                    self.register(
                                        collector_class=attr,
                                        collector_type=collector_type,
                                        source_type=source_type,
                                        module_path=full_module_name,
                                        class_name=attr_name
                                    )
                                    count += 1
                                    logger.info(f"Odkryto kolektor: {attr_name} w {full_module_name}")
                        
                    except ImportError as e:
                        logger.warning(f"Nie mozna zaimportowac {full_module_name}: {e}")
                        continue
            
            self._discovered = True
            self._status = RegistryStatus.READY
            logger.info(f"Odkryto {count} kolektorow w pakiecie {package_name}")
            
        except Exception as e:
            logger.error(f"Blad podczas skanowania pakietu: {e}")
            self._status = RegistryStatus.FAILED
        
        return count
    
    def _is_collector_class(self, cls: Type) -> bool:
        """Sprawdza czy klasa jest kolektorem"""
        # Sprawdz czy ma metode collect lub collect_all
        required_methods = ['collect', 'collect_all', 'initialize']
        return any(hasattr(cls, method) for method in required_methods)
    
    def _determine_collector_type(self, class_name: str) -> Optional[CollectorType]:
        """Określa Typ kolektora na podstawie nazwy klasy"""
        mapping = {
            "v2": CollectorType.V2,
            "V2": CollectorType.V2,
            "v3": CollectorType.V3,
            "V3": CollectorType.V3,
            "v4": CollectorType.V4,
            "V4": CollectorType.V4,
            "external": CollectorType.EXTERNAL,
            "External": CollectorType.EXTERNAL,
            "collector": None,
            "Collector": None
        }
        
        class_lower = class_name.lower()
        for pattern, collector_type in mapping.items():
            if pattern in class_lower and collector_type:
                return collector_type
        
        # Jeśli nazwa klasy kończy się na DataCollector
        if class_lower.endswith("datacollector"):
            # Wyciagnij prefiks (V2, V3, V4, External)
            prefix = class_name[:-12]  # Usun "DataCollector"
            return mapping.get(prefix, CollectorType.CUSTOM)
        
        return None
    
    def _determine_source_type(self, class_name: str) -> Optional[DataSource]:
        """Określa Typ zrodla na podstawie nazwy klasy"""
        mapping = {
            "v2": DataSource.V2_MODELS,
            "V2": DataSource.V2_MODELS,
            "v3": DataSource.V3_KNOWLEDGE,
            "V3": DataSource.V3_KNOWLEDGE,
            "v4": DataSource.V4_AGENTS,
            "V4": DataSource.V4_AGENTS,
            "external": DataSource.AGENTS,
            "External": DataSource.AGENTS
        }
        
        class_lower = class_name.lower()
        for pattern, source_type in mapping.items():
            if pattern in class_lower:
                return source_type
        
        return None
    
    # =========================================================================
    # REJESTRACJA RECZNA
    # =========================================================================
    
    def register(
        self,
        collector_class: Type,
        collector_type: CollectorType,
        source_type: DataSource,
        module_path: str = "",
        class_name: str = "",
        priority: int = 0,
        is_enabled: bool = True
    ) -> CollectorType:
        """
        Rejestruje kolektor recznie.
        
        Args:
            collector_class: Klasa kolektora
            collector_type: Typ kolektora
            source_type: Typ zrodla (DataSource enum)
            module_path: Sciezka do modulu
            class_name: Nazwa klasy
            priority: Priorytet
            is_enabled: Czy wlaczony
            
        Returns:
            CollectorType
        """
        name = class_name or collector_class.__name__
        
        registration = CollectorRegistration(
            name=name,
            module_path=module_path,
            class_name=class_name or collector_class.__name__,
            collector_type=collector_type,
            source_type=source_type,
            class_reference=collector_class,
            priority=priority,
            is_enabled=is_enabled
        )
        
        self._registry[collector_type] = registration
        logger.info(f"Zarejestrowano kolektor: {name} ({collector_type.value})")
        
        return collector_type
    
    def register_v2(self, collector_class: Type) -> CollectorType:
        """Rejestruje kolektor V2"""
        return self.register(
            collector_class=collector_class,
            collector_type=CollectorType.V2,
            source_type=DataSource.V2_MODELS
        )
    
    def register_v3(self, collector_class: Type) -> CollectorType:
        """Rejestruje kolektor V3"""
        return self.register(
            collector_class=collector_class,
            collector_type=CollectorType.V3,
            source_type=DataSource.V3_KNOWLEDGE
        )
    
    def register_v4(self, collector_class: Type) -> CollectorType:
        """Rejestruje kolektor V4"""
        return self.register(
            collector_class=collector_class,
            collector_type=CollectorType.V4,
            source_type=DataSource.V4_AGENTS
        )
    
    def register_external(self, collector_class: Type) -> CollectorType:
        """Rejestruje kolektor External"""
        return self.register(
            collector_class=collector_class,
            collector_type=CollectorType.EXTERNAL,
            source_type=DataSource.AGENTS
        )
    
    def unregister(self, collector_type: CollectorType) -> bool:
        """Us Front kolektor z rejestru"""
        if collector_type in self._registry:
            del self._registry[collector_type]
            logger.info(f"Usunieto kolektor z rejestru: {collector_type.value}")
            return True
        return False
    
    # =========================================================================
    # DOSTEP DO KOLEKTOROW
    # =========================================================================
    
    def get_collector(self, collector_type: CollectorType) -> Optional[Type]:
        """Zwraca klase kolektora"""
        registration = self._registry.get(collector_type)
        if registration:
            return registration.get_class()
        return None
    
    def get_registration(self, collector_type: CollectorType) -> Optional[CollectorRegistration]:
        """Zwraca rejestracje kolektora"""
        return self._registry.get(collector_type)
    
    def get_all_collectors(self) -> Dict[CollectorType, CollectorRegistration]:
        """Zwraca wszystkie zarejestrowane kolektory"""
        return self._registry.copy()
    
    def get_collector_types(self) -> List[CollectorType]:
        """Zwraca liste typow kolektorow"""
        return list(self._registry.keys())
    
    def has_collector(self, collector_type: CollectorType) -> bool:
        """Czy kolektor jest zarejestrowany?"""
        return collector_type in self._registry
    
    def get_source_type(self, collector_type: CollectorType) -> Optional[DataSource]:
        """Zwraca typ zrodla dla kolektora"""
        registration = self._registry.get(collector_type)
        if registration:
            return registration.source_type
        return None
    
    def get_collector_for_source(self, source_type: DataSource) -> Optional[Type]:
        """Zwraca klase kolektora dla zrodla"""
        for registration in self._registry.values():
            if registration.source_type == source_type:
                return registration.get_class()
        return None
    
    # =========================================================================
    # INTEGRACJA Z MANAGEREM
    # =========================================================================
    
    def create_manager(self) -> KnowledgeCollectorManager:
        """
        Tworzy KnowledgeCollectorManager z zarejestrowanymi kolektorami.
        
        Returns:
            Zainicjalizowany KnowledgeCollectorManager
        """
        manager = KnowledgeCollectorManager()
        
        for collector_type, registration in self._registry.items():
            if registration.is_enabled and registration.class_reference:
                manager.register_collector(
                    collector_class=registration.class_reference,
                    source_type=registration.source_type,
                    collector_type=collector_type,
                    name=registration.name,
                    priority=registration.priority,
                    is_enabled=registration.is_enabled
                )
                logger.info(f"Zarejestrowano {registration.name} w managerze")
        
        return manager
    
    def create_manager_and_collect(self) -> SSIKnowledgePackage:
        """
        Tworzy managera, rejestruje kolektory i zbiera dane.
        
        Returns:
            SSIKnowledgePackage z zebranymi danymi
        """
        manager = self.create_manager()
        if manager.initialize():
            return manager.collect_all()
        else:
            raise RuntimeError("Nie mozna zainicjalizowac managera")
    
    # =========================================================================
    # TWORZENIE INSTANCJI
    # =========================================================================
    
    def create_instance(self, collector_type: CollectorType, *args, **kwargs) -> Any:
        """
        Tworzy instancje kolektora.
        
        Args:
            collector_type: Typ kolektora
            *args: Argumenty dla konstruktora
            **kwargs: Argumenty klucz-wartosc
            
        Returns:
            Instancja kolektora
        """
        cls = self.get_collector(collector_type)
        if cls:
            instance = cls(*args, **kwargs)
            logger.info(f"Utworzono instancje kolektora: {collector_type.value}")
            return instance
        raise ValueError(f"Kolektor {collector_type.value} nie jest zarejestrowany")
    
    def create_v2_instance(self, *args, **kwargs) -> Any:
        """Tworzy instancje kolektora V2"""
        return self.create_instance(CollectorType.V2, *args, **kwargs)
    
    def create_v3_instance(self, *args, **kwargs) -> Any:
        """Tworzy instancje kolektora V3"""
        return self.create_instance(CollectorType.V3, *args, **kwargs)
    
    def create_v4_instance(self, *args, **kwargs) -> Any:
        """Tworzy instancje kolektora V4"""
        return self.create_instance(CollectorType.V4, *args, **kwargs)
    
    def create_external_instance(self, *args, **kwargs) -> Any:
        """Tworzy instancje kolektora External"""
        return self.create_instance(CollectorType.EXTERNAL, *args, **kwargs)
    
    # =========================================================================
    # STATYSTYKI
    # =========================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Zwraca statystyki rejestru"""
        return {
            "total_registered": len(self._registry),
            "discovered": self._discovered,
            "status": self._status.value,
            "collector_types": [ct.value for ct in self.get_collector_types()]
        }
    
    def display(self) -> None:
        """Wyswietla informacje o rejestrze"""
        print("=" * 60)
        print("COLLECTOR REGISTRY")
        print("=" * 60)
        print(f"Status: {self._status.value}")
        print(f"Odkryty: {self._discovered}")
        print(f"Zarejestrowani kolektorzy: {len(self._registry)}")
        print()
        
        for collector_type, registration in self._registry.items():
            status = "ENABLED" if registration.is_enabled else "DISABLED"
            print(f"  {registration.name} ({collector_type.value}): {status}")
            print(f"    Source: {registration.source_type.name}")
            print(f"    Priority: {registration.priority}")
        
        print("=" * 60)


class GlobalCollectorRegistry:
    """
    Singletonowa wersja CollectorRegistry.
    """
    
    _instance: Optional[CollectorRegistry] = None
    
    @classmethod
    def get_instance(cls) -> CollectorRegistry:
        """Zwraca instancje singletona"""
        if cls._instance is None:
            cls._instance = CollectorRegistry()
            cls._instance._is_singleton = True
        return cls._instance
    
    @classmethod
    def get_manager(cls) -> KnowledgeCollectorManager:
        """Zwraca managera z singletonowym rejestrem"""
        registry = cls.get_instance()
        return registry.create_manager()


# Globalna instancja rejestru
registry: Optional[CollectorRegistry] = None


def get_registry() -> CollectorRegistry:
    """Zwraca globalna instancje rejestru"""
    global registry
    if registry is None:
        registry = GlobalCollectorRegistry.get_instance()
    return registry


def get_collector_registry() -> CollectorRegistry:
    """Alias dla get_registry()"""
    return get_registry()
