# SSI V5 Agent Layer - Trust Manager
# ==================================================
#
# ETAP: 5.2.5 FAZA 1
# Data: 2026-08-04
#
# Odpowiedzialnosc:
# - Zarządzanie macierzą zaufania między agentami
# - System reputacji agentów
# - Ocena jakości decyzji
# - Historia zaufania
#
# Zgodnosc z: SSI_DOCUMENTATION/05_AGENT_SYSTEM.md (sekcja 6)

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Set, Tuple
from enum import Enum
from datetime import datetime
import uuid
import copy
import json
import os
from threading import RLock


class TrustLevel(Enum):
    """Poziomy zaufania"""
    DISTRUST = "distrust"        # Brak zaufania (< 0.3)
    LOW = "low"                  # Niskie zaufanie (0.3 - 0.5)
    NEUTRAL = "neutral"         # Neutralne (0.5 - 0.7)
    HIGH = "high"                # Wysokie zaufanie (0.7 - 0.9)
    FULL_TRUST = "full_trust"   # Pełne zaufanie (>= 0.9)


class ReputationLevel(Enum):
    """Poziomy reputacji"""
    POOR = "poor"               # Siedma (< 0.4)
    FAIR = "fair"               # Średnia (0.4 - 0.6)
    GOOD = "good"               # Dobra (0.6 - 0.8)
    EXCELLENT = "excellent"     # Wybitna (0.8 - 0.95)
    OUTSTANDING = "outstanding" # Wyjątkowa (>= 0.95)


class DecisionOutcome(Enum):
    """Wyniki decyzji dla oceny zaufania"""
    CORRECT = "correct"          # Trafna decyzja
    INCORRECT = "incorrect"     # Błędna decyzja
    PARTIAL = "partial"         # Częściowo trafna
    NEUTRAL = "neutral"        # Neutralna


# Wagi dla różnych typów decyzji
DECISION_WEIGHTS = {
    'high_confidence': 1.5,    # Decyzje z wysoką pewnością mają większą wagę
    'medium_confidence': 1.0,
    'low_confidence': 0.5,
    'default': 1.0
}


decision_quality_weights = {
    DecisionOutcome.CORRECT.value: 1.0,
    DecisionOutcome.PARTIAL.value: 0.5,
    DecisionOutcome.NEUTRAL.value: 0.0,
    DecisionOutcome.INCORRECT.value: -1.0
}


