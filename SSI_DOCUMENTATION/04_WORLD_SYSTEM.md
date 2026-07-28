# SSI World System
## System Światów wiedzy Self Learning Intelligence Ecosystem

[TAGS: WORLD, ARCHITECTURE, DATA, V3, MEMORY, MODEL]

---

## 1. Wprowadzenie do Systemu Światów

**V3 World Knowledge Engine** jest sercem systemu SSI, odpowiedzialnym za **interpretację danych i budowę mapy wiedzy**. Każdy świat reprezentuje **odrębny sposób widzenia i analizowania rzeczywistości**.

### 1.1 Filozofia Światów

> **Jeden mecz posiada wiele możliwych reprezentacji.**
> **Nie ma jednej prawdy - są różne interpretacje świata.**

Klasyczny system AI szuka jednej odpowiedzi. SSI buduje **wiele światów**, z których każdy dostarcza **innej perspektywy** i **innych wzorców**.

### 1.2 Cel Systemu Światów

- **Interpretacja:** Każdy model z V2 tworzy własny świat
- **Dywersyfikacja:** Różne światy dostarczają różnych informacji
- **Synergia:** Połączenie światów zwiększa trafność
- **Odkrywanie:** Nowe światy odkrywają ukryte zależności
- **Ewolucja:** System stale buduje nowe światy

---

## 2. Architektura Systemu Światów

```
┌─────────────────────────────────────────────────────────────────┐
│                      V3 WORLD KNOWLEDGE ENGINE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────┐ ┌─────────────────────┐                 │
│  │   Input: V2 Models    │ │   Input: Data Layer  │                 │
│  │   - siec_01           │ │   - CSV Files        │                 │
│  │   - siec_02           │ │   - History          │                 │
│  │   - RandomForest      │ │   - Features         │                 │
│  └──────────┬───────────┘ └──────────┬───────────┘                 │
│              ↓                           ↓                          │
│              └───────────────────────────┬──────────────────┘        │
│                                          ↓                          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    ŚWIATY V3                                ││
│  │  ┌─────────────────────┐ ┌─────────────────────┐             ││
│  │  │   Świat Zmian        │ │   Świat Dynamiki     │             ││
│  │  │   Kursów             │ │   (Amplituda, Tempo)│             ││
│  │  └─────────────────────┘ └─────────────────────┘             ││
│  │  ┌─────────────────────┐ ┌─────────────────────┐             ││
│  │  │   Świat Klasyfikacji│ │   Świat Relacji      │             ││
│  │  │   (Logarytmy)        │ │   (Ratio)            │             ││
│  │  └─────────────────────┘ └─────────────────────┘             ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                PAMIĘCI ŚWIATÓW (World Memory)                 ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                METADANE (Metadata)                           ││
│  │  - Tagowanie (7 kategorii)                                      ││
│  │  - Zależności między światami                                   ││
│  │  - Analiza ekonomiczna                                         ││
│  │  - Wartość oczekiwana (EV)                                      ││
│  │  - Odwrócone wzorce                                            ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Output: Knowledge Map                              │
│  - ŚWIATY → CECHY → ZACHOWANIE → SKUTECZNOŚĆ → ZASTOSOWANIE         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Definicja Światów

### 3.1 Klasyfikacja Światów

**[WORLD]** **[ARCHITECTURE]**

| Świat | Identyfikator | Model Źródłowy | Typ Analizy | Cechy Główné |
|-------|--------------|-----------------|-------------|--------------|
| Świat Zmian Kursów | `swiat_zmian_kursow` | `siec_01_zmiana_kursow` | Analiza zmian | `zmiana_1`, `zmiana_X`, `zmiana_2` |
| Świat Amplitudy | `swiat_amplitudy` | `siec_02_amplituda` | Analiza zakresu | `amplituda_1`, `amplituda_X`, `amplituda_2` |
| Świat Tempo | `swiat_tempo` | `siec_03_tempo` | Analiza szybkości | `tempo_1`, `tempo_X`, `tempo_2` |
| Świat Synchronizacji | `swiat_synchronizacji` | `siec_04_synchronizacja` | Analiza koordynacji | `synchronizacja` |
| Świat Dynamiki | `swiat_dynamiki` | Multiple | Analiza kompleksowa | `amplituda`, `tempo`, `wahania`, `synchronizacja` |
| Świat Klasyfikacji | `swiat_klasyfikacji` | Klasyfikatory | Analiza logarytmiczna | `log_start`, `log_koniec` |
| Świat Relacji | `swiat_relacji` | - | Analiza stosunków | `ratio_1X`, `ratio_1_2`, `ratio_X2` |

### 3.2 Hierarchia Światów

```
Swiat Zmian Kursow (siec_01)
├── Świat Amplitudy (siec_02)
├── Świat Tempo (siec_03)
└── Świat Synchronizacji (siec_04)
    └── Świat Dynamiki (kombinacja)
        └── Świat Klasyfikacji (logarytmy)
            └── Świat Relacji (stosunki)
