# SSI V5 Laboratory Module - Strategy Laboratory
# ==================================================
#
# ETAP: 5.2.6.1 - Strategy Laboratory Foundation
# Data: 2026-08-04
#
# Odpowiedzialnosc:
# - Izolowane srodowisko testowe dla strategii
# - Eksperymenty strategii bez wplywu na produkcje
# - Historia eksperymentow
# - Porownanie wariantow strategii
# - Ocena jakości eksperymentow
#
# ZASADY:
# 1. NIE MODYFIKUJE PRODUKCJI
# 2. Korzysta z kopii danych (nie oryginalow)
# 3. Wyniki sa niezalezne od systemu produkcyjnego
#

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from pathlib import Path
from datetime import datetime
import json
import os
import copy
import uuid
from threading import RLock


class ExperimentStatus(Enum):
    """Status eksperymentu strategii"""
    PENDING = "pending"       # Oczekuje na wykonanie
    RUNNING = "running"       # W trakcie wykonania
    COMPLETED = "completed"   # Zakonczony pomyslnie
    FAILED = "failed"         # Zakonczony bledem
    CANCELLED = "cancelled"   # Anulowany


@dataclass
class StrategyExperiment:
    """
    Niezmienialny rekord eksperymentu strategii.
    
    Encja gotowa do przyszlego zapisu w Strategy Memory.
    Zasada: powinna byc samowystarczalna i zawierac wszystkie dane
    potrzebne do odtworzenia eksperymentu.
    """

    # ===== WYMAGANE POLA (bez domyslnych) =====
    strategy_id: str
    world_version: str

    # ===== OPCJONALNE POLA Z DOMYSLNYMI =====
    experiment_id: str = field(default_factory=lambda: f"exp_{uuid.uuid4().hex[:8]}")
    lab_session_id: str = "default_session"
    strategy_version: str = "1.0.0"
    strategy_parameters: Dict[str, Any] = field(default_factory=dict)
    dataset_version: str = "default"
    model_reference: str = "default"
    features: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    result: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    status: ExperimentStatus = ExperimentStatus.PENDING
    execution_context: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ===== METODY =====
    def mark_completed(self, result: Dict[str, Any], metrics: Dict[str, float]) -> None:
        """Zaznacz eksperyment jako ukonczyli"""
        self.result = result
        self.metrics = metrics
        self.status = ExperimentStatus.COMPLETED
        self.end_time = datetime.now()

    def mark_failed(self, error: str) -> None:
        """Zaznacz eksperyment jako nieudany"""
        self.error = error
        self.status = ExperimentStatus.FAILED
        self.end_time = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika"""
        return {
            'experiment_id': self.experiment_id,
            'lab_session_id': self.lab_session_id,
            'strategy_id': self.strategy_id,
            'strategy_version': self.strategy_version,
            'strategy_parameters': copy.deepcopy(self.strategy_parameters),
            'world_version': self.world_version,
            'dataset_version': self.dataset_version,
            'model_reference': self.model_reference,
            'features': copy.deepcopy(self.features),
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'result': copy.deepcopy(self.result),
            'metrics': copy.deepcopy(self.metrics),
            'status': self.status.value,
            'execution_context': copy.deepcopy(self.execution_context),
            'error': self.error,
            'metadata': copy.deepcopy(self.metadata)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StrategyExperiment':
        """Tworzenie z slownika"""
        return cls(
            experiment_id=data.get('experiment_id', f"exp_{uuid.uuid4().hex[:8]}"),
            lab_session_id=data.get('lab_session_id', 'default_session'),
            strategy_id=data['strategy_id'],
            strategy_version=data.get('strategy_version', '1.0.0'),
            strategy_parameters=copy.deepcopy(data.get('strategy_parameters', {})),
            world_version=data['world_version'],
            dataset_version=data.get('dataset_version', 'default'),
            model_reference=data.get('model_reference', 'default'),
            features=copy.deepcopy(data.get('features', [])),
            start_time=datetime.fromisoformat(data['start_time']) if data.get('start_time') else datetime.now(),
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            result=copy.deepcopy(data.get('result', {})),
            metrics=copy.deepcopy(data.get('metrics', {})),
            status=ExperimentStatus(data.get('status', 'pending')),
            execution_context=copy.deepcopy(data.get('execution_context', {})),
            error=data.get('error'),
            metadata=copy.deepcopy(data.get('metadata', {}))
        )


class StrategyLab:
    """
    Strategy Laboratory - izolowane srodowisko testowe dla strategii.

    ZASADY:
    1. NIE MODYFIKUJE PRODUKCJI
       - Nie zmienia aktywnych modeli
       - Nie zmienia produkcyjnych strategii
       - Nie zmienia reputacji agentow
    2. Korzysta z kopii danych (nie oryginalow)
    3. Wyniki sa niezalezne od systemu produkcyjnego
    
    Integracje:
    - WorldEngine (tylko odczyt WorldSnapshot)
    - StrategyManager (tylko odczyt strategii)
    
    NIE INTEGRUJE Z:
    - MemoryManager
    - CollectiveManager  
    - Pipeline
    - TrustManager
    """

    # Domy Slne ustawienia
    DEFAULT_HISTORY_DIR = "history"
    DEFAULT_EXPERIMENTS_FILE = "strategy_lab_history.json"

    def __init__(
        self,
        lab_name: str = "SSI_V5_STRATEGY_LAB",
        history_dir: Optional[str] = None,
        execution_engine: Optional[Callable] = None
    ):
        """
        Inicjalizacja laboratorium.

        :param lab_name: Nazwa laboratorium
        :param history_dir: Katalog historii (domyslnie: laboratory/history)
        :param execution_engine: Funkcja wykonujaca eksperyment (placeholder)
        """
        self.lab_name = lab_name
        self.experiments: Dict[str, StrategyExperiment] = {}
        self.sessions: Dict[str, List[StrategyExperiment]] = {}
        self._lock = RLock()

        # Konfiguracja katalogow
        if history_dir is None:
            base_path = Path(__file__).parent
            self.history_dir = Path(base_path) / self.DEFAULT_HISTORY_DIR
        else:
            self.history_dir = Path(history_dir)

        self.history_file = self.history_dir / self.DEFAULT_EXPERIMENTS_FILE

        # Utworz katalogi
        self.history_dir.mkdir(parents=True, exist_ok=True)

        # Placeholder dla silnika wykonawczego
        # (na tym etapie nie implementujemy logiki, tylko interfejs)
        self.execution_engine = execution_engine or self._default_execution_engine

        # Wczytanie historii
        self._load_history()

    def _default_execution_engine(
        self,
        strategy_id: str,
        strategy_parameters: Dict[str, Any],
        world_snapshot: Dict[str, Any],
        dataset: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Domy Slny placeholder dla silnika wykonawczego.
        Zwraca symulowane wyniki (do przyszlej implementacji).

        :return: Symulowany wynik eksperymentu
        """
        # TODO: W przyszlosci tutaj bedzie realna logika
        # Na razie symulujemy wynik
        import random
        random.seed(42)  # Powtarzalne wyniki
        
        decision_count = len(world_snapshot.get("matches", []))
        simulated_accuracy = round(random.uniform(0.6, 0.95), 4)
        simulated_roi = round(random.uniform(0.8, 1.5), 4)
        
        return {
            "status": "simulated",
            "decision_count": decision_count,
            "simulated_accuracy": simulated_accuracy,
            "simulated_roi": simulated_roi,
            "risk_score": round(random.uniform(0.1, 0.8), 4),
            "stability_score": round(random.uniform(0.5, 1.0), 4),
            "message": "Placeholder execution - real implementation in next phase"
        }

    def run_experiment(
        self,
        strategy_id: str,
        world_snapshot: Dict[str, Any],
        strategy_version: str = "1.0.0",
        dataset: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        model_reference: str = "default",
        features: Optional[List[str]] = None,
        execution_context: Optional[Dict[str, Any]] = None,
        lab_session_id: Optional[str] = None
    ) -> StrategyExperiment:
        """
        Uruchom pojedynczy eksperyment strategii.

        :param strategy_id: ID testowanej strategii
        :param strategy_version: Wersja strategii
        :param world_snapshot: Zrzut swiata (tylko do odczytu, kopia!)
        :param dataset: Dataset testowy
        :param parameters: Parametry eksperymentu
        :param model_reference: Referencja do modelu
        :param features: Lista uzywanych feature'y
        :param execution_context: Kontekst wykonania
        :param lab_session_id: ID sesji (grupa eksperymentow)
        :return: StrategyExperiment (gotowy obiekt)
        """
        with self._lock:
            # Utworz nowy eksperyment
            experiment = StrategyExperiment(
                strategy_id=strategy_id,
                strategy_version=strategy_version,
                world_version=world_snapshot.get("version", "unknown"),
                dataset_version=dataset.get("version", "default") if dataset else "none",
                model_reference=model_reference,
                strategy_parameters=copy.deepcopy(parameters) or {},
                features=features or [],
                execution_context=execution_context or {
                    "engine": "SSI_V5",
                    "environment": "laboratory",
                    "execution_mode": "simulation"
                },
                lab_session_id=lab_session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            # Zaznacz jako uruchomiony
            experiment.status = ExperimentStatus.RUNNING

            # Zapisz tymczasowo
            self.experiments[experiment.experiment_id] = experiment

            # Dodaj do sesji
            if experiment.lab_session_id not in self.sessions:
                self.sessions[experiment.lab_session_id] = []
            self.sessions[experiment.lab_session_id].append(experiment)

        # ===== WYKONANIE EKSPERYMENTU (IZOLOWANE) =====
        try:
            # Wywolaj silnik wykonawczy (placeholder)
            # UWAGA: Nie modyfikuje world_snapshot, parameters, itp.
            result = self.execution_engine(
                strategy_id=strategy_id,
                strategy_parameters=experiment.strategy_parameters,
                world_snapshot=copy.deepcopy(world_snapshot),  # Kopia!
                dataset=copy.deepcopy(dataset) if dataset else None
            )

            # Zaktualizuj eksperyment
            experiment.mark_completed(result=result, metrics=self._extract_metrics(result))

        except Exception as e:
            experiment.mark_failed(error=str(e))

        # Zapisz do historii
        self.save_experiment(experiment)

        return experiment

    def run_experiment_batch(
        self,
        strategy_variants: List[Dict[str, Any]],
        world_snapshot: Dict[str, Any],
        dataset: Optional[Dict[str, Any]] = None,
        lab_session_id: Optional[str] = None
    ) -> List[StrategyExperiment]:
        """
        Uruchom serie eksperymentow (porownanie wariantow).

        :param strategy_variants: Lista wariantow {strategy_id, strategy_version, parameters}
        :param world_snapshot: Zrzut swiata
        :param dataset: Dataset testowy
        :param lab_session_id: ID sesji
        :return: Lista eksperymentow
        """
        experiments = []
        session_id = lab_session_id or f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        for variant in strategy_variants:
            experiment = self.run_experiment(
                strategy_id=variant.get("strategy_id", "unknown"),
                strategy_version=variant.get("strategy_version", "1.0.0"),
                world_snapshot=world_snapshot,
                dataset=dataset,
                parameters=variant.get("parameters", {}),
                lab_session_id=session_id
            )
            experiments.append(experiment)

        return experiments

    def compare_variants(
        self,
        experiments: List[StrategyExperiment],
        metric: str = "simulated_accuracy",
        sort_descending: bool = True
    ) -> Dict[str, Any]:
        """
        Porownaj wyniki eksperymentow wg podanej metryki.

        :param experiments: Lista eksperymentow do porownania
        :param metric: Metryka do porownania (domyslnie: simulated_accuracy)
        :param sort_descending: Sortowanie malejace (domyslnie: True)
        :return: Ranking + statystyki
        """
        if not experiments:
            return {"error": "No experiments to compare"}

        # Filtrowanie ukonc quedando eksperymentow
        completed_experiments = [
            exp for exp in experiments
            if exp.status == ExperimentStatus.COMPLETED
        ]

        if not completed_experiments:
            return {"error": "No completed experiments to compare"}

        # Sortowanie po metryce
        sorted_experiments = sorted(
            completed_experiments,
            key=lambda x: x.metrics.get(metric, 0),
            reverse=sort_descending
        )

        # Tworzenie rankingu
        ranking = []
        for i, exp in enumerate(sorted_experiments, 1):
            ranking.append({
                "rank": i,
                "experiment_id": exp.experiment_id,
                "strategy_id": exp.strategy_id,
                "strategy_version": exp.strategy_version,
                "metric_value": exp.metrics.get(metric, 0),
                "all_metrics": exp.metrics
            })

        # Statystyki
        metric_values = [exp.metrics.get(metric, 0) for exp in completed_experiments]
        stats = {
            "count": len(completed_experiments),
            "mean": sum(metric_values) / len(metric_values) if metric_values else 0,
            "min": min(metric_values) if metric_values else 0,
            "max": max(metric_values) if metric_values else 0,
            "best_experiment_id": ranking[0]["experiment_id"] if ranking else None
        }

        return {
            "ranking": ranking,
            "statistics": stats,
            "metric": metric,
            "timestamp": datetime.now().isoformat()
        }

    def evaluate_quality(
        self,
        experiment: StrategyExperiment
    ) -> Dict[str, Any]:
        """
        Ocena jakości eksperymentu.

        :param experiment: Eksperyment do oceny
        :return: Rozszerzone metryki + ocena jakościowa
        """
        if experiment.status != ExperimentStatus.COMPLETED:
            return {"error": "Experiment not completed", "status": experiment.status.value}

        # Pobierz metryki
        accuracy = experiment.metrics.get("simulated_accuracy", 0)
        roi = experiment.metrics.get("simulated_roi", 0)
        risk = experiment.metrics.get("risk_score", 0.5)
        stability = experiment.metrics.get("stability_score", 0.5)
        decision_count = experiment.result.get("decision_count", 0)

        # Ocena jakości (waga: accuracy 40%, roi 30%, stability 20%, low risk 10%)
        roi_contribution = ((roi - 1) * 0.3) if roi > 1 else (roi * 0.3)
        quality_score = (
            accuracy * 0.4 +
            roi_contribution +
            stability * 0.2 +
            (1 - risk) * 0.1
        )

        if quality_score >= 0.8:
            quality_rating = "EXCELLENT"
        elif quality_score >= 0.6:
            quality_rating = "GOOD"
        elif quality_score >= 0.4:
            quality_rating = "FAIR"
        else:
            quality_rating = "POOR"

        return {
            "experiment_id": experiment.experiment_id,
            "quality_score": round(quality_score, 4),
            "quality_rating": quality_rating,
            "details": {
                "accuracy": round(accuracy, 4),
                "accuracy_contribution": round(accuracy * 0.4, 4),
                "roi": round(roi, 4),
                "roi_contribution": round(((roi - 1) * 0.3) if roi > 1 else (roi * 0.3), 4),
                "stability": round(stability, 4),
                "stability_contribution": round(stability * 0.2, 4),
                "risk": round(risk, 4),
                "risk_contribution": round((1 - risk) * 0.1, 4),
                "decision_count": decision_count
            },
            "recommendation": (
                "ACCEPT" if quality_rating in ["EXCELLENT", "GOOD"]
                else "REJECT"
            ),
            "timestamp": datetime.now().isoformat()
        }

    def save_experiment(self, experiment: StrategyExperiment) -> bool:
        """
        Zapisz eksperyment do HISTORII LABORATORIUM.
        NIE zapisuje do Strategy Memory (to przyszly etap)!

        :param experiment: Eksperyment do zapisu
        :return: Czy zapis sie powiodl
        """
        with self._lock:
            # Aktualizuj w pamienci
            self.experiments[experiment.experiment_id] = experiment

            # Zapisz histone na dysk
            return self._save_history()

    def get_experiment(self, experiment_id: str) -> Optional[StrategyExperiment]:
        """Pobierz eksperyment po ID"""
        with self._lock:
            return copy.deepcopy(self.experiments.get(experiment_id))

    def get_session_experiments(self, session_id: str) -> List[StrategyExperiment]:
        """Pobierz wszystkie eksperymenty z sesji"""
        with self._lock:
            return copy.deepcopy(self.sessions.get(session_id, []))

    def get_lab_history(self) -> List[StrategyExperiment]:
        """Pobierz pelna historie laboratorium"""
        with self._lock:
            return copy.deepcopy(list(self.experiments.values()))

    def clear_lab_history(self) -> None:
        """Wyczysc 궁historie (tylko dla celow testowych!)"""
        with self._lock:
            self.experiments.clear()
            self.sessions.clear()

    def _extract_metrics(self, result: Dict[str, Any]) -> Dict[str, float]:
        """Wydobywanie metryk z wyniku"""
        metrics = {}
        for key, value in result.items():
            if isinstance(value, (int, float)):
                # Normalizuj nazwe (usun "simulated_" dla metryk)
                clean_key = key.replace("simulated_", "")
                metrics[clean_key] = float(value)
                # Zachowaj oryginalna nazwe dla wstecznej kompatybilnosci
                metrics[key] = float(value)
        return metrics

    def _load_history(self) -> None:
        """Wczytanie historii z pliku"""
        if not self.history_file.exists():
            return

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

                for exp_data in data.get("experiments", []):
                    experiment = StrategyExperiment.from_dict(exp_data)
                    self.experiments[experiment.experiment_id] = experiment

                    # Dodaj do sesji
                    if experiment.lab_session_id not in self.sessions:
                        self.sessions[experiment.lab_session_id] = []
                    self.sessions[experiment.lab_session_id].append(experiment)

        except Exception as e:
            print(f"[LAB] Warning: Error loading history: {e}")

    def _save_history(self) -> bool:
        """Zapis historii do pliku"""
        try:
            data = {
                "lab_name": self.lab_name,
                "timestamp": datetime.now().isoformat(),
                "experiments": [exp.to_dict() for exp in self.experiments.values()]
            }

            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False, default=str)

            return True

        except Exception as e:
            print(f"[LAB] Error saving history: {e}")
            return False

    def __repr__(self) -> str:
        return (f"StrategyLab(name='{self.lab_name}', "
                f"experiments={len(self.experiments)}, "
                f"sessions={len(self.sessions)}))")