@dataclass
class TrustScore:
    """
    Wynik zaufania pomiędzy dwoma agentami.
    
    Zakres: 0.0 - 1.0
    """
    from_agent_id: str
    to_agent_id: str
    trust_score: float = 0.5  # Domyślnie neutralne zaufanie
    weight: float = 1.0       # Waga opinii (zależy od reputacji)
    interaction_count: int = 0
    correct_interactions: int = 0
    incorrect_interactions: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            'from_agent_id': self.from_agent_id,
            'to_agent_id': self.to_agent_id,
            'trust_score': self.trust_score,
            'weight': self.weight,
            'interaction_count': self.interaction_count,
            'correct_interactions': self.correct_interactions,
            'incorrect_interactions': self.incorrect_interactions,
            'last_updated': self.last_updated.isoformat(),
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrustScore':
        """Tworzenie TrustScore z słownika"""
        return cls(
            from_agent_id=data['from_agent_id'],
            to_agent_id=data['to_agent_id'],
            trust_score=data.get('trust_score', 0.5),
            weight=data.get('weight', 1.0),
            interaction_count=data.get('interaction_count', 0),
            correct_interactions=data.get('correct_interactions', 0),
            incorrect_interactions=data.get('incorrect_interactions', 0),
            last_updated=datetime.fromisoformat(data.get('last_updated', datetime.now().isoformat())),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat()))
        )
    
    def get_trust_level(self) -> TrustLevel:
        """Pobranie poziomu zaufania"""
        if self.trust_score >= 0.9:
            return TrustLevel.FULL_TRUST
        elif self.trust_score >= 0.7:
            return TrustLevel.HIGH
        elif self.trust_score >= 0.5:
            return TrustLevel.NEUTRAL
        elif self.trust_score >= 0.3:
            return TrustLevel.LOW
        else:
            return TrustLevel.DISTRUST
    
    def get_success_rate(self) -> float:
        """Obliczenie odsetka trafnych interakcji"""
        if self.interaction_count == 0:
            return 0.5  # Neutralne domyślnie
        return self.correct_interactions / self.interaction_count
    
    def update_from_feedback(self, outcome: DecisionOutcome, 
                           confidence_weight: float = 1.0) -> None:
        """
        Aktualizacja zaufania na podstawie wyniku decyzji.
        
        Args:
            outcome: Wynik decyzji (CORRECT, INCORRECT, PARTIAL, NEUTRAL)
            confidence_weight: Waga (domyślnie 1.0)
        """
        # Zaktualizuj liczniki interakcji
        self.interaction_count += 1
        self.last_updated = datetime.now()
        
        # Zaktualizuj liczniki na podstawie wyniku
        outcome_weight = decision_quality_weights.get(outcome.value, 0.0)
        weighted_outcome = outcome_weight * confidence_weight
        
        if outcome == DecisionOutcome.CORRECT:
            self.correct_interactions += 1
        elif outcome == DecisionOutcome.INCORRECT:
            self.incorrect_interactions += 1
        
        # Aktualizuj trust score ( Średnia ważona wyników)
        if self.interaction_count == 1:
            # Pierwsza interakcja - ustaw na podstawie wyniku
            self.trust_score = max(0.0, min(1.0, 0.5 + weighted_outcome * 0.3))
        else:
            # Średnia ważona z nowym wynikiem
            current_weight = (self.interaction_count - 1) / self.interaction_count
            new_weight = 1 / self.interaction_count
            
            # Nowy trust score
            new_trust = current_weight * self.trust_score + new_weight * (0.5 + weighted_outcome * 0.5)
            self.trust_score = max(0.0, min(1.0, new_trust))


