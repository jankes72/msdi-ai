"""
SSI V5 - Strategy Ranking Engine

Silnik rankingu strategii dla Strategy Laboratory.

Ranking według:
- skuteczność (effectiveness)
- stabilność (stability)
- ilość prób (usage count)
- aktualność (recency)
- poziom pewności (confidence)

Wersja: 1.0.0
Data: 2026-08-01
"""

import threading
import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from enum import Enum
import numpy as np

from .strategy_models import (
    Strategy,
    StrategyRanking,
    StrategyStatus,
    StrategyType
)

# Konfiguracja logowania
logger = logging.getLogger(__name__)


class RankingCriteria(Enum):
    """Kryteria rankingu."""
    EFFECTIVENESS = "effectiveness"      # Skuteczność
    STABILITY = "stability"             # Stabilność
    USAGE_COUNT = "usage_count"         # Ilość użyć
    RECENCY = "recency"                 # Aktualność
    CONFIDENCE = "confidence"           # Poziom pewności
    SUCCESS_RATE = "success_rate"       # Wskaźnik sukcesu
    AVG_SCORE = "avg_score"             # Średnia ocena
    RELIABILITY = "reliability"         # Niezawodność
    RANKING_SCORE = "ranking_score"     # Wynik rankingu (z ocen)
    REPEATABILITY = "repeatability"     # Powtarzalność wyników
    CONDITION_MATCH = "condition_match" # Dopasowanie do warunków działania
    ACTUALITY = "actuality"             # Aktualność (czas od ostatniej aktualizacji)


@dataclass
class RankingWeights:
    """Wagi kryteriów rankingu."""
    
    # Dom inch
    effectiveness: float = 0.25
    stability: float = 0.15
    usage_count: float = 0.10
    recency: float = 0.10
    confidence: float = 0.15
    success_rate: float = 0.10
    avg_score: float = 0.05
    reliability: float = 0.05
    
    # Nowe kryteria
    repeatability: float = 0.10
    condition_match: float = 0.05
    actuality: float = 0.05
    
    def to_dict(self) -> Dict[str, float]:
        """Konwersja do słownika."""
        return {
            'effectiveness': self.effectiveness,
            'stability': self.stability,
            'usage_count': self.usage_count,
            'recency': self.recency,
            'confidence': self.confidence,
            'success_rate': self.success_rate,
            'avg_score': self.avg_score,
            'reliability': self.reliability,
            'repeatability': self.repeatability,
            'condition_match': self.condition_match,
            'actuality': self.actuality
        }
    
    def normalize(self) -> 'RankingWeights':
        """Normalizacja wag."""
        total = sum(self.to_dict().values())
        if total == 0:
            return RankingWeights()
        
        normalized = RankingWeights()
        for key, value in self.to_dict().items():
            setattr(normalized, key, value / total)
        
        return normalized
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'RankingWeights':
        """Tworzenie z słownika."""
        return cls(
            effectiveness=data.get('effectiveness', 0.25),
            stability=data.get('stability', 0.15),
            usage_count=data.get('usage_count', 0.10),
            recency=data.get('recency', 0.10),
            confidence=data.get('confidence', 0.15),
            success_rate=data.get('success_rate', 0.10),
            avg_score=data.get('avg_score', 0.05),
            reliability=data.get('reliability', 0.05),
            repeatability=data.get('repeatability', 0.10),
            condition_match=data.get('condition_match', 0.05),
            actuality=data.get('actuality', 0.05)
        )


