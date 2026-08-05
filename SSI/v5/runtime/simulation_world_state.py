# SSI V5 - Simulated World State
# ==================================
#
# ETAP: 5.3.4 - Symulacja pelnego cyklu 24H
# Data: 2026-08-04
#
# Odpowiedzialnosc:
# - Dostarczanie symulowanego stanu swiata dla testow
# - Symuluje realne stany swiata w kolejnych momentach dnia
#
# ZASADY:
# - NIE wymuszaj faz - Oddaj realistyczny stan swiata
# - CycleController sam powinien wykryc faze
# - TYLKO do uzycia testowego/symulacyjnego
# - NIE zastępuje rzeczywistego stanu swiata
# - NIE wpisuje sie do Pipeline
# - Uzywane tylko w test_simulation_cycle.py
#
# Autor: SSI V5 System
# Wersja: 1.0.0

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class SimulatedWorldState:
    """
    Symulowany stan swiata dla testow cyklu.
    
    Odpowiedzialnosc:
    - Dostarcza realistyczne dane o stanie swiata w rożnych momentach dnia
    - Umozliwia testowanie detekcji faz przez CycleController
    
    ZASADA: Nie wymuszamy fazy. Oddajemy stan swiata taki jak w rzeczywistosci.
    CycleController powinien sam wykryc faze na podstawie stanu.
    """
    
    # Stan wynikow
    new_results_available: bool = False
    results_processed: bool = False
    
    # Stan swiata
    world_status: str = "UNKNOWN"
    world_is_ready: bool = False
    
    # Stan bazy danych
    database_status: str = "UNKNOWN"
    database_version: str = "1.0.0"
    database_timestamp: Optional[str] = None
    
    # Stan kursow
    odds_available: bool = False
    odds_timestamp: Optional[str] = None
    
    # Stan predykcji
    prediction_cycle_completed: bool = False
    
    # Metadane
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def set_time_based_state(self, hour: int, minute: int) -> None:
        """
        Ustawia stan swiata na podstawie godziny i minuty.
        
        Symuluje typowy przeplyw dzienny:
        - 02:00-02:15: Nowe wyniki dostepne (RESULT_ANALYSIS)
        - 02:15-08:05: Oczekiwanie na generowanie swiata (WORLD_PREPARATION)
        - 08:05-13:00: Swiat gotowy, generowanie kursow (PREDICTION_WINDOW)
        - 13:00-15:07: Predykcja zakonczona (STRATEGY_EVOLUTION)
        - 15:07-21:07: Preparowanie do kolejnj fazy (OPTIMIZATION)
        - 21:07-02:00: Czas oczekiwania (WAITING)
        
        Args:
            hour: Godzina (0-23)
            minute: Minuta (0-59)
        """
        # Resetuj wszystkie flagi do domyslnych
        self.new_results_available = False
        self.results_processed = False
        self.world_status = "UNKNOWN"
        self.world_is_ready = False
        self.database_status = "UNKNOWN"
        self.database_timestamp = None
        self.odds_available = False
        self.odds_timestamp = None
        self.prediction_cycle_completed = False
        
        # 02:00-02:15: Nowe wyniki dostepne (RESULT_ANALYSIS)
        if hour == 2 and minute >= 0 and minute <= 15:
            self.new_results_available = True
            self.results_processed = False
            self.world_status = "UNKNOWN"
            self.world_is_ready = False
            self.database_status = "READY"
            
        # 02:15-08:05: Swiat w przygotowaniu (WORLD_PREPARATION)
        elif (hour == 2 and minute > 15) or (hour >= 3 and hour < 8) or (hour == 8 and minute < 5):
            self.new_results_available = False
            self.results_processed = True
            self.world_status = "GENERATING"
            self.world_is_ready = False
            self.database_status = "GENERATING"
            
        # 08:05-12:59: Swiat gotowy, kursy dostepne (PREDICTION_WINDOW)
        # UWAGA: O 8:05 swiat wciaz sie generuje (GENERATING), gotowosc osiagamy ok. 8:30
        elif (hour == 8 and minute >= 5 and minute < 30) or (hour >= 9 and hour <= 12):
            self.new_results_available = False
            self.results_processed = True
            # O 8:05-8:29: swiat wciaz sie finalizuje
            if hour == 8 and minute < 30:
                self.world_status = "GENERATING"
                self.world_is_ready = False
                self.database_status = "READY"
                self.database_timestamp = datetime.now().isoformat()
                self.odds_available = False  # Kursy nie sa jeszcze gotowe
            else:
                # Od 8:30: swiat gotowy
                self.world_status = "READY"
                self.world_is_ready = True
                self.database_status = "READY"
                self.database_timestamp = datetime.now().isoformat()
                self.odds_available = True
                self.odds_timestamp = datetime.now().isoformat()
            
        # 13:00-15:06: Cykl predykcji zakonczony (STRATEGY_EVOLUTION)
        elif (hour == 13) or (hour == 14) or (hour == 15 and minute < 7):
            self.new_results_available = False
            self.results_processed = True
            self.world_status = "COMPLETED"  # Klucz: nie READY
            self.world_is_ready = False
            self.database_status = "COMPLETED"  # Klucz: nie READY, aby ominac WORLD_PREPARATION
            self.database_timestamp = None  # Klucz: brak timestamp
            self.odds_available = False
            self.prediction_cycle_completed = True
            
        # 15:07-21:06: Optymalizacja (OPTIMIZATION)
        elif (hour == 15 and minute >= 7) or (hour >= 16 and hour <= 20) or (hour == 21 and minute < 7):
            self.new_results_available = False
            self.results_processed = True
            self.world_status = "COMPLETED"  # Klucz: nie READY
            self.world_is_ready = False
            self.database_status = "COMPLETED"  # Klucz: nie READY
            self.database_timestamp = None  # Klucz: brak timestamp
            self.odds_available = False
            self.prediction_cycle_completed = True
            
        # 21:07-02:00: Czas oczekiwania (WAITING)
        else:
            self.new_results_available = False
            self.results_processed = True
            self.world_status = "WAITING"
            self.world_is_ready = False
            self.database_status = "READY"
        
        # Zaktualizuj timestamp
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika dla PhaseDetector."""
        return {
            'new_results_available': self.new_results_available,
            'results_processed': self.results_processed,
            'status': self.world_status,
            'is_ready': self.world_is_ready,
            'database_status': self.database_status,
            'database_version': self.database_version,
            'database_timestamp': self.database_timestamp,
            'odds_available': self.odds_available,
            'odds_timestamp': self.odds_timestamp,
            'prediction_cycle_completed': self.prediction_cycle_completed,
            'timestamp': self.timestamp,
        }
    
    def __repr__(self) -> str:
        return (
            f"SimulatedWorldState("
            f"time={self.timestamp[:16]}, "
            f"world_status={self.world_status}, "
            f"world_ready={self.world_is_ready}, "
            f"results={self.new_results_available}, "
            f"odds={self.odds_available}, "
            f"prediction_done={self.prediction_cycle_completed})"
        )


def create_simulated_world_state_for_time(hour: int, minute: int) -> SimulatedWorldState:
    """
    Fabryka do tworzenia SimulatedWorldState dla danego czasu.
    
    Args:
        hour: Godzina (0-23)
        minute: Minuta (0-59)
    
    Returns:
        Nowa instancja SimulatedWorldState z stanem odpowiadajacym podanemu czasowi
    """
    world_state = SimulatedWorldState()
    world_state.set_time_based_state(hour, minute)
    return world_state
