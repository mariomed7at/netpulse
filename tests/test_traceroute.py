from importlib import import_module

import pytest

from netpulse.exceptions import SystemUtilityNotFoundError
from netpulse.routes import _parse_traceroute_output, traceroute

traceroute_module = import_module("netpulse.routes")


def test_parse_traceroute_output():
    output = """traceroute to 1.1.1.1
 1  192.0.2.1  1.2 ms  1.1 ms
 2  1.1.1.1  10.0 ms
"""
    result = _parse_traceroute_output("1.1.1.1", output, ["traceroute", "1.1.1.1"])
    assert len(result.hops) == 2
    assert result.hops[0].addresses == ("192.0.2.1",)
    assert result.completed


def test_parse_timeout_hop():
    result = _parse_traceroute_output("example.com", " 1  * * *", ["traceroute"])
    assert len(result.hops) == 1
    assert result.hops[0].addresses == ()
    assert not result.completed


def test_traceroute_validation():
    with pytest.raises(ValueError):
        traceroute("")
    with pytest.raises(ValueError):
        traceroute("localhost", max_hops=0)
    with pytest.raises(ValueError):
        traceroute("localhost", timeout=0)


def test_traceroute_missing_utility(monkeypatch):
    monkeypatch.setattr(traceroute_module.platform, "system", lambda: "Linux")
    monkeypatch.setattr(traceroute_module.shutil, "which", lambda _: None)
    with pytest.raises(SystemUtilityNotFoundError):
        traceroute("localhost")


def test_parse_traceroute_hostname_destination_from_header():
    output = "traceroute to example.com (93.184.216.34), 20 hops max\\n 1  192.0.2.1  1.0 ms\\n 2  93.184.216.34  10.0 ms\\n"
    result = _parse_traceroute_output("example.com", output, ["traceroute", "example.com"])
    assert result.completed
