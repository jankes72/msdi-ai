# SSI_V5_GENERATOR_FINAL_CODE_MAP.md

## Pelna Mapa Kodu Generatora SSI V5

**Data:** 2026-08-03  
**Status:** W TRAKCIE - Etap 1A  
**Wersja:** 1.0  
**Cel:** Jedno zrodlo prawdy dla calego systemu generatora

---

## STRUKTURA DOKUMENTU

```
CZESC1.PY (27,066 linii)
├── SEKCJA A:  1-228    → Globalne struktury SSI V5
├── SEKCJA B: 234-473   → Funkcje pomocnicze
├── SEKCJA C: 477-664   → Przetwarzanie CSV (subway)
├── SEKCJA D: 705-2032  → Klasyfikacja kursow
├── SEKCJA E: 2039-2488 → Dopasowywanie historyczne
├── SEKCJA F: 2494-3625 → Modelowanie (RF + Poisson+Dixon)
└── SEKCJA G: 3626+      → Predykcja Poisson+Dixon v2

CZESC2.PY (19,718 linii)
└── [DO ANALIZY]

CZESC3.PY (19,692 linii)
├── CZESC 3A: 1-979      → Budowa sieci neuronowych kursow
└── CZESC 3B: 989+       → System WORLD
    ├── WorldHierarchyManager: 1082-1276
    ├── DynamicWeightsManager: 1282-1367
    └── CognitiveTeacher: 1373+

CZESC4.PY (23,386 linii)
├── SEKCJA 4.A:  1-20      → Importy i konfiguracja
├── SEKCJA 4.B: 21-74      → Konfiguracja sciezek
├── SEKCJA 4.C: 79-100     → Wczytanie metadanych modelu
├── SEKCJA 4.D: 109-135    → Wczytanie klas wynikowych
├── SEKCJA 4.E: 141-217    → Wczytanie aktualnej predykcji CSV
├── SEKCJA 4.F: 178-217    → Mapowanie cech modelu
├── SEKCJA 4.G: 220-254    → Przygotowanie danych predykcji
├── SEKCJA 4.H: 257-299    → Wczytanie historii z wynikami
├── SEKCJA 4.I: 302-319    → Wczytanie modelu
├── SEKCJA 4.J: 324-354    → Predykcja historii
├── SEKCJA 4.K: 356-384    → Predykcja aktualnych meczow
├── SEKCJA 4.L: 389-413    → Wczytanie pamięci obserwacji
├── SEKCJA 4.M: 421-472    → Wczytanie oceny modelu
├── SEKCJA 4.N: 477-497    → Inicjalizacja struktur sesji
├── SEKCJA 4.O: 536-727    → Analiza historii z wynikami
├── SEKCJA 4.P: 732-791    → Aktualne mecze bez wyniku
├── SEKCJA 4.Q: 798-913    → Aktualizacja ocena modelu
├── SEKCJA 4.R: 921-947    → Zapis pamięci obserwacji
├── SEKCJA 4.S: 953-979    → Zapis oceny modelu
├── SEKCJA 4.T: 988-1016   → Zapis aktualnej predykcji CSV
└── SEKCJA 4.U: 1024-1048  → Zapis historii z wynikami CSV
```

---

## CZESC 1.PY

### SEKCJA 1.A: Globalne Struktury SSI V5 (1-228)

| Element | Wartosc |
|--------|--------|
| **Zakres** | Linie 1-228 czesc1.py |
| **Funkcje** | update_stage_status, register_agent_input, export_agent_output, SSI_EVENT, SSI_START_NETWORK_BUILD, SSI_START_TRAINING, SSI_END_TRAINING, SSI_OUTPUT_READY, SSI_NETWORK_FINISH, SSI_MAIN_LOOP_START, SSI_MAIN_LOOP_END |
| **Struktury** | SSI_STAGE_STATUS, SSI_AGENT_INPUT, SSI_AGENT_OUTPUT, SSI_EVENTS |
| **Wejscie** | - |
| **Wyjscie** | Globalne struktury SSI |
| **Uzytkownicy** | Caly system (czesc1-4.py) |
| **Zaleznosci** | - |

**Szczegoly:**
- Importy: csv, math, statistics, os, sys, time, datetime
- CSV config: csv.field_size_limit(sys.maxsize)

---

### SEKCJA 1.B: Funkcje Pomocnicze (234-473)

| Element | Wartosc |
|--------|--------|
| **Zakres** | Linie 234-473 czesc1.py |
| **Funkcje** | normalize, bezpieczny_log, oblicz_cechy_3kursy_rozszerzone |
| **Wejscie** | value, min_val, max_val (normalize); value (bezpieczny_log); bloki (oblicz_cechy) |
| **Wyjscie** | znormalizowana wartosc; logarytm; lista 42 cech |
| **Uzytkownicy** | caly plik czesc1.py, czesc3.py, czesc4.py |
| **Zaleznosci** | SEKCJA 1.A (importy) |

