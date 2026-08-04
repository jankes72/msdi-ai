# SSI V5 - GENERATOR AGENT INTERFACE

## Kontrakt Interfejsu Miedzy Agentami a Generatorem

**Data:** 2026-08-03  
**Status:** PROJEKT KONTRAKTU (ETAP B1)  
**Wersja:** 1.0 - Do zatwierdzenia przed implementacja

---

## 1. ARCHITEKTURA WARSTW

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SSI V5 AGENT-GENERATOR INTERFACE                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────┐     ┌─────────────────────────┐     ┌─────────┐ │
│  │                 │     │                         │     │         │ │
│  │   AGENT         │────▶│    SSI_INPUT_GATE       │────▶│  CZĘŚĆ  │ │
│  │   (External)    │     │   (Wejscie Kontrolowane) │     │   1     │ │
│  │                 │     │                         │     │  BUDOWA │ │
│  └─────────────────┘     └─────────────┬───────────┘     │  MODELI │ │
│                                  │                    │         │ │
│                                  │   SSI_EVENT       │         │         │ │
│                                  ▼                    ▼         │         │ │
│                            ┌─────────────────────────────────┐   │         │ │
│                            │  SSI_V5_SPORTS_WORLD_MODEL_      │   │         │ │
│                            │  GENERATOR                       │   │         │ │
│                            │  (Generator Glowny)              │◀──┘         │ │
│                            │                                     │         │ │
│                            │  ┌─────────────────────────────┐  │         │ │
│                            │  │  CZĘŚĆ 1: Budowa Modeli       │  │         │ │
│                            │  │  CZĘŚĆ 2: Predykcja          │  │         │ │
│                            │  │  CZĘŚĆ 3: Teacher Engine      │  │         │ │
│                            │  │  CZĘŚĆ 4: Analiza Operacyjna │  │         │ │
│                            │  └─────────────────────────────┘  │         │ │
│                            └──────────────────┬────────────────┘   │         │ │
│                                           │                        │         │ │
│                                           ▼                        ▼         │ │
│                            ┌─────────────────────────────────┐   │         │ │
│                            │    SSI_OUTPUT_GATE              │   │         │ │
│                            │   (Wyjscie Kontrolowane)         │   │         │ │
│                            └──────────────────┬────────────────┘   │         │ │
│                                           │                           │         │ │
│                                           ▼                           ▼         │ │
│                                    ┌─────────────────┐            ┌─────┐ │ │
│                                    │   AGENT         │            │ ... │ │ │
│                                    │   (External)    │            │     │ │ │
│                                    └─────────────────┘            └─────┘ │ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. ZASADY OGOLNE

### 2.1 Separacja Odpowiedzialnosci

| Warstwa | Odpowiedzialnosc | Dostep |
|--------|------------------|--------|
| **Agent** | Wysyla zapyta, odbiera wyniki | Zewnetrzny |
| **SSI_INPUT_GATE** | Walidacja, routing, transformacja | Wyłacznie przez SSI_EVENT |
| **Generator** | Przetwarzanie, analiza, generowanie | Wewnetrzny |
| **SSI_OUTPUT_GATE** | Formatowanie, filtrowanie, zwrot | Wyłacznie do Agentow |

### 2.2 Kluczowe Zasady

1. **Agent NIGDY nie dotyka bezposrednio kodu generatora**
2. **Wszystkie zapyta musza ostrze SSI_EVENT**
3. **Generator NIGDY nie wywoluje beach agentow**
4. **Wszystkie dane wejsciowe/wyjsciowe sa walidowane**
5. **Kontrakt musi byc stabilny - zmiany wymagaja wersji 2.0**

---

## 3. KONTRAKT SSI_EVENT

### 3.1 Typy Eventow

| Typ Eventu | Opis | Kierunek |
|------------|------|----------|
| `SSI_REQUEST` | Zapyanie od Agenta | Agent → Generator |
| `SSI_RESPONSE` | Odpowiedz dla Agenta | Generator → Agent |
| `SSI_NOTIFICATION` | Powiadomienie (np. gotowosc modelu) | Generator → Agent |
| `SSI_HEARTBEAT` | Sprawdzenie stanu | Obustronny |
| `SSI_ERROR` | Blad przetwarzania | Obustronny |

