# 02 - DEVELOPER INPUT ARCHITECTURE

**Data utworzenia:** 2026-08-01  
**Wersja:** 1.0.0  
**Status:** DRAFT  
**Autor:** Mistral Vibe - CLI Coding Agent  
**Typ dokumentu:** ARCHITEKTURA WEJSCIA PROGRAMISTY  
**Zaleznosc:** 
- SSI_V5_MASTER_SYSTEM_FLOW_ARCHITECTURE.md (podstawa)
- 01_SYSTEM_SIGNAL_ARCHITECTURE.md (sygnaly)

---

## 1. PODSUMOWANIE EXECUTIVE

Ten dokument definiuje **Developer Input Architecture** - system wejscia programisty do systemu SSI V5. 

**ZASADA FUNDAMENTALNA:** Programista NIE komunikuje sie bezposrednio z modulami systemu.

Wszystkie polecenia programisty przeplywaja przez łańcuch:
**PROGRAMISTA -> Developer Command Interface -> Governance Validation -> Information Flow Controller -> Orchestrator -> Modul**

---

## 2. GLOWNE ZASADY

### 2.1. Izolacja Programisty
Programista jest izlowany od bezposredniego dostepu do:
- Modulow systemowych (V1, V2, V3, V4, V5)
- Agentow i ich pamieci
- Kolejki sygnalow
- Stanu systemu runtime

### 2.2. Kontrola Dostepu
Wszystkie polecenia programisty sa:
1. Weryfikowane syntaktycznie
2. Walidowane pod wzgledem dostepu
3. Autoryzowane przez System Governance
4. Monitorowane i logowane

### 2.3. Jednolity Interfejs
Programista uzywa **jednolitego interfejsu** dla wszystkich operacji, niezaleznie od docelowego modulu.

---

## 3. ARCHITEKTURA SYSTEMU

### 3.1. High-Level View

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DEVELOPER INPUT ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐                                                         │
│  │   PROGRAMISTA     │                                                         │
│  │  (User Input)     │                                                         │
│  └────────┬─────────┘                                                         │
│           │                                                                   │
│           ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    DEVELOPER COMMAND INTERFACE                          │    │
│  │  tentativo l'input principale per il programmatore                        │    │
│  │                                                                         │    │
│  │  ┌─────────────────────────┐  ┌─────────────────────────┐              │    │
│  │  │   Command Parser          │  │   Input Validator         │              │    │
│  │  │  - Parsowanie komend       │  │  - Walidacja syntax       │              │    │
│  │  │  - Ekstrakcja parametrow   │  │  - Walidacja typow        │              │    │
│  │  │  - Konwersja formatow     │  │  - Walidacja wartości     │              │    │
│  │  └───────────┬───────────────┘  └─────────────────┬───────────┘              │    │
│  │              │                                  │                          │    │
│  │              ▼                                  ▼                          │    │
│  │  ┌─────────────────────────────────────────────────────────────┐     │    │
│  │  │                      COMMAND PROCESSOR                          │     │    │
│  │  │  - Budowanie drzewa polecen                           │     │    │
│  │  │  -_RANGE Rozwiazywania zaleznosci                              │     │    │
│  │  │  - Optymalizacja wykonania                                  │     │    │
│  │  └──────────────────────────────┬─────────────────────────┘     │    │
│  │                                  │                                      │    │
│  │                                  ▼                                      │    │
│  └──────────────────────────────────┼──────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      GOVERNANCE VALIDATION                             │    │
│  │  - Walidacja uprawnien                                         │    │
│  │  - Sprawdzanie dostepu do modulu                               │    │
│  │  - Weryfikacja zgodnosci z politykami systemowymi               │    │
│  │  - Autoryzacja polecenia                                       │    │
│  └──────────────────────────────────┬──────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                   INFORMATION FLOW CONTROLLER                            │    │
│  │  - Routing sygnalu polecenia                                         │    │
│  │  - Konwersja do formatu systemowego                             │    │
│  │  - Dodanie kontekstu i metadanych                                  │    │
│  └──────────────────────────────────┬──────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        ORCHESTRATOR                                    │    │
│  │  - Koordynacja z Runtime Controller                                  │    │
│  │  - Zarzadzanie kolejka polecen                                      │    │
│  │  - Synchronizacja z cyklem systemu                                 │    │
│  └──────────────────────────────────┬──────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                       TARGET MODULE                                     │    │
│  │  - Wykonanie polecenia                                              │    │
│  │  - Generowanie odpowiedzi                                           │    │
│  │  - Raportowanie statusu                                             │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2. Sequential Flow

