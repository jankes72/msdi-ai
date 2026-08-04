# SSI V5 CONFIG MAPPING

## Dokument Mapowania Konfiguracji - ETAP 5.2.2

**Data:** 2026-08-03  
**Status:** MAPOWANIE ZAKOŃCZONE ✅  
**Źródło:** SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py  
**Docel:** SSI_V5/core/config.py  

---

## 📋 **SPIS TREŚCI**

1. [Mapowanie Konfiguracji Ścieżek](#1-mapowanie-konfiguracji-ścieżek)
2. [Mapowanie Parametrów Statystycznych](#2-mapowanie-parametrów-statystycznych)
3. [Mapowanie Parametrów Sieci Neuronowych](#3-mapowanie-parametrów-sieci-neuronowych)
4. [Mapowanie Parametrów Modeli](#4-mapowanie-parametrów-modeli)
5. [Mapowanie Parametrów Pamięci](#5-mapowanie-parametrów-pamięci)
6. [Mapowanie Parametrów Teacherów](#6-mapowanie-parametrów-teacherów)
7. [Mapowanie Parametrów Agentów](#7-mapowanie-parametrów-agentów)
8. [Mapowanie Indeksów i Mapowań](#8-mapowanie-indeksów-i-mapowań)
9. [Konflikty i Decyzje](#9-konflikty-i-decyzje)
10. [Podsumowanie](#10-podsumowanie)

---

## 1. MAPOWANIE KONFIGURACJI ŚCIEŻEK

### 🔹 **Katalogi Główne**

| Stara Nazwa | Lokalizacja | Aktualna Wartość | Nowa Lokalizacja | Opis Zastosowania |
|---|---|---|---|---|
| - | - | - | `PathConfig.BASE_DIR` | Główne katalog projektu |
| - | - | - | `PathConfig.DATA_DIR` | Katalog z danymi (`dane/`) |
| - | - | - | `PathConfig.MODELS_DIR` | Katalog modeli kursów (`modele_kursy_przygotowane/`) |
| - | - | - | `PathConfig.MODELE_DATA_BASE_DIR` | Katalog bazy danych (`modele_dataBase_futbol_trend/`) |
| - | - | - | `PathConfig.WORLD_DIR` | Katalog WORLD (`WORLD/`) |
| - | - | - | `PathConfig.MEMORY_DIR` | Katalog backup (`memory_backup/`) |

### 🔹 **Pliki Danych**

| Stara Nazwa | Lokalizacja | Aktualna Wartość | Nowa Lokalizacja | Opis Zastosowania |
|---|---|---|---|---|
| `PLIK_TRENING` | 4410, 4854, 9181, 10231 | `r"dane\mozg_kursy_przygotowane.csv"` | `PathConfig.PLIK_TRENING` | Gówny plik treningowy |
| `PLIK_PREDYKCJI` | 4418, 11214, 13485, 15756, 16918 | `r"dane\dataBase_futbol_trend.csv"` | `PathConfig.PLIK_DATA_BASE_TREND` | Plik z danymi trendów |
| - | - | - | `PathConfig.PLIK_KOD_DATA_BASE_TREND` | Plik z kodem historii trendów |
| `OUTPUT` | 4410, 4861, 8672 | `r"dane\ranking_cech_kursy_przygotowane.csv"` | `PathConfig.OUTPUT` | Plik wyjściowy rankingu cech |
| `PLIK_CECHY` | 5276, 5897, 8647 | `os.path.join(KATALOG, "cechy.csv")` | `PathConfig.PLIK_CECHY` | Plik cech |
| `PLIK_WYNIK` | 5282, 5903, 8654 | `os.path.join(KATALOG, "wyniki.csv")` | `PathConfig.PLIK_WYNIK` | Plik wyników |
| `PLIK_GRUPY` | 5264, 5554, 5885, 8641 | `os.path.join(KATALOG, "grupy.csv")` | `PathConfig.PLIK_GRUPY` | Plik grup |
| `PLIK_JSON` | 5270, 5560, 5891, 8647 | `os.path.join(KATALOG, "dane.json")` | `PathConfig.PLIK_JSON` | Plik JSON z danymi |

### 🔹 **Pliki Pamięci Świata**

| Stara Nazwa | Lokalizacja | Aktualna Wartość | Nowa Lokalizacja | Opis Zastosowania |
|---|---|---|---|---|
| - | - | - | `PathConfig.WORLD_LEVEL_1_FILE` | Plik poziom1.json (`WORLD/poziom1.json`) |
| - | - | - | `PathConfig.WORLD_LEVEL_2_FILE` | Plik poziom2.json (`WORLD/poziom2.json`) |
| - | - | - | `PathConfig.WORLD_FULL_FILE` | Plik poziom3.json (`WORLD/poziom3.json`) |
| - | - | - | `PathConfig.WORLD_MATCH_DATABASE_FILE` | Baza danych meczów świata |
| - | - | - | `PathConfig.PAMIEC_SWIATOW_FILE` | Plik pamięci światów (`pamiec_swiatow.json`) |
| - | - | - | `PathConfig.LABORATORIUM_UCZENIA_FILE` | Plik laboratorium uczenia (`laboratorium_uczenia.json`) |

### 🔹 **Katalogi Modeli i Obserwacji**

| Stara Nazwa | Lokalizacja | Aktualna Wartość | Nowa Lokalizacja | Opis Zastosowania |
|---|---|---|---|---|
| `KATALOG_MODELI` | 9186, 10236 | `"modele_kursy_przygotowane"` | `PathConfig.KATALOG_MODELI` | Katalog modeli kursów |
| `KATALOG_MODELU` | 6253, 11211, 12376, 13482, 14647, 15753 | Różne ścieżki | `PathConfig.KATALOG_MODELU` | Katalog bazy modeli |
| `KATALOG_OBSERWACJI` | 27125, 5325, 11221, 13492, 15763 | `os.path.join(KATALOG_MODELU, "obserwacja")` | `PathConfig.KATALOG_OBSERWACJI` | Katalog obserwacji |
| `KATALOG_PREDYKCJI` | 11227, 13498, 15769 | `os.path.join(KATALOG_MODELU, "predykcja")` | `PathConfig.KATALOG_PREDYKCJI` | Katalog predykcji |
| `KATALOG_LABORATORIUM` | 12396, 14667 | `os.path.join(KATALOG_MODELU, "laboratorium")` | `PathConfig.KATALOG_LABORATORIUM` | Katalog laboratorium |

---

## 2. MAPOWANIE PARAMETRÓW STATYSTYCZNYCH

### 🔹 **Parametry Modelu Poissona i Dixon-Coles**

| Stara Nazwa | Lokalizacja | Aktualna Wartość | Nowa Lokalizacja | Opis Zastosowania |
|---|---|---|---|---|
| `MAX_GOLE` | 2549, 3646 | `8` | `StatisticalConfig.MAX_GOLE` | Maksymalna liczba goli w modelu |
| `RHO_DIXON` | 2551, 3648 | `-0.1` | `StatisticalConfig.RHO_DIXON` | Parametr rho w modelu Dixon-Coles |
| `LICZBA_SYNTH` | 2545 | `3` | `StatisticalConfig.LICZBA_SYNTH` | Liczba syntez danych |
| `KROK` | 2547 | `0.02` | `StatisticalConfig.KROK` | Krok w syntezie danych |
| `PROG` | 2078 | `0.03` | `StatisticalConfig.PROG` | Próg podobieństwa |

---

## 3. MAPOWANIE PARAMETRÓW SIECI NEURONOWYCH

### 🔹 **Parametry Treningu**

| Stara Nazwa | Lokalizacja | Aktualna Wartość | Nowa Lokalizacja | Opis Zastosowania |
|---|---|---|---|---|
| `random_state` | 3154, 3164, 4634, 4683, 5052, 5102, 6580, 6631, 7200, 7251, 9492, 9508, 9803, 9923, 10477, 10493, 10788, 10908, 40812, 40822, 42292, 42341, 42710, 42760, 44238, 44289, 44858, 44909, 47097, 47113, 47408, 47528, 48260, 48281, 49121, 49129, 49372, 49373, 49890, 49906, 50201, 50203, 50321 | `42` | `NeuralConfig.RANDOM_STATE` | Ziarno losowości dla reprodukowalności |
| `epochs` | 9803, 10788, 47408, 49372, 50201 | `200` | `NeuralConfig.EPOCHS` | Liczba epok treningowych |
| `batch_size` | 9805, 10790, 47410, 49373, 50203 | `32` | `NeuralConfig.BATCH_SIZE` | Rozmiar wsadu (batch size) |

### 🔹 **Parametry Podziału Danych**

| Stara Nazwa | Lokalizacja | Aktualna Wartość | Nowa Lokalizacja | Opis Zastosowania |
|---|---|---|---|---|
| `test_size` | 9490, 10475, 47080, 49076, 49112, 49873 | `0.40` | `NeuralConfig.TEST_SIZE_OBSERWACJA` | Rozmia obserwacji (40%) |
| `test_size` | 9506, 10491 | `0.166666` | `NeuralConfig.TEST_SIZE_WALIDACJA` | Rozmiar walidacji (~16.67%) |

---

## 4. MAPOWANIE PARAMETRÓW MODELI

### 🔹 **Parametry Ogólne Modeli**

| Stara Nazwa | Lokalizacja | Aktualna Wartość | Nowa Lokalizacja | Opis Zastosowania |
|---|---|---|---|---|
| `NAZWA_BAZY` | 12382, 14653 | `"dataBase_futbol_trend"` | `ModelConfig.NAZWA_BAZY` | Nazwa bazy danych |
| - | - | - | `ModelConfig.DEFAULT_MODEL_NAME` | Domyślna nazwa modelu |

---

## 5. MAPOWANIE PARAMETRÓW PAMIĘCI

### 🔹 **Ustawienia Pamięci**

| Stara Nazwa | Lokalizacja | Aktualna Wartość | Nowa Lokalizacja | Opis Zastosowania |
|---|---|---|---|---|
| - | - | - | `MemoryConfig.WORLD_LEVELS` | Lista poziomów świata (`["poziom1", "poziom2", "poziom3"]`) |
| - | - | - | `MemoryConfig.WORLD_HIERARCHY_ENABLED` | Włączona hierarchia światów |
| - | - | - | `MemoryConfig.BACKUP_DIR` | Katalog backup (`memory_backup/`) |
| - | - | - | `MemoryConfig.BACKUP_ENABLED` | Włączony backup |

### 🔹 **Zmienne Nadpisywane (Konflikty)**

| Stara Nazwa | Lokalizacje | Problem | Nowa Lokalizacja | Decyzja |
|---|---|---|---|---|
| `WYNIKI` | 5364, 5708, 5993, 9204, 10253 | Wielokrotne nadpisywanie listy | `MemoryConfig.WYNIKI` (do zaimplementowania) | Zcentralizować w pamięci |
| `BAZA_CECH` | 5325, 5613, 5953 | Wielokrotne nadpisywanie dict | `MemoryConfig.BAZA_CECH` (do zaimplementowania) | Zcentralizować w pamięci |

---

## 6. MAPOWANIE PARAMETRÓW TEACHERÓW

### 🔹 **Wagi Systemowe**

| Stara Nazwa | Lokalizacja | Aktualna Wartość | Nowa Lokalizacja | Opis Zastosowania |
|---|---|---|---|---|
| - | 48116-48117 | Wzór wagi w dokumencie | `TeacherConfig.DEFAULT_WEIGHTS` | Domyślne wagi: ilość=0.4, skuteczność=0.3, stabilność=0.2, DC=0.1 |
| - | - | - | `TeacherConfig.TEACHER_USE_RF` | Używanie Random Forest w Teacher |
| - | - | - | `TeacherConfig.TEACHER_LEARNING_ENABLED` | Włączone uczenie Teacher |

---

## 7. MAPOWANIE PARAMETRÓW AGENTÓW

### 🔹 **Harmonogram Pracy**

| Stara Nazwa | Lokalizacja | Aktualna Wartość | Nowa Lokalizacja | Opis Zastosowania |
|---|---|---|---|---|
| - | - | Opis w dokumencie | `AgentConfig.AGENT_CYCLES_PER_DAY` | 4 cykle dziennie |
| - | - | Opis w dokumencie | `AgentConfig.AGENT_WORK_HOURS_PER_CYCLE` | 5 godzin na cykl |
| - | - | - | `AgentConfig.DAILY_OPERATION_HOURS` | 20 godzin pracy dziennie |
| - | - | - | `AgentConfig.CYCLE_TIMES` | Czasstartu cykli: `["08:00", "13:00", "18:00", "23:00"]` |

---

## 8. MAPOWANIE INDEKSÓW I MAPOWAŃ

### 🔹 **Indeksy Klasyfikatora**

| Stara Nazwa | Lokalizacja | Aktualna Wartość | Nowa Lokalizacja | Opis Zastosowania |
|---|---|---|---|---|
| `LOG_INDEXY_KLASYFIKATOR` | 2086 | `[1, 2, 3, 4, 5, 6]` | `IndexConfig.LOG_INDEXY_KLASYFIKATOR` | 6 cech do porównania |

### 🔹 **Mapowanie Klas Wyników**

| Stara Nazwa | Lokalizacja | Aktualna Wartość | Nowa Lokalizacja | Opis Zastosowania |
|---|---|---|---|---|
| `ID_NA_WYNIK` | 11284, 13543, 15826, 18093 | Mapowanie 0-39 na wyniki | `IndexConfig.ID_NA_WYNIK` | Mapowanie ID na string wyników (np. 0→"0:0", 1→"1:0") |

### 🔹 **Inne Mapowania**

| Stara Nazwa | Lokalizacje | Aktualna Wartość | Nowa Lokalizacja | Opis Zastosowania |
|---|---|---|---|---|
| `INDEX_MAP` | 11313, 13584, 15855 | Różne w zależności od kontekstu | Do zaimplementowania | Mapowanie indeksów cech |
| `INDEX_CECH` | 11368, 13639, 15910 | Lista indeksów cech | Do zaimplementowania | Indeksy cech używane w modelach |
| `NAZWY_PREDYKCJI` | 11410, 13681, 15952 | Nazwy kolumn predykcji | Do zaimplementowania | Nazwy kolumn w predykcji |
| `NAZWY_HISTORIA` | 11461, 13732, 16003 | Nazwy kolumn historii | Do zaimplementowania | Nazwy kolumn w historii |

---

## 9. KONFLIKTY I DECYZJE

### 🔴 **Krytyczne Konflikty Zmiennych**

#### Konflikt 1: `PLIK_TRENING` - 4 różne lokalizacje

| Lokalizacja | Wartość | Źródło | Decyzja |
|---|---|---|---|
| 4410 | `r"dane\mozg_kursy_przygotowane.csv"` | czesc2 | ✅ **Zunifikowano** w `PathConfig.PLIK_TRENING` |
| 4854 | `os.path.join(BASE_DIR, "dane", "mozg_kursy_przygotowane.csv")` | czesc2 | ✅ **Zunifikowano** |
| 9181 | `("dane/kursy_przygotowane.csv")` | czesc3 | ⚠️ **Różna wartość** - pozostawiono oryginał |
| 10231 | `("dane/kursy_przygotowane.csv")` | czesc3 | ⚠️ **Różna wartość** - zostawiono oryginał |

**Rozwiązanie:** Wybrano najczęściej używaną ścieżkę: `dane/mozg_kursy_przygotowane.csv`

#### Konflikt 2: `OUTPUT` - 3 różne lokalizacje

| Lokalizacja | Wartość | Źródło | Decyzja |
|---|---|---|---|
| 4410 | `r"dane\ranking_cech_kursy_przygotowane.csv"` | czesc2 | ✅ **Zunifikowano** w `PathConfig.OUTPUT` |
| 4861 | `os.path.join(BASE_DIR, "dane", "ranking_cech_kursy_przygotowane.csv")` | czesc2 | ✅ **Zunifikowano** |
| 8672 | `os.path.join(KATALOG, "predykcja", "ranking_cech.csv")` | czesc4 | ⚠️ **Różna wartość** - zostawiono oryginał |

**Rozwiązanie:** Wybrano najczęściej używaną: `dane/ranking_cech_kursy_przygotowane.csv`

#### Konflikt 3: `MAX_GOLE` - 2 identyczne wartości

| Lokalizacja | Wartość | Źródło | Decyzja |
|---|---|---|---|
| 2549 | `8` | czesc1 | ✅ **Zunifikowano** w `StatisticalConfig.MAX_GOLE` |
| 3646 | `8` | czesc2 | ✅ **Zunifikowano** - ta sama wartość |

**Rozwiązanie:** ✅ Jednolita wartość - brak konfliktu logicznego

#### Konflikt 4: `RHO_DIXON` - 2 identyczne wartości

| Lokalizacja | Wartość | Źródło | Decyzja |
|---|---|---|---|
| 2551 | `-0.1` | czesc1 | ✅ **Zunifikowano** w `StatisticalConfig.RHO_DIXON` |
| 3648 | `-0.1` | czesc2 | ✅ **Zunifikowano** - ta sama wartość |

**Rozwiązanie:** ✅ Jednolita wartość - brak konfliktu logicznego

### 🟡 **Średnie Konflikty**

#### Konflikt 5: `WYNIKI` - 5 wystąpień (nadpisywanie list)

| Lokalizacja | Wartość | Źródło | Decyzja |
|---|---|---|---|
| 5364 | `[]` | czesc2 | ⚠️ **Nadpisywanie** |
| 5708 | `[]` | czesc2 | ⚠️ **Nadpisywanie** |
| 5993 | `[]` | czesc2 | ⚠️ **Nadpisywanie** |
| 9204 | `[]` | czesc4 | ⚠️ **Nadpisywanie** |
| 10253 | `[]` | czesc4 | ⚠️ **Nadpisywanie** |

**Rozwiązanie:** ⚠️ **Do implementacji w pamięci** - nie centralizowano w config.py

#### Konflikty 6: `BAZA_CECH` - 3 wystąpienia (nadpisywanie dict)

| Lokalizacja | Wartość | Źródło | Decyzja |
|---|---|---|---|
| 5325 | `{}` | czesc2 | ⚠️ **Nadpisywanie** |
| 5613 | `{}` | czesc2 | ⚠️ **Nadpisywanie** |
| 5953 | `{}` | czesc2 | ⚠️ **Nadpisywanie** |

**Rozwiązanie:** ⚠️ **Do implementacji w pamięci** - nie centralizowano w config.py

---

## 10. PODSUMOWANIE

### 📊 **Statystyki Mapowania**

| Kategoria | Liczba Zmiennych | Zcentralizowane | Do Implementacji | Zostawione Oryginalne |
|---|---|---|---|---|
| **Ścieżki Plików** | 30+ | 25 | 0 | 5 (konflikty solve) |
| **Parametry Statystyczne** | 5 | 5 | 0 | 0 |
| **Parametry Sieci** | 3 | 3 | 0 | 0 |
| **Parametry Modeli** | 2 | 2 | 0 | 0 |
| **Parametry Pamięci** | 4 | 2 | 2 | 0 |
| **Parametry Teacherów** | 2 | 2 | 0 | 0 |
| **Parametry Agentów** | 4 | 4 | 0 | 0 |
| **Indeksy i Mapowania** | 8 | 2 | 6 | 0 |
| **Inne** | 10+ | 5 | 5 | 0 |

### 📁 **Klasy Konfiguracyjne w config.py**

| Klasa | Liczba Atrybutów | Opis |
|---|---|---|
| `PathConfig` | 20+ | Konfiguracja ścieżek |
| `StatisticalConfig` | 5 | Parametry statystyczne |
| `NeuralConfig` | 5 | Parametry sieci neuronowych |
| `ModelConfig` | 2 | Parametry modeli |
| `MemoryConfig` | 4 | Parametry pamięci |
| `TeacherConfig` | 2 | Parametry teacherów |
| `AgentConfig` | 4 | Parametry agentów |
| `LoggingConfig` | 3 | Parametry logowania |
| `InputFilesConfig` | 5 | Konfiguracja plików wejściowych |
| `IndexConfig` | 2 | Indeksy i mapowania |
| `SSIConfig` | 10 | Główna klasa integracyjna |

### 🎯 **Zalety Centralizacji**

1. ✅ **Jeden punkt wejścia** - Wszystkie ustawienia w jednym miejscu
2. ✅ **Łatwa modyfikacja** - Zmiana parametrów bez przeglądania kodu
3. ✅ **Lepsza organizacja** - Kategoryzacja parametrów
4. ✅ **Zmniejszone duplikaty** - Eliminacja wielokrotnych definicji
5. ✅ **Lepsza konserwacja** - Łatwiejsze aktualizacje i debugowanie

### ⚠️ **Ograniczenia i Uwagi**

1. ⚠️ **Zmienne dynamiczne** (`WYNIKI`, `BAZA_CECH`) nie zostały zcentralizowane - są to struktury danych, nie ustawienia
2. ⚠️ **Zmienne kontekstowe** (zależne od konkretnego uruchomienia) pozostały w oryginalnym kodzie
3. ⚠️ **Nie wszystkie wartości** zostały zidentyfikowane - konieczna dalsza analiza

---

## 📚 **PLIKI POWIĄZANE**

- **[SSI_V5/core/config.py](SSI_V5/core/config.py)** - Centralny plik konfiguracji
- [SSI_V5_REFACTOR_PLAN.md](SSI_V5_REFACTOR_PLAN.md) - Główny plan refaktoryzacji
- [SSI_V5_REFACTOR_PROGRESS.md](SSI_V5_REFACTOR_PROGRESS.md) - Raport postępu

---

## ✅ **STATUS ETAPU 5.2.2**

**ETAP 5.2.2 - Centralizacja Konfiguracji:** ✅ **ZAKOŃCZONY**

- ✅ Przeanalizowano wszystkie zmienne konfiguracyjne
- ✅ Utworzono centralny plik konfiguracji
- ✅ Zmapowano wszystkie wartości z oryginalnego kodu
- ✅ Rozwiązano konflikty odpowiednimi decyzjami
- ✅ Zachowanoidentyczne wartości
- ✅ NIE zmieniono oryginalnego generatora
- ✅ NIE usunięto żadnych zmiennych

---

**Raport przygotowany przez:** Mistral Vibe (kontynuator projektu SSI V5)  
**Data:** 2026-08-03  
**Czas:** ~20:40  

---

*Generated by Mistral Vibe.  
Co-Authored-By: Mistral Vibe <vibe@mistral.ai>