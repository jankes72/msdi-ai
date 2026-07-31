"""
SSI V5 - External Input Layer - Data Models
Modele danych dla zewnetrznych zrodel wiedzy

Odpowiedzialnosc:
- Definicja struktur danych od programisty
- Definicja struktur danych z laboratoriow
- Definicja struktur danych od agentow
- Definicja struktur danych systemowych
- Pakowanie danych w ExternalDataPackage

Wersja: 1.0
Data: 2026-07-31
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

from .source_types import SourceType, LaboratoryType, ExternalStatus


# ============================================================================
# DEVELOPER MODELE - Dane od programisty
# ============================================================================

@dataclass
class DeveloperCommand:
    """
    Polecenie od programisty.
    
    Attributes:
        command_id: Unikalny identyfikator polecenia
        command: Tresc polecenia
        priority: Priorytet polecenia (1-10, 10 = najwyzszy)
        timestamp: Data i godzina stworzenia
        metadata: Dodatkowe metadane
    """
    command_id: str
    command: str
    priority: int = 5
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not 1 <= self.priority <= 10:
            raise ValueError("Priority must be between 1 and 10")


@dataclass
class Requirement:
    """
    Wymaganie systemowe od programisty.
    
    Attributes:
        requirement_id: Unikalny identyfikator wymagania
        title: Tytul wymagania
        description: Opis wymagania
        category: Kategoria wymagania (np. "functionality", "performance", "security")
        priority: Priorytet
        status: Status realizacji
        deadline: Termin realizacji
        depends_on: Zaleznosci miedzy wymaganiami
        metadata: Dodatkowe metadane
    """
    requirement_id: str
    title: str
    description: str
    category: str = "functionality"
    priority: int = 5
    status: str = "pending"  # pending, in_progress, completed, cancelled
    deadline: Optional[datetime] = None
    depends_on: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ArchitectureDecision:
    """
    Decyzja architektoniczna podjeta przez programiste.
    
    Attributes:
        decision_id: Unikalny identyfikator decyzji
        title: Tytul decyzji
        description: Opis decyzji
        rationale: Uzasadnienie decyzji
        impact: Wplyw na system
        alternatives: Rozpatrywane alternatywy
        status: Status decyzji
        timestamp: Data podjecia decyzji
        metadata: Dodatkowe metadane
    """
    decision_id: str
    title: str
    description: str
    rationale: str = ""
    impact: str = ""
    alternatives: List[str] = field(default_factory=list)
    status: str = "active"  # active, deprecated, superseded
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeveloperInput:
    """
    Pakiet danych od programisty.
    
    Attributes:
        developer_id: Identyfikator programisty
        source_type: Typ zrodla (DEVELOPER)
        commands: Lista polecen
        requirements: Lista wymagan
        decisions: Lista decyzji architektonicznych
        analysis_requests: Zadania analizy systemu
        change_history: Historia zmian
        timestamp: Data zebrania danych
        status: Status zebrania
        metadata: Dodatkowe metadane
    """
    developer_id: str
    source_type: SourceType = SourceType.DEVELOPER
    commands: List[DeveloperCommand] = field(default_factory=list)
    requirements: List[Requirement] = field(default_factory=list)
    decisions: List[ArchitectureDecision] = field(default_factory=list)
    analysis_requests: List[str] = field(default_factory=list)
    change_history: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    status: ExternalStatus = ExternalStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_command(self, command: DeveloperCommand) -> None:
        """Dodaje polecenie do pakietu."""
        self.commands.append(command)
    
    def add_requirement(self, requirement: Requirement) -> None:
        """Dodaje wymaganie do pakietu."""
        self.requirements.append(requirement)
    
    def add_decision(self, decision: ArchitectureDecision) -> None:
        """Dodaje decyzje do pakietu."""
        self.decisions.append(decision)
    
    def get_high_priority_items(self, min_priority: int = 8) -> List[Union[DeveloperCommand, Requirement]]:
        """Zwraca elementy o wysokim priorytecie."""
        high_priority = []
        for cmd in self.commands:
            if cmd.priority >= min_priority:
                high_priority.append(cmd)
        for req in self.requirements:
            if req.priority >= min_priority:
                high_priority.append(req)
        return high_priority


# ============================================================================
# LABORATORY MODELE - Dane z laboratoriow
# ============================================================================

@dataclass
class ExperimentResult:
    """
    Wynik eksperymentu z laboratorium.
    
    Attributes:
        experiment_id: Unikalny identyfikator eksperymentu
        laboratory_type: Typ laboratorium
        title: Tytul eksperymentu
        hypothesis: Hipoteza testowana w eksperymencie
        methodology: Metodologia eksperymentu
        data: Dane zebrane podczas eksperymentu
        results: Wyniki eksperymentu
        conclusions: Wnioski
        success: Czy eksperyment sie powiodl
        timestamp: Data wykonania
        metadata: Dodatkowe metadane
    """
    experiment_id: str
    laboratory_type: LaboratoryType
    title: str
    hypothesis: str = ""
    methodology: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    conclusions: List[str] = field(default_factory=list)
    success: bool = True
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DiscoveryRecord:
    """
    Rekord odkrycia naukowego/technicznego.
    
    Attributes:
        discovery_id: Unikalny identyfikator odkrycia
        laboratory_type: Typ laboratorium
        title: Tytul odkrycia
        description: Opis odkrycia
        category: Kategoria odkrycia
        impact: Wplyw na system
        evidence: Dowody na poparcie odkrycia
        related_experiments: Powiazane eksperymenty
        timestamp: Data odkrycia
        metadata: Dodatkowe metadane
    """
    discovery_id: str
    laboratory_type: LaboratoryType
    title: str
    description: str
    category: str = "scientific"
    impact: str = ""
    evidence: List[Any] = field(default_factory=list)
    related_experiments: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LaboratoryData:
    """
    Pakiet danych z laboratoriow.
    
    Attributes:
        lab_id: Identyfikator laboratorium
        source_type: Typ zrodla (LABORATORIES)
        laboratory_type: Typ laboratorium
        experiments: Lista eksperymentow
        discoveries: Lista odkryc
        active_research: Aktualne badania
        completed_research: Zakonczone badania
        timestamp: Data zebrania danych
        status: Status zebrania
        metadata: Dodatkowe metadane
    """
    lab_id: str
    source_type: SourceType = SourceType.LABORATORIES
    laboratory_type: LaboratoryType = LaboratoryType.WORLD_LAB
    experiments: List[ExperimentResult] = field(default_factory=list)
    discoveries: List[DiscoveryRecord] = field(default_factory=list)
    active_research: List[str] = field(default_factory=list)
    completed_research: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    status: ExternalStatus = ExternalStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_experiment(self, experiment: ExperimentResult) -> None:
        """Dodaje eksperyment do pakietu."""
        self.experiments.append(experiment)
    
    def add_discovery(self, discovery: DiscoveryRecord) -> None:
        """Dodaje odkrycie do pakietu."""
        self.discoveries.append(discovery)
    
    def get_recent_experiments(self, days: int = 7) -> List[ExperimentResult]:
        """Zwraca niedawne eksperymenty."""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        return [exp for exp in self.experiments if exp.timestamp >= cutoff]
    
    def get_successful_experiments(self) -> List[ExperimentResult]:
        """Zwraca udane eksperymenty."""
        return [exp for exp in self.experiments if exp.success]


# ============================================================================
# AGENT MODELE - Dane od agentow
# ============================================================================

class MessageType(Enum):
    """Typy komunikatow od agentow."""
    COMMAND = "command"
    QUESTION = "question"
    INFORMATION = "information"
    WARNING = "warning"
    ERROR = "error"
    COLLABORATION = "collaboration"
    DECISION = "decision"


class EventType(Enum):
    """Typy zdarzen agentowych."""
    CREATED = "created"
    ACTIVATED = "activated"
    DEACTIVATED = "deactivated"
    STATE_CHANGE = "state_change"
    STRATEGY_CHANGE = "strategy_change"
    COLLABORATION_START = "collaboration_start"
    COLLABORATION_END = "collaboration_end"
    CONFLICT = "conflict"
    ALLIANCE = "alliance"


@dataclass
class AgentMessage:
    """
    Komunikat od agenta.
    
    Attributes:
        message_id: Unikalny identyfikator komunikat
        agent_id: Identyfikator agenta
        message_type: Typ komunikatu
        content: Tresc komunikatu
        recipient: Odbiorca (None = broadcast)
        priority: Priorytet
        timestamp: Data wyslania
        metadata: Dodatkowe metadane
    """
    message_id: str
    agent_id: str
    message_type: MessageType = MessageType.INFORMATION
    content: str = ""
    recipient: Optional[str] = None
    priority: int = 5
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentEvent:
    """
    Zdarzenie zwiazane z agentem.
    
    Attributes:
        event_id: Unikalny identyfikator zdarzenia
        agent_id: Identyfikator agenta
        event_type: Typ zdarzenia
        description: Opis zdarzenia
        participants: Uczestnicy zdarzenia
        timestamp: Data zdarzenia
        metadata: Dodatkowe metadane
    """
    event_id: str
    agent_id: str
    event_type: EventType
    description: str = ""
    participants: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentInputData:
    """
    Pakiet danych od agentow.
    
    Attributes:
        source_type: Typ zrodla (AGENTS)
        agent_id: Identyfikator agenta (opcjonalnie)
        messages: Lista komunikatow
        events: Lista zdarzen
        collaborations: Lista wspolprac
        conflicts: Lista konfliktow
        alliances: Lista sojuszy
        timestamp: Data zebrania danych
        status: Status zebrania
        metadata: Dodatkowe metadane
    """
    source_type: SourceType = SourceType.AGENTS
    agent_id: Optional[str] = None
    messages: List[AgentMessage] = field(default_factory=list)
    events: List[AgentEvent] = field(default_factory=list)
    collaborations: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    alliances: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    status: ExternalStatus = ExternalStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, message: AgentMessage) -> None:
        """Dodaje komunikat do pakietu."""
        self.messages.append(message)
    
    def add_event(self, event: AgentEvent) -> None:
        """Dodaje zdarzenie do pakietu."""
        self.events.append(event)
    
    def get_recent_messages(self, hours: int = 24) -> List[AgentMessage]:
        """Zwraca niedawne komunikaty."""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(hours=hours)
        return [msg for msg in self.messages if msg.timestamp >= cutoff]
    
    def get_high_priority_messages(self, min_priority: int = 8) -> List[AgentMessage]:
        """Zwraca komunikaty o wysokim priorytecie."""
        return [msg for msg in self.messages if msg.priority >= min_priority]


# ============================================================================
# SYSTEM MODELE - Dane systemowe
# ============================================================================

class LogLevel(Enum):
    """Poziomy logow systemowych."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SystemStatusType(Enum):
    """Typy statusow systemowych."""
    STARTUP = "startup"
    SHUTDOWN = "shutdown"
    READY = "ready"
    BUSY = "busy"
    ERROR_STATE = "error_state"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


