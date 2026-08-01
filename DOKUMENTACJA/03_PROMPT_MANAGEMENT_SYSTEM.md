# 03 - PROMPT MANAGEMENT SYSTEM

**Data utworzenia:** 2026-08-01  
**Wersja:** 1.0.0  
**Status:** DRAFT  
**Autor:** Mistral Vibe - CLI Coding Agent  
**Typ dokumentu:** SYSTEM ZARZADZANIA PROMPTAMI  
**Zaleznosc:**
- SSI_V5_MASTER_SYSTEM_FLOW_ARCHITECTURE.md (podstawa)
- 01_SYSTEM_SIGNAL_ARCHITECTURE.md (sygnaly)
- 02_DEVELOPER_INPUT_ARCHITECTURE.md (wejscie programisty)

---

## 1. PODSUMOWANIE EXECUTIVE

Ten dokument definiuje **Prompt Management System** - system zarzadzania promptami w SSI V5. System zapewnia centralne repozytorium, wersjonowanie, kategoryzacje i monitorowanie uzycia promptow przez wszystkie moduly systemu.

**Kluczowe cechy:**
- Centralne repozytorium promptow
- Kategoryzacja: system_prompts, agent_prompts, developer_prompts, laboratory_prompts
- Pełne wersjonowanie i historia zmian
- Monitoring zuzycia i efektywnosci
- Integracja z Developer Input Architecture

---

## 2. GLOWNE KONCEPCJE

### 2.1. Definicja Promptu
**Prompt** to strukturyzowane zapytanie lub instrukcja dla modelu LLM, zawierajaca:
- **Cel:** Co ma osiagac
- **Kontekst:** Informacje tla
- **Instrukcje:** Sposob wykonania
- **Variables:** Parametry dynamiczne
- **Constraints:** Ograniczenia i wymagania

### 2.2. Zasady Systemu

1. **Zasada Unikalnosci:** Kazdy prompt ma unikalny identyfikator
2. **Zasada Wersjonowania:** Kazda zmiana tworzy nowa wersje
3. **Zasada Kategoryzacji:** Kazdy prompt nalezy do okreslonej kategorii
4. **Zasada Autentycznosci:** Autorstwo jest sledzone
5. **Zasada Monitorowania:** Kazde uzycie jest logowane

### 2.3. Kategorie Promptow

| Kategoria | Opis | Uzycie | Przyklady |
|-----------|------|--------|----------|
| **system_prompts** | Prompty systemowe | Operacje systemowe | Decyzje, analiza, zarzadzanie |
| **agent_prompts** | Prompty dla agentow | Cykl pracy agentow | Analiza, predykcja, decyzja |
| **developer_prompts** | Prompty programisty |Operacje developerskie | Tworzenie, testowanie, debugowanie |
| **laboratory_prompts** | Prompty laboratoryjne | Badania i eksperymenty | Testy, symulacje, ocena |

---

## 3. ARCHITEKTURA SYSTEMU

### 3.1. High-Level View

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PROMPT MANAGEMENT SYSTEM                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    PROMPT REPOSITORY                                    │    │
│  │  Centralne przechowywanie wszystkich promptow                         │    │
│  │                                                                         │    │
│  │  ┌─────────────────────┐  ┌─────────────────────┐                      │    │
│  │  │    system_prompts    │  │    agent_prompts     │                      │    │
│  │  │  - Decyzje           │  │  - Analiza           │                      │    │
│  │  │  - Zarzadzanie       │  │  - Predykcja         │                      │    │
│  │  │  - Monitorowanie     │  │  - Decyzja           │                      │    │
│  │  └─────────────────────┘  └─────────────────────┘                      │    │
│  │                                                                         │    │
│  │  ┌─────────────────────┐  ┌─────────────────────┐                      │    │
│  │  │  developer_prompts   │  │  laboratory_prompts  │                      │    │
│  │  │  - Tworzenie         │  │  - Testy             │                      │    │
│  │  │  - Debugowanie       │  │  - Symulacje         │                      │    │
│  │  │  - Analiza           │  │  - Ocena             │                      │    │
│  │  └─────────────────────┘  └─────────────────────┘                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                          │                                    │
│                                          ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    PROMPT MANAGER                                     │    │
│  │  Glowny zarzadca systemu promptow                                   │    │
│  │                                                                         │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │    │
│  │  │ Version Control  │  │ Category Manager │  │ Usage Monitor    │          │    │
│  │  │ - Wersjonowanie  │  │ - Kategoryzacja   │  │ - Monitorowanie   │          │    │
│  │  │ - Historia zmian │  │ - Weryfikacja     │  │ - Statystyki     │          │    │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                          │                                    │
│                                          ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    PROMPT SERVICE                                      │    │
│  │  Interfejs dostepowy dla uzytkownikow systemu                        │    │
│  │                                                                         │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │    │
│  │  │ Prompt API      │  │ Developer        │  │ Agent Interface  │          │    │
│  │  │ - REST API       │  │ Interface        │  │ - Hana LLM       │          │    │
│  │  │ - gRPC           │  │ (z 02_)         │  │ - Interakcja     │          │    │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                          │                                    │
│                                          ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    PROMPT USAGE LOGS                                   │    │
│  │  Historia uzycia i monitorowanie efektywnosci                         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2. Data Flow