---

## 4. KONTRAKT SSI_AGENT_INPUT (WEJSCIE)

### 4.1 Struktura Bazowa

```json
{
  "ssi_version": "5.0",
  "event_type": "SSI_REQUEST",
  "timestamp": "2026-08-03T14:30:00Z",
  "request_id": "UUID_v4",
  "agent_id": "AGENT_001",
  "contract_version": "1.0",
  "action": "string",
  "world": "string",
  "target": "string",
  "parameters": {},
  "context": {}
}
```

### 4.2 Pola Wymagane

| Pole | Typ | Opis | Wymagane |
|------|-----|------|----------|
| `ssi_version` | string | Wersja SSI | ✅ |
| `event_type` | enum | Typ eventu (SSI_REQUEST) | ✅ |
| `timestamp` | ISO8601 | Data/czas zapytania | ✅ |
| `request_id` | UUID | Unikalny identyfikator | ✅ |
| `agent_id` | string | Identyfikator agenta | ✅ |
| `contract_version` | string | Wersja kontraktu | ✅ |
| `action` | enum | Akcja do wykonania | ✅ |
| `world` | enum | Swiat/sport | ⚠️ (zalezy od action) |
| `target` | string | Cel operacji | ⚠️ (zalezy od action) |
| `parameters` | object | Parametry akcji | ❌ |
| `context` | object | Kontekst dodatkowy | ❌ |

---

## 5. DEFINICJE AKCJI (ACTIONS)

### 5.1 Akcje Ogolne (Generator)

#### `ping` - Sprawdzenie Stanu
```json
{
  "action": "ping",
  "world": null,
  "target": null,
  "parameters": {},
  "context": {}
}
```

**Opis:** Sprawdza czy generator jest dostepny.  
**Odpowiedź:** Status generatora i wersje komponentow.

---

#### `status` - Status Generatora
```json
{
  "action": "status",
  "world": null,
  "target": null,
  "parameters": {
    "detailed": true/false,
    "components": ["czesc1", "czesc2", "czesc3", "czesc4"]
  },
  "context": {}
}
```

**Opis:** Zwraca status wszystkich czesci generatora.  
**Odpowiedź:** Stan kazdej czesci, ostatnie operacje, bledy.

---

### 5.2 Akcje dla Modeli (Czesc1 - Budowa)

#### `build_model` - Budowa Nowego Modelu
```json
{
  "action": "build_model",
  "world": "football",
  "target": "siec_08_log_koniec",
  "parameters": {
    "data_source": "dataBase_futbol_trend",
    "training_range": "2020-01-01_to_2026-01-01",
    "features": ["feature1", "feature2"],
    "layers": [128, 64, 32],
    "epochs": 100,
    "batch_size": 32
  },
  "context": {
    "priority": "high",
    "callback_url": "https://agent.example.com/callback"
  }
}
```

**Opis:** Buduje nowy model sieci neuronowej.  
**Dostepne `world`:** `"football"`, `"hockey"` (przyszłosc)  
**Dostepne `target`:** Nazwa sieci (np. `"siec_08_log_koniec"`)  
**Odpowiedź:** Status budowy, ID operacji, szacowany czas.

---

#### `train_model` - Trening Istnie الرواية Modelu
```json
{
  "action": "train_model",
  "world": "football",
  "target": "siec_08_log_koniec",
  "parameters": {
    "data_source": "dataBase_futbol_trend",
    "training_range": "2024-01-01_to_2026-01-01",
    "validation_split": 0.2,
    "epochs": 50
  },
  "context": {
    "resume_training": false,
    "model_version": "v1.2.0"
  }
}
```

**Opis:** Trenuje istniejacy model na nowych danych.  
**Odpowiedź:** Postep treningu, metryki (loss, accuracy).

---

#### `load_model` - Ladowanie Modelu
```json
{
  "action": "load_model",
  "world": "football",
  "target": "siec_08_log_koniec",
  "parameters": {
    "model_path": "modele_dataBase_futbol_trend/siec_08_log_koniec/model.h5",
    "load_metadata": true,
    "load_classes": true
  },
  "context": {
    "persistent": true
  }
}
```

