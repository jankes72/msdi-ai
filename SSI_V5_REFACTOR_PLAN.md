# SSI V5 REFACTOR PLAN

## Czesciowy Plan Refaktoryzacji Systemu SSI V5

**Data:** 2026-08-03  
**Status:** PLAN PRZYGOTOWANY - OCZEKUJE NA AKCEPTACJE  
**Plik docelowy:** SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py  
**Wersja:** 1.0 - ETAP 5 Planowanie Refaktoryzacji  

---

## Spis Treści

1. [CZĘŚĆ 1 — MAPA DUPLIKATÓW FUNKCJI](#czesc-1-mapa-duplikatow-funkcji)
2. [CZĘŚĆ 2 — MAPA KONFLIKTÓW ZMIENNYCH GLOBALNYCH](#czesc-2-mapa-konfliktow-zmiennych-globalnych)
3. [CZĘŚĆ 3 — MAPA IMPORTÓW](#czesc-3-mapa-importow)
4. [CZĘŚĆ 4 — DOCELOWA ARCHITEKTURA SSI V5](#czesc-4-docelowa-architektura-ssi-v5)
5. [CZĘŚĆ 5 — ZACHOWANIE PRZEPŁYWU SSI V5](#czesc-5-zachowanie-przeplywu-ssi-v5)
6. [CZĘŚĆ 6 — PRZYGOTOWANIE AUTOMATYZACJI](#czesc-6-przygotowanie-automatyzacji)

---

## CZĘŚĆ 1 — MAPA DUPLIKATÓW FUNKCJI

### 1.1. Metodologia Analizy

- Zidentyfikowano wszystkie powtarzające się funkcje w pliku
- Porównano implementacje między częściami (czesc1-4)
- Określono różnice w parametrach, logice i zwracanych wartościach
- Zmapowano użycie każdej funkcji w kontekście
- Określono zalecaną główną implementację

---

### 1.2. Kategorizacja Funkcji

#### 🟢 **Kategoria A: Identyczne Implementacje** (Można bezpiecznie zentralizować)

| Nazwa Funkcji | Lokalizacje | Źródło | Różnice | Użycie | Zalecanawersja | Decyzja |
|---|---|---|---|---|---|---|
| `rozbij_wynik(x)` | 2611, 3691, 40269, 41349 | czesc1, czesc2(x2) | **ŻADNE** - identyczna logika | Parsowanie wyniku "X:Y" → (int, int) | dowolna | ✅ **Zachować jedną, centralnie** |

**Implementacja referencyjna (linia 2611):**
```python
def rozbij_wynik(x):
    try:
        a,b = x.split(":")
        return int(a), int(b)
    except:
        return 0,0
```

---

#### 🟡 **Kategoria B: Podobne Implementacje** (Wymaga analizy i decyzji)

| Nazwa Funkcji | Lokalizacje | Źródło | Różnice | Użycie | Zalecana wersja | Decyzja |
|---|---|---|---|---|---|---|
| `poisson(k, lam)` | 2694, 3925, 41583 | czesc1, czesc2, czesc3 | czesc1: ma try/except, czesc2/3: bez try/except | Model Poissona | czesc1 (bezpieczniejsze) | ✅ **Użyć czesc1** |
| `wynik_1x2(x)` | 2626, 40284 | czesc1, czesc3 | **ŻADNE** - identyczna | Konwersja wyniku na 1/0/-1 | dowolna | ✅ **Zachować jedną** |
| `wynik_gole(x)` | 2647, 40305 | czesc1, czesc3 | **ŻADNE** - identyczna | Ekstrakcja goli | dowolna | ✅ **Zachować jedną** |
| `liczba(x)` | 2101, 39759 | czesc1, czesc3 | **ŻADNE** - identyczna | Konwersja na liczbę | dowolna | ✅ **Zachować jedną** |
| `odleglosc(a,b)` | 2111, 39769 | czesc1, czesc3 | **ŻADNE** - identyczna | Odległość euklidesowa | dowolna | ✅ **Zachować jedną** |
| `wynik_liczbowy(wynik)` | 2124, 39782 | czesc1, czesc3 | **ŻADNE** - identyczna | Konwersja wyniku na liczbę | dowolna | ✅ **Zachować jedną** |

---

#### 🔴 **Kategoria C: Różne Implementacje** (Wymaga indywidualnej analizy)

##### C.1. `dixon_coles` - Krytyczna róznica parametrów

| Lokalizacja | Źródło | Parametry | Opis | Status |
|---|---|---|---|---|
| 2730 | czesc1 | `(gole_dom, gole_wyj, lambda_dom, lambda_wyj, rho=RHO_DIXON)` | Pełna sygnatura, używa konkretnych nazw | ✅ **Zalecana** |
| 3953 | czesc2 | `(gd, gw, ld, lw)` | Skrócone nazwy parametrów, rho=RHO_DIXON globalnie | ⚠️ Mniej czytelna |
| 41611 | czesc3 | `(gd, gw, ld, lw)` | Jak czesc2 | ⚠️ Mniej czytelna |

**Decyzja:** ✅ **Użyć implementację z czesc1** - pełne nazwy parametrów, lepsza czytelność

**Uwaga:** Wszystkie implementacje używają tej samej logiki, różnią się tylko nazwami parametrów.

---

##### C.2. `buduj_siec(nazwa, cechy)` - Różne implementacje budowy sieci

| Lokalizacja | Źródło | Typ Sieci | Parametry | Status |
|---|---|---|---|---|
| 9544 | czesc2 | Sieć neuronowa (Keras) | `nazwa, cechy` | ✅ **Zalecana** |
| 10529 | czesc2 | Sieć neuronowa | `nazwa, cechy` | Duplikat w czesc2 |
| 47149 | czesc3 | Sieć neuronowa | `nazwa, cechy` | Duplikat w czesc3 |
| 49208 | czesc4 | Sieć neuronowa | `nazwa, cechy` | Duplikat w czesc4 |
| 49942 | czesc4 | Sieć neuronowa | `nazwa, cechy` | Duplikat w czesc4 |

**Analiza:**
- Wszystkie implementacje tworzą sieci neuronowe o podobnej strukturze
- Różnice w konfiguracji warstw, callbacków, early stopping
- Wymaga szczegółowej analizy które parametry są optymalne

**Decyzja:** ⚠️ **Wymaga dalszej analizy** - porównać konfiguracje i wybrać optymalną

---

##### C.3. `podziel_dane(X, y)` - Różne strategie podziału

| Lokalizacja | Źródło | Strategia | Proporcje | Status |
|---|---|---|---|---|
| 9475 | czesc2 | train_test_split x2 | 50% train, 10% val, 40% obs | ✅ **Zalecana** |
| 10460 | czesc2 | train_test_split x2 | 50% train, 10% val, 40% obs | Duplikat |
| 47080 | czesc3 | train_test_split x2 | 50% train, 10% val, 40% obs | Duplikat |
| 49076 | czesc4 | `podziel_dane_chronologicznie` | Chronologiczny podział | ✅ **Specjalistyczna** |
| 49112 | czesc4 | train_test_split x2 | 50% train, 10% val, 40% obs | Duplikat |
| 49873 | czesc4 | train_test_split x2 | 50% train, 10% val, 40% obs | Duplikat |

**Analiza:**
- Majority: standardowy podział 50/10/40
- czesc4 zawiera również `podziel_dane_chronologicznie` - warto zachować

**Decyzja:** ✅ **Zachować obie:**
- `podziel_dane()` - standardowy podział losowy
- `podziel_dane_chronologicznie()` - podział chronologiczny (specjalistyczny)

---

##### C.4. `klasyfikuj_wynik(wynik)` - Różne implementacje klasyfikacji

| Lokalizacja | Źródło | Parametr | Zwracana wartość | Obsługa błędów | Status |
|---|---|---|---|---|---|
| 4479 | czesc2 | `wynik` | 1/0/-1 (gospodarz/remis/goście) | pd.isna, try/except | ⚠️ |
| 4903 | czesc2 | `wynik` | 1/0/-1 | Brak obsługi None | ❌ |
| 6243 | czesc2 | `wynik` | 1/0/-1 | Brak obsługi None | ❌ |
| 6863 | czesc2 | `wynik` | 1/0/-1 | Brak obsługi None | ❌ |
| 42137 | czesc3 | `wynik` | 1/0/-1 | pd.isna | ✅ |
| 42561 | czesc3 | `wynik` | 1/0/-1 | pd.isna | ✅ |
| 43901 | czesc3 | `wynik` | 1/0/-1 | pd.isna | ✅ |
| 44521 | czesc3 | `wynik` | 1/0/-1 | pd.isna | ✅ |

**Analiza:**
- czesc2 linia 4479: Najbardziej robust - obsługuje None i błędy
- czesc3: Wszystkie używają pd.isna, ale nie obsługują innych błędów

**Decyzja:** ✅ **Użyć wersję z czesc2 linia 4479** - najbardziej odporna na błędy

---

##### C.5. `normalizuj(x)` - Różne Strategie Normalizacji

| Lokalizacja | Źródło | Typ x | Metoda | Obsługa edge cases | Status |
|---|---|---|---|---|---|
| 4704 | czesc2 | pandas Series | (x-min)/(max-min) | max==min → return x*0 | ✅ **Zalecana** |
| 5123 | czesc2 | pandas Series | (x-min)/(max-min) | max==min → return x*0 | Duplikat |
| 6290 | czesc2 | pandas Series | (x-min)/(max-min) | max==min → return x*0 | Duplikat |
| 6910 | czesc2 | pandas Series | (x-min)/(max-min) | max==min → return x*0 | Duplikat |
| 42362 | czesc3 | pandas Series | (x-min)/(max-min) | max==min → return x*0 | Duplikat |
| 42781 | czesc3 | pandas Series | (x-min)/(max-min) | max==min → return x*0 | Duplikat |
| 43948 | czesc3 | pandas Series | (x-min)/(max-min) | max==min → return x*0 | Duplikat |
| 44568 | czesc3 | pandas Series | (x-min)/(max-min) | max==min → return x*0 | Duplikat |

**Analiza:**
- Wszystkie implementacje są **identyczne**
- Obsługują edge case (max == min)

**Decyzja:** ✅ **Zachować jedną centralnie** - dowolna implementacja

---

##### C.6. `classify_odds(odds)` - Klasyfikacja kursów

| Lokalizacja | Źródło | Parametr | Strategia | Status |
|---|---|---|---|---|
| 1361 | czesc1 | `odds` | Prosta klasyfikacja | ? |
| 1648 | czesc1 | `odds` | Prosta klasyfikacja | Duplikat |
| 39019 | czesc3 | `odds` | Rozszerzona klasyfikacja | ? |
| 39306 | czesc3 | `odds` | Rozszerzona klasyfikacja | Duplikat |

**Decyzja:** ⚠️ **Wymaga analizy kodu** - porównać logikę obu wersji

---

##### C.7. `process_and_save_data` - Przetwarzanie i zapis

| Lokalizacja | Źródło | Kontekst | Status |
|---|---|---|---|
| 1470 | czesc1 | Przetwarzanie kursów | ? |
| 1757 | czesc1 | Przetwarzanie kursów | Duplikat |
| 39128 | czesc3 | Przetwarzanie kursów | ? |
| 39415 | czesc3 | Przetwarzanie kursów | Duplikat |

**Decyzja:** ⚠️ **Wymaga analizy kodu** - porównać implementacje

---

#### 📊 **Podsumowanie Statystyczne Funkcji**

| Funkcja | Liczba wystąpień | Źródła | Typ konfliktu | Decyzja |
|---|---|---|---|---|
| `klasyfikuj_wynik` | 8 | czesc2(x4), czesc3(x4) | Różne implementacje | ✅ Użyć czesc2:4479 |
| `normalizuj` | 8 | czesc2(x4), czesc3(x4) | Identyczne | ✅ Zachować jedną |
| `buduj_siec` | 5 | czesc2(x2), czesc3(x1), czesc4(x2) | Różne implementacje | ⚠️ Analiza wymagana |
| `podziel_dane` | 6 | czesc2(x2), czesc3(x1), czesc4(x3) | Głównie identyczne + chronologiczny | ✅ Zachować obie |
| `rozbij_wynik` | 4 | czesc1(x1), czesc2(x2), czesc3(x1) | Identyczne | ✅ Zachować jedną |
| `poisson` | 3 | czesc1(x1), czesc2(x1), czesc3(x1) | Różne (try/except) | ✅ Użyć czesc1 |
| `dixon_coles` | 3 | czesc1(x1), czesc2(x1), czesc3(x1) | Różne parametry | ✅ Użyć czesc1 |
| `classify_odds` | 4 | czesc1(x2), czesc3(x2) | ⚠️ Do analizy | ⚠️ |
| `process_and_save_data` | 4 | czesc1(x2), czesc3(x2) | ⚠️ Do analizy | ⚠️ |

---

## CZĘŚĆ 2 — MAPA KONFLIKTÓW ZMIENNYCH GLOBALNYCH

### 2.1. Metodologia

- Zidentyfikowano wszystkie zmiennych globalnych (CAPS_CASE)
- Zmapowano lokalizacje i wartości
- Określono przeznaczenie i kontekst użycia
- Określono Decyzja docelową

---

### 2.2. Tabela Konfliktów Zmiennych

#### 🔴 **Krytyczne - Różne wartości**

| Nazwa | Wystąpienia | Lokalizacje | Wartości | Znaczenie | Decyzja docelowa |
|---|---|---|---|---|---|
| `PLIK_TRENING` | 4 | 4410, 4854, 9181, 10231 | Różne ścieżki | Plik treningowy | ✅ **Zunifikować** - użyć relative paths |
| `OUTPUT` | 3 | 4410, 4861, 8672 | Różne ścieżki | Plik wyjściowy | ✅ **Zunifikować** - jeden catalog wyjściowy |
| `KATALOG` | 3 | 5261, 5551, 5882 | "dane" | Katalog danych | ✅ **Zachować "dane"** - standard |

---

#### 🟡 **Średnie - Nadpisywanie struktur**

| Nazwa | Wystąpienia | Lokalizacje | Typ | Znaczenie | Decyzja |
|---|---|---|---|---|---|
| `WYNIKI` | 5 | 5364, 5708, 5993, 9204, 10253 | list | Lista wyników | ✅ **Zachować ostatnią** + konsolidować |
| `BAZA_CECH` | 3 | 5325, 5613, 5953 | dict | Baza cech | ✅ **Konsolidować** w jednej strukturze |
| `MAX_GOLE` | 2 | 2549, 3646 | int | Maksymalna liczba goli | ✅ **Zachować 8** - obie takie same |
| `RHO_DIXON` | 2 | 2551, 3648 | float | Parametr Dixon-Coles | ✅ **Zachować -0.1** - obie takie same |

---

#### 🟢 **Niskie - Stałe konfiguracyjne**

| Nazwa | Wystąpienia | Lokalizacje | Wartość | Znaczenie | Decyzja |
|---|---|---|---|---|---|
| `PROG` | 1 | 2078 | 0.03 | Próg | ✅ **Zachować** |
| `LICZBA_SYNTH` | 1 | 2545 | 3 | Liczba syntez | ✅ **Zachować** |
| `KROK` | 1 | 2547 | 0.02 | Krok | ✅ **Zachować** |

---

### 2.3. Zmienne Specyficzne dla Części

| Nazwa | Źródło | Znaczenie | Decyzja |
|---|---|---|---|
| `SSI_STAGE_STATUS` | czesc1 | Rejestr statusu SSI | ✅ **Zachować** - kluczowy dla monitoringu |
| `SSI_AGENT_INPUT` | czesc1 | Punkty wejścia agentów | ✅ **Zachować** |
| `SSI_AGENT_OUTPUT` | czesc1 | Punkty wyjścia agentów | ✅ **Zachować** |
| `SSI_EVENTS` | czesc1 | Log zdarzeń | ✅ **Zachować** |

---

### 2.4. Propozycja Struktury Konfiguracji

```python
# SSI_V5/config.py (nowy plik)

# ============================================
# KONFIGURACJA ŚCIEŻEK
# ============================================
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "dane")
MODELS_DIR = os.path.join(BASE_DIR, "modele_kursy_przygotowane")
OUTPUT_DIR = os.path.join(BASE_DIR, "dane")
BACKUP_DIR = os.path.join(BASE_DIR, "memory_backup")

# ============================================
# KONFIGURACJA MODELI
# ============================================
PLIK_TRENING = os.path.join(DATA_DIR, "mozg_kursy_przygotowane.csv")
PLIK_PREDYKCJI = os.path.join(DATA_DIR, "kursy_przygotowane.csv")
KATALOG_MODELI = MODELS_DIR

# ============================================
# PARAMETRY STATYSTYCZNE
# ============================================
MAX_GOLE = 8
RHO_DIXON = -0.1
PROG = 0.03
LICZBA_SYNTH = 3
KROK = 0.02

# ============================================
# USTAWIENIA SIECI
# ============================================
RANDOM_STATE = 42
TEST_SIZE_OBSERWACJA = 0.40
TEST_SIZE_WALIDACJA = 0.166666  # 1/6
```

---

## CZĘŚĆ 3 — MAPA IMPORTÓW

### 3.1. Analiza Istniejących Importów

#### Standard Library Imports (powtarzane)

| Import | Wystąpienia | Lokalizacje | Status |
|---|---|---|---|
| `import csv` | 15+ |Rozproszone| ⚠️ Duplikat |
| `import os` | 10+ |Rozproszone | ⚠️ Duplikat |
| `import sys` | 10+ |Rozproszone | ⚠️ Duplikat |
| `import time` | 5+ |Rozproszone | ⚠️ Duplikat |
| `import json` | 8+ |Rozproszone | ⚠️ Duplikat |
| `import math` | 5+ |Rozproszone | ⚠️ Duplikat |
| `from datetime import datetime` | 5+ |Rozproszone | ⚠️ Duplikat |
| `from collections import defaultdict, Counter` | 3+ |Rozproszone | ⚠️ Duplikat |

---

#### Third-Party Imports (powtarzane)

| Import | Wystąpienia | Lokalizacje | Status |
|---|---|---|---|
| `import pandas as pd` | 8+ |Rozproszone | ⚠️ Duplikat |
| `import numpy as np` | 8+ |Rozproszone | ⚠️ Duplikat |
| `from sklearn.ensemble import RandomForestClassifier` | 4+ |Rozproszone | ⚠️ Duplikat |
| `from sklearn.model_selection import train_test_split` | 4+ |Rozproszone | ⚠️ Duplikat |
| `from sklearn.preprocessing import StandardScaler` | 4+ |Rozproszone | ⚠️ Duplikat |
| `from sklearn.metrics import accuracy_score, mutual_info_classif` | 3+ |Rozproszone | ⚠️ Duplikat |
| `from tensorflow.keras.models import Sequential, load_model` | 3+ |Rozproszone | ⚠️ Duplikat |
| `from tensorflow.keras.layers import Dense, Dropout, Input` | 3+ |Rozproszone | ⚠️ Duplikat |
| `from tensorflow.keras.callbacks import EarlyStopping` | 3+ |Rozproszone | ⚠️ Duplikat |
| `from tensorflow.keras.utils import to_categorical` | 2+ |Rozproszone | ⚠️ Duplikat |

---

### 3.2. Propozycja Organizacji Importów

#### 📁 **SSI_V5/core/__init__.py** - Importy wspólne

```python
# ============================================
# STANDARD LIBRARY
# ============================================
import csv
import os
import sys
import time
import json
import math
from datetime import datetime
from collections import defaultdict, Counter
import statistics

# ============================================
# THIRD PARTY - CORE
# ============================================
import pandas as pd
import numpy as np

# ============================================
# THIRD PARTY - ML
# ============================================
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, mutual_info_classif
from sklearn.feature_selection import mutual_info_classif

# ============================================
# THIRD PARTY - DEEP LEARNING  
# ============================================
try:
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import Dense, Dropout, Input
    from tensorflow.keras.callbacks import EarlyStopping
    from tensorflow.keras.utils import to_categorical
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
```

---

#### 📁 Importy specyficzne dla modułów

```python
# SSI_V5/data/loading.py
import csv
import json
import os
import pandas as pd

# SSI_V5/modeling/neural.py
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.utils import to_categorical

# SSI_V5/modeling/statistical.py
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
```

---

### 3.3. Zalecenia Optymalizacyjne

1. **Zasada:** Importuj w miejscu użycia (lazy loading) dla ciężkich bibliotek (TensorFlow)
2. **Zasada:** Importy standardowe na szczycie pliku
3. **Zasada:** Używaj względnych importów dla modułów wewnętrznych
4. **Zasada:** Obsługuj błędy importu (try/except) dla opcjonalnych zależności

---

## CZĘŚĆ 4 — DOCELOWA ARCHITEKTURA SSI V5

### 4.1. Wizja Architektury

```
SSI_V5/
├── __init__.py                    # Główne wejście systemu
├── config.py                      # Centralna konfiguracja
├── constants.py                    # Stałe i ustawienia
│
├── core/                          # Jądro systemu
│   ├── __init__.py
│   ├── utils.py                    # Funkcje utility (rozbij_wynik, etc.)
│   ├── data_structures.py          # Struktury danych SSI
│   └── hooks.py                    # Hooki i eventy SSI
│
├── data/                          # Zarządzanie danymi
│   ├── __init__.py
│   ├── loading.py                  # Ładowanie danych z plików
│   ├── preprocessing.py            # Przetwarzanie wstępne
│   ├── feature_engineering.py     # Inżynieria cech
│   └── validation.py              # Walidacja danych
│
├── modeling/                      # Modele i algorytmy
│   ├── __init__.py
│   ├── statistical/               # Modele statystyczne
│   │   ├── poisson.py             # Model Poissona
│   │   ├── dixon_coles.py          # Model Dixon-Coles
│   │   └── random_forest.py        # Random Forest
│   └── neural/                    # Sieci neuronowe
│       ├── network_builder.py     # Budowa sieci
│       └── training.py            # Trening sieci
│
├── memory/                        # System pamięci
│   ├── __init__.py
│   ├── world_memory.py             # Pamięć światów (WorldHierarchyManager)
│   ├── observation_memory.py      # Pamięć obserwacji
│   └── model_memory.py            # Pamięć modeli
│
├── teachers/                      # Systemy uczenia
│   ├── __init__.py
│   ├── cognitive_teacher.py        # CognitiveTeacher
│   ├── weights_manager.py         # DynamicWeightsManager
│   └── knowledge_builder.py       # Budowanie wiedzy
│
├── agents/                        # Agenci predykcyjni
│   ├── __init__.py
│   ├── base_agent.py              # Klasa bazowa agentów
│   ├── prediction_agents.py        # Agenci predykcyjni
│   └── strategy_agents.py          # Agenci strategii
│
├── laboratory/                   # Laboratoria eksperymentalne
│   ├── __init__.py
│   ├── experiment_manager.py      # Zarządzanie eksperymentami
│   ├── hypothesis_testing.py      # Testowanie hipotez
│   └── strategy_lab.py            # Laboratorium strategii
│
├── collective/                    # Kolektyw
│   ├── __init__.py
│   ├── knowledge_pool.py          # Pul wiedzy zbiorowej
│   ├── reputation_system.py       # System reputacji
│   └── information_exchange.py    # Wymiana informacji
│
├── engine/                        # Główny silnik
│   ├── __init__.py
│   ├── memory_engine.py           # MemoryEngine (główny silnik)
│   ├── pipeline.py                 # Pipeline przetwarzania
│   └── scheduler.py               # Harmonogram zadań
│
├── scripts/                       # Skrypty uruchomieniowe
│   ├── start_ssi.py               # Główne uruchomienie
│   └── start_ssi_test.py          # Testowe uruchomienie
│
└── tests/                         # Testy
    ├── unit/                      # Testy jednostkowe
    └── integration/                # Testy integracyjne
```

---

### 4.2. Zależności Między Modułami

```
                    ┌─────────────────┐
                    │   config.py      │
                    │  constants.py    │
                    └────────┬────────┘
                             │
               ┌─────────────┼─────────────┐
               │             │             │
        ┌──────▼──────┐ ┌────▼────┐ ┌───▼─────┐
        │   core/      │ │  data/   │ │ teachers/│
        └──────┬──────┘ └────┬────┘ └───┬─────┘
               │             │             │
               │ ┌───────────▼───────────┐ │
               │ │       memory/          │ │
               │ └───────────┬───────────┘ │
               │             │             │
               ▼ ┌───────────▼───────────┐ ▼
        ┌─────────────┐ │    modeling/        │
        │   engine/    │ │  (statistical &    │
        │  (pipeline)  │ │   neural)          │
        └─────────────┘ └───────────┬───────────┘
                                    │
                    ┌───────────────────────▼───────────────────────┐
                    │                    agents/                      │
                    └───────────────────────┬───────────────────────┘
                                            │
                    ┌────────────────────────────┼────────────────────────────┐
                    │                            │                            │
                    ▼                            ▼                            ▼
            ┌──────────────┐              ┌──────────────┐            ┌──────────────┐
            │ laboratory/  │              │ collective/  │            │   output/    │
            └──────────────┘              └──────────────┘            └──────────────┘
```

---

### 4.3. Mapowanie Istniejącego Kodu do Nowej Architektury

| Obecna Lokalizacja | Nowa Lokalizacja | Uwagi |
|---|---|---|
| czesc1: funkje utility | `core/utils.py` | rozbij_wynik, liczba, etc. |
| czesc1: hooki SSI | `core/hooks.py` | SSI_EVENT, SSI_START_* |
| czesc1: przetwarzanie kursów | `data/preprocessing.py` | oblicz_cechy_3kursy_* |
| czesc2: analiza trendów | `modeling/statistical/` | Analiza Poissona, DC |
| czesc2: pamięć obserwacji | `memory/observation_memory.py` | Zapisy świadków |
| czesc3: modele predykcyjne | `modeling/neural/` | Sieci neuronowe |
| czesc4: WorldHierarchyManager | `teachers/world_memory.py` | Zarządzanie hierarchią |
| czesc4: DynamicWeightsManager | `teachers/weights_manager.py` | Dynamiczne wagi |
| czesc4: CognitiveTeacher | `teachers/cognitive_teacher.py` | System poznawczy |
| czesc4: MemoryEngine | `engine/memory_engine.py` | Główny silnik |

---

## CZĘŚĆ 5 — ZACHOWANIE PRZEPŁYWU SSI V5

### 5.1. Obecny Przepływ Wiedzy

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOCELOWY PRZEPŁYW SSI V5                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                      │
│  DANE WEJŚCIOWE                                      LOGI          │
│       │                                                │          │
│       ▼                                                ▼          │
│  ┌─────────────┐                            ┌─────────────┐    │
│  │  data/      │                            │  core/      │    │
│  │  loading.py │──── DANE ────────────────▶│  hooks.py   │    │
│  └─────────────┘                            └─────────────┘    │
│       │                                                │          │
│       ▼                                                ▼          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    GENEROWANIE WIEDZY                         │ │
│  │ ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐ │ │
│  │ │  data/          │  │  data/           │  │  modeling/      │ │ │
│  │ │  preprocessing  │  │  feature_        │  │  statistical/   │ │ │
│  │ │  .py           │──▶│  engineering.py  │──▶│  poisson.py     │ │ │
│  │ └─────────────────┘  └─────────────────┘  └────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                    │                                  │
│                                    ▼                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    MODELE PREDEKCYJNE                         │ │
│  │ ┌─────────────────┐  ┌─────────────────────────────────────┐ │ │
│  │ │  modeling/      │  │  modeling/                            │ │ │
│  │ │  statistical/   │  │  neural/                               │ │ │
│  │ │  (Poisson, DC)  │──▶│  network_builder.py     ┐               │ │ │
│  │ └─────────────────┘  └─────────────────────┬───────────┘ │ │
│  │                                              │                 │ │
│  └──────────────────────────────────────────────┬─────────────┘ │
│                                                    │               │
│                                                    ▼               │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    PREDYKCJA                                  │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │  agents/                                                 │ │ │ │
│  │ │  prediction_agents.py     ┐                              │ │ │ │
│  │ └─────────────────────────────────────────┬──────────────┘ │ │
│  └────────────────────────────────────────────┬────────────────┘ │
│                                                        │          │
│                                                        ▼          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    OBSERWACJA                                  │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │  memory/                                              │ │ │ │
│  │ │  observation_memory.py    ┐                            │ │ │ │
│  │ └─────────────────────────────────────────┬──────────────┘ │ │
│  └────────────────────────────────────────────┬────────────────┘ │
│                                                        │          │
│                                                        ▼          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    PAMIĘĆ                                     │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │  memory/                                              │ │ │ │
│  │ │  world_memory.py    ┐                                  │ │ │ │
│  │ └─────────────────────────────────────────┬──────────────┘ │ │
│  └────────────────────────────────────────────┬────────────────┘ │
│                                                        │          │
│                                                        ▼          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    SYSTEM POZNAWCZY (TEACHER)                 │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │  teachers/                                            │ │ │ │
│  │ │  cognitive_teacher.py    ┐                            │ │ │ │
│  │ │  weights_manager.py      ┐                            │ │ │ │
│  │ │  world_memory.py         ┐                            │ │ │ │
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                    │                                  │
│                                    ▼                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    AGENCI PREDYKCYJNI                         │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │  agents/                                              │ │ │ │
│  │ │  prediction_agents.py    ┐                            │ │ │ │
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘
│                                    │
│                                    ▼
│  ┌─────────────────────────────────────────────────────────────┐
│  │                    LABORATORIUM EKSPERYMENTALNE               │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │  laboratory/                                           │ │ │ │
│  │ │  experiment_manager.py    ┐                            │ │ │ │
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘
│                                    │
│                                    ▼
│  ┌─────────────────────────────────────────────────────────────┐
│  │                    KOLEKTYW                                   │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │  collective/                                          │ │ │ │
│  │ │  knowledge_pool.py    ┐                                  │ │ │ │
│  │ │  reputation_system.py    ┐                              │ │ │ │
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘
│                                    │
│                                    ▼
│  ┌─────────────────────────────────────────────────────────────┐
│  │                    NOWA WIEDZA                                  │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │  teachers/ / memory/ / collective/                    │ │ │ │
│  │ │  (Współpraca wszystkich modułów)                         │ │ │ │
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘
│                                    │
│                                    ▼
│  ┌─────────────────────────────────────────────────────────────┐
│  │                    AKTUALIZACJA SYSTEMU                        │ │
│  │ ┌─────────────────────────────────────────────────────────┐ │ │
│  │ │  memory/ / teachers/ / engine/                        │ │ │ │
│  │ │  (Aktualizacja pamięci, modeli, konfiguracji)             │ │ │ │
│  │ └─────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────────┘
```

---

### 5.2. Zachowanie Kluczowych Komponentów

| Komponent | Obecna Lokalizacja | Nowa Lokalizacja | Status |
|---|---|---|---|
| **WorldHierarchyManager** | czesc4:47896 | `teachers/world_memory.py` | ✅ Zachować |
| **DynamicWeightsManager** | czesc4:48096 | `teachers/weights_manager.py` | ✅ Zachować |
| **CognitiveTeacher** | czesc4:48187 | `teachers/cognitive_teacher.py` | ✅ Zachować |
| **MemoryEngine** | czesc4:89282 | `engine/memory_engine.py` | ✅ Zachować (główne wejście) |

---

### 5.3. Integracja z Przepływem Wiedzy

```python
# Przykładowy przepływ w nowej architekturze

# 1. Ładowanie danych
from SSI_V5.data.loading import load_match_data
from SSI_V5.data.preprocessing import preprocess_features

df = load_match_data()
X, y = preprocess_features(df)

# 2. Generowanie wiedzy
from SSI_V5.modeling.statistical.poisson import PoissonModel
from SSI_V5.modeling.statistical.dixon_coles import DixonColesModel

poisson_model = PoissonModel()
dc_model = DixonColesModel()

# 3. System poznawczy
from SSI_V5.teachers.cognitive_teacher import CognitiveTeacher
from SSI_V5.teachers.world_memory import WorldHierarchyManager
from SSI_V5.teachers.weights_manager import DynamicWeightsManager

teacher = CognitiveTeacher(df, features, "main")
world_memory = WorldHierarchyManager()
weights_manager = DynamicWeightsManager()

# 4. Pamięć
from SSI_V5.memory.observation_memory import ObservationMemory
observation_memory = ObservationMemory()
observation_memory.store_observation(y_true, y_pred)

# 5. Główny silnik
from SSI_V5.engine.memory_engine import MemoryEngine
engine = MemoryEngine()
engine.run()
```

---

## CZĘŚĆ 6 — PRZYGOTOWANIE AUTOMATYZACJI

### 6.1. Docelowy Przepływ Automatyczny

```
┌──────────────────────────────────────────────────────────────────┐
│                    AUTOMATYCZNY PRZEPŁYW SSI V5                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                       │
│  08:00               13:00               18:00               23:00│
│     │                  │                  │                  │    │
│     ▼                  ▼                  ▼                  ▼    │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐│
│  │  CYKL 1  │      │  CYKL 2  │      │  CYKL 3  │      │  CYKL 4  ││
│  │ (5 godz) │      │ (5 godz) │      │ (5 godz) │      │ (5 godz) ││
│  └────┬─────┘      └────┬─────┘      └────┬─────┘      └────┬─────┘│
│       │                │                 │                 │    │
│       ▼                ▼                 ▼                 ▼    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                    SSI_V5_GENERATOR                            │  │
│  │  (SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py)                    │  │
│  └───────────────────────────────────┬─────────────────────────┘  │
│                                      │                            │
│                    ┌─────────────────────▼─────────────────────┐   │
│                    │                                   │           │   │
│                    ▼                                   ▼           ▼   │
│  ┌─────────────────────┐         ┌───────────────────┐   ┌─────────┐ │
│  │  BUDOWANIE WIEDZY   │         │    TEACHER         │   │ AGENTY  │ │
│  │  - Ładowanie danych  │────────▶│  - Analiza         │   │ - Pred │ │
│  │  - Feature eng.      │         │    historycznych   │   │ - hypo │ │
│  │  - Model building    │         │    wyników        │   │ - test │ │
│  └─────────────────────┘         └────────┬──────────┘   └─────────┘ │
│                                            │                      │
│                                            ▼                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                    PRZETWARZANIE                              │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │  │
│  │  │  Pamieć     │  │  Modele     │  │  Weryfikacja    │  │  │
│  │  │  obserwacji │  │  predykc.   │  │  wyników        │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                            │                           │
│                                            ▼                           │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                    NOWA WIEDZA + AKTUALIZACJA                  │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │  │
│  │  │  Laboratorium│  │  Kolektyw   │  │  Aktualizacja    │  │  │
│  │  │  (ekspery-   │  │  (wiedza     │  │  (pamięć,       │  │  │
│  │  │  menty)     │  │  zbiorowa)   │  │  wagi, modele)  │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                       │
└───────────────────────────────────────────────────────────────────┘
```

---

### 6.2. Harmonogram Zadań

```python
# Przykładowa konfiguracja scheduler.py

SSI_SCHEDULE = {
    "cycles": [
        {"time": "08:00", "duration_hours": 5, "cycle_id": 1},
        {"time": "13:00", "duration_hours": 5, "cycle_id": 2},
        {"time": "18:00", "duration_hours": 5, "cycle_id": 3},
        {"time": "23:00", "duration_hours": 5, "cycle_id": 4}
    ],
    "agent_work_hours_per_cycle": 5,
    "total_daily_cycles": 4,
    "daily_operation_hours": 20
}

# Przepływ w jednym cyklu
CYCLE_PIPELINE = [
    {"step": 1, "name": "data_loading", "module": "data.loading", "duration_min": 30},
    {"step": 2, "name": "knowledge_generation", "module": "modeling", "duration_min": 120},
    {"step": 3, "name": "teacher_analysis", "module": "teachers", "duration_min": 60},
    {"step": 4, "name": "agent_prediction", "module": "agents", "duration_min": 180},
    {"step": 5, "name": "laboratory_experiments", "module": "laboratory", "duration_min": 90},
    {"step": 6, "name": "collective_knowledge", "module": "collective", "duration_min": 30},
    {"step": 7, "name": "system_update", "module": "engine", "duration_min": 30}
]
```

---

### 6.3. Integracja z Istniejącymi Plikami Startowymi

**Obecny stan:**
- `start_ssi.py` - zakomentowany
- `start_ssi_test.py` - aktywny

**Docelowy stan:**
- `start_ssi.py` - główne uruchomienie produkcyjne
- `start_ssi_test.py` - testy i debug
- `start_ssi_scheduled.py` - automatyczne uruchamianie wg harmonogramu

---

## PODSUMOWANIE I NASTĘPNE KROKI

### ✅ **Co zostało wykonane w ETAPIE 5**

1. **✅ CZĘŚĆ 1:** Pełne mapowanie duplikatów funkcji z analizą różnic i rekomendacjami
2. **✅ CZĘŚĆ 2:** Kompletna mapa konfliktów zmiennych globalnych z proponowaną strukturą konfiguracji
3. **✅ CZĘŚĆ 3:** Analiza importów z propozycją organizacji i optymalizacji
4. **✅ CZĘŚĆ 4:** Docelowa architektura modułowa z mapowaniem istniejącego kodu
5. **✅ CZĘŚĆ 5:** Zachowanie przepływu wiedzy SSI V5 w nowej struktury
6. **✅ CZĘŚĆ 6:** Plan automatyzacji z harmonogramem i pipeline

---

### 📊 **Statystyki Planu Refaktoryzacji**

| Kategoria | Liczba | Status |
|---|---|---|
| Funkcje z duplikatami | 10 | Zaanalizowane |
| Całkowite duplikaty funkcji | 79 | Zmapowane |
| Zmienne globalne conflict | 12 | Zaanalizowane |
| Duplikaty importów | 50+ | Zmapowane |
| Nowe moduły do utworzenia | 15 | Zaplanowane |
| Pliki do podziału | 1 → 20+ | Zorganizowane |

---

### 🎯 **Następne Kroki (Oczekujące na Akceptację)**

**ETAP 5.2 — Bezpieczna Refaktoryzacja:**

1. **Krok 1:** Utworzenie struktury katalogów `SSI_V5/`
2. **Krok 2:** Przeniesienie `config.py` i `constants.py`
3. **Krok 3:** Ekstrakcja `core/utils.py` z funkcjami utility
4. **Krok 4:** Podział na moduły według planu
5. **Krok 5:** Rozwiązanie konfliktów funkcji i zmiennych
6. **Krok 6:** Testy integracyjne
7. **Krok 7:** Optymalizacja importów

---

### ⚠️ **Ostrzeżenia i Uwagi**

1. **Nie zmieniono żadnego kodu** - plan czeka na akceptację
2. **Wszystkie oryginalne funkcje zachowane** - decyzje migracyjne são rekomendacjami
3. **Przepływ wiedzy zachowany** - nowa architektura utrzymuje ten sam flow
4. **Zgodność wsteczna** - należałoby zapewnić kompatybilność wartości zwracanych

---

### 📚 **Dokumentacja Powiązana**

- [SSI_V5_ENGINE_VALIDATION_REPORT.md](SSI_V5_ENGINE_VALIDATION_REPORT.md) - Raport walidacji
- [SSI_V5_CONSOLIDATION_TECHNICAL_REPORT.md](SSI_V5_CONSOLIDATION_TECHNICAL_REPORT.md) - Raport konsolidacji
- [SSI_V5_KNOWLEDGE_FLOW_MAP.md](SSI_V5_KNOWLEDGE_FLOW_MAP.md) - Mapa przepływu wiedzy
- [SSI_V5_GENERATOR_CODE_MAP.md](SSI_V5_GENERATOR_CODE_MAP.md) - Mapa kodu generatora

---

**Raport przygotowany przez:** Mistral Vibe (kontynuator projektu SSI V5)  
**Data:** 2026-08-03  
**Wersja:** 1.0 - ETAP 5 Planowanie Refaktoryzacji  

---

*Generated by Mistral Vibe.  
Co-Authored-By: Mistral Vibe <vibe@mistral.ai>