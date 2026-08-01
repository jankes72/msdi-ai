"""
SSI V5 - Memory Types
Typy pamieci modeli

Zgodnie z dokumentacja:
- 04_AGENT_MEMORY_BEHAVIOR_EVOLUTION.md Sekcja: Model Memory Ecosystem

Definiuje 5 typow pamieci modeli:
1. Training Memory: Pamiec tresowania i uczenia
2. Observation Memory: Pamiec obserwacji systemu i agentow
3. Behavior Memory: Pamiec zachowan i wzorcow
4. Agent Analysis Memory: Pamiec analiz agentow
5. Decision Layer Memory: Pamiec podejmowanych decyzji
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum, auto
import json
import os


class TrainingPhase(Enum):
    """Fazy tresowania."""
    INITIAL = auto()      # Tresowanie poczatkowe
    CONTINUOUS = auto()   # Tresowanie ciagle
    FINE_TUNING = auto()  # Dostrajanie
    REINFORCEMENT = auto() # Uczenie ze wzmocnieniem


class ObservationScope(Enum):
    """Zakres obserwacji."""
    SYSTEM = auto()        # Obserwacja calego systemu
    AGENT = auto()         # Obserwacja pojedynczego agenta
    GROUP = auto()         # Obserwacja grupy agentow
    ENVIROMENT = auto()    # Obserwacja srodowiska


class BehaviorType(Enum):
    """Typy zachowan."""
    DECISION = auto()      # Zachowanie decyzyjne
    ANALYSIS = auto()       # Zachowanie analityczne
    CREATIVE = auto()      # Zachowanie kreatywne
    SOCIAL = auto()        # Zachowanie spoleczne
    LEARNING = auto()      # Zachowanie uczace


class AnalysisType(Enum):
    """Typy analiz agentow."""
    PERFORMANCE = auto()   # Analiza wydajnosci
    BEHAVIOR = auto()      # Analiza zachowania
    STRATEGY = auto()      # Analiza strategii
    COLLABORATION = auto() # Analiza wspolpracy
    EVOLUTION = auto()     # Analiza ewolucji


@dataclass
class TrainingMemory:
    """Pamiec tresowania.
    
    Przechowuje informacje o:
    - Sesjach tresowania
    - Uczych danych
    - Modelach i ich parametrach
    - Wynikach tresowania
    - Metrykach uczenia
    
    Uzywana przez:
    - Teacher Engine do uczenia modeli
    - Agenci do dostrajania swoich strategii
    """
    
    # Unikalne ID
    session_id: str
    
    # Informacje o sesji
    start_time: str
    end_time: Optional[str] = None
    duration_seconds: float = 0.0
    
    # Typ tresowania
    phase: TrainingPhase = TrainingPhase.CONTINUOUS
    method: str = "online_learning"
    
    # Dane tresowaniowe
    training_data_count: int = 0
    training_data_source: str = ""
    training_data_description: str = ""
    
    # Model
    model_name: str = "default"
    model_version: str = "1.0.0"
    model_parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Metryki
    initial_metrics: Dict[str, float] = field(default_factory=dict)
    final_metrics: Dict[str, float] = field(default_factory=dict)
    improvement: Dict[str, float] = field(default_factory=dict)
    
    # Wyniki
    success_rate: float = 0.0
    convergence_rate: float = 0.0
    validation_score: float = 0.0
    
    # Kontekst
    context: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        """Inicjalizacja po utworzeniu."""
        if self.end_time:
            try:
                start = datetime.fromisoformat(self.start_time)
                end = datetime.fromisoformat(self.end_time)
                self.duration_seconds = (end - start).total_seconds()
            except:
                self.duration_seconds = 0.0
    
    @property
    def is_complete(self) -> bool:
        """Czy sesja tresowania jest zakonczona."""
        return self.end_time is not None
    
    @property
    def training_improvement(self) -> float:
        """Srednia poprawa metryk."""
        if not self.improvement:
            return 0.0
        return sum(self.improvement.values()) / len(self.improvement)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        data = {
            "session_id": self.session_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": self.duration_seconds,
            "phase": self.phase.name,
            "method": self.method,
            "training_data_count": self.training_data_count,
            "training_data_source": self.training_data_source,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "model_parameters": self.model_parameters,
            "initial_metrics": self.initial_metrics,
            "final_metrics": self.final_metrics,
            "improvement": self.improvement,
            "success_rate": self.success_rate,
            "convergence_rate": self.convergence_rate,
            "validation_score": self.validation_score,
            "context": self.context,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrainingMemory':
        """Tworzenie z slownika."""
        return cls(
            session_id=data.get("session_id", ""),
            start_time=data.get("start_time", ""),
            end_time=data.get("end_time"),
            duration_seconds=data.get("duration_seconds", 0.0),
            phase=TrainingPhase[data.get("phase", "CONTINUOUS")],
            method=data.get("method", "online_learning"),
            training_data_count=data.get("training_data_count", 0),
            training_data_source=data.get("training_data_source", ""),
            training_data_description=data.get("training_data_description", ""),
            model_name=data.get("model_name", "default"),
            model_version=data.get("model_version", "1.0.0"),
            model_parameters=data.get("model_parameters", {}),
            initial_metrics=data.get("initial_metrics", {}),
            final_metrics=data.get("final_metrics", {}),
            improvement=data.get("improvement", {}),
            success_rate=data.get("success_rate", 0.0),
            convergence_rate=data.get("convergence_rate", 0.0),
            validation_score=data.get("validation_score", 0.0),
            context=data.get("context", {}),
            notes=data.get("notes", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", "")
        )


@dataclass
class ObservationMemory:
    """Pamiec obserwacji.
    
    Przechowuje informacje o:
    - Obserwacjach systemu
    - Zachowaniach agentow
    - Zdarzeniach
    - Wzorach
    - Anomaliach
    
    Uzywana przez:
    - Teacher Engine do monitorowania
    - Agenci do uczenia od innych
    - System do podejmowania decyzji
    """
    
    # Unikalne ID
    observation_id: str
    
    # Czas
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Zakres obserwacji
    scope: ObservationScope = ObservationScope.SYSTEM
    target_id: Optional[str] = None  # ID agenta/systemu/grupy
    
    # Typ obserwacji
    observation_type: str = "behavior"
    
    # Dane obserowane
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Analiza
    patterns_detected: List[str] = field(default_factory=list)
    anomalies_detected: List[str] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    
    # Metryki
    confidence: float = 0.0
    importance: float = 0.0
    novelty: float = 0.0
    
    # Kontekst
    context: Dict[str, Any] = field(default_factory=dict)
    related_observations: List[str] = field(default_factory=list)
    
    # Metadata
    source: str = "teacher_engine"
    validated: bool = False
    validation_notes: str = ""
    
    @property
    def scope_name(self) -> str:
        """Nazwa zakresu obserwacji."""
        return self.scope.name
    
    @property
    def has_anomalies(self) -> bool:
        """Czy wykryto anomalii."""
        return len(self.anomalies_detected) > 0
    
    @property
    def has_patterns(self) -> bool:
        """Czy wykryto wzorce."""
        return len(self.patterns_detected) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        return {
            "observation_id": self.observation_id,
            "timestamp": self.timestamp,
            "scope": self.scope.name,
            "target_id": self.target_id,
            "observation_type": self.observation_type,
            "data": self._sanitize_data(self.data),
            "patterns_detected": self.patterns_detected,
            "anomalies_detected": self.anomalies_detected,
            "insights": self.insights,
            "confidence": self.confidence,
            "importance": self.importance,
            "novelty": self.novelty,
            "context": self.context,
            "related_observations": self.related_observations,
            "source": self.source,
            "validated": self.validated,
            "validation_notes": self.validation_notes
        }
    
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanityzacja danych do serializacji."""
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            else:
                sanitized[key] = str(type(value))
        return sanitized
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ObservationMemory':
        """Tworzenie z slownika."""
        return cls(
            observation_id=data.get("observation_id", ""),
            timestamp=data.get("timestamp", ""),
            scope=ObservationScope[data.get("scope", "SYSTEM")],
            target_id=data.get("target_id"),
            observation_type=data.get("observation_type", "behavior"),
            data=data.get("data", {}),
            patterns_detected=data.get("patterns_detected", []),
            anomalies_detected=data.get("anomalies_detected", []),
            insights=data.get("insights", []),
            confidence=data.get("confidence", 0.0),
            importance=data.get("importance", 0.0),
            novelty=data.get("novelty", 0.0),
            context=data.get("context", {}),
            related_observations=data.get("related_observations", []),
            source=data.get("source", "teacher_engine"),
            validated=data.get("validated", False),
            validation_notes=data.get("validation_notes", "")
        )


