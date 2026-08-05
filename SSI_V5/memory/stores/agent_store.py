# SSI V5 - Agent Memory Store
# ETAP 1.2.7.3: Adaptive Knowledge Ecosystem

"""
AgentMemoryStore -_indywidualna pamięć agentów.

Odpowiada za:
- Przechowywanie indywidualnych doświadczeń agentów
- Historia decyzji i ich konsekwencji
- Wyciągnięte wnioski i nauczone lekcje
- Preferencje i style podejmowania decyzji

Przykładowy rekord:
{
    "type": "agent_experience",
    "agent_id": "agent_001",
    "experience_type": "failed_prediction",  # decision, success, failure, learning, observation
    "decision": {
        "type": "BTTS_Yes",
        "confidence": 0.75,
        "reasoning": "Home team strong attack",
        "context": {
            "match": "TeamA vs TeamB",
            "odds": 1.85,
            "league": "Premier League"
        }
    },
    "outcome": {
        "result": "BTTS_No",
        "actual_outcome": "0:0",
        "profit": -1.0
    },
    "lesson": {
        "title": "Overconfidence in low-scoring teams",
        "description": "Agent overestimated BTTS probability for defensive teams",
        "confidence": 0.76,
        "tags": ["overconfidence", "defensive_teams", "BTTS"]
    },
    "preferences": {
        "risk_tolerance": "medium",
        "preferred_markets": ["BTTS", "Over25"],
        "avoid": ["Draw"]
    },
    "performance": {
        "total_decisions": 150,
        "success_rate": 0.68,
        "avg_confidence": 0.72
    }
}

Interfejs:
    - Dziedziczy z BaseMemoryStore
    - Rozszerza o specyficzne metody agentów
"""

from typing import Any, Dict, List, Optional
from .base_store import BaseMemoryStore, MemoryRecord, MemoryQuery


