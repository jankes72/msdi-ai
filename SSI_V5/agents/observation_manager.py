# SSI V5 Agent Layer - Observation Manager
# ==================================================
#
# ETAP: 5.2.4 FAZA 4
# Data: 2026-08-03
# 
# Odpowiedzialnosc:
# - Zarządzanie obserwacjami agenta
# - Analiza i zapamiętywanie wyników obserwacji
# - Integracja z pamięcią agenta
# - Tworzenie raportów obserwacyjnych

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Callable
from enum import Enum
from datetime import datetime, timedelta
import uuid
import copy
import json
import pandas as pd
import numpy as np


class ObservationType(Enum):
    """Typy obserwacji"""
    WORLD_STATE = "world_state"              # Stan świata
    MODEL_PERFORMANCE = "model_performance"    # Wydajność modelu
    WEIGHT_ANALYSIS = "weight_analysis"        # Analiza wag
    DECISION_OUTCOME = "decision_outcome"      # Wynik decyzji
    SYSTEM_FEEDBACK = "system_feedback"        # Informacja zwrotna od systemu
    CONTRACT_DATA = "contract_data"            # Dane z kontraktu


class ObservationStatus(Enum):
    """Statusy obserwacji"""
    NEW = "new"                          # Nowa obserwacja
    PROCESSED = "processed"                # Przetworzona
    ANALYZED = "analyzed"                 # Zanalizowana
    ARCHIVED = "archived"                 # Zarchiwizowana


@dataclass
class Observation:
    """Pojedyncza obserwacja agenta"""
    observation_id: str
    observation_type: ObservationType
    agent_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    priority: int = 0
    status: ObservationStatus = ObservationStatus.NEW
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    analysis: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            'observation_id': self.observation_id,
            'observation_type': self.observation_type.value,
            'agent_id': self.agent_id,
            'data': copy.deepcopy(self.data),
            'metadata': copy.deepcopy(self.metadata),
            'confidence': self.confidence,
            'priority': self.priority,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'analysis': copy.deepcopy(self.analysis) if self.analysis else None
        }
    
    def process(self, analysis_data: Optional[Dict[str, Any]] = None) -> None:
        """Przetworzenie obserwacji"""
        self.status = ObservationStatus.PROCESSED
        self.processed_at = datetime.now()
        self.analysis = analysis_data or {}
    
    def analyze(self, analysis_data: Dict[str, Any]) -> None:
        """Analiza obserwacji"""
        self.status = ObservationStatus.ANALYZED
        self.analysis = analysis_data
        self.processed_at = datetime.now()
    
    def archive(self) -> None:
        """Archiwizacja obserwacji"""
        self.status = ObservationStatus.ARCHIVED


@dataclass
class ObservationBatch:
    """Zbiór obserwacji (np. z jednego cyklu)"""
    batch_id: str
    cycle_id: str
    observations: List[Observation] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    summary: Dict[str, Any] = field(default_factory=dict)
    
    def add_observation(self, observation: Observation) -> None:
        """Dodanie obserwacji do zbioru"""
        self.observations.append(observation)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            'batch_id': self.batch_id,
            'cycle_id': self.cycle_id,
            'observations': [obs.to_dict() for obs in self.observations],
            'created_at': self.created_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'summary': copy.deepcopy(self.summary),
            'observation_count': len(self.observations)
        }


