import pytest

from portfolio_upgrade.monitor import DoorMonitor


def test_hysteresis_prevents_state_flapping() -> None:
    monitor = DoorMonitor(threshold_cm=22, hysteresis_cm=2)
    assert monitor.update(15)['state'] == 'closed'
    assert monitor.update(23)['state'] == 'closed'
    assert monitor.update(24)['state'] == 'open'
    assert monitor.update(21)['state'] == 'open'
    assert monitor.update(20)['state'] == 'closed'


def test_only_transitions_create_events() -> None:
    monitor = DoorMonitor()
    monitor.update(15)
    monitor.update(16)
    monitor.update(31)
    monitor.update(32)
    assert [event['state'] for event in monitor.events()] == ['open', 'closed']


def test_invalid_distance_is_rejected() -> None:
    with pytest.raises(ValueError):
        DoorMonitor().update(800)
