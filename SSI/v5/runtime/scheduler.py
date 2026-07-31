"""
SSI V5 - Scheduler
Harmonogramowanie zadan w systemie runtime

Zgodnie z dokumentacja Sprint 11.5:
- Runtime Controller
- Agent Runtime Foundation
- Memory Observation System
"""

import time
import threading
import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Union
from enum import Enum
import logging

from .runtime_config import RuntimeConfig, RuntimeConfigManager
from .state_manager import StateManager, RuntimeStatus


class TaskPriority(Enum):
    """Priorytety zadan."""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    BACKGROUND = 1


class TaskStatus(Enum):
    """Statusy zadan."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SchedulerMode(Enum):
    """Tryby pracy schedulera."""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    THREADED = "threaded"


@dataclass
class ScheduledTask:
    """Zadanie zaplanowane do wykonania."""
    
    task_id: str
    name: str
    callback: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    
    # Czas
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[float] = None  # w sekundach
    
    # Priorytet i status
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    
    # Powtarzanie
    repeat: bool = False
    repeat_interval: float = 0.0  # w sekundach
    repeat_count: int = 0
    max_repeats: int = 0
    
    # Bledy
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CycleConfig:
    """Konfiguracja pojedynczego cyklu."""
    
    # Czas
    duration_hours: int = 5
    start_delay: float = 0.0  # opoznienie startu w sekundach
    
    # Zadania w cyklu
    tasks: List[str] = field(default_factory=list)
    task_order: List[str] = field(default_factory=list)
    
    # Warunki
    pre_conditions: List[Callable] = field(default_factory=list)
    post_conditions: List[Callable] = field(default_factory=list)
    
    # Income
    enabled: bool = True
    auto_continue: bool = True


class Scheduler:
    """Scheduler zadan systemu runtime."""
    
    def __init__(self, config: Optional[RuntimeConfig] = None,
                 state_manager: Optional[StateManager] = None):
        self.config = config or RuntimeConfig()
        self.state_manager = state_manager or StateManager(config)
        
        # Tryb pracy
        self.mode = SchedulerMode.SYNCHRONOUS
        
        # Kolekcja zadan
        self._tasks: Dict[str, ScheduledTask] = {}
        self._task_queue: List[str] = []
        self._running_tasks: Dict[str, threading.Thread] = {}
        
        # Flagi
        self._running = False
        self._paused = False
        self._shutdown_requested = False
        
        # Logging
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Metryki
        self._tasks_completed = 0
        self._tasks_failed = 0
        self._total_execution_time = 0.0
        
    def initialize(self) -> None:
        """Inicjalizacja schedulera."""
        self._running = False
        self._paused = False
        self._shutdown_requested = False
        self._tasks = {}
        self._task_queue = []
        self._running_tasks = {}
        
        self._tasks_completed = 0
        self._tasks_failed = 0
        self._total_execution_time = 0.0
        
    def start(self) -> None:
        """Uruchomienie schedulera."""
        if self._running:
            return
            
        self._running = True
        self._paused = False
        
        if self.mode == SchedulerMode.ASYNCHRONOUS:
            self._async_loop = asyncio.new_event_loop()
            self._async_loop.run_until_complete(self._async_run())
        elif self.mode == SchedulerMode.THREADED:
            self._thread = threading.Thread(target=self._threaded_run, daemon=True)
            self._thread.start()
        else:  # SYNCHRONOUS
            self._run_sync()
            
    def stop(self) -> None:
        """Zatrzymanie schedulera."""
        self._running = False
        self._shutdown_requested = True
        
        # Oczekiwanie na zakonczenie zadan
        for task_id, thread in self._running_tasks.items():
            if thread.is_alive():
                thread.join(timeout=5.0)
                
        self._running_tasks.clear()
        
    def pause(self) -> None:
        """Pauzowanie schedulera."""
        self._paused = True
        
    def resume(self) -> None:
        """Wznowienie schedulera."""
        self._paused = False
        
    def shutdown(self) -> None:
        """Wylaczenie schedulera."""
        self.stop()
        self._shutdown_requested = True
        
    def add_task(self, task: ScheduledTask) -> str:
        """Dodanie nowego zadania."""
        if task.task_id in self._tasks:
            raise ValueError(f"Task with ID {task.task_id} already exists")
            
        self._tasks[task.task_id] = task
        self._task_queue.append(task.task_id)
        
        # Sortowanie po priorytecie
        self._sort_task_queue()
        
        return task.task_id
        
    def remove_task(self, task_id: str) -> bool:
        """Usuniecie zadania."""
        if task_id in self._tasks:
            # Zatrzymanie miejscowego zadania
            if task_id in self._running_tasks:
                thread = self._running_tasks[task_id]
                # thread.join() - nie czekaj,nie po prostu usuwaj
                del self._running_tasks[task_id]
                
            del self._tasks[task_id]
            if task_id in self._task_queue:
                self._task_queue.remove(task_id)
                
            return True
        return False
        
    def cancel_task(self, task_id: str) -> bool:
        """Anulowanie zadania."""
        if task_id in self._tasks:
            self._tasks[task_id].status = TaskStatus.CANCELLED
            return True
        return False
        
    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """Pobranie zadania."""
        return self._tasks.get(task_id)
        
    def get_all_tasks(self) -> Dict[str, ScheduledTask]:
        """Pobranie wszystkich zadan."""
        return self._tasks
        
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Pobranie statusu zadania."""
        if task_id in self._tasks:
            return self._tasks[task_id].status
        return None
        
    def create_cycle_tasks(self, data_collector_callback: Optional[Callable] = None,
                          agent_cycle_callback: Optional[Callable] = None,
                          save_state_callback: Optional[Callable] = None) -> List[str]:
        """Utworzenie zadan dla pojedynczego cyklu pracy systemu."""
        task_ids = []
        
        # 1. Inicjalizacja cyklu
        start_cycle_task = ScheduledTask(
            task_id="start_cycle",
            name="Start SSI Cycle",
            callback=self._start_cycle_wrapper,
            priority=TaskPriority.CRITICAL,
            metadata={"cycle_phase": "initialization"}
        )
        self.add_task(start_cycle_task)
        task_ids.append(start_cycle_task.task_id)
        
        # 2. Uruchomienie collectorow
        if data_collector_callback:
            collectors_task = ScheduledTask(
                task_id="run_collectors",
                name="Run Data Collectors",
                callback=data_collector_callback,
                priority=TaskPriority.HIGH,
                metadata={"cycle_phase": "data_collection"}
            )
            self.add_task(collectors_task)
            task_ids.append(collectors_task.task_id)
            
        # 3. Uruchomienie agentow
        if agent_cycle_callback:
            agents_task = ScheduledTask(
                task_id="run_agents",
                name="Run Agent Cycle",
                callback=agent_cycle_callback,
                priority=TaskPriority.HIGH,
                metadata={"cycle_phase": "agent_execution"}
            )
            self.add_task(agents_task)
            task_ids.append(agents_task.task_id)
            
        # 4. Zapis stanu
        if save_state_callback:
            save_task = ScheduledTask(
                task_id="save_state",
                name="Save System State",
                callback=save_state_callback,
                priority=TaskPriority.MEDIUM,
                metadata={"cycle_phase": "finalization"}
            )
            self.add_task(save_task)
            task_ids.append(save_task.task_id)
            
        # 5. Zakonczenie cyklu
        end_cycle_task = ScheduledTask(
            task_id="end_cycle",
            name="End SSI Cycle",
            callback=self._end_cycle_wrapper,
            priority=TaskPriority.CRITICAL,
            metadata={"cycle_phase": "cleanup"}
        )
        self.add_task(end_cycle_task)
        task_ids.append(end_cycle_task.task_id)
        
        return task_ids
        
    def run_full_cycle(self, data_collector_callback: Callable,
                      agent_cycle_callback: Callable,
                      save_state_callback: Callable) -> bool:
        """Wykonanie pelnego cyklu:
        1. Start cyklu
        2. Collectors
        3. Agenci
        4. Zapis stanu
        5. Koniec cyklu
        """
        self.state_manager.start_cycle()
        
        try:
            # Uruchomienie collectorow
            self.logger.info("Running data collectors...")
            result = data_collector_callback()
            self.logger.info(f"Collectors result: {result}")
            
            # Uruchomienie agentow
            self.logger.info("Running agents...")
            result = agent_cycle_callback()
            self.logger.info(f"Agents result: {result}")
            
            # Zapis stanu
            self.logger.info("Saving state...")
            result = save_state_callback()
            self.logger.info(f"Save result: {result}")
            
            self.state_manager.end_cycle()
            return True
            
        except Exception as e:
            self.logger.error(f"Cycling execution error: {e}")
            self.state_manager.set_error(str(e))
            return False
    
    def run_timed_cycle(self, hours: int = 5) -> None:
        """Wykonywanie cyklu przez okreslony czas."""
        self.logger.info(f"Starting timed cycle: {hours} hours")
        self.state_manager.start_cycle()
        
        start_time = time.time()
        end_time = start_time + (hours * 3600)
        
        while time.time() < end_time and self._running and not self._shutdown_requested:
            if not self._paused:
                # Sprawdz, czy sa zadania do wykonania
                if self._task_queue:
                    self._execute_next_task()
                else:
                    # Brak zadan - czekaj
                    time.sleep(1.0)
            else:
                time.sleep(0.1)
                
        self.state_manager.end_cycle()
        
    def _start_cycle_wrapper(self) -> None:
        """Wrapper dla Start cyklu."""
        self.state_manager.start_cycle()
        self.logger.info("Cycle started")
        
    def _end_cycle_wrapper(self) -> None:
        """Wrapper dla End cyklu."""
        self.state_manager.end_cycle()
        self.logger.info("Cycle ended")
        
    def _sort_task_queue(self) -> None:
        """Sortowanie kolejki zadan po priorytecie."""
        def get_priority(task_id: str) -> int:
            if task_id in self._tasks:
                return self._tasks[task_id].priority.value
            return 0
            
        self._task_queue.sort(key=get_priority, reverse=True)
        
    def _execute_next_task(self) -> bool:
        """Wykonywanie nastepnego zadania w kolejce."""
        if not self._task_queue:
            return False
            
        task_id = self._task_queue[0]
        if task_id not in self._tasks:
            self._task_queue.pop(0)
            return False
            
        task = self._tasks[task_id]
        
        # Sprawdzenie statusu
        if task.status != TaskStatus.PENDING and task.status != TaskStatus.SCHEDULED:
            self._task_queue.pop(0)
            return False
            
        # Wykonywanie zadania
        task.status = TaskStatus.RUNNING
        task.start_time = datetime.now().isoformat()
        
        try:
            start_exec = time.time()
            
            if self.mode == SchedulerMode.ASYNCHRONOUS:
                asyncio.run(task.callback(*task.args, **task.kwargs))
            else:
                result = task.callback(*task.args, **task.kwargs)
                
            end_exec = time.time()
            task.duration = end_exec - start_exec
            task.end_time = datetime.now().isoformat()
            task.status = TaskStatus.COMPLETED
            
            self._tasks_completed += 1
            self._total_execution_time += task.duration or 0.0
            
            # Usuniecie z kolejki
            self._task_queue.pop(0)
            
            # Powtarzanie
            if task.repeat and (task.max_repeats == 0 or task.repeat_count < task.max_repeats):
                task.repeat_count += 1
                task.status = TaskStatus.PENDING
                self._task_queue.append(task_id)
                self._sort_task_queue()
                
            return True
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            
            # Retry
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                self._tasks_failed += 1
                
                # Ponowne dodanie do kolejki
                self._task_queue.append(task_id)
                self._sort_task_queue()
                
                return False
            else:
                self._tasks_failed += 1
                self._task_queue.pop(0)
                return False
                
    def _run_sync(self) -> None:
        """Synchronne wykonanie zadan."""
        while self._running and not self._shutdown_requested:
            if not self._paused:
                if self._task_queue:
                    self._execute_next_task()
                else:
                    time.sleep(0.1)
            else:
                time.sleep(0.1)
                
    async def _async_run(self) -> None:
        """Asynchronne wykonanie zadan."""
        while self._running and not self._shutdown_requested:
            if not self._paused:
                if self._task_queue:
                    self._execute_next_task()
                else:
                    await asyncio.sleep(0.1)
            else:
                await asyncio.sleep(0.1)
                
    def _threaded_run(self) -> None:
        """Wykonywanie w watku."""
        while self._running and not self._shutdown_requested:
            if not self._paused:
                if self._task_queue:
                    self._execute_next_task()
                else:
                    time.sleep(0.1)
            else:
                time.sleep(0.1)
                
    def get_metrics(self) -> Dict[str, Any]:
        """Pobranie metryk schedulera."""
        return {
            "total_tasks": len(self._tasks),
            "tasks_completed": self._tasks_completed,
            "tasks_failed": self._tasks_failed,
            "total_execution_time": self._total_execution_time,
            "avg_execution_time": self._total_execution_time / max(self._tasks_completed, 1),
            "running": self._running,
            "paused": self._paused,
            "queue_length": len(self._task_queue)
        }


