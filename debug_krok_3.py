#!/usr/bin/env python3

import sys
sys.path.insert(0, 'D:/sts/aplikacjaTyperBetAi')

import datetime
from SSI_V5.agents.agent_runtime import AgentRuntime, AgentContract
from SSI_V5.memory.memory_integration import MemoryIntegrationLayer

# Mock CollectiveMemoryManager
class MockCollectiveMemoryManager:
    def __init__(self):
        self.storage = []
    def store_memory(self, record):
        doc_id = f"doc_{len(self.storage) + 1}"
        self.storage.append(record)
        print(f"[DEBUG] Stored in collective memory: {doc_id}")
        return doc_id
    def store_batch(self, records):
        return [f"batch_{i}" for i in range(len(records))]
    def search_memories(self, query, top_k=5, min_similarity=0.0, source_type_filter=None):
        print(f"[DEBUG] search_memories called with query: {query}")
        return []
    def get_relevant_memories(self, current_context, top_k=5, min_similarity=0.6):
        print(f"[DEBUG] get_relevant_memories called with context: {current_context}")
        return []
    def build_agent_context(self, agent_id, current_situation, max_context_length=2000):
        print(f"[DEBUG] build_agent_context called for {agent_id}")
        return {
            'agent_id': agent_id,
            'situation': current_situation,
            'relevant_memories': [],
            'memory_count': 0
        }
    @property
    def _stats(self):
        return {'total_memories': len(self.storage)}

# Setup
mock_manager = MockCollectiveMemoryManager()
memory_layer = MemoryIntegrationLayer(mock_manager)

# Create agent with memory integration
agent = AgentRuntime(
    agent_id="debug_agent",
    name="DebugAgent",
    mode="AUTO"
)
agent.set_memory_integration_reference(memory_layer)

print(f"[DEBUG] Memory integration enabled: {agent.is_memory_integration_enabled()}")

# Create test contract
contract = AgentContract(
    contract_id="debug_contract",
    cycle_id="debug_cycle",
    world_name="DebugWorld",
    world_data={'team_a': 'TeamA', 'team_b': 'TeamB'},
    model_evaluation={'model_v1': {'accuracy': 0.85}},
    current_weights={'weight1': 0.6, 'weight2': 0.4},
    recommendations=[{'action': 'select', 'model': 'v1'}],
    timestamp=datetime.datetime.now()
)

print(f"[DEBUG] Contract world_data: {contract.world_data}")
print(f"[DEBUG] Contract world_name: {contract.world_name}")

# Test receiving contract
try:
    print("[DEBUG] About to call receive_contract...")
    result = agent.receive_contract(contract)
    print(f"[DEBUG] receive_contract result: {result}")
except Exception as e:
    print(f"[DEBUG] Exception in receive_contract: {e}")
    import traceback
    traceback.print_exc()