from __future__ import annotations

import json
from collections.abc import Iterator

import serial


def serial_readings(port: str, baud_rate: int = 115200) -> Iterator[float]:
    """Yield distance readings from the Arduino JSON serial stream.

    Keep this adapter separate from the API so the simulator and tests do not
    require hardware. A deployment can feed yielded values into DoorMonitor.
    """
    with serial.Serial(port, baud_rate, timeout=2) as connection:
        while True:
            raw = connection.readline().decode("utf-8", errors="replace").strip()
            if not raw:
                continue
            payload = json.loads(raw)
            yield float(payload["distance_cm"])
