# SSI V5 - CZĘŚĆ 3 - MAPA HOOKÓW INTEGRACYJNYCH

## INFORMACJE PODSTAWOWE

- **Plik:** `czesc3.py`
- **Część generatora:** **Laboratorium Poznawcze + Teacher Engine Core (SSI V5 RDZEŃ)**
- **Ilość linii:** 19,692
- **Data mapowania:** 2026-08-03
- **Status:** Tylko analiza - brak modyfikacji, brak hooków
- **Rola:** **HYBRYDA** - Trening nowych modeli + Integracja z Teacher Engine + Generowanie pamięci poznawczej

---

## 🎯 **ODKRRYCIE KLUCZOWE: CZĘŚĆ 3 TO RDZEŃ SSI V5!**

czesc3.py **NIE JEST** zwykłą częścią generatora. To jest **GŁÓWNY ENGINE SSI V5** zawierający:

1. **3 KLASY TEACHER ENGINE** (linie 1082-1373):
   - `WorldHierarchyManager` - Hierarchiczna pamięć światów
   - `DynamicWeightsManager` - Dynamiczne zarządzanie wagami
   - `CognitiveTeacher` - Model poznawczy generujący wiedzę

2. **GENEROWANIE KLUCZOWYCH PLIKÓW SSI:**
   - `PAMIEC_MODEL_POZNAWCZY.json` - Pamięć poznawcza modelu
   - `WIEDZA_DLA_MODELU_DOCELOWEGO.json` - Wiedza dla modelu docelowego
   - `kolektor_wiedzy.json` - Zzbiór wiedzy dla agentów
   - `analiza_*.json` - Rozszerzone analizy

3. **INTEGRACJA Z POPRZEDNIMI CZĘŚCIAMI:**
   - **Ładuje WORLD_MATCH_DATABASE.json** (z czesc2.py)
   - **Ładuje pamięć_obserwacji.json, ocena.json** (z czesc2.py)
   - **Korzysta z modeli z czesc1.py**

---

## PODSUMOWANIE RÓŻNIC: CZĘŚĆ 1 → CZĘŚĆ 2 → **CZĘŚĆ 3**

| Aspekt | Część 1 | Część 2 | **Część 3 (RDZEŃ SSI)** |
|--------|---------|---------|------------------|
| **Rola** | Trenowanie modeli | Predykcje i analizy | **Teacher Engine + Trenowanie + Integracja** |
| **Modele** | Generuje | Ładuje i używa | **Generuje + Ładuje + Integruje** |
| **Klasy** | ❌ Brak | ❌ Brak | ✅ **3 klasy Teacher Engine** |
| **Pliki SSI** | ❌ Brak | ❌ Brak | ✅ **PAMIĘĆ POZNAWCZA + WIEDZA** |
| **WORLD DB** | ❌ Brak | ✅ Generuje | ✅ **Ładuje i używa** |
| **Integracja** | Samodzielna | Zależy od C1 | **Integracja C1 + C2 + C4** |

---

## 🏗️ **STRUKTURA PLIKU CZĘŚĆ 3**

### **CZĘŚĆ A: TRENING NOWYCH MODELI** (Podobna do czesc1.py)

Plik składa się z **3 niezależnych bloków trenowania**, każdy z ownym `SPOJRZENIA` i `KATALOG_MODELE`:

#### **BLOK 1: kursy_przygotowane** (linie ~29-3000)
- **Konfig:** `PLIK_PREDYKCJI = "dane/kursy_przygotowane.csv"`
- **Trening:** `PLIK_TRENING = "dane/mozg_kursy_przygotowane.csv"`
- **Modele:** `KATALOG_MODELE = "modele_kursy_przygotowane"`
- **Funkcje:** `buduj_siec()` (linia 335), `podziel_dane()`
- **Pętla główna:** `for nazwa, cechy in SPOJRZENIA.items():` (linia 928)
- **Sieci:** Definicja w `SPOJRZENIA` (do sprawdzenia)

#### **BLOK 2: dataBase_futbol_trend** (linie ~2300-6000)
- **Konfig:** Podobna struktura do Bloku 1
- **Funkcje:** `buduj_siec()` (linia 2394)
- **Pętla główna:** `for nazwa, cechy in SPOJRZENIA.items():` (linia 2765)

#### **BLOK 3: Rozszerzone analizy** (linie ~6050-10000)
- **Konfig:** Kolejna iteracja trenowania
- **Funkcje:** `buduj_siec()` (linia 3128)
- **Pętla główna:** `for nazwa, cechy in SPOJRZENIA.items():` (linia 3721)

