"""
SSI V5 - Collective Memory Manager
ETAP: 5.4.2.2 - CollectiveMemoryManager Foundation

Odpowiedzialnosc:
- Centralne zarzadzanie pamiecia zbiorowa
- Integracja z VectorIndex
- API dla agentow
- Pobieranie kontekstu semantycznego dla agentow

ZASADY:
1. NIE modyfikowac istniejacych pamieci
2. TYLKO dodawanie nowej warstwy abstrakcji
3. NIE zmieniac CycleController, Pipeline, Runtime
4. Wszystkie operacje thread-safe

Architektura:
    Agent
     |
    v
CollectiveMemoryManager
     |
    +-- MemoryDocumentAdapter (warstwa adapterow)
     |
    +-- VectorIndex (abstrakcja indeksu)
     |    
    +-- Backend (Numpy/FAISS/ChromaDB)
     |
    +-- EmbeddingGenerator

Przeplyw danych:
    1. Agent -> store_memory(memory_record)
    2. CollectiveMemoryManager -> MemoryDocumentAdapter.convert()
    3. MemoryDocumentAdapter -> VectorIndex.add()
    4. VectorIndex -> Backend.add_vector()
    
    Wyszukiwanie:
    1. Agent -> search_memories(query)
    2. CollectiveMemoryManager -> VectorIndex.search()
    3. VectorIndex -> Backend.search()
    4. Wynik -> CollectiveMemoryDocument

Autor: SSI V5 System / Mistral Vibe
Data: 2026-08-04
Wersja: 2.0.0
"""

from typing import Dict, Any, Optional, List, Union
import threading
import logging

# Import z warstwy adapterow
from .memory_document import CollectiveMemoryDocument
from .memory_document_adapter_v2 import MemoryDocumentAdapter
from .vector_index import VectorIndex, VectorIndexConfig, SearchResult, create_vector_index
from .embedding_generator import EmbeddingGenerator, create_embedding_generator

# Konfiguracja logowania
logger = logging.getLogger(__name__)