```
Uzytkownik (Developer/Agent/System/Lab)
    │
    ▼
Prompt Service (API/Interface)
    │
    ▼
Prompt Manager
    ├── Version Control → Sprawdz wersje
    ├── Category Manager → Sprawdz kategorie
    └── Usage Monitor → Loguj uzycie
    │
    ▼
Prompt Repository
    ├── system_prompts/
    │   ├── prompt_001_v1.json
    │   ├── prompt_001_v2.json
    │   └── ...
    ├── agent_prompts/
    │   ├── decision_prompt_v1.json
    │   └── ...
    ├── developer_prompts/
    │   └── ...
    └── laboratory_prompts/
        └── ...
    │
    ▼
Prompt Usage Logs
    └── Rejestracja kazdego uzycia
```

---

## 4. STRUKTURA PROMPTA

### 4.1. Standardowy Format Prompta

```json
{
  "prompt_id": "UNIKALNY_ID",
  "version": "MAJOR.MINOR.PATCH",
  "category": "system|agent|developer|laboratory",
  "type": "instruction|question|analysis|generation|evaluation",
  "system_prompt": "<SYSTEM_INSTRUCTION>",
  "user_prompt": "<USER_INPUT_TEMPLATE>",
  "template": "<FULL_PROMPT_TEMPLATE>",
  "variables": {
    "<variable_name>": {
      "type": "string|number|boolean|json",
      "required": true|false,
      "default": "<default_value>",
      "description": "<variable_description>"
    }
  },
  "metadata": {
    "autor": "<AUTHOR_ID>",
    "created_timestamp": "<ISO8601_TIMESTAMP>",
    "last_modified": "<ISO8601_TIMESTAMP>",
    "modified_by": "<USER_ID>",
    "description": "<PROMPT_DESCRIPTION>",
    "purpose": "<PROMPT_PURPOSE>",
    "tags": ["<TAG1>", "<TAG2>", ...],
    "related_strategies": ["<STRATEGY_ID1>", "<STRATEGY_ID2>", ...],
    "related_agents": ["<AGENT_ID1>", "<AGENT_ID2>", ...],
    "status": "ACTIVE|DEPRECATED|ARCHIVED|DRAFT"
  },
  "examples": [
    {
      "input": { ... },
      "output": { ... },
      "explanation": "<EXPLANATION>"
    }
  ],
  "validation_rules": {
    "max_tokens": 4096,
    "temperature_range": [0, 1],
    "top_p_range": [0, 1],
    "response_format": "json|text|markdown"
  },
  "performance_metrics": {
    "avg_response_time_ms": 1500,
    "success_rate": 0.95,
    "quality_score": 0.88,
    "usage_count": 150
  },
  "dependencies": {
    "requires_models": ["<MODEL_ID1>", "<MODEL_ID2>"],
    "requires_memory": ["BEHAVIOR", "STRATEGY"],
    "requires_data": ["V2_DATA", "V3_KNOWLEDGE"]
  }
}
```

### 4.2. Pola Obowiazkowe

