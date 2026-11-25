# Architecture

NetPulse is currently a small Python package with a deliberately narrow runtime surface.

- `icmp.py` delegates ICMP echo requests to the operating system's `ping` command and parses common reply/statistics formats.
- `ports.py` uses `socket.create_connection` for one bounded TCP connection attempt.
- `routes.py` delegates route discovery to `tracert` or `traceroute` and parses hop lines.
- `models.py` defines immutable result dataclasses shared by the library and CLI.
- `cli.py` exposes the same operations through the `netpulse` command and supports JSON output.

The package does not run a background service, discover entire subnets, or collect telemetry continuously. Those capabilities would require a separate design covering scheduling, rate limits, storage, access control, and alert delivery.
