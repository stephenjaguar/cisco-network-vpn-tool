# Flask Frontend Test Against Packet Tracer

## Start the App

```bash
cd ~/Learning/cisco-network-vpn-tool
source .venv/bin/activate
python main.py
```

Open:

```text
http://127.0.0.1:5000
```

## Frontend Values

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

## Expected Frontend Result

```text
Compliance: COMPLIANT
Hostname: PASS
VLAN 10: PASS
VLAN 20: PASS
VLAN 50: PASS
```

## Expected Backup

The app should create a file matching:

```text
backups/AUTOMATED_SWITCH_<timestamp>.cfg
```
