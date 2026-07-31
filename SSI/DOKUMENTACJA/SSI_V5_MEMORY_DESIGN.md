# SSI V5 MEMORY DESIGN

**Data utworzenia:** 2026-07-31  
**Wersja:** 1.0.0  
**Status:** PROJEKT  

---

## SPIS TRESCI

1. [WSTEP](#wstep)
2. [ZASADY PROJEKTOWANIA PAMIECI](#zasady-projektowania-pamieci)
3. [STRUKTURA PAMIECI](#struktura-pamieci)
4. [AGENT MEMORY - SZCZEGOLY](#agent-memory---szczegoly)
5. [COLLECTIVE MEMORY - SZCZEGOLY](#collective-memory---szczegoly)
6. [LONG TERM MEMORY - SZCZEGOLY](#long-term-memory---szczegoly)
7. [WORLD MEMORY](#world-memory)
8. [ENTRY STRUKTURY](#entry-struktury)
9. [INDEKSY I WYSZUKIWANIE](#indeksy-i-wyszukiwanie)
10. [PERSYSTENCJA](#persystencja)
11. [SYNCHRONIZACJA PAMIECI](#synchronizacja-pamieci)
12. [BACKUP I RECOVERY](#backup-i-recovery)

---

## WSTEP

System pamieci SSI V5 jest zaprojektowany aby:
- Przechowywać wszystkie istotne dane systemu
- Umożliwić szybkie wyszukiwanie i odczyt
- Zapewnić persistencje (trwalosc) danych
- Wspierac rozproszona i kolektywną pamięć
- Byc skalowalny i elastyczny

---

## ZASADY PROJEKTOWANIA PAMIECI

### 1. SEPARATION OF CONCERNS

Kazdy typ pamieci odpowiada za inna dziedzinę:
- **Agent Memory:** Indywidualna pamiec kazdego agenta
- **Collective Memory:** Wiedza wspólna wszystkich agentow
- **Long Term Memory:** Historyczna wiedza systemu
- **World Memory:** Aktualny stan świata

### 2. HIERARCHICAL ORGANIZATION

Pamiec zorganizowana jest hierarchicznie:
```
System Memory
├── Long Term Memory (LTM)
│   ├── Patterns
│   ├── Experience
│   └── Validated Knowledge
├── Collective Memory (CM)
│   ├── Knowledge
│   ├── Relations
│   ├── Conflicts
│   ├── Alliances
│   └── Consensus
├── World Memory (WM)
│   └── UnifiedInputPackage
└── Agent Memory (AM) x6
    ├── Agent_01
    │   ├── Personality
    │   ├── Behavior
    │   ├── Strategy
    │   ├── History
    │   ├── Relationship
    │   └── Prompt
    └── Agent_06
        └── ...
```

### 3. PRIVATE vs SHARED

| Typ | Zakres | Dostep |
|-----|--------|--------|
| Agent Memory | Per agent | Private (owner: read/write, CCL: read-only) |
| Collective Memory | System | Shared (all: read/write) |
| Long Term Memory | System | Shared (all: read, specialized: write) |
| World Memory | Global | Shared (all: read, Runtime: write) |

### 4. PERSISTENCE LEVELS

| Poziom | Opis | Implementacja |
|--------|------|---------------|
| L1 - In-Memory | Tymczasowa pamiec | Python objects |
| L2 - Disk | Trwala pamiec na dysku | JSON files |
| L3 - Backup | Kopia zapasowa | Compressed archives |
| L4 - Versioned | Historia zmian | Versioned files |

### 5. RETENTION POLICY

| Typ pamieci | Retention | Cleanup |
|-------------|-----------|---------|
| Personality | Forever | Never |
| Behavior | Forever | Never |
| Strategy | Forever | Never |
| History | Configurable | By date or count |
| Relationship | Forever | Never |
| Knowledge | Forever | Never |
| Relations | Forever | Never |
| Conflicts | Configurable | After resolution |
| Patterns | Forever | Never |
| Experience | Forever | Never |

---

## STRUKTURA PAMIECI

### STRUKTURA KATALOGOW

```
SSI/
├── memory/
│   ├── agents/
│   │   ├── agent_01/
│   │   │   ├── personality.json
│   │   │   ├── behavior.json
│   │   │   ├── strategy.json
│   │   │   ├── history.json
│   │   │   ├── relationship.json
│   │   │   ├── prompt_memory.json
│   │   │   ├── indexes.json
│   │   │   └── stats.json
│   │   ├── agent_02/
│   │   │   └── ...
│   │   └── agent_06/
│   │       └── ...
│   ├── collective/
│   │   ├── knowledge.json
│   │   ├── relations.json
│   │   ├── conflicts.json
│   │   ├── alliances.json
│   │   ├── consensus.json
│   │   └── stats.json
│   ├── longterm/
│   │   ├── patterns.json
│   │   ├── experience.json
│   │   ├── validated.json
│   │   └── stats.json
│   ├── world/
│   │   └── world_state.json
│   └── runtime/
│       └── runtime_state.json
└── v5/
    └── runtime/
        └── state/
            ├── runtime_state.json
            ├── agents_state.json
            ├── memory_state.json
            └── collectors_state.json
```

### OPIS PLIKOW

#### Agent Memory Files

| Plik | Format | Zawartosc |
|------|--------|-----------|
| `personality.json` | JSON (List) | Lista PersonalityMemoryEntry |
| `behavior.json` | JSON (List) | Lista BehaviorMemoryEntry |
| `strategy.json` | JSON (List) | Lista StrategyMemoryEntry |
| `history.json` | JSON (List) | Lista HistoryMemoryEntry |
| `relationship.json` | JSON (List) | Lista RelationshipMemoryEntry |
| `prompt_memory.json` | JSON (List) | Lista PromptMemoryEntry |
| `indexes.json` | JSON (Dict) | Indeksy dla szybkiego wyszukiwania |
| `stats.json` | JSON (Dict) | Statystyki pamieci |

#### Collective Memory Files

| Plik | Format | Zawartosc |
|------|--------|-----------|
| `knowledge.json` | JSON (List) | Lista KnowledgeEntry |
| `relations.json` | JSON (List) | Lista RelationEntry |
| `conflicts.json` | JSON (List) | Lista ConflictEntry |
| `alliances.json` | JSON (List) | Lista AllianceEntry |
| `consensus.json` | JSON (List) | Lista ConsensusEntry |
| `stats.json` | JSON (Dict) | Statystyki pamieci kolektywnej |

#### Long Term Memory Files

| Plik | Format | Zawartosc |
|------|--------|-----------|
| `patterns.json` | JSON (List) | Lista PatternEntry |
| `experience.json` | JSON (List) | Lista ExperienceEntry |
| `validated.json` | JSON (List) | Lista ValidatedKnowledgeEntry |
| `stats.json` | JSON (Dict) | Statystyki pamieci dlugoterminowej |

---

## AGENT MEMORY - SZCZEGOLY

### PERSONALITY MEMORY

**Przeznaczenie:** Przechowywanie cech osobowosci agenta

**Entry Structure:**
```python
@dataclass
class PersonalityMemoryEntry(MemoryEntry):
    # Wagi cech
    risk: float = 0.5            # Tolerancja ryzyka (0-1)
    analysis: float = 0.5       # Glebia analizy (0-1)
    creativity: float = 0.5    # Kreatywnosc (0-1)
    trust_v2: float = 0.8      # Zaufanie do V2 (0-1)
    trust_v3: float = 0.8      # Zaufanie do V3 (0-1)
    trust_v4: float = 0.8      # Zaufanie do V4 (0-1)
    trust_external: float = 0.6 # Zaufanie do external (0-1)
    
    # Cechy
    traits: Dict[str, float] = field(default_factory=dict)
    
    # Opis
    description: str = ""
    agent_type: str = "balanced"
    
    # Priorytety
    priorities: List[str] = field(default_factory=list)
```

**JSON Representation:**
```json
{
  "entry_id": "personality_01_001",
  "created_at": "2026-07-31T23:59:59",
  "updated_at": "2026-07-31T23:59:59",
  "data": {},
  "memory_type": "personality",
  "risk": 0.5,
  "analysis": 0.8,
  "creativity": 0.5,
  "trust_v2": 0.8,
  "trust_v3": 0.8,
  "trust_v4": 0.8,
  "trust_external": 0.6,
  "traits": {
    "risk_tolerance": 0.5,
    "analysis_depth": 0.8,
    "creativity_level": 0.5
  },
  "description": "Initial personality configuration",
  "agent_type": "balanced",
  "priorities": ["accuracy", "speed"]
}
```

**Uzycie:**
- Wybor strategii
- Ocena zaufania do zródeł
- Dopasowanie narzedzi
- Generowanie decyzji

### BEHAVIOR MEMORY

**Przeznaczenie:** Rejestrowanie zachowan agenta

**Entry Structure:**
```python
@dataclass
class BehaviorMemoryEntry(MemoryEntry):
    # Zachowanie
    action: str = ""
    behavior_type: str = "decision"  # decision, analysis, prediction, etc.
    description: str = ""
    
    # Kontekst
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Wykorzystane dane
    data_sources: List[str] = field(default_factory=list)
    
    # Skutecznosc
    effectiveness: float = 0.0    # 0-1
    success_rate: float = 0.0     # 0-1
    
    # Historia uzycia
    usage_count: int = 0
    first_used: str = ""
    last_used: str = ""
    
    # Bledy
    errors: List[str] = field(default_factory=list)
    corrections: List[str] = field(default_factory=list)
```

**JSON Representation:**
```json
{
  "entry_id": "beh_01_20260731235959",
  "created_at": "2026-07-31T23:59:59",
  "updated_at": "2026-07-31T23:59:59",
  "data": {},
  "memory_type": "behavior",
  "action": "prediction",
  "behavior_type": "decision_making",
  "description": "Made prediction using analytical strategy",
  "context": {
    "cycle": 5,
    "iteration": 30,
    "data_quality": 0.85
  },
  "data_sources": ["v2", "v3"],
  "effectiveness": 0.0,
  "success_rate": 0.0,
  "usage_count": 1,
  "first_used": "2026-07-31T23:59:59",
  "last_used": "2026-07-31T23:59:59",
  "errors": [],
  "corrections": []
}
```

**Uzycie:**
- Analiza historyczna zachowan
- Ocena skutecznosci dzialan
- Wybor optymalnych zachowan
- Unikanie bledow

### STRATEGY MEMORY

**Przeznaczenie:** Przechowywanie informacji o strategiach

**Entry Structure:**
```python
@dataclass
class StrategyMemoryEntry(MemoryEntry):
    # Strategia
    strategy_name: str = ""
    strategy_type: str = ""
    
    # Opis
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Historia uzycia
    times_used: int = 0
    times_successful: int = 0
    first_used: str = ""
    last_used: str = ""
    
    # Wyniki
    avg_confidence: float = 0.0
    avg_effective: float = 0.0
    success_rate: float = 0.0
    
    # Konteksty zastosowania
    contexts: List[Dict[str, Any]] = field(default_factory=list)
```

**JSON Representation:**
```json
{
  "entry_id": "strategy_01_analytical_001",
  "created_at": "2026-07-31T23:59:59",
  "updated_at": "2026-07-31T23:59:59",
  "data": {},
  "memory_type": "strategy",
  "strategy_name": "analytical",
  "strategy_type": "analytical",
  "description": "Analytical strategy for data-driven decisions",
  "parameters": {
    "depth": 3,
    "threshold": 0.7
  },
  "times_used": 5,
  "times_successful": 4,
  "first_used": "2026-07-31T23:59:59",
  "last_used": "2026-07-31T23:59:59",
  "avg_confidence": 0.85,
  "avg_effective": 0.8,
  "success_rate": 0.8,
  "contexts": [
    {"cycle": 1, "confidence": 0.9},
    {"cycle": 2, "confidence": 0.8}
  ]
}
```

**Uzycie:**
- Wybor strategii dla nowych decyzji
- Ocena skutecznosci strategii
- Optymalizacja parametrow
- Archiwizacja historyczna

### HISTORY MEMORY

**Przeznaczenie:** Zapisywanie historii decyzji i zdarzen

**Entry Structure:**
```python
@dataclass
class HistoryMemoryEntry(MemoryEntry):
    # Zdarzenie
    event_type: str = ""  # decision_made, cycle_completed, error, etc.
    description: str = ""
    
    # Kategorizacja
    categories: List[str] = field(default_factory=list)
    
    # Powiazania
    related_agent_id: Optional[str] = None
    related_decision_id: Optional[str] = None
    related_strategy_id: Optional[str] = None
    
    # Wyniki
    outcome: Dict[str, Any] = field(default_factory=dict)
    success: Optional[bool] = None
    
    # Ocena
    evaluation: float = 0.0  # 0-1
    confidence: float = 0.0  # 0-1
```

**JSON Representation:**
```json
{
  "entry_id": "hist_01_20260731235959",
  "created_at": "2026-07-31T23:59:59",
  "updated_at": "2026-07-31T23:59:59",
  "data": {},
  "memory_type": "history",
  "event_type": "decision_made",
  "description": "Decision: high_confidence_choice",
  "categories": ["decision", "autonomous"],
  "related_agent_id": null,
  "related_decision_id": "dec_01_20260731235959",
  "related_strategy_id": "strategy_01_analytical_001",
  "outcome": {},
  "success": null,
  "evaluation": 0.0,
  "confidence": 0.85
}
```

**Uzycie:**
- Analiza historyczna
- Wykrywanie trendow
- Ocena poprawnosci decyzji
- uczenie sie na bledach

### RELATIONSHIP MEMORY

**Przeznaczenie:** Przechowywanie informacji o relacjach z innymi agentami

**Entry Structure:**
```python
@dataclass
class RelationshipMemoryEntry(MemoryEntry):
    # Relacja
    other_agent_id: str = ""
    relationship_type: str = "neutral"  # trust, conflict, collaboration, competition, neutral
    
    # Wartosc
    trust_score: float = 0.0  # -1 to +1
    collaboration_score: float = 0.0  # 0 to 1
    conflict_score: float = 0.0  # 0 to 1
    
    # Historia
    interactions: int = 0
    positive_interactions: int = 0
    negative_interactions: int = 0
    neutral_interactions: int = 0
    
    # Ostatnia interakcja
    last_interaction: str = ""
    last_interaction_type: str = ""
    last_interaction_result: str = ""
    
    # Wymiana informacji
    information_shared: int = 0
    information_received: int = 0
    information_quality: float = 0.0
```

**JSON Representation:**
```json
{
  "entry_id": "rel_01_02_001",
  "created_at": "2026-07-31T23:59:59",
  "updated_at": "2026-07-31T23:59:59",
  "data": {},
  "memory_type": "relationship",
  "other_agent_id": "02",
  "relationship_type": "trust",
  "trust_score": 0.8,
  "collaboration_score": 0.7,
  "conflict_score": 0.1,
  "interactions": 5,
  "positive_interactions": 4,
  "negative_interactions": 1,
  "neutral_interactions": 0,
  "last_interaction": "2026-07-31T23:59:59",
  "last_interaction_type": "decision_sharing",
  "last_interaction_result": "positive",
  "information_shared": 3,
  "information_received": 2,
  "information_quality": 0.85
}
```

**Uzycie:**
- Ocena zaufania do innych agentow
- Wykrywanie sojuszy i konfliktow
- Optymalizacja wspolpracy
- Zarzadzanie spolecznoscia agentow

### PROMPT MEMORY

**Przeznaczenie:** Przechowywanie promptow dla modeli jezykowych

**Entry Structure:**
```python
@dataclass
class PromptMemoryEntry(MemoryEntry):
    # Prompt
    prompt_text: str = ""
    prompt_type: str = "system"  # system, user, assistant, context
    
    # Kontekst
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Uzycie
    times_used: int = 0
    avg_response_quality: float = 0.0
    avg_confidence: float = 0.0
    
    # Powiazania
    related_data: List[str] = field(default_factory=list)
    
    # Wygenerowane wyniki
    generated_results: List[Dict[str, Any]] = field(default_factory=list)
```

---

## COLLECTIVE MEMORY - SZCZEGOLY

### KNOWLEDGE ENTRY

**Przeznaczenie:** Przechowywanie wiedzy kolektywnej

**Structure:**
```python
@dataclass
class KnowledgeEntry:
    entry_id: str
    created_at: str
    updated_at: str
    
    # Treść
    title: str = ""
    content: str = ""
    summary: str = ""
    
    # Kategorizacja
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Źródła
    sources: List[str] = field(default_factory=list)
    source_quality: Dict[str, float] = field(default_factory=dict)
    
    # Walidacja
    validated: bool = False
    validation_score: float = 0.0
    validated_at: str = ""
    validated_by: str = ""
    
    # Historia
    version: int = 1
    previous_versions: List[str] = field(default_factory=list)
    
    # Statystyki
    used_by_agents: List[str] = field(default_factory=list)
    usage_count: int = 0
    last_used: str = ""
```

**Lokalizacja:** `SSI/memory/collective/knowledge.json`

### RELATION ENTRY

**Przeznaczenie:** Przechowywanie relacji miedzy agentami

**Structure:**
```python
@dataclass
class RelationEntry:
    entry_id: str
    created_at: str
    updated_at: str
    
    # Agenci
    agent_a: str = ""
    agent_b: str = ""
    
    # Typ relacji
    relation_type: str = "neutral"
    
    # Wagi
    trust_score: float = 0.0
    collaboration_score: float = 0.0
    conflict_score: float = 0.0
    competition_score: float = 0.0
    
    # Historia
    interactions: int = 0
    positive_interactions: int = 0
    negative_interactions: int = 0
    
    # Ostatnia interakcja
    last_interaction: str = ""
    last_interaction_type: str = ""
```

**Lokalizacja:** `SSI/memory/collective/relations.json`

### CONFLICT ENTRY

**Przeznaczenie:** Przechowywanie informacji o konfliktach

**Structure:**
```python
@dataclass
class ConflictEntry:
    entry_id: str
    created_at: str
    updated_at: str
    resolved_at: Optional[str] = None
    
    # Strony konfliktu
    involved_agents: List[str] = field(default_factory=list)
    
    # Typ konfliktu
    conflict_type: str = "decision"  # decision, resource, goal, etc.
    severity: str = "low"  # low, medium, high, critical
    
    # Opis
    description: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    status: str = "open"  # open, resolving, resolved, escalated
    resolution: Optional[str] = None
    resolution_quality: float = 0.0
    
    # Historia
    related_decisions: List[str] = field(default_factory=list)
    related_events: List[str] = field(default_factory=list)
```

**Lokalizacja:** `SSI/memory/collective/conflicts.json`

### ALLIANCE ENTRY

**Przeznaczenie:** Przechowywanie informacji o sojuszech

**Structure:**
```python
@dataclass
class AllianceEntry:
    entry_id: str
    created_at: str
    updated_at: str
    dissolved_at: Optional[str] = None
    
    # Czlonkowie
    members: List[str] = field(default_factory=list)
    
    # Typ sojuszu
    alliance_type: str = "information_sharing"  # information_sharing, decision_coordination, etc.
    
    # Cechy
    strength: float = 0.0  # 0-1
    stability: float = 0.0  # 0-1
    effectiveness: float = 0.0  # 0-1
    
    # Cel
    purpose: str = ""
    goals: List[str] = field(default_factory=list)
    
    # Historia
    formation_reason: str = ""
    formed_by: str = ""
    dissolution_reason: Optional[str] = None
    
    # Aktywnosc
    active: bool = True
    last_activity: str = ""
```

**Lokalizacja:** `SSI/memory/collective/alliances.json`

### CONSENSUS ENTRY

**Przeznaczenie:** Przechowywanie informacji o konsensusie

**Structure:**
```python
@dataclass
class ConsensusEntry:
    entry_id: str
    created_at: str
    updated_at: str
    
    # Temat
    topic: str = ""
    description: str = ""
    
    # Uczestnicy
    participating_agents: List[str] = field(default_factory=list)
    
    # Status
    status: str = "in_progress"  # in_progress, reached, failed
    consensus_level: float = 0.0  # 0-1 (1 = full consensus)
    
    # Głosy
    votes: Dict[str, Any] = field(default_factory=dict)  # agent_id -> vote
    voting_completed: bool = False
    
    # Wynik
    result: Optional[Dict[str, Any]] = None
    result_timestamp: Optional[str] = None
    
    # Historia
    discussion_history: List[Dict[str, Any]] = field(default_factory=list)
```

**Lokalizacja:** `SSI/memory/collective/consensus.json`

---

## LONG TERM MEMORY - SZCZEGOLY

### PATTERN ENTRY

**Przeznaczenie:** Przechowywanie historycznych wzorców

**Structure:**
```python
@dataclass
class PatternEntry:
    entry_id: str
    created_at: str
    updated_at: str
    
    # Wzorzec
    pattern_name: str = ""
    pattern_type: str = ""  # trend, cycle, correlation, anomaly, etc.
    description: str = ""
    
    # Definicja
    definition: Dict[str, Any] = field(default_factory=dict)
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Walidacja
    validated: bool = False
    validation_count: int = 0
    last_validated: str = ""
    
    # Statystyki
    occurrence_count: int = 0
    last_occurrence: str = ""
    average_strength: float = 0.0
    reliability: float = 0.0  # 0-1
    
    # Powiazania
    related_patterns: List[str] = field(default_factory=list)
    related_agents: List[str] = field(default_factory=list)
    
    # Historia
    discovery_source: str = ""
    discovered_by: str = ""
```

**Lokalizacja:** `SSI/memory/longterm/patterns.json`

### EXPERIENCE ENTRY

**Przeznaczenie:** Przechowywanie doświadczeń i lekcji

**Structure:**
```python
@dataclass
class ExperienceEntry:
    entry_id: str
    created_at: str
    updated_at: str
    
    # Doświadczenie
    title: str = ""
    description: str = ""
    lesson: str = ""
    
    # Kontekst
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Kategorizacja
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Walidacja
    validated: bool = False
    validation_score: float = 0.0
    validated_at: str = ""
    validated_by: str = ""
    
    # Zastosowanie
    applied_count: int = 0
    success_rate: float = 0.0
    last_applied: str = ""
    
    # Powiazania
    related_decisions: List[str] = field(default_factory=list)
    related_patterns: List[str] = field(default_factory=list)
    related_agents: List[str] = field(default_factory=list)
```

**Lokalizacja:** `SSI/memory/longterm/experience.json`

### VALIDATED KNOWLEDGE ENTRY

**Przeznaczenie:** Przechowywanie zweryfikowanej wiedzy

**Structure:**
```python
@dataclass
class ValidatedKnowledgeEntry:
    entry_id: str
    created_at: str
    updated_at: str
    
    # Wiedza
    title: str = ""
    content: str = ""
    summary: str = ""
    
    # Walidacja
    validation_method: str = ""
    validation_score: float = 0.0  # 0-1
    validated_at: str = ""
    validated_by: str = ""
    validation_evidence: List[str] = field(default_factory=list)
    
    # Źródła
    sources: List[str] = field(default_factory=list)
    source_reliability: Dict[str, float] = field(default_factory=dict)
    
    # Kategorizacja
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Zastosowanie
    used_by: List[str] = field(default_factory=list)
    usage_count: int = 0
    last_used: str = ""
    
    # WAZNOSC
    expires_at: Optional[str] = None
    refresh_interval: Optional[str] = None  # e.g., "7d", "30d"
```

**Lokalizacja:** `SSI/memory/longterm/validated.json`

---

## WORLD MEMORY

### UNIFIED INPUT PACKAGE

**Przeznaczenie:** Agregacja wszystkich danych wejsciowych

**Structure:**
```python
@dataclass
class UnifiedInputPackage:
    timestamp: str
    version: str = "1.0.0"
    
    # Dane z collectorow
    data: Dict[str, Any] = field(default_factory=dict)
    # Format: {"v2": {...}, "v3": {...}, "v4": {...}, "external": {...}}
    
    # Metadane
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Format: {"quality_scores": {...}, "trust_scores": {...}, ...}
    
    # Stan
    state: Dict[str, Any] = field(default_factory=dict)
```

**Lokalizacja:** Runtime memory (not persistent by default)

---

## ENTRY STRUKTURY

### BAZOWA STRUKTURA

Wszystkie wpisy pamieci dziedzicza z `MemoryEntry`:

```python
@dataclass
class MemoryEntry:
    # Pola wymagane
    entry_id: str
    created_at: str
    updated_at: str
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Pola z domyslnymi wartosciami
    memory_type: MemoryType = MemoryType.PERSONALITY
    tags: List[str] = field(default_factory=list)
    priority: int = 1
    expiration: Optional[str] = None
    
    # Aktywne
    active: bool = True
    validated: bool = False
```

### POLA WSPOLNE

| Pole | Typ | Opis | Wymagane |
|------|-----|------|----------|
| entry_id | str | Unikalny identyfikator | TAK |
| created_at | str | Data utworzenia (ISO format) | TAK |
| updated_at | str | Data ostatniej modyfikacji (ISO format) | TAK |
| data | Dict | Dodatkowe dane | NIE |
| memory_type | MemoryType | Typ pamieci | NIE |
| tags | List[str] | Tagi dla indeksowania | NIE |
| priority | int | Priorytet (1 = normal, 2 = high, 0 = low) | NIE |
| expiration | Optional[str] | Data waznosci (ISO format) | NIE |
| active | bool | Czy wpis jest aktywny | NIE |
| validated | bool | Czy wpis zostal zweryfikowany | NIE |

---

## INDEKSY I WYSZUKIWANIE

### SYSTEM INDEKSOW

Kazdy `AgentMemoryStore` utrzymuje indeksy dla szybkiego wyszukiwania:

```python
_indexes: Dict[MemoryType, Dict[str, List[str]]] = {
    MemoryType.PERSONALITY: {},
    MemoryType.BEHAVIOR: {},
    MemoryType.STRATEGY: {},
    MemoryType.HISTORY: {},
    MemoryType.RELATIONSHIP: {},
    MemoryType.PROMPT: {}
}
```

### RODZAJE INDEKSOW

**1. Indeks "all"**
- Zawiera wszystkie entry_id dla danego typu pamieci
- Uzycie: `query_by_index(memory_type, "all")`

**2. Indeksy po typach**
- Dla Behavior: `type:{behavior_type}` (np. "type:decision_making")
- Dla Strategy: `name:{strategy_name}` (np. "name:analytical")
- Dla History: `type:{event_type}` (np. "type:decision_made")
- Dla Relationship: `agent:{other_agent_id}` (np. "agent:02"), `type:{relationship_type}`
- Dla Prompt: `type:{prompt_type}` (np. "type:system")

**3. Indeksy po kategoriach**
- Dla History: `category:{category}` (np. "category:decision")

**4. Indeksy po tagach**
- Dla wszystkich typów: `tag:{tag}` (np. "tag:important")

### METODY WYSZUKIWANIA

**1. get_entry(entry_id, memory_type)**
- Pobierz pojedynczy wpis po ID
- Opcjonalnie: typ pamieci dla szybszego wyszukiwania

**2. query_entries(memory_type, **filters)**
- Zapytanie z filtrowaniem
- Obsluguje filtry: `tags`, `active`, oraz dowolne pole

**3. query_by_index(memory_type, index_key)**
- Pobierz wszystkie wpisy dla danego indeksu

**4. get_all_entries(memory_type)**
- Pobierz wszystkie wpisy danego typu

### PRZYKLADY UZYCIA

```python
# Pobierz wpis po ID
entry = memory_store.get_entry("personality_01_001", "personality")

# Zapytaj o zachowania typu "decision_making"
behaviors = memory_store.query_entries(MemoryType.BEHAVIOR, behavior_type="decision_making")

# Pobierz wszystkie strategie "analytical"
strategies = memory_store.query_by_index(MemoryType.STRATEGY, "name:analytical")

# Pobierz wszystkie aktywne wpisy historii
active_history = memory_store.query_entries(MemoryType.HISTORY, active=True)

# Pobierz wszystkie wpisy z tagiem "important"
important = memory_store.query_entries(MemoryType.HISTORY, tags=["important"])
```

---

## PERSYSTENCJA

### ZAPIS DO DYSKU

**Proces zapisu:**
1. Serializacja wszystkich wpisów do JSON
2. Konwersja enumow do stringow
3. Zapis do poszczególnych plików (personality.json, behavior.json, etc.)
4. Zapis indeksow do indexes.json
5. Zapis statystyk do stats.json

**Format pliku:**
- Kazdy typ pamieci w osobnym pliku JSON
- Lista wpisów (dla Personality, Behavior, etc.)
- Dictionary (dla indexes, stats)

### ODCZYT Z DYSKU

**Proces odczytu:**
1. Odczyt pliku JSON
2. Deserializacja do objetosci Python
3. Konwersja stringow do enumow (MemoryType)
4. Tworzenie odpowiednich klas (PersonalityMemoryEntry, etc.)
5. Wczytanie indeksow i statystyk

### AUTO-SAVE

**Konfiguracja:**
- `auto_save`: bool (domyslnie True)
- `save_interval`: int (ilosc cykli miedzy zapisami)

**Triggery zapisu:**
- Po kazdym cyklu (jeśli `save_interval` ustawiony)
- Przy shutting down systemu
- Na zadosc (manualne wywolanie `save_to_disk()`)

---

## SYNCHRONIZACJA PAMIECI

### AGENT MEMORY SYNC

**Zakres:** Tylko wlasna pamiec agenta

**Proces:**
1. Agent wczytuje pamiec na poczatku cyklu (`load_memory()`)
2. Agent zapisuje pamiec po zakonczeniu cyklu (`save_memory()`)
3. Runtime Controller moze wymusic zapis (`save_state()`)

**Izolacja:**
- Kazdy agent ma swoja wlasna pamiec
- Agenci nie maja dostepu do pamieci innych agentow
- CCL ma dostep read-only do wszystkich pamieci

### COLLECTIVE MEMORY SYNC

**Zakres:** Wspólna pamiec systemu

**Proces:**
1. Kazdy agent moze dodawac wpisy do pamieci kolektywnej
2. CCL analizuje pamiec kolektywna
3. Pamiec kolektywna jest zapisywana po kazdym cyklu

**Warunki:**
- Tylko zweryfikowane informacje
- Zgodnosc miedzy agentami
- Walidacja przez CCL

### WORLD MEMORY SYNC

**Zakres:** Aktualny stan świata

**Proces:**
1. Runtime Controller tworzony nowy UnifiedInputPackage po kazdym cyklu collectorow
2. World Memory jest aktualizowana z nowymi danymi
3. Agenci czytaja World Memory na poczatku swoego cyklu

**Cechy:**
- Tymczasowa (nie trwala na dysku)
- Odswiezana przy kazdym cyklu
- Globalny dostep

---

## BACKUP I RECOVERY

### BACKUP STRATEGY

**1. Regularne backupy:**
- Co N cykli (konfigurowalne)
- Zapis do osobnego katalogu backup

**2. Versioned backups:**
- Kazdy backup ma numer wersji
- Zachowywanie ostatnich X backupow

**3. Compressed backups:**
- Kompresja JSON do formatu .zip
- Mniejsze zuzycie miejsca

### STRUKTURA BACKUP

```
SSI/backup/
├── memory/
│   ├── 2026-07-31_00-00-00/
│   │   ├── agents/
│   │   │   ├── agent_01/
│   │   │   │   ├── personality.json
│   │   │   │   ├── behavior.json
│   │   │   │   └── ...
│   │   │   └── agent_06/
│   │   │       └── ...
│   │   ├── collective/
│   │   │   ├── knowledge.json
│   │   │   └── ...
│   │   └── longterm/
│   │       └── ...
│   └── 2026-07-30_00-00-00/
│       └── ...
└── state/
    └── 2026-07-31_00-00-00/
        └── runtime_state.json
```

### RECOVERY PROCES

**1. Pełny recovery:**
- Odczyt ostatniego backupu
- Wczytanie wszystkich pamieci
- Wznowienie pracy od ostatniego stanu

**2. Czesciowy recovery:**
- Odzysk tylko wybranej pamieci
- Rekonstrukcja brakujacych danych

**3. Emergency recovery:**
- Odzysk z uszkodzonych plikow
- Naprawa struktury danych
- Walidacja integralnosci

---

**Nota:** Ta dokumentacja jest czescia Projektu SSI V5. Pozostale dokumenty to: SSI_V5_ARCHITECTURE_PART1.md, SSI_V5 ARCHITECTURE_PART2.md, SSI_V5_DATA_FLOW.md, SSI_V5_AGENT_BEHAVIOR.md.

**Ostatnia aktualizacja:** 2026-07-31
