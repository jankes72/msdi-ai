"""
SSI V5 - Strategy Memory

Pamiec strategii dla Strategy Laboratory.

Struktura logiczna dla kazdego agenta:
Agent_X
├── strategy_memory
├── strategy_ranking
├── experiments
├── predictions
├── results
├── evaluations
└── evolution_history

Wersja: 1.0.0
Data: 2026-08-01
"""

import threading
import logging
import os
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import uuid

from .strategy_models import (
    Strategy,
    StrategyEvaluation,
    StrategyResult,
    StrategyRanking,
    StrategyStatus
)
from .experiment_models import (
    Experiment,
    ExperimentResult,
    ExperimentComparison,
    ExperimentStatus
)

# Konfiguracja logowania
logger = logging.getLogger(__name__)


@dataclass
class StrategyMemoryConfig:
    """Konfiguracja pamięci strategii."""
    
    # Ogólne
    persistence_enabled: bool = True
    persistence_path: str = "data/strategy_lab"
    auto_save_interval: int = 60  # Sekundy
    
    # Limity
    max_strategies_per_agent: int = 100
    max_experiments_per_agent: int = 50
    max_results_per_strategy: int = 1000
    
    # Zachowanie
    cleanup_interval_hours: int = 24
    archive_after_days: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika."""
        return {
            'persistence_enabled': self.persistence_enabled,
            'persistence_path': self.persistence_path,
            'auto_save_interval': self.auto_save_interval,
            'max_strategies_per_agent': self.max_strategies_per_agent,
            'max_experiments_per_agent': self.max_experiments_per_agent,
            'max_results_per_strategy': self.max_results_per_strategy,
            'cleanup_interval_hours': self.cleanup_interval_hours,
            'archive_after_days': self.archive_after_days
        }


@dataclass
class AgentStrategyLaboratory:
    """
    Laboratorium strategii dla pojedynczego agenta.
    
    Struktura:
    Agent_X
    ├── strategy_memory
    ├── strategy_ranking
    ├── experiments
    ├── predictions
    ├── results
    ├── evaluations
    └── evolution_history
    """
    
    agent_id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Pamiec strategii
    strategies: Dict[str, Strategy] = field(default_factory=dict)
    strategy_rankings: Dict[str, StrategyRanking] = field(default_factory=dict)
    
    # Eksperymenty
    experiments: Dict[str, Experiment] = field(default_factory=dict)
    experiment_results: Dict[str, ExperimentResult] = field(default_factory=dict)
    experiment_comparisons: Dict[str, ExperimentComparison] = field(default_factory=dict)
    
    # Wyniki strategii
    strategy_results: Dict[str, StrategyResult] = field(default_factory=dict)
    
    # Oceny
    strategy_evaluations: Dict[str, StrategyEvaluation] = field(default_factory=dict)
    
    # Historia ewolucji
    evolution_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Statystyki
    total_strategies: int = 0
    total_experiments: int = 0
    total_results: int = 0
    total_evaluations: int = 0
    
    def __post_init__(self):
        """Inicjalizacja po utworzeniu."""
        self.total_strategies = len(self.strategies)
        self.total_experiments = len(self.experiments)
        self.total_results = len(self.strategy_results)
        self.total_evaluations = len(self.strategy_evaluations)
    
    def add_strategy(self, strategy: Strategy) -> str:
        """Dodanie strategii."""
        if strategy.agent_owner != self.agent_id:
            raise ValueError(f"Strategy owner {strategy.agent_owner} doesn't match lab owner {self.agent_id}")
        
        strategy_id = strategy.strategy_id
        self.strategies[strategy_id] = strategy
        self.total_strategies += 1
        self.last_updated = datetime.now()
        
        # Zapis do historii ewolucji
        self._add_to_evolution_history("strategy_created", {
            'strategy_id': strategy_id,
            'name': strategy.name,
            'strategy_type': strategy.strategy_type.name
        })
        
        logger.info(f"Strategy {strategy_id} added to agent {self.agent_id} lab")
        return strategy_id
    
    def update_strategy(self, strategy: Strategy) -> bool:
        """Aktualizacja strategii."""
        if strategy.strategy_id not in self.strategies:
            return False
        
        self.strategies[strategy.strategy_id] = strategy
        self.last_updated = datetime.now()
        
        # Zapis do historii ewolucji
        self._add_to_evolution_history("strategy_updated", {
            'strategy_id': strategy.strategy_id,
            'name': strategy.name,
            'version': strategy.version,
            'changes': 'Updated strategy properties'
        })
        
        return True
    
    def remove_strategy(self, strategy_id: str) -> bool:
        """Usunięcie strategii."""
        if strategy_id not in self.strategies:
            return False
        
        strategy = self.strategies[strategy_id]
        del self.strategies[strategy_id]
        self.total_strategies -= 1
        self.last_updated = datetime.now()
        
        # Zapis do historii ewolucji
        self._add_to_evolution_history("strategy_removed", {
            'strategy_id': strategy_id,
            'name': strategy.name
        })
        
        return True
    
    def add_experiment(self, experiment: Experiment) -> str:
        """Dodanie eksperymentu."""
        if experiment.agent_owner != self.agent_id:
            raise ValueError(f"Experiment owner {experiment.agent_owner} doesn't match lab owner {self.agent_id}")
        
        experiment_id = experiment.experiment_id
        self.experiments[experiment_id] = experiment
        self.total_experiments += 1
        self.last_updated = datetime.now()
        
        # Zapis do historii ewolucji
        self._add_to_evolution_history("experiment_created", {
            'experiment_id': experiment_id,
            'name': experiment.name,
            'strategy_id': experiment.strategy_id
        })
        
        logger.info(f"Experiment {experiment_id} added to agent {self.agent_id} lab")
        return experiment_id
    
    def update_experiment(self, experiment: Experiment) -> bool:
        """Aktualizacja eksperymentu."""
        if experiment.experiment_id not in self.experiments:
            return False
        
        self.experiments[experiment.experiment_id] = experiment
        self.last_updated = datetime.now()
        
        # Zapis do historii ewolucji
        self._add_to_evolution_history("experiment_updated", {
            'experiment_id': experiment.experiment_id,
            'status': experiment.status.name
        })
        
        return True
    
    def add_strategy_result(self, result: StrategyResult) -> str:
        """Dodanie wyniku strategii."""
        if result.strategy_id not in self.strategies:
            raise ValueError(f"Strategy {result.strategy_id} not found in lab")
        
        result_id = result.result_id
        self.strategy_results[result_id] = result
        self.total_results += 1
        self.last_updated = datetime.now()
        
        # Zapis do historii ewolucji
        self._add_to_evolution_history("strategy_result_added", {
            'result_id': result_id,
            'strategy_id': result.strategy_id,
            'success': result.success,
            'score': result.score
        })
        
        return result_id
    
    def add_experiment_result(self, result: ExperimentResult) -> str:
        """Dodanie wyniku eksperymentu."""
        if result.experiment_id not in self.experiments:
            raise ValueError(f"Experiment {result.experiment_id} not found in lab")
        
        result_id = result.result_id
        self.experiment_results[result_id] = result
        self.last_updated = datetime.now()
        
        # Zapis do historii ewolucji
        self._add_to_evolution_history("experiment_result_added", {
            'result_id': result_id,
            'experiment_id': result.experiment_id,
            'success': result.success
        })
        
        return result_id
    
    def add_evaluation(self, evaluation: StrategyEvaluation) -> str:
        """Dodanie oceny strategii."""
        if evaluation.strategy_id not in self.strategies:
            raise ValueError(f"Strategy {evaluation.strategy_id} not found in lab")
        
        evaluation_id = evaluation.evaluation_id
        self.strategy_evaluations[evaluation_id] = evaluation
        self.total_evaluations += 1
        self.last_updated = datetime.now()
        
        # Zapis do historii ewolucji
        self._add_to_evolution_history("strategy_evaluated", {
            'evaluation_id': evaluation_id,
            'strategy_id': evaluation.strategy_id,
            'overall_score': evaluation.overall_score
        })
        
        return evaluation_id
    
    def add_ranking(self, ranking: StrategyRanking) -> str:
        """Dodanie rankingu strategii."""
        ranking_id = ranking.ranking_id
        self.strategy_rankings[ranking_id] = ranking
        self.last_updated = datetime.now()
        return ranking_id
    
    def add_experiment_comparison(self, comparison: ExperimentComparison) -> str:
        """Dodanie porównania eksperymentów."""
        comparison_id = comparison.comparison_id
        self.experiment_comparisons[comparison_id] = comparison
        self.last_updated = datetime.now()
        
        # Zapis do historii ewolucji
        self._add_to_evolution_history("experiments_compared", {
            'comparison_id': comparison_id,
            'experiment_count': len(comparison.experiment_ids),
            'winner': comparison.winner_experiment_id
        })
        
        return comparison_id
    
    def _add_to_evolution_history(self, event_type: str, data: Dict[str, Any]) -> None:
        """Dodanie wydarzenia do historii ewolucji."""
        entry = {
            'event_id': str(uuid.uuid4()),
            'event_type': event_type,
            'timestamp': datetime.now().isoformat(),
            'agent_id': self.agent_id,
            'data': data
        }
        self.evolution_history.append(entry)
        
        # Ograniczenie wielkości historii
        if len(self.evolution_history) > 1000:
            self.evolution_history = self.evolution_history[-1000:]
    
    def get_strategy(self, strategy_id: str) -> Optional[Strategy]:
        """Pobranie strategii."""
        return self.strategies.get(strategy_id)
    
    def get_experiment(self, experiment_id: str) -> Optional[Experiment]:
        """Pobranie eksperymentu."""
        return self.experiments.get(experiment_id)
    
    def get_strategy_results(self, strategy_id: str) -> List[StrategyResult]:
        """Pobranie wszystkich wyników strategii."""
        return [r for r in self.strategy_results.values() if r.strategy_id == strategy_id]
    
    def get_experiment_results(self, experiment_id: str) -> List[ExperimentResult]:
        """Pobranie wszystkich wyników eksperymentu."""
        return [r for r in self.experiment_results.values() if r.experiment_id == experiment_id]
    
    def get_strategy_evaluations(self, strategy_id: str) -> List[StrategyEvaluation]:
        """Pobranie wszystkich ocen strategii."""
        return [e for e in self.strategy_evaluations.values() if e.strategy_id == strategy_id]
    
    def get_evolution_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Pobranie historii ewolucji."""
        return self.evolution_history[-limit:]
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika."""
        return {
            'agent_id': self.agent_id,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'total_strategies': self.total_strategies,
            'total_experiments': self.total_experiments,
            'total_results': self.total_results,
            'total_evaluations': self.total_evaluations,
            'strategies': {k: v.to_dict() for k, v in self.strategies.items()},
            'experiments': {k: v.to_dict() for k, v in self.experiments.items()},
            'strategy_results': {k: v.to_dict() for k, v in self.strategy_results.items()},
            'experiment_results': {k: v.to_dict() for k, v in self.experiment_results.items()},
            'strategy_evaluations': {k: v.to_dict() for k, v in self.strategy_evaluations.items()},
            'strategy_rankings': {k: v.to_dict() for k, v in self.strategy_rankings.items()},
            'experiment_comparisons': {k: v.to_dict() for k, v in self.experiment_comparisons.items()},
            'evolution_history': self.evolution_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentStrategyLaboratory':
        """Tworzenie z słownika."""
        lab = cls(
            agent_id=data['agent_id'],
            created_at=datetime.fromisoformat(data['created_at']),
            last_updated=datetime.fromisoformat(data['last_updated']),
            total_strategies=data.get('total_strategies', 0),
            total_experiments=data.get('total_experiments', 0),
            total_results=data.get('total_results', 0),
            total_evaluations=data.get('total_evaluations', 0)
        )
        
        # Przwracanie strategii
        for sid, sdata in data.get('strategies', {}).items():
            strategy = Strategy.from_dict(sdata)
            lab.strategies[sid] = strategy
        
        # Przywracanie eksperymentów
        for eid, edata in data.get('experiments', {}).items():
            experiment = Experiment.from_dict(edata)
            lab.experiments[eid] = experiment
        
        # Przywracanie wyników strategii
        for rid, rdata in data.get('strategy_results', {}).items():
            result = StrategyResult.from_dict(rdata)
            lab.strategy_results[rid] = result
        
        # Przywracanie wyników eksperymentów
        for rid, rdata in data.get('experiment_results', {}).items():
            result = ExperimentResult.from_dict(rdata)
            lab.experiment_results[rid] = result
        
        # Przywracanie ocen
        for eid, edata in data.get('strategy_evaluations', {}).items():
            evaluation = StrategyEvaluation.from_dict(edata)
            lab.strategy_evaluations[eid] = evaluation
        
        # Przywracanie rankingów
        for rid, rdata in data.get('strategy_rankings', {}).items():
            ranking = StrategyRanking.from_dict(rdata)
            lab.strategy_rankings[rid] = ranking
        
        # Przywracanie porównań
        for cid, cdata in data.get('experiment_comparisons', {}).items():
            comparison = ExperimentComparison.from_dict(cdata)
            lab.experiment_comparisons[cid] = comparison
        
        # Przywracanie historii ewolucji
        lab.evolution_history = data.get('evolution_history', [])
        
        return lab
    
    def to_json(self, indent: int = 2) -> str:
        """Konwersja do JSON."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgentStrategyLaboratory':
        """Tworzenie z JSON."""
        data = json.loads(json_str)
        return cls.from_dict(data)


