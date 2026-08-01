# SSI V5 — SYSTEM SIGNAL ARCHITECTURE

**Data utworzenia:** 2026-08-01  
**Wersja:** 1.0.0  
**Status:** FINAL DRAFT  
**Autor:** Mistral Vibe (Signal System Architect)  
**Typ dokumentu:** Core Communication Architecture  

---

## 1. CEL DOKUMENTU

Ten dokument opisuje **SYSTEM SIGNAL ARCHITECTURE** - nową warstwę systemu SSI V5 odpowiedzialną za:
- Generowanie sygnałów systemowych
- Routing sygnałów wewnętrznych i zewnętrznych
- Obsługę braku możliwości (fallback mechanism)
- Komunikację z AI Laboratory
- Monitorowanie stanu systemu przez sygnały

**Zasada główna:** Każdy sygnał posiada źródło, cel, kontekst i identyfikację.

---

## 2. ARCHITECTURE OVERVIEW

### 2.1. Miejsce w Systemie

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SSI V5 SYSTEM SIGNAL ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         SIGNAL SYSTEM LAYER                             │   │
│  │  ┌─────────────────────────────┐  ┌─────────────────────────────┐   │   │
│  │  │          SIGNAL GENERATOR     │  │         SIGNAL ROUTER       │   │   │
│  │  │  (Tworzenie sygnałów)        │  │  (Routing sygnałów)          │   │   │
│  │  └────────────────┬────────────────┘  └────────────────┬────────────┘   │   │
│  │                   │                                  │                  │   │
│  │  ┌────────────────▼────────────────┐        ┌─────────▼──────────┐   │   │
│  │  │            SIGNAL QUEUE           │        │   SIGNAL HISTORY    │   │   │
│  │  │  (Kolejka sygnałów do przetworzenia)│     │   (Historia sygnałów)│   │   │
│  │  └─────────────────────────────────┘        └─────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                           │                                                         │
│                           ▼                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      CONNECTION TO OTHER LAYERS                           │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │   │
│  │  │  ALL MODULES    │  │  DEVELOPER      │  │  AI LABORATORY   │   │   │
│  │  │  (Source)      │  │  INPUT          │  │  (External)       │   │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2. Zasady Systemu

1. **Każdy moduł może generować sygnały**
2. **Sygnały są standardowo formatowane** (patrz: Sekcja 5)
3. **Sygnały mają priorytety** (CRITICAL, HIGH, MEDIUM, LOW)
4. **Sygnały są pingowane** (każdy sygnał ma unikalne ID)
5. **Sygnały są monitorowane** (historia i statystyki)

---

## 3. SIGNAL GENERATOR

### 3.1. Odpowiedzialność

| Odpowiedzialność | Opis | Priorytet |
|------------------|------|-----------|
| Sygnał tworzenia | Generowanie sygnałów przez moduły | CRITICAL |
| Format walidacja | Sprawdzanie poprawności formatu sygnału | CRITICAL |
| Kontekst uzupełnianie | Dodawanie kontekstu systemowego | HIGH |
| Priorytet ustalanie | Określanie priorytetu sygnału | HIGH |
| ID generowanie | Tworzenie unikalnego ID sygnału | HIGH |

### 3.2. Typy Sygnałów

#### 3.2.1. SYSTEM SIGNALS (Sygnały Systemowe)

