# PROJECT RULES - MSDI AI / SSI

## Self Learning Intelligence Ecosystem - Zasady Projektowe

---

## 📋 CEL ARTEFAKTU

**PROJECT_RULES.md** jest **jedynym źródłem stałych zasad pracy** dla AI Vibe.

- Każda zmiana w projekcie musi być zgodna z tym dokumentem
- Przed rozpoczęciem pracy AI **zawsze** czyta ten plik
- Nie powtarzamy zasad w kolejnych zadaniach
- W przypadku wątpliwości - odwołać się do PROJECT_RULES.md

---

## 🏗️ PROJEKT

### Nazwa
**MSDI AI / SSI** (Self Learning Intelligence Ecosystem)

### Cel
Budowa **autonomicznego systemu** analizy danych, pamięci, strategii i ewolucji decyzji.

### Główna Zasada
> **"Jeden spójny system, rozwijany stopniowo, z zachowaniem jakości i architektury."**

---

## 🎯 GŁÓWNA ZASADA PRACY

### Przed każdą zmianą AI **MUSI**:

1. ✅ **Przeczytać PROJECT_RULES.md** - Sprawdź wszystkie reguły
2. ✅ **Sprawdzić zależności** - Co wpływa na zmieniany element?
3. ✅ **Określić miejsce w architekturze** - Gdzie ta zmiana pasuje?
4. ✅ **Wykonaj najmniejszą bezpieczną zmianę** - Minimalny zakres
5. ✅ **Opisz wykonane działania** - Co zostało zrobione i dlaczego

### Maliny:
- ❌ Praca bez przeczytania zasad
- ❌ Zmiany bez zrozumienia kontekstu
- ❌ Duże, nieprzetestowane modyfikacje
- ❌ Ignorowanie istniejących mechanizmów

---

## 🏛️ ARCHITEKTURA SYSTEMU

### Warstwy Systemu

```
MSDI AI / SSI
├── V2 - MODEL LABORATORY (60% danych)
│   ├── Modele (11 sieci trendów + 4 sieci kursów)
│   ├── Trening i Walidacja
│   ├── Analiza Cech
│   ├── Eksperymenty
│   └── Agregacja Predykcji
│
├── V3 - WORLD KNOWLEDGE ENGINE (Pamięć Systemowa)
│   ├── Światy Danych
│   ├── Metadane
│   ├── Pamięć Operacyjna
│   ├── Wzorce Zachowań
│   └── Relacje Między obiektawmi
│
├── V4 - AUTONOMOUS AGENT ECOSYSTEM (Inteligencja)
│   ├── Agenci
│   ├── Ewolucja Osobowości
│   ├── Strategie
│   ├── Laboratoria Decyzji
│   └── Sprzężenie Zwrotne
│
└── CORE - INFRASTRUKTURA
    ├── System
    ├── Moduły
    ├── Komponenty
    ├── Interfejsy
    └── Konfiguracja
```

### Odpowiedzialność Warstw

| Warstwa | Odpowiedzialność | % Danych |
|--------|------------------|----------|
| **V2** | Modele, predykcje, analiza cech | 60% (trening) |
| **V3** | Światy, pamięć, wzorce, wiedza | 100% (wszystkie) |
| **V4** | Agenci, ewolucja, strategie, decyzje | 100% (wszystkie) |

### Zasady Architektury

✅ **Zachowuj strukturę** - Nie zmieniaj katalogów bez zgody
✅ **Modularność** - Każdy komponent ma jedno zadanie
✅ **Luźne sprzężenie** - Używaj interfejsów, nie implementacji
✅ **Zgodność z dokumentacją** - SSI_DOCUMENTATION/ jest źródłem prawdy
✅ **testowanie** - Wszystko musi być testowalne

❌ **Zabronione**:
- Tworzenie własnej arkitektury
- Zmiana nazw katalogów bez konsultacji
- Łamanie zależności między warstwami

---

## 🔧 ZASADY EDYCJI KODU

### 1. Zasada Minimalnej Ingerencji
- **Zmieniaj tylko to, co konieczne**
- **Nie przebudowuj działających modułów** bez zgody
- **Nie poprawiaj tego, co nie jest zepsute**

