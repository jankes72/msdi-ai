# SSI V5 - Model Memory Store
# ETAP 1.2.7.3: Adaptive Knowledge Ecosystem

"""
ModelMemoryStore - Pamięć doświadczeń modeli.

Odpowiada za:
- Przechowywanie doświadczeń modeli predykcyjnych
- Historia dokładności i skuteczności
- Kontekst użycia modeli
- Powiązania z strategiami

Przykładowy rekord:
{
    "type": "model_experience",
    "model_name": "RandomForest_v3",
    "model_version": "1.2.0",
    "strategy": "trend_follow",
    "result": "success",
    "accuracy": 0.82,
    "confidence": 0.78,
    "context": {
        "league": "Premier League",
        "market": "BTTS",
        "odds_range": [1.5, 3.0],
        "sample_size": 120
    },
    "performance_metrics": {
        "precision": 0.85,
        "recall": 0.78,
        "f1_score": 0.81
    },
    "training_data": {
        "features": ["home_form", "away_form", "h2h"],
        "target": "BTTS_Yes"
    },
    "lessons_learned": [
        "Works best with sample_size > 100",
        "Struggles with draw predictions"
    ]
}

Interfejs:
    - Dziedziczy z BaseMemoryStore
    - Rozszerza o specyficzne metody modeli
"""

from typing import Any, Dict, List, Optional
from .base_store import BaseMemoryStore, MemoryRecord, MemoryQuery


