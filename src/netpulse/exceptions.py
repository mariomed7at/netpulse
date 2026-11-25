"""Exception types raised by NetPulse."""


class NetPulseError(RuntimeError):
    """Base exception for NetPulse operational errors."""


class SystemUtilityNotFoundError(NetPulseError):
    """Raised when a required operating-system network utility is unavailable."""


class NetworkCommandError(NetPulseError):
    """Raised when an operating-system network command cannot be executed."""
