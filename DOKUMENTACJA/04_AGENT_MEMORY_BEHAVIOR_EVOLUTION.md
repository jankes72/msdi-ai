# 04 - AGENT MEMORY & BEHAVIOR EVOLUTION

**Data utworzenia:** 2026-08-01  
**Wersja:** 1.0.0  
**Status:** DRAFT  
**Autor:** Mistral Vibe - CLI Coding Agent  
**Typ dokumentu:** EWOLUCJA PAMIECI I ZACHOWANIA AGENTOW  
**Zaleznosc:**
- SSI_V5_MASTER_SYSTEM_FLOW_ARCHITECTURE.md (podstawa)
- 01_SYSTEM_SIGNAL_ARCHITECTURE.md (sygnaly)
- 02_DEVELOPER_INPUT_ARCHITECTURE.md (wejscie)
- 03_PROMPT_MANAGEMENT_SYSTEM.md (prompty)

---

## 1. PODSUMOWANIE EXECUTIVE

Ten dokument definiuje **Agent Memory & Behavior Evolution** - system ewolucji pamięci i zachowania agentów w SSI V5. Jest to **kluczowy dokument**, ktory szczegolowo opisuje jak kazdy agent posiada wlasna pamięć, wlasne predykcje, wlasny katalog wynikow, wlasny ranking strategii, historię sukcesow i bledow, oraz jak zmienia sie jego zachowanie w czasie.

**ZASADA FUNDAMENTALNA:** Pamięć wpływa na zachowanie agenta.

---

## 2. GLOWNE KONCEPCJE

### 2.1. Autonomiczny Agent

Kazdy agent w SSI V5 jest **autonomiczna jednostka decyzyjna** z:
- **Wlasna Pamiecia** - nie dzieli sie z innymi agentami (oproc layers wspolne)
- **Wlasna Osobowoscia** - unikalny wektor cech
- **Wlasnym Doświadczeniem** - historia decyzji i wynikow
- **Wlasnym Rankingiem Strategii** - preferencje decyzyjne
- **Wlasna Ewolucja** - zmiana zachowania w czasie

### 2.2. Zasady Pamięci

1. **Zasada Prywatnosci:** Kazdy agent ma wlasna, prywatna pamiec
2. **Zasada Trwalosci:** Pamiec jest zachowywana miedzy cyklami
3. **Zasada Kontekstu:** Pamiec jest ladowana na poczatku cyklu
4. **Zasada Aktualnosci:** Pamiec jest aktualizowana po kazdym cyklu
5. **Zasada Ewolucji:** Pamiec wpływa na przyszłe zachowanie

### 2.3. Zasady Zachowania

1. **Zasada Centrum:** Zachowanie agenta jest determinowane przez jego pamięć i osobowosc
2. **Zasada Doświadczenia:** Doświadczenia zmieniaja zachowanie
3. **Zasada Adaptacji:** Agenci uczą sie na bledach i sukcesach
4. **Zasada Indywidualnosci:** Kazdy agent rozwija sie inaczej
5. **Zasada Konsekwencji:** Zachowanie ma konsekwencje (sukces/porazka)

### 2.4. Rodzaje Pamięci (z agent_memory_store.py)

Kazdy agent posiada 4 typy pamieci, kazdy seriowany do osobnego pliku JSON:

| Typ Pamieci | Opis | Plik | Czyta/Pisze |
|-------------|------|------|--------------|
| **PERSONALITY** | Parametry osobowosci, wektor ewolucji | `PERSONALITY.json` | Cykl歐盟 |
| **BEHAVIOR** | Decyzje, predykcje, katalog wynikow, ranking strategii | `BEHAVIOR.json` | Cykl സമ |
| **STRATEGY** | Strategie produkcyjne i eksperymentalne | `STRATEGY.json` | Cyklّها |
| **HISTORY** | Historia sukcesow, bledow, doswiadczen | `HISTORY.json` | Cykl کی |

---

## 3. STRUKTURA PAMIECI AGENTA

### 3.1. PERSONALITY Memory - Osobowosc

**Odpowiedzialnosc:** Przechowywanie parametrow osobowosci agenta i ich ewolucji w czasie.

**Struktura:**
```json
{
  "agent_id": "01",
  "agent_name": "Analityk",
  "created_timestamp": "2026-01-01T00:00:00",
  "last_updated": "2026-08-01T12:00:00",
  
  "personality_vector": {
    "analysis": 0.90,
    "caution": 0.85,
    "curiosity": 0.60,
    "risk_tolerance": 0.40,
    "stability": 0.80,
    "exploration": 0.50,
    "confidence": 0.75,
    "social": 0.30
  },
  
  "personality_traits": {
    "FIXED": {
      "description": "Cecha stała, niezmienna w czasie",
      "value": 0.90,
      "weight": 0.5
    },
    "ADAPTIVE": {
      "description": "Cecha dostosowujaca sie do doswiadczen",
      "current_value": 0.40,
      "initial_value": 0.50,
      "min": 0.0,
      "max": 1.0,
      "adaptation_rate": 0.05,
      "history": [
        {"timestamp": "2026-01-01T00:00:00", "value": 0.50, "reason": "initial"},
        {"timestamp": "2026-02-01T00:00:00", "value": 0.45, "reason": "3 failures"},
        {"timestamp": "2026-03-01T00:00:00", "value": 0.42, "reason": "2 more failures"},
        {"timestamp": "2026-08-01T00:00:00", "value": 0.40, "reason": "1 more failure"}
      ]
    }
  },
  
  "evolution_rules": {
    "success": {
      "confidence": +0.01,
      "exploration": +0.02,
      "risk_tolerance": +0.01
    },
    "failure": {
      "caution": +0.02,
      "risk_tolerance": -0.02,
      "exploration": -0.01
    },
    "high_risk_success": {
      "confidence": +0.03,
      "risk_tolerance": +0.02,
      "exploration": +0.03
    },
    "high_risk_failure": {
      "caution": +0.05,
      "risk_tolerance": -0.05,
      "exploration": -0.03
    }
  },
  
  "evolution_history": [
    {
      "timestamp": "2026-01-01T00:00:00",
      "change": "initial",
      "old_vector": null,
      "new_vector": {"analysis": 0.90, "caution": 0.85, ...},
      "reason": "Initial configuration"
    },
    {
      "timestamp": "2026-02-01T00:00:00",
      "change": "adaptation",
      "old_vector": {"analysis": 0.90, "caution": 0.85, "risk_tolerance": 0.50},
      "new_vector": {"analysis": 0.90, "caution": 0.87, "risk_tolerance": 0.48},
      "reason": "3 consecutive failures",
      "decision_ids": ["dec_001", "dec_002", "dec_003"]
    }
  ],
  
  "trust_memory": {
    "other_agents": {
      "02": {"trust_score": 0.85, "interactions": 47, "last_interaction": "2026-08-01T10:00:00"},
      "03": {"trust_score": 0.70, "interactions": 23, "last_interaction": "2026-07-30T14:00:00"},
      "04": {"trust_score": 0.60, "interactions": 15, "last_interaction": "2026-07-28T09:00:00"},
      "05": {"trust_score": 0.90, "interactions": 56, "last_interaction": "2026-08-01T11:00:00"},
      "06": {"trust_score": 0.75, "interactions": 32, "last_interaction": "2026-07-31T16:00:00"}
    },
    "data_sources": {
      "V2_siec_01": {"trust_score": 0.95, "usage_count": 100},
      "V2_siec_02": {"trust_score": 0.88, "usage_count": 95},
      "V3_WorldMemory": {"trust_score": 0.98, "usage_count": 150}
    }
  }
}
```

