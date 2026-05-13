# Cisco IOS Switch Automation for GNS3

This project is a Flask-based Python tool for configuring a Cisco IOS switch from a browser. It supports a local mock driver for testing and a Netmiko SSH driver for a Cisco IOSvL2 switch running in GNS3.

The app can configure:

- Switch hostname
- Required VLANs:
  - VLAN 10: `VLAN_DATA`
  - VLAN 20: `VLAN_VOICE`
  - VLAN 50: `VLAN_SECURITY`
- One optional additional VLAN ID/name
- `write memory`
- Local running-config backup
- Compliance validation for hostname and the three required VLANs

The optional additional VLAN is pushed to the switch, but it is not part of the compliance check.

## Project Files

| File | Purpose |
| --- | --- |
| `main.py` | Flask frontend, form parsing, automation workflow |
| `driver.py` | Mock and Netmiko switch drivers |
| `validator.py` | Compliance report logic |
| `templates/index.html` | Browser UI |
| `tests/` | Pytest coverage |
| `scripts/device_reachability_check.py` | Optional SSH reachability helper |
| `VPN_PLAN.md` | Part 2 FortiGate-to-Palo Alto VPN automation plan |
| `vpn_planner.py` | Part 2 structured VPN plan builder |
| `scripts/generate_vpn_plan.py` | Part 2 JSON plan generator |
| `scripts/vpn_connectivity_check.py` | Optional Part 2 VPN reachability helper |
| `backups/` | Generated running-config backups |

## Requirements

- Python 3
- GNS3
- Cisco IOSvL2 image added to GNS3
- IP reachability from your Mac to the GNS3 switch management IP
- SSH enabled on the IOSvL2 switch

Python dependencies are listed in `requirements.txt`:

```text
flask
netmiko
pytest
python-dotenv
```

## Setup

From the project directory:

```bash
cd /Users/thunder/Documents/Meli
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run tests:

```bash
pytest -q
```

Run the app:

```bash
python main.py
```

Open:

```text
http://127.0.0.1:5000
```

## GNS3 IOSvL2 Setup

In GNS3, add and start your IOSvL2 switch. Give it a management IP that your Mac can reach, for example `192.168.31.50`.

Example switch-side SSH setup:

```text
enable
conf t
hostname GNS3-SW
ip domain-name lab.local
username admin privilege 15 secret admin
crypto key generate rsa modulus 2048
ip ssh version 2

interface vlan 1
 ip address 192.168.31.50 255.255.255.0
 no shutdown
exit

ip default-gateway 192.168.31.1

line vty 0 4
 login local
 transport input ssh
