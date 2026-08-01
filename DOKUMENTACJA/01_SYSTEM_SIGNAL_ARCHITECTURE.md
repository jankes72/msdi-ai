# 01 - SYSTEM SIGNAL ARCHITECTURE

**Data utworzenia:** 2026-08-01  
**Wersja:** 1.0.0  
**Status:** DRAFT  
**Autor:** Mistral Vibe - CLI Coding Agent  
**Typ dokumentu:** ARCHITEKTURA WARSTWY SYGNALOW  
**Zaleznosc:** SSI_V5_MASTER_SYSTEM_FLOW_ARCHITECTURE.md  

---

## 1. PODSUMOWANIE EXECUTIVE

Ten dokument definiuje **System Signal Architecture** - warstwe sygnalow systemowych SSI V5. Kazdy modul sistema implementuje wzorzec:

**INPUT -> PROCESS -> OUTPUT -> SIGNAL -> MEMORY UPDATE**

jest to spojna warstwa komunikacji miedzy所有模组, umozliwiajaca przeplyw informacji o stanie, bledach, decyzjach i zmianach.

---

## 2. GLOWNE ZASADY

### 2.1. Definicja Sygnalu
**Sygnal** to strukturyzowana wiadomosc przesylana miedzy komponentami systemu, zawierajaca:
- Typ sygnalu
- Nadawce
- Odbiorce
- Tresc/dane
- Timestamp
- Priorytet
- Kontekst

### 2.2. Zasady Sygnalow

1. **Zasada Jednokierunkowosci:** Sygnaly plynaca w jednym kierunku (od nadawcy do odbiorcy)
2. **Zasada Pfojnostki:** Kazdy sygnal ma jednoznacznie zdefiniowanego nadawce
3. **Zasada Priorytetu:** Sygnaly o wyzszym priorytecie sa przetwarzane pierwsze
4. **Zasada Kontekstu:** Kazdy sygnal zawiera kontekst swoego powstania
5. **Zasada Trwalosci:** Wazne sygnaly sa zapisywane w dzienniku systemowym

### 2.3. Typy Sygnalow

| Kategoria | Typ Sygnalu | Opis | Priorytet |
|-----------|-------------|------|-----------|
| **DECYZYJNE** | DECISION_SIGNAL | Decyzja podjeta przez agenta | HIGH |
| | DECISION_READY | Decyzja gotowa do oceny | MEDIUM |
| | DECISION_APPROVED | Decyzja zaakceptowana | MEDIUM |
| | DECISION_REJECTED | Decyzja odrzucona | MEDIUM |
| **BLEDOWE** | ERROR_SIGNAL | Blad krytyczny | CRITICAL |
| | WARNING_SIGNAL | Ostrzezenie | HIGH |
| | INFO_SIGNAL | Informacja | LOW |
| | DEBUG_SIGNAL | Debug | LOWEST |
| **PAMIECIOWE** | MEMORY_UPDATE | Aktualizacja pamieci | MEDIUM |
| | MEMORY_SYNC | Synchronizacja pamieci | MEDIUM |
| | MEMORY_CONFLICT | Konflikt pamieci | HIGH |
| **STRATEGICZNE** | STRATEGY_REQUEST | Zadanie testu strategii | LOW |
| | STRATEGY_RESULT | Wynik testu strategii | MEDIUM |
| | STRATEGY_PROMOTION | Awans strategii | HIGH |
| | STRATEGY_RETIREMENT | wycofanie strategii | MEDIUM |
| **SYSTEMOWE** | STATE_CHANGE | Zmiana stanu systemu | HIGH |
| | CYCLE_START | Rozpoczecie cyklu | HIGH |
| | CYCLE_COMPLETE | Zakonczenie cyklu | HIGH |
| | SHUTDOWN_REQUEST | Zadanie zatrzymania | CRITICAL |
| | HEARTBEAT | Sygnal zycia | LOWEST |
| **AI LAB** | AI_LAB_REQUEST | Zadanie do AI Lab | MEDIUM |
| | AI_LAB_RESULT | Wynik z AI Lab | MEDIUM |
| | AI_LAB_ERROR | Blad w AI Lab | HIGH |
| **COLLECTOR** | DATA_READY | Dane gotowe | MEDIUM |
| | DATA_MISSING | Brakujace dane | HIGH |
| | DATA_INVALID | Niewlasciwe dane | HIGH |

---

## 3. ARCHITECTURA SYGNALOW DLA KAZDEGO MODULU

### 3.1. V1 Data System - Signal Flow

