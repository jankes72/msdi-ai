# Sprint 11 - REFACTORED: Uniwersalna Magistrala Danych SSI V5

**Wersja dokumentu:** 2.0  
**Data utworzenia:** 2026-07-31  
**Status:** AKTYWNY - Nowa Architektura  
**Autor:** MSDI AI / SSI System + Mistral Vibe  
**Podstawa:** `SSI_V5_ROADMAP.md`, `PROJECT_RULES.md`, Dyskusja Architekturalna  

---

## 🎯 NOWA WIZJA ARCHITEKTURY

**Problem z poprzednim podejściem:** Kopiowanie kodu dla V3, V4, Laboratoriów itd. prowadziłoby do:
- Duplikacji kodu
- Trudnego utrzymania
- Braku spójności
- Problemów ze skalowalnością

**Rozwiązanie:** Zbudować **uniwersalną magistralę danych** z:
1. **Wspólnym interfejsem kolektorów** (BaseCollector)
2. **Uniwersalnym pakietem wiedzy** (SSIKnowledgePackage)
3. **Oddzieleniem zbierania danych od ich przetwarzania**

---

## 🏗️ NOWA ARCHITEKTURA SSI V5

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ŹRÓDŁA DANYCH                                   │
├─────────────────┬─────────────────┬─────────────────┬─────────────────┤
│   V2 Models      │   V3 Knowledge   │   V4 Agents      │   Laboratories   │
│   - Siec 01-04   │   - Worlds      │   - Personalities│   - World Lab   │
│   - RandomForest  │   - Memory       │   - Strategies   │   - Type Lab    │
│   - Classifiers   │   - Patterns     │   - Decisions    │   - Group Lab   │
└────────┬─────────┴────────┬─────────┴────────┬─────────┴────────┬───────┘
         │                 │                 │                 │
         ▼                 ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  BASE COLLECTORS (Wspólny Interfejs)                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  BaseCollector (ABC)                                         │   │
│  │    ├── collect() -> KnowledgePackage                          │   │
│  │    ├── validate() -> bool                                    │   │
│  │    └── get_source_type() -> SourceType                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌───────────────────┐  ┌───────────────────┐  ┌─────────────────┐   │
│  │  V2DataCollector   │  │  V3DataCollector   │  │ V4DataCollector  │   │
│  │   (Sprint 11.1)    │  │   (Sprint 11.2)    │  │  (Sprint 11.3)   │   │
│  └───────────────────┘  └───────────────────┘  └─────────────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  ExternalKnowledgeCollector                                   │   │
│  │    - Panel Programisty                                        │   │
│  │    - Laboratoria (Świat, Typy, Grupy, Kupony)                  │   │
│  │    - Kolektyw Agentów                                         │   │
│  │    - Komunikaty Systemowe                                     │   │
│  │   (Sprint 11.4)                                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  UNIFIED INPUT LAYER (Sprint 11.5)                         │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  KnowledgeCollectorManager                                   │   │
│  │    - Zarzadza wszystkimi kolektorami                          │   │
│  │    - Agreguje dane w jeden pakiet                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  SSIKnowledgePackage                                          │   │
│  │    - V2: Modele, Predykcje, Walidacje, Interpretacje Świata   │   │
│  │    - V3: Pamięć, Wzorce, Relacje, Wiedza                       │   │
│  │    - V4: Agenci, Osobowości, Strategie, Decyzje              │   │
│  │    - External: Programista, Laboratoria, Kolektyw, System     │   │
│  │    - Metadata: Timestamps, Version, Source-Type                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  KNOWLEDGE PROCESSING PIPELINE                         │
│                                                                       │
│  ┌───────────────────┐    ┌───────────────────┐    ┌─────────────────┐   │
│  │ Knowledge         │    │ Knowledge         │    │ Prompt          │   │
│  │ Classifier        │    │ Builder          │    │ Builder         │   │
│  │ (Sprint 11.6)     │    │ (Sprint 11.7)    │    │ (Sprint 11.7)   │   │
│  │                   │    │                   │    │                 │   │
│  │ - Skad pochodzi   │    │ - Budowa kontekstu│    │ - Budowa promptu│   │
│  │   dana?           │    │   dla modelu     │    │   dla Qwen/Ollama│   │
│  │ - Do jakiego     │    │ - Selekcja       │    │                 │   │
│  │   modułu należy?  │    │   istotnych danych│    │                 │   │
│  │ - Czy do modelu?  │    │                   │    │                 │   │
│  │ - Czy do logu?    │    │                   │    │                 │   │
│  │ - Czy wymaga      │    │                   │    │                 │   │
│  │   działania?     │    │                   │    │                 │   │
│  └───────────────────┘    └───────────────────┘    └─────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI GATEWAY (Sprint 11.8)                            │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  AIModelGateway                                              │   │
│  │    - Komunikacja z Ollama                                     │   │
│  │    - Wybór modelu (Qwen2.5:7B, przyszłe modele)                │   │
│  │    - Zarządzanie kolejką zadań                               │   │
│  │    - Monitorowanie wydajności                                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                     │                                    │
│                                     ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     QWEN2.5:7B / OLLAMA                        │   │
│  │                  (Lokalne Modele Językowe)                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 KORZYŚCI NOWEJ ARCHITEKTURY