end
write memory
```

Make sure at least one switch port in VLAN 1 is up, otherwise `interface vlan 1` may remain down.

Verify on the switch:

```text
show ip interface brief
show ip ssh
show running-config | section line vty
```

Verify from your Mac:

```bash
ping 192.168.31.50
nc -vz 192.168.31.50 22
```

Both tests should succeed before using the Netmiko driver in the frontend.

## Frontend Usage

The browser form has these fields:

| Field | Meaning |
| --- | --- |
| Driver | `Mock Cisco IOS Driver` or `Netmiko Cisco IOS SSH` |
| Device IP | GNS3 switch management IP, such as `192.168.31.50` |
| Username | IOS local username |
| Password | IOS local password |
| Hostname | Hostname to configure and validate |
| VLAN Configuration | Required VLAN rows used for compliance |
| Additional VLAN | Optional VLAN pushed to the switch only |

When you click **Run Automation**, the app:

1. Connects to the selected driver.
2. Pushes the hostname.
3. Pushes the three required VLANs and optional additional VLAN if provided.
4. Runs `write memory`.
5. Reads the running config and writes a local backup.
6. Runs compliance validation for hostname, VLAN 10, VLAN 20, and VLAN 50.

## Compliance Logic

Compliance is checked against:

| Item | Expected |
| --- | --- |
| Hostname | The hostname submitted in the frontend |
| VLAN 10 | `VLAN_DATA` |
| VLAN 20 | `VLAN_VOICE` |
| VLAN 50 | `VLAN_SECURITY` |

The optional additional VLAN is not checked for compliance. It can be any valid VLAN ID/name as long as the VLAN ID does not duplicate one of the submitted VLAN rows.

The frontend shows:

- `COMPLIANT` when all required checks pass
- `NON_COMPLIANT` when hostname or required VLAN output does not match
- Alert messages for each mismatch

## Netmiko Driver Details

The Netmiko driver uses:

- `device_type="cisco_ios"`
- SSH port `22`
- `conn_timeout=15`
- `auth_timeout=15`
- `banner_timeout=15`
- `read_timeout=60` for config and show commands

Commands sent by the app include:

```text
hostname <hostname>
vlan <id>
name <vlan_name>
write memory
show running-config
show vlan brief
show run | i ^hostname
```

## Backups

Every successful run writes a backup file:

```text
backups/[hostname]_[YYYYMMDD_HHMMSS].cfg
```

The backup contains the running config returned by the selected driver.

## Troubleshooting GNS3 SSH

If the frontend shows a TCP connection failure for `cisco_ios <ip>:22`, check:

```bash
ping <switch-ip>
nc -vz <switch-ip> 22
```

If `ping` fails, check the GNS3 topology, management IP, subnet, cloud/NAT adapter, and macOS network path.

If `ping` works but TCP 22 fails, check IOS SSH configuration:

```text
show ip ssh
show running-config | section line vty
show ip interface brief
```

If Netmiko reports `No existing session`, the code already uses a 15 second connection timeout. Recheck reachability and SSH responsiveness from the terminal before retrying the frontend.

## Mock Driver

Use `Mock Cisco IOS Driver` when you want to test the frontend without GNS3. The mock driver keeps the configured hostname and VLANs in memory, returns Cisco-like show output, and creates a backup file.

## Part 2: FortiGate to Palo Alto IPSec VPN Automation Planning

Part 1 is the GNS3 Cisco switch automation app described above. Part 2 is kept in the same Git repository but separated from the Part 1 Flask workflow so the working switch automation code is not affected.

Part 2 deliverables:

| Artifact | Purpose |
| --- | --- |
| `VPN_PLAN.md` | Markdown plan for automating an IPSec VPN between FortiGate and Palo Alto |
| `PART2_VPN_DELIVERABLES.md` | Requirement-to-artifact review index |
| `vpn_planner.py` | Python module that builds a structured VPN automation plan |
| `scripts/generate_vpn_plan.py` | CLI that prints the structured plan as JSON |
| `scripts/vpn_connectivity_check.py` | Simple post-build ICMP tunnel connectivity check |
| `examples/fortigate_ipsec_cli.conf` | Conceptual FortiGate CLI example |
| `examples/paloalto_ipsec_set_commands.txt` | Conceptual Palo Alto set-command example |
| `tests/test_vpn_planner.py` | Tests for the Part 2 plan builder |

### Part 2 VPN Parameters

The default plan uses these values:

| Parameter | Value |
| --- | --- |
| FortiGate WAN IP | `198.51.100.10` |
| Palo Alto WAN IP | `203.0.113.20` |
| FortiGate local network | `10.10.10.0/24` |
| Palo Alto local network | `10.20.20.0/24` |
| Tunnel network | `169.255.1.0/30` |
| FortiGate tunnel IP | `169.255.1.1/30` |
| Palo Alto tunnel IP | `169.255.1.2/30` |
| IKE version | IKEv2 |
| Phase 1 proposal | AES-256, SHA-256, DH Group 14, lifetime 28800 |
| Phase 2 proposal | AES-256, SHA-256, PFS Group 14, lifetime 3600 |

The traffic selectors are mirrored:

| Device | Local Selector | Remote Selector |
| --- | --- | --- |
| FortiGate | `10.10.10.0/24` | `10.20.20.0/24` |
| Palo Alto | `10.20.20.0/24` | `10.10.10.0/24` |

### Part 2 Tools and APIs

Possible automation interfaces:

- FortiGate FortiOS REST API for Phase 1, Phase 2, interfaces, address objects, firewall policies, and static routes.
- Palo Alto PAN-OS REST API for address objects, tunnel interfaces, IKE gateways, IPSec tunnels, routes, and security policy.
- PAN-OS XML API or Panorama for commit and operational commands.
- SSH with Netmiko or Paramiko for CLI fallback and validation commands.
- A centralized tool such as Panorama, FortiManager, Ansible, or a CI runner for controlled execution.

### Part 2 Automation Steps

The automation workflow should:

1. Validate all input parameters, networks, tunnel IPs, and secret references.
2. Create address objects for local and remote protected networks on both firewalls.
3. Configure FortiGate and Palo Alto tunnel interfaces with `169.255.1.1/30` and `169.255.1.2/30`.
4. Configure compatible Phase 1/IKE settings on both sides.
5. Configure compatible Phase 2/IPSec settings and mirrored Proxy-ID/traffic selectors.
6. Add static routes for the opposite protected subnet through the tunnel.
7. Create firewall policies allowing VPN traffic in the required direction.
8. Commit or apply the configuration, including a PAN-OS commit.
9. Validate configuration state and operational tunnel state.
10. Generate alerts for failed validation checks.

### Part 2 Vendor Considerations

Important multi-vendor risks:

- FortiGate traffic selectors and Palo Alto Proxy-IDs must be mirrored exactly.
- IKE version, Phase 1 proposal, Phase 2 proposal, PFS, and lifetimes must match.
- PAN-OS uses a candidate configuration and requires commit before changes are active.
- FortiGate and Palo Alto use different zone, route, interface, and policy models.
- Pre-shared keys should come from a secret manager and must not be committed to Git.
- NAT-T, route priority, and security policy logging should be aligned with the real network design.

### Part 2 Validation and Alerts

Validation should check both configuration and live tunnel state:

- FortiGate: `get vpn ipsec tunnel summary`, `diagnose vpn tunnel list`, route lookup, policy checks, FortiOS monitor API.
- Palo Alto: `show vpn ike-sa`, `show vpn ipsec-sa`, route lookup, system logs, PAN-OS operational API.
- End-to-end: ICMP or application test traffic between protected networks.

Alert examples:

- `VPN_DOWN`: IKE or IPSec SA is not established.
- `PROXY_ID_MISMATCH`: FortiGate selectors and Palo Alto Proxy-ID are not mirrored.
- `PROPOSAL_MISMATCH`: Phase 1 or Phase 2 settings differ.
- `ROUTE_MISSING`: Remote protected subnet is not routed through the tunnel.
- `POLICY_MISSING`: Security policy does not allow VPN traffic.
- `COMMIT_PENDING`: PAN-OS candidate configuration has not been committed.

### Generate the Part 2 JSON Plan

Run:

```bash
source .venv/bin/activate
python scripts/generate_vpn_plan.py
```

Override default parameters when needed:

```bash
python scripts/generate_vpn_plan.py \
  --fortigate-wan-ip 198.51.100.10 \
  --paloalto-wan-ip 203.0.113.20 \
  --fortigate-lan 10.10.10.0/24 \
  --paloalto-lan 10.20.20.0/24
```

The script prints a JSON object containing parameters, API/tool options, FortiGate steps, Palo Alto steps, validation checks, alert conditions, and vendor considerations.

## Safety

Use the Netmiko driver only against a lab switch or approved test device. The app changes hostname, VLAN configuration, and saves the configuration to startup-config.
