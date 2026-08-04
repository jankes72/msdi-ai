# SSI V5 PART ANALYSIS - czesc1.py

## Podsumowanie Części 1

**Plik:** `czesc1.py`  
**Liczba linii:** 26,818  
**Rola w silniku:** Przetwarzanie wstępne i analiza trendów kursów bukmacherskich

---

## 1. ODPOWIEDZIALNOŚĆ CZĘŚCI

`czesc1.py` jest odpowiedzialna za:

### 1.1 Główne funkcjonalności
- **Przetwarzanie surowych danych kursów** - konwersja i normalizacja danych z plików CSV
- **Ekstrakcja cech trendów** - obliczanie wskaźników zmienności, amplitudy, tempa zmian
- **Klasyfikacja kursów** - podział kursów na poziomy (poziom1-poziom20 wg wartości)
- **Analiza statystyczna** - średnie, mediany, odchylenia standardowe
- **Przygotowanie danych wejściowych** dla kolejnych części silnika

### 1.2 Kluczowe dane wejściowe
- `./dane/database_popularne_dzisiaj.csv` - popularne mecze z kursami
- `./dane/database_dzisiaj.csv` - wszystkie mecze z kursami
- Format: CSV z separatorem `;` zawierający historię kursów dla każdego meczu

### 1.3 Kluczowe dane wyjściowe
- `./dane/dataBase_futbol_popularne_trend.csv` - przetworzone dane trendów (popularne)
- `./dane/dataBase_futbol_trend.csv` - przetworzone dane trendów (wszystkie)
- `./dane/kursy_popularne_przygotowane.csv` - sklasyfikowane kursy

---

## 2. STRUKTURA PLIKU

### 2.1 Główne sekcje kodu

| Sekcja | Linie | Opis |
|--------|-------|------|
| **Funkcje narzędziowe** | 14-256 | `normalize()`, `bezpieczny_log()`, `oblicz_cechy_3kursy_rozszerzone()` |
| **START - Przetwarzanie głównych plików** | 428-454 | Główna pętla przetwarzania plików CSV |
| **Przetwarzanie kursów popularnych** | 462-1093 | Odczyt, klasyfikacja i zapis kursów popularnych |
| **Klasyfikacja kursów** | 1095-1490 | Funkcje `classify_odds()` i `process_and_save_data()` |
| **Funkcje matematyczne** | 1835-2348 | Funkcje pomocnicze: `liczba()`, `odleglosc()`, `wynik_liczbowy()` |
| **Analiza statystyczna** | 2349-3000 | Funkcje `poisson()`, `dixon_coles()`, `policz_dc()` |
| **Klasyfikacja wyników** | 3400-4500 | `klasyfikuj_wynik()`, `normalizuj()`, analizy korelacji |
| **Analiza grup i warstw** | 7500-8500 | `analiza_grupy()`, `pobierz_poziomy()`, `analizuj_warstwę()` |
| **Budowa sieci neuronowych** | 9200-10300 | `podziel_dane()`, `buduj_siec()` |

### 2.2 Kluczowe funkcje

#### Funkcje przetwarzania danych
- `oblicz_cechy_3kursy_rozszerzone(bloki)` - wylicza 30+ cech z bloków kursów
- `przetworz_plik_3kursy_rozszerzone(nazwa_pliku, nazwa_wyjsciowa)` - główna funkcja przetwarzająca
- `classify_odds(odds)` - klasyfikuje kursy na 20 poziomów
- `process_and_save_data(input_file, output_file)` - przetwarza i zapisuje sklasyfikowane dane

#### Funkcje statystyczne
- `poisson(k, lam)` - rozkład Poissona
- `dixon_coles(home_goals, away_goals, home_attack, away_attack, ...)` - model Dixon-Coles
- `policz_dc(row)` - liczy parametry modelu DC

#### Funkcje pomocnicze
- `normalize(value, min_val, max_val)` - normalizacja wartości
- `bezpieczny_log(value)` - bezpieczna funkcja logarytmiczna
- `liczba(x)` - konwersja na float
- `rozbij_wynik(x)` - parsowanie wyniku meczu

---

## 3. IDENTYFIKACJA PUNKTÓW WEJŚCIA/WYJŚCIA

### 3.1 Punkty wejścia (Input Hooks)

