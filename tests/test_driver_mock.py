from pathlib import Path

import sys
import types

from driver import DEFAULT_HOSTNAME, DEFAULT_VLANS, NetmikoSwitchDriver, MockSwitchDriver


def test_mock_driver_applies_hostname_and_vlans():
    driver = MockSwitchDriver("192.0.2.10", "admin", "admin")
    driver.connect()
    driver.push_hostname(DEFAULT_HOSTNAME)
    driver.push_vlan_config(DEFAULT_VLANS)

    assert driver.show_hostname() == f"hostname {DEFAULT_HOSTNAME}"
    vlan_output = driver.show_vlan_brief()
    assert "10   VLAN_DATA" in vlan_output
    assert "20   VLAN_VOICE" in vlan_output
    assert "50   VLAN_SECURITY" in vlan_output


def test_mock_driver_writes_backup(tmp_path):
    driver = MockSwitchDriver("192.0.2.10", "admin", "admin")
    driver.connect()
    driver.push_hostname(DEFAULT_HOSTNAME)
    driver.push_vlan_config(DEFAULT_VLANS)

    backup_path = driver.backup_config(DEFAULT_HOSTNAME, backup_dir=str(tmp_path))

    assert isinstance(backup_path, Path)
    assert backup_path.exists()
    assert backup_path.name.startswith(f"{DEFAULT_HOSTNAME}_")
    assert backup_path.suffix == ".cfg"
    assert f"hostname {DEFAULT_HOSTNAME}" in backup_path.read_text(encoding="utf-8")


class FakeNetmikoConnection:
    def __init__(self):
        self.config_calls = []
        self.command_calls = []
        self.timing_calls = []
        self.base_prompt_calls = []

    def send_config_set(self, commands, **kwargs):
        self.config_calls.append((commands, kwargs))
        return "config output"

    def send_command(self, command, **kwargs):
        self.command_calls.append((command, kwargs))
        return "command output"

    def send_command_timing(self, command, **kwargs):
        self.timing_calls.append((command, kwargs))
        return f"{command}\n"

    def set_base_prompt(self, **kwargs):
        self.base_prompt_calls.append(kwargs)
        return DEFAULT_HOSTNAME


def test_netmiko_commands_use_two_minute_timing_reads():
    driver = NetmikoSwitchDriver("192.0.2.10", "admin", "admin")
    connection = FakeNetmikoConnection()
    driver.connection = connection

    assert driver.push_vlan_config({10: "VLAN_DATA"}) == (
        "configure terminal\nvlan 10\nname VLAN_DATA\nend\n"
    )
    assert driver.get_running_config() == "show running-config\n"

    assert connection.timing_calls == [
        ("configure terminal", {"read_timeout": 120, "cmd_verify": False}),
        ("vlan 10", {"read_timeout": 120, "cmd_verify": False}),
        ("name VLAN_DATA", {"read_timeout": 120, "cmd_verify": False}),
        ("end", {"read_timeout": 120, "cmd_verify": False}),
        ("show running-config", {"read_timeout": 120, "cmd_verify": False}),
    ]


def test_netmiko_hostname_change_uses_generic_prompt_and_refreshes_base_prompt():
    driver = NetmikoSwitchDriver("192.0.2.10", "admin", "admin")
    connection = FakeNetmikoConnection()
    driver.connection = connection

    assert driver.push_hostname("AUTOMAT") == (
        "configure terminal\nhostname AUTOMAT\nend\n"
    )

    assert connection.timing_calls == [
        ("configure terminal", {"read_timeout": 120, "cmd_verify": False}),
        ("hostname AUTOMAT", {"read_timeout": 120, "cmd_verify": False}),
        ("end", {"read_timeout": 120, "cmd_verify": False}),
    ]
    assert connection.base_prompt_calls == [{"pattern": r"[>#]"}]


def test_netmiko_show_hostname_falls_back_to_running_config_when_include_is_empty():
    driver = NetmikoSwitchDriver("192.0.2.10", "admin", "admin")
    connection = FakeNetmikoConnection()
    responses = {
        "show running-config | include hostname": "",
        "show running-config": "hostname AUTOMATED_SWITCH\nend\n",
    }

    def fake_send_command_timing(command, **kwargs):
        connection.timing_calls.append((command, kwargs))
        return responses[command]

    connection.send_command_timing = fake_send_command_timing
    driver.connection = connection

    assert driver.show_hostname() == "hostname AUTOMATED_SWITCH\nend\n"
    assert connection.timing_calls == [
        (
            "show running-config | include hostname",
            {"read_timeout": 120, "cmd_verify": False},
        ),
        ("show running-config", {"read_timeout": 120, "cmd_verify": False}),
    ]


def test_netmiko_connect_uses_fifteen_second_connection_timeouts(monkeypatch):
    captured_kwargs = {}

    def fake_connect_handler(**kwargs):
        captured_kwargs.update(kwargs)
        return FakeNetmikoConnection()

    fake_netmiko = types.SimpleNamespace(ConnectHandler=fake_connect_handler)
    monkeypatch.setitem(sys.modules, "netmiko", fake_netmiko)

    driver = NetmikoSwitchDriver("192.0.2.10", "admin", "admin")

    assert driver.connect() == "Connected to Cisco IOS device at 192.0.2.10"
    assert captured_kwargs["conn_timeout"] == 15
    assert captured_kwargs["auth_timeout"] == 15
    assert captured_kwargs["banner_timeout"] == 15
