"""
SSI V5 - Testy Vector Index
ETAP: 5.4.1 - Memory Embedding Foundation

Testy jednostkowe dla VectorIndex i backendow.

Zakres testow:
1. NumpyVectorIndexBackend
2. VectorIndex
3. IndexedVector
4. SearchResult
5. Persystencja
6. Batch operations

Autor: SSI V5 System / Mistral Vibe
Data: 2026-08-04
Wersja: 1.0.0
"""

import unittest
import tempfile
import shutil
import os
import numpy as np
from datetime import datetime

# Import klas do testow
from SSI_V5.memory.collective_memory.vector_index import (
    VectorIndex,
    VectorIndexConfig,
    IndexedVector,
    SearchResult,
    BaseVectorIndexBackend,
    NumpyVectorIndexBackend,
    FAISSVectorIndexBackend,
    ChromaDBVectorIndexBackend,
    create_vector_index,
    INDEX_TYPE_NUMPY,
    INDEX_TYPE_FAISS,
    INDEX_TYPE_CHROMA
)
from SSI_V5.memory.collective_memory.embedding_generator import (
    EmbeddingGenerator,
    EmbeddingResult
)
from SSI_V5.memory.collective_memory.memory_document_adapter import (
    CollectiveMemoryDocument
)


# =============================================================================
# TESTY VectorIndexConfig
# =============================================================================

class TestVectorIndexConfig(unittest.TestCase):
    """Testy konfiguracji VectorIndex."""
    
    def test_default_config(self):
        """Test domyslnej konfiguracji."""
        config = VectorIndexConfig()
        
        self.assertEqual(config.index_type, INDEX_TYPE_NUMPY)
        self.assertEqual(config.dimension, 384)
        self.assertEqual(config.max_size, 100000)
        self.assertTrue(config.auto_save)
    
    def test_custom_config(self):
        """Test niestandardowej konfiguracji."""
        config = VectorIndexConfig(
            index_type=INDEX_TYPE_FAISS,
            storage_path="/tmp/test",
            dimension=768,
            max_size=50000,
            auto_save=False
        )
        
        self.assertEqual(config.index_type, INDEX_TYPE_FAISS)
        self.assertEqual(config.storage_path, "/tmp/test")
        self.assertEqual(config.dimension, 768)
        self.assertEqual(config.max_size, 50000)
        self.assertFalse(config.auto_save)
    
    def test_serialization(self):
        """Test serializacji konfiguracji."""
        config = VectorIndexConfig(
            index_type=INDEX_TYPE_NUMPY,
            dimension=384
        )
        
        data = config.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['index_type'], INDEX_TYPE_NUMPY)
        
        restored = VectorIndexConfig.from_dict(data)
        self.assertEqual(restored.index_type, config.index_type)
        self.assertEqual(restored.dimension, config.dimension)


# =============================================================================
# TESTY IndexedVector
# =============================================================================

class TestIndexedVector(unittest.TestCase):
    """Testy klasy IndexedVector."""
    
    def test_create_indexed_vector(self):
        """Test tworzenia IndexedVector."""
        doc = CollectiveMemoryDocument(
            source_id="test_001",
            source_type="strategy_memory",
            text="Test content"
        )
        
        vector = IndexedVector(
            vector_id="vec_001",
            embedding=[0.1, 0.2, 0.3],
            document=doc,
            metadata={"key": "value"}
        )
        
        self.assertEqual(vector.vector_id, "vec_001")
        self.assertEqual(vector.embedding, [0.1, 0.2, 0.3])
        self.assertEqual(vector.document, doc)
        self.assertEqual(vector.metadata, {"key": "value"})
        self.assertIsInstance(vector.timestamp, datetime)
    
    def test_indexed_vector_serialization(self):
        """Test serializacji IndexedVector."""
        doc = CollectiveMemoryDocument(
            source_id="test_001",
            text="Test content"
        )
        
        vector = IndexedVector(
            vector_id="vec_001",
            embedding=[0.1, 0.2, 0.3],
            document=doc,
            metadata={"key": "value"}
        )
        
        data = vector.to_dict()
        self.assertIn('vector_id', data)
        self.assertIn('embedding', data)
        self.assertIn('document', data)
        
        restored = IndexedVector.from_dict(data)
        self.assertEqual(restored.vector_id, vector.vector_id)
        self.assertEqual(restored.embedding, vector.embedding)
        self.assertEqual(restored.document.source_id, vector.document.source_id)


