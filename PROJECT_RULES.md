# PROJECT RULES - MSDI AI / SSI

## Self Learning Intelligence Ecosystem - Zasady Projektowe

**Wersja zasad:** 2.0  
**Aktualizacja:** 2026-07-30  
**Podstawa aktualizacji:** `SSI_DOCUMENTATION/AUDYT_ZGODNOSCI_I_GOTOWOSCI_DO_SKALOWANIA_2026-07-30.md`

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
├── V2 - MODEL LABORATORY (trening + walidacja według DataSplitPolicy)
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
| **V2** | Modele, predykcje, analiza cech | 60% łącznie: trening + walidacja, do czasu zatwierdzenia `DataSplitPolicy` |
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
- **Testuj lokalnie** przed commitem.
- **Sprawdź składnię** - `python -m compileall -q .`.
- **Sprawdź importy** zmienianego modułu i jego bezpośrednich konsumentów.
- **Uruchom testy** - `python -m pytest`; brak wykrytych testów nie oznacza sukcesu.
- **Sprawdź zależności** - `python -m pip check`.
- **Uruchom smoke test** odpowiedniego przepływu, nie tylko konstruktor klasy.
- **Sprawdź kod procesu** - wyjątek, timeout lub brak testów musi dać kod różny od zera.
- **Nie uznawaj `print("tests passed")` za test** bez asercji i test runnera.
- **Nie zamykaj zadania**, jeśli wymaganych testów nie dało się uruchomić; oznacz je jako niezweryfikowane i opisz blokadę.

### 5. Zasada Środowiska

- Wspierany interpreter: **Python 3.11.x, 64-bit**.
- Projekt uruchamiaj w izolowanym `.venv`, nie w globalnym środowisku użytkownika.
- Zależności instaluj z zatwierdzonego pliku projektu i lockfile.
- Nie dodawaj zależności tylko dlatego, że istnieje w środowisku lokalnym.
- Kod nie może zależeć od ścieżek konkretnego komputera, np. `D:\...`.
- Import modułu nie może wykonywać zapisu, tworzyć katalogów ani konfigurować file handlera.
- Wszystkie pliki tekstowe, logi i dokumentacja używają UTF-8.

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
- **SPRINTY.md** - Bieżąca kolejność prac i kryteria akceptacji
- **AUDYT_ZGODNOSCI_I_GOTOWOSCI_DO_SKALOWANIA_2026-07-30.md** - Rejestr ryzyk bazowych

Dokumentacja opisuje stan planowany, ale **stan `implemented`, `tested` lub `operational` musi mieć dowód w kodzie i testach**. W razie konfliktu:

1. stałe zasady określa `PROJECT_RULES.md`;
2. kolejność i Definition of Done określa `SPRINTY.md`;
3. kontrakt techniczny określa `SSI_DOCUMENTATION/`;
4. faktyczny stan implementacji potwierdza kod;
5. faktyczny stan jakości potwierdza automatyczny test i CI;
6. status operacyjny potwierdza smoke test, health check i metryki.

### Zasady Dokumentacji

✅ **Każda nowa funkcjonalność musi być udokumentowana**
✅ **Każda decyzja architektoniczna musi być zapisana**
✅ **Każda zmiana w systemie musi być zarejestrowana w PROJECT_JOURNAL.md**
✅ **Każdy status musi używać jednego ze stanów:** `planned`, `implemented`, `tested`, `operational`
✅ **Każde wymaganie krytyczne musi wskazywać test lub kryterium akceptacji**
✅ **Każdy przykład komendy musi być wykonywalny albo jawnie oznaczony jako pseudokod**

❌ **Zabronione**:
- Tworzenie konkurencyjnej dokumentacji
- Dokumentacja nieaktualna
- Brak dokumentacji dla nowych modułów
- Deklarowanie testów, których nie ma w test runnerze
- Deklarowanie gotowości tylko na podstawie obecności klasy lub feature flag

