# SSI V5 Core Module - World Engine
# ==================================================
#
# ETAP: 5.2.4 FAZA 3.3.1
# Data: 2026-08-03
# 
# Odpowiedzialnosc:
# - Odbior danych z generatora SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py
# - Przygotowanie kontraktu danych WorldEngineOutput
# - Przekazanie danych do Modeling Layer
# - Przekazanie wynikow do Teacher Layer
#
# ZASADA: NIE ZMIENIAMY GENERATORA
# WorldEngine dziala jako most pomiedzy generatorem a kolejnymi warstwami

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime
import json
import copy


@dataclass
class WorldEngineOutput:
    """
    Kontrakt danych WorldEngine.
    
    Pola:
    - results: Haupt Ergebnisse der Weltgenerierung
    - features: Eingangsmerkmale und abgeleitete Merkmale
    - models: Generierte Modelle und ihre Konfigurationen
    - predictions: Vorhersagen aus den Modellen
    - observations: Beobachtungen und Analysen
    - metadata: Metadaten des Verarbeitungszyklus
    """
    results: Dict[str, Any] = field(default_factory=dict)
    features: Dict[str, Any] = field(default_factory=dict)
    models: Dict[str, Any] = field(default_factory=dict)
    predictions: Dict[str, Any] = field(default_factory=dict)
    observations: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do niezmiennego slownika"""
        return {
            'results': copy.deepcopy(self.results),
            'features': copy.deepcopy(self.features),
            'models': copy.deepcopy(self.models),
            'predictions': copy.deepcopy(self.predictions),
            'observations': copy.deepcopy(self.observations),
            'metadata': copy.deepcopy(self.metadata)
        }

    def to_json(self, indent: int = 2) -> str:
        """Konwersja do formatu JSON"""
        data = self.to_dict()
        # Konwersja typow nieobsługiwanych przez JSON
        for key in data:
            if isinstance(data[key], dict):
                data[key] = self._convert_to_json_serializable(data[key])
        return json.dumps(data, indent=indent, ensure_ascii=False, default=str)

    def _convert_to_json_serializable(self, obj: Any) -> Any:
        """Konwersja obiektow do formatu serializowalnego JSON"""
        if isinstance(obj, dict):
            return {k: self._convert_to_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._convert_to_json_serializable(item) for item in obj]
        elif isinstance(obj, (np.ndarray, pd.DataFrame, pd.Series)):
            return obj.tolist() if hasattr(obj, 'tolist') else str(obj)
        elif isinstance(obj, (datetime, np.datetime64)):
            return str(obj)
        elif hasattr(obj, '__dict__'):
            return str(obj)
        else:
            return obj

    def update_metadata(self, key: str, value: Any) -> None:
        """Aktualizacja metadanych"""
        self.metadata[key] = value
        self.metadata['last_update'] = datetime.now().isoformat()


@dataclass
class ProcessingContext:
    """
    Kontekst przetwarzania dla pojedynczego cyklu swiata.
    
    Zawiera:
    - cycle_id: Unikalny identyfikator cyklu
    - timestamp: Data i czas utworzenia
    - world_name: Nazwa swiata
    - generator_reference: Referencja do generatora danych
    """
    cycle_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    world_name: str = "SSI_V5_WORLD"
    generator_reference: str = "SSI_V5_SPORTS_WORLD_MODEL_GENERATOR"
    stage: str = "world_generation"


class WorldEngine:
    """
    WorldEngine - Glowny silnik cyklu zycia SSI V5.
    
    Odpowiedzialnosc:
    1. Odbior danych z generatora (SSI_V5_SPORTS_WORLD_MODEL_GENERATOR.py)
    2. Przygotowanie kontraktu danych WorldEngineOutput
    3. Przekazanie danych do Modeling Layer
    4. Przekazanie wynikow do Teacher Layer
    
    NIE ZMIENIA GENERATORA - dziala jako most/adapter.
    
    Uzycie:
    >>> engine = WorldEngine(generator_data, world_name="test_world")
    >>> output = engine.process()
    >>> engine.send_to_modeling(output)
    >>> engine.send_to_teacher(output)
    """

    def __init__(self, generator_data: Optional[Dict[str, Any]] = None, 
                 world_name: str = "SSI_V5_WORLD", 
                 context: Optional[ProcessingContext] = None):
        """
        Inicjalizacja WorldEngine.
        
        Args:
            generator_data: Dane wejsciowe z generatora (opcjonalne)
            world_name: Nazwa swiata
            context: Kontekst przetwarzania (opcjonalny)
        """
        self.world_name = world_name
        self.generator_data = generator_data or {}
        
        # Kontekst przetwarzania
        if context is None:
            self.context = ProcessingContext(
                cycle_id=f"{world_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                world_name=world_name
            )
        else:
            self.context = context
        
        # Stan silnika
        self._is_initialized = False
        self._processing_stage = "initialized"
        
        # Referencje do warstw
        self._modeling_layer = None
        self._teacher_layer = None
        
        # Pamięć cyklu
        self.cycle_history: List[WorldEngineOutput] = []
        
        self._initialize()

    def _initialize(self) -> None:
        """Inicjalizacja silnika"""
        self._is_initialized = True
        self._processing_stage = "ready"
        
        # Logowanie inicjalizacji
        self._log_event("engine_initialized", {"world_name": self.world_name})

    def _log_event(self, event_type: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Logowanie zdarzenia"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "cycle_id": self.context.cycle_id,
            "world_name": self.world_name,
            "stage": self._processing_stage,
            "data": data or {}
        }
        # Tutaj mozna dodac zapisy do pliku lub bazy danych
        # Na potrzeby SSI V5 obecnie trzymamy w pamieci
        if not hasattr(self, '_event_log'):
            self._event_log = []
        self._event_log.append(event)

    def receive_from_generator(self, generator_data: Dict[str, Any], 
                              generator_name: str = "SSI_V5_SPORTS_WORLD_MODEL_GENERATOR") -> None:
        """
        Odbior danych z generatora.
        
        NIE ZMIENIA GENERATORA - seulement odbiera dane.
        
        Args:
            generator_data: Dane wyjsciowe z generatora
            generator_name: Nazwa generatora
        """
        self.generator_data = copy.deepcopy(generator_data)
        self.context.generator_reference = generator_name
        
        # Zaktualizuj stage
        self._processing_stage = "data_received"
        
        self._log_event("data_received_from_generator", {
            "data_keys": list(generator_data.keys()) if isinstance(generator_data, dict) else "unknown",
            "generator_name": generator_name
        })

    def prepare_contract(self, additional_data: Optional[Dict[str, Any]] = None) -> WorldEngineOutput:
        """
        Przygotowanie kontraktu danych WorldEngineOutput.
        
        Tworzy strukture wyjsciowa z danymi z generatora
        oraz dodatkowymi informacjami.
        
        Args:
            additional_data: Dodatkowe dane do kontraktu
            
        Returns:
            WorldEngineOutput z przygotowanymi danymi
        """
        contract = WorldEngineOutput()
        
        # Mapowanie danych z generatora do kontraktu
        if isinstance(self.generator_data, dict):
            # Results - glowne wyniki generatora
            if 'results' in self.generator_data:
                contract.results = self._prepare_results(self.generator_data['results'])
            elif any(key in self.generator_data for key in ['Y', 'predictions', 'wyniki']):
                contract.results = self._extract_results_from_generator()
            
            # Features - cechy i dane wejsciowe
            if 'features' in self.generator_data:
                contract.features = self._prepare_features(self.generator_data['features'])
            elif any(key in self.generator_data for key in ['X', 'cechy', 'input_data', 'df']):
                contract.features = self._extract_features_from_generator()
            
            # Models - modele i ich parametry
            if 'models' in self.generator_data:
                contract.models = self._prepare_models(self.generator_data['models'])
            elif any(key in self.generator_data for key in ['modele', 'model_data', 'sieci']):
                contract.models = self._extract_models_from_generator()
            
            # Predictions - predykcje
            if 'predictions' in self.generator_data:
                contract.predictions = self._prepare_predictions(self.generator_data['predictions'])
            elif any(key in self.generator_data for key in ['predykcje', 'Y_pred']):
                contract.predictions = self._extract_predictions_from_generator()
            
            # Observations - obserwacje i analiza
            if 'observations' in self.generator_data:
                contract.observations = self._prepare_observations(self.generator_data['observations'])
            
            # Additional data - rozne
            if 'observations' in self.generator_data:
                contract.observations = self._prepare_observations(self.generator_data['observations'])
            elif any(key in self.generator_data for key in ['obserwacje', 'analiza', 'diagnostyka']):
                contract.observations = self._extract_observations_from_generator()
        
        # Dodatkowe dane
        if additional_data:
            self._merge_additional_data(contract, additional_data)
        
        # Metadane
        contract.update_metadata('cycle_id', self.context.cycle_id)
        contract.update_metadata('world_name', self.world_name)
        contract.update_metadata('generator', self.context.generator_reference)
        contract.update_metadata('processing_timestamp', datetime.now().isoformat())
        contract.update_metadata('engine_version', 'SSI_V5_ETAPE_5.2.4_FAZA_3.3.1')
        
        # Zaktualizuj stage
        self._processing_stage = "contract_prepared"
        
        self._log_event("contract_prepared", {
            "contract_keys": list(contract.to_dict().keys()),
            "results_keys": list(contract.results.keys()) if contract.results else [],
            "features_keys": list(contract.features.keys()) if contract.features else []
        })
        
        return contract

    def _prepare_results(self, results_data: Any) -> Dict[str, Any]:
        """Przygotowanie sekcji results"""
        results = {}
        
        if isinstance(results_data, dict):
            results = copy.deepcopy(results_data)
        elif isinstance(results_data, (pd.DataFrame, pd.Series)):
            results['data'] = results_data.to_dict()
            results['shape'] = results_data.shape
            results['columns'] = list(results_data.columns) if hasattr(results_data, 'columns') else []
        elif isinstance(results_data, np.ndarray):
            results['data'] = results_data.tolist()
            results['shape'] = results_data.shape
        else:
            results['raw'] = str(results_data)
        
        return results

    def _prepare_features(self, features_data: Any) -> Dict[str, Any]:
        """Przygotowanie sekcji features"""
        features = {}
        
        if isinstance(features_data, dict):
            features = copy.deepcopy(features_data)
            # Konwersja DataFrame/Series do dict
            for key, value in features.items():
                if isinstance(value, (pd.DataFrame, pd.Series)):
                    features[key] = value.to_dict()
        elif isinstance(features_data, (pd.DataFrame, np.ndarray)):
            features['data'] = features_data.to_dict() if hasattr(features_data, 'to_dict') else features_data.tolist()
        else:
            features['raw'] = str(features_data)
        
        return features

    def _prepare_models(self, models_data: Any) -> Dict[str, Any]:
        """Przygotowanie sekcji models"""
        models = {}
        
        if isinstance(models_data, dict):
            models = copy.deepcopy(models_data)
        elif isinstance(models_data, list):
            models['list'] = [str(m) for m in models_data]
        else:
            models['raw'] = str(models_data)
        
        return models

    def _prepare_predictions(self, predictions_data: Any) -> Dict[str, Any]:
        """Przygotowanie sekcji predictions"""
        predictions = {}
        
        if isinstance(predictions_data, dict):
            predictions = copy.deepcopy(predictions_data)
        elif isinstance(predictions_data, (pd.DataFrame, np.ndarray)):
            predictions['data'] = predictions_data.to_dict() if hasattr(predictions_data, 'to_dict') else predictions_data.tolist()
        else:
            predictions['raw'] = str(predictions_data)
        
        return predictions

    def _prepare_observations(self, observations_data: Any) -> Dict[str, Any]:
        """Przygotowanie sekcji observations"""
        observations = {}
        
        if isinstance(observations_data, dict):
            observations = copy.deepcopy(observations_data)
        elif isinstance(observations_data, (pd.DataFrame, np.ndarray)):
            observations['data'] = observations_data.to_dict() if hasattr(observations_data, 'to_dict') else observations_data.tolist()
        else:
            observations['raw'] = str(observations_data)
        
        return observations

    def _extract_results_from_generator(self) -> Dict[str, Any]:
        """Wydobywanie wynikow z danych generatora"""
        results = {}
        
        for key in ['Y', 'results', 'wyniki', 'target', 'targets']:
            if key in self.generator_data:
                results['main'] = self._prepare_results(self.generator_data[key])
                break
        
        return results

    def _extract_features_from_generator(self) -> Dict[str, Any]:
        """Wydobywanie cech z danych generatora"""
        features = {}
        
        for key in ['X', 'features', 'cechy', 'input_data', 'df', 'data']:
            if key in self.generator_data:
                features['main'] = self._prepare_features(self.generator_data[key])
                break
        
        return features

    def _extract_models_from_generator(self) -> Dict[str, Any]:
        """Wydobywanie modeli z danych generatora"""
        models = {}
        
        for key in ['models', 'modele', 'model_data', 'sieci', 'networks']:
            if key in self.generator_data:
                models = self._prepare_models(self.generator_data[key])
                break
        
        return models

    def _extract_predictions_from_generator(self) -> Dict[str, Any]:
        """Wydobywanie predykcji z danych generatora"""
        predictions = {}
        
        for key in ['predictions', 'predykcje', 'Y_pred', 'y_pred']:
            if key in self.generator_data:
                predictions = self._prepare_predictions(self.generator_data[key])
                break
        
        return predictions

    def _extract_observations_from_generator(self) -> Dict[str, Any]:
        """Wydobywanie obserwacji z danych generatora"""
        observations = {}
        
        for key in ['observations', 'obserwacje', 'analiza', 'diagnostyka', 'analysis']:
            if key in self.generator_data:
                observations = self._prepare_observations(self.generator_data[key])
                break
        
        return observations

    def _merge_additional_data(self, contract: WorldEngineOutput, 
                              additional_data: Dict[str, Any]) -> None:
        """Laczenie dodatkowych danych z kontraktem"""
        for section, data in additional_data.items():
            if section == 'results':
                contract.results.update(data)
            elif section == 'features':
                contract.features.update(data)
            elif section == 'models':
                contract.models.update(data)
            elif section == 'predictions':
                contract.predictions.update(data)
            elif section == 'observations':
                contract.observations.update(data)
            elif section == 'metadata':
                contract.metadata.update(data)

    def process(self, generator_data: Optional[Dict[str, Any]] = None, 
                additional_data: Optional[Dict[str, Any]] = None) -> WorldEngineOutput:
        """
        Pelny proces WorldEngine: odbior danych -> przygotowanie kontraktu.
        
        Args:
            generator_data: Nowe dane z generatora (opcjonalne, nadpisuje istniejace)
            additional_data: Dodatkowe dane do kontraktu
            
        Returns:
            WorldEngineOutput - przygotowany kontrakt danych
        """
        if generator_data is not None:
            self.receive_from_generator(generator_data)
        
        contract = self.prepare_contract(additional_data)
        
        # Zapisz w historii cyklu
        self.cycle_history.append(copy.deepcopy(contract))
        
        # Zaktualizuj stage
        self._processing_stage = "processed"
        
        self._log_event("processing_complete", {
            "contract_summary": {
                "results_count": len(contract.results),
                "features_count": len(contract.features),
                "models_count": len(contract.models),
                "predictions_count": len(contract.predictions),
                "observations_count": len(contract.observations)
            }
        })
        
        return contract

    def send_to_modeling(self, contract: WorldEngineOutput) -> Dict[str, Any]:
        """
        Przekazanie kontraktu danych do Modeling Layer.
        
        Args:
            contract: Kontrakt danych WorldEngineOutput
            
        Returns:
            Wynik przekazania do Modeling Layer
        """
        try:
            # Import Modeling Layer
            from SSI_V5.modeling import (
                normalizuj, normalizuj_dataframe,
                podziel_dane, podziel_dane_standard,
                poisson, dixon_coles
            )
            
            modeling_result = {
                'status': 'success',
                'layer': 'modeling',
                'contract_id': contract.metadata.get('cycle_id', 'unknown'),
                'processing_start': datetime.now().isoformat()
            }
            
            # Przetwarzanie w Modeling Layer - tutaj mozna dodac konkretna logike
            # Na razie zwracamy염 informationsze o udanym przekazaniu
            
            #'extérieur features
            if contract.features:
                modeling_result['features_processed'] = list(contract.features.keys())
            
            # Przetwarzanie cech
            if 'main' in contract.features and isinstance(contract.features['main'], dict):
                features_df = pd.DataFrame(contract.features['main'])
                modeling_result['features_shape'] = features_df.shape
                
                # Przyklad: normalizacja cech
                try:
                    normalized_features = normalizuj_dataframe(features_df)
                    modeling_result['features_normalized'] = True
                except Exception as e:
                    modeling_result['features_normalization_error'] = str(e)
            
            # exterior models
            if contract.models:
                modeling_result['models_loaded'] = list(contract.models.keys())
            
            modeling_result['processing_end'] = datetime.now().isoformat()
            
            # Zaktualizuj stage
            self._processing_stage = "modeling_sent"
            
            self._log_event("sent_to_modeling", modeling_result)
            
            return modeling_result
            
        except Exception as e:
            error_result = {
                'status': 'error',
                'error': str(e),
                'layer': 'modeling',
                'timestamp': datetime.now().isoformat()
            }
            
            self._log_event("modeling_error", error_result)
            return error_result

    def send_to_teacher(self, contract: WorldEngineOutput) -> Dict[str, Any]:
        """
        Przekazanie kontraktu danych i wynikow do Teacher Layer.
        
        Args:
            contract: Kontrakt danych WorldEngineOutput
            
        Returns:
            Wynik analizy Teacher Layer
        """
        try:
            # Import Teacher Layer
            from SSI_V5.teachers import (
                CognitiveTeacher,
                WorldHierarchyManager,
                DynamicWeightsManager,
                MemoryManager,
                ModelEvaluator
            )
            
            teacher_result = {
                'status': 'success',
                'layer': 'teacher',
                'contract_id': contract.metadata.get('cycle_id', 'unknown'),
                'processing_start': datetime.now().isoformat()
            }
            
            # Inicjalizacja CognitiveTeacher - jeśli są dane do analizy
            if contract.results and contract.features:
                try:
                    # Przygotowanie danych dla CognitiveTeacher
                    # CognitiveTeacher oczekuje DataFrame z kolumna 'wynik'
                    if 'main' in contract.results and 'main' in contract.features:
                        # Konwersja do DataFrame
                        results_data = contract.results['main']
                        features_data = contract.features['main']
                        
                        # Tworzenie DataFrame z cechami
                        if isinstance(features_data, dict):
                            df_features = pd.DataFrame(features_data)
                        else:
                            df_features = pd.DataFrame()
                        
                        # Dodanie kolumny 'wynik' jeśli istnieje
                        if isinstance(results_data, dict) and 'wynik' in results_data:
                            df_features['wynik'] = results_data['wynik']
                        
                        # Liste der Merkmale
                        cechy = list(df_features.columns.difference(['wynik'])) if 'wynik' in df_features.columns else list(df_features.columns)
                        
                        if cechy and 'wynik' in df_features.columns:
                            # Inicjalizacja CognitiveTeacher
                            cognitive_teacher = CognitiveTeacher(
                                df=df_features,
                                cechy=cechy,
                                siec_name=f"world_{contract.metadata.get('cycle_id', 'default')}"
                            )
                            
                            teacher_result['cognitive_teacher_initialized'] = True
                            teacher_result['analyzed_features'] = cechy
                            teacher_result['samples_count'] = len(df_features)
                            
                            # Można tu dodać konkretne wywoływanie metod CognitiveTeacher
                            # Na razie sprawdzamy tylko inicjalizację
                        else:
                            teacher_result['cognitive_teacher_skip_reason'] = 'missing_required_data'
                    
                except Exception as e:
                    teacher_result['cognitive_teacher_error'] = str(e)
            
            # Inicjalizacja WorldHierarchyManager
            try:
                world_hierarchy = WorldHierarchyManager()
                teacher_result['world_hierarchy_initialized'] = True
            except Exception as e:
                teacher_result['world_hierarchy_error'] = str(e)
            
            # Inicjalizacja innych managerow
            teacher_components = {
                'DynamicWeightsManager': DynamicWeightsManager,
                'MemoryManager': MemoryManager,
                'ModelEvaluator': ModelEvaluator
            }
            
            for name, component_class in teacher_components.items():
                try:
                    instance = component_class()
                    teacher_result[f'{name}_initialized'] = True
                except Exception as e:
                    teacher_result[f'{name}_error'] = str(e)
            
            teacher_result['processing_end'] = datetime.now().isoformat()
            
            # Zaktualizuj stage
            self._processing_stage = "teacher_sent"
            
            self._log_event("sent_to_teacher", teacher_result)
            
            return teacher_result
            
        except Exception as e:
            error_result = {
                'status': 'error',
                'error': str(e),
                'layer': 'teacher',
                'timestamp': datetime.now().isoformat()
            }
            
            self._log_event("teacher_error", error_result)
            return error_result

    def get_cycle_history(self, limit: Optional[int] = None) -> List[WorldEngineOutput]:
        """
        Pobranie historii cykli.
        
        Args:
            limit: Maksymalna liczba cykli do zwrocenia (opcjonalne)
            
        Returns:
            Lista kontraktow z historii cykli
        """
        if limit is None:
            return copy.deepcopy(self.cycle_history)
        else:
            return copy.deepcopy(self.cycle_history[-limit:])

    def get_current_context(self) -> ProcessingContext:
        """Pobranie biezacego kontekstu przetwarzania"""
        return copy.deepcopy(self.context)

    def get_processing_stage(self) -> str:
        """Pobranie biezacego etapu przetwarzania"""
        return self._processing_stage

    def reset_cycle(self) -> None:
        """Resetowanie silnika dla nowego cyklu"""
        self.generator_data = {}
        self._processing_stage = "initialized"
        self.context = ProcessingContext(
            cycle_id=f"{self.world_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            world_name=self.world_name
        )
        self._event_log = []

    def get_event_log(self) -> List[Dict[str, Any]]:
        """Pobranie dziennika zdarzen"""
        return copy.deepcopy(getattr(self, '_event_log', []))


# Funkcje pomocnicze dla integracji z istniejacym kodem

def create_world_engine_from_generator(generator_reference: str = "SSI_V5_SPORTS_WORLD_MODEL_GENERATOR",
                                       world_name: str = "SSI_V5_WORLD") -> WorldEngine:
    """
    Fabryka WorldEngine dla integracji z istniejacym generatorem.
    
    Args:
        generator_reference: Referencja do generatora
        world_name: Nazwa swiata
        
    Returns:
        Zainicjalizowany WorldEngine
    """
    engine = WorldEngine(world_name=world_name)
    engine.context.generator_reference = generator_reference
    return engine


def create_world_engineOutput_from_dict(data: Dict[str, Any]) -> WorldEngineOutput:
    """
    Tworzenie WorldEngineOutput z slownika.
    
    Args:
        data: Slownik z danymi kontraktu
        
    Returns:
        WorldEngineOutput
    """
    output = WorldEngineOutput()
    
    for section in ['results', 'features', 'models', 'predictions', 'observations', 'metadata']:
        if section in data:
            setattr(output, section, copy.deepcopy(data[section]))
    
    return output


# Eksportowane funkcje i klasy
__all__ = [
    'WorldEngineOutput',
    'ProcessingContext', 
    'WorldEngine',
    'create_world_engine_from_generator',
    'create_world_engineOutput_from_dict'
]
