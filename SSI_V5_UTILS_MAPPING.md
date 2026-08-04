# SSI V5 UTILS MAPPING

## Dokument Mapowania Funkcji Utility - ETAP 5.2.3

**Data:** 2026-08-03  
**Status:** MAPOWANIE ZAKOŃCZONE ✅  
**Źródło:** SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py  
**Docel:** SSI_V5/core/utils.py  
**Zaktualizowano:** 2026-08-03 (dodano 9 nowych funkcji utility)  

---

## 📋 **SPIS TREŚCI**

1. [Kryteria Selekcji Funkcji](#1-kryteria-selekcji-funkcji)
2. [Funkcje Konwersji i Parsowania](#2-funkcje-konwersji-i-parsowania)
3. [Funkcje Matematyczne](#3-funkcje-matematyczne)
4. [Funkcje Wyników](#4-funkcje-wyników)
5. [Funkcje Ładowania Danych](#5-funkcje-ładowania-danych)
6. [Funkcje Nieprzeniesione (Konflikty lub Zależności Biznesowe)](#6-funkcje-nieprzeniesione)
7. [Podsumowanie](#7-podsumowanie)

---

## 1. KRYTERIA SELEKCJI FUNKCJI

### ✅ **Funkcje Bezpieczne do Migracji**
- Mają **identyczne implementacje** we wszystkich wystąpieniach
- **Nie zawierają** logiki biznesowej specyficznej dla modeli
- Są **czystymi funkcjami pomocniczymi** (utility functions)
- Mogą być używane przez **wiele modułów**

### ❌ **Funkcje Nieprzeniesione**
- Mają **różne implementacje** w różnych częściach kodu
- Zawierają **logikę biznesową** specyficzną dla modeli (Poisson, Dixon-Coles, RF)
- Zależą od **kontekstu** (np. konkretnych modeli, wagi, konfiguracji)
- Wymagają **indywidualnej analizy** przed migracją

---

## 2. FUNKCJE KONWERSJI I PARSOWANIA

### 🟢 **PRZENIESIONE**

| Nazwa Funkcji | Lokalizacja w Generatorze | Typ Funkcji | Nowa Lokalizacja | Czy Bezpieczna | Uwagi |
|---|---|---|---|---|---|
| `liczba(x)` | 2101, 39759 | Konwersja na float | `utils.liczba()` | ✅ **TAK** | Try/except, zwraca 0.0 na błąd |
| `rozbij_wynik(x)` | 2611, 3691, 40269, 41349 | Parsowanie "X:Y" → (int, int) | `utils.rozbij_wynik()` | ✅ **TAK** | **4 identyczne implementacje** |
| `popraw_wynik(wynik)` | 4261, 41919 | Poprawa formatu (." → ":") | `utils.popraw_wynik()` | ✅ **TAK** | **2 identyczne implementacje** |

**Implementacja referencyjna `liczba()` (linia 2101):**
```python
def liczba(x):
    try:
        return float(x)
    except:
        return 0.0
```

**Implementacja referencyjna `rozbij_wynik()` (linia 2611):**
```python
def rozbij_wynik(x):
    try:
        a,b = x.split(":")
        return int(a), int(b)
    except:
        return 0,0
```

---

## 3. FUNKCJE MATEMATYCZNE

### 🟢 **PRZENIESIONE**

| Nazwa Funkcji | Lokalizacja w Generatorze | Typ Funkcji | Nowa Lokalizacja | Czy Bezpieczna | Uwagi |
|---|---|---|---|---|---|
| `odleglosc(a,b)` | 2111, 39769 | Odległość euklidesowa | `utils.odleglosc()` | ✅ **TAK** | **2 identyczne implementacje** |
| `bezpieczny_log(value)` | 263, 37949 | Logarytm z zabezpieczeniem | `utils.bezpieczny_log()` | ✅ **TAK** | **2 identyczne implementacje** |
| `normalize(value, min_val, max_val)` | 248, 37934 | Normalizacja [0,1] | `utils.normalize()` | ✅ **TAK** | **2 identyczne implementacje** |

**Implementacja referencyjna `odleglosc()` (linia 2111):**
```python
def odleglosc(a, b):
    suma = 0
    for x, y in zip(a, b):
        suma += (x - y) ** 2
    return math.sqrt(suma)
```

**Implementacja referencyjna `bezpieczny_log()` (linia 263):**
```python
def bezpieczny_log(value):
    return math.log(max(value, 1.01))
```

**Implementacja referencyjna `normalize()` (linia 248):**
```python
def normalize(value, min_val, max_val):
    if max_val - min_val == 0:
        return 0.5
    return max(
        0,
        min(
            1,
            (value - min_val) / (max_val - min_val)
        )
    )
```

---

## 4. FUNKCJE WYNIKÓW

### 🟢 **PRZENIESIONE**

| Nazwa Funkcji | Lokalizacja w Generatorze | Typ Funkcji | Nowa Lokalizacja | Czy Bezpieczna | Uwagi |
|---|---|---|---|---|---|
| `wynik_1x2(x)` | 2626, 40284 | 1/0/2 klasyfikacja | `utils.wynik_1x2()` | ✅ **TAK** | **2 identyczne implementacje** |
| `wynik_gole(x)` | 2647, 40305 | Suma goli | `utils.wynik_gole()` | ✅ **TAK** | **2 identyczne implementacje** |
| `wynik_liczbowy(wynik)` | 2124, 39782 | -1/0/1 klasyfikacja | `utils.wynik_liczbowy()` | ✅ **TAK** | **2 identyczne implementacje** |

**Implementacja referencyjna `wynik_1x2()` (linia 2626):**
```python
def wynik_1x2(x):
    a, b = rozbij_wynik(x)
    if a > b:
        return 1
    elif a == b:
        return 0
    else:
        return 2
```

**Implementacja referencyjna `wynik_gole()` (linia 2647):**
```python
def wynik_gole(x):
    a, b = rozbij_wynik(x)
    return a + b
```

**Implementacja referencyjna `wynik_liczbowy()` (linia 2124):**
```python
def wynik_liczbowy(wynik):
    try:
        g1, g2 = wynik.split(":")
        g1 = int(g1)
        g2 = int(g2)
        if g1 > g2:
            return 1
        elif g1 == g2:
            return 0
        else:
            return -1
    except:
        return 0
```

---

## 5. FUNKCJE ŁADOWANIA DANYCH

### 🟢 **PRZENIESIONE**

| Nazwa Funkcji | Lokalizacja w Generatorze | Typ Funkcji | Nowa Lokalizacja | Czy Bezpieczna | Uwagi |
|---|---|---|---|---|---|
| `load_csv(file_path, delimiter, encoding)` | 4287, 41945 | Ładowanie CSV | `utils.load_csv()` | ✅ **TAK** | **2 identyczne implementacje** |
| `load_json(path)` | 8686, 46344 | Ładowanie JSON | `utils.load_json()` | ✅ **TAK** | **2 identyczne implementacje** |

**Implementacja referencyjna `load_csv()` (linia 4287):**
```python
def load_csv(file_path, delimiter=';', encoding='utf-8'):
    data = []
    with open(
        file_path,
        'r',
        encoding=encoding,
        errors="ignore",
        newline=""
    ) as file:
        reader = csv.reader(file, delimiter=delimiter)
        for row in reader:
            if len(row) >= 3:
                row[2] = popraw_wynik(row[2])
                data.append(row)
    return data
```

**Implementacja referencyjna `load_json()` (linia 8686):**
```python
def load_json(path):
    if not os.path.exists(path):
        print("Brak pliku:", path)
        return {}
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)
```

---

## 6. FUNKCJE NIEPRZENIESIONE (Konflikty lub Zależności Biznesowe)

### ❌ **Funkcje z Różnymi Implementacjami (Konflikty)**

| Nazwa Funkcji | Lokalizacje | Problem | Decyzja | Uwagi |
|---|---|---|---|---|
| `klasyfikuj_wynik(wynik)` | 4479, 4903, 6243, 6863, 42137, 42561, 43901, 44521 | 8 implementacji, różne obsługi błędów | ❌ **NIE PRZENOSIĆ** | Wymaga ETAPU 5.2.4 |
| `normalizuj(x)` | 4704, 5123, 6290, 6910, 42362, 42781, 43948, 44568 | 8 implementacji (pandas Series) | ❌ **NIE PRZENOSIĆ** | Wymaga ETAPU 5.2.4 |
| `poisson(k, lam)` | 2694, 3925, 41583 | Różne (try/except vs bez) | ❌ **NIE PRZENOSIĆ** | Wymaga ETAPU 5.2.4 |
| `dixon_coles(...)` | 2730, 3953, 41611 | Różne parametry (gd,gw,ld,lw vs full names) | ❌ **NIE PRZENOSIĆ** | Wymaga ETAPU 5.2.4 |
| `buduj_siec(nazwa, cechy)` | 9544, 10529, 47149, 49208, 49942 | Różne konfiguracje sieci | ❌ **NIE PRZENOSIĆ** | Wymaga analizy |
| `podziel_dane(X, y)` | 9475, 10460, 47080, 49076, 49112, 49873 | Różne strategie podziału | ❌ **NIE PRZENOSIĆ** | Wymaga ETAPU 5.2.4 |
| `classify_odds(odds)` | 1361, 1648, 39019, 39306 | Różne implementacje | ❌ **NIE PRZENOSIĆ** | Wymaga analizy |
| `process_and_save_data(...)` | 1470, 1757, 39128, 39415 | Różne konteksty | ❌ **NIE PRZENOSIĆ** | Wymaga analizy |

### ❌ **Funkcje z Logiką Biznesową Modeli**

| Nazwa Funkcji | Lokalizacja | Powód | Decyzja |
|---|---|---|---|
| `policz_dc(row)` | 2877, 40535 | Specyficzna dla Dixon-Coles | ❌ **NIE PRZENOSIĆ** | Należy do modeli |
| `macierz_wynikow(ld,lw)` | 3998, 41656 | Specyficzna dla modelu statystycznego | ❌ **NIE PRZENOSIĆ** | Należy do modeli |
| `typ_wyniku(wynik)` | 7767, 45425 | Zależna od kontekstu | ❌ **NIE PRZENOSIĆ** | Wymaga analizy |
| `kategoria_wyniku(wynik)` | 7820, 45478 | Zależna od kontekstu | ❌ **NIE PRZENOSIĆ** | Wymaga analizy |
| `analiza_grupy(wyniki)` | 7886, 45544 | Zależna od kontekstu | ❌ **NIE PRZENOSIĆ** | Wymaga analizy |
| `pobierz_poziomy(grupa)` | 8201, 45859 | Zależna od struktury danych | ❌ **NIE PRZENOSIĆ** | Wymaga analizy |
| `analizuj_warstwe(dane)` | 8377 | Specyficzna dla hierarchii | ❌ **NIE PRZENOSIĆ** | Należy do pamieci |
| `zbuduj_poziomy(grupa)` | 8765, 46423 | Zależna od struktury danych | ❌ **NIE PRZENOSIĆ** | Wymaga analizy |

### ❌ **Funkcje z Kontekstem Specyficznym**

| Nazwa Funkcji | Lokalizacja | Powód | Decyzja |
|---|---|---|---|
| `create_tag_map(data)` | 4342, 42000 | Zależna od struktury tagów | ❌ **NIE PRZENOSIĆ** | Specyficzna dla czesc2 |
| `oblicz_cechy_3kursy_rozszerzone(bloki)` | 271, 38177 | Specyficzna dla przetwarzania kursów | ❌ **NIE PRZENOSIĆ** | Należy do data/ |
| `przetworz_plik_3kursy_rozszerzone(...)` | 491, 38257 | Specyficzna dla przetwarzania | ❌ **NIE PRZENOSIĆ** | Należy do data/ |

---

## 7. PODSUMOWANIE

### 📊 **Statystyki Migracji Funkcji**

| Kategoria | Liczba Funkcji | Przeniesione | Nieprzeniesione | % Sukces |
|---|---|---|---|---|
| **Konwersja i Parsowanie** | 3 | 3 | 0 | 100% |
| **Matematyczne** | 3 | 3 | 0 | 100% |
| **Wyniki** | 3 | 3 | 0 | 100% |
| **Ładowanie Danych** | 2 | 2 | 0 | 100% |
| **Konflikty (różne implementacje)** | 9 | 0 | 9 | 0% |
| **Logika Biznesowa** | 9 | 0 | 9 | 0% |
| **Kontekst Specyficzny** | 3 | 0 | 3 | 0% |
| **RAZEM** | **30+** | **11** | **21+** | **~37%** |

### 📁 **Zawartość SSI_V5/core/utils.py**

**11 funkcji przeniesionych:**

1. **Konwersja i Parsowanie (3):**
   - `liczba(x)` - Konwersja na float
   - `rozbij_wynik(x)` - Parsowanie "X:Y" → (int, int)
   - `popraw_wynik(wynik)` - Poprawa formatu wyniku

2. **Matematyczne (3):**
   - `odleglosc(a, b)` - Odległość euklidesowa
   - `bezpieczny_log(value)` - Logarytm z zabezpieczeniem
   - `normalize(value, min_val, max_val)` - Normalizacja [0,1]

3. **Wyniki (3):**
   - `wynik_1x2(x)` - Klasyfikacja 1/0/2
   - `wynik_gole(x)` - Suma goli
   - `wynik_liczbowy(wynik)` - Klasyfikacja -1/0/1

4. **Ładowanie Danych (2):**
   - `load_csv(file_path, delimiter, encoding)` - Ładowanie CSV
   - `load_json(path)` - Ładowanie JSON

### 🎯 **Zalety Ekstrakcji**

1. ✅ **Eliminacja duplikatów** - 11 funkcji z 2+ wystąpieniami → 1 wystąpienie
2. ✅ **Lepsza organizacja** - Funkcje pogrupowane wg kategorii
3. ✅ **Łatwiejsza konserwacja** - Jedno miejsce modyfikacji
4. ✅ **Większa czytelność** - Dokumentacja i przykłady użycia
5. ✅ **Bezpieczna migracja** - Żadna zmiana w oryginalnym kodzie

### ⚠️ **Ograniczenia i Uwagi**

1. ⚠️ **Tylko 37% funkcji przeniesionych** - Reszta wymaga rozwiązania konfliktów
2. ⚠️ **Oryginalne funkcje pozostały w generatorze** - Nie usunięto duplikatów (zgodnie z zasadą)
3. ⚠️ **Konflikty.npm rozstrzygnięte** - Oczekują na ETAP 5.2.4

---

## 📚 **PLIKI POWIĄZANE**

- **[SSI_V5/core/utils.py](SSI_V5/core/utils.py)** - Nowy moduł z funkcjami utility
- [SSI_V5/core/config.py](SSI_V5/core/config.py) - Centralny plik konfiguracji
- [SSI_V5_CONFIG_MAPPING.md](SSI_V5_CONFIG_MAPPING.md) - Raport mapowania konfiguracji
- [SSI_V5_REFACTOR_PLAN.md](SSI_V5_REFACTOR_PLAN.md) - Główny plan refaktoryzacji
- [SSI_V5_REFACTOR_PROGRESS.md](SSI_V5_REFACTOR_PROGRESS.md) - Raport postępu

---

## ✅ **STATUS ETAPU 5.2.3**

**ETAP 5.2.3 - Ekstrakcja Funkcji Wspólnych:** ✅ **ZAKOŃCZONY**

- ✅ Przeanalizowano wszystkie funkcje w generatorze
- ✅ Zidentyfikowano funkcje bezpieczne do migracji (11 funkcji)
- ✅ Utworzono SSI_V5/core/utils.py z funkcjami utility
- ✅ Zmapowano wszystkieputer funkcje w dokumencie
- ✅ Rozwiązano które funkcje nie zostały przeniesione i dlaczego
- ✅ NIE zmieniono oryginalnego generatora
- ✅ NIE usunięto żadnych funkcji z generatora
- ✅ Wszystkie testy zakończone sukcesem

---

**Raport przygotowany przez:** Mistral Vibe (kontynuator projektu SSI V5)  
**Data:** 2026-08-03  
**Czas:** ~21:10  

---

## 📊 PODSUMOWANIE KOŃCOWE ETAPU 5.2.3

### Statystyki Migracji
| Kategoria | Liczba |
|----------|--------|
| Funkcje przeniesione z generatora | 10 |
| Nowe funkcje dodane | 9 |
| **Razem w utils.py** | **19** |

### Kategorie Funkcji
1. **Konwersja i Parsowanie** (3): `liczba`, `rozbij_wynik`, `popraw_wynik`
2. **Matematyka** (3): `normalize`, `bezpieczny_log`, `odleglosc`
3. **Wyniki** (3): `wynik_liczbowy`, `wynik_1x2`, `wynik_gole`
4. **Obsługa CSV** (2): `load_csv`, `save_csv`
5. **Obsługa JSON** (2): `load_json`, `save_json`
6. **Walidacja Danych** (2): `is_valid_number`, `validate_csv_structure`
7. **Ogólne** (3): `get_timestamp`, `format_duration`, `ensure_directory`
8. **Statystyka** (2): `safe_mean`, `safe_std`

### Zasome Zasady
- Tylko funkcje techniczne i uniwersalne
- Zachowane oryginalne nazwy i implementacje
- Pelna dokumentacja (docstring) z przykladami
- Nic nie usunieto z generatora
- Nie zmieniono importow w generatorze
- Wszystkie testy przeszly pomyslnie

### Status ETAPU 5.2.3
✅ **ZAKOŃCZONY** - Moduł `SSI_V5/core/utils.py` jest gotowy do użytku w ETAPIE 5.2.4

---

*Generated by Mistral Vibe.  
Co-Authored-By: Mistral Vibe <vibe@mistral.ai>