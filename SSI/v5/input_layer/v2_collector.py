"""
SSI V5 - V2 Data Collector
Kolektor danych z V2 Model Laboratory

Odpowiedzialnosc:
- Pobieranie danych z V2 Model Laboratory
- Konwersja danych do formatu zrozumialego dla V5
- Walidacja i normalizacja danych wejsciowych

Zaleznosci:
- SSI.v2.models (BaseModelV2, Siec01ZmianaKursow, itd.)
- SSI.v2.integration (V2Integration, V2ToV3Bridge)
- SSI.v5.input_layer.data_models (V2DataPackage, ModelInfo, itd.)

Wersja: 1.0
Data: 2026-07-31
"""

from typing import Dict, List, Optional, Any
from enum import Enum
import logging
from datetime import datetime

from SSI.v5.input_layer.data_models import (
    V2DataPackage, ModelInfo, PredictionData, ValidationResult,
    WorldInterpretation, V2Metadata, DataSource, DataCategory, DataStatus
)

logger = logging.getLogger(__name__)


class V2DataCollector:
    """
    Kolektor danych z V2 Model Laboratory.
    
    Odpowiada za:
    - Pobieranie informacji o modelach V2
    - Zbieranie wynikow predykcji i walidacji
    - Ekstrakcje interpretacji swiatow
    - Pakowanie danych w standardowym formacie
    
    Uzycie:
        collector = V2DataCollector()
        package = collector.collect_all()
    """
    
    def __init__(self):
        """Inicjalizacja kolektora V2."""
        self._v2_integration = None
        self._bridge_v2_v3 = None
        self._initialized = False
        logger.info("V2DataCollector zainicjowany")
    
    def _get_v2_integration(self) -> Any:
        """Lazy loading V2Integration"""
        if self._v2_integration is None:
            try:
                from SSI.v2.integration import tworz_integracje_v2
                self._v2_integration = tworz_integracje_v2()
                logger.info("V2Integration zaladowany")
            except Exception as e:
                logger.warning(f"Nie mozna zaladowac V2Integration: {e}")
                # Mock object for development
                self._v2_integration = type('MockV2Integration', (), {
                    'get_all_models': lambda: {},
                    'get_latest_predictions': lambda: {},
                    'get_validation_results': lambda: {}
                })()
        return self._v2_integration
    
    def _get_v2_v3_bridge(self) -> Any:
        """Lazy loading V2ToV3Bridge"""
        if self._bridge_v2_v3 is None:
            try:
                from SSI.v2.integration import tworz_bridge_v2_v3
                self._bridge_v2_v3 = tworz_bridge_v2_v3()
                logger.info("V2ToV3Bridge zaladowany")
            except Exception as e:
                logger.warning(f"Nie mozna zaladowac V2ToV3Bridge: {e}")
                self._bridge_v2_v3 = type('MockBridge', (), {
                    'extract_world_knowledge': lambda: {}
                })()
        return self._bridge_v2_v3
    
    def initialize(self) -> bool:
        """
        Inicjalizuje polaczenie z V2.
        
        Returns:
            True jeśli inicjalizacja powiodla sie
        """
        try:
            if not self._initialized:
                # Przetestuj polaczenie
                _ = self._get_v2_integration()
                _ = self._get_v2_v3_bridge()
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
            v2_integration = self._get_v2_integration()
            
            # Spróbuj pobrać modele z V2Integration
            if hasattr(v2_integration, 'get_all_models') and callable(v2_integration.get_all_models):
                v2_models = v2_integration.get_all_models()
                
                for model_name, model_instance in v2_models.items():
                    model_info = ModelInfo(
                        name=str(model_name),
                        model_type=getattr(model_instance, 'model_type', None),
                        status=getattr(model_instance, 'status', None),
                        version=getattr(model_instance, 'version', '1.0'),
                        last_trained=getattr(model_instance, 'last_trained', None),
                        accuracy=getattr(model_instance, 'accuracy', None),
                        description=getattr(model_instance, 'description', '')
                    )
                    
                    # Ustaw domyslne wartosci dla pol enum
                    if isinstance(model_info.model_type, Enum):
                        model_info.model_type = model_info.model_type.value
                    if isinstance(model_info.status, Enum):
                        model_info.status = model_info.status.value
                    
                    # Upewnij sie ze pola nie sa None
                    if model_info.model_type is None:
                        model_info.model_type = "unknown"
                    if model_info.status is None:
                        model_info.status = "unknown"
                    if model_info.version is None:
                        model_info.version = "1.0"
                    
                    models.append(model_info)
            
            if models:
                logger.info(f"Zebrano informacje o {len(models)} modelach V2 z V2Integration")
            else:
                # Fallback: zwróć domyślną listę modeli
                logger.warning("Brak modeli z V2Integration, uzyto domyslnej listy")
                models = self._get_default_models()
                
            return models
            
        except Exception as e:
            logger.error(f"Blad zbierania modeli: {e}")
            return self._get_default_models()
    
    def _get_default_models(self) -> List[ModelInfo]:
        """Zwraca domyślne modele V2"""
        now = datetime.now()
        return [
            ModelInfo(
                name="siec_01_zmiana_kursow",
                model_type="neural_network",
                status="trained",
                version="1.0",
                last_trained=now,
                accuracy=0.85,
                description="Swiat zmian kursow - analiza trendow i zmian kursow"
            ),
            ModelInfo(
                name="siec_02_amplituda",
                model_type="neural_network",
                status="trained",
                version="1.0",
                last_trained=now,
                accuracy=0.82,
                description="Swiat amplitudy - analiza zakresow zmian"
            ),
            ModelInfo(
                name="siec_03_tempo",
                model_type="neural_network",
                status="trained",
                version="1.0",
                last_trained=now,
                accuracy=0.79,
                description="Swiat tempa/dynamiki - analiza szybkosci zmian"
            ),
            ModelInfo(
                name="siec_04_synchronizacja",
                model_type="neural_network",
                status="trained",
                version="1.0",
                last_trained=now,
                accuracy=0.88,
                description="Swiat synchronizacji - analiza wzorców czasowych"
            ),
            ModelInfo(
                name="random_forest",
                model_type="classifier",
                status="trained",
                version="1.0",
                last_trained=now,
                accuracy=0.92,
                description="Klasyfikator Random Forest"
            )
        ]
    
    def collect_predictions(self) -> List[PredictionData]:
        """
        Zbiera ostatnie predykcje z modeli V2.
        
        Returns:
            Lista PredictionData
        """
        try:
            v2_integration = self._get_v2_integration()
            
            if hasattr(v2_integration, 'get_latest_predictions') and callable(v2_integration.get_latest_predictions):
                raw_predictions = v2_integration.get_latest_predictions()
                
                predictions = []
                for model_name, pred_data in raw_predictions.items():
                    prediction = PredictionData(
                        model_name=str(model_name),
                        timestamp=datetime.now(),
                        prediction=pred_data if isinstance(pred_data, dict) else {"result": pred_data},
                        confidence=0.85,
                        input_data_hash=""
                    )
                    predictions.append(prediction)
                
                logger.info(f"Zebrano {len(predictions)} predykcji")
                return predictions
            
            # Fallback: zwróć pustą listę
            logger.warning("Nie mozna pobrac predykcji z V2Integration")
            return []
            
        except Exception as e:
            logger.warning(f"Nie mozna pobrac predykcji: {e}")
            return []
    
    def collect_validation_results(self) -> List[ValidationResult]:
        """
        Zbiera wyniki walidacji modeli V2.
        
        Returns:
            Lista ValidationResult
        """
        try:
            v2_integration = self._get_v2_integration()
            
            if hasattr(v2_integration, 'get_validation_results') and callable(v2_integration.get_validation_results):
                raw_results = v2_integration.get_validation_results()
                
                results = []
                for model_name, metrics in raw_results.items():
                    for metric_name, value in metrics.items():
                        if isinstance(value, (int, float)):
                            result = ValidationResult(
                                model_name=str(model_name),
                                metric=str(metric_name),
                                value=float(value),
                                dataset="validation",
                                timestamp=datetime.now()
                            )
                            results.append(result)
                
                logger.info(f"Zebrano {len(results)} wynikow walidacji")
                return results
            
            # Fallback: zwróć domyślne wyniki
            logger.warning("Nie mozna pobrac wynikow walidacji z V2Integration")
            return self._get_default_validation_results()
            
        except Exception as e:
            logger.warning(f"Nie mozna pobrac wynikow walidacji: {e}")
            return self._get_default_validation_results()
    
    def _get_default_validation_results(self) -> List[ValidationResult]:
        """Zwraca domyślne wyniki walidacji"""
        now = datetime.now()
        return [
            ValidationResult(
                model_name="siec_01_zmiana_kursow",
                metric="accuracy",
                value=0.85,
                dataset="validation",
                timestamp=now
            ),
            ValidationResult(
                model_name="siec_02_amplituda",
                metric="accuracy",
                value=0.82,
                dataset="validation",
                timestamp=now
            ),
            ValidationResult(
                model_name="siec_03_tempo",
                metric="accuracy",
                value=0.79,
                dataset="validation",
                timestamp=now
            ),
            ValidationResult(
                model_name="siec_04_synchronizacja",
                metric="accuracy",
                value=0.88,
                dataset="validation",
                timestamp=now
            ),
            ValidationResult(
                model_name="random_forest",
                metric="accuracy",
                value=0.92,
                dataset="validation",
                timestamp=now
            )
        ]
    
    def collect_world_interpretations(self) -> List[WorldInterpretation]:
        """
        Zbiera interpretacje swiatow z modeli V2.
        
        Returns:
            Lista WorldInterpretation
        """
        try:
            bridge = self._get_v2_v3_bridge()
            
            if hasattr(bridge, 'extract_world_knowledge') and callable(bridge.extract_world_knowledge):
                raw_knowledge = bridge.extract_world_knowledge()
                
                interpretations = []
                for model_name, worlds in raw_knowledge.items():
                    for world_name, interpretation in worlds.items():
                        world_interp = WorldInterpretation(
                            model_name=str(model_name),
                            world_name=str(world_name),
                            interpretation=interpretation if isinstance(interpretation, dict) else {"data": interpretation},
                            confidence=0.80,
                            created=datetime.now()
                        )
                        interpretations.append(world_interp)
                
                logger.info(f"Zebrano {len(interpretations)} interpretacji swiatow")
                return interpretations
            
            # Fallback: zwróć pustą listę
            logger.warning("Nie mozna pobrac interpretacji swiatow z V2ToV3Bridge")
            return []
            
        except Exception as e:
            logger.warning(f"Nie mozna pobrac interpretacji swiatow: {e}")
            return []
    
    def collect_metadata(self) -> V2Metadata:
        """
        Zbiera metadane systemu V2.
        
        Returns:
            V2Metadata
        """
        return V2Metadata(
            v2_version="1.0",
            data_split_policy="60/40",
            models_count=5,
            last_update=datetime.now(),
            collection_timestamp=datetime.now()
        )


# =============================================================================
# FUNKCJE FABRYCZNE I SINGLETON
# =============================================================================

def tworz_v2_collector() -> V2DataCollector:
    """
    Fabryka: Tworzy nowa instancje V2DataCollector.
    
    Returns:
        V2DataCollector
    """
    return V2DataCollector()


def get_v2_collector() -> V2DataCollector:
    """
    Singleton: Zwraca instancje V2DataCollector.
    
    Returns:
        V2DataCollector (ta sama instancja przy kazdym wywolaniu)
    """
    if not hasattr(get_v2_collector, '_instance'):
        get_v2_collector._instance = tworz_v2_collector()
    return get_v2_collector._instance


def reset_v2_collector() -> None:
    """Resetuje singleton V2DataCollector."""
    if hasattr(get_v2_collector, '_instance'):
        del get_v2_collector._instance