```
V1 DATA SYSTEM
├── INPUT: Zadanie pobrania danych (DATA_FETCH_REQUEST)
│   ├── Nadawca: CollectorManager
│   ├── Odbiorca: pobieranieKursow.py / pobieranieWynikow.py
│   └── Kontekst: Zrodlo, typ danych, zakres czasowy
│
├── PROCESS: Pobieranie i przetwarzanie danych
│   ├── Sygnal: DATA_PROCESSING (INFO)
│   │   └── Stan: processing_start, processing_progress, processing_complete
│   └── Sygnal: DATA_VALIDATION (DEBUG)
│       └── Wynik: valid, invalid, partially_valid
│
├── OUTPUT: Dane gotowe do uzycia
│   └── Sygnal: DATA_READY (MEDIUM)
│       ├── Nadawca: V1 Components
│       ├── Odbiorca: V2 Collector / CollectorManager
│       ├── Dane: pobrane i przetworzone dane
│       └── Timestamp: czas pobrania
│
└── SIGNAL & MEMORY UPDATE:
    ├── Sygnal: DATA_STATISTICS_UPDATE (LOW)
    │   └── Statystyki: ilosc rekordow, czas pobrania, rozmiar
    ├── Sygnal: DATA_ERROR (HIGH/CRITICAL)
    │   └── Typ: connection_error, parsing_error, validation_error
    └── Memory Update: Aktualizacja Data Layer Memory
        └── Zapis: historia pobran, statystyki, bledy
```

**Przyklad:**
```json
{
  "signal_type": "DATA_READY",
  "sender": "pobieranieKursow.py",
  "receiver": "V2Collector",
  "timestamp": "2026-08-01T12:00:00",
  "priority": "MEDIUM",
  "data": {
    "source": "bukmacher_01",
    "record_count": 1500,
    "file_path": "kursy_przygotowane.csv",
    "data_type": "courses"
  },
  "context": {
    "request_id": "req_001",
    "cycle_number": 1
  }
}
```

### 3.2. V2 Model Laboratory - Signal Flow

```
V2 MODEL LABORATORY
├── INPUT: Dane z V1 (DATA_READY)
│   ├── Odbiorca: V2 Models (siec_01, siec_02, siec_03, siec_04)
│   └── Kontekst: typ danych, zakres, format
│
├── PROCESS: Trening i obserwacja modeli
│   ├── Sygnal: MODEL_TRAINING_START (INFO)
│   │   └── Model: siec_01_zmiana_kursow / etc.
│   ├── Sygnal: MODEL_TRAINING_PROGRESS (DEBUG)
│   │   └── Progress: 0-100%
│   ├── Sygnal: MODEL_TRAINING_COMPLETE (MEDIUM)
│   │   └── Metryki: accuracy, loss, validation_score
│   └── Sygnal: MODEL_OBSERVATION (INFO)
│       └── Dane: 40% danych obserwacyjnych
│
├── OUTPUT: Modele gotowe do uzycia
│   └── Sygnal: MODEL_READY (MEDIUM)
│       ├── Nadawca: V2 Model Laboratory
│       ├── Odbiorca: V3 Collector
│       └── Dane: wytrenowana siec + metryki
│
└── SIGNAL & MEMORY UPDATE:
    ├── Sygnal: MODEL_EVALUATION (MEDIUM)
    │   └── Wyniki: performance, stability, confidence
    ├── Sygnal: MODEL_ERROR (HIGH)
    │   └── Typ: training_error, validation_error, convergence_error
    └── Memory Update: Aktualizacja Model Memory
        └── Zapis: parametry modelu, wyniki, historia treningu
```

**Przyklad:**
```json
{
  "signal_type": "MODEL_READY",
  "sender": "siec_01_zmiana_kursow",
  "receiver": "V3Collector",
  "timestamp": "2026-08-01T12:05:00",
  "priority": "MEDIUM",
  "data": {
    "model_id": "siec_01",
    "model_type": "zmiana_kursow",
    "training_accuracy": 0.92,
    "validation_accuracy": 0.88,
    "epochs": 100
  },
  "context": {
    "training_data_percentage": 60,
    "observation_data_percentage": 40
  }
}
```

### 3.3. V3 World Memory System - Signal Flow

```
V3 WORLD MEMORY SYSTEM
├── INPUT: Modele z V2 (MODEL_READY)
│   ├── Odbiorca: V3 World Builders
│   └── Kontekst: model type, performance metrics
│
├── PROCESS: Budowa mapy wiedzy
│   ├── Sygnal: WORLD_CREATION_START (INFO)
│   │   └── Swiat: zmiana_kursow / dynamiki / klasyfikacji
│   ├── Sygnal: PATTERN_DETECTION (INFO)
│   │   └── Wzorce: synchronizacja, amplituda, tempo
│   ├── Sygnal: MEMORY_TAGGING (DEBUG)
│   │   └── Kategorie: wynik, zachowanie, skutecznosc, odchylenia, ekonomia, zaleznosci, strategiczne
│   └── Sygnal: ECONOMIC_ANALYSIS (INFO)
│       └── Analiza: wartosc oczekiwana, kurs, ryzyko
│
├── OUTPUT: Mapa wiedzy gotowa
│   └── Sygnal: WORLD_MEMORY_READY (MEDIUM)
│       ├── Nadawca: V3 World Memory System
│       ├── Odbiorca: V4 Collector / Agents
│       └── Dane: swiaty, pamieci, metadane, wzorce
│
└── SIGNAL & MEMORY UPDATE:
    ├── Sygnal: INVERSE_PATTERN_DETECTED (HIGH)
    │   └── Odwrocone wzorce wykryte
    ├── Sygnal: MEMORY_CONFLICT (HIGH)
    │   └── Konflikty miedzy swiatami
    └── Memory Update: Aktualizacja World/Group/Pattern Memory
        └── Zapis: swiaty, grupy, wzorce, historia, zaleznosci
```