#### Poziom 1: Wejście główne
**Lokalizacja:** Linia 428-454 (sekcja START)
```python
# ================================
# START
# ================================

pliki = [
    ("./dane/database_popularne_dzisiaj.csv", "./dane/dataBase_futbol_popularne_trend.csv"),
    ("./dane/database_dzisiaj.csv", "./dane/dataBase_futbol_trend.csv")
]

for plik_in, plik_out in pliki:
    przetworz_plik_3kursy_rozszerzone(plik_in, plik_out)
```

**Zalecenie:** Dodać hook przed pętlą, aby agent mógł:
- Dodać własne pliki do przetwarzania
- Zmodyfikować listę plików
- Przekazać własne dane zamiast plików

#### Poziom 2: Przetwarzanie pojedynczego pliku
**Lokalizacja:** Linia 257-420 (funkcja `przetworz_plik_3kursy_rozszerzone`)
```python
def przetworz_plik_3kursy_rozszerzone(nazwa_pliku, nazwa_wyjsciowa):
    # Odczyt pliku i przetwarzanie
```

**Zalecenie:** Dodać hook na początku funkcji, aby agent mógł:
- Przekazać dane bezpośrednio (zamiast odczytu z pliku)
- Zmodyfikować parametry przetwarzania

#### Poziom 3: Ekstrakcja cech
**Lokalizacja:** Linia 37-256 (funkcja `oblicz_cechy_3kursy_rozszerzone`)
```python
def oblicz_cechy_3kursy_rozszerzone(bloki):
    # Obliczanie 30+ cech z bloków kursów
```

**Zalecenie:** Dodać hook na początku i końcu, aby agent mógł:
- Dodać własne cechy
- Zmodyfikować obliczone cechy
- Monitorować proces ekstrakcji

#### Poziom 4: Klasyfikacja kursów
**Lokalizacja:** Linia 1099-1206 (funkcja `classify_odds`)
```python
def classify_odds(odds):
    # Klasyfikacja kursów na 20 poziomów
```

**Zalecenie:** Dodać hook, aby agent mógł:
- Zmienić algorytm klasyfikacji
- Dodać własne kategorie

### 3.2 Punkty wyjścia (Output Hooks)

#### Poziom 1: Wyniki przetwarzania pliku
**Lokalizacja:** Koniec funkcji `przetworz_plik_3kursy_rozszerzone` (linia 420)
**Zalecenie:** Dodać hook zwracający:
- Statystyki przetwarzania
- Zapisane dane
- Czas wykonania

#### Poziom 2: Wyniki ekstrakcji cech
**Lokalizacja:** Koniec funkcji `oblicz_cechy_3kursy_rozszerzone` (linia 256)
**Zalecenie:** Dodać hook zwracający:
- Obliczone cechy
- Statystyki bloków

#### Poziom 3: Wyniki klasyfikacji
**Lokalizacja:** Koniec funkcji `classify_odds` (linia 1206)
**Zalecenie:** Dodać hook zwracający:
- Rozkład klasyfikacji
- Statystyki poziomów

---

## 4. PROPOZYCJA LOKALIZACJI HOOKÓW

### 4.1 Hooki główne (Poziom Modułu)

| Hook | Lokalizacja | Typ | cel |
|------|-------------|-----|-----|
| `SSI_AGENT_HOOK_MODULE_START` | Linia 1-10 (początek pliku) | START | Inicjalizacja modułu, rejestracja agentów |
| `SSI_AGENT_HOOK_MODULE_END` | Koniec pliku | END | Zakończenie modułu, zwolnienie zasobów |

### 4.2 Hooki przetwarzania (Poziom Procesu)

| Hook | Lokalizacja | Typ | cel |
|------|-------------|-----|-----|
| `SSI_AGENT_HOOK_PROCESS_START` | Linia 428 (przed pętlą główną) | START | Rozpoczęcie przetwarzania wsadowego |
| `SSI_AGENT_HOOK_FILE_PROCESS_START` | Linia 257 (początek `przetworz_plik_3kursy_rozszerzone`) | START | Rozpoczęcie przetwarzania pojedynczego pliku |
| `SSI_AGENT_HOOK_FILE_PROCESS_END` | Linia 420 (koniec `przetworz_plik_3kursy_rozszerzone`) | END | Zakończenie przetwarzania pliku |
| `SSI_AGENT_HOOK_PROCESS_END` | Linia 454 (koniec pętli głównej) | END | Zakończenie przetwarzania wsadowego |

### 4.3 Hooki ekstrakcji cech (Poziom Analizy)

