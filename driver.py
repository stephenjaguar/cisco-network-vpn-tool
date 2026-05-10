"""Switch driver implementations for Cisco IOS automation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict


DEFAULT_VLANS: Dict[int, str] = {
    10: "VLAN_DATA",
    20: "VLAN_VOICE",
    50: "VLAN_SECURITY",
}


class BaseSwitchDriver(ABC):
    """Interface shared by mock and real Cisco switch drivers."""

    @abstractmethod
    def connect(self) -> str:
        """Open a connection to the device."""

    @abstractmethod
    def push_vlan_config(self, vlans: Dict[int, str]) -> str:
        """Apply VLAN configuration."""

    @abstractmethod
    def push_hostname(self, hostname: str) -> str:
        """Apply hostname configuration."""

    @abstractmethod
    def save_config(self) -> str:
        """Save running configuration to startup configuration."""

    @abstractmethod
    def get_running_config(self) -> str:
        """Return running configuration."""

    @abstractmethod
    def show_vlan_brief(self) -> str:
        """Return show vlan brief output."""

    @abstractmethod
    def show_hostname(self) -> str:
        """Return hostname command output."""

    def backup_config(self, hostname: str, backup_dir: str = "backups") -> Path:
        """Save running config to backups/[hostname]_[timestamp].cfg."""
        safe_hostname = "".join(
            char if char.isalnum() or char in ("-", "_") else "_" for char in hostname
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = Path(backup_dir) / f"{safe_hostname}_{timestamp}.cfg"
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        backup_path.write_text(self.get_running_config(), encoding="utf-8")
        return backup_path


class MockSwitchDriver(BaseSwitchDriver):
    """In-process Cisco IOS mock used for deterministic local testing."""

    def __init__(self, device_ip: str, username: str, password: str) -> None:
        self.device_ip = device_ip
        self.username = username
        self.password = password
        self.connected = False
        self.hostname = "Switch"
        self.vlans: Dict[int, str] = {}
        self.saved = False

    def connect(self) -> str:
        self.connected = True
        return f"Connected to mock Cisco IOS device at {self.device_ip}"

    def push_vlan_config(self, vlans: Dict[int, str]) -> str:
        self._require_connection()
        self.vlans.update(vlans)
        return f"Applied {len(vlans)} VLAN definitions"

    def push_hostname(self, hostname: str) -> str:
        self._require_connection()
        self.hostname = hostname
        return f"Hostname set to {hostname}"

    def save_config(self) -> str:
        self._require_connection()
        self.saved = True
        return "Building configuration...\n[OK]"

    def get_running_config(self) -> str:
        lines = [
            "version 15.2",
            f"hostname {self.hostname}",
            "!",
        ]
        for vlan_id in sorted(self.vlans):
            lines.extend(
                [
                    f"vlan {vlan_id}",
                    f" name {self.vlans[vlan_id]}",
                    "!",
                ]
            )
        lines.append("end")
        return "\n".join(lines) + "\n"

    def show_vlan_brief(self) -> str:
        lines = [
            "VLAN Name                             Status    Ports",
            "---- -------------------------------- --------- -------------------------------",
            "1    default                          active    Gi0/1, Gi0/2, Gi0/3, Gi0/4",
        ]
        for vlan_id in sorted(self.vlans):
            lines.append(f"{vlan_id:<4} {self.vlans[vlan_id]:<32} active")
        return "\n".join(lines)

    def show_hostname(self) -> str:
        return f"hostname {self.hostname}"

    def _require_connection(self) -> None:
        if not self.connected:
            raise RuntimeError("Driver is not connected")


class NetmikoSwitchDriver(BaseSwitchDriver):
    """Cisco IOS SSH driver backed by Netmiko."""

    def __init__(self, device_ip: str, username: str, password: str) -> None:
        self.device_ip = device_ip
        self.username = username
        self.password = password
        self.connection = None

    def connect(self) -> str:
        from netmiko import ConnectHandler

        self.connection = ConnectHandler(
            device_type="cisco_ios",
            host=self.device_ip,
            username=self.username,
            password=self.password,
        )
        return f"Connected to Cisco IOS device at {self.device_ip}"

    def push_vlan_config(self, vlans: Dict[int, str]) -> str:
        commands = []
        for vlan_id, vlan_name in sorted(vlans.items()):
            commands.extend([f"vlan {vlan_id}", f"name {vlan_name}"])
        return self._send_config(commands)

    def push_hostname(self, hostname: str) -> str:
        return self._send_config([f"hostname {hostname}"])

    def save_config(self) -> str:
        return self._send_command("write memory")

    def get_running_config(self) -> str:
        return self._send_command("show running-config")

    def show_vlan_brief(self) -> str:
        return self._send_command("show vlan brief")

    def show_hostname(self) -> str:
        return self._send_command("show run | i ^hostname")

    def _send_config(self, commands: list[str]) -> str:
        self._require_connection()
        return self.connection.send_config_set(commands)

    def _send_command(self, command: str) -> str:
        self._require_connection()
        return self.connection.send_command(command)

    def _require_connection(self) -> None:
        if self.connection is None:
            raise RuntimeError("Driver is not connected")


def create_driver(
    mode: str, device_ip: str, username: str, password: str
) -> BaseSwitchDriver:
    """Factory for selecting mock or Netmiko-backed switch access."""
    if mode == "netmiko":
        return NetmikoSwitchDriver(device_ip, username, password)
    return MockSwitchDriver(device_ip, username, password)
