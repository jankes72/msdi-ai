# SSI V5 Runtime - Test Launcher
# ==================================================
#
# ETAP: 5.2.4 FAZA 3.3.3
# Data: 2026-08-03
#
# Odpowiedzialnosc:
# - Testowy launcher dla SSI V5
# - Uruchomienie Pipeline w trybie TEST
# - 10 cykli testowych
# - Zapis stanu runtime_state.json
# - Zapis historii cykli
# - Obsluga bledow
# - Graceful shutdown

import sys
import os
import json
import traceback
from datetime import datetime
from pathlib import Path

# Dodanie sciezki do SSI_V5 do sys.path
ssi_path = str(Path(__file__).parent.parent)
if ssi_path not in sys.path:
    sys.path.insert(0, ssi_path)

from SSI_V5.core.pipeline import (
    SSIPipeline, 
    PipelineMode, 
    CycleStatus,
    CycleMetadata,
    PipelineStatus
)
from SSI_V5.core.world_engine import WorldEngine, WorldEngineOutput


# ============================================================================
# KONFIGURACJA TESTOWA
# ============================================================================

CONFIG_TEST = {
    "mode": "TEST",
    "pipeline_mode": PipelineMode.TEST,
    "num_cycles": 10,
    "delay_between_cycles": 0.05,  # 50ms opoznienie miedzy cyklami
    "world_name": "SSI_V5_TEST_WORLD",
    "output_dir": "state",
    "files": {
        "runtime_state": "runtime_state.json",
        "last_cycle": "last_cycle.json",
        "cycle_history": "cycle_history.json",
        "event_log": "event_log.json"
    }
}


# ============================================================================
# FILE MANAGER - Zarzadzanie zapisywaniem i odczytywaniem stanu
# ============================================================================

class FileManager:
    """
    Manager plikow dla mechanizmu recovery.
    Odpowiedzialny za zapis i odczyt stanu systemu.
    """
    
    def __init__(self, base_dir: str = "state", config: dict = None):
        """
        Inicjalizacja FileManager.
        
        Args:
            base_dir: Bazowy katalog dla plikow stanu
            config: Konfiguracja z nazwa plikow
        """
        self.base_dir = Path(base_dir)
        self.config = config or CONFIG_TEST
        
        # Upewnij sie ze katalog istnieje
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def get_file_path(self, file_name: str) -> Path:
        """Pobranie pelnej sciezki do pliku."""
        return self.base_dir / file_name
    
    def save_runtime_state(self, runtime_state: dict) -> bool:
        """Zapis stanu runtime do pliku."""
        try:
            file_path = self.get_file_path(self.config["files"]["runtime_state"])
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(runtime_state, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"[ERROR] Nie udalo sie zapisa stan runtime: {e}")
            return False
    
    def load_runtime_state(self) -> dict:
        """Odczyt stanu runtime z pliku."""
        try:
            file_path = self.get_file_path(self.config["files"]["runtime_state"])
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[WARNING] Nie udalo sie odczytac stan runtime: {e}")
        return {}
    
    def save_last_cycle(self, cycle_data: dict) -> bool:
        """Zapis ostatniego cyklu do pliku."""
        try:
            file_path = self.get_file_path(self.config["files"]["last_cycle"])
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cycle_data, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"[ERROR] Nie udalo sie zapisa ostatniego cyklu: {e}")
            return False
    
    def load_last_cycle(self) -> dict:
        """Odczyt ostatniego cyklu z pliku."""
        try:
            file_path = self.get_file_path(self.config["files"]["last_cycle"])
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[WARNING] Nie udalo sie odczytac ostatniego cyklu: {e}")
        return {}
    
    def save_cycle_history(self, history: list) -> bool:
        """Zapis historii cykli do pliku."""
        try:
            file_path = self.get_file_path(self.config["files"]["cycle_history"])
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"[ERROR] Nie udalo sie zapisa historii cykli: {e}")
            return False
    
    def save_event_log(self, event_log: list) -> bool:
        """Zapis dziennika zdarzen do pliku."""
        try:
            file_path = self.get_file_path(self.config["files"]["event_log"])
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(event_log, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"[ERROR] Nie udalo sie zapisa dziennika zdarzen: {e}")
            return False


# ============================================================================
# TEST LAUNCHER
# ============================================================================