### Hierarchia Dokumentów

```
PROJECT_RULES.md       # Zasady (ten plik) - NAJWYŻSZY PRIORYTET
├── SPRINTY.md           # Roadmapa i wykonywalne kryteria akceptacji
├── SSI_DOCUMENTATION/  # Dokumentacja techniczna i audyty
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

### Nienaruszalna granica kod/dane

- Każdy `*.py` wymagany przez entrypoint, import lub test **musi trafić do Git**.
- Nie wolno ignorować całego katalogu zawierającego jednocześnie kod i artefakty runtime.
- Dla `pamiec_modeli_v2/` kod Python ma być śledzony, a archiwa, dane i modele ignorowane precyzyjnymi regułami.
- Małe fixture testowe mogą trafić do Git, jeżeli nie zawierają danych produkcyjnych ani sekretów.
- Przed zakończeniem zadania sprawdź, czy świeży checkout zawiera wszystkie importowane moduły.

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

## 🧭 MAPA OPERACYJNA DLA PROGRAMISTY I ASYSTENTA

Ta sekcja jest obowiązkową instrukcją wykonawczą. Asystent ma używać jej przy każdym zadaniu dotyczącym kodu, testów, konfiguracji lub dokumentacji.

### 1. Kolejność poznania kontekstu

Przed planowaniem zmiany przeczytaj w podanej kolejności:

1. `PROJECT_RULES.md`;
2. odpowiedni zakres i kryteria w `SPRINTY.md`;
3. odpowiedni dokument w `SSI_DOCUMENTATION/`;
4. ostatnie istotne wpisy `PROJECT_JOURNAL.md`;
5. kod zmienianego modułu;
6. testy modułu i jego konsumentów;
7. konfigurację, entrypoint i `.gitignore`, jeżeli zmiana dotyczy runtime.

Nie zakładaj, że status w dokumencie oznacza działającą implementację. Potwierdź go testem.

### 2. Klasyfikacja zadania

Przypisz zadanie do co najmniej jednej kategorii:

| Kategoria | Obowiązkowa weryfikacja |
|---|---|
| Dokumentacja | zgodność z kodem, linki, komendy, UTF-8 |
| Konfiguracja/ścieżki | test na ścieżkach względnych i absolutnych, brak `SSI/SSI`, brak ścieżek autora |
| V2/ML | kontrakt danych, split policy, seed, lineage, brak leakage |
| V3/pamięć | integralność, wersja schematu, odczyt/zapis, współbieżność |
| V4/agenci | timeout, deadlock, race condition, zmiana stanu, izolacja błędu |
| Integracja V2→V3→V4 | kontrakty obu granic i pionowy smoke test |
| CLI/runtime | poprawny exit code, brak maskowania wyjątków, `--help`, smoke test |
| Zależności | izolowany venv, lockfile, `pip check`, licencja i bezpieczeństwo |
| Git/struktura | kod śledzony, artefakty ignorowane, świeży checkout |

### 3. Obowiązkowy baseline przed edycją

Asystent zapisuje wynik lub jasno raportuje brak możliwości wykonania:

```powershell
python --version
python -m compileall -q .
python -m pip check
python -m pytest
```

Dodatkowo:

- wykonaj import smoke zmienianego modułu;
- sprawdź aktualny `git status`;
- zidentyfikuj istniejące błędy bazowe, aby nie przypisać ich nowej zmianie;
- nie naprawiaj automatycznie niepowiązanych problemów bez rozszerzenia zakresu.

### 4. Hierarchia priorytetów implementacji

Do czasu spełnienia bramki Sprintu 10 obowiązuje kolejność:

1. **P0 — reprodukowalność:** checkout, venv, zależności, kod w Git;
2. **P0 — poprawność runtime:** ścieżki, importy, exit codes;
3. **P0 — bezpieczeństwo V4:** deadlocki i kontrolowane timeouty;
4. **P0 — kontrakty:** V2→V3→V4 i pionowy smoke test;
5. **P1 — testy i CI:** automatyczne bramki jakości;
6. **P1 — obserwowalność:** logi, health checks i metryki;
7. **P1 — synchronizacja dokumentacji;**
8. **dopiero potem nowe funkcje:** Strategy, Laboratories, Feedback, Evolution, Decision i V5.

Asystent nie powinien dodawać nowych typów agentów ani kolejnych abstrakcji, jeżeli zmiana omija aktywny blocker P0 dotyczący tej samej ścieżki.

### 5. Kontrakty między warstwami

Każda granica V2→V3 i V3→V4 musi mieć:

- jawny, wersjonowany typ danych;
- pola wymagane i wartości domyślne;
- walidację typów, zakresów i brakujących wartości;
- identyfikator korelacji;
- wersję datasetu, modelu, konfiguracji i kodu;
- określoną obsługę niekompatybilnej wersji;
- test pozytywny, negatywny i kompatybilności;
- zakaz przekazywania nieudokumentowanego `Dict[str, Any]` jako trwałego kontraktu.

Zmiana kontraktu wymaga:

1. aktualizacji schematu;
2. decyzji o kompatybilności;
3. migracji lub adaptera;
4. testów producenta i konsumenta;
5. aktualizacji dokumentacji.

### 6. Reguły danych i eksperymentów ML

- Jedyną zatwierdzoną politykę podziału danych przechowuj jako wersjonowany `DataSplitPolicy`.
- Dokumentacja i kod muszą tak samo rozróżniać trening, walidację i niezależną obserwację.
- Split danych czasowych nie może powodować przecieku informacji z przyszłości.
- Każdy eksperyment zapisuje seed, zakres danych, wersję cech, modelu i konfiguracji.
- Wynik bez lineage jest wynikiem diagnostycznym, nie artefaktem produkcyjnym.
- Testy używają małych fixture, nie pełnych danych ani zasobów sieciowych.
- Model nie może być uznany za lepszy bez zatwierdzonej metryki, baseline i przedziału danych.

### 7. Reguły współbieżności

- Domyślnie preferuj prosty model własności danych zamiast współdzielonego stanu.
- Każdy lock ma właściciela, opis chronionego stanu i minimalny zakres.
- Nie wywołuj publicznej metody przejmującej ten sam `threading.Lock` z wnętrza sekcji krytycznej.
- Jeśli wymagane jest ponowne wejście, decyzja o `RLock` musi być świadoma i pokryta testem.
- Nie wykonuj I/O, operacji ML ani callbacków pod lockiem.
- Ustal kolejność przejmowania wielu locków.
- Każda operacja agenta i synchronizacji ma limit czasu.
- Test wielowątkowy musi mieć asercje, timeout i wielokrotne powtórzenie w CI.
- Timeout lub deadlock jest błędem krytycznym, nigdy „wolnym testem”.

### 8. Reguły błędów i kodów procesu

- Warstwa domenowa zgłasza jawne wyjątki; nie drukuje błędu i nie kontynuuje w nieokreślonym stanie.
- Szeroki `except Exception` jest dozwolony na granicy CLI/orchestracji, jeśli:
  1. zapisuje traceback;
  2. mapuje błąd na czytelny komunikat;
  3. kończy proces kodem różnym od zera;
  4. nie oznacza operacji jako sukces.
- `pytest` bez testów, timeout, nieudany import i konflikt `pip check` są niepowodzeniem bramki.
- Nie używaj tekstu „tests passed”, jeżeli wynik nie pochodzi z wykonanych asercji.
- Nie przechwytuj `KeyboardInterrupt` i sygnałów zakończenia jako zwykłego błędu biznesowego.

### 9. Reguły konfiguracji i przenośności

- Ścieżki buduj przez `pathlib.Path` względem jednego jawnego root.
- Pole konfiguracji przechowuje ścieżkę względną albo absolutną, ale nie miesza obu modeli.
- Nie dodawaj prefiksu `SSI` do wartości, która już go zawiera.
- Brak wymaganego katalogu lub pliku zgłoś podczas walidacji startowej.
- Feature flag nie jest dowodem istnienia ani gotowości modułu.
- Niezaimplementowana funkcja ma domyślnie `False`.
- Sekrety pochodzą ze zmiennych środowiskowych lub zatwierdzonego secret store; nigdy z Git.
- Import ma być bezpieczny i pozbawiony efektów ubocznych.

### 10. Reguły logowania i obserwowalności

- Konfiguruj logowanie raz, w entrypoincie.
- Biblioteka używa `logging.getLogger(__name__)` i nie wywołuje `basicConfig()`.
- Log strukturalny zawiera co najmniej: czas, poziom, moduł, zdarzenie i `correlation_id`.
- Nie loguj sekretów, pełnych rekordów użytkownika ani dużych tensorów.
- Health check odpowiada, czy proces żyje.
- Readiness check potwierdza, czy wymagane moduły i zależności są faktycznie gotowe.
- Metryki rozróżniają sukces, błąd kontrolowany, timeout i odrzucenie walidacji.

### 11. Minimalna macierz testów

| Rodzaj zmiany | Unit | Integration | Smoke | Dodatkowo |
|---|:---:|:---:|:---:|---|
| Czysta dokumentacja | — | — | — | linki, komendy, UTF-8 |
| Funkcja domenowa | ✅ | według zależności | — | przypadki brzegowe |
| Kontrakt danych | ✅ | ✅ | — | kompatybilność wersji |
| Ścieżki/konfiguracja | ✅ | ✅ | ✅ | różny CWD i Windows |
| Agent V4 | ✅ | ✅ | ✅ | timeout i współbieżność |
| CLI | ✅ | ✅ | ✅ | exit codes |
| Zależność zewnętrzna | ✅ | ✅ | ✅ | `pip check`, security |
| Przepływ V2→V4 | ✅ | ✅ | ✅ | lineage i determinism |

### 12. Definition of Done

Zadanie jest zakończone wyłącznie, gdy:

- [ ] zakres odpowiada aktywnemu sprintowi lub zatwierdzonej zmianie;
- [ ] kod i dokumentacja są spójne;
- [ ] importy i kompilacja przechodzą;
- [ ] wymagane testy istnieją i przechodzą;
- [ ] nie ma nowego deadlocku, timeoutu ani maskowanego wyjątku;
- [ ] exit code odzwierciedla wynik operacji;
- [ ] `pip check` przechodzi lub nie dotyczy zmiany i istniejące konflikty są jawnie opisane;
- [ ] kod wymagany przez funkcję jest śledzony przez Git;
- [ ] nie zapisano danych, modeli, logów ani sekretów do Git;
- [ ] zaktualizowano dokumentację, sprint i journal, jeśli zmienił się status;
- [ ] raport końcowy podaje dokładnie uruchomione testy i ich wyniki;
- [ ] niewykonanej weryfikacji nie przedstawiono jako sukces.

### 13. Statusy funkcjonalności

| Status | Znaczenie | Wymagany dowód |
|---|---|---|
| `planned` | opisano zakres | wpis w roadmapie |
| `implemented` | kod istnieje | import/kompilacja i review |
| `tested` | zachowanie potwierdzone | automatyczny test z asercją |
| `operational` | działa w środowisku | smoke test, health check, metryki |

Status może przesuwać się tylko o jeden poziom po dostarczeniu dowodu. Plik klasy, demonstracja lub komunikat w konsoli nie wystarcza do statusu `tested`.

### 14. Znane blokery bazowe z audytu

Do czasu zamknięcia odpowiednich sprintów asystent musi pamiętać, że audyt wykazał:

- brak repozytoryjnego test suite i CI;
- kod `pamiec_modeli_v2` ignorowany przez Git mimo użycia w entrypoincie;
- konflikt zależności w środowisku globalnym;
- nieprzenośną ścieżkę `D:\...` w warstwie 5;
- podwójny prefiks `SSI/SSI` w konfiguracji ścieżek;
- deadlock operacji decyzyjnych V4;
- runner testów maskujący błąd kodem procesu `0`;
- niespójne statusy dokumentacji i implementacji.

Nie zakładaj, że blocker nadal istnieje: przed zmianą odtwórz go testem. Po naprawie dodaj test regresyjny i zaktualizuj audyt, sprint oraz journal.

### 15. Raport asystenta po zadaniu

Raport musi zawierać:

1. wynik i status;
2. pliki zmienione;
3. wpływ na warstwy i kontrakty;
4. dokładne komendy testowe;
5. liczbę testów zaliczonych, niezaliczonych i pominiętych;
6. znane ograniczenia;
7. zmianę statusu `planned/implemented/tested/operational`;
8. następny bezpieczny krok.

Nie używaj samego stwierdzenia „wszystko działa”.

### 16. Bramka skalowania

- Domyślny status projektu pozostaje `NO-GO` dla skalowania produkcyjnego do czasu zamknięcia Sprintu 10.
- Decyzja `GO` wymaga przejścia wszystkich kryteriów Sprintu 10 i zamknięcia ryzyk P0.
- Brak dowodu oznacza `NO-GO`; nie wolno przyjmować gotowości na podstawie deklaracji.
- Decyzja musi wskazywać wersję kodu, środowiska, danych, raport testów, benchmark i ryzyka rezydualne.
- `GO` dla developmentu nie oznacza `GO` dla produkcji ani skalowania danych.

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
   - PROJECT_JOURNAL.md (ostatnie wpisy)
   - SPRINTY.md (aktywny zakres i kryteria)
    - SSI_DOCUMENTATION/ (kontekst)
   - baseline: Python, compileall, pip check, pytest
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
   - Test regresyjny
   ↓
7. WERYFIKACJA
    - Importy działają?
    - Testy przechodzą?
   - Smoke test przechodzi?
   - Exit code jest poprawny?
   - Brak timeoutu/deadlocku?
    - Kod jest czytelny?
   ↓
8. DOKUMENTACJA
    - Zaktualizuj PROJECT_JOURNAL.md
   - Zaktualizuj SPRINTY.md, jeśli zmienił się status
    - Dodaj komentarze w kodzie
    - Zaktualizuj dokumentację (jeśli potrzebne)
   ↓
9. COMMIT
   - Tylko jeśli użytkownik zlecił commit
    - git add [pliki]
    - git commit -m "[TYP]: [Opis]"
    - git push (jeśli zatwierdzone)
   ↓
10. RAPORT
    - Co zostało zrobione
    - Jakie dokładnie testy uruchomiono
    - Jaki status funkcjonalności osiągnięto
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
**Poziom funkcjonalności**: planned | implemented | tested | operational

### Co Zostało Zrobione
- Krok 1: [opis]
- Krok 2: [opis]
- Krok 3: [opis]

### Pliki Zmienione
- `ścieżka/do/pliku.py` - [co zostało zmienione]

### Testy
- Komenda: `[dokładna komenda]`
- Wynik: `[exit code, passed/failed/skipped]`
- Smoke test: `[wynik albo nie dotyczy]`
- Brakujące: `[czego nie zweryfikowano i dlaczego]`

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
3. **Jedno Źródło Prawdy** - PROJECT_RULES.md, SPRINTY.md, SSI_DOCUMENTATION/ i dowody testowe
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
2. **Sprawdź** SPRINTY.md
3. **Sprawdź** SSI_DOCUMENTATION/
4. **Sprawdź** PROJECT_JOURNAL.md
5. **Sprawdź** kod i testy
6. **Zapytaj** o konkretną sprawę

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
