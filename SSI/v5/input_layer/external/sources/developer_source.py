"""
SSI V5 - External Input Layer - Developer Source
Handler zrodla danych od programisty

Odpowiedzialnosc:
- Zbieranie danych od programisty
- Tworzenie DeveloperInput z roznych zrodel
- Integracja z panelami programisty

Wersja: 1.0
Data: 2026-07-31
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..source_types import SourceType, ExternalStatus
from ..external_models import (
    DeveloperInput, DeveloperCommand, Requirement, ArchitectureDecision,
    create_developer_command, create_requirement, create_architecture_decision
)

logger = logging.getLogger(__name__)


class DeveloperSource:
    """
    Handler zrodla danych od programisty.
    
    Odpowiada za:
    - Zbieranie polecen od programisty
    - Zbieranie wymagan systemowych
    - Zbieranie decyzji architektonicznych
    - Pakowanie danych w DeveloperInput
    - Walidacja zebranych danych
    """
    
    def __init__(self, developer_id: str = "default", source_name: str = "developer_panel"):
        """
        Inicjalizacja zrodla programisty.
        
        Args:
            developer_id: Identyfikator programisty
            source_name: Nazwa zrodla (dla logow)
        """
        self.developer_id = developer_id
        self.source_name = source_name
        self._commands: List[DeveloperCommand] = []
        self._requirements: List[Requirement] = []
        self._decisions: List[ArchitectureDecision] = []
        self._analysis_requests: List[str] = []
        self._change_history: List[str] = []
        self._status = ExternalStatus.PENDING
        self._timestamp = None
        self._metadata: Dict[str, Any] = {}
        
        logger.info(f"DeveloperSource zainicjowany: {self.developer_id}")
    
    def add_command(
        self,
        command_id: str,
        command: str,
        priority: int = 5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DeveloperCommand:
        """
        Dodaje polecenie od programisty.
        
        Args:
            command_id: Unikalny identyfikator polecenia
            command: Tresc polecenia
            priority: Priorytet (1-10)
            metadata: Dodatkowe metadane
            
        Returns:
            Utworzony DeveloperCommand
        """
        cmd = create_developer_command(command_id, command, priority)
        if metadata:
            cmd.metadata.update(metadata)
        self._commands.append(cmd)
        logger.debug(f"Dodano polecenie: {command_id} (priorytet: {priority})")
        return cmd
    
    def add_requirement(
        self,
        requirement_id: str,
        title: str,
        description: str,
        category: str = "functionality",
        priority: int = 5,
        status: str = "pending",
        deadline: Optional[datetime] = None,
        depends_on: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Requirement:
        """
        Dodaje wymaganie systemowe.
        
        Args:
            requirement_id: Unikalny identyfikator wymagania
            title: Tytul wymagania
            description: Opis wymagania
            category: Kategoria wymagania
            priority: Priorytet
            status: Status wymagania
            deadline: Termin realizacji
            depends_on: Lista zaleznosci
            metadata: Dodatkowe metadane
            
        Returns:
            Utworzone Requirement
        """
        req = create_requirement(requirement_id, title, description, priority)
        req.category = category
        req.status = status
        req.deadline = deadline
        if depends_on:
            req.depends_on.extend(depends_on)
        if metadata:
            req.metadata.update(metadata)
        self._requirements.append(req)
        logger.debug(f"Dodano wymaganie: {requirement_id} - {title}")
        return req
    
    def add_architecture_decision(
        self,
        decision_id: str,
        title: str,
        description: str,
        rationale: str = "",
        impact: str = "",
        alternatives: Optional[List[str]] = None,
        status: str = "active",
        metadata: Optional[Dict[str, Any]] = None
    ) -> ArchitectureDecision:
        """
        Dodaje decyzje architektoniczna.
        
        Args:
            decision_id: Unikalny identyfikator decyzji
            title: Tytul decyzji
            description: Opis decyzji
            rationale: Uzasadnienie decyzji
            impact: Wplyw na system
            alternatives: Lista alternatyw
            status: Status decyzji
            metadata: Dodatkowe metadane
            
        Returns:
            Utworzona ArchitectureDecision
        """
        decision = create_architecture_decision(decision_id, title, description)
        decision.rationale = rationale
        decision.impact = impact
        if alternatives:
            decision.alternatives.extend(alternatives)
        decision.status = status
        if metadata:
            decision.metadata.update(metadata)
        self._decisions.append(decision)
        logger.debug(f"Dodano decyzje architektoniczna: {decision_id} - {title}")
        return decision
    
    def add_analysis_request(self, request: str) -> None:
        """
        Dodaje zadanie analizy systemu.
        
        Args:
            request: Tresc zadania analizy
        """
        self._analysis_requests.append(request)
        logger.debug(f"Dodano zadanie analizy: {request[:50]}...")
    
    def add_change_history(self, change_description: str) -> None:
        """
        Dodaje rekord do historii zmian.
        
        Args:
            change_description: Opis zmiany
        """
        self._change_history.append(change_description)
        logger.debug(f"Dodano zmien do historii: {change_description[:50]}...")
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Ustawia metadane.
        
        Args:
            key: Klucz metadanych
            value: Wartosc metadanych
        """
        self._metadata[key] = value
    
    def collect(self) -> DeveloperInput:
        """
        Zbiera wszystkie zebrane dane i zwraca je jako DeveloperInput.
        
        Returns:
            DeveloperInput zawierajacy wszystkie zebrane dane
        """
        self._timestamp = datetime.now()
        self._status = ExternalStatus.COMPLETED
        
        dev_input = DeveloperInput(
            developer_id=self.developer_id,
            source_type=SourceType.DEVELOPER,
            commands=self._commands.copy(),
            requirements=self._requirements.copy(),
            decisions=self._decisions.copy(),
            analysis_requests=self._analysis_requests.copy(),
            change_history=self._change_history.copy(),
            timestamp=self._timestamp,
            status=self._status,
            metadata=self._metadata.copy()
        )
        
        logger.info(f"Zebrano dane programisty: {len(dev_input.commands)} polecen, "
                    f"{len(dev_input.requirements)} wymagan, "
                    f"{len(dev_input.decisions)} decyzji")
        
        return dev_input
    
    def clear(self) -> None:
        """Czysci zebrane dane."""
        self._commands.clear()
        self._requirements.clear()
        self._decisions.clear()
        self._analysis_requests.clear()
        self._change_history.clear()
        self._status = ExternalStatus.PENDING
        self._timestamp = None
        self._metadata.clear()
        logger.info(f"Wyczyszczono dane programisty: {self.developer_id}")
    
    def get_status(self) -> ExternalStatus:
        """Zwraca aktualny status zrodla."""
        return self._status
    
    def set_status(self, status: ExternalStatus) -> None:
        """Ustawia status zrodla."""
        self._status = status
        logger.debug(f"Status DeveloperSource ustawiony na: {status}")
    
    def get_data_count(self) -> Dict[str, int]:
        """
        Zwraca liczbe zebranych elementow.
        
        Returns:
            Slownik z liczbami elementow
        """
        return {
            "commands": len(self._commands),
            "requirements": len(self._requirements),
            "decisions": len(self._decisions),
            "analysis_requests": len(self._analysis_requests),
            "change_history": len(self._change_history)
        }
    
    @property
    def has_data(self) -> bool:
        """Czy zrodlo ma jakiekolwiek dane?"""
        return bool(
            self._commands or
            self._requirements or
            self._decisions or
            self._analysis_requests or
            self._change_history
        )
    
    def validate(self) -> bool:
        """
        Waliduje zebrane dane.
        
        Returns:
            True jeśli dane sa poprawne
        """
        # Sprawdz czy sa jakies dane
        if not self.has_data:
            logger.warning(f"Brak danych programisty: {self.developer_id}")
            self._status = ExternalStatus.INVALID
            return False
        
        # Sprawdz poprawnosc polecen
        for cmd in self._commands:
            if not 1 <= cmd.priority <= 10:
                logger.error(f"Nieprawidlowy priorytet polecenia: {cmd.command_id}")
                self._status = ExternalStatus.INVALID
                return False
        
        self._status = ExternalStatus.VALIDATED
        return True
    
    def __repr__(self) -> str:
        counts = self.get_data_count()
        return (f"DeveloperSource(developer_id='{self.developer_id}', "
                f"commands={counts['commands']}, requirements={counts['requirements']}, "
                f"decisions={counts['decisions']})")