### **CZĘŚĆ B: TEACHER ENGINE CORE** (linie 1082-17730)

To jest **RDZEŃ SSI V5** - najważniejsza część generatora:

#### **1. WorldHierarchyManager** (linie 1082-1280)
- **Rola:** Zarządzanie hierarchiczną pamięcią światów
- **Poziomy hierarchii:**
  - **POZIOM 1:** Szeroki świat (np. "poziom30") - najszerszy
  - **POZIOM 2:** Średni świat (np. "poziom30poziom25")
  - **POZIOM 3:** Pełny świat (np. "poziom30poziom25poziom2") - najmniejszy
- **Funkcje:**
  - `_load_world_data()` - Wczytuje WORLD_MATCH_DATABASE, WORLD_LEVEL_1, WORLD_LEVEL_2
  - `select_best_level()` - Wybiera najlepszy poziom na podstawie ilości danych
  - `get_data_for_level()` - Pobiera dane dla danach poziomu
- **Zależności:** **Ładuje WORLD_MATCH_DATABASE.json z czesc2.py**

#### **2. DynamicWeightsManager** (linie 1282-1371)
- **Rola:** Dynamiczne zarządzanie wagami cech
- **Funkcje:**
  - `calculate_feature_weights()` - Obliczanie wag cech
  - `adjust_weights()` - Dostosowywanie wag
  - `get_optimized_weights()` - Optymalne wagi
- **Cel:** Dynamiczna adaptacja wag w oparciu o doświadczenie

#### **3. CognitiveTeacher** (linie 1373-17730) - **GŁÓWNY RDZEŃ!**
- **Rola:** Model Poznawczy - analiza historycznych danych i generowanie wiedzy
- **KLUCZOWA ZASADA:** **"Korzysta WYŁĄCZNIE z rzeczywistych wyników (Y). Nie używa predykcji, danych przyszłych ani mieszania zbiorów."**
- **Pliki generowane:**
  - `PAMIEC_MODEL_POZNAWCZY.json` (linia 1386)
  - `WIEDZA_DLA_MODELU_DOCELOWEGO.json` (linia 1387)
- **Integracje:**
  - `WorldHierarchyManager()` - Hierarchia światów
  - `DynamicWeightsManager()` - Zarządzanie wagami
  - `self.swiat_doswiadczenia = {}` - Pamięć doświadczeń świata
- **Metody kluczowe:**
  - `wczytaj_pamiec()` - Wczytanie istniejących pamięci
  - `wczytaj_wiedze()` - Wczytanie wiedzy
  - `prepare_teacher_targets()` - Przygotowanie celów nauczania
  - `analiza_zmian()` - Analiza zmian
  - `generate_cognitive_memory()` - Generowanie pamięci poznawczej
  - `generate_target_knowledge()` - Generowanie wiedzy docelowej

---

## 🔍 **CZĘŚĆ C: ANALIZA I GENEROWANIE WIEDZY** (linie ~3800-19692)

Po trenowaniu modeli, czesc3.py przeprowadza **zaawansowaną analizę i generowanie wiedzy**:

### **Główne komponenty:**

#### **1. System Pamięci Obserwacji** (linie ~4200-4800)
- **Ładuje:** `pamiec_obserwacji.json` z czesc2.py
- **Generuje:** Aktualizowaną pamięć z nowymi predykcjami
- **Integracja:** Połączona z CognitiveTeacher

#### **2. Analiza कोशिश (Klas)** (linie ~5200-5350)
- **Generuje:** `analiza_klas.json`
- **Cel:** Analiza rozkładu klas wyników

#### **3. Analiza Pewności** (linie ~5350-5600)
- **Generuje:** `analiza_pewnosci.json`, `analiza_pewnosci_klasy.json`
- **Cel:** Ocena pewności predykcji

#### **4. Analiza Odchyleń** (linie ~5550-5650)
- **Generuje:** `analiza_odchylen.json`
- **Cel:** Analiza odchyleń predykcji

#### **5. Analiza Pamięci** (linie ~5640-5750)
- **Generuje:** `analiza_pamieci.json`
- **Cel:** Analiza pamięci obserwacji

#### **6. Kolektor Wiedzy** (linie ~5872-5970)
- **Generuje:** `kolektor_wiedzy.json` - **GŁÓWNY PLIK DLA AGENTÓW!**
- **Zawartość:**
  ```json
  {
      "analiza_klas": {...},
      "analiza_pewnosci": {...},
      "analiza_pewnosci_klasy": {...},
      "analiza_odchylen": {...},
      "analiza_pamieci": {...}
  }
  ```

