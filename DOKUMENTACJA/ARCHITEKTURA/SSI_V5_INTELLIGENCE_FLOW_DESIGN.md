# SSI V5 - PRZEPŁYW INTELIGENCJI

**Data:** 2026-08-01  
**Sprint:** 11.5 → 12+ (Faza Projektowania)  
**Status:** Dokumentacja projektowa - Wersja 1.0.0  
**Autor:** Główny Architekt SSI V5  

---

## 1. WSTĘP

### 1.1. Filozofia Systemu
- **Autonomia agentów:** Każdy agent podejmuje własne decyzje
- **Ewolucja:** Agenci uczą się na doświadczeniach
- **Współpraca:** Agenci wymieniają informacje i rozwiązują konflikty
- **Obserwowalność:** Każda decyzja jest śledzona i odtwarzalna

### 1.2. Model CTER
| **Składnik** | **Opis** | **Źródło** |
|--------------|----------|------------|
| **Context** | Stan świata, dane, historyczny kontekst | V2, V3, V4, External |
| **Tools** | Narzędzia analizy, selekcji, walidacji | AgentRuntime, CollectorManager |
| **Experience** | Historia, zachowania, strategie, błędy | Memory Store |
| **Reasoning** | Logika decyzyjna, ocena ryzyka, kalibracja | Decision Engine |

---

## 2. OGÓLNY PRZEPŁYW INTELIGENCJI

```
RUNTIME CONTROLLER
│
├─ 1. ZBIERANIE DANYCH (CollectorManager)
│   ├─ V2 World Data (warunki rynkowe, zdarzenia)
│   ├─ V3 Knowledge Data (wiedza domenowa, insighty)
│   ├─ V4 Agents Data (stan agentów, relacje)
│   └─ External Data (dane zewnętrzne, rynek)
│   └─ → UnifiedInputPackage
│
├─ 2. PRZETWARZANIE PRZEZ AGENTÓW (6× na cykl)
│   ├─ Agent_01: Dane → Analiza → Decyzja → Uczenie
│   ├─ Agent_02: Dane → Analiza → Decyzja → Uczenie
│   ├─ Agent_03: Dane → Analiza → Decyzja → Uczenie
│   ├─ Agent_04: Dane → Analiza → Decyzja → Uczenie
│   ├─ Agent_05: Dane → Analiza → Decyzja → Uczenie
│   └─ Agent_06: Dane → Analiza → Decyzja → Uczenie
│
├─ 3. KOLEKTYWNA INTELIGENCJIA (Sprint 12+)
│   ├─ Collective Memory (wspólna wiedza)
│   └─ Long Term Memory (archiwum systemowe)
│
└─ 4. WARSTWA LLM (Sprint 15+)
    └─ LLM Decision Layer (analiza decyzji)
```

### 2.1. Cykl Agenta (Podstawowy)

```
AGENT CYCLE:
├─ 1. LOAD MEMORY (personality, behavior, strategy, history)
├─ 2. FETCH DATA (V2, V3, V4, External)
├─ 3. SELECT DATA SOURCES (na podstawie trust_scores)
├─ 4. ANALYZE DATA (quality, trust, patterns, anomalies)
├─ 5. SELECT STRATEGY (na podstawie kontekstu)
├─ 6. MAKE DECISION (choice, confidence, reasoning)
├─ 7. SAVE EXPERIENCE (do pamięci)
└─ 8. UPDATE HISTORY (statystyki)
```

---

## 3. WYBÓR ŹRÓDEŁ DANYCH

### 3.1. Algorytm Selekcji

