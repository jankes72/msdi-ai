# SSI V5 Agent Layer - Decision Engine
# ==================================================
#
# ETAP: 5.2.4 FAZA 4
# Data: 2026-08-03
# 
# Odpowiedzialnosc:
# - Podejmowanie decyzji przez agenta
# - Integracja z modelem poznawczym
# - Wykorzystanie kontekstu świata do podejmowania optymalnych decyzji
# - Zapisywanie historii decyzji

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Callable
from enum import Enum
from datetime import datetime
import uuid
import copy
import random
import numpy as np


class DecisionType(Enum):
    """Typy decyzji"""
    MODEL_SELECTION = "model_selection"      # Wybór modelu
    WEIGHT_ADJUSTMENT = "weight_adjustment"  # Dostosowanie wag
    STRATEGY_CHANGE = "strategy_change"      # Zmiana strategii
    ACTION_EXECUTION = "action_execution"    # Wykonywanie działań
    OBSERVATION = "observation"              # Obserwacja
    OPTIMIZATION = "optimization"            # Optymalizacja


class DecisionStatus(Enum):
    """Statusy decyzji"""
    PENDING = "pending"              # Oczekuje na realizację
    EXECUTED = "executed"            # Zrealizowana
    FAILED = "failed"                # Nieudana
    ROOLBACK = "rollback"            # Wycoowana


@dataclass
class Decision:
    """Pojedyncza decyzja agenta"""
    decision_id: str
    decision_type: DecisionType
    agent_id: str
    context: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    priority: int = 0
    status: DecisionStatus = DecisionStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            'decision_id': self.decision_id,
            'decision_type': self.decision_type.value,
            'agent_id': self.agent_id,
            'context': copy.deepcopy(self.context),
            'parameters': copy.deepcopy(self.parameters),
            'confidence': self.confidence,
            'priority': self.priority,
            'status': self.status.value,
            'result': copy.deepcopy(self.result) if self.result else None,
            'created_at': self.created_at.isoformat(),
            'executed_at': self.executed_at.isoformat() if self.executed_at else None
        }
    
    def mark_as_executed(self, result: Dict[str, Any]) -> None:
        """Oznaczenie jako zrealizowaną"""
        self.status = DecisionStatus.EXECUTED
        self.result = copy.deepcopy(result)
        self.executed_at = datetime.now()
    
    def mark_as_failed(self, error: str) -> None:
        """Oznaczenie jako nieudaną"""
        self.status = DecisionStatus.FAILED
        self.result = {'error': error}
        self.executed_at = datetime.now()
    
    def rollback(self, reason: str) -> None:
        """Wycofaniedecyzji"""
        self.status = DecisionStatus.ROOLBACK
        self.result = {'rollback_reason': reason}
        self.executed_at = datetime.now()


@dataclass
class DecisionContext:
    """Kontekst podejmowania decyzji"""
    world_data: Dict[str, Any] = field(default_factory=dict)
    model_info: Dict[str, Any] = field(default_factory=dict)
    weights: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    risk_factors: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def calculate_confidence(self) -> float:
        """Obliczenie współczynnika pewności"""
        # Bazowy współczynnik pewności
        confidence = 0.5
        
        # Analiza rekomendacji - ich waga i jakość
        if self.recommendations:
            total_weight = sum(rec.get('weight', 1.0) for rec in self.recommendations)
            avg_confidence = sum(rec.get('confidence', 0.5) for rec in self.recommendations) / len(self.recommendations)
            confidence = min(1.0, confidence + (avg_confidence * 0.3))
        
        # Analiza informacji o modelu
        if self.model_info:
            model_scores = [v for v in self.model_info.values() if isinstance(v, (int, float))]
            if model_scores:
                avg_score = sum(model_scores) / len(model_scores)
                confidence = min(1.0, confidence + (avg_score * 0.2))
        
        # Analiza czynników ryzyka
        if self.risk_factors:
            risk_values = [v for v in self.risk_factors.values() if isinstance(v, float)]
            if risk_values:
                avg_risk = sum(risk_values) / len(risk_values)
                # Im wyższe ryzyko, tym niższa pewność
                confidence = max(0.0, confidence - (avg_risk * 0.2))
        
        return confidence


