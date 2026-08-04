# SSI V5 - GENERATOR HOOK MAP

## Uniwersalna Mapa Punktow Wejścia/Wyjścia dla World Trend Analysis Engine

**Data:** 2026-08-03  
**Status:** PROJEKT MAPY HOOKÓW (ETAP B2)  
**Wersja:** 1.0 - Do zatwierdzenia przed implementacja  
**Zakres:** Przygotowanie architektury dla uniwersalnego SSI V5 World Trend Analysis Engine

---

## 🎯 CELE DOKUMENTU

1. **Zdefiniować warstwy abstrakcji** pomiędzy agentami a generatorem
2. **Mapować punkty wejścia/wyjścia** dla różnych światów danych
3. **Przygotować architekturę** dla przyszłych ekosystemów (waluty, giełda, etc.)
4. **Zapewnić spójność** pomiędzy Częściami 1-4
5. **Umożliwić rozbudowę** bez przebudowy istniejącego kodu

---

## 🏗️ ARCHITEKTURA WARSTW

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SSI V5 WORLD TREND ANALYSIS ENGINE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      WARSTWA 4: AGENT                                    │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │   │
│  │  │   SPORTS AGENT  │  │  FINANCE AGENT  │  │   CUSTOM AGENT   │      │   │
│  │  │                 │  │                 │  │                 │      │   │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘      │   │
│  │           │                 │                 │                 │   │
│  └───────────┼─────────────────┼─────────────────┼─────────────────┘   │
│                │                 │                 │                     │
│                ▼                 ▼                 ▼                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      WARSTWA 1: STEROWANIE                               │   │
│  │                    (Globalne Punkty Kontrolne)                         │   │
│  │                                                                         │   │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │   │
│  │  │ SSI_GENERATOR_   │  │ SSI_WORLD_LOAD   │  │ SSI_GENERATOR_   │   │   │
│  │  │     START       │──▶│    & CONFIG      │──▶│     STOP        │   │   │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘   │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│                │                                                             │
│                ▼                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      WARSTWA 2: KONTEKST ŚWIATA                         │   │
│  │                    (World Context Layer)                                 │   │
│  │                                                                         │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │                   WORLD_CONTEXT                                  │   │   │
│  │  │  {                                                               │   │   │
│  │  │    "world_id": "football_odds|EUR_USD|SP500",                 │   │   │
│  │  │    "domain": "sports|financial_market|commodities",            │   │   │
│  │  │    "source": "dataBase_futbol_trend|fx_data|market_data",     │   │   │
│  │  │    "observation_type": "match|price|candlestick|volume",        │   │   │
│  │  │    "prediction_target": "match_result|price_direction|index",    │   │   │
│  │  │    "time_window": "1h|1d|1w|1m",                              │   │   │
│  │  │    "output_type": ["trend", "probability", "stability"]         │   │   │
│  │  │  }                                                               │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│                │                                                             │
│                ▼                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      WARSTWA 3: CZĘŚCI GENERATORA                       │   │
│  │                    (Component-Specific Hooks)                           │   │
│  │                                                                         │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │  CZĘŚĆ 1    │  │  CZĘŚĆ 2    │  │  CZĘŚĆ 3    │              │   │
│  │  │  Budowa     │  │  Predykcja  │  │  Teacher    │              │   │
│  │  │  Modeli     │  │  & Analiza  │  │  Engine     │              │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │   │
│  │         │                 │                 │                      │   │
│  │  ┌─────▼──────┐      ┌─────▼──────┐      ┌─────▼──────┐          │   │
│  │  │ MODEL_BUILD │      │ PREDICT    │      │ KNOWLEDGE  │          │   │
│  │  │ MODEL_TRAIN │      │ ANALYZE    │      │ GENERATE   │          │   │
│  │  │ MODEL_SAVE  │      │ VALIDATE   │      │ TEACH      │          │   │
│  │  └─────────────┘      └─────────────┘      └─────────────┘          │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│                │                                                             │
│                ▼                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      WARSTWA 0: DANE & EKOSYSTEMY                         │   │
│  │                    (Data & Ecosystem Layer)                              │   │
│  │                                                                         │   │
│  │  SPORTS WORLD                 FINANCIAL WORLD                       │   │
│  │  ├── football_odds             ├── EUR_USD                            │   │
│  │  │   ├── dataBase_futbol_trend │   ├── GBP_USD                        │   │
│  │  │   ├── siec_08_log_koniec    │   ├── EUR_GBP                        │   │
│  │  │   └── ...                  │   └── ...                           │   │
│  │  │                             elhos                                   │   │
│  │  └── hockey_odds              ├── SP500                             │   │
│  │      └── ...                  ├── NASDAQ                           │   │
│  │                                   └── ...                           │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🌍 UNIWERSALNA ARCHITEKTURA ŚWIATÓW

### Aktualne Środowiska (Zaimplementowane)

| Środowisko | Domain | World ID | Source | Prediction Target | Output Type |
|------------|--------|----------|--------|-------------------|-------------|
| **Piłka Nożna** | sports | `football_odds` | `dataBase_futbol_trend` | `match_result` | `probability`, `trend` |
| **Kursy Piłka** | sports | `football_courses` | `kursy_przygotowane` | `price_movement` | `probability`, `trend` |

### Przyszłe Środowiska (Do Dodania)

| Środowisko | Domain | World ID | Source | Prediction Target | Output Type |
|------------|--------|----------|--------|-------------------|-------------|
| **Waluty** | financial_market | `EUR_USD` | `fx_data` | `price_direction` | `trend`, `probability`, `volatility` |
| **Waluty** | financial_market | `GBP_USD` | `fx_data` | `price_direction` | `trend`, `probability`, `volatility` |
| **Giełda** | financial_market | `SP500` | `market_data` | `index_direction` | `trend`, `probability`, `stability` |
| **Giełda** | financial_market | `NASDAQ` | `market_data` | `index_direction` | `trend`, `probability`, `stability` |
| **Surowce** | commodities | `GOLD` | `commodity_data` | `price_direction` | `trend`, `probability`, `volatility` |
| **Surowce** | commodities | `OIL` | `commodity_data` | `price_direction` | `trend`, `probability`, `volatility` |
| **Hokej** | sports | `hockey_odds` | `dataBase_hockey_trend` | `match_result` | `probability`, `trend` |