### ✅ Zalety:
1. **Brak duplikacji kodu** - Wspólny interfejs `BaseCollector`
2. **Łatwe dodawanie nowych źródeł** - Nowy kolektor = nowa klasa dziedzicząca
3. **Oddzielenie zbierania od przetwarzania** - Ziarnista architektura
4. **Skalowalność** - Nowe komputery/Modele AI nie wymagają przebudowy kolektorów
5. **Utrzymywalność** - Jeden pakiet wiedzy `SSIKnowledgePackage` dla wszystkich źródeł
6. **Testowalność** - Każdy kolektor może być testowany osobno

### 🎯 Główne Cechy:
- **Uniwersalny pakiet wiedzy** - `SSIKnowledgePackage` agreguje wszystkie dane
- **Wspólny interfejs** - `BaseCollector` dla wszystkich kolektorów
- **Modularne przetwarzanie** - Klassyfikator, Builder, Gateway jako osobne warstwy
- **Odporność na zmiany** - Nowe źródła/Modele nie łamią istniejącej architektury

---

## 📊 NOWY PODZIAŁ SPRINTU 11

```
Sprint 11: Uniwersalna Magistrala Danych SSI V5
├── Sprint 11.1: V2 Data Collector (✅ ZAKOŃCZONY)
│   ├── BaseCollector (Interfejs Wspólny) ← NOWOŚĆ
│   ├── V2DataCollector
│   ├── data_models.py
│   └── test_v2_collector.py (28 testów)
│
├── Sprint 11.2: V3 Knowledge Collector
│   ├── V3DataCollector (dziedziczy z BaseCollector)
│   ├── V3-specific data models
│   └── test_v3_collector.py
│
├── Sprint 11.3: V4 Agent Collector
│   ├── V4DataCollector (dziedziczy z BaseCollector)
│   ├── V4-specific data models
│   └── test_v4_collector.py
│
├── Sprint 11.4: External Knowledge Collector
│   ├── ExternalKnowledgeCollector (dziedziczy z BaseCollector)
│   ├── Source types: DEVELOPER, LABORATORIES, COLLECTIVE, SYSTEM
│   └── test_external_collector.py
│
├── Sprint 11.5: Unified Input Layer
│   ├── KnowledgeCollectorManager (agreguje wszystkie kolektory)
│   ├── SSIKnowledgePackage (uniwersalny pakiet wiedzy)
│   ├── KnowledgeCollectorRegistry (rejestr kolektorów)
│   └── test_unified_input.py
│
├── Sprint 11.6: Knowledge Classifier
│   ├── KnowledgeClassifier (klasyfikuje dane)
│   ├── ClassificationRules (zasady klasyfikacji)
│   └── test_classifier.py
│
├── Sprint 11.7: Context & Prompt Builder
│   ├── KnowledgeContextBuilder (buduje kontekst)
│   ├── PromptBuilder (buduje prompty dla modelu)
│   └── test_prompt_builder.py
│
└── Sprint 11.8: AI Gateway
    ├── AIModelGateway (komunikacja z Ollama)
    ├── ModelRouter (wybór modelu)
    ├── TaskQueue (kolejka zadań)
    └── test_ai_gateway.py
```