| Pole | Typ | Opis | Wymagane |
|------|-----|------|----------|
| prompt_id | string | Unikalny identyfikator | ✅ |
| version | string | Numer wersji (semver) | ✅ |
| category | enum | bulk: system, agent, developer, laboratory | ✅ |
| type | enum | Typ promptu | ✅ |
| template | string | Szablon promptu | ✅ |
| metadata.autor | string | Autor promptu | ✅ |
| metadata.created_timestamp | string | Data utworzenia | ✅ |
| metadata.description | string | Opis promptu | ✅ |

### 4.3. Pola Opcjonalne

| Pole | Typ | Opis | Domyślna |
|------|-----|------|----------|
| system_prompt | string | Instrukcja systemowa | "" |
| user_prompt | string | Instrukcja uzytkownika | "" |
| variables | object | Zmienne dynamiczne | {} |
| examples | array | Przyklady uzycia | [] |
| validation_rules | object | Reguly walidacji | {} |
| performance_metrics | object | Metryki wydajnosci | {} |
| dependencies | object | Zaleznosci | {} |

### 4.4. Przyklady Promptow

**Przyklad 1: Agent Decision Prompt (agent_prompts)**
```json
{
  "prompt_id": "agent_decision_01",
  "version": "1.2.0",
  "category": "agent",
  "type": "decision",
  "template": "Jestes agentem {agent_name} z osobowoscia: {personality}. Analizuj dostepne dane: {data_context}. Porownaj z historia: {history}. Podjdz decyzje: {decision_type}. Uzasadnij swoja decyzje. Odpowiedz w formacie JSON z polami: ['decision', 'confidence', 'reasoning', 'risk_assessment'].",
  "variables": {
    "agent_name": {"type": "string", "required": true, "description": "Nazwa agenta"},
    "personality": {"type": "json", "required": true, "description": "Wektor osobowosci"},
    "data_context": {"type": "json", "required": true, "description": "Dane do analizy"},
    "history": {"type": "json", "required": true, "description": "Historia agenta"},
    "decision_type": {"type": "string", "required": true, "description": "Typ decyzji"}
  },
  "metadata": {
    "autor": "system",
    "created_timestamp": "2026-01-01T00:00:00",
    "last_modified": "2026-07-30T10:00:00",
    "description": "Podstawowy prompt decyzyjny dla agentow",
    "purpose": "Podejmowanie decyzji na podstawie analizy",
    "tags": ["decision", "analysis", "reasoning"],
    "status": "ACTIVE"
  },
  "validation_rules": {
    "max_tokens": 2048,
    "response_format": "json"
  }
}
```

**Przyklad 2: Strategy Evaluation Prompt (laboratory_prompts)**
```json
{
  "prompt_id": "strategy_eval_01",
  "version": "2.1.0",
  "category": "laboratory",
  "type": "evaluation",
  "template": "Ocen nowa strategie: {strategy_description}. Przeanalizuj jej parametry: {parameters}. Porownaj z historia wynikow: {history}. Ocen skutecznosc na podstawie: [trafnosc, kurs, ryzyko, stabilnosc]. Wygeneruj ocene: [0-100]. Uzasadnij ocene. Zaproponuj poprawki jesli potrzeba.",
  "variables": {
    "strategy_description": {"type": "string", "required": true},
    "parameters": {"type": "json", "required": true},
    "history": {"type": "json", "required": true}
  },
  "metadata": {
    "autor": "system",
    "created_timestamp": "2026-02-01T00:00:00",
    "description": "Prompt do oceny strategii laboratoryjnych",
    "purpose": "Testowanie i ocena nowych strategii",
    "tags": ["strategy", "evaluation", "laboratory"],
    "status": "ACTIVE"
  },
  "validation_rules": {
    "max_tokens": 1024,
    "response_format": "json"
  }
}
```

**Przyklad 3: System Analysis Prompt (system_prompts)**
```json
{
  "prompt_id": "system_analysis_01",
  "version": "3.0.0",
  "category": "system",
  "type": "analysis",
  "system_prompt": "Jestes ekspertem w analizie systemow decyzyjnych.",
  "user_prompt": "Przeanalizuj stan systemu: {system_state}. Zidentyfikuj potencjalne problemy, optymalizacje i polepszenia. Odpowiedz w JSON.",
  "template": "Jestes ekspertem w analizie systemow decyzyjnych. Przeanalizuj stan systemu: {system_state}. Zidentyfikuj potencjalne problemy, optymalizacje i polepszenia. Odpowiedz w formacie JSON z polami: ['problems', 'optimizations', 'recommendations', 'priority'].",
  "variables": {
    "system_state": {"type": "json", "required": true, "description": "Aktualny stan systemu"}
  },
  "metadata": {
    "autor": "developer_01",
    "created_timestamp": "2026-03-01T00:00:00",
    "description": "Systemowy prompt do analizy stanu SSI V5",
    "purpose": "Diagnostyka i optymalizacja systemu",
    "tags": ["system", "analysis", "diagnostics"],
    "status": "ACTIVE"
  }
}
```

