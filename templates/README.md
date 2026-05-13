# Templates

This folder contains the Flask HTML template for the Part 1 Cisco switch automation frontend.

## `index.html`

`index.html` is the browser UI rendered by `main.py` at:

```text
http://127.0.0.1:5000
```

It provides the form used to run Cisco switch automation.

The page lets the user choose:

- `Mock Cisco IOS Driver`
- `Netmiko Cisco IOS SSH`

The page lets the user enter:

- device IP
- username
- password
- hostname
- VLAN 10, VLAN 20, and VLAN 50 IDs and names
- optional additional VLAN ID and name

When the user clicks **Run Automation**, the form is submitted to the Flask `POST /` route in `main.py`.

The page displays:

- connection and configuration command output
- backup file link
- compliance status
- validation checks
- alert messages when validation fails

In short:

```text
templates/index.html = the web UI for Part 1 Cisco switch automation
```
