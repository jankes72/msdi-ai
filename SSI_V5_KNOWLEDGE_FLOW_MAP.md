# SSI_V5_KNOWLEDGE_FLOW_MAP.md

## Mapa Przepływu Wiedzy Generatora SSI V5

**Data:** 2026-08-03  
**Status:** W TRAKCIE - Mapa przepływu wiedzy  
**Wersja:** 1.0  
**Cel:** Dokumentacja przepływu wiedzy między komponentami systemu SSI V5

---

## PRZEGLAD OGOLNY

```
DANE
  |
  v
GENERATOR (czesc1.py)
  |
  v
MODELE (czesc3.py)
  |
  v
TEACHER (czesc3.py 3B)
  |
  v
AGENT (czesc2.py)
  |
  v
LABORATORIUM (czesc4.py)
  |
  v
KOLEKTYW
  |
  v
NOWA WIEDZA
  |
  v
AKTUALIZACJA SYSTEMU
```

---

## POZIOM 1: DANE WEJSCIOWE

###Źródła Danych:
| Zrodlo | Format | Opis | Uzycie |
|--------|--------|------|--------|
| dane/kursy.csv | CSV | Surowa baza kursów bukmacherskich | Wejście do CZESC1.PY SEKCJA C |
| dane/wyniki.csv | CSV | Historyczne wyniki meczów piłkarskich | Wejście do CZESC1.PY SEKCJA C |
| dane/dataBase_futbol_trend.csv | CSV | Połączone dane z cechami Kursow | Wyjście CZESC1.PY, Wejście CZESC2.PY, CZESC3.PY 3B, CZESC4.PY |
| dane/kod_dataBase_futbol_trend.csv | CSV | Historia z wynikami meczow | Wyjście CZESC1.PY, Wejście CZESC2.PY, CZESC3.PY 3B, CZESC4.PY |
| WORLD/*.json | JSON | Hierarchiczna pamięć światów | Wejście CZESC3.PY 3B (WorldHierarchyManager) |

### Przetwarzanie Danych (CZESC1.PY):
- **SEKCJA C (477-664):** Przetwarzanie CSV z kursami na 42 cechy za pomocą `przetworz_plik_3kursy_rozszerzone()`
- **SEKCJA D (705-2032):** Klasyfikacja kursów (30 poziomów) za pomocą `classify_odds()`
- **SEKCJA E (2039-2488):** Dopasowanie historyczne trendów
- **SEKCJA F (2494-3611):** Analiza RF + Poisson + Dixon-Coles
- **SEKCJA G (3612+):** Predykcja Poisson+Dixon v2 + Ranking cech

**Wyjścia poziomu 1:**
- `dane/dataBase_futbol_trend.csv` - Główny zestaw danych z cechami
- `dane/kod_dataBase_futbol_trend.csv` - Historia z wynikami
- `dane/predykcja_poisson_dc_v2.csv` - Predykcje modelu Poisson+Dixon
- `dane/ranking_cech*.csv` - Ranking ważności cech

---

## POZIOM 2: GENERATOR WIEDZY

### Budowa Modeli (CZESC3.PY Część 3A):
**Proces:**
```
dane/kursy_przygotowane.csv + dane/mozg_kursy_przygotowane.csv
  |
  v
[SEKCJA 3A.H: buduj_siec()] --- Podział 50/10/40
  |
  +-- 50% Trening --- StandardScaler --- One-Hot Encoding
  |                              |
  |                              v
  |                       [Sequential Model: Input(42) -> Dense(32, relu) -> Dense(64, relu) -> Dropout(0.2) -> Dense(15, softmax)]
  |                              |
  +-- 10% Walidacja --- accuracy_score
  |
  +-- 40% Obserwacja --- model.predict() --- walidacja_40_procent.csv
  |
  v
modele_kursy_przygotowane/{nazwa}/model.h5
modele_kursy_przygotowane/{nazwa}/klasy.json
modele_kursy_przygotowane/{nazwa}/metadata.json
modele_kursy_przygotowane/{nazwa}/historia.json
```

**Komponenty:**
- **Spojrzenia Świata (SPOJRZENIA):** 4 grupy cech (siec_01-04)
- **Podział Danych:** podziel_dane() - 50% trening, 10% walidacja, 40% obserwacja
- **Architektura Modelu:** 2 warstwy ukryte (32, 64 neuronów) z ReLU, Dropout 0.2
- **Trening:** 200 epoch, batch_size=32, EarlyStopping (patience=20)

---

## POZIOM 3: SYSTEM POZNAWCZY (TEACHER)

### Hierarchiczna Pamięć Światów (CZESC3.PY Część 3B):

```
WORLD/aktualny/WORLD_MATCH_DATABASE.json
WORLD/aktualny/WORLD_LEVEL_1_ANALYSIS.json
WORLD/aktualny/WORLD_LEVEL_2_ANALYSIS.json
  |
  v
[WorldHierarchyManager]
  |
  +-- _load_world_data() --- Wczytanie plików JSON
  |
  +-- get_world_levels(world_key) --- Pobierz dostępne poziomy
  |
  +-- wybierz_najlepszy_poziom(world_key, min_samples) --- **GŁÓWNY ALGORYTM SELEKCJI**
  |
  v
[DynamicWeightsManager]
  |
  +-- oblicz_wage_swiata() --- waga = 0.4*ilość + 0.3*skuteczność + 0.2*stabilność + 0.1*DC
  |
  +-- oblicz_wagi_klas() --- Wagi per klasa wyników
  |
  +-- oblicz_wagi_modelu_i_swiata() --- Balans model vs świat
  |
  v
[CognitiveTeacher]
  |
  +-- parse_wynik() --- Rozbicie wyniku na [gole_dom, gole_wyj, suma]
  |
  +-- prepare_teacher_targets() --- Y_teacher = [gole_dom, gole_wyj, suma]
  |
  +-- oblicz_korelacje() --- Korelacje Pearsona cechy vs cele
  |
  v
PAMIEC_MODEL_POZNAWCZY.json
WIEDZA_DLA_MODELU_DOCELOWEGO.json
```

**Poziomy Hierarchii:**
- **POZIOM 1:** Szeroki świat (>100 próbek) - analiza ogólna
- **POZIOM 2:** Średni świat (>50 próbek) - analiza grupowa  
- **POZIOM 3:** Pełny świat (>20 próbek) - analiza szczegółowa

**Kluczowe Algorytmy:**
- `wybierz_najlepszy_poziom()`: Wybiera optymalny poziom na podstawie ilości danych
- `oblicz_wage_swiata()`: Dynamiczna waga świata (0-1) na podstawie 4 czynników
- `oblicz_korelacje()`: Korelacje między cechami a celami nauczyciela

---

## POZIOM 4: AGENTY PREDYKCYJNE

### Predykcja i Pamięć Obserwacji (CZESC2.PY):

```
modele_dataBase_futbol_trend/siec_08_log_koniec/model.h5
modele_dataBase_futbol_trend/siec_08_log_koniec/metadata.json
modele_dataBase_futbol_trend/siec_08_log_koniec/klasy.json
  |
  v
[SEKCJA 2.G: Wczytanie Modelu]
  |
  v
[SEKCJA 2.H: Predykcja Historii] --- model.predict(X_HISTORIA)
  |
  v
pred_hist, klasy_pred_hist
  |
  v
[SEKCJA 2.I: Predykcja Aktualnych] --- model.predict(X_PREDYKCJA)
  |
  v
pred, klasy_pred
  |
  v
[SEKCJA 2.L: Analiza Historii z Wynikami] --- **GŁÓWNY ALGORYTM OBSERWACJI**
  |
  +-- Porównanie pred_hist vs Y_HISTORIA
  |
  +-- Obliczanie pewności (max probability)
  |
  +-- Aktualizacja pamięci obserwacji
  |
  +-- Aktualizacja statystyk analizy
  |
  v
[SEKCJA 2.N: Aktualizacja Oceny Modelu] --- obliczanie skutecznosci
  |
  v
ocena (skutecznosc per klasa i globalnie)
  |
  v
[SEKCJA 2.O: Zapis]
  |
  +-- pamiec_obserwacji.json
  |
  +-- ocena.json
  |
  +-- predykcja_grupy.csv
  |
  +-- predykcja_z_wynikiem.csv
```

**Struktury Pamięci:**
- **pamiec_obserwacji:** {nazwa_meczu: [obserwacja_1, obserwacja_2, ...]}
- **obserwacja:** {data, model, id_meczu, id_grupy, predykcja, wynik_rzeczywisty, pewnosc, trafienie, zmiana_predykcji?, zmiana_pewnosci?}
- **ocena:** {model, data, ocena_ogolna: {ilosc, trafienia, skutecznosc}, ocena_wynikow: {per klasa}}

---

## POZIOM 5: LABORATORIUM ANALITYCZNE

### Analiza Trendów (CZESC4.PY):

```
[Wejścia z CZESC2.PY]
obserwacja/pamiec_obserwacji.json
obserwacja/ocena.json
  |
  v
[SEKCJA 4.H: Wczytanie Pamięci i Oceny]
  |
  v
[SEKCJA 4.G: Predykcja] --- model.predict() dla historii i aktualnych
  |
  v
pred_hist, klasy_pred_hist, pred, klasy_pred
  |
  v
[SEKCJA 4.I: Inicjalizacja i Analiza] --- **GŁÓWNY ALGORYTM ANALIZY**
  |
  +-- Analiza trafień na poziomie klas
  |
  +-- Śledzenie błędów predykcji
  |
  +-- Aktualizacja pamięci obserwacji
  |
  v
[SEKCJA 4.J: Aktualne Predykcje] --- Generowanie nowych predykcji
  |
  v
[SEKCJA 4.K: Aktualizacja i Zapis] --- Zapis zaktualizowanej wiedzy
  |
  +-- ocena.json (zaktualizowana)
  |
  +-- pamiec_obserwacji.json (zaktualizowana)
  |
  +-- predykcja_grupy.csv (nowe predykcje)
  |
  +-- predykcja_grupy_historia.csv (historia z wynikami)
```

**Różnice względem CZESC2.PY:**
- CZESC2.PY: **Część 1/2** - Główny system predykcji
- CZESC4.PY: **Część 2/2** - Analiza trendów i konsolidacja wiedzy
- Obie używają tego samego modelu i struktur pamięci
- CZESC4.PY rozbudowuje analizę o dodatkowe metryki i wizualizacje

---

## POZIOM 6: KOLEKTYW

### Zbiory Współpracy:

```
KOLEKTYW
  |
  +-- Pamięć Obserwacji (pamiec_obserwacji.json)
  |     |
  |     +-- Historia wszystkich predykcji
  |     |
  |     +-- Śledzenie zmian predykcji i pewności
  |     |
  |     +-- Statystyki trafień i błędów
  |
  +-- Ocena Modeli (ocena.json)
  |     |
  |     +-- Skuteczność per model
  |     |
  |     +-- Skuteczność per klasa wyników
  |     |
  |     +-- Historia oceny w czasie
  |
  +-- Wiedza Światów (WORLD/*.json)
  |     |
  |     +-- WORLD_MATCH_DATABASE.json - Baza meczów
  |     |
  |     +-- WORLD_LEVEL_1_ANALYSIS.json - Analiza poziomu 1
  |     |
  |     +-- WORLD_LEVEL_2_ANALYSIS.json - Analiza poziomu 2
  |
  +-- Modele (modele_*/*.h5)
        |
        +-- modele_kursy_przygotowane/ - Modele dla cech kursowych
        |
        +-- modele_dataBase_futbol_trend/ - Modele dla bazy trendów