class ModelMemoryStore(BaseMemoryStore):
    """
    Pamięć doświadczeń modeli predykcyjnych.
    """
    
    def __init__(self):
        """Inicjalizacja ModelMemoryStore."""
        super().__init__(store_type="model")
        # Dodatkowe indeksy specyficzne dla modeli
        self._model_index: Dict[str, List[str]] = {}  # model_name -> [memory_ids]
        self._strategy_index: Dict[str, List[str]] = {}  # strategy -> [memory_ids]
        self._result_index: Dict[str, List[str]] = {}  # result -> [memory_ids]
    
    def _get_memory_type(self) -> str:
        """Typ pamięci: model_memory."""
        return "model_memory"
    
    def _validate_record(self, record: MemoryRecord) -> bool:
        """
        Walidacja rekordu ModelMemory.
        
        Wymagane pola:
        - model_name: Nazwa modelu
        - result: Wynik (success, failure, partial)
        """
        content = record.content
        
        # Wymagane pola
        required_fields = ['model_name', 'result']
        for field in required_fields:
            if field not in content:
                return False
        
        # Walidacja wyniku
        valid_results = ['success', 'failure', 'partial', 'unknown']
        if content['result'] not in valid_results:
            return False
        
        return True
    
    def _add_to_indexes(self, record: MemoryRecord) -> None:
        """Dodanie rekordu do dodatkowych indeksów."""
        super()._add_to_indexes(record)
        
        content = record.content
        
        # Indeks po nazwie modelu
        model_name = content.get('model_name', 'unknown')
        if model_name not in self._model_index:
            self._model_index[model_name] = []
        self._model_index[model_name].append(record.memory_id)
        
        # Indeks po strategii
        strategy = content.get('strategy', 'unknown')
        if strategy not in self._strategy_index:
            self._strategy_index[strategy] = []
        self._strategy_index[strategy].append(record.memory_id)
        
        # Indeks po wyniku
        result = content.get('result', 'unknown')
        if result not in self._result_index:
            self._result_index[result] = []
        self._result_index[result].append(record.memory_id)
    
    def _remove_from_indexes(self, record: MemoryRecord) -> None:
        """Usunięcie rekordu z dodatkowych indeksów."""
        super()._remove_from_indexes(record)
        
        content = record.content
        
        # Indeks po nazwie modelu
        model_name = content.get('model_name', 'unknown')
        if model_name in self._model_index:
            if record.memory_id in self._model_index[model_name]:
                self._model_index[model_name].remove(record.memory_id)
        
        # Indeks po strategii
        strategy = content.get('strategy', 'unknown')
        if strategy in self._strategy_index:
            if record.memory_id in self._strategy_index[strategy]:
                self._strategy_index[strategy].remove(record.memory_id)
        
        # Indeks po wyniku
        result = content.get('result', 'unknown')
        if result in self._result_index:
            if record.memory_id in self._result_index[result]:
                self._result_index[result].remove(record.memory_id)
    
    def save_model_experience(
        self,
        model_name: str,
        model_version: str = "1.0.0",
        strategy: str = "unknown",
        result: str = "success",
        accuracy: Optional[float] = None,
        confidence: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
        performance_metrics: Optional[Dict[str, float]] = None,
        training_data: Optional[Dict[str, Any]] = None,
        lessons_learned: Optional[List[str]] = None,
        source: str = "pipeline",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Zapis doświadczenia modelu (wygodna metoda).
        
        Args:
            model_name: Nazwa modelu
            model_version: Wersja modelu
            strategy: Strategia z jaką był używany
            result: Wynik (success, failure, partial)
            accuracy: Dokładność (0.0-1.0)
            confidence: Pewność (0.0-1.0)
            context: Kontekst użycia
            performance_metrics: Metryki wydajności
            training_data: Dane treningowe
            lessons_learned: Wyciągnięte wnioski
            source: Źródło rekordu
            metadata: Metadane
            
        Returns:
            memory_id zapisanego rekordu
        """
        content = {
            'model_name': model_name,
            'model_version': model_version,
            'strategy': strategy,
            'result': result,
        }
        
        if accuracy is not None:
            content['accuracy'] = accuracy
        if confidence is not None:
            content['confidence'] = confidence
        if context:
            content['context'] = context
        if performance_metrics:
            content['performance_metrics'] = performance_metrics
        if training_data:
            content['training_data'] = training_data
        if lessons_learned:
            content['lessons_learned'] = lessons_learned
        
        record = MemoryRecord.create(
            content=content,
            memory_type=self._get_memory_type(),
            source=source,
            metadata=metadata
        )
        
        return self.save(record)
    
    def get_by_model(self, model_name: str) -> List[MemoryRecord]:
        """
        Pobranie wszystkich doświadczeń konkretnego modelu.
        
        Args:
            model_name: Nazwa modelu
            
        Returns:
            Lista rekordów
        """
        memory_ids = self._model_index.get(model_name, [])
        return [self._records[mid] for mid in memory_ids if mid in self._records]
    
    def get_by_strategy(self, strategy: str) -> List[MemoryRecord]:
        """
        Pobranie wszystkich doświadczeń związanych z strategią.
        
        Args:
            strategy: Nazwa strategii
            
        Returns:
            Lista rekordów
        """
        memory_ids = self._strategy_index.get(strategy, [])
        return [self._records[mid] for mid in memory_ids if mid in self._records]
    
    def get_successful(self) -> List[MemoryRecord]:
        """Pobranie wszystkich udanych doświadczeń."""
        return self.get_by_result('success')
    
    def get_failed(self) -> List[MemoryRecord]:
        """Pobranie wszystkich nieudanych doświadczeń."""
        return self.get_by_result('failure')
    
    def get_by_result(self, result: str) -> List[MemoryRecord]:
        """
        Pobranie doświadczeń po wyniku.
        
        Args:
            result: Wynik (success, failure, partial)
            
        Returns:
            Lista rekordów
        """
        memory_ids = self._result_index.get(result, [])
        return [self._records[mid] for mid in memory_ids if mid in self._records]
    
    def get_model_statistics(self, model_name: str) -> Dict[str, Any]:
        """
        Pobranie statystyk dla konkretnego modelu.
        
        Args:
            model_name: Nazwa modelu
            
        Returns:
            Statystyki modelu
        """
        records = self.get_by_model(model_name)
        
        if not records:
            return {
                'model_name': model_name,
                'total_experiences': 0,
                'success_rate': 0.0,
                'avg_accuracy': 0.0,
                'avg_confidence': 0.0
            }
        
        total = len(records)
        successful = sum(1 for r in records if r.content.get('result') == 'success')
        accuracies = [r.content.get('accuracy') for r in records if r.content.get('accuracy') is not None]
        confidences = [r.content.get('confidence') for r in records if r.content.get('confidence') is not None]
        
        return {
            'model_name': model_name,
            'total_experiences': total,
            'success_rate': successful / total if total > 0 else 0.0,
            'avg_accuracy': sum(accuracies) / len(accuracies) if accuracies else 0.0,
            'avg_confidence': sum(confidences) / len(confidences) if confidences else 0.0,
            'success_count': successful,
            'failure_count': total - successful
        }
    
    def get_best_models(self, limit: int = 5, min_experiences: int = 10) -> List[Dict[str, Any]]:
        """
        Pobranie najlepszych modeli według success_rate.
        
        Args:
            limit: Maksymalna liczba modeli
            min_experiences: Minimalna liczba doświadczeń
            
        Returns:
            Lista modeli posortowanych po success_rate
        """
        model_stats = {}
        for model_name in self._model_index:
            stats = self.get_model_statistics(model_name)
            if stats['total_experiences'] >= min_experiences:
                model_stats[model_name] = stats
        
        # Sortowanie po success_rate
        sorted_models = sorted(
            model_stats.values(),
            key=lambda x: x['success_rate'],
            reverse=True
        )[:limit]
        
        return sorted_models
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Pobranie statystyk składowej.
        
        Returns:
            Statystyki z dodatkowymi informacjami o modelach
        """
        stats = super().get_statistics()
        stats['models'] = list(self._model_index.keys())
        stats['strategies'] = list(self._strategy_index.keys())
        stats['results'] = {k: len(v) for k, v in self._result_index.items()}
        stats['total_models'] = len(self._model_index)
        stats['total_strategies'] = len(self._strategy_index)
        return stats
    
    def clear(self) -> None:
        """Wyczyszczenie pamięci."""
        super().clear()
        self._model_index.clear()
        self._strategy_index.clear()
        self._result_index.clear()
