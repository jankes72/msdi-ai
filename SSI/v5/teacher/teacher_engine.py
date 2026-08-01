"""
SSI V5 - Teacher Engine Core
Glowny silnik nauczyciela

Zgodnie z dokumentacja:
- 04_AGENT_MEMORY_BEHAVIOR_EVOLUTION.md Sekcja: Teacher Engine
- 02_DEVELOPER_INPUT_ARCHITECTURE.md (Obserwacja agentow)

ZASADY (zgodnie z V5 Architecture):
1. Kazdy agent ma wlasna pamiec, predykcje, katalog wynikow, ranking strategii
2. Pamiec wplywa na zachowanie agenta
3. Teacher Engine obserwuje, analizuje i uczy
4. Agenci NIE kopiuja strategii innych - jedynie analizuja i tworza wlasne ulepszenia
5. Teacher NIE ingeruje bezposrednio w pamiec agentow - jedynie sugeruje
"""

import os
import sys
import time
import json
import logging
import threading
import queue as python_queue
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

# Dodanie sciezki do SSI do sys.path
SSI_PATH = "D:\\sts\\aplikacjaTyperBetAi\\SSI"
if SSI_PATH not in sys.path:
    sys.path.insert(0, SSI_PATH)

from .teacher_config import (
    TeacherConfig, TeacherMode, TeachingStrategy, 
    TeacherStatus, ObservationStatus
)

logger = logging.getLogger(__name__)


@dataclass
class AgentStateSnapshot:
    """Zrzut stanu agenta."""
    agent_id: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = ""
    current_task: Optional[str] = None
    current_strategy: Optional[str] = None
    memory_loaded: bool = False
    memory_size: int = 0
    decisions_made: int = 0
    recent_successes: int = 0
    recent_failures: int = 0
    avg_confidence: float = 0.0
    cycle_number: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "timestamp": self.timestamp,
            "status": self.status,
            "current_strategy": self.current_strategy,
            "memory_loaded": self.memory_loaded,
            "decisions_made": self.decisions_made,
            "recent_successes": self.recent_successes,
            "recent_failures": self.recent_failures
        }


@dataclass
class ObservationData:
    """Dane obserwacji agenta."""
    observation_id: str = field(default_factory=lambda: f"obs_{datetime.now().strftime('%Y%m%d%H%M%S%f')}")
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    agent_id: str = ""
    agent_name: str = ""
    state: AgentStateSnapshot = field(default_factory=AgentStateSnapshot)
    observation_type: str = "routine"
    findings: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    anomalies: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    confidence: float = 0.0
    importance: float = 0.0
    status: ObservationStatus = ObservationStatus.COMPLETED
    error: Optional[str] = None


@dataclass
class AnalysisResult:
    """Wynik analizy zachowania agenta."""
    analysis_id: str = field(default_factory=lambda: f"analysis_{datetime.now().strftime('%Y%m%d%H%M%S%f')}")
    observation_ids: List[str] = field(default_factory=list)
    agent_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    analysis_type: str = "comprehensive"
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    decision_quality: float = 0.0
    decision_confidence: float = 0.0
    decision_accuracy: float = 0.0
    overall_score: float = 0.0
    grade: str = "C"
    behavior_patterns: List[str] = field(default_factory=list)
    behavior_anomalies: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    priority_recommendations: List[str] = field(default_factory=list)
    improvement_areas: List[str] = field(default_factory=list)
    overall_feedback: str = ""


@dataclass
class TeachingSession:
    """Sesja nauczania agenta."""
    session_id: str = field(default_factory=lambda: f"session_{datetime.now().strftime('%Y%m%d%H%M%S%f')}")
    agent_id: str = ""
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None
    duration_seconds: float = 0.0
    analysis_id: Optional[str] = None
    session_type: str = "guidance"
    teaching_goal: str = ""
    learning_objectives: List[str] = field(default_factory=list)
    lessons_taught: List[str] = field(default_factory=list)
    understanding_level: float = 0.0
    improvement_achieved: float = 0.0
    status: str = "completed"
    error: Optional[str] = None


@dataclass
class EvaluationResult:
    """Wynik oceny agenta."""
    evaluation_id: str = field(default_factory=lambda: f"eval_{datetime.now().strftime('%Y%m%d%H%M%S%f')}")
    agent_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    period_start: str = ""
    period_end: str = ""
    criteria_scores: Dict[str, float] = field(default_factory=dict)
    performance_score: float = 0.0
    overall_score: float = 0.0
    grade: str = "C"
    percentile: float = 50.0
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    evaluations_count: int = 0


class TeacherEngine:
    """Glowny silnik nauczyciela."""
    
    def __init__(self, config: Optional[TeacherConfig] = None):
        self.config = config or TeacherConfig()
        self._status = TeacherStatus.IDLE
        self._running = False
        self._stop_requested = False
        
        # Dane
        self._agents: Dict[str, Any] = {}
        self._agent_states: Dict[str, AgentStateSnapshot] = {}
        self._observation_history: Dict[str, List[ObservationData]] = {}
        self._analysis_results: Dict[str, List[AnalysisResult]] = {}
        self._teaching_sessions: Dict[str, List[TeachingSession]] = {}
        self._evaluation_results: Dict[str, List[EvaluationResult]] = {}
        
        # Kolejki
        self._observation_queue: python_queue.Queue = python_queue.Queue()
        self._analysis_queue: python_queue.Queue = python_queue.Queue()
        self._teaching_queue: python_queue.Queue = python_queue.Queue()
        self._evaluation_queue: python_queue.Queue = python_queue.Queue()
        
        # Watki
        self._observation_thread: Optional[threading.Thread] = None
        self._analysis_thread: Optional[threading.Thread] = None
        self._teaching_thread: Optional[threading.Thread] = None
        self._evaluation_thread: Optional[threading.Thread] = None
        
        # Czas
        self._last_observation_time: float = 0.0
        self._last_analysis_time: float = 0.0
        self._last_teaching_time: float = 0.0
        self._last_evaluation_time: float = 0.0
        
        # Locki
        self._lock = threading.RLock()
        
        # Statystyki
        self._statistics = {
            "observations_made": 0,
            "analyses_completed": 0,
            "teaching_sessions": 0,
            "evaluations_completed": 0,
            "recommendations_generated": 0,
            "errors": 0
        }
        
        # Integracja
        self._model_memory_store: Optional[Any] = None
        self._llm_queue_manager: Optional[Any] = None
        
        # Logging
        if self.config.debug_mode:
            logger.setLevel(logging.DEBUG)
        
        logger.info(f"Teacher Engine {self.config.name} v{self.config.version} initialized")
    
    def start(self) -> bool:
        """Uruchomienie Teacher Engine."""
        if self._running:
            return False
        
        try:
            self._running = True
            self._stop_requested = False
            self._status = TeacherStatus.OBSERVING
            
            self._start_threads()
            logger.info("Teacher Engine started")
            return True
        except Exception as e:
            logger.error(f"Error starting Teacher Engine: {e}")
            self._running = False
            self._status = TeacherStatus.ERROR
            return False
    
    def stop(self) -> bool:
        """Zatrzymanie Teacher Engine."""
        if not self._running:
            return False
        
        try:
            self._stop_requested = True
            self._running = False
            self._stop_threads()
            self._save_state()
            self._status = TeacherStatus.IDLE
            logger.info("Teacher Engine stopped")
            return True
        except Exception as e:
            logger.error(f"Error stopping Teacher Engine: {e}")
            self._status = TeacherStatus.ERROR
            return False
    
    def _start_threads(self) -> None:
        """Uruchomienie watkow pracy."""
        self._observation_thread = threading.Thread(target=self._observation_loop, daemon=True)
        self._observation_thread.start()
        
        self._analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        self._analysis_thread.start()
        
        self._teaching_thread = threading.Thread(target=self._teaching_loop, daemon=True)
        self._teaching_thread.start()
        
        self._evaluation_thread = threading.Thread(target=self._evaluation_loop, daemon=True)
        self._evaluation_thread.start()
    
    def _stop_threads(self) -> None:
        """Zatrzymanie watkow pracy."""
        threads = [self._observation_thread, self._analysis_thread, 
                  self._teaching_thread, self._evaluation_thread]
        for thread in threads:
            if thread and thread.is_alive():
                thread.join(timeout=5.0)
    
    # ==================== OBSERWACJA ====================
    
    def _observation_loop(self) -> None:
        """Glowna petla obserwacji."""
        while self._running and not self._stop_requested:
            try:
                current_time = time.time()
                if current_time - self._last_observation_time >= self.config.observation_interval_seconds:
                    self._perform_observation()
                    self._last_observation_time = current_time
                self._process_observation_queue()
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in observation loop: {e}")
                time.sleep(1.0)
    
    def _perform_observation(self) -> None:
        """Wykonywanie obserwacji wszystkich agentow."""
        self._status = TeacherStatus.OBSERVING
        
        with self._lock:
            agents_to_observe = self._get_agents_to_observe()
        
        for agent_id in agents_to_observe:
            try:
                state = self._observe_agent(agent_id)
                if state:
                    observation = self._create_observation(agent_id, state)
                    self._save_observation(observation)
                    self._analysis_queue.put(observation)
                    self._statistics["observations_made"] += 1
                time.sleep(0.01)
            except Exception as e:
                logger.error(f"Error observing agent {agent_id}: {e}")
        
        self._status = TeacherStatus.IDLE
    
    def _get_agents_to_observe(self) -> List[str]:
        """Pobranie listy agentow do obserwacji."""
        if self.config.monitor_all_agents:
            return list(self._agents.keys())
        return self.config.monitored_agent_ids
    
    def _observe_agent(self, agent_id: str) -> Optional[AgentStateSnapshot]:
        """Obserwacja pojedynczego agenta."""
        try:
            agent = self._agents.get(agent_id)
            if not agent:
                return None
            
            snapshot = AgentStateSnapshot(
                agent_id=agent_id,
                status=getattr(agent, '_status', '').name if hasattr(getattr(agent, '_status', ''), 'name') else str(getattr(agent, '_status', '')),
                current_strategy=getattr(agent, '_current_strategy', None),
                memory_loaded=hasattr(agent, 'memory_store') and agent.memory_store is not None,
                decisions_made=getattr(agent, '_decisions_made', 0)
            )
            
            if hasattr(agent, 'memory_store') and agent.memory_store:
                try:
                    stats = agent.memory_store.get_statistics()
                    snapshot.memory_size = stats.get('entry_count', 0)
                except:
                    pass
            
            with self._lock:
                self._agent_states[agent_id] = snapshot
            
            return snapshot
        except Exception as e:
            logger.error(f"Error observing agent {agent_id}: {e}")
            return None
    
    def _create_observation(self, agent_id: str, state: AgentStateSnapshot) -> ObservationData:
        """Utworzenie danych obserwacji."""
        observation = ObservationData(
            agent_id=agent_id,
            agent_name=f"Agent_{agent_id}",
            state=state
        )
        self._analyze_agent_state(observation)
        return observation
    
    def _analyze_agent_state(self, observation: ObservationData) -> None:
        """Poczatkowa analiza stanu agenta."""
        state = observation.state
        
        if state.status and "ERROR" in state.status:
            observation.anomalies.append(f"Agent in ERROR status: {state.status}")
            observation.importance = 0.9
        
        if not state.memory_loaded:
            observation.findings.append("Agent memory not loaded")
            observation.importance = max(observation.importance, 0.7)
        
        total = state.recent_successes + state.recent_failures
        if total > 0:
            success_rate = state.recent_successes / total
            if success_rate < self.config.failure_threshold:
                observation.anomalies.append(f"Low success rate: {success_rate:.2f}")
                observation.importance = max(observation.importance, 0.8)
            elif success_rate > self.config.success_threshold:
                observation.patterns.append(f"High success rate: {success_rate:.2f}")
        
        observation.quality_score = min(1.0, 0.3 + (state.memory_size / 100.0) * 0.2 + state.avg_confidence * 0.5)
        observation.confidence = min(0.95, observation.quality_score * 1.1)
    
    def _save_observation(self, observation: ObservationData) -> None:
        """Zapisanie obserwacji."""
        with self._lock:
            if observation.agent_id not in self._observation_history:
                self._observation_history[observation.agent_id] = []
            self._observation_history[observation.agent_id].append(observation)
            if len(self._observation_history[observation.agent_id]) > 1000:
                self._observation_history[observation.agent_id] = self._observation_history[observation.agent_id][-1000:]
    
    def _process_observation_queue(self) -> None:
        """Przetwarzanie kolejki obserwacji."""
        while not self._observation_queue.empty():
            try:
                self._observation_queue.get_nowait()
            except python_queue.Empty:
                break
    
    # ==================== ANALIZA ====================
    
    def _analysis_loop(self) -> None:
        """Glowna petla analizy."""
        while self._running and not self._stop_requested:
            try:
                current_time = time.time()
                if current_time - self._last_analysis_time >= self.config.analysis_interval_seconds:
                    self._perform_analysis()
                    self._last_analysis_time = current_time
                self._process_analysis_queue()
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in analysis loop: {e}")
                time.sleep(1.0)
    
    def _perform_analysis(self) -> None:
        """Wykonywanie analizy agentow."""
        self._status = TeacherStatus.ANALYZING
        
        with self._lock:
            for agent_id, observations in self._observation_history.items():
                if observations:
                    recent_obs = observations[-10:]
                    if recent_obs:
                        analysis = self._analyze_agent_behavior(agent_id, recent_obs)
                        self._save_analysis(analysis)
                        self._teaching_queue.put(analysis)
                        self._statistics["analyses_completed"] += 1
        
        self._status = TeacherStatus.IDLE
    
    def _analyze_agent_behavior(self, agent_id: str, observations: List[ObservationData]) -> AnalysisResult:
        """Analiza zachowania agenta."""
        success_count = 0
        failure_count = 0
        total_decisions = 0
        confidence_sum = 0.0
        confidence_count = 0
        behavior_patterns: Dict[str, int] = {}
        detected_anomalies: List[str] = []
        
        for obs in observations:
            state = obs.state
            if state.recent_successes > 0 or state.recent_failures > 0:
                success_count += state.recent_successes
                failure_count += state.recent_failures
                total_decisions += state.recent_successes + state.recent_failures
            if state.avg_confidence > 0:
                confidence_sum += state.avg_confidence
                confidence_count += 1
            for pattern in obs.patterns:
                behavior_patterns[pattern] = behavior_patterns.get(pattern, 0) + 1
            detected_anomalies.extend(obs.anomalies)
        
        success_rate = success_count / total_decisions if total_decisions > 0 else 0.0
        avg_confidence = confidence_sum / confidence_count if confidence_count > 0 else 0.0
        
        analysis = AnalysisResult(
            agent_id=agent_id,
            observation_ids=[obs.observation_id for obs in observations],
            performance_metrics={
                "success_rate": success_rate,
                "failure_rate": 1.0 - success_rate,
                "avg_confidence": avg_confidence,
                "total_decisions": total_decisions
            },
            decision_quality=min(1.0, success_rate * avg_confidence * 1.2),
            decision_confidence=avg_confidence,
            decision_accuracy=success_rate,
            overall_score=min(100.0, (success_rate * 40) + (avg_confidence * 30) + ((len(behavior_patterns) / 10) * 30)),
            grade=self._calculate_grade(success_rate, avg_confidence),
            behavior_patterns=list(behavior_patterns.keys()),
            behavior_anomalies=detected_anomalies,
            recommendations=self._generate_recommendations(agent_id, success_rate, avg_confidence)
        )
        analysis.overall_feedback = self._generate_feedback(analysis)
        return analysis
    
    def _calculate_grade(self, success_rate: float, avg_confidence: float) -> str:
        """Obliczenie oceny (A-E)."""
        score = (success_rate * 0.7) + (avg_confidence * 0.3)
        if score >= 0.9: return "A"
        elif score >= 0.8: return "B"
        elif score >= 0.7: return "C"
        elif score >= 0.6: return "D"
        else: return "E"
    
    def _generate_recommendations(self, agent_id: str, success_rate: float, avg_confidence: float) -> List[str]:
        """Generowanie rekomendacji."""
        recommendations = []
        if success_rate < self.config.success_threshold:
            recommendations.append("Focus on improving decision accuracy")
        if avg_confidence < 0.7:
            recommendations.append("Increase confidence level")
        if success_rate > self.config.success_threshold and avg_confidence > 0.8:
            recommendations.append("Consider testing new strategies")
        recommendations.append(f"Maintain current performance (success: {success_rate:.2f}, confidence: {avg_confidence:.2f})")
        return recommendations
    
    def _generate_feedback(self, analysis: AnalysisResult) -> str:
        """Generowanie feedbacku."""
        if analysis.grade == "A": return f"Excellent! Score: {analysis.overall_score:.1f}/100"
        elif analysis.grade == "B": return f"Good! Score: {analysis.overall_score:.1f}/100"
        elif analysis.grade == "C": return f"Average. Score: {analysis.overall_score:.1f}/100"
        elif analysis.grade == "D": return f"Below average. Score: {analysis.overall_score:.1f}/100"
        else: return f"Poor. Score: {analysis.overall_score:.1f}/100"
    
    def _save_analysis(self, analysis: AnalysisResult) -> None:
        """Zapisanie analizy."""
        with self._lock:
            if analysis.agent_id not in self._analysis_results:
                self._analysis_results[analysis.agent_id] = []
            self._analysis_results[analysis.agent_id].append(analysis)
            if len(self._analysis_results[analysis.agent_id]) > 100:
                self._analysis_results[analysis.agent_id] = self._analysis_results[analysis.agent_id][-100:]
    
    def _process_analysis_queue(self) -> None:
        """Przetwarzanie kolejki analiz."""
        while not self._analysis_queue.empty():
            try:
                self._analysis_queue.get_nowait()
            except python_queue.Empty:
                break
    
    # ==================== NAUCZANIE ====================
    
    def _teaching_loop(self) -> None:
        """Glowna petla nauczania."""
        while self._running and not self._stop_requested:
            try:
                current_time = time.time()
                if current_time - self._last_teaching_time >= self.config.teaching_interval_seconds:
                    self._perform_teaching()
                    self._last_teaching_time = current_time
                self._process_teaching_queue()
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in teaching loop: {e}")
                time.sleep(1.0)
    
    def _perform_teaching(self) -> None:
        """Wykonywanie nauczania agentow."""
        self._status = TeacherStatus.TEACHING
        
        with self._lock:
            for agent_id, analyses in self._analysis_results.items():
                if analyses:
                    latest_analysis = analyses[-1]
                    if self._should_teach_agent(latest_analysis):
                        session = self._create_teaching_session(agent_id, latest_analysis)
                        self._save_teaching_session(session)
                        self._statistics["teaching_sessions"] += 1
                        self._statistics["recommendations_generated"] += len(session.recommendations)
        
        self._status = TeacherStatus.IDLE
    
    def _should_teach_agent(self, analysis: AnalysisResult) -> bool:
        """Decyzja czy nauczyc agenta."""
        if analysis.grade in ["D", "E"]:
            return True
        if analysis.priority_recommendations:
            return True
        if analysis.grade == "C" and (hash(analysis.agent_id) % 10) < 3:
            return True
        if analysis.grade == "B" and (hash(analysis.agent_id) % 10) == 0:
            return True
        return False
    
    def _create_teaching_session(self, agent_id: str, analysis: AnalysisResult) -> TeachingSession:
        """Utworzenie sesji nauczania."""
        if analysis.grade in ["D", "E"]:
            session_type = "correction"
            teaching_goal = "Improve performance"
        elif analysis.grade == "C":
            session_type = "guidance"
            teaching_goal = "Reach good performance"
        else:
            session_type = "guidance"
            teaching_goal = "Maintain performance"
        
        lessons = self._generate_lessons(analysis)
        
        return TeachingSession(
            agent_id=agent_id,
            session_type=session_type,
            teaching_goal=teaching_goal,
            learning_objectives=analysis.improvement_areas,
            analysis_id=analysis.analysis_id,
            observation_ids=analysis.observation_ids,
            lessons_taught=lessons,
            recommendations=analysis.recommendations + analysis.priority_recommendations,
            methods_used=[session_type, "feedback"]
        )
    
    def _generate_lessons(self, analysis: AnalysisResult) -> List[str]:
        """Generowanie lekcji."""
        lessons = []
        if analysis.grade == "E":
            lessons.extend(["Review basic decision-making principles", "Analyze recent failures"])
        elif analysis.grade == "D":
            lessons.extend(["Focus on improving success rate", "Review strategy selection"])
        elif analysis.grade == "C":
            lessons.extend(["Review successful patterns", "Analyze decision confidence"])
        else:
            lessons.extend(["Refine successful strategies", "Explore new approaches"])
        return lessons[:5]
    
    def _save_teaching_session(self, session: TeachingSession) -> None:
        """Zapisanie sesji nauczania."""
        with self._lock:
            if session.agent_id not in self._teaching_sessions:
                self._teaching_sessions[session.agent_id] = []
            self._teaching_sessions[session.agent_id].append(session)
            if len(self._teaching_sessions[session.agent_id]) > 50:
                self._teaching_sessions[session.agent_id] = self._teaching_sessions[session.agent_id][-50:]
    
    def _process_teaching_queue(self) -> None:
        """Przetwarzanie kolejki nauczania."""
        while not self._teaching_queue.empty():
            try:
                self._teaching_queue.get_nowait()
            except python_queue.Empty:
                break
    
    # ==================== OCENA ====================
    
    def _evaluation_loop(self) -> None:
        """Glowna petla oceny."""
        while self._running and not self._stop_requested:
            try:
                current_time = time.time()
                if current_time - self._last_evaluation_time >= self.config.evaluation_interval_seconds:
                    self._perform_evaluation()
                    self._last_evaluation_time = current_time
                self._process_evaluation_queue()
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in evaluation loop: {e}")
                time.sleep(1.0)
    
    def _perform_evaluation(self) -> None:
        """Wykonywanie oceny agentow."""
        self._status = TeacherStatus.EVALUATING
        
        with self._lock:
            for agent_id in self._get_agents_to_observe():
                analyses = self._analysis_results.get(agent_id, [])
                sessions = self._teaching_sessions.get(agent_id, [])
                if analyses:
                    evaluation = self._evaluate_agent(agent_id, analyses, sessions)
                    self._save_evaluation(evaluation)
                    self._statistics["evaluations_completed"] += 1
        
        self._status = TeacherStatus.IDLE
    
    def _evaluate_agent(self, agent_id: str, analyses: List[AnalysisResult], sessions: List[TeachingSession]) -> EvaluationResult:
        """Ocena pojedynczego agenta."""
        total_score = 0.0
        count = 0
        grades = []
        
        for analysis in analyses[-5:]:
            total_score += analysis.overall_score
            count += 1
            grades.append(analysis.grade)
        
        avg_score = total_score / count if count > 0 else 0.0
        grade = self._calculate_overall_grade(grades)
        
        return EvaluationResult(
            agent_id=agent_id,
            criteria_scores={"performance": min(100.0, (avg_score / 100.0) * 100)},
            overall_score=min(100.0, avg_score),
            grade=grade,
            percentile=50.0,
            recommendations=[f"Goal: achieve {grade} to {self._next_grade(grade)} level"],
            evaluations_count=count
        )
    
    def _calculate_overall_grade(self, grades: List[str]) -> str:
        """Obliczenie ogolnej oceny."""
        if not grades:
            return "C"
        grade_values = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1}
        total = sum(grade_values.get(g, 3) for g in grades)
        avg = total / len(grades)
        if avg >= 4.5: return "A"
        elif avg >= 3.5: return "B"
        elif avg >= 2.5: return "C"
        elif avg >= 1.5: return "D"
        else: return "E"
    
    def _next_grade(self, current: str) -> str:
        """Nastepna klasa."""
        grades = ["E", "D", "C", "B", "A"]
        try:
            idx = grades.index(current)
            return grades[min(idx + 1, len(grades) - 1)]
        except:
            return "C"
    
    def _save_evaluation(self, evaluation: EvaluationResult) -> None:
        """Zapisanie oceny."""
        with self._lock:
            if evaluation.agent_id not in self._evaluation_results:
                self._evaluation_results[evaluation.agent_id] = []
            self._evaluation_results[evaluation.agent_id].append(evaluation)
            if len(self._evaluation_results[evaluation.agent_id]) > 20:
                self._evaluation_results[evaluation.agent_id] = self._evaluation_results[evaluation.agent_id][-20:]
    
    def _process_evaluation_queue(self) -> None:
        """Przetwarzanie kolejki oceny."""
        while not self._evaluation_queue.empty():
            try:
                self._evaluation_queue.get_nowait()
            except python_queue.Empty:
                break
    
    # ==================== INTEGRACJA ====================
    
    def register_agents(self, agents: Dict[str, Any]) -> None:
        """Rejestracja agentow."""
        with self._lock:
            self._agents = agents.copy()
            for agent_id in agents.keys():
                for prop in ['_observation_history', '_analysis_results', '_teaching_sessions', '_evaluation_results']:
                    if agent_id not in getattr(self, prop):
                        getattr(self, prop)[agent_id] = []
        logger.info(f"Registered {len(agents)} agents")
    
    def register_agent(self, agent_id: str, agent: Any) -> None:
        """Rejestracja pojedynczego agenta."""
        with self._lock:
            self._agents[agent_id] = agent
            for prop in ['_observation_history', '_analysis_results', '_teaching_sessions', '_evaluation_results']:
                if agent_id not in getattr(self, prop):
                    getattr(self, prop)[agent_id] = []
        logger.info(f"Registered agent {agent_id}")
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Pobranie statusu agenta."""
        with self._lock:
            state = self._agent_states.get(agent_id)
        
        if not state:
            return {"agent_id": agent_id, "error": "Not observed yet"}
        
        observations = self._observation_history.get(agent_id, [])
        analyses = self._analysis_results.get(agent_id, [])
        evaluations = self._evaluation_results.get(agent_id, [])
        
        latest_analysis = analyses[-1] if analyses else None
        latest_evaluation = evaluations[-1] if evaluations else None
        
        return {
            "agent_id": agent_id,
            "current_state": state.to_dict(),
            "observations_count": len(observations),
            "analyses_count": len(analyses),
            "evaluations_count": len(evaluations),
            "latest_analysis": latest_analysis.to_dict() if latest_analysis else None,
            "latest_evaluation": latest_evaluation.to_dict() if latest_evaluation else None,
            "overall_grade": latest_evaluation.grade if latest_evaluation else "N/A"
        }
    
    def set_model_memory_store(self, store: Any) -> None:
        """Ustawienie storagu pamieci modeli."""
        self._model_memory_store = store
    
    def get_statistics(self) -> Dict[str, Any]:
        """Pobranie statystyk."""
        return {
            "status": self._status.name,
            "running": self._running,
            "statistics": self._statistics.copy(),
            "agents_monitored": len(self._agents)
        }
    
    def _save_state(self) -> None:
        """Zapis stanu."""
        try:
            state = {"statistics": self._statistics, "agent_states": {k: v.to_dict() for k, v in self._agent_states.items()}}
            os.makedirs("data", exist_ok=True)
            with open(os.path.join("data", "teacher_engine_state.json"), 'w') as f:
                json.dump(state, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving state: {e}")


_default_teacher: Optional[TeacherEngine] = None
_teacher_lock = threading.Lock()


def create_teacher_engine(config: Optional[TeacherConfig] = None, auto_start: bool = True) -> TeacherEngine:
    """Tworzenie Teacher Engine."""
    engine = TeacherEngine(config=config)
    if auto_start:
        engine.start()
    return engine


def get_teacher_engine() -> TeacherEngine:
    """Pobranie instancji Teacher Engine (singleton)."""
    global _default_teacher
    with _teacher_lock:
        if _default_teacher is None:
            _default_teacher = create_teacher_engine()
        return _default_teacher
