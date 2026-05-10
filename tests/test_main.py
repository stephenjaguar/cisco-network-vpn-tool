from pathlib import Path

from main import app


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
            "hostname": "AUTOMATED_SWITCH",
        },
    )

    body = response.get_data(as_text=True)
    backups = list((tmp_path / "backups").glob("AUTOMATED_SWITCH_*.cfg"))

    assert response.status_code == 200
    assert "COMPLIANT" in body
    assert "Hostname set to AUTOMATED_SWITCH" in body
    assert "VLAN 10" in body
    assert "VLAN 20" in body
    assert "VLAN 50" in body
    assert len(backups) == 1
    assert "hostname AUTOMATED_SWITCH" in backups[0].read_text(encoding="utf-8")
