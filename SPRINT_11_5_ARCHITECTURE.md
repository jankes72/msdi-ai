# SSI V5 - Sprint 11.5 Architecture

**Sprint Name:** Runtime Foundation + Agent Runtime Loop  
**Version:** 2.0 (ARCHITECTURAL CORRECTION)  
**Date:** 2026-07-31  
**Status:** IN PROGRESS  
**Author:** MSDI AI / SSI System

---

## 📋 Executive Summary

**ARCHITECTURAL DECISION:**
> SSI Runtime został zmieniony z pojedynczego wykonania na **ciągły cykl agentowy** z wielokrotnym wykonywaniem agentów podczas jednego uruchomienia systemu.

**Previous Approach (INCORRECT):**
```
START -> Data Collection -> Single Agent Pass -> STOP
```

**New Approach (CORRECT):**
```
START -> Runtime Controller -> CONTINUOUS LOOP (up to 5 hours) -> STOP
                     ↓
       while runtime_active:
         ↓
         Load Current World Context
         ↓
         Run Agent_01 → Save Experience → Update Memory
         Run Agent_02 → Save Experience → Update Memory
         Run Agent_03 → Save Experience → Update Memory
         Run Agent_04 → Save Experience → Update Memory
         Run Agent_05 → Save Experience → Update Memory
         Run Agent_06 → Save Experience → Update Memory
         ↓
         Update Shared Memory
         Begin Next Cycle
         ↓
       (repeat until time limit reached)
```

---

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    SSI V5 - RUNTIME SYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    RUNTIME CONTROLLER                           │ │
│  │  (SSI/v5/runtime/runtime_controller.py)                        │ │
│  │                                                                 │ │
│  │  Functions: initialize(), start_cycle(), run_loop(),          │ │
│  │              save_state(), load_previous_state(), shutdown()  │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                ↓                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    SCHEDULER                                   │ │
│  │  (SSI/v5/runtime/scheduler.py)                                │ │
│  │                                                                 │ │
│  │  Manage task execution, timing, priorities                      │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                ↓                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    STATE MANAGER                               │ │
│  │  (SSI/v5/runtime/state_manager.py)                           │ │
│  │                                                                 │ │
│  │  RuntimeState, AgentState, MemoryState, CollectorState        │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                ↓                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 AGENT MANAGER                                  │ │
│  │  (SSI/v5/agents/agent_manager.py)                            │ │
│  │                                                                 │ │
│  │  Create, coordinate, and manage all 6 agents                  │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                ↓                                    │
│  ┌─────────────────────┐  ┌─────────────────────┐              │ │
│  │    Agent_01         │  │    Agent_02         │              │ │
│  │  (Individual)        │  │  (Individual)        │              │ │
│  └─────────────────────┘  └─────────────────────┘              │ │
│  ┌─────────────────────┐  ┌─────────────────────┐              │ │
│  │    Agent_03         │  │    Agent_04         │              │ │
│  └─────────────────────┘  └─────────────────────┘              │ │
│  ┌─────────────────────┐  ┌─────────────────────┐              │ │
│  │    Agent_05         │  │    Agent_06         │              │ │
│  └─────────────────────┘  └─────────────────────┘              │ │
│                                                                     │
│  Each Agent has:                                                   │
│  - own personality (personality.json)                           │
│  - own behavior history (behavior.json)                        │
│  - own strategies (strategy.json)                               │
│  - own history (history.json)                                    │
│  - own relationships (relationship.json)                        │
│  - own prompt memory (prompt_memory.json)                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT LAYER (Sprint 11.4)                       │
├─────────────────────────────────────────────────────────────────┤
│  V2DataCollector │ V3KnowledgeCollector │ V4AgentsCollector     │
│  ExternalKnowledgeCollector                                       │
│                     ↓                                              │
│              UnifiedInputPackage ════════════►                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Runtime Loop - Core Architecture

### Main Loop Pattern

