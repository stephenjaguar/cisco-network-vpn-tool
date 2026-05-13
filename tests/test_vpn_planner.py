import pytest

from vpn_planner import VpnParameters, build_vpn_plan, validate_vpn_parameters


def test_build_vpn_plan_contains_required_parameters_and_mirrored_selectors():
    plan = build_vpn_plan()
    parameters = plan["parameters"]

    assert parameters["fortigate_wan_ip"] == "198.51.100.10"
    assert parameters["paloalto_wan_ip"] == "203.0.113.20"
    assert parameters["tunnel_network"] == "169.255.1.0/30"
    assert parameters["fortigate_tunnel_ip"] == "169.255.1.1/30"
    assert parameters["paloalto_tunnel_ip"] == "169.255.1.2/30"
    assert parameters["fortigate_selector"] == {
        "local": "10.10.10.0/24",
        "remote": "10.20.20.0/24",
    }
    assert parameters["paloalto_proxy_id"] == {
        "local": "10.20.20.0/24",
        "remote": "10.10.10.0/24",
    }


def test_build_vpn_plan_includes_vendor_tools_steps_validation_and_alerts():
    plan = build_vpn_plan()

    assert "FortiOS REST API" in " ".join(plan["tools_and_apis"]["fortigate"])
    assert "PAN-OS REST API" in " ".join(plan["tools_and_apis"]["paloalto"])
    assert any(step["step"] == "create_phase1_interface" for step in plan["fortigate_steps"])
    assert any(step["step"] == "create_ipsec_tunnel_and_proxy_id" for step in plan["paloalto_steps"])
    assert any(check["check"] == "IKE SA established" for check in plan["validation_checks"])
    assert "VPN_DOWN" in plan["alert_conditions"]
    assert "PROXY_ID_MISMATCH" in plan["alert_conditions"]


def test_validate_vpn_parameters_rejects_bad_tunnel_network():
    params = VpnParameters(tunnel_network="169.255.1.0/29")

    errors = validate_vpn_parameters(params)

    assert "Tunnel network must be a /30 network" in errors


def test_build_vpn_plan_rejects_overlapping_lans():
    params = VpnParameters(
        fortigate_lan="10.10.10.0/24",
        paloalto_lan="10.10.10.128/25",
    )

    with pytest.raises(ValueError, match="must not overlap"):
        build_vpn_plan(params)
