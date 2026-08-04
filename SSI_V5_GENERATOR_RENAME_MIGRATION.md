# SSI V5 - GENERATOR RENAME & MIGRATION PLAN

## Cel Migracji

Zmiana historycznej nazwy `generatorDataBaseTrendAnalisAll.py` na nową, spójna z architekturą SSI V5:

```
Stara nazwa:    generatorDataBaseTrendAnalisAll.py
Nowa nazwa:    SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py
```

---

## Uzasadnienie Nowej Nazwy

### Analiza Składników Nazwy

| Składnik | Znaczenie | Uzasadnienie |
|----------|-----------|--------------|
| **SSI_V5** | Architektura | Sygnalizuje należność do SSI Version 5 |
| **SPORTS** | Domeny | Nie ogranicza do piłki - obsługuje piłkę, hokej, inne dyscypliny |
| **WORLD_MODEL** | Funkcjonalność | Odpowiada aktualnej architekturze: World Memory, Teacher Engine, modele, wiedza, obserwacje |
| **GENERATOR** | Rola | Buduje i przelicza świat danych - jasne określenie funkcji |

### Porównanie z Alternatywami

| Nazwa | Zalety | Wady | Decyzja |
|-------|--------|------|---------|
| `SSI_V5_FOOTBALL_HOCKEY_WORLD_MODEL_GENERATOR.py` | Jawnie wymienia dyscypliny | Za długa, ogranicza do konkretnych sportów | ❌ |
| `SSI_V5_SPORTS_WORLD_TREND_ANALYSIS_GENERATOR.py` | Dobrze opisuje funkcję | "TREND_ANALYSIS" może być mylące (nie tylko trendy) | ❌ |
| `SSI_V5_SPORTS_MODEL_MEMORY_GENERATOR.py` | Podkreśla modele i pamięć | Mniej ogólne niż "WORLD_MODEL" | ❌ |
| **`SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py`** | **✅ Ogólna, przyszłościowa, spójna z architekturą** | ✅ **WYBRANE** |

---

## Nowa Dokumentacja Modułu

### SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py

**Odpowiedzialność:**
- Budowa modeli sportowych (sieci neuronowe Keras)
- Generowanie predykcji na podstawie danych historycznych
- Analiza trendów i zachowań (kursy, statystyki, dynamika)
- Tworzenie pamięci modeli (obserwacje, oceny, historia)
- Generowanie wiedzy dla agentów SSI V5
- Obsługa rezultatów i błędów predykcji

**Obsługiwane Ekosystemy:**
```
Ekosystem A: dataBase_futbol_trend
├── siec_08_log_koniec
├── siec_09_ratio_start
├── siec_10_ratio_koniec
└── siec_11_statystyka

Ekosystem B: kursy_przygotowane
├── siec_01_start_kursow
├── siec_02_koniec_kursow
├── siec_03_zmiana_kursow
└── siec_04_procent_kursow

Ekosystem C: dataBase_futbol_popularne_trend (PRZYSZŁOŚĆ)
└── (do zaimplementowania)

Ekosystem D: kursy_popularne_przygotowane (PRZYSZŁOŚĆ)
└── (do zaimplementowania)
```

---

## Lista Zmian - Migracja Nazwy

### 1. Zmiana Nazwy Pliku Głównego

| Stara Lokalizacja | Nowa Lokalizacja | Status |
|-------------------|------------------|--------|
| `D:/sts/aplikacjaTyperBetAi/generatorDataBaseTrendAnalisAll.py` | `D:/sts/aplikacjaTyperBetAi/SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py` | ⏳ Oczekuje na zatwierdzenie |

---

### 2. Zmiany w Plikach Czesci (czesc1-4.py)

#### Wszystkie pliki (czesc1.py, czesc2.py, czesc3.py, czesc4.py)

**Aktualne importy/referencje:**
```python
# Obecnie w czesc2.py, czesc3.py, czesc4.py:
from GeneratorDataBaseTrendAnalisAll import *
# lub
import GeneratorDataBaseTrendAnalisAll
# lub
from generatorDataBaseTrendAnalisAll import oblicz_cechy_3kursy_rozszerzone, normalize, bezpieczny_log
```

**Do zamiany na:**
```python
from SSI_V5_SPORTS_WORLD_MODEL_GENERATOR import *
# lub
import SSI_V5_SPORTS_WORLD_MODEL_GENERATOR
# lub
from SSI_V5_SPORTS_WORLD_MODEL_GENERATOR import oblicz_cechy_3kursy_rozszerzone, normalize, bezpieczny_log
```

**Liczba wystąpień do zamiany:**
- `czesc1.py`: ~5-10 referencji
- `czesc2.py`: ~15-20 referencji
- `czesc3.py`: ~10-15 referencji
- `czesc4.py`: ~20-25 referencji

---

### 3. Zmiany w Plikach Konfiguracyjnych

#### 3.1 Skrypty Uruchamiajace

