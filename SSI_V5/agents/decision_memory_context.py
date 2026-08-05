# SSI V5 - Decision Memory Context
# ==================================================
#
# ETAP: 0 KROK 2 - Decision Memory Context
# Data: 2026-08-04
# 
# Odpowiedzialnosc:
# - Rozszerzenie DecisionContext o kontekst pamieci historycznej
# - Dostarczenie historycznych danych dla DecisionEngine
# - Integracja z MemoryIntegrationLayer
#
# ZASADY:
# 1. NIE modyfikowac istniejacego DecisionContext
# 2. TYLKO dodawac nowa warstwe abstrakcji
# 3. NIE zmieniac Decision Engine w tym kroku
# 4. Wszystkie operacje thread-safe
#
# Uzycie:
#   from SSI_V5.agents.decision_memory_context import DecisionMemoryContextBuilder
#   
#   # Inicjalizacja
#   memory_context_builder = DecisionMemoryContextBuilder(memory_integration_layer)
#   
#   # Budowanie kontekstu pamieci
#   memory_context = memory_context_builder.build_memory_context(
#       agent_id=agent.agent_id,
#       current_situation=contract.to_dict()
#   )
#   
#   # Rozszerzenie istniejącego DecisionContext
#   enhanced_context = memory_context_builder.enhance_decision_context(
#       original_context=decision_engine.current_context,
#       memory_context=memory_context
#   )
#

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import threading
import logging
import copy

# Konfiguracja logowania
logger = logging.getLogger(__name__)


class DecisionMemoryContextError(Exception):
    """Wyjatki dla kontekstu pamieci decyzji"""
    pass