@dataclass
class SystemEvent:
    """
    Zdarzenie systemowe.
    
    Attributes:
        event_id: Unikalny identyfikator zdarzenia
        event_type: Typ zdarzenia
        component: Komponent systemu
        message: Tresc zdarzenia
        log_level: Poziom logu
        timestamp: Data zdarzenia
        metadata: Dodatkowe metadane
    """
    event_id: str
    event_type: str
    component: str
    message: str
    log_level: LogLevel = LogLevel.INFO
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemStatus:
    """
    Status systemu.
    
    Attributes:
        status_id: Unikalny identyfikator statusu
        status_type: Typ statusu
        message: Tresc statusu
        component: Komponent (opcjonalnie)
        timestamp: Data statusu
        metadata: Dodatkowe metadane
    """
    status_id: str
    status_type: SystemStatusType = SystemStatusType.UNKNOWN
    message: str = ""
    component: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemMessages:
    """
    Pakiet komunikatow systemowych.
    
    Attributes:
        source_type: Typ zrodla (SYSTEM)
        events: Lista zdarzen systemowych
        statuses: Lista statusow systemowych
        logs: Lista logow
        timestamp: Data zebrania danych
        status: Status zebrania
        metadata: Dodatkowe metadane
    """
    source_type: SourceType = SourceType.SYSTEM
    events: List[SystemEvent] = field(default_factory=list)
    statuses: List[SystemStatus] = field(default_factory=list)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    status: ExternalStatus = ExternalStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_event(self, event: SystemEvent) -> None:
        """Dodaje zdarzenie do pakietu."""
        self.events.append(event)
    
    def add_status(self, status: SystemStatus) -> None:
        """Dodaje status do pakietu."""
        self.statuses.append(status)
    
    def add_log(self, log: Dict[str, Any]) -> None:
        """Dodaje log do pakietu."""
        self.logs.append(log)
    
    def get_errors(self) -> List[Union[SystemEvent, SystemStatus]]:
        """Zwraca bledy i zdarzenia krytyczne."""
        errors = []
        for event in self.events:
            if event.log_level in [LogLevel.ERROR, LogLevel.CRITICAL]:
                errors.append(event)
        for status in self.statuses:
            if status.status_type == SystemStatusType.ERROR_STATE:
                errors.append(status)
        return errors