---

## 5. PROMPT REPOSITORY

### 5.1. Struktura Katalogu

```
DOKUMENTACJA/PROMPTS/
├── system_prompts/
│   ├── system_analysis_01_v1.0.0.json
│   ├── system_analysis_01_v2.0.0.json
│   ├── decision_optimization_01_v1.0.0.json
│   └── ...
├── agent_prompts/
│   ├── agent_decision_01_v1.2.0.json
│   ├── agent_prediction_01_v1.1.0.json
│   ├── agent_learning_01_v1.0.0.json
│   └── ...
├── developer_prompts/
│   ├── code_generation_01_v1.0.0.json
│   ├── debugging_01_v1.0.0.json
│   └── ...
├── laboratory_prompts/
│   ├── strategy_eval_01_v2.1.0.json
│   ├── simulation_01_v1.0.0.json
│   └── ...
├── ARCHIVE/
│   ├── system_prompts/
│   │   └── deprecated_prompts/
│   ├── agent_prompts/
│   │   └── deprecated_prompts/
│   └── ...
└── repository_index.json
```

### 5.2. Index Repozytorium

```json
{
  "version": "1.0.0",
  "last_updated": "2026-08-01T00:00:00",
  "categories": {
    "system_prompts": {
      "count": 15,
      "active": 12,
      "deprecated": 2,
      "archived": 1,
      "path": "system_prompts/"
    },
    "agent_prompts": {
      "count": 25,
      "active": 20,
      "deprecated": 3,
      "archived": 2,
      "path": "agent_prompts/"
    },
    "developer_prompts": {
      "count": 8,
      "active": 8,
      "deprecated": 0,
      "archived": 0,
      "path": "developer_prompts/"
    },
    "laboratory_prompts": {
      "count": 12,
      "active": 10,
      "deprecated": 1,
      "archived": 1,
      "path": "laboratory_prompts/"
    }
  },
  "total_prompts": 60,
  "stats": {
    "most_used": "agent_decision_01",
    "highest_rated": "strategy_eval_01",
    "recently_updated": "system_analysis_01"
  }
}
```

---

## 6. PROMPT MANAGER

### 6.1. Odpowiedzialnosc
- Zarzadzanie repozytorium promptow
- Kontrola wersji i historii
- Kategoryzacja i organizacja
- Monitorowanie uzycia
- Automatyczne archiwizowanie

### 6.2. Funkcje

**Version Control:**
- Tworzenie nowych wersji promptow
- Porownywanie wersji
- Cofanie zmian (rollback)
- Merge zmian miedzy wersjami

**Category Management:**
- Przypisywanie kategorii
- Zmiana kategorii
- Walidacja kategorii
- Statystyki po kategoriach

**Usage Monitoring:**
- Logowanie kazdego uzycia
- Statystyki uzycia
- Monitoring efektywnosci
- Alerty o problemach

### 6.3. Operacje

| Operacja | Opis | Parametry | Wynik |
|----------|------|-----------|-------|
| create | Utworz nowy prompt | prompt_data | prompt_id, version |
| read | Pobierz prompt | prompt_id, version | prompt_data |
| update | Zaktualizuj prompt | prompt_id, new_data | new_version |
| delete | Usun prompt | prompt_id | status |
| list | Lista promptow | category, status, tags | prompt_list |
| search | Szukaj promptow | query, filters | search_results |
| version:list | Lista wersji | prompt_id | version_list |
| version:rollback | Cofnij do wersji | prompt_id, version | status |
| stats | Statystyki | category, period | statistics |

---

## 7. PROMPT SERVICE

### 7.1. Interfejsy Dostepu