```

**Mechanizmy Współpracy:**
- **Wiedza Dziedziczona:** Nowe modele korzystają z pamięci światów (WORLD)
- **UCzenie Ciągłe:** Pamięć obserwacji jest aktualizowana przy każdym uruchomieniu
- **Ocena Kolektywna:** Wspólna ocena wszystkich modeli w systemie
- **Hierarchia Świata:** Wybór optymalnego poziomu doświadczenia

---

## POZIOM 7: NOWA WIEDZA

### Generowanie Wiedzy:

**Źródła Nowej Wiedzy:**
1. **Analiza Korelacji** (CZESC3.PY 3B): Korelacje Pearsona między cechami a celami
2. **Feature Importance** (CZESC1.PY SEKCJA F): Ważność cech z Random Forest
3. **Statystyki Predykcji** (CZESC2.PY, CZESC4.PY): Trafienia, błędy, pewność
4. **Hierarchia Światów** (CZESC3.PY 3B): Wiedza o różnych poziomach abstrakcji
5. **Dynamiczne Wagi** (CZESC3.PY 3B): Adaptacyjne wagi świata i modelu

**Formy Wiedzy:**
- **Wiedza Jawną:** pliki JSON (PAMIEC_MODEL_POZNAWCZY.json, WIEDZA_DLA_MODELU_DOCELOWEGO.json)
- **Wiedza Utajona:** parametry modeli sieci neuronowych (.h5)
- **Wiedza Statystyczna:** ranking cech, korelacje, skuteczność
- **Wiedza Hierarchiczna:** struktura światów na 3 poziomach

---

## POZIOM 8: AKTUALIZACJA SYSTEMU

### Ciągłe Uczenie:

```
NOWE DANE WEJSCIOWE
  |
  v
