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
        self.base_prompt_calls = []

    def send_config_set(self, commands, **kwargs):
        self.config_calls.append((commands, kwargs))
        return "config output"

    def send_command(self, command, **kwargs):
        self.command_calls.append((command, kwargs))
        return "command output"

    def set_base_prompt(self, **kwargs):
        self.base_prompt_calls.append(kwargs)
        return DEFAULT_HOSTNAME


def test_netmiko_commands_use_one_minute_read_timeout():
    driver = NetmikoSwitchDriver("192.0.2.10", "admin", "admin")
    connection = FakeNetmikoConnection()
    driver.connection = connection

    assert driver.push_vlan_config({10: "VLAN_DATA"}) == "config output"
    assert driver.get_running_config() == "command output"

    assert connection.config_calls == [
        (["vlan 10", "name VLAN_DATA"], {"read_timeout": 60, "terminator": r"[>#]"})
    ]
    assert connection.command_calls == [
        (
            "show running-config",
            {"read_timeout": 60, "expect_string": r"[>#]", "auto_find_prompt": False},
        )
    ]


def test_netmiko_hostname_change_uses_generic_prompt_and_refreshes_base_prompt():
    driver = NetmikoSwitchDriver("192.0.2.10", "admin", "admin")
    connection = FakeNetmikoConnection()
    driver.connection = connection

    assert driver.push_hostname("AUTOMAT") == "config output"

    assert connection.config_calls == [
        (
            ["hostname AUTOMAT"],
            {"cmd_verify": False, "read_timeout": 60, "terminator": r"[>#]"},
        )
    ]
    assert connection.base_prompt_calls == [{"pattern": r"[>#]"}]


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