**1. REST API**
```
GET    /api/prompts/{category}              - Lista promptow
GET    /api/prompts/{category}/{prompt_id}  - Pobierz prompt
POST   /api/prompts/{category}              - Utworz prompt
PUT    /api/prompts/{category}/{prompt_id}  - Zaktualizuj prompt
DELETE /api/prompts/{category}/{prompt_id}  - Usun prompt

GET    /api/prompts/search                  - Szukaj promptow
GET    /api/prompts/stats                   - Statystyki
```

**2. gRPC Interface**
```protobuf
service PromptService {
  rpc CreatePrompt (CreatePromptRequest) returns (PromptResponse);
  rpc GetPrompt (GetPromptRequest) returns (PromptResponse);
  rpc UpdatePrompt (UpdatePromptRequest) returns (PromptResponse);
  rpc DeletePrompt (DeletePromptRequest) returns (StatusResponse);
  rpc ListPrompts (ListPromptsRequest) returns (PromptListResponse);
  rpc SearchPrompts (SearchPromptsRequest) returns (PromptListResponse);
  rpc GetPromptStats (StatsRequest) returns (PromptStatsResponse);
}
```

**3. Developer Interface (z 02_DEVELOPER_INPUT_ARCHITECTURE.md)**
```bash
# Tworzenie promptu
prompt:create type=agent category=decision autor=programista_01 \
  description=" polityka decyzyjna dla agentow"

# Aktualizacja promptu
prompt:update id=agent_decision_01 version=1.3.0 \
  description="Zaktualizowany opis"

# Lista promptow
prompt:list category=agent status=active

# Pobierz prompt
prompt:get id=agent_decision_01 version=latest

# Usun prompt
prompt:delete id=test_prompt_01

# Statystyki
prompt:stats category=laboratory period=7d
```

**4. Agent Interface**
Agenci uzyskuja dostep do promptow przez:
- PromptStore (skladnica promptow dla agentow)
- Dynamiczne wstrzykiwanie promptow
- Cache promptow dla wydajnosci

---

## 8. PROMPT LIFECYCLE

### 8.1. Cykl Zycia Prompta

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   DRAFT     │────▶│    ACTIVE    │────▶│  DEPRECATED  │────▶│   ARCHIVED  │
│             │     │             │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │                   │
      ▼                   ▼                   ▼                   ▼
  Tworzenie          Uzycie             Ostrzezenie          Archiwum
  i testowanie     produkcyjne       o przestarzalosc        dlugoterminowe
