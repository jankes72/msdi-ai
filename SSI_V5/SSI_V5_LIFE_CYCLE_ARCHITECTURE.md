# SSI V5 Life Cycle Architecture

## ETAP 5.2.4 FAZA 3.3.3 - Runtime + Life Cycle Integration

**Data:** 2026-08-03  
**Status:** IMPLEMENTED  
**Wersja:** V5 Complete

---

## Spis Tresci

1. [Przeglad Architektury](#1-przeglad-architektury)
2. [Poziomy Sterowania](#2-poziomy-sterowania)
3. [Pelny Cykl Zycia](#3-pelny-cykl-zycia)
4. [Harmonogram Dobowy](#4-harmonogram-dobowy)
5. [Komponenty Systemu](#5-komponenty-systemu)
6. [Mechanizmy Recovery](#6-mechanizmy-recovery)
7. [Przeplywy Danych](#7-przeplywy-danych)
8. [Integracja z Istniejacym Systemem](#8-integracja-z-istniejacym-systemem)

---

## 1. Przeglad Architektury

SSI V5 to wielowarstwowy system do analizy sportowych z automatycznym cyklami zycia i odpornoscia na restarty.

```
┌─────────────────────────────────────────────────────────────┐
│                    SSI V5 SYSTEM ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐     ┌──────────────────┐              │
│  │   V1 SCHEDULER    │────▶│ SSI_V5_SPORTS_   │              │
│  │   (24/7 Service)  │     │ WORLD_MODEL_      │              │
│  │                  │     │ GENERATOR.py      │              │
│  └──────────────────┘     └──────────────────┘              │
│             │                    │                              │
│             │                    ▼                              │
│             │        ┌──────────────────┐                        │
│             └────────│   WORLD ENGINE   │                        │
│                      └──────────────────┘                        │
│                                 │                               │
│                                 ▼                               │
│                      ┌──────────────────┐                        │
│                      │    PIPELINE      │                        │
│                      │   (SSIPipeline)  │                        │
│                      └────────┬─────────┘                        │
│                               │                                        │
│         ┌─────────────────────┼─────────────────────┐          │
│         │                     │                     │          │
│         ▼                     ▼                     ▼          │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐    │
│  │  MODELING    │      │   TEACHER    │      │    AGENTS    │    │
│  │   LAYER      │      │    LAYER     │      │    LAYER     │    │
│  └──────────────┘      └──────────────┘      └──────────────┘    │
│         │                     │                     │          │
│         └─────────────────────┼─────────────────────┘          │
│                               ▼                               │
│                      ┌──────────────────┐                        │
│                      │    MEMORY        │                        │
│                      │   MANAGEMENT     │                        │
│                      └──────────────────┘                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Poziomy Sterowania

### POZIOM 1 - V1 SCHEDULER (24/7 Service)

**Odpowiedzialnosc:**
- Sprawdzanie godzin systemowych
- Uruchamianie procesow wedlug harmonogramu
- Pilnowanie kolejnosci wykonywania modulow
- Monitorowanie stanu systemu

**Charakterystyka:**
- Dziala caly czas (24/7)
- NIE wykonuje logiki AI
- Tylko uruchamia i koordynuje procesy
- Odporny na bledy poszczegolnych modulow

### POZIOM 2 - SSI V5 RUNTIME

**Odpowiedzialnosc:**
- Wykonuje pelne cykle zycia systemu
- Zarządza przeplywem danych
- Kontroluje modele i agenty
- Zapewnia odpornosc na restarty

**Tryby pracy:**
- **TEST**: 10 cykli, tryb rozwojowy
- **PRODUCTION**: Ciagla praca (do 5 godzin)
- **SINGLE**: Pojedynczy cykl

---

## 3. Pelny Cykl Zycia

### Przetwarzanie Jednego Cyklu

```
┌─────────────────────────────────────────────────────────────┐
│                    SSI V5 CYCLE LIFECYCLE                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  START CYCLE                                                   │
│       │                                                       │
│       ▼                                                       │
│  ┌─────────────────┐                                         │
│  │ WORLD GENERATION │  ← WorldEngine.receive_from_generator() │
│  │   (Step 1)       │  ← WorldEngine.process()                │
│  └────────┬────────┘                                         │
│           │                                                   │
│           ▼                                                   │
│  ┌─────────────────┐                                         │
│  │   MODELING      │  ← world_engine.send_to_modeling()      │
│  │   (Step 2)      │  ← normalizer, poisson, dixon_coles     │
│  └────────┬────────┘                                         │
│           │                                                   │
│           ▼                                                   │
│  ┌─────────────────┐                                         │
│  │ TEACHER         │  ← world_engine.send_to_teacher()       │
│  │ ANALYSIS        │  ← CognitiveTeacher, WorldHierarchy     │
│  │ (Step 3)        │  ← MemoryManager, ModelEvaluator         │
│  └────────┬────────┘                                         │
│           │                                                   │
│           ▼                                                   │
│  ┌─────────────────┐                                         │
│  │ AGENT           │  ← agent_interface.execute_cycle()       │
│  │ EXECUTION       │  ← Agent_01, Agent_02, ..., Agent_06      │
│  │ (Step 4)        │  ← Kazdy agent analizuje świat          │
│  └────────┬────────┘                                         │
│           │                                                   │
│           ▼                                                   │
│  ┌─────────────────┐                                         │
│  │ OBSERVATION     │  ← agent_interface.observe()           │
│  │ (Step 5)        │  ← Zapis obserwacji                       │
│  └────────┬────────┘                                         │
│           │                                                   │
│           ▼                                                   │
│  ┌─────────────────┐                                         │
│  │ MEMORY UPDATE    │  ← MemoryManager update                │
│  │ (Step 6)        │  ← Zapis doświadczeń                       │
│  └────────┬────────┘                                         │
│           │                                                   │
│           ▼                                                   │
│  END CYCLE                                                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Statusy Cyklu

| Status | Opis | Kiedy wystepuje |
|--------|------|----------------|
| `IDLE` | System gotowy | Przed startem, po zakonczeniu |
| `INITIALIZING` | Inicjalizacja | Rozpoczecie cyklu |
| `WORLD_GENERATION` | Generowanie swiata | WorldEngine przetwarza dane |
| `MODELING` | Modelowanie | Modeling Layer analizuje cechy |
| `TEACHER_ANALYSIS` | Analiza nauczyciela | Teacher Layer ocenia wyniki |
| `AGENT_EXECUTION` | Wykonanie agentow | Agenci testuja strategie |
| `OBSERVATION` | Obserwacja | Zapis wynikow i obserwacji |
| `MEMORY_UPDATE` | Aktualizacja pamieci | Zapis doświadczeń do pamieci |
| `COMPLETE` | zakonczony | Pelny cykl zakonczony sukcesem |
| `ERROR` | Blad | Blad w kterytkolwiek kroku |
| `SHUTDOWN` | Zamkniety | System zamkniety |

---

## 4. Harmonogram Dobowy

### Typowy Dzien Operacji

```
┌─────────────────────────────────────────────────────────────┐
│                   HARMONOGRAM DOBOWY SSI V5                    │
├─────────────┬───────────────────────┬─────────────────────────┤
│   Godzina    │      Proces           │    Opis                 │
├─────────────┼───────────────────────┼─────────────────────────┤
│  01:01      │ Pobieranie kursow     │ Pobrane z bukmacherow    │
├─────────────┼───────────────────────┼─────────────────────────┤
│  01:58      │ Pobieranie wynikow    │ Mecze z poprzedniego dnia│
├─────────────┼───────────────────────┼─────────────────────────┤
│  02:04      │ Dodawanie wynikow     │ Aktualizacja bazy        │
├─────────────┼───────────────────────┼─────────────────────────┤
│  02:07      │ Start SSI Runtime     │ start_ssi.py             │
├─────────────┼───────────────────────┼─────────────────────────┤
│  08:03      │ Generator bazy danych │ generatorDataBase.py     │
├─────────────┼───────────────────────┼─────────────────────────┤
│  08:05      │ Generowanie swiata    │ SSI_V5_SPORTS_WORLD_    │
│             │                       │ MODEL_GENERATOR.py        │
├─────────────┼───────────────────────┼─────────────────────────┤
│  15:07      │ SSI Runtime           │ start_ssi.py (5 godzin)   │
├─────────────┼───────────────────────┼─────────────────────────┤
│  20:07      │ Koniec SSI Runtime    │ Zapisz stan               │
├─────────────┼───────────────────────┼─────────────────────────┤
│  21:07      │ SSI Runtime           │ start_ssi.py (kolejna    │
│             │                       │ sesja 5 godzin)           │
├─────────────┼───────────────────────┼─────────────────────────┤
│  02:07      │ SSI Runtime           │ Sesja nocna               │
└─────────────┴───────────────────────┴─────────────────────────┘
```

### Cykl Zycia Dobowy

```
┌─────────────────────────────────────────────────────────────┐
│              DOBOWY CYKL ZYCIA SSI V5                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  RANO (01:00 - 02:10)                                         │
│  ├── 01:01 → Pobieranie kursow bukmacherskich               │
│  ├── 01:58 → Pobieranie wynikow meczow                        │
│  └── 02:04-02:07 → Aktualizacja bazy i start SSI               │
│                                                              │
│  PORANEK (08:00 - 08:10)                                       │
│  ├── 08:03 → generatorDataBase.py                             │
│  └── 08:05 → SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py          │
│                                                              │
│  DZIEN (15:07 - 20:07)                                         │
│  └── SSI Runtime (5 godzin)                                   │
│                                                              │
│  WIECZOR (21:07 - 02:07+1)                                     │
│  └── SSI Runtime (5 godzin)                                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Komponenty Systemu

### 5.1 WorldEngine

**Plik:** `SSI_V5/core/world_engine.py`

**Odpowiedzialnosc:**
- Odbior danych z generatora
- Przygotowanie kontraktu WorldEngineOutput
- Przekazanie danych do Modeling Layer
- Przekazanie wynikow do Teacher Layer

**Kontrakt WorldEngineOutput:**
```python
@dataclass
class WorldEngineOutput:
    results: Dict[str, Any]      # Glowne wyniki
    features: Dict[str, Any]    # Cechy i dane wejsciowe
    models: Dict[str, Any]      # Modele i ich parametry
    predictions: Dict[str, Any] # Predykcje
    observations: Dict[str, Any] # Obserwacje i analiza
    metadata: Dict[str, Any]    # Metadane cyklu
```

### 5.2 SSIPipeline

**Plik:** `SSI_V5/core/pipeline.py`

**Odpowiedzialnosc:**
- Glowny sterownik cykli zycia
- Zarzadzanie przeplywem: WorldEngine → Modeling → Teacher → Agent → Memory
- Kontrola statusu systemu
- Obsluga wielu cykli

**Tryby pracy:**
- `PipelineMode.TEST` - Tryb testowy
- `PipelineMode.PRODUCTION` - Tryb produkcyjny  
- `PipelineMode.SINGLE` - Pojedynczy cykl

### 5.3 Runtime Launchers

#### Test Launcher (`runtime/start_ssi_test.py`)

- Uruchamia Pipeline w trybie TEST
- Wykonuje 10 cykli testowych
- Zapisuje stan do: runtime_state.json, last_cycle.json
- Obsluguje bledy i graceful shutdown

#### Production Launcher (`runtime/start_ssi.py`)

- Uruchamia Pipeline w trybie PRODUCTION
- Pracuje do 5 godzin
- Zapisuje stan co 5 cykli
- Mechanizm recovery po restarcie
- TimeManager do kontroli czasu pracy
- StateManager do zarzadzania plikami stanu
- RecoveryManager do odzysku po restarcie

### 5.4 Teacher Layer

**Plik:** `SSI_V5/teachers/`

| Komponent | Odpowiedzialnosc |
|-----------|------------------|
| `CognitiveTeacher` | Analiza harmadik wynikow, uczenie sie wzorców |
| `WorldHierarchyManager` | Zarzadzanie hierarchia swiatow, dziedziczenie wiedzy |
| `DynamicWeightsManager` | Dynamiczna regulacja wag modeli |
| `MemoryManager` | Zarzadzanie pamiecia systemu, zapis doswiadczen |
| `ModelEvaluator` | Ocenianie modeli, wybieranie najlepszych strategii |

### 5.5 Modeling Layer

**Plik:** `SSI_V5/modeling/`

| Komponent | Odpowiedzialnosc |
|-----------|------------------|
| `normalizer.py` | Normalizacja danych |
| `splitter.py` | Podzial danych na zbiory treningowe/testowe |
| `poisson.py` | Model Poissona do predykcji wynikow |
| `dixon_coles.py` | Model Dixon-Coles (rozszerzony Poisson) |
| `matrix.py` | Macierze prawdopodobienstw |
| `network_builder.py` | Budowa sieci neuronowych (5 wersji) |

---

## 6. Mechanizmy Recovery

### 6.1 Pliki Stanu Systemu

| Plik | Opis | Zawartosc |
|------|------|-----------|
| `runtime_state.json` | Aktualny stan systemu | Mode, pipeline_status, time_summary, config |
| `last_cycle.json` | Ostatni wykonany cykl | Metadane i wyniki ostatniego cyklu |
| `cycle_history.json` | Historia cykli | Lista wszystkich wykonanych cykli |
| `event_log.json` | Dziennik zdarzen | Wszystkie zdarzenia systemowe |
| `recovery_info.json` | Informacje recovery | session_id, start_time, cycle_count |

### 6.2 Mechanizm Recovery

```
┌─────────────────────────────────────────────────────────────┐
│                    RECOVERY MECHANISM                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  SYSTEM RESTART                                                │
│       │                                                       │
│       ▼                                                       │
│  ┌─────────────────┐                                         │
│  │ RecoveryManager  │                                         │
│  │ check_for_recovery│────▶ Czy jest recovery_info.json?     │
│  └────────┬────────┘                                         │
│           │ YES                                               │
│           ▼                                                   │
│  ┌─────────────────┐                                         │
│  │ Load All State   │  ← recovery_info.json                  │
│  │                  │  ← runtime_state.json                   │
│  │                  │  ← last_cycle.json                      │
│  └────────┬────────┘                                         │
│           │                                                   │
│           ▼                                                   │
│  ┌─────────────────┐                                         │
│  │ Kontynuuj prace   │  ← Od ostatniego cyklu                 │
│  │                  │  ← Z zachowanym stanem                  │
│  └──────────────────┘                                         │
│                                                              │
│  NOWA SESJA                                                   │
│       │                                                       │
│       ▼                                                       │
│  ┌─────────────────┐                                         │
│  │ Tworz nowa       │  ← Nowa sesja, nowy session_id         │
│  │ sesje           │  ← Nowe pliki stanu                    │
│  └──────────────────┘                                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 Odpornosc na Restarty

1. **Przed restartem systemu operacyjnego:**
   - System zapisuje stan co 5 cykli
   - Ostatni stan jest zawsze zapisyany
   - recovery_info.json jest aktualizowany po kazdym cyklu

2. **Po restarcie:**
   - RecoveryManager sprawdza czy istnieja pliki stanu
   - Jesli tak, ladowane sa wszystkie dane
   - System kontynuuje od ostatniego znanego stanu
   - Nowa sesja dostaje nowy session_id

3. **Zapewnienie ciaglosci:**
   - Kazdy launcher (test i production) uzywa tych samych mechanizow recovery
   - Pliki stanu sa w tym samym katalogu
   - Format JSON zapewnia kompatybilnosc

---

## 7. Przeplywy Danych

### 7.1 Przeplyw Glowny

```
Generator → WorldEngine → Pipeline → Modeling → Teacher → Agents → Observation → Memory
```

### 7.2 Kontrakt Danych (WorldEngineOutput)

```json
{
  "results": {
    "main": {"wynik": ["2:1", "1:0", "3:2"], "shape": [3, 1]}
  },
  "features": {
    "main": {
      "atak_gospodarzy": [1.5, 1.2, 1.8],
      "obrona_gospodarzy": [1.0, 1.3, 0.9],
      "atak_gosci": [1.1, 0.9, 1.4],
      "obrona_gosci": [1.2, 1.0, 1.1]
    }
  },
  "models": {
    "poisson": {"params": {...}},
    "dixon_coles": {"params": {...}}
  },
  "predictions": {
    "poisson": {"Y_pred": ["2:1", "1:1", "2:0"]},
    "dixon_coles": {"Y_pred": ["2:1", "1:0", "2:1"]}
  },
  "observations": {
    "accuracy": 0.85,
    "analysis": {...}
  },
  "metadata": {
    "cycle_id": "SSI_V5_WORLD_CYCLE_20260803_150700_123456",
    "world_name": "SSI_V5_WORLD",
    "generator": "SSI_V5_SPORTS_WORLD_MODEL_GENERATOR",
    "processing_timestamp": "2026-08-03T15:07:00.123456",
    "engine_version": "SSI_V5_ETAPE_5.2.4_FAZA_3.3.3"
  }
}
```

### 7.3 Zaleznosci Miedzywarstwowe

```
WorldEngine
    ├── odbiera dane z generatora
    ├── przygotowuje WorldEngineOutput
    ├── przekazuje do Modeling Layer
    └── przekazuje do Teacher Layer

Pipeline
    ├── używa WorldEngine
    ├── koordynuje Modeling Layer
    ├── koordynuje Teacher Layer
    ├── zarządza Agent Layer
    └── kontroluje Memory Update

Modeling Layer
    ├── normalizuje dane (normalizer.py)
    ├── dzieli dane (splitter.py)
    ├── buduje modele (poisson.py, dixon_coles.py)
    └── analizuje wyniki (matrix.py, network_builder.py)

Teacher Layer
    ├── CognitiveTeacher - analizuje wyniki
    ├── WorldHierarchyManager - zarządza hierarchią
    ├── DynamicWeightsManager - reguluje wagi
    ├── MemoryManager - zarządza pamięcią
    └── ModelEvaluator - ocenia modele
```

---

## 8. Integracja z Istniejacym Systemem

### 8.1 Chronione Moduly (NIE ZMIENIAMY)

- ✅ **NIE ROBIMY ZMIAN** w `SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py`
- ✅ **NIE ROBIMY ZMIAN** w istniejacych testach WorldEngine
- ✅ **NIE ROBIMY ZMIAN** w istniejacych testach Teacher Layer
- ✅ **NIE ROBIMY ZMIAN** w istniejacych testach Pipeline

### 8.2 Nowe Moduly (UTWORZONE)

- ✅ `SSI_V5/core/world_engine.py` - Most miedzy generatorem a kolejными warstwami
- ✅ `SSI_V5/core/pipeline.py` - Glowny sterownik cykli zycia
- ✅ `SSI_V5/teachers/` - Caly Teacher Layer (5 komponentow)
- ✅ `SSI_V5/runtime/` - Runtime Layer (2 launchery, mechanizm recovery)

### 8.3 Zaleznosci i Integracja

```
V1 SCHEDULER (Istniejący, 24/7)
    │
    └──▶ Uruchamia procesy wedlug harmonogramu
            │
            ├── 01:01 → Pobieranie kursow
            ├── 01:58 → Pobieranie wynikow
            ├── 02:04 → Dodawanie wynikow
            ├── 02:07 → start_ssi.py / start_ssi_test.py
            ├── 08:03 → generatorDataBase.py
            ├── 08:05 → SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py
            └── 15:07/21:07 → start_ssi.py

SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py (Istniejący, NIENARUSZONY)
    │
    └──▶ Generuje dane swiata
            │
            └──▶ WorldEngine.receive_from_generator()
                    │
                    └──▶ Pipeline.run_cycle()
                            │
                            ├── Modeling Layer
                            ├── Teacher Layer
                            ├── Agent Layer
                            └── Memory Update
```

---

## Zalozenia Systemowe

1. **System 24/7:** V1 Scheduler dziala caly czas
2. **Odpornosc na Restarty:** Mechanizm recovery Pozwala na kontynuacje po restarcie komputera
3. **Limit Czasu:** Production launcher pracuje maksymalnie 5 godzin
4. **Bufor Czasowy:** 5 minut przed koncem system zaprzestaje nowych cykli
5. **Testowy vs Produkcyjny:** Tryb TEST uzywa 10 cykli, PRODUCTION uzywa pêtli ciaglej

---

## Wskazowki Rozwojowe

1. **Tworzac nowe moduly:**
   - Uzywaj taj samej struktury co istniejące
   - Zapewnij compatybilnosc z WorldEngineOutput
   - Dodaj testy jednostkowe
   - Dokumentuj kod

2. **Modyfikujac istniejące:**
   - NIE modyfikuj generatora
   - Zmiany w Pipeline musza byc backwards compatible
   - Zawsze aktualizuj dokumentacje

3. **Testowanie:**
   - Uruchamiaj start_ssi_test.py przed commit
   - Sprawdzaj wszystkie testy (min. 25 testow)
   - Testuj mechanizm recovery

---

## Podsumowanie

SSI V5 Life Cycle Architecture to pelnoprawny system z:

- ✅ Dwa poziomy sterowania (Scheduler + Runtime)
- ✅ Pelny cykl zycia danych (World Generation → Memory)
- ✅ Odpornoscia na restarty systemu
- ✅ Trybem testowym i produkcyjnym
- ✅ Mechanizmami recovery i ciaglosci
- ✅ Dokumentacja i zaleznosci

**ETAP 5.2.4 FAZA 3.3.3:** ZAKONCZONY ✅

---

*Generated: 2026-08-03  
ETAP: 5.2.4 FAZA 3.3.3 - Runtime + Life Cycle Integration*
