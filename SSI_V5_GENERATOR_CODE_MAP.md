# SSI_V5_GENERATOR_CODE_MAP.md

## Mapa Kodu Generatora SSI V5 - Konsolidacja czesc1-4.py

**Data:** 2026-08-03  
**Status:** ✅ **CZESC1.PY ZAKOŃCZONA** | ✅ **CZESC2.PY ZAKOŃCZONA** | ✅ **CZESC3.PY ZAKOŃCZONA** | ✅ **CZESC4.PY ZAKOŃCZONA**  
**Wersja:** 2.0  
**Cel:** Dokumentacja struktur kodu przed konsolidacja do SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py

---

## 🔚 **STATUS ANALIZY CZESC1.PY: ✅ ZAKOŃCZONA 100%**

| Sekcja | Zakres | Docelowy moduł | Status |
|--------|--------|----------------|--------|
| **A** | 1-228 | `core/ssi_globals.py` + `core/hooks.py` | ✅ |
| **B** | 234-473 | `core/utils.py` + `data_processing/feature_engineering.py` | ✅ |
| **C** | 477-1300 | `data_processing/csv_processor.py` | ✅ |
| **D** | 1344-2032 | `modeling/classification.py` | ✅ |
| **E** | 2039-2488 | `modeling/matching.py` | ✅ |
| **F** | 2494-3611 | `modeling/complex_models.py` | ✅ |
| **G** | 3612+ | `modeling/neural_networks.py` + `modeling/complex_models.py` | ✅ |

---

---

## PODSUMOWANIE ARCHITEKTURY

### Odkryte Komponenty SSI V5:
1. **WorldHierarchyManager** (czesc3.py:1082-1276) - Zarzadza hierarchiczna pamiecia swiatow
2. **DynamicWeightsManager** (czesc3.py:1282-1367) - Dynamiczne wagi swiata i klas
3. **CognitiveTeacher** (czesc3.py:1373+) - Model poznawczy, uzywa komponentow 1 i 2

### Podzial czesc3.py:
- **Czesc 3A** (linie 1-979): Budowa sieci neuronowych na dane/kursy_przygotowane.csv
- **Czesc 3B** (linie 989+): System WORLD z WorldHierarchyManager, DynamicWeightsManager, CognitiveTeacher

### Wejscia Wyjscia czesc3.py:
- **Czesc 3A:** dane/kursy_przygotowane.csv + dane/mozg_kursy_przygotowane.csv -> modele_kursy_przygotowane/
- **Czesc 3B:** dane/dataBase_futbol_trend.csv + dane/kod_dataBase_futbol_trend.csv -> modele_dataBase_futbol_trend/

---

## CZESC 1.PY - ANALIZA

### SEKCJA 1.A: Globalne Struktury SSI V5
| Sekcja | 1.A | Zrodlo | czesc1.py | Linie | 1-228 |
|---|---|---|---|---|---|
| Funkcje/Klasy | SSI_STAGE_STATUS, SSI_AGENT_INPUT, SSI_AGENT_OUTPUT, SSI_EVENTS, update_stage_status, register_agent_input, export_agent_output, SSI_EVENT, SSI_START_NETWORK_BUILD, SSI_START_TRAINING, SSI_END_TRAINING, SSI_OUTPUT_READY, SSI_NETWORK_FINISH, SSI_MAIN_LOOP_START, SSI_MAIN_LOOP_END |
| Wejscie | - | Wyjscie | SSI_STAGE_STATUS, SSI_AGENT_INPUT, SSI_AGENT_OUTPUT, SSI_EVENTS |
| Uzytkownicy | Caly system SSI V5 | Zaleznosci | - |

**Opis:**
Globalne struktury dla agentow SSI V5:
- SSI_STAGE_STATUS (dict): Rejestr statusu procesu
- SSI_AGENT_INPUT (dict): Punkty wejscia dla agentow
- SSI_AGENT_OUTPUT (dict): Punkty wyjscia dla agentow
- SSI_EVENTS (list): Lista zdarzen systemowych

Funkcje zarzadzania stanem:
- update_stage_status(stage, status, timestamp)
- register_agent_input(data_type, data)
- export_agent_output(data_type, data)

Hooki zdarzen (Event Logging):
- SSI_EVENT(event, network, stage, status, data)
- SSI_START_NETWORK_BUILD(network, features)
- SSI_START_TRAINING(network, X_train_shape, y_train_shape, X_val_shape, epochs, batch_size)
- SSI_END_TRAINING(network, accuracy, loss, val_accuracy, val_loss, duration)
- SSI_OUTPUT_READY(network, catalog, file_list, model_accuracy)
- SSI_NETWORK_FINISH(network)
- SSI_MAIN_LOOP_START(total_networks)
- SSI_MAIN_LOOP_END(completed_networks, skipped_networks)

**Zaleznosci:**
- Importy: csv, math, statistics, os, sys, time, datetime
- CSV config: csv.field_size_limit(sys.maxsize)

---

### SEKCJA 1.B: Funkcje Pomocnicze
| Sekcja | 1.B | Zrodlo | czesc1.py | Linie | 234-473 |
|---|---|---|---|---|---|
| Funkcje/Klasy | normalize, bezpieczny_log, oblicz_cechy_3kursy_rozszerzone |
| Wejscie | value, min_val, max_val (normalize); value (bezpieczny_log); bloki (oblicz_cechy_*) |
| Wyjscie |.remote znormalizowana wartosc; logarytm; lista 42 cech |
| Uzytkownicy | caly plik czesc1.py, czesc3.py, czesc4.py | Zaleznosci | SEKCJA 1.A (importy) |

**Opis:**
Funkcje pomocnicze dla przetwarzania kursow:
- **normalize(value, min_val, max_val)**: Normalizacja wartosci do zakresu [0,1]
  - Jezeli max_val - min_val == 0: zwraca 0.5
  - max(0, min(1, (value - min_val) / (max_val - min_val)))

- **bezpieczny_log(value)**: Logarytm naturalny z zabezpieczeniem
  - return math.log(max(value, 1.01))

