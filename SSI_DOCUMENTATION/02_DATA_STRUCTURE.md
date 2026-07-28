# SSI Data Structure
## Struktury Danych Systemu Self Learning Intelligence Ecosystem

[TAGS: DATA, STRUCTURE, WORLD, MEMORY, AGENT, STRATEGY]

---

## 1. Przegląd Struktur Danych

System SSI operuje na wielu warstwach danych, z których każda posiada swoją własną strukturę i cel funkcjonalny. Główne kategorie struktur danych:

1. **Dane Pierwotne (Raw Data)** - CSV, surowa historia
2. **Dane Modeli (Model Data)** - Cechy, parametry, wyniki
3. **Dane Światów (World Data)** - Interpretacje, pamięci, metadane
4. **Dane Agentów (Agent Data)** - Osobowości, pamięci, strategie
5. **Dane Strategii (Strategy Data)** - Obiekty, historie, rankingi

---

## 2. Dane Pierwotne (Data Intelligence Layer)

### 2.1 Źródła Danych

**[DATA]**

| Plik/Proses | Cel | Wyjście | Status |
|-------------|-----|---------|--------|
| `pobieranieKursow.py` | Pobieranie kursów z bukmacherów | `kursy_przygotowane.csv` | ✅ Gotowe |
| `pobieranieWynikow.py` | Pobieranie wyników meczów | Dane wyników | ✅ Gotowe |
| `dodawanieWynikow.py` | Dodawanie wyników do historii | Historia zdarzeń | ✅ Gotowe |
| `generatorDataBase.py` | Generowanie bazy meczów | Baza danych | ✅ Gotowe |
| `generatorDataBaseTrendAnalisAll.py` | Analiza trendów | Cechy trendów | ✅ Gotowe |

### 2.2 Struktura kursy_przygotowane.csv

**[DATA]**

```csv
mecz;kurs_1_start;kurs_X_start;kurs_2_start;kurs_1_koniec;kurs_X_koniec;kurs_2_koniec;zmiana_kurs_1;zmiana_kurs_X;zmiana_kurs_2;procent_kurs_1;procent_kurs_X;procent_kurs_2
Simba SC - Ruvu Shooting;1.1;7.4;18.0;1.13;6.8;16.0;0.029999999999999805;-0.6000000000000005;-2.0;0.027272727272727094;-0.08108108108108115;-0.1111111111111111;3:0
```

**Pola:**
- `mecz` - Nazwa meczu
- `kurs_1_start` - Kurs na wygraną gospodarzy (początkowy)
- `kurs_X_start` - Kurs na remis (początkowy)
- `kurs_2_start` - Kurs na wygraną gości (początkowy)
- `kurs_1_koniec` - Kurs na wygraną gospodarzy (końcowy)
- `kurs_X_koniec` - Kurs na remis (końcowy)
- `kurs_2_koniec` - Kurs na wygraną gości (końcowy)
- `zmiana_kurs_1` - Absolutna zmiana kursu 1
- `zmiana_kurs_X` - Absolutna zmiana kursu X
- `zmiana_kurs_2` - Absolutna zmiana kursu 2
- `procent_kurs_1` - Procentowa zmiana kursu 1
- `procent_kurs_X` - Procentowa zmiana kursu X
- `procent_kurs_2` - Procentowa zmiana kursu 2

---

## 3. Struktury Danych V2 Model Laboratory

### 3.1 Podział Danych Modelowych

**[DATA]**

```
100% DANYCH
├── 60% TRening + Walidacja
│   ├── 60% Trening
│   └── 40% Walidacja (w ramach 60%)
└── 40% NIEZALEŻNA OBSERWACJA
    ├── Tworzenie pamięci
    ├── Analiza zachowania
    └── Wykrywanie wzorców
```

### 3.2 Cechy Modelowe

**[DATA]** [WORLD]

Każdy model operuje na swoim zbiorze cech:

**Świat 1: Zmiany Kursów**
- `zmiana_1` - Zmiana kursu na 1
- `zmiana_X` - Zmiana kursu na X
- `zmiana_2` - Zmiana kursu na 2

