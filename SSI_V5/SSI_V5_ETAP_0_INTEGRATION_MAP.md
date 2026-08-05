# SSI V5 ETAP 0 INTEGRATION MAP

**Data**: 2026-08-04  
**Cel**: Dokładna mapa punktów integracji Collective Memory do aktualnego systemu agentów  
**Status**: ANALIZA PRZED IMPLEMENTACJĄ - ETAP 0 NIE ZOSTAŁ JESZCZE ZAIMPLEMENTOWANY

---

## 1. AGENT RUNTIME FLOW - ANALIZA ISTNIEEJĄCEGO PRZEPŁYWU

### Obecny przepływ w AgentRuntime (agent_runtime.py):

```
Agent Start
↓
receive_contract(AgentContract) [linia 466-529]
↓
_process_contract(contract) [linia 531-569]
    ├─ _apply_execution_context(execution_context) [linia 594-644]
    ├─ observation_manager.receive_world_data() [linia 539-544]
    ├─ strategy_manager.receive_context() [linia 546-553]
    ├─ decision_engine.receive_contract(contract) [linia 555-556]
    ├─ _generate_observations(contract) [linia 558-559]
    └─ _execute_decision(contract) [linia 646-656]
        └─ decision_engine.make_decision() [linia 649-654]
↓
_record_decision_and_observation(decision, contract) [linia 658-683]
    ├─ memory.add_decision(decision) [linia 661]
    ├─ decision_engine.record_decision(decision) [linia 662]
    └─ memory.add_observation(feedback_observation) [linia 664-673]
↓
Agent Memory Storage (lokalna AgentMemory)
```

### Idenyfikowane punkty wpięcia Memory Retrieval:

#### 🔹 PUNKT 1: Memory Retrieval PRZED Decision Engine
**Lokalizacja**: `_process_contract()` metoda, linia 555-556  
**Obecny kod**:
```python
# Przekazanie do Decision Engine
self.decision_engine.receive_contract(contract)
```

**Propozycja integracji**:
```python
# NOWE: Pobranie kontekstu z Collective Memory PRZED decyzją
if hasattr(self, 'collective_memory_manager') and self.collective_memory_manager:
    memory_context = self.collective_memory_manager.build_agent_context(
        self.agent_id, 
        current_situation=self._extract_situation_from_contract(contract)
    )
    # Dodanie kontekstu pamięci do kontraktu lub Decision Engine
    contract.memory_context = memory_context

# Przekazanie do Decision Engine (z rozszernionym kontekstem)
self.decision_engine.receive_contract(contract, memory_context=memory_context)
```

#### 🔹 PUNKT 2: Memory Retrieval W Decision Engine
**Lokalizacja**: `decision_engine.py` metoda `receive_contract()` i `make_decision()`  
**Obecny kod**:
- `receive_contract()` [204-237] - tworzy DecisionContext z kontraktu
- `make_decision()` [239-285] - podejmuje decyzję na podstawie kontekstu

**Propozycja integracji**:
```python
def receive_contract(self, contract: Any, memory_context: Optional[Dict] = None) -> None:
    # ... istniejący kod ...
    
    # NOWE: Integracja z pamięcią kolektywną
    if memory_context:
        self.current_context.memory_context = memory_context
        # Zapisanie w lokalnej pamięci agenta
        if self.memory:
            self.memory.store_in_short_term("memory_context", memory_context)

def make_decision(self, **kwargs) -> Dict[str, Any]:
    # ... istniejący kod ...
    
    # NOWE: Uwzględnienie kontekstu pamięci w podejmowaniu decyzji
    if (self.current_context and 
        hasattr(self.current_context, 'memory_context') and
        self.current_context.memory_context):
        # Wykorzystanie historycznych doświadczeń w Statenie decyzji
        self._incorporate_memory_into_decision()
```

### Idenyfikowane punkty wpięcia Memory Storage:

#### 🔹 PUNKT 3: Memory Storage PO Decision Engine
**Lokalizacja**: `_record_decision_and_observation()` metoda, linia 658-683  
**Obecny kod**:
```python
def _record_decision_and_observation(self, decision: Dict[str, Any], contract: AgentContract) -> None:
    # Zapisanie decyzji
    self.memory.add_decision(decision)  # Lokalna pamięć agenta
    self.decision_engine.record_decision(decision)
    
    # Zapisanie obserwacji zwrotnej
    feedback_observation = {...}
    self.memory.add_observation(feedback_observation)
```

