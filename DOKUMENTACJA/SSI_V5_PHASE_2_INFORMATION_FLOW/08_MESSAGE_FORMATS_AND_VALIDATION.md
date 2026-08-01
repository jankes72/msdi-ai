# SSI V5 Phase 2 - Message Formats and Validation Module

**Data utworzenia:** 2026-08-01  
**Wersja:** 1.0.0  
**Status:** FINAL DRAFT  
**Autor:** Glowny Architekt SSI V5  
**Typ dokumentu:** Core Architecture Document  

---

## 1. DESCRIPTION

### 1.1 Cel Dokumentu

Ten dokument opisuje **Message Formats and Validation Module** - system Normalizacja formatów komunikatów oraz ich walidacji w SSI V5 Phase 2. Moduł ten zapewnia:
- ujednolicone formaty dla wszystkich komunikatów w systemie,
- walidację struktury i treści komunikatów,
- sprawdzanie poprawności kontekstu,
- kontrolę integralności danych,
- kompatybilność między wszystkimi modułami.

### 1.2 Zakres

**Message Formats and Validation Module jest odpowiedzialny za:**
- Definiowanie standardowych formatów komunikatów
- Walidację syntaktyczną i semantyczną komunikatów
- Sprawdzanie poprawności pól kontekstu
- Weryfikację integralności i autentyczności komunikatów
- Konwersję formatów pomiędzy modułami (jeśli konieczne)
- Generowanie raportów walidacji

### 1.3 Kontekst w Systemie

**Położenie w architekturze:**

```
┌─────────────────────────────────────────────────────────────┐
│              INFORMATION FLOW CONTROLLER                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │      MESSAGE FORMATS AND VALIDATION MODULE              │   │
│  │  (This Document - Standardization & Validation Layer)    │   │
│  │                                                         │   │
│  │  ✓ Format Standardization Engine                        │   │
│  │  ✓ Schema Validation Engine                             │   │
│  │  ✓ Context Validation Engine                            │   │
│  │  ✓ Integrity Verification                               │   │
│  │  ✓ Format Conversion Service (if needed)                │   │
│  │  ✓ Validation Reporting                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Other IFC Components                     │   │
│  │  - Context Integrity Layer                           │   │
│  │  - System State Awareness                            │   │
│  │  - Dynamic Context Correction                         │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Message Formats and Validation działa według następującej zasady:**

```
MODUŁ ŹRÓDŁOWY (np. Teacher Engine)
     |
     ▼
MESSAGE CREATION (Tworzenie komunikatu wg standardu)
     |
     ▼
MESSAGE FORMATS AND VALIDATION (Walidacja formatu i kontekstu)
     |
     ▼
IF VALID
     ▼
INFORMATION FLOW CONTROLLER (Przekazanie do celu)

IF INVALID
     ▼
DYNAMIC CONTEXT CORRECTION (Próba korekty)
     |
     ▼
REVALIDATION (Ponowna walidacja)
     |
     ▼
