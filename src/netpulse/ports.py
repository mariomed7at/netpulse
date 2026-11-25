"""TCP port connectivity checks using Python's standard library."""

from __future__ import annotations

import socket
from time import perf_counter

from .models import PortCheckResult


def check_port(host: str, port: int, *, timeout: float = 2.0) -> PortCheckResult:
    """Attempt one TCP connection to ``host:port``.

    A failed connection means only that a connection was not established; it does
    not prove that the port is closed (a firewall or routing issue may be involved).
    """
    if not isinstance(host, str) or not host.strip():
        raise ValueError("host must be a non-empty string")
    if not 1 <= port <= 65535:
        raise ValueError("port must be between 1 and 65535")
    if timeout <= 0:
        raise ValueError("timeout must be greater than 0")

    started = perf_counter()
    try:
        with socket.create_connection((host.strip(), port), timeout=timeout):
            elapsed = (perf_counter() - started) * 1000
            return PortCheckResult(host.strip(), port, True, round(elapsed, 2), None)
    except OSError as exc:
        elapsed = (perf_counter() - started) * 1000
        return PortCheckResult(host.strip(), port, False, round(elapsed, 2), str(exc))
