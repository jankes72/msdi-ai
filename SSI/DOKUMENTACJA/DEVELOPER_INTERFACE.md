# DEVELOPER INTERFACE - SSI V5 Phase 2 Design

**Wersja:** 1.0.0  
**Data:** 2026-07-31  
**Status:** PROJEKT FAZY 2 (Przed implementacją)  
**Autor:** SSI V5 Architecture Team  

---

## 📋 SPIS TREŚCI

1. [Przegląd Developer Interface](#1-przegląd-developer-interface)
2. [Architektura Interfejsu](#2-architektura-interfejsu)
3. [Typy Poleceń](#3-typy-poleceń)
4. [API Developer Interface](#4-api-developer-interface)
5. [Przykłady Użycia](#5-przykłady-użycia)
6. [BEzpieczeństwo i Autoryzacja](#6-bezpieczeństwo-i-autoryzacja)
7. [Pliki i Struktur](#7-pliki-i-struktura)

---

## 1. Przegląd Developer Interface

### 1.1 Cel

**Developer Interface** (DI) jest specjalnym wejściem do systemu SSI V5, które umożliwia programiście:

- **Testowanie systemu** bez wpływu na normalne działanie
- **Wymuszanie działań** na agentach i modułach
- **Uruchamianie modułów** na żądanie
- **Badanie pamięci** (odczyt, modyfikacja, eksport)
- **Generowanie modeli** i konfiguracji

### 1.2 Zasady

- **Oddzielone od normalnego procesu** - DI nie wpływa na autonomiczną pracę agentów
- **Pełna kontrola** - Programista może wykonywać dowolne operacje
- **Audyt** - Wszystkie działania są rejestrowane
- **Bezpieczeństwo** - Tylko uprawnieni użytkownicy

### 1.3 Funkcje

| **Kategoria** | **Funkcje** | **Opis** |
|---------------|-------------|----------|
| System | start, stop, pause, resume, status | Kontrola cyklu życia systemu |
| Agenci | run, force_decision, set_strategy, test | Kontrola indywidualnych agentów |
| Pamięć | read, write, modify, clear, export, import | Operacje na pamięci agentów |
| Kolektory | run, get_data, test, enable, disable | Kontrola kolektorów danych |
| CCL | status, vote, conflicts, consensus | Kontrola warstwy kolektywnej |
| Modele | create, register, test, performance | Zarządzanie modelami |

---

## 2. Architektura Interfejsu

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DEVELOPER INTERFACE ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         PROGRAMISTA                                       │   │
│  └───────────────────────────┬───────────────────────────────────────────┘   │
│                              │                                               │
│              ┌───────────────────┼───────────────────┐                       │
│              ▼                   ▼                   ▼                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    DeveloperConsole                                    │   │
│  │  GŁÓWNY INTERFEJS PROGRAMISTY                                         │   │
│  │                                                                     │   │
│  │  - parse_command()      - Parsowanie poleceń                          │   │
│  │  - validate_command()   - Walidacja poleceń                          │   │
│  │  - authorize_command()  - Autoryzacja poleceń                         │   │
│  │  - execute_command()    - Wykonanie poleceń                           │   │
│  │  - get_history()        - Pobranie historii poleceń                   │   │
│  └───────────────────┬───────────────────────────────────────────────────┘   │
│                      │                                                   │
│                      ▼                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    CommandExecutor                                     │   │
│  │  WYKONYWANIE POLECEŃ                                                  │   │
│  │                                                                     │   │
│  │  System Commands:       Agent Commands:           Memory Commands:   │   │
│  │  - start_system          - run_agent               - read_memory     │   │
│  │  - stop_system           - force_decision          - write_memory    │   │
│  │  - pause_system          - set_strategy            - modify_memory   │   │
│  │  - resume_system         - get_agent_status        - clear_memory    │   │
│  │  - get_status            - test_agent              - export_memory   │   │
│  │  - run_cycle             - enable_agent            - import_memory   │   │
│  │  - save_state            - disable_agent           - memory_stats    │   │
│  │  - load_state                                                      │   │
│  │                                                                     │   │
│  │  Collector Commands:    CCL Commands:              Model Commands:   │   │
│  │  - run_collector         - get_ccl_status         - create_model    │   │
│  │  - get_collector_data    - get_collaboration       - register_model   │   │
│  │  - test_collector        - get_conflicts          - test_model      │   │
│  │  - enable_collector      - get_consensus          - get_performance  │   │
│  │  - disable_collector     - initiate_vote                            │   │
│  └───────────────────┬───────────────────────────────────────────────────┘   │
│                      │                                                   │
│                      ▼                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    AuditLogger                                         │   │
│  │  REJESTROWANIE DZIAŁAŃ PROGRAMISTY                                   │   │
│  │                                                                     │   │
│  │  - log_command()       - Rejestracja polecenia i wyniku             │   │
│  │  - get_logs()          - Pobranie logów                              │   │
│  │  - clear_logs()        - Wyczyszczenie logów                         │   │
│  │  - export_logs()        - Eksport logów                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Typy Poleceń

### 3.1 System Commands

| **Polecenie** | **Opis** | **Parametry** | **Przykład** |
|---------------|----------|---------------|--------------|
| `system start` | Uruchomienie systemu | - | `system start` |
| `system stop` | Zatrzymanie systemu | - | `system stop` |
| `system pause` | Pauzowanie systemu | - | `system pause` |
| `system resume` | Wznowienie systemu | - | `system resume` |
| `system status` | Pobranie statusu systemu | - | `system status` |
| `system run_cycle` | Wykonywanie N cykli | `cycles` (int) | `system run_cycle 5` |
| `system save_state` | Zapis stanu systemu | `state_type` (str) | `system save_state full` |
| `system load_state` | Załadowanie stanu systemu | `state_type` (str) | `system load_state full` |

### 3.2 Agent Commands

| **Polecenie** | **Opis** | **Parametry** | **Przykład** |
|---------------|----------|---------------|--------------|
| `agent {id} run` | Uruchomienie agenta | `data` (str) | `agent 01 run all` |
| `agent {id} force_decision` | Wymuszenie decyzji | `decision` (str), `confidence` (float) | `agent 01 force_decision choice_a 0.9` |
| `agent {id} set_strategy` | Ustawienie strategii | `strategy` (str) | `agent 01 set_strategy analytical` |
| `agent {id} get_status` | Pobranie statusu agenta | - | `agent 01 get_status` |
| `agent {id} test` | Testowanie agenta | `test_type` (str) | `agent 01 test basic` |
| `agent {id} enable` | Włączenie agenta | - | `agent 01 enable` |
| `agent {id} disable` | Wyłączenie agenta | - | `agent 01 disable` |

### 3.3 Memory Commands

| **Polecenie** | **Opis** | **Parametry** | **Przykład** |
|---------------|----------|---------------|--------------|
| `memory {id} read` | Odczyt pamięci agenta | `memory_type` (str), `entry_id` (str) | `memory 01 read history` |
| `memory {id} write` | Zapis do pamięci | `memory_type` (str), `data` (dict) | `memory 01 write strategy {"name": "new_strategy"}` |
| `memory {id} modify` | Modyfikacja pamięci | `memory_type` (str), `entry_id` (str), `updates` (dict) | `memory 01 modify history hist_001 {"success": true}` |
| `memory {id} clear` | Wyczyszczenie pamięci | `memory_type` (str) | `memory 01 clear all` |
| `memory {id} export` | Eksport pamięci | `path` (str) | `memory 01 export /backup/agent_01.json` |
| `memory {id} import` | Import pamięci | `path` (str) | `memory 01 import /backup/agent_01.json` |
| `memory {id} stats` | Statystyki pamięci | - | `memory 01 stats` |

### 3.4 Collector Commands

| **Polecenie** | **Opis** | **Parametry** | **Przykład** |
|---------------|----------|---------------|--------------|
| `collector {name} run` | Uruchomienie collectora | - | `collector v2 run` |
| `collector {name} get_data` | Pobranie danych | - | `collector v3 get_data` |
| `collector {name} test` | Testowanie collectora | - | `collector v4 test` |
| `collector {name} enable` | Włączanie collectora | - | `collector external enable` |
| `collector {name} disable` | Wyłączanie collectora | - | `collector external disable` |

### 3.5 CCL Commands

| **Polecenie** | **Opis** | **Parametry** | **Przykład** |
|---------------|----------|---------------|--------------|
| `ccl status` | Status CCL | - | `ccl status` |
| `ccl collaboration_matrix` | Macierz współpracy | - | `ccl collaboration_matrix` |
| `ccl conflicts` | Lista konfliktów | - | `ccl conflicts` |
| `ccl consensus` | Historia konsensusów | - | `ccl consensus` |
| `ccl initiate_vote` | Inicjowanie głosowania | `topic`, `proposal`, `deadline` | `ccl initiate_vote strategy "Use analytical" 5` |
| `ccl recommendations` | Zalecenia CCL | - | `ccl recommendations` |

### 3.6 Model Commands

| **Polecenie** | **Opis** | **Parametry** | **Przykład** |
|---------------|----------|---------------|--------------|
| `model create` | Tworzenie nowego modelu | `name`, `type`, `parameters` | `model create v2_new prediction {"version": "2.0"}` |
| `model register` | Rejestracja modelu | `name`, `path` | `model register v2_new /models/v2_new.py` |
| `model test` | Testowanie modelu | `name`, `test_data` | `model test v2_new {"input": "test"}` |
| `model performance` | Wydajność modelu | `name` | `model performance v2_new` |

---

## 4. API Developer Interface

### 4.1 Metody Główne

```python
# Inicjalizacja
from SSI.v5.developer import DeveloperConsole

# Utworzenie konsoli (w runtime_controller.py)
developer_console = DeveloperConsole(runtime_controller)

# Wykonanie polecenia (string)
result = developer_console.execute_command("system status")

# Wykonanie polecenia (dict)
result = developer_console.execute_command({
    "type": "agent",
    "target": "01",
    "action": "force_decision",
    "args": {
        "decision": "choice_a",
        "confidence": 0.9
    }
})

# Pobranie historii
history = developer_console.get_history(limit=10)

# Pobranie logów audytu
audit_logs = developer_console.audit_logger.get_logs()
```

### 4.2 Format Polecenia (Dict)

```python
{
    "type": "system" | "agent" | "memory" | "collector" | "ccl" | "model",
    "target": "01" | "02" | ... | "v2" | "v3" | "all",
    "action": "start" | "stop" | "run" | "force_decision" | ...,
    "args": {
        # Parametry specyficzne dla polecenia
        "param1": "value1",
        "param2": 123
    }
}
```

### 4.3 Format Wyniku

```python
{
    "success": True | False,
    "data": { ... },  # Wynik polecenia (jeśli sukces)
    "error": "...",    # Błąd (jeśli niepowodzenie)
    "timestamp": "2026-07-31T12:00:00Z",
    "command": { ... }  # Oryginalne polecenie
}
```

### 4.4 Błędy

| **Kod Błędu** | **Opis** | **Przyczyna** |
|---------------|----------|--------------|
| `INVALID_COMMAND` | Nieprawidłowe polecenie | Błędny format lub nieznane polecenie |
| `UNAUTHORIZED` | Brak autoryzacji | Programista nie ma uprawnień |
| `AGENT_NOT_FOUND` | Agent nie istnieje | Błędny identyfikator agenta |
| `MEMORY_ERROR` | Błąd pamięci | Problem z odczytem/zapisem pamięci |
| `COLLECTOR_ERROR` | Błąd collectora | Problem z kolektorem danych |
| `INTERNAL_ERROR` | Błąd wewnętrzny | Wyjątek w systemie |

---

## 5. Przykłady Użycia

### 5.1 Podstawowe Polecenia Systemowe

```python
# Uruchomienie systemu
result = developer_console.execute_command("system start")
# {"success": True, "data": {"status": "started"}}

# Pobranie statusu
result = developer_console.execute_command("system status")
# {"success": True, "data": {... stan systemu ...}}

# Zatrzymanie systemu
result = developer_console.execute_command("system stop")
# {"success": True, "data": {"status": "stopped"}}
```

### 5.2 Kontrola Agentów

```python
# Wymuszenie decyzji agenta 01
result = developer_console.execute_command(
    "agent 01 force_decision high_confidence_choice 0.95"
)
# {"success": True, "data": {"agent_id": "01", "decision": {...}}}

# Ustawienie strategii
result = developer_console.execute_command(
    "agent 02 set_strategy aggressive"
)
# {"success": True, "data": {"agent_id": "02", "strategy": "aggressive"}}

# Pobranie statusu agenta
result = developer_console.execute_command("agent 03 get_status")
# {"success": True, "data": {"status": "IDLE", "strategy": "analytical", ...}}
```

### 5.3 Operacje na Pamięci

```python
# Odczyt pamięci historii agenta 01
result = developer_console.execute_command("memory 01 read history")
# {"success": True, "data": [ {... wpisy historii ...} ]}

# Modyfikacja wpisu historii
result = developer_console.execute_command(
    "memory 01 modify history hist_001 {'success': True, 'evaluation': 0.9}"
)
# {"success": True, "data": {"entry_id": "hist_001", "updated": True}}

# Statystyki pamięci
result = developer_console.execute_command("memory 01 stats")
# {"success": True, "data": {"personality": 1, "behavior": 5, "strategy": 3, ...}}
```

### 5.4 Kontrola Kolektorów

```python
# Uruchomienie collectora V2
result = developer_console.execute_command("collector v2 run")
# {"success": True, "data": {"collector": "v2", "result": {...}}}

# Pobranie danych z V3
result = developer_console.execute_command("collector v3 get_data")
# {"success": True, "data": {... dane V3 ...}}
```

### 5.5 Kontrola CCL

```python
# Pobranie macierzy współpracy
result = developer_console.execute_command("ccl collaboration_matrix")
# {"success": True, "data": {"01": {"02": 0.8, ...}, ...}}

# Inicjowanie głosowania
result = developer_console.execute_command(
    "ccl initiate_vote prediction_strategy 'Use analytical for next cycle' 10"
)
# {"success": True, "data": {"vote_id": "vote_20260731120000", ...}}
```

---

## 6. Bezpieczeństwo i Autoryzacja

### 6.1 Model Autoryzacji

```python
class AuthorizationModel:
    """Model autoryzacji dla Developer Interface."""
    
    # Poziomy dostępu
    LEVEL_READ = "read"       # Tylko odczyt
    LEVEL_WRITE = "write"     # Odczyt i zapis
    LEVEL_ADMIN = "admin"     # Pełna kontrola
    
    # Zasady dostępu
    ACCESS_RULES = {
        "system": {
            "start": LEVEL_ADMIN,
            "stop": LEVEL_ADMIN,
            "pause": LEVEL_ADMIN,
            "resume": LEVEL_ADMIN,
            "status": LEVEL_READ,
            "run_cycle": LEVEL_WRITE,
            "save_state": LEVEL_WRITE,
            "load_state": LEVEL_WRITE
        },
        "agent": {
            "run": LEVEL_WRITE,
            "force_decision": LEVEL_ADMIN,
            "set_strategy": LEVEL_WRITE,
            "get_status": LEVEL_READ,
            "test": LEVEL_WRITE,
            "enable": LEVEL_ADMIN,
            "disable": LEVEL_ADMIN
        },
        "memory": {
            "read": LEVEL_READ,
            "write": LEVEL_WRITE,
            "modify": LEVEL_WRITE,
            "clear": LEVEL_ADMIN,
            "export": LEVEL_READ,
            "import": LEVEL_WRITE,
            "stats": LEVEL_READ
        },
        "collector": {
            "run": LEVEL_WRITE,
            "get_data": LEVEL_READ,
            "test": LEVEL_WRITE,
            "enable": LEVEL_ADMIN,
            "disable": LEVEL_ADMIN
        },
        "ccl": {
            "status": LEVEL_READ,
            "collaboration_matrix": LEVEL_READ,
            "conflicts": LEVEL_READ,
            "consensus": LEVEL_READ,
            "initiate_vote": LEVEL_WRITE,
            "recommendations": LEVEL_READ
        }
    }
```

### 6.2 Uwierzytelnianie

```python
class DeveloperAuthenticator:
    """Uwierzytelnianie programisty."""
    
    def __init__(self):
        self.users = {
            "admin": {"password": "...", "level": "admin"},
            "developer": {"password": "...", "level": "write"},
            "analyst": {"password": "...", "level": "read"}
        }
        self.session_tokens = {}
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Uwierzytelnianie użytkownika."""
        if username in self.users and self.users[username]["password"] == password:
            token = self._generate_token(username)
            self.session_tokens[token] = {
                "username": username,
                "level": self.users[username]["level"],
                "expires": datetime.now() + timedelta(hours=1)
            }
            return token
        return None
    
    def authorize(self, token: str, command_type: str, action: str) -> bool:
        """Sprawdzenie autoryzacji."""
        if token not in self.session_tokens:
            return False
        
        session = self.session_tokens[token]
        user_level = session["level"]
        required_level = AuthorizationModel.ACCESS_RULES.get(
            command_type, {}
        ).get(action, AuthorizationModel.LEVEL_ADMIN)
        
        # Hierarchia poziomów: read < write < admin
        levels = [AuthorizationModel.LEVEL_READ, 
                 AuthorizationModel.LEVEL_WRITE, 
                 AuthorizationModel_LEVE
        
        return levels.index(user_level) >= levels.index(required_level)
```

### 6.3 Integracja z DeveloperConsole

```python
class DeveloperConsole:
    def __init__(self, runtime_controller: SSIRuntimeController):
        self.runtime_controller = runtime_controller
        self.command_executor = CommandExecutor(runtime_controller)
        self.audit_logger = AuditLogger()
        self.authenticator = DeveloperAuthenticator()
        self.current_token = None
        self.current_user = None
    
    def login(self, username: str, password: str) -> bool:
        """Logowanie programisty."""
        token = self.authenticator.authenticate(username, password)
        if token:
            self.current_token = token
            self.current_user = username
            return True
        return False
    
    def logout(self) -> None:
        """Wylogowanie."""
        self.current_token = None
        self.current_user = None
    
    def execute_command(self, command: Union[str, Dict]) -> Dict:
        """Wykonywanie polecenia z autoryzacją."""
        if not self.current_token:
            return {"success": False, "error": "Not authenticated"}
        
        parsed = self._parse_command(command)
        
        # Sprawdzenie autoryzacji
        if not self._check_authorization(parsed):
            return {"success": False, "error": "Unauthorized"}
        
        # Walidacja i wykonanie
        return super().execute_command(command)
    
    def _check_authorization(self, command: Dict) -> bool:
        """Sprawdzenie autoryzacji dla polecenia."""
        cmd_type = command.get("type", "system")
        action = command.get("action", "status")
        
        return self.authenticator.authorize(
            self.current_token, cmd_type, action
        )
```

---

## 7. Pliki i Struktur

### 7.1 Struktura Katalogów

```
SSI/
├── v5/
│   └── developer/
│       ├── __init__.py
│       ├── console.py          # Główna konsola
│       ├── command_executor.py # Wykonanie poleceń
│       ├── audit_logger.py     # Logowanie działań
│       ├── authenticator.py    # Uwierzytelnianie
│       └── commands/           # Definicje poleceń
│           ├── __init__.py
│           ├── system_commands.py
│           ├── agent_commands.py
│           ├── memory_commands.py
│           ├── collector_commands.py
│           ├── ccl_commands.py
│           └── model_commands.py
│
└── memory/
    └── developer/
        └── developer_log.json   # Log działań programisty
```

### 7.2 Pliki Generowane

| **Ścieżka** | **Kto tworzy** | **Kiedy powstaje** | **Zawartość** |
|--------------|----------------|-------------------|---------------|
| `SSI/memory/developer/developer_log.json` | AuditLogger | Po każdym poleceniu | Historia działań programisty |
| `SSI/memory/developer/session_{token}.json` | Authenticator | Przy logowaniu | Informacje o sesji |

### 7.3 Pliki Konfiguracyjne

| **Ścieżka** | **Format** | **Opis** |
|--------------|-----------|----------|
| `SSI/v5/developer/users.json` | JSON | Lista użytkowników i haseł (zahashowanych) |
| `SSI/v5/developer/access_rules.json` | JSON | Reguły dostępu i poziomy uprawnień |

---

## 📌 Podsumowanie

Dokument **DEVELOPER_INTERFACE.md** definiuje:

- ✅Architekturę interfejsu programisty
- ✅Typy poleceń (System, Agent, Memory, Collector, CCL, Model)
- ✅API z metodami i formatami
- ✅Przykłady użycia
- ✅System autoryzacji i uwierzytelniania
- ✅Strukturę plików

**Następne kroki:**
1. Utworzenie PHASE_2_IMPLEMENTATION_PLAN.md
2. Aktualizacja PROJECT_JOURNAL_V5.md
3. Utworzenie PHASE_2_DESIGN_REPORT.md

---

**Dokument podpisany cyfrowo:** SSI V5 Architecture Team  
**Data utrwalenia:** 2026-07-31  
**Wersja systemu:** Sprint 11.5 + Phase 2 Design