```python
# In SSI/v5/runtime/runtime_controller.py

def run_loop(self) -> None:
    """Main runtime loop - runs for up to cycle_duration_hours"""
    
    self._running = True
    self._shutdown_requested = False
    
    # Set start time
    start_time = time.time()
    end_time = start_time + (self.config.cycle_duration_hours * 3600)
    
    self.logger.info(f"Starting SSI Runtime Loop (max {self.config.cycle_duration_hours}h)")
    self.state_manager.start_cycle()
    
    # ↓↓↓ MAIN CONTINUOUS LOOP ↓↓↓
    while (time.time() < end_time and 
           self._running and 
           not self._shutdown_requested):
        
        # Get current world context
        world_context = self._get_current_context()
        
        # Run EACH agent in sequence
        for agent_id, agent in self.agents.items():
            if not self._running or self._shutdown_requested:
                break
                
            # ↓↓↓ SINGLE AGENT CYCLE ↓↓↓
            self._run_single_agent_cycle(agent, world_context)
            
            # Update shared memory
            self._update_shared_memory()
        
        # Increment cycle counter
        self.state_manager.end_cycle()
        self.state_manager.start_cycle()
        
        # Optional: Save state periodically
        if self.config.auto_save and self._should_save_state():
            self.save_state()
            
    # Loop ended - final save
    self._finalize_runtime_loop()
```

### Single Agent Cycle

```python
# In SSI/v5/agents/agent_runtime.py

class AgentRuntime:
    def run_cycle(self, world_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute single agent cycle"""
        
        # Step 1: Load memory
        self._load_memory()
        
        # Step 2: Fetch data from all collectors
        input_data = self._fetch_collector_data(world_context)
        
        # Step 3: Compare old knowledge vs new data
        analysis_result = self._analyze_data(input_data)
        
        # Step 4: Make decision
        decision = self._make_decision(analysis_result)
        
        # Step 5: Record experience
        self._save_experience(decision, analysis_result)
        
        # Step 6: Update history
        self._update_historydecision)
        
        return {
            "agent_id": self.agent_id,
            "decision": decision,
            "experience_saved": True,
            "memory_updated": True
        }
```

---

## 🧠 Agent Architecture

### Agent Structure

```
SSI/v5/agents/
├── __init__.py
├── agents_config.py          # Agent configuration classes
├── agent_state.py           # Agent state management
├── agent_runtime.py         # Agent execution engine
├── agent_manager.py         # Central agent coordinator
├── agent_memory_manager.py  # Memory management
├── agent_memory_store.py    # Memory storage
└── prompt_memory_builder.py # LLM context builder

SSI/memory/agents/
├── agent_01/
│   ├── personality.json
│   ├── behavior.json
│   ├── strategy.json
│   ├── history.json
│   ├── relationship.json
│   └── prompt_memory.json
├── agent_02/
│   ├── ...
├── agent_03/
│   ├── ...
├── agent_04/
│   ├── ...
├── agent_05/
│   ├── ...
└── agent_06/
    ├── ...
```

### Agent Components

#### 1. **Personality Memory** (`personality.json`)
```json
{
  "initial_weights": {
    "risk": 0.5,
    "analysis": 0.8,
    "creativity": 0.5,
    "trust_v2": 0.8,
    "trust_v3": 0.8,
    "trust_v4": 0.8,
    "trust_external": 0.6
  },
  "traits": {
    "risk_tolerance": 0.5,
    "analysis_depth": 0.7,
    "creativity_level": 0.5,
    "patience": 0.6
  },
  "priorities": ["accuracy", "verification", "balance"],
  "agent_type": "balanced",
  "updated_at": "2026-07-31T00:00:00",
  "version": "1.0.0"
}
```

#### 2. **Behavior Memory** (`behavior.json`)
```json
{
  "decisions": [
    {
      "decision_id": "dec_001",
      "timestamp": "2026-07-31T00:00:00",
      "decision_type": "prediction",
      "choice": "win",
      "confidence": 0.85,
      "success": true,
      "strategy_used": "analytical",
      "used_sources": ["v2", "v3"],
      "outcome": {"correct": true, "value": 1.0},
      "evaluation": 0.9
    }
  ],
  "behaviors": [
    {
      "behavior_id": "beh_001",
      "behavior_type": "data_analysis",
      "action": "compare_v2_v3",
      "effectiveness": 0.8,
      "success_rate": 0.75,
      "errors": [],
      "corrections": []
    }
  ],
  "statistics": {
    "total_decisions": 10,
    "successful_decisions": 8,
    "avg_confidence": 0.75,
    "avg_effectiveness": 0.8
  }
}
```

#### 3. **Strategy Memory** (`strategy.json`)
```json
{
  "current_strategy": "analytical",
  "available_strategies": [
    {
      "name": "analytical",
      "type": "analytical",
      "times_used": 15,
      "times_successful": 12,
      "success_rate": 0.8,
      "avg_confidence": 0.75,
      "contexts": ["high_certainty", "verified_data"]
    },
    {
      "name": "conservative",
      "type": "conservative", 
      "times_used": 8,
      "times_successful": 7,
      "success_rate": 0.875,
      "avg_confidence": 0.65,
      "contexts": ["high_risk", "low_certainty"]
    }
  ]
}
```