@dataclass
class RankingConfig:
    """Konfiguracja rankingu."""
    
    # Wagi
    weights: RankingWeights = field(default_factory=RankingWeights)
    
    # Normalizacja
    normalize_scores: bool = True
    min_max_normalization: bool = True
    
    # Aktualność
    recency_days: int = 30  # Okres aktualności w dniach
    recency_decay_rate: float = 0.95  # Współczynnik zaniku
    
    # Progi
    min_usage_count: int = 5  # Minimalna ilość użyć do uwzględnienia
    min_success_rate: float = 0.5  # Minimalny wskaźnik sukcesu
    
    # Grupowanie
    group_by_agent: bool = False
    group_by_type: bool = False
    
    # Inne
    max_rankings: int = 100  # Maksymalna liczba ranked strategii
    update_interval_hours: int = 24  # Interwał aktualizacji rankingu
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika."""
        return {
            'weights': self.weights.to_dict(),
            'normalize_scores': self.normalize_scores,
            'min_max_normalization': self.min_max_normalization,
            'recency_days': self.recency_days,
            'recency_decay_rate': self.recency_decay_rate,
            'min_usage_count': self.min_usage_count,
            'min_success_rate': self.min_success_rate,
            'group_by_agent': self.group_by_agent,
            'group_by_type': self.group_by_type,
            'max_rankings': self.max_rankings,
            'update_interval_hours': self.update_interval_hours
        }


class ScoreNormalizer:
    """Normalizator wyników."""
    
    @staticmethod
    def min_max_normalization(values: List[float]) -> List[float]:
        """Normalizacja min-max."""
        if not values:
            return []
        
        min_val = min(values)
        max_val = max(values)
        
        if min_val == max_val:
            return [1.0 for _ in values]
        
        return [(x - min_val) / (max_val - min_val) for x in values]
    
    @staticmethod
    def z_score_normalization(values: List[float]) -> List[float]:
        """Normalizacja Z-score."""
        if not values:
            return []
        
        mean = sum(values) / len(values)
        std = (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5
        
        if std == 0:
            return [1.0 for _ in values]
        
        return [(x - mean) / std for x in values]
    
    @staticmethod
    def sigmoid_normalization(values: List[float], scale: float = 1.0) -> List[float]:
        """Normalizacja sigmoid."""
        return [1 / (1 + math.exp(-x * scale)) for x in values]
    
    @staticmethod
    def normalize_to_range(values: List[float], min_val: float = 0.0, max_val: float = 1.0) -> List[float]:
        """Normalizacja do zakresu."""
        if not values:
            return []
        
        normalized = ScoreNormalizer.min_max_normalization(values)
        return [min_val + (max_val - min_val) * x for x in normalized]


class RecencyCalculator:
    """Kalkulator aktualności."""
    
    def __init__(self, recency_days: int = 30, decay_rate: float = 0.95):
        self.recency_days = recency_days
        self.decay_rate = decay_rate
    
    def calculate_recency_score(self, last_used: Optional[datetime] = None,
                               last_evaluated: Optional[datetime] = None) -> float:
        """Obliczenie wyniku aktualności."""
        now = datetime.now()
        
        if last_used is None and last_evaluated is None:
            return 0.0
        
        # Używamy bardziej świeżej daty
        latest_date = last_used or last_evaluated
        if latest_date is None:
            latest_date = last_evaluated or last_used
        
        if latest_date is None:
            return 0.0
        
        # Obliczenie czasu od ostatniego użycia
        days_since_use = (now - latest_date).days
        
        if days_since_use <= 0:
            return 1.0
        elif days_since_use >= self.recency_days:
            return 0.0
        
        # Wykładniczy zanik
        return self.decay_rate ** days_since_use
    
    def calculate_usage_frequency(self, usage_count: int, days: int) -> float:
        """Obliczenie częstotliwości użycia."""
        if days <= 0:
            return 0.0
        
        return min(1.0, usage_count / days)


class StrategyRankingEngine:
    """
    Główna klasa silnika rankingu strategii.
    
    Ranking według:
    - skuteczność
    - stabilność
    - ilość prób
    - aktualność
    - poziom pewności
    """
    
    def __init__(self, config: Optional[RankingConfig] = None):
        self.config = config or RankingConfig()
        self.normalizer = ScoreNormalizer()
        self.recency_calculator = RecencyCalculator(
            recency_days=self.config.recency_days,
            decay_rate=self.config.recency_decay_rate
        )
        
        # Cache
        self._ranking_cache: Dict[str, List[StrategyRanking]] = {}
        self._last_update: datetime = datetime.min
        self._lock = threading.RLock()
        
        # Hooki
        self._on_rank_hooks: List[Callable[[List[StrategyRanking]], None]] = []
        
        logger.info(f"StrategyRankingEngine initialized with config: {self.config.to_dict()}")
    
    def on_rank(self, callback: Callable[[List[StrategyRanking]], None]) -> None:
        """Rejestracja hooka na ranking."""
        self._on_rank_hooks.append(callback)
    
    def _trigger_on_rank(self, rankings: List[StrategyRanking]) -> None:
        """Wywołanie hooków na ranking."""
        for hook in self._on_rank_hooks:
            try:
                hook(rankings)
            except Exception as e:
                logger.error(f"Error in on_rank hook: {e}")
    
    def normalize_weights(self, weights: Optional[RankingWeights] = None) -> RankingWeights:
        """Normalizacja wag."""
        if weights is None:
            weights = self.config.weights
        
        return weights.normalize()
    
    def calculate_strategy_score(
        self,
        strategy: Strategy,
        weights: Optional[RankingWeights] = None
    ) -> float:
        """
        Obliczenie wyniku rankingu dla strategii.
        
        Args:
            strategy: Strategia do oceny
            weights: Wagi kryteriów (opcjonalnie)
            
        Returns:
            float: Wynik rankingu (0.0 - 1.0)
        """
        if weights is None:
            weights = self.normalize_weights()
        
        # Obliczenie składników
        components = {}
        
        # 1. Skuteczność (effectiveness) - na podstawie avg_score i success_rate
        effectiveness = strategy.avg_score * strategy.success_rate
        components['effectiveness'] = effectiveness
        
        # 2. Stabilność (stability) - na podstawieξύ reliability i confidence
        stability = (strategy.reliability + strategy.confidence) / 2
        components['stability'] = stability
        
        # 3. Ilość prób (usage_count)
        usage_count = strategy.usage_count
        components['usage_count'] = min(100, usage_count) / 100  # Normalizacja do 0-1
        
        # 4. Aktualność (recency)
        recency = self.recency_calculator.calculate_recency_score(
            strategy.last_used, 
            strategy.last_evaluation
        )
        components['recency'] = recency
        
        # 5. Poziom pewności (confidence)
        confidence = strategy.confidence
        components['confidence'] = confidence
        
        # 6. Wskaźnik sukcesu (success_rate)
        success_rate = strategy.success_rate
        components['success_rate'] = success_rate
        
        # 7. Średnia ocena (avg_score)
        avg_score = strategy.avg_score
        components['avg_score'] = avg_score
        
        # 8. Niezawodność (reliability)
        reliability = strategy.reliability
        components['reliability'] = reliability
        
        # 9. Istniejący wynik rankingu
        ranking_score = strategy.ranking_score
        components['ranking_score'] = ranking_score
        
        # Obliczenie ważonej sumy
        weighted_sum = sum(
            components[criteria.value] * getattr(weights, criteria.value, 0.0)
            for criteria in RankingCriteria
        )
        
        return weighted_sum
    
    def calculate_mus_score(
        self,
        strategy: Strategy,
        weights: Optional[RankingWeights] = None
    ) -> Dict[str, Any]:
        """
        Obliczenie rozbudowanego wyniku rankingu (MUS - Multi-criteria Urgency Score).
        
        Args:
            strategy: Strategia do oceny
            weights: Wagi kryteriów (opcjonalnie)
            
        Returns:
            Dict: Słownik z wynikami i componentami
        """
        if weights is None:
            weights = self.normalize_weights()
        
        # Obliczenie podstawowych componentów
        components = self._calculate_components(strategy)
        
        # Obliczenie ważonej sumy
        weighted_components = {}
        for criteria, value in components.items():
            weight = getattr(weights, criteria, 0.0)
            weighted_components[criteria] = value * weight
        
        # Sumowanie
        total_score = sum(weighted_components.values())
        
        # Normalizacja do 0-1
        mus_score = self._normalize_score(total_score)
        
        return {
            'total_score': total_score,
            'mus_score': mus_score,
            'components': components,
            'weighted_components': weighted_components,
            'weights': weights.to_dict()
        }
    
    def _calculate_components(self, strategy: Strategy) -> Dict[str, float]:
        """Obliczenie componentów rankingu."""
        components = {}
        
        # Podstawowe metryki
        components['effectiveness'] = strategy.avg_score * strategy.success_rate
        components['stability'] = (strategy.reliability + strategy.confidence) / 2
        components['usage_count'] = min(100, strategy.usage_count) / 100
        components['recency'] = self.recency_calculator.calculate_recency_score(
            strategy.last_used, strategy.last_evaluation
        )
        components['confidence'] = strategy.confidence
        components['success_rate'] = strategy.success_rate
        components['avg_score'] = strategy.avg_score
        components['reliability'] = strategy.reliability
        components['ranking_score'] = strategy.ranking_score
        
        # Nowe kryteria
        
        # Powtarzalność (repeatability) - na podstawie stability, confidence i success_rate
        # Im wyższe i bardziej stabilne wyniki, tym wyższa powtarzalność
        repeatability = (strategy.stability + strategy.confidence + strategy.success_rate) / 3.0
        components['repeatability'] = repeatability
        
        # Dopasowanie do warunków działania (condition_match) - na podstawie usage_count i success_rate
        # Im więcej użyć i wyższy success_rate, tym lepsze dopasowanie do warunków
        condition_match = min(1.0, strategy.usage_count / 20.0) * strategy.success_rate
        components['condition_match'] = condition_match
        
        # Aktualność (actuality) - na podstawie czasu od ostatniej aktualizacji/oceny
        # Im bardziej aktualna strategia, tym wyższa aktualność
        now = datetime.now()
        if strategy.last_updated:
            days_since_update = (now - strategy.last_updated).days
            # 0 dni = 1.0, 30 dni = 0.0 (wykładniczy zanik)
            actuality = max(0.0, 1.0 - (days_since_update / 30.0))
        else:
            actuality = 0.5
        components['actuality'] = actuality
        
        return components
    
    def _normalize_score(self, score: float) -> float:
        """Normalizacja wyniku do zakresu 0-1."""
        return max(0.0, min(1.0, score))
    
    def rank_strategies(
        self,
        strategies: List[Strategy],
        weights: Optional[RankingWeights] = None,
        filter_active: bool = True,
        filter_min_usage: bool = True,
        limit: Optional[int] = None
    ) -> List[StrategyRanking]:
        """
        Ranking strategii.
        
        Args:
            strategies: Lista strategii do rankingu
            weights: Wagi kryteriów (opcjonalnie)
            filter_active: Filtrować tylko aktywne strategie
            filter_min_usage: Filtrować strategie z minimalną ilością użyć
            limit: Maksymalna liczba wyników
            
        Returns:
            List[StrategyRanking]: Posortowana lista rankingów
        """
        with self._lock:
            # Filtrowanie
            filtered_strategies = []
            for strategy in strategies:
                if filter_active and strategy.status != StrategyStatus.ACTIVE:
                    continue
                if filter_min_usage and strategy.usage_count < self.config.min_usage_count:
                    continue
                if filter_min_usage and strategy.success_rate < self.config.min_success_rate:
                    continue
                
                filtered_strategies.append(strategy)
            
            if not filtered_strategies:
                return []
            
            # Obliczenie wyników
            scores = []
            for strategy in filtered_strategies:
                score = self.calculate_strategy_score(strategy, weights)
                scores.append(score)
            
            # Normalizacja wyników
            if self.config.normalize_scores:
                if self.config.min_max_normalization:
                    normalized_scores = ScoreNormalizer.min_max_normalization(scores)
                else:
                    normalized_scores = ScoreNormalizer.z_score_normalization(scores)
            else:
                normalized_scores = scores
            
            # Tworzenie rankingów
            strategy_scores = list(zip(filtered_strategies, normalized_scores))
            
            # Sortowanie
            sorted_scores = sorted(
                strategy_scores,
                key=lambda x: x[1],
                reverse=True
            )
            
            # Tworzenie listy rankingów
            rankings = []
            for i, (strategy, score) in enumerate(sorted_scores[:limit]):
                ranking = StrategyRanking(
                    strategy_id=strategy.strategy_id,
                    rank=i + 1,
                    total_strategies=len(sorted_scores),
                    percentile=1.0 - (i / len(sorted_scores)) if len(sorted_scores) > 0 else 0.0,
                    ranking_category="overall",
                    weights_used=weights.to_dict() if weights else self.config.weights.to_dict()
                )
                rankings.append(ranking)
            
            # Aktualizacja cache
            cache_key = self._get_cache_key(strategies, weights, filter_active, filter_min_usage)
            self._ranking_cache[cache_key] = rankings
            self._last_update = datetime.now()
            
            # Wywołanie hooków
            self._trigger_on_rank(rankings)
            
            logger.info(f"Ranked {len(rankings)} strategies (total: {len(filtered_strategies)})")
            
            return rankings
    
    def rank_by_agent(
        self,
        strategies: List[Strategy],
        agent_id: str,
        weights: Optional[RankingWeights] = None,
        filter_active: bool = True,
        limit: Optional[int] = None
    ) -> List[StrategyRanking]:
        """
        Ranking strategii dla konkretnego agenta.
        
        Args:
            strategies: Lista strategii
            agent_id: ID agenta
            weights: Wagi kryteriów
            filter_active: Filtrować tylko aktywne
            limit: Maksymalna liczba wyników
            
        Returns:
            List[StrategyRanking]: Ranking dla agenta
        """
        # Filtrowanie strategii agenta
        agent_strategies = [s for s in strategies if s.agent_owner == agent_id]
        
        # Ranking
        rankings = self.rank_strategies(
            strategies=agent_strategies,
            weights=weights,
            filter_active=filter_active,
            filter_min_usage=False,  # Nie filtrować po minimalnym użyciu
            limit=limit
        )
        
        # Aktualizacja kategorii
        for ranking in rankings:
            ranking.ranking_category = f"agent_{agent_id}"
            ranking.agent_specific = True
            ranking.target_agent_id = agent_id
        
        return rankings
    
    def rank_by_type(
        self,
        strategies: List[Strategy],
        strategy_type: Union[str, StrategyType],
        weights: Optional[RankingWeights] = None,
        filter_active: bool = True,
        limit: Optional[int] = None
    ) -> List[StrategyRanking]:
        """
        Ranking strategii po typie.
        
        Args:
            strategies: Lista strategii
            strategy_type: Typ strategii
            weights: Wagi kryteriów
            filter_active: Filtrować tylko aktywne
            limit: Maksymalna liczba wyników
            
        Returns:
            List[StrategyRanking]: Ranking dla typu
        """
        # Filtrowanie strategii po typie
        type_name = strategy_type if isinstance(strategy_type, str) else strategy_type.name
        type_strategies = [s for s in strategies if s.strategy_type.name == type_name]
        
        # Ranking
        rankings = self.rank_strategies(
            strategies=type_strategies,
            weights=weights,
            filter_active=filter_active,
            filter_min_usage=True,
            limit=limit
        )
        
        # Aktualizacja kategorii
        for ranking in rankings:
            ranking.ranking_category = f"type_{type_name}"
        
        return rankings
    
    def get_top_n_ranked(
        self,
        strategies: List[Strategy],
        n: int = 10,
        weights: Optional[RankingWeights] = None
    ) -> List[Strategy]:
        """
        Pobranie top N strategii.
        
        Args:
            strategies: Lista strategii
            n: Liczba strategii do zwrócenia
            weights: Wagi kryteriów
            
        Returns:
            List[Strategy]: Posortowana lista top N strategii
        """
        rankings = self.rank_strategies(
            strategies=strategies,
            weights=weights,
            filter_active=True,
            filter_min_usage=True,
            limit=n
        )
        
        # Pobranie strategii według rankingu
        top_strategies = []
        for ranking in rankings[:n]:
            for strategy in strategies:
                if strategy.strategy_id == ranking.strategy_id:
                    top_strategies.append(strategy)
                    break
        
        return top_strategies
    
    def _get_cache_key(
        self,
        strategies: List[Strategy],
        weights: Optional[RankingWeights],
        filter_active: bool,
        filter_min_usage: bool
    ) -> str:
        """Generowanie klucza cache."""
        strategy_ids = sorted([s.strategy_id for s in strategies])
        weights_str = str(weights.to_dict() if weights else self.config.weights.to_dict())
        return f"{','.join(strategy_ids)}::{weights_str}::{filter_active}::{filter_min_usage}"
    
    def get_cached_ranking(
        self,
        strategies: List[Strategy],
        weights: Optional[RankingWeights] = None,
        filter_active: bool = True,
        filter_min_usage: bool = True
    ) -> Optional[List[StrategyRanking]]:
        """Pobranie rankingu z cache."""
        cache_key = self._get_cache_key(strategies, weights, filter_active, filter_min_usage)
        return self._ranking_cache.get(cache_key)
    
    def clear_cache(self) -> None:
        """Wyczyszczenie cache."""
        self._ranking_cache.clear()
        logger.info("Ranking cache cleared")
    
    def get_ranking_report(
        self,
        strategies: List[Strategy],
        weights: Optional[RankingWeights] = None,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Generowanie raportu rankingu.
        
        Args:
            strategies: Lista strategii
            weights: Wagi kryteriów
            include_details: Czy dołączać szczegóły
            
        Returns:
            Dict: Raport rankingu
        """
        # Obliczenie rankingu
        rankings = self.rank_strategies(
            strategies=strategies,
            weights=weights,
            filter_active=True,
            filter_min_usage=True,
            limit=20
        )
        
        # Generowanie raportu
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_strategies': len(strategies),
            'ranked_strategies': len(rankings),
            'weights': weights.to_dict() if weights else self.config.weights.to_dict(),
            'config': self.config.to_dict(),
            'rankings': [r.to_dict() for r in rankings]
        }
        
        if include_details:
            details = []
            for ranking in rankings:
                for strategy in strategies:
                    if strategy.strategy_id == ranking.strategy_id:
                        mus_score = self.calculate_mus_score(strategy, weights)
                        details.append({
                            'strategy_id': strategy.strategy_id,
                            'name': strategy.name,
                            'agent_owner': strategy.agent_owner,
                            'score': mus_score['mus_score'],
                            'rank': ranking.rank,
                            'components': mus_score['components'],
                            'weighted_components': mus_score['weighted_components']
                        })
                        break
            
            report['details'] = details
        
        return report


# Singleton
_ranking_engine: Optional[StrategyRankingEngine] = None
_ranking_engine_lock = threading.Lock()


def create_ranking_engine(config: Optional[RankingConfig] = None) -> StrategyRankingEngine:
    """Tworzenie nowej instancji Strategy Ranking Engine."""
    global _ranking_engine
    with _ranking_engine_lock:
        if _ranking_engine is None:
            _ranking_engine = StrategyRankingEngine(config)
        return _ranking_engine


def get_ranking_engine() -> StrategyRankingEngine:
    """Pobranie instancji singleton Strategy Ranking Engine."""
    global _ranking_engine
    if _ranking_engine is None:
        _ranking_engine = create_ranking_engine()
    return _ranking_engine


__all__ = [
    'RankingCriteria',
    'RankingWeights',
    'RankingConfig',
    'ScoreNormalizer',
    'RecencyCalculator',
    'StrategyRankingEngine',
    'create_ranking_engine',
    'get_ranking_engine'
]