@dataclass
class Reputation:
    """
    Reputacja pojedynczego agenta.
    
    Zakres: 0.0 - 1.0
    """
    agent_id: str
    agent_name: str
    reputation_score: float = 0.5
    total_decisions: int = 0
    correct_decisions: int = 0
    incorrect_decisions: int = 0
    collaboration_score: float = 0.5
    trustworthiness: float = 0.5
    last_updated: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'reputation_score': self.reputation_score,
            'total_decisions': self.total_decisions,
            'correct_decisions': self.correct_decisions,
            'incorrect_decisions': self.incorrect_decisions,
            'collaboration_score': self.collaboration_score,
            'trustworthiness': self.trustworthiness,
            'last_updated': self.last_updated.isoformat(),
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Reputation':
        """Tworzenie Reputation z słownika"""
        return cls(
            agent_id=data['agent_id'],
            agent_name=data.get('agent_name', 'Unknown'),
            reputation_score=data.get('reputation_score', 0.5),
            total_decisions=data.get('total_decisions', 0),
            correct_decisions=data.get('correct_decisions', 0),
            incorrect_decisions=data.get('incorrect_decisions', 0),
            collaboration_score=data.get('collaboration_score', 0.5),
            trustworthiness=data.get('trustworthiness', 0.5),
            last_updated=datetime.fromisoformat(data.get('last_updated', datetime.now().isoformat())),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat()))
        )
    
    def get_reputation_level(self) -> ReputationLevel:
        """Pobranie poziomu reputacji"""
        if self.reputation_score >= 0.95:
            return ReputationLevel.OUTSTANDING
        elif self.reputation_score >= 0.8:
            return ReputationLevel.EXCELLENT
        elif self.reputation_score >= 0.6:
            return ReputationLevel.GOOD
        elif self.reputation_score >= 0.4:
            return ReputationLevel.FAIR
        else:
            return ReputationLevel.POOR
    
    def get_decision_accuracy(self) -> float:
        """Obliczenie dokładności decyzji"""
        if self.total_decisions == 0:
            return 0.5  # Neutralne domyślnie
        return self.correct_decisions / self.total_decisions
    
    def update_from_decision(self, outcome: DecisionOutcome, 
                            confidence: float = 0.5,
                            collaboration: float = 0.5) -> None:
        """
        Aktualizacja reputacji na podstawie pojedynczej decyzji.
        
        Args:
            outcome: Wynik decyzji
            confidence: Pewność decyzji (0.0-1.0)
            collaboration: Stopień współpracy (0.0-1.0)
        """
        self.total_decisions += 1
        self.last_updated = datetime.now()
        
        # Zaktualizuj liczniki decyzji
        if outcome == DecisionOutcome.CORRECT:
            self.correct_decisions += 1
        elif outcome == DecisionOutcome.INCORRECT:
            self.incorrect_decisions += 1
        
        # Oblicz nową reputację (średnia ważona)
        old_weight = (self.total_decisions - 1) / self.total_decisions if self.total_decisions > 1 else 0.0
        new_weight = 1 / self.total_decisions
        
        # Punkty za decyzję
        decision_points = 0.0
        if outcome == DecisionOutcome.CORRECT:
            decision_points = 0.5 + confidence * 0.5
        elif outcome == DecisionOutcome.PARTIAL:
            decision_points = 0.25 + confidence * 0.25
        elif outcome == DecisionOutcome.INCORRECT:
            decision_points = -0.5 - (1 - confidence) * 0.5
        
        # Nowa reputacja
        if self.total_decisions == 1:
            self.reputation_score = max(0.0, min(1.0, 0.5 + decision_points * 0.5))
        else:
            self.reputation_score = old_weight * self.reputation_score + new_weight * (0.5 + decision_points * 0.5)
        
        # Zaktualizuj collaboration score
        old_collab_weight = (self.total_decisions - 1) / self.total_decisions if self.total_decisions > 1 else 0.0
        new_collab_weight = 1 / self.total_decisions
        self.collaboration_score = old_collab_weight * self.collaboration_score + new_collab_weight * collaboration
        
        # Trustworthiness - zależy od spójności decyzji
        if self.total_decisions >= 3:
            consistency = 1.0 - abs(self.get_decision_accuracy() - self.collaboration_score)
            self.trustworthiness = old_weight * self.trustworthiness + new_weight * consistency


