from pathlib import Path

from driver import DEFAULT_HOSTNAME
from main import app


def test_index_renders_translated_assignment_defaults():
    client = app.test_client()

    response = client.get("/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert DEFAULT_HOSTNAME in body
    assert "VLAN_DATA" in body
    assert "VLAN_VOICE" in body
    assert "VLAN_SECURITY" in body


def test_flask_mock_workflow_returns_compliant_report_and_backup(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    client = app.test_client()

    response = client.post(
        "/",
        data={
            "driver_mode": "mock",
            "device_ip": "192.0.2.10",
            "username": "admin",
            "password": "admin",
            "hostname": DEFAULT_HOSTNAME,
            "vlan_id_1": "100",
            "vlan_name_1": "USERS",
            "vlan_id_2": "200",
            "vlan_name_2": "VOICE",
            "vlan_id_3": "300",
            "vlan_name_3": "CAMERAS",
        },
    )

    body = response.get_data(as_text=True)
    backups = list((tmp_path / "backups").glob(f"{DEFAULT_HOSTNAME}_*.cfg"))

    assert response.status_code == 200
    assert "COMPLIANT" in body
    assert f"Hostname set to {DEFAULT_HOSTNAME}" in body
    assert "VLAN 100" in body
    assert "VLAN 200" in body
    assert "VLAN 300" in body
    assert len(backups) == 1
    backup_text = backups[0].read_text(encoding="utf-8")
    assert f"hostname {DEFAULT_HOSTNAME}" in backup_text
    assert "vlan 100" in backup_text


def test_flask_rejects_invalid_vlan_id():
    client = app.test_client()

    response = client.post(
        "/",
        data={
            "driver_mode": "mock",
            "device_ip": "192.0.2.10",
            "username": "admin",
            "password": "admin",
            "hostname": DEFAULT_HOSTNAME,
            "vlan_id_1": "abc",
            "vlan_name_1": "USERS",
            "vlan_id_2": "20",
            "vlan_name_2": "VOICE",
            "vlan_id_3": "50",
            "vlan_name_3": "SECURITY",
        },
    )

    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "VLAN row 1: VLAN ID must be numeric" in body


def test_flask_rejects_duplicate_vlan_id():
    client = app.test_client()

    response = client.post(
        "/",
        data={
            "driver_mode": "mock",
            "device_ip": "192.0.2.10",
            "username": "admin",
            "password": "admin",
            "hostname": DEFAULT_HOSTNAME,
            "vlan_id_1": "10",
            "vlan_name_1": "USERS",
            "vlan_id_2": "10",
            "vlan_name_2": "VOICE",
            "vlan_id_3": "50",
            "vlan_name_3": "SECURITY",
        },
    )

    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Duplicate VLAN ID submitted: 10" in body
    assert body.count('value="10"') == 2
