"""ICMP ping implementation backed by the system ping executable."""

from __future__ import annotations

import math
import platform
import re
import shutil
import subprocess

from .exceptions import NetworkCommandError, SystemUtilityNotFoundError
from .models import PingResult

_LATENCY_RE = re.compile(r"time[=<]\s*(\d+(?:\.\d+)?)\s*ms", re.IGNORECASE)
_REPLY_RE = re.compile(r"(?:bytes\s+from|reply\s+from|bytes=)", re.IGNORECASE)
_UNIX_STATS_RE = re.compile(r"(\d+)\s+packets transmitted", re.IGNORECASE)
_WINDOWS_SENT_RE = re.compile(r"Sent\s*=\s*(\d+)", re.IGNORECASE)
_WINDOWS_RECEIVED_RE = re.compile(r"Received\s*=\s*(\d+)", re.IGNORECASE)


def _build_ping_command(host: str, count: int, timeout: float) -> list[str]:
    system = platform.system().lower()
    if system == "windows":
        return ["ping", "-n", str(count), "-w", str(max(1, math.ceil(timeout * 1000))), host]
    if system == "linux":
        # Linux iputils expresses -W in seconds.
        return ["ping", "-n", "-c", str(count), "-W", str(max(1, math.ceil(timeout))), host]
    if system == "darwin":
        # macOS expresses -W in milliseconds.
        return ["ping", "-n", "-c", str(count), "-W", str(max(1, math.ceil(timeout * 1000))), host]
    raise NetworkCommandError(f"Unsupported operating system for ping: {platform.system()} (supported: Windows, Linux, macOS)")


def _parse_ping_output(host: str, output: str, requested_count: int) -> PingResult:
    """Parse common Linux, macOS, and Windows ping reply/statistics formats."""
    lines = output.splitlines()
    reply_lines = [line for line in lines if _REPLY_RE.search(line)]
    latencies = tuple(
        float(match.group(1))
        for line in reply_lines
        if (match := _LATENCY_RE.search(line)) is not None
    )

    transmitted = requested_count
    received = len(reply_lines)

    unix_match = _UNIX_STATS_RE.search(output)
    windows_sent = _WINDOWS_SENT_RE.search(output)
    windows_received = _WINDOWS_RECEIVED_RE.search(output)
    if unix_match:
        transmitted = int(unix_match.group(1))
    elif windows_sent:
        transmitted = int(windows_sent.group(1))
    if windows_received:
        received = int(windows_received.group(1))

    transmitted = max(0, transmitted)
    received = max(0, min(received, transmitted))
    loss = ((transmitted - received) / transmitted * 100.0) if transmitted else 100.0
    return PingResult(
        host=host,
        transmitted=transmitted,
        received=received,
        packet_loss_pct=round(loss, 2),
        latencies_ms=latencies,
    )


def ping(host: str, *, count: int = 4, timeout: float = 1.0) -> PingResult:
    """Send ICMP echo requests to *host* and return a structured summary.

    Args:
        host: Hostname or IP address to test.
        count: Number of echo requests; must be positive.
        timeout: Per-request timeout in seconds; must be positive.

    Raises:
        ValueError: If arguments are invalid.
        SystemUtilityNotFoundError: If the system ``ping`` executable is missing.
        NetworkCommandError: If the command cannot be started or the OS is unsupported.
    """
    if not isinstance(host, str) or not host.strip():
        raise ValueError("host must be a non-empty string")
    if count < 1:
        raise ValueError("count must be at least 1")
    if timeout <= 0:
        raise ValueError("timeout must be greater than 0")
    executable = shutil.which("ping")
    if executable is None:
        raise SystemUtilityNotFoundError("The 'ping' executable was not found on PATH")

    command = _build_ping_command(host.strip(), count, timeout)
    command[0] = executable
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            errors="replace",
            check=False,
            timeout=(count * timeout) + 5,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode(errors="replace")
        parsed = _parse_ping_output(host.strip(), f"{stdout}\n{stderr}", count)
        if parsed.received:
            return parsed
        return PingResult(host.strip(), count, 0, 100.0, ())
    except OSError as exc:
        raise NetworkCommandError(f"Unable to execute ping: {exc}") from exc

    output = f"{completed.stdout}\n{completed.stderr}"
    return _parse_ping_output(host.strip(), output, count)
