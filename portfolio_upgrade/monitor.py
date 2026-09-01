from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Literal

DoorState = Literal["open", "closed", "unknown"]


@dataclass(frozen=True)
class DoorEvent:
    state: DoorState
    distance_cm: float
    occurred_at: str


class DoorMonitor:
    """Convert noisy ultrasonic readings into stable door transitions."""

    def __init__(self, threshold_cm: float = 22.0, hysteresis_cm: float = 2.0) -> None:
        if threshold_cm <= 0 or hysteresis_cm <= 0:
            raise ValueError("Threshold and hysteresis must be positive.")
        self.threshold_cm = threshold_cm
        self.hysteresis_cm = hysteresis_cm
        self.state: DoorState = "unknown"
        self.distance_cm = 0.0
        self._events: deque[DoorEvent] = deque(maxlen=100)

    def update(self, distance_cm: float) -> dict[str, object]:
        if not 0 <= distance_cm <= 500:
            raise ValueError("Distance must be between 0 and 500 cm.")
        previous = self.state
        if self.state in {"unknown", "closed"} and distance_cm >= self.threshold_cm + self.hysteresis_cm:
            self.state = "open"
        elif self.state in {"unknown", "open"} and distance_cm <= self.threshold_cm - self.hysteresis_cm:
            self.state = "closed"
        elif self.state == "unknown":
            self.state = "open" if distance_cm >= self.threshold_cm else "closed"
        self.distance_cm = round(float(distance_cm), 2)
        changed = previous != self.state
        if changed:
            self._events.appendleft(DoorEvent(self.state, self.distance_cm, datetime.now(timezone.utc).isoformat()))
        return {
            "state": self.state,
            "distance_cm": self.distance_cm,
            "state_changed": changed,
            "threshold_cm": self.threshold_cm,
            "hysteresis_cm": self.hysteresis_cm,
        }

    def events(self) -> list[dict[str, object]]:
        return [asdict(event) for event in self._events]