```

---

## 4. Szczegółowy Opis Światów

### 4.1 Świat Zmian Kursów

**[WORLD]** **[DATA]**

**Identyfikator:** `swiat_zmian_kursow`  
**Model Źródłowy:** `siec_01_zmiana_kursow`  
**Cel:** Analiza absolutnych zmian kursów bukmacherskich

#### Cechy:
- `zmiana_1` - Zmiana kursu na wygraną gospodarzy (1)
- `zmiana_X` - Zmiana kursu na remis (X)
- `zmiana_2` - Zmiana kursu na wygraną gości (2)

#### Zastosowanie:
- Wykrywanie trendów w zmianach kursów
- Identyfikacja kierunku ruchu kursów
- Analiza siły zmian dla różnych wyników

#### Przykładowe wzorce:
- Duża zmiana kursu 2 w ostatnim wcześniejszym może wskazywać na podwyższone prawdopodobieństwo wygranej gości
- Zmiana kursu 1 > 0.5 może sygnalizować nadchodzącą wygraną gospodarzy

### 4.2 Świat Amplitudy

**[WORLD]** **[DATA]**

**Identyfikator:** `swiat_amplitudy`  
**Model Źródłowy:** `siec_02_amplituda`  
**Cel:** Analiza zakresu (amplitudy) zmian kursów

#### Cechy:
- `amplituda_1` - Amplituda (zakres) zmian kursu 1
- `amplituda_X` - Amplituda zmian kursu X
- `amplituda_2` - Amplituda zmian kursu 2

#### Zastosowanie:
- Ocena stabilności/niestabilności kursów
- Identyfikacja meczy z dużą zmiennością
- Wykrywanie anomalii w zachowaniu kursów

#### Interpretacja:
- Mała amplituda = stabilny kurs = bezpieczniejsza predykcja
- Duża amplituda = zmienny kurs = większe ryzyko

### 4.3 Świat Tempo

**[WORLD]** **[DATA]**

**Identyfikator:** `swiat_tempo`  
**Model Źródłowy:** `siec_03_tempo`  
**Cel:** Analiza szybkości (tempo) zmian kursów

#### Cechy:
- `tempo_1` - Tempo (szybkość) zmian kursu 1
- `tempo_X` - Tempo zmian kursu X
- `tempo_2` - Tempo zmian kursu 2

#### Zastosowanie:
- Ocena dynamiki zmian kursów
- Identyfikacja gwałtownych ruchów
- Predykcja krótkoterminowych zmian

### 4.4 Świat Synchronizacji

**[WORLD]** **[DATA]**

**Identyfikator:** `swiat_synchronizacji`  
**Model Źródłowy:** `siec_04_synchronizacja`  
**Cel:** Analiza synchronizacji zmian między różnymi kursami

#### Cechy:
- `synchronizacja` - Poziom synchronizacji między zmianami kursów 1, X, 2
- `max_wahanie_1` - Maksymalne wahanie kursu 1
- `max_wahanie_X` - Maksymalne wahanie kursu X
- `max_wahanie_2` - Maksymalne wahanie kursu 2

#### Zastosowanie:
- Ocena koordynacji między kursami
- Wykrywanie rozbieżności między kursami
- Identyfikacja wzorców synchronizacji

#### Interpretacja:
- Synchronizacja = 1: Wszystkie kursy zmieniają się razem
- Synchronizacja = 0: Kursy zmieniają się niezależnie

### 4.5 Świat Klasyfikacji (Logarytmiczny)

**[WORLD]** **[DATA]**

**Identyfikator:** `swiat_klasyfikacji`  
**Model Źródłowy:** Klasyfikatory (RandomForest, etc.)  
**Cel:** Analiza logarytmicznych transformacji kursów

#### Cechy:
- `log_start_1` - Logarytm naturalny kursu 1 (początek)
- `log_start_X` - Logarytm naturalny kursu X (początek)
- `log_start_2` - Logarytm naturalny kursu 2 (początek)
- `log_koniec_1` - Logarytm naturalny kursu 1 (koniec)
- `log_koniec_X` - Logarytm naturalny kursu X (koniec)
- `log_koniec_2` - Logarytm naturalny kursu 2 (koniec)

#### Zastosowanie:
- Normalizacja danych kursowych
- Wykrywanie nieliniowych zależności
- Analiza proporcji między kursami

### 4.6 Świat Relacji

**[WORLD]** **[DATA]**

**Identyfikator:** `swiat_relacji`  
**Cel:** Analiza stosunków (ratio) między kursami

#### Cechy:
- `ratio_1X_start` - Stosunek kursu 1 do X (początek)
- `ratio_1_2_start` - Stosunek kursu 1 do 2 (początek)
- `ratio_X2_start` - Stosunek kursu X do 2 (początek)
- `ratio_1X_koniec` - Stosunek kursu 1 do X (koniec)
- `ratio_1_2_koniec` - Stosunek kursu 1 do 2 (koniec)
- `ratio_X2_koniec` - Stosunek kursu X do 2 (koniec)

#### Zastosowanie:
- Ocena względnych relacji między kursami
- Wykrywanie nierównowagi kursowej
- Identyfikacja wzorców relacyjnych

#### Interpretacja:
- `ratio_1_2` < 1: Kurs na gobarzy jest niższym niż na gości
- `ratio_1_2` > 1: Kurs na gospodarzy jest wyszym niż na gości

### 4.7 Świat Dynamiki (Kombinowany)

**[WORLD]** **[DATA]**

**Identyfikator:** `swiat_dynamiki`  
**Modele Źródłowe:** `siec_02_amplituda`, `siec_03_tempo`, `siec_04_synchronizacja`  
**Cel:** Kompleksowa analiza dynamiki kursów

#### Cechy (połączone):
- Cechy z światów: Amplituda, Tempo, Synchronizacja
- `synchronizacja` - Poziom synchronizacji
- `max_wahanie_1`, `max_wahanie_X`, `max_wahanie_2` - Maksymalne wahania

#### Zastosowanie:
- Holistyczna analiza zachowania kursów
- Wykrywanie złożonych wzorców dynamicznych
- Predykcja na podstawie wielu wymiarów

---

## 5. Metadane Światów

**[WORLD]** **[DATA]** **[MEMORY]**

Każdy świat posiada **metadane**, które opisują jego właściwości i zależności.

### 5.1 Struktura Metadanych

```json
{
  "world_id": "swiat_zmian_kursow",
  "world_name": "Świat Zmian Kursów",
  "version": "1.0",
  "source_model": "siec_01_zmiana_kursow",
  "model_type": "neural_network",
  "features": [
    {
      "feature_id": "zmiana_1",
      "name": "Zmiana kursu 1",
      "type": "float",
      "range": [-1.0, 1.0],
      "description": "Absolutna zmiana kursu na wygraną gospodarzy"
    },
    {
      "feature_id": "zmiana_X",
      "name": "Zmiana kursu X",
      "type": "float",
      "range": [-1.0, 1.0],
      "description": "Absolutna zmiana kursu na remis"
    },
    {
      "feature_id": "zmiana_2",
      "name": "Zmiana kursu 2",
      "type": "float",
      "range": [-1.0, 1.0],
      "description": "Absolutna zmiana kursu na wygraną gości"
    }
  ],
  "statistics": {
    "total_entries": 10000,
    "average_accuracy": 0.68,
    "stability": 0.75,
    "correlation_with_reality": 0.62
  },
  "dependencies": {
    "related_worlds": ["swiat_dynamiki", "swiat_klasyfikacji"],
    "influence_on": ["swiat_relacji"],
    "influenced_by": ["swiat_amplitudy"]
  },
  "tags": [
    "@zachowanie:zmienne",
    "@skutecznosc:srednia",
    "@zaleznosc: silna_z_swiatem_dynamiki"
  ],
  "performance": {
    "1X2_accuracy": 0.72,
    "exact_score_accuracy": 0.45,
    "economic_value": 0.80
  },
  "creation_date": "YYYY-MM-DD HH:MM:SS",
  "last_updated": "YYYY-MM-DD HH:MM:SS"
}
```

### 5.2 Kategorie Metadanych

| Kategoria | Opis | Przykład |
|----------|------|---------|
| **source** | Źródło światów | V2 Model Laboratory |
| **model** | Model źródłowy | siec_01_zmiana_kursow |
| **features** | Cechy światów | zmiana_1, zmiana_X, zmiana_2 |
| **statistics** | Statystyki efektywności | average_accuracy, stability |
| **dependencies** | Zależności z innymi światami | related_worlds, influence_on |
| **tags** | System tagowania | @zachowanie:zmienne |
| **performance** | Wydajność światów | 1X2_accuracy, economic_value |

---

## 6. System Tagowania Światów

**[WORLD]** **[DATA]** **[TAGGING]**

System tagowania umożliwia **kategoryzację i szybkie wyszukiwanie światów** na podstawie różnych kryteriów.

### 6.1 7 Haupt Kategorii Tagów

| Kategoria | Opis | Tagi z V3 | Nowe Tagi (V4) |
|----------|------|-----------|----------------|
| **wynik** | Wynik meczu | @wynik:1:0, @wynik:2:1 | @wynik:HighValue |
| **zachowanie** | Zachowanie modelu | @zachowanie:stabilne, @zachowanie:zmienne | @zachowanie:adaptacyjne |
| **skuteczność** | Skuteczność predykcji | @skutecznosc:wysoka, @skutecznosc:niska | @skutecznosc:A+, @skutecznosc:B |
| **odchylenia** | Odchylenia od normy | @odchylenie:duze, @odchylenie:male | @odchylenie:ekstremalne |
| **ekonomia** | Aspekty ekonomiczne | @ekonomia:wysoki_kurs | @ekonomia:wartosc_EV, @ekonomia: AKO |
| **zależności** | Zależności między światami | @zaleznosc:silna, @zaleznosc:słaba | @zaleznosc:kluczowa |
| **strategiczne** | Kategorie strategiczne | - | @strategia:bezpieczna, @strategia:wysokie_AKO, @strategia:odwrocony_wzorzec |

### 6.2 Zależności Między Światami

**[DEPENDENCY]**

Światy nie działają w izolacji. System identyfikuje **zależności i korelacje** między różnymi światami:

```
Świat Zmian Kursów
├── silna zależność → Świat Dynamiki
│   └── korelacja: 0.85
├── średnia zależność → Świat Klasyfikacji
│   └── korelacja: 0.65
└── słaba zależność → Świat Relacji
    └── korelacja: 0.40
