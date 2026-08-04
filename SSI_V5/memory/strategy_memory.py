# SSI V5 Memory Module - Strategy Memory Foundation
# ====================================================
#
# ETAP: 5.2.6.2 - Strategy Memory Foundation
# Data: 2026-08-04
#
# Odpowiedzialnosc:
# - Przechowywanie historii i ewolucji strategii
# - Powiazanie z Strategy Laboratory
# - Zapis i odczyt doświadczeń strategii
# - Wersjonowanie strategii
#
# ZASADY:
# 1. Strategy Laboratory tworzy doświadczenia
# 2. Strategy Memory przechowuje historię i ewolucję tych doświadczeń
# 3. NIE wpływa na aktywne strategie wykorzystywane w systemie
# 4. NIE modyfikuje TrustManager, AgentRuntime, Pipeline, CollectiveManager, WorldEngine
# 5. Tylko zapisuje doświadczenie - nie podejmuje decyzji
#
# Archived by Mistral Vibe.
# Co-Authored-By: Mistral Vibe <vibe@mistral.ai>

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json
import os
import uuid
from pathlib import Path
import copy
from threading import RLock


@dataclass
class StrategyMemoryRecord:
    """
    Rekord pamięci strategii.
    
    Przechowuje kompletna historię i ewolucję pojedynczej strategii.
    
    ZASADA: Powinien być samowystarczalny i zawierać wszystkie dane
    potrzebne do odtworzenia historii strategii.
    
    Attributes:
        memory_id: Unikalne ID rekord pamięci
        strategy_id: Identyfikator strategii
        strategy_version: Wersja strategii
        strategy_definition: Definicja strategii (struktura, typ, cel)
        strategy_parameters: Parametry strategii
        feature_schema: Schemat cech używanych przez strategię
        model_reference: Referencja do modelu/algorytmu
        creation_time: Czas utworzenia rekord
        last_updated: Ostatnia aktualizacja
        EXPERIMENT_HISTORY: Historia eksperymentów miejsce dla StrategyExperiment
        PREDICTION_HISTORY: Placeholder dla Prediction Trace Engine
        RESULT_HISTORY: Placeholder dla wyników
        REPUTATION_HISTORY: Placeholder dla reputacji strategii
        EVOLUTION_HISTORY: Placeholder dla ewolucji strategii
    """
    
    # ===== IDENTYFIKACJA =====
    memory_id: str = field(default_factory=lambda: f"smr_{uuid.uuid4().hex[:12]}")
    strategy_id: str = ""
    strategy_version: str = "1.0.0"
    
    # ===== DEFINICJA STRATEGII =====
    strategy_definition: Dict[str, Any] = field(default_factory=dict)
    strategy_parameters: Dict[str, Any] = field(default_factory=dict)
    feature_schema: List[str] = field(default_factory=list)
    model_reference: str = "default"
    
    # ===== METADANE =====
    creation_time: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # ===== HISTORIA EKSPERYMENTOW =====
    # Główna historia - na podstawie StrategyExperiment z StrategyLab
    EXPERIMENT_HISTORY: List[Dict[str, Any]] = field(default_factory=list)
    
    # ===== PLACEHOLDERY DLA PRZYSZŁYCH FUNKCJI =====
    # (Nie implementujemy logiki, tylko przygotowujemy strukturę)
    PREDICTION_HISTORY: List[Dict[str, Any]] = field(default_factory=list)
    RESULT_HISTORY: List[Dict[str, Any]] = field(default_factory=list)
    REPUTATION_HISTORY: List[Dict[str, Any]] = field(default_factory=list)
    EVOLUTION_HISTORY: List[Dict[str, Any]] = field(default_factory=list)
    
    # ===== METODY =====
    
    def add_experiment(self, experiment_data: Dict[str, Any]) -> None:
        """
        Dodaj eksperyment do historii.
        
        Args:
            experiment_data: Dane eksperymentu (z StrategyExperiment.to_dict())
        """
        # Ustaw timestamp jeśli nie istnieje
        if "timestamp" not in experiment_data:
            experiment_data["timestamp"] = datetime.now().isoformat()
        
        self.EXPERIMENT_HISTORY.append(copy.deepcopy(experiment_data))
        self.last_updated = datetime.now()
    
    def add_experiment_from_strategy_experiment(self, strategy_experiment: Any) -> None:
        """
        Dodaj eksperyment z StrategyExperiment (z StrategyLab).
        
        Args:
            strategy_experiment: Instancja StrategyExperiment
        """
        if hasattr(strategy_experiment, 'to_dict'):
            experiment_data = strategy_experiment.to_dict()
        else:
            # Fallback: konwersja manualna
            experiment_data = {
                'experiment_id': getattr(strategy_experiment, 'experiment_id', ''),
                'strategy_id': getattr(strategy_experiment, 'strategy_id', ''),
                'strategy_version': getattr(strategy_experiment, 'strategy_version', ''),
                'world_version': getattr(strategy_experiment, 'world_version', ''),
                'dataset_version': getattr(strategy_experiment, 'dataset_version', ''),
                'model_reference': getattr(strategy_experiment, 'model_reference', ''),
                'features': getattr(strategy_experiment, 'features', []),
                'start_time': getattr(strategy_experiment, 'start_time', None),
                'end_time': getattr(strategy_experiment, 'end_time', None),
                'result': getattr(strategy_experiment, 'result', {}),
                'metrics': getattr(strategy_experiment, 'metrics', {}),
                'status': getattr(strategy_experiment, 'status', None),
                'strategy_parameters': getattr(strategy_experiment, 'strategy_parameters', {}),
                'execution_context': getattr(strategy_experiment, 'execution_context', {}),
                'error': getattr(strategy_experiment, 'error', None),
                'metadata': getattr(strategy_experiment, 'metadata', {}),
            }
            # Konwersja datetime do string
            for time_field in ['start_time', 'end_time']:
                if hasattr(experiment_data[time_field], 'isoformat') and experiment_data[time_field]:
                    experiment_data[time_field] = experiment_data[time_field].isoformat()
        
        self.add_experiment(experiment_data)
    
    def update_version(self, new_version: str, change_description: str = "") -> None:
        """
        Zaktualizuj wersję strategii i zarejestruj zmianę w ewolucji.
        
        Args:
            new_version: Nowa wersja strategii
            change_description: Opis zmian
        """
        # Zapisz starą wersję w historii ewolucji
        evolution_record = {
            "timestamp": datetime.now().isoformat(),
            "old_version": self.strategy_version,
            "new_version": new_version,
            "change_description": change_description,
            "strategy_id": self.strategy_id
        }
        self.EVOLUTION_HISTORY.append(evolution_record)
        
        self.strategy_version = new_version
        self.last_updated = datetime.now()
    
    def get_experiment_count(self) -> int:
        """Pobierz liczbę eksperymentów."""
        return len(self.EXPERIMENT_HISTORY)
    
    def get_latest_experiment(self) -> Optional[Dict[str, Any]]:
        """Pobierz ostatni eksperyment."""
        if self.EXPERIMENT_HISTORY:
            return self.EXPERIMENT_HISTORY[-1]
        return None
    
    def get_experiments_by_world_version(self, world_version: str) -> List[Dict[str, Any]]:
        """Pobierz eksperymenty dla konkretnej wersji świata."""
        return [
            exp for exp in self.EXPERIMENT_HISTORY
            if exp.get("world_version") == world_version
        ]
    
    def get_experiments_by_dataset_version(self, dataset_version: str) -> List[Dict[str, Any]]:
        """Pobierz eksperymenty dla konkretnej wersji datasetu."""
        return [
            exp for exp in self.EXPERIMENT_HISTORY
            if exp.get("dataset_version") == dataset_version
        ]
    
    def get_best_experiment(self, metric_key: str = "accuracy") -> Optional[Dict[str, Any]]:
        """
        Pobierz najlepszy eksperyment według podanego metryki.
        
        Args:
            metric_key: Klucz metryki do porównania (domyślnie 'accuracy')
            
        Returns:
            Najlepszy eksperyment lub None
        """
        if not self.EXPERIMENT_HISTORY:
            return None
        
        # Filtrowanie eksperymentów z podaną metryką
        experiments_with_metric = [
            exp for exp in self.EXPERIMENT_HISTORY
            if metric_key in exp.get("metrics", {})
        ]
        
        if not experiments_with_metric:
            return None
        
        # Znajdź eksperyment z najlepszą wartością metryki
        best_exp = max(
            experiments_with_metric,
            key=lambda x: x["metrics"][metric_key]
        )
        return best_exp
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do słownika."""
        result = {
            'memory_id': self.memory_id,
            'strategy_id': self.strategy_id,
            'strategy_version': self.strategy_version,
            'strategy_definition': copy.deepcopy(self.strategy_definition),
            'strategy_parameters': copy.deepcopy(self.strategy_parameters),
            'feature_schema': copy.deepcopy(self.feature_schema),
            'model_reference': self.model_reference,
            'creation_time': self.creation_time.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'metadata': copy.deepcopy(self.metadata),
            'EXPERIMENT_HISTORY': copy.deepcopy(self.EXPERIMENT_HISTORY),
            'PREDICTION_HISTORY': copy.deepcopy(self.PREDICTION_HISTORY),
            'RESULT_HISTORY': copy.deepcopy(self.RESULT_HISTORY),
            'REPUTATION_HISTORY': copy.deepcopy(self.REPUTATION_HISTORY),
            'EVOLUTION_HISTORY': copy.deepcopy(self.EVOLUTION_HISTORY),
        }
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StrategyMemoryRecord':
        """Utworzenie z słownika."""
        # Konwersja pól datetime
        creation_time = data.get('creation_time')
        last_updated = data.get('last_updated')
        
        if isinstance(creation_time, str):
            creation_time = datetime.fromisoformat(creation_time)
        if isinstance(last_updated, str):
            last_updated = datetime.fromisoformat(last_updated)
        
        return cls(
            memory_id=data.get('memory_id', f"smr_{uuid.uuid4().hex[:12]}"),
            strategy_id=data.get('strategy_id', ''),
            strategy_version=data.get('strategy_version', '1.0.0'),
            strategy_definition=data.get('strategy_definition', {}),
            strategy_parameters=data.get('strategy_parameters', {}),
            feature_schema=data.get('feature_schema', []),
            model_reference=data.get('model_reference', 'default'),
            creation_time=creation_time or datetime.now(),
            last_updated=last_updated or datetime.now(),
            metadata=data.get('metadata', {}),
            EXPERIMENT_HISTORY=data.get('EXPERIMENT_HISTORY', []),
            PREDICTION_HISTORY=data.get('PREDICTION_HISTORY', []),
            RESULT_HISTORY=data.get('RESULT_HISTORY', []),
            REPUTATION_HISTORY=data.get('REPUTATION_HISTORY', []),
            EVOLUTION_HISTORY=data.get('EVOLUTION_HISTORY', []),
        )
    
    def to_json(self, indent: int = 4) -> str:
        """Konwersja do JSON."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'StrategyMemoryRecord':
        """Utworzenie z JSON."""
        data = json.loads(json_str)
        return cls.from_dict(data)


