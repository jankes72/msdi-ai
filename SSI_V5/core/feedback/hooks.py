from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from .events import FeedbackEvent, FeedbackEvents


class FeedbackHooks:
    """Hooki obserwujące wejście do pętli feedback.

    Ich celem jest niezmienianie istniejącej logiki, a jedynie rejestrowanie
    zdarzeń z PredictionTrace, MatchResultMemory oraz StrategyEvolution.
    """

    def __init__(self, events: Optional[FeedbackEvents] = None):
        self.events = events or FeedbackEvents()
        self._callbacks: Dict[str, List[Callable[[FeedbackEvent], None]]] = {}
        self._trace_manager: Optional[Any] = None
        self._match_result_memory: Optional[Any] = None
        self._strategy_manager: Optional[Any] = None

    def attach_trace_manager(self, trace_manager: Any) -> None:
        self._trace_manager = trace_manager

    def attach_match_result_memory(self, memory: Any) -> None:
        self._match_result_memory = memory

    def attach_strategy_manager(self, strategy_manager: Any) -> None:
        self._strategy_manager = strategy_manager

    def register_callback(self, event_type: str, callback: Callable[[FeedbackEvent], None]) -> None:
        self._callbacks.setdefault(event_type, []).append(callback)

    def _emit(self, event_type: str, source: str, payload: Optional[Dict[str, Any]] = None, cycle_id: Optional[str] = None) -> FeedbackEvent:
        event = self.events.record(event_type=event_type, source=source, payload=payload or {}, cycle_id=cycle_id)
        for callback in self._callbacks.get(event_type, []):
            try:
                callback(event)
            except Exception:
                continue
        return event

    def on_prediction_trace(self, trace: Any, cycle_id: Optional[str] = None) -> FeedbackEvent:
        payload = self._extract_payload(trace)
        event = self._emit(
            event_type="prediction_trace_received",
            source="prediction_trace",
            payload=payload,
            cycle_id=cycle_id,
        )
        if self._trace_manager is not None:
            event.payload.setdefault("trace_manager_connected", True)
        return event

    def on_match_result(self, match_result: Any, cycle_id: Optional[str] = None) -> FeedbackEvent:
        payload = self._extract_payload(match_result)
        event = self._emit(
            event_type="match_result_received",
            source="match_result_memory",
            payload=payload,
            cycle_id=cycle_id,
        )
        if self._match_result_memory is not None:
            event.payload.setdefault("memory_connected", True)
        return event

    def on_strategy_evolution(self, evolution_data: Any, cycle_id: Optional[str] = None) -> FeedbackEvent:
        payload = self._extract_payload(evolution_data)
        event = self._emit(
            event_type="strategy_evolution_observed",
            source="strategy_evolution",
            payload=payload,
            cycle_id=cycle_id,
        )
        if self._strategy_manager is not None:
            event.payload.setdefault("strategy_manager_connected", True)
        return event

    @staticmethod
    def _extract_payload(obj: Any) -> Dict[str, Any]:
        if obj is None:
            return {}
        if isinstance(obj, dict):
            return dict(obj)
        if hasattr(obj, "to_dict"):
            try:
                return obj.to_dict()
            except Exception:
                pass
        payload: Dict[str, Any] = {}
        for field_name in ("trace_id", "match_id", "strategy_id", "status", "record_id", "population_id"):
            value = getattr(obj, field_name, None)
            if value is not None:
                payload[field_name] = value
        return payload

    def get_events(self, limit: Optional[int] = None) -> List[FeedbackEvent]:
        return self.events.get_events(limit=limit)
