"""
SSI V5 - Testy Embedding Generator
ETAP: 5.4.1 - Memory Embedding Foundation

Testy jednostkowe dla EmbeddingGenerator.

Zakres testow:
1. MockEmbeddingBackend
2. EmbeddingGenerator
3. EmbeddingResult
4. EmbeddingCache
5. Funkcje prostowe (cosine_similarity, etc.)
6. Batch processing

Autor: SSI V5 System / Mistral Vibe
Data: 2026-08-04
Wersja: 1.0.0
"""

import unittest
import numpy as np
from datetime import datetime

# Import klas do testow
from SSI_V5.memory.collective_memory.embedding_generator import (
    EmbeddingResult,
    EmbeddingCache,
    EmbeddingGenerator,
    BaseEmbeddingBackend,
    MockEmbeddingBackend,
    SentenceTransformerBackend,
    cosine_similarity,
    euclidean_distance,
    dot_product,
    create_embedding_generator
)


# =============================================================================
# TESTY EmbeddingResult
# =============================================================================

class TestEmbeddingResult(unittest.TestCase):
    """Testy klasy EmbeddingResult."""
    
    def test_create_embedding_result(self):
        """Test tworzenia EmbeddingResult."""
        embedding = [0.1, 0.2, 0.3, 0.4]
        result = EmbeddingResult(
            document_id="test_001",
            embedding=embedding,
            model_name="mock-v1",
            dimension=4
        )
        
        self.assertEqual(result.document_id, "test_001")
        self.assertEqual(result.embedding, embedding)
        self.assertEqual(result.model_name, "mock-v1")
        self.assertEqual(result.dimension, 4)
        self.assertIsInstance(result.timestamp, datetime)
    
    def test_embedding_result_validation(self):
        """Test walidacji EmbeddingResult."""
        # Poprawny embedding
        valid_result = EmbeddingResult(
            document_id="valid",
            embedding=[0.1, 0.2, 0.3],
            dimension=3
        )
        self.assertTrue(valid_result.validate())
        
        # Zly rozmiar
        invalid_result = EmbeddingResult(
            document_id="invalid",
            embedding=[0.1, 0.2],  # 2 zamiast 3
            dimension=3
        )
        self.assertFalse(invalid_result.validate())
        
        # Puste embedding
        empty_result = EmbeddingResult(
            document_id="empty",
            embedding=[],
            dimension=0
        )
        self.assertFalse(empty_result.validate())
        
        # Zle typy (string)
        wrong_type_result = EmbeddingResult(
            document_id="wrong",
            embedding=["0.1", "0.2", "0.3"],
            dimension=3
        )
        self.assertFalse(wrong_type_result.validate())
    
    def test_embedding_to_numpy(self):
        """Test konwersji embeddingu do numpy."""
        result = EmbeddingResult(
            document_id="test",
            embedding=[1.0, 2.0, 3.0],
            dimension=3
        )
        
        np_array = result.to_numpy()
        self.assertIsInstance(np_array, np.ndarray)
        self.assertEqual(np_array.shape, (3,))
        self.assertTrue(np.allclose(np_array, [1.0, 2.0, 3.0]))
    
    def test_embedding_normalized(self):
        """Test normalizacji embeddingu."""
        result = EmbeddingResult(
            document_id="test",
            embedding=[1.0, 1.0, 1.0],
            dimension=3
        )
        
        normalized = result.normalized()
        
        # Po normalizacji norm应该byc bliska 1
        np_array = np.array(normalized, dtype=np.float32)
        norm = np.linalg.norm(np_array)
        self.assertAlmostEqual(norm, 1.0, places=5)
    
    def test_embedding_similarity(self):
        """Test obliczania podobienstwa pomiedzy embeddingami."""
        # Identyczne wektory - podobienstwo = 1.0
        emb1 = EmbeddingResult(
            document_id="doc1",
            embedding=[1.0, 0.0, 0.0],
            dimension=3
        )
        emb2 = EmbeddingResult(
            document_id="doc2",
            embedding=[1.0, 0.0, 0.0],
            dimension=3
        )
        self.assertAlmostEqual(emb1.similarity(emb2), 1.0, places=5)
        
        # Prostopadle wektory - podobienstwo = 0.0
        emb3 = EmbeddingResult(
            document_id="doc3",
            embedding=[1.0, 0.0, 0.0],
            dimension=3
        )
        emb4 = EmbeddingResult(
            document_id="doc4",
            embedding=[0.0, 1.0, 0.0],
            dimension=3
        )
        self.assertAlmostEqual(emb3.similarity(emb4), 0.0, places=5)
        
        # Przeciwne wektory - podobienstwo = -1.0
        emb5 = EmbeddingResult(
            document_id="doc5",
            embedding=[1.0, 0.0, 0.0],
            dimension=3
        )
        emb6 = EmbeddingResult(
            document_id="doc6",
            embedding=[-1.0, 0.0, 0.0],
            dimension=3
        )
        self.assertAlmostEqual(emb5.similarity(emb6), -1.0, places=5)
    
    def test_embedding_serialization(self):
        """Test serializacji i deserializacji EmbeddingResult."""
        original = EmbeddingResult(
            document_id="test",
            embedding=[0.1, 0.2, 0.3],
            model_name="mock-v1",
            dimension=3,
            metadata={"key": "value"}
        )
        
        # Serializacja
        data = original.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['document_id'], "test")
        self.assertEqual(data['embedding'], [0.1, 0.2, 0.3])
        
        # Deserializacja
        restored = EmbeddingResult.from_dict(data)
        self.assertEqual(restored.document_id, original.document_id)
        self.assertEqual(restored.embedding, original.embedding)
        self.assertEqual(restored.model_name, original.model_name)


