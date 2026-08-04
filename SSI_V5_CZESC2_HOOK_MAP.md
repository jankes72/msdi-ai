# SSI V5 - CZĘŚĆ 2 - MAPA HOOKÓW INTEGRACYJNYCH

## INFORMACJE PODSTAWOWE

- **Plik:** `czesc2.py`
- **Część generatora:** Analiza Predykcji + Pamięć Obserwacji (Ainsi Analysis Engine)
- **Ilość linii:** 19,718
- **Data mapowania:** 2026-08-03
- **Status:** Tylko analiza - brak modyfikacji, brak hooków
- **Zależność:** **Korzysta z modeli wygenerowanych w czesc1.py**

---

## PODSUMOWANIE RÓŻNIC: CZĘŚĆ 1 vs CZĘŚĆ 2

| Aspekt | Część 1 (czesc1.py) | Część 2 (czesc2.py) |
|--------|-------------------|-------------------|
| **Rola** | Trenowanie modeli | Używanie modeli do predykcji |
| **Główny cel** | Generowanie modeli sieci neuronowych | Generowanie analiz i predykcji |
| **Import modeli** | `from tensorflow.keras.models import Sequential` | `from tensorflow.keras.models import load_model` |
| **Epartnerzy** | `model.fit()` | `model.predict()` |
| **Struktury SSI** | ✅ Tak (SSI_STAGE_STATUS, SSI_AGENT_*) | ❌ Nie (brak importu) |
| **Liczba bloków** | 2 bloki trenowania | 10 bloków przetwarzania |

---

## STRUKTURA PLIKU CZĘŚĆ 2

### 🔍 **OGÓLNA ARCHITEKTURA**

```
czesc2.py
├── BLOK 1: siec_08_log_koniec (dataBase_futbol_trend)
│   ├── Wczytanie modelu (model.h5)
│   ├── Wczytanie metadanych (metadata.json, klasy.json)
│   ├── Predykcja historii
│   ├── Predykcja aktualnych meczów
│   └── Zapis do katalogów obserwacji i predykcji
│
├── BLOK 2: siec_08_log_koniec (duplikat lub rozszerzenie)
│   └── ... (podobna struktura)
│
├── BLOK 3: siec_09_ratio_start
├── BLOK 4: siec_09_ratio_start (duplikat/rozszerzenie)
├── BLOK 5: siec_10_ratio_koniec
├── BLOK 6: siec_10_ratio_koniec (duplikat/rozszerzenie)
├── BLOK 7: siec_11_statystyka
├── BLOK 8: siec_11_statystyka (duplikat/rozszerzenie)
├── BLOK 9: siec_01_start_kursow (kursy_przygotowane)
└── BLOK 10: ... (kursy_przygotowane)
```

### 📊 **10 BLOKÓW PRZETWARZANIA**

| Nr | Linie | Model | typ bazy | Cel |
|----|-------|-------|----------|-----|
| 1 | 27-996 | siec_08_log_koniec | dataBase_futbol_trend | Analiza historii + predykcje |
| 2 | 1025-2278 | siec_08_log_koniec | dataBase_futbol_trend | Rozszerzona analiza (3 kursy) |
| 3 | 2293-4549 | siec_09_ratio_start | dataBase_futbol_trend | Analiza trendów ratio |
| 4 | 4560-5719 | siec_09_ratio_start | dataBase_futbol_trend | Rozszerzona analiza ratio |
| 5 | 5734-7107 | siec_10_ratio_koniec | dataBase_futbol_trend | Analiza końcowych ratio |
| 6 | 7123-8000 | siec_10_ratio_koniec | dataBase_futbol_trend | Rozszerzona analiza |
| 7 | 8005-9270 | siec_11_statystyka | dataBase_futbol_trend | Analiza statystyczna |
| 8 | 9289-10440 | siec_11_statystyka | dataBase_futbol_trend | Rozszerzona analiza statystyczna |
| 9 | 10900-11820 | siec_01_start_kursow | kursy_przygotowane | Analiza startowych kursów |
| 10 | 11830-19718 | ... | kursy_przygotowane | Finalna baza danych i rankingi |

---

## ANALIZA STRUKTURY POJEDYNCZEGO BLOKU

### **Przykład: BLOK 1 (linie 27-996)**