```
1. PROGRAMISTA wpisuje polecenie
   │
2. Developer Command Interface odbiera komende
   ├── Parsuje syntax
   ├── Ekstrahuje parametry
   └── Konwertuje formaty
   │
3. Command Processor labuju drzewo polecen
   ├── Rozwiazuje zaleznosci
   └── Optymalizuje kolejke wykonania
   │
4. Governance Validation sprawdza uprawnienia
   ├── Waliduje dostep do modulu
   ├── Weryfikuje zgodnosc z politykami
   └── Autoryzuje lub odrzuca
   │
5. Information Flow Controller routuje polecenie
   ├── Konwertuje do formatu systemowego
   ├── Dodaje kontekst (user_id, timestamp, etc.)
   └── Wysyla do Orchestrator
   │
6. Orchestrator koordynuje wykonanie
   ├── Synchronizuje z cyklem systemu
   ├── Zarzadza kolejka polecen
   └── Przekazuje do docelowego modulu
   │
7. Target Module wykonuje polecenie
   ├── Przetwarza zadanie
   ├── Generuje odpowiedz
   └── Raportuje status
   │
8. Odpowiedz wraca tahrz ta sama sciezka
   └── Programista otrzymuje wynik
```

---

## 4. DEVELOPER COMMAND INTERFACE

### 4.1. Odpowiedzialnosc
Glowne zelo interfejsu:
- Odebranie polecen od programisty
- Parsowanie i walidacja syntax
- Ekstrakcja parametrow
- Konwersja do formatu wewnetrznego
- Inicjowanie przetwarzania

### 4.2. Komponenty

**Command Parser:**
- Analiza skladniowa polecen
- Rozkład na tokeny
- Identyfikacja typow polecen
- Ekstrakcja parametrow

**Input Validator:**
- Walidacja typow danych
- Sprawdzanie zakresow wartosci
- Weryfikacja wymaganych parametrow
- Detekcja potencjalnych bledow

**Format Converter:**
- Konwersja formatow danych
- Normalizacja wartosci
- Adaptacja do oczekiwan systemowych

### 4.3. Obslugiwane Typy Polecen

| Kategoria | Typ Polecenia | Opis | Przyklad |
|----------|---------------|------|----------|
| **SYSTEM** | system:status | Pobierz status systemu | `system:status` |
| | system:start | Uruchom system | `system:start mode=production` |
| | system:stop | Zatrzymaj system | `system:stop` |
| | system:config | Pobierz/ustaw konfiguracje | `system:config get runtime.cycle_limit` |
| **AGENT** | agent:list | Lista agentow | `agent:list` |
| | agent:status | Status agenta | `agent:status 01` |
| | agent:activate | Aktywuj agenta | `agent:activate 01` |
| | agent:deactivate | Deaktywuj agenta | `agent:deactivate 02` |
| | agent:memory | Zarzadzanie pamiecia | `agent:memory 01 export` |
| **MODULE** | module:list | Lista modulow | `module:list` |
| | module:status | Status modulu | `module:status DecisionEngine` |
| | module:start | Uruchom modul | `module:start StrategyLaboratory` |
| | module:stop | Zatrzymaj modul | `module:stop AI_Lab` |
| **MEMORY** | memory:export | Eksport pamieci | `memory:export agent=01 type=BEHAVIOR` |
| | memory:import | Import pamieci | `memory:import file=backup_01.json` |
| | memory:backup | Backup pamieci | `memory:backup all` |
| | memory:restore | Przywroc pamiec | `memory:restore agent=01 version=2026-07-31` |
| **STRATEGY** | strategy:list | Lista strategii | `strategy:list agent=01` |
| | strategy:create | Utworz strategie | `strategy:create agent=01 type=experimental` |
| | strategy:test | Testuj strategie | `strategy:test agent=01 strategy_id=strat_001` |
| | strategy:promote | Awansuj strategie | `strategy:promote agent=01 strategy_id=strat_001` |
| **DATA** | data:collect | Zbierz dane | `data:collect v2` |
| | data:export | Eksportuj dane | `data:export type=courses format=csv` |
| | data:import | Importuj dane | `data:import file=new_data.csv` |
| **PROMPT** | prompt:list | Lista promptow | `prompt:list` |
| | prompt:create | Utworz prompt | `prompt:create type=agent category=decision` |
| | prompt:update | Aktualizuj prompt | `prompt:update id=prompt_001 version=2.0` |
| | prompt:delete | Usun prompt | `prompt:delete id=prompt_001` |
| **DEVELOPER** | dev:log | Pobierz logi | `dev:log level=debug limit=100` |
| | dev:stats | Statystyki systemu | `dev:stats module=AgentManager` |
| | dev:test | Test systemu | `dev:test module=SignalSystem` |
| | dev:trace | Sledzenie polecen | `dev:trace on` |

