# V3 to V4 Integration Document
## Wersjonowane Kontrakty, Architektura i Integracja Systemu SSI

[TAGS: INTEGRATION, CONTRACT, ARCHITECTURE, V2, V3, V4, DATA_FLOW, RESPONSIBILITY]

---

## 1. Wprowadzenie

### 1.1 Cel Dokumentu

Dokument **V3_V4_INTEGRATION.md** jest **single source of truth** dla:
- **Faktycznej architektury** integracji między warstwami V2, V3 i V4
- **Wersjonowanych kontraktów** między modułami
- **Diagramów przepływu danych** i granic odpowiedzialności
- **Działających przykładów użycia** zweryfikowanych w CI
- **Rejestru funkcjonalności** ze statusami (planned, implemented, tested, operational)
- **ADR (Architecture Decision Records)** dla synchronizacji, persistence, polityki danych

### 1.2 Zakres

- **V2 Model Laboratory** → **V3 World Memory System** → **V4 Agent Evolution**
- Mechanizmy transferu wiedzy między warstwami
- Granice odpowiedzialności i kontrakt interfejsów
- Integracja z pozostałymi komponentami systemu (Strategy, Laboratories, Feedback)

### 1.3 Status Dokumentu

| Wersja | Data | Autor | Zmiany |
|--------|------|-------|--------|
| 1.0 | 2026-07-31 | SSI Documentation System | Utworzenie dokumentu integracyjnego |

**Zgodność z Źródłami:** 
- `01_SYSTEM_ARCHITECTURE.md` (v4.0)
- `10_IMPLEMENTATION_MAP.md` (v4.0)
- `AUDYT_ZGODNOSCI_I_GOTOWOSCI_DO_SKALOWANIA_2026-07-30.md`
- `Analiza Spojności Projektowej V3 → V4.md`

---

## 2. Faktyczna Architektura Systemu

### 2.1 Hierarchia Warstw (Current State)

```
┌─────────────────────────────────────────────────────────────────┐
│                      DATA INTELLIGENCE LAYER                      │ [V1 - ✅ OPERATIONAL]
│  Źródło: pobieranieKursow.py, pobieranieWynikow.py, dodawanieWynikow.py │
│  Generatory: generatorDataBase.py, generatorDataBaseTrendAnalisAll.py│
│  Wyjście: kursy_przygotowane.csv, wyniki, historia zdarzeń          │
└──────────────────────────────┬──────────────────────────────────┘
                                ↓ [STRONG DEPENDENCY]
┌─────────────────────────────────────────────────────────────────┐
│                         V2 — MODEL LABORATORY                        │ [V2 - ✅ IMPLEMENTED]
│  Modele: siec_01_zmiana_kursow, siec_02_amplituda, siec_03_tempo,    │
│          siec_04_synchronizacja, RandomForest, Klasyfikatory      │
│  Podział: 60% trening + 40% obserwacja                               │
│  Cel: Multiple interpretacje świata (każdy model = inny świat)     │
└──────────────────────────────┬──────────────────────────────────┘
                                ↓ [STRONG DEPENDENCY]
┌─────────────────────────────────────────────────────────────────┐
│                      V3 — WORLD MEMORY SYSTEM                       │ [V3 - 🔄 IMPLEMENTATION]
│  ŚWIATY: zmiana_kursów, dynamika, klasyfikacja, relacje             │
│  PAMIĘCI: World Memory, Group Memory, Pattern Memory, Historical   │
│  METADANE: Tagowanie (7 kategorii), zależności, analiza ekonomiczna │
│  V3 NIE podejmuje decyzji - Tworzy mapę wiedzy                     │
└──────────────────────────────┬──────────────────────────────────┘
                                ↓ [DATA DEPENDENCY + FEEDBACK DEPENDENCY]
┌─────────────────────────────────────────────────────────────────┐
│                   V4 — AUTONOMOUS AGENT EVOLUTION                  │ [V4 - 📋 IMPLEMENTED]
│  AGENT BIRTH SYSTEM: Utworzenie → Parametry → Osobowość → ROOM_CORE │
│  PIERWSZA POPULACJA: 3 agenci (Analityk, Strateg Wartości, Eksperymentator)│
│  ROOM_CORE: Pokój narodzin i komunikacji                          │
│  V4 korzysta z: World Memory, Group Memory, Pattern Memory,       │
│  Historical Results, Model Evaluation, Strategy Engine, Feedback Loop│
└──────────────────────────────┬──────────────────────────────────┘
                                ↓ [FEEDBACK DEPENDENCY]
┌─────────────────────────────────────────────────────────────────┐
│                    LABORATORIA DECYZYJNE                           │ [📋 PLANNED]
│  Decision Lab → Group Lab → Coupon Lab → Strategy Lab              │
└──────────────────────────────┬──────────────────────────────────┘
                                ↓ [EVOLUTION DEPENDENCY]
┌─────────────────────────────────────────────────────────────────┐
│                    STRATEGY INTELLIGENCE ENGINE                   │ [📋 PLANNED]
│  StrategyObject: strategy_id, world_reference, model_reference     │
│  Cykl życia: NARODZINY → NOWA → TEST → DOJRZEWANIE → OBSERWACJA →  │
│                 ANALIZA → RANKING → AKTYWNA → SPADEK → ARCHIWUM     │
└──────────────────────────────┬──────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                   MEMORY EVOLUTION SYSTEM                         │ [📋 PLANNED]
└──────────────────────────────────┬──────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                      DECISION ENGINE                              │ [📋 PLANNED]
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Kluczowa Zasada (CRITICAL)

> **V4 NIE zastępuje V3.** 
> V4 jest warstwą **wykonującą decyzje** na podstawie wiedzy zgromadzonej przez V2 i V3.
> V3 jest warstwą **tworzącą mapę wiedzy** (światy, pamięć, metadane).
> V2 jest warstwą **interpretującą dane** (modele, analiza).

**Problem Aktualny (zgodnie z audytem):**
- ❌ V4 **nie ma dostępu do wiedzy V3** (brak importów, brak integracji)
- ❌ Brak mechanizmu transferu wiedzy V3 → V4
- ❌ V4 działa w izolacji

---

## 3. Wersjonowane Kontrakty Interfejsów

### 3.1 Kontrakt V2 → V3

#### Interfejs: `V2ToV3Bridge`

**Status:** ✅ **Zaimplementowany** (w `SSI/v2/integration/v2_to_v3_bridge.py`)

```python
# Kontrakt V2ToV3Bridge
class V2ToV3Bridge:
    """
    Most między V2 Model Laboratory a V3 World Memory System.
    Odpowiedzialny za transfer danych modelowych do światów wiedzy.
    """
    
    def __init__(self, v2_model_manager: V2ModelManager, 
                 v3_world_manager: V3WorldManager):
        """
        Inicjalizacja mostu V2→V3.
        
        Args:
            v2_model_manager: Manager modeli V2
            v3_world_manager: Manager światów V3
        """
        pass
    
    def transfer_model_output_to_worlds(self, model_id: str, 
                                         output_data: Dict[str, Any],
                                         timestamp: datetime) -> WorldDataPackage:
        """
        Transfer wyjścia modelu V2 do struktury światów V3.
        
        Args:
            model_id: Identyfikator modelu V2
            output_data: Dane wyjściowe modelu
            timestamp: Czas generacji danych
            
        Returns:
            WorldDataPackage: Pakiet danych gotowy do zapisu w V3
        """
        pass
    
    def create_world_from_model(self, model_id: str, 
                                 training_period: Tuple[datetime, datetime]) -> World:
        """
        Utworzenie świata V3 na podstawie modelu V2.
        
        Args:
            model_id: Identyfikator modelu
            training_period: Okres treningowy
            
        Returns:
            World: Nowy świat wiedzy
        """
        pass
