# SSI V5 - RAG Retrieval Layer
# ==================================================
#
# ETAP: 0 KROK 4 - RAG Retrieval Layer
# Data: 2026-08-04
# 
# Odpowiedzialnosc:
# - Warstwa inteligentnego wyszukiwania wiedzy
# - Integracja z VectorIndex i CollectiveMemoryManager
# - Dostarczanie istotnej wiedzy dla DecisionEngine
#
# ZASADY:
# 1. NIE tworzyć nowego VectorIndex
# 2. NIE modyfikować istniejacego CollectiveMemoryManager
# 3. TYLKO dodawac warstwe abstrakcji
# 4. Wszystkie operacje thread-safe
#
# Uzycie:
#   from SSI_V5.memory.collective_memory.rag_retrieval import RAGRetrieval
#   
#   # Inicjalizacja
#   rag_retrieval = RAGRetrieval(vector_index, collective_manager)
#   
#   # Wyszukiwanie wiedzy
#   relevant_knowledge = rag_retrieval.retrieve_knowledge(
#       query="Liverpool vs Arsenal prediction",
#       agent_id="agent_01",
#       top_k=5,
#       min_similarity=0.6
#   )
#

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import threading
import logging
import copy
import numpy as np

# Konfiguracja logowania
logger = logging.getLogger(__name__)


class RAGRetrievalError(Exception):
    """Wyjatki dla warstwy RAG Retrieval"""
    pass


