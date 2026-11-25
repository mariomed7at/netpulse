from netpulse.models import PingResult, PortCheckResult, TracerouteHop, TracerouteResult


def test_ping_result_metrics():
    result = PingResult("localhost", 4, 3, 25.0, (1.0, 2.0, 3.0))
    assert result.is_reachable
    assert result.min_latency_ms == 1.0
    assert result.max_latency_ms == 3.0
    assert result.avg_latency_ms == 2.0
    assert result.to_dict()["is_reachable"] is True


def test_ping_result_without_latency():
    result = PingResult("example.invalid", 2, 0, 100.0)
    assert not result.is_reachable
    assert result.avg_latency_ms is None


def test_other_result_serialization():
    port = PortCheckResult("localhost", 443, True, 1.2)
    assert port.to_dict()["is_open"] is True
    trace = TracerouteResult("localhost", (TracerouteHop(1, ("127.0.0.1",)),), True, ("traceroute",))
    assert trace.to_dict()["hops"][0]["hop"] == 1


def test_submodules_remain_importable():
    from netpulse import icmp, routes

    assert callable(icmp.ping)
    assert callable(routes.traceroute)
