# SSI V5 - MAPA PAMIĘCI SYSTEMU

**Data:** 2026-08-01  
**Sprint:** 11.5 → 12+ (Planowanie)  
**Status:** Dokumentacja projektowa - Wersja 1.0.0  
**Autor:** Główny Architekt SSI V5  

---

## 📋 SPIS TREŚCI

1. [Aktualna Struktura Pamięci (Sprint 11.5)](#1-aktualna-struktura-pamięci-sprint-115)
2. [Typy Pamięci i Ich Role](#2-typy-pamięci-i-ich-role)
3. [Przyszła Struktura Pamięci (Sprint 12+)](#3-przyszła-struktura-pamięci-sprint-12)
4. [Odpowiedzialność Modułów Pamięci](#4-odpowiedzialność-modułów-pamięci)
5. [Formaty Danych Pamięci](#5-formaty-danych-pamięci)

---

## 1. AKTUALNA STRUKTURA PAMIĘCI (Sprint 11.5)

### 1.1. Struktura Katalogów

```
SSI/
└── memory/
    └── agents/
        ├── agent_01/
        │   ├── personality.json    # ✅ PersonalityMemoryEntry
        │   ├── behavior.json      # ✅ BehaviorMemoryEntry
        │   ├── strategy.json      # ✅ StrategyMemoryEntry
        │   └── history.json       # ✅ HistoryMemoryEntry
        ├── agent_02/
        │   └── (analogiczne)
        ├── agent_03/
        │   └── (analogiczne)
        ├── agent_04/
        │   └── (analogiczne)
        ├── agent_05/
        │   └── (analogiczne)
        └── agent_06/
            └── (analogiczne)
```

### 1.2. Kontakt z Systemem

- **Główne wejście:** `SSI/memory/agents/agent_XX/`
- **Liczba agentów:** 6 (agent_01 do agent_06)
- **Liczba plików na agenta:** 4 (personality, behavior, strategy, history)
- **Format:** JSON (serializowane dataclass)
- **Zużycie dysku:** ~Kilka KB na agenta na cykl

---

## 2. TYPY PAMIĘCI I ICH ROLE

| **Typ (MemoryType)** | **Plik** | **Klasa (dataclass)** | **Przeznaczenie** | **Częstotliwość Aktualizacji** | **Status** |
|----------------------|----------|------------------------|-------------------|--------------------------------|------------|
| PERSONALITY | personality.json | PersonalityMemoryEntry | Cechy osobowości, wagi, zaufanie | Rzadko (zmiana konfiguracji) | ✅ Sprint 11.5 |
| BEHAVIOR | behavior.json | BehaviorMemoryEntry | Historia zachowań, akcje, skuteczność | Co cykl (nowy wpis) | ✅ Sprint 11.5 |
| STRATEGY | strategy.json | StrategyMemoryEntry | Strategie, statystyki użycia | Co cykl (aktualizacja liczników) | ✅ Sprint 11.5 |
| HISTORY | history.json | HistoryMemoryEntry | Historia zdarzeń, decyzji | Co cykl (nowy wpis) | ✅ Sprint 11.5 |
| RELATIONSHIP | relationship.json | RelationshipMemoryEntry | Relacje między agentami | Przyszłość (Sprint 13) | 🟡 Planowany |
| PROMPT | prompt.json | PromptMemoryEntry | Prompty dla LLM | Przyszłość (Sprint 15) | 🟡 Planowany |

### 2.1. Charakterystyka Typów Pamięci

#### PERSONALITY
- **Przeznaczenie:** Przechowuje cechy osobowości agenta
- **Aktualizacja:** Rzadko, głównie przy zmianie konfiguracji
- **Wpływ na zachowanie:** Wysoki - określa styl podejmowania decyzji
- **Dostęp:** Tylko dla własnego agenta

#### BEHAVIOR  
- **Przeznaczenie:** Historia zachowań i akcji agenta
- **Aktualizacja:** Co cykl - nowy wpis
- **Wpływ na zachowanie:** Średni - informacja o przeszłych’actionach
- **Dostęp:** Tylko dla własnego agenta

#### STRATEGY
- **Przeznaczenie:** Strategie używane przez agenta i ich skuteczność
- **Aktualizacja:** Co cykl - aktualizacja liczników użycia
- **Wpływ na zachowanie:** Wysoki - wybór strategii na podstawie historii
- **Dostęp:** Tylko dla własnego agenta

#### HISTORY
- **Przeznaczenie:** Pełna historia zdarzeń i decyzji
- **Aktualizacja:** Co cykl - nowy wpis
- **Wpływ na zachowanie:** Średni - kontekst historyczny
- **Dostęp:** Tylko dla własnego agenta

---

## 3. PRZYSZŁA STRUKTURA PAMIĘCI (Sprint 12+)

### 3.1. Pełna Struktura z Nowymi Warstwami

```
SSI/
├── memory/
│   │
│   ├── agents/                      # ✅ AKTUALNIE (Sprint 11.5)
│   │   └── agent_01/ ... agent_06/  # Indywidualna pamięć agentów
│   │       └── {personality,behavior,strategy,history,relationship,prompt}.json
│   │
│   ├── collective/                   # 🟡 SPRINT 12 - Collective Memory Layer
│   │   ├── global_memory.json        # Globalna wiedza systemu
│   │   ├── strategy_memory.json      # Wspólne strategie zespołowe
│   │   ├── knowledge_memory.json      # Zunifikowana baza wiedzy
│   │   └── interaction_memory.json    # Historia interakcji agentów
│   │
│   └── long_term/                    # 🟡 SPRINT 12 - Long Term Memory System
│       ├── events_history.json       # Archiwum zdarzeń systemowych
│       ├── agents_evolution.json     # Ewolucja parametrów agentów
│       ├── decisions_archive.json    # Archiwum wszystkich decyzji
│       ├── errors_log.json           # Logi błędów i nauczone lekcje
│       └── patterns_library.json     # Biblioteka wykrytych wzorców
│
└── v5/
    └── llm/                          # 🟡 SPRINT 15 - LLM Integration
        └── language_model/
            ├── agent_context/         # Kontekst indywidualny agentów
            │   ├── agent_01_context.json
            │   └── ...
            ├── collective_context/     # Kontekst zespołowy
            │   └── team_context.json
            └── prompt_memory/          # Pamięć promptów
                ├── system_prompts.json
                ├── decision_prompts.json
                └── analysis_prompts.json
```

### 3.2. Nowe Typy Pamięci (Sprint 12+)

#### Collective Memory Layer
| **Plik** | **Przeznaczenie** | **Zawartość** | **Dostęp** |
|----------|-------------------|---------------|------------|
| global_memory.json | Globalna wiedza systemu | Agregacja wiedzy z V2,V3,V4, external | Wszyscy agenci |
| strategy_memory.json | Wspólne strategie zespołu | Strategie zespołowe, plany współpracy | Wszyscy agenci |
| knowledge_memory.json | Zunifikowana baza wiedzy | Zunifikowana wiedza, indeksowana | Wszyscy agenci |
| interaction_memory.json | Historia interakcji | Komunikacja agent-agent, współpraca, konflikty | Wszyscy agenci |

#### Long Term Memory System
| **Plik** | **Przeznaczenie** | **Zawartość** | **Dostęp** |
|----------|-------------------|---------------|------------|
| events_history.json | Archiwum zdarzeń | Wszystkie zdarzenia z timestampem i kontekstem | System |
| agents_evolution.json | Ewolucja agentów | Historia zmian parametrów i zachowań | System |
| decisions_archive.json | Archiwum decyzji | Wszystkie decyzje z wynikami i ocenami | System |
| errors_log.json | Logi błędów | Błędy z kontekstem i nauczonymi lekcjami | System |
| patterns_library.json | Biblioteka wzorców | Wykryte wzorce zachowań i trendy | System |

#### LLM Memory Layer
| **Plik** | **Przeznaczenie** | **Zawartość** | **Dostęp** |
|----------|-------------------|---------------|------------|
| agent_XX_context.json | Kontekst indywidualny | Kontekst dla modelu językowego | Agent + LLM |
| team_context.json | Kontekst zespołowy | Zespołowy kontekst dla LLM | Team + LLM |
| system_prompts.json | Prompty systemowe | Szablony promptów systemowych | LLM |
| decision_prompts.json | Prompty decyzyjne | Szablony promptów decyzyjnych | LLM |
| analysis_prompts.json | Prompty analityczne | Szablony promptów analitycznych | LLM |
| response_history.json | Historia odpowiedzi | Historia odpowiedzi LLM | LLM + System |

---

## 4. ODPOWIEDZIALNOŚĆ MODUŁÓW PAMIĘCI

| **Moduł** | **Plik** | **Odpowiedzialność** | **Dane Wejściowe** | **Dane Wyjściowe** | **Zależności** |
|-----------|----------|----------------------|---------------------|---------------------|----------------|
| AgentMemoryStore | agent_memory_store.py | Serializacja/deserializacja pamięci agenta | MemoryEntry[], agent_id | JSON files | RuntimeController, AgentRuntime |
| LongTermMemoryManager | long_term_memory.py (FUTURE) | Zarządzanie pamięcią długoterminową | RuntimeState, AgentState[] | JSON files | StateManager, AgentManager |
| CollectiveMemoryManager | collective_memory.py (FUTURE) | Zarządzanie pamięcią zbiorową | AgentMemory[], Decision[] | JSON files | AgentManager, RuntimeController |
| MemoryAnalytics | memory_analytics.py (FUTURE) | Indeksowanie i wyszukiwanie | MemoryEntry[] | Optimized queries | LongTermMemoryManager |

### 4.1. Hierarchia Zarządzania Pamięcią

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HIERARCHIA PAMIĘCI SSI V5                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        MEMORY MANAGEMENT SYSTEM                      │    │
│  │                                                                     │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │    │
│  │  │  AgentMemory    │  │ CollectiveMemory │  │ LongTermMemory   │   │    │
│  │  │  Store          │  │ Manager          │  │ Manager          │   │    │
│  │  │                 │  │                 │  │                 │   │    │
│  │  │  ✅ Sprint 11.5 │  │ 🟡 Sprint 12     │  │ 🟡 Sprint 12     │   │    │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘   │    │
│  │           │                 │                 │              │    │
│  │  ┌────────▼────────┐ ┌────────▼────────┐ ┌────────▼────────┐   │    │
│  │  │ agent_01/       │ │ global_memory  │ │ events_history  │   │    │
│  │  │ agent_02/       │ │ strategy_memory │ │ agents_evolution │   │    │
│  │  │ ...            │ │ knowledge_memory│ │ decisions_archive│   │    │
│  │  │ agent_06/       │ │ interaction_mem │ │ errors_log       │   │    │
│  │  └─────────────────┘ └─────────────────┘ └─────────────────┘   │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  INTEGRACJA:                                                                │
│  AgentMemoryStore ◄──────► AgentRuntime                                   │
│  CollectiveMemoryManager ◄─► RuntimeController                              │
│  LongTermMemoryManager ◄──► StateManager                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. FORMATY DANYCH PAMIĘCI

### 5.1. PersonalityMemoryEntry

**Opis:** Cechy osobowości agenta

```json
{
  "memory_type": "PERSONALITY",
  "entry_id": "pers_01_20260801000000",
  "agent_id": "01",
  "timestamp": "2026-08-01T00:00:00",
  "personality_traits": {
    "risk_tolerance": 0.3,
    "analysis_depth": 0.9,
    "creativity": 0.4,
    "cooperation": 0.7,
    "patience": 0.6
  },
  "trust_scores": {
    "trust_v2": 0.8,
    "trust_v3": 0.8,
    "trust_v4": 0.7,
    "trust_external": 0.6
  },
  "behavior_weights": {
    "risk_weight": 0.3,
    "analysis_weight": 0.9,
    "creativity_weight": 0.4
  }
}
```

**Pola:**
- `memory_type`: Typ pamięci (enum)
- `entry_id`: Unikalny identyfikator
- `agent_id`: ID agenta
- `timestamp`: Data utworzenia/aktualizacji
- `personality_traits`: Cechy osobowości (0.0-1.0)
- `trust_scores`: Zaufanie do źródeł danych (0.0-1.0)
- `behavior_weights`: Wagi zachowań (0.0-1.0)

### 5.2. BehaviorMemoryEntry

**Opis:** Historia zachowań i akcji

```json
{
  "memory_type": "BEHAVIOR", 
  "entry_id": "beh_01_20260801000000",
  "agent_id": "01",
  "timestamp": "2026-08-01T00:00:00",
  "cycle_count": 5,
  "behavior_type": "decision_making",
  "action": "analytical",
  "data_sources": ["v2", "v3", "v4", "external"],
  "usage_count": 1,
  "success_rate": 0.87,
  "confidence": 0.85,
  "outcome": "success",
  "performance_metrics": {
    "execution_time_ms": 45,
    "quality_score": 0.82
  }
}
```

**Pola:**
- `behavior_type`: Typ zachowania (decision_making, analysis, etc.)
- `action`: Podjęta akcja
- `data_sources`: Źródła danych użyte w akcji
- `usage_count`: Ilość użyć tego zachowania
- `success_rate`: Wskaźnik sukcesu (0.0-1.0)
- `confidence`: Poziom pewności (0.0-1.0)
- `outcome`: Wynik (success, failure, neutral)

### 5.3. StrategyMemoryEntry

**Opis:** Strategie i ich statystyki użycia

```json
{
  "memory_type": "STRATEGY",
  "entry_id": "str_analytical_01_20260801000000", 
  "agent_id": "01",
  "timestamp": "2026-08-01T00:00:00",
  "strategy_name": "analytical",
  "strategy_type": "decision_strategy",
  "times_used": 5,
  "success_count": 4,
  "failure_count": 1,
  "average_confidence": 0.82,
  "last_used": "2026-08-01T00:00:00",
  "performance": {
    "average_quality": 0.85,
    "average_execution_time": 67,
    "success_rate": 0.80
  },
  "preferred_conditions": {
    "market_volatility": "low",
    "data_quality": "high"
  }
}
```

**Pola:**
- `strategy_name`: Nazwa strategii
- `strategy_type`: Typ strategii (decision, analysis, communication, etc.)
- `times_used`: Liczba użyć
- `success_count`: Liczba sukcesów
- `failure_count`: Liczba porażek
- `average_confidence`: Średni poziom pewności
- `performance`: Metryki wydajności
- `preferred_conditions`: Preferowane warunki stosowania

### 5.4. HistoryMemoryEntry

**Opis:** Historia zdarzeń i decyzji

```json
{
  "memory_type": "HISTORY",
  "entry_id": "hist_01_20260801000000",
  "agent_id": "01", 
  "timestamp": "2026-08-01T00:00:00",
  "cycle_count": 5,
  "event_type": "decision_made",
  "related_decision_id": "dec_01_20260801000000",
  "description": "Agent 01 made analytical decision with confidence 0.87",
  "choice": "high_confidence_choice",
  "confidence": 0.87,
  "strategy": "analytical",
  "sources_used": ["v2", "v3", "v4"],
  "outcome": "success",
  "outcome_details": {
    "actual_result": "positive",
    "expected_result": "positive",
    "confidence_calibration": 0.92
  },
  "lessons_learned": ["V2 data was most reliable", "Consider V3 insights more"],
  "context": {
    "world_state": {"volatility": 0.45, "trends": ["trend_1"]},
    "agent_state": {"mood": "confident", "fatigue": 0.1}
  }
}
```

**Pola:**
- `event_type`: Typ zdarzenia (decision_made, data_analysis, error, etc.)
- `related_decision_id`: Powiązana decyzja (jeśli dotyczy)
- `description`: Opis zdarzenia
- `choice`: Wybór/decyzja
- `sources_used`: Źródła danych użyte
- `outcome`: Wynik (success, failure, neutral, pending)
- `outcome_details`: Szczegóły wyniku
- `lessons_learned`: Wyciągnięte wnioski
- `context`: Kontekst zdarzenia

---

**Data utworzenia:** 2026-08-01  
**Wersja:** 1.0.0  
**Status:** Gotowy do przeglądu