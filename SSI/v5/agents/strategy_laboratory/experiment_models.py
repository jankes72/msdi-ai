"""
SSI V5 - Experiment Models

Modul zawiera modele danych dla eksperymentów w Strategy Laboratory.

Wersja: 1.0.0
Data: 2026-08-01
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Union
import uuid
import json


class ExperimentStatus(Enum):
    """Status eksperymentu."""
    PLANNED = auto()         # Zaplanowany
    PREPARING = auto()       # W przygotowaniu
    RUNNING = auto()         # W trakcie wykonania
    PAUSED = auto()          # Wstrzymany
    COMPLETED = auto()       # Zakończony
    FAILED = auto()          # Nieudany
    CANCELLED = auto()       # Anulowany


class ExperimentType(Enum):
    """Typ eksperymentu."""
    A_B_TESTING = auto()         # Test A/B
    PARAMETER_OPTIMIZATION = auto()  # Optymalizacja parametrów
    STRATEGY_COMPARISON = auto()    # Porównanie strategii
    PERFORMANCE_TEST = auto()      # Test wydajności
    STRESS_TEST = auto()           # Test obciążeniowy
    VALIDATION = auto()            # Walidacja
    EXPLORATION = auto()           # Eksploracja
    EVOLUTION = auto()             # Ewolucja strategii


class TestMethodology(Enum):
    """Metodologia testowania."""
    RANDOMIZED = auto()      # Losowe przypisanie
    SEQUENTIAL = auto()      # Sekwencyjny test
    PARALLEL = auto()        # Test równoległy
    CROSS_VALIDATION = auto()  # Walidacja krzyżowa
    BOOTSTRAP = auto()       # Metoda bootstrap
    MONTE_CARLO = auto()     # Symulacja Monte Carlo


@dataclass
class ExperimentParameters:
    """Parametry eksperymentu."""
    
    # Ustawienia ogólne
    experiment_type: ExperimentType = ExperimentType.A_B_TESTING
    methodology: TestMethodology = TestMethodology.RANDOMIZED
    iterations: int = 100
    max_duration_seconds: float = 3600.0  # Maksymalna długość trwania
    
    # Ustawienia testów A/B
    test_group_size: int = 50
    control_group_size: int = 50
    randomization_seed: Optional[int] = None
    
    # Ustawienia optymalizacji
    optimization_algorithm: str = "grid_search"
    search_space: Dict[str, List[Any]] = field(default_factory=dict)
    objective_function: str = "maximize_success_rate"
    constraints: List[Dict[str, Any]] = field(default_factory=list)
    
    # Ustawienia porównania
    comparison_strategies: List[str] = field(default_factory=list)
    comparison_metrics: List[str] = field(default_factory=lambda: [
        "success_rate", "confidence", "execution_time"
    ])
    significance_level: float = 0.05
    
    # Ustawienia wydajności
    performance_metrics: List[str] = field(default_factory=lambda: [
        "throughput", "latency", "memory_usage", "cpu_usage"
    ])
    load_levels: List[int] = field(default_factory=lambda: [25, 50, 75, 100])
    warmup_period: int = 10
    
    # Ustawienia walidacji
    validation_metrics: List[str] = field(default_factory=lambda: [
        "accuracy", "precision", "recall", "f1_score"
    ])
    validation_split: float = 0.8
    
    # Ustawienia monitorowania
    monitor_interval: float = 1.0  # Interwał monitorowania w sekundach
    early_stopping: bool = True
    early_stopping_patience: int = 10
    
    # Kryteria triumfu
    success_criteria: Dict[str, float] = field(default_factory=lambda: {
        'min_success_rate': 0.7,
        'min_confidence': 0.6,
        'max_execution_time_ms': 1000.0
    })
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika."""
        return {
            'experiment_type': self.experiment_type.name,
            'methodology': self.methodology.name,
            'iterations': self.iterations,
            'max_duration_seconds': self.max_duration_seconds,
            'test_group_size': self.test_group_size,
            'control_group_size': self.control_group_size,
            'randomization_seed': self.randomization_seed,
            'optimization_algorithm': self.optimization_algorithm,
            'search_space': self.search_space,
            'objective_function': self.objective_function,
            'constraints': self.constraints,
            'comparison_strategies': self.comparison_strategies,
            'comparison_metrics': self.comparison_metrics,
            'significance_level': self.significance_level,
            'performance_metrics': self.performance_metrics,
            'load_levels': self.load_levels,
            'warmup_period': self.warmup_period,
            'validation_metrics': self.validation_metrics,
            'validation_split': self.validation_split,
            'monitor_interval': self.monitor_interval,
            'early_stopping': self.early_stopping,
            'early_stopping_patience': self.early_stopping_patience,
            'success_criteria': self.success_criteria
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExperimentParameters':
        """Tworzenie z słownika."""
        return cls(
            experiment_type=ExperimentType[data.get('experiment_type', 'A_B_TESTING')],
            methodology=TestMethodology[data.get('methodology', 'RANDOMIZED')],
            iterations=data.get('iterations', 100),
            max_duration_seconds=data.get('max_duration_seconds', 3600.0),
            test_group_size=data.get('test_group_size', 50),
            control_group_size=data.get('control_group_size', 50),
            randomization_seed=data.get('randomization_seed'),
            optimization_algorithm=data.get('optimization_algorithm', 'grid_search'),
            search_space=data.get('search_space', {}),
            objective_function=data.get('objective_function', 'maximize_success_rate'),
            constraints=data.get('constraints', []),
            comparison_strategies=data.get('comparison_strategies', []),
            comparison_metrics=data.get('comparison_metrics', ['success_rate', 'confidence', 'execution_time']),
            significance_level=data.get('significance_level', 0.05),
            performance_metrics=data.get('performance_metrics', ['throughput', 'latency']),
            load_levels=data.get('load_levels', [25, 50, 75, 100]),
            warmup_period=data.get('warmup_period', 10),
            validation_metrics=data.get('validation_metrics', ['accuracy', 'precision']),
            validation_split=data.get('validation_split', 0.8),
            monitor_interval=data.get('monitor_interval', 1.0),
            early_stopping=data.get('early_stopping', True),
            early_stopping_patience=data.get('early_stopping_patience', 10),
            success_criteria=data.get('success_criteria', {'min_success_rate': 0.7})
        )
    
    def validate(self) -> bool:
        """Walidacja parametrów."""
        if self.iterations < 1:
            return False
        if self.max_duration_seconds <= 0:
            return False
        if self.test_group_size < 1 or self.control_group_size < 1:
            return False
        if not 0.0 < self.significance_level < 1.0:
            return False
        if not 0.0 < self.validation_split < 1.0:
            return False
        if self.early_stopping_patience < 1:
            return False
        return True


@dataclass
class ExperimentResult:
    """Wynik eksperymentu."""
    
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    experiment_id: str = ""
    iteration: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Wyniki testów
    test_group_results: List[Dict[str, Any]] = field(default_factory=list)
    control_group_results: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metryki ogólne
    metrics: Dict[str, float] = field(default_factory=dict)
    statistical_tests: Dict[str, Any] = field(default_factory=dict)
    
    # Porównania
    comparisons: List[Dict[str, Any]] = field(default_factory=list)
    
    # Optymalizacja
    optimal_parameters: Dict[str, Any] = field(default_factory=dict)
    optimization_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Status
    success: bool = False
    confidence: float = 0.0
    
    # Błędy i ostrzeżenia
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Kontekst
    context: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_statistical_significance(self, metric: str = "success_rate") -> Dict[str, Any]:
        """Obliczenie istotności statystycznej."""
        if not self.test_group_results and not self.control_group_results:
            return {'significant': False, 'p_value': 1.0, 'effect_size': 0.0}
        
        # Uproszczona koristycja testu t-Studenta (autor Goulden)
        test_values = [
            r.get(metric, 0.0) 
            for r in self.test_group_results 
            if metric in r and isinstance(r[metric], (int, float))
        ]
        control_values = [
            r.get(metric, 0.0) 
            for r in self.control_group_results 
            if metric in r and isinstance(r[metric], (int, float))
        ]
        
        if not test_values or not control_values:
            return {'significant': False, 'p_value': 1.0, 'effect_size': 0.0}
        
        # Obliczenia uproszczone
        test_mean = sum(test_values) / len(test_values)
        control_mean = sum(control_values) / len(control_values)
        
        # Rozmiar efektu (Cohen's d)
        pooled_std = ((sum((x - test_mean) ** 2 for x in test_values) +
                     sum((x - control_mean) ** 2 for x in control_values)) / 
                    (len(test_values) + len(control_values) - 2)) ** 0.5
        
        if pooled_std == 0:
            effect_size = 0.0
        else:
            effect_size = abs(test_mean - control_mean) / pooled_std
        
        # Uproszczona ocena istotności
        p_value = 1.0 / (1.0 + effect_size * len(test_values) ** 0.5)
        
        return {
            'significant': p_value < 0.05,
            'p_value': p_value,
            'effect_size': effect_size,
            'test_mean': test_mean,
            'control_mean': control_mean
        }
    
    def get_best_parameters(self) -> Dict[str, Any]:
        """Pobranie najlepszych parametrów."""
        if self.optimization_history:
            return sorted(
                self.optimization_history, 
                key=lambda x: x.get('score', 0.0), 
                reverse=True
            )[0].get('parameters', {})
        return self.optimal_parameters
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika."""
        return {
            'result_id': self.result_id,
            'experiment_id': self.experiment_id,
            'iteration': self.iteration,
            'timestamp': self.timestamp.isoformat(),
            'test_group_results': self.test_group_results,
            'control_group_results': self.control_group_results,
            'metrics': self.metrics,
            'statistical_tests': self.statistical_tests,
            'comparisons': self.comparisons,
            'optimal_parameters': self.optimal_parameters,
            'optimization_history': self.optimization_history,
            'success': self.success,
            'confidence': self.confidence,
            'errors': self.errors,
            'warnings': self.warnings,
            'context': self.context
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExperimentResult':
        """Tworzenie z słownika."""
        return cls(
            result_id=data.get('result_id', str(uuid.uuid4())),
            experiment_id=data.get('experiment_id', ""),
            iteration=data.get('iteration', 0),
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
            test_group_results=data.get('test_group_results', []),
            control_group_results=data.get('control_group_results', []),
            metrics=data.get('metrics', {}),
            statistical_tests=data.get('statistical_tests', {}),
            comparisons=data.get('comparisons', []),
            optimal_parameters=data.get('optimal_parameters', {}),
            optimization_history=data.get('optimization_history', []),
            success=data.get('success', False),
            confidence=data.get('confidence', 0.0),
            errors=data.get('errors', []),
            warnings=data.get('warnings', []),
            context=data.get('context', {})
        )


@dataclass
class ExperimentComparison:
    """Porównanie wyników eksperymentów."""
    
    comparison_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    experiment_ids: List[str] = field(default_factory=list)
    comparison_timestamp: datetime = field(default_factory=datetime.now)
    
    # Porównane metryki
    compared_metrics: List[str] = field(default_factory=list)
    
    # Wyniki porównań
    comparisons: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Ranking eksperymentów
    experiment_ranking: List[Dict[str, Any]] = field(default_factory=list)
    
    # Wnioski
    winner_experiment_id: Optional[str] = None
    conclusions: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def determine_winner(self, metric: str = "overall_score") -> Optional[str]:
        """Okreslenie zwycięzcy porównania."""
        if not self.experiment_ranking:
            return None
        
        sorted_ranking = sorted(
            self.experiment_ranking,
            key=lambda x: x.get(metric, 0.0),
            reverse=True
        )
        
        if sorted_ranking:
            return sorted_ranking[0].get('experiment_id')
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika."""
        return {
            'comparison_id': self.comparison_id,
            'experiment_ids': self.experiment_ids,
            'comparison_timestamp': self.comparison_timestamp.isoformat(),
            'compared_metrics': self.compared_metrics,
            'comparisons': self.comparisons,
            'experiment_ranking': self.experiment_ranking,
            'winner_experiment_id': self.winner_experiment_id,
            'conclusions': self.conclusions,
            'recommendations': self.recommendations
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExperimentComparison':
        """Tworzenie z słownika."""
        return cls(
            comparison_id=data.get('comparison_id', str(uuid.uuid4())),
            experiment_ids=data.get('experiment_ids', []),
            comparison_timestamp=datetime.fromisoformat(data.get('comparison_timestamp', datetime.now().isoformat())),
            compared_metrics=data.get('compared_metrics', []),
            comparisons=data.get('comparisons', {}),
            experiment_ranking=data.get('experiment_ranking', []),
            winner_experiment_id=data.get('winner_experiment_id'),
            conclusions=data.get('conclusions', []),
            recommendations=data.get('recommendations', [])
        )


@dataclass
class Experiment:
    """
    Główny model eksperymentu.
    
    Powiązany z strategiami i ich testowaniem.
    """
    
    # Podstawowe informacje
    experiment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_owner: str = ""
    name: str = "Unnamed Experiment"
    
    # Powiązania ze strategiami
    strategy_id: str = ""  # Główna strategia testowana
    comparison_strategy_ids: List[str] = field(default_factory=list)
    
    # Status i typ
    status: ExperimentStatus = ExperimentStatus.PLANNED
    experiment_type: ExperimentType = ExperimentType.A_B_TESTING
    
    # Czas
    creation_date: datetime = field(default_factory=datetime.now)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Parametry
    parameters: ExperimentParameters = field(default_factory=ExperimentParameters)
    
    # Opis
    description: str = ""
    hypothesis: str = ""
    objectives: List[str] = field(default_factory=list)
    
    # Wyniki
    results: List[ExperimentResult] = field(default_factory=list)
    result_ids: List[str] = field(default_factory=list)
    
    # Statystyki
    total_iterations: int = 0
    successful_iterations: int = 0
    failed_iterations: int = 0
    
    # Metryki ogólne
    avg_success_rate: float = 0.0
    avg_confidence: float = 0.0
    avg_execution_time_ms: float = 0.0
    
    # Ranking
    ranking_score: float = 0.0
    
    # Kontekst
    context: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Inicjalizacja po utworzeniu."""
        if self.total_iterations > 0:
            self.avg_success_rate = self.successful_iterations / self.total_iterations
        else:
            self.avg_success_rate = 0.0
    
    def add_result(self, result: ExperimentResult) -> None:
        """Dodanie wyniki eksperymentu."""
        self.results.append(result)
        self.result_ids.append(result.result_id)
        self.total_iterations += 1
        
        if result.success:
            self.successful_iterations += 1
        else:
            self.failed_iterations += 1
        
        # Aktualizacja statystyk
        self._update_statistics()
    
    def _update_statistics(self) -> None:
        """Aktualizacja statystyk."""
        if self.total_iterations > 0:
            self.avg_success_rate = self.successful_iterations / self.total_iterations
        else:
            self.avg_success_rate = 0.0
        
        if self.results:
            total_confidence = sum(r.confidence for r in self.results)
            self.avg_confidence = total_confidence / len(self.results)
            
            total_time = sum(r.metrics.get('execution_time_ms', 0.0) for r in self.results)
            self.avg_execution_time_ms = total_time / len(self.results)
    
    def start(self) -> None:
        """Rozpoczęcie eksperymentu."""
        self.status = ExperimentStatus.RUNNING
        self.start_date = datetime.now()
        self.last_updated = datetime.now()
    
    def complete(self) -> None:
        """Zakończenie eksperymentu."""
        self.status = ExperimentStatus.COMPLETED
        self.end_date = datetime.now()
        self.last_updated = datetime.now()
    
    def fail(self) -> None:
        """Zakończenie eksperymentu niepowodzeniem."""
        self.status = ExperimentStatus.FAILED
        self.end_date = datetime.now()
        self.last_updated = datetime.now()
    
    def cancel(self) -> None:
        """Anulowanie eksperymentu."""
        self.status = ExperimentStatus.CANCELLED
        self.end_date = datetime.now()
        self.last_updated = datetime.now()
    
    def get_duration_seconds(self) -> float:
        """Obliczenie czasu trwania."""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).total_seconds()
        elif self.start_date:
            return (datetime.now() - self.start_date).total_seconds()
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika."""
        return {
            'experiment_id': self.experiment_id,
            'agent_owner': self.agent_owner,
            'name': self.name,
            'strategy_id': self.strategy_id,
            'comparison_strategy_ids': self.comparison_strategy_ids,
            'status': self.status.name,
            'experiment_type': self.experiment_type.name,
            'creation_date': self.creation_date.isoformat(),
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'last_updated': self.last_updated.isoformat(),
            'parameters': self.parameters.to_dict(),
            'description': self.description,
            'hypothesis': self.hypothesis,
            'objectives': self.objectives,
            'result_ids': self.result_ids,
            'total_iterations': self.total_iterations,
            'successful_iterations': self.successful_iterations,
            'failed_iterations': self.failed_iterations,
            'avg_success_rate': self.avg_success_rate,
            'avg_confidence': self.avg_confidence,
            'avg_execution_time_ms': self.avg_execution_time_ms,
            'ranking_score': self.ranking_score,
            'context': self.context,
            'duration_seconds': self.get_duration_seconds()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Experiment':
        """Tworzenie z słownika."""
        experiment = cls(
            experiment_id=data.get('experiment_id', str(uuid.uuid4())),
            agent_owner=data.get('agent_owner', ""),
            name=data.get('name', "Unnamed Experiment"),
            strategy_id=data.get('strategy_id', ""),
            comparison_strategy_ids=data.get('comparison_strategy_ids', []),
            status=ExperimentStatus[data.get('status', 'PLANNED')],
            experiment_type=ExperimentType[data.get('experiment_type', 'A_B_TESTING')],
            creation_date=datetime.fromisoformat(data.get('creation_date', datetime.now().isoformat())),
            start_date=datetime.fromisoformat(data.get('start_date')) if data.get('start_date') else None,
            end_date=datetime.fromisoformat(data.get('end_date')) if data.get('end_date') else None,
            last_updated=datetime.fromisoformat(data.get('last_updated', datetime.now().isoformat())),
            parameters=ExperimentParameters.from_dict(data.get('parameters', {})),
            description=data.get('description', ""),
            hypothesis=data.get('hypothesis', ""),
            objectives=data.get('objectives', []),
            result_ids=data.get('result_ids', []),
            total_iterations=data.get('total_iterations', 0),
            successful_iterations=data.get('successful_iterations', 0),
            failed_iterations=data.get('failed_iterations', 0),
            avg_success_rate=data.get('avg_success_rate', 0.0),
            avg_confidence=data.get('avg_confidence', 0.0),
            avg_execution_time_ms=data.get('avg_execution_time_ms', 0.0),
            ranking_score=data.get('ranking_score', 0.0),
            context=data.get('context', {})
        )
        
        # Rekalkulacja statystyk
        if experiment.total_iterations > 0:
            experiment.avg_success_rate = experiment.successful_iterations / experiment.total_iterations
        
        return experiment
    
    def to_json(self, indent: int = 2) -> str:
        """Konwersja do JSON."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Experiment':
        """Tworzenie z JSON."""
        data = json.loads(json_str)
        return cls.from_dict(data)


def create_experiment(
    agent_owner: str,
    name: str,
    strategy_id: str = "",
    experiment_type: ExperimentType = ExperimentType.A_B_TESTING,
    description: str = "",
    parameters: Optional[ExperimentParameters] = None,
    **kwargs
) -> Experiment:
    """Tworzenie nowego eksperymentu."""
    if parameters is None:
        parameters = ExperimentParameters(experiment_type=experiment_type)
    
    experiment = Experiment(
        agent_owner=agent_owner,
        name=name,
        strategy_id=strategy_id,
        experiment_type=experiment_type,
        description=description,
        parameters=parameters,
        **kwargs
    )
    
    return experiment


def update_experiment_stats(experiment: Experiment, result: ExperimentResult) -> Experiment:
    """Aktualizacja statystyk eksperymentu na podstawie wyniku."""
    experiment.add_result(result)
    experiment.last_updated = datetime.now()
    return experiment


# Eksport
__all__ = [
    'ExperimentStatus',
    'ExperimentType',
    'TestMethodology',
    'ExperimentParameters',
    'ExperimentResult',
    'ExperimentComparison',
    'Experiment',
    'create_experiment',
    'update_experiment_stats'
]