# =============================================================================
# TESTY EmbeddingCache
# =============================================================================

class TestEmbeddingCache(unittest.TestCase):
    """Testy klasy EmbeddingCache."""
    
    def test_cache_initialization(self):
        """Test inicjalizacji cache."""
        cache = EmbeddingCache(max_size=100, ttl_seconds=3600)
        self.assertEqual(cache.max_size, 100)
        self.assertEqual(cache.ttl_seconds, 3600)
        self.assertEqual(cache.size(), 0)
    
    def test_cache_set_and_get(self):
        """Test zapisywania i pobierania z cache."""
        cache = EmbeddingCache(max_size=100)
        
        result = EmbeddingResult(
            document_id="test",
            embedding=[0.1, 0.2, 0.3],
            dimension=3
        )
        
        cache.set("test text", result)
        
        retrieved = cache.get("test text")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.document_id, "test")
        self.assertEqual(retrieved.embedding, [0.1, 0.2, 0.3])
    
    def test_cache_miss(self):
        """Test pobierania nieistniejacego wpisu z cache."""
        cache = EmbeddingCache()
        
        result = cache.get("nonexistent text")
        self.assertIsNone(result)
    
    def test_cache_size_limit(self):
        """Test limitu rozmiaru cache."""
        cache = EmbeddingCache(max_size=3)
        
        # Dodaj 4 wpisy
        for i in range(4):
            result = EmbeddingResult(
                document_id=f"doc_{i}",
                embedding=[float(i)] * 3,
                dimension=3
            )
            cache.set(f"text_{i}", result)
        
        # Powinno zostac 3 wpisy (FIFO - pierwszy/zostal usuniety)
        self.assertEqual(cache.size(), 3)
    
    def test_cache_clear(self):
        """Test czyszczenia cache."""
        cache = EmbeddingCache()
        
        # Dodaj kilka wpisow
        for i in range(5):
            result = EmbeddingResult(
                document_id=f"doc_{i}",
                embedding=[float(i)] * 3,
                dimension=3
            )
            cache.set(f"text_{i}", result)
        
        # Czysc
        cache.clear()
        self.assertEqual(cache.size(), 0)


# =============================================================================
# TESTY BaseEmbeddingBackend (Mock)
# =============================================================================

