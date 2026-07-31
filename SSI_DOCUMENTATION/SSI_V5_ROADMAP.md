# SSI V5 - GLOWA MAPA SPRINTOW

## Self Learning Intelligence Ecosystem - Roadmapa Przejscia V4 do V5

**Wersja dokumentu:** 2.0  
**Data utworzenia:** 2026-07-31  
**Status:** AKTYWNY - Zaktualizowany z nowa architektura  
**Podstawa:** `PROJECT_RULES.md`, `PROJECT_JOURNAL.md`, Dyskusja Architekturalna  

---

## 📋 CEL DOKUMENTU

Dokument definuje **glowna mape sprintow** dla etapu przejscia **V4 do V5** systemu SSI.

**ZMIANA ARCHITEKTURY:** Od wersji 2.0 dokument uwzglednia **uniwersalna magistrale danych** z:
- Wspolnym interfejsem kolektorow (`BaseCollector`)
- Uniwersalnym pakietem wiedzy (`SSIKnowledgePackage`)
- Oddzielonymi warstwami: Kolektory -> Pakiet -> Klasyfikacja -> Kontekst -> Prompt -> AI Gateway

**Zalety nowej architektury:**
- Brak duplikacji kodu dla V2, V3, V4, Laboratoriow
- Latwe dodawanie nowych zrodeł danych
- Skalowalnosc - nowe modele AI nie wymagaja przebudowy kolektorow
- Utrzymywalnosc - wspolny kod i interfejsy

---

## 🎯 ETAP GLOWNY

**Integracja AI Core + przygotowanie samorozwoju systemu**

**Cel etapu:** Stworzenie **autonomicznego systemu V5**, ktory:
1. Rozumie caly stan SSI (V2, V3, V4) poprzez **uniwersalna magistrale danych**
2. Posiada pamiec wejsciowa i wiedze systemowa
3. Wykorzystuje lokalne modele jezykowe (Ollama, Qwen)
4. Klasyfikuje informacje i rutuje je do odpowiednich modulow
5. Zapewnia kontrole programisty i uzytkownika koncowego

---

## 🏗️ NOWA ARCHITEKTURA SSI V5

```
V2 Models, V3 Knowledge, V4 Agents, External Sources
     |
     v
BaseCollector (ABC) - Wspolny interfejs
     |
     +-- V2DataCollector (Sprint 11.1 - GOTOWY)
     +-- V3DataCollector (Sprint 11.2)
     +-- V4DataCollector (Sprint 11.3)
     +-- ExternalKnowledgeCollector (Sprint 11.4)
     |
     v
KnowledgeCollectorManager (Sprint 11.5)
     |
     v
SSIKnowledgePackage (Uniwersalny Pakiet Wiedzy)
     |
     v
KnowledgeClassifier (Sprint 11.6)
     |
     v
ContextBuilder -> PromptBuilder (Sprint 11.7)
     |
     v
AIModelGateway -> ModelRouter -> TaskQueue -> OllamaIntegration (Sprint 11.8)
     |
     v
Qwen2.5:7B / i5 / i7 / Future Models
```

---

## 📊 STRUKTURA SPRINTOW GLOWNYCH

**ETAP: Integracja AI Core + Samorozwoj Systemu**

```
Sprint 11:uniwersalna Magistrala Danych (8 pod-sprintow)
├── 11.1: V2 Data Collector + BaseCollector (ZAKONCZONY)
├── 11.2: V3 Knowledge Collector
├── 11.3: V4 Agent Collector  
├── 11.4: External Knowledge Collector
├── 11.5: Unified Input Layer
├── 11.6: Knowledge Classifier
├── 11.7: Context i Prompt Builder
└── 11.8: AI Gateway

Sprint 12: System Pamieci Wejsciowej i Wiedzy SSI
Sprint 13: Model Jezykowy SSI V5 Core
Sprint 14: Klasyfikacja Informacji i Routing (polaczony z 11.6)
Sprint 15: Panel Programisty SSI V5
Sprint 16: Panel Uzytkownika SSI  
Sprint 17: Zarzadzanie Wieloma Modelami AI (polaczony z 11.8)
Sprint 18: Integracja Laboratoriow AI
Sprint 19: Kolektyw Agentow i Komunikacja
Sprint 20: Bramka Gotowosci SSI V5
```

---

## 📁 DETALICZNY OPIS SPRINTU 11

### Sprint 11.1: V2 Data Collector (ZAKONCZONY)
- v2_collector.py (Kolektor V2)
- data_models.py (Modele danych V2)
- test_v2_collector.py (28 testow unit)
- test_input_layer_smoke.py (27 testow smoke)
- Status: IMPLEMENTED + TESTED + OPERATIONAL

### Sprint 11.2: Base Collector + V3 Knowledge Collector
- base_collector.py (Interfejs Wspolny)
- V3DataCollector (dziedziczy z BaseCollector)
- V3-specific data models
- Integration z V3Integration
- Testy jednostkowe (min. 20 testow)
- Status: PLANNED