**Świat 2: Dynamika**
- `amplituda_1` - Amplituda zmian kursu 1
- `amplituda_X` - Amplituda zmian kursu X
- `amplituda_2` - Amplituda zmian kursu 2
- `tempo_1` - Tempo zmian kursu 1
- `tempo_X` - Tempo zmian kursu X
- `tempo_2` - Tempo zmian kursu 2
- `synchronizacja` - Synchronizacja zmian między kursami
- `max_wahanie_1` - Maksymalne wahanie kursu 1
- `max_wahanie_X` - Maksymalne wahanie kursu X
- `max_wahanie_2` - Maksymalne wahanie kursu 2

**Świat 3: Klasyfikacja**
- `log_start_1` - Logarytm kursu 1 (początek)
- `log_start_X` - Logarytm kursu X (początek)
- `log_start_2` - Logarytm kursu 2 (początek)
- `log_koniec_1` - Logarytm kursu 1 (koniec)
- `log_koniec_X` - Logarytm kursu X (koniec)
- `log_koniec_2` - Logarytm kursu 2 (koniec)

**Świat 4: Relacje**
- `ratio_1X_start` - Stosunek kursu 1 do X (początek)
- `ratio_1_2_start` - Stosunek kursu 1 do 2 (początek)
- `ratio_X2_start` - Stosunek kursu X do 2 (początek)
- `ratio_1X_koniec` - Stosunek kursu 1 do X (koniec)
- `ratio_1_2_koniec` - Stosunek kursu 1 do 2 (koniec)
- `ratio_X2_koniec` - Stosunek kursu X do 2 (koniec)

**Statystyki:**
- `mean_1`, `mean_X`, `mean_2` - Średnie kursów
- `median_1`, `median_X`, `median_2` - Medianowe kursów
- `stdev_1`, `stdev_X`, `stdev_2` - Odchylenie standardowe kursów
- `czas_h` - Czas obserwacji w godzinach

---

## 4. Struktury Danych V3 World Memory System

### 4.1 World Memory

**[MEMORY]** **[DATA]**

```json
{
  "world_id": "swiat_zmian_kursow",
  "world_type": "change_analysis",
  "features": [
    "zmiana_1", "zmiana_X", "zmiana_2"
  ],
  "metadata": {
    "source": "V2 Model Laboratory",
    "model_reference": "siec_01_zmiana_kursow",
    "creation_date": "YYYY-MM-DD",
    "last_updated": "YYYY-MM-DD"
  },
  "memory_entries": [
    {
      "entry_id": "unique_id",
      "event": "mecz_example",
      "features": { ... },
      " timestamp": "YYYY-MM-DD HH:MM:SS",
      "value": 0.85
    }
  ]
}
```

### 4.2 System Tagowania

**[DATA]** **[MEMORY]**

**7 Kategorii Tagów:**

| Kategoria | Opis | Przykładowe Tagi |
|-----------|------|------------------|
| wynik | Wynik meczu | `@wynik:1:0`, `@wynik:2:1`, `@wynik:X` |
| zachowanie | Zachowanie modelu | `@zachowanie:stabilne`, `@zachowanie:zmienne` |
| skuteczność | Skuteczność predykcji | `@skutecznosc:wysoka`, `@skutecznosc:niska` |
| odchylenia | Odchylenia od normy | `@odchylenie:duze`, `@odchylenie:male` |
| ekonomia | Aspekty ekonomiczne | `@ekonomia:wysoki_kurs`, `@ekonomia:wartosc_EV` |
| zależności | Zależności między światami | `@zaleznosc:swiat1_swiat2`, `@zaleznosc:silna` |
| strategiczne | Kategorie strategiczne | `@strategia:bezpieczna`, `@strategia:wysokie_AKO`, `@strategia:odwrocony_wzorzec` |

---

## 5. Struktury Danych V4 Agent System

### 5.1 Personality Vector

**[AGENT]** **[DATA]**

**Struktura:**