**Szczegoly:**
- normalize(value, min_val, max_val): Normalizacja do [0,1]
- bezpieczny_log(value): math.log(max(value, 1.01))
- oblicz_cechy_3kursy_rozszerzone(bloki): 42 cechy z kursow (patrz SEKCJA 1.C)

**42 Cechy:**
1-3: zmiana_1, zmiana_X, zmiana_2
4-6: amplituda_1, amplituda_X, amplituda_2  
7-9: tempo_1, tempo_X, tempo_2
10: synchronizacja
11-13: max_wahanie_1, max_wahanie_X, max_wahanie_2
14-16: start_1, start_X, start_2 (raw)
17-19: koniec_1, koniec_X, koniec_2 (raw)
20-25: log_start_1, log_start_X, log_start_2, log_koniec_1, log_koniec_X, log_koniec_2
26-31: ratio_1X_start, ratio_1_2_start, ratio_X2_start, ratio_1X_koniec, ratio_1_2_koniec, ratio_X2_koniec
32-34: mean_1, mean_X, mean_2
35-37: median_1, median_X, median_2
38-40: stdev_1, stdev_X, stdev_2
41: czas_h

---

### SEKCJA 1.C: Przetwarzanie CSV (477-664)

| Element | Wartosc |
|--------|--------|
| **Zakres** | Linie 477-664 czesc1.py |
| **Funkcje** | przetworz_plik_3kursy_rozszerzone |
| **Wejscie** | nazwa_pliku (CSV), nazwa_wyjsciowa (CSV) |
| **Wyjscie** | CSV z 42 cechami + id_meczu |
| **Uzytkownicy** | czesc2.py, czesc3.py, czesc4.py |
| **Zaleznosci** | SEKCJA 1.A (SSI hooks), SEKCJA 1.B (oblicz_cechy) |

**Szczegoly:**
- Przetwarza pliki: ./dane/database_poprawne_dzisiaj.csv → ./dane/dataBase_futbol_popularne_trend.csv
- Przetwarza pliki: ./dane/database_dzisiaj.csv → ./dane/dataBase_futbol_trend.csv
- Sprawdza SSI_AGENT_INPUT["files_to_process"] dla dodatkowych plikow
- Format: delimiter=";", encoding="utf-8-sig" (in), encoding="utf-8" (out)
- Wywołuje oblicz_cechy_3kursy_rozszerzone dla kazdego wiersza
- Hooki SSI: update_stage_status, export_agent_output

**Pliki wejsciowe (STANDARD):**
- ./dane/database_popularne_dzisiaj.csv
- ./dane/database_dzisiaj.csv

**Pliki wyjsciowe (STANDARD):**
- ./dane/dataBase_futbol_popularne_trend.csv
- ./dane/dataBase_futbol_trend.csv (WYJSCIE DO czesc2, czesc3B, czesc4)

---

### SEKCJA 1.D: Klasyfikacja Kursow (705-2032)

| Element | Wartosc |
|--------|--------|
| **Zakres** | Linie 705-2032 czesc1.py |
| **Funkcje** | [DO DOKLADNEJ ANALIZY] |
| **Wejscie** | ./dane/database_popularne_dzisiaj.csv |
| **Wyjscie** | ./dane/kursy_popularne_przygotowane.csv |
| **Uzytkownicy** | czesc3A (sieci kursow) |
| **Zaleznosci** | SEKCJA 1.C (przetwarzanie CSV) |

**Szczegoly:**
- [TODO: Analiza w nastepnym etapie]

---

### SEKCJA 1.E: Dopasowywanie Historyczne (2039-2488)

| Element | Wartosc |
|--------|--------|
| **Zakres** | Linie 2039-2488 czesc1.py |
| **Funkcje** | [DO DOKLADNEJ ANALIZY] |
| **Wejscie** | [DO OKRESLENIA] |
| **Wyjscie** | [DO OKRESLENIA] |
| **Uzytkownicy** | [DO OKRESLENIA] |
| **Zaleznosci** | SEKCJA 1.D |

**Szczegoly:**
- [TODO: Analiza w nastepnym etapie]

---

### SEKCJA 1.F: Modelowanie (2494-3625)

| Element | Wartosc |
|--------|--------|
| **Zakres** | Linie 2494-3625 czesc1.py |
| **Funkcje** | [DO DOKLADNEJ ANALIZY] |
| **Wejscie** | [DO OKRESLENIA] |
| **Wyjscie** | [DO OKRESLENIA] |
| **Uzytkownicy** | [DO OKRESLENIA] |
| **Zaleznosci** | SEKCJA 1.E |