---

## ⚙️ WARSTWA 1: STEROWANIE GENERATOREM

### Hooki Globalne (Kontrola Cyklu Życia)

| Hook | Typ | Lokalizacja | Opis | Parametry | Zwracane |
|------|-----|-------------|------|-----------|-----------|
| **`SSI_GENERATOR_START`** | START | Początek głównych operacji | Inicjalizacja generatora | `config`, `worlds` | `status`, `timestamp` |
| **`SSI_GENERATOR_READY`** | STATUS | Po załadowaniu wszystkich modułów | Generator gotowy do pracy | - | `components`, `versions` |
| **`SSI_GENERATOR_PAUSE`** | CONTROL | Przerwanie przetwarzania | Wstrzymanie wszystkich operacji | `graceful` | `status`, `pending_operations` |
| **`SSI_GENERATOR_RESUME`** | CONTROL | Wznowienie po pauzie | Kontynuacja operacji | - | `status`, `resumed_operations` |
| **`SSI_GENERATOR_STOP`** | STOP | Zakończenie pracy | Czyszczenie zasobów | `force` | `status`, `cleanup_report` |
| **`SSI_GENERATOR_ERROR`** | ERROR | Obsługa błędów krytycznych | Reakcja na błędy systemowe | `error_code`, `details` | `recovery_actions`, `status` |

### Diagram Sekwencji - Cykl Życia

```
Agent                          SSI_INPUT_GATE          Generator
  │                                │                  │
  │── SSI_REQUEST (start) ───────▶│                  │
  │                                │── SSI_GENERATOR_START ──▶│
  │                                │                  │
  │◀── SSI_RESPONSE (ready) ─────│◀─ SSI_GENERATOR_READY ──│
  │                                │                  │
  │── SSI_REQUEST (action) ───────▶│                  │
  │                                │── SSI_WORLD_LOAD ——▶│
  │                                │                  │
  │◀── SSI_RESPONSE (result) ─────│◀───── (result) ───────│
  │                                │                  │
  │── SSI_REQUEST (stop) ────────▶│                  │
  │                                │── SSI_GENERATOR_STOP ──▶│
  │                                │                  │
  │◀── SSI_RESPONSE (stopped) ────│◀─ SSI_GENERATOR_STOP ──│
```

---

## 🌐 WARSTWA 2: KONTEKST ŚWIATA (World Context Layer)

### Struktura WORLD_CONTEXT

```json
{
  "context_id": "UUID_v4",
  "timestamp": "ISO8601",
  
  // Identyfikacja świata
  "world_id": "football_odds|EUR_USD|SP500|GOLD",
  "world_name": "Football Odds Analysis|EUR/USD Forex|S&P 500 Index|Gold Commodity",
  
  // Klasyfikacja
  "domain": "sports|financial_market|commodities|crypto",
  "category": "match_prediction|currency_pair|stock_index|commodity",
  
  // Źródło danych
  "source": {
    "type": "database|csv|api|stream",
    "location": "dane/dataBase_futbol_trend.csv|api.forex.com|...",
    "format": "csv|json|parquet",
    "update_frequency": "realtime|1min|1h|1d"
  },
  
  // Typ obserwacji
  "observation_type": "match|price|candlestick|volume|timestamp",
  "observation_window": {
    "size": "1h|1d|1w|1m|all",
    "unit": "minutes|hours|days|weeks"
  },
  
  // Cel predykcji
  "prediction_target": "match_result|price_direction|index_value|volatility",
  "prediction_type": "classification|regression|trend_analysis",
  
  // Oczekiwany typ wyjścia
  "output_type": [
    "trend",        // wzrost/spadek/stabilność
    "probability",   // prawdopodobieństwo [0-1]
    "direction",    // +1/-1/0
    "magnitude",    // siła zmienności
    "confidence",   // pewność modelu
    "stability",    // stabilność trendu
    "volatility",   // zmienność
    "time_frame"     // ramy czasowe
  ],
  
  // Parametry czasowe
  "time_window": {
    "start": "ISO8601",
    "end": "ISO8601",
    "duration": "PT1H|P1D|P1W"
  },
  
  // Kontekst dodatkowy
  "metadata": {
    "priority": "low|medium|high",
    "agent_id": "AGENT_001",
    "session_id": "SESSION_UUID",
    "correlation_id": "CORR_UUID"
  }
}
```

### Hooki Kontekstu Świata

| Hook | Typ | Opis | WORLD_CONTEXT | Zwracane |
|------|-----|------|---------------|-----------|
| **`SSI_WORLD_LOAD`** | LOAD | Ładowanie kontekstu świata | ✅ Wymagany | `world_config`, `status` |
| **`SSI_WORLD_SELECT`** | SELECT | Wybór aktywnego świata | ✅ Wymagany | `active_world`, `available_worlds` |
| **`SSI_WORLD_CONFIGURE`** | CONFIG | Konfiguracja parametrów świata | ✅ Wymagany | `configuration`, `validation` |
| **`SSI_WORLD_VALIDATE`** | VALIDATE | Walidacja kontekstu | ✅ Wymagany | `is_valid`, `errors`, `warnings` |
| **`SSI_WORLD_SWITCH`** | SWITCH | Zmiana świata w trakcie sesji | ⚠️ Opcjonalny | `previous_world`, `new_world` |
| **`SSI_WORLD_UNLOAD`** | UNLOAD | Zwolnienie kontekstu świata | ⚠️ Opcjonalny | `status`, `cleanup_report` |

