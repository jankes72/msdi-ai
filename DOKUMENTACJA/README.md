# 📚 SSI V5 - DOKUMENTACJA SYSTEMOWA

**Ostatnia aktualizacja:** 2026-07-31  
**Sprint:** 11.5  
**Status:** Kompletna dokumentacja projektowa  

---

## 📋 SPIS TREŚCI

### 🎯 Dokumentacja Sprintu 11.5 (Obecny stan)

| **Plik** | **Opis** | **Status** |
|----------|----------|------------|
| [SSRINT_11_5_ARCHITECTURE.md](../SPRINT_11_5_ARCHITECTURE.md) | Główna dokumentacja architektury (oryginalna) | ✅ Istnieje |
| [SSI_V5_PART1_AKTUALNY_STAN.md](SSI_V5_PART1_AKTUALNY_STAN.md) | **Część 1-3:** Analiza aktualnego systemu, mapa cyklu agenta, model 10 cykli, struktura pamięci | ✅ Nowy |
| [SSI_V5_PART2_PRZYSZLE_MODULY.md](SSI_V5_PART2_PRZYSZLE_MODULY.md) | **Część 4-8:** Przyszłe moduły, dokumentacja, mapa plików, roadmapa Sprintów 12-20 | ✅ Nowy |

---

## 📖 STRUKTURA DOKUMENTACJI

### CZĘŚĆ 1: Analiza Aktualnego Systemu (SSI_V5_PART1_AKTUALNY_STAN.md)
- **1.1. Punkty wejścia i uruchomienie systemu**
  - `start_ssi.py` (PRODUCTION)
  - `start_ssi_test.py` (TEST MODE)
  - Przepływ uruchomienia

- **1.2. Przepływ danych w systemie**
  - Diagram przepływu od uruchomienia do zapisu
  - Inicjalizacja: Runtime Controller → Agent Manager → Collectors
  - Runtime Loop: Cycle → Collect → Agents ×6 → Save

- **1.3. Tworzenie agentów**
  - `runtime_controller.py` → `_initialize_agents()`
  - `agent_manager.py` → `create_agent()`
  - `agent_runtime.py` → `__init__()`

- **1.4. Wykonanie cyklu pojedynczego agenta**
  - Sekwencyjny przepływ: load_memory → run_cycle → save_memory
  - Krok po kroku: Analiza → Decyzja → Zapis doświadczenia → Aktualizacja historii

- **1.5. Kolektory (V2, V3, V4, External)**
  - Lokalizacja: `SSI/v5/input_layer/`
  - Rola i integracja

- **1.6. Zapis pamięci agenta**
  - Proces: `AgentMemoryStore.save_to_disk()`
  - Serializacja: enum → string
  - Lokalizacja: `SSI/memory/agents/agent_X/`

- **1.7. Zapis stanu systemu**
  - Proces: `StateManager.save_state()`
  - Zawartość: `runtime_state.json`

---

### CZĘŚĆ 2: Mapa Jednego Cyklu Agenta (SSI_V5_PART1_AKTUALNY_STAN.md)
- **2.1. Dokładny przepływ (diagram sekwencyjny)**
  - Cycle N → state_manager.start_cycle()
  - _collect_current_data() → {v2, v3, v4, external}
  - FOR agent_id IN ["01"-"06"]:
    - load_memory() → JSON files
    - run_cycle() → analysis → decision → save_experience
    - save_memory() → JSON files
  - state_manager.end_cycle()
  - save_state()

- **2.2. Pliki biorące udział w jednym cyklu**
  - Tabela: Krok → Plik → Metoda → Operacja

- **2.3. Dane wejściowe i wyjściowe agenta**
  - Wejściowe: `collector_data`, `world_context`, `agent_memory`
  - Wyjściowe: `result` (decision, analysis), new memory entries

---