class CollectiveMemoryManager:
    """
    Centralny manager pamieci zbiorowej.
    
    Odpowiedzialny za:
    - Zapis i odczyt dokumentow pamieci
    - Integracje z VectorIndex
    - Wyszukiwanie semantyczne
    - Budowanie kontekstu dla agentow
    
    Usage:
        manager = CollectiveMemoryManager(vector_index_config, embedding_config)
        
        # Zapis pamieci
        manager.store_memory(strategy_record)
        manager.store_memory(match_result)
        
        # Wyszukiwanie
        results = manager.search_memories("Liverpool vs Arsenal", top_k=5)
        
        # Budowanie kontekstu dla agenta
        context = manager.build_agent_context(agent_id, current_situation)
    """
    
    def __init__(
        self,
        vector_index: Optional[VectorIndex] = None,
        memory_adapter: Optional[MemoryDocumentAdapter] = None,
        embedding_generator: Optional[EmbeddingGenerator] = None
    ):
        """
        Inicjalizacja CollectiveMemoryManager.
        
        Args:
            vector_index: Instancja VectorIndex (opcjonalnie - zostanie utworzona)
            memory_adapter: Instancja MemoryDocumentAdapter (opcjonalnie)
            embedding_generator: Instancja EmbeddingGenerator (opcjonalnie)
        """
        # Thread-safety
        self._lock = threading.RLock()
        
        # Komponenty
        self._vector_index = vector_index
        self._memory_adapter = memory_adapter or MemoryDocumentAdapter()
        self._embedding_generator = embedding_generator
        
        # Statystyki
        self._stats = {
            'total_memories': 0,
            'memories_by_type': {},
            'search_operations': 0,
            'store_operations': 0
        }
        
        logger.info("CollectiveMemoryManager initialized")
    
    @property
    def vector_index(self) -> VectorIndex:
        """Zwraca instancje VectorIndex."""
        if self._vector_index is None:
            raise ValueError("VectorIndex not initialized. Call initialize() or provide in constructor.")
        return self._vector_index
    
    @property
    def embedding_generator(self) -> EmbeddingGenerator:
        """Zwraca instancje EmbeddingGenerator."""
        if self._embedding_generator is None:
            raise ValueError("EmbeddingGenerator not initialized.")
        return self._embedding_generator
    
    def initialize(
        self,
        vector_index_config: Optional[VectorIndexConfig] = None,
        embedding_dimension: int = 384
    ) -> None:
        """
        Inicjalizuje komponenty jeśli nie zostały dostarczone w konstruktorze.
        
        Args:
            vector_index_config: Konfiguracja VectorIndex
            embedding_dimension: Rozmiar wektorow
        """
        with self._lock:
            # Najpierw stwórz EmbeddingGenerator jesli potrzebny
            if self._embedding_generator is None:
                self._embedding_generator = create_embedding_generator(
                    dimension=embedding_dimension
                )
                logger.info(f"EmbeddingGenerator initialized with dimension: {embedding_dimension}")
            
            # Potem stwórz VectorIndex z EmbeddingGenerator
            if self._vector_index is None:
                config = vector_index_config or VectorIndexConfig(
                    dimension=embedding_dimension
                )
                self._vector_index = create_vector_index(
                    index_type=config.index_type,
                    dimension=config.dimension,
                    storage_path=config.storage_path,
                    auto_save=config.auto_save,
                    embedding_generator=self._embedding_generator
                )
                logger.info(f"VectorIndex initialized with config: {config.to_dict()}")
    
    # =====================================================================
    # STORING MEMORIES
    # =====================================================================
    
    def store_memory(self, memory_record: Any) -> Optional[str]:
        """
        Zapisuje rekord pamieci do zbiorczej pamieci.
        
        Args:
            memory_record: Rekord pamieci (StrategyMemoryRecord, MatchResult, etc.)
            
        Returns:
            ID zindeksowanego dokumentu lub None jesli typ nieobslugiwany
        """
        with self._lock:
            # Konwertuj na CollectiveMemoryDocument
            doc = self._memory_adapter.convert(memory_record)
            if doc is None:
                logger.warning(f"Cannot convert memory record of type {type(memory_record).__name__}")
                return None
            
            # Dodaj do indeksu
            indexed = self.vector_index.add(doc)
            if indexed is None:
                logger.warning(f"Failed to index memory document {doc.document_id}")
                return None
            
            # Aktualizuj statystyki
            self._stats['total_memories'] += 1
            source_type = doc.source_type
            self._stats['memories_by_type'][source_type] = \
                self._stats['memories_by_type'].get(source_type, 0) + 1
            self._stats['store_operations'] += 1
            
            logger.debug(f"Stored memory: {doc.source_type}/{doc.source_id}")
            return indexed.vector_id
    
    def store_batch(self, memory_records: List[Any]) -> List[str]:
        """
        Zapisuje wiele rekordow pamieci wsadowo.
        
        Args:
            memory_records: Lista rekordow pamieci
            
        Returns:
            Lista ID zindeksowanych dokumentow
        """
        with self._lock:
            results = []
            for record in memory_records:
                doc_id = self.store_memory(record)
                if doc_id:
                    results.append(doc_id)
            
            logger.info(f"Stored batch of {len(results)}/{len(memory_records)} memories")
            return results
    
    # =====================================================================
    # SEARCHING MEMORIES
    # =====================================================================
    
    def search_memories(
        self,
        query: str,
        top_k: int = 10,
        min_similarity: float = 0.0,
        source_type_filter: Optional[str] = None
    ) -> List[CollectiveMemoryDocument]:
        """
        Szuka podobnych pamięci w indeksie.
        
        Args:
            query: Zapytanie tekstowe
            top_k: Maksymalna liczba wynikow
            min_similarity: Minimalne podobieństwo (0.0-1.0)
            source_type_filter: Filtr po typie zrodla (opcjonalnie)
            
        Returns:
            Lista CollectiveMemoryDocument posortowana po podobieństwie
        """
        with self._lock:
            # Przeplyw: query -> embedding -> search -> results
            results = []
            
            # Wyszukaj w indeksie
            search_results = self.vector_index.search_by_text(query, top_k=top_k * 2)
            
            # Filtruj i konwertuj wyniki
            for sr in search_results:
                # Filtruj po podobieństwie
                if sr.similarity < min_similarity:
                    continue
                
                # Filtruj po typie zrodla
                if source_type_filter and sr.document and sr.document.source_type != source_type_filter:
                    continue
                
                if sr.document:
                    results.append(sr.document)
                
                # Ogranicz do top_k
                if len(results) >= top_k:
                    break
            
            # Aktualizuj statystyki
            self._stats['search_operations'] += 1
            
            logger.debug(f"Search: '{query}' -> {len(results)} results")
            return results
    
    def search_by_situation(
        self,
        situation: Dict[str, Any],
        top_k: int = 5,
        min_similarity: float = 0.5
    ) -> List[CollectiveMemoryDocument]:
        """
        Szuka pamięci podobnych do podanej sytuacji.
        
        Args:
            situation: Słownik opisujacy aktualna sytuacje
            top_k: Maksymalna liczba wynikow
            min_similarity: Minimalne podobieństwo
            
        Returns:
            Lista pasujacych dokumentow pamieci
        """
        with self._lock:
            # Konwertuj sytuacje na tekst do wyszukiwania
            query_text = self._situation_to_query(situation)
            
            # Wyszukaj
            return self.search_memories(
                query=query_text,
                top_k=top_k,
                min_similarity=min_similarity
            )
    
    def _situation_to_query(self, situation: Dict[str, Any]) -> str:
        """Konwertuje sytuacje na zapytanie tekstowe."""
        parts = []
        for key, value in situation.items():
            if isinstance(value, (str, int, float)):
                parts.append(f"{key}:{value}")
            elif isinstance(value, list):
                parts.append(f"{key}:[{', '.join(str(v) for v in value)}]")
            elif isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    parts.append(f"{key}_{sub_key}:{sub_value}")
        return " ".join(parts)
    
    # =====================================================================
    # RETRIEVING AND CONTEXT BUILDING
    # =====================================================================
    
    def retrieve_memory(self, document_id: str) -> Optional[CollectiveMemoryDocument]:
        """
        Pobiera pojedyńczy dokument pamieci po ID.
        
        Args:
            document_id: ID dokumentu
            
        Returns:
            CollectiveMemoryDocument lub None
        """
        with self._lock:
            doc = self.vector_index.get(document_id)
            if doc:
                return doc
            return None
    
    def get_relevant_memories(
        self,
        current_context: Dict[str, Any],
        top_k: int = 5,
        min_similarity: float = 0.6
    ) -> List[CollectiveMemoryDocument]:
        """
        Pobiera pamięci istotne dla bieżącego kontekstu.
        
        Args:
            current_context: Biezacy kontekst (sytuacja, strategia, etc.)
            top_k: Maksymalna liczba wynikow
            min_similarity: Minimalne podobieństwo
            
        Returns:
            Lista istotnych pamięci
        """
        with self._lock:
            # Buduj zapytanie z kontekstu
            query = " ".join(f"{k}:{v}" for k, v in current_context.items() if isinstance(v, (str, int, float)))
            
            # Wyszukaj
            return self.search_memories(
                query=query,
                top_k=top_k,
                min_similarity=min_similarity
            )
    
    def build_agent_context(
        self,
        agent_id: str,
        current_situation: Dict[str, Any],
        max_context_length: int = 2000
    ) -> Dict[str, Any]:
        """
        Buduje kontekst dla agenta na podstawie historii i podobnych sytuacji.
        
        Args:
            agent_id: ID agenta
            current_situation: Biezaca sytuacja
            max_context_length: Maksymalna dlugosc kontekstu (w znakach)
            
        Returns:
            Słownik z kontekstem dla agenta
        """
        with self._lock:
            context = {
                'agent_id': agent_id,
                'situation': current_situation,
                'relevant_memories': [],
                'memory_context': '',
                'memory_count': 0,
                'avg_similarity': 0.0
            }
            
            # Znajdz podobne pamięci
            memories = self.get_relevant_memories(current_situation, top_k=5)
            
            if not memories:
                return context
            
            # Buduj kontekst tekstowy
            context_parts = []
            total_similarity = 0.0
            
            for i, memory in enumerate(memories, 1):
                # Add memory to context
                context_parts.append(f"Memory {i} ({memory.source_type}):")
                context_parts.append(f"  {memory.text}")
                context_parts.append("")
                
                # Add to relevant_memories
                context['relevant_memories'].append({
                    'document_id': memory.document_id,
                    'source_type': memory.source_type,
                    'source_id': memory.source_id,
                    'text': memory.text,
                    'metadata': memory.metadata
                })
            
            # Polacz kontekst
            context['memory_context'] = "\n".join(context_parts)
            context['memory_count'] = len(memories)
            
            return context
    
    # =====================================================================
    # STATISTICS AND MONITORING
    # =====================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Zwraca statystyki manager."""
        with self._lock:
            stats = self._stats.copy()
            
            # Dodaj statystyki z VectorIndex
            if self._vector_index:
                index_stats = self._vector_index.get_stats()
                stats['vector_index'] = index_stats
            
            return stats
    
    def get_memory_distribution(self) -> Dict[str, int]:
        """Zwraca rozkład typów pamięci."""
        with self._lock:
            return self._stats['memories_by_type'].copy()
    
    # =====================================================================
    # PERSISTENCE
    # =====================================================================
    
    def save(self, path: Optional[str] = None) -> bool:
        """
        Zapisuje stan pamieci zbiorowej.
        
        Args:
            path: Sciezka do zapisu (opcjonalnie - uzywa domyslnej z VectorIndex)
            
        Returns:
            True jesli zapisano pomyslnie
        """
        with self._lock:
            if self._vector_index:
                return self._vector_index.save() if path is None else self._vector_index.save(path)
            return False
    
    def load(self, path: Optional[str] = None) -> bool:
        """
        Wczytuje stan pamieci zbiorowej.
        
        Args:
            path: Sciezka do wczytania (opcjonalnie)
            
        Returns:
            True jesli wczytano pomyslnie
        """
        with self._lock:
            if self._vector_index:
                result = self._vector_index.load() if path is None else self._vector_index.load(path)
                if result:
                    # Zaktualizuj statystyki po wczytaniu
                    self._stats['total_memories'] = self._vector_index.size
                    logger.info(f"Loaded {self._vector_index.size} memories")
                return result
            return False
    
    def clear(self) -> None:
        """Czyści pamiec zbiorowa."""
        with self._lock:
            if self._vector_index:
                self._vector_index.clear()
            
            # Reset statystyk
            self._stats = {
                'total_memories': 0,
                'memories_by_type': {},
                'search_operations': 0,
                'store_operations': 0
            }
            
            logger.info("Collective memory cleared")


