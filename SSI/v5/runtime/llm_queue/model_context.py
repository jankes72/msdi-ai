"""
SSI V5 - Model Context
Kontekst i zarzadzanie stanem modelu LLM

Zgodnie z dokumentacja:
- 06_AI_LAB_REQUEST_PIPELINE.md Sekcja 6.1
- Wzorzec: MODEL START -> WORK -> SAVE MEMORY -> MODEL STOP -> NEXT MODEL

Kazdy model LLM w kolejce posiada:
- Unikalne ID zadania
- Typ modelu
- Priorytet
- Stan (PENDING, STARTING, WORKING, SAVING, STOPPING, COMPLETED, ERROR)
- Kontekst (prompt, parametry, kontekst systemowy)
- Wynik (response, metadata, czas wykonania)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable, Union
from enum import Enum, auto
import uuid
import time


class ModelType(Enum):
    """Typy modeli LLM."""
    # Ogolne
    GENERIC = "generic"
    
    # Modele do analizy
    ANALYSIS = "analysis"
    EVALUATION = "evaluation"
    
    # Modele do generacji
    GENERATION = "generation"
    CREATIVE = "creative"
    
    # Modele do predykcji
    PREDICTION = "prediction"
    STRATEGY = "strategy"
    
    # Modele do uczenia
    TEACHER = "teacher"
    LEARNING = "learning"
    
    # Specjalne
    AI_LAB = "ai_lab"  # Zadania dla AI Laboratory
    DEVELOPER = "developer"  # Zadania od dewelopera
    
    @classmethod
    def get_priority(cls, model_type: 'ModelType') -> int:
        """Pobranie domyslnego priorytetu dla typu modelu."""
        priority_map = {
            cls.TEACHER: 10,
            cls.AI_LAB: 9,
            cls.DEVELOPER: 8,
            cls.EVALUATION: 7,
            cls.ANALYSIS: 6,
            cls.STRATEGY: 6,
            cls.PREDICTION: 5,
            cls.GENERATION: 4,
            cls.CREATIVE: 3,
            cls.LEARNING: 2,
            cls.GENERIC: 1
        }
        return priority_map.get(model_type, 1)


class ModelStatus(Enum):
    """Statusy modelu w kolejce."""
    PENDING = auto()      # Oczekuje w kolejce
    STARTING = auto()     # Rozpoczynanie modelu (MODEL START)
    WORKING = auto()      # Model pracuje (WORK)
    SAVING = auto()       # Zapis pamieci (SAVE MEMORY)
    STOPPING = auto()      # Zatrzymywanie modelu (MODEL STOP)
    COMPLETED = auto()    # Zakonczone sukcesem
    ERROR = auto()        # Blednie zakonczone
    CANCELLED = auto()     # Anulowane
    TIMEOUT = auto()      # Przekroczony timeout
    
    def __str__(self) -> str:
        return self.name
    
    @property
    def is_active(self) -> bool:
        """Czy model jest aktywny (w trakcje przetwarzania)."""
        return self in [ModelStatus.STARTING, ModelStatus.WORKING, ModelStatus.SAVING, ModelStatus.STOPPING]
    
    @property
    def is_final(self) -> bool:
        """Czy status jest koncowy."""
        return self in [ModelStatus.COMPLETED, ModelStatus.ERROR, ModelStatus.CANCELLED, ModelStatus.TIMEOUT]


class ModelPriority(Enum):
    """Priorytety zadan w kolejce."""
    CRITICAL = 5    # Natychmiastowe, moga przerwac biezacy model
    HIGH = 4       # Wysoki priorytet
    MEDIUM = 3     # Sredni priorytet (domyslny)
    LOW = 2        # Niski priorytet
    BACKGROUND = 1 # Tlo, wykonywane tylko przy wolnych zasobach
    
    @property
    def can_interrupt(self) -> bool:
        """Czy zadanie moze przerwac biezacy model."""
        return self == ModelPriority.CRITICAL


@dataclass
class ModelRequest:
    """Zadanie (request) dla modelu LLM."""
    
    # Unikalne ID
    request_id: str = field(default_factory=lambda: f"req_{uuid.uuid4().hex[:12]}")
    
    # Typ modelu i zadania
    model_type: ModelType = ModelType.GENERIC
    task_type: str = "generic"
    
    # Priorytet
    priority: ModelPriority = ModelPriority.MEDIUM
    
    # Kontekst
    prompt: str = ""
    system_prompt: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Parametry modelu
    model_name: str = "default"
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 0.9
    top_k: int = 50
    
    # Kontekst systemowy
    agent_id: Optional[str] = None
    cycle_number: Optional[int] = None
    source: str = "runtime"  # runtime, developer, ai_lab, system
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    submitted_by: str = "system"
    
    # Limity (z queue_config)
    timeout_seconds: float = 300.0
    max_memory_gb: float = 8.0
    
    # Callbacks
    on_start: Optional[Callable[[str], None]] = None
    on_progress: Optional[Callable[[str, float], None]] = None
    on_complete: Optional[Callable[[Any], None]] = None
    on_error: Optional[Callable[[str], None]] = None
    
    def __post_init__(self):
        """Inicjalizacja po utworzeniu."""
        # Ustaw domyslny priorytet na podstawie typu modelu
        if self.priority == ModelPriority.MEDIUM:
            default_priority = ModelType.get_priority(self.model_type)
            self.priority = ModelPriority(default_priority)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        return {
            "request_id": self.request_id,
            "model_type": self.model_type.value,
            "task_type": self.task_type,
            "priority": self.priority.value,
            "prompt": self.prompt[:100] + "..." if len(self.prompt) > 100 else self.prompt,
            "model_name": self.model_name,
            "agent_id": self.agent_id,
            "source": self.source,
            "created_at": self.created_at,
            "submitted_by": self.submitted_by,
            "timeout_seconds": self.timeout_seconds
        }
    
    @property
    def estimated_tokens(self) -> int:
        """Szacowana liczba tokenow."""
        # Uproszczone oszacowanie: ~4 tokeny na wyraz
        prompt_tokens = len(self.prompt.split()) * 4
        context_tokens = sum(len(str(v).split()) * 4 for v in self.context.values())
        return prompt_tokens + context_tokens + 100  # +100 na safety


@dataclass
class ModelResult:
    """Wynik wykonania modelu LLM."""
    
    # Odniesienie do requestu
    request_id: str = ""
    
    # Wynik
    response: str = ""
    
    # Metadata
    model_name: str = ""
    model_type: ModelType = ModelType.GENERIC
    task_type: str = ""
    
    # Czas wykonania
    start_time: str = ""
    end_time: str = ""
    processing_time_seconds: float = 0.0
    
    # Statystyki
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    # Status
    status: ModelStatus = ModelStatus.COMPLETED
    error_message: Optional[str] = None
    
    # Kontekst zwrotny
    return_context: Dict[str, Any] = field(default_factory=dict)
    
    # Pamiac
    memory_saved: bool = False
    memory_entries: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Inicjalizacja po utworzeniu."""
        if self.start_time and self.end_time:
            try:
                start = datetime.fromisoformat(self.start_time)
                end = datetime.fromisoformat(self.end_time)
                self.processing_time_seconds = (end - start).total_seconds()
            except:
                self.processing_time_seconds = 0.0
    
    @property
    def success(self) -> bool:
        """Czy wykonanie powiodlo sie."""
        return self.status == ModelStatus.COMPLETED
    
    @property
    def cost_estimate(self) -> float:
        """Szacowany koszt (tokeny)."""
        return self.total_tokens / 1000  # Assuming $0.001 per 1K tokens
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        return {
            "request_id": self.request_id,
            "response": self.response[:200] + "..." if len(self.response) > 200 else self.response,
            "model_name": self.model_name,
            "model_type": self.model_type.value,
            "task_type": self.task_type,
            "status": str(self.status),
            "processing_time_seconds": self.processing_time_seconds,
            "total_tokens": self.total_tokens,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "success": self.success,
            "error_message": self.error_message,
            "memory_saved": self.memory_saved,
            "memory_entries_count": len(self.memory_entries)
        }