```python
# agent_runtime.py:_select_data_sources()

def _select_data_sources(self, collector_data, context):
    # Wagi: Trust (40%), Quality (40%), Relevance (20%)
    
    # 1. Pobierz wagi zaufania z personality.json
    trust_weights = {
        "v2": self.memory.personality.trust_v2,
        "v3": self.memory.personality.trust_v3,
        "v4": self.memory.personality.trust_v4,
        "external": self.memory.personality.trust_external
    }
    
    # 2. Oceń jakość danych (z metadanych)
    quality_scores = {src: data["metadata"]["data_quality"] 
                     for src, data in collector_data.items()}
    
    # 3. Oceń trafność do zadania
    relevance_scores = self._calculate_relevance(collector_data, context)
    
    # 4. Oblicz łączny wynik
    source_scores = {}
    for source in collector_data:
        source_scores[source] = (
            trust_weights[source] * 0.4 +
            quality_scores[source] * 0.4 +
            relevance_scores[source] * 0.2
        )
    
    # 5. Wybierz top 2-3 źródła
    sorted_sources = sorted(source_scores.items(), 
                          key=lambda x: x[1], reverse=True)
    selected = [s[0] for s in sorted_sources[:3]]
    
    return selected
```

### 3.2. Typowe Scenariusze

| **Scenariusz** | **Wybrane Źródła** | **Uzasadnienie** |
|----------------|-------------------|------------------|
| Wysokie ryzyko | V2, V3, V4 | Wymaga wielu potwierdzeń |
| Szybka analiza | V2, V3 | Najwyższa jakość i zaufanie |
| Analiza rynku | V2, External | World data + market data |
| Zachowania | V3, V4 | Knowledge + agents data |

---

## 4. KORZYSTANIE Z PAMIĘCI WŁASNEJ

### 4.1. Wykorzystanie Personality Memory

```python
# Wybór strategii na podstawie cech osobowości
risk_tolerance = self.memory.personality.risk_tolerance
analysis_depth = self.memory.personality.analysis_depth

if risk_tolerance > 0.7:
    strategy_pool = ["aggressive", "high_risk"]
elif risk_tolerance > 0.5:
    strategy_pool = ["balanced", "analytical"]
else:
    strategy_pool = ["conservative", "safe"]

if analysis_depth > 0.8:
    min_sources = 3  # Głęboka analiza
else:
    min_sources = 2  # Szybka analiza
```

### 4.2. Wykorzystanie Behavior Memory

```python
# Adaptacja pewności na podstawie historii
success_rate = self.memory.behavior.statistics.success_rate
if success_rate > 0.8:
    confidence_boost = +0.1
elif success_rate > 0.6:
    confidence_boost = 0.0
else:
    confidence_boost = -0.1

# Wybór najskuteczniejszej akcji
most_successful = max(
    self.memory.behavior.behaviors,
    key=lambda b: b.get("success_rate", 0)
)
```

### 4.3. Wykorzystanie Strategy Memory

**Algorytm wyboru strategii:**
1. Filtruj strategie pasujące do kontekstu
2. Rankuj po: `success_rate * 0.5 + context_match * 0.3 + exploration_bonus * 0.2`
3. Wybierz najlepszą (80%) lub eksploruj nową (20%)

---

## 5. KORZYSTANIE Z PAMIĘCI KOLEKTYWU (Sprint 12+)

### 5.1. Struktura Pamięci Kolektywu

```
SSI/memory/collective/
├── global_memory.json      # Agregowana wiedza z V2/V3/V4
├── strategy_memory.json    # Wspólne strategie zespołowe
├── knowledge_memory.json  # Zunifikowana baza wiedzy (z indeksami)
└── interaction_memory.json # Historia interakcji agentów
```

### 5.2. Wykorzystanie

```python
# Global Memory - dostęp do zbiorczej wiedzy
global_knowledge = CollectiveMemoryManager.get_global_memory()
analysis["global_patterns"] = global_knowledge["patterns"]
analysis["historical_trends"] = global_knowledge["trends"]

# Knowledge Memory - wyszukiwanie
results = CollectiveMemoryManager.search_knowledge({
    "keywords": analysis["patterns"],
    "min_confidence": 0.7,
    "max_results": 5
})

# Interaction Memory - sojusze i konflikty
interaction_data = CollectiveMemoryManager.get_interaction_memory()
allies = interaction_data["alliances"][self.agent_id]
conflicts = interaction_data["conflicts"][self.agent_id]
```

