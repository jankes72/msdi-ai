"""
SSI V3 Integration - Integracja z innymi warstwami

Moduł odpowiedzialny za:
- Integrację z V2 (odbiór predykcji)
- Integrację z V4 (dostarczanie wiedzy)
- Koordynację między systemami
- Przetwarzanie pakietów danych

Zgodnie z:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 3.3 (V3 Integration)
- 10_IMPLEMENTATION_MAP.md Etap 3C

Architektura:
V2 Models → V2ToV3Bridge → V3 Integration → V3 World Knowledge Engine → V3 Memory
                                          ↓
                                     V3ToV4Bridge → V4 Agents

Wersja: 1.0
Data: 2026-07-28
"""

from .world_integration import (
    WorldIntegration,
    WorldIntegrationConfig,
    IntegrationStatus,
    tworz_integracje_v3
)

# Re-export V2ToV3Bridge z V2
from ..v2.integration.v2_to_v3_bridge import (
    V2ToV3Bridge,
    BridgeConfig,
    WorldDataPackage
)

__all__ = [
    # V3 Integration
    'WorldIntegration',
    'WorldIntegrationConfig',
    'IntegrationStatus',
    'tworz_integracje_v3',
    
    # Re-exported from V2
    'V2ToV3Bridge',
    'BridgeConfig',
    'WorldDataPackage'
]
