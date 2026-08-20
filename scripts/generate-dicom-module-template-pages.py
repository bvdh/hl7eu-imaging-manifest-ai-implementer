#!/usr/bin/env python3
"""
Generate per-module and per-template mapping pages from the step11 results.

For each DICOM module (step11-dicom-module-fhir-obligations.csv) and each DICOM
template TID (step11-dicom-template-fhir-obligations.csv), write one markdown
include page to imaging-manifest-fork/input/pagecontent/ with:
  - a short description
  - a link to the DICOM source definition and to IHE-MADO
  - an attribute/node table including Consumer + Producer obligations
"""

import csv
import re
from collections import OrderedDict
from pathlib import Path

MODULE_CSV = Path("ai-result/step11-dicom-module-fhir-obligations.csv")
TEMPLATE_CSV = Path("ai-result/step11-dicom-template-fhir-obligations.csv")
OUT = Path("imaging-manifest-fork/input/pagecontent")
PS3 = "https://dicom.nema.org/medical/dicom/current/output/chtml/part03/"

# The DICOM chtml output chunks modules at a coarser level than their
# sub-subsection number, so f"sect_{ref}.html" 404s for most modules. Map each
# module's DICOM Reference to its verified chtml page + table anchor.
MODULE_DICOM_URL = {
    "C.7.1.1": PS3 + "sect_C.7.html#table_C.7-1",
    "C.7.2.1": PS3 + "sect_C.7.2.html#table_C.7-3",
    "C.7.5.1": PS3 + "sect_C.7.5.html#table_C.7-8",
    "C.12.1": PS3 + "sect_C.12.html#table_C.12-1",
    "C.17.6.1": PS3 + "sect_C.17.6.html#table_C.17.6-1",
    "C.17.6.2": PS3 + "sect_C.17.6.2.html#table_C.17.6-2",
}
MADO = "https://www.ihe.net/uploadedFiles/Documents/Radiology/IHE_RAD_Suppl_MADO.pdf"

# Manual intro additions to preserve across regeneration. The generated intro
# sentence is a fixed template; any extra sentence authored by hand is appended
# here, keyed by module name (MODULE_INTRO_EXTRA) or template ID
# (TEMPLATE_INTRO_EXTRA), so re-running this generator does not overwrite it.
MODULE_INTRO_EXTRA = {}
TEMPLATE_INTRO_EXTRA = {
    "2010": "This is used in the SR Document Module.",
}


# CodeSystem page that defines the obligation codes used in the Consumer/Producer
# columns. Each code cell links to its concept anchor on this page.
OBLIGATION_CS = "http://hl7.org/fhir/extensions/5.3.0/CodeSystem-obligation.html"