class StrategyMemoryManager:
    """
    Menadżer pamięci strategii.
    
    Odpowiedzialny za:
    - Tworzenie i zarządzanie StrategyMemoryRecord
    - Zapis eksperymentów z StrategyLab
    - Pobieranie historii strategii
    - Wersjonowanie strategii
    - Zapis i odczyt JSON
    
    ZASADA: Tylko zapisuje doświadczenie. Nie wpływa na aktywną strategię.
    """
    
    def __init__(self, memory_dir: str = None, strategy_id: str = None):
        """
        Inicjalizacja StrategyMemoryManager.
        
        Args:
            memory_dir: Katalog do zapisywania pamięci strategii
            strategy_id: Domyślne ID strategii (opcjonalne)
        """
        if memory_dir is None:
            from ..core.config import PathConfig
            memory_dir = PathConfig.MEMORY_DIR
        
        self.memory_dir = Path(memory_dir)
        self.strategy_id = strategy_id
        
        # Utwórz katalog pamięci strategii
        self.strategy_memory_dir = self.memory_dir / "strategy_memory"
        os.makedirs(self.strategy_memory_dir, exist_ok=True)
        
        # Rejestr aktywnych pamięci strategii (w pamięci)
        self._memory_register: Dict[str, StrategyMemoryRecord] = {}
        
        # Blokada dla thread-safety
        self._lock = RLock()
        
        # Wczytanie istniejącej pamięci
        self._load_existing_memory()
    
    def _load_existing_memory(self) -> None:
        """Wczytanie istniejącej pamięci z dysku."""
        if not self.strategy_memory_dir.exists():
            return
        
        for memory_file in self.strategy_memory_dir.glob("*.json"):
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                record = StrategyMemoryRecord.from_dict(data)
                self._memory_register[record.memory_id] = record
                
            except Exception as e:
                print(f"[STRATEGY MEMORY] Warning: Error loading {memory_file}: {e}")
    
    def _get_memory_file_path(self, memory_id: str) -> Path:
        """Pobierz ścieżkę pliku pamięci."""
        return self.strategy_memory_dir / f"{memory_id}.json"
    
    def create_strategy_memory(
        self,
        strategy_id: str,
        strategy_definition: Dict[str, Any] = None,
        strategy_parameters: Dict[str, Any] = None,
        feature_schema: List[str] = None,
        model_reference: str = "default",
        version: str = "1.0.0",
        metadata: Dict[str, Any] = None
    ) -> StrategyMemoryRecord:
        """
        Utwórz nową pamięć strategii.
        
        Args:
            strategy_id: Identyfikator strategii
            strategy_definition: Definicja strategii (opcjonalnie)
            strategy_parameters: Parametry strategii (opcjonalnie)
            feature_schema: Schemat cech (opcjonalnie)
            model_reference: Referencja do modelu (opcjonalnie)
            version: Wersja strategii (domyślnie 1.0.0)
            metadata: Metadane (opcjonalnie)
            
        Returns:
            StrategyMemoryRecord: Nowy rekord pamięci
        """
        with self._lock:
            record = StrategyMemoryRecord(
                strategy_id=strategy_id,
                strategy_version=version,
                strategy_definition=strategy_definition or {},
                strategy_parameters=strategy_parameters or {},
                feature_schema=feature_schema or [],
                model_reference=model_reference,
                metadata=metadata or {}
            )
            
            # Zapis do rejestru
            self._memory_register[record.memory_id] = record
            
            # Zapis na dysk
            self._save_record(record)
            
            return record
    
    def _save_record(self, record: StrategyMemoryRecord) -> bool:
        """Zapisz pojedynczy rekord na dysk."""
        try:
            file_path = self._get_memory_file_path(record.memory_id)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(record.to_dict(), f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[STRATEGY MEMORY] Error saving record {record.memory_id}: {e}")
            return False
    
    def save_experiment(
        self,
        strategy_experiment: Any,
        strategy_id: str = None,
        create_if_not_exists: bool = True
    ) -> Optional[StrategyMemoryRecord]:
        """
        Zapisz eksperyment z StrategyLab do pamięci strategii.
        
        Args:
            strategy_experiment: Instancja StrategyExperiment
            strategy_id: ID strategii (jeśli nie ma w eksperymencie)
            create_if_not_exists: Utwórz nową pamięć jeśli nie istnieje
            
        Returns:
            StrategyMemoryRecord: Zaktualizowany rekord lub None
        """
        # Pobierz strategy_id z eksperymentu
        exp_strategy_id = getattr(strategy_experiment, 'strategy_id', strategy_id or self.strategy_id)
        
        if not exp_strategy_id:
            print("[STRATEGY MEMORY] Warning: Cannot save experiment without strategy_id")
            return None
        
        with self._lock:
            # Znajdź lub utwórz rekord pamięci
            record = self.get_strategy_memory(exp_strategy_id)
            
            if record is None:
                if not create_if_not_exists:
                    print(f"[STRATEGY MEMORY] Warning: No memory record for strategy {exp_strategy_id}")
                    return None
                
                # Utwórz nowy rekord
                record = self.create_strategy_memory(
                    strategy_id=exp_strategy_id,
                    strategy_parameters=getattr(strategy_experiment, 'strategy_parameters', {}),
                    feature_schema=getattr(strategy_experiment, 'features', []),
                    model_reference=getattr(strategy_experiment, 'model_reference', 'default'),
                    version=getattr(strategy_experiment, 'strategy_version', '1.0.0')
                )
            
            # Dodaj eksperyment do historii
            record.add_experiment_from_strategy_experiment(strategy_experiment)
            
            # Zapis na dysk
            self._save_record(record)
            
            return record
    
    def get_strategy_memory(self, strategy_id: str) -> Optional[StrategyMemoryRecord]:
        """
        Pobierz pamięć strategii po ID strategii.
        
        Args:
            strategy_id: ID strategii
            
        Returns:
            StrategyMemoryRecord lub None
        """
        # Szukaj po strategy_id lub memory_id
        for record in self._memory_register.values():
            if record.strategy_id == strategy_id:
                return record
            if record.memory_id == strategy_id:
                return record
        return None
    
    def get_strategy_memory_by_id(self, memory_id: str) -> Optional[StrategyMemoryRecord]:
        """
        Pobierz pamięć strategii po memory_id.
        
        Args:
            memory_id: ID pamięci strategii
            
        Returns:
            StrategyMemoryRecord lub None
        """
        return self._memory_register.get(memory_id)
    
    def get_all_strategy_memories(self) -> List[StrategyMemoryRecord]:
        """Pobierz wszystkie pamięci strategii."""
        return list(self._memory_register.values())
    
    def get_strategy_memories_by_id(self, strategy_id: str) -> List[StrategyMemoryRecord]:
        """Pobierz wszystkie pamięci dla danej strategii (wszystkie wersje)."""
        return [
            record for record in self._memory_register.values()
            if record.strategy_id == strategy_id
        ]
    
    def update_strategy_version(
        self,
        strategy_id: str,
        new_version: str,
        change_description: str = ""
    ) -> bool:
        """
        Zaktualizuj wersję strategii.
        
        Args:
            strategy_id: ID strategii
            new_version: Nowa wersja
            change_description: Opis zmian
            
        Returns:
            bool: Czy aktualizacja się powiodła
        """
        record = self.get_strategy_memory(strategy_id)
        if record is None:
            return False
        
        with self._lock:
            record.update_version(new_version, change_description)
            self._save_record(record)
            return True
    
    def save_to_json(self, file_path: str = None) -> bool:
        """
        Zapisz całą pamięć strategii do jednego pliku JSON.
        
        Args:
            file_path: Ścieżka pliku (domyślnie strategy_memory_collection.json)
            
        Returns:
            bool: Czy zapis się powiódł
        """
        if file_path is None:
            file_path = str(self.strategy_memory_dir / "strategy_memory_collection.json")
        
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'total_records': len(self._memory_register),
                'strategy_memories': [
                    record.to_dict() for record in self._memory_register.values()
                ]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"[STRATEGY MEMORY] Error saving collection to {file_path}: {e}")
            return False
    
    def load_from_json(self, file_path: str = None) -> bool:
        """
        Wczytanie pamięci strategii z pliku JSON.
        
        Args:
            file_path: Ścieżka pliku (domyślnie strategy_memory_collection.json)
            
        Returns:
            bool: Czy wczytanie się powiodło
        """
        if file_path is None:
            file_path = str(self.strategy_memory_dir / "strategy_memory_collection.json")
        
        if not os.path.exists(file_path):
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with self._lock:
                for record_data in data.get('strategy_memories', []):
                    record = StrategyMemoryRecord.from_dict(record_data)
                    self._memory_register[record.memory_id] = record
                    
            return True
        except Exception as e:
            print(f"[STRATEGY MEMORY] Error loading collection from {file_path}: {e}")
            return False
    
    def clear_strategy_memory(self, strategy_id: str) -> bool:
        """
        Wyczyść pamięć strategii.
        
        Args:
            strategy_id: ID strategii lub memory_id
            
        Returns:
            bool: Czy czyszczenie się powiodło
        """
        record = self.get_strategy_memory(strategy_id)
        if record is None:
            record = self.get_strategy_memory_by_id(strategy_id)
            if record is None:
                return False
        
        with self._lock:
            del self._memory_register[record.memory_id]
            
            # Wyczyść plik
            file_path = self._get_memory_file_path(record.memory_id)
            if file_path.exists():
                file_path.unlink()
            
            return True
    
    def clear_all_memory(self) -> bool:
        """Wyczyść całą pamięć strategii."""
        with self._lock:
            self._memory_register.clear()
            
            # Wyczyść pliki
            for memory_file in self.strategy_memory_dir.glob("*.json"):
                memory_file.unlink()
            
            return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Pobierz statystyki pamięci strategii.
        
        Returns:
            Dict: Statystyki
        """
        total_records = len(self._memory_register)
        total_experiments = sum(
            len(record.EXPERIMENT_HISTORY) 
            for record in self._memory_register.values()
        )
        
        strategies = {}
        for record in self._memory_register.values():
            if record.strategy_id not in strategies:
                strategies[record.strategy_id] = {
                    'versions': [],
                    'experiment_count': 0
                }
            
            strategies[record.strategy_id]['versions'].append(record.strategy_version)
            strategies[record.strategy_id]['experiment_count'] += len(record.EXPERIMENT_HISTORY)
        
        return {
            'total_records': total_records,
            'total_experiments': total_experiments,
            'strategies': strategies,
            'memory_ids': list(self._memory_register.keys())
        }
    
    # ========================================================================
    # INTEGRACJA Z STRATEGYLAB
    # ========================================================================
    
    def connect_to_strategy_lab(self, strategy_lab: Any) -> None:
        """
        Połącz z StrategyLab.
        
        Dodaje metodę save_to_strategy_memory do StrategyLab.
        
        Args:
            strategy_lab: Instancja StrategyLab
        """
        # Ustaw referencję do StrategyMemoryManager w StrategyLab
        strategy_lab._strategy_memory_manager = self
        
        # Dodaj metodę save_to_strategy_memory do StrategyLab
        def save_to_strategy_memory_func(experiment: Any = None, experiment_id: str = None) -> Optional[StrategyMemoryRecord]:
            """Zapisz eksperyment do pamięci strategii."""
            if experiment is None and experiment_id:
                # Pobierz eksperyment z laboratorium
                experiment = strategy_lab.get_experiment(experiment_id)
            
            if experiment is None:
                print(f"[STRATEGY MEMORY] Warning: No experiment to save (id: {experiment_id})")
                return None
            
            return self.save_experiment(experiment)
        
        # Przypisz metodę do StrategyLab
        strategy_lab.save_to_strategy_memory = save_to_strategy_memory_func
        
        # Also provide direct access to the manager
        strategy_lab.strategy_memory_manager = self
    
    # ========================================================================
    # METODY UTYLITY (dla testów i debugowania)
    # ========================================================================
    
    def list_all_memories(self) -> List[str]:
        """Lista wszystkich memory_id."""
        return list(self._memory_register.keys())
    
    def get_memory_summary(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Podsumowanie pamięci strategii."""
        record = self.get_strategy_memory_by_id(memory_id)
        if record is None:
            record = self.get_strategy_memory(memory_id)
            if record is None:
                return None
        
        return {
            'memory_id': record.memory_id,
            'strategy_id': record.strategy_id,
            'strategy_version': record.strategy_version,
            'experiment_count': record.get_experiment_count(),
            'creation_time': record.creation_time,
            'last_updated': record.last_updated,
            'feature_count': len(record.feature_schema),
            'model_reference': record.model_reference
        }


