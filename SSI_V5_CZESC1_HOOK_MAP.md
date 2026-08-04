# SSI V5 - CZĘŚĆ 1 - MAPA HOOKÓW INTEGRACYJNYCH

## INFORMACJE PODSTAWOWE

- **Plik:** `czesc1.py`
- **Część generatora:** DataBase Trend Analysis (generowanie modeli na podstawie trendów kursów)
- **Data mapowania:** 2026-08-03
- **Status:** Przypisane funkcje hookowe, oczekujący na implementację wywołań
- **Zależności:** Korzysta z istniejących struktur SSI V5 (`SSI_STAGE_STATUS`, `SSI_AGENT_INPUT`, `SSI_AGENT_OUTPUT`)

---

## STRUKTURA PLIKU

Plik `czesc1.py` składa się z **dwóch niezależnych bloków trenowania**:

### BLOK 1: `DataBase_futbol_trend` (linie ~9530-10175)
- **Konfig:** `PLIK_PREDYKCJI = "dane/dataBase_futbol_trend.csv"`
- **Trening:** `PLIK_TRENING = "dane/kod_dataBase_futbol_trend.csv"`
- **Modele:** `KATALOG_MODELE = "modele_dataBase_futbol_trend"`
- **Sieci:** 11 sieci zdefiniowanych w `SPOJRZENIA` (siec_01_zmiana_kursow → siec_11_statystyka)

### BLOK 2: `kursy_przygotowane` (linie ~10350-11145)
- **Konfig:** `PLIK_PREDYKCJI = "dane/kursy_przygotowane.csv"`
- **Trening:** `PLIK_TRENING = "dane/mozg_kursy_przygotowane.csv"`
- **Modele:** `KATALOG_MODELE = "modele_kursy_przygotowane"`
- **Sieci:** 4 sieci zdefiniowanych w `SPOJRZENIA` (siec_01_start_kursow → siec_04_procent_kursow)

**KAŻDY BLOK ma identyczną strukturę:**
1. Konfiguracja plików
2. Wczytanie schematu kolumn i danych treningowych
3. Filtracja poprawnych wyników
4. Identyfikacja klas
5. Funkcja `podziel_dane()` - podział 50/10/40
6. Funkcja `buduj_siec()` - inauguracja, trening, zapis
7. Pętla główna iterująca po `SPOJRZENIA.items()`

---

## ISTNIEJĄCE STRUKTURY SSI V5 (od linii 14-213)

### 1. Globalny Rejestr Statusu
```python
SSI_STAGE_STATUS = {
    "engine": "generatorDataBaseTrendAnalisAll",
    "part": "czesc1", 
    "stage": "",
    "status": "",
    "timestamp": "",
    "processing_stats": {},
    "errors": []
}
```

### 2. Punkty Wejścia dla Agentów
```python
SSI_AGENT_INPUT = {
    "files_to_process": None,
    "custom_data": None, 
    "analysis_params": None,
    "observations": None,
    "research_task": None
}
```

### 3. Punkty Wyjścia dla Agentów
```python
SSI_AGENT_OUTPUT = {
    "results": None,
    "analyses": None,
    "memory_updates": None, 
    "diagnostics": None,
    "processing_time": None
}
```

### 4. Funkcje Obsługi Agentów
- `update_stage_status(stage, status, timestamp=None)` - Aktualizuje `SSI_STAGE_STATUS`
- `register_agent_input(data_type, data)` - Rejestruje dane wejściowe
- `export_agent_output(data_type, data)` - Eksportuje dane wyjściowe

### 5. NOWE Funkcje Hookowe (dodane w ramach SSI V5 Czesc1)
```python
# Dodano: import time (linia 8)

# Funkcje logowania zdarzeń (linie 119-213)
SSI_EVENTS = []
SSI_EVENT(event, network, stage, status, data)  # Główny logger
SSI_START_NETWORK_BUILD(network, features)     # Hook: Start budowy
SSI_START_TRAINING(network, shapes, params)     # Hook: Start treningu  
SSI_END_TRAINING(network, metrics, duration)    # Hook: Koniec treningu
SSI_OUTPUT_READY(network, catalog, files, acc) # Hook: Gotowość wyjścia
SSI_NETWORK_FINISH(network)                    # Hook: Koniec sieci
SSI_MAIN_LOOP_START(total_networks)           # Hook: Start pętli głównej
SSI_MAIN_LOOP_END(completed, skipped)         # Hook: Koniec pętli głównej
```

