"""
SSI V5 - Dynamic Context Correction

Modul odpowiedzialny za automatyczna korekte kontekstu wiadomosci.
Poprawia brakujace lub niepoprawne dane kontekstowe przed walidacja.

Zasady:
- Najpierw: korekta kontekstu -> walidacja -> wykonanie
- Korekta jest wykonana tylko gdy jest to bezpieczne i logiczne

Wersja: 2.0.0
Data: 2026-08-01
"""

import uuid
import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from SSI.v5.core.information_flow_controller.message_models import (
    SSIMessage,
    SystemStateSnapshot,
    ModuleIdentifier,
    ProcessType,
    PriorityLevel
)
from SSI.v5.core.information_flow_controller.context_manager import (
    ContextManager,
    get_context_manager
)

# Konfiguracja logowania
logger = logging.getLogger(__name__)


class CorrectionAction(Enum):
    """Typy korekcji."""
    GENERATE_MESSAGE_ID = "generate_message_id"      # Wygenerowanie ID wiadomosci
    SET_TIMESTAMP = "set_timestamp"                  # Ustawienie timestamp
    SET_SESSION_ID = "set_session_id"                # Ustawienie session_id
    SET_CYCLE_ID = "set_cycle_id"                    # Ustawienie cycle_id
    SET_CORRELATION_ID = "set_correlation_id"        # Ustawienie correlation_id
    UPDATE_SYSTEM_STATE = "update_system_state"    # Aktualizacja system_state
    SET_SOURCE = "set_source"                        # Ustawienie zródla
    SET_TARGET = "set_target"                        # Ustawienie celu
    SET_PROCESS_TYPE = "set_process_type"          # Ustawienie typu procesu
    SET_PRIORITY = "set_priority"                    # Ustawienie priorytetu
    AUTO_DETECT = "auto_detect"                      # Auto-wykrywanie kontekstu


class CorrectionStrategy(Enum):
    """Strategie korekcji."""
    SAFE = "safe"                  # Tylko bezpieczne korekty (nie zmieniamy istniejacych wartosci)
    SMART = "smart"                # Inteligenta korekta (zmieniamy gdy to ma sens)
    AGGRESSIVE = "aggressive"      # Agresywna korekta (zmieniamy wszystko co sie da)