IF VALID NOW -> IFC
IF STILL INVALID -> REJECT + notification
```

**Message Formats and Validation NIE:**
- ❌ Nie modyfikuje treści komunikatów (tylko waliduje)
- ❌ Nie pobiera danych z Internetu
- ❌ Nie podejmuje decyzji biznesowych
- ❌ Nie zarządza flow komunikatów

**Message Formats and Validation MOŻE:**
- ✅ Sprawdzać poprawność formatu
- ✅ Weryfikować kontekst
- ✅ Walidować integralność
- ✅ Raportować błędy walidacji
- ✅ Sugerować poprawki

---

## 2. RESPONSIBILITIES

### 2.1 Główne Odpowiedzialności

| # | Odpowiedzialnosc | Opis | Priorytet |
|---|------------------|------|-----------|
| 1 | Format Standardization | Utrzymywanie standardów formatów | CRITICAL |
| 2 | Schema Validation | Walidacja struktury komunikatów | CRITICAL |
| 3 | Context Validation | Sprawdzanie poprawności kontekstu | CRITICAL |
| 4 | Integrity Verification | Weryfikacja integralności danych | HIGH |
| 5 | Format Conversion | Konwersja formatów (jeśli konieczna) | MEDIUM |
| 6 | Validation Reporting | Raportowanie błędów walidacji | MEDIUM |

### 2.2 Szczegółowe Funkcje

**📋 FUNKCJA 1: Format Standardization Engine**
- Definiowanie schema dla wszystkich typów komunikatów
- Utrzymywanie dokumentacji formatów
- Aktualizacja standardów w miarę ewolucji systemu
- Walidacja nowych typów komunikatów

**📋 FUNKCJA 2: Schema Validation Engine**
- Walidacja struktury JSON/YAML
- Sprawdzanie wymaganych pól
- Weryfikacja typów danych
- Sprawdzanie ograniczeń (min/max length, ranges)
- Walidacja wzorców (regex patterns)

**📋 FUNKCJA 3: Context Validation Engine**
- Walidacja pól kontekstu (data_version, system_state, itp.)
- Sprawdzanie spójności kontekstu
- Weryfikacja zgodności z System State Awareness
- Sprawdzanie aktualności kontekstu

**📋 FUNKCJA 4: Integrity Verification**
- Weryfikacja checksum/hash komunikatów
- Sprawdzanie sygnatur cyfrowych (jeśli stosowane)
- Walidacja integralność danych binarnych
- Wykrywanie modyfikacji nieautoryzowanych

**📋 FUNKCJA 5: Format Conversion Service**
- Konwersja między wersjami formatów
- Konwersja JSON <-> YAML (jeśli konieczna)
- Normalizacja formatów z modułów zewnętrznych
- Konwersja formatów historycznych

**📋 FUNKCJA 6: Validation Reporting**
- Generowanie raportów walidacji
- Statystyki błędów walidacji
- Alerty o problemach z formatami
- Sugestie poprawek

---

## 3. MESSAGE FORMAT SPECIFICATION

### 3.1 Podstawowa Struktura Komuniatu

**Wszystkie komunikaty w SSI V5 Phase 2 MUSZĄ posiadać następującą strukturę:**

```json
{
  "message_metadata": {
    "message_id": "UNIQUE_ID",
    "message_type": "TYPE_FROM_ENUM",
    "timestamp": "ISO_8601_TIMESTAMP",
    "source": {
      "module": "SOURCE_MODULE_NAME",
      "instance": "INSTANCE_ID",
      "version": "MODULE_VERSION"
    },
    "target": {
      "module": "TARGET_MODULE_NAME",
      "instance": "INSTANCE_ID"
    },
    "priority": "PRIORITY_LEVEL"
  },
  
  "context": {
    "data_version": "YYYY-MM-DD",
    "system_state": "CURRENT_STATE",
    "cycle_number": INTEGER,
    "session_id": "SESSION_ID",
    "process_type": "PROCESS_TYPE",
    "correlation_id": "CORRELATION_ID"
  },
  
  "payload": {
    // Specyficzna treść dla danego typu komuniatu
  },
  
  "security": {
    "checksum": "sha256:...",
    "signature": "DIGITAL_SIGNATURE_IF_APPLICABLE",
    "integrity_hash": "HASH_OF_PAYLOAD"
  }
}
```

### 3.2 Wymagane Pola Kontekstu

| Pole | Typ | Format | Opis | Wymagane |
|------|-----|--------|------|----------|
| data_version | string | YYYY-MM-DD | Data wersji danych | ✅ |
| system_state | string | ENUM | Aktualny stan systemu | ✅ |
| cycle_number | integer | 0-9999 | Numer cyklu V5 | ✅ |
| session_id | string | SESSION_YYYYMMDD_HHMM | Identyfikator sesji | ✅ |
| process_type | string | ENUM | Typ procesu | ✅ |
| correlation_id | string | UUID | Identyfikator korelacji | ⚪ |

### 3.3 Dozwolone Stany Systemu (system_state)

| Stan | Opis | Kiedy wystarczy |
|------|------|------------------|
| INITIALIZING | Inicjalizacja systemu | Przy starcie V5 |
| DATA_LOADING | Ładowanie danych od V1 | Po aktualizacji danych |
| PREDICTION_MODE | Tryb predykcji | Normalna praca systemu |
| TRAINING_MODE | Tryb treningowy | Podczas treningu modeli |
| ANALYSIS_MODE | Tryb analizy | Podczas znaczących analiz |
| DIAGNOSTIC_MODE | Tryb diagnostyczny | Podczas diagnostyki |
| MAINTENANCE_MODE | Tryb konserwacji | Podczas konserwacji |
| EMERGENCY_MODE | Tryb awaryjny | W przypadku awarii |
| SHUTDOWN | Wyłączanie systemu | Przy zatrzymywaniu V5 |

### 3.4 Dozwolone Typy Procesów (process_type)

| Typ Procesu | Opis | Moduł Źródłowy |
|-------------|------|-----------------|
| DATA_PROCESSING | Przetwarzanie danych | V1, Data System |
| MATCH_ANALYSIS | Analiza meczów | Teacher Engine |
| PREDICTION_GENERATION | Generowanie predykcji | Agent System |
| STRATEGY_CREATION | Tworzenie strategii | Strategy System |
| MODEL_TRAINING | Trening modeli | Teacher Engine |
| MEMORY_UPDATE | Aktualizacja pamięci | Memory System |
| COMMAND_EXECUTION | Wykonanie polecenia | Dev Command Input |
| LABORATORY_TASK | Zadanie dla laboratorium | AI Lab Integration |
| SYSTEM_MONITORING | Monitorowanie systemu | Orchestration |
| ERROR_HANDLING | Obsługa błędów | Governance |

### 3.5 Typy Komunikatów (message_type)

**Kategorie komunikatów:**

#### DATA Messages
| Typ | Opis | Payload |
|-----|------|---------|
| DATA_REQUEST | Żądanie danych | {data_type, parameters, filters} |
| DATA_RESPONSE | Odpowiedź z danymi | {data, metadata, query_info} |
| DATA_UPDATE | Aktualizacja danych | {updated_data, changes, timestamp} |

#### COMMAND Messages
| Typ | Opis | Payload |
|-----|------|---------|
| COMMAND | Polecenie do wykonania | {command, parameters, options} |
| COMMAND_ACK | Potwierdzenie odbioru | {command_id, status, timestamp} |
| COMMAND_COMPLETE | Zakończenie polecenia | {command_id, results, status} |
| COMMAND_FAILED | Błąd polecenia | {command_id, error, details} |

#### ANALYSIS Messages
| Typ | Opis | Payload |
|-----|------|---------|
| ANALYSIS_REQUEST | Żądanie analizy | {analysis_type, data, parameters} |
| ANALYSIS_RESULT | Wynik analizy | {results, metrics, confidence} |
| ANALYSIS_FEEDBACK | Informacja zwrotna | {feedback, rating, comments} |

#### TRAINING Messages
| Typ | Opis | Payload |
|-----|------|---------|
| TRAINING_REQUEST | Żądanie treningu | {model, data, parameters} |
| TRAINING.Start | Rozczęcie treningu | {training_id, model, config} |
| TRAINING_PROGRESS | Postęp treningu | {progress, metrics, checkpoint} |
| TRAINING_COMPLETE | Zakończenie treningu | {results, model_state, metrics} |

#### MEMORY Messages
| Typ | Opis | Payload |
|-----|------|---------|
| MEMORY_READ | Odczyt pamięci | {memory_type, query, filters} |
| MEMORY_WRITE | Zapis do pamięci | {memory_type, data, metadata} |
| MEMORY_SYNC | Synchronizacja pamięci | {sync_type, data, checksum} |
| MEMORY_BACKUP | Backup pamięci | {backup_type, location, timestamp} |

#### ERROR Messages
| Typ | Opis | Payload |
|-----|------|---------|
| ERROR_REPORT | Raport o błędzie | {error_code, message, stacktrace} |
| ERROR_ACK | Potwierdzenie błędu | {error_id, action, timestamp} |
| SYSTEM_ALERT | Alert systemowy | {alert_level, message, module} |

#### SYSTEM Messages
| Typ | Opis | Payload |
|-----|------|---------|
| HEARTBEAT | Sygnał życia | {module, timestamp, status} |
| STATUS_REQUEST | Żądanie statusu | {module, query} |
| STATUS_RESPONSE | Odpowiedź statusu | {module, status, metrics} |
| SYSTEM_EVENT | Zdarzenie systemowe | {event_type, data, timestamp} |

### 3.6 Schemat Walidacji JSON (JSON Schema)

**Podstawowy schemat dla wszystkich komunikatów:**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SSI_V5_Base_Message",
  "description": "Podstawowy schemat dla wszystkich komunikatów SSI V5",
  "type": "object",
  "required": ["message_metadata", "context", "payload"],
  "additionalProperties": false,
  
  "properties": {
    "message_metadata": {
      "type": "object",
      "required": ["message_id", "message_type", "timestamp", "source", "target"],
      "properties": {
        "message_id": {
          "type": "string",
          "pattern": "^MSG_[0-9]{4}(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])_[0-9]{6}_[0-9]{3}$",
          "description": "Unikalny identyfikator wiadomosci w formacie MSG_YYYYMMDD_HHMMSS_XXX"
        },
        "message_type": {
          "type": "string",
          "enum": [
            "DATA_REQUEST", "DATA_RESPONSE", "DATA_UPDATE",
            "COMMAND", "COMMAND_ACK", "COMMAND_COMPLETE", "COMMAND_FAILED",
            "ANALYSIS_REQUEST", "ANALYSIS_RESULT", "ANALYSIS_FEEDBACK",
            "TRAINING_REQUEST", "TRAINING_START", "TRAINING_PROGRESS", "TRAINING_COMPLETE",
            "MEMORY_READ", "MEMORY_WRITE", "MEMORY_SYNC", "MEMORY_BACKUP",
            "ERROR_REPORT", "ERROR_ACK", "SYSTEM_ALERT",
            "HEARTBEAT", "STATUS_REQUEST", "STATUS_RESPONSE", "SYSTEM_EVENT"
          ],
          "description": "Typ wiadomosci z domkniętej listy"
        },
        "timestamp": {
          "type": "string",
          "format": "date-time",
          "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
          "description": "Timestamp w formacie ISO 8601 UTC"
        },
        "source": {
          "type": "object",
          "required": ["module"],
          "properties": {
            "module": {"type": "string", "minLength": 1, "maxLength": 50},
            "instance": {"type": "string", "minLength": 1, "maxLength": 50},
            "version": {"type": "string", "pattern": "^[0-9]+\.[0-9]+\.[0-9]+$"}
          }
        },
        "target": {
          "type": "object",
          "required": ["module"],
          "properties": {
            "module": {"type": "string", "minLength": 1, "maxLength": 50},
            "instance": {"type": "string", "minLength": 1, "maxLength": 50}
          }
        },
        "priority": {
          "type": "string",
          "enum": ["REALTIME", "CRITICAL", "HIGH", "MEDIUM", "LOW"],
          "description": "Poziom priorytetu wiadomosci"
        }
      }
    },
    
    "context": {
      "type": "object",
      "required": ["data_version", "system_state", "cycle_number", "session_id", "process_type"],
      "properties": {
        "data_version": {
          "type": "string",
          "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
          "description": "Data wersji danych w formacie YYYY-MM-DD"
        },
        "system_state": {
          "type": "string",
          "enum": [
            "INITIALIZING", "DATA_LOADING", "PREDICTION_MODE", "TRAINING_MODE",
            "ANALYSIS_MODE", "DIAGNOSTIC_MODE", "MAINTENANCE_MODE",
            "EMERGENCY_MODE", "SHUTDOWN"
          ],
          "description": "Aktualny stan systemu"
        },
        "cycle_number": {
          "type": "integer",
          "minimum": 0,
          "maximum": 9999,
          "description": "Numer cyklu V5"
        },
        "session_id": {
          "type": "string",
          "pattern": "^SESSION_[0-9]{4}(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])_[0-9]{4}$",
          "description": "Identyfikator sesji w formacie SESSION_YYYYMMDD_HHMM"
        },
        "process_type": {
          "type": "string",
          "enum": [
            "DATA_PROCESSING", "MATCH_ANALYSIS", "PREDICTION_GENERATION",
            "STRATEGY_CREATION", "MODEL_TRAINING", "MEMORY_UPDATE",
            "COMMAND_EXECUTION", "LABORATORY_TASK", "SYSTEM_MONITORING",
            "ERROR_HANDLING"
          ],
          "description": "Typ procesu"
        },
        "correlation_id": {
          "type": "string",
          "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
          "description": "UUID do korelacji wiadomosci"
        }
      }
    },
    
    "payload": {
      "type": "object",
      "description": "Specyficzna treść wiadomosci, zależy od message_type"
    },
    
    "security": {
      "type": "object",
      "properties": {
        "checksum": {
          "type": "string",
          "pattern": "^sha256:[a-f0-9]{64}$",
          "description": "SHA-256 checksum całej wiadomosci"
        },
        "signature": {
          "type": "string",
          "description": "Sygnatura cyfrowa (opcjonalnie)"
        },
        "integrity_hash": {
          "type": "string",
          "pattern": "^sha256:[a-f0-9]{64}$",
          "description": "SHA-256 hash payload"
        }
      }
    }
  }
}
```