```
┌─────────────────────────────────────────────────────────────┐
│                      SYSTEM SIGNALS                              │
├─────────────────────────────────────────────────────────────┤
│  V5_START-SIGNAL                                              │
│    │                                                         │
│    ├── Wygenerowany przez: TIME CONTROL MODULE               │
│    ├── Wyzwalacz: Dane z V1 gotowe + czas OK                  │
│    ├── Cel: SYSTEM ORCHESTRATION (uruchom V5)                │
│    ├── Priorytet: CRITICAL                                    │
│    └── Akcja: Uruchomienie start_ssi.py                      │
│                                                             │
│  V5_STOP-SIGNAL                                               │
│    │                                                         │
│    ├── Wygenerowany przez: TIME CONTROL MODULE               │
│    ├── Wyzwalacz: 5 godzin działania V5 upłynęło            │
│    ├── Cel: SYSTEM ORCHESTRATION (zakończ V5)                │
│    ├── Priorytet: CRITICAL                                    │
│    └── Akcja: Auto shutdown + zapis stanu                     │
│                                                             │
│  DATA_READY-SIGNAL                                           │
│    │                                                         │
│    ├── Wygenerowany przez: V1 DATA SYSTEM                      │
│    ├── Wyzwalacz: Zakończenie procesów V1                     │
│    ├── Cel: TIME CONTROL MODULE                              │
│    ├── Priorytet: HIGH                                       │
│    └── Akcja: Sprawdzenie warunków uruchomienia V5           │
│                                                             │
│  STATE_UPDATE-SIGNAL                                         │
│    │                                                         │
│    ├── Wygenerowany przez: SYSTEM STATE AWARENESS           │
│    ├── Wyzwalacz: Zmiana stanu systemu                        │
│    ├── Cel: Wszystkie moduły (broadcast)                      │
│    ├── Priorytet: HIGH                                       │
│    └── Akcja: Aktualizacja stanu w modułach                  │
└─────────────────────────────────────────────────────────────┘
```

#### 3.2.2. PROCESS SIGNALS (Sygnały Przetwarzania)

```
┌─────────────────────────────────────────────────────────────┐
│                     PROCESS SIGNALS                             │
├─────────────────────────────────────────────────────────────┤
│  PROCESS_STARTED-SIGNAL                                        │
│    │                                                         │
│    ├── Wygenerowany przez: dowolny moduł                      │
│    ├── Wyzwalacz: Rozwój procesu                              │
│    ├── Cel: SYSTEM ORCHESTRATION                               │
│    ├── Priorytet: MEDIUM                                      │
│    └── Akcja: Monitorowanie postępu                           │
│                                                             │
│  PROCESS_COMPLETED-SIGNAL                                     │
│    │                                                         │
│    ├── Wygenerowany przez: dowolny moduł                      │
│    ├── Wyzwalacz: Zakończenie procesu                          │
│    ├── Cel: FEEDBACK LOOP + MEMORY SYSTEM                     │
│    ├── Priorytet: HIGH                                       │
│    └── Akcja: Zapis wyniku i aktualizacja pamięci             │
│                                                             │
│  PROCESS_FAILED-SIGNAL                                        │
│    │                                                         │
│    ├── Wygenerowany przez: dowolny moduł                      │
│    ├── Wyzwalacz: Błąd w trakcie przetwarzania                  │
│    ├── Cel: ERROR HANDLING + SIGNAL ROUTER                    │
│    ├── Priorytet: CRITICAL                                    │
│    └── Akcja: Routing do AI Lab lubDeveloper Input            │
│                                                             │
│  PROCESS_QUEUED-SIGNAL                                        │
│    │                                                         │
│    ├── Wygenerowany przez: SYSTEM ORCHESTRATION              │
│    ├── Wyzwalacz: Kolejkowanie nowego procesu                │
│    ├── Cel: Moduł docelowy                                   │
│    ├── Priorytet: LOW-MEDIUM                                 │
│    └── Akcja: Oczekiwanie na przetworzenie                     │
└─────────────────────────────────────────────────────────────┘
```

#### 3.2.3. ERROR SIGNALS (Sygnały Błędów)