@dataclass
class ObservationReport:
    """Raport obserwacyjny"""
    report_id: str
    agent_id: str
    period_start: datetime
    period_end: datetime
    total_observations: int = 0
    observations_by_type: Dict[str, int] = field(default_factory=dict)
    key_findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika"""
        return {
            'report_id': self.report_id,
            'agent_id': self.agent_id,
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'total_observations': self.total_observations,
            'observations_by_type': copy.deepcopy(self.observations_by_type),
            'key_findings': copy.deepcopy(self.key_findings),
            'recommendations': copy.deepcopy(self.recommendations),
            'statistics': copy.deepcopy(self.statistics),
            'generated_at': self.generated_at.isoformat()
        }


class ObservationManager:
    """
    Menadżer obserwacji - zarządza obserwacjami i analizą ich wyników.
    
    Odpowiedzialność:
    - Zbieranie obserwacji
    - Przetwarzanie i analiza obserwacji
    - Generowanie raportów
    - Integracja z pamięcią agenta
    """
    
    def __init__(self, agent_id: str):
        """
        Inicjalizacja Observation Manager.
        
        Args:
            agent_id: ID agenta
        """
        self.agent_id = agent_id
        self.memory: Optional[Any] = None  # Referencja do AgentMemory
        
        # Kolekcja obserwacji
        self.observations: List[Observation] = []
        self.observation_batches: List[ObservationBatch] = []
        
        # Bufor na nowe obserwacje
        self._new_observations: List[Observation] = []
        
        # Statystyki
        self.total_observations = 0
        self.observations_by_type: Dict[str, int] = {}
        self.processed_count = 0
        self.analyzed_count = 0
        
        # Inicjalizacja typów obserwacji
        self._initialize_observation_types()
        
        # Konfiguracja
        self.max_observations_in_memory = 1000
        self.batch_size = 10
        
        # Rejestry callbacków
        self._observation_callbacks: List[Callable] = []
        
        # Flagi
        self._initialized = False
    
    def initialize(self) -> Dict[str, Any]:
        """
        Inicjalizacja menadżera obserwacji.
        
        Returns:
            Status inicjalizacji
        """
        if self._initialized:
            return {
                'status': 'success',
                'message': 'ObservationManager already initialized',
                'agent_id': self.agent_id
            }
        
        try:
            self._initialized = True
            self._initialize_observation_types()
            
            return {
                'status': 'success',
                'message': 'ObservationManager initialized',
                'agent_id': self.agent_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Initialization failed: {str(e)}',
                'agent_id': self.agent_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _initialize_observation_types(self) -> None:
        """Inicjalizacja liczników typów obserwacji"""
        for obs_type in ObservationType:
            self.observations_by_type[obs_type.value] = 0
    
    def add_observation(self, observation_data: Dict[str, Any], 
                        observation_type: Optional[Union[ObservationType, str]] = None) -> str:
        """
        Dodanie nowej obserwacji.
        
        Args:
            observation_data: Dane obserwacji
            observation_type: Typ obserwacji (opcjonalny, domyślnie WORLD_STATE)
            
        Returns:
            ID nowej obserwacji
        """
        # Określenie typu
        if observation_type is None:
            obs_type = ObservationType.WORLD_STATE
        elif isinstance(observation_type, str):
            try:
                obs_type = ObservationType(observation_type)
            except ValueError:
                obs_type = ObservationType.WORLD_STATE
        else:
            obs_type = observation_type
        
        # Generacja ID
        observation_id = f"obs_{self.agent_id}_{uuid.uuid4().hex[:8]}"
        
        # Utworzenie obserwacji
        observation = Observation(
            observation_id=observation_id,
            observation_type=obs_type,
            agent_id=self.agent_id,
            data=copy.deepcopy(observation_data),
            metadata={
                'timestamp': datetime.now().isoformat(),
                'source': observation_data.get('source', 'agent'),
                'cycle_id': observation_data.get('cycle_id', ''),
                'contract_id': observation_data.get('contract_id', '')
            },
            confidence=observation_data.get('confidence', 0.5),
            priority=observation_data.get('priority', 0),
            created_at=datetime.now()
        )
        
        # Dodanie do kolekcji
        self._new_observations.append(observation)
        self.total_observations += 1
        self.observations_by_type[obs_type.value] += 1
        
        # Zapisanie w pamięci
        if self.memory:
            self.memory.add_observation(observation.to_dict())
        
        # Sprawdzenie, czy należy utworzyć nowy batch
        if len(self._new_observations) >= self.batch_size:
            self._create_batch()
        
        # Powiadomienie callbacków
        self._notify_observation_callbacks(observation)
        
        return observation_id
    
    def _create_batch(self) -> ObservationBatch:
        """Utworzenie nowego zbioru obserwacji"""
        if not self._new_observations:
            return None
        
        batch_id = f"batch_{self.agent_id}_{uuid.uuid4().hex[:8]}"
        
        # Określenie ID cyklu z pierwszej obserwacji
        first_obs = self._new_observations[0]
        cycle_id = first_obs.metadata.get('cycle_id', f"cycle_{datetime.now().isoformat()}")
        
        batch = ObservationBatch(
            batch_id=batch_id,
            cycle_id=cycle_id,
            observations=copy.deepcopy(self._new_observations),
            created_at=datetime.now()
        )
        
        # Generowanie podsumowania
        batch.summary = self._generate_batch_summary(batch)
        
        self.observation_batches.append(batch)
        self._new_observations.clear()
        
        # Archwizacja starych batchy
        if len(self.observation_batches) > 100:
            self._archive_old_batches()
        
        return batch
    
    def _generate_batch_summary(self, batch: ObservationBatch) -> Dict[str, Any]:
        """Generowanie podsumowania zbioru obserwacji"""
        summary = {
            'observation_count': len(batch.observations),
            'types': {},
            'priority_distribution': {},
            'confidence_distribution': {},
            'data_keys': set(),
            'metadata_keys': set()
        }
        
        priority_ranges = {'low': 0, 'medium': 0, 'high': 0}
        confidence_ranges = {'low': 0, 'medium': 0, 'high': 0}
        
        for observation in batch.observations:
            # Typy
            obs_type = observation.observation_type.value
            summary['types'][obs_type] = summary['types'].get(obs_type, 0) + 1
            
            # Priorytety
            if observation.priority < 3:
                priority_ranges['low'] += 1
            elif observation.priority < 7:
                priority_ranges['medium'] += 1
            else:
                priority_ranges['high'] += 1
            
            # Pewność
            if observation.confidence < 0.4:
                confidence_ranges['low'] += 1
            elif observation.confidence < 0.7:
                confidence_ranges['medium'] += 1
            else:
                confidence_ranges['high'] += 1
            
            # Klucze
            summary['data_keys'].update(observation.data.keys())
            summary['metadata_keys'].update(observation.metadata.keys())
        
        summary['priority_distribution'] = priority_ranges
        summary['confidence_distribution'] = confidence_ranges
        
        return summary
    
    def receive_world_data(self, world_data: Dict[str, Any], 
                          cycle_id: Optional[str] = None,
                          world_name: Optional[str] = None) -> str:
        """
        Odbiór danych o stanie świata ( z WorldEngine/Contract).
        
        Args:
            world_data: Dane o stanie świata
            cycle_id: ID cyklu (opcjonalny)
            world_name: Nazwa świata (opcjonalny)
            
        Returns:
            ID nowej obserwacji
        """
        observation_data = {
            'type': 'world_state',
            'world_data': world_data,
            'world_name': world_name or '',
            'cycle_id': cycle_id or '',
            'source': 'world_engine',
            'confidence': 0.8,
            'priority': 5
        }
        
        return self.add_observation(observation_data, ObservationType.WORLD_STATE)
    
    def receive_contract_data(self, contract_data: Dict[str, Any], 
                            contract_id: Optional[str] = None) -> str:
        """
        Odbiór danych z kontraktu.
        
        Args:
            contract_data: Dane kontraktu
            contract_id: ID kontraktu (opcjonalny)
            
        Returns:
            ID nowej obserwacji
        """
        observation_data = {
            'type': 'contract_data',
            'contract_data': contract_data,
            'contract_id': contract_id or contract_data.get('contract_id', ''),
            'cycle_id': contract_data.get('cycle_id', ''),
            'world_name': contract_data.get('world_name', ''),
            'source': 'agent_contract',
            'confidence': 0.9,
            'priority': 6
        }
        
        return self.add_observation(observation_data, ObservationType.CONTRACT_DATA)
    
    def receive_model_evaluation(self, evaluation_data: Dict[str, Any]) -> str:
        """
        Odbiór oceny modelu od Teacher Layer.
        
        Args:
            evaluation_data: Dane oceny
            
        Returns:
            ID nowej obserwacji
        """
        observation_data = {
            'type': 'model_evaluation',
            'evaluation_data': evaluation_data,
            'source': 'teacher_layer',
            'confidence': 0.7,
            'priority': 5
        }
        
        return self.add_observation(observation_data, ObservationType.MODEL_PERFORMANCE)
    
    def receive_system_feedback(self, feedback_data: Dict[str, Any]) -> str:
        """
        Odbiór informacji zwrotnej od systemu.
        
        Args:
            feedback_data: Dane informacji zwrotnej
            
        Returns:
            ID nowej obserwacji
        """
        observation_data = {
            'type': 'system_feedback',
            'feedback_data': feedback_data,
            'source': 'pipeline',
            'confidence': 0.6,
            'priority': 4
        }
        
        return self.add_observation(observation_data, ObservationType.SYSTEM_FEEDBACK)
    
    def process_observations(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Przetworzenie oczekujących obserwacji.
        
        Args:
            limit: Maksymalna liczba obserwacji do przetworzenia
            
        Returns:
            Status przetworzenia
        """
        to_process = self._new_observations if not limit else self._new_observations[:limit]
        
        processed_count = 0
        
        for observation in to_process:
            # Symulacja przetworzenia
            self._basic_analysis(observation)
            observation.process()
            processed_count += 1
        
        self.processed_count += processed_count
        
        # Wykonaj batchowanie
        if len(self._new_observations) >= self.batch_size:
            self._create_batch()
        
        return {
            'status': 'success',
            'processed_count': processed_count,
            'remaining': len(self._new_observations),
            'timestamp': datetime.now().isoformat()
        }
    
    def _basic_analysis(self, observation: Observation) -> None:
        """Podstawowa analiza obserwacji"""
        analysis = {
            'analyzed_at': datetime.now().isoformat(),
            'basic_metrics': {}
        }
        
        # Analiza danych obserwacji
        if observation.data:
            analysis['basic_metrics'] = {
                'data_size': self._calculate_data_size(observation.data),
                'numeric_values': self._count_numeric_values(observation.data),
                'text_length': self._calculate_text_length(observation.data)
            }
        
        observation.analysis = analysis
    
    def _calculate_data_size(self, data: Dict[str, Any]) -> int:
        """Obliczenie rozmiaru danych"""
        return len(json.dumps(data)) if data else 0
    
    def _count_numeric_values(self, data: Any) -> int:
        """Zliczanie wartości numerycznych"""
        count = 0
        
        if isinstance(data, dict):
            for value in data.values():
                count += self._count_numeric_values(value)
        elif isinstance(data, (list, tuple)):
            for item in data:
                count += self._count_numeric_values(item)
        elif isinstance(data, (int, float, np.number)):
            count += 1
        
        return count
    
    def _calculate_text_length(self, data: Any) -> int:
        """Obliczenie łącznej długości tekstu"""
        length = 0
        
        if isinstance(data, dict):
            for value in data.values():
                length += self._calculate_text_length(value)
        elif isinstance(data, (list, tuple)):
            for item in data:
                length += self._calculate_text_length(item)
        elif isinstance(data, str):
            length += len(data)
        
        return length
    
    def analyze_observations(self, observation_ids: Optional[List[str]] = None, 
                             limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Zaawansowana analiza obserwacji.
        
        Args:
            observation_ids: Lista ID obserwacji do analizy
            limit: Maksymalna liczba obserwacji
            
        Returns:
            Wynik analizy
        """
        observations_to_analyze = []
        
        if observation_ids:
            observations_to_analyze = [
                obs for obs in self.observations 
                if obs.observation_id in observation_ids
            ]
        elif limit:
            observations_to_analyze = self.observations[-limit:]
        else:
            observations_to_analyze = self.observations
        
        analyzed_count = 0
        findings = []
        
        for observation in observations_to_analyze:
            # Zaawansowana analiza
            advanced_analysis = self._advanced_analysis(observation)
            observation.analyze(advanced_analysis)
            analyzed_count += 1
            
            if advanced_analysis.get('findings'):
                findings.extend(advanced_analysis['findings'])
        
        self.analyzed_count += analyzed_count
        
        return {
            'status': 'success',
            'analyzed_count': analyzed_count,
            'total_observations': len(self.observations),
            'key_findings': findings,
            'timestamp': datetime.now().isoformat()
        }
    
    def _advanced_analysis(self, observation: Observation) -> Dict[str, Any]:
        """Zaawansowana analiza obserwacji"""
        analysis = {
            'findings': [],
            'metrics': {},
            'recommendations': []
        }
        
        # Analiza typu obserwacji
        if observation.observation_type == ObservationType.WORLD_STATE:
            analysis = self._analyze_world_state(observation)
        elif observation.observation_type == ObservationType.MODEL_PERFORMANCE:
            analysis = self._analyze_model_performance(observation)
        elif observation.observation_type == ObservationType.WEIGHT_ANALYSIS:
            analysis = self._analyze_weight_distribution(observation)
        
        return analysis
    
    def _analyze_world_state(self, observation: Observation) -> Dict[str, Any]:
        """Analiza stanu świata"""
        analysis = {
            'findings': [],
            'metrics': {},
            'recommendations': []
        }
        
        world_data = observation.data.get('world_data', {})
        
        if world_data:
            # Analiza rozkładu wartości
            numeric_values = self._extract_numeric_values(world_data)
            
            if numeric_values:
                analysis['metrics'] = {
                    'mean': np.mean(numeric_values) if numeric_values else 0,
                    'std': np.std(numeric_values) if len(numeric_values) > 1 else 0,
                    'min': min(numeric_values) if numeric_values else 0,
                    'max': max(numeric_values) if numeric_values else 0
                }
        
        return analysis
    
    def _analyze_model_performance(self, observation: Observation) -> Dict[str, Any]:
        """Analiza wydajności modelu"""
        analysis = {
            'findings': [],
            'metrics': {},
            'recommendations': []
        }
        
        evaluation_data = observation.data.get('evaluation_data', {})
        
        if evaluation_data:
            # Wyekstrahowanie metryk wydajności
            accuracy = evaluation_data.get('accuracy', 0)
            precision = evaluation_data.get('precision', 0)
            recall = evaluation_data.get('recall', 0)
            f1_score = evaluation_data.get('f1_score', 0)
            
            analysis['metrics'] = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1_score,
                'overall_performance': (accuracy + precision + recall + f1_score) / 4 if (accuracy + precision + recall + f1_score) > 0 else 0
            }
            
            # Generowanie wniosków
            if accuracy > 0.8:
                analysis['findings'].append('Model wykazuje wysoką dokładność')
            elif accuracy < 0.6:
                analysis['findings'].append('Model wykazuje niską dokładność - zalecana optymalizacja')
            
            # Generowanie rekomendacji
            if accuracy < 0.7:
                analysis['recommendations'].append({
                    'type': 'model_optimization',
                    'priority': 'high',
                    'description': 'Optymalizacja modelu aby poprawić dokładność'
                })
        
        return analysis
    
    def _analyze_weight_distribution(self, observation: Observation) -> Dict[str, Any]:
        """Analiza rozkładu wag"""
        analysis = {
            'findings': [],
            'metrics': {},
            'recommendations': []
        }
        
        weights = observation.data.get('weights', {})
        
        if weights:
            weight_values = list(weights.values())
            
            analysis['metrics'] = {
                'mean': np.mean(weight_values),
                'std': np.std(weight_values),
                'min': min(weight_values),
                'max': max(weight_values),
                'balanced': 'yes' if 0.3 < np.mean(weight_values) < 0.7 else 'no'
            }
        
        return analysis
    
    def _extract_numeric_values(self, data: Any) -> List[float]:
        """Wyekstrahowanie wartości numerycznych"""
        values = []
        
        if isinstance(data, dict):
            for value in data.values():
                values.extend(self._extract_numeric_values(value))
        elif isinstance(data, (list, tuple)):
            for item in data:
                values.extend(self._extract_numeric_values(item))
        elif isinstance(data, (int, float, np.number)):
            values.append(float(data))
        
        return values
    
    def generate_report(self, period_days: int = 7) -> ObservationReport:
        """
        Generowanie raportu obserwacyjnego za dany okres.
        
        Args:
            period_days: Liczba dni (domyślnie 7)
            
        Returns:
            Raport obserwacyjny
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Filtrowanie obserwacji z okresu
        period_observations = [
            obs for obs in self.observations 
            if start_date <= obs.created_at <= end_date
        ]
        
        # Tworzenie raportu
        report = ObservationReport(
            report_id=f"report_{self.agent_id}_{uuid.uuid4().hex[:8]}",
            agent_id=self.agent_id,
            period_start=start_date,
            period_end=end_date,
            total_observations=len(period_observations),
            generated_at=datetime.now()
        )
        
        # Statystyki według typów
        for obs_type in ObservationType:
            count = len([
                obs for obs in period_observations 
                if obs.observation_type.value == obs_type.value
            ])
            report.observations_by_type[obs_type.value] = count
        
        # Kluczowe wnioski
        report.key_findings = self._extract_key_findings(period_observations)
        
        # Rekomendacje
        report.recommendations = self._generate_report_recommendations(report.key_findings)
        
        # Statystyki
        report.statistics = self._calculate_report_statistics(period_observations)
        
        # Zapisanie raportu w pamięci
        if self.memory:
            self.memory.store_in_long_term(f"report_{report.report_id}", report.to_dict())
        
        return report
    
    def _extract_key_findings(self, observations: List[Observation]) -> List[Dict[str, Any]]:
        """Wyciągnięcie kluczowych wniosków z obserwacji"""
        findings = []
        
        # Analiza typów obserwacji
        type_counts = {}
        for obs in observations:
            type_counts[obs.observation_type.value] = type_counts.get(obs.observation_type.value, 0) + 1
        
        most_common_type = max(type_counts.items(), key=lambda x: x[1]) if type_counts else (None, 0)
        findings.append({
            'type': 'observation_trend',
            'description': f'Najczęstszy typ obserwacji: {most_common_type[0]} ({most_common_type[1]} razy)',
            'severity': 'low'
        })
        
        # Analiza pewności
        confidences = [obs.confidence for obs in observations if isinstance(obs.confidence, (int, float))]
        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            if avg_confidence > 0.7:
                findings.append({
                    'type': 'confidence_level',
                    'description': f'Średnia pewność obserwacji: {avg_confidence:.2f} (wysoka)',
                    'severity': 'low'
                })
            elif avg_confidence < 0.5:
                findings.append({
                    'type': 'confidence_level',
                    'description': f'Średnia pewność obserwacji: {avg_confidence:.2f} (niska)',
                    'severity': 'medium'
                })
        
        return findings
    
    def _generate_report_recommendations(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generowanie rekomendacji na podstawie wniosków"""
        recommendations = []
        
        for finding in findings:
            if finding['type'] == 'confidence_level' and 'niska' in finding['description']:
                recommendations.append({
                    'type': 'improve_data_quality',
                    'priority': 'high',
                    'description': 'Poprawić jakość danych wejściowych aby zwiększyć pewność obserwacji',
                    'related_finding': finding['type']
                })
        
        return recommendations
    
    def _calculate_report_statistics(self, observations: List[Observation]) -> Dict[str, Any]:
        """Obliczenie statystyk dla raportu"""
        if not observations:
            return {}
        
        # Czasowe statystyki
        timestamps = [obs.created_at.timestamp() for obs in observations]
        
        return {
            'earliest_observation': min(timestamps) if timestamps else 0,
            'latest_observation': max(timestamps) if timestamps else 0,
            'observation_frequency': len(observations) / len(timestamps) if timestamps else 0,
            'avg_confidence': np.mean([obs.confidence for obs in observations if isinstance(obs.confidence, (int, float))]) if observations else 0,
            'avg_priority': np.mean([obs.priority for obs in observations]) if observations else 0
        }
    
    def _archive_old_batches(self, max_batches: int = 100) -> None:
        """Archiwizacja starych zbiorów obserwacji"""
        if len(self.observation_batches) > max_batches:
            # Usunięcie najstarszych batchy
            batches_to_remove = len(self.observation_batches) - max_batches
            self.observation_batches = self.observation_batches[batches_to_remove:]
    
    def get_observations(self, observation_type: Optional[Union[ObservationType, str]] = None,
                         limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Pobranie obserwacji według kryteriów.
        
        Args:
            observation_type: Typ obserwacji (opcjonalny)
            limit: Maksymalna liczba obserwacji
            
        Returns:
            Lista obserwacji
        """
        observations = self.observations
        
        if observation_type:
            obs_type = ObservationType(observation_type) if isinstance(observation_type, str) else observation_type
            observations = [obs for obs in observations if obs.observation_type == obs_type]
        
        if limit:
            observations = observations[-limit:]
        
        return [obs.to_dict() for obs in observations]
    
    def get_observation_statistics(self) -> Dict[str, Any]:
        """Pobranie statystyk obserwacji"""
        return {
            'total_observations': self.total_observations,
            'processed_count': self.processed_count,
            'analyzed_count': self.analyzed_count,
            'observations_by_type': copy.deepcopy(self.observations_by_type),
            'new_observations': len(self._new_observations),
            'batch_count': len(self.observation_batches)
        }
    
    def clear_observations(self) -> None:
        """Wyczyszczenie obserwacji"""
        self.observations.clear()
        self._new_observations.clear()
        self.total_observations = 0
        self.processed_count = 0
        self.analyzed_count = 0
        self._initialize_observation_types()
    
    # Obsługa callbacków
    def on_observation_added(self, callback: Callable) -> None:
        """Rejestracja callbacka na dodanie obserwacji"""
        self._observation_callbacks.append(callback)
    
    def _notify_observation_callbacks(self, observation: Observation) -> None:
        """Powiadomienie callbacków o dodaniu obserwacji"""
        for callback in self._observation_callbacks:
            try:
                callback(observation, self)
            except Exception:
                pass


# Eksportowane funkcje i klasy
__all__ = [
    'ObservationType',
    'ObservationStatus',
    'Observation',
    'ObservationBatch',
    'ObservationReport',
    'ObservationManager'
]