---

## 📝 SZCZEGÓŁOWY OPIS NOWYCH SPRINTÓW

---

### 🔢 **Sprint 11.2: V3 Knowledge Collector**

**Cel:** Pobieranie wiedzy z V3 World Memory System i pakowanie jej w uniwersalnym formacie.

#### **Zakres:**
| Lp | Obszar | Opis |
|----|--------|------|
| 1 | BaseCollector | Użycie wspólnego interfejsu |
| 2 | V3DataCollector | Specyficzny kolektor dla V3 |
| 3 | V3 Data Models | Modele dla pamięci, światów, wzorców |
| 4 | Integration | Połączenie z V3Integration |
| 5 | Tests | Testy jednostkowe (co najmniej 20 testów) |
| 6 | Smoke Test | Integracja z całym systemem |

#### **Architektura:**
```
V3 World Memory System
   │
   ▼
V3DataCollector (extends BaseCollector)
   │
   ▼
SSIKnowledgePackage (V3 section)
```

#### **Pliki do utworzenia:**
```
SSI/v5/input_layer/
├── __init__.py (zaktualizowany)
├── base_collector.py (NOWY - interfejs wspólny)
├── v3_collector.py (NOWY)
└── v3_models.py (NOWY - modele specyficzne dla V3)

SSI/tests/v5/
└── test_v3_collector.py (NOWY)
```

#### **Kryteria Akceptacji:**
- [ ] `V3DataCollector` dziedziczy z `BaseCollector`
- [ ] Wszystkie dane V3 są zebrane i spakowane
- [ ] Testy jednostkowe przechodzą (min. 20 testów)
- [ ] Integracja z `V3Integration` działa
- [ ] Dokumentacja zaktualizowana

---

### 🔢 **Sprint 11.3: V4 Agent Collector**

**Cel:** Zbieranie danych z V4 Agent Evolution (agenci, osobowości, strategie, decyzje).

#### **Zakres:**
| Lp | Obszar | Opis |
|----|--------|------|
| 1 | V4DataCollector | Specyficzny kolektor dla V4 |
| 2 | V4 Data Models | Modele dla agentów, obszności, strategii |
| 3 | Integration | Połączenie z V4 systemem agentów |
| 4 | Tests | Testy jednostkowe |
| 5 | Smoke Test | Integracja z całym systemem |

#### **Architektura:**
```
V4 Agent Evolution
   │
   ▼
V4DataCollector (extends BaseCollector)
   │
   ▼
SSIKnowledgePackage (V4 section)
```

#### **Pliki do utworzenia:**
```
SSI/v5/input_layer/
├── v4_collector.py (NOWY)
└── v4_models.py (NOWY)

SSI/tests/v5/
└── test_v4_collector.py (NOWY)
```

---

### 🔢 **Sprint 11.4: External Knowledge Collector**

**Cel:** Zbieranie danych z zewnętrznych źródeł (programista, laboratoria, kolektyw, system).

#### **Źródła danych:**
| Źródło | Typ | Opis |
|--------|-----|------|
| Panel Programisty | DEVELOPER | Polecenia, analiza systemu, historia zmian |
| Laboratorium Świata | LABORATORY | Badania, eksperymenty, wyniki |
| Laboratorium Typów | LABORATORY | Typy, kategorie, klasyfikacje |
| Laboratorium Grup | LABORATORY | Grupy, kupony, strategie grupowe |
| Laboratorium Kuponów | LABORATORY | Kupony, kombinacje, analiza ryzyka |
| Kolektyw Agentów | COLLECTIVE | Rozmowy, decyzje, konflikty, sojusze |
| Komunikaty Systemowe | SYSTEM | Logi, status, zdarzenia systemowe |