```
┌─────────────────────────────────────────────────────────────┐
│                       ERROR SIGNALS                             │
├─────────────────────────────────────────────────────────────┤
│  ERROR_DETECTED-SIGNAL                                         │
│    │                                                         │
│    ├── Wygenerowany przez: dowolny moduł (via Error Handler) │
│    ├── Wyzwalacz: Wykrycie błędu                               │
│    ├── Cel: ERROR HANDLING + SIGNAL ROUTER                    │
│    ├── Priorytet: CRITICAL                                    │
│    └── Akcja: Próba korekcji lokalnej, jeśli nie → eskalacja  │
│                                                             │
│  ERROR_RECOVERED-SIGNAL                                       │
│    │                                                         │
│    ├── Wygenerowany przez: ERROR HANDLING                       │
│    ├── Wyzwalacz: Udana korekta błędu                         │
│    ├── Cel: SYSTEMState Awareness + Memory System             │
│    ├── Priorytet: HIGH                                       │
│    └── Akcja: Zapisstd Wiadomości o odzysku i kontynuacja     │
│                                                             │
│  ERROR_ESCALATED-SIGNAL                                       │
│    │                                                         │
│    ├── Wygenerowany przez: ERROR HANDLING                       │
│    ├── Wyzwalacz: Niemożność lokalnej korekcji               │
│    ├── Cel: SIGNAL ROUTER → AI LAB QUEUE                     │
│    ├── Priorytet: CRITICAL                                    │
│    └── Akcja: Przekazanie do drugiego komputera               │
│                                                             │
│  CONTEXT_LOST-SIGNAL                                          │
│    │                                                         │
│    ├── Wygenerowany przez: CONTEXT INTEGRITY LAYER            │
│    ├── Wyzwalacz: Utrata kontekstu w wiadomości                 │
│    ├── Cel: DYNAMIC CONTEXT CORRECTION                        │
│    ├── Priorytet: HIGH                                       │
│    └── Akcja: Próba odzysku kontekstu                        │
└─────────────────────────────────────────────────────────────┘
```

#### 3.2.4. MEMORY SIGNALS (Sygnały Pamięci)

```
┌─────────────────────────────────────────────────────────────┐
│                      MEMORY SIGNALS                             │
├─────────────────────────────────────────────────────────────┤
│  MEMORY_UPDATED-SIGNAL                                        │
│    │                                                         │
│    ├── Wygenerowany przez: dowolny moduł pamięci              │
│    ├── Wyzwalacz: Zapis nowych danych do pamięci             │
│    ├── Cel: MEMORY SYSTEM (agregacja)                         │
│    ├── Priorytet: MEDIUM                                      │
│    └── Akcja: Aktualizacja indeksów pamięci                   │
│                                                             │
│  MEMORY_CORRUPTED-SIGNAL                                      │
│    │                                                         │
│    ├── Wygenerowany przez: MEMORY SYSTEM                       │
│    ├── Wyzwalacz: Wykrycie uszkodzenia danych                  │
│    ├── Cel: ERROR HANDLING + SIGNAL ROUTER                    │
│    ├── Priorytet: CRITICAL                                    │
│    └── Akcja: Próba odzysku z backupu                        │
│                                                             │
│  MEMORY_BACKUP-SIGNAL                                         │
│    │                                                         │
│    ├── Wygenerowany przez: MEMORY SYSTEM                       │
│    ├── Wyzwalacz: Ręczne uruchomienie lub harmonogram         │
│    ├── Cel: MEMORY SYSTEM (archiwizacja)                     │
│    ├── Priorytet: LOW                                        │
│    └── Akcja: Zapis backupu pamięci                            │
└─────────────────────────────────────────────────────────────┘
```

#### 3.2.5. REQUEST SIGNALS (Sygnały Żądań)

