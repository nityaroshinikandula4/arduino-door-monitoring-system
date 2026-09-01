from app.monitor import DoorMonitor, DoorState


def test_classification_thresholds() -> None:
    monitor = DoorMonitor(closed_threshold=18, open_threshold=35)
    assert monitor.classify(10) == DoorState.CLOSED
    assert monitor.classify(25) == DoorState.AJAR
    assert monitor.classify(42) == DoorState.OPEN
    assert monitor.classify(-1) == DoorState.UNKNOWN


def test_state_changes_create_events() -> None:
    monitor = DoorMonitor()
    monitor.update(10)
    assert monitor.events() == []  # startup transition is not treated as an alert
    monitor.update(42)
    events = monitor.events()
    assert len(events) == 1
    assert events[0]["previous_state"] == "closed"
    assert events[0]["state"] == "open"
    assert monitor.snapshot()["unacknowledged_count"] == 1
    assert monitor.acknowledge(events[0]["event_id"])
    assert monitor.snapshot()["unacknowledged_count"] == 0