def esc(t):
    return ("" if t is None else t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def oblig_anchor(code):
    # FHIR CodeSystem page anchors keep alphanumerics/-/_/. and encode any other
    # character as ".<decimal-codepoint>" (e.g. ":" -> ".58").
    return "".join(ch if (ch.isalnum() or ch in "-_.") else f".{ord(ch)}" for ch in code)


def oblig_link(code):
    code = (code or "").strip()
    if not code:
        return ""
    return f'<a href="{OBLIGATION_CS}#obligation-{oblig_anchor(code)}" target="_blank">{esc(code)}</a>'


def th(cols):
    return "      <tr>" + "".join(f'<th style="text-align:center">{c}</th>' for c in cols) + "</tr>"


def colgroup(widths):
    return "    <colgroup>" + "".join(f'<col style="width:{w}">' for w in widths) + "</colgroup>"


def td(cells, left=(), raw=()):
    out = []
    for i, c in enumerate(cells):
        style = "" if i in left else ' style="text-align:center"'
        content = c if i in raw else esc(c)
        out.append(f"<td{style}>{content}</td>")
    return "  <tr>" + "".join(out) + "</tr>"


def write_modules():
    groups = OrderedDict()
    for r in csv.DictReader(MODULE_CSV.open(encoding="utf-8")):
        groups.setdefault(r["Module"], []).append(r)
    cols = ["Attribute Name", "Tag", "DICOM Type", "IHE Usage", "Consumer Obligation", "Producer Obligation"]
    widths = ["26%", "9%", "8%", "9%", "24%", "24%"]
    for module, rows in groups.items():
        ref = rows[0]["DICOM Reference"]
        dicom_url = MODULE_DICOM_URL.get(ref, f"{PS3}sect_{ref}.html") if ref else ""
        body = [f"#### {module} Module", ""]
        intro = f"DICOM {module} attributes (PS3.3 {ref}) with their IHE-MADO usage and EU-MADO Consumer/Producer obligations."
        extra = MODULE_INTRO_EXTRA.get(module)
        body.append(f"{intro} {extra}" if extra else intro)
        body.append("")
        body.append("<ul>")
        if dicom_url:
            body.append(f'  <li><strong>DICOM source:</strong> <a href="{dicom_url}" target="_blank">PS3.3 {ref}</a></li>')
        body.append(f'  <li><strong>IHE-MADO:</strong> <a href="{MADO}" target="_blank">IHE RAD MADO supplement</a></li>')
        body.append("</ul>")
        body.append("")
        body.append('<div class="table-wrap">')
        body.append(f'  <table summary="{module} Module">')
        body.append(f"    <caption>{module} Module</caption>")
        body.append(colgroup(widths))
        body.append("    <thead>")
        body.append(th(cols))
        body.append("    </thead>")
        body.append("    <tbody>")
        for r in rows:
            body.append(td([r["Attribute Name"], r["Tag"], r["DICOM Type"], r["MADO IHE Usage"], oblig_link(r["Consumer Obligation"]), oblig_link(r["Producer Obligation"])], left={0}, raw={4, 5}))
        body.append("    </tbody>")
        body.append("  </table>")
        body.append("</div>")
        body.append("")
        (OUT / f"dicom-module-{slug(module)}.md").write_text("\n".join(body), encoding="utf-8")
    return list(groups)


def write_templates():
    groups = OrderedDict()
    for r in csv.DictReader(TEMPLATE_CSV.open(encoding="utf-8")):
        groups.setdefault((r["Template ID"], r["DICOM TID Name"]), []).append(r)
    cols = ["Row No", "NL", "REL with Parent", "VT", "Concept Name", "VM", "Req Type (DICOM)", "Req Type (IHE)", "Consumer Obligation", "Producer Obligation"]
    widths = ["6%", "5%", "13%", "6%", "22%", "5%", "8%", "8%", "13.5%", "13.5%"]
    for (tid, name), rows in groups.items():
        d_url = rows[0]["DICOM Section URL"]
        m_url = rows[0]["MADO Page URL"]
        body = [f"#### TID {tid} {name}", ""]
        intro = f"DICOM SR template TID {tid} ({name}) nodes with DICOM/IHE requirement types and EU-MADO Consumer/Producer obligations."
        extra = TEMPLATE_INTRO_EXTRA.get(tid)
        body.append(f"{intro} {extra}" if extra else intro)
        body.append("")
        body.append("<ul>")
        if d_url:
            body.append(f'  <li><strong>DICOM source:</strong> <a href="{d_url}" target="_blank">PS3.16 TID {tid}</a></li>')
        body.append(f'  <li><strong>IHE-MADO:</strong> <a href="{m_url or MADO}" target="_blank">IHE RAD MADO supplement</a></li>')
        body.append("</ul>")
        body.append("")
        body.append('<div class="table-wrap">')
        body.append(f'  <table summary="TID {tid} {name}">')
        body.append(f"    <caption>TID {tid} {name}</caption>")
        body.append(colgroup(widths))
        body.append("    <thead>")
        body.append(th(cols))
        body.append("    </thead>")
        body.append("    <tbody>")
        for r in rows:
            body.append(td([r["Row No"], r["NL"], r["REL with Parent"], r["VT"], r["Concept Name"], r["VM"], r["Req Type (DICOM)"], r["Req Type (IHE)"], oblig_link(r["Consumer Obligation"]), oblig_link(r["Producer Obligation"])], left={4}, raw={8, 9}))
        body.append("    </tbody>")
        body.append("  </table>")
        body.append("</div>")
        body.append("")
        (OUT / f"dicom-template-{tid}.md").write_text("\n".join(body), encoding="utf-8")
    return list(groups)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    m = write_modules()
    t = write_templates()
    print(f"modules:   {len(m)} pages -> {[slug(x) for x in m]}")
    print(f"templates: {len(t)} pages -> {[tid for tid, _ in t]}")


if __name__ == "__main__":
    main()