---

## MIEJSCA INTEGRACJI HOOKÓW

### 🎯 K Category: **START PROCESU**

#### 1.1. START BUDOWY SIECI
- **Lokalizacja:** Początek funkcji `buduj_siec(nazwa, cechy)`
- **Linie:** 9530 (Blok1), 10515 (Blok2)
- **Akcja:** `SSI_START_NETWORK_BUILD(nazwa, cechy)`
- **Parametry:**
  - `network`: nazwa sieci (np. "siec_01_zmiana_kursow")
  - `features`: lista cech辽
- **Cel:** Agent wie, która sieć startuje
- **Częstotliwość:** 1x na sieć (nie w pętli danych)

#### 1.2. START PĘTLI GŁÓWNEJ
- **Lokalizacja:** Przed `for nazwa, cechy in SPOJRZENIA.items()`
- **Linie:** 10123 (Blok1), 11108 (Blok2) 
- **Akcja:** `SSI_MAIN_LOOP_START(len(SPOJRZENIA))`
- **Parametry:** `total_networks` = liczba sieci do przetworzenia
- **Cel:** Agent wie, ile sieci będzie trenowanych

### 🎯 KATEGORY: **TRENING**

#### 2.1. START SZKOLENIA
- **Lokalizacja:** Bezpośrednio PRZED `model.fit()`
- **Linie:** ~9777 (Blok1), ~10762 (Blok2)
- **Akcja:** `SSI_START_TRAINING(nazwa, X_train.shape, y_train.shape, X_val.shape, epochs, batch_size)`
- **Parametry:**
  - `network`: nazwa sieci
  - `X_train_shape`: rozmiar danych treningowych
  - `y_train_shape`: rozmiar etykiet treningowych  
  - `X_val_shape`: rozmiar danych walidacyjnych
  - `epochs`: liczba epok (200)
  - `batch_size`: rozmiar batcha (32)
- **Cel:** Agent wie, że trening się rozpoczął
- **UWAGA:** Musi być **PRZED** `model.fit()`, nie wewnątrz

#### 2.2. KONIEC SZKOLENIA  
- **Lokalizacja:** Bezpośrednio PO `model.fit()` (przed testem walidacyjnym)
- **Linie:** ~9797 (Blok1), ~10782 (Blok2)
- **Akcja:** `SSI_END_TRAINING(nazwa, accuracy, loss, val_accuracy, val_loss, duration)`
- **Parametry:**
  - `network`: nazwa sieci
  - `accuracy`: ostateczna dokładność na treningu (z `historia.history['accuracy'][-1]`)
  - `loss`: ostateczna strata na treningu
  - `val_accuracy`: dokładność na walidacji
  - `val_loss`: strata na walidacji  
  - `duration`: czas trwania treningu (z `time.time()`)
- **Cel:** Agent wie, że trening się zakończył i zna wyniki
- **UWAGA:** Musi być **PO** `model.fit()`, przed `model.predict()`

### 🎯 KATEGORY: **ZAPIS WYNIKÓW**

#### 3.1. GOTOWOŚĆ WYJŚCIA
- **Lokalizacja:** PRZED zapisywaniem plików CSV/JSON/H5
- **Linie:** ~9970 (Blok1 - przed `tabela_40.to_csv()`), ~10955 (Blok2)
- **Akcja:** `SSI_OUTPUT_READY(nazwa, katalog, file_list, acc)`
- **Parametry:**
  - `network`: nazwa sieci
  - `catalog`: ścieżka katalogu (np. "modele_dataBase_futbol_trend/siec_01_zmiana_kursow")
  - `file_list`: lista plików do zapisu: `["walidacja_40_procent.csv", "model.h5", "klasy.json", "metadata.json", "historia.json"]`
  - `model_accuracy`: dokładność modelu (`acc` z walidacji)
- **Cel:** Agent wie, które pliki zostaną wygenerowane
- **UWAGA:** Musi być **PRZED** wszelkimi operacjami zapisu

