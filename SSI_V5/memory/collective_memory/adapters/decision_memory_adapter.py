"""
SSI V5 - Decision Memory Adapter
ETAP: 5.4.2.1 - CollectiveMemoryDocument Pipeline

Adapter konwertujacy DecisionMemory na CollectiveMemoryDocument.

Autor: SSI V5 System / Mistral Vibe
Data: 2026-08-04
Wersja: 1.0.0
"""

from typing import Any

from .base_memory_adapter import BaseMemoryAdapter
from SSI_V5.memory.collective_memory.memory_document import CollectiveMemoryDocument


class DecisionMemoryAdapter(BaseMemoryAdapter):
    """
    Adapter dla DecisionMemory.
    
    Konwertuje pamięć decyzji na dokument do indeksowania semantycznego.
    """
    
    source_type = "decision_memory"
    priority = 70
    
    def can_handle(self, obj: Any) -> bool:
        """Sprawdza czy obiekt jest DecisionMemory."""
        # Sprawdź po nazwie klasy
        if type(obj).__name__ == 'DecisionMemory':
            return True
        
        # Sprawdź po charakterystycznych polach
        required_fields = ['decision_id', 'decision_outcome']
        return all(hasattr(obj, field) for field in required_fields)
    
    def convert(self, memory: Any) -> CollectiveMemoryDocument:
        """
        Konwertuje DecisionMemory na CollectiveMemoryDocument.
        
        Args:
            memory: Pamięć decyzji
            
        Returns:
            CollectiveMemoryDocument gotowy do indeksowania
        """
        if not self.can_handle(memory):
            raise ValueError(f"Cannot convert {type(memory).__name__} to CollectiveMemoryDocument")
        
        # Buduj tekst dokumentu
        text_parts = []
        
        # Podstawowe informacje
        text_parts.append(f"Decision: {memory.decision_id}")
        
        # Typ decyzji
        if hasattr(memory, 'decision_type') and memory.decision_type:
            text_parts.append(f"Decision Type: {memory.decision_type}")
        
        # Kontekst decyzji
        if hasattr(memory, 'context') and memory.context:
            text_parts.append("Context:")
            for key, value in memory.context.items():
                text_parts.append(f"  {key}: {value}")
        
        # Opcje rozważane
        if hasattr(memory, 'options') and memory.options:
            text_parts.append("Options considered:")
            for i, option in enumerate(memory.options, 1):
                text_parts.append(f"  {i}. {option}")
        
        # Wybrana opcja
        if hasattr(memory, 'selected_option') and memory.selected_option:
            text_parts.append(f"Selected: {memory.selected_option}")
        
        # Wynik decyzji
        if hasattr(memory, 'decision_outcome') and memory.decision_outcome:
            text_parts.append(f"Outcome: {memory.decision_outcome}")
        
        # Uzasadnienie
        if hasattr(memory, 'rationale') and memory.rationale:
            text_parts.append(f"Rationale: {memory.rationale}")
        
        # Metryki decyzji
        if hasattr(memory, 'metrics') and memory.metrics:
            text_parts.append("Metrics:")
            for key, value in memory.metrics.items():
                text_parts.append(f"  {key}: {value}")
        
        # Buduj metadane
        metadata = {
            'decision_id': memory.decision_id,
            'decision_type': getattr(memory, 'decision_type', ''),
            'context': getattr(memory, 'context', {}),
            'options': getattr(memory, 'options', []),
            'selected_option': getattr(memory, 'selected_option', ''),
            'decision_outcome': getattr(memory, 'decision_outcome', ''),
            'rationale': getattr(memory, 'rationale', ''),
            'metrics': getattr(memory, 'metrics', {}),
            'created_at': getattr(memory, 'created_at', None),
            'updated_at': getattr(memory, 'updated_at', None),
        }
        
        # Oblicz ważność dokumentu
        importance = self._calculate_importance(memory)
        
        # Tagi
        tags = self._generate_tags(memory)
        
        return self.create_document(
            source_id=memory.decision_id,
            text="\n".join(text_parts),
            metadata=metadata,
            importance=importance,
            tags=tags
        )
    
    def _calculate_importance(self, memory: Any) -> float:
        """Oblicza ważność dokumentu na podstawie decyzji."""
        importance = 0.5  # Domyślna wartość
        
        # Wyższa ważność dla celebry decyzji (wiele opcji)
        if hasattr(memory, 'options') and memory.options:
            if len(memory.options) > 5:
                importance += 0.2
            elif len(memory.options) > 2:
                importance += 0.1
        
        # Wyższa ważność dla pozytywnych wyników
        if hasattr(memory, 'decision_outcome') and memory.decision_outcome:
            outcome_lower = memory.decision_outcome.lower()
            if 'SUCCESS' in outcome_lower or 'OPTIMAL' in outcome_lower:
                importance += 0.25
            elif 'GOOD' in outcome_lower:
                importance += 0.15
            elif 'ACCEPTABLE' in outcome_lower:
                importance += 0.05
        
        # Wyższa ważność dla decyzji z uzasadnieniem
        if hasattr(memory, 'rationale') and memory.rationale:
            # Im dłuższe uzasadnienie, tym ważniejsza decyzja
            if len(memory.rationale) > 200:
                importance += 0.1
            elif len(memory.rationale) > 100:
                importance += 0.05
        
        # Ogranicz do zakresu 0.0-1.0
        return min(1.0, max(0.0, importance))
    
    def _generate_tags(self, memory: Any) -> list:
        """Generuje tagi dla dokumentu."""
        tags = [f"decision:{memory.decision_id}"]
        
        # Tag typu decyzji
        if hasattr(memory, 'decision_type') and memory.decision_type:
            tags.append(f"type:{memory.decision_type.lower()}")
        
        # Tag wyniku
        if hasattr(memory, 'decision_outcome') and memory.decision_outcome:
            outcome_lower = memory.decision_outcome.lower()
            if 'success' in outcome_lower or 'optimal' in outcome_lower:
                tags.append("outcome:success")
            elif 'good' in outcome_lower:
                tags.append("outcome:good")
            elif 'acceptable' in outcome_lower:
                tags.append("outcome:acceptable")
            elif 'failure' in outcome_lower or 'poor' in outcome_lower:
                tags.append("outcome:failure")
            else:
                tags.append(f"outcome:{outcome_lower}")
        
        # Tag złożoności (liczba opcji)
        option_count = len(getattr(memory, 'options', []))
        if option_count > 5:
            tags.append("complexity:high")
        elif option_count > 2:
            tags.append("complexity:medium")
        else:
            tags.append("complexity:low")
        
        return tags