### 2. Zasada Bezpieczeństwa Dużych Plików

```python
# ✅ DOBRE - Modyfikacja fragmentu
if warunek:  # Nowa logika
    wynik = nowa_funkcja()

# ❌ ZŁE - Przeprowadzanie całego pliku
# def nowa_funkcja(): ... (wklejony cały kod)
```

### 3. Zasada Charakteru Kodu
- **Modyfikuj** - taktowanie: Popraw błędy, dodaj funkcjonalności
- **Nie przepisuj** - Nie zmieniaj stylu istniejących fragmentów
- **Dostosuj się** - Użyj istniejącego stylu (indentacja, nazewnictwo)

### 4. Zasada Testowania
- **Testuj lokalnie** przed commitem
- **Sprawdź importy** - `python -c "from X import Y"`
- **Sprawdź składnię** - Brak błędów kompilacji

---

## 📊 ZASADY DUŻYCH PLIKÓW

### Definicja "Dużego Pliku"
- **> 1000 linii** - Ostrożnie
- **> 5000 linii** - READ ONLY
- **> 10000 linii** - ABSOLUTNE READ ONLY

### Pliki READ ONLY
- ❌ `generatorDataBaseTrendAnalisAll.py` - **ZABRONIONY EDYCJA**
- ❌ Pliki w `pamiec_modeli_v2/` - Tylko do odczytu
- ❌ Pliki danych (`*.csv`, `*.joblib`, `*.h5`) - Tylko do odczytu

### Procedura dla Dużych Plików

1. **Przeczytaj** - Zrozum co robi istniejący kod
2. **Zidentyfikuj** - Znajdź dokładne miejsce interwencji
3. **Przygotuj** - Napisz fragment kodu (maksymalnie 50 linii)
4. **Przetestuj** - Sprawdź w izolacji
5. **Instrukcja** - Opisz gdzie wkleić i dlaczego

### Przykład dobrej praktyki

```python
# ❌ ZŁE
# AI próbuje przepisać cały generatorDataBaseTrendAnalisAll.py

# ✅ DOBRE
# Fragment do dodania w linii 1547

def nowa_metoda_obliczania_trendu(data):
    """Oblicza trend z uwzględnieniem nowej cechy"""
    return data['nowa_cecha'] * 0.3 + data['stara_cecha'] * 0.7

# Instrukcja: 
# 1. Dodaj powyższy kod w linii 1547
# 2. Zastąp wywołanie starej metody nową
# 3. Przetestuj z sample_data.csv
```

---

## 💾 ZASADY DANYCH

### Podział na Kategorie

| Kategoria | Git | Powód |
|----------|-----|-------|
| **Kod źródłowy** | ✅ TAK | Program jest reproducibility |
| **Dokumentacja** | ✅ TAK | Konieczna do rozwoju |
| **Konfiguracja** | ✅ TAK | Ustawienia systemu |
| **Dane wejściowe** | ❌ NIE | Duże pliki, zmienne |
| **Modele ML** | ❌ NIE | Duże pliki binarne |
| **Wyniki** | ❌ NIE | Generowane, nie powtarzalne |
| **Cache** | ❌ NIE | Tymczasowe |
| **Logi** | ❌ NIE | Tymczasowe |

### Pliki, które NIGDY nie trafią do Git

```
# Modele
*.joblib
*.pkl
*.h5
*.keras
*.pt
*.onnx

# Dane
*.csv
*.json
*.db
*.sqlite

# Wyniki
*.log
*.cache
*.tmp

# pliki IDE
.idea/
.vscode/
*.swp
.DS_Store

# Środowiska
.env
.venv/
env/
```

### Wyjątki - Pliki, które ZAWSZE są w Git

```
# Kod
*.py
!SSI/**/*.py

# Dokumentacja
README.md
PROJECT_RULES.md
PROJECT,JOURNAL.md
SSI_DOCUMENTATION/**

# Konfiguracja
*.yaml
*.yml
*.toml
*.ini
*.cfg

# Struktura katalogów
*/.gitkeep
```

