from unittest.mock import MagicMock

import pytest

from netpulse.ports import check_port


def test_check_port_validates_arguments():
    with pytest.raises(ValueError):
        check_port("localhost", 0)
    with pytest.raises(ValueError):
        check_port("localhost", 65536)
    with pytest.raises(ValueError):
        check_port("localhost", 80, timeout=0)


def test_check_port_success(monkeypatch):
    context = MagicMock()
    context.__enter__.return_value = context
    context.__exit__.return_value = False
    monkeypatch.setattr("netpulse.ports.socket.create_connection", lambda *a, **k: context)
    result = check_port("localhost", 443)
    assert result.is_open
    assert result.latency_ms is not None
    assert result.error is None


def test_check_port_failure(monkeypatch):
    def fail(*args, **kwargs):
        raise ConnectionRefusedError("refused")
    monkeypatch.setattr("netpulse.ports.socket.create_connection", fail)
    result = check_port("localhost", 443)
    assert not result.is_open
    assert "refused" in result.error
