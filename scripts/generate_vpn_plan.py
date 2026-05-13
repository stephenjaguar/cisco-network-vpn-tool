"""Generate the Part 2 FortiGate-to-Palo Alto VPN automation plan as JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from vpn_planner import VpnParameters, build_vpn_plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a FortiGate-to-Palo Alto IPSec VPN automation plan"
    )
    parser.add_argument("--fortigate-wan-ip", default=VpnParameters.fortigate_wan_ip)
    parser.add_argument("--paloalto-wan-ip", default=VpnParameters.paloalto_wan_ip)
    parser.add_argument("--fortigate-lan", default=VpnParameters.fortigate_lan)
    parser.add_argument("--paloalto-lan", default=VpnParameters.paloalto_lan)
    parser.add_argument("--tunnel-network", default=VpnParameters.tunnel_network)
    parser.add_argument("--fortigate-tunnel-ip", default=VpnParameters.fortigate_tunnel_ip)
    parser.add_argument("--paloalto-tunnel-ip", default=VpnParameters.paloalto_tunnel_ip)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    params = VpnParameters(
        fortigate_wan_ip=args.fortigate_wan_ip,
        paloalto_wan_ip=args.paloalto_wan_ip,
        fortigate_lan=args.fortigate_lan,
        paloalto_lan=args.paloalto_lan,
        tunnel_network=args.tunnel_network,
        fortigate_tunnel_ip=args.fortigate_tunnel_ip,
        paloalto_tunnel_ip=args.paloalto_tunnel_ip,
    )
    print(json.dumps(build_vpn_plan(params), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