### CZĘŚĆ 3: Model 10 Cykli Testowych (SSI_V5_PART1_AKTUALNY_STAN.md)
- **3.1. Schemat wykonywania**
  - CYCLE 1: Agent_01(It#1) → Agent_02(It#2) → ... → Agent_06(It#6)
  - CYCLE 2: Agent_01(It#7) → ... → Agent_06(It#12)
  - ...
  - CYCLE 10: Agent_01(It#55) → ... → Agent_06(It#60)

- **3.2. Podsumowanie 10 cykli**
  - Metryki: 60 iteracji, 60 decyzji, 120 nowych wpisów pamięci

- **3.3. Typy agentów w TEST MODE**
  - Agent_01: ANALYTICAL (risk=0.3, analysis=0.9)
  - Agent_02: CREATIVE (risk=0.7, analysis=0.5, creativity=0.9)
  - Agent_03: CONSERVATIVE (risk=0.2, analysis=0.8)
  - Agent_04: RISK_TAKER (risk=0.9, analysis=0.4)
  - Agent_05: BALANCED (risk=0.5, analysis=0.7)
  - Agent_06: EXPLORER (risk=0.6, analysis=0.6, creativity=0.8)

---

### CZĘŚĆ 4: Struktura Pamięci (SSI_V5_PART1_AKTUALNY_STAN.md)
- **4.1. Aktualna struktura (Sprint 11.5)**
  ```
  SSI/memory/agents/agent_X/
  ├── personality.json    # PERSONALITY
  ├── behavior.json      # BEHAVIOR
  ├── strategy.json      # STRATEGY
  └── history.json       # HISTORY
  ```

- **4.2. Typy pamięci i ich rola**
  - PERSONALITY: Cechy osobowości, zaufanie (rzadko aktualizowane)
  - BEHAVIOR: Zachowania, akcje (co cykl - nowy wpis)
  - STRATEGY: Strategie, statystyki (co cykl - aktualizacja liczników)
  - HISTORY: Zdarzenia, decyzje (co cykl - nowy wpis)
  - RELATIONSHIP: Relacje między agentami (przyszłość)
  - PROMPT: Prompty dla LLM (przyszłość)

- **4.3. Przyszła struktura (Sprint 12+)**
  ```
  SSI/memory/
  ├── agents/           # ✅ Aktualnie (indywidualna)
  ├── collective/      # 🟡 Sprint 12 (zbiorowa)
  │   ├── global_memory.json
  │   ├── strategy_memory.json
  │   ├── knowledge_memory.json
  │   └── interaction_memory.json
  └── long_term/        # 🟡 Sprint 12 (długoterminowa)
      ├── events_history.json
      ├── agents_evolution.json
      ├── decisions_archive.json
      ├── errors_log.json
      └── patterns_library.json
  ```

- **4.4. Opis plików przyszłościowych**
  - global_memory.json: Agregacja wiedzy z V2,V3,V4,external
  - interaction_memory.json: Komunikacja agent-agent
  - events_history.json: Archiwum zdarzeń z timestampem
  - patterns_library.json: Biblioteka wykrytych wzorców

---

### CZĘŚĆ 5: Przyszłe Moduły SSI V5 (SSI_V5_PART2_PRZYSZLE_MODULY.md)

#### 5.1. Long Term Memory System (Sprint 12)
- **Cel:** Stała pamięć całego kolektywu
- **Pliki:** `long_term_memory.py`, pliki w `SSI/memory/long_term/`
- **Funkcjonalności:** Serializacja, indeksowanie, backup, kompresja
- **Integracja:** StateManager, AgentMemoryStore
- **Metryki:** 100% odzysk danych, <100ms wyszukiwanie

#### 5.2. Agent Communication Analyzer (Sprint 13)
- **Cel:** Analiza rozmów entre agentami
- **Pliki:** `communication_analyzer.py`, `interaction_memory.json`
- **Funkcjonalności:** Monitorowanie, wzorce współpracy, wykrywanie konfliktów
- **Raporty:** Communication Patterns, Collaboration Metrics, Conflict Analysis
- **Metryki:** Współczynnik synergii, efektywność zespołowa

#### 5.3. LLM Decision Layer (Sprint 15)
- **Cel:** Warstwa LLM do wsparcia decyzyjnego (NIE zastępuje agenta)
- **Pliki:** `llm_client.py`, `llm_decision_layer.py`, `prompt_builder.py`
- **Funkcjonalności:** Analiza decyzji, sugestie, weryfikacja, rekomendacje
- **Pamięć:** `memory/language_model/` (prompty, kontekst, historia odpowiedzi)
- **Metryki:** Czas odpowiedzi <5s, token usage <1000/cykl

#### 5.4. Behavioral Calibration Engine (Sprint 14)
- **Cel:** Dynamiczna adaptacja wag behawioralnych
- **Parametry:** risk_tolerance, analysis_depth, creativity, trust_v2/v3/v4/external
- **Mechanizmy:** Success/Failure/Trend/Feedback-Based Adaptation
- **Algorytmy:** Gradient Descent, Reinforcement Learning, Bayesian Optimization
- **Metryki:** Poprawa decyzji +15%, czas adaptacji <10 cykli

#### 5.5. Collective Intelligence Layer (Sprint 16)
- **Cel:** Inteligencja zbiorowa zespołu agentów
- **Komponenty:** Knowledge Aggregator, Knowledge Graph, Consensus Builder, Resource Allocator
- **Funkcjonalności:** Agregacja wiedzy, konsensus, alokacja zasobów, wykrywanie synergii
- **Metryki:** Współczynnik synergii +30%, jakość decyzji zespołowych +20%

---

### CZĘŚĆ 6: Dokumentacja Systemowa (SSI_V5_PART2_PRZYSZLE_MODULY.md)

#### 6.1. Lista dokumentów do utrzymywania

| **Dokument** | **Cel** | **Odpowiedzialny** | **Kiedy aktualizować** |
|--------------|---------|-------------------|------------------------|
| SPRINT_11_5_ARCHITECTURE.md | Dokumentacja architektury Sprint 11.5 | Architekt | Po Sprincie 11.5 ✅ |
| PROJECT_JOURNAL.md | Dziennik projektu, historia zmian | Kierownik | Po każdym Sprincie ⏳ |
| ROADMAP.md | Plan rozwoju systemu | Architekt | Przed Sprintem ⏳ |
| MEMORY_ARCHITECTURE.md | Dokumentacja systemu pamięci | Specjalista pamięci | Przed Sprintem 12 ⏳ |
| COLLECTIVE_MEMORY_DESIGN.md | Projekt pamięci zbiorowej | Architekt pamięci | Przed Sprintem 12 ⏳ |
| AGENT_BEHAVIOR_MODEL.md | Model zachowań agentów | Psycholog systemu | Przed Sprintem 13 ⏳ |
| LLM_INTEGRATION_PLAN.md | Plan integracji z LLM | Inżynier LLM | Przed Sprintem 15 ⏳ |
| DECISION_FLOW_DIAGRAM.md | Diagramy przepływu decyzji | Architekt | Po zmianach ⏳ |
| TEST_PROTOCOL.md | Protokoły testowania | Inżynier QA | Przed Sprintem 12 ⏳ |

#### 6.2. Szablon dokumentów
- Nagłówek z metadany (Sprint, Data, Wersja, Status, Autor)
- Sekcje: Cel, Kontekst, Główna treść, Decyzje, Zależności, Implementacja, Testowanie, Historia zmian, Załączniki

#### 6.3. Konwencje nazewnictwa
- `[NAZWA]_ARCHITECTURE.md` - Dokumentacja architektoniczna
- `[NAZWA]_DESIGN.md` - Projekt modułów
- `[NAZWA]_PLAN.md` - Plany integracji
- `[NAZWA]_JOURNAL.md` - Dzienniki
- `[NAZWA]_DIAGRAM.md` - Diagramy
- `[NAZWA]_PROTOCOL.md` - Protokoły

---

### CZĘŚĆ 7: Mapa Plików Systemu (SSI_V5_PART2_PRZYSZLE_MODULY.md)

#### 7.1. Tabela plików - Stan obecny (Sprint 11.5)

| **Moduł** | **Plik** | **Lokalizacja** | **Odpowiedzialność** |
|-----------|----------|----------------|--------------------|
| Runtime | runtime_controller.py | SSI/v5/runtime/ | Sterowanie cyklem, agentami, collectorami |
| Runtime | runtime_config.py | SSI/v5/runtime/ | Konfiguracja systemu |
| Runtime | state_manager.py | SSI/v5/runtime/ | Zarządzanie stanem |
| Runtime | scheduler.py | SSI/v5/runtime/ | Planowanie zadań |
| Agenci | agent_runtime.py | SSI/v5/agents/ | Cykl pojedynczego agenta |
| Agenci | agent_manager.py | SSI/v5/agents/ | Zarządzanie agentami |
| Agenci | agents_config.py | SSI/v5/agents/ | Konfiguracja typów agentów |
| Agenci | agent_memory_store.py | SSI/v5/agents/ | Pamięć agenta |
| Agenci | agent_state.py | SSI/v5/agents/ | Stan agenta |
| Kolektory | v2_collector.py | SSI/v5/input_layer/ | Dane światowe |
| Kolektory | v3_collector.py | SSI/v5/input_layer/ | Wiedza |
| Kolektory | v4_collector.py | SSI/v5/input_layer/ | Dane o agentach |
| Kolektory | external.py | SSI/v5/input_layer/external/ | Dane zewnętrzne |

#### 7.2. Tabela plików - Przyszłe moduły (Sprint 12-16)

| **Moduł** | **Plik** | **Sprint** |
|-----------|----------|------------|
| Pamięć | long_term_memory.py, collective_memory.py, memory_analytics.py | 12 |
| Laboratorium | sandbox.py, experiment_runner.py, results_analyzer.py, strategy_optimizer.py | 13 |
| Analiza | communication_analyzer.py | 13 |
| Zachowanie | calibration_engine.py | 14 |
| LLM | llm_client.py, llm_decision_layer.py, prompt_builder.py, llm_config.py | 15 |
| Inteligencja | collective_intelligence.py, knowledge_graph.py, consensus_builder.py, resource_allocator.py | 16 |

#### 7.3. Wizualizacja struktur katalogów
- **Obecna struktura (Sprint 11.5)** - zobacz dokument
- **Przyszła struktura (Sprint 12+)** - zobacz dokument

---

### CZĘŚĆ 8: Roadmap - Plan Sprintów 12-20 (SSI_V5_PART2_PRZYSZLE_MODULY.md)

#### Sprint 12: Memory Architecture
- **Cel:** Rozbudowa systemu pamięci o warstwy zbiorowe i długoterminowe
- **Zadania:** Long Term Memory, Collective Memory, Serialization, Indexing, Backup
- **Kryteria:** Pamięć zachowuje stan między sesjami, backupy działają
- **Dokumentacja:** MEMORY_ARCHITECTURE.md, COLLECTIVE_MEMORY_DESIGN.md

#### Sprint 13: Agent Laboratory
- **Cel:** Środowisko do eksperymentów i autonomicznego uczenia
- **Zadania:** Sandbox, Experiment Runner, Results Analyzer, Strategy Optimizer, Communication Analyzer
- **Kryteria:** Eksperymenty uruchamiane automatycznie, wyniki analizowane
- **Dokumentacja:** AGENT_BEHAVIOR_MODEL.md, LAB_PROTOCOL.md

#### Sprint 14: Behavioral Engine
- **Cel:** Dynamiczna adaptacja zachowań agentów
- **Zadania:** Calibration Engine z mechanizmami adaptacji
- **Kryteria:** Agenci adaptują parametry na podstawie wyników
- **Dokumentacja:** AGENT_BEHAVIOR_MODEL.md (aktualizacja)

#### Sprint 15: LLM Integration Layer
- **Cel:** Integracja z modelami językowymi
- **Zadania:** LLM Client, Prompt Builder, LLM Decision Layer, Token Management
- **Kryteria:** LLM analizuje decyzje, system działa offline
- **Dokumentacja:** LLM_INTEGRATION_PLAN.md, LLM_CONFIG.md

#### Sprint 16: Collective Intelligence Layer
- **Cel:** Inteligencja zbiorowa zespołu
- **Zadania:** Knowledge Aggregator, Knowledge Graph, Consensus Builder, Resource Allocator
- **Kryteria:** Knowledge Graph działa, conflict resolution rozwiązuje 90% konfliktów
- **Dokumentacja:** COLLECTIVE_INTELLIGENCE_DESIGN.md

#### Sprint 17-20: Optymalizacja, Bezpieczeństwo, UI, Wdrożenie
- **Sprint 17:** Optimization & Performance
- **Sprint 18:** Security & Safety
- **Sprint 19:** User Interface & Monitoring
- **Sprint 20:** Deployment & Production Readiness

---

## 🎯 ZASADY DALSZEGO ROZWOJU

### 1. 🛡️  Niemodyfikowalność Sprintu 11.5
- **Runtime Controller, Agent Runtime, Memory System działają poprawnie**
- ❌ **NIE wprowadzać zmian, które mogą złamać obecny system**
- ✅ Nowe funkcjonalności dodawać jako **osobne moduły**

### 2. ✅ Kompatybilność wsteczna
- Nowe moduły muszą być kompatybilne z istniejącym systemem
- Możliwość włączania/wyłączania nowych feature flagami (np. `enable_llm=False`)

### 3. 🧪 Testowanie
- Każdy nowy moduł musi mieć testy jednostkowe
- Testy integracyjne z istniejącym runtime
- Testy wydajnościowe dla krytycznych modułów
- Kryteria akceptacji muszą być zdefiniowane

### 4. 📚 Dokumentacja
- Każdy Sprint kończy się zaktualizowaną dokumentacją
- Nowe moduły muszą mieć swoją dokumentację (wg szablonu)
- Zmiany w strukturze plików muszą być udokumentowane
- Dokumentacja jest częścią definicji gotowości Sprintu

### 5. 📊 Wersjonowanie
- Używać **SemVer** (MAJOR.MINOR.PATCH) dla modułów
- Wersje muszą być **kompatybilne między modułami**
- Zmiany **breaking** (niezgodne wstecznie) **muszą** być:
  - Wyraźnie zaznaczone w dokumentacji
  - Komunikowane zespołowi
  - Wprowadzane w nowej wersji MAJOR

---

## 📁 STRUKTURA KATALOGU DOKUMENTACJI

```
DOKUMENTACJA/
├── README.md                          # Ten plik - spis treści
├── SSI_V5_PART1_AKTUALNY_STAN.md    # Część 1-4: Analiza, Mapa Cyklu, Model Testowy, Pamięć
└── SSI_V5_PART2_PRZYSZLE_MODULY.md  # Część 5-8: Moduły, Dokumentacja, Mapa Plików, Roadmap

/
├── SPRINT_11_5_ARCHITECTURE.md         # Oryginalna dokumentacja Sprintu 11.5
├── PROJECT_JOURNAL.md                # Dziennik projektu (do uzupełnienia)
└── ROADMAP.md                        # Roadmapa (do uzupełnienia)

SSI/
├── v5/
│   ├── runtime/
│   │   └── [runtime_controller.py, runtime_config.py, state_manager.py, scheduler.py]
│   ├── agents/
│   │   └── [agent_runtime.py, agent_manager.py, agents_config.py, agent_memory_store.py, agent_state.py]
│   └── input_layer/
│       └── [collector_manager.py, v2_collector.py, v3_collector.py, v4_collector.py, external/]
└── memory/
    └── agents/
        └── [agent_01/ ... agent_06/]
            └── [personality.json, behavior.json, strategy.json, history.json]
```

---

## 🚀 JAK KORZYSTAĆ Z DOKUMENTACJI

### 1. Początkujący użytkownik
- Przeczytaj **SPRINT_11_5_ARCHITECTURE.md** - ogólny opis systemu
- Zapoznaj się z **SSI_V5_PART1_AKTUALNY_STAN.md** - jak działa obecny system
- Uruchom **start_ssi_test.py** - zobacz działanie w praktyce

### 2. Developer rozwijający system
- **SSI_V5_PART1_AKTUALNY_STAN.md** - dokumentacja obecnej architektury
- **SSI_V5_PART2_PRZYSZLE_MODULY.md** - plan rozwoju, nuevos moduły
- Zawsze sprawdzaj **PROJECT_JOURNAL.md** - historia zmian i znane problemy

### 3. Architekt systemu
- Przestudiuj **SSI_V5_PART2_PRZYSZLE_MODULY.md** - Część 5 (przyszłe moduły)
- Zapoznaj się z **Częścią 7** (mapa plików) i **Częścią 8** (roadmapa)
- Aktualizuj **ROADMAP.md** przed każdym Sprintem

---

## 🔍 SŁOWNIK POJĘĆ

| **Pojęcie** | **Opis** |
|-------------|----------|
| **Runtime Controller** | Główny kontroler systemu, zarządza cyklem pracy |
| **Agent Runtime** | Kluczowy moduł wykonywania pojedynczego agenta |
| **Continuous Loop** | Ciągła pętla pracy systemu (do 5 godzin) |
| **TEST_MODE** | Tryb testowy: 10 cykli, 60 iteracji, szybki |
| **PRODUCTION_MODE** | Tryb produkcyjny: 5 godzin, wolniejszy |
| **MemoryType** | Enum definujący typy pamięci (PERSONALITY, BEHAVIOR, etc.) |
| **UnifiedInputPackage** | Zunifikowany pakiet danych z wszystkich collectorów |
| **Agent_01-06** | 6 agentów o różnych typach osobowości |
| **Collectory** | Moduły zbierające dane: V2, V3, V4, External |

---

## 📞 KONTAKT I INFORMACJE

**Ostatnia aktualizacja:** 2026-07-31  
**Wersja dokumentacji:** 1.0.0  
**Status:** Kompletna dokumentacja projektowa po Sprincie 11.5  

**Pliki powiązane:**
- [главный файл архитектуры](../SPRINT_11_5_ARCHITECTURE.md)
- [Część 1: Aktualny stan](SSI_V5_PART1_AKTUALNY_STAN.md)
- [Część 2: Przyszłe moduły](SSI_V5_PART2_PRZYSZLE_MODULY.md)

---

**🎉 DOKUMENTACJA ZAKOŃCZONA**