#### **Architektura:**
```
┌─────────────────────────┐
│  External Sources        │
│  - Developer Panel       │
│  - Laboratories (4 types)│
│  - Collective            │
│  - System Messages       │
└─────────────┬───────────┘
              │
              ▼
ExternalKnowledgeCollector (extends BaseCollector)
              │
              ▼
SSIKnowledgePackage (External section)
```

#### **Pliki do utworzenia:**
```
SSI/v5/input_layer/
├── external_collector.py (NOWY)
├── external_models.py (NOWY)
├── sources/ (NOWY KATALOG)
│   ├── developer_source.py
│   ├── laboratory_source.py
│   ├── collective_source.py
│   └── system_source.py
└── source_types.py (NOWY - enumy typów źródeł)

SSI/tests/v5/
└── test_external_collector.py (NOWY)
```

**Uwaga:** To będzie **jeden z ważniejszych sprintów**, ponieważ łączy wszystkie zewnętrzne źródła wiedzy.

---

### 🔢 **Sprint 11.5: Unified Input Layer**

**Cel:** Połączenie wszystkich kolektorów w **jednolitą warstwę wejścia**.

#### **Architektura docelowa:**
```
┌─────────────────────────────────────────────────────────────────┐
│  KnowledgeCollectorManager                                      │
│    - register_collector(collector: BaseCollector)               │
│    - unregister_collector(source_type: SourceType)              │
│    - get_collector(source_type: SourceType) -> BaseCollector     │
│    - collect_all() -> SSIKnowledgePackage                        │
│    - collect_specific(source_types: List[SourceType])           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  KnowledgeCollectorRegistry                                    │
│    - _collectors: Dict[SourceType, BaseCollector]              │
│    - auto_discover() -> List[BaseCollector]                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  SSIKnowledgePackage (Uniwersalny Pakiet Wiedzy)                │
│    - timestamp: datetime                                         │
│    - source_packages: Dict[SourceType, Any]                    │
│    │   - V2: V2DataPackage                                       │
│    │   - V3: V3DataPackage                                       │
│    │   - V4: V4DataPackage                                       │
│    │   - EXTERNAL: ExternalKnowledgePackage                      │
│    - metadata: KnowledgeMetadata                                │
│    - validation_info: ValidationResult                           │
└─────────────────────────────────────────────────────────────────┘
```

#### **Pliki do utworzenia:**
```
SSI/v5/input_layer/
├── collector_manager.py (NOWY)
├── collector_registry.py (NOWY)
├── knowledge_package.py (NOWY - uniwersalny pakiet)
└── knowledge_metadata.py (NOWY)

SSI/tests/v5/
└── test_unified_input.py (NOWY)
```

#### **Kryteria Akceptacji:**
- [ ] `KnowledgeCollectorManager` zarządza wszystkimi kolektorami
- [ ] `SSIKnowledgePackage` agreguje dane ze wszystkich źródeł
- [ ] System potrafi zebrać dane z dowolnej kombinacji źródeł
- [ ] Testy integracyjne przechodzą

---

### 🔢 **Sprint 11.6: Knowledge Classifier**

**Cel:** Klasyfikacja wiedzy - odpowiedź na pytanie: **"Co zrobić z tą informacją?"**

#### **Zakres klasyfikacji:**
| Pytanie | Możliwe Odpowiedzi | Akcja |
|---------|-------------------|-------|
| Skąd pochodzi dana? | V2, V3, V4, External, System | Określ źródło |
| Do jakiego modułu należy? | Memory, LLM, Laboratory, Agent, Decision | Kieruj do modułu |
| Czy ma trafić do modelu? | Tak/Nie | Obsłuż odpowiednio |
| Czy wymaga odpowiedzi? | Tak/Nie | Wygeneruj/Ignoruj |
| Czy jest tylko logiem? | Tak/Nie | Zapisz/Pomiń |
| Czy wymaga działania? | Tak/Nie | Wykonaj/ collaborative |

