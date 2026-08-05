"""
SSI V5 - Base Memory Adapter
ETAP: 5.4.2.1 - CollectiveMemoryDocument Pipeline

Bazowy kontrakt dla wszystkich adapterow pamieci.

Zasady:
1. Kazdy adapter dziedziczy po tej klasie
2. Kazdy adapter implementuje can_handle() i convert()
3. Adapter NIE modyfikuje oryginalnej pamieci
4. Adapter TYLKO konwertuje na CollectiveMemoryDocument
5. Adapter powinien byc idempotentny (ta sama wejsciowa pamiec -> ten sam dokument)

Autor: SSI V5 System / Mistral Vibe
Data: 2026-08-04
Wersja: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from SSI_V5.memory.collective_memory.memory_document import CollectiveMemoryDocument


class BaseMemoryAdapter(ABC):
    """
    Abstrakcyjna klasa bazowa dla adapterow pamieci.
    
    Kazdy adapter konwertuje specyficzny typ pamieci SSI V5
    na spójna strukturę CollectiveMemoryDocument.
    
    Attributes:
        source_type: Typ zrodlowej pamieci (np. 'strategy_memory', 'match_result')
        priority: Priorytet adaptera (do rozstrzygania kolizji)
    """
    
    # Typ zrodlowej pamieci - musi byc zdefiniowany w klasie dziedziczacej
    source_type: str = ""
    
    # Priorytet (do rozstrzygania kolizji przy wielu pasujacych adapterach)
    # Nizsza wartosc = wyzszy priorytet
    priority: int = 100
    
    @abstractmethod
    def can_handle(self, obj: Any) -> bool:
        """
        Sprawdza czy adapter moze obsluzyc dany obiekt.
        
        Args:
            obj: Obiekt do sprawdzenia
            
        Returns:
            True jesli adapter moze konwertowac ten typ obiektu
        """
        pass
    
    @abstractmethod
    def convert(self, obj: Any) -> CollectiveMemoryDocument:
        """
        Konwertuje obiekt pamieci na CollectiveMemoryDocument.
        
        Args:
            obj: Obiekt pamieci do konwersji
            
        Returns:
            CollectiveMemoryDocument - skonwertowany dokument
            
        Raises:
            ValueError: Jesli obiekt nie moze byc skonwertowany
        """
        pass
    
    def get_source_type(self) -> str:
        """Zwraca typ zrodlowej pamieci."""
        return self.source_type
    
    def get_priority(self) -> int:
        """Zwraca priorytet adaptera."""
        return self.priority
    
    def create_document(
        self,
        source_id: str,
        text: str,
        metadata: Optional[dict] = None,
        importance: float = 0.5,
        tags: Optional[list] = None
    ) -> CollectiveMemoryDocument:
        """
        Tworzy CollectiveMemoryDocument z podanych komponentow.
        
        Metoda pomocnicza dla adapterow.
        
        Args:
            source_id: ID zrodlowego rekordu
            text: Tekst dokumentu
            metadata: Metadane
            importance: Waga dokumentu (0.0-1.0)
            tags: Lista tagow
            
        Returns:
            CollectiveMemoryDocument
        """
        return CollectiveMemoryDocument(
            source_id=source_id,
            source_type=self.source_type,
            text=text,
            metadata=metadata or {},
            importance=importance,
            tags=tags or []
        )
