from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

from .events import FeedbackEvents
from .hooks import FeedbackHooks


@dataclass
class CycleFeedbackController:
    """Kontroler cyklu feedback dla ETAP 5.2.8.

    Jest to minimalna, bezpieczna warstwa kontrolna, która nie modyfikuje
    istniejących komponentów produkcyjnych. Zamiast tego rejestruje zdarzenia,
    zbiera informacje o predykcji, rezultacie i ewolucji strategii.
    """

    trace_manager: Optional[Any] = None
    match_result_memory: Optional[Any] = None
    strategy_manager: Optional[Any] = None
    events: FeedbackEvents = field(default_factory=FeedbackEvents)
    hooks: Optional[FeedbackHooks] = None
    enabled: bool = True

    def __post_init__(self) -> None:
        if self.hooks is None:
            self.hooks = FeedbackHooks(events=self.events)
        if self.trace_manager is not None:
            self.hooks.attach_trace_manager(self.trace_manager)
        if self.match_result_memory is not None:
            self.hooks.attach_match_result_memory(self.match_result_memory)
        if self.strategy_manager is not None:
            self.hooks.attach_strategy_manager(self.strategy_manager)

    def register_hook(self, event_type: str, callback) -> None:
        self.hooks.register_callback(event_type, callback)

    def process_cycle(
        self,
        prediction_trace: Optional[Any] = None,
        match_result: Optional[Any] = None,
        strategy_evolution: Optional[Any] = None,
        cycle_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self.enabled:
            return {
                "cycle_id": cycle_id or f"cycle_{uuid.uuid4().hex[:12]}",
                "status": "disabled",
                "events": [],
                "trace_id": None,
                "match_id": None,
                "strategy_id": None,
                "metadata": metadata or {},
            }

        resolved_cycle_id = cycle_id or f"cycle_{uuid.uuid4().hex[:12]}"
        run_metadata = dict(metadata or {})
        run_metadata.setdefault("started_at", datetime.utcnow().isoformat())

        trace_event = None
        match_event = None
        evolution_event = None

        if prediction_trace is not None:
            trace_event = self.hooks.on_prediction_trace(prediction_trace, cycle_id=resolved_cycle_id)
        if match_result is not None:
            match_event = self.hooks.on_match_result(match_result, cycle_id=resolved_cycle_id)
        if strategy_evolution is not None:
            evolution_event = self.hooks.on_strategy_evolution(strategy_evolution, cycle_id=resolved_cycle_id)

        result = {
            "cycle_id": resolved_cycle_id,
            "status": "completed",
            "events": [event.to_dict() for event in self.events.get_events()],
            "trace_id": self._extract_id(prediction_trace, "trace_id"),
            "match_id": self._extract_id(match_result, "match_id"),
            "strategy_id": self._extract_id(strategy_evolution, "strategy_id"),
            "metadata": run_metadata,
        }

        if trace_event is not None:
            result["trace_event"] = trace_event.to_dict()
        if match_event is not None:
            result["match_event"] = match_event.to_dict()
        if evolution_event is not None:
            result["evolution_event"] = evolution_event.to_dict()

        return result

    @staticmethod
    def _extract_id(obj: Any, field_name: str) -> Optional[str]:
        if obj is None:
            return None
        if isinstance(obj, dict):
            return obj.get(field_name)
        return getattr(obj, field_name, None)

    def get_events(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return [event.to_dict() for event in self.events.get_events(limit=limit)]

    def clear_events(self) -> None:
        self.events.clear()
