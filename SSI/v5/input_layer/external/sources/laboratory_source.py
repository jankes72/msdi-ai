"""
SSI V5 - External Input Layer - Laboratory Source
Handler zrodla danych z laboratoriow

Odpowiedzialnosc:
- Zbieranie danych z róznych typów laboratoriow
- Tworzenie LaboratoryData z eksperymentów i odkryc
- Integracja z systemem laboratoriow

Wersja: 1.0
Data: 2026-07-31
"""

import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta

from ..source_types import SourceType, LaboratoryType, ExternalStatus
from ..external_models import (
    LaboratoryData, ExperimentResult, DiscoveryRecord,
    create_experiment_result, create_discovery_record
)

logger = logging.getLogger(__name__)


class LaboratorySource:
    """
    Handler zrodla danych z laboratoriow.
    
    Odpowiada za:
    - Zbieranie danych z róznych typów laboratoriow
    - Tworzenie eksperymentów i odkryc
    - Pakowanie danych w LaboratoryData
    - Walidacja zebranych danych
    
    Obsluguje typy laboratoriow:
    - WORLD_LAB: Badania swiatow
    - TYPE_LAB: Badania typow i klasyfikacji
    - GROUP_LAB: Badania grup i strategii grupowych
    - COUPON_LAB: Badania kuponow i analizy ryzyka
    """
    
    def __init__(
        self,
        lab_id: str = "default",
        laboratory_type: LaboratoryType = LaboratoryType.WORLD_LAB,
        source_name: str = "laboratory"
    ):
        """
        Inicjalizacja zrodla laboratorium.
        
        Args:
            lab_id: Identyfikator laboratorium
            laboratory_type: Typ laboratorium
            source_name: Nazwa zrodla (dla logow)
        """
        self.lab_id = lab_id
        self.laboratory_type = laboratory_type
        self.source_name = source_name
        self.source_type = SourceType.LABORATORIES
        
        self._experiments: List[ExperimentResult] = []
        self._discoveries: List[DiscoveryRecord] = []
        self._active_research: List[str] = []
        self._completed_research: List[str] = []
        self._status = ExternalStatus.PENDING
        self._timestamp = None
        self._metadata: Dict[str, Any] = {}
        
        logger.info(f"LaboratorySource zainicjowany: {self.lab_id} ({self.laboratory_type.value})")
    
    def add_experiment(
        self,
        experiment_id: str,
        title: str,
        hypothesis: str = "",
        methodology: str = "",
        data: Optional[Dict[str, Any]] = None,
        results: Optional[Dict[str, Any]] = None,
        conclusions: Optional[List[str]] = None,
        success: bool = True,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ExperimentResult:
        """
        Dodaje eksperyment do laboratorium.
        
        Args:
            experiment_id: Unikalny identyfikator eksperymentu
            title: Tytul eksperymentu
            hypothesis: Hipoteza testowana
            methodology: Metodologia
            data: Dane zebrane
            results: Wyniki
            conclusions: Wnioski
            success: Czy eksperyment sie powiodl
            timestamp: Data wykonania (domyslnie teraz)
            metadata: Dodatkowe metadane
            
        Returns:
            Utworzony ExperimentResult
        """
        exp = create_experiment_result(
            experiment_id, self.laboratory_type, title, hypothesis, success
        )
        exp.methodology = methodology
        if data:
            exp.data.update(data)
        if results:
            exp.results.update(results)
        if conclusions:
            exp.conclusions.extend(conclusions)
        if timestamp:
            exp.timestamp = timestamp
        if metadata:
            exp.metadata.update(metadata)
        
        self._experiments.append(exp)
        logger.debug(f"Dodano eksperyment: {experiment_id} - {title}")
        return exp
    
    def add_discovery(
        self,
        discovery_id: str,
        title: str,
        description: str,
        category: str = "scientific",
        impact: str = "",
        evidence: Optional[List[Any]] = None,
        related_experiments: Optional[List[str]] = None,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DiscoveryRecord:
        """
        Dodaje odkrycie naukowe/techniczne.
        
        Args:
            discovery_id: Unikalny identyfikator odkrycia
            title: Tytul odkrycia
            description: Opis odkrycia
            category: Kategoria odkrycia
            impact: Wplyw na system
            evidence: Dowody na poparcie
            related_experiments: Powiazane eksperymenty
            timestamp: Data odkrycia (domyslnie teraz)
            metadata: Dodatkowe metadane
            
        Returns:
            Utworzony DiscoveryRecord
        """
        discovery = create_discovery_record(
            discovery_id, self.laboratory_type, title, description
        )
        discovery.category = category
        discovery.impact = impact
        if evidence:
            discovery.evidence.extend(evidence)
        if related_experiments:
            discovery.related_experiments.extend(related_experiments)
        if timestamp:
            discovery.timestamp = timestamp
        if metadata:
            discovery.metadata.update(metadata)
        
        self._discoveries.append(discovery)
        logger.debug(f"Dodano odkrycie: {discovery_id} - {title}")
        return discovery
    
    def add_active_research(self, research_topic: str) -> None:
        """
        Dodaje temat aktywnych badan.
        
        Args:
            research_topic: Temat badan
        """
        if research_topic not in self._active_research:
            self._active_research.append(research_topic)
            logger.debug(f"Dodano temat badan: {research_topic}")
    
    def add_completed_research(self, research_topic: str) -> None:
        """
        Dodaje temat zakonczonych badan.
        
        Args:
            research_topic: Temat badan
        """
        if research_topic not in self._completed_research:
            self._completed_research.append(research_topic)
            # Usun z aktywnych jesli tam jest
            if research_topic in self._active_research:
                self._active_research.remove(research_topic)
            logger.debug(f"Dodano zakonczone badanie: {research_topic}")
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Ustawia metadane.
        
        Args:
            key: Klucz metadanych
            value: Wartosc metadanych
        """
        self._metadata[key] = value
    
    def collect(self) -> LaboratoryData:
        """
        Zbiera wszystkie zebrane dane i zwraca je jako LaboratoryData.
        
        Returns:
            LaboratoryData zawierajacy wszystkie zebrane dane
        """
        self._timestamp = datetime.now()
        self._status = ExternalStatus.COMPLETED
        
        lab_data = LaboratoryData(
            lab_id=self.lab_id,
            source_type=SourceType.LABORATORIES,
            laboratory_type=self.laboratory_type,
            experiments=self._experiments.copy(),
            discoveries=self._discoveries.copy(),
            active_research=self._active_research.copy(),
            completed_research=self._completed_research.copy(),
            timestamp=self._timestamp,
            status=self._status,
            metadata=self._metadata.copy()
        )
        
        logger.info(f"Zebrano dane laboratorium {self.lab_id}: "
                    f"{len(lab_data.experiments)} eksperymentow, "
                    f"{len(lab_data.discoveries)} odkryc")
        
        return lab_data
    
    def clear(self) -> None:
        """Czysci zebrane dane."""
        self._experiments.clear()
        self._discoveries.clear()
        self._active_research.clear()
        self._completed_research.clear()
        self._status = ExternalStatus.PENDING
        self._timestamp = None
        self._metadata.clear()
        logger.info(f"Wyczyszczono dane laboratorium: {self.lab_id}")
    
    def get_status(self) -> ExternalStatus:
        """Zwraca aktualny status zrodla."""
        return self._status
    
    def set_status(self, status: ExternalStatus) -> None:
        """Ustawia status zrodla."""
        self._status = status
        logger.debug(f"Status LaboratorySource ustawiony na: {status}")
    
    def get_data_count(self) -> Dict[str, int]:
        """
        Zwraca liczbe zebranych elementow.
        
        Returns:
            Slownik z liczbami elementow
        """
        return {
            "experiments": len(self._experiments),
            "discoveries": len(self._discoveries),
            "active_research": len(self._active_research),
            "completed_research": len(self._completed_research)
        }
    
    @property
    def has_data(self) -> bool:
        """Czy zrodlo ma jakiekolwiek dane?"""
        return bool(
            self._experiments or
            self._discoveries or
            self._active_research or
            self._completed_research
        )
    
    def get_recent_experiments(self, days: int = 7) -> List[ExperimentResult]:
        """
        Zwraca niedawne eksperymenty.
        
        Args:
            days: Liczba dni wstecz
            
        Returns:
            Lista niedawnych eksperymentow
        """
        cutoff = datetime.now() - timedelta(days=days)
        return [exp for exp in self._experiments if exp.timestamp >= cutoff]
    
    def get_successful_experiments(self) -> List[ExperimentResult]:
        """
        Zwraca udane eksperymenty.
        
        Returns:
            Lista udanych eksperymentow
        """
        return [exp for exp in self._experiments if exp.success]
    
    def get_failed_experiments(self) -> List[ExperimentResult]:
        """
        Zwraca nieudane eksperymenty.
        
        Returns:
            Lista nieudanych eksperymentow
        """
        return [exp for exp in self._experiments if not exp.success]
    
    def validate(self) -> bool:
        """
        Waliduje zebrane dane.
        
        Returns:
            True jeśli dane sa poprawne
        """
        # Sprawdz czy sa jakies dane
        if not self.has_data:
            logger.warning(f"Brak danych laboratorium: {self.lab_id}")
            self._status = ExternalStatus.INVALID
            return False
        
        # Sprawdz czy eksperymenty maja poprawne typy laboratorium
        for exp in self._experiments:
            if exp.laboratory_type != self.laboratory_type:
                logger.warning(f"Eksperyment {exp.experiment_id} ma nieprawidlowy typ laboratorium")
                self._status = ExternalStatus.INVALID
                return False
        
        # Sprawdz czy odkrycia maja poprawne typy laboratorium
        for disc in self._discoveries:
            if disc.laboratory_type != self.laboratory_type:
                logger.warning(f"Odkrycie {disc.discovery_id} ma nieprawidlowy typ laboratorium")
                self._status = ExternalStatus.INVALID
                return False
        
        self._status = ExternalStatus.VALIDATED
        return True
    
    def __repr__(self) -> str:
        counts = self.get_data_count()
        return (f"LaboratorySource(lab_id='{self.lab_id}', "
                f"type={self.laboratory_type.value}, "
                f"experiments={counts['experiments']}, "
                f"discoveries={counts['discoveries']})")
