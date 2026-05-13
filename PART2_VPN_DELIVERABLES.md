# Part 2 VPN Deliverables

This file is the review index for the FortiGate-to-Palo Alto IPSec VPN planning requirement.

## Where Each Requirement Is Covered

| Evaluation Item | Repository Artifact |
| --- | --- |
| Understanding of IPSec VPN concepts | `VPN_PLAN.md` sections: Overview, Automation Logic Flow, Interoperability Challenges |
| Correct VPN parameter definition | `VPN_PLAN.md` section: Sample Topology and VPN Parameters |
| Quality and feasibility of automation plan | `VPN_PLAN.md` section: Automation Logic Flow |
| FortiGate tools/APIs | `VPN_PLAN.md` section: API Endpoints and Tools |
| Palo Alto tools/APIs | `VPN_PLAN.md` section: API Endpoints and Tools |
| Heterogeneous vendor challenges | `VPN_PLAN.md` section: Interoperability Challenges |
| VPN validation strategy | `VPN_PLAN.md` section: Validation and Alerting Strategy |
| Alert handling | `VPN_PLAN.md` section: Validation and Alerting Strategy |
| Optional FortiGate example | `vpncliexamples/fortigate_ipsec_cli.conf` |
| Optional Palo Alto example | `vpncliexamples/paloalto_ipsec_set_commands.txt` |
| Optional connectivity test script | `scripts/vpn_connectivity_check.py` |

## VPN Parameter Summary

| Parameter | Value |
| --- | --- |
| FortiGate WAN IP | `198.51.100.10` |
| Palo Alto WAN IP | `203.0.113.20` |
| FortiGate LAN | `10.10.10.0/24` |
| Palo Alto LAN | `10.20.20.0/24` |
| Tunnel subnet | `169.255.1.0/30` |
| FortiGate tunnel IP | `169.255.1.1/30` |
| Palo Alto tunnel IP | `169.255.1.2/30` |
| IKE version | IKEv2 |
| Phase 1 proposal | AES-256, SHA-256, DH Group 14 |
| Phase 2 proposal | AES-256, SHA-256, PFS Group 14 |

## Proxy-ID / Selector Mapping

| Device | Local Selector | Remote Selector |
| --- | --- | --- |
| FortiGate | `10.10.10.0/24` | `10.20.20.0/24` |
| Palo Alto | `10.20.20.0/24` | `10.10.10.0/24` |

The selectors are intentionally mirrored. A selector mismatch is called out in `VPN_PLAN.md` as a high-risk multi-vendor failure mode.

## Optional Connectivity Test

The connectivity helper is intentionally simple because a working VPN lab is not required by the assignment.

Example usage:

```bash
python scripts/vpn_connectivity_check.py 10.20.20.10 --count 3
```

Expected success output:

```text
VPN_CONNECTIVITY_OK target=10.20.20.10
```

Expected failure output:

```text
VPN_CONNECTIVITY_FAILED target=10.20.20.10
```