---

## 4. VALIDATION PROCESS

### 4.1 Główny Proces Walidacji

```
┌─────────────────────────────────────────────────────────────┐
│           MESSAGE VALIDATION PIPELINE                          │
├─────────────────────────────────────────────────────────────┤
│                                                                 │
│  INPUT: MESSAGE FROM ANY MODULE                                 │
│        │                                                      │
│        ▼                                                      │
│  ┌─────────────────────┐                                    │
│  │ 1. BASIC STRUCTURE   │                                    │
│  │    VALIDATION       │                                    │
│  │    - Check if JSON  │                                    │
│  │    - Check required │                                    │
│  │      top-level     │                                    │
│  │      fields        │                                    │
│  │    - Check data    │                                    │
│  │      types         │                                    │
│  └──────────┬───────────┘                                    │
│              │                                                 │
│         ┌────┴────┐                                           │
│         │         │                                           │
│    ┌────▼────┐ ┌──▼────┐                                      │
│    │ VALID   │ │INVALID │                                      │
│    └────┬────┘ └─────┬──┘                                      │
│         │            │                                          │
│         ▼            ▼                                          │
│    ┌────────    ┌─────────────────┐                            │
│    │ 2. SCHEMA │ │ REJECT MESSAGE   │                            │
│    │ VALIDATION│ │ + Notify source  │                            │
│    │            │ │    module      │                            │
│    │ - Validate│ │                 │                            │
│    │   against │ │ ← END VALIDATION│                            │
│    │   JSON    │ │   (for this     │                            │
│    │   Schema │ │    message)     │                            │
│    └────┬─────┘ └─────────────────┘                            │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────────────┐                                    │
│  │ 3. CONTEXT         │                                    │
│  │    VALIDATION       │                                    │
│  │    - Verify all    │                                    │
│  │      context       │                                    │
│  │      fields        │                                    │
│  │    - Check         │                                    │
│  │      data_version  │                                    │
│  │    - Check         │                                    │
│  │      system_state  │                                    │
│  │    - Validate with │                                    │
│  │      System State  │                                    │
│  │      Awareness    │                                    │
│  └──────────┬───────────┘                                    │
│              │                                                 │
│         ┌────┴────┐                                           │
│         │         │                                           │
│    ┌────▼────┐ ┌──▼────┐                                      │
│    │ VALID   │ │INVALID │                                      │
│    └────┬────┘ └────┬────┘                                      │
│         │            │                                          │
│         ▼            ▼                                          │
│    ┌────────    ┌─────────────────┐                            │
│    │ 4.         │ │ SEND TO DCC     │ (Dynamic Context          │
│    │ INTEGRITY  │ │    for possible  │  Correction)              │
│    │ VERIFICATION│ │    correction    │                            │
│    │            │ │                 │                            │
│    │ - Check   │ │ ← REVALIDATE     │                            │
│    │   checksum │ │    after        │                            │
│    │ - Verify  │ │    correction   │                            │
│    │   hash    │ │                 │                            │
│    └────┬─────┘ └─────────────────┘                            │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────────────┐                                    │
│  │ 5. PAYLOAD       │                                    │
│  │    VALIDATION    │                                    │
│  │    - Validate   │                                    │
│  │      payload    │                                    │
│  │      structure  │                                    │
│  │    - Check      │                                    │
│  │      message-   │                                    │
│  │      specific   │                                    │
│  │      rules      │                                    │
│  └──────────┬───────────┘                                    │
│              │                                                 │
│         ┌────┴────┐                                           │
│         │         │                                           │
│    ┌────▼────┐ ┌──▼────┐                                      │
│    │ VALID   │ │INVALID │                                      │
│    └────┬────┘ └────┬────┘                                      │
│         │            │                                          │
│         ▼            ▼                                          │
│    ┌────────    ┌─────────────────┐                            │
│    │ APPROVED │ │ SEND TO DCC     │                            │
│    │ (Send to │ │    + Notify     │                            │
│    │  IFC)    │ │    source       │                            │
│    └─────────┘ └─────────────────┘                            │
│                                                         │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Proces Walidacji Schemy

**Schema Validation Flow:**

```
1. LOAD APPROPRIATE SCHEMA
   └─ Based on message_type