| Plik | Obecna zawartość | Nowa zawartość |
|------|------------------|----------------|
| `run_generator.bat` | `python generatorDataBaseTrendAnalisAll.py` | `python SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py` |
| `start_ssiv5.sh` | `python3 generatorDataBaseTrendAnalisAll.py` | `python3 SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py` |
| `setup.py` (jeśli istnieje) | `scripts=['generatorDataBaseTrendAnalisAll.py']` | `scripts=['SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py']` |

#### 3.2 Pliki Konfiguracyjne Systemowe

**Do sprawdzenia w:**
- `config.json` (jeśli istnieje)
- `settings.py` (jeśli istnieje)
- Pliki YAML/INI z ustawieniami

**Szukać wzorców:**
```
"generatorDataBaseTrendAnalisAll"
'generatorDataBaseTrendAnalisAll'
generatorDataBaseTrendAnalisAll
GeneratorDataBaseTrendAnalisAll
```

---

### 4. Zmiany w Dokumentacji

#### 4.1 Pliki Markdown

| Plik | Zmiana |
|------|--------|
| `README.md` | Zaktualizować wszystkie referencje do nazwy generatora |
| `SSI_V5_GENERATOR_FULL_ARCHITECTURE.md` | Zaktualizować nagłówki i opisy |
| `SSI_V5_CZESC1_HOOK_MAP.md` | Zaktualizować referencje do głównego pliku |
| `SSI_V5_CZESC2_HOOK_MAP.md` | Zaktualizować referencje do głównego pliku |
| `SSI_V5_CZESC3_HOOK_MAP.md` | Zaktualizować referencje do głównego pliku |
| `SSI_V5_CZESC4_HOOK_MAP.md` | Zaktualizować referencje do głównego pliku |

#### 4.2 Komentarze w Kodzie

**Szukać i zamienić w:**
- Komentarze na początku plików czesc1-4.py
- Komentarze w funkcjach
- Docstringi

**Przykład:**
```python
# Stare:
# GeneratorDataBaseTrendAnalisAll - Modul glowny

# Nowe:
# SSI_V5_SPORTS_WORLD_MODEL_GENERATOR - Modul glowny
```

---

### 5. Zmiany w Ścieżkach Systemowych

#### 5.1 Zmienne Środowiskowe

**Do sprawdzenia w:**
- `.env` files
- Systemowe zmienne środowiskowe (Windows/Linux)
- Pliki konfiguracyjne IDE

**Szukać:**
```
GENERATOR_PATH=generatorDataBaseTrendAnalisAll.py
MAIN_GENERATOR=generatorDataBaseTrendAnalisAll
```

#### 5.2 Harmonogram Uruchamiania (Cron/Task Scheduler)

**Windows Task Scheduler:**
- Sprawdzić wszystkie zaplanowane zadania
- Zaktualizować ścieżki do nowej nazwy pliku

**Linux Cron:**
```bash
# Stare:
0 2 * * * /usr/bin/python3 /d/sts/aplikacjaTyperBetAi/generatorDataBaseTrendAnalisAll.py

# Nowe:
0 2 * * * /usr/bin/python3 /d/sts/aplikacjaTyperBetAi/SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py
```

---

### 6. Zmiany w Systemach Zewnętrznych

#### 6.1 Systemy Monitorujące
- **Prometheus/Grafana**: Configuration files
- **Log collectors**: Path configurations
- **Alert systems**: File watchers

#### 6.2 Systemy CI/CD
- `.github/workflows/` (jeśli używasz GitHub Actions)
- Jenkins/GitLab CI configuration
- Dockerfiles

#### 6.3 Backup Systems
- Skrypty backupowe
- Lista plików do backupu
- Restore procedures

---

## Harmonogram Migracji

### Fazy Migracji

