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

## Safety

Use the Netmiko driver only against a lab switch or approved test device. The app changes hostname, VLAN configuration, and saves the configuration to startup-config.
