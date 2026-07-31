# SPRINT 11.4 - QUICKSTART GUIDE

**Sprint:** 11.4 - External Input Layer  
**Status:** PLAN ZATWIERDZONY  
**Data:** 2026-07-31  
**Autor:** Mistral Vibe - Glowny Inzynier SSI V5  

---

## STRESZCZENIE

**Cel:** Zbudowac uniwersalny kolektor dla zewnetrznych zrodel danych.

**Architektura:**
```
ExternalKnowledgeCollector
├── DeveloperSourceHandler   -> polecenia, wymagania, decyzje
├── LaboratorySourceHandler  -> 4 typy laboratoriow + odkrycia  
├── AgentSourceHandler       -> nowi agenci, komunikaty, decyzje
├── SystemSourceHandler      -> logi, statusy, zdarzenia, metryki
└── Walidatory dla kazdego typu
```

**Zakres:** 14 dni, 125+ testow, 25+ modeli danych

---

## STRUKTURA PLIKOW

```
SSI/v5/input_layer/external/
├── __init__.py
├── source_types.py          # Enumy
├── external_models.py       # 20+ modeli dataclass
├── external_collector.py    # Glowny kolektor
├── sources/
│   ├── __init__.py
│   ├── developer_source.py
│   ├── laboratory_source.py
│   ├── agent_source.py
│   └── system_source.py
└── validators/
    ├── __init__.py
    ├── developer_validator.py
    ├── laboratory_validator.py
    ├── agent_validator.py
    └── system_validator.py
```

**Testy:** `SSI/tests/v5/test_external_*.py` (125+ testow)

---

## PRIORYTETY IMPLEMENTACYJNE

### P1 - Fundament (Dzien 1)
- [ ] Katalogi: `SSI/v5/input_layer/external/` + podkatalogi
- [ ] `source_types.py` (SourceType, LaboratoryType, DeveloperInputType, etc.)
- [ ] Update `data_models.py` (DataSource + 4 nowe wartosci)

### P2 - Modele Danych (Dzien 2-3)
- [ ] ExternalMetadata
- [ ] Developer: DeveloperInput, DeveloperCommand, Requirement, ArchitecturalDecision
- [ ] Laboratories: LaboratoriesData, LaboratoryExperiment, LaboratoryDiscovery, LaboratoryStats
- [ ] Agents: AgentInputData, NewAgentInfo, AgentCommunication, AgentDecision, AgentStatus
- [ ] System: SystemMessages, SystemLog, SystemStatus, SystemEvent, PerformanceMetrics
- [ ] ExternalDataPackage (agregator)

### P3 - Source Handlers (Dzien 4-6)
Kazdy handler implementuje:
```python
class BaseSourceHandler:
    def initialize(self) -> bool: ...
    def collect(self) -> Any: ...
```

### P4 - Glowny Kolektor (Dzien 7-8)
```python
class ExternalKnowledgeCollector:
    def __init__(self): ...
    def initialize(self) -> bool: ...
    def collect_all(self) -> ExternalDataPackage: ...
    def collect_specific(source_types: List[SourceType]): ...
    def collect_developer_input(self) -> DeveloperInput: ...
    def collect_laboratories(self) -> LaboratoriesData: ...
    def collect_agent_input(self) -> AgentInputData: ...
    def collect_system_messages(self) -> SystemMessages: ...
    def validate(self, package) -> bool: ...
    def get_summary(self) -> Dict: ...
```

### P5 - Walidatory (Dzien 9-10)
- [ ] DeveloperInputValidator
- [ ] LaboratoryDataValidator  
- [ ] AgentInputValidator
- [ ] SystemMessagesValidator

### P6 - Testy (Dzien 11-13)
- 20 testow: ExternalKnowledgeCollector
- 25 testow: ExternalDataPackage + modele
- 40 testow: Source Handlers (10 kazdy)
- 40 testow: Walidatory (10 kazdy)

### P7 - Finalizacja (Dzien 14)
- [ ] Update `SSI/v5/input_layer/__init__.py`
- [ ] Docstrings w kodzie
- [ ] PROJECT_JOURNAL.md update
- [ ] Commit i push

---

## KONTRAKTY INTERFEJSOW

### ExternalDataPackage
```python
@dataclass
class ExternalDataPackage:
    timestamp: datetime
    developer_data: Optional[DeveloperInput]
    laboratories_data: Optional[LaboratoriesData]
    agent_data: Optional[AgentInputData]
    system_data: Optional[SystemMessages]
    metadata: Optional[ExternalMetadata]
    status: str
    
    def to_dict() -> Dict[str, Any]: ...
    def to_json(indent=2) -> str: ...
    @classmethod
    def from_dict(data: Dict) -> "ExternalDataPackage": ...
    def validate() -> bool: ...
```

### ExternalKnowledgeCollector
```python
class ExternalKnowledgeCollector:
    def initialize() -> bool: ...
    def collect_all() -> ExternalDataPackage: ...
    def collect_specific(source_types: List[SourceType]) -> ExternalDataPackage: ...
    # + 4 individual collect methods
    def validate(package: ExternalDataPackage) -> bool: ...
    def get_summary() -> Dict[str, Any]: ...
    def get_source_type() -> SourceType: ...
```

---

## TESTY (125+)

```
SSI/tests/v5/
├── test_external_collector.py     # 20 testow
├── test_external_models.py        # 25 testow
├── test_source_handlers/          # 40 testow
│   ├── test_developer_handler.py # 10
│   ├── test_laboratory_handler.py # 10
│   ├── test_agent_handler.py     # 10
│   └── test_system_handler.py    # 10
└── test_validators/                # 40 testow
    ├── test_developer_validator.py # 10
    ├── test_laboratory_validator.py # 10
    ├── test_agent_validator.py     # 10
    └── test_system_validator.py    # 10
```

---

## CHECKLISTA

- [ ] Struktura katalogow
- [ ] source_types.py
- [ ] Update data_models.py
- [ ] external_models.py (20+ klas)
- [ ] 4 Source Handlers
- [ ] 4 Walidatory
- [ ] ExternalKnowledgeCollector
- [ ] Update __init__.py
- [ ] 125+ testow
- [ ] Dokumentacja

---

## ZASADY

1. **Nie zmieniac V2/V3/V4**
2. **Nie tworzyc duplikatow**
3. **100% kompatybilnosc**
4. **Testowac wszystko**
5. **Dokumentowac kod**
6. **Zachowac spojnosc** stylu

---

## NASTEPNE KROKI

1. Utworzyc strukture katalogow
2. Zaimplementowac source_types.py
3. Zaktualizowac data_models.py
4. Zaczac external_models.py

---

**Dokument:** `SSI_DOCUMENTATION/SPRINT_11_4_QUICKSTART.md`  
**Wersja:** 1.0  
**Data:** 2026-07-31  
**Status:** GOTOWY DO UZYCIA
