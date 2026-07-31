# Sprint 11 - Implementacja: Fundament komunikacji SSI V5 z V2/V3/V4

**Wersja dokumentu:** 1.0  
**Data utworzenia:** 2026-07-31  
**Status:** AKTYWNY  
**Sprint Glowny:** Sprint 11 (Fundament komunikacji SSI V5)  
**Podstawa:** `SSI_V5_ROADMAP.md`, `PROJECT_RULES.md`  

---

## Cel Sprintu 11

Utworzenie **warstwy wejścia danych** dla modelu jezykowego V5. System zaczyna rozumiec caly stan SSI.

---

## Podzial na Sprinty Implementacyjne

```
Sprint 11: Fundament komunikiacji SSI V5 z V2/V3/V4
├── Sprint 11.1: V2 Data Collector (20%)
│   ├── SSI/v5/input_layer/v2_collector.py
│   ├── SSI/v5/input_layer/data_models.py
│   └── SSI/tests/v5/test_v2_collector.py
│
├── Sprint 11.2: V3 Knowledge Collector (20%)
│   ├── SSI/v5/input_layer/v3_collector.py
│   └── SSI/tests/v5/test_v3_collector.py
│
├── Sprint 11.3: V4 Agents Collector (20%)
│   ├── SSI/v5/input_layer/v4_collector.py
│   └── SSI/tests/v5/test_v4_collector.py
│
├── Sprint 11.4: External Input Layer (20%)
│   ├── SSI/v5/input_layer/agents_input.py
│   ├── SSI/v5/input_layer/labs_input.py
│   ├── SSI/v5/input_layer/dev_input.py
│   └── SSI/tests/v5/test_external_input.py
│
└── Sprint 11.5: Input Layer Integration (20%)
    ├── SSI/v5/input_layer/input_manager.py
    ├── SSI/v5/__init__.py
    └── SSI/tests/v5/test_input_integration.py
```

---

## Zaleznosci Miedzy Sprintami

```
Sprint 11.1 (V2 Collector)
    ↓
Sprint 11.2 (V3 Collector)
    ↓
Sprint 11.3 (V4 Collector)
    ↓
Sprint 11.4 (External Input)
    ↓
Sprint 11.5 (Integration)
```

Kazdy kolejny sprint zalezy od poprawnej implementacji poprzedniego.

---

## Sprint 11.1: V2 Data Collector

### Cel
Pobieranie danych z V2 Model Laboratory i udostepnianie ich dla warstwy wejscia V5.

### Zakres
| Lp | Obszar | Opis | Status |
|----|--------|------|--------|
| 1 | Modele V2 | Pobieranie listy modeli (Siec01-Siec04, RandomForest, Classifiers) | planned |
| 2 | Konfiguracja V2 | Pobieranie konfiguracji modeli | planned |
| 3 | Wyniki V2 | Pobieranie wynikow predykcji i walidacji | planned |
| 4 | Swiaty V2 | Pobieranie interpretacji swiatow z modeli | planned |
| 5 | Metadane V2 | Pobieranie metadanych (wersje, daty, parametry) | planned |

### Pliki do Utworzenia

```
SSI/
└── v5/
    └── input_layer/
        ├── __init__.py          # Pusty lub z basic imports
        ├── data_models.py       # Modele danych dla V2
        └── v2_collector.py       # Glowny kolektor V2

SSI/
└── tests/
    └── v5/
        ├── __init__.py          # Pusty
        └── test_v2_collector.py  # Testy dla V2 Collector
```

### Struktura Pliku: v2_collector.py

