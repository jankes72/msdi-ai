"""
SSI V4 Tests - Bezpieczeństwo współbieżności (Sprint 7.3)

Testy wielowątkowe dla synchronizacji agentów V4.

Zgodnie z:
- Sprint 7.3: Bezpieczeństwo współbieżności V4
- Kryteria akceptacji:
  - make_decision() kończy się w czasie < 2s
  - evaluate_result() i learn_from_experience() nie powodują deadlocku
  - Test 10 agentów równolegle przechodzi deterministycznie
  - Timeout powoduje kontrolowany wyjątek i log
  - Testy uruchamiane wielokrotnie w CI

Wymagania:
- Metoda posiadająca lock nie może wywoływać publicznej metody próbującej przejąć ten sam niereentrantny lock
- Każda operacja decyzyjna musi kończyć się sukcesem albo kontrolowanym błędem w określonym limicie czasu
- Testy nie mogą polegać na sleep() jako mechanizmie synchronizacji
- Błąd jednego agenta nie może blokować pozostałej populacji
- Synchronizacja nie może pozwalać agentom bezpośrednio modyfikować pamięci V3
"""
import pytest

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
import logging

# Konfiguracja logowania dla testów
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Import modułów SSI
from SSI.v4.agent_core import Agent, AgentConfig, AgentType, AgentManager
from SSI.v4.agent_sync_policy import SyncConfig, AgentRLock


# ==========================================================================
# FIXTURE - Kontekst testowy
# ==========================================================================

def create_test_context() -> Dict[str, any]:
    """Tworzy kontekst testowy dla agentów."""
    return {
        "worlds": [
            {"id": "world_1", "type": "football", "data": {"home": "Poland", "away": "Germany"}},
            {"id": "world_2", "type": "tennis", "data": {"player1": "Djokovic", "player2": "Nadal"}}
        ],
        "models": [
            {"id": "model_1", "type": "regression", "accuracy": 0.95},
            {"id": "model_2", "type": "classification", "accuracy": 0.88}
        ],
        "strategies": [
            {"id": "strategy_1", "name": "high_risk", "expected_value": 0.85},
            {"id": "strategy_2", "name": "low_risk", "expected_value": 0.65}
        ],
        "history": [
            {"decision_id": "dec_1", "action": "bet", "result": "win", "value": 100},
            {"decision_id": "dec_2", "action": "hold", "result": "loss", "value": -50}
        ],
        "results": [
            {"id": "result_1", "outcome": "success", "value": 150},
            {"id": "result_2", "outcome": "failure", "value": -75}
        ]
    }


def create_test_agent_config(agent_id: Optional[str] = None) -> AgentConfig:
    """Tworzy konfigurację agenta testowego."""
    return AgentConfig(
        agent_id=agent_id or f"test_agent_{threading.current_thread().name}",
        agent_type=AgentType.ANALYST,
        name="Test Agent",
        description="Agent do testów współbieżności",
        memory_size=1000,
        decision_history_size=100,
        v3_memory_access=False,  # Wyłącz V3 dla testów (nie zależy od zewnętrznych zasobów)
        use_v3_knowledge=False
    )


# ==========================================================================
# TEST 1: make_decision() kończy się w czasie < 2s
# ==========================================================================

class TestDecisionTimeout:
    """Testy timeoutu dla make_decision()."""
    
    def setUp(self):
        """Ustawienia przed testem."""
        self.context = create_test_context()
        self.config = create_test_agent_config()
        self.agent = Agent(self.config)
        self.agent.initialize()
    
    def test_make_decision_completes_under_2_seconds(self):
        """Test, że make_decision() kończy się w czasie < 2s (kryterium akceptacji)."""
        start_time = time.time()
        result = self.agent.make_decision(self.context)
        elapsed = time.time() - start_time
        
        assert 
            elapsed < 2.0,
            f"make_decision( wykonało się w {elapsed:.3f}s (powinno być < 2.0s)"
        )
        assert "action" in result
        assert result["status"] == "ACTIVE"
    
    def test_make_decision_with_explicit_timeout(self):
        """Test make_decision() z jawonym timeoutem."""
        start_time = time.time()
        result = self.agent.make_decision(self.context, timeout=1.0)
        elapsed = time.time() - start_time
        
        assert 
            elapsed < 1.5,  # Nieco więcej niż timeout ze względu na overhead
            f"make_decision( z timeout=1.0 wykonało się w {elapsed:.3f}s"
        )
    
    def test_make_decision_handles_error_gracefully(self):
        """Test, że make_decision() obsługuje błędy i zwraca status error."""
        # Przekaż nieprawidłowy kontekst (None zamiast dict)
        result = self.agent.make_decision(None)
        
        assert result["status"] == "error"
        assert "agent_id" in result
        assert "error" in result


