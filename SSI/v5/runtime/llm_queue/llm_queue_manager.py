"""
SSI V5 - LLM Queue Manager
Glowny manager kolejki modeli LLM

Zgodnie z dokumentacja:
- 06_AI_LAB_REQUEST_PIPELINE.md Sekcja 6.1, 6.2
- 01_SYSTEM_SIGNAL_ARCHITECTURE.md (Ograniczenia sprzetowe)

ZASADA: TYLKO JEDEN MODEL LLM MOZE BYC AKTYWNY
Wzorzec: MODEL START -> WORK -> SAVE MEMORY -> MODEL STOP -> NEXT MODEL

Odpowiedzialnosc:
- Zarzadzanie kolejka zadan LLM z priorytetami
- Ograniczenie do 1 aktywnego modelu na raz
- Sekwencyjne wykonywanie: MODEL START -> WORK -> SAVE MEMORY -> MODEL STOP
- Monitorowanie zasobow (pamiec, GPU)
- Obsluga przerwan (tylko CRITICAL)
- Zapis pamieci miedzy modelami
"""

import os
import sys
import time
import json
import logging
import threading
import queue as python_queue
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field

# Dodanie sciezki do SSI do sys.path
SSI_PATH = "D:\\sts\\aplikacjaTyperBetAi\\SSI"
if SSI_PATH not in sys.path:
    sys.path.insert(0, SSI_PATH)

from .model_context import (
    ModelContext, ModelRequest, ModelResult, ModelStatus, 
    ModelPriority, ModelType
)
from .queue_config import (
    LLMQueueSettings, HardwareConstraints, ModelLimits,
    MemoryCleanupStrategy, QueueMode, create_default_queue_config
)

logger = logging.getLogger(__name__)


class LLMQueueError(Exception):
    """Blad kolejki LLM."""
    pass


class QueueFullError(LLMQueueError):
    """Kolejka jest pelna."""
    pass


class ModelNotAvailableError(LLMQueueError):
    """Model nie jest dostepny."""
    pass


class HardwareLimitError(LLMQueueError):
    """Osiagnieto limit sprzetowy."""
    pass


@dataclass
class QueueStatistics:
    """Statystyki kolejki LLM."""
    
    # Liczniki
    total_requests: int = 0
    completed_requests: int = 0
    failed_requests: int = 0
    timedout_requests: int = 0
    interrupted_requests: int = 0
    
    # Czas
    total_processing_time: float = 0.0
    avg_processing_time: float = 0.0
    min_processing_time: float = float('inf')
    max_processing_time: float = 0.0
    
    # Zamieci
    longest_queue_length: int = 0
    current_queue_length: int = 0
    
    # Aktywny model
    current_model: Optional[str] = None
    current_model_start_time: Optional[str] = None
    
    # Historia
    completed_model_types: Dict[str, int] = field(default_factory=dict)
    failed_model_types: Dict[str, int] = field(default_factory=dict)
    
    def update_queue_length(self, length: int) -> None:
        """Aktualizacja dlugosci kolejki."""
        self.current_queue_length = length
        self.longest_queue_length = max(self.longest_queue_length, length)
    
    def add_completed(self, model_type: str, processing_time: float) -> None:
        """Dodanie zakonczonego zadania."""
        self.completed_requests += 1
        self.total_requests += 1
        self.total_processing_time += processing_time
        self.min_processing_time = min(self.min_processing_time, processing_time)
        self.max_processing_time = max(self.max_processing_time, processing_time)
        
        if processing_time > 0:
            self.avg_processing_time = self.total_processing_time / self.completed_requests
        
        self.completed_model_types[model_type] = \
            self.completed_model_types.get(model_type, 0) + 1
    
    def add_failed(self, model_type: str, error_type: str = "error") -> None:
        """Dodanie nieudanych zadania."""
        self.failed_requests += 1
        self.total_requests += 1
        
        if error_type == "timeout":
            self.timedout_requests += 1
        elif error_type == "interrupted":
            self.interrupted_requests += 1
            
        self.failed_model_types[model_type] = \
            self.failed_model_types.get(model_type, 0) + 1


