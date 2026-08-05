"""
SSI V5 - Embedding Generator
ETAP: 5.4.1 - Memory Embedding Foundation

Odpowiedzialnosc:
- Generowanie embeddingow (wektorow) dla tekstow i dokumentow pamieci
- Interfejs gotowy pod rozne backendy:
  * Mock/Lokalne embeddinge (domyslnie)
  * Sentence Transformers (sentence-transformers)
  * Zewnetrzne API (OpenAI, etc.)
  * Lokalne modele LLM

ZASADY:
1. Interfejs abstrakcyjny - Mozliwosc wymiany backendow
2. Domy Rzeczywiste mockowe embeddinge do testow
3. NIE zaleznosc od zewnetrznych API w bazowej implementacji
4. Cache embeddingow dla wydajnosci
5. Dolaczona walidacja wektorow

Architektura:
    EmbeddingGenerator (Iterator)
        |
    +-- BaseEmbeddingBackend (Abstrakcyjny)
        |
        +-- MockEmbeddingBackend (Domy wanty)
        +-- SentenceTransformerBackend (Opcjonalny)
        +-- APIEmbeddingBackend (Opcjonalny)

Autor: SSI V5 System / Mistral Vibe
Data: 2026-08-04
Wersja: 1.0.0
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union, Tuple
import numpy as np
import hashlib
import json
from datetime import datetime
import threading

from .memory_document_adapter import CollectiveMemoryDocument


# Rozmiar wektora (domyslnie 384 - MiniLM-L6-v2)
DEFAULT_EMBEDDING_DIM = 384


@dataclass
class EmbeddingResult:
    """
    Wynik generowania embeddingu.
    
    Attributes:
        document_id: ID dokumentu
        embedding: Wektor jako lista float
        model_name: Nazwa modelu uzytego do generacji
        dimension: Rozmiar wektora
        timestamp: Czas generacji
        metadata: Dodatkowe metadane
    """
    document_id: str
    embedding: List[float]
    model_name: str = "mock"
    dimension: int = DEFAULT_EMBEDDING_DIM
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Walidacja
    def validate(self) -> bool:
        """Waliduje poprawnosc embeddingu."""
        if not self.embedding:
            return False
        if len(self.embedding) != self.dimension:
            return False
        if not all(isinstance(x, (int, float)) for x in self.embedding):
            return False
        return True
    
    def to_numpy(self) -> np.ndarray:
        """Konwersja do numpy array."""
        return np.array(self.embedding, dtype=np.float32)
    
    def normalized(self) -> List[float]:
        """Zwraca znormalizowany wektor (L2 norm)."""
        vec = np.array(self.embedding, dtype=np.float32)
        norm = np.linalg.norm(vec)
        if norm == 0:
            return self.embedding
        return (vec / norm).tolist()
    
    def similarity(self, other: 'EmbeddingResult') -> float:
        """Oblicza podobienstwo kosinusowe z innym embeddingiem."""
        if len(self.embedding) != len(other.embedding):
            raise ValueError(f"Embeddings have different dimensions: {len(self.embedding)} vs {len(other.embedding)}")
        
        vec_a = np.array(self.embedding, dtype=np.float32)
        vec_b = np.array(other.embedding, dtype=np.float32)
        
        # Normalizacja
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        # Iloczyn skalarny / (norm_a * norm_b)
        dot_product = np.dot(vec_a, vec_b)
        cosine_similarity = dot_product / (norm_a * norm_b)
        
        return float(cosine_similarity)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do dict."""
        return {
            'document_id': self.document_id,
            'embedding': self.embedding,
            'model_name': self.model_name,
            'dimension': self.dimension,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmbeddingResult':
        """Konwersja z dict."""
        data = data.copy()
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class EmbeddingCache:
    """
    Cache embeddingow dla wydajnosci.
    
    Uzywa MD5 hash tekstu jako klucz.
    """
    max_size: int = 10000  # Maksymalna liczba wpisow
    ttl_seconds: int = 3600  # Czas zycia wpisu (1 godzina)
    
    def __init__(self, max_size: int = 10000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Tuple[EmbeddingResult, datetime]] = {}
        self._lock = threading.RLock()
    
    def get(self, text: str) -> Optional[EmbeddingResult]:
        """Pobiera embedding z cache."""
        cache_key = self._generate_cache_key(text)
        
        with self._lock:
            if cache_key in self._cache:
                embedding, timestamp = self._cache[cache_key]
                
                # Sprawdz TTL
                if (datetime.now() - timestamp).total_seconds() < self.ttl_seconds:
                    return embedding
                else:
                    # Usun przeterminowany
                    del self._cache[cache_key]
        
        return None
    
    def set(self, text: str, embedding: EmbeddingResult):
        """Zapisuje embedding do cache."""
        cache_key = self._generate_cache_key(text)
        
        with self._lock:
            # Sprawdz limit rozmiaru
            if len(self._cache) >= self.max_size:
                self._evict_oldest()
            
            self._cache[cache_key] = (embedding, datetime.now())
    
    def _generate_cache_key(self, text: str) -> str:
        """Generuje klucz cache z tekstu."""
        # Uzyj MD5 hash
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _evict_oldest(self):
        """Usuwa najstarszy wpis (FIFO)."""
        if not self._cache:
            return
        
        # Znajdz najstarszy
        oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
        del self._cache[oldest_key]
    
    def clear(self):
        """Czysci cache."""
        with self._lock:
            self._cache.clear()
    
    def size(self) -> int:
        """Zwraca rozmiar cache."""
        with self._lock:
            return len(self._cache)


# =============================================================================
# ABSTRAKCYJNY BACKEND DLA EMBEDDING
# =============================================================================

class BaseEmbeddingBackend(ABC):
    """
    Abstrakcyjna klasa backend dla generowania embeddingow.
    
    Kazdy backend musi implementowac:
    - generate_embedding(text) -> List[float]
    - generate_batch(texts) -> List[List[float]]
    - model_name: str
    - dimension: int
    """
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Nazwa modelu."""
        pass
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Rozmiar wektora."""
        pass
    
    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generuje embedding dla pojedynczego tekstu.
        
        Args:
            text: Tekst do zakodowania
            
        Returns:
            Wektor jako lista float
        """
        pass
    
    @abstractmethod
    def generate_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generuje embeddingi dla wielu tekstow (bardziej wydajne).
        
        Args:
            texts: Lista tekstow do zakodowania
            
        Returns:
            Lista wektorow (jeden wektor na tekst)
        """
        pass
    
    def validate_embedding(self, embedding: List[float]) -> bool:
        """Waliduje poprawnosc wektora."""
        if len(embedding) != self.dimension:
            return False
        if not all(isinstance(x, (int, float)) for x in embedding):
            return False
        return True


# =============================================================================
# MOCK EMBEDDING BACKEND (DOMYSLNY)
# =============================================================================

class MockEmbeddingBackend(BaseEmbeddingBackend):
    """
    Mock backend generujacy losowe embeddinge.
    
    Uzywany jako domyslny backend bez zewnetrznych zaleznosci.
    Generuje powtarzalne embeddinge na podstawie hash tekstu.
    """
    
    def __init__(self, dimension: int = DEFAULT_EMBEDDING_DIM, seed: int = 42):
        self._dimension = dimension
        self._seed = seed
    
    @property
    def model_name(self) -> str:
        return "mock-v1"
    
    @property
    def dimension(self) -> int:
        return self._dimension
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generuje powtarzalny mock embedding.
        
        Uzywa hash tekstu jako seed do generacji Deterministyczny.
        """
        # Uzyj hash tekstu jako seed (zabezpieczenie przed ujemnymi wartosciami)
        text_hash = hash(text)
        # Zapewnij ze seed jest dodatni i w zakresie 0-2^32-1
        seed = abs(text_hash) % (2**32)
        np.random.seed(seed)
        
        # Generuj losowy wektor w zakresie [-1, 1]
        embedding = np.random.uniform(-1, 1, self.dimension).tolist()
        
        # Normalizacja (opcjonalnie)
        embedding = self._normalize(embedding)
        
        return embedding
    
    def generate_batch(self, texts: List[str]) -> List[List[float]]:
        """Generuje embeddinge dla wielu tekstow."""
        return [self.generate_embedding(text) for text in texts]
    
    def _normalize(self, embedding: List[float]) -> List[float]:
        """Normalizuje wektor do dlugosci 1."""
        vec = np.array(embedding, dtype=np.float32)
        norm = np.linalg.norm(vec)
        if norm == 0:
            return embedding
        return (vec / norm).tolist()


# =============================================================================
# SENTENCE TRANSFORMERS BACKEND (OPCJONALNY)
# =============================================================================

class SentenceTransformerBackend(BaseEmbeddingBackend):
    """
    Backend uzywajacy Sentence Transformers.
    
    Wymaga: pip install sentence-transformers
    
    Opcjonalny backend - nie jest wymagany do dzialania systemu.
    """
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self._model_name = model_name
        self._model = None
        self._dimension = self._get_model_dimension(model_name)
        self._initialize_model()
    
    def _get_model_dimension(self, model_name: str) -> int:
        """Zwraca rozmiar wektora dla modelu."""
        # Znane modele i ich rozmiary
        known_models = {
            "sentence-transformers/all-mpnet-base-v2": 768,
            "sentence-transformers/all-MiniLM-L6-v2": 384,
            "sentence-transformers/all-MiniLM-L12-v2": 384,
            "sentence-transformers/multi-qa-mpnet-base-dot-v1": 768,
        }
        return known_models.get(model_name, DEFAULT_EMBEDDING_DIM)
    
    def _initialize_model(self):
        """Inicjalizacja modelu (lazy loading)."""
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self._model_name)
        except ImportError:
            raise ImportError(
                f"Sentence Transformers not installed. "
                f"Please install: pip install sentence-transformers"
            )
    
    @property
    def model_name(self) -> str:
        return self._model_name
    
    @property
    def dimension(self) -> int:
        return self._dimension
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generuje embedding uzywajac Sentence Transformers."""
        if self._model is None:
            self._initialize_model()
        
        embedding = self._model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    def generate_batch(self, texts: List[str]) -> List[List[float]]:
        """Generuje embeddinge dla wielu tekstow."""
        if self._model is None:
            self._initialize_model()
        
        embeddings = self._model.encode(texts, convert_to_tensor=False)
        return embeddings.tolist()


# =============================================================================
# EMBEDDING GENERATOR (GLOWNA KLASA)
# =============================================================================

class EmbeddingGenerator:
    """
    Glowny generator embeddingow dla systemu Collective Memory.
    
    Uzywa wybranego backend do generowania embeddingow.
    Obsluguje:
    - Pojedyncze teksty
    - Dokumenty pamieci (CollectiveMemoryDocument)
    - Batch processing
    - Cache embeddingow
    
    Usage:
        generator = EmbeddingGenerator()  # Domy wanty Mock
        
        # Pojedynczy tekst
        embedding = generator.generate("Sample text")
        
        # Dokument pamieci
        doc = CollectiveMemoryDocument(...)
        embedding = generator.generate_document(doc)
        
        # Batch
        texts = ["text1", "text2", "text3"]
        embeddings = generator.generate_batch(texts)
    """
    
    # Dostepne backendy
    BACKEND_MOCK = "mock"
    BACKEND_SENTENCE_TRANSFORMERS = "sentence-transformers"
    
    def __init__(
        self,
        backend: str = BACKEND_MOCK,
        model_name: Optional[str] = None,
        cache_config: Optional[Dict[str, Any]] = None,
        dimension: Optional[int] = None
    ):
        """
        Inicjalizacja generatora.
        
        Args:
            backend: Typ backend (mock, sentence-transformers)
            model_name: Nazwa modelu (dla ST backend)
            cache_config: Konfiguracja cache
            dimension: Rozmiar wektora (domyslnie 384)
        """
        self.backend_name = backend
        self.dimension = dimension or DEFAULT_EMBEDDING_DIM
        
        # Inicjalizacja backend
        self._backend = self._create_backend(backend, model_name, self.dimension)
        
        # Inicjalizacja cache
        cache_config = cache_config or {}
        self._cache = EmbeddingCache(
            max_size=cache_config.get('max_size', 10000),
            ttl_seconds=cache_config.get('ttl_seconds', 3600)
        )
    
    def _create_backend(
        self,
        backend: str,
        model_name: Optional[str],
        dimension: int
    ) -> BaseEmbeddingBackend:
        """Tworzy backend na podstawie nazwy."""
        if backend == self.BACKEND_MOCK:
            return MockEmbeddingBackend(dimension=dimension)
        elif backend == self.BACKEND_SENTENCE_TRANSFORMERS:
            return SentenceTransformerBackend(
                model_name=model_name or self._get_default_st_model()
            )
        else:
            raise ValueError(f"Unknown backend: {backend}")
    
    def _get_default_st_model(self) -> str:
        """Zwraca domyslny model ST."""
        return "sentence-transformers/all-MiniLM-L6-v2"
    
    @property
    def model_name(self) -> str:
        """Nazwa modelu."""
        return self._backend.model_name
    
    @property
    def backend(self) -> BaseEmbeddingBackend:
        """Aktualny backend."""
        return self._backend
    
    # ========================================================================
    # METODY GENERACJI
    # ========================================================================
    
    def generate(self, text: str, use_cache: bool = True) -> EmbeddingResult:
        """
        Generuje embedding dla tekstu.
        
        Args:
            text: Tekst do zakodowania
            use_cache: Czy uzyc cache
            
        Returns:
            EmbeddingResult
        """
        # Sprawdz cache
        if use_cache:
            cached = self._cache.get(text)
            if cached:
                return cached
        
        # Generuj embedding
        embedding = self._backend.generate_embedding(text)
        
        # Walidacja
        if not self._backend.validate_embedding(embedding):
            raise ValueError(f"Invalid embedding generated by {self.model_name}")
        
        # Tworz wynik
        result = EmbeddingResult(
            document_id=self._generate_document_id(text),
            embedding=embedding,
            model_name=self.model_name,
            dimension=self.dimension,
            metadata={'backend': self.backend_name}
        )
        
        #Cache
        if use_cache:
            self._cache.set(text, result)
        
        return result
    
    def generate_document(
        self,
        document: CollectiveMemoryDocument,
        use_cache: bool = True
    ) -> EmbeddingResult:
        """
        Generuje embedding dla dokumentu pamieci.
        
        Uzywa dokumentu.text jako tekstu wejsciowego.
        
        Args:
            document: Dokument pamieci
            use_cache: Czy uzyc cache
            
        Returns:
            EmbeddingResult
        """
        return self.generate(document.text, use_cache=use_cache)
    
    def generate_batch(
        self,
        texts: List[str],
        use_cache: bool = True
    ) -> List[EmbeddingResult]:
        """
        Generuje embeddinge dla wielu tekstow.
        
        Args:
            texts: Lista tekstow
            use_cache: Czy uzyc cache
            
        Returns:
            Lista EmbeddingResult
        """
        # Sprawdz cache
        results = []
        uncached_texts = []
        uncached_indices = []
        
        for i, text in enumerate(texts):
            if use_cache:
                cached = self._cache.get(text)
                if cached:
                    results.append(cached)
                    continue
            
            uncached_texts.append(text)
            uncached_indices.append(i)
        
        # Generuj embeddinge dla.textow bez cache
        if uncached_texts:
            batch_embeddings = self._backend.generate_batch(uncached_texts)
            
            for j, embedding in enumerate(batch_embeddings):
                text = uncached_texts[j]
                index = uncached_indices[j]
                
                result = EmbeddingResult(
                    document_id=self._generate_document_id(text),
                    embedding=embedding,
                    model_name=self.model_name,
                    dimension=self.dimension,
                    metadata={'backend': self.backend_name}
                )
                
                results.insert(index, result)
                
                if use_cache:
                    self._cache.set(text, result)
        
        return results
    
    def generate_documents_batch(
        self,
        documents: List[CollectiveMemoryDocument],
        use_cache: bool = True
    ) -> List[EmbeddingResult]:
        """
        Generuje embeddinge dla wielu dokumentow.
        
        Args:
            documents: Lista dokumentow pamieci
            use_cache: Czy uzyc cache
            
        Returns:
            Lista EmbeddingResult
        """
        texts = [doc.text for doc in documents]
        return self.generate_batch(texts, use_cache=use_cache)
    
    # ========================================================================
    # METODY UTILITY
    # ========================================================================
    
    def _generate_document_id(self, text: str) -> str:
        """Generuje ID dokumentu z tekstu."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()[:12]
    
    def calculate_similarity(
        self,
        text1: str,
        text2: str
    ) -> float:
        """
        Oblicza podobienstwo kosinusowe pomiedzy dwoma tekstami.
        
        Args:
            text1: Pierwszy tekst
            text2: Drugi tekst
            
        Returns:
            Podobienstwo w zakresie [-1, 1] ('im wyzsze tym bardziej podobne)
        """
        emb1 = self.generate(text1, use_cache=True)
        emb2 = self.generate(text2, use_cache=True)
        return emb1.similarity(emb2)
    
    def calculate_similarities(
        self,
        query_text: str,
        target_texts: List[str]
    ) -> List[float]:
        """
        Oblicza podobienstwa pomiedzy tekstem zapytania a lista tekstow docelowych.
        
        Args:
            query_text: Tekst zapytania
            target_texts: Lista tekstow docelowych
            
        Returns:
            Lista podobienstw
        """
        query_emb = self.generate(query_text, use_cache=True)
        
        similarities = []
        for target_text in target_texts:
            target_emb = self.generate(target_text, use_cache=True)
            similarities.append(query_emb.similarity(target_emb))
        
        return similarities
    
    def clear_cache(self):
        """Czysci cache embeddingow."""
        self._cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Zwraca statystyki cache."""
        return {
            'size': self._cache.size(),
            'max_size': self._cache.max_size,
            'ttl_seconds': self._cache.ttl_seconds
        }


# =============================================================================
# FABRYKA
# =============================================================================

def create_embedding_generator(
    backend: str = EmbeddingGenerator.BACKEND_MOCK,
    model_name: Optional[str] = None,
    **kwargs
) -> EmbeddingGenerator:
    """
    Fabryka EmbeddingGenerator.
    
    Args:
        backend: Typ backend
        model_name: Nazwa modelu
        **kwargs: Dodatkowe argumenty dla generatora
        
    Returns:
        EmbeddingGenerator
    """
    return EmbeddingGenerator(
        backend=backend,
        model_name=model_name,
        **kwargs
    )


# =============================================================================
# UTYLITY
# =============================================================================

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Oblicza podobienstwo kosinusowe pomiedzy dwoma wektorami.
    
    Args:
        vec1: Pierwszy wektor
        vec2: Drugi wektor
        
    Returns:
        Podobienstwo w zakresie [-1, 1]
    """
    if len(vec1) != len(vec2):
        raise ValueError(f"Vectors have different dimensions: {len(vec1)} vs {len(vec2)}")
    
    a = np.array(vec1, dtype=np.float32)
    b = np.array(vec2, dtype=np.float32)
    
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    dot_product = np.dot(a, b)
    return float(dot_product / (norm_a * norm_b))


def euclidean_distance(vec1: List[float], vec2: List[float]) -> float:
    """
    Oblicza odleglosc euklidesowa pomiedzy dwoma wektorami.
    
    Args:
        vec1: Pierwszy wektor
        vec2: Drugi wektor
        
    Returns:
        Odleglosc euklidesowa
    """
    if len(vec1) != len(vec2):
        raise ValueError(f"Vectors have different dimensions: {len(vec1)} vs {len(vec2)}")
    
    a = np.array(vec1, dtype=np.float32)
    b = np.array(vec2, dtype=np.float32)
    
    return float(np.linalg.norm(a - b))


def dot_product(vec1: List[float], vec2: List[float]) -> float:
    """
    Oblicza iloczyn skalarny pomiedzy dwoma wektorami.
    
    Args:
        vec1: Pierwszy wektor
        vec2: Drugi wektor
        
    Returns:
        Iloczyn skalarny
    """
    if len(vec1) != len(vec2):
        raise ValueError(f"Vectors have different dimensions: {len(vec1)} vs {len(vec2)}")
    
    return float(np.dot(vec1, vec2))
