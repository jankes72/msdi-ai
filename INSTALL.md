# SSI/MSDI AI - Instrukcja Instalacji

## Przewodnik tworzenia reprodukowalnego środowiska uruchomieniowego

**Wersja:** 1.0.0  
**Data:** 2026-07-28  
**Sprint:** 7.1 - Reprodukowalne środowisko uruchomieniowe  
**Priorytet:** P0

---

## Wstęp

Ten dokument zawiera **jedyną oficjalną procedurę** instalacji systemu SSI/MSDI AI z czystego checkoutu.

**Zgodnie z PROJECT_RULES.md:**
- Instalacja nie może zależeć od globalnego środowiska Python użytkownika
- Wszystkie wymagania muszą być spełnione przez lokalne .venv
- `python -m pip check` musi kończyć się kodem 0
- `import pamiec_modeli_v2.integration` musi działać bez ręcznej zmiany PYTHONPATH

---

## Wymagania Systemowe

### Wspierana wersja Python

```
Python 3.11.x (wymagany)
```

**Sprawdzenie:**
```bash
python --version
# Powinno zwrócić: Python 3.11.x
```

> **UWAGA:** System NIE jest kompatybilny z Python 3.10, 3.12, ani 2.7. Wymagane jest **dokładnie Python 3.11**.

### Wspierane systemy operacyjne

| System | Status | Uwagi |
|--------|--------|-------|
| Windows 10/11 | ✅ Pełne wsparcie | Zalecane |
| Linux (Ubuntu 22.04+) | ✅ Pełne wsparcie | Wymaga apt/dnf |
| macOS (12+) | ✅ Wsparcie | Wymaga Homebrew |

---

## Krok 1: Klonowanie Repozytorium

```bash
# Z poziomu terminala (Git Bash / CMD / PowerShell)
git clone https://github.com/msdi-ai/ssi.git
cd ssi
```

**Wynik:** Powinieneś znaleźć się w katalogu `ssi/` zawierającym pliki:
- `pyproject.toml`
- `requirements-*.txt`
- `INSTALL.md` (ten plik)
- `SSI/` (kod źródłowy)
- `pamiec_modeli_v2/` (kod źródłowy)

---

## Krok 2: Tworzenie Środowiska Wirtualnego (.venv)

### Opcja A: Korzystając z wbudowanego modułu venv (Zalecane)

```bash
# Utwórz środowisko wirtualne w katalogu .venv
python -m venv .venv
```

### Opcja B: Korzystając z virtualenv (Jeśli venv niedostępne)

```bash
# Najpierw zainstaluj virtualenv globalnie (tylko jeśli konieczne)
python -m pip install --user virtualenv

# Utwórz środowisko
python -m virtualenv .venv
```

**Wynik:** Powinien powstać katalog `.venv/` zawierający:
- `Scripts/` (Windows) lub `bin/` (Linux/macOS)
- `Lib/` (Windows) lub `lib/` (Linux/macOS)

---

## Krok 3: Aktywacja Środowiska Wirtualnego

### Windows (CMD)

```cmd
.venv\Scripts\activate
```

### Windows (PowerShell)

```powershell
.\.venv\Scripts\Activate.ps1
```

### Linux/macOS (Bash/Zsh)

```bash
source .venv/bin/activate
```

**Sprawdzenie aktywacji:**
```bash
# Powinieneś zobaczyć (.venv) na początku promptu
(.venv) $ python --version
# Powinno zwrócić: Python 3.11.x
```

---

## Krok 4: Instalacja Zależności

System używa **pyproject.toml** jako głównego źródła konfiguracji.
Dostępne są także pliki requirements-*.txt dla różnych scenariuszy.

### Opcja A: Instalacja pełna (Runtime + Dev + ML)

```bash
# Zainstaluj wszystkie zależności (produkcja + development + ML)
pip install -r requirements-runtime.txt
pip install -r requirements-dev.txt
pip install -r requirements-ml.txt
```

### Opcja B: Instalacja minimalna (Tylko Runtime)

```bash
# Tylko zależności wymagane do uruchomienia systemu
pip install -r requirements-runtime.txt
```

### Opcja C: Instalacja z pyproject.toml (Alternatywna)

```bash
# Zainstaluj pakiet w trybie editable (development mode)
pip install -e ".[dev,ml]"
```

**Czas instalacji:** ~5-15 minut (w zależności od prędkości internetu i sprzętu)

**Przestrzeń dyskowa:** ~2-4 GB (głównie TensorFlow)

---

## Krok 5: Weryfikacja Instalacji

### Test 1: Wersja Python

```bash
python --version
```