```python
# =====================================================
# KONFIGURACJA
# =====================================================
KATALOG_MODELU = r"modele_dataBase_futbol_trend\siec_08_log_koniec"
PLIK_PREDYKCJI = r"dane\dataBase_futbol_trend.csv"
PLIK_HISTORIA = r"dane\kod_dataBase_futbol_trend.csv"

KATALOG_OBSERWACJI = os.path.join(KATALOG_MODELU, "obserwacja")
KATALOG_PREDYKCJI = os.path.join(KATALOG_MODELU, "predykcje")
PLIK_PAMIEC = os.path.join(KATALOG_OBSERWACJI, "pamiec_obserwacji.json")
PLIK_OCENA = os.path.join(KATALOG_OBSERWACJI, "ocena.json")

# =====================================================
# WCZYTANIE METADANYCH MODELU
# =====================================================
with open(os.path.join(KATALOG_MODELU, "metadata.json"), encoding="utf-8") as f:
    metadata = json.load(f)

CECHY = metadata["cechy"]
NAZWA_MODELU = metadata["nazwa"]

# =====================================================
# WCZYTANIE KLAS
# =====================================================
with open(os.path.join(KATALOG_MODELU, "klasy.json"), encoding="utf-8") as f:
    klasy = json.load(f)

ID_NA_WYNIK = {int(v): k for k,v in klasy.items()}

# =====================================================
# WCZYTANIE AKTUALNEJ PREDYKCJI
# =====================================================
df_pred = pd.read_csv(PLIK_PREDYKCJI, sep=";", encoding="utf-8")
NAGLOWKI = list(df_pred.columns)
INDEX_CECH = [i for i, col in enumerate(NAGLOWKI) if col in CECHY]

# =====================================================
# WCZYTANIE HISTORII Z WYNIKAMI
# =====================================================
hist = pd.read_csv(PLIK_HISTORIA, sep=";", header=None, encoding="utf-8")
NAZWY_HISTORIA = hist.iloc[:,0].astype(str)
X_HISTORIA = hist.iloc[:, INDEX_CECH]
Y_HISTORIA = hist.iloc[:,-1]

# =====================================================
# WCZYTANIE MODELU
# =====================================================
model = load_model(os.path.join(KATALOG_MODELU, "model.h5"))

# =====================================================
# PREDYKCJA HISTORII
# =====================================================
pred_hist = model.predict(X_HISTORIA)
klasy_pred_hist = np.argmax(pred_hist, axis=1)

# Konwersja na wyniki tekstowe
WYNIKI = list(klasy.keys())
wyniki_pred_hist = [WYNIKI[x] for x in klasy_pred_hist]

# =====================================================
# PREDYKCJA AKTUALNYCH MECZÓW
# =====================================================
X_PREDYKCJA = df_pred.iloc[:, INDEX_CECH].values
pred_current = model.predict(X_PREDYKCJA)
klasy_pred_current = np.argmax(pred_current, axis=1)
wyniki_pred_current = [WYNIKI[x] for x in klasy_pred_current]

# =====================================================
# ZAPIS PAMIĘCI OBSERWACJI
# =====================================================
# Generowanie danych do zapisu
pamiec_data = {
    "model": NAZWA_MODELU,
    "cechy": CECHY,
    "historia": {
        "mecze": NAZWY_HISTORIA.tolist(),
        "predykcje": wynik_pred_hist,
        "rzeczywiste": [WYNIKI.get(y, "") for y in Y_HISTORIA]
    },
    "aktualne": {
        "mecze": df_pred["mecz"].tolist(),
        "predykcje": wynik_pred_current
    }
}

with open(PLIK_PAMIEC, "w", encoding="utf-8") as f:
    json.dump(pamiec_data, f, indent=4, ensure_ascii=False)

# =====================================================
# OCENA DOKŁADNOŚCI
# =====================================================
# (Porównanie predykcji z rzeczywistymi wynikami)
ocean_data = {
    "model": NAZWA_MODELU,
    "dokladnosc_historia": ...
}

with open(PLIK_OCENA, "w", encoding="utf-8") as f:
    json.dump(ocena_data, f, indent=4, ensure_ascii=False)

# =====================================================
# ZAPIS PREDYKCJI CSV
# =====================================================
df_results = pd.DataFrame({
    "mecz": df_pred["mecz"],
    "predykcja": wynik_pred_current,
    "prawdopodobienstwo": np.max(pred_current, axis=1)
})

df_results.to_csv(
    os.path.join(KATALOG_PREDYKCJI, "predykcje_{nazwa_modelu}.csv"),
    sep=";",
    index=False,
    encoding="utf-8"
)
```