```

### 8.2. Transition Rules

| Z | Do | Warunek |
|---|----|---------|
| DRAFT | ACTIVE | Walidacja i akceptacja |
| ACTIVE | DEPRECATED | Nowa wersja dostepna |
| ACTIVE | ARCHIVED | Manualne archiwizowanie |
| DEPRECATED | ACTIVE | Powrot do starszej wersji |
| DEPRECATED | ARCHIVED | 30 dni bez uzycia |
| ARCHIVED | ACTIVE | Manualne przywracanie |

### 8.3. Versioning Rules

**Format wersji:** MAJOR.MINOR.PATCH
- MAJOR: Zmiany niekompatybilne wstecz
- MINOR: Nowe funkcjonalnosci (kompatybilne)
- PATCH: Poprawki bledow

**Zasady wersjonowania:**
1. kazda zmiana w templacie = nowy PATCH
2. Nowe zmienne = nowy MINOR
3. Zmiana typu/kategorii = nowy MAJOR
4. Wszystkie wersje sa zachowywane

---

## 9. PROMPT USAGE MONITORING

### 9.1. Usage Log Structure

```json
{
  "usage_id": "usage_001",
  "prompt_id": "agent_decision_01",
  "prompt_version": "1.2.0",
  "user_agent": "Agent_01",
  "user_type": "agent|developer|system|laboratory",
  "timestamp": "2026-08-01T12:00:00",
  "execution_time_ms": 1500,
  "tokens_used": 512,
  "response_length": 256,
  "status": "SUCCESS|FAILED|PARTIAL",
  "quality_score": 0.85,
  "feedback": {
    "user_rating": 4,
    "comment": "Dobra jakosc odpowiedzi",
    "suggestions": [""],
    "timestamp": "2026-08-01T12:05:00"
  },
  "context": {
    "cycle_number": 1,
    "decision_id": "dec_001",
    "session_id": "sess_001"
  }
}
```

### 9.2. Metryki Wydajnosci

| Metryka | Opis | Obliczanie |
|---------|------|------------|
| Usage Count | Liczba uzyc | Sumowanie |
| Success Rate | Odsetek sukcesow | SUCCESS / (SUCCESS + FAILED) |
| Avg Response Time | Sredni czas odpowiedzi | Srednia z execution_time_ms |
| Avg Quality Score | Srednia ocena jakosci | Srednia z quality_score |
| Token Usage | Zuzycie tokenow | Sumowanie tokens_used |
| Efficiency | Wydajnosc | Usage Count / Avg Response Time |

### 9.3. Monitorowane Alerty

| Alert | Warunek | Dzialanie |
|-------|---------|----------|
| Low Success Rate | Success Rate < 0.8 | Powiadom administratora |
| High Latency | Avg Response Time > 5s | Investigacja |
| High Token Usage | Tokens > 8000/cycle | Optymalizacja |
| No Usage | 0 uzyc w ostatnich 30 dniach | Candidacy for archival |
| Negative Feedback | >3 negatywne oceny | Review promptu |

---

## 10. PROMPT OPTIMIZATION

### 10.1. Automatyczna Optymalizacja

**1. Template Optimization:**
- usuwanie redundancji
- standaryzacja formatu
- optymalizacja dlugosci

**2. Caching:**
- Cache czesto uzywanych promptow
- Cache wyniki dla tych samych parametrow
- TTL cache: 1 godzina

**3. Load Balancing:**
- Rozklad uzyc promptow
- Unikanie overloadu pojedynczych promptow
- Priorytetyzacja promptow

### 10.2. Rekomendacje

**Dobre Praktyki:**
1. Uzywaj specyficznych instrukcji
2. Okreslaj role systemu
3. Zapewniaj kontekst
4. Uzywaj przykładów
5. Okreslaj oczekiwany format odpowiedzi

**Do Unikania:**
1. Zbyt ogolne prompty
2. Brak struktury
3. Zbyt dlugie instrukcje
4. Niejednoznacznosci
5. Brak walidacji

---

## 11. INTEGRACJA Z INNYMI SYSTEMAMI

### 11.1. Integracja z Agent System

Agenci uzyskuja dostep do promptow przez:
- **PromptStore**: Przechowuje prompty dla agentow
- **PromptSelector**: Wybiera najlepszy prompt dla zadania
- **PromptCache**: Zwieksza wydajnosc

**Przeplyw:**
```
Agent (01-06)
    │
    ▼
PromptStore
    │
    ▼
PromptSelector → Wybiera prompt na podstawie:
    ├── Typ zadania
    ├── Osobowosc agenta
    ├── Historia uzyc
    └── Preferencje agenta
    │
    ▼
PromptCache (jesli dostepny)
    │
    ▼
Prompt Execution → Wykonanie z uzyciem LLM
    │
    ▼
Response → Odpowiedz dla agenta
```

### 11.2. Integracja z Strategy Laboratory

Strategie laboratoryjne korzystaja z promptow:
- **Strategy Creation:** Uzycie laboratory_prompts do generowania nowych strategii
- **Strategy Testing:** Uzycie agent_prompts do testowania strategii
- **Strategy Evaluation:** Uzycie system_prompts do oceny strategii

### 11.3. Integracja z AI Lab

AI Laboratory uzywa promptow do:
- **Experiments:** Testowanie nowych koncepcji
- **Simulations:** Symulacja scenariuszy
- **Analysis:** Gleboka analiza danych

---

## 12. INTEGRACJA Z DOCUMENTAMI ARCHITEKTONICZNYMI

### 12.1. Powiazanie z Developer Input Architecture

**Zgodnosc z 02_DEVELOPER_INPUT_ARCHITECTURE.md:**
- Polecenia `prompt:*` sa czescia Developer Command Interface
- Uzytkownik moze zarzadzac promptami przez CLI
- Wszystkie operacje podlegaja Governance Validation

**Przeplyw polecen prompt:**
```
PROGRAMISTA
    → Developer Command Interface
        → Governance Validation
            → Information Flow Controller
                → Orchestrator
                    → Prompt Service
                        → Prompt Manager
                            → Prompt Repository