**Oczekiwany wynik:** `Python 3.11.x`

### Test 2: Sprawdzenie zależności (pip check)

```bash
python -m pip check
```

**Oczekiwany wynik:**
```
No broken requirements found.
```

**Status:** ⭐ **KRYTERIUM AKCEPTACJI** - musi zwrócić kod 0

### Test 3: Import głównych modułów

```bash
# Test importu pamiec_modeli_v2.integration
python -c "from pamiec_modeli_v2.integration import SystemPamieciV2, utworz_system; print('pamiec_modeli_v2.integration: OK')"

# Test importu SSI
python -c "from SSI.v2 import V2Integration; from SSI.v3 import V3Integration; from SSI.v4 import Agent; print('SSI modules: OK')"

# Test importu schematów
python -c "from pamiec_modeli_v2.schemas import PredykcjaLevel1, Obserwacja; print('schemas: OK')"
```

**Oczekiwany wynik:** Wszystkie komendy powinny zakończyć się bez błędów.

### Test 4: Pełna inicjalizacja systemu

```bash
# Test pełnej inicjalizacji (może zająć kilka sekund)
python -c "
from pamiec_modeli_v2.integration import utworz_system
system = utworz_system()
print(f'System zainicjalizowany: {system._zainicjalizowany}')
print(f'Agregator: {system.agregator is not None}')
print(f'Kalibrator: {system.kalibrator is not None}')
print(f'Repozytorium: {system.repozytorium is not None}')
"
```

**Oczekiwany wynik:** Wszystkie pola powinny być `True`.

---

## Krok 6: Konfiguracja Środowiska (Opcjonalne)

### Ustawienie PYTHONPATH (Jeśli importy nie działają)

Mimo że system powinien działać bez ręcznej zmiany PYTHONPATH, w niektórych przypadkach może być konieczne:

```bash
# Windows
export PYTHONPATH=%PYTHONPATH%;%cd%

#Linux/macOS
export PYTHONPATH="$PYTHONPATH:$(pwd)"
```

**UWAGA:** Jeśli importy działają (Test 3), ten krok **nie jest konieczny**.

### Konfiguracja IDE

#### PyCharm

1. Otwórz projekt `ssi/`
2. Przejdź do: `File > Settings > Project: ssi > Python Interpreter`
3. Kliknij ikonę koła zębatego > `Add Interpreter` > `Add Local Interpreter`
4. Wybierz `Existing environment`
5. W polu `Interpreter` wskaż: `.venv\Scripts\python.exe` (Windows) lub `.venv/bin/python` (Linux/macOS)
6. Kliknij OK

#### VSCode

1. Otwórz projekt w VSCode
2. Naciśnij `Ctrl+Shift+P` > `Python: Select Interpreter`
3. Wybierz: `.venv\Scripts\python.exe` (Windows) lub `.venv/bin/python` (Linux/macOS)
4. Zainstaluj rozszerzenie `Python` (Microsoft)

---

## Rozwiązywanie Problemów

### Problem 1: `python --version` zwraca nieprawidłową wersję

**Objaw:**
```
$ python --version
Python 3.10.11
```

**Rozwiązanie:**
```bash
# Zainstaluj Python 3.11 z oficjalnej strony
# https://www.python.org/downloads/

# Po instalacji, użyj pełnej ścieżki do python 3.11
C:\Python311\python.exe -m venv .venv
```

### Problem 2: `pip install` kończy się błędem TensorFlow

**Objaw:**
```
ERROR: Could not build wheels for*tensorflow*
```

**Rozwiązanie:**
```bash
# Zainstaluj Microsoft Visual C++ Build Tools
# https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Lub użyj pre-built wheels
pip install --only-binary :all: tensorflow
```

### Problem 3: ImportError: No module named 'pamiec_modeli_v2'

**Objaw:**
```
ImportError: No module named 'pamiec_modeli_v2'
```

**Rozwiązanie 1:** (Zalecane)
```bash
# Zainstaluj pakiet w trybie editable
pip install -e .
```

**Rozwiązanie 2:**
```bash
# Dodaj bieżący katalog do PYTHONPATH
export PYTHONPATH="$PYTHONPATH:$(pwd)"
# LUB (Windows)
set PYTHONPATH=%PYTHONPATH%;%cd%\n```

### Problem 4: `pip check` sygnalizuje konflikty

**Objaw:**
```
$ python -m pip check
numpy 1.24.0 has requirement python>=3.8,<3.12, but you have python 3.11.5
```

**Rozwiązanie:**
```bash
# Użyj lockfile (jeśli dostępny)
pip install -r requirements-lock.txt

# Lub zaktualizuj zależności
pip install --upgrade numpy
```