### 4.4. Syntax Polecen

**Format ogolny:**
```
<kategoria>:<akcja> [param1=wartosc1] [param2=wartosc2] ... [--flag1] [--flag2]
```

**Przyklady:**
```bash
# Pobierz status systemu
system:status

# Uruchom system w trybie testowym
system:start mode=test cycles=5

# Pobierz pamiec agenta 01
agent:memory 01 export type=BEHAVIOR format=json

# Testuj strategie eksperymentalna
strategy:test agent=01 strategy_id=strat_experimental_001 data=historical_2026

# Utworz prompt dla agenta
prompt:create type=agent category=decision autor=programista_01 Cel="Decyzje produktcyjne"

# Zbierz dane z V2 dla ostatnich 7 dni
data:collect v2 start_date=2026-07-25 end_date=2026-08-01
```

### 4.5. Parametry Specjalne

| Parametr | Opis | Wymagany | Domyślna |
|----------|------|----------|-----------|
| `--help` | Pokaz pomoc | Nie | - |
| `--verbose` | Tryb rozbudowany | Nie | false |
| `--dry-run` | Symulacja (bez wykonania) | Nie | false |
| `--async` | Wykonaj asynchronicznie | Nie | false |
| `--priority` | Priorytet polecenia | Nie | MEDIUM |
| `--timeout` | Limit czasu (sekundy) | Nie | 30 |
| `--force` | Wymusz wykonanie | Nie | false |

---

## 5. COMMAND PROCESSOR

### 5.1. Odpowiedzialnosc
- Budowanie drzewa polecen z zaleznosciami
- Rozwiazywania konfliktow polecen
- Optymalizacja kolejnosci wykonania
- Zarzadzanie kontekstem polecen

### 5.2. Drzewo Polecen

```
Przyklad: system:start mode=production

Command Tree:
{
  "command_id": "cmd_001",
  "type": "system:start",
  "parameters": {
    "mode": "production"
  },
  "dependencies": [],
  "priority": "HIGH",
  "timeout": 60,
  "children": [
    {
      "command_id": "cmd_002",
      "type": "module:start",
      "module": "RuntimeController",
      "dependencies": ["cmd_001"],
      "sequence": 1
    },
    {
      "command_id": "cmd_003",
      "type": "module:start",
      "module": "CollectorManager",
      "dependencies": ["cmd_002"],
      "sequence": 2
    },
    {
      "command_id": "cmd_004",
      "type": "module:start",
      "module": "AgentManager",
      "dependencies": ["cmd_003"],
      "sequence": 3
    }
  ]
}
```

### 5.3. Rozwiazywania Zaleznosci

**Typy Zaleznosci:**
1. **SEKWENCYJNA:** Polecenie B musi poczekac na zakonczenie A
2. **ROWNOLEGLA:** Polecenia moga byc wykonane w dowolnej kolejnosci
3. **WYLACZNA:** Tylko jedno z polecen moze byc wykonane

