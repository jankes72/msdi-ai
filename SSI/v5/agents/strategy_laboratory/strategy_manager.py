"""
SSI V5 - Strategy Manager

Manager strategii dla Strategy Laboratory.

Implementuje funkcje:
- create_strategy()
- update_strategy()
- evaluate_strategy()
- rank_strategies()
- archive_strategy()

Wersja: 1.0.0
Data: 2026-08-01
"""

import threading
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import uuid

from .strategy_models import (
    Strategy,
    StrategyParameters,
    StrategyResult,
    StrategyEvaluation,
    StrategyRanking,
    StrategyStatus,
    StrategyVersion,
    StrategyType,
    create_strategy as _create_strategy,
    update_strategy_stats as _update_strategy_stats
)

# Konfiguracja logowania
logger = logging.getLogger(__name__)


@dataclass
class StrategyManagerConfig:
    """Konfiguracja Strategy Manager."""
    
    # Ogólne
    max_strategies_per_agent: int = 100
    max_active_strategies: int = 50
    auto_archive_after_days: int = 30
    auto_evaluate_after_uses: int = 10
    
    # Walidacja
    enable_validation: bool = True
    require_unique_names: bool = True
    require_description: bool = True
    
    # Dom fantazji
    default_strategy_type: StrategyType = StrategyType.DECISION
    default_version: str = "1.0.0"
    
    # Zachowanie
    allow_duplicate_names_different_agents: bool = True
    enable_auto_ranking: bool = True
    auto_ranking_interval_hours: int = 24
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika."""
        return {
            'max_strategies_per_agent': self.max_strategies_per_agent,
            'max_active_strategies': self.max_active_strategies,
            'auto_archive_after_days': self.auto_archive_after_days,
            'auto_evaluate_after_uses': self.auto_evaluate_after_uses,
            'enable_validation': self.enable_validation,
            'require_unique_names': self.require_unique_names,
            'require_description': self.require_description,
            'default_strategy_type': self.default_strategy_type.name,
            'default_version': self.default_version,
            'allow_duplicate_names_different_agents': self.allow_duplicate_names_different_agents,
            'enable_auto_ranking': self.enable_auto_ranking,
            'auto_ranking_interval_hours': self.auto_ranking_interval_hours
        }


class StrategyStorage:
    """Przechowalnia strategii."""
    
    def __init__(self):
        self._strategies: Dict[str, Strategy] = {}
        self._by_agent: Dict[str, List[str]] = {}
        self._by_type: Dict[str, List[str]] = {}
        self._by_status: Dict[str, List[str]] = {}
        self._lock = threading.RLock()
    
    def add(self, strategy: Strategy) -> str:
        """Dodanie strategii."""
        with self._lock:
            strategy_id = strategy.strategy_id
            self._strategies[strategy_id] = strategy
            
            # Indeksowanie
            if strategy.agent_owner not in self._by_agent:
                self._by_agent[strategy.agent_owner] = []
            self._by_agent[strategy.agent_owner].append(strategy_id)
            
            if strategy.strategy_type.name not in self._by_type:
                self._by_type[strategy.strategy_type.name] = []
            self._by_type[strategy.strategy_type.name].append(strategy_id)
            
            if strategy.status.name not in self._by_status:
                self._by_status[strategy.status.name] = []
            self._by_status[strategy.status.name].append(strategy_id)
            
            return strategy_id
    
    def get(self, strategy_id: str) -> Optional[Strategy]:
        """Pobranie strategii."""
        with self._lock:
            return self._strategies.get(strategy_id)
    
    def get_by_agent(self, agent_id: str) -> List[Strategy]:
        """Pobranie strategii agenta."""
        with self._lock:
            strategy_ids = self._by_agent.get(agent_id, [])
            return [self._strategies[sid] for sid in strategy_ids if sid in self._strategies]
    
    def get_by_type(self, strategy_type: Union[str, StrategyType]) -> List[Strategy]:
        """Pobranie strategii po typie."""
        with self._lock:
            type_name = strategy_type if isinstance(strategy_type, str) else strategy_type.name
            strategy_ids = self._by_type.get(type_name, [])
            return [self._strategies[sid] for sid in strategy_ids if sid in self._strategies]
    
    def get_by_status(self, status: Union[str, StrategyStatus]) -> List[Strategy]:
        """Pobranie strategii po statusie."""
        with self._lock:
            status_name = status if isinstance(status, str) else status.name
            strategy_ids = self._by_status.get(status_name, [])
            return [self._strategies[sid] for sid in strategy_ids if sid in self._strategies]
    
    def update(self, strategy: Strategy) -> bool:
        """Aktualizacja strategii."""
        with self._lock:
            if strategy.strategy_id not in self._strategies:
                return False
            
            old_strategy = self._strategies[strategy.strategy_id]
            
            # Aktualizacja indeksów przy zmianie właściciela
            if old_strategy.agent_owner != strategy.agent_owner:
                if old_strategy.agent_owner in self._by_agent:
                    self._by_agent[old_strategy.agent_owner].remove(strategy.strategy_id)
                if strategy.agent_owner not in self._by_agent:
                    self._by_agent[strategy.agent_owner] = []
                self._by_agent[strategy.agent_owner].append(strategy.strategy_id)
            
            # Aktualizacja indeksów przy zmianie typu
            if old_strategy.strategy_type.name != strategy.strategy_type.name:
                if old_strategy.strategy_type.name in self._by_type:
                    self._by_type[old_strategy.strategy_type.name].remove(strategy.strategy_id)
                if strategy.strategy_type.name not in self._by_type:
                    self._by_type[strategy.strategy_type.name] = []
                self._by_type[strategy.strategy_type.name].append(strategy.strategy_id)
            
            # Aktualizacja indeksów przy zmianie statusu
            if old_strategy.status.name != strategy.status.name:
                if old_strategy.status.name in self._by_status:
                    self._by_status[old_strategy.status.name].remove(strategy.strategy_id)
                if strategy.status.name not in self._by_status:
                    self._by_status[strategy.status.name] = []
                self._by_status[strategy.status.name].append(strategy.strategy_id)
            
            self._strategies[strategy.strategy_id] = strategy
            return True
    
    def remove(self, strategy_id: str) -> bool:
        """Usunięcie strategii."""
        with self._lock:
            if strategy_id not in self._strategies:
                return False
            
            strategy = self._strategies[strategy_id]
            
            # Usunięcie z indeksów
            if strategy.agent_owner in self._by_agent:
                self._by_agent[strategy.agent_owner].remove(strategy_id)
                if not self._by_agent[strategy.agent_owner]:
                    del self._by_agent[strategy.agent_owner]
            
            if strategy.strategy_type.name in self._by_type:
                self._by_type[strategy.strategy_type.name].remove(strategy_id)
                if not self._by_type[strategy.strategy_type.name]:
                    del self._by_type[strategy.strategy_type.name]
            
            if strategy.status.name in self._by_status:
                self._by_status[strategy.status.name].remove(strategy_id)
                if not self._by_status[strategy.status.name]:
                    del self._by_status[strategy.status.name]
            
            del self._strategies[strategy_id]
            return True
    
    def list_all(self) -> List[Strategy]:
        """Pobranie wszystkich strategii."""
        with self._lock:
            return list(self._strategies.values())
    
    def count(self) -> int:
        """Liczba wszystkich strategii."""
        with self._lock:
            return len(self._strategies)
    
    def count_by_agent(self, agent_id: str) -> int:
        """Liczba strategii agenta."""
        with self._lock:
            return len(self._by_agent.get(agent_id, []))
    
    def exists(self, strategy_id: str) -> bool:
        """Sprawdzenie czy strategia istnieje."""
        with self._lock:
            return strategy_id in self._strategies


class StrategyValidator:
    """Weryfikator strategii."""
    
    def __init__(self, config: StrategyManagerConfig):
        self.config = config
    
    def validate_strategy(self, strategy: Strategy, is_update: bool = False) -> Tuple[bool, List[str]]:
        """Walidacja strategii."""
        errors = []
        
        # Walidacja wymaganych pól
        if not strategy.agent_owner:
            errors.append("Agent owner is required")
        
        if not strategy.name:
            errors.append("Strategy name is required")
            
        if self.config.require_description and not strategy.description:
            errors.append("Strategy description is required")
        
        # Walidacja parametrów
        if not strategy.parameters.validate():
            errors.append("Invalid strategy parameters")
        
        # Walidacja unikalności nazwy
        if self.config.require_unique_names:
            if not self.config.allow_duplicate_names_different_agents:
                # Sprawdzanie unikalności globalnej
                pass  # Do implementacji w managerze
        
        # Walidacja wersji
        try:
            if strategy.version:
                # Podstawowa walidacja formatu wersji
                parts = strategy.version.split('.')
                if len(parts) < 2:
                    errors.append("Invalid version format. Use MAJOR.MINOR.PATCH")
                for part in parts[:2]:  # Sprawdzamy pierwsze 2 części
                    if not part.isdigit():
                        errors.append(f"Version part '{part}' must be numeric")
        except Exception:
            errors.append("Invalid version format")
        
        return len(errors) == 0, errors


class StrategyManager:
    """
    Główny manager strategii.
    
    Implementuje:
    - create_strategy()
    - update_strategy()
    - evaluate_strategy()
    - rank_strategies()
    - archive_strategy()
    """
    
    def __init__(self, config: Optional[StrategyManagerConfig] = None):
        self.config = config or StrategyManagerConfig()
        self.storage = StrategyStorage()
        self.validator = StrategyValidator(self.config)
        self._lock = threading.RLock()
        
        # Hooki na zdarzenia
        self._on_create_hooks: List[Callable[[Strategy], None]] = []
        self._on_update_hooks: List[Callable[[Strategy], None]] = []
        self._on_archive_hooks: List[Callable[[Strategy], None]] = []
        self._on_evaluate_hooks: List[Callable[[Strategy, StrategyEvaluation], None]] = []
        self._on_rank_hooks: List[Callable[[List[StrategyRanking]], None]] = []
        
        logger.info(f"StrategyManager initialized with config: {self.config.to_dict()}")
    
    def on_create(self, callback: Callable[[Strategy], None]) -> None:
        """Rejestracja hooka na tworzenie strategii."""
        self._on_create_hooks.append(callback)
    
    def on_update(self, callback: Callable[[Strategy], None]) -> None:
        """Rejestracja hooka na aktualizację strategii."""
        self._on_update_hooks.append(callback)
    
    def on_archive(self, callback: Callable[[Strategy], None]) -> None:
        """Rejestracja hooka na archiwizację strategii."""
        self._on_archive_hooks.append(callback)
    
    def on_evaluate(self, callback: Callable[[Strategy, StrategyEvaluation], None]) -> None:
        """Rejestracja hooka na ocenę strategii."""
        self._on_evaluate_hooks.append(callback)
    
    def on_rank(self, callback: Callable[[List[StrategyRanking]], None]) -> None:
        """Rejestracja hooka na ranking strategii."""
        self._on_rank_hooks.append(callback)
    
    def _trigger_on_create(self, strategy: Strategy) -> None:
        """Wywołanie hooków na tworzenie."""
        for hook in self._on_create_hooks:
            try:
                hook(strategy)
            except Exception as e:
                logger.error(f"Error in on_create hook: {e}")
    
    def _trigger_on_update(self, strategy: Strategy) -> None:
        """Wywołanie hooków na aktualizację."""
        for hook in self._on_update_hooks:
            try:
                hook(strategy)
            except Exception as e:
                logger.error(f"Error in on_update hook: {e}")
    
    def _trigger_on_archive(self, strategy: Strategy) -> None:
        """Wywołanie hooków na archiwizację."""
        for hook in self._on_archive_hooks:
            try:
                hook(strategy)
            except Exception as e:
                logger.error(f"Error in on_archive hook: {e}")
    
    def _trigger_on_evaluate(self, strategy: Strategy, evaluation: StrategyEvaluation) -> None:
        """Wywołanie hooków na ocenę."""
        for hook in self._on_evaluate_hooks:
            try:
                hook(strategy, evaluation)
            except Exception as e:
                logger.error(f"Error in on_evaluate hook: {e}")
    
    def _trigger_on_rank(self, rankings: List[StrategyRanking]) -> None:
        """Wywołanie hooków na ranking."""
        for hook in self._on_rank_hooks:
            try:
                hook(rankings)
            except Exception as e:
                logger.error(f"Error in on_rank hook: {e}")
    
    def create_strategy(
        self,
        agent_owner: str,
        name: str,
        strategy_type: StrategyType = None,
        description: str = "",
        parameters: Optional[StrategyParameters] = None,
        version: str = None,
        category: str = "default",
        tags: List[str] = None,
        purpose: str = "",
        methodology: str = "",
        **kwargs
    ) -> Strategy:
        """
        Tworzenie nowej strategii.
        
        Args:
            agent_owner: Agent będący właścicielem strategii
            name: Nazwa strategii
            strategy_type: Typ strategii (domyślnie z konfiguracji)
            description: Opis strategii
            parameters: Parametry strategii
            version: Wersja strategii
            category: Kategoria strategii
            tags: Tagi strategii
            purpose: Cel strategii
            methodology: Metodologia strategii
            **kwargs: Dodatkowe parametry
            
        Returns:
            Strategy: Nowo utworzona strategia
        """
        with self._lock:
            # Ustawienia domyślne
            if strategy_type is None:
                strategy_type = self.config.default_strategy_type
            if version is None:
                version = self.config.default_version
            if tags is None:
                tags = []
            
            # Utworzenie strategii
            if parameters is None:
                parameters = StrategyParameters(strategy_type=strategy_type)
            
            strategy = _create_strategy(
                agent_owner=agent_owner,
                name=name,
                strategy_type=strategy_type,
                description=description,
                parameters=parameters,
                version=version,
                category=category,
                tags=tags,
                purpose=purpose,
                methodology=methodology,
                **kwargs
            )
            
            # Walidacja
            if self.config.enable_validation:
                valid, errors = self.validator.validate_strategy(strategy)
                if not valid:
                    error_msg = f"Strategy validation failed: {errors}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
            
            # Sprawdzenie limitów
            agent_strategies = self.storage.count_by_agent(agent_owner)
            if agent_strategies >= self.config.max_strategies_per_agent:
                error_msg = f"Agent {agent_owner} has reached maximum strategies limit ({self.config.max_strategies_per_agent})"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            active_strategies = len(self.storage.get_by_status(StrategyStatus.ACTIVE))
            active_by_agent = len([s for s in self.storage.get_by_agent(agent_owner) 
                                  if s.status == StrategyStatus.ACTIVE])
            
            if active_by_agent >= self.config.max_active_strategies:
                error_msg = f"Agent {agent_owner} has reached maximum active strategies limit ({self.config.max_active_strategies})"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Dodanie do przechowalni
            strategy_id = self.storage.add(strategy)
            strategy.strategy_id = strategy_id
            
            # Wywołanie hooków
            self._trigger_on_create(strategy)
            
            logger.info(f"Strategy created: {strategy_id} by agent {agent_owner}")
            
            return strategy
    
    def update_strategy(
        self,
        strategy_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parameters: Optional[StrategyParameters] = None,
        version: Optional[str] = None,
        status: Optional[StrategyStatus] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        purpose: Optional[str] = None,
        methodology: Optional[str] = None,
        **kwargs
    ) -> Optional[Strategy]:
        """
        Aktualizacja strategii.
        
        Args:
            strategy_id: ID strategii do zaktualizowania
            name: Nowa nazwa (opcjonalnie)
            description: Nowy opis (opcjonalnie)
            parameters: Nowe parametry (opcjonalnie)
            version: Nowa wersja (opcjonalnie)
            status: Nowy status (opcjonalnie)
            category: Nowa kategoria (opcjonalnie)
            tags: Nowe tagi (opcjonalnie)
            purpose: Nowy cel (opcjonalnie)
            methodology: Nowa metodologia (opcjonalnie)
            **kwargs: Dodatkowe parametry
            
        Returns:
            Strategy: Zaktualizowana strategia lub None jeśli nie znaleziono
        """
        with self._lock:
            strategy = self.storage.get(strategy_id)
            if strategy is None:
                logger.warning(f"Strategy not found: {strategy_id}")
                return None
            
            # Aktualizacja pól
            if name is not None:
                strategy.name = name
            if description is not None:
                strategy.description = description
            if parameters is not None:
                strategy.parameters = parameters
            if version is not None:
                strategy.version = version
            if status is not None:
                strategy.status = status
            if category is not None:
                strategy.category = category
            if tags is not None:
                strategy.tags = tags
            if purpose is not None:
                strategy.purpose = purpose
            if methodology is not None:
                strategy.methodology = methodology
            
            # Aktualizacja dodatkowych pól
            for key, value in kwargs.items():
                if hasattr(strategy, key):
                    setattr(strategy, key, value)
            
            strategy.last_updated = datetime.now()
            
            # Walidacja
            if self.config.enable_validation:
                valid, errors = self.validator.validate_strategy(strategy, is_update=True)
                if not valid:
                    error_msg = f"Strategy validation failed: {errors}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
            
            # Zapis
            self.storage.update(strategy)
            
            # Wywołanie hooków
            self._trigger_on_update(strategy)
            
            logger.info(f"Strategy updated: {strategy_id}")
            
            return strategy
    
    def evaluate_strategy(
        self,
        strategy_id: str,
        evaluator_agent_id: str,
        effectiveness: float = 0.0,
        stability: float = 0.0,
        efficiency: float = 0.0,
        reliability: float = 0.0,
        adaptability: float = 0.0,
        confidence: float = 0.0,
        strengths: List[str] = None,
        weaknesses: List[str] = None,
        recommendations: List[str] = None,
        notes: str = "",
        **kwargs
    ) -> Tuple[Optional[Strategy], Optional[StrategyEvaluation]]:
        """
        Ocena strategii.
        
        Args:
            strategy_id: ID strategii do oceny
            evaluator_agent_id: ID agenta oceniającego
            effectiveness: Skuteczność (0.0 - 1.0)
            stability: Stabilność (0.0 - 1.0)
            efficiency: Wydajność (0.0 - 1.0)
            reliability: Niezawodność (0.0 - 1.0)
            adaptability: Dostosowalność (0.0 - 1.0)
            confidence: Pewność oceny (0.0 - 1.0)
            strengths: Lista mocnych stron
            weaknesses: Lista słabych stron
            recommendations: Lista zaleceń
            notes: Notatki
            **kwargs: Dodatkowe parametry
            
        Returns:
            Tuple[Strategy, StrategyEvaluation]: Zaktualizowana strategia i ocena
        """
        with self._lock:
            strategy = self.storage.get(strategy_id)
            if strategy is None:
                logger.warning(f"Strategy not found: {strategy_id}")
                return None, None
            
            # Walidacja wartości
            def clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
                return max(min_val, min(max_val, value))
            
            effectiveness = clamp(effectiveness)
            stability = clamp(stability)
            efficiency = clamp(efficiency)
            reliability = clamp(reliability)
            adaptability = clamp(adaptability)
            confidence = clamp(confidence)
            
            # Utworzenie oceny
            evaluation = StrategyEvaluation(
                strategy_id=strategy_id,
                evaluator_agent_id=evaluator_agent_id,
                effectiveness=effectiveness,
                stability=stability,
                efficiency=efficiency,
                reliability=reliability,
                adaptability=adaptability,
                confidence=confidence,
                strengths=strengths or [],
                weaknesses=weaknesses or [],
                recommendations=recommendations or [],
                notes=notes
            )
            
            # Obliczenie ogólnej oceny
            evaluation.overall_score = evaluation.calculate_overall_score()
            evaluation.ranking_score = evaluation.overall_score * confidence
            
            # Aktualizacja strategii
            strategy.update_from_evaluation(evaluation)
            strategy.last_evaluation = datetime.now()
            
            # Zapis oceny
            strategy.evaluations.append(evaluation.evaluation_id)
            
            # Zapis strategii
            self.storage.update(strategy)
            
            # Wywołanie hooków
            self._trigger_on_evaluate(strategy, evaluation)
            
            logger.info(f"Strategy evaluated: {strategy_id} by {evaluator_agent_id}, score: {evaluation.overall_score:.3f}")
            
            return strategy, evaluation
    
    def rank_strategies(
        self,
        agent_id: Optional[str] = None,
        strategy_type: Optional[StrategyType] = None,
        status: Optional[StrategyStatus] = None,
        limit: int = 10,
        weights: Optional[Dict[str, float]] = None
    ) -> List[StrategyRanking]:
        """
        Ranking strategii.
        
        Args:
            agent_id: ID agenta (opcjonalnie, dla rankingu specyficznego dla agenta)
            strategy_type: Typ strategii (opcjonalnie)
            status: Status strategii (opcjonalnie)
            limit: Maksymalna liczba wyników
            weights: Własne wagi dla kryteriów rankingu
            
        Returns:
            List[StrategyRanking]: Lista rankingów strategii
        """
        with self._lock:
            # Pobranie strategii do rankingu
            strategies = self.storage.list_all()
            
            # Filtrowanie
            if agent_id:
                strategies = [s for s in strategies if s.agent_owner == agent_id]
            if strategy_type:
                strategies = [s for s in strategies if s.strategy_type == strategy_type]
            if status:
                strategies = [s for s in strategies if s.status == status]
            
            # Sortowanie według ranking_score
            sorted_strategies = sorted(
                strategies,
                key=lambda s: (s.ranking_score, s.success_rate, s.avg_score),
                reverse=True
            )
            
            # Tworzenie rankingu
            rankings = []
            for i, strategy in enumerate(sorted_strategies[:limit]):
                ranking = StrategyRanking(
                    strategy_id=strategy.strategy_id,
                    rank=i + 1,
                    total_strategies=len(sorted_strategies),
                    percentile=1.0 - (i / len(sorted_strategies)) if len(sorted_strategies) > 0 else 0.0,
                    ranking_category="overall" if not agent_id else f"agent_{agent_id}",
                    agent_specific=agent_id is not None,
                    target_agent_id=agent_id or ""
                )
                
                # Aktualizacja rankingu w strategii
                strategy.current_rank = i + 1
                
                rankings.append(ranking)
            
            # Wywołanie hooków
            self._trigger_on_rank(rankings)
            
            logger.info(f"Strategies ranked, {len(rankings)} results for {agent_id or 'all'}")
            
            return rankings
    
    def archive_strategy(
        self,
        strategy_id: str,
        reason: str = "Manual archive",
        **kwargs
    ) -> Optional[Strategy]:
        """
        Archiwizacja strategii.
        
        Args:
            strategy_id: ID strategii do archiwizacji
            reason: Powód archiwizacji
            **kwargs: Dodatkowe parametry
            
        Returns:
            Strategy: Archiwizowana strategia lub None jeśli nie znaleziono
        """
        with self._lock:
            strategy = self.storage.get(strategy_id)
            if strategy is None:
                logger.warning(f"Strategy not found: {strategy_id}")
                return None
            
            # Archiwizacja
            strategy.archive()
            strategy.context['archive_reason'] = reason
            strategy.context['archive_date'] = datetime.now().isoformat()
            
            # Zapis
            self.storage.update(strategy)
            
            # Wywołanie hooków
            self._trigger_on_archive(strategy)
            
            logger.info(f"Strategy archived: {strategy_id}, reason: {reason}")
            
            return strategy
    
    def get_strategy(self, strategy_id: str) -> Optional[Strategy]:
        """Pobranie strategii po ID."""
        with self._lock:
            return self.storage.get(strategy_id)
    
    def get_strategies_by_agent(self, agent_id: str) -> List[Strategy]:
        """Pobranie strategii agenta."""
        with self._lock:
            return self.storage.get_by_agent(agent_id)
    
    def get_active_strategies(self, agent_id: Optional[str] = None) -> List[Strategy]:
        """Pobranie aktywnych strategii."""
        with self._lock:
            strategies = self.storage.get_by_status(StrategyStatus.ACTIVE)
            if agent_id:
                strategies = [s for s in strategies if s.agent_owner == agent_id]
            return strategies
    
    def delete_strategy(self, strategy_id: str) -> bool:
        """Usunięcie strategii."""
        with self._lock:
            result = self.storage.remove(strategy_id)
            if result:
                logger.info(f"Strategy deleted: {strategy_id}")
            else:
                logger.warning(f"Strategy not found for deletion: {strategy_id}")
            return result
    
    def count_strategies(self, agent_id: Optional[str] = None) -> int:
        """Zliczenie strategii."""
        with self._lock:
            if agent_id:
                return self.storage.count_by_agent(agent_id)
            return self.storage.count()
    
    def cleanup_archived(self, days: int = 30) -> int:
        """Czyszczenie archiwalnych strategii starszych niż N dni."""
        with self._lock:
            from datetime import timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days)
            archived_strategies = self.storage.get_by_status(StrategyStatus.ARCHIVED)
            
            deleted_count = 0
            for strategy in archived_strategies:
                if strategy.last_updated and (datetime.now() - strategy.last_updated).days > days:
                    self.storage.remove(strategy.strategy_id)
                    deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} archived strategies older than {days} days")
            return deleted_count


# Singleton
_strategy_manager: Optional[StrategyManager] = None
_strategy_manager_lock = threading.Lock()


def create_strategy_manager(config: Optional[StrategyManagerConfig] = None) -> StrategyManager:
    """Tworzenie nowej instancji Strategy Manager."""
    global _strategy_manager
    with _strategy_manager_lock:
        if _strategy_manager is None:
            _strategy_manager = StrategyManager(config)
        return _strategy_manager


def get_strategy_manager() -> StrategyManager:
    """Pobranie instancji singleton Strategy Manager."""
    global _strategy_manager
    if _strategy_manager is None:
        _strategy_manager = create_strategy_manager()
    return _strategy_manager


__all__ = [
    'StrategyManagerConfig',
    'StrategyStorage',
    'StrategyValidator',
    'StrategyManager',
    'create_strategy_manager',
    'get_strategy_manager'
]
