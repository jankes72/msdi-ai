"""
SSI (Self Learning Intelligence Ecosystem)
Główny moduł systemu SSI - Self Learning Intelligence

Ten moduł dostarcza struktury dla autonomicznego ekosystemu uczących się agentów,
który analizuje, rozumie i podejmuje decyzje w sposób inteligentny i adaptacyjny.

Architektura:
- V2 Model Laboratory: Modele interpretujące świat
- V3 World Memory System: Mapa wiedzy o światach i wzorcach  
- V4 Agent Evolution: Autonomiczne jednostki decyzyjne
- Strategy Intelligence Engine: System tworzenia i ewolucji strategii
- Decision Laboratories: Środowiska eksperymentalne
- Feedback Loop: System ciągłej poprawy

Wersja: 1.0
Data: 2026-07-28
"""

from .core import SSISystem, SSIModule, SSIComponent
from .config import SSIConfig

__version__ = "1.0.0"
__author__ = "SSI System"

# Eksport głównych klas
__all__ = [
    'SSISystem',
    'SSIModule', 
    'SSIComponent',
    'SSIConfig',
    '__version__',
    '__author__'
]