@dataclass
class ModelContext:
    """Kontekst wykonania modelu LLM.
    
    Zawiera wszystkie informacje potrzebne do:
    1. Rozpoczecia modelu (MODEL START)
    2. Wykonania pracy (WORK)
    3. Zapisania pamieci (SAVE MEMORY)
    4. Zatrzymania modelu (MODEL STOP)
    """
    
    # Request
    request: ModelRequest
    
    # Stan wykonania
    status: ModelStatus = ModelStatus.PENDING
    current_step: str = "pending"
    progress: float = 0.0  # 0-100%
    
    # Czas
    started_at: Optional[str] = None
    step_started_at: Optional[str] = None
    step_completed_at: Optional[str] = None
    
    # Wynik
    result: Optional[ModelResult] = None
    
    # Bledy
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Zasoby
    memory_before_gb: Optional[float] = None
    memory_after_gb: Optional[float] = None
    gpu_memory_used_gb: Optional[float] = None
    
    # Flagi
    _interrupted: bool = False
    _timeout_triggered: bool = False
    
    def __post_init__(self):
        """Inicjalizacja po utworzeniu."""
        self.memory_before_gb = self._get_memory_usage()
    
    def start(self) -> None:
        """Rozpoczecie modelu (MODEL START)."""
        self.status = ModelStatus.STARTING
        self.current_step = "starting"
        self.started_at = datetime.now().isoformat()
        self.step_started_at = self.started_at
        self.progress = 0.0
        
    def begin_work(self) -> None:
        """Rozpoczecie pracy (WORK)."""
        self.status = ModelStatus.WORKING
        self.current_step = "working"
        self.step_started_at = datetime.now().isoformat()
        self.progress = 10.0  # 10% - rozpoczeto prace
        
    def begin_save_memory(self) -> None:
        """Rozpoczecie zapisu pamieci (SAVE MEMORY)."""
        self.status = ModelStatus.SAVING
        self.current_step = "saving_memory"
        self.step_started_at = datetime.now().isoformat()
        self.progress = 90.0  # 90% - zapis pamieci
        self.memory_after_gb = self._get_memory_usage()
        
    def stop(self) -> None:
        """Zakończenie pracy (MODEL STOP)."""
        self.status = ModelStatus.STOPPING
        self.current_step = "stopping"
        self.step_completed_at = datetime.now().isoformat()
        self.progress = 95.0  # 95% - zatrzymywanie
        
    def complete(self, result: ModelResult) -> None:
        """Zakonczenie z sukcesem."""
        self.result = result
        self.status = ModelStatus.COMPLETED
        self.current_step = "completed"
        self.step_completed_at = datetime.now().isoformat()
        self.progress = 100.0
        self.memory_after_gb = self._get_memory_usage()
        
    def set_error(self, error: str) -> None:
        """Ustawienie bledu."""
        self.errors.append(error)
        self.status = ModelStatus.ERROR
        self.current_step = "error"
        self.step_completed_at = datetime.now().isoformat()
        self.progress = 100.0  # Zakonczone, ale z bledem
        
    def set_timeout(self) -> None:
        """Ustawienie timeoutu."""
        self._timeout_triggered = True
        self.status = ModelStatus.TIMEOUT
        self.current_step = "timeout"
        self.step_completed_at = datetime.now().isoformat()
        
    def interrupt(self) -> None:
        """Przerwanie (tylko dla CRITICAL)."""
        self._interrupted = True
        self.status = ModelStatus.STOPPING
        self.current_step = "interrupted"
        
    def update_progress(self, progress: float) -> None:
        """Aktualizacja postępu."""
        self.progress = min(100.0, max(0.0, progress))
        
    def _get_memory_usage(self) -> Optional[float]:
        """Pobranie uzycia pamieci w GB."""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            return round(memory_mb / 1024, 2)  # GB
        except ImportError:
            return None
    
    @property
    def memory_used_gb(self) -> Optional[float]:
        """Pamiec uzyta podczas wykonania."""
        if self.memory_before_gb and self.memory_after_gb:
            return self.memory_after_gb - self.memory_before_gb
        return None
    
    @property
    def is_final(self) -> bool:
        """Czy kontekst jest w stanie koncowym."""
        return self.status.is_final
    
    @property
    def was_interrupted(self) -> bool:
        """Czy zostal przerwany."""
        return self._interrupted
    
    @property
    def was_timeout(self) -> bool:
        """Czy wystapil timeout."""
        return self._timeout_triggered
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        result = {
            "request_id": self.request.request_id,
            "model_type": str(self.request.model_type),
            "status": str(self.status),
            "current_step": self.current_step,
            "progress": self.progress,
            "started_at": self.started_at,
            "processing_time": self.result.processing_time_seconds if self.result else 0.0,
            "success": self.status == ModelStatus.COMPLETED,
            "interrupted": self._interrupted,
            "timeout": self._timeout_triggered,
            "errors_count": len(self.errors)
        }
        
        if self.result:
            result["result"] = self.result.to_dict()
            
        return result