---

## 6. POWSTAWANIE STRATEGII

### 6.1. Źródła Strategii

| **Źródło** | **Sprint** | **Opis** | **Przykłady** |
|------------|------------|----------|---------------|
| agents_config.py | 11.5 | Domyślne typy strategii | analytical, conservative, creative |
| strategy.json | 11.5 | Indywidualne doświadczenie | success_rate, times_used |
| strategy_memory.json | 12+ | Strategie zespołowe | plany współpracy, wzorce |
| calibration_engine.py | 14+ | Dynamiczne generowanie | optymalizacja wag |
| llm_decision_layer.py | 15+ | LLM-generowane | kreatywne rozwiązania |

### 6.2. Życie Strategii

```
NOWA STRATEGIA
    │
    ▼
TESTOWANIE → AKTYWACJA → MONITOROWANIE → EWALUACJA
    │
    ├── Ewaluacja: success_rate > 0.65
    ├── Adaptacja: dostosowanie parametrów
    └── Archiwizacja: historia użycia
    │
    ▼
DEAKTYWACJA (jeśli success_rate < 0.40 lub nieużywana >90 dni)
```

### 6.3. Algorytm Wyboru Strategii

```python
def _select_strategy(self, analysis, context):
    # 1. Filtruj strategie pasujące do kontekstu
    context_compatible = [s for s in all_strategies 
                        if context["type"] in s.get("contexts", [])]
    
    # 2. Filtruj po profilu ryzyka
    risk_compatible = [s for s in context_compatible 
                     if self._check_risk_compatibility(s, context)]
    
    # 3. Rankuj strategie
    ranked = sorted(risk_compatible, key=lambda s: (
        s["success_rate"] * 0.4 +
        s["avg_confidence"] * 0.3 +
        (1/(s["times_used"]+1)) * 0.2 +  # Eksploracja
        context_match * 0.1
    ), reverse=True)
    
    # 4. Wybór: eksploatacja (80%) vs eksploracja (20%)
    exploration_rate = self.memory.personality.creativity * 0.2
    if random.random() < exploration_rate and len(ranked) > 1:
        return random.choice(ranked[1:3])  # Eksploracja
    else:
        return ranked[0]  # Eksploatacja
```

---

## 7. KONFLIKTY I SOJUSZE

### 7.1. Typy Konfliktów

| **Typ** | **Przykład** | **Wykrycie** | **Rozwiązywanie** |
|---------|--------------|--------------|------------------|
| Konflikt strategii | Agent_01: "invest", Agent_04: "save" | Rozbieżne decyzje | Negocjacje, głosowanie |
| Konflikt danych | V2 vs V3 dają sprzeczne dane | Różne trust + rozbieżne dane | Cross-validation |
| Konflikt zasobów | Dwa agenty chcą ten sam budżet | Conflicting requests | Prioritization, sharing |
| Konflikt priorytetów | Długotermin vs krótkotermin | Rozbieżne cele | Kompromis, podział zadań |

### 7.2. Typy Sojuszy

| **Typ** | **Przykład** | **Wykrycie** | **Wzmocnienie** |
|---------|--------------|--------------|-----------------|
| Sojusz informacyjny | Częste wymienianie danych | Wspólne źródła | +trust_score, +information_sharing |
| Sojusz strategiczny | Komplementarne strategie | Kompatybilne kompetencje | +collaboration_score, +synergy |
| Sojusz decyzyjny | Podobne decyzje | Podobne wzorce | +decision_consensus, +validation |
| Sojusz eksperymentalny | Wspólne testy | Wspólna eksploracja | +innovation_score |

### 7.3. Metryki Relacji

