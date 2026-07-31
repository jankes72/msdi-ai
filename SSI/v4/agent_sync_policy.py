"""
SSI V4 Agent Synchronization Policy - Jednolita polityka synchronizacji dla agentów

Odpowiedzialność:
- Definicja locków (RILock, timeouty, konteksty)
- Zasady dostępu do sekcji krytycznych
- Polityka obsługi zakleszczeń i timeoutów

Zgodnie z:
- Sprint 7.3 (Bezpieczeństwo współbieżności V4)
- Wymagania: Niereentrantny lock nie może być przejmowany przez ten sam wątek

Architektura:
┌─────────────────────────────────────────────────────────────┐
│                 AGENT SYNC POLICY                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐      ┌─────────────────┐                 │
│  │   RLock         │      │  Timeout        │                 │
│  │  - Reentrantny  │      │  - 2s domyślny  │                 │
│  │  - Bez deadlocka│      │  - Konfigur.    │                 │
│  └─────────────────┘      └─────────────────┘                 │
│         ↓                    ↓                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │               Sekcje krytyczne                         │  │
│  │  - Stan agenta (status, emocje, osobowość)            │  │
│  │  - Historia decyzji (decision_history)                │  │
│  │  - Metryki (metrics)                                   │  │
│  │  - Pamięć prywatna (private_notebook)                 │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ✗ NIE chronione (tylko odczyt):                             │
│    - V3 Memory (WorldMemory, PatternMemory, itd.)            │
│    - Konfiguracja (config)                                   │
│    - ID, typ, room_id                                       │
└─────────────────────────────────────────────────────────────┘

Wersja: 1.0
Data: 2026-07-31
"""

import threading
import logging
from typing import Optional, Callable, Any, Dict
from functools import wraps
import time

logger = logging.getLogger(__name__)


# ==========================================================================
# KONFIGURACJA SYNCHRONIZACJI
# ==========================================================================

class SyncConfig:
    """Konfiguracja synchronizacji dla agentów V4."""
    
    # Czas oczekiwania na lock (w sekundach)
    LOCK_TIMEOUT: float = 2.0  # Domyślny timeout (2s - zgodnie z kryteriami akceptacji)
    
    # Maksymalny czas trwania operacji agenta
    MAX_DECISION_TIME: float = 1.8  # Mniej niż 2s, aby zapewnić margin
    MAX_EVALUATE_TIME: float = 1.5
    MAX_LEARN_TIME: float = 1.5
    
    # Konfiguracja retry
    MAX_RETRIES: int = 1  # Liczba powtórzeń przy timeout
    RETRY_DELAY: float = 0.1  # Opóźnienie między retry


# ==========================================================================
# CUSTOM REENTRANT LOCK Z TIMEOUT
# ==========================================================================