class AgentMemoryStore(BaseMemoryStore):
    """
    Indywidualna pamięć agentów.
    """
    
    def __init__(self):
        """Inicjalizacja AgentMemoryStore."""
        super().__init__(store_type="agent")
        # Dodatkowe indeksy specyficzne dla agentów
        self._agent_index: Dict[str, List[str]] = {}  # agent_id -> [memory_ids]
        self._experience_index: Dict[str, List[str]] = {}  # experience_type -> [memory_ids]
    
    def _get_memory_type(self) -> str:
        """Typ pamięci: agent_memory."""
        return "agent_memory"
    
    def _validate_record(self, record: MemoryRecord) -> bool:
        """
        Walidacja rekordu AgentMemory.
        
        Wymagane pola:
        - agent_id: ID agenta
        - experience_type: Typ doświadczenia
        """
        content = record.content
        
        # Debug
        # print(f"DEBUG: Validating record with content keys: {list(content.keys())}")
        # print(f"DEBUG: content = {content}")
        
        # Wymagane pola
        required_fields = ['agent_id', 'experience_type']
        for field in required_fields:
            if field not in content:
                return False
        
        # Walidacja typu doświadczenia
        valid_experiences = [
            'decision', 'success', 'failure', 'partial_success',
            'learning', 'observation', 'error', 'correction',
            'failed_prediction', 'successful_prediction'
        ]
        if content['experience_type'] not in valid_experiences:
            return False
        
        return True
    
    def _add_to_indexes(self, record: MemoryRecord) -> None:
        """Dodanie rekordu do dodatkowych indeksów."""
        super()._add_to_indexes(record)
        
        content = record.content
        
        # Indeks po ID agenta
        agent_id = content.get('agent_id', 'unknown')
        if agent_id not in self._agent_index:
            self._agent_index[agent_id] = []
        self._agent_index[agent_id].append(record.memory_id)
        
        # Indeks po typie doświadczenia
        exp_type = content.get('experience_type', 'unknown')
        if exp_type not in self._experience_index:
            self._experience_index[exp_type] = []
        self._experience_index[exp_type].append(record.memory_id)
    
    def _remove_from_indexes(self, record: MemoryRecord) -> None:
        """Usunięcie rekordu z dodatkowych indeksów."""
        super()._remove_from_indexes(record)
        
        content = record.content
        
        # Indeks po ID agenta
        agent_id = content.get('agent_id', 'unknown')
        if agent_id in self._agent_index:
            if record.memory_id in self._agent_index[agent_id]:
                self._agent_index[agent_id].remove(record.memory_id)
        
        # Indeks po typie doświadczenia
        exp_type = content.get('experience_type', 'unknown')
        if exp_type in self._experience_index:
            if record.memory_id in self._experience_index[exp_type]:
                self._experience_index[exp_type].remove(record.memory_id)
    
    def save_agent_experience(
        self,
        agent_id: str,
        experience_type: str,
        decision: Optional[Dict[str, Any]] = None,
        outcome: Optional[Dict[str, Any]] = None,
        lesson: Optional[Dict[str, Any]] = None,
        preferences: Optional[Dict[str, Any]] = None,
        performance: Optional[Dict[str, Any]] = None,
        source: str = "agent_runtime",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Zapis doświadczenia agenta (wygodna metoda).
        
        Args:
            agent_id: ID agenta
            experience_type: Typ doświadczenia
            decision: Informacje o decyzji
            outcome: Skutek decyzji
            lesson: Wyciągnięta lekcja
            preferences: Preferencje agenta
            performance: Metryki wydajności
            source: Źródło rekordu
            metadata: Metadane
            
        Returns:
            memory_id zapisanego rekordu
        """
        content = {
            'agent_id': agent_id,
            'experience_type': experience_type,
        }
        
        if decision:
            content['decision'] = decision
        if outcome:
            content['outcome'] = outcome
        if lesson:
            content['lesson'] = lesson
        if preferences:
            content['preferences'] = preferences
        if performance:
            content['performance'] = performance
        
        record = MemoryRecord.create(
            content=content,
            memory_type=self._get_memory_type(),
            source=source,
            metadata=metadata
        )
        
        return self.save(record)
    
    def get_by_agent(self, agent_id: str) -> List[MemoryRecord]:
        """
        Pobranie wszystkich doświadczeń konkretnego agenta.
        
        Args:
            agent_id: ID agenta
            
        Returns:
            Lista rekordów
        """
        memory_ids = self._agent_index.get(agent_id, [])
        return [self._records[mid] for mid in memory_ids if mid in self._records]
    
    def get_by_experience_type(self, exp_type: str) -> List[MemoryRecord]:
        """
        Pobranie wszystkich doświadczeń danego typu.
        
        Args:
            exp_type: Typ doświadczenia
            
        Returns:
            Lista rekordów
        """
        memory_ids = self._experience_index.get(exp_type, [])
        return [self._records[mid] for mid in memory_ids if mid in self._records]
    
    def get_successes(self, agent_id: str) -> List[MemoryRecord]:
        """Pobranie wszystkich sukcesów agenta."""
        all_experiences = self.get_by_agent(agent_id)
        return [r for r in all_experiences if r.content.get('experience_type') == 'success']
    
    def get_failures(self, agent_id: str) -> List[MemoryRecord]:
        """Pobranie wszystkich porażek agenta."""
        all_experiences = self.get_by_agent(agent_id)
        return [r for r in all_experiences if r.content.get('experience_type') in ['failure', 'error']]
    
    def get_lessons(self, agent_id: str) -> List[MemoryRecord]:
        """Pobranie wszystkich lekcji agenta."""
        all_experiences = self.get_by_agent(agent_id)
        return [r for r in all_experiences if 'lesson' in r.content]
    
    def get_agent_statistics(self, agent_id: str) -> Dict[str, Any]:
        """
        Pobranie statystyk dla konkretnego agenta.
        
        Args:
            agent_id: ID agenta
            
        Returns:
            Statystyki agenta
        """
        records = self.get_by_agent(agent_id)
        
        if not records:
            return {
                'agent_id': agent_id,
                'total_experiences': 0,
                'success_count': 0,
                'failure_count': 0,
                'experience_types': {},
                'lessons_learned': 0
            }
        
        # Klasyfikacja typów doświadczeń
        SUCCESS_TYPES = ['success', 'successful_prediction']
        FAILURE_TYPES = ['failure', 'failed_prediction', 'error', 'correction']
        
        total = len(records)
        successes = sum(1 for r in records if r.content.get('experience_type') in SUCCESS_TYPES)
        failures = sum(1 for r in records if r.content.get('experience_type') in FAILURE_TYPES)
        
        # Typy doświadczeń
        exp_types = {}
        for r in records:
            exp_type = r.content.get('experience_type', 'unknown')
            exp_types[exp_type] = exp_types.get(exp_type, 0) + 1
        
        # Lekcje
        lessons = sum(1 for r in records if 'lesson' in r.content)
        
        return {
            'agent_id': agent_id,
            'total_experiences': total,
            'success_count': successes,
            'failure_count': failures,
            'success_rate': successes / total if total > 0 else 0.0,
            'experience_types': exp_types,
            'lessons_learned': lessons
        }
    
    def get_all_agents_statistics(self) -> List[Dict[str, Any]]:
        """
        Pobranie statystyk dla wszystkich agentów.
        
        Returns:
            Lista statystyk agentów
        """
        return [self.get_agent_statistics(agent_id) for agent_id in self._agent_index]
    
    def get_best_agents(self, limit: int = 5, min_experiences: int = 10) -> List[Dict[str, Any]]:
        """
        Pobranie najlepszych agentów według success_rate.
        
        Args:
            limit: Maksymalna liczba agentów
            min_experiences: Minimalna liczba doświadczeń
            
        Returns:
            Lista agentów posortowanych po success_rate
        """
        agents_stats = []
        for agent_id in self._agent_index:
            stats = self.get_agent_statistics(agent_id)
            if stats['total_experiences'] >= min_experiences:
                agents_stats.append(stats)
        
        # Sortowanie po success_rate
        sorted_agents = sorted(
            agents_stats,
            key=lambda x: x['success_rate'],
            reverse=True
        )[:limit]
        
        return sorted_agents
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Pobranie statystyk składowej.
        
        Returns:
            Statystyki z dodatkowymi informacjami o agentach
        """
        stats = super().get_statistics()
        stats['agents'] = list(self._agent_index.keys())
        stats['experience_types'] = list(self._experience_index.keys())
        stats['total_agents'] = len(self._agent_index)
        stats['total_experience_types'] = len(self._experience_index)
        return stats
    
    def clear(self) -> None:
        """Wyczyszczenie pamięci."""
        super().clear()
        self._agent_index.clear()
        self._experience_index.clear()
