# FortiGate to Palo Alto IPSec VPN Automation Plan

## Overview

This document describes how to automate an IPSec VPN between a FortiGate firewall and a Palo Alto firewall. The plan focuses on repeatable configuration flow, API touchpoints, and multi-vendor interoperability checks.

## VPN Parameters

| Item | Value |
| --- | --- |
| IKE version | IKEv2 |
| Phase 1 encryption | AES-256 |
| Phase 1 authentication | SHA-256 |
| Phase 1 DH group | Group 14 |
| Phase 2 encryption | AES-256 |
| Phase 2 authentication | SHA-256 |
| PFS | Group 14 |
| Tunnel subnet | `169.255.1.0/30` |
| FortiGate tunnel IP | `169.255.1.1/30` |
| Palo Alto tunnel IP | `169.255.1.2/30` |
| Authentication | Pre-shared key or certificate, depending on policy |

Example Proxy-ID / traffic selectors:

| Side | Local Selector | Remote Selector |
| --- | --- | --- |
| FortiGate | FortiGate protected subnet | Palo Alto protected subnet |
| Palo Alto | Palo Alto protected subnet | FortiGate protected subnet |

Selectors should use protocol `any` and ports `any` unless the design intentionally narrows traffic.

## API Endpoints and Tools

FortiOS uses CMDB REST endpoints for configuration operations:

- `POST /api/v2/cmdb/vpn.ipsec/phase1-interface/`
- `POST /api/v2/cmdb/vpn.ipsec/phase2-interface/`
- `POST /api/v2/cmdb/system/interface/`
- `POST /api/v2/cmdb/firewall/address/`
- `POST /api/v2/cmdb/firewall/policy/`
- `POST /api/v2/cmdb/router/static/`

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

References:

- Fortinet VPN configuration APIs: https://docs.fortinet.com/document/fortigate/7.2.0/secgw-for-mobile-networks-deployment/305564/vpn-configuration-apis
- PAN-OS REST API: https://pan.dev/panos/docs/restapi/
- PAN-OS REST request structure: https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-panorama-api/get-started-with-the-pan-os-rest-api/pan-os-rest-api-request-response-structure.html
- PAN-OS IPSec tunnels: https://docs.paloaltonetworks.com/pan-os/11-0/pan-os-web-interface-help/network/network-ipsec-tunnels

## Automation Logic Flow

1. Validate inputs.
   - Peer public IPs
   - Protected subnets
   - Tunnel interface IDs
   - Pre-shared key or certificate reference
   - Routing targets and zones

2. Create network objects.
   - Local protected subnet object
   - Remote protected subnet object
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
   - Authentication method

5. Configure Phase 2 / IPSec.
   - AES-256
   - SHA-256
   - PFS Group 14
   - Proxy-ID / traffic selectors
   - Replay protection and lifetimes aligned across vendors

6. Configure routing.
   - Add static routes for remote protected subnets through the tunnel interface.
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