**Ewolucja Osobowosci:**
- Każde doświadczenie (sukces/porażka) wpływa na wektor osobowości
- Zmiany sa stopniowe (adaptation_rate)
- Historia zmian jest zachowywana
- Możliwy powrót do wcześniejszych wartości

**Pierwsza Populacja (z SSI/V4):**
- **Agent 01 (Analityk):** analysis=0.9, caution=0.85, curiosity=0.6
- **Agent 02 (Strateg Wartości):** risk_tolerance=0.8, analysis=0.75, confidence=0.9
- **Agent 03 (Eksperymentator):** curiosity=0.95, exploration=0.9, risk_tolerance=0.7

### 3.2. BEHAVIOR Memory - Zachowanie i Decyzje

**Odpowiedzialnosc:** Przechowywanie historii decyzji, predykcji, strategii i rankingu.

**Struktura:**
```json
{
  "agent_id": "01",
  "last_updated": "2026-08-01T12:00:00",
  
  "decision_history": [
    {
      "decision_id": "dec_001",
      "timestamp": "2026-08-01T10:00:00",
      "cycle_number": 1,
      "decision_type": "bet_placement",
      "context": {
        "match_id": "match_001",
        "data_sources": ["V2_siec_01", "V2_siec_02", "V3_WorldMemory"],
        "available_strategies": ["strategy_01", "strategy_05", "strategy_12"],
        "market_conditions": {
          "course_1": 2.15,
          "course_X": 3.20,
          "course_2": 3.50
        }
      },
      "chosen_action": {
        "type": "PLACE_BET",
        "selection": "1",
        "amount": 100,
        "odds": 2.15,
        "strategy_id": "strategy_05",
        "strategy_version": "2.1"
      },
      "alternatives_considered": [
        {"type": "PLACE_BET", "selection": "X", "amount": 100, "odds": 3.20, "rejected_reason": "low_value"},
        {"type": "NO_BET", "amount": 0, "rejected_reason": "high_confidence"}
      ],
      "confidence": 0.87,
      "risk_assessment": 0.13,
      "expected_value": 115.00,
      "outcome": "SUCCESS",
      "actual_result": "WIN",
      "profit": 115.00,
      "performance_score": 0.92,
      "feedback": {
        "self_assessment": "Good decision based on available data",
        "lessons_learned": ["Course was accurate", "Strategy performed well"],
        "improvements": ["Consider higher risk tolerance"]
      }
    },
    {
      "decision_id": "dec_002",
      "timestamp": "2026-08-01T11:00:00",
      "cycle_number": 2,
      "decision_type": "bet_placement",
      "context": { ... },
      "chosen_action": {
        "type": "PLACE_BET",
        "selection": "1",
        "amount": 200,
        "odds": 1.90,
        "strategy_id": "strategy_12"
      },
      "confidence": 0.78,
      "risk_assessment": 0.22,
      "expected_value": 152.00,
      "outcome": "FAILURE",
      "actual_result": "LOSS",
      "profit": -200.00,
      "performance_score": 0.45,
      "feedback": {
        "self_assessment": "Incorrect assessment of risk",
        "lessons_learned": ["Course was misleading", "Strategy failed"],
        "improvements": ["Need better risk evaluation"]
      }
    }
  ],
  
  "prediction_history": [
    {
      "prediction_id": "pred_001",
      "timestamp": "2026-08-01T10:00:00",
      "cycle_number": 1,
      "target": "match_001_result",
      "predicted_value": "1",
      "confidence": 0.85,
      "method": "siec_01_analysis",
      "actual_value": "1",
      "accuracy": 1.0,
      "calibration": 0.95,
      "impact_on_decision": "HIGH"
    },
    {
      "prediction_id": "pred_002",
      "timestamp": "2026-08-01T11:00:00",
      "cycle_number": 2,
      "target": "match_002_result",
      "predicted_value": "X",
      "confidence": 0.72,
      "method": "siec_02_analysis",
      "actual_value": "1",
      "accuracy": 0.0,
      "calibration": 0.30,
      "impact_on_decision": "MEDIUM",
      "miss_reason": "Insufficient data"
    }
  ],
  
  "strategy_ranking": {
    "production_strategies": [
      {
        "strategy_id": "strategy_05",
        "version": "2.1",
        "rank": 1,
        "score": 92.5,
        "usage_count": 45,
        "success_count": 38,
        "failure_count": 7,
        "success_rate": 0.844,
        "avg_profit": 85.50,
        "avg_confidence": 0.88,
        "avg_risk": 0.12,
        "last_used": "2026-08-01T10:00:00",
        "status": "ACTIVE",
        "preference": 0.95
      },
      {
        "strategy_id": "strategy_12",
        "version": "1.0",
        "rank": 2,
        "score": 78.3,
        "usage_count": 23,
        "success_count": 15,
        "failure_count": 8,
        "success_rate": 0.652,
        "avg_profit": 42.50,
        "avg_confidence": 0.75,
        "avg_risk": 0.25,
        "last_used": "2026-08-01T11:00:00",
        "status": "ACTIVE",
        "preference": 0.70
      },
      {
        "strategy_id": "strategy_01",
        "version": "3.0",
        "rank": 3,
        "score": 75.0,
        "usage_count": 18,
        "success_count": 12,
        "failure_count": 6,
        "success_rate": 0.667,
        "avg_profit": 38.00,
        "avg_confidence": 0.80,
        "avg_risk": 0.15,
        "last_used": "2026-07-31T16:00:00",
        "status": "ACTIVE",
        "preference": 0.65
      }
    ],
    "experimental_strategies": [
      {
        "strategy_id": "exp_strategy_01",
        "version": "0.5",
        "rank": 1,
        "score": 65.0,
        "usage_count": 5,
        "success_count": 3,
        "failure_count": 2,
        "success_rate": 0.600,
        "test_phase": "ALPHA",
        "status": "TESTING",
        "promotion_candidate": true,
        "required_tests": 10,
        "completed_tests": 5
      }
    ],
    "ranking_algorithm": "SCORING",
    "scoring_formula": "score = (success_rate * 0.4) + (avg_profit_normalized * 0.3) + (avg_confidence * 0.2) + (usage_count_normalized * 0.1)"
  },
  
  "results_catalog": {
    "by_outcome": {
      "SUCCESS": {
        "count": 38,
        "total_profit": 3245.00,
        "avg_profit": 85.39,
        "avg_confidence": 0.89
      },
      "FAILURE": {
        "count": 15,
        "total_loss": -1250.00,
        "avg_loss": -83.33,
        "avg_confidence": 0.72
      },
      "NEUTRAL": {
        "count": 7,
        "total_profit": 0.00,
        "avg_confidence": 0.65
      }
    },
    "by_strategy": {...},
    "by_decision_type": {...},
    "by_cycle": {...}
  },
  
  "behavior_patterns": [
    {
      "pattern_id": "pattern_01",
      "name": "Conservative Betting",
      "description": "Layer bety przy wysokiej pewnosci (>0.85)",
      "activation_count": 25,
      "success_rate": 0.88,
      "avg_profit": 75.00,
      "typical_confidence": 0.90,
      "typical_risk": 0.10
    },
    {
      "pattern_id": "pattern_02",
      "name": "High Risk Opportunity",
      "description": "Wysokie zakłady przy wykrytych okazjach",
      "activation_count": 12,
      "success_rate": 0.58,
      "avg_profit": 150.00,
      "typical_confidence": 0.75,
      "typical_risk": 0.35
    }
  ]
}
```