#### **7. Zapis Plików Analiz** (linie ~5970-6000)
- **Generuje:**
  - `analiza_klas.json`
  - `analiza_pewnosci.json`
  - `analiza_pewnosci_klasy.json`
  - `analiza_odchylen.json`
  - `analiza_pamieci.json`
  - `kolektor_wiedzy.json`

#### **8. oraz kolejne bloki analiz (linie 7000-18000)**
- **Wiele powtarzających się bloków** analizy i generowania plików
- **Każdy blok:** ładuje pamięć, wykonuje analizę, zapisuje wyniki

#### **9. Raport Końcowy** (linie 19630-19692)
- **Wyświetla:**
  - Model
  - Katalog
  - Analizowane mecze
  - Wygenerowane pliki
- **Kończy:** "LABORATORIUM V2 ZAKOŃCZONE"

---

## 🔗 **ZALEŻNOŚCI MIĘDZY CZĘŚCIAMI**

### **PRZEPŁYW DANYCH:**

```
CZĘŚĆ 1 (czesc1.py)
│
├── Generuje modele i metadane
│   ├── modele_kursy_przygotowane/siec_*/model.h5
│   ├── modele_dataBase_futbol_trend/siec_*/model.h5
│   └── metadata.json, klasy.json, historia.json
│
└── Trening podstawowy
    (DataFrame: cechy → klasa Wyniku)

CZĘŚĆ 2 (czesc2.py)
│
├── Ładuje modele z C1
│   └── load_model() na model.h5
│
├── Generuje predykcje
│   ├── Predykcje historii
│   └── Predykcje aktualnych meczów
│
└── Zapisuje wyniki
    ├── WORLD_MATCH_DATABASE.json  ← **KLUCZOWY DLA C3**
    ├── pamięć_obserwacji.json    ← **UŻYWANY W C3**
    ├── ocena.json                ← **UŻYWANY W C3**
    └── predykcje_*.csv

CZĘŚĆ 3 (czesc3.py)  ← **TUTAJ JESTEŚMY**
│
├── **TRENOWANIE (Część A):**
│   ├── 3 bloki trenowania (jak C1)
│   ├── Generuje NOWE modele
│   └── Zapisuje: model.h5, metadata.json, itp.
│
├── **TEACHER ENGINE (Część B - RDZEŃ):**
│   ├── WorldHierarchyManager
│   │   └── Ładuje WORLD_MATCH_DATABASE.json (z C2)
│   ├── DynamicWeightsManager
│   │   └── Zarządza wagami cech
│   └── CognitiveTeacher
│       ├── Ładuje pamięć_obserwacji.json (z C2)
│       ├── Generuje PAMIEC_MODEL_POZNAWCZY.json
│       └── Generuje WIEDZA_DLA_MODELU_DOCELOWEGO.json
│
├── **ANALIZA WIEDZY (Część C):**
│   ├── Analiza klas
│   ├── Analiza pewności
│   ├── Analiza odchyleń
│   ├── Analiza pamięci
│   └── Kolektor wiedzy (kolektor_wiedzy.json)
│
└── **GENEROWANE PLIKI KLUCZOWE DLA SSI:**
    ├── PAMIEC_MODEL_POZNAWCZY.json
    ├── WIEDZA_DLA_MODELU_DOCELOWEGO.json
    ├── kolektor_wiedzy.json
    ├── analiza_*.json (6 plików)
    └── Zaktualizowane predykcje_*.csv

CZĘŚĆ 4 (czesc4.py) → [DO ANALIZY]
└── Prawdopodobnie:
    ├── Ładuje pliki z C3
    ├── Finalizacja procesu
    └── Generowanie ostatecznych raportów
```

### **KLUCZOWE ZALEŻNOŚCI:**

| Plik | Źródło | Cel | Użycie |
|------|--------|-----|--------|
| **WORLD_MATCH_DATABASE.json** | czesc2.py | czesc3.py | WorldHierarchyManager |
| **pamiec_obserwacji.json** | czesc2.py | czesc3.py | CognitiveTeacher |
| **ocena.json** | czesc2.py | czesc3.py | CognitiveTeacher |
| **PAMIEC_MODEL_POZNAWCZY.json** | czesc3.py | czesc4.py? | **DLA AGENTÓW** |
| **WIEDZA_DLA_MODELU_DOCELOWEGO.json** | czesc3.py | czesc4.py? | **DLA AGENTÓW** |
| **kolektor_wiedzy.json** | czesc3.py | czesc4.py? | **GŁÓWNY DLA AGENTÓW** |