### Problem 5: Brak uprawnień do instalacji pakietów

**Objaw (Windows):**
```
ERROR: Could not install packages due to an OSError: [WinError 5] Access is denied
```

**Rozwiązanie:**
```cmd
# Uruchom PowerShell jako Administrator
# Lub zainstaluj dla bieżącego użytkownika
python -m pip install --user -r requirements-runtime.txt
```

---

## Aktualizacja Środowiska

### Aktualizacja zależności

```bash
# Zaktualizuj konkretny pakiet
pip install --upgrade numpy

# Zaktualizuj wszystkie pakiety
pip list --outdated
pip install --upgrade -r requirements-runtime.txt
```

### Reinstalacja środowiska

```bash
# Usunięcie starego środowiska
rm -rf .venv/  # Linux/macOS
del /s /q .venv  # Windows (CMD)

# Utworzenie nowego środowiska
python -m venv .venv

# Aktywacja i instalacja
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
pip install -r requirements-runtime.txt
```

---

## Generowanie Lockfile (Dla zaawansowanych użytkowników)

Aby wygenerować **deterministyczny lockfile**:

```bash
# Zainstaluj pip-tools
pip install pip-tools

# Wygeneruj requirements-lock.txt z requirements-runtime.txt
pip-compile --resolver=backtracking requirements-runtime.txt

# Wygeneruj requirements-dev-lock.txt
pip-compile --resolver=backtracking requirements-dev.txt

# Zainstaluj z lockfile
pip-sync requirements-runtime.txt requirements-lock.txt
```

**UWAGA:** Generowanie lockfile możeając zajmować kilka minut.

---

## Struktura Plików Projektu

```
ssi/
├── .gitignore                    # Ignorowane pliki
├── pyproject.toml                # Główna konfiguracja (PEP 621)
├── INSTALL.md                    # Ta instrukcja
├── PROJECT_RULES.md              # Zasady projektu
├── README.md                     # Ogólna dokumentacja
│
├── requirements-runtime.txt      # Zależności produkcji
├── requirements-dev.txt         # Zależności developerskie
└── requirements-ml.txt           # Zależności ML (opcjonalne)
│
├── SSI/                          # Kod źródłowy
│   ├── __init__.py
│   ├── v2/                       # V2 Model Laboratory
│   ├── v3/                       # V3 World Knowledge Engine
│   └── v4/                       # V4 Autonomous Agent Ecosystem
│
└── pamiec_modeli_v2/             # System pamięci modeli
    ├── __init__.py
    ├── integration.py            # Główna fasada
    ├── schemas.py                # Schematy danych
    └── ...
```

---

## Kryteria Akceptacji (Sprint 7.1)

| Kryterium | Komenda | Oczekiwany Wynik | Status |
|----------|---------|-----------------|--------|
| Czysty checkout daje się uruchomić | `git clone && cd ssi` |intesu | ⬜ |
| `python --version` zwraca 3.11.x | `python --version` | `Python 3.11.x` | ⬜ |
| Instalacja z lockfile bez konfliktów | `pip install -r requirements-lock.txt` | EXIT CODE 0 | ⬜ |
| `import pamiec_modeli_v2.integration` działa | `python -c "from pamiec_modeli_v2.integration import *"` | No errors | ⬜ |
| `python -m pip check` kończy się 0 | `python -m pip check` | EXIT CODE 0 | ⬜ |
| Fixture danych istnieje | `ls data/fixtures/` | Pliki obecne | ⬜ |

---

## Wsparcie i Kontakt

### Dokumentacja

- `PROJECT_RULES.md` - Zasady projektu (NAJWAŻNIEJSZE!)
- `SSI_DOCUMENTATION/` - Dokumentacja techniczna
- `01_SYSTEM_ARCHITECTURE.md` - Architektura systemu
- `10_IMPLEMENTATION_MAP.md` - Plan implementacji

### Rozwiązywanie problemów

1. **Sprawdź** `INSTALL.md` (ten plik)
2. **Sprawdź** `PROJECT_RULES.md`
3. **Sprawdź** `PROJECT_JOURNAL.md` (historia projektu)
4. **Szukaj** w `SSI_DOCUMENTATION/`

---

## Historia Dokumentu

| Wersja | Data | Autor | Zmiany |
|--------|------|-------|--------|
| 1.0.0 | 2026-07-28 | MSDI AI + Mistral Vibe | Utworzenie instrukcji (Sprint 7.1) |

---

**Dokument: INSTALL.md**  
**Status: AKTYWNY**  
**Zgodny z: PROJECT_RULES.md, Sprint 7.1**