**-ranking strategii** jest indywidualny dla kazdego agenta:
- Agenci NIE kopiuja strategii innych agentow
- Mogą analizować sposób działania innych agentow
- Każdy agent tworzy własne ulepszenia i ranking

**Katalog wynikow** klasyifikuje decyzje wedlug:
- Outcome (SUCCESS, FAILURE, NEUTRAL)
- Strategy used
- Decision type
- Cycle number

**Wzorce zachowania** sa automatycznie wykrywane na podstawie historii decyzji.

### 3.3. STRATEGY Memory - Strategie

**Odpowiedzialnosc:** Przechowywanie strategii produkcyjnych i eksperymentalnych, ich parametrow, historii i rankingu.

**Struktura:**
```json
{
  "agent_id": "01",
  "last_updated": "2026-08-01T12:00:00",
  
  "production_strategies": {
    "strategy_05": {
      "strategy_id": "strategy_05",
      "version": "2.1",
      "name": "Value Betting",
      "description": "Strategia oparta na wartosci kursu i pewnosci",
      "category": "production",
      "status": "ACTIVE",
      
      "parameters": {
        "min_confidence": 0.80,
        "max_risk": 0.20,
        "min_expected_value": 1.2,
        "preferred_bet_type": ["1", "2"],
        "avoid_bet_type": ["X"],
        "amount_calculation": "kelly_criterion",
        "kelly_fraction": 0.5
      },
      
      "creation_info": {
        "created_by": "system",
        "created_timestamp": "2026-01-01T00:00:00",
        "source": "initial_population"
      },
      
      "usage_history": [
        {
          "usage_id": "use_001",
          "decision_id": "dec_001",
          "timestamp": "2026-08-01T10:00:00",
          "parameters_used": { ... },
          "outcome": "SUCCESS",
          "confidence": 0.87,
          "risk": 0.13,
          "profit": 115.00,
          "performance_score": 0.92
        },
        {
          "usage_id": "use_042",
          "decision_id": "dec_042",
          "timestamp": "2026-07-30T14:00:00",
          "parameters_used": { ... },
          "outcome": "FAILURE",
          "confidence": 0.82,
          "risk": 0.18,
          "profit": -150.00,
          "performance_score": 0.55
        }
      ],
      
      "performance_metrics": {
        "total_usage": 45,
        "success_count": 38,
        "failure_count": 7,
        "success_rate": 0.844,
        "total_profit": 2850.00,
        "avg_profit": 85.50,
        "max_profit": 450.00,
        "min_profit": -150.00,
        "std_dev_profit": 125.30,
        "avg_confidence": 0.88,
        "avg_risk": 0.12,
        "sharpe_ratio": 2.15,
        "sortino_ratio": 3.20
      },
      
      "adaptation_history": [
        {
          "timestamp": "2026-02-01T00:00:00",
          "change": "parameter_tuning",
          "old_parameters": { ... },
          "new_parameters": {"min_confidence": 0.80, "kelly_fraction": 0.5},
          "reason": "Reduce variance",
          "performance_before": 0.78,
          "performance_after": 0.84
        }
      ],
      
      "peer_analysis": {
        "compared_with": ["Agent_02", "Agent_05"],
        "relative_performance": 0.92,
        "unique_strengths": ["Better risk assessment", "Higher consistency"],
        "potential_improvements": ["More aggressive when confident"]
      }
    },
    "strategy_12": { ... },
    "strategy_01": { ... }
  },
  
  "experimental_strategies": {
    "exp_strategy_01": {
      "strategy_id": "exp_strategy_01",
      "version": "0.5",
      "name": "Dynamic Risk Adaptation",
      "description": "Eksperymentalna strategia dostosowujaca ryzyko do warunkow rynkowych",
      "category": "experimental",
      "status": "TESTING",
      "test_phase": "ALPHA",
      
      "hypothesis": {
        "statement": "Adaptacyjne ryzyko zwieksza skutecznosc o 15%",
        "success_criteria": "success_rate > 0.75 i avg_profit > 100",
        "failure_criteria": "success_rate < 0.60 lub total_loss > 500"
      },
      
      "parameters": {
        "initial_risk": 0.25,
        "adaptation_rate": 0.05,
        "max_risk": 0.40,
        "min_risk": 0.10,
        "market_indicators": ["volatility", "liquidity", "trend_strength"]
      },
      
      "test_results": [
        {
          "test_id": "test_01",
          "timestamp": "2026-07-30T10:00:00",
          "data_used": "historical_2026_01-06",
          "outcome": "SUCCESS",
          "result": {
            "success_rate": 0.80,
            "avg_profit": 125.00,
            "total_tests": 20,
            "success_count": 16
          },
          "notes": "Good results on stable markets"
        },
        {
          "test_id": "test_02",
          "timestamp": "2026-07-31T10:00:00",
          "data_used": "historical_2026_01-07",
          "outcome": "PARTIAL",
          "result": {
            "success_rate": 0.65,
            "avg_profit": 95.00,
            "total_tests": 20,
            "success_count": 13
          },
          "notes": "Struggles with volatile markets"
        }
      ],
      
      "evaluation": {
        "current_score": 65.0,
        "promotion_recommendation": "CONTINUE_TESTING",
        "required_improvements": ["Handle volatility better"],
        "estimated_potential": 85.0
      }
    }
  },
  
  "strategy_evolution": {
    "creation_process": "POMYSL -> TEST -> OCENA -> RANKING -> AKCEPTACJA",
    "innovation_rate": 0.2,
    "adoption_rate": 0.15,
    "retirement_rate": 0.05,
    
    "created_strategies": [
      {"strategy_id": "exp_strategy_01", "created_at": "2026-07-01", "inspired_by": "Agent_02"}
    ],
    "adopted_strategies": [
      {"strategy_id": "strategy_05", "adopted_from": "none", "adaptation": "own_creation"}
    ],
    "retired_strategies": [
      {"strategy_id": "strategy_03", "retired_at": "2026-06-01", "reason": "low_performance"}
    ]
  }
}
```

