"""
SSI V5 - IFC Integrator for Strategy Laboratory

Integracja Strategy Laboratory z Information Flow Controller.

Zasada: Wszystkie operacje laboratoryjne przechodzą przez IFC.

Schemat:
Agent
↓
IFC
↓
Validation
↓
Strategy Laboratory
↓
Memory Update

Wersja: 1.0.0
Data: 2026-08-01
"""

import threading
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import uuid

from SSI.v5.core.information_flow_controller.ifc_controller import (
    InformationFlowController,
    get_controller,
    IFCTStatistics
)
from SSI.v5.core.information_flow_controller.message_models import (
    SSIMessage,
    MessageResponse,
    MessageStatus,
    PriorityLevel,
    ProcessType,
    ModuleIdentifier
)
from SSI.v5.core.information_flow_controller.message_factory import (
    create_message,
    create_response_message,
    create_error_message
)
from SSI.v5.core.information_flow_controller.message_history import (
    MessageHistory,
    get_history
)

from .strategy_models import (
    Strategy,
    StrategyParameters,
    StrategyResult,
    StrategyEvaluation,
    StrategyRanking,
    StrategyStatus,
    StrategyType,
    StrategyVersion
)
from .experiment_models import (
    Experiment,
    ExperimentParameters,
    ExperimentResult,
    ExperimentComparison,
    ExperimentStatus,
    ExperimentType
)

# Konfiguracja logowania
logger = logging.getLogger(__name__)