# ============================================================================
# TESTY MODUŁU (do uruchomienia z python -m SSI_V5.memory.strategy_memory)
# ============================================================================

def test_strategy_memory_record():
    """Test StrategyMemoryRecord."""
    print("\n" + "="*60)
    print("TEST: StrategyMemoryRecord")
    print("="*60)
    
    try:
        # Test tworzenia
        record = StrategyMemoryRecord(
            strategy_id="test_strategy",
            strategy_version="1.0.0",
            strategy_definition={"type": "test"},
            strategy_parameters={"param1": 0.5},
            feature_schema=["feature1", "feature2"],
            model_reference="test_model"
        )
        
        assert record.memory_id.startswith("smr_")
        assert record.strategy_id == "test_strategy"
        assert record.strategy_version == "1.0.0"
        print("[OK] Test tworzenia StrategyMemoryRecord - zaliczony")
        
        # Test eksperymentu
        exp_data = {"experiment_id": "exp_001", "result": {"accuracy": 0.85}}
        record.add_experiment(exp_data)
        assert len(record.EXPERIMENT_HISTORY) == 1
        print("[OK] Test add_experiment - zaliczony")
        
        # Test aktualizacji wersji
        record.update_version("1.1.0", "Poprawka błędów")
        assert record.strategy_version == "1.1.0"
        assert len(record.EVOLUTION_HISTORY) == 1
        print("[OK] Test update_version - zaliczony")
        
        # Test konwersji do dict
        record_dict = record.to_dict()
        assert record_dict['strategy_id'] == "test_strategy"
        print("[OK] Test to_dict - zaliczony")
        
        # Test konwersji z dict
        record2 = StrategyMemoryRecord.from_dict(record_dict)
        assert record2.strategy_id == record.strategy_id
        print("[OK] Test from_dict - zaliczony")
        
        # Test JSON
        json_str = record.to_json()
        record3 = StrategyMemoryRecord.from_json(json_str)
        assert record3.strategy_id == record.strategy_id
        print("[OK] Test JSON serialization - zaliczony")
        
        # Test get_best_experiment
        record.add_experiment({"experiment_id": "exp_002", "metrics": {"accuracy": 0.90}})
        best = record.get_best_experiment("accuracy")
        assert best["experiment_id"] == "exp_002"
        print("[OK] Test get_best_experiment - zaliczony")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Test StrategyMemoryRecord - error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_strategy_memory_manager():
    """Test StrategyMemoryManager."""
    print("\n" + "="*60)
    print("TEST: StrategyMemoryManager")
    print("="*60)
    
    try:
        import tempfile
        import shutil
        
        # Tymczasowy katalog
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Test inicjalizacji
            manager = StrategyMemoryManager(memory_dir=temp_dir)
            assert hasattr(manager, '_memory_register')
            print("[OK] Test inicjalizacji StrategyMemoryManager - zaliczony")
            
            # Test tworzenia pamięci
            record = manager.create_strategy_memory(
                strategy_id="test_strategy_1",
                strategy_definition={"type": "test"},
                version="1.0.0"
            )
            assert record is not None
            assert len(manager.get_all_strategy_memories()) == 1
            print("[OK] Test create_strategy_memory - zaliczony")
            
            # Test pobierania pamięci
            retrieved = manager.get_strategy_memory("test_strategy_1")
            assert retrieved is not None
            assert retrieved.strategy_id == "test_strategy_1"
            print("[OK] Test get_strategy_memory - zliczony")
            
            # Test zapisu eksperymentu
            class MockStrategyExperiment:
                strategy_id = "test_strategy_1"
                experiment_id = "exp_test"
                strategy_version = "1.0.0"
                world_version = "world_v1"
                dataset_version = "data_v1"
                model_reference = "model_v1"
                features = ["f1", "f2"]
                start_time = datetime.now()
                end_time = datetime.now()
                result = {"success": True}
                metrics = {"accuracy": 0.85}
                status = "completed"
                strategy_parameters = {}
                execution_context = {}
                error = None
                metadata = {}
                
                def to_dict(self):
                    return {
                        'experiment_id': self.experiment_id,
                        'strategy_id': self.strategy_id,
                        'strategy_version': self.strategy_version,
                        'world_version': self.world_version,
                        'dataset_version': self.dataset_version,
                        'model_reference': self.model_reference,
                        'features': self.features,
                        'start_time': self.start_time.isoformat(),
                        'end_time': self.end_time.isoformat(),
                        'result': self.result,
                        'metrics': self.metrics,
                        'status': str(self.status),
                        'strategy_parameters': self.strategy_parameters,
                        'execution_context': self.execution_context,
                        'error': self.error,
                        'metadata': self.metadata,
                    }
            
            exp = MockStrategyExperiment()
            manager.save_experiment(exp)
            
            retrieved = manager.get_strategy_memory("test_strategy_1")
            assert len(retrieved.EXPERIMENT_HISTORY) == 1
            print("[OK] Test save_experiment - zaliczony")
            
            # Test statystyk
            stats = manager.get_statistics()
            assert stats['total_records'] == 1
            assert stats['total_experiments'] == 1
            print("[OK] Test get_statistics - zaliczony")
            
            # Test zapisu JSON
            success = manager.save_to_json()
            assert success is True
            print("[OK] Test save_to_json - zaliczony")
            
            # Test wczytywania JSON
            manager2 = StrategyMemoryManager(memory_dir=temp_dir)
            success = manager2.load_from_json()
            assert success is True
            assert len(manager2.get_all_strategy_memories()) == 1
            print("[OK] Test load_from_json - zaliczony")
            
            # Test czyszczenia
            manager.clear_strategy_memory("test_strategy_1")
            assert manager.get_strategy_memory("test_strategy_1") is None
            print("[OK] Test clear_strategy_memory - zaliczony")
            
            return True
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except Exception as e:
        print(f"[FAIL] Test StrategyMemoryManager - error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Uruchom wszystkie testy."""
    print("\n" + "="*70)
    print("SSI V5 STRATEGY MEMORY - URUCHAMIANIE TESTOW")
    print("="*70)
    
    results = []
    results.append(("StrategyMemoryRecord", test_strategy_memory_record()))
    results.append(("StrategyMemoryManager", test_strategy_memory_manager()))
    
    print("\n" + "="*70)
    print("PODSUMOWANIE TESTOW")
    print("="*70)
    
    for test_name, passed in results:
        status = "✅ ZALICZONY" if passed else "❌ NIE ZALICZONY"
        print(f"{test_name}: {status}")
    
    all_passed = all(passed for _, passed in results)
    print(f"\nOgółem: {sum(1 for _, p in results if p)}/{len(results)} testów zaliczono")
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    if success:
        print("\n✅ Wszystkie testy pamięci strategii zaliczone!")
    else:
        print("\n❌ Niektóre testy nie zostały zaliczone")
    
    exit(0 if success else 1)