```
┌─────────────────────────────────────────────────────────────┐
│                      REQUEST SIGNALS                            │
├─────────────────────────────────────────────────────────────┤
│  MISSING_RESOURCE-SIGNAL                                      │
│    │                                                         │
│    ├── Wygenerowany przez: dowolny moduł                      │
│    ├── Wyzwalacz: Brak wymaganych zasobów                      │
│    ├── Cel: SIGNAL ROUTER                                     │
│    ├── Priorytet: HIGH                                       │
│    └── Akcja: Routing do AI Lab lub kolejkowanie              │
│                                                             │
│  STRATEGY_IMPROVEMENT-SIGNAL                                   │
│    │                                                         │
│    ├── Wygenerowany przez: AGENT SYSTEM                       │
│    ├── Wyzwalacz: Konieczność ulepszenia strategii           │
│    ├── Cel: STRATEGY LABORATORY                               │
│    ├── Priorytet: MEDIUM                                      │
│    └── Akcja: Test i ocena nowej strategii                    │
│                                                             │
│  MODULE_GENERATION-SIGNAL                                     │
│    │                                                         │
│    ├── Wygenerowany przez: DEVELOPER INPUT                    │
│    ├── Wyzwalacz: Żądanie nowego modułu                        │
│    ├── Cel: AI LAB QUEUE                                      │
│    ├── Priorytet: HIGH                                       │
│    └── Akcja: Generowanie nowego modułu w laboratorium        │
│                                                             │
│  AI_LAB_REQUEST-SIGNAL                                        │
│    │                                                         │
│    ├── Wygenerowany przez: dowolny moduł                      │
│    └── Cel: AI LAB QUEUE (dla zadań laboratoryjnych)        │
│    ├── Priorytet: Zależy od kontekstu                         │
│    └── Akcja: Kolejkowanie w AI Laboratory                    │
└─────────────────────────────────────────────────────────────┘
```

### 3.3. AGENT-SPECIFIC SIGNALS

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT-SPECIFIC SIGNALS                        │
├─────────────────────────────────────────────────────────────┤
│  STRATEGY_SELECTED-SIGNAL                                     │
│    │                                                         │
│    ├── Wygenerowany przez: AGENT SYSTEM                      │
│    ├── Wyzwalacz: Wybór strategii dla decyzji                 │
│    ├── Cel: DECISION LAYER + MEMORY SYSTEM                    │
│    ├── Priorytet: HIGH                                       │
│    └── Akcja: Zapis wyboru i przygotowanie do decyzji          │
│                                                             │
│  STRATEGY_TEST_REQUEST-SIGNAL                                │
│    │                                                         │
│    ├── Wygenerowany przez: AGENT SYSTEM                      │
│    ├── Wyzwalacz: Nowa strategia do przetestowania           │
│    ├── Cel: STRATEGY LABORATORY                               │
│    ├── Priorytet: MEDIUM                                      │
│    └── Akcja: Dodanie do kolejki testowej                     │
│                                                             │
│  AGENT_COLLABORATION_REQUEST-SIGNAL                          │
│    │                                                         │
│    ├── Wygenerowany przez: AGENT SYSTEM                      │
│    ├── Wyzwalacz: Potrzeba współpracy między agentami        │
│    ├── Cel: Inni agenci                                       │
│    ├── Priorytet: MEDIUM                                      │
│    └── Akcja: Dostarczenie informacji o potrzebie             │
│                                                             │
│  BEHAVIOR_UPDATE-SIGNAL                                      │
│    │                                                         │
│    ├── Wygenerowany przez: AGENT SYSTEM                      │
│    ├── Wyzwalacz: Zmiana zachowania agenta                     │
│    ├── Cel: MEMORY SYSTEM (Agent Memory)                      │
│    ├── Priorytet: MEDIUM                                      │
│    └── Akcja: Zapis nowego stanu zachowania                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. SIGNAL ROUTER

### 4.1. Odpowiedzialność

| Odpowiedzialność | Opis | Priorytet |
|------------------|------|-----------|
| Routing wewnętrzny | Kierowanie sygnałów między modułami | CRITICAL |
| Routing zewnętrzny | Kierowanie sygnałów do AI Laboratory | CRITICAL |
| Priorytetyzacja | Ustalanie kolejności przetwarzania sygnałów | HIGH |
| Duplikacja | Zapobieganie duplikatom sygnałów | HIGH |
| Monitoring | Śledzenie stanu sygnałów | MEDIUM |

### 4.2. Routing Matrix

