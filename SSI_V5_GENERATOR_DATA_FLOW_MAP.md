# SSI_V5_GENERATOR_DATA_FLOW_MAP.md

## Mapa Przeplywu Danych Generatora SSI V5

**Data:** 2026-08-03  
**Status:** W TRAKCIE - Mapa wejsc/wyjsc  
**Wersja:** 1.0  
**Cel:** Dokumentacja przeplywu danych miedzy czesc1-4.py

---

## PRZEGLAD OGOLNY

```
CZESC1.PY          CZESC2.PY          CZESC3.PY          CZESC4.PY
     |                  |                  |                  |
     v                  v                  v                  v
[PRZYGOTOWANIE] -> [PREDYKCJA] -> [BUDOWA/NAUKA] -> [ANALIZA+PAMIEC]
     |                  |                  |                  |
     +------------------+------------------+------------------+
                         (PRZEPLYW LINEARNY)
```

---

## CZESC 1.PY - PRZYGOTOWANIE DANYCH

### Wejscia:
| Plik | Sciezka | Format | Zrodlo | Opis |
|------|---------|--------|--------|------|
| Kursy | `dane/kursy.csv` | CSV | Zewnetrzne API | Surowa baza kursow |
| Wyniki | `dane/wyniki.csv` | CSV | Zewnetrzne API | Historyczne wyniki meczow |
| Baza | `dane/dataBase_futbol_trend.csv` | CSV | - | Polaczone dane (WYJSCIE) |
| Historia | `dane/kod_dataBase_futbol_trend.csv` | CSV | - | Historia z wynikami (WYJSCIE) |

### Wyjscia:
| Plik | Sciezka | Format | Uzycie | Zarodlo (Sekcja czesc1) |
|------|---------|--------|--------|---------------------|
| Baza trendow | `dane/dataBase_futbol_trend.csv` | CSV | czesc2, czesc4 | SEKCJA C |
| Historia kodowa | `dane/kod_dataBase_futbol_trend.csv` | CSV | czesc2, czesc3B | SEKCJA C |
| Kursy popularne | `dane/kursy_popularne_przygotowane.csv` | CSV | ? | SEKCJA D |
| Klasyfikacja popularne | `dane/analizaKursowDni_dataBase_futbol_Popularne.csv` | CSV | ? | SEKCJA D |
| Klasyfikacja wszystkie | `dane/analizaKursowDni_dataBase_futbol.csv` | CSV | ? | SEKCJA D |
| Klasyfikator (baza) | `dane/dataBase_futbol_trend_klasyfikator.csv` | CSV | SEKCJA E | SEKCJA D.8 |
| Klasyfikator (kod) | `dane/kod_dataBase_futbol_trend_klasyfikator.csv` | CSV | SEKCJA E | SEKCJA D.9 |
| Dopasowane trendy | `dane/dopasowane_trendy_historyczne.csv` | CSV | SEKCJA F, SEKCJA G | SEKCJA E |
| Wagi dopasowania | `dane/wagi_dopasowania.csv` | CSV | SEKCJA F | SEKCJA E |
| Analiza Poisson+Dixon | `dane/analiza_poisson_dixon.csv` | CSV | ? | SEKCJA F |
| Korelacje cech | `dane/analiza_korelacji_cech.csv` | CSV | ? | SEKCJA F |
| RF ważność cech | `dane/random_forest_waznosc_cech.csv` | CSV | ? | SEKCJA F |
| Ranking cech | `dane/ranking_cech.csv` | CSV | ? | SEKCJA F |
| Dane syntetyczne | `dane/syntetyczne_trendy_historyczne.csv` | CSV | ? | SEKCJA F |
| Predykcja v2 | `dane/predykcja_poisson_dc_v2.csv` | CSV | czesc2, czesc4 | SEKCJA G.1 |
| Ranking cech (kursy) | `dane/ranking_cech_kursy_przygotowane.csv` | CSV | ? | SEKCJA G.3 |
| Ranking cech (dataBase) | `dane/ranking_cech_dataBase_futbol_trend_klasyfikator.csv` | CSV | ? | SEKCJA G.4 |