class StrategyMemory:
    """
    Główny manager pamięci strategii.
    
    Zarządza laboratoriami wszystkich agentów.
    """
    
    def __init__(self, config: Optional[StrategyMemoryConfig] = None):
        self.config = config or StrategyMemoryConfig()
        self._agent_labs: Dict[str, AgentStrategyLaboratory] = {}
        self._lock = threading.RLock()
        self._initialized = False
        
        # Inicjalizacja
        self._initialize_persistence()
        
        logger.info(f"StrategyMemory initialized with config: {self.config.to_dict()}")
    
    def _initialize_persistence(self) -> None:
        """Inicjalizacja systemu persistencji."""
        if not self.config.persistence_enabled:
            return
        
        try:
            # Utworzenie katalogu jeśli nie istnieje
            if not os.path.exists(self.config.persistence_path):
                os.makedirs(self.config.persistence_path, exist_ok=True)
            
            # Wczytanie istniejących danych
            self._load_all()
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing persistence: {e}")
    
    def _get_lab_path(self, agent_id: str) -> str:
        """Pobranie ścieżki do pliku laboratorium agenta."""
        return os.path.join(
            self.config.persistence_path, 
            f"agent_{agent_id}_strategy_lab.json"
        )
    
    def _load_lab(self, agent_id: str) -> Optional[AgentStrategyLaboratory]:
        """Wczytanie laboratorium agenta."""
        if not self.config.persistence_enabled:
            return None
        
        try:
            lab_path = self._get_lab_path(agent_id)
            if not os.path.exists(lab_path):
                return None
            
            with open(lab_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            lab = AgentStrategyLaboratory.from_dict(data)
            return lab
            
        except Exception as e:
            logger.error(f"Error loading lab for agent {agent_id}: {e}")
            return None
    
    def _save_lab(self, lab: AgentStrategyLaboratory) -> bool:
        """Zapisanie laboratorium agenta."""
        if not self.config.persistence_enabled:
            return True
        
        try:
            lab_path = self._get_lab_path(lab.agent_id)
            with open(lab_path, 'w', encoding='utf-8') as f:
                json.dump(lab.to_dict(), f, indent=2, ensure_ascii=False)
            return True
            
        except Exception as e:
            logger.error(f"Error saving lab for agent {lab.agent_id}: {e}")
            return False
    
    def _load_all(self) -> None:
        """Wczytanie wszystkich laboratoriów."""
        if not self.config.persistence_enabled:
            return
        
        try:
            lab_files = [
                f for f in os.listdir(self.config.persistence_path)
                if f.endswith('_strategy_lab.json')
            ]
            
            for lab_file in lab_files:
                agent_id = lab_file.replace('_strategy_lab.json', '').replace('agent_', '')
                lab = self._load_lab(agent_id)
                if lab:
                    self._agent_labs[agent_id] = lab
                    
            logger.info(f"Loaded {len(self._agent_labs)} agent labs from persistence")
            
        except Exception as e:
            logger.error(f"Error loading all labs: {e}")
    
    def _save_all(self) -> bool:
        """Zapisanie wszystkich laboratoriów."""
        if not self.config.persistence_enabled:
            return True
        
        success = True
        for lab in self._agent_labs.values():
            if not self._save_lab(lab):
                success = False
        
        return success
    
    def get_or_create_lab(self, agent_id: str) -> AgentStrategyLaboratory:
        """Pobranie lub utworzenie laboratorium agenta."""
        with self._lock:
            if agent_id not in self._agent_labs:
                # Spróbuj wczytać z pliku
                lab = self._load_lab(agent_id)
                if lab is None:
                    lab = AgentStrategyLaboratory(agent_id=agent_id)
                self._agent_labs[agent_id] = lab
            
            return self._agent_labs[agent_id]
    
    def get_lab(self, agent_id: str) -> Optional[AgentStrategyLaboratory]:
        """Pobranie laboratorium agenta."""
        with self._lock:
            return self._agent_labs.get(agent_id)
    
    def has_lab(self, agent_id: str) -> bool:
        """Sprawdzenie czy laboratorium agenta istnieje."""
        with self._lock:
            return agent_id in self._agent_labs
    
    def delete_lab(self, agent_id: str) -> bool:
        """Usunięcie laboratorium agenta."""
        with self._lock:
            if agent_id not in self._agent_labs:
                return False
            
            # Usunięcie pliku
            if self.config.persistence_enabled:
                try:
                    lab_path = self._get_lab_path(agent_id)
                    if os.path.exists(lab_path):
                        os.remove(lab_path)
                except Exception as e:
                    logger.error(f"Error deleting lab file for agent {agent_id}: {e}")
            
            del self._agent_labs[agent_id]
            return True
    
    def get_agent_strategies(self, agent_id: str) -> List[Strategy]:
        """Pobranie strategii agenta."""
        lab = self.get_lab(agent_id)
        if lab is None:
            return []
        return list(lab.strategies.values())
    
    def get_agent_experiments(self, agent_id: str) -> List[Experiment]:
        """Pobranie eksperymentów agenta."""
        lab = self.get_lab(agent_id)
        if lab is None:
            return []
        return list(lab.experiments.values())
    
    def get_all_strategies(self) -> List[Strategy]:
        """Pobranie wszystkich strategii."""
        with self._lock:
            all_strategies = []
            for lab in self._agent_labs.values():
                all_strategies.extend(lab.strategies.values())
            return all_strategies
    
    def get_all_experiments(self) -> List[Experiment]:
        """Pobranie wszystkich eksperymentów."""
        with self._lock:
            all_experiments = []
            for lab in self._agent_labs.values():
                all_experiments.extend(lab.experiments.values())
            return all_experiments
    
    def count_agents(self) -> int:
        """Zliczenie agentów."""
        with self._lock:
            return len(self._agent_labs)
    
    def count_all_strategies(self) -> int:
        """Zliczenie wszystkich strategii."""
        with self._lock:
            return sum(len(lab.strategies) for lab in self._agent_labs.values())
    
    def cleanup_archived(self, days: int = 30) -> Dict[str, int]:
        """Czyszczenie archiwalnych danych."""
        with self._lock:
            cleanup_stats = {
                'strategies_removed': 0,
                'experiments_removed': 0,
                'results_removed': 0,
                'evaluations_removed': 0
            }
            
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for lab in self._agent_labs.values():
                # Czyszczenie archiwalnych strategii
                archived_strategies = [
                    sid for sid, strategy in lab.strategies.items()
                    if (strategy.status == StrategyStatus.ARCHIVED and
                        strategy.last_updated and
                        (datetime.now() - strategy.last_updated).days > days)
                ]
                
                for sid in archived_strategies:
                    del lab.strategies[sid]
                    cleanup_stats['strategies_removed'] += 1
                
                # Czyszczenie zakończonych eksperymentów
                completed_experiments = [
                    eid for eid, experiment in lab.experiments.items()
                    if (experiment.status == ExperimentStatus.COMPLETED and
                        experiment.end_date and
                        (datetime.now() - experiment.end_date).days > days)
                ]
                
                for eid in completed_experiments:
                    del lab.experiments[eid]
                    cleanup_stats['experiments_removed'] += 1
            
            # Zapisanie zmian
            self._save_all()
            
            logger.info(f"Cleanup completed: {cleanup_stats}")
            return cleanup_stats
    
    def auto_save(self) -> bool:
        """Automatyczne zapisanie wszystkich laboratoriów."""
        if not self.config.persistence_enabled:
            return True
        
        return self._save_all()


# Singleton
_strategy_memory: Optional[StrategyMemory] = None
_strategy_memory_lock = threading.Lock()


def create_strategy_memory(config: Optional[StrategyMemoryConfig] = None) -> StrategyMemory:
    """Tworzenie nowej instancji Strategy Memory."""
    global _strategy_memory
    with _strategy_memory_lock:
        if _strategy_memory is None:
            _strategy_memory = StrategyMemory(config)
        return _strategy_memory


def get_strategy_memory() -> StrategyMemory:
    """Pobranie instancji singleton Strategy Memory."""
    global _strategy_memory
    if _strategy_memory is None:
        _strategy_memory = create_strategy_memory()
    return _strategy_memory


__all__ = [
    'StrategyMemoryConfig',
    'AgentStrategyLaboratory',
    'StrategyMemory',
    'create_strategy_memory',
    'get_strategy_memory'
]