---

## 🎯 **ISTNIEJĄCE STRUKTURY SSI**

### ❌ **Brak jawnej struktury SSI V5**

```python
# W czesc3.py NIE MA:
# - SSI_STAGE_STATUS (jak w czesc1.py)
# - SSI_AGENT_INPUT
# - SSI_AGENT_OUTPUT  
# - SSI_EVENTS
# - Funkcji update_stage_status()
```

**ALE:** Plik **GENERUJE KLUCZOWE PLIKI DLA SSI:**
- `PAMIEC_MODEL_POZNAWCZY.json`
- `WIEDZA_DLA_MODELU_DOCELOWEGO.json`
- `kolektor_wiedzy.json`

---

## 📋 **FUNKCJE W PLIKU**

### **Funkcje głównych bloków trenowania:**

| Linia | Funkcja | Rola |
|-------|---------|------|
| 335 | `buduj_siec(nazwa, cechy)` | Budowa i trenowanie sieci (Blok 1) |
| 2394 | `buduj_siec(nazwa, cechy)` | Budowa i trenowanie sieci (Blok 2) |
| 3128 | `buduj_siec(nazwa, cechy)` | Budowa i trenowanie sieci (Blok 3) |

### **Klasy Teacher Engine (RDZEŃ SSI V5):**

| Linia | Klasa | Rola |
|-------|-------|------|
| **1082** | **`WorldHierarchyManager`** | Zarządzanie hierarchiczną pamięcią światów |
| **1282** | **`DynamicWeightsManager`** | Dynamiczne zarządzanie wagami cech |
| **1373** | **`CognitiveTeacher`** | **Główny model poznawczy - generowanie wiedzy** |

### **Funkcje analizy (wybrane):**

| Linia | Funkcja | Rola |
|-------|---------|------|
| 10846 | `normalize(value, min_val, max_val)` | Normalizacja (duplikat z czesc2?) |
| 2032 | `analiza_rozkładu_wyników(...)` | Analiza rozkładu wyników |
| 1620 | `analiza_zmian(...)` | Analiza zmian w rankingach |
| ... | **Wiele funkcji...** | **Wiele analiz...** |

---

## 🎯 **PUNKTY STEROWANIA I KONTROLI**

### **🟢 ISTNIEJĄCE PUNKTY START**

#### **CZĘŚĆ A: TRENING MODELI**

| Nr | Lokalizacja | Typ | Co uruchamia |
|----|-------------|-----|-------------|
| 1 | Linie 6-20 | Importy | Ładowanie bibliotek (Sequential, Dense, EarlyStopping) |
| 2 | Linie 24-48 | Konfiguracja | Ustawienia KATALOG_MODELE, plików |
| 3 | Linie 29-168 | Wczytanie | `predykcja = pd.read_csv(PLIK_PREDYKCJI)` |
| 4 | Linie 182-198 | Wczytanie | `df = pd.read_csv(PLIK_TRENING)` |
| 5 | **Linie 335** | **Start budowy sieci** | `def buduj_siec(nazwa, cechy):` |
| 6 | Linie 344-347 | Start sieci | `print("START:", nazwa)` |
| 7 | Linie 356-364 | Inicjalizacja | `os.makedirs(katalog, exist_ok=True)` |
| 8 | Linie 580-601 | **Start treningu** | `historia = model.fit(...)` |
| 9 | Linie 928 | **Pętla główna** | `for nazwa, cechy in SPOJRZENIA.items()` |

#### **CZĘŚĆ B: TEACHER ENGINE**

| Nr | Lokalizacja | Typ | Co uruchamia |
|----|-------------|-----|-------------|
| 10 | **Linie 1082** | **Start WorldHierarchyManager** | `class WorldHierarchyManager:` |
| 11 | Linie 1105 | Ładowanie danych światów | `_load_world_data()` |
| 12 | Linie 1109-1116 | **Ładowanie WORLD_MATCH_DATABASE** | `json.load(WORLD_MATCH_DATABASE.json)` |
| 13 | **Linie 1282** | **Start DynamicWeightsManager** | `class DynamicWeightsManager:` |
| 14 | **Linie 1373** | **Start CognitiveTeacher** | `class CognitiveTeacher:` |
| 15 | Linie 1386-1387 | Definicja ścieżek pamięci | `pamiec_path`, `wiedza_path` |
| 16 | Linie 1401-1402 | **Ładowanie pamięci z czesc2** | `wczytaj_pamiec()`, `wczytaj_wiedze()` |

#### **CZĘŚĆ C: ANALIZA WIEDZY**