### Przykłady WORLD_CONTEXT

#### 🏈 Piłka Nożna (Obecne)
```json
{
  "world_id": "football_odds",
  "world_name": "Football Match Odds Analysis",
  "domain": "sports",
  "category": "match_prediction",
  "source": {
    "type": "csv",
    "location": "dane/dataBase_futbol_trend.csv",
    "format": "csv",
    "update_frequency": "1d"
  },
  "observation_type": "match",
  "observation_window": {"size": "1d", "unit": "days"},
  "prediction_target": "match_result",
  "prediction_type": "classification",
  "output_type": ["probability", "trend", "confidence"],
  "time_window": {"duration": "P7D"}
}
```

#### 💱 Waluty (Przyszłe)
```json
{
  "world_id": "EUR_USD",
  "world_name": "EUR/USD Forex Pair Analysis",
  "domain": "financial_market",
  "category": "currency_pair",
  "source": {
    "type": "api",
    "location": "api.forex.com/realtime",
    "format": "json",
    "update_frequency": "realtime"
  },
  "observation_type": "price",
  "observation_window": {"size": "1h", "unit": "hours"},
  "prediction_target": "price_direction",
  "prediction_type": "trend_analysis",
  "output_type": ["trend", "probability", "volatility", "magnitude"],
  "time_window": {"duration": "PT1H"}
}
```

#### 📈 Giełda (Przyszłe)
```json
{
  "world_id": "SP500",
  "world_name": "S&P 500 Index Analysis",
  "domain": "financial_market",
  "category": "stock_index",
  "source": {
    "type": "api",
    "location": "api.marketdata.com/sp500",
    "format": "json",
    "update_frequency": "1min"
  },
  "observation_type": "candlestick",
  "observation_window": {"size": "1d", "unit": "days"},
  "prediction_target": "index_direction",
  "prediction_type": "trend_analysis",
  "output_type": ["trend", "probability", "stability", "volatility"],
  "time_window": {"duration": "P1D"}
}
```

---

## ⚡ WARSTWA 3: CZĘŚCI GENERATORA (Component Hooks)

### CZĘŚĆ 1: Budowa Modeli

```
┌─────────────────────────────────────────────┐
│  CZĘŚĆ 1: BUDOWA MODELI                       │
│  Odpowiedzialność: Tworzenie struktur modeli  │
├─────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────────┐      ┌──────────────────┐   │
│  │ MODEL_DEFINITION │─────▶│ MODEL_BUILDING   │   │
│  │ (Definicja       │      │ (Budowa          │   │
│  │  struktury)     │      │  sieci)          │   │
│  └────────┬─────────┘      └────────┬─────────┘   │
│            │                         │            │
│            ▼                         ▼            │
│  ┌──────────────────┐      ┌──────────────────┐   │
│  │ MODEL_TRAINING   │◀─────│ MODEL_COMPILE   │   │
│  │ (Trening         │      │ (Kompilacja      │   │
│  │  modelu)        │      │  modelu)         │   │
│  └────────┬─────────┘      └────────┬─────────┘   │
│            │                         │            │
│            ▼                         ▼            │
│  ┌──────────────────┐      ┌──────────────────┐   │
│  │ MODEL_SAVE       │◀─────│ MODEL_VALIDATE  │   │
│  │ (Zapis modelu:  │      │ (Walidacja      │   │
│  │  .h5, metadata, │      │  modelu)        │   │
│  │  klasy)         │      │                  │   │
│  └──────────────────┘      └──────────────────┘   │
│                                                  │
└─────────────────────────────────────────────┘
```

#### Hooki Czesci 1

| Hook | Typ | Lokalizacja | Opis | WORLD_CONTEXT | Zwracane |
|------|-----|-------------|------|---------------|-----------|
| **`SSI_MODEL_DEFINE_START`** | START | Poczatek definicji | Rozpoczecie definicji struktury | ✅ Wymagany | `model_config`, `features` |
| **`SSI_MODEL_DEFINE_END`** | END | Koniec definicji | Zakończenie definicji struktury | ✅ Wymagany | `model_definition`, `status` |
| **`SSI_MODEL_BUILD_START`** | START | Przed budowa | Rozpoczecie budowy sieci | ✅ Wymagany | `architecture`, `params` |
| **`SSI_MODEL_BUILD_END`** | END | Po budowie | Zakończenie budowy sieci | ✅ Wymagany | `model`, `summary` |
| **`SSI_MODEL_TRAIN_START`** | START | Przed treningiem | Rozpoczecie treningu | ✅ Wymagany | `training_config`, `data_info` |
| **`SSI_MODEL_TRAIN_EPOCH`** | PROGRESS | Po kazdej epoke | Postep treningu | ⚠️ Opcjonalny | `epoch`, `loss`, `accuracy` |
| **`SSI_MODEL_TRAIN_END`** | END | Po treningu | Zakończenie treningu | ✅ Wymagany | `final_metrics`, `model_performance` |
| **`SSI_MODEL_VALIDATE`** | VALIDATE | Przed zapisaniem | Walidacja modelu | ✅ Wymagany | `validation_report`, `is_valid` |
| **`SSI_MODEL_SAVE_START`** | START | Przed zapisaniem | Rozpoczecie zapisu | ✅ Wymagany | `save_path`, `format` |
| **`SSI_MODEL_SAVE_END`** | END | Po zapisie | Zakończenie zapisu | ✅ Wymagany | `saved_files`, `checksums` |

---

### CZĘŚĆ 2: Predykcja & Analiza Podstawowa

