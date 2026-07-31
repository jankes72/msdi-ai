# SPRINT 11.4 — PROFESSIONAL IMPLEMENTATION PLAN

**Sprint:** 11.4 - External Input Layer  
**Tytuł:** Uniwersalny Kolektor Danych Zewnętrznych  
**Status:** PLANOWANY  
**Data rozpoczęcia:** 2026-07-31  
**Data zakończenia:** (do ustalenia)  
**Autor:** Mistral Vibe (Główny Inżynier SSI V5)  
**Podstawa:** SPRINT_11_REFACTORED.md, PROJECT_RULES.md, Dokumentacja V2/V3/V4  

---

## 🎯 CEL SPRINTU

**Główny cel:** Stworzenie warstwy wejścia dla zewnętrznych źródeł danych, która zintegruje wszystkie przyszłe wejścia do systemu SSI V5 w spójny i modularny sposób.

### Cele szczegółowe:
1. ✅ Zbudować `ExternalKnowledgeCollector` dziedziczący z `BaseCollector`
2. ✅ Zdefiniować modele danych dla zewnętrznych źródeł
3. ✅ Zaimplementować obsługę 4 typów źródeł: DEVELOPER, LABORATORIES, AGENTS, SYSTEM
4. ✅ Zapewnić serializację, walidację i logging
5. ✅ Przygotować testy jednostkowe (min. 100 testów)
6. ✅ Zachować 100% kompatybilność z istniejącą architektoniką

---

## 🏗️ ARCHITEKTURA SPRINTU 11.4

### Schemat architektoniczny:

```
EXTERNAL INPUT LAYER
├─────────────────────────────────────┐
│  SourceType (Enumy)                    │
│    ├── DEVELOPER                     │
│    ├── LABORATORIES (WORLD, TYPE, GROUP, COUPON)  │
│    ├── AGENTS                        │
│    └── SYSTEM                        │
└─────────────────────────────────────┘
                    │
                    ▼
EXTERNAL KNOWLEDGE COLLECTOR
├─────────────────────────────────────┐
│  collect_all() -> ExternalDataPackage  │
│  collect_specific(source_types)        │
│  validate() -> bool                   │
└─────────────────────────────────────┘
                    │
                    ▼
SOURCE HANDLERS (Adapter Pattern)
├───────────────────┬───────────────────┬───────────────────┐
│ DeveloperSource   │ LaboratorySource   │ AgentSource        │
│ Handler            │ Handler            │ Handler            │
└───────────────────┴───────────────────┴───────────────────┘
                    │
                    ▼
VALIDATORS
├───────────────────┬───────────────────┬───────────────────┐
│ DeveloperValidator │ LaboratoryValidator│ AgentValidator     │
└───────────────────┴───────────────────┴───────────────────┘
```

---

## 📁 STRUKTURA PLIKÓW

### Nowe katalogi i pliki:
```
SSI/v5/input_layer/
└── external/                    # NOWY KATALOG
    ├── __init__.py              # Moduł external
    ├── source_types.py          # Enumy typów źródeł
    ├── external_models.py       # WSZYSTKIE modele danych (20+ klas)
    ├── external_collector.py    # Główny kolektor
    │
    ├── sources/                 # Handlers
    │   ├── __init__.py
    │   ├── developer_source.py
    │   ├── laboratory_source.py
    │   ├── agent_source.py
    │   └── system_source.py
    │
    └── validators/              # Walidatory
        ├── __init__.py
        ├── developer_validator.py
        ├── laboratory_validator.py
        ├── agent_validator.py
        └── system_validator.py
```

### Pliki do zaktualizowania:
- `SSI/v5/input_layer/__init__.py` - Dodanie importów External
- `SSI/v5/input_layer/data_models.py` - Rozszerzenie DataSource enum

---

## 📊 MODELE DANYCH

### 1. source_types.py - Typy źródeł

```python
from enum import Enum

class SourceType(Enum):
    DEVELOPER = "developer"
    LABORATORIES = "laboratories"
    AGENTS = "agents"
    SYSTEM = "system"

class LaboratoryType(Enum):
    WORLD_LAB = "world_lab"
    TYPE_LAB = "type_lab"
    GROUP_LAB = "group_lab"
    COUPON_LAB = "coupon_lab"

class DeveloperInputType(Enum):
    COMMAND = "command"
    REQUIREMENT = "requirement"
    ARCHITECTURAL_DECISION = "architectural_decision"
    CODE_CHANGE = "code_change"
    SYSTEM_ANALYSIS = "system_analysis"
    QUERY = "query"

class AgentInputType(Enum):
    NEW_AGENT = "new_agent"
    AGENT_COMMUNICATION = "agent_communication"
    AGENT_DECISION = "agent_decision"
    AGENT_STATUS = "agent_status"
    AGENT_MEMORY = "agent_memory"

class SystemMessageType(Enum):
    LOG = "log"
    STATUS = "status"
    EVENT = "event"
    ERROR = "error"
    WARNING = "warning"
    PERFORMANCE = "performance"
```