#### **Architektura:**
```
SSIKnowledgePackage
     │
     ▼
┌─────────────────────────────────┐
│  KnowledgeClassifier              │
│  - classify_package(package)      │
│  - classify_item(item)            │
│  - determine_action(item)        │
└─────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────┐
│  ClassificationResult             │
│  - source_type: SourceType        │
│  - target_module: ModuleType      │
│  - requires_llm: bool             │
│  - requires_response: bool        │
│  - requires_action: bool          │
│  - priority: PriorityLevel         │
└─────────────────────────────────┘
```

#### **Pliki do utworzenia:**
```
SSI/v5/processing/
├── __init__.py
├── classifier.py (NOWY)
├── classification_rules.py (NOWY)
└── classification_types.py (NOWY - enumy)

SSI/tests/v5/
└── test_classifier.py (NOWY)
```

---

### 🔢 **Sprint 11.7: Context & Prompt Builder**

**Cel:** Budowanie kontekstu i promptów dla modelu językowego.

#### **Krok 1: Knowledge Context Builder**
- **Cel:** Wybór istotnych informacji z `SSIKnowledgePackage`
- **Funkcje:**
  - `select_relevant_data(package, query)` - wybranie istotnych danych
  - `build_context(query, selected_data)` - budowa kontekstu
  - `compress_context(context, max_tokens)` - kompresja kontekstu

#### **Krok 2: Prompt Builder**
- **Cel:** Konwersja kontekstu na prompt dla modelu
- **Funkcje:**
  - `build_system_prompt()` - prompt systemowy
  - `build_user_prompt(query, context)` - prompt użytkownika
  - `build_full_prompt(system, user, context)` - pełny prompt

#### **Architektura:**
```
SSIKnowledgePackage
     │
     ▼
KnowledgeContextBuilder
     │
     ▼
Context (wybrana wiedza)
     │
     ▼
PromptBuilder
     │
     ▼
FullPrompt (dla Qwen/Ollama)
```

#### **Pliki do utworzenia:**
```
SSI/v5/processing/
├── context_builder.py (NOWY)
└── prompt_builder.py (NOWY)

SSI/tests/v5/
├── test_context_builder.py (NOWY)
└── test_prompt_builder.py (NOWY)
```

---

### 🔢 **Sprint 11.8: AI Gateway**

**Cel:** Komunikacja z modelami AI (Ollama, Qwen, przyszłe modele).

#### **Architektura:**
```
FullPrompt
     │
     ▼
┌─────────────────────────────────────────────┐
│  AIModelGateway                                │
│    - send_to_model(prompt, model_name)         │
│    - select_model(task_type) -> ModelConfig   │
│    - manage_task_queue()                       │
└─────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────┐
│  ModelRouter                                   │
│    - _models: Dict[str, ModelConfig]            │
│    - route_task(task, criteria) -> ModelName  │
│    - register_model(model_config)              │
└─────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────┐
│  TaskQueue                                     │
│    - _queue: List[ModelTask]                    │
│    - add_task(task: ModelTask)                 │
│    - get_next_task() -> ModelTask               │
│    - process_queue()                           │
└─────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────┐
│  OllamaIntegration                            │
│    - _client: OllamaClient                      │
│    - generate(prompt, model) -> str             │
│    - list_models() -> List[str]                 │
└─────────────────────────────────────────────┘
     │
     ▼
──────────► Qwen2.5:7B / i5 / i7 / Future Models
```

#### **Pliki do utworzenia:**
```
SSI/v5/ai_gateway/
├── __init__.py
├── model_gateway.py (NOWY)
├── model_router.py (NOWY)
├── task_queue.py (NOWY)
├── ollama_integration.py (NOWY)
└── model_config.py (NOWY)

SSI/tests/v5/
└── test_ai_gateway.py (NOWY)
```

---

## 📈 PODSUMOWANIE NOWEJ ARCHITEKTURY

### **Porównanie Starej vs Nowej:**