**Przyklad:**
```
Polecenie: system:stop force=true

Zaleznosci:
1. agent:deactivate ALL (SEKWENCYJNA)
2. module:stop DecisionEngine (ROWNOLEGLA z AgentManager)
3. module:stop StrategyLaboratory (ROWNOLEGLA z DecisionEngine)
4. module:stop MemoryEvolution (ROWNOLEGLA)
5. module:stop AI_Lab (ROWNOLEGLA)
6. system:save_state (SEKWENCYJNA, po wszystkich)
7. system:shutdown (SEKWENCYJNA, ostatnie)
```

### 5.4. Optymalizacja Wykonania

Strategie optymalizacji:
1. **Batch Processing:** Laczenie zbiorczych operacji
2. **Parallel Execution:** Wykonywanie niezaleznych polecen rownolegle (z zachowaniem ograniczen sprzetowych)
3. **Caching:** Buforowanie czesto uzywanych wynikow
4. **Lazy Evaluation:** Odraczanie obliczen dopoki nie sa potrzebne

---

## 6. GOVERNANCE VALIDATION

### 6.1. Odpowiedzialnosc
- Walidacja uprawnien usuarios
- Sprawdzanie dostepu do modulow i operacji
- Weryfikacja zgodnosci z politykami systemowymi
- Autoryzacja lub odrzucenie polecen

### 6.2. Polityki Dostepu

**Pozniom Dostepu:**
| Pozniom | Opis | Operacje |
|--------|------|----------|
| READ_ONLY | Tylko odczyt | system:status, agent:list, memory:export |
| BASIC | Odczyt + proste operacje | system:start, system:stop, agent:status |
| ADVANCED | Pelna kontrola modulow | module:*, agent:*, strategy:* |
| DEVELOPER | Dostep developerski | dev:*, prompt:*, data:import/export |
| ADMIN | Pelna kontrola | wszystkie + system:config |

**Macierz Dostepu:**
| Modul \ Pozniom | READ_ONLY | BASIC | ADVANCED | DEVELOPER | ADMIN |
|------------------|-----------|--------|----------|-----------|-------|
| RuntimeController | R | R+W | R+W | R+W | R+W |
| AgentManager | R | R | R+W | R+W | R+W |
| DecisionEngine | R | R | R+W | R+W | R+W |
| StrategyLaboratory | R | R | R | R+W | R+W |
| MemorySystem | R | R | R | R+W | R+W |
| AI_Lab | - | - | - | R | R+W |
| PromptManagement | - | - | - | R+W | R+W |
| DataCollectors | R | R | R+W | R+W | R+W |

**Legenda:** R = Read, W = Write, - = Brak dostepu

### 6.3. Weryfikacja Polityk

**Polityki Systemowe:**
1. **Safety First:** Zablokuj operacje mogace uszkodzic system
2. **Data Integrity:** Zablokuj operacje mogace uszkodzic dane
3. **Resource Limits:** Ograniczenia uzycia zasobow
4. **Audit Trail:** Wszystkie operacje sa logowane
5. **Rate Limiting:** Ograniczenie czestotliwosci polecen

**Przyklady Blokowanych Operacji:**
- `system:stop` podczas Production Mode (bez `--force`)
- `memory:delete` dla aktywnych agentow
- `strategy:promote` bez testow
- `data:import` bez walidacji

### 6.4. Proces Walidacji

```
1. Sprawdzenie autentycznosci uzytkownika
   │
2. Weryfikacja uprawnien (poziom dostepu)
   │
3. Sprawdzenie dostepu do modulu
   │
4. Weryfikacja zgodnosci z politykami
   │
5. Sprawdzenie zaleznosci i ogoliczen
   │
6. Decision: AUTORYZUJ lub ODRZUC
   │
7. Jeśli ODRZUC:
   ├── Powod odrzucenia
   ├── Sugestia poprawnej komendy
   └── Logowanie zdarzenia
```

---

## 7. INFORMATION FLOW CONTROLLER INTEGRATION

### 7.1. Konwersja do FormatU Systemowego

Developer Command -> System Signal:

```
Developer Input: agent:status 01

System Signal:
{
  "signal_id": "sig_dev_001",
  "signal_type": "DEVELOPER_COMMAND",
  "sender": "Developer_Interface",
  "receiver": "AgentManager",
  "timestamp": "2026-08-01T13:00:00",
  "priority": "MEDIUM",
  "data": {
    "command": "agent:status",
    "target": "01",
    "parameters": {},
    "command_id": "cmd_dev_001"
  },
  "context": {
    "user_id": "programista_01",
    "session_id": "sess_001",
    "original_command": "agent:status 01",
    "validation_passed": true,
    "authorization_level": "ADVANCED"
  }
}
```

### 7.2. Dodatkowe Metadane

Kazde polecenie programisty jest wzbogacane o:
- user_id: Identyfikator uzytkownika
- session_id: Identyfikator sesji
- timestamp: Czas zlozenia polecenia
- source: Zrodlo (CLI, API, GUI)
- priority: Priorytet (motywowany przez uzytkownika lub system)
- timeout: Limit czasu wykonania
- trace_id: Unikalny identyfikator sledzenia

---

## 8. ORCHESTRATOR INTEGRATION

### 8.1. Synchronizacja z Cyklu Systemowym

**Zasady integracji:**
1. Polecenia programisty NIE przerywaja bieżącego cyklu
2. Polecenia są wykonywane w przerwach miedzy cyklami
3. Polecenia o wysokim priorytecie moga byc wykonywane natychmiast (z zatrzymaniem cyklu)
4. System zawsze wraca do normalnego cyklu po wykonaniu polecenia

**Przyklad:**
```
Cykle systemu: [CYCLE_1] -> [CYCLE_2] -> [CYCLE_3] -> ...

Polecenie programisty wszystkich podczas CYCLE_2:
- Jeśli priorytet LOW/MEDIUM: Czeka do konca CYCLE_2, wykonywane przed CYCLE_3
- Jeśli priorytet HIGH: Przerwanie CYCLE_2, wykonanie polecenia, wznowienie CYCLE_2
- Jeśli priorytet CRITICAL: Natychmiastowe przerwanie i wykonanie
```

### 8.2. Kolejka Polecen

**Zarzadzanie kolejka:**
- Polecenia sa dodawane do kolejki FIFO
- Priorytety: CRITICAL > HIGH > MEDIUM > LOW
- Polecenia o tym samym priorytecie wykonane w kolejnosci przyjscia
- Mozliwosc wstrzymania polecen w kolejce

**Stan kolejki:**
```json
{
  "queue_id": "dev_command_queue",
  "status": "ACTIVE",
  "commands": [
    {
      "command_id": "cmd_001",
      "type": "system:status",
      "priority": "LOW",
      "timestamp": "2026-08-01T13:00:00",
      "status": "PENDING"
    },
    {
      "command_id": "cmd_002",
      "type": "agent:memory",
      "priority": "MEDIUM",
      "timestamp": "2026-08-01T13:01:00",
      "status": "PENDING"
    }
  ],
  "stats": {
    "total_commands": 2,
    "completed": 0,
    "failed": 0,
    "avg_wait_time": 0
  }
}
```

### 8.3. Współdziałanie z Runtime Controller

**Integracja z runtime_controller.py:**
- RuntimeController monitoruje kolejke polecen programisty
- RuntimeController decyduje o momencie wykonania
- RuntimeController zarzadza zasobami (ograniczenie 1 model LLM)
- RuntimeController raportuje status polecen do programisty

---

## 9. TARGET MODULE EXECUTION

### 9.1. Wykonanie Polecenia

Kazdy modul docelowy implementuje interfejs do obsługi polecen programisty:

**Interfejs Modulu:**
```python
class DeveloperCommandInterface:
    def execute_command(self, command: DeveloperCommand) -> CommandResult:
        """Wykonaj polecenie programisty"""
        pass
    
    def validate_command(self, command: DeveloperCommand) -> ValidationResult:
        """Waliduj polecenie"""
        pass
    
    def get_command_schema(self, command_type: str) -> CommandSchema:
        """Pobierz schema polecenia"""
        pass
```

### 9.2. Typy Wynikow