# =============================================================================
# TESTY SearchResult
# =============================================================================

class TestSearchResult(unittest.TestCase):
    """Testy klasy SearchResult."""
    
    def test_create_search_result(self):
        """Test tworzenia SearchResult."""
        result = SearchResult(
            vector_id="vec_001",
            similarity=0.95,
            embedding=[0.1, 0.2, 0.3],
            document=None,
            metadata={"source_type": "strategy_memory"},
            rank=0
        )
        
        self.assertEqual(result.vector_id, "vec_001")
        self.assertEqual(result.similarity, 0.95)
        self.assertEqual(result.rank, 0)
    
    def test_search_result_serialization(self):
        """Test serializacji SearchResult."""
        doc = CollectiveMemoryDocument(
            source_id="test_001",
            text="Test content"
        )
        
        result = SearchResult(
            vector_id="vec_001",
            similarity=0.95,
            embedding=[0.1, 0.2, 0.3],
            document=doc,
            metadata={"source_type": "strategy_memory"},
            rank=0
        )
        
        data = result.to_dict()
        restored = SearchResult.from_dict(data)
        
        self.assertEqual(restored.vector_id, result.vector_id)
        self.assertEqual(restored.similarity, result.similarity)
        self.assertEqual(restored.rank, result.rank)


# =============================================================================
# TESTY NumpyVectorIndexBackend
# =============================================================================

class TestNumpyVectorIndexBackend(unittest.TestCase):
    """Testy backend NumpyVectorIndex."""
    
    def setUp(self):
        """Inicjalizacja backend."""
        self.backend = NumpyVectorIndexBackend(dimension=3)
    
    def test_backend_initialization(self):
        """Test inicjalizacji backend."""
        self.assertEqual(self.backend.index_type, INDEX_TYPE_NUMPY)
        self.assertEqual(self.backend.dimension, 3)
        self.assertEqual(self.backend.size, 0)
    
    def test_add_vector(self):
        """Test dodawania wektora."""
        result = self.backend.add_vector(
            vector_id="vec_001",
            embedding=[1.0, 0.0, 0.0],
            metadata={"source": "test"}
        )
        
        self.assertTrue(result)
        self.assertEqual(self.backend.size, 1)
    
    def test_add_multiple_vectors(self):
        """Test dodawania wielu wektorow."""
        vectors = [
            ("vec_001", [1.0, 0.0, 0.0]),
            ("vec_002", [0.0, 1.0, 0.0]),
            ("vec_003", [0.0, 0.0, 1.0])
        ]
        
        for vec_id, emb in vectors:
            self.backend.add_vector(vec_id, emb)
        
        self.assertEqual(self.backend.size, 3)
    
    def test_search_similar_vectors(self):
        """Test wyszukiwania podobnych wektorow."""
        # Dodaj wektory
        self.backend.add_vector("vec_001", [1.0, 0.0, 0.0])
        self.backend.add_vector("vec_002", [0.0, 1.0, 0.0])
        self.backend.add_vector("vec_003", [1.0, 0.0, 0.0])  # Ten sam jak vec_001
        
        # Wyszukaj
        results = self.backend.search([1.0, 0.0, 0.0], top_k=2)
        
        self.assertEqual(len(results), 2)
        # vec_001 i vec_003 powinny byc najbardziej podobne (similarity = 1.0)
        self.assertEqual(results[0][0], "vec_001")  # lub "vec_003"
        self.assertAlmostEqual(results[0][1], 1.0, places=5)
    
    def test_remove_vector(self):
        """Test usuwania wektora."""
        self.backend.add_vector("vec_001", [1.0, 0.0, 0.0])
        self.backend.add_vector("vec_002", [0.0, 1.0, 0.0])
        
        result = self.backend.remove_vector("vec_001")
        
        self.assertTrue(result)
        self.assertEqual(self.backend.size, 1)
    
    def test_get_vector(self):
        """Test pobierania wektora."""
        self.backend.add_vector("vec_001", [1.0, 2.0, 3.0])
        
        vector = self.backend.get_vector("vec_001")
        
        self.assertIsNotNone(vector)
        self.assertEqual(vector, [1.0, 2.0, 3.0])
    
    def test_get_nonexistent_vector(self):
        """Test pobierania nieistniejacego wektora."""
        vector = self.backend.get_vector("nonexistent")
        self.assertIsNone(vector)
    
    def test_save_and_load(self):
        """Test zapisu i wczytania indeksu."""
        # Dodaj wektory
        self.backend.add_vector("vec_001", [1.0, 0.0, 0.0])
        self.backend.add_vector("vec_002", [0.0, 1.0, 0.0])
        
        # Zapisz i wczytaj
        temp_file = tempfile.mktemp(suffix=".pkl")
        try:
            self.backend.save(temp_file)
            
            # Utworz nowy backend i wczytaj
            new_backend = NumpyVectorIndexBackend(dimension=3)
            result = new_backend.load(temp_file)
            
            self.assertTrue(result)
            self.assertEqual(new_backend.size, 2)
            self.assertEqual(new_backend.get_vector("vec_001"), [1.0, 0.0, 0.0])
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_clear(self):
        """Test czyszczenia indeksu."""
        self.backend.add_vector("vec_001", [1.0, 0.0, 0.0])
        self.backend.add_vector("vec_002", [0.0, 1.0, 0.0])
        
        self.backend.clear()
        
        self.assertEqual(self.backend.size, 0)
    
    def test_invalid_dimension(self):
        """Test dodawania wektora o zlym rozmiarze."""
        with self.assertRaises(ValueError):
            self.backend.add_vector("vec_001", [1.0, 0.0])  # 2 zamiast 3
    
    def test_invalid_query_dimension(self):
        """Test wyszukiwania z zapytaniem o zlym rozmiarze."""
        self.backend.add_vector("vec_001", [1.0, 0.0, 0.0])
        
        with self.assertRaises(ValueError):
            self.backend.search([1.0, 0.0])  # 2 zamiast 3