class RAGRetrieval:
    """
    Warstwa RAG Retrieval - inteligentne wyszukiwanie wiedzy dla systemu SSI V5.
    
    Odpowiedzialnosc:
    - Pośredniczenie między DecisionEngine a VectorIndex
    - Konwersja zapytań tekstowych na wektory i wyszukiwanie
    - Filtrowanie i ranking wyników wyszukiwania
    - Dostarczanie strukturyzowanej wiedzy dla decyzji
    
    Architektura:
        Query (tekst)
            ↓
        Text → Embedding (via EmbeddingGenerator)
            ↓
        Vector Search (via VectorIndex)
            ↓
        Raw Memories
            ↓
        Filter & Rank
            ↓
        Relevant Knowledge (strukturalizowane)
    
    Uzycie:
        # Inicjalizacja
        from SSI_V5.memory.collective_memory.vector_index import VectorIndex
        from SSI_V5.memory.collective_memory.collective_memory_manager import CollectiveMemoryManager
        from SSI_V5.memory.collective_memory.embedding_generator import EmbeddingGenerator
        
        embedding_gen = EmbeddingGenerator()
        vector_index = VectorIndex(embedding_generator=embedding_gen)
        collective_manager = CollectiveMemoryManager()
        
        rag_retrieval = RAGRetrieval(vector_index, collective_manager)
        
        # Wyszukiwanie
        knowledge = rag_retrieval.retrieve_knowledge(
            query="high risk betting strategy",
            agent_id="agent_01",
            context={"phase": "prediction_window"}
        )
    """
    
    def __init__(self, vector_index: Any, collective_memory_manager: Any):
        """
        Inicjalizacja warstwy RAG Retrieval.
        
        Args:
            vector_index: Instancja VectorIndex do wyszukiwania wektorowego
            collective_memory_manager: Instancja CollectiveMemoryManager do dostępu do pamięci
            
        Raises:
            RAGRetrievalError: Jeśli którykolwiek z komponentów jest None
        """
        if vector_index is None:
            raise RAGRetrievalError("VectorIndex cannot be None")
        
        if collective_memory_manager is None:
            raise RAGRetrievalError("CollectiveMemoryManager cannot be None")
        
        self._vector_index = vector_index
        self._collective_manager = collective_memory_manager
        self._lock = threading.RLock()
        self._initialized = False
        
        # Statystyki operacji
        self._stats = {
            'retrieval_operations': 0,
            'success_count': 0,
            'error_count': 0,
            'total_retrieved': 0,
            'average_similarity': 0.0
        }
        
        logger.info("RAGRetrieval initialized")
    
    def initialize(self) -> Dict[str, Any]:
        """
        Inicjalizacja warstwy RAG Retrieval.
        
        Returns:
            Status inicjalizacji
        """
        with self._lock:
            if self._initialized:
                return {
                    'status': 'success',
                    'message': 'Already initialized',
                    'timestamp': datetime.now().isoformat()
                }
            
            try:
                # Sprawdzenie[NIE modyfikować istniejacego CollectiveMemoryManager]
                # 2. NIE modyfikować istniejacego VectorIndex
                # 
                if not hasattr(self._vector_index, 'search'):
                    raise RAGRetrievalError("VectorIndex missing search method")
                
                if not hasattr(self._collective_manager, 'get_relevant_memories'):
                    raise RAGRetrievalError("CollectiveMemoryManager missing get_relevant_memories method")
                
                self._initialized = True
                logger.info("RAGRetrieval successfully initialized")
                
                return {
                    'status': 'success',
                    'message': 'RAGRetrieval initialized',
                    'components': {
                        'vector_index': type(self._vector_index).__name__,
                        'collective_manager': type(self._collective_manager).__name__
                    },
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"RAGRetrieval initialization failed: {str(e)}")
                return {
                    'status': 'error',
                    'message': f'Initialization failed: {str(e)}',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
    
    @property
    def is_initialized(self) -> bool:
        """Czy warstwa jest zainicjalizowana?"""
        return self._initialized
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Zwraca statystyki operacji"""
        with self._lock:
            return copy.deepcopy(self._stats)
    
    def retrieve_knowledge(
        self,
        query: str,
        agent_id: Optional[str] = None,
        top_k: int = 5,
        min_similarity: float = 0.6,
        context: Optional[Dict[str, Any]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Pobieranie wiedzy na podstawie zapytania tekstowego.
        
        Ta metoda wykona pełny przepływ RAG:
        1. Konwersja zapytania na embedding
        2. Wyszukiwanie wektorowe w VectorIndex
        3. Filtrowanie i ranking wyników
        4. Zwrócenie strukturyzowanej wiedzy
        
        Args:
            query: Zapytanie tekstowe (np: "Liverpool vs Arsenal high risk")
            agent_id: Opcjonalny ID agenta do filtrowania wyników
            top_k: Maksymalna liczba wyników do zwrócenia (domyślnie 5)
            min_similarity: Minimalne podobieństwo (0.0-1.0, domyślnie 0.6)
            context: Dodatkowy kontekst do wzbogacenia zapytania
            filters: Filtry dla wyników (np: {"type": "decision", "outcome": "success"})
            
        Returns:
            Struktura z wiedzą gotową do użycia przez DecisionEngine:
            {
                'status': 'success',
                'query': query,
                'results': [
                    {
                        'memory_id': 'mem_xxx',
                        'content': {...},
                        'similarity': 0.85,
                        'type': 'decision/observation/experience',
                        'relevance_score': 0.92
                    }
                ],
                'summary': {
                    'total_results': X,
                    'average_similarity': Y,
                    'top_categories': [...]
                },
                'timestamp': '...'
            }
        """
        with self._lock:
            self._stats['retrieval_operations'] += 1
            
            try:
                start_time = datetime.now()
                
                # Walidacja inputu
                if not query or not isinstance(query, str):
                    raise RAGRetrievalError("Invalid query: must be a non-empty string")
                
                if not self._initialized:
                    logger.warning("RAGRetrieval not initialized, initializing now...")
                    self.initialize()
                
                # Krok 1: Wyszukiwanie wektorowe - uzywamy istniejacej metody VectorIndex i CollectiveMemory
                raw_results = []
                
                # Wyszukiwanie przez VectorIndex (jeśli dostępny)
                if hasattr(self._vector_index, 'search'):
                    vector_results = self._vector_index.search(
                        query=query,
                        top_k=top_k * 2,  # Pobierz więcej, potem zfiltrujemy
                        min_similarity=min_similarity
                    )
                    raw_results.extend(vector_results)
                
                # Dodatkowe wyszukiwanie przez CollectiveMemoryManager (wapien przed wektorami na tekst)
                if hasattr(self._collective_manager, 'search_memories'):
                    text_results = self._collective_manager.search_memories(
                        query=query,
                        top_k=top_k * 2,
                        min_similarity=min_similarity
                    )
                    # Dodaj wyniki w formie wspólnej
                    for doc in text_results:
                        if hasattr(doc, 'to_dict'):
                            raw_results.append(doc.to_dict())
                        elif isinstance(doc, dict):
                            raw_results.append(doc)
                
                # Krok 2: Filtrowanie i ranking
                filtered_results = self._filter_and_rank_results(
                    raw_results, 
                    agent_id=agent_id, 
                    min_similarity=min_similarity,
                    filters=filters,
                    top_k=top_k
                )
                
                # Krok 3: Ekstrakcja i strukturyzacja wiedzy
                structured_knowledge = self._extract_structured_knowledge(
                    filtered_results, query, context
                )
                
                # Krok 4: Statystyki i formatowanie wyniku
                result = self._format_retrieval_result(
                    query, 
                    filtered_results, 
                    structured_knowledge, 
                    start_time
                )
                
                self._stats['success_count'] += 1
                self._stats['total_retrieved'] += len(filtered_results)
                
                logger.debug(f"RAG Retrieval: {len(filtered_results)} results for query '{query[:50]}...'")
                
                return result
                
            except Exception as e:
                self._stats['error_count'] += 1
                logger.error(f"RAG Retrieval error for query '{query[:50]}...': {str(e)}")
                return {
                    'status': 'error',
                    'query': query,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
    
    def retrieve_for_decision_context(
        self,
        current_situation: Dict[str, Any],
        agent_id: str,
        top_k: int = 5,
        min_similarity: float = 0.6
    ) -> Dict[str, Any]:
        """
        Pobieranie wiedzy na podstawie bieżącej sytuacji agenta.
        
        Ta metoda jest specjalnie zaprojektowana do współpracy z DecisionEngine
        i MemoryIntegrationLayer. Tworzy zapytanie na podstawie kontekstu aktualnego.
        
        Args:
            current_situation: Bieżąca sytuacja agenta (słownik z danymi)
            agent_id: ID agenta
            top_k: Maksymalna liczba wyników
            min_similarity: Minimalne podobieństwo
            
        Returns:
            Wiadomość gotowa do użycia przez DecisionMemoryContext
        """
        with self._lock:
            try:
                # Konwersja sytuacji na zapytanie tekstowe
                query = self._create_query_from_situation(current_situation)
                
                # Pobranie wiedzy
                knowledge = self.retrieve_knowledge(
                    query=query,
                    agent_id=agent_id,
                    top_k=top_k,
                    min_similarity=min_similarity,
                    context=current_situation
                )
                
                # Formatowanie specjalne dla decision context
                decision_knowledge = self._format_for_decision_context(knowledge, current_situation)
                
                return decision_knowledge
                
            except Exception as e:
                logger.error(f"Error retrieving decision context knowledge: {str(e)}")
                return {
                    'status': 'error',
                    'query': self._create_query_from_situation(current_situation),
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
    
    def _create_query_from_situation(self, situation: Dict[str, Any]) -> str:
        """Tworzenie zapytania tekstowego z sytuacji agenta"""
        query_parts = []
        
        # Dodaj kluczowe informacje z sytuacji
        if 'world_name' in situation:
            query_parts.append(situation['world_name'])
        
        if 'phase' in situation:
            query_parts.append(situation['phase'])
        
        if 'goal' in situation:
            query_parts.append(situation['goal'])
        
        if 'world_data_keys' in situation:
            for key in situation['world_data_keys'][:3]:  # Maksymalnie 3 klucze
                query_parts.append(key)
        
        # Główny typ przedmiotu
        query = " ".join(query_parts) if query_parts else "general"
        return query
    
    def _filter_and_rank_results(
        self,
        raw_results: List[Dict[str, Any]],
        agent_id: Optional[str] = None,
        min_similarity: float = 0.6,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Filtrowanie i ranking wyników wyszukiwania"""
        filtered = []
        
        for result in raw_results:
            if not isinstance(result, dict):
                continue
            
            # Filtrowanie po agent_id
            if agent_id:
                result_agent_id = result.get('agent_id') or result.get('source_metadata', {}).get('agent_id')
                if result_agent_id and result_agent_id != agent_id:
                    continue
            
            # Filtrowanie po minimalnym podobieństwie
            similarity = result.get('similarity', 0.0)
            if similarity < min_similarity:
                continue
            
            # Filtrowanie wedługez user filters
            if filters:
                match = True
                for key, value in filters.items():
                    if result.get(key) != value:
                        # Sprawdź też w content
                        content = result.get('content', {})
                        if content.get(key) != value:
                            match = False
                            break
                if not match:
                    continue
            
            filtered.append(result)
        
        # Sortowanie po similarity (malejąco)
        filtered.sort(key=lambda x: x.get('similarity', 0.0), reverse=True)
        
        # Ogranicz do top_k
        return filtered[:top_k]
    
    def _extract_structured_knowledge(
        self,
        results: List[Dict[str, Any]],
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Ekstrakcja strukturyzowanej wiedzy z wyników"""
        knowledge = {
            'relevant_cases': [],
            'decision_patterns': [],
            'risk_factors': [],
            'success_indicators': [],
            'statistics': {}
        }
        
        for result in results:
            content = result.get('content', {})
            result_type = result.get('type', 'unknown')
            
            # Klasyfikacja na podstawie typu
            if result_type in ['decision', 'decision_outcome']:
                knowledge['decision_patterns'].append(content)
            elif result_type in ['observation', 'world_state']:
                knowledge['relevant_cases'].append(content)
            elif result_type in ['risk_assessment', 'risk_analysis']:
                knowledge['risk_factors'].append(content)
            elif result_type in ['success_pattern', 'positive_outcome']:
                knowledge['success_indicators'].append(content)
            else:
                # Ogólne przypadki
                knowledge['relevant_cases'].append(content)
        
        # Statystyki
        knowledge['statistics'] = {
            'total_cases': len(knowledge['relevant_cases']),
            'total_patterns': len(knowledge['decision_patterns']),
            'total_risk_factors': len(knowledge['risk_factors']),
            'total_success_indicators': len(knowledge['success_indicators'])
        }
        
        return knowledge
    
    def _format_retrieval_result(
        self,
        query: str,
        filtered_results: List[Dict[str, Any]],
        structured_knowledge: Dict[str, Any],
        start_time: datetime
    ) -> Dict[str, Any]:
        """Formatowanie wyniku wyszukiwania"""
        # Oblicz średnie podobieństwo
        similarities = [r.get('similarity', 0.0) for r in filtered_results]
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
        
        # Kategorie
        categories = set()
        for result in filtered_results:
            categories.add(result.get('type', 'unknown'))
        
        # Formatowanie wyników
        formatted_results = []
        for result in filtered_results:
            formatted_results.append({
                'memory_id': result.get('id', result.get('memory_id', 'unknown')),
                'content': result.get('content', {}),
                'similarity': result.get('similarity', 0.0),
                'type': result.get('type', 'unknown'),
                'relevance_score': result.get('relevance_score', result.get('similarity', 0.0))
            })
        
        # Aktualizacja statystyk
        self._stats['average_similarity'] = avg_similarity
        
        return {
            'status': 'success',
            'query': query,
            'results': formatted_results,
            'structured_knowledge': structured_knowledge,
            'summary': {
                'total_results': len(formatted_results),
                'average_similarity': avg_similarity,
                'top_categories': list(categories),
                'retrieval_time_ms': (datetime.now() - start_time).total_seconds() * 1000
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _format_for_decision_context(
        self,
        knowledge: Dict[str, Any],
        current_situation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Formatowanie wiedzy specjalnie dla DecisionContext"""
        # Jeśli było ok
        if knowledge.get('status') != 'success':
            return knowledge
        
        formatted = {
            'status': 'success',
            'query': knowledge.get('query', ''),
            'relevant_memories': knowledge.get('results', []),
            'structured_knowledge': knowledge.get('structured_knowledge', {}),
            'memory_count': knowledge.get('summary', {}).get('total_results', 0),
            'similarity_stats': {
                'average': knowledge.get('summary', {}).get('average_similarity', 0.0),
                'categories': knowledge.get('summary', {}).get('top_categories', [])
            },
            'context_matching': {
                'world_name': current_situation.get('world_name', 'unknown'),
                'phase': current_situation.get('phase', 'unknown'),
                'match_score': 0.0  # Mogłoby być obliczane na podstawie dopasowania
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return formatted
    
    def get_relevant_knowledge_for_decision(
        self,
        decision_type: str,
        context: Dict[str, Any],
        agent_id: str
    ) -> Dict[str, Any]:
        """
        Pobieranie istotnej wiedzy dla konkretnego typu decyzji.
        
        Ta metoda jest optymalizowana do pracy z DecisionEngine
        i dostarcza wiedzę specyficzną dla danego typu decyzji.
        
        Args:
            decision_type: Typ decyzji (np: "model_selection", "weight_adjustment")
            context: Kontekst aktualnej decyzji
            agent_id: ID agenta
            
        Returns:
            Wiadomość z wiedzą specyficzną dla typu decyzji
        """
        # Budowa zapytania na podstawie typu decyzji i kontekstu
        query = f"{decision_type} {self._context_to_query(context)}"
        
        # Pobranie ogólnej wiedzy
        knowledge = self.retrieve_knowledge(
            query=query,
            agent_id=agent_id,
            top_k=10,
            min_similarity=0.5
        )
        
        # Filtrowanie według typu decyzji
        if knowledge.get('status') == 'success':
            filtered_results = []
            for result in knowledge.get('results', []):
                result_type = result.get('type', 'unknown')
                result_content = result.get('content', {})
                
                # Filtrowanie po typie decyzji i powiązanych typach
                relevant_types = [
                    decision_type,
                    'decision',
                    f'{decision_type}_pattern',
                    f'{decision_type}_outcome'
                ]
                
                if result_type in relevant_types or result_content.get('decision_type') == decision_type:
                    filtered_results.append(result)
            
            # Aktualizacja wyniku
            knowledge['results'] = filtered_results
            knowledge['summary']['total_results'] = len(filtered_results)
        
        return knowledge
    
    def _context_to_query(self, context: Dict[str, Any]) -> str:
        """Konwersja kontekstu na fragment zapytania"""
        parts = []
        
        for key, value in context.items():
            if isinstance(value, (str, int, float)) and key not in ['timestamp', 'agent_id']:
                parts.append(f"{key}:{value}")
        
        return " ".join(parts)
