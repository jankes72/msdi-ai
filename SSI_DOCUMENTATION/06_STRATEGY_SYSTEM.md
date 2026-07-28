# SSI Strategy System
## System Strategii Ewolucyjnych Self Learning Intelligence Ecosystem

[TAGS: STRATEGY, EVOLUTION, AGENT, WORLD, MEMORY, OBJECT]

---

## 1. Wprowadzenie do Systemu Strategii

**Strategy Intelligence Engine** jest **centralnym mechanizmem** systemu SSI, odpowiedzialnym za **tworzenie, testowanie, ewoluowanie i zarządzanie strategiami decyzyjnymi**.

### 1.1 Nowatorskie Podejście do Strategii

**WAŻNA ZASADA:**
> **Strategia NIE jest tekstem.**
> **Strategia jest obiektem systemowym.**

Klasyczne systemy traktują strategię jako opis tekstowy. W SSI, **strategia jest autonomicznym obiektem z własnym cyklem życia, historią, wartością i możliwością odtworzenia**.

### 1.2 Rola Strategii w SSI

Strategie w SSI pełnią **kluczową rolę** w procesie decyzyjnym:

- Agenci **wykorzystują** strategie do podejmowania decyzji
- Strategie **ewoluują** na podstawie wyników
- System ** TESTuje** nowe strategie w laboratoriach
- Historyczne strategie **zachowują** swoją wiedzę w Experience Trace

### 1.3 Filozofia Ewolucji Strategii

```
STRATEGIA NIE JEST STATYCZNA
↓
STRATEGIA SIĘ ROZWIJA
↓
STRATEGIA UCZY SIĘ NA BŁĘDACH
↓
STRATEGIA PRZYSTOSOWUJE SIĘ DO ZMIAN
```

---

## 2. StrategyObject - Obiekt Strategii

**[STRATEGY]** **[DATA]** **[OBJECT]**

### 2.1 Struktura StrategyObject

**strategia jest obiektem systemowym z gehörten atrybutami:**

```json
{
  "object_type": "StrategyObject",
  "strategy_id": "strategy_001",
  "version": "1.0",
  
  // Referencje
  "world_reference": "swiat_zmian_kursow",
  "model_reference": "siec_01_zmiana_kursow",
  
  // Definicja strategii
  "name": "Analiza stabilnych wzorców zmian kursów",
  "description": "Strategia oparta na świecie zmian kursów, szukająca stabilnych wzorców",
  
  // Cechy i dane
  "features": [
    "zmiana_1",
    "zmiana_X", 
    "zmiana_2",
    "amplituda_1",
    "tempo_1"
  ],
  
  "training_data": {
    "source": "dataBase_futbol_trend.csv",
    "period": {
      "start": "2023-01-01",
      "end": "2024-12-31"
    },
    "sample_size": 10000,
    "split": {
      "training": 0.60,
      "validation": 0.20,
      "observation": 0.20
    },
    "features_used": 27,
    "target_variable": "result_1X2"
  },
  
  // Mechanizm predykcji
  "prediction_generator": {
    "type": "neural_network",
    "algorithm": "siec_01_zmiana_kursow",
    "parameters": {
      "hidden_layers": 3,
      "neurons_per_layer": [64, 32, 16],
      "activation_function": "relu",
      "learning_rate": 0.001,
      "batch_size": 32,
      "epochs": 100
    },
    "implementation_reference": "models.siec_01_zmiana_kursow",
    "prediction_method": "classification_1X2"
  },
  
  // Konfiguracja strategii
  "parameters": {
    "risk_level": "MEDIUM",
    "min_odds_threshold": 2.0,
    "max_odds_threshold": 10.0,
    "confidence_threshold": 0.75,
    "min_sample_size": 100,
    "max_volatility": 0.30,
    "preferred_outcome": "2",
    "time_horizon": "short_term"
  },
  
  // Historia i wyniki
  "results_history": [
    {
      "decision_id": "dec_001",
      "timestamp": "2024-07-01 14:30:00",
      "match": "Team A - Team B",
      "prediction": "2",
      "actual_result": "2",
      "outcome": "CORRECT",
      "odds": 3.2,
      "confidence": 0.85,
      "value": 3.2,
      "contribution_to_accuracy": 0.85
    },
    {
      "decision_id": "dec_002",
      "timestamp": "2024-07-01 16:45:00",
      "match": "Team C - Team D",
      "prediction": "1",
      "actual_result": "X",
      "outcome": "INCORRECT",
      "odds": 2.8,
      "confidence": 0.65,
      "value": 0.0,
      "contribution_to_accuracy": -0.35
    }
  ],
  
  // Metryki efektywności
  "performance_metrics": {
    "total_decisions": 150,
    "correct_predictions": 95,
    "incorrect_predictions": 55,
    "accuracy": 0.633,
    "success_rate": 0.633,
    "average_odds": 3.15,
    "average_value": 2.05,
    "sharpe_ratio": 1.25,
    "max_drawdown": 0.25,
    "stability": 0.78,
    "repeatability": 0.72
  },
  
  // Wartość i ranking
  "value_score": 0.82,
  "ranking": "A",
  "economic_value": 0.88,
  
  // Status i cykl życia
  "status": "ACTIVE",
  "life_cycle_stage": "ACTIVE",
  "created_at": "2024-06-01 10:00:00",
  "updated_at": "2024-07-28 14:30:00",
  "last_used": "2024-07-28 14:30:00",
  
  // Powiązania
  "created_by": "agent_001",
  "used_by_agents": ["agent_001", "agent_002"],
  "related_strategies": ["strategy_002", "strategy_005"],
  "parent_strategy": null,
  "child_strategies": ["strategy_015", "strategy_022"]
}
```