```
┌─────────────────────────┬─────────────────────┬─────────────────────┐
│         ŹRÓDŁO           │     TYP SYGNAŁU     │       CEL           │
├─────────────────────────┼─────────────────────┼─────────────────────┤
│ TIME CONTROL MODULE    │ V5_START-SIGNAL      │ SYSTEM ORCHESTRATION│
│ TIME CONTROL MODULE    │ V5_STOP-SIGNAL       │ SYSTEM ORCHESTRATION│
│ V1 DATA SYSTEM          │ DATA_READY-SIGNAL    │ TIME CONTROL MODULE │
│ AGENT SYSTEM            │ MISSING_RESOURCE     │ AI LAB QUEUE         │
│ AGENT SYSTEM            │ STRATEGY_IMPROVEMENT │ STRATEGY LABORATORY  │
│ ERROR HANDLING          │ ERROR_ESCALATED      │ AI LAB QUEUE         │
│ DEVELOPER INPUT         │ MODULE_GENERATION    │ AI LAB QUEUE         │
│ MEMORY SYSTEM           │ MEMORY_CORRUPTED    │ ERROR HANDLING       │
│Ale moduł               │ ERROR_DETECTED       │ ERROR HANDLING       │
└─────────────────────────┴─────────────────────┴─────────────────────┘
```

### 4.3. External Routing (AI Laboratory)

**Sygnały kierowane do AI Laboratory:**
- MISSING_RESOURCE-SIGNAL
- ERROR_ESCALATED-SIGNAL
- MODULE_GENERATION-SIGNAL
- AI_LAB_REQUEST-SIGNAL
- STRATEGY_IMPROVEMENT-SIGNAL (double)

**Mechanizm:**
```
MODUŁ ŹRÓDŁOWY
     │
     ▼
┌──────────────────┐
│ SIGNAL GENERATOR │ (Tworzenie sygnału)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ SIGNAL ROUTER    │ (Routing zewnętrzny)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ AI LAB QUEUE     │ (Kolejka zadań)
└──────────────────┘
```

---

## 5. SIGNAL FORMAT SPECIFICATION

### 5.1. Podstawowa Struktur

**Wszystkie sygnały MUSZĄ posiadać następującą strukturę:**

```json
{
  "signal_metadata": {
    "signal_id": "UNIQUE_UUID_v4",
    "signal_type": "SIGNAL_TYPE_ENUM",
    "signal_version": "1.0",
    "timestamp": "2026-08-01T15:00:00Z",
    "priority": "CRITICAL|HIGH|MEDIUM|LOW"
  },
  
  "source": {
    "module": "SOURCE_MODULE_NAME",
    "instance": "INSTANCE_ID",
    "version": "MODULE_VERSION"
  },
  
  "context": {
    "system_state": "CURRENT_SYSTEM_STATE",
    "process_id": "UNIQUE_PROCESS_ID",
    "session_id": "V5_SESSION_UUID",
    "cycle_number": "CYCLE_COUNT",
    "correlation_id": "CORRELATION_UUID"
  },
  
  "payload": {
    // Specyficzna dla typu sygnału
  },
  
  "routing": {
    "target_module": "TARGET_MODULE_NAME",
    "target_instance": "TARGET_INSTANCE_ID",
    "route_type": "INTERNAL|EXTERNAL|BROADCAST",
    "timeout": "TIMEOUT_IN_SECONDS"
  },
  
  "status": {
    "current": "CREATED|QUEUED|IN_TRANSIT|DELIVERED|PROCESSED|FAILED",
    "history": [
      {
        "timestamp": "ISO_8601",
        "status": "STATUS",
        "module": "MODULE"
      }
    ]
  },
  
  "security": {
    "checksum": "sha256:HASH_OF_PAYLOAD",
    "signature": "DIGITAL_SIGNATURE_IF_APPLICABLE"
  }
}
```

### 5.2. Type-Specific Payloads

#### 5.2.1. ERROR_DETECTED-SIGNAL

```json
{
  "signal_metadata": {
    "signal_type": "ERROR_DETECTED",
    "priority": "CRITICAL"
  },
  "payload": {
    "error_type": "MODULE_ERROR|DATA_ERROR|CONTEXT_ERROR|SYSTEM_ERROR",
    "error_code": "ERROR_CODE",
    "error_message": "Detailed error description",
    "error_data": {
      "failed_operation": "OPERATION_NAME",
      "input_data": "INPUT_DATA_SNAPSHOT",
      "stack_trace": "TRACEBACK_IF_AVAILABLE"
    },
    "severity": "FATAL|CRITICAL|WARNING|INFO",
    "recoverable": true
  }
}
```