#### 3.2. KONIEC PRZETWARZANIA SIECI
- **Lokalizacja:** Na końcu funkcji `buduj_siec()` (po wszystkich zapisach)
- **Linie:** ~10117 (Blok1), ~11097 (Blok2)
- **Akcja:** `SSI_NETWORK_FINISH(nazwa)`
- **Parametry:** `network`: nazwa sieci
- **Cel:** Agent wie, że cała sieć została przetworzona

### 🎯 KATEGORY: **ZAKOŃCZENIE PROCESU**

#### 4.1. KONIEC PĘTLI GŁÓWNEJ
- **Lokalizacja:** PO pętli `for nazwa, cechy in SPOJRZENIA.items()`
- **Linie:** ~10175 (Blok1), ~11145 (Blok2)
- **Akcja:** `SSI_MAIN_LOOP_END(completed_networks, skipped_networks)`
- **Parametry:**
  - `completed_networks`: liczba pomyślnie przetrenowanych sieci
  - `skipped_networks`: liczba pominiętych sieci (z `brak` cech)
- **Cel:** Agent wie, że cały blok został ukończony

---

## SEKWENCJA ZDARZEŃ DLA POJEDYNCZEJ SIECI

```
1. NETWORK_START           → Rozpoczęcie budowy sieci
   └─ Dane: network_name, features_list

2. TRAINING_START          → Rozpoczęcie treningu  
   └─ Dane: shapes, epochs, batch_size

3. TRAINING_END            → Zakończenie treningu
   └─ Dane: accuracy, loss, val_accuracy, val_loss, duration

4. OUTPUT_READY            → Gotowość wyników
   └─ Dane: catalog, file_list, model_accuracy

5. NETWORK_FINISH          → Zakończenie przetwarzania sieci
   └─ Dane: network_name
```

**DMY KAŻDEJ SIECI: 5 zdarzeń w linku kolejności**

---

## SEKWENCJA ZDARZEŃ DLA CAŁEGO BLOKU

```
BLOK 1 (DataBase_futbol_trend):
├─ MAIN_LOOP_START          → Rozpoczęcie pętli (11 sieci)
│
├─ Sieć 1: NETWORK_START → TRAINING_START → TRAINING_END → OUTPUT_READY → NETWORK_FINISH
├─ Sieć 2: NETWORK_START → TRAINING_START → TRAINING_END → OUTPUT_READY → NETWORK_FINISH  
├─ Sieć 3: NETWORK_START → TRAINING_START → TRAINING_END → OUTPUT_READY → NETWORK_FINISH
├─ ... (11 sieci)
│
└─ MAIN_LOOP_END            → Zakończenie pętli

BLOK 2 (kursy_przygotowane):
├─ MAIN_LOOP_START          → Rozpoczęcie pętli (4 sieci)
│
├─ Sieć 1: NETWORK_START → TRAINING_START → TRAINING_END → OUTPUT_READY → NETWORK_FINISH
├─ Sieć 2: NETWORK_START → TRAINING_START → TRAINING_END → OUTPUT_READY → NETWORK_FINISH
├─ Sieć 3: NETWORK_START → TRAINING_START → TRAINING_END → OUTPUT_READY → NETWORK_FINISH
├─ Sieć 4: NETWORK_START → TRAINING_START → TRAINING_END → OUTPUT_READY → NETWORK_FINISH
│
└─ MAIN_LOOP_END            → Zakończenie pętli
```

---

## PUNKTY WEJŚCIA DLA AGENTÓW

### 1. DANE WEJŚCIOWE
- **Główne źródło:** `PLIK_PREDYKCJI` i `PLIK_TRENING` (CSV)
- **Format:** Kolumny zdefiniowane przez `NAGLOWKI` (z pliku predykcji)
- **Agencyjne wejście:** `SSI_AGENT_INPUT["files_to_process"]`
- **Możliwości:**
  - `--files_to_process`: Nadpisanie domyślnych plików
  - `custom_data`: Dodatkowe dane treningowe
  - `analysis_params`: Parametry analizy (np. inne podziały danych)

### 2. KONFIGURACJA SIECI
- **Sieci zdefiniowane:** `SPOJRZENIA` dict
- **Format:** `{nazwa_sieci: [lista_cech]}`
- **Przykłady:**
  - Blok1: `siec_01_zmiana_kursow: ["zmiana_1", "zmiana_X", "zmiana_2"]`
  - Blok2: `siec_01_start_kursow: ["kurs_1_start", "kurs_X_start", "kurs_2_start"]`