**Opis:** Laduje model do pamieci generatora.  
**Odpowiedź:** Status ladowania, metadane modelu.

---

### 5.3 Akcje dla Predykcji (Czesc2 - Predykcja)

#### `predict` - Generowanie Predykcji
```json
{
  "action": "predict",
  "world": "football",
  "target": "dataBase_futbol_trend",
  "parameters": {
    "model": "siec_08_log_koniec",
    "data_range": "latest",
    "match_ids": ["MECZ_001", "MECZ_002"],
    "confidence_threshold": 0.7,
    "include_features": true
  },
  "context": {
    "store_in_memory": true,
    "generate_history": true
  }
}
```

**Opis:** Generuje predykcje dla podanych meczow.  
**Dostepne `data_range`:** `"latest"`, `"today"`, `"range:2026-08-01_to_2026-08-03"`  
**Odpowiedź:** Lista predykcji z pewnoscia, klasyfikacja.

---

#### `predict_batch` - Predykcja wsadowa
```json
{
  "action": "predict_batch",
  "world": "football",
  "target": "all_models",
  "parameters": {
    "data_source": "dataBase_futbol_trend",
    "batch_size": 1000,
    "start_date": "2026-08-01",
    "end_date": "2026-08-03"
  },
  "context": {
    "async": true,
    "notify_on_complete": true
  }
}
```

**Opis:** Predykcja dla wiekszej partii danych.  
**Odpowiedź:** ID operacji (async) lub wyniki (sync).

---

#### `get_prediction_history` - Historia Predykcji
```json
{
  "action": "get_prediction_history",
  "world": "football",
  "target": "siec_08_log_koniec",
  "parameters": {
    "match_id": "MECZ_001",
    "limit": 100,
    "include_results": true
  },
  "context": {
    "format": "json"
  }
}
```

**Opis:** Pobiera historie predykcji dla meczu/modelu.  
**Odpowiedź:** Lista predykcji z datami, wynikami, pewnoscia.

---

### 5.4 Akcje dla Wiedzy Poznawczej (Czesc3 - Teacher Engine)

#### `generate_knowledge` - Generowanie Wiedzy Poznawczej
```json
{
  "action": "generate_knowledge",
  "world": "football",
  "target": "PAMIEC_MODEL_POZNAWCZY",
  "parameters": {
    "models": ["siec_08_log_koniec", "siec_09_ratio_start"],
    "data_range": "all",
    "include_errors": true,
    "depth": "deep"
  },
  "context": {
    "regenerate": false
  }
}
```

**Opis:** Generuje pamięć poznawczą na podstawie predykcji i rezultatow.  
**Odpowiedź:** Status generowania, rozmiar wiedzy, metryki.

---

#### `get_cognitive_memory` - Pobranie Pamieci Poznawczej
```json
{
  "action": "get_cognitive_memory",
  "world": "football",
  "target": "PAMIEC_MODEL_POZNAWCZY",
  "parameters": {
    "model": "siec_08_log_koniec",
    "query": "remis",
    "limit": 10
  },
  "context": {
    "format": "structured"
  }
}
```

**Opis:** Pobiera fragment pamięci poznawczej.  
**Odpowiedź:** Wyszukane wzorce, powiazania, statystyki.

---

#### `update_teacher_engine` - Aktualizacja Teacher Engine
```json
{
  "action": "update_teacher_engine",
  "world": "football",
  "target": "CognitiveTeacher",
  "parameters": {
    "new_weights": {"feature1": 0.8, "feature2": 0.5},
    "learning_rate": 0.01,
    "strategy": "reinforcement"
  },
  "context": {
    "validate": true
  }
}
```

**Opis:** Aktualizuje parametry Teacher Engine.  
**Odpowiedź:** Status aktualizacji, nowe metryki.

---

### 5.5 Akcje dla Analizy Operacyjnej (Czesc4 - Laboratorium)

#### `analyze_trends` - Analiza Trendow
```json
{
  "action": "analyze_trends",
  "world": "football",
  "target": "dataBase_futbol_trend",
  "parameters": {
    "model": "siec_08_log_koniec",
    "trend_type": "price_movement",
    "time_range": "30_days",
    "min_confidence": 0.75
  },
  "context": {
    "include_visualization": false
  }
}
```