2. VALIDATE STRUCTURE
   ├─ Check all required fields exist
   └─ Check no extra fields exist

3. VALIDATE DATA TYPES
   ├─ Check each field has correct type
   └─ Handle type coercion if configured

4. VALIDATE CONSTRAINTS
   ├─ Check string lengths
   ├─ Check numeric ranges
   └─ Check pattern matching (regex)

5. VALIDATE ENUMS
   └─ Check enum values are valid

6. COLLECT VALIDATION RESULTS
   └─ List of all validation errors/warnings
```

### 4.3 Proces Walidacji Kontekstu

**Context Validation Flow:**

```
1. CHECK REQUIRED CONTEXT FIELDS
   └─ data_version, system_state, cycle_number, session_id, process_type

2. VALIDATE FIELD FORMATS
   ├─ data_version: YYYY-MM-DD format
   ├─ session_id: SESSION_YYYYMMDD_HHMM format
   └─ cycle_number: 0-9999 range

3. VALIDATE SYSTEM STATE
   ├─ Check if state is in allowed enum
   └─ Check if state transition is valid

4. VERIFY CONSISTENCY WITH SSA
   ├─ Compare with System State Awareness
   └─ Check if context matches actual system state

5. CHECK DATA VERSION
   ├─ Verify data_version is valid
   └─ Check if data_version is current

