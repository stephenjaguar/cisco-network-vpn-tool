import socket
from contextlib import nullcontext

from scripts.device_reachability_check import build_ping_command, check_tcp_port


def test_build_ping_command_uses_posix_count_flag(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Darwin")

    assert build_ping_command("192.0.2.10", 3) == ["ping", "-c", "3", "192.0.2.10"]


def test_build_ping_command_uses_windows_count_flag(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Windows")

    assert build_ping_command("192.0.2.10", 3) == ["ping", "-n", "3", "192.0.2.10"]


def test_check_tcp_port_passes_when_connection_opens(monkeypatch):
    def fake_create_connection(address, timeout):
        assert address == ("192.0.2.10", 22)
        assert timeout == 2
        return nullcontext()

    monkeypatch.setattr(socket, "create_connection", fake_create_connection)

    assert check_tcp_port("192.0.2.10", 22, 2) is True


def test_check_tcp_port_fails_when_connection_is_refused(monkeypatch):
    def fake_create_connection(address, timeout):
        raise OSError("connection refused")

    monkeypatch.setattr(socket, "create_connection", fake_create_connection)

    assert check_tcp_port("192.0.2.10", 22, 1) is False