class LLMQueueConfig:
    """Konfiguracja kolejki LLM (kompatybilnosc wsteczna)."""
    
    def __init__(self, 
                 max_active_models: int = 1,
                 queue_mode: QueueMode = QueueMode.PRIORITY,
                 cleanup_strategy: MemoryCleanupStrategy = MemoryCleanupStrategy.BASIC):
        self.max_active_models = max_active_models
        self.queue_mode = queue_mode
        self.cleanup_strategy = cleanup_strategy
    
    @classmethod
    def from_settings(cls, settings: LLMQueueSettings) -> 'LLMQueueConfig':
        """Tworzenie z LLMQueueSettings."""
        return cls(
            max_active_models=settings.hardware.max_active_models,
            queue_mode=settings.mode,
            cleanup_strategy=settings.hardware.cleanup_strategy
        )


class ModelExecutor:
    """Wykonawca modelu LLM.
    
    Odpowiedzialny za:
    1. MODEL START
    2. WORK
    3. SAVE MEMORY  
    4. MODEL STOP
    """
    
    def __init__(self, config: LLMQueueSettings):
        self.config = config
        self._current_model: Optional[ModelContext] = None
        self._executing = False
        self._stop_requested = False
        
    def execute(self, context: ModelContext) -> ModelResult:
        """Wykonanie modelu wedlug wzorca.
        
        Wzorec:
        1. MODEL START
        2. WORK  
        3. SAVE MEMORY
        4. MODEL STOP
        """
        self._current_model = context
        self._executing = True
        self._stop_requested = False
        
        try:
            # 1. MODEL START
            logger.info(f"MODEL START: {context.request.request_id} ({context.request.model_type.value})")
            context.start()
            self._prepare_model(context)
            
            # Sprawdz czy jest wystarczajaco pamieci
            if not self._check_hardware_constraints(context):
                raise HardwareLimitError("Insufficient hardware resources")
            
            # 2. WORK
            logger.info(f"WORK: {context.request.request_id}")
            context.begin_work()
            result = self._execute_model(context)
            
            # 3. SAVE MEMORY
            logger.info(f"SAVE MEMORY: {context.request.request_id}")
            context.begin_save_memory()
            self._save_memory(context, result)
            result.memory_saved = True
            
            # 4. MODEL STOP
            logger.info(f"MODEL STOP: {context.request.request_id}")
            context.stop()
            
            # Zakonczenie
            context.complete(result)
            return result
            
        except Exception as e:
            logger.error(f"Error executing {context.request.request_id}: {e}")
            context.set_error(str(e))
            result = ModelResult(
                request_id=context.request.request_id,
                status=ModelStatus.ERROR,
                error_message=str(e)
            )
            return result
        finally:
            self._cleanup_model(context)
            self._current_model = None
            self._executing = False
    
    def _prepare_model(self, context: ModelContext) -> None:
        """Przygotowanie modelu (MODEL START)."""
        # Wywol callback on_start
        if context.request.on_start:
            try:
                context.request.on_start(context.request.request_id)
            except Exception as e:
                logger.warning(f"Error in on_start callback: {e}")
        
        # Logowanie
        if self.config.log_model_operations:
            logger.info(f"Prepared model {context.request.model_name} for {context.request.model_type.value}")
    
    def _execute_model(self, context: ModelContext) -> ModelResult:
        """Wykonanie pracy modelu (WORK).
        
        TO DO: Tutaj bedzie integracja z rzeczywistymi modelami LLM
        (Mistral, Llama, itp.)
        
        Tymczasowo: symulacja
        """
        request = context.request
        start_time = datetime.now().isoformat()
        
        # Symulacja pracy modelu
        time.sleep(0.1)  # Symulacja opoznienia
        
        # Generowanie fake response
        response = self._generate_fake_response(request)
        
        end_time = datetime.now().isoformat()
        
        # Tworzenie wyniku
        result = ModelResult(
            request_id=request.request_id,
            response=response,
            model_name=request.model_name,
            model_type=request.model_type,
            task_type=request.task_type,
            start_time=start_time,
            end_time=end_time,
            prompt_tokens=context.request.estimated_tokens,
            completion_tokens=len(response.split()) * 4,
            total_tokens=context.request.estimated_tokens + len(response.split()) * 4
        )
        
        # Wywol callback on_progress
        if request.on_progress:
            try:
                request.on_progress(request.request_id, 50.0)
            except Exception as e:
                logger.warning(f"Error in on_progress callback: {e}")
        
        return result
    
    def _generate_fake_response(self, request: ModelRequest) -> str:
        """Generowanie fake response do testow."""
        responses = {
            ModelType.ANALYSIS: f"Analysis of '{request.prompt[:50]}...' completed. Key findings: [simulated analysis results]",
            ModelType.EVALUATION: f"Evaluation of input: Score = {hash(request.prompt) % 100}/100",
            ModelType.PREDICTION: f"Prediction based on input: [simulated prediction]. Confidence: {(hash(request.prompt) % 90) + 10}%",
            ModelType.STRATEGY: f"Strategy recommendation for '{request.task_type}': [strategy details]",
            ModelType.TEACHER: f"Teacher analysis: Agent behavior assessment based on context",
            ModelType.GENERATION: f"Generated content: [simulated generated text based on '{request.prompt[:30]}...']",
            ModelType.AI_LAB: f"AI Laboratory result: [experimental strategy testing results]",
            ModelType.DEVELOPER: f"Developer command executed: {request.prompt[:100]}"
        }
        
        return responses.get(request.model_type, f"Response to: {request.prompt[:100]}")
    
    def _save_memory(self, context: ModelContext, result: ModelResult) -> None:
        """Zapis pamieci (SAVE MEMORY)."""
        # Tutaj bedzie integracja z systemem pamieci
        # Na razie symulacja
        if self.config.log_memory_usage:
            logger.info(f"Memory saved for {context.request.request_id}")
        
        # Wywol callback on_complete
        if context.request.on_complete:
            try:
                context.request.on_complete(result)
            except Exception as e:
                logger.warning(f"Error in on_complete callback: {e}")
        
        # Dodaj mannry do wyniku
        memory_entry_id = f"mem_{context.request.request_id}"
        result.memory_entries.append(memory_entry_id)
    
    def _cleanup_model(self, context: ModelContext) -> None:
        """Czyszczenie po modelu (MODEL STOP)."""
        # Czyszczenie pamieci wedlug strategii
        if self.config.hardware.cleanup_strategy == MemoryCleanupStrategy.BASIC:
            self._basic_cleanup()
        elif self.config.hardware.cleanup_strategy == MemoryCleanupStrategy.AGGRESSIVE:
            self._aggressive_cleanup()
        
        if self.config.log_memory_usage:
            logger.info(f"Cleanup completed for {context.request.request_id}")
    
    def _basic_cleanup(self) -> None:
        """Podstawowe czyszczenie pamieci."""
        try:
            import gc
            gc.collect()
        except:
            pass
    
    def _aggressive_cleanup(self) -> None:
        """Agresywne czyszczenie pamieci."""
        self._basic_cleanup()
        # W przyszlosci: restart procesu Python
    
    def _check_hardware_constraints(self, context: ModelContext) -> bool:
        """Sprawdzenie ograniczen sprzetowych."""
        try:
            import psutil
            
            # Sprawdz pamiec RAM
            if psutil:
                memory = psutil.virtual_memory()
                available_gb = memory.available / (1024**3)
                
                if available_gb < self.config.hardware.min_memory_gb:
                    logger.warning(f"Low memory: {available_gb:.2f}GB available, need {self.config.hardware.min_memory_gb}GB")
                    return False
                
                # Sprawdz uzycie pamieci
                usage_percent = memory.percent
                if usage_percent > self.config.hardware.max_memory_usage_percent:
                    logger.warning(f"High memory usage: {usage_percent}%, max {self.config.hardware.max_memory_usage_percent}%")
                    return False
                
                # Sprawdz GPU (jesli dostepne)
                if self.config.hardware.gpu_available:
                    try:
                        import torch
                        if torch.cuda.is_available():
                            allocated = torch.cuda.memory_allocated() / (1024**3)
                            total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                            available_gpu = total - allocated
                            
                            if available_gpu < self.config.hardware.gpu_memory_buffer_gb:
                                logger.warning(f"Low GPU memory: {available_gpu:.2f}GB available")
                                return False
                    except:
                        pass
            
            return True
            
        except ImportError:
            # psutil/torch nie sa dostepne
            return True
    
    @property
    def is_executing(self) -> bool:
        """Czy obecnie wykonywany jest model."""
        return self._executing
    
    @property
    def current_model(self) -> Optional[ModelContext]:
        """Obecnie wykonywany model."""
        return self._current_model
    
    def stop_execution(self) -> None:
        """Zatrzymanie biezacego wykonania."""
        self._stop_requested = True
        if self._current_model:
            self._current_model.interrupt()


