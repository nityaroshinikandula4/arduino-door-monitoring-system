# DoorSense End-to-End Reference Build

DoorSense converts ultrasonic distance measurements into stable, reviewable door events.

## Data path

```text
HC-SR04 echo pulse
      ↓
Arduino distance calculation
      ↓
threshold + hysteresis state logic
      ↓
LED / buzzer transition + JSON serial message
      ↓
serial gateway → API → WebSocket dashboard
```

The Python state machine in this folder mirrors the firmware behavior so the important transition rules can be tested without hardware.

## Test

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r portfolio_upgrade/requirements.txt
pytest -q portfolio_upgrade/tests
```

## Default behavior

With a 22 cm threshold and 2 cm hysteresis:

- a closed door opens at 24 cm or greater;
- an open door closes at 20 cm or less;
- values between those points preserve the current state.

## Production boundary

A deployed IoT product would also need device identity, encrypted transport, durable event storage, offline buffering, sensor-failure detection, secure provisioning, alert delivery, monitoring, and a physical-installation review. The portfolio project uses synthetic demonstration events.