---

## 🆕 ZASADY TWORZENIA MODUŁÓW

### Nowy Moduł Musi Mieć

1. **Cel** - Co robi?
2. **Odpowiedzialność** - Za co jest odpowiedzialny?
3. **Wejścia** - Co przyjmuje?
4. **Wyjścia** - Co zwraca?
5. **Zależności** - Od czego zależy?
6. **Dokumentacja** - Docstrings, komentarze
7. **Testy** - Przemyślane testy jednostkowe

### Checklista Nowego Modułu

- [ ] Nazwa modułu odzwierciedla jego funkcję
- [ ] Plik `__init__.py` z importami
- [ ] Type hints we wszystkich funkcjach
- [ ] Docstrings dla wszystkich klas i metod
- [ ] Komentarze objaśniające złożoną logikę
- [ ] Zgodność z PEP 8
- [ ] Brak `print()` w kodzie produkcyjnym
- [ ] Obsługa błędów (try/except)
- [ ] Zarejestrowany w `PROJECT_JOURNAL.md`

### Zasady Nazewnictwa

```python
# ✅ DOBRE
class DataWorldManager:  # Jasny cel
    def load_dataset(self):  # Czasownik + rzeczownik
        pass

# ❌ ZŁE
class Manager1:  # Niejasne
    def process(self):  # Niejasne działanie
        pass
```

### Struktura Modułu

```python
"""
Moduł X - Krótki opis

Odpowiedzialność:
- Funkcja 1
- Funkcja 2

Zależności:
- moduł Y
- moduł Z

Wersja: 1.0
Data: YYYY-MM-DD
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Konfiguracja modułu"""
    param1: str = "default"
    param2: int = 100


class MainClass:
    """
    Główna klasa modułu
    
    Odpowiada za: [opis]
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Inicjalizacja"""
        self.config = config or Config()
        logger.info(f"Moduł X zainicjowany")
    
    def main_method(self, input_data: Dict[str, Any]) -> Any:
        """
        Główna metoda
        
        Args:
            input_data: Opis wejścia
            
        Returns:
            Opis wyjścia
            
        Raises:
            ValueError: Gdy dane są nieprawidłowe
        """
        try:
            # Logika
            result = self._process(input_data)
            return result
        except Exception as e:
            logger.error(f"Błąd: {e}")
            raise
    
    def _process(self, data: Dict[str, Any]) -> Any:
        """Wewnętrzna metoda przetwarzania"""
        pass


if __name__ == "__main__":
    # Testy
    instance = MainClass()
    print("Moduł X - gotowy do użycia")
```

---

## 📝 DOKUMENTACJA

