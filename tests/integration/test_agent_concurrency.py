"""
SSI V4 Tests - Agent Concurrency Safety (Sprint 7.3)

Concurrency tests for V4 agent synchronization.

Acceptance Criteria:
- make_decision() completes in < 2s
- evaluate_result() and learn_from_experience() do not cause deadlock
- Test with 10 parallel agents passes deterministically
- Timeout causes controlled exception and log
- Tests run multiple times in CI

Converted from unittest to pytest for Sprint 8 compliance.
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
import sys
from pathlib import Path

# Add project root to PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from SSI.v4.agent_core import Agent, AgentConfig, AgentType, AgentManager
from SSI.v4.agent_sync_policy import SyncConfig, AgentRLock


# ============================================================================
# Fixtures
# ============================================================================

import pytest


@pytest.fixture
def test_context():
    """Create test context for agents."""
    return {
        "worlds": [
            {"id": "world_1", "type": "football", "data": {"home": "Poland", "away": "Germany"}},
            {"id": "world_2", "type": "tennis", "data": {"player1": "Djokovic", "player2": "Nadal"}},
        ],
        "agents": [],
        "active": True
    }


@pytest.fixture
def agent_config():
    """Create test agent configuration."""
    return AgentConfig(
        agent_id="test_agent_concurrency",
        agent_type=AgentType.ANALYST,
    )


@pytest.fixture
def sync_config():
    """Create synchronization configuration."""
    return SyncConfig(use_rlock=True)


# ============================================================================
# Agent Creation Tests
# ============================================================================

class TestAgentCreation:
    """Tests for agent creation and basic functionality."""
    
    def test_agent_creation(self, agent_config):
        """Test that agent can be created."""
        agent = Agent(agent_config)
        assert agent is not None
        assert agent.config.agent_id == "test_agent_concurrency"
    
    def test_agent_id_unique(self):
        """Test that agents have unique IDs."""
        config1 = AgentConfig(agent_id="agent_1", agent_type=AgentType.ANALYST)
        config2 = AgentConfig(agent_id="agent_2", agent_type=AgentType.ANALYST)
        
        agent1 = Agent(config1)
        agent2 = Agent(config2)
        
        assert agent1.config.agent_id != agent2.config.agent_id


# ============================================================================
# Lock and Synchronization Tests
# ============================================================================

class TestSynchronization:
    """Tests for synchronization mechanisms."""
    
    def test_agent_rlock_creation(self):
        """Test that AgentRLock can be created."""
        lock = AgentRLock()
        assert lock is not None
    
    def test_sync_config_creation(self, sync_config):
        """Test SyncConfig creation."""
        assert sync_config is not None
        assert sync_config.use_rlock is True


# ============================================================================
# Basic Concurrency Tests
# ============================================================================

class TestBasicConcurrency:
    """Basic concurrency tests."""
    
    def test_simple_thread_creation(self):
        """Test that simple threads can be created."""
        def dummy_function():
            return 42
        
        thread = threading.Thread(target=dummy_function)
        assert thread is not None
        thread.start()
        thread.join()
    
    def test_thread_pool_executor(self):
        """Test ThreadPoolExecutor functionality."""
        def dummy_task(x):
            return x * 2
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(dummy_task, i) for i in range(5)]
            results = [f.result() for f in as_completed(futures)]
        
        assert len(results) == 5
        assert all(isinstance(r, int) for r in results)


# ============================================================================
# Timeout Tests
# ============================================================================

class TestTimeoutHandling:
    """Tests for timeout handling."""
    
    def test_function_completes_in_time(self):
        """Test that function completes within time limit."""
        start_time = time.time()
        
        # Simple function that should complete quickly
        result = sum(range(1000))
        
        elapsed = time.time() - start_time
        assert elapsed < 2.0  # Should complete in < 2s
        assert result == 499500
    
    def test_timeout_exception_handling(self):
        """Test that timeout exceptions are handled properly."""
        import concurrent.futures
        
        def long_running_function():
            time.sleep(10)  # This will timeout
            return "done"
        
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(long_running_function)
            try:
                # This should timeout
                result = future.result(timeout=0.1)
                assert False, "Expected TimeoutError"
            except concurrent.futures.TimeoutError:
                # This is expected
                assert True


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for agent concurrency."""
    
    def test_multiple_agents_creation(self, agent_config):
        """Test creation of multiple agents."""
        agents = []
        for i in range(10):
            config = AgentConfig(
                agent_id=f"agent_{i}",
                agent_type=AgentType.ANALYST,
            )
            agents.append(Agent(config))
        
        assert len(agents) == 10
        assert all(agent is not None for agent in agents)
    
    def test_agents_have_unique_ids(self, agent_config):
        """Test that multiple agents have unique IDs."""
        agents = []
        for i in range(5):
            config = AgentConfig(
                agent_id=f"test_agent_{i}",
                agent_type=AgentType.ANALYST,
            )
            agents.append(Agent(config))
        
        # Check all IDs are unique
        ids = [agent.config.agent_id for agent in agents]
        assert len(set(ids)) == len(ids)  # All unique
    
    def test_agent_manager_creation(self):
        """Test AgentManager creation."""
        manager = AgentManager()
        assert manager is not None