#### 4. **History Memory** (`history.json`)
```json
{
  "entries": [
    {
      "entry_id": "hist_001",
      "timestamp": "2026-07-31T00:00:00",
      "event_type": "decision_made",
      "description": "Predicted match outcome",
      "categories": ["prediction", "success"],
      "related_decision_id": "dec_001",
      "outcome": {"correct": true, "profits": 2.5},
      "evaluation": 0.9
    }
  ],
  "statistics": {
    "total_entries": 50,
    "categories_distribution": {
      "prediction": 30,
      "analysis": 15,
      "error": 5
    }
  }
}
```

#### 5. **Relationship Memory** (`relationship.json`)
```json
{
  "agents": [
    {
      "agent_id": "02",
      "relationship_type": "collaboration",
      "trust_score": 0.8,
      "collaboration_score": 0.9,
      "conflict_score": 0.1,
      "interactions": 25,
      "positive_interactions": 22,
      "negative_interactions": 2,
      "neutral_interactions": 1,
      "information_shared": 15,
      "information_received": 18,
      "last_interaction": "2026-07-31T00:00:00",
      "last_interaction_type": "data_exchange"
    }
  ],
  "statistics": {
    "avg_trust_score": 0.75,
    "total_interactions": 150
  }
}
```

#### 6. **Prompt Memory** (`prompt_memory.json`)
```json
{
  "system_prompt": {
    "text": "You are an autonomous analytical agent in the SSI V5 system. Your role is to analyze betting data and make informed decisions based on your personality, experience, and available information.",
    "times_used": 100,
    "last_used": "2026-07-31T00:00:00"
  },
  "context_template": {
    "personality": "You have the following personality: {personality}",
    "history": "Your previous decisions: {history}",
    "strategies": "Your available strategies: {strategies}",
    "errors": "Your previous errors: {errors}",
    "new_data": "New data received: {new_data}"
  },
  "prompt_history": [
    {
      "prompt_id": "prompt_001",
      "prompt_type": "analysis",
      "prompt_text": "Analyze V2 and V3 data...",
      "context": {"v2_data": "...", "v3_data": "..."},
      "response": "After analysis...",
      "quality": 0.9,
      "confidence": 0.85,
      "timestamp": "2026-07-31T00:00:00"
    }
  ]
}
```

---

## 🔄 Agent Workflow (Single Cycle)

```
Agent Cycle for each agent in each runtime loop iteration:

┌─────────────────────────────────────────────────────────────┐
│                    AGENT CYCLE                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. LOAD MEMORY                                              │
│     ↓                                                       │
│     - Load personality.json                                │
│     - Load behavior.json                                   │
│     - Load strategy.json                                    │
│     - Load history.json                                     │
│     - Load relationship.json                                │
│     - Load prompt_memory.json                               │
│                                                             │
│  2. FETCH DATA                                               │
│     ↓                                                       │
│     - Get V2 World data                                     │
│     - Get V3 Knowledge data                                  │
│     - Get V4 Agents data                                     │
│     - Get External Input data                                │
│     - Create UnifiedInputPackage view                        │
│                                                             │
│  3. ANALYZE                                                 │
│     ↓                                                       │
│     - Compare OLD knowledge vs NEW data                     │
│     - Identify patterns and anomalies                       │
│     - Evaluate data quality and trust                        │
│     - Analyze previous decisions                             │
│     - Analyze other agents' behavior                         │
│                                                             │
│  4. DECIDE                                                  │
│     ↓                                                       │
│     - Select strategy based on analysis                    │
│     - Make prediction/decision                               │
│     - Calculate confidence level                             │
│     - Generate reasoning                                     │
│     - Record decision in state                               │
│                                                             │
│  5. SAVE EXPERIENCE                                         │
│     ↓                                                       │
│     - Save decision to behavior.json                         │
│     - Update strategy effectiveness in strategy.json       │
│     - Add history entry to history.json                     │
│     - Update weights in personality.json (if needed)        │
│                                                             │
│  6. UPDATE HISTORY                                          │
│     ↓                                                       │
│     - Add new entry to history                               │
│     - Update statistics                                     │
│     - Sync with shared memory (future)                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Prompt Memory Builder

### Purpose
Prepare context for Language Models so they **never start from zero**.

### Input to LLM
```
[SYSTEM ROLE]
You are Agent_01, an autonomous analytical agent in the SSI V5 system.

