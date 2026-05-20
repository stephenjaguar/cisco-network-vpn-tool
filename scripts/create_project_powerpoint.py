"""Create a formal PowerPoint deck for the Part 1 and Part 2 review."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile


EMU = 914400
SLIDE_W = 12192000
SLIDE_H = 6858000

NAVY = "17365D"
BLUE = "2F5597"
LIGHT_BLUE = "D9EAF7"
GREEN = "548235"
LIGHT_GREEN = "E2F0D9"
ORANGE = "C55A11"
LIGHT_ORANGE = "FCE4D6"
YELLOW = "FFF2CC"
GRAY = "5C6678"
LIGHT_GRAY = "F4F6F8"
TEXT = "172033"
WHITE = "FFFFFF"


@dataclass(frozen=True)
class DiagramBox:
    text: str
    x: float
    y: float
    w: float
    h: float
    fill: str
    line: str = BLUE


@dataclass(frozen=True)
class DiagramLine:
    x1: float
    y1: float
    x2: float
    y2: float
    color: str = GRAY


@dataclass(frozen=True)
class SlideSpec:
    layout: str
    title: str
    subtitle: str = ""
    bullets: tuple[str, ...] = ()
    left_title: str = ""
    left_bullets: tuple[str, ...] = ()
    right_title: str = ""
    right_bullets: tuple[str, ...] = ()
    boxes: tuple[DiagramBox, ...] = ()
    lines: tuple[DiagramLine, ...] = ()
    takeaway: str = ""


def inch(value: float) -> int:
    return int(value * EMU)


def main() -> int:
    output = Path("demoresult/part1_part2_project_overview.pptx")
    output.parent.mkdir(parents=True, exist_ok=True)
    build_pptx(output, slides())
    print(output)
    return 0


def slides() -> list[SlideSpec]:
    return [
        SlideSpec(
            "cover",
            "Cisco IOS Automation and IPSec VPN Planning",
            "Part 1: Flask + GNS3 switch automation\nPart 2: FortiGate-to-Palo Alto IPSec VPN automation plan",
            bullets=(
                "Repository: /Users/thunder/Documents/Meli",
                "Evidence: README, setup guide, test plan, VPN plan, screenshots, CLI examples",
                "Current verification: 26 automated tests passing",
            ),
        ),
        SlideSpec(
            "agenda",
            "Review Agenda",
            bullets=(
                "Project objective and repository structure",
                "Part 1 architecture, topology, workflow, validation, and tests",
                "Part 2 VPN topology, parameters, APIs, automation flow, and alerts",
                "Evidence and final review summary",
            ),
        ),
        SlideSpec(
            "section",
            "Part 1",
            "Cisco IOS switch automation with Flask, GNS3, Netmiko, backup, and compliance validation",
        ),
        SlideSpec(
            "two_col",
            "Part 1 Architecture",
            left_title="Runtime Components",
            left_bullets=(
                "main.py handles Flask routes, form parsing, and workflow orchestration.",
                "templates/index.html provides the browser UI.",
                "driver.py exposes MockSwitchDriver and NetmikoSwitchDriver.",
            ),
            right_title="Control Outputs",
            right_bullets=(
                "validator.py compares observed switch output with intended state.",
                "backups/ stores timestamped running-config files.",
                "demoresult/ stores Part 1 screenshot evidence.",
            ),
            takeaway="The UI, device driver, validation, and backup responsibilities are separated cleanly.",
        ),
        SlideSpec(
            "diagram",
            "Part 1 GNS3 Topology",
            boxes=(
                DiagramBox("Mac\nFlask App\nhttp://127.0.0.1:5000", 0.7, 2.1, 2.4, 1.2, LIGHT_BLUE, BLUE),
                DiagramBox("GNS3\nCloud / NAT\nManagement Path", 4.55, 2.1, 2.4, 1.2, LIGHT_GRAY, GRAY),
                DiagramBox("IOSvL2 Switch\nSVI 192.168.31.50/24\nGW 192.168.31.1\nSSH TCP/22", 8.25, 1.75, 3.0, 1.9, LIGHT_GREEN, GREEN),
            ),
            lines=(
                DiagramLine(3.1, 2.7, 4.55, 2.7),
                DiagramLine(6.95, 2.7, 8.25, 2.7),
            ),
            takeaway="Netmiko mode depends on IP reachability and SSH availability before automation starts.",
        ),
        SlideSpec(
            "process",
            "Part 1 Automation Flow",
            boxes=(
                DiagramBox("1\nSubmit Flask form", 0.55, 2.1, 1.75, 1.2, LIGHT_BLUE),
                DiagramBox("2\nCreate driver", 2.55, 2.1, 1.75, 1.2, LIGHT_BLUE),
                DiagramBox("3\nPush hostname + VLANs", 4.55, 2.1, 2.0, 1.2, LIGHT_BLUE),
                DiagramBox("4\nwrite memory", 6.85, 2.1, 1.75, 1.2, LIGHT_BLUE),
                DiagramBox("5\nBackup + validate", 8.85, 2.1, 2.0, 1.2, LIGHT_BLUE),
            ),
            lines=(
                DiagramLine(2.3, 2.7, 2.55, 2.7, BLUE),
                DiagramLine(4.3, 2.7, 4.55, 2.7, BLUE),
                DiagramLine(6.55, 2.7, 6.85, 2.7, BLUE),
                DiagramLine(8.6, 2.7, 8.85, 2.7, BLUE),
            ),
            takeaway="The same workflow runs against the mock driver or a real GNS3 IOSvL2 SSH target.",
        ),
        SlideSpec(
            "two_col",
            "Part 1 Configuration and Compliance",
            left_title="Configuration Inputs",
            left_bullets=(
                "Hostname defaults to AUTOMATED_SWITCH and can be submitted from the frontend.",
                "Required VLANs: 10 VLAN_DATA, 20 VLAN_VOICE, 50 VLAN_SECURITY.",
                "One optional additional VLAN can be pushed if it does not duplicate another VLAN ID.",
            ),
            right_title="Compliance Checks",
            right_bullets=(
                "Hostname is compared against the submitted frontend hostname.",
                "VLAN 10/20/50 names are validated from show vlan brief output.",
                "Optional additional VLAN is configured but not included in compliance scoring.",
            ),
            takeaway="Compliance is based on observed switch output, not only successful command submission.",
        ),
        SlideSpec(
            "two_col",
            "Part 1 Netmiko and Reliability Controls",
            left_title="Connection Behavior",
            left_bullets=(
                "Device type is cisco_ios.",
                "conn_timeout, auth_timeout, and banner_timeout are 15 seconds.",
                "read_timeout is 60 seconds for config and show commands.",
            ),
            right_title="Prompt Handling",
            right_bullets=(
                "Generic IOS prompt pattern [>#] avoids hostname-specific prompt failures.",
                "Hostname changes disable command verification.",
                "Base prompt is refreshed after hostname changes.",
            ),
            takeaway="These controls address common IOSvL2 SSH delays and prompt changes in GNS3.",
        ),
        SlideSpec(
            "two_col",
            "Part 1 Testing and Evidence",
            left_title="Automated Testing",
            left_bullets=(
                "pytest -q currently returns 26 passed.",
                "Tests cover Flask UI flow, mock driver, validator behavior, Netmiko timeouts, and prompt handling.",
                "Reachability helper tests verify ping and TCP checks.",
            ),
            right_title="Demo Evidence",
            right_bullets=(
                "demoresult/part1screenshot.md indexes screenshots.",
                "Screenshots cover frontend, switch CLI, validation alerts, compliance, and backup evidence.",
                "PART1_FLASK_GNS3_SETUP.md documents the GNS3 setup path.",
            ),
        ),
        SlideSpec(
            "section",
            "Part 2",
            "FortiGate-to-Palo Alto IPSec VPN automation planning with parameters, APIs, validation, and alerts",
        ),
        SlideSpec(
            "diagram",
            "Part 2 VPN Topology",
            boxes=(
                DiagramBox("FortiGate\nFGT-BRANCH\nWAN 198.51.100.10\nLAN 10.10.10.0/24", 0.65, 1.85, 3.0, 1.65, LIGHT_ORANGE, ORANGE),
                DiagramBox("IPSec Tunnel\n169.255.1.0/30\nFGT 169.255.1.1\nPA 169.255.1.2", 4.45, 1.95, 3.0, 1.45, YELLOW, "BF9000"),
                DiagramBox("Palo Alto\nPA-DC\nWAN 203.0.113.20\nLAN 10.20.20.0/24", 8.25, 1.85, 3.0, 1.65, LIGHT_BLUE, BLUE),
            ),
            lines=(
                DiagramLine(3.65, 2.65, 4.45, 2.65, GRAY),
                DiagramLine(7.45, 2.65, 8.25, 2.65, GRAY),
            ),
            takeaway="The tunnel uses mirrored selectors: FortiGate local 10.10.10.0/24 to Palo Alto local 10.20.20.0/24.",
        ),
        SlideSpec(
            "two_col",
            "Part 2 Required Parameters",
            left_title="Network Parameters",
            left_bullets=(
                "FortiGate WAN IP: 198.51.100.10.",
                "Palo Alto WAN IP: 203.0.113.20.",
                "FortiGate protected subnet: 10.10.10.0/24.",
                "Palo Alto protected subnet: 10.20.20.0/24.",
            ),
            right_title="Tunnel and Crypto",
            right_bullets=(
                "Tunnel network: 169.255.1.0/30.",
                "FortiGate tunnel IP: 169.255.1.1/30.",
                "Palo Alto tunnel IP: 169.255.1.2/30.",
                "IKEv2, AES-256, SHA-256, DH/PFS Group 14.",
            ),
        ),
        SlideSpec(
            "two_col",
            "Part 2 Tools and API Strategy",
            left_title="FortiGate",
            left_bullets=(
                "FortiOS REST CMDB endpoints for VPN Phase 1 and Phase 2.",
                "REST endpoints for interfaces, address objects, policies, and routes.",
                "Monitor API or SSH commands for tunnel state and route checks.",
                "API token docs: docs.fortinet.com/.../administration-guide/940602/using-apis",
                "REST API admin docs: docs.fortinet.com/.../administration-guide/399023/rest-api-administrator",
            ),
            right_title="Palo Alto",
            right_bullets=(
                "PAN-OS REST API for objects, tunnel interfaces, gateways, tunnels, routes, and policy.",
                "XML API or Panorama for operational commands and commit workflows.",
                "SSH remains a fallback for show/test commands.",
                "REST API key docs: docs.paloaltonetworks.com/.../get-started-with-the-pan-os-rest-api",
                "XML API key docs: docs.paloaltonetworks.com/.../get-your-api-key",
            ),
        ),
        SlideSpec(
            "process",
            "Part 2 Automation Flow",
            boxes=(
                DiagramBox("1\nValidate inputs", 0.45, 2.0, 1.65, 1.15, YELLOW),
                DiagramBox("2\nCreate objects", 2.25, 2.0, 1.65, 1.15, YELLOW),
                DiagramBox("3\nBuild tunnels", 4.05, 2.0, 1.65, 1.15, YELLOW),
                DiagramBox("4\nRoutes + policy", 5.85, 2.0, 1.65, 1.15, YELLOW),
                DiagramBox("5\nCommit/apply", 7.65, 2.0, 1.65, 1.15, YELLOW),
                DiagramBox("6\nValidate + alert", 9.45, 2.0, 1.9, 1.15, YELLOW),
            ),
            lines=(
                DiagramLine(2.1, 2.58, 2.25, 2.58, ORANGE),
                DiagramLine(3.9, 2.58, 4.05, 2.58, ORANGE),
                DiagramLine(5.7, 2.58, 5.85, 2.58, ORANGE),
                DiagramLine(7.5, 2.58, 7.65, 2.58, ORANGE),
                DiagramLine(9.3, 2.58, 9.45, 2.58, ORANGE),
            ),
            takeaway="The plan is repeatable: validate, configure both vendors, commit/apply, then verify operational state.",
        ),
        SlideSpec(
            "two_col",
            "Part 2 Multi-Vendor Considerations",
            left_title="Common Failure Points",
            left_bullets=(
                "Proxy-ID and traffic selector mismatch.",
                "Phase 1 / Phase 2 proposal mismatch.",
                "PFS or lifetime mismatch.",
                "Missing static routes or asymmetric routing.",
            ),
            right_title="Operational Considerations",
            right_bullets=(
                "PAN-OS candidate configuration must be committed.",
                "FortiGate and Palo Alto use different zone and policy models.",
                "NAT-T and logging behavior should be aligned with the design.",
                "Pre-shared keys must come from a secret manager.",
            ),
        ),
        SlideSpec(
            "two_col",
            "Part 2 Validation and Alerts",
            left_title="Validation Methods",
            left_bullets=(
                "FortiGate: get vpn ipsec tunnel summary.",
                "FortiGate: diagnose vpn tunnel list and route lookup.",
                "Palo Alto: show vpn ike-sa and show vpn ipsec-sa.",
                "End-to-end ICMP or application traffic test.",
            ),
            right_title="Alert Conditions",
            right_bullets=(
                "VPN_DOWN.",
                "PROXY_ID_MISMATCH.",
                "PROPOSAL_MISMATCH.",
                "ROUTE_MISSING.",
                "POLICY_MISSING or COMMIT_PENDING.",
            ),
        ),
        SlideSpec(
            "two_col",
            "Part 2 Repository Artifacts",
            left_title="Planning Artifacts",
            left_bullets=(
                "VPN_PLAN.md provides the written automation plan.",
                "PART2_VPN_DELIVERABLES.md maps requirements to artifacts.",
                "vpn_planner.py builds structured plan data.",
            ),
            right_title="Execution Examples",
            right_bullets=(
                "scripts/generate_vpn_plan.py prints the plan as JSON.",
                "vpncliexamples/ stores FortiGate and Palo Alto conceptual CLI examples.",
                "scripts/vpn_connectivity_check.py provides optional ICMP validation.",
            ),
        ),
        SlideSpec(
            "summary",
            "Final Review Summary",
            bullets=(
                "Part 1 demonstrates working Cisco switch automation with Flask, GNS3 readiness, backup, and compliance validation.",
                "Part 2 provides a complete FortiGate-to-Palo Alto IPSec VPN automation plan with structured code and example artifacts.",
                "The repository includes setup documentation, test plan, requirement mapping, screenshot evidence, and CLI examples.",
            ),
        ),
    ]


def build_pptx(output: Path, specs: list[SlideSpec]) -> None:
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types_xml(len(specs)))
        archive.writestr("_rels/.rels", root_rels_xml())
        archive.writestr("docProps/core.xml", core_xml())
        archive.writestr("docProps/app.xml", app_xml(len(specs)))
        archive.writestr("ppt/presentation.xml", presentation_xml(len(specs)))
        archive.writestr("ppt/_rels/presentation.xml.rels", presentation_rels_xml(len(specs)))
        archive.writestr("ppt/slideMasters/slideMaster1.xml", slide_master_xml())
        archive.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", slide_master_rels_xml())
        archive.writestr("ppt/slideLayouts/slideLayout1.xml", slide_layout_xml())
        archive.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", slide_layout_rels_xml())
        archive.writestr("ppt/theme/theme1.xml", theme_xml())
        for index, spec in enumerate(specs, start=1):
            archive.writestr(f"ppt/slides/slide{index}.xml", slide_xml(spec, index, len(specs)))
            archive.writestr(f"ppt/slides/_rels/slide{index}.xml.rels", slide_rels_xml())


def slide_xml(spec: SlideSpec, index: int, total: int) -> str:
    shapes: list[str] = [background()]
    if spec.layout == "cover":
        shapes.extend(cover_shapes(spec))
    elif spec.layout == "section":
        shapes.extend(section_shapes(spec, index, total))
    else:
        shapes.append(header(spec.title, index, total))
        if spec.layout == "agenda":
            shapes.append(numbered_list(spec.bullets, 1.0, 1.55, 10.3, 3.8))
        elif spec.layout == "two_col":
            shapes.extend(two_column_shapes(spec))
        elif spec.layout in {"diagram", "process"}:
            shapes.extend(diagram_shapes(spec))
        elif spec.layout == "summary":
            shapes.append(bullet_panel(spec.bullets, 1.05, 1.65, 10.25, 3.8, LIGHT_BLUE))
        if spec.takeaway:
            shapes.append(takeaway_box(spec.takeaway))

    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
      {''.join(shapes)}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>"""


