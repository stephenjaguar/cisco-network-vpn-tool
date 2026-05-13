"""Part 2 IPSec VPN automation planning helpers.

The module is intentionally offline and vendor-neutral: it builds a structured
plan that can later be translated into FortiOS REST calls, PAN-OS REST/XML API
calls, or SSH command execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from ipaddress import ip_interface, ip_network


@dataclass(frozen=True)
class CryptoProposal:
    ike_version: str = "ikev2"
    phase1_encryption: str = "aes256"
    phase1_authentication: str = "sha256"
    phase1_dh_group: str = "14"
    phase1_lifetime_seconds: int = 28800
    phase2_encryption: str = "aes256"
    phase2_authentication: str = "sha256"
    phase2_pfs_group: str = "14"
    phase2_lifetime_seconds: int = 3600


@dataclass(frozen=True)
class VpnParameters:
    fortigate_name: str = "FGT-BRANCH"
    paloalto_name: str = "PA-DC"
    fortigate_wan_ip: str = "198.51.100.10"
    paloalto_wan_ip: str = "203.0.113.20"
    fortigate_lan: str = "10.10.10.0/24"
    paloalto_lan: str = "10.20.20.0/24"
    tunnel_network: str = "169.255.1.0/30"
    fortigate_tunnel_ip: str = "169.255.1.1/30"
    paloalto_tunnel_ip: str = "169.255.1.2/30"
    fortigate_tunnel_interface: str = "vpn-pa-dc"
    paloalto_tunnel_interface: str = "tunnel.10"
    fortigate_zone: str = "vpn"
    paloalto_zone: str = "vpn"
    fortigate_outside_interface: str = "wan1"
    paloalto_virtual_router: str = "default"
    pre_shared_key_secret_ref: str = "secret://ipsec/fortigate-paloalto/psk"
    crypto: CryptoProposal = CryptoProposal()


def validate_vpn_parameters(params: VpnParameters) -> list[str]:
    """Return validation errors for a FortiGate-to-Palo Alto VPN plan."""
    errors: list[str] = []

    fortigate_lan = _network_or_error(params.fortigate_lan, "FortiGate LAN", errors)
    paloalto_lan = _network_or_error(params.paloalto_lan, "Palo Alto LAN", errors)
    tunnel_network = _network_or_error(params.tunnel_network, "Tunnel network", errors)
    fortigate_tunnel_ip = _interface_or_error(
        params.fortigate_tunnel_ip, "FortiGate tunnel IP", errors
    )
    paloalto_tunnel_ip = _interface_or_error(
        params.paloalto_tunnel_ip, "Palo Alto tunnel IP", errors
    )

    if fortigate_lan and paloalto_lan and fortigate_lan.overlaps(paloalto_lan):
        errors.append("FortiGate LAN and Palo Alto LAN must not overlap")

    if tunnel_network and tunnel_network.prefixlen != 30:
        errors.append("Tunnel network must be a /30 network")

    if tunnel_network and fortigate_tunnel_ip and fortigate_tunnel_ip.ip not in tunnel_network:
        errors.append("FortiGate tunnel IP must be inside the tunnel network")

    if tunnel_network and paloalto_tunnel_ip and paloalto_tunnel_ip.ip not in tunnel_network:
        errors.append("Palo Alto tunnel IP must be inside the tunnel network")

    if fortigate_tunnel_ip and paloalto_tunnel_ip:
        if fortigate_tunnel_ip.ip == paloalto_tunnel_ip.ip:
            errors.append("Tunnel endpoint IP addresses must be different")

    if not params.pre_shared_key_secret_ref:
        errors.append("Pre-shared key must be referenced from a secret store")

    return errors


def build_vpn_plan(params: VpnParameters | None = None) -> dict[str, object]:
    """Build a structured automation plan for the Part 2 VPN requirement."""
    params = params or VpnParameters()
    errors = validate_vpn_parameters(params)
    if errors:
        raise ValueError("; ".join(errors))

    return {
        "parameters": _parameter_summary(params),
        "tools_and_apis": {
            "fortigate": [
                "FortiOS REST API /api/v2/cmdb/vpn.ipsec/phase1-interface",
                "FortiOS REST API /api/v2/cmdb/vpn.ipsec/phase2-interface",
                "FortiOS REST API /api/v2/cmdb/firewall/address",
                "FortiOS REST API /api/v2/cmdb/firewall/policy",
                "FortiOS REST API /api/v2/cmdb/router/static",
                "SSH fallback with Netmiko or Paramiko for operational checks",
            ],
            "paloalto": [
                "PAN-OS REST API for objects, network interfaces, IKE gateways, IPSec tunnels, and policy",
                "PAN-OS XML API operational commands and commit operations",
                "Panorama for centralized deployment when firewalls are managed",
                "SSH fallback with Netmiko or Paramiko for show/test commands",
            ],
        },
        "fortigate_steps": _fortigate_steps(params),
        "paloalto_steps": _paloalto_steps(params),
        "validation_checks": _validation_checks(params),
        "alert_conditions": [
            "VPN_DOWN",
            "PROXY_ID_MISMATCH",
            "PROPOSAL_MISMATCH",
            "ROUTE_MISSING",
            "POLICY_MISSING",
            "COMMIT_PENDING",
        ],
        "vendor_considerations": [
            "Proxy-ID and traffic selectors must be mirrored between vendors.",
            "IKE, Phase 1, Phase 2, PFS, and lifetimes must match.",
            "PAN-OS changes require commit before becoming active.",
            "FortiGate and Palo Alto use different object, zone, and routing models.",
            "Secrets should be read from a secret manager, never stored in source control.",
        ],
    }


def _parameter_summary(params: VpnParameters) -> dict[str, object]:
    return {
        "fortigate_wan_ip": params.fortigate_wan_ip,
        "paloalto_wan_ip": params.paloalto_wan_ip,
        "fortigate_lan": params.fortigate_lan,
        "paloalto_lan": params.paloalto_lan,
        "tunnel_network": params.tunnel_network,
        "fortigate_tunnel_ip": params.fortigate_tunnel_ip,
        "paloalto_tunnel_ip": params.paloalto_tunnel_ip,
        "fortigate_selector": {
            "local": params.fortigate_lan,
            "remote": params.paloalto_lan,
        },
        "paloalto_proxy_id": {
            "local": params.paloalto_lan,
            "remote": params.fortigate_lan,
        },
        "crypto": params.crypto.__dict__,
        "pre_shared_key_secret_ref": params.pre_shared_key_secret_ref,
    }


def _fortigate_steps(params: VpnParameters) -> list[dict[str, object]]:
    return [
        {
            "step": "create_address_objects",
            "objects": {
                "local": {"name": "FGT_LOCAL_LAN", "subnet": params.fortigate_lan},
                "remote": {"name": "PA_REMOTE_LAN", "subnet": params.paloalto_lan},
            },
        },
        {
            "step": "create_phase1_interface",
            "endpoint": "/api/v2/cmdb/vpn.ipsec/phase1-interface/",
            "payload": {
                "name": params.fortigate_tunnel_interface,
                "interface": params.fortigate_outside_interface,
                "remote-gw": params.paloalto_wan_ip,
                "ike-version": params.crypto.ike_version,
                "proposal": f"{params.crypto.phase1_encryption}-{params.crypto.phase1_authentication}",
                "dhgrp": params.crypto.phase1_dh_group,
                "keylife": params.crypto.phase1_lifetime_seconds,
                "psksecret": params.pre_shared_key_secret_ref,
            },
        },
        {
            "step": "create_phase2_interface",
            "endpoint": "/api/v2/cmdb/vpn.ipsec/phase2-interface/",
            "payload": {
                "name": f"{params.fortigate_tunnel_interface}-p2",
                "phase1name": params.fortigate_tunnel_interface,
                "proposal": f"{params.crypto.phase2_encryption}-{params.crypto.phase2_authentication}",
                "pfs": "enable",
                "dhgrp": params.crypto.phase2_pfs_group,
                "keylifeseconds": params.crypto.phase2_lifetime_seconds,
                "src-subnet": params.fortigate_lan,
                "dst-subnet": params.paloalto_lan,
            },
        },
        {
            "step": "configure_tunnel_interface_ip",
            "interface": params.fortigate_tunnel_interface,
            "ip": params.fortigate_tunnel_ip,
        },
        {
            "step": "create_static_route",
            "destination": params.paloalto_lan,
            "device": params.fortigate_tunnel_interface,
        },
        {
            "step": "create_firewall_policies",
            "policies": [
                "allow FortiGate LAN to Palo Alto LAN through tunnel",
                "allow Palo Alto LAN to FortiGate LAN through tunnel if required",
            ],
        },
    ]


def _paloalto_steps(params: VpnParameters) -> list[dict[str, object]]:
    return [
        {
            "step": "create_address_objects",
            "objects": {
                "local": {"name": "PA_LOCAL_LAN", "subnet": params.paloalto_lan},
                "remote": {"name": "FGT_REMOTE_LAN", "subnet": params.fortigate_lan},
            },
        },
        {
            "step": "create_crypto_profiles",
            "profiles": {
                "ike": {
                    "encryption": params.crypto.phase1_encryption,
                    "authentication": params.crypto.phase1_authentication,
                    "dh_group": params.crypto.phase1_dh_group,
                    "lifetime_seconds": params.crypto.phase1_lifetime_seconds,
                },
                "ipsec": {
                    "encryption": params.crypto.phase2_encryption,
                    "authentication": params.crypto.phase2_authentication,
                    "pfs_group": params.crypto.phase2_pfs_group,
                    "lifetime_seconds": params.crypto.phase2_lifetime_seconds,
                },
            },
        },
        {
            "step": "create_tunnel_interface",
            "interface": params.paloalto_tunnel_interface,
            "ip": params.paloalto_tunnel_ip,
            "zone": params.paloalto_zone,
            "virtual_router": params.paloalto_virtual_router,
        },
        {
            "step": "create_ike_gateway",
            "peer_ip": params.fortigate_wan_ip,
            "pre_shared_key": params.pre_shared_key_secret_ref,
        },
        {
            "step": "create_ipsec_tunnel_and_proxy_id",
            "tunnel": params.paloalto_tunnel_interface,
            "proxy_id": {
                "local": params.paloalto_lan,
                "remote": params.fortigate_lan,
                "protocol": "any",
            },
        },
        {
            "step": "create_static_route",
            "destination": params.fortigate_lan,
            "interface": params.paloalto_tunnel_interface,
        },
        {
            "step": "create_security_policy_and_commit",
            "actions": [
                "allow Palo Alto LAN to FortiGate LAN",
                "allow FortiGate LAN to Palo Alto LAN if required",
                "commit candidate configuration",
            ],
        },
    ]


def _validation_checks(params: VpnParameters) -> list[dict[str, str]]:
    return [
        {
            "device": params.fortigate_name,
            "check": "IKE SA established",
            "method": "GET /api/v2/monitor/vpn/ipsec or get vpn ipsec tunnel summary",
        },
        {
            "device": params.fortigate_name,
            "check": "IPSec SA established",
            "method": "diagnose vpn tunnel list",
        },
        {
            "device": params.fortigate_name,
            "check": "route to Palo Alto LAN uses tunnel",
            "method": f"get router info routing-table details {params.paloalto_lan}",
        },
        {
            "device": params.paloalto_name,
            "check": "IKE SA established",
            "method": "show vpn ike-sa",
        },
        {
            "device": params.paloalto_name,
            "check": "IPSec SA established",
            "method": "show vpn ipsec-sa",
        },
        {
            "device": params.paloalto_name,
            "check": "route to FortiGate LAN uses tunnel",
            "method": f"show routing route destination {params.fortigate_lan}",
        },
    ]


def _network_or_error(value: str, label: str, errors: list[str]):
    try:
        return ip_network(value, strict=True)
    except ValueError:
        errors.append(f"{label} must be a valid network")
        return None


def _interface_or_error(value: str, label: str, errors: list[str]):
    try:
        return ip_interface(value)
    except ValueError:
        errors.append(f"{label} must be a valid interface address")
        return None