**Proces Pomysl -> Test -> Ocena -> Ranking -> Akceptacja:**
1. Agent identyfikuje nowa mozliwosc (inspiracja z wlasnych doswiadczen, analizy innych agentow, lub nowych danych)
2. Tworzy eksperymentalna strategie (exp_strategy_XX)
3. Testuje na historycznych danych lub w symulacji
4. Ocenia wyniki zgodnie z hypothesis
5. Jesli success_criteria spelnione: awans do produkcji
6. Jesli failure_criteria spelnione: porzuca strategie
7. Jeśli można poprawić: kontynuuje testy

**Agenci NIE kopiuja strategii innych agentow** - moga jedynie analizować ich sposób działania i tworzyć własne ulepszenia.

### 3.4. HISTORY Memory - Historia

**Odpowiedzialnosc:** Pełna historia doswiadczen, sukcesow, bledow i nauki agenta.

**Struktura:**
```json
{
  "agent_id": "01",
  "created_timestamp": "2026-01-01T00:00:00",
  "last_updated": "2026-08-01T12:00:00",
  
  "cycle_history": [
    {
      "cycle_number": 1,
      "timestamp": "2026-08-01T10:00:00",
      "duration_ms": 15000,
      "decisions_made": 1,
      "predictions_made": 3,
      "memory_updated": true,
      "outcome": "SUCCESS",
      "total_profit": 115.00,
      "learning_outcomes": [
        "Confirmed strategy_05 effectiveness",
        "Identified new pattern in data"
      ],
      "errors": [],
      "warnings": []
    },
    {
      "cycle_number": 2,
      "timestamp": "2026-08-01T11:00:00",
      "duration_ms": 14500,
      "decisions_made": 1,
      "predictions_made": 2,
      "memory_updated": true,
      "outcome": "FAILURE",
      "total_profit": -200.00,
      "learning_outcomes": [
        "Identified risk evaluation weakness",
        "Strategy_12 needs improvement"
      ],
      "errors": ["Prediction error for match_002"],
      "warnings": ["High risk tolerance may be too aggressive"]
    }
  ],
  
  "success_history": [
    {
      "success_id": "succ_001",
      "timestamp": "2026-08-01T10:00:00",
      "cycle_number": 1,
      "decision_id": "dec_001",
      "type": "BET_WIN",
      "profit": 115.00,
      "confidence": 0.87,
      "impact_on_learning": "HIGH",
      "lessons": [
        "Strategy_05 works well with high confidence",
        "Course analysis was accurate"
      ],
      "reinforcement": {
        "positive": 0.9,
        "applied_to": ["confidence", "strategy_05_preference"]
      }
    },
    {
      "success_id": "succ_005",
      "timestamp": "2026-07-30T16:00:00",
      "cycle_number": 15,
      "decision_id": "dec_015",
      "type": "HIGH_VALUE_DISCOVERY",
      "profit": 500.00,
      "confidence": 0.92,
      "impact_on_learning": "CRITICAL",
      "lessons": [
        "Identified new value pattern",
        "Created exp_strategy_01 concept"
      ],
      "reinforcement": {
        "positive": 1.0,
        "applied_to": ["exploration", "curiosity", "confidence"]
      }
    }
  ],
  
  "error_history": [
    {
      "error_id": "err_001",
      "timestamp": "2026-08-01T11:00:00",
      "cycle_number": 2,
      "decision_id": "dec_002",
      "type": "RISK_MISASSESSMENT",
      "severity": "HIGH",
      "impact": {
        "financial": -200.00,
        "learning": "MEDIUM"
      },
      "root_cause": "Overestimated course reliability",
      "contributing_factors": [
        "Insufficient historical data",
        "Ignored volatility indicator"
      ],
      "lessons_learned": [
        "Need better volatility analysis",
        "Increase caution with high odds"
      ],
      "preventive_actions": [
        "Updated risk assessment criteria",
        "Modified strategy_12 parameters"
      ],
      "reinforcement": {
        "negative": 0.8,
        "applied_to": ["risk_tolerance", "caution"]
      }
    },
    {
      "error_id": "err_005",
      "timestamp": "2026-07-28T12:00:00",
      "cycle_number": 10,
      "decision_id": "dec_010",
      "type": "DATA_MISINTERPRETATION",
      "severity": "MEDIUM",
      "impact": {
        "financial": -75.00,
        "learning": "HIGH"
      },
      "root_cause": "Incorrect pattern recognition",
      "contributing_factors": ["Limited data sample", "Overfitting to recent trends"],
      "lessons_learned": ["Need larger data samples", "Consider longer trends"],
      "preventive_actions": ["Increased data validation"],
      "reinforcement": {
        "negative": 0.6,
        "applied_to": ["analysis", "stability"]
      }
    }
  ],
  
  "learning_curves": {
    "overall": {
      "data_points": [
        {"cycle": 1, "performance": 0.65, "confidence": 0.70, "profit": 50.00},
        {"cycle": 10, "performance": 0.78, "confidence": 0.80, "profit": 1500.00},
        {"cycle": 50, "performance": 0.85, "confidence": 0.85, "profit": 12500.00},
        {"cycle": 100, "performance": 0.88, "confidence": 0.88, "profit": 35000.00}
      ],
      "regression": {
        "equation": "performance = 0.65 + (0.0023 * cycle)",
        "r_squared": 0.89
      }
    },
    "by_strategy": {
      "strategy_05": {
        "data_points": [...],
        "improvement_rate": 0.003
      }
    },
    "by_decision_type": {
      "bet_placement": {
        "data_points": [...],
        "asymptote": 0.92
      }
    }
  },
  
  "cumulative_statistics": {
    "total_cycles": 100,
    "total_decisions": 600,
    "total_predictions": 1800,
    "total_profit": 35500.00,
    "total_successes": 420,
    "total_failures": 140,
    "total_neutral": 40,
    "overall_success_rate": 0.700,
    "overall_roi": 3.55,
    "effectiveness_score": 0.82
  },
  
  "milenstones": [
    {
      "milestone_id": "ms_001",
      "name": "First Successful Decision",
      "timestamp": "2026-01-01T10:00:00",
      "cycle_number": 1,
      "description": "Pierwsza sukcesowna decyzja z profit 115.00",
      "significance": "HIGH"
    },
    {
      "milestone_id": "ms_005",
      "name": "Break Even Point",
      "timestamp": "2026-01-15T12:00:00",
      "cycle_number": 25,
      "description": "Calkowity zysk przewyzsza Strate calkowita",
      "significance": "CRITICAL"
    },
    {
      "milestone_id": "ms_010",
      "name": "Strategy Creation",
      "timestamp": "2026-07-01T14:00:00",
      "cycle_number": 95,
      "description": "Utworzenie pierwszej wlasnej strategii (exp_strategy_01)",
      "significance": "CRITICAL"
    }
  ],
  
  "experience_trace": {
    "description": "Pelna historia doswiadczen agenta, NIGDY nie usuwana",
    "compression": "enabled",
    "retention_policy": "ALL",
    "size_bytes": 450000,
    "entry_count": 600
  }
}
```