```json
{
  "agent_id": "agent_001",
  "personality_vector": {
    "analysis_power": 0.80,
    "risk_acceptance": 0.30,
    "curiosity": 0.70,
    "security_preference": 0.85,
    "experimentation_level": 0.40,
    "independence": 0.60,
    "trust_level": 0.50,
    "resilience": 0.90
  },
  "personality_type": "ANALYST_AGENT",
  "specialization": ["pattern_detection", "stable_analysis"],
  "evolution_history": [
    {
      "timestamp": "YYYY-MM-DD HH:MM:SS",
      "previous_values": { ... },
      "new_values": { ... },
      "reason": "discovered_value_in_high_odds"
    }
  ]
}
```

**Parametry Osobowości:**

| Parametr | Zakres | Opis | Wpływ na zachowanie |
|----------|--------|------|---------------------|
| `analysis_power` | 0.0 - 1.0 | Zdolność do analizy danych i wzorców | Wyższa = bardziej analityczne podejście |
| `risk_acceptance` | 0.0 - 1.0 | Poziom akceptowanego ryzyka | Wyższa = większa akceptacja ryzyka |
| `curiosity` | 0.0 - 1.0 | Skłonność do poszukiwania nowych rozwiązań | Wyższa = więcej eksperymentów |
| `security_preference` | 0.0 - 1.0 | Preferencja stabilnych i bezpiecznych decyzji | Wyższa = bardziej ostrożne strategie |
| `experimentation_level` | 0.0 - 1.0 | Gotowość do testowania nowych hipotez | Wyższa = więcej testów nowych strategii |
| `independence` | 0.0 - 1.0 | Poziom samodzielności decyzji | Wyższa = mniej zależności od innych agentów |
| `trust_level` | 0.0 - 1.0 | Aktualny poziom zaufania do innych agentów | Wyższa = większa waga opinii innych |
| `resilience` | 0.0 - 1.0 | Odporność na błędne decyzje i porażki | Wyższa = szybszy powrót po porażkach |

### 5.2 Emotional Parameters

**[AGENT]** **[DATA]**

```json
{
  "emotional_state": {
    "confidence": 0.75,
    "frustration": 0.10,
    "curiosity_level": 0.85,
    "satisfaction": 0.60,
    "strategic_pressure": 0.20
  },
  "emotional_history": [
    {
      "timestamp": "YYYY-MM-DD HH:MM:SS",
      "event": "correct_prediction",
      "emotional_change": { "satisfaction": +0.15 }
    },
    {
      "timestamp": "YYYY-MM-DD HH:MM:SS",
      "event": "three_consecutive_errors",
      "emotional_change": { "frustration": +0.30, "strategic_pressure": +0.25 }
    }
  ]
}
```

**Parametry Emocjonalne:**

| Parametr | Trigger | Efekt |
|----------|---------|--------|
| `confidence` | Trafne decyzje, dobre strategie | Wzmacnia własne opinie, zwiększa pewność |
| `frustration` | Seria błędnych decyzji | Zmniejsza pewność, zwiększa potrzebę zmiany |
| `curiosity_level` | Nowe odkrycia, nieoczekiwane wzorce | Zwiększa ilość eksperymentów |
| `satisfaction` | Trafne decyzje, skuteczne strategie | Wzmacnia obecne zachowania |
| `strategic_pressure` | Powtarzalne błędy, brak skuteczności | Zmniejsza zaufanie do obecnej strategii, szuka zmian |

### 5.3 Trust Memory

**[AGENT]** **[DATA]**

```json
{
  "agent_id": "agent_001",
  "trust_matrix": {
    "agent_002": {
      "trust_score": 0.85,
      "weight": 0.90,
      "history": [
        {
          "event": "shared_quarter_strategy",
          "outcome": "correct",
          "trust_change": +0.10
        }
      ]
    },
    "agent_003": {
      "trust_score": 0.45,
      "weight": 0.30,
      "history": [
        {
          "event": "shared_high_risk_strategy",
          "outcome": "incorrect",
          "trust_change": -0.20
        }
      ]
    }
  },
  "average_trust": 0.65
}
```