---

## ZALEŻNOŚCI MIĘDZY CZĘŚCIAMI

### 🔗 **CZĘŚĆ 1 → CZĘŚĆ 2**

#### **Przekazywane dane:**

| Typ | Źródło (czesc1.py) | Cel (czesc2.py) | Format |
|-----|-------------------|----------------|--------|
| Modele sieci | `model.save()` w `buduj_siec()` | `load_model()` w każdym bloku | `.h5` (Keras) |
| Metadane modelu | `metadata.json` | Wczytanie za pomocą `json.load()` | JSON |
| Mapa klas | `klasy.json` | Wczytanie za pomocą `json.load()` | JSON |
| Historia treningu | `historia.json` | *Nie używane w czesc2* | JSON |

#### **Lokalizacje modeli:**

**Z czesc1.py - Blok 1 (dataBase_futbol_trend):**
- `modele_dataBase_futbol_trend/siec_01_zmiana_kursow/model.h5`
- `modele_dataBase_futbol_trend/siec_02_amplituda/model.h5`
- `modele_dataBase_futbol_trend/siec_03_tempo/model.h5`
- `modele_dataBase_futbol_trend/siec_04_max_wahanie/model.h5`
- `modele_dataBase_futbol_trend/siec_05_start_raw/model.h5`
- `modele_dataBase_futbol_trend/siec_06_koniec_raw/model.h5`
- `modele_dataBase_futbol_trend/siec_07_log_start/model.h5`
- `modele_dataBase_futbol_trend/siec_08_log_koniec/model.h5` ← **Używane w czesc2**
- `modele_dataBase_futbol_trend/siec_09_ratio_start/model.h5` ← **Używane w czesc2**
- `modele_dataBase_futbol_trend/siec_10_ratio_koniec/model.h5` ← **Używane w czesc2**
- `modele_dataBase_futbol_trend/siec_11_statystyka/model.h5` ← **Używane w czesc2**

**Z czesc1.py - Blok 2 (kursy_przygotowane):**
- `modele_kursy_przygotowane/siec_01_start_kursow/model.h5` ← **Używane w czesc2**
- `modele_kursy_przygotowane/siec_02_koniec_kursow/model.h5`
- `modele_kursy_przygotowane/siec_03_zmiana_kursow/model.h5`
- `modele_kursy_przygotowane/siec_04_procent_kursow/model.h5`

#### **Zależność:**
- **czesc2.py NIE MOŻE dzialać BEZ czesc1.py**
- czesc2.py **WYMAGA** istnienia katalogów i plików wygenerowanych przez czesc1.py
- **Sekwencja wykonania:** czesc1.py → czesc2.py → czesc3.py → czesc4.py

### 🔄 **CZĘŚĆ 2 → CZĘŚĆ 3/4**

#### **Generowane dane (wyjścia czesc2.py):**

| Typ | Lokalizacja | Format | Użycie w kolejnych częściach |
|-----|-------------|--------|------------------------------|
| Pamięć obserwacji | `{KATALOG_MODELU}/obserwacja/pamiec_obserwacji.json` | JSON | ⚠️ Prawdopodobnie używane |
| Ocena modelu | `{KATALOG_MODELU}/obserwacja/ocena.json` | JSON | ⚠️ Prawdopodobnie używane |
| Predykcje CSV | `{KATALOG_MODELU}/predykcje/predykcje_{model}.csv` | CSV | ⚠️ Prawdopodobnie używane |
| World Match Database | *Końcowy plik* | JSON | ✅ **Główne wyjście** |

---

## PUNKTY STEROWANIA I KONTROLI

### 🎯 **ISTNIEJĄCE PUNKTY START**