6. GENERATE CONTEXT VALIDATION REPORT
   └─ List of context validation issues
```

### 4.4 Proces Weryfikacji Integralności

**Integrity Verification Flow:**

```
1. EXTRACT SECURITY DATA
   └─ Get checksum, signature, integrity_hash from message

2. RECONDIT DANE
   └─ Reconstruct message without security section

3. CALCULATE CHECKSUM
   └─ Compute SHA-256 of reconstructed message

4. COMPARE CHECKSUMS
   ├─ If match: Integralność potwierdzona
   └─ If not match: INTEGRITY_ERROR

5. VERIFY PAYLOAD HASH (if present)
   └─ Verify hash of payload matches integrity_hash

6. VERIFY DIGITAL SIGNATURE (if present)
   └─ Use public key to verify signature
```

### 4.5 Proces Walidacji Payload

**Payload Validation Flow:**

```
1. IDENTIFY PAYLOAD SCHEMA
   └─ Based on message_type

2. VALIDATE PAYLOAD STRUCTURE
   └─ Validate against message_type-specific schema

3. VALIDATE BUSINESS RULES
   ├─ Check business logic constraints
   └─ Validate domain-specific rules

4. COLLECT PAYLOAD VALIDATION RESULTS
   └─ List of payload-specific validation issues
