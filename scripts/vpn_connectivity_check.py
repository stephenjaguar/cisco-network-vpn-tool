"""Conceptual IPSec tunnel connectivity test helper.

This script assumes the VPN tunnel has already been built. It performs a small
ICMP test from the host running the script to a supplied remote IP address.
"""

from __future__ import annotations

import argparse
import platform
import subprocess


def build_ping_command(target: str, count: int) -> list[str]:
    if platform.system().lower() == "windows":
        return ["ping", "-n", str(count), target]
    return ["ping", "-c", str(count), target]


def main() -> int:
    parser = argparse.ArgumentParser(description="Test connectivity across a VPN tunnel")
    parser.add_argument("target", help="Remote host IP behind the IPSec tunnel")
    parser.add_argument("--count", type=int, default=3, help="Number of ICMP probes")
    args = parser.parse_args()

    command = build_ping_command(args.target, args.count)
    result = subprocess.run(command, check=False)
    if result.returncode == 0:
        print(f"VPN_CONNECTIVITY_OK target={args.target}")
    else:
        print(f"VPN_CONNECTIVITY_FAILED target={args.target}")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
