# Portfolio Architecture Notes

## Device path

1. The Arduino triggers the ultrasonic sensor and measures the echo duration with a bounded timeout.
2. Firmware converts duration to distance, rejects invalid readings, and feeds a small state machine.
3. A configurable threshold determines the nominal open or closed state.
4. Hysteresis requires the reading to cross a second boundary before reversing state, reducing noisy oscillation.
5. Firmware emits normalized serial messages for readings, transitions, and health conditions.

## Gateway and API path

1. The Python gateway reads serial messages or generates equivalent simulator events.
2. Messages are parsed into typed observations with timestamps and source metadata.
3. The FastAPI service keeps current state and bounded recent history.
4. REST endpoints expose health, current state, history, and configuration.
5. WebSocket clients receive state changes and readings without polling.
6. The browser dashboard visualizes door state, connection health, recent distance, and event history.

## Design decisions

### Hysteresis in the state machine

A single threshold can cause rapid open/closed changes when readings fluctuate near the boundary. Separate transition boundaries make the state more stable.

### Simulator parity

The simulator produces the same event shape as the serial gateway so the API and interface can be developed and tested without physical hardware.

### Transition events plus readings

Raw readings support diagnostics, while explicit transition events support user-facing history and alerts.

### Bounded in-memory history for the demo

The reference application stays easy to run. A production system should use durable storage with retention and integrity controls.

## Production hardening backlog

- Device identity, signed firmware, and authenticated gateway connections
- TLS and token-based API/WebSocket authorization
- Durable event storage with retention and export policies
- Watchdog behavior, reconnect backoff, and offline alerting
- Sensor calibration, enclosure design, and environmental testing
- Metrics for stale data, invalid readings, latency, and device restarts
- Alert routing, escalation policy, and duplicate suppression
- Threat modeling for physical tampering and network compromise
