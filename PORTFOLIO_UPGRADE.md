# DoorSense Portfolio Upgrade

This branch presents the Arduino door-monitoring project as an end-to-end IoT reference system rather than an isolated hardware sketch.

## Evidence demonstrated

- HC-SR04 ultrasonic distance sampling
- Threshold and hysteresis state logic
- Local LED and buzzer transitions
- JSON serial messages for a gateway
- Backend-ready event modeling
- Automated state-machine tests
- Clear hardware and production limitations

## Review order

1. Read `portfolio_upgrade/README.md`.
2. Inspect `portfolio_upgrade/monitor.py` for stable state transitions.
3. Review `portfolio_upgrade/door_monitor.ino` for the firmware data path.
4. Run `pytest -q portfolio_upgrade/tests`.

All sample readings and events are synthetic portfolio data.