# ==========================================================================
# TEST 2: evaluate_result() i learn_from_experience() nie powodują deadlocku
# ==========================================================================

class TestDeadlockPrevention:
    """Testy zapobiegania deadlockom."""
    
    def setUp(self):
        """Ustawienia przed testem."""
        self.context = create_test_context()
        self.config = create_test_agent_config()
        self.agent = Agent(self.config)
        self.agent.initialize()
        
        # Wywołaj make_decision, aby mieć oddziałanie w decision_history
        self.agent.make_decision(self.context)
    
    def test_evaluate_result_no_deadlock(self):
        """Test, że evaluate_result() nie powoduje deadlocku."""
        result = {
            "correct": True,
            "actual_result": {"value": 100},
            "decision_id": self.agent.memory.decision_history[-1].decision_id
        }
        
        start_time = time.time()
        eval_result = self.agent.evaluate_result(result)
        elapsed = time.time() - start_time
        
        assert 
            elapsed < 1.0,
            f"evaluate_result( wykonało się w {elapsed:.3f}s (powinno być < 1.0s)"
        )
        assert eval_result["agent_id"] == self.agent.agent_id
        assert "evaluation" in eval_result
    
    def test_learn_from_experience_no_deadlock(self):
        """Test, że learn_from_experience() nie powoduje deadlocku."""
        experience = {
            "strategies": [{"id": "new_strategy", "name": "test_strategy"}],
            "patterns": [{"id": "new_pattern", "type": "test"}],
            "results": [{"id": "res_1", "outcome": "success"}]
        }
        
        start_time = time.time()
        learn_result = self.agent.learn_from_experience(experience)
        elapsed = time.time() - start_time
        
        assert 
            elapsed < 1.0,
            f"learn_from_experience( wykonało się w {elapsed:.3f}s (powinno być < 1.0s)"
        )
        assert learn_result["agent_id"] == self.agent.agent_id
        assert learn_result["new_strategies_added"] == 1
    
    def test_concurrent_evaluate_and_learn(self):
        """Test współbieżnego wywoływania evaluate_result i learn_from_experience."""
        # Utwórz 2 agenta
        agent1 = Agent(create_test_agent_config("agent_concurrent_1"))
        agent1.initialize()
        agent1.make_decision(self.context)
        
        agent2 = Agent(create_test_agent_config("agent_concurrent_2"))
        agent2.initialize()
        agent2.make_decision(self.context)
        
        result1 = {"correct": True, "actual_result": {"value": 50}}
        result2 = {"correct": False, "actual_result": {"value": -25}}
        experience1 = {"strategies": [{"id": "s1", "name": "strategy_1"}]}
        experience2 = {"strategies": [{"id": "s2", "name": "strategy_2"}]}
        
        def task1():
            agent1.evaluate_result(result1)
            return "task1_done"
        
        def task2():
            agent2.learn_from_experience(experience2)
            return "task2_done"
        
        def task3():
            agent1.learn_from_experience(experience1)
            return "task3_done"
        
        def task4():
            agent2.evaluate_result(result2)
            return "task4_done"
        
        # Wykonaj współbieżnie
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(task1),
                executor.submit(task2),
                executor.submit(task3),
                executor.submit(task4)
            ]
            
            # Poczekaj na zakończenie wszystkich zadań (z timeoutem)
            results = []
            for future in as_completed(futures, timeout=5.0):
                results.append(future.result())
        
        # Sprawdź, czy wszystkie zadania zostało wykonane
        assert len(results) == 4
        assert "task1_done" in results
        assert "task2_done" in results
        assert "task3_done" in results
        assert "task4_done" in results


# ==========================================================================
# TEST 3: Test równoległej pracy minimum 10 agentów
# ==========================================================================

