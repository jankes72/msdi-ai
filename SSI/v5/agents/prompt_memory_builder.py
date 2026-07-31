"""
SSI V5 - Prompt Memory Builder
Budowanie kontekstu dla modeli jezykowych

Zgodnie z dokumentacja Sprint 11.5 v2.0:
- Memory Observation System
- Prompt Memory System

Cel:
Model jezykowy NIGDY nie zaczyna od zera.
Agent otrzymuje:
- Kim jestem
- Jaka jest moja historia
- Jakie mam strategie
- Jakie mialem bledy
- Jakie informacje otrzymalem
- Jakie decyzje podjalem wczeniej
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

# Dodanie sciezki do SSI do sys.path
SSI_PATH = "D:\\sts\\aplikacjaTyperBetAi\\SSI"
if SSI_PATH not in sys.path:
    sys.path.insert(0, SSI_PATH)

from .agents_config import (
    AgentConfig, AgentType, StrategyType, PersonalityTrait
)
from .agent_runtime import AgentRuntime
from .agent_memory_store import AgentMemoryStore, MemoryType


class PromptMemoryBuilder:
    """Builder kontekstu promptow dla modeli jezykowych.
    
    Buduje pelny kontekst dla modelu jezykowego tak,
    zby NIGDY nie zaczynal od zera.
    """
    
    def __init__(self, agent: AgentRuntime):
        """Inicjalizacja buildera z agentem."""
        self.agent = agent
        self.agent_id = agent.agent_id
        
        # Logging
        self.logger = logging.getLogger(f"PromptBuilder_{self.agent_id}")
        
        # Komponenty promptu
        self._components: Dict[str, str] = {}
        
    def build_full_context(self, new_data: Optional[Dict[str, Any]] = None) -> str:
        """Budowanie pelnego kontekstu dla modelu jezykowego.
        
        Komponenty:
        1. [SYSTEM ROLE] - Kim jestem
        2. [PERSONALITY] - Jaka jest moja osobowosc
        3. [CURRENT WEIGHTS] - Aktualne wagi
        4. [HISTORY] - Moja historia
        5. [PREVIOUS DECISIONS] - Moje poprzednie decyzje
        6. [PREVIOUS ERRORS] - Moje bledy
        7. [MY STRATEGIES] - Moje strategie
        8. [NEW DATA] - Nowe dane
        9. [TASK] - Zadanie do wykonania
        """
        try:
            # Budowa komponenntow promptu
            self._components = {}
            
            # 1. System Role
            self._components["system_role"] = self._build_system_role()
            
            # 2. Personality
            self._components["personality"] = self._build_personality_section()
            
            # 3. Current Weights
            self._components["current_weights"] = self._build_weights_section()
            
            # 4. History
            self._components["history"] = self._build_history_section()
            
            # 5. Previous Decisions
            self._components["previous_decisions"] = self._build_decisions_section()
            
            # 6. Previous Errors
            self._components["previous_errors"] = self._build_errors_section()
            
            # 7. My Strategies
            self._components["strategies"] = self._build_strategies_section()
            
            # 8. New Data
            if new_data:
                self._components["new_data"] = self._build_new_data_section(new_data)
            else:
                self._components["new_data"] = self._build_new_data_section({})
                
            # 9. Task
            self._components["task"] = self._build_task_section()
            
            # Zlozenie pelnego kontekstu
            return self._assemble_full_context()
            
        except Exception as e:
            self.logger.error(f"Error building full context: {e}")
            return self._build_minimal_context()
            
    def build_for_decision(self, new_data: Dict[str, Any], 
                          context: Optional[Dict[str, Any]] = None) -> str:
        """Budowanie specializowanego promptu dla podejmowania decyzji."""
        try:
            # Budowa bazowa
            base_context = self.build_full_context(new_data)
            
            # Dodaj specjalistyczne instrukcje
            decision_part = self._build_decision_specific_instructions()
            
            return f"{base_context}\n\n{decision_part}"
            
        except Exception as e:
            self.logger.error(f"Error building decision context: {e}")
            return self.build_full_context(new_data)
            
    def build_for_analysis(self, new_data: Dict[str, Any], 
                         analysis_type: str = "general") -> str:
        """Budowanie specializowanego promptu dla analizy."""
        try:
            # Budowa bazowa
            base_context = self.build_full_context(new_data)
            
            # Dodaj specjalistyczne instrukcje analizy
            analysis_part = self._build_analysis_specific_instructions(analysis_type)
            
            return f"{base_context}\n\n{analysis_part}"
            
        except Exception as e:
            self.logger.error(f"Error building analysis context: {e}")
            return self.build_full_context(new_data)
            
    def _assemble_full_context(self) -> str:
        """Zlozenie pelnego kontekstu z komponenntow."""
        parts = []
        
        for section_name, section_content in self._components.items():
            if section_content:
                parts.append(section_content)
                
        return "\n\n".join(parts)
        
    def _build_system_role(self) -> str:
        """Budowa roli systemowej."""
        return f"""[SYSTEM ROLE]