### 2.2 Atrybuty StrategyObject

| Atrybut | Typ | Opis | Wymagany |
|---------|-----|------|----------|
| `strategy_id` | string | Unikalny identyfikator strategii | ✅ |
| `world_reference` | string | Świat, dla którego działa strategia | ✅ |
| `model_reference` | string | Model wykorzystany przez strategię | ✅ |
| `features` | array | Zestaw wykorzystywanych cech | ✅ |
| `training_data` | object | Dane wykorzystane do nauki | ✅ |
| `prediction_generator` | object | Mechanizm generowania predykcji | ✅ |
| `parameters` | object | Konfiguracja strategii | ✅ |
| `results_history` | array | Historia wyników | ✅ |
| `value_score` | float | Aktualna wartość strategii (0-1) | ✅ |
| `status` | string | Aktualny etap życia | ✅ |

### 2.3 Typy Strategii

| Typ | Opis | Charakterystyka |
|-----|------|----------------|
| **Podstawowa** | Strategia oparta na jednym świecie | Prosta, jednośladowa |
| **Kombinowana** | Strategia łącząca wiele światów | Złożona, wielowymiarowa |
| **Eksperymentalna** | Nowo utworzona strategia w fazie testów | Wysokie ryzyko, potencjalnie wysoka nagroda |
| **Adaptacyjna** | Strategia dostosowująca się do warunków |Dynamiczna, elastyczna |
| **Odwrócona** | Strategia wykorzystująca odwrócone wzorce | Niestandardowa, innowacyjna |

---

## 3. Generator Strategii

**[STRATEGY]** **[COMPONENT]** **[EVOLUTION]**

### 3.1 Strategy Generator

- **ID:** `STRATEGY_GENERATOR`
- **Typ:** `Evolutionary Creation Engine`
- **Rola:** Tworzenie nowych strategii na podstawie doświadczeń systemu

### 3.2 Wejścia Generatora

Generator strategii wykorzystuje **6 źródeł wiedzy**:

1. **Stare strategie** - Istniejące strategie jako baza
2. **Wyniki** - Historia wyników i efektów
3. **Spotkania agentów** - Wymiana wiedzy między agentami
4. **Obserwacje** - Nowe wzorce i zjawiska
5. **Błędy** - Analiza niepowodzeń
6. **Odkryte wzorce** - Nowe zależności w danych

### 3.3 Proces Tworzenia Nowej Strategii

```
ISTNIEJĄCA STRATEGIA
    +
NOWA WIEDZA
    +
DOŚWIADCZENIE
        ↓
    NOWA STRATEGIA
```

**Szczegółowy Przebieg:**
```
1. Analiza istniejących strategii
   ↓
2. Identyfikacja luk i możliwości polepszenia
   ↓
3. Połączenie z nową wiedzą (nowe wzorce, obserwacje)
   ↓
4. Wykorzystanie doświadczenia (błędy, sukcesy)
   ↓
5. Generowanie nowej konfiguracji
   ↓
6. Walidacja i testy wstępne
   ↓
7. Utworzenie nowego StrategyObject
```

### 3.4 Przykład Powstania Nowej Strategii

