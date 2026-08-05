"""
SSI V5 - Memory Document Adapter
ETAP: 5.4.1 - Memory Embedding Foundation

Odpowiedzialnosc:
- Konwersja istniejacych typow pamieci SSI V5 na spójna strukture dokumentu
- Obsluga wszystkich typow pamieci:
  * StrategyMemoryRecord
  * MatchResult (z match_result_memory)
  * TrainingMemory, ObservationMemory, BehaviorMemory, AgentAnalysisMemory, DecisionMemory
  * ModelMemoryStore records

ZASADY:
1. NIE modyfikowac istniejacych klas pamieci
2. Adapter TYLKO konwertuje, NIE przechowuje
3. Kazdy typ pamieci ma swoja metode adaptacyjna
4. Wyjsciowa struktura to CollectiveMemoryDocument

Autor: SSI V5 System / Mistral Vibe
Data: 2026-08-04
Wersja: 1.0.0
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import json
import uuid


@dataclass
class CollectiveMemoryDocument:
    """
    Unifikowana struktura dokumentu pamięci dla systemu Collective Memory.
    
    To jest format wejściowy dla EmbeddingGenerator i VectorIndex.
    
    Attributes:
        document_id: Unikalne ID dokumentu (generowane automatycznie)
        source_id: ID zródełowego rekordu pamięci (np. strategy_id, match_id)
        source_type: Typ źródłowej pamięci (strategy_memory, match_result, etc.)
        text: Tekst do konwersji na embedding (główna treść)
        metadata: Dodatkowe metadane (strukturizowane dane)
        timestamp: Data stworzenia/aktualizacji dokumentu
        importance: Waga/ważność dokumentu (0.0-1.0)
        tags: Lista tagów dla klasyfikacji
    """
    
    # Unikalne identyfikatory
    document_id: str = field(default_factory=lambda: f"cmd_{uuid.uuid4().hex[:12]}")
    source_id: str = ""
    source_type: str = ""  # strategy_memory, match_result, training_memory, etc.
    
    # Tresc dokumentu
    text: str = ""
    
    # Metadane
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Czas
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Waga i klasyfikacja
    importance: float = 0.5  # 0.0 - 1.0, domyslnie 0.5
    tags: List[str] = field(default_factory=list)
    
    # Serializacja
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do dict (dla JSON)."""
        result = asdict(self)
        # Konwersja datetime do ISO format
        if isinstance(result['timestamp'], datetime):
            result['timestamp'] = self.timestamp.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CollectiveMemoryDocument':
        """Konwersja z dict (z JSON)."""
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)
    
    def to_json(self) -> str:
        """Konwersja do JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'CollectiveMemoryDocument':
        """Konwersja z JSON."""
        return cls.from_dict(json.loads(json_str))


class MemoryDocumentAdapter:
    """
    Adapter konwertujacy istniejace typy pamieci SSI V5 na CollectiveMemoryDocument.
    
    Obslugiwane typy pamieci:
    - StrategyMemoryRecord (z SSI_V5/memory/strategy_memory.py)
    - MatchResult (z SSI_V5/ingestion/result_models.py)
    - TrainingMemory, ObservationMemory, BehaviorMemory, AgentAnalysisMemory, DecisionMemory
      (z SSI/V5/memory/memory_types.py)
    
    Metody:
    - adapt_strategy_memory(record) -> CollectiveMemoryDocument
    - adapt_match_result(record) -> CollectiveMemoryDocument
    - adapt_training_memory(record) -> CollectiveMemoryDocument
    - adapt_observation_memory(record) -> CollectiveMemoryDocument
    - adapt_behavior_memory(record) -> CollectiveMemoryDocument
    - adapt_agent_analysis_memory(record) -> CollectiveMemoryDocument
    - adapt_decision_memory(record) -> CollectiveMemoryDocument
    - adapt_any(record) -> CollectiveMemoryDocument (auto-detekcja)
    """
    
    def __init__(self):
        self._type_registry = {}
        self._register_adapters()
    
    def _register_adapters(self):
        """Rejestracja metod adaptera dla roznych typow."""
        self._type_registry = {
            'StrategyMemoryRecord': self.adapt_strategy_memory,
            'MatchResult': self.adapt_match_result,
            'TrainingMemory': self.adapt_training_memory,
            'ObservationMemory': self.adapt_observation_memory,
            'BehaviorMemory': self.adapt_behavior_memory,
            'AgentAnalysisMemory': self.adapt_agent_analysis_memory,
            'DecisionMemory': self.adapt_decision_memory,
        }
    
    def get_supported_types(self) -> List[str]:
        """Zwraca liste obslugiwanych typow pamieci."""
        return list(self._type_registry.keys())
    
    def adapt_any(self, record: Any) -> Optional[CollectiveMemoryDocument]:
        """
        Konwertuje dowolny rekord pamieci na CollectiveMemoryDocument.
        Auto-detekcja typu na podstawie nazwy klasy.
        
        Args:
            record: Rekord pamieci (obiekt klasy pamieci)
            
        Returns:
            CollectiveMemoryDocument lub None jesli typ nieobslugiwany
        """
        class_name = type(record).__name__
        adapter_method = self._type_registry.get(class_name)
        
        if adapter_method:
            return adapter_method(record)
        else:
            # Proba detekcji po polach klasy
            for type_name, method in self._type_registry.items():
                if self._is_type(record, type_name):
                    return method(record)
        
        return None
    
    def _is_type(self, record: Any, type_name: str) -> bool:
        """Sprawdza czy rekord jest danego typu."""
        # Implementacja detekcji po polach charakterystycznych
        type_fields = {
            'StrategyMemoryRecord': ['memory_id', 'strategy_id', 'strategy_version'],
            'MatchResult': ['match_id', 'home_team', 'away_team'],
            'TrainingMemory': ['session_id', 'training_data_count'],
            'ObservationMemory': ['observation_id', 'scope'],
            'BehaviorMemory': ['behavior_id', 'behavior_type'],
            'AgentAnalysisMemory': ['analysis_id', 'analysis_type'],
            'DecisionMemory': ['decision_id', 'decision_outcome'],
        }
        
        required_fields = type_fields.get(type_name, [])
        if required_fields:
            return all(hasattr(record, field) for field in required_fields)
        return False
    
    # ========================================================================
    # ADAPTERY DLA POSZCZEGOLNYCH TYPÓW PAMIĘCI
    # ========================================================================
    
    def adapt_strategy_memory(self, record: Any) -> CollectiveMemoryDocument:
        """
        Konwertuje StrategyMemoryRecord na CollectiveMemoryDocument.
        
        Format tekstu zawiera:
        - Nazwe/ID strategii
        - Definicje strategii
        - Parametry
        - Historie eksperymentow (podsumowanie)
        - Ranking i confidence
        - Status
        """
        # Tekst dokumentu
        text_parts = []
        text_parts.append(f"STRATEGY: {record.strategy_id}")
        text_parts.append(f"Version: {record.strategy_version}")
        text_parts.append(f"Status: {record.status}")
        
        if record.strategy_definition:
            def_str = json.dumps(record.strategy_definition, ensure_ascii=False, default=str)
            text_parts.append(f"Definition: {def_str}")
        
        if record.strategy_parameters:
            params_str = json.dumps(record.strategy_parameters, ensure_ascii=False, default=str)
            text_parts.append(f"Parameters: {params_str}")
        
        if record.feature_schema:
            text_parts.append(f"Features: {', '.join(record.feature_schema)}")
        
        if hasattr(record, 'ranking_position'):
            text_parts.append(f"Ranking: {record.ranking_position}")
        if hasattr(record, 'confidence_score'):
            text_parts.append(f"Confidence: {record.confidence_score:.3f}")
        
        # Podsumowanie eksperymentów
        if record.EXPERIMENT_HISTORY:
            exp_count = len(record.EXPERIMENT_HISTORY)
            text_parts.append(f"Experiments: {exp_count}")
            
            # Ostatni eksperyment
            last_exp = record.EXPERIMENT_HISTORY[-1]
            if 'result' in last_exp:
                result_str = json.dumps(last_exp['result'], ensure_ascii=False, default=str)
                text_parts.append(f"Last Experiment Result: {result_str}")
        
        # Tekst dokumentu
        text = "\n".join(text_parts)
        
        # Metadane
        metadata = {
            'strategy_id': record.strategy_id,
            'strategy_version': record.strategy_version,
            'model_reference': record.model_reference,
            'ranking_position': getattr(record, 'ranking_position', 0),
            'confidence_score': getattr(record, 'confidence_score', 0.0),
            'status': record.status,
            'experiment_count': len(getattr(record, 'EXPERIMENT_HISTORY', [])),
            'tested_variants': getattr(record, 'tested_variants', []),
            'next_evaluation': getattr(record, 'next_evaluation', True),
        }
        
        # Tagi
        tags = ['strategy', 'memory']
        if record.status:
            tags.append(f'status:{record.status.lower()}')
        if record.model_reference:
            tags.append(f'model:{record.model_reference}')
        
        # Importance na podstawie confidence
        importance = getattr(record, 'confidence_score', 0.5)
        if importance == 0:
            importance = 0.5
        
        return CollectiveMemoryDocument(
            source_id=record.strategy_id or record.memory_id,
            source_type='strategy_memory',
            text=text,
            metadata=metadata,
            timestamp=getattr(record, 'last_updated', datetime.now()),
            importance=importance,
            tags=tags
        )
    
    def adapt_match_result(self, record: Any) -> CollectiveMemoryDocument:
        """
        Konwertuje MatchResult na CollectiveMemoryDocument.
        
        Format tekstu zawiera:
        - Druzyny i wynik meczu
        - Statystyki meczu
        - Informacje o kursach
        - Data i source
        """
        text_parts = []
        
        # Podstawowe informacje
        home_team = getattr(record, 'home_team', 'Unknown')
        away_team = getattr(record, 'away_team', 'Unknown')
        home_score = getattr(record, 'home_score', None)
        away_score = getattr(record, 'away_score', None)
        
        text_parts.append(f"MATCH: {home_team} vs {away_team}")
        
        if home_score is not None and away_score is not None:
            text_parts.append(f"Result: {home_score}-{away_score}")
            
            # Określ wynik
            if home_score > away_score:
                result = "HOME WIN"
            elif home_score < away_score:
                result = "AWAY WIN"
            else:
                result = "DRAW"
            text_parts.append(f"Outcome: {result}")
        
        # Data meczu
        match_date = getattr(record, 'match_date', None) or getattr(record, 'date', None)
        if match_date:
            text_parts.append(f"Date: {match_date}")
        
        # Statystyki
        stats = getattr(record, 'statistics', {})
        if stats:
            stats_str = json.dumps(stats, ensure_ascii=False, default=str)
            text_parts.append(f"Statistics: {stats_str}")
        
        # Kursy
        odds = getattr(record, 'odds', {})
        if odds:
            odds_str = json.dumps(odds, ensure_ascii=False, default=str)
            text_parts.append(f"Odds: {odds_str}")
        
        # Źródło
        source = getattr(record, 'source', None)
        if source:
            text_parts.append(f"Source: {source}")
        
        # Tekst dokumentu
        text = "\n".join(text_parts)
        
        # Metadane
        match_id = getattr(record, 'match_id', '') or getattr(record, 'id', '')
        metadata = {
            'match_id': match_id,
            'home_team': home_team,
            'away_team': away_team,
            'home_score': home_score,
            'away_score': away_score,
            'outcome': result if 'result' in locals() else None,
            'source': source,
        }
        if match_date:
            metadata['match_date'] = str(match_date)
        
        # Tagi
        tags = ['match', 'result', 'memory']
        if result:
            tags.append(f'outcome:{result.lower()}')
        
        # Importance - mecze z dużymi statystykami/odchyleniami są ważniejsze
        importance = 0.7  # Domyślnie wysoka waga dla wyników
        
        return CollectiveMemoryDocument(
            source_id=match_id,
            source_type='match_result',
            text=text,
            metadata=metadata,
            timestamp=getattr(record, 'timestamp', datetime.now()),
            importance=importance,
            tags=tags
        )
    
    def adapt_training_memory(self, record: Any) -> CollectiveMemoryDocument:
        """
        Konwertuje TrainingMemory na CollectiveMemoryDocument.
        """
        text_parts = []
        
        text_parts.append(f"TRAINING SESSION: {record.session_id}")
        text_parts.append(f"Phase: {record.phase.name if hasattr(record.phase, 'name') else record.phase}")
        text_parts.append(f"Method: {record.method}")
        text_parts.append(f"Model: {record.model_name} v{record.model_version}")
        
        if record.training_data_count:
            text_parts.append(f"Data Count: {record.training_data_count}")
        if record.training_data_source:
            text_parts.append(f"Data Source: {record.training_data_source}")
        
        # Metryki
        if record.final_metrics:
            metrics_str = json.dumps(record.final_metrics, ensure_ascii=False, default=str)
            text_parts.append(f"Final Metrics: {metrics_str}")
        
        if record.improvement:
            imp_str = json.dumps(record.improvement, ensure_ascii=False, default=str)
            text_parts.append(f"Improvement: {imp_str}")
        
        text = "\n".join(text_parts)
        
        metadata = {
            'session_id': record.session_id,
            'phase': record.phase.name if hasattr(record.phase, 'name') else str(record.phase),
            'method': record.method,
            'model_name': record.model_name,
            'model_version': record.model_version,
            'data_count': record.training_data_count,
            'metrics': record.final_metrics,
            'duration_seconds': record.duration_seconds,
        }
        
        tags = ['training', 'memory', 'learning']
        importance = min(record.training_data_count / 1000.0, 1.0) if record.training_data_count else 0.5
        
        return CollectiveMemoryDocument(
            source_id=record.session_id,
            source_type='training_memory',
            text=text,
            metadata=metadata,
            timestamp=datetime.fromisoformat(record.start_time) if isinstance(record.start_time, str) else getattr(record, 'start_time', datetime.now()),
            importance=importance,
            tags=tags
        )
    
    def adapt_observation_memory(self, record: Any) -> CollectiveMemoryDocument:
        """
        Konwertuje ObservationMemory na CollectiveMemoryDocument.
        """
        text_parts = []
        
        text_parts.append(f"OBSERVATION: {getattr(record, 'observation_id', 'Unknown')}")
        
        scope = getattr(record, 'scope', None)
        if scope:
            if hasattr(scope, 'name'):
                text_parts.append(f"Scope: {scope.name}")
            else:
                text_parts.append(f"Scope: {scope}")
        
        if hasattr(record, 'observation_data'):
            data_str = json.dumps(record.observation_data, ensure_ascii=False, default=str)
            text_parts.append(f"Data: {data_str}")
        
        if hasattr(record, 'metrics'):
            metrics_str = json.dumps(record.metrics, ensure_ascii=False, default=str)
            text_parts.append(f"Metrics: {metrics_str}")
        
        text = "\n".join(text_parts)
        
        metadata = {
            'observation_id': getattr(record, 'observation_id', ''),
            'scope': str(scope) if scope else '',
            'metrics': getattr(record, 'metrics', {}),
        }
        
        tags = ['observation', 'memory']
        importance = 0.6
        
        return CollectiveMemoryDocument(
            source_id=getattr(record, 'observation_id', ''),
            source_type='observation_memory',
            text=text,
            metadata=metadata,
            timestamp=getattr(record, 'timestamp', datetime.now()),
            importance=importance,
            tags=tags
        )
    
    def adapt_behavior_memory(self, record: Any) -> CollectiveMemoryDocument:
        """
        Konwertuje BehaviorMemory na CollectiveMemoryDocument.
        """
        text_parts = []
        
        behavior_id = getattr(record, 'behavior_id', 'Unknown')
        text_parts.append(f"BEHAVIOR: {behavior_id}")
        
        behavior_type = getattr(record, 'behavior_type', None)
        if behavior_type:
            if hasattr(behavior_type, 'name'):
                text_parts.append(f"Type: {behavior_type.name}")
            else:
                text_parts.append(f"Type: {behavior_type}")
        
        if hasattr(record, 'description'):
            text_parts.append(f"Description: {record.description}")
        
        if hasattr(record, 'pattern'):
            pattern_str = json.dumps(record.pattern, ensure_ascii=False, default=str)
            text_parts.append(f"Pattern: {pattern_str}")
        
        if hasattr(record, 'frequency'):
            text_parts.append(f"Frequency: {record.frequency}")
        
        text = "\n".join(text_parts)
        
        metadata = {
            'behavior_id': behavior_id,
            'behavior_type': str(behavior_type) if behavior_type else '',
            'frequency': getattr(record, 'frequency', 0),
        }
        
        tags = ['behavior', 'memory']
        importance = min(getattr(record, 'frequency', 0) / 100.0, 1.0) if hasattr(record, 'frequency') else 0.5
        
        return CollectiveMemoryDocument(
            source_id=behavior_id,
            source_type='behavior_memory',
            text=text,
            metadata=metadata,
            timestamp=getattr(record, 'timestamp', datetime.now()),
            importance=importance,
            tags=tags
        )
    
    def adapt_agent_analysis_memory(self, record: Any) -> CollectiveMemoryDocument:
        """
        Konwertuje AgentAnalysisMemory na CollectiveMemoryDocument.
        """
        text_parts = []
        
        analysis_id = getattr(record, 'analysis_id', 'Unknown')
        text_parts.append(f"AGENT ANALYSIS: {analysis_id}")
        
        analysis_type = getattr(record, 'analysis_type', None)
        if analysis_type:
            if hasattr(analysis_type, 'name'):
                text_parts.append(f"Type: {analysis_type.name}")
            else:
                text_parts.append(f"Type: {analysis_type}")
        
        if hasattr(record, 'agent_id'):
            text_parts.append(f"Agent: {record.agent_id}")
        
        if hasattr(record, 'analysis_data'):
            data_str = json.dumps(record.analysis_data, ensure_ascii=False, default=str)
            text_parts.append(f"Data: {data_str}")
        
        if hasattr(record, 'results'):
            results_str = json.dumps(record.results, ensure_ascii=False, default=str)
            text_parts.append(f"Results: {results_str}")
        
        text = "\n".join(text_parts)
        
        metadata = {
            'analysis_id': analysis_id,
            'analysis_type': str(analysis_type) if analysis_type else '',
            'agent_id': getattr(record, 'agent_id', ''),
        }
        
        tags = ['agent_analysis', 'memory', 'analysis']
        importance = 0.7
        
        return CollectiveMemoryDocument(
            source_id=analysis_id,
            source_type='agent_analysis_memory',
            text=text,
            metadata=metadata,
            timestamp=getattr(record, 'timestamp', datetime.now()),
            importance=importance,
            tags=tags
        )
    
    def adapt_decision_memory(self, record: Any) -> CollectiveMemoryDocument:
        """
        Konwertuje DecisionMemory na CollectiveMemoryDocument.
        """
        text_parts = []
        
        decision_id = getattr(record, 'decision_id', 'Unknown')
        text_parts.append(f"DECISION: {decision_id}")
        
        if hasattr(record, 'decision_outcome'):
            text_parts.append(f"Outcome: {record.decision_outcome}")
        
        if hasattr(record, 'decision_context'):
            context_str = json.dumps(record.decision_context, ensure_ascii=False, default=str)
            text_parts.append(f"Context: {context_str}")
        
        if hasattr(record, 'decision_action'):
            text_parts.append(f"Action: {record.decision_action}")
        
        if hasattr(record, 'confidence'):
            text_parts.append(f"Confidence: {record.confidence:.3f}")
        
        if hasattr(record, 'performance'):
            perf_str = json.dumps(record.performance, ensure_ascii=False, default=str)
            text_parts.append(f"Performance: {perf_str}")
        
        text = "\n".join(text_parts)
        
        metadata = {
            'decision_id': decision_id,
            'outcome': getattr(record, 'decision_outcome', ''),
            'action': getattr(record, 'decision_action', ''),
            'confidence': getattr(record, 'confidence', 0.0),
        }
        
        tags = ['decision', 'memory']
        importance = getattr(record, 'confidence', 0.5)
        
        return CollectiveMemoryDocument(
            source_id=decision_id,
            source_type='decision_memory',
            text=text,
            metadata=metadata,
            timestamp=getattr(record, 'timestamp', datetime.now()),
            importance=importance,
            tags=tags
        )