```
┌─────────────────────────────────────────────┐
│  CZĘŚĆ 2: PREDYKCJA & ANALIZA PODSTAWOWA    │
│  Odpowiedzialność: Ładowanie modeli,          │
│                   generowanie predykcji       │
├─────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────────┐      ┌──────────────────┐   │
│  │ MODEL_LOAD       │─────▶│ DATA_PREPARE     │   │
│  │ (Ladowanie       │      │ (Przygotowanie    │   │
│  │  modelu)        │      │  danych)          │   │
│  └────────┬─────────┘      └────────┬─────────┘   │
│            │                         │            │
│            ▼                         ▼            │
│  ┌──────────────────┐      ┌──────────────────┐   │
│  │ PREDICT_START    │◀─────│ DATA_VALIDATE    │   │
│  │ (Rozpoczecie      │      │ (Walidacja       │   │
│  │  predykcji)      │      │  danych)          │   │
│  └────────┬─────────┘      └──────────────────┘   │
│            │                              │            │
│            ▼                              ▼            │
│  ┌──────────────────┐      ┌──────────────────┐   │
│  │ PREDICT_EXECUTE  │─────▶│ ANALYZE_BASE     │   │
│  │ (Wykonywanie     │      │ (Analiza          │   │
│  │  predykcji)      │      │  podstawowa)      │   │
│  └────────┬─────────┘      └────────┬─────────┘   │
│            │                         │            │
│            ▼                         ▼            │
│  ┌──────────────────┐      ┌──────────────────┐   │
│  │ PREDICT_END      │◀─────│ RESULTS_AGGREGATE│   │
│  │ (Zakończenie     │      │ (Agregacja        │   │
│  │  predykcji)      │      │  wynikow)         │   │
│  └──────────────────┘      └──────────────────┘   │
│                                                  │
└─────────────────────────────────────────────┘
```

#### Hooki Czesci 2

| Hook | Typ | Lokalizacja | Opis | WORLD_CONTEXT | Zwracane |
|------|-----|-------------|------|---------------|-----------|
| **`SSI_MODEL_LOAD_START`** | START | Przed ladowaniem | Rozpoczecie ladowania modelu | ✅ Wymagany | `model_path`, `config` |
| **`SSI_MODEL_LOAD_END`** | END | Po ladowaniu | Zakończenie ladowania modelu | ✅ Wymagany | `model`, `metadata`, `classes` |
| **`SSI_DATA_LOAD_START`** | START | Przed ladowaniem danych | Rozpoczecie ladowania danych | ✅ Wymagany | `data_source`, `range` |
| **`SSI_DATA_LOAD_END`** | END | Po ladowaniu danych | Zakończenie ladowania danych | ✅ Wymagany | `data`, `statistics` |
| **`SSI_DATA_PREPARE_START`** | START | Przed preparacja | Rozpoczecie przygotowania danych | ✅ Wymagany | `preprocessing_steps` |
| **`SSI_DATA_PREPARE_END`** | END | Po preparacji | Zakończenie przygotowania | ✅ Wymagany | `prepared_data`, `features` |
| **`SSI_PREDICT_START`** | START | Przed predykcja | Rozpoczecie predykcji | ✅ Wymagany | `model`, `input_data`, `params` |
| **`SSI_PREDICT_BATCH_START`** | START | Przed predykcja wsadowa | Rozpoczecie predykcji wsadowej | ⚠️ Opcjonalny | `batch_size`, `total_items` |
| **`SSI_PREDICT_BATCH_PROGRESS`** | PROGRESS | W trakcie | Postep predykcji wsadowej | ⚠️ Opcjonalny | `processed`, `remaining`, `percentage` |
| **`SSI_PREDICT_END`** | END | Po predykcji | Zakończenie predykcji | ✅ Wymagany | `predictions`, `confidences`, `statistics` |
| **`SSI_ANALYZE_START`** | START | Przed analiza | Rozpoczecie analizy podstawowej | ✅ Wymagany | `analysis_type`, `data` |
| **`SSI_ANALYZE_END`** | END | Po analize | Zakończenie analizy | ✅ Wymagany | `analysis_results`, `insights` |

---

### CZĘŚĆ 3: Teacher Engine (Rdzeń Poznawczy)

```
┌─────────────────────────────────────────────┐
│  CZĘŚĆ 3: TEACHER ENGINE                     │
│  Odpowiedzialność: Generowanie wiedzy         │
│                   poznawczej                  │
├─────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────────┐      ┌──────────────────┐   │
│  │ WORLD_HIERARCHY  │─────▶│ DYNAMIC_WEIGHTS  │   │
│  │ (Hierarchia      │      │ (Dynamiczne      │   │
│  │  wiedzy)         │      │  wagowanie)       │   │
│  └────────┬─────────┘      └────────┬─────────┘   │
│            │                         │            │
│            ▼                         ▼            │
│  ┌──────────────────┐      ┌──────────────────┐   │
│  │ COGNITIVE_       │◀─────│ MEMORY_LOAD      │   │
│  │ TEACHER          │      │ (Ladowanie       │   │
│  │ (Nauczanie)      │      │  pamieci)        │   │
│  └────────┬─────────┘      └────────┬─────────┘   │
│            │                         │            │
│            ▼                         ▼            │
│  ┌──────────────────┐      ┌──────────────────┐   │
│  │ KNOWLEDGE_       │◀─────│ WORLD_OBSERVE   │   │
│  │ GENERATE         │      │ (Obserwacja      │   │
│  │ (Generowanie     │      │  swiata)         │   │
│  │  wiedzy)         │      │                  │   │
│  └────────┬─────────┘      └──────────────────┘   │
│            │                              │            │
│            ▼                              ▼            │
│  ┌──────────────────┐      ┌──────────────────┐   │
│  │ KNOWLEDGE_SAVE   │◀─────│ MEMORY_UPDATE    │   │
│  │ (Zapis wiedzy)   │      │ (Aktualizacja    │   │
│  └──────────────────┘      │  pamieci)         │   │
│                            └──────────────────┘   │
│                                                  │
└─────────────────────────────────────────────┘
```