**Przyklad:**
```json
{
  "signal_type": "WORLD_MEMORY_READY",
  "sender": "V3_WorldMemorySystem",
  "receiver": "V4Collector",
  "timestamp": "2026-08-01T12:10:00",
  "priority": "MEDIUM",
  "data": {
    "worlds": ["zmiana_1", "zmiana_X", "zmiana_2"],
    "memories": ["World Memory", "Group Memory", "Pattern Memory"],
    "metadata_count": 1500,
    "patterns_detected": 47
  },
  "context": {
    "source_models": ["siec_01", "siec_02", "siec_03", "siec_04"],
    "data_split": "60_40"
  }
}
```

### 3.4. V4 Agent Evolution - Signal Flow

```
V4 AGENT EVOLUTION (Kazdy Agent Indywidualnie)
┌─────────────────────────────────────────────────────────────────┐
│ AGENT 01                                                                 │
├── INPUT: Dane z V3 + V2 + V4 + External (DATA_READY)              │
│   ├── Odbiorca: Agent Runtime                                    │
│   └── Kontekst: agent_id, cycle_number, data_types               │
│                                                                 │
├── PROCESS: Cykl agenta                                             │
│   ├── Sygnal: AGENT_AWAKE (INFO)                                   │
│   │   └── Stan: ready, processing, sleeping                         │
│   ├── Sygnal: MEMORY_LOAD_START (DEBUG)                          │
│   │   └── Typy: PERSONALITY, BEHAVIOR, STRATEGY, HISTORY          │
│   ├── Sygnal: MEMORY_LOADED (INFO)                               │
│   │   └── Status: success, partial, failed                          │
│   ├── Sygnal: DATA_COMPARISON (INFO)                             │
│   │   └── Porownanie: STARA WIEDZA + NOWE DANE                    │
│   ├── Sygnal: ANALYSIS_START (INFO)                               │
│   │   └── Typ: decision, prediction, strategy_evaluation            │
│   ├── Sygnal: DECISION_MAKING (INFO)                              │
│   │   └── Proces: option_evaluation, risk_assessment, selection   │
│   └── Sygnal: DECISION_COMPLETE (MEDIUM)                          │
│       └── Wynik: decision, confidence, expected_value, risk       │
│                                                                 │
├── OUTPUT: Decyzja agenta                                          │
│   └── Sygnal: DECISION_SIGNAL (HIGH)                              │
│       ├── Nadawca: Agent 01                                       │
│       ├── Odbiorca: Information Flow Controller / Decision Engine │
│       └── Dane: decision, context, confidence, strategy_used        │
│                                                                 │
└── SIGNAL & MEMORY UPDATE:                                            │
    ├── Sygnal: AGENT_LEARNING (MEDIUM)                             │
    │   └── Nowa wiedza zdobyta                                     │
    ├── Sygnal: PERSONALITY_EVOLUTION (MEDIUM)                       │
    │   └── Zmiana wektora osobowosci                                │
    └── Memory Update: Aktualizacja wszystkich typow pamieci       │
        └── Zapis: decyzje, predykcje, strategie, historia           │
└─────────────────────────────────────────────────────────────────┘
```

**Przyklad DECISION_SIGNAL:**
```json
{
  "signal_type": "DECISION_SIGNAL",
  "sender": "Agent_01",
  "receiver": "DecisionEngine",
  "timestamp": "2026-08-01T12:15:00",
  "priority": "HIGH",
  "data": {
    "decision_id": "dec_001_01",
    "decision_type": "bet_placement",
    "action": "PLACE_BET",
    "parameters": {
      "match_id": "match_001",
      "bet_type": "1X2",
      "Selection": "1",
      "amount": 100,
      "odds": 2.15
    },
    "confidence": 0.87,
    "expected_value": 115.00,
    "risk": 0.13,
    "strategy_id": "strategy_05",
    "strategy_version": "2.1"
  },
  "context": {
    "agent_id": "01",
    "agent_name": "Analityk",
    "cycle_number": 1,
    "data_sources": ["V2_siec_01", "V2_siec_02", "V3_WorldMemory"],
    "personality_vector": {
      "analysis": 0.9,
      "caution": 0.85,
      "curiosity": 0.6
    }
  }
}
```