- **oblicz_cechy_3kursy_rozszerzone(bloki)**: Glowna funkcja obliczania cech
  - Wejscie: bloki = lista krotek (kurs_1, kurs_X, kurs_2, czas)
  - Wyjscie: lista 42 znormalizowanych cech:
    
  **Cechy zwracane (42 elementy):**
  
  1-3: zmiana_1, zmiana_X, zmiana_2 (normalizowane -100 do 100)
  4-6: amplituda_1, amplituda_X, amplituda_2 (normalizowane 0 do 100)
  7-9: tempo_1, tempo_X, tempo_2 (normalizowane -50 do 50)
  10: synchronizacja (0 lub 1)
  11-13: max_wahanie_1, max_wahanie_X, max_wahanie_2 (wartosci absolutne)
  14-16: start_1, start_X, start_2 (normalizowane 1.01 do 10)
  17-19: koniec_1, koniec_X, koniec_2 (normalizowane 1.01 do 10)
  20-22: log_start_1, log_start_X, log_start_2 (normalizowane logarytmy)
  23-25: log_koniec_1, log_koniec_X, log_koniec_2 (normalizowane logarytmy)
  26-28: ratio_1X_start, ratio_1_2_start, ratio_X2_start (normalizowane 0 do 10)
  29-31: ratio_1X_koniec, ratio_1_2_koniec, ratio_X2_koniec (normalizowane 0 do 10)
  32-34: mean_1, mean_X, mean_2 (normalizowane 1 do 10)
  35-37: median_1, median_X, median_2 (normalizowane 1 do 10)
  38-40: stdev_1, stdev_X, stdev_2 (normalizowane 0 do 5)
  41: czas_h (godziny)

  **Obliczenia:**
  - zmiana_X = ((start_X - koniec_X) / start_X) * 100
  - amplituda_X = ((max(kurs_X) - min(kurs_X)) / start_X) * 100
  - tempo_X = zmiana_X / czas_h
  - synchronizacja = 1 if (wszystkie zmiany > 0) or (wszystkie zmiany < 0) else 0
  - max_wahanie_X = max(|kurs_X[i+1] - kurs_X[i]| for all i)
  - ratio_1X_start = start_1 / start_X
  - stat_mean/median/stdev = statistics functions on kurs lists

**Zaleznosci:**
- Uzywa: normalize(), bezpieczny_log()
- Importy: math, statistics

---

### SEKCJA 1.C: Przetwarzanie CSV (linie 477-664)
| Sekcja | 1.C | Zrodlo | czesc1.py | Linie | 477-664 |
|---|---|---|---|---|---|
| Funkcje/Klasy | przetworz_plik_3kursy_rozszerzone |
| Wejscie | nazwa_pliku (CSV), nazwa_wyjsciowa (CSV) |
| Wyjscie | CSV z 42 cechami + id_meczu |
| Uzytkownicy | czesc2.py, czesc3.py, czesc4.py | Zaleznosci | SEKCJA 1.A (SSI hooks), SEKCJA 1.B (oblicz_cechy_*) |

**Opis:**
Funkcja przetwarzania pliku CSV z kursami na rozszerzone cechy:
- **przetworz_plik_3kursy_rozszerzone(nazwa_pliku, nazwa_wyjsciowa)**

**Proces:**
1. Sprawdza czy agent dostarczył custom_data (SSI_AGENT_INPUT)
2. Sprawdza istnienie pliku wejsciowego
3. Otwiera plik wejsciowy (encoding="utf-8-sig") i wyjsciowy (encoding="utf-8")
4. Czytanie CSV z delimiter=";" (csv.reader)
5. Pisanie CSV z delimiter=";" (csv.writer)
6. Naglowek wyjsciowy: id_meczu + 42 cechy (zobacz SEKCJA 1.B)
7. Dla kazdego wiersza:
   - Pomija wiersze z len(row) < 7
   - mecz = row[2] (id meczu)
   - Bloki: lista krotek (k1, kX, k2, czas) z krokow 4 (row[3], row[4], row[5], row[6], itd.)
   - Pomija wiersze z len(bloki) < 2
   - Oblicza cechy: oblicz_cechy_3kursy_rozszerzone(bloki)
   - Zapisuje: mecz + [round(x,5) for x in cechy]
8. Liczniki: zapisano, pominieto
9. Hooki SSI: update_stage_status, export_agent_output

**Format wejsciowy CSV:**
- Delimiter: ";"
- Encoding: utf-8-sig
- Kolumny: [?, ?, id_meczu, k1, kX, k2, czas, k1, kX, k2, czas, ...]
- Bloki kursow: kazde 4 kolumny = (k1, kX, k2, czas)

**Format wyjsciowy CSV:**
- Delimiter: ";"
- Encoding: utf-8
- Naglowek: id_meczu + 42 cechy (patrz SEKCJA 1.B)
- Dane: kazdy wiersz = [id_meczu, cecha1, cecha2, ..., cecha42]

**Hooki SSI:**
- SSI_AGENT_HOOK_START (linie 481): update_stage_status("file_processing", "start")
- SSI_AGENT_HOOK_END (linie 656-663): update_stage_status + export_agent_output
- Bledy: update_stage_status("file_processing", "error") + SSI_STAGE_STATUS["errors"]

**Zaleznosci:**
- Uzywa: oblicz_cechy_3kursy_rozszerzone z SEKCJA 1.B
- Uzywa: SSI_STAGE_STATUS, SSI_AGENT_INPUT z SEKCJA 1.A

---

### SEKCJA 1.D: Klasyfikacja Kursow (linie 705-2032)
| Sekcja | 1.D | Zrodlo | czesc1.py | Linie | 705-2032 |


## LEGENDA

| Kolumna | Opis |
|--------|------|
| Sekcja | Logiczna czesc kodu |
| Zrodlo | Plik zrodlowy (czesc1-4.py) |
| Linie | Zakres linii w pliku zrodlowym |
| Funkcje/Klasy | Glowne elementy kodu |
| Wejscie | Dane wejsciowe |
| Wyjscie | Dane wyjsciowe |
| Uzytkownicy | Kto korzysta z tych danych |
| Zaleznosci | Zaleznosci od innych sekcji |

---

## CZESC 2.PY - ANALIZA

### CZESC 2.PY - PREDYKCJA I PAMIEC OBSERWACJI (Część 1/2)
**Opis:** Główny system predykcji inspirowany genetyką, wykorzystujacy wytrenowane modele do generowania predykcji meczów piłkarskich oraz zarządzania pamięcią obserwacji i oceny modelu.

### SEKCJA 2.A: Importy i Konfiguracja
| Sekcja | 2.A | Zrodlo | czesc2.py | Linie | 1-74 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | - | Wyjscie | KATALOG_MODELU, KATALOG_OBSERWACJI, KATALOG_PREDYKCJI, PLIK_PAMIEC, PLIK_OCENA |
| Uzytkownicy | Caly plik czesc2.py | Zaleznosci | - |
| Opis | Importy: os, json, pandas, numpy, datetime, tensorflow.keras.models.load_model. Konfiguracja ścieżek dla modelu, obserwacji i predykcji. Tworzenie katalogów obserwacji i predykcji. |

### SEKCJA 2.B: Wczytanie Metadanych Modelu
| Sekcja | 2.B | Zrodlo | czesc2.py | Linie | 79-107 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | metadata.json | Wyjscie | metadata, CECHY, NAZWA_MODELU |
| Uzytkownicy | SEKCJA 2.C, SEKCJA 2.E | Zaleznosci | SEKCJA 2.A (KATALOG_MODELU) |
| Opis | Wczytanie pliku metadata.json z katalogu modelu. Ekstrakcja listy cech (CECHY) i nazwy modelu (NAZWA_MODELU). |