#### Hooki Czesci 3

| Hook | Typ | Lokalizacja | Opis | WORLD_CONTEXT | Zwracane |
|------|-----|-------------|------|---------------|-----------|
| **`SSI_WORLD_HIERARCHY_LOAD`** | START | Ładowanie hierarchii | Rozpoczecie ladowania hierarchii wiedzy | ✅ Wymagany | `hierarchy_config`, `levels` |
| **`SSI_WORLD_HIERARCHY_END`** | END | Zakończenie hierarchii | Zakończenie ladowania hierarchii | ✅ Wymagany | `hierarchy`, `validation` |
| **`SSI_DYNAMIC_WEIGHTS_LOAD`** | START | Ładowanie wag | Rozpoczecie ladowania dynamicznych wag | ✅ Wymagany | `weights_config`, `features` |
| **`SSI_DYNAMIC_WEIGHTS_UPDATE`** | UPDATE | Aktualizacja wag | Aktualizacja dynamicznych wag | ⚠️ Opcjonalny | `old_weights`, `new_weights` |
| **`SSI_COGNITIVE_TEACHER_START`** | START | Rozpoczecie nauczania | Rozpoczecie pracy CognitiveTeacher | ✅ Wymagany | `teacher_config`, `strategy` |
| **`SSI_WORLD_OBSERVE_START`** | START | Rozpoczecie obserwacji | Rozpoczecie obserwacji świata | ✅ Wymagany | `observation_type`, `parameters` |
| **`SSI_WORLD_OBSERVE_END`** | END | Zakończenie obserwacji | Zakończenie obserwacji świata | ✅ Wymagany | `observations`, `patterns` |
| **`SSI_KNOWLEDGE_GENERATE_START`** | START | Rozpoczecie generowania | Rozpoczecie generowania wiedzy | ✅ Wymagany | `knowledge_type`, `sources` |
| **`SSI_KNOWLEDGE_GENERATE_END`** | END | Zakończenie generowania | Zakończenie generowania wiedzy | ✅ Wymagany | `knowledge`, `statistics`, `insights` |
| **`SSI_KNOWLEDGE_SAVE_START`** | START | Przed zapisaniem | Rozpoczecie zapisu wiedzy | ✅ Wymagany | `save_config`, `format` |
| **`SSI_KNOWLEDGE_SAVE_END`** | END | Po zapisie | Zakończenie zapisu wiedzy | ✅ Wymagany | `saved_files`, `knowledge_id` |
| **`SSI_MEMORY_UPDATE`** | UPDATE | Aktualizacja pamięci | Aktualizacja pamięci poznawczej | ⚠️ Opcjonalny | `memory_id`, `changes` |

---

### CZĘŚĆ 4: Laboratorium V2 (Analiza Operacyjna)

```
┌─────────────────────────────────────────────┐
│  CZĘŚĆ 4: LABORATORIUM V2                    │
│  Odpowiedzialność: Analiza operacyjna,       │
│                   pamięć obserwacji,           │
│                   kolektor wiedzy             │
├─────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────────┐      ┌──────────────────┐   │
│  │ OBSERVATION_     │─────▶│ TREND_           │   │
│  │ MEMORY_LOAD      │      │ ANALYSIS         │   │
│  │ (Ladowanie       │      │ (Analiza         │   │
│  │  obserwacji)    │      │  trendow)        │   │
│  └────────┬─────────┘      └────────┬─────────┘   │
│            │                         │            │
│            ▼                         ▼            │
│  ┌──────────────────┐      ┌──────────────────┐   │
│  │ CONFIDENCE_      │◀─────│ CLASS_           │   │
│  │ ANALYSIS         │      │ ANALYSIS         │   │
│  │ (Analiza         │      │ (Analiza         │   │
│  │  pewnosci)       │      │  klas)           │   │
│  └────────┬─────────┘      └────────┬─────────┘   │
│            │                         │            │
│            ▼                         ▼            │
│  ┌──────────────────┐      ┌──────────────────┐   │
│  │ DEVIATION_       │◀─────│ KNOWLEDGE_       │   │
│  │ ANALYSIS         │      │ COLLECTOR        │   │
│  │ (Analiza         │      │ (Kolektor        │   │
│  │  odchyleń)       │      │  wiedzy)         │   │
│  └────────┬─────────┘      └────────┬─────────┘   │
│            │                         │            │
│            ▼                         ▼            │
│  ┌──────────────────┐      ┌──────────────────┐   │
│  │ KNOWLEDGE_       │◀─────│ REPORT_GENERATE │   │
│  │ STORAGE_SAVE     │      │ (Generowanie     │   │
│  │ (Zapis wynikow) │      │  raportu)        │   │
│  └──────────────────┘      └──────────────────┘   │
│                                                  │
└─────────────────────────────────────────────┘
```

#### Hooki Czesci 4