```

---

## 5. OUTPUT

### 5.1 Dane Wyjściowe

**Message Formats and Validation genera:**
- Potwierdzenia poprawności komunikatów
- Raporty błędów walidacji
- Komunikaty o odrzuceniu
- Statystyki walidacji

### 5.2 Typy Odpowiedzi

**📋 VALIDATION_SUCCESS**
```json
{
  "validation_result": "SUCCESS",
  "message_id": "MSG_20260801_1600_001",
  "validated_at": "2026-08-01T16:00:01Z",
  "validation_time_ms": 5,
  "checks_performed": [
    {"check": "STRUCTURE_VALIDATION", "status": "PASS"},
    {"check": "SCHEMA_VALIDATION", "status": "PASS"},
    {"check": "CONTEXT_VALIDATION", "status": "PASS"},
    {"check": "INTEGRITY_VERIFICATION", "status": "PASS"},
    {"check": "PAYLOAD_VALIDATION", "status": "PASS"}
  ],
  "warnings": [],
  "forward_to": "INFORMATION_FLOW_CONTROLLER"
}
```

**📋 VALIDATION_FAILURE**
```json
{
  "validation_result": "FAILURE",
  "message_id": "MSG_20260801_1600_002",
  "validated_at": "2026-08-01T16:00:02Z",
  "validation_time_ms": 8,
  "error_code": "INVALID_CONTEXT",
  "error_message": "Context validation failed",
  "errors": [
    {
      "check": "CONTEXT_VALIDATION",
      "status": "FAIL",
      "field": "system_state",
      "error_code": "INVALID_ENUM_VALUE",
      "error_message": "system_state 'TRAINING' is not valid in current system state",
      "expected": ["PREDICTION_MODE", "ANALYSIS_MODE"],
      "actual": "TRAINING"
    },
    {
      "check": "CONTEXT_VALIDATION",
      "status": "FAIL",
      "field": "data_version",
      "error_code": "OUTDATED_VERSION",
      "error_message": "data_version is 2 days old",
      "current_version": "2026-08-01",
      "message_version": "2026-07-30"
    }
  ],
  "suggested_action": "APPLY_CONTEXT_CORRECTION",
  "forward_to": "DYNAMIC_CONTEXT_CORRECTION",
  "retry_after_correction": true
}
```

**📋 VALIDATION_WARNING**
```json
{
  "validation_result": "SUCCESS_WITH_WARNINGS",
  "message_id": "MSG_20260801_1600_003",
  "validated_at": "2026-08-01T16:00:01Z",
  "validation_time_ms": 10,
  "warnings": [
    {
      "check": "PAYLOAD_VALIDATION",
      "status": "WARN",
      "field": "payload.parameters.learning_rate",
      "warning_code": "RECOMMENDED_RANGE_EXCEEDED",
      "warning_message": "learning_rate 0.1 is higher than recommended max 0.01",
      "recommended_value": 0.01
    },
    {
      "check": "CONTEXT_VALIDATION",
      "status": "WARN",
      "field": "cycle_number",
      "warning_code": "CYCLE_OUT_OF_SYNC",
      "warning_message": "cycle_number differs from system cycle",
      "system_cycle": 43,
      "message_cycle": 42
    }
  ],
  "forward_to": "INFORMATION_FLOW_CONTROLLER",
  "message": "Message validated with warnings, use with caution"
}
```

**📋 VALIDATION_REJECT**
```json
{
  "validation_result": "REJECTED",
  "message_id": "MSG_20260801_1600_004",
  "validated_at": "2026-08-01T16:00:03Z",
  "rejection_reason": "CRITICAL_VALIDATION_FAILURE",
  "errors": [
    {
      "check": "STRUCTURE_VALIDATION",
      "status": "FAIL",
      "error_code": "MISSING_REQUIRED_FIELD",
      "field": "message_metadata.message_id",
      "error_message": "Required field message_id is missing"
    },
    {
      "check": "SCHEMA_VALIDATION",
      "status": "FAIL",
      "error_code": "INVALID_MESSAGE_TYPE",
      "field": "message_metadata.message_type",
      "error_message": "Invalid message_type: UNKNOWN_TYPE",
      "allowed_types": ["DATA_REQUEST", "COMMAND", "ANALYSIS_REQUEST", ...]
    }
  ],
  "suggested_action": "FIX_MESSAGE_FORMAT_AND_RESEND",
  "source_module": "TEACHER_ENGINE",
  "notification_sent": true,
  "message": "Message rejected due to critical validation errors"
}
```

### 5.3 Raport Walidacji

**📋 VALIDATION_STATISTICS_REPORT** (Generowany okresowo)
```json
{
  "report_type": "VALIDATION_STATISTICS_REPORT",
  "period": {
    "start": "2026-08-01T00:00:00Z",
    "end": "2026-08-01T23:59:59Z"
  },
  "summary": {
    "total_messages_validated": 1423,
    "messages_valid": 1380,
    "messages_with_warnings": 25,
    "messages_rejected": 18,
    "messages_corrected": 12,
    "validation_success_rate": 0.970,
    "avg_validation_time_ms": 8
  },
  "by_validation_type": {
    "STRUCTURE_VALIDATION": {"total": 1423, "failed": 0, "success_rate": 1.0},
    "SCHEMA_VALIDATION": {"total": 1423, "failed": 5, "success_rate": 0.9965},
    "CONTEXT_VALIDATION": {"total": 1423, "failed": 12, "success_rate": 0.9915},
    "INTEGRITY_VERIFICATION": {"total": 1423, "failed": 1, "success_rate": 0.9993},
    "PAYLOAD_VALIDATION": {"total": 1423, "failed": 8, "success_rate": 0.9944}
  },
  "by_message_type": {
    "DATA_REQUEST": {"count": 345, "rejected": 2, "rejection_rate": 0.0058},
    "COMMAND": {"count": 201, "rejected": 0, "rejection_rate": 0.0},
    "ANALYSIS_REQUEST": {"count": 456, "rejected": 8, "rejection_rate": 0.0175},
    "TRAINING_REQUEST": {"count": 123, "rejected": 5, "rejection_rate": 0.0407},
    "HEARTBEAT": {"count": 298, "rejected": 3, "rejection_rate": 0.0101}
  },
  "by_source_module": {
    "TEACHER_ENGINE": {"count": 456, "rejected": 10, "rejection_rate": 0.0219},
    "AGENT_SYSTEM": {"count": 345, "rejected": 2, "rejection_rate": 0.0058},
    "SYSTEM_ORCHESTRATION": {"count": 234, "rejected": 1, "rejection_rate": 0.0043},
    "AI_LABORATORY": {"count": 123, "rejected": 3, "rejection_rate": 0.0244},
    "DEVELOPER_COMMAND": {"count": 265, "rejected": 2, "rejection_rate": 0.0075}
  },
  "most_common_errors": [
    {
      "error_code": "INVALID_CONTEXT",
      "count": 8,
      "percentage": 0.0056,
      "modules": ["TEACHER_ENGINE", "AGENT_SYSTEM"]
    },
    {
      "error_code": "OUTDATED_VERSION",
      "count": 5,
      "percentage": 0.0035,
      "modules": ["TEACHER_ENGINE"]
    }
  ],
  "recommendations": [
    "Implement automatic context version checking in TEACHER_ENGINE",
    "Add validation to AGENT_SYSTEM for context fields",
    "Consider reducing rejection threshold for non-critical errors"
  ]
}
```

---

## 6. SCHEMAS

### 6.1 Schematy Dla Specyficznych Typów Wiadomości

**Schemat dla DATA_REQUEST:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "DATA_REQUEST",
  "type": "object",
  "required": ["data_type", "parameters"],
  "properties": {
    "data_type": {
      "type": "string",
      "enum": ["MATCHES", "ODDS", "RESULTS", "STATISTICS", "HISTORICAL", "ANALYSIS"],
      "description": "Typ żądanych danych"
    },
    "parameters": {
      "type": "object",
      "properties": {
        "date_range": {
          "type": "object",
          "properties": {
            "start": {"type": "string", "format": "date"},
            "end": {"type": "string", "format": "date"}
          },
          "required": ["start", "end"]
        },
        "filters": {
          "type": "object",
          "additionalProperties": true
        },
        "limit": {
          "type": "integer",
          "minimum": 1,
          "maximum": 10000
        },
        "include": {
          "type": "array",
          "items": {"type": "string"}
        }
      }
    }
  }
}
```