| Nr | Lokalizacja | Typ | Co uruchamia |
|----|-------------|-----|-------------|
| 17 | Linie 4202 | **Ładowanie pamięci obserwacji** | `pamiec_obserwacji = json.load(f)` |
| 18 | Linie 5872 | **Start Kolektora Wiedzy** | `kolektor_wiedzy = {}` |
| 19 | Linie 5970 | **Generowanie JSONów** | Pętla zapisu plików analiza_*.json |
| 20 | Linie 19630 | **Raport końcowy** | `print("LABORATORIUM V2 ZAKOŃCZONE")` |

### **🔴 ISTNIEJĄCE PUNKTY STOP/KONIEC**

| Nr | Lokalizacja | Typ | Co kończy |
|----|-------------|-----|-----------|
| 1 | Linie 611-624 | Test walidacyjny | `pred_val = model.predict(X_val)` |
| 2 | Linie 997-1000 | **Zapis CSV** | `tabela_40.to_csv(...)` |
| 3 | Linie 1084 | **Zapis modelu** | `model.save(...)` |
| 4 | Linie 5842 | **Zapis analizy** | `df_analiza_predykcji.to_csv(...)` |
| 5 | Linie 5963 | **Zapis kolektora wiedzy** | `json.dump(kolektor_wiedzy, ...)` |
| 6 | Linie 5970 | **Zapis wszystkich JSONów** | Pętla zapisu 6 plików analiza_*.json |
| 7 | Linie 19692 | **Koniec pliku** | Ostateczny koniec procesu |

---

## 🔧 **PUNKTY INTEGRACJI DLA SSI V5**

### **📌 PROPOZYCJA HOOKÓW DLA CZĘŚCI 3**

#### **1. STRUKTURA SSI V5 (Brak - Należy DODAĆ)**

**Lokalizacja:** Na początku pliku (linie 1-20)

```python
# Dodatkowe struktury SSI V5  
SSI_STAGE_STATUS = {
    "engine": "generatorDataBaseTrendAnalisAll",
    "part": "czesc3",
    "stage": "",
    "status": "",
    "timestamp": "",
    "processing_stats": {},
    "errors": []
}

SSI_AGENT_INPUT = {
    "files_to_process": None,
    "custom_data": None,
    "analysis_params": None,
    "world_data": None,  # WORLD_MATCH_DATABASE
    "observations": None
}

SSI_AGENT_OUTPUT = {
    "results": None,
    "analyses": None,
    "memory_updates": None,
    "diagnostics": None,
    "cognitive_memory": None,  # PAMIEC_MODEL_POZNAWCZY
    "target_knowledge": None,   # WIEDZA_DLA_MODELU_DOCELOWEGO
    "knowledge_collector": None # kolektor_wiedzy
}
```

#### **2. HOOKI DLA CZĘŚCI A (TRENING MODELI)**

| Hook | Lokalizacja | Cel | Parametry |
|------|-------------|-----|-----------|
| `SSI_TRAINING_START("czesc3")` | Linia 1 | Rozpoczęcie części 3 | part="czesc3" |
| `SSI_BLOCK_START("Block_1")` | Linia 29 | Rozpoczęcie Bloku 1 | block_name, model_config |
| `SSI_NETWORK_BUILD_START(nazwa)` | Linia 335 | Rozpoczęcie budowy sieci | network_name, features |
| `SSI_MODEL_TRAINING_START(nazwa)` | Linia 580 | Rozpoczęcie treningu | network, epochs, batch_size |
| `SSI_MODEL_TRAINING_COMPLETE(nazwa)` | Linia 601 | Zakończenie treningu | network, accuracy, duration |
| `SSI_BLOCK_COMPLETE("Block_1")` | ~Linia 1000 | Zakończenie Bloku 1 | block_name, results |
| `SSI_BLOCK_START("Block_2")` | ~Linia 2300 | Rozpoczęcie Bloku 2 | block_name |
| `SSI_BLOCK_START("Block_3")` | ~Linia 6050 | Rozpoczęcie Bloku 3 | block_name |

#### **3. HOOKI DLA CZĘŚCI B (TEACHER ENGINE - RDZEŃ)**