#### 5.2.2. MISSING_RESOURCE-SIGNAL

```json
{
  "signal_metadata": {
    "signal_type": "MISSING_RESOURCE",
    "priority": "HIGH"
  },
  "payload": {
    "resource_type": "DATA|MODULE|STRATEGY|MEMORY|COMPUTE",
    "resource_id": "RESOURCE_IDENTIFIER",
    "required_for": "OPERATION_NAME",
    "alternatives": ["ALT_1", "ALT_2"],
    "can_wait": true,
    "max_wait_time": "PT30M"
  }
}
```

#### 5.2.3. STRATEGY_IMPROVEMENT-SIGNAL

```json
{
  "signal_metadata": {
    "signal_type": "STRATEGY_IMPROVEMENT",
    "priority": "MEDIUM"
  },
  "payload": {
    "agent_id": "AGENT_ID",
    "current_strategy": "STRATEGY_NAME",
    "improvement_idea": "DESCRIPTION_OF_IMPROVEMENT",
    "expected_impact": "IMPACT_ASSESSMENT",
    "test_required": true,
    "test_parameters": {
      "dataset": "TEST_DATASET",
      "metrics": ["METRIC_1", "METRIC_2"]
    }
  }
}
```

#### 5.2.4. V5_START-SIGNAL

```json
{
  "signal_metadata": {
    "signal_type": "V5_START",
    "priority": "CRITICAL"
  },
  "payload": {
    "v1_status": {
      "pobieranieWynikow": "completed",
      "dodawanieWynikow": "completed",
      "generatorDataBase": "completed"
    },
    "data_version": "2026-08-01",
    "available_data": ["results", "courses", "trends"],
    "recommended_mode": "PRODUCTION|TEST"
  }
}
```

---

## 6. SIGNAL QUEUE

### 6.1. Funkcjonalność

- **FIFO z priorytetem** - Sygnały CRITICAL są przetwarzane pierwsze
- **Timeout monitoring** - Sygnały z timeoutem są usuwane
- **Retry mechanism** - Nieudane sygnały są ponawiane (max 3 razy)
- **Duplicate detection** - Unikalne ID zapobiega duplikatom

### 6.2. Queue Structure

```
SIGNAL QUEUE (Priorytetowa):
┌─────────────────────────────────┐
│ CRITICAL Priority Queue        │
│ ├── ERROR_ESCALATED-SIGNAL    │
│ ├── V5_STOP-SIGNAL            │
│ └── ERROR_DETECTED-SIGNAL      │
└─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────┐
│ HIGH Priority Queue            │
│ ├── DATA_READY-SIGNAL          │
│ ├── MISSING_RESOURCE-SIGNAL    │
│ └── MODULE_GENERATION-SIGNAL   │
└─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────┐
│ MEDIUM Priority Queue          │
│ ├── PROCESS_COMPLETED-SIGNAL   │
│ ├── STRATEGY_IMPROVEMENT-SIGNAL │
│ └── PROCESS_STARTED-SIGNAL      │
└─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────┐
│ LOW Priority Queue              │
│ ├── PROCESS_QUEUED-SIGNAL       │
│ ├── MEMORY_BACKUP-SIGNAL        │
│ └── STATE_UPDATE-SIGNAL         │
└─────────────────────────────────┘
```

---

## 7. SIGNAL HISTORY

### 7.1. Przechowywane Informacje

| Pole | Typ | Opis |
|------|-----|------|
| signal_id | UUID | Unikalny identyfikator sygnału |
| signal_type | String | Typ sygnału |
| timestamp | ISO8601 | Czas utworzenia |
| source_module | String | Moduł źródłowy |
| target_module | String | Moduł docelowy |
| status | String | Ostateczny status (DELIVERED/FAILED) |
| processing_time | Float | Czas przetwarzania (ms) |
| payload_size | Integer | Rozmiar payloadu (bytes) |
| error_message | String | Błąd, jeśli wystąpił |