**Reguły Aktualizacji Zaufania:**
- Dobra informacja (trafiona strategia) → wzrost zaufania
- Zła informacja (powtarzalne błędy) → spadek zaufania
- Agent NIGDY nie jest usuwany z powodu błędów
- Zmienia się jedynie waga jego opinii

---

## 6. Struktury Danych Agent Memory

### 6.1 Agent Memory System

**[MEMORY]** **[DATA]**

```json
{
  "agent_id": "agent_001",
  "memory": {
    "strategies": [ ... ],
    "experiments": [ ... ],
    "results": [ ... ],
    "errors": [ ... ],
    "lessons": [ ... ],
    "decision_history": [ ... ]
  }
}
```

### 6.2 AgentMemory - Pełna Struktura

**[MEMORY]** **[DATA]**

```json
{
  "agent_id": "string",
  "type": "AgentMemory",
  "created_at": "YYYY-MM-DD HH:MM:SS",
  "last_updated": "YYYY-MM-DD HH:MM:SS",
  "strategies": [
    {
      "strategy_id": "string",
      "status": "ACTIVE|TESTING|ARCHIVED",
      "performance": 0.75
    }
  ],
  "experiments": [
    {
      "experiment_id": "string",
      "hypothesis": "description",
      "setup": { ... },
      "result": "SUCCESS|FAILURE|PARTIAL",
      "timestamp": "YYYY-MM-DD HH:MM:SS"
    }
  ],
  "results": [
    {
      "decision_id": "string",
      "match": "string",
      "prediction": "1|X|2",
      "actual_result": "1|X|2",
      "outcome": "CORRECT|INCORRECT",
      "value": 2.5,
      "timestamp": "YYYY-MM-DD HH:MM:SS"
    }
  ],
  "errors": [
    {
      "error_id": "string",
      "decision_id": "string",
      "type": "PREDICTION|STRATEGY|ANALYSIS",
      "description": "string",
      "impact": 0.5,
      "timestamp": "YYYY-MM-DD HH:MM:SS"
    }
  ],
  "lessons": [
    {
      "lesson_id": "string",
      "from_error_id": "string",
      "content": "description",
      "application": "how_to_apply",
      "timestamp": "YYYY-MM-DD HH:MM:SS"
    }
  ],
  "decision_history": [
    {
      "decision_id": "string",
      "world": "string",
      "model": "string",
      "strategy": "string",
      "criteria": { ... },
      "outcome": "CORRECT|INCORRECT",
      "timestamp": "YYYY-MM-DD HH:MM:SS"
    }
  ]
}
```

### 6.3 Dwuwarstwowa Pamięć

**[MEMORY]** **[ARCHITECTURE]**

#### Global Memory
- **Typ:** Shared Knowledge Layer
- **Dostęp:** Wszyscy agenci
- **Zawartość:**
  - Potwierdzone odkrycia
  - Stabilne wzorce
  - Wyniki laboratoriów
  - Sprawdzone strategie
  - Historia skutecznych decyzji
- **Reguła:** Informacja trafia dopiero po procesie oceny (obserwacja → test → wynik → walidacja → globalizacja)

#### Private Notebook
- **Typ:** Private Agent Knowledge Storage
- **Dostęp:** Pojedynczy agent
- **Zawartość:**
  - Prywatne hipotezy
  - Eksperymenty
  - Pomysły
  - Niepewne obserwacje
  - Alternatywne rozwiązania
- **Reguła:** Nie każda informacja musi być od razu udostępniana

---

## 7. Struktury Danych Strategy System

### 7.1 StrategyObject

**[STRATEGY]** **[DATA]**

**strategia NIE jest tekstem. Strategia jest obiektem systemowym.**