| Aspekt | Stara Architektura | Nowa Architektura |
|--------|-------------------|-------------------|
| **Kolektory** | Oddzielne klasy dla każdego źródła | Wspólny interfejs `BaseCollector` |
| **Dane** | Oddzielne pakiety dla V2, V3, V4 | **Jeden** `SSIKnowledgePackage` |
| **Rozbudowa** | Trudna, wymaga duplikacji | Łatwa, nowy kolektor = nowa klasa |
| **Skalowalność** | Ograniczona | Wysoka (nowe modele AI nie łamią kolektorów) |
| **Utrzymanie** | Trudne | Łatwe (wspólny kod) |
| **Testowanie** | Złożone | Proste (każdy kolektor osobno) |

### **Korzyści Długoterminowe:**

1. **Nowe źródła danych** - Dodanie nowego źródła to kwestia utworzenia jednej klasy
2. **Nowe modele AI** - Cambiano tylko `AI Gateway`, kolektory pozostają niezmienione
3. **Zmiany w V2/V3/V4** - Zmiany w źródłowych systemach nie łamią warstwy wejścia
4. **Wielojęzyczne modele** - Łatwe dodawanie nowych modeli (i5, i7, słabsze/większe Qweny)

---

## 🎯 NOWA MAPA PLIKÓW PO SPRINCIE 11

```
SSI/
└── v5/
    ├── __init__.py                    # Glowny modul V5
    │
    └── input_layer/                   # Warstwa Wejścia
        ├── __init__.py                # Modul input layer
        ├── base_collector.py         # Wspólny interfejs kolektorów
        ├── v2_collector.py           # Kolektor V2 (Sprint 11.1)
        ├── v2_models.py               # Modele danych V2
        ├── v3_collector.py           # Kolektor V3 (Sprint 11.2)
        ├── v3_models.py               # Modele danych V3
        ├── v4_collector.py           # Kolektor V4 (Sprint 11.3)
        ├── v4_models.py               # Modele danych V4
        ├── external_collector.py     # Kolektor External (Sprint 11.4)
        ├── external_models.py         # Modele danych External
        ├── sources/                   # Zrodla External
        │   ├── developer_source.py
        │   ├── laboratory_source.py
        │   ├── collective_source.py
        │   └── system_source.py
        ├── collector_manager.py       # Manager kolektorów (Sprint 11.5)
        ├── collector_registry.py      # Rejestr kolektorów
        ├── knowledge_package.py       # Uniwersalny pakiet wiedzy
        └── knowledge_metadata.py      # Metadane wiedzy
    │
    └── processing/                   # Przetwarzanie Wiedzy
        ├── __init__.py
        ├── classifier.py             # Klasyfikator (Sprint 11.6)
        ├── classification_rules.py
        ├── classification_types.py
        ├── context_builder.py        # Builder kontekstu (Sprint 11.7)
        └── prompt_builder.py         # Builder promptow
    │
    └── ai_gateway/                   # Bramka AI
        ├── __init__.py
        ├── model_gateway.py          # Bramka modeli (Sprint 11.8)
        ├── model_router.py           # Router modeli
        ├── task_queue.py             # Kolejka zadań
        ├── ollama_integration.py    # Integracja z Ollama
        └── model_config.py           # Konfiguracja modeli

SSI/tests/
└── v5/
    ├── __init__.py
    ├── test_v2_collector.py         # Testy V2 (Sprint 11.1)
    ├── test_v3_collector.py         # Testy V3 (Sprint 11.2)
    ├── test_v4_collector.py         # Testy V4 (Sprint 11.3)
    ├── test_external_collector.py  # Testy External (Sprint 11.4)
    ├── test_unified_input.py       # Testy Unified (Sprint 11.5)
    ├── test_classifier.py           # Testy Classifier (Sprint 11.6)
    ├── test_context_builder.py     # Testy Context (Sprint 11.7)
    ├── test_prompt_builder.py      # Testy Prompt (Sprint 11.7)
    ├── test_ai_gateway.py          # Testy AI Gateway (Sprint 11.8)
    └── test_input_layer_smoke.py   # Testy Smoke (Sprint 11.1)

SSI_DOCUMENTATION/
├── SSI_V5_ROADMAP.md              # Glowna mapa (do zaktualizowania)
├── SPRINT_11_IMPLEMENTATION.md    # Stary podzial (do archiwizacji)
└── SPRINT_11_REFACTORED.md        # NOWY - Ten dokument
```

