"""
SSI V5 - Main Module
Glowny modul warstwy V5 (AI Core + Samorozwoj Systemu)

Odpowiedzialnosc:
- Input Layer (warstwa wejscia) - Sprint 11
- Knowledge Memory (pamiec wejsciowa) - Sprint 12
- LLM Core (model jezykowy) - Sprint 13
- Classification & Routing (klasyfikacja i routowanie) - Sprint 14
- Developer Panel (panel programisty) - Sprint 15
- User Panel (panel uzytkownika) - Sprint 16
- Model Router (zarzadzanie modelami) - Sprint 17
- Laboratories Integration (integracja laboratoriow) - Sprint 18
- Collective System (kolektyw agentow) - Sprint 19

Zaleznosci:
- SSI.v2 (V2 Model Laboratory)
- SSI.v3 (V3 World Memory System)
- SSI.v4 (V4 Agent Evolution)

Wersja: 1.0
Data: 2026-07-31
"""

# Input Layer (Sprint 11)
from SSI.v5.input_layer import (
    data_models,
    v2_collector
)

# W przyszlosci:
# from SSI.v5.memory import knowledge_memory
# from SSI.v5.llm import llm_core
# from SSI.v5.classification import classifier
# from SSI.v5.panels import developer_panel, user_panel

__all__ = [
    # Input Layer
    'data_models',
    'v2_collector'
]

__version__ = "1.0.0"
__author__ = "MSDI AI / SSI System"