class DecisionEngine:
    """
    Silnik decyzji - podejmuje decyzje na podstawie kontekstu świata.
    
    Odpowiedzialność:
    - Podejmowanie decyzji osobistej
    - Wykorzystanie kontekstu od Teacher Layer
    - Integracja z agent memory
    """
    
    def __init__(self, agent_id: str):
        """
        Inicjalizacja Decision Engine.
        
        Args:
            agent_id: ID agenta
        """
        self.agent_id = agent_id
        self.memory: Optional[Any] = None  # Referencja do AgentMemory
        
        # Historia decyzji
        self.decision_history: List[Decision] = []
        self.decision_queue: List[Decision] = []
        self.current_decision: Optional[Decision] = None
        
        # Kontekst
        self.current_context: Optional[DecisionContext] = None
        self._contract_data: Optional[Dict[str, Any]] = None
        
        # Statystyki
        self.total_decisions = 0
        self.successful_decisions = 0
        self.failed_decisions = 0
        
        # Rejestry callbacków
        self._decision_callbacks: List[Callable] = []
        
        # Flagi
        self._initialized = False
    
    def initialize(self) -> Dict[str, Any]:
        """
        Inicjalizacja silnika decyzji.
        
        Returns:
            Status inicjalizacji
        """
        if self._initialized:
            return {
                'status': 'success',
                'message': 'DecisionEngine already initialized',
                'agent_id': self.agent_id
            }
        
        try:
            self._initialized = True
            
            return {
                'status': 'success',
                'message': 'DecisionEngine initialized',
                'agent_id': self.agent_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Initialization failed: {str(e)}',
                'agent_id': self.agent_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def receive_contract(self, contract: Any) -> None:
        """
        Odbiór kontraktu od Pipeline/Teacher Layer.
        
        Args:
            contract: Kontrakt danych (AgentContract)
        """
        if hasattr(contract, 'to_dict'):
            self._contract_data = contract.to_dict()
        else:
            self._contract_data = copy.deepcopy(contract)
        
        # Utworzenie kontekstu z kontraktu
        self.current_context = DecisionContext(
            world_data=self._contract_data.get('world_data', {}),
            model_info=self._contract_data.get('model_evaluation', {}),
            weights=self._contract_data.get('current_weights', {}),
            recommendations=self._contract_data.get('recommendations', []),
            timestamp=datetime.now()
        )
        
        # Zapisanie w pamięci
        if self.memory:
            context_record = {
                'type': 'decision_context',
                'contract_id': self._contract_data.get('contract_id', ''),
                'cycle_id': self._contract_data.get('cycle_id', ''),
                'world_data_keys': list(self.current_context.world_data.keys()),
                'model_info_keys': list(self.current_context.model_info.keys()),
                'weights_keys': list(self.current_context.weights.keys()),
                'recommendations_count': len(self.current_context.recommendations),
                'timestamp': datetime.now().isoformat()
            }
            self.memory.store_in_short_term(f"decision_context_{datetime.now().isoformat()}", context_record)
    
    def make_decision(self, **kwargs) -> Dict[str, Any]:
        """
        Podejmowanie decyzji na podstawie dostępnego kontekstu.
        
        Args:
            **kwargs: Dodatkowe parametry kontekstu
            
        Returns:
            Decyzja w formie słownika
        """
        # Aktualizacja kontekstu z dodatkowych parametrów
        if kwargs:
            self._update_context_from_kwargs(**kwargs)
        
        if not self.current_context:
            self.current_context = DecisionContext(timestamp=datetime.now())
        
        # Obliczenie pewności
        confidence = self.current_context.calculate_confidence()
        
        # Wybór typu decyzji na podstawie kontekstu
        decision_type = self._select_decision_type()
        
        # Generowanie decyzji
        decision_data = self._generate_decision(decision_type, confidence)
        
        # Utworzenie obiektu decyzji
        decision = Decision(
            decision_id=f"dec_{uuid.uuid4().hex[:8]}",
            decision_type=decision_type,
            agent_id=self.agent_id,
            context=self._get_context_dict(),
            parameters=decision_data.get('parameters', {}),
            confidence=confidence,
            priority=self._calculate_priority(decision_type, confidence),
            created_at=datetime.now()
        )
        
        # Zapisanie historii
        self.decision_history.append(decision)
        self.total_decisions += 1
        
        # Zapisanie w pamięci
        if self.memory:
            self.memory.add_decision(decision.to_dict())
        
        return decision.to_dict()
    
    def _update_context_from_kwargs(self, **kwargs) -> None:
        """Aktualizacja kontekstu z dodatkowych parametrów"""
        if not self.current_context:
            self.current_context = DecisionContext(timestamp=datetime.now())
        
        if 'world_context' in kwargs:
            self.current_context.world_data.update(kwargs['world_context'])
        if 'model_info' in kwargs:
            self.current_context.model_info.update(kwargs['model_info'])
        if 'weights' in kwargs:
            self.current_context.weights.update(kwargs['weights'])
        if 'recommendations' in kwargs:
            self.current_context.recommendations.extend(kwargs['recommendations'])
        if 'risk_factors' in kwargs:
            self.current_context.risk_factors.update(kwargs['risk_factors'])
        if 'constraints' in kwargs:
            self.current_context.constraints.update(kwargs['constraints'])
    
    def _select_decision_type(self) -> DecisionType:
        """Wybór typu decyzji na podstawie kontekstu"""
        if not self.current_context:
            return DecisionType.ACTION_EXECUTION
        
        # Analiza kontekstu w celu wyboru typu decyzji
        context_keys = list(self.current_context.world_data.keys())
        model_info_keys = list(self.current_context.model_info.keys())
        recommendations_count = len(self.current_context.recommendations)
        weights_count = len(self.current_context.weights)
        
        # Jeśli są rekomendacje, możemy podejmować decyzję o działaniu
        if recommendations_count > 0:
            return DecisionType.ACTION_EXECUTION
        
        # Jeśli są informacje o modelu, możemy wybierać model
        if model_info_keys:
            return DecisionType.MODEL_SELECTION
        
        # Jeśli są wagi, możemy dostosowywać wagi
        if weights_count > 0:
            return DecisionType.WEIGHT_ADJUSTMENT
        
        # Domyślnie - wykonywanie działania
        return DecisionType.ACTION_EXECUTION
    
    def _generate_decision(self, decision_type: DecisionType, confidence: float) -> Dict[str, Any]:
        """Generowanie konkretnej decyzji na podstawie typu"""
        
        if decision_type == DecisionType.MODEL_SELECTION:
            return self._generate_model_selection_decision(confidence)
        
        elif decision_type == DecisionType.WEIGHT_ADJUSTMENT:
            return self._generate_weight_adjustment_decision(confidence)
        
        elif decision_type == DecisionType.STRATEGY_CHANGE:
            return self._generate_strategy_change_decision(confidence)
        
        elif decision_type == DecisionType.ACTION_EXECUTION:
            return self._generate_action_execution_decision(confidence)
        
        elif decision_type == DecisionType.OBSERVATION:
            return self._generate_observation_decision(confidence)
        
        elif decision_type == DecisionType.OPTIMIZATION:
            return self._generate_optimization_decision(confidence)
        
        else:
            # Domyślna decyzja
            return {
                'decision_type': decision_type.value,
                'action': 'default_action',
                'parameters': {},
                'confidence': confidence
            }
    
    def _generate_model_selection_decision(self, confidence: float) -> Dict[str, Any]:
        """Generowanie decyzji o wyborze modelu"""
        if not self.current_context or not self.current_context.model_info:
            return {
                'decision_type': DecisionType.MODEL_SELECTION.value,
                'action': 'select_default_model',
                'parameters': {'model_name': 'default'},
                'confidence': min(0.3, confidence)
            }
        
        # Wybór najlepszego modelu na podstawie dostępnych informacji
        best_model = None
        best_score = -1
        
        for model_name, model_info in self.current_context.model_info.items():
            if isinstance(model_info, dict):
                score = model_info.get('accuracy', model_info.get('score', 0.5))
                if score > best_score:
                    best_score = score
                    best_model = model_name
        
        if best_model:
            return {
                'decision_type': DecisionType.MODEL_SELECTION.value,
                'action': 'select_model',
                'parameters': {
                    'model_name': best_model,
                    'confidence_score': best_score,
                    'evaluation': self.current_context.model_info.get(best_model, {})
                },
                'confidence': min(1.0, confidence + best_score * 0.3)
            }
        else:
            # Wybór losowy, jeśli nie ma wystarczających informacji
            model_names = list(self.current_context.model_info.keys())
            selected_model = random.choice(model_names) if model_names else 'default'
            return {
                'decision_type': DecisionType.MODEL_SELECTION.value,
                'action': 'select_random_model',
                'parameters': {'model_name': selected_model},
                'confidence': 0.3
            }
    
    def _generate_weight_adjustment_decision(self, confidence: float) -> Dict[str, Any]:
        """Generowanie decyzji o dostosowaniu wag"""
        if not self.current_context or not self.current_context.weights:
            return {
                'decision_type': DecisionType.WEIGHT_ADJUSTMENT.value,
                'action': 'no_weight_change',
                'parameters': {},
                'confidence': confidence
            }
        
        # Analiza wag i rekomendacji
        weight_adjustments = {}
        
        if self.current_context.recommendations:
            # Wykorzystanie rekomendacji do dostosowania wag
            for recommendation in self.current_context.recommendations:
                if 'weight_adjustment' in recommendation:
                    weight_adjustments.update(recommendation['weight_adjustment'])
        
        if weight_adjustments:
            return {
                'decision_type': DecisionType.WEIGHT_ADJUSTMENT.value,
                'action': 'adjust_weights',
                'parameters': {
                    'adjustments': weight_adjustments,
                    'base_weights': copy.deepcopy(self.current_context.weights),
                    'recommendation_count': len(self.current_context.recommendations)
                },
                'confidence': confidence
            }
        else:
            # Powolne dostosowanie wag na podstawie losowych zmian
            selected_keys = random.sample(
                list(self.current_context.weights.keys()),
                min(2, len(self.current_context.weights))
            )
            adjustments = {}
            for key in selected_keys:
                current_value = self.current_context.weights.get(key, 0.5)
                # Losowe dostosowanie w zakresie -0.2 do +0.2
                adjustment = random.uniform(-0.2, 0.2)
                new_value = max(0.0, min(1.0, current_value + adjustment))
                adjustments[key] = new_value
            
            return {
                'decision_type': DecisionType.WEIGHT_ADJUSTMENT.value,
                'action': 'random_weight_adjustment',
                'parameters': {
                    'adjustments': adjustments,
                    'base_weights': copy.deepcopy(self.current_context.weights)
                },
                'confidence': max(0.1, confidence - 0.2)
            }
    
    def _generate_action_execution_decision(self, confidence: float) -> Dict[str, Any]:
        """Generowanie decyzji o wykonaniu działania"""
        if not self.current_context:
            return {
                'decision_type': DecisionType.ACTION_EXECUTION.value,
                'action': 'default_action',
                'parameters': {},
                'confidence': confidence
            }
        
        # Budowa parametrów akcji na podstawie kontekstu
        action_params = {
            'world_state': self._simplify_data(self.current_context.world_data),
            'model_info': self._simplify_data(self.current_context.model_info),
            'weights': self._simplify_data(self.current_context.weights),
            'risk_level': self.current_context.risk_factors.get('overall_risk', 0.5),
            'timestamp': datetime.now().isoformat()
        }
        
        # Jeśli są rekomendacje, użyj najwyżej ocenianej
        if self.current_context.recommendations:
            best_rec = max(
                self.current_context.recommendations,
                key=lambda x: x.get('confidence', 0.5)
            )
            action = best_rec.get('action', 'recommended_action')
            action_params['recommendation'] = best_rec
        else:
            action = 'standard_action'
        
        return {
            'decision_type': DecisionType.ACTION_EXECUTION.value,
            'action': action,
            'parameters': action_params,
            'confidence': confidence
        }
    
    def _generate_strategy_change_decision(self, confidence: float) -> Dict[str, Any]:
        """Generowanie decyzji o zmianie strategii"""
        # Analiza dotychczasowej wydajności (symulacja)
        # W rzeczywistości ta decyzja powinna być podejmowana przez StrategyManager
        
        change_reason = 'performance_optimization'
        suggested_strategy = 'adaptive'
        
        return {
            'decision_type': DecisionType.STRATEGY_CHANGE.value,
            'action': 'change_strategy',
            'parameters': {
                'reason': change_reason,
                'suggested_strategy': suggested_strategy,
                'current_performance': random.uniform(0.6, 0.9),
                'target_performance': random.uniform(0.7, 1.0)
            },
            'confidence': confidence
        }
    
    def _generate_observation_decision(self, confidence: float) -> Dict[str, Any]:
        """Generowanie decyzji obserwacyjnej"""
        observation_targets = []
        
        if self.current_context:
            if self.current_context.world_data:
                observation_targets.append('world_state')
            if self.current_context.model_info:
                observation_targets.append('model_performance')
            if self.current_context.weights:
                observation_targets.append('weight_distribution')
            if self.current_context.recommendations:
                observation_targets.append('recommendation_quality')
        
        return {
            'decision_type': DecisionType.OBSERVATION.value,
            'action': 'observe',
            'parameters': {
                'targets': observation_targets,
                'frequency': 'high',
                'granularity': 'detailed'
            },
            'confidence': confidence
        }
    
    def _generate_optimization_decision(self, confidence: float) -> Dict[str, Any]:
        """Generowanie decyzji optymalizacyjnej"""
        optimization_targets = ['model_accuracy', 'weight_distribution', 'risk_minimization']
        
        return {
            'decision_type': DecisionType.OPTIMIZATION.value,
            'action': 'optimize',
            'parameters': {
                'targets': optimization_targets,
                'method': 'gradient_descent',
                'learning_rate': 0.01,
                'iterations': 100
            },
            'confidence': confidence
        }
    
    def _calculate_priority(self, decision_type: DecisionType, confidence: float) -> int:
        """Obliczenie priorytetu decyzji"""
        # Różne typy decyzji mają różne priorytety bazowe
        type_priority = {
            DecisionType.MODEL_SELECTION: 5,
            DecisionType.WEIGHT_ADJUSTMENT: 4,
            DecisionType.STRATEGY_CHANGE: 3,
            DecisionType.ACTION_EXECUTION: 6,
            DecisionType.OBSERVATION: 2,
            DecisionType.OPTIMIZATION: 1
        }
        
        base_priority = type_priority.get(decision_type, 0)
        
        # Dostosowanie na podstawie pewności
        confidence_factor = int(confidence * 10)
        
        return base_priority + confidence_factor
    
    def _get_context_dict(self) -> Dict[str, Any]:
        """Pobranie słownika kontekstu"""
        if not self.current_context:
            return {}
        
        return {
            'world_data_keys': list(self.current_context.world_data.keys()),
            'model_info_keys': list(self.current_context.model_info.keys()),
            'weights_keys': list(self.current_context.weights.keys()),
            'recommendations_count': len(self.current_context.recommendations),
            'risk_factors': copy.deepcopy(self.current_context.risk_factors),
            'constraints': copy.deepcopy(self.current_context.constraints),
            'calculated_confidence': self.current_context.calculate_confidence()
        }
    
    def _simplify_data(self, data: Dict[str, Any], max_depth: int = 3, max_items: int = 5) -> Dict[str, Any]:
        """Uproszczenie danych dla parametryzacji"""
        if not isinstance(data, dict):
            return {}
        
        simplified = {}
        for i, (key, value) in enumerate(data.items()):
            if i >= max_items:
                break
            
            if isinstance(value, dict) and max_depth > 0:
                simplified[key] = self._simplify_data(value, max_depth - 1, max_items)
            elif isinstance(value, (list, tuple)) and len(value) > 0:
                simplified[key] = f"{type(value).__name__}[{len(value)}]"
            else:
                simplified[key] = value
        
        return simplified
    
    def execute_decision(self, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Wykonywanie podejmowanej decyzji.
        
        Args:
            decision_data: Dane decyzji do wykonania
            
        Returns:
            Wynik wykonania
        """
        decision_id = decision_data.get('decision_id', f"dec_{uuid.uuid4().hex[:8]}")
        
        try:
            # Znalezienie lub utworzenie decyzji
            if decision_id in [d.decision_id for d in self.decision_history]:
                decision = next(d for d in self.decision_history if d.decision_id == decision_id)
            else:
                decision = Decision(
                    decision_id=decision_id,
                    decision_type=DecisionType(decision_data.get('decision_type', 'action_execution')),
                    agent_id=self.agent_id,
                    context=decision_data.get('context', {}),
                    parameters=decision_data.get('parameters', {}),
                    confidence=decision_data.get('confidence', 0.5),
                    priority=decision_data.get('priority', 0)
                )
            
            # Realizacji decyzji (symulacja)
            result = self._simulate_decision_execution(decision)
            
            # Oznaczenie jako zrealizowaną
            decision.mark_as_executed(result)
            self.successful_decisions += 1
            
            # Zapisanie w pamięci
            if self.memory:
                execution_record = {
                    'type': 'decision_execution',
                    'decision_id': decision_id,
                    'decision_type': decision.decision_type.value,
                    'result': copy.deepcopy(result),
                    'status': 'executed',
                    'timestamp': datetime.now().isoformat()
                }
                self.memory.store_in_short_term(f"execution_{decision_id}", execution_record)
            
            self._notify_decision_callbacks(decision)
            
            return {
                'status': 'success',
                'message': 'Decision executed',
                'decision_id': decision_id,
                'result': copy.deepcopy(result),
                'agent_id': self.agent_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            # Oznaczenie jako nieudaną
            if decision_id in [d.decision_id for d in self.decision_history]:
                decision = next(d for d in self.decision_history if d.decision_id == decision_id)
                decision.mark_as_failed(str(e))
            
            self.failed_decisions += 1
            
            return {
                'status': 'error',
                'message': f'Decision execution failed: {str(e)}',
                'decision_id': decision_id,
                'error': str(e),
                'agent_id': self.agent_id,
                'timestamp': datetime.now().isoformat()
            }
    
    def _simulate_decision_execution(self, decision: Decision) -> Dict[str, Any]:
        """Symulacja wykonania decyzji"""
        # Symulacja wyników na podstawie rodzaju decyzji
        
        if decision.decision_type == DecisionType.MODEL_SELECTION:
            selected_model = decision.parameters.get('model_name', 'unknown')
            return {
                'execution_result': 'model_selected',
                'selected_model': selected_model,
                'performance_estimate': random.uniform(0.7, 0.95),
                'confidence': decision.confidence
            }
        
        elif decision.decision_type == DecisionType.WEIGHT_ADJUSTMENT:
            adjustments = decision.parameters.get('adjustments', {})
            return {
                'execution_result': 'weights_adjusted',
                'adjusted_weights': adjustments,
                'impact_assessment': random.uniform(-0.1, 0.3),
                'new_weights': {**self.current_context.weights, **adjustments} if self.current_context else adjustments
            }
        
        elif decision.decision_type == DecisionType.ACTION_EXECUTION:
            action = decision.parameters.get('action', 'unknown')
            return {
                'execution_result': 'action_executed',
                'action': action,
                'outcome': random.choice(['success', 'partial_success', 'failure']),
                'reward': random.uniform(-1.0, 2.0)
            }
        
        else:
            return {
                'execution_result': 'decision_processed',
                'decision_type': decision.decision_type.value,
                'status': 'completed'
            }
    
    def record_decision(self, decision_data: Dict[str, Any]) -> str:
        """
        Zapisanie decyzji z zewnątrz (np. z Hội samej przez inny komponent).
        
        Args:
            decision_data: Dane decyzji
            
        Returns:
            ID decyzji
        """
        decision_id = decision_data.get('decision_id', f"dec_{uuid.uuid4().hex[:8]}")
        
        decision = Decision(
            decision_id=decision_id,
            decision_type=DecisionType(decision_data.get('decision_type', DecisionType.ACTION_EXECUTION.value)),
            agent_id=self.agent_id,
            context=decision_data.get('context', {}),
            parameters=decision_data.get('parameters', {}),
            confidence=decision_data.get('confidence', 0.5),
            priority=decision_data.get('priority', 0),
            created_at=datetime.fromisoformat(decision_data.get('created_at')) if decision_data.get('created_at') else datetime.now()
        )
        
        self.decision_history.append(decision)
        self.total_decisions += 1
        
        # Zapisanie w pamięci
        if self.memory:
            self.memory.add_decision(decision.to_dict())
        
        return decision_id
    
    def get_decision_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Pobranie historii decyzji"""
        if limit is None:
            return [d.to_dict() for d in self.decision_history]
        else:
            return [d.to_dict() for d in self.decision_history[-limit:]]
    
    def get_pending_decisions(self) -> List[Dict[str, Any]]:
        """Pobranie oczekujących decyzji"""
        return [
            d.to_dict() for d in self.decision_history 
            if d.status == DecisionStatus.PENDING
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Pobranie statystyk silnika decyzji"""
        return {
            'total_decisions': self.total_decisions,
            'successful_decisions': self.successful_decisions,
            'failed_decisions': self.failed_decisions,
            'success_rate': self.successful_decisions / self.total_decisions if self.total_decisions > 0 else 0.0,
            'decision_history_size': len(self.decision_history),
            'current_decision': self.current_decision.to_dict() if self.current_decision else None,
            'last_decision_type': self.decision_history[-1].decision_type.value if self.decision_history else None
        }
    
    def clear_history(self) -> None:
        """Wyczyszczenie historii"""
        self.decision_history.clear()
        self.total_decisions = 0
        self.successful_decisions = 0
        self.failed_decisions = 0
    
    # Obsługa callbacków
    def on_decision_made(self, callback: Callable) -> None:
        """Rejestracja callbacka na podjęcie decyzji"""
        self._decision_callbacks.append(callback)
    
    def _notify_decision_callbacks(self, decision: Decision) -> None:
        """Powiadomienie callbacków o podjęciu decyzji"""
        for callback in self._decision_callbacks:
            try:
                callback(decision, self)
            except Exception:
                pass


# Eksportowane funkcje i klasy
__all__ = [
    'DecisionType',
    'DecisionStatus',
    'Decision',
    'DecisionContext',
    'DecisionEngine'
]