class TestMockEmbeddingBackend(unittest.TestCase):
    """Testy klasy MockEmbeddingBackend."""
    
    def test_backend_initialization(self):
        """Test inicjalizacji backend."""
        backend = MockEmbeddingBackend(dimension=384)
        self.assertEqual(backend.dimension, 384)
        self.assertEqual(backend.model_name, "mock-v1")
    
    def test_generate_embedding(self):
        """Test generowania embeddingu."""
        backend = MockEmbeddingBackend(dimension=384)
        
        embedding = backend.generate_embedding("Test text")
        
        self.assertIsInstance(embedding, list)
        self.assertEqual(len(embedding), 384)
        self.assertTrue(all(isinstance(x, float) for x in embedding))
    
    def test_generate_embedding_deterministic(self):
        """Test deterministycznosci generacji embeddingu."""
        backend = MockEmbeddingBackend(dimension=384)
        
        # Taki sam tekst = taki sam embedding
        emb1 = backend.generate_embedding("Test text")
        emb2 = backend.generate_embedding("Test text")
        
        # Powinny byc identyczne
        for a, b in zip(emb1, emb2):
            self.assertAlmostEqual(a, b, places=10)
    
    def test_different_texts_different_embeddings(self):
        """Test czy rozne teksty generuja rozne embeddinge."""
        backend = MockEmbeddingBackend(dimension=384)
        
        emb1 = backend.generate_embedding("Text A")
        emb2 = backend.generate_embedding("Text B")
        
        # Powinny byc rozne (z wysoka pewnoscia)
        self.assertNotEqual(emb1, emb2)
    
    def test_generate_batch(self):
        """Test generowania embeddingu dla batch."""
        backend = MockEmbeddingBackend(dimension=384)
        
        texts = ["Text A", "Text B", "Text C"]
        embeddings = backend.generate_batch(texts)
        
        self.assertEqual(len(embeddings), 3)
        for emb in embeddings:
            self.assertEqual(len(emb), 384)
    
    def test_validate_embedding(self):
        """Test walidacji embeddingu."""
        backend = MockEmbeddingBackend(dimension=384)
        
        # Poprawny embedding
        valid_embedding = [0.0] * 384
        self.assertTrue(backend.validate_embedding(valid_embedding))
        
        # Zly rozmiar
        invalid_embedding = [0.0] * 100
        self.assertFalse(backend.validate_embedding(invalid_embedding))
        
        # Zle typy
        wrong_type_embedding = ["0.0"] * 384
        self.assertFalse(backend.validate_embedding(wrong_type_embedding))


# =============================================================================
# TESTY EmbeddingGenerator
# =============================================================================

class TestEmbeddingGenerator(unittest.TestCase):
    """Testy klasy EmbeddingGenerator."""
    
    def setUp(self):
        """Inicjalizacja generatora."""
        self.generator = EmbeddingGenerator(backend="mock", dimension=384)
    
    def test_generator_initialization(self):
        """Test inicjalizacji generatora."""
        gen = EmbeddingGenerator()
        self.assertIsNotNone(gen)
        self.assertEqual(gen.backend_name, "mock")
        self.assertEqual(gen.dimension, 384)
    
    def test_generate_single(self):
        """Test generowania pojedynczego embeddingu."""
        result = self.generator.generate("Test text")
        
        self.assertIsInstance(result, EmbeddingResult)
        self.assertEqual(len(result.embedding), 384)
        self.assertEqual(result.model_name, "mock-v1")
        self.assertTrue(result.validate())
    
    def test_generate_with_cache(self):
        """Test generowania z cache."""
        # Pierwsz llegada powinna byc nowy embedding
        result1 = self.generator.generate("Cached text", use_cache=True)
        
        # Drugi raz powinien byc z cache
        result2 = self.generator.generate("Cached text", use_cache=True)
        
        # Powinny byc identyczne (ten sam dokument_id)
        self.assertEqual(result1.document_id, result2.document_id)
        
        # Cache powinien byc pusty na poczatku
        stats = self.generator.get_cache_stats()
        self.assertEqual(stats['size'], 1)
    
    def test_generate_without_cache(self):
        """Test generowania bez cache."""
        result1 = self.generator.generate("Text A", use_cache=False)
        result2 = self.generator.generate("Text A", use_cache=False)
        
        # W naszym implementacji document_id jest generowany z hash tekstu
        # Wiec zawsze bedzie taki sam dla tego samego tekstu
        # Sprawdzam ze dokument_id jest taki sam (poniewaz oparty na tekscie)
        self.assertEqual(result1.document_id, result2.document_id)
        
        # Ale wartosci embeddingow powinny byc takie same (deterministyczne)
        # Poniewaz te same teksty -> ten sam hash -> ten sam seed -> ten sam embedding
        for a, b in zip(result1.embedding, result2.embedding):
            self.assertAlmostEqual(a, b, places=10)
    
    def test_generate_batch(self):
        """Test generowania batch embeddingu."""
        texts = ["Text A", "Text B", "Text C"]
        results = self.generator.generate_batch(texts)
        
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIsInstance(result, EmbeddingResult)
            self.assertEqual(len(result.embedding), 384)
    
    def test_calculate_similarity(self):
        """Test obliczania podobienstwa pomiedzy tekstami."""
        # Taki sam tekst = podobienstwo 1.0
        similarity = self.generator.calculate_similarity("Test text", "Test text")
        self.assertAlmostEqual(similarity, 1.0, places=5)
        
        # Rozne teksty = podobienstwo < 1.0
        similarity2 = self.generator.calculate_similarity("Text A", "Text B")
        self.assertLess(similarity2, 1.0)
    
    def test_calculate_similarities(self):
        """Test obliczania podobienstw dla wielu tekstow."""
        query = "Query text"
        targets = ["Similar text", "Different text", "Another text"]
        
        similarities = self.generator.calculate_similarities(query, targets)
        
        self.assertEqual(len(similarities), 3)
        for sim in similarities:
            self.assertIsInstance(sim, float)
            self.assertGreaterEqual(sim, -1.0)
            self.assertLessEqual(sim, 1.0)
    
    def test_clear_cache(self):
        """Test czyszczenia cache."""
        # Generuj kilka embeddingow
        for i in range(5):
            self.generator.generate(f"Text {i}", use_cache=True)
        
        # Cache powinien miec 5 wpisow
        stats = self.generator.get_cache_stats()
        self.assertEqual(stats['size'], 5)
        
        # Czysc cache
        self.generator.clear_cache()
        
        # Cache powinien byc pusty
        stats = self.generator.get_cache_stats()
        self.assertEqual(stats['size'], 0)