**Kolejnosc agentow:** Agent 01 -> 02 -> 03 -> 04 -> 05 -> 06 (sekwencyjnie, zgodnie z ograniczeniem sprzetowym)

### 3.5. V5 System Orchestration - Signal Flow

```
V5 SYSTEM ORCHESTRATION (Runtime Controller)
├── INPUT: Sygnaly od wszystkich modulow
│   ├── DECISION_SIGNAL (od Agentow)
│   ├── MEMORY_UPDATE (od Agentow)
│   ├── STATE_CHANGE (od State Manager)
│   └── DATA_READY (od Collector Manager)
│
├── PROCESS: Koordynacja systemu
│   ├── Sygnal: CYCLE_START (HIGH)
│   │   └── Rozpoczecie nowego cyklu
│   ├── Sygnal: AGENT_QUEUE_UPDATE (INFO)
│   │   └── Aktualizacja kolejki agentow
│   ├── Sygnal: MODEL_START (HIGH)
│   │   └── Aktywacja modelu LLM
│   ├── Sygnal: MODEL_STOP (HIGH)
│   │   └── Deaktywacja modelu LLM
│   └── Sygnal: MODEL_NEXT (HIGH)
│       └── Przelaczenie na nastepny model/agenta
│
├── OUTPUT: Sterowanie systemem
│   ├── Sygnal: AGENT_ACTIVATE (HIGH)
│   │   ├── Nadawca: RuntimeController
│   │   ├── Odbiorca: Agent X
│   │   └── Polecenie: Start cyklu
│   ├── Sygnal: COLLECTOR_ACTIVATE (MEDIUM)
│   │   └── Polecenie: Zbieranie danych
│   └── Sygnal: SHUTDOWN_INITIATED (CRITICAL)
│       └── Polecenie: Zatrzymanie systemu
│
└── SIGNAL & MEMORY UPDATE:
    ├── Sygnal: SYSTEM_STATISTICS (LOW)
    │   └── Statystyki: wykonane cykle, czas, bledy
    └── Memory Update: Aktualizacja RuntimeState
        └── Zapis: stan systemu, liczniki, czasy
```

### 3.6. Information Flow Controller - Signal Flow

```
INFORMATION FLOW CONTROLLER
├── INPUT: Wszystkie sygnaly systemowe
│   ├── Od: V1, V2, V3, V4, V5, Moduly
│   └── Typy: DECISION, ERROR, MEMORY, STRATEGY, SYSTEM
│
├── PROCESS: Agregacja i routing sygnalow
│   ├── Sygnal: SIGNAL_RECEIVED (DEBUG)
│   │   └── Logowanie odebranego sygnalu
│   ├── Sygnal: SIGNAL_AGGREGATED (INFO)
│   │   └── Agregacja sygnalow tego samego typu
│   ├── Sygnal: SIGNAL_ROUTED (INFO)
│   │   └── Routing do wlasciwego odbiorcy
│   └── Sygnal: SIGNAL_PROCESSED (DEBUG)
│       └── Potwierdzenie przetworzenia
│
├── OUTPUT: Rozpropagowanie sygnalow
│   ├── Do: Decision Engine, Strategy Lab, Memory System, AI Lab
│   └── Wszystkie moduly zgodnie z addressed routing
│
└── SIGNAL & MEMORY UPDATE:
    ├── Sygnal: SIGNAL_QUEUE_STATUS (LOW)
    │   └── Stan kolejki sygnalow
    └── Memory Update: Aktualizacja Signal Log
        └── Zapis: historia sygnalow, statystyki, bledy routingu
```

### 3.7. Decision Engine - Signal Flow

```
DECISION ENGINE
├── INPUT: DECISION_SIGNAL od agentow
│   ├── Odbiorca: Decision Evaluator
│   └── Kontekst: agent, cycle, strategy
│
├── PROCESS: Ocena i selekcja decyzji
│   ├── Sygnal: DECISION_EVALUATION_START (INFO)
│   │   └── Decyzja wejsciowa
│   ├── Sygnal: SCORING_CALCULATION (DEBUG)
│   │   └── Wartosc = trafnosci x kurs x powtarzalnosc x stabilnosc - ryzyko
│   ├── Sygnal: DECISION_COMPARISON (INFO)
│   │   └── Porownanie z innymi decyzjami
│   └── Sygnal: FINAL_DECISION (HIGH)
│       └── Ostateczna decyzja systemowa
│
├── OUTPUT: Akceptacja/odrzucenie decyzji
│   ├── Sygnal: DECISION_APPROVED (MEDIUM)
│   │   ├── Nadawca: Decision Engine
│   │   ├── Odbiorca: Agent + Memory
│   │   └── Decyzja zaakceptowana do wykonania
│   └── Sygnal: DECISION_REJECTED (MEDIUM)
│       └── Decyzja odrzucona z przyczyna
│
└── SIGNAL & MEMORY UPDATE:
    ├── Sygnal: DECISION_STATE_UPDATE (LOW)
    │   └── Aktualizacja stanu decyzji
    └── Memory Update: Aktualizacja Decision History
        └── Zapis: zaakceptowane/odrzucone decyzje, powody
```

