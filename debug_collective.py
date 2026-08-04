import sys
sys.path.insert(0, 'D:/sts/aplikacjaTyperBetAi')
from SSI_V5.core.pipeline import SSIPipeline, PipelineMode

pipeline = SSIPipeline(mode=PipelineMode.TEST, world_name='TEST', use_agent_runtime_manager=True)
pipeline.initialize()

# Wykonaj agent execution
from SSI_V5.teachers import CognitiveTeacher
import pandas as pd

mock_df = pd.DataFrame({'wynik': ['1:0', '2:1', '0:0']})
mock_cechy = ['feat1', 'feat2']
cognitive_teacher = CognitiveTeacher(mock_df, mock_cechy)

# Uruchom world generation
world_result = pipeline._run_world_generation()
modeling_result = pipeline._run_modeling(world_result.get('output'))
teacher_result = pipeline._run_teacher_analysis(modeling_result.get('output'))

print('Teacher result status:', teacher_result['status'])
print('Teacher analysis keys:', teacher_result.get('teacher_data', {}).keys())

# Uruchom agent execution
agent_result = pipeline._run_agent_execution(teacher_result.get('analysis', {}))
print('Agent result status:', agent_result['status'])
print('Agent result keys:', agent_result.keys())
print('Agent decisions keys:', agent_result.get('decisions', {}).keys())

# teraz collective consensus
collective_result = pipeline._run_collective_consensus(agent_result.get('decisions', {}))
print('Collective result:', collective_result)

# Sprawdź pamięć kolektywną
collective_memory = pipeline.collective_manager.get_collective_memory()
print('Collective decisions:', len(collective_memory['decisions']))
