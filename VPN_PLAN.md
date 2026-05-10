# FortiGate to Palo Alto IPSec VPN Automation Plan

## Overview

This document describes how to automate an IPSec VPN between a FortiGate firewall and a Palo Alto firewall. The plan focuses on repeatable configuration flow, API touchpoints, and multi-vendor interoperability checks.

## Sample Topology and VPN Parameters

| Item | Value |
| --- | --- |
| FortiGate device name | `FGT-BRANCH` |
| Palo Alto device name | `PA-DC` |
| FortiGate WAN IP | `198.51.100.10` |
| Palo Alto WAN IP | `203.0.113.20` |
| FortiGate protected subnet | `10.10.10.0/24` |
| Palo Alto protected subnet | `10.20.20.0/24` |
| FortiGate tunnel interface | `vpn-pa-dc` |
| Palo Alto tunnel interface | `tunnel.10` |
| IKE version | IKEv2 |
| Phase 1 encryption | AES-256 |
| Phase 1 authentication | SHA-256 |
| Phase 1 DH group | Group 14 |
| Phase 1 lifetime | 28800 seconds |
| Phase 2 encryption | AES-256 |
| Phase 2 authentication | SHA-256 |
| PFS | Group 14 |
| Phase 2 lifetime | 3600 seconds |
| Tunnel subnet | `169.255.1.0/30` |
| FortiGate tunnel IP | `169.255.1.1/30` |
| Palo Alto tunnel IP | `169.255.1.2/30` |
| Authentication | Pre-shared key |
| Pre-shared key example | Store in a secret manager, not in source control |

Example Proxy-ID / traffic selectors:

| Side | Local Selector | Remote Selector |
| --- | --- | --- |
| FortiGate | `10.10.10.0/24` | `10.20.20.0/24` |
| Palo Alto | `10.20.20.0/24` | `10.10.10.0/24` |

Selectors should use protocol `any` and ports `any` unless the design intentionally narrows traffic.

## API Endpoints and Tools

FortiOS uses CMDB REST endpoints for configuration operations:

- `POST /api/v2/cmdb/vpn.ipsec/phase1-interface/`
- `POST /api/v2/cmdb/vpn.ipsec/phase2-interface/`
- `POST /api/v2/cmdb/system/interface/`
- `POST /api/v2/cmdb/firewall/address/`
- `POST /api/v2/cmdb/firewall/policy/`
- `POST /api/v2/cmdb/router/static/`

FortiGate status and validation can use monitor endpoints or SSH commands:

- `GET /api/v2/monitor/vpn/ipsec`
- `GET /api/v2/monitor/router/lookup`
- `diagnose vpn tunnel list`
- `get vpn ipsec tunnel summary`
- `get router info routing-table details 10.20.20.0`

PAN-OS supports REST API configuration for many objects and policies. The exact resource URIs are version-specific and should be confirmed from the target firewall at:

```text
https://<PANOS_HOST>/restapi
```

Likely PAN-OS automation resources include:

- Address objects
- IKE crypto profile
- IPSec crypto profile
- Tunnel interface
- IKE gateway
- IPSec tunnel
- IPSec tunnel Proxy-ID
- Virtual router static route
- Security policy

PAN-OS REST configuration changes may still require a commit operation through XML API or another management interface before they become active.

PAN-OS validation can use operational API calls or CLI commands:

- `show vpn ike-sa`
- `show vpn ipsec-sa`
- `show routing route destination 10.10.10.0/24`
- `test vpn ike-sa gateway <gateway-name>`
- `test vpn ipsec-sa tunnel <tunnel-name>`
- XML API operation calls with `type=op`

References:

- Fortinet VPN configuration APIs: https://docs.fortinet.com/document/fortigate/7.2.0/secgw-for-mobile-networks-deployment/305564/vpn-configuration-apis
- PAN-OS REST API: https://pan.dev/panos/docs/restapi/
- PAN-OS REST request structure: https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-panorama-api/get-started-with-the-pan-os-rest-api/pan-os-rest-api-request-response-structure.html
- PAN-OS IPSec tunnels: https://docs.paloaltonetworks.com/pan-os/11-0/pan-os-web-interface-help/network/network-ipsec-tunnels

## Automation Logic Flow

1. Validate inputs.
   - Peer public IPs: `198.51.100.10` and `203.0.113.20`
   - Protected subnets: `10.10.10.0/24` and `10.20.20.0/24`
   - Tunnel interface IDs: `vpn-pa-dc` and `tunnel.10`
   - Pre-shared key secret reference
   - Routing targets and zones

