#!/usr/bin/env python
import sys
sys.path.insert(0, 'SSI_V5')

from core.pipeline import SSIPipeline, PipelineMode

print('Step 1: Create pipeline')
pipeline = SSIPipeline(mode=PipelineMode.SINGLE, use_agent_runtime_manager=True)

print('Step 2: Call _initialize_world_engine')
from core.world_engine import create_world_engine_from_generator
pipeline.world_engine = create_world_engine_from_generator('SSI_V5_WORLD')
print('  world_engine OK')

print('Step 3: Call _initialize_agent_runtime')
from SSI_V5.agents import AgentRuntimeManager
pipeline.agent_runtime_manager = AgentRuntimeManager(
    pipeline_reference=str(id(pipeline)),
    number_of_agents=6
)
pipeline.agent_interface = pipeline.agent_runtime_manager
result = pipeline.agent_runtime_manager.initialize()
print('  agent_runtime OK, status:', result['status'])

print('Step 4: Call _initialize_teacher_layer')
pipeline._initialize_teacher_layer()
print('  teacher_layer OK')

print('Step 5: Call _initialize_modeling_layer')
pipeline._initialize_modeling_layer()
print('  modeling_layer OK')

print('Step 6: Call _initialize_collective_manager')
pipeline._initialize_collective_manager()
print('  collective_manager OK')

print('Step 7: Call _initialize_memory_layer')
pipeline._initialize_memory_layer()
print('  memory_layer OK')

print('Step 8: Call _initialize_trust_manager')
pipeline._initialize_trust_manager()
print('  trust_manager OK')

print('Step 9: Call _initialize_personality_manager')
pipeline._initialize_personality_manager()
print('  personality_manager OK')

print('Step 10: Call _connect_components')
pipeline._connect_components()
print('  connect_components OK')

print('\nFinal status:')
print('  trust_manager:', pipeline.trust_manager is not None)
print('  personality_manager:', pipeline.personality_manager is not None)
