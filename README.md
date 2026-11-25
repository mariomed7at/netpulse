# NetPulse

**A lightweight, cross-platform network diagnostics toolkit for Python.**

NetPulse provides small, scriptable building blocks for common network checks. The first release focuses on ICMP reachability, TCP port checks, and traceroute output. It has no third-party runtime dependencies.

> **Project status:** early alpha (`00.1.0`). APIs may change before a stable `1.0` release. NetPulse is a diagnostics library, not a full NOC platform or an always-on monitoring service yet.

## Features

- ICMP ping using the host operating system's `ping` executable.
- TCP port checks using Python's standard library.
- Traceroute using the system `traceroute` (Linux/macOS) or `tracert` (Windows) utility.
- Structured, typed result objects and a JSON-capable command-line interface.
- Python 3.11+; no third-party runtime dependencies.

## Requirements

- Python 3.11 or newer.
- For `ping`: the operating system's `ping` utility must be available on `PATH`.
- For `traceroute`: `tracert` on Windows or `traceroute` on Linux/macOS must be available on `PATH`.
- TCP port checks use Python sockets and require no external utility.

NetPulse does not install or configure system networking utilities. On some systems, ICMP or traceroute may require elevated privileges or may be blocked by a firewall.

## Install from source

```bash
git clone https://github.com/mariomed7at/netpulse.git
cd netpulse
python -m pip install .
```

For development:

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
```

## Python usage

### Ping

```python
from netpulse import ping

result = ping("1.1.1.1", count=4, timeout=1.0)
print(result.is_reachable)
print(f"Packet loss: {result.packet_loss_pct:.1f}%")
print(f"Received: {result.received}/{result.transmitted}")
print(f"Average latency: {result.avg_latency_ms} ms")
```

### TCP port check

```python
from netpulse import check_port

result = check_port("example.com", 443, timeout=2.0)
if result.is_open:
    print(f"Port is open ({result.latency_ms:.1f} ms)")
else:
    print(f"Port is closed or unreachable: {result.error}")
```

A failed TCP connection cannot always distinguish a closed port from a filtered port, routing failure, or host outage. Treat `is_open=False` as “connection not established,” not proof that the port is closed.

### Traceroute

```python
from netpulse import traceroute

result = traceroute("example.com", max_hops=20, timeout=2.0)
for hop in result.hops:
    addresses = ", ".join(hop.addresses) or "*"
    print(f"{hop.hop:>2}: {addresses}")
```

Traceroute availability and output depend on the operating system, installed utility, and network policy.

## Command-line usage

```bash
netpulse ping 1.1.1.1 --count 4 --timeout 1
netpulse ping example.com --json
netpulse port example.com 443 --timeout 2
netpulse port 192.0.2.10 22 --json
netpulse trace example.com --max-hops 20 --timeout 2
```

Use `netpulse --help` or `netpulse <command> --help` for all options. The CLI returns exit code `0` when a ping receives a reply or a TCP connection succeeds, and `2` when the check does not succeed. Traceroute returns `0` when it completes a run and `2` if it cannot be started or executed.

## Safety and scope

NetPulse is intended for systems and networks you own or are explicitly authorized to test. Use conservative timeouts and rates. The current release performs only user-requested, single-target diagnostics; it does not perform subnet scanning, credential testing, exploitation, or stealth activity.

See [SECURITY.md](SECURITY.md) for responsible disclosure guidance and [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## Roadmap

The roadmap is a proposal, not a promise of existing functionality:

- [ ] Consistent cross-platform test coverage on Windows, Linux, and macOS.
- [ ] Optional async TCP checks with bounded concurrency.
- [ ] SNMP polling through an optional dependency.
- [ ] A simple scheduled monitor and pluggable alert handlers.
- [ ] JSON/NDJSON output and configuration profiles.
- [ ] Additional operating-system traceroute parsers.

## Contributing

Issues and pull requests are welcome. Please include a reproducible use case, tests for behavior changes, and documentation updates where appropriate. Do not submit secrets, customer data, or private network details.

## License

NetPulse is distributed under the MIT License. See [LICENSE](LICENSE).