[CZESC1.PY] --- Przetwarzanie i klasyfikacja
  |
  v
[CZESC3.PY 3A] --- Trening nowych modeli (jeśli potrzebne)
  |
  v
[CZESC3.PY 3B] --- Aktualizacja wiedzy nauczyciela
  |
  v
[CZESC2.PY] --- Predykcja z nowymi danymi
  |
  v
[CZESC4.PY] --- Analiza trendów i konsolidacja
  |
  v
AKTUALIZACJA PAMIĘCI I OCENY
  |
  v
+-- pamiec_obserwacji.json (nowe rejestry)
|
+-- ocena.json (nowe statystyki)
|
+-- WORLD/*.json (nowe doświadczenia)
|
+-- modele/*/*.h5 (nowe/caffected modele)
```

**Cykle Aktualizacji:**
1. **Cykliczne:** CZESC1 → CZESC2 → CZESC3 → CZESC4 (pewny przeplyw)
2. **Inkrementalne:** Nowe dane → CZESC1 → CZESC2/CZESC4
3. **Ewolucyjne:** Nowe wiedza → CZESC3 (CognitiveTeacher) → CZESC2/CZESC4

---

## PUNKTY WEJŚCIA DLA KOMPONENTÓW

### Punkty Wejścia dla Teacherów:
| Komponent | Punkt Wejścia | Format | Opis |
|-----------|---------------|--------|------|
| CognitiveTeacher | `__init__(df, cechy, siec_name)` | DataFrame, list, str | Inicjalizacja z danymi historycznymi |
| CognitiveTeacher | `prepare_teacher_targets()` | - | Przygotowanie celów nauczyciela (Y_teacher) |
| CognitiveTeacher | `oblicz_korelacje(X, y_teacher)` | ndarray, ndarray | Obliczanie korelacji Pearsona |
| WorldHierarchyManager | `wybierz_najlepszy_poziom(world_key)` | str | Wybór optymalnego pozioma świata |
| DynamicWeightsManager | `oblicz_wage_swiata(...)` | float params | Obliczanie dynamicznej wagi |

### Punkty Wejścia dla Agentów:
| Komponent | Punkt Wejścia | Format | Opis |
|-----------|---------------|--------|------|
| czesc2.py | `load_model(KATALOG_MODELU)` | str | Ładowanie modelu do predykcji |
| czesc2.py | Wczytanie pamięci (PLIK_PAMIEC) | JSON | Odczyt istniejącej pamięci |
| czesc2.py | SEKCJA 2.L: Analiza historii | - | Główny algorytm obserwacji |
| czesc4.py | Wczytanie metadanych | JSON | Konfiguracja modelu i cech |
| czesc4.py | SEKCJA 4.I: Analiza | - | Analiza predykcji i wyników |

### Punkty Wejścia dla Kolektywu:
| Komponent | Punkt Wejścia | Format | Opis |
|-----------|---------------|--------|------|
| Pamięć Obserwacji | `pamiec_obserwacji.json` | JSON | Wspólna baza doświadczeń |
| Ocena Modeli | `ocena.json` | JSON | Wspólne metryki efektywności |
| Hierarchia Światów | `WORLD/*.json` | JSON | Wspólna wiedza o światach |
| modele | `*.h5, metadata.json, klasy.json` | H5, JSON | Wspólne modele i konfiguracje |

---

## ZALEŻNOŚCI MIĘDZY KOMPONENTAMI

### Macierz Zależności:

| Z | CZESC1 | CZESC2 | CZESC3 3A | CZESC3 3B | CZESC4 |
|---|--------|--------|-----------|-----------|--------|
| **CZESC1** | - | Pliki CSV | Pliki CSV | - | Pliki CSV |
| **CZESC2** | Pliki CSV | - | model.h5 | - | Pliki JSON |
| **CZESC3 3A** | Pliki CSV | - | - | - | - |
| **CZESC3 3B** | - | - | - | - | WORLD JSON |
| **CZESC4** | Pliki CSV | model.h5 | - | - | - |

**Legenda:**
- **Pliki CSV:** dane/*, modele_*/*/walidacja_40_procent.csv
- **model.h5:** Wygenerowany w CZESC3 3A, używany w CZESC2 i CZESC4
- **Pliki JSON:** metadata.json, klasy.json, pamięć, ocena, WORLD/*

---

## PODSUMOWANIE PRZEPŁYWU WIEDZY

### 8 Poziomów Abstrakcji:
1. **Dane Surowa** → Przetwarzanie i ekstrakcja cech
2. **Modele Statystyczne** → RF, Poisson, Dixon-Coles
3. **Sieci Neuronowe** → Trening i walidacja
4. **System Poznawczy** → Hierarchia światów, dynamiczne wagi
5. **Agent Predykcyjne** → Predykcja i obserwacja
6. **Laboratorium** → Analiza trendów i konsolidacja
7. **Kolektyw** → Wspólna pamięć i ocena
8. **Nowa Wiedza** → Aktualizacja systemu

### Kluczowe Zasady:
- ✅ **Brak mieszania zbiorów**: CognitiveTeacher używa WYŁĄCZNIE rzeczywistych wyników (Y)
- ✅ **Hierarchiczna pamięć**: 3 poziomy światów (POZIOM1-3)
- ✅ **Dynamiczne wagi**: Adaptacyjne wagowanie świata i modelu
- ✅ **Ciągła obserwacja**: Pamięć aktualizowana w każdym cyklu
- ✅ **Wspólna wiedza**: Kolektyw korzysta z tych samych struktur pamięci

### Główne Związki:
- CZESC1 → CZESC3 → CZESC2/CZESC4 (przepływ modeli)
- CZESC2 ↔ CZESC4 (podobne funkcjonalności, różne zastosowania)
- CZESC3 3B → CZESC2/CZESC4 (wiedza nauczyciela → agenti)
- WORLD JSON → WorldHierarchyManager → CognitiveTeacher → Agenci

---

## TODO
- [ ] Uzupełnić szczegóły implementacyjne dla CognitiveTeacher
- [ ] Dodać diagramy sekwencyjne dla kluczowych przepływów
- [ ] Zdefiniować interfejsy API między komponentami
- [ ] Opisać mechanizmy synchronizacji pamięci
- [ ] Określić protokoły komunikacji kolektywu

---

## HISTORIA ZMIAN
- **2026-08-03**: Utworzenie dokumentu - Podstawowa struktura przepływu wiedzy
- **2026-08-03**: Dodanie poziomów abstrakcji i punktów wejścia
- **2026-08-03**: Uzupełnienie macierzy zależności i zasad systemu