### SEKCJA 2.C: Wczytanie Klas
| Sekcja | 2.C | Zrodlo | czesc2.py | Linie | 110-136 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | klasy.json | Wyjscie | klasy, ID_NA_WYNIK (dict) |
| Uzytkownicy | SEKCJA 2.L, SEKCJA 2.M, SEKCJA 2.N | Zaleznosci | SEKCJA 2.A (KATALOG_MODELU) |
| Opis | Wczytanie pliku klasy.json. Tworzenie odwrotnego mapowania ID_NA_WYNIK: {int(v): k for k,v in klasy.items()}. |

### SEKCJA 2.D: Wczytanie Aktualnej Predykcji
| Sekcja | 2.D | Zrodlo | czesc2.py | Linie | 141-177 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | PLIK_PREDYKCJI (CSV) | Wyjscie | df_pred, INDEX_MAP, NAZWY_PREDYKCJI |
| Uzytkownicy | SEKCJA 2.E, SEKCJA 2.F | Zaleznosci | SEKCJA 2.A (PLIK_PREDYKCJI), SEKCJA 1.C (dostarcza plik) |
| Opis | Ładowanie CSV z aktualnymi meczami do predykcji. Tworzenie mapy kolumn INDEX_MAP i listy nazw meczów NAZWY_PREDYKCJI. Wyświetlanie MAPA CECH (debug). |

### SEKCJA 2.E: Mapowanie Cech
| Sekcja | 2.E | Zrodlo | czesc2.py | Linie | 180-217 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | CECHY, INDEX_MAP | Wyjscie | INDEX_CECH (lista indeksów) |
| Uzytkownicy | SEKCJA 2.F, SEKCJA 2.G | Zaleznosci | SEKCJA 2.B (CECHY), SEKCJA 2.D (INDEX_MAP) |
| Opis | Mapowanie nazw cech na indeksy kolumn. Walidacja obecności wszystkich cech modelu w danych predykcyjnych. |

### SEKCJA 2.F: Wczytanie Historii z Wynikami
| Sekcja | 2.F | Zrodlo | czesc2.py | Linie | 221-299 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | PLIK_HISTORIA (CSV) | Wyjscie | hist, NAZWY_HISTORIA, X_HISTORIA, Y_HISTORIA |
| Uzytkownicy | SEKCJA 2.H, SEKCJA 2.I | Zaleznosci | SEKCJA 2.A (PLIK_HISTORIA), SEKCJA 1.C (dostarcza plik) |
| Opis | Ładowanie historycznych danych meczów z wynikami (header=None). Ekstrakcja NAZWY_HISTORIA, X_HISTORIA (cechy), Y_HISTORIA (wyniki). Konwersja NaN do 0. |

### SEKCJA 2.G: Wczytanie Modelu
| Sekcja | 2.G | Zrodlo | czesc2.py | Linie | 306-321 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | model.h5 | Wyjscie | model (TensorFlow) |
| Uzytkownicy | SEKCJA 2.H, SEKCJA 2.I | Zaleznosci | SEKCJA 2.A (KATALOG_MODELU), SEKCJA 3.A (dostarcza model.h5) |
| Opis | Ładowanie wytrenowanego modelu sieci neuronowej z pliku model.h5 za pomocą tensorflow.keras.models.load_model. |

### SEKCJA 2.H: Predykcja Historii
| Sekcja | 2.H | Zrodlo | czesc2.py | Linie | 327-356 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | model, X_HISTORIA | Wyjscie | pred_hist, klasy_pred_hist |
| Uzytkownicy | SEKCJA 2.L | Zaleznosci | SEKCJA 2.G (model), SEKCJA 2.F (X_HISTORIA) |
| Opis | Generowanie predykcji dla historycznych meczów. pred_hist = model.predict(X_HISTORIA). klasy_pred_hist = np.argmax(pred_hist, axis=1). |

### SEKCJA 2.I: Predykcja Aktualnych Meczów
| Sekcja | 2.I | Zrodlo | czesc2.py | Linie | 358-387 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | model, X_PREDYKCJA | Wyjscie | pred, klasy_pred |
| Uzytkownicy | SEKCJA 2.M | Zaleznosci | SEKCJA 2.G (model), SEKCJA 2.F (X_PREDYKCJA) |
| Opis | Generowanie predykcji dla aktualnych meczów bez wyników. Analogiczny proces do SEKCJA 2.H. |

### SEKCJA 2.J: Wczytanie Pamięci i Oceny
| Sekcja | 2.J | Zrodlo | czesc2.py | Linie | 391-472 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | PLIK_PAMIEC (opcjonalnie), PLIK_OCENA (opcjonalnie) | Wyjscie | pamiec_obserwacji, ocena |
| Uzytkownicy | SEKCJA 2.L, SEKCJA 2.N, SEKCJA 2.O | Zaleznosci | SEKCJA 2.A (PLIK_PAMIEC, PLIK_OCENA) |
| Opis | Wczytanie istniejącej pamięci obserwacji i oceny modelu. Jeśli pliki nie istnieją, tworzone są domyślne struktury: pamiec_obserwacji = {}, ocena = {model, ocena_ogolna, ocena_wynikow}. |

### SEKCJA 2.K: Struktury Sesji
| Sekcja | 2.K | Zrodlo | czesc2.py | Linie | 478-529 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | - | Wyjscie | czas, nowe_obserwacje, nowe_predykcje, nowa_historia, analiza |
| Uzytkownicy | SEKCJA 2.L, SEKCJA 2.M, SEKCJA 2.N | Zaleznosci | - |
| Opis | Inicjalizacja struktur dla bieżącej sesji: czas (timestamp), listy nowych obserwacji/predykcji, analiza (statystyki na poziomie klas wyników: ilosc_wystapien, trafienia, bledy). |

### SEKCJA 2.L: Analiza Historii z Wynikami
| Sekcja | 2.L | Zrodlo | czesc2.py | Linie | 538-729 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | klasy_pred_hist, Y_HISTORIA, NAZWY_HISTORIA, pred_hist, pamiec_obserwacji, analiza | Wyjscie | pamiec_obserwacji (updated), analiza (updated), nowe_obwersacje |
| Uzytkownicy | SEKCJA 2.N, SEKCJA 2.O | Zaleznosci | SEKCJA 2.H, SEKCJA 2.F, SEKCJA 2.J, SEKCJA 2.K |
| Opis | **GŁÓWNY ALGORYTM OBSERWACJI HISTORII**. Dla każdego meczu historycznego: pobieranie predykcji, porównanie z rzeczywistym wynikiem, obliczanie pewności (max probability), sprawdzanie trafienia. Aktualizacja pamięci obserwacji z nowym rekordem. Śledzenie zmian predykcji i pewności między sesjami. Aktualizacja statystyk analizy na poziomie klas. |

### SEKCJA 2.M: Aktualne Mecze bez Wyniku
| Sekcja | 2.M | Zrodlo | czesc2.py | Linie | 733-795 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | klasy_pred, pred, NAZWY_PREDYKCJI | Wyjscie | nowe_predykcje |
| Uzytkownicy | SEKCJA 2.O | Zaleznosci | SEKCJA 2.I, SEKCJA 2.D |
| Opis | Generowanie listy nowych predykcji dla aktualnych meczów (bez znanych wyników). Każda predykcja zawiera: id_meczu, id_grupy, wynik_predykcji, pewnosc. |

