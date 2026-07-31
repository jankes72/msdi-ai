"""
SSI V5 - External Input Layer - Agent Source
Handler zrodla danych od agentow

Odpowiedzialnosc:
- Zbieranie komunikatow i zdarzen od agentow
- monitorowanie aktivnosci agentow
- Pakowanie danych w AgentInputData

Wersja: 1.0
Data: 2026-07-31
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from ..source_types import SourceType, ExternalStatus
from ..external_models import (
    AgentInputData, AgentMessage, AgentEvent,
    MessageType, EventType,
    create_agent_message, create_agent_event
)

logger = logging.getLogger(__name__)


class AgentSource:
    """
    Handler zrodla danych od agentow.
    
    Odpowiada za:
    - Zbieranie komunikatow od agentow
    - Monitorowanie zdarzen agentowych
    - Sledzenie wspolpracy, konfliktow i sojuszow
    - Pakowanie danych w AgentInputData
    - Walidacja zebranych danych
    """
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        source_name: str = "agent_system"
    ):
        """
        Inicjalizacja zrodla agentow.
        
        Args:
            agent_id: Identyfikator agenta (opcjonalnie - moze byc kolektor dla wielu agentow)
            source_name: Nazwa zrodla (dla logow)
        """
        self.agent_id = agent_id
        self.source_name = source_name
        self.source_type = SourceType.AGENTS
        
        self._messages: List[AgentMessage] = []
        self._events: List[AgentEvent] = []
        self._collaborations: List[str] = []
        self._conflicts: List[str] = []
        self._alliances: List[str] = []
        self._status = ExternalStatus.PENDING
        self._timestamp = None
        self._metadata: Dict[str, Any] = {}
        
        logger.info(f"AgentSource zainicjowany: {self.agent_id or 'multiple_agents'}")
    
    def add_message(
        self,
        message_id: str,
        agent_id: str,
        content: str,
        message_type: MessageType = MessageType.INFORMATION,
        recipient: Optional[str] = None,
        priority: int = 5,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentMessage:
        """
        Dodaje komunikat od agenta.
        
        Args:
            message_id: Unikalny identyfikator komunikatu
            agent_id: Identyfikator agenta nadawcy
            content: Tresc komunikatu
            message_type: Typ komunikatu
            recipient: Odbiorca (None = broadcast)
            priority: Priorytet
            timestamp: Data wyslania (domyslnie teraz)
            metadata: Dodatkowe metadane
            
        Returns:
            Utworzony AgentMessage
        """
        msg = create_agent_message(
            message_id, agent_id, content, message_type
        )
        msg.recipient = recipient
        msg.priority = priority
        if timestamp:
            msg.timestamp = timestamp
        if metadata:
            msg.metadata.update(metadata)
        
        self._messages.append(msg)
        logger.debug(f"Dodano komunikat agenta {agent_id}: {message_type.value} - {content[:30]}...")
        return msg
    
    def add_event(
        self,
        event_id: str,
        agent_id: str,
        event_type: EventType,
        description: str = "",
        participants: Optional[List[str]] = None,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentEvent:
        """
        Dodaje zdarzenie agentowe.
        
        Args:
            event_id: Unikalny identyfikator zdarzenia
            agent_id: Identyfikator agenta
            event_type: Typ zdarzenia
            description: Opis zdarzenia
            participants: Lista uczestnikow
            timestamp: Data zdarzenia (domyslnie teraz)
            metadata: Dodatkowe metadane
            
        Returns:
            Utworzony AgentEvent
        """
        event = create_agent_event(event_id, agent_id, event_type)
        event.description = description
        if participants:
            event.participants.extend(participants)
        if timestamp:
            event.timestamp = timestamp
        if metadata:
            event.metadata.update(metadata)
        
        self._events.append(event)
        logger.debug(f"Dodano zdarzenie agenta {agent_id}: {event_type.value}")
        
        # Automatyczne sledzenie wspolpracy, konfliktow, sojuszow
        self._track_agent_relationships(event_type, event.participants)
        
        return event
    
    def _track_agent_relationships(self, event_type: EventType, participants: List[str]) -> None:
        """
        Sledzi relacje miedzy agentami na podstawie zdarzen.
        
        Args:
            event_type: Typ zdarzenia
            participants: Lista uczestnikow
        """
        if event_type == EventType.COLLABORATION_START:
            # Rozpoczecie wspolpracy
            if len(participants) >= 2:
                collab_key = ":".join(sorted(participants))
                if collab_key not in self._collaborations:
                    self._collaborations.append(collab_key)
                    logger.debug(f"Rozpoczeta wspolpraca: {collab_key}")
        
        elif event_type == EventType.COLLABORATION_END:
            # Zakonczenie wspolpracy
            if len(participants) >= 2:
                collab_key = ":".join(sorted(participants))
                if collab_key in self._collaborations:
                    self._collaborations.remove(collab_key)
                    logger.debug(f"Zakonczona wspolpraca: {collab_key}")
        
        elif event_type == EventType.CONFLICT:
            # Konflikt miedzy agentami
            if len(participants) >= 2:
                conflict_key = ":".join(sorted(participants))
                if conflict_key not in self._conflicts:
                    self._conflicts.append(conflict_key)
                    logger.debug(f"Konflikt: {conflict_key}")
        
        elif event_type == EventType.ALLIANCE:
            # Sojusz miedzy agentami
            if len(participants) >= 2:
                alliance_key = ":".join(sorted(participants))
                if alliance_key not in self._alliances:
                    self._alliances.append(alliance_key)
                    logger.debug(f"Sojusz: {alliance_key}")
    
    def add_collaboration(self, agent_ids: List[str]) -> None:
        """
        Dodaje rekod wspolpracy miedzy agentami.
        
        Args:
            agent_ids: Lista identyfikatorow agentow bioracych udzial
        """
        if len(agent_ids) >= 2:
            collab_key = ":".join(sorted(agent_ids))
            if collab_key not in self._collaborations:
                self._collaborations.append(collab_key)
                logger.debug(f"Dodano wspolprace: {collab_key}")
    
    def add_conflict(self, agent_ids: List[str]) -> None:
        """
        Dodaje rekod konfliktu miedzy agentami.
        
        Args:
            agent_ids: Lista identyfikatorow agentow bioracych udzial
        """
        if len(agent_ids) >= 2:
            conflict_key = ":".join(sorted(agent_ids))
            if conflict_key not in self._conflicts:
                self._conflicts.append(conflict_key)
                logger.debug(f"Dodano konflikt: {conflict_key}")
    
    def add_alliance(self, agent_ids: List[str]) -> None:
        """
        Dodaje rekod sojuszu miedzy agentami.
        
        Args:
            agent_ids: Lista identyfikatorow agentow bioracych udzial
        """
        if len(agent_ids) >= 2:
            alliance_key = ":".join(sorted(agent_ids))
            if alliance_key not in self._alliances:
                self._alliances.append(alliance_key)
                logger.debug(f"Dodano sojusz: {alliance_key}")
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Ustawia metadane.
        
        Args:
            key: Klucz metadanych
            value: Wartosc metadanych
        """
        self._metadata[key] = value
    
    def collect(self) -> AgentInputData:
        """
        Zbiera wszystkie zebrane dane i zwraca je jako AgentInputData.
        
        Returns:
            AgentInputData zawierajacy wszystkie zebrane dane
        """
        self._timestamp = datetime.now()
        self._status = ExternalStatus.COMPLETED
        
        # Jesli agent_id nie jest ustawiony, spróbuj go wywnioskowac
        primary_agent_id = self.agent_id
        if not primary_agent_id and self._messages:
            # Uzyj ID pierwszego agenta który wyslal komunikat
            primary_agent_id = self._messages[0].agent_id
        
        agent_data = AgentInputData(
            source_type=SourceType.AGENTS,
            agent_id=primary_agent_id,
            messages=self._messages.copy(),
            events=self._events.copy(),
            collaborations=self._collaborations.copy(),
            conflicts=self._conflicts.copy(),
            alliances=self._alliances.copy(),
            timestamp=self._timestamp,
            status=self._status,
            metadata=self._metadata.copy()
        )
        
        logger.info(f"Zebrano dane agentow: {len(agent_data.messages)} komunikatow, "
                    f"{len(agent_data.events)} zdarzen, "
                    f"{len(agent_data.collaborations)} wspolprac")
        
        return agent_data
    
    def clear(self) -> None:
        """Czysci zebrane dane."""
        self._messages.clear()
        self._events.clear()
        self._collaborations.clear()
        self._conflicts.clear()
        self._alliances.clear()
        self._status = ExternalStatus.PENDING
        self._timestamp = None
        self._metadata.clear()
        logger.info(f"Wyczyszczono dane agentow: {self.agent_id or 'multiple_agents'}")
    
    def get_status(self) -> ExternalStatus:
        """Zwraca aktualny status zrodla."""
        return self._status
    
    def set_status(self, status: ExternalStatus) -> None:
        """Ustawia status zrodla."""
        self._status = status
        logger.debug(f"Status AgentSource ustawiony na: {status}")
    
    def get_data_count(self) -> Dict[str, int]:
        """
        Zwraca liczbe zebranych elementow.
        
        Returns:
            Slownik z liczbami elementow
        """
        return {
            "messages": len(self._messages),
            "events": len(self._events),
            "collaborations": len(self._collaborations),
            "conflicts": len(self._conflicts),
            "alliances": len(self._alliances)
        }
    
    @property
    def has_data(self) -> bool:
        """Czy zrodlo ma jakiekolwiek dane?"""
        return bool(
            self._messages or
            self._events or
            self._collaborations or
            self._conflicts or
            self._alliances
        )
    
    def get_recent_messages(self, hours: int = 24) -> List[AgentMessage]:
        """
        Zwraca niedawne komunikaty.
        
        Args:
            hours: Liczba godzin wstecz
            
        Returns:
            Lista niedawnych komunikatow
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        return [msg for msg in self._messages if msg.timestamp >= cutoff]
    
    def get_messages_by_type(self, message_type: MessageType) -> List[AgentMessage]:
        """
        Zwraca komunikaty danego typu.
        
        Args:
            message_type: Typ komunikatow do filtrowania
            
        Returns:
            Lista komunikatow danego typu
        """
        return [msg for msg in self._messages if msg.message_type == message_type]
    
    def get_high_priority_messages(self, min_priority: int = 8) -> List[AgentMessage]:
        """
        Zwraca komunikaty o wysokim priorytecie.
        
        Args:
            min_priority: Minimalny priorytet
            
        Returns:
            Lista komunikatow o wysokim priorytecie
        """
        return [msg for msg in self._messages if msg.priority >= min_priority]
    
    def get_events_by_type(self, event_type: EventType) -> List[AgentEvent]:
        """
        Zwraca zdarzenia danego typu.
        
        Args:
            event_type: Typ zdarzen do filtrowania
            
        Returns:
            Lista zdarzen danego typu
        """
        return [evt for evt in self._events if evt.event_type == event_type]
    
    def get_messages_from_agent(self, agent_id: str) -> List[AgentMessage]:
        """
        Zwraca komunikaty od specyficznego agenta.
        
        Args:
            agent_id: Identyfikator agenta
            
        Returns:
            Lista komunikatow od agenta
        """
        return [msg for msg in self._messages if msg.agent_id == agent_id]
    
    def validate(self) -> bool:
        """
        Waliduje zebrane dane.
        
        Returns:
            True jeśli dane sa poprawne
        """
        # Sprawdz czy sa jakies dane
        if not self.has_data:
            logger.warning(f"Brak danych agentow: {self.agent_id or 'multiple_agents'}")
            self._status = ExternalStatus.INVALID
            return False
        
        # Sprawdz poprawnosc komunikatow
        for msg in self._messages:
            if not msg.agent_id:
                logger.error("Komunikat bez agent_id")
                self._status = ExternalStatus.INVALID
                return False
            if not 1 <= msg.priority <= 10:
                logger.error(f"Nieprawidlowy priorytet komunikatu: {msg.message_id}")
                self._status = ExternalStatus.INVALID
                return False
        
        # Sprawdz poprawnosc zdarzen
        for evt in self._events:
            if not evt.agent_id:
                logger.error("Zdarzenie bez agent_id")
                self._status = ExternalStatus.INVALID
                return False
        
        self._status = ExternalStatus.VALIDATED
        return True
    
    def get_agent_stats(self) -> Dict[str, Dict[str, int]]:
        """
        Zwraca statystyki dla kazdego agenta.
        
        Returns:
            Slownik ze statystykami na agente:
            {
                agent_id: {
                    "messages": int,
                    "events": int,
                    "collaborations": int,
                    "conflicts": int,
                    "alliances": int
                }
            }
        """
        stats = {}
        
        # Zlicz komunikaty i zdarzenia po agentach
        for msg in self._messages:
            if msg.agent_id not in stats:
                stats[msg.agent_id] = {"messages": 0, "events": 0, "collaborations": 0, "conflicts": 0, "alliances": 0}
            stats[msg.agent_id]["messages"] += 1
        
        for evt in self._events:
            if evt.agent_id not in stats:
                stats[evt.agent_id] = {"messages": 0, "events": 0, "collaborations": 0, "conflicts": 0, "alliances": 0}
            stats[evt.agent_id]["events"] += 1
        
        # Zlicz relacje (wspolpraca, konflikty, sojusze)
        for rel_list, rel_type in [
            (self._collaborations, "collaborations"),
            (self._conflicts, "conflicts"),
            (self._alliances, "alliances")
        ]:
            for key in rel_list:
                participants = key.split(":")
                for agent_id in participants:
                    if agent_id not in stats:
                        stats[agent_id] = {"messages": 0, "events": 0, "collaborations": 0, "conflicts": 0, "alliances": 0}
                    stats[agent_id][rel_type] += 1
        
        return stats
    
    def __repr__(self) -> str:
        counts = self.get_data_count()
        return (f"AgentSource(agent_id='{self.agent_id or 'multiple'}', "
                f"messages={counts['messages']}, "
                f"events={counts['events']}, "
                f"collaborations={counts['collaborations']})")
