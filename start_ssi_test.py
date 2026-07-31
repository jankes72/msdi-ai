#!/usr/bin/env python3
"""
SSI V5 - Start Script (TEST MODE)
Testowe uruchomienie systemu SSI V5 w trybie testowym

Uzycie:
    python start_ssi_test.py
    
Oczekiwany wynik:
    SSI STARTED
    Runtime: ACTIVE
    ... (10 cykli x 6 agentow = 60 iteracji)
    SSI SHUTDOWN
    State saved: runtime_state.json
    
Wykonuje 10 pelnych cykli, kazdy cykl to:
    Agent_01 -> Agent_02 -> Agent_03 -> Agent_04 -> Agent_05 -> Agent_06
"""

import sys
import os
import logging
import time
import signal
from datetime import datetime

# Dodanie sciezki do SSI do sys.path
SSI_PATH = os.path.dirname(os.path.abspath(__file__))
if SSI_PATH not in sys.path:
    sys.path.insert(0, SSI_PATH)

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(SSI_PATH, 'SSI', 'v5', 'runtime', 'runtime_test.log'))
    ]
)

logger = logging.getLogger(__name__)


def setup_signal_handlers(controller):
    """Ustawienie obslugi sygnalow (Ctrl+C itp.)."""
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, shutting down gracefully...")
        controller.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame))
    signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(sig, frame))


def print_startup_header():
    """Wyswietlenie naglowka startowego."""
    print("=" * 60)
    print("SSI V5 - Self Learning Intelligence System")
    print("Runtime Controller - Sprint 11.5 - TEST MODE")
    print("=" * 60)
    print()


def print_test_summary(controller, start_time):
    """Wyswietlenie podsumowania testu."""
    end_time = time.time()
    duration_seconds = end_time - start_time
    duration_minutes = duration_seconds / 60
    
    status = controller.get_status()
    
    print("=" * 60)
    print("TEST MODE SUMMARY")
    print("=" * 60)
    print(f"Duration: {duration_seconds:.2f} seconds ({duration_minutes:.2f} minutes)")
    
    if 'runtime_state' in status:
        rs = status['runtime_state']
        print(f"Total Cycles: {rs.get('total_cycles', 0)}")
        print(f"Total Iterations: {rs.get('metadata', {}).get('total_iterations', 0)}")
        print(f"Expected: 10 cycles x 6 agents = 60 iterations")
    
    print()
    
    # Sprawdzenie czy pamiec zostala zapisana
    memory_path = os.path.join(SSI_PATH, 'SSI', 'memory', 'agents')
    if os.path.exists(memory_path):
        agent_dirs = [d for d in os.listdir(memory_path) if d.startswith('agent_')]
        print(f"Memory saved for agents: {', '.join(sorted(agent_dirs))}")
        
        for agent_dir in sorted(agent_dirs):
            agent_files = os.listdir(os.path.join(memory_path, agent_dir))
            if agent_files:
                print(f"  {agent_dir}: {len(agent_files)} memory files")
    
    print()
    print("State saved: runtime_state.json")
    print("=" * 60)


def main():
    """Glowna funkcja uruchomieniowa - TEST MODE."""
    print_startup_header()
    
    try:
        from SSI.v5.runtime import create_runtime_controller
        from SSI.v5.runtime.runtime_config import create_default_runtime_config, RuntimeMode
        
        # Utworzenie konfiguracji dla trybu testowego
        config = create_default_runtime_config()
        config.mode = RuntimeMode.TEST
        config.test_mode = True
        config.test_cycles = 10
        config.auto_save = True
        config.memory_persistence = True
        
        # Utworzenie kontrolera
        logger.info("Creating SSI Runtime Controller (TEST MODE)...")
        controller = create_runtime_controller(config)
        
        # Inicjalizacja systemu
        logger.info("Initializing system...")
        if not controller.initialize():
            logger.error("Failed to initialize SSI Runtime Controller!")
            sys.exit(1)
        
        # Wyswietlenie statusu
        print("Runtime Controller initialized in TEST MODE")
        print(f"Test Cycles: {config.test_cycles}")
        print(f"Expected Iterations: {config.test_cycles * 6}")
        print()
        
        # Ustawienie obslugi sygnalow
        setup_signal_handlers(controller)
        
        # Uruchomienie glownej petli runtime - TEST MODE
        logger.info("Starting main runtime loop in TEST MODE...")
        start_time = time.time()
        
        if not controller.run_loop():
            logger.error("Runtime loop ended with errors!")
        
        end_time = time.time()
        duration_hours = (end_time - start_time) / 3600
        
        logger.info(f"SSI Runtime TEST completed. Duration: {duration_hours:.2f} hours")
        
        # Zapis stanu
        controller.save_state()
        
        # Wyswietlenie podsumowania testu
        print_test_summary(controller, start_time)
        
        # Wyswietlenie statusu zakonczenia
        print()
        logger.info("SSI Runtime TEST shutdown completed successfully!")
        
        return 0
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        print(f"ERROR: Failed to import SSI modules: {e}")
        print("Please ensure all SSI modules are installed correctly.")
        return 1
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        print("=" * 60)


# Wywolanie glowne
if __name__ == "__main__":
    sys.exit(main())
