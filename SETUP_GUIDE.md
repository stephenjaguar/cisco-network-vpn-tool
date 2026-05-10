# Step-by-Step Setup Guide

This guide sets up the Cisco Network Automation & IPSec VPN Planning Tool on macOS. The default demo path uses a Python mock Cisco switch, so you do not need GNS3, EVE-NG, VMware, VirtualBox, or a physical Cisco switch.

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
cd ~/Learning/cisco-network-vpn-tool
```

## 3. Run the One-Command Setup

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
| Driver | Mock Cisco IOS Driver |
| Device IP | `192.0.2.10` |
| Username | `admin` |
| Password | `admin` |
| Hostname | `AUTOMATED_SWITCH` |
| VLAN row 1 | `10`, `VLAN_DATA` |
| VLAN row 2 | `20`, `VLAN_VOICE` |
| VLAN row 3 | `50`, `VLAN_SECURITY` |

Click `Run Automation`.

Expected:

- Compliance status is `COMPLIANT`.
- Hostname check is `PASS`.
- VLAN 10, VLAN 20, and VLAN 50 checks are `PASS`.
- A backup path is shown.

You can also edit the VLAN rows before submitting. The app will apply the submitted VLANs, then validate the resulting switch state against the required assignment VLAN policy.

Compliance is intentionally checked against the assignment VLAN policy. If VLAN 10 is not named `VLAN_DATA`, VLAN 20 is not named `VLAN_VOICE`, or VLAN 50 is not named `VLAN_SECURITY`, the result should be `NON_COMPLIANT`.

## 6. Verify Backup File

In a second Terminal window:

```bash
cd ~/Learning/cisco-network-vpn-tool
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
cd ~/Learning/cisco-network-vpn-tool
source .venv/bin/activate
pytest -v
```

Expected:

```text
12 passed
```

## 8. Open the Interview Explanation Page

Open this file in your browser:

```text
~/Learning/cisco-network-vpn-tool/interview_overview.html
```

It explains the thinking behind the design, why mock mode was used, how validation works, and how to connect to a real physical Cisco switch.

## 9. Real Cisco Switch Connection Checklist

Only use real device mode on a lab switch or a switch where you have permission to make changes.

For the assignment's Packet Tracer simulation path, follow `simulation/README.md` and `PACKET_TRACER_SETUP.md`. The same Netmiko mode is used whether the SSH target is a Packet Tracer switch or a physical Cisco switch.

On the Cisco switch, SSH must be enabled. Example Cisco IOS preparation:

```text
enable
configure terminal
hostname LAB-SW1
ip domain-name lab.local
username admin privilege 15 secret StrongPassword123
crypto key generate rsa modulus 2048
ip ssh version 2
line vty 0 4
 login local
 transport input ssh
exit
interface vlan 1
 ip address 192.168.1.10 255.255.255.0
 no shutdown
exit
ip default-gateway 192.168.1.1
end
write memory
```

From your Mac, verify reachability:

```bash
ping 192.168.1.10
ssh admin@192.168.1.10
```

Then use the app with:

| Field | Value |
| --- | --- |
| Driver | Netmiko Cisco IOS SSH |
| Device IP | Real switch management IP |
| Username | Cisco local username |
| Password | Cisco local password |
| Hostname | Desired switch hostname |

The app will connect over SSH using Netmiko and run the same workflow as mock mode.

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
- Confirm SSH works manually.
- Confirm the username has privilege to enter configuration mode.
- Confirm the switch is Cisco IOS or IOS-like.
- Confirm no firewall blocks TCP port 22.
