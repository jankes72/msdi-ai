# SSI_V5_GATE_IMPLEMENTATION_PLAN.md

## Spis treści
1. [Wprowadzenie](#1-wprowadzenie)
2. [SSI_INPUT_GATE](#2-ssi_input_gate)
3. [SSI_OUTPUT_GATE](#3-ssi_output_gate)
4. [Routing](#4-routing)
5. [Zakaz zmian](#5-zakaz-zmian)
6. [Teacher Ecosystem](#6-teacher-ecosystem)
7. [Formaty danych](#7-formaty-danych)
8. [Zabiezpieczenia](#8-zabezpieczenia)
9. [Przykłady](#9-przykłady)

---

## 1. Wprowadzenie

Dokument opisuje plan implementacji warstwy komunikacyjnej **SSI V5** — **B3 Phase**. 
Celem jest stworzenie standaryzowanych punktów wejścia/wyjścia dla generatora, które umożliwią:
- Komunikację z agentami
- Obsługę wielu światów (football, hokej, waluty, rynki finansowe)
- Integrację z Teacher Ecosystem
- Zapis i zarządzanie pamięcią kolektywną

**Architektura docelowa:**
`SSI_V5_SPORTS_WORLD_MODEL_GENERATOR`

---

## 2. SSI_INPUT_GATE

### 2.1. Opis ogólny
**SSI_INPUT_GATE** jest pierwszym punktem kontaktowym dla żądań od agentów. Odpowiada za:
1. Odbiór i walidację żądań
2. Identyfikację `WORLD_CONTEXT`
3. Wybór odpowiedniego modułu generatora
4. Zabezpieczenie przed błędnym uruchomieniem

### 2.2. Format wejścia od agenta

Każde żądanie od agenta musi być strukturą JSON zgodną z poniższym schematem:

```json
{
  "SSI_REQUEST_ID": "string (UUID)",
  "AGENT_ID": "string",
  "WORLD_CONTEXT": "string", // football_market | hokej_market | currency_market | financial_market | custom
  "REQUEST_TYPE": "string", // analyse_probability_change | trend_analysis | amplitude_detection | relation_mapping | full_observation
  "DATA_SOURCE": {
    "type": "string", // dataBase_futbol_trend | live_feed | historical | simulated
    "params": {}
  },
  "INPUT_DATA": {},
  "PRIORITY": "low | medium | high | critical",
  "TIMESTAMP": "ISO8601"
}
```

### 2.3. Walidacja żądania

**Kryteria walidacji:**
- `SSI_REQUEST_ID` — unikalny, niepusty
- `AGENT_ID` — zarejestrowany w systemie
- `WORLD_CONTEXT` — obsługiwany przez generator
- `REQUEST_TYPE` — dopuszczalny dla danego `WORLD_CONTEXT`
- `DATA_SOURCE` — dostępny i autoryzowany
- `TIMESTAMP` — nie starszy niż 24h (domyślnie)

**Błędy walidacji:**
- `SSI_VALIDATION_ERROR` — zwrócony do agenta z powodem
- `SSI_CONTEXT_UNSUPPORTED` — nieznany `WORLD_CONTEXT`
- `SSI_REQUEST_INVALID` — nieprawidłowy format
- `SSI_SOURCE_UNAVAILABLE` — brak dostępu do `DATA_SOURCE`

### 2.4. Identyfikacja WORLD_CONTEXT

`WORLD_CONTEXT` określa, którego modułu generatora użyć. 
**Dostępne konteksty:**

| WORLD_CONTEXT | Moduł generatora | Opis |
|--------------|------------------|------|
| `football_market` | `czesc1.py` + `czesc2.py` | Analiza piłki nożnej |
| `hokej_market` | `czesc3.py` | Analiza hokeja |
| `currency_market` | `czesc4.py` | Analiza rynku walut |
| `financial_market` | `czesc4.py` | Analiza rynków finansowych |
| `custom` | Dynamiczny | Ustawiany przez `INPUT_DATA.context_override` |

### 2.5. Wybór środowiska

Na podstawie `WORLD_CONTEXT` i `REQUEST_TYPE`, **SSI_INPUT_GATE** wybiera:
- **Moduł generatora** (`czesc1-4`)
- **Teacher** (jeśli wymagany)
- **Pamięć kolektywną** (do odczytu/zapisu)

**Mapowanie:**
```
football_market + analyse_probability_change → czesc1.py + CognitiveTeacher
currency_market + trend_analysis → czesc4.py + FinancialTeacher
```

### 2.6. Zabezpieczenie przed błędnym uruchomieniem

- **Lock mechanizm:** Tylko jedno żądanie na `AGENT_ID` w danym `WORLD_CONTEXT`
- **Timeout:** Maksymalny czas oczekiwania na odpowiedź: 30s
- **Rate limiting:** 10 żądań/minutę na `AGENT_ID`
- **Circuit breaker:** Po 3 błędach z rzędu — blokada na 5 minut

---

## 3. SSI_OUTPUT_GATE

### 3.1. Opis ogólny
**SSI_OUTPUT_GATE** odpowiada za:
1. Standaryzację wyników
2. Zapis pamięci
3. Przekazywanie wiedzy do agentów/kolektywu
4. Generowanie metadanych wykonania

### 3.2. Format wyników

Każda odpowiedź z **SSI_OUTPUT_GATE** musi zawierać:

```json
{
  "SSI_RESPONSE_ID": "string (UUID)",
  "SSI_REQUEST_ID": "string", // Odwołanie do żądania
  "AGENT_ID": "string",
  "WORLD_CONTEXT": "string",
  "MODEL_USED": "string", // Nazwa modułu generatora
  "INPUT_SOURCE": "string", // Źródło danych wejściowych
  "PROCESS_STATUS": "success | partial_success | error",
  "OUTPUT_DATA": {},
  "MEMORY_UPDATE": {
    "PAMIEC_MODEL_POZNAWCZY": [],
    "WIEDZA_DLA_MODELU_DOCELOWEGO": [],
    "kolektor_wiedzy": [],
    "pamiec_obserwacji": []
  },
  "CONFIDENCE": "0.0-1.0",
  "TIMESTAMP": "ISO8601",
  "METADATA": {
    "processing_time_ms": 0,
    "hooks_used": [],
    "teacher_used": "string | null",
    "warnings": []
  }
}
```

### 3.3. Zapis pamięci

**SSI_OUTPUT_GATE** aktualizuje następujące pliki pamięci:
- `PAMIEC_MODEL_POZNAWCZY.json` — wiedza poznawcza modelu
- `WIEDZA_DLA_MODELU_DOCELOWEGO.json` — wiedza docelowa
- `kolektor_wiedzy.json` — zebrane dane z obserwacji
- `pamiec_obserwacji.json` — historia obserwacji

**Zasady zapisu:**
- Każda odpowiedź aktualizuje co najmniej jeden plik pamięci
- Aktualizacje są atomowe (transakcyjne)
- Stara wersja pamięci jest backupowana przed zmianą

### 3.4. Przekazywanie wiedzy

Wyniki są przekazywane do:
1. **Agenta** — bezpośrednia odpowiedź
2. **Collective Memory** — konsolidacja wiedzy dla wszystkich agentów
3. **Teacher Ecosystem** — aktualizacja modeli nauczania

### 3.5. Status procesu

**Możliwe statusy:**
- `success` — pełne wykonanie
- `partial_success` — częściowy wynik (np. brak danych)
- `error` — błąd podczas przetwarzania

---

## 4. Routing

### 4.1. Przepływ żądania

```
Agent
↓
SSI_INPUT_GATE
│── Walidacja żądania
│── Identyfikacja WORLD_CONTEXT
│── Wybór modułu generatora
│── Zabezpieczenia (lock, timeout, rate limiting)
↓
Generator (czesc1-4)
│── Przetwarzanie danych
│── Użycie Teacher (opcjonalnie)
│── Generowanie wyników
↓
SSI_OUTPUT_GATE
│── Standaryzacja wyników
│── Zapis pamięci
│── Generowanie metadanych
↓
Agent / Collective Memory
```

### 4.2. Ścieżki na podstawie WORLD_CONTEXT

```
football_market:
  Agent → SSI_INPUT_GATE → czesc1.py/czesc2.py → CognitiveTeacher → SSI_OUTPUT_GATE → Agent

currency_market:
  Agent → SSI_INPUT_GATE → czesc4.py → FinancialTeacher → SSI_OUTPUT_GATE → Agent

financial_market:
  Agent → SSI_INPUT_GATE → czesc4.py → MarketTeacher → SSI_OUTPUT_GATE → Collective Memory
```

### 4.3. Integracja z Teacher Ecosystem

- **CognitiveTeacher** — używany dla `football_market`
- **FinancialTeacher** — używany dla `currency_market` i `financial_market`
- **Dodatkowe 2 teachery** — do zaimplementowania dla pełnych modeli
- **Teacher Engine Core** — zarządza wszystkimi teacherami

---

## 5. Zakaz zmian

### 5.1. Niedozwolone modyfikacje

❌ **Nie zmieniać** `czesc1.py`
❌ **Nie zmieniać** `czesc2.py`
❌ **Nie zmieniać** `czesc3.py`
❌ **Nie zmieniać** `czesc4.py`

### 5.2. Dozwolone modyfikacje

✅ Dodawanie nowych plików:
- `SSI_INPUT_GATE.py`
- `SSI_OUTPUT_GATE.py`
- `SSI_ROUTER.py`
- `SSI_MEMORY_MANAGER.py`

✅ Dodawanie hooków w nowych plikach
✅ Dodawanie flag sterujących
✅ Dodawanie wejść/wyjść w warstwie SSI

---

## 6. Teacher Ecosystem

### 6.1. Istniejący Teacher Ecosystem

| Teacher | Plik | Zastosowanie |
|---------|------|--------------|
| **CognitiveTeacher** | `CognitiveTeacher.py` | Nauczanie modeli poznawczych |
| **FinancialTeacher** | `FinancialTeacher.py` | Nauczanie modeli finansowych |
| ** Teacher Engine Core** | `TeacherEngineCore.py` | Zarządzanie teacherami |

### 6.2. Nowe Teachery (do dodania)

1. **SportsTeacher** — dla `football_market` i `hokej_market`
2. **MarketTeacher** — dla `currency_market` i `financial_market`

### 6.3. Pamięć kolektywna

**Pliki pamięci do uwzględnienia:**

| Plik | Opis | Użycie |
|------|------|--------|
| `PAMIEC_MODEL_POZNAWCZY.json` | Wiedza poznawcza | Odczyt/Zapis |
| `WIEDZA_DLA_MODELU_DOCELOWEGO.json` | Wiedza docelowa | Odczyt/Zapis |
| `kolektor_wiedzy.json` | Zebrane dane | Odczyt/Zapis |
| `pamiec_obserwacji.json` | Historia obserwacji | Odczyt/Zapis |

**Zasady:**
- Każdy teacher może korzystać z pamięci kolektywnej
- Pamięć jest współdzielona między wszystkimi agentami
- Aktualizacje pamięci są logowane

---

## 7. Formaty danych

### 7.1. Format żądania (Agent → SSI_INPUT_GATE)

```json
{
  "SSI_REQUEST_ID": "a1b2c3d4-e5f6-7890",
  "AGENT_ID": "agent_001",
  "WORLD_CONTEXT": "football_market",
  "REQUEST_TYPE": "analyse_probability_change",
  "DATA_SOURCE": {
    "type": "dataBase_futbol_trend",
    "params": {
      "table": "matches",
      "range": "2023-2025"
    }
  },
  "INPUT_DATA": {
    "team_home": "Legia",
    "team_away": "ŁKS"
  },
  "PRIORITY": "high",
  "TIMESTAMP": "2025-01-15T10:30:00Z"
}
```

### 7.2. Format odpowiedzi (SSI_OUTPUT_GATE → Agent)

```json
{
  "SSI_RESPONSE_ID": "x1y2z3a4-b5c6-7890",
  "SSI_REQUEST_ID": "a1b2c3d4-e5f6-7890",
  "AGENT_ID": "agent_001",
  "WORLD_CONTEXT": "football_market",
  "MODEL_USED": "czesc1.py",
  "INPUT_SOURCE": "dataBase_futbol_trend",
  "PROCESS_STATUS": "success",
  "OUTPUT_DATA": {
    "probability_change": 0.75,
    "trend": "up",
    "amplitude": 12.5
  },
  "MEMORY_UPDATE": {
    "PAMIEC_MODEL_POZNAWCZY": ["new_observation_1"],
    "WIEDZA_DLA_MODELU_DOCELOWEGO": ["updated_knowledge_1"],
    "kolektor_wiedzy": ["collected_data_1"],
    "pamiec_obserwacji": ["observation_1"]
  },
  "CONFIDENCE": 0.92,
  "TIMESTAMP": "2025-01-15T10:30:15Z",
  "METADATA": {
    "processing_time_ms": 1500,
    "hooks_used": ["hook_1", "hook_2"],
    "teacher_used": "CognitiveTeacher",
    "warnings": []
  }
}
```

---

## 8. Zabiezpieczenia

### 8.1. Mechanizmy bezpieczeństwa

| Mechanizm | Opis | Progi |
|-----------|------|-------|
| **Lock** | Blokada wielokrotnego żądania | 1 żądanie/AGENT_ID/WORLD_CONTEXT |
| **Timeout** | Maksymalny czas przetwarzania | 30s |
| **Rate Limiting** | Ograniczenie częstotliwości | 10 żądań/min/AGENT_ID |
| **Circuit Breaker** | Blokada po błędach | 3 błędy → 5min blokady |
| **Input Validation** | Walidacja wejścia | Schema JSON |
| **Output Validation** | Walidacja wyjścia | Schema JSON |

### 8.2. Obsługa błędów

**Typy błędów:**
- `SSI_VALIDATION_ERROR` — nieprawidłowe dane wejściowe
- `SSI_CONTEXT_UNSUPPORTED` — nieobsługiwany WORLD_CONTEXT
- `SSI_TIMEOUT_ERROR` — przekroczony timeout
- `SSI_RATE_LIMIT_ERROR` — zbyt wiele żądań
- `SSI_INETRNAL_ERROR` — błąd wewnętrzny generatora

**Format błędu:**
```json
{
  "error": "SSI_VALIDATION_ERROR",
  "message": "Invalid WORLD_CONTEXT",
  "details": {"field": "WORLD_CONTEXT", "expected": "football_market | hokej_market | ..."},
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

## 9. Przykłady

### 9.1. Przykład 1: Analiza piłki nożnej

**Żądanie:**
```json
{
  "SSI_REQUEST_ID": "req_001",
  "AGENT_ID": "football_agent",
  "WORLD_CONTEXT": "football_market",
  "REQUEST_TYPE": "analyse_probability_change",
  "DATA_SOURCE": {"type": "dataBase_futbol_trend"},
  "INPUT_DATA": {"match_id": "match_123"}
}
```

**Przepływ:**
1. **SSI_INPUT_GATE** waliduje żądanie
2. Wybiera `czesc1.py` (dla `football_market`)
3. Uruchamia generator z `CognitiveTeacher`
4. **SSI_OUTPUT_GATE** zwraca:
   - `OUTPUT_DATA` z analizą prawdopodobieństwa
   - `MEMORY_UPDATE` dla `PAMIEC_MODEL_POZNAWCZY.json`

### 9.2. Przykład 2: Analiza rynku walut

**Żądanie:**
```json
{
  "SSI_REQUEST_ID": "req_002",
  "AGENT_ID": "finance_agent",
  "WORLD_CONTEXT": "currency_market",
  "REQUEST_TYPE": "trend_analysis",
  "DATA_SOURCE": {"type": "live_feed", "params": {"currency": "EUR/USD"}},
  "INPUT_DATA": {"period": "1h"}
}
```

**Przepływ:**
1. **SSI_INPUT_GATE** waliduje `currency_market`
2. Wybiera `czesc4.py` + `FinancialTeacher`
3. **SSI_OUTPUT_GATE** zwraca:
   - `OUTPUT_DATA` z trendem i amplitudą
   - `MEMORY_UPDATE` dla `kolektor_wiedzy.json`

---

## Podsumowanie

Dokument opisuje komponent plan implementacji **SSI_INPUT_GATE** i **SSI_OUTPUT_GATE** wraz z routingiem, formatami danych i integracją z Teacher Ecosystem. 

**Następne kroki:**
1. Review dokumentu
2. Zatwierdzenie planu
3. Implementacja **SSI_INPUT_GATE.py**
4. Implementacja **SSI_OUTPUT_GATE.py**
5. Testy integracyjne

---
*Document: SSI_V5_GATE_IMPLEMENTATION_PLAN.md*
*Version: 1.0*
*Status: Pending Review*