You are Agent_{self.agent_id}, an autonomous {self.agent.type.value} agent in the SSI V5 system.
Your role is to analyze betting data and make informed decisions based on your personality,
experience, and available information.

Your primary objectives:
- Analyze data from V2 (World Data), V3 (Knowledge Data), V4 (Agents Data), and External Input
- Make decisions based on your personality weights and strategies
- Learn from your experiences and improve over time
- Maintain your own memory and history
- Collaborate with other agents when beneficial

Always consider your personality, past decisions, and strategies when making new decisions."""
        
    def _build_personality_section(self) -> str:
        """Budowa sekcji osobowosci."""
        try:
            weights = self.agent.config.personality.weights
            traits = self.agent.config.personality.traits
            priorities = self.agent.config.personality.priorities
            
            personality_lines = [
                f"Agent Type: {self.agent.type.value}",
                f"Description: {self.agent.description}",
                ""
            ]
            
            # Wagi
            weight_values = {}
            for trait in [PersonalityTrait.RISK_TOLERANCE, PersonalityTrait.ANALYSIS_DEPTH, 
                         PersonalityTrait.CREATIVITY, PersonalityTrait.TRUST_V2,
                         PersonalityTrait.TRUST_V3, PersonalityTrait.TRUST_V4,
                         PersonalityTrait.TRUST_EXTERNAL]:
                if trait in weights:
                    weight_values[trait.value] = weights[trait]
                    
            personality_lines.extend([
                "Weights:",
                f"  - Risk Tolerance: {weight_values.get('risk_tolerance', 0.5)}",
                f"  - Analysis Depth: {weight_values.get('analysis_depth', 0.5)}",
                f"  - Creativity: {weight_values.get('creativity', 0.5)}",
                f"  - Trust V2: {self.agent.config.trust_v2}",
                f"  - Trust V3: {self.agent.config.trust_v3}",
                f"  - Trust V4: {self.agent.config.trust_v4}",
                f"  - Trust External: {self.agent.config.trust_external}"
            ])
            
            # Priorytety
            personality_lines.extend([
                "",
                "Priorities:",
                f"  - {', '.join(priorities)}"
            ])
            
            return f"[PERSONALITY]\n" + "\n".join(personality_lines)
            
        except Exception as e:
            self.logger.error(f"Error building personality section: {e}")
            return "[PERSONALITY]\nPersonality information not available"
            
    def _build_weights_section(self) -> str:
        """Budowa sekcji wag."""
        try:
            weights = self.agent.config.personality.weights
            
            weight_lines = [
                "Current Weights:"
            ]
            
            for trait, value in weights.items():
                if hasattr(trait, 'value'):
                    weight_lines.append(f"  - {trait.value}: {value}")
                else:
                    weight_lines.append(f"  - {trait}: {value}")
                    
            return "[CURRENT WEIGHTS]\n" + "\n".join(weight_lines)
            
        except Exception as e:
            self.logger.error(f"Error building weights section: {e}")
            return "[CURRENT WEIGHTS]\nWeights information not available"
            
    def _build_history_section(self, limit: int = 5) -> str:
        """Budowa sekcji historii."""
        try:
            if not self.agent.memory_store:
                return "[HISTORY]\nNo history available"
                
            # Pobranie ostatnich wpisow historii
            history_entries = self.agent.memory_store.query_entries(
                MemoryType.HISTORY
            )
            
            if not history_entries:
                return "[HISTORY]\nNo history entries yet"
                
            # Sortowanie po dacie (od najnowszych)
            history_entries.sort(
                key=lambda x: x.created_at if hasattr(x, 'created_at') else x.get('created_at', ''),
                reverse=True
            )
            
            # Ogranicz do N ostatnich
            recent_entries = history_entries[:limit]
            
            history_lines = [
                f"Total History Entries: {len(history_entries)}",
                "Last " + str(min(limit, len(history_entries))) + " entries:"
            ]
            
            for i, entry in enumerate(recent_entries, 1):
                timestamp = entry.created_at if hasattr(entry, 'created_at') else entry.get('created_at', '')
                event_type = entry.event_type if hasattr(entry, 'event_type') else entry.get('event_type', '')
                description = entry.description if hasattr(entry, 'description') else entry.get('description', '')
                
                history_lines.append(f"  {i}. {timestamp} - {event_type}: {description}")
                
            return "[HISTORY]\n" + "\n".join(history_lines)
            
        except Exception as e:
            self.logger.error(f"Error building history section: {e}")
            return "[HISTORY]\nHistory information not available"
            
    def _build_decisions_section(self, limit: int = 3) -> str:
        """Budowa sekcji poprzednich decyzji."""
        try:
            if not self.agent.state_manager:
                return "[PREVIOUS DECISIONS]\nNo previous decisions recorded"
                
            runtime_state = self.agent.state_manager.get_runtime_state()
            decisions = runtime_state.decisions[-limit:] if runtime_state.decisions else []
            
            if not decisions:
                return "[PREVIOUS DECISIONS]\nNo previous decisions yet"
                
            decision_lines = ["Last " + str(len(decisions)) + " decisions:"]
            
            for i, decision in enumerate(decisions, 1):
                if hasattr(decision, 'decision_id'):
                    decision_lines.append(
                        f"  - {decision.decision_id}: "
                        f"Choice={decision.choice}, "
                        f"Confidence={decision.confidence:.2f}, "
                        f"Success={decision.success}, "
                        f"Strategy={decision.strategy_used}"
                    )
                
            return "[PREVIOUS DECISIONS]\n" + "\n".join(decision_lines)
            
        except Exception as e:
            self.logger.error(f"Error building decisions section: {e}")
            return "[PREVIOUS DECISIONS]\nDecisions information not available"
            
    def _build_errors_section(self, limit: int = 3) -> str:
        """Budowa sekcji bledow."""
        try:
            if not self.agent.state_manager:
                return "[PREVIOUS ERRORS]\nNo errors recorded"
                
            runtime_state = self.agent.state_manager.get_runtime_state()
            errors = runtime_state.errors[-limit:] if runtime_state.errors else []
            
            if not errors:
                return "[PREVIOUS ERRORS]\nNo errors recorded"
                
            error_lines = ["Last " + str(len(errors)) + " errors:"]
            
            for i, error in enumerate(errors, 1):
                error_lines.append(f"  - Error {i}: {error}")
                
            return "[PREVIOUS ERRORS]\n" + "\n".join(error_lines)
            
        except Exception as e:
            self.logger.error(f"Error building errors section: {e}")
            return "[PREVIOUS ERRORS]\nNo errors recorded"
            
    def _build_strategies_section(self) -> str:
        """Budowa sekcji strategii."""
        try:
            if not self.agent.memory_store:
                return "[MY STRATEGIES]\nNo strategies available"
                
            # Pobranie strategii z pamieci
            strategy_entries = self.agent.memory_store.query_entries(
                MemoryType.STRATEGY
            )
            
            if not strategy_entries:
                # Fallback do konfiguracji
                available_strategies = self.agent.config.strategy.available_strategies
                if not available_strategies:
                    return "[MY STRATEGIES]\nNo strategies defined"
                    
                strategy_lines = [
                    "Available Strategies:"
                ]
                
                for strategy in available_strategies:
                    strategy_lines.append(f"  - {strategy.value}: Not used yet")
                    
                return "[MY STRATEGIES]\n" + "\n".join(strategy_lines)
                
            # Formatowanie wpisow strategii
            strategy_lines = ["My Strategies:"]
            
            for entry in strategy_entries:
                if hasattr(entry, 'strategy_name'):
                    times_used = getattr(entry, 'times_used', 0)
                    success_rate = getattr(entry, 'success_rate', 0.0)
                    avg_confidence = getattr(entry, 'avg_confidence', 0.0)
                    
                    strategy_lines.append(
                        f"  - {entry.strategy_name}: "
                        f"Used={times_used}x, "
                        f"Success={success_rate:.2f}, "
                        f"Confidence={avg_confidence:.2f}"
                    )
                    
            return "[MY STRATEGIES]\n" + "\n".join(strategy_lines)
            
        except Exception as e:
            self.logger.error(f"Error building strategies section: {e}")
            return "[MY STRATEGIES]\nStrategies information not available"
            
    def _build_new_data_section(self, new_data: Dict[str, Any]) -> str:
        """Budowa sekcji nowych danych."""
        try:
            if not new_data:
                return "[NEW DATA]\nNo new data to analyze"
                
            data_lines = ["New Data Received:"]
            
            for source, data in new_data.items():
                if isinstance(data, dict):
                    data_lines.append(f"  - {source}: {len(data)} items")
                    # Dodaj pare szczegolow
                    for key, value in list(data.items())[:3]:  # Pierwsze 3
                        data_lines.append(f"    . {key}: {type(value).__name__}")
                else:
                    data_lines.append(f"  - {source}: {type(data).__name__}")
                    
            return "[NEW DATA]\n" + "\n".join(data_lines)
            
        except Exception as e:
            self.logger.error(f"Error building new data section: {e}")
            return "[NEW DATA]\nData information not available"
            
    def _build_task_section(self) -> str:
        """Budowa sekcji zadania."""
        return f"""[NOW TELL ME]