### SEKCJA 2.N: Aktualizacja Oceny Modelu
| Sekcja | 2.N | Zrodlo | czesc2.py | Linie | 800-914 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | analiza | Wyjscie | ocena (updated) |
| Uzytkownicy | SEKCJA 2.O | Zaleznosci | SEKCJA 2.L (analiza), SEKCJA 2.J (ocena) |
| Opis | **GŁÓWNY ALGORYTM OCENY MODELU**. Agregacja statystyk z analizy historii: ilosc_globalna, trafienia_globalne, ocena_wynikow (per klasa). Obliczanie skutecznosci = trafienia/ilosc na poziomie klas i globalnie. Tworzenie struktury oceny do zapisania. |

### SEKCJA 2.O: Zapis Pamięci, Ocena i Predykcje
| Sekcja | 2.O | Zrodlo | czesc2.py | Linie | 923-1149 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | pamiec_obserwacji, ocena, nowe_predykcje, pamiec_obserwacji | Wyjscie | PLIK_PAMIEC (JSON), PLIK_OCENA (JSON), predykcja_grupy.csv, predykcja_z_wynikiem.csv |
| Uzytkownicy | - | Zaleznosci | SEKCJA 2.L, SEKCJA 2.M, SEKCJA 2.N, SEKCJA 2.J |
| Opis | Zapis wszystkich wygenerowanych danych: (1) pamięć obserwacji do JSON, (2) ocena modelu do JSON, (3) aktualne predykcje do CSV, (4) historia z wynikami do CSV. Wyświetlanie podsumowania ścieżek plików. |

---

## CZESC 4.PY - ANALIZA

### SEKCJA 4.A: Importy i Konfiguracja
| Sekcja | 4.A | Zrodlo | czesc4.py | Linie | 1-74 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | - | Wyjscie | KATALOG_MODELU, PLIK_PREDYKCJI, PLIK_HISTORIA |
| Uzytkownicy | Caly plik czesc4.py | Zaleznosci | - |
| Opis | Importy: os, json, pandas, numpy, datetime, tensorflow.keras.models.load_model. Konfiguracja ścieżek dla modelu i danych. Tworzenie katalogów obserwacji i predykcji (podobnie do czesc2.py). |

### SEKCJA 4.B: Wczytanie Modelu i Metadanych
| Sekcja | 4.B | Zrodlo | czesc4.py | Linie | 79-135 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | metadata.json, klasy.json | Wyjscie | metadata, CECHY, NAZWA_MODELU, klasy, ID_NA_WYNIK |
| Uzytkownicy | SEKCJA 4.D, SEKCJA 4.E | Zaleznosci | SEKCJA 4.A (KATALOG_MODELU) |
| Opis | Wczytanie pliku metadata.json z Katalogu modelu. Ekstrakcja listy cech (CECHY) i nazwy modelu (NAZWA_MODELU). Wczytanie klas i tworzenie odwrotnego mapowania ID_NA_WYNIK. |

### SEKCJA 4.C: Wczytanie Danych CSV
| Sekcja | 4.C | Zrodlo | czesc4.py | Linie | 141-217 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | PLIK_PREDYKCJI (CSV) | Wyjscie | df_pred, INDEX_MAP |
| Uzytkownicy | SEKCJA 4.D, SEKCJA 4.E | Zaleznosci | SEKCJA 4.A (PLIK_PREDYKCJI), SEKCJA 1.C (dostarcza plik) |
| Opis | Ładowanie CSV z aktualnymi meczami do predykcji (sep=";"). Tworzenie mapy kolumn INDEX_MAP. |

### SEKCJA 4.D: Mapowanie Cech
| Sekcja | 4.D | Zrodlo | czesc4.py | Linie | 178-217 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | CECHY, INDEX_MAP | Wyjscie | INDEX_CECH (lista indeksów) |
| Uzytkownicy | SEKCJA 4.E | Zaleznosci | SEKCJA 4.B (CECHY), SEKCJA 4.C (INDEX_MAP) |
| Opis | Mapowanie nazw cech na indeksy kolumn dla potrzeb modelu. Walidacja obecności wszystkich cech modelu w danych. |

### SEKCJA 4.E: Przygotowanie Danych
| Sekcja | 4.E | Zrodlo | czesc4.py | Linie | 220-299 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | df_pred, PLIK_HISTORIA, INDEX_CECH | Wyjscie | X_PREDYKCJA, X_HISTORIA, Y_HISTORIA |
| Uzytkownicy | SEKCJA 4.G | Zaleznosci | SEKCJA 4.C (df_pred), SEKCJA 4.A (PLIK_HISTORIA), SEKCJA 4.D (INDEX_CECH) |
| Opis | Ekstrakcja X_PREDYKCJA (cechy dla aktualnych predykcji), X_HISTORIA i Y_HISTORIA (cechy i wyniki historyczne). Konwersja NaN do 0 za pomocą np.nan_to_num. |

### SEKCJA 4.F: Ładowanie Modelu
| Sekcja | 4.F | Zrodlo | czesc4.py | Linie | 302-319 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | model.h5 | Wyjscie | model (TensorFlow) |
| Uzytkownicy | SEKCJA 4.G | Zaleznosci | SEKCJA 4.A (KATALOG_MODELU), SEKCJA 3.A (dostarcza model.h5) |
| Opis | Ładowanie wytrenowanego modelu sieci neuronowej z pliku model.h5 za pomocą tensorflow.keras.models.load_model. |

### SEKCJA 4.G: Predykcja
| Sekcja | 4.G | Zrodlo | czesc4.py | Linie | 324-384 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | model, X_HISTORIA, X_PREDYKCJA | Wyjscie | pred_hist, klasy_pred_hist, pred, klasy_pred |
| Uzytkownicy | SEKCJA 4.I, SEKCJA 4.J | Zaleznosci | SEKCJA 4.F (model), SEKCJA 4.E (X_HISTORIA, X_PREDYKCJA) |
| Opis | **GŁÓWNY SYSTEM PREDYKCJI**. Generowanie predykcji dla danych historycznych (pred_hist) i aktualnych (pred). Użycie model.predict() i np.argmax() do obtencji klas decyzyjnych. |

### SEKCJA 4.H: Wczytanie Pamięci i Oceny
| Sekcja | 4.H | Zrodlo | czesc4.py | Linie | 389-472 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | PLIK_PAMIEC (opcjonalnie), PLIK_OCENA (opcjonalnie) | Wyjscie | pamiec_obserwacji, ocena |
| Uzytkownicy | SEKCJA 4.I, SEKCJA 4.K | Zaleznosci | SEKCJA 4.A (PLIK_PAMIEC, PLIK_OCENA) |
| Opis | Wczytanie istniejącej pamięci obserwacji i oceny modelu z plików JSON. Jeśli pliki nie istnieją, tworzone są domyślne struktury (podobnie do czesc2.py SEKCJA J). |