| Nr | Lokalizacja | Typ | Co uruchamia |
|----|-------------|-----|-------------|
| 1 | Linie 64-67 | Inicjalizacja | `os.makedirs(KATALOG_OBSERWACJI)` |
| 2 | Linie 71-74 | Inicjalizacja | `os.makedirs(KATALOG_PREDYKCJI)` |
| 3 | Linie 85-96 | Wczytanie | `metadata = json.load(f)` |
| 4 | Linie 114-125 | Wczytanie | `klasy = json.load(f)` |
| 5 | Linie 146-149 | Wczytanie | `df_pred = pd.read_csv(PLIK_PREDYKCJI)` |
| 6 | Linie 9349-9358 | Wczytanie | `hist = pd.read_csv(PLIK_HISTORIA)` |
| 7 | **Linie 310-320** | **Ładowanie modelu** | `model = load_model(...)` |
| 8 | Linie 337-341 | Predykcja | `pred_hist = model.predict(X_HISTORIA)` |
| 9 | Linie 9369-9373 | Predykcja | `pred_current = model.predict(X_PREDYKCJA)` |

### 🛑 **ISTNIEJĄCE PUNKTY STOP/KONIEC**

| Nr | Lokalizacja | Typ | Co kończy |
|----|-------------|-----|-----------|
| 1 | Linie 938-974 | Zapis | `json.dump(pamiec_data, PLIK_PAMIEC)` |
| 2 | Linie 970-990 | Zapis | `json.dump(ocena_data, PLIK_OCENA)` |
| 3 | Linie 997-1000 | Zapis | `df_results.to_csv(...)` |
| 4 | Linie 2047 | Zapis | `df_analiza_predykcji.to_csv(...)` |
| 5 | Linie 19664 | Zapis | `json.dump(WORLD_MATCH_DATABASE, ...)` |

---

## FUNKCJE W PLIKU

### 📋 **Lista głównych funkcji** (44 funkcje)

| Nr | Linia | Funkcja | Rola | Wykorzystanie |
|----|-------|---------|------|---------------|
| 1 | 10846 | `normalize(value, min_val, max_val)` | Normalizacja | Pomocnicza |
| 2 | 10861 | `bezpieczny_log(value)` | Logarytm | Pomocnicza |
| 3 | 10869 | `oblicz_cechy_3kursy_rozszerzone(bloki)` | Obliczanie cech | Analiza kursów |
| 4 | 11089 | `przetworz_plik_3kursy_rozszerzone(...)` | Przetwarzanie | Analiza kursów |
| 5 | 11931 | `classify_odds(odds)` | Klasyfikacja | Analiza wyników |
| 6 | 12040 | `process_and_save_data(...)` | Przetwarzanie | Zapis danych |
| 7 | 12218 | `classify_odds(odds)` | Klasyfikacja | Duplikat funkcji |
| 8 | 12327 | `process_and_save_data(...)` | Przetwarzanie | Duplikat funkcji |
| 9 | 12671 | `liczba(x)` | Typ wynik | Pomocnicza |
| 10 | 12681 | `odleglosc(a,b)` | Metryka | Pomocnicza |
| 11 | 12694 | `wynik_liczbowy(wynik)` | Konwersja | Pomocnicza |
| 12 | 13181 | `rozbij_wynik(x)` | Parsing | Pomocnicza |
| 13 | 13196 | `wynik_1x2(x)` | Konwersja | Pomocnicza |
| 14 | 13217 | `wynik_gole(x)` | Konwersja | Pomocnicza |
| 15 | 13264 | `poisson(k, lam)` | Statystyka | Model Poisson |
| 16 | 13300 | `dixon_coles(...)` | Statystyka | Model Dixon-Coles |
| 17 | 13447 | `policz_dc(row)` | Obliczenia | Pomocnicza |
| 18 | 14261 | `rozbij_wynik(x)` | Parsing | **Duplikat (linia 13181)** |
| 19 | 14300 | `pobierz_druzyny(x)` | Parsing | Pomocnicza |
| 20 | 14495 | `poisson(k, lam)` | Statystyka | **Duplikat (linia 13264)** |
| 21 | 14523 | `dixon_coles(...)` | Statystyka | **Duplikat (linia 13300)** |
| 22 | 14568 | `macierz_wynikow(ld,lw)` | Matematyka | Pomocnicza |
| 23 | 14831 | `popraw_wynik(wynik)` | Walidacja | Pomocnicza |
| 24 | 14857 | `load_csv(...)` | Wczytywanie | Pomocnicza |
| 25 | 14912 | `create_tag_map(data)` | Mapowanie | Pomocnicza |
| 26 | 15049 | `klasyfikuj_wynik(wynik)` | Klasyfikacja | Pomocnicza |
| 27 | 15274 | `normalizuj(x)` | Normalizacja | **Duplikat (linia 10846)** |
| 28 | 15473 | `klasyfikuj_wynik(wynik)` | Klasyfikacja | **Duplikat (linia 15049)** |
| 29 | 15693 | `normalizuj(x)` | Normalizacja | **Duplikat (linia 15274)** |
| 30 | 16813 | `klasyfikuj_wynik(wynik)` | Klasyfikacja | **Duplikat (linia 15473)** |
| 31 | 16860 | `normalizuj(x)` | Normalizacja | **Duplikat (linia 15693)** |
| 32 | 16885 | `policz_korelacje(cecha, y)` | Analiza | Pomocnicza |
| 33 | 16923 | `analizuj_plik(nazwa_pliku)` | Analiza | Pomocnicza |
| 34 | 17345 | `klasyfikuj_wynik(wynik)` | Klasyfikacja | **Duplikat (linia 16813)** |
| 35 | 17480 | `normalizuj(x)` | Normalizacja | **Duplikat (linia 16860)** |
| 36 | 17505 | `policz_korelacje(cecha, y)` | Analiza | **Duplikat (linia 16885)** |
| 37 | 17543 | `analizuj_plik(nazwa_pliku)` | Analiza | **Duplikat (linia 16923)** |
| 38 | 18337 | `typ_wyniku(wynik)` | Klasyfikacja | Pomocnicza |
| 39 | 18390 | `kategoria_wyniku(wynik)` | Klasyfikacja | Pomocnicza |
| 40 | 18456 | `analiza_grupy(wyniki)` | Analiza | Pomocnicza |
| 41 | 18771 | `pobierz_poziomy(grupa)` | Analiza | Pomocnicza |
| 42 | 18947 | `analizuj_warstwe(dane)` | Analiza | Pomocnicza |
| 43 | 19256 | `load_json(path)` | Wczytywanie | Pomocnicza |
| 44 | 19335 | `zbuduj_poziomy(grupa)` | Budowa | Pomocnicza |

