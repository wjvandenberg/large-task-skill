#!/usr/bin/env python3
"""check_pptx.py - a LIGHT check of a finished PowerPoint file, for what "it opens" misses.

Run it on the FINAL .pptx, whenever the final deliverable is a PowerPoint file. The plan's own
criteria check the CONTENT first; this checks four things only, and renders nothing.

    off the slide      a shape running past an edge of the slide
    template text      an EMPTY placeholder - anyone who opens the deck to edit it sees
                       "Click to add text" - or a layout prompt or Lorem ipsum left as text
    comments           comments left in the file
    hidden slides      a slide marked hidden, which a slideshow skips and a reader may not

What it cannot see it says so, as NOT CHECKED - a shape inside a group, a position taken
from the layout, a rotated shape, text inside a chart - never skipping silently.

    python check_pptx.py FILE.pptx [--allow comments]
    python check_pptx.py --selftest

EXIT: 0 PASS · 1 FAIL · 2 the file could not be read. NOT CHECKED alone keeps 0, and the
OVERALL line counts it.
"""
from __future__ import annotations

import io
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
R_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
PKG_REL = "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"
SHAPES = {P + "sp", P + "pic", P + "cxnSp", P + "graphicFrame", P + "grpSp"}
QUIET = {"dt", "ftr", "sldNum", "hdr"}          # placeholders that are empty by design
PROMPT = re.compile(r"click to (add|edit)|lorem ipsum", re.I)
TOLERANCE = 12700                               # one point, in EMU: rounding is not a defect
CM = 360000                                     # EMU per centimetre
PASS, FAIL, UNREADABLE = 0, 1, 2


def row(name, items, detail, allowed=False):
    """FAIL when anything was found - unless the plan declared it, which the line then says."""
    if items and allowed:
        return ("PASS", name, f"ALLOWED by --allow: {detail}", items)
    return ("FAIL" if items else "PASS", name, detail, items)


def report(rows, unseen, examined):
    """What was examined, a line per check, what was NOT CHECKED, and one verdict."""
    lines = [f"examined    {examined}"]
    for verdict, name, detail, items in rows:
        lines.append(f"{verdict:12}{name:18} {detail}")
        lines += [f"{'':14}{i}" for i in list(items)[:10]] if verdict == "FAIL" else []
    lines += [f"NOT CHECKED {u}" for u in unseen]
    failed = sum(r[0] == "FAIL" for r in rows)
    lines.append(f"OVERALL: {'FAIL' if failed else 'PASS'} - {failed} of {len(rows)} checks "
                 f"failed, {len(unseen)} NOT CHECKED")
    return (FAIL if failed else PASS), lines, {r[1]: r[0] for r in rows}


def text_of(el):
    return "".join(t.text or "" for t in el.iter(A + "t"))


def outside(shape, width, height):
    """The edges a shape runs past, or None when its position cannot be read here."""
    xfrm = shape.find(P + "xfrm") if shape.tag == P + "graphicFrame" else None
    for holder in (P + "spPr", P + "grpSpPr"):
        if xfrm is None and shape.find(holder) is not None:
            xfrm = shape.find(holder).find(A + "xfrm")
    if xfrm is None or xfrm.find(A + "off") is None or xfrm.find(A + "ext") is None:
        return None
    if xfrm.get("rot", "0") not in ("0", "10800000"):
        return "rotated"
    x, y = int(xfrm.find(A + "off").get("x")), int(xfrm.find(A + "off").get("y"))
    cx, cy = int(xfrm.find(A + "ext").get("cx")), int(xfrm.find(A + "ext").get("cy"))
    over = [("left", -x), ("top", -y), ("right", x + cx - width), ("bottom", y + cy - height)]
    return [f"{edge} edge by {amount / CM:.1f} cm" for edge, amount in over if amount > TOLERANCE]