**Uwaga:** Model `.h5` **NIE JEST GENEROWANY** w czesc1.py. Pliki modeli generowane są w **czesc3.py** (Część 3A).



### Zaleznosci wejsciowe:
- **nie ma** - czesc1.py jest punktem startowym, pobiera dane z zewnatrz (API kursow i wynikow)

### Zaleznosci wyjsciowe:
- **czesc2.py** - korzysta z:
  - `dane/dataBase_futbol_trend.csv` (SEKCJA C)
  - `dane/kod_dataBase_futbol_trend.csv` (SEKCJA C)
  - `dane/predykcja_poisson_dc_v2.csv` (SEKCJA G.1)
- **czesc3.py Czesc 3B** - korzysta z:
  - `dane/dataBase_futbol_trend.csv` (SEKCJA C)
  - `dane/kod_dataBase_futbol_trend.csv` (SEKCJA C)
- **czesc4.py** - korzysta z:
  - `dane/dataBase_futbol_trend.csv` (SEKCJA C)
  - `dane/kod_dataBase_futbol_trend.csv` (SEKCJA C)
  - `dane/predykcja_poisson_dc_v2.csv` (SEKCJA G.1)

**Uwaga:** Modele `.h5` **NIE SĄ GENEROWANE** w czesc1.py. Pliki modeli generowane są w **czesc3.py** (Część 3A).

---

## CZESC 2.PY - PREDYKCJA I PAMIEC OBSERWACJI (Czesc 1/2)

### Wejscia:
| Plik | Sciezka | Zrodlo | Uzycie | Format |
|------|---------|--------|--------|--------|
| Baza predykcji | `dane/dataBase_futbol_trend.csv` | czesc1 SEKCJA C | X_PREDYKCJA, NAZWY_PREDYKCJI | CSV |
| Historia | `dane/kod_dataBase_futbol_trend.csv` | czesc1 SEKCJA D | X_HISTORIA, Y_HISTORIA, NAZWY_HISTORIA | CSV |
| Model | `modele_dataBase_futbol_trend/siec_08_log_koniec/model.h5` | czesc1 SEKCJA G | model.predict() | H5 |
| Metadane | `modele_dataBase_futbol_trend/siec_08_log_koniec/metadata.json` | czesc1 SEKCJA G | CECHY, NAZWA_MODELU | JSON |
| Klasy | `modele_dataBase_futbol_trend/siec_08_log_koniec/klasy.json` | czesc1 SEKCJA G | klasy, ID_NA_WYNIK | JSON |
| Pamiec | `modele_dataBase_futbol_trend/siec_08_log_koniec/obserwacja/pamiec_obserwacji.json` | czesc2 (poprzednie uruchomienie) | pamiec_obserwacji | JSON |
| Ocena | `modele_dataBase_futbol_trend/siec_08_log_koniec/obserwacja/ocena.json` | czesc2 (poprzednie uruchomienie) | ocena | JSON |

### Wyjscia:
| Plik | Sciezka | Format | Opis |
|------|---------|--------|------|
| Pamiec obserwacji | `modele_dataBase_futbol_trend/siec_08_log_koniec/obserwacja/pamiec_obserwacji.json` | JSON | Zaktualizowana pamiec z nowymi obserwacjami |
| Ocena | `modele_dataBase_futbol_trend/siec_08_log_koniec/obserwacja/ocena.json` | JSON | Zaktualizowana ocena modelu |
| Predykcje aktualne | `modele_dataBase_futbol_trend/siec_08_log_koniec/predykcje/predykcja_*.csv` | CSV | Aktualne predykcje meczow |

### Zaleznosci:
- **zalezy od:** czesc1.py (dane wejsciowe i model)
- **uzywana przez:** czesc4.py (kontynuacja analizy i aktualizacji pamięci)