def cover_shapes(spec: SlideSpec) -> list[str]:
    return [
        rect(0, 0, 13.333, 7.5, NAVY, NAVY),
        text(spec.title, 0.85, 1.05, 11.4, 1.0, 34, WHITE, bold=True),
        text(spec.subtitle, 0.9, 2.05, 10.7, 0.8, 18, "D7DEEA"),
        bullet_panel(spec.bullets, 0.9, 3.25, 7.6, 1.75, "24496F", text_color=WHITE),
        text("Project Review Deck", 0.9, 6.55, 4.8, 0.35, 12, "D7DEEA"),
    ]


def section_shapes(spec: SlideSpec, index: int, total: int) -> list[str]:
    return [
        rect(0, 0, 13.333, 7.5, NAVY, NAVY),
        text(spec.title, 0.9, 2.15, 10.8, 0.9, 44, WHITE, bold=True),
        text(spec.subtitle, 0.95, 3.1, 10.6, 0.8, 20, "D7DEEA"),
        text(f"{index}/{total}", 11.65, 6.75, 0.8, 0.3, 11, "D7DEEA"),
    ]


def header(title: str, index: int, total: int) -> str:
    return (
        rect(0, 0, 13.333, 0.72, NAVY, NAVY)
        + text(title, 0.55, 0.17, 10.8, 0.38, 18, WHITE, bold=True)
        + text(f"{index}/{total}", 11.85, 0.2, 0.85, 0.3, 10, "D7DEEA")
    )


