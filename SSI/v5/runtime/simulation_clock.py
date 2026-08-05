# SSI V5 - Simulation Clock
# ==================================
#
# ETAP: 5.3.4 - Symulacja pełnego cyklu 24H
# Data: 2026-08-04
#
# Odpowiedzialnosc:
# - Dostarczanie symulowanego czasu dla testow
# - Przesuwanie czasu z przyspieszeniem
# - Umozliwienie testowania pelnego cyklu 24H w krotkim czasie
#
# ZASADY:
# - TYLKO dostawca czasu, NIE zarządza fazami
# - NIE zastępuje V1 scheduler
# - NIE steruje pipeline
# - NIE uruchamia agentow
# - Wyłacznie do uzycia testowego/symulacyjnego
#
# Autor: SSI V5 System
# Wersja: 1.0.0

from datetime import datetime, timedelta
from typing import Optional, List, Generator
import time


class SimulationClock:
    """
    Zegar symulacyjny dla testow cyklu 24H.
    
    Odpowiedzialnosc:
    - Przechowywanie aktualnego czasu symulacji
    - Ustawianie czasu na dowolna wartosc
    - Przesuwanie czasu o okreslona ilosc minut/sekund
    - Przyspieszanie symulacji (speed_factor > 1.0)
    
    ZASADA: Tylko dostarcza czas, NIE ingeruje w logike biznesowa.
    """
    
    def __init__(self, start_time: Optional[datetime] = None):
        """
        Inicjalizacja zegara symulacyjnego.
        
        Args:
            start_time: Poczatkowy czas symulacji. Domyslnie teraz.
        """
        self.start_time = start_time or datetime.now()
        self._current_time = self.start_time
        self.speed_factor = 1.0  # 1.0 = czas rzeczywisty, >1.0 = przyspieszony
        self._last_update: Optional[datetime] = None
    
    @property
    def current_time(self) -> datetime:
        """Aktualny czas symulacji."""
        return self._current_time
    
    def set_time(self, new_time: datetime) -> None:
        """
        Ustawienie czasu symulacji na konkretna wartosc.
        
        Args:
            new_time: Nowy czas symulacji
        """
        self._current_time = new_time
        self._last_update = datetime.now()
    
    def advance_time(self, minutes: int) -> None:
        """
        Przesuniecie czasu o podana ilosc minut.
        
        Args:
            minutes: Ilosc minut do przesuniecia (moze byc ujemna)
        """
        self._current_time += timedelta(minutes=minutes)
        self._last_update = datetime.now()
    
    def advance_seconds(self, seconds: int) -> None:
        """
        Przesuniecie czasu o podana ilosc sekund.
        
        Args:
            seconds: Ilosc sekund do przesuniecia (moze byc ujemna)
        """
        self._current_time += timedelta(seconds=seconds)
        self._last_update = datetime.now()
    
    def get_current_time(self) -> datetime:
        """
        Pobranie aktualnego czasu symulacji.
        
        Returns:
            Aktualny czas symulacji
        """
        return self._current_time
    
    def set_speed_factor(self, speed: float) -> None:
        """
        Ustawienie wspolczynnika przyspieszenia symulacji.
        
        Args:
            speed: Wspolczynnik przyspieszenia (1.0 = normalny, 100.0 = 100x)
        """
        if speed <= 0:
            raise ValueError("Speed factor must be positive")
        self.speed_factor = speed
    
    def get_speed_factor(self) -> float:
        """Pobranie aktualnego wspolczynnika przyspieszenia."""
        return self.speed_factor
    
    def reset(self) -> None:
        """Reset zegara do poczatkowego czasu symulacji."""
        self._current_time = self.start_time
        self.speed_factor = 1.0
        self._last_update = datetime.now()
    
    def simulate_day(
        self, 
        start_hour: int = 2, 
        start_minute: int = 7,
        speed: float = 100.0
    ) -> Generator[datetime, None, None]:
        """
        Generator symulujacy pelny dzien (24h) z podanym przyspieszeniem.
        
        Args:
            start_hour: Godzina startu (domyslnie 2 = 02:07)
            start_minute: Minuta startu (domyslnie 7)
            speed: Wspolczynnik przyspieszenia (domyslnie 100x)
        
        Yields:
            Kolejne chwile czasu w symulowanym dniu
        
        Uzycie:
            for current_time in sim_clock.simulate_day(start_hour=2, start_minute=7, speed=100):
                # Tutaj mozna testowac fazy
                pass
        """
        # Ustaw poczatek symulacji
        self.set_time(datetime(
            self.start_time.year, 
            self.start_time.month, 
            self.start_time.day, 
            start_hour, 
            start_minute, 
            0
        ))
        self.set_speed_factor(speed)
        
        # Symuluj kazda minute przez 24 godziny
        total_minutes = 24 * 60
        for minute in range(total_minutes + 1):
            current = self.get_current_time()
            yield current
            self.advance_time(1)
    
    def get_phase_test_times(self) -> List[datetime]:
        """
        Pobranie kluczowych momentow czasu dla testowania faz.
        
        Returns:
            Lista datetimow dla kluczowych momentow w symulowanym dniu
        """
        base_date = self.start_time.date()
        return [
            # 02:07 - RESULT_ANALYSIS
            datetime.combine(base_date, datetime.min.time()).replace(hour=2, minute=7, second=0),
            # 08:05 - WORLD_PREPARATION
            datetime.combine(base_date, datetime.min.time()).replace(hour=8, minute=5, second=0),
            # 13:00 - PREDICTION_WINDOW (przykladowy czas)
            datetime.combine(base_date, datetime.min.time()).replace(hour=13, minute=0, second=0),
            # 15:07 - STRATEGY_EVOLUTION
            datetime.combine(base_date, datetime.min.time()).replace(hour=15, minute=7, second=0),
            # 21:07 - OPTIMIZATION
            datetime.combine(base_date, datetime.min.time()).replace(hour=21, minute=7, second=0),
        ]
    
    def __repr__(self) -> str:
        return (
            f"SimulationClock(current_time={self._current_time.isoformat()}, "
            f"speed_factor={self.speed_factor})"
        )


def create_simulation_clock(start_time: Optional[datetime] = None) -> SimulationClock:
    """
    Fabryka do tworzenia SimulationClock.
    
    Args:
        start_time: Poczatkowy czas symulacji
    
    Returns:
        Nowa instancja SimulationClock
    """
    return SimulationClock(start_time=start_time)