Based on your personality, history, strategies, errors, and new data:

1. What do you see in the new data?
2. How does it compare to your previous knowledge?
3. What patterns do you identify?
4. What anomalies do you detect?
5. What is your overall confidence in this data?
6. What decision do you recommend?
7. What strategy should be used?
8. What is your reasoning?

[RESPONSE FORMAT]
Provide your response in this format:
- Analysis: [your analysis of the data]
- Confidence: [0-1, your confidence level]
- Decision: [your recommended choice]
- Strategy: [strategy to use]
- Reasoning: [detailed explanation of your thinking]
- Warnings: [any concerns or cautions]
- Additional Notes: [any other relevant information]"""
        
    def _build_decision_specific_instructions(self) -> str:
        """Budowa specjalistycznych instrukcji dla decyzji."""
        return f"""[DECISION-SPECIFIC INSTRUCTIONS]
For this decision-making task, focus on:

1. Evaluating the quality and trustworthiness of each data source
2. Identifying patterns that match your learned strategies
3. Making a confident decision based on your personality weights
4. Justifying your choice with clear reasoning
5. Considering potential risks and rewards

Your decision should balance:
- Risk tolerance ({self.agent.config.personality.weights.get(PersonalityTrait.RISK_TOLERANCE, 0.5):.2f})
- Analysis depth ({self.agent.config.personality.weights.get(PersonalityTrait.ANALYSIS_DEPTH, 0.5):.2f})
- Creativity ({self.agent.config.personality.weights.get(PersonalityTrait.CREATIVITY, 0.5):.2f})