**Bazowa Strategia:** `strategy_001` - Analiza zmian kursów (accuracy: 0.65)  
**Nowa Wiedza:** Odkryty wzorzec: `zmiana_2 > 0.5 → 2` (accuracy: 0.72)  
**Doświadczenie:** Błędy w sytuacjach wysokiej zmienności  

**Nowa Strategia:** `strategy_015`
- **Źródło:** strategy_001 + nowy wzorzec
- **Zmiany:** Dodanie cechy `zmiana_2 > 0.5` jako filtra
- **Oczekiwany efekt:** Zwiększenie accuracy do 0.70-0.75

---

## 4. Cykl Życia Strategii

**[STRATEGY]** **[EVOLUTION]**

### 4.1 10 Etapów Cyklu Życia

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
RANKING (RANKING) - Ocena i przydzielenie poziomu (A+/A/B/C/D)
    ↓
AKTYWNE UŻYCIE (ACTIVE) - Strategia jest wykorzystywana w procesach decyzyjnych
    ↓
SPADEK WARTOŚCI (DECLINING) - Strategia traci wartość lub przestaje pasować do aktualnych warunków
    ↓
ARCHIWUM (ARCHIVED) - Strategia nie jest aktywnie używana, ale pozostaje w historii systemu
```

### 4.2 Opis Etapów

#### 1. Narodziny (Birth)
- **Czas trwania:** Chwila
- **Cecha:** Powstaje nowy pomysł na strategię
- **Akcja:** Inicjalizacja StrategyObject

#### 2. Nowa Strategia (New)
- **Czas trwania:** Krótki okres (tygodnie)
- **Cecha:** Strategia nie posiada historii
- **Akcja:** Wstępne testy, konfiguracja

#### 3. Test (Testing)
- **Czas trwania:** 1-4 tygodnie
- **Cecha:** Strategia przechodzi intensywne eksperymenty
- **Akcja:** Walidacja na historycznych i bieżących danych

#### 4. Dojrzewanie (Maturing)
- **Czas trwania:** 1-3 miesiące
- **Cecha:** Strategia zdobywa doświadczenie
- **Akcja:** Stopniowe zwiększanie zaufania

#### 5. Obserwacja (Observation)
- **Czas trwania:** Ciągła
- **Cecha:** Strategia jest monitorowana w warunkach rzeczywistych
- **Akcja:** Zbiór danych do oceny

#### 6. Analiza (Analysis)
- **Czas trwania:** Okresowa
- **Cecha:** Głęboka ocena skuteczności
- **Akcja:** Analiza wzorców, odiochyleń, stabilności

#### 7. Ranking (Ranking)
- **Czas trwania:** Okresowa (co miesiąc)
- **Cecha:** Przydzielenie poziomu ligowego
- **Akcja:** Klasyfikacja i ocena wartości

#### 8. Aktywne Użycie (Active)
- **Czas trwania:** Do utraty skuteczności
- **Cecha:** Strategia jest aktywnie wykorzystywana
- **Akcja:** Regularne użycie w decyzjach

#### 9. Spadek Wartości (Declining)
- **Czas trwania:** Zależy od tempa spadku
- **Cecha:** Strategia traci na skuteczności
- **Akcja:** Stopniowe wycofywanie

#### 10. Archiwum (Archived)
- **Czas trwania:** Wieczysty
- **Cecha:** Strategia nie jest aktywnie używana
- **Akcja:** Zachowanie w Experience Trace

### 4.3 Mechanizmy Przejścia Między Etapami

**Awans (Promotion):**
- Dobre wyniki (accuracy > 70%)
- Stabilność (małe odchylenia)
- Powtarzalność (spójne wyniki)
- Zgodność z rzeczywistością

**Spadek (Degradation):**
- Utrata skuteczności (accuracy < 50%)
- Zmiana warunków rynkowych
- Powtarzalne błędy
- Brak przewagi nad innymi strategiami

---

## 5. System Ligi Strategii (Ranking)

**[STRATEGY]** **[DATA]**

### 5.1 Poziomy Rankingowe

| Poziom | Opis | Charakterystyka | Waga w Systemie |
|--------|------|----------------|-----------------|
| **A+** | Najwyższa skuteczność | Strategie kluczowe, sprawdzone w wielu warunkach | 1.0 |
| **A** | Bardzo wartościowe | Strategie o wysokiej skuteczności | 0.9 |
| **B** | Użyteczne | Strategie wymagające dalszej obserwacji | 0.7 |
| **C** | Eksperymentalne | Nowe strategie, w fazie testów | 0.5 |
| **D** | Niska wartość | Strategie o niskiej aktualnej wartości | 0.3 |

### 5.2 Kryteria Rankingowe

**Wzór Oceny:**
```
RANKING_SCORE = 
  (accuracy × 0.40) +
  (stability × 0.25) +
  (repeatability × 0.20) +
  (economic_value × 0.15)
