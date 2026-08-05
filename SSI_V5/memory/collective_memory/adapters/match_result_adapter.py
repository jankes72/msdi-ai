"""
SSI V5 - Match Result Adapter
ETAP: 5.4.2.1 - CollectiveMemoryDocument Pipeline

Adapter konwertujacy MatchResult na CollectiveMemoryDocument.

Przykład konwersji:
    Wejście: MatchResult(match_id="m123", home_team="Liverpool", away_team="Arsenal", home_goals=2, away_goals=1)
    Wyjście: CollectiveMemoryDocument(
                source_type="match_result",
                text="Liverpool 2-1 Arsenal. Liverpool won at home.",
                metadata={"match_id": "m123", "home_team": "Liverpool", ...}
             )

Autor: SSI V5 System / Mistral Vibe
Data: 2026-08-04
Wersja: 1.0.0
"""

from typing import Any
from datetime import datetime

from .base_memory_adapter import BaseMemoryAdapter
from SSI_V5.memory.collective_memory.memory_document import CollectiveMemoryDocument


class MatchResultAdapter(BaseMemoryAdapter):
    """
    Adapter dla MatchResult.
    
    Konwertuje wyniki meczów na dokumety do indeksowania semantycznego.
    To stanowią WorldMemory - wiedzę o świecie ( historycznych meczach).
    """
    
    source_type = "match_result"
    priority = 20  # Wysoki priorytet - wyniki meczów są fundamentalne
    
    def can_handle(self, obj: Any) -> bool:
        """Sprawdza czy obiekt jest MatchResult."""
        # Sprawdź po nazwie klasy
        if type(obj).__name__ == 'MatchResult':
            return True
        
        # Sprawdź po charakterystycznych polach
        required_fields = ['match_id', 'home_team', 'away_team', 'home_goals', 'away_goals']
        return all(hasattr(obj, field) for field in required_fields)
    
    def convert(self, result: Any) -> CollectiveMemoryDocument:
        """
        Konwertuje MatchResult na CollectiveMemoryDocument.
        
        Args:
            result: Wynik meczu
            
        Returns:
            CollectiveMemoryDocument gotowy do indeksowania
        """
        if not self.can_handle(result):
            raise ValueError(f"Cannot convert {type(result).__name__} to CollectiveMemoryDocument")
        
        # Buduj tekst dokumentu
        text_parts = []
        
        # Podstawowe informacje o meczu
        result_text = self._get_result_text(result)
        text_parts.append(f"{result.home_team} {result.home_goals}-{result.away_goals} {result.away_team}")
        text_parts.append(f"Result: {result_text}")
        
        # Data meczu (jeśli dostępna)
        if hasattr(result, 'match_date') and result.match_date:
            text_parts.append(f"Date: {result.match_date}")
        
        # Źródło danych
        source = getattr(result, 'source', '')
        if source:
            text_parts.append(f"Source: {source}")
        
        # Buduj metadane
        created_at = getattr(result, 'created_at', None)
        metadata = {
            'match_id': result.match_id,
            'home_team': result.home_team,
            'away_team': result.away_team,
            'home_goals': result.home_goals,
            'away_goals': result.away_goals,
            'result': result_text,
            'source': source,
            'created_at': created_at.isoformat() if created_at and hasattr(created_at, 'isoformat') else str(created_at) if created_at else None,
        }
        
        # Dodaj dodatkowe metadane jeśli istnieją
        if hasattr(result, 'metadata') and result.metadata:
            metadata.update(result.metadata)
        
        # Oblicz ważność dokumentu
        importance = self._calculate_importance(result)
        
        # Tagi
        tags = self._generate_tags(result)
        
        return self.create_document(
            source_id=result.match_id,
            text="\n".join(text_parts),
            metadata=metadata,
            importance=importance,
            tags=tags
        )
    
    def _get_result_text(self, result: Any) -> str:
        """Zwraca tekstowy opis wyniku."""
        if result.home_goals > result.away_goals:
            return "HOME_WIN"
        elif result.home_goals < result.away_goals:
            return "AWAY_WIN"
        else:
            return "DRAW"
    
    def _calculate_importance(self, result: Any) -> float:
        """Oblicza ważność dokumentu na podstawie charakteru meczu."""
        importance = 0.5  # Domyślna wartość
        
        # Wyższa ważność dla meczów z wieloma golami (bardziej interesujące)
        total_goals = result.home_goals + result.away_goals
        if total_goals >= 5:
            importance += 0.2
        elif total_goals >= 3:
            importance += 0.1
        
        # Wyższa ważność dla niespodziewanych wyników
        # (Przykład: słabsza drużyna wygrywa wysoko)
        # Tutaj można by dodać logikę porównania siły drużyn, ale na razie pomijamy
        
        # Ogranicz do zakresu 0.0-1.0
        return min(1.0, max(0.0, importance))
    
    def _generate_tags(self, result: Any) -> list:
        """Generuje tagi dla dokumentu."""
        tags = [
            f"team:{result.home_team.lower()}",
            f"team:{result.away_team.lower()}",
            f"match:{result.match_id}"
        ]
        
        # Tag wyniku
        result_text = self._get_result_text(result)
        tags.append(f"result:{result_text.lower()}")
        
        # Tag liczby goli
        total_goals = result.home_goals + result.away_goals
        if total_goals >= 5:
            tags.append("goals:high")
        elif total_goals >= 3:
            tags.append("goals:medium")
        else:
            tags.append("goals:low")
        
        # Tag różnicy goli
        goal_diff = abs(result.home_goals - result.away_goals)
        if goal_diff >= 3:
            tags.append("margin:large")
        elif goal_diff >= 2:
            tags.append("margin:medium")
        else:
            tags.append("margin:small")
        
        return tags
