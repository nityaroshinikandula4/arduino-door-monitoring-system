from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import StrEnum
from threading import Lock


class DoorState(StrEnum):
    CLOSED = "closed"
    AJAR = "ajar"
    OPEN = "open"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Reading:
    distance_cm: float
    state: DoorState
    changed: bool
    alarm: bool
    source: str
    recorded_at: str

    def to_dict(self) -> dict[str, object]:
        value = asdict(self)
        value["state"] = self.state.value
        return value


@dataclass(frozen=True)
class DoorEvent:
    event_id: int
    previous_state: DoorState
    state: DoorState
    distance_cm: float
    recorded_at: str
    acknowledged: bool = False

    def to_dict(self) -> dict[str, object]:
        value = asdict(self)
        value["previous_state"] = self.previous_state.value
        value["state"] = self.state.value
        return value


class DoorMonitor:
    def __init__(self, closed_threshold: float = 18.0, open_threshold: float = 35.0, max_events: int = 100) -> None:
        if closed_threshold >= open_threshold:
            raise ValueError("Closed threshold must be lower than open threshold.")
        self.closed_threshold = closed_threshold
        self.open_threshold = open_threshold
        self._state = DoorState.UNKNOWN
        self._reading = Reading(-1.0, DoorState.UNKNOWN, False, False, "startup", datetime.now(UTC).isoformat())
        self._events: deque[DoorEvent] = deque(maxlen=max_events)
        self._next_event_id = 1
        self._lock = Lock()

    def classify(self, distance_cm: float) -> DoorState:
        if distance_cm < 0:
            return DoorState.UNKNOWN
        if distance_cm <= self.closed_threshold:
            return DoorState.CLOSED
        if distance_cm >= self.open_threshold:
            return DoorState.OPEN
        return DoorState.AJAR

    def update(self, distance_cm: float, source: str = "simulator") -> Reading:
        with self._lock:
            previous = self._state
            current = self.classify(distance_cm)
            changed = current != previous
            recorded_at = datetime.now(UTC).isoformat()
            alarm = current == DoorState.OPEN
            self._state = current
            self._reading = Reading(round(distance_cm, 2), current, changed, alarm, source, recorded_at)
            if changed and previous != DoorState.UNKNOWN:
                self._events.appendleft(DoorEvent(self._next_event_id, previous, current, round(distance_cm, 2), recorded_at))
                self._next_event_id += 1
            return self._reading

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            return {
                "reading": self._reading.to_dict(),
                "thresholds": {"closed_cm": self.closed_threshold, "open_cm": self.open_threshold},
                "event_count": len(self._events),
                "unacknowledged_count": sum(not event.acknowledged for event in self._events),
            }

    def events(self) -> list[dict[str, object]]:
        with self._lock:
            return [event.to_dict() for event in self._events]

    def acknowledge(self, event_id: int) -> bool:
        with self._lock:
            updated: deque[DoorEvent] = deque(maxlen=self._events.maxlen)
            found = False
            for event in self._events:
                if event.event_id == event_id:
                    event = DoorEvent(**{**asdict(event), "acknowledged": True})
                    found = True
                updated.append(event)
            self._events = updated
            return found
