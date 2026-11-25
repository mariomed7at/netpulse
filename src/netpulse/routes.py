"""Traceroute wrapper for the operating system's native utility."""

from __future__ import annotations

import ipaddress
import math
import platform
import re
import shutil
import subprocess

from .exceptions import NetworkCommandError, SystemUtilityNotFoundError
from .models import TracerouteHop, TracerouteResult

_HOP_RE = re.compile(r"^\s*(\d+)\s+(.*)$")
_LATENCY_RE = re.compile(r"(\d+(?:\.\d+)?)\s*ms", re.IGNORECASE)
_TOKEN_RE = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?:%[\w.-]+)?|(?<![\w:])[0-9a-fA-F:]{2,}(?:%[\w.-]+)?|\*")


def _valid_ip_token(token: str) -> bool:
    candidate = token.split("%", 1)[0]
    try:
        ipaddress.ip_address(candidate)
        return True
    except ValueError:
        return False


def _parse_traceroute_output(destination: str, output: str, command: list[str]) -> TracerouteResult:
    hops: list[TracerouteHop] = []
    destination_addresses: set[str] = set()
    try:
        destination_addresses.add(ipaddress.ip_address(destination.split("%", 1)[0]).compressed.lower())
    except ValueError:
        pass

    for line in output.splitlines():
        # Both traceroute and tracert commonly print the resolved destination in
        # their first line, even when numeric hop display is enabled.
        if "traceroute to" in line.lower() or "tracing route to" in line.lower():
            for token in _TOKEN_RE.findall(line):
                if token != "*" and _valid_ip_token(token):
                    try:
                        destination_addresses.add(ipaddress.ip_address(token.split("%", 1)[0]).compressed.lower())
                    except ValueError:
                        continue
        match = _HOP_RE.match(line)
        if not match:
            continue
        hop_number = int(match.group(1))
        remainder = match.group(2)
        tokens = [token for token in _TOKEN_RE.findall(remainder) if token == "*" or _valid_ip_token(token)]
        addresses = tuple(dict.fromkeys(token for token in tokens if token != "*"))
        latencies = tuple(float(item) for item in _LATENCY_RE.findall(remainder))
        hops.append(TracerouteHop(hop_number, addresses, latencies, line.strip()))

    completed = any(
        ipaddress.ip_address(address.split("%", 1)[0]).compressed.lower() in destination_addresses
        for hop in hops
        for address in hop.addresses
    )
    return TracerouteResult(destination, tuple(hops), completed, tuple(command))


def traceroute(
    destination: str,
    *,
    max_hops: int = 20,
    timeout: float = 2.0,
) -> TracerouteResult:
    """Run a system traceroute and parse its hop output.

    The operation is bounded by ``max_hops`` and a subprocess timeout. The exact
    behavior is determined by the locally installed system utility.
    """
    if not isinstance(destination, str) or not destination.strip():
        raise ValueError("destination must be a non-empty string")
    if max_hops < 1:
        raise ValueError("max_hops must be at least 1")
    if timeout <= 0:
        raise ValueError("timeout must be greater than 0")

    system = platform.system().lower()
    if system == "windows":
        executable = shutil.which("tracert")
        if not executable:
            raise SystemUtilityNotFoundError("The 'tracert' executable was not found on PATH")
        command = [executable, "-d", "-h", str(max_hops), "-w", str(max(1, math.ceil(timeout * 1000))), destination.strip()]
    elif system in {"linux", "darwin", "freebsd", "openbsd", "netbsd"}:
        executable = shutil.which("traceroute")
        if not executable:
            raise SystemUtilityNotFoundError("The 'traceroute' executable was not found on PATH")
        command = [executable, "-n", "-m", str(max_hops), "-w", str(timeout), destination.strip()]
    else:
        raise NetworkCommandError(f"Unsupported operating system for traceroute: {platform.system()}")

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            errors="replace",
            check=False,
            timeout=(max_hops * timeout * 3) + 10,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode(errors="replace")
        return _parse_traceroute_output(destination.strip(), f"{stdout}\n{stderr}", command)
    except OSError as exc:
        raise NetworkCommandError(f"Unable to execute traceroute: {exc}") from exc

    if completed.returncode != 0 and not completed.stdout.strip():
        detail = completed.stderr.strip() or f"traceroute exited with status {completed.returncode}"
        raise NetworkCommandError(detail)
    return _parse_traceroute_output(destination.strip(), f"{completed.stdout}\n{completed.stderr}", command)