### 2. external_models.py - Główne modele (skrócona wersja)

Listę wszystkich modeli danych zawiera dokument **SPRINT_11_4_DATA_MODELS.md**

Główne kategorie:
- **ExternalMetadata** - Metadane pakietu
- **DeveloperInput, DeveloperCommand, Requirement, ArchitecturalDecision** - DEVELOPER
- **LaboratoriesData, LaboratoryExperiment, LaboratoryDiscovery, LaboratoryStats** - LABORATORIES
- **AgentInputData, NewAgentInfo, AgentCommunication, AgentDecision, AgentStatus** - AGENTS
- **SystemMessages, SystemLog, SystemStatus, SystemEvent, PerformanceMetrics** - SYSTEM
- **ExternalDataPackage** - Główny pakiet agregujący

### 3. Kontrakt ExternalDataPackage

```python
@dataclass
class ExternalDataPackage:
    timestamp: datetime
    developer_data: Optional[DeveloperInput]
    developer_commands: List[DeveloperCommand]
    requirements: List[Requirement]
    architectural_decisions: List[ArchitecturalDecision]
    laboratories_data: Optional[LaboratoriesData]
    agent_data: Optional[AgentInputData]
    system_data: Optional[SystemMessages]
    metadata: Optional[ExternalMetadata]
    status: str
    
    def to_dict(self) -> Dict[str, Any]: pass
    def to_json(self, indent: int = 2) -> str: pass
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExternalDataPackage": pass
    def validate(self) -> bool: pass
```

---

## 🎯 EXTERNAL KNOWLEDGE COLLECTOR

### Główne metody:

```python
class ExternalKnowledgeCollector:
    def __init__(self) -> None: pass
    def initialize(self) -> bool: pass
    def collect_all(self) -> ExternalDataPackage: pass
    def collect_specific(self, source_types: List[SourceType]) -> ExternalDataPackage: pass
    def collect_developer_input(self) -> DeveloperInput: pass
    def collect_laboratories(self) -> LaboratoriesData: pass
    def collect_agent_input(self) -> AgentInputData: pass
    def collect_system_messages(self) -> SystemMessages: pass
    def validate(self, package: ExternalDataPackage) -> bool: pass
    def get_summary(self) -> Dict[str, Any]: pass
    def get_source_type(self) -> SourceType: pass
```

### Architektura wewnętrzna:

- **Handlery źródeł**: Każde źródło ma dedykowanego handlera (Adapter Pattern)
- **Lazy loading**: Handlers są inicjalizowane przy pierwszym użyciu
- **Error handling**: Błędy w jednym handlerze nie zatrzymują całego kolektora
- **Fallback**: Demo data przy braku rzeczywistych źródeł

---

## 🔌 SOURCE HANDLERS

### DeveloperSourceHandler
Obsługuje: polecenia, wymagania, decyzje architektoniczne, zapytania

### LaboratorySourceHandler  
Obsługuje: eksperymenty i odkrycia z 4 typów laboratoriów

### AgentSourceHandler
Obsługuje: nowi agenci (nie V4!), komunikacja, decyzje, statusy

### SystemSourceHandler
Obsługuje: logi, statusy komponentów, zdarzenia, metryki wydajności

---

## 🧪 WALIDATORY

Każdy walidator dostarcza:
- Walidację pojedynczych elementów
- Walidację kolekcji
- Czyszczenie danych
- Raport błędów i ostrzeżeń

---

## 🧪 TESTY JEDNOSTKOWE

### Struktura testów:
```
SSI/tests/v5/
├── test_external_collector.py      # 20 testów
├── test_external_models.py         # 25 testów
├── test_source_handlers/           # 40 testów
│   ├── test_developer_handler.py
│   ├── test_laboratory_handler.py
│   ├── test_agent_handler.py
│   └── test_system_handler.py
└── test_validators/                 # 40 testów
    ├── test_developer_validator.py
    ├── test_laboratory_validator.py
    ├── test_agent_validator.py
    └── test_system_validator.py
```

### **RAZEM: ≥125 testów**

---