| Hook | Typ | Lokalizacja | Opis | WORLD_CONTEXT | Zwracane |
|------|-----|-------------|------|---------------|-----------|
| **`SSI_OBSERVATION_MEMORY_LOAD`** | START | Ładowanie pamięci | Rozpoczecie ladowania pamięci obserwacji | ✅ Wymagany | `memory_type`, `range` |
| **`SSI_OBSERVATION_MEMORY_UPDATE`** | UPDATE | Aktualizacja pamięci | Aktualizacja pamięci obserwacji | ✅ Wymagany | `changes`, `statistics` |
| **`SSI_OBSERVATION_MEMORY_SAVE`** | END | Zapis pamięci | Zakończenie zapisu pamięci | ✅ Wymagany | `saved_location`, `size` |
| **`SSI_TREND_ANALYSIS_START`** | START | Rozpoczecie analizy | Rozpoczecie analizy trendow | ✅ Wymagany | `trend_type`, `parameters` |
| **`SSI_TREND_ANALYSIS_END`** | END | Zakończenie analizy | Zakończenie analizy trendow | ✅ Wymagany | `results`, `patterns`, `anomalies` |
| **`SSI_CONFIDENCE_ANALYSIS_START`** | START | Rozpoczecie analizy | Rozpoczecie analizy pewnosci | ✅ Wymagany | `method`, `bins` |
| **`SSI_CONFIDENCE_ANALYSIS_END`** | END | Zakończenie analizy | Zakończenie analizy pewnosci | ✅ Wymagany | `confidence_distribution`, `stats` |
| **`SSI_CLASS_ANALYSIS_START`** | START | Rozpoczecie analizy | Rozpoczecie analizy klas | ✅ Wymagany | `class_type`, `metrics` |
| **`SSI_CLASS_ANALYSIS_END`** | END | Zakończenie analizy | Zakończenie analizy klas | ✅ Wymagany | `class_performance`, `insights` |
| **`SSI_DEVIATION_ANALYSIS_START`** | START | Rozpoczecie analizy | Rozpoczecie analizy odchyleń | ✅ Wymagany | `comparison_method`, `threshold` |
| **`SSI_DEVIATION_ANALYSIS_END`** | END | Zakończenie analizy | Zakończenie analizy odchyleń | ✅ Wymagany | `deviations`, `reversed_patterns` |
| **`SSI_KNOWLEDGE_COLLECTOR_START`** | START | Rozpoczecie kolektora | Rozpoczecie agregacji wiedzy | ✅ Wymagany | `sources`, `aggregation_method` |
| **`SSI_KNOWLEDGE_COLLECTOR_END`** | END | Zakończenie kolektora | Zakończenie agregacji wiedzy | ✅ Wymagany | `collected_knowledge`, `summary` |
| **`SSI_KNOWLEDGE_STORAGE_SAVE`** | END | Zapis kolektora | Zakończenie zapisu kolektora | ✅ Wymagany | `files`, `knowledge_id` |

---

## 🎯 WARSTWA 4: AGENT (Użycie)

### Format Żądania Agenta (Abstrakcyjny)

```json
{
  "type": "ANALYZE_TREND|PREDICT|BUILD_MODEL|EVALUATE",
  "world": "football_odds|EUR_USD|SP500|GOLD",
  "time": "1h|1d|1w|1m|custom",
  "goal": "predict_direction|predict_result|analyze_trend|evaluate_performance",
  "parameters": {
    "model": "siec_08_log_koniec|siec_01_start_kursow|auto",
    "range": "latest|today|custom",
    "confidence_threshold": 0.7,
    "include_features": true,
    "aggregation": "none|daily|weekly"
  },
  "context": {
    "session_id": "UUID",
    "priority": "low|medium|high",
    "callback": "https://agent/callback"
  }
}
```

### Przykłady Żądań od Agenta

#### 🎯Predykcja Meczów Piłki Nożnej
```json
{
  "type": "PREDICT",
  "world": "football_odds",
  "time": "1d",
  "goal": "predict_result",
  "parameters": {
    "model": "siec_08_log_koniec",
    "range": "today",
    "confidence_threshold": 0.75,
    "match_ids": ["MECZ_001", "MECZ_002", "MECZ_003"]
  }
}
```

**Generator wybierze:**
- Część 2 (Predykcja)
- Model `siec_08_log_koniec`
- Dane z `dataBase_futbol_trend.csv`
- Wygeneruje predykcje z pewnością

---

#### 📈Analiza Trendu Walutowego
```json
{
  "type": "ANALYZE_TREND",
  "world": "EUR_USD",
  "time": "1h",
  "goal": "predict_direction",
  "parameters": {
    "trend_type": "price_movement",
    "min_confidence": 0.8,
    "include_volatility": true
  }
}
```

**Generator wybierze:**
- Część 4 (Laboratorium)
- Analizę trendów
- Dane z `fx_data` (przyszłe źródło)
- Wygeneruje trend z pewnością i zmiennością

---

#### 🏗️Budowa Nowego Modelu
```json
{
  "type": "BUILD_MODEL",
  "world": "football_odds",
  "time": "1m",
  "goal": "model_training",
  "parameters": {
    "model_name": "siec_12_new_strategy",
    "data_source": "dataBase_futbol_trend",
    "training_range": "2024-01-01_to_2026-08-01",
    "layers": [128, 64, 32],
    "epochs": 100
  }
}
```

**Generator wybierze:**
- Część 1 (Budowa Modeli)
- Utworzy nowy model `siec_12_new_strategy`
- Wytrenuje na danych historycznych
- Zapiszemy model i metadane

---

#### 🧠Generowanie Wiedzy Poznawczej
```json
{
  "type": "GENERATE_KNOWLEDGE",
  "world": "football_odds",
  "time": "1w",
  "goal": "cognitive_memory",
  "parameters": {
    "models": ["siec_08_log_koniec", "siec_09_ratio_start"],
    "depth": "deep",
    "include_errors": true
  }
}
```

**Generator wybierze:**
- Część 3 (Teacher Engine)
- CognitiveTeacher
- Wygeneruje `PAMIEC_MODEL_POZNAWCZY.json`
- Wygeneruje `WIEDZA_DLA_MODELU_DOCELOWEGO.json`

---

#### 📊Ocena Modelu
```json
{
  "type": "EVALUATE",
  "world": "football_odds",
  "time": "1m",
  "goal": "performance_analysis",
  "parameters": {
    "model": "siec_08_log_koniec",
    "test_range": "2026-01-01_to_2026-07-31",
    "metrics": ["accuracy", "precision", "recall", "f1"]
  }
}
```

**Generator wybierze:**
- Część 4 (Laboratorium)
- Analizę klas i pewności
- Wygeneruje `ocena.json` i `analiza_klas.json`

---

