# Sentinel Door — Recruiter-Facing Project Overview

Sentinel Door is an end-to-end IoT monitoring reference application that connects ultrasonic sensor firmware, threshold and hysteresis logic, a Python serial gateway, a FastAPI service, WebSocket updates, a simulator, and a responsive live dashboard.

## Engineering highlights

- Arduino firmware for HC-SR04 distance sampling with bounded timing behavior
- Configurable open/closed threshold and hysteresis to reduce rapid state flapping
- State-transition events rather than noisy duplicate readings
- Python serial gateway that normalizes device messages before forwarding them
- REST endpoints for current state, history, and configuration
- WebSocket updates for a low-latency browser dashboard
- Simulator mode for development and automated testing without physical hardware
- Structured event timestamps, connection state, and sensor-health feedback
- Automated state-machine and API tests in the complete project package

## Architecture

```text
HC-SR04 sensor
      |
      v
Arduino sampling + hysteresis state machine
      |
 serial event messages
      v
Python gateway
      |
      v
FastAPI state store + REST + WebSocket
      |
      v
Live responsive monitoring dashboard
```

## Responsible framing

This is a portfolio and learning implementation, not a certified physical-security or life-safety system. Ultrasonic readings can be affected by placement, materials, temperature, power quality, and obstruction. A production deployment would need authenticated devices, encrypted transport, durable event storage, health monitoring, watchdogs, offline behavior, calibrated hardware, alert routing, and a documented threat model.

## Recommended repository topics

`arduino` · `iot` · `fastapi` · `websocket` · `python` · `embedded-systems` · `real-time-dashboard`