[PERSONALITY]
- Agent Type: analytical
- Risk Tolerance: 0.3
- Analysis Depth: 0.9  
- Creativity: 0.4
- Trust Levels: V2=0.8, V3=0.8, V4=0.8, External=0.6
- Priorities: accuracy, analysis, verification

[CURRENT WEIGHTS]
- risk: 0.3
- analysis: 0.9
- creativity: 0.4
- trust_v2: 0.8
- trust_v3: 0.8
- trust_v4: 0.8

[HISTORY - Last 5 entries]
1. 2026-07-31T00:00:00 - Predicted match X, Success: Yes, Confidence: 0.85
2. 2026-07-31T01:00:00 - Analyzed pattern Y, Success: Yes, Confidence: 0.90
3. 2026-07-31T02:00:00 - Decision Z, Success: No, Confidence: 0.60
...

[PREVIOUS DECISIONS - Last 3]
- Dec 001: Choice=win, Confidence=0.85, Success=true, Strategy=analytical
- Dec 002: Choice=draw, Confidence=0.70, Success=false, Strategy=balanced
- Dec 003: Choice=loss, Confidence=0.90, Success=true, Strategy=analytical

[PREVIOUS ERRORS - Last 3]
- Err 001: Overestimated probability, Data source: V2, Correction: adjust weight
- Err 002: Incorrect pattern recognition, Strategy: conservative
...

[MY STRATEGIES]
- analytical: Success rate=0.80, Times used=15, Last used=2026-07-31T00:00:00
- conservative: Success rate=0.88, Times used=8, Last used=2026-07-31T01:00:00
- balanced: Success rate=0.75, Times used=10, Last used=2026-07-31T02:00:00

[NEW DATA]
- V2 World: {"pattern": "...", "confidence": 0.95, "timestamp": "..."}
- V3 Knowledge: {"world": "...", "Stability": 0.85, "timestamp": "..."}
- V4 Agents: {"trends": "...", "confidence": 0.90, "timestamp": "..."}
- External Input: {"news": "...", "priority": "high", "timestamp": "..."}

[NOW TELL ME]
Based on your personality, history, strategies, errors, and new data:
1. What pattern do you see?
2. What is your confidence in this data?
3. What decision do you recommend?
4. What strategy should be used?
5. What is your reasoning?

[RESPONSE FORMAT]
- Pattern: [identified pattern]
- Confidence: [0-1]
- Decision: [your choice]
- Strategy: [strategy name]
- Reasoning: [detailed explanation]
- Warnings: [any concerns]
```

### Implementation

```python
# SSI/v5/agents/prompt_memory_builder.py

class PromptMemoryBuilder:
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.prompt_template = self._load_prompt_template()
        
    def build_full_context(self, new_data: Dict[str, Any]) -> str:
        """Build complete context for LLM"""
        
        context_parts = []
        
        # 1. System Role
        context_parts.append(self._build_system_role())
        
        # 2. Personality (who I am)
        context_parts.append(self._build_personality_section())
        
        # 3. Current Weights
        context_parts.append(self._build_weights_section())
        
        # 4. History
        context_parts.append(self._build_history_section())
        
        # 5. Previous Decisions
        context_parts.append(self._build_decisions_section())
        
        # 6. Previous Errors
        context_parts.append(self._build_errors_section())
        
        # 7. My Strategies
        context_parts.append(self._build_strategies_section())
        
        # 8. New Data
        context_parts.append(self._build_new_data_section(new_data))
        
        # 9. Question/Task
        context_parts.append(self._build_task_section())
        
        return "\n\n".join(context_parts)
        
    def build_for_decision(self, decision_context: Dict[str, Any]) -> str:
        """Build specialized prompt for decision making"""
        # Similar structure but focused on decision
        pass
        
    def build_for_analysis(self, analysis_context: Dict[str, Any]) -> str:
        """Build specialized prompt for analysis"""
        # Similar structure but focused on analysis
        pass