@dataclass
class MemoryContext:
    """
    Kontener dla kontekstu pamieci historycznej.
    
    Zawiera historyczne dane, ktore DecisionEngine moze wykorzystac
    do podejmowania lepszych decyzji.
    
    Atrybuty:
        historical_memories: Lista pamięci historycznych powiązanych z aktualną sytuacją
        similar_cases: Podobne случаи z przeszłości (z semantycznego wyszukiwania)
        previous_decisions: Poprzednie decyzje agenta w podobnych sytuacjach
        agent_experience: Doświadczenie agenta zebrane z poprzednich cykli
        relevant_knowledge: Kluczowa wiedza wyekstrahowana z pamięci
        memory_stats: Statystyki kontekstu pamięci
    """
    
    # Listy z historycznymi danymi
    historical_memories: List[Dict[str, Any]] = field(default_factory=list)
    similar_cases: List[Dict[str, Any]] = field(default_factory=list)
    previous_decisions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Agregowana wiedza
    agent_experience: Dict[str, Any] = field(default_factory=dict)
    relevant_knowledge: Dict[str, Any] = field(default_factory=dict)
    
    # Metadane i statystyki
    memory_stats: Dict[str, Any] = field(default_factory=dict)
    retrieval_timestamp: datetime = field(default_factory=datetime.now)
    source: str = "memory_integration_layer"
    
    def __post_init__(self):
        """Inicjalizacja po utworzeniu"""
        # Zapewnienie ze wszystkie listy sa zainicjowane
        if self.historical_memories is None:
            self.historical_memories = []
        if self.similar_cases is None:
            self.similar_cases = []
        if self.previous_decisions is None:
            self.previous_decisions = []
        if self.agent_experience is None:
            self.agent_experience = {}
        if self.relevant_knowledge is None:
            self.relevant_knowledge = {}
        if self.memory_stats is None:
            self.memory_stats = {}
        
        # Aktualizacja statystyk
        self._update_stats()
    
    def _update_stats(self) -> None:
        """Aktualizacja statystyk kontekstu"""
        self.memory_stats = {
            'historical_memories_count': len(self.historical_memories),
            'similar_cases_count': len(self.similar_cases),
            'previous_decisions_count': len(self.previous_decisions),
            'agent_experience_keys': list(self.agent_experience.keys()) if self.agent_experience else [],
            'relevant_knowledge_keys': list(self.relevant_knowledge.keys()) if self.relevant_knowledge else [],
            'total_context_items': len(self.historical_memories) + len(self.similar_cases) + len(self.previous_decisions)
        }
    
    def add_historical_memory(self, memory: Dict[str, Any]) -> None:
        """Dodanie pamięci historycznej"""
        if memory and isinstance(memory, dict):
            self.historical_memories.append(copy.deepcopy(memory))
            self._update_stats()
    
    def add_similar_case(self, case: Dict[str, Any]) -> None:
        """Dodanie podobnego przypadku"""
        if case and isinstance(case, dict):
            self.similar_cases.append(copy.deepcopy(case))
            self._update_stats()
    
    def add_previous_decision(self, decision: Dict[str, Any]) -> None:
        """Dodanie poprzedniej decyzji"""
        if decision and isinstance(decision, dict):
            self.previous_decisions.append(copy.deepcopy(decision))
            self._update_stats()
    
    def add_agent_experience(self, key: str, value: Any) -> None:
        """Dodanie doświadczenia agenta"""
        if key and isinstance(key, str):
            self.agent_experience[key] = copy.deepcopy(value)
            self._update_stats()
    
    def add_relevant_knowledge(self, key: str, value: Any) -> None:
        """Dodanie istotnej wiedzy"""
        if key and isinstance(key, str):
            self.relevant_knowledge[key] = copy.deepcopy(value)
            self._update_stats()
    
    @classmethod
    def from_memory_retrieval_result(
        cls,
        retrieval_result: Dict[str, Any],
        agent_id: Optional[str] = None
    ) -> 'MemoryContext':
        """
        Tworzenie MemoryContext z wyniku retrieve_context() z MemoryIntegrationLayer.
        
        Args:
            retrieval_result: Wynik z memory_layer.retrieve_context()
            agent_id: Opcjonalny ID agenta do filtrowania
            
        Returns:
            MemoryContext gotowy do uzycia
        """
        if not retrieval_result or not isinstance(retrieval_result, dict):
            return cls()
        
        # Utworzenie nowego kontekstu
        memory_context = cls()
        
        # Pobranie danych z wyniku
        memory_context_data = retrieval_result.get('memory_context', {})
        related_memories = retrieval_result.get('related_memories', [])
        
        # Dodanie pamięci powiązanych jako historical_memories
        for memory in related_memories:
            if isinstance(memory, dict):
                memory_context.add_historical_memory(memory)
        
        # Dodanie informacji z memory_context
        if isinstance(memory_context_data, dict):
            # Szukanie poprzednich decyzji w pamięci
            if 'relevant_memories' in memory_context_data:
                for mem in memory_context_data.get('relevant_memories', []):
                    if isinstance(mem, dict) and mem.get('type') == 'decision':
                        memory_context.add_previous_decision(mem)
                    elif isinstance(mem, dict):
                        memory_context.add_similar_case(mem)
            
            # Dodanie statystyk
            memory_context.memory_stats['source'] = memory_context_data.get('agent_id', 'unknown')
            memory_context.memory_stats['memory_count'] = memory_context_data.get('memory_count', 0)
        
        # Ustawienie źródła
        memory_context.source = f"memory_retrieval_{retrieval_result.get('agent_id', 'unknown')}"
        
        return memory_context
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            'historical_memories': copy.deepcopy(self.historical_memories),
            'similar_cases': copy.deepcopy(self.similar_cases),
            'previous_decisions': copy.deepcopy(self.previous_decisions),
            'agent_experience': copy.deepcopy(self.agent_experience),
            'relevant_knowledge': copy.deepcopy(self.relevant_knowledge),
            'memory_stats': copy.deepcopy(self.memory_stats),
            'retrieval_timestamp': self.retrieval_timestamp.isoformat(),
            'source': self.source
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Pobranie podsumowania kontekstu"""
        return {
            'status': 'success',
            'memory_context_type': self.__class__.__name__,
            'stats': copy.deepcopy(self.memory_stats),
            'has_historical_data': len(self.historical_memories) > 0,
            'has_similar_cases': len(self.similar_cases) > 0,
            'has_previous_decisions': len(self.previous_decisions) > 0,
            'has_agent_experience': bool(self.agent_experience),
            'has_relevant_knowledge': bool(self.relevant_knowledge),
            'retrieval_timestamp': self.retrieval_timestamp.isoformat()
        }


@dataclass
class EnhancedDecisionContext:
    """
    Rozszerzony DecisionContext z dodatkowym kontekstem pamięci.
    
    Łączy oryginalny DecisionContext z MemoryContext,
    aby DecisionEngine miał dostęp do zarówno bieżących danych jak i historii.
    
    Użycie:
        # Tworzenie na podstawie istniejących danych
        original_context = DecisionContext(
            world_data=contract.world_data,
            model_info=contract.model_evaluation,
            weights=contract.current_weights,
            recommendations=contract.recommendations
        )
        
        memory_context = MemoryContext.from_memory_retrieval_result(retrieval_result)
        
        enhanced_context = EnhancedDecisionContext(
            original_context=original_context,
            memory_context=memory_context
        )
    """
    
    # Oryginalny kontekst (biezący)
    original_context: Any = None
    
    # Kontekst pamięci (historyczny)
    memory_context: MemoryContext = field(default_factory=MemoryContext)
    
    # Połączony kontekst (automatycznie budowany)
    combined_context: Dict[str, Any] = field(default_factory=dict)
    
    # Flagi dostępności danych
    has_original_context: bool = False
    has_memory_context: bool = False
    
    def __post_init__(self):
        """Inicjalizacja po utworzeniu"""
        self.has_original_context = self.original_context is not None
        self.has_memory_context = self.memory_context is not None
        
        # Budowa połączonego kontekstu
        self._build_combined_context()
    
    def _build_combined_context(self) -> None:
        """Budowa połączonego kontekstu z oryginalnego i pamięci"""
        self.combined_context = {}
        
        # Dodanie oryginalnych danych
        if self.has_original_context and hasattr(self.original_context, 'world_data'):
            self.combined_context['world_data'] = copy.deepcopy(getattr(self.original_context, 'world_data', {}))
            self.combined_context['model_info'] = copy.deepcopy(getattr(self.original_context, 'model_info', {}))
            self.combined_context['weights'] = copy.deepcopy(getattr(self.original_context, 'weights', {}))
            self.combined_context['recommendations'] = copy.deepcopy(getattr(self.original_context, 'recommendations', []))
            self.combined_context['risk_factors'] = copy.deepcopy(getattr(self.original_context, 'risk_factors', {}))
            self.combined_context['constraints'] = copy.deepcopy(getattr(self.original_context, 'constraints', {}))
        
        # Dodanie kontekstu pamięci
        if self.has_memory_context:
            self.combined_context['memory_context'] = self.memory_context.to_dict()
            
            # Dodanie kluczowych informacji na pierwszym poziomie
            if self.memory_context.previous_decisions:
                self.combined_context['previous_decisions'] = copy.deepcopy(self.memory_context.previous_decisions)
            
            if self.memory_context.similar_cases:
                self.combined_context['similar_cases'] = copy.deepcopy(self.memory_context.similar_cases)
            
            if self.memory_context.agent_experience:
                self.combined_context['agent_experience'] = copy.deepcopy(self.memory_context.agent_experience)
            
            if self.memory_context.relevant_knowledge:
                self.combined_context['relevant_knowledge'] = copy.deepcopy(self.memory_context.relevant_knowledge)
    
    def add_memory_context(self, memory_context: MemoryContext) -> None:
        """Dodanie kontekstu pamięci do istniejących danych"""
        self.memory_context = memory_context
        self.has_memory_context = True
        self._build_combined_context()
    
    def get_combined_context(self) -> Dict[str, Any]:
        """Pobranie połączonego kontekstu"""
        return copy.deepcopy(self.combined_context)
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Pobranie podsumowania kontekstu pamięci"""
        if self.has_memory_context:
            return self.memory_context.get_summary()
        return {'status': 'no_memory_context', 'message': 'Memory context not available'}
    
    def has_historical_data(self) -> bool:
        """Czy są dostępne dane historyczne?"""
        return self.has_memory_context and len(self.memory_context.historical_memories) > 0
    
    def has_previous_decisions(self) -> bool:
        """Czy są dostępne poprzednie decyzje?"""
        return self.has_memory_context and len(self.memory_context.previous_decisions) > 0
    
    def has_similar_cases(self) -> bool:
        """Czy są dostępne podobne przypadki?"""
        return self.has_memory_context and len(self.memory_context.similar_cases) > 0
    
    # ============================================================================
    # DELEGACJA DO ORYGINALNEGO CONTEXT
    # ============================================================================
    
    @property
    def world_data(self) -> Dict[str, Any]:
        """Delegacja do world_data"""
        if self.has_original_context and hasattr(self.original_context, 'world_data'):
            return self.original_context.world_data
        return self.combined_context.get('world_data', {})
    
    @property
    def model_info(self) -> Dict[str, Any]:
        """Delegacja do model_info"""
        if self.has_original_context and hasattr(self.original_context, 'model_info'):
            return self.original_context.model_info
        return self.combined_context.get('model_info', {})
    
    @property
    def weights(self) -> Dict[str, Any]:
        """Delegacja do weights"""
        if self.has_original_context and hasattr(self.original_context, 'weights'):
            return self.original_context.weights
        return self.combined_context.get('weights', {})
    
    @property
    def recommendations(self) -> List[Dict[str, Any]]:
        """Delegacja do recommendations"""
        if self.has_original_context and hasattr(self.original_context, 'recommendations'):
            return self.original_context.recommendations
        return self.combined_context.get('recommendations', [])
    
    @property
    def risk_factors(self) -> Dict[str, Any]:
        """Delegacja do risk_factors"""
        if self.has_original_context and hasattr(self.original_context, 'risk_factors'):
            return self.original_context.risk_factors
        return self.combined_context.get('risk_factors', {})
    
    @property
    def constraints(self) -> Dict[str, Any]:
        """Delegacja do constraints"""
        if self.has_original_context and hasattr(self.original_context, 'constraints'):
            return self.original_context.constraints
        return self.combined_context.get('constraints', {})
    
    def calculate_confidence(self) -> float:
        """Delegacja do calculate_confidence"""
        if self.has_original_context and hasattr(self.original_context, 'calculate_confidence'):
            return self.original_context.calculate_confidence()
        return 0.5