```

**Progi:**
- A+ ≥ 0.90
- A ≥ 0.80
- B ≥ 0.65
- C ≥ 0.50
- D < 0.50

### 5.3 Cóż się dzieje na Poszczególnych Poziomach

| Poziom | Aktywne Użycie | Testowanie | Monitorowanie | Archiwizacja |
|--------|----------------|------------|--------------|--------------|
| A+ | ✅ Pełne | ❌ | ✅ Ciągłe | ❌ |
| A | ✅ Pełne | ❌ | ✅ Ciągłe | ❌ |
| B | ✅ Ograniczone | ✅ Okresowe | ✅ Ciągłe | ❌ |
| C | ❌ | ✅ Intensywne | ✅ Okresowe | ❌ |
| D | ❌ | ❌ | ✅ Minimalne | ✅ |

---

## 6. Experience Trace - Ślad Doświadczenia

**[STRATEGY]** **[MEMORY]** **[EVOLUTION]**

### 6.1 Zasada Experience Trace

> **Strategia nigdy nie jest całkowicie usuwana.**
> **Usuwane jest tylko aktywne wykorzystanie.**
> **Pozostaje pełny ślad doświadczenia w systemie.**

### 6.2 Zawartość Experience Trace

```json
{
  "experience_trace_id": "trace_strategy_001",
  "trace_type": "STRATEGY_ARCHIVE",
  "original_strategy_id": "strategy_001",
  "original_name": "Analiza zmian kursów v1.0",
  
  // Pełna historia
  "full_history": {
    "creation": {
      "timestamp": "2024-01-15 10:00:00",
      "creator_agent": "agent_001",
      "initial_parameters": { ... },
      "creation_reason": "Odkryty nowy wzorzec w świecie zmian kursów"
    },
    "usage": {
      "total_usages": 2450,
      "successful_usages": 1620,
      "failed_usages": 830,
      "success_rate": 0.661,
      "best_period": {
        "start": "2024-03-01",
        "end": "2024-05-30",
        "success_rate": 0.745
      },
      "worst_period": {
        "start": "2024-06-15",
        "end": "2024-07-15",
        "success_rate": 0.521
      }
    },
    "evolution": {
      "versions": ["v1.0", "v1.1", "v1.2", "v1.3"],
      "modifications": [
        {
          "version": "v1.1",
          "date": "2024-02-20",
          "changes": "Dodano filtr na minimalny kurs 2.5",
          "reason": "Zbyt wiele bledow przy niskich kursach",
          "impact": "+0.08 accuracy"
        },
        {
          "version": "v1.2",
          "date": "2024-04-01",
          "changes": "Zwiększono wagę cechy zmiana_2",
          "reason": "Odkryto siląp korelację z wynikiem 2",
          "impact": "+0.05 accuracy"
        }
      ]
    }
  },
  
  // Dane wejściowe
  "input_data": {
    "primary_source": "dataBase_futbol_trend.csv",
    "secondary_sources": ["dataBase_futbol_popularne_trend.csv"],
    "features": [
      "zmiana_1", "zmiana_X", "zmiana_2",
      "amplituda_1", "amplituda_X", "amplituda_2",
      "tempo_1", "tempo_X", "tempo_2"
    ],
    "period": {
      "start": "2023-01-01",
      "end": "2024-07-28"
    },
    "sample_size": 15648
  },
  
  // Model użyty
  "model_used": {
    "model_id": "siec_01_zmiana_kursow",
    "model_type": "neural_network",
    "version": "v2.3",
    "parameters": { ... },
    "architecture": "3 hidden layers: 64-32-16"
  },
  
  // Wyniki i statystyki
  "results": [
    {"decision": "2", "actual": "2", "outcome": "CORRECT", "value": 3.2, "timestamp": "..."},
    {"decision": "1", "actual": "X", "outcome": "INCORRECT", "value": 0.0, "timestamp": "..."}
  ],
  "statistics": {
    "total_decisions": 2450,
    "correct": 1620,
    "incorrect": 830,
    "accuracy": 0.661,
    "average_odds": 3.45,
    "economic_value": 2.15
  },
  
  // Powód archiwizacji
  "archival_reason": "Utrata skuteczności spowodowana zmianą warunków rynkowych - nowy sezon z innymi charakterystykami meczów",
  "degradation_analysis": {
    "primary_cause": "market_condition_change",
    "secondary_causes": ["increased_volatility", "new_team_dynamics"],
    "degradation_rate": 0.15,
    "degradation_period": "2024-06-01 to 2024-07-28"
  },
  
  // Ukryta wartość
  "hidden_value": "Strategia może działać w warunkach wysokiej zmienności kursów - warto przetestować ponownie przyvolatility > 0.35",
  "restoration_potential": 0.75,
  "restoration_conditions": [
    "market_volatility > 0.35",
    "min_odds < 3.0",
    "season_type == 'transition'"
  ],
  
  // informacje archiwalne
  "archived_at": "2024-07-28 15:30:00",
  "archived_by": "strategy_evolution_engine",
  "restoration_possible": true,
  "last_verified": "2024-07-28 15:30:00"
}
```

### 6.3 Korzyści Experience Trace

1. **Pełna Odwracalność**
   - System może zrekonstruować każdą strategię
   - Możliwe przywrócenie w nowych warunkach

2. **Historyczna Analiza**
   - Badanie ewolucji strategii w czasie
   - Identyfikacja powodów sukcesów i porażek

3. **Odkrywanie Ukrytej Wartości**
   - Strategie archiwalne mogą okazać się wartościowe w nowych warunkach
   - Możliwość adaptacji do zmienionego środowiska

4. **Unikanie Powtarzania Błędów**
   - Historia błędów dostępna dla nowych agentów
   - System uczy się na błędach przeszłości

5. **Ewolucyjne Uczenie**
   - Nowe strategie korzystają z doświadczeń archiwalnych
   - Kontynuacja rozwoju na podstawie historii

---

## 7. System Odtwarzalności Strategii

**[STRATEGY]** **[COMPONENT]**

### 7.1 Strategy Reproduction System

- **ID:** `STRATEGY_REPRODUCTION_SYSTEM`
- **Typ:** `Strategy Reconstruction Mechanism`
- **Rola:** Zapewnienie, że każda strategia jest odtwarzalna

### 7.2 Zasady Odtwarzalności

**Każda strategia musi być odtwarzalna. System musi znać:**
1. Jak ją utworzyć
2. Jak ją wyszkolić
3. Jakich danych użyć
4. Jak wygenerować predykcję

### 7.3 Proces Odtworzenia

```
STRATEGY_OBJECT (z archiwum)
    ↓