@dataclass
class TrustUpdate:
    """Rekord aktualizacji zaufania"""
    update_id: str
    from_agent_id: str
    to_agent_id: str
    previous_trust: float
    new_trust: float
    outcome: DecisionOutcome
    confidence: float
    cycle_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            'update_id': self.update_id,
            'from_agent_id': self.from_agent_id,
            'to_agent_id': self.to_agent_id,
            'previous_trust': self.previous_trust,
            'new_trust': self.new_trust,
            'outcome': self.outcome.value,
            'confidence': self.confidence,
            'cycle_id': self.cycle_id,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class AgentTrustState:
    """
    Stan zaufania pojedynczego agenta.
    
    Zgodnosc z: SSI_DOCUMENTATION/05_AGENT_SYSTEM.md (sekcja 6)
    """
    agent_id: str
    agent_name: str
    
    # Macierz zaufania - zaufanie tego agenta do innych
    trust_in_agents: Dict[str, TrustScore] = field(default_factory=dict)
    
    # Reputacja ( oceniana przez system na podstawie wyników)
    reputation: Optional[Reputation] = None
    
    # Historia aktualizacji zaufania
    trust_history: List[TrustUpdate] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    _lock: RLock = field(default_factory=RLock, compare=False, repr=False)
    
    def __post_init__(self):
        """Inicjalizacja po utworzeniu"""
        if not hasattr(self, '_lock') or self._lock is None:
            self._lock = Lock()
        
        # Inicjalizacja reputacji
        if self.reputation is None:
            self.reputation = Reputation(
                agent_id=self.agent_id,
                agent_name=self.agent_name
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'trust_in_agents': {k: v.to_dict() for k, v in self.trust_in_agents.items()},
            'reputation': self.reputation.to_dict() if self.reputation else None,
            'trust_history': [t.to_dict() for t in self.trust_history],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def get_trust_score(self, other_agent_id: str) -> Optional[float]:
        """Pobranie poziomu zaufania do innego agenta"""
        trust_score = self.trust_in_agents.get(other_agent_id)
        if trust_score:
            return trust_score.trust_score
        return None
    
    def get_trust_level(self, other_agent_id: str) -> TrustLevel:
        """Pobranie poziomu zaufania do innego agenta"""
        trust_score = self.get_trust_score(other_agent_id)
        if trust_score is not None:
            if trust_score >= 0.9:
                return TrustLevel.FULL_TRUST
            elif trust_score >= 0.7:
                return TrustLevel.HIGH
            elif trust_score >= 0.5:
                return TrustLevel.NEUTRAL
            elif trust_score >= 0.3:
                return TrustLevel.LOW
            else:
                return TrustLevel.DISTRUST
        return TrustLevel.NEUTRAL  # Domyślnie neutralne
    
    def get_weight_for_agent(self, other_agent_id: str) -> float:
        """
        Pobranie wagi opinii innego agenta na podstawie zaufania.
        
        Args:
            other_agent_id: ID innego agenta
            
        Returns:
            float: Waga (0.0-1.0)
        """
        trust_score = self.get_trust_score(other_agent_id)
        if trust_score is not None:
            # Waga = trust_score * reputation_factor
            reputation_factor = self._get_reputation_factor(other_agent_id)
            return min(1.0, trust_score * reputation_factor)
        return 0.5  # Domyślnie neutralna waga
    
    def _get_reputation_factor(self, other_agent_id: str) -> float:
        """Pobranie czynnika reputacji innego agenta (0.5-1.5)"""
        # To uproszczona wersja - w przyszłości będzie używać reputacji systemowej
        trust_level = self.get_trust_level(other_agent_id)
        
        # Mapowanie poziomu zaufania na czynnik
        level_map = {
            TrustLevel.FULL_TRUST: 1.5,
            TrustLevel.HIGH: 1.3,
            TrustLevel.NEUTRAL: 1.0,
            TrustLevel.LOW: 0.7,
            TrustLevel.DISTRUST: 0.5
        }
        
        return level_map.get(trust_level, 1.0)
    
    def update_trust_from_feedback(self, other_agent_id: str, 
                                   outcome: DecisionOutcome,
                                   confidence: float = 0.5,
                                   cycle_id: Optional[str] = None) -> Optional[TrustUpdate]:
        """
        Aktualizacja zaufania do innego agenta na podstawie feedbacku.
        
        Args:
            other_agent_id: ID innego agenta
            outcome: Wynik interakcji/decyzji
            confidence: Pewność (0.0-1.0)
            cycle_id: ID cyklu
            
        Returns:
            TrustUpdate: Rekord aktualizacji
        """
        with self._lock:
            # Pobierz lub utwórz TrustScore
            if other_agent_id not in self.trust_in_agents:
                self.trust_in_agents[other_agent_id] = TrustScore(
                    from_agent_id=self.agent_id,
                    to_agent_id=other_agent_id
                )
            
            trust_score = self.trust_in_agents[other_agent_id]
            previous_trust = trust_score.trust_score
            
            # Zaktualizuj TrustScore
            confidence_weight = DECISION_WEIGHTS.get(
                'high_confidence' if confidence > 0.7 else 
                'medium_confidence' if confidence > 0.4 else 'low_confidence',
                DECISION_WEIGHTS['default']
            )
            trust_score.update_from_feedback(outcome, confidence_weight)
            
            # Utwórz rekord aktualizacji
            update_record = TrustUpdate(
                update_id=f"trust_update_{uuid.uuid4().hex[:8]}",
                from_agent_id=self.agent_id,
                to_agent_id=other_agent_id,
                previous_trust=previous_trust,
                new_trust=trust_score.trust_score,
                outcome=outcome,
                confidence=confidence,
                cycle_id=cycle_id,
                timestamp=datetime.now()
            )
            
            # Zapisz do historii
            self.trust_history.append(update_record)
            self.updated_at = datetime.now()
            
            return update_record
    
    def update_reputation_from_decision(self, outcome: DecisionOutcome,
                                       confidence: float = 0.5,
                                       collaboration: float = 0.5,
                                       cycle_id: Optional[str] = None) -> None:
        """
        Aktualizacja reputacji agenta na podstawie pojedynczej decyzji.
        
        Args:
            outcome: Wynik decyzji
            confidence: Pewność decyzji
            collaboration: Stopień współpracy
            cycle_id: ID cyklu
        """
        with self._lock:
            if self.reputation:
                self.reputation.update_from_decision(outcome, confidence, collaboration)
                self.updated_at = datetime.now()
    
    def get_average_trust(self) -> float:
        """Obliczenie średniego zaufania do innych agentów"""
        if not self.trust_in_agents:
            return 0.5  # Neutralne domyślnie
        
        total = sum(ts.trust_score for ts in self.trust_in_agents.values())
        return total / len(self.trust_in_agents)
    
    def get_trust_matrix_row(self) -> Dict[str, float]:
        """Pobranie wiersza macierzy zaufania (zaufanie tego agenta do innych)"""
        return {agent_id: ts.trust_score for agent_id, ts in self.trust_in_agents.items()}
    
    def get_trust_summary(self) -> Dict[str, Any]:
        """Pobranie podsumowania zaufania"""
        return {
            'average_trust': self.get_average_trust(),
            'trust_counts': {
                level.value: sum(1 for ts in self.trust_in_agents.values() 
                               if ts.get_trust_level() == level)
                for level in TrustLevel
            },
            'total_interactions': sum(ts.interaction_count for ts in self.trust_in_agents.values()),
            'reputation_score': self.reputation.reputation_score if self.reputation else 0.5,
            'reputation_level': self.reputation.get_reputation_level().value if self.reputation else 'neutral'
        }


class TrustManager:
    """
    Menadżer zaufania - zarządza macierzą zaufania i reputacją wszystkich agentów.
    
    Odpowiedzialność:
    - Zarządzanie macierzą zaufania pomiędzy agentami
    - Aktualizacja reputacji agentów
    - Zbieranie wyników agentów
    - Ocena jakości decyzji
    """
    
    def __init__(self, world_name: str = "SSI_V5_WORLD"):
        """
        Inicjalizacja TrustManager.
        
        Args:
            world_name: Nazwa świata
        """
        self.world_name = world_name
        
        # Stany zaufania wszystkich agentów
        self._agent_trust_states: Dict[str, AgentTrustState] = {}
        
        # Całościowa macierz zaufania (przetrzymywana także w postaci 2D)
        self.trust_matrix: Dict[str, Dict[str, float]] = {}
        
        # Reputacje wszystkich agentów
        self.reputations: Dict[str, Reputation] = {}
        
        # Historia wszystkich aktualizacji zaufania
        self.trust_update_history: List[TrustUpdate] = []
        
        # Blokady
        self._lock = RLock()
        
        # Mechanizm idempotencji - zapobiega podwójnej inicjalizacji
        self._all_trust_initialized = False
        self._initialized_agents: set = set()
        
        # Konfiguracja
        self._default_trust = 0.5
        self._trust_decay_factor = 0.99  # Stopniowe obniżanie zaufania bez interakcji
    
    def initialize_agent_trust(self, agent_id: str, agent_name: str, 
                              known_agents: Optional[List[str]] = None) -> AgentTrustState:
        """
        Inicjalizacja stanu zaufania dla nowego agenta.
        Mechanizm idempotencji: jeśli agent został już zainicjalizowany, zwraca istniejacy stan.
        
        Args:
            agent_id: ID agenta
            agent_name: Nazwa agenta
            known_agents: Lista znanych agentów (opcjonalna)
            
        Returns:
            AgentTrustState
        """
        with self._lock:
            # Mechanizm idempotencji: jeśli agent już istnieje, zwróć istniejacy stan
            if agent_id in self._agent_trust_states:
                return self._agent_trust_states[agent_id]
            
            # Zaznacz agenta jako zainicjalizowanego
            self._initialized_agents.add(agent_id)
            
            # Utwórz nowy stan
            state = AgentTrustState(
                agent_id=agent_id,
                agent_name=agent_name
            )
            
            # Inicjalizuj zaufanie do znanych agentów
            if known_agents:
                for other_agent_id in known_agents:
                    if other_agent_id != agent_id and other_agent_id not in state.trust_in_agents:
                        state.trust_in_agents[other_agent_id] = TrustScore(
                            from_agent_id=agent_id,
                            to_agent_id=other_agent_id,
                            trust_score=self._default_trust
                        )
            
            self._agent_trust_states[agent_id] = state
            self._update_trust_matrix()
            
            return state
    
    def get_agent_trust_state(self, agent_id: str) -> Optional[AgentTrustState]:
        """Pobranie stanu zaufania agenta"""
        with self._lock:
            return self._agent_trust_states.get(agent_id)
    
    def get_trust_score(self, from_agent_id: str, to_agent_id: str) -> Optional[float]:
        """Pobranie poziomu zaufania pomiędzy dwoma agentami"""
        state = self.get_agent_trust_state(from_agent_id)
        if state:
            return state.get_trust_score(to_agent_id)
        return None
    
    def get_weight_for_agent(self, evaluator_agent_id: str, target_agent_id: str) -> float:
        """
        Pobranie wagi opinii jednego agenta względem drugiego.
        
        Args:
            evaluator_agent_id: ID agenta, który ocenia
            target_agent_id: ID agenta, którego opinia jest ważona
            
        Returns:
            float: Waga (0.0-1.0)
        """
        state = self.get_agent_trust_state(evaluator_agent_id)
        if state:
            return state.get_weight_for_agent(target_agent_id)
        return 0.5  # Domyślnie neutralna waga
    
    def update_trust_from_feedback(self, from_agent_id: str, to_agent_id: str,
                                   outcome: DecisionOutcome,
                                   confidence: float = 0.5,
                                   cycle_id: Optional[str] = None) -> Optional[TrustUpdate]:
        """
        Aktualizacja zaufania na podstawie feedbacku.
        
        Args:
            from_agent_id: ID agenta, który ocenia
            to_agent_id: ID agenta, którego zaufanie jest aktualizowane
            outcome: Wynik interakcji/decyzji
            confidence: Pewność (0.0-1.0)
            cycle_id: ID cyklu
            
        Returns:
            TrustUpdate: Rekord aktualizacji
        """
        with self._lock:
            state = self.get_agent_trust_state(from_agent_id)
            if state:
                update = state.update_trust_from_feedback(
                    to_agent_id, outcome, confidence, cycle_id
                )
                
                if update:
                    # Zapisz do globalnej historii
                    self.trust_update_history.append(update)
                    self._update_trust_matrix()
                    
                return update
            
        return None
    
    def update_reputation_from_decision(self, agent_id: str, outcome: DecisionOutcome,
                                       confidence: float = 0.5,
                                       collaboration: float = 0.5,
                                       cycle_id: Optional[str] = None) -> None:
        """
        Aktualizacja reputacji agenta na podstawie pojedynczej decyzji.
        
        Args:
            agent_id: ID agenta
            outcome: Wynik decyzji
            confidence: Pewność decyzji
            collaboration: Stopień współpracy
            cycle_id: ID cyklu
        """
        with self._lock:
            state = self.get_agent_trust_state(agent_id)
            if state:
                state.update_reputation_from_decision(outcome, confidence, collaboration, cycle_id)
                self.reputations[agent_id] = copy.deepcopy(state.reputation)
    
    def get_full_trust_matrix(self) -> Dict[str, Dict[str, float]]:
        """Pobranie pełnej macierzy zaufania"""
        with self._lock:
            return copy.deepcopy(self.trust_matrix)
    
    def _update_trust_matrix(self) -> None:
        """Aktualizacja macierzy zaufania na podstawie stanów agentów"""
        with self._lock:
            self.trust_matrix.clear()
            
            for agent_id, state in self._agent_trust_states.items():
                self.trust_matrix[agent_id] = state.get_trust_matrix_row()
    
    def initialize_all_trust(self, agent_ids: List[str], agent_names: Dict[str, str]) -> None:
        """
        Inicjalizacja zaufania pomiędzy wszystkimi agentami.
        Mechanizm idempotencji: jeśli wszystkie agenci są już zainicjalizowani, pomija inicjalizację.
        
        Args:
            agent_ids: Lista ID agentów
            agent_names: Słownik {agent_id: agent_name}
        """
        # Mechanizm idempotencji: sprawdź, czy wszyscy agenci są już zainicjalizowani
        with self._lock:
            all_initialized = all(agent_id in self._agent_trust_states for agent_id in agent_ids)
            
            if all_initialized and self._all_trust_initialized:
                # Wszyscy agenci są już zainicjalizowani, pomiń
                return
        
        # Inicjalizuj stany zaufania dla wszystkich agentów (BEZ zagnieżdżonej blokady!)
        # initialize_agent_trust używa swojej własnej blokady
        for agent_id in agent_ids:
            if agent_id not in self._agent_trust_states:
                agent_name = agent_names.get(agent_id, f"Agent_{agent_id}")
                self.initialize_agent_trust(agent_id, agent_name, agent_ids)
        
        # Zaznacz, że wszyscy agenci zostali zainicjalizowani
        with self._lock:
            self._all_trust_initialized = True
    
    def get_agent_reputation(self, agent_id: str) -> Optional[Reputation]:
        """Pobranie reputacji agenta"""
        with self._lock:
            state = self.get_agent_trust_state(agent_id)
            if state and state.reputation:
                return copy.deepcopy(state.reputation)
            return None
    
    def get_reputation_ranking(self) -> List[Tuple[str, float]]:
        """
        Pobranie rankingu agentów według reputacji.
        
        Returns:
            Lista tupli (agent_id, reputation_score) posortowana malejąco
        """
        with self._lock:
            reputation_scores = []
            for agent_id, state in self._agent_trust_states.items():
                if state.reputation:
                    reputation_scores.append((agent_id, state.reputation.reputation_score))
            
            # Sortuj malejąco według reputacji
            reputation_scores.sort(key=lambda x: x[1], reverse=True)
            return reputation_scores
    
    def get_trust_summary(self) -> Dict[str, Any]:
        """Pobranie podsumowania zaufania i reputacji"""
        with self._lock:
            total_interactions = sum(
                sum(ts.interaction_count for ts in state.trust_in_agents.values())
                for state in self._agent_trust_states.values()
            )
            
            avg_trust = sum(
                state.get_average_trust()
                for state in self._agent_trust_states.values()
            ) / len(self._agent_trust_states) if self._agent_trust_states else 0.5
            
            avg_reputation = sum(
                state.reputation.reputation_score if state.reputation else 0.5
                for state in self._agent_trust_states.values()
            ) / len(self._agent_trust_states) if self._agent_trust_states else 0.5
            
            return {
                'total_agents': len(self._agent_trust_states),
                'total_interactions': total_interactions,
                'average_trust_score': avg_trust,
                'average_reputation_score': avg_reputation,
                'trust_distribution': self._get_trust_distribution(),
                'reputation_distribution': self._get_reputation_distribution(),
                'total Updates': len(self.trust_update_history)
            }
    
    def _get_trust_distribution(self) -> Dict[str, int]:
        """Obliczenie rozkładu poziomów zaufania"""
        distribution = {level.value: 0 for level in TrustLevel}
        
        for state in self._agent_trust_states.values():
            for trust_score in state.trust_in_agents.values():
                level = trust_score.get_trust_level()
                distribution[level.value] += 1
        
        return distribution
    
    def _get_reputation_distribution(self) -> Dict[str, int]:
        """Obliczenie rozkładu poziomów reputacji"""
        distribution = {level.value: 0 for level in ReputationLevel}
        
        for state in self._agent_trust_states.values():
            if state.reputation:
                level = state.reputation.get_reputation_level()
                distribution[level.value] += 1
        
        return distribution
    
    def save_trust_state(self, file_path: Optional[str] = None) -> bool:
        """
        Zapis stanu zaufania do pliku JSON.
        
        Args:
            file_path: Ścieżka do pliku (opcjonalna)
            
        Returns:
            bool: Czy zapis się powiódł
        """
        try:
            if file_path is None:
                from ..core.config import PathConfig
                memory_dir = PathConfig.MEMORY_DIR
                os.makedirs(memory_dir, exist_ok=True)
                file_path = os.path.join(memory_dir, f"{self.world_name}_trust_state.json")
            
            data = {
                'world_name': self.world_name,
                'trust_matrix': self.trust_matrix,
                'reputations': {k: v.to_dict() for k, v in self.reputations.items()},
                'trust_update_history': [t.to_dict() for t in self.trust_update_history],
                'saved_at': datetime.now().isoformat()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"[TRUST] Error saving trust state: {e}")
            return False
    
    def load_trust_state(self, file_path: Optional[str] = None) -> bool:
        """
        Wczytanie stanu zaufania z pliku JSON.
        
        Args:
            file_path: Ścieżka do pliku (opcjonalna)
            
        Returns:
            bool: Czy wczytanie się powiodło
        """
        try:
            if file_path is None:
                from ..core.config import PathConfig
                memory_dir = PathConfig.MEMORY_DIR
                file_path = os.path.join(memory_dir, f"{self.world_name}_trust_state.json")
            
            if not os.path.exists(file_path):
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Wczytanie macierzy zaufania
            self.trust_matrix = data.get('trust_matrix', {})
            
            # Wczytanie reputacji
            self.reputations.clear()
            for agent_id, rep_data in data.get('reputations', {}).items():
                self.reputations[agent_id] = Reputation.from_dict(rep_data)
            
            # Wczytanie historii aktualizacji
            self.trust_update_history.clear()
            for update_data in data.get('trust_update_history', []):
                update = TrustUpdate(
                    update_id=update_data['update_id'],
                    from_agent_id=update_data['from_agent_id'],
                    to_agent_id=update_data['to_agent_id'],
                    previous_trust=update_data['previous_trust'],
                    new_trust=update_data['new_trust'],
                    outcome=DecisionOutcome(update_data['outcome']),
                    confidence=update_data['confidence'],
                    cycle_id=update_data.get('cycle_id'),
                    timestamp=datetime.fromisoformat(update_data['timestamp'])
                )
                self.trust_update_history.append(update)
            
            # Odbudowa stanów agentów na podstawie załadowanych danych
            self._rebuild_agent_trust_states()
            
            return True
            
        except Exception as e:
            print(f"[TRUST] Error loading trust state: {e}")
            return False
    
    def _rebuild_agent_trust_states(self) -> None:
        """Odbudowa stanów zaufania agentów na podstawie załadowanych danych"""
        # To uproszczona wersja - pełna odbudowa będzie w późniejszych fazach
        pass


# Eksportowane elementy
__all__ = [
    'TrustLevel',
    'ReputationLevel',
    'DecisionOutcome',
    'DECISION_WEIGHTS',
    'decision_quality_weights',
    'TrustScore',
    'Reputation',
    'TrustUpdate',
    'AgentTrustState',
    'TrustManager'
]