## 🔄 INTEGRACJA Z ISTNIEJĄCĄ ARCHITEKTURĄ

### Kompatybilność z V2/V3/V4:
- ✅ Żadna zależność od V2 (V2DataCollector jest osobny)
- ✅ Żadna zależność od V3 (V3KnowledgeCollector jest osobny)
- ✅ Żadna zależność od V4 (V4AgentsCollector jest osobny)
- ✅ Nowa warstwa EXTERNAL nie wpływa na istniejące

### Integracja z data_models.py:
```python
# Dodanie do DataSource enum
class DataSource(Enum):
    V2_MODELS = "v2_models"
    V3_KNOWLEDGE = "v3_knowledge"  
    V4_AGENTS = "v4_agents"
    AGENTS = "agents"                 # NOWE
    LABORATORIES = "laboratories"     # NOWE
    DEVELOPER = "developer"           # NOWE
    SYSTEM = "system"                 # NOWE
```

---

## 🎯 KRYTERIA AKCEPTACJI

### Kryteria techniczne:
- [ ] ExternalKnowledgeCollector gotowy do dziedziczenia z BaseCollector
- [ ] Wszystkie modele mają serializację (to_dict, from_dict, to_json)
- [ ] Wszystkie modele mają walidację
- [ ] Wszystkie handlery implementują spójny interfejs
- [ ] System logging zintegrowany
- [ ] Obsługa błędów i fallbacki (demo data)

### Kryteria danych:
- [ ] Wszystkie 4 typy źródeł obsługiwane
- [ ] ExternalDataPackage agreguje wszystkie dane
- [ ] Kompatybilność z DataSource enum

### Kryteria testów:
- [ ] ≥125 testów jednostkowych
- [ ] Testy serializacji/deserializacji
- [ ] Testy walidacji
- [ ] Testy integracyjne

### Kryteria dokumentacji:
- [ ] Dokumentacja kodu (docstrings)
- [ ] Dokumentacja API
- [ ] Zaktualizowany PROJECT_JOURNAL.md

---

## 📈 WPŁYW NA PRZYSZŁOŚĆ

### Zależności:
| Sprint | Zależność od 11.4 |
|--------|-------------------|
| 11.5 (Unified Input) | ExternalKnowledgeCollector w KnowledgeCollectorManager |
| 11.6 (Runtime) | ExternalDataPackage w harmonogramie |
| 11.7 (Classifier) | Klasyfikacja danych EXTERNAL |
| 11.8 (Prompt) | Kontekst z danych EXTERNAL |

### Integracja z przyszłymi systemami:
- **Developer Gateway (Sprint 11.11+)** → używa DeveloperSourceHandler
- **Agent Registry (Sprint 11.10+)** → używa AgentSourceHandler
- **Laboratoria (Sprint 11.12+)** → używa LaboratorySourceHandler

---

## 📅 PLAN IMPLEMENTACJI

### Etapy:
1. **Dzień 1**: Struktur katalogów + source_types.py + update data_models.py
2. **Dzień 2-3**: external_models.py ( Electrical structure)
3. **Dzień 4-6**: Handlery źródeł (4 handlers)
4. **Dzień 7-8**: ExternalKnowledgeCollector + integracja
5. **Dzień 9-10**: Walidatory (4 validators)
6. **Dzień 11-13**: Testy (125+ testów)
7. **Dzień 14**: Dokumentacja + finalizacja

### Szacowany czas: **14 dni roboczych**

---

## 📝 DOKUMENTY POWIĄZANE

- [SPRINT_11_4_DATA_MODELS.md](SPRINT_11_4_DATA_MODELS.md) - Pełne definicje modeli danych
- [SPRINT_11_4_TEST_PLAN.md](SPRINT_11_4_TEST_PLAN.md) - Szczegółowy plan testów
- [SPRINT_11_4_CODE_STRUCTURE.md](SPRINT_11_4_CODE_STRUCTURE.md) - Struktura kodu

---

**Dokument:** `SSI_DOCUMENTATION/SPRINT_11_4_IMPLEMENTATION_PLAN.md`  
**Wersja:** 1.0  
**Data:** 2026-07-31  
**Autor:** Mistral Vibe (Główny Inżynier SSI V5)  
**Status:** ✅ GOTOWY DO IMPLEMENTACJI

---

> **"Dobra architektura nie powstaje przez przypadek. Powstaje przez planowanie, dyscyplinę i uwagę na detale."**
> 
> **"Sprint 11.4 to fundament dla wszystkich przyszłych źródeł danych w SSI V5."**