```

---

## 📊 Components Summary

### Runtime Module (`SSI/v5/runtime/`)

| File | Purpose | Status |
|------|---------|--------|
| `runtime_controller.py` | Main controller with **continuous loop** | ✅ Created - Needs Update |
| `scheduler.py` | Task scheduling and management | ✅ Created |
| `state_manager.py` | System state management | ✅ Created |
| `runtime_config.py` | Configuration management | ✅ Created |
| `__init__.py` | Module initialization | ✅ Created |

### Agents Module (`SSI/v5/agents/`)

| File | Purpose | Status |
|------|---------|--------|
| `agent_manager.py` | Central agent coordinator | ❌ Missing |
| `agent_runtime.py` | Individual agent execution | ❌ Missing |
| `agent_state.py` | Agent state tracking | ✅ Created |
| `agent_memory_manager.py` | Agent memory coordination | ❌ Missing |
| `agent_memory_store.py` | Agent memory storage | ✅ Created |
| `agents_config.py` | Agent configurations | ✅ Created |
| `prompt_memory_builder.py` | LLM context builder | ❌ Missing |
| `__init__.py` | Module initialization | ❌ Missing |

### Memory Structure (`SSI/memory/agents/`)

| Agent | Files | Status |
|-------|-------|--------|
| agent_01 | 6 JSON files | ✅ Directories exist - Files missing |
| agent_02 | 6 JSON files | ✅ Directories exist - Files missing |
| agent_03 | 6 JSON files | ✅ Directories exist - Files missing |
| agent_04 | 6 JSON files | ✅ Directories exist - Files missing |
| agent_05 | 6 JSON files | ✅ Directories exist - Files missing |
| agent_06 | 6 JSON files | ✅ Directories exist - Files missing |

---

## 🚀 Integration Points

### With Existing Collectors (DO NOT CHANGE)
- ✅ V2 Data Collector - Integrated via UnifiedInputPackage
- ✅ V3 Knowledge Collector - Integrated via UnifiedInputPackage
- ✅ V4 Agents Collector - Integrated via UnifiedInputPackage
- ✅ External Input Layer - Integrated via UnifiedInputPackage

### Data Flow
```
Collector Layer → UnifiedInputPackage → Runtime Controller → Agent Manager → Individual Agents
                                                      ↓
                                                 State Manager ← Memory Updates
```

---

## 📈 Future Architecture (Documentation Only)

### Sprint 11.6: Runtime Queue System
- Task queue with priorities
- Schedule-based execution
- Dependency management between tasks

### Sprint 11.7: Context Memory System
- Contextual memory classification
- Information categorization
- Semantic indexing

### Sprint 11.8: Language Model Context Layer
- Full prompt management
- Context window management
- Response validation

### Sprint 11.9+: AI Orchestrator
- Multi-agent coordination
- Group decision making
- Consensus algorithms

### Sprint 12+: Agent Laboratory System
- Agent experimentation framework
- Strategy testing
- Performance analysis
- Evolution simulation

---

## 📝 Implementation Checklist

### Phase 1: Documentation (Current)
- [ ] Create SPRINT_11_5_ARCHITECTURE.md ✅ **DONE**
- [ ] Update PROJECT_JOURNAL.md with architectural decision
- [ ] Review and approve architecture

### Phase 2: Core Runtime Loop
- [ ] Update runtime_controller.py with continuous loop
- [ ] Create agent_manager.py
- [ ] Create agent_runtime.py
- [ ] Create prompt_memory_builder.py
- [ ] Create agent_memory_manager.py
- [ ] Create agents __init__.py

### Phase 3: Memory Initialization
- [ ] Create default personality.json for all agents
- [ ] Create default behavior.json for all agents
- [ ] Create default strategy.json for all agents
- [ ] Create default history.json for all agents
- [ ] Create default relationship.json for all agents
- [ ] Create default prompt_memory.json for all agents

### Phase 4: Integration
- [ ] Integrate with existing collectors
- [ ] Test unified data flow
- [ ] Verify agent cycles

### Phase 5: Testing
- [ ] Test single agent cycle
- [ ] Test multiple agent cycles
- [ ] Test continuous loop
- [ ] Test memory persistence
- [ ] Test state management

---

## 🎯 Success Criteria

After implementation, the system should output:

```
SSI STARTED

Runtime: ACTIVE

Agents:
✓ Agent_01
✓ Agent_02
✓ Agent_03
✓ Agent_04
✓ Agent_05
✓ Agent_06

Collectors:
✓ V2
✓ V3
✓ V4
✓ External

Memory: ✓ Loaded

-- Runtime Loop Active --

Agent_01: Cycle 1 completed, Decision: X, Confidence: 0.85
Agent_02: Cycle 1 completed, Decision: Y, Confidence: 0.90
Agent_03: Cycle 1 completed, Decision: Z, Confidence: 0.75
...

[After 5 hours]

SSI SHUTDOWN

State saved: runtime_state.json
```

---

**Architectural Correction Version:** 2.0  
**Correction Date:** 2026-07-31  
**Decision:** Changed from single-execution to continuous-agent-loop model  
**Rationale:** Enable multiple agent cycles during single runtime session for genuine autonomous behavior