class AgentRLock:
    """
    Reentrantny lock z obsługą timeoutu i logowaniem.
    
    Rozwiązanie problemu:
    - threading.RLock jest reentrantny, ale nie obsługuje timeout w acquire()
    - Ta klasa dodaje timeout i lepsze logowanie.
    """
    
    def __init__(self, name: str = "AgentLock"):
        self._lock = threading.RLock()
        self._name = name
        self._owner_thread: Optional[threading.Thread] = None
        self._acquire_count = 0
        self._last_acquire_time: Optional[float] = None
        
    def acquire(self, timeout: Optional[float] = None, blocking: bool = True) -> bool:
        """
        Próbuje przejąć lock z opcjonalnym timeoutem.
        
        Args:
            timeout: Maksymalny czas oczekiwania (None = czekaj w nieskończoność)
            blocking: Czy blokować (True) czy próba natychmiastowa (False)
            
        Returns:
            True jeśli lock został zdobyty, False jeśli timeout
        """
        start_time = time.time()
        
        try:
            # Jeśli timeout jest None, użyj domyślnego z SyncConfig
            if timeout is None:
                timeout = SyncConfig.LOCK_TIMEOUT
            
            # Jeśli nie blokujący, spróbuj natychmiast
            if not blocking:
                acquired = self._lock.acquire(blocking=False)
                if acquired:
                    self._on_acquire()
                return acquired
            
            # Blokujący z timeoutem
            if timeout <= 0:
                # Natychmiastowa próba
                acquired = self._lock.acquire(blocking=False)
                if acquired:
                    self._on_acquire()
                return acquired
            
            # Oczekiwanie na lock z timeoutem
            end_time = start_time + timeout
            while True:
                remaining = end_time - time.time()
                if remaining <= 0:
                    logger.warning(
                        f"Timeout acquiringu {self._name} po {timeout:.2f}s "
                        f"(current owner: {self._owner_thread.name if self._owner_thread else 'None'})"
                    )
                    return False
                
                # Próba zdobycia locka
                acquired = self._lock.acquire(blocking=True, timeout=min(remaining, 0.01))
                if acquired:
                    self._on_acquire()
                    return True
                
                # Jeśli nie zdobyto, kontynuuj pętlę
                if remaining > 0.01:
                    time.sleep(0.01)
        
        except Exception as e:
            logger.error(f"Błąd przy przejmowaniu {self._name}: {e}")
            return False
    
    def _on_acquire(self) -> None:
        """Wywoływane po zdobytym locku."""
        current_thread = threading.current_thread()
        self._owner_thread = current_thread
        self._acquire_count += 1
        self._last_acquire_time = time.time()
        
        if self._acquire_count == 1:
            logger.debug(f"Lock {self._name} zdobyty przez {current_thread.name}")
        else:
            logger.debug(
                f"Lock {self._name} ponowny acquire ({self._acquire_count}x) "
                f"przez {current_thread.name}"
            )
    
    def release(self) -> None:
        """Zwraca lock."""
        try:
            if self._acquire_count <= 0:
                logger.warning(f"Próba zwolnienia niezajętego locka {self._name}")
                return
            
            self._acquire_count -= 1
            
            if self._acquire_count == 0:
                self._owner_thread = None
                self._last_acquire_time = None
                logger.debug(f"Lock {self._name} zwolniony")
            
            self._lock.release()
        
        except RuntimeError as e:
            # Threading error (np. zwolnienie locka, którego się nie posiada)
            logger.error(f"Błąd zwalniania {self._name}: {e}")
            self._acquire_count = 0
            self._owner_thread = None
            raise
    
    def __enter__(self) -> 'AgentRLock':
        """Context manager - wejście."""
        acquired = self.acquire(timeout=SyncConfig.LOCK_TIMEOUT)
        if not acquired:
            raise RuntimeError(f"Nie udało się zdobyć locka {self._name} w czasie {SyncConfig.LOCK_TIMEOUT}s")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager - wyjście."""
        self.release()
    
    @property
    def is_held(self) -> bool:
        """Czy lock jest aktualnie zajęty."""
        return self._acquire_count > 0
    
    @property
    def owner_thread_name(self) -> str:
        """Nazwa wątku, który posiada lock."""
        return self._owner_thread.name if self._owner_thread else "None"


# ==========================================================================
# DEKORATORY SYNCHRONIZACJI
# ==========================================================================

def with_agent_lock(lock_attr: str = "_lock", timeout: Optional[float] = None):
    """
    Dekorator, który automatycznie zarządza lockiem agenta.
    
    Użycie:
        @with_agent_lock(timeout=2.0)
        def make_decision(self, context):
            ...
    
    Args:
        lock_attr: Nazwa atrybutu locka w instancji
        timeout: Timeout w sekundach (None = domyślny z SyncConfig)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            lock = getattr(self, lock_attr, None)
            if lock is None:
                logger.warning(f"Brak locka {lock_attr} w {self.__class__.__name__}.{func.__name__}")
                return func(self, *args, **kwargs)
            
            # Sprawdź, czy ten wątek już posiada lock (dla RLock)
            if isinstance(lock, (threading.RLock, AgentRLock)):
                start_time = time.time()
                try:
                    acquired = lock.acquire(timeout=timeout)
                    if not acquired:
                        raise RuntimeError(
                            f"Timeout oczekiwania na {lock_attr} w {self.__class__.__name__}.{func.__name__} "
                            f"po {timeout or SyncConfig.LOCK_TIMEOUT}s"
                        )
                    try:
                        result = func(self, *args, **kwargs)
                        return result
                    finally:
                        lock.release()
                except Exception as e:
                    if isinstance(e, RuntimeError) and "Timeout" in str(e):
                        logger.error(
                            f"Timeout synchronizacji w {self.__class__.__name__}.{func.__name__}: {e}"
                        )
                    raise
            
            # Dla zwykłego Lock (niereentrantny - użyj only if nie ma reentry)
            else:
                with lock:
                    return func(self, *args, **kwargs)
        
        return wrapper
    return decorator