```json
{
  "trust_score": 0.85,           // Zaufanie między agentami (0.0-1.0)
  "collaboration_score": 0.90,   // Poziom współpracy (0.0-1.0)
  "conflict_score": 0.15,       // Poziom konfliktów (0.0-1.0)
  "information_shared": 45,      // Ilość wymienionych informacji
  "positive_interactions": 38,   // Pozytywne interakcje
  "negative_interactions": 2,    // Negatywne interakcje
  "strategy_synergy": 0.80,     // Synergia strategiczna (0.0-1.0)
  "decision_consensus": 0.75     // Zgoda decyzyjna (0.0-1.0)
}
```

---

## 8. ZATWIERDZANIE DECYZJI PRZEZ KOLEKTYW

### 8.1. Proces Zatwierdzania

```
DECYZJA AGENTA
    │
    ▼
1. WERYFIKACJA INFORMACJI
    ├── Spójność danych: V2↔V3↔V4
    ├── Jakość analizy
    └── Dopasowanie strategii
    │
    ▼
    verification_score = 0.92
    │
    ▼
2. KONSULTACJA Z INNYMI AGENTAMI
    ├── Agent_02: Agree (confidence: 0.90)
    ├── Agent_03: Disagree (confidence: 0.65)
    └── Agent_05: Agree with mods (confidence: 0.80)
    │
    ▼
    consensus_score = 0.85
    suggestions = [...]
    │
    ▼
3. ROZWIAZYWANIE KONFLIKTÓW (jeśli consensus < 0.70)
    ├── Negocjacje (dyskusja, kompromis)
    ├── Głosowanie (weighted voting)
    ├── Autorytet (najbardziej doświadczony)
    └── LLM (obiektywna analiza - Sprint 15+)
    │
    ▼
4. ZATWIERDZENIE LUB ODRIZUCENIE
    ├── Decyzja zatwierdzona: confidence ≥ 0.75
    ├── Decyzja odrzucona: confidence < 0.60
    └── Decyzja wymaga rewizji: 0.60 ≤ confidence < 0.75
    │
    ▼
5. WYKONANIE I ZAPIS
    └── Zapis decyzji do pamięci + uczenie
```

### 8.2. Matryca Zatwierdzania

| **Consensus Score** | **Verification Score** | **Akcja** | **Wymagania** |
|---------------------|------------------------|----------|---------------|
| ≥ 0.90 | ≥ 0.90 | **Auto-Approve** | Natychmiastowa akceptacja |
| ≥ 0.80 | ≥ 0.80 | **Approve** | Zatwierdź |
| ≥ 0.70 | ≥ 0.70 | **Approve with Review** | Zatwierdź z monitorowaniem |
| ≥ 0.70 | < 0.70 | **Conditional Approve** | Zatwierdźwarunkowo |
| < 0.70 | ≥ 0.80 | **Consultation Needed** | Wymagana konsultacja |
| < 0.70 | < 0.80 | **Reject** | Odrzuć |

### 8.3. Wpływ Sojuszy na Odecyzje

```python
# Wykorzystanie sojuszy w _make_decision()

# Pobranie sojuszników
allies = CollectiveMemoryManager.get_allies(self.agent_id)

# Średnia decyzja sojuszników
if allies:
    allies_decisions = [self.get_agent_decision(a, "latest") for a in allies]
    avg_allies_choice = self._calculate_average_choice(allies_decisions)
    avg_allies_confidence = sum(d["confidence"] for d in allies_decisions) / len(allies_decisions)
    
    # Wpływ sojuszników
    if avg_allies_confidence > 0.8:
        allies_influence = 0.25  # 25% wpływ
    else:
        allies_influence = 0.05  # 5% wpływ
    
    # Dostosowanie decyzji
    if allies_influence > 0.2:
        decision["choice"] = self._merge_choices(decision["choice"], avg_allies_choice)
```

---

## 9. WARSTWA MODELU JĘZYKOWEGO (Sprint 15+)

### 9.1. Integracja LLM z Decyzjami

```
AGENT DECISION
    │
    ▼
LLM ANALYSIS (Opcjonalna)
    │
    ├── Decision Quality Score (1-10)
    ├── Argument Strength (0.0-1.0)
    ├── Logical Consistency (0.0-1.0)
    ├── Alternative Perspectives [...]
    ├── Potential Errors [...]
    ├── Recommendations [...]
    └── Confidence Calibration (skorygowana pewność)
    │
    ▼
ENHANCED DECISION
    └── Decyzja wzbogacona o analizę LLM
```

