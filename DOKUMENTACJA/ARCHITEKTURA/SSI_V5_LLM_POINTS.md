# SSI V5 - MIJSCA NA MODELE JĘZYKOWE

**Data:** 2026-08-01  
**Sprint:** 15 (Planowanie)  
**Status:** Dokumentacja projektowa - Wersja 1.0.0  
**Autor:** Główny Architekt SSI V5  

---

## 📋 SPIS TREŚCI

1. [LLM Layer - Planowana Lokalizacja](#1-llm-layer---planowana-lokalizacja)
2. [Integracja z Istniejącym Systemem](#2-integracja-z-istniejącym-systemem)
3. [Interfejs Programisty z LLM](#3-interfejs-programisty-z-llm)
4. [Pamięć Warstwy LLM](#4-pamięć-warstwy-llm)

---

## 1. LLM LAYER - PLANANA LOKALIZACJA

### 1.1. Struktura Katalogów (Sprint 15)

```
SSI/
└── v5/
    └── llm/                          # 🟡 SPRINT 15 - LLM Integration Layer
        ├── llm_client.py              # Klient API do modeli LLM ✅
        ├── llm_decision_layer.py      # Analiza decyzji agentów przez LLM ✅
        ├── prompt_builder.py          # Budowanie i zarządzanie promptami ✅
        ├── llm_config.py              # Konfiguracja połączeń z LLM ✅
        ├── llm_analytics.py           # Metryki i analiza użycia LLM 🟡
        └── llm_errors.py              # Obsługa błędów LLM 🟡
```

### 1.2. Pliki i Odpowiedzialności

| **Plik** | **Odpowiedzialność** | **Status** | **Sprint** |
|----------|----------------------|------------|------------|
| llm_client.py | Klient API modeli LLM (OpenAI, Claude, lokalne) | 🟡 Planowany | 15 |
| llm_decision_layer.py | Analiza decyzji agentów przez LLM | 🟡 Planowany | 15 |
| prompt_builder.py | Budowanie i zarządzanie promptami | 🟡 Planowany | 15 |
| llm_config.py | Konfiguracja połączeń z LLM | 🟡 Planowany | 15 |
| llm_analytics.py | Metryki i analiza użycia LLM | 🟡 Planowany | 15 |
| llm_errors.py | Obsługa błędów i retry logic | 🟡 Planowany | 15 |

---

## 2. INTEGRACJA Z ISTNIEJĄCYM SYSTEMEM

### 2.1. Diagram Integracji LLM

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LLM INTEGRATION POINTS                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PRZEPŁYW Z LLM:                                                           │
│                                                                             │
│  ┌─────────────────────┐       ┌─────────────────────────┐                │
│  │   AgentRuntime      │       │   LLMDecisionLayer      │                │
│  │   agent_runtime.py  │──────►│   llm_decision_layer.py  │                │
│  │                     │       │                         │                │
│  │  run_cycle()         │       │   analyze_decision()    │                │
│  │  _make_decision()    │──────►│   - decision_quality    │                │
│  │  _analyze_data()     │──────►│   - argument_strength   │                │
│  │                     │       │   - potential_errors    │                │
│  └─────────────────────┘       │   - recommendations      │                │
│                           ←──────┘                         │                │
│                                  *.calibrated_confidence    │                │
│                                  *.suggested_actions         │                │
│                                                                             │
│  ┌─────────────────────┐       ┌─────────────────────────┐                │
│  │   PromptBuilder     │       │   Memory Integration     │                │
│  │   prompt_builder.py │──────►│   agent_memory_store.py  │                │
│  │                     │       │                         │                │
│  │   build_prompt()     │──────►│   Insights saved to:     │                │
│  │   - system prompts   │       │   - behavior.json       │                │
│  │   - decision prompts │       │   - history.json        │                │
│  │   - analysis prompts │       │   - prompt.json (FUTURE)│                │
│  └─────────────────────┘       └─────────────────────────┘                │
│                                                                             │
│  ┌─────────────────────┐       ┌─────────────────────────┐                │
│  │   LLMClient         │       │   Collective Memory      │                │
│  │   llm_client.py     │──────►│   collective_memory.py   │                │
│  │                     │       │                         │                │
│  │   send_request()    │──────►│   context retrieving      │                │
│  │   - OpenAI API      │       │   for LLM analysis       │                │
│  │   - Claude API      │       │                         │                │
│  │   - Local Models    │       └─────────────────────────┘                │
│  └─────────────────────┘                                                              │
│                                                                             │
│  DOSTĘPNE MODELE:                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │ LLMClient (llm_client.py)                                          │        │
│  │  ├─ OpenAI API                                                      │        │
│  │  │   └─ models: gpt-4, gpt-3.5-turbo, etc.                        │        │
│  │  ├─ Claude API                                                     │        │
│  │  │   └─ models: claude-3-haiku, claude-3-sonnet, etc.             │        │
│  │  ├─ Local Models (GGUF, etc.)                                      │        │
│  │  │   └─ models: llama2, mistral, phi2, etc.                         │        │
│  │  └─ Fallback Strategy (offline mode)                              │        │
│  │                                                                   │        │
│  │  METRICS:                                                          │        │
│  │  ├─ Token Usage Tracking   - Monitorowanie zużycia tokenów        │        │
│  │  ├─ Response Time Monitoring - Czas odpowiedzi                     │        │
│  │  ├─ Rate Limiting            - Ograniczenia szybkości zapytań      │        │
│  │  └─ Error Handling & Retry  - Obsługa błędów i ponowienia        │        │
│  └─────────────────────────────────────────────────────────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2. Punkty Integracji z Runtime

#### Integracja z AgentRuntime

```python
# agent_runtime.py - _make_decision() z LLM

def _make_decision(self, analysis: AnalysisResult) -> Decision:
    # 1. Podjęcie decyzji przez agenta (standardowo)
    decision = self._make_standard_decision(analysis)
    
    # 2. Opcjonalna analiza przez LLM (jeśli włączone)
    if FEATURE_FLAGS["ENABLE_LLM_ANALYSIS"]:
        llm_analysis = LLMDecisionLayer.analyze_decision(
            agent_id=self.agent_id,
            decision=decision,
            analysis=analysis,
            context=self._get_agent_context()
        )
        
        # 3. Aktualizacja decyzji na podstawie LLM
        decision = self._apply_llm_feedback(decision, llm_analysis)
        
    # 4. Zapis insightów LLM do pamięci
    self._save_llm_insights(llm_analysis)
    
    return decision
```

#### Integracja z CollectorManager

```python
# collector_manager.py - Uwzględnianie danych LLM

def _create_unified_input_package(self) -> dict:
    package = {
        "v2": self.v2_collector.get_latest_data(),
        "v3": self.v3_collector.get_latest_data(),
        "v4": self.v4_collector.get_latest_data(),
        "external": self.external_collector.get_latest_data()
    }
    
    # Opcjonalne dodanie analizy LLM do pakietu
    if FEATURE_FLAGS["ENABLE_LLM_CONTEXT"]:
        package["llm_context"] = LLMDecisionLayer.get_global_context()
    
    return self._add_metadata(package)
```

---

## 3. INTERFEJS PROGRAMISTY Z LLM

### 3.1. Główne Funkcje LLM

| **Funkcja** | **Opis** | **Wejście** | **Wyjście** | **Plik** | **Status** |
|-------------|----------|-------------|-------------|----------|------------|
| analyze_decision | Analiza decyzji agenta | decision, context, agent_memory | llm_analysis, suggestions | llm_decision_layer.py | 🟡 Sprint 15 |
| validate_reasoning | Weryfikacja logiki | reasoning, data | consistency_score, errors | llm_decision_layer.py | 🟡 Sprint 15 |
| generate_alternatives | Alternatywne perspektywy | decision_context | alternative_choices | llm_decision_layer.py | 🟡 Sprint 15 |
| calibrate_confidence | Kalibracja confidence | confidence, data_quality | calibrated_confidence | llm_decision_layer.py | 🟡 Sprint 15 |
| build_decision_prompt | Budowa promptu decyzyjnego | agent_id, context | prompt_string | prompt_builder.py | 🟡 Sprint 15 |
| optimize_prompt | Optymalizacja promptu | prompt, results | optimized_prompt | prompt_builder.py | 🟡 Sprint 15 |
| send_to_llm | Wysyłanie zapytania | prompt, model, params | llm_response | llm_client.py | 🟡 Sprint 15 |

### 3.2. LLMDecisionLayer API

```python
# llm_decision_layer.py

class LLMDecisionLayer:
    """Warstwa analizy decyzji przez modele językowe"""
    
    @staticmethod
    def analyze_decision(agent_id: str, decision: dict, 
                       analysis: dict, context: dict) -> dict:
        """
        Analiza decyzji agenta przez LLM
        
        Args:
            agent_id: ID agenta
            decision: Decyzja agenta (choice, confidence, strategy, reasoning)
            analysis: Analiza agenta (quality_scores, trust_scores, etc.)
            context: Kontekst (world_context, agent_memory, etc.)
        
        Returns:
            dict: Analiza LLM i sugestie
        """
        prompt = PromptBuilder.build_decision_prompt(
            agent_id=agent_id,
            decision=decision,
            analysis=analysis,
            context=context
        )
        
        llm_response = LLMClient.send_request(prompt, model="gpt-4")
        
        return LLMDecisionLayer._parse_llm_response(llm_response)
    
    @staticmethod
    def _parse_llm_response(response: str) -> dict:
        """Parsowanie odpowiedzi LLM do struktury"""
        # Konwersja odpowiedzi tekstowej do strukturyzowanych danych
        return {
            "decision_quality_score": extract_score(response, "quality"),
            "argument_strength": extract_score(response, "argument"),
            "logical_consistency": extract_score(response, "consistency"),
            "alternative_perspectives": extract_list(response, "alternatives"),
            "potential_errors": extract_list(response, "errors"),
            "recommendations": extract_list(response, "recommendations"),
            "confidence_calibration": extract_score(response, "calibration"),
            "suggested_actions": extract_actions(response)
        }
```

### 3.3. PromptBuilder

```python
# prompt_builder.py

class PromptBuilder:
    """Budowanie i zarządzanie promptami dla LLM"""
    
    PROMPT_TEMPLATES = {
        "system": """
        Jesteś asystentem systemu SSI V5 - Self-learning System Intelligence.
        Twoim zadaniem jest analiza decyzji podejmowanych przez agentów.
        
        Zasady:
        1. Oceń jakość decyzji obiektywnie
        2. Zidentyfikuj potencjalne błędy w rozumowaniu
        3. Zaproponuj konkretne ulepszenia
        4. Użyj formatu JSON dla odpowiedzi
        """,
        
        "decision_analysis": """
        Analizuj następującą decyzję agenta:
        
        Agent: {agent_id}
        Typ osobowości: {personality_type}
        Decyzja: {choice}
        Pewność: {confidence}
        Strategia: {strategy}
        Uzasadnienie: {reasoning}
        
        Kontekst:
        Düne światowe: {world_context}
        Analiza: {analysis}
        Historia agenta: {history}
        
        Oceń (1-10):
        - Jakość decyzji:
        - Siła argumentacji:
        - Spójność logiczna:
        
        Zidentyfikuj:
        - Potencjalne błędy:
        - Alternatywne perspektywy:
        - Sugestie ulepszeń:
        """,
        
        "calibration": """
        Skalibruj pewność decyzji na podstawie:
        - Jakości danych: {data_quality}
        - Spójności analizy: {analysis_consistency}
        - Historia agenta: {agent_history}
        
        Czy confidence {original_confidence} jest:
        - Zbyt wysoki?
        - Zbyt niski?
        - Odpowiedni?
        
        Zaproponuj skorygowaną wartość (0.0-1.0):
        """
    }
    
    @staticmethod
    def build_decision_prompt(agent_id: str, decision: dict, 
                             analysis: dict, context: dict) -> str:
        """Buduje prompt do analizy decyzji"""
        template = PromptBuilder.PROMPT_TEMPLATES["decision_analysis"]
        return template.format(
            agent_id=agent_id,
            personality_type=context.get("personality_type", "unknown"),
            choice=decision.get("choice", ""),
            confidence=decision.get("confidence", 0),
            strategy=decision.get("strategy", ""),
            reasoning=decision.get("reasoning", ""),
            world_context=context.get("world_context", {}),
            analysis=analysis,
            history=context.get("agent_history", {})
        )
    
    @staticmethod
    def build_system_prompt() -> str:
        """Buduje systemowy prompt"""
        return PromptBuilder.PROMPT_TEMPLATES["system"]
    
    @staticmethod
    def optimize_prompt(prompt: str, results: list) -> str:
        """Optymalizuje prompt na podstawie historii wyników"""
        # Analiza jakie prompty dają najlepsze wyniki
        # i dostosowanie nowego promptu
        return optimized_prompt
```

### 3.4. LLMClient

```python
# llm_client.py

class LLMClient:
    """Klient API dla różnych modeli językowych"""
    
    SUPPORTED_MODELS = {
        "openai": ["gpt-4", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"],
        "anthropic": ["claude-3-haiku", "claude-3-sonnet", "claude-3-opus", "claude-2"],
        "local": ["llama2-7b", "mistral-7b", "phi2"]
    }
    
    # Konfiguracja połączeń
    API_CONFIG = {
        "openai": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "base_url": "https://api.openai.com/v1",
            "timeout": 60,
            "max_retries": 3
        },
        "anthropic": {
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "base_url": "https://api.anthropic.com",
            "timeout": 120,
            "max_retries": 3
        },
        "local": {
            "base_url": "http://localhost:8000",
            "timeout": 300,
            "max_retries": 2
        }
    }
    
    @staticmethod
    def send_request(prompt: str, model: str = "gpt-4", 
                   provider: str = "openai", **params) -> str:
        """
        Wysyła zapytanie do modelu językowego
        
        Args:
            prompt: Treść promptu
            model: Model do użycia
            provider: Dostawca (openai, anthropic, local)
            params: Dodatkowe parametry (temperature, max_tokens, etc.)
        
        Returns:
            str: Odpowiedź modelu
        """
        if not LLMConfig.is_enabled():
            return LLMClient._get_fallback_response(prompt)
        
        try:
            client = LLMClient._get_client(provider)
            response = client.create_completion(
                model=model,
                prompt=prompt,
                **params
            )
            
            LLMAnalytics.track_usage(
                model=model,
                provider=provider,
                tokens_input=response.usage.prompt_tokens,
                tokens_output=response.usage.completion_tokens,
                response_time=response.response_time
            )
            
            return response.choices[0].text
            
        except Exception as e:
            LLMErrors.handle_error(e, model, provider, params)
            return LLMClient._get_fallback_response(prompt)
    
    @staticmethod
    def _get_fallback_response(prompt: str) -> str:
        """Zwieraca domyślną odpowiedź w przypadku awarii LLM"""
        # Prosta analiza oparte na regułach
        return FallbackAnalyzer.analyze(prompt)
```

### 3.5. LLMConfig

```python
# llm_config.py

class LLMConfig:
    """Konfiguracja warstwy LLM"""
    
    @staticmethod
    def is_enabled() -> bool:
        """Sprawdza czy LLM jest włączone"""
        return FEATURE_FLAGS.get("ENABLE_LLM_ANALYSIS", False)
    
    @staticmethod
    def get_default_model() -> str:
        """Zwraca domyślny model"""
        return os.getenv("LLM_DEFAULT_MODEL", "gpt-4")
    
    @staticmethod
    def get_default_provider() -> str:
        """Zwraca domyślnego dostawcę"""
        return os.getenv("LLM_DEFAULT_PROVIDER", "openai")
    
    @staticmethod
    def get_settings() -> dict:
        """Zwraca wszystkie ustawienia LLM"""
        return {
            "enabled": LLMConfig.is_enabled(),
            "default_model": LLMConfig.get_default_model(),
            "default_provider": LLMConfig.get_default_provider(),
            "temperature": float(os.getenv("LLM_TEMPERATURE", "0.7")),
            "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "2000")),
            "timeout": int(os.getenv("LLM_TIMEOUT", "60")),
            "rate_limit": int(os.getenv("LLM_RATE_LIMIT", "60")),  # requests/min
            "cache_enabled": os.getenv("LLM_CACHE_ENABLED", "true").lower() == "true"
        }
    
    @staticmethod
    def get_provider_config(provider: str) -> dict:
        """Zwraca konfigurację dla dostawcy"""
        return LLMClient.API_CONFIG.get(provider, {})
```

---

## 4. PAMIĘĆ WARSTWY LLM

### 4.1. Struktura Pamięci LLM

```
SSI/memory/language_model/          # 🟡 SPRINT 15
├── agent_context/
│   ├── agent_01_context.json       # Indywidualny kontekst
│   ├── agent_02_context.json
│   ├── agent_03_context.json
│   ├── agent_04_context.json
│   ├── agent_05_context.json
│   └── agent_06_context.json
├── collective_context/
│   └── team_context.json           # Zespołowy kontekst
└── prompt_memory/
    ├── system_prompts.json         # Prompty systemowe
    ├── decision_prompts.json        # Prompty decyzyjne
    ├── analysis_prompts.json        # Prompty analityczne
    └── response_history.json        # Historia odpowiedzi
```

### 4.2. Zawartość Plików Pamięci

#### agent_XX_context.json

```json
{
  "agent_id": "01",
  "last_updated": "2026-08-01T12:00:00",
  "context_type": "decision_support",
  "recent_decisions": [
    {
      "decision_id": "dec_01_20260801120000",
      "decision": {"choice": "high_confidence", "confidence": 0.87},
      "llm_analysis": {
        "quality_score": 0.92,
        "suggestions": ["Consider V2 data more"],
        "warnings": ["Low confidence in external data"]
      },
      "timestamp": "2026-08-01T12:00:00"
    }
  ],
  "preferences": {
    "preferred_strategy": "analytical",
    "trusted_sources": ["v2", "v3"],
    "risk_tolerance": "medium"
  },
  "llm_interaction_history": [
    {
      "interaction_id": "llm_001",
      "prompt_type": "decision_analysis",
      "model_used": "gpt-4",
      "tokens_used": 543,
      "response_time_ms": 2345,
      "timestamp": "2026-08-01T12:00:00"
    }
  ]
}
```

#### team_context.json

```json
{
  "team_id": "SSI_V5",
  "last_updated": "2026-08-01T12:00:00",
  "agents_overview": {
    "01": {"role": "analyst", "specialization": "data_analysis"},
    "02": {"role": "creator", "specialization": "strategy_development"},
    "03": {"role": "guardian", "specialization": "risk_management"},
    "04": {"role": "explorer", "specialization": "new_opportunities"},
    "05": {"role": "mediator", "specialization": "conflict_resolution"},
    "06": {"role": "coordinator", "specialization": "team_synergy"}
  },
  "team_strengths": [
    "High data analysis accuracy",
    "Good risk management",
    "Creative strategy development"
  ],
  "team_weaknesses": [
    "Limited external data trust",
    "Occasional overconfidence"
  ],
  "recent_collaborations": [
    {
      "collaboration_id": "coll_001",
      "agents_involved": ["01", "02", "05"],
      "topic": "Market trend analysis",
      "outcome": "success",
      "llm_contribution": "Identified additional data sources",
      "timestamp": "2026-08-01T11:30:00"
    }
  ]
}
```

#### system_prompts.json

```json
{
  "version": "1.0",
  "last_updated": "2026-08-01T12:00:00",
  "prompts": {
    "system": {
      "id": "prompt_system_v1",
      "content": "Jesteś asystentem systemu SSI V5...",
      "version": "1.0",
      "created_at": "2026-08-01T12:00:00",
      "usage_count": 150,
      "performance_score": 0.87,
      "last_used": "2026-08-01T12:00:00"
    },
    "decision_analysis": {
      "id": "prompt_decision_v1",
      "content": "Analizuj następującą decyzję agenta...",
      "version": "1.1",
      "created_at": "2026-08-01T12:00:00",
      "usage_count": 45,
      "performance_score": 0.92,
      "last_used": "2026-08-01T12:00:00",
      "optimization_notes": ["Added more context fields"]
    },
    "alternatives_generation": {
      "id": "prompt_alternatives_v1",
      "content": "Wygeneruj alternatywne perspektywy...",
      "version": "1.0",
      "created_at": "2026-08-01T12:00:00",
      "usage_count": 12,
      "performance_score": 0.85,
      "last_used": "2026-08-01T11:30:00"
    }
  },
  "statistics": {
    "total_prompts": 3,
    "total_usage": 207,
    "average_performance": 0.88,
    "most_used": "prompt_system_v1",
    "best_performing": "prompt_decision_v1"
  }
}
```

#### response_history.json

```json
{
  "version": "1.0",
  "responses": [
    {
      "response_id": "resp_001",
      "prompt_id": "prompt_decision_v1",
      "model": "gpt-4",
      "provider": "openai",
      "agent_id": "01",
      "decision_id": "dec_01_20260801120000",
      "input_tokens": 456,
      "output_tokens": 321,
      "total_tokens": 777,
      "response_time_ms": 2345,
      "cost": 0.00234,
      "timestamp": "2026-08-01T12:00:00",
      "quality_score": 0.92,
      "relevance_score": 0.88,
      "error_occurred": false,
      "notes": "Good analysis with actionable suggestions"
    },
    {
      "response_id": "resp_002",
      "prompt_id": "prompt_decision_v1",
      "model": "gpt-4",
      "provider": "openai",
      "agent_id": "02",
      "decision_id": "dec_02_20260801120000",
      "input_tokens": 512,
      "output_tokens": 289,
      "total_tokens": 801,
      "response_time_ms": 2100,
      "cost": 0.00245,
      "timestamp": "2026-08-01T12:00:00",
      "quality_score": 0.85,
      "relevance_score": 0.90,
      "error_occurred": false,
      "notes": "Identified logical inconsistency in reasoning"
    }
  ],
  "statistics": {
    "total_responses": 2,
    "total_tokens_used": 1578,
    "total_cost": 0.00479,
    "average_response_time_ms": 2222.5,
    "average_quality": 0.885,
    "models_used": {"gpt-4": 2},
    "providers_used": {"openai": 2},
    "errors_count": 0
  }
}
```

---

**Data utworzenia:** 2026-08-01  
**Wersja:** 1.0.0  
**Status:** Gotowy do przeglądu