```

**Typy Zależności:**
- **Silna (0.7-1.0):** Ściśle powiązane, wzajemnie się uzupełniają
- **Średnia (0.4-0.7):** Częściowa korelacja, przydatne do połączonej analizy
- **Słaba (0.0-0.4):** Mała korelacja, mogą być używane niezależnie

### 6.3 Odwrócone Wzorce

**[WORLD]** **[DATA]**

**Odwrócone wzorce** to sytuacje, w których model uważa za błędny według klasycznej oceny, ale posiada ukrytą wartość strageczną.

**Przykłady Odwróconych Wzorców:**
- Model przewiduje 1:0, a rzeczywistość to 0:1 → Może być sygnałem do strategii na gości
- Model z niską trafnością ogólną, ale wysoką trafnością na specificznym typie meczów
- Model, który często myli się w jednym kierunku, ale z wysoką powtarzalnością

**Tagowanie Odwróconych Wzorców:**
```
@odwrocony_wzorzec:model_predykcja_1_0_rzeczywistosc_0_1
@odwrocony_wzorzec:strategia_gości
@odwrocony_wzorzec:powtarzalny_błąd_jednokierunkowy
```

---

## 7. Analiza Ekonomiczna Światów

**[WORLD]** **[DATA]** **[ECONOMIC]**

Każdy świat jest analizowany pod kątem **wartości ekonomicznej** i **opłacalności decyzji**.

### 7.1 Wartość Oczekiwana (EV - Expected Value)

```
EV = (Prawdopodobieństwo ✓ Kurs) - Ryzyko
```

**Dla każdego świata obliczana jest:**
- Średnia wartość oczekiwana
- Maksymalna wartość oczekiwana
- Stabilność wartości oczekiwanej
- Ryzyko powiązane z danym światem

### 7.2 Metryki Ekonomiczne

| Metryka | Opis | Wzór |
|--------|------|------|
| **Trafność 1X2** | Procent poprawnych predykcji grupy 1/X/2 | (trafione / wszystkie) × 100 |
| **Wartość Średnia** | Średnia wartość wygranej | Σ(kurs × trafność) / n |
| **Powtarzalność** | Jak często dany wzorzec się powtarza | (wystąpienia / total) |
| **Stabilność** | Jak stabilne są wyniki w czasie | odchylenie_standardowe |
| **Ryzyko** | Poziom ryzyka związanego ze światem | funkcja(odchylenie, zmienność) |

### 7.3 Ranking Światów pod względem Wartości

```
1. Świat Relacji (ratio) - Wartość: 0.92
2. Świat Klasyfikacji (log) - Wartość: 0.88
3. Świat Dynamiki (amplituda+tempo+synch) - Wartość: 0.85
4. Świat Zmian Kursów - Wartość: 0.82
5. Świat Synchronizacji - Wartość: 0.78
6. Świat Amplitudy - Wartość: 0.75
```

---

## 8. Integracja z Innymi Modułami

### 8.1 Światy a V2 Model Laboratory

- **Zależność:** V2 → V3
- **Przepływ:** Modele z V2 tworzą światy w V3
- **1 Model = 1 Świat:** Każdy model z V2 generuje swój własny świat wiedzy
- **Wyjątki:** Niektóre światy (jak Świat Dynamiki) mogą łączyć wiele modeli

### 8.2 Światy a V4 Agent Evolution

- V4 korzysta ze światów dostarczonych przez V3
- Agenci wybierają, które światy wykorzystać
- Agenci mogą łączyć wiele światów
- Agenci odkrywają nowe zastosowania dla istniejących światów

### 8.3 Światy a Memory System

- Każdy świat posiada swoją własną pamięć (World Memory)
- Pamięci światów są łączone w Global Memory
- System tagowania ułatwia nawigację między światami

### 8.4 Światy a Strategy System

- Strategie są budowane na podstawie jednego lub wielu światów
- World Reference w StrategyObject wskazuje na świat źródłowy
- Agenci testują, które światy najlepiej współpracują

---

## 9. Podsumowanie

| Świat | Model | Główne Cechy | Zastosowanie | Wartość Ekonomiczna |
|-------|-------|--------------|--------------|---------------------|
| Świat Zmian Kursów | siec_01 | zmiana_1, zmiana_X, zmiana_2 | Analiza trendów | 0.82 |
| Świat Amplitudy | siec_02 | amplituda_1, amplituda_X, amplituda_2 | Ocena stabilności | 0.75 |
| Świat Tempo | siec_03 | tempo_1, tempo_X, tempo_2 | Analiza szybkości | 0.78 |
| Świat Synchronizacji | siec_04 | synchronizacja, max_wahanie | Analiza koordynacji | 0.85 |
| Świat Dynamiki | Multiple | amplituda, tempo, synchronizacja | Analiza kompleksowa | 0.85 |
| Świat Klasyfikacji | Klasyfikatory | log_start, log_koniec | Analiza logarytmiczna | 0.88 |
| Świat Relacji | - | ratio_1X, ratio_1_2, ratio_X2 | Analiza stosunków | 0.92 |

**Kluczowe Statystyki:**
- Liczba światów: 7 (podstawowych)
- Liczba cech: 27 (łącznie we wszystkich światach)
- Liczba kategorii tagów: 7
- Liczba modeli źródłowych: 4 + klasyfikatory

---

**Status Dokumentu:** Kompletny  
**Wersja:** 4.0  
**Zgodność z Źródłami:** stuktura1.csv, stuktura2.csv, stuktura3.csv, stuktura4.csv  
**Ostatnia Aktualizacja:** 28.07.2026