# =============================================================================
# TESTY VectorIndex (Glowna klasa)
# =============================================================================

class TestVectorIndex(unittest.TestCase):
    """Testy glównej klasy VectorIndex."""
    
    def setUp(self):
        """Inicjalizacja indeksu."""
        self.generator = EmbeddingGenerator(dimension=3)
        self.index = VectorIndex(
            config=VectorIndexConfig(dimension=3),
            embedding_generator=self.generator
        )
    
    def test_vector_index_initialization(self):
        """Test inicjalizacji VectorIndex."""
        self.assertEqual(self.index.size, 0)
        self.assertEqual(self.index.dimension, 3)
    
    def test_add_document(self):
        """Test dodawania dokumentu."""
        doc = CollectiveMemoryDocument(
            source_id="test_001",
            source_type="strategy_memory",
            text="Test content"
        )
        
        result = self.index.add(doc)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.vector_id, doc.document_id)
        self.assertEqual(self.index.size, 1)
    
    def test_add_document_with_embedding(self):
        """Test dodawania dokumentu z embeddingiem."""
        doc = CollectiveMemoryDocument(
            source_id="test_001",
            source_type="strategy_memory",
            text="Test content"
        )
        
        embedding = self.generator.generate_document(doc)
        result = self.index.add(doc, embedding)
        
        self.assertIsNotNone(result)
        self.assertEqual(self.index.size, 1)
    
    def test_add_batch(self):
        """Test dodawania wielu dokumentow."""
        docs = [
            CollectiveMemoryDocument(source_id=f"test_{i}", text=f"Content {i}")
            for i in range(5)
        ]
        
        results = self.index.add_batch(docs)
        
        self.assertEqual(len(results), 5)
        self.assertEqual(self.index.size, 5)
    
    def test_search_by_text(self):
        """Test wyszukiwania po tekście."""
        # Dodaj dokumenty
        doc1 = CollectiveMemoryDocument(
            source_id="doc1",
            text="Strategy with high confidence"
        )
        doc2 = CollectiveMemoryDocument(
            source_id="doc2",
            text="Strategy with low confidence"
        )
        
        self.index.add(doc1)
        self.index.add(doc2)
        
        # Wyszukaj
        results = self.index.search_by_text("high confidence", top_k=1)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].rank, 0)
    
    def test_search_by_embedding(self):
        """Test wyszukiwania po embedding."""
        doc = CollectiveMemoryDocument(
            source_id="test_001",
            text="Test content"
        )
        
        embedding = self.generator.generate_document(doc)
        self.index.add(doc, embedding)
        
        # Wyszukaj
        results = self.index.search(embedding.embedding, top_k=1)
        
        self.assertEqual(len(results), 1)
        self.assertAlmostEqual(results[0].similarity, 1.0, places=5)
    
    def test_search_by_document(self):
        """Test wyszukiwania po dokumencie."""
        doc1 = CollectiveMemoryDocument(
            source_id="doc1",
            text="Similar content"
        )
        doc2 = CollectiveMemoryDocument(
            source_id="doc2",
            text="Similar content"
        )
        
        self.index.add(doc1)
        
        results = self.index.search_by_document(doc2, top_k=1)
        
        self.assertEqual(len(results), 1)
    
    def test_remove_document(self):
        """Test usuwania dokumentu."""
        doc = CollectiveMemoryDocument(
            source_id="test_001",
            text="Test content"
        )
        
        self.index.add(doc)
        self.assertEqual(self.index.size, 1)
        
        result = self.index.remove(doc.document_id)
        
        self.assertTrue(result)
        self.assertEqual(self.index.size, 0)
    
    def test_get_document(self):
        """Test pobierania dokumentu."""
        doc = CollectiveMemoryDocument(
            source_id="test_001",
            text="Test content"
        )
        
        self.index.add(doc)
        
        retrieved = self.index.get(doc.document_id)
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.source_id, doc.source_id)
    
    def test_save_and_load(self):
        """Test zapisu i wczytania indeksu."""
        # Dodaj dokumenty
        for i in range(3):
            doc = CollectiveMemoryDocument(
                source_id=f"test_{i}",
                text=f"Content {i}"
            )
            self.index.add(doc)
        
        # Zapisz i wczytaj
        temp_dir = tempfile.mkdtemp()
        try:
            config = VectorIndexConfig(
                storage_path=f"{temp_dir}/test_index",
                dimension=3
            )
            index = VectorIndex(config=config, embedding_generator=self.generator)
            
            # Dodaj te same dokumenty
            for i in range(3):
                doc = CollectiveMemoryDocument(
                    source_id=f"test_{i}",
                    text=f"Content {i}"
                )
                index.add(doc)
            
            # Zapisz
            index.save()
            
            # Utworz nowy indeks i wczytaj
            new_index = VectorIndex(
                config=config,
                embedding_generator=self.generator
            )
            new_index.load()
            
            self.assertEqual(new_index.size, 3)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_get_stats(self):
        """Test statystyk indeksu."""
        # Dodaj kilka dokumentow
        for i in range(5):
            doc = CollectiveMemoryDocument(
                source_id=f"test_{i}",
                text=f"Content {i}"
            )
            self.index.add(doc)
        
        stats = self.index.get_stats()
        
        self.assertEqual(stats['size'], 5)
        self.assertEqual(stats['dimension'], 3)
        self.assertEqual(stats['documents_count'], 5)
    
    def test_clear(self):
        """Test czyszczenia indeksu."""
        # Dodaj dokumenty
        for i in range(3):
            doc = CollectiveMemoryDocument(
                source_id=f"test_{i}",
                text=f"Content {i}"
            )
            self.index.add(doc)
        
        self.index.clear()
        
        self.assertEqual(self.index.size, 0)


# =============================================================================
# TESTY FABRYKI
# =============================================================================

class TestFactory(unittest.TestCase):
    """Testy fabryki."""
    
    def test_create_vector_index_default(self):
        """Test tworzenia indeksu z domyslnymi parametrami."""
        index = create_vector_index()
        
        self.assertIsInstance(index, VectorIndex)
        self.assertEqual(index.backend_type, INDEX_TYPE_NUMPY)
    
    def test_create_vector_index_custom(self):
        """Test tworzenia indeksu z niestandardowymi parametrami."""
        index = create_vector_index(
            index_type=INDEX_TYPE_NUMPY,
            dimension=768,
            storage_path="/tmp/test"
        )
        
        self.assertIsInstance(index, VectorIndex)
        self.assertEqual(index.dimension, 768)


# =============================================================================
# RUNNER
# =============================================================================

if __name__ == '__main__':
    unittest.main()
