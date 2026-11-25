"""NetPulse: lightweight network diagnostics for Python."""

from .exceptions import NetPulseError, SystemUtilityNotFoundError
from .models import PingResult, PortCheckResult, TracerouteHop, TracerouteResult
from .icmp import ping
from .ports import check_port
from .routes import traceroute

__all__ = [
    "NetPulseError",
    "PingResult",
    "PortCheckResult",
    "SystemUtilityNotFoundError",
    "TracerouteHop",
    "TracerouteResult",
    "check_port",
    "ping",
    "traceroute",
]

__version__ = "0.1.0"