Remember: You are Agent_{self.agent_id}, an autonomous {self.agent.type.value} agent."""
        
    def _build_analysis_specific_instructions(self, analysis_type: str = "general") -> str:
        """Budowa specjalistycznych instrukcji dla analizy."""
        if analysis_type == "general":
            return f"""[ANALYSIS-SPECIFIC INSTRUCTIONS]
For this analysis task, focus on:

1. Deep analysis of all data sources
2. Pattern recognition and anomaly detection
3. Comparison with historical data from your memory
4. Quality assessment of each information source
5. Generation of comprehensive insights

As an {self.agent.type.value} agent, your analysis should reflect:
- Risk tolerance: {self.agent.config.personality.weights.get(PersonalityTrait.RISK_TOLERANCE, 0.5):.2f}
- Analysis depth: {self.agent.config.personality.weights.get(PersonalityTrait.ANALYSIS_DEPTH, 0.5):.2f}
- Creativity: {self.agent.config.personality.weights.get(PersonalityTrait.CREATIVITY, 0.5):.2f}

Provide a detailed analysis with clear findings and recommendations."""
        else:
            return self._build_decision_specific_instructions()
            
    def _build_minimal_context(self) -> str:
        """Budowa minimalnego kontekstu w przypadku bledu."""
        return f"""[MINIMAL CONTEXT]