```
CommandResult:
{
  "command_id": "cmd_001",
  "status": "SUCCESS|FAILED|PARTIAL|PENDING",
  "result": { ... },  # Dane wyniku
  "errors": [],         # Lista bledow
  "warnings": [],       # Lista ostrzezen
  "execution_time_ms": 150,
  "timestamp_complete": "2026-08-01T13:05:00"
}
```

**Statusy:**
- SUCCESS: Polecenie wykonane poprawnie
- FAILED: Blad podczas wykonania
- PARTIAL: Czargesowe wykonanie
- PENDING: Polecenie w kolejce

### 9.3. Raportowanie Statusu

**Mechanizm raportowania:**
1. Modul docelowy generuje CommandResult
2. Wynik przesylany jest z powrotem przez te sama sciezke:
   Target Module -> Orchestrator -> Information Flow Controller -> Governance -> Command Processor -> Developer Interface
3. Developer Interface formatuje wynik dla programisty
4. Programista otrzymuje odpowiedz

---

## 10. OBSLUGA ODPOWIEDZI

### 10.1. Format Odpowiedzi

**Dla uzytkownika:**
```
[SUCCESS] system:status
{
  "status": "RUNNING",
  "mode": "production",
  "cycle_count": 15,
  "agents": ["01", "02", "03", "04", "05", "06"],
  "start_time": "2026-08-01T12:00:00"
}

[FAILED] agent:activate 07
Error: Agent 07 does not exist
Suggestion: Use agent:list to see available agents

[PARTIAL] memory:export agent=01 type=ALL
Warning: Type 'ALL' is deprecated, use specific types
Exported: PERSONALITY, BEHAVIOR, STRATEGY
Skipped: HISTORY (too large)
```

### 10.2. Typy Odpowiedzi

| Typ | Opis | Format |
|-----|------|--------|
| SUCCESS | Poprawne wykonanie | JSON z wynikiem |
| FAILED | Blad wykonania | Tekst bledy + sugestia |
| PARTIAL | Czesciowe wykonanie | JSON + ostrzezenia |
| PENDING | W kolejce | command_id + szacowany czas |
| TIMEOUT | Przekroczony limit czasu | Error + sugestia |

### 10.3. History i Audit

Wszystkie polecenia i odpowiedzi sa zapisywane w:
- Developer Command Log
- System Audit Trail

**Struktura logu:**
```json
{
  "log_id": "dev_log_001",
  "command_id": "cmd_001",
  "command": "system:status",
  "user_id": "programista_01",
  "timestamp_command": "2026-08-01T13:00:00",
  "timestamp_complete": "2026-08-01T13:00:01",
  "status": "SUCCESS",
  "priority": "LOW",
  "execution_time_ms": 1500,
  "result": { ... },
  "errors": [],
  "metadata": {
    "session_id": "sess_001",
    "source": "CLI",
    "trace_id": "trace_001"
  }
}
```

---

## 11. ERROR HANDLING

### 11.1. Typy Bledow

| Typ Bledu | Opis | Kod | Sugestia |
|----------|------|-----|---------|
| UNKNOWN_COMMAND | Nieznane polecenie | ERR_001 | Uzyj --help |
| INVALID_SYNTAX | Bledna skladnia | ERR_002 | Sprawdz syntax |
| MISSING_PARAMETER | Brakujacy parametr | ERR_003 | Podaj wartosc |
| INVALID_PARAMETER | Niewlasciwa wartosc | ERR_004 | Sprawdz zakres |
| ACCESS_DENIED | Brak uprawnien | ERR_005 | Skontaktuj z admin |
| MODULE_UNAVAILABLE | Modul niedostepny | ERR_006 | Spróbuj pozniej |
| RESOURCE_LIMIT | Limit zasobow | ERR_007 | Zmniejsz zakres |
| TIMEOUT | Przekroczonyczas | ERR_008 | Zwieksz timeout |
| INTERNAL_ERROR | Blad wewnetrzny | ERR_009 | Skontaktuj z support |

### 11.2. Strategie Pobierania

1. **Retry:** Ponowne wybustenie (maksymalnie 3 razy)
2. **Fallback:** Uzycie alternatywnej sciezki
3. **Partial Execution:** Wykonanie czesci polecenia
4. **Queue:** Dodanie do kolejki i powtórzenie później
5. **Reject:** Odrzucenie z wyjasnieniem

