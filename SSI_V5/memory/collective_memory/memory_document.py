"""
SSI V5 - Collective Memory Document
ETAP: 5.4.2.1 - CollectiveMemoryDocument Pipeline

Unifikowana struktura dokumentu pamięci dla systemu Collective Memory.

Ten plik zawiera TYLKO klasę CollectiveMemoryDocument.
Jest importowany przez adaptery i memory_document_adapter_v2.

Autor: SSI V5 System / Mistral Vibe
Data: 2026-08-04
Wersja: 1.0.0
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List
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
        source_id: ID źródłowego rekordu pмяci (np. strategy_id, match_id)
        source_type: Typ źródłowej pмяci (strategy_memory, match_result, etc.)
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
    
    # Treść dokumentu
    text: str = ""
    
    # Metadane
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Czas
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Waga i klasyfikacja
    importance: float = 0.5  # 0.0 - 1.0, domyślnie 0.5
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
