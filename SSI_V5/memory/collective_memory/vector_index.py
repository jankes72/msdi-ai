"""
SSI V5 - Vector Index
ETAP: 5.4.1 - Memory Embedding Foundation

Odpowiedzialnosc:
- Przechowywanie wektorow embeddingow z metadanymi
- Indeksowanie dla szybkiego wyszukiwania podobienstw
- Obsluga lokalnych backendow: FAISS, ChromaDB, prosty numpy

ZASADY:
1. NIE zaleznosc od zewnetrznych serwisow (tylko lokalne rozwiazania)
2. Interfejs abstrakcyjny - mozliwosc wymiany backendow
3. Persystencja na dysku (JSON + wektory)
4. Thread-safe operacje
5. Domy wanty prosty numpy-based index (bez zewnetrznych zaleznosci)

Architektura:
    VectorIndex (Iterator)
        |
    +-- BaseVectorIndexBackend (Abstrakcyjny)
        |
        +-- NumpyVectorIndexBackend (Domy wanty)
        +-- FAISSVectorIndexBackend (Opcjonalny)
        +-- ChromaDBVectorIndexBackend (Opcjonalny)

Autor: SSI V5 System / Mistral Vibe
Data: 2026-08-04
Wersja: 1.0.0
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime
import json
import os
import threading
import pickle
import hashlib
import numpy as np

from .memory_document_adapter import CollectiveMemoryDocument
from .embedding_generator import EmbeddingResult, EmbeddingGenerator


# Typy indeksow
INDEX_TYPE_NUMPY = "numpy"
INDEX_TYPE_FAISS = "faiss"
INDEX_TYPE_CHROMA = "chroma"


@dataclass
class VectorIndexConfig:
    """
    Konfiguracja VectorIndex.
    
    Attributes:
        index_type: Typ indeksu (numpy, faiss, chroma)
        storage_path: Sciezka do almaczenia indeksu na dysku
        dimension: Rozmiar wektorow
        max_size: Maksymalna liczba wektorow
        auto_save: Czy automatycznie zapisywac zmiany
    """
    index_type: str = INDEX_TYPE_NUMPY
    storage_path: str = "data/collective_memory_index"
    dimension: int = 384
    max_size: int = 100000
    auto_save: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do dict."""
        return {
            'index_type': self.index_type,
            'storage_path': self.storage_path,
            'dimension': self.dimension,
            'max_size': self.max_size,
            'auto_save': self.auto_save
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VectorIndexConfig':
        """Konwersja z dict."""
        return cls(**data)


@dataclass
class IndexedVector:
    """
    Wektor z metadanymi zindeksowany w VectorIndex.
    
    Attributes:
        vector_id: Unikalne ID wektora
        embedding: Wektor jako lista float
        document: Oryginalny dokument pamieci (opcjonalnie)
        metadata: Dodatkowe metadane
        timestamp: Czas dodania do indeksu
    """
    vector_id: str
    embedding: List[float]
    document: Optional[CollectiveMemoryDocument] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do dict."""
        result = {
            'vector_id': self.vector_id,
            'embedding': self.embedding,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }
        if self.document:
            result['document'] = self.document.to_dict()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IndexedVector':
        """Konwersja z dict."""
        data = data.copy()
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        if 'document' in data and data['document']:
            data['document'] = CollectiveMemoryDocument.from_dict(data['document'])
        
        return cls(**data)


@dataclass
class SearchResult:
    """
    Wynik wyszukiwania w indeksie wektorowym.
    
    Attributes:
        vector_id: ID znalezionego wektora
        similarity: Podobienstwo kosinusowe (0.0-1.0)
        embedding: Wektor (opcjonalnie)
        document: Dokument pamieci (opcjonalnie)
        metadata: Metadane wektora
        rank: Pozycja w rankingu wynikow
    """
    vector_id: str
    similarity: float
    embedding: Optional[List[float]] = None
    document: Optional[CollectiveMemoryDocument] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    rank: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do dict."""
        result = {
            'vector_id': self.vector_id,
            'similarity': self.similarity,
            'metadata': self.metadata,
            'rank': self.rank
        }
        if self.embedding:
            result['embedding'] = self.embedding
        if self.document:
            result['document'] = self.document.to_dict()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchResult':
        """Konwersja z dict."""
        data = data.copy()
        
        if 'document' in data and data['document']:
            data['document'] = CollectiveMemoryDocument.from_dict(data['document'])
        
        return cls(**data)


# =============================================================================
# ABSTRAKCYJNY BACKEND DLA INDEKSU WEKTOROWEGO
# =============================================================================

class BaseVectorIndexBackend(ABC):
    """
    Abstrakcyjna klasa backend dla indeksu wektorowego.
    
    Kazdy backend musi implementowac:
    - add_vector(vector_id, embedding, metadata)
    - search(query_embedding, top_k) -> List[Tuple[vector_id, similarity]]
    - remove_vector(vector_id)
    - save()
    - load()
    - clear()
    """
    
    @property
    @abstractmethod
    def index_type(self) -> str:
        """Typ indeksu."""
        pass
    
    @property
    @abstractmethod
    def size(self) -> int:
        """Liczba zindeksowanych wektorow."""
        pass
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Rozmiar wektorow."""
        pass
    
    @abstractmethod
    def add_vector(
        self,
        vector_id: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Dodaje wektor do indeksu.
        
        Args:
            vector_id: Unikalne ID wektora
            embedding: Wektor jako lista float
            metadata: Dodatkowe metadane
            
        Returns:
            True jesli dodano pomyslnie
        """
        pass
    
    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Wyszukuje najbardziej podobne wektory.
        
        Args:
            query_embedding: Wektor zapytania
            top_k: Liczba wynikow do zwrocenia
            
        Returns:
            Lista tuple (vector_id, similarity)
        """
        pass
    
    @abstractmethod
    def remove_vector(self, vector_id: str) -> bool:
        """
        Usuwa wektor z indeksu.
        
        Args:
            vector_id: ID wektora do usuniecia
            
        Returns:
            True jesli usunieto pomyslnie
        """
        pass
    
    @abstractmethod
    def save(self, path: str) -> bool:
        """
        Zapisuje indeks do pliku.
        
        Args:
            path: Sciezka do pliku
            
        Returns:
            True jesli zapisano pomyslnie
        """
        pass
    
    @abstractmethod
    def load(self, path: str) -> bool:
        """
        Wczytuje indeks z pliku.
        
        Args:
            path: Sciezka do pliku
            
        Returns:
            True jesli wczytano pomyslnie
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Czysci indeks."""
        pass
    
    def update_vector(
        self,
        vector_id: str,
        new_embedding: List[float],
        new_metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Aktualizuje istniejusty wektor.
        
        Args:
            vector_id: ID wektora do zaktualizowania
            new_embedding: Nowy wektor
            new_metadata: Nowe metadane
            
        Returns:
            True jesli zaktualizowano pomyslnie
        """
        # Domy wanta implementacja: usun i dodaj ponownie
        if self.remove_vector(vector_id):
            return self.add_vector(vector_id, new_embedding, new_metadata)
        return False
    
    def get_vector(self, vector_id: str) -> Optional[List[float]]:
        """
        Pobiera wektor po ID.
        
        Args:
            vector_id: ID wektora
            
        Returns:
            Wektor lub None
        """
        pass


# =============================================================================
# NUMPY VECTOR INDEX BACKEND (DOMYSLNY)
# =============================================================================

class NumpyVectorIndexBackend(BaseVectorIndexBackend):
    """
    Backend indeksu wektorowego oparty na numpy.
    
    Najprostsza implementacja - sprawdza wszystkie wektory sekwencyjnie.
    Domy wanty backend bez zewnetrznych zaleznosci.
    
    Wydajnosc: O(n) dla wyszukiwania - odpowiedni dla small/medium datasets.
    """
    
    def __init__(self, dimension: int = 384):
        self._dimension = dimension
        self._vectors: Dict[str, np.ndarray] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
    
    @property
    def index_type(self) -> str:
        return INDEX_TYPE_NUMPY
    
    @property
    def size(self) -> int:
        with self._lock:
            return len(self._vectors)
    
    @property
    def dimension(self) -> int:
        return self._dimension
    
    def add_vector(
        self,
        vector_id: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Dodaje wektor do indeksu."""
        if len(embedding) != self.dimension:
            raise ValueError(f"Embedding dimension {len(embedding)} != {self.dimension}")
        
        with self._lock:
            self._vectors[vector_id] = np.array(embedding, dtype=np.float32)
            self._metadata[vector_id] = metadata or {}
        
        return True
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Wyszukuje najbardziej podobne wektory.
        
        Oblicza podobienstwo kosinusowe z wszystkimi wektorami.
        """
        if len(query_embedding) != self.dimension:
            raise ValueError(f"Query dimension {len(query_embedding)} != {self.dimension}")
        
        query_vec = np.array(query_embedding, dtype=np.float32)
        
        results = []
        
        with self._lock:
            for vector_id, vector in self._vectors.items():
                # Oblicz podobienstwo kosinusowe
                similarity = self._cosine_similarity(query_vec, vector)
                results.append((vector_id, similarity))
            
            # Sortuj po podobienstwie (malejaco)
            results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_k]
    
    def remove_vector(self, vector_id: str) -> bool:
        """Usuwa wektor z indeksu."""
        with self._lock:
            if vector_id in self._vectors:
                del self._vectors[vector_id]
                if vector_id in self._metadata:
                    del self._metadata[vector_id]
                return True
        return False
    
    def get_vector(self, vector_id: str) -> Optional[List[float]]:
        """Pobiera wektor po ID."""
        with self._lock:
            if vector_id in self._vectors:
                return self._vectors[vector_id].tolist()
        return None
    
    def save(self, path: str) -> bool:
        """Zapisuje indeks do pliku (pickle)."""
        with self._lock:
            data = {
                'vectors': {k: v.tolist() for k, v in self._vectors.items()},
                'metadata': self._metadata.copy(),
                'dimension': self.dimension
            }
        
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as f:
                pickle.dump(data, f)
            return True
        except Exception as e:
            print(f"Error saving index: {e}")
            return False
    
    def load(self, path: str) -> bool:
        """Wczytuje indeks z pliku."""
        if not os.path.exists(path):
            return False
        
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
            
            with self._lock:
                self._vectors = {k: np.array(v, dtype=np.float32) for k, v in data['vectors'].items()}
                self._metadata = data['metadata']
                self._dimension = data['dimension']
            
            return True
        except Exception as e:
            print(f"Error loading index: {e}")
            return False
    
    def clear(self) -> None:
        """Czysci indeks."""
        with self._lock:
            self._vectors.clear()
            self._metadata.clear()
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Oblicza podobienstwo kosinusowe."""
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        dot_product = np.dot(vec1, vec2)
        return float(dot_product / (norm1 * norm2))


# =============================================================================
# FAISS VECTOR INDEX BACKEND (OPCJONALNY)
# =============================================================================

class FAISSVectorIndexBackend(BaseVectorIndexBackend):
    """
    Backend indeksu wektorowego oparty na FAISS (Facebook AI Similarity Search).
    
    Wymaga: pip install faiss-cpu lub faiss-gpu
    
    Opcjonalny backend - znaczaco szybsze wyszukiwanie dla duzych datasetow.
    """
    
    def __init__(self, dimension: int = 384):
        self._dimension = dimension
        self._index = None
        self._vectors: Dict[str, np.ndarray] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._id_to_index: Dict[str, int] = {}
        self._index_to_id: Dict[int, str] = {}
        self._lock = threading.RLock()
        self._initialized = False
    
    def _initialize_index(self):
        """Inicjalizacja indeksu FAISS."""
        try:
            import faiss
            self._index = faiss.IndexFlatIP(self._dimension)
            self._initialized = True
        except ImportError:
            raise ImportError(
                "FAISS not installed. Please install: pip install faiss-cpu or faiss-gpu"
            )
    
    @property
    def index_type(self) -> str:
        return INDEX_TYPE_FAISS
    
    @property
    def size(self) -> int:
        with self._lock:
            return len(self._vectors)
    
    @property
    def dimension(self) -> int:
        return self._dimension
    
    def add_vector(
        self,
        vector_id: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Dodaje wektor do indeksu."""
        if len(embedding) != self.dimension:
            raise ValueError(f"Embedding dimension {len(embedding)} != {self.dimension}")
        
        with self._lock:
            if not self._initialized:
                self._initialize_index()
            
            vec = np.array(embedding, dtype=np.float32)
            
            # Normalizacja (FAISS preferuje znormalizowane wektory)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            
            # Dodaj do indeksu FAISS
            index = len(self._vectors)
            self._index.add(vec.reshape(1, -1))
            
            # Przechowuj lokalnie
            self._vectors[vector_id] = vec
            self._metadata[vector_id] = metadata or {}
            self._id_to_index[vector_id] = index
            self._index_to_id[index] = vector_id
        
        return True
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Wyszukuje najbardziej podobne wektory uzywajac FAISS.
        """
        if len(query_embedding) != self.dimension:
            raise ValueError(f"Query dimension {len(query_embedding)} != {self.dimension}")
        
        with self._lock:
            if not self._initialized or self._index is None:
                return []
            
            query_vec = np.array(query_embedding, dtype=np.float32)
            norm = np.linalg.norm(query_vec)
            if norm > 0:
                query_vec = query_vec / norm
            
            # Wyszukiwanie FAISS
            distances, indices = self._index.search(query_vec.reshape(1, -1), top_k)
            
            results = []
            for i in range(len(indices[0])):
                idx = indices[0][i]
                if idx in self._index_to_id:
                    vector_id = self._index_to_id[idx]
                    similarity = 1.0 - distances[0][i]  # Konwersja distance na similarity
                    results.append((vector_id, float(similarity)))
            
            return results
    
    def remove_vector(self, vector_id: str) -> bool:
        """
        Usuwa wektor z indeksu.
        
        Note: FAISS nie obsluguje bezposrednio usuniecia.
        Robimy to przez odbudowe indeksu (tylko dla malych datasetow).
        """
        with self._lock:
            if vector_id in self._vectors:
                del self._vectors[vector_id]
                if vector_id in self._metadata:
                    del self._metadata[vector_id]
                if vector_id in self._id_to_index:
                    del self._id_to_index[vector_id]
                
                # Odbuduj indeks (tylko jesli niewielki)
                if len(self._vectors) < 10000:
                    self._rebuild_index()
                
                return True
        return False
    
    def _rebuild_index(self):
        """Odbudowuje indeks FAISS."""
        if not self._initialized:
            self._initialize_index()
        
        self._index.reset()
        self._index_to_id.clear()
        
        vectors_list = []
        for vector_id, vec in self._vectors.items():
            vectors_list.append(vec)
            self._id_to_index[vector_id] = len(self._index_to_id)
            self._index_to_id[len(self._index_to_id)] = vector_id
        
        if vectors_list:
            vectors_array = np.array(vectors_list, dtype=np.float32)
            self._index.add(vectors_array)
    
    def get_vector(self, vector_id: str) -> Optional[List[float]]:
        """Pobiera wektor po ID."""
        with self._lock:
            if vector_id in self._vectors:
                return self._vectors[vector_id].tolist()
        return None
    
    def save(self, path: str) -> bool:
        """Zapisuje indeks do pliku."""
        with self._lock:
            data = {
                'vectors': {k: v.tolist() for k, v in self._vectors.items()},
                'metadata': self._metadata.copy(),
                'dimension': self.dimension
            }
        
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as f:
                pickle.dump(data, f)
            return True
        except Exception as e:
            print(f"Error saving FAISS index: {e}")
            return False
    
    def load(self, path: str) -> bool:
        """Wczytuje indeks z pliku."""
        if not os.path.exists(path):
            return False
        
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
            
            with self._lock:
                self._vectors = {k: np.array(v, dtype=np.float32) for k, v in data['vectors'].items()}
                self._metadata = data['metadata']
                self._dimension = data['dimension']
                self._rebuild_index()
            
            return True
        except Exception as e:
            print(f"Error loading FAISS index: {e}")
            return False
    
    def clear(self) -> None:
        """Czysci indeks."""
        with self._lock:
            self._vectors.clear()
            self._metadata.clear()
            self._id_to_index.clear()
            self._index_to_id.clear()
            if self._index is not None:
                self._index.reset()


# =============================================================================
# CHROMA DB BACKEND (PRZYSZLOŚĆ - OPCJONALNY)
# =============================================================================

class ChromaDBVectorIndexBackend(BaseVectorIndexBackend):
    """
    Backend indeksu wektorowego oparty na ChromaDB.
    
    Wymaga: pip install chromadb
    
    Opcjonalny backend - outpatient dla bardzo duzych datasetow.
    
    Note: Ta implementacja jest placeholder - ChromaDB wymaga oddzielnej
    konfiguracji i serwera. Zostanie zaimplementowana w przyszlosci.
    """
    
    def __init__(self, dimension: int = 384):
        self._dimension = dimension
        self._collection = None
        self._client = None
    
    @property
    def index_type(self) -> str:
        return INDEX_TYPE_CHROMA
    
    @property
    def size(self) -> int:
        if self._collection:
            return self._collection.count()
        return 0
    
    @property
    def dimension(self) -> int:
        return self._dimension
    
    def _initialize_client(self):
        """Inicjalizacja klienta ChromaDB."""
        try:
            import chromadb
            self._client = chromadb.PersistentClient(path="data/chroma_db")
            self._collection = self._client.get_or_create_collection(
                name="ssi_v5_collective_memory"
            )
        except ImportError:
            raise ImportError(
                "ChromaDB not installed. Please install: pip install chromadb"
            )
    
    def add_vector(
        self,
        vector_id: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Dodaje wektor do indeksu."""
        if len(embedding) != self.dimension:
            raise ValueError(f"Embedding dimension {len(embedding)} != {self.dimension}")
        
        if self._collection is None:
            self._initialize_client()
        
        self._collection.add(
            documents=[vector_id],
            embeddings=[embedding],
            metadatas=[metadata or {}],
            ids=[vector_id]
        )
        return True
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """Wyszukuje najbardziej podobne wektory."""
        if self._collection is None:
            self._initialize_client()
        
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Konwersja wynikow
        output = []
        for i in range(len(results['ids'][0])):
            vector_id = results['ids'][0][i]
            similarity = 1.0 - results['distances'][0][i]  # Konwersja distance na similarity
            output.append((vector_id, similarity))
        
        return output
    
    def remove_vector(self, vector_id: str) -> bool:
        """Usuwa wektor z indeksu."""
        if self._collection is None:
            self._initialize_client()
        
        self._collection.delete(ids=[vector_id])
        return True
    
    def get_vector(self, vector_id: str) -> Optional[List[float]]:
        """Pobiera wektor po ID."""
        # ChromaDB nie obsluguje bezposrednio pobierania po ID
        # To jest uproszczone
        return None
    
    def save(self, path: str) -> bool:
        """ChromaDB automatycznie persystuje dane."""
        return True
    
    def load(self, path: str) -> bool:
        """Inicjalizacja laduje dane z domyslnej lokalizacji."""
        try:
            self._initialize_client()
            return True
        except:
            return False
    
    def clear(self) -> None:
        """Czysci indeks."""
        if self._collection is None:
            self._initialize_client()
        
        # Usuwa wszystko (tylko dla testow)
        self._client.delete_collection("ssi_v5_collective_memory")
        self._collection = None


# =============================================================================
# GLOWNA KLASA VectorIndex
# =============================================================================

class VectorIndex:
    """
    Glowny indeks wektorowy dla Collective Memory.
    
    Uzywa wybranego backend do indeksowania i wyszukiwania wektorow.
    
    Obsluguje:
    - Dodawanie wektorow z dokumentami
    - Wyszukiwanie podobnych wektorow
    - Usuwanie wektorow
    - Persystencja na dysku
    
    Usage:
        index = VectorIndex()  # Domy wanty numpy
        
        # Dodaj dokument
        doc = CollectiveMemoryDocument(...)
        embedding = generator.generate_document(doc)
        index.add(doc, embedding)
        
        # Wyszukaj podobne
        results = index.search(query_embedding, top_k=5)
        
        # Persystencja
        index.save("path/to/index")
    """
    
    # Dostepne typy indeksow
    INDEX_TYPE_NUMPY = INDEX_TYPE_NUMPY
    INDEX_TYPE_FAISS = INDEX_TYPE_FAISS
    INDEX_TYPE_CHROMA = INDEX_TYPE_CHROMA
    
    def __init__(
        self,
        config: Optional[VectorIndexConfig] = None,
        embedding_generator: Optional[EmbeddingGenerator] = None
    ):
        """
        Inicjalizacja indeksu.
        
        Args:
            config: Konfiguracja indeksu
            embedding_generator: Generator embeddingow (opcjonalny)
        """
        self.config = config or VectorIndexConfig()
        self.embedding_generator = embedding_generator
        
        # Inicjalizacja backend
        self._backend = self._create_backend()
        
        # Lokalne przechowywanie dokumentow
        self._documents: Dict[str, CollectiveMemoryDocument] = {}
        self._lock = threading.RLock()
        
        # Statystyki
        self._add_count = 0
        self._search_count = 0
    
    def _create_backend(self) -> BaseVectorIndexBackend:
        """Tworzy backend na podstawie konfiguracji."""
        if self.config.index_type == self.INDEX_TYPE_FAISS:
            return FAISSVectorIndexBackend(dimension=self.config.dimension)
        elif self.config.index_type == self.INDEX_TYPE_CHROMA:
            return ChromaDBVectorIndexBackend(dimension=self.config.dimension)
        else:
            return NumpyVectorIndexBackend(dimension=self.config.dimension)
    
    @property
    def backend_type(self) -> str:
        """Typ uzywanego backend."""
        return self._backend.index_type
    
    @property
    def size(self) -> int:
        """Liczba zindeksowanych wektorow."""
        return self._backend.size
    
    @property
    def dimension(self) -> int:
        """Rozmiar wektorow."""
        return self._backend.dimension
    
    # ========================================================================
    # METODY GLÓWNE
    # ========================================================================
    
    def add(
        self,
        document: CollectiveMemoryDocument,
        embedding: Optional[EmbeddingResult] = None
    ) -> IndexedVector:
        """
        Dodaje dokument z jego embeddingiem do indeksu.
        
        Args:
            document: Dokument pamieci
            embedding: Embedding (opcjonalny - moze zostac wygenerowany automatycznie)
            
        Returns:
            IndexedVector
        """
        # Generuj embedding jesli nie podano
        if embedding is None:
            if self.embedding_generator is None:
                raise ValueError("Embedding or embedding_generator required")
            embedding = self.embedding_generator.generate_document(document)
        
        # Walidacja
        if not embedding.validate():
            raise ValueError(f"Invalid embedding for document {document.document_id}")
        
        with self._lock:
            # Dodaj do backend
            self._backend.add_vector(
                vector_id=document.document_id,
                embedding=embedding.embedding,
                metadata={
                    'source_id': document.source_id,
                    'source_type': document.source_type,
                    'importance': document.importance,
                    'tags': document.tags,
                    'timestamp': document.timestamp.isoformat()
                }
            )
            
            # Przechowaj dokument lokalnie
            self._documents[document.document_id] = document
            self._add_count += 1
        
        return IndexedVector(
            vector_id=document.document_id,
            embedding=embedding.embedding,
            document=document,
            metadata=embedding.metadata,
            timestamp=datetime.now()
        )
    
    def add_batch(
        self,
        documents: List[CollectiveMemoryDocument],
        embeddings: Optional[List[EmbeddingResult]] = None
    ) -> List[IndexedVector]:
        """
        Dodaje wiele dokumentow do indeksu.
        
        Args:
            documents: Lista dokumentow
            embeddings: Lista embeddingow (opcjonalna)
            
        Returns:
            Lista IndexedVector
        """
        if embeddings is None:
            if self.embedding_generator is None:
                raise ValueError("Embeddings or embedding_generator required")
            embeddings = self.embedding_generator.generate_documents_batch(documents)
        
        results = []
        for doc, emb in zip(documents, embeddings):
            results.append(self.add(doc, emb))
        
        return results
    
    def search(
        self,
        query_embedding: Union[List[float], EmbeddingResult],
        top_k: int = 10
    ) -> List[SearchResult]:
        """
        Wyszukuje najbardziej podobne dokumenty.
        
        Args:
            query_embedding: Wektor zapytania (lista float lub EmbeddingResult)
            top_k: Liczba wynikow
            
        Returns:
            Lista SearchResult
        """
        if isinstance(query_embedding, EmbeddingResult):
            query_vec = query_embedding.embedding
        else:
            query_vec = query_embedding
        
        if len(query_vec) != self.dimension:
            raise ValueError(f"Query dimension {len(query_vec)} != {self.dimension}")
        
        with self._lock:
            # Wyszukaj w backend
            backend_results = self._backend.search(query_vec, top_k)
            
            # Konwersja na SearchResult
            results = []
            for rank, (vector_id, similarity) in enumerate(backend_results):
                metadata = self._backend._metadata.get(vector_id, {})
                
                result = SearchResult(
                    vector_id=vector_id,
                    similarity=similarity,
                    embedding=self._get_embedding(vector_id),
                    document=self._documents.get(vector_id),
                    metadata=metadata,
                    rank=rank
                )
                results.append(result)
            
            self._search_count += 1
        
        return results
    
    def search_by_text(
        self,
        query_text: str,
        top_k: int = 10
    ) -> List[SearchResult]:
        """
        Wyszukuje najbardziej podobne dokumenty na podstawie tekstu zapytania.
        
        Args:
            query_text: Tekst zapytania
            top_k: Liczba wynikow
            
        Returns:
            Lista SearchResult
        """
        if self.embedding_generator is None:
            raise ValueError("Embedding generator required for text search")
        
        query_embedding = self.embedding_generator.generate(query_text)
        return self.search(query_embedding, top_k)
    
    def search_by_document(
        self,
        document: CollectiveMemoryDocument,
        top_k: int = 10
    ) -> List[SearchResult]:
        """
        Wyszukuje najbardziej podobne dokumenty do podanego dokumentu.
        
        Args:
            document: Dokument zapytania
            top_k: Liczba wynikow
            
        Returns:
            Lista SearchResult
        """
        if self.embedding_generator is None:
            raise ValueError("Embedding generator required for document search")
        
        query_embedding = self.embedding_generator.generate_document(document)
        return self.search(query_embedding, top_k)
    
    def remove(self, vector_id: str) -> bool:
        """
        Usuwa dokument z indeksu.
        
        Args:
            vector_id: ID dokumentu do usuniecia
            
        Returns:
            True jesli usunieto pomyslnie
        """
        with self._lock:
            result = self._backend.remove_vector(vector_id)
            if result and vector_id in self._documents:
                del self._documents[vector_id]
            return result
    
    def get(self, vector_id: str) -> Optional[CollectiveMemoryDocument]:
        """
        Pobiera dokument po ID.
        
        Args:
            vector_id: ID dokumentu
            
        Returns:
            Dokument lub None
        """
        with self._lock:
            return self._documents.get(vector_id)
    
    def get_embedding(self, vector_id: str) -> Optional[List[float]]:
        """
        Pobiera wektor po ID.
        
        Args:
            vector_id: ID wektora
            
        Returns:
            Wektor lub None
        """
        return self._backend.get_vector(vector_id)
    
    def _get_embedding(self, vector_id: str) -> Optional[List[float]]:
        """Wewnetzna metoda do pobierania embeddingu."""
        return self._backend.get_vector(vector_id)
    
    def update(
        self,
        document: CollectiveMemoryDocument,
        new_embedding: Optional[EmbeddingResult] = None
    ) -> bool:
        """
        Aktualizuje dokument w indeksie.
        
        Args:
            document: Dokument do zaktualizowania
            new_embedding: Nowy embedding (opcjonalny)
            
        Returns:
            True jesli zaktualizowano pomyslnie
        """
        if new_embedding is None:
            if self.embedding_generator is None:
                raise ValueError("Embedding or embedding_generator required")
            new_embedding = self.embedding_generator.generate_document(document)
        
        with self._lock:
            # Zaktualizuj wektor
            result = self._backend.update_vector(
                vector_id=document.document_id,
                new_embedding=new_embedding.embedding,
                new_metadata={
                    'source_id': document.source_id,
                    'source_type': document.source_type,
                    'importance': document.importance,
                    'tags': document.tags,
                    'timestamp': document.timestamp.isoformat()
                }
            )
            
            # Zaktualizuj dokument
            self._documents[document.document_id] = document
            
            return result
    
    # ========================================================================
    # PERSYSTENCJA
    # ========================================================================
    
    def save(self, path: Optional[str] = None) -> bool:
        """
        Zapisuje indeks do pliku.
        
        Args:
            path: Sciezka do zapisu (domyslnie z konfiguracji)
            
        Returns:
            True jesli zapisano pomyslnie
        """
        path = path or self.config.storage_path
        
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Zapis indeksu backend
            backend_path = f"{path}.backend"
            self._backend.save(backend_path)
            
            # Zapis dokumentow
            docs_path = f"{path}.documents"
            with open(docs_path, 'w', encoding='utf-8') as f:
                docs_data = {k: v.to_dict() for k, v in self._documents.items()}
                json.dump(docs_data, f, ensure_ascii=False, indent=2)
            
            # Zapis konfiguracji
            config_path = f"{path}.config"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config.to_dict(), f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving index: {e}")
            return False
    
    def load(self, path: Optional[str] = None) -> bool:
        """
        Wczytuje indeks z pliku.
        
        Args:
            path: Sciezka do pliku (domyslnie z konfiguracji)
            
        Returns:
            True jesli wczytano pomyslnie
        """
        path = path or self.config.storage_path
        
        try:
            # Wczytanie indeksu backend
            backend_path = f"{path}.backend"
            if os.path.exists(backend_path):
                self._backend.load(backend_path)
            
            # Wczytanie dokumentow
            docs_path = f"{path}.documents"
            if os.path.exists(docs_path):
                with open(docs_path, 'r', encoding='utf-8') as f:
                    docs_data = json.load(f)
                    self._documents = {
                        k: CollectiveMemoryDocument.from_dict(v)
                        for k, v in docs_data.items()
                    }
            
            # Wczytanie konfiguracji
            config_path = f"{path}.config"
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self.config = VectorIndexConfig.from_dict(config_data)
            
            return True
        except Exception as e:
            print(f"Error loading index: {e}")
            return False
    
    def clear(self) -> None:
        """Czysci caly indeks."""
        with self._lock:
            self._backend.clear()
            self._documents.clear()
            self._add_count = 0
            self._search_count = 0
    
    # ========================================================================
    # STATYSTYKI
    # ========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Zwraca statystyki indeksu."""
        return {
            'size': self.size,
            'backend_type': self.backend_type,
            'dimension': self.dimension,
            'add_count': self._add_count,
            'search_count': self._search_count,
            'documents_count': len(self._documents)
        }


# =============================================================================
# FABRYKA
# =============================================================================

def create_vector_index(
    index_type: str = INDEX_TYPE_NUMPY,
    dimension: int = 384,
    storage_path: str = "data/collective_memory_index",
    auto_save: bool = True,
    embedding_generator: Optional[EmbeddingGenerator] = None
) -> VectorIndex:
    """
    Fabryka VectorIndex.
    
    Args:
        index_type: Typ indeksu (numpy, faiss, chroma)
        dimension: Rozmiar wektorow
        storage_path: Sciezka do przechowywania
        auto_save: Czy automatycznie zapisywac
        embedding_generator: Generator embeddingow
        
    Returns:
        VectorIndex
    """
    config = VectorIndexConfig(
        index_type=index_type,
        storage_path=storage_path,
        dimension=dimension,
        auto_save=auto_save
    )
    
    return VectorIndex(config=config, embedding_generator=embedding_generator)
