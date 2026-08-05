# SSI V5 Runtime - Production Launcher
# ==================================================
#
# ETAP: 5.2.4 FAZA 3.3.3
# Data: 2026-08-03
#
# Odpowiedzialnosc:
# - Produkcyjny launcher dla SSI V5
# - Tryb PipelineMode.PRODUCTION
# - Czas startu i zakonczenia
# - Limit pracy 5 godzin
# - Zapis stanu
# - Obsluga restartu systemu

import sys
import os
import json
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

# Dodanie sciezki do SSI_V5 do sys.path
ssi_path = str(Path(__file__).parent.parent)
if ssi_path not in sys.path:
    sys.path.insert(0, ssi_path)

from SSI_V5.core.world_engine import WorldEngine, WorldEngineOutput

# ETAP 1.2.7.3: Memory Integration
from SSI_V5.ifc.registry import IFCRegistry
from SSI_V5.memory.ecosystem import MemoryEcosystem
from SSI_V5.memory.integrator import MemoryIntegrator

# Opóźnione importy, aby uniknąć circular imports (pipeline -> runtime -> start_ssi -> pipeline)
# from SSI_V5.core.pipeline import SSIPipeline, PipelineMode, CycleStatus, CycleMetadata, PipelineStatus


# ============================================================================
# KONFIGURACJA PRODUKCYJNA
# ============================================================================

CONFIG_PRODUCTION = {
    "mode": "PRODUCTION",
    "pipeline_mode": "PRODUCTION",  # Changed from PipelineMode.PRODUCTION to string to avoid circular import
    "max_runtime_hours": 5,  # Makrymalny czas pracy w godzinach
    "time_buffer_minutes": 5,  # Bufor czasowy przed koncem (minuty)
    "world_name": "SSI_V5_PRODUCTION_WORLD",
    "check_interval_seconds": 30.0,  # Sprawdzanie czasu co 30 sekund
    "output_dir": "state",
    "files": {
        "runtime_state": "runtime_state.json",
        "last_cycle": "last_cycle.json", 
        "cycle_history": "cycle_history.json",
        "event_log": "event_log.json",
        "recovery_info": "recovery_info.json"
    }
}


# ============================================================================
# RECOVERY MANAGER - Mechanizm odzysku po restarcie
# ============================================================================

