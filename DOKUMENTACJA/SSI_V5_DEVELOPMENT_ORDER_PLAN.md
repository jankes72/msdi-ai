# SSI V5 - DEVELOPMENT ORDER PLAN
# Plan Kolejności Budowy Systemu

**Data utworzenia:** 2026-08-03  
**Wersja:** 1.0.0  
**Status:** PLAN GŁÓWNY - OCZEKUJE NA ZATWIERDZENIE  
**Autor:** Mistral Vibe - CLI Coding Agent  
**Typ dokumentu:** ARCHITEKTURA KOLEJNOŚCI IMPLEMENTACJI

---

## 📋 SPIS TREŚCI

1. [Podsumowanie Executive](#1-podsumowanie-executive)
2. [Aktualny Stan Projektu](#2-aktualny-stan-projektu)
3. [Mapa Zależności Między Modułami](#3-mapa-zależności-między-modułami)
4. [Kolejność Etapów Budowy](#4-kolejność-etapów-budowy)
5. [Szczegółowy Plan Sprintów](#5-szczegółowy-plan-sprintów)
6. [Konflikty do Rozstrzygnięcia](#6-konflikty-do-rozstrzygnięcia)
7. [Optymalna Kolejność Budowy](#7-optymalna-kolejność-budowy)

---

## 1. PODSUMOWANIE EXECUTIVE

**CEL:** Ustalenie optymalnej kolejności budowy SSI V5, aby **nie robić przebudowy później**.

**GŁÓWNE WNIOSKI:**
- System SSI V5 posiada **solidny fundament** (Sprint 11.5 ukończony)
- Zidentyfikowano **23 niespójności** (zob. SSI_V5_ARCHITECTURE_CONSISTENCY_REPORT.md)
- **8 decyzji projektowych** musi zostać podjętych PRZED rozpoczęciem implementacji
- Optymalna kolejność budowy opiera się na **zależnościach hierarchicznych**

**ZASADA GŁÓWNA:**
> **Budować od fundamentów do warstw wyższego poziomu.**
> **Upewnić się, że każda warstwa jest stabilna przed budowaniem następnej.**

---

## 2. AKTUALNY STAN PROJEKTU

### 2.1. CO JUŻ MAMY (✅ ZAIMPLEMENTOWANE)

| **Kategoria** | **Moduły** | **Lokalizacja** | **Status** |
|--------------|-------------|----------------|------------|
| **Runtime** | Runtime Controller + State Manager + Scheduler | `SSI/v5/runtime/` | ✅ **STABILNY** |
| **Runtime** | LLM Queue Manager | `SSI/v5/runtime/llm_queue/` | ✅ **STABILNY (FAZA 1)** |
| **Agenci** | Agent Runtime + Agent Manager + Agent Memory Store | `SSI/v5/agents/` | ✅ **STABILNY** |
| **Agenci** | Strategy Laboratory (8 plików, ~240KB) | `SSI/v5/agents/strategy_laboratory/` | ✅ **STABILNY (FAZA 1)** |
| **Input Layer** | Collector Manager + V2/V3/V4 Collectors | `SSI/v5/input_layer/` | ✅ **STABILNY** |
| **Input Layer** | External Collector (3 pliki, ~60KB) | `SSI/v5/input_layer/external/` | ✅ **STABILNY (NOWY)** |
| **Memory** | Model Memory Store (5 typów) | `SSI/v5/memory/` | ✅ **STABILNY** |
| **Teacher** | Teacher Engine | `SSI/v5/teacher/` | ✅ **STABILNY** |
| **Pamięć Agentów** | JSON Files (8 typów na agenta) | `SSI/memory/agents/agent_01-06/` | ✅ **STABILNY** |

### 2.2. FUNDAMENTY GOTOWE

```
┌─────────────────────────────────────────────────────────────┐
│                    FUNDAMENT SSI V5 (Sprint 11.5)                │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │   RUNTIME       │    │     AGENTS       │    │ INPUT LAYER  │ │
│  │  Controller     │    │  01-06          │    │ V2/V3/V4    │ │
│  │  State         │    │  Memory         │    │ External    │ │
│  │  Scheduler     │    │  Strategy Lab   │    │             │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
│                              │                                      │
│                              ▼                                      │
│                    ┌─────────────────────────┐                   │
│                    │  LLM QUEUE + TEACHER     │                   │
│                    │  + MODEL MEMORY          │                   │
│                    └─────────────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

**Status:** ✅ **GOTOWY DO ROZBUDOWY**

---

## 3. MAPA ZALEŻNOŚCI MIĘDZY MODUŁAMI

### 3.1. HIERARCHIA ZALEŻNOŚCI

```
POZIOM 0 - FUNDAMENT (✅ GOTOWY)
┌─────────────────────────────────────────────────────────────┐
│ Runtime Controller + State Manager + Scheduler               │
│ Agent Runtime + Agent Manager + Agent Memory                 │
│ Collectors (V2/V3/V4/External) + Teacher Engine               │
│ LLM Queue Manager + Model Memory Store                       │
│ Strategy Laboratory + External Collector                      │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
POZIOM 1 - INTEGRACJA PAMIĘCI (⏳ Sprint 12)
┌─────────────────────────────────────────────────────────────┐
│ Long Term Memory + Collective Memory + Memory Analytics     │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
POZIOM 2 - DECYZJE I MODELE (⏳ Sprint 12)
┌─────────────────────────────────────────────────────────────┐
│ Decision Engine + Model Ecosystem + Decision Replay System   │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
POZIOM 3 - KONTEKST I ROUTING (⏳ Sprint 13-14)
┌─────────────────────────────────────────────────────────────┐
│ Memory Context Builder + Supervisor Model + Agent Lifecycle   │
│ Prompt Routing System + Calibration Engine                    │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
POZIOM 4 - INTELIGENCJA KOLEKTYWNA (⏳ Sprint 14-16)
┌─────────────────────────────────────────────────────────────┐
│ Knowledge Aggregator + Knowledge Graph + Consensus Builder    │
│ Resource Allocator + AI Lab Request Pipeline                 │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
POZIOM 5 - INTEGRACJA LLM (⏳ Sprint 15)
┌─────────────────────────────────────────────────────────────┐
│ LLM Client + LLM Decision Layer + Prompt Builder              │
└─────────────────────────────────────────────────────────────┘
```

### 3.2. MACIERZ ZALEŻNOŚCI

| **Moduł** | **Zależy od** | **Wymagany przed** | **Krytyczność** | **Sprint** |
|-----------|---------------|-------------------|------------------|------------|
| **Decision Engine** | Runtime, Agent Memory, Model Memory | Replay System, Collective Intelligence | 🔴 **KRYTYCZNY** | 12 |
| **Model Ecosystem** | Runtime, LLM Queue | Decision Engine, LLM Integration | 🔴 **KRYTYCZNY** | 12 |
| **Decision Replay System** | Decision Engine, Long Term Memory | Collective Intelligence, AI Lab | 🔴 **KRYTYCZNY** | 12 |
| **Long Term Memory** | Runtime, State Manager | Decision Replay, Collective Memory | 🔴 **KRYTYCZNY** | 12 |
| **Collective Memory** | Long Term Memory, Agent Memory | Decision Replay, Collective Intelligence | 🟡 **WYSOKI** | 12 |
| **Memory Context Builder** | Long Term Memory, Collective Memory | LLM Integration | 🟡 **WYSOKI** | 13 |
| **Supervisor Model** | Decision Engine, Agent Runtime | Collective Intelligence | 🟡 **WYSOKI** | 13 |
| **LLM Client** | Runtime, LLM Queue | LLM Decision Layer, Prompt Builder | 🟡 **WYSOKI** | 15 |
| **LLM Decision Layer** | LLM Client, Model Ecosystem | Collective Intelligence | 🟡 **WYSOKI** | 15 |
| **Knowledge Aggregator** | Collective Memory, Long Term Memory | Knowledge Graph | 🟡 **WYSOKI** | 16 |

### 3.3. MODUŁY BLOKUJĄCE (Krytyczna Ścieżka)

```
Decision Engine + Model Ecosystem + Decision Replay System
       │                         │                         │
       ▼                         ▼                         ▼
  All Other Modules (Collective Intelligence, LLM Integration, etc.)
```

---

## 4. KOLEJNOŚĆ ETAPÓW BUDOWY

### 4.1. ETAP 1 - FUNDAMENTY PAMIĘCI (Sprint 12 - Faza A: 0-14 dni)

**Cel:** Utworzenie systemu pamięci długoterminowej i zbiorowej.

**Moduły:**
1. Long Term Memory Manager (`SSI/v5/memory/long_term_memory.py`)
2. Collective Memory Manager (`SSI/v5/memory/collective_memory.py`)
3. Memory Serialization
4. Memory Indexing
5. Memory Backup System

**Dlaczego teraz:**
- Decision Replay System **wymaga** Long Term Memory
- Collective Intelligence **wymaga** Collective Memory
- Wszystkie wyższe warstwy opierają się na pamięci

**Integracja:** LongTermMemory ↔ StateManager, AgentMemoryStore, Runtime

**Kryteria zakończenia:**
- Pamięć zachowuje stan między uruchomieniami (100%)
- Collective Memory działa z agentami
- Czas wyszukiwania <100ms dla 1000+ wpisów
- Zużycie pamięci <1GB dla 10000 wpisów

---

### 4.2. ETAP 2 - SILNIK DECYZYJNY (Sprint 12 - Faza B: 14-28 dni)

**Cel:** Utworzenie centralnego silnika podejmowania decyzji.

**Moduły:**
1. Decision Engine
2. Model Ecosystem
3. Decision Replay System

**Dlaczego później (ale w tym samym Sprincie):**
- Decision Engine **wymaga** Long Term Memory (z Fazy A)
- Model Ecosystem **wymaga** LLM Queue (już gotowy)
- Decision Replay System **wymaga** Decision Engine + Long Term Memory

**⚠️ KRYTYCZNE:** Te 3 moduły **blokują** całą resztę systemu!

**Integracja:** DecisionEngine ↔ AgentRuntime, ModelEcosystem, LongTermMemory

**Kryteria zakończenia:**
- Decision Engine ocenia decyzje agentów
- Model Ecosystem zarządza wieloma modelami
- Decision Replay System odtwarza każdą decyzję z kontekstem

---

### 4.3. ETAP 3 - KONTEKST I OPTYMALIZACJA (Sprint 13 - 28-42 dni)

**Cel:** Budowa warstwy kontekstu i optymalizacji.

**Moduły:**
1. Memory Context Builder
2. Supervisor / Controller Model
3. Agent Lifecycle Manager
4. Communication Analyzer
5. Sandbox Environment
6. Experiment Runner

**Równoległość:** Communication Analyzer, Sandbox, Experiment Runner **mogą być budowane równolegle**

**Dlaczego teraz:** Wszystkie wymagają fundamentów z Sprintu 12

---

### 4.4. ETAP 4 - BEHAVIOR I OPTYMALIZACJA (Sprint 14 - 42-56 dni)

**Moduły:**
1. Calibration Engine
2. Strategy Optimizer
3. Behavioral Analysis

**Dlaczego teraz:** Wymagają Long Term Memory (Sprint 12) i Agent Runtime (gotowy)

---

### 4.5. ETAP 5 - INTEGRACJA LLM (Sprint 15 - 56-70 dni)

**Moduły:**
1. LLM Client
2. LLM Decision Layer
3. Prompt Builder
4. Prompt Routing System
5. AI Lab Request Pipeline

**Dlaczego teraz:** Wymagają Model Ecosystem i Decision Engine (Sprint 12)

---

### 4.6. ETAP 6 - INTELIGENCJA KOLEKTYWNA (Sprint 16 - 70-90 dni)

**Moduły:**
1. Knowledge Aggregator
2. Knowledge Graph
3. Consensus Builder
4. Resource Allocator

**Dlaczego teraz:** Wymagają Collective Memory (Sprint 12) i Decision Replay System (Sprint 12)

---

## 5. SZCZEGÓŁOWY PLAN SPRINTÓW

| **Sprint** | **Czas** | **Moduły** | **Cel** |
|------------|----------|------------|---------|
| **12A** | 0-14 dni | Long Term Memory, Collective Memory, Memory Analytics, Backup | Fundament pamięci |
| **12B** | 14-28 dni | Decision Engine, Model Ecosystem, Decision Replay System | Silnik decyzyjny |
| **13** | 28-42 dni | Memory Context Builder, Supervisor, Lifecycle, Communication, Sandbox, Experiment | Kontekst i laboratorium |
| **14** | 42-56 dni | Calibration Engine, Strategy Optimizer, Behavioral Analysis | Zachowanie i optymalizacja |
| **15** | 56-70 dni | LLM Client, Decision Layer, Prompt Builder, Routing, AI Lab Pipeline | Integracja LLM |
| **16** | 70-90 dni | Knowledge Aggregator, Graph, Consensus Builder, Resource Allocator | Inteligencja kolektywna |

---

## 6. KONFLIKTY DO ROZSTRZYGNIĘCIA

### 6.1. PRIORYTET 1 - Muszą zostać rozstrzygnięte PRZED Sprintem 12

**1. Priorytety modułów krytycznych**
- **Pytanie:** Czy implementować wszystkie 3 moduły (Decision Engine, Model Ecosystem, Decision Replay System) w Sprincie 12?
- **Opcje:** A) Wszystkie 3, B) 2 z 3, C) 1 z 3
- **Rekomendacja:** **A) Wszystkie 3** (muszą być razem, bo wzajemnie zależne)

**2. Status LLM Queue Manager**
- **Pytanie:** Czy LLM Queue Manager powinien być oficjalnie częścią architektury systemowej?
- **Rekomendacja:** **Tak** - dodać do SSI_V5_MASTER_SYSTEM_FLOW_ARCHITECTURE.md

**3. Status Strategy Laboratory**
- **Pytanie:** Czy Strategy Laboratory jest gotowy do użycia w Sprint 12?
- **Rekomendacja:** **Tak** - zaktualizować dokumentację o referencje do implementacji

**4. Status External Collector**
- **Pytanie:** Czy External Collector powinien zostać szczegółowo udokumentowany?
- **Rekomendacja:** **Tak** - dodać dokumentację i zintegrować z Collector Manager

### 6.2. PRIORYTET 2 - Wymagają decyzji w ciągu tygodnia

**5. Spójność nazewnictwa**
- **Pytanie:** Która konwencja nazewnictwa: dokumentacja (V2 Model Laboratory) czy kod (v2_collector.py)?
- **Rekomendacja:** **Zmienić dokumentację** na nazewnictwo kodu (mniej zmian, kod stabilny)

**6. Lokalizacja sieci V2**
- **Pytanie:** Gdzie powinny znajdować się sieci V2?
- **Rekomendacja:** **Zaktualizować dokumentację** - sieci w modele_kursy_przygotowane/, nie przenosić

**7. Status pamięci długoterminowej**
- **Pytanie:** Czy Long Term Memory i Collective Memory powinny zostać zaimplementowane w Sprincie 12?
- **Rekomendacja:** **Tak** - są fundamentem dla Decision Replay i Collective Intelligence

**8. Integracja z sieciami**
- **Pytanie:** Gdzie powinny znajdować się 15 sieci specjalistycznych?
- **Rekomendacja:** **Zaktualizować dokumentację** - scalić informacje o lokalizacji

---

## 7. OPTYMALNA KOLEJNOŚĆ BUDOWY SSI V5

### 7.1. ODPOWIEDŹ NA GŁÓWNE PYTANIE

**❓ Pytanie:** *"Jaka jest optymalna kolejność dalszej budowy SSI V5, aby nie robić przebudowy później?"*

**✅ Odpowiedź:**

```
ETAP 1 (Sprint 12 - 0-28 dni):
├── Faza 12A (0-14 dni): Long Term Memory + Collective Memory + Memory Analytics
└── Faza 12B (14-28 dni): Decision Engine + Model Ecosystem + Decision Replay System

ETAP 2 (Sprint 13 - 28-42 dni):
├── Memory Context Builder + Supervisor Model + Agent Lifecycle Manager
└── Communication Analyzer + Sandbox Environment + Experiment Runner

ETAP 3 (Sprint 14 - 42-56 dni):
└── Calibration Engine + Strategy Optimizer + Behavioral Analysis

ETAP 4 (Sprint 15 - 56-70 dni):
└── LLM Client + LLM Decision Layer + Prompt Builder + Prompt Routing + AI Lab Pipeline

ETAP 5 (Sprint 16 - 70-90 dni):
└── Knowledge Aggregator + Knowledge Graph + Consensus Builder + Resource Allocator
```

### 7.2. KLUCZOWE ZASADY

1. **Zasada 1:** Zawsze budować od fundamentów do warstw wyższego poziomu
2. **Zasada 2:** Nigdy nie budować modułu, jeśli jego zależności nie są gotowe
3. **Zasada 3:** Decision Engine, Model Ecosystem, Decision Replay System **muszą** zostać zaimplementowane w Sprincie 12
4. **Zasada 4:** Long Term Memory i Collective Memory **muszą** zostać zaimplementowane przed Decision Replay System
5. **Zasada 5:** LLM Integration **musi** zostać zaimplementowana przed Collective Intelligence

### 7.3. WIZUALIZACJA

```
SPRINT 11.5 (✅ ZAKOŃCZONY)
┌──────────────────────────────────────────┐
│ FUNDAMENT: Runtime + Agents + Collectors + │
│ Teacher + Memory + LLM Queue + Strategy Lab│
└──────────────────────────────────────────┘
                    │
                    ▼
SPRINT 12 (0-28 dni) - 🔴 KRYTYCZNY
┌──────────────────────────────────────────┐
│ 12A (0-14): Long Term + Collective Memory  │
│ 12B (14-28): Decision Engine + Model Ecosys│
│              + Decision Replay             │
└──────────────────────────────────────────┘
                    │
                    ▼
SPRINT 13 (28-42 dni) - 🟡 WAŻNY
┌──────────────────────────────────────────┐
│ Memory Context + Supervisor + Lifecycle   │
│ Communication + Sandbox + Experiment      │
└──────────────────────────────────────────┘
                    │
                    ▼
SPRINT 14 (42-56 dni) - 🟡 WAŻNY
┌──────────────────────────────────────────┐
│ Calibration + Strategy Optimization       │
│ + Behavioral Analysis                      │
└──────────────────────────────────────────┘
                    │
                    ▼
SPRINT 15 (56-70 dni) - 🟡 WAŻNY
┌──────────────────────────────────────────┐
│ LLM Client + Decision Layer + Prompt      │
│ Builder + Routing + AI Lab Pipeline       │
└──────────────────────────────────────────┘
                    │
                    ▼
SPRINT 16 (70-90 dni) - 🟢 KOLEKTYWNA
┌──────────────────────────────────────────┐
│ Knowledge Aggregator + Graph + Consensus  │
│ + Resource Allocator                      │
└──────────────────────────────────────────┘
```

---

## STATUS KOŃCOWY

**✅ SSI V5 DEVELOPMENT ORDER ANALYSIS COMPLETE**

**📌 Aktualny Status:**
- Dokumentacja architektury: ✅ 100% gotowa
- Analiza zależności: ✅ 100% gotowa
- Plan kolejności budowy: ✅ 100% gotowy
- Gotowość do implementacji: ⚠️ **OCZEKUJE NA DECYZJE**

**⏳ WAITING FOR:**
1. Rozwiązanie 8 konfliktów projektowych (sekcja 6)
2. Zatwierdzenie planu kolejności budowy
3. Potwierdzenie priorytetów modułów

**🎯 Następny Krok:**
Przedstawić ten dokument projektantowi do zatwierdzenia i rozstrzygnięcia zidentyfikowanych konfliktów.

**⚠️ Ostrzeżenie:**
> **Nie rozpoczynać implementacji Sprintu 12 bez rozstrzygnięcia konfliktów i zatwierdzenia planu kolejności budowy.**
> **Zła kolejność implementacji może spowodować konieczność przebudowy modułów, co opóźni projekt o tygodnie lub miesiące.**

---

**Data utworzenia:** 2026-08-03  
**Wersja:** 1.0.0  
**Status:** ✅ PLAN GŁÓWNY - OCZEKUJE NA ZATWIERDZENIE  
**Autor:** Mistral Vibe - CLI Coding Agent

---

**Powiązane Dokumenty:**
- [SSI_V5_ARCHITECTURE_CONSISTENCY_REPORT.md](./SSI_V5_ARCHITECTURE_CONSISTENCY_REPORT.md)
- [SSI_V5_CURRENT_STATE_AUDIT.md](./SSI_V5_CURRENT_STATE_AUDIT.md)
- [SSI_V5_MASTER_SYSTEM_FLOW_ARCHITECTURE.md](./SSI_V5_MASTER_SYSTEM_FLOW_ARCHITECTURE.md)
- [SSI_V5_PART2_PRZYSZLE_MODULY.md](./SSI_V5_PART2_PRZYSZLE_MODULY.md)