---

## CZESC 3.PY - BUDOWA MODELI I SYSTEM WORLD

### Podzial na dwie czesci:

#### Czesc 3A: Budowa Sieci Neuronowych (linie 1-979)

**Wejscia Czesc 3A:**
| Plik | Sciezka | Format | Zrodlo | Opis |
|------|---------|--------|--------|------|
| Kursy przygotowane | `dane/kursy_przygotowane.csv` | CSV | czesc1? / zewnetrzne | Przetworzone cechy kursow |
| Mozg kursy | `dane/mozg_kursy_przygotowane.csv` | CSV | czesc1? / zewnetrzne | Historia z wynikami do nauki |

**Wyjscia Czesc 3A:**
| Plik | Sciezka | Format | Opis |
|------|---------|--------|------|
| Model sieci N | `modele_kursy_przygotowane/{nazwa_sieci}/model.h5` | H5 | Wytrenowany model dla danego "spojrzenia" |
| Klasy | `modele_kursy_przygotowane/{nazwa_sieci}/klasy.json` | JSON | Mapa klas wynikowych |
| Metadane | `modele_kursy_przygotowane/{nazwa_sieci}/metadata.json` | JSON | Informacje o sieci (nazwa, cechy, dokladnosc) |
| Historia | `modele_kursy_przygotowane/{nazwa_sieci}/historia.json` | JSON | Historia treningu |
| Walidacja 40% | `modele_kursy_przygotowane/{nazwa_sieci}/walidacja_40_procent.csv` | CSV | Dane walidacyjne (40% zbioru) |

**Spojrzenia (Feature Sets):**
- siec_01_start_kursow: [kurs_1_start, kurs_X_start, kurs_2_start]
- siec_02_koniec_kursow: [kurs_1_koniec, kurs_X_koniec, kurs_2_koniec]
- siec_03_zmiana_kursow: [zmiana_kurs_1, zmiana_kurs_X, zmiana_kurs_2]
- siec_04_procent_kursow: [procent_kurs_1, procent_kurs_X, procent_kurs_2]
- dataBase_futbol_trend: [42 cechy trendow]

**Zaleznosci Czesc 3A:**
- **zalezy od:** Pliki wejsciowe kursy (prawdopodobnie wygenerowane przez czesc1 lub zewnetrzne)
- **uzywana przez:** System predykcji kursow (nie wiadomo czy czesc4 korzysta)

---

#### Czesc 3B: System WORLD i Cognitive Teacher (linie 989+)

**Wejscia Czesc 3B:**
| Plik | Sciezka | Format | Zrodlo | Opis |
|------|---------|--------|--------|------|
| Baza trendow | `dane/dataBase_futbol_trend.csv` | CSV | czesc1 SEKCJA C | Aktualne dane do predykcji |
| Historia kodowana | `dane/kod_dataBase_futbol_trend.csv` | CSV | czesc1 SEKCJA D | Historia z wynikami do nauki |
| World Database | `WORLD/aktualny/WORLD_MATCH_DATABASE.json` | JSON | System WORLD | Hierarchiczna baza meczow |
| World Level 1 | `WORLD/aktualny/WORLD_LEVEL_1_ANALYSIS.json` | JSON | System WORLD | Analiza poziomu 1 (szeroki) |
| World Level 2 | `WORLD/aktualny/WORLD_LEVEL_2_ANALYSIS.json` | JSON | System WORLD | Analiza poziomu 2 (sredni) |

**Wyjscia Czesc 3B:**
| Plik | Sciezka | Format | Opis |
|------|---------|--------|------|
| Model | `modele_dataBase_futbol_trend/{siec_name}/model.h5` | H5 | Model wytrenowany przez CognitiveTeacher |
| Pamiec poznawcza | `modele_dataBase_futbol_trend/{siec_name}/PAMIEC_MODEL_POZNAWCZY.json` | JSON | Pamiec modelu CognitiveTeacher |
| Wiedza | `modele_dataBase_futbol_trend/{siec_name}/WIEDZA_DLA_MODELU_DOCELOWEGO.json` | JSON | Wiedza dla modelu docelowego |