```
┌─────────────────────────────────────────────────────────────────┐
│                    HARMONOGRAM MIGRACJI                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  FAZA 0: PRZYGOTOWANIE (1-2 dni)                                 │
│  ├─ Zatwierdzenie nowej nazwy                                     │
│  ├─ Utworzenie listy zmian (ten dokument)                       │
│  └─ Backup wszystkich plików                                     │
│                                                                  │
│  FAZA 1: DOKUMENTACJA (1 dzień)                                   │
│  ├─ Zaktualizowanie wszystkich plików .md                        │
│  └─ Zaktualizowanie komentarzy w kodzie                          │
│                                                                  │
│  FAZA 2: KOD (1-2 dni)                                           │
│  ├─ Zmiana nazwy głównego pliku                                  │
│  ├─ Zaktualizowanie importów w czesc1-4.py                       │
│  └─ Testy jednostkowe czesci                                     │
│                                                                  │
│  FAZA 3: KONFIGURACJA (1 dzień)                                  │
│  ├─ Skrypty uruchamiające                                       │
│  ├─ Pliki konfiguracyjne                                        │
│  └─ Ścieżki systemowe                                           │
│                                                                  │
│  FAZA 4: SYSTEMY ZEWNETRZNE (1 dzień)                             │
│  ├─ Cron/Task Scheduler                                          │
│  ├─ Systemy monitorujące                                        │
│  └─ CI/CD pipelines                                              │
│                                                                  │
│  FAZA 5: WERYFIKACJA (1-2 dni)                                   │
│  ├─ Testy integracyjne                                         │
│  ├─ Weryfikacja wszystkich zależności                           │
│  └─ Raport z migracji                                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Szacowany Czas Calkowity: **5-7 dni roboczych**

---

## Checklista Weryfikacji

### Przed Migracją
- [ ] Zatwierdzenie nowej nazwy przez zespół
- [ ] Backup całego projektu
- [ ] Zweryfikowanie listy zmian
- [ ] Przeprowadzenie testów na kopii projektu

### Po Migracji
- [ ] Wszystkie pliki kompilują się poprawnie
- [ ] Wszystkie importy działają
- [ ] Skrypty uruchamiające funkcjonują
- [ ] Harmonogramy uruchamiania działają
- [ ] Systemy zewnętrzne widzą nową nazwę
- [ ] Testy jednostkowe przebiegają pomyślnie
- [ ] Testy integracyjne przebiegają pomyślnie

---

## Procedura Awaryjna (Rollback)

### Krok 1: Natychmiastowe Przerwanie
```bash
# Jeśli coś pójdzie nie tak:
1. Zatrzymać wszystkie procesy korzystające z generatora
2. Przywrócić backup plików
```

### Krok 2: Przywrócenie Starej Nazwy
```bash
# Jeśli migracja nie powiedzie się:
1. Skopiować backup z powrotem do starej nazwy
2. Zaktualizować wszystkie importy z powrotem
3. Uruchomić testy weryfikacyjne
```

### Krok 3: Weryfikacja
```bash
# Sprawdzić:
- Czy wszystkie systemy działają z powrotem do starej nazwy
- Czy nie ma uszkodzonych zależności
- Czy harmonogramy uruchamiania działają
```

---

## Ryzyka i Mitigacje

| Ryzyko | Prawdopodobieństwo | Wpływ | Mitigacja |
|--------|-------------------|-------|-----------|
| Uszkodzone importy w czesc1-4.py | Wysokie | Wysoki | Testy jednostkowe przed migracją |
| Błędy w harmonogramach uruchamiania | Średnie | Wysoki | Weryfikacja wszystkich zadań cron |
| Problemy z systemami zewnętrznymi | Niskie | Średni | Koordynacja z zespołem DevOps |
| Utrata danych konfiguracyjnych | Niske | Wysoki | Pełny backup przed migracją |
| Konflikty合并 | Średnie | Średni | Użycie gałęzi feature branch |

---

## Zespoly Odpowiedzialne

| Zespół | Odpowiedzialność | Osoba Kontaktowa |
|--------|------------------|-----------------|
| **Architektura SSI** | Zatwierdzenie nazwy, nadzór migracji | - |
| **Backend** | Zmiany w kodzie (importy, referencje) | - |
| **DevOps** | Skrypty, harmonogramy, CI/CD | - |
| **QA** | Testy weryfikacyjne | - |
| **Dokumentacja** | Aktualizacja plików .md | - |

---

## Status Migracji

| Data | Etap | Status | Uwagi |
|------|------|--------|-------|
| 2026-08-03 | Przygotowanie dokumentu | ✅ Zakończone | Dokument gotowy do zatwierdzenia |
| TBD | Zatwierdzenie | ⏳ Oczekuje | Czeka na decyzję zespołu |
| TBD | Dokumentacja | ⏳ Oczekuje | Po zatwierdzeniu |
| TBD | Kod | ⏳ Oczekuje | Po zatwierdzeniu |
| TBD | Konfiguracja | ⏳ Oczekuje | Po zatwierdzeniu |
| TBD | Systemy Zewnętrzne | ⏳ Oczekuje | Po zatwierdzeniu |
| TBD | Weryfikacja | ⏳ Oczekuje | Po zatwierdzeniu |

---

## Podsumowanie

### Co Teraz?
1. **NIE ZMIENIAĆ** fizycznej nazwy pliku `generatorDataBaseTrendAnalisAll.py`
2. **ZATWIERDZIĆ** nową nazwę: `SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py`
3. **ZATWIERDZIĆ** ten plan migracji
4. **PRZYGOTOWAĆ** środowisko testowe

### Kolejne Kroki Po Zatwierdzeniu
1. Utworzyć branch `feature/ssiv5-generator-rename`
2. Wykonować migrację zgodnie z harmonogramem
3. Przeprowadzić testy weryfikacyjne
4. Zmergować zmiany do main
5. Zaktualizować wszystkie systemy zewnętrzne

---

## Załączniki

- [ ] Backup projektu przed migracją
- [ ] Skrypt automatyzujący zamianę nazw (opcjonalnie)
- [ ] Raport z testów weryfikacyjnych

---

**Dokument przygotowany:** 2026-08-03  
**Wersja:** 1.0  
**Status:** Oczekuje na zatwierdzenie
