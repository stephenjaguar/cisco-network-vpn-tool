# Requirements Comparison

This document maps the assignment requirements to the current repository implementation.

## Part 1: Cisco Switch Automation

| Requirement | Status | Repository Evidence |
| --- | --- | --- |
| Git repository | Complete | Project files are organized in this repository |
| README with overview and run instructions | Complete | `README.md`, `SETUP_GUIDE.md` |
| Python automation script | Complete | `main.py`, `driver.py`, `validator.py` |
| Frontend for VLAN input | Complete | Flask UI in `templates/index.html`; template notes in `templates/README.md` |
| VLAN 10 `VLAN_DATA` | Complete | `driver.DEFAULT_VLANS`, default frontend row, tests |
| VLAN 20 `VLAN_VOICE` | Complete | `driver.DEFAULT_VLANS`, default frontend row, tests |
| VLAN 50 `VLAN_SECURITY` | Complete | `driver.DEFAULT_VLANS`, default frontend row, tests |
| Optional additional VLAN | Complete | `main.parse_vlan_form()` supports one extra non-duplicate VLAN row |
| Apply VLAN config using network automation library | Complete | `NetmikoSwitchDriver` uses Netmiko SSH; `MockSwitchDriver` supports local validation |
| Hostname change | Complete | Default hostname is `AUTOMATED_SWITCH`; frontend can submit a custom hostname |
| Save config to NVRAM | Complete | `save_config()` sends `write memory` |
| Backup running config | Complete | `backup_config()` writes `backups/[hostname]_[timestamp].cfg` |
| Validate VLAN and hostname config | Complete | `validate_switch_state()` checks submitted hostname and required VLAN policy: 10/20/50 with `VLAN_DATA`, `VLAN_VOICE`, `VLAN_SECURITY` |
| Display alerts for drift | Complete | Frontend displays validation alerts and input validation errors |
| GNS3 simulation path | Complete | `PART1_FLASK_GNS3_SETUP.md` documents GNS3 IOSvL2 SSH flow with management IP `192.168.31.50/24` |
| Frontend/switch evidence screenshots | Complete | `demoresult/part1screenshot.md` and `demoresult/part1screenshot/` |
| Test plan | Complete | `TEST_PLAN.md` |

## Part 2: FortiGate to Palo Alto IPSec VPN Automation Plan

| Requirement | Status | Repository Evidence |
| --- | --- | --- |
| Markdown VPN automation plan | Complete | `VPN_PLAN.md` |
| Part 2 README coverage in main README | Complete | `README.md` Part 2 section |
| Review index for Part 2 | Complete | `PART2_VPN_DELIVERABLES.md` |
| WAN IP parameters | Complete | `VPN_PLAN.md`, `vpn_planner.py` |
| Example local networks | Complete | `10.10.10.0/24` and `10.20.20.0/24` in `VPN_PLAN.md` and `vpn_planner.py` |
| Tunnel network `169.255.1.0/30` | Complete | `VPN_PLAN.md`, `vpn_planner.py` |
| Tunnel IP assignment to both ends | Complete | FortiGate `169.255.1.1/30`, Palo Alto `169.255.1.2/30` |
| Compatible Phase 1 and Phase 2 proposals | Complete | AES-256, SHA-256, DH/PFS Group 14, IKEv2 in `VPN_PLAN.md` and `vpn_planner.py` |
| FortiGate and Palo Alto tools/APIs | Complete | FortiOS REST endpoints, PAN-OS REST/XML API strategy, SSH fallback |
| Automation steps | Complete | Object, crypto, tunnel, routing, policy, commit/apply, validation flow in `VPN_PLAN.md` and `vpn_planner.py` |
| Multi-vendor considerations | Complete | Proxy-ID/selector, proposal, routing, commit, policy, and secret-handling risks |
| VPN validation and alerts | Complete | Validation commands/API checks and alert conditions in `VPN_PLAN.md` and `vpn_planner.py` |
| Structured planning code | Complete | `vpn_planner.py`, `scripts/generate_vpn_plan.py`, `tests/test_vpn_planner.py` |
| Optional sample configs/scripts | Complete | `vpncliexamples/` and `scripts/vpn_connectivity_check.py` |

## Current Validation

Automated test command:

```bash
pytest -q
```

Expected result:

```text
26 passed
```