**Opis:** Analiza trendow dla podanego modelu/ekosystemu.  
**Dostepne `trend_type`:** `"price_movement"`, `"volume"`, `"ratio"`, `"statistics"`  
**Odpowiedź:** Statystyki, wzorce, anomalie.

---

#### `get_knowledge_collector` - Pobranie Kolektora Wiedzy
```json
{
  "action": "get_knowledge_collector",
  "world": "football",
  "target": "kolektor_wiedzy",
  "parameters": {
    "date_from": "2026-07-01",
    "date_to": "2026-08-01",
    "metrics": ["accuracy", "confidence", "errors"]
  },
  "context": {
    "aggregate": true
  }
}
```

**Opis:** Pobiera zebrana wiedze z Laboratorium V2.  
**Odpowiedź:** Agregowana wiedza dla okresu.

---

#### `get_observation_memory` - Pobranie Pamieci Obserwacji
```json
{
  "action": "get_observation_memory",
  "world": "football",
  "target": "pamiec_obserwacji",
  "parameters": {
    "match_id": "MECZ_001",
    "limit": 50,
    "include_changes": true
  },
  "context": {
    "format": "detailed"
  }
}
```

**Opis:** Pobiera pamięć obserwacji dla meczu/modelu.  
**Odpowiedź:** Historia obserwacji, zmiany predykcji, pewnosc.

---

#### `evaluate_model` - Ocena Modelu
```json
{
  "action": "evaluate_model",
  "world": "football",
  "target": "siec_08_log_koniec",
  "parameters": {
    "test_range": "2026-01-01_to_2026-07-31",
    "metrics": ["accuracy", "precision", "recall", "f1"],
    "cross_validation": true
  },
  "context": {
    "generate_report": true
  }
}
```

**Opis:** Pełna ocena modelu na danych testowych.  
**Odpowiedź:** Dokument oceny z metrykami i zaleceniami.

---

### 5.6 Akcje dla Ekosystemow

#### `list_ecosystems` - Lista Dostepnych Ekosystemow
```json
{
  "action": "list_ecosystems",
  "world": null,
  "target": null,
  "parameters": {
    "include_disabled": false
  },
  "context": {}
}
```

**Opis:** Zwraca liste wszystkich dostepnych ekosystemow.  
**Odpowiedź:** Nazwy ekosystemow, status, opisy.

---

#### `get_ecosystem_status` - Status Ekosystemu
```json
{
  "action": "get_ecosystem_status",
  "world": "football",
  "target": "dataBase_futbol_trend",
  "parameters": {
    "include_models": true,
    "include_data": true
  },
  "context": {}
}
```

**Opis:** Zwraca status konkretnego ekosystemu.  
**Odpowiedź:** Stan modeli, dostepnosc danych, ostatnie operacje.

---

#### `switch_ecosystem` -Przelacz Ekosystem
```json
{
  "action": "switch_ecosystem",
  "world": "football",
  "target": "kursy_przygotowane",
  "parameters": {
    "model": "siec_01_start_kursow",
    "activate": true
  },
  "context": {}
}
```

**Opis:** Aktywuje/deaktywuje ekosystem.  
**Odpowiedź:** Status przelaczenia.

---

## 6. KONTRAKT SSI_AGENT_OUTPUT (WYJSCIE)

### 6.1 Struktura Bazowa

```json
{
  "ssi_version": "5.0",
  "event_type": "SSI_RESPONSE",
  "timestamp": "2026-08-03T14:30:05Z",
  "request_id": "UUID_v4",
  "agent_id": "AGENT_001",
  "contract_version": "1.0",
  "status": "success|error|pending|partial",
  "action": "string",
  "response": {},
  "metadata": {},
  "warnings": []
}
```

### 6.2 Pola Wymagane

| Pole | Typ | Opis | Wymagane |
|------|-----|------|----------|
| `ssi_version` | string | Wersja SSI | ✅ |
| `event_type` | enum | Typ eventu (SSI_RESPONSE) | ✅ |
| `timestamp` | ISO8601 | Data/czas odpowiedzi | ✅ |
| `request_id` | UUID | ID zapyta | ✅ |
| `agent_id` | string | Identyfikator agenta | ✅ |
| `contract_version` | string | Wersja kontraktu | ✅ |
| `status` | enum | Status wykonania | ✅ |
| `action` | string | Akcja ktora byla wykonana | ✅ |
| `response` | object | Dane odpowiedzi | ⚠️ (zalezy od status) |
| `metadata` | object | Metadane odpowiedzi | ❌ |
| `warnings` | array | Ostrzezenia | ❌ |

