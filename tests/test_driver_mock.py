from pathlib import Path

from driver import DEFAULT_VLANS, MockSwitchDriver


def test_mock_driver_applies_hostname_and_vlans():
    driver = MockSwitchDriver("192.0.2.10", "admin", "admin")
    driver.connect()
    driver.push_hostname("AUTOMATED_SWITCH")
    driver.push_vlan_config(DEFAULT_VLANS)

    assert driver.show_hostname() == "hostname AUTOMATED_SWITCH"
    vlan_output = driver.show_vlan_brief()
    assert "10   VLAN_DATA" in vlan_output
    assert "20   VLAN_VOICE" in vlan_output
    assert "50   VLAN_SECURITY" in vlan_output


def test_mock_driver_writes_backup(tmp_path):
    driver = MockSwitchDriver("192.0.2.10", "admin", "admin")
    driver.connect()
    driver.push_hostname("AUTOMATED_SWITCH")
    driver.push_vlan_config(DEFAULT_VLANS)

    backup_path = driver.backup_config("AUTOMATED_SWITCH", backup_dir=str(tmp_path))

    assert isinstance(backup_path, Path)
    assert backup_path.exists()
    assert backup_path.name.startswith("AUTOMATED_SWITCH_")
    assert backup_path.suffix == ".cfg"
    assert "hostname AUTOMATED_SWITCH" in backup_path.read_text(encoding="utf-8")
