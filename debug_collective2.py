import sys
sys.path.insert(0, 'D:/sts/aplikacjaTyperBetAi')
from SSI_V5.core.pipeline import SSIPipeline, PipelineMode

pipeline = SSIPipeline(mode=PipelineMode.TEST, world_name='TEST', use_agent_runtime_manager=True)
pipeline.initialize()

# Wykonaj jeden cykl
cycle_result = pipeline.run_cycle()
print('Cycle result status:', cycle_result['status'])

# Sprawdź pamięć kolektywną
collective_memory = pipeline.collective_manager.get_collective_memory()
print('Collective decisions:', len(collective_memory['decisions']))
print('Collective observations:', len(collective_memory['observations']))
print('Total collective decisions:', pipeline.collective_manager.total_collective_decisions)