---

## 7. DEFINICJE STATUSOW

### 7.1 Statusy Glowne

| Status | Opis | Kiedy Uzywac |
|--------|------|--------------|
| `success` |Operacja zakonczona powodzeniem | Wszystko OK |
| `error` | Blad podczas operacji | Wyjatek, blad walidacji |
| `pending` | Operacja w toku (async) | Długotrwałe operacje |
| `partial` | Czesciowy sukces | část operacji sie powiodła |

### 7.2 Statusy Szczegolowe (dla poszczegolnych akcji)

| Akcja | Możliwe Statusy |
|-------|-----------------|
| `build_model` | `building`, `completed`, `failed` |
| `train_model` | `training`, `epoch_X_Y`, `completed`, `failed` |
| `predict` | `predicting`, `completed`, `failed` |
| `generate_knowledge` | `generating`, `completed`, `failed` |

---

## 8. PRZYKLADOWE ODPOWIEDZI

### 8.1 Odpowiedz dla `predict`

```json
{
  "ssi_version": "5.0",
  "event_type": "SSI_RESPONSE",
  "timestamp": "2026-08-03T14:30:05Z",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_id": "AGENT_001",
  "contract_version": "1.0",
  "status": "success",
  "action": "predict",
  "response": {
    "model": "siec_08_log_koniec",
    "world": "football",
    "ecosystem": "dataBase_futbol_trend",
    "predictions": [
      {
        "match_id": "MECZ_001",
        "prediction": "1",
        "confidence": 0.85,
        "class": 0,
        "features": {"feature1": 0.7, "feature2": 0.9},
        "timestamp": "2026-08-03T14:30:00Z"
      },
      {
        "match_id": "MECZ_002",
        "prediction": "X",
        "confidence": 0.72,
        "class": 1,
        "features": {"feature1": 0.5, "feature2": 0.8},
        "timestamp": "2026-08-03T14:30:00Z"
      }
    ],
    "statistics": {
      "total": 2,
      "average_confidence": 0.785,
      "high_confidence_count": 1
    }
  },
  "metadata": {
    "processing_time_ms": 450,
    "model_version": "v1.2.0",
    "data_timestamp": "2026-08-03T14:25:00Z"
  },
  "warnings": []
}
```

---

### 8.2 Odpowiedz dla `get_observation_memory`

```json
{
  "ssi_version": "5.0",
  "event_type": "SSI_RESPONSE",
  "timestamp": "2026-08-03T14:31:00Z",
  "request_id": "550e8400-e29b-41d4-a716-446655440001",
  "agent_id": "AGENT_001",
  "contract_version": "1.0",
  "status": "success",
  "action": "get_observation_memory",
  "response": {
    "match_id": "MECZ_001",
    "observations": [
      {
        "timestamp": "2026-08-03T12:00:00Z",
        "prediction": "1",
        "actual_result": "1",
        "confidence": 0.85,
        "hit": true,
        "model": "siec_08_log_koniec",
        "notes": "pierwsza_obserwacja"
      },
      {
        "timestamp": "2026-08-03T14:00:00Z",
        "prediction": "1",
        "actual_result": null,
        "confidence": 0.82,
        "hit": null,
        "model": "siec_08_log_koniec",
        "notes": null
      }
    ],
    "statistics": {
      "total_observations": 50,
      "hits": 38,
      "accuracy": 0.76,
      "confidence_distribution": {
        "0.0-0.25": 2,
        "0.25-0.50": 8,
        "0.50-0.75": 20,
        "0.75-1.0": 20
      }
    }
  },
  "metadata": {
    "storage_location": "modele_dataBase_futbol_trend/siec_08_log_koniec/obserwacja/pamiec_obserwacji.json"
  },
  "warnings": [
    "No actual result for latest observation"
  ]
}
```

---

### 8.3 Odpowiedz dla `evaluate_model`