### 3.8. Strategy Laboratory - Signal Flow

```
STRATEGY LABORATORY
├── INPUT: STRATEGY_REQUEST od agentow
│   ├── Odbiorca: Strategy Manager
│   └── Kontekst: agent, strategy_type, test_parameters
│
├── PROCESS: Testowanie i ewolucja strategii
│   ├── Sygnal: STRATEGY_TEST_START (INFO)
│   │   └── Rozpoczecie testu nowej strategii
│   ├── Sygnal: STRATEGY_EXECUTION (DEBUG)
│   │   └── Wykonanie strategii na historycznych danych
│   ├── Sygnal: STRATEGY_EVALUATION (INFO)
│   │   └── Ocena: skutecznosc, ryzyko, stabilnosc
│   └── Sygnal: STRATEGY_RANKING_UPDATE (MEDIUM)
│       └── Aktualizacja rankingu strategii
│
├── OUTPUT: Rezultaty testow strategii
│   ├── Sygnal: STRATEGY_RESULT_READY (MEDIUM)
│   │   ├── Nadawca: Strategy Laboratory
│   │   ├── Odbiorca: Agent (zleceniodawca)
│   │   └── Wyniki testu z ocena
│   ├── Sygnal: STRATEGY_PROMOTION (HIGH)
│   │   └── Strategia awansowana do produkcji
│   └── Sygnal: STRATEGY_RETIREMENT (MEDIUM)
│       └── Strategia wycofana z uzytku
│
└── SIGNAL & MEMORY UPDATE:
    ├── Sygnal: STRATEGY_STATISTICS (LOW)
    │   └── Statystyki: liczba uzyc, sukcesy, porazki
    └── Memory Update: Aktualizacja Strategy Memory
        └── Zapis: strategie, wyniki, ranking, historia
```

**Proces Pomysl -> Test -> Ocena -> Ranking -> Akceptacja:**
1. Agent generuje nowy pomysl na strategie (experimental)
2. Strategy Lab: STRATEGY_TEST_START
3. Test na historycznych danych
4. Strategy Lab: STRATEGY_EVALUATION
5. Ocena: skutecznosc > 70% ?
6. Strategy Lab: STRATEGY_PROMOTION (Production)
7. Agent dodaje do swojego rankingu

### 3.9. Memory Evolution System - Signal Flow

```
MEMORY EVOLUTION SYSTEM
├── INPUT: MEMORY_UPDATE od agentow i modulow
│   ├── Odbiorca: Memory Processor
│   └── Kontekst: typ pamieci, agent_id, data
│
├── PROCESS: Dojrzewanie i ewolucja pamieci
│   ├── Sygnal: MEMORY_MATURE_START (INFO)
│   │   └── Rozpoczecie dojrzewania pamieci surowych
│   ├── Sygnal: MEMORY_ANALYSIS (INFO)
│   │   └── Analiza wzorców i zaleznosci
│   ├── Sygnal: MEMORY_CATEGORIZATION (DEBUG)
│   │   └── Kategoryzacja: wynik, zachowanie, skutecznosc, etc.
│   └── Sygnal: MEMORY_BRIDGING (MEDIUM)
│       └── Laczenie ze zwiazana wiedza
│
├── OUTPUT: Pamięć gotowa do uzytku
│   ├── Sygnal: MEMORY_ACTIVATED (MEDIUM)
│   │   └── Pamięć aktywowana w systemie
│   └── Sygnal: MEMORY_ARCHIVED (LOW)
│       └── Pamięć zarchiwizowana
│
└── SIGNAL & MEMORY UPDATE:
    ├── Sygnal: MEMORY_STATE_CHANGE (LOW)
    │   └── Zmiana stanu pamieci
    └── Memory Update: Aktualizacja Memory State
        └── Zapis: stany pamieci, statystyki, historia ewolucji
```

**Cykl Pamieci:**
DOSWIADCZENIE -> PAMIEC SUROWA -> DOJRZEWANIE -> OBSERWACJA -> OCENA -> RANKING -> STRATEGIA -> SLAD DOSWIADCZENIA

Stany: NOWA -> DOJRZEWAJACA -> OBSERWOWANA -> ANALIZOWANA -> AKTYWNA -> ARCHIWALNA

### 3.10. AI Lab Request Pipeline - Signal Flow