### Sprint 11.3: V4 Agent Collector
- V4DataCollector (dziedziczy z BaseCollector)
- V4-specific data models
- Integration z V4
- Testy jednostkowe
- Status: PLANNED

### Sprint 11.4: External Knowledge Collector
- ExternalKnowledgeCollector (dziedziczy z BaseCollector)
- Zrodla: DEVELOPER, LABORATORIES, COLLECTIVE, SYSTEM
- Status: PLANNED (WAZNY!)

### Sprint 11.5: Unified Input Layer
- KnowledgeCollectorManager (agreguje wszystkie kolektory)
- SSIKnowledgePackage (uniwersalny pakiet wiedzy)
- KnowledgeCollectorRegistry (rejestr kolektorow)
- Status: PLANNED

### Sprint 11.6: Knowledge Classifier
- KnowledgeClassifier (klasyfikuje dane)
- ClassificationRules (zasady klasyfikacji)
- Status: PLANNED

### Sprint 11.7: Context and Prompt Builder
- KnowledgeContextBuilder (buduje kontekst)
- PromptBuilder (buduje prompty dla modelu)
- Status: PLANNED

### Sprint 11.8: AI Gateway
- AIModelGateway (komunikacja z Ollama)
- ModelRouter (wybor modelu)
- TaskQueue (kolejka zadan)
- OllamaIntegration (integracja z Ollama)
- Status: PLANNED

---

## SPRINT 12-20: POZOSTALE FUNKCJONALNOSCI

### Sprint 12: System Pamieci Wejsciowej i Wiedzy SSI

### Sprint 13: Model Jezykowy SSI V5 Core

### Sprint 14: Klasyfikacja Informacji i Routing
UWAGA: Polaczony z Sprintem 11.6

### Sprint 15: Panel Programisty SSI V5

### Sprint 16: Panel Uzytkownika SSI

### Sprint 17: Zarzadzanie Wieloma Modelami AI
UWAGA: Polaczony z Sprintem 11.8

### Sprint 18: Integracja Laboratoriow AI
UWAGA: Czesciowo zrealizowane w Sprint 11.4

### Sprint 19: Kolektyw Agentow i Komunikacja
UWAGA: Czesciowo zrealizowane w Sprint 11.4

### Sprint 20: Bramka Gotowosci SSI V5

---

## STALE PLIKI

Kazdy sprint aktualizuje:
- PROJECT_JOURNAL.md
- CHANGELOG.md
- STATUS.md
- SPRINT_STATUS.md

---

## NOWA MAPA PLIKOW

SSI/v5/
├── input_layer/
│   ├── base_collector.py (Sprint 11.2)
│   ├── v2_collector.py (Sprint 11.1 - GOTOWY)
│   ├── v3_collector.py (Sprint 11.2)
│   ├── v4_collector.py (Sprint 11.3)
│   ├── external_collector.py (Sprint 11.4)
│   ├── collector_manager.py (Sprint 11.5)
│   └── knowledge_package.py (Sprint 11.5)
│
├── processing/
│   ├── classifier.py (Sprint 11.6)
│   ├── context_builder.py (Sprint 11.7)
│   └── prompt_builder.py (Sprint 11.7)
│
└── ai_gateway/
    ├── model_gateway.py (Sprint 11.8)
    └── ollama_integration.py (Sprint 11.8)

---

## Kierunek Rozwoju po Input Layer (Sprint 11.1-11.8)

Po zakonczeniu Input Layer, SSI V5 bedzie rozwijany w kierunku:

1. **SSI V5 CORE** - warstwa sterujaca i zarzadzajaca
2. **AI Model Orchestrator** - zarzadzanie wieloma wyspecjalizowanymi modelami
3. **State Management** - pamiec ciagla i odpornosc na awarie
4. **Developer Gateway** - komunikacja z zewnetrznymi systemami
5. **Network Architecture** - sieciowa architektura z wieloma wezlami

Szczegolowy opis dostepny w: [SSI_V5_ARCHITECTURE_DIRECTION.md](./SSI_V5_ARCHITECTURE_DIRECTION.md)

---

## KOLEJNE KROKI

1. Zatwierdzic nowa architekture
2. Zaktualizowac PROJECT_JOURNAL.md
3. Zaimplementowac Sprint 11.2 (BaseCollector + V3DataCollector)
4. Zapoznac sie z dokumentem [SSI_V5_ARCHITECTURE_DIRECTION.md](./SSI_V5_ARCHITECTURE_DIRECTION.md) przed kolejnymi sprintami

---

## Referencje do Nowej Architektury

- [SSI_V5_ARCHITECTURE_DIRECTION.md](./SSI_V5_ARCHITECTURE_DIRECTION.md) - Glowny dokument z kierunkiem architektonicznym
- [SPRINT_11_REFACTORED.md](./SPRINT_11_REFACTORED.md) - Zaktualizowana wizja Sprintu 11

Dokument: SSI_DOCUMENTATION/SSI_V5_ROADMAP.md
Wersja: 2.1
Data: 2026-07-31
Status: AKTYWNY