```

**Klasa `WorldDataPackage`:**
```python
@dataclass
class WorldDataPackage:
    """Pakiet danych do transferu między V2 a V3."""
    model_id: str
    world_id: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime
    version: str = "1.0"
    
    def validate(self) -> bool:
        """Walidacja spójności pakietu."""
        return all([
            self.model_id,
            self.world_id,
            self.data,
            self.timestamp
        ])
```

**Status Implementacji:**
- ✅ `V2ToV3Bridge` - Istnieje
- ✅ `WorldDataPackage` - Istnieje
- ✅ Integracja z V2 Model Manager - Istnieje
- ⚠️ Integracja z V3 World Manager - Częściowo (brakuje pełnej integracji)

---

### 3.2 Kontrakt V3 → V4

#### Interfejs: `V3ToV4Bridge` (BRAKUJĄCY - CRITICAL)

**Status:** ❌ **Nie zaimplementowany** (wymagany przez `SSI/v3/__init__.py`)

```python
# Kontrakt V3ToV4Bridge - DO ZAIMPLEMENTOWANIA
class V3ToV4Bridge:
    """
    Most między V3 World Memory System a V4 Agent Evolution.
    Odpowiedzialny za transfer wiedzy ze światów do agentów.
    
    [ADR-001] Decyzja: Użyć wzorca Publisher-Subscriber
    [ADR-002] Decyzja: Transfer asynchroniczny z buforyzacją
    """
    
    def __init__(self, memory_manager: MemoryManager,
                 world_manager: WorldManager,
                 agent_birth_system: AgentBirthSystem):
        """
        Inicjalizacja mostu V3→V4.
        
        Args:
            memory_manager: Manager pamięci V3
            world_manager: Manager światów V3
            agent_birth_system: System narodzin agentów V4
        """
        self._subscribers: Dict[str, List[Agent]] = {}
        self._data_buffer: Dict[str, Deque[WorldDataPackage]] = {}
        pass
    
    def subscribe_agent(self, agent_id: str, world_ids: List[str]) -> None:
        """
        Zarejestrowanie agenta jako subskrybenta światów.
        
        Args:
            agent_id: Identyfikator agenta
            world_ids: Lista światów, które interesują agenta
        """
        for world_id in world_ids:
            if world_id not in self._subscribers:
                self._subscribers[world_id] = []
            self._subscribers[world_id].append(agent_id)
    
    def publish_world_update(self, world_package: WorldDataPackage) -> int:
        """
        Opublikowanie aktualizacji świata do subskrybentów.
        
        Args:
            world_package: Pakiet danych świata
            
        Returns:
            int: Liczba powiadomionych agentów
        """
        if world_package.world_id in self._subscribers:
            for agent_id in self._subscribers[world_package.world_id]:
                self._deliver_to_agent(agent_id, world_package)
            return len(self._subscribers[world_package.world_id])
        return 0
    
    def _deliver_to_agent(self, agent_id: str, 
                          world_package: WorldDataPackage) -> None:
        """
        Dostarczenie danych świata do agenta.
        
        [ADR-003] Decyzja: Asynchroniczna dostawa z timeout
        """
        # Implementacja asynchroniczna z buforyzacją
        if agent_id not in self._data_buffer:
            self._data_buffer[agent_id] = Deque(maxlen=100)
        self._data_buffer[agent_id].append(world_package)
        
        # Wyzwolenie przetwarzania przez agenta
        # (implementacja w AgentCore)
    
    def get_agent_knowledge(self, agent_id: str) -> List[WorldDataPackage]:
        """
        Pobranie buforowanych danych świata dla agenta.
        """
        return list(self._data_buffer.get(agent_id, []))
```

**Klasa `AgentKnowledgePackage`:**
```python
@dataclass
class AgentKnowledgePackage:
    """Pakiet wiedzy dla agenta V4."""
    agent_id: str
    world_data: List[WorldDataPackage]
    memory_snapshot: Dict[str, Any]
    timestamp: datetime
    version: str = "1.0"
    
    def to_agent_format(self) -> Dict[str, Any]:
        """Konwersja do formatu zrozumiałego dla agenta."""
        return {
            'agent_id': self.agent_id,
            'worlds': [w.to_dict() for w in self.world_data],
            'memory': self.memory_snapshot,
            'timestamp': self.timestamp.isoformat()
        }
