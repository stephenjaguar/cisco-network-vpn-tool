# Cisco Network Automation & IPSec VPN Planning Tool

This project is an interview-ready Python automation tool for Cisco IOS switch configuration and validation. It uses Flask for the frontend, Netmiko for real SSH support, and a built-in mock Cisco driver for local testing without GNS3, EVE-NG, VMware, or VirtualBox.

Repository URL:

```text
https://github.com/stephenjaguar/cisco-network-vpn-tool
```

## Features

- Browser UI for device IP, username, password, hostname, and editable VLAN rows.
- Default VLAN intent:
  - VLAN 10: `VLAN_DATA`
  - VLAN 20: `VLAN_VOICE`
  - VLAN 50: `VLAN_SECURITY`
- Hostname configuration with default `AUTOMATED_SWITCH`.
- VLAN ID/name input with validation for numeric IDs, valid VLAN range, required names, and duplicate IDs.
- Save configuration with `write memory`.
- Backup running config to `backups/[hostname]_[timestamp].cfg`.
- Compliance validation from Cisco-like command output.
- Mock driver default for reliable demos and tests.
- Optional Netmiko driver for real Cisco IOS devices.

## Part 2: IPSec VPN Planning Deliverables

The FortiGate-to-Palo Alto IPSec VPN planning requirement is covered by these files:

| Requirement Area | File |
| --- | --- |
| VPN automation plan | `VPN_PLAN.md` |
| Part 2 review index | `PART2_VPN_DELIVERABLES.md` |
| FortiGate conceptual config | `examples/fortigate_ipsec_cli.conf` |
| Palo Alto conceptual config | `examples/paloalto_ipsec_set_commands.txt` |
| Optional tunnel connectivity helper | `scripts/vpn_connectivity_check.py` |

`PART2_VPN_DELIVERABLES.md` maps each Part 2 evaluation criterion to the exact repository artifact.

## Cisco Mocking Approach

The default mode uses `MockSwitchDriver`, an in-process Python mock of a Cisco IOS switch. It does not start a virtual machine or external network emulator. The mock stores hostname and VLAN state, returns Cisco-like `show vlan brief` and hostname output, and generates a running config for backup testing.

This keeps the interview demo deterministic while preserving a clean driver interface for real Netmiko-based devices later.

For the assignment simulation requirement, see `simulation/PACKET_TRACER_GNS3_TESTING.md`, `simulation/README.md`, and `PACKET_TRACER_SETUP.md`. Packet Tracer or GNS3 can provide a Cisco switch with SSH enabled, and the Flask app can connect to that switch through the `Netmiko Cisco IOS SSH` driver.

## Setup

```bash
cd ~/Learning/cisco-network-vpn-tool
chmod +x setup_all.sh
./setup_all.sh
```

For detailed setup, test, and real Cisco switch instructions, see `SETUP_GUIDE.md`.

The English translation of the Spanish assignment is saved in `ASSIGNMENT_TRANSLATION.md`, and the requirement-by-requirement comparison is saved in `REQUIREMENTS_COMPARISON.md`.

## Run Tests

```bash
source .venv/bin/activate
pytest -v
```

See `TEST_PLAN.md` for the complete verification procedure and expected results.

## Interview Overview

Open `interview_overview.html` in a browser for a single-page explanation of the design thinking, mock strategy, validation flow, and real Cisco switch connection process.

## Run the App

```bash
source .venv/bin/activate
python main.py
```

Open:

```text
http://127.0.0.1:5000
```

Use `Mock Cisco IOS Driver` for the normal demo. Use `Netmiko Cisco IOS SSH` only when you have a reachable Cisco IOS device or lab image.

The VLAN rows are editable, but compliance validation is fixed to the assignment policy. The final switch state must contain:

| VLAN ID | Name |
| --- | --- |
| `10` | `VLAN_DATA` |
| `20` | `VLAN_VOICE` |
| `50` | `VLAN_SECURITY` |

If the submitted VLAN IDs or names do not match this policy, the app displays `NON_COMPLIANT` and shows the mismatch alert.

## Optional Real Device Mode

Netmiko mode expects a Cisco IOS SSH target and uses:

- `hostname <name>`
- `vlan <id>`
- `name <vlan_name>`
- `write memory`
- `show running-config`
- `show vlan brief`
- `show run | i ^hostname`

Do not use real device mode against production equipment without change approval.

## Backup Location

Every successful run writes a running-config backup here:

```text
backups/[hostname]_[YYYYMMDD_HHMMSS].cfg
```

Generated backups are ignored by Git because they may contain device-specific configuration. The README and `TEST_PLAN.md` describe how to verify that the backup exists and contains the configured hostname and VLANs.

## Assignment Requirements Mapping

| Requirement | Implementation |
| --- | --- |
| Git repository and README | This repo plus this README |
| Python automation script | `main.py`, `driver.py`, `validator.py` |
| Frontend for VLAN and hostname input | Flask UI in `templates/index.html` |
| VLAN 10/20/50 support | Default editable VLAN rows |
| Apply VLAN config to Cisco switch | `NetmikoSwitchDriver.push_vlan_config()` |
| Change hostname | `push_hostname()` through mock or Netmiko driver |
| Save to NVRAM | `save_config()` runs `write memory` |
| Backup config | `backup_config()` writes timestamped local files |
| Validate config and alert on drift | `validate_switch_state()` and frontend compliance report |
| Packet Tracer/GNS3 simulation path | `simulation/PACKET_TRACER_GNS3_TESTING.md`, `simulation/`, and `PACKET_TRACER_SETUP.md` |
| VPN automation planning | `VPN_PLAN.md` |
| Part 2 VPN deliverables index | `PART2_VPN_DELIVERABLES.md` |
| Optional VPN examples | `examples/fortigate_ipsec_cli.conf`, `examples/paloalto_ipsec_set_commands.txt` |
| Optional tunnel test helper | `scripts/vpn_connectivity_check.py` |
| Test plan | `TEST_PLAN.md` |