| Hook | Lokalizacja | Cel | Parametry |
|------|-------------|-----|-----------|
| `SSI_TEACHER_ENGINE_START()` | Linia 1082 | Rozpoczęcie Teacher Engine | engine="CognitiveTeacher" |
| `SSI_WORLD_HIERARCHY_LOAD()` | Linie 1105-1129 | Załadowanie hierarchii światów | levels_loaded, records_count |
| `SSI_WORLD_DB_LOAD()` | Linia 1110 | **Ładowanie WORLD_MATCH_DATABASE** | file_path, records_count |
| `SSI_WORLD_DB_INTEGRATION()` | Linie 1109-1130 | Integracja bazy danych | world_data_status |
| `SSI_COGNITIVE_TEACHER_START()` | Linia 1373 | Rozpoczęcie CognitiveTeacher | siec_name, features_count |
| `SSI_MEMORY_LOAD()` | Linie 1401-1402 | **Ładowanie pamięci z czesc2** | pamiec_path, wiedza_path |
| `SSI_COGNITIVE_ANALYSIS_START()` | Po inicjalizacji | Rozpoczęcie analizy poznawczej | teacher_status |
| `SSI_MEMORY_GENERATION_START()` | Linie 1386-1387 | **Generowanie pamięci poznawczej** | pamiec_path |
| `SSI_KNOWLEDGE_GENERATION_START()` | Linie 1386-1387 | **Generowanie wiedzy docelowej** | wiedza_path |

#### **4. HOOKI DLA CZĘŚCI C (ANALIZA WIEDZY)**

| Hook | Lokalizacja | Cel | Parametry |
|------|-------------|-----|-----------|
| `SSI_KNOWLEDGE_ANALYSIS_START()` | ~Linia 4200 | Rozpoczęcie analizy wiedzy | analysis_type |
| `SSI_OBSERVATION_MEMORY_LOAD()` | Linia 4202 | **Ładowanie pamięci obserwacji** | file_path, records |
| `SSI_KNOWLEDGE_COLLECTOR_START()` | Linia 5872 | **Start kolektora wiedzy** | collector_name |
| `SSI_KNOWLEDGE_SAVE_START()` | Linie 5938+ | Zapis plików wiedzy | file_list, total_files |
| `SSI_ANALYSIS_COMPLETE()` | ~Linia 6000 | Zakończenie analizy | results_summary |
| `SSI_TRAINING_COMPLETE("czesc3")` | Linia 19692 | **Zakończenie części 3** | part="czesc3", status="completed" |

---

## 📥 **WEJŚCIA DLA AGENTÓW**

### **1. Dane z poprzednich części:**

| Typ | Źródło | Format | Użycie w czesc3.py |
|-----|--------|--------|-------------------|
| **WORLD_MATCH_DATABASE.json** | czesc2.py | JSON | WorldHierarchyManager (linie 1061, 1110-1116) |
| **pamiec_obserwacji.json** | czesc2.py | JSON | CognitiveTeacher (linie 4202, 1805) |
| **ocena.json** | czesc2.py | JSON | CognitiveTeacher (linie 4202) |
| **predykcje_*.csv** | czesc2.py | CSV | Rather predykcji (linie 5127, itp.) |
| **Modele .h5** | czesc1.py | Keras | `load_model()` (linie 4105, 6376, itp.) |
| **metadata.json** | czesc1.py | JSON | Wczytywanie w buduj_siec() |
| **klasy.json** | czesc1.py | JSON | Wczytywanie w buduj_siec() |

### **2. Potencjalne wejścia od agentów (PRZYSZŁOŚĆ):**

| Typ | Propozycja struktury | Opis |
|-----|---|---|
| World data override | `SSI_AGENT_INPUT["world_data"]` | Nadpisanie WORLD_MATCH_DATABASE |
| Memory override | `SSI_AGENT_INPUT["cognitive_memory"]` | Dodatkowa pamięć poznawcza |
| Knowledge base | `SSI_AGENT_INPUT["knowledge_base"]` | Baza wiedzy z zewnątrz |
| Analysis parameters | `SSI_AGENT_INPUT["analysis_params"]` | Parametry analiz untuk Teacher Engine |

---

## 📤 **WYJŚCIA DLA AGENTÓW**

### **1. Kluczowe pliki SSI generowane w czesc3.py:**

