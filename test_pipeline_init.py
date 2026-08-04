import sys
sys.path.insert(0, 'SSI_V5')

print('1. Starting test...')
from core.pipeline import SSIPipeline, PipelineMode
print('2. Imported pipeline')

pipeline = SSIPipeline(mode=PipelineMode.SINGLE, use_agent_runtime_manager=True)
print('3. Created pipeline')

result = pipeline.initialize()
print('4. Initialized')
print('Status:', result['status'])
print('Trust Manager:', pipeline.trust_manager is not None)
print('Personality Manager:', pipeline.personality_manager is not None)
