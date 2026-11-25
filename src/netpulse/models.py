"""Typed result models returned by NetPulse checks."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class PingResult:
    """Summary of an ICMP echo request run."""

    host: str
    transmitted: int
    received: int
    packet_loss_pct: float
    latencies_ms: tuple[float, ...] = ()

    @property
    def is_reachable(self) -> bool:
        """Whether at least one ICMP reply was received."""
        return self.received > 0

    @property
    def min_latency_ms(self) -> float | None:
        return min(self.latencies_ms) if self.latencies_ms else None

    @property
    def max_latency_ms(self) -> float | None:
        return max(self.latencies_ms) if self.latencies_ms else None

    @property
    def avg_latency_ms(self) -> float | None:
        return sum(self.latencies_ms) / len(self.latencies_ms) if self.latencies_ms else None

    def to_dict(self) -> dict[str, object]:
        return asdict(self) | {
            "is_reachable": self.is_reachable,
            "min_latency_ms": self.min_latency_ms,
            "max_latency_ms": self.max_latency_ms,
            "avg_latency_ms": self.avg_latency_ms,
        }


@dataclass(frozen=True, slots=True)
class PortCheckResult:
    """Result of attempting a TCP connection to a host and port."""

    host: str
    port: int
    is_open: bool
    latency_ms: float | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class TracerouteHop:
    """One hop in a traceroute result."""

    hop: int
    addresses: tuple[str, ...] = ()
    latencies_ms: tuple[float, ...] = ()
    raw: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class TracerouteResult:
    """Parsed traceroute output."""

    destination: str
    hops: tuple[TracerouteHop, ...]
    completed: bool
    command: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "destination": self.destination,
            "hops": [hop.to_dict() for hop in self.hops],
            "completed": self.completed,
            "command": list(self.command),
        }