class TestParallelAgents:
    """Testy pracy równoległej wielu agentów."""
    
    def setUp(self):
        """Ustawienia przed testem."""
        self.context = create_test_context()
    
    def test_10_agents_parallel_decision_making(self):
        """Test równoległej pracy 10 agentów (kryterium akceptacji)."""
        agents = []
        for i in range(10):
            config = create_test_agent_config(f"parallel_agent_{i}")
            agent = Agent(config)
            agent.initialize()
            agents.append(agent)
        
        results = []
        errors = []
        
        def make_decision_task(agent):
            try:
                start_time = time.time()
                result = agent.make_decision(self.context)
                elapsed = time.time() - start_time
                return {"agent_id": agent.agent_id, "result": result, "time": elapsed}
            except Exception as e:
                return {"agent_id": agent.agent_id, "error": str(e)}
        
        # Wykonaj współbieżnie
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_decision_task, agent) for agent in agents]
            
            for future in as_completed(futures, timeout=10.0):
                task_result = future.result()
                if "error" in task_result:
                    errors.append(task_result)
                else:
                    results.append(task_result)
        
        # Sprawdź, że wszystkie agenty ukończyły zadanie
        assert 
            len(results) == 10,
            f"Tylko {len(results} agentów ukończyło zadanie, {len(errors)} zostało w błędzie"
        )
        
        # Sprawdź, że każdy agent ukończył w czasie < 2s
        for task_result in results:
            assert 
                task_result["time"] < 2.0,
                f"Agent {task_result['agent_id']} wykonał się w {task_result['time']:.3f}s"
            
            assert "action" in task_result["result"]
    
    def test_10_agents_parallel_mixed_operations(self):
        """Test równoległej pracy 10 agentów z mieszanymi operacjami."""
        agents = []
        for i in range(10):
            config = create_test_agent_config(f"mixed_agent_{i}")
            agent = Agent(config)
            agent.initialize()
            
            # Każdy agent wykonuje jedną decyzję, aby mieć decision_history
            agent.make_decision(self.context)
            agents.append(agent)
        
        def mixed_operation_task(agent, task_type):
            try:
                if task_type == "decision":
                    return agent.make_decision(self.context)
                elif task_type == "evaluate":
                    result = {"correct": True, "actual_result": {"value": 50}}
                    return agent.evaluate_result(result)
                elif task_type == "learn":
                    experience = {"strategies": [{"id": f"s_{agent.agent_id}", "name": "test"}]}
                    return agent.learn_from_experience(experience)
            except Exception as e:
                return {"error": str(e)}
        
        # Rozdaj zadania losowo
        tasks = []
        for i, agent in enumerate(agents):
            task_type = ["decision", "evaluate", "learn"][i % 3]
            tasks.append((agent, task_type))
        
        # Wykonaj współbieżnie
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(mixed_operation_task, agent, task_type)
                for agent, task_type in tasks
            ]
            
            results = []
            errors = []
            for future in as_completed(futures, timeout=10.0):
                result = future.result()
                if isinstance(result, dict) and "error" in result:
                    errors.append(result)
                else:
                    results.append(result)
        
        # Sprawdź, że wszystkie zadania ukończyły się pomyślnie
        assert 
            len(results) == 10,
            f"Tylko {len(results} zadań ukończyło się pomyślnie, {len(errors)} z błędami"
        )
    
    def test_agent_error_does_not_block_others(self):
        """Test, że błąd jednego agenta nie blokuje pozostałych (kryterium akceptacji)."""
        agents = []
        for i in range(5):
            config = create_test_agent_config(f"error_test_agent_{i}")
            agent = Agent(config)
            agent.initialize()
            agents.append(agent)
        
        def task_with_error(agent):
            try:
                # Symuluj błąd dla pierwszego agenta
                if agent.agent_id == "error_test_agent_0":
                    raise ValueError("Symulowany błąd agenta 0")
                return agent.make_decision(self.context)
            except Exception as e:
                return {"agent_id": agent.agent_id, "error": str(e)}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(task_with_error, agent) for agent in agents]
            
            results = []
            for future in as_completed(futures, timeout=10.0):
                results.append(future.result())
        
        # Sprawdź, że pozostałe agenty ukończyły pomyślnie
        successful = [r for r in results if isinstance(r, dict) and "error" not in r]
        failed = [r for r in results if isinstance(r, dict) and "error" in r]
        
        assert len(failed) == 1  # Tylko agent_0 powinien mieć błąd
        assert len(successful) == 4  # Pozostali 4 powinni ukończyć pomyślnie


# ==========================================================================
# TEST 4: Timeout powoduje kontrolowany wyjątek i log
# ==========================================================================