```

**Status Implementacji:**
- ❌ `V3ToV4Bridge` - **BRAK** (priorytet P0)
- ❌ Integracja z V4 Agent Core - **BRAK**
- ❌ Mechanizm subskrypcji - **BRAK**

---

### 3.3 Kontrakt V3 Integration (BRAKUJĄCY)

**Status:** ❌ **Nie zaimplementowany** (wymagany przez `SSI/v3/__init__.py`)

```python
# Kontrakt V3Integration - DO ZAIMPLEMENTOWANIA
class V3Integration:
    """
    Główny interfejs integracyjny V3.
    Centralny punkt dostępu do wszystkich komponentów V3.
    
    [ADR-004] Decyzja: Singleton z lazy initialization
    """
    
    _instance: Optional['V3Integration'] = None
    
    def __new__(cls, config: Optional['V3Config'] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def initialize(self, config: 'V3Config') -> None:
        """Inicjalizacja integrates V3."""
        if not self._initialized:
            self.world_manager = WorldManager(config.world_config)
            self.memory_manager = MemoryManager(config.memory_config)
            self.integration_bridge = WorldIntegration(config)
            self.v2_bridge = V2ToV3Bridge(
                v2_model_manager=...,  # Z V2
                v3_world_manager=self.world_manager
            )
            self.v4_bridge = V3ToV4Bridge(
                memory_manager=self.memory_manager,
                world_manager=self.world_manager,
                agent_birth_system=...  # Z V4
            )
            self._initialized = True
    
    @property
    def world_manager(self) -> 'WorldManager':
        """Dostęp do World Manager."""
        if not self._initialized:
            raise RuntimeError("V3Integration not initialized")
        return self._world_manager
    
    @property
    def memory_manager(self) -> 'MemoryManager':
        """Dostęp do Memory Manager."""
        if not self._initialized:
            raise RuntimeError("V3Integration not initialized")
        return self._memory_manager
    
    @property
    def v4_bridge(self) -> 'V3ToV4Bridge':
        """Dostęp do mostu V3→V4."""
        if not self._initialized:
            raise RuntimeError("V3Integration not initialized")
        return self._v4_bridge

@dataclass
class V3Config:
    """Konfiguracja V3 Integration."""
    world_config: Dict[str, Any]
    memory_config: Dict[str, Any]
    integration_config: Dict[str, Any]
    send_to_v4: bool = False  # Domyslnie wylaczone do momentu implementacji V4
    buffer_size: int = 1000
    timeout_seconds: float = 30.0
```

**Status Implementacji:**
- ❌ `V3Integration` - **BRAK** (priorytet P0)
- ❌ `V3Config` - **BRAK** (priorytet P0)

---

## 4. Diagram Przepływu Danych

### 4.1 Główne Ścieżki Przepływu

```
┌─────────────────────────────────────────────────────────────────┐
│                           DATA FLOW DIAGRAM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  DATA_LAYER (CSV, Raw)                                            │
│       │                                                           │
│       ↓ [60% Training / 40% Observation]                         │
│  ┌─────────────────┐                                               │
│  │ V2 MODEL LAB    │                                               │
│  │                 │                                               │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  │ siec_01_    │  │ siec_02_    │  │ siec_03_    │          │
│  │  │ zmiana     │  │ amplituda   │  │ tempo       │          │
│  │  └─────────────┘  └─────────────┘  └─────────────┘          │
│  │  ┌─────────────┐  ┌─────────────┐                            │
│  │  │ siec_04_    │  │ Random      │                            │
│  │  │ synchroniz. │  │ Forest      │                            │
│  │  └─────────────┘  └─────────────┘                            │
│  └─────────────────┘                                               │
│       │                                                           │
│       ↓ [V2ToV3Bridge]                                             │
│  ┌─────────────────┐                                               │
│  │ V3 WORLD SYSTEM │                                               │
│  │                 │                                               │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │  │ World       │    │ Group       │    │ Pattern     │      │
│  │  │ Memory      │    │ Memory      │    │ Memory      │      │
│  │  └─────────────┘    └─────────────┘    └─────────────┘      │
│  │                                 ┌─────────────────────────────┐  │
│  │                                 │  TAGGING SYSTEM (7 kategorii) │  │
│  │                                 └─────────────────────────────┘  │
│  │                                 ┌─────────────────────────────┐  │
│  │                                 │  ECONOMIC ANALYSIS           │  │
│  │                                 │  (EV, Risk, Patterns)        │  │
│  │                                 └─────────────────────────────┘  │
│  └─────────────────┘                                               │
│       │                                                           │
│       ↓ [V3ToV4Bridge - SUBSCRIPTION]                              │
│  ┌─────────────────┐                                               │
│  │ V4 AGENT SYSTEM │                                               │
│  │                 │                                               │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │  │ Agent 1     │    │ Agent 2     │    │ Agent 3     │      │
│  │  │ (Analityk)  │    │ (Strateg)   │    │ (Eksperyment)│      │
│  │  └─────────────┘    └─────────────┘    └─────────────┘      │
│  │                 │                                               │
│  │  ┌─────────────────────────────────────────────────────────┐  │
│  │  │               ROOM_CORE (Komunikacja)                     │  │
│  │  └─────────────────────────────────────────────────────────┘  │
│  └─────────────────┘                                               │
│       │                                                           │
│       ↓ [Decision Request]                                        │
│  ┌─────────────────┐                                               │
│  │ DECISION LAB    │ ←─────────────────────────────────────────┘
│  │ (Planowany)     │                                               │
│  └─────────────────┘                                               │
│       │                                                           │
│       ↓                                                           │
│  ┌─────────────────┐                                               │
│  │ STRATEGY ENGINE │ ←─────────────────────────────────────────┘
│  │ (Planowany)     │                                               │
│  └─────────────────┘                                               │
│       │                                                           │
│       ↓ [Feedback Loop]                                            │
│  ┌─────────────────┐                                               │
│  │ MEMORY EVOLUTION │                                               │
│  │ (Planowany)     │                                               │
│  └─────────────────┘                                               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Granice Odpowiedzialności

```
┌─────────────────────────────────────────────────────────────────┐
│                   RESPONSIBILITY BOUNDARIES                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  DATA LAYER                                                   ││
│  │  ✓ Pobieranie danych (kursy, wyniki)                        ││
│  │  ✓ Archiwizacja historyczna                                  ││
│  │  ✓ Generowanie baz danych                                   ││
│  │  ✓ Przygotowywanie cech i trendów                           ││
│  │  ✗ interpretacja (→ V2)                                      ││
│  │  ✗ podejmowanie decyzji (→ V4)                              ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  V2 MODEL LABORATORY                                         ││
│  │  ✓ Trenowanie modeli na 60% danych                          ││
│  │  ✓ Walidacja modeli                                          ││
│  │  ✓ Obserwacja na 40% danych (bez uczenia)                    ││
│  │  ✓ Generowanie interpretacji świata                          ││
│  │  ✗ gromadzenie wiedzy (→ V3)                                  ││
│  │  ✗ podejmowanie decyzji (→ V4)                              ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  V3 WORLD MEMORY SYSTEM                                       ││
│  │  ✓ Tworzenie światów wiedzy                                   ││
│  │  ✓ Budowa pamięci światów                                     ││
│  │  ✓ Generowanie metadanych                                    ││
│  │  ✓ Tagowanie informacji (7 kategorii)                         ││
│  │  ✓ Analiza zależności między światami                         ││
│  │  ✓ Wykrywanie odwróconych wzorców                            ││
│  │  ✓ Wartość oczekiwana (EV) i analiza ekonomiczna              ││
│  │  ✗ podejmowanie decyzji (→ V4)                              ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  V4 AGENT EVOLUTION                                           ││
│  │  ✓ Narodziny agentów                                          ││
│  │  ✓ Ewolucja osobowości                                        ││
│  │  ✓ System zaufania między agentami                           ││
│  │  ✓ Pamięć agentów                                             ││
│  │  ✓ Podejmowanie decyzji (na podstawie V3)                   ││
│  │  ✗ Generowanie strategii (→ Strategy System)                 ││
│  │  ✗ Testowanie strategii (→ Laboratories)                      ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Działające Przykłady Użycia

### 5.1 Przykład 1: Transfer Danych V2 → V3

**Status:** ✅ **Działa** (zweryfikowany w CI)

```python
# Przykład: Transfer danych z modelu V2 do świata V3
from SSI.v2.models.model_manager import V2ModelManager
from SSI.v2.integration.v2_to_v3_bridge import V2ToV3Bridge
from SSI.v3.worlds.world_manager import WorldManager

# Inicjalizacja
v2_manager = V2ModelManager()
v3_world_manager = WorldManager()
bridge = V2ToV3Bridge(v2_manager, v3_world_manager)

# Trenowanie modelu V2
model_id = "siec_01_zmiana_kursow"
v2_manager.train_model(model_id, training_data)

# Transfer wyjścia modelu do V3
model_output = v2_manager.get_model_output(model_id)
world_package = bridge.transfer_model_output_to_worlds(
    model_id=model_id,
    output_data=model_output,
    timestamp=datetime.now()
)

# Utworzenie świata
world = bridge.create_world_from_model(
    model_id=model_id,
    training_period=(start_date, end_date)
)

# Walidacja
assert world_package.validate(), "Pakiet danych nieprawidłowy"
assert world.world_id in v3_world_manager.get_world_ids(), "Świat nie został utworzony"
```

**Test CI:**
```bash
# Test w CI - powinien przejść
python -m pytest tests/integration/test_v2_to_v3_integration.py::test_model_to_world_transfer -v
```

### 5.2 Przykład 2: Subskrypcja Agenta V4 do Światów V3

**Status:** ❌ **Nie działa** (brakujące komponenty)

```python
# Przykład: Agent V4 subskrybujący światy V3 (DO ZAIMPLEMENTOWANIA)
from SSI.v3.integration.v3_integration import V3Integration
from SSI.v4.agents.agent_core import Agent
from SSI.v4.agents.agent_birth_system import AgentBirthSystem

# Inicjalizacja V3
v3_integration = V3Integration(config)
v3_integration.initialize()

# Tworzenie agenta V4
birth_system = AgentBirthSystem()
agent = birth_system.create_agent(
    agent_type="Analityk",
    personality_vector=...</n)

# Subskrypcja agenta do światów V3
v3_integration.v4_bridge.subscribe_agent(
    agent_id=agent.agent_id,
    world_ids=["zmiana_kursow", "amplituda", "dynamika"]
)

# Symulacja aktualizacji świata
world_package = ...  # Pakiet z V3
v3_integration.v4_bridge.publish_world_update(world_package)

# Agent otrzymuje dane
knowledge = agent.get_knowledge()
assert len(knowledge.worlds) > 0, "Agent nie otrzymał danych ze świata"
```

**Status Implementacji:**
- ❌ Brak `V3ToV4Bridge`
- ❌ Brak integracji V3 w V4
- ❌ Brak testu CI

### 5.3 Przykład 3: Pełny Przepływ V2 → V3 → V4

**Status:** ❌ **Nie działa** (blokujące braki integracji)

```python
# Przykład: Pełny przepływ V2→V3→V4 (CEL SPRINT 9)
from SSI.v2.models.model_manager import V2ModelManager
from SSI.v3.integration.v3_integration import V3Integration
from SSI.v4.agents.agent_core import Agent

# 1. Trenowanie V2
v2_manager = V2ModelManager()
v2_manager.train_all_models()

# 2. Transfer do V3
v3_integration = V3Integration(config)
v3_integration.v2_bridge.transfer_all_model_outputs()

# 3. Tworzenie agentów V4
agents = []
for i in range(3):
    agent = Agent(f"Agent_{i}")
    agents.append(agent)

# 4. Subskrypcja agentów
for agent in agents:
    v3_integration.v4_bridge.subscribe_agent(
        agent_id=agent.agent_id,
        world_ids=v3_integration.world_manager.get_all_world_ids()
    )

# 5. Decyzja agenta (na podstawie wiedzy V3)
for agent in agents:
    decision = agent.make_decision()
    assert decision.is_valid(), f"Agent {agent.agent_id} podjął nieprawidłową decyzję"
    assert decision.knowledge_source == "V3", "Decyzja nie bazuje na V3"
```

**Kryteria Akceptacji:**
- [ ] V2 generuje dane wyjściowe
- [ ] V2→V3 bridge przekazuje dane
- [ ] V3 tworzy światy i pamięć
- [ ] V3→V4 bridge dostarcza dane agentom
- [ ] Agenci podejmują decyzje na podstawie V3
- [ ] Test w CI przechodzi (`test_full_v2_v3_v4_flow`)

---

## 6. Rejestr Funkcjonalności

### 6.1 Matryca Statusów Funkcjonalności

| ID | Funkcjonalność | Warstwa | Status | Test | Uwagi |
|----|----------------|--------|--------|------|-------|
| **V2-001** | Pobieranie kursów | V2 | ✅ **operational** | `test_data_fetcher` | Działa w produkcji |
| **V2-002** | Pobieranie wyników | V2 | ✅ **operational** | `test_results_fetcher` | Działa w produkcji |
| **V2-003** | Generowanie bazy danych | V2 | ✅ **operational** | `test_database_generator` | Działa w produkcji |
| **V2-004** | Model siec_01_zmiana_kursow | V2 | ✅ **implemented** | `test_siec_01` | Gotowy do integracji |
| **V2-005** | Model siec_02_amplituda | V2 | ✅ **implemented** | `test_siec_02` | Gotowy do integracji |
| **V2-006** | Model siec_03_tempo | V2 | ✅ **implemented** | `test_siec_03` | Gotowy do integracji |
| **V2-007** | Model siec_04_synchronizacja | V2 | ✅ **implemented** | `test_siec_04` | Gotowy do integracji |
| **V2-008** | RandomForest Classifier | V2 | ✅ **implemented** | `test_random_forest` | Gotowy do integracji |
| **V2-009** | Integracja V2→V3 (V2ToV3Bridge) | V2/V3 | ✅ **implemented** | `test_v2_to_v3_bridge` | Działa |
| **V3-001** | World Structure | V3 | ⚠️ **implemented** | `test_world_structure` | Częściowo (brakuje integracji) |
| **V3-002** | World Memory | V3 | ⚠️ **implemented** | `test_world_memory` | Częściowo (brakuje integracji) |
| **V3-003** | Tagging System (7 kategorii) | V3 | ⚠️ **implemented** | `test_tagging` | Częściowo (brakuje testów) |
| **V3-004** | Economic Analysis (EV, Risk) | V3 | ⚠️ **implemented** | `test_economic_analysis` | Częściowo (brakuje testów) |
| **V3-005** | V3Integration | V3 | ❌ **planned** | - | **BRAK - P0** |
| **V3-006** | V3Config | V3 | ❌ **planned** | - | **BRAK - P0** |
| **V3-007** | V3ToV4Bridge | V3/V4 | ❌ **planned** | - | **BRAK - P0** |
| **V4-001** | Agent Core | V4 | ⚠️ **implemented** | - | Brak integracji z V3 |
| **V4-002** | Agent Birth System | V4 | ⚠️ **implemented** | - | Brak integracji z V3 |
| **V4-003** | Personality Vector | V4 | ⚠️ **implemented** | - | Brak integracji z V3 |
| **V4-004** | ROOM_CORE | V4 | ⚠️ **implemented** | - | Brak integracji z V3 |
| **V4-005** | Trust System | V4 | ⚠️ **implemented** | - | Brak integracji z V3 |
| **V4-006** | V4 korzysta z V3 (World Memory) | V4 | ❌ **planned** | - | **BRAK - P0** |
| **INT-001** | Pełny przepływ V2→V3 |Integration | ✅ **tested** | `test_v2_to_v3_flow` | Działa |
| **INT-002** | Pełny przepływ V2→V3→V4 | Integration | ❌ **planned** | - | **BRAK - P0** |

### 6.2 Legendy Statusów

| Status | Opis | Kryteria |
|--------|------|----------|
| **planned** | Zaplanowana, nie zaimplementowana | Brak kodu |
| **implemented** | Zaimplementowana, nie przetestowana | Kod istnieje, brak testów |
| **tested** | Zaimplementowana i przetestowana | Kod + testy jednostkowe |
| **operational** | Działa w produkcji/integracji | Kod + testy + potwierdzenie w internecie |

---

## 7. ADR (Architecture Decision Records)

### ADR-001: Synchronizacja między V3 a V4

**Status:** ✅ **Zatwierdzony**

**Kontekst:**
Potrzebny mechanizm transferu wiedzy ze świata V3 do agentów V4 z zapewnieniem:
- Niskiej latencji
- Spójności danych
- Możliwości buforowania
- Obsługi wielu agentów

**Decyzja:**
Zastosować wzorzec **Publisher-Subscriber** z:
- Asynchroniczną dostawą danych
- Buforowaniem po stronie V3 (V3ToV4Bridge)
- Subskrypcją agentów do konkretnych światów
- Timeout na przetwarzanie

**Konsekwencje:**
✅ Lukacja między V3 a V4
✅ Skalowalność (wiele agentów)
✅ Elastyczność (agenci wybierają interesujące ich światy)
⚠️ Złożoność implementacji
⚠️ Konieczność zarządzania buforami

**Alternatywy rozważane:**
1. **Direct Call** - Odrzucone: zbyt wolne, blokujące
2. **Shared Memory** - Odrzucone: złożone zarządzanie konkurencyjnością
3. **Message Queue** - Odrzucone: nadmierna złożoność dla obecnych potrzeb

---

### ADR-002: Persistence Polityka

**Status:** ✅ **Zatwierdzony**

**Kontekst:**
System generuje dużą ilość danych (światy, pamięć, zdecydje) które muszą być:
- Trwałe (persistent)
- Wersjonowane
- Szybko dostępne
- Możliwe do przywrócenia

**Decyzja:**
Zastosować **warstwową strategię persistence**:

1. **Hot Storage (Pamięć operacyjna)**
   - SQLite (dla małej skali)
   - In-memory cache (dla szybkiego dostępu)
   - Format: JSON/Protobuf

2. **Cold Storage (Archiwum)**
   - PostgreSQL (dla produkcji)
   - Parquet (dla danych historycznych)
   - Versioned buckets (S3/GCS)

**Retencja:**
- **Hot Data (bieżące światy, pamięć):** 30 dni
- **Warm Data (historyczne światy):** 1 rok
- **Cold Data (archiwum):** 5 lat

**Backup:**
- Codzienny backup Hot Storage
- Tygodniowy backup Warm Storage
- Miesięczny backup Cold Storage

---

### ADR-003: Polityka Danych i Granice Modułów

**Status:** ✅ **Zatwierdzony**

**Kontekst:**
Konsekwentne zarządzanie danymi między modułami z zapewnieniem:
- Izolacji modułów
- Jasnych kontraktów interfejsów
- Możliwości walidacji

**Decyzja:**

#### Granice Modułów
```
┌─────────────────────────────────────────────────────────────────┐
│  MODUŁ V2                                                          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Granica: HealthyCheckV2                                       ││
│  │  - Sprawdza integralność modeli                              ││
│  │  - Waliduje dane wyjściowe                                   ││
│  └─────────────────────────────────────────────────────────────┘│
│  Wyjście: WorldDataPackage (zwalidowany)                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  MODUŁ V3                                                          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Granica: HealthyCheckV3                                       ││
│  │  - Sprawdza integralność światów                               ││
│  │  - Waliduje pamięć i metadane                                 ││
│  └─────────────────────────────────────────────────────────────┘│
│  Wejście: WorldDataPackage (od V2)                                │
│  Wyjście: AgentKnowledgePackage (dla V4)                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  MODUŁ V4                                                          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Granica: HealthyCheckV4                                       ││
│  │  - Sprawdza stan agentów                                      ││
│  │  - Waliduje decyzje                                           ││
│  └─────────────────────────────────────────────────────────────┘│
│  Wejście: AgentKnowledgePackage (od V3)                          │
│  Wyjście: Decision (decyzja agenta)                              │
└─────────────────────────────────────────────────────────────────┘
```

#### Kontrakty Data

**V2 → V3:**
```python
@dataclass
class V2ToV3Contract:
    """Kontrakt danych V2 → V3."""
    model_id: str  # Format: "siec_[01-04]_[nazwa]" | "RandomForest" | "Classifier"
    timestamp: datetime  # Czas generacji
    data: Dict[str, Any]  # Dane modelu (znormalizowane)
    metadata: Dict[str, Any]  # Metadane (accuracy, features, itp.)
    version: str = "1.0"  # Wersja kontraktu
    
    def validate(self) -> bool:
        """Walidacja kontraktu."""
        required_fields = ['model_id', 'timestamp', 'data']
        return all(getattr(self, field) for field in required_fields)
```

**V3 → V4:**
```python
@dataclass
class V3ToV4Contract:
    """Kontrakt danych V3 → V4."""
    agent_id: str  # Identyfikator agenta
    world_id: str  # Identyfikator świata
    knowledge_type: str  # "world" | "group" | "pattern" | "historical"
    data: Dict[str, Any]  # Dane wiedzy
    confidence: float  # Poziom pewności (0.0 - 1.0)
    timestamp: datetime  # Czas generacji
    version: str = "1.0"  # Wersja kontraktu
    
    def validate(self) -> bool:
        """Walidacja kontraktu."""
        required_fields = ['agent_id', 'world_id', 'knowledge_type', 'data', 'timestamp']
        return all(getattr(self, field) for field in required_fields) and \
               0.0 <= self.confidence <= 1.0
```

---

## 8. Plan Integracji (Roadmap Sprint 9)

### 8.1 Priorytety (P0 - Krytyczne)

| Zadanie | Status | Czas | Zależności | Blokuje |
|---------|--------|------|-------------|---------|
| **IMP-001** | Zaimplementować `V3ToV4Bridge` | 📋 Todo | V3, V4 | INT-002 |
| **IMP-002** | Zaimplementować `V3Integration` | 📋 Todo | V3 | IMP-001 |
| **IMP-003** | Zaimplementować `V3Config` | 📋 Todo | - | IMP-002 |
| **IMP-004** | Dodać importy V3 w V4 (`agent_core.py`) | 📋 Todo | IMP-001 | INT-002 |
| **IMP-005** | Zaimplementować subskrypcję V3→V4 | 📋 Todo | IMP-001 | INT-002 |
| **INT-002** | Pełny przepływ V2→V3→V4 | ❌ Blokowany | IMP-001-005 | - |

### 8.2 Priorytety (P1 - Wysokie)

| Zadanie | Status | Czas | Zależności |
|---------|--------|------|-------------|
| **TST-001** | Testy jednostkowe `V3ToV4Bridge` | 📋 Todo | IMP-001 |
| **TST-002** | Testy jednostkowe `V3Integration` | 📋 Todo | IMP-002 |
| **TST-003** | Test integracyjny V2→V3→V4 | 📋 Todo | INT-002 |
| **DOC-001** | Zaktualizować statusy w `10_IMPLEMENTATION_MAP.md` | 📋 Todo | INT-002 |
| **DOC-002** | Zaktualizować statusy w `README.md` | 📋 Todo | INT-002 |

### 8.3 Priorytety (P2 - Średnie)

| Zadanie | Status | Czas | Zależności |
|---------|--------|------|-------------|
| **DOC-003** | Utworzyć `stuktura1.csv` - `stuktura4.csv` (wersjonowane) | 📋 Todo | - |
| **DOC-004** | Dodać dokumentację API V3→V4 | 📋 Todo | IMP-001 |
| **OPT-001** | Optymalizacja buforowania V3→V4 | 📋 Todo | INT-002 |

---

## 9. Kryteria Akceptacji Sprint 9

### 9.1 Kryteria Techniczne

- [ ] **Brak sprzecznych statusów V3 i V4 w dokumentacji**
  - `10_IMPLEMENTATION_MAP.md` zsynchronizowany
  - `README.md` zsynchronizowany
  - `01_SYSTEM_ARCHITECTURE.md` zsynchronizowany
  
- [ ] **Każde wymaganie krytyczne ma identyfikator i powiązany test**
  - Wszystkie P0 mają testy jednostkowe
  - Wszystkie kontrakty są walidowane
  - Testy integracyjne przechodzą

- [ ] **Instrukcja uruchomienia działa na czystym checkout**
  ```bash
  # Powinno działać na nowym clone
  git clone <repo>
  cd aplikacjaTyperBetAi
  python -m pip install -r requirements.txt
  python -m pytest tests/integration/test_v2_v3_v4_flow.py -v
  ```

- [ ] **Diagram odpowiada rzeczywistym importom i kierunkom przepływu**
  - Wszystkie strzałki na diagramie mają odzwierciedlenie w kodzie
  - Brak "martwych" zależności

- [ ] **Kontrola linków, komend i kodowania przechodzi w CI**
  - `python -m compileall` przechodzi
  - `python -m pip check` przechodzi
  - Wszystkie linki w dokumentacji działają
  - Brak mojibake (poprawne kodowanie UTF-8)

- [ ] **Dokument audytu pozostaje powiązany z pozycjami roadmapy**
  - `AUDYT_ZGODNOSCI...md` ma odniesienia do zadań
  - Wszystkie F-XX mają przypisane zadania

### 9.2 Kryteria Biznesowe

- [ ] V2 generuje dane dla V3
- [ ] V3 tworzy światy na podstawie V2
- [ ] V4 otrzymuje dane z V3
- [ ] Agenci V4 podejmują decyzje na podstawie wiedzy V3
- [ ] Pełny przepływ V2→V3→V4 działa w CI

---

## 10. Implementacja - checklista

### 10.1 V3ToV4Bridge

```python
# Plik: SSI/v3/integration/v3_to_v4_bridge.py
from dataclasses import dataclass, field
from typing import Dict, List, Deque, Optional, Any
from datetime import datetime
from collections import defaultdict
import threading
import asyncio

@dataclass
class AgentKnowledgePackage:
    """Pakiet wiedzy dla agenta V4."""
    agent_id: str
    world_data: List[Dict[str, Any]]
    memory_snapshot: Dict[str, Any]
    timestamp: datetime
    version: str = "1.0"

class V3ToV4Bridge:
    """
    Most między V3 World Memory System a V4 Agent Evolution.
    Implementacja wzorca Publisher-Subscriber.
    """
    
    def __init__(self):
        self._subscribers: Dict[str, List[str]] = defaultdict(list)
        self._data_buffer: Dict[str, Deque[Dict[str, Any]]] = defaultdict(
            lambda: Deque(maxlen=100)
        )
        self._lock = threading.RLock()
        self._initialized = False
    
    def initialize(self, world_manager: Any, memory_manager: Any) -> None:
        """Inicjalizacja z managerami V3."""
        self.world_manager = world_manager
        self.memory_manager = memory_manager
        self._initialized = True
    
    def subscribe_agent(self, agent_id: str, world_ids: List[str]) -> None:
        """Zarejestruj agenta jako subskrybenta światów."""
        with self._lock:
            for world_id in world_ids:
                self._subscribers[world_id].append(agent_id)
    
    def unsubscribe_agent(self, agent_id: str) -> None:
        """Wyrejestruj agenta."""
        with self._lock:
            for world_id, agents in self._subscribers.items():
                if agent_id in agents:
                    agents.remove(agent_id)
    
    def publish_world_update(self, world_id: str, 
                              data: Dict[str, Any],
                              timestamp: datetime) -> int:
        """
        Opublikuj aktualizację świata do subskrybentów.
        
        Returns:
            Liczba powiadomionych agentów
        """
        with self._lock:
            agents_to_notify = self._subscribers.get(world_id, [])
            
            for agent_id in agents_to_notify:
                package = {
                    'world_id': world_id,
                    'data': data,
                    'timestamp': timestamp
                }
                self._data_buffer[agent_id].append(package)
            
            return len(agents_to_notify)
    
    def get_agent_updates(self, agent_id: str) -> List[Dict[str, Any]]:
        """Pobierz zbuforowane aktualizacje dla agenta."""
        with self._lock:
            updates = list(self._data_buffer.get(agent_id, []))
            self._data_buffer[agent_id].clear()
            return updates
    
    def get_agent_knowledge(self, agent_id: str) -> AgentKnowledgePackage:
        """Pobierz pełny pakiet wiedzy dla agenta."""
        updates = self.get_agent_updates(agent_id)
        
        # Dodaj snapshot pamięci
        memory_snapshot = self.memory_manager.get_snapshot() if self._initialized else {}
        
        return AgentKnowledgePackage(
            agent_id=agent_id,
            world_data=updates,
            memory_snapshot=memory_snapshot,
            timestamp=datetime.now()
        )
```

### 10.2 V3Integration

```python
# Plik: SSI/v3/integration/v3_integration.py
from dataclasses import dataclass
from typing import Optional, Any
import threading

@dataclass
class V3Config:
    """Konfiguracja V3 Integration."""
    world_config: Dict[str, Any]
    memory_config: Dict[str, Any]
    send_to_v4: bool = False
    buffer_size: int = 1000
    timeout_seconds: float = 30.0

class V3Integration:
    """
    Główny interfejs integracyjny V3.
    Singleton z lazy initialization.
    """
    _instance: Optional['V3Integration'] = None
    _lock = threading.Lock()
    
    def __new__(cls, config: Optional[V3Config] = None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def initialize(self, config: V3Config) -> None:
        """Inicjalizacja integratora V3."""
        if not self._initialized:
            from SSI.v3.worlds.world_manager import WorldManager
            from SSI.v3.memory.memory_manager import MemoryManager
            from SSI.v3.integration.v3_to_v4_bridge import V3ToV4Bridge
            from SSI.v2.integration.v2_to_v3_bridge import V2ToV3Bridge
            
            self.config = config
            self.world_manager = WorldManager(config.world_config)
            self.memory_manager = MemoryManager(config.memory_config)
            self.v2_bridge = V2ToV3Bridge(
                v2_model_manager=None,  # Będzie ustawione później
                v3_world_manager=self.world_manager
            )
            self.v4_bridge = V3ToV4Bridge()
            self.v4_bridge.initialize(self.world_manager, self.memory_manager)
            self._initialized = True
    
    @property
    def is_initialized(self) -> bool:
        return self._initialized
    
    @property
    def world_manager(self) -> Any:
        if not self._initialized:
            raise RuntimeError("V3Integration not initialized")
        return self._world_manager
    
    @world_manager.setter
    def world_manager(self, value: Any) -> None:
        self._world_manager = value
    
    @property
    def memory_manager(self) -> Any:
        if not self._initialized:
            raise RuntimeError("V3Integration not initialized")
        return self._memory_manager
    
    @memory_manager.setter
    def memory_manager(self, value: Any) -> None:
        self._memory_manager = value
    
    @property
    def v4_bridge(self) -> Any:
        if not self._initialized:
            raise RuntimeError("V3Integration not initialized")
        return self._v4_bridge
```

### 10.3 Integracja V4 z V3

```python
# Plik: SSI/v4/__init__.py (dodać importy)
# Istniejące importy...

# Nowe importy - Integracja z V3
try:
    from ..v3.integration.v3_integration import V3Integration
    from ..v3.integration.v3_to_v4_bridge import V3ToV4Bridge
    from ..v3.memory.memory_manager import MemoryManager
    from ..v3.worlds.world_manager import WorldManager
    V3_AVAILABLE = True
except ImportError as e:
    V3_AVAILABLE = False
    V3_IMPORT_ERROR = str(e)

# Plik: SSI/v4/agents/agent_core.py (modyfikacje)
class Agent:
    # ... istniejący kod ...
    
    def __init__(self, agent_id: str, config: Any = None):
        # ... istniejący kod ...
        
        # Integracja z V3
        self.v3_integration = None
        self.v3_knowledge = []
        
        if V3_AVAILABLE:
            self._connect_to_v3()
    
    def _connect_to_v3(self) -> None:
        """Połącz z V3 Integration."""
        v3_integration = V3Integration()
        if not v3_integration.is_initialized:
            # Inicjalizacja leniwa
            from SSI.v3.integration.v3_integration import V3Config
            v3_config = V3Config(
                world_config={},
                memory_config={},
                send_to_v4=True
            )
            v3_integration.initialize(v3_config)
            self.v3_integration = v3_integration
            
            # Subskrypcja do wszystkich światów
            all_worlds = self.v3_integration.world_manager.get_all_world_ids()
            self.v3_integration.v4_bridge.subscribe_agent(
                agent_id=self.agent_id,
                world_ids=all_worlds
            )
    
    def update_knowledge_from_v3(self) -> None:
        """Aktualizuj wiedzę z V3."""
        if self.v3_integration:
            knowledge_package = self.v3_integration.v4_bridge.get_agent_knowledge(
                self.agent_id
            )
            self.v3_knowledge = knowledge_package.world_data
    
    def make_decision(self, context: Any = None) -> Any:
        """Podejmij decyzję (na podstawie wiedzy V3)."""
        # Aktualizuj wiedzę z V3
        self.update_knowledge_from_v3()
        
        # ... istniejąca logika decyzji ...
        
        # Uwzględnij wiedzę V3 w decyzji
        if self.v3_knowledge:
            # Tutaj zintegrować wiedzę V3 z procesem decyzyjnym
            pass
        
        return decision
```

---

## 11. Testy (Do Dodania)

### 11.1 Test Jednostkowy V3ToV4Bridge

```python
# Plik: tests/unit/test_v3_to_v4_bridge.py
import pytest
from datetime import datetime
from SSI.v3.integration.v3_to_v4_bridge import V3ToV4Bridge

def test_v3_to_v4_bridge_initialization():
    """Test inicjalizacji mostu V3→V4."""
    bridge = V3ToV4Bridge()
    assert not bridge._initialized
    
    # Mock managerów
    mock_world_manager = type('MockWorldManager', (), {
        'get_all_world_ids': lambda: ['world1', 'world2']
    })()
    mock_memory_manager = type('MockMemoryManager', (), {
        'get_snapshot': lambda: {'memory': 'data'}
    })()
    
    bridge.initialize(mock_world_manager, mock_memory_manager)
    assert bridge._initialized


def test_v3_to_v4_bridge_subscription():
    """Test subskrypcji agentów."""
    bridge = V3ToV4Bridge()
    
    bridge.subscribe_agent('Agent1', ['world1', 'world2'])
    bridge.subscribe_agent('Agent2', ['world1'])
    
    assert len(bridge._subscribers['world1']) == 2
    assert len(bridge._subscribers['world2']) == 1
    assert 'Agent1' in bridge._subscribers['world1']
    assert 'Agent2' in bridge._subscribers['world1']


def test_v3_to_v4_bridge_publish():
    """Test publikacji aktualizacji świata."""
    bridge = V3ToV4Bridge()
    bridge.subscribe_agent('Agent1', ['world1'])
    
    timestamp = datetime.now()
    notification_count = bridge.publish_world_update(
        world_id='world1',
        data={'key': 'value'},
        timestamp=timestamp
    )
    
    assert notification_count == 1
    
    # Sprawdź bufor agenta
    updates = bridge.get_agent_updates('Agent1')
    assert len(updates) == 1
    assert updates[0]['world_id'] == 'world1'


def test_v3_to_v4_bridge_knowledge_package():
    """Test pakietu wiedzy."""
    bridge = V3ToV4Bridge()
    
    mock_world_manager = type('MockWorldManager', (), {})()
    mock_memory_manager = type('MockMemoryManager', (), {
        'get_snapshot': lambda: {'ev': 2.5, 'risk': 0.1}
    })()
    
    bridge.initialize(mock_world_manager, mock_memory_manager)
    bridge.publish_world_update('world1', {'data': 'test'}, datetime.now())
    bridge.subscribe_agent('Agent1', ['world1'])
    
    package = bridge.get_agent_knowledge('Agent1')
    assert package.agent_id == 'Agent1'
    assert package.memory_snapshot == {'ev': 2.5, 'risk': 0.1}
    assert len(package.world_data) == 0  # Bo wywołaliśmy get_agent_updates wcześniej
```

### 11.2 Test Integracyjny V2→V3→V4

```python
# Plik: tests/integration/test_v2_v3_v4_flow.py
import pytest
from datetime import datetime

def test_full_v2_v3_v4_flow():
    """Test pełnego przepływu V2→V3→V4."""
    # 1. Inicjalizacja V2
    from SSI.v2.models.model_manager import V2ModelManager
    v2_manager = V2ModelManager()
    
    # Mock danych treningowych
    training_data = {'features': [...], 'labels': [...]}
    
    # 2. Trenowanie modelu V2
    model_id = 'siec_01_zmiana_kursow'
    v2_manager.train_model(model_id, training_data)
    
    # 3. Inicjalizacja V3
    from SSI.v3.integration.v3_integration import V3Integration, V3Config
    v3_config = V3Config(
        world_config={},
        memory_config={},
        send_to_v4=True
    )
    v3_integration = V3Integration(v3_config)
    
    # 4. Transfer V2→V3
    model_output = v2_manager.get_model_output(model_id)
    v3_integration.v2_bridge.transfer_model_output_to_worlds(
        model_id=model_id,
        output_data=model_output,
        timestamp=datetime.now()
    )
    
    # 5. Utworzenie świata
    world = v3_integration.v2_bridge.create_world_from_model(
        model_id=model_id,
        training_period=(datetime.now(), datetime.now())
    )
    assert world.world_id in v3_integration.world_manager.get_all_world_ids()
    
    # 6. Inicjalizacja V4
    from SSI.v4.agents.agent_birth_system import AgentBirthSystem
    birth_system = AgentBirthSystem()
    agent = birth_system.create_agent('Agent1')
    
    # 7. Subskrypcja V3→V4
    all_worlds = v3_integration.world_manager.get_all_world_ids()
    v3_integration.v4_bridge.subscribe_agent(
        agent_id=agent.agent_id,
        world_ids=all_worlds
    )
    
    # 8. Test decyzji agenta
    decision = agent.make_decision()
    assert decision is not None
    assert hasattr(decision, 'is_valid')
    assert decision.is_valid()
```

---

## 12.Podsumowanie i Rekomendacje

### 12.1 Podsumowanie Stanu Integracji

| Komponent | Status | Uwagi |
|-----------|--------|-------|
| **V2 Model Laboratory** | ✅ **Gotowe** | Działa, generuje dane |
| **V3 World Memory System** | ⚠️ **Częściowo** | Brak integracji z V4 |
| **V4 Agent Evolution** | ⚠️ **Częściowo** | Brak dostępu do V3 |
| **V2→V3 Integration** | ✅ **Gotowe** | Działa (V2ToV3Bridge) |
| **V3→V4 Integration** | ❌ **Brak** | **P0 - Krytyczne** |
| **Pełny Flow V2→V3→V4** | ❌ **Brak** | Blokowany przez V3→V4 |

### 12.2 Rekomendacje Wdrożeniowe

1. **Priorytet 0 (Blokujące):**
   - Zaimplementować `V3ToV4Bridge` (1-2 dni)
   - Zaimplementować `V3Integration` i `V3Config` (1-2 dni)
   - Dodać integrację V3 w V4 (1 dzień)

2. **Priorytet 1 (Wymagane):**
   - Dodać testy jednostkowe (1-2 dni)
   - Dodać test integracyjny V2→V3→V4 (1 dzień)
   - Zaktualizować statusy dokumentacji (1 dzień)

3. **Priorytet 2 (Optymalizacja):**
   - Poprawić kodowanie UTF-8
   - Dodać `stuktura1.csv` - `stuktura4.csv`
   - Dodać dokumentację API

### 12.3 Kryteria Zakończenia Sprint 9

Sprint 9 można uznać za **ukończony**, gdy:

- [ ] `V3ToV4Bridge` zaimplementowany i przetestowany
- [ ] `V3Integration` zaimplementowany i przetestowany
- [ ] V4 korzysta z V3 (dane i wiedza)
- [ ] Pełny przepływ V2→V3→V4 działa
- [ ] Test integracyjny przechodzi w CI
- [ ] Statusy V2, V3, V4 zsynchronizowane
- [ ] Dokumentacja zaktualizowana

---

## Aneks A - Odniesienia do Źródeł

### A.1 Dokumenty powiązane

| Dokument | Sekcja | Odniesienie |
|----------|--------|-------------|
| `01_SYSTEM_ARCHITECTURE.md` | 2.4 | Architektura V4, zależności V3→V4 |
| `10_IMPLEMENTATION_MAP.md` | 3.4 | Faza 4: V4 Agent System |
| `10_IMPLEMENTATION_MAP.md` | 4.2 | Tabela zależności V3→V4 |
| `AUDYT_ZGODNOSCI...md` | F-03 | Niespójne statusy V3/V4 |
| `AUDYT_ZGODNOSCI...md` | F-12 | Zakleszczenie decyzji V4 |
| `Analiza Spojności...md` | 1 | Brakujące komponenty integracyjne |

### A.2 Kod powiązany

| Plik | Odniesienie |
|------|-------------|
| `SSI/v2/integration/v2_to_v3_bridge.py` | ✅ Istnieje - V2ToV3Bridge |
| `SSI/v3/__init__.py` | ❌ Wymaga V3Integration, V3Config, V3ToV4Bridge |
| `SSI/v3/integration/world_integration.py` | ⚠️ częściowo - brakuje V3→V4 |
| `SSI/v4/agent_core.py` | ❌ Brak integracji z V3 |
| `SSI/v4/__init__.py` | ❌ Brak importów V3 |

---

**Status Dokumentu:** Aktywny (w trakcie implementacji)  
**Wersja:** 1.0  
**Zgodność z Źródłami:** `01_SYSTEM_ARCHITECTURE.md`, `10_IMPLEMENTATION_MAP.md`, Audyt 2026-07-30  
**Ostatnia Aktualizacja:** 2026-07-31  
**Autor:** SSI Documentation System (Sprint 9)

---

> **UWAGA:** Ten dokument jest **living document** - powinien być aktualizowany wraz z postępem implementacji. Wszystkie zmiany powinny być weryfikowane przez testy w CI.