def two_column_shapes(spec: SlideSpec) -> list[str]:
    return [
        panel(spec.left_title, spec.left_bullets, 0.75, 1.35, 5.55, 4.45, LIGHT_GRAY),
        panel(spec.right_title, spec.right_bullets, 6.65, 1.35, 5.55, 4.45, LIGHT_GRAY),
        takeaway_box(spec.takeaway) if spec.takeaway else "",
    ]


def diagram_shapes(spec: SlideSpec) -> list[str]:
    shapes = []
    for line in spec.lines:
        shapes.append(connector(line))
    for box in spec.boxes:
        shapes.append(diagram_box(box))
    return shapes


def panel(title: str, bullets: tuple[str, ...], x: float, y: float, w: float, h: float, fill: str) -> str:
    return (
        rect(x, y, w, h, fill, "D8E1ED")
        + rect(x, y, w, 0.55, NAVY, NAVY)
        + text(title, x + 0.25, y + 0.15, w - 0.5, 0.25, 13, WHITE, bold=True)
        + bullet_panel(bullets, x + 0.25, y + 0.8, w - 0.5, h - 1.0, fill, no_border=True)
    )


def takeaway_box(value: str) -> str:
    return rect(0.75, 6.05, 11.8, 0.62, "EEF3F8", "D8E1ED") + text(
        "Takeaway: " + value, 1.0, 6.21, 11.25, 0.25, 12, TEXT, bold=True
    )