```json
{
  "strategy_id": "strategy_001",
  "world_reference": "swiat_zmian_kursow",
  "model_reference": "siec_01_zmiana_kursow",
  "features": [
    "zmiana_1", "zmiana_X", "zmiana_2",
    "amplituda_1", "tempo_1"
  ],
  "training_data": {
    "source": "dataBase_futbol_trend.csv",
    "period": "2023-01-01 to 2024-12-31",
    "sample_size": 1000,
    "split": "60% training, 40% observation"
  },
  "prediction_generator": {
    "type": "neural_network|random_forest|classifier",
    "parameters": { ... },
    "implementation": "code_reference"
  },
  "parameters": {
    "risk_level": "LOW|MEDIUM|HIGH",
    "min_odds": 2.0,
    "max_groups": 5,
    "confidence_threshold": 0.70
  },
  "results_history": [
    {
      "decision_id": "dec_001",
      "timestamp": "YYYY-MM-DD HH:MM:SS",
      "prediction": "2",
      "actual": "2",
      "outcome": "CORRECT",
      "value": 3.5,
      "accuracy_contribution": 0.85
    }
  ],
  "value_score": 0.82,
  "status": "ACTIVE",
  "created_at": "YYYY-MM-DD HH:MM:SS",
  "updated_at": "YYYY-MM-DD HH:MM:SS",
  "life_cycle_stage": "ACTIVE",
  "ranking": "A"
}
```

**Pola StrategyObject:**

| Pole | Typ | Opis |
|------|-----|------|
| `strategy_id` | string | Unikalny identyfikator |
| `world_reference` | string | Świat, dla którego działa strategia |
| `model_reference` | string | Model wykorzystany przez strategię |
| `features` | array | Zestaw wykorzystywanych cech |
| `training_data` | object | Dane wykorzystane do nauki |
| `prediction_generator` | object | Mechanizm generowania predykcji |
| `parameters` | object | Konfiguracja strategii |
| `results_history` | array | Historia wyników |
| `value_score` | float | Aktualna wartość strategii (0-1) |
| `status` | string | Aktualny etap życia |

### 7.2 Strategy Life Cycle Stages

**[STRATEGY]** **[EVOLUTION]**

**10 Etapów Cyklu Życia:**

```
NARODZINY (BIRTH)
↓
NOWA STRATEGIA (NEW) - Strategia właśnie powstała, nie posiada historii
↓
TEST (TESTING) - Strategia przechodzi eksperymenty i pierwsze oceny
↓
DOJRZEWANIE (MATURING) - Strategia zdobywa doświadczenie i zwiększa wiarygodność
↓
OBSERWACJA (OBSERVATION) - Strategia jest monitorowana
↓
ANALIZA (ANALYSIS) - Głęboka analiza skuteczności
↓
RANKING (RANKING) - Ocena i przydzielenie poziomu
↓
AKTYWNE UŻYCIE (ACTIVE) - Strategia jest wykorzystywana w procesach decyzyjnych
↓
SPADEK WARTOŚCI (DECLINING) - Strategia traci wartość lub przestaje pasować
↓
ARCHIWUM (ARCHIVED) - Strategia nie jest aktywnie używana, ale pozostaje w historii
```

### 7.3 System Ligi Strategii

**[STRATEGY]** **[DATA]**

**Poziomy Rankingowe:**

| Poziom | Opis | Charakterystyka |
|--------|------|-----------------|
| **A+** | Najwyższa skuteczność | Strategie kluczowe, sprawdzone w wielu warunkach |
| **A** | Bardzo wartościowe | Strategie o wysokiej skuteczności |
| **B** | Użyteczne | Strategie wymagające dalszej obserwacji |
| **C** | Eksperymentalne | Nowe strategie, testowane |
| **D** | Niska wartość | Strategie o niskiej aktualnej wartości |

**Reguły Awansu:**
- Dobre wyniki
- Stabilność
- Powtarzalność
- Zgodność z rzeczywistością

**Reguły Spadku:**
- Utrata skuteczności
- Zmiana warunków
- Powtarzalne błędy
- Brak przewagi

### 7.4 Experience Trace

**[STRATEGY]** **[MEMORY]** **[DATA]**

**Strategia nigdy nie jest całkowicie usuwana. Usuwane jest tylko aktywne wykorzystanie.**