### 7.2. Retention Policy

- **CRITICAL sygnały:** Przechowywane 30 dni
- **HIGH sygnały:** Przechowywane 14 dni
- **MEDIUM sygnały:** Przechowywane 7 dni
- **LOW sygnały:** Przechowywane 1 dzień

---

## 8. INTEGRACJA Z ISTNIEJĄCYMI MODUŁAMI

### 8.1. Integracja z Information Flow Controller

Sygnały są walidowane przez **Message Formats and Validation Module** przed wysłaniem.

### 8.2. Integracja z System State Awareness

Sygnały zawierają aktualny stan systemu w polu `context.system_state`.

### 8.3. Integracja z Error Handling

Sygnały błędów są generowane przez **Error Handling Modules** i kierowane do **SIGNAL ROUTER**.

---

## 9. PRZYKŁADOWE SCENARIUSZE

### 9.1. Scenariusz: Brak Danych

```
AGENT SYSTEM
     │
     ▼ (Wykrywa brak danych)
┌──────────────────┐
│ SIGNAL GENERATED  │: MISSING_RESOURCE-SIGNAL
│ Type: DATA        │
│ Priority: HIGH    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ SIGNAL ROUTER    │ (Weryfikuje typ i cel)
└────────┬─────────┘
         │
         ▼ (Routing zewnętrzny → AI Laboratory)
┌──────────────────┐
│ AI LAB QUEUE     │ (Kolejka zadań laboratoryjnych)
└──────────────────┘
```

**Sygnał:**
```json
{
  "signal_metadata": {
    "signal_id": "550e8400-e29b-41d4-a716-446655440000",
    "signal_type": "MISSING_RESOURCE",
    "priority": "HIGH",
    "timestamp": "2026-08-01T15:30:00Z"
  },
  "source": {
    "module": "AGENT SYSTEM",
    "instance": "Agent_01",
    "version": "1.0.0"
  },
  "context": {
    "system_state": "V5_RUNNING",
    "process_id": "AGENT_DECISION_20260801_1530",
    "session_id": "V5_SESSION_20260801_0215",
    "cycle_number": "3"
  },
  "payload": {
    "resource_type": "DATA",
    "resource_id": "COURSE_DATA_20260801",
    "required_for": "DECISION_PREDICTION",
    "can_wait": true
  }
}
```

### 9.2. Scenariusz: Poprawa Strategii

```
AGENT SYSTEM (Agent_01)
     │
     ▼ (Analizuje wyniki i widzi potrzebę ulepszenia)
┌──────────────────┐
│ SIGNAL GENERATED  │: STRATEGY_IMPROVEMENT-SIGNAL
│ Type: STRATEGY    │
│ Priority: MEDIUM  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ SIGNAL ROUTER    │ (Routing wewnętrzny)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ STRATEGY         │ (Odbiór sygnału)
│ LABORATORY       │
└──────────────────┘
```

**Sygnał:**
```json
{
  "signal_metadata": {
    "signal_id": "550e8400-e29b-41d4-a716-446655440001",
    "signal_type": "STRATEGY_IMPROVEMENT",
    "priority": "MEDIUM",
    "timestamp": "2026-08-01T16:00:00Z"
  },
  "source": {
    "module": "AGENT SYSTEM",
    "instance": "Agent_01",
    "version": "1.0.0"
  },
  "payload": {
    "agent_id": "Agent_01",
    "current_strategy": "balanced",
    "improvement_idea": "Dodanie analizy trendów długoterminowych",
    "expected_impact": "Zwiększenie skuteczności o 15%",
    "test_required": true
  }
}
```

### 9.3. Scenariusz: Błąd Krytyczny