---

## 🔄 KOLEJNE KROKI

### **Natychmiastowe:**
1. ✅ **Zatwierdzić nową architekturę** (ten dokument)
2. **Zarchiwizować** `SPRINT_11_IMPLEMENTATION.md` (stary podział)
3. **Zaktualizować** `SSI_V5_ROADMAP.md` z nowym podziałem
4. **Zaktualizować** `PROJECT_JOURNAL.md` z nowym planem

### **Implementacyjne:**
1. **Sprint 11.2** - Utworzyć `BaseCollector` + `V3DataCollector`
2. **Sprint 11.3** - `V4DataCollector`
3. **Sprint 11.4** - `ExternalKnowledgeCollector` (najważniejszy!)
4. **Sprint 11.5** - `SSIKnowledgePackage` + `KnowledgeCollectorManager`
5. **Sprint 11.6** - `KnowledgeClassifier`
6. **Sprint 11.7** - `ContextBuilder` + `PromptBuilder`
7. **Sprint 11.8** - `AIModelGateway` + `OllamaIntegration`

### **Długoterminowe:**
- **Sprint 12+** - Kontynuować z pamięcią wejściową, modelami językowymi itd.
- **Skalowanie** - Nowe komputery/Modele AI będą łatwe do dodania

---

## 📝 UWAGI ARCHITEKTONICZNE

### **Zasady Projektowe:**
1. **Każdy kolektor dziedziczy z `BaseCollector`**
2. **Każdy kolektor zwraca dane w formacie kompatybilnym z `SSIKnowledgePackage`**
3. **Każde źródło ma swój typ (`SourceType` enum)**
4. **Każdy pakiet wiedzy ma metadane (timestamp, version, source)**
5. **Klasyfikator nie modyfikuje danych, tylko je klasyfikuje**
6. **Prompt Builder nie zna modelu, tylko buduje prompty**

### **Wzorce Projektowe:**
- **Strategy Pattern** - Różne strategie kolekcji danych
- **Factory Pattern** - Tworzenie kolektorów
- **Singleton Pattern** - Manager kolektorów
- **Facade Pattern** - AI Gateway jako fasada dla modeli
- **Observer Pattern** - Subskrypcja na nowe dane

### **Zasady Nazewnictwa:**
- Kolektory: `{Source}DataCollector` (np. `V2DataCollector`)
- Pakiety: `{Source}DataPackage` (np. `V2DataPackage`)
- Modele danych: `{Entity}Data` (np. `ModelInfo`, `PredictionData`)
- Typy: `PascalCase` dla klas, `snake_case` dla funkcji/metod

---

## ✅ PODSUMOWANIE

**Nowa architektura rozwiązuje główne problemy:**
1. ❌ **Duplikacja kodu** → ✅ **Wspólny interfejs `BaseCollector`**
2. ❌ **Brak spójności** → ✅ **Jeden pakiet `SSIKnowledgePackage`**
3. ❌ **Trudna rozbudowa** → ✅ **Modularna architektura**
4. ❌ **Problemy ze skalowaniem** → ✅ **Oddzielenie warstw**

**Rezultat:** System SSI V5 będzie **łatwiejszy w utrzymaniu, bardziej skalowalny i gotowy na przyszłe rozszerzenia**.

---

**Dokument:** `SSI_DOCUMENTATION/SPRINT_11_REFACTORED.md`  
**Wersja:** 2.0  
**Data:** 2026-07-31  
**Autor:** MSDI AI / SSI System + Mistral Vibe  
**Status:** **OCZEKUJE NA ZATWIERDZENIE**

---

> **"Dobra architektura to nie ta, która działa. Dobra architektura to ta, która działa i jest łatwa do zmiany."**
>
> **"SSI V5 to system, który będzie ewoluował przez lata. Ta architektura zapewnia, że będzie to możliwe."**