### SEKCJA 4.I: Inicjalizacja i Analiza
| Sekcja | 4.I | Zrodlo | czesc4.py | Linie | 477-727 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | pred_hist, X_HISTORIA, pamiec_obserwacji | Wyjscie | pamiec_obserwacji (updated), analiza |
| Uzytkownicy | SEKCJA 4.K | Zaleznosci | SEKCJA 4.G (pred_hist, X_HISTORIA), SEKCJA 4.H (pamiec_obserwacji) |
| Opis | **GŁÓWNY ALGORYTM ANALIZY HISTORII**. Inicjalizacja struktur sesji. Dla każdego historycznego meczu: porównanie pred_hist z Y_HISTORIA, obliczanie pewności, śledzenie trafień i błędów. Aktualizacja pamięci obserwacji i statystyk analizy (podobnie do czesc2.py SEKCJA L). |

### SEKCJA 4.J: Aktualne Predykcje
| Sekcja | 4.J | Zrodlo | czesc4.py | Linie | 732-791 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | klasy_pred, pred, NAZWY_PREDYKCJI | Wyjscie | nowe_predykcje (lista słowników) |
| Uzytkownicy | SEKCJA 4.K | Zaleznosci | SEKCJA 4.G (klasy_pred, pred), SEKCJA 4.C (NAZWY_PREDYKCJI) |
| Opis | Generowanie listy nowych predykcji dla aktualnych meczów (bez znanych wyników). Każda predykcja zawiera: id_meczu, id_grupy, wynik_predykcji, pewnosc (podobnie do czesc2.py SEKCJA M). |

### SEKCJA 4.K: Aktualizacja i Zapis
| Sekcja | 4.K | Zrodlo | czesc4.py | Linie | 798-1048 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | analiza, ocena, pamiec_obserwacji, nowe_predykcje | Wyjscie | ocena.json, pamiec_obserwacji.json, predykcja_grupy.csv, predykcja_grupy_historia.csv |
| Uzytkownicy | - | Zaleznosci | SEKCJA 4.I (analiza), SEKCJA 4.H (ocena, pamiec_obserwacji), SEKCJA 4.J (nowe_predykcje) |
| Opis | **GŁÓWNY SYSTEM ZAPISU**. Aktualizacja oceny modelu na podstawie statystyk analizy. Zapis: (1) pamięć obserwacji do JSON, (2) ocena modelu do JSON, (3) aktualne predykcje do predykcja_grupy.csv, (4) historia z wynikami do predykcja_grupy_historia.csv (podobnie do czesc2.py SEKCJA O). |

---

## PRZEPLYW DANYCH CZESC4.PY

### Wejscia zewnetrzne:
1. czesc1.py SEKCJA C -> dane/dataBase_futbol_trend.csv
2. czesc1.py SEKCJA D -> dane/kod_dataBase_futbol_trend.csv  
3. czesc1.py SEKCJA G -> modele_dataBase_futbol_trend/siec_08_log_koniec/model.h5
4. KATALOG_MODELU/metadata.json
5. KATALOG_MODELU/klasy.json
6. KATALOG_OBSERWACJI/pamiec_obserwacji.json (opcjonalnie)
7. KATALOG_OBSERWACJI/ocena.json (opcjonalnie)

### Wyjscia:
1. modele_dataBase_futbol_trend/siec_08_log_koniec/obserwacja/pamiec_obserwacji.json
2. modele_dataBase_futbol_trend/siec_08_log_koniec/obserwacja/ocena.json
3. modele_dataBase_futbol_trend/siec_08_log_koniec/predykcje/predykcja_grupy.csv
4. modele_dataBase_futbol_trend/siec_08_log_koniec/predykcje/predykcja_grupy_historia.csv

---

## CZESC 3.PY - ANALIZA

### Część 3A: Budowa Sieci Neuronowych Kursów (linie 1-978)
**Opis:** System budowy i trenowania sieci neuronowych na podstawie przygotowanych danych kursowych.

#### SEKCJA 3A.A: Importy i Konfiguracja
| Sekcja | 3A.A | Zrodlo | czesc3.py | Linie | 1-51 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | - | Wyjscie | PLIK_PREDYKCJI, PLIK_TRENING, KATALOG_MODELE |
| Uzytkownicy | Caly plik 3A | Zaleznosci | - |
| Opis | Importy: os, json, pandas, numpy, sklearn, tensorflow.keras. Konfiguracja ścieżek plików i tworzenie katalogu modeli. |

#### SEKCJA 3A.B: Definicja Klas Wyników
| Sekcja | 3A.B | Zrodlo | czesc3.py | Linie | 53-95 |
|---|---|---|---|---|---|
| Funkcje/Klasy | WYNIKI, MAPA_KLAS | Wejscie | - | Wyjscie | WYNIKI (15 wyników), MAPA_KLAS (dict) |
| Uzytkownicy | SEKCJA 3A.C, SEKCJA 3B | Zaleznosci | - |
| Opis | Definicja 15 możliwych wyników meczów piłkarskich i mapowanie na indeksy klas. |

#### SEKCJA 3A.C: Spojrzenia Świata (Feature Groups)
| Sekcja | 3A.C | Zrodlo | czesc3.py | Linie | 97-140 |
|---|---|---|---|---|---|
| Funkcje/Klasy | SPOJRZENIA | Wejscie | - | Wyjscie | SPOJRZENIA (dict z 4 grupami cech) |
| Uzytkownicy | SEKCJA 3A.G, SEKCJA 3B | Zaleznosci | - |
| Opis | Definicja 4 grup cech (spojrzeń): siec_01_start_kursow, siec_02_koniec_kursow, siec_03_zmiana_kursow, siec_04_procent_kursow. Każda grupa zawiera 3 cechy. |

#### SEKCJA 3A.D: Wczytanie Schematu Kolumn
| Sekcja | 3A.D | Zrodlo | czesc3.py | Linie | 143-178 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | PLIK_PREDYKCJI (CSV) | Wyjscie | predykcja (DataFrame), NAGLOWKI (lista) |
| Uzytkownicy | SEKCJA 3A.E | Zaleznosci | SEKCJA 3A.A |
| Opis | Ładowanie CSV z przygotowanymi danymi kursowymi i ekstrakcja nazw kolumn. |

#### SEKCJA 3A.E: Wczytanie Historii bez Nagłówka
| Sekcja | 3A.E | Zrodlo | czesc3.py | Linie | 181-237 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | PLIK_TRENING (CSV) | Wyjscie | df (DataFrame) z kolumną 'wynik' |
| Uzytkownicy | SEKCJA 3A.F, SEKCJA 3A.G | Zaleznosci | SEKCJA 3A.A, SEKCJA 3A.D (NAGLOWKI) |
| Opis | Ładowanie historycznych danych z wynikami (header=None). Przypisanie nazw kolumn z NAGLOWKI + 'wynik'. Filtrowanie pułapnych rekordów. |