**Schemat dla COMMAND:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "COMMAND",
  "type": "object",
  "required": ["command", "parameters"],
  "properties": {
    "command": {
      "type": "string",
      "enum": [
        "START_ANALYSIS", "STOP_ANALYSIS", "GENERATE_PREDICTION",
        "TRAIN_MODEL", "VALIDATE_DATA", "RUN_DIAGNOSTIC",
        "SYNC_MEMORY", "BACKUP_SYSTEM", "RESTART_MODULE"
      ],
      "description": "Komenda do wykonania"
    },
    "parameters": {
      "type": "object",
      "additionalProperties": true,
      "description": "Parametry komendy, zależne od typu"
    },
    "options": {
      "type": "object",
      "properties": {
        "timeout_ms": {"type": "integer", "minimum": 0, "maximum": 86400000},
        "retry_on_failure": {"type": "boolean"},
        "max_retries": {"type": "integer", "minimum": 0, "maximum": 10}
      }
    }
  }
}
```

**Schemat dla ANALYSIS_REQUEST:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ANALYSIS_REQUEST",
  "type": "object",
  "required": ["analysis_type", "data", "criteria"],
  "properties": {
    "analysis_type": {
      "type": "string",
      "enum": [
        "MATCH_ANALYSIS", "TEAM_ANALYSIS", "LEAGUE_ANALYSIS",
        "PERFORMANCE_ANALYSIS", "TREND_ANALYSIS", "PATTERN_DISCOVERY"
      ],
      "description": "Typ analizy"
    },
    "data": {
      "type": "object",
      "properties": {
        "references": {
          "type": "array",
          "items": {"type": "string"}
        },
        "inline_data": {"type": "object"}
      }
    },
    "criteria": {
      "type": "object",
      "properties": {
        "confidence_threshold": {"type": "number", "minimum": 0, "maximum": 1},
        "min_data_points": {"type": "integer", "minimum": 1},
        "time_window_hours": {"type": "integer", "minimum": 1, "maximum": 720}
      }
    }
  }
}
```

---

## 7. MEMORY USED

### 7.1 Używana Pamięć

| Typ Pamięci | Cel | Dostęp | Aktualizacja |
|-------------|-----|--------|-------------|
| JSON Schemas | Schematy walidacji | READ | Przy starcie systemu |
| Validation Cache | Cache wyników walidacji | READ/WRITE | Dynamicznie |
| Error Patterns | Wzorce błędów walidacji | READ/WRITE | Każdy błąd |
| Statistics | Statystyki walidacji | READ/WRITE | Codziennie |

### 7.2 Struktura Pamięci

**JSON Schemas Collection:**
```json
{
  "schemas": {
    "SSI_V5_Base_Message": {
      "version": "1.0.0",
      "last_updated": "2026-08-01T00:00:00Z",
      "status": "ACTIVE",
      "schema": {...}
    },
    "DATA_REQUEST": {
      "version": "1.0.0",
      "last_updated": "2026-08-01T00:00:00Z",
      "status": "ACTIVE",
      "schema": {...}
    },
    "COMMAND": {
      "version": "1.0.0",
      "last_updated": "2026-08-01T00:00:00Z",
      "status": "ACTIVE",
      "schema": {...}
    }
  },
  "schema_versions": {
    "current": "1.0.0",
    "previous": ["0.9.0"]
  }
}
```

---

## 8. MEMORY UPDATED

### 8.1 Aktualizowana Pamięć

| Typ Pamięci | Czym | Czystość | Retencja |
|-------------|------|---------|----------|
| Validation Log | Logi walidacji | Każda walidacja | 6 miesięcy |
| Error Log | Błędy walidacji | Każdy błąd | 1 rok |
| Schema History | Historia schematów | Każda zmiana | 2 lata |

---

## 9. COMMUNICATION

### 9.1 Komunikacja z Innymi Modułami

| Moduł | Typ Komunikacji | Cel | Protokół |
|--------|-----------------|-----|----------|
| Information Flow Controller | INTERNAL | Odbieranie i przekazywanie komunikatów | Direct Call |
| Context Integrity Layer | INTERNAL | Współpraca przy walidacji kontekstu | Direct Call |
| System State Awareness | INTERNAL | Pobieranie aktualnego stanu systemu | Direct Call |
| Dynamic Context Correction | INTERNAL | Przekazywanie błędów do korekty | Direct Call |
| System Governance | INTERNAL | Raportowanie krytycznych błędów | Direct Call |

---

## 10. ERROR HANDLING

### 10.1 Rodzaje Obsługiwanych Błędów