def with_timeout(max_time: float, operation_name: str = "operation"):
    """
    Dekorator, który ogranicz czas wykonania metody.
    
    Użycie:
        @with_timeout(2.0, "make_decision")
        def make_decision(self, context):
            ...
    
    Args:
        max_time: Maksymalny czas wykonania w sekundach
        operation_name: Nazwa operacji do logowania
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            start_time = time.time()
            try:
                result = func(self, *args, **kwargs)
                elapsed = time.time() - start_time
                if elapsed > max_time:
                    logger.warning(
                        f"{self.__class__.__name__}.{func.__name__} wykonało się w {elapsed:.3f}s "
                        f"(przekroczyło limit {max_time}s)"
                    )
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    f"Błąd w {operation_name} po {elapsed:.3f}s: {e}"
                )
                raise
        return wrapper
    return decorator


# ==========================================================================
# POLITYKA SYNCHRONIZACJI DLA AGENTÓW
# ==========================================================================

class AgentSyncPolicy:
    """
    Jednolita polityka synchronizacji dla systemu agentów V4.
    
    Zasady:
    1. Używaj RLock zamiast Lock (reentrantny, unika deadlock w tym samym wątku)
    2. Ogranicz czas trwania sekcji krytycznych
    3. Nigdy nie wywołuj publicznych metod agenta z wnętrza sekcji krytycznej
    4. V3 Memory jest tylko do odczytu - nie chronić lockiem agenta
    5. Timeouty na wszystkie operacje blokujące
    
    Obszary chronione:
    - Zmiany stanu agenta (status, emocje, osobowość)
    - Modyfikacja pamięci prywatnej (decision_history, strategies, etc.)
    - Aktualizacja metryk
    
    Obszary NIE chronione (tylko odczyt):
    - V3 Memory (WorldMemory, PatternMemory, etc.)
    - Konfiguracja agenta (config)
    - ID, typ, room_id
    """
    
    # Typy locków
    LOCK_TYPE_RLOCK = "RLock"  # Reentrantny, dla metod, które mogą wywoływać andere metody
    LOCK_TYPE_LOCK = "Lock"    # Niereentrantny, dla prostych sekcji krytycznych
    
    # Poziomy synchronizacji
    LEVEL_NONE = 0      # Brak synchronizacji
    LEVEL_READ = 1      # Synchronizacja tylko dla zapisu
    LEVEL_FULL = 2      # Pełna synchronizacja (odczyt i zapis)
    
    # Polityka dla poszczególnych metod
    METHOD_POLICIES: Dict[str, Dict[str, Any]] = {
        "make_decision": {
            "level": LEVEL_FULL,
            "lock_type": LOCK_TYPE_RLOCK,
            "timeout": 2.0,
            "max_time": 1.8,
            "description": "Pełna synchronizacja, RLock (może wywoływać set_status)"
        },
        "evaluate_result": {
            "level": LEVEL_FULL,
            "lock_type": LOCK_TYPE_RLOCK,
            "timeout": 2.0,
            "max_time": 1.5,
            "description": "Pełna synchronizacja, RLock (aktualizuje metryki i stan)"
        },
        "learn_from_experience": {
            "level": LEVEL_FULL,
            "lock_type": LOCK_TYPE_RLOCK,
            "timeout": 2.0,
            "max_time": 1.5,
            "description": "Pełna synchronizacja, RLock (modyfikuje pamięć)"
        },
        "set_status": {
            "level": LEVEL_FULL,
            "lock_type": LOCK_TYPE_RLOCK,
            "timeout": 1.0,
            "max_time": 0.5,
            "description": "Synchronizacja stanu agenta"
        },
        "initialize": {
            "level": LEVEL_FULL,
            "lock_type": LOCK_TYPE_RLOCK,
            "timeout": 1.0,
            "max_time": 0.5,
            "description": "Inicjalizacja agenta"
        },
        # Metody tylko do odczytu - bez synchronizacji
        "get_world_memory": {
            "level": LEVEL_NONE,
            "lock_type": None,
            "timeout": None,
            "description": "Tylko odczyt V3 Memory"
        },
        "get_pattern_memory": {
            "level": LEVEL_NONE,
            "lock_type": None,
            "timeout": None,
            "description": "Tylko odczyt V3 Memory"
        },
        "get_metadata_memory": {
            "level": LEVEL_NONE,
            "lock_type": None,
            "timeout": None,
            "description": "Tylko odczyt V3 Memory"
        },
    }
    
    @classmethod
    def get_policy(cls, method_name: str) -> Dict[str, Any]:
        """Zwraca politykę synchronizacji dla metody."""
        return cls.METHOD_POLICIES.get(method_name, {
            "level": cls.LEVEL_FULL,
            "lock_type": cls.LOCK_TYPE_RLOCK,
            "timeout": SyncConfig.LOCK_TIMEOUT,
            "max_time": SyncConfig.MAX_DECISION_TIME,
            "description": "Domyślna polityka - pełna synchronizacja"
        })
    
    @classmethod
    def should_sync(cls, method_name: str) -> bool:
        """Czy metoda powinna być synchronizowana."""
        policy = cls.get_policy(method_name)
        return policy.get("level", cls.LEVEL_FULL) != cls.LEVEL_NONE


# ==========================================================================
# WSPÓŁDZIELENE ZASOBY (Singleton)
# ==========================================================================

# Globalny lock manager (opcjonalnie)
_global_sync_manager = None
_global_sync_manager_lock = threading.Lock()


class AgentSyncManager:
    """
    Manager synchronizacji dla całej populacji agentów.
    
    Zapewnia:
    - Globalne locki dla operacji popuacyjicznych
    - Monitorowanie zakleszczeń
    - Statystyki synchronizacji
    """
    
    def __init__(self):
        self._agents_lock = AgentRLock("AgentsLock")
        self._statistics = {
            "lock_timeouts": 0,
            "deadlocks_detected": 0,
            "operations_completed": 0,
            "operations_failed": 0
        }
    
    @property
    def agents_lock(self) -> AgentRLock:
        """Lock dla operacji na całej populacji agentów."""
        return self._agents_lock
    
    def record_timeout(self) -> None:
        """Rejestruje timeout locka."""
        self._statistics["lock_timeouts"] += 1
    
    def record_deadlock(self) -> None:
        """Rejestruje wykryte zakleszczenie."""
        self._statistics["deadlocks_detected"] += 1
    
    def record_operation(self, success: bool = True) -> None:
        """Rejestruje wynik operacji."""
        if success:
            self._statistics["operations_completed"] += 1
        else:
            self._statistics["operations_failed"] += 1
    
    def get_statistics(self) -> Dict[str, int]:
        """Zwraca statystyki synchronizacji."""
        return self._statistics.copy()


def get_sync_manager() -> AgentSyncManager:
    """Zwraca globalnego menedżera synchronizacji."""
    global _global_sync_manager
    if _global_sync_manager is None:
        with _global_sync_manager_lock:
            if _global_sync_manager is None:
                _global_sync_manager = AgentSyncManager()
    return _global_sync_manager