| Hook | Lokalizacja | Typ | cel |
|------|-------------|-----|-----|
| `SSI_AGENT_HOOK_FEATURE_EXTRACTION_START` | Linia 37 (początek `oblicz_cechy_3kursy_rozszerzone`) | START | Rozpoczęcie ekstrakcji cech |
| `SSI_AGENT_HOOK_FEATURE_CALCULATION` | W środku funkcji (np. linia 60-70) | MID | Monitorowanie obliczeń cech |
| `SSI_AGENT_HOOK_FEATURE_EXTRACTION_END` | Linia 256 (koniec `oblicz_cechy_3kursy_rozszerzone`) | END | Zakończenie ekstrakcji cech |

### 4.4 Hooki klasyfikacji (Poziom Decyzji)

| Hook | Lokalizacja | Typ | cel |
|------|-------------|-----|-----|
| `SSI_AGENT_HOOK_CLASSIFY_START` | Linia 1099 (początek `classify_odds`) | START | Rozpoczęcie klasyfikacji |
| `SSI_AGENT_HOOK_CLASSIFY_END` | Linia 1206 (koniec `classify_odds`) | END | Zakończenie klasyfikacji |

### 4.5 Hooki statystyczne (Poziom Modelu)

| Hook | Lokalizacja | Typ | cel |
|------|-------------|-----|-----|
| `SSI_AGENT_HOOK_STATISTICAL_ANALYSIS_START` | Linia 6053 (początek `analizuj_plik`) | START | Rozpoczęcie analizy statystycznej |
| `SSI_AGENT_HOOK_CORRELATION_CALC` | Linia 6053 (w medio `policz_korelacje`) | MID | Monitorowanie obliczeń korelacji |
| `SSI_AGENT_HOOK_STATISTICAL_ANALYSIS_END` | Koniec `analizuj_plik` | END | Zakończenie analizy |

### 4.6 Hooki sieci neuronowych (Poziom UCzenia)

| Hook | Lokalizacja | Typ | cel |
|------|-------------|-----|-----|
| `SSI_AGENT_HOOK_NN_TRAINING_START` | Linia 9213 (początek `podziel_dane`) | START | Rozpoczęcie podziału danych |
| `SSI_AGENT_HOOK_NN_BUILD_START` | Linia 9282 (początek `buduj_siec`) | START | Rozpoczęcie budowy sieci |
| `SSI_AGENT_HOOK_NN_TRAINING_END` | Koniec `buduj_siec` | END | Zakończenie budowy sieci |

---

## 5. PROPOZYCJA ZMIENNYCH GLOBALNYCH

### 5.1 Rejestr statusu procesu
```python
SSI_STAGE_STATUS = {
    "engine": "generatorDataBaseTrendAnalisAll",
    "part": "czesc1",
    "stage": "",
    "status": "",
    "timestamp": "",
    "agent_input": None,
    " agent_output": None,
    "processing_stats": {},
    "errors": []
}
```

### 5.2 Punkty wejścia dla agentów
```python
# Globalne punkty wejścia
SSI_AGENT_INPUT = {
    "files_to_process": None,        # Agent może dodać własne pliki
    "custom_data": None,             # Agent może przekazać własne dane
    "analysis_params": None,         # Parametry analizy od agenta
    "observations": None,            # Dodatkowe obserwacje od agenta
    "research_task": None            # Zadanie badawcze od agenta
}
```

### 5.3 Punkty wyjścia dla agentów
```python
# Globalne punkty wyjścia
SSI_AGENT_OUTPUT = {
    "results": None,                 # Wyniki dla agenta
    "analyses": None,                # Analizy dla agenta
    "memory_updates": None,          # Aktualizacje pamięci
    "diagnostics": None,             # Informacje diagnostyczne
    "processing_time": None          # Czas przetwarzania
}
```

---

## 6. IMPLEMENTACJA - KROKI

### 6.1 Krok 1: Dodanie globalnych zmiennych (Linie 1-20)
Dodać na początku pliku:
- `SSI_STAGE_STATUS`
- `SSI_AGENT_INPUT`
- `SSI_AGENT_OUTPUT`
- Import obiektu `datetime` dla timestampów

### 6.2 Krok 2: Dodanie hooków modułu (Linie 1-10 i koniec pliku)
Dodać:
- `SSI_AGENT_HOOK_MODULE_START` na początku
- `SSI_AGENT_HOOK_MODULE_END` na końcu