@dataclass
class CorrectionResult:
    """Wynik korekcji kontekstu."""
    message_id: str
    actions_performed: List[CorrectionAction] = field(default_factory=list)
    fields_corrected: List[str] = field(default_factory=list)
    fields_unchanged: List[str] = field(default_factory=list)
    correction_score: float = 0.0  # 0.0 - 1.0, jak duzo skorygowano
    processing_time_ms: float = 0.0
    corrected_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwersja do slownika."""
        return {
            'message_id': self.message_id,
            'actions_performed': [a.value for a in self.actions_performed],
            'fields_corrected': self.fields_corrected,
            'fields_unchanged': self.fields_unchanged,
            'correction_score': self.correction_score,
            'processing_time_ms': self.processing_time_ms,
            'corrected_at': self.corrected_at.isoformat(),
            'actions_count': len(self.actions_performed),
            'fields_corrected_count': len(self.fields_corrected)
        }
    
    def __str__(self) -> str:
        return f"CorrectionResult({self.message_id}): Actions: {len(self.actions_performed)}, Corrected: {len(self.fields_corrected)}"


@dataclass
class CorrectionConfig:
    """Konfiguracja korekcji kontekstu."""
    # Strategia korekcji
    strategy: CorrectionStrategy = CorrectionStrategy.SMART
    
    # Czy automatycznie generowac brakujace ID
    auto_generate_message_id: bool = True
    auto_set_timestamp: bool = True
    auto_set_session_id: bool = True
    auto_set_cycle_id: bool = True
    auto_set_correlation_id: bool = True
    auto_update_system_state: bool = True
    
    # Czy akceptowac domyslne wartosci
    accept_default_session_id: bool = True
    accept_default_cycle_id: bool = True
    
    # Czy uzupelniac brakujace pola
    fill_missing_fields: bool = True
    
    # Czy korekcja moze zmienic istniejące wartosci
    allow_overwrite: bool = False
    
    # Maksymalny czas korygowania wiadomosci (w sekundach)
    max_message_age_for_correction: int = 300  # 5 minut
    
    @classmethod
    def safe(cls) -> 'CorrectionConfig':
        """Konfiguracja bezpieczna - minimalna ingerencja."""
        return cls(
            strategy=CorrectionStrategy.SAFE,
            auto_generate_message_id=True,
            auto_set_timestamp=True,
            auto_set_session_id=True,
            auto_set_cycle_id=True,
            allow_overwrite=False
        )
    
    @classmethod
    def aggressive(cls) -> 'CorrectionConfig':
        """Konfiguracja agresywna - maksymalna korekta."""
        return cls(
            strategy=CorrectionStrategy.AGGRESSIVE,
            auto_generate_message_id=True,
            auto_set_timestamp=True,
            auto_set_session_id=True,
            auto_set_cycle_id=True,
            auto_set_correlation_id=True,
            auto_update_system_state=True,
            allow_overwrite=True,
            fill_missing_fields=True
        )


class DynamicContextCorrection:
    """
    Dynamiczna korekta kontekstu wiadomosci.
    
    Odpowiedzialnosc:
    - Automatyczne generowanie brakujacych identyfikatorów
    - Ustawianie domyslnych wartosci kontekstowych
    - Aktualizacja system_state
    - Powiazanie wiadomosci w ³ancuchy (correlation_id)
    - Wspólpraca z ContextManager
    
    Zasady:
    1. Najpierw: korekta kontekstu -> walidacja -> wykonanie
    2. Korekta jest wykonana tylko gdy jest to bezpieczne i logiczne
    """
    
    def __init__(self, config: CorrectionConfig = None):
        """
        Inicjalizacja korektora kontekstu.
        
        Args:
            config: Konfiguracja korektora (opcjonalnie)
        """
        self.config = config or CorrectionConfig()
        self._context_manager: Optional[ContextManager] = None
        self._correction_hooks: List[Callable[[SSIMessage, CorrectionResult], None]] = []
        self._lock = threading.RLock()
        self._initialized = False
        
        self._initialize()
        logger.info(f"DynamicContextCorrection zainicjalizowany ze strategia: {self.config.strategy.value}")
    
    def _initialize(self) -> None:
        """Inicjalizacja korektora."""
        if self._initialized:
            return
        
        # Pobranie context manager
        try:
            self._context_manager = get_context_manager()
            logger.debug("DynamicContextCorrection polaczony z ContextManager")
        except Exception as e:
            logger.warning(f"Nie mozna polaczyc z ContextManager: {e}")
        
        self._initialized = True
    
    @classmethod
    def get_instance(cls, config: CorrectionConfig = None) -> 'DynamicContextCorrection':
        """Pobranie instancji korektora (singleton)."""
        if not hasattr(cls, '_instance'):
            cls._instance = cls(config)
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset instancji singleton."""
        if hasattr(cls, '_instance'):
            del cls._instance
    
    def set_config(self, config: CorrectionConfig) -> None:
        """Ustawienie konfiguracji korektora."""
        self.config = config
        logger.info(f"Zmieniono konfiguracje DynamicContextCorrection na: {config.strategy.value}")
    
    def set_context_manager(self, context_manager: ContextManager) -> None:
        """Ustawienie ContextManager."""
        self._context_manager = context_manager
        logger.info("DynamicContextCorrection: ustawiono ContextManager")
    
    def register_correction_hook(
        self, 
        hook: Callable[[SSIMessage, CorrectionResult], None]
    ) -> None:
        """Rejestracja hooka korygujacego."""
        self._correction_hooks.append(hook)
        logger.debug(f"Zarejestrowano correction hook: {hook.__name__}")
    
    def correct(self, message: SSIMessage) -> Tuple[SSIMessage, CorrectionResult]:
        """
        Glowna metoda korekcji kontekstu wiadomosci.
        
        Args:
            message: Wiadomosc do skorygowania
            
        Returns:
            Tuple[SSIMessage, CorrectionResult]: Skorygowana wiadomosc i raport
        """
        import time
        start_time = time.time()
        
        result = CorrectionResult(
            message_id=message.message_id,
            actions_performed=[],
            fields_corrected=[],
            fields_unchanged=[]
        )
        
        try:
            with self._lock:
                corrected_message = message
                
                # Korekta wśród lock (thread-safe)
                # 1. Auto-generacja message_id
                if self.config.auto_generate_message_id:
                    corrected_message, action = self._correct_message_id(corrected_message)
                    if action:
                        result.actions_performed.append(action)
                        result.fields_corrected.append("message_id")
                
                # 2. Auto-ustawienie timestamp
                if self.config.auto_set_timestamp:
                    corrected_message, action = self._correct_timestamp(corrected_message)
                    if action:
                        result.actions_performed.append(action)
                        result.fields_corrected.append("timestamp")
                
                # 3. Auto-ustawienie system_state
                if self.config.auto_update_system_state:
                    corrected_message, action = self._correct_system_state(corrected_message)
                    if action:
                        result.actions_performed.append(action)
                        result.fields_corrected.append("system_state")
                
                # 4. Auto-ustawienie session_id
                if self.config.auto_set_session_id:
                    corrected_message, action = self._correct_session_id(corrected_message)
                    if action:
                        result.actions_performed.append(action)
                        result.fields_corrected.append("session_id")
                
                # 5. Auto-ustawienie cycle_id
                if self.config.auto_set_cycle_id:
                    corrected_message, action = self._correct_cycle_id(corrected_message)
                    if action:
                        result.actions_performed.append(action)
                        result.fields_corrected.append("cycle_id")
                
                # 6. Auto-ustawienie correlation_id
                if self.config.auto_set_correlation_id:
                    corrected_message, action = self._correct_correlation_id(corrected_message)
                    if action:
                        result.actions_performed.append(action)
                        result.fields_corrected.append("correlation_id")
                
                # 7. Auto-wykrywanie kontekstu
                if self.config.strategy in [CorrectionStrategy.SMART, CorrectionStrategy.AGGRESSIVE]:
                    corrected_message, actions = self._auto_detect_context(corrected_message)
                    result.actions_performed.extend(actions)
                    for action in actions:
                        if "session" in action.value:
                            result.fields_corrected.append("session_id")
                        elif "cycle" in action.value:
                            result.fields_corrected.append("cycle_id")
                        elif "correlation" in action.value:
                            result.fields_corrected.append("correlation_id")
                
                # Wywolanie hookow
                for hook in self._correction_hooks:
                    try:
                        hook(corrected_message, result)
                    except Exception as e:
                        logger.warning(f"Hook korekcji zaliczony: {e}")
                
                # Obliczenie correction_score
                total_fields = 6  # message_id, timestamp, session_id, cycle_id, correlation_id, system_state
                corrected_count = len(result.fields_corrected)
                result.correction_score = min(1.0, corrected_count / total_fields)
        
        except Exception as e:
            logger.error(f"Blad podczas korekcji kontekstu: {e}")
            # Zwracamy oryginalna wiadomosc w przypadku bledu
            corrected_message = message
        
        # Czas przetwarzania
        result.processing_time_ms = (time.time() - start_time) * 1000
        
        return corrected_message, result
    
    def correct_batch(
        self, 
        messages: List[SSIMessage]
    ) -> Dict[str, Tuple[SSIMessage, CorrectionResult]]:
        """
        Korekcja wsadu wiadomosci.
        
        Args:
            messages: Lista wiadomosci do skorygowania
            
        Returns:
            Dict[str, Tuple[SSIMessage, CorrectionResult]]: Skorygowane wiadomosci i raporty
        """
        results = {}
        for message in messages:
            corrected, result = self.correct(message)
            results[message.message_id] = (corrected, result)
        return results
    
    def _correct_message_id(
        self, 
        message: SSIMessage
    ) -> Tuple[SSIMessage, Optional[CorrectionAction]]:
        """Korekta message_id."""
        if not message.message_id:
            new_message_id = str(uuid.uuid4())
            corrected = message.clone(message_id=new_message_id)
            return corrected, CorrectionAction.GENERATE_MESSAGE_ID
        
        # Sprawdzenie czy message_id jest zastrzezony
        reserved_ids = {"default", "none", "null", ""}
        if message.message_id in reserved_ids:
            new_message_id = str(uuid.uuid4())
            if self.config.allow_overwrite:
                corrected = message.clone(message_id=new_message_id)
                return corrected, CorrectionAction.GENERATE_MESSAGE_ID
            else:
                # Nie zmieniamy istniejacego ID
                return message, None
        
        return message, None
    
    def _correct_timestamp(
        self, 
        message: SSIMessage
    ) -> Tuple[SSIMessage, Optional[CorrectionAction]]:
        """Korekta timestamp."""
        if not message.timestamp:
            corrected = message.clone(timestamp=datetime.now())
            return corrected, CorrectionAction.SET_TIMESTAMP
        
        # Sprawdzenie czy timestamp nie jest w przyszlosci
        if message.timestamp > datetime.now():
            if self.config.allow_overwrite:
                corrected = message.clone(timestamp=datetime.now())
                return corrected, CorrectionAction.SET_TIMESTAMP
        
        return message, None
    
    def _correct_system_state(
        self, 
        message: SSIMessage
    ) -> Tuple[SSIMessage, Optional[CorrectionAction]]:
        """Korekta system_state."""
        if not message.system_state:
            # Pobranie aktualnego stanu systemu
            if self._context_manager:
                try:
                    current_system_state = self._context_manager.get_system_state()
                    if current_system_state:
                        if isinstance(current_system_state, SystemStateSnapshot):
                            corrected = message.clone(system_state=current_system_state)
                        else:
                            corrected = message.clone(system_state=SystemStateSnapshot())
                        return corrected, CorrectionAction.UPDATE_SYSTEM_STATE
                except Exception as e:
                    logger.debug(f"Nie mozna pobrac system_state z ContextManager: {e}")
            
            # Ustawienie domyslnego system_state
            corrected = message.clone(system_state=SystemStateSnapshot())
            return corrected, CorrectionAction.UPDATE_SYSTEM_STATE
        
        # Aktualizacja istniejacego system_state
        if self._context_manager and self.config.allow_overwrite:
            try:
                current_system_state = self._context_manager.get_system_state()
                if (current_system_state and 
                    message.system_state.timestamp < current_system_state.timestamp):
                    corrected = message.clone(system_state=current_system_state)
                    return corrected, CorrectionAction.UPDATE_SYSTEM_STATE
            except Exception:
                pass
        
        return message, None
    
    def _correct_session_id(
        self, 
        message: SSIMessage
    ) -> Tuple[SSIMessage, Optional[CorrectionAction]]:
        """Korekta session_id."""
        if not message.session_id or message.session_id == "default":
            # Pobranie aktualnej sesji
            if self._context_manager:
                try:
                    current_context = self._context_manager.get_context()
                    if current_context.session_id and current_context.session_id != "default":
                        corrected = message.clone(session_id=current_context.session_id)
                        return corrected, CorrectionAction.SET_SESSION_ID
                except Exception as e:
                    logger.debug(f"Nie mozna pobrac session_id z ContextManager: {e}")
            
            # Jeśli nie ma aktywnej sesji i akceptujemy domyslny
            if self.config.accept_default_session_id:
                return message, None
            else:
                # Generujemy nowy session_id
                new_session_id = f"session_{uuid.uuid4().hex[:8]}"
                corrected = message.clone(session_id=new_session_id)
                return corrected, CorrectionAction.SET_SESSION_ID
        
        return message, None
    
    def _correct_cycle_id(
        self, 
        message: SSIMessage
    ) -> Tuple[SSIMessage, Optional[CorrectionAction]]:
        """Korekta cycle_id."""
        if not message.cycle_id or message.cycle_id == "default":
            # Pobranie aktualnego cyklu
            if self._context_manager:
                try:
                    current_context = self._context_manager.get_context()
                    if current_context.cycle_id and current_context.cycle_id != "default":
                        corrected = message.clone(cycle_id=current_context.cycle_id)
                        return corrected, CorrectionAction.SET_CYCLE_ID
                except Exception as e:
                    logger.debug(f"Nie mozna pobrac cycle_id z ContextManager: {e}")
            
            # Jeśli nie ma aktywnego cyklu i akceptujemy domyslny
            if self.config.accept_default_cycle_id:
                return message, None
            else:
                # Generujemy nowy cycle_id
                new_cycle_id = f"cycle_{uuid.uuid4().hex[:8]}"
                corrected = message.clone(cycle_id=new_cycle_id)
                return corrected, CorrectionAction.SET_CYCLE_ID
        
        return message, None
    
    def _correct_correlation_id(
        self, 
        message: SSIMessage
    ) -> Tuple[SSIMessage, Optional[CorrectionAction]]:
        """Korekta correlation_id."""
        if not message.correlation_id:
            # Ustawienie correlation_id = message_id
            corrected = message.clone(correlation_id=message.message_id)
            return corrected, CorrectionAction.SET_CORRELATION_ID
        
        # Jeśli correlation_id = message_id, to OK
        if message.correlation_id == message.message_id:
            return message, None
        
        return message, None
    
    def _auto_detect_context(
        self, 
        message: SSIMessage
    ) -> Tuple[SSIMessage, List[CorrectionAction]]:
        """
        Auto-wykrywanie i korekta kontekstu.
        
        Returns:
            Tuple[SSIMessage, List[CorrectionAction]]: Skorygowana wiadomosc i lista akcji
        """
        actions = []
        corrected = message
        
        # Sprawdzenie czy session_id i cycle_id sa powiazane
        if (corrected.session_id and corrected.session_id != "default" and
            corrected.cycle_id and corrected.cycle_id != "default"):
            
            # Jeśli cycle_id nie zawiera session_id, spróbujmy to naprawić
            session_prefix = corrected.session_id.split("_")[0]
            if not corrected.cycle_id.startswith(session_prefix):
                if self.config.allow_overwrite:
                    new_cycle_id = f"{session_prefix}_{corrected.cycle_id}"
                    corrected = corrected.clone(cycle_id=new_cycle_id)
                    actions.append(CorrectionAction.SET_CYCLE_ID)
        
        # Sprawdzenie czy timestamp jest spójny z system_state
        if (corrected.timestamp and corrected.system_state and
            corrected.system_state.timestamp):
            
            time_diff = abs((corrected.timestamp - corrected.system_state.timestamp).total_seconds())
            if time_diff > 60:  # 1 minuta
                if self.config.allow_overwrite:
                    # Ustawianie timestamp wiadomosci na podstawie system_state
                    corrected = corrected.clone(timestamp=corrected.system_state.timestamp)
                    actions.append(CorrectionAction.SET_TIMESTAMP)
        
        return corrected, actions
    
    def ensure_context_completeness(self, message: SSIMessage) -> SSIMessage:
        """
        Zapewnienie kompletnosci kontekstu (szybka metoda).
        
        Args:
            message: Wiadomosc
            
        Returns:
            SSIMessage: Wiadomosc z zapewnionym kontekstem
        """
        corrected, _ = self.correct(message)
        return corrected


# Funkcje helper

def get_corrector(config: CorrectionConfig = None) -> DynamicContextCorrection:
    """Pobranie instancji korektora."""
    return DynamicContextCorrection.get_instance(config)


def correct_context(
    message: SSIMessage, 
    config: CorrectionConfig = None
) -> Tuple[SSIMessage, CorrectionResult]:
    """
    Szybka korekta kontekstu wiadomosci.
    
    Args:
        message: Wiadomosc do skorygowania
        config: Konfiguracja korektora (opcjonalnie)
        
    Returns:
        Tuple[SSIMessage, CorrectionResult]: Skorygowana wiadomosc i raport
    """
    corrector = get_corrector(config)
    return corrector.correct(message)


def ensure_context_complete(
    message: SSIMessage, 
    config: CorrectionConfig = None
) -> SSIMessage:
    """
    Zapewnienie kompletnosci kontekstu.
    
    Args:
        message: Wiadomosc
        config: Konfiguracja korektora (opcjonalnie)
        
    Returns:
        SSIMessage: Wiadomosc z zapewnionym kontekstem
    """
    corrector = get_corrector(config)
    return corrector.ensure_context_completeness(message)


# Inicjalizacja modulu
import threading
