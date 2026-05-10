"""Compliance validation for Cisco IOS automation results."""

from __future__ import annotations

from typing import Dict, List, TypedDict


class ComplianceCheck(TypedDict):
    name: str
    expected: str
    actual: str
    passed: bool


class ComplianceReport(TypedDict):
    status: str
    checks: List[ComplianceCheck]
    alerts: List[str]


def validate_switch_state(
    show_vlan_output: str,
    hostname_output: str,
    intended_hostname: str,
    intended_vlans: Dict[int, str],
) -> ComplianceReport:
    """Compare command output against intended hostname and VLAN state."""
    checks: List[ComplianceCheck] = []
    alerts: List[str] = []

    actual_hostname = _parse_hostname(hostname_output)
    hostname_passed = actual_hostname == intended_hostname
    checks.append(
        {
            "name": "Hostname",
            "expected": intended_hostname,
            "actual": actual_hostname or "<missing>",
            "passed": hostname_passed,
        }
    )
    if not hostname_passed:
        alerts.append(
            f"Hostname mismatch: expected {intended_hostname}, got {actual_hostname or '<missing>'}"
        )

    vlan_table = _parse_show_vlan_brief(show_vlan_output)
    for vlan_id, expected_name in sorted(intended_vlans.items()):
        actual_name = vlan_table.get(vlan_id)
        passed = actual_name == expected_name
        checks.append(
            {
                "name": f"VLAN {vlan_id}",
                "expected": expected_name,
                "actual": actual_name or "<missing>",
                "passed": passed,
            }
        )
        if not passed:
            alerts.append(
                f"VLAN {vlan_id} mismatch: expected {expected_name}, got {actual_name or '<missing>'}"
            )

    status = "COMPLIANT" if all(check["passed"] for check in checks) else "NON_COMPLIANT"
    return {"status": status, "checks": checks, "alerts": alerts}


def _parse_hostname(output: str) -> str:
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith("hostname "):
            return stripped.split(maxsplit=1)[1]
    return ""


def _parse_show_vlan_brief(output: str) -> Dict[int, str]:
    vlans: Dict[int, str] = {}
    for line in output.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        if parts[0].isdigit():
            vlans[int(parts[0])] = parts[1]
    return vlans
