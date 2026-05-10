# Test Plan: Cisco Network Automation & IPSec VPN Planning Tool

## Objective

Verify that the project works as an interview-ready demo without requiring GNS3, EVE-NG, VMware, VirtualBox, or a physical Cisco switch. The default validation path uses the in-process `MockSwitchDriver`.

## Scope

This test plan verifies:

- Python environment setup.
- Mock Cisco switch automation.
- Hostname and VLAN configuration logic.
- Running-config backup creation.
- Compliance validation.
- Flask UI workflow.
- Documentation deliverables.

Real Cisco SSH testing through Netmiko is out of scope unless a lab switch, Cisco CML image, DevNet sandbox, or Containerlab Cisco IOL image is available.

## Environment

- macOS on Apple Silicon or Intel.
- Python 3.10 or newer.
- Project path: `~/Learning/cisco-network-vpn-tool`.
- Default driver: `Mock Cisco IOS Driver`.

## Setup Verification

Run:

```bash
cd ~/Learning/cisco-network-vpn-tool
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
cd ~/Learning/cisco-network-vpn-tool
source .venv/bin/activate
pytest -v
```

Expected result:

```text
7 passed
```

The automated tests verify:

- `MockSwitchDriver` applies hostname changes.
- `MockSwitchDriver` applies VLAN 10, 20, and 50.
- `MockSwitchDriver` returns Cisco-like `show vlan brief` output.
- `MockSwitchDriver` writes a local backup config.
- Validator returns `COMPLIANT` when intended state matches observed output.
- Validator returns `NON_COMPLIANT` for missing VLANs.
- Validator returns `NON_COMPLIANT` for wrong VLAN names.
- Validator returns `NON_COMPLIANT` for hostname mismatch.
- Flask POST workflow runs the full mock automation path and renders `COMPLIANT`.
- Flask POST workflow creates a backup file.

## Manual UI Test

Start the app:

```bash
cd ~/Learning/cisco-network-vpn-tool
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
| Driver | Mock Cisco IOS Driver |
| Device IP | `192.0.2.10` |
| Username | `admin` |
| Password | `admin` |
| Hostname | `AUTOMATED_SWITCH` |

Expected page result:

- Automation command output is displayed.
- Backup file path is displayed.
- Compliance status is `COMPLIANT`.
- Hostname check is `PASS`.
- VLAN 10 check is `PASS`.
- VLAN 20 check is `PASS`.
- VLAN 50 check is `PASS`.

Verify backup file:

```bash
ls backups
```

Expected result:

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

## Negative Validation Tests

These are covered by `pytest`, but they can also be explained in the interview:

- Missing VLAN 50 should produce `NON_COMPLIANT`.
- VLAN 20 named incorrectly should produce `NON_COMPLIANT`.
- Hostname different from `AUTOMATED_SWITCH` should produce `NON_COMPLIANT`.

The validator reports exact mismatch alerts so the operator can see which intended state failed.

## Documentation Verification

Confirm the required deliverables exist:

```bash
ls README.md VPN_PLAN.md TEST_PLAN.md main.py driver.py validator.py setup.sh
```

Expected result:

- `README.md` explains setup, mock mode, and real Netmiko mode.
- `VPN_PLAN.md` documents FortiGate-to-Palo Alto IPSec VPN automation.
- `TEST_PLAN.md` documents setup, automated tests, manual tests, and expected results.

## Pass Criteria

The project is considered working when:

- `pytest -v` returns all tests passing.
- The Flask app loads at `http://127.0.0.1:5000`.
- Submitting the default mock form returns `COMPLIANT`.
- A backup config file is generated under `backups/`.
- `README.md`, `VPN_PLAN.md`, and `TEST_PLAN.md` are present and complete.

## Known Limitations

- Mock mode verifies logic, not real Cisco SSH reachability.
- Netmiko mode requires a reachable Cisco IOS device and valid credentials.
- PAN-OS REST endpoints can vary by PAN-OS version, so production automation should confirm resource URIs from `https://<PANOS_HOST>/restapi`.
