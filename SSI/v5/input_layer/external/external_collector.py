"""
SSI V5 - External Input Layer - External Knowledge Collector
Glowny kolektor danych zewnetrznych

Odpowiedzialnosc:
- Zarzadzanie zrodlami danych zewnetrznych
- Koordynacja zbierania danych z roznych zrodel
- Agregacja danych w jeden pakiet (ExternalDataPackage)
- Walidacja zebranych danych

Wersja: 1.0
Data: 2026-07-31
"""

import logging
from typing import Optional, List, Dict, Any, Union, Set
from datetime import datetime

from .source_types import SourceType, LaboratoryType, ExternalStatus
from .external_models import (
    ExternalDataPackage, DeveloperInput, LaboratoryData,
    AgentInputData, SystemMessages,
    create_external_package
)
from .sources import (
    DeveloperSource, LaboratorySource, AgentSource, SystemSource
)

logger = logging.getLogger(__name__)


class ExternalKnowledgeCollector:
    """
    Glowny kolektor danych zewnetrznych.
    
    Odpowiada za:
    - Inicjalizacje i zarzadzanie zrodlami danych
    - Zbieranie danych ze wszystkich zrodel
    - Agregacje danych w ExternalDataPackage
    - Walidacje zebranych danych
    - Generowanie podsumowan (summary)
    
    Uzycie:
        collector = ExternalKnowledgeCollector()
        collector.initialize()
        
        # Zbieranie wszystkich danych
        package = collector.collect_all()
        
        # wbieranie specyficznych zrodel
        dev_data = collector.collect_developer_input()
        lab_data = collector.collect_laboratories()
        
        # Walidacja
        is_valid = collector.validate()
        
        # Podsumowanie
        summary = collector.get_summary()
    """
    
    def __init__(self):
        """Inicjalizacja kolektora."""
        # Zrodla danych
        self._developer_source: Optional[DeveloperSource] = None
        self._laboratory_sources: Dict[str, LaboratorySource] = {}
        self._agent_source: Optional[AgentSource] = None
        self._system_source: Optional[SystemSource] = None
        
        # Status
        self._initialized = False
        self._status = ExternalStatus.PENDING
        self._last_collection_timestamp: Optional[datetime] = None
        
        # Statystyki
        self._collection_stats: Dict[str, int] = {}
        self._validation_results: Dict[str, bool] = {}
        
        # pakiet danych
        self._current_package: Optional[ExternalDataPackage] = None
        
        logger.info("ExternalKnowledgeCollector zainicjowany")
    
    def initialize(self, developer_id: str = "default") -> bool:
        """
        Inicjalizuje wszystkie zrodla danych.
        
        Args:
            developer_id: Identyfikator programisty (domyslnie "default")
            
        Returns:
            True jeśli inicjalizacja sie powiodla
        """
        try:
            # Inicjalizuj zrodlo programisty
            self._developer_source = DeveloperSource(
                developer_id=developer_id,
                source_name="main_developer_panel"
            )
            logger.info(f"Zainicjowano DeveloperSource: {developer_id}")
            
            # Inicjalizuj zrodlo systemowe
            self._system_source = SystemSource(source_name="main_system")
            logger.info("Zainicjowano SystemSource")
            
            # Inicjalizuj zrodlo agentow
            self._agent_source = AgentSource(agent_id=None, source_name="main_agent_system")
            logger.info("Zainicjowano AgentSource")
            
            # Inicjalizuj zrodla laboratoriow (dla kazdego typu)
            for lab_type in LaboratoryType:
                # Utworz zrodlo dla kazdego typu laboratorium
                self._laboratory_sources[lab_type.value] = LaboratorySource(
                    lab_id=f"lab_{lab_type.value}",
                    laboratory_type=lab_type,
                    source_name=f"{lab_type.value}_laboratory"
                )
                logger.info(f"Zainicjowano LaboratorySource: {lab_type.value}")
            
            self._initialized = True
            self._status = ExternalStatus.READY
            logger.info("ExternalKnowledgeCollector zainicjalizowany")
            
            return True
            
        except Exception as e:
            logger.error(f"Blad inicjalizacji ExternalKnowledgeCollector: {e}")
            self._status = ExternalStatus.FAILED
            return False
    
    def _ensure_initialized(self) -> bool:
        """
        Sprawdza czy kolektor jest zainicjalizowany.
        
        Returns:
            True jeśli zainicjalizowany
            
        Raises:
            RuntimeError: Jesli kolektor nie jest zainicjalizowany
        """
        if not self._initialized:
            error_msg = "ExternalKnowledgeCollector nie jest zainicjalizowany. Wywolaj initialize() najpierw."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        return True
    
    def get_developer_source(self) -> DeveloperSource:
        """Zwraca zrodlo programisty."""
        self._ensure_initialized()
        if not self._developer_source:
            raise RuntimeError("DeveloperSource nie jest zainicjalizowany")
        return self._developer_source
    
    def get_laboratory_source(self, laboratory_type: str) -> LaboratorySource:
        """
        Zwraca zrodlo laboratorium.
        
        Args:
            laboratory_type: Typ laboratorium (world_lab, type_lab, group_lab, coupon_lab)
            
        Returns:
            LaboratorySource
        """
        self._ensure_initialized()
        source = self._laboratory_sources.get(laboratory_type)
        if not source:
            raise ValueError(f"Nieznany typ laboratorium: {laboratory_type}")
        return source
    
    def get_agent_source(self) -> AgentSource:
        """Zwraca zrodlo agentow."""
        self._ensure_initialized()
        if not self._agent_source:
            raise RuntimeError("AgentSource nie jest zainicjalizowany")
        return self._agent_source
    
    def get_system_source(self) -> SystemSource:
        """Zwraca zrodlo systemowe."""
        self._ensure_initialized()
        if not self._system_source:
            raise RuntimeError("SystemSource nie jest zainicjalizowany")
        return self._system_source
    
    # ========================================================================
    # METODY ZBIERANIA POJEDYNCZYCH ZRODEL
    # ========================================================================
    
    def collect_developer_input(self) -> DeveloperInput:
        """
        Zbiera dane od programisty.
        
        Returns:
            DeveloperInput z danymi od programisty
        """
        self._ensure_initialized()
        
        if not self._developer_source:
            raise RuntimeError("DeveloperSource nie jest zainicjalizowany")
        
        logger.info("Zbieranie danych od programisty...")
        data = self._developer_source.collect()
        
        # Zaktualizuj status zrodla
        self._developer_source.set_status(ExternalStatus.COMPLETED)
        
        # Zarejestruj w statystykach
        counts = self._developer_source.get_data_count()
        self._collection_stats["developer"] = sum(counts.values())
        
        logger.info(f"Zebrano {sum(counts.values())} elementow od programisty")
        return data
    
    def collect_laboratories(self) -> List[LaboratoryData]:
        """
        Zbiera dane ze wszystkich laboratoriow.
        
        Returns:
            Lista LaboratoryData ze wszystkich laboratoriow
        """
        self._ensure_initialized()
        
        all_lab_data = []
        total_count = 0
        
        logger.info("Zbieranie danych z laboratoriow...")
        
        for lab_type, source in self._laboratory_sources.items():
            # Zbierz dane z kazdego laboratorium
            lab_data = source.collect()
            all_lab_data.append(lab_data)
            
            # Zaktualizuj status zrodla
            source.set_status(ExternalStatus.COMPLETED)
            
            # Zaktualizuj statystyki
            counts = source.get_data_count()
            type_count = sum(counts.values())
            total_count += type_count
            self._collection_stats[f"laboratory_{lab_type}"] = type_count
            
            logger.info(f"  Laboratorium {lab_type}: {type_count} elementow")
        
        self._collection_stats["laboratories_total"] = total_count
        logger.info(f"Zebrano {total_count} elementow z {len(all_lab_data)} laboratoriow")
        
        return all_lab_data
    
    def collect_agent_input(self) -> List[AgentInputData]:
        """
        Zbiera dane od wszystkich agentow.
        
        Returns:
            Lista AgentInputData od wszystkich agentow
        """
        self._ensure_initialized()
        
        if not self._agent_source:
            raise RuntimeError("AgentSource nie jest zainicjalizowany")
        
        logger.info("Zbieranie danych od agentow...")
        
        # Zbierz dane
        data = [self._agent_source.collect()]
        
        # Zaktualizuj status zrodla
        self._agent_source.set_status(ExternalStatus.COMPLETED)
        
        # Zaktualizuj statystyki
        counts = self._agent_source.get_data_count()
        total_count = sum(counts.values())
        self._collection_stats["agents"] = total_count
        
        logger.info(f"Zebrano {total_count} elementow od agentow")
        return data
    
    def collect_system_messages(self) -> SystemMessages:
        """
        Zbiera komunikaty systemowe.
        
        Returns:
            SystemMessages z komunikatami systemowymi
        """
        self._ensure_initialized()
        
        if not self._system_source:
            raise RuntimeError("SystemSource nie jest zainicjalizowany")
        
        logger.info("Zbieranie danych systemowych...")
        
        # Zbierz dane
        data = self._system_source.collect()
        
        # Zaktualizuj status zrodla
        self._system_source.set_status(ExternalStatus.COMPLETED)
        
        # Zaktualizuj statystyki
        counts = self._system_source.get_data_count()
        total_count = sum(counts.values())
        self._collection_stats["system"] = total_count
        
        logger.info(f"Zebrano {total_count} elementow systemowych")
        return data
    
    # ========================================================================
    # METODY ZBIERANIA WSZYSTKICH DANYCH
    # ========================================================================
    
    def collect_all(self) -> ExternalDataPackage:
        """
        Zbiera wszystkie dane zewnetrzne i pakuje je w jeden ExternalDataPackage.
        
        Returns:
            ExternalDataPackage zawierajacy wszystkie zebrane dane
        """
        self._ensure_initialized()
        
        logger.info("Rozpoczynanie zbierania wszystkich danych zewnetrznych...")
        self._status = ExternalStatus.COLLECTING
        self._last_collection_timestamp = datetime.now()
        
        # Wyczysc poprzednie statystyki
        self._collection_stats.clear()
        self._validation_results.clear()
        
        # Tworz nowy pakiet
        package = create_external_package()
        
        try:
            # Zbierz dane od programisty
            dev_input = self.collect_developer_input()
            package.add_developer_data(dev_input)
            
            # Zbierz dane z laboratoriow
            lab_data = self.collect_laboratories()
            for data in lab_data:
                package.add_laboratory_data(data)
            
            # Zbierz dane od agentow
            agent_data = self.collect_agent_input()
            for data in agent_data:
                package.add_agent_data(data)
            
            # Zbierz dane systemowe
            sys_data = self.collect_system_messages()
            package.add_system_data(sys_data)
            
            # Ustaw status pakietu
            package.set_status(ExternalStatus.COMPLETED)
            
            # Zapisz pakiet jako biezacy
            self._current_package = package
            self._status = ExternalStatus.COMPLETED
            
            # Zaktualizuj statystyki paczki
            counts = package.get_all_data_count()
            self._collection_stats["total"] = sum(counts.values())
            
            logger.info(f"Pakowanie zakonczone. Poczatkowy pakiet: {package.package_id}")
            logger.info(f"Statystyki: {counts}")
            
            return package
            
        except Exception as e:
            self._status = ExternalStatus.FAILED
            logger.error(f"Blad podczas zbierania wszystkich danych: {e}")
            raise
    
    def collect_specific(self, source_types: List[SourceType]) -> ExternalDataPackage:
        """
        Zbiera dane tylko z okreslonych typow zrodel.
        
        Args:
            source_types: Lista typow zrodel do zebrania
            
        Returns:
            ExternalDataPackage z danymi z wybranych zrodel
        """
        self._ensure_initialized()
        
        logger.info(f"Zbieranie danych z okreslonych zrodel: {[st.name for st in source_types]}")
        self._status = ExternalStatus.COLLECTING
        self._last_collection_timestamp = datetime.now()
        
        # Wyczysc statystyki
        self._collection_stats.clear()
        
        # Tworz nowy pakiet
        package = create_external_package()
        
        try:
            for source_type in source_types:
                if source_type == SourceType.DEVELOPER:
                    dev_input = self.collect_developer_input()
                    package.add_developer_data(dev_input)
                
                elif source_type == SourceType.LABORATORIES:
                    lab_data = self.collect_laboratories()
                    for data in lab_data:
                        package.add_laboratory_data(data)
                
                elif source_type == SourceType.AGENTS:
                    agent_data = self.collect_agent_input()
                    for data in agent_data:
                        package.add_agent_data(data)
                
                elif source_type == SourceType.SYSTEM:
                    sys_data = self.collect_system_messages()
                    package.add_system_data(sys_data)
            
            # Ustaw status
            package.set_status(ExternalStatus.COMPLETED)
            self._current_package = package
            self._status = ExternalStatus.COMPLETED
            
            logger.info(f"Zebrano dane z {len(source_types)} zrodel")
            return package
            
        except Exception as e:
            self._status = ExternalStatus.FAILED
            logger.error(f"Blad podczas zbierania specyficznych danych: {e}")
            raise
    
    # ========================================================================
    # METODY WALIDACJI
    # ========================================================================
    
    def validate(self, package: Optional[ExternalDataPackage] = None) -> bool:
        """
        Waliduje zebrane dane.
        
        Args:
            package: Pakiet do walidacji (domyslnie biezacy pakiet)
            
        Returns:
            True jeśli wszystkie dane sa poprawne
        """
        self._ensure_initialized()
        
        logger.info(" Walidacja zebranych danych...")
        
        # Uzyj biezacego pakietu jesli nie podano
        if package is None:
            package = self._current_package
            if package is None:
                logger.warning("Brak pakietu do walidacji. Wywolaj collect_all() lub collect_specific() najpierw.")
                return False
        
        all_valid = True
        self._validation_results.clear()
        
        try:
            # Waliduj dane od programisty
            if package.developer_data:
                dev_valid = self._developer_source.validate()
                self._validation_results["developer"] = dev_valid
                if not dev_valid:
                    all_valid = False
                    logger.error("Nieprawidlowe dane programisty")
                else:
                    logger.info("Dane programisty: poprawne")
            
            # Waliduj dane z laboratoriow
            for lab_data in package.laboratory_data:
                lab_source = self._laboratory_sources.get(lab_data.lab_id)
                if lab_source:
                    lab_valid = lab_source.validate()
                    self._validation_results[f"laboratory_{lab_data.lab_id}"] = lab_valid
                    if not lab_valid:
                        all_valid = False
                        logger.error(f"Nieprawidlowe dane laboratorium: {lab_data.lab_id}")
                    else:
                        logger.info(f"Dane laboratorium {lab_data.lab_id}: poprawne")
            
            # Waliduj dane od agentow
            if package.agent_data:
                for agent_data in package.agent_data:
                    agent_valid = self._agent_source.validate()
                    self._validation_results["agents"] = agent_valid
                    if not agent_valid:
                        all_valid = False
                        logger.error("Nieprawidlowe dane agentow")
                    else:
                        logger.info("Dane agentow: poprawne")
                    break  # Tylko raz, bo wszyscy agenci sa w jednym zrodle
            
            # Waliduj dane systemowe
            if package.system_data:
                sys_valid = self._system_source.validate()
                self._validation_results["system"] = sys_valid
                if not sys_valid:
                    all_valid = False
                    logger.error("Nieprawidlowe dane systemowe")
                else:
                    logger.info("Dane systemowe: poprawne")
            
            # Ustaw status pakietu
            if all_valid:
                package.status = ExternalStatus.VALIDATED
                self._status = ExternalStatus.VALIDATED
            else:
                package.status = ExternalStatus.INVALID
                self._status = ExternalStatus.INVALID
            
            # Zaktualizuj wyniki walidacji w pakiecie
            package.validation_results = self._validation_results.copy()
            
            result_str = "SUKCES" if all_valid else "NIEPOWODZENIE"
            logger.info(f"Walidacja zakonczona: {result_str}")
            return all_valid
            
        except Exception as e:
            logger.error(f"Blad podczas walidacji: {e}")
            self._status = ExternalStatus.FAILED
            return False
    
    # ========================================================================
    # METODY PODSUMOWANIA
    # ========================================================================
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Zwraca podsumowanie zebranych danych.
        
        Returns:
            Slownik z podsumowaniem zebranych danych
        """
        self._ensure_initialized()
        
        summary = {
            "collector_status": self._status.name,
            "is_initialized": self._initialized,
            "last_collection_timestamp": self._last_collection_timestamp.isoformat() if self._last_collection_timestamp else None,
            "collection_stats": self._collection_stats.copy(),
            "validation_results": self._validation_results.copy()
        }
        
        # Dodaj informacje o biezacym pakiecie
        if self._current_package:
            summary["current_package"] = {
                "package_id": self._current_package.package_id,
                "status": self._current_package.status.name,
                "timestamp": self._current_package.timestamp.isoformat(),
                "data_counts": self._current_package.get_all_data_count(),
                "source_types": [st.name for st in self._current_package.get_source_types_present()]
            }
        else:
            summary["current_package"] = None
        
        # Dodaj informacje o zrodlach
        summary["sources"] = {
            "developer": {
                "initialized": self._developer_source is not None,
                "has_data": self._developer_source.has_data if self._developer_source else False,
                "status": self._developer_source.get_status().name if self._developer_source else "NOT_INITIALIZED"
            },
            "laboratories": {
                lab_id: {
                    "has_data": source.has_data,
                    "status": source.get_status().name
                }
                for lab_id, source in self._laboratory_sources.items()
            },
            "agents": {
                "initialized": self._agent_source is not None,
                "has_data": self._agent_source.has_data if self._agent_source else False,
                "status": self._agent_source.get_status().name if self._agent_source else "NOT_INITIALIZED"
            },
            "system": {
                "initialized": self._system_source is not None,
                "has_data": self._system_source.has_data if self._system_source else False,
                "status": self._system_source.get_status().name if self._system_source else "NOT_INITIALIZED"
            }
        }
        
        return summary
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Zwraca statystyki kolektora.
        
        Returns:
            Slownik ze statystykami
        """
        return {
            "total_collections": 1 if self._current_package else 0,
            "total_items": self._collection_stats.get("total", 0),
            "by_source": self._collection_stats.copy(),
            "validation_pass_rate": (
                sum(1 for v in self._validation_results.values() if v) / len(self._validation_results)
                if self._validation_results else 0
            )
        }
    
    def get_current_package(self) -> Optional[ExternalDataPackage]:
        """
        Zwraca biezacy pakiet danych.
        
        Returns:
            Biezacy ExternalDataPackage lub None
        """
        return self._current_package
    
    # ========================================================================
    # METODY UTILITY
    # ========================================================================
    
    def reset(self) -> None:
        """
        Resetuje stan kolektora (nie usuwa zainicjalizowanych zrodel).
        """
        self._status = ExternalStatus.PENDING
        self._last_collection_timestamp = None
        self._collection_stats.clear()
        self._validation_results.clear()
        self._current_package = None
        
        # Wyczysc dane ze zrodel (ale nie usuwaj zrodel)
        if self._developer_source:
            self._developer_source.clear()
        if self._agent_source:
            self._agent_source.clear()
        if self._system_source:
            self._system_source.clear()
        for source in self._laboratory_sources.values():
            source.clear()
        
        logger.info("ExternalKnowledgeCollector zresetowany")
    
    def clear_all(self) -> None:
        """
        Calkowicie czyści kolektor (wrpm zrodla).
        """
        self._developer_source = None
        self._laboratory_sources.clear()
        self._agent_source = None
        self._system_source = None
        self._initialized = False
        self._status = ExternalStatus.PENDING
        self._last_collection_timestamp = None
        self._collection_stats.clear()
        self._validation_results.clear()
        self._current_package = None
        
        logger.info("ExternalKnowledgeCollector w pelni wyczyszczony")
    
    def get_status(self) -> ExternalStatus:
        """Zwraca aktualny status kolektora."""
        return self._status
    
    def is_ready(self) -> bool:
        """Czy kolektor jest gotowy do zbierania danych?"""
        return self._initialized and self._status not in [
            ExternalStatus.FAILED, ExternalStatus.COLLECTING, ExternalStatus.VALIDATING
        ]
    
    def __repr__(self) -> str:
        status_str = self._status.name if self._initialized else "NOT_INITIALIZED"
        return (f"ExternalKnowledgeCollector(status={status_str}, "
                f"initialized={self._initialized}, "
                f"has_package={self._current_package is not None})")
