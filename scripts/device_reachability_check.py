"""Reachability checks for a Cisco IOS SSH target used by Netmiko.

The script verifies the path from the local machine to a simulated or real
Cisco IOS device before the Flask app tries to automate it with Netmiko.
"""

from __future__ import annotations

import argparse
import platform
import socket
import subprocess
import sys
from getpass import getpass

from ssh_compat import enable_legacy_ios_kex


DEFAULT_COMMAND = "show ip interface brief"


def build_ping_command(host: str, count: int) -> list[str]:
    """Build a platform-specific ping command."""
    if platform.system().lower() == "windows":
        return ["ping", "-n", str(count), host]
    return ["ping", "-c", str(count), host]


def run_ping(host: str, count: int, timeout: int) -> bool:
    """Return True when the host replies to ICMP echo."""
    command = build_ping_command(host, count)
    try:
        result = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"PING: FAIL ({exc})")
        return False

    if result.returncode == 0:
        print("PING: PASS")
        return True

    print("PING: FAIL")
    output = result.stdout.strip()
    if output:
        print(output)
    return False


def check_tcp_port(host: str, port: int, timeout: int) -> bool:
    """Return True when a TCP connection can be opened."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            print(f"TCP {port}: PASS")
            return True
    except OSError as exc:
        print(f"TCP {port}: FAIL ({exc})")
        return False


def read_ssh_banner(host: str, port: int, timeout: int) -> str | None:
    """Read the SSH server banner when the remote device sends one."""
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            sock.settimeout(timeout)
            banner = sock.recv(255).decode("ascii", errors="replace").strip()
    except OSError as exc:
        print(f"SSH banner: FAIL ({exc})")
        return None

    if banner:
        print(f"SSH banner: {banner}")
        return banner

    print("SSH banner: no banner received")
    return None


def run_netmiko_show(
    host: str,
    username: str,
    password: str,
    command: str,
    timeout: int,
) -> bool:
    """Connect with Netmiko and run one IOS show command."""
    try:
        enable_legacy_ios_kex()
    except RuntimeError as exc:
        print(f"NETMIKO: FAIL ({exc})")
        return False

    try:
        from netmiko import ConnectHandler
    except ImportError:
        print("NETMIKO: FAIL (netmiko is not installed)")
        return False

    try:
        connection = ConnectHandler(
            device_type="cisco_ios",
            host=host,
            username=username,
            password=password,
            conn_timeout=timeout,
            auth_timeout=timeout,
            banner_timeout=timeout,
        )
        try:
            output = connection.send_command(command)
        finally:
            connection.disconnect()
    except Exception as exc:  # Netmiko raises several transport/auth exceptions.
        print(f"NETMIKO: FAIL ({exc})")
        return False

    print("NETMIKO: PASS")
    print(f"$ {command}")
    print(output.strip())
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check local reachability to a Cisco IOS SSH target"
    )
    parser.add_argument("host", help="Device management IP or hostname")
    parser.add_argument("--port", type=int, default=22, help="SSH TCP port")
    parser.add_argument("--count", type=int, default=3, help="ICMP ping count")
    parser.add_argument("--timeout", type=int, default=5, help="Timeout in seconds")
    parser.add_argument("--username", help="SSH username for Netmiko test")
    parser.add_argument("--password", help="SSH password for Netmiko test")
    parser.add_argument(
        "--command",
        default=DEFAULT_COMMAND,
        help="IOS show command for the Netmiko test",
    )
    parser.add_argument(
        "--skip-netmiko",
        action="store_true",
        help="Only test ICMP/TCP/SSH banner reachability",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    print(f"Target: {args.host}:{args.port}")
    ping_ok = run_ping(args.host, args.count, args.timeout)
    tcp_ok = check_tcp_port(args.host, args.port, args.timeout)
    banner_ok = read_ssh_banner(args.host, args.port, args.timeout) is not None

    netmiko_ok = True
    if not args.skip_netmiko:
        username = args.username or input("SSH username: ")
        password = args.password or getpass("SSH password: ")
        netmiko_ok = run_netmiko_show(
            args.host, username, password, args.command, args.timeout
        )

    if ping_ok and tcp_ok and banner_ok and netmiko_ok:
        print("RESULT: reachable for Netmiko")
        return 0

    print("RESULT: not ready for Netmiko")
    return 1


if __name__ == "__main__":
    sys.exit(main())