def check(source, allow=()):
    """(exit code, report lines, {check: verdict}) for a path or a file-like object."""
    try:
        with zipfile.ZipFile(source) as z:
            names = z.namelist()
            if "ppt/presentation.xml" not in names:
                return UNREADABLE, ["UNREADABLE  no ppt/presentation.xml - not a PowerPoint "
                                    "file"], {}
            pres = ET.fromstring(z.read("ppt/presentation.xml"))
            rels = {r.get("Id"): r.get("Target") for r in
                    ET.fromstring(z.read("ppt/_rels/presentation.xml.rels")).iter(PKG_REL)}
            slides = [ET.fromstring(z.read("ppt/" + rels[s.get(R_ID)].lstrip("/").replace(
                "ppt/", "", 1))) for s in pres.iter(P + "sldId")]
            notes = [el for n in names if n.startswith("ppt/comments/") and n.endswith(".xml")
                     for el in ET.fromstring(z.read(n)).iter() if el.tag.endswith("}cm")]
    except (zipfile.BadZipFile, ET.ParseError, OSError, KeyError, ValueError) as e:
        return UNREADABLE, [f"UNREADABLE  {type(e).__name__}: {e}"], {}

    size = pres.find(P + "sldSz")
    width, height = (int(size.get("cx")), int(size.get("cy"))) if size is not None else (0, 0)
    off, template, hidden, shapes = [], [], [], 0
    grouped = inherited = rotated = charts = 0
    for i, slide in enumerate(slides, 1):
        if slide.get("show") in ("0", "false"):
            hidden.append(f"slide {i} is hidden")
        tree = slide.find(P + "cSld/" + P + "spTree")
        tops = [el for el in (tree if tree is not None else []) if el.tag in SHAPES]
        for shape in tops:
            shapes += 1
            cnv = next(shape.iter(P + "cNvPr"), None)
            name = cnv.get("name", "?") if cnv is not None else "?"
            edges = outside(shape, width, height) if width else None
            if edges == "rotated":
                rotated += 1
            elif edges is None:
                inherited += 1
            elif edges:
                off.append(f"slide {i}: '{name}' runs past the {' and '.join(edges)}")
            if shape.tag == P + "grpSp":
                grouped += sum(1 for el in shape.iter() if el.tag in SHAPES) - 1
        for sp in slide.iter(P + "sp"):
            ph = sp.find(P + "nvSpPr/" + P + "nvPr/" + P + "ph")
            if ph is not None and ph.get("type") not in QUIET and not text_of(sp).strip():
                cnv = sp.find(P + "nvSpPr/" + P + "cNvPr")
                template.append(f"slide {i}: an empty {ph.get('type', 'content')} placeholder "
                                f"'{cnv.get('name', '?') if cnv is not None else '?'}'")
        for para in slide.iter(A + "p"):
            m = PROMPT.search(text_of(para))
            if m:
                template.append(f"slide {i}: {text_of(para).strip()[:50]!r}")
        charts += sum(1 for g in slide.iter(A + "graphicData")
                      if re.search(r"/(chart|diagram)$", g.get("uri", "")))

    rows = [row("off the slide", off, f"{len(off)} shape(s)" if off else "every shape inside"),
            row("template text", template, f"{len(template)} found" if template else "none"),
            row("comments", [repr("".join(c.itertext()).strip()[:50]) for c in notes],
                f"{len(notes)} left in the file" if notes else "none", "comments" in allow),
            row("hidden slides", hidden, f"{len(hidden)} hidden" if hidden else "none")]
    unseen = [f"{n} {what}" for n, what in (
        (grouped, "shape(s) inside a group - each group's outline is checked"),
        (inherited, "shape(s) take their position from the layout"),
        (rotated, "rotated shape(s)"), (charts, "chart or diagram(s): the text inside is not read"))
        if n]
    if not width:
        unseen.append("the slide size is not stated, so no position could be checked")
    return report(rows, unseen, f"{len(slides)} slide(s) of {width / CM:.1f} x {height / CM:.1f}"
                                f" cm, {shapes} shape(s)")