| Plik | Lokalizacja | Format | Zawartość | **Priorytet** |
|------|-------------|--------|-----------|--------------|
| **PAMIEC_MODEL_POZNAWCZY.json** | `{KATALOG_MODELE}/{siec_name}/` | JSON | Pamięć poznawcza modelu | ⭐⭐⭐ **KRYTYCZNY** |
| **WIEDZA_DLA_MODELU_DOCELOWEGO.json** | `{KATALOG_MODELE}/{siec_name}/` | JSON | Wiedza dla modelu docelowego | ⭐⭐⭐ **KRYTYCZNY** |
| **kolektor_wiedzy.json** | `{KATALOG_MODELE}/{siec_name}/` | JSON | **Zbiorczy kolektor wiedzy** | ⭐⭐⭐ **GŁÓWNY DLA AGENTÓW** |
| **analiza_klas.json** | `{KATALOG_MODELE}/{siec_name}/` | JSON | Analiza rozkładu klas | ⭐⭐ |
| **analiza_pewnosci.json** | `{KATALOG_MODELE}/{siec_name}/` | JSON | Analiza pewności predykcji | ⭐⭐ |
| **analiza_pewnosci_klasy.json** | `{KATALOG_MODELE}/{siec_name}/` | JSON | Analiza pewności klas | ⭐⭐ |
| **analiza_odchylen.json** | `{KATALOG_MODELE}/{siec_name}/` | JSON | Analiza odchyleń | ⭐⭐ |
| **analiza_pamieci.json** | `{KATALOG_MODELE}/{siec_name}/` | JSON | Analiza pamięci | ⭐⭐ |

### **2. Nowe modele (wyjście do czesc4.py):**

| Typ | Lokalizacja | Format | Użycie |
|-----|-------------|--------|--------|
| modele_kursy_przygotowane/siec_*/model.h5 | 3 bloki trenowania | Keras .h5 | **Dla czesc4.py** |
| modele_dataBase_futbol_trend/siec_*/model.h5 | Powtarzające bloki | Keras .h5 | **Dla czesc4.py** |

### **3. Potencjalne wyjścia dla agentów:**

| Typ | Propozycja struktury | Opis |
|-----|---|---|
| Cognitive Memory | `SSI_AGENT_OUTPUT["cognitive_memory"]` | PAMIEC_MODEL_POZNAWCZY.json |
| Target Knowledge | `SSI_AGENT_OUTPUT["target_knowledge"]` | WIEDZA_DLA_MODELU_DOCELOWEGO.json |
| Knowledge Collector | `SSI_AGENT_OUTPUT["knowledge_collector"]` | kolektor_wiedzy.json |
| Analysis Results | `SSI_AGENT_OUTPUT["analyses"]` | Wszystkie pliki analiza_*.json |
| Teacher Status | `SSI_AGENT_OUTPUT["teacher_status"]` | Status Teacher Engine |

---

## 🔗 **SEKWENCJA ZDARZEŃ DLA SSI V5**

### **Pełny przepływ zdarzeń:**

```
CZĘŚĆ 1 → CZĘŚĆ 2 → CZĘŚĆ 3 (Teacher Engine) → CZĘŚĆ 4

CZĘŚĆ 3 - SEKWENCJA:
├─ SSI_TRAINING_START_czesc3
│
├─ BLOK 1 (kursy_przygotowane):
│   ├─ SSI_BLOCK_START("Block_1")
│   ├─ Sieć 1: SSI_NETWORK_BUILD → SSI_TRAINING_START → SSI_TRAINING_COMPLETE
│   ├─ Sieć 2: SSI_NETWORK_BUILD → SSI_TRAINING_START → SSI_TRAINING_COMPLETE
│   │   ... (wszystkie sieci w SPOJRZENIA)
│   └─ SSI_BLOCK_COMPLETE("Block_1")
│
├─ BLOK 2 (dataBase_futbol_trend):
│   ├─ SSI_BLOCK_START("Block_2")
│   ├─ Sieci: bautuj_siec() dla każdej w SPOJRZENIA
│   └─ SSI_BLOCK_COMPLETE("Block_2")
│
├─ BLOK 3 (Rozszerzone):
│   ├─ SSI_BLOCK_START("Block_3")
│   └─ SSI_BLOCK_COMPLETE("Block_3")
│
├─ TEACHER ENGINE (RDZEŃ):
│   ├─ SSI_TEACHER_ENGINE_START
│   │
│   ├─ WorldHierarchyManager:
│   │   ├─ SSI_WORLD_HIERARCHY_LOAD
│   │   └─ SSI_WORLD_DB_LOAD (WORLD_MATCH_DATABASE.json)
│   │
│   ├─ DynamicWeightsManager:
│   │   └─ (Weights management hooks)
│   │
│   └─ CognitiveTeacher:
│       ├─ SSI_COGNITIVE_TEACHER_START
│       ├─ SSI_MEMORY_LOAD (z czesc2.py)
│       ├─ SSI_MEMORY_GENERATION_START (PAMIEC_MODEL_POZNAWCZY.json)
│       └─ SSI_KNOWLEDGE_GENERATION_START (WIEDZA_DLA_MODELU...)
│
├─ ANALIZA WIEDZY:
│   ├─ SSI_KNOWLEDGE_ANALYSIS_START
│   ├─ SSI_OBSERVATION_MEMORY_LOAD
│   ├─ SSI_KNOWLEDGE_COLLECTOR_START
│   ├─ Klarownica analiza_*.json
│   └─ SSI_KNOWLEDGE_SAVE_START
│
└─ SSI_TRAINING_COMPLETE_czesc3
```