| Kod Błędu | Opis | Akcja |
|-----------|------|-------|
| MISSING_REQUIRED_FIELD | Brakujące wymagane pole | REJECT + powiadomienie źródła |
| INVALID_DATA_TYPE | Niewłaściwy typ danych | REJECT + sugerowanie poprawki |
| INVALID_ENUM_VALUE | Niewłaściwa wartość enum | REJECT/WARNING w zależności od Kontekst |
| PATTERN_MISMATCH | Niezgodność z wzorcem | REJECT + informacja o wzorcu |
| OUT_OF_RANGE | Wartość poza zakresem | REJECT/WARNING |
| INVALID_CONTEXT | Błędny kontekst | SEND TO DCC + retry |
| OUTDATED_VERSION | Przestarzała wersja danych | WARNING + sugerowanie aktualizacji |
| INTEGRITY_ERROR | Błąd integralności | CRITICAL REJECT + alert |
| INVALID_MESSAGE_TYPE | Niewłaściwy typ wiadomości | REJECT + lista dozwolonych typów |
| SCHEMA_NOT_FOUND | Schemat nie znaleziony | REJECT + powiadomienie administratora |

### 10.2 Obsługa Krytycznych Błędów

**Critical Validation Failure Procedure:**

```
1. DETECT CRITICAL VALIDATION ERROR
   └─ Error that cannot be automatically resolved

2. LOG CRITICAL ERROR
   └─ Full details in error log with CRITICAL severity

3. NOTIFY SOURCE MODULE
   └─ Immediate notification to message source

4. NOTIFY SYSTEM GOVERNANCE
   └─ Alert about critical validation issue

5. REJECT MESSAGE
   └─ Prevent message from being processed

6. LOG FOR ANALYSIS
   └─ Pattern analysis and improvement
```

---

## 11. PERFORMANCE

### 11.1 Wymagania Wydajnościowe

| Metryka | Cel | Limit |
|---------|-----|-------|
| Czas walidacji struktury | < 1ms | < 5ms |
| Czas walidacji schemy | < 2ms | < 10ms |
| Czas walidacji kontekstu | < 2ms | < 10ms |
| Czas weryfikacji integralności | < 1ms | < 5ms |
| Czas walidacji payload | < 3ms | < 15ms |
| Czas całkowitej walidacji | < 10ms | < 30ms |
| Pamięć używana | < 20MB | < 50MB |
| Przeptywość walidacji | > 10,000 msg/s | > 1,000 msg/s |

---

## 12. FUTURE EXTENSIONS

### 12.1 Możliwości Rozbudowy

| Rozbudowa | Opis | Priorytet |
|-----------|------|-----------|
| XML Support | Obsługa komunikatów XML | LOW |
| Avro Support | Obsługa formatu Avro | LOW |
| Protobuf Support | Obsługa Protobuf | MEDIUM |
| Schema Evolution | Automatyczna obsługa nowych wersji schematów | HIGH |
| AI-Based Validation | Walidacja wspomagana AI | LOW |
| Automated Schema Generation | Automatyczne generowanie schematów | MEDIUM |

---

## 13. PODSUMOWANIE

### 13.1 Kluczowe Właściwości Message Formats and Validation

✅ **Standaryzacja formatów** - Ujednolicone formaty dla wszystkich komunikatów  
✅ **Pełna walidacja** - Sprawdzanie wszystkich aspektów komunikatów  
✅ **Integracja z DCC** - Współpraca z Dynamic Context Correction  
✅ **Bezpieczeństwo** - Weryfikacja integralności i autentyczności  
✅ **Elastyczność** - Obsługa różnych typów komunikatów  
✅ **Statystyki** - Kompleksowe raportowanie i analiza  

### 13.2 Integracja z SSI V5

- **Część IFC** - Zintegrowany z Information Flow Controller
- **Krytyczna rola** - Wszystkie komunikaty muszą przejść walidację
- **Separation of Concerns** - Tylko waliduje, nie modyfikuje treści
- **Pełna zgodność** - Obsługa wszystkich modułów SSI V5
- **Bezpieczeństwo** - Chroni system przed błędnymi danymi

### 13.3 Korzyści dla Systemu

**Bez Message Formats and Validation:**
- ❌ Brak standaryzacji komunikatów
- ❌ Błędy w strukturze komunikatów nie są wykrywane
- ❌ Moduły muszą same walidować dane
- ❌ Problem z debugowaniem błędów w komunikacji

**Z Message Formats and Validation:**
- ✅ Ustandaryzowane i przewidywalne komunikaty
- ✅ Wczesne wykrywanie błędów formatu
- ✅ Centralna walidacja dla wszystkich modułów
- ✅ Łatwe debugowanie i analiza problemów
- ✅ Bezpieczeństwo i integralność danych

---

**Data utworzenia:** 2026-08-01  
**Wersja:** 1.0.0  
**Status:** FINAL DRAFT  
**Autor:** Glowny Architekt SSI V5  

**📌 NOTATKA KOŃCOWA:**
Message Formats and Validation Module jest kluczowym elementem zapewniajacym poprawnosc i spojnosc wszystkich komunikatow w systemie SSI V5 Phase 2. Bez tego modułu system nie byłby w stanie zagwarantowac poprawnosci przesyłanych danych pomiędzy modułami.

**🎯 NASTĘPNY DOKUMENT:** 09_ERROR_HANDLING_AND_RECOVERY.md - Obsługa błędów i odzysk systemu