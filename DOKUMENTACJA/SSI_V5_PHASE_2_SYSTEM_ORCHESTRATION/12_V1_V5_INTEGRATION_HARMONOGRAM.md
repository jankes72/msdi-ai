# SSI V5 PHASE 2: V1 ↔ V5 INTEGRATION & HARMONOGRAM

**Sprint:** 12+ (Phase 2 Foundation)  
**Data:** 2026-08-01  
**Wersja:** 1.0.0  
**Status:** COMPLETED (Architecture Audit)  
**Autor:** Mistral Vibe (Architecture Synchronization Engine)  

---

## 🎯 CEL DOKUMENTU

Ten dokument opisuje **kluczową zasadę integracji** między V1 (Data Collection Layer) a V5 (SSI Core). Dokumentuje:

1. **Harmonogram V1 → V5** - dokładne czasy i sekwencje zdarzeń
2. **Zasadę V1 jako START CONTROLLER** - V1 inicjuje V5, V5 nie uruchamia się sam
3. **System Runtime Awareness** - świadomość stanu systemu (system_state.json)
4. **Komunikację międzywarstwową** - jak V1 i V5 się komunikują

**🔴 WAŻNE:** To **zmiana paradugmatu** - V5 nie jest autonomiczny, wymaga sygnału z V1.

---

## 📋 SPIS TREŚCI