### ⚠️ **WAŻNA OBSERWACJA:**
- **Dużo powtarzających się funkcji** (duplikaty)
- Brak struktur **SSI V5** (SSI_STAGE_STATUS, SSI_AGENT_*)
- Brak importu czesc1.py (ale importuje modele z plików)

---

## ISTNIEJĄCE STRUKTURY SSI

### ❌ **Brak struktury SSI V5**

```python
# W czesc2.py NIE MA:
# - SSI_STAGE_STATUS
# - SSI_AGENT_INPUT  
# - SSI_AGENT_OUTPUT
# - SSI_EVENTS
# - Funkcji update_stage_status()
# - Funkcji register_agent_input()
# - Funkcji export_agent_output()
```

**To jest problem dla integracji SSI V5!**

---

## PUNKTY INTEGRACJI DLA SSI V5

### 🎯 **PROPOZYCJA MIEJSC NA HOOKI**

#### **1. START PROCESU (całego czesc2.py)**
- **Lokalizacja:** Początek pliku (linia 1)
- **Propozycja:** `SSI_MAIN_PROCESS_START("czesc2")`
- **Cel:** Zgłoszenie rozpoczęcia części 2

#### **2. START BLOKU PRZETWARZANIA**
- **Lokalizacja:** Początek każdego bloku (linie: 27, 1025, 2293, 4560, 9100, itp.)
- **Propozycja:** `SSI_BLOCK_START(block_name, model_name)`
- **Parametry:**
  - `block_name`: "Block_1", "Block_2", itp.
  - `model_name`: "siec_08_log_koniec", itp.
- **Częstotliwość:** 1x na blok (10 razy w pliku)

#### **3. ŁADOWANIE MODELU**
- **Lokalizacja:** Przed `model = load_model(...)` (linie: 310, 2581, 4852, 7123, 9396)
- **Propozycja:** `SSI_MODEL_LOAD_START(model_path)`
- **Cel:** Agent wie, który model jest ładowany
- **Parametry:** `model_path` - ścieżka do modelu

#### **4. PO ŁADOWANIU MODELU**
- **Lokalizacja:** Po `model = load_model(...)`
- **Propozycja:** `SSI_MODEL_LOAD_COMPLETE(model_name, model_info)`
- **Cel:** Potwierdzenie załadowania modelu

