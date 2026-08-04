"""
SSI V5 - Strategy Memory Integrator

Integracja Strategy Laboratory z Memory Ecosystem.

Każdy wynik strategii musi wpływać na:
- Behavior Memory
- Decision Memory  
- Agent Analysis Memory

Czyli:
Strategia
↓
Wynik
↓
Ocena
↓
Zmiana zachowania agenta

Wersja: 1.0.0
Data: 2026-08-01
"""

import threading
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import uuid

from SSI.v5.memory.memory_types import (
    BehaviorMemory,
    DecisionLayerMemory,
    AgentAnalysisMemory,
    BehaviorType,
    AnalysisType
)
from SSI.v5.core.information_flow_controller.message_models import (
    SSIMessage,
    MessageResponse,
    MessageStatus,
    PriorityLevel,
    ProcessType
)
from SSI.v5.core.information_flow_controller.message_factory import (
    create_message,
    create_response_message
)

from .strategy_models import (
    Strategy,
    StrategyResult,
    StrategyEvaluation,
    StrategyRanking,
    StrategyStatus,
    StrategyType
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
class MemoryIntegratorConfig:
    """Konfiguracja Memory Integrator."""
    
    # Ogólne
    update_behavior_memory: bool = True
    update_decision_memory: bool = True
    update_agent_analysis_memory: bool = True
    auto_update_on_result: bool = True
    auto_update_on_evaluation: bool = True
    auto_update_on_ranking: bool = True
    
    # Mapowanie typów
    strategy_to_behavior_type: Dict[str, BehaviorType] = field(default_factory=lambda: {
        'DECISION': BehaviorType.DECISION,
        'ANALYSIS': BehaviorType.ANALYSIS,
        'PREDICTION': BehaviorType.ANALYSIS,
        'LEARNING': BehaviorType.LEARNING,
        'COLLABORATION': BehaviorType.SOCIAL,
        'OPTIMIZATION': BehaviorType.DECISION,
        'EXPERIMENTAL': BehaviorType.CREATIVE
    })
    
    strategy_to_analysis_type: Dict[str, AnalysisType] = field(default_factory=lambda: {
        'DECISION': AnalysisType.BEHAVIOR,
        'ANALYSIS': AnalysisType.STRATEGY,
        'PREDICTION': AnalysisType.PERFORMANCE,
        'LEARNING': AnalysisType.EVOLUTION,
        'COLLABORATION': AnalysisType.COLLABORATION,
        'OPTIMIZATION': AnalysisType.PERFORMANCE,
        'EXPERIMENTAL': AnalysisType.STRATEGY
    })
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika."""
        return {
            'update_behavior_memory': self.update_behavior_memory,
            'update_decision_memory': self.update_decision_memory,
            'update_agent_analysis_memory': self.update_agent_analysis_memory,
            'auto_update_on_result': self.auto_update_on_result,
            'auto_update_on_evaluation': self.auto_update_on_evaluation,
            'auto_update_on_ranking': self.auto_update_on_ranking,
            'strategy_to_behavior_type': {k: v.name for k, v in self.strategy_to_behavior_type.items()},
            'strategy_to_analysis_type': {k: v.name for k, v in self.strategy_to_analysis_type.items()}
        }


class StrategyMemoryIntegrator:
    """
    Integracja Strategy Laboratory z Memory Ecosystem.
    
    Odpowiedzialny za:
    - Aktualizację Behavior Memory na podstawie wyników strategii
    - Aktualizację Decision Memory na podstawie decyzji podejmowanych przez strategie
    - Aktualizację Agent Analysis Memory na podstawie ocen i rankingów strategii
    """
    
    def __init__(self, config: Optional[MemoryIntegratorConfig] = None):
        self.config = config or MemoryIntegratorConfig()
        self._lock = threading.RLock()
        
        # Hooki na zdarzenia
        self._on_memory_update_hooks: List[Callable[[str, str, Dict[str, Any]], None]] = []
        
        logger.info(f"StrategyMemoryIntegrator initialized with config: {self.config.to_dict()}")
    
    def on_memory_update(self, callback: Callable[[str, str, Dict[str, Any]], None]) -> None:
        """Rejestracja hooka na aktualizację pamięci."""
        self._on_memory_update_hooks.append(callback)
    
    def _trigger_memory_update(self, memory_type: str, agent_id: str, data: Dict[str, Any]) -> None:
        """Wywołanie hooków na aktualizację pamięci."""
        for hook in self._on_memory_update_hooks:
            try:
                hook(memory_type, agent_id, data)
            except Exception as e:
                logger.error(f"Error in memory update hook: {e}")
    
    def _get_behavior_type(self, strategy_type: StrategyType) -> BehaviorType:
        """Pobranie BehaviorType na podstawie StrategyType."""
        return self.config.strategy_to_behavior_type.get(
            strategy_type.name,
            BehaviorType.DECISION
        )
    
    def _get_analysis_type(self, strategy_type: StrategyType) -> AnalysisType:
        """Pobranie AnalysisType na podstawie StrategyType."""
        return self.config.strategy_to_analysis_type.get(
            strategy_type.name,
            AnalysisType.BEHAVIOR
        )
    
    def create_behavior_memory_entry(
        self,
        strategy: Strategy,
        result: StrategyResult
    ) -> Dict[str, Any]:
        """Utworzenie wpisu do Behavior Memory."""
        behavior_type = self._get_behavior_type(strategy.strategy_type)
        
        entry = {
            'memory_type': 'behavior_memory',
            'entry_id': str(uuid.uuid4()),
            'agent_id': strategy.agent_owner,
            'strategy_id': strategy.strategy_id,
            'behavior_type': behavior_type.name,
            'timestamp': datetime.now().isoformat(),
            'result_id': result.result_id,
            
            # Metryki
            'success': result.success,
            'score': result.score,
            'confidence': result.confidence,
            'execution_time_ms': result.execution_time_ms,
            
            # Kontekst strategii
            'strategy_name': strategy.name,
            'strategy_version': strategy.version,
            'strategy_status': strategy.status.name,
            
            # Metadane
            'metrics': result.metrics,
            'outcome': result.outcome,
            'errors': result.errors,
            'warnings': result.warnings,
            
            # Tagowanie
            'tags': strategy.tags + ['strategy_result', 'behavior_tracking']
        }
        
        return entry
    
    def create_decision_memory_entry(
        self,
        strategy: Strategy,
        result: StrategyResult,
        decision_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Utworzenie wpisu do Decision Memory."""
        decision_context = decision_context or {}
        
        entry = {
            'memory_type': 'decision_layer_memory',
            'entry_id': str(uuid.uuid4()),
            'agent_id': strategy.agent_owner,
            'strategy_id': strategy.strategy_id,
            'decision_type': 'strategy_execution',
            'timestamp': datetime.now().isoformat(),
            'result_id': result.result_id,
            
            # Kontekst decyzji
            'input_data': result.input_data,
            'output_data': result.output_data,
            'decision_outcome': result.outcome,
            'success': result.success,
            
            # Metryki decyzji
            'decision_quality': result.score,
            'confidence': result.confidence,
            'execution_time_ms': result.execution_time_ms,
            
            # Informacje o strategii
            'strategy_name': strategy.name,
            'strategy_type': strategy.strategy_type.name,
            'strategy_parameters': strategy.parameters.to_dict(),
            
            # Kontekst dodatkowy
            'context': decision_context,
            'resources_used': result.resources_used,
            
            # Tagowanie
            'tags': strategy.tags + ['strategy_decision', 'decision_tracking']
        }
        
        return entry
    
    def create_agent_analysis_entry(
        self,
        strategy: Strategy,
        evaluation: StrategyEvaluation
    ) -> Dict[str, Any]:
        """Utworzenie wpisu do Agent Analysis Memory."""
        analysis_type = self._get_analysis_type(strategy.strategy_type)
        
        entry = {
            'memory_type': 'agent_analysis_memory',
            'entry_id': str(uuid.uuid4()),
            'agent_id': strategy.agent_owner,
            'strategy_id': strategy.strategy_id,
            'analysis_type': analysis_type.name,
            'evaluation_id': evaluation.evaluation_id,
            'evaluator_agent_id': evaluation.evaluator_agent_id,
            'timestamp': datetime.now().isoformat(),
            
            # Ocena strategii
            'effectiveness': evaluation.effectiveness,
            'stability': evaluation.stability,
            'efficiency': evaluation.efficiency,
            'reliability': evaluation.reliability,
            'adaptability': evaluation.adaptability,
            'overall_score': evaluation.overall_score,
            'ranking_score': evaluation.ranking_score,
            
            # Statystyki strategii
            'strategy_success_rate': strategy.success_rate,
            'strategy_confidence': strategy.confidence,
            'strategy_usage_count': strategy.usage_count,
            'strategy_avg_score': strategy.avg_score,
            
            # Informacje o strategii
            'strategy_name': strategy.name,
            'strategy_version': strategy.version,
            'strategy_status': strategy.status.name,
            
            # Analiza
            'strengths': evaluation.strengths,
            'weaknesses': evaluation.weaknesses,
            'recommendations': evaluation.recommendations,
            'notes': evaluation.notes,
            
            # Tagowanie
            'tags': strategy.tags + ['strategy_analysis', 'performance_evaluation']
        }
        
        return entry
    
    def create_ranking_analysis_entry(
        self,
        strategy: Strategy,
        ranking: StrategyRanking
    ) -> Dict[str, Any]:
        """Utworzenie wpisu do Agent Analysis Memory na podstawie rankingu."""
        entry = {
            'memory_type': 'agent_analysis_memory',
            'entry_id': str(uuid.uuid4()),
            'agent_id': strategy.agent_owner,
            'strategy_id': strategy.strategy_id,
            'analysis_type': 'STRATEGY',  # Ranking jest analizą strategii
            'ranking_id': ranking.ranking_id,
            'timestamp': datetime.now().isoformat(),
            
            # Dane rankingu
            'rank': ranking.rank,
            'total_strategies': ranking.total_strategies,
            'percentile': ranking.percentile,
            'ranking_category': ranking.ranking_category,
            'ranking_score': strategy.ranking_score,
            'current_rank': strategy.current_rank,
            
            # Statystyki strategii
            'strategy_success_rate': strategy.success_rate,
            'strategy_confidence': strategy.confidence,
            'strategy_usage_count': strategy.usage_count,
            'strategy_avg_score': strategy.avg_score,
            
            # Informacje o strategii
            'strategy_name': strategy.name,
            'strategy_version': strategy.version,
            'strategy_status': strategy.status.name,
            'strategy_type': strategy.strategy_type.name,
            
            # Wagi użyte do rankingu
            'weights_used': ranking.weights_used,
            
            # Tagowanie
            'tags': strategy.tags + ['ranking_analysis', 'performance_ranking']
        }
        
        return entry
    
    def update_from_strategy_result(
        self,
        strategy: Strategy,
        result: StrategyResult
    ) -> List[Dict[str, Any]]:
        """
        Aktualizacja pamięci na podstawie wyniku strategii.
        
        Tworzy wpisy do:
        - Behavior Memory
        - Decision Memory
        
        Args:
            strategy: Strategia której dotyczy wynik
            result: Wynik wykonania strategii
            
        Returns:
            List[Dict]: Lista utworzonych wpisów pamięci
        """
        entries = []
        
        # Aktualizacja Behavior Memory
        if self.config.update_behavior_memory:
            behavior_entry = self.create_behavior_memory_entry(strategy, result)
            entries.append(behavior_entry)
            
            # Trigger hooków
            if self._on_memory_update_hooks:
                self._trigger_memory_update(
                    'behavior_memory',
                    strategy.agent_owner,
                    behavior_entry
                )
            
            logger.info(f"Behavior Memory updated for strategy {strategy.strategy_id} result")
        
        # Aktualizacja Decision Memory
        if self.config.update_decision_memory:
            decision_entry = self.create_decision_memory_entry(strategy, result)
            entries.append(decision_entry)
            
            # Trigger hooków
            if self._on_memory_update_hooks:
                self._trigger_memory_update(
                    'decision_layer_memory',
                    strategy.agent_owner,
                    decision_entry
                )
            
            logger.info(f"Decision Memory updated for strategy {strategy.strategy_id} result")
        
        return entries
    
    def update_from_strategy_evaluation(
        self,
        strategy: Strategy,
        evaluation: StrategyEvaluation
    ) -> List[Dict[str, Any]]:
        """
        Aktualizacja pamięci na podstawie oceny strategii.
        
        Tworzy wpisy do:
        - Agent Analysis Memory
        - Behavior Memory (aktualizacja)
        
        Args:
            strategy: Strategia której dotyczy ocena
            evaluation: Ocena strategii
            
        Returns:
            List[Dict]: Lista utworzonych wpisów pamięci
        """
        entries = []
        
        # Aktualizacja Agent Analysis Memory
        if self.config.update_agent_analysis_memory:
            analysis_entry = self.create_agent_analysis_entry(strategy, evaluation)
            entries.append(analysis_entry)
            
            # Trigger hooków
            if self._on_memory_update_hooks:
                self._trigger_memory_update(
                    'agent_analysis_memory',
                    strategy.agent_owner,
                    analysis_entry
                )
            
            logger.info(f"Agent Analysis Memory updated for strategy {strategy.strategy_id} evaluation")
        
        return entries
    
    def update_from_strategy_ranking(
        self,
        strategy: Strategy,
        ranking: StrategyRanking
    ) -> List[Dict[str, Any]]:
        """
        Aktualizacja pamięci na podstawie rankingu strategii.
        
        Tworzy wpisy do:
        - Agent Analysis Memory
        
        Args:
            strategy: Strategia której dotyczy ranking
            ranking: Ranking strategii
            
        Returns:
            List[Dict]: Lista utworzonych wpisów pamięci
        """
        entries = []
        
        # Aktualizacja Agent Analysis Memory
        if self.config.update_agent_analysis_memory:
            ranking_entry = self.create_ranking_analysis_entry(strategy, ranking)
            entries.append(ranking_entry)
            
            # Trigger hooków
            if self._on_memory_update_hooks:
                self._trigger_memory_update(
                    'agent_analysis_memory',
                    strategy.agent_owner,
                    ranking_entry
                )
            
            logger.info(f"Agent Analysis Memory updated for strategy {strategy.strategy_id} ranking")
        
        return entries
    
    def update_from_experiment_result(
        self,
        experiment: Experiment,
        result: ExperimentResult
    ) -> List[Dict[str, Any]]:
        """
        Aktualizacja pamięci na podstawie wyniku eksperymentu.
        
        Args:
            experiment: Eksperyment którego dotyczy wynik
            result: Wynik eksperymentu
            
        Returns:
            List[Dict]: Lista utworzonych wpisów pamięci
        """
        entries = []
        
        # Eksperyment nie jest bezpośrednio powiązany z pojedynczą strategią
        # ale można zaktualizować pamięć agenta na podstawie wyników
        
        # Tworzymy wpis do Agent Analysis Memory
        if self.config.update_agent_analysis_memory:
            analysis_entry = {
                'memory_type': 'agent_analysis_memory',
                'entry_id': str(uuid.uuid4()),
                'agent_id': experiment.agent_owner,
                'experiment_id': experiment.experiment_id,
                'analysis_type': 'EXPLORATION',
                'result_id': result.result_id,
                'timestamp': datetime.now().isoformat(),
                
                # Wyniki eksperymentu
                'experiment_success_rate': result.metrics.get('success_rate', 0.0),
                'avg_score': result.metrics.get('avg_score', 0.0),
                'confidence': result.confidence,
                'success': result.success,
                
                # Informacje o eksperymencie
                'experiment_name': experiment.name,
                'experiment_type': experiment.experiment_type.name,
                'strategy_id': experiment.strategy_id,
                
                # Tagowanie
                'tags': ['experiment_analysis', 'performance_testing']
            }
            
            entries.append(analysis_entry)
            
            # Trigger hooków
            if self._on_memory_update_hooks:
                self._trigger_memory_update(
                    'agent_analysis_memory',
                    experiment.agent_owner,
                    analysis_entry
                )
            
            logger.info(f"Agent Analysis Memory updated for experiment {experiment.experiment_id} result")
        
        return entries
    
    def update_from_experiment_comparison(
        self,
        comparison: ExperimentComparison
    ) -> List[Dict[str, Any]]:
        """
        Aktualizacja pamięci na podstawie porównania eksperymentów.
        
        Args:
            comparison: Porównanie eksperymentów
            
        Returns:
            List[Dict]: Lista utworzonych wpisów pamięci
        """
        entries = []
        
        if not comparison.winner_experiment_id:
            return entries
        
        # Pobranie eksperymentów (w prawdziwej implementacji z Experiment Manager)
        # Tu tworzymy wpis analizy na podstawie porównania
        
        if self.config.update_agent_analysis_memory:
            analysis_entry = {
                'memory_type': 'agent_analysis_memory',
                'entry_id': str(uuid.uuid4()),
                'agent_id': 'system',  # Będzie ustawione na podstawie kontekstu
                'comparison_id': comparison.comparison_id,
                'analysis_type': 'STRATEGY',
                'timestamp': datetime.now().isoformat(),
                
                # Wyniki porównania
                'compared_experiments': len(comparison.experiment_ids),
                'winner_experiment_id': comparison.winner_experiment_id,
                'conclusions': comparison.conclusions,
                'recommendations': comparison.recommendations,
                
                # Ranking eksperymentów
                'experiment_ranking': comparison.experiment_ranking,
                
                # Tagowanie
                'tags': ['experiment_comparison', 'strategy_analysis']
            }
            
            entries.append(analysis_entry)
            
            logger.info(f"Agent Analysis Memory updated for experiment comparison {comparison.comparison_id}")
        
        return entries
    
    def create_memory_update_message(
        self,
        memory_type: str,
        data: Dict[str, Any]
    ) -> SSIMessage:
        """
        Utworzenie wiadomości do aktualizacji pamięci.
        
        Args:
            memory_type: Typ pamięci (behavior_memory, decision_layer_memory, agent_analysis_memory)
            data: Dane do zapisania
            
        Returns:
            SSIMessage: Wiadomość do IFC
        """
        return create_message(
            sender='strategy_laboratory',
            receiver='memory_ecosystem',
            process_type=ProcessType.MEMORY_WRITE,
            priority=PriorityLevel.NORMAL,
            data=data,
            metadata={
                'memory_type': memory_type,
                'action': 'update',
                'source': 'strategy_laboratory'
            }
        )
    
    def batch_update_memory(
        self,
        entries: List[Dict[str, Any]]
    ) -> List[SSIMessage]:
        """
        Batchowa aktualizacja pamięci.
        
        Args:
            entries: Lista wpisów do aktualizacji
            
        Returns:
            List[SSIMessage]: Lista wiadomości do IFC
        """
        messages = []
        
        for entry in entries:
            message = self.create_memory_update_message(
                memory_type=entry.get('memory_type', 'unknown'),
                data=entry
            )
            messages.append(message)
        
        return messages
    
    def update_behavior_memory_from_strategy(
        self,
        strategy: Strategy
    ) -> Dict[str, Any]:
        """
        Aktualizacja Behavior Memory na podstawie obecnego stanu strategii.
        
        Tworzy wpis podsumowujący dotychczasowe zachowanie strategii.
        """
        behavior_type = self._get_behavior_type(strategy.strategy_type)
        
        entry = {
            'memory_type': 'behavior_memory',
            'entry_id': str(uuid.uuid4()),
            'agent_id': strategy.agent_owner,
            'strategy_id': strategy.strategy_id,
            'behavior_type': behavior_type.name,
            'timestamp': datetime.now().isoformat(),
            
            # Statystyki strategii
            'total_uses': strategy.usage_count,
            'success_count': strategy.success_count,
            'failure_count': strategy.failure_count,
            'success_rate': strategy.success_rate,
            'avg_score': strategy.avg_score,
            'confidence': strategy.confidence,
            
            # Informacje o strategii
            'strategy_name': strategy.name,
            'strategy_version': strategy.version,
            'strategy_status': strategy.status.name,
            'strategy_type': strategy.strategy_type.name,
            
            # Metadane
            'last_used': strategy.last_used.isoformat() if strategy.last_used else None,
            'last_evaluated': strategy.last_evaluation.isoformat() if strategy.last_evaluation else None,
            
            # Tagowanie
            'tags': strategy.tags + ['strategy_summary', 'behavior_profile']
        }
        
        return entry
    
    def generate_strategy_profile(
        self,
        strategy: Strategy
    ) -> Dict[str, Any]:
        """
        Generowanie profilu strategii do analizy.
        
        Args:
            strategy: Strategia do zanalizowania
            
        Returns:
            Dict: Profil strategii
        """
        return {
            'strategy_id': strategy.strategy_id,
            'agent_id': strategy.agent_owner,
            'name': strategy.name,
            'version': strategy.version,
            'type': strategy.strategy_type.name,
            'status': strategy.status.name,
            
            # Metryki
            'usage_count': strategy.usage_count,
            'success_rate': strategy.success_rate,
            'confidence': strategy.confidence,
            'avg_score': strategy.avg_score,
            'ranking_score': strategy.ranking_score,
            'current_rank': strategy.current_rank,
            
            # Parametry
            'parameters': strategy.parameters.to_dict(),
            
            # Opis
            'description': strategy.description,
            'purpose': strategy.purpose,
            'methodology': strategy.methodology,
            
            # Czas
            'created': strategy.creation_date.isoformat(),
            'last_used': strategy.last_used.isoformat() if strategy.last_used else None,
            'last_updated': strategy.last_updated.isoformat()
        }
    
    def get_memory_update_summary(
        self,
        strategy: Strategy
    ) -> Dict[str, Any]:
        """
        Pobranie podsumowania aktualizacji pamięci dla strategii.
        
        Args:
            strategy: Strategia do podsumowania
            
        Returns:
            Dict: Podsumowanie aktualizacji
        """
        return {
            'strategy_id': strategy.strategy_id,
            'agent_id': strategy.agent_owner,
            'last_result': strategy.results[-1] if strategy.results else None,
            'last_evaluation': strategy.evaluations[-1] if strategy.evaluations else None,
            'last_ranking': strategy.current_rank,
            'behavior_memory_updates': len([
                r for r in strategy.results
                if self.config.update_behavior_memory
            ]),
            'decision_memory_updates': len([
                r for r in strategy.results
                if self.config.update_decision_memory
            ]),
            'analysis_memory_updates': len([
                e for e in strategy.evaluations
                if self.config.update_agent_analysis_memory
            ])
        }


# Singleton
_memory_integrator: Optional[StrategyMemoryIntegrator] = None
_memory_integrator_lock = threading.Lock()


def create_memory_integrator(config: Optional[MemoryIntegratorConfig] = None) -> StrategyMemoryIntegrator:
    """Tworzenie nowej instancji Memory Integrator."""
    global _memory_integrator
    with _memory_integrator_lock:
        if _memory_integrator is None:
            _memory_integrator = StrategyMemoryIntegrator(config)
        return _memory_integrator


def get_memory_integrator() -> StrategyMemoryIntegrator:
    """Pobranie instancji singleton Memory Integrator."""
    global _memory_integrator
    if _memory_integrator is None:
        _memory_integrator = create_memory_integrator()
    return _memory_integrator


__all__ = [
    'MemoryIntegratorConfig',
    'StrategyMemoryIntegrator',
    'create_memory_integrator',
    'get_memory_integrator'
]