### 11.3.とはいえ Escalation

```
Blad po raz pierwszy:
  → Logowanie + Powiadomienie uzytkownika

Blad po raz drugi:
  → Logowanie + Sugestia alternatywy

Blad po raz trzeci:
  → Logowanie + Escalation do administratora

Blad krytyczny:
  → Powiadomienie administratora
  → Możliwe zatrzymanie systemu
```

---

## 12. SECURITY I BEZPIECZENSTWO

### 12.1. Autentykacja
- Weryfikacja tożsamości programisty
- Sesje z limitem czasu
- Mechanizm logowania/wylogowania

### 12.2. Autoryzacja
- RBAC (Role-Based Access Control)
-/yпозиomotive na poziomie:
  - Uzytkownik
  - Grupa
  - Rola
  - Modul

### 12.3. Szyfrowanie
- Szyfrowanie komunikatow
- Ochrona danych wrażliwych
- Bezpieczne przechowywanie hasel

### 12.4. Audit
- Pelne logowanie wszystkich operacji
- Nieusunalne dzienniki
- Monitorowanie aktywnosci

---

## 13. INTEGRACJA Z INNYMI DOKUMENTAMI

### 13.1. Powiazanie z Master System Flow

**because w SSI_V5_MASTER_SYSTEM_FLOW_ARCHITECTURE.md:**
- Developer Input Architecture jest czescia Information Flow Controller
- Polecenia programisty są traktowane jako jeden z typów sygnałów
- Wykonanie przebiega przez Orchestrator

### 13.2. Powiazanie z System Signal Architecture

**Zgodnosc z 01_SYSTEM_SIGNAL_ARCHITECTURE.md:**
- Polecenia programisty generuja sygnaly DEVELOPER_COMMAND
- Sygnaly przeplywaja przez Information Flow Controller
- Format sygnałów zgodny ze standardem

### 13.3. Hierarchia Dokumentow

```
SSI_V5_MASTER_SYSTEM_FLOW_ARCHITECTURE.md (Podstawa)
├── 01_SYSTEM_SIGNAL_ARCHITECTURE.md (Sygnały)
│
└── 02_DEVELOPER_INPUT_ARCHITECTURE.md (Ten dokument)
    └── 03_PROMPT_MANAGEMENT_SYSTEM.md (Nastepny)
```

---

## 14. PRZYKLADY UZYCIA

### 14.1. Przyklad 1: Pobierz Status Systemu

```bash
# Komenda
system:status

# Przeplyw
1. Developer Interface: Parsuje komende
2. Command Processor: Buduje drzewo polecen
3. Governance: Waliduje uprawnienia (READ_ONLY wystarcza)
4. Information Flow Controller: Konwertuje do sygnalu
5. Orchestrator: Przekazuje do RuntimeController
6. RuntimeController: Wykonuje i zwraca status

# Odpowiedz
[SUCCESS] system:status
{
  "status": "RUNNING",
  "mode": "production",
  "cycle_count": 42,
  "uptime": "02:30:15",
  "agents_active": 6,
  "memory_usage": "45%"
}
```

### 14.2. Przyklad 2: Utworz Nowa Strategie

```bash
# Komenda
strategy:create agent=01 type=experimental name="Testowa Strategia" 
  description="Test nowej koncepcji decyzyjnej"

# Przeplyw
1. Developer Interface: Parsuje komende z parametrami
2. Command Processor: Weryfikuje zaleznosci (agent 01 musi byc aktywny)
3. Governance: Sprawdza uprawnienia (ADVANCED minimum)
4. Information Flow Controller: Route do StrategyLaboratory
5. Orchestrator: Synchronizuje z cyklem systemu
6. StrategyLaboratory: Tworzy nowa strategie

# Odpowiedz
[SUCCESS] strategy:create
{
  "strategy_id": "strat_experimental_001",
  "agent_id": "01",
  "type": "experimental",
  "status": "CREATED",
  "ready_for_test": false
}
```

### 14.3. Przyklad 3: Eksport Pamieci Agenta