**Komponenty SSI V5 w Czesc 3B:**

```
WORLD HIERARCHY MANAGER
├── WORLD_MATCH_DATABASE.json (POZIOM 3 - pelny)
├── WORLD_LEVEL_1_ANALYSIS.json (POZIOM 1 - szeroki)
└── WORLD_LEVEL_2_ANALYSIS.json (POZIOM 2 - sredni)

DYNAMIC WEIGHTS MANAGER
├── waga = 0.4 * ilosc_norm + 0.3 * skutecznosc_norm + 0.2 * stabilnosc_norm + 0.1 * dc_norm
├── oblicz_wage_swiata()
├── oblicz_wagi_klas()
└── oblicz_wagi_modelu_i_swiata()

COGNITIVE TEACHER
├── parse_wynik()
├── prepare_teacher_targets() - Y_teacher = [gole_dom, gole_wyj, suma]
├── oblicz_korelacje()
├── UZYWA: WorldHierarchyManager
└── UZYWA: DynamicWeightsManager
```

**Zaleznosci Czesc 3B:**
- **zalezy od:** czesc1.py (dane wejsciowe)
- **zalezy od:** System WORLD (pliki WORLD/*.json)
- **uzywana przez:** System nauki i predykcji

---

## CZESC 4.PY - ANALIZA TRENDOW + PAMIEC OBSERWACJI (Czesc 2/2)

### Wejscia:
| Plik | Sciezka | Zrodlo | Uzycie | Format |
|------|---------|--------|--------|--------|
| Baza predykcji | `dane/dataBase_futbol_trend.csv` | czesc1 SEKCJA C | X_PREDYKCJA, NAZWY_PREDYKCJI | CSV |
| Historia | `dane/kod_dataBase_futbol_trend.csv` | czesc1 SEKCJA D | X_HISTORIA, Y_HISTORIA, NAZWY_HISTORIA | CSV |
| Model | `modele_dataBase_futbol_trend/siec_08_log_koniec/model.h5` | czesc1 SEKCJA G | model.predict() | H5 |
| Metadane | `modele_dataBase_futbol_trend/siec_08_log_koniec/metadata.json` | czesc1 SEKCJA G | CECHY, NAZWA_MODELU | JSON |
| Klasy | `modele_dataBase_futbol_trend/siec_08_log_koniec/klasy.json` | czesc1 SEKCJA G | klasy, ID_NA_WYNIK | JSON |
| Pamiec | `modele_dataBase_futbol_trend/siec_08_log_koniec/obserwacja/pamiec_obserwacji.json` | czesc2 (lub poprzednie czesc4) | pamiec_obserwacji | JSON |
| Ocena | `modele_dataBase_futbol_trend/siec_08_log_koniec/obserwacja/ocena.json` | czesc2 (lub poprzednie czesc4) | ocena | JSON |

### Wyjscia:
| Plik | Sciezka | Format | Opis |
|------|---------|--------|------|
| Pamiec obserwacji | `modele_dataBase_futbol_trend/siec_08_log_koniec/obserwacja/pamiec_obserwacji.json` | JSON | Zaktualizowana pamiec z nowymi obserwacjami historii |
| Ocena | `modele_dataBase_futbol_trend/siec_08_log_koniec/obserwacja/ocena.json` | JSON | Zaktualizowana ocena modelu ze statystykami |
| Predykcje aktualne | `modele_dataBase_futbol_trend/siec_08_log_koniec/predykcje/predykcja_grupy.csv` | CSV | Aktualne predykcje meczow |
| Historia predykcji | `modele_dataBase_futbol_trend/siec_08_log_koniec/predykcje/predykcja_grupy_historia.csv` | CSV | Historia predykcji z obserwacjami |

### Proces:
1. **Wczytanie modelu** z czesc1 SEKCJA G
2. **Predykcja historii** (model.predict na X_HISTORIA) - analiza meczow z wynikami
3. **Predykcja aktualna** (model.predict na X_PREDYKCJA) - predykcja meczow bez wynikow
4. **Aktualizacja pamięci obserwacji** - dodawanie nowych obserwacji dla historii
5. **Detekcja zmian** - sprawdzanie zmian predykcji i pewnosci miedzy kolejnymi uruchomieniami
6. **Statystyka klas** - liczenie wystapien, trafien, bledow po klasach
7. **Aktualizacja oceny** - obliczanie skutecznosci globalnej i po klasach
8. **Zapis** wszystkich struktur

### Zaleznosci:
- **zalezy od:** czesc1.py (dane wejsciowe i model)
- **zalezy od:** czesc2.py (pamiec i ocena z poprzedniego uruchomienia - OPCJONALNIE)
- **uzywana przez:** System monitoringu i raportowania

---

## PODSUMOWANIE PRZEPLYWU GLOWNEGO

```
[ZEWNETRZNE API]
     |
     v
[CZESC1: PRZYGOTOWANIE]
     |
     +---> dane/dataBase_futbol_trend.csv --+---> [CZESC2: PREDYKCJA 1/2]
     |                                            |
     +---> dane/kod_dataBase_futbol_trend.csv --+---> [CZESC4: ANALIZA 2/2]
     |                                            |
     +---> model.h5, metadata.json, klasy.json ----+
     |
     v
[CZESC3A: BUDOWA SIECI KURSOW] (niezwiazana z glownym przeplywem)
     |
     v
   modele_kursy_przygotowane/

[CZESC3B: SYSTEM WORLD + COGNITIVE TEACHER] (uzywa czesc1 wyjsc)
     |
     +---> dane/dataBase_futbol_trend.csv (z czesc1)
     |
     +---> WORLD/*.json (system WORLD)
     |
     v
   modele_dataBase_futbol_trend/ (CognitiveTeacher)

[CZESC2 -> CZESC4: PRZEPLYW PAMIECI]
     |
     +---> pamiec_obserwacji.json (zaktualizowana przez czesc2)
     |                                             (uzywana przez czesc4 w nastepnym uruchomieniu)
     v
   [REGULARNE URUCHOMIENIA: czesc2 -> czesc4 -> czesc2 -> czesc4 ...]
```

---

## KONFLIKTY I UWAGI

### 1. Duplikacja Plikow CSV
- **czesc1 SEKCJA C:** generuje `dane/dataBase_futbol_trend.csv`
- **czesc1 SEKCJA D:** generuje `dane/kod_dataBase_futbol_trend.csv`
- **czesc3A:** uzywa `dane/kursy_przygotowane.csv` i `dane/mozg_kursy_przygotowane.csv`
- **czesc3B:** uzywa `dane/dataBase_futbol_trend.csv` i `dane/kod_dataBase_futbol_trend.csv` (z czesc1)

**Decyzja:** Zachowac obie sciezki, rozroznic uzycie w zaleznosci od kontekstu.

### 2. Duplikacja Modeli
- **czesc1 SEKCJA G:** generuje `modele_dataBase_futbol_trend/siec_08_log_koniec/model.h5`
- **czesc3A:** generuje `modele_kursy_przygotowane/{nazwa}/model.h5`
- **czesc3B:** generuje `modele_dataBase_futbol_trend/{siec_name}/model.h5`

** Decyzja:** Rozne katalogi, rozne cele. Zachowac.

### 3. Pamiec Obserwacji - Czym sie rozni czesc2 od czesc4?
- **czesc2:** PREDYKCJA I PAMIEC OBSERWACJI (Czesc 1/2)
- **czesc4:** GENERATOR ANALIZY TRENDOW + PAMIEC OBSERWACJI (Czesc 2/2)

**Analiza:**
- czesc2: predykcja modelu i zapis pamięci
- czesc4: analiza historii z wynikami + aktualne predykcje + aktualizacja tej samej pamięci
- **Wniosek:** czesc2 i czesc4 to **dwie części jednego procesu** (stąd nazwy "CzęŚĆ 1/2" i "CzęŚĆ 2/2")

### 4. Zaleznosc pomiedzy czesc2 a czesc4
- czesc2 zaladowuje model z czesc1 i robi predykcje
- czesc4 zaladowuje TEN SAM model i robi ANALIZE HISTORII + AKTUALNE PREDYKCJIE
- Obie uzywaja tej samej pamięci obserwacji i oceny

**Przeplyw:** czesc1 -> (czesc2 -> czesc4) <- powtarzany cykl

---

## STRUKTURA PRZEPLYWU DANYCH

### Formaty Plikow:

**CSV:**
- `dane/*.csv` - rozmowionymi; separator ";" encoding="utf-8"
- `modele_*/*.csv` - wyjsciowe separatory ";" encoding="utf-8"

**JSON:**
- `WORLD/*.json` - UTF-8, hierarchiczna struktura
- `modele_*/*.json` - UTF-8, indent=4, ensure_ascii=False
- `modele_*/pamiec_obserwacji.json` - szczegolna struktura:
  ```json
  {
    "id_meczu": [
      {
        "data": "YYYY-MM-DD HH:MM:SS",
        "model": "siec_08_log_koniec",
        "id_grupy": 0,
        "predykcja": "1:0",
        "wynik_rzeczywisty": "1:0",
        "pewnosc": 0.95,
        "trafienie": true,
        "pierwsza_obserwacja": false,
        "zmiana_predykcji": {"stara": "0:1", "nowa": "1:0"},
        "zmiana_pewnosci": {"stara": 0.8, "nowa": 0.95}
      }
    ]
  }
  ```
- `modele_*/ocena.json` - struktura:
  ```json
  {
    "model": "siec_08_log_koniec",
    "data": "YYYY-MM-DD HH:MM:SS",
    "ocena_ogolna": {
      "ilosc_meczow": 100,
      "trafienia": 85,
      "skutecznosc": 0.85
    },
    "ocena_wynikow": {
      "1:0": {"ilosc_predykcji": 20, "trafienia": 18, "skutecznosc": 0.9, "bledy": {"0:1": 2}}
    }
  }
  ```

### Slownik nazewnictwa:
- `dataBase_futbol_trend` - glowny model trendow
- `siec_08_log_koniec` - konkretna siec w modelu dataBase_futbol_trend
- `kursy_przygotowane` - Dane kursow przygotowane do nauki
- `mozg_kursy_przygotowane` - Historia kursow z wynikami (mozg = nauka)

---

## PODSUMOWANIE

### Glowny Przeplyw Produkcyjny:
```
[START] -> czesc1 (przygotowanie danych) -> [czesc2 (predykcja) -> czesc4 (analiza)] -> [REPEAT]
                                                   ^--------------------------'
```

### Alternatywne Srodowisko:
```
czesc3A (budowa sieci kursow) -> modele_kursy_przygotowane/
czesc3B (system WORLD) -> modele_dataBase_futbol_trend/ (CognitiveTeacher)
```

### Zaleznosci MiedzyPlikowe:
- **czesc2 -> czesc1:** Zalezy od plikow CSV i modelu z czesc1
- **czesc4 -> czesc1:** Zalezy od plikow CSV i modelu z czesc1
- **czesc4 -> czesc2:** Uzywa Pamieci i Oceny z czesc2 (opcjonalnie)
- **czesc3A:** Niezalezna (uzywa wlasnych plikow wejsciowych)
- **czesc3B -> czesc1:** Zalezy od plikow CSV z czesc1
