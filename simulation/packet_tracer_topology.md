# Packet Tracer Topology

## Goal

Use Packet Tracer to provide the Cisco switch simulation expected by the assignment.

## Devices

Use this minimal topology:

| Device | Purpose |
| --- | --- |
| Cisco 2960 switch | Simulated Cisco switch target |
| PC or laptop in Packet Tracer | Optional local management host |
| macOS host running Flask app | Automation frontend and Netmiko client |

## Addressing

| Item | Value |
| --- | --- |
| Switch management VLAN | VLAN 1 |
| Switch management IP | `192.168.1.10/24` |
| Default gateway | `192.168.1.1` |
| SSH username | `admin` |
| SSH password | `StrongPassword123` |
| Enable secret | `EnableSecret123` |

## Target Configuration From Flask

| Item | Value |
| --- | --- |
| Hostname | `AUTOMATED_SWITCH` |
| VLAN 10 | `VLAN_DATA` |
| VLAN 20 | `VLAN_VOICE` |
| VLAN 50 | `VLAN_SECURITY` |

## Build Steps

1. Open Cisco Packet Tracer.
2. Add a Cisco 2960 switch.
3. Configure the switch with `switch_initial_setup.txt`.
4. Confirm SSH is enabled on the switch.
5. If your Packet Tracer version exposes the switch to the macOS host network, test from Terminal:

```bash
ping 192.168.1.10
ssh admin@192.168.1.10
```

6. If direct host-to-Packet-Tracer SSH is unavailable, still use this topology for CLI verification and use mock mode for automated local testing.

## Expected CLI Verification

After running the Flask app in Netmiko mode, verify on the switch:

```text
show run | include hostname
show vlan brief
show running-config | section vlan
```

Expected output includes:

```text
hostname AUTOMATED_SWITCH
10   VLAN_DATA
20   VLAN_VOICE
50   VLAN_SECURITY
```