#### 🔄Zmiana Kontekstu Świata
```json
{
  "type": "SWITCH_WORLD",
  "world": "EUR_USD",
  "time": null,
  "goal": "change_context",
  "parameters": {
    "from": "football_odds",
    "persist_previous": false
  }
}
```

**Generator wybierze:**
- Zmieni WORLD_CONTEXT
- Załaduje nowy ekosystem
- Zresetuje pamięć tymczasową

---

## 🔄 Integracja z Kontraktem SSI_AGENT_INTERFACE

### Mapowanie Akcji Agent → Hooki Generatora

| Akcja (Contract) | Typ Żądania (Agent) | Hooki Generatora | Część |
|------------------|---------------------|------------------|-------|
| `ping` | SYSTEM | `SSI_GENERATOR_START`, `SSI_GENERATOR_READY` | Global |
| `status` | SYSTEM | `SSI_WORLD_LOAD`, `SSI_MODEL_LOAD_END` | Global |
| `build_model` | BUILD_MODEL | `SSI_MODEL_DEFINE_START`, `SSI_MODEL_BUILD_START`, `SSI_MODEL_TRAIN_START`, `SSI_MODEL_SAVE_START` | 1 |
| `train_model` | BUILD_MODEL | `SSI_MODEL_LOAD_START`, `SSI_MODEL_TRAIN_START` | 1, 2 |
| `load_model` | SYSTEM | `SSI_MODEL_LOAD_START` | 2 |
| `predict` | PREDICT | `SSI_MODEL_LOAD_START`, `SSI_PREDICT_START` | 2 |
| `predict_batch` | PREDICT | `SSI_PREDICT_BATCH_START` | 2 |
| `get_prediction_history` | PREDICT | `SSI_PREDICT_START` (historyczny) | 2 |
| `generate_knowledge` | GENERATE_KNOWLEDGE | `SSI_KNOWLEDGE_GENERATE_START` | 3 |
| `get_cognitive_memory` | GENERATE_KNOWLEDGE | `SSI_WORLD_HIERARCHY_LOAD`, `SSI_COGNITIVE_TEACHER_START` | 3 |
| `update_teacher_engine` | SYSTEM | `SSI_DYNAMIC_WEIGHTS_UPDATE` | 3 |
| `analyze_trends` | ANALYZE_TREND | `SSI_TREND_ANALYSIS_START` | 4 |
| `get_knowledge_collector` | ANALYZE_TREND | `SSI_KNOWLEDGE_COLLECTOR_START` | 4 |
| `get_observation_memory` | PREDICT | `SSI_OBSERVATION_MEMORY_LOAD` | 4 |
| `evaluate_model` | EVALUATE | `SSI_CLASS_ANALYSIS_START`, `SSI_CONFIDENCE_ANALYSIS_START` | 4 |
| `list_ecosystems` | SYSTEM | `SSI_WORLD_LOAD` (lista) | Global |
| `get_ecosystem_status` | SYSTEM | `SSI_WORLD_SELECT` (status) | Global |
| `switch_ecosystem` | SWITCH_WORLD | `SSI_WORLD_SWITCH` | Global |

---

## 📁 UNIWERSALNE TYPY WYJŚĆ (Abstrakcyjne)

### Typy Wyników (Output Types)

| Typ | Opis | Strukturka | Użycie |
|-----|------|------------|--------|
| **`trend`** | Kierunek trendu | `{direction: +1/-1/0, strength: 0.0-1.0}` | Waluty, Giełda, Surowce |
| **`probability`** | Prawdopodobieństwo | `{class: string, probability: 0.0-1.0}` | Piłka, Hokej |
| **`direction`** | Kierunek (prosty) | `+1` (wzrost), `-1` (spadek), `0` (stabilność) | Waluty, Giełda |
| **`magnitude`** | Siła zmienności | `0.0-1.0` (niska-wysoka) | Waluty, Surowce |
| **`confidence`** | Pewność modelu | `0.0-1.0` | Wszystkie |
| **`stability`** | Stabilność trendu | `0.0-1.0` (niestabilny-stabilny) | Giełda |
| **`volatility`** | Zmienność | `0.0-1.0` (niska-wysoka) | Waluty, Surowce |
| **`time_frame`** | Ramy czasowe | `{start: ISO8601, end: ISO8601, duration: string}` | Wszystkie |

### Przykładowe Wyniki

#### Piłka Nożna
```json
{
  "type": "probability",
  "value": {
    "match_id": "MECZ_001",
    "result": "1",
    "probability": 0.85,
    "confidence": 0.92,
    "trend": {"direction": 0, "strength": 0.0},
    "time_frame": {"duration": "PT90M"}
  }
}
```

#### Waluty
```json
{
  "type": "trend",
  "value": {
    "pair": "EUR_USD",
    "direction": +1,
    "strength": 0.75,
    "confidence": 0.88,
    "magnitude": 0.65,
    "volatility": 0.45,
    "time_frame": {"duration": "PT1H"}
  }
}
```

#### Giełda
```json
{
  "type": "stability",
  "value": {
    "index": "SP500",
    "direction": -1,
    "stability": 0.35,
    "confidence": 0.82,
    "volatility": 0.78,
    "time_frame": {"duration": "P1D"}
  }
}
```

---

## 🔧 IMPLEMENTACJA (PRZYSZŁOŚĆ - ETAP C)

### Kroki Implementacji

1. **Stworzyć SSI_INPUT_GATE**
   - Walidacja SSI_AGENT_INPUT
   - Konwersja na WORLD_CONTEXT
   - Routing do odpowiednich części

2. **Stworzyć SSI_OUTPUT_GATE**
   - Formatowanie odpowiedzi
   - Konwersja z WORLD_CONTEXT
   - Walidacja SSI_AGENT_OUTPUT