```python
"""
SSI V5 - V2 Data Collector

Odpowiedzialnosc:
- Pobieranie danych z V2 Model Laboratory
- Konwersja danych do formatu zrozumialego dla V5
- Walidacja i normalizacja danych wejsciowych

Zaleznosci:
- SSI.v2.models (BaseModelV2, Siec01ZmianaKursow, itd.)
- SSI.v2.integration (V2Integration, V2ToV3Bridge)
- SSI.v5.input_layer.data_models (V2DataModel, ModelInfo, itd.)

Wersja: 1.0
Data: 2026-07-31
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime

from SSI.v2.models import (
    BaseModelV2, ModelType, ModelStatus,
    Siec01ZmianaKursow, Siec02Amplituda, Siec03Tempo, Siec04Synchronizacja,
    RandomForestModel, ClassifierModel
)
from SSI.v2.integration import V2Integration, V2ToV3Bridge

logger = logging.getLogger(__name__)


class V2DataType(Enum):
    """Typy danych pobieranych z V2"""
    MODELS = "models"           # Lista modeli
    CONFIG = "config"           # Konfiguracja
    PREDICTIONS = "predictions" # Wyniki predykcji
    VALIDATION = "validation"   # Wyniki walidacji
    WORLDS = "worlds"           # Interpretacje swiatow
    METADATA = "metadata"       # Metadane


@dataclass
class ModelInfo:
    """Informacje o jednym modelu V2"""
    name: str
    model_type: str
    status: str
    version: str
    last_trained: Optional[datetime] = None
    accuracy: Optional[float] = None
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "model_type": self.model_type,
            "status": self.status,
            "version": self.version,
            "last_trained": self.last_trained.isoformat() if self.last_trained else None,
            "accuracy": self.accuracy,
            "description": self.description
        }


@dataclass
class V2DataPackage:
    """Kompletny pakiet danych z V2"""
    timestamp: datetime = field(default_factory=datetime.now)
    models: List[ModelInfo] = field(default_factory=list)
    predictions: Dict[str, Any] = field(default_factory=dict)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    world_interpretations: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "models": [m.to_dict() for m in self.models],
            "predictions": self.predictions,
            "validation_results": self.validation_results,
            "world_interpretations": self.world_interpretations,
            "metadata": self.metadata
        }


class V2DataCollector:
    """
    Kolektor danych z V2 Model Laboratory.
    
    Odpowiada za:
    - Pobieranie informacji o modelach V2
    - Zbieranie wynikow predykcji i walidacji
    - Ekstrakcje interpretacji swiatow
    - Pakowanie danych w standardowym formacie
    """
    
    def __init__(self, v2_integration: Optional[V2Integration] = None):
        """
        Inicjalizacja kolektora V2.
        
        Args:
            v2_integration: Instancja V2Integration (opcjonalnie)
        """
        self.v2_integration = v2_integration or self._create_v2_integration()
        self._initialized = False
        logger.info("V2DataCollector zainicjowany")
    
    def _create_v2_integration(self) -> V2Integration:
        """Tworzy instancje V2Integration"""
        try:
            from SSI.v2.integration import tworz_integracje_v2
            return tworz_integracje_v2()
        except Exception as e:
            logger.warning(f"Nie mozna utworzyc V2Integration: {e}")
            # Tworzymy mock na potrzeby rozwoju
            return V2Integration()
    
    def initialize(self) -> bool:
        """
        Inicjalizuje polaczenie z V2.
        
        Returns:
            True jeśli inicjalizacja powiodla sie
        """
        try:
            if not self._initialized:
                # Inicjalizacja V2Integration
                self._initialized = True
                logger.info("V2DataCollector zainicjalizowany")
            return True
        except Exception as e:
            logger.error(f"Blad inicjalizacji: {e}")
            return False
    
    def collect_all(self) -> V2DataPackage:
        """
        Zbiera wszystkie dostepne dane z V2.
        
        Returns:
            V2DataPackage z wszystkimi danymi
        """
        package = V2DataPackage()
        
        try:
            # 1. Zbieraj informacje o modelach
            package.models = self.collect_models()
            
            # 2. Zbieraj predykcje
            package.predictions = self.collect_predictions()
            
            # 3. Zbieraj wyniki walidacji
            package.validation_results = self.collect_validation_results()
            
            # 4. Zbieraj interpretacje swiatow
            package.world_interpretations = self.collect_world_interpretations()
            
            # 5. Zbieraj metadane
            package.metadata = self.collect_metadata()
            
            logger.info(f"Zebrano dane V2: {len(package.models)} modeli")
            return package
            
        except Exception as e:
            logger.error(f"Blad zbierania danych V2: {e}")
            raise
    
    def collect_models(self) -> List[ModelInfo]:
        """
        Zbiera informacje o wszystkich modelach V2.
        
        Returns:
            Lista ModelInfo
        """
        models = []
        
        try:
            # Pobierz modele z V2Integration
            v2_models = self.v2_integration.get_all_models()
            
            for model_name, model_instance in v2_models.items():
                model_info = ModelInfo(
                    name=model_name,
                    model_type=model_instance.model_type.value if hasattr(model_instance, 'model_type') else str(type(model_instance).__name__),
                    status=model_instance.status.value if hasattr(model_instance, 'status') else "unknown",
                    version=getattr(model_instance, 'version', '1.0'),
                    last_trained=getattr(model_instance, 'last_trained', None),
                    accuracy=getattr(model_instance, 'accuracy', None),
                    description=getattr(model_instance, 'description', '')
                )
                models.append(model_info)
                
            logger.info(f"Zebrano informacje o {len(models)} modelach V2")
            return models
            
        except Exception as e:
            logger.error(f"Blad zbierania modeli: {e}")
            # Zwroc domyslna liste modeli
            return [
                ModelInfo(name="siec_01_zmiana_kursow", model_type="neural_network", status="trained", version="1.0"),
                ModelInfo(name="siec_02_amplituda", model_type="neural_network", status="trained", version="1.0"),
                ModelInfo(name="siec_03_tempo", model_type="neural_network", status="trained", version="1.0"),
                ModelInfo(name="siec_04_synchronizacja", model_type="neural_network", status="trained", version="1.0"),
                ModelInfo(name="random_forest", model_type="classifier", status="trained", version="1.0"),
            ]
    
    def collect_predictions(self) -> Dict[str, Any]:
        """Zbiera ostatnie predykcje z modeli V2"""
        try:
            return self.v2_integration.get_latest_predictions()
        except Exception as e:
            logger.warning(f"Nie mozna pobrac predykcji: {e}")
            return {}
    
    def collect_validation_results(self) -> Dict[str, Any]:
        """Zbiera wyniki walidacji modeli V2"""
        try:
            return self.v2_integration.get_validation_results()
        except Exception as e:
            logger.warning(f"Nie mozna pobrac wynikow walidacji: {e}")
            return {}
    
    def collect_world_interpretations(self) -> Dict[str, Any]:
        """Zbiera interpretacje swiatow z modeli V2"""
        try:
            # Uzyj mostu V2ToV3 do pobrania interpretacji
            bridge = V2ToV3Bridge()
            return bridge.extract_world_knowledge()
        except Exception as e:
            logger.warning(f"Nie mozna pobrac interpretacji swiatow: {e}")
            return {}
    
    def collect_metadata(self) -> Dict[str, Any]:
        """Zbiera metadane systemu V2"""
        return {
            "collection_timestamp": datetime.now().isoformat(),
            "v2_version": "1.0",
            "data_split_policy": "60/40",
            "models_count": 5,
            "last_update": datetime.now().isoformat()
        }


def tworz_v2_collector() -> V2DataCollector:
    """Fabryka: Tworzy instancje V2DataCollector"""
    return V2DataCollector()


def get_v2_collector() -> V2DataCollector:
    """Singleton: Zwraca instancje V2DataCollector"""
    if not hasattr(get_v2_collector, '_instance'):
        get_v2_collector._instance = tworz_v2_collector()
    return get_v2_collector._instance