# =============================================================================
# FABRYKA
# =============================================================================

class CollectiveMemoryManagerConfig:
    """Konfiguracja CollectiveMemoryManager."""
    
    def __init__(
        self,
        vector_index_config: Optional[VectorIndexConfig] = None,
        embedding_dimension: int = 384,
        storage_path: str = "data/collective_memory"
    ):
        self.vector_index_config = vector_index_config or VectorIndexConfig(
            dimension=embedding_dimension,
            storage_path=storage_path
        )
        self.embedding_dimension = embedding_dimension
        self.storage_path = storage_path


def create_collective_memory_manager(
    config: Optional[CollectiveMemoryManagerConfig] = None
) -> CollectiveMemoryManager:
    """
    Tworzy CollectiveMemoryManager z domyslna konfiguracja.
    
    Args:
        config: Konfiguracja (opcjonalnie)
        
    Returns:
        Zainicjalizowany CollectiveMemoryManager
    """
    cfg = config or CollectiveMemoryManagerConfig()
    
    manager = CollectiveMemoryManager()
    manager.initialize(
        vector_index_config=cfg.vector_index_config,
        embedding_dimension=cfg.embedding_dimension
    )
    
    logger.info("CollectiveMemoryManager created with default configuration")
    return manager


# =============================================================================
# EKSPORT
# =============================================================================

__all__ = [
    'CollectiveMemoryManager',
    'CollectiveMemoryManagerConfig',
    'create_collective_memory_manager',
]
