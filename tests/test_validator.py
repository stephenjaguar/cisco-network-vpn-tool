from validator import validate_switch_state


INTENDED_VLANS = {
    10: "VLAN_DATA",
    20: "VLAN_VOICE",
    50: "VLAN_SECURITY",
}


def test_validator_reports_compliant_state():
    vlan_output = """
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Gi0/1
10   VLAN_DATA                       active
20   VLAN_VOICE                         active
50   VLAN_SECURITY                   active
"""
    report = validate_switch_state(
        vlan_output, "hostname AUTOMATED_SWITCH", "AUTOMATED_SWITCH", INTENDED_VLANS
    )

    assert report["status"] == "COMPLIANT"
    assert report["alerts"] == []


def test_validator_detects_missing_vlan():
    vlan_output = """
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
10   VLAN_DATA                       active
20   VLAN_VOICE                         active
"""
    report = validate_switch_state(
        vlan_output, "hostname AUTOMATED_SWITCH", "AUTOMATED_SWITCH", INTENDED_VLANS
    )

    assert report["status"] == "NON_COMPLIANT"
    assert "VLAN 50 mismatch" in report["alerts"][0]


def test_validator_detects_wrong_vlan_name():
    vlan_output = """
10   VLAN_DATA                       active
20   WRONG_NAME                       active
50   VLAN_SECURITY                   active
"""
    report = validate_switch_state(
        vlan_output, "hostname AUTOMATED_SWITCH", "AUTOMATED_SWITCH", INTENDED_VLANS
    )

    assert report["status"] == "NON_COMPLIANT"
    assert any("VLAN 20 mismatch" in alert for alert in report["alerts"])


def test_validator_detects_hostname_mismatch():
    vlan_output = """
10   VLAN_DATA                       active
20   VLAN_VOICE                         active
50   VLAN_SECURITY                   active
"""
    report = validate_switch_state(
        vlan_output, "hostname OLD_SWITCH", "AUTOMATED_SWITCH", INTENDED_VLANS
    )

    assert report["status"] == "NON_COMPLIANT"
    assert any("Hostname mismatch" in alert for alert in report["alerts"])
