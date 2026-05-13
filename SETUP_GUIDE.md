# Step-by-Step Setup Guide

This guide sets up the current Cisco IOS switch automation and VPN planning repository on macOS. The default demo path uses a Python mock Cisco switch, so GNS3 is optional for local testing.

## 1. Confirm Prerequisites

Open Terminal and check Python:

```bash
python3 --version
```

Expected:

```text
Python 3.10 or newer
```

If Python is missing, install it from Python.org or Homebrew.

## 2. Go to the Project Folder

```bash
cd /Users/thunder/Documents/Meli
```

## 3. Run the Setup Script

```bash
chmod +x setup_all.sh
./setup_all.sh
```

This will:

- Create `.venv/`.
- Install Python dependencies.
- Create `backups/`.
- Run the automated test suite.
- Print the command to start the web app.

Expected final result:

```text
All setup checks passed.
Run app: source .venv/bin/activate && python main.py
```

## 4. Start the Web App

```bash
source .venv/bin/activate
python main.py
```

Open:

```text
http://127.0.0.1:5000
```

## 5. Test the Mock Cisco Workflow

Use these form values:

| Field | Value |
| --- | --- |
| Driver | `Mock Cisco IOS Driver` |
| Device IP | `192.0.2.10` |
| Username | `admin` |
| Password | `admin` |
| Hostname | `AUTOMATED_SWITCH` |
| VLAN row 1 | `10`, `VLAN_DATA` |
| VLAN row 2 | `20`, `VLAN_VOICE` |
| VLAN row 3 | `50`, `VLAN_SECURITY` |
| Additional VLAN | leave blank, or use a non-duplicate VLAN such as `60`, `VLAN_GUEST` |

Click `Run Automation`.

Expected:

- Compliance status is `COMPLIANT`.
- Hostname check is `PASS`.
- VLAN 10, VLAN 20, and VLAN 50 checks are `PASS`.
- A backup path is shown.

The optional additional VLAN is pushed to the device or mock driver when provided, but it is not included in the compliance checks.

Compliance is checked against the required VLAN policy:

| VLAN | Expected Name |
| --- | --- |
| 10 | `VLAN_DATA` |
| 20 | `VLAN_VOICE` |
| 50 | `VLAN_SECURITY` |

The hostname check uses the hostname submitted in the frontend.

## 6. Verify Backup File

In a second Terminal window:

```bash
cd /Users/thunder/Documents/Meli
ls backups
```

Expected file pattern:

```text
AUTOMATED_SWITCH_<timestamp>.cfg
```

Inspect the backup:

```bash
cat backups/AUTOMATED_SWITCH_*.cfg
```

Expected content includes:

```text
hostname AUTOMATED_SWITCH
vlan 10
 name VLAN_DATA
vlan 20
 name VLAN_VOICE
vlan 50
 name VLAN_SECURITY
```

## 7. Run Tests Again Any Time

```bash
cd /Users/thunder/Documents/Meli
source .venv/bin/activate
pytest -q
```

Expected:

```text
26 passed
```

## 8. Optional GNS3 IOSvL2 Test

Use GNS3 when you want to test the real Netmiko SSH path.

Follow:

```text
PART1_FLASK_GNS3_SETUP.md
```

Current GNS3 lab values in that guide:

| Item | Value |
| --- | --- |
| Switch management IP | `192.168.31.50/24` |
| Default gateway | `192.168.31.1` |
| SSH username | `admin` |
| SSH password | `admin` |

Before using the frontend Netmiko driver, verify from macOS:

```bash
ping 192.168.31.50
nc -vz 192.168.31.50 22
```

Optional helper:

```bash
python scripts/device_reachability_check.py 192.168.31.50 --username admin --password admin
```

Then use the app with:

| Field | Value |
| --- | --- |
| Driver | `Netmiko Cisco IOS SSH` |
| Device IP | `192.168.31.50` |
| Username | `admin` |
| Password | `admin` |
| Hostname | `AUTOMATED_SWITCH` or your chosen test hostname |

The app will connect over SSH using Netmiko and run the same workflow as mock mode.

## 9. Part 2 VPN Planning

Part 2 is documentation and planning code for a FortiGate-to-Palo Alto IPSec VPN. It is separate from the Part 1 Flask workflow.

Useful files:

| File | Purpose |
| --- | --- |
| `VPN_PLAN.md` | Written Part 2 automation plan |
| `vpn_planner.py` | Structured VPN plan builder |
| `scripts/generate_vpn_plan.py` | Prints the Part 2 plan as JSON |
| `scripts/vpn_connectivity_check.py` | Optional tunnel ping helper |
| `vpncliexamples/` | FortiGate and Palo Alto conceptual CLI examples |

Generate the JSON plan:

```bash
python scripts/generate_vpn_plan.py
```

## Troubleshooting

If `pip install` fails with network errors, reconnect to the internet and rerun:

```bash
./setup_all.sh
```

If the Flask app cannot start because port 5000 is already in use:

```bash
lsof -i :5000
```

Stop the existing process or change the port in `main.py`.

If real Cisco mode fails:

- Confirm the switch is reachable with `ping`.
- Confirm TCP port 22 is open with `nc -vz <switch-ip> 22`.
- Confirm SSH works manually.
- Confirm the username has privilege to enter configuration mode.
- Confirm the switch is Cisco IOS or IOS-like.
- Confirm no firewall blocks TCP port 22.