### 9.2. Funkcje LLM Decision Layer

| **Funkcja** | **Wejście** | **Wyjście** | **Czas** |
|-------------|-------------|-------------|----------|
| analyze_decision | decision, context, memory | llm_analysis | ~3-5s |
| validate_reasoning | reasoning, data | consistency_score, errors | ~2-3s |
| generate_alternatives | context | alternative_choices | ~4-6s |
| calibrate_confidence | confidence, data_quality | calibrated_confidence | ~1-2s |

### 9.3. Wpływ LLM na Decyzje

```python
# agent_runtime.py z LLM

def _make_decision_with_llm(self, analysis, strategy):
    # 1. Standardowa decyzja agenta
    decision = self._make_standard_decision(analysis, strategy)
    
    # 2. Opcjonalna analiza LLM
    if FEATURE_FLAGS["ENABLE_LLM_ANALYSIS"]:
        llm_feedback = LLMDecisionLayer.analyze_decision(
            agent_id=self.agent_id,
            decision=decision,
            analysis=analysis,
            context=self._get_full_context()
        )
        
        # 3. Zastosuj feedback
        decision = self._apply_llm_feedback(decision, llm_feedback)
        
        # 4. Zapis insightów
        self._save_llm_insights(llm_feedback)
    
    return decision
```

---

## 10. UCZENIE PO WYKONANIU DECYZJI

### 10.1. Proces Uczenia

```
DECYZJA → WYKONANIE → WYNIK → UCZENIE
    │
    ▼
1. OCENA WYNIKU
    ├── Porównaj expected vs actual
    ├── Oblicz accuracy, precision, recall
    └── Określ outcome (success, failure, partial)
    │
    ▼
2. AKTUALIZACJA PAMIĘCI
    ├── BehaviorMemory: aktualizuj success_rate
    ├── StrategyMemory: aktualizuj times_used, times_successful
    └── HistoryMemory: dodaj nowy wpis z wynikiem
    │
    ▼
3. ADAPTACJA STRATEGII
    ├── Success: +waga strategii, która osiągnęła sukces
    ├── Failure: -waga strategii, która zawiodła
    └── Similarity: nauka od podobnych sytuacji
    │
    ▼
4. AKTUALIZACJA OSOBOWOŚCI (Długoterminowa)
    ├── Gradient descent: dostosuj wagi
    ├── Reinforcement learning: nagradzaj dobre decyzji
    └── Bayesian optimization: optymalizuj z niepewnością
```

### 10.2. Matryca Uczenia

| **Wynik** | **Akcja** | **Behavior Update** | **Strategy Update** | **Personality Update** |
|-----------|-----------|---------------------|----------------------|------------------------|
| Success | + | confidence ↑, success_rate ↑ | times_successful ↑, success_rate ↑ | risk_tolerance adjust |
| Failure | - | confidence ↓, failure_rate ↑ | times_failed ↑, success_rate ↓ | risk_tolerance adjust |
| Partial | ± | neutral | neutral | neutral |

### 10.3. Mechanizmy Adaptacji

**1. Success-Based Adaptation:**
- +10% waga cechy, która przyczyniła się do sukcesu
- +5% waga strategii, która osiągnęła sukces

**2. Failure-Based Adaptation:**
- -15% waga cechy, która spowodowała błąd
- -10% waga strategii, która zawiodła

**3. Trend-Based Adaptation:**
- Dostosowanie do wykrytych trendów rynkowych
- Reagowanie na zmiany w V2/V3/V4

**4. Similarity-Based Learning:**
- Nauka od podobnych sytuacji z przeszłości
- Transfer learning między domenami

---

**Data utworzenia:** 2026-08-01  
**Wersja:** 1.0.0  
**Status:** Gotowy do przeglądu