3. **Dodać Hooki do Części 1-4**
   - Zgodnie z mapą powyżej
   - Z aktualnym WORLD_CONTEXT
   - Z logowaniem i audytem

4. **Zintegrować z Agentami**
   - Testy komunikacji
   - Walidacja kontraktu
   - Obsługa błędów

### Przykład Implementacji Hooka (Pseudokod)

```python
# W SSI_INPUT_GATE

def SSI_GENERATOR_START(context: WORLD_CONTEXT) -> dict:
    """
    hook wywoływany na początku operacji generatora
    """
    log_hook_call("SSI_GENERATOR_START", context)
    
    # Inicjalizacja
    init_generator()
    init_world_context(context)
    
    # Powiadomienie
    notify_agents({
        "event_type": "SSI_NOTIFICATION",
        "notification": "GENERATOR_STARTED",
        "world": context.world_id
    })
    
    return {
        "status": "started",
        "timestamp": datetime.utcnow().isoformat(),
        "context_id": context.context_id
    }


# W CZĘŚĆ 2 (czesc2.py)

def SSI_PREDICT_START(context: WORLD_CONTEXT, data: dict) -> dict:
    """
    hook wywoływany przed predykcją
    """
    log_hook_call("SSI_PREDICT_START", context)
    
    # Walidacja
    validate_world_context(context)
    validate_prediction_data(data)
    
    # Ładowanie modelu
    model = load_model(context.world_id, data.get("model"))
    
    # Przygotowanie danych
    prepared_data = prepare_data(data.get("input"), context)
    
    return {
        "status": "ready",
        "model": model.info,
        "data": prepared_data.info
    }
```

---

## ✅ PODSUMOWANIE

### Co Zostało Zdefiniowane w ETAP B2

✅ **Warstwa 1 - Sterowanie**: Globalne hooki kontrolne (START, STOP, READY, etc.)  
✅ **Warstwa 2 - Kontekst Świata**: WORLD_CONTEXT z uniwersalnymi polami  
✅ **Warstwa 3 - Części Generatora**: Hooki dla Części 1-4 (25+ hooków)  
✅ **Warstwa 4 - Agent**: Abstrakcyjne żądania i wyniki  
✅ **Mapowanie Kontraktów**: Powiązanie z SSI_AGENT_INTERFACE  
✅ **Uniwersalność**: Gotowość na waluty, giełdę, surowce, hokej  
✅ **Abstrakcja Wyników**:Uniwersalne typy wyjściowe (trend, probability, etc.)  

### Kluczowe Zasady

1. **Agent NIGDY nie wie** której części używa - zdecyduje Generator
2. **Wszystko przechodzi przez WORLD_CONTEXT** - uniwersalny kontekst
3. **Hooki sa zagnieżdżone** - globalne → świat → część → operacja
4. **Uniwersalność** - ta sama架构 dla sportu, walut, giełdy
5. ** Rozszerzalność** - nowe światy dodawane bez zmiany kodu

---

## 🎯 CO DALEJ (ETAP B3)

Po zatwierdzeniu tej mapy:

1. **ETAP B3**: Zaimplementować SSI_INPUT_GATE i SSI_OUTPUT_GATE
2. **ETAP C1**: Dodać hooki do czesc1-4.py (tylko flagi, nie logika)
3. **ETAP C2**: Zintegrować z agentami (testy)
4. **ETAP D**: Dodawać nowe światy (waluty, giełda)

---

## 📊 PODSUMOWANIE ARCHITEKTURY

```
┌─────────────────────────────────────────────────────────────────┐
│  SSI V5 WORLD TREND ANALYSIS ENGINE (Uniwersalny)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ╔════════════════════════════════════════════════════════════╗  │
│  ║                    WARSTWA INTERFEJSU                        ║  │
│  ║  Agent ↔ SSI_INPUT_GATE ↔ Generator ↔ SSI_OUTPUT_GATE     ║  │
│  ╚════════════════════════════════════════════════════════════╝  │
│                                                                  │
│  ╔════════════════════════════════════════════════════════════╗  │
│  ║                    WARSTWA KONTEKSTU                         ║  │
│  ║  WORLD_CONTEXT: world_id, domain, source, output_type      ║  │
│  ║  Obsługuje: sports, financial_market, commodities           ║  │
│  ╚════════════════════════════════════════════════════════════╝  │
│                                                                  │
│  ╔════════════════════════════════════════════════════════════╗  │
│  ║                    WARSTWA GENERATORA                        ║  │
│  ║  CZĘŚĆ 1: Budowa Modeli (20+ modeli)                         ║  │
│  ║  CZĘŚĆ 2: Predykcja & Analiza (4 ekosystemy)               ║  │
│  ║  CZĘŚĆ 3: Teacher Engine & Wiedza Poznawcza                ║  │
│  ║  CZĘŚĆ 4: Laboratorium V2 & Kolektor Wiedzy                  ║  │
│  ╚════════════════════════════════════════════════════════════╝  │
│                                                                  │
│  ╔════════════════════════════════════════════════════════════╗  │
│  ║                    WARSTWA DANYCH                            ║  │
│  ║  SPORTS: football_odds, hockey_odds                          ║  │
│  ║  FINANCIAL: EUR_USD, SP500, NASDAQ, GOLD                      ║  │
│  ║  (Rozszerzalne - nowe światy dodawane dynamicznie)          ║  │
│  ╚════════════════════════════════════════════════════════════╝  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📝 HISTORIA DOKUMENTU

| Data | Wersja | Autor | Opis |
|------|--------|-------|------|
| 2026-08-03 | 1.0 | Mistral Vibe | ETAP B2: Uniwersalna mapa hooków dla World Trend Analysis Engine |

---

**Status:** Oczekuje na zatwierdzenie (ETAP B2)  
**Nastepny krok:** ETAP B3 (Implementacja SSI_INPUT_GATE/SSI_OUTPUT_GATE) po zatwierdzeniu