def create_scheduler(config: Optional[RuntimeConfig] = None,
                    state_manager: Optional[StateManager] = None) -> Scheduler:
    """Tworzenie schedulera."""
    return Scheduler(config, state_manager)


if __name__ == "__main__":
    import logging
    
    # Konfiguracja logowania
    logging.basicConfig(level=logging.INFO)
    
    # Test schedulera
    from .runtime_config import create_default_runtime_config
    
    config = create_default_runtime_config()
    scheduler = create_scheduler(config)
    
    print("Testing Scheduler...")
    
    def test_task_1():
        print("Task 1 executed")
        return True
        
    def test_task_2():
        print("Task 2 executed")
        return True
        
    # Dodanie zadan
    task1 = ScheduledTask(
        task_id="test_1",
        name="Test Task 1",
        callback=test_task_1,
        priority=TaskPriority.HIGH
    )
    
    task2 = ScheduledTask(
        task_id="test_2",
        name="Test Task 2", 
        callback=test_task_2,
        priority=TaskPriority.LOW
    )
    
    scheduler.add_task(task1)
    scheduler.add_task(task2)
    
    print(f"Tasks in queue: {scheduler._task_queue}")
    print(f"Next task: {scheduler._task_queue[0]}")
    
    # Wykonywanie zadan
    scheduler._execute_next_task()
    scheduler._execute_next_task()
    
    metrics = scheduler.get_metrics()
    print(f"Metrics: {metrics}")
    
    print("Scheduler test completed!")