```json
{
  "ssi_version": "5.0",
  "event_type": "SSI_RESPONSE",
  "timestamp": "2026-08-03T14:35:00Z",
  "request_id": "550e8400-e29b-41d4-a716-446655440002",
  "agent_id": "AGENT_001",
  "contract_version": "1.0",
  "status": "success",
  "action": "evaluate_model",
  "response": {
    "model": "siec_08_log_koniec",
    "evaluation_range": "2026-01-01_to_2026-07-31",
    "metrics": {
      "accuracy": 0.82,
      "precision": 0.80,
      "recall": 0.78,
      "f1_score": 0.79,
      "confusion_matrix": {
        "1": {"1": 120, "X": 15, "2": 10},
        "X": {"1": 20, "X": 80, "2": 5},
        "2": {"1": 5, "X": 12, "2": 110}
      }
    },
    "class_performance": {
      "1": {"precision": 0.83, "recall": 0.84, "f1": 0.83, "support": 145},
      "X": {"precision": 0.75, "recall": 0.72, "f1": 0.73, "support": 117},
      "2": {"precision": 0.81, "recall": 0.79, "f1": 0.80, "support": 128}
    },
    "recommendations": [
      "Model performs well on class '1'",
      "Consider retraining with more data for class 'X'",
      "Confidence threshold of 0.75 recommended"
    ]
  },
  "metadata": {
    "evaluation_id": "EVAL_20260803_143500",
    "samples_count": 390,
    "processing_time_ms": 2450
  },
  "warnings": []
}
```

---

### 8.4 Odpowiedz dla `error`

```json
{
  "ssi_version": "5.0",
  "event_type": "SSI_RESPONSE",
  "timestamp": "2026-08-03T14:40:00Z",
  "request_id": "550e8400-e29b-41d4-a716-446655440003",
  "agent_id": "AGENT_001",
  "contract_version": "1.0",
  "status": "error",
  "action": "predict",
  "response": {
    "error": {
      "code": "MODEL_NOT_LOADED",
      "message": "Model siec_08_log_koniec is not loaded in memory",
      "details": {
        "model": "siec_08_log_koniec",
        "available_models": ["siec_09_ratio_start", "siec_10_ratio_koniec"]
      }
    }
  },
  "metadata": {
    "error_timestamp": "2026-08-03T14:40:00Z"
  },
  "warnings": []
}
```

---

## 9. KODY BLEDOW

### 9.1 Kody Ogolne

| Kod | Opis | HTTP Status |
|-----|------|-------------|
| `INVALID_REQUEST` | Nieprawidłowa struktura zapytania | 400 |
| `INVALID_ACTION` | Nieznana akcja | 400 |
| `INVALID_PARAMETERS` | Bledne parametry akcji | 400 |
| `UNAUTHORIZED` | Brak uprawnien | 401 |
| `NOT_FOUND` | Zasob nie znaleziony | 404 |
| `INTERNAL_ERROR` | Blad wewnetrzny generatora | 500 |
| `SERVICE_UNAVAILABLE` | Generator niedostepny | 503 |

### 9.2 Kody Specyficzne dla Generatora

| Kod | Opis | Dotyczacy |
|-----|------|-----------|
| `MODEL_NOT_FOUND` | Model nie istnieje | build_model, load_model |
| `MODEL_NOT_LOADED` | Model nie zaladowany | predict, evaluate |
| `MODEL_ALREADY_EXISTS` | Model juz istnieje | build_model |
| `TRAINING_IN_PROGRESS` | Trening w toku | train_model |
| `NO_DATA_AVAILABLE` | Brak danych | predict, analyze |
| `INVALID_DATA_RANGE` | Nieprawidłowy zakres dat | predict, analyze |
| `MEMORY_NOT_AVAILABLE` | Pamięć niedostępna | get_cognitive_memory |
| `ECOSYSTEM_NOT_AVAILABLE` | Ekosystem niedostępny | switch_ecosystem |

---

## 10. WALIDACJA DANYCH

### 10.1 Walidacja SSI_AGENT_INPUT