def diagram_box(box: DiagramBox) -> str:
    body = []
    for idx, line in enumerate(box.text.split("\n")):
        body.append(paragraph(line, 15 if idx else 16, bold=idx == 0, align="ctr"))
    return shape("rect", box.x, box.y, box.w, box.h, "".join(body), box.fill, box.line)


def bullet_panel(
    bullets: tuple[str, ...],
    x: float,
    y: float,
    w: float,
    h: float,
    fill: str,
    text_color: str = TEXT,
    no_border: bool = False,
) -> str:
    body = "".join(bullet_paragraph(item, text_color) for item in bullets)
    return shape("rect", x, y, w, h, body, fill, fill if no_border else "D8E1ED")


def numbered_list(items: tuple[str, ...], x: float, y: float, w: float, h: float) -> str:
    body = "".join(paragraph(f"{idx}. {item}", 20, color=TEXT) for idx, item in enumerate(items, start=1))
    return shape("rect", x, y, w, h, body, WHITE, WHITE)


def background() -> str:
    return rect(0, 0, 13.333, 7.5, WHITE, WHITE)


def rect(x: float, y: float, w: float, h: float, fill: str, line: str) -> str:
    return shape("rect", x, y, w, h, "", fill, line)


def text(value: str, x: float, y: float, w: float, h: float, size: int, color: str, bold: bool = False) -> str:
    body = "".join(paragraph(line, size, color=color, bold=bold) for line in value.split("\n"))
    return shape("rect", x, y, w, h, body, None, None)


