# TOOL DEPENDENCY GRAPH - SSI V5 Phase 2 Design

**Wersja:** 1.0.0  
**Data:** 2026-07-31  
**Status:** PROJEKT FAZY 2 (Przed implementacją)  
**Autor:** SSI V5 Architecture Team  

---

## 📋 SPIS TREŚCI

1. [Przegląd Grafu Zależności](#1-przegląd-grafu-zależności)
2. [Agent Tool System - Projekt](#2-agent-tool-system---projekt)
3. [Collective Control Layer - Projekt](#3-collective-control-layer---projekt)
4. [Developer Interface - Projekt](#4-developer-interface---projekt)
5. [Graf Zależności Modułów](#5-graf-zależności-modułów)
6. [Macierz Zależności](#6-macierz-zależności)
7. [Sekwencja Inicjalizacji](#7-sekwencja-inicjalizacji)

---

## 1. Przegląd Grafu Zależności

### 1.1 Cel Dokumentu

Dokument **TOOL_DEPENDENCY_GRAPH.md** definiuje kompletny graf zależności pomiędzy modułami SSI V5 Phase 2.

### 1.2 Zakres

- Agent Tool System (dynamiczny system narzędzi)
- Collective Control Layer (warstwa kontroli kolektywnej)
- Developer Interface (interfejs programisty)
- Graf zależności modułów
- Macierz zależności
- Sekwencja inicjalizacji

---

## 2. Agent Tool System - Projekt

### 2.1 Wstęp

**Agent Tool System** (ATS) umożliwia agentom dynamiczny wybór narzędzi i strategii.

**Funkcje:**
- Wybór narzędzi na podstawie personality vector
- Dobór strategii do aktualnego celu
- Wybór kolejności działań
- Pomijanie kroków procesu
- Zmiana sposobu działania

### 2.2 Architektura

```
AgentRuntime
    │
    ├── ToolSelector (wybór narzędzi)
    │   ├── personality_vector
    │   ├── current_strategy
    │   └── world_context
    │
    ├── ToolExecutor (wykonanie)
    │   └── results
    │
    └── ToolRegistry (rejestr narzędzi)
        ├── Analysis Tools
        ├── Decision Tools  
        └── Memory Tools
```

### 2.3 Składowe

**ToolSelector** (`SSI/v5/agents/tool_selector.py`):
- Wybiera narzędzia na podstawie osobowości, strategii, doświadczenia
- Ocena użyteczności narzędzi w aktualnym kontekście
- Ustala kolejność wykonania

**ToolRegistry** (`SSI/v5/agents/tool_registry.py`):
- Rejestr wszystkich dostępnych narzędzi
- Metadane: nazwa, typ, opis, parametry, wymagania

**ToolExecutor** (`SSI/v5/agents/tool_executor.py`):
- Wykonuje wybrane narzędzia
- Zarządza kontekstem i błędami
- Loguje wyniki

### 2.4 Typy Narzędzi

| **Typ** | **Narzędzia** | **Opis** |
|---------|--------------|----------|
| Analysis | data_quality_evaluator, pattern_detector, anomaly_detector, trust_scorer | Analiza danych |
| Decision | strategy_selector, confidence_calculator, decision_logger, outcome_predictor | Podejmowanie decyzji |
| Memory | memory_query, memory_update, memory_search, memory_compare, memory_validate, memory_index, memory_statistics | Operacje na pamięci |

### 2.5 Pliki

- `SSI/v5/agents/tool_selector.py`
- `SSI/v5/agents/tool_executor.py`
- `SSI/v5/agents/tool_registry.py`
- `SSI/v5/agents/tools/` (katalog implementacji)

---

## 3. Collective Control Layer - Projekt

### 3.1 Wstęp

**Collective Control Layer** (CCL) monitoruje i kontroluje ekosystem agentów.

**Funkcje:**
- Monitorowanie współpracy agentów
- Analiza konfliktów i sojuszy
- Ocena jakości strategii
- Kontrola przepływu informacji
- Kalibracja parametrów systemu

**CCL NIE zastępuje agentów** - jedynie kontroluje i kalibruje.

### 3.2 Architektura

```
RuntimeController
    │
    └── CollectiveControlLayer
        ├── CollaborationMonitor (współpraca)
        ├── ConflictAnalyzer (konflikty)
        ├── ConsensusManager (konsensus)
        ├── WorldMemoryManager (pamięć świata)
        └── CollectiveMemoryManager (pamięć kolektywna)
```

### 3.3 Składowe

**CollaborationMonitor** (`SSI/v5/ccl/collaboration_monitor.py`):
- Śledzenie interakcji pomiędzy agentami
- Ocenia jakość współpracy
- Identyfikuje wzorce współpracy
- Generuje zalecenia

**ConflictAnalyzer** (`SSI/v5/ccl/conflict_analyzer.py`):
- Wykrywa konflikty na podstawie decyzji
- Analizuje przyczyny konfliktów
- Ocenia powagę konfliktów
- Generuje strategie rozwiązywania

**ConsensusManager** (`SSI/v5/ccl/consensus_manager.py`):
- Zarządzanie procesem głosowania
- Śledzenie zgody pomiędzy agentami
- Rejestrowanie wyników konsensusu

### 3.4 Pliki

- `SSI/v5/ccl/ccl.py` (główna klasa)
- `SSI/v5/ccl/collaboration_monitor.py`
- `SSI/v5/ccl/conflict_analyzer.py`
- `SSI/v5/ccl/consensus_manager.py`
- `SSI/v5/ccl/world_memory_manager.py`
- `SSI/v5/ccl/collective_memory_manager.py`

---

## 4. Developer Interface - Projekt

### 4.1 Wstęp

**Developer Interface** (DI) jest specjalnym interfejsem dla programisty.

**Funkcje:**
- Testowanie systemu
- Wymuszanie działań agentów
- Uruchamianie modułów
- Badanie i modyfikacja pamięci
- Generowanie nowych modeli

### 4.2 Architektura

```
Programista
    │
    ▼
DeveloperConsole
    │
    ├── CommandExecutor (wykonanie poleceń)
    │   ├── System Commands
    │   ├── Agent Commands
    │   ├── Memory Commands
    │   ├── Collector Commands
    │   └── CCL Commands
    │
    └── AuditLogger (logowanie działań)
        └── developer_log.json
```

### 4.3 Typy Poleceń

| **Kategoria** | **Polecenia** | **Opis** |
|---------------|---------------|----------|
| System | start, stop, pause, resume, status, run_cycle, save_state, load_state | Kontrola systemu |
| Agent | run, force_decision, set_strategy, get_status, test, enable, disable | Kontrola agentów |
| Memory | read, write, modify, clear, export, import, stats | Operacje na pamięci |
| Collector | run, get_data, test, enable, disable | Kontrola kolektorów |
| CCL | status, collaboration_matrix, conflicts, consensus, initiate_vote, recommendations | Kontrola CCL |

### 4.4 Pliki

- `SSI/v5/developer/console.py`
- `SSI/v5/developer/command_executor.py`
- `SSI/v5/developer/audit_logger.py`
- `SSI/memory/developer/developer_log.json`

---

## 5. Graf Zależności Modułów

### 5.1 Diagram High-Level

```
FUNDAMENT (Sprint 11.5 - NIE MODYFIKOWAĆ)
┌─────────────────────────────────────────┐
│          RuntimeController                 │
│  ├── state_manager.py                     │
│  ├── scheduler.py                          │
│  ├── agent_manager.py                     │
│  └── collector_manager.py                 │
└───────────────────┬──────────────────────┘
                    │ IMPORTUJE
                    ▼
PRZYSZŁE MODUŁY (Phase 2)
┌─────────────────────────────────────────┐
│ Agent Tool System    Collective Control Layer │
│      │                      │                │
│      │                      ▼                │
│      │              ┌─────────────────┐       │
│      │              │ World Memory    │       │
│      │              │ Manager         │       │
│      │              └────────┬────────┘       │
│      │                     │                  │
│      ▼                     ▼                  │
│ Developer Interface   CollectiveMemory   │
│      │                 Manager             │
└─────────────────────────────────────────┘
```

### 5.2 Zależności Szczegółowe

| **Moduł** | **Zależy od** | **Typ** | **Opis** |
|-----------|---------------|---------|----------|
| tool_selector.py | tool_registry.py | Import | Rejestr narzędzi |
| tool_selector.py | agent_runtime.py | Import | Dostęp do osobowości |
| tool_executor.py | tool_registry.py | Import | Rejestr narzędzi |
| tool_executor.py | agent_memory_store.py | Import | Zapis wyników |
| ccl.py | runtime_controller.py | Import | Dostęp do systemu |
| ccl.py | collaboration_monitor.py | Import | Monitor współpracy |
| ccl.py | conflict_analyzer.py | Import | Analiza konfliktów |
| ccl.py | consensus_manager.py | Import | Zarządzanie konsensusem |
| ccl.py | world_memory_manager.py | Import | Pamięć świata |
| ccl.py | collective_memory_manager.py | Import | Pamięć kolektywna |
| console.py | runtime_controller.py | Import | Dostęp do systemu |
| console.py | command_executor.py | Import | Wykonanie poleceń |
| console.py | audit_logger.py | Import | Logowanie działań |
| command_executor.py | * | Import | Wszystkie moduły systemowe |

---

## 6. Macierz Zależności

### 6.1 Macierz Modułów Fundamentu vs. Phase 2

```
                  ┌──────────┬──────────┬──────────┐
                  │Runtime   │Agents    │Input     │
                  │Controller│          │Layer     │
├─────────────────┼──────────┼──────────┼──────────┤
│Tool Selector    │          │ ✓        │          │
├─────────────────┼──────────┼──────────┼──────────┤
│Tool Executor     │          │ ✓        │          │
├─────────────────┼──────────┼──────────┼──────────┤
│Tool Registry     │          │          │          │
├─────────────────┼──────────┼──────────┼──────────┤
│CCL              │ ✓        │ ✓        │ ✓        │
├─────────────────┼──────────┼──────────┼──────────┤
│Developer Console │ ✓        │ ✓        │ ✓        │
└─────────────────┴──────────┴──────────┴──────────┘

Legenda: ✓ = zależy od
```

### 6.2 Macierz Nowych Modułów

```
                  ┌──────────┬──────────┬──────────┬──────────┐
                  │Tool      │Tool      │Collective│World     │
                  │Selector  │Executor  │Control   │Memory    │
├─────────────────┼──────────┼──────────┼──────────┼──────────┤
│Tool Registry     │ ✓        │ ✓        │          │          │
├─────────────────┼──────────┼──────────┼──────────┼──────────┤
│Collaboration Mon │          │          │ ✓        │ ✓        │
├─────────────────┼──────────┼──────────┼──────────┼──────────┤
│Conflict Analyzer │          │          │ ✓        │ ✓        │
├─────────────────┼──────────┼──────────┼──────────┼──────────┤
│Consensus Manager │          │          │ ✓        │ ✓        │
├─────────────────┼──────────┼──────────┼──────────┼──────────┤
│CCL Main         │ ✓        │ ✓        │ -        │ ✓        │
└─────────────────┴──────────┴──────────┴──────────┴──────────┘
```

---

## 7. Sekwencja Inicjalizacji

### 7.1 Kolejność Inicjalizacji Systemu

1. **RuntimeConfigManager** - Ładowanie konfiguracji
2. **StateManager** - Inicjalizacja stanów
3. **Scheduler** - Konfiguracja zadań
4. **AgentManager** - Tworzenie 6 agentów z pamięciami
5. **Collectors** - Inicjalizacja v2, v3, v4, external
6. **CollectorManager** - Rejestracja kolektorów
7. **CollectiveControlLayer** - Inicjalizacja CCL (Phase 2)
8. **DeveloperConsole** - Inicjalizacja DI (Phase 2)
9. **Ustawienie stanu: READY**

### 7.2 Sekwencja Implementacji Phase 2

| **Etap** | **Moduły** | **Priorytet** | **Zależności** |
|----------|------------|--------------|----------------|
| 1 | Agent Tool System | WYSOKI | tool_registry → tool_executor → tool_selector → integracja |
| 2 | World Memory Manager | ŚREDNI | collector_manager |
| 3 | Collective Control Layer | ŚREDNI | world_memory_manager + collective_memory_manager + monitor + analyzer + consensus → ccl.py |
| 4 | Developer Interface | NISKI | runtime_controller + command_executor + audit_logger → console |
| 5 | Long Term Memory Manager | NISKI | (brak zależności) |

---

## 📌 Podsumowanie

Dokument **TOOL_DEPENDENCY_GRAPH.md** definiuje:

- ✅ Agent Tool System (dynamiczny system narzędzi)
- ✅ Collective Control Layer (warstwa kontroli kolektywnej)
- ✅ Developer Interface (interfejs programisty)
- ✅ Graf zależności modułów
- ✅ Macierz zależności
- ✅ Sekwencja inicjalizacji

**Następne kroki:**
1. Utworzenie DEVELOPER_INTERFACE.md
2. Utworzenie PHASE_2_IMPLEMENTATION_PLAN.md
3. Aktualizacja PROJECT_JOURNAL_V5.md

---

**Dokument podpisany cyfrowo:** SSI V5 Architecture Team  
**Data utrwalenia:** 2026-07-31  
**Wersja systemu:** Sprint 11.5 + Phase 2 Design
