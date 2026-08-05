# SSI V5 ETAP 0 MEMORY INTEGRATION PLAN

**Cel:** Integracja istniejących modułów ETAP 5.4 z głównym przepływem systemu, a nie budowa od zera.

**Status wejściowy:**
- ✅ VectorIndex - zaimplementowany
- ✅ EmbeddingGenerator - zaimplementowany  
- ✅ CollectiveMemoryManager - zaimplementowany
- ✅ Wewnętrzna integracja collective_memory/ - istnieje
- ❌ Integracja z Agent Runtime/Decision Engine - brakuje
- ❌ RAG Retrieval Layer - brakuje
- ❌ Knowledge Graph Foundation - brakuje

---

## KOLEJNOŚĆ BUDOWY ETAP 0

### Krok 1: Agent Memory Integration
**Cel:** Agent zapisuje obserwacje i pobiera wcześniejszą wiedzę

**Istniejące pliki do wykorzystania:**
- `SSI_V5/memory/collective_memory/collective_memory_manager.py` - API: `store_memory()`, `search_memories()`
- `SSI_V5/agents/agent_runtime.py` - lokalne `long_term_memory` (fragmentaryczne)

**Nowe pliki wymagane:**
- `SSI_V5/agents/memory_integration.py` - Adapter pomiędzy Agent Runtime a CollectiveMemoryManager

**Zależności:** Brak

**Kryteria zakończenia:**
- Agent może zapisywać obserwacje do Collective Memory za pomocą `store_memory()`
- Agent może pobierać kontekst historyczny za pomocą `search_memories()`
- Testy potwierdzają zapis i odczyt pamięci przez agentów

---

### Krok 2: Decision Engine Memory Interface
**Cel:** Decision Engine uzna kontekst z pamięci przed podjęciem decyzji

**Istniejące pliki do wykorzystania:**
- `SSI_V5/agents/decision_engine.py` - istniejące API decyzji
- `SSI_V5/memory/collective_memory/collective_memory_manager.py` - `search_memories()`

**Nowe pliki wymagane:**
- `SSI_V5/agents/decision_memory_context.py` - Kontekst pamięci dla decyzji

**Zależności:** Krok 1 (Agent Memory Integration)

**Kryteria zakończenia:**
- Przed podjęciem decyzji: `query_memory()` → `retrieve_similar_cases()` → `get_context()`
- Decision Engine znajdzie podobne przypadki z przeszłości
- Kontekst pamięci jest dostępny dla każdej decyzji

---

### Krok 3: Decision Feedback Memory
**Cel:** Zapis decyzji, wyniku i doświadczenia po decyzji

**Istniejące pliki do wykorzystania:**
- `SSI_V5/agents/decision_engine.py` - `Decision`, `DecisionType`, `DecisionStatus`
- `SSI_V5/memory/collective_memory/collective_memory_manager.py` - `store_memory()`
- `SSI_V5/feedback/` - `PredictionOutcome`, `StrategyFitness`

**Nowe pliki wymagane:**
- `SSI_V5/agents/decision_feedback_handler.py` - Obsługa zapisu feedbacku decyzji

**Zależności:** Krok 2 (Decision Engine Memory Interface)

**Kryteria zakończenia:**
- Po decyzji: zapis do pamięci (decision, parameters, outcome, fitness)
- Historia decyzji jest dostępna do przyszłych zapytań
- Feedback loop: decyzja → wynik → ewaluacja → pamięć

---

### Krok 4: RAG Retrieval Layer
**Cel:** Adapter pomiędzy Decision Engine a CollectiveMemoryManager

**Istniejące pliki do wykorzystania:**
- `SSI_V5/memory/collective_memory/collective_memory_manager.py` - pełne API
- `SSI_V5/memory/collective_memory/vector_index.py` - `search_by_text()`, `search_by_vector()`

**Nowe pliki wymagane:**
- `SSI_V5/memory/collective_memory/rag_retrieval.py` - Warstwa RAG dla semantycznego wyszukiwania

**Zależności:** Krok 3 (Decision Feedback Memory)

**Kryteria zakończenia:**
- Semantyczne wyszukiwanie w pamięci kolektywnej
- Ranking wyników po podobieństwie
- Integracja z Decision Engine Memory Interface

---

### Krok 5: Knowledge Graph Foundation
**Cel:** Minimalna wersja grafu wiedzy

**Istniejące pliki do wykorzystania:**
- `SSI_V5/memory/collective_memory/memory_document.py` - `CollectiveMemoryDocument`
- `SSI_V5/memory/collective_memory/collective_memory_manager.py` - zarządzanie dokumentami

**Nowe pliki wymagane:**
- `SSI_V5/memory/collective_memory/knowledge_graph.py` - Podstawowa struktura grafu

**Zależności:** Krok 4 (RAG Retrieval Layer)

**Kryteria zakończenia:**
- Graf wiedzy zawierający: Dokument, Agent, Strategia, Relacja
- Podstawowe relacje między encjami
- Możliwość nawigacji po grafie

---

## ZALEŻNOŚCI MIĘDZY KROKAMI