**Propozycja integracji**:
```python
def _record_decision_and_observation(self, decision: Dict[str, Any], contract: AgentContract) -> None:
    # ... istniejący kod ...
    
    # NOWE: Zapis do Collective Memory
    if hasattr(self, 'collective_memory_manager') and self.collective_memory_manager:
        # Zapis decyzji do pamięci kolektywnej
        decision_for_collective = self._prepare_decision_for_collective_memory(decision, contract)
        self.collective_memory_manager.store_memory(decision_for_collective)
        
        # Zapis obserwacji do pamięci kolektywnej
        observation_for_collective = self._prepare_observation_for_collective_memory(
            feedback_observation, contract
        )
        self.collective_memory_manager.store_memory(observation_for_collective)
```

---

## 2. DECISION ENGINE FLOW - ANALIZA

### Obecny przepływ w DecisionEngine (decision_engine.py):

```
receive_contract(contract) [204-237]
↓
Utworzenie DecisionContext z kontraktu [217-223]
↓
Zapisanie kontekstu w pamięci agenta [226-237]
↓
make_decision(**kwargs) [239-285]
    ↓
    _update_context_from_kwargs() [250-303]
    ↓
    _select_decision_type() [305-329]
    ↓
    _generate_decision() [331-360]
    ↓
    Zapisanie w pamięci agenta [282-283]
```

### Przed decyzją - Kto pobiera kontekst?

**Obecny stan**: 
- `DecisionContext` jest tworzony wyłącznie z danych kontraktu (world_data, model_info, weights, recommendations)
- **Brak pobierania kontekstu z pamięci kolektywnej**
- Pamięć agenta (`self.memory`) jest wykorzystywana jedynie do zapisu, nie do odczytu

**Propozycja wsparcia**:
- **DecisionEngine** powinien mieć referencję do `CollectiveMemoryManager`
- Metoda `receive_contract()` powinna pobierać kontekst pamięci PRZED utworzeniem `DecisionContext`

### Po decyzji - Kto zapisuje doświadczenie?

**Obecny stan**:
- `decision_engine.record_decision()` zapisuje do `self.decision_history` (lokalna lista)
- `memory.add_decision()` zapisuje do `AgentMemory` (lokalna pamięć agenta)
- **Brak zapisu do Collective Memory**

**Propozycja wsparcia**:
- `DecisionEngine` powinien mieć referencję do `CollectiveMemoryManager`
- Po zapisie lokalnym, należy zawsze zapisywać do pamięci kolektywnej
- Należy przygotować adapter, który konwertuje `Decision` → format rozumiany przez `collective_memory`

---

## 3. EXISTING COMPONENTS MAPPING

### Tabela funkcjonowania istniejących komponentów:

| Funkcja | Czy istnieje | Lokalizacja | Czy wykorzystać | Uwagi |
|---|---|---|---|---|
| **agent_memory** | ✅ Tak | `agents/agent_runtime.py:72-148` | ✅ Tak | klasa `AgentMemory` - pamięć lokalna agenta, powinna być rozszerszona o połączenie z Collective Memory |
| **experience_memory** | ❌ Nie | - | ❌ Nie | Brak takiej klasy, funkcjonalność rozproszona |
| **decision_history** | ✅ Tak | `agents/decision_engine.py:152` | ✅ Tak | lista w `DecisionEngine`, lokalna historia |
| **feedback_loop** | ✅ Partial | `SSI_V5/feedback/` | ✅ Tak | `feedback_engine.py`, `prediction_evaluator.py` - istnieją, ale nie są połączone z pamięcią |
| **learning_memory** | ❌ Nie | - | ❌ Nie | Brak takiej klasy |
| **CollectiveMemoryManager** | ✅ Tak | `memory/collective_memory/collective_memory_manager.py` | ✅ Tak | **Główny komponent** - pełna implementacja z VectorIndex i EmbeddingGenerator |
| **VectorIndex** | ✅ Tak | `memory/collective_memory/vector_index.py` | ✅ Tak | Pełna implementacja z backendami |
| **EmbeddingGenerator** | ✅ Tak | `memory/collective_memory/embedding_generator.py` | ✅ Tak | Pełna implementacja |
| **AgentRuntimeManager** | ✅ Tak | `agents/agent_runtime.py:1079-` | ✅ Tak | Ma pole `collective_manager` (linia 1122) - **OTO PUNKT INTEGRACJI!** |
| **Memory Adapters** | ✅ Tak | `memory/collective_memory/adapters/` | ✅ Tak | Adaptery do konwersji różnych typów danych do formatu CollectiveMemory |

### KLUCZOWE ODKRYCIE:

**`AgentRuntimeManager` MA JUŻ POLE `collective_manager` (linia 1122)**:
```python
# Pamięć kolektywna - referencja do CollectiveManager (opcjonalna)
self.collective_manager = None
```

**Inne ważne odkrycia**:
1. `AgentRuntime` ma `self.memory` (AgentMemory) - lokalna pamięć agenta
2. `DecisionEngine` ma `self.memory` (referencja do AgentMemory)
3. `StrategyManager` ma `self.memory` (referencja do AgentMemory)
4. `ObservationManager` ma `self.memory` (referencja do AgentMemory)
5. Wszystkie menedżery mają połączenie z lokalną pamięcią agenta

---

## 4. NOWE PLIKI - WERYFIKACJA POTRZEBY

### memory_integration.py

**Status**: ⚠️ **CZĘŚCIOWO POTRZEBNY**  
**Powód**: 
- `AgentRuntimeManager` ma już pole `collective_manager`, ale nie ma implementacji połączenia
- Konieczny jest adapter między Agent Runtime a CollectiveMemoryManager
- **Zalecenie**: Utworzyć `agents/memory_integration.py` jako warstwę abstrakcji

**Cel**:
- Zapewnić jednolite API dla agentów do korzystania z Collective Memory
- Zarządzać połączeniem między lokalną pamięcią agenta a pamięcią kolektywną
- Integrować z istniejącym `collective_manager` w `AgentRuntimeManager`

### decision_memory_context.py

**Status**: ✅ **POTRZEBNY**  
**Powód**: 
- `DecisionEngine` nie ma obecnie mechanizmu pobierania kontekstu z pamięci
- Nie istnieje komponent, który dostarcza historyczny kontekst do podejmowania decyzji
- Obecny `DecisionContext` jest tworzony jedynie z bieżących danych kontraktu

**Cel**:
- Rozszerzyć `DecisionContext` o dane z pamięci kolektywnej
- Zapewnić mechanism pobierania podobnych przypadków z przeszłości
- Integrować z RAG Retrieval Layer

### decision_feedback_handler.py

**Status**: ⚠️ **CZĘŚCIOWO POTRZEBNY**  
**Powód**:
- `feedback/` katalog istnieje z `feedback_engine.py` i `prediction_evaluator.py`
- Brak jest komponentu, który automatycznie zapisuje wyniki decyzji + feedback do pamięci
- Istniejące komponenty feedback nie są połączone z Collective Memory

**Zalecenie**: 
- Rozszerzyć istniejący `feedback_engine.py` o funkcjonalność zapisu do pamięci
- **Alternatywa**: Utworzyć nowy `decision_feedback_handler.py` jako specjalizowany handler

### rag_retrieval.py

**Status**: ✅ **POTRZEBNY**  
**Powód**: 
- Nie istnieje warstwa abstrakcji RAG
- `CollectiveMemoryManager.search_memories()` przeprowadza semantyczne wyszukiwanie, ale brak jest najlepszych praktyk RAG
- Konieczna jest warstwa pośrednia dla:
  - Burnowania zapytań (query burning)
  - Re-ranking wyników
  - Formatowania kontekstu dla modeli
  - Obsługi różnych typów zapytań

**Uwaga**: Powinien być umieszczony w `memory/collective_memory/rag_retrieval.py`

### knowledge_graph.py

**Status**: ⚠️ **OPCJONALNY**  
**Powód**: 
- Nie istnieje obecnie żadna forma knowledge graph
- Jest to rozszerzenie, nie podstawowa wymagania integracji
- Może być zaimplementowany w późniejszych etapach

**Zalecenie**: 
- Na potrzeby ETAP 0: **ignorować** lub zaimplementować minimalną wersję
- W przyszłości: opcode o relacje między encjami (Dokument, Agent, Strategia, Decyzja, Wynik)

---

## 5. FINALNY SCHEMAT INTEGRACJI

### Schemat docelowy po ETAP 0:

