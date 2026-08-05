"""
SSI V5 - Training Memory Adapter
ETAP: 5.4.2.1 - CollectiveMemoryDocument Pipeline

Adapter konwertujacy TrainingMemory na CollectiveMemoryDocument.

Autor: SSI V5 System / Mistral Vibe
Data: 2026-08-04
Wersja: 1.0.0
"""

from typing import Any

from .base_memory_adapter import BaseMemoryAdapter
from SSI_V5.memory.collective_memory.memory_document import CollectiveMemoryDocument


class TrainingMemoryAdapter(BaseMemoryAdapter):
    """
    Adapter dla TrainingMemory.
    
    Konwertuje pamięć tresowania na dokument do indeksowania semantycznego.
    """
    
    source_type = "training_memory"
    priority = 30
    
    def can_handle(self, obj: Any) -> bool:
        """Sprawdza czy obiekt jest TrainingMemory."""
        # Sprawdź po nazwie klasy
        if type(obj).__name__ == 'TrainingMemory':
            return True
        
        # Sprawdź po charakterystycznych polach
        required_fields = ['session_id', 'start_time', 'training_data_count']
        return all(hasattr(obj, field) for field in required_fields)
    
    def convert(self, memory: Any) -> CollectiveMemoryDocument:
        """
        Konwertuje TrainingMemory na CollectiveMemoryDocument.
        
        Args:
            memory: Pamięć tresowania
            
        Returns:
            CollectiveMemoryDocument gotowy do indeksowania
        """
        if not self.can_handle(memory):
            raise ValueError(f"Cannot convert {type(memory).__name__} to CollectiveMemoryDocument")
        
        # Buduj tekst dokumentu
        text_parts = []
        
        # Podstawowe informacje
        text_parts.append(f"Training Session: {memory.session_id}")
        
        # Czas trwania
        if hasattr(memory, 'duration_seconds') and memory.duration_seconds > 0:
            hours = int(memory.duration_seconds // 3600)
            minutes = int((memory.duration_seconds % 3600) // 60)
            text_parts.append(f"Duration: {hours}h {minutes}m")
        
        # Faza tresowania
        if hasattr(memory, 'phase'):
            text_parts.append(f"Phase: {memory.phase.name}")
        
        # Metoda tresowania
        if hasattr(memory, 'method'):
            text_parts.append(f"Method: {memory.method}")
        
        # Dane tresowaniowe
        text_parts.append(f"Training data: {memory.training_data_count} samples")
        if hasattr(memory, 'training_data_source') and memory.training_data_source:
            text_parts.append(f"Data source: {memory.training_data_source}")
        
        # Model
        if hasattr(memory, 'model_name'):
            text_parts.append(f"Model: {memory.model_name} v{memory.model_version}")
        
        # Metryki
        if hasattr(memory, 'success_rate') and memory.success_rate > 0:
            text_parts.append(f"Success rate: {memory.success_rate:.2%}")
        if hasattr(memory, 'validation_score') and memory.validation_score > 0:
            text_parts.append(f"Validation score: {memory.validation_score:.4f}")
        
        # Buduj metadane
        metadata = {
            'session_id': memory.session_id,
            'start_time': str(memory.start_time),
            'end_time': str(memory.end_time) if memory.end_time else None,
            'duration_seconds': memory.duration_seconds,
            'training_data_count': memory.training_data_count,
            'training_data_source': getattr(memory, 'training_data_source', ''),
            'method': getattr(memory, 'method', ''),
            'model_name': getattr(memory, 'model_name', ''),
            'model_version': getattr(memory, 'model_version', ''),
            'success_rate': getattr(memory, 'success_rate', 0.0),
            'validation_score': getattr(memory, 'validation_score', 0.0),
            'convergence_rate': getattr(memory, 'convergence_rate', 0.0),
        }
        
        # Dodaj metryki jeśli istnieją
        if hasattr(memory, 'initial_metrics') and memory.initial_metrics:
            metadata['initial_metrics'] = memory.initial_metrics
        if hasattr(memory, 'final_metrics') and memory.final_metrics:
            metadata['final_metrics'] = memory.final_metrics
        if hasattr(memory, 'improvement') and memory.improvement:
            metadata['improvement'] = memory.improvement
        
        # Dodaj kontekst
        if hasattr(memory, 'context') and memory.context:
            metadata['context'] = memory.context
        
        # Oblicz ważność dokumentu
        importance = self._calculate_importance(memory)
        
        # Tagi
        tags = self._generate_tags(memory)
        
        return self.create_document(
            source_id=memory.session_id,
            text="\n".join(text_parts),
            metadata=metadata,
            importance=importance,
            tags=tags
        )
    
    def _calculate_importance(self, memory: Any) -> float:
        """Oblicza ważność dokumentu na podstawie metryk tresowania."""
        importance = 0.5  # Domyślna wartość
        
        # Wyższa ważność dla wysokich wyników
        if hasattr(memory, 'validation_score'):
            if memory.validation_score > 0.9:
                importance += 0.3
            elif memory.validation_score > 0.8:
                importance += 0.2
            elif memory.validation_score > 0.7:
                importance += 0.1
        
        # Wyższa ważność dla wysokiej skuteczności
        if hasattr(memory, 'success_rate'):
            if memory.success_rate > 0.9:
                importance += 0.2
            elif memory.success_rate > 0.8:
                importance += 0.1
        
        # Ogranicz do zakresu 0.0-1.0
        return min(1.0, max(0.0, importance))
    
    def _generate_tags(self, memory: Any) -> list:
        """Generuje tagi dla dokumentu."""
        tags = [f"session:{memory.session_id}"]
        
        # Tag fazy tresowania
        if hasattr(memory, 'phase'):
            tags.append(f"phase:{memory.phase.name.lower()}")
        
        # Tag modelu
        if hasattr(memory, 'model_name') and memory.model_name:
            tags.append(f"model:{memory.model_name.lower()}")
        
        # Tag jakości tresowania
        if hasattr(memory, 'validation_score'):
            if memory.validation_score > 0.9:
                tags.append("quality:excellent")
            elif memory.validation_score > 0.8:
                tags.append("quality:good")
            elif memory.validation_score > 0.7:
                tags.append("quality:fair")
            else:
                tags.append("quality:low")
        
        return tags