# ============================================================================
# EXTERNAL DATA PACKAGE - Glowny pakiet danych zewnetrznych
# ============================================================================

@dataclass
class ExternalDataPackage:
    """
    Glowny pakiet agregujacy wszystkie dane zewnetrzne.
    
    Attributes:
        package_id: Unikalny identyfikator pakietu
        developer_data: Dane od programisty
        laboratory_data: Dane z laboratoriow
        agent_data: Dane od agentow
        system_data: Dane systemowe
        timestamp: Data utworzenia pakietu
        status: Status pakietu
        validation_results: Wyniki walidacji
        metadata: Dodatkowe metadane
    """
    package_id: str = field(default_factory=lambda: f"external_package_{datetime.now().strftime('%Y%m%d%H%M%S')}")
    developer_data: Optional[DeveloperInput] = None
    laboratory_data: List[LaboratoryData] = field(default_factory=list)
    agent_data: List[AgentInputData] = field(default_factory=list)
    system_data: Optional[SystemMessages] = None
    timestamp: datetime = field(default_factory=datetime.now)
    status: ExternalStatus = ExternalStatus.PENDING
    validation_results: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_developer_data(self, data: DeveloperInput) -> None:
        """Dodaje dane od programisty."""
        self.developer_data = data
    
    def add_laboratory_data(self, data: LaboratoryData) -> None:
        """Dodaje dane z laboratorium."""
        self.laboratory_data.append(data)
    
    def add_agent_data(self, data: AgentInputData) -> None:
        """Dodaje dane od agentow."""
        self.agent_data.append(data)
    
    def add_system_data(self, data: SystemMessages) -> None:
        """Dodaje dane systemowe."""
        self.system_data = data
    
    def set_status(self, status: ExternalStatus) -> None:
        """Ustawia status pakietu."""
        self.status = status
    
    def add_validation_result(self, source_type: str, result: Any) -> None:
        """Dodaje wynik walidacji."""
        self.validation_results[source_type] = result
    
    def get_all_data_count(self) -> Dict[str, int]:
        """Zwraca liczbe elementow w kazdej sekcji."""
        counts = {
            "developer_commands": len(self.developer_data.commands) if self.developer_data else 0,
            "developer_requirements": len(self.developer_data.requirements) if self.developer_data else 0,
            "developer_decisions": len(self.developer_data.decisions) if self.developer_data else 0,
            "laboratory_experiments": sum(len(lab.experiments) for lab in self.laboratory_data),
            "laboratory_discoveries": sum(len(lab.discoveries) for lab in self.laboratory_data),
            "agent_messages": sum(len(agent.messages) for agent in self.agent_data),
            "agent_events": sum(len(agent.events) for agent in self.agent_data),
            "system_events": len(self.system_data.events) if self.system_data else 0,
            "system_statuses": len(self.system_data.statuses) if self.system_data else 0
        }
        return counts
    
    def get_source_types_present(self) -> List[SourceType]:
        """Zwraca liste obecnych typow zrodel."""
        source_types = []
        if self.developer_data:
            source_types.append(SourceType.DEVELOPER)
        if self.laboratory_data:
            source_types.append(SourceType.LABORATORIES)
        if self.agent_data:
            source_types.append(SourceType.AGENTS)
        if self.system_data:
            source_types.append(SourceType.SYSTEM)
        return source_types
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje pakiet do slownika (dla serializacji)."""
        result = {
            "package_id": self.package_id,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.name,
            "metadata": self.metadata,
            "validation_results": self.validation_results,
            "data_counts": self.get_all_data_count()
        }
        
        if self.developer_data:
            result["developer_data"] = {
                "commands_count": len(self.developer_data.commands),
                "requirements_count": len(self.developer_data.requirements),
                "decisions_count": len(self.developer_data.decisions)
            }
        
        if self.laboratory_data:
            result["laboratory_data"] = [
                {
                    "lab_id": lab.lab_id,
                    "laboratory_type": lab.laboratory_type.value,
                    "experiments_count": len(lab.experiments),
                    "discoveries_count": len(lab.discoveries)
                }
                for lab in self.laboratory_data
            ]
        
        if self.agent_data:
            result["agent_data"] = [
                {
                    "agent_id": agent.agent_id,
                    "messages_count": len(agent.messages),
                    "events_count": len(agent.events)
                }
                for agent in self.agent_data
            ]
        
        if self.system_data:
            result["system_data"] = {
                "events_count": len(self.system_data.events),
                "statuses_count": len(self.system_data.statuses),
                "logs_count": len(self.system_data.logs)
            }
        
        return result


# ============================================================================
# FABRYKI I FUNKCJE POMOCNICZE
# ============================================================================

def create_developer_command(command_id: str, command: str, priority: int = 5) -> DeveloperCommand:
    """Tworzy nowy DeveloperCommand."""
    return DeveloperCommand(command_id=command_id, command=command, priority=priority)


def create_requirement(requirement_id: str, title: str, description: str, priority: int = 5) -> Requirement:
    """Tworzy nowy Requirement."""
    return Requirement(
        requirement_id=requirement_id,
        title=title,
        description=description,
        priority=priority
    )


def create_architecture_decision(decision_id: str, title: str, description: str) -> ArchitectureDecision:
    """Tworzy nowy ArchitectureDecision."""
    return ArchitectureDecision(
        decision_id=decision_id,
        title=title,
        description=description
    )


def create_experiment_result(
    experiment_id: str,
    laboratory_type: LaboratoryType,
    title: str,
    hypothesis: str = "",
    success: bool = True
) -> ExperimentResult:
    """Tworzy nowy ExperimentResult."""
    return ExperimentResult(
        experiment_id=experiment_id,
        laboratory_type=laboratory_type,
        title=title,
        hypothesis=hypothesis,
        success=success
    )


def create_discovery_record(
    discovery_id: str,
    laboratory_type: LaboratoryType,
    title: str,
    description: str
) -> DiscoveryRecord:
    """Tworzy nowy DiscoveryRecord."""
    return DiscoveryRecord(
        discovery_id=discovery_id,
        laboratory_type=laboratory_type,
        title=title,
        description=description
    )


def create_agent_message(
    message_id: str,
    agent_id: str,
    content: str,
    message_type: MessageType = MessageType.INFORMATION
) -> AgentMessage:
    """Tworzy nowy AgentMessage."""
    return AgentMessage(
        message_id=message_id,
        agent_id=agent_id,
        content=content,
        message_type=message_type
    )


def create_agent_event(
    event_id: str,
    agent_id: str,
    event_type: EventType
) -> AgentEvent:
    """Tworzy nowy AgentEvent."""
    return AgentEvent(
        event_id=event_id,
        agent_id=agent_id,
        event_type=event_type
    )


def create_system_event(
    event_id: str,
    event_type: str,
    component: str,
    message: str,
    log_level: LogLevel = LogLevel.INFO
) -> SystemEvent:
    """Tworzy nowy SystemEvent."""
    return SystemEvent(
        event_id=event_id,
        event_type=event_type,
        component=component,
        message=message,
        log_level=log_level
    )


def create_system_status(
    status_id: str,
    status_type: SystemStatusType,
    message: str = "",
    component: Optional[str] = None
) -> SystemStatus:
    """Tworzy nowy SystemStatus."""
    return SystemStatus(
        status_id=status_id,
        status_type=status_type,
        message=message,
        component=component
    )


def create_external_package() -> ExternalDataPackage:
    """Tworzy nowy ExternalDataPackage z unikalnym ID."""
    return ExternalDataPackage()