2. Create network objects.
   - FortiGate local subnet object: `FGT_LAN_10.10.10.0_24`
   - Palo Alto local subnet object: `PA_LAN_10.20.20.0_24`
   - Remote subnet objects on the opposite devices
   - Optional peer gateway object

3. Create tunnel interfaces.
   - FortiGate tunnel interface with `169.255.1.1/30`
   - Palo Alto tunnel interface with `169.255.1.2/30`
   - Assign interfaces to appropriate zones.

4. Configure Phase 1 / IKE.
   - IKEv2
   - AES-256
   - SHA-256
   - DH Group 14
   - Peer gateway IP
   - Pre-shared key secret

5. Configure Phase 2 / IPSec.
   - AES-256
   - SHA-256
   - PFS Group 14
   - Proxy-ID / traffic selectors
   - Replay protection and lifetimes aligned across vendors

6. Configure routing.
   - FortiGate route: `10.20.20.0/24` through `vpn-pa-dc`
   - Palo Alto route: `10.10.10.0/24` through `tunnel.10`
   - Confirm return routes exist on both sides.

7. Configure security policy.
   - Permit local-to-remote VPN traffic.
   - Permit remote-to-local VPN traffic when required.
   - Apply logging based on operational policy.

8. Commit or apply configuration.
   - FortiGate CMDB changes apply through the FortiOS configuration system.
   - PAN-OS changes require commit before becoming active.

9. Validate.
   - Confirm IKE Phase 1 is established.
   - Confirm IPSec Phase 2 SA is established.
   - Test route lookup.
   - Test traffic across the tunnel.
   - Check logs for selector, proposal, NAT-T, or policy denies.

## Interoperability Challenges

Proxy-ID and traffic-selector mismatches are one of the most common FortiGate-to-Palo Alto VPN issues. The local selector on one firewall must mirror the remote selector on the other firewall. For example, if FortiGate local is `10.10.10.0/24` and remote is `10.20.20.0/24`, then Palo Alto local must be `10.20.20.0/24` and remote must be `10.10.10.0/24`.

Other common mismatches:

- IKE version mismatch, especially IKEv1 versus IKEv2.
- Phase 1 proposal mismatch.
- Phase 2 proposal mismatch.
- PFS enabled on one side but disabled on the other.
- Lifetime mismatch causing unstable rekey behavior.
- NAT-T behavior mismatch.
- Missing static routes.
- Security policy allows one direction but not the return path.
- PAN-OS candidate config not committed.

## Validation Outputs

An automation workflow should produce a report containing:

- Created or updated objects.
- Phase 1 proposal on both peers.
- Phase 2 proposal on both peers.
- Proxy-ID / selector comparison.
- Route table checks.
- Policy checks.
- Tunnel status.
- Any mismatches requiring operator review.

## Validation and Alerting Strategy

The automation should validate both configuration state and operational state after applying changes.

Configuration checks:

- Phase 1 proposal equals AES-256/SHA-256/DH14/IKEv2 on both devices.
- Phase 2 proposal equals AES-256/SHA-256/PFS14 on both devices.
- FortiGate selector local/remote equals `10.10.10.0/24` to `10.20.20.0/24`.
- Palo Alto Proxy-ID mirrors that selector as `10.20.20.0/24` to `10.10.10.0/24`.
- Static routes exist for the opposite protected subnet.
- Security policies allow traffic in the required direction.

Operational checks:

- FortiGate IKE SA is established.
- FortiGate IPSec SA is established.
- Palo Alto IKE SA is established.
- Palo Alto IPSec SA is established.
- Test traffic can pass from `10.10.10.0/24` to `10.20.20.0/24`.

Alert conditions:

- `VPN_DOWN`: IKE or IPSec SA is missing on either device.
- `PROXY_ID_MISMATCH`: local and remote selectors are not mirrored correctly.
- `PROPOSAL_MISMATCH`: Phase 1 or Phase 2 crypto settings differ.
- `ROUTE_MISSING`: remote protected subnet is not routed through the tunnel.
- `POLICY_MISSING`: firewall policy does not permit VPN traffic.
- `COMMIT_PENDING`: PAN-OS candidate configuration has not been committed.

Alerts should include the expected value, observed value, device name, and remediation hint. For example:

```text
PROXY_ID_MISMATCH on PA-DC: expected local 10.20.20.0/24 remote 10.10.10.0/24, observed local 10.10.10.0/24 remote 10.20.20.0/24.
```