```
TEACHER ENGINE (siec_01)
     │
     ▼ (Wykrywa błąd w modelu)
┌──────────────────┐
│ SIGNAL GENERATED  │: ERROR_DETECTED-SIGNAL
│ Type: ERROR       │
│ Priority: CRITICAL│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ SIGNAL ROUTER    │ (Routing do Error Handling)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ ERROR HANDLING   │ (Próba lokalnej korekcji)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ SIGNAL GENERATED  │: ERROR_ESCALATED-SIGNAL
│ (jeśli nie udana) │
└────────┬─────────┘
         │
         ▼ (Routing zewnętrzny)
┌──────────────────┐
│ AI LAB QUEUE     │ (Analiza w laboratorium)
└──────────────────┘
```

---

## 10. STATYSTYKI I MONITORING

### 10.1. Metryki Sygnałów

| Metryka | Opis | Cel |
|---------|------|-----|
| signals_generated_total | Cidade sygnałów wygenerowanych | Monitorowanie aktywności |
| signals_by_type | Rozkład sygnałów po typach | Analiza użycia |
| signals_by_priority | Rozkład sygnałów po priorytetach | Optymalizacja |
| signals_processed_time | Średni czas przetwarzania | Wydajność |
| signals_failed_total | Liczba nieudanych sygnałów | Wykrywanie problemów |
| signal_queue_length | Aktualna długość kolejki | Monitorowanie obciążenia |

### 10.2. Alerty

| Alert | Warunek | Akcja |
|-------|---------|-------|
| CRITICAL_signal_timeout | Sygnał CRITICAL nie przetworzony w 1 min | Powiadomienie developera |
| queue_overflow | Kolejka sygnałów > 1000 | Powiadomienie + czyszczenie |
| failed_signals_threshold | > 10% sygnałów nieudanych | Powiadomienie + analiza |

---

## 11. ZGODNOŚĆ Z INNYMI MODUŁAMI

### 11.1. Zgodność z Information Flow Controller

✅ **Message Formats and Validation Module:**
- Sygnały są walidowane jako komunikaty systemowe
- Format sygnałów zgodny z Message Format Specification

✅ **Context Integrity Layer:**
- Sygnały zawierają pełny kontekst
- Wykrywanie utraty kontekstu w sygnałach

✅ **System State Awareness:**
- Sygnały zawierają aktualny stan systemu
- Monitoring przez System State Awareness Module

### 11.2. Zgodność z Teacher Engine i Agent System

✅ **Teacher Engine:**
- Generuje SYSTEM SIGNALS (V5_START, V5_STOP)
- Odbiera DATA_READY-SIGNAL

✅ **Agent System:**
- Generuje AGENT SIGNALS (STRATEGY_SELECTED, MISSING_RESOURCE)
- Odbiera STATE_UPDATE-SIGNAL

---

## 12. PODSUMOWANIE

### 12.1. Korzyści z Signal System

✅ **Centralizacja komunikacji** - Jeden system sygnałów dla wszystkich modułów
✅ **Standaryzacja** - Ujednolicony format sygnałów
✅ **Traceability** - Pełna historia sygnałów
✅ **Fallback Mechanism** - Brak możliwości → sygnał → AI Laboratory
✅ **Monitoring** - Statystyki i alerty dla sygnałów
✅ **Rozszerzalność** - Nowe typy sygnałów mogą być dodawane

### 12.2. Gotowość do Implementacji

- ✅ **Architektura zdefiniowana**
- ✅ **Format sygnałów określony**
- ✅ **Routing matrix przygotowany**
- ✅ **Integracja z istniejącymi modułami zaplanowana**
- ✅ **Scenariusze użycia opisane**

---

## 13. DOKUMENTY POWIĄZANE

| Dokument | vescovo | Opis |
|----------|--------|------|
| SSI_V5_MASTER_SYSTEM_FLOW_ARCHITECTURE.md | Haupt dokument | Pełna mapa systemu |
| 08_MESSAGE_FORMATS_AND_VALIDATION.md | PSI_V5_PHASE_2_INFORMATION_FLOW | Format komunikatów |
| 03_SYSTEM_STATE_AWARENESS.md | PSI_V5_PHASE_2_INFORMATION_FLOW | Świadomość stanu |

---

*Dokument: SSI V5 System Signal Architecture | Data: 2026-08-01 | Status: FINAL DRAFT*