**Historia sukcesow i bledow** jest kluczowa dla ewolucji agenta:
- **Sukcesy** wzmacniaja pozytywne cechy (confidence, exploration, risk_tolerance)
- **Bledy** wzmacniaja ostroznosc (caution) i redukuja ryzyko (risk_tolerance)
- Kazda lekcja jest zapamietywana i wpływa na przyszłe zachowanie

**Krzywe uczenia sie** pokazują postęp agenta w czasie.

**Experience Trace** jest NIGDY usuwany - zapewnia ciagłosc pamieci.

---

## 4. BEHAVIOR EVOLUTION - EWOLUCJA ZACHOWANIA

### 4.1. Wplyw Pamieci na Zachowanie

```
PAMIEC → OSOBOWOSC → ZACHOWANIE
   │          │            │
   ▼          ▼            ▼
Dane → Wektor → Decyzje
z przyszlosci
```

**Doświadczenia wpływaja na:**
1. **Sposob decyzji** - Jak agent podejmuje decyzje
2. **Poziom ryzyka** - Jak duze ryzyko agent akceptuje
3. **Pewnosc siebie** - Jak bardzo agent ufa swoim decyzjom
4. **Eksploracje** - Jak chetnie agent testuje nowosci
5. **Preferowane strategie** - Ktore strategie agent preferuje

### 4.2. Mechanizmy Ewolucji

**1. Direct Reinforcement (Wzmocnienie Bezposrednie):**
```
Sukces → +Reinforcement → Zmiana parametrow
   │
   ├── confidence += 0.01 * (1 - confidence) * success_impact
   ├── exploration += 0.02 * (1 - exploration)
   ├── risk_tolerance += 0.01 * (1 - risk_tolerance)
   └── strategy_preference[used_strategy] += 0.05

Porazka → -Reinforcement → Zmiana parametrow
   │
   ├── caution += 0.02 * (1 - caution) * failure_impact
   ├── risk_tolerance -= 0.02 * risk_tolerance
   ├── exploration -= 0.01 * exploration
   └── strategy_preference[used_strategy] -= 0.10
```

**2. Adaptive Learning (Uczenie Adaptacyjne):**
```
Agent analizuje wzorce w swoich decyzjach:
1. Jakie czynniki prowadza do sukcesu
2. Jakie czynniki prowadza do porazki
3. Jakie strategie dzialaja najlepiej w jakich warunkach

Przyklad:
- Jeśli wysoka pewnosc + niskie ryzyko → sukces (80% przypadkow)
  → Zwieksz wagę tych czynnikow w przyszłych decyzjach

- Jeśli niska pewnosc + wysokie ryzyko → porazka (70% przypadkow)
  → Zmniejsz wagę tych czynnikow
```

