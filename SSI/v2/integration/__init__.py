"""
SSI V2 Integration - Integracja podsystemów

Moduł odpowiedzialny za:
- Łączenie modeli Level 1 i Level 2
- Agregację predykcji z różnych sieci
- Most pomiędzy V2 a V3
- Koordynację przepływu danych

Zgodnie z dokumentacją:
- 01_SYSTEM_ARCHITECTURE.md Sekcja 2.2
- 02_DATA_STRUCTURE.md

Wersja: 1.0
Data: 2026-07-28
"""

from .v2_integration import (
    V2Integration, 
    V2Config, 
    PredictionResult, 
    CalibrationData,
    tworz_integracje_v2
)
from .model_output_aggregator import (
    ModelOutputAggregator,
    AggregationConfig,
    AggregatedPrediction,
    tworz_agregator
)
from .v2_to_v3_bridge import (
    V2ToV3Bridge,
    BridgeConfig,
    WorldDataPackage,
    tworz_bridge_v2_v3
)

__all__ = [
    # V2 Integration
    'V2Integration', 'V2Config', 'PredictionResult', 'CalibrationData', 'tworz_integracje_v2',
    
    # Aggregator
    'ModelOutputAggregator', 'AggregationConfig', 'AggregatedPrediction', 'tworz_agregator',
    
    # Bridge to V3
    'V2ToV3Bridge', 'BridgeConfig', 'WorldDataPackage', 'tworz_bridge_v2_v3'
]
