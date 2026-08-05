"""
SSI V5 - Strategy Memory Adapter
ETAP: 5.4.2.1 - CollectiveMemoryDocument Pipeline

Adapter konwertujacy StrategyMemoryRecord na CollectiveMemoryDocument.

Przykład konwersji:
    Wejście: StrategyMemoryRecord(strategy_id="str_001", result="WIN", confidence=0.78, profit=120)
    Wyjście: CollectiveMemoryDocument(
                source_type="strategy_memory",
                text="Strategy str_001 achieved WIN. Confidence 78%. Profit 120.",
                metadata={"strategy_id": "str_001", "result": "WIN", ...}
             )

Autor: SSI V5 System / Mistral Vibe
Data: 2026-08-04
Wersja: 1.0.0
"""

from typing import Any

from .base_memory_adapter import BaseMemoryAdapter
from SSI_V5.memory.collective_memory.memory_document import CollectiveMemoryDocument


class StrategyMemoryAdapter(BaseMemoryAdapter):
    """
    Adapter dla StrategyMemoryRecord.
    
    Konwertuje rekordy pamięci strategii na dokumety do indeksowania semantycznego.
    """
    
    source_type = "strategy_memory"
    priority = 10  # Wysoki priorytet - strategie sa kluczowe
    
    def can_handle(self, obj: Any) -> bool:
        """Sprawdza czy obiekt jest StrategyMemoryRecord."""
        # Sprawdź po nazwie klasy
        if type(obj).__name__ == 'StrategyMemoryRecord':
            return True
        
        # Sprawdź po charakterystycznych polach
        required_fields = ['memory_id', 'strategy_id', 'strategy_version']
        return all(hasattr(obj, field) for field in required_fields)
    
    def convert(self, record: Any) -> CollectiveMemoryDocument:
        """
        Konwertuje StrategyMemoryRecord na CollectiveMemoryDocument.
        
        Args:
            record: Rekord pamięci strategii
            
        Returns:
            CollectiveMemoryDocument gotowy do indeksowania
        """
        if not self.can_handle(record):
            raise ValueError(f"Cannot convert {type(record).__name__} to CollectiveMemoryDocument")
        
        # Buduj tekst dokumentu
        text_parts = []
        
        # Podstawowe informacje
        text_parts.append(f"Strategy {record.strategy_id} v{record.strategy_version}")
        
        # Definicja strategii
        if getattr(record, 'strategy_definition', None):
            strategy_type = record.strategy_definition.get('type', 'unknown')
            strategy_goal = record.strategy_definition.get('goal', '')
            if strategy_type != 'unknown':
                text_parts.append(f"Type: {strategy_type}")
            if strategy_goal:
                text_parts.append(f"Goal: {strategy_goal}")
        
        # Parametry strategii
        if getattr(record, 'strategy_parameters', None):
            text_parts.append("Parameters:")
            for key, value in record.strategy_parameters.items():
                text_parts.append(f"  {key}: {value}")
        
        # Historia eksperymentów
        if getattr(record, 'EXPERIMENT_HISTORY', None):
            successful_experiments = sum(
                1 for exp in record.EXPERIMENT_HISTORY 
                if exp.get('result') == 'SUCCESS'
            )
            total_experiments = len(record.EXPERIMENT_HISTORY)
            text_parts.append(f"Experiments: {successful_experiments}/{total_experiments} successful")
        
        # Metryki strategii (z ETAP 5.3.3)
        confidence = getattr(record, 'confidence_score', 0.0)
        if confidence > 0:
            text_parts.append(f"Confidence score: {confidence:.2%}")
        ranking = getattr(record, 'ranking_position', 0)
        if ranking > 0:
            text_parts.append(f"Ranking position: {ranking}")
        status = getattr(record, 'status', '')
        if status:
            text_parts.append(f"Status: {status}")
        
        # Buduj metadane
        creation_time = getattr(record, 'creation_time', None)
        last_updated = getattr(record, 'last_updated', None)
        
        metadata = {
            'strategy_id': record.strategy_id,
            'strategy_version': record.strategy_version,
            'memory_id': record.memory_id,
            'model_reference': getattr(record, 'model_reference', 'default'),
            'creation_time': creation_time.isoformat() if creation_time and hasattr(creation_time, 'isoformat') else str(creation_time) if creation_time else None,
            'last_updated': last_updated.isoformat() if last_updated and hasattr(last_updated, 'isoformat') else str(last_updated) if last_updated else None,
            'status': getattr(record, 'status', 'UNKNOWN'),
            'confidence_score': getattr(record, 'confidence_score', 0.0),
            'ranking_position': getattr(record, 'ranking_position', 0),
            'feature_schema': getattr(record, 'feature_schema', []),
            'tested_variants': getattr(record, 'tested_variants', []),
            'next_evaluation': getattr(record, 'next_evaluation', True),
        }
        
        # Dodaj informacje o eksperymentach
        exp_history = getattr(record, 'EXPERIMENT_HISTORY', None)
        if exp_history:
            metadata['experiment_count'] = len(exp_history)
            metadata['successful_experiments'] = successful_experiments
        
        # Dodaj definicję i parametry strategii
        if getattr(record, 'strategy_definition', None):
            metadata['strategy_definition'] = record.strategy_definition
        if getattr(record, 'strategy_parameters', None):
            metadata['strategy_parameters'] = record.strategy_parameters
        
        # Oblicz ważność dokumentu
        importance = self._calculate_importance(record)
        
        # Tagi
        tags = self._generate_tags(record)
        
        return self.create_document(
            source_id=record.memory_id,
            text="\n".join(text_parts),
            metadata=metadata,
            importance=importance,
            tags=tags
        )
    
    def _calculate_importance(self, record: Any) -> float:
        """Oblicza ważność dokumentu na podstawie metryk strategii."""
        importance = 0.5  # Domyślna wartość
        
        # Wyższa ważność dla aktywnych strategii
        status = getattr(record, 'status', '')
        if status == "ACTIVE":
            importance += 0.2
        
        # Wyższa ważność dla strategii z wysokim confidence
        confidence = getattr(record, 'confidence_score', 0.0)
        if confidence > 0.8:
            importance += 0.2
        elif confidence > 0.6:
            importance += 0.1
        
        # Wyższa ważność dla strategii z wysoką pozycją w rankingu
        ranking = getattr(record, 'ranking_position', 0)
        if ranking > 0 and ranking <= 10:
            importance += 0.1
        elif ranking > 10 and ranking <= 50:
            importance += 0.05
        
        # Ogranicz do zakresu 0.0-1.0
        return min(1.0, max(0.0, importance))
    
    def _generate_tags(self, record: Any) -> list:
        """Generuje tagi dla dokumentu."""
        tags = [f"strategy:{record.strategy_id}", f"version:{record.strategy_version}"]
        
        # Tag statusu
        status = getattr(record, 'status', '')
        if status:
            tags.append(f"status:{status.lower()}")
        
        # Tag modelu
        model_ref = getattr(record, 'model_reference', '')
        if model_ref:
            tags.append(f"model:{model_ref}")
        
        # Tag po typie strategii
        strategy_def = getattr(record, 'strategy_definition', None)
        if strategy_def:
            strategy_type = strategy_def.get('type', '')
            if strategy_type:
                tags.append(f"type:{strategy_type.lower()}")
        
        # Tag confidence
        confidence = getattr(record, 'confidence_score', 0.0)
        if confidence > 0.8:
            tags.append("confidence:high")
        elif confidence > 0.5:
            tags.append("confidence:medium")
        else:
            tags.append("confidence:low")
        
        return tags
