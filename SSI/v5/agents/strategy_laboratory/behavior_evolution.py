"""
SSI V5 - Behavior Evolution Module

Mechanizm ewolucji zachowania wynikajacy z doswiadczen strategii.

Wyniki strategii wplywaja na:
Behavior Memory
↓
Agent Analysis Memory
↓
Decision Memory
↓
Behavior Evolution
↓
Personality Evolution
↓
Preferencje kolejnych strategii

Zasada: Tworzymy jedynie mechanizm ewolucji zachowania wynikajacy z doswiadczen.
Nie tworzymy sztucznej osobowosci.

Wersja: 1.0.0
Data: 2026-08-01
"""

import threading
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from enum import Enum, auto
import uuid
import math
from collections import defaultdict

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


class BehaviorEvolutionType(Enum):
    """Typ ewolucji zachowania."""
    SUCCESS_PATTERN = auto()      # Wzorce sukcesu - powtarzanie udanych strategii
    FAILURE_AVOIDANCE = auto()    # Unikanie porazek - redukcja ryzyka
    STABILITY_PREFERENCE = auto()  # Stabilnosc - preferowanie stabilnych strategii
    CONFIDENCE_EVOLUTION = auto() # Ewolucja pewnosci - dostosowanie progow pewnosci
    RISK_ADJUSTMENT = auto()     # Dostosowanie ryzyka na podstawie wynikow
    ADAPTABILITY_FOCUS = auto()   # Dostosowywanie sie do zmiennych warunkow
    CONDITION_LEARNING = auto()   # Uczenie sie warunkow dzialania
    REPEATABILITY_FOCUS = auto() # Skupienie na powtarzalnosci wynikow


class EvolutionDirection(Enum):
    """Kierunek ewolucji."""
    INCREASE = auto()    # Zwiekszenie
    DECREASE = auto()    # Zmniejszenie
    MAINTAIN = auto()    # Utrzymanie
    ADAPT = auto()       # Dostosowanie
    OPTIMIZE = auto()    # Optymalizacja


class InfluenceFactor(Enum):
    """Czynniki wplywajace na ewolucje."""
    SUCCESS_RATE = "success_rate"
    FAILURE_RATE = "failure_rate"
    CONFIDENCE = "confidence"
    STABILITY = "stability"
    RISK_LEVEL = "risk_level"
    EXECUTION_TIME = "execution_time"
    RESOURCE_USAGE = "resource_usage"
    ADAPTABILITY = "adaptability"
    REPEATABILITY = "repeatability"
    CONDITIONS = "conditions"