```
AI LAB Request Pipeline
├── INPUT: AI_LAB_REQUEST od modulow
│   ├── Odbiorca: AI Lab Queue Manager
│   └── Kontekst: request_type, priority, data
│
├── PROCESS: Zarzadzanie kolejka zadan
│   ├── Sygnal: QUEUE_ADD (INFO)
│   │   └── Dodanie zadania do kolejki
│   ├── Sygnal: QUEUE_PROCESSING (INFO)
│   │   └── Przetwarzanie kolejki (FIFO)
│   ├── Sygnal: MODEL_START (HIGH)
│   │   └── MODEL START (tylko gdy nie działa zaden model)
│   └── Sygnal: MODEL_STOP (HIGH)
│       └── MODEL STOP po zakonczeniu pracy
│
├── OUTPUT: Wyniki z drugiego komputera
│   ├── Sygnal: AI_LAB_RESULT_READY (MEDIUM)
│   │   ├── Nadawca: AI Lab Queue Manager
│   │   ├── Odbiorca: Requesting Module
│   │   └── Wyniki obliczen z drugiego komputera
│   └── Sygnal: AI_LAB_ERROR (HIGH)
│       └── Blad podczas przetwarzania
│
└── SIGNAL & MEMORY UPDATE:
    ├── Sygnal: QUEUE_STATUS (LOW)
    │   └── Stan kolejki: liczba zadan, czasy oczekiwania
    └── Memory Update: Aktualizacja AI Lab Memory
        └── Zapis: zadania, wyniki, czasy, bledy
```

**Przeplyw:**
MAIN SSI -> AI LAB REQUEST QUEUE -> DRUGI KOMPUTER -> WYNIK -> SSI MEMORY

**Zgodnosc z ograniczeniem sprzetowym:**
- Drugi komputer traktowany jak model w kolejce
- MODEL START -> WORK -> SAVE MEMORY -> MODEL STOP
- Tylko jeden model (glowny LLM + drugi komputer) nie dziala jednoczesnie

### 3.11. Prompt Management System - Signal Flow

```
PROMPT MANAGEMENT SYSTEM
├── INPUT: Zadania zwiazane z promptami
│   ├── Od: Developer, Agents, System, Laboratory
│   └── Typy: create, update, delete, search, version
│
├── PROCESS: Zarzadzanie repozytorium promptow
│   ├── Sygnal: PROMPT_CREATED (MEDIUM)
│   │   └── Nowy prompt dodany
│   ├── Sygnal: PROMPT_UPDATED (MEDIUM)
│   │   └── Prompt zaktualizowany
│   ├── Sygnal: PROMPT_DEPRECATED (LOW)
│   │   └── Starsza wersja promptu
│   └── Sygnal: PROMPT_SEARCH (INFO)
│       └── Wyszukiwanie promptow po kryteriach
│
├── OUTPUT: Prompty gotowe do uzycia
│   ├── Sygnal: PROMPT_READY (MEDIUM)
│   │   └── Prompt dostepny dla zleceniodawcy
│   └── Sygnal: PROMPT_HISTORY_UPDATE (LOW)
│       └── Aktualizacja historii uzytku
│
└── SIGNAL & MEMORY UPDATE:
    └── Memory Update: Aktualizacja Prompt Repository
        └── Zapis: prompty, wersje, autorzy, historia uzytku
```

**Kategorie Promptow:**
- system_prompts: Prompty systemowe
- agent_prompts: Prompty dla agentow
- developer_prompts: Prompty programisty
- laboratory_prompts: Prompty laboratoryjne

**Atrybuty Promptu:**
- prompt_id: Unikalny identyfikator
- autor: Tworca
- wersja: Numer wersji
- cel: Przeznaczenie
- wynik: Rezultat uzytku
- historia: Historia zmian i uzyc

### 3.12. Developer Input Architecture - Signal Flow

```
DEVELOPER INPUT ARCHITECTURE
├── INPUT: Polecenie od programisty
│   ├── Odbiorca: Developer Command Interface
│   └── Kontekst: komenda, parametry, priorytet
│
├── PROCESS: Walidacja i autoryzacja
│   ├── Sygnal: COMMAND_RECEIVED (INFO)
│   │   └── Odebrane polecenie
│   ├── Sygnal: COMMAND_VALIDATION (INFO)
│   │   └── Walidacja: syntaktyka, uprawnienia, dostepnosc komand
│   ├── Sygnal: COMMAND_AUTHORIZED (MEDIUM)
│   │   └── Autoryzacja: pozwolenie na wykonanie
│   └── Sygnal: COMMAND_REJECTED (MEDIUM)
│       └── Odmowa z przyczyna
│
├── OUTPUT: Polecenie do realizacji
│   ├── Sygnal: COMMAND_FORWARDED (MEDIUM)
│   │   ├── Nadawca: Developer Command Interface
│   │   ├── Odbiorca: Governance Validation
│   │   └── Komenda przekazana dalej
│   └── Sygnal: COMMAND_COMPLETE (MEDIUM)
│       └── Komenda zrealizowana
│
└── SIGNAL & MEMORY UPDATE:
    └── Memory Update: Aktualizacja Developer Log
        └── Zapis: polecenia, rezultaty, czasy, uzyte komandy
```

**Przeplyw:**
PROGRAMISTA -> Developer Command Interface -> Governance Validation -> Information Flow Controller -> Orchestrator -> Modul

