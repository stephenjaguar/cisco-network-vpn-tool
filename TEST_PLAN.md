# Test Plan: Cisco IOS Switch Automation and VPN Planning

## Objective

Verify the current repository behavior without requiring a live Cisco switch. The default validation path uses the in-process `MockSwitchDriver`, while GNS3 IOSvL2 can be used for optional real SSH testing with Netmiko.

## Scope

This test plan verifies:

- Python environment setup.
- Flask frontend workflow.
- Mock Cisco switch automation.
- Hostname and VLAN configuration logic.
- Optional additional VLAN input.
- Running-config backup creation.
- Compliance validation.
- Part 2 VPN planning helpers.
- Documentation/demo artifacts.

## Environment

- macOS on Apple Silicon or Intel.
- Python 3.10 or newer.
- Project path: `/Users/thunder/Documents/Meli`.
- Default driver: `Mock Cisco IOS Driver`.
- Optional emulator: GNS3 IOSvL2.

## Setup Verification

Run:

```bash
cd /Users/thunder/Documents/Meli
chmod +x setup.sh
./setup.sh
source .venv/bin/activate
```

Expected result:

- `.venv/` exists.
- Required packages install successfully.
- `pytest`, `flask`, and `netmiko` are available inside the virtual environment.

Optional checks:

```bash
python --version
python -c "import flask, netmiko, pytest; print('dependencies ok')"
```

Expected result:

```text
dependencies ok
```

## Automated Test Execution

Run:

```bash
cd /Users/thunder/Documents/Meli
source .venv/bin/activate
pytest -q
```

Expected result:

```text
26 passed
```

The automated tests verify:

- `MockSwitchDriver` applies hostname changes.
- `MockSwitchDriver` applies VLAN 10, VLAN 20, and VLAN 50.
- `MockSwitchDriver` returns Cisco-like `show vlan brief` output.
- `MockSwitchDriver` writes a local backup config.
- `NetmikoSwitchDriver` uses 15 second connection/auth/banner timeouts.
- `NetmikoSwitchDriver` uses 60 second command read timeouts.
- `NetmikoSwitchDriver` uses a generic IOS prompt pattern for `>` or `#`.
- Flask renders the default frontend values.
- Flask workflow accepts required VLAN rows and optional additional VLAN input.
- Flask workflow reports `COMPLIANT` when observed output matches intended hostname and required VLANs.
- Flask workflow reports `NON_COMPLIANT` when required VLAN names do not match.
- Flask workflow rejects non-numeric VLAN IDs.
- Flask workflow rejects duplicate VLAN IDs.
- Validator returns `COMPLIANT` and `NON_COMPLIANT` reports correctly.
- Part 1 reachability helpers build expected ping/TCP checks.
- Part 2 VPN planner builds required parameters, mirrored selectors, tools, steps, validation checks, and alerts.
- Part 2 VPN connectivity helper builds the correct platform-specific ping command.

## Manual UI Test

Start the app:

```bash
cd /Users/thunder/Documents/Meli
source .venv/bin/activate
python main.py
```

Open:

```text
http://127.0.0.1:5000
```

Submit the form with:

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

Expected page result:

- Automation command output is displayed.
- Backup file path is displayed as a clickable link.
- Compliance status is `COMPLIANT`.
- Hostname check is `PASS`.
- VLAN 10 check is `PASS`.
- VLAN 20 check is `PASS`.
- VLAN 50 check is `PASS`.

The optional additional VLAN is pushed to the switch when provided, but it is not part of the compliance report.

## Negative Validation Test

Submit the form with VLAN 10 changed to `USERS`:

| Field | Value |
| --- | --- |
| VLAN row 1 | `10`, `USERS` |
| VLAN row 2 | `20`, `VLAN_VOICE` |
| VLAN row 3 | `50`, `VLAN_SECURITY` |

Expected page result:

- Compliance status is `NON_COMPLIANT`.
- An alert explains that VLAN 10 expected `VLAN_DATA` but observed `USERS`.

Other expected non-compliant cases:

- Missing VLAN 50.
- VLAN 20 named incorrectly.
- Hostname observed from the switch does not match the hostname submitted in the frontend.

## Backup Verification

After a successful run:

```bash
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

If an optional additional VLAN was submitted, the backup should include it too.

## Optional GNS3 Netmiko Test

Use `PART1_FLASK_GNS3_SETUP.md` for the GNS3 IOSvL2 setup. The expected switch management IP in that guide is:

```text
192.168.31.50/24
```

Before using Netmiko mode, verify from macOS:

```bash
ping 192.168.31.50
nc -vz 192.168.31.50 22
```

You can also run:

```bash
python scripts/device_reachability_check.py 192.168.31.50 --username admin --password admin
```

## Documentation Verification

Confirm the required deliverables exist:

```bash
ls README.md VPN_PLAN.md TEST_PLAN.md SETUP_GUIDE.md PART1_FLASK_GNS3_SETUP.md
ls main.py driver.py validator.py vpn_planner.py
ls demoresult vpncliexamples templates/README.md
```

Expected result:

- `README.md` explains Part 1 and Part 2.
- `VPN_PLAN.md` documents FortiGate-to-Palo Alto IPSec VPN automation planning.
- `TEST_PLAN.md` documents setup, automated tests, manual tests, and expected results.
- `PART1_FLASK_GNS3_SETUP.md` documents the GNS3 IOSvL2 simulation path.
- `demoresult/` contains Part 1 screenshots.
- `vpncliexamples/` contains Part 2 CLI examples.

## Pass Criteria

The project is considered working when:

- `pytest -q` returns `26 passed`.
- The Flask app loads at `http://127.0.0.1:5000`.
- Submitting the default mock form returns `COMPLIANT`.
- A backup config file is generated under `backups/`.
- Required documentation and demo artifacts are present.

## Known Limitations

- Mock mode verifies logic, not real Cisco SSH reachability.
- Netmiko mode requires a reachable Cisco IOS or IOS-like device and valid credentials.
- GNS3 reachability depends on the local GNS3 network/cloud/NAT setup.
- PAN-OS REST endpoints can vary by PAN-OS version, so production automation should confirm resource URIs from `https://<PANOS_HOST>/restapi`.