#### **5. START PREDYKCJI**
- **Lokalizacja:** Przed `model.predict(...)` (linie: 337, 9369, itp.)
- **Propozycja:** `SSI_PREDICTION_START(model_name, data_type, data_shape)`
- **Parametry:**
  - `model_name`: nazwa modelu
  - `data_type`: "historia" lub "aktualne"
  - `data_shape`: rozmiar danych wejściowych

#### **6. KONIEC PREDYKCJI**
- **Lokalizacja:** Po `model.predict(...)` i przetworzeniu wyników
- **Propozycja:** `SSI_PREDICTION_COMPLETE(model_name, predictions_count, results)`
- **Cel:** Agent wie, jakie predykcje zostały wygenerowane

#### **7. ZAPIS PAMIĘCI OBSERWACJI**
- **Lokalizacja:** Przed `json.dump(pamiec_data, PLIK_PAMIEC)` (linie: 938, 3209, itp.)
- **Propozycja:** `SSI_SAVE_OBSERVATION_START(model_name, file_path)`
- **Cel:** Zgłoszenie zapisu pamięci

#### **8. ZAPIS PREDYKCJI**
- **Lokalizacja:** Przed `df_results.to_csv(...)` (linie: 997, 3268, itp.)
- **Propozycja:** `SSI_SAVE_PREDICTION_START(model_name, file_path, records_count)`

#### **9. KONIEC BLOKU PRZETWARZANIA**
- **Lokalizacja:** Koniec każdego bloku
- **Propozycja:** `SSI_BLOCK_COMPLETE(block_name, model_name, results_summary)`

#### **10. ZAPIS WORLD MATCH DATABASE**
- **Lokalizacja:** Przed `json.dump(WORLD_MATCH_DATABASE, ...)` (linia 19664)
- **Propozycja:** `SSI_SAVE_WORLD_DATABASE_START(file_path, records_count)`
- **Cel:** Zgłoszenie zapisu głównej bazy danych

#### **11. KONIEC PROCESU (całego czesc2.py)**
- **Lokalizacja:** Koniec pliku (linia 19718)
- **Propozycja:** `SSI_MAIN_PROCESS_COMPLETE("czesc2")`

---

## WEJŚCIA DLA AGENTÓW

### 📥 **Dane dostępne z czesc1.py (weumann)**

| Typ | Źródło | Format | Jak pobrać |
|-----|--------|--------|-------------|
| **Modele** | `modele_dataBase_futbol_trend/*/model.h5` | Keras `.h5` | `load_model()` |
| **Metadane** | `modele_dataBase_futbol_trend/*/metadata.json` | JSON | `json.load()` |
| **Mapa klas** | `modele_dataBase_futbol_trend/*/klasy.json` | JSON | `json.load()` |
| **Walidacja 40%** | `modele_*/walidacja_40_procent.csv` | CSV | `pd.read_csv()` |

### 📥 **Potencjalne wejścia od agentów**

| Typ | Propozycja struktury | Opis |
|-----|---|---|
| Model selection | `SSI_AGENT_INPUT["model_to_use"]` | Który model użyć (zamiast domyślnego) |
| Additional data | `SSI_AGENT_INPUT["additional_data"]` | Dodatkowe dane do analizy |
| Analysis params | `SSI_AGENT_INPUT["analysis_params"]` | Parametry analizy |
| Filter criteria | `SSI_AGENT_INPUT["filter_criteria"]` | Kryteria filtrowania meczów |

---

## WYJŚCIA DLA AGENTÓW

### 📤 **Generowane pliki (wyjścia)**

| Typ | Lokalizacja | Format | Zawartość |
|-----|-------------|--------|-----------|
| **Pamięć obserwacji** | `{KATALOG_MODELU}/obserwacja/pamiec_obserwacji.json` | JSON | Predykcje historii + aktualne |
| **Ocena modelu** | `{KATALOG_MODELU}/obserwacja/ocena.json` | JSON | Dokładność, błędy |
| **Predykcje CSV** | `{KATALOG_MODELU}/predykcje/predykcje_{model}.csv` | CSV | Predykcje dla aktualnych meczów |
| **World Match Database** | *Końcowy plik JSON* | JSON | **Główna baza danych meczów** |

### 📤 **Potencjalne wyjścia dla agentów**

