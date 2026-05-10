# Cisco Network Automation & IPSec VPN Planning Tool

This project is an interview-ready Python automation tool for Cisco IOS switch configuration and validation. It uses Flask for the frontend, Netmiko for real SSH support, and a built-in mock Cisco driver for local testing without GNS3, EVE-NG, VMware, or VirtualBox.

## Features

- Browser UI for device IP, username, password, and hostname.
- Standard VLAN intent:
  - VLAN 10: `VLAN_DATA`
  - VLAN 20: `VLAN_VOICE`
  - VLAN 50: `VLAN_SECURITY`
- Hostname configuration with default `AUTOMATED_SWITCH`.
- Save configuration with `write memory`.
- Backup running config to `backups/[hostname]_[timestamp].cfg`.
- Compliance validation from Cisco-like command output.
- Mock driver default for reliable demos and tests.
- Optional Netmiko driver for real Cisco IOS devices.

## Cisco Mocking Approach

The default mode uses `MockSwitchDriver`, an in-process Python mock of a Cisco IOS switch. It does not start a virtual machine or external network emulator. The mock stores hostname and VLAN state, returns Cisco-like `show vlan brief` and hostname output, and generates a running config for backup testing.

This keeps the interview demo deterministic while preserving a clean driver interface for real Netmiko-based devices later.

## Setup

```bash
cd ~/Learning/cisco-network-vpn-tool
chmod +x setup_all.sh
./setup_all.sh
```

For detailed setup, test, and real Cisco switch instructions, see `SETUP_GUIDE.md`.

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