LOAD PARAMETERS (z Experience Trace)
    ↓
LOAD DATA (źródła i okres)
    ↓
TRAIN MODEL (z parametrami)
    ↓
GENERATE PREDICTION (test)
    ↓
COMPARE RESULT (walidacja)
```

### 7.4 Korzyści Odtwarzalności

- **Kontrola jakości:** Możliwość weryfikacji historycznych decyzji
- **Eksperymenty:** Testowanie starych strategii w nowych warunkach
- **Ewolucja:** Rozwijanie istniejących strategii
- **Archiwizacja:** Zachowanie wiedzy dla przyszłych pokoleń agentów

---

## 8. Laboratoria Strategii

**[STRATEGY]** **[LABORATORIES]**

### 8.1 Strategy Laboratory

**Cel:** Tworzenie, testowanie i rozwój strategii

**Funkcje:**
- Tworzenie nowych StrategyObject
- Testowanie strategii na historycznych i bieżących danych
- Optymalizacja parametrów strategii
- Walidacja i ocena skuteczności
- Ewolucja istniejących strategii

### 8.2 Proces w Laboratorium Strategii

```
WYBÓR CELOWEJ STRATEGII
    ↓
KONFIGURACJA TESTU
    ↓
PRZYGOTOWANIE DANYCH
    ↓
URUCHOMIENIE EKSPERYMENTU
    ↓
ZBIÓR WYNIKÓW
    ↓
ANALIZA SKUTECZNOŚCI
    ↓