```python
# Pseudokod walidacji
def validate_input(request):
    # 1. Sprawdz wersje SSI
    if request.get('ssi_version') not in ['5.0']:
        raise ValidationError('Unsupported SSI version')
    
    # 2. Sprawdz typ eventu
    if request.get('event_type') != 'SSI_REQUEST':
        raise ValidationError('Invalid event type')
    
    # 3. Sprawdzcontract_version
    if request.get('contract_version') != '1.0':
        raise ValidationError('Unsupported contract version')
    
    # 4. Sprawdz wymagane pola
    required_fields = ['timestamp', 'request_id', 'agent_id', 'action']
    for field in required_fields:
        if field not in request:
            raise ValidationError(f'Missing required field: {field}')
    
    # 5. Sprawdz format timestamp
    if not is_valid_iso8601(request.get('timestamp')):
        raise ValidationError('Invalid timestamp format')
    
    # 6. Sprawdz format request_id (UUID v4)
    if not is_valid_uuid4(request.get('request_id')):
        raise ValidationError('Invalid request_id format')
    
    # 7. Sprawdz akcje
    if request.get('action') not in ALLOWED_ACTIONS:
        raise ValidationError('Invalid action')
    
    # 8. Sprawdz parametry dla akcji
    action_params = ACTION_PARAMETERS.get(request.get('action'))
    if action_params:
        validate_action_parameters(request, action_params)
    
    return True
```

### 10.2 Walidacja Specyficznych Pol

| Pole | Walidacja | Opis |
|------|-----------|------|
| `world` | enum: `['football', 'hockey']` | Dopuszczalne swiaty |
| `target` | string (max 100) | Nazwa celu |
| `model` | regex: `[a-z0-9_]+` | Poprawna nazwa modelu |
| `data_range` | enum/regex | `latest`, `today`, lub zakres dat |
| `confidence` | float (0.0-1.0) | Prawidlowa pewnosc |

---

## 11. BEZPIECZENSTWO

### 11.1 Autoryzacja

- Wszystkie zapyta musza byc **podpisane** (JWT lub similar)
- Agent musi miec **uprawnienia** do danej akcji
- **Rate limiting** na poziomie agenta i akcji

### 11.2 Ograniczenia

| Akcja | Max na minute | Max równoczesne |
|-------|---------------|-----------------|
| `ping` | 60 | 10 |
| `status` | 10 | 5 |
| `predict` | 30 | 15 |
| `build_model` | 5 | 2 |
| `train_model` | 3 | 1 |
| Inne | 20 | 10 |

### 11.3 Audyt

- Wszystkie zapyta i odpowiedzi sa **logowane**
- **Audit trail** dla operacji krytycznych (build, train, delete)
- **Encryption** dla wrażliwych danych

---

## 12. ROZSZERZALNOSC

### 12.1 Nowe Akcje

Nowe akcje moga byc dodawane w przyszłych wersjach kontraktu.  
Kazda nowa akcja musi:
1. Zostac zdefiniowana w nowej wersji kontraktu
2. Byc **wstecznie kompatybilna** lub miec mechanizm migracji
3. Zostac udokumentowana z przykladami

### 12.2 Nowe Swiaty (Worlds)

Nowe swiaty (np. `"hockey"`, `"tennis"`) moga byc dodawane bez zmiany kontraktu.  
Wymaga jedynie:
1. Rejestracji w generatorze
2. Zdefiniowania dostepnych ekosystemow
3. Aktualizacji dokumentacji

### 12.3 Nowe Ekosystemy

Nowe ekosystemy (np. `"dataBase_hockey_trend"`) moga byc dodawane dynamicznie.  
Wymaga:
1. Konfiguracji w generatorze
2. Zarejestrowania w `list_ecosystems`

---

## 13. WERSJONOWANIE KONTRAKTU

### 13.1 Zasady Wersjonowania

| Zmiana | Wersja | Opis |
|--------|--------|------|
| Poprawki bledow | Patch (1.0.1) | Bledy w istniejacych polach |
| Nowe pola opcjonalne | Minor (1.1.0) | Nowe pola nie wymagane |
| Zmiany w polach wymaganych | Major (2.0.0) | Zmiany niekompatybilne |

### 13.2 Historia Wersji

| Wersja | Data | Zmiany |
|--------|------|--------|
| 1.0 | 2026-08-03 | Pierwotna wersja kontraktu |

---