class LLMQueueManager:
    """Glowny manager kolejki modeli LLM.
    
    ZASADA: TYLKO JEDEN MODEL LLM MOZE BYC AKTYWNY
    
    Funkcje:
    - add_request(): Dodawanie zadania do kolejki
    - process_next(): Przetwarzanie nastepnego zadania
    - get_status(): Pobieranie statusu kolejki
    - get_statistics(): Pobieranie statystyk
    - stop_all(): Zatrzymanie wszystkich zadan
    """
    
    def __init__(self, 
                 settings: Optional[LLMQueueSettings] = None,
                 config: Optional[LLMQueueConfig] = None):
        """Inicjalizacja kolejki LLM."""
        # Konfiguracja
        self.settings = settings or create_default_queue_config()
        self.config = config or LLMQueueConfig.from_settings(self.settings)
        
        # Kolejka zadan
        self._queue: python_queue.PriorityQueue = python_queue.PriorityQueue()
        
        # Wykonawca
        self._executor = ModelExecutor(self.settings)
        
        # Stan
        self._running = False
        self._stop_requested = False
        self._processing_thread: Optional[threading.Thread] = None
        
        # Statystyki
        self._statistics = QueueStatistics()
        
        # Locki
        self._queue_lock = threading.Lock()
        self._executor_lock = threading.Lock()
        
        # Logging
        self._setup_logging()
        
        logger.info(f"LLM Queue Manager initialized (max_models={self.config.max_active_models})")
    
    def _setup_logging(self) -> None:
        """Konfiguracja logowania."""
        if self.settings.log_queue_operations:
            logger.setLevel(logging.INFO)
        if self.settings.debug_mode:
            logger.setLevel(logging.DEBUG)
    
    def start(self) -> None:
        """Uruchomienie kolejki."""
        if self._running:
            logger.warning("Queue already running")
            return
        
        self._running = True
        self._stop_requested = False
        
        # Uruchomienie watku przetwarzania
        self._processing_thread = threading.Thread(
            target=self._processing_loop,
            daemon=True
        )
        self._processing_thread.start()
        
        logger.info("LLM Queue Manager started")
    
    def stop(self) -> None:
        """Zatrzymanie kolejki."""
        self._stop_requested = True
        self._running = False
        
        # Zatrzymanie biezacego wykonania
        self._executor.stop_execution()
        
        # Oczekiwanie na zakonczenie watku
        if self._processing_thread:
            self._processing_thread.join(timeout=5.0)
        
        logger.info("LLM Queue Manager stopped")
    
    def _processing_loop(self) -> None:
        """Glowna petla przetwarzania kolejki."""
        while self._running and not self._stop_requested:
            try:
                # Sprawdzenie limits sprzetowych
                if not self._check_hardware_limits():
                    logger.warning("Hardware limits exceeded, waiting...")
                    time.sleep(1.0)
                    continue
                
                # Pobranie nastepnego zadania
                context = self._get_next_request()
                
                if context is None:
                    # Kolejka pusta, czekaj
                    time.sleep(0.1)
                    continue
                
                # Wykonanie modelu
                self._execute_request(context)
                
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                time.sleep(1.0)
    
    def _check_hardware_limits(self) -> bool:
        """Sprawdzenie ograniczen sprzetowych."""
        # Zawsze zwroc True jesli nie mamy biezacego modelu
        # (poniewaz tylko 1 model moze byc aktywny)
        if not self._executor.is_executing:
            return True
        
        # Tutaj sprawdzanie ogolnych ograniczen systemu
        try:
            import psutil
            memory = psutil.virtual_memory()
            if memory.percent > self.config.max_active_models * 80:
                return False
        except ImportError:
            pass
        
        return True
    
    def _get_next_request(self) -> Optional[ModelContext]:
        """Pobranie nastepnego zadania z kolejki."""
        with self._queue_lock:
            if self._queue.empty():
                self._statistics.update_queue_length(0)
                return None
            
            self._statistics.update_queue_length(self._queue.qsize())
            
            # Pobranie zadania z kolejki priorytetowej
            # W PriorityQueue: nizej wartosc = wyzszy priorytet
            try:
                priority, context = self._queue.get_nowait()
                return context
            except python_queue.Empty:
                return None
    
    def _execute_request(self, context: ModelContext) -> None:
        """Wykonanie zadania."""
        with self._executor_lock:
            # Sprawdzanie czy mozna uruchomic model
            if self._executor.is_executing:
                # Juz jest aktywny model, poczekaj
                self._queue.put((context.request.priority.value, context))
                return
            
            # Ustaw aktywny model w statystykach
            self._statistics.current_model = context.request.model_name
            self._statistics.current_model_start_time = datetime.now().isoformat()
            
            # Wykonanie
            result = self._executor.execute(context)
            
            # Aktualizacja statystyk
            if result.success:
                self._statistics.add_completed(
                    context.request.model_type.value,
                    result.processing_time_seconds
                )
            else:
                error_type = "timeout" if context.was_timeout else "error"
                self._statistics.add_failed(context.request.model_type.value, error_type)
            
            # Wywol callback on_complete/on_error
            if result.success and context.request.on_complete:
                try:
                    context.request.on_complete(result)
                except Exception as e:
                    logger.warning(f"Error in on_complete: {e}")
            elif not result.success and context.request.on_error:
                try:
                    context.request.on_error(str(result.error_message or "Unknown error"))
                except Exception as e:
                    logger.warning(f"Error in on_error: {e}")
            
            # Czyszczenie
            self._statistics.current_model = None
            self._statistics.current_model_start_time = None
    
    def add_request(self, request: ModelRequest) -> str:
        """Dodanie zadania do kolejki.
        
        Args:
            request: ModelRequest do dodania
            
        Returns:
            request_id: ID dodanego zadania
            
        Raises:
            QueueFullError: [(asna).Jesli kolejka jest pelna
        """
        with self._queue_lock:
            # Sprawdzanie czy kolejka nie jest pelna
            if self._queue.qsize() >= self.settings.hardware.queue_width:
                raise QueueFullError(
                    f"Queue full: {self._queue.qsize()} requests waiting, max {self.settings.hardware.queue_width}"
                )
            
            # Utworzenie kontekstu
            context = ModelContext(request=request)
            
            # Dodanie do kolejki (PriorityQueue: nizej wartosc = wyzszy priorytet)
            # Dla CRITICAL: moze przerwac biezacy model
            if request.priority.can_interrupt and self._executor.is_executing:
                # Przerwanie biezacego modelu dla CRITICAL
                logger.warning(f"CRITICAL request {request.request_id} interrupting current model")
                self._executor.stop_execution()
                time.sleep(0.5)  # Poczekaj na czyste zatrzymanie
                
                # Dodaj CRITICAL na poczatek kolejki
                self._queue.put_nowait((0, context))  # 0 = najwyzszy priorytet
            else:
                # Normalne dodanie
                priority_value = request.priority.value
                self._queue.put_nowait((priority_value, context))
            
            self._statistics.update_queue_length(self._queue.qsize())
            self._statistics.total_requests += 1
            
            if self.settings.log_queue_operations:
                logger.info(f"Added request {request.request_id} (priority={request.priority.name}, type={request.model_type.value})")
        
        return request.request_id
    
    def add_request_async(self, 
                        model_type: ModelType,
                        prompt: str,
                        system_prompt: str = "",
                        context: Optional[Dict[str, Any]] = None,
                        priority: ModelPriority = ModelPriority.MEDIUM,
                        task_type: str = "generic",
                        model_name: str = "default",
                        agent_id: Optional[str] = None,
                        cycle_number: Optional[int] = None,
                        source: str = "runtime",
                        timeout_seconds: float = 300.0,
                        on_complete: Optional[Callable[[Any], None]] = None,
                        on_error: Optional[Callable[[str], None]] = None) -> str:
        """Dodanie zadania za pomoca parametrow (wygodniejsza metoda).
        
        Args:
            model_type: Typ modelu
            prompt: Prompt do przetworzenia
            system_prompt: System prompt
            context: Dodatkowy kontekst
            priority: Priorytet (domyslnie MEDIUM)
            task_type: Typ zadania
            model_name: Nazwa modelu
            agent_id: ID agenta (opcjonalnie)
            cycle_number: Numer cyklu (opcjonalnie)
            source: Zrodlo zadania
            timeout_seconds: Timeout w sekundach
            on_complete: Callback po zakonczeniu
            on_error: Callback w przypadku bledu
            
        Returns:
            request_id: ID dodanego zadania
        """
        request = ModelRequest(
            model_type=model_type,
            prompt=prompt,
            system_prompt=system_prompt,
            context=context or {},
            priority=priority,
            task_type=task_type,
            model_name=model_name,
            agent_id=agent_id,
            cycle_number=cycle_number,
            source=source,
            timeout_seconds=timeout_seconds,
            on_complete=on_complete,
            on_error=on_error
        )
        
        return self.add_request(request)
    
    def create_agent_request(self,
                           agent_id: str,
                           cycle_number: int,
                           model_type: ModelType,
                           prompt: str,
                           task_type: str = "analysis",
                           context: Optional[Dict[str, Any]] = None,
                           priority: ModelPriority = ModelPriority.MEDIUM) -> str:
        """Utworzenie zadania od agenta.
        
        Uzywane przez agenty do wysylania zadan do kolejki LLM.
        
        Args:
            agent_id: ID agenta
            cycle_number: Numer cyklu
            model_type: Typ modelu
            prompt: Prompt do przetworzenia
            task_type: Typ zadania
            context: Dodatkowy kontekst
            priority: Priorytet
            
        Returns:
            request_id: ID zadania
        """
        return self.add_request_async(
            model_type=model_type,
            prompt=prompt,
            context=context or {},
            priority=priority,
            task_type=task_type,
            agent_id=agent_id,
            cycle_number=cycle_number,
            source="agent",
            model_name=f"{agent_id}_model"
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Pobranie statusu kolejki."""
        with self._queue_lock:
            queue_size = self._queue.qsize()
        
        status = {
            "running": self._running,
            "queue_size": queue_size,
            "max_queue_size": self.settings.hardware.queue_width,
            "is_executing": self._executor.is_executing,
            "current_model": self._statistics.current_model,
            "current_model_start_time": self._statistics.current_model_start_time,
            "mode": self.settings.mode.value,
            "max_active_models": self.config.max_active_models,
            "cleanup_strategy": self.settings.hardware.cleanup_strategy.value
        }
        
        if self._executor.current_model:
            status["current_model_details"] = self._executor.current_model.to_dict()
        
        return status
    
    def get_statistics(self) -> Dict[str, Any]:
        """Pobranie statystyk kolejki."""
        return {
            "total_requests": self._statistics.total_requests,
            "completed_requests": self._statistics.completed_requests,
            "failed_requests": self._statistics.failed_requests,
            "timedout_requests": self._statistics.timedout_requests,
            "interrupted_requests": self._statistics.interrupted_requests,
            "current_queue_length": self._statistics.current_queue_length,
            "longest_queue_length": self._statistics.longest_queue_length,
            "total_processing_time": self._statistics.total_processing_time,
            "avg_processing_time": self._statistics.avg_processing_time,
            "min_processing_time": self._statistics.min_processing_time if self._statistics.min_processing_time != float('inf') else 0.0,
            "max_processing_time": self._statistics.max_processing_time,
            "completed_by_type": self._statistics.completed_model_types,
            "failed_by_type": self._statistics.failed_model_types
        }
    
    def get_queue_contents(self) -> List[Dict[str, Any]]:
        """Pobranie zawartosci kolejki (tylko do debug)."""
        if not self.settings.debug_mode:
            logger.warning("get_queue_contents() requires debug_mode=True")
            return []
        
        contents = []
        with self._queue_lock:
            # Poniewaz PriorityQueue nie mozna iterowac, tworzymy kopie
            temp_queue = python_queue.PriorityQueue()
            
            while not self._queue.empty():
                try:
                    priority, context = self._queue.get_nowait()
                    contents.append({
                        "request_id": context.request.request_id,
                        "priority": context.request.priority.name,
                        "model_type": context.request.model_type.value,
                        "status": str(context.status),
                        "created_at": context.request.created_at
                    })
                    temp_queue.put_nowait((priority, context))
                except python_queue.Empty:
                    break
            
            # Przywroc kolejke
            while not temp_queue.empty():
                try:
                    priority, context = temp_queue.get_nowait()
                    self._queue.put_nowait((priority, context))
                except python_queue.Empty:
                    break
        
        return contents
    
    def clear_queue(self) -> int:
        """Wyczyszczenie kolejki."""
        with self._queue_lock:
            count = self._queue.qsize()
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                except python_queue.Empty:
                    break
            
            self._statistics.update_queue_length(0)
            logger.info(f"Cleared {count} requests from queue")
            return count
    
    def stop_all(self) -> None:
        """Zatrzymanie wszystkich zadan."""
        logger.info("Stopping all LLM queue operations...")
        
        # Zatrzymanie biezacego wykonania
        self._executor.stop_execution()
        
        # Wyczyszczenie kolejki
        cleared = self.clear_queue()
        logger.info(f"Stopped all operations, cleared {cleared} queued requests")
    
    def wait_for_completion(self, request_id: str, timeout: float = 300.0) -> Optional[ModelResult]:
        """Oczekiwanie na zakonczenie konkretnego zadania.
        
        TO DO: Wymaga implementacji systemu sledzenia zadan
        
        Args:
            request_id: ID zadania
            timeout: Timeout w sekundach
            
        Returns:
            ModelResult lub None jeśli timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Sprawdz czy zadanie jest wykonywane
            with self._executor_lock:
                if (self._executor.current_model and 
                    self._executor.current_model.request.request_id == request_id and
                    self._executor.current_model.result):
                    return self._executor.current_model.result
            
            # Sprawdz w statystykach
            time.sleep(0.1)
        
        return None
    
    def __del__(self):
        """Destruktor."""
        self.stop()


def create_llm_queue_manager(
    settings: Optional[LLMQueueSettings] = None,
    auto_start: bool = True
) -> LLMQueueManager:
    """Tworzenie i opcjonalnie uruchomienie kolejki LLM.
    
    Args:
        settings: Ustawienia kolejki (domyslnie default)
        auto_start: Czy automatycznie uruchomic kolejke
        
    Returns:
        LLMQueueManager
    """
    manager = LLMQueueManager(settings=settings)
    
    if auto_start:
        manager.start()
    
    return manager