- **Agencyjne wejście:** `SSI_AGENT_INPUT["analysis_params"]["network_features"]`

### 3. PARAMETRY TRENINGU
- **Epochs:** 200 (stałe)
- **Batch size:** 32 (stałe)
- **EarlyStopping:** patience=20, restore_best_weights=True
- **Podział danych:** 50% treening, 10% walidacja, 40% obserwacja
- **Agencyjne wejście:** `SSI_AGENT_INPUT["analysis_params"]["training_params"]`

---

## PUNKTY WYJŚCIA DLA AGENTÓW

### 1. MODELE WYTRENOWANE
- **Format:** `.h5` (Keras Sequential)
- **Lokalizacja:** `{KATALOG_MODELE}/{nazwa_sieci}/model.h5`
- **Agencyjne wyjście:** `SSI_AGENT_OUTPUT["results"]["models"]`

### 2. WYNIKI WALIDACJI
- **Format:** CSV z predykcjami na 40% danych
- **Lokalizacja:** `{KATALOG_MODELE}/{nazwa_sieci}/walidacja_40_procent.csv`
- **Zawartość:** id_meczu, cechy, klasa_predykcji, wynik_predykcji, prawdopodobienstwo, wynik
- **Agencyjne wyjście:** `SSI_AGENT_OUTPUT["results"]["validations"]`

### 3. METADANE MODELI
- **Format:** JSON
- **Lokalizacje:**
  - `klasy.json`: Mapa klas (WYNIKI → index)
  - `metadata.json`: nazwa, cechy, dokładność, podział
  - `historia.json`: Historia treningu (accuracy, loss per epoch)
- **Agencyjne wyjście:** `SSI_AGENT_OUTPUT["analyses"]["metadata"]`

### 4. ZDARZENIA PRZETWARZANIA
- **Format:** Lista zdarzeń z timestampami
- **Dostęp:** `SSI_EVENTS` (globalna lista)
- **Agencyjne wyjście:** `SSI_AGENT_OUTPUT["events"]` (przez `export_agent_output`)

---

## STAN OBECNY (PO ETAPIE PRZYGOTOWAŃ)

### ✅ Zaimplementowane
- `import time` (linia 8)
- Funkcje hookowe: `SSI_EVENT()`, `SSI_START_NETWORK_BUILD()`, `SSI_START_TRAINING()`, `SSI_END_TRAINING()`, `SSI_OUTPUT_READY()`, `SSI_NETWORK_FINISH()`, `SSI_MAIN_LOOP_START()`, `SSI_MAIN_LOOP_END()` (linie 119-213)
- Globalna lista `SSI_EVENTS` (linia 105)
- Integracja z istniejącymi `SSI_STAGE_STATUS`, `SSI_AGENT_OUTPUT`

### ⏳ Oczekujące na Implementację
- [ ] Wywołanie `SSI_START_NETWORK_BUILD()` w `buduj_siec()` (linie 9530, 10515)
- [ ] Wywołanie `SSI_START_TRAINING()` przed `model.fit()` (linie ~9777, ~10762)
- [ ] Wywołanie `SSI_END_TRAINING()` po `model.fit()` (linie ~9797, ~10782)
- [ ] Wywołanie `SSI_OUTPUT_READY()` przed zapisem plików (linie ~9970, ~10955)
- [ ] Wywołanie `SSI_NETWORK_FINISH()` na końcu `buduj_siec()` (linie ~10117, ~11097)
- [ ] Wywołanie `SSI_MAIN_LOOP_START()` przed pętlą główną (linie ~10123, ~11108)
- [ ] Wywołanie `SSI_MAIN_LOOP_END()` po pętli głównej (linie ~10175, ~11145)

### ❌ Zakazane (według zaleceń)
- Zmiana `model.fit()`
- Zmiana architektury sieci (Sequential, Dense, Dropout)
- Zmiana danych treningowych
- Zmiana zapisów istniejących plików
- Przenoszenie kodu między plikami

---

## SCHEMAT INTEGRACJI (PRZYKŁAD)