**3. Social Learning (Uczenie Społeczne):**
```
Agent moze uczyc sie od innych agentow:
1. Analizuje decyzje innych agentow
2. Porownuje z wlasnymi decyzjami
3. Wypatruje wzorców i róznic
4. Tworzy wlasne ulepszenia

WAZNE: Agenci NIE kopiuja strategii innych!
Moga jedynie analizowac i tworzyc wlasne wersje.

Przyklad:
- Agent 05 osiaga wysoka skutecznosc z niska pewnoscia
- Agent 01 analizuje: "Agent 05 uzywa innych wskaźnikow ryzyka"
- Agent 01 tworzy: Wlasna strategie z modyfikowanymi ryzykiem
- Agent 01 testuje: Nowa strategie (exp_strategy_02)
```

**4. Environmental Adaptation (Adaptacja do Srodowiska):**
```
Agent dostosowuje sie do zmian w srodowisku:
1. Wykrywa zmiane wzorców danych
2. Okresla typ zmiany (trend, wahania, anomalie)
3. Dostosowuje swoje parametry

Przyklad:
- Wykryto zwiekszona zmiennosc rynku
- Zwieksz wagę stabilnosci w ocenie
- Zmniejsz tolerancje ryzyka tymczasowo
```

### 4.3. Wplyw na Osobowosc

**Ewolucja Wektora Osobowosci:**
```
Osobowosc = f(Sukcesy, Porazki, Srodowisko, Czas)

Przyklad dla Agenta 01 (Analityk):
Poczatkowa: {analysis: 0.90, caution: 0.85, curiosity: 0.60, risk_tolerance: 0.40}

Po 100 cykli:
- 65 sukcesow (avg confidence: 0.88)
- 35 porazek (avg risk: 0.25)
- 5 nowych strategii utworzonych
- 12 analized innych agentow

Nowa: {analysis: 0.92, caution: 0.88, curiosity: 0.72, risk_tolerance: 0.38}

Zmiany:
- analysis: +0.02 (wiecej danych do analizy)
- caution: +0.03 (wiecej porazek z ryzykiem)
- curiosity: +0.12 (wiecej sukcesow z eksploracja)
- risk_tolerance: -0.02 (wiecej porazek)
```

### 4.4. Zmiana Zachowania w Czasie

**Fazy Ewolucji Agenta:**

```
┌─────────────────────────────────────────────────────────────────┐
│ Faza 1: AKLIMATYZACJA (Cycles 1-10)                              │
│ - Uczenie sie srodowiska                                          │
│ - Testowanie poczatkowych strategii                              │
│ - Budowanie zaufania do danych                                    │
│ - Wysokie ryzyko bledow                                           │
│ - Niska pewnosc                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Faza 2: STABILIZACJA (Cycles 11-50)                             │
│ - Redukcja bledow                                                 │
│ - Zwiekszanie pewnosci                                            │
│ - Optymalizacja poczatkowych strategii                           │
│ - Budowanie wzorców zachowania                                   │
│ - Stabilne wyniki                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Faza 3: OPTYMALIZACJA (Cycles 51-150)                            │
│ - Tworzenie wlasnych strategii                                   │
│ - Analiza innych agentow                                          │
│ - Adaptacja do srodowiska                                         │
│ - Zwiekszanie efektywnosci                                        │
│ -due do procesu decyzyjnego                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Faza 4: MASTERING (Cycles 150+)                                   │
│ - Pelne zrozumienie srodowiska                                    │
│ - zaawansowane strategie                                          │
│ - Minimalne bledy                                                  │
│ - Wysoka efektywnosc                                              │
│ - Innowacyjnosc i kreatywnosc                                     │
└─────────────────────────────────────────────────────────────────┘
```

### 4.5. Charakter Zachowania

**Agent 01 - Analityk:**
- **Poczatek:** Wysoka analiza, wysoka ostroznosc, niska ciekawosc
- **Ewolucja:** Zwieksza ciekawosc, redukuje ryzyko po bledach
- **Charakter:** Ahmetyczny, ostrozony, metodyczny
- **Mocne strony:** Dokladnosc, stabilnosc, niskie ryzyko
- **Sklonnosci:** Unikanie ryzyka, dlugie analizy

**Agent 02 - Strateg Wartosci:**
- **Poczatek:** Wysoka akceptacja ryzyka, wysoka analiza kursu
- **Ewolucja:** Zmniejsza ryzyko po portkwiazach, zwieksza pewnosc
- **Charakter:** Odwazny, optymistyczny, skupiony na wartosci
- **Mocne strony:** Wysokie zyski w dobrych warunkach
- **Sklonnosci:** Przesadna pewnosc sie, lekcewazenie ryzyka

**Agent 03 - Eksperymentator:**
- **Poczatek:** Wysoka ciekawosc, wysoka eksploracja, umiarkowana tolerate ryzyka
- **Ewolucja:** Balansuje eksperymenty z produkcja
- **Charakter:** Innowacyjny, kreatywny, ciekawy
- **Mocne strony:** Odkrywanie nowych wzorców, tworzenie nowych strategii
- **Sklonnosci:** Nadmierna eksploracja, niestabilnosc

---

## 5. MEMORY OPERATIONS

### 5.1. Cykl Zycia Pamieci w Cyklu Agenta

```
AGENT CYCLE MEMORY FLOW (z agent_runtime.py):

STEP 1: LOAD MEMORY (Poczatek cyklu)
├── Load PERSONALITY.json
├── Load BEHAVIOR.json
├── Load STRATEGY.json
└── Load HISTORY.json
    │
    ▼
STEP 2: FETCH DATA (Pobieranie danych)
├── Get V2 Data
├── Get V3 Data
├── Get V4 Data
└── Get External Data
    │
    ▼
STEP 3: COMPARE (Porownanie)
└── STARA WIEDZA + NOWE DANE
    │ (Wykrywanie zmian, nowych wzorców, rozbieznosci)
    │
    ▼
STEP 4: ANALYZE (Analiza)
└── Uzycie pamieci do:
    ├── Kontekst historyczny
    ├── Similar decisions
    ├── Strategy selection
    └── Risk assessment
    │
    ▼
STEP 5: DECISION (Decyzja)
└── Wybor ACTION na podstawie:
    ├── Personality vector
    ├── Strategy ranking
    ├── Risk tolerance
    └── Current context
    │
    ▼
STEP 6: RECORD EXPERIENCE (Zapis doswiadczenia)
├── Save Decision Record → BEHAVIOR.json
├── Save Prediction Record → BEHAVIOR.json
├── Update Strategy Usage → STRATEGY.json
└── Update History → HISTORY.json
    │
    ▼
STEP 7: MEMORY UPDATE (Aktualizacja pamieci)
├── Update Personality (jesli ewolucja)
├── Update Behavior Patterns
├── Update Strategy Rankings
└── Update History Statistics
    │
    ▼
STEP 8: SAVE MEMORY (Zapis na dysk)
├── Save PERSONALITY.json
├── Save BEHAVIOR.json
├── Save STRATEGY.json
└── Save HISTORY.json
```

