"""Command-line interface for NetPulse."""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__, check_port, ping, traceroute
from .exceptions import NetPulseError


def _emit(payload: dict[str, object], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    for key, value in payload.items():
        if isinstance(value, (dict, list)):
            print(f"{key}: {json.dumps(value, ensure_ascii=False)}")
        else:
            print(f"{key}: {value}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="netpulse", description="Lightweight network diagnostics toolkit")
    parser.add_argument("--version", action="version", version=f"netpulse {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ping_parser = subparsers.add_parser("ping", help="send ICMP echo requests")
    ping_parser.add_argument("host")
    ping_parser.add_argument("--count", type=int, default=4)
    ping_parser.add_argument("--timeout", type=float, default=1.0, help="per-request timeout in seconds")
    ping_parser.add_argument("--json", action="store_true", dest="as_json")

    port_parser = subparsers.add_parser("port", help="check a TCP port")
    port_parser.add_argument("host")
    port_parser.add_argument("port", type=int)
    port_parser.add_argument("--timeout", type=float, default=2.0)
    port_parser.add_argument("--json", action="store_true", dest="as_json")

    trace_parser = subparsers.add_parser("trace", help="run traceroute")
    trace_parser.add_argument("destination")
    trace_parser.add_argument("--max-hops", type=int, default=20)
    trace_parser.add_argument("--timeout", type=float, default=2.0, help="per-hop probe timeout in seconds")
    trace_parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "ping":
            result = ping(args.host, count=args.count, timeout=args.timeout)
            _emit(result.to_dict(), args.as_json)
            return 0 if result.is_reachable else 2
        if args.command == "port":
            result = check_port(args.host, args.port, timeout=args.timeout)
            _emit(result.to_dict(), args.as_json)
            return 0 if result.is_open else 2
        result = traceroute(args.destination, max_hops=args.max_hops, timeout=args.timeout)
        _emit(result.to_dict(), args.as_json)
        return 0
    except (NetPulseError, ValueError) as exc:
        print(f"netpulse: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