@dataclass
class BehaviorEvolutionConfig:
    """Konfiguracja modulu ewolucji zachowania."""
    
    # Ogolne
    enabled: bool = True
    learning_rate: float = 0.1  # terminou uczenia sie (0.0 - 1.0)
    evolution_interval: int = 10  # Liczba wynikow przed ponowna ewolucja
    
    # Wagi czynnikiw
    weights: Dict[InfluenceFactor, float] = field(default_factory=lambda: {
        InfluenceFactor.SUCCESS_RATE: 0.25,
        InfluenceFactor.FAILURE_RATE: 0.20,
        InfluenceFactor.CONFIDENCE: 0.15,
        InfluenceFactor.STABILITY: 0.15,
        InfluenceFactor.RISK_LEVEL: 0.10,
        InfluenceFactor.ADAPTABILITY: 0.10,
        InfluenceFactor.REPEATABILITY: 0.10,
        InfluenceFactor.CONDITIONS: 0.05
    })
    
    # Progi ewolucji
    success_threshold: float = 0.7  # Prog sukcesu do wzmacniania zachowania
    failure_threshold: float = 0.3  # Prog porazki do oslabiania zachowania
    stability_threshold: float = 0.8  # Prog stabilnosci
    confidence_threshold: float = 0.6  # Prog pewnosci
    
    # Ograniczenia
    max_evolution_rate: float = 0.5  # Maksymalna szybkosc ewolucji
    min_behavior_change: float = 0.01  # Minimalna zmiana zachowania
    
    # Persystencja
    persistence_enabled: bool = True
    persistence_path: str = "data/behavior_evolution"
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        return {
            'enabled': self.enabled,
            'learning_rate': self.learning_rate,
            'evolution_interval': self.evolution_interval,
            'weights': {k.name: v for k, v in self.weights.items()},
            'success_threshold': self.success_threshold,
            'failure_threshold': self.failure_threshold,
            'stability_threshold': self.stability_threshold,
            'confidence_threshold': self.confidence_threshold,
            'max_evolution_rate': self.max_evolution_rate,
            'min_behavior_change': self.min_behavior_change,
            'persistence_enabled': self.persistence_enabled,
            'persistence_path': self.persistence_path
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BehaviorEvolutionConfig':
        """Tworzenie z slownika."""
        weights = {}
        for key, value in data.get('weights', {}).items():
            try:
                factor = InfluenceFactor[key]
                weights[factor] = value
            except KeyError:
                pass
        
        return cls(
            enabled=data.get('enabled', True),
            learning_rate=data.get('learning_rate', 0.1),
            evolution_interval=data.get('evolution_interval', 10),
            weights=weights or cls().weights,
            success_threshold=data.get('success_threshold', 0.7),
            failure_threshold=data.get('failure_threshold', 0.3),
            stability_threshold=data.get('stability_threshold', 0.8),
            confidence_threshold=data.get('confidence_threshold', 0.6),
            max_evolution_rate=data.get('max_evolution_rate', 0.5),
            min_behavior_change=data.get('min_behavior_change', 0.01),
            persistence_enabled=data.get('persistence_enabled', True),
            persistence_path=data.get('persistence_path', "data/behavior_evolution")
        )


@dataclass
class BehaviorEvolutionEvent:
    """Zdarzenie ewolucji zachowania."""
    
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    strategy_id: str = ""
    evolution_type: BehaviorEvolutionType = BehaviorEvolutionType.SUCCESS_PATTERN
    direction: EvolutionDirection = EvolutionDirection.MAINTAIN
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Metryki
    success_rate: float = 0.0
    confidence: float = 0.0
    stability: float = 0.0
    risk_level: float = 0.0
    adaptability: float = 0.0
    repeatability: float = 0.0
    
    # Cambios
    behavior_changes: Dict[str, float] = field(default_factory=dict)
    personality_changes: Dict[str, float] = field(default_factory=dict)
    preference_changes: Dict[str, Any] = field(default_factory=dict)
    
    # Kontekst
    result_id: Optional[str] = None
    evaluation_id: Optional[str] = None
    experiment_id: Optional[str] = None
    
    # Opis
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        return {
            'event_id': self.event_id,
            'agent_id': self.agent_id,
            'strategy_id': self.strategy_id,
            'evolution_type': self.evolution_type.name,
            'direction': self.direction.name,
            'timestamp': self.timestamp.isoformat(),
            'success_rate': self.success_rate,
            'confidence': self.confidence,
            'stability': self.stability,
            'risk_level': self.risk_level,
            'adaptability': self.adaptability,
            'repeatability': self.repeatability,
            'behavior_changes': self.behavior_changes,
            'personality_changes': self.personality_changes,
            'preference_changes': self.preference_changes,
            'result_id': self.result_id,
            'evaluation_id': self.evaluation_id,
            'experiment_id': self.experiment_id,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BehaviorEvolutionEvent':
        """Tworzenie z slownika."""
        return cls(
            event_id=data.get('event_id', str(uuid.uuid4())),
            agent_id=data.get('agent_id', ""),
            strategy_id=data.get('strategy_id', ""),
            evolution_type=BehaviorEvolutionType[data.get('evolution_type', 'SUCCESS_PATTERN')],
            direction=EvolutionDirection[data.get('direction', 'MAINTAIN')],
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
            success_rate=data.get('success_rate', 0.0),
            confidence=data.get('confidence', 0.0),
            stability=data.get('stability', 0.0),
            risk_level=data.get('risk_level', 0.0),
            adaptability=data.get('adaptability', 0.0),
            repeatability=data.get('repeatability', 0.0),
            behavior_changes=data.get('behavior_changes', {}),
            personality_changes=data.get('personality_changes', {}),
            preference_changes=data.get('preference_changes', {}),
            result_id=data.get('result_id'),
            evaluation_id=data.get('evaluation_id'),
            experiment_id=data.get('experiment_id'),
            description=data.get('description', "")
        )


@dataclass
class AgentBehaviorProfile:
    """Profil zachowania agenta."""
    
    agent_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Parametry zachowania
    risk_tolerance: float = 0.5  # Tolerancja ryzyka (0.0 - 1.0)
    confidence_preference: float = 0.7  # Preferowane minimum pewnosci (0.0 - 1.0)
    stability_preference: float = 0.8  # Preferencja stabilnosci (0.0 - 1.0)
    adaptability_preference: float = 0.5  # Preferencja dostosowalnosci (0.0 - 1.0)
    
    # Parametry decyzyjne
    decision_speed: float = 0.5  # Predkosc podejmowania decyzji (0.0 - 1.0, slow to fast)
    analysis_depth: int = 3  # Glebowosc analizy (1 - 10)
    consider_alternatives: bool = True  # Czy rozpatrywac alternatywy
    
    # Preferencje strategii
    preferred_strategy_types: Dict[str, float] = field(default_factory=dict)  # Typy strategii i ich wagi
    preferred_risk_levels: Dict[str, float] = field(default_factory=dict)  # Poziomy ryzyka i wagi
    
    # Historia ewolucji
    evolution_history: List[str] = field(default_factory=list)  # Liste des ID zdarzen
    evolution_events: Dict[str, BehaviorEvolutionEvent] = field(default_factory=dict)
    
    # Statystyki
    total_evolutions: int = 0
    last_evolution: Optional[datetime] = None
    
    def __post_init__(self):
        """Inicjalizacja po utworzeniu."""
        if not hasattr(self, 'preferred_strategy_types') or not self.preferred_strategy_types:
            # Inicjalizacja preferencji typow strategii
            for strategy_type in StrategyType:
                self.preferred_strategy_types[strategy_type.name] = 0.5
        
        if not hasattr(self, 'preferred_risk_levels') or not self.preferred_risk_levels:
            # Inicjalizacja preferencji poziomow ryzyka
            self.preferred_risk_levels = {
                'LOW': 0.3,
                'MEDIUM': 0.5,
                'HIGH': 0.2
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        return {
            'agent_id': self.agent_id,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'risk_tolerance': self.risk_tolerance,
            'confidence_preference': self.confidence_preference,
            'stability_preference': self.stability_preference,
            'adaptability_preference': self.adaptability_preference,
            'decision_speed': self.decision_speed,
            'analysis_depth': self.analysis_depth,
            'consider_alternatives': self.consider_alternatives,
            'preferred_strategy_types': self.preferred_strategy_types,
            'preferred_risk_levels': self.preferred_risk_levels,
            'evolution_history': self.evolution_history,
            'total_evolutions': self.total_evolutions,
            'last_evolution': self.last_evolution.isoformat() if self.last_evolution else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentBehaviorProfile':
        """Tworzenie z slownika."""
        profile = cls(
            agent_id=data.get('agent_id', ""),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            last_updated=datetime.fromisoformat(data.get('last_updated', datetime.now().isoformat())),
            risk_tolerance=data.get('risk_tolerance', 0.5),
            confidence_preference=data.get('confidence_preference', 0.7),
            stability_preference=data.get('stability_preference', 0.8),
            adaptability_preference=data.get('adaptability_preference', 0.5),
            decision_speed=data.get('decision_speed', 0.5),
            analysis_depth=data.get('analysis_depth', 3),
            consider_alternatives=data.get('consider_alternatives', True),
            preferred_strategy_types=data.get('preferred_strategy_types', {}),
            preferred_risk_levels=data.get('preferred_risk_levels', {}),
            evolution_history=data.get('evolution_history', []),
            total_evolutions=data.get('total_evolutions', 0),
            last_evolution=datetime.fromisoformat(data.get('last_evolution')) if data.get('last_evolution') else None
        )
        
        # Inicjalizacja preferencji jeśli puste
        if not profile.preferred_strategy_types:
            for strategy_type in StrategyType:
                profile.preferred_strategy_types[strategy_type.name] = 0.5
        
        if not profile.preferred_risk_levels:
            profile.preferred_risk_levels = {'LOW': 0.3, 'MEDIUM': 0.5, 'HIGH': 0.2}
        
        return profile
    
    def get_strategy_type_preference(self, strategy_type: StrategyType) -> float:
        """Pobranie preferencji dla typu strategii."""
        return self.preferred_strategy_types.get(strategy_type.name, 0.5)
    
    def get_risk_level_preference(self, risk_level: float) -> float:
        """Pobranie preferencji dla poziomu ryzyka."""
        if risk_level < 0.3:
            return self.preferred_risk_levels.get('LOW', 0.3)
        elif risk_level < 0.7:
            return self.preferred_risk_levels.get('MEDIUM', 0.5)
        else:
            return self.preferred_risk_levels.get('HIGH', 0.2)
    
    def update_preference(self, strategy_type: StrategyType, delta: float) -> None:
        """Aktualizacja preferencji dla typu strategii."""
        current = self.preferred_strategy_types.get(strategy_type.name, 0.5)
        new_value = max(0.0, min(1.0, current + delta))
        self.preferred_strategy_types[strategy_type.name] = new_value
        self.last_updated = datetime.now()
    
    def update_risk_preference(self, risk_level: str, delta: float) -> None:
        """Aktualizacja preferencji dla poziomu ryzyka."""
        if risk_level in self.preferred_risk_levels:
            current = self.preferred_risk_levels[risk_level]
            new_value = max(0.0, min(1.0, current + delta))
            self.preferred_risk_levels[risk_level] = new_value
            self.last_updated = datetime.now()


@dataclass
class StrategyInfluenceAnalysis:
    """Analiza wplywu strategii na zachowanie."""
    
    strategy_id: str = ""
    agent_id: str = ""
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    
    # Metryki strategii
    success_rate: float = 0.0
    confidence: float = 0.0
    stability: float = 0.0
    reliability: float = 0.0
    adaptability: float = 0.0
    avg_score: float = 0.0
    usage_count: int = 0
    
    # Wplyw na zachowanie
    influence_scores: Dict[InfluenceFactor, float] = field(default_factory=dict)
    evolution_recommendations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Ostateczna ocena wplywu
    overall_influence: float = 0.0
    evolution_direction: EvolutionDirection = EvolutionDirection.MAINTAIN
    
    def calculate_influence_scores(self, config: BehaviorEvolutionConfig) -> None:
        """Obliczenie wynikow wplywu."""
        # Normalizacja metryk
        scores = {}
        
        # Success rate (wywroz citing)
        scores[InfluenceFactor.SUCCESS_RATE] = self.success_rate
        
        # Failure rate (1 - success_rate)
        scores[InfluenceFactor.FAILURE_RATE] = 1.0 - self.success_rate
        
        # Confidence
        scores[InfluenceFactor.CONFIDENCE] = self.confidence
        
        # Stability
        scores[InfluenceFactor.STABILITY] = self.stability
        
        # Risk level (odwrotnie proporcjonalny do success_rate i confidence)
        risk_score = (1.0 - self.success_rate) * (1.0 - self.confidence)
        scores[InfluenceFactor.RISK_LEVEL] = risk_score
        
        # Adaptability
        scores[InfluenceFactor.ADAPTABILITY] = self.adaptability
        
        # Repeatability (na podstawie stability i confidence)
        repeatability = (self.stability + self.confidence) / 2.0
        scores[InfluenceFactor.REPEATABILITY] = repeatability
        
        # Conditions (na podstawie usage_count - im wiecej uzyc, tym bardziej znane warunki)
        conditions_score = min(1.0, self.usage_count / 10.0)  # Normalizacja do 10 uzyc
        scores[InfluenceFactor.CONDITIONS] = conditions_score
        
        self.influence_scores = scores
        
        # Obliczenie ogolnego wplywu
        self.overall_influence = sum(
            score * config.weights.get(factor, 0.0)
            for factor, score in scores.items()
        )
        
        # Okreslenie kierunku ewolucji
        if self.overall_influence > 0.7:
            self.evolution_direction = EvolutionDirection.INCREASE
        elif self.overall_influence < 0.3:
            self.evolution_direction = EvolutionDirection.DECREASE
        else:
            self.evolution_direction = EvolutionDirection.MAINTAIN
        
        # Generowanie zalecec ewolucji
        self._generate_recommendations(config)
    
    def _generate_recommendations(self, config: BehaviorEvolutionConfig) -> None:
        """Generowanie zalecec ewolucji."""
        recommendations = []
        
        # Analiza success_rate
        if self.success_rate > config.success_threshold:
            recommendations.append({
                'factor': InfluenceFactor.SUCCESS_RATE.name,
                'action': 'REINFORCE',
                'description': f'Wzmacniaj zachowania zwiazane z ta strategia (success_rate: {self.success_rate:.2f})'
            })
        elif self.success_rate < config.failure_threshold:
            recommendations.append({
                'factor': InfluenceFactor.SUCCESS_RATE.name,
                'action': 'REDUCED',
                'description': f'Zmniejszaj uzycie tej strategii lub modyfikuj (success_rate: {self.success_rate:.2f})'
            })
        
        # Analiza confidence
        if self.confidence > config.confidence_threshold:
            recommendations.append({
                'factor': InfluenceFactor.CONFIDENCE.name,
                'action': 'INCREASE_TRUST',
                'description': f'Zwieksz zaufanie do tej strategii i podobnych (confidence: {self.confidence:.2f})'
            })
        else:
            recommendations.append({
                'factor': InfluenceFactor.CONFIDENCE.name,
                'action': 'VERIFY',
                'description': f'Zweryfikuj wynikami tej strategii (confidence: {self.confidence:.2f})'
            })
        
        # Analiza stability
        if self.stability > config.stability_threshold:
            recommendations.append({
                'factor': InfluenceFactor.STABILITY.name,
                'action': 'PREFER_STABLE',
                'description': f'Preferuj stabilne strategie (stability: {self.stability:.2f})'
            })
        
        # Analiza adaptability
        if self.adaptability > 0.7:
            recommendations.append({
                'factor': InfluenceFactor.ADAPTABILITY.name,
                'action': 'ENCOURAGE_FLEXIBILITY',
                'description': f'Zachecaj do elastycznych strategii (adaptability: {self.adaptability:.2f})'
            })
        
        self.evolution_recommendations = recommendations


class BehaviorEvolutionEngine:
    """
    Glowny silnik ewolucji zachowania.
    
    Odpowiedzialny za:
    - Analize wplywu strategii na zachowanie agenta
    - Generowanie zalecec ewolucji
    - Aktualizacje profilu zachowania agenta
    - Ewolucje preferencji strategii
    """
    
    def __init__(self, config: Optional[BehaviorEvolutionConfig] = None):
        self.config = config or BehaviorEvolutionConfig()
        self._lock = threading.RLock()
        
        # Profile agentow
        self._agent_profiles: Dict[str, AgentBehaviorProfile] = {}
        
        # Historia zdarzen ewolucji
        self._evolution_events: Dict[str, BehaviorEvolutionEvent] = {}
        self._evolution_history: List[str] = []
        
        # Cache analiz
        self._analysis_cache: Dict[str, StrategyInfluenceAnalysis] = {}
        
        # Hooki
        self._on_evolution_hooks: List[Callable[[AgentBehaviorProfile, BehaviorEvolutionEvent], None]] = []
        
        logger.info(f"BehaviorEvolutionEngine initialized with config: {self.config.to_dict()}")
    
    def on_evolution(self, callback: Callable[[AgentBehaviorProfile, BehaviorEvolutionEvent], None]) -> None:
        """Rejestracja hooka na ewolucje."""
        self._on_evolution_hooks.append(callback)
    
    def _trigger_evolution_hooks(self, profile: AgentBehaviorProfile, event: BehaviorEvolutionEvent) -> None:
        """Wywojq hookow na ewolucje."""
        for hook in self._on_evolution_hooks:
            try:
                hook(profile, event)
            except Exception as e:
                logger.error(f"Error in evolution hook: {e}")
    
    def get_or_create_profile(self, agent_id: str) -> AgentBehaviorProfile:
        """Pobranie lub utworzenie profilu agenta."""
        with self._lock:
            if agent_id not in self._agent_profiles:
                self._agent_profiles[agent_id] = AgentBehaviorProfile(agent_id=agent_id)
            return self._agent_profiles[agent_id]
    
    def analyze_strategy_influence(
        self,
        strategy: Strategy,
        result: Optional[StrategyResult] = None,
        evaluation: Optional[StrategyEvaluation] = None
    ) -> StrategyInfluenceAnalysis:
        """
        Analiza wplywu strategii na zachowanie.
        
        Args:
            strategy: Strategia do analizy
            result: Ostatni wynik strategii (opcjonalnie)
            evaluation: Ostatnia ocena strategii (opcjonalnie)
            
        Returns:
            StrategyInfluenceAnalysis: Analiza wplywu
        """
        with self._lock:
            cache_key = f"{strategy.strategy_id}:{result.result_id if result else 'no_result'}:{evaluation.evaluation_id if evaluation else 'no_eval'}"
            
            if cache_key in self._analysis_cache:
                return self._analysis_cache[cache_key]
            
            # Utworzenie analizy
            analysis = StrategyInfluenceAnalysis(
                strategy_id=strategy.strategy_id,
                agent_id=strategy.agent_owner,
                success_rate=strategy.success_rate,
                confidence=strategy.confidence,
                stability=strategy.reliability,  # Uzywamy reliability jako stability
                reliability=strategy.reliability,
                adaptability=strategy.parameters.adaptability if hasattr(strategy.parameters, 'adaptability') else 0.5,
                avg_score=strategy.avg_score,
                usage_count=strategy.usage_count
            )
            
            # Obliczenie wynikow wplywu
            analysis.calculate_influence_scores(self.config)
            
            # Cache
            self._analysis_cache[cache_key] = analysis
            
            logger.info(f"Strategy influence analyzed: {strategy.strategy_id}, overall_influence: {analysis.overall_influence:.3f}")
            
            return analysis
    
    def apply_behavior_evolution(
        self,
        strategy: Strategy,
        analysis: StrategyInfluenceAnalysis,
        result: Optional[StrategyResult] = None,
        evaluation: Optional[StrategyEvaluation] = None
    ) -> Tuple[AgentBehaviorProfile, BehaviorEvolutionEvent]:
        """
        Zastosowanie ewolucji zachowania na podstawie analizy.
        
        Args:
            strategy: Strategia
            analysis: Analiza wplywu
            result: Wynik strategii (opcjonalnie)
            evaluation: Ocena strategii (opcjonalnie)
            
        Returns:
            Tuple[AgentBehaviorProfile, BehaviorEvolutionEvent]: Zaktualizowany profil i zdarzenie
        """
        with self._lock:
            profile = self.get_or_create_profile(strategy.agent_owner)
            
            # Okreslenie typu ewolucji
            if analysis.overall_influence > 0.7:
                evolution_type = BehaviorEvolutionType.SUCCESS_PATTERN
            elif analysis.success_rate > 0.8:
                evolution_type = BehaviorEvolutionType.REPEATABILITY_FOCUS
            elif analysis.stability > 0.7:
                evolution_type = BehaviorEvolutionType.STABILITY_PREFERENCE
            elif analysis.confidence > 0.6:
                evolution_type = BehaviorEvolutionType.CONFIDENCE_EVOLUTION
            else:
                evolution_type = BehaviorEvolutionType.ADAPTABILITY
            
            # Okreslenie kierunku ewolucji
            direction = analysis.evolution_direction
            
            # Utworzenie zdarzenia ewolucji
            event = BehaviorEvolutionEvent(
                agent_id=strategy.agent_owner,
                strategy_id=strategy.strategy_id,
                evolution_type=evolution_type,
                direction=direction,
                success_rate=analysis.success_rate,
                confidence=analysis.confidence,
                stability=analysis.stability,
                risk_level=analysis.influence_scores.get(InfluenceFactor.RISK_LEVEL, 0.0),
                adaptability=analysis.adaptability,
                repeatability=analysis.influence_scores.get(InfluenceFactor.REPEATABILITY, 0.0),
                result_id=result.result_id if result else None,
                evaluation_id=evaluation.evaluation_id if evaluation else None,
                description=f"Ewolucja zachowania na podstawie strategii {strategy.name}"
            )
            
            # Aktualizacja profilu zachowania
            self._update_profile_from_analysis(profile, analysis, event, strategy)
            
            # Zapisanie zdarzenia
            self._evolution_events[event.event_id] = event
            self._evolution_history.append(event.event_id)
            profile.evolution_history.append(event.event_id)
            profile.evolution_events[event.event_id] = event
            profile.total_evolutions += 1
            profile.last_evolution = datetime.now()
            
            # Wywolanie hookow
            self._trigger_evolution_hooks(profile, event)
            
            logger.info(f"Behavior evolution applied for agent {strategy.agent_owner}, strategy {strategy.strategy_id}, type: {evolution_type.name}")
            
            return profile, event
    
    def _update_profile_from_analysis(
        self,
        profile: AgentBehaviorProfile,
        analysis: StrategyInfluenceAnalysis,
        event: BehaviorEvolutionEvent,
        strategy: Strategy
    ) -> None:
        """Aktualizacja profilu zachowania na podstawie analizy."""
        learning_rate = self.config.learning_rate
        
        # 1. Aktualizacja tolerancji ryzyka
        risk_tolerance_change = 0.0
        if analysis.success_rate > self.config.success_threshold:
            # ponad przecietny divisible - zwieksz tolerancje ryzyka
            risk_tolerance_change = learning_rate * (analysis.success_rate - self.config.success_threshold)
        elif analysis.success_rate < self.config.failure_threshold:
            # niski divisible - zmniejsz tolerancje ryzyka
            risk_tolerance_change = -learning_rate * (self.config.failure_threshold - analysis.success_rate)
        
        profile.risk_tolerance = max(0.0, min(1.0, profile.risk_tolerance + risk_tolerance_change))
        event.behavior_changes['risk_tolerance'] = risk_tolerance_change
        
        # 2. Aktualizacja preferencji pewnosci
        confidence_change = 0.0
        if analysis.confidence > self.config.confidence_threshold:
            # wysoka pewnosc - mozesz obnizyc preferencje pewnosci (akceptuj mniej pewne strategie)
            confidence_change = -learning_rate * (analysis.confidence - self.config.confidence_threshold)
        else:
            # niska pewnosc - zwieksz preferencje pewnosci
            confidence_change = learning_rate * (self.config.confidence_threshold - analysis.confidence)
        
        profile.confidence_preference = max(0.0, min(1.0, profile.confidence_preference + confidence_change))
        event.behavior_changes['confidence_preference'] = confidence_change
        
        # 3. Aktualizacja preferencji stabilnosci
        stability_change = 0.0
        if analysis.stability > self.config.stability_threshold:
            # wysoka stabilnosc - zwieksz preferencje stabilnosci
            stability_change = learning_rate * (analysis.stability - self.config.stability_threshold)
        
        profile.stability_preference = max(0.0, min(1.0, profile.stability_preference + stability_change))
        event.behavior_changes['stability_preference'] = stability_change
        
        # 4. Aktualizacja preferencji dostosowalnosci
        adaptability_change = 0.0
        if analysis.adaptability > 0.7:
            adaptability_change = learning_rate * (analysis.adaptability - 0.7)
        
        profile.adaptability_preference = max(0.0, min(1.0, profile.adaptability_preference + adaptability_change))
        event.behavior_changes['adaptability_preference'] = adaptability_change
        
        # 5. Aktualizacja preferencji typow strategii
        strategy_type = strategy.strategy_type
        preference_change = 0.0
        
        # Im lepsze wyniki, tym wieksza preferencja dla tego typu
        if analysis.overall_influence > 0.7:
            preference_change = learning_rate * (analysis.overall_influence - 0.7)
        elif analysis.overall_influence < 0.3:
            preference_change = -learning_rate * (0.3 - analysis.overall_influence)
        
        old_preference = profile.get_strategy_type_preference(strategy_type)
        profile.update_preference(strategy_type, preference_change)
        event.preference_changes['strategy_type'] = {
            'type': strategy_type.name,
            'old': old_preference,
            'new': profile.get_strategy_type_preference(strategy_type),
            'change': preference_change
        }
        
        # 6. Aktualizacja poziomu ryzyka
        risk_level = strategy.parameters.risk_level if hasattr(strategy.parameters, 'risk_level') else 0.5
        risk_preference_change = 0.0
        
        if analysis.success_rate > self.config.success_threshold:
            # وبما że strategia jest skuteczna, zwieksz preferencje dla tego poziomu ryzyka
            risk_preference_change = learning_rate * (analysis.success_rate - self.config.success_threshold)
        else:
            # niska skutecznosc - zmniejsz preferencje dla tego poziomu ryzyka
            risk_preference_change = -learning_rate * (self.config.success_threshold - analysis.success_rate)
        
        risk_category = 'LOW' if risk_level < 0.3 else ('MEDIUM' if risk_level < 0.7 else 'HIGH')
        old_risk_preference = profile.preferred_risk_levels.get(risk_category, 0.3)
        profile.update_risk_preference(risk_category, risk_preference_change)
        event.preference_changes['risk_level'] = {
            'category': risk_category,
            'old': old_risk_preference,
            'new': profile.preferred_risk_levels.get(risk_category, 0.3),
            'change': risk_preference_change
        }
        
        # 7. Aktualizacja predkosci podejmowania decyzji
        if analysis.success_rate > self.config.success_threshold and analysis.avg_score > 0.7:
            # Dobre wyniki - mozesz zdecydowac szybcej
            decision_speed_change = learning_rate * 0.1
            profile.decision_speed = max(0.0, min(1.0, profile.decision_speed + decision_speed_change))
            event.behavior_changes['decision_speed'] = decision_speed_change
        
        # 8. Aktualizacja glebowosci analizy
        if analysis.adaptability > 0.7:
            # Wysoka dostosowalnosc - mozesz analizowac plyciej
            analysis_depth_change = -1
            profile.analysis_depth = max(1, min(10, profile.analysis_depth + analysis_depth_change))
            event.behavior_changes['analysis_depth'] = analysis_depth_change
        
        # Aktualizacja timestamp
        profile.last_updated = datetime.now()
    
    def get_agent_preferences(self, agent_id: str) -> Dict[str, Any]:
        """Pobranie preferencji agenta."""
        profile = self.get_or_create_profile(agent_id)
        
        return {
            'agent_id': agent_id,
            'risk_tolerance': profile.risk_tolerance,
            'confidence_preference': profile.confidence_preference,
            'stability_preference': profile.stability_preference,
            'adaptability_preference': profile.adaptability_preference,
            'decision_speed': profile.decision_speed,
            'analysis_depth': profile.analysis_depth,
            'consider_alternatives': profile.consider_alternatives,
            'preferred_strategy_types': profile.preferred_strategy_types,
            'preferred_risk_levels': profile.preferred_risk_levels
        }
    
    def get_evolution_history(self, agent_id: str = None, limit: int = 100) -> List[BehaviorEvolutionEvent]:
        """Pobranie historii ewolucji."""
        with self._lock:
            if agent_id:
                profile = self._agent_profiles.get(agent_id)
                if profile:
                    event_ids = profile.evolution_history[-limit:]
                    return [profile.evolution_events[eid] for eid in event_ids if eid in profile.evolution_events]
            else:
                event_ids = self._evolution_history[-limit:]
                return [self._evolution_events[eid] for eid in event_ids if eid in self._evolution_events]
        
        return []
    
    def get_behavior_influence_on_strategy_selection(
        self,
        agent_id: str,
        strategies: List[Strategy]
    ) -> List[Dict[str, Any]]:
        """
        Obliczenie wplywu zachowania na wybór strategii.
        
        Args:
            agent_id: ID agenta
            strategies: Lista strategii do oceny
            
        Returns:
            List[Dict]: Lista strategii z dodatkowym scoringiem zachowania
        """
        profile = self.get_or_create_profile(agent_id)
        
        scored_strategies = []
        
        for strategy in strategies:
            # Podstawowy scoring
            base_score = strategy.ranking_score
            
            # Wpływ preferencji typu strategii
            type_preference = profile.get_strategy_type_preference(strategy.strategy_type)
            type_score = base_score * (1.0 + (type_preference - 0.5))  # -0.5 do 0.5
            
            # Wpływ preferencji poziomu ryzyka
            risk_level = strategy.parameters.risk_level if hasattr(strategy.parameters, 'risk_level') else 0.5
            risk_category = 'LOW' if risk_level < 0.3 else ('MEDIUM' if risk_level < 0.7 else 'HIGH')
            risk_preference = profile.preferred_risk_levels.get(risk_category, 0.3)
            risk_score = type_score * (1.0 + (risk_preference - 0.5))
            
            # Wpływ tolerancji ryzyka na formule
            if risk_level > profile.risk_tolerance:
                # Ryzyko wyższe niż tolerancja - penalizacja
                risk_penalty = (risk_level - profile.risk_tolerance) * 0.5
                risk_score *= (1.0 - risk_penalty)
            
            # Wpływ preferencji pewności
            if strategy.confidence >= profile.confidence_preference:
                confidence_bonus = 0.1
            else:
                confidence_penalty = (profile.confidence_preference - strategy.confidence) * 0.2
                confidence_bonus = -confidence_penalty
            
            final_score = risk_score * (1.0 + confidence_bonus)
            
            scored_strategies.append({
                'strategy_id': strategy.strategy_id,
                'base_score': base_score,
                'type_score': type_score,
                'risk_score': risk_score,
                'confidence_bonus': confidence_bonus,
                'final_score': final_score,
                'profile_match': {
                    'type_preference': type_preference,
                    'risk_preference': risk_preference,
                    'risk_tolerance_match': risk_level <= profile.risk_tolerance,
                    'confidence_match': strategy.confidence >= profile.confidence_preference
                }
            })
        
        return scored_strategies
    
    def clear_cache(self) -> None:
        """Wyczyszczenie cache."""
        with self._lock:
            self._analysis_cache.clear()
            logger.info("Behavior evolution analysis cache cleared")


# Singleton
_behavior_evolution_engine: Optional[BehaviorEvolutionEngine] = None
_behavior_evolution_engine_lock = threading.Lock()


def create_behavior_evolution_engine(config: Optional[BehaviorEvolutionConfig] = None) -> BehaviorEvolutionEngine:
    """Tworzenie nowej instancji Behavior Evolution Engine."""
    global _behavior_evolution_engine
    with _behavior_evolution_engine_lock:
        if _behavior_evolution_engine is None:
            _behavior_evolution_engine = BehaviorEvolutionEngine(config)
        return _behavior_evolution_engine


def get_behavior_evolution_engine() -> BehaviorEvolutionEngine:
    """Pobranie instancji singleton Behavior Evolution Engine."""
    global _behavior_evolution_engine
    if _behavior_evolution_engine is None:
        _behavior_evolution_engine = create_behavior_evolution_engine()
    return _behavior_evolution_engine


__all__ = [
    'BehaviorEvolutionConfig',
    'BehaviorEvolutionEvent',
    'BehaviorEvolutionType',
    'EvolutionDirection',
    'InfluenceFactor',
    'AgentBehaviorProfile',
    'StrategyInfluenceAnalysis',
    'BehaviorEvolutionEngine',
    'create_behavior_evolution_engine',
    'get_behavior_evolution_engine'
]
