from netpulse.cli import build_parser, main


def test_parser_version():
    parser = build_parser()
    args = parser.parse_args(["port", "localhost", "443", "--json"])
    assert args.command == "port"
    assert args.port == 443
    assert args.as_json


def test_cli_returns_error_for_invalid_ping_count():
    assert main(["ping", "localhost", "--count", "0"]) == 2
