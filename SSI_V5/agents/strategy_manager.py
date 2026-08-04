# SSI V5 Agent Layer - Strategy Manager
# ==================================================
#
# ETAP: 5.2.4 FAZA 4
# Data: 2026-08-03
# 
# Odpowiedzialnosc:
# - Zarządzanie strategiami agenta
# - Wybór optymalnej strategii na podstawie kontekstu
# - Adaptacja strategii w czasie rzeczyswistym
# - Integracja z modelem poznawczym (CognitiveTeacher)

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Callable
from enum import Enum
from datetime import datetime
import uuid
import copy
import random
import numpy as np


class StrategyType(Enum):
    """Typy strategii"""
    CONSERVATIVE = "conservative"      # Strategia zachowawcza - minimalne ryzyko
    AGGRESSIVE = "aggressive"          # Strategia agresywna - maksymalne ryzyko
    BALANCED = "balanced"              # Strategia zrównoważona - umiarkowane ryzyko
    ADAPTIVE = "adaptive"              # Strategia adaptacyjna - dostosowuje się do warunków
    EXPERIMENTAL = "experimental"      # Strategia doświadczalna - testuje nowe podejścia
    OPTIMIZED = "optimized"            # Strategia zoptymalizowana - bazująca na historycznych wynikach


class LearningMode(Enum):
    """Tryby uczenia się strategii"""
    OFF = "off"                       # Brak uczenia się
    PASSIVE = "passive"               # Uczenie się pasywne - obserwacja i zapamiętywanie
    ACTIVE = "active"                 # Uczenie się aktywne - testowanie nowych strategii


@dataclass
class Strategy:
    """Pojedyncza strategia agenta"""
    strategy_id: str
    strategy_type: StrategyType
    name: str
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    usage_count: int = 0
    success_rate: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            'strategy_id': self.strategy_id,
            'strategy_type': self.strategy_type.value,
            'name': self.name,
            'description': self.description,
            'parameters': copy.deepcopy(self.parameters),
            'performance_metrics': copy.deepcopy(self.performance_metrics),
            'usage_count': self.usage_count,
            'success_rate': self.success_rate,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def update_performance(self, success: bool, metrics: Optional[Dict[str, Any]] = None) -> None:
        """Aktualizacja metryk wydajności"""
        self.usage_count += 1
        
        if success:
            # Aktualizacja współczynnika sukcesu ( śr. ważona)
            total_count = self.usage_count
            new_success_rate = ((self.success_rate * (total_count - 1)) + 1) / total_count if total_count > 1 else 1.0
            self.success_rate = new_success_rate
        else:
            # Obliczenie nowego współczynnika
            total_count = self.usage_count
            new_success_rate = ((self.success_rate * (total_count - 1)) + 0) / total_count if total_count > 1 else 0.0
            self.success_rate = new_success_rate
        
        # Aktualizacja metryk
        if metrics:
            self.performance_metrics.update(metrics)
        
        self.updated_at = datetime.now()


@dataclass
class StrategyContext:
    """Kontekst dla podejmowania decyzjiycznej"""
    world_state: Dict[str, Any] = field(default_factory=dict)
    model_evaluation: Dict[str, Any] = field(default_factory=dict)
    current_weights: Dict[str, Any] = field(default_factory=dict)
    world_memory: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    risk_level: float = 0.5
    uncertainty: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def calculate_risk_level(self) -> float:
        """Obliczenie poziomu ryzyka na podstawie kontekstu"""
        # Bazowy poziom ryzyka
        risk = 0.5
        
        # Analiza wagi modelo - im gorsze oceny, tym wyższe ryzyko
        if self.model_evaluation:
            model_scores = [v for v in self.model_evaluation.values() if isinstance(v, (int, float))]
            if model_scores:
                avg_score = sum(model_scores) / len(model_scores)
                # Normalizacja do zakresu 0-1
                if avg_score > 0:
                    risk = min(1.0, max(0.0, 1.0 - avg_score))
        
        # Analiza niepewności
        if self.uncertainty > 0:
            risk = min(1.0, risk + self.uncertainty * 0.5)
        
        self.risk_level = risk
        return risk
    
    def get_recommendation_weights(self) -> Dict[str, float]:
        """Pobranie wag rekomendacji"""
        weights = {}
        for i, recommendation in enumerate(self.recommendations):
            weight = recommendation.get('weight', 1.0 / len(self.recommendations) if self.recommendations else 1.0)
            rec_id = recommendation.get('recommendation_id', f"rec_{i}")
            weights[rec_id] = float(weight)
        return weights