# =============================================================================
# TESTY FUNKCJI UZYTKOWYCH
# =============================================================================

class TestUtilityFunctions(unittest.TestCase):
    """Testy funkcji uzytecznych."""
    
    def test_cosine_similarity_identical(self):
        """Test podobienstwa kosinusowego dla identycznych wektorow."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        
        self.assertAlmostEqual(cosine_similarity(vec1, vec2), 1.0, places=5)
    
    def test_cosine_similarity_perpendicular(self):
        """Test podobienstwa kosinusowego dla prostopadlych wektorow."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]
        
        self.assertAlmostEqual(cosine_similarity(vec1, vec2), 0.0, places=5)
    
    def test_cosine_similarity_opposite(self):
        """Test podobienstwa kosinusowego dla przeciwnych wektorow."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [-1.0, 0.0, 0.0]
        
        self.assertAlmostEqual(cosine_similarity(vec1, vec2), -1.0, places=5)
    
    def test_cosine_similarity_different_dimensions(self):
        """Test podobienstwa kosinusowego dla roznych rozmiarow."""
        vec1 = [1.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        
        with self.assertRaises(ValueError):
            cosine_similarity(vec1, vec2)
    
    def test_euclidean_distance(self):
        """Test odleglosci euklidesowej."""
        vec1 = [0.0, 0.0, 0.0]
        vec2 = [1.0, 1.0, 1.0]
        
        # sqrt(1^2 + 1^2 + 1^2) = sqrt(3)
        self.assertAlmostEqual(euclidean_distance(vec1, vec2), np.sqrt(3), places=5)
    
    def test_dot_product(self):
        """Test iloczynu skalarnego."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [4.0, 5.0, 6.0]
        
        # 1*4 + 2*5 + 3*6 = 4 + 10 + 18 = 32
        self.assertAlmostEqual(dot_product(vec1, vec2), 32.0, places=5)


# =============================================================================
# TESTY FABRYKI
# =============================================================================

class TestFactory(unittest.TestCase):
    """Testy fabryki."""
    
    def test_create_embedding_generator_default(self):
        """Test tworzenia generatora z domyslnymi parametrami."""
        generator = create_embedding_generator()
        
        self.assertIsInstance(generator, EmbeddingGenerator)
        self.assertEqual(generator.backend_name, EmbeddingGenerator.BACKEND_MOCK)
    
    def test_create_embedding_generator_mock(self):
        """Test tworzenia generatora z backend mock."""
        generator = create_embedding_generator(backend="mock")
        
        self.assertIsInstance(generator, EmbeddingGenerator)
        self.assertEqual(generator.backend_name, "mock")


# =============================================================================
# RUNNER
# =============================================================================

if __name__ == '__main__':
    unittest.main()
