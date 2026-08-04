# SSI V5 Teacher Layer - Memory Manager
# ==================================================
#
# Zarządza pamięcią światów, modeli i obserwacji dla SSI V5.
#
# Odpowiedzialność:
# - pamięć światów
# - pamięć modeli
# - pamięć obserwacji
# - zapis JSON
# - odczyt poprzednich doświadczeń
# - przygotowanie danych dla kolejnych cykli
#
# Data: 2026-08-03
# ETAP: 5.2.4 FAZA 3.2
#
# Zasada: Nowa warstwa dodatkowa, nie zmieniamy istniejącej logiki

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional, Union


class MemoryManager:
    """
    Zarządza pamięcią systemu SSI V5 w warstwie Teacher Layer.
    
    Odpowiedzialny za:
    - pamięć światów (world memory)
    - pamięć modeli (model memory)  
    - pamięć obserwacji (observation memory)
    - zapis i odczyt JSON
    - zarządzanie historią doświadczeń
    - przygotowanie danych dla kolejnych cykli uczenia
    
    Współpracuje z:
    - CognitiveTeacher
    - WorldHierarchyManager
    - DynamicWeightsManager
    """
    
    def __init__(self, memory_dir: str = None, network_name: str = "default"):
        """
        Inicjalizacja MemoryManager.
        
        Args:
            memory_dir: Katalog do zapisywania pamięci (domyślnie używa config)
            network_name: Nazwa sieci/modelu
        """
        if memory_dir is None:
            from ..core.config import PathConfig
            memory_dir = PathConfig.MEMORY_DIR
        
        self.memory_dir = memory_dir
        self.network_name = network_name
        self.network_memory_dir = os.path.join(memory_dir, f"network_{network_name}")
        
        # Tworzymy katalog pamięci dla sieci
        os.makedirs(self.network_memory_dir, exist_ok=True)
        
        # Ścieżki plików pamięci
        self.world_memory_path = os.path.join(self.network_memory_dir, "world_memory.json")
        self.model_memory_path = os.path.join(self.network_memory_dir, "model_memory.json")
        self.observation_memory_path = os.path.join(self.network_memory_dir, "observation_memory.json")
        self.experience_history_path = os.path.join(self.network_memory_dir, "experience_history.json")
        
        # Wczytanie istniejącej pamięci
        self.world_memory = self._load_memory(self.world_memory_path, {})
        self.model_memory = self._load_memory(self.model_memory_path, {})
        self.observation_memory = self._load_memory(self.observation_memory_path, {})
        self.experience_history = self._load_memory(self.experience_history_path, [])
        
        # Rejestr aktywnych pamięci
        self.active_memory_register = {
            "world": self.world_memory,
            "model": self.model_memory,
            "observation": self.observation_memory,
            "history": self.experience_history
        }
    
    def _load_memory(self, file_path: str, default_value: Any) -> Any:
        """Wczytaj pamięć z pliku JSON"""
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[MEMORY] Warning: Error loading {file_path}: {e}")
                return default_value
        return default_value
    
    def _save_memory(self, data: Any, file_path: str) -> bool:
        """Zapisz pamięć do pliku JSON"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[MEMORY] Error saving {file_path}: {e}")
            return False
    
    # ========================================================================
    # PAMIĘĆ ŚWIATÓW
    # ========================================================================
    
    def save_world_memory(self, world_data: Dict[str, Any], world_key: str = "default") -> bool:
        """
        Zapisz pamięć świata.
        
        Args:
            world_data: Dane świata do zapisania
            world_key: Klucz identyfikujący świat
        
        Returns:
            bool: Czy zapis się powiódł
        """
        if world_key not in self.world_memory:
            self.world_memory[world_key] = {}
        
        # Zachowaj timestamp
        world_data["last_updated"] = datetime.now().isoformat()
        
        self.world_memory[world_key].update(world_data)
        self._save_memory(self.world_memory, self.world_memory_path)
        
        return True
    
    def get_world_memory(self, world_key: str = "default") -> Dict[str, Any]:
        """
        Pobierz pamięć świata.
        
        Args:
            world_key: Klucz identyfikujący świat
            
        Returns:
            Dict: Dane świata lub pusty dict
        """
        return self.world_memory.get(world_key, {})
    
    def get_all_world_memories(self) -> Dict[str, Any]:
        """Pobierz wszystkie pamięci światów"""
        return self.world_memory
    
    def update_world_statistics(self, world_key: str, stats: Dict[str, Any]) -> bool:
        """
        Zaktualizuj statystyki świata.
        
        Args:
            world_key: Klucz identyfikujący świat
            stats: Nowe statystyki
            
        Returns:
            bool: Czy aktualizacja się powiodła
        """
        if world_key not in self.world_memory:
            self.world_memory[world_key] = {}
        
        if "statistics" not in self.world_memory[world_key]:
            self.world_memory[world_key]["statistics"] = {}
        
        self.world_memory[world_key]["statistics"].update(stats)
        self._save_memory(self.world_memory, self.world_memory_path)
        
        return True
    
    def clear_world_memory(self, world_key: str = None) -> bool:
        """
        Wyczyść pamięć świata.
        
        Args:
            world_key: Klucz świata do wyczyszczenia (None = wyczyść wszystkie)
            
        Returns:
            bool: Czy czyszczenie się powiodło
        """
        if world_key is None:
            self.world_memory = {}
        elif world_key in self.world_memory:
            del self.world_memory[world_key]
        
        self._save_memory(self.world_memory, self.world_memory_path)
        return True
    
    # ========================================================================
    # PAMIĘĆ MODELI
    # ========================================================================
    
    def save_model_memory(self, model_data: Dict[str, Any], model_key: str = "default") -> bool:
        """
        Zapisz pamięć modelu.
        
        Args:
            model_data: Dane modelu do zapisania
            model_key: Klucz identyfikujący model
            
        Returns:
            bool: Czy zapis się powiódł
        """
        if model_key not in self.model_memory:
            self.model_memory[model_key] = {}
        
        # Zachowaj timestamp
        model_data["last_updated"] = datetime.now().isoformat()
        
        self.model_memory[model_key].update(model_data)
        self._save_memory(self.model_memory, self.model_memory_path)
        
        return True
    
    def get_model_memory(self, model_key: str = "default") -> Dict[str, Any]:
        """
        Pobierz pamięć modelu.
        
        Args:
            model_key: Klucz identyfikujący model
            
        Returns:
            Dict: Dane modelu lub pusty dict
        """
        return self.model_memory.get(model_key, {})
    
    def get_all_model_memories(self) -> Dict[str, Any]:
        """Pobierz wszystkie pamięci modeli"""
        return self.model_memory
    
    def update_model_performance(self, model_key: str, performance: Dict[str, float]) -> bool:
        """
        Zaktualizuj wyniki modelu.
        
        Args:
            model_key: Klucz identyfikujący model
            performance: Nowe wyniki (accuracy, loss, etc.)
            
        Returns:
            bool: Czy aktualizacja się powiodła
        """
        if model_key not in self.model_memory:
            self.model_memory[model_key] = {}
        
        if "performance" not in self.model_memory[model_key]:
            self.model_memory[model_key]["performance"] = []
        
        performance["timestamp"] = datetime.now().isoformat()
        self.model_memory[model_key]["performance"].append(performance)
        
        # Zachowaj ostatnie 100 rezultatów
        if len(self.model_memory[model_key]["performance"]) > 100:
            self.model_memory[model_key]["performance"] = \
                self.model_memory[model_key]["performance"][-100:]
        
        self._save_memory(self.model_memory, self.model_memory_path)
        return True
    
    def clear_model_memory(self, model_key: str = None) -> bool:
        """
        Wyczyść pamięć modelu.
        
        Args:
            model_key: Klucz modelu do wyczyszczenia (None = wyczyść wszystkie)
            
        Returns:
            bool: Czy czyszczenie się powiodło
        """
        if model_key is None:
            self.model_memory = {}
        elif model_key in self.model_memory:
            del self.model_memory[model_key]
        
        self._save_memory(self.model_memory, self.model_memory_path)
        return True
    
    # ========================================================================
    # PAMIĘĆ OBSERWACJI
    # ========================================================================
    
    def save_observation_memory(self, observation_data: Dict[str, Any], 
                              observation_key: str = None) -> bool:
        """
        Zapisz pamięć obserwacji.
        
        Args:
            observation_data: Dane obserwacji do zapisania
            observation_key: Klucz identyfikujący obserwację (opcjonalny)
            
        Returns:
            bool: Czy zapis się powiódł
        """
        if observation_key is None:
            observation_key = f"obs_{len(self.observation_memory) + 1}"
        
        if observation_key not in self.observation_memory:
            self.observation_memory[observation_key] = {}
        
        # Zachowaj timestamp
        observation_data["timestamp"] = datetime.now().isoformat()
        
        self.observation_memory[observation_key].update(observation_data)
        self._save_memory(self.observation_memory, self.observation_memory_path)
        
        return True
    
    def get_observation_memory(self, observation_key: str = None) -> Dict[str, Any]:
        """
        Pobierz pamięć obserwacji.
        
        Args:
            observation_key: Klucz identyfikujący obserwację
            
        Returns:
            Dict: Dane obserwacji lub wszystkie dane
        """
        if observation_key is None:
            return self.observation_memory
        return self.observation_memory.get(observation_key, {})
    
    def add_prediction_observation(self, match_id: str, prediction: Dict[str, Any], 
                                  actual_result: Dict[str, Any] = None) -> bool:
        """
        Dodaj obserwację predykcji.
        
        Args:
            match_id: ID meczu
            prediction: Predykcja modelu
            actual_result: Rzeczywisty wynik (opcjonalny)
            
        Returns:
            bool: Czy dodanie się powiodło
        """
        observation = {
            "match_id": match_id,
            "prediction": prediction,
            "actual_result": actual_result,
            "timestamp": datetime.now().isoformat()
        }
        
        if match_id not in self.observation_memory:
            self.observation_memory[match_id] = []
        
        self.observation_memory[match_id].append(observation)
        
        # Zachowaj ostatnie 50 obserwacji na mecz
        if len(self.observation_memory[match_id]) > 50:
            self.observation_memory[match_id] = self.observation_memory[match_id][-50:]
        
        self._save_memory(self.observation_memory, self.observation_memory_path)
        return True
    
    def clear_observation_memory(self, observation_key: str = None) -> bool:
        """
        Wyczyść pamięć obserwacji.
        
        Args:
            observation_key: Klucz obserwacji do wyczyszczenia (None = wyczyść wszystkie)
            
        Returns:
            bool: Czy czyszczenie się powiodło
        """
        if observation_key is None:
            self.observation_memory = {}
        elif observation_key in self.observation_memory:
            del self.observation_memory[observation_key]
        
        self._save_memory(self.observation_memory, self.observation_memory_path)
        return True
    
    # ========================================================================
    # HISTORIA DOŚWIADCZEŃ
    # ========================================================================
    
    def add_experience_record(self, experience: Dict[str, Any]) -> bool:
        """
        Dodaj rekord do historii doświadczeń.
        
        Args:
            experience: Rekord doświadczenia
            
        Returns:
            bool: Czy dodanie się powiodło
        """
        # Ustaw timestamp jeśli nie istnieje
        if "timestamp" not in experience:
            experience["timestamp"] = datetime.now().isoformat()
        
        self.experience_history.append(experience)
        
        # Zachowaj ostatnie 1000 rekordów
        if len(self.experience_history) > 1000:
            self.experience_history = self.experience_history[-1000:]
        
        self._save_memory(self.experience_history, self.experience_history_path)
        return True
    
    def get_experience_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Pobierz historię doświadczeń.
        
        Args:
            limit: Maksymalna liczba rekordów (None = wszystkie)
            
        Returns:
            List: Historia doświadczeń
        """
        if limit is None:
            return self.experience_history
        return self.experience_history[-limit:]
    
    def get_experience_by_network(self, network_name: str) -> List[Dict[str, Any]]:
        """
        Pobierz doświadczenia dla konkretnej sieci.
        
        Args:
            network_name: Nazwa sieci
            
        Returns:
            List: Doświadczenia dla sieci
        """
        return [exp for exp in self.experience_history 
                if exp.get("network_name") == network_name]
    
    def get_experience_by_date(self, start_date: str, end_date: str = None) -> List[Dict[str, Any]]:
        """
        Pobierz doświadczenia z konkretnego okresu.
        
        Args:
            start_date: Data początkowa (ISO format)
            end_date: Data końcowa (ISO format, opcjonalny)
            
        Returns:
            List: Doświadczenia z okresu
        """
        result = []
        for exp in self.experience_history:
            exp_date = exp.get("timestamp", "")
            if exp_date and exp_date >= start_date:
                if end_date is None or exp_date <= end_date:
                    result.append(exp)
        return result
    
    def clear_experience_history(self) -> bool:
        """Wyczyść historię doświadczeń"""
        self.experience_history = []
        self._save_memory(self.experience_history, self.experience_history_path)
        return True
    
    # ========================================================================
    # OPERACJE GLOBALNE
    # ========================================================================
    
    def save_all_memory(self) -> bool:
        """Zapisz wszystkie pamięci"""
        success = True
        success &= self._save_memory(self.world_memory, self.world_memory_path)
        success &= self._save_memory(self.model_memory, self.model_memory_path)
        success &= self._save_memory(self.observation_memory, self.observation_memory_path)
        success &= self._save_memory(self.experience_history, self.experience_history_path)
        return success
    
    def load_all_memory(self) -> bool:
        """Wczytaj wszystkie pamięci"""
        self.world_memory = self._load_memory(self.world_memory_path, {})
        self.model_memory = self._load_memory(self.model_memory_path, {})
        self.observation_memory = self._load_memory(self.observation_memory_path, {})
        self.experience_history = self._load_memory(self.experience_history_path, [])
        return True
    
    def clear_all_memory(self) -> bool:
        """Wyczyść wszystkie pamięci"""
        self.world_memory = {}
        self.model_memory = {}
        self.observation_memory = {}
        self.experience_history = []
        
        # Wyczyść pliki
        for path in [self.world_memory_path, self.model_memory_path, 
                    self.observation_memory_path, self.experience_history_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"[MEMORY] Warning: Could not delete {path}: {e}")
        
        return True
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """
        Pobierz statystyki pamięci.
        
        Returns:
            Dict: Statystyki wszystkich pamięci
        """
        return {
            "world_memory": {
                "count": len(self.world_memory),
                "keys": list(self.world_memory.keys())
            },
            "model_memory": {
                "count": len(self.model_memory),
                "keys": list(self.model_memory.keys())
            },
            "observation_memory": {
                "count": len(self.observation_memory),
                "total_observations": sum(len(v) if isinstance(v, list) else 1 
                                       for v in self.observation_memory.values())
            },
            "experience_history": {
                "count": len(self.experience_history)
            }
        }
    
    def prepare_memory_for_next_cycle(self, cognitive_teacher_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Przygotuj pamięć dla kolejnego cyklu uczenia.
        
        Args:
            cognitive_teacher_result: Wynik z CognitiveTeacher.uruchom_analyse()
            
        Returns:
            Dict: Przygotowane dane pamięci для następnego cyklu
        """
        prepared = {
            "timestamp": datetime.now().isoformat(),
            "network_name": self.network_name,
            "world_data": cognitive_teacher_result.get("swiat", {}),
            "weights": cognitive_teacher_result.get("wagi", {}),
            "ranking": cognitive_teacher_result.get("ranking", []),
            "rules": cognitive_teacher_result.get("reguly", []),
            "conclusions": cognitive_teacher_result.get("wnioski", []),
            "memory_stats": self.get_memory_statistics()
        }
        
        # Dodaj rekord do historii doświadczeń
        self.add_experience_record(prepared)
        
        return prepared
    
    def integrate_with_teacher(self, teacher_instance) -> None:
        """
        Zintegruj z instancją CognitiveTeacher.
        
        Args:
            teacher_instance: Instancja CognitiveTeacher
        """
        # Ustaw referencję do MemoryManager w teacherze
        if hasattr(teacher_instance, 'memory_manager'):
            teacher_instance.memory_manager = self
        
        # Synchronizuj pamięć świecie
        if hasattr(teacher_instance, 'swiat_doswiadczenia'):
            self.save_world_memory(
                teacher_instance.swiat_doswiadczenia,
                f"teacher_{teacher_instance.siec_name}"
            )


# ============================================================================
# TESTY MODUŁU
# ============================================================================

def test_memory_manager():
    """Test podstawowych funkcjonalności MemoryManager"""
    print("\n" + "="*60)
    print("TEST: MemoryManager")
    print("="*60)
    
    try:
        import tempfile
        import shutil
        
        # Tworzymy tymczasowy katalog
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Test inicjalizacji
            manager = MemoryManager(memory_dir=temp_dir, network_name="test")
            assert hasattr(manager, 'world_memory')
            assert hasattr(manager, 'model_memory')
            assert hasattr(manager, 'observation_memory')
            assert hasattr(manager, 'experience_history')
            print("[OK] Test inicjalizacji - zaliczony")
            
            # Test zapisywania pamięci świata
            world_data = {"level": "poziom3", "accuracy": 0.85}
            manager.save_world_memory(world_data, "test_world")
            assert "test_world" in manager.world_memory
            print("[OK] Test save_world_memory - zaliczony")
            
            # Test zapisywania pamięci modelu
            model_data = {"accuracy": 0.9, "loss": 0.1}
            manager.save_model_memory(model_data, "test_model")
            assert "test_model" in manager.model_memory
            print("[OK] Test save_model_memory - zaliczony")
            
            # Test zapisywania pamięci obserwacji
            obs_data = {"match_id": "123", "prediction": {"result": "2:1"}}
            manager.save_observation_memory(obs_data, "obs_1")
            assert "obs_1" in manager.observation_memory
            print("[OK] Test save_observation_memory - zaliczony")
            
            # Test dodawania rekordu doświadczenia
            exp_record = {"type": "analysis", "result": "success"}
            manager.add_experience_record(exp_record)
            assert len(manager.experience_history) == 1
            print("[OK] Test add_experience_record - zaliczony")
            
            # Test statystyk pamięci
            stats = manager.get_memory_statistics()
            assert "world_memory" in stats
            assert "model_memory" in stats
            print("[OK] Test get_memory_statistics - zaliczony")
            
            # Test save_all_memory
            success = manager.save_all_memory()
            assert success is True
            print("[OK] Test save_all_memory - zaliczony")
            
            # Test wczytywania pamięci
            manager2 = MemoryManager(memory_dir=temp_dir, network_name="test")
            assert "test_world" in manager2.world_memory
            assert "test_model" in manager2.model_memory
            print("[OK] Test persistence - zaliczony")
            
            return True
            
        finally:
            # Usunięcie tymczasowego katalogu
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except Exception as e:
        print(f"[FAIL] Test MemoryManager - error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_edge_cases():
    """Test przypadków brzegowych"""
    print("\n" + "="*60)
    print("TEST: MemoryManager edge cases")
    print("="*60)
    
    try:
        import tempfile
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            manager = MemoryManager(memory_dir=temp_dir)
            
            # Test z pustymi danymi
            world_data = manager.get_world_memory("nonexistent")
            assert world_data == {}
            print("[OK] Test get nonexistent world memory - zaliczony")
            
            # Test czyszczenia pamięci
            manager.save_world_memory({"test": "data"}, "test")
            manager.clear_world_memory("test")
            assert "test" not in manager.world_memory
            print("[OK] Test clear_world_memory - zaliczony")
            
            # Test czyszczenia całej pamięci
            manager.clear_all_memory()
            assert len(manager.world_memory) == 0
            assert len(manager.model_memory) == 0
            print("[OK] Test clear_all_memory - zaliczony")
            
            return True
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except Exception as e:
        print(f"[FAIL] Test MemoryManager edge cases - error: {e}")
        return False


if __name__ == "__main__":
    test_memory_manager()
    test_edge_cases()
    print("\nMemoryManager - Testy wykonane")