| Typ | Propozycja struktury | Opis |
|-----|---|---|
| Predictions | `SSI_AGENT_OUTPUT["predictions"]` | Raport predykcji |
| Accuracy metrics | `SSI_AGENT_OUTPUT["metrics"]` | Metryki dokładności |
| Analysis results | `SSI_AGENT_OUTPUT["analyses"]` | Wyniki analiz |
| World database | `SSI_AGENT_OUTPUT["world_database"]` | Главная база данных |

---

## ZALEŻNOŚCI I PRZEPŁYW DANYCH

```
CZĘŚĆ 1 (czesc1.py)
│
├── Generuje modele:
│   ├── modele_dataBase_futbol_trend/siec_08_log_koniec/
│   ├── modele_dataBase_futbol_trend/siec_09_ratio_start/
│   ├── modele_dataBase_futbol_trend/siec_10_ratio_koniec/
│   ├── modele_dataBase_futbol_trend/siec_11_statystyka/
│   └── modele_kursy_przygotowane/siec_01_start_kursow/
│
└── Pliki wejściowe:
    ├── metadata.json
    ├── klasy.json
    └── model.h5

CZĘŚĆ 2 (czesc2.py)
│
├── Ładuje modele z CZĘŚCI 1:
│   ├── siec_08_log_koniec (Bloki 1-2)
│   ├── siec_09_ratio_start (Bloki 3-4)
│   ├── siec_10_ratio_koniec (Bloki 5-6)
│   ├── siec_11_statystyka (Bloki 7-8)
│   └── siec_01_start_kursow (Blok 9)
│
├── Przetwarza:
│   ├── Predykcje historii
│   ├── Predykcje aktualnych meczów
│   ├── Analiza statystyczna
│   └── Rankingi i korelacje
│
└── Generuje:
    ├── pamięć_obserwacji.json
    ├── ocena.json
    ├── predykcje_*.csv
    └── WORLD_MATCH_DATABASE.json

CZĘŚĆ 3 (czesc3.py) → *[Do analizy]*
└── Prawdopodobnie używa:
    ├── WORLD_MATCH_DATABASE.json
    └── predykcje_*.csv

CZĘŚĆ 4 (czesc4.py) → *[Do analizy]*
└── Prawdopodobnie finalizacja i raporty
```

---

## PROBLEMY I WYZWANIA DLA SSI V5

### ❌ **Główne problemy:**

1. **Brak struktur SSI** - czesc2.py nie korzysta z istniejącej infrastruktury SSI
2. **Powtarzający się kod** - dużo duplikatów funkcji i bloków
3. **Brak modularności** - trudny do utrzymania i rozbudowy
4. **Zależność od czesc1.py** - nie może działać samodzielnie

### ✅ **Szanse:**

1. **Jasny przepływ danych** - czesc1 → czesc2 → czesc3 → czesc4
2. **Dobra struktura blokowa** - każdy blok jest samodzielną jednostką
3. **Czytelne punkty wejścia/wyjścia** - łatwo zidentyfikować co jest ładowane i zapisywane
4. **Możliwość dodania hooków** - bez zmian logiki głównej

---

## REKOMENDACJE DLA INTEGRACJI SSI V5

### **1. Dodać struktury SSI na początku pliku:**

```python
# Na początku czesc2.py (po importach)

# SSI V5 - Import struktury z czesc1
# (Jeśli czesc1 jest importowana lub struktury są współdzielone)

SSI_STAGE_STATUS = {
    "engine": "generatorDataBaseTrendAnalisAll",
    "part": "czesc2",
    "stage": "",
    "status": "",
    "timestamp": "",
    "processing_stats": {},
    "errors": []
}

# Jeśli nie ma dostępu do SSI_AGENT_* z czesc1, należy je zdefiniować
if 'SSI_AGENT_INPUT' not in globals():
    SSI_AGENT_INPUT = {
        "files_to_process": None,
        "custom_data": None,
        "analysis_params": None,
        "observations": None,
        "research_task": None
    }
    
if 'SSI_AGENT_OUTPUT' not in globals():
    SSI_AGENT_OUTPUT = {
        "results": None,
        "analyses": None,
        "memory_updates": None,
        "diagnostics": None,
        "processing_time": None
    }
```

### **2. Zdefiniować funkcje hookowe dla czesc2.py:**

