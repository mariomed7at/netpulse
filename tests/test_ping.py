from importlib import import_module
from unittest.mock import Mock

import pytest

from netpulse.exceptions import SystemUtilityNotFoundError
from netpulse.icmp import _parse_ping_output, ping

ping_module = import_module("netpulse.icmp")


def test_parse_linux_ping_output():
    output = """64 bytes from 1.1.1.1: icmp_seq=1 ttl=58 time=10.1 ms
64 bytes from 1.1.1.1: icmp_seq=2 ttl=58 time=11.2 ms
2 packets transmitted, 2 received, 0% packet loss
"""
    result = _parse_ping_output("1.1.1.1", output, 4)
    assert result.transmitted == 2
    assert result.received == 2
    assert result.packet_loss_pct == 0.0
    assert result.avg_latency_ms == pytest.approx(10.65)


def test_parse_windows_ping_output():
    output = """Reply from 1.1.1.1: bytes=32 time=9ms TTL=57
Packets: Sent = 4, Received = 1, Lost = 3 (75% loss),
"""
    result = _parse_ping_output("1.1.1.1", output, 4)
    assert result.transmitted == 4
    assert result.received == 1
    assert result.packet_loss_pct == 75.0


def test_ping_validates_arguments():
    with pytest.raises(ValueError):
        ping("", count=1)
    with pytest.raises(ValueError):
        ping("localhost", count=0)
    with pytest.raises(ValueError):
        ping("localhost", timeout=0)


def test_ping_missing_executable(monkeypatch):
    monkeypatch.setattr(ping_module.shutil, "which", lambda _: None)
    with pytest.raises(SystemUtilityNotFoundError):
        ping("localhost")


def test_ping_runs_command(monkeypatch):
    monkeypatch.setattr(ping_module.shutil, "which", lambda _: "/bin/ping")
    monkeypatch.setattr(ping_module.platform, "system", lambda: "Linux")
    fake = Mock(
        stdout=(
            "64 bytes from 127.0.0.1: time=0.2 ms" + chr(10)
            + "1 packets transmitted, 1 received, 0% packet loss"
        ),
        stderr="",
        returncode=0,
    )
    monkeypatch.setattr(ping_module.subprocess, "run", lambda *a, **k: fake)
    result = ping("127.0.0.1", count=1)
    assert result.is_reachable
    assert result.received == 1