@dataclass
class BehaviorMemory:
    """Pamiec zachowan.
    
    Przechowuje informacje o:
    - Wzorach zachowan
    - Reakcjach na sytuacje
    - Preferencjach
    - Nawiaskach
    - Adaptacjach
    
    Uzywana przez:
    - Teacher Engine do analizy zachowan
    - Agenci do uczenia sie wzorcow
    - System do przewidywania zachowan
    """
    
    # Unikalne ID
    behavior_id: str
    
    # Ogolne
    name: str = ""
    description: str = ""
    behavior_type: BehaviorType = BehaviorType.DECISION
    
    # Czas
    first_observed: str = field(default_factory=lambda: datetime.now().isoformat())
    last_observed: str = field(default_factory=lambda: datetime.now().isoformat())
    frequency: int = 1
    
    # Agenci
    agent_ids: List[str] = field(default_factory=list)
    group_ids: List[str] = field(default_factory=list)
    
    # Kontekst i wywoływanie
    trigger_conditions: List[Dict[str, Any]] = field(default_factory=list)
    trigger_probability: float = 0.0
    
    # Wyniki
    outcomes: List[Dict[str, Any]] = field(default_factory=list)
    success_rate: float = 0.0
    effectiveness: float = 0.0
    
    # ocena
    confidence: float = 0.0
    stability: float = 0.0  # 0 = zmienny, 1 = stabilny
    adaptability: float = 0.0  # 0 = sztywny, 1 = elastyczny
    
    # Metadane
    source: str = "observation"
    validated: bool = False
    validation_notes: str = ""
    
    @property
    def age_days(self) -> float:
        """Wiek zachowania w dniach."""
        try:
            first = datetime.fromisoformat(self.first_observed)
            now = datetime.now()
            return (now - first).total_seconds() / 86400
        except:
            return 0.0
    
    @property
    def is_recent(self) -> bool:
        """Czy zachowanie jest niedawne (< 7 dni)."""
        return self.age_days < 7
    
    @property
    def is_stable(self) -> bool:
        """Czy zachowanie jest stabilne."""
        return self.stability > 0.8 and self.frequency >= 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        return {
            "behavior_id": self.behavior_id,
            "name": self.name,
            "description": self.description,
            "behavior_type": self.behavior_type.name,
            "first_observed": self.first_observed,
            "last_observed": self.last_observed,
            "frequency": self.frequency,
            "agent_ids": self.agent_ids,
            "group_ids": self.group_ids,
            "trigger_conditions": self.trigger_conditions,
            "trigger_probability": self.trigger_probability,
            "outcomes": self.outcomes,
            "success_rate": self.success_rate,
            "effectiveness": self.effectiveness,
            "confidence": self.confidence,
            "stability": self.stability,
            "adaptability": self.adaptability,
            "source": self.source,
            "validated": self.validated,
            "validation_notes": self.validation_notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BehaviorMemory':
        """Tworzenie z slownika."""
        return cls(
            behavior_id=data.get("behavior_id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            behavior_type=BehaviorType[data.get("behavior_type", "DECISION")],
            first_observed=data.get("first_observed", ""),
            last_observed=data.get("last_observed", ""),
            frequency=data.get("frequency", 1),
            agent_ids=data.get("agent_ids", []),
            group_ids=data.get("group_ids", []),
            trigger_conditions=data.get("trigger_conditions", []),
            trigger_probability=data.get("trigger_probability", 0.0),
            outcomes=data.get("outcomes", []),
            success_rate=data.get("success_rate", 0.0),
            effectiveness=data.get("effectiveness", 0.0),
            confidence=data.get("confidence", 0.0),
            stability=data.get("stability", 0.0),
            adaptability=data.get("adaptability", 0.0),
            source=data.get("source", "observation"),
            validated=data.get("validated", False),
            validation_notes=data.get("validation_notes", "")
        )


@dataclass
class AgentAnalysisMemory:
    """Pamiec analiz agentow.
    
    Przechowuje informacje o:
    - Indywidualnych analizach agentow
    - Porownaniach miedzy agentami
    - Ocenach wydajnosci
    - Rekomendacjach
    
    Uzywana przez:
    - Teacher Engine do resterowania agentow
    - Agenci do uczenia sie od najlepszych
    - System do optymalizacji
    """
    
    # Unikalne ID
    analysis_id: str
    
    # Agent
    agent_id: str
    agent_name: str = ""
    agent_type: str = ""
    
    # Czas
    analysis_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    period_start: str = ""
    period_end: str = ""
    
    # Typ analizy
    analysis_type: AnalysisType = AnalysisType.PERFORMANCE
    
    # Dane analizy
    metrics: Dict[str, float] = field(default_factory=dict)
    performance_data: Dict[str, Any] = field(default_factory=dict)
    behavior_data: Dict[str, Any] = field(default_factory=dict)
    strategy_data: Dict[str, Any] = field(default_factory=dict)
    
    # Porownania
    comparisons: Dict[str, Dict[str, float]] = field(default_factory=dict)
    ranking: Dict[str, float] = field(default_factory=dict)
    
    # Oceny
    scores: Dict[str, float] = field(default_factory=dict)
    overall_score: float = 0.0
    grade: str = "C"  # A, B, C, D, E
    
    # Rekomendacje
    recommendations: List[str] = field(default_factory=list)
    improvement_areas: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    
    # Kontekst
    context: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""
    
    @property
    def grade_description(self) -> str:
        """Opis oceny."""
        grades = {
            "A": "Excellent",
            "B": "Good", 
            "C": "Average",
            "D": "Below Average",
            "E": "Poor"
        }
        return grades.get(self.grade, "Unknown")
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        return {
            "analysis_id": self.analysis_id,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "analysis_timestamp": self.analysis_timestamp,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "analysis_type": self.analysis_type.name,
            "metrics": self.metrics,
            "performance_data": self._sanitize_data(self.performance_data),
            "behavior_data": self._sanitize_data(self.behavior_data),
            "strategy_data": self._sanitize_data(self.strategy_data),
            "comparisons": self.comparisons,
            "ranking": self.ranking,
            "scores": self.scores,
            "overall_score": self.overall_score,
            "grade": self.grade,
            "recommendations": self.recommendations,
            "improvement_areas": self.improvement_areas,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "context": self.context,
            "notes": self.notes
        }
    
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanityzacja danych do serializacji."""
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, (str, int, float, bool, list, dict)):
                sanitized[key] = value
            else:
                sanitized[key] = str(type(value))
        return sanitized
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentAnalysisMemory':
        """Tworzenie z slownika."""
        return cls(
            analysis_id=data.get("analysis_id", ""),
            agent_id=data.get("agent_id", ""),
            agent_name=data.get("agent_name", ""),
            agent_type=data.get("agent_type", ""),
            analysis_timestamp=data.get("analysis_timestamp", ""),
            period_start=data.get("period_start", ""),
            period_end=data.get("period_end", ""),
            analysis_type=AnalysisType[data.get("analysis_type", "PERFORMANCE")],
            metrics=data.get("metrics", {}),
            performance_data=data.get("performance_data", {}),
            behavior_data=data.get("behavior_data", {}),
            strategy_data=data.get("strategy_data", {}),
            comparisons=data.get("comparisons", {}),
            ranking=data.get("ranking", {}),
            scores=data.get("scores", {}),
            overall_score=data.get("overall_score", 0.0),
            grade=data.get("grade", "C"),
            recommendations=data.get("recommendations", []),
            improvement_areas=data.get("improvement_areas", []),
            strengths=data.get("strengths", []),
            weaknesses=data.get("weaknesses", []),
            context=data.get("context", {}),
            notes=data.get("notes", "")
        )


@dataclass
class DecisionMemory:
    """Pamiec podejmowanych decyzji.
    
    Przechowuje informacje o:
    - Podjetych decyzjach
    - Kontekcie decyzji
    - geeignet skutkach
    - Uczeniu sie z decyzji
    
    Uzywana przez:
    - Decision Layer do podejmowania lepszych decyzji
    - Teacher Engine do oceniania decyzji
    - Agenci do uczenia sie
    """
    
    # Unikalne ID
    decision_id: str
    
    # Ogolne
    description: str = ""
    decision_type: str = "strategy_selection"
    
    # Czas
    made_at: str = field(default_factory=lambda: datetime.now().isoformat())
    executed_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    # Kontekst
    context: Dict[str, Any] = field(default_factory=dict)
    agent_id: Optional[str] = None
    cycle_number: Optional[int] = None
    
    # Decyzja
    decision: Any = None  # Moze byc dowolnego typu (str, dict, itp.)
    decision_json: str = ""
    
    # Alternatywy
    alternatives_considered: List[Any] = field(default_factory=list)
    alternatives_json: List[str] = field(default_factory=list)
    
    # Prawdopodobieństwa
    confidence: float = 0.0
    probabilities: Dict[str, float] = field(default_factory=dict)
    
    # Skutki
    outcomes: List[Dict[str, Any]] = field(default_factory=list)
    expected_outcomes: List[Dict[str, float]] = field(default_factory=list)
    actual_outcomes: List[Dict[str, float]] = field(default_factory=list)
    
    # Ocena
    success: bool = True
    score: float = 0.0
    evaluation: str = ""
    lessons_learned: List[str] = field(default_factory=list)
    
    # Strategia
    strategy_used: Optional[str] = None
    strategy_effectiveness: float = 0.0
    
    # metadata
    source: str = "agent"
    validated: bool = False
    
    def __post_init__(self):
        """Inicjalizacja po utworzeniu."""
        # Serializacja decyzji
        if self.decision is not None:
            try:
                if isinstance(self.decision, (str, int, float, bool)):
                    self.decision_json = str(self.decision)
                else:
                    self.decision_json = json.dumps(self.decision, default=str)
            except:
                self.decision_json = ""
    
    @property
    def execution_time_seconds(self) -> float:
        """Czas wykonania decyzji w sekundach."""
        if self.executed_at and self.completed_at:
            try:
                exec_time = datetime.fromisoformat(self.executed_at)
                comp_time = datetime.fromisoformat(self.completed_at)
                return (comp_time - exec_time).total_seconds()
            except:
                return 0.0
        return 0.0
    
    @property
    def outcome_accuracy(self) -> float:
        """Dokladnosc przewidywanych skutkow."""
        if not self.expected_outcomes or not self.actual_outcomes:
            return 0.0
        
        # Porownanie oczekiwanych i rzeczywistych skutkow
        matches = 0
        total = 0
        
        for expected in self.expected_outcomes:
            for actual in self.actual_outcomes:
                # Uproszczone porownanie
                if expected.get("type") == actual.get("type"):
                    matches += 1
                    total += 1
                else:
                    total += 1
        
        return matches / total if total > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        return {
            "decision_id": self.decision_id,
            "description": self.description,
            "decision_type": self.decision_type,
            "made_at": self.made_at,
            "executed_at": self.executed_at,
            "completed_at": self.completed_at,
            "context": self._sanitize_context(self.context),
            "agent_id": self.agent_id,
            "cycle_number": self.cycle_number,
            "decision": self.decision,
            "decision_json": self.decision_json,
            "alternatives_considered": [str(a) for a in self.alternatives_considered],
            "confidence": self.confidence,
            "probabilities": self.probabilities,
            "outcomes": self.outcomes,
            "expected_outcomes": self.expected_outcomes,
            "actual_outcomes": self.actual_outcomes,
            "success": self.success,
            "score": self.score,
            "evaluation": self.evaluation,
            "lessons_learned": self.lessons_learned,
            "strategy_used": self.strategy_used,
            "strategy_effectiveness": self.strategy_effectiveness,
            "source": self.source,
            "validated": self.validated
        }
    
    def _sanitize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Sanityzacja kontekstu."""
        sanitized = {}
        for key, value in context.items():
            try:
                if isinstance(value, (str, int, float, bool, list, dict)):
                    sanitized[key] = value
                else:
                    sanitized[key] = str(value)
            except:
                sanitized[key] = "<unserializable>"
        return sanitized
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DecisionMemory':
        """Tworzenie z slownika."""
        decision = data.get("decision")
        try:
            if isinstance(decision, str):
                decision = json.loads(decision)
        except:
            pass
        
        return cls(
            decision_id=data.get("decision_id", ""),
            description=data.get("description", ""),
            decision_type=data.get("decision_type", "strategy_selection"),
            made_at=data.get("made_at", ""),
            executed_at=data.get("executed_at"),
            completed_at=data.get("completed_at"),
            context=data.get("context", {}),
            agent_id=data.get("agent_id"),
            cycle_number=data.get("cycle_number"),
            decision=decision,
            decision_json=data.get("decision_json", ""),
            confidence=data.get("confidence", 0.0),
            probabilities=data.get("probabilities", {}),
            outcomes=data.get("outcomes", []),
            expected_outcomes=data.get("expected_outcomes", []),
            actual_outcomes=data.get("actual_outcomes", []),
            success=data.get("success", True),
            score=data.get("score", 0.0),
            evaluation=data.get("evaluation", ""),
            lessons_learned=data.get("lessons_learned", []),
            strategy_used=data.get("strategy_used"),
            strategy_effectiveness=data.get("strategy_effectiveness", 0.0),
            source=data.get("source", "agent"),
            validated=data.get("validated", False)
        )