## 14. DOKUMENTACJA TECHNICZNA

### 14.1 Schematy JSON

Pełne schematy JSON dostepne w:
- `schemas/SSI_AGENT_INPUT_v1.0.json`
- `schemas/SSI_AGENT_OUTPUT_v1.0.json`

### 14.2 Przyklady w Raznych Jezykach

#### Python
```python
import json
from uuid import uuid4
from datetime import datetime

# Tworzenie zapytania
request = {
    "ssi_version": "5.0",
    "event_type": "SSI_REQUEST",
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "request_id": str(uuid4()),
    "agent_id": "AGENT_001",
    "contract_version": "1.0",
    "action": "predict",
    "world": "football",
    "target": "dataBase_futbol_trend",
    "parameters": {
        "model": "siec_08_log_koniec",
        "data_range": "latest"
    }
}

# Wyslanie zapytania (przyklad z requests)
import requests
response = requests.post(
    "http://generator.ssid5.local/api/v1/event",
    json=request,
    headers={"Authorization": "Bearer TOKEN", "Content-Type": "application/json"}
)

# Obsluga odpowiedzi
if response.status_code == 200:
    result = response.json()
    if result.get('status') == 'success':
        predictions = result['response']['predictions']
        # Przetwarzanie...
```

#### JavaScript
```javascript
// Tworzenie zapytania
const request = {
    ssi_version: "5.0",
    event_type: "SSI_REQUEST",
    timestamp: new Date().toISOString(),
    request_id: crypto.randomUUID(),
    agent_id: "AGENT_001",
    contract_version: "1.0",
    action: "predict",
    world: "football",
    target: "dataBase_futbol_trend",
    parameters: {
        model: "siec_08_log_koniec",
        data_range: "latest"
    }
};

// Wyslanie zapytania (przyklad z fetch)
fetch('http://generator.ssid5.local/api/v1/event', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer TOKEN',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(request)
})
.then(response => response.json())
.then(data => {
    if (data.status === 'success') {
        const predictions = data.response.predictions;
        // Przetwarzanie...
    }
});
```

---

## 15. PODSUMOWANIE

### 15.1 Co Zostalo Zdefiniowane

✅ **Archiitektura warstw**: Agent → SSI_INPUT_GATE → Generator → SSI_OUTPUT_GATE → Agent  
✅ **Typy eventow**: SSI_REQUEST, SSI_RESPONSE, SSI_NOTIFICATION, SSI_HEARTBEAT, SSI_ERROR  
✅ **Kontrakt wejścia**: SSI_AGENT_INPUT z 15+ akcjami  
✅ **Kontrakt wyjścia**: SSI_AGENT_OUTPUT ze strukturami odpowiedzi  
✅ **Walidacja danych**: Zasady i przyklady  
✅ **Bezpieczeństwo**: Autoryzacja, rate limiting, audyt  
✅ **Rozszerzalność**: Nowe akcje, swiaty, ekosystemy  
✅ **Wersjonowanie**: Zasady aktualizacji kontraktu

### 15.2 Co Dalej (ETAP B2)

Po zatwierdzeniu tego dokumentu:

1. **ETAP B2**: Stworzyć `SSI_V5_GENERATOR_HOOK_MAP.md` - mapa hooków w oparciu o ten kontrakt
2. **ETAP B3**: Zaimplementować SSI_INPUT_GATE i SSI_OUTPUT_GATE
3. **ETAP C**: Zaimplementować hooki w czesc1-4.py

### 15.3 Zalecenia

1. **Nie zmieniac kodu** az ten kontrakt nie zostanie zatwierdzony
2. **Przetestować kontrakt** na mockach przed implementacja
3. **Utrzymywać wersjonowanie** - kazda zmiana wymaga nowej wersji
4. **Dokumentować zmiany** w histori wersji

---

## 16. HISTORIA DOKUMENTU

| Data | Wersja | Autor | Opis |
|------|--------|-------|------|
| 2026-08-03 | 1.0 | Mistral Vibe | Pierwotna wersja kontraktu interfejsu Agent-Generator |

---

**Status:** Oczekuje na zatwierdzenie (ETAP B1)  
**Nastepny krok:** ETAP B2 (Mapa Hooków) po zatwierdzeniu