**Szczegoly:**
- [TODO: Analiza w nastepnym etapie]

---

### SEKCJA 1.G: Predykcja Poisson+Dixon v2 (3626+)

| Element | Wartosc |
|--------|--------|
| **Zakres** | Linie 3626+ czesc1.py |
| **Funkcje** | [DO DOKLADNEJ ANALIZY] |
| **Wejscie** | [DO OKRESLENIA] |
| **Wyjscie** | modele_dataBase_futbol_trend/siec_08_log_koniec/model.h5, metadata.json, klasy.json |
| **Uzytkownicy** | czesc2.py, czesc4.py |
| **Zaleznosci** | SEKCJA 1.F |

**Szczegoly:**
- Wyjscie: model.h5, metadata.json, klasy.json w katalogu modele_dataBase_futbol_trend/siec_08_log_koniec/
- Uzywane przez czesc2 i czesc4 do predykcji

---

## CZESC 2.PY

### [DO ANALIZY]

---

## CZESC 3.PY

### CZESC 3A: Budowa Sieci Neuronowych (1-979)

| Element | Wartosc |
|--------|--------|
| **Zakres** | Linie 1-979 czesc3.py |
| **Funkcje** | buduj_siec, podziel_dane, main loop |
| **Klasy** | Sequential (tensorflow) |
| **Wejscie** | dane/kursy_przygotowane.csv, dane/mozg_kursy_przygotowane.csv |
| **Wyjscie** | modele_kursy_przygotowane/{nazwa_sieci}/model.h5, klasy.json, metadata.json, historia.json, walidacja_40_procent.csv |
| **Uzytkownicy** | System predykcji kursow |
| **Zaleznosci** | - |

**Szczegoly:**
- 5 sieci: siec_01_start_kursow, siec_02_koniec_kursow, siec_03_zmiana_kursow, siec_04_procent_kursow, dataBase_futbol_trend
- Podzial danych: 50% trening, 10% walidacja, 40% obserwacja
- Model: Sequential [Input(32)→Dense(32,relu)→Dense(64,relu)→Dropout(0.2)→Dense(15,softmax)]
- Kompilacja: optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"]
- Szkolenie: epochs=200, batch_size=32, EarlyStopping(patience=20)

---

### CZESC 3B: System WORLD (989+)

#### WorldHierarchyManager (1082-1276)

| Element | Wartosc |
|--------|--------|
| **Zakres** | Linie 1082-1276 czesc3.py |
| **Klasy** | WorldHierarchyManager |
| **Wejscie** | WORLD/aktualny/WORLD_MATCH_DATABASE.json, WORLD_LEVEL_1_ANALYSIS.json, WORLD_LEVEL_2_ANALYSIS.json |
| **Wyjscie** | world_data, level_1_data, level_2_data (w pamieci) |
| **Uzytkownicy** | CognitiveTeacher |
| **Zaleznosci** | - |

**Metody:**
- __init__(world_match_db_path, level_1_path, level_2_path)
- _load_world_data()
- get_world_levels(world_key)
- wybierz_najlepszy_poziom(world_key, min_samples) **GLOWNA METODA**
- _extract_world_stats(world_data)
- _extract_level_stats(level_data)
- _parse_world_stats(stats)
- _oblicz_srednie_gole(wyniki_docelowe)

---

#### DynamicWeightsManager (1282-1367)

| Element | Wartosc |
|--------|--------|
| **Zakres** | Linie 1282-1367 czesc3.py |
| **Klasy** | DynamicWeightsManager |
| **Wejscie** | poziom, ilosc_przypadkow, procent_gospodarze, procent_remis, procent_goscie, korelacje_stabilnosc, dc_accuracy |
| **Wyjscie** | waga_swiata, wagi_klas, wagi_modelu_i_swiata |
| **Uzytkownicy** | CognitiveTeacher |
| **Zaleznosci** | - |

**Metody:**
- __init__()
- oblicz_wage_swiata() **GLOWNA METODA**
  - wzor: 0.4*ilosc_norm + 0.3*skutecznosc_norm + 0.2*stabilnosc_norm + 0.1*dc_norm
- oblicz_wagi_klas(procent_gospodarze, procent_remis, procent_goscie, waga_swiata)
- oblicz_wagi_modelu_i_swiata(waga_swiata)

---

#### CognitiveTeacher (1373+)