# ---- self-test. Every fixture is raw XML text written into a zip, never serialised by
# ElementTree, which rebinds namespace prefixes so that PowerPoint then rejects the file.
# The decks carry only the parts this checker reads - no master, layout or theme - so they
# test the READER; opening a real deck is a separate check, made by hand.
HEAD = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
PKG = "http://schemas.openxmlformats.org/package/2006/"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PML = "application/vnd.openxmlformats-officedocument.presentationml."
NS = (f'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="{REL}" '
      'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"')


def pptx(slides, comments=0):
    """A deck of 12192000 x 6858000 EMU: [(shape XML, hidden?)], and N legacy comments."""
    parts = {
        "[Content_Types].xml": f'{HEAD}<Types xmlns="{PKG}content-types"><Default Extension='
        '"rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default '
        f'Extension="xml" ContentType="application/xml"/><Override PartName="/ppt/presentation.'
        f'xml" ContentType="{PML}presentation.main+xml"/>' + "".join(
            f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="{PML}slide+xml"/>'
            for i in range(1, len(slides) + 1)) + "</Types>",
        "_rels/.rels": f'{HEAD}<Relationships xmlns="{PKG}relationships"><Relationship Id="rId1" '
        f'Type="{REL}/officeDocument" Target="ppt/presentation.xml"/></Relationships>',
        "ppt/presentation.xml": f"{HEAD}<p:presentation {NS}><p:sldIdLst>" + "".join(
            f'<p:sldId id="{255 + i}" r:id="rId{i}"/>' for i in range(1, len(slides) + 1))
        + '</p:sldIdLst><p:sldSz cx="12192000" cy="6858000"/></p:presentation>',
        "ppt/_rels/presentation.xml.rels": f'{HEAD}<Relationships xmlns="{PKG}relationships">'
        + "".join(f'<Relationship Id="rId{i}" Type="{REL}/slide" Target="slides/slide{i}.xml"/>'
                  for i in range(1, len(slides) + 1)) + "</Relationships>"}
    for i, (shapes, hide) in enumerate(slides, 1):
        parts[f"ppt/slides/slide{i}.xml"] = (
            f'{HEAD}<p:sld {NS}{" show=" + chr(34) + "0" + chr(34) if hide else ""}><p:cSld>'
            '<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/>'
            f'</p:nvGrpSpPr><p:grpSpPr/>{shapes}</p:spTree></p:cSld></p:sld>')
    if comments:
        parts["ppt/comments/comment1.xml"] = f"{HEAD}<p:cmLst {NS}>" + "".join(
            f'<p:cm authorId="0" idx="{k}"><p:pos x="10" y="10"/><p:text>check</p:text></p:cm>'
            for k in range(1, comments + 1)) + "</p:cmLst>"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, text in parts.items():
            z.writestr(name, text)
    buf.seek(0)
    return buf


def box(name, at=(1000000, 1000000, 2000000, 500000), text="words", ph=""):
    """A text box, or a placeholder when ph is given; at=None takes the layout's position."""
    pos = "" if at is None else (f'<a:xfrm><a:off x="{at[0]}" y="{at[1]}"/>'
                                 f'<a:ext cx="{at[2]}" cy="{at[3]}"/></a:xfrm>')
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="2" name="{name}"/><p:cNvSpPr/><p:nvPr>{ph}</p:nvPr>'
            f'</p:nvSpPr><p:spPr>{pos}</p:spPr><p:txBody><a:bodyPr/><a:p><a:r><a:t>{text}</a:t>'
            "</a:r></a:p></p:txBody></p:sp>")


