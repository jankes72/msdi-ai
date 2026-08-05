"""
SSI V5 - Collective Memory Layer
ETAP: 5.4.2.2 - CollectiveMemoryManager Foundation

Autor: SSI V5 System / Mistral Vibe
Data: 2026-08-04
Wersja: 2.0.0
"""

from .memory_document import CollectiveMemoryDocument
from .memory_document_adapter_v2 import MemoryDocumentAdapter
from .embedding_generator import EmbeddingGenerator, EmbeddingResult, create_embedding_generator
from .vector_index import VectorIndex, VectorIndexConfig, SearchResult, IndexedVector, create_vector_index
from .vector_index import INDEX_TYPE_NUMPY, INDEX_TYPE_FAISS, INDEX_TYPE_CHROMA
from .collective_memory_manager import (
    CollectiveMemoryManager,
    CollectiveMemoryManagerConfig,
    create_collective_memory_manager
)
from .rag_retrieval import RAGRetrieval, RAGRetrievalError

__all__ = [
    "CollectiveMemoryDocument",
    "MemoryDocumentAdapter",
    "EmbeddingGenerator",
    "EmbeddingResult",
    "create_embedding_generator",
    "VectorIndex",
    "VectorIndexConfig",
    "SearchResult",
    "IndexedVector",
    "create_vector_index",
    "INDEX_TYPE_NUMPY",
    "INDEX_TYPE_FAISS",
    "INDEX_TYPE_CHROMA",
    "CollectiveMemoryManager",
    "CollectiveMemoryManagerConfig",
    "create_collective_memory_manager",
    "RAGRetrieval",
    "RAGRetrievalError",
]