class RecoveryManager:
    """
    Manager recovery - odzysk stanu po restarcie systemu.
    Odpowiedzialny za:
    - Sprawdzanie czy wystapil restart
    - Odzysk ostatniego stanu
    - Kontynuacja od odpowiedniego cyklu
    """
    
    def __init__(self, base_dir: str = "state", config: dict = None):
        """
        Inicjalizacja RecoveryManager.
        
        Args:
            base_dir: Bazowy katalog dla plikow stanu
            config: Konfiguracja
        """
        self.base_dir = Path(base_dir)
        self.config = config or CONFIG_PRODUCTION
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.recovery_info = {}
        self.last_cycle_data = {}
        self.runtime_state = {}
        
    def check_for_recovery(self) -> bool:
        """
        Sprawdzenie czy istnieja pliki do recovery.
        
        Returns:
            True jesli zwyczajne recovery jest mozliwe
        """
        recovery_file = self.base_dir / self.config["files"]["recovery_info"]
        return recovery_file.exists()
    
    def load_recovery_info(self) -> dict:
        """Zaladowanie informacji o recovery."""
        try:
            recovery_file = self.base_dir / self.config["files"]["recovery_info"]
            if recovery_file.exists():
                with open(recovery_file, 'r', encoding='utf-8') as f:
                    self.recovery_info = json.load(f)
        except Exception as e:
            print(f"[WARNING] Nie udalo sie zaladowac recovery_info: {e}")
            self.recovery_info = {}
        return self.recovery_info
    
    def load_all_state(self) -> dict:
        """Zaladowanie wszystkich plikow stanu."""
        # 1. Runtime state
        self._load_runtime_state()
        
        # 2. Last cycle
        self._load_last_cycle()
        
        # 3. Recovery info
        self.load_recovery_info()
        
        return {
            'recovery_info': self.recovery_info,
            'runtime_state': self.runtime_state,
            'last_cycle': self.last_cycle_data
        }
    
    def _load_runtime_state(self) -> dict:
        """Zaladowanie stanu runtime."""
        try:
            runtime_file = self.base_dir / self.config["files"]["runtime_state"]
            if runtime_file.exists():
                with open(runtime_file, 'r', encoding='utf-8') as f:
                    self.runtime_state = json.load(f)
        except Exception as e:
            print(f"[WARNING] Nie udalo sie zaladowac runtime_state: {e}")
            self.runtime_state = {}
        return self.runtime_state
    
    def _load_last_cycle(self) -> dict:
        """Zaladowanie ostatniego cyklu."""
        try:
            last_cycle_file = self.base_dir / self.config["files"]["last_cycle"]
            if last_cycle_file.exists():
                with open(last_cycle_file, 'r', encoding='utf-8') as f:
                    self.last_cycle_data = json.load(f)
        except Exception as e:
            print(f"[WARNING] Nie udalo sie zaladowac ostatniego cyklu: {e}")
            self.last_cycle_data = {}
        return self.last_cycle_data
    
    def get_last_cycle_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Pobranie metadanych ostatniego cyklu.
        
        Returns:
            Metadane ostatniego cyklu lub None
        """
        if self.last_cycle_data:
            return self.last_cycle_data
        return None
    
    def get_recovery_start_data(self) -> Dict[str, Any]:
        """
        Pobranie danych startowych dla recovery.
        
        Returns:
            Dane do kontynuacji pracy
        """
        all_state = self.load_all_state()
        
        start_data = {
            'recovery_mode': True,
            'previous_session': all_state['recovery_info'].get('session_id', 'unknown'),
            'last_cycle_metadata': all_state['runtime_state'].get('pipeline_status', {}),
            'restart_timestamp': datetime.now().isoformat(),
            'message': 'Recovery mode - odzysk po restarcie'
        }
        
        return start_data
    
    def save_recovery_info(self, info: dict) -> bool:
        """Zapis informacji o recovery."""
        try:
            recovery_file = self.base_dir / self.config["files"]["recovery_info"]
            with open(recovery_file, 'w', encoding='utf-8') as f:
                json.dump(info, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"[ERROR] Nie udalo sie zapisa recovery_info: {e}")
            return False


# ============================================================================
# TIME MANAGER - Zarzadzanie czasem pracy
# ============================================================================

class TimeManager:
    """
    Manager czasu pracy systemu.
    Odpowiedzialny za:
    - Monitorowanie czasu pracy
    - Sprawdzanie czy nigdy pozostalego czasu
    - Obliczanie pozostalego czasu
    """
    
    def __init__(self, max_runtime_hours: int = 5, time_buffer_minutes: int = 5):
        """
        Inicjalizacja TimeManager.
        
        Args:
            max_runtime_hours: Maksymalny czas pracy w godzinach
            time_buffer_minutes: Bufor czasowy w minutach
        """
        self.max_runtime_hours = max_runtime_hours
        self.time_buffer_minutes = time_buffer_minutes
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.time_check_interval = 30.0  # Sprawdzanie co 30 sekund
    
    def initialize(self, start_time: Optional[datetime] = None) -> None:
        """
        Inicjalizacja czasu startu.
        
        Args:
            start_time: Czas startu (opcjonalny, domyslnie now)
        """
        self.start_time = start_time or datetime.now()
        self.end_time = self.start_time + timedelta(hours=self.max_runtime_hours)
    
    def get_remaining_time(self) -> timedelta:
        """
        Pobranie pozostalego czasu pracy.
        
        Returns:
            Pozostaly czas jako timedelta
        """
        if not self.end_time:
            return timedelta(0)
        
        remaining = self.end_time - datetime.now()
        return remaining if remaining > timedelta(0) else timedelta(0)
    
    def get_remaining_seconds(self) -> float:
        """
        Pobranie pozostalego czasu w sekundach.
        
        Returns:
            Pozostaly czas w sekundach
        """
        return self.get_remaining_time().total_seconds()
    
    def should_continue(self) -> bool:
        """
        Sprawdzenie czy system powinien kontynuowac prace.
        
        Uwzględnia bufor czasowy.
        
        Returns:
            True jesli powinien kontynuowac
        """
        buffer_seconds = self.time_buffer_minutes * 60
        remaining_seconds = self.get_remaining_seconds()
        
        # Kontynuuj jesli pozostalo wiecej niz bufor czasu
        return remaining_seconds > buffer_seconds
    
    def get_time_summary(self) -> Dict[str, Any]:
        """
        Pobranie podsumowania czasu.
        
        Returns:
            Podsumowanie czasu pracy
        """
        elapsed_seconds = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        remaining_seconds = self.get_remaining_seconds()
        
        return {
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'max_runtime_hours': self.max_runtime_hours,
            'time_buffer_minutes': self.time_buffer_minutes,
            'elapsed_seconds': elapsed_seconds,
            'elapsed_hours': elapsed_seconds / 3600,
            'remaining_seconds': remaining_seconds,
            'remaining_minutes': remaining_seconds / 60,
            'should_continue': self.should_continue(),
            'buffer_threshold': self.time_buffer_minutes * 60
        }


# ============================================================================
# STATE MANAGER - Zarzadzanie zapisem stanu
# ============================================================================

class StateManager:
    """
    Manager stanu - uniwersalny manager do zapisywania i odczytywania stanu systemu.
    """
    
    def __init__(self, base_dir: str = "state", config: dict = None):
        """
        Inicjalizacja StateManager.
        
        Args:
            base_dir: Bazowy katalog
            config: Konfiguracja
        """
        self.base_dir = Path(base_dir)
        self.config = config or CONFIG_PRODUCTION
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def save_runtime_state(self, pipeline, 
                          time_manager: TimeManager, 
                          additional_data: dict = None) -> bool:
        """
        Zapis calego stanu systemu.
        
        Args:
            pipeline: Instancja Pipeline
            time_manager: Instancja TimeManager
            additional_data: Dodatkowe dane
            
        Returns:
            Status zapisywania
        """
        runtime_state = {
            'mode': 'PRODUCTION',
            'start_time': time_manager.start_time.isoformat() if time_manager.start_time else None,
            'end_time': time_manager.end_time.isoformat() if time_manager.end_time else None,
            'pipeline_status': pipeline.get_status(),
            'time_summary': time_manager.get_time_summary(),
            'config': self.config,
            'system_info': {
                'launcher': 'start_ssi.py',
                'etap': '5.2.4',
                'faza': '3.3.3',
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Dodaj dodatkowe dane
        if additional_data:
            runtime_state.update(additional_data)
        
        try:
            file_path = self.base_dir / self.config["files"]["runtime_state"]
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(runtime_state, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"[ERROR] Nie udalo sie zapisa runtime_state: {e}")
            return False
    
    def save_cycle_state(self, pipeline) -> bool:
        """
        Zapis stanu cyklu.
        
        Args:
            pipeline: Instancja Pipeline
            
        Returns:
            Status zapisywania
        """
        success = True
        
        # Zapis ostatniego cyklu
        cycle_history = pipeline.get_cycle_history() if hasattr(pipeline, 'get_cycle_history') else []
        if cycle_history:
            last_cycle = cycle_history[-1]
            try:
                last_cycle_file = self.base_dir / self.config["files"]["last_cycle"]
                with open(last_cycle_file, 'w', encoding='utf-8') as f:
                    json.dump(last_cycle.to_dict() if hasattr(last_cycle, 'to_dict') else last_cycle, f, indent=2, ensure_ascii=False, default=str)
            except Exception as e:
                print(f"[ERROR] Nie udalo sie zapisa ostatniego cyklu: {e}")
                success = False
        
        # Zapis historii cykli
        try:
            history_file = self.base_dir / self.config["files"]["cycle_history"]
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(pipeline.get_cycle_history(), f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"[ERROR] Nie udalo sie zapisa historii cykli: {e}")
            success = False
        
        # Zapis dziennika zdarzen
        try:
            event_log_file = self.base_dir / self.config["files"]["event_log"]
            with open(event_log_file, 'w', encoding='utf-8') as f:
                json.dump(pipeline.get_event_log(), f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"[ERROR] Nie udalo sie zapisa dziennika zdarzen: {e}")
            success = False
        
        return success
    
    def save_recovery_info(self, session_id: str, 
                          start_time: datetime, 
                          cycle_count: int = 0) -> bool:
        """
        Zapis informacji do recovery.
        
        Args:
            session_id: Unikalny identyfikator sesji
            start_time: Czas startu sesji
            cycle_count: Liczba wykonanych cykli
            
        Returns:
            Status zapisywania
        """
        recovery_info = {
            'session_id': session_id,
            'start_time': start_time.isoformat(),
            'last_update': datetime.now().isoformat(),
            'cycle_count': cycle_count,
            'mode': 'PRODUCTION',
            'launcher': 'start_ssi.py'
        }
        
        try:
            recovery_file = self.base_dir / self.config["files"]["recovery_info"]
            with open(recovery_file, 'w', encoding='utf-8') as f:
                json.dump(recovery_info, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"[ERROR] Nie udalo sie zapisa recovery_info: {e}")
            return False


# ============================================================================
# PRODUCTION LAUNCHER
# ============================================================================

class ProductionLauncher:
    """
    Produkcyjny launcher dla SSI V5.
    Uruchamia Pipeline w trybie PRODUCTION.
    """
    
    def __init__(self, config: dict = None):
        """
        Inicjalizacja ProductionLauncher.
        
        Args:
            config: Konfiguracja launchera
        """
        self.config = config or CONFIG_PRODUCTION
        self.pipeline = None
        self.time_manager = None
        self.state_manager = None
        self.recovery_manager = None
        self.session_id = None
        self.start_time = None
        self.end_time = None
        self.running = False
        
        # ETAP 1.2.7.3: Memory Integration
        self.ifc = None
        self.memory_ecosystem = None
        self.memory_integrator = None
        
    def initialize(self) -> dict:
        """
        Inicjalizacja systemu z recovery.
        
        ETAP 1.2.7.3: Kolejność bootstrapu:
        TimeManager -> StateManager -> RecoveryManager -> IFCRegistry ->
        MemoryEcosystem -> MemoryIntegrator -> SSIPipeline
        
        Returns:
            Status inicjalizacji
        """
        print("=" * 80)
        print("SSI V5 PRODUCTION LAUNCHER - ETAP 1.2.7.3")
        print("Adaptive Knowledge Ecosystem")
        print("=" * 80)
        
        self.start_time = datetime.now()
        self.session_id = f"SSI_PROD_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Inicjalizacja managerow (TimeManager, StateManager, RecoveryManager)
        self.recovery_manager = RecoveryManager(config=self.config)
        self.state_manager = StateManager(config=self.config)
        self.time_manager = TimeManager(
            max_runtime_hours=self.config["max_runtime_hours"],
            time_buffer_minutes=self.config["time_buffer_minutes"]
        )
        
        # Sprawdzenie recovery
        recovery_needed = self.recovery_manager.check_for_recovery()
        
        if recovery_needed:
            print("[INFO] Wykryto stan do recovery - odzysk po restarcie")
            recovery_data = self.recovery_manager.get_recovery_start_data()
            print(f"[INFO] Poprzednia sesja: {recovery_data.get('previous_session', 'unknown')}")
            print(f"[INFO] Odzysk z: {recovery_data.get('restart_timestamp', 'unknown')}")
        else:
            print("[INFO] Nowa sesja - brak recovery")
        
        # ETAP 1.2.7.3: Inicjalizacja IFCRegistry
        # IFC jest magistrala komunikacji - musi istniec przed MemoryEcosystem
        try:
            self.ifc = IFCRegistry()
            
            # Rejestracja IFC w samym sobie (platform/IFC bus)
            self.ifc.register(
                "ifc_registry",
                self.ifc,
                component_type="system"
            )
            print("[INFO] IFCRegistry zainicjalizowany")
        except Exception as e:
            return {
                'status': 'error',
                'error': f"IFCRegistry initialization failed: {e}",
                'traceback': traceback.format_exc(),
                'step': 'ifc_initialization'
            }
        
        # ETAP 1.2.7.3: Inicjalizacja MemoryEcosystem
        # MemoryEcosystem jest orkiestratorem pamięci, otrzymuje IFC do tez publikacji zdarzeń
        try:
            self.memory_ecosystem = MemoryEcosystem(
                ifc=self.ifc
            )
            
            # Rejestracja w IFC (MemoryEcosystem nie rejestruje się sam)
            self.ifc.register(
                "memory_ecosystem",
                self.memory_ecosystem,
                component_type="memory"
            )
            print("[INFO] MemoryEcosystem zainicjalizowany")
        except Exception as e:
            return {
                'status': 'error',
                'error': f"MemoryEcosystem initialization failed: {e}",
                'traceback': traceback.format_exc(),
                'step': 'memory_ecosystem_initialization'
            }
        
        # ETAP 1.2.7.3: Inicjalizacja MemoryIntegrator
        # MemoryIntegrator jest warstwa wejscia, otrzymuje MemoryEcosystem i IFC
        try:
            self.memory_integrator = MemoryIntegrator(
                memory_ecosystem=self.memory_ecosystem,
                ifc=self.ifc
            )
            # MemoryIntegrator rejestruje się sam w __init__, nie Hayes celle robimy to drugą raz
            print("[INFO] MemoryIntegrator zainicjalizowany")
        except Exception as e:
            return {
                'status': 'error',
                'error': f"MemoryIntegrator initialization failed: {e}",
                'traceback': traceback.format_exc(),
                'step': 'memory_integrator_initialization'
            }
        
        # Inicjalizacja Pipeline - otrzymuje IFC i MemoryEcosystem
        # Pipeline NIE otrzymuje MemoryIntegrator (zgodnie z kontrakcie architektoniczny)
        try:
            # Opóźnione importy, aby uniknąć circular imports
            from SSI_V5.core.pipeline import SSIPipeline, PipelineMode
            
            # Konwersja string mode do PipelineMode enum
            mode = self.config["pipeline_mode"]
            if isinstance(mode, str):
                mode = PipelineMode[mode.upper()]
            
            self.pipeline = SSIPipeline(
                mode=mode,
                world_name=self.config["world_name"],
                ifc=self.ifc,
                memory_ecosystem=self.memory_ecosystem
            )
            
            # Inicjalizacja Pipeline
            init_result = self.pipeline.initialize()
            
            if init_result.get('status') != 'success':
                return {
                    'status': 'error',
                    'error': init_result.get('error', 'Unknown initialization error'),
                    'step': 'pipeline_initialization'
                }
            
            # Rejestracja Pipeline w IFC
            self.ifc.register(
                "pipeline",
                self.pipeline,
                component_type="system"
            )
            
            # Inicjalizacja czasu
            self.time_manager.initialize(start_time=self.start_time)
            
            # Zapis informacji o sesji
            self.state_manager.save_recovery_info(
                session_id=self.session_id,
                start_time=self.start_time,
                cycle_count=0
            )
            
            print(f"[INFO] Pipeline zainicjalizowany: {init_result.get('pipeline_status', 'unknown')}")
            print(f"[INFO] Sesja: {self.session_id}")
            print(f"[INFO] Maksymalny czas pracy: {self.config['max_runtime_hours']} godzin")
            
            # Pokaz podsumowanie czasu
            time_summary = self.time_manager.get_time_summary()
            print(f"[INFO] Planowane zakonczenie: {time_summary['end_time']}")
            
            return {
                'status': 'success',
                'message': 'ProductionLauncher zainicjalizowany pomyslnie (ETAP 1.2.7.3)',
                'pipeline_status': init_result,
                'session_id': self.session_id,
                'recovery_mode': recovery_needed,
                'memory_ecosystem_status': self.memory_ecosystem.health() if self.memory_ecosystem else None,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'traceback': traceback.format_exc(),
                'step': 'launcher_initialization'
            }
    
    def run_production_cycle(self) -> dict:
        """
        Wykonanie pojedynczego cyklu produkcyjnego.
        
        Returns:
            Wynik cyklu
        """
        if not self.pipeline or not self.pipeline._initialized:
            return {
                'status': 'error',
                'error': 'Pipeline not initialized',
                'timestamp': datetime.now().isoformat()
            }
        
        # Generacja unikalnej nazwy swiata
        cycle_world_name = f"{self.config['world_name']}_CYCLE_{len(self.pipeline.cycle_history) + 1}"
        
        # Wykonaj pojedynczy cykl
        cycle_result = self.pipeline.run_cycle(world_name=cycle_world_name)
        
        # Aktualizacja informacji o sesji
        cycle_count = len(self.pipeline.cycle_history)
        self.state_manager.save_recovery_info(
            session_id=self.session_id,
            start_time=self.start_time,
            cycle_count=cycle_count
        )
        
        return cycle_result
    
    def run_production(self) -> dict:
        """
        Glowna petla produkcyjna.
        
        Returns:
            Podsumowanie wykonania
        """
        if not self.pipeline or not self.pipeline._initialized:
            return {
                'status': 'error',
                'error': 'Pipeline not initialized',
                'timestamp': datetime.now().isoformat()
            }
        
        print(f"\n[INFO] Rozpoczynanie petli produkcyjnej...")
        print(f"[INFO] Limit czasu: {self.config['max_runtime_hours']} godzin")
        
        summary = {
            'status': 'success',
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'session_id': self.session_id,
            'total_cycles': 0,
            'successful_cycles': 0,
            'failed_cycles': 0,
            'cycle_results': [],
            'recovery_enabled': True
        }
        
        self.running = True
        
        try:
            while self.running and self.time_manager.should_continue():
                # Sprawdz czasu
                time_summary = self.time_manager.get_time_summary()
                
                # Pokaz progress co 10 cykli
                cycle_count = len(self.pipeline.cycle_history)
                if cycle_count % 10 == 0:
                    remaining_minutes = time_summary['remaining_minutes']
                    elapsed_hours = time_summary['elapsed_hours']
                    print(f"\n[INFO] Progress: {cycle_count} cykli | "
                          f"Czas: {elapsed_hours:.2f}h | "
                          f"Pozostalo: {remaining_minutes:.1f}m")
                
                # Wykonaj cykl
                cycle_result = self.run_production_cycle()
                
                summary['cycle_results'].append({
                    'cycle_index': len(summary['cycle_results']) + 1,
                    'cycle_id': cycle_result.get('cycle_id'),
                    'status': cycle_result.get('status'),
                    'duration': cycle_result.get('duration'),
                    'timestamp': datetime.now().isoformat()
                })
                
                if cycle_result.get('status') == 'success':
                    summary['successful_cycles'] += 1
                else:
                    summary['failed_cycles'] += 1
                    # Logowanie bledu ale kontynuuj
                    print(f"[WARNING] Cykl zakonczony bledem: {cycle_result.get('error', 'unknown')}")
                
                summary['total_cycles'] += 1
                
                # Zapis stanu co 5 cykli
                if cycle_count % 5 == 0:
                    self._save_intermediate_state()
                
                # Opóźnienie pomiedzy cyklami
                time.sleep(self.config['check_interval_seconds'])
            
        except KeyboardInterrupt:
            print("\n[INFO] Otrzymano sygnal przerwania (Ctrl+C)")
        except Exception as e:
            print(f"\n[ERROR] Blad w petli produkcyjnej: {e}")
            print(f"[TRACEBACK] {traceback.format_exc()}")
            summary['status'] = 'error'
            summary['error'] = str(e)
        
        finally:
            self.running = False
            self.end_time = datetime.now()
        
        # Finalne zapisanie stanu
        self._save_intermediate_state()
        
        return summary
    
    def _save_intermediate_state(self) -> bool:
        """Zapis pośredniego stanu systemu."""
        if not self.pipeline:
            return False
        
        # Zapis stanu cyklu
        success = self.state_manager.save_cycle_state(self.pipeline)
        
        # Zapis stanu runtime
        time_summary = self.time_manager.get_time_summary()
        cycle_history = self.pipeline.get_cycle_history() if hasattr(self.pipeline, 'get_cycle_history') else []
        additional_data = {
            'session_id': self.session_id,
            'cycle_count': len(cycle_history),
            'time_elapsed': time_summary['elapsed_seconds']
        }
        
        runtime_success = self.state_manager.save_runtime_state(
            self.pipeline, 
            self.time_manager, 
            additional_data
        )
        
        return success and runtime_success
    
    def shutdown(self) -> dict:
        """
        Graceful shutdown systemu.
        
        ETAP 1.2.7.3: Czyści auch zasoby IFC, MemoryEcosystem, MemoryIntegrator
        
        Returns:
            Status zamkniecia
        """
        print("\n[INFO] Rozpoczynanie graceful shutdown...")
        
        self.running = False
        self.end_time = datetime.now()
        
        # ETAP 1.2.7.3: Shutdown MemoryIntegrator
        if self.memory_integrator:
            try:
                self.memory_integrator.shutdown()
                print("[INFO] MemoryIntegrator zamkniety")
            except Exception as e:
                print(f"[WARNING] Blad podczas zamykania MemoryIntegrator: {e}")
        
        # ETAP 1.2.7.3: Shutdown MemoryEcosystem
        if self.memory_ecosystem:
            try:
                self.memory_ecosystem.shutdown()
                print("[INFO] MemoryEcosystem zamkniety")
            except Exception as e:
                print(f"[WARNING] Blad podczas zamykania MemoryEcosystem: {e}")
        
        # Finalne zapisanie stanu
        self._save_intermediate_state()
        
        # Zamkniecie Pipeline
        try:
            shutdown_result = self.pipeline.shutdown()
            print(f"[INFO] Pipeline zamkniety: {shutdown_result.get('status', 'unknown')}")
        except Exception as e:
            print(f"[WARNING] Blad podczas zamykania Pipeline: {e}")
            shutdown_result = {'status': 'error', 'error': str(e)}
        
        # Podsumowanie
        duration = (self.end_time - self.start_time).total_seconds() if self.start_time else None
        
        print("\n" + "=" * 80)
        print("PRODUCTION LAUNCHER - PODSUMOWANIE")
        print("=" * 80)
        print(f"Sesja: {self.session_id}")
        print(f"Czas startu: {self.start_time.isoformat() if self.start_time else 'N/A'}")
        print(f"Czas zakonczenia: {self.end_time.isoformat() if self.end_time else 'N/A'}")
        print(f"Calkowity czas: {duration:.3f}s ({duration/3600:.2f}h)" if duration else "Calkowity czas: N/A")
        
        if self.pipeline:
            status = self.pipeline.get_status()
            print(f"Liczba cykli: {status.get('total_cycles', 0)}")
            print(f"Udane cykle: {status.get('successful_cycles', 0)}")
            print(f"Bledy: {status.get('failed_cycles', 0)}")
        
        print(f"Status zamkniecia: {shutdown_result.get('status', 'unknown')}")
        print("=" * 80)
        
        return {
            'status': shutdown_result.get('status', 'error'),
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': duration,
            'pipeline_shutdown': shutdown_result,
            'message': 'ProductionLauncher shutdown completed'
        }
    
    def run(self) -> dict:
        """
        Pelny przebieg produkcyjny.
        
        Returns:
            Calkowity wynik uruchomienia
        """
        print("\n" + "=" * 80)
        print("START PRODUCTION LAUNCHER - ETAP 5.2.4 FAZA 3.3.3")
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
        
        # 2. Wykonanie petli produkcyjnej
        try:
            production_result = self.run_production()
        except Exception as e:
            print(f"\n[ERROR] Blad podczas produkcji: {e}")
            print(f"[TRACEBACK] {traceback.format_exc()}")
            production_result = {'status': 'error', 'error': str(e)}
        
        # 3. Shutdown
        shutdown_result = self.shutdown()
        
        # Calkowity wynik
        result = {
            'status': 'success' if all([
                init_result.get('status') == 'success',
                production_result.get('status') == 'success',
                shutdown_result.get('status') == 'success'
            ]) else 'partial_success',
            'steps': {
                'initialization': init_result.get('status', 'error'),
                'production': production_result.get('status', 'error'),
                'shutdown': shutdown_result.get('status', 'error')
            },
            'summary': production_result,
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat()
        }
        
        return result


# ============================================================================
# GLOWNA FUNKCJA
# ============================================================================

def main():
    """Glowna funkcja uruchomieniowa."""
    print("SSI V5 Production Launcher Starting...")
    print("ETAP 5.2.4 FAZA 3.3.3 - Runtime + Life Cycle Integration")
    print(f"Czas: {datetime.now().isoformat()}")
    
    # Tworzenie i uruchomienie launchera
    launcher = ProductionLauncher()
    result = launcher.run()
    
    # Zwroc kod wyjscia
    if result.get('status') == 'success':
        print("\n[SUCCESS] Production Launcher zakonczyl sie pomyslnie!")
        return 0
    elif result.get('status') == 'partial_success':
        print("\n[WARNING] Production Launcher zakonczyl sie z ostrzezeniami!")
        return 1
    else:
        print("\n[ERROR] Production Launcher zakonczyl sie bledem!")
        return 2


if __name__ == "__main__":
    sys.exit(main())
