"""
SSI V5 - Behavior Memory Adapter
ETAP: 5.4.2.1 - CollectiveMemoryDocument Pipeline

Adapter konwertujacy BehaviorMemory na CollectiveMemoryDocument.

Autor: SSI V5 System / Mistral Vibe
Data: 2026-08-04
Wersja: 1.0.0
"""

from typing import Any

from .base_memory_adapter import BaseMemoryAdapter
from SSI_V5.memory.collective_memory.memory_document import CollectiveMemoryDocument


class BehaviorMemoryAdapter(BaseMemoryAdapter):
    """
    Adapter dla BehaviorMemory.
    
    Konwertuje pamięć zachowań na dokument do indeksowania semantycznego.
    """
    
    source_type = "behavior_memory"
    priority = 50
    
    def can_handle(self, obj: Any) -> bool:
        """Sprawdza czy obiekt jest BehaviorMemory."""
        # Sprawdź po nazwie klasy
        if type(obj).__name__ == 'BehaviorMemory':
            return True
        
        # Sprawdź po charakterystycznych polach
        required_fields = ['behavior_id', 'behavior_type']
        return all(hasattr(obj, field) for field in required_fields)
    
    def convert(self, memory: Any) -> CollectiveMemoryDocument:
        """
        Konwertuje BehaviorMemory na CollectiveMemoryDocument.
        
        Args:
            memory: Pamięć zachowań
            
        Returns:
            CollectiveMemoryDocument gotowy do indeksowania
        """
        if not self.can_handle(memory):
            raise ValueError(f"Cannot convert {type(memory).__name__} to CollectiveMemoryDocument")
        
        # Buduj tekst dokumentu
        text_parts = []
        
        # Podstawowe informacje
        text_parts.append(f"Behavior: {memory.behavior_id}")
        
        # Typ zachowania
        if hasattr(memory, 'behavior_type'):
            behavior_type_name = getattr(memory.behavior_type, 'name', str(memory.behavior_type))
            text_parts.append(f"Type: {behavior_type_name}")
        
        # Opis zachowania
        if hasattr(memory, 'description') and memory.description:
            text_parts.append(f"Description: {memory.description}")
        
        # Akcje wykonane
        if hasattr(memory, 'actions') and memory.actions:
            text_parts.append("Actions:")
            for i, action in enumerate(memory.actions, 1):
                text_parts.append(f"  {i}. {action}")
        
        # Wynik zachowania
        if hasattr(memory, 'outcome') and memory.outcome:
            text_parts.append(f"Outcome: {memory.outcome}")
        
        # Metryki zachowania
        if hasattr(memory, 'metrics') and memory.metrics:
            text_parts.append("Metrics:")
            for key, value in memory.metrics.items():
                text_parts.append(f"  {key}: {value}")
        
        # Buduj metadane
        metadata = {
            'behavior_id': memory.behavior_id,
            'behavior_type': str(getattr(memory.behavior_type, 'name', memory.behavior_type)) if hasattr(memory, 'behavior_type') else '',
            'description': getattr(memory, 'description', ''),
            'actions': getattr(memory, 'actions', []),
            'outcome': getattr(memory, 'outcome', ''),
            'metrics': getattr(memory, 'metrics', {}),
            'created_at': getattr(memory, 'created_at', None),
            'updated_at': getattr(memory, 'updated_at', None),
        }
        
        # Oblicz ważność dokumentu
        importance = self._calculate_importance(memory)
        
        # Tagi
        tags = self._generate_tags(memory)
        
        return self.create_document(
            source_id=memory.behavior_id,
            text="\n".join(text_parts),
            metadata=metadata,
            importance=importance,
            tags=tags
        )
    
    def _calculate_importance(self, memory: Any) -> float:
        """Oblicza ważność dokumentu na podstawie zachowania."""
        importance = 0.5  # Domyślna wartość
        
        # Wyższa ważność dla zachowań decyzyjnych i strategicznych
        if hasattr(memory, 'behavior_type'):
            behavior_type_name = str(getattr(memory.behavior_type, 'name', memory.behavior_type))
            if 'DECISION' in behavior_type_name:
                importance += 0.2
            elif 'STRATEGY' in behavior_type_name:
                importance += 0.15
            elif 'ANALYSIS' in behavior_type_name:
                importance += 0.1
        
        # Wyższa ważność dla zachowań z pozytywnym wynikiem
        if hasattr(memory, 'outcome') and memory.outcome:
            if 'SUCCESS' in memory.outcome or 'POSITIVE' in memory.outcome:
                importance += 0.15
            elif 'PARTIAL' in memory.outcome:
                importance += 0.05
        
        # Wyższa ważność dla złożonych zachowań (wiele akcji)
        if hasattr(memory, 'actions') and memory.actions:
            if len(memory.actions) > 5:
                importance += 0.1
            elif len(memory.actions) > 2:
                importance += 0.05
        
        # Ogranicz do zakresu 0.0-1.0
        return min(1.0, max(0.0, importance))
    
    def _generate_tags(self, memory: Any) -> list:
        """Generuje tagi dla dokumentu."""
        tags = [f"behavior:{memory.behavior_id}"]
        
        # Tag typu zachowania
        if hasattr(memory, 'behavior_type'):
            behavior_type_name = str(getattr(memory.behavior_type, 'name', memory.behavior_type))
            tags.append(f"type:{behavior_type_name.lower()}")
        
        # Tag wyniku
        if hasattr(memory, 'outcome') and memory.outcome:
            outcome_lower = memory.outcome.lower()
            if 'success' in outcome_lower or 'positive' in outcome_lower:
                tags.append("outcome:success")
            elif 'partial' in outcome_lower:
                tags.append("outcome:partial")
            elif 'failure' in outcome_lower or 'negative' in outcome_lower:
                tags.append("outcome:failure")
            else:
                tags.append(f"outcome:{outcome_lower}")
        
        # Tag złożoności
        if hasattr(memory, 'actions') and memory.actions:
            action_count = len(memory.actions)
            if action_count > 5:
                tags.append("complexity:high")
            elif action_count > 2:
                tags.append("complexity:medium")
            else:
                tags.append("complexity:low")
        
        return tags