```
┌─────────────────┐
│     Agent        │
│  (AgentRuntime)  │
└────────┬────────┘
         │
         │ receive_contract()
         ↓
┌───────────────────────────────┐
│     Memory Retrieval          │
│  (memory_integration.py)      │
│  ✓ collective_manager.store() │
│  ✓ collective_manager.search()│
└────────┬──────────────────────┘
         │
         │ build_agent_context()
         ↓
┌───────────────────────────────┐
│    Decision Memory Context    │
│  (decision_memory_context.py) │
│  ✓ query_memory()             │
│  ✓ retrieve_similar_cases()    │
│  ✓ get_context()               │
└────────┬──────────────────────┘
         │
         │ memory_context
         ↓
┌───────────────────────────────┐
│     Decision Engine            │
│  (decision_engine.py)          │
│  ✓ make_decision()             │
│  ✓ record_decision()           │
└────────┬──────────────────────┘
         │
         │ decision + outcome
         ↓
┌───────────────────────────────┐
│     Action                     │
│  (Agent Runtime Execution)     │
└────────┬──────────────────────┘
         │
         │ execute → result
         ↓
┌───────────────────────────────┐
│    Decision Feedback           │
│  (decision_feedback_handler.py)│
│  ✓ store_decision_result()    │
│  ✓ update_fitness()            │
└────────┬──────────────────────┘
         │
         │ store_memory()
         ↓
┌───────────────────────────────┐
│   Collective Memory             │
│  (CollectiveMemoryManager)     │
│  ✓ VectorIndex.search()        │
│  ✓ store_memory()              │
│  ✓ build_agent_context()       │
└────────┬──────────────────────┘
         │
         │ (opcjonalnie)
         ↓
┌───────────────────────────────┐
│    RAG Retrieval               │
│  (rag_retrieval.py)            │
│  ✓ query_expansion()           │
│  ✓ rerank_results()            │
│  ✓ format_context()            │
└───────────────────────────────┘
```

### Przepływ danych z punktami integracji:

```
1. Memory Retrieval → Decision Context
   AgentRuntime.receive_contract() 
   ↓
   memory_integration.get_agent_context()
   ↓
   collective_manager.build_agent_context()
   ↓
   decision_engine.receive_contract(contract, memory_context)

2. Decision Engine → Memory Storage
   DecisionEngine.make_decision()
   ↓
   AgentRuntime._record_decision_and_observation()
   ↓
   memory_integration.store_decision()
   ↓
   collective_manager.store_memory()

3. Feedback Loop
   AgentRuntime.execute_cycle()
   ↓
   decision_feedback_handler.process_outcome()
   ↓
   memory_integration.store_feedback()
   ↓
   collective_manager.store_memory()
```

---

## 6. PODSUMOWANIE I REKOMENDACJE

### 🎯 Kluczowe wnioski:

1. **Integracja jest wykonalna z minimalnymi zmianami w istniejących plikach**
2. **Keć `AgentRuntimeManager` ma już pole `collective_manager` - to dobra baza startowa**
3. **`CollectiveMemoryManager` jest w pełni funkcjonujący i gotowy do użycia**
4. **Brak jest jedynie warstwy abstrakcji i połączenia między komponentami**

### 📋 Nowe pliki wymagane (priorytet):

| Plik | Priorytet | Zależności | Status |
|------|----------|------------|--------|
| `SSI_V5/agents/memory_integration.py` | 🔴 **WYSOKI** | Brak | **POTRZEBNY** |
| `SSI_V5/agents/decision_memory_context.py` | 🔴 **WYSOKI** | memory_integration.py | **POTRZEBNY** |
| `SSI_V5/agents/decision_feedback_handler.py` | 🟡 **ŚREDNI** | decision_memory_context.py | **POTRZEBNY** |
| `SSI_V5/memory/collective_memory/rag_retrieval.py` | 🟡 **ŚREDNI** | CollectiveMemoryManager | **POTRZEBNY** |
| `SSI_V5/memory/collective_memory/knowledge_graph.py` | 🟢 **NISKI** | rag_retrieval.py | **OPCJONALNY** |

### 🔧 Minimalne zmiany w istniejących plikach:

1. **`agents/agent_runtime.py`**:
   - Dodać referencję do `CollectiveMemoryManager` w `AgentRuntimeManager`
   - Zmodyfikować `_process_contract()` - pobieranie kontekstu pamięci
   - Zmodyfikować `_record_decision_and_observation()` - zapis do pamięci kolektywnej

2. **`agents/decision_engine.py`**:
   - Dodać referencję do `CollectiveMemoryManager`
   - Zmodyfikować `receive_contract()` - akceptować `memory_context`
   - Zmodyfikować `make_decision()` - uwzględniać kontekst pamięci

3. **`agents/agent_runtime.py` (klasa `AgentRuntime`)**:
   - Dodać metodę do obsługi połączenia z pamięcią kolektywną

### ⚡ gotowy do implementacji ETAP 0

**Tak - System jest gotowy do implementacji ETAP 0.**

Wszystkie wymagane komponenty istnieją lub są jasno zidentyfikowane. Integracja polega głównie na:
1. Utworzeniu warstwy abstrakcji (nowe pliki)
2. Połączeniu istniejących komponentów (minimalne modyfikacje)
3. Testowaniu przepływu danych

**Nie ma blokad technicznych.**