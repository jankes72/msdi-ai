# SSI V5 - Experiment Memory Store
# ETAP 1.2.7.3: Adaptive Knowledge Ecosystem

"""
ExperimentMemoryStore - Pamięć wyników eksperymentów.

Odpowiada za:
- Przechowywanie hipotez i ich weryfikacji
- Rejestrację eksperymentów systemowych
- Powiązanie eksperymentów z decyzjami i wynikami
- Śledzenie ewolucji strategii

Przykładowy rekord:
{
    "type": "experiment_record",
    "experiment_id": "exp_001",
    "cycle_id": "cycle_001",
    "hypothesis": {
        "title": "Market reacts slower after odds movement",
        "description": "Test if BTTS probability changes lag behind odds changes",
        "category": "market_behavior",
        "confidence": 0.75,
        "expected_outcome": " confirming | denying | inconclusive"
    },
    "design": {
        "type": "A/B_test",
        "control_group": {
            "strategy": "current_baseline",
            "size": 50
        },
        "test_group": {
            "strategy": "odds_lag_v1",
            "size": 50
        },
        "duration": "7_days",
        "start_time": "2026-08-04T10:00:00",
        "end_time": "2026-08-04T17:00:00"
    },
    "input": {
        "world_state": {...},
        "strategy_parameters": {...},
        "market_conditions": {...}
    },
    "execution": {
        "start_timestamp": "2026-08-04T10:00:00",
        "end_timestamp": "2026-08-04T10:05:00",
        "status": "completed",
        "errors": []
    },
    "result": {
        "outcome": "confirming",
        "confidence": 0.82,
        "metrics": {
            "accuracy": 0.78,
            "profit_factor": 1.25,
            "sharpe_ratio": 1.45
        },
        "detailed_findings": {
            "control_group": {"accuracy": 0.72, "profit": 10.5},
            "test_group": {"accuracy": 0.84, "profit": 15.2}
        }
    },
    "conclusion": {
        "verdict": "accept_hypothesis",
        "recommendation": "Implement odds_lag_v1 strategy",
        "next_steps": ["Test with larger sample", "Optimize parameters"]
    },
    "knowledge_impact": {
        "new_knowledge": ["Odds lag confirmed for BTTS markets"],
        "invalidated_knowledge": ["Immediate odds reaction assumption"],
        "related_knowledge": ["exp_045", "exp_078"]
    }
}

Interfejs:
    - Dziedziczy z BaseMemoryStore
    - Rozszerza o specyficzne metody eksperymentów
"""

from typing import Any, Dict, List, Optional
from .base_store import BaseMemoryStore, MemoryRecord, MemoryQuery


