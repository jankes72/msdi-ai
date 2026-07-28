"""
Warstwa 5 - Generator Rozszerzonego Swiata Obserwacji SSI

Ten moduł jest odpowiedzialny za:
1. Zbieranie doświadczeń z V2 (pamiec_obserwacji.json, ocena.json, itd.)
2. Generowanie metadanych dla każdej sieci i meczu
3. Analizę ewolucji pamięci w czasie
4. Eksport rozszerzonego świata obserwacji

Architektura:
    V2 (Laboratorium modeli)
        ↓ (doświadczenia)
    Warstwa 5 (Generator Rozszerzonego Śwwiata)
        ↓
    SSI V3 (Świat wiedzy, role, agenci, strategie)

Author: SSI System
Date: 2026-07-27
"""

from . import kolektor_doswiadczen
from . import generator_metadanych
from . import analizator_ewolucji
from . import eksport_swiata
from . import konfiguracja

__version__ = "1.0.0"
__all__ = [
    'kolektor_doswiadczen',
    'generator_metadanych', 
    'analizator_ewolucji',
    'eksport_swiata',
    'konfiguracja'
]
