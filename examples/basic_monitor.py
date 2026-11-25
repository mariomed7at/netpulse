"""Small example using NetPulse as an imported library."""

from netpulse import check_port, ping

TARGET = "1.1.1.1"
WEB_HOST = "example.com"

ping_result = ping(TARGET, count=2, timeout=1.0)
print(f"{TARGET}: reachable={ping_result.is_reachable}, loss={ping_result.packet_loss_pct:.1f}%")

https_result = check_port(WEB_HOST, 443, timeout=2.0)
print(f"{WEB_HOST}:443: connection_established={https_result.is_open}")
