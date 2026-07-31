#!/usr/bin/env python3
"""
SSI V5 - Start Script
Glowne wywolanie systemu SSI V5

Zgodnie z dokumentacja Sprint 11.5 v2.0:
- Runtime Controller
- Agent Runtime Foundation
- Memory Observation System

Uzycie:
    python start_ssi.py
    
Oczekiwany wynik:
    SSI STARTED
    Runtime: ACTIVE
    Agents: \u2713 Agent_01 ... \u2713 Agent_06
    Collectors: \u2713 V2 \u2713 V3 \u2713 V4 \u2713 External
    Memory: \u2713 Loaded
    
    [Po 5 godzinach]
    SSI SHUTDOWN
    State saved: runtime_state.json
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
        logging.FileHandler(os.path.join(SSI_PATH, 'SSI', 'v5', 'runtime', 'runtime.log'))
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
    print("Runtime Controller - Sprint 11.5")
    print("=" * 60)
    print()


def print_system_status(controller):
    """Wyswietlenie statusu systemu."""
    if controller:
        controller.print_status()
        
        # Dodatkowe informacje o pamieci
        print("Memory: OK Loaded")
        print()


def main():
    """Glowna funkcja uruchomieniowa."""
    print_startup_header()
    
    try:
        from SSI.v5.runtime import create_runtime_controller
        from SSI.v5.runtime.runtime_config import create_default_runtime_config, RuntimeMode
        
        # Utworzenie konfiguracji
        config = create_default_runtime_config()
        
        # Ustaw tryb testowy - domyslnie TEST_MODE = False
        # Aby uruchomic tryb testowy: ustaw config.test_mode = True i config.test_cycles = 10
        # Na przykład dla testu:
        # config.test_mode = True
        # config.test_cycles = 10
        
        # Na razie domyslnie tryb produkcji (5 godzin)
        config.mode = RuntimeMode.PRODUCTION
        config.test_mode = False
        config.test_cycles = 10
        
        # Utworzenie kontrolera
        logger.info("Creating SSI Runtime Controller...")
        controller = create_runtime_controller(config)
        
        # Inicjalizacja systemu
        logger.info("Initializing system...")
        if not controller.initialize():
            logger.error("Failed to initialize SSI Runtime Controller!")
            sys.exit(1)
        
        # Wyswietlenie statusu
        print_system_status(controller)
        
        # Ustawienie obslugi sygnalow
        setup_signal_handlers(controller)
        
        # Uruchomienie glownej petli runtime
        logger.info("Starting main runtime loop...")
        start_time = time.time()
        
        # **GLowna petla - CIAGLY CYKL (Sprint 11.5 v2.0)**
        # Wykonuje sie przez okres do 5 godzin z wielokrotnym wykonywaniem agentow
        if not controller.run_loop():
            logger.error("Runtime loop ended with errors!")
        
        end_time = time.time()
        duration_hours = (end_time - start_time) / 3600
        
        logger.info(f"SSI Runtime completed. Duration: {duration_hours:.2f} hours")
        
        # Zapis stanu
        controller.save_state()
        
        # Wyswietlenie statusu zakonczenia
        print()
        logger.info("SSI Runtime shutdown completed successfully!")
        
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