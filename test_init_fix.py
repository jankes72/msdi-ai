#!/usr/bin/env python
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'SSI_V5'))

print('Step 1: Importing...')
from core.pipeline import SSIPipeline, PipelineMode

print('Step 2: Creating pipeline...')
pipeline = SSIPipeline(mode=PipelineMode.SINGLE, use_agent_runtime_manager=True)

print('Step 3: Initializing...')
result = pipeline.initialize()

print('Step 4: Results')
print('Init status:', result['status'])
print('Trust Manager exists:', pipeline.trust_manager is not None)
print('Personality Manager exists:', pipeline.personality_manager is not None)
print('Components:', list(result['components'].keys()))
