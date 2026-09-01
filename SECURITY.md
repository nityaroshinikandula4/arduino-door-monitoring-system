# Security Policy

## Project scope

Sentinel Door is a portfolio reference implementation for sensor ingestion, state transitions, real-time APIs, and dashboard design. It is not a certified alarm, access-control, life-safety, or physical-security product.

## Reporting a vulnerability

Please avoid publishing exploit details, credentials, private network information, or real facility data in a public issue. Send a concise report to `nityaroshinikandula412@gmail.com` with:

- affected component and commit
- reproduction steps using simulator or synthetic data
- expected and observed behavior
- potential impact
- suggested mitigation, when available

## Safe testing

- Use the simulator before connecting hardware.
- Do not deploy the reference service directly to the public internet.
- Do not rely on the system as the only control protecting a person or property.
- Keep serial, API, and WebSocket inputs bounded and validated.
- Test fail-safe behavior for stale data, disconnects, restarts, and invalid readings.

## Production expectations

A production deployment would need authenticated devices, encrypted network transport, secure firmware updates, managed secrets, API authorization, durable and tamper-evident event storage, health monitoring, calibrated hardware, alert escalation, privacy controls, and a documented physical and cyber threat model.