```

### 12.2. Powiazanie z System Signal Architecture

**Zgodnosc z 01_SYSTEM_SIGNAL_ARCHITECTURE.md:**
- Operacje na promptach generuja sygnaly PROMPT_*
- Sygnaly sa przetwarzane przez Information Flow Controller
- Format sygnałow zgodny ze standardem

**Sygnaly zwiazane z promptami:**
- PROMPT_CREATED: Nowy prompt utworzony
- PROMPT_UPDATED: Prompt zaktualizowany
- PROMPT_DELETED: Prompt usuniety
- PROMPT_READ: Prompt odczytany
- PROMPT_ERROR: Blad operacji na prompcie

### 12.3. Powiazanie z Master System Flow

**Zgodnosc z SSI_V5_MASTER_SYSTEM_FLOW_ARCHITECTURE.md:**
- Prompt Management System jest czescia Modułów Systemowych
- Integracja z Information Flow Controller
- Uzycie promptow w cyklu pracy agentow

---

## 13. HIERARCHIA DOKUMENTOW

```
SSI_V5_MASTER_SYSTEM_FLOW_ARCHITECTURE.md (Podstawa)
├── 01_SYSTEM_SIGNAL_ARCHITECTURE.md (Sygnały)
│
└── 02_DEVELOPER_INPUT_ARCHITECTURE.md (Wejscie Programisty)
    └── 03_PROMPT_MANAGEMENT_SYSTEM.md (Ten dokument)
        └── 04_AGENT_MEMORY_BEHAVIOR_EVOLUTION.md (Nastepny)
```

---

## 14. PRZYKLADY UZYCIA

### 14.1. Przyklad 1: Tworzenie Nowego Prompta

```bash
# Komenda programisty
prompt:create \
  type=agent \
  category=decision \
  autor=programista_01 \
  description="Prompt decyzyjny dla agresywnych strategii" \
  template="Jestes agentem {agent_name} o wysokiej tolerancji ryzyka. Analizuj {data}. Podjdz decyzje z uwzglednieniem wysokiego ryzyka. Odpowiedz w JSON." \
  variables.agent_name="string" \
  variables.data="json"

# Przeplyw
1. Walidacja polecenia (Governance)
2. Utworzenie nowego promptu w Prompt Repository
3. Przypisanie version 1.0.0
4. Zapis w system_prompts/ lub agent_prompts/
5. Potwierdzenie dla programisty

# Odpowiedz
[SUCCESS] prompt:create
{
  "prompt_id": "aggressive_decision_01",
  "version": "1.0.0",
  "category": "agent",
  "status": "DRAFT",
  "path": "agent_prompts/aggressive_decision_01_v1.0.0.json"
}
```

### 14.2. Przyklad 2: Uzycie Prompta przez Agenta

```
# Agent 01 otrzymuje zadanie
1. Agent 01 identyfikuje typ zadania: DECISION
2. PromptSelector wybiera prompt: agent_decision_01 v1.2.0
3. PromptStore dostarcza prompt
4. Agent 01 uzupełnia szablon:
   - agent_name: "Agent_01"
   - personality: {analysis: 0.9, caution: 0.85, curiosity: 0.6}
   - data_context: {match_data, course_data, history}
   - decision_type: "bet_placement"
5. LLM generuje odpowiedz w formacie JSON
6. Odpowiedz jest przetwarzana przez Agenta 01
7. Usage Monitor loguje uzycie

# Usage Log
{
  "usage_id": "usage_001",
  "prompt_id": "agent_decision_01",
  "prompt_version": "1.2.0",
  "user_agent": "Agent_01",
  "execution_time_ms": 1200,
  "tokens_used": 1024,
  "status": "SUCCESS",
  "context": {"cycle_number": 1, "decision_id": "dec_001"}
}
```

### 14.3. Przyklad 3: Aktualizacja i Wersjonowanie

```bash
# Aktualizacja promptu
prompt:update \
  id=agent_decision_01 \
  version=1.3.0 \
  template="Jestes agentem {agent_name}... [zaktualizowany szablon]" \
  description="Zaktualizowany prompt decyzyjny"

# Repozytorium po aktualizacji
agent_prompts/
├── agent_decision_01_v1.0.0.json  (stara wersja)
├── agent_decision_01_v1.1.0.json  (stara wersja)
├── agent_decision_01_v1.2.0.json  (stara wersja)
└── agent_decision_01_v1.3.0.json  (NOWA - ACTIVE)

