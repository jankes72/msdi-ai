#!/usr/bin/env python
# Weryfikacja integracji Pipeline + AgentRuntimeManager
import sys
sys.path.insert(0, 'D:/sts/aplikacjaTyperBetAi')

from SSI_V5.core.pipeline import SSIPipeline, PipelineMode
from SSI_V5.agents import AgentRuntimeManager

def test_pipeline_agent_runtime_manager():
    """Test że Pipeline używa AgentRuntimeManager"""
    print("=" * 80)
    print("TEST: Pipeline + AgentRuntimeManager Integration")
    print("=" * 80)
    
    # 1. Tworzenie Pipeline z use_agent_runtime_manager=True (domyślne)
    pipeline = SSIPipeline(
        mode=PipelineMode.TEST,
        world_name="TEST_INTEGRATION",
        use_agent_runtime_manager=True
    )
    
    # 2. Inicjalizacja
    init_result = pipeline.initialize()
    print(f"\n[1] Pipeline initialization: {init_result['status']}")
    
    if init_result['status'] != 'success':
        print(f"ERROR: {init_result.get('error')}")
        return False
    
    # 3. Sprawdzenie czy agent_interface to AgentRuntimeManager
    is_manager = isinstance(pipeline.agent_interface, AgentRuntimeManager)
    print(f"[2] agent_interface is AgentRuntimeManager: {is_manager}")
    
    if not is_manager:
        print(f"ERROR: agent_interface is {type(pipeline.agent_interface)}")
        return False
    
    # 4. Sprawdzenie czy agent_runtime_manager jest ustawiony
    has_manager = pipeline.agent_runtime_manager is not None
    print(f"[3] agent_runtime_manager is not None: {has_manager}")
    
    if not has_manager:
        print("ERROR: agent_runtime_manager is None")
        return False
    
    # 5. Sprawdzenie czy agenci zostali stworzeni
    agents_count = len(pipeline.agent_runtime_manager.agents)
    print(f"[4] Number of agents created: {agents_count}")
    
    if agents_count != 6:
        print(f"WARNING: Expected 6 agents, got {agents_count}")
    
    # 6. Wykonanie jednego cyklu
    cycle_result = pipeline.run_cycle()
    print(f"\n[5] Single cycle execution: {cycle_result['status']}")
    
    if cycle_result['status'] != 'success':
        print(f"ERROR: {cycle_result.get('error')}")
        return False
    
    # 7. Sprawdzenie czy agent_execution był częścią cyklu
    agent_step = cycle_result['steps'].get('agent_execution', {})
    agent_status = agent_step.get('status')
    agents_active = agent_step.get('agents_active', 0)
    
    print(f"[6] Agent execution step: {agent_status}")
    print(f"[7] Agents active in cycle: {agents_active}")
    
    if agent_status != 'success':
        print(f"ERROR: Agent execution failed: {agent_step.get('error')}")
        return False
    
    if agents_active != 6:
        print(f"WARNING: Expected 6 agents active, got {agents_active}")
    
    # 8. Zamknięcie
    shutdown_result = pipeline.shutdown()
    print(f"\n[8] Pipeline shutdown: {shutdown_result['status']}")
    
    if shutdown_result['status'] != 'success':
        print(f"ERROR: {shutdown_result.get('error')}")
        return False
    
    print("\n" + "=" * 80)
    print("ALL TESTS PASSED!")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = test_pipeline_agent_runtime_manager()
    sys.exit(0 if success else 1)