```
Krok 1: Agent Memory Integration
    ↓
Krok 2: Decision Engine Memory Interface
    ↓
Krok 3: Decision Feedback Memory
    ↓
Krok 4: RAG Retrieval Layer
    ↓
Krok 5: Knowledge Graph Foundation
```

**Całkowity czas ETAP 0:** 5 kroków, szacowany 1-2 tygodnie

---

## ISTNIEJĄCE API DO WYKORZYSTANIA

### CollectiveMemoryManager (pełne API):
- `store_memory(memory_record)` → `Optional[str]` (document_id)
- `search_memories(query, top_k=5)` → `List[CollectiveMemoryDocument]`
- `get_memory(document_id)` → `Optional[CollectiveMemoryDocument]`
- `vector_index()` → `VectorIndex` (property)
- `embedding_generator()` → `EmbeddingGenerator` (property)

### VectorIndex (pełne API):
- `add(document)` → `str` (vector_id)
- `search_by_text(query, top_k=5)` → `List[SearchResult]`
- `search_by_vector(vector, top_k=5)` → `List[SearchResult]`
- `get(document_id)` → `Optional[IndexedVector]`

### EmbeddingGenerator (pełne API):
- `generate_embedding(text)` → `List[float]`
- `generate_batch_embeddings(texts)` → `List[List[float]]`

---

## NOWE PLIKI WYMAGANE W ETAP 0

| Krok | Plik | Opis | Zależności |
|------|------|------|-------------|
| 1 | `SSI_V5/agents/memory_integration.py` | Adapter Agent ↔ Collective Memory | Brak |
| 2 | `SSI_V5/agents/decision_memory_context.py` | Kontekst pamięci dla Decisions | Krok 1 |
| 3 | `SSI_V5/agents/decision_feedback_handler.py` | Zapis feedbacku decyzji | Krok 2 |
| 4 | `SSI_V5/memory/collective_memory/rag_retrieval.py` | Warstwa RAG | Krok 3 |
| 5 | `SSI_V5/memory/collective_memory/knowledge_graph.py` | Graf wiedzy | Krok 4 |

---

## PRZEPŁYW DANYCH PO ETAP 0

### Przed ETAP 0:
```
Agent Runtime
    ↓
Decision Engine (decision_engine.py)
    ↓
??? (Brak połączenia z pamięcią kolektywną)
    ↓
Memory System (strategy_memory, match_result_memory)
```

### Po ETAP 0:
```
Agent Runtime
    ↓
1. Agent Memory Integration
    │
    ├─ store_memory(obserwacje) → CollectiveMemoryManager
    └─ search_memories(zapytanie) ← CollectiveMemoryManager
    │
    ↓
Decision Engine
    ↓
2. Decision Engine Memory Interface
    │
    ├─ query_memory(kontekst) → RAG Retrieval
    │   │
    │   ↓
    │  4. RAG Retrieval Layer → VectorIndex.search_by_text()
    │       │
    │       ↓
    │      5. Knowledge Graph (opcjonalnie)
    │
    └─ get_context() ← CollectiveMemoryManager
    │
    ↓
Decyzja
    ↓
3. Decision Feedback Memory
    │
    ├─ store_memory(decyzja + wynik + fitness) → CollectiveMemoryManager
    └─ update_knowledge_graph() (opcjonalnie)
```

---

## KRYTERIA ZAKOŃCZENIA ETAP 0

### Kryteria techniczne:
1. ✅ Agent Runtime może zapisywać do Collective Memory
2. ✅ Agent Runtime może czytać z Collective Memory
3. ✅ Decision Engine uzyskuje kontekst pamięci przed decyzją
4. ✅ Decyzje, wyniki i fitness są zapisywane do pamięci
5. ✅ RAG Retrieval Layer działa i zwraca semantycznie podobne przypadki
6. ✅ Knowledge Graph istnieje (minimalna wersja)

### Kryteria testowe:
1. ✅ Test zapisu i odczytu pamięci przez Agent Runtime
2. ✅ Test perpływu: Decision Engine → Memory Query → Context → Decision
3. ✅ Test feedback loop: Decision → Outcome → Fitness → Memory
4. ✅ Test RAG: semantyczne wyszukiwanie w pamięci kolektywnej
5. ✅ Test Knowledge Graph: nawigacja po podstawowych relacjach

### Kryteria integracyjne:
1. ✅ Brak duplikacji kodu (wykorzystanie istniejących modułów)
2. ✅ Wszystkie połączenia są dwukierunkowe (zapis + odczyt)
3. ✅ Pamięć kolektywna jest dostępna dla wszystkich agentów
4. ✅ System działa bez błędów w głównym przepływie

---

## PODSUMOWANIE

**ETAP 0 to INTEGRACJA, nie implementacja od zera.**

**Co mamy:** Pełny system pamięci kolektywnej z indeksem wektorowym i generatorem embeddingów
**Co brakuje:** Połączenie tego systemu zprincipal przepływem agentów i decyzji

**Kolejność:** Agent Memory → Decision Context → Feedback Loop → RAG → Knowledge Graph

**Rezultat końcowy ETAP 0:** Jednolity system, w którym agenci podejmują decyzje z kontekstem historycznym, zapisują doświadczenia i uczą się na podstawie przeszłości.
