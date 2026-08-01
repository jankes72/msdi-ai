# SSI V5 PHASE 2: DATA SOURCE ARCHITECTURE

**Sprint:** 12+ (Phase 2 Foundation)
**Data:** 2026-08-01
**Wersja:** 1.0.0
**Status:** Draft / Completed
**Autor:** Glowny Architekt SSI V5

---

## SPIS TRESCI

1. [DATA ARCHITECTURE OVERVIEW](#1-data-architecture-overview)
2. [LAYER 1 — SOURCE DATA](#2-layer-1--source-data)
3. [LAYER 2 — LABORATORY DATA LAYER](#3-layer-2--laboratory-data-layer)
4. [LAYER 3 — MODEL DATA LAYER](#4-layer-3--model-data-layer)
5. [LAYER 4 — WORLD MEMORY DATA LAYER](#5-layer-4--world-memory-data-layer)
6. [LAYER 5 — FEATURE KNOWLEDGE LAYER](#6-layer-5--feature-knowledge-layer)
7. [LAYER 6 — PREDICTION DATA LAYER](#7-layer-6--prediction-data-layer)
8. [DATA OWNERSHIP MODEL](#8-data-ownership-model)
9. [DATA FLOW DIAGRAM](#9-data-flow-diagram)
10. [DATA INTEGRITY RULES](#10-data-integrity-rules)

---

## 1. DATA ARCHITECTURE OVERVIEW

### 1.1 Hierarchia Warstw Danych

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SSI V5 PHASE 2 DATA ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    LAYER 1: SOURCE DATA                           │   │
│  │  ┌─────────────────┐  ┌─────────────────┐                       │   │
│  │  │  wyniki.csv      │  │ kursy_przygotow │                       │   │
│  │  │  (IMMUTABLE)     │  │ ane.csv          │                       │   │
│  │  └─────────────────┘  └─────────────────┘                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                             │                                           │
│                             ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    LAYER 2: LABORATORY DATA                        │   │
│  │  ┌─────────────────────────────┐                              │   │
│  │  │ dataBase_futbol_trend/        │                              │   │
│  │  │  ├── siec_01_zmiana_kursow │                              │   │
│  │  │  ├── siec_02_amplituda     │                              │   │
│  │  │  └── ... (siec_03-11)      │                              │   │
│  │  └─────────────────────────────┘                              │   │
│  │  ┌─────────────────────────────┐                              │   │
│  │  │ kursy_przygotowane/          │                              │   │
│  │  │  ├── siec_01_start_kursow  │                              │   │
│  │  │  └── ... (siec_02-04)      │                              │   │
│  │  └─────────────────────────────┘                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                             │                                           │
│                             ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                  LAYER 3: MODEL DATA LAYER                       │   │
│  │  ┌─────────────────────────────────────────────────────────┐   │   │
│  │  │ modele_dataBase_futbol_trend/                             │   │   │
│  │  │  └── [11 modeli] x (obserwacja + ocena + ... )          │   │   │
│  │  └─────────────────────────────────────────────────────────┘   │   │
│  │  ┌─────────────────────────────────────────────────────────┐   │   │
│  │  │ modele_kursy_przygotowane/                                │   │   │
│  │  │  └── [4 modele] x (obserwacja + ocena + ... )           │   │   │
│  │  └─────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                             │                                           │
│                             ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                LAYER 4: WORLD MEMORY DATA LAYER                   │   │
│  │  ┌─────────────────────────────────────────────────────────┐   │   │
│  │  │ dopasowanie_swiata_mozg_kursy_przygotowane.csv            │   │   │
│  │  │ dopasowanie_swiata_kod_dataBase_futbol_trend.csv          │   │   │
│  │  │ dopasowanie_swiata_kod_dataBase_futbol_trend_klasyfikator  │   │   │
│  │  └─────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                             │                                           │
│                             ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │               LAYER 5: FEATURE KNOWLEDGE LAYER                   │   │
│  │  ┌─────────────────────────────────────────────────────────┐   │   │
│  │  │ ranking_cech/                                              │   │   │
│  │  │  └── [Johnson Metrics: korelacja, RF, DC, sila]             │   │   │
│  │  └─────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                             │                                           │
│                             ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              LAYER 6: PREDICTION DATA LAYER                       │   │
│  │  ┌─────────────────────────────────────────────────────────┐   │   │
│  │  │ predykcje/predykcja_grupy.csv                              │   │   │
│  │  └─────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Zasada Fundamentalna

**DATA → ANALYSIS → KNOWLEDGE → TEACHER MODELS → AGENTS → DECISION → FEEDBACK → MEMORY UPDATE**

Kazda warstwa danych stanowia **fundament** dla kolejnej warstwy **wiedzy i przetwarzania**.

### 1.3 Podzial Roli

| Warstwa | Rola | Typ Danych | Czy Zmienialne |
|---------|------|------------|----------------|
| Source Data | Dane Pierwotne | Surowa | ❌ NIE (IMMUTABLE) |
| Laboratory Data | Dane Analizowane | Przetworzona | ❌ NIE (tylko przez Laboratorium) |
| Model Data | Dane Modeli | Specyficzna | ✅ TAK (przez wlasne moduly) |
| World Memory | Pamięć Historyczna | Wzorce | ✅ TAK (przez Laboratory Teacher) |
| Feature Knowledge | Wiedza o Cechach | Rankingi | ✅ TAK (przez Feedback Loop) |
| Prediction Data | Wyniki Predykcji | Decyzje | ✅ TAK (przez Teacher Models) |

---

## 2. LAYER 1 — SOURCE DATA

### 2.1 Dane Pierwotne

**⚠️ ZASADA: source data sa IMMUTABLE (niezmienialne)**

Brak modyfikacji dopuszczalny. Kazda zmiana wymaga tworzenia nowej wersji pliku.

---

#### 2.1.1 wyniki.csv

**INPUT:**
- **Zrodlo:** System zewnetrzny (eksploracja wynikow meczy)
- **Format:** UTF-8
- **Separator:** `;`
- **Format wyniku:** `GOSPODARZE:GOSCIE`

**PROCESS:**
1. System zewnetrzny generuje plik z wynikami meczy
2. Plik jest przekazywany do systemu SSI V5
3. Data Layer (V2 Collector) odczytuje i waliduje plik
4. Feedback Loop wykorzystuje dane do porównania z predykcjami

**OUTPUT:**
- Zrodlo prawdy dla Feedback Loop
- Wejscie do oceny skutecznosci modeli

**USED BY:**
- Data Layer (V2 Collector)
- Feedback Loop

**MEMORY ROLE:**
- **Zrodlo historii** - Rezultaty rzeczywiste do porównań
- **Punkt odniesienia** - Validacja predykcji

**UPDATE RULES:**
- **Czesotliwosc:** Codziennie o 02:00
- **Modification:** ❌ ZABRONIONE
- **Owner:** External System (tylko do odczytu)
- **Backup:** Automatyczny przed kazda analiza

---

#### 2.1.2 kursy_przygotowane.csv

**INPUT:**
- **Zrodlo:** System zewnetrzny (kursy bukmacherskie)
- **Format:** UTF-8
- **Separator:** `;`
- **Zawartosc:** Kursy startowe, koncowe, zmiany, procenty

**PROCESS:**
1. System zewnetrzny dostarcza dane kursowe
2. Plik jestanalizowany przez V2/V3 Collector
3. Dane sa konwertowane na prawdopodobienstwa
4. Wykorzystywane sa do analizy rynku

**OUTPUT:**
- Dane wejsciowe dla modeli kursowych
- Podstawa analizy zachowań rynkowych

**USED BY:**
- Data Layer (V2 Collector)
- modele_kursy_przygotowane (4 modele)
- Laboratory (analiza wzorców)

**MEMORY ROLE:**
- **Kontekst rynkowy** - Stan rynku przed meczem
- **Dane historyczne** - Porównanie z poprzednimi kursami

**UPDATE RULES:**
- **Czesotliwosc:** Codziennie o 08:00
- **Modification:** ❌ ZABRONIONE
- **Owner:** External System (tylko do odczytu)
- **Backup:** Automatyczny przed kazda analiza

---

### 2.2 Podsumowanie Source Data

| Plik | Typ | Rolka | Wlasciciel | Zmienialnosc |
|------|-----|-------|------------|-------------|
| wyniki.csv | Rezultaty | Zrodlo prawdy | External | ❌ NIE |
| kursy_przygotowane.csv | Kursy | Kontekst rynkowy | External | ❌ NIE |

**⚠️ KLUCZOWE:** Te pliki **NIE MOGA** byc modyfikowane przez zaden moduł SSI V5. Sa one **niezmienialnym fundamentem** systemu.

---

## 3. LAYER 2 — LABORATORY DATA LAYER

### 3.1 Struktura Laboratoriów

```
laboratorium/
├── dataBase_futbol_trend/
│   ├── siec_01_zmiana_kursow/
│   ├── siec_02_amplituda/
│   ├── siec_03_tempo/
│   ├── siec_04_max_wahanie/
│   ├── siec_05_start_raw/
│   ├── siec_06_koniec_raw/
│   ├── siec_07_log_start/
│   ├── siec_08_log_koniec/
│   ├── siec_09_ratio_start/
│   ├── siec_10_ratio_koniec/
│   └── siec_11_statystyka/
│
└── kursy_przygotowane/
    ├── siec_01_start_kursow/
    ├── siec_02_koniec_kursow/
    ├── siec_03_zmiana_kursow/
    └── siec_04_procent_kursow/
```

### 3.2 Cel Laboratoriów

Laboratoria sa **srodowiskiem badawczym** systemu SSI V5 Phase 2.

**Zadania:**
- Odkrywanie wzorców historycznych
- Analiza zachowań rynkowych
- Ranking cech
- Przygotowanie kontekstu dla Teacher Models

**⚠️ OGRANICZENIA:**
- Nie wykonuja predykcji
- Nie podejmuja decyzji
- Nie môdifizuje danyç źródłowych (Source Data)

### 3.3 dataBase_futbol_trend (11 modeli)

**INPUT:**
- kursy_przygotowane.csv
- wyniki.csv
- Dane historyczne (archiwum)

**PROCESS:**
- Analiza zmian kursów w czasie
- Obliczanie charakterystyk rynku (amplituda, tempo, wahania)
- Tworzenie sygnatur zachowań
- Klasyfikacja światów meczy

**OUTPUT:**
- dopasowanie_swiata_kod_dataBase_futbol_trend.csv
- Sieci neuronowe dostrojone do wzorców
- Wiedza o zachowaniu rynku

**USED BY:**
- Teacher Models (Agent Teacher)
- Memory Context Builder
- Analysis Layer

### 3.4 kursy_przygotowane (4 modele)

**INPUT:**
- kursy_przygotowane.csv
- Historyczne kursy (archiwum)

**PROCESS:**
- Analiza kursów startowych i końcowych
- Obliczanie zmienności i trendów
- Porównanie z wynikami rzeczywistymi
- Generowanie rankingów cech kursowych

**OUTPUT:**
- dopasowanie_swiata_mozg_kursy_przygotowane.csv
- Modele predykcyjne dla kursów
- Wzorce zachowań kursowych

**USED BY:**
- Teacher Models (Agent Teacher)
- Collective Teacher
- Laboratory Teacher

### 3.5 Zasady Bezpieczenstwa

**❌ ZABRONIONE:**
- Modyfikacja plików Source Data (wyniki.csv, kursy_przygotowane.csv)
- Usunięcie historii laboratoryjnych
- Ingerencja w zamrożone moduły (V2/V3/V4)

**✅ DOZWOLONE:**
- Tworzenie kopii roboczych
- Generowanie nowych plików wynikowych
- Aktualizacja wlasnych plików laboratoryjnych

---

## 4. LAYER 3 — MODEL DATA LAYER

### 4.1 Struktura Modeli

```
modele_dataBase_futbol_trend/
├── siec_01_zmiana_kursow/
│   ├── obserwacja/
│   ├── ocena/
│   ├── pamiec_obserwacji/
│   ├── kolektor_wiedzy/
│   ├── ranking_cech/
│   ├── historia_predykcji/
│   └── predykcje/
│
├── siec_02_amplituda/
│   ├── obserwacja/
│   ├── ocena/
│   ├── pamiec_obserwacji/
│   ├── kolektor_wiedzy/
│   ├── ranking_cech/
│   ├── historia_predykcji/
│   └── predykcje/
│
└── ... (siec_03 do siec_11)

modele_kursy_przygotowane/
├── siec_01_start_kursow/
│   ├── obserwacja/
│   ├── ocena/
│   ├── pamiec_obserwacji/
│   ├── kolektor_wiedzy/
│   ├── ranking_cech/
│   ├── historia_predykcji/
│   └── predykcje/
│
└── ... (siec_02, siec_03, siec_04)
```

### 4.2 Struktura Pojedynczego Modelu

Kazdy model (15地方) posiada **wlasny kontekst wiedzy** i **wlasna pamiec**.

| Folder | Rola | Zawartosc | Aktualizowany przez |
|--------|------|-----------|-------------------|
| obserwacja/ | Dane wejsciowe | Co model widzial | Model + Teacher |
| ocena/ | Ocena | Jak model dzialal | Teacher Model |
| pamiec_obserwacji/ | Historia | Historia doswiadczen | Teacher Model |
| kolektor_wiedzy/ | Wiedza | Zbiorcza wiedza modelu | Teacher Model |
| ranking_cech/ | Ranking | Istotnosc cech (Johnson) | Teacher Model |
| historia_predykcji/ | Historia | Poprzednie predykcje | Teacher Model |
| predykcje/ | Wyjscie | Aktualne predykcje | Model |

### 4.3 15 Niezaleznych Modeli

**modele_dataBase_futbol_trend (11 modeli):**

| Model | Specjalizacja | Rola |
|-------|---------------|------|
| siec_01_zmiana_kursow | Zmiany kursów | Dynamiczna analiza rynku |
| siec_02_amplituda | Amplituda | Zakres wahań |
| siec_03_tempo | Tempo | Szybkosc zmian |
| siec_04_max_wahanie | Maksymalne wahanie | Ekstremalne odchylenia |
| siec_05_start_raw | Stan poczatkowy | Surowa analiza startu |
| siec_06_koniec_raw | Stan koncowy | Surowa analiza konstantu |
| siec_07_log_start | Logarytmiczny start | Transformowane dane poczatkowe |
| siec_08_log_koniec | Logarytmiczny koniec | Transformowane dane koncowe |
| siec_09_ratio_start | Ratio poczatkowe | Stosunki poczatkowe |
| siec_10_ratio_koniec | Ratio koncowe | Stosunki koncowe |
| siec_11_statystyka | Statystyka | Aggregacja danych statystycznych |

**modele_kursy_przygotowane (4 modele):**

| Model | Specjalizacja | Rola |
|-------|---------------|------|
| siec_01_start_kursow | Kursy startowe | Analiza poczatkowych kursow |
| siec_02_koniec_kursow | Kursy koncowe | Analiza koncowych kursow |
| siec_03_zmiana_kursow | Zmiana kursów | Roznica miedzy startem a konstantem |
| siec_04_procent_kursow | Procentowe zmiany | Procentowe zmiany kursowe |

### 4.4 Zasada Niezaleznosci

Kazdy model:
- ✅ Ma **wlasna pamiec** (nie dzieli z innymi)
- ✅Ma **wlasny ranking cech** (dostosowany do specjalizacji)
- ✅ Generuje **wlasne predykcje** (niezaleznie)
- ✅ Posiada **wlasna ocene** (indywidualna)
- ❌ **NIE MOZE** modyfikowac danych innych modeli

---

## 5. LAYER 4 — WORLD MEMORY DATA LAYER

### 5.1 wstep

**World Memory** to **pamięć historyczna** systemu, która przechowuje wzorce zachowań rynkowych i klasyfikacje światów.

**⚠️ KLUCZOWE:** Te pliki **NIE WYKONUJA PREDIKCJI**. Sa one **zrodlem wiedzy** dla Teacher Models.

---

### 5.2 dopasowanie_swiata_mozg_kursy_przygotowane.csv

**INPUT:**
- Historyczne dane kursowe (kursy_przygotowane.csv)
- Wyniki meczy (wyniki.csv)
- Zachowanie rynku z poprzednich cykli

**PROCESS:**
1. Analiza podobieństw między światami kursowymi
2. Porównanie wzorców kursowych
3. Powiązanie zachowań kursowych z wynikami meczy
4. Identyfikacja analogicznych sytuacji rynkowych

**OUTPUT:**
- Pamięć podobnych światów kursowych
- Historyczne wzorce zachowań
- Kontekst dla nowych analiz

**USED BY:**
- Memory Context Builder
- Teacher Models (wszystkie)
- Collective Teacher

**MEMORY ROLE:**
- **Identyfikacja wzorców** - Znajdowanie podobnych sytuacji historycznych
- **Kontekst historyczny** - Dostarczenie kontekstu dla nowych predykcji
- **Analiza zachowań** - Zrozumienie dynamiki rynku

**UPDATE RULES:**
- **Czesotliwosc:** Po kazdym cyklu analizy laboratoryjnej
- **Modification:** Laboratory Teacher tylko
- **Owner:** Laboratory Teacher
- **Backup:** Automatyczny przed kazda aktualizacja

---

### 5.3 dopasowanie_swiata_kod_dataBase_futbol_trend.csv

**INPUT:**
- Surowa historia zmian kursów
- Dane o amplitudzie, tempie, synchronizacji
- Informacje o max_wahanie, start_raw, koniec_raw

**PROCESS:**
1. Analiza statystyczna zachowania rynku
2. Obliczanie miar centralnych (mean, median)
3. Określenie rozkładu (stdev)
4. Śledzenie maksymalnych wahań
5. Identyfikacja cech charakterystycznych świata

**Cechy zawarte:**
- zmiana_kursow
- amplituda
- tempo
- synchronizacja
- max_wahanie
- start_raw
- koniec_raw
- log_start
- log_koniec
- ratio (stosunki)
- mean (srednia)
- median (mediana)
- stdev (odchylenie standardowe)
- czas (time)

**OUTPUT:**
- Pamięć zachowania rynku
- Historyczne statystyki
- Charakterystyka światów

**USED BY:**
- Memory Context Builder
- Teacher Models (szczegolnie siec_01-siec_11)
- Laboratory Teacher

**MEMORY ROLE:**
- **Analiza trendów** - Zrozumienie dynamiki zmienności
- **Statystyki historyczne** - Podstawa dla obliczeń
- **Charakterystyka światów** - Identyfikacja typów zachowań

**UPDATE RULES:**
- **Czesotliwosc:** Po kazdym cyklu analitycznym
- **Modification:** Laboratory Teacher tylko
- **Owner:** Laboratory Teacher
- **Backup:** Automatyczny z wersjonowaniem

---

### 5.4 dopasowanie_swiata_kod_dataBase_futbol_trend_klasyfikator.csv

**INPUT:**
- log_start (logarytmiczna transformacja stanu początkowego)
- log_koniec (logarytmiczna transformacja stanu końcowego)
- Dane historyczne

**PROCESS:**
1. Klasyfikacja świata na podstawie transformowanych cech
2. Grupowanie podobnych zachowań
3. Określenie typologii światów
4. Identyfikacja wzorców klasyfikacyjnych

**OUTPUT:**
- Klasyfikacja świata
- Kategoryzacja zachowań rynkowych
- Typologia światów meczy

**USED BY:**
- Laboratory Teacher
- Teacher Models (do szybkiej identyfikacji)
- Memory Context Builder

**MEMORY ROLE:**
- **Szybka identyfikacja** - Kategoryzacja nowych światów
- **Typologia** - Klasyfikacja zachowań
- **Podobieństwo** - Znajdowanie analogicznych przypadków

**UPDATE RULES:**
- **Czesotliwosc:** Po kazdym nowym odkryciu wzorca
- **Modification:** Laboratory Teacher tylko
- **Owner:** Laboratory Teacher
- **Backup:** Z historica zmian

---

### 5.5 Podsumowanie World Memory

| Plik | Cel | Zawartosc | Aktualizowany przez |
|------|-----|-----------|-------------------|
| dopasowanie_swiata_mozg_kursy_przygotowanie.csv | Podobieństwo światów kursowych | Wzorce kursowe | Laboratory Teacher |
| dopasowanie_swiata_kod_dataBase_futbol_trend.csv | Zachowanie rynku | Statystyki i cechy | Laboratory Teacher |
| dopasowanie_swiata_kod_dataBase_futbol_trend_klasyfikator.csv | Klasyfikacja świata | Typologia | Laboratory Teacher |

**⚠️ KLUCZOWE:** Wszystkie trzy pliki stanowia **World Memory** - pamięć historyczna systemu, która **nie wykonuje predykcji**, lecz dostarcza **wiedze o przeszłości**.

---

## 6. LAYER 5 — FEATURE KNOWLEDGE LAYER

### 6.1 Ranking Cech Johnson

**INPUT:**
- Historyczne dane o świecie
- Wyniki poprzednich predykcji
- Zachowanie cech w czasie
- Informacje z World Memory

**PROCESS:**
1. **Ocena korelacji** - Pomiar sił powiązań między cechami a wynikami
2. **Ocena RF (Random Forest)** - Znaczenie cech w modelu losowego lasu
3. **Ocena DC (Dixon-Coles)** - Współczynnik decyzyjny
4. **Obliczenie siły cechy** - Aggregacja metryk: Strength = (Correlation * 0.4) + (RF * 0.3) + (DC * 0.3)

**OUTPUT:**
- Ranking cech według siły
- Wiedza o istotności cech dla różnych typów światów
- Informacja które sygnały historycznie miały znaczenie

**USED BY:**
- Teacher Models (wszystkie)
- Memory Context Builder
- Collective Teacher

### 6.2 Struktura Cechy Johnson

Kazda cecha posiada:

| Metryka | Zakres | Znaczenie | Waga w Strength |
|---------|--------|-----------|-----------------|
| korelacja | 0.0 - 1.0 | Siła korelacji z wynikiem | 40% |
| RF | 0.0 - 1.0 | Znaczenie w Random Forest | 30% |
| Dixon-Coles | 0.0 - 1.0 | Współczynnik decyzyjny | 30% |
| sila | 0.0 - 1.0 | **Calkowita istotnosc cechy** | 100% |

### 6.3 Przyklady Cech

**Przykład 1: ratio_X2_koniec**

```
Feature Name: ratio_X2_koniec
Source: modele_dataBase_futbol_trend/siec_10_ratio_koniec

Metrics:
  korelacja: 0.881
  RF: 0.821
  DC: 0.775
  sila: 0.831

Interpretation:
  - Silna korelacja z wynikiem meczu
  - Wysokie znaczenie w modelu Random Forest
  - Dobry wspolczynnik Dixon-Coles
  - Ogolna istotnosc: 83.1%
```

**Przykład 2: mean_1**

```
Feature Name: mean_1
Source: modele_dataBase_futbol_trend/siec_11_statystyka

Metrics:
  korelacja: 0.752
  RF: 0.689
  DC: 0.723
  sila: 0.734

Interpretation:
  - Srednia korelacja z wynikiem
  - Umiarkowane znaczenie RF
  - Dobry wspolczynnik DC
  - Ogolna istotnosc: 73.4%
```

**Przykład 3: zmiana_1**

```
Feature Name: zmiana_1
Source: modele_dataBase_futbol_trend/siec_01_zmiana_kursow

Metrics:
  korelacja: 0.912
  RF: 0.876
  DC: 0.845
  sila: 0.881

Interpretation:
  - Bardzo silna korelacja
  - Wysokie znaczenie w RF
  - Doskonaly wspolczynnik DC
  - Ogolna istotnosc: 88.1% (Bardzo wysoka)
```

### 6.4 Zasady Feature Knowledge

**⚠️ KLUCZOWE:**
1. **Ranking NIE WYKONUJE PREDIKCJI** - Jest źródłem wiedzy, nie decyzji
2. **Cechy sa kontekstowe** - Ich istotnosc zalezy od typu świata
3. **Dynamiczna aktualizacja** - Ranking zmienosc sie z kazdym nowym cyklem nauki
4. **Specyficzne dla modelu** - Kazdy Teacher Model moze miec wlasny ranking

**Rola Feature Knowledge:**
- Odpowiada na pytanie: **"które cechy były ważne w podobnych świeciech?"**
- NIE odpowiada na pytanie: **"jaki będzie wynik meczu?"**

---

## 7. LAYER 6 — PREDICTION DATA LAYER

### 7.1 predykcje/predykcja_grupy.csv

**INPUT:**
- Indywidualne predykcje od 15 Agent Teacher
- Zbiorcza wiedza od Collective Teacher
- Kontekst decyzyjny od Laboratory Teacher

**MODEL SOURCE:**
- Kazdy z 15 Teacher Models generuje wlasna predykcje
- Collective Teacher agreguje i porównuje predykcje
- Finalna decyzja jest wynikiem konsensusu lub głosowania

**PROCESS:**
1. Agent Teacher generuja predykcje indywidualne
2. Collective Teacher agreguje i ocenia predykcje
3. Laboratory Teacher weryfikuje trafnosc
4. Zapis finalnej predykcji do predykcja_grupy.csv

**OUTPUT:**
- Plik CSV zawierajacy zespołowe predykcje
- Dostepny dla Agent System i Feedback Loop

**Format pliku:**

| Pole | Typ | Opis | Zakres | Przykład |
|------|-----|------|--------|---------|
| id_meczu | string | Unikalny identyfikator meczu | - | MATCH_20260801_001 |
| id_grupy | string | Identyfikator grupy modeli | - | GRUPA_01 |
| wynik_predykcji | string | Przewidywany wynik | GOSPODARZE:GOSCIE | 2:1 |
| pewnosc | float | Poziom pewności | 0.0 - 1.0 | 0.88 |

**CONFIDENCE:**
- **0.90-1.00:** Bardzo wysoka pewnosc (silny konsensus)
- **0.70-0.89:** Wysoka pewnosc (zgodnosc wiekszosci)
- **0.50-0.69:** Srednia pewnosc ( partialny konsensus)
- **0.30-0.49:** Niska pewnosc (slaby konsensus)
- **0.00-0.29:** Bardzo niska pewnosc (konflikt)

**FEEDBACK:**
- Porównywany z wynikami rzeczywistymi (wyniki.csv)
- Wykorzystywany do aktualizacji ocena.json
- Źródło nauki dla Teacher Models

---

## 8. DATA OWNERSHIP MODEL

### 8.1 Tabela Odpowiedzialnosci

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DATA OWNERSHIP MODEL                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ŹRÓDŁO DANYCH         ←  WŁAŚCICIEL    ←  CZYTAJĄCY       ←  MODYFIKACJA   │
│  ─────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  SOURCE DATA                                                          │
│  ├── wyniki.csv            ← External System  ← ALL        ← ❌ NIE       │
│  └── kursy_przygotowane    ← External System  ← ALL        ← ❌ NIE       │
│       .csv                                                           │
│                                                                             │
│  LABORATORY DATA                                                      │
│  ├── dataBase_futbol_   ← Laboratory        ← Teacher      ← Laboratory  │
│  │   trend/             System            Models         Teacher       │
│  └── kursy_przygotowane/                                only          │
│                                                                             │
│  MODEL DATA                                                           │
│  ├── modele_dataBase_     ← Individual        ← Owner          ← Owner       │
│  │   futbol_trend/        Model             Model          Model       │
│  └── modele_kursy_       (15 models)        only           only         │
│      przygotowane/                                                   │
│                                                                             │
│  WORLD MEMORY                                                         │
│  ├── dopasowanie_swiata_    ← Laboratory        ← ALL        ← Laboratory  │
│  │   mozg_kursy_         Teacher                            Teacher       │
│  │   przygotowane.csv                                               │
│  ├── dopasowanie_swiata_    ← Laboratory        ← ALL        ← Laboratory  │
│  │   kod_dataBase_         Teacher                            Teacher       │
│  │   futbol_trend.csv                                              │
│  └── dopasowanie_swiata_    ← Laboratory        ← ALL        ← Laboratory  │
│      kod_dataBase_         Teacher                            Teacher       │
│      futbol_trend_                                                  │
│      klasyfikator.csv                                              │
│                                                                             │
│  FEATURE KNOWLEDGE                                                     │
│  └── ranking_cech/          ← Feedback Loop     ← Teacher      ← Feedback    │
│                              (Johnson)          Models         Loop         │
│                                                                             │
│  PREDICTION DATA                                                       │
│  └── predykcja_grupy.csv   ← Teacher Models    ← Agent        ← Teacher     │
│                                  (Collective)      System        Models       │
│                                                                             │
│  MEMORY LAYERStroke                      │
│  ├── pamiec_obserwacji/  ← Agent Teacher       ← Agent          ← Agent       │
│  │                           + Feedback Loop      Teacher        Teacher      │
│  ├── ocena/               ← Agent Teacher       ← ALL           ← Agent       │
│  │                           + Feedback Loop                   Teacher      │
│  ├── kolektor_wiedzy/     ← Collective         ← Collective    ← Collective  │
│  │                           Teacher             Teacher        Teacher      │
│  └── world memory/        ← Laboratory         ← ALL           ← Laboratory  │
│                              Teacher                                       Teacher       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Matryca Dostępu

| Warstwa | Właściciel | Czytanie | Zapis | Modfikacja Zrodlowych |
|---------|------------|----------|-------|------------------------|
| Source Data | External System | All | ❌ NIE | ❌ ZABRONIONE |
| Laboratory Data | Laboratory System | Teacher Models | Laboratory Teacher | ❌ ZABRONIONE |
| Model Data | Individual Model | Owner + Teachers | Owner | ❌ ZABRONIONE |
| World Memory | Laboratory Teacher | All | Laboratory Teacher | ❌ ZABRONIONE |
| Feature Knowledge | Feedback Loop | Teacher Models | Feedback Loop | ❌ ZABRONIONE |
| Prediction Data | Teacher Models | All | Teacher Models | ❌ ZABRONIONE |
| Memory Layer | Various | Various | Owners | ❌ ZABRONIONE |

### 8.3 Zasady Wlasnosci

1. **Kazde zrodlo ma jednego wlasciciela** - Odpowiedzialnosc jest jasno zdefiniowana
2. **Dostep do odczytu jest szeroki** - Wiele modulow moze czytac, ale pisac moze tylko wlasciciel
3. **Dane zrodlowe sa niezmienialne** - Source Data i Laboratory Data nie moga byc modyfikowane przez moduly nalezace do innych warstw
4. **Pamięć jest hierarchiczna** - Kazda warstwa pamieci ma swoja role i wlasciciela

---

## 9. DATA FLOW DIAGRAM

### 9.1 Glówny Przeplyw Danych

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DATA FLOW DIAGRAM - SSI V5 PHASE 2                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐     ┌─────────────────┐                              │
│  │  wyniki.csv      │     │ kursy_przygotow │                              │
│  │  (Source Data)   │     │ ane.csv          │                              │
│  │                  │     │ (Source Data)   │                              │
│  └────────┬────────┘     └────────┬────────┘                              │
│           │                          │                                      │
│           └──────────────┬──────────┘                                      │
│                          ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    LABORATORY DATA LAYER                          │   │
│  │  ┌─────────────────────────────────────────────────────────┐  │   │
│  │  │ dataBase_futbol_trend/ (11 modeli)                        │  │   │
│  │  └─────────────────────────────────────────────────────────┘  │   │
│  │  ┌─────────────────────────────────────────────────────────┐  │   │
│  │  │ kursy_przygotowane/ (4 modele)                            │  │   │
│  │  └─────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                          │                                                  │
│                          ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                  WORLD MEMORY LAYER                               │   │
│  │  ┌─────────────────────────────────────────────────────────┐  │   │
│  │  │ dopasowanie_swiata_mozg_kursy_przygotowane.csv             │  │   │
│  │  │ dopasowanie_swiata_kod_dataBase_futbol_trend.csv           │  │   │
│  │  │ dopasowanie_swiata_kod_dataBase_futbol_trend_klasyfikator   │  │   │
│  │  └─────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                          │                                                  │
│                          ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                 FEATURE KNOWLEDGE LAYER                             │   │
│  │  ┌─────────────────────────────────────────────────────────┐  │   │
│  │  │ ranking_cech/ (Johnson Metrics)                            │  │   │
│  │  └─────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                          │                                                  │
│                          ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   TEACHER MODELS LAYER                             │   │
│  │  ┌─────────────────────────────────────────────────────────┐  │   │
│  │  │ Agent Teacher (15 modeli)                                   │  │   │
│  │  │ Collective Teacher                                         │  │   │
│  │  │ Laboratory Teacher                                         │  │   │
│  │  └─────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                          │                                                  │
│                          ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   AGENT SYSTEM LAYER                              │   │
│  │  ┌─────────────────────────────────────────────────────────┐  │   │
│  │  │ Decyzje oparte na wiedzy od Teacher Models                  │  │   │
│  │  └─────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                          │                                                  │
│                          ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                 PREDICTION DATA LAYER                             │   │
│  │  ┌─────────────────────────────────────────────────────────┐  │   │
│  │  │ predykcja_grupy.csv                                         │  │   │
│  │  └─────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                          │                                                  │
│                          ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                  FEEDBACK LOOP LAYER                               │   │
│  │  ┌─────────────────────────────────────────────────────────┐  │   │
│  │  │ Porownanie: predykcja_grupy.csv vs wyniki.csv               │  │   │
│  │  │ Ocena skutecznosci                                             │  │   │
│  │  │ Aktualizacja pamieci                                           │  │   │
│  │  └─────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 10. DATA INTEGRITY RULES

### 10.1 Podstawowe Zasady

1. **❌ Brak nadpisywania historii**
   - Pamięci operacyjne (pamiec_obserwacji, ocena) moga byc aktualizowane
   - Pamięci historyczne (world memory) moga byc rozbudowywane
   - **ZABRONIONE** jest usuwanie lub modyfikowanie istniejacych wpisów

2. **❌ Brak usuwania danych**
   - Żaden moduł nie ma prawa usuwac danych z innych warstw
   - Archiwizacja zamiast usuwania
   - Backup przed kazda operacja zapisu

3. **❌ Brak mieszania pamięci modeli**
   - Kazdy Teacher Model posiada **wlasna pamiec**
   - Pamiec NIE MOZE byc udostepniana innym modelom do zapisu
   - Odczyt pamieci innych modeli jest dozwolony

4. **✅ Kazdy Teacher Model posiada wlasna pamiec**
   - Niezalezne konteksty
   - Wlasne rankingi cech
   - Indywidualne historie predykcji

5. **✅ Feedback aktualizuje wiedze, nie zrodla**
   - Feedback Loop aktualizuje pamiec_obserwacji i ocena
   - Teacher Models aktualizuja kolektor_wiedzy
   - Laboratory Teacher aktualizuje world memory
   - **Żaden moduł nie aktualizuje Source Data**

### 10.2 Zasady Specyficzne

| Zasada | Opis | Wyjatek |
|--------|------|----------|
| **Immutability** | Source Data i Laboratory Data sa niezmienialne | Nowa wersja pliku |
| **Ownership** | Tylko wlasciciel moze modyfikowac swoje dane | Brak |
| **Integrity** | Wszystkie dane musza byc spójne i zwalidowane | Brak |
| **Backup** | Kazda operacja zapisu wymaga backupu | Operacje tymczasowe |
| **Validation** | Wszystkie dane musza byc walidowane przed uzyciem | Brak |
| **Audit** | Wszystkie operacje na danych sa logowane | Brak |

### 10.3 Kontrola Integralnosci

**1. Hash Verification:**
- Kazdy plik Source Data powinien miec obliczony hash (SHA256)
- Przed uzyciem dane sa weryfikowane

**2. Checksum:**
- Pamięci sa walidowane pod wzgledem spójnosci
- Bledne dane sa pomijane lub naprawiane

**3. Rollback:**
- W przypadku awarii moéliwy jest rollback do poprzedniej wersji
- Historia zmian jest zachowywana

---

**Data utworzenia:** 2026-08-01
**Wersja:** 1.0.0
**Status:** Completed
**Autor:** Glowny Architekt SSI V5

---

**NOTATKA:**
Ten dokument opisuje **kompletna architekture danych SSI V5 Phase 2**. Zaprezentowano wszystkie warstwy danych, ich role, wlascicieli, czytelników i zasady modyfikacji.

**Powiazane dokumenty:**
- `01_VISION_AND_GOALS.md` - Wizja i cele systemu
- `02_ARCHITECTURE_LAYERS.md` - Warstwy architektoniczne
- `03_DESIGN_PRINCIPLES.md` - Zasady projektowe
- `01_MAIN_FLOW.md` - Glowny przeplyw danych
- `02_INTEGRATION_FLOW.md` - Szczegołowy przeplyw integracji
- `04_TEACHER_MODEL_ARCHITECTURE.md` - Architektura Teacher Models
- `05_MODULE_DOCUMENTATION_TEMPLATES.md` - Szablony dokumentacji

**Nastepny sugerowany dokument:**
- Implementacja Poszczegolnych modulow wedlug dokumentacji
- Tworzenie dokumentacji dla konkretnych instancji modulow