#### SEKCJA 3A.F: Filtrowanie i Identyfikacja Klasy
| Sekcja | 3A.F | Zrodlo | czesc3.py | Linie | 220-255 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | df, WYNIKI, MAPA_KLAS | Wyjscie | df (przefiltrowany) z kolumną 'klasa' |
| Uzytkownicy | SEKCJA 3A.G | Zaleznosci | SEKCJA 3A.E, SEKCJA 3A.B |
| Opis | Filtrowanie DataFrame do rekordów z poprawnymi wynikami. Dodanie kolumny 'klasa' poprzez mapowanie wyników na indeksy. |

#### SEKCJA 3A.G: Funkcja Podziału Danych
| Sekcja | 3A.G | Zrodlo | czesc3.py | Linie | 257-328 |
|---|---|---|---|---|---|
| Funkcje/Klasy | podziel_dane(X, y) | Wejscie | X, y | Wyjscie | X_train, X_val, X_obserwacja, y_train, y_val, y_obserwacja |
| Uzytkownicy | SEKCJA 3A.H (buduj_siec) | Zaleznosci | sklearn.model_selection.train_test_split |
| Opis | Podział danych na: 50% trening, 10% walidacja, 40% obserwacja. Używa stratyfikacji na podstawie y. |

#### SEKCJA 3A.H: Funkcja Budowy Sieci
| Sekcja | 3A.H | Zrodlo | czesc3.py | Linie | 331-920 |
|---|---|---|---|---|---|
| Funkcje/Klasy | buduj_siec(nazwa, cechy) | Wejscie | nazwa, cechy, df | Wyjscie | model.h5, klasy.json, metadata.json, historia.json, walidacja_40_procent.csv |
| Uzytkownicy | SEKCJA 3A.I | Zaleznosci | SEKCJA 3A.F (df), SEKCJA 3A.G (podziel_dane) |
| Opis | **GŁÓWNA FUNKCJA BUDOWY SIECI NEURONOWYCH**. Dla danego zbioru cech: (1) podział danych, (2) normalizacja StandardScaler, (3) konwersja klas do one-hot, (4) budowa modelu Sequential z 2 warstwami Dense (32, 64) + Dropout(0.2) + warstwa wyjściowa softmax, (5) kompilacja (adam, categorical_crossentropy), (6) trening z EarlyStopping (200 epoch, batch_size=32), (7) walidacja na zbiorze walidacyjnym, (8) predykcja na 40% zbiorze obserwacyjnym, (9) zapis modelu i metadanych. |

#### SEKCJA 3A.I: Uruchomienie Budowy Sieci
| Sekcja | 3A.I | Zrodlo | czesc3.py | Linie | 924-978 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | SPOJRZENIA | Wyjscie | Zbudowane modele dla każdej grupy cech |
| Uzytkownicy | - | Zaleznosci | SEKCJA 3A.C (SPOJRZENIA), SEKCJA 3A.H (buduj_siec) |
| Opis | Iteracja po wszystkich spojrzeniach (sieciach) i uruchomienie buduj_siec() dla każdego. Pominięcie spojrzeń z brakującymi cechami w df. |

---

### Część 3B: System WORLD z CognitiveTeacher (linie 989+)
**Opis:** System poznawczy SSI V5 oparty na hierarchicznej pamięci światów, dynamicznych wagach i modelu nauczyciela.

#### SEKCJA 3B.A: Importy i Konfiguracja 3B
| Sekcja | 3B.A | Zrodlo | czesc3.py | Linie | 980-1016 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | - | Wyjscie | PLIK_PREDYKCJI, PLIK_TRENING, KATALOG_MODELE |
| Uzytkownicy | Caly plik 3B | Zaleznosci | - |
| Opis | Importy uzupełniające: RandomForestRegressor, permutation_importance, Counter, defaultdict, scipy.stats. Konfiguracja ścieżek (przelaczenie na dataBase_futbol_trend). |

#### SEKCJA 3B.B: Definicja Klas Wyników i Spojrzeń 3B
| Sekcja | 3B.B | Zrodlo | czesc3.py | Linie | 1018-1056 |
|---|---|---|---|---|---|
| Funkcje/Klasy | WYNIKI, MAPA_KLAS, SPOJRZENIA | Wejscie | - | Wyjscie | WYNIKI (15 wyników), MAPA_KLAS, SPOJRZENIA (dataBase_futbol_trend) |
| Uzytkownicy | SEKCJA 3B.F | Zaleznosc | - |
| Opis | Ponowna definicja klas wyników i pojedynczego spojrzenia 'dataBase_futbol_trend' z 36 cechami. |

#### SEKCJA 3B.C: Konfiguracja Pamięci Światów
| Sekcja | 3B.C | Zrodlo | czesc3.py | Linie | 1058-1069 |
|---|---|---|---|---|---|
| Funkcje/Klasy | - | Wejscie | - | Wyjscie | WORLD_DATA_PATH, WORLD_LEVEL_1_PATH, WORLD_LEVEL_2_PATH, WORLD_FULL_GROUP_PATH, MIN_SAMPLES_* |
| Uzytkownicy | SEKCJA 3B.D | Zaleznosci | - |
| Opis | Definicja ścieżek do plików WORLD i minimalnych liczb próbek dla trzech poziomów hierarchii. |

#### SEKCJA 3B.D: Definicja Klas Wyników do Klasyfikacji
| Sekcja | 3B.D | Zrodlo | czesc3.py | Linie | 1071-1077 |
|---|---|---|---|---|---|
| Funkcje/Klasy | KLASA_WYGRANA_GOSPODARZE, KLASA_REMIS, KLASA_WYGRANA_GOSCIE | Wejscie | - | Wyjscie | 3 listy wyników pogrupowane po typie |
| Uzytkownicy | SEKCJA 3B.F (CognitiveTeacher) | Zaleznosci | - |
| Opis | Podział 15 wyników na 3 kategorie: wygrana gospodarzy (6), remis (3), wygrana gości (6). |

#### SEKCJA 3B.E: WorldHierarchyManager (linie 1079-1276)
| Sekcja | 3B.E | Zrodlo | czesc3.py | Linie | 1079-1276 |
|---|---|---|---|---|---|
| Funkcje/Klasy | WorldHierarchyManager | Wejscie | WORLD_*.json | Wyjscie | Obiekty z hierarchiczną pamięcią świata |
| Uzytkownicy | SEKCJA 3B.G (CognitiveTeacher) | Zaleznosci | SEKCJA 3B.C (ścieżki) |
| Opis | **KOMPONENT SSI V5 - ZARZĄDCA HIERARCHII ŚWIATÓW**. Zarządza 3-poziowową hierarchią pamięci: POZIOM1 (szeroki, >100 próbek), POZIOM2 (średni, >50 próbek), POZIOM3 (pełny, >20 próbek). Metody: _load_world_data() - ładuje pliki JSON, get_world_levels(world_key) - zwraca dostępne poziomy, wybierz_najlepszy_poziom() - **GŁÓWNY ALGORYTM** wybierający optymalny poziom na podstawie ilości danych, _extract_world_stats(), _parse_world_stats(), _oblicz_srednie_gole(). |