---

## 🏆 **PODSUMOWANIE: DLACZEGO CZĘŚĆ 3 JEST NAJWAŻNIEJSZA?)**

**czesc3.py to SRCE SSI V5 ponieważ:**

### ✅ **ZAWERA TEACHER ENGINE:**
- `WorldHierarchyManager` - Inteligentna hierarchia światów
- `DynamicWeightsManager` - Dynamiczna adaptacja wag
- `CognitiveTeacher` - **Główny model poznawczy**

### ✅ **GENERUJE KLUCZOWE PLIKI DLA AGENTÓW:**
- **PAMIEC_MODEL_POZNAWCZY.json** - Pamięć poznawcza
- **WIEDZA_DLA_MODELU_DOCELOWEGO.json** - Wiedza docelowa
- **kolektor_wiedzy.json** - **GŁÓWNY ZBIÓR WIEDZY DLA AGENTÓW**
- **analiza_*.json** - 6 plików analiz

### ✅ **INTEGRUJE WSZYSTKIE CZĘŚCI:**
- **Ładuje WORLD_MATCH_DATABASE.json** z czesc2.py
- **Korzysta z modeli** z czesc1.py
- **Generuje dane** dla czesc4.py
- **Jest mostem** między trenowaniem a agentami

### ✅ **MA 3 WARSTWY FUNKCJONALNOŚCI:**
1. **Trenowanie modeli** (jak czesc1.py) - 3 bloki
2. **Teacher Engine** (rdzeń SSI) - klasy Teacher
3. **Generowanie wiedzy** - analizy i kolektory

---

## 📋 **STAN I REKOMENDACJE**

### **STAN OBECNY:**
- ✅ **Rola:** Zidentyfikowana (Teacher Engine Core + Trenowanie + Wiedza)
- ✅ **Struktura:** 3 Części (Trenowanie + Teacher + Analiza)
- ✅ **Funkcje:** 3 klasy Teacher + 3× buduj_siec() + wiele analitycznych
- ✅ **Wejścia:** WORLD_MATCH_DATABASE.json, pamięć_obserwacji.json, modele .h5
- ✅ **Wyjścia:** Pamięć poznawcza, wiedza docelowa, kolektor wiedzy, analizy
- ❌ **SSI Status:** Brak struktur SSI V5 (należy dodać)
- ⏳ **Hooki:** Zidentyfikowano 20+ punktów integracji

### **REKOMENDACJE DLA IMPLEMENTACJI:**

1. **Dodać struktury SSI** na początku pliku
2. **Dodać import WORLD_MATCH_DATABASE** (z czesc2.py) jako SSI_AGENT_INPUT
3. **Zdefiniować hooki dla:**
   - Trenowania modeli (3 bloki)
   - Teacher Engine (WorldHierarchy, DynamicWeights, CognitiveTeacher)
   - Generowania wiedzy (pamięć poznawcza, wiedza docelowa, kolektor)
4. **Zapewnić ciągłość danych** między częściami

### **KOLEJNE KROKI:**
1. ✅ **CZĘŚĆ 1:** Mapa gotowa
2. ✅ **CZĘŚĆ 2:** Mapa gotowa  
3. ✅ **CZĘŚĆ 3:** Mapa gotowa (**ten dokument**)
4. ⏳ **CZĘŚĆ 4:** Przeanalizować czesc4.py → `SSI_V5_CZESC4_HOOK_MAP.md`
5. ⏳ **ARCHITEKTURA:** Utworzyć `SSI_V5_FULL_GENERATOR_HOOK_ARCHITECTURE.md`
6. ⏳ **IMPLEMENTACJA:** Dodać hooki do wszystkich 4 części

---

## 🎉 **SSI V5 CZĘŚĆ 3 HOOK MAP READY** ✅

*Dokument wygenerowany dla SSI V5 - CZĘŚĆ 3 - MAPA HOOKÓW (RDZEŃ TEACHER ENGINE)*
*Data: 2026-08-03*
*Analizowany plik: czesc3.py (linie 1-19692)*
*Odkrycie: **CZĘŚĆ 3 TO GŁÓWNY ENGINE SSI V5 Z TEACHER EM!**
