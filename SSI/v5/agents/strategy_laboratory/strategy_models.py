"""
SSI V5 - Strategy Models

Modul zawiera modele danych dla strategii agentów w Strategy Laboratory.

Każda strategia musi posiadać:
- strategy_id
- agent_owner
- version
- creation_date
- parameters
- description
- usage_count
- success_count
- failure_count
- success_rate
- confidence
- ranking_score
- last_evaluation

Wersja: 1.0.0
Data: 2026-08-01
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Union
import uuid
import json
import os


class StrategyStatus(Enum):
    """Status strategii."""
    DRAFT = auto()           # W przygotowaniu
    TESTING = auto()         # W trakcie testowania
    ACTIVE = auto()          # Aktywna, gotowa do użycia
    ARCHIVED = auto()        # Zawieszona/archiwalna
    DEPRECATED = auto()      # Przestarzała


class StrategyVersion(Enum):
    """Wersja strategii."""
    ALPHA = "0.1"           # Wstępna wersja testowa
    BETA = "0.5"            # Testowana przez agenta
    RELEASE_CANDIDATE = "1.0-rc"  # Kandydat do produkcji
    STABLE = "1.0"          # Stabilna wersja
    OPTIMIZED = "2.0"       # Zoptymalizowana


class StrategyType(Enum):
    """Typ strategii."""
    DECISION = auto()        # Strategia decyzyjna
    ANALYSIS = auto()        # Strategia analityczna
    PREDICTION = auto()      # Strategia predykcyjna
    LEARNING = auto()        # Strategia ucząca
    COLLABORATION = auto()   # Strategia współpracy
    OPTIMIZATION = auto()    # Strategia optymalizacyjna
    EXPERIMENTAL = auto()    # Strategia eksperymentalna


@dataclass
class StrategyParameters:
    """Parametry strategii."""
    
    # Parametry ogólne
    strategy_type: StrategyType = StrategyType.DECISION
    risk_level: float = 0.5  # Poziom ryzyka (0.0 - 1.0)
    confidence_threshold: float = 0.7  # Próg pewności do akceptacji
    learning_rate: float = 0.1  # Współczynnik uczenia
    
    # Parametry decyzyjne
    decision_threshold: float = 0.6
    max_decision_time: float = 2.0  # Maksymalny czas decyzji w sekundach
    consider_alternatives: bool = True
    
    # Parametry analityczne
    analysis_depth: int = 3  # Głębokość analizy
    data_sources: List[str] = field(default_factory=lambda: ["memory", "context"])
    use_historical_data: bool = True
    
    # Parametry predykcyjne
    prediction_horizon: int = 5  # Horyzont predykcji
    confidence_required: float = 0.8
    use_ensemble: bool = False
    
    # Parametry eksperymentalne
    experiment_iterations: int = 10
    success_threshold: float = 0.75
    allow_failure: bool = True
    
    # Dodatkowe parametry specyficzne dla strategii
    custom_parameters: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika."""
        return {
            'strategy_type': self.strategy_type.name,
            'risk_level': self.risk_level,
            'confidence_threshold': self.confidence_threshold,
            'learning_rate': self.learning_rate,
            'decision_threshold': self.decision_threshold,
            'max_decision_time': self.max_decision_time,
            'consider_alternatives': self.consider_alternatives,
            'analysis_depth': self.analysis_depth,
            'data_sources': self.data_sources,
            'use_historical_data': self.use_historical_data,
            'prediction_horizon': self.prediction_horizon,
            'confidence_required': self.confidence_required,
            'use_ensemble': self.use_ensemble,
            'experiment_iterations': self.experiment_iterations,
            'success_threshold': self.success_threshold,
            'allow_failure': self.allow_failure,
            'custom_parameters': self.custom_parameters
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StrategyParameters':
        """Tworzenie z słownika."""
        return cls(
            strategy_type=StrategyType[data.get('strategy_type', 'DECISION')],
            risk_level=data.get('risk_level', 0.5),
            confidence_threshold=data.get('confidence_threshold', 0.7),
            learning_rate=data.get('learning_rate', 0.1),
            decision_threshold=data.get('decision_threshold', 0.6),
            max_decision_time=data.get('max_decision_time', 2.0),
            consider_alternatives=data.get('consider_alternatives', True),
            analysis_depth=data.get('analysis_depth', 3),
            data_sources=data.get('data_sources', ["memory", "context"]),
            use_historical_data=data.get('use_historical_data', True),
            prediction_horizon=data.get('prediction_horizon', 5),
            confidence_required=data.get('confidence_required', 0.8),
            use_ensemble=data.get('use_ensemble', False),
            experiment_iterations=data.get('experiment_iterations', 10),
            success_threshold=data.get('success_threshold', 0.75),
            allow_failure=data.get('allow_failure', True),
            custom_parameters=data.get('custom_parameters', {})
        )
    
    def validate(self) -> bool:
        """Walidacja parametrów."""
        if not 0.0 <= self.risk_level <= 1.0:
            return False
        if not 0.0 <= self.confidence_threshold <= 1.0:
            return False
        if not 0.0 <= self.learning_rate <= 1.0:
            return False
        if self.analysis_depth < 1 or self.analysis_depth > 10:
            return False
        if self.prediction_horizon < 1:
            return False
        if self.experiment_iterations < 1:
            return False
        return True


@dataclass
class StrategyResult:
    """Wynik wykonania strategii."""
    
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    strategy_id: str = ""
    execution_timestamp: datetime = field(default_factory=datetime.now)
    
    # Wynik
    success: bool = False
    outcome: str = ""
    score: float = 0.0  # Wynik numeryczny (0.0 - 1.0)
    confidence: float = 0.0  # Pewność wyniku
    
    # Metryki
    execution_time_ms: float = 0.0
    resources_used: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    
    # Kontekst
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def calculate_success_score(self) -> float:
        """Obliczenie ogólnego wyniku sukcesu."""
        if self.success:
            return self.score * self.confidence
        else:
            return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika."""
        return {
            'result_id': self.result_id,
            'strategy_id': self.strategy_id,
            'execution_timestamp': self.execution_timestamp.isoformat(),
            'success': self.success,
            'outcome': self.outcome,
            'score': self.score,
            'confidence': self.confidence,
            'execution_time_ms': self.execution_time_ms,
            'resources_used': self.resources_used,
            'metrics': self.metrics,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'errors': self.errors,
            'warnings': self.warnings,
            'success_score': self.calculate_success_score()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StrategyResult':
        """Tworzenie z słownika."""
        return cls(
            result_id=data.get('result_id', str(uuid.uuid4())),
            strategy_id=data.get('strategy_id', ""),
            execution_timestamp=datetime.fromisoformat(data.get('execution_timestamp', datetime.now().isoformat())),
            success=data.get('success', False),
            outcome=data.get('outcome', ""),
            score=data.get('score', 0.0),
            confidence=data.get('confidence', 0.0),
            execution_time_ms=data.get('execution_time_ms', 0.0),
            resources_used=data.get('resources_used', {}),
            metrics=data.get('metrics', {}),
            input_data=data.get('input_data', {}),
            output_data=data.get('output_data', {}),
            errors=data.get('errors', []),
            warnings=data.get('warnings', [])
        )


@dataclass
class StrategyEvaluation:
    """Ocena strategii."""
    
    evaluation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    strategy_id: str = ""
    evaluator_agent_id: str = ""
    evaluation_timestamp: datetime = field(default_factory=datetime.now)
    
    # Ocena
    effectiveness: float = 0.0  # Skuteczność (0.0 - 1.0)
    stability: float = 0.0     # Stabilność (0.0 - 1.0)
    efficiency: float = 0.0   # Wydajność (0.0 - 1.0)
    reliability: float = 0.0  # Niezawodność (0.0 - 1.0)
    adaptability: float = 0.0 # Dostosowalność (0.0 - 1.0)
    
    # Ogólna ocena
    overall_score: float = 0.0
    confidence: float = 0.0
    ranking_score: float = 0.0
    
    # Komentarz
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    notes: str = ""
    
    def calculate_overall_score(self) -> float:
        """Obliczenie ogólnej oceny."""
        weights = {
            'effectiveness': 0.3,
            'stability': 0.2,
            'efficiency': 0.2,
            'reliability': 0.2,
            'adaptability': 0.1
        }
        
        total = sum(
            getattr(self, key) * weight 
            for key, weight in weights.items()
        )
        return total
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika."""
        return {
            'evaluation_id': self.evaluation_id,
            'strategy_id': self.strategy_id,
            'evaluator_agent_id': self.evaluator_agent_id,
            'evaluation_timestamp': self.evaluation_timestamp.isoformat(),
            'effectiveness': self.effectiveness,
            'stability': self.stability,
            'efficiency': self.efficiency,
            'reliability': self.reliability,
            'adaptability': self.adaptability,
            'overall_score': self.calculate_overall_score(),
            'confidence': self.confidence,
            'ranking_score': self.ranking_score,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'recommendations': self.recommendations,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StrategyEvaluation':
        """Tworzenie z słownika."""
        return cls(
            evaluation_id=data.get('evaluation_id', str(uuid.uuid4())),
            strategy_id=data.get('strategy_id', ""),
            evaluator_agent_id=data.get('evaluator_agent_id', ""),
            evaluation_timestamp=datetime.fromisoformat(data.get('evaluation_timestamp', datetime.now().isoformat())),
            effectiveness=data.get('effectiveness', 0.0),
            stability=data.get('stability', 0.0),
            efficiency=data.get('efficiency', 0.0),
            reliability=data.get('reliability', 0.0),
            adaptability=data.get('adaptability', 0.0),
            overall_score=data.get('overall_score', 0.0),
            confidence=data.get('confidence', 0.0),
            ranking_score=data.get('ranking_score', 0.0),
            strengths=data.get('strengths', []),
            weaknesses=data.get('weaknesses', []),
            recommendations=data.get('recommendations', []),
            notes=data.get('notes', "")
        )


@dataclass
class StrategyRanking:
    """Ranking strategii."""
    
    ranking_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    strategy_id: str = ""
    ranking_timestamp: datetime = field(default_factory=datetime.now)
    
    # Pozycja w rankingu
    rank: int = 0
    total_strategies: int = 0
    percentile: float = 0.0  # Percentyl (0.0 - 1.0)
    
    # Wagi i dodatkowe metryki
    weights_used: Dict[str, float] = field(default_factory=dict)
    custom_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Kontekst rankingu
    ranking_category: str = "overall"
    agent_specific: bool = False
    target_agent_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika."""
        return {
            'ranking_id': self.ranking_id,
            'strategy_id': self.strategy_id,
            'ranking_timestamp': self.ranking_timestamp.isoformat(),
            'rank': self.rank,
            'total_strategies': self.total_strategies,
            'percentile': self.percentile,
            'weights_used': self.weights_used,
            'custom_metrics': self.custom_metrics,
            'ranking_category': self.ranking_category,
            'agent_specific': self.agent_specific,
            'target_agent_id': self.target_agent_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StrategyRanking':
        """Tworzenie z słownika."""
        return cls(
            ranking_id=data.get('ranking_id', str(uuid.uuid4())),
            strategy_id=data.get('strategy_id', ""),
            ranking_timestamp=datetime.fromisoformat(data.get('ranking_timestamp', datetime.now().isoformat())),
            rank=data.get('rank', 0),
            total_strategies=data.get('total_strategies', 0),
            percentile=data.get('percentile', 0.0),
            weights_used=data.get('weights_used', {}),
            custom_metrics=data.get('custom_metrics', {}),
            ranking_category=data.get('ranking_category', "overall"),
            agent_specific=data.get('agent_specific', False),
            target_agent_id=data.get('target_agent_id', "")
        )


@dataclass
class Strategy:
    """
    Główny model strategii.
    
    Każda strategia posiada:
    - strategy_id: Unikalny identyfikator
    - agent_owner: Agent będący właścicielem
    - version: Wersja strategii
    - creation_date: Data utworzenia
    - parameters: Parametry strategii
    - description: Opis strategii
    - usage_count: Liczba użyć
    - success_count: Liczba sukcesów
    - failure_count: Liczba porażek
    - success_rate: Wskaźnik sukcesu
    - confidence: Pewność strategii
    - ranking_score: Wynik rankingu
    - last_evaluation: Ostatnia ocena
    """
    
    # Podstawowe informacje
    strategy_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_owner: str = ""
    name: str = "Unnamed Strategy"
    
    # Wersja i status
    version: str = "1.0.0"
    strategy_version: StrategyVersion = StrategyVersion.ALPHA
    status: StrategyStatus = StrategyStatus.DRAFT
    
    # Czas
    creation_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    last_evaluation: Optional[datetime] = None
    
    # Typ i kategoria
    strategy_type: StrategyType = StrategyType.DECISION
    category: str = "default"
    tags: List[str] = field(default_factory=list)
    
    # Parametry
    parameters: StrategyParameters = field(default_factory=StrategyParameters)
    
    # Opis
    description: str = ""
    purpose: str = ""
    methodology: str = ""
    
    # Statystyki użycia
    usage_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    
    # Wskaźniki wydajności
    success_rate: float = 0.0
    confidence: float = 0.0
    reliability: float = 0.0
    avg_score: float = 0.0
    
    # Ranking
    ranking_score: float = 0.0
    current_rank: int = 0
    
    # Powiązania
    related_strategies: List[str] = field(default_factory=list)
    experiments: List[str] = field(default_factory=list)
    results: List[str] = field(default_factory=list)
    evaluations: List[str] = field(default_factory=list)
    
    # Zależności
    dependencies: List[str] = field(default_factory=list)
    required_memory_types: List[str] = field(default_factory=lambda: [
        "behavior_memory", "decision_memory", "agent_analysis_memory"
    ])
    
    # Pochodzenie
    inspired_by: Optional[str] = None
    based_on: Optional[str] = None
    
    def __post_init__(self):
        """Inicjalizacja po utworzeniu."""
        if self.usage_count > 0:
            self.success_rate = self.success_count / self.usage_count if self.usage_count > 0 else 0.0
        else:
            self.success_rate = 0.0
    
    def update_from_result(self, result: StrategyResult) -> None:
        """Aktualizacja statystyk na podstawie wyniku."""
        self.usage_count += 1
        self.last_used = datetime.now()
        
        if result.success:
            self.success_count += 1
        else:
            self.failure_count += 1
        
        # Aktualizacja wskaźników
        self.success_rate = self.success_count / self.usage_count if self.usage_count > 0 else 0.0
        
        # Średnia ocena
        if self.avg_score == 0.0:
            self.avg_score = result.score
        else:
            self.avg_score = (self.avg_score * (self.usage_count - 1) + result.score) / self.usage_count
        
        # Aktualizacja pewności
        self.confidence = (self.confidence * (self.usage_count - 1) + result.confidence) / self.usage_count
    
    def update_from_evaluation(self, evaluation: StrategyEvaluation) -> None:
        """Aktualizacja na podstawie oceny."""
        self.last_evaluation = datetime.now()
        self.ranking_score = evaluation.ranking_score
        self.confidence = evaluation.confidence
    
    def archive(self) -> None:
        """Archiwizacja strategii."""
        self.status = StrategyStatus.ARCHIVED
        self.last_updated = datetime.now()
    
    def deactivate(self) -> None:
        """Deaktywacja strategii."""
        self.status = StrategyStatus.DEPRECATED
        self.last_updated = datetime.now()
    
    def activate(self) -> None:
        """Aktywacja strategii."""
        self.status = StrategyStatus.ACTIVE
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika."""
        return {
            'strategy_id': self.strategy_id,
            'agent_owner': self.agent_owner,
            'name': self.name,
            'version': self.version,
            'strategy_version': self.strategy_version.value,
            'status': self.status.name,
            'creation_date': self.creation_date.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'last_evaluation': self.last_evaluation.isoformat() if self.last_evaluation else None,
            'strategy_type': self.strategy_type.name,
            'category': self.category,
            'tags': self.tags,
            'parameters': self.parameters.to_dict(),
            'description': self.description,
            'purpose': self.purpose,
            'methodology': self.methodology,
            'usage_count': self.usage_count,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'success_rate': self.success_rate,
            'confidence': self.confidence,
            'reliability': self.reliability,
            'avg_score': self.avg_score,
            'ranking_score': self.ranking_score,
            'current_rank': self.current_rank,
            'related_strategies': self.related_strategies,
            'experiments': self.experiments,
            'results': self.results,
            'evaluations': self.evaluations,
            'dependencies': self.dependencies,
            'required_memory_types': self.required_memory_types,
            'inspired_by': self.inspired_by,
            'based_on': self.based_on
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Strategy':
        """Tworzenie z słownika."""
        strategy = cls(
            strategy_id=data.get('strategy_id', str(uuid.uuid4())),
            agent_owner=data.get('agent_owner', ""),
            name=data.get('name', "Unnamed Strategy"),
            version=data.get('version', "1.0.0"),
            strategy_version=StrategyVersion(data.get('strategy_version', 'DRAFT')),
            status=StrategyStatus(data.get('status', 'DRAFT')),
            creation_date=datetime.fromisoformat(data.get('creation_date', datetime.now().isoformat())),
            last_updated=datetime.fromisoformat(data.get('last_updated', datetime.now().isoformat())),
            last_used=datetime.fromisoformat(data.get('last_used')) if data.get('last_used') else None,
            last_evaluation=datetime.fromisoformat(data.get('last_evaluation')) if data.get('last_evaluation') else None,
            strategy_type=StrategyType[data.get('strategy_type', 'DECISION')],
            category=data.get('category', "default"),
            tags=data.get('tags', []),
            parameters=StrategyParameters.from_dict(data.get('parameters', {})),
            description=data.get('description', ""),
            purpose=data.get('purpose', ""),
            methodology=data.get('methodology', ""),
            usage_count=data.get('usage_count', 0),
            success_count=data.get('success_count', 0),
            failure_count=data.get('failure_count', 0),
            success_rate=data.get('success_rate', 0.0),
            confidence=data.get('confidence', 0.0),
            reliability=data.get('reliability', 0.0),
            avg_score=data.get('avg_score', 0.0),
            ranking_score=data.get('ranking_score', 0.0),
            current_rank=data.get('current_rank', 0),
            related_strategies=data.get('related_strategies', []),
            experiments=data.get('experiments', []),
            results=data.get('results', []),
            evaluations=data.get('evaluations', []),
            dependencies=data.get('dependencies', []),
            required_memory_types=data.get('required_memory_types', [
                "behavior_memory", "decision_memory", "agent_analysis_memory"
            ]),
            inspired_by=data.get('inspired_by'),
            based_on=data.get('based_on')
        )
        
        # Rekalkulacja success_rate
        if strategy.usage_count > 0:
            strategy.success_rate = strategy.success_count / strategy.usage_count
        
        return strategy
    
    def to_json(self, indent: int = 2) -> str:
        """Konwersja do JSON."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Strategy':
        """Tworzenie z JSON."""
        data = json.loads(json_str)
        return cls.from_dict(data)


def create_strategy(
    agent_owner: str,
    name: str,
    strategy_type: StrategyType = StrategyType.DECISION,
    description: str = "",
    parameters: Optional[StrategyParameters] = None,
    **kwargs
) -> Strategy:
    """Tworzenie nowej strategii."""
    if parameters is None:
        parameters = StrategyParameters(strategy_type=strategy_type)
    
    strategy = Strategy(
        agent_owner=agent_owner,
        name=name,
        strategy_type=strategy_type,
        description=description,
        parameters=parameters,
        **kwargs
    )
    
    return strategy


def update_strategy_stats(strategy: Strategy, result: StrategyResult) -> Strategy:
    """Aktualizacja statystyk strategii na podstawie wyniku."""
    strategy.update_from_result(result)
    strategy.last_updated = datetime.now()
    return strategy


# Eksport
__all__ = [
    'StrategyStatus',
    'StrategyVersion',
    'StrategyType',
    'StrategyParameters',
    'StrategyResult',
    'StrategyEvaluation',
    'StrategyRanking',
    'Strategy',
    'create_strategy',
    'update_strategy_stats'
]