#### SEKCJA 3B.F: DynamicWeightsManager (linie 1278-1367)
| Sekcja | 3B.F | Zrodlo | czesc3.py | Linie | 1278-1367 |
|---|---|---|---|---|---|
| Funkcje/Klasy | DynamicWeightsManager | Wejscie | Statystyki świata | Wyjscie | Dynamiczne wagi (0-1) |
| Uzytkownicy | SEKCJA 3B.G (CognitiveTeacher) | Zaleznosci | - |
| Opis | **KOMPONENT SSI V5 - DYNAMICZNE WAGI**. Zarządza wagami świata na podstawie: ilości próbek (40%), skuteczności (30%), stabilności korelacji (20%), zgodności Dixon-Coles (10%). Metody: oblicz_wage_swiata() - **GŁÓWNY ALGORYTM WAG**, oblicz_wagi_klas() - wagi per klasa wyników, oblicz_wagi_modelu_i_swiata() - balans pomiędzy modelem a światem. |

#### SEKCJA 3B.G: CognitiveTeacher (linie 1369+)
| Sekcja | 3B.G | Zrodlo | czesc3.py | Linie | 1369+ |
|---|---|---|---|---|---|
| Funkcje/Klasy | CognitiveTeacher | Wejscie | df, cechy, siec_name | Wyjscie | PAMIEC_MODEL_POZNAWCZY.json, WIEDZA_DLA_MODELU_DOCELOWEGO.json |
| Uzytkownicy | - | Zaleznosci | SEKCJA 3B.E (WorldHierarchyManager), SEKCJA 3B.F (DynamicWeightsManager) |
| Opis | **KOMPONENT SSI V5 - MODEL POZNAWCZY (NAUCZYCIEL)**. Główne zadania: (1) Analiza historycznych danych WYŁĄCZNIE z rzeczywistych wyników (Y), (2) Korzystanie z WorldHierarchyManager i DynamicWeightsManager, (3) Generowanie wiedzy dla modelu docelowego. Metody: parse_wynik() - rozbijanie wyniku na gole, prepare_teacher_targets() - Y_teacher = [gole_dom, gole_wyj, suma], oblicz_korelacje() - korelacje Pearsona, ... (**CIĄG DALSZY W CZESC3.PY**) |

### Wejscia Wyjscia czesc3.py:
- **Czesc 3A:** 
  - Wejscia: dane/kursy_przygotowane.csv, dane/mozg_kursy_przygotowane.csv
  - Wyjscia: modele_kursy_przygotowane/{nazwa}/model.h5, klasy.json, metadata.json, historia.json, walidacja_40_procent.csv
  