class DecisionMemoryContextBuilder:
    """
    Builder kontekstu pamięci dla DecisionEngine.
    
    Odpowiedzialność:
    - Budowanie MemoryContext na podstawie aktualnej sytuacji
    - Rozszerzanie DecisionContext o kontekst pamięci
    - Integracja z MemoryIntegrationLayer
    
    Użycie:
        # Inicjalizacja (w AgentRuntime lub DecisionEngine)
        from SSI_V5.memory.memory_integration import MemoryIntegrationLayer
        from SSI_V5.agents.decision_memory_context import DecisionMemoryContextBuilder
        
        memory_layer = MemoryIntegrationLayer(collective_manager)
        context_builder = DecisionMemoryContextBuilder(memory_layer)
        
        # Budowanie kontekstu pamięci dla agenta
        memory_context = context_builder.build_memory_context(
            agent_id="agent_01",
            current_situation=contract.to_dict()
        )
        
        # Rozszerzenie istniejącego DecisionContext
        enhanced_context = context_builder.enhance_decision_context(
            original_context=decision_engine.current_context,
            memory_context=memory_context
        )
    """
    
    def __init__(self, memory_integration_layer: Any = None):
        """
        Inicjalizacja buildera.
        
        Args:
            memory_integration_layer: Instancja MemoryIntegrationLayer (opcjonalna)
        """
        self._memory_layer = memory_integration_layer
        self._lock = threading.RLock()
        
        # Statystyki
        self._stats = {
            'context_builds': 0,
            'enhancements': 0,
            'success_count': 0,
            'error_count': 0
        }
        
        logger.info("DecisionMemoryContextBuilder initialized")
    
    @property
    def memory_layer(self) -> Any:
        """Zwraca warstwę integracji pamięci"""
        return self._memory_layer
    
    @memory_layer.setter
    def memory_layer(self, layer: Any) -> None:
        """Ustawia warstwę integracji pamięci"""
        self._memory_layer = layer
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Zwraca statystyki operacji"""
        with self._lock:
            return copy.deepcopy(self._stats)
    
    def set_memory_layer(self, memory_layer: Any) -> None:
        """Ustawienie warstwy integracji pamięci"""
        self._memory_layer = memory_layer
        logger.info("MemoryIntegrationLayer set for DecisionMemoryContextBuilder")
    
    def build_memory_context(
        self,
        agent_id: str,
        current_situation: Dict[str, Any],
        top_k: int = 5,
        min_similarity: float = 0.6,
        include_previous_decisions: bool = True,
        include_similar_cases: bool = True,
        include_agent_experience: bool = True
    ) -> MemoryContext:
        """
        Buduje MemoryContext na podstawie aktualnej sytuacji.
        
        Ta metoda pobiera dane z pamięci kolektywnej i organizuje je
        w strukturze MemoryContext, która może być użyta przez DecisionEngine.
        
        Args:
            agent_id: ID agenta
            current_situation: Bieżąca sytuacja (słownik z danymi)
            top_k: Maksymalna liczba pamięci do pobrania
            min_similarity: Minimalne podobieństwo
            include_previous_decisions: Czy włączać poprzednie decyzje
            include_similar_cases: Czy włączać podobne przypadki
            include_agent_experience: Czy włączać doświadczenie agenta
            
        Returns:
            MemoryContext gotowy do użycia
        """
        with self._lock:
            self._stats['context_builds'] += 1
            
            try:
                # Walidacja inputu
                if not agent_id or not isinstance(agent_id, str):
                    raise DecisionMemoryContextError("Invalid agent_id")
                
                if not current_situation or not isinstance(current_situation, dict):
                    raise DecisionMemoryContextError("Invalid current_situation")
                
                if self._memory_layer is None:
                    raise DecisionMemoryContextError("MemoryIntegrationLayer not set")
                
                start_time = datetime.now()
                
                # Pobranie kontekstu z warstwy integracji
                retrieval_result = self._memory_layer.retrieve_context(
                    agent_id=agent_id,
                    current_situation=current_situation,
                    top_k=top_k,
                    min_similarity=min_similarity
                )
                
                if retrieval_result.get('status') != 'success':
                    logger.warning(f"Failed to retrieve memory context: {retrieval_result.get('error', 'Unknown error')}")
                    return MemoryContext()
                
                # Konwersja na MemoryContext
                memory_context = MemoryContext.from_memory_retrieval_result(retrieval_result)
                
                # Opcjonalne filtrowanie danych
                if not include_previous_decisions:
                    memory_context.previous_decisions = []
                if not include_similar_cases:
                    memory_context.similar_cases = []
                if not include_agent_experience:
                    memory_context.agent_experience = {}
                
                # Aktualizacja statystyk
                self._stats['success_count'] += 1
                build_time_ms = (datetime.now() - start_time).total_seconds() * 1000
                memory_context.memory_stats['build_time_ms'] = build_time_ms
                
                logger.debug(f"Built memory context for agent {agent_id}: {memory_context.memory_stats}")
                
                return memory_context
                
            except Exception as e:
                self._stats['error_count'] += 1
                logger.error(f"Error building memory context for agent {agent_id}: {str(e)}")
                return MemoryContext()
    
    def enhance_decision_context(
        self,
        original_context: Any,
        memory_context: Optional[MemoryContext] = None,
        agent_id: Optional[str] = None,
        current_situation: Optional[Dict[str, Any]] = None
    ) -> EnhancedDecisionContext:
        """
        Rozszerza istniejacy DecisionContext o kontekst pamięci.
        
        Ta metoda tworzy EnhancedDecisionContext, który łączy oryginalne
        dane decyzji z historycznym kontekstem pamięci.
        
        Args:
            original_context: Oryginalny DecisionContext
            memory_context: Opcjonalny MemoryContext (jeśli nie podany, zostanie zbudowany)
            agent_id: Opcjonalny ID agenta (do zbudowania MemoryContext)
            current_situation: Opcjonalna bieżąca sytuacja (do zbudowania MemoryContext)
            
        Returns:
            EnhancedDecisionContext gotowy do użycia
        """
        with self._lock:
            self._stats['enhancements'] += 1
            
            try:
                # Walidacja inputu
                if original_context is None:
                    raise DecisionMemoryContextError("original_context cannot be None")
                
                # Jeśli MemoryContext nie został podany, zbuduj go
                if memory_context is None:
                    if agent_id and current_situation:
                        memory_context = self.build_memory_context(
                            agent_id=agent_id,
                            current_situation=current_situation
                        )
                    else:
                        # Utwórz pusty MemoryContext
                        memory_context = MemoryContext()
                
                # Utworzenie EnhancedDecisionContext
                enhanced_context = EnhancedDecisionContext(
                    original_context=original_context,
                    memory_context=memory_context
                )
                
                self._stats['success_count'] += 1
                logger.debug(f"Enhanced DecisionContext created with memory context")
                
                return enhanced_context
                
            except Exception as e:
                self._stats['error_count'] += 1
                logger.error(f"Error enhancing decision context: {str(e)}")
                # Zwróć EnhancedDecisionContext z pustym MemoryContext
                return EnhancedDecisionContext(
                    original_context=original_context,
                    memory_context=MemoryContext()
                )
    
    def get_decision_context_with_memory(
        self,
        agent_id: str,
        current_situation: Dict[str, Any],
        contract_data: Optional[Dict[str, Any]] = None
    ) -> EnhancedDecisionContext:
        """
        Utniej metoda do budowania kompletniez EnhancedDecisionContext.
        
        Łączy budowanie MemoryContext i tworzenie EnhancedDecisionContext
        w jednej operacji.
        
        Args:
            agent_id: ID agenta
            current_situation: Bieżąca sytuacja
            contract_data: Opcjonalne dane kontraktu do utworzenia DecisionContext
            
        Returns:
            EnhancedDecisionContext z pełnym kontekstem
        """
        with self._lock:
            try:
                # Budowanie MemoryContext
                memory_context = self.build_memory_context(
                    agent_id=agent_id,
                    current_situation=current_situation
                )
                
                # Utworzenie oryginalnego DecisionContext z danych kontraktu
                if contract_data:
                    # Import tutaj, aby unikać zależności cyklicznych
                    from .decision_engine import DecisionContext
                    original_context = DecisionContext(
                        world_data=contract_data.get('world_data', {}),
                        model_info=contract_data.get('model_evaluation', {}),
                        weights=contract_data.get('current_weights', {}),
                        recommendations=contract_data.get('recommendations', []),
                        risk_factors=contract_data.get('risk_factors', {}),
                        constraints=contract_data.get('constraints', {})
                    )
                else:
                    # Utworzenie pustego DecisionContext
                    from .decision_engine import DecisionContext
                    original_context = DecisionContext()
                
                # Rozszerzenie kontekstu
                return self.enhance_decision_context(
                    original_context=original_context,
                    memory_context=memory_context
                )
                
            except Exception as e:
                logger.error(f"Error building complete decision context: {str(e)}")
                from .decision_engine import DecisionContext
                return EnhancedDecisionContext(
                    original_context=DecisionContext(),
                    memory_context=MemoryContext()
                )
    
    def extract_learning_patterns(
        self,
        memory_context: MemoryContext
    ) -> Dict[str, Any]:
        """
        Ekstrakcja wzorców uczenia się z kontekstu pamięci.
        
        Analizuje historyczne dane i wyodrębnia kluczowe wzorce,
        które mogą pomóc w podejmowaniu decyzji.
        
        Args:
            memory_context: MemoryContext do analizy
            
        Returns:
            Słownik zidentyfikowanych wzorców
        """
        patterns = {
            'decision_patterns': [],
            'success_patterns': [],
            'failure_patterns': [],
            'risk_patterns': [],
            'opportunity_patterns': []
        }
        
        if not memory_context:
            return patterns
        
        # Analiza poprzednich decyzji
        for decision in memory_context.previous_decisions:
            if not isinstance(decision, dict):
                continue
            
            decision_type = decision.get('decision_type', 'unknown')
            outcome = decision.get('outcome', 'unknown')
            confidence = decision.get('confidence', 0.0)
            
            pattern = {
                'decision_type': decision_type,
                'outcome': outcome,
                'confidence': confidence,
                'parameters': decision.get('parameters', {}),
                'context': decision.get('context', {})
            }
            
            patterns['decision_patterns'].append(pattern)
            
            # Klasyfikacja wzorców
            if outcome in ['success', 'positive', 'good', 'win']:
                patterns['success_patterns'].append(pattern)
            elif outcome in ['failure', 'negative', 'bad', 'lose']:
                patterns['failure_patterns'].append(pattern)
            
            # Analiza ryzyka
            if confidence < 0.5:
                patterns['risk_patterns'].append(pattern)
            elif confidence > 0.8:
                patterns['opportunity_patterns'].append(pattern)
        
        # Analiza podobnych przypadków
        for case in memory_context.similar_cases:
            if not isinstance(case, dict):
                continue
            
            # Ekstrakcja kluczowych informacji
            case_info = {
                'type': case.get('type', 'unknown'),
                'similarity': case.get('similarity', 0.0),
                'data': case.get('data', {})
            }
            
            # Dodanie do odpowiednich kategorii
            if case_info['similarity'] > 0.8:
                patterns['success_patterns'].append(case_info)
        
        return patterns