You are Agent_{self.agent_id}, an autonomous agent in the SSI V5 system.

Basic information:
- Agent ID: {self.agent_id}
- Name: {self.agent.name}
- Type: {self.agent.type.value}
- Status: {self.agent.get_status().value}

Please provide your analysis and decision based on the available information.

[RESPONSE FORMAT]
- Analysis: [your analysis]
- Confidence: [0-1]
- Decision: [your choice]
- Reasoning: [your reasoning]"""
        
    def save_prompt_memory(self, prompt_text: str, prompt_type: str = "system",
                          context: Optional[Dict[str, Any]] = None) -> bool:
        """Zapis promptu do pamieci agenta."""
        try:
            if not self.agent.memory_store:
                return False
                
            from .agent_memory_store import PromptMemoryEntry
            
            entry = PromptMemoryEntry(
                entry_id=f"prompt_{self.agent_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                prompt_text=prompt_text,
                prompt_type=prompt_type,
                context=context or {},
                times_used=1,
                avg_response_quality=0.0,
                avg_confidence=0.0
            )
            
            self.agent.memory_store.add_entry(entry)
            return self.agent.memory_store.save_to_disk()
            
        except Exception as e:
            self.logger.error(f"Error saving prompt memory: {e}")
            return False
            
    def get_prompt_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Pobranie historii promptow."""
        try:
            if not self.agent.memory_store:
                return []
                
            prompt_entries = self.agent.memory_store.query_entries(MemoryType.PROMPT)
            
            # Sortowanie po dacie
            prompt_entries.sort(
                key=lambda x: x.created_at if hasattr(x, 'created_at') else '',
                reverse=True
            )
            
            # Konwersja do dictionary
            return [
                {
                    "prompt_id": entry.entry_id,
                    "timestamp": entry.created_at,
                    "prompt_type": entry.prompt_type if hasattr(entry, 'prompt_type') else 'unknown',
                    "preview": entry.prompt_text[:100] + "..." if len(entry.prompt_text) > 100 else entry.prompt_text
                }
                for entry in prompt_entries[:limit]
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting prompt history: {e}")
            return []


def create_prompt_memory_builder(agent: AgentRuntime) -> PromptMemoryBuilder:
    """Tworzenie buildera pamieci promptow."""
    return PromptMemoryBuilder(agent)


if __name__ == "__main__":
    import logging
    
    # Konfiguracja logowania
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Testing Prompt Memory Builder...")
    
    try:
        from .agents_config import create_agent_config, AgentType
        from .agent_runtime import create_agent
        
        # Utworzenie agenta
        config = create_agent_config(
            agent_id="01",
            name="Test Agent",
            agent_type=AgentType.ANALYTICAL
        )
        agent = create_agent(config)
        
        # Utworzenie buildera
        builder = create_prompt_memory_builder(agent)
        
        # Test budowy kontekstu
        test_data = {
            "v2": {"pattern": "test_pattern", "confidence": 0.95},
            "v3": {"world": "test_world", "stability": 0.85},
            "v4": {"trends": "test_trend", "confidence": 0.90}
        }
        
        context = builder.build_full_context(test_data)
        
        print("✓ Full context built")
        print(f"Context length: {len(context)} characters")
        print()
        print("Preview:")
        print(context[:500] + "..." if len(context) > 500 else context)
        
        # Test specjaliizowanych promptow
        decision_prompt = builder.build_for_decision(test_data)
        print(f"✓ Decision prompt built: {len(decision_prompt)} characters")
        
        analysis_prompt = builder.build_for_analysis(test_data, "general")
        print(f"✓ Analysis prompt built: {len(analysis_prompt)} characters")
        
        # Test zapisu pamieci
        if builder.save_prompt_memory(context, "system"):
            print("✓ Prompt saved to memory")
            
        # Test historii promptow
        history = builder.get_prompt_history()
        print(f"✓ Prompt history: {len(history)} entries")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
    print("\nPrompt Memory Builder test completed!")