- **Czesc 3B:**
  - Wejscia: dane/dataBase_futbol_trend.csv, dane/kod_dataBase_futbol_trend.csv, WORLD/*.json
  - Wyjscia: modele_dataBase_futbol_trend/{siec_name}/model.h5, PAMIEC_MODEL_POZNAWCZY.json, WIEDZA_DLA_MODELU_DOCELOWEGO.json

---

## TODO
- [x] Analiza czesc1.py (SEKCJA A-G)
- [x] Analiza czesc2.py (SEKCJA 2.A-2.O)
- [x] Analiza czesc3.py (SEKCJA 3A.A-3A.I, 3B.A-3B.G)
- [x] Analiza czesc4.py (SEKCJA 4.A-4.K)
- [x] Mapa wejscia/wyjscia (SSI_V5_GENERATOR_DATA_FLOW_MAP.md)
- [x] Raport konsolidacji (SSI_V5_GENERATOR_CONSOLIDATION_REPORT.md)
- [x] Mapa przeplywu wiedzy (SSI_V5_KNOWLEDGE_FLOW_MAP.md)
- [ ] Konsolidacja kodu do SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py

---

## 📌 **PEŁNA DOKUMENTACJA SEKCJI CZESC1.PY**

### --- SEKCJA F (2494-3611): Modelowanie RF + Poisson + Dixon-Coles ---

| Sekcja | F | Zrodlo | czesc1.py | Linie | 2494-3611 |
|---|---|---|---|---|---|
| **Funkcje/Klasy** | `poisson()`, `dixon_coles()`, `policz_dc()`, `rozbij_wynik()`, `wynik_1x2()`, `wynik_gole()` |
| **Wejscie** | `dopasowane_trendy_historyczne.csv`, `wagi_dopasowania.csv` |
| **Wyjscie** | `analiza_poisson_dixon.csv`, `analiza_korelacji_cech.csv`, `random_forest_waznosc_cech.csv`, `ranking_cech.csv`, `syntetyczne_trendy_historyczne.csv` |
| **Uzytkownicy** | SEKCJA G (dane wejściowe) | **Zaleznosci** | SEKCJA E (dostarcza pliki wejściowe) |

**Opis:**
- **Ładowanie danych:** `dopasowane_trendy_historyczne.csv` (z SEKCJA E) + `wagi_dopasowania.csv` (merge po `id_meczu_predykcja`)
- **Analiza wyniku:** Funkcje `rozbij_wynik()`, `wynik_1x2()`, `wynik_gole()` do ekstrakcji goli i klas (1/0/2)
- **Poisson + Dixon-Coles:**
  - `poisson(k, lam)`: Rozkład Poissona
  - `dixon_coles(gd, gw, ld, lw)`: Korekta dla rzadkich wyników (RHO_DIXON = -0.1)
  - `policz_dc(row)`: Oblicza prawdopodobieństwo dla każdego wiersza
  - Zapis do `analiza_poisson_dixon.csv`
- **Random Forest:**
  - `RandomForestClassifier(n_estimators=300, random_state=42, class_weight="balanced")`
  - `train_test_split(test_size=0.2, random_state=42)`
  - Feature importance zapisywane do `random_forest_waznosc_cech.csv`
- **Korelacja cech:**
  - Korelacja Pearsona między cechami a `wynik_modelowy` (gole * prawdopodobienstwo_dc)
  - Zapis do `analiza_korelacji_cech.csv`
- **Ranking cech:**
  - `sila = abs(korelacja_dc) * RF * DC` (wagi: 1.0, 1.0, 1.0)
  - Sortowanie malejące po `sila`
  - Zapis do `ranking_cech.csv`
- **Dane syntetyczne:**
  - `LICZBA_SYNTH=3` warianty na rekord
  - `KROK=0.02` modyfikacja cech na podstawie korelacji
  - Zapis do `syntetyczne_trendy_historyczne.csv`

**Parametry:**
- `LICZBA_SYNTH = 3`
- `KROK = 0.02`
- `MAX_GOLE = 8`
- `RHO_DIXON = -0.1`

---

### --- SEKCJA G (3612+): Predykcja Poisson+Dixon v2 + Ranking cech ---

#### Podsekcja G.1 (3613-4228): Predykcja Poisson+Dixon v2

| Sekcja | G.1 | Zrodlo | czesc1.py | Linie | 3613-4228 |
|---|---|---|---|---|---|
| **Funkcje/Klasy** | `rozbij_wynik()`, `pobierz_druzyny()`, `poisson()`, `dixon_coles()`, `macierz_wynikow()` |
| **Wejscie** | `dopasowane_trendy_historyczne.csv` |
| **Wyjscie** | `predykcja_poisson_dc_v2.csv` |
| **Uzytkownicy** | czesc2.py, czesc4.py | **Zaleznosci** | SEKCJA E (dostarcza plik wejściowy) |

**Opis:**
- **Ładowanie:** `dopasowane_trendy_historyczne.csv` (42 kolumny)
- **Wydobywanie drużyn:** `pobierz_druzyny()` (obsługa "-" i " vs ") → `gospodarz`, `gosc`
- **Siła ataku/obrony:**
  - `atak_dom` = średnia goli gospodarza / średnia globalna
  - `obrona_dom` = średnia goli straconych przez gospodarza / średnia globalna
  - Analogicznie dla `atak_wyj`, `obrona_wyj`
- **Macierz wyników:**
  - `lambda_dom = srednia_goli * attack_dom * defence_gosc`
  - `lambda_wyj = srednia_goli_wyj * attack_gosc * defence_dom`
  - `macierz_wynikow(ld, lw)`: Generuje wszystkie kombinacje goli (0-`MAX_GOLE`) z prawdopodobieństwami
- **Predykcja:**
  - Wybiera najwyższe prawdopodobieństwo z macierzy
  - Typ wyniku: `1` (gospodarz), `X` (remis), `2` (gość)
  - Zapis do `predykcja_poisson_dc_v2.csv` (mecz, lambda_dom, lambda_wyj, wynik_model, prawdopodobienstwo, typ)

**Duplikacje:**
- `poisson()` (duplikacja z SEKCJA F)
- `dixon_coles()` (duplikacja z SEKCJA F)
- `rozbij_wynik()` (duplikacja z SEKCJA F)

**Parametry:**
- `MAX_GOLE = 8`
- `RHO_DIXON = -0.1`

---

#### Podsekcja G.2 (4234-4376): Funkcje utylitarne (nieaktywne w czesc1.py)

| Sekcja | G.2 | Zrodlo | czesc1.py | Linie | 4234-4376 |
|---|---|---|---|---|---|
| **Funkcje/Klasy** | `popraw_wynik()`, `load_csv()`, `create_tag_map()` |
| **Wejscie** | - | **Wyjscie** | - |
| **Uzytkownicy** | ? (prawdopodobnie czesc2.py/czesc4.py) | **Zaleznosci** | - |

**Opis:**
- **`popraw_wynik(wynik)`:** Zamiana "3.0" → "3:0"
- **`load_csv(file_path)`:** Ładowanie CSV z automatyczną poprawką wyniku
- **`create_tag_map(data)`:** Grupowanie meczów po tagach (np. grupa ligowa)
- **Uwaga:** Brak wywołań w czesc1.py – prawdopodobnie używane w czesc2.py/czesc4.py

---

#### Podsekcja G.3 (4380-4815): Ranking cech (kursy)

| Sekcja | G.3 | Zrodlo | czesc1.py | Linie | 4380-4815 |
|---|---|---|---|---|---|
| **Funkcje/Klasy** | `klasyfikuj_wynik()`, `normalizuj()` |
| **Wejscie** | `dane/mozg_kursy_przygotowane.csv` (bez nagłówka) |
| **Wyjscie** | `dane/ranking_cech_kursy_przygotowane.csv` |
| **Uzytkownicy** | ? | **Zaleznosci** | - |

**Opis:**
- **Ładowanie:** `mozg_kursy_przygotowane.csv` (`pd.read_csv(header=None, names=KOLUMNY)`)
- **Klasyfikacja:** `klasyfikuj_wynik()` → 1 (gospodarz), 0 (remis), -1 (gość)
- **Korelacja DC:** Korelacja Pearsona między cechami a `klasa`
- **Random Forest:** 500 drzew, `class_weight="balanced"` → feature importance
- **Mutual Information:** `mutual_info_classif` z `StandardScaler`
- **Ranking:**
  - Normalizacja min-max (`korelacja_n`, `rf_n`, `dc_n`)
  - `sila = korelacja_dc * 0.4 + RF * 0.3 + DC * 0.3`
  - Sortowanie malejące po `sila`
- **Zapis:** `ranking_cech_kursy_przygotowane.csv`

---

#### Podsekcja G.4 (4819+): Ranking cech (dataBase)

| Sekcja | G.4 | Zrodlo | czesc1.py | Linie | 4819+ |
|---|---|---|---|---|---|
| **Funkcje/Klasy** | `klasyfikuj_wynik()`, `normalizuj()` |
| **Wejscie** | `dane/kod_dataBase_futbol_trend_klasyfikator.csv` (z nagłówkiem) |
| **Wyjscie** | `dane/ranking_cech_dataBase_futbol_trend_klasyfikator.csv` |
| **Uzytkownicy** | ? | **Zaleznosci** | SEKCJA D.9 (dostarcza plik wejściowy) |

**Opis:**
- **Powtórka G.3** na `kod_dataBase_futbol_trend_klasyfikator.csv`
- **Różnice:** Plik wejściowy **ma nagłówek** (w przeciwieństwie do G.3)

---

## 🔍 **DUPLIKACJE FUNKCJI W CZESC1.PY**

| Funkcja | Zakres | Typ | Decyzja konsolidacyjna |
|---------|--------|-----|----------------------|
| `classify_odds()` | 1347-1448, 1634-1735 | Klasyfikacja kursów (30 poziomów) | Zachować 1 kopię w `modeling/classification.py` |
| `process_and_save_data()` | 1456-1590, 1743-1876 | Przetwarzanie CSV z klasyfikacją | Zachować 1 kopię w `modeling/classification.py` |
| `rozbij_wynik()` | 2597-2608, 3677-3687 | Rozbicie "2:1" → (2, 1) | Zachować 1 kopię w `core/utils.py` |
| `poisson()` | 2680-2711, 3911-3930 | Rozkład Poissona | Zachować 1 kopię w `modeling/complex_models.py` |
| `dixon_coles()` | 2716-2818, 3939-3975 | Korekta Dixon-Coles | Zachować 1 kopię w `modeling/complex_models.py` |

## ⚠️ **FUNKCJE NIEAKTYWNE (DO ZACHOWANIA)**

| Funkcja | Zakres | Typ | Uwagi |
|---------|--------|-----|-------|
| `popraw_wynik()` | 4247-4258 | Zamiana "3.0" → "3:0" | Prawdopodobnie używana w czesc2.py/czesc4.py |
| `load_csv()` | 4273-4313 | Ładowanie CSV z poprawką | Prawdopodobnie używana w czesc2.py/czesc4.py |
| `create_tag_map()` | 4328-4368 | Grupowanie meczów po tagach | Prawdopodobnie używana w czesc2.py/czesc4.py |

---