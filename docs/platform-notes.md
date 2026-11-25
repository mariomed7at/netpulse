# Platform notes

NetPulse uses native operating-system utilities for ICMP and traceroute instead of reimplementing low-level packet handling.

- Windows uses `ping` and `tracert`.
- Linux and macOS use `ping` and `traceroute` when available.
- TCP checks use Python sockets on all supported platforms.

Native utilities differ in flags, localization, output formatting, and privilege requirements. The current parsers cover common English-language output. Contributions that add platform coverage should include captured, sanitized fixtures and tests. Never include production hostnames or sensitive routing data in fixtures.
