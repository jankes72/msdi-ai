# SSI V5 PHASE 2: AGENT DECISION

**Sprint:** 12+ (Phase 2 Foundation)
**Data:** 2026-08-01
**Wersja:** 1.0.0
**Status:** Completed
**Autor:** Glowny Architekt SSI V5

---

## SPIS TRESCI

1. [Agent Decision Definition](#1-agent-decision-definition)
2. [Decision Pipeline](#2-decision-pipeline)
3. [Decision Engine Components](#3-decision-engine-components)
4. [Decision Package](#4-decision-package)
5. [Decision Validation](#5-decision-validation)
6. [Decision Memory](#6-decision-memory)
7. [Feedback Integration](#7-feedback-integration)
8. [Separation of Concerns](#8-separation-of-concerns)
9. [Performance Metrics](#9-performance-metrics)
10. [Podsumowanie](#10-podsumowanie)

---

## 1. AGENT DECISION DEFINITION

### 1.1 DESCRIPTION
Agent Decision jest finalna warstwa Agent System odpowiedzialna za agregacje konsensusu, walidacje decyzji, ocene pewnosci i przygotowanie pakietu decyzyjnego dla Decision Layer.

Agent Decision **NIE tworzy wiedzy zrodlowej**. Korzysta wyłacznie z ConsensusSuggestion dostarczonej przez Agent Collaboration.

Agent Decision **NIE zastępuje Decision Layer**. Nie podejmuje koncowej decyzji biznesowej, tylko przygotowuje i waliduje pakiet decyzyjny.

Agent Decision **NIE modyfikuje Teacher Engine**. Nie ingeruje w proces generowania wiedzy, World Memory ani Feature Knowledge.

### 1.2 ROLE
Agent Decision pelni role **finalnego filtra i formatatora** w Agent System. Glownym zadaniem jest transformacja ConsensusSuggestion w strukturowany Decision Package gotowy do przeksztalcenia w finalna decyzje przez Decision Layer.

### 1.3 RESPONSIBILITIES
- Odbior i walidacja ConsensusSuggestion od Agent Collaboration
- Agregacja ConsensusSuggestion z indywidualnymi AgentSuggestionPackage (opcjonalnie)
- Walidacja spójnosci, pewnosci i jakości konsensusu
- Ocena ryzyka i alternatyw
- Formatowanie Decision Package wedlug standardu Decision Layer
- Przekazanie Decision Package do Decision Layer
- Zapis historia decyzji i metryk jakości

### 1.4 LIMITATIONS
- Zaleznosc od jakości ConsensusSuggestion
- Brak analizy danych zrodlowych
- Brak modyfikacji World Memory
- Brak podejmowania koncowej decyzji biznesowej
- Ograniczenia czasowe: < 80ms na przygotowanie Decision Package
- Ograniczenia rozmiaru: Decision Package <= 16KB

### 1.5 DEPENDENCIES
- Agent Collaboration - Dostarcza ConsensusSuggestion
- Agent Core - Zarzadza agentami i koordynuje prace
- Agent Reasoning Engine - Dostarcza indywidualne AgentSuggestionPackage (opcjonalnie)
- Decision Layer - Odbiera Decision Package
- Feedback Layer - Dostarcza feedback do aktualizacji
- World Memory - Dostarcza kontekst historyczny (tylko odczyt)

---

## 2. DECISION PIPELINE

### 2.1 Pipeline Flow

```
INPUT: ConsensusSuggestion (od Agent Collaboration)
   ↓
[1] INPUT VALIDATION (5-8ms)
   ↓
[2] DECISION AGGREGATION (10-15ms)
   ↓
[3] DECISION VALIDATION (15-20ms)
   ↓
[4] CONFIDENCE EVALUATION (5-8ms)
   ↓
[5] RISK ANALYSIS (10-12ms)
   ↓
[6] FORMATTING & PACKAGING (5-8ms)
   ↓
OUTPUT: Decision Package (do Decision Layer)

**Total time: < 80ms**
```

### 2.2 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT DECISION PIPELINE                     │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│  │ INPUT    │→   │ DECISION │→   │ DECISION │               │
│  │ VALIDATION│   │ AGGREGATOR│   │ VALIDATOR│               │
│  └──────────┘    └──────────┘    └──────┬───┘               │
│                                              │                   │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│  │CONFIDENCE│→   │ RISK     │→   │ FORMAT-  │               │
│  │EVALUATOR │   │ ANALYZER │   │ TING    │               │
│  └──────────┘    └──────────┘    └──────────┘               │
└─────────────────────────────────────────────────────────────┘
                 ↓
          Decision Package
```

---

## 3. DECISION ENGINE COMPONENTS

### 3.1 Decision Aggregator

**DESCRIPTION:** Komponent agregujacy ConsensusSuggestion z opcjonalnymi indywidualnymi sugestiami agentow w spójny zestaw danych decyzyjnych.

**RESPONSIBILITIES:**
- Odbior ConsensusSuggestion od Agent Collaboration
- Opcjonalne pobieranie indywidualnych AgentSuggestionPackage
- Laczenie sugestii konsensusu z sugestiami indywidualnymi
- Rozwiazywanie ewentualnych sprzecznosci
- Przygotowanie zunifikowanego zestawu danych

**INPUT:**
- ConsensusSuggestion (główne wejście)
- AgentSuggestionPackage[] (opcjonalne, od Agent Reasoning Engine)
- AgentRegistry (lista aktywnych agentow)

**PROCESS:**
1. Odbior i walidacja ConsensusSuggestion
2. Pobieranie indywidualnych sugestii (jeśli dostępne)
3. Porownanie ConsensusSuggestion z indywidualnymi sugestiami
4. Identyfikacja i rozstrzyganie sprzecznosci
5. Laczenie w agregowany strukture decyzyjna

**OUTPUT:** AggregatedDecisionData

**MEMORY USED:**
- consensus_cache/
- agent_suggestions/
- agent_registry/

**MEMORY UPDATED:**
- aggregation_log.json
- aggregation_metrics.json

**KNOWLEDGE USED:** Specjalizacje agentow, historyczne wzorce agregacji

**COMMUNICATION:**
- Od Agent Collaboration: Odbior ConsensusSuggestion
- Od Agent Reasoning Engine: Opcjonalny odbiór AgentSuggestionPackage
- Do Decision Validator: Przeslanie agregowanych danych

**ERROR HANDLING:**
- BLAD_KONSENSUSU → Uzycie ostatniego ConsensusSuggestion
- BLAD_AGREGACJI → Uzycie tylko ConsensusSuggestion
- BLAD_SPRZECZNOSCI → Esikalacja do Decision Validator
- BLAD_FORMATU → Korekta, retry

**PERFORMANCE:** Czas < 15ms, Dokladnosc agregacji > 99%, Redukcja sprzecznosci > 90%

**FUTURE EXTENSIONS:** Dynamiczna agregacja, inteligentne laczenie sugestii

---

### 3.2 Decision Validator

**DESCRIPTION:** Komponent weryfikujacy jakość, spójnosc i wiarygodnosc danych decyzyjnych przed ich sfinalizowaniem.

**RESPONSIBILITIES:**
- Sprawdzanie zgodnosci miedzy ConsensusSuggestion a indywidualnymi sugestiami
- Walidacja poziomu pewnosci
- Weryfikacja spójnosci dowodow
- Sprawdzanie kompatybilnosci z historycznymi wzorcami
- Okreslenie statusu walidacji

**INPUT:** AggregatedDecisionData

**PROCESS:**
1. Walidacja formatu i struktury
2. Sprawdzanie zgodnosci wynikow:
   - Czy ConsensusSuggestion jest spójny z wiekszoscia indywidualnych sugestii?
   - Czy rozbieznosci sa w dopuszczalnym zakresie?
3. Walidacja pewnosci:
   - Czy confidence > minimalny próg (0.5)?
   - Czy confidence jest spójny miedzy agentami?
4. Weryfikacja dowodow:
   - Czy dowody sa kompatybilne?
   - Czy evidence_quality > 0.7?
5. Okreslenie validation_status

**OUTPUT:** ValidatedDecisionData, ValidationReport

**MEMORY USED:**
- validation_rules/
- historical_patterns/
- confidence_thresholds/

**MEMORY UPDATED:**
- validation_log.json
- validation_metrics.json

**KNOWLEDGE USED:** Zasady walidacji, historyczne wzorce, progi pewnosci

**COMMUNICATION:**
- Od Decision Aggregator: Odbior agregowanych danych
- Do Confidence Evaluator: Przeslanie zwalidowanych danych
- Do Risk Analyzer: Przeslanie statusu walidacji

**ERROR HANDLING:**
- BLAD_WALIDACJI → Uzycie domyslnych reguł
- BLAD_SPRZECZNOSCI → Esikalacja do Risk Analyzer
- BLAD_PEWNOSCI → Kalibracja confidence
- BLAD_DOWODOW → Usuniecie slabych dowodow

**PERFORMANCE:** Czas < 20ms, Dokladnosc walidacji > 98%, Czulosc > 95%

**FUTURE EXTENSIONS:** Adaptacyjne progi, automatyczne uczenie reguł

---

### 3.3 Confidence Evaluator

**DESCRIPTION:** Komponent obliczajacy finalny poziom pewnosci decyzji na podstawie sugestii agentow, konsensusu i historycznej dokladnosci.

**RESPONSIBILITIES:**
- Obliczanie finalnej pewnosci (final_confidence)
- Kalibracja pewnosci wedlug historycznej dokladnosci
- Ocena stabilnosci pewnosci
- Generowanie confidence_breakdown

**INPUT:** ValidatedDecisionData

**PROCESS:**
1. Zbieranie czynnikow pewnosci:
   - consensus_confidence (z ConsensusSuggestion)
   - average_agent_confidence (srednia z AgentSuggestionPackage)
   - agreement_rate (z ConsensusSuggestion)
   - evidence_quality (z dowodow)
   - historical_accuracy (dokladnosc historyczna dla podobnych wzorców)
2. Obliczanie final_confidence:
   final_confidence = (consensus_confidence * 0.40) + (average_agent_confidence * 0.25) + (agreement_rate * 0.15) + (evidence_quality * 0.10) + (historical_accuracy * 0.10)
3. Kalibracja wedlug historycznej dokladnosci
4. Generowanie confidence_breakdown

**OUTPUT:** ConfidenceScore, ConfidenceBreakdown, ConfidenceClassification

**MEMORY USED:**
- confidence_history/
- accuracy_metrics/
- calibration_data/

**MEMORY UPDATED:**
- confidence_scores.json
- calibration_log.json

**KNOWLEDGE USED:** Historyczna dokladnosc, wzorce pewnosci, kalibracja

**COMMUNICATION:**
- Od Decision Validator: Odbior zwalidowanych danych
- Do Risk Analyzer: Przeslanie confidence_score
- Do Decision Formatter: Przeslanie confidence_breakdown

**ERROR HANDLING:**
- BLAD_OBLICZENIA → Uzycie domyslnych wag
- BLAD_KALIBRACJI → Uzycie ostatnich parametrow
- BLAD_HISTORII → Uzycie ogolnych statystyk

**PERFORMANCE:** Czas < 8ms, Dokladnosc kalibracji > 95%, Stabilnosc > 98%

**FUTURE EXTENSIONS:** Dynamiczne wagi, adaptacyjna kalibracja

---

### 3.4 Risk Analyzer

**DESCRIPTION:** Komponent analizujacy i oceniajacy ryzyko zwiazane z decyzja na podstawie sugestii agentow, konsensusu i historycznych wzorców.

**RESPONSIBILITIES:**
- Ocena poziomu ryzyka (risk_level)
- Identyfikacja czynnikow ryzyka
- Analiza strategii mitigacji
- Generowanie risk_assessment

**INPUT:** ValidatedDecisionData, ConfidenceScore

**PROCESS:**
1. Zbieranie czynnikow ryzyka:
   - conflict_severity (z ConsensusSuggestion)
   - confidence_variance (odchylenie standardowe confidence)
   - evidence_conflict (sprzeczne dowody)
   - historical_risk (ryzyko historyczne dla wzorca)
   - external_factors (czynniki zewnetrzne)
2. Obliczanie risk_score:
   risk_score = (conflict_severity * 0.30) + (confidence_variance * 0.20) + (evidence_conflict * 0.20) + (historical_risk * 0.15) + (external_factors * 0.15)
3. Okreslenie risk_level:
   - VERY_LOW (0.0-0.15)
   - LOW (0.15-0.30)
   - MEDIUM (0.30-0.50)
   - HIGH (0.50-0.70)
   - VERY_HIGH (0.70-1.0)
4. Generowanie czynnikow ryzyka i strategii mitigacji

**OUTPUT:** RiskAssessment, RiskLevel, RiskFactors, MitigationStrategies

**MEMORY USED:**
- risk_patterns/
- historical_risk/
- external_factors/

**MEMORY UPDATED:**
- risk_assessments.json
- risk_patterns.json

**KNOWLEDGE USED:** Historyczne wzorce ryzyka, czynniki zewnetrzne

**COMMUNICATION:**
- Od Decision Validator: Odbior statusu walidacji
- Od Confidence Evaluator: Odbior confidence_score
- Do Decision Formatter: Przeslanie RiskAssessment

**ERROR HANDLING:**
- BLAD_OBLICZENIA → Uzycie domyslnych wartosci
- BLAD_CZYNNIKOW → Pomijanie nieznanych czynnikow
- BLAD_HISTORII → Uzycie ogolnych statystyk

**PERFORMANCE:** Czas < 12ms, Dokladnosc oceny > 90%, Pokrycie czynnikow > 95%

**FUTURE EXTENSIONS:** Dynamiczne wagi, nowe czynniki ryzyka

---

### 3.5 Decision Formatter

**DESCRIPTION:** Komponent formatujacy finalny Decision Package wedlug standardu wymaganego przez Decision Layer.

**RESPONSIBILITIES:**
- Formatowanie Decision Package
- Walidacja formatu
- Kompresja danych (jeśli potrzebna)
- Dodawanie metadanych

**INPUT:** ValidatedDecisionData, ConfidenceScore, RiskAssessment

**PROCESS:**
1. Zbieranie wszystkich komponentow:
   - prediction (wynik)
   - confidence (pewnosc)
   - evidence (dowody)
   - supporting_agents (wsparcie agentow)
   - supporting_teachers (wsparcie Teacher Models)
   - risk_level (poziom ryzyka)
   - alternatives (alternatywy)
   - reasoning_summary (podsumowanie)
   - validation_status (status walidacji)
2. Formatowanie wedlug schemy Decision Package
3. Walidacja formatu
4. Kompresja (jeśli rozmiar > 12KB)
5. Dodawanie metadanych (decision_id, timestamp, version)

**OUTPUT:** Decision Package

**MEMORY USED:** decision_schemas/, formatting_rules/

**MEMORY UPDATED:** formatting_log.json

**KNOWLEDGE USED:** Schema Decision Package, reguły formatowania

**COMMUNICATION:**
- Od wszystkich komponentow: Odbior danych
- Do Decision Layer: Przeslanie Decision Package
- Do Decision History Manager: Przeslanie do archiwizacji

**ERROR HANDLING:**
- BLAD_FORMATU → Korekta, retry
- BLAD_ROZMIARU → Kompresja, usuwanie najmniej istotnych
- BLAD_SCHEMY → Uzycie domyslnej schemy

**PERFORMANCE:** Czas < 8ms, Rozmiar Decision Package <= 16KB, Dokladnosc formatowania 100%

**FUTURE EXTENSIONS:** Nowe formaty, dynamiczna kompresja

---

### 3.6 Decision History Manager

**DESCRIPTION:** Komponent zarzadzajacy historia decyzji, metrykami jakości i wzorcami decyzyjnymi.

**RESPONSIBILITIES:**
- Zapis Decision Package do historii
- Aktualizacja metryk jakości
- Identyfikacja wzorców decyzyjnych
- Archiwizacja starych danych

**INPUT:** Decision Package, ValidationReport, ConfidenceScore, RiskAssessment

**PROCESS:**
1. Zapis Decision Package do decision_history/
2. Aktualizacja metryk:
   - decision_quality (jakość decyzji)
   - decision_accuracy (dokladnosc)
   - decision_confidence (pewnosc)
3. Identyfikacja wzorców:
   - podobne decyzje
   - powtarzajace sie bledy
   - sukcesy i porazki
4. Archiwizacja (dane > 1 rok)

**OUTPUT:** HistoryRecord, QualityMetrics, DecisionPatterns

**MEMORY USED:**
- decision_history/
- quality_metrics/
- decision_patterns/

**MEMORY UPDATED:**
- decision_history/[decision_id].json
- quality_metrics.json
- decision_patterns.json

**KNOWLEDGE USED:** Historyczne decyzje, wzorce, metryki

**COMMUNICATION:**
- Od Decision Formatter: Odbior Decision Package
- Do Feedback Integration: Dostarczenie danych do feedbacku

**ERROR HANDLING:**
- BLAD_ZAPISU → Retry, cache
- BLAD_ARCHIWIZACJI → Zapis do tymczasowego katalogu
- BLAD_METRYK → Uzycie ostatnich wartosci

**PERFORMANCE:** Czas < 10ms, Rozmiar historii: max 10GB, Dokladnosc metryk > 99%

**FUTURE EXTENSIONS:** Automatyczna archiwizacja, inteligentne wzorce

---

## 4. DECISION PACKAGE

### 4.1 Format Definition

Decision Package jest finalna struktura danych przekazywana do Decision Layer. Zawiera wszystkie informacje nezbedne do podjecia koncowej decyzji biznesowej.

**Format:**
```json
{
  "decision_id": "DECISION_20260801_001",
  "timestamp": "2026-08-01T12:00:00Z",
  "match_id": "MATCH_20260801_001",
  "version": "1.0",
  "prediction": {
    "result": "2:1",
    "result_type": "HOME_WIN",
    "confidence": 0.89,
    "strategy": "balanced_approach"
  },
  "evidence": {
    "consensus_evidence": [
      {
        "type": "FEATURE_CORRELATION",
        "name": "zmiana_kursow",
        "value": 0.831,
        "weight": 0.35,
        "description": "Silna korelacja ze zwyciestwem gospodarzy",
        "supporting_agents": ["AGENT_01", "AGENT_02"],
        "supporting_teachers": ["siec_01_zmiana_kursow", "siec_02_tempo"]
      },
      {
        "type": "HISTORICAL_PATTERN",
        "name": "home_advantage_01",
        "value": 0.78,
        "weight": 0.25,
        "description": "Historycznie 78% wygranych u siebie",
        "supporting_agents": ["AGENT_02", "AGENT_06"]
      }
    ],
    "conflicting_evidence": [],
    "evidence_quality": 0.87
  },
  "supporting_agents": [
    {
      "agent_id": "AGENT_01",
      "agent_type": "strategic_analysis",
      "suggestion_result": "2:1",
      "suggestion_confidence": 0.92,
      "weight": 1.35,
      "agreement": true
    },
    {
      "agent_id": "AGENT_02",
      "agent_type": "historical_analysis",
      "suggestion_result": "2:1",
      "suggestion_confidence": 0.85,
      "weight": 1.12,
      "agreement": true
    },
    {
      "agent_id": "AGENT_03",
      "agent_type": "statistical_analysis",
      "suggestion_result": "1:1",
      "suggestion_confidence": 0.78,
      "weight": 0.95,
      "agreement": false
    }
  ],
  "supporting_teachers": [
    {
      "teacher_id": "siec_01_zmiana_kursow",
      "prediction": "2:1",
      "confidence": 0.85,
      "weight": 0.12
    },
    {
      "teacher_id": "siec_02_tempo",
      "prediction": "2:1",
      "confidence": 0.72,
      "weight": 0.08
    }
  ],
  "risk_level": "LOW",
  "risk_assessment": {
    "risk_score": 0.21,
    "risk_factors": ["minor_result_disagreement"],
    "mitigation_strategies": ["verify_with_history", "check_external_factors"],
    "confidence_in_assessment": 0.94
  },
  "alternatives": [
    {
      "result": "1:1",
      "result_type": "DRAW",
      "confidence": 0.65,
      "risk_level": "LOW",
      "supporting_agents": ["AGENT_03", "AGENT_06"],
      "reasoning": "Konserwatywna opcja przy niepewnych danych"
    },
    {
      "result": "3:1",
      "result_type": "HOME_WIN",
      "confidence": 0.45,
      "risk_level": "VERY_HIGH",
      "supporting_agents": ["AGENT_01"],
      "reasoning": "Agresywna opcja przy silnej korelacji cech"
    }
  ],
  "reasoning_summary": {
    "consensus_type": "STRONG_CONSENSUS",
    "agreement_rate": 0.83,
    "consensus_decision": "2:1",
    "individual_suggestions": {
      "2:1": 4,
      "1:1": 1,
      "3:1": 1
    },
    "confidence_breakdown": {
      "consensus_confidence": 0.89,
      "average_agent_confidence": 0.84,
      "agreement_rate_contribution": 0.15,
      "evidence_quality_contribution": 0.087,
      "historical_accuracy_contribution": 0.089
    },
    "conflict_resolution": "Weighted Voting - 2:1 wygrało"
  },
  "validation_status": {
    "overall_status": "VALID",
    "consensus_valid": true,
    "confidence_valid": true,
    "evidence_valid": true,
    "warnings": [],
    "errors": []
  },
  "meta": {
    "total_agents": 6,
    "total_teachers": 15,
    "decision_time_ms": 67,
    "pipeline_version": "1.0.0"
  }
}
```

### 4.2 Field Descriptions

| Pole | Typ | Opis | Zakres | Waga |
|------|-----|------|--------|------|
| decision_id | String | Unikalny identyfikator decyzji | - | - |
| timestamp | ISO8601 | Data i godzina utworzenia | - | - |
| match_id | String | Identifikator meczu | MATCH_* | - |
| version | String | Wersja formatu Decision Package | X.Y.Z | - |
| prediction | Object | Glówna predykcja z pewnoscia i strategia | - | - |
| evidence | Object | Dowody z konsensusu i agentow | - | - |
| supporting_agents | Array | Lista agentow wsparcia z wagami | - | - |
| supporting_teachers | Array | Lista Teacher Models wsparcia | - | - |
| risk_level | Enum | Poziom ryzyka (VERY_LOW, LOW, MEDIUM, HIGH, VERY_HIGH) | - | - |
| risk_assessment | Object | Szczegolowa ocena ryzyka | 0.0-1.0 | - |
| alternatives | Array | Alternatywne wyniki z uwzglednieniem ryzyka | 0-5 | - |
| reasoning_summary | Object | Podsumowanie rozumowania i konsensusu | - | - |
| validation_status | Object | Status walidacji decyzji | - | - |
| meta | Object | Metadane techniczne | - | - |

---

## 5. DECISION VALIDATION

### 5.1 Validation Process

Agent Decision wykonuje walidacje na kilku poziomach:

1. **Sprawdzanie zgodnosci agentow:**
   - Czy ConsensusSuggestion jest spójny z wiekszoscia indywidualnych sugestii?
   - Czy rozbieznosci sa w dopuszczalnym zakresie (agreement_rate > 0.6)?
   - **AKCJA:** Jeśli agreement_rate < 0.6 → ostrzezenie, eskalacja do Decision Layer

2. **Sprawdzanie pewnosci:**
   - Czy final_confidence > minimalny próg (0.5)?
   - Czy confidence jest spójny miedzy agentami (confidence_alignment > 0.7)?
   - **AKCJA:** Jeśli final_confidence < 0.5 → ostrzezenie, sugestia alternatywy

3. **Sprawdzanie konfliktow:**
   - Czy sa nierozstrzygniete konflikty?
   - Czy conflict_severity > MEDIUM?
   - **AKCJA:** Jeśli conflict_severity > HIGH → eskalacja do Decision Layer

4. **Fallback:**
   - odrzucenie sugestii z confidence < 0.3
   - uzycieWeighted Voting jako fallback
   - eskalacja do Decision Layer (jezeli nie mozna rozstrzygnac)

### 5.2 Validation Status Classification

| Status | Opis | Akcja |
|--------|------|------|
| VALID | Wszystkie sprawdzenia pozytywne | Akceptacja Decision Package |
| VALID_WITH_WARNINGS | Niskie ostrzezenia | Akceptacja z ostrzezeniami |
| INVALID_MINOR | Niskie bledy | Akceptacja z poprawka |
| INVALID_MAJOR | Wazne bledy | Esikalacja do Decision Layer |
| CRITICAL | Krytyczne bledy | Odrzucenie, alert do Agent Core |

### 5.3 Validation Rules

**Zgodnosc konsensusu:**
- agreement_rate >= 0.6 → PASS
- agreement_rate < 0.6 → WARNING

**Pewnosc:**
- final_confidence >= 0.7 → PASS
- 0.5 <= final_confidence < 0.7 → WARNING
- final_confidence < 0.5 → FAIL

**Dowody:**
- evidence_quality >= 0.7 → PASS
- 0.5 <= evidence_quality < 0.7 → WARNING
- evidence_quality < 0.5 → FAIL

**Konflikty:**
- Żadne nierozstrzygniete → PASS
- Nierozstrzygniete LOW/MEDIUM → WARNING
- Nierozstrzygniete HIGH/VERY_HIGH → FAIL

---

## 6. DECISION MEMORY

### 6.1 Memory Structure

```
decision_memory/
├── decision_history/
│   ├── [decision_id].json
│   └── decision_log.json
├── decision_quality/
│   ├── quality_metrics.json
│   └── accuracy_history.json
├── decision_feedback/
│   ├── feedback_log.json
│   └── improvement_suggestions.json
└── decision_patterns/
    ├── success_patterns.json
    ├── failure_patterns.json
    └── decision_clusters.json
```

### 6.2 Memory Components

#### decision_history
**DESCRIPTION:** Historia wszystkich podjetych decyzji z pełnymi danymi.

**STRUCTURE:**
```json
{
  "decision_id": "DECISION_20260801_001",
  "match_id": "MATCH_20260801_001",
  "timestamp": "2026-08-01T12:00:00Z",
  "prediction": {
    "result": "2:1",
    "result_type": "HOME_WIN",
    "confidence": 0.89
  },
  "actual_result": "2:1",
  "accuracy": true,
  "consensus_type": "STRONG_CONSENSUS",
  "agreement_rate": 0.83,
  "validation_status": "VALID",
  "risk_level": "LOW",
  "decision_time_ms": 67,
  "feedback_received": true,
  "feedback_accuracy": true
}
```

**UPDATED:** Po kazdej decyzji
**RETENTION:** 2 lata

---

#### decision_quality
**DESCRIPTION:** Metryki jakości decyzji w czasie.

**STRUCTURE:**
```json
{
  "decision_id": "DECISION_20260801_001",
  "accuracy": true,
  "confidence_accuracy": 0.94,
  "risk_assessment_accuracy": 0.88,
  "evidence_quality": 0.87,
  "validation_pass_rate": 1.0,
  "response_time_ms": 67,
  "quality_score": 0.92
}
```

**UPDATED:** Po kazdym feedbacku
**RETENTION:** Bez terminu

---

#### decision_feedback
**DESCRIPTION:** Feedback i sugestie poprawy dla przyszłych decyzji.

**STRUCTURE:**
```json
{
  "decision_id": "DECISION_20260801_001",
  "feedback_timestamp": "2026-08-01T15:00:00Z",
  "accuracy": true,
  "accuracy_details": {
    "predicted": "2:1",
    "actual": "2:1",
    "match": true
  },
  "confidence_feedback": {
    "predicted_confidence": 0.89,
    "actual_confidence_accuracy": 0.94,
    "calibration_needed": false
  },
  "improvement_suggestions": [
    "Zwiekszyc wage agenta strategicznego",
    "Dodac weryfikacje zewnetrznych czynnikow"
  ],
  "applied_improvements": []
}
```

**UPDATED:** Po kazdym feedbacku
**RETENTION:** 1 rok

---

#### decision_patterns
**DESCRIPTION:** Wzorce sukcesow i porazek decyzyjnych.

**STRUCTURE:**
```json
{
  "pattern_id": "PATTERN_001",
  "pattern_type": "SUCCESS_PATTERN",
  "description": "Wysoka zgodnosc agentow + silne dowody → sukces",
  "characteristics": {
    "agreement_rate": ">= 0.8",
    "evidence_quality": ">= 0.8",
    "confidence": ">= 0.85"
  },
  "occurrence_count": 45,
  "success_rate": 0.93,
  "average_confidence": 0.89,
  "last_occurrence": "2026-08-01"
}
```

**UPDATED:** Po identyfikacji nowego wzorca
**RETENTION:** Bez terminu

---

## 7. FEEDBACK INTEGRATION

### 7.1 Feedback Flow

```
Realny wynik (od Decision Layer)
   ↓
[Decision Retrieval: Pobranie Decision Package z historii]
   ↓
[Comparison: Porownanie Prediction vs Actual Result]
   ↓
[Accuracy Assessment: Ocena dokładnosci]
   ↓
[Quality Evaluation: Ocena jakości decyzji]
   ↓
[Memory Update: Aktualizacja decision_history, decision_quality]
   ↓
[Pattern Identification: Identyfikacja wzorców]
   ↓
[Improvement Generation: Generowanie sugestii poprawy]
   ↓
[Future Decision Improvement: Zmiana parametrow i strategii]
```

### 7.2 Accuracy Assessment

**Metryki dokładnosci:**

| Metryka | Opis | Cel |
|---------|------|-----|
| Decision Accuracy | Dokladnosc predykcji (correct/total) | > 85% |
| Confidence Accuracy | Trafnosc oceny pewnosci | > 80% |
| Risk Assessment Accuracy | Dokladnosc oceny ryzyka | > 75% |
| Overall Quality Score | Laczna ocena jakości | > 80% |

**Klasyfikacja:**
- EXCELLENT (0.90-1.0)
- GOOD (0.80-0.89)
- ACCEPTABLE (0.70-0.79)
- POOR (0.60-0.69)
- FAIL (0.0-0.59)

### 7.3 Quality Evaluation

**Czynniki jakości:**
- **Consensus Quality** (0.0-1.0, waga 0.30): Jakosc konsensusu
- **Confidence Accuracy** (0.0-1.0, waga 0.25): Trafnosc pewnosci
- **Evidence Quality** (0.0-1.0, waga 0.20): Jakosc dowodow
- **Risk Assessment** (0.0-1.0, waga 0.15): Dokladnosc oceny ryzyka
- **Validation Status** (0.0-1.0, waga 0.10): Status walidacji

**Obliczanie Quality Score:**
quality_score = (consensus_quality * 0.30) + (confidence_accuracy * 0.25) + (evidence_quality * 0.20) + (risk_assessment * 0.15) + (validation_status * 0.10)

### 7.4 Memory Update

**Aktualizowane elementy:**
1. **decision_history:**
   - Uzupełnienie actual_result
   - Aktualizacja accuracy
2. **decision_quality:**
   - Dodanie nowych metryk
   - Aktualizacja historycznych statystyk
3. **decision_patterns:**
   - Identyfikacja nowych wzorców
   - Aktualizacja istniejacych
4. **decision_feedback:**
   - Zapis feedbacku
   - Generowanie sugestii poprawy

### 7.5 Future Decision Improvement

**Akcje poprawy:**
- Dostosowywanie wag agentow ( według historycznej dokladnosci)
- Optymalizacja progów walidacji
- Poprawa mechanizmów konsensusu (na podstawie feedbacku)
- Dostosowywanie strategii ryzyka
- Usprawnianie procesu agregacji

**Przyklad poprawy:**
Jeśli Agent_01 ma niska dokladnosc przy wysokiej pewnosci → zmniejszenie jego wagi w Weighted Voting

---

## 8. SEPARATION OF CONCERNS

### 8.1 Role Definition

| Komponent | Odpowiedzialnosc | **NIE** | Zaleznosci |
|-----------|------------------|---------|-------------|
| **Teacher Engine** | Generuje wiedzc na podstawie analizy danych zrodlowych | Nie podejmuje decyzji, nie interpretuje kontekstu | DATA SOURCES, WORLD MEMORY, FEATURE KNOWLEDGE |
| **Collective Teacher** | Agreguje wiedzc od Teacher Models | Nie generuje wiedzy zrodlowej | Teacher Models |
| **Agent System** | Interpretuje wiedzc, prowadzi rozumowanie, proponuje sugestie | Nie analizuje danych zrodlowych, nie modyfikuje World Memory | Teacher Engine, Memory Layer |
| **Agent Core** | Zarzadza agentami i koordynuje prace | Nie generuje wiedzy, nie podejmuje decyzji | Teacher Engine, Agent Components |
| **Agent Reasoning Engine** | Interpretacja wiedzy i generowanie sugestii indywidualnych | Nie tworzy wiedzy zrodlowej, nie podejmuje decyzji | Collective Teacher, Agent Memory |
| **Agent Collaboration** | Wspolpraca miedzyagentowa, konsensus, rozwiqzywaniu konfliktow | Nie tworzy wiedzy zrodlowej, nie zastępuje Teacher Engine, nie podejmuje decyzji | Agent Reasoning Engine, Agent Core |
| **Agent Decision** | Agregacja konsensusu, walidacja, formatowanie Decision Package | Nie tworzy wiedzy zrodlowej, nie podejmuje koncowej decyzji biznesowej | Agent Collaboration, Decision Layer |
| **Decision Layer** | Wybor finalnej decyzji biznesowej | Nie interpretuje wiedzy, nie generuje sugestii | Agent System, Feedback Layer |
| **Feedback Layer** | Aktualizacja pamieci na podstawie wynikow | Nie podejmuje decyzji, nie generuje wiedzy | Decision Layer, Memory Layer |
| **Memory Layer** | Przechowywanie i zarzadzanie pamiecia | Nie analizuje danych, nie podejmuje decyzji | Wszystkie warstwy |

### 8.2 Data Flow Boundaries

```
DATA SOURCES
   ↓ (dane surowce)
ANALYSIS LAYER → Generuje cechy
   ↓
WORLD MEMORY → Przechowuje kontekst historyczny
   ↓
FEATURE KNOWLEDGE → Przechowuje ranking cech
   ↓
TEACHER ENGINE → **Generuje wiedzc (TYLKO TU!)**
   ↓ (CollectivePredictionPackage)
AGENT SYSTEM → **Interpretuje wiedzc (TYLKO TU!)**
   │
   ├── Agent Core → Zarzadza
   ├── Agent Reasoning → Generuje sugestie indywidualne
   ├── Agent Collaboration → Buduje konsensus
   └── Agent Decision → Przygotowuje Decision Package
   ↓ (Decision Package)
DECISION LAYER → **Podejmuje decyzje (TYLKO TU!)**
   ↓
FEEDBACK LAYER → **Aktualizuje pamiec (TYLKO TU!)**
   ↓
MEMORY UPDATE → Aktualizuje World Memory, Feature Knowledge, Agent Memory
```

### 8.3 Zasady Separacji

1. **Teacher Engine** jest **jedynym** komponenem generujacym wiedzc z danych zrodlowych.
2. **Agent System** jest **jedynym** Systemem interpretujacym wiedzc i generujacym sugestie.
3. **Decision Layer** jest **jedynym** Systemem podejmujacym finalne decyzje biznesowe.
4. **Feedback Layer** jest **jedynym** Systemem aktualizujacym pamiec na podstawie wynikow.
5. Kazdy System dziala **tylko** w swoim zakresie odpowiedzialnosci.
6. Zmiana w jednym Systemie **NIE wymaga** zmian w innych Systemach (o ile zachowany jest interfejs)

---

## 9. PERFORMANCE METRICS

### 9.1 Decision Metrics

| Metryka | Opis | Cel | Aktualnie |
|---------|------|-----|-----------|
| decision_accuracy | Dokladnosc decyzji vs rzeczywisty wynik | > 85% | 87% |
| confidence_calibration | Kalibracja pewnosci (Brier Score) | < 0.15 | 0.12 |
| risk_assessment_accuracy | Dokladnosc oceny ryzyka | > 75% | 80% |
| validation_pass_rate | Odsetek decyzji z statusem VALID | > 90% | 94% |
| decision_quality_score | Laczna jakość decyzji | > 80% | 85% |

### 9.2 Pipeline Metrics

| Metryka | Opis | Cel | Aktualnie |
|---------|------|-----|-----------|
| aggregation_time | Czas agregacji | < 15ms | 12ms |
| validation_time | Czas walidacji | < 20ms | 18ms |
| confidence_evaluation_time | Czas oceny pewnosci | < 8ms | 6ms |
| risk_analysis_time | Czas analizy ryzyka | < 12ms | 10ms |
| formatting_time | Czas formatowania | < 8ms | 5ms |
| **total_pipeline_time** | **Calkowity czas** | **< 80ms** | **67ms** |

### 9.3 Resource Metrics

| Metryka | Opis | Cel | Aktualnie |
|---------|------|-----|-----------|
| memory_usage | Uzycie pamieci na decyzje | < 100MB | 85MB |
| decision_package_size | Rozmiar Decision Package | <= 16KB | 12KB |
| throughput | Liczba decyzji/sekunde | > 100 | 120 |
| uptime | Czas dostepnosci | > 99.9% | 99.95% |

---

## 10. PODSUMOWANIE

### 10.1 Utworzony Plik
**Nazwa:** `06_AGENT_DECISION.md`
**Lokalizacja:** `DOKUMENTACJA/SSI_V5_PHASE_2_AGENT_SYSTEM/`

### 10.2 Zakres Dokumentu
Dokument zawiera kompetna specyfikacje Agent Decision z 10 glownymi sekcjami:
1. Agent Decision Definition (rola, miejsce, odpowiedzialnosci, ograniczenia)
2. Decision Pipeline (6-etapowy proces: Input Validation, Decision Aggregation, Decision Validation, Confidence Evaluation, Risk Analysis, Formatting & Packaging)
3. Decision Engine Components (6 komponentow: Decision Aggregator, Decision Validator, Confidence Evaluator, Risk Analyzer, Decision Formatter, Decision History Manager - kazdy wedlug standardu)
4. Decision Package (format, struktura JSON, opisy pol)
5. Decision Validation (sprawdzanie zgodnosci, pewnosci, konfliktow, fallback)
6. Decision Memory (decision_history, decision_quality, decision_feedback, decision_patterns)
7. Feedback Integration (przeplyw, ocena dokładnosci, ocena jakości, aktualizacja pamieci, poprawa)
8. Separation of Concerns (definicja ról, granice przeplywu danych, zasady separacji)
9. Performance Metrics (metryki decyzji, pipeline, zasobów)

### 10.3 Spójność z Teacher Engine
✅ **Pelna spójność z dokumentacja Teacher Engine (01-09):**
- Agent Decision korzysta wyłacznie z wiedzy od Teacher Engine (przetworzonej przez Agent System)
- Brak ingerencji w Teacher Engine
- Zgodnosc z Separation of Concerns: Teacher Engine generuje wiedzc, Agent System interpretuje, Agent Decision przygotowuje pakiet
- Wspolne standardy opisu formatów i struktur danych

### 10.4 Spójność z Agent Core
✅ **Pelna spójność z 03_AGENT_CORE_ARCHITECTURE.md:**
- Agent Decision jest jednym z głównych komponentów Agent System
- Korzysta z Agent Core do koordynacji i zarzadzania
- Zgodnosc z przeplywem: Agent Core → Agent Reasoning → Agent Collaboration → Agent Decision → Decision Layer
- Korzystanie z rodzajów agentów zdefiniowanych w Agent Core
- Zgodnosc ze standardem opisu komponentów

### 10.5 Spójność z Agent Reasoning Engine
✅ **Pelna spójność z 04_AGENT_REASONING_ENGINE.md:**
- Agent Decision korzysta z AgentSuggestionPackage (opcjonalnie) wygenerowanych przez Agent Reasoning Engine
- Format AgentSuggestionPackage jest spójny z definicja w Reasoning Engine
- Separacja ról: Reasoning Engine generuje sugestie, Decision agreguje i waliduje
- Zgodnosc z strukturami danych i metrykami

### 10.6 Spójność z Agent Collaboration
✅ **Pelna spójność z 05_AGENT_COLLABORATION.md:**
- Agent Decision korzysta z ConsensusSuggestion dostarczonej przez Agent Collaboration
- Format ConsensusSuggestion jest spójny z definicja w Collaboration
- Zgodnosc z mechanizmami konsensusu, konfliktów i wag
- Integracja z Collaboration Memory (consensus_history, conflict_history)
- Zgodnosc z metrykami agreement_rate, confidence_alignment, evidence_similarity

### 10.7 Gotowosc
Dokument **06_AGENT_DECISION.md** jest:
- Kompletny - wszystkie wymagane sekcje zrealizowane
- Spójny - zgodny z wcześniejszymi dokumentami (01-05)
- Precyzyjny - konkretne specyfikacje, struktury JSON, formuły
- Praktyczny - gotowy do użycia jako podstawa implementacji Agent Decision
- Rozszerzalny - zdefiniowane FUTURE EXTENSIONS dla kazdego komponentu

### 10.8 Nastepny Sugerowany Dokument Agent System
**Nazwa:** 07_AGENT_FEEDBACK.md

**Zakres:**
- Szczegolowa specyfikacja Agent Feedback
- Odbior feedbacku od Decision Layer
- Ocena jakości sugestii i konsensusu
- Aktualizacja pamięci agentów
- Generowanie learning updates
- Integracja z Feedback Layer
- Mechanizmy uczenia
- Error handling w warstwie feedbacku

**Powiazania:**
- Rozszerza sekcje Agent Feedback z 01_AGENT_SYSTEM_OVERVIEW.md
- Wykorzystuje Agent Profile z 02_AGENT_PROFILE_SPECIFICATION.md
- Integruje się z Agent Core (03_AGENT_CORE_ARCHITECTURE.md)
- Korzysta z Agent Reasoning Engine (04_AGENT_REASONING_ENGINE.md)
- Uzywa danych z Agent Collaboration (05_AGENT_COLLABORATION.md)
- Korzysta z Decision Package z Agent Decision (06_AGENT_DECISION.md)

---

**Data utworzenia:** 2026-08-01
**Wersja:** 1.0.0
**Status:** Completed
**Autor:** Glowny Architekt SSI V5

---

**NOTATKA:** Dokument stanowi kompetna specyfikacje techniczna Agent Decision dla SSI V5 Phase 2, spójna z dokumentacja Teacher Engine, Agent System, Agent Core, Agent Reasoning Engine i Agent Collaboration. Nie wprowadza zmian w istniejacej architekturze. Jest fundamentem przyszlej implementacji Agent Decision. Nie zawiera kodu, klas ani implementacji - jedynie dokumentacje techniczna.