from scripts.vpn_connectivity_check import build_ping_command


def test_build_ping_command_uses_requested_target_and_count():
    command = build_ping_command("10.20.20.10", 5)

    assert "10.20.20.10" in command
    assert "5" in command
    assert command[0] == "ping"
