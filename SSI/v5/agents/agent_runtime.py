"""
SSI V5 - Agent Runtime
Cykl pracy pojedynczego agenta

Zgodnie z dokumentacja Sprint 11.5 v2.0:
- Agent Runtime Foundation
- Memory Observation System
- CIAGLY CYKL AGENTOW (nowa architektura)

CYKL AGENTA:
1. Wczytaj pamięć
2. Pobierz dane (V2, V3, V4, External)
3. Porównaj: STARA WIEDZA + NOWE DANE
4. Analiza
5. Decyzja
6. Zapis doświadczenia
7. Aktualizacja historii
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict

# Dodanie sciezki do SSI do sys.path
SSI_PATH = "D:\\sts\\aplikacjaTyperBetAi\\SSI"
if SSI_PATH not in sys.path:
    sys.path.insert(0, SSI_PATH)

from .agents_config import (
    AgentConfig, AgentStatus, AgentType, StrategyType, PersonalityTrait
)
from .agent_state import (
    AgentStateManager, DecisionRecord, BehaviorRecord, StrategyRecord, 
    HistoryEntry, RelationshipEntry, AgentRuntimeState, create_agent_state_manager
)
from .agent_memory_store import (
    AgentMemoryStore, PersonalityMemoryEntry, BehaviorMemoryEntry, 
    StrategyMemoryEntry, HistoryMemoryEntry, RelationshipMemoryEntry, 
    PromptMemoryEntry, MemoryType, create_agent_memory_store
)


class AgentRuntime:
    """Runtime pojedynczego agenta.
    
    Odpowiedzialnosc:
    - Wykonanie cyklu agenta
    - Zarzadzanie pamięcia
    - Podejmowanie decyzji
    - Rejestrowanie doświadczeń
    """
    
    def __init__(self, config: AgentConfig):
        """Inicjalizacja agenta."""
        self.config = config
        self.agent_id = config.agent_id
        self.name = config.name
        self.description = config.description
        self.type = config.type
        
        # Status
        self._status = AgentStatus.INITIALIZED
        
        # Pamiec
        self.memory_store: Optional[AgentMemoryStore] = None
        self.state_manager: Optional[AgentStateManager] = None
        
        # Logging
        self.logger = logging.getLogger(f"Agent_{self.agent_id}")
        
        # Inicjalizacja
        self._initialize_memory()
        self._initialize_state()
        
    def _initialize_memory(self) -> None:
        """Inicjalizacja pamieci agenta."""
        try:
            base_path = self.config.memory.base_path
            os.makedirs(base_path, exist_ok=True)
            
            self.memory_store = create_agent_memory_store(
                self.agent_id, 
                base_path
            )
            self.memory_store.initialize()
            
            #ిత్రydé pliki pamieci z dysku
            self._load_memory_files()
            
            self.logger.info(f"Agent {self.agent_id} memory initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing memory: {e}")
            raise
            
    def _initialize_state(self) -> None:
        """Inicjalizacja stanu agenta."""
        self.state_manager = create_agent_state_manager(self.agent_id)
        self.state_manager.initialize()
        self._status = AgentStatus.INITIALIZED
        
    def _load_memory_files(self) -> None:
        """Zaladowanie plikow pamieci z dysku."""
        try:
            base_path = self.config.memory.base_path
            
            # Sprawdzenie czy pliki istnieja
            if os.path.exists(base_path):
                self.memory_store.load_from_disk()
                
            # Jeśli brak plików, utworz domyślne
            if not self._has_memory_data():
                self._create_default_memory()
                
        except Exception as e:
            self.logger.error(f"Error loading memory files: {e}")
            # Utworz domyslne w przypadku bledu
            self._create_default_memory()
            
    def _has_memory_data(self) -> bool:
        """Sprawdzenie czy agent ma dane w pamieci."""
        if not self.memory_store:
            return False
            
        stats = self.memory_store.get_statistics()
        return any(stat["count"] > 0 for stat in stats.values())
        
    def _create_default_memory(self) -> None:
        """Utworzenie domyslnych danych pamieci."""
        try:
            # Osobowosc
            personality = PersonalityMemoryEntry(
                entry_id=f"personality_{self.agent_id}_001",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                data={},  # Pole wymagane
                risk=self.config.personality.weights.get(PersonalityTrait.RISK_TOLERANCE, 0.5),
                analysis=self.config.personality.weights.get(PersonalityTrait.ANALYSIS_DEPTH, 0.5),
                creativity=self.config.personality.weights.get(PersonalityTrait.CREATIVITY, 0.5),
                trust_v2=self.config.trust_v2,
                trust_v3=self.config.trust_v3,
                trust_v4=self.config.trust_v4,
                trust_external=self.config.trust_external,
                agent_type=self.config.type.value,
                description="Initial personality configuration",
                traits={
                    "risk_tolerance": self.config.personality.weights.get(PersonalityTrait.RISK_TOLERANCE, 0.5),
                    "analysis_depth": self.config.personality.weights.get(PersonalityTrait.ANALYSIS_DEPTH, 0.7),
                    "creativity_level": self.config.personality.weights.get(PersonalityTrait.CREATIVITY, 0.5)
                },
                priorities=self.config.personality.priorities
            )
            self.memory_store.add_entry(personality)
            
            # Strategie
            for strategy in self.config.strategy.available_strategies:
                strategy_entry = StrategyMemoryEntry(
                    entry_id=f"strategy_{self.agent_id}_{strategy.value}_001",
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat(),
                    strategy_name=strategy.value,
                    strategy_type=strategy.value,
                    description=f"Default {strategy.value} strategy",
                    times_used=0,
                    times_successful=0,
                    success_rate=0.0
                )
                self.memory_store.add_entry(strategy_entry)
                
            # Zapis domyslnych na dysku
            self.save_memory()
            
            self.logger.info(f"Agent {self.agent_id} default memory created")
            
        except Exception as e:
            self.logger.error(f"Error creating default memory: {e}")
            
    def is_active(self) -> bool:
        """Sprawdzenie czy agent jest aktywny."""
        return self.config.enabled and self._status not in [
            AgentStatus.ERROR, AgentStatus.SHUTDOWN
        ]
        
    def get_status(self) -> AgentStatus:
        """Pobranie statusu agenta."""
        return self._status
        
    def set_status(self, status: AgentStatus) -> None:
        """Ustawienie statusu agenta."""
        self._status = status
        if self.state_manager:
            self.state_manager.set_status(status)
            
    def load_memory(self) -> bool:
        """Zaladowanie pamieci agenta (krok 1 cyklu)."""
        try:
            if not self.memory_store:
                return False
                
            # Odczyt z dysku
            self.memory_store.load_from_disk()
            
            # Aktualizacja stanu pamieci
            stats = self.memory_store.get_statistics()
            if self.state_manager:
                self.state_manager.update_memory_counts(
                    personality=stats.get("personality", {}).get("count", 0) if isinstance(stats, dict) else 0,
                    behavior=stats.get("behavior", {}).get("count", 0) if isinstance(stats, dict) else 0,
                    strategy=stats.get("strategy", {}).get("count", 0) if isinstance(stats, dict) else 0,
                    history=stats.get("history", {}).get("count", 0) if isinstance(stats, dict) else 0,
                    relationship=stats.get("relationship", {}).get("count", 0) if isinstance(stats, dict) else 0,
                    prompt=stats.get("prompt", {}).get("count", 0) if isinstance(stats, dict) else 0
                )
                
            self._status = AgentStatus.IDLE
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading memory: {e}")
            return False
            
    def save_memory(self) -> bool:
        """Zapis pamieci agenta do pliku."""
        try:
            if not self.memory_store:
                return False
                
            return self.memory_store.save_to_disk()
            
        except Exception as e:
            self.logger.error(f"Error saving memory: {e}")
            return False
            
    def run_cycle(self, collector_data: Dict[str, Any], 
                  world_context: Dict[str, Any], 
                  cycle_count: int) -> Dict[str, Any]:
        """Wykonywanie pojedynczego cyklu agenta.
        
        CYKL AGENTA (zgodnie z Sprint 11.5 v2.0):
        1. Wczytaj pamięć
        2. Pobierz dane (V2, V3, V4, External)
        3. Porównaj: STARA WIEDZA + NOWE DANE
        4. Analiza
        5. Decyzja
        6. Zapis doświadczenia
        7. Aktualizacja historii
        """
        try:
            # Krok 1: Wczytaj pamięć (juz zaladowana w _run_single_agent_cycle)
            # Pominiety tutaj, poniewaz memory jest ladowana w runtime_controller
            
            # Krok 2: Pobierz dane (juz pobrane i przekazane jako collector_data)
            # Dane: V2 World, V3 Knowledge, V4 Agents, External Input
            
            # Krok 3: Porównaj STARA WIEDZA + NOWE DANE
            analysis_result = self._analyze_data(collector_data, world_context)
            
            # Krok 4: Analiza
            # Podzial na etapy:
            # - Analiza jakości danych
            # - Porównanie z historycznymi wzorcami
            # - Identyfikacja anomalii
            # - Ocena zaufania do zrodeł
            
            # Krok 5: Decyzja
            decision = self._make_decision(analysis_result)
            
            # Krok 6: Zapis doświadczenia
            self._save_experience(decision, analysis_result, cycle_count)
            
            # Krok 7: Aktualizacja historii
            self._update_history(decision, analysis_result, cycle_count)
            
            # Aktualizacja stanu
            self._status = AgentStatus.IDLE
            
            # Aktualizacja statystyk
            if self.state_manager:
                self.state_manager.increment_cycle()
                self.state_manager.update_activity_time()
                
            # Zwrocenie wyniku
            return {
                "agent_id": self.agent_id,
                "cycle_count": cycle_count,
                "decision": decision,
                "analysis": analysis_result,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in agent cycle: {e}")
            self._status = AgentStatus.ERROR
            return {
                "agent_id": self.agent_id,
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
            
    def _analyze_data(self, collector_data: Dict[str, Any], 
                      world_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza danych z collectorow (krok 3).
        
        Porownanie:
        - STARA WIEDZA (z pamieci) vs NOWE DANE (z collectorow)
        - Identyfikacja zmian i wzorców
        - Ocena jakości i zaufania
        """
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "sources_used": list(collector_data.keys()),
            "quality_scores": {},
            "trust_scores": {},
            "detected_changes": [],
            "identified_patterns": [],
            "anomalies": [],
            "overall-confidence": 0.0
        }
        
        try:
            # Analiza kazdego zródła
            for source_name, source_data in collector_data.items():
                if source_data is None:
                    analysis["quality_scores"][source_name] = 0.0
                    analysis["trust_scores"][source_name] = 0.0
                    continue
                    
                # Ocena jakości danych
                quality = self._evaluate_data_quality(source_name, source_data)
                analysis["quality_scores"][source_name] = quality
                
                # Ocena zaufania
                trust = self._get_trust_score(source_name)
                analysis["trust_scores"][source_name] = trust
                
                # Porównanie ze stara wiedza
                changes = self._compare_with_memory(source_name, source_data)
                if changes:
                    analysis["detected_changes"].extend(changes)
                    
            # Identyfikacja wzorców
            patterns = self._identify_patterns(analysis)
            analysis["identified_patterns"] = patterns
            
            # Identyfikacja anomalii
            anomalies = self._identify_anomalies(analysis)
            analysis["anomalies"] = anomalies
            
            # Ogolne zaufanie
            analysis["overall-confidence"] = self._calculate_overall_confidence(analysis)
            
            self.logger.info(f"Agent {self.agent_id}: Analysis completed, confidence: {analysis['overall-confidence']:.2f}")
            
        except Exception as e:
            self.logger.error(f"Error in data analysis: {e}")
            
        return analysis
        
    def _evaluate_data_quality(self, source_name: str, data: Any) -> float:
        """Ocena jakości danych ze zródła."""
        # Bazowa ocena
        base_quality = 0.7
        
        # Ocena na podstawie typu zródła
        if source_name == "v2":
            return min(0.95, base_quality + 0.2)  # V2 - wysoka jakość
        elif source_name == "v3":
            return min(0.90, base_quality + 0.15)  # V3 - dobra jakość
        elif source_name == "v4":
            return min(0.85, base_quality + 0.10)  # V4 - dobra jakość
        elif source_name == "external":
            return min(0.60, base_quality - 0.10)  # External - niższa jakość
        else:
            return base_quality
            
    def _get_trust_score(self, source_name: str) -> float:
        """Pobranie poziomu zaufania dla zródła."""
        if source_name == "v2":
            return self.config.trust_v2
        elif source_name == "v3":
            return self.config.trust_v3
        elif source_name == "v4":
            return self.config.trust_v4
        elif source_name == "external":
            return self.config.trust_external
        else:
            return 0.5
            
    def _compare_with_memory(self, source_name: str, new_data: Any) -> List[Dict[str, Any]]:
        """Porównanie nowych danych ze stara wiedza z pamieci."""
        changes = []
        
        try:
            # W przyszlosci: porównanie z historycznymi danymi
            # Na razie: zwroc pustą liste (implementacja podstawowa)
            changes.append({
                "source": source_name,
                "type": "new_data",
                "description": f"New data received from {source_name}",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Error comparing with memory: {e}")
            
        return changes
        
    def _identify_patterns(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identyfikacja wzorców w danych."""
        patterns = []
        
        try:
            # W przyszlosci: zaawansowana identyfikacja wzorców
            # Na razie: rozpznanie podstawowych wzorców
            if analysis["overall-confidence"] > 0.7:
                patterns.append({
                    "pattern_type": "high_confidence",
                    "description": "High confidence data pattern detected",
                    "strength": analysis["overall-confidence"]
                })
                
        except Exception as e:
            self.logger.error(f"Error identifying patterns: {e}")
            
        return patterns
        
    def _identify_anomalies(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identyfikacja anomalii w danych."""
        anomalies = []
        
        try:
            # W przyszlosci: zaawansowane wykrywanie anomalii
            # Na razie: sprawdzenie jakości danych
            for source, quality in analysis.get("quality_scores", {}).items():
                if quality < 0.5:
                    anomalies.append({
                        "source": source,
                        "type": "low_quality",
                        "severity": "medium",
                        "description": f"Low quality data from {source}"
                    })
                    
        except Exception as e:
            self.logger.error(f"Error identifying anomalies: {e}")
            
        return anomalies
        
    def _calculate_overall_confidence(self, analysis: Dict[str, Any]) -> float:
        """Obliczenie ogolnego poziomu zaufania."""
        try:
            quality_scores = analysis.get("quality_scores", {})
            trust_scores = analysis.get("trust_scores", {})
            
            if not quality_scores or not trust_scores:
                return 0.5
                
            # Srednia wazona
            total_weight = 0
            weighted_sum = 0
            
            for source in quality_scores.keys():
                if source in trust_scores:
                    weight = trust_scores[source]
                    score = quality_scores[source]
                    weighted_sum += score * weight
                    total_weight += weight
                    
            if total_weight > 0:
                return weighted_sum / total_weight
            else:
                return 0.5
                
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {e}")
            return 0.5
            
    def _make_decision(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Podejmowanie decyzji (krok 5).
        
        Wybor strategii i podjcie decyzji na podstawie:
        - Analizy danych
        - Osobowosci agenta
        - Doświadczenia historycznego
        - Dostepnych strategii
        """
        try:
            # Wybor strategii
            strategy = self._select_strategy(analysis)
            
            # Generowanie decyzji
            decision = self._generate_decision(strategy, analysis)
            
            # Okreslenie poziomu zaufania
            confidence = self._calculate_decision_confidence(strategy, analysis)
            
            # Rejestracja decyzji
            decision_record = DecisionRecord(
                decision_id=f"dec_{self.agent_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                timestamp=datetime.now().isoformat(),
                decision_type="prediction",  # Domyslnie predykcja
                choice=decision["choice"],
                confidence=confidence,
                input_data={"sources": list(analysis.get("sources_used", []))},
                used_sources=list(analysis.get("sources_used", [])),
                analysis_result={"patterns": len(analysis.get("identified_patterns", []))},
                reasoning=decision.get("reasoning", ""),
                success=None,  # Bede ustawione pozniejsze (po weryfikacji)
                strategy_used=strategy
            )
            
            # Dodanie do pamieci zachowan
            if self.memory_store:
                behavior_record = BehaviorMemoryEntry(
                    entry_id=f"beh_{self.agent_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat(),
                    behavior_type="decision_making",
                    action=strategy,
                    description=f"Made decision using {strategy} strategy",
                    data_used=list(analysis.get("sources_used", [])),
                    effectiveness=0.0,  # Bede aktualizowane
                    success_rate=0.0,
                    usage_count=1
                )
                self.memory_store.add_entry(behavior_record)
                
            # Aktualizacja stanu agenta
            if self.state_manager:
                self.state_manager.add_decision(decision_record)
                self.state_manager.set_current_strategy(strategy)
                
            return {
                "decision_id": decision_record.decision_id,
                "choice": decision["choice"],
                "confidence": confidence,
                "strategy": strategy,
                "reasoning": decision.get("reasoning", ""),
                "advanced": decision.get("advanced", {}),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error making decision: {e}")
            return {
                "choice": "error",
                "confidence": 0.0,
                "strategy": "none",
                "reasoning": f"Error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            
    def _select_strategy(self, analysis: Dict[str, Any]) -> str:
        """Wybór strategii na podstawie analizy i osobowosci."""
        # Domyslnie aktualna strategia
        default_strategy = self.config.strategy.default_strategy.value
        
        # Jeśli dostępne strategie, sprawdż która jest najlepsza
        available = [s.value for s in self.config.strategy.available_strategies]
        if default_strategy in available:
            return default_strategy
        elif available:
            return available[0]  # Pierwsza dostępna
        else:
            return "analytical"  # Fallback
            
    def _generate_decision(self, strategy: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generowanie decyzji dla danej strategii."""
        # prostitution na podstawie strategii
        if strategy == "analytical":
            return self._generate_analytical_decision(analysis)
        elif strategy == "conservative":
            return self._generate_conservative_decision(analysis)
        elif strategy == "balanced":
            return self._generate_balanced_decision(analysis)
        elif strategy == "aggressive":
            return self._generate_aggressive_decision(analysis)
        else:
            return self._generate_analytical_decision(analysis)
            
    def _generate_analytical_decision(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generowanie decyzji analitycznej."""
        confidence = analysis.get("overall-confidence", 0.7)
        
        # Decyzja na podstawie analizy
        if confidence > 0.8:
            choice = "high_confidence_choice"
        elif confidence > 0.6:
            choice = "medium_confidence_choice"
        else:
            choice = "low_confidence_choice"
            
        return {
            "choice": choice,
            "confidence": confidence,
            "reasoning": f"Analytical decision based on confidence {confidence:.2f}",
            "advanced": {
                "data_quality": analysis.get("overall-confidence", 0.0),
                "patterns_detected": len(analysis.get("identified_patterns", [])),
                "anomalies_detected": len(analysis.get("anomalies", []))
            }
        }
        
    def _generate_conservative_decision(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generowanie zachowawczej decyzji."""
        confidence = analysis.get("overall-confidence", 0.7) * 0.8  # Redukcja zaufania
        
        return {
            "choice": "conservative_choice",
            "confidence": confidence,
            "reasoning": "Conservative decision with reduced risk",
            "advanced": {"risk_factor": 0.2}
        }
        
    def _generate_balanced_decision(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generowanie zrownowazonej decyzji."""
        return {
            "choice": "balanced_choice",
            "confidence": 0.7,
            "reasoning": "Balanced decision considering all factors",
            "advanced": {}
        }
        
    def _generate_aggressive_decision(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generowanie agresywnej decyzji."""
        confidence = analysis.get("overall-confidence", 0.7) * 1.2  # Zwiekszenie zaufania
        
        return {
            "choice": "aggressive_choice",
            "confidence": min(0.95, confidence),
            "reasoning": "Aggressive decision with higher risk tolerance",
            "advanced": {"risk_factor": 0.8}
        }
        
    def _calculate_decision_confidence(self, strategy: str, analysis: Dict[str, Any]) -> float:
        """Obliczenie poziomu zaufania do decyzji."""
        base_confidence = analysis.get("overall-confidence", 0.5)
        
        # Modyfikacja na podstawie strategii
        if strategy == "analytical":
            return base_confidence
        elif strategy == "conservative":
            return base_confidence * 0.8
        elif strategy == "aggressive":
            return min(0.95, base_confidence * 1.2)
        else:
            return base_confidence
            
    def _save_experience(self, decision: Dict[str, Any], 
                        analysis: Dict[str, Any], 
                        cycle_count: int) -> None:
        """Zapis doświadczenia (krok 6)."""
        try:
            # Zapis decyzji do pamieci historycznej
            if self.memory_store:
                history_entry = HistoryMemoryEntry(
                    entry_id=f"hist_{self.agent_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat(),
                    event_type="decision_made",
                    description=f"Decision: {decision.get('choice', 'unknown')}",
                    categories=["decision", "autonomous"],
                    related_decision_id=decision.get("decision_id", ""),
                    outcome={},
                    success=None,
                    evaluation=0.0,
                    confidence=decision.get("confidence", 0.0)
                )
                self.memory_store.add_entry(history_entry)
                
            # Aktualizacja strategii
            self._update_strategy_effectiveness(decision.get("strategy", ""), decision.get("confidence", 0.0))
            
        except Exception as e:
            self.logger.error(f"Error saving experience: {e}")
            
    def _update_strategy_effectiveness(self, strategy_name: str, confidence: float) -> None:
        """Aktualizacja skutecznosci strategii."""
        try:
            if not self.memory_store:
                return
                
            # Znajdz strategie w pamieci
            entries = self.memory_store.query_entries(MemoryType.STRATEGY, strategy_name=strategy_name)
            
            if entries:
                for entry in entries:
                    if hasattr(entry, 'strategy_name') and entry.strategy_name == strategy_name:
                        # Aktualizacja
                        entry.times_used += 1
                        entry.last_used = datetime.now().isoformat()
                        
                        # Aktualizacja mediantej skutecznosci
                        if entry.times_used > 0:
                            entry.success_rate = (entry.times_successful / entry.times_used) if entry.times_used > 0 else 0.0
                            
                # Zapis zaktualizowanej pamieci
                self.memory_store.save_to_disk()
                
        except Exception as e:
            self.logger.error(f"Error updating strategy effectiveness: {e}")
            
    def _update_history(self, decision: Dict[str, Any], 
                       analysis: Dict[str, Any], 
                       cycle_count: int) -> None:
        """Aktualizacja historii (krok 7)."""
        try:
            # Aktualizacja stanu agenta
            if self.state_manager:
                history_entry = HistoryEntry(
                    entry_id=f"hist_run_{self.agent_id}_{cycle_count}",
                    timestamp=datetime.now().isoformat(),
                    event_type="cycle_completed",
                    description=f"Cycle {cycle_count} completed successfully",
                    details={
                        "decision": decision.get("choice", ""),
                        "strategy": decision.get("strategy", ""),
                        "confidence": decision.get("confidence", 0.0)
                    },
                    categories=["cycle", "runtime"],
                    tags=["autonomous", "agent_cycle"]
                )
                self.state_manager.add_history_entry(history_entry)
                
        except Exception as e:
            self.logger.error(f"Error updating history: {e}")
            
    def shutdown(self) -> bool:
        """Wylaczenie agenta."""
        try:
            # Zapis stanu
            self.save_memory()
            
            # Aktualizacja statusu
            self._status = AgentStatus.SHUTDOWN
            if self.state_manager:
                self.state_manager.set_status(AgentStatus.SHUTDOWN)
                
            self.logger.info(f"Agent {self.agent_id} shut down")
            return True
            
        except Exception as e:
            self.logger.error(f"Error shutting down agent: {e}")
            return False


def create_agent(config: AgentConfig) -> AgentRuntime:
    """Tworzenie nowego agenta."""
    return AgentRuntime(config)


if __name__ == "__main__":
    import logging
    
    # Konfiguracja logowania
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Testing Agent Runtime...")
    
    try:
        from .agents_config import create_agent_config, AgentType
        
        # Utworzenie konfiguracji
        config = create_agent_config(
            agent_id="01",
            name="Agent_01",
            agent_type=AgentType.ANALYTICAL
        )
        
        # Utworzenie agenta
        agent = create_agent(config)
        
        print(f"Created Agent: {agent.agent_id}")
        print(f"Name: {agent.name}")
        print(f"Type: {agent.type.value}")
        print(f"Status: {agent.get_status().value}")
        
        # Test pamieci
        if agent.load_memory():
            print("✓ Memory loaded")
        
        # Test cyklu (z pustymi danymi)
        test_data = {"v2": {"test": "data"}, "v3": {"test": "data"}}
        test_context = {"timestamp": datetime.now().isoformat(), "cycle_count": 1}
        
        result = agent.run_cycle(test_data, test_context, 1)
        print(f"✓ Cycle completed: {result.get('success')}")
        print(f"  Decision: {result.get('decision', {}).get('choice')}")
        print(f"  Strategy: {result.get('decision', {}).get('strategy')}")
        print(f"  Confidence: {result.get('decision', {}).get('confidence'):.2f}")
        
        # Zapis pamieci
        if agent.save_memory():
            print("✓ Memory saved")
            
        # stat down
        if agent.shutdown():
            print("✓ Agent shut down")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
    print("\nAgent Runtime test completed!")