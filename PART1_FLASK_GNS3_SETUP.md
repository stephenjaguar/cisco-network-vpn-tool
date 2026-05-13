# GNS3 Cisco IOSvL2 Switch Simulation Guide

This guide explains how to satisfy the Part 1 simulation requirement using GNS3 and the app's `Netmiko Cisco IOS SSH` driver.

## Goal

Create a GNS3 IOSvL2 switch that accepts SSH from the Mac, then use the Flask frontend to configure:

- Hostname: `AUTOMAT`
- VLAN 10: `VLAN_DATA`
- VLAN 20: `VLAN_VOICE`
- VLAN 50: `VLAN_SECURITY`

## GNS3 Topology

Use a simple topology:

```text
Mac running Flask app
  |
GNS3 management/cloud network
  |
IOSvL2 switch
```

Switch management settings:

| Item | Value |
| --- | --- |
| Switch management IP | `192.168.31.50/24` |
| Default gateway | `192.168.31.1` |
| SSH username | `admin` |
| SSH password | `admin` |
| Enable secret | `admin` |

## Cisco IOSvL2 SSH Preparation

Run these commands on the GNS3 IOSvL2 switch console:

```text
enable
configure terminal
hostname GNS3-SW
ip domain-name lab.local
enable secret admin
username admin privilege 15 secret admin
crypto key generate rsa modulus 2048
ip ssh version 2
line vty 0 4
 login local
 transport input ssh
exit
interface vlan 1
 ip address 192.168.31.50 255.255.255.0
 no shutdown
exit
ip default-gateway 192.168.31.1
end
write memory
```

Make sure at least one switch port in VLAN 1 is up. If no VLAN 1 port is up, `interface vlan 1` may stay down and SSH will not work.

## macOS Reachability Test

From Terminal:

```bash
ping 192.168.31.50
nc -vz 192.168.31.50 22
ssh admin@192.168.31.50
```

If TCP port `22` succeeds, the GNS3 switch is ready for the app's Netmiko mode.

You can also run the repository helper:

```bash
python scripts/device_reachability_check.py 192.168.31.50 --username admin --password admin
```

## Run the Flask App

```bash
cd /Users/thunder/Documents/Meli
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
| Device IP | `192.168.31.50` |
| Username | `admin` |
| Password | `admin` |
| Hostname | `AUTOMAT` |
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
backups/AUTOMAT_<timestamp>.cfg
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
hostname AUTOMAT
10   VLAN_DATA
20   VLAN_VOICE
50   VLAN_SECURITY
```

## Troubleshooting

- If `ping` fails, confirm the GNS3 cloud/NAT connection, switch SVI IP, subnet, and Mac routing.
- If TCP port `22` fails, confirm RSA keys, `ip ssh version 2`, VTY login, and local username.
- If Netmiko login fails, confirm username/password and privilege level.
- If the SVI is down, connect an active switch port in VLAN 1.
- If validation fails, compare the frontend VLAN intent against `show vlan brief` and `show run | include hostname`.