@dataclass
class IFCIntegratorConfig:
    """Konfiguracja IFC Integrator."""
    
    # Ogólne
    use_ifc: bool = True
    enable_validation: bool = True
    enable_history: bool = True
    
    # priorytety
    default_priority: PriorityLevel = PriorityLevel.NORMAL
    strategy_creation_priority: PriorityLevel = PriorityLevel.HIGH
    experiment_creation_priority: PriorityLevel = PriorityLevel.HIGH
    evaluation_priority: PriorityLevel = PriorityLevel.NORMAL
    ranking_priority: PriorityLevel = PriorityLevel.LOW
    memory_update_priority: PriorityLevel = PriorityLevel.HIGH
    
    # Timeouty
    default_timeout_seconds: float = 30.0
    high_priority_timeout_seconds: float = 10.0
    
    # Moduły docelowe
    strategy_manager_target: str = "strategy_manager"
    experiment_manager_target: str = "experiment_manager"
    memory_ecosystem_target: str = "memory_ecosystem"
    teacher_engine_target: str = "teacher_engine"
    runtime_controller_target: str = "runtime_controller"
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika."""
        return {
            'use_ifc': self.use_ifc,
            'enable_validation': self.enable_validation,
            'enable_history': self.enable_history,
            'default_priority': self.default_priority.name,
            'strategy_creation_priority': self.strategy_creation_priority.name,
            'experiment_creation_priority': self.experiment_creation_priority.name,
            'evaluation_priority': self.evaluation_priority.name,
            'ranking_priority': self.ranking_priority.name,
            'memory_update_priority': self.memory_update_priority.name,
            'default_timeout_seconds': self.default_timeout_seconds,
            'high_priority_timeout_seconds': self.high_priority_timeout_seconds,
            'strategy_manager_target': self.strategy_manager_target,
            'experiment_manager_target': self.experiment_manager_target,
            'memory_ecosystem_target': self.memory_ecosystem_target
        }


class StrategyIFCIntegrator:
    """
    Główna klasa integracyjna Strategy Laboratory z IFC.
    
    Wszystkie operacje laboratoryjne przechodzą przez ten moduł.
    """
    
    def __init__(self, config: Optional[IFCIntegratorConfig] = None):
        self.config = config or IFCIntegratorConfig()
        self._ifc: Optional[InformationFlowController] = None
        self._lock = threading.RLock()
        
        # Hooki na odpowiedzi
        self._response_hooks: Dict[str, Callable] = {}
        self._message_hooks: List[Callable[[SSIMessage, MessageResponse], None]] = []
        
        # Statystyki
        self._stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'messages_failed': 0,
            'errors': []
        }
        
        logger.info(f"StrategyIFCIntegrator initialized with config: {self.config.to_dict()}")
    
    @property
    def ifc(self) -> InformationFlowController:
        """Pobranie instancji IFC."""
        if self._ifc is None:
            self._ifc = get_controller()
        return self._ifc
    
    def on_response(self, message_id: str, callback: Callable[[MessageResponse], None]) -> None:
        """Rejestracja callbacka na odpowiedź."""
        self._response_hooks[message_id] = callback
    
    def on_message(self, callback: Callable[[SSIMessage, MessageResponse], None]) -> None:
        """Rejestracja hooka na wiadomości."""
        self._message_hooks.append(callback)
    
    def _get_priority(self, process_type: ProcessType) -> PriorityLevel:
        """Pobranie priorytetu na podstawie typu procesu."""
        priority_map = {
            ProcessType.STRATEGY_CREATE: self.config.strategy_creation_priority,
            ProcessType.STRATEGY_TEST: self.config.strategy_creation_priority,
            ProcessType.STRATEGY_UPDATE: self.config.strategy_creation_priority,
            ProcessType.STRATEGY_RANKING: self.config.ranking_priority,
            ProcessType.DECISION_REQUEST: PriorityLevel.HIGH,
            ProcessType.DECISION_ANALYSIS: PriorityLevel.HIGH,
            ProcessType.MEMORY_WRITE: self.config.memory_update_priority,
            ProcessType.MEMORY_UPDATE: self.config.memory_update_priority
        }
        
        return priority_map.get(process_type, self.config.default_priority)
    
    def _get_timeout(self, priority: PriorityLevel) -> float:
        """Pobranie timeoutu na podstawie priorytetu."""
        timeout_map = {
            PriorityLevel.CRITICAL: 5.0,
            PriorityLevel.HIGH: self.config.high_priority_timeout_seconds,
        }
        
        return timeout_map.get(priority, self.config.default_timeout_seconds)
    
    def send_message(self, message: SSIMessage) -> MessageResponse:
        """
        Wysłanie wiadomości przez IFC.
        
        Args:
            message: Wiadomość do wysłania
            
        Returns:
            MessageResponse: Odpowiedź z IFC
        """
        if not self.config.use_ifc:
            # Symulacja odpowiedzi
            return MessageResponse(
                message_id=message.message_id,
                status=MessageStatus.PROCESSED,
                response_data={'simulated': True, 'message': 'IFC disabled'},
                timestamp=datetime.now()
            )
        
        try:
            # Ustawienie priorytetu jeśli nie ustawiono
            if message.priority == PriorityLevel.NORMAL and hasattr(message, 'process_type'):
                message.priority = self._get_priority(message.process_type)
            
            # Wysłanie wiadomości
            response = self.ifc.send_message(message)
            
            # Zaktualizowanie statystyk
            self._stats['messages_sent'] += 1
            
            # Wywołanie hooków na odpowiedź
            if message.message_id in self._response_hooks:
                callback = self._response_hooks.pop(message.message_id)
                callback(response)
            
            return response
            
        except Exception as e:
            self._stats['messages_failed'] += 1
            self._stats['errors'].append(str(e))
            logger.error(f"Error sending message {message.message_id}: {e}")
            
            return create_error_message(
                message=message,
                error=str(e),
                status=MessageStatus.FAILED
            )
    
    def send_message_async(self, message: SSIMessage, callback: Callable[[MessageResponse], None] = None) -> str:
        """
        Asynchroniczne wysłanie wiadomości.
        
        Args:
            message: Wiadomość do wysłania
            callback: Callback na odpowiedź
            
        Returns:
            str: ID wiadomości
        """
        if callback:
            self.on_response(message.message_id, callback)
        
        # W prawdziwej implementacji tutaj byłoby asynchroniczne wysłanie
        # Na razie wysyłamy synchronicznie w tle
        import threading
        def async_send():
            try:
                response = self.send_message(message)
                if callback:
                    callback(response)
            except Exception as e:
                logger.error(f"Error in async message send: {e}")
        
        thread = threading.Thread(target=async_send, daemon=True)
        thread.start()
        
        return message.message_id
    
    def create_strategy_message(
        self,
        agent_id: str,
        strategy_data: Dict[str, Any],
        **kwargs
    ) -> SSIMessage:
        """
        Utworzenie wiadomości do tworzenia strategii.
        
        Args:
            agent_id: ID agenta
            strategy_data: Dane strategii
            **kwargs: Dodatkowe parametry
            
        Returns:
            SSIMessage: Wiadomość do IFC
        """
        data = {
            'action': 'create_strategy',
            'agent_id': agent_id,
            'strategy_data': strategy_data,
            'kwargs': kwargs
        }
        
        return create_message(
            sender='strategy_laboratory',
            receiver=self.config.strategy_manager_target,
            process_type=ProcessType.STRATEGY_CREATE,
            priority=self.config.strategy_creation_priority,
            data=data,
            metadata={
                'module': 'strategy_laboratory',
                'function': 'create_strategy',
                'source': 'ifc_integrator'
            }
        )
    
    def create_experiment_message(
        self,
        agent_id: str,
        experiment_data: Dict[str, Any],
        **kwargs
    ) -> SSIMessage:
        """
        Utworzenie wiadomości do tworzenia eksperymentu.
        
        Args:
            agent_id: ID agenta
            experiment_data: Dane eksperymentu
            **kwargs: Dodatkowe parametry
            
        Returns:
            SSIMessage: Wiadomość do IFC
        """
        data = {
            'action': 'create_experiment',
            'agent_id': agent_id,
            'experiment_data': experiment_data,
            'kwargs': kwargs
        }
        
        return create_message(
            sender='strategy_laboratory',
            receiver=self.config.experiment_manager_target,
            process_type=ProcessType.DEVELOPER_TEST,  # Eksperyment jako test
            priority=self.config.experiment_creation_priority,
            data=data,
            metadata={
                'module': 'strategy_laboratory',
                'function': 'create_experiment',
                'source': 'ifc_integrator'
            }
        )
    
    def create_evaluation_message(
        self,
        evaluator_id: str,
        strategy_id: str,
        evaluation_data: Dict[str, Any],
        **kwargs
    ) -> SSIMessage:
        """
        Utworzenie wiadomości do oceny strategii.
        
        Args:
            evaluator_id: ID agenta oceniającego
            strategy_id: ID strategii
            evaluation_data: Dane oceny
            **kwargs: Dodatkowe parametry
            
        Returns:
            SSIMessage: Wiadomość do IFC
        """
        data = {
            'action': 'evaluate_strategy',
            'evaluator_id': evaluator_id,
            'strategy_id': strategy_id,
            'evaluation_data': evaluation_data,
            'kwargs': kwargs
        }
        
        return create_message(
            sender='strategy_laboratory',
            receiver=self.config.strategy_manager_target,
            process_type=ProcessType.TEACHER_EVALUATION,
            priority=self.config.evaluation_priority,
            data=data,
            metadata={
                'module': 'strategy_laboratory',
                'function': 'evaluate_strategy',
                'source': 'ifc_integrator'
            }
        )
    
    def create_ranking_message(
        self,
        agent_id: Optional[str] = None,
        ranking_data: Dict[str, Any] = None,
        **kwargs
    ) -> SSIMessage:
        """
        Utworzenie wiadomości do rankingu strategii.
        
        Args:
            agent_id: ID agenta (opcjonalnie)
            ranking_data: Dane rankingu (opcjonalnie)
            **kwargs: Dodatkowe parametry
            
        Returns:
            SSIMessage: Wiadomość do IFC
        """
        data = {
            'action': 'rank_strategies',
            'agent_id': agent_id,
            'ranking_data': ranking_data or {},
            'kwargs': kwargs
        }
        
        return create_message(
            sender='strategy_laboratory',
            receiver=self.config.strategy_manager_target,
            process_type=ProcessType.STRATEGY_RANKING,
            priority=self.config.ranking_priority,
            data=data,
            metadata={
                'module': 'strategy_laboratory',
                'function': 'rank_strategies',
                'source': 'ifc_integrator'
            }
        )
    
    def create_memory_update_message(
        self,
        memory_type: str,
        data: Dict[str, Any],
        **kwargs
    ) -> SSIMessage:
        """
        Utworzenie wiadomości do aktualizacji pamięci.
        
        Args:
            memory_type: Typ pamięci
            data: Dane do aktualizacji
            **kwargs: Dodatkowe parametry
            
        Returns:
            SSIMessage: Wiadomość do IFC
        """
        return create_message(
            sender='strategy_laboratory',
            receiver=self.config.memory_ecosystem_target,
            process_type=ProcessType.MEMORY_WRITE,
            priority=self.config.memory_update_priority,
            data=data,
            metadata={
                'memory_type': memory_type,
                'module': 'strategy_laboratory',
                'function': 'update_memory',
                'source': 'ifc_integrator',
                'kwargs': kwargs
            }
        )
    
    # Metody wysokiego poziomu (wrappery)
    
    def create_strategy(
        self,
        agent_id: str,
        name: str,
        strategy_type: Union[str, StrategyType] = StrategyType.DECISION,
        description: str = "",
        parameters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> MessageResponse:
        """
        Tworzenie strategii przez IFC.
        
        Args:
            agent_id: ID agenta
            name: Nazwa strategii
            strategy_type: Typ strategii
            description: Opis strategii
            parameters: Parametry strategii
            **kwargs: Dodatkowe parametry
            
        Returns:
            MessageResponse: Odpowiedź z IFC
        """
        strategy_type_name = strategy_type if isinstance(strategy_type, str) else strategy_type.name
        
        strategy_data = {
            'name': name,
            'strategy_type': strategy_type_name,
            'description': description,
            'parameters': parameters or {},
            'version': kwargs.get('version', '1.0.0'),
            'category': kwargs.get('category', 'default'),
            'tags': kwargs.get('tags', []),
            'purpose': kwargs.get('purpose', ''),
            'methodology': kwargs.get('methodology', '')
        }
        
        message = self.create_strategy_message(agent_id, strategy_data, **kwargs)
        return self.send_message(message)
    
    def update_strategy(
        self,
        strategy_id: str,
        updates: Dict[str, Any],
        **kwargs
    ) -> MessageResponse:
        """
        Aktualizacja strategii przez IFC.
        
        Args:
            strategy_id: ID strategii
            updates: Aktualizacje
            **kwargs: Dodatkowe parametry
            
        Returns:
            MessageResponse: Odpowiedź z IFC
        """
        data = {
            'action': 'update_strategy',
            'strategy_id': strategy_id,
            'updates': updates,
            'kwargs': kwargs
        }
        
        message = create_message(
            sender='strategy_laboratory',
            receiver=self.config.strategy_manager_target,
            process_type=ProcessType.STRATEGY_UPDATE,
            priority=self.config.strategy_creation_priority,
            data=data,
            metadata={
                'module': 'strategy_laboratory',
                'function': 'update_strategy',
                'source': 'ifc_integrator'
            }
        )
        
        return self.send_message(message)
    
    def evaluate_strategy(
        self,
        evaluator_id: str,
        strategy_id: str,
        effectiveness: float = 0.0,
        stability: float = 0.0,
        efficiency: float = 0.0,
        reliability: float = 0.0,
        adaptability: float = 0.0,
        confidence: float = 0.0,
        **kwargs
    ) -> MessageResponse:
        """
        Ocena strategii przez IFC.
        
        Args:
            evaluator_id: ID agenta oceniającego
            strategy_id: ID strategii
            effectiveness: Skuteczność
            stability: Stabilność
            efficiency: Wydajność
            reliability: Niezawodność
            adaptability: Dostosowalność
            confidence: Pewność
            **kwargs: Dodatkowe parametry
            
        Returns:
            MessageResponse: Odpowiedź z IFC
        """
        evaluation_data = {
            'effectiveness': effectiveness,
            'stability': stability,
            'efficiency': efficiency,
            'reliability': reliability,
            'adaptability': adaptability,
            'confidence': confidence,
            'strengths': kwargs.get('strengths', []),
            'weaknesses': kwargs.get('weaknesses', []),
            'recommendations': kwargs.get('recommendations', []),
            'notes': kwargs.get('notes', '')
        }
        
        message = self.create_evaluation_message(evaluator_id, strategy_id, evaluation_data, **kwargs)
        return self.send_message(message)
    
    def rank_strategies(
        self,
        agent_id: Optional[str] = None,
        limit: int = 10,
        **kwargs
    ) -> MessageResponse:
        """
        Ranking strategii przez IFC.
        
        Args:
            agent_id: ID agenta (opcjonalnie)
            limit: Limit wyników
            **kwargs: Dodatkowe parametry
            
        Returns:
            MessageResponse: Odpowiedź z IFC
        """
        ranking_data = {
            'limit': limit,
            **kwargs
        }
        
        message = self.create_ranking_message(agent_id, ranking_data, **kwargs)
        return self.send_message(message)
    
    def archive_strategy(
        self,
        strategy_id: str,
        reason: str = "Manual archive",
        **kwargs
    ) -> MessageResponse:
        """
        Archiwizacja strategii przez IFC.
        
        Args:
            strategy_id: ID strategii
            reason: Powód archiwizacji
            **kwargs: Dodatkowe parametry
            
        Returns:
            MessageResponse: Odpowiedź z IFC
        """
        data = {
            'action': 'archive_strategy',
            'strategy_id': strategy_id,
            'reason': reason,
            'kwargs': kwargs
        }
        
        message = create_message(
            sender='strategy_laboratory',
            receiver=self.config.strategy_manager_target,
            process_type=ProcessType.SYSTEM_STATUS,
            priority=PriorityLevel.NORMAL,
            data=data,
            metadata={
                'module': 'strategy_laboratory',
                'function': 'archive_strategy',
                'source': 'ifc_integrator'
            }
        )
        
        return self.send_message(message)
    
    def create_experiment(
        self,
        agent_id: str,
        strategy_id: str,
        name: str,
        experiment_type: Union[str, ExperimentType] = ExperimentType.A_B_TESTING,
        description: str = "",
        **kwargs
    ) -> MessageResponse:
        """
        Tworzenie eksperymentu przez IFC.
        
        Args:
            agent_id: ID agenta
            strategy_id: ID strategii
            name: Nazwa eksperymentu
            experiment_type: Typ eksperymentu
            description: Opis eksperymentu
            **kwargs: Dodatkowe parametry
            
        Returns:
            MessageResponse: Odpowiedź z IFC
        """
        experiment_type_name = experiment_type if isinstance(experiment_type, str) else experiment_type.name
        
        experiment_data = {
            'name': name,
            'strategy_id': strategy_id,
            'experiment_type': experiment_type_name,
            'description': description,
            'hypothesis': kwargs.get('hypothesis', ''),
            'objectives': kwargs.get('objectives', [])
        }
        
        message = self.create_experiment_message(agent_id, experiment_data, **kwargs)
        return self.send_message(message)
    
    def run_experiment(
        self,
        experiment_id: str,
        **kwargs
    ) -> MessageResponse:
        """
        Uruchomienie eksperymentu przez IFC.
        
        Args:
            experiment_id: ID eksperymentu
            **kwargs: Dodatkowe parametry
            
        Returns:
            MessageResponse: Odpowiedź z IFC
        """
        data = {
            'action': 'run_experiment',
            'experiment_id': experiment_id,
            'kwargs': kwargs
        }
        
        message = create_message(
            sender='strategy_laboratory',
            receiver=self.config.experiment_manager_target,
            process_type=ProcessType.DEVELOPER_TEST,
            priority=self.config.experiment_creation_priority,
            data=data,
            metadata={
                'module': 'strategy_laboratory',
                'function': 'run_experiment',
                'source': 'ifc_integrator'
            }
        )
        
        return self.send_message(message)
    
    def compare_experiment_results(
        self,
        experiment_ids: List[str],
        **kwargs
    ) -> MessageResponse:
        """
        Porównanie wyników eksperymentów przez IFC.
        
        Args:
            experiment_ids: Lista ID eksperymentów
            **kwargs: Dodatkowe parametry
            
        Returns:
            MessageResponse: Odpowiedź z IFC
        """
        data = {
            'action': 'compare_results',
            'experiment_ids': experiment_ids,
            'kwargs': kwargs
        }
        
        message = create_message(
            sender='strategy_laboratory',
            receiver=self.config.experiment_manager_target,
            process_type=ProcessType.DEVELOPER_ANALYSIS,
            priority=self.config.evaluation_priority,
            data=data,
            metadata={
                'module': 'strategy_laboratory',
                'function': 'compare_results',
                'source': 'ifc_integrator'
            }
        )
        
        return self.send_message(message)
    
    def update_memory(
        self,
        memory_type: str,
        data: Dict[str, Any],
        **kwargs
    ) -> MessageResponse:
        """
        Aktualizacja pamięci przez IFC.
        
        Args:
            memory_type: Typ pamięci
            data: Dane do aktualizacji
            **kwargs: Dodatkowe parametry
            
        Returns:
            MessageResponse: Odpowiedź z IFC
        """
        message = self.create_memory_update_message(memory_type, data, **kwargs)
        return self.send_message(message)
    
    def get_strategy(
        self,
        strategy_id: str
    ) -> MessageResponse:
        """
        Pobranie strategii przez IFC.
        
        Args:
            strategy_id: ID strategii
            
        Returns:
            MessageResponse: Odpowiedź z IFC
        """
        data = {
            'action': 'get_strategy',
            'strategy_id': strategy_id
        }
        
        message = create_message(
            sender='strategy_laboratory',
            receiver=self.config.strategy_manager_target,
            process_type=ProcessType.MEMORY_READ,
            priority=PriorityLevel.NORMAL,
            data=data,
            metadata={
                'module': 'strategy_laboratory',
                'function': 'get_strategy',
                'source': 'ifc_integrator'
            }
        )
        
        return self.send_message(message)
    
    def get_experiment(
        self,
        experiment_id: str
    ) -> MessageResponse:
        """
        Pobranie eksperymentu przez IFC.
        
        Args:
            experiment_id: ID eksperymentu
            
        Returns:
            MessageResponse: Odpowiedź z IFC
        """
        data = {
            'action': 'get_experiment',
            'experiment_id': experiment_id
        }
        
        message = create_message(
            sender='strategy_laboratory',
            receiver=self.config.experiment_manager_target,
            process_type=ProcessType.MEMORY_READ,
            priority=PriorityLevel.NORMAL,
            data=data,
            metadata={
                'module': 'strategy_laboratory',
                'function': 'get_experiment',
                'source': 'ifc_integrator'
            }
        )
        
        return self.send_message(message)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Pobranie statystyk integratora."""
        return {
            **self._stats,
            'ifc_stats': self.ifc.get_statistics().to_dict() if self._ifc else {},
            'config': self.config.to_dict()
        }
    
    def reset_statistics(self) -> None:
        """Reset statystyk."""
        self._stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'messages_failed': 0,
            'errors': []
        }


# Singleton
_ifc_integrator: Optional[StrategyIFCIntegrator] = None
_ifc_integrator_lock = threading.Lock()


def create_ifc_integrator(config: Optional[IFCIntegratorConfig] = None) -> StrategyIFCIntegrator:
    """Tworzenie nowej instancji IFC Integrator."""
    global _ifc_integrator
    with _ifc_integrator_lock:
        if _ifc_integrator is None:
            _ifc_integrator = StrategyIFCIntegrator(config)
        return _ifc_integrator


def get_ifc_integrator() -> StrategyIFCIntegrator:
    """Pobranie instancji singleton IFC Integrator."""
    global _ifc_integrator
    if _ifc_integrator is None:
        _ifc_integrator = create_ifc_integrator()
    return _ifc_integrator


__all__ = [
    'IFCIntegratorConfig',
    'StrategyIFCIntegrator',
    'create_ifc_integrator',
    'get_ifc_integrator'
]