1. [V1 jako START CONTROLLER](#1-v1-jako-start-controller)
2. [Harmonogram V1 → V5](#2-harmonogram-v1--v5)
3. [System Runtime Awareness](#3-system-runtime-awareness)
4. [Komunikacja V1 ↔ V5](#4-komunikacja-v1--v5)
5. [Zależnoć Czasowa](#5-zależnoć-czasowa)
6. [Procedury Awaryjne](#6-procedury-awaryjne)

---

## 1. V1 JAKO START CONTROLLER

### 1.1 Zasada Działania

**🎯 FUNDAMENTAL RULE:**

```
V1 SCHEDULER
     │
     ▼
START EVENT
     │
     ▼
SSI V5 ACTIVATION
```

**V5 NIE URUCHAMIA SIĘ SAMODZIELNIE.**

### 1.2 Powody tej Zmiany

| **Problem** | **Rozwiązanie** | **Korzyści** |
|-------------|-----------------|--------------|
| Brak kontroli nad startem V5 | V1 decyduje kiedy V5 może wystartować | Lepsza synchronizacja |
| Rozłączenie V1 i V5 | V1 dba o dane, V5 o analizę | Czysty podział odpowiedzialności |
| Ryzyko uruchomienia V5 na nieaktualnych danych | V1 czeka aż dane będą gotowe | Wiarygodność wyników |
| Utrata kontroli nad cyklem | V1 jest jednostką nadrzędną | Łatwiejsze zarządzanie |

### 1.3 Architektura Kontroli

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    START CONTROLLER ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                           V1 LAYER                                             │   │
│  │              (Data Collection & Scheduling)                                 │   │
│  │   ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │   │                    V1 SCHEDULER                                    │   │   │
│  │   │  ✓ Kontrola czasu i harmonogramu                                   │   │   │
│  │   │  ✓ Monitorowanie stanu danych                                      │   │   │
│  │   │  ✓ Decyzja o starcie V5                                          │   │   │
│  │   │  ✓ Generowanie START EVENT                                        │   │   │
│  │   │  ✓ Monitorowanie pracy V5                                         │   │   │
│  │   └─────────────────────────────────────────────────────────────────┘   │   │
│  │                                                                         │   │
│  │   ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │   │              DATA COLLECTION ENGINE                              │   │   │
│  │   │  ✓ Pobieranie wyników (01:58)                                     │   │   │
│  │   │  ✓ Dodawanie wyników (02:04)                                      │   │   │
│  │   │  ✓ Aktualizacja bazy danych                                       │   │   │
│  │   │  ✓ Generator Database (08:03)                                     │   │   │
│  │   │  ✓ Generator Trend Analysis (08:05)                                │   │   │
│  │   └─────────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                              │                                                │
│                              ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                           V5 LAYER                                             │   │
│  │           (SSI Core - Self-Contained System)                                │   │
│  │   ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │   │                V5 ACTIVATION MANAGER                             │   │   │
│  │   │  ✓ Odbiór START EVENT z V1                                      │   │   │
│  │   │  ✓ Aktywacja System Orchestration                               │   │   │
│  │   │  ✓ Inicjalizacja wszystkich modułów                             │   │   │
│  │   │  ✓ Zarządzanie cyklem życia V5                                   │   │   │
│  │   │  ✓ Shutdown na żądanie V1                                        │   │   │
│  │   └─────────────────────────────────────────────────────────────────┘   │   │
│  │                                                                         │   │
│  │   ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │   │                    SSI V5 CORE                                    │   │   │
│  │   │  ✓ Kontroluje własny cykl życia                                   │   │   │
│  │   │  ✓ Zarządza pamięcią i stanem                                      │   │   │
│  │   │  ✓ Wykonyuje analizy i generuje predykcje                         │   │   │
│  │   │  ❌ NIE dostępuje do V1 Database (tylko przez API)                │   │   │
│  │   └─────────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.4 Odpowiedzialności

| **Komponent** | **Odpowiedzialność** | **Kontrola nad V5** |
|---------------|---------------------|---------------------|
| V1 Scheduler | Decyzja o starcie/stopie V5 | ✅ TAK |
| V1 Data Collection | Zbieranie i przygotowanie danych | ❌ NIE (ale V5 zależy od V1) |
| V5 Activation Manager | Odbiór sygnałów i aktywacja | ✅ TAK (wykonuje polecenia V1) |
| SSI V5 Core | Wykonywanie analiz i generowanie wyników | ❌ NIE (sam nie decyduje o starcie) |
| System Orchestration | Koordynacja modułów V5 | ✅ TAK (wewnątrz V5) |

### 1.5 Sygnały Kontrolne

**Sygnały od V1 do V5:**

| **Sygnał** | **Opis** | **Czas wysłania** | **Oczekiwana akcja V5** |
|------------|----------|-------------------|-------------------------|
| `START_V5` | Uruchom system V5 | 09:00 | Inicjalizacja i start |
| `SHUTDOWN_V5` | Zakończ pracę V5 | 14:00 | Zapis stanu i zamknięcie |
| `DATA_READY` | Dane gotowe do analizy | 08:05 | Można rozpocząć przetwarzanie |
| `EMERGENCY_STOP` | Natychmiastowe zatrzymanie | Kiedykolwiek | Natychmiastowe zamknięcie |
| `SYSTEM_PAUSE` | Wstrzymanie pracy | Zależy od warunków | Wstrzymanie bez zamknięcia |
| `RESUME` | Wznowienie pracy | Po PAUSE | Kontynuacja od stanu |

**Sygnały od V5 do V1:**

| **Sygnał** | **Opis** | **Czas wysłania** | **Oczekiwana akcja V1** |
|------------|----------|-------------------|-------------------------|
| `V5_READY` | V5 gotowy do pracy | 09:00:30 | Potwierdzenie startu |
| `V5_SHUTDOWN_COMPLETE` | V5 zakończył pracę | 14:00:30 | Potwierdzenie zamknięcia |
| `V5_ERROR` | Błąd w V5 | Kiedykolwiek |Logowanie i ewentualne restart |
| `V5_STATUS` | Status V5 (heartbeat) | Co 5 minut | Monitorowanie stanu |
| `MEMORY_UPDATE_REQUEST` | Żądanie aktualizacji pamięci | 02:10 | Aktualizacja pamięci systemu |

---

## 2. HARMONOGRAM V1 → V5

### 2.1 Pełny Cykl Dobowy

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    DAILY SCHEDULE: V1 → V5                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  GODZINA  │   V1 ACTION                          │   V5 STATUS    │ NOTES    │
│  ────────┼───────────────────────────────────┼────────────────┼───────────│
│  00:00   │ -                                  │ OFF            │ -       │
│  ────────┼───────────────────────────────────┼────────────────┼───────────│
│  01:58   │ Pobranie wyników (fetch results)   │ OFF            │ 🔴 KLUCZ │
│  ────────┼───────────────────────────────────┼────────────────┼───────────│
│  02:00   │ -                                  │ OFF            │ -       │
│  ────────┼───────────────────────────────────┼────────────────┼───────────│
│  02:04   │ Dodanie wyników (add results)       │ OFF            │ 🔴 KLUCZ │
│  ────────┼───────────────────────────────────┼────────────────┼───────────│
│  02:05   │ -                                  │ OFF            │ -       │
│  ────────┼───────────────────────────────────┼────────────────┼───────────│
│  02:10   │ ✅ DATA READY FOR MEMORY UPDATE    │ OFF            │ 🟡 MEM  │
│          │    -> V5 może zaktualizować pamięć │                │ UPDATE  │
│  ────────┼───────────────────────────────────┼────────────────┼───────────│
│  02:10-  │ Monitorowanie nowych danych         │ OFF            │ -       │
│  08:00   │                                       │                │          │
│  ────────┼───────────────────────────────────┼────────────────┼───────────│
│  08:00   │ Generator Database (prepare data)   │ OFF            │ 🔴 KLUCZ │
│  ────────┼───────────────────────────────────┼────────────────┼───────────│
│  08:03   │ Generator Database completetion     │ OFF            │ -       │
│  ────────┼───────────────────────────────────┼────────────────┼───────────│
│  08:05   │ ✅ Generator Trend Analysis complete │ OFF            │ 🟡 READY│
│          │    -> V5 może zacząć pracę         │                │ STATE   │
│  ────────┼───────────────────────────────────┼────────────────┼───────────│
│  08:05-  │ Czekanie na 09:00                    │ OFF            │ -       │
│  08:59   │                                       │                │          │
│  ────────┼───────────────────────────────────┼────────────────┼───────────│
│  09:00   │ ✅ START_V5 SIGNAL                   │ BOOTING        │ 🔴 START │
│          │    -> V5 uruchamia się               │                │ EVENT   │
│  ────────┼───────────────────────────────────┼────────────────┼───────────│
│  09:00:10│ -                                  │ INITIALIZING   │ -       │
│  ────────┼───────────────────────────────────┼────────────────┼───────────│
│  09:00:30│ -                                  │ ✅ READY        │ 🟢 V5   │
│          │    <- V5_READY signal to V1         │                │ READY   │
│  ────────┼───────────────────────────────────┼────────────────┼───────────│
│  09:00:30│ -                                  │ WORKING        │ -       │
│          │    V5 rozpoczęło pracę              │                │          │
│  ────────┼───────────────────────────────────┼────────────────┼───────────│
│  09:00-  │ V1Monitoruje stan danych             │ WORKING        │ -       │
│  13:50   │ V5 wykonuje analizy                  │                │          │
│  ────────┼───────────────────────────────────┼────────────────┼───────────│
│  13:50   │ -                                  │ WORKING        │ 🟡 END  │
│          │                                    │                │ OF DAY  │
│          │ End of prediction window            │                │ PREP    │
│  ────────┼───────────────────────────────────┼────────────────┼───────────│
│  13:50-  │ Przygotowanie do zamknięcia        │ PRE_SHUTDOWN    │ -       │
│  13:59   │ (zapis stanu, finalizacja)           │                │          │
│  ────────┼───────────────────────────────────┼────────────────┼───────────│
│  14:00   │ ✅ SHUTDOWN_V5 SIGNAL               │ SHUTTING_DOWN  │ 🔴 STOP  │
│          │    -> V5 kończy pracę                │                │ EVENT   │
│  ────────┼───────────────────────────────────┼────────────────┼───────────│
│  14:00:30│ -                                  │ ✅ OFF           │ 🟢 V5   │
│          │    <- V5_SHUTDOWN_COMPLETE to V1    │                │ STOPPED │
│  ────────┼───────────────────────────────────┼────────────────┼───────────│
│  14:01+  │ V1 kontynuuje swoją pracę           │ OFF            │ -       │
│  ────────┼───────────────────────────────────┼────────────────┼───────────│
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Wizualizacja Czasowa

```
DOBA V1-V5:
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  00:00                  09:00                        14:00                24:00│
│    │                    │                            │                   │
│    ▼                    ▼                            ▼                   ▼
│  ┌───┐              ┌─────────────┐            ┌─────┐              ┌───┐ │
│  │   │              │             │            │     │              │   │ │
│  │V1 │              │    V5       │            │ V5  │              │V1 │ │
│  │   │◄─────────────►│  WORKING    │◄──────────►│OFF  │              │   │ │
│  │   │  START EVENT  │             │  STOP EVENT │     │              │   │ │
│  │   │              │             │            │     │              │   │ │
│  └───┘              └─────────────┘            └─────┘              └───┘ │
│    │                    │                            │                   │
│    ▼                    ▼                            ▼                   ▼
│  ┌────────────────────────────────────────────────────────────┐            │
│  │                    V1 ACTIVITY                                  │            │
│  │  ├─ 01:58: Pobranie wyników                                      │            │
│  │  ├─ 02:04: Dodanie wyników                                       │            │
│  │  ├─ 08:03: Generator Database                                     │            │
│  │  ├─ 08:05: Generator Trend Analysis                              │            │
│  │  ├─ 09:00: START_V5                                             │            │
│  │  └─ 14:00: SHUTDOWN_V5                                          │            │
│  └────────────────────────────────────────────────────────────┘            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Kluczowe Punkty Czasowe

#### 🔴 KLUCZOWE ZDARZENIA (MUSZĄ BYĆ DOKŁADNE)

| **Godzina** | **Zdarzenie** | **System** | **Status V5** | **Znaczenie** |
|-------------|---------------|-----------|---------------|---------------|
| 01:58 | Pobranie wyników | V1 | OFF | Dane do aktualizacji |
| 02:04 | Dodanie wyników | V1 | OFF | **Dane gotowe** |
| 02:10 | DATA_READY | V1→V5 | OFF | **V5 może zaktualizować pamięć** |
| 08:03 | Generator Database | V1 | OFF | Przygotowanie bazy |
| 08:05 | Generator Trend Analysis | V1 | OFF | **Dane analizowane i gotowe** |
| 09:00 | START_V5 | V1→V5 | BOOTING | **START V5** |
| 09:00:30 | V5_READY | V5→V1 | READY | Potwierdzenie |
| 14:00 | SHUTDOWN_V5 | V1→V5 | SHUTTING_DOWN | **STOP V5** |
| 14:00:30 | V5_SHUTDOWN_COMPLETE | V5→V1 | OFF | Potwierdzenie |

#### 🟡 WAŻNE ZDARZENIA

| **Godzina** | **Zdarzenie** | **Znaczenie** |
|-------------|---------------|---------------|
| 02:10 | Memory Update Request | V5 może zaktualizować pamięć na podstawie nowych wyników |
| 08:05 | Ready State | Wszystkie dane gotowe, V5 oczekuje na START |
| 13:50 | End of Prediction Window | V5 kończy generowanie nowych predykcji |
| 13:50-13:59 | Preparation for Shutdown | Zapis stanu, finalizacja cykli |

---

## 3. SYSTEM RUNTIME AWARENESS

### 3.1 Potrzeba Runtime Awareness

**Problem:** V5 musi wiedzieć:
- Jaki jest **aktualny stan systemu**
- Czy **dane są gotowe** do analizy
- Czy **okno predykcji jest otwarte**
- Kiedy **nastąpi shutdown**
- Jaki jest **stan V1**

**Rozwiązanie:** `system_state.json` - centralny plik stanu systemu

### 3.2 Struktura: system_state.json

```json
{
  "system_metadata": {
    "schema_version": "1.0",
    "generated_at": "2026-08-01T09:15:23Z",
    "generated_by": "V1_Scheduler",
    "system_version": "SSI_V5_Phase_2_v2.0.0"
  },
  
  "runtime": {
    "current_time": "2026-08-01T09:15:23Z",
    "timezone": "UTC",
    "system_uptime": "PT2H15M23S",
    "v5_runtime": true,
    "v5_start_time": "2026-08-01T09:00:00Z",
    "v5_elapsed_time": "PT15M23S",
    "next_shutdown": "2026-08-01T14:00:00Z",
    "time_to_shutdown": "PT4H44M37S"
  },
  
  "data_status": {
    "v1_database": {
      "status": "UPDATED",
      "last_update": "2026-08-01T08:05:15Z",
      "version": "20260801_0805",
      "is_latest": true,
      "data_quality": 0.95,
      "completeness": 1.00
    },
    
    "results_available": true,
    "results_timestamp": "2026-08-01T02:04:20Z",
    "results_count": 45,
    "results_quality": 0.92,
    
    "analysis_complete": true,
    "analysis_timestamp": "2026-08-01T08:05:30Z",
    "trend_data_ready": true,
    "feature_ranking_ready": true
  },
  
  "prediction_window": {
    "status": "OPEN",
    "opened_at": "2026-08-01T09:00:00Z",
    "closes_at": "2026-08-01T13:50:00Z",
    "time_remaining": "PT4H34M37S",
    "can_generate_predictions": true,
    "prediction_counter": 234
  },
  
  "memory_state": {
    "status": "READY",
    "last_update": "2026-08-01T02:10:10Z",
    "update_trigger": "RESULTS_ADDED",
    "next_update_possible": "2026-08-01T02:10:00Z",
    "-out-of-date": false
  },
  
  "system_health": {
    "overall_status": "HEALTHY",
    "v1_status": "ACTIVE",
    "v5_status": "ACTIVE",
    "database_connection": "ESTABLISHED",
    "memory_usage": 0.68,
    "cpu_usage": 0.45,
    "last_error": null
  },
  
  "external_conditions": {
    "market_volatility": "medium",
    "market_type": "neutral",
    "data_sources_active": ["football_api", "course_provider"],
    "data_sources_health": {
      "football_api": "HEALTHY",
      "course_provider": "HEALTHY"
    }
  },
  
  "control_flags": {
    "v1_can_start_v5": true,
    "v1_can_stop_v5": true,
    "v5_can_request_memory_update": true,
    "emergency_stop_enabled": false,
    "maintenance_mode": false
  },
  
  "history": {
    "previous_states": [
      {
        "timestamp": "2026-08-01T02:10:10Z",
        "event": "RESULTS_ADDED",
        "v5_status": "OFF",
        "memory_updated": true
      },
      {
        "timestamp": "2026-08-01T08:05:30Z",
        "event": "ANALYSIS_COMPLETE",
        "v5_status": "OFF",
        "ready_state": true
      },
      {
        "timestamp": "2026-08-01T09:00:00Z",
        "event": "START_V5",
        "v5_status": "BOOTING",
        "triggered_by": "V1_SCHEDULER"
      },
      {
        "timestamp": "2026-08-01T09:00:30Z",
        "event": "V5_READY",
        "v5_status": "READY",
        "响应_time_ms": 234
      }
    ],
    "next_expected_event": {
      "event": "PREDICTION_WINDOW_CLOSE",
      "expected_at": "2026-08-01T13:50:00Z"
    }
  }
}
```

### 3.3 Przykładowe Stany w Różnych Godzinach

#### 🕑 **Godzina 02:10 - Po dodaniu wyników**

```json
{
  "current_time": "2026-08-01T02:10:10Z",
  "data_status": {
    "results_available": true,
    "results_timestamp": "2026-08-01T02:04:20Z"
  },
  "prediction_window": {
    "status": "CLOSED",
    "can_generate_predictions": false
  },
  "memory_state": {
    "status": "CAN_UPDATE",
    "next_update_possible": "2026-08-01T02:10:00Z"
  },
  "runtime": {
    "v5_runtime": false,
    "v5_status": "OFF"
  }
}
```

**co się dzieje:**
- ✅ **Można zaktualizować pamięć** (Memory Update)
- ❌ V5 jeszcze nie działa (czeka na 09:00)
- ✅ Dane są świeże i gotowe

#### 🕑 **Godzina 09:00 - Start V5**

```json
{
  "current_time": "2026-08-01T09:00:00Z",
  "data_status": {
    "v1_database": {
      "status": "UPDATED",
      "is_latest": true
    },
    "analysis_complete": true
  },
  "prediction_window": {
    "status": "OPEN",
    "can_generate_predictions": true
  },
  "runtime": {
    "v5_runtime": true,
    "v5_status": "BOOTING",
    "v5_start_time": "2026-08-01T09:00:00Z"
  }
}
```

**co się dzieje:**
- ✅ **Dane gotowe do analizy**
- ✅ **Okno predykcji OTWARTE**
- ✅ **V5 się uruchamia**
- ✅ **Można generować strategie**

#### 🕑 **Godzina 09:15 - V5 w pełni aktywny**

```json
{
  "current_time": "2026-08-01T09:15:23Z",
  "system_health": {
    "overall_status": "HEALTHY",
    "v5_status": "ACTIVE",
    "memory_usage": 0.68
  },
  "prediction_window": {
    "status": "OPEN",
    "time_remaining": "PT4H34M37S",
    "prediction_counter": 234
  },
  "runtime": {
    "v5_runtime": true,
    "v5_elapsed_time": "PT15M23S"
  }
}
```

**co się dzieje:**
- ✅ **V5 działa w pełni**
- ✅ **Generuje predykcje i strategie**
- ✅ **Okno predykcji otwarte**

#### 🕑 **Godzina 13:50 - Końcówka cyklu**

```json
{
  "current_time": "2026-08-01T13:50:00Z",
  "prediction_window": {
    "status": "CLOSED",
    "can_generate_predictions": false
  },
  "runtime": {
    "v5_runtime": true,
    "v5_status": "WORKING",
    "next_shutdown": "2026-08-01T14:00:00Z"
  },
  "memory_state": {
    "status": "READY_FOR_UPDATE",
    "last_update": "2026-08-01T09:15:00Z"
  }
}
```

**co się dzieje:**
- ❌ **Okno predykcji ZAMKNIĘTE**
- ✅ **Zapis pamięci i przygotowanie do shutdown**
- ✅ **V5 kończy obecne cykle**

#### 🕑 **Godzina 14:00 - Shutdown V5**

```json
{
  "current_time": "2026-08-01T14:00:00Z",
  "runtime": {
    "v5_runtime": false,
    "v5_status": "SHUTTING_DOWN"
  },
  "system_health": {
    "v5_status": "STOPPING"
  }
}
```

**co się dzieje:**
- 🔴 **V5 się wyłącza**
- ✅ **Zapis finalnego stanu**
- ✅ **Powiadomienie V1 o zamknięciu**

### 3.4 Aktualizacja i Monitoring

**Częstotliwość aktualizacji system_state.json:**
- **V1 Updates:** Co 1 minutę (status danych)
- **V5 Updates:** Co 15 sekund (status systemu)
- **Full Sync:** Co 5 minut (pełna synchronizacja)

**Monitoring system_state.json:**
- V1 monitoruje `v5_runtime` i `v5_status`
- V5 monitoruje `data_status` i `prediction_window`
- System Orchestration monitoruje `system_health`

---

## 4. KOMUNIKACJA V1 ↔ V5

### 4.1 Interfejsy Komunikacyjne

#### V1 → V5 (Commands)

```python
class V1ToV5Commands:
    """Komendy wysyłane z V1 do V5"""
    
    @staticmethod
    def start_v5() -> dict:
        """
        Uruchom V5
        Returns: {"status": "started", "timestamp": "...", "response": "ACK/NACK"}
        """
        return {
            "command": "START_V5",
            "timestamp": "2026-08-01T09:00:00Z",
            "parameters": {
                "prediction_window_end": "2026-08-01T13:50:00Z",
                "data_version": "20260801_0805"
            },
            "expected_response": "V5_READY"
        }
    
    @staticmethod
    def shutdown_v5() -> dict:
        """
        Zatrzymaj V5
        Returns: {"status": "shutdown_started", "timestamp": "..."}
        """
        return {
            "command": "SHUTDOWN_V5",
            "timestamp": "2026-08-01T14:00:00Z",
            "parameters": {
                "graceful": True,
                "timeout": 30  # sekund
            },
            "expected_response": "V5_SHUTDOWN_COMPLETE"
        }
    
    @staticmethod
    def emergency_stop() -> dict:
        """
        Natychmiastowe zatrzymanie V5 (awaryjne)
        """
        return {
            "command": "EMERGENCY_STOP",
            "timestamp": "2026-08-01TXX:XX:XXZ",
            "priority": "CRITICAL",
            "reason": "..."
        }
    
    @staticmethod
    def system_pause() -> dict:
        """
        Wstrzymanie V5 (bez zamknięcia)
        """
        return {
            "command": "SYSTEM_PAUSE",
            "timestamp": "2026-08-01TXX:XX:XXZ"
        }
    
    @staticmethod
    def system_resume() -> dict:
        """
        Wznowienie V5 po pauzie
        """
        return {
            "command": "SYSTEM_RESUME",
            "timestamp": "2026-08-01TXX:XX:XXZ"
        }
```

#### V5 → V1 (Status & Requests)

```python
class V5ToV1Commands:
    """Komendy i statusy wysyłane z V5 do V1"""
    
    @staticmethod
    def v5_ready() -> dict:
        """
        V5 gotowy do pracy
        """
        return {
            "status": "V5_READY",
            "timestamp": "2026-08-01T09:00:30Z",
            "system_info": {
                "version": "2.0.0",
                "modules_loaded": 21,
                "initialization_time_ms": 234
            }
        }
    
    @staticmethod
    def v5_shutdown_complete() -> dict:
        """
        V5 zakończył pracę
        """
        return {
            "status": "V5_SHUTDOWN_COMPLETE",
            "timestamp": "2026-08-01T14:00:30Z",
            "summary": {
                "predictions_generated": 2876,
                "errors": 0,
                "runtime": "PT5H0M30S"
            }
        }
    
    @staticmethod
    def v5_error(error_data: dict) -> dict:
        """
        Błąd w V5
        """
        return {
            "status": "V5_ERROR",
            "timestamp": "2026-08-01TXX:XX:XXZ",
            "error": error_data,
            "severity": "HIGH/MEDIUM/LOW"
        }
    
    @staticmethod
    def memory_update_request() -> dict:
        """
        Żądanie aktualizacji pamięci (02:10)
        """
        return {
            "request": "MEMORY_UPDATE",
            "timestamp": "2026-08-01T02:10:00Z",
            "trigger": "RESULTS_ADDED",
            "data_info": {
                "results_count": 45,
                "version": "20260801_0204"
            }
        }
    
    @staticmethod
    def heartbeat() -> dict:
        """
        Regularny sygnał życiowy (co 5 minut)
        """
        return {
            "status": "V5_HEARTBEAT",
            "timestamp": "2026-08-01T09:05:00Z",
            "health": {
                "memory_usage": 0.68,
                "cpu_usage": 0.45,
                "status": "HEALTHY"
            }
        }
```

### 4.2 Protokół Komunikacyjny

**Transport:** ZeroMQ (REQ/REP pattern)
**Format:** JSON
**Szyfrowanie:** TLS 1.3 (opcjonalnie)
**Timeout:** 30 sekund (domyślnie)

**Adresy:**
- V1 Command Endpoint: `tcp://localhost:5555`
- V5 Status Endpoint: `tcp://localhost:5556`
- V5 Heartbeat Endpoint: `tcp://localhost:5557`
- System State Endpoint: `tcp://localhost:5558` (broadcast)

---

## 5. ZALEŻNOŚĆ CZASOWA

### 5.1 Zależności Między Zdarzeniami

```
SEKWENCJA ZDARZEŃ:
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│  01:58:00                                                     │                │
│     ├─ V1: Pobranie wyników                                             │                │
│     │                                                               │                │
│  02:04:00                                                     │                │
│     ├─ V1: Dodanie wyników                                              │                │
│     │    ╰─ causas DATA_READY = true (fuerza V5 Actualizacion memoria)│         │
│  02:10:00                                                     │
│     └─ V5: (OPCIONAL) Memory Update (si system_state memoria actualizada)   │
│                                                                                 │
│  08:03:00                                                     │
│     ├─ V1: Generator Database                                           │                │
│     │                                                               │
│  08:05:00                                                     │
│     ├─ V1: Generator Trend Analysis                                      │                │
│     │    ╰─ causas READY_STATE = true (V5 pode comecar analise)             │
│     │                                                               │
│  09:00:00                                                     │
│     ├─ V1: START_V5 signal                                              │                │
│     │    ╰─ V5: Inicializacja                                           │                │
│     │                                                               │                │
│  09:00:30                                                     │
│     ├─ V5: V5_READY signal                                              │                │
│     │    ╰─ V1: Confirma recepção                                       │                │
│     │                                                               │
│  13:50:00                                                     │
│     ├─ V5: Finalizacja cykli (zapis pamięci)                              │
│     │    ╰─Prediction window zamknięty                                  │
│     │                                                               │
│  14:00:00                                                     │
│     └─ V1: SHUTDOWN_V5 signal                                            │
│          ╰─ V5: Zakończenie pracy                                        │
│              ╰─ V5_SHUTDOWN_COMPLETE signal                              │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Blokady Czasowe

**Blokady zapobiegające konfliktom:**

| **Blokada** | **Warunek** | **Działanie** |
|-------------|-------------|--------------|
| V5 nie może wystartować | V1 Database nie jest UPDATED | Oczekiwanie na aktualizację |
| V5 nie może wystartować | `current_time` < 09:00 | Oczekiwanie na 09:00 |
| V5 nie może generować predykcji | `prediction_window` != OPEN | Oczekiwanie na otwarcie okna |
| V5 nie może się zatrzymać | V5 jest w środku cyklu | Oczekiwanie na zakończenie cyklu |
| Memory Update nie może się wykonać | `results_available` = false | Oczekiwanie na dane |

---

## 6. PROCEDURY AWARYJNE

### 6.1 Scenariusze Awaryjne

#### 🔴 Scenariusz 1: V1 nie wysyła START_V5 o 09:00

**Detekcja:** V5 monitoruje `current_time` i oczekuje sygnału
**Akcja po 09:05:**
1. V5 wysyła `V5_ERROR` z typem `START_SIGNAL_MISSING`
2. V1 sprawdza swój stan
3. Jeśli V1 jest zdrowy: ponawia `START_V5`
4. Jeśli V1 ma problem: uruchamia procedurę awaryjną

#### 🔴 Scenariusz 2: V5 nie odpowiada na START_V5

**Detekcja:** V1 oczekuje `V5_READY` przez 60 sekund
**Akcja:**
1. V1 wysyła ponownie `START_V5` (max 3 próby)
2. Jeśli brak odpowiedzi: `EMERGENCY_STOP` + restart V5
3. Logowanie błędu i powiadomienie administratora

#### 🔴 Scenariusz 3: Błąd krytyczny w V5

**Detekcja:** V5 wykrywa błąd krytyczny
**Akcja:**
1. V5 wysyła `V5_ERROR` z severity `CRITICAL`
2. V5 wykonuje `EMERGENCY_STOP` (jeśli możliwe)
3. V1 odbiera error i decyduje o restarcie
4. Pełny restart systemu (jeśli konieczne)

#### 🔴 Scenariusz 4: V1 ulega awarii podczas pracy V5

**Detekcja:** V5 traci połączenie z V1
**Akcja:**
1. V5 kontynuuje pracę (autonomiczny tryb)
2. Monitoruje connection co 30 sekund
3. Po 5 minutach bez V1: `graceful shutdown`
4. Zapis stanu i czekanie na restart V1

### 6.2 Hierarchia Awaryjna

```
Priority Level 1 (CRITICAL):
├─ Loss of database connection
├─ Memory overflow
├─ Unrecoverable system error
└─ Action: IMMEDIATE SHUTDOWN

Priority Level 2 (HIGH):
├─ V1 communication lost
├─ Data corruption detected
├─ Multiple consecutive errors
└─ Action: GRACEFUL SHUTDOWN + RESTART

Priority Level 3 (MEDIUM):
├─ Single prediction error
├─ Performance degradation
└─ Action: LOG + CONTINUE

Priority Level 4 (LOW):
├─ Minor data inconsistency
├─ Network latency
└─ Action: LOG ONLY
```

---

## 7. PODSUMOWANIE

### 7.1 Kluczowe Zasady

✅ **V1 jest START CONTROLLER** - V5 nie uruchamia się sam
✅ **Harmonogram jest ścisły** - 01:58, 02:04, 08:05, 09:00, 14:00
✅ **System Runtime Awareness** - V5 wie co się dzieje w systemie
✅ **Komunikacja dwukierunkowa** - V1 ↔ V5 z wykorzystaniem ZeroMQ
✅ **Zależności czasowe** - Sekwencja zdarzeń jest ściśle zdefiniowana
✅ **Procedury awaryjne** - Obsługa scenariuszy awaryjnych

### 7.2 Architektura Kontroli

```
FINAL ARCHITECTURE:
┌─────────────────────────────────────────────────────────────────┐
│                        V1 LAYER                                      │
│   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│   │V1 Scheduler     │  │ Data Collection  │  │   Generators    │   │
│   │ (START CONTROLLER)│  │  (Results, DB)   │  │  (08:03, 08:05)│   │
│   └─────────────────┘  └─────────────────┘  └─────────────────┘   │
│                        │                                              │
│   ┌─────────────────────────────────────────────────────────┐    │
│   │                    system_state.json                        │    │
│   │  ✓ Runtime awareness                                          │    │
│   │  ✓ Data status                                                  │    │
│   │  ✓ Prediction window status                                    │    │
│   └─────────────────────────────────────────────────────────┘    │
└────────────────────┬──────────────────────────────────────────────┘
                     │
                     │ START/STOP Signals
                     │ Data Status Updates
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                        V5 LAYER                                      │
│   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│   │Activation       │  │ System          │  │   SSI Core      │   │
│   │Manager         │  │ Orchestration   │  │  (Analysis)     │   │
│   └─────────────────┘  └─────────────────┘  └─────────────────┘   │
│                        │                                              │
│   ┌─────────────────────────────────────────────────────────┐    │
│   │  System controlla su propio ciclo de vida ( BOOT / SHUTDOWN)   │    │
│   │  V1 solo da la senal de inicio y parada                       │    │
│   └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 7.3 Gotowość do Implementacji

- ✅ **Architektura zdefiniowana**
- ✅ **Harmonogram ustalony**
- ✅ **System Runtime Awareness zaprojektowany**
- ✅ **Komunikacja zdefiniowana**
- ✅ **Procedury awaryjne przygotowane**
- ⚠️ **Oczekuje na implementację**

---

*Dokument wygenerowany przez Mistral Vibe - Architecture Synchronization Engine  
Data: 2026-08-01  
Status: ✅ SYNCHRONIZATION COMPLETE*