# Statystyki
{
  "prompt_id": "agent_decision_01",
  "current_version": "1.3.0",
  "all_versions": ["1.0.0", "1.1.0", "1.2.0", "1.3.0"],
  "active_version": "1.3.0",
  "previous_versions": ["1.2.0"]
}
```

### 14.4. Przyklad 4: Statystyki i Monitoring

```bash
# Pobierz statystyki dla laboratory_prompts
prompt:stats category=laboratory period=30d

# Odpowiedz
[SUCCESS] prompt:stats
{
  "category": "laboratory",
  "period": "30d",
  "total_prompts": 12,
  "stats": {
    "total_usage": 450,
    "success_rate": 0.92,
    "avg_response_time_ms": 1800,
    "total_tokens_used": 250000,
    "top_prompts": [
      {"prompt_id": "strategy_eval_01", "usage": 150, "success_rate": 0.95},
      {"prompt_id": "simulation_01", "usage": 120, "success_rate": 0.88}
    ],
    "recent_usage": [
      {"timestamp": "2026-08-01", "count": 30, "avg_time_ms": 1750},
      {"timestamp": "2026-07-31", "count": 25, "avg_time_ms": 1800}
    ]
  },
  "alerts": []
}
```

---

## 15. TESTOWANIE I WALIDACJA

### 15.1. Test Cases

| ID | Scenariusz | Spodziewany Wynik | Status |
|----|-----------|-------------------|--------|
| PMP-001 | Tworzenie promptu | SUCCESS + prompt_id | ✅ |
| PMP-002 | Odczyt promptu | SUCCESS + prompt_data | ✅ |
| PMP-003 | Aktualizacja promptu | SUCCESS + new_version | ✅ |
| PMP-004 | Usuniecie promptu | SUCCESS | ✅ |
| PMP-005 | Lista promptow | SUCCESS + prompt_list | ✅ |
| PMP-006 | Szukanie promptow | SUCCESS + results | ✅ |
| PMP-007 | Wersjonowanie | SUCCESS + version_history | ✅ |
| PMP-008 | Uzycie promptu | SUCCESS + response | ✅ |
| PMP-009 | Statystyki | SUCCESS + statistics | ✅ |
| PMP-010 | Archiwizowanie | SUCCESS + moved to ARCHIVE | ✅ |

### 15.2. Validation Rules

- [ ] prompt_id jest unikalny
- [ ] version jest w formacie semver
- [ ] category jest jedna z: system, agent, developer, laboratory
- [ ] template nie jest pusty
- [ ] metadata.autor jest okreslony
- [ ] Wszystkie wymagane zmienne sa zdefiniowane
- [ ] response_format jest spójny z validation_rules

---

## 16. PODSUMOWANIE

**Prompt Management System** zapewnia:

1. **Centralne zarzadzanie** promptami dla calego systemu
2. **Pełne wersjonowanie** i historia zmian
3. **Kategoryzacje** i organizacje promptow
4. **Monitorowanie uzycia** i metryki wydajnosci
5. **Integracje** z innymi modulami SSI V5
6. **Bezpieczenstwo** i kontrole dostepu

**Kluczowe cechy:**
- Repozytorium z podziałem na Kategorie
- Cykl zycia promptow: DRAFT -> ACTIVE -> DEPRECATED -> ARCHIVED
- Wersjonowanie semver (MAJOR.MINOR.PATCH)
- Monitoring zycia i Alerty
- Integracja z Developer Input i Agent System

---

**Data utworzenia:** 2026-08-01  
**Wersja:** 1.0.0  
**Status:** DRAFT - Gotowy do przegladu  
**Autor:** Mistral Vibe - CLI Coding Agent  
**Nastepny dokument:** 04_AGENT_MEMORY_BEHAVIOR_EVOLUTION.md  

---

**Powiazane Dokumenty:**
- SSI_V5_MASTER_SYSTEM_FLOW_ARCHITECTURE.md
- 01_SYSTEM_SIGNAL_ARCHITECTURE.md
- 02_DEVELOPER_INPUT_ARCHITECTURE.md
- 04_AGENT_MEMORY_BEHAVIOR_EVOLUTION.md (nastepny)