### 5.2. Zarzadzanie Plikami Pamieci

**Struktura plikow (z SSI/v5/memory/agents/):**
```
SSI/v5/memory/agents/
├── agent_01/
│   ├── PERSONALITY.json
│   ├── BEHAVIOR.json
│   ├── STRATEGY.json
│   └── HISTORY.json
├── agent_02/
│   ├── PERSONALITY.json
│   ├── BEHAVIOR.json
│   ├── STRATEGY.json
│   └── HISTORY.json
├── agent_03/
│   ├── ...
├── agent_04/
│   ├── ...
├── agent_05/
│   ├── ...
└── agent_06/
    ├── ...
```

**AgentMemoryStore (z agent_memory_store.py):**
- Zarzadza odczytem/zapisem plikow JSON
- Zapewnia transakcyjnosc (caly stan albo wcale)
- Implemetnuje backup i recovery
- Monitoruje rozmiar pamieci

### 5.3. Synchronizacja Pamieci

**Zasady synchronizacji:**
1. Pamiec jest ladowana na poczatku kazdego cyklu
2. Pamiec jest aktualizowana w tracie cyklu
3. Pamiec jest zapisywana na koncu cyklu
4. W przypadku bledu: powrot do ostatniej poprawniej wersji

**Mechanizm Backup:**
```
Przed zapisem:
1. Utworz backup aktualnych plikow
2. Sprawdz integralnosc nowych danych
3. Zapisz nowe pliki
4. Zweryfikuj zapis
5. Usun stare backupy (zachowaj ostatnie 10)
```

---

## 6. COLLECTIVE INTELLIGENCE

### 6.1. Wspolpraca Miedzy Agentami

**Zasady:**
1. **Brak Bezposredniego Kopiowania:** Agenci NIE kopiuja strategii innych
2. **Analiza i Inspiracja:** Agenci znacznie analizowac idee innych
3. **Wlasne Implementacje:** Kazdy agent tworzy wlasne ulepszenia
4. **Wspolne Wzorce:** Agenci moga uczyc sie z wzorców systemowych

**Mechanizmy Wspolpracy:**

**1. Trust Memory:**
```json
"trust_memory": {
  "other_agents": {
    "02": {"trust_score": 0.85, "reliability": "HIGH", "specialty": "value_betting"},
    "03": {"trust_score": 0.70, "reliability": "MEDIUM", "specialty": "experimentation"},
    "05": {"trust_score": 0.90, "reliability": "VERY_HIGH", "specialty": "analysis"}
  }
}
```

**2. Information Sharing:**
```
Agenci moga dzielic sie informacjami (nie strategiami!):
- Wy detected patterns
- Zmiany w srodowisku
- Ostrzezenia o ryzyku
- Sukcesy pewnych typow decyzji
```

**3. Social Learning:**
```
Agent 01 obserwuje:
- Agent 05 osiaga 90% skutecznosc z strategia X
- Agent 02 traci przy wysokim ryzyku

Agent 01 wyciaga wnioski:
- "Wysokie ryzyko moze byc niebezpieczne"
- "Strategia X wart testow"

Agent 01 dziala:
- Tworzy wlasna wersje strategii X (exp_strategy_03)
- Testuje przy niskim ryzyku
- Ocenia wyniki
```

### 6.2. Roznice Miedzy Agentami

| Agent | Osobowosc | Style Decyzyjne | Mocne Strony | Slabe Strony |
|-------|-----------|-----------------|--------------|--------------|
| 01 | Analityk | Ostroczny, metodyczny | Dokladnosc, stabilnosc | Wolne decyzje, mała eksploracja |
| 02 | Strateg W. | Odwazny, optymistyczny | Wysokie zyski | Wysokie ryzyko, przerost pewnosci |
| 03 | Eksperymentator | Kreatywny, innowacyjny | Nowe strategie, odkrycia | Niestabilnosc, nieregularnosc |
| 04 | Balansowy | Zrownowazony | Stala wydajnosc | Brak specjalizacji |
| 05 | Konserwatysta | Bezpieczny, ostrozny | Minimalne straty | Małe zyski |
| 06 | Agresor | Wysokie ryzyko | Duze zyski | Duze straty |

### 6.3. System Zaufania

**Trust Score** jest obliczany na podstawie:
- **Reliability:** Czy agent dotrzymuje obietnic
- **Accuracy:** Czy predykcje agenta sa trafne
- **Consistency:** Czy zachowanie jest stabilne
- **Transparency:** Czy agent dzieli sie informacjami

**Wpływ Trust Score:**
- Wysoki trust: Wieksza waga decyzji agenta w Decision Engine
- Niski trust: Mniejsza waga, wiecej walidacji
- Zero trust: Decyzje agenta sa ignorowane

---

## 7. INTEGRACJA Z INNYMI SYSTEMAMI

### 7.1. Integracja z Strategy Laboratory

**Proces Pomysl -> Test -> Ocena -> Ranking -> Akceptacja** jest scisle zwiazany z pamiecia agenta:

```
Agent Memory → Strategy Laboratory
├── Inspiracja do nowych strategii
├── Historia strategii (sukcesy/porazki)
├── Ranking strategii
└── Parametry strategii

Strategy Laboratory → Agent Memory
├── Nowe strategie do testow
├── Wyniki testow
├── Awans strategii
└── wycofaniem strategii
```

**Kazdy agent ma:**
- Wlasne **Production Strategies** (uzywane w produkcji)
- Wlasne **Experimental Strategies** (testowane)
- Wlasny **Ranking** i preferencje
- Wlasna **Historia testow**

### 7.2. Integracja z Memory Evolution System

