"""
SSI V5 - Agent Analysis Memory Adapter
ETAP: 5.4.2.1 - CollectiveMemoryDocument Pipeline

Adapter konwertujacy AgentAnalysisMemory na CollectiveMemoryDocument.

Autor: SSI V5 System / Mistral Vibe
Data: 2026-08-04
Wersja: 1.0.0
"""

from typing import Any

from .base_memory_adapter import BaseMemoryAdapter
from SSI_V5.memory.collective_memory.memory_document import CollectiveMemoryDocument


class AgentAnalysisMemoryAdapter(BaseMemoryAdapter):
    """
    Adapter dla AgentAnalysisMemory.
    
    Konwertuje pamięć analiz agentów na dokument do indeksowania semantycznego.
    """
    
    source_type = "agent_analysis_memory"
    priority = 60
    
    def can_handle(self, obj: Any) -> bool:
        """Sprawdza czy obiekt jest AgentAnalysisMemory."""
        # Sprawdź po nazwie klasy
        if type(obj).__name__ == 'AgentAnalysisMemory':
            return True
        
        # Sprawdź po charakterystycznych polach
        required_fields = ['analysis_id', 'analysis_type']
        return all(hasattr(obj, field) for field in required_fields)
    
    def convert(self, memory: Any) -> CollectiveMemoryDocument:
        """
        Konwertuje AgentAnalysisMemory na CollectiveMemoryDocument.
        
        Args:
            memory: Pamięć analiz agentów
            
        Returns:
            CollectiveMemoryDocument gotowy do indeksowania
        """
        if not self.can_handle(memory):
            raise ValueError(f"Cannot convert {type(memory).__name__} to CollectiveMemoryDocument")
        
        # Buduj tekst dokumentu
        text_parts = []
        
        # Podstawowe informacje
        text_parts.append(f"Agent Analysis: {memory.analysis_id}")
        
        # Typ analizy
        if hasattr(memory, 'analysis_type'):
            analysis_type_name = getattr(memory.analysis_type, 'name', str(memory.analysis_type))
            text_parts.append(f"Analysis Type: {analysis_type_name}")
        
        # Agent/cel analizy
        if hasattr(memory, 'agent_id') and memory.agent_id:
            text_parts.append(f"Agent: {memory.agent_id}")
        if hasattr(memory, 'target_id') and memory.target_id:
            text_parts.append(f"Target: {memory.target_id}")
        
        # Wyniki analizy
        if hasattr(memory, 'findings') and memory.findings:
            text_parts.append("Findings:")
            for i, finding in enumerate(memory.findings, 1):
                text_parts.append(f"  {i}. {finding}")
        
        # Metryki
        if hasattr(memory, 'metrics') and memory.metrics:
            text_parts.append("Metrics:")
            for key, value in memory.metrics.items():
                text_parts.append(f"  {key}: {value}")
        
        # Rekomendacje
        if hasattr(memory, 'recommendations') and memory.recommendations:
            text_parts.append("Recommendations:")
            for i, recommendation in enumerate(memory.recommendations, 1):
                text_parts.append(f"  {i}. {recommendation}")
        
        # Buduj metadane
        metadata = {
            'analysis_id': memory.analysis_id,
            'analysis_type': str(getattr(memory.analysis_type, 'name', memory.analysis_type)) if hasattr(memory, 'analysis_type') else '',
            'agent_id': getattr(memory, 'agent_id', ''),
            'target_id': getattr(memory, 'target_id', ''),
            'findings': getattr(memory, 'findings', []),
            'metrics': getattr(memory, 'metrics', {}),
            'recommendations': getattr(memory, 'recommendations', []),
            'created_at': getattr(memory, 'created_at', None),
            'updated_at': getattr(memory, 'updated_at', None),
        }
        
        # Oblicz ważność dokumentu
        importance = self._calculate_importance(memory)
        
        # Tagi
        tags = self._generate_tags(memory)
        
        return self.create_document(
            source_id=memory.analysis_id,
            text="\n".join(text_parts),
            metadata=metadata,
            importance=importance,
            tags=tags
        )
    
    def _calculate_importance(self, memory: Any) -> float:
        """Oblicza ważność dokumentu na podstawie analizy."""
        importance = 0.5  # Domyślna wartość
        
        # Wyższa ważność dla analiz strategicznych i ewolucyjnych
        if hasattr(memory, 'analysis_type'):
            analysis_type_name = str(getattr(memory.analysis_type, 'name', memory.analysis_type))
            if 'EVOLUTION' in analysis_type_name:
                importance += 0.25
            elif 'STRATEGY' in analysis_type_name:
                importance += 0.2
            elif 'PERFORMANCE' in analysis_type_name:
                importance += 0.15
            elif 'COLLABORATION' in analysis_type_name:
                importance += 0.1
        
        # Wyższa ważność dla analiz z wieloma znaleziskami
        if hasattr(memory, 'findings') and memory.findings:
            if len(memory.findings) > 5:
                importance += 0.15
            elif len(memory.findings) > 2:
                importance += 0.1
        
        # Wyższa ważność dla analiz z rekomendacjami
        if hasattr(memory, 'recommendations') and memory.recommendations:
            if len(memory.recommendations) > 3:
                importance += 0.1
            else:
                importance += 0.05
        
        # Ogranicz do zakresu 0.0-1.0
        return min(1.0, max(0.0, importance))
    
    def _generate_tags(self, memory: Any) -> list:
        """Generuje tagi dla dokumentu."""
        tags = [f"analysis:{memory.analysis_id}"]
        
        # Tag typu analizy
        if hasattr(memory, 'analysis_type'):
            analysis_type_name = str(getattr(memory.analysis_type, 'name', memory.analysis_type))
            tags.append(f"type:{analysis_type_name.lower()}")
        
        # Tag agenta
        if hasattr(memory, 'agent_id') and memory.agent_id:
            tags.append(f"agent:{memory.agent_id}")
        
        # Tag celu
        if hasattr(memory, 'target_id') and memory.target_id:
            tags.append(f"target:{memory.target_id}")
        
        # Tag bogactwa analizy
        finding_count = len(getattr(memory, 'findings', []))
        recommendation_count = len(getattr(memory, 'recommendations', []))
        
        if finding_count + recommendation_count > 5:
            tags.append("insight:rich")
        elif finding_count + recommendation_count > 2:
            tags.append("insight:medium")
        else:
            tags.append("insight:basic")
        
        return tags