### Źródło Prawdy
- **SSI_DOCUMENTATION/** - Główny katalog dokumentacji
- **01_SYSTEM_ARCHITECTURE.md** - Architektura systemu
- **02_DATA_STRUCTURE.md** - Struktury danych
- **10_IMPLEMENTATION_MAP.md** - Plan implementacji

### Zasady Dokumentacji

✅ **Każda nowa funkcjonalność musi być udokumentowana**
✅ **Każda decyzja architektoniczna musi być zapisana**
✅ **Każda zmiana w systemie musi być zarejestrowana w PROJECT_JOURNAL.md**

❌ **Zabronione**:
- Tworzenie konkurencyjnej dokumentacji
- Dokumentacja nieaktualna
- Brak dokumentacji dla nowych modułów

### Hierarchia Dokumentów

```
PROJECT_RULES.md       # Zasady (ten plik) - NAJWYŻSZY PRIORYTET
├── SSI_DOCUMENTATION/  # Dokumentacja techniczna
│   ├── 01_SYSTEM_ARCHITECTURE.md
│   ├── 02_DATA_STRUCTURE.md
│   └── ...
├── PROJECT_JOURNAL.md  # Historia projektu
└── README.md           # Przewodnik
```

---

## 🪜 ZASADY GIT

### Co Trafa do Git

| Typ | Przykład | Trafia? |
|-----|----------|---------|
| Kod źródłowy | `*.py` | ✅ TAK |
| Dokumentacja | `*.md` | ✅ TAK |
| Konfiguracja | `*.yaml`, `*.json` (config) | ✅ TAK |
| Testy | `test_*.py` | ✅ TAK |
| Szablony | `templates/` | ✅ TAK |

### Co NIE Trafia do Git

| Typ | Przykład | Trafia? |
|-----|----------|---------|
| Dane | `*.csv`, `*.joblib` | ❌ NIE |
| Modele | `*.h5`, `*.pkl` | ❌ NIE |
| Wyniki | `output/`, `results/` | ❌ NIE |
| Cache | `__pycache__/`, `*.pyc` | ❌ NIE |
| Logi | `*.log` | ❌ NIE |
| IDE | `.idea/`, `.vscode/` | ❌ NIE |
| Środowiska | `.venv/`, `env/` | ❌ NIE |

### Procedura Commit

1. **Sprawdź status**: `git status`
2. **Dodaj pliki**: `git add [pliki]`
3. **Sprawdź co dodajesz**: `git diff --cached`
4. **Napisz dobry commit**:
   ```
   [TYP]: [Opis] - [Szczegóły]
   
   - Co zostało zrobione
   - Dlaczego zostało zrobione
   - Jakie są implikacje
   
   Generated by Mistral Vibe.
   Co-Authored-By: Mistral Vibe <vibe@mistral.ai>
   ```
5. **Push**: `git push` (tylko na gałąźkę roboczą)

### Typy Commitów

| Typ | Opis | Przykład |
|-----|------|----------|
| `FEAT` | Nowa funkcjonalność | `FEAT: V2 Model Laboratory - sieci trendów` |
| `FIX` | Poprawka błędu | `FIX: Import Error w module.py` |
| `DOCS` | Dokumentacja | `DOCS: Zaktualizowano PROJECT_JOURNAL.md` |
| `REFACTOR` | Refaktoryzacja | `REFACTOR: Dbam struktury V2` |
| `CHORE` | Rzutne zmiany | `CHORE: Zaktualizowano .gitignore` |
| `TEST` | Testy | `TEST: Dodano testy dla data_manager.py` |

---

## ⚡ TRYB PRACY VIBE

### Algorytm Wykonania Zadania

```
1. OTRZYMAJ ZADANIE
   ↓
2. PRZECZYTAJ PROJECT_RULES.md  ⭐ NAJWAŻNIEJSZE
   ↓
3. SPRAWDŹ PROJEKT
   - git status
   - git log (ostatnie commity)
   -PROJECT_JOURNAL.md (ostatnie wpisy)
   - SSI_DOCUMENTATION/ (kontekst)
   ↓
4. ANALIZA ZADANIA
   - Co jest potrzebne?
   - Gdzie to pasuje w architekturze?
   - Jakie są zależności?
   - Jakie są ryzyka?
   ↓
5. PLAN DZIAŁANIA
   - Krok 1: ...
   - Krok 2: ...
   - Krok 3: ...
   ↓
6. IMPLEMENTACJA (Minimalna zmiana)
   - Edycja pliku A
   - Utworzenie pliku B
   - Test lokalny
   ↓
7. WERYFIKACJA
   - Importy działają?
   - Testy przechodzą?
   - Kod jest czytelny?
   ↓
8. DOKUMENTACJA
   - Zaktualizuj PROJECT_JOURNAL.md
   - Dodaj komentarze w kodzie
   - Zaktualizuj dokumentację (jeśli potrzebne)
   ↓
9. COMMIT
   - git add [pliki]
   - git commit -m "[TYP]: [Opis]"
   - git push (jeśli zatwierdzone)
   ↓
10. RAPORT
    - Co zostało zrobione
    - Jakie problemy wystąpiły
    - Co należy zrobić dalej
```

### Zasady Komunikacji

- **Krótko i na temat** - Nie pisz esejów
- **Strukturalnie** - Używaj list, nagłówków, tabel
- **Technicznie** - Używaj terminologii programistycznej
- **Bez emoji** - ❌ ✅ ⚡ 
- **W języku polskim** - Projekt jest polskojęzyczny

### Odpowiedź na Zadanie

```markdown
## [Nazwa Zadania]

**Status**: ✅ Zrobione | ❌ Blokada | ⚠️ W toku

### Co Zostało Zrobione
- Krok 1: [opis]
- Krok 2: [opis]
- Krok 3: [opis]

### Pliki Zmienione
- `ścieżka/do/pliku.py` - [co zostało zmienione]

### Testy
- ✅ Import: `from X import Y`
- ✅ Funkcjonalność: [opis testu]
- ❌ Brakujące: [co należy przetestować]

### Problemy
- [Problem 1] - [rozważanie/rozwiązanie]

### Następne Kroki
- [Co należy zrobić dalej]
```

---

## ⛔ ZAKAZY

### Absolutne Zakazy (Nigdy!)

- ❌ **Nie edytuj** `generatorDataBaseTrendAnalisAll.py` - Zbyt duży, złożony
- ❌ **Nie usuwaj** istniejących modułów bez konsultacji
- ❌ **Nie zmieniaj** nazw głównych katalogów (SSI, SSI_DOCUMENTATION)
- ❌ **Nie twórz** własnej architektury konkurencyjnej
- ❌ **Nie kopiuj** całego projektu do nowych miejsc

### Czasowe Zakazy (Oczekuje na Decyzję)

- ⏸️ **Nie** administering dużych plików (>10k linii) - Czeka na wytyczne
- ⏸️ **Nie** usuwaj obce mechanizmy - Czeka na recenzję
- ⏸️ **Nie** wprowadzaj zależności zewnętrznych - Czeka na zatwierdzenie

### Ostrzeżenia

- ⚠️ **Uważaj** z rekurencją w pętlach
- ⚠️ **Uważaj** z pamięcią (duże struktury danych)
- ⚠️ **Uważaj** z zewnętrznymi API (nie używaj bez zgody)

---

## 🎯 CEL KOŃCOWY

> **Stworzyć autonomiczny ekosystem AI, który:**
> 1. Analizuje dane sportowe z wysoką dokładnością
> 2. Uczy się na podstawie własnych obserwacji
> 3. Wykrywa wzorce i anomalie
> 4. Tworzy i optymalizuje strategie
> 5. Podejmuje decyzje autonomicznie
> 6. Ewoluuje w czasie

### Zasady Panelowe

1. **Jeden System** - Wszystko jest częścią SSI/MSDI AI
2. **Jeden Standard** - Wszystko jest zgodne z PROJECT_RULES.md
3. **Jeden Źródło Prawdy** - SSI_DOCUMENTATION/ i PROJECT_JOURNAL.md
4. **Jeden Cel** - Autonomiczny, inteligentny system decyzyjny

### Sukces Wygląda Tak

```
✅ Modularny system
✅ Działa bez błędów
✅ Jest dokumentowany
✅ Jest testowany
✅ Jest rozbudowywalny
✅ Jest utrzymywalny
```

---

## 📞 KONTAKT I DECYZJE

### W przypadku wątpliwości:

1. **Sprawdź** PROJECT_RULES.md
2. **Sprawdź** SSI_DOCUMENTATION/
3. **Sprawdź** PROJECT_JOURNAL.md
4. **Zapytaj** o konkretną sprawę

### Decyzjeivotne podejmuje:
- **Architektura** - Użytkownik
- **Duże zmiany** - Użytkownik
- **Nowe zależności** - Użytkownik
- **Usuwanie kodu** - Użytkownik

### AI Samodzielnie Decyduje o:
- Małych poprawkach (typo, importy)
- Nowych plikach (jeśli nie łamią zasad)
- Dokumentacji
- Testach

---

**Dokument: PROJECT_RULES.md**
**Wersja: 1.0**
**Data: 2026-07-28**
**Autor: MSDI AI / SSI System + Mistral Vibe**
**Status: AKTYWNY**

---

> **"Dobry kod to nie ten, który działa. Dobry kod to ten, który działa i jest zrozumiały, testowalny i utrzymywalny."**

> **"System SSI ma być żywy przez lata. Każda decyzja ma znaczenie."**