**Cykl Pamieci:**
```
DOSWIADCZENIE → PAMIEC SUROWA → DOJRZEWANIE → OBSERWACJA → OCENA → RANKING → STRATEGIA → SLAD DOSWIADCZENIA
```

**Stany Pamieci:**
```
NOWA → DOJRZEWAJACA → OBSERWOWANA → ANALIZOWANA → AKTYWNA → ARCHIWALNA
```

**Agent Memory zapewnia:**
- **Doświadczenia:** Surowa pamiec z kazdego cyklu
- **Analiza:** Przetwarzanie i kategoryzacja
- **Ewolucja:** Zmiana zachowania na podstawie nauki

### 7.3. Integracja z Decision Engine

**Wplyw Pamieci na Decyzje:**
```
Agent Memory → Decision Making
├── Personality vector → Decyzje zwiazane z charakterem
├── Strategy ranking → Wybor strategii
├── Decision history → Kontekst historyczny
├── Trust memory → Waga decyzji innych agentow
└── Behavior patterns → Typowe wzorce

Decision → Memory Update
├── Sukces/Porazka → Ewolucja osobowosci
├── Decyzja → Historia decyzji
└── Wynik → Katalog wynikow
```

### 7.4. Integracja z Information Flow Controller

**Sygnaly zwiazane z pamiecia:**
- MEMORY_UPDATE: Aktualizacja pamieci
- AGENT_LEARNING: Nowa wiedza zdobyta
- PERSONALITY_EVOLUTION: Zmiana osobowosci
- STRATEGY_RANKING_UPDATE: Aktualizacja rankingu

---

## 8. PRIORYTETY I OGRANICZENIA

### 8.1. Ograniczenia Pamieci

**Rozmiar:**
- Kazdy typ pamieci: max 1MB
- Calkowita pamiec agenta: max 5MB
- Kompresja: enabled (JSON compression)

**Retention Policy:**
- Experience Trace: NIGDY nie usuwany
- Decision History: Ostatnie 1000 decyzji
- Prediction History: Ostatnie 5000 predykcji
- Cycle History: Ostatnie 1000 cykli

### 8.2. Priorytety Przetwarzania

**Kolejnosc aktualizacji pamieci:**
1. PERSONALITY (tylko przy ewolucji)
2. BEHAVIOR (kazdy cykl)
3. STRATEGY (kazdy cykl)
4. HISTORY (kazdy cykl)

### 8.3. Zgodnosc z Ograniczeniem Sprzetowym

**Tylko 1 aktywny model LLM na raz:**
- Pamiec jest ladowana/zapisywana sekwencyjnie
- Kazdy agent czeka na swoja kolej
- Orchestrator zarzadza kolejka (MODEL START -> WORK -> SAVE MEMORY -> MODEL STOP)

---

## 9. TESTOWANIE I WALIDACJA

### 9.1. Test Cases

| ID | Scenariusz | Spodziewany Wynik | Status |
|----|-----------|-------------------|--------|
| AMB-001 | Laczenie pamieci | 4 pliki JSON zaladowane | ✅ |
| AMB-002 | Zapis pamieci | 4 pliki JSON zapisane | ✅ |
| AMB-003 | Ewolucja osobowosci po sukcesie | Zwiekszenie confidence | ✅ |
| AMB-004 | Ewolucja osobowosci po porazce | Zwiekszenie caution | ✅ |
| AMB-005 | Ranking strategii | Strategie posortowane wedlug score | ✅ |
| AMB-006 | Tworzenie nowej strategii | Nowy wpis w experimental_strategies | ✅ |
| AMB-007 | Awans strategii | Przeniesienie z experimental do production | ✅ |
| AMB-008 | Historia sukcesow | Wszystkie sukcesy zapamietane | ✅ |
| AMB-009 | Historia bledow | Wszystkie bledy zapamietane | ✅ |
| AMB-010 | Krzywe uczenia | Postep widoczny w learning_curves | ✅ |

### 9.2. Validation Rules

- [ ] Kazdy typ pamieci ma poprawny format JSON
- [ ] Wszystkie pola obowiazkowe sa obecne
- [ ] personality_vector ma wartosci w [0, 1]
- [ ] ranking strategii jest spojny (suma preference = 1)
- [ ] Historia jest chronologiczna
- [ ] Statystyki sa poprawne

---

## 10. PODSUMOWANIE

**Agent Memory & Behavior Evolution** zapewnia:

1. ** individuelle Pamiec** kazdego agenta (4 typy: PERSONALITY, BEHAVIOR, STRATEGY, HISTORY)
2. **Wlasne Predykcje** i katalog wynikow
3. **Wlasny Ranking Strategii** (azdo 6 agentow ma inny ranking)
4. **Historie Sukcesow i Bledow** z pelna nauka
5. **Zmiane Zachowania w Czasie** (ewolucja osobowosci)

**ZASADA FUNDAMENTALNA:** Pamięć wpływa na zachowanie agenta.

**Kazdy agent:**
- Uczy sie na wlasnych doswiadczeniach
- Analizuje wzorce i tworzy wlasne strategie
- NIE kopiuje strategii innych agentow
- Moze analizowac innych i tworzc wlasne ulepszenia
- Ewoluuje w unikalny sposob

**Pamięć jest:**
- Prywatna (indywidualna dla kazdego agenta)
- Trwala (zachowywana miedzy cyklami)
- Wpływowa (zmienia zachowanie)
- Monitorowana (statystyki, historia)

---

**Data utworzenia:** 2026-08-01  
**Wersja:** 1.0.0  
**Status:** DRAFT - Gotowy do przegladu  
**Autor:** Mistral Vibe - CLI Coding Agent  
**Nastepny dokument:** 05_STRATEGY_LABORATORY_ARCHITECTURE.md  

---

**Powiazane Dokumenty:**
- SSI_V5_MASTER_SYSTEM_FLOW_ARCHITECTURE.md
- 01_SYSTEM_SIGNAL_ARCHITECTURE.md
- 02_DEVELOPER_INPUT_ARCHITECTURE.md
- 03_PROMPT_MANAGEMENT_SYSTEM.md
- 05_STRATEGY_LABORATORY_ARCHITECTURE.md (nastepny)
- SSI/v5/agents/agent_memory_store.py