class ExperimentMemoryStore(BaseMemoryStore):
    """
    Pamięć wyników eksperymentów systemowych.
    """
    
    def __init__(self):
        """Inicjalizacja ExperimentMemoryStore."""
        super().__init__(store_type="experiment")
        # Dodatkowe indeksy specyficzne dla eksperymentów
        self._experiment_index: Dict[str, List[str]] = {}  # experiment_id -> [memory_ids]
        self._cycle_index: Dict[str, List[str]] = {}  # cycle_id -> [memory_ids]
        self._hypothesis_index: Dict[str, List[str]] = {}  # hypothesis_category -> [memory_ids]
        self._outcome_index: Dict[str, List[str]] = {}  # outcome -> [memory_ids]
        self._verdict_index: Dict[str, List[str]] = {}  # verdict -> [memory_ids]
    
    def _get_memory_type(self) -> str:
        """Typ pamięci: experiment_memory."""
        return "experiment_memory"
    
    def _validate_record(self, record: MemoryRecord) -> bool:
        """
        Walidacja rekordu ExperimentMemory.
        
        Dla rekordów typu experiment_memory wymagane:
        - experiment_id: ID eksperymentu
        
        Dla rekordów innych typów (np. system_memory, knowledge_record)
        walidacja jest pomijana, ponieważ nie są to Amtow security eksperymenty.
        """
        content = record.content
        
        # TYLKO rekordy typu experiment_memory muszą mieć experiment_id
        if record.type == "experiment_memory":
            required_fields = ['experiment_id']
            for field in required_fields:
                if field not in content:
                    return False
        
        # Dla innych typów (system_memory, knowledge_record) nie wymagamy experiment_id
        # Jest to rozwiązanie tymczasowe dla ETAPU 1.2.7.3
        # Docelowo system_memory i knowledge_record będą miały swoje Store'y
        
        return True
    
    def _add_to_indexes(self, record: MemoryRecord) -> None:
        """Dodanie rekordu do dodatkowych indeksów."""
        super()._add_to_indexes(record)
        
        content = record.content
        
        # Indeks po ID eksperymentu
        exp_id = content.get('experiment_id', 'unknown')
        if exp_id not in self._experiment_index:
            self._experiment_index[exp_id] = []
        self._experiment_index[exp_id].append(record.memory_id)
        
        # Indeks po ID cyklu
        cycle_id = content.get('cycle_id', 'unknown')
        if cycle_id not in self._cycle_index:
            self._cycle_index[cycle_id] = []
        self._cycle_index[cycle_id].append(record.memory_id)
        
        # Indeks po kategorii hipotezy
        hypothesis = content.get('hypothesis', {})
        category = hypothesis.get('category', 'unknown') if isinstance(hypothesis, dict) else 'unknown'
        if category not in self._hypothesis_index:
            self._hypothesis_index[category] = []
        self._hypothesis_index[category].append(record.memory_id)
        
        # Indeks po wyniku (outcome)
        result = content.get('result', {})
        outcome = result.get('outcome', 'unknown') if isinstance(result, dict) else 'unknown'
        if outcome not in self._outcome_index:
            self._outcome_index[outcome] = []
        self._outcome_index[outcome].append(record.memory_id)
        
        # Indeks po werdykcie
        conclusion = content.get('conclusion', {})
        verdict = conclusion.get('verdict', 'unknown') if isinstance(conclusion, dict) else 'unknown'
        if verdict not in self._verdict_index:
            self._verdict_index[verdict] = []
        self._verdict_index[verdict].append(record.memory_id)
    
    def _remove_from_indexes(self, record: MemoryRecord) -> None:
        """Usunięcie rekordu z dodatkowych indeksów."""
        super()._remove_from_indexes(record)
        
        content = record.content
        
        # Indeks po ID eksperymentu
        exp_id = content.get('experiment_id', 'unknown')
        if exp_id in self._experiment_index:
            if record.memory_id in self._experiment_index[exp_id]:
                self._experiment_index[exp_id].remove(record.memory_id)
        
        # Indeks po ID cyklu
        cycle_id = content.get('cycle_id', 'unknown')
        if cycle_id in self._cycle_index:
            if record.memory_id in self._cycle_index[cycle_id]:
                self._cycle_index[cycle_id].remove(record.memory_id)
        
        # Indeks po kategorii hipotezy
        hypothesis = content.get('hypothesis', {})
        category = hypothesis.get('category', 'unknown') if isinstance(hypothesis, dict) else 'unknown'
        if category in self._hypothesis_index:
            if record.memory_id in self._hypothesis_index[category]:
                self._hypothesis_index[category].remove(record.memory_id)
        
        # Indeks po wyniku
        result = content.get('result', {})
        outcome = result.get('outcome', 'unknown') if isinstance(result, dict) else 'unknown'
        if outcome in self._outcome_index:
            if record.memory_id in self._outcome_index[outcome]:
                self._outcome_index[outcome].remove(record.memory_id)
        
        # Indeks po werdykcie
        conclusion = content.get('conclusion', {})
        verdict = conclusion.get('verdict', 'unknown') if isinstance(conclusion, dict) else 'unknown'
        if verdict in self._verdict_index:
            if record.memory_id in self._verdict_index[verdict]:
                self._verdict_index[verdict].remove(record.memory_id)
    
    def save_experiment_result(
        self,
        experiment_id: str,
        cycle_id: Optional[str] = None,
        hypothesis: Optional[Dict[str, Any]] = None,
        design: Optional[Dict[str, Any]] = None,
        input_data: Optional[Dict[str, Any]] = None,
        execution: Optional[Dict[str, Any]] = None,
        result: Optional[Dict[str, Any]] = None,
        conclusion: Optional[Dict[str, Any]] = None,
        knowledge_impact: Optional[Dict[str, Any]] = None,
        source: str = "pipeline",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Zapis wyniku eksperymentu (wygodna metoda).
        
        Args:
            experiment_id: ID eksperymentu
            cycle_id: ID cyklu (opcjonalny)
            hypothesis: Hipoteza testowana
            design: Projekt eksperymentu
            input_data: Dane wejściowe
            execution: Informacje o wykonaniu
            result: Wynik eksperymentu
            conclusion: Wniosek
            knowledge_impact: Wpływ na wiedzę
            source: Źródło rekordu
            metadata: Metadane
            
        Returns:
            memory_id zapisanego rekordu
        """
        content = {
            'experiment_id': experiment_id,
        }
        
        if cycle_id:
            content['cycle_id'] = cycle_id
        if hypothesis:
            content['hypothesis'] = hypothesis
        if design:
            content['design'] = design
        if input_data:
            content['input'] = input_data
        if execution:
            content['execution'] = execution
        if result:
            content['result'] = result
        if conclusion:
            content['conclusion'] = conclusion
        if knowledge_impact:
            content['knowledge_impact'] = knowledge_impact
        
        record = MemoryRecord.create(
            content=content,
            memory_type=self._get_memory_type(),
            source=source,
            metadata=metadata
        )
        
        return self.save(record)
    
    def get_by_experiment(self, experiment_id: str) -> List[MemoryRecord]:
        """
        Pobranie wszystkich rekordów danego eksperymentu.
        
        Args:
            experiment_id: ID eksperymentu
            
        Returns:
            Lista rekordów
        """
        memory_ids = self._experiment_index.get(experiment_id, [])
        return [self._records[mid] for mid in memory_ids if mid in self._records]
    
    def get_by_cycle(self, cycle_id: str) -> List[MemoryRecord]:
        """
        Pobranie wszystkich eksperymentów z danego cyklu.
        
        Args:
            cycle_id: ID cyklu
            
        Returns:
            Lista rekordów
        """
        memory_ids = self._cycle_index.get(cycle_id, [])
        return [self._records[mid] for mid in memory_ids if mid in self._records]
    
    def get_by_hypothesis_category(self, category: str) -> List[MemoryRecord]:
        """
        Pobranie eksperymentów według kategorii hipotezy.
        
        Args:
            category: Kategoria hipotezy
            
        Returns:
            Lista rekordów
        """
        memory_ids = self._hypothesis_index.get(category, [])
        return [self._records[mid] for mid in memory_ids if mid in self._records]
    
    def get_by_outcome(self, outcome: str) -> List[MemoryRecord]:
        """
        Pobranie eksperymentów według wyniku (outcome).
        
        Args:
            outcome: Wynik (confirming, denying, inconclusive)
            
        Returns:
            Lista rekordów
        """
        memory_ids = self._outcome_index.get(outcome, [])
        return [self._records[mid] for mid in memory_ids if mid in self._records]
    
    def get_by_verdict(self, verdict: str) -> List[MemoryRecord]:
        """
        Pobranie eksperymentów według werdyktu.
        
        Args:
            verdict: Werdykt (accept_hypothesis, reject_hypothesis, needs_more_data)
            
        Returns:
            Lista rekordów
        """
        memory_ids = self._verdict_index.get(verdict, [])
        return [self._records[mid] for mid in memory_ids if mid in self._records]
    
    def get_successful_experiments(self) -> List[MemoryRecord]:
        """Pobranie wszystkich udanych eksperymentów (potwierdzonych hipotez)."""
        confirming = self.get_by_outcome('confirming')
        accepted = self.get_by_verdict('accept_hypothesis')
        # Zwróć unikalne rekordy
        return list(set(confirming + accepted))
    
    def get_failed_experiments(self) -> List[MemoryRecord]:
        """Pobranie wszystkich nieudanych eksperymentów."""
        denying = self.get_by_outcome('denying')
        rejected = self.get_by_verdict('reject_hypothesis')
        # Zwróć unikalne rekordy
        return list(set(denying + rejected))
    
    def get_inconclusive_experiments(self) -> List[MemoryRecord]:
        """Pobranie eksperymentów z niejednoznacznym rezultatem."""
        return self.get_by_outcome('inconclusive') + self.get_by_verdict('needs_more_data')
    
    def get_experiment_statistics(self, experiment_id: str) -> Dict[str, Any]:
        """
        Pobranie statystyk konkretnego eksperymentu.
        
        Args:
            experiment_id: ID eksperymentu
            
        Returns:
            Statystyki eksperymentu
        """
        records = self.get_by_experiment(experiment_id)
        
        if not records:
            return {
                'experiment_id': experiment_id,
                'total_records': 0,
                'has_result': False
            }
        
        # Bierzemy ostatni rekord jako najnowszy
        latest = records[-1]
        content = latest.content
        
        return {
            'experiment_id': experiment_id,
            'total_records': len(records),
            'has_hypothesis': 'hypothesis' in content,
            'has_result': 'result' in content,
            'outcome': content.get('result', {}).get('outcome', 'unknown'),
            'verdict': content.get('conclusion', {}).get('verdict', 'unknown'),
            'confidence': content.get('result', {}).get('confidence', 0.0)
        }
    
    def get_hypothesis_statistics(self, category: str) -> Dict[str, Any]:
        """
        Pobranie statystyk hipotez w danej kategorii.
        
        Args:
            category: Kategoria hipotezy
            
        Returns:
            Statystyki hipotez
        """
        records = self.get_by_hypothesis_category(category)
        
        if not records:
            return {
                'category': category,
                'total_experiments': 0,
                'confirming': 0,
                'denying': 0,
                'inconclusive': 0
            }
        
        confirming = sum(1 for r in records if r.content.get('result', {}).get('outcome') == 'confirming')
        denying = sum(1 for r in records if r.content.get('result', {}).get('outcome') == 'denying')
        inconclusive = sum(1 for r in records if r.content.get('result', {}).get('outcome') == 'inconclusive')
        
        return {
            'category': category,
            'total_experiments': len(records),
            'confirming': confirming,
            'denying': denying,
            'inconclusive': inconclusive,
            'confirmation_rate': confirming / len(records) if records else 0.0
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Pobranie statystyk składowej.
        
        Returns:
            Statystyki z dodatkowymi informacjami o eksperymentach
        """
        stats = super().get_statistics()
        stats['experiments'] = list(self._experiment_index.keys())
        stats['cycles'] = list(self._cycle_index.keys())
        stats['hypothesis_categories'] = list(self._hypothesis_index.keys())
        stats['outcomes'] = {k: len(v) for k, v in self._outcome_index.items()}
        stats['verdicts'] = {k: len(v) for k, v in self._verdict_index.items()}
        stats['total_experiments'] = len(self._experiment_index)
        stats['total_cycles'] = len(self._cycle_index)
        stats['total_hypothesis_categories'] = len(self._hypothesis_index)
        return stats
    
    def clear(self) -> None:
        """Wyczyszczenie pamięci."""
        super().clear()
        self._experiment_index.clear()
        self._cycle_index.clear()
        self._hypothesis_index.clear()
        self._outcome_index.clear()
        self._verdict_index.clear()
