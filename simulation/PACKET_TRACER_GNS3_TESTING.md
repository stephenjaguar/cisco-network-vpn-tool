# Part 1 Simulation Testing: Packet Tracer and GNS3

This guide explains how to test the Cisco switch automation workflow with either Packet Tracer or GNS3.

## What You Are Testing

The Flask frontend sends the submitted hostname and VLAN configuration to a Cisco IOS-like switch through Netmiko SSH.

Required assignment policy:

| VLAN ID | Name |
| --- | --- |
| `10` | `VLAN_DATA` |
| `20` | `VLAN_VOICE` |
| `50` | `VLAN_SECURITY` |

Required hostname:

```text
AUTOMATED_SWITCH
```

Expected frontend result:

```text
Compliance: COMPLIANT
```

## Option 1: Packet Tracer

### 1. Build the Topology

Open Cisco Packet Tracer and add:

```text
Cisco 2960 switch
```

Use this management IP:

```text
192.168.1.10/24
```

### 2. Configure SSH on the Switch

In the Packet Tracer switch CLI, paste:

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

### 3. Test SSH From macOS

From Terminal:

```bash
ping 192.168.1.10
ssh admin@192.168.1.10
```

If SSH works, continue to the Flask test.

### 4. Start the Flask App

```bash
cd ~/Learning/cisco-network-vpn-tool
source .venv/bin/activate
python main.py
```

Open:

```text
http://127.0.0.1:5000
```

### 5. Use Netmiko Mode

In the frontend:

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

### 6. Verify on the Switch CLI

```text
show run | include hostname
show vlan brief
show running-config | section vlan
```

Expected:

```text
hostname AUTOMATED_SWITCH
10   VLAN_DATA
20   VLAN_VOICE
50   VLAN_SECURITY
```

### Packet Tracer Limitation

Some Packet Tracer versions do not expose the simulated switch SSH service directly to the macOS host network. If `ssh admin@192.168.1.10` fails from macOS even though the switch CLI config is correct:

- Use Packet Tracer CLI to verify the switch-side commands.
- Use the app's `Mock Cisco IOS Driver` to verify the full automation workflow locally.
- Document that Packet Tracer host-to-simulation SSH was unavailable in your environment.

## Option 2: GNS3

Use GNS3 if you have a Cisco IOSvL2, IOSv, or another Cisco IOS-like switch image available. GNS3 images are not included in this repository.

### 1. Create the GNS3 Topology

Recommended topology:

```text
macOS host
  |
GNS3 cloud / NAT / host-only network
  |
Cisco IOSvL2 switch
```

Recommended addressing:

| Item | Value |
| --- | --- |
| Switch management IP | `192.168.122.10/24` |
| Default gateway | `192.168.122.1` |
| SSH username | `admin` |
| SSH password | `StrongPassword123` |
| Enable secret | `EnableSecret123` |

You can use a different subnet if your GNS3 host-only or NAT network uses another range.

### 2. Configure the GNS3 Switch

On the Cisco switch CLI:

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
 ip address 192.168.122.10 255.255.255.0
 no shutdown
exit
ip default-gateway 192.168.122.1
end
write memory
```

If your IOS image uses a routed interface instead of SVI management, configure the reachable interface IP instead of `interface vlan 1`.

### 3. Test Reachability From macOS

```bash
ping 192.168.122.10
ssh admin@192.168.122.10
```

If ping fails:

- Confirm the GNS3 cloud/NAT/host-only adapter is connected.
- Confirm the switch interface is up.
- Confirm macOS has a route to the GNS3 subnet.

If SSH fails:

- Confirm RSA keys were generated.
- Confirm `ip ssh version 2`.
- Confirm VTY lines use `login local` and `transport input ssh`.
- Confirm the username has privilege 15.

### 4. Start the Flask App

```bash
cd ~/Learning/cisco-network-vpn-tool
source .venv/bin/activate
python main.py
```

Open:

```text
http://127.0.0.1:5000
```

### 5. Use Netmiko Mode

In the frontend:

| Field | Value |
| --- | --- |
| Driver | `Netmiko Cisco IOS SSH` |
| Device IP | `192.168.122.10` |
| Username | `admin` |
| Password | `StrongPassword123` |
| Hostname | `AUTOMATED_SWITCH` |
| VLAN row 1 | `10`, `VLAN_DATA` |
| VLAN row 2 | `20`, `VLAN_VOICE` |
| VLAN row 3 | `50`, `VLAN_SECURITY` |

Click `Run Automation`.

### 6. Verify on GNS3 Switch CLI

```text
show run | include hostname
show vlan brief
show running-config | section vlan
```

Expected:

```text
hostname AUTOMATED_SWITCH
10   VLAN_DATA
20   VLAN_VOICE
50   VLAN_SECURITY
```

## Expected Backup

After a successful run, the app creates a clickable backup link in the frontend:

```text
backups/AUTOMATED_SWITCH_<timestamp>.cfg
```

Click the link to open the saved running configuration in the browser.

## Expected Non-Compliance Test

To prove alerting works:

1. Keep VLAN ID `10`.
2. Change its name to `USERS`.
3. Submit the form.

Expected result:

```text
Compliance: NON_COMPLIANT
VLAN 10 mismatch: expected VLAN_DATA, got USERS
```

## Local Mock Fallback

If Packet Tracer or GNS3 SSH cannot be reached from macOS, use:

```text
Driver: Mock Cisco IOS Driver
```

Mock mode verifies:

- Frontend form submission.
- VLAN and hostname command generation.
- Backup file generation.
- Compliance validation.
- Alert display.

Run automated tests with:

```bash
cd ~/Learning/cisco-network-vpn-tool
source .venv/bin/activate
pytest -v
```

Expected:

```text
13 passed
```