### 6.3 Krok 3: Dodanie hooków przetwarzania (Sekcja START)
Dodać:
- `SSI_AGENT_HOOK_PROCESS_START` przed pętlą główną
- `SSI_AGENT_HOOK_PROCESS_END` po pętli głównej

### 6.4 Krok 4: Dodanie hooków w kluczowych funkcjach
Dodać w każdej głównych funkcjach:
- Hook START na początku
- Hook END na końcu
- Aktualizację `SSI_STAGE_STATUS`

### 6.5 Krok 5: Dodanie mechanizmu kawałkowania (Chunking)
Dodać możliwość przetwarzania w części:
- `SSI_CHUNK_SIZE = 1000` - domyślny rozmiar kawałka
- Funkcje do przetwarzania pojedynczego chunk'a

---

## 7. PRZYKŁADOWA IMPLEMENTACJA HOOKA

```python
# Na początku pliku
def update_stage_status(stage, status, timestamp=None):
    import datetime
    SSI_STAGE_STATUS["stage"] = stage
    SSI_STAGE_STATUS["status"] = status
    SSI_STAGE_STATUS["timestamp"] = str(datetime.datetime.now()) if timestamp is None else timestamp

# W funkcji przetworz_plik_3kursy_rozszerzone:
def przetworz_plik_3kursy_rozszerzone(nazwa_pliku, nazwa_wyjsciowa):
    # SSI_AGENT_HOOK_START
    update_stage_status("file_processing", "start")
    
    if SSI_AGENT_INPUT.get("custom_data"):
        # Agent dostarczył własne dane - użyj ich
        bloki = SSI_AGENT_INPUT["custom_data"]
    else:
        # Standardowy odczyt z pliku
        # ... istniejący kod ...
    
    # ... reszta kodu ...
    
    # SSI_AGENT_HOOK_END
    update_stage_status("file_processing", "end")
    
    if SSI_AGENT_OUTPUT.get("results") is None:
        SSI_AGENT_OUTPUT["results"] = []
    SSI_AGENT_OUTPUT["results"].append({"file": nazwa_pliku, "output": nazwa_wyjsciowa})
```

---

## 8. PODSUMOWANIE ZMIAN

### 8.1 Nowe zmienne globalne
1. `SSI_STAGE_STATUS` - rejestr statusu
2. `SSI_AGENT_INPUT` - punkty wejścia
3. `SSI_AGENT_OUTPUT` - punkty wyjścia
4. `SSI_CHUNK_SIZE` - rozmiar kawałka (opcjonalnie)

### 8.2 Nowe funkcje
1. `update_stage_status(stage, status, timestamp=None)` - aktualizacja statusu
2. (Opcjonalnie) `register_agent_input(data)` - rejestracja wejścia od agenta

### 8.3 Modyfikowane funkcje (dodanie hooków)
1. `przetworz_plik_3kursy_rozszerzone`
2. `oblicz_cechy_3kursy_rozszerzone`
3. `classify_odds`
4. `process_and_save_data`
5. `analizuj_plik`
6. `podziel_dane`
7. `buduj_siec`

### 8.4 Liczba hooków do dodania
- **Hooki START/END:** ~14 par (28 punktów)
- **Znaczniki komentarzy:** ~28
- **Aktualizacje statusu:** ~14

---

## 9. PRIORYTETY IMPLEMENTACJI

### 9.1 Wysoki priorytet (muszą zostać zaimplementowane)
1. Globalne zmienne rejestru i punktów wejścia/wyjścia
2. Hooki modułu (START/END)
3. Hooki głównego przetwarzania (sekcja START)
4. Hooki principalnych funkcji przetwarzających

### 9.2 Średni priorytet (polecane)
1. Hooki ekstrakcji cech
2. Hooki klasyfikacji
3. Hooki statystyczne

### 9.3 Niski priorytet (opcjonalne)
1. Hooki sieci neuronowych
2. Mechanizm kawałkowania

---

## 10. TESTOWANIE

Po implementacji należy przetestować:
1. Czy silnik działa tak samo jak przed modyfikacjami
2. Czy hooki są wywoływane w odpowiednich momentach
3. Czy statusy są poprawnie aktualizowane
4. Czy agenci mogą przekazywać dane przez punkty wejścia
5. Czy agenci mogą odbierać wyniki przez punkty wyjścia

---

**Status:** ANALIZA ZAKOŃCZONA  
**Następny krok:** Implementacja hooków w czesc1.py