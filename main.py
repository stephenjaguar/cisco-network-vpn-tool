"""Flask frontend for Cisco switch automation."""

from __future__ import annotations

from pathlib import Path

from flask import Flask, abort, render_template, request, send_file, url_for
from werkzeug.utils import secure_filename

from driver import DEFAULT_HOSTNAME, DEFAULT_VLANS, create_driver
from validator import validate_switch_state


app = Flask(__name__)


@app.get("/")
def index():
    return render_template(
        "index.html",
        vlan_rows=_default_vlan_rows(),
        extra_vlan=_empty_extra_vlan(),
        default_hostname=DEFAULT_HOSTNAME,
        result=None,
    )


@app.post("/")
def automate_switch():
    device_ip = request.form.get("device_ip", "").strip()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    hostname = request.form.get("hostname", DEFAULT_HOSTNAME).strip()
    driver_mode = request.form.get("driver_mode", "mock")

    if not hostname:
        hostname = DEFAULT_HOSTNAME

    result = {
        "commands": [],
        "backup_path": None,
        "report": None,
        "error": None,
        "driver_mode": driver_mode,
    }

    try:
        vlans = parse_vlan_form(request.form)
        driver = create_driver(driver_mode, device_ip, username, password)
        result["commands"].append(driver.connect())
        result["commands"].append(driver.push_hostname(hostname))
        result["commands"].append(driver.push_vlan_config(vlans))
        result["commands"].append(driver.save_config())
        backup_path = driver.backup_config(hostname)
        result["backup_path"] = str(backup_path)
        result["backup_url"] = url_for("download_backup", filename=backup_path.name)

        report = validate_switch_state(
            show_vlan_output=driver.show_vlan_brief(),
            hostname_output=driver.show_hostname(),
            intended_hostname=hostname,
            intended_vlans=DEFAULT_VLANS,
        )
        result["report"] = report
    except Exception as exc:  # noqa: BLE001 - visible interview demo error reporting
        result["error"] = str(exc)

    return render_template(
        "index.html",
        vlan_rows=_submitted_vlan_rows(request.form),
        extra_vlan=_submitted_extra_vlan(request.form),
        default_hostname=hostname,
        result=result,
    )


@app.get("/backups/<path:filename>")
def download_backup(filename: str):
    safe_filename = secure_filename(filename)
    if safe_filename != filename or not safe_filename.endswith(".cfg"):
        abort(404)

    backup_path = Path.cwd() / "backups" / safe_filename
    if not backup_path.is_file():
        abort(404)

    return send_file(backup_path, mimetype="text/plain")


def parse_vlan_form(form) -> dict[int, str]:
    """Parse policy VLAN rows plus one optional additional VLAN row."""
    vlans: dict[int, str] = {}

    for index in range(1, 4):
        vlan_id_raw = form.get(f"vlan_id_{index}", "").strip()
        vlan_name = form.get(f"vlan_name_{index}", "").strip()

        if not vlan_id_raw:
            raise ValueError(f"VLAN row {index}: VLAN ID is required")
        if not vlan_id_raw.isdigit():
            raise ValueError(f"VLAN row {index}: VLAN ID must be numeric")

        vlan_id = int(vlan_id_raw)
        if vlan_id < 1 or vlan_id > 4094:
            raise ValueError(f"VLAN row {index}: VLAN ID must be between 1 and 4094")
        if not vlan_name:
            raise ValueError(f"VLAN row {index}: VLAN name is required")
        if vlan_id in vlans:
            raise ValueError(f"Duplicate VLAN ID submitted: {vlan_id}")

        vlans[vlan_id] = vlan_name

    extra_vlan_id_raw = form.get("extra_vlan_id", "").strip()
    extra_vlan_name = form.get("extra_vlan_name", "").strip()
    if extra_vlan_id_raw or extra_vlan_name:
        if not extra_vlan_id_raw:
            raise ValueError("Additional VLAN: VLAN ID is required when name is set")
        if not extra_vlan_id_raw.isdigit():
            raise ValueError("Additional VLAN: VLAN ID must be numeric")

        extra_vlan_id = int(extra_vlan_id_raw)
        if extra_vlan_id < 1 or extra_vlan_id > 4094:
            raise ValueError("Additional VLAN: VLAN ID must be between 1 and 4094")
        if not extra_vlan_name:
            raise ValueError("Additional VLAN: VLAN name is required when ID is set")
        if extra_vlan_id in vlans:
            raise ValueError(f"Duplicate VLAN ID submitted: {extra_vlan_id}")

        vlans[extra_vlan_id] = extra_vlan_name

    return vlans


def _default_vlan_rows() -> list[dict[str, str]]:
    return [
        {"id": str(vlan_id), "name": vlan_name}
        for vlan_id, vlan_name in DEFAULT_VLANS.items()
    ]


def _submitted_vlan_rows(form) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for index, (default_id, default_name) in enumerate(DEFAULT_VLANS.items(), start=1):
        vlan_id_raw = form.get(f"vlan_id_{index}", str(default_id)).strip()
        vlan_name = form.get(f"vlan_name_{index}", default_name).strip()
        rows.append(
            {"id": vlan_id_raw or str(default_id), "name": vlan_name or default_name}
        )
    return rows


def _empty_extra_vlan() -> dict[str, str]:
    return {"id": "", "name": ""}


def _submitted_extra_vlan(form) -> dict[str, str]:
    return {
        "id": form.get("extra_vlan_id", "").strip(),
        "name": form.get("extra_vlan_name", "").strip(),
    }


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
