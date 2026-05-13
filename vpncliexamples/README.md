# VPN CLI Examples

This folder contains conceptual CLI examples for Part 2: FortiGate-to-Palo Alto IPSec VPN automation planning.

These files are not used by the Part 1 Flask app. They are review/demo artifacts that show what the generated VPN intent could look like on each firewall vendor. Do not paste them into production without adapting interface names, zones, routes, policies, addresses, NAT behavior, and secret handling for the real environment.

## Files

| File | Purpose |
| --- | --- |
| `fortigate_ipsec_cli.conf` | Conceptual FortiGate IPSec VPN CLI configuration |
| `paloalto_ipsec_set_commands.txt` | Conceptual Palo Alto PAN-OS set commands |

## FortiGate Example

`fortigate_ipsec_cli.conf` shows the FortiGate side of the VPN configuration.

It includes:

- firewall address objects
- Phase 1 VPN configuration
- Phase 2 VPN configuration
- tunnel interface IP `169.255.1.1/30`
- static route to the Palo Alto LAN
- firewall policy allowing VPN traffic

## Palo Alto Example

`paloalto_ipsec_set_commands.txt` shows the Palo Alto side of the VPN configuration.

It includes:

- IKE crypto profile
- IPSec crypto profile
- tunnel interface IP `169.255.1.2/30`
- IKE gateway
- IPSec tunnel
- Proxy-ID
- static route to the FortiGate LAN
- address objects
- security policy
- `commit`

## Relationship to Part 2

The values align with:

- `VPN_PLAN.md`
- `PART2_VPN_DELIVERABLES.md`
- `vpn_planner.py`
- `scripts/generate_vpn_plan.py`

The examples support the written automation plan. They are not a replacement for device-specific API implementation, lab validation, or change review.