**Zasada:** Programista NIE komunikuje sie bezposrednio z modulami

---

## 4. SYGNAL ROUTING I PROPAGACJA

### 4.1. Signal Routing Matrix

| Nadawca \ Odbiorca | RuntimeCtrl | AgentMgr | DecEngine | StratLab | MemEvo | AI Lab | DevInput | Collectors |
|-------------------|-------------|----------|-----------|----------|---------|--------|----------|------------|
| RuntimeCtrl | - | HIGH | HIGH | MED | MED | HIGH | MED | HIGH |
| Agent 01-06 | HIGH | - | HIGH | MED | HIGH | LOW | LOW | LOW |
| DecEngine | MED | HIGH | - | MED | LOW | LOW | LOW | LOW |
| StratLab | LOW | MED | MED | - | LOW | LOW | LOW | LOW |
| MemEvo | LOW | HIGH | LOW | MED | - | LOW | LOW | LOW |
| AI Lab | LOW | LOW | LOW | LOW | LOW | - | LOW | LOW |
| DevInput | MED | LOW | LOW | LOW | LOW | LOW | - | LOW |
| Collectors | MED | HIGH | LOW | LOW | LOW | LOW | LOW | - |

**Priorytety:**
- HIGH: Decyzje, bledy, zmiany stanu, rozkazy
- MEDIUM: Aktualizacje pamieci, wyniki testow, gotowosc
- LOW: Statystyki, logi, informacje rozne

### 4.2. Signal Propagation Rules

1. **Zasada Sekwencyjnosci:** Sygnaly przetwarzane w kolejnosci priorytetu
2. **Zasada Niezatracalnosc:** Kazdy sygnal jest przetwarzany conajmniej raz
3. **Zasada Priorytetu:** Sygnaly CRITICAL > HIGH > MEDIUM > LOW > LOWEST
4. **Zasada Czasu:** Sygnaly z wczesniejszym timestamp sa przetwarzane pierwsze (przy tym samym priorytecie)
5. **Zasada Unikalnosci:** Kazdy sygnal ma unikalny signal_id

### 4.3. Signal Format

```
STANDARDOWY FORMAT SYGNALU:
{
  "signal_id": "<UNIKALNY_ID>",
  "signal_type": "<TYP_SYGNALU>",
  "sender": "<NADAWCA>",
  "receiver": "<ODBIORCA>|<GRUPA>|<ALL>",
  "timestamp": "<ISO8601_TIMESTAMP>",
  "priority": "<CRITICAL|HIGH|MEDIUM|LOW|LOWEST>",
  "data": { ... },
  "context": { ... },
  "metadata": {
    "version": "1.0",
    "schema": "ssi_v5_signal"
  }
}
```

---

## 5. ERROR HANDLING W SYSTEMIE SYGNALOW

### 5.1. Error Signal Processing

```
ERROR_SIGNAL PRZEPLYW:
1. Wykrycie bledu przez modul
2. Utworzenie ERROR_SIGNAL (CRITICAL/HIGH)
3. Wyslanie do Information Flow Controller
4. Zalogowanie bledu
5. Powiadomienie RuntimeController
6. RuntimeController decyduje o akcji:
   ├── CRITICAL: Shutdown request
   ├── HIGH: Retry z fallback
   └── MEDIUM/LOW: Log i continue
```

### 5.2. Error Recovery Strategies

| Typ Bledu | Strategia | Sygnal Naprawczy |
|-----------|-----------|------------------|
| Connection Error | Retry (3x) + Fallback | RETRYAttempt_SIGNAL |
| Data Validation Error | Skip record + Notify | DATA_SKIP_SIGNAL |
| Model Training Error | Restart training | MODEL_RESTART_SIGNAL |
| Memory Load Error | Load from backup | MEMORY_LOAD_BACKUP_SIGNAL |
| Agent Crash | Restart agent | AGENT_RESTART_SIGNAL |
| System Overload | Reduce load + Queue | SYSTEM_THROTTLE_SIGNAL |

### 5.3. Error Escalation Path

```
Agent Error
    → Agent Manager
        → Runtime Controller
            → System Shutdown (jeśli CRITICAL)

Module Error
    → Information Flow Controller
        → Runtime Controller
            → Decision: Continue / Shutdown

Collector Error
    → Collector Manager
        → Runtime Controller
            → Use cached data / Shutdown
```

---

## 6. MONITORING I LOGOWANIE SYGNALOW

### 6.1. Signal Log Structure

```json
{
  "log_id": "log_001",
  "signal_id": "sig_001",
  "signal_type": "DECISION_SIGNAL",
  "sender": "Agent_01",
  "receiver": "DecisionEngine",
  "timestamp_send": "2026-08-01T12:15:00",
  "timestamp_receive": "2026-08-01T12:15:01",
  "timestamp_process": "2026-08-01T12:15:02",
  "priority": "HIGH",
  "status": "PROCESSED",
  "processing_time_ms": 1000,
  "data_size_bytes": 512,
  "error": null
}
```