def bullet_paragraph(value: str, color: str) -> str:
    return f"""<a:p><a:pPr marL="285750" indent="-171450"><a:buChar char="•"/></a:pPr><a:r><a:rPr lang="en-US" sz="1650"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:rPr><a:t>{escape(value)}</a:t></a:r></a:p>"""


def paragraph(value: str, size: int, color: str = TEXT, bold: bool = False, align: str = "l") -> str:
    bold_attr = ' b="1"' if bold else ""
    return f"""<a:p><a:pPr algn="{align}"/><a:r><a:rPr lang="en-US" sz="{size * 100}"{bold_attr}><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:rPr><a:t>{escape(value)}</a:t></a:r></a:p>"""


def shape(kind: str, x: float, y: float, w: float, h: float, body: str, fill: str | None, line: str | None) -> str:
    fill_xml = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else "<a:noFill/>"
    line_xml = f'<a:ln w="9525"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln>' if line else "<a:ln><a:noFill/></a:ln>"
    return f"""<p:sp>
  <p:nvSpPr><p:cNvPr id="{shape_id(x, y, w, h)}" name="shape"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{inch(x)}" y="{inch(y)}"/><a:ext cx="{inch(w)}" cy="{inch(h)}"/></a:xfrm><a:prstGeom prst="{kind}"><a:avLst/></a:prstGeom>{fill_xml}{line_xml}</p:spPr>
  <p:txBody><a:bodyPr wrap="square" anchor="mid" lIns="91440" tIns="45720" rIns="91440" bIns="45720"/><a:lstStyle/>{body or '<a:p/>'}</p:txBody>
</p:sp>"""


