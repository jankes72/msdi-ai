"""
SSI V5 - Observation Memory Adapter
ETAP: 5.4.2.1 - CollectiveMemoryDocument Pipeline

Adapter konwertujacy ObservationMemory na CollectiveMemoryDocument.

Autor: SSI V5 System / Mistral Vibe
Data: 2026-08-04
Wersja: 1.0.0
"""

from typing import Any

from .base_memory_adapter import BaseMemoryAdapter
from SSI_V5.memory.collective_memory.memory_document import CollectiveMemoryDocument


class ObservationMemoryAdapter(BaseMemoryAdapter):
    """
    Adapter dla ObservationMemory.
    
    Konwertuje pamięć obserwacji na dokument do indeksowania semantycznego.
    """
    
    source_type = "observation_memory"
    priority = 40
    
    def can_handle(self, obj: Any) -> bool:
        """Sprawdza czy obiekt jest ObservationMemory."""
        # Sprawdź po nazwie klasy
        if type(obj).__name__ == 'ObservationMemory':
            return True
        
        # Sprawdź po charakterystycznych polach
        required_fields = ['observation_id', 'scope']
        return all(hasattr(obj, field) for field in required_fields)
    
    def convert(self, memory: Any) -> CollectiveMemoryDocument:
        """
        Konwertuje ObservationMemory na CollectiveMemoryDocument.
        
        Args:
            memory: Pamięć obserwacji
            
        Returns:
            CollectiveMemoryDocument gotowy do indeksowania
        """
        if not self.can_handle(memory):
            raise ValueError(f"Cannot convert {type(memory).__name__} to CollectiveMemoryDocument")
        
        # Buduj tekst dokumentu
        text_parts = []
        
        # Podstawowe informacje
        text_parts.append(f"Observation: {memory.observation_id}")
        
        # Zakres obserwacji
        if hasattr(memory, 'scope'):
            scope_name = getattr(memory.scope, 'name', str(memory.scope))
            text_parts.append(f"Scope: {scope_name}")
        
        # Opis obserwacji
        if hasattr(memory, 'description') and memory.description:
            text_parts.append(f"Description: {memory.description}")
        
        # Dane obserwacji
        if hasattr(memory, 'observation_data') and memory.observation_data:
            text_parts.append("Observation Data:")
            for key, value in memory.observation_data.items():
                text_parts.append(f"  {key}: {value}")
        
        # Metryki
        if hasattr(memory, 'metrics') and memory.metrics:
            text_parts.append("Metrics:")
            for key, value in memory.metrics.items():
                text_parts.append(f"  {key}: {value}")
        
        # Buduj metadane
        metadata = {
            'observation_id': memory.observation_id,
            'scope': str(getattr(memory.scope, 'name', memory.scope)) if hasattr(memory, 'scope') else '',
            'description': getattr(memory, 'description', ''),
            'observation_data': getattr(memory, 'observation_data', {}),
            'metrics': getattr(memory, 'metrics', {}),
            'created_at': getattr(memory, 'created_at', None),
            'updated_at': getattr(memory, 'updated_at', None),
        }
        
        # Oblicz ważność dokumentu
        importance = self._calculate_importance(memory)
        
        # Tagi
        tags = self._generate_tags(memory)
        
        return self.create_document(
            source_id=memory.observation_id,
            text="\n".join(text_parts),
            metadata=metadata,
            importance=importance,
            tags=tags
        )
    
    def _calculate_importance(self, memory: Any) -> float:
        """Oblicza ważność dokumentu na podstawie obserwacji."""
        importance = 0.5  # Domyślna wartość
        
        # Wyższa ważność dla obserwacji systemowych (szerszy kontekst)
        if hasattr(memory, 'scope'):
            scope_name = str(getattr(memory.scope, 'name', memory.scope))
            if 'SYSTEM' in scope_name:
                importance += 0.2
            elif 'GROUP' in scope_name:
                importance += 0.1
        
        # Wyższa ważność dla bogatszych obserwacji
        if hasattr(memory, 'observation_data') and memory.observation_data:
            if len(memory.observation_data) > 10:
                importance += 0.15
            elif len(memory.observation_data) > 5:
                importance += 0.1
        
        # Ogranicz do zakresu 0.0-1.0
        return min(1.0, max(0.0, importance))
    
    def _generate_tags(self, memory: Any) -> list:
        """Generuje tagi dla dokumentu."""
        tags = [f"observation:{memory.observation_id}"]
        
        # Tag zakresu
        if hasattr(memory, 'scope'):
            scope_name = str(getattr(memory.scope, 'name', memory.scope))
            tags.append(f"scope:{scope_name.lower()}")
        
        # Tag bogactwa danych
        if hasattr(memory, 'observation_data') and memory.observation_data:
            data_count = len(memory.observation_data)
            if data_count > 10:
                tags.append("data:rich")
            elif data_count > 5:
                tags.append("data:medium")
            else:
                tags.append("data:sparse")
        
        return tags
