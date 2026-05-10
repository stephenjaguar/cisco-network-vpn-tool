# Packet Tracer Cisco Switch Simulation Guide

This guide explains how to satisfy the assignment simulation requirement using Cisco Packet Tracer and the app's `Netmiko Cisco IOS SSH` driver.

## Goal

Create a simulated Cisco switch that accepts SSH from the Mac, then use the Flask frontend to configure:

- Hostname: `AUTOMATED_SWITCH`
- VLAN 10: `VLAN_DATA`
- VLAN 20: `VLAN_VOICE`
- VLAN 50: `VLAN_SECURITY`

## Important Note

Packet Tracer support for external SSH access depends on the Packet Tracer version, host networking behavior, and device model. If direct SSH from macOS into Packet Tracer is unavailable, use the same Cisco IOS commands in Packet Tracer CLI to demonstrate the equivalent device-side configuration, and use mock mode for automated unit testing.

## Packet Tracer Topology

Use a simple topology:

```text
Mac running Flask app
  |
Packet Tracer network
  |
Cisco switch
```

Recommended switch management settings:

| Item | Value |
| --- | --- |
| Switch management IP | `192.168.1.10/24` |
| Default gateway | `192.168.1.1` |
| SSH username | `admin` |
| SSH password | `StrongPassword123` |
| Enable secret | `EnableSecret123` |

## Cisco Switch SSH Preparation

Run these commands on the Packet Tracer switch:

```text
enable
configure terminal
hostname LAB-SW1
ip domain-name lab.local
enable secret EnableSecret123
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

## macOS Reachability Test

From Terminal:

```bash
ping 192.168.1.10
ssh admin@192.168.1.10
```

If SSH succeeds, Packet Tracer is ready for the app's Netmiko mode.

## Run the Flask App

```bash
cd ~/Learning/cisco-network-vpn-tool
source .venv/bin/activate
python main.py
```

Open:

```text
http://127.0.0.1:5000
```

Use these frontend values:

| Field | Value |
| --- | --- |
| Driver | `Netmiko Cisco IOS SSH` |
| Device IP | `192.168.1.10` |
| Username | `admin` |
| Password | `StrongPassword123` |
| Hostname | `AUTOMATED_SWITCH` |
| VLAN row 1 | `10`, `VLAN_DATA` |
| VLAN row 2 | `20`, `VLAN_VOICE` |
| VLAN row 3 | `50`, `VLAN_SECURITY` |

Click `Run Automation`.

## Expected Validation

The app should display:

```text
Compliance: COMPLIANT
Hostname: PASS
VLAN 10: PASS
VLAN 20: PASS
VLAN 50: PASS
```

The app should also create:

```text
backups/AUTOMATED_SWITCH_<timestamp>.cfg
```

## Manual CLI Verification

On the switch CLI:

```text
show vlan brief
show run | include hostname
show running-config | section vlan
```

Expected output should include:

```text
hostname AUTOMATED_SWITCH
10   VLAN_DATA
20   VLAN_VOICE
50   VLAN_SECURITY
```

## Troubleshooting

- If `ping` fails, confirm the Packet Tracer IP addressing and host connectivity.
- If SSH fails, confirm RSA keys, `ip ssh version 2`, VTY login, and local username.
- If Netmiko login fails, confirm username/password and privilege level.
- If validation fails, compare the frontend VLAN intent against `show vlan brief`.
- If Packet Tracer cannot expose SSH to macOS, use mock mode for app validation and Packet Tracer CLI for device-command demonstration.