```python
# Funkcje specyficzne dla czesc2.py
def SSI_BLOCK_START(block_name, model_name):
    """Hook: Rozpoczęcie bloku przetwarzania"""
    update_stage_status(f"block_{block_name}", "started")
    SSI_EVENT("BLOCK_START", network=model_name, stage=f"block_{block_name}", status="started")

def SSI_MODEL_LOAD_START(model_path):
    """Hook: Rozpoczęcie ładowania modelu"""
    update_stage_status("model_loading", "started")
    SSI_EVENT("MODEL_LOAD_START", data={"model_path": model_path})

def SSI_PREDICTION_START(model_name, data_type, data_shape):
    """Hook: Rozpoczęcie predykcji"""
    update_stage_status("prediction", "started")
    SSI_EVENT("PREDICTION_START", network=model_name, data={"data_type": data_type, "shape": data_shape})

def SSI_SAVE_REULTS_START(output_type, file_path):
    """Hook: Rozpoczęcie zapisu wyników"""
    update_stage_status("saving", "started")
    SSI_EVENT("SAVE_START", data={"output_type": output_type, "file_path": file_path})
```

### **3. Mapa hooków do dodania:**

| Blok | Miejsce | Typ hooka | Funkcja | Parametry |
|------|---------|-----------|---------|-----------|
| **Ogólne** | Linia 1 | Start procesu | `SSI_MAIN_PROCESS_START` | "czesc2" |
| **Ogólne** | Linia 19718 | Koniec procesu | `SSI_MAIN_PROCESS_COMPLETE` | "czesc2" |
| **Blok 1** | Linia 27 | Start bloku | `SSI_BLOCK_START` | "Block_1", "siec_08_log_koniec" |
| **Blok 1** | Linia 310 | Ładowanie modelu | `SSI_MODEL_LOAD_START` | model_path |
| **Blok 1** | Linia 337 | Start predykcji | `SSI_PREDICTION_START` | model, "historia", X_HISTORIA.shape |
| **Blok 1** | Linia 938 | Zapis pamięci | `SSI_SAVE_REULTS_START` | "observation_memory", PLIK_PAMIEC |
| **Blok 1** | Linia 997 | Zapis predykcji | `SSI_SAVE_REULTS_START` | "predictions", csv_path |
| **Blok 2** | Linia 1025 | Start bloku | `SSI_BLOCK_START` | "Block_2", "siec_08_log_koniec" |
| **...** | **...** | **...** | **...** | **...** |
| **Blok 10** | Linia ~11830 | Start bloku | `SSI_BLOCK_START` | "Block_10", "siec_01_start_kursow" |
| **Końcowy** | Linia 19664 | Zapis bazy | `SSI_SAVE_REULTS_START` | "world_database", OUTPUT |

---

## PODSUMOWANIE

**czesc2.py - Charakterystyka:**
- ✅ **Funkcjonalność:** Analiza predykcji za pomocą modeli z czesc1.py
- ✅ **Struktura:** 10 bloków przetwarzania, każdy z własnym modelem
- ✅ **Wejścia:** Modele, metadane, dane CSV z czesc1.py
- ✅ **Wyjścia:** Pamięć obserwacji, oceny, predykcje CSV, World Match Database
- ❌ **SSI Status:** Brak struktur SSI V5 (napshot importować z czesc1)
- ⏳ **Hooki:** Zidentyfikowano 11+ punktów integracji (oczekuje na implementację)

**Zależności:**
- **WYMAGA** czesc1.py (modele muszą być wygenerowane)
- **PRZED** czesc3.py i czesc4.py (generuje dane wejściowe)

**Następne kroki:**
1. ✅ **CZĘŚĆ 2:** Mapa hooków wykonana (ten dokument)
2. ⏳ **CZĘŚĆ 3:** Przeanalizować czesc3.py → `SSI_V5_CZESC3_HOOK_MAP.md`
3. ⏳ **CZĘŚĆ 4:** Przeanalizować czesc4.py → `SSI_V5_CZESC4_HOOK_MAP.md`
4. ⏳ **ARCHITEKTURA:** Utworzyć `SSI_V5_FULL_GENERATOR_HOOK_ARCHITECTURE.md`
5. ⏳ **IMPLEMENTACJA:** Dodać hooki do wszystkich części

---

## **SSI V5 CZĘŚĆ 2 HOOK MAP READY** ✅

*Dokument wygenerowany dla SSI V5 - CZĘŚĆ 2 - MAPA HOOKÓW*
*Data: 2026-08-03*
*Analizowany plik: czesc2.py (linie 1-19718)*