def selftest():
    defect = [(box("TextBox 3", (11000000, 1000000, 2000000, 500000)), False)]
    twin = [(box("TextBox 3", (9000000, 1000000, 2000000, 500000)), False)]
    first = []
    for label, deck in (("FIRST RUN - a text box past the slide's right edge:", defect),
                        ("ITS CLEAN TWIN - the same box, inside the slide:", twin)):
        first.append(check(pptx(deck)))
        print(label + "\n" + "\n".join("  " + line for line in first[-1][1]))
    def verdict(deck, name, allow=(), comments=0):
        return check(pptx(deck, comments), allow)[2].get(name)
    group = ('<p:grpSp><p:nvGrpSpPr><p:cNvPr id="5" name="Group 5"/><p:cNvGrpSpPr/><p:nvPr/>'
             '</p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="100" cy="100"/>'
             '<a:chOff x="0" y="0"/><a:chExt cx="100" cy="100"/></a:xfrm></p:grpSpPr>'
             + box("inside", (99000000, 0, 10, 10)) + "</p:grpSp>")
    grouped, inherited = check(pptx([(group, False)])), check(pptx([(box("T", None), False)]))
    clean = [(box("T"), False)]
    cases = [
        ("the defect FAILS on off the slide", first[0][0] == FAIL
         and first[0][2]["off the slide"] == "FAIL" and "right edge" in "".join(first[0][1])),
        ("its clean twin PASSES every check", first[1][0] == PASS),
        ("a box past the LEFT edge -> FAIL", verdict(
            [(box("T", (-500000, 0, 100, 100)), False)], "off the slide") == "FAIL"),
        ("a hidden slide -> FAIL", verdict([(box("T"), True)], "hidden slides") == "FAIL"),
        ("no hidden slide -> PASS", verdict(clean, "hidden slides") == "PASS"),
        ("a comment -> FAIL", verdict(clean, "comments", (), 1) == "FAIL"),
        ("... and PASS, shown, with --allow comments",
         verdict(clean, "comments", ("comments",), 2) == "PASS"
         and "ALLOWED" in "".join(check(pptx(clean, 2), ("comments",))[1])),
        ("no comment -> PASS", verdict(clean, "comments") == "PASS"),
        ("an EMPTY title placeholder -> FAIL", verdict(
            [(box("Title 1", text="", ph='<p:ph type="title"/>'), False)], "template text") == "FAIL"),
        ("a FILLED title placeholder -> PASS", verdict(
            [(box("Title 1", text="Q3", ph='<p:ph type="title"/>'), False)], "template text") == "PASS"),
        ("an empty slide-number placeholder -> PASS", verdict(
            [(box("N", text="", ph='<p:ph type="sldNum"/>'), False)], "template text") == "PASS"),
        ("Lorem ipsum left as text -> FAIL", verdict(
            [(box("T", text="Lorem ipsum dolor"), False)], "template text") == "FAIL"),
        ("a layout prompt left as text -> FAIL", verdict(
            [(box("T", text="Click to add title"), False)], "template text") == "FAIL"),
        ("a shape inside a group -> NOT CHECKED, still exit 0",
         grouped[0] == PASS and "inside a group" in "".join(grouped[1])),
        ("a position from the layout -> NOT CHECKED",
         inherited[0] == PASS and "from the layout" in "".join(inherited[1])),
        ("not a zip -> exit 2", check(io.BytesIO(b"not a zip"))[0] == UNREADABLE),
    ]
    for name, ok in cases:
        print(f"  {'ok  ' if ok else 'FAIL'}  {name}")
    passed = sum(ok for _, ok in cases)
    print(f"selftest: {passed} of {len(cases)} cases")
    return PASS if passed == len(cases) else FAIL


def main(argv):
    if argv == ["--selftest"]:
        return selftest()
    allow, files, it = [], [], iter(argv)
    for a in it:
        if a == "--allow":
            allow.append(next(it, ""))
        else:
            files.append(a)
    if len(files) != 1 or any(a != "comments" for a in allow):
        print("usage: check_pptx.py FILE.pptx [--allow comments]")
        return UNREADABLE
    code, lines, _ = check(files[0], allow)
    print(f"check_pptx  {files[0]}\n" + "\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
