import sys
sys.path.insert(0, 'D:/sts/aplikacjaTyperBetAi')
from SSI_V5.core.pipeline import SSIPipeline, PipelineMode

pipeline = SSIPipeline(mode=PipelineMode.TEST, world_name='TEST', use_agent_runtime_manager=True)
pipeline.initialize()

# Wykonaj world generation
world_result = pipeline._run_world_generation()
print('World result status:', world_result['status'])

# Wykonaj modeling
modeling_result = pipeline._run_modeling(world_result.get('output'))
print('Modeling result:', modeling_result)
