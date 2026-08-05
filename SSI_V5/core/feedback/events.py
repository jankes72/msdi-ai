from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import copy
import uuid


@dataclass
class FeedbackEvent:
    """Zdarzenie generowane przez pętlę feedback."""

    event_id: str = field(default_factory=lambda: f"fb_event_{uuid.uuid4().hex[:12]}")
    event_type: str = "cycle_started"
    source: str = "core.feedback"
    cycle_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "source": self.source,
            "cycle_id": self.cycle_id,
            "timestamp": self.timestamp.isoformat(),
            "payload": copy.deepcopy(self.payload),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeedbackEvent":
        event = cls(
            event_id=data.get("event_id", f"fb_event_{uuid.uuid4().hex[:12]}"),
            event_type=data.get("event_type", "cycle_started"),
            source=data.get("source", "core.feedback"),
            cycle_id=data.get("cycle_id"),
            payload=copy.deepcopy(data.get("payload", {})),
        )
        if data.get("timestamp"):
            try:
                event.timestamp = datetime.fromisoformat(data["timestamp"])
            except ValueError:
                pass
        return event


class FeedbackEvents:
    """Prosty rejestr zdarzeń dla feedback loop."""

    def __init__(self):
        self._events: List[FeedbackEvent] = []

    def record(
        self,
        event_type: str,
        source: str = "core.feedback",
        payload: Optional[Dict[str, Any]] = None,
        cycle_id: Optional[str] = None,
    ) -> FeedbackEvent:
        event = FeedbackEvent(
            event_type=event_type,
            source=source,
            cycle_id=cycle_id,
            payload=payload or {},
        )
        self._events.append(event)
        return event

    def get_events(self, limit: Optional[int] = None) -> List[FeedbackEvent]:
        if limit is None:
            return list(self._events)
        return list(self._events)[-limit:]

    def clear(self) -> None:
        self._events.clear()

    def to_dict(self) -> List[Dict[str, Any]]:
        return [event.to_dict() for event in self._events]

    @classmethod
    def from_dict(cls, data: List[Dict[str, Any]]) -> "FeedbackEvents":
        events = cls()
        for item in data:
            events._events.append(FeedbackEvent.from_dict(item))
        return events