class TestLauncher:
    """
    Testowy launcher dla SSI V5.
    Uruchamia Pipeline w trybie TEST z 10 cyklami.
    """
    
    def __init__(self, config: dict = None):
        """
        Inicjalizacja TestLauncher.
        
        Args:
            config: Konfiguracja launchera (opcjonalna)
        """
        self.config = config or CONFIG_TEST
        self.pipeline = None
        self.file_manager = None
        self.start_time = None
        self.end_time = None
        
    def initialize(self) -> dict:
        """
        Inicjalizacja systemu.
        
        Returns:
            Status inicjalizacji
        """
        print("=" * 80)
        print("SSI V5 TEST LAUNCHER - ETAP 5.2.4 FAZA 3.3.3")
        print("=" * 80)
        
        self.start_time = datetime.now()
        self.file_manager = FileManager(config=self.config)
        
        # Inicjalizacja Pipeline z AgentRuntimeManager (aktualna architektura V5)
        try:
            self.pipeline = SSIPipeline(
                mode=self.config["pipeline_mode"],
                world_name=self.config["world_name"],
                use_agent_runtime_manager=True  # Użyj AgentRuntimeManager, nie interfejsu
            )
            
            # Inicjalizacja Pipeline
            init_result = self.pipeline.initialize()
            
            if init_result.get('status') != 'success':
                return {
                    'status': 'error',
                    'error': init_result.get('error', 'Unknown initialization error'),
                    'step': 'pipeline_initialization'
                }
            
            print(f"[INFO] Pipeline zainicjalizowany: {init_result.get('pipeline_status', 'unknown')}")
            
            return {
                'status': 'success',
                'message': 'TestLauncher zainicjalizowany pomyslnie',
                'pipeline_status': init_result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'traceback': traceback.format_exc(),
                'step': 'launcher_initialization'
            }
    
    def run_test_cycles(self) -> dict:
        """
        Wykonanie testowych cykli.
        
        Returns:
            Podsumowanie wykonanych cykli
        """
        if not self.pipeline or not self.pipeline._initialized:
            return {
                'status': 'error',
                'error': 'Pipeline not initialized',
                'timestamp': datetime.now().isoformat()
            }
        
        print(f"\n[INFO] Rozpoczeto execute {self.config['num_cycles']} cykli testowych...")
        
        # Uruchomienie wielu cykli
        summary = self.pipeline.run_cycles(
            number=self.config['num_cycles'],
            delay=self.config['delay_between_cycles']
        )
        
        summary['launcher_config'] = {
            'mode': self.config['mode'],
            'num_cycles': self.config['num_cycles'],
            'delay': self.config['delay_between_cycles'],
            'world_name': self.config['world_name']
        }
        
        return summary
    
    def save_state(self) -> dict:
        """
        Zapis stanu systemu po testach.
        
        Returns:
            Status zapisywania
        """
        if not self.pipeline:
            return {'status': 'error', 'error': 'Pipeline not available'}
        
        print("\n[INFO] Zapisywnie stanu systemu...")
        
        # 1. Zapis runtime_state.json
        runtime_state = {
            'mode': self.config['mode'],
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': datetime.now().isoformat(),
            'pipeline_status': self.pipeline.get_status(),
            'config': self.config,
            'system_info': {
                'launcher': 'start_ssi_test.py',
                'etap': '5.2.4',
                'faza': '3.3.3',
                'timestamp': datetime.now().isoformat()
            }
        }
        
        self.file_manager.save_runtime_state(runtime_state)
        print(f"[SUCCESS] Zapisano runtime_state.json")
        
        # 2. Zapis ostatniego cyklu
        cycle_history = self.pipeline.get_cycle_history()
        if cycle_history:
            last_cycle = cycle_history[-1]
            last_cycle_data = last_cycle
            self.file_manager.save_last_cycle(last_cycle_data)
            print(f"[SUCCESS] Zapisano last_cycle.json (cycle: {last_cycle['cycle_id']})")
        
        # 3. Zapis historii cykli
        cycle_history = self.pipeline.get_cycle_history()
        self.file_manager.save_cycle_history(cycle_history)
        print(f"[SUCCESS] Zapisano cycle_history.json ({len(cycle_history)} cykli)")
        
        # 4. Zapis dziennika zdarzen
        event_log = self.pipeline.get_event_log()
        self.file_manager.save_event_log(event_log)
        print(f"[SUCCESS] Zapisano event_log.json ({len(event_log)} zdarzen)")
        
        return {
            'status': 'success',
            'files_saved': ['runtime_state.json', 'last_cycle.json', 'cycle_history.json', 'event_log.json'],
            'timestamp': datetime.now().isoformat()
        }
    
    def shutdown(self) -> dict:
        """
        Graceful shutdown systemu.
        
        Returns:
            Status zamkniecia
        """
        print("\n[INFO] Rozpoczynanie graceful shutdown...")
        
        self.end_time = datetime.now()
        
        # Zamkniecie Pipeline
        try:
            shutdown_result = self.pipeline.shutdown()
            print(f"[INFO] Pipeline zamkniety: {shutdown_result.get('status', 'unknown')}")
        except Exception as e:
            print(f"[WARNING] Blad podczas zamykania Pipeline: {e}")
            shutdown_result = {'status': 'error', 'error': str(e)}
        
        # Zapisz state na koniec
        self.save_state()
        
        # Podsumowanie
        duration = (self.end_time - self.start_time).total_seconds() if self.start_time else None
        
        print("\n" + "=" * 80)
        print("TEST LAUNCHER - PODSUMOWANIE")
        print("=" * 80)
        print(f"Czas startu: {self.start_time.isoformat() if self.start_time else 'N/A'}")
        print(f"Czas zakonczenia: {self.end_time.isoformat() if self.end_time else 'N/A'}")
        print(f"Calkowity czas: {duration:.3f}s" if duration else "Calkowity czas: N/A")
        print(f"Status zamkniecia: {shutdown_result.get('status', 'unknown')}")
        print("=" * 80)
        
        return {
            'status': shutdown_result.get('status', 'error'),
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': duration,
            'pipeline_shutdown': shutdown_result,
            'message': 'TestLauncher shutdown completed'
        }
    
    def run(self) -> dict:
        """
        Pelny przebieg testowy.
        
        Returns:
            Calkowity wynik uruchomienia
        """
        print("\n" + "=" * 80)
        print("START TEST LAUNCHER - ETAP 5.2.4 FAZA 3.3.3")
        print("=" * 80)
        
        # 1. Inicjalizacja
        init_result = self.initialize()
        if init_result.get('status') != 'success':
            error_msg = init_result.get('error', 'Unknown error')
            print(f"\n[ERROR] Blad inicjalizacji: {error_msg}")
            print(f"[TRACEBACK] {init_result.get('traceback', '')}")
            
            return {
                'status': 'error',
                'step': 'initialization',
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            }
        
        # 2. Wykonanie cykli
        try:
            cycle_result = self.run_test_cycles()
            if cycle_result.get('status') != 'success':
                print(f"\n[WARNING] Problemy podczas wykonywania cykli: {cycle_result.get('error', '')}")
        except Exception as e:
            print(f"\n[ERROR] Blad podczas wykonywania cykli: {e}")
            print(f"[TRACEBACK] {traceback.format_exc()}")
            cycle_result = {'status': 'error', 'error': str(e)}
        
        # 3. Zapisz state
        try:
            state_result = self.save_state()
        except Exception as e:
            print(f"\n[ERROR] Blad podczas zapisywania stanu: {e}")
            state_result = {'status': 'error', 'error': str(e)}
        
        # 4. Shutdown
        shutdown_result = self.shutdown()
        
        # Calkowity wynik
        result = {
            'status': 'success' if all([
                init_result.get('status') == 'success',
                cycle_result.get('status') == 'success',
                state_result.get('status') == 'success',
                shutdown_result.get('status') == 'success'
            ]) else 'partial_success',
            'steps': {
                'initialization': init_result.get('status', 'error'),
                'cycle_execution': cycle_result.get('status', 'error'),
                'state_saving': state_result.get('status', 'error'),
                'shutdown': shutdown_result.get('status', 'error')
            },
            'summary': cycle_result,
            'timestamp': datetime.now().isoformat()
        }
        
        return result


# ============================================================================
# GLOWNA FUNKCJA
# ============================================================================

def main():
    """Glowna funkcja uruchomieniowa."""
    print("SSI V5 Test Launcher Starting...")
    print("ETAP 5.2.4 FAZA 3.3.3 - Runtime + Life Cycle Integration")
    print(f"Czas: {datetime.now().isoformat()}")
    
    # Tworzenie i uruchomienie launchera
    launcher = TestLauncher()
    result = launcher.run()
    
    # Zwroc kod wyjscia
    if result.get('status') == 'success':
        print("\n[SUCCESS] Test Launcher zakonczyl sie pomyslnie!")
        return 0
    elif result.get('status') == 'partial_success':
        print("\n[WARNING] Test Launcher zakonczyl sie z ostrzezeniami!")
        return 1
    else:
        print("\n[ERROR] Test Launcher zakonczyl sie bledem!")
        return 2


if __name__ == "__main__":
    sys.exit(main())