```json
{
  "experience_trace_id": "trace_001",
  "strategy_id": "strategy_001",
  "full_history": { ... },
  "input_data": { ... },
  "model_used": { ... },
  "features_used": [ ... ],
  "parameters_used": { ... },
  "results": [ ... ],
  "decisions": [ ... ],
  "errors": [ ... ],
  "rejection_reason": "lost_effectiveness_due_to_market_change",
  "hidden_value": "may_work_in_different_conditions",
  "archived_at": "YYYY-MM-DD HH:MM:SS",
  "restoration_possible": true
}
```

**Zawartość Experience Trace:**
- Pełna historia strategii
- Dane wejściowe
- Model użyty
- Cechy użyte
- Parametry użyte
- Wyniki
- Decyzje
- Błędy
- Powód odrzucenia
- Ukryta wartość
- Moment archiwizacji

---

## 8. Struktury Danych Laboratoriów

### 8.1 Laboratorium Decyzji

**[DATA]**

```json
{
  "laboratory_type": "DECISION",
  "agent_id": "agent_001",
  "experiment": {
    "world_selected": "swiat_zmian_kursow",
    "model_selected": "siec_01_zmiana_kursow",
    "data_selected": "dataBase_futbol_trend.csv",
    "strategy_selected": "strategy_001",
    "prediction": "2",
    "confidence": 0.85,
    "value": 3.2,
    "risk": "MEDIUM"
  },
  "result": {
    "actual": "2",
    "outcome": "CORRECT",
    "value_achieved": 3.2
  },
  "timestamp": "YYYY-MM-DD HH:MM:SS"
}
```

### 8.2 Laboratorium Grup

**[DATA]**

```json
{
  "laboratory_type": "GROUP",
  "agent_id": "agent_001",
  "analysis": {
    "number_of_matches": 8,
    "risk_level": "LOW",
    "group_arrangement": "2x4",
    "dependency_analysis": { ... }
  },
  "result": {
    "group_effectiveness": 0.75,
    "risk_assessment": "ACCEPTABLE"
  }
}
```

### 8.3 Laboratorium Kuponów

**[DATA]**

```json
{
  "laboratory_type": "COUPON",
  "agent_id": "agent_001",
  "analysis": {
    "number_of_groups": 4,
    "combinations": 16,
    "profitability": 2.5,
    "total_risk": "MEDIUM"
  },
  "result": {
    "coupon_value": 15.2,
    "success_rate": 0.68
  }
}
```

### 8.4 Laboratorium Strategii

**[DATA]**

```json
{
  "laboratory_type": "STRATEGY",
  "agent_id": "agent_001",
  "strategy_creation": {
    "base_strategy_id": "strategy_001",
    "new_knowledge": "discovered_pattern",
    "experience_applied": "previous_errors",
    "new_strategy_id": "strategy_002"
  },
  "testing": {
    "test_cases": 100,
    "success_rate": 0.72,
    "average_value": 2.8
  }
}
```

---

## 9. Podsumowanie Struktur Danych

| Kategoria | Główne Struktury | Cel |
|----------|------------------|-----|
| Dane Pierwotne | kursy_przygotowane.csv, wyniki | Surowa historia, dane wejściowe |
| Modele V2 | personality_vector, model_parameters | Konfiguracja i parametry modeli |
| Świecie V3 | world_data, world_memory, metadata | Wiedza o światach i wzorcach |
| Agenci V4 | personality_vector, emotional_parameters, trust_memory | Konfiguracja i stan agentów |
| Pamięć | agent_memory, global_memory, private_notebook | Przechowywanie doświadczeń |
| Strategie | strategy_object, experience_trace | Definicja i historia strategii |
| Laboratoria | decision_lab, group_lab, coupon_lab, strategy_lab | Eksperymenty i analiza |

 **Totalne Ilości:**
- Parametry Osobowości: 8
- Parametry Emocjonalne: 5
- Kategorie Tagów: 7
- Typy Laboratoriów: 4
- Etapy Cyklu Życia: 10
- Poziomy Rankingowe: 5 (A+, A, B, C, D)

---

**Status Dokumentu:** Kompletny  
**Wersja:** 4.0  
**Zgodność z Źródłami:** stuktura1.csv, stuktura2.csv, stuktura3.csv, stuktura4.csv  
**Ostatnia Aktualizacja:** 28.07.2026