### 6.2. Signal Statistics

| Metryka | Opis | Czelstotliwosc |
|---------|------|--------------|
| signals_per_cycle | Liczba sygnalow na cykl | Co cykl |
| signals_by_type | Rozklad sygnalow po typach | Co cykl |
| signals_by_priority | Rozklad sygnalow po priorytetach | Co cykl |
| avg_processing_time | Sredni czas przetwarzania | Ciagle |
| max_queue_length | Maksymalna dlugosc kolejki | Ciagle |
| error_rate | Odsetek blednych sygnalow | Co cykl |

---

## 7. SIGNAL TESTING I WALIDACJA

### 7.1. Test Cases for Signal System

1. **SYG-001:** Sygnal DECISION_SIGNAL od Agenta 01 do Decision Engine
   - Spodziewany: Przetworzony w <100ms
   - Wynik: DECISION_APPROVED/REJECTED

2. **SYG-002:** Sygnal ERROR_SIGNAL (CRITICAL) od dowolnego modulu
   - Spodziewany: Natychmiastowa eskalacja do RuntimeController
   - Wynik: Shutdown lub retry

3. **SYG-003:** Sygnal MEMORY_UPDATE od wszystkich agentow
   - Spodziewany: Sekwencyjne przetwarzanie
   - Wynik: Memory zaktualizowana

4. **SYG-004:** Sygnal AI_LAB_REQUEST z kolejką zadan
   - Spodziewany: MODEL START -> WORK -> MODEL STOP
   - Wynik: Wyniki w SSI MEMORY

5. **SYG-005:** Sygnal CYCLE_COMPLETE
   - Spodziewany: Zapis stanu, inkrementacja licznika
   - Wynik: Gotowy na nastepny cykl

### 7.2. Validation Rules

- [ ] Kazdy sygnal ma poprawny format
- [ ] signal_id jest unikalny
- [ ] timestamp jest w formacie ISO8601
- [ ] priority jest jedna z: CRITICAL, HIGH, MEDIUM, LOW, LOWEST
- [ ] sender i receiver sa rozpoznawalne
- [ ] data jest zgodne ze schema dla danego signal_type

---

## 8. INTEGRACJA Z MASTER SYSTEM FLOW

**Powiazanie z SSI_V5_MASTER_SYSTEM_FLOW_ARCHITECTURE.md:**

Kazdy modul zdefiniowany w Master Flow ma zdefiniowana warstwe sygnalow:

```
Master Flow Phase → Signal Architecture
├── DATA FLOW (V1→V2→V3→V4) → DATA_READY, MODEL_READY, WORLD_MEMORY_READY
├── CONTROL FLOW (Runtime→Agents) → AGENT_ACTIVATE, CYCLE_START, MODEL_START/STOP
├── MEMORY FLOW (Agents→Memory) → MEMORY_UPDATE, MEMORY_SYNC
├── SIGNAL FLOW (Dwukierunkowy) → Wszystkie typy sygnalow
└── DECISION FLOW (V4→Decision→Strategy) → DECISION_SIGNAL, STRATEGY_REQUEST, STRATEGY_RESULT
```

**Kolejnosc dokumentow:**
1. SSI_V5_MASTER_SYSTEM_FLOW_ARCHITECTURE.md ✅
2. 01_SYSTEM_SIGNAL_ARCHITECTURE.md ✅ (Ten dokument)
3. 02_DEVELOPER_INPUT_ARCHITECTURE.md ⏳

---

## 9. PODSUMOWANIE

**System Signal Architecture** jest fundamentalna warstwa komunikacji w systemie SSI V5, zapewniajaca:

1. **Spójny przepływ informacji** miedzy wszystkimi modulami
2. **Uniwersalny mechanizm sygnalizacji** dla decyzji, bledow i aktualizacji
3. **Scentralizowane zarzadzanie sygnalami** przez Information Flow Controller
4. **Zgodnosc z ograniczeniami sprzetowymi** (sekwencyjne przetwarzanie)
5. **Pelne monitorowanie i logowanie** wszystkich operacji

**Kazdy modul systemu implementuje wzorzec:**
INPUT → PROCESS → OUTPUT → SIGNAL → MEMORY UPDATE

---

**Data utworzenia:** 2026-08-01  
**Wersja:** 1.0.0  
**Status:** DRAFT - Gotowy do przegladu  
**Autor:** Mistral Vibe - CLI Coding Agent  
**Nastepny dokument:** 02_DEVELOPER_INPUT_ARCHITECTURE.md  

---

**Powiazane Dokumenty:**
- SSI_V5_MASTER_SYSTEM_FLOW_ARCHITECTURE.md
- 02_DEVELOPER_INPUT_ARCHITECTURE.md (następny)
- SSI/v5/runtime/runtime_controller.py
- SSI/v5/input_layer/collector_manager.py
