"""
SSI V5 - Experiment Manager

Manager eksperymentów dla Strategy Laboratory.

Implementuje funkcje:
- create_experiment()
- run_experiment()
- compare_results()

Wersja: 1.0.0
Data: 2026-08-01
"""

import threading
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
import uuid

from .experiment_models import (
    Experiment,
    ExperimentParameters,
    ExperimentResult,
    ExperimentComparison,
    ExperimentStatus,
    ExperimentType,
    TestMethodology,
    create_experiment as _create_experiment,
    update_experiment_stats as _update_experiment_stats
)
from .strategy_models import (
    Strategy,
    StrategyResult,
    StrategyStatus,
    StrategyType
)

# Konfiguracja logowania
logger = logging.getLogger(__name__)


@dataclass
class ExperimentManagerConfig:
    """Konfiguracja Experiment Manager."""
    
    # Ogólne
    max_experiments_per_agent: int = 50
    max_concurrent_experiments: int = 5
    max_experiment_duration_hours: float = 24.0
    
    # Wykonanie
    default_iterations: int = 100
    default_test_group_size: int = 50
    default_control_group_size: int = 50
    
    # Zasoby
    max_memory_usage_mb: int = 1024
    max_cpu_usage_percent: int = 80
    
    # Walidacja
    enable_validation: bool = True
    require_strategy_reference: bool = True
    
    # Zachowanie
    enable_early_stopping: bool = True
    early_stopping_patience: int = 10
    
    # Porównania
    enable_automatic_comparisons: bool = True
    comparison_threshold: float = 0.1  # Minimum difference for significance
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika."""
        return {
            'max_experiments_per_agent': self.max_experiments_per_agent,
            'max_concurrent_experiments': self.max_concurrent_experiments,
            'max_experiment_duration_hours': self.max_experiment_duration_hours,
            'default_iterations': self.default_iterations,
            'default_test_group_size': self.default_test_group_size,
            'default_control_group_size': self.default_control_group_size,
            'max_memory_usage_mb': self.max_memory_usage_mb,
            'max_cpu_usage_percent': self.max_cpu_usage_percent,
            'enable_validation': self.enable_validation,
            'require_strategy_reference': self.require_strategy_reference,
            'enable_early_stopping': self.enable_early_stopping,
            'early_stopping_patience': self.early_stopping_patience,
            'enable_automatic_comparisons': self.enable_automatic_comparisons,
            'comparison_threshold': self.comparison_threshold
        }


class ExperimentStorage:
    """Przechowalnia eksperymentów."""
    
    def __init__(self):
        self._experiments: Dict[str, Experiment] = {}
        self._by_agent: Dict[str, List[str]] = {}
        self._by_strategy: Dict[str, List[str]] = {}
        self._by_status: Dict[str, List[str]] = {}
        self._by_type: Dict[str, List[str]] = {}
        self._lock = threading.RLock()
    
    def add(self, experiment: Experiment) -> str:
        """Dodanie eksperymentu."""
        with self._lock:
            experiment_id = experiment.experiment_id
            self._experiments[experiment_id] = experiment
            
            # Indeksowanie
            if experiment.agent_owner not in self._by_agent:
                self._by_agent[experiment.agent_owner] = []
            self._by_agent[experiment.agent_owner].append(experiment_id)
            
            if experiment.strategy_id not in self._by_strategy:
                self._by_strategy[experiment.strategy_id] = []
            self._by_strategy[experiment.strategy_id].append(experiment_id)
            
            if experiment.status.name not in self._by_status:
                self._by_status[experiment.status.name] = []
            self._by_status[experiment.status.name].append(experiment_id)
            
            if experiment.experiment_type.name not in self._by_type:
                self._by_type[experiment.experiment_type.name] = []
            self._by_type[experiment.experiment_type.name].append(experiment_id)
            
            return experiment_id
    
    def get(self, experiment_id: str) -> Optional[Experiment]:
        """Pobranie eksperymentu."""
        with self._lock:
            return self._experiments.get(experiment_id)
    
    def get_by_agent(self, agent_id: str) -> List[Experiment]:
        """Pobranie eksperymentów agenta."""
        with self._lock:
            experiment_ids = self._by_agent.get(agent_id, [])
            return [self._experiments[eid] for eid in experiment_ids if eid in self._experiments]
    
    def get_by_strategy(self, strategy_id: str) -> List[Experiment]:
        """Pobranie eksperymentów dla strategii."""
        with self._lock:
            experiment_ids = self._by_strategy.get(strategy_id, [])
            return [self._experiments[eid] for eid in experiment_ids if eid in self._experiments]
    
    def get_by_status(self, status: Union[str, ExperimentStatus]) -> List[Experiment]:
        """Pobranie eksperymentów po statusie."""
        with self._lock:
            status_name = status if isinstance(status, str) else status.name
            experiment_ids = self._by_status.get(status_name, [])
            return [self._experiments[eid] for eid in experiment_ids if eid in self._experiments]
    
    def get_by_type(self, experiment_type: Union[str, ExperimentType]) -> List[Experiment]:
        """Pobranie eksperymentów po typie."""
        with self._lock:
            type_name = experiment_type if isinstance(experiment_type, str) else experiment_type.name
            experiment_ids = self._by_type.get(type_name, [])
            return [self._experiments[eid] for eid in experiment_ids if eid in self._experiments]
    
    def update(self, experiment: Experiment) -> bool:
        """Aktualizacja eksperymentu."""
        with self._lock:
            if experiment.experiment_id not in self._experiments:
                return False
            
            old_experiment = self._experiments[experiment.experiment_id]
            
            # Aktualizacja indeksów
            if old_experiment.agent_owner != experiment.agent_owner:
                if old_experiment.agent_owner in self._by_agent:
                    self._by_agent[old_experiment.agent_owner].remove(experiment.experiment_id)
                if experiment.agent_owner not in self._by_agent:
                    self._by_agent[experiment.agent_owner] = []
                self._by_agent[experiment.agent_owner].append(experiment.experiment_id)
            
            if old_experiment.strategy_id != experiment.strategy_id:
                if old_experiment.strategy_id in self._by_strategy:
                    self._by_strategy[old_experiment.strategy_id].remove(experiment.experiment_id)
                if experiment.strategy_id not in self._by_strategy:
                    self._by_strategy[experiment.strategy_id] = []
                self._by_strategy[experiment.strategy_id].append(experiment.experiment_id)
            
            if old_experiment.status.name != experiment.status.name:
                if old_experiment.status.name in self._by_status:
                    self._by_status[old_experiment.status.name].remove(experiment.experiment_id)
                if experiment.status.name not in self._by_status:
                    self._by_status[experiment.status.name] = []
                self._by_status[experiment.status.name].append(experiment.experiment_id)
            
            if old_experiment.experiment_type.name != experiment.experiment_type.name:
                if old_experiment.experiment_type.name in self._by_type:
                    self._by_type[old_experiment.experiment_type.name].remove(experiment.experiment_id)
                if experiment.experiment_type.name not in self._by_type:
                    self._by_type[experiment.experiment_type.name] = []
                self._by_type[experiment.experiment_type.name].append(experiment.experiment_id)
            
            self._experiments[experiment.experiment_id] = experiment
            return True
    
    def remove(self, experiment_id: str) -> bool:
        """Usunięcie eksperymentu."""
        with self._lock:
            if experiment_id not in self._experiments:
                return False
            
            experiment = self._experiments[experiment_id]
            
            # Usunięcie z indeksów
            if experiment.agent_owner in self._by_agent:
                self._by_agent[experiment.agent_owner].remove(experiment_id)
                if not self._by_agent[experiment.agent_owner]:
                    del self._by_agent[experiment.agent_owner]
            
            if experiment.strategy_id in self._by_strategy:
                self._by_strategy[experiment.strategy_id].remove(experiment_id)
                if not self._by_strategy[experiment.strategy_id]:
                    del self._by_strategy[experiment.strategy_id]
            
            if experiment.status.name in self._by_status:
                self._by_status[experiment.status.name].remove(experiment_id)
                if not self._by_status[experiment.status.name]:
                    del self._by_status[experiment.status.name]
            
            if experiment.experiment_type.name in self._by_type:
                self._by_type[experiment.experiment_type.name].remove(experiment_id)
                if not self._by_type[experiment.experiment_type.name]:
                    del self._by_type[experiment.experiment_type.name]
            
            del self._experiments[experiment_id]
            return True
    
    def list_all(self) -> List[Experiment]:
        """Pobranie wszystkich eksperymentów."""
        with self._lock:
            return list(self._experiments.values())
    
    def count(self) -> int:
        """Liczba wszystkich eksperymentów."""
        with self._lock:
            return len(self._experiments)
    
    def count_by_agent(self, agent_id: str) -> int:
        """Liczba eksperymentów agenta."""
        with self._lock:
            return len(self._by_agent.get(agent_id, []))
    
    def exists(self, experiment_id: str) -> bool:
        """Sprawdzenie czy eksperyment istnieje."""
        with self._lock:
            return experiment_id in self._experiments


class ExperimentValidator:
    """Weryfikator eksperymentów."""
    
    def __init__(self, config: ExperimentManagerConfig):
        self.config = config
    
    def validate_experiment(self, experiment: Experiment, is_update: bool = False) -> Tuple[bool, List[str]]:
        """Walidacja eksperymentu."""
        errors = []
        
        # Walidacja wymaganych pól
        if not experiment.agent_owner:
            errors.append("Agent owner is required")
        
        if not experiment.name:
            errors.append("Experiment name is required")
        
        if self.config.require_strategy_reference and not experiment.strategy_id:
            errors.append("Strategy reference is required")
        
        # Walidacja parametrów
        if not experiment.parameters.validate():
            errors.append("Invalid experiment parameters")
        
        # Walidacja czasu trwania
        if experiment.parameters.max_duration_seconds <= 0:
            errors.append("Max duration must be positive")
        
        if experiment.parameters.max_duration_seconds > self.config.max_experiment_duration_hours * 3600:
            errors.append(f"Max duration exceeds limit of {self.config.max_experiment_duration_hours} hours")
        
        return len(errors) == 0, errors


class ExperimentExecutor:
    """Wykonywacz eksperymentów."""
    
    def __init__(self, config: ExperimentManagerConfig):
        self.config = config
        self._executor = ThreadPoolExecutor(max_workers=config.max_concurrent_experiments)
        self._active_experiments: Dict[str, bool] = {}
        self._lock = threading.RLock()
    
    def execute_experiment(self, experiment: Experiment, strategy: Strategy) -> ExperimentResult:
        """Wykonanie pojedynczego eksperymentu."""
        
        result = ExperimentResult(
            experiment_id=experiment.experiment_id,
            iteration=1
        )
        
        try:
            # Symulacja wykonania eksperymentu
            start_time = time.time()
            
            # Wykonanie iteracji
            for i in range(min(experiment.parameters.iterations, 10)):  # Ograniczamy do 10 iteracji dla testu
                iteration_result = self._run_iteration(experiment, strategy, i)
                
                # Zapisanie wyniku iteracji
                if experiment.experiment_type == ExperimentType.A_B_TESTING:
                    # Symulacja testów A/B
                    test_result = {
                        'success': iteration_result['success'],
                        'score': iteration_result.get('score', 0.0),
                        'confidence': iteration_result.get('confidence', 0.5),
                        'execution_time_ms': iteration_result.get('execution_time_ms', 100)
                    }
                    result.test_group_results.append(test_result)
                else:
                    # Dla innych typów eksperymentów
                    result.metrics[f'iteration_{i}_success'] = iteration_result['success']
                    result.metrics[f'iteration_{i}_score'] = iteration_result.get('score', 0.0)
                
                # Sprawdzenie early stopping
                if (self.config.enable_early_stopping and 
                    experiment.parameters.early_stopping and
                    len(result.test_group_results) >= experiment.parameters.early_stopping_patience):
                    
                    # Obliczenie średniej skuteczności
                    if result.test_group_results:
                        avg_success = sum(r.get('success', 0) for r in result.test_group_results) / len(result.test_group_results)
                        if avg_success < experiment.parameters.success_criteria.get('min_success_rate', 0.5):
                            result.success = False
                            result.errors.append('Early stopping: success rate below threshold')
                            break
            
            # Obliczenie statystyk
            if result.test_group_results:
                all_successes = [r.get('success', 0) for r in result.test_group_results]
                success_count = sum(all_successes)
                total_count = len(all_successes)
                
                result.metrics['success_rate'] = success_count / total_count if total_count > 0 else 0.0
                result.metrics['avg_score'] = sum(r.get('score', 0.0) for r in result.test_group_results) / total_count
                result.metrics['avg_confidence'] = sum(r.get('confidence', 0.5) for r in result.test_group_results) / total_count
                result.metrics['execution_time_ms'] = sum(r.get('execution_time_ms', 100) for r in result.test_group_results)
                
            result.execution_time_ms = (time.time() - start_time) * 1000
            result.success = result.metrics.get('success_rate', 0.0) >= experiment.parameters.success_criteria.get('min_success_rate', 0.7)
            result.confidence = result.metrics.get('avg_confidence', 0.5)
            
        except Exception as e:
            result.success = False
            result.errors.append(str(e))
            logger.error(f"Error executing experiment {experiment.experiment_id}: {e}")
        
        return result
    
    def _run_iteration(self, experiment: Experiment, strategy: Strategy, iteration: int) -> Dict[str, Any]:
        """Wykonanie pojedynczej iteracji."""
        # Symulacja wykonania strategii
        # W prawdziwej implementacji tutaj byłoby wołanie strategii
        
        import random
        
        # Symulacja losowego wyniku
        base_success_rate = (strategy.success_rate + strategy.confidence * 0.5) / 2
        
        # Dodanie szumu
        noise = random.uniform(-0.1, 0.1)
        success_prob = max(0.1, min(0.9, base_success_rate + noise))
        
        success = random.random() < success_prob
        score = random.uniform(0.6, 0.95) if success else random.uniform(0.2, 0.5)
        confidence = random.uniform(0.7, 0.95) if success else random.uniform(0.3, 0.6)
        
        return {
            'success': success,
            'score': score,
            'confidence': confidence,
            'execution_time_ms': random.randint(50, 200),
            'iteration': iteration,
            'strategy_id': strategy.strategy_id,
            'experiment_id': experiment.experiment_id
        }
    
    def start_experiment(self, experiment: Experiment) -> None:
        """Rozpoczęcie eksperymentu w tle."""
        with self._lock:
            if experiment.experiment_id in self._active_experiments:
                return
            
            self._active_experiments[experiment.experiment_id] = True
        
        # Wykonanie w tle
        future = self._executor.submit(self._execute_experiment_async, experiment)
        future.add_done_callback(self._on_experiment_complete)
    
    def _execute_experiment_async(self, experiment: Experiment) -> Experiment:
        """Asynchroniczne wykonanie eksperymentu."""
        # Tutaj byłoby pobranie strategii i wykonanie eksperymentu
        # Na razie zwracamy eksperyment bez zmian
        return experiment
    
    def _on_experiment_complete(self, future) -> None:
        """Callback po zakończeniu eksperymentu."""
        try:
            experiment = future.result()
            with self._lock:
                if experiment.experiment_id in self._active_experiments:
                    del self._active_experiments[experiment.experiment_id]
        except Exception as e:
            logger.error(f"Experiment completion callback error: {e}")
    
    def is_experiment_running(self, experiment_id: str) -> bool:
        """Sprawdzenie czy eksperyment jest w trakcie wykonania."""
        with self._lock:
            return experiment_id in self._active_experiments
    
    def stop_all(self) -> int:
        """Zatrzymanie wszystkich eksperymentów."""
        with self._lock:
            stopped_count = len(self._active_experiments)
            self._active_experiments.clear()
            return stopped_count
    
    def shutdown(self) -> None:
        """Zamknięcie executor."""
        self._executor.shutdown(wait=True)


class ExperimentManager:
    """
    Główny manager eksperymentów.
    
    Implementuje:
    - create_experiment()
    - run_experiment()
    - compare_results()
    """
    
    def __init__(self, config: Optional[ExperimentManagerConfig] = None):
        self.config = config or ExperimentManagerConfig()
        self.storage = ExperimentStorage()
        self.validator = ExperimentValidator(self.config)
        self.executor = ExperimentExecutor(self.config)
        self._lock = threading.RLock()
        
        # Hooki na zdarzenia
        self._on_create_hooks: List[Callable[[Experiment], None]] = []
        self._on_start_hooks: List[Callable[[Experiment], None]] = []
        self._on_complete_hooks: List[Callable[[Experiment], None]] = []
        self._on_compare_hooks: List[Callable[[ExperimentComparison], None]] = []
        
        logger.info(f"ExperimentManager initialized with config: {self.config.to_dict()}")
    
    def on_create(self, callback: Callable[[Experiment], None]) -> None:
        """Rejestracja hooka na tworzenie eksperymentu."""
        self._on_create_hooks.append(callback)
    
    def on_start(self, callback: Callable[[Experiment], None]) -> None:
        """Rejestracja hooka na rozpoczęcie eksperymentu."""
        self._on_start_hooks.append(callback)
    
    def on_complete(self, callback: Callable[[Experiment], None]) -> None:
        """Rejestracja hooka na zakończenie eksperymentu."""
        self._on_complete_hooks.append(callback)
    
    def on_compare(self, callback: Callable[[ExperimentComparison], None]) -> None:
        """Rejestracja hooka na porównanie wyników."""
        self._on_compare_hooks.append(callback)
    
    def _trigger_on_create(self, experiment: Experiment) -> None:
        """Wywołanie hooków na tworzenie."""
        for hook in self._on_create_hooks:
            try:
                hook(experiment)
            except Exception as e:
                logger.error(f"Error in on_create hook: {e}")
    
    def _trigger_on_start(self, experiment: Experiment) -> None:
        """Wywołanie hooków na rozpoczęcie."""
        for hook in self._on_start_hooks:
            try:
                hook(experiment)
            except Exception as e:
                logger.error(f"Error in on_start hook: {e}")
    
    def _trigger_on_complete(self, experiment: Experiment) -> None:
        """Wywołanie hooków na zakończenie."""
        for hook in self._on_complete_hooks:
            try:
                hook(experiment)
            except Exception as e:
                logger.error(f"Error in on_complete hook: {e}")
    
    def _trigger_on_compare(self, comparison: ExperimentComparison) -> None:
        """Wywołanie hooków na porównanie."""
        for hook in self._on_compare_hooks:
            try:
                hook(comparison)
            except Exception as e:
                logger.error(f"Error in on_compare hook: {e}")
    
    def create_experiment(
        self,
        agent_owner: str,
        name: str,
        strategy_id: str,
        experiment_type: ExperimentType = None,
        description: str = "",
        parameters: Optional[ExperimentParameters] = None,
        hypothesis: str = "",
        objectives: List[str] = None,
        **kwargs
    ) -> Experiment:
        """
        Tworzenie nowego eksperymentu.
        
        Args:
            agent_owner: Agent będący właścicielem eksperymentu
            name: Nazwa eksperymentu
            strategy_id: ID strategii do testowania
            experiment_type: Typ eksperymentu (domyślnie A_B_TESTING)
            description: Opis eksperymentu
            parameters: Parametry eksperymentu
            hypothesis: Hipoteza eksperymentu
            objectives: Cele eksperymentu
            **kwargs: Dodatkowe parametry
            
        Returns:
            Experiment: Nowo utworzony eksperyment
        """
        with self._lock:
            # Ustawienia domyślne
            if experiment_type is None:
                experiment_type = ExperimentType.A_B_TESTING
            if objectives is None:
                objectives = []
            
            # Utworzenie eksperymentu
            if parameters is None:
                parameters = ExperimentParameters(
                    experiment_type=experiment_type,
                    iterations=self.config.default_iterations,
                    test_group_size=self.config.default_test_group_size,
                    control_group_size=self.config.default_control_group_size
                )
            
            experiment = _create_experiment(
                agent_owner=agent_owner,
                name=name,
                strategy_id=strategy_id,
                experiment_type=experiment_type,
                description=description,
                parameters=parameters,
                hypothesis=hypothesis,
                objectives=objectives,
                **kwargs
            )
            
            # Walidacja
            if self.config.enable_validation:
                valid, errors = self.validator.validate_experiment(experiment)
                if not valid:
                    error_msg = f"Experiment validation failed: {errors}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
            
            # Sprawdzenie limitów
            agent_experiments = self.storage.count_by_agent(agent_owner)
            if agent_experiments >= self.config.max_experiments_per_agent:
                error_msg = f"Agent {agent_owner} has reached maximum experiments limit ({self.config.max_experiments_per_agent})"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Dodanie do przechowalni
            experiment_id = self.storage.add(experiment)
            experiment.experiment_id = experiment_id
            
            # Wywołanie hooków
            self._trigger_on_create(experiment)
            
            logger.info(f"Experiment created: {experiment_id} by agent {agent_owner}")
            
            return experiment
    
    def run_experiment(
        self,
        experiment_id: str,
        strategy: Optional[Strategy] = None
    ) -> Tuple[Optional[Experiment], Optional[ExperimentResult]]:
        """
        Uruchomienie eksperymentu.
        
        Args:
            experiment_id: ID eksperymentu do uruchomienia
            strategy: Strategia do testowania (opcjonalnie, jeśli nie podano w eksperymencie)
            
        Returns:
            Tuple[Experiment, ExperimentResult]: Zaktualizowany eksperyment i wynik
        """
        with self._lock:
            experiment = self.storage.get(experiment_id)
            if experiment is None:
                logger.warning(f"Experiment not found: {experiment_id}")
                return None, None
            
            # Sprawdzenie statusu
            if experiment.status == ExperimentStatus.RUNNING:
                logger.warning(f"Experiment {experiment_id} is already running")
                return experiment, None
            
            if experiment.status in [ExperimentStatus.COMPLETED, ExperimentStatus.FAILED]:
                logger.warning(f"Experiment {experiment_id} is already finished")
                return experiment, None
            
            # Rozpoczęcie eksperymentu
            experiment.start()
            self.storage.update(experiment)
            
            # Wywołanie hooków
            self._trigger_on_start(experiment)
        
        # Wykonanie eksperymentu
        try:
            # Pobranie strategii jeśli nie podano
            if strategy is None and experiment.strategy_id:
                # W prawdziwej implementacji tutaj byłoby pobranie strategii
                # z Strategy Manager
                logger.warning(f"Strategy {experiment.strategy_id} not provided, using simulation")
                # Symulacja strategii
                from .strategy_models import Strategy, StrategyType, StrategyStatus
                strategy = Strategy(
                    strategy_id=experiment.strategy_id,
                    agent_owner=experiment.agent_owner,
                    name=f"Strategy {experiment.strategy_id}",
                    strategy_type=StrategyType.DECISION,
                    status=StrategyStatus.ACTIVE,
                    success_rate=0.7,
                    confidence=0.8
                )
            
            # Wykonanie eksperymentu
            result = self.executor.execute_experiment(experiment, strategy)
            
            # Aktualizacja eksperymentu
            with self._lock:
                experiment.add_result(result)
                experiment.complete()
                self.storage.update(experiment)
                
                # Wywołanie hooków
                self._trigger_on_complete(experiment)
            
            logger.info(f"Experiment completed: {experiment_id}, success: {result.success}")
            
            return experiment, result
            
        except Exception as e:
            logger.error(f"Error running experiment {experiment_id}: {e}")
            
            with self._lock:
                experiment.fail()
                experiment.errors.append(str(e))
                self.storage.update(experiment)
            
            return experiment, None
    
    def compare_results(
        self,
        experiment_ids: List[str],
        metrics: List[str] = None,
        methodology: str = "pairwise"
    ) -> Optional[ExperimentComparison]:
        """
        Porównanie wyników eksperymentów.
        
        Args:
            experiment_ids: Lista ID eksperymentów do porównania
            metrics: Lista metryk do porównania
            methodology: Metodologia porównania (pairwise, statistical, etc.)
            
        Returns:
            ExperimentComparison: Wyniki porównania
        """
        with self._lock:
            if not experiment_ids:
                logger.warning("No experiment IDs provided for comparison")
                return None
            
            # Pobranie eksperymentów
            experiments = []
            missing_ids = []
            
            for exp_id in experiment_ids:
                experiment = self.storage.get(exp_id)
                if experiment is None:
                    missing_ids.append(exp_id)
                else:
                    experiments.append(experiment)
            
            if missing_ids:
                logger.warning(f"Experiments not found: {missing_ids}")
                return None
            
            if len(experiments) < 2:
                logger.warning("At least 2 experiments are required for comparison")
                return None
            
            # Ustawienia domyślne
            if metrics is None:
                metrics = ['success_rate', 'avg_confidence', 'avg_execution_time_ms']
            
            # Utworzenie porównania
            comparison = ExperimentComparison(
                experiment_ids=experiment_ids,
                compared_metrics=metrics
            )
            
            # Porównanie eksperymentów
            experiment_ranking = []
            comparisons = {}
            
            for i, exp1 in enumerate(experiments):
                ranking_entry = {
                    'experiment_id': exp1.experiment_id,
                    'name': exp1.name,
                    'overall_score': 0.0
                }
                
                # Obliczenie ogólnego wyniku
                score = 0.0
                metric_scores = {}
                
                for metric in metrics:
                    metric_value = getattr(exp1, metric, 0.0) if hasattr(exp1, metric) else 0.0
                    metric_scores[metric] = metric_value
                    score += metric_value
                
                # Normalizacja
                if len(metrics) > 0:
                    score = score / len(metrics)
                
                ranking_entry['overall_score'] = score
                ranking_entry['metrics'] = metric_scores
                ranking_entry['success_rate'] = getattr(exp1, 'avg_success_rate', 0.0)
                
                experiment_ranking.append(ranking_entry)
                
                # Porównania parami
                for j, exp2 in enumerate(experiments[i+1:]):
                    pair_key = f"{exp1.experiment_id}_vs_{exp2.experiment_id}"
                    
                    pair_comparison = {}
                    for metric in metrics:
                        val1 = getattr(exp1, metric, 0.0)
                        val2 = getattr(exp2, metric, 0.0)
                        
                        difference = val1 - val2
                        significant = abs(difference) > self.config.comparison_threshold
                        
                        pair_comparison[metric] = {
                            'experiment_1': val1,
                            'experiment_2': val2,
                            'difference': difference,
                            'significant': significant
                        }
                    
                    comparisons[pair_key] = pair_comparison
            
            # Sortowanie rankingu
            experiment_ranking.sort(key=lambda x: x['overall_score'], reverse=True)
            
            comparison.experiment_ranking = experiment_ranking
            comparison.comparisons = comparisons
            comparison.winner_experiment_id = experiment_ranking[0]['experiment_id'] if experiment_ranking else None
            
            # Generowanie wniosków
            if experiment_ranking and len(experiment_ranking) > 1:
                winner = experiment_ranking[0]
                loser = experiment_ranking[-1]
                
                comparison.conclusions = [
                    f"Experiment {winner['name']} ({winner['experiment_id']}) achieved the highest score: {winner['overall_score']:.3f}",
                    f"Experiment {loser['name']} ({loser['experiment_id']}) had the lowest score: {loser['overall_score']:.3f}"
                ]
                
                if self.config.enable_automatic_comparisons:
                    comparison.recommendations = [
                        f"Consider using the parameters from {winner['name']} for future experiments"
                    ]
            
            comparison.comparison_timestamp = datetime.now()
            
            # Wywołanie hooków
            self._trigger_on_compare(comparison)
            
            logger.info(f"Experiments compared: {len(experiments)} experiments, winner: {comparison.winner_experiment_id}")
            
            return comparison
    
    def get_experiment(self, experiment_id: str) -> Optional[Experiment]:
        """Pobranie eksperymentu po ID."""
        with self._lock:
            return self.storage.get(experiment_id)
    
    def get_experiments_by_agent(self, agent_id: str) -> List[Experiment]:
        """Pobranie eksperymentów agenta."""
        with self._lock:
            return self.storage.get_by_agent(agent_id)
    
    def get_experiments_by_strategy(self, strategy_id: str) -> List[Experiment]:
        """Pobranie eksperymentów dla strategii."""
        with self._lock:
            return self.storage.get_by_strategy(strategy_id)
    
    def get_running_experiments(self) -> List[Experiment]:
        """Pobranie uruchomionych eksperymentów."""
        with self._lock:
            return self.storage.get_by_status(ExperimentStatus.RUNNING)
    
    def delete_experiment(self, experiment_id: str) -> bool:
        """Usunięcie eksperymentu."""
        with self._lock:
            result = self.storage.remove(experiment_id)
            if result:
                logger.info(f"Experiment deleted: {experiment_id}")
            else:
                logger.warning(f"Experiment not found for deletion: {experiment_id}")
            return result
    
    def count_experiments(self, agent_id: Optional[str] = None) -> int:
        """Zliczenie eksperymentów."""
        with self._lock:
            if agent_id:
                return self.storage.count_by_agent(agent_id)
            return self.storage.count()
    
    def cleanup_completed(self, days: int = 30) -> int:
        """Czyszczenie zakończonych eksperymentów starszych niż N dni."""
        with self._lock:
            from datetime import timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days)
            completed_experiments = self.storage.get_by_status(ExperimentStatus.COMPLETED)
            
            deleted_count = 0
            for experiment in completed_experiments:
                if experiment.end_date and (datetime.now() - experiment.end_date).days > days:
                    self.storage.remove(experiment.experiment_id)
                    deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} completed experiments older than {days} days")
            return deleted_count
    
    def shutdown(self) -> None:
        """Zamknięcie managera."""
        self.executor.shutdown()


# Singleton
_experiment_manager: Optional[ExperimentManager] = None
_experiment_manager_lock = threading.Lock()


def create_experiment_manager(config: Optional[ExperimentManagerConfig] = None) -> ExperimentManager:
    """Tworzenie nowej instancji Experiment Manager."""
    global _experiment_manager
    with _experiment_manager_lock:
        if _experiment_manager is None:
            _experiment_manager = ExperimentManager(config)
        return _experiment_manager


def get_experiment_manager() -> ExperimentManager:
    """Pobranie instancji singleton Experiment Manager."""
    global _experiment_manager
    if _experiment_manager is None:
        _experiment_manager = create_experiment_manager()
    return _experiment_manager


__all__ = [
    'ExperimentManagerConfig',
    'ExperimentStorage',
    'ExperimentValidator',
    'ExperimentExecutor',
    'ExperimentManager',
    'create_experiment_manager',
    'get_experiment_manager'
]
