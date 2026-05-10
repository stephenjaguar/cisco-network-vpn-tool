"""Flask frontend for Cisco switch automation."""

from __future__ import annotations

from flask import Flask, render_template, request

from driver import DEFAULT_VLANS, create_driver
from validator import validate_switch_state


app = Flask(__name__)


@app.get("/")
def index():
    return render_template(
        "index.html",
        vlans=DEFAULT_VLANS,
        default_hostname="AUTOMATED_SWITCH",
        result=None,
    )


@app.post("/")
def automate_switch():
    device_ip = request.form.get("device_ip", "").strip()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    hostname = request.form.get("hostname", "AUTOMATED_SWITCH").strip()
    driver_mode = request.form.get("driver_mode", "mock")

    if not hostname:
        hostname = "AUTOMATED_SWITCH"

    result = {
        "commands": [],
        "backup_path": None,
        "report": None,
        "error": None,
        "driver_mode": driver_mode,
    }

    try:
        driver = create_driver(driver_mode, device_ip, username, password)
        result["commands"].append(driver.connect())
        result["commands"].append(driver.push_hostname(hostname))
        result["commands"].append(driver.push_vlan_config(DEFAULT_VLANS))
        result["commands"].append(driver.save_config())
        backup_path = driver.backup_config(hostname)
        result["backup_path"] = str(backup_path)

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
        vlans=DEFAULT_VLANS,
        default_hostname=hostname,
        result=result,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