class StrategyManager:
    """
    Menadżer strategii - zarządza zestawem strategii agenta.
    
    Odpowiedzialność:
    - Zarządzanie zestawem strategii
    - Wybór optymalnej strategii
    - Adaptacja strategii
    - Integracja z kontekstem świata
    """
    
    # Domyślne strategie
    DEFAULT_STRATEGIES = {
        'conservative': {
            'type': StrategyType.CONSERVATIVE,
            'name': 'Konserwatywna',
            'description': 'Minimalne ryzyko, bezpieczne podejście',
            'parameters': {
                'risk_threshold': 0.3,
                'uncertainty_threshold': 0.2,
                'learning_mode': LearningMode.PASSIVE,
                'max_position_size': 0.1
            }
        },
        'aggressive': {
            'type': StrategyType.AGGRESSIVE,
            'name': 'Agresywna',
            'description': 'Maksymalne ryzyko, wysoka potencjalna nagroda',
            'parameters': {
                'risk_threshold': 0.8,
                'uncertainty_threshold': 0.6,
                'learning_mode': LearningMode.ACTIVE,
                'max_position_size': 0.5
            }
        },
        'balanced': {
            'type': StrategyType.BALANCED,
            'name': 'Zrównoważona',
            'description': 'Umiarkowane ryzyko, stabilne wyniki',
            'parameters': {
                'risk_threshold': 0.5,
                'uncertainty_threshold': 0.4,
                'learning_mode': LearningMode.PASSIVE,
                'max_position_size': 0.25
            }
        },
        'adaptive': {
            'type': StrategyType.ADAPTIVE,
            'name': 'Adaptacyjna',
            'description': 'Dostosowuje się do warunków rynkowych',
            'parameters': {
                'risk_threshold': 0.6,
                'uncertainty_threshold': 0.3,
                'learning_mode': LearningMode.ACTIVE,
                'max_position_size': 0.2,
                'adaptation_speed': 0.3
            }
        }
    }
    
    def __init__(self, agent_id: str):
        """
        Inicjalizacja Strategy Manager.
        
        Args:
            agent_id: ID agenta, któremu należy manager
        """
        self.agent_id = agent_id
        self.strategies: Dict[str, Strategy] = {}
        self.active_strategy: Optional[Strategy] = None
        self.current_context: Optional[StrategyContext] = None
        self.memory: Optional[Any] = None  # Referencja do AgentMemory
        
        # Konfiguracja
        self.learning_mode = LearningMode.PASSIVE
        self.tracking_mode = True
        self.performance_history: List[Dict[str, Any]] = []
        self.strategy_usage: Dict[str, int] = {}
        
        # Statystyki
        self.total_decisions = 0
        self.total_strategy_changes = 0
        
        # Flagi
        self._initialized = False
    
    def initialize(self) -> Dict[str, Any]:
        """
        Inicjalizacja menadżera strategii.
        
        Returns:
            Status inicjalizacji
        """
        if self._initialized:
            return {
                'status': 'success',
                'message': 'StrategyManager already initialized',
                'agent_id': self.agent_id
            }
        
        try:
            # Ładowanie domyślnych strategii
            self._load_default_strategies()
            
            # Ustawienie aktywnej strategii (domyślnie zrównoważona)
            if 'balanced' in self.strategies:
                self.active_strategy = self.strategies['balanced']
            elif self.strategies:
                self.active_strategy = list(self.strategies.values())[0]
            
            self._initialized = True
            
            return {
                'status': 'success',
                'message': 'StrategyManager initialized',
                'agent_id': self.agent_id,
                'strategies_loaded': len(self.strategies),
                'active_strategy': self.active_strategy.name if self.active_strategy else 'None',
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
    
    def _load_default_strategies(self) -> None:
        """Załadowanie domyślnych strategii"""
        for strategy_id, config in self.DEFAULT_STRATEGIES.items():
            strategy = Strategy(
                strategy_id=strategy_id,
                strategy_type=config['type'],
                name=config['name'],
                description=config['description'],
                parameters=copy.deepcopy(config['parameters'])
            )
            self.strategies[strategy_id] = strategy
            self.strategy_usage[strategy_id] = 0
    
    def receive_context(self, model_evaluation: Optional[Dict[str, Any]] = None,
                       current_weights: Optional[Dict[str, Any]] = None,
                       world_memory: Optional[Dict[str, Any]] = None,
                       recommendations: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Odbiór kontekstu od Teacher Layer.
        
        Args:
            model_evaluation: Ocena modeli
            current_weights: Aktualne wagi
            world_memory: Pamięć świata
            recommendations: Rekomendacje
        """
        self.current_context = StrategyContext(
            world_state={},
            model_evaluation=model_evaluation or {},
            current_weights=current_weights or {},
            world_memory=world_memory or {},
            recommendations=recommendations or [],
            timestamp=datetime.now()
        )
        
        # Obliczenie poziomu ryzyka
        self.current_context.calculate_risk_level()
        
        # Zapisanie w pamięci
        if self.memory:
            context_data = {
                'type': 'strategy_context',
                'model_evaluation': model_evaluation,
                'current_weights': current_weights,
                'recommendations': recommendations,
                'risk_level': self.current_context.risk_level,
                'timestamp': datetime.now().isoformat()
            }
            self.memory.store_in_short_term(f"context_{datetime.now().isoformat()}", context_data)
    
    def select_strategy(self, context: Optional[StrategyContext] = None) -> Strategy:
        """
        Wybór optymalnej strategii na podstawie kontekstu.
        
        Args:
            context: Kontekst (jeśli nie podano, używa current_context)
            
        Returns:
            Wybrana strategia
        """
        if context is None:
            context = self.current_context
        
        if context is None:
            return self.active_strategy or list(self.strategies.values())[0]
        
        # Dynamiczny wybór strategii na podstawie poziomu ryzyka
        risk_level = context.risk_level
        
        # Logika wyboru strategii
        if risk_level < 0.3:
            # Niskie ryzyko - strategia agresywna
            chosen_type = StrategyType.AGGRESSIVE
        elif risk_level < 0.5:
            # Średnie ryzyko - strategia zrównoważona
            chosen_type = StrategyType.BALANCED
        elif risk_level < 0.7:
            # Podwyższone ryzyko - strategia zachowawcza
            chosen_type = StrategyType.CONSERVATIVE
        else:
            # Bardzo wysokie ryzyko - strategia adaptacyjna
            chosen_type = StrategyType.ADAPTIVE
        
        # Znajdź najlepszą strategię danego typu
        best_strategy = None
        best_score = -1
        
        for strategy in self.strategies.values():
            if strategy.strategy_type == chosen_type:
                # Ocenianie strategii na podstawie historycznej wydajności
                score = strategy.success_rate * strategy.usage_count
                if score > best_score:
                    best_score = score
                    best_strategy = strategy
                    
        # Jeśli nie znaleziono strategii danego typu, użyj aktywnej
        if best_strategy is None:
            return self.active_strategy or list(self.strategies.values())[0]
        
        # Zmiana aktywnej strategii, jeśli jest lepsza
        if best_strategy.success_rate > (self.active_strategy.success_rate if self.active_strategy else 0):
            self._change_strategy(best_strategy)
            
        return best_strategy
    
    def _change_strategy(self, new_strategy: Strategy) -> None:
        """Zmiana aktywnej strategii"""
        if self.active_strategy == new_strategy:
            return
        
        old_strategy = self.active_strategy
        self.active_strategy = new_strategy
        self.total_strategy_changes += 1
        
        # Logowanie zmiany
        change_record = {
            'timestamp': datetime.now().isoformat(),
            'agent_id': self.agent_id,
            'old_strategy': old_strategy.name if old_strategy else 'None',
            'new_strategy': new_strategy.name,
            'new_strategy_type': new_strategy.strategy_type.value,
            'success_rate': new_strategy.success_rate,
            'usage_count': new_strategy.usage_count,
            'total_changes': self.total_strategy_changes
        }
        
        if self.memory:
            self.memory.store_in_short_term(f"strategy_change_{self.total_strategy_changes}", change_record)
    
    def get_recommendation(self, context: Optional[StrategyContext] = None) -> Dict[str, Any]:
        """
        Generowanie rekomendacji na podstawie aktualnej strategii i kontekstu.
        
        Args:
            context: Kontekst (opcjonalny)
            
        Returns:
            Rekomendacja
        """
        # Wybór strategii
        strategy = self.select_strategy(context)
        
        # Generowanie rekomendacji
        recommendation = {
            'recommendation_id': f"rec_{uuid.uuid4().hex[:8]}",
            'agent_id': self.agent_id,
            'strategy_name': strategy.name,
            'strategy_type': strategy.strategy_type.value,
            'parameters': copy.deepcopy(strategy.parameters),
            'confidence': strategy.success_rate,
            'usage_count': strategy.usage_count,
            'risk_level': context.risk_level if context else 0.5,
            'timestamp': datetime.now().isoformat()
        }
        
        return recommendation
    
    def evaluate_performance(self, outcome: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ocena wydajności aktualnej strategii.
        
        Args:
            outcome: Wynik działania
            
        Returns:
            Ocena wydajności
        """
        if not self.active_strategy:
            return {'status': 'error', 'message': 'No active strategy'}
        
        success = outcome.get('status', '') == 'success'
        metrics = outcome.get('metrics', {})
        
        # Aktualizacja strategii
        self.active_strategy.update_performance(success, metrics)
        self.strategy_usage[self.active_strategy.strategy_id] += 1
        
        # Zapisanie w historii
        performance_record = {
            'timestamp': datetime.now().isoformat(),
            'agent_id': self.agent_id,
            'strategy_id': self.active_strategy.strategy_id,
            'strategy_name': self.active_strategy.name,
            'success': success,
            'metrics': copy.deepcopy(metrics),
            'usage_count': self.active_strategy.usage_count,
            'success_rate': self.active_strategy.success_rate
        }
        
        self.performance_history.append(performance_record)
        
        # Zapisanie w pamięci
        if self.memory:
            self.memory.store_in_long_term(f"performance_{len(self.performance_history)}", performance_record)
        
        return {
            'status': 'success',
            'strategy': self.active_strategy.name,
            'success': success,
            'new_success_rate': self.active_strategy.success_rate,
            'usage_count': self.active_strategy.usage_count
        }
    
    def add_strategy(self, strategy_config: Dict[str, Any]) -> str:
        """
        Dodanie nowej strategii.
        
        Args:
            strategy_config: Konfiguracja strategii
            
        Returns:
            ID nowej strategii
        """
        strategy_id = strategy_config.get('strategy_id', f"strategy_{uuid.uuid4().hex[:8]}")
        strategy_type = StrategyType(strategy_config.get('type', 'balanced'))
        
        strategy = Strategy(
            strategy_id=strategy_id,
            strategy_type=strategy_type,
            name=strategy_config.get('name', 'Custom Strategy'),
            description=strategy_config.get('description', ''),
            parameters=strategy_config.get('parameters', {}),
            created_at=datetime.now()
        )
        
        self.strategies[strategy_id] = strategy
        self.strategy_usage[strategy_id] = 0
        
        return strategy_id
    
    def remove_strategy(self, strategy_id: str) -> bool:
        """Usunięcie strategii"""
        if strategy_id in self.strategies:
            if self.active_strategy and self.active_strategy.strategy_id == strategy_id:
                # Wybór nowej aktywnej strategii
                self.active_strategy = list(self.strategies.values())[0] if self.strategies else None
            
            del self.strategies[strategy_id]
            if strategy_id in self.strategy_usage:
                del self.strategy_usage[strategy_id]
            
            return True
        return False
    
    def get_current_strategy(self) -> Optional[Strategy]:
        """Pobranie aktualnej strategii"""
        return self.active_strategy
    
    def get_all_strategies(self) -> Dict[str, Strategy]:
        """Pobranie wszystkich strategii"""
        return copy.deepcopy(self.strategies)
    
    def get_strategy_statistics(self) -> List[Dict[str, Any]]:
        """Pobranie statystyk strategii"""
        statistics = []
        for strategy in self.strategies.values():
            statistics.append({
                'strategy_id': strategy.strategy_id,
                'name': strategy.name,
                'type': strategy.strategy_type.value,
                'usage_count': strategy.usage_count + self.strategy_usage.get(strategy.strategy_id, 0),
                'success_rate': strategy.success_rate,
                'is_active': strategy == self.active_strategy
            })
        return statistics
    
    def update_learning_mode(self, mode: Union[LearningMode, str]) -> None:
        """Aktualizacja trybu uczenia się"""
        if isinstance(mode, str):
            self.learning_mode = LearningMode(mode)
        else:
            self.learning_mode = mode
    
    def adapt_strategy_parameters(self, new_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dostosowanie parametrów aktualnej strategii.
        
        Args:
            new_parameters: Nowe parametry
            
        Returns:
            Status dostosowania
        """
        if not self.active_strategy:
            return {'status': 'error', 'message': 'No active strategy'}
        
        old_parameters = copy.deepcopy(self.active_strategy.parameters)
        self.active_strategy.parameters.update(new_parameters)
        
        # Zapisanie zmian w pamięci
        if self.memory:
            adaptation_record = {
                'timestamp': datetime.now().isoformat(),
                'agent_id': self.agent_id,
                'strategy_id': self.active_strategy.strategy_id,
                'old_parameters': old_parameters,
                'new_parameters': copy.deepcopy(new_parameters),
                'learning_mode': self.learning_mode.value
            }
            self.memory.store_in_short_term(f"adaptation_{len(self.performance_history) + 1}", adaptation_record)
        
        return {
            'status': 'success',
            'message': 'Parameters adapted',
            'new_parameters': copy.deepcopy(self.active_strategy.parameters)
        }
    
    def get_strategy_for_world_state(self, world_state: Dict[str, Any]) -> Strategy:
        """
        Wybór strategii na podstawie stanu świata.
        
        Args:
            world_state: Stan świata
            
        Returns:
            Rekomendowana strategia
        """
        # Aktualizacja kontekstu
        if self.current_context:
            self.current_context.world_state = world_state
            self.current_context.risk_level = self.current_context.calculate_risk_level()
        else:
            self.current_context = StrategyContext(
                world_state=world_state,
                timestamp=datetime.now()
            )
            self.current_context.calculate_risk_level()
        
        # Wybór strategii
        return self.select_strategy()


# Eksportowane funkcje i klasy
__all__ = [
    'StrategyType',
    'LearningMode',
    'Strategy',
    'StrategyContext',
    'StrategyManager'
]