```python
# BLOK 1 - Pętla główna
def buduj_siec(nazwa, cechy):
    # 1. START BUDOWY SIECI
    SSI_START_NETWORK_BUILD(nazwa, cechy)
    
    # ... istniejący kod (katalog, dane, model) ...
    
    # 2. START SZKOLENIA
    start_time = time.time()
    SSI_START_TRAINING(nazwa, X_train.shape, y_train.shape, X_val.shape, 200, 32)
    
    # 3. TRENING
    historia = model.fit(...)
    
    # 4. KONIEC SZKOLENIA
    duration = time.time() - start_time
    last_epoch_acc = historia.history['accuracy'][-1]
    last_epoch_val_acc = historia.history['val_accuracy'][-1] 
    SSI_END_TRAINING(nazwa, last_epoch_acc, ..., last_epoch_val_acc, ..., duration)
    
    # ... test walidacyjny, predykcje ...
    
    # 5. GOTOWOŚĆ WYJŚCIA
    file_list = ["walidacja_40_procent.csv", "model.h5", "klasy.json", "metadata.json", "historia.json"]
    SSI_OUTPUT_READY(nazwa, katalog, file_list, acc)
    
    # ... zapis plików ...
    
    # 6. KONIEC PRZETWARZANIA SIECI
    SSI_NETWORK_FINISH(nazwa)

# Pętla główna
SSI_MAIN_LOOP_START(len(SPOJRZENIA))
for nazwa, cechy in SPOJRZENIA.items():
    # ... sprawdzenie brak cech ...
    buduj_siec(nazwa, cechy)
SSI_MAIN_LOOP_END(completed_count, skipped_count)
```

---

## REKOMENDACJE DLA NASTĘPNYCH CZĘŚCI

### Dla czesc2.py, czesc3.py, czesc4.py:
1. **Sprawdzić czy używają tej samej struktury** `buduj_siec()`
2. **Zidentyfikować unikalne nazwy sieci** (jeśli inne niż w czesc1)
3. **Sprawdzić czy korzystają z tych samych** `SSI_STAGE_STATUS` i `SSI_AGENT_*`
4. **Określić zależności między częściami** (czy czesc2 używa wyjść z czesc1?)
5. **Zmapować punkty wejścia/wyjścia** dla przenoszenia danych między częściami

### Konwencja nazewnictwa:
- **Hooki:** `SSI_*` (prefix dla wszystkich funkcji SSI)
- **Zdarzenia:** `NETWORK_START`, `TRAINING_START`, itp. (DUŻE LITERY)
- **Statusy:** `started`, `completed`, `ready`, `error` (małe litery)
- **Sieci:** zachować oryginalne nazwy z `SPOJRZENIA`

---

## PODSUMOWANIE

**czesc1.py jest gotowa do integracji z SSI V5:**
- ✅ Istnieją struktury agentowe (`SSI_STAGE_STATUS`, `SSI_AGENT_INPUT/OUTPUT`)
- ✅ Zdefiniowane funkcje hookowe (7ункcji для 7 typów zdarzeń)
- ✅ Zidentyfikowane dokładne miejsca integracji (15 punktów w 2 blokach)
- ✅ Przygotowana sekwencja zdarzeń (5 zdarzeń na sieć)
- ✅ Określone punkty wejścia/wyjścia dla agentów
- ⏳ **Oczekuje na dodanie wywołań hooków** (14 wywołań: 7 typów × 2 bloki)

**Następny krok:**
1. Utworzyć `SSI_V5_CZESC2_HOOK_MAP.md` (analiza czesc2.py)
2. Utworzyć `SSI_V5_CZESC3_HOOK_MAP.md` (analiza czesc3.py)  
3. Utworzyć `SSI_V5_CZESC4_HOOK_MAP.md` (analiza czesc4.py)
4. Utworzyć `SSI_V5_FULL_GENERATOR_HOOK_ARCHITECTURE.md` (integracja wszystkich części)
5. **Dopiero wtedy** dodać wywołania hooków do wszystkich plików

---

*Dokument wygenerowany dla SSI V5 - CZĘŚĆ 1 - MAPOWANIE HOOKÓW*
*Data: 2026-08-03*
*Analizowany plik: czesc1.py (linie 1-26903+)*
