# SSI V5 - MAPA MODUŁÓW V2/V3/V4

**Data:** 2026-08-01  
**Sprint:** 11.5 (Działający)  
**Status:** Dokumentacja projektowa - Wersja 1.0.0  
**Autor:** Główny Architekt SSI V5  

---

## 📋 SPIS TREŚCI

1. [Lokalizacja i struktura modułów V2/V3/V4](#1-lokalizacja-i-struktura-modułów-v2v3v4)
2. [Szczegółowe Belle Modułów](#2-szczegółowe-belle-modułów)
3. [Formaty Danych Wyjściowych](#3-formaty-danych-wyjściowych)
4. [Unified Input Package](#4-unified-input-package)
5. [Integracja z Systemem](#5-integracja-z-systemem)

---

## 1. LOKALIZACJA I STRUKTURA MODUŁÓW V2/V3/V4

### 1.1. Struktura Katalogów

```
SSI/
└── v5/
    └── input_layer/
        ├── collector_manager.py    # 🟢 Manager wszystkich collectorów
        ├── v2_collector.py         # 🟢 V2 World Data Collector
        ├── v3_collector.py         # 🟢 V3 Knowledge Collector
        ├── v4_collector.py         # 🟢 V4 Agents Data Collector
        └── external/
            └── external.py         # 🟢 External Data Collector
```

### 1.2. Podsumowanie Modułów

| **Moduł** | **Plik** | **Lokalizacja** | **Status** |
|-----------|----------|----------------|------------|
| V2Collector | v2_collector.py | SSI/v5/input_layer/ | ✅ Sprint 11.5 |
| V3Collector | v3_collector.py | SSI/v5/input_layer/ | ✅ Sprint 11.5 |
| V4Collector | v4_collector.py | SSI/v5/input_layer/ | ✅ Sprint 11.5 |
| External | external.py | SSI/v5/input_layer/external/ | ✅ Sprint 11.5 |
| CollectorManager | collector_manager.py | SSI/v5/input_layer/ | ✅ Sprint 11.5 |

---

## 2. SZCZEGÓŁOWE BELLE MODUŁÓW

### 2.1. V2Collector (World Data Collector)

| **Atrybut** | **Wartość** |
|-------------|------------|
| **Odpowiedzialność** | Zbieranie danych światowych |
| **Lokalizacja** | SSI/v5/input_layer/v2_collector.py |
| **Dane wyjściowe** | world_state, events[], timestamp |
| **Częstotliwość** | Co cykl |
| **Status** | ✅ Sprint 11.5 |

**Opis funkcjonalności:**
- Zbieranie aktualnego stanu świata (warunki rynkowe, trendy, anomalie)
- Monitorowanie zdarzeń światowych
-generowanie timestampów dla synchronizacji

**Metody:**
```python
# v2_collector.py
def get_latest_data() -> dict:
    """Pobiera najnowsze dane światowe"""
    return {
        "world_state": {...},
        "events": [...],
        "timestamp": "..."
    }

def refresh_data() -> None:
    """Odświeża dane ze źródeł"""
    pass
```

### 2.2. V3Collector (Knowledge Collector)

| **Atrybut** | **Wartość** |
|-------------|------------|
| **Odpowiedzialność** | Zbieranie wiedzy |
| **Lokalizacja** | SSI/v5/input_layer/v3_collector.py |
| **Dane wyjściowe** | knowledge_base, insights[], timestamp |
| **Częstotliwość** | Co cykl |
| **Status** | ✅ Sprint 11.5 |

**Opis funkcjonalności:**
- Agregacja wiedzy z różnych domen (sport, finanse, technologia)
- Generowanie insightów na podstawie zebranej wiedzy
- Indeksowanie i kategoryzacja wiedzy

**Metody:**
```python
# v3_collector.py
def get_latest_data() -> dict:
    """Pobiera najnowszą bazę wiedzy"""
    return {
        "knowledge_base": {...},
        "insights": [...],
        "timestamp": "..."
    }

def add_insight(insight: dict) -> None:
    """Dodaje nowy insight do bazy wiedzy"""
    pass
```

### 2.3. V4Collector (Agents Data Collector)

| **Atrybut** | **Wartość** |
|-------------|------------|
| **Odpowiedzialność** | Zbieranie danych o agentach |
| **Lokalizacja** | SSI/v5/input_layer/v4_collector.py |
| **Dane wyjściowe** | agents_data, relationships, timestamp |
| **Częstotliwość** | Co cykl |
| **Status** | ✅ Sprint 11.5 |

**Opis funkcjonalności:**
- Monitorowanie stanu wszystkich agentów
- Zbieranie informacji o relacjach między agentami
- Śledzenie statystyk wydajności agentów

**Metody:**
```python
# v4_collector.py
def get_latest_data() -> dict:
    """Pobiera dane o wszystkich agentach"""
    return {
        "agents_data": {...},
        "relationships": {...},
        "timestamp": "..."
    }

def update_agent_stats(agent_id: str, stats: dict) -> None:
    """Aktualizuje statystyki agenta"""
    pass
```

### 2.4. ExternalCollector

| **Atrybut** | **Wartość** |
|-------------|------------|
| **Odpowiedzialność** | Zbieranie danych zewnętrznych |
| **Lokalizacja** | SSI/v5/input_layer/external/external.py |
| **Dane wyjściowe** | external_inputs, market_data, timestamp |
| **Częstotliwość** | Co cykl |
| **Status** | ✅ Sprint 11.5 |

**Opis funkcjonalności:**
- Pobieranie danych z zewnętrznych API
- Monitorowanie rynku (ceny, wolumen, sentyment)
- Integracja z dodatkowymi źródłami danych

**Metody:**
```python
# external.py
def get_latest_data() -> dict:
    """Pobiera zewnętrzne dane"""
    return {
        "external_inputs": {...},
        "market_data": {...},
        "timestamp": "..."
    }

def fetch_api_data(url: str, params: dict = None) -> dict:
    """Pobiera dane z zewnętrznego API"""
    pass
```

### 2.5. CollectorManager

| **Atrybut** | **Wartość** |
|-------------|------------|
| **Odpowiedzialność** | Zarządzanie collectorami |
| **Lokalizacja** | SSI/v5/input_layer/collector_manager.py |
| **Dane wyjściowe** | UnifiedInputPackage |
| **Częstotliwość** | Co cykl |
| **Status** | ✅ Sprint 11.5 |

**Opis funkcjonalności:**
- Inicjalizacja i zarządzanie wszystkimi collectorami
- Tworzenie zunifikowanego pakietu danych
- Walidacja zebranych danych
- Monitorowanie stanu collectorów

**Metody:**
```python
# collector_manager.py
def __init__(self):
    """Inicjalizuje wszystkie collectory"""
    self.collectors = {
        "v2": V2Collector(),
        "v3": V3Collector(),
        "v4": V4Collector(),
        "external": ExternalCollector()
    }

def get_latest_data(self) -> dict:
    """Pobiera najnowsze dane ze wszystkich collectorów"""
    return {name: collector.get_latest_data() 
            for name, collector in self.collectors.items()}

def get_collector(self, collector_type: str):
    """Zwraca konkretny collector"""
    return self.collectors.get(collector_type)

def validate_packages(self) -> dict:
    """Walibuje zebrane dane"""
    return {"v2": True, "v3": True, "v4": True, "external": True}
```

---

## 3. FORMATY DANYCH WYJŚCIOWYCH

### 3.1. V2 Data (World)

**Plik:** v2_collector.py  
**Format:** dict  
**Zawartość:**

```json
{
  "collector_type": "V2",
  "data_type": "world_state",
  "timestamp": "2026-08-01T00:00:00",
  "cycle_count": 5,
  "world_state": {
    "market_conditions": "stable",
    "volatility_index": 0.45,
    "market_trend": "bullish",
    "trends": ["trend_1", "trend_2", "trend_3"],
    "anomalies": [
      {
        "anomaly_id": "anom_001",
        "type": "price_spike",
        "severity": 0.85,
        "description": "Nagły wzrost cen aktywa X"
      }
    ]
  },
  "events": [
    {
      "event_id": "evt_001",
      "event_type": "market_change",
      "category": "financial",
      "description": "Zmiana warunków rynkowych",
      "impact_score": 0.75,
      "timestamp": "2026-08-01T00:00:00",
      "source": "V2"
    },
    {
      "event_id": "evt_002", 
      "event_type": "news_event",
      "category": "political",
      "description": "Ogłoszenie polityczne wpływające na rynek",
      "impact_score": 0.65,
      "timestamp": "2026-08-01T00:00:00",
      "source": "V2"
    }
  ],
  "metadata": {
    "data_quality": 0.92,
    "confidence": 0.88,
    "sources_count": 5,
    "last_updated": "2026-08-01T00:00:00"
  }
}
```

**Pola:**
- `collector_type`: Typ collectora (V2)
- `data_type`: Typ danych (world_state)
- `timestamp`: Data i godzina zebrania
- `world_state`: Główny stan świata
- `events`: Lista zdarzeń
- `metadata`: Metadane o jakości danych

### 3.2. V3 Data (Knowledge)

**Plik:** v3_collector.py  
**Format:** dict  
**Zawartość:**

```json
{
  "collector_type": "V3",
  "data_type": "knowledge_base",
  "timestamp": "2026-08-01T00:00:00",
  "cycle_count": 5,
  "knowledge_base": {
    "domains": ["sports", "finance", "technology", "politics"],
    "categories": {
      "sports": {"count": 45, "last_updated": "2026-08-01T00:00:00"},
      "finance": {"count": 38, "last_updated": "2026-08-01T00:00:00"},
      "technology": {"count": 22, "last_updated": "2026-08-01T00:00:00"}
    },
    "insights_count": 105,
    "knowledge_score": 0.87,
    "last_update": "2026-08-01T00:00:00",
    "sources": ["source_1", "source_2", "source_3"]
  },
  "insights": [
    {
      "insight_id": "ins_001",
      "domain": "sports",
      "category": "football",
      "title": "Analiza statystyczna meczy piłkarskich",
      "content": "Na podstawie ostatnich 100 meczy, team A wygrywa 65% spotkań u siebie",
      "confidence": 0.88,
      "quality_score": 0.92,
      "sources": ["statistics_db", "expert_opinion"],
      "timestamp": "2026-08-01T00:00:00",
      "expiry_date": "2026-08-08T00:00:00"
    },
    {
      "insight_id": "ins_002",
      "domain": "finance", 
      "category": "stock_market",
      "title": "Trend wzrostowy dla sektora technologicznego",
      "content": "Sektor technologiczny notuje średni wzrost 2.3% tygodniowo",
      "confidence": 0.75,
      "quality_score": 0.81,
      "sources": ["market_data", "analyst_reports"],
      "timestamp": "2026-08-01T00:00:00",
      "expiry_date": "2026-08-03T00:00:00"
    }
  ],
  "metadata": {
    "data_quality": 0.90,
    "confidence": 0.85,
    "completeness": 0.88,
    "last_updated": "2026-08-01T00:00:00"
  }
}
```

**Pola:**
- `collector_type`: Typ collectora (V3)
- `data_type`: Typ danych (knowledge_base)
- `knowledge_base`: Podstawowa baza wiedzy
- `insights`: Lista insightów/wglądów
- `metadata`: Metadane jakości

### 3.3. V4 Data (Agents)

**Plik:** v4_collector.py  
**Format:** dict  
**Zawartość:**

```json
{
  "collector_type": "V4",
  "data_type": "agents_data",
  "timestamp": "2026-08-01T00:00:00",
  "cycle_count": 5,
  "agents_data": {
    "total_agents": 6,
    "active_agents": ["01", "02", "03", "04", "05", "06"],
    "inactive_agents": [],
    "performance_metrics": {
      "average_confidence": 0.82,
      "decision_success_rate": 0.85,
      "average_execution_time_ms": 45,
      "total_decisions": 30,
      "successful_decisions": 25,
      "failed_decisions": 5
    },
    "agent_types": {
      "ANALYTICAL": ["01"],
      "CREATIVE": ["02"],
      "CONSERVATIVE": ["03"],
      "RISK_TAKER": ["04"],
      "BALANCED": ["05"],
      "EXPLORER": ["06"]
    }
  },
  "relationships": {
    "01": {
      "agent_id": "01",
      "agent_type": "ANALYTICAL",
      "allies": ["02", "05"],
      "conflicts": ["04"],
      "collaboration_score": 0.78,
      "communication_frequency": "high"
    },
    "02": {
      "agent_id": "02",
      "agent_type": "CREATIVE", 
      "allies": ["01", "03", "05"],
      "conflicts": [],
      "collaboration_score": 0.85,
      "communication_frequency": "very_high"
    },
    "03": {
      "agent_id": "03",
      "agent_type": "CONSERVATIVE",
      "allies": ["02", "05"],
      "conflicts": ["04"],
      "collaboration_score": 0.65,
      "communication_frequency": "medium"
    },
    "04": {
      "agent_id": "04",
      "agent_type": "RISK_TAKER",
      "allies": ["06"],
      "conflicts": ["01", "03"],
      "collaboration_score": 0.55,
      "communication_frequency": "low"
    },
    "05": {
      "agent_id": "05", 
      "agent_type": "BALANCED",
      "allies": ["01", "02", "03", "06"],
      "conflicts": [],
      "collaboration_score": 0.92,
      "communication_frequency": "very_high"
    },
    "06": {
      "agent_id": "06",
      "agent_type": "EXPLORER",
      "allies": ["04", "05"],
      "conflicts": [],
      "collaboration_score": 0.72,
      "communication_frequency": "medium"
    }
  },
  "metadata": {
    "data_quality": 0.95,
    "confidence": 0.90,
    "last_updated": "2026-08-01T00:00:00"
  }
}
```

**Pola:**
- `collector_type`: Typ collectora (V4)
- `data_type`: Typ danych (agents_data)
- `agents_data`: Dane o wszystkich agentach
- `relationships`: Relacje między agentami
- `metadata`: Metadane jakości

### 3.4. External Data

**Plik:** external.py  
**Format:** dict  
**Zawartość:**

```json
{
  "collector_type": "EXTERNAL",
  "data_type": "external_inputs",
  "timestamp": "2026-08-01T00:00:00",
  "cycle_count": 5,
  "external_inputs": {
    "api_calls_made": 15,
    "api_calls_successful": 14,
    "api_calls_failed": 1,
    "data_sources": [
      {
        "source_id": "api_1",
        "source_name": "Financial Data API",
        "type": "REST",
        "status": "active",
        "data_quality": 0.90,
        "last_call": "2026-08-01T00:00:00"
      },
      {
        "source_id": "api_2",
        "source_name": "Sports Statistics",
        "type": "GraphQL", 
        "status": "active",
        "data_quality": 0.85,
        "last_call": "2026-08-01T00:00:00"
      },
      {
        "source_id": "web_scraping",
        "source_name": "News Aggregator",
        "type": "HTML",
        "status": "active",
        "data_quality": 0.78,
        "last_call": "2026-08-01T00:00:00"
      }
    ],
    "web_scraping": {
      "pages_scraped": 8,
      "successful": 7,
      "failed": 1
    }
  },
  "market_data": {
    "currencies": {
      "USD/PLN": {"rate": 4.25, "change_24h": 0.012, "volatility": 0.35},
      "EUR/PLN": {"rate": 4.56, "change_24h": -0.008, "volatility": 0.28},
      "GBP/PLN": {"rate": 5.12, "change_24h": 0.021, "volatility": 0.42}
    },
    "stock_indices": {
      "WIG20": {"value": 2456.78, "change": 45.23, "change_pct": 1.88},
      "mWIG40": {"value": 3892.45, "change": 32.67, "change_pct": 0.85},
      "sWIG80": {"value": 12345.67, "change": 89.34, "change_pct": 0.73}
    },
    "volume": {
      "total": 12345678,
      "buy": 6789012,
      "sell": 5556666
    },
    "sentiment": {
      "overall": "positive",
      "positive": 55,
      "neutral": 30,
      "negative": 15,
      "score": 0.65
    }
  },
  "metadata": {
    "data_quality": 0.85,
    "confidence": 0.80,
    "sources_active": 3,
    "sources_total": 5,
    "last_updated": "2026-08-01T00:00:00"
  }
}
```

**Pola:**
- `collector_type`: Typ collectora (EXTERNAL)
- `data_type`: Typ danych (external_inputs)
- `external_inputs`: Informacje o źródłach zewnętrznych
- `market_data`: Dane rynkowe
- `metadata`: Metadane jakości

---

## 4. UNIFIED INPUT PACKAGE

### 4.1. Strukturą Pakietu

**Tworzony przez:** `CollectorManager._create_unified_input_package()`  
**Lokalizacja:** collector_manager.py:432  
**Format:** dict

```json
{
  "package_id": "unified_001_20260801000000",
  "timestamp": "2026-08-01T00:00:00",
  "cycle_count": 5,
  "v2": {
    "collector_type": "V2",
    "data_type": "world_state",
    "timestamp": "2026-08-01T00:00:00",
    "world_state": {...},
    "events": [...],
    "metadata": {...}
  },
  "v3": {
    "collector_type": "V3", 
    "data_type": "knowledge_base",
    "timestamp": "2026-08-01T00:00:00",
    "knowledge_base": {...},
    "insights": [...],
    "metadata": {...}
  },
  "v4": {
    "collector_type": "V4",
    "data_type": "agents_data",
    "timestamp": "2026-08-01T00:00:00",
    "agents_data": {...},
    "relationships": {...},
    "metadata": {...}
  },
  "external": {
    "collector_type": "EXTERNAL",
    "data_type": "external_inputs",
    "timestamp": "2026-08-01T00:00:00", 
    "external_inputs": {...},
    "market_data": {...},
    "metadata": {...}
  },
  "metadata": {
    "package_version": "1.0",
    "created_by": "collector_manager",
    "created_at": "2026-08-01T00:00:00",
    "validation_status": "valid",
    "validation_errors": [],
    "data_quality_scores": {
      "v2": 0.95,
      "v3": 0.90,
      "v4": 0.92,
      "external": 0.85
    },
    "overall_quality": 0.91
  }
}
```

### 4.2. Proces Tworzenia Pakietu

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PROCES TWORZENIA UNIFIED INPUT Package                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CollectorManager._create_unified_input_package()                           │
│    │                                                                         │
│    ├── 1. ZBIERANIE DANYCH OD COLLECTORÓW                                    │
│    │     ├─ v2_data = v2_collector.get_latest_data()                       │
│    │     ├─ v3_data = v3_collector.get_latest_data()                       │
│    │     ├─ v4_data = v4_collector.get_latest_data()                       │
│    │     └─ external_data = external_collector.get_latest_data()         │
│    │                                                                         │
│    ├── 2. WALIDACJA DANYCH                                                   │
│    │     └─ validate_packages() -> sprawdzenie poprawności danych        │
│    │                                                                         │
│    ├── 3. TWORZENIE PAKIETU                                                 │
│    │     ├─ package_id = generate_id()                                      │
│    │     ├─ timestamp = current_time()                                     │
│    │     └─ metadata = create_metadata()                                    │
│    │                                                                         │
│    └── 4. ZWRACANIE PAKIETU                                                  │
│        └─ return {v2, v3, v4, external, metadata}                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. INTEGRACJA Z SYSTEMEM

### 5.1. Diagram Integracji

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INTEGRACJA V2/V3/V4 Z RUNTIME                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  RuntimeController.run_loop()                                             │
│    └─ _collect_current_data() -> collector_manager.get_current_data()    │
│           └─ collector_manager.get_latest_data()                          │
│               ├─ v2_collector.get_latest_data() -> V2 Data               │
│               ├─ v3_collector.get_latest_data() -> V3 Data               │
│               ├─ v4_collector.get_latest_data() -> V4 Data               │
│               └─ external_collector.get_latest_data() -> External Data    │
│                                                                             │
│  CollectorManager:                                                         │
│    ├─ _create_unified_input_package() -> UnifiedInputPackage              │
│    ├─ validate_packages() -> ValidationResult                               │
│    └─ get_collector(collector_type) -> CollectorInstance                    │
│                                                                             │
│  Agenci używają:                                                           │
│    agent.run_cycle(collector_data, world_context, cycle_count)             │
│    └─ _analyze_data(collector_data) -> analysis                           │
│        └─ collector_data["v2"], collector_data["v3"], ...             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2. Tabela Integracji

| **Moduł Źródłowy** | **Dane** | **Moduł Docelowy** | **Użycie** | **Częstotliwość** |
|---------------------|----------|---------------------|------------|-------------------|
| V2Collector | world_state, events | AgentRuntime | Analiza danych światowych | Co cykl |
| V3Collector | knowledge_base, insights | AgentRuntime | Analiza wiedzy | Co cykl |
| V4Collector | agents_data, relationships | AgentRuntime | Analiza stanu agentów | Co cykl |
| External | external_inputs, market_data | AgentRuntime | Analiza danych zewnętrznych | Co cykl |
| CollectorManager | UnifiedInputPackage | RuntimeController | Dystrybucja do agentów | Co cykl |

### 5.3. Zależności

```
┌──────────────────────────────────┐
│        V2/V3/V4/EXTERNAL          │
│      (Input Layer Collectors)     │
└─────────────────┬────────────────┘
                  │
                  ▼
┌──────────────────────────────────┐
│       CollectorManager           │
│   (Zarządzanie i agregacja)        │
└─────────────────┬────────────────┘
                  │
                  ▼
┌──────────────────────────────────┐
│      RuntimeController            │
│   (_collect_current_data)         │
└─────────────────┬────────────────┘
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
┌───────────┐ ┌─────────┐ ┌─────────┐
│ Agent 01  │ │ Agent 02 │ │ Agent 03 │
│ Agent 04  │ │ Agent 05 │ │ Agent 06 │
└───────────┘ └─────────┘ └─────────┘
```

---

**Data utworzenia:** 2026-08-01  
**Wersja:** 1.0.0  
**Status:** Gotowy do przeglądu