OCENA I KLASYFIKACJA
```

### 8.3 Typy Eksperymentów

| Typ | Opis | Cel |
|-----|------|-----|
| **Podstawowy** | Test strategii na standardowych danych | Walidacja bazowa |
| **Optymalizacyjny** | Poszukiwanie optymalnych parametrów | Maksymalizacja efektywności |
| **Porównawczy** | Porównanie wielu strategii | Ocena względna |
| **Ewolucyjny** | Testowanie nowych wersji | Rozwój strategii |
| **Historyczny** | Test na historycznych okresach | Sprawdzenie stabilności |

---

## 9. Integracja z Innymi Modułami

### 9.1 Strategie a Światy (V3)

- **Zależność:** Strategie korzystają ze światów V3
- **World Reference:** Każda strategia wiąże się z jednym lub wieloma światami
- **Feature Selection:** Cechy strategii pochodzą ze światów

### 9.2 Strategie a Agenci (V4)

- **Tworzenie:** Agenci tworzą nowe strategie
- **Wykorzystanie:** Agenci używają strategii w decyzjach
- **Ewolucja:** Agenci wpływają na rozwój strategii
- ** ocenianie:** Agenci oceniają skuteczność strategii

### 9.3 Strategie a Pamięć

- **Experience Trace:** Historia strategii zachowana w pamięci
- **Global Memory:** Sprawdzone strategie dostępne dla wszystkich
- **Agent Memory:** Strategie powiązane z konkretnymi agentami

### 9.4 Strategie a Laboratoria Decyzyjne

- **Testowanie:** Strategie testowane w laboratoriach
- **Optymalizacja:** Laboratoria pomagają w doskonaleniu strategii
- **Walidacja:** Laboratoria weryfikują skuteczność strategii

---

## 10. Podsumowanie Systemu Strategii

| Komponent | Typ | Rola | Status |
|-----------|-----|------|--------|
| StrategyObject | [DATA] | Obiekt strategii | ✅ Zdefiniowany |
| Strategy Generator | [COMPONENT] | Tworzenie strategii | ✅ Zaimplementowany (projekt) |
| Strategy Life Cycle | [EVOLUTION] | Cykl życia strategii | ✅ Zdefiniowany |
| Strategy League System | [DATA] | System rankingowy | ✅ Zaimplementowany (projekt) |
| Strategy Archive System | [MEMORY] | Archiwizacja strategii | ✅ Zaimplementowany (projekt) |
| Experience Trace | [MEMORY] | Ślad doświadczenia | ✅ Zaimplementowany (projekt) |
| Strategy Reproduction | [COMPONENT] | Odtwarzalność strategii | ✅ Zdefiniowany |
| Strategy Laboratory | [LABORATORIES] | Testowanie strategii | ✅ Zaimplementowany (projekt) |

**Statystyki:**
- Liczba etapiw cykli życia: 10
- Liczba poziomów rankingowych: 5 (A+, A, B, C, D)
- Liczba typów strategii: 5
- Zasada: Nigdy nie usuwaj, zawsze archiwizuj

**Kluczowe Zasady:**
1. Strategia jest obiektem systemowym
2. Strategia posiada własny cykl życia
3. Strategia ewoluuje na podstawie doświadczenia
4. Strategia nigdy nie jest całkowicie usuwana
5. Strategia musi być odtwarzalna

---

## 11. Wzór na Wartość Strategii

**Ostateczna formuła oceny strategii:**

```
WARTOŚĆ STRATEGII = 
  trafność × waga_trafności +
  kurs × waga_kursu +
  powtarzalność × waga_powtarzalności +
  stabilność × waga_stabilności -
  ryzyko × waga_ryzyka

Gdzie:
- trafność = accuracy (0-1)
- kurs = średnia wartość kursów
- powtarzalność = (liczba powtórzeń / total)
- stabilność = 1 / odchylenie_standardowe
- ryzyko = funkcja strat i zmienności
```

**Przykład Obliczenia:**
```
Strategia A:
- trafność: 0.75
- kurs: 3.0
- powtarzalność: 0.80
- stabilność: 0.85
- ryzyko: 0.20

Wartość = (0.75 × 0.40) + (3.0 × 0.25) + (0.80 × 0.20) + (0.85 × 0.15) - (0.20 × 0.10)
       = 0.30 + 0.75 + 0.16 + 0.1275 - 0.02
       = 1.3175 ( skala normalizowana do 0-1: 0.82)
```

---

**Status Dokumentu:** Kompletny  
**Wersja:** 4.0  
**Zgodność z Źródłami:** stuktura1.csv, stuktura2.csv, stuktura3.csv, stuktura4.csv  
**Ostatnia Aktualizacja:** 28.07.2026
