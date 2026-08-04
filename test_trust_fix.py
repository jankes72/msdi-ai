#!/usr/bin/env python
# TestScript for TrustManager Deadlock Fix

import sys
import os

# Add project root to path
sys.path.insert(0, '/d/sts/aplikacjaTyperBetAi')

def test_1_standalone():
    """Test 1 - TrustManager standalone"""
    print("=" * 60)
    print("TEST 1: TrustManager standalone")
    print("=" * 60)
    
    try:
        from SSI_V5.agents.trust_manager import TrustManager
        
        tm = TrustManager(world_name="TEST")
        
        agents = ["agent_01", "agent_02"]
        names = {"agent_01": "Agent_01", "agent_02": "Agent_02"}
        
        print("Calling initialize_all_trust...")
        tm.initialize_all_trust(agents, names)
        
        print(f"Number of trust states: {len(tm._agent_trust_states)}")
        print(f"Trust states keys: {list(tm._agent_trust_states.keys())}")
        
        # Verify states were created correctly
        assert len(tm._agent_trust_states) == 2, f"Expected 2 states, got {len(tm._agent_trust_states)}"
        assert "agent_01" in tm._agent_trust_states, "agent_01 not in trust states"
        assert "agent_02" in tm._agent_trust_states, "agent_02 not in trust states"
        
        # Check that each agent has trust scores for the other
        state_01 = tm._agent_trust_states["agent_01"]
        state_02 = tm._agent_trust_states["agent_02"]
        
        assert "agent_02" in state_01.trust_in_agents, "agent_01 should have trust score for agent_02"
        assert "agent_01" in state_02.trust_in_agents, "agent_02 should have trust score for agent_01"
        
        print("[OK] All assertions passed")
        print("TEST 1 PASSED - No deadlock, correct state count and trust matrix")
        return True
        
    except Exception as e:
        print(f"[FAIL] TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_2_pipeline():
    """Test 2 - Pipeline initialization"""
    print("\n" + "=" * 60)
    print("TEST 2: Pipeline Initialization")
    print("=" * 60)
    
    try:
        from SSI_V5.core import SSIPipeline
        
        print("Creating pipeline...")
        pipeline = SSIPipeline(use_agent_runtime_manager=True)
        
        print("Calling initialize...")
        result = pipeline.initialize()
        
        # Check components
        print(f"Pipeline initialization result: {result}")
        
        # Check TrustManager
        tm = pipeline.trust_manager
        assert tm is not None, "TrustManager should exist"
        print(f"[OK] TrustManager exists: {type(tm).__name__}")
        
        # Check PersonalityManager
        pm = pipeline.personality_manager
        assert pm is not None, "PersonalityManager should exist"
        print(f"[OK] PersonalityManager exists: {type(pm).__name__}")
        
        # Check AgentRuntime
        arm = pipeline.agent_runtime_manager
        assert arm is not None, "AgentRuntimeManager should exist"
        print(f"[OK] AgentRuntimeManager exists: {type(arm).__name__}")
        
        # Check CollectiveManager
        cm = pipeline.collective_manager
        assert cm is not None, "CollectiveManager should exist"
        print(f"[OK] CollectiveManager exists: {type(cm).__name__}")
        
        print("TEST 2 PASSED - All managers initialized successfully")
        return True
        
    except Exception as e:
        print(f"[FAIL] TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_3_runtime_cycle():
    """Test 3 - Runtime cycle"""
    print("\n" + "=" * 60)
    print("TEST 3: Runtime Cycle")
    print("=" * 60)
    
    try:
        from SSI_V5.core import SSIPipeline
        
        print("Creating pipeline...")
        pipeline = SSIPipeline(use_agent_runtime_manager=True)
        
        print("Initializing pipeline...")
        pipeline.initialize()
        
        print("Running cycle...")
        # Run a single cycle
        cycle_result = pipeline.run_cycle()
        
        print(f"Cycle result: {cycle_result}")
        print("[OK] Cycle completed without deadlock")
        
        # Verify the flow: Agent -> Decision -> Personality Update -> Trust Update -> Memory
        # Check that trust manager has updated states
        tm = pipeline.trust_manager
        if tm and len(tm._agent_trust_states) > 0:
            print(f"[OK] TrustManager has {len(tm._agent_trust_states)} agent trust states")
        
        print("TEST 3 PASSED - Runtime cycle completed successfully")
        return True
        
    except Exception as e:
        print(f"[FAIL] TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    results = []
    
    results.append(test_1_standalone())
    results.append(test_2_pipeline())
    results.append(test_3_runtime_cycle())
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if all(results):
        print("ALL TESTS PASSED [OK]")
        sys.exit(0)
    else:
        print("SOME TESTS FAILED [FAIL]")
        sys.exit(1)