def connector(line: DiagramLine) -> str:
    x = min(line.x1, line.x2)
    y = min(line.y1, line.y2)
    w = abs(line.x2 - line.x1) or 0.01
    h = abs(line.y2 - line.y1) or 0.01
    return f"""<p:cxnSp>
  <p:nvCxnSpPr><p:cNvPr id="{shape_id(line.x1, line.y1, line.x2, line.y2)}" name="connector"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr>
  <p:spPr><a:xfrm><a:off x="{inch(x)}" y="{inch(y)}"/><a:ext cx="{inch(w)}" cy="{inch(h)}"/></a:xfrm><a:prstGeom prst="straightConnector1"><a:avLst/></a:prstGeom><a:ln w="19050"><a:solidFill><a:srgbClr val="{line.color}"/></a:solidFill></a:ln></p:spPr>
</p:cxnSp>"""


def shape_id(*values: float) -> int:
    return 100 + abs(hash(tuple(round(v, 3) for v in values))) % 900000


def content_types_xml(count: int) -> str:
    slides_xml = "\n".join(
        f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, count + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  {slides_xml}
</Types>"""


def root_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""


def presentation_xml(count: int) -> str:
    slide_ids = "".join(f'<p:sldId id="{255 + i}" r:id="rId{i}"/>' for i in range(1, count + 1))
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId{count + 1}"/></p:sldMasterIdLst>
  <p:sldIdLst>{slide_ids}</p:sldIdLst>
  <p:sldSz cx="{inch(13.333)}" cy="{inch(7.5)}" type="wide"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>"""


def presentation_rels_xml(count: int) -> str:
    rels = [
        f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, count + 1)
    ]
    rels.append(
        f'<Relationship Id="rId{count + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{''.join(rels)}</Relationships>"""


def slide_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>"""


def slide_master_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
</p:sldMaster>"""


def slide_master_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>"""


def slide_layout_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1">
  <p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>"""


def slide_layout_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>"""


def theme_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Formal">
  <a:themeElements>
    <a:clrScheme name="Formal"><a:dk1><a:srgbClr val="000000"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="17365D"/></a:dk2><a:lt2><a:srgbClr val="F4F6F8"/></a:lt2><a:accent1><a:srgbClr val="2F5597"/></a:accent1><a:accent2><a:srgbClr val="C55A11"/></a:accent2><a:accent3><a:srgbClr val="548235"/></a:accent3><a:accent4><a:srgbClr val="8064A2"/></a:accent4><a:accent5><a:srgbClr val="4BACC6"/></a:accent5><a:accent6><a:srgbClr val="F79646"/></a:accent6><a:hlink><a:srgbClr val="0000FF"/></a:hlink><a:folHlink><a:srgbClr val="800080"/></a:folHlink></a:clrScheme>
    <a:fontScheme name="Formal"><a:majorFont><a:latin typeface="Aptos Display"/></a:majorFont><a:minorFont><a:latin typeface="Aptos"/></a:minorFont></a:fontScheme>
    <a:fmtScheme name="Formal"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="6350"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme>
  </a:themeElements>
</a:theme>"""


def core_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <dc:title>Cisco IOS Automation and VPN Planning</dc:title>
  <dc:creator>Codex</dc:creator>
</cp:coreProperties>"""


def app_xml(count: int) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">
  <Application>Codex</Application>
  <PresentationFormat>On-screen Show (16:9)</PresentationFormat>
  <Slides>{count}</Slides>
</Properties>"""


if __name__ == "__main__":
    raise SystemExit(main())