```bash
# Komenda
agent:memory 01 export type=BEHAVIOR format=json file=behavior_backup_01.json

# Przeplyw
1. Developer Interface: Parsuje komende
2. Command Processor: Sprawdza dostepnosc agenta 01
3. Governance: Waliduje uprawnienia (ADVANCED)
4. Information Flow Controller: Route do AgentManager
5. Orchestrator: Czeka na koniec bieżącego cyklu
6. AgentManager: Pobiera pamiec od Agenta 01

# Odpowiedz
[SUCCESS] agent:memory
{
  "agent_id": "01",
  "memory_type": "BEHAVIOR",
  "export_format": "json",
  "file_path": "behavior_backup_01.json",
  "record_count": 150,
  "export_time_ms": 850
}
```

### 14.4. Przyklad 4: Blad - Brak Uprawnien

```bash
# Komenda (uzytkownik ma tylko READ_ONLY)
agent:activate 01

# Przeplyw
1. Developer Interface: Parsuje komende
2. Command Processor: Buduje drzewo
3. Governance: Sprawdza uprawnienia
   └── Pozniom: READ_ONLY
   └── Wymagany: ADVANCED
   └── Decision: ACCESS_DENIED

# Odpowiedz
[FAILED] agent:activate 01
Error: ACCESS_DENIED (ERR_005)
Required permission level: ADVANCED
Current level: READ_ONLY
Suggestion: Contact administrator for permission upgrade
```

---

## 15. TESTOWANIE I WALIDACJA

### 15.1. Test Cases

| ID | Scenariusz | Spodziewany Wynik | Status |
|----|-----------|-------------------|--------|
| DEV-001 | system:status (READ_ONLY) | SUCCESS + status JSON | ✅ |
| DEV-002 | agent:list (READ_ONLY) | SUCCESS + lista agentow | ✅ |
| DEV-003 | agent:activate 01 (BASIC) | SUCCESS | ✅ |
| DEV-004 | strategy:create (ADVANCED) | SUCCESS | ✅ |
| DEV-005 | strategy:create (READ_ONLY) | FAILED (ACCESS_DENIED) | ✅ |
| DEV-006 | system:stop (BASIC, Production) | FAILED (POLICY) | ✅ |
| DEV-007 | unknown:command | FAILED (UNKNOWN_COMMAND) | ✅ |
| DEV-008 | agent:status 99 | FAILED (INVALID_PARAMETER) | ✅ |

### 15.2. Validation Rules

- [ ] Kazda komenda ma poprawna syntax
- [ ] Wszystkie wymagane parametry sa podane
- [ ] Parametry maja poprawne typy i zakresy
- [ ] Uzytkownik ma odpowiednie uprawnienia
- [ ] Polecenie jest zgodne z politykami systemowymi
- [ ] Modul docelowy jest dostepny

---

## 16. PODSUMOWANIE

**Developer Input Architecture** zapewnia:

1. **Bezpieczne wejscie** programisty do systemu SSI V5
2. **Izolacje** od bezposredniego dostepu do modulow
3. **Kontrole dostepu** i walidacje na wieluziomach
4. **Jednolity interfejs** dla wszystkich operacji
5. **Pelne monitorowanie** i logowanie
6. **Zgodnosc z** Master System Flow i System Signal Architecture

**ZASADA FUNDAMENTALNA:** Programista NIE komunikuje sie bezposrednio z modulami.

**Przeplyw:** PROGRAMISTA -> Developer Command Interface -> Governance Validation -> Information Flow Controller -> Orchestrator -> Modul

---

**Data utworzenia:** 2026-08-01  
**Wersja:** 1.0.0  
**Status:** DRAFT - Gotowy do przegladu  
**Autor:** Mistral Vibe - CLI Coding Agent  
**Nastepny dokument:** 03_PROMPT_MANAGEMENT_SYSTEM.md  

---

**Powiazane Dokumenty:**
- SSI_V5_MASTER_SYSTEM_FLOW_ARCHITECTURE.md
- 01_SYSTEM_SIGNAL_ARCHITECTURE.md
- 03_PROMPT_MANAGEMENT_SYSTEM.md (następny)
