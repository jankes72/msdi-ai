# SSI V5 - IFC (Infrastructure Communication Fabric)
# ETAP 1.2.7.3: Adaptive Knowledge Ecosystem

"""
IFC - Układ nerwowy SSI V5.
Odpowiada za:
- Rejestrację komponentów systemowych
- Routing komunikatów między modułami
- Separację i luźne sprzężenie komponentów

Architektura:
    Component A --> IFC --> Component B
    
Przyszłe użycie:
    ETAP 1.2.7.3: register(), get(), send(), route()
    ETAP 1.5:     AgentMessage, TutorMessage, KnowledgeProposal
    ETAP 2.0:    EvolutionProposal, ValidationRequest, DeploymentCommand
"""

from .registry import IFCRegistry
from .message import IFCMessage
from .router import IFCRouter

__all__ = ['IFCRegistry', 'IFCMessage', 'IFCRouter']