| Element | Wartosc |
|--------|--------|
| **Zakres** | Linie 1373+ czesc3.py |
| **Klasy** | CognitiveTeacher |
| **Wejscie** | df, cechy, siec_name |
| **Wyjscie** | PAMIEC_MODEL_POZNAWCZY.json, WIEDZA_DLA_MODELU_DOCELOWEGO.json |
| **Uzytkownicy** | - |
| **Zaleznosci** | WorldHierarchyManager, DynamicWeightsManager |

**Metody:**
- __init__(df, cechy, siec_name, use_rf)
- parse_wynik(wynik_str)
- prepare_teacher_targets()
- oblicz_korelacje(X, y_teacher)

---

## CZESC 4.PY

### SEKCJA 4.A: Importy i Konfiguracja (1-20)

| Element | Wartosc |
|--------|--------|
| **Zakres** | Linie 1-20 czesc4.py |
| **Importy** | os, json, pandas, numpy, datetime, tensorflow.keras.models.load_model |
| **Wejscie** | - |
| **Wyjscie** | - |
| **Uzytkownicy** | caly plik czesc4.py |
| **Zaleznosci** | - |

---

### SEKCJA 4.B: Konfiguracja Sciezek (21-74)

| Element | Wartosc |
|--------|--------|
| **Zakres** | Linie 21-74 czesc4.py |
| **Zmienne** | KATALOG_MODELU, PLIK_PREDYKCJI, PLIK_HISTORIA, KATALOG_OBSERWACJI, KATALOG_PREDYKCJI, PLIK_PAMIEC, PLIK_OCENA |
| **Wejscie** | - |
| **Wyjscie** | Sciezki do katalogow i plikow |
| **Uzytkownicy** | Wszystkie sekcje czesc4.py |
| **Zaleznosci** | - |

**Sciezki:**
- KATALOG_MODELU = r"modele_dataBase_futbol_trend\siec_08_log_koniec"
- PLIK_PREDYKCJI = r"dane\dataBase_futbol_trend.csv" (WEJSCIE z czesc1 SEKCJA C)
- PLIK_HISTORIA = r"dane\kod_dataBase_futbol_trend.csv" (WEJSCIE z czesc1 SEKCJA D)
- KATALOG_OBSERWACJI = os.path.join(KATALOG_MODELU, "obserwacja")
- KATALOG_PREDYKCJI = os.path.join(KATALOG_MODELU, "predykcje")
- PLIK_PAMIEC = os.path.join(KATALOG_OBSERWACJI, "pamiec_obserwacji.json")
- PLIK_OCENA = os.path.join(KATALOG_OBSERWACJI, "ocena.json")

---

## PRZEPLYW DANYCH POMIEDZY CZESCIAMI

### GLOWNE WEJSCIA/WYJSCIA:

| Plik | Producent | Konsument |
|------|-----------|-----------|
| dane/dataBase_futbol_trend.csv | czesc1 SEKCJA C | czesc2, czesc3B, czesc4 |
| dane/kod_dataBase_futbol_trend.csv | czesc1 SEKCJA D | czesc2, czesc3B, czesc4 |
| modele_dataBase_futbol_trend/siec_08_log_koniec/model.h5 | czesc1 SEKCJA G | czesc2, czesc4 |
| modele_dataBase_futbol_trend/siec_08_log_koniec/metadata.json | czesc1 SEKCJA G | czesc4 |
| modele_dataBase_futbol_trend/siec_08_log_koniec/klasy.json | czesc1 SEKCJA G | czesc4 |

### CYKL GLOWNY:
```
czesc1 (przygotowanie) → czesc2 (predykcja 1/2) → czesc4 (analiza 2/2)
                                                  ↑______________________↓
                                             (povera pamięci i oceny)
```

---

## Stan Analizy

| Sekcja | Status | Uczen |
|--------|--------|-------|
| 1.A | ✅ | 100% |
| 1.B | ✅ | 100% |
| 1.C | ✅ | 100% |
| 1.D | ⏳ | 0% |
| 1.E | ⏳ | 0% |
| 1.F | ⏳ | 0% |
| 1.G | ⏳ | 0% |
| 2.* | ⏳ | 0% |
| 3A.* | ✅ | 100% (podsumowanie) |
| 3B.* | ✅ | 100% (podsumowanie) |
| 4.* | ✅ | 100% |

---

## TODO
- [ ] Analiza Szczegolowa 1.D (705-2032)
- [ ] Analiza Szczegolowa 1.E (2039-2488)
- [ ] Analiza Szczegolowa 1.F (2494-3625)
- [ ] Analiza Szczegolowa 1.G (3626+)
- [ ] Analiza czesc2.py (19,718 linii)
- [ ] Utworzenie SSI_V5_GENERATOR_CONSOLIDATION_PLAN.md
