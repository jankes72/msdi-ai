# SSI V5 - ARCHITEKTURA OVERVIEW

**Data:** 2026-08-01  
**Sprint:** 11.5 → 12+ (Planowanie)  
**Status:** Dokumentacja projektowa - Wersja 1.0.0  
**Autor:** Główny Architekt SSI V5  

---

## 📋 SPIS TREŚCI

1. [Aktualna Mapa Architektury SSI V5](#1-aktualna-mapa-architektury-ssi-v5)
2. [Podsumowanie i Zależności](#2-podsumowanie-i-zaleznosci)

---

## 1. AKTUALNA MAPA ARCHITEKTURY SSI V5

### 1.1. Stan Obecny (Sprint 11.5 - STABILNY FUNDAMENT)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         SSI V5 - PEŁNA ARCHITEKTURA                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                        WARSTWA URUCHOMIENIOWA                            │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                       │    │
│  │  │ start_ssi.py │  │start_ssi_   │  │  runtime_    │                       │    │
│  │  │ PRODUCTION   │  │ test.py     │  │  controller  │                       │    │
│  │  │ 5 godzin     │  │ 10 cykli    │  │    .py      │                       │    │
│  │  └─────────────┘  └─────────────┘  └──────────┬──────────┘               │    │
│  └──────────────────────────────────────────────────────┬──────────────────┘    │
│                                                               │                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                        RUNTIME CONTROLLER                                  │    │
│  │  runtime_controller.py:45                                             │    │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │    │
│  │  │  RuntimeConfigManager → runtime_config.py                        │   │    │
│  │  │  StateManager → state_manager.py                                 │   │    │
│  │  │  Scheduler → scheduler.py                                         │   │    │
│  │  │  AgentManager → agent_manager.py:???                            │   │    │
│  │  │  CollectorManager → collector_manager.py                         │   │    │
│  │  └─────────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                              │                 │                 │               │
│              ┌───────────────▼───────────┐ ┌────────▼─────────┐ ┌─────▼───────┐ │
│              │    AGENT RUNTIME LAYER     │ │  INPUT LAYER      │ │ STATE        │ │
│              │    (6 agentów)              │ │  (Kolektory)      │ │ MANAGEMENT   │ │
│              └───────────────────────────┘ └──────────────────┘ └──────────────┘ │
│                                                                                  │
│  ┌────────────────────────┐    ┌─────────────────────────┐    ┌─────────────┐  │
│  │   AGENT_01 to AGENT_06   │    │  V2, V3, V4, External   │    │ runtime      │  │
│  │   agent_runtime.py:239   │    │  input_layer/           │    │ state.json   │  │
│  │   ┌──────────────────┐   │    │  ┌──────────────┐        │    │              │  │
│  │   │ run_cycle()      │   │    │  │v2_collector  │        │    │              │  │
│  │   │  ├─ _analyze    │◄─┼────┤  │v3_collector  │        │    │              │  │
│  │   │  ├─ _make       │   │    │  │v4_collector  │        │    │              │  │
│  │   │  ├─ _save_expe  │   │    │  │external.py   │        │    │              │  │
│  │   │  └─ _update     │   │    │  └──────────────┘        │    │              │  │
│  │   └────────┬─────────┘   │    └─────────────────────────┘        │    └─────────────┘  │
│  │            │            │                                             │        │
│  └────────────┼────────────┘            │                                             │        │
│                │                       │                                             │        │
│  ┌─────────────▼─────────────┐       ┌─────▼─────────┐                                 │        │
│  │   AGENT MEMORY STORE       │       │  UNIFIED      │                                 │        │
│  │   agent_memory_store.py    │       │  INPUT        │                                 │        │
│  │   ┌─────────────────────┐  │       │  PACKAGE     │                                 │        │
│  │   │  JSON Serialization  │  │       │  collector_  │                                 │        │
│  │   │  enum -> string        │  │       │  data        │                                 │        │
│  │   └────────┬─────────────┘  │       └──────────────┘                                 │        │
│  └─────────────┼─────────────┘                                                   │        │
│                 │                                                                 │        │
│  ┌─────────────▼─────────────┐                                                   │        │
│  │     MEMORY STRUCTURE      │                                                   │        │
│  │  SSI/memory/              │                                                   │        │
│  │  └── agents/              │                                                   │        │
│  │      ├── agent_01/        │                                                   │        │
│  │      │   ├── personality.json    # PersonalityMemoryEntry           │        │
│  │      │   ├── behavior.json       # BehaviorMemoryEntry              │        │
│  │      │   ├── strategy.json       # StrategyMemoryEntry              │        │
│  │      │   └── history.json         # HistoryMemoryEntry               │        │
│  │      └── ... agent_06/    │                                                   │        │
│  └───────────────────────────┘                                                   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2. Lista Modułów z Odpowiedzialnością

| **Warstwa** | **Moduł** | **Plik** | **Lokalizacja** | **Odpowiedzialność** | **Status** |
|------------|-----------|----------|----------------|----------------------|------------|
| Uruchomienie | Main Entry | start_ssi.py | / | Główne wejście PRODUCTION | ✅ Sprint 11.5 |
| Uruchomienie | Test Entry | start_ssi_test.py | / | Wejście TEST MODE (10 cykli) | ✅ Sprint 11.5 |
| Runtime | Controller | runtime_controller.py | SSI/v5/runtime/ | Sterowanie cyklem, agentami, collectorami | ✅ Sprint 11.5 |
| Runtime | Config Manager | runtime_config.py | SSI/v5/runtime/ | Konfiguracja systemu RuntimeConfig | ✅ Sprint 11.5 |
| Runtime | State Manager | state_manager.py | SSI/v5/runtime/ | Zarządzanie stanem RuntimeState | ✅ Sprint 11.5 |
| Runtime | Scheduler | scheduler.py | SSI/v5/runtime/ | Planowanie zadań cyklicznych | ✅ Sprint 11.5 |
| Agenci | Runtime | agent_runtime.py | SSI/v5/agents/ | Cykl pojedynczego agenta | ✅ Sprint 11.5 |
| Agenci | Manager | agent_manager.py | SSI/v5/agents/ | Zarządzanie agentami (fabryka) | ✅ Sprint 11.5 |
| Agenci | Config | agents_config.py | SSI/v5/agents/ | Konfiguracja typów agentów | ✅ Sprint 11.5 |
| Agenci | Memory Store | agent_memory_store.py | SSI/v5/agents/ | Pamięć agenta (JSON) | ✅ Sprint 11.5 |
| Agenci | State | agent_state.py | SSI/v5/agents/ | Stan agenta DecisionRecord | ✅ Sprint 11.5 |
| Kolektory | V2 World | v2_collector.py | SSI/v5/input_layer/ | Zbieranie danych światowych | ✅ Sprint 11.5 |
| Kolektory | V3 Knowledge | v3_collector.py | SSI/v5/input_layer/ | Zbieranie wiedzy | ✅ Sprint 11.5 |
| Kolektory | V4 Agents | v4_collector.py | SSI/v5/input_layer/ | Zbieranie danych o agentach | ✅ Sprint 11.5 |
| Kolektory | External | external.py | SSI/v5/input_layer/external/ | Zewnętrzne dane | ✅ Sprint 11.5 |
| Kolektory | Manager | collector_manager.py | SSI/v5/input_layer/ | Manager collectorów | ✅ Sprint 11.5 |

---

## 2. PODSUMOWANIE I ZALEŻNOŚCI

### 2.1. Aktualny Stan Systemu (Sprint 11.5)

| **Komponent** | **Status** | **Pliki** | **Zależności** |
|---------------|------------|-----------|----------------|
| Runtime Controller | ✅ STABILNY | runtime_controller.py | runtime_config.py, state_manager.py |
| Agent Runtime | ✅ STABILNY | agent_runtime.py | agent_memory_store.py, agent_state.py |
| Memory System | ✅ STABILNY | agent_memory_store.py | JSON serialization |
| Input Layer | ✅ STABILNY | v2,v3,v4,external collectors | collector_manager.py |
| Test System | ✅ STABILNY | start_ssi_test.py | runtime_controller.py |

### 2.2. Planowane Rozszerzenia

| **Sprint** | **Moduł** | **Cele** | **Zależności** | **Status** |
|------------|-----------|----------|----------------|------------|
| 12 | Long Term Memory | Pamięć długoterminowa | Sprint 11.5 | 🟡 Planowany |
| 12 | Collective Memory | Pamięć zbiorowa | Sprint 11.5 | 🟡 Planowany |
| 13 | Agent Laboratory | Środowisko testowe | Sprint 12 | 🟡 Planowany |
| 13 | Communication Analyzer | Analiza interakcji | Sprint 11.5 | 🟡 Planowany |
| 14 | Behavioral Engine | Kalibracja zachowań | Sprint 12 | 🟡 Planowany |
| 15 | LLM Integration | Warstwa LLM | Sprint 13 | 🟡 Planowany |
| 16 | Collective Intelligence | Inteligencja zbiorowa | Sprint 12,13 | 🟡 Planowany |

### 2.3. Zasady Rozwoju

1. **🛡️  Niemodyfikowalność Sprintu 11.5**: Runtime Controller, Agent Runtime, Memory System działają poprawnie - **NIE wprowadzać zmian, które mogą złamać obecny system**
2. **✅ Kompatybilność wsteczna**: Nowe moduły muszą być kompatybilne z istniejącym systemem
3. **🧪 Testowanie**: Każdy nowy moduł musi mieć testy jednostkowe i integracyjne
4. **📚 Dokumentacja**: Każda zmiana = aktualizacja dokumentacji
5. **📊 Wersjonowanie**: Używać SemVer dla modułów (MAJOR.MINOR.PATCH)

---

**Data utworzenia:** 2026-08-01  
**Wersja:** 1.0.0  
**Status:** Gotowy do przeglądu