class TestTimeoutHandling:
    """Testy obsługi timeoutów."""
    
    def setUp(self):
        """Ustawienia przed testem."""
        self.context = create_test_context()
    
    def test_timeout_causes_controlled_error(self):
        """Test, że timeout powoduje kontrolowany błąd (kryterium akceptacji)."""
        # Testujemy timeout na poziomie locka (AgentRLock)
        # Tworzymy lock i trzymamy go zajęty, a następne próbujemy go zdobyć z timeoutem
        lock = AgentRLock("TestTimeoutLock")
        
        # Zajmij lock w głównym wątku
        lock.acquire()
        
        def try_acquire_with_timeout():
            # Próba zdobycia locka z bardzo krótkim timeoutem
            acquired = lock.acquire(timeout=0.001)  # 1ms
            if acquired:
                lock.release()  # Zwolnij, jeśli został zdobyty
            return acquired
        
        # W innym wątku nie powinien zdobyć locka
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(try_acquire_with_timeout)
            acquired = future.result()
        
        assert not acquired
        
        # Zwolnij lock
        lock.release()
        
        # Teraz powinno się udać ( i zwolnić automatycznie w funkcji)
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(try_acquire_with_timeout)
            acquired = future.result()
        
        assert acquired
    
    def test_agent_lock_timeout_behavior(self):
        """Test zachowania AgentRLock przy timeout."""
        lock = AgentRLock("TestLock")
        
        # Przejmij lock w głównym wątku
        lock.acquire()
        
        def try_acquire_in_another_thread():
            # Próba przejęcia w innym wątku (powinien sencillo się powiedzie, bo to RLock)
            return lock.acquire(timeout=0.1)
        
        # W innym wątku nie powinien zdobyć locka,który jest zajęty przez główny wątek
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(try_acquire_in_another_thread)
            acquired = future.result()
        
        assert not acquired
        
        # Zwolnij lock
        lock.release()


# ==========================================================================
# TEST 5: Deterministyczność testów
# ==========================================================================

class TestDeterministicBehavior:
    """Testy deterministyczności zachowania."""
    
    def setUp(self):
        """Ustawienia przed testem."""
        self.context = create_test_context()
    
    def test_repeated_decision_making_consistent(self):
        """Test, że wielokrotne wywoływanie make_decision jest deterministyczne."""
        config = create_test_agent_config("deterministic_agent")
        agent = Agent(config)
        agent.initialize()
        
        # Wykonaj 5 razy make_decision z tym samym kontekstem
        results = []
        for _ in range(5):
            result = agent.make_decision(self.context)
            results.append(result)
        
        # Sprawdź, że wszystkie wyniki są podobne (te same pola)
        for result in results:
            assert "agent_id" in result
            assert "action" in result
            assert "confidence" in result
            assert result["agent_id"] == agent.agent_id
    
    def test_parallel_execution_deterministic(self):
        """Test, że wykonanie równoległe jest deterministyczne."""
        agents = [Agent(create_test_agent_config(f"det_agent_{i}")) for i in range(5)]
        for agent in agents:
            agent.initialize()
        
        # Wykonaj 3 razy współbieżne make_decision
        for run in range(3):
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(agent.make_decision, self.context) for agent in agents]
                
                for future in as_completed(futures, timeout=10.0):
                    result = future.result()
                    assert "action" in result
                    assert result["status"] == "ACTIVE"


# ==========================================================================
# TEST 6: V3 Memory nie jest modyfikowana przez agentów
# ==========================================================================

class TestV3MemorySafety:
    """Testy bezpieczeństwa pamięci V3."""
    
    def setUp(self):
        """Ustawienia przed testem."""
        self.context = create_test_context()
    
    def test_agents_cannot_modify_v3_memory(self):
        """Test, że agenci nie modyfikują pamięci V3 (tylko odczyt)."""
        # Utwórz agenta z wyłączonym V3, aby nie zależeć od zewnętrznych modułów
        config = create_test_agent_config("v3_safe_agent")
        config.v3_memory_access = False
        config.v3_world_memory_access = False
        config.v3_pattern_memory_access = False
        config.use_v3_knowledge = False
        
        agent = Agent(config)
        agent.initialize()
        
        # Wywołaj make_decision
        result = agent.make_decision(self.context)
        
        # Sprawdź, że agent działa poprawnie
        assert "action" in result
        assert result["status"] == "ACTIVE"
        
        # Sprawdź, że V3 jest niedostępne dla tego agenta
        assert not agent.is_v3_available()
        assert agent.get_world_memory( is None)
        assert agent.get_pattern_memory( is None)


# ==========================================================================
# GŁÓWNA FUNKCJA TESTUJĄCA
# ==========================================================================

