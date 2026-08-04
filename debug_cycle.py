import sys
sys.path.insert(0, 'D:/sts/aplikacjaTyperBetAi')
from SSI_V5.core.pipeline import SSIPipeline, PipelineMode

pipeline = SSIPipeline(mode=PipelineMode.TEST, world_name='TEST', use_agent_runtime_manager=True)
pipeline.initialize()

cycle_result = pipeline.run_cycle()
print('Status:', cycle_result['status'])
for step, data in cycle_result['steps'].items():
    print(f"{step}: {data.get('status', 'unknown')}")
