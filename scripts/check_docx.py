#!/usr/bin/env python3
"""check_docx.py - a LIGHT check of a finished Word file, for what "it opens" misses.

Run it on the FINAL .docx, whenever the final deliverable is a Word file. Whether the
CONTENT is right is the plan's own criteria, checked first; this checks only that the file
does not still carry its drafting. It reads the XML - it renders and evaluates nothing.

    tracked changes    insertions, deletions, moves or formatting changes left in the file
    comments           comments left in the file
    cross-references   a REF, PAGEREF or NOTEREF field, or an internal link, whose bookmark
                       no longer exists. The number it shows can still look right: the
                       break appears only when Word next updates its fields
    Markdown symbols   **bold**, __bold__, a paragraph opening "# ", `code`, [text](link)

What it cannot see it says so, as NOT CHECKED - it never skips silently.

    python check_docx.py FILE.docx [--allow tracked-changes] [--allow comments]
    python check_docx.py --selftest

--allow is for a deliverable the plan says IS a markup; the report shows the allowance.
EXIT: 0 PASS · 1 FAIL · 2 the file could not be read. NOT CHECKED alone keeps 0, and the
OVERALL line counts it.
"""
from __future__ import annotations

import io
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
FALLBACK = "{http://schemas.openxmlformats.org/markup-compatibility/2006}Fallback"
STORY = re.compile(r"word/(document|header\d*|footer\d*|footnotes|endnotes)\.xml$")
CHANGES = {"ins", "del", "moveFrom", "moveTo", "rPrChange", "pPrChange", "sectPrChange",
           "tblPrChange", "trPrChange", "tcPrChange", "cellIns", "cellDel"}
FIELD_REF = re.compile(r"\s*(REF|PAGEREF|NOTEREF)\s+([^\s\\]+)", re.I)
WORD_ERRORS = ("Error! Reference source not found", "Error! Bookmark not defined")
MARKDOWN = [("**bold**", re.compile(r"\*\*[^*\s][^*]*\*\*")),
            ("__bold__", re.compile(r"__[^_\s][^_]*__")),
            ("# heading", re.compile(r"#{1,6}\s+\S")),
            ("`code`", re.compile(r"`[^`]+`")),
            ("[text](link)", re.compile(r"\[[^\]]+\]\((?:https?://|mailto:|www\.|#)[^)\s]*\)"))]
UNREAD = re.compile(r"word/(embeddings|charts|diagrams)/")
PASS, FAIL, UNREADABLE = 0, 1, 2
ALLOWABLE = ("tracked-changes", "comments")
USAGE = "usage: check_docx.py FILE.docx [--allow tracked-changes] [--allow comments]"


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


def walk(el):
    """Every element in document order, skipping the mc:Fallback copy of anything that has one."""
    yield el
    for child in el:
        if child.tag != FALLBACK:
            yield from walk(child)


def paragraphs(root):
    """The text of each paragraph, joined across its runs - a nested paragraph kept apart."""
    out = []

    def visit(el, buf):
        for child in el:
            if child.tag == W + "p":
                mine = []
                visit(child, mine)
                out.append("".join(mine))
            elif child.tag == W + "t":
                buf.append(child.text or "")
            elif child.tag != FALLBACK:
                visit(child, buf)
    visit(root, [])
    return out


def references(root):
    """(kind, target, shown) for each cross-reference: complex field, simple field, link."""
    refs, stack = [], []
    for el in walk(root):
        if el.tag == W + "fldChar":
            kind = el.get(W + "fldCharType")
            if kind == "begin":
                stack.append({"instr": [], "shown": [], "sep": False})
            elif kind == "separate" and stack:
                stack[-1]["sep"] = True
            elif kind == "end" and stack:
                f = stack.pop()
                m = FIELD_REF.match("".join(f["instr"]))
                if m:
                    refs.append((m.group(1).upper(), m.group(2), "".join(f["shown"])))
        elif el.tag == W + "instrText" and stack and not stack[-1]["sep"]:
            stack[-1]["instr"].append(el.text or "")
        elif el.tag == W + "t" and stack and stack[-1]["sep"]:
            stack[-1]["shown"].append(el.text or "")
        elif el.tag == W + "fldSimple":
            m = FIELD_REF.match(el.get(W + "instr", ""))
            if m:
                refs.append((m.group(1).upper(), m.group(2),
                             "".join(t.text or "" for t in el.iter(W + "t"))))
        elif el.tag == W + "hyperlink" and el.get(W + "anchor"):
            refs.append(("link to", el.get(W + "anchor"), ""))
    return refs


def check(source, allow=()):
    """(exit code, report lines, {check: verdict}) for a path or a file-like object."""
    try:
        z = zipfile.ZipFile(source)
        names = z.namelist()
        parts = sorted(n for n in names if STORY.match(n))
        if "word/document.xml" not in parts:
            return UNREADABLE, ["UNREADABLE  no word/document.xml - not a Word document"], {}
        trees = {n.split("/")[-1]: ET.fromstring(z.read(n)) for n in parts}
        noted = []
        if "word/comments.xml" in names:
            noted = list(ET.fromstring(z.read("word/comments.xml")).iter(W + "comment"))
    except (zipfile.BadZipFile, ET.ParseError, OSError) as e:
        return UNREADABLE, [f"UNREADABLE  {type(e).__name__}: {e}"], {}
    texts = {n: paragraphs(r) for n, r in trees.items()}
    counts = [(n, sum(1 for el in walk(r) if el.tag.startswith(W) and el.tag[len(W):] in CHANGES))
              for n, r in trees.items()]
    changes = [f"{c} in {n}" for n, c in counts if c]
    marked = sum(1 for r in trees.values() for el in walk(r) if el.tag == W + "commentReference")
    count = max(len(noted), marked)

    marks = {el.get(W + "name") for r in trees.values() for el in r.iter(W + "bookmarkStart")}
    marks.add("_top")                                   # Word's own: the top of the document
    refs = [(n,) + ref for n, r in trees.items() for ref in references(r)]
    broken = [f"{k} {t}" + (f' (still shown as "{s.strip()[:30]}")' if s.strip() else "")
              + f" in {n}: no bookmark by that name" for n, k, t, s in refs if t not in marks]
    broken += [f'Word\'s own "{e}" in {n}' for n, ps in texts.items() for p in ps
               for e in WORD_ERRORS if e in p]

    hits = []
    for n, ps in texts.items():
        for i, p in enumerate(ps, 1):
            for label, pat in MARKDOWN:
                m = pat.match(p) if label == "# heading" else pat.search(p)
                if m:
                    hits.append(f"{label} in {n}, paragraph {i}: {m.group(0)[:40]!r}")
    rows = [row("tracked changes", changes, f"{sum(c for _, c in counts)} found" if changes else "none",
                "tracked-changes" in allow),
            row("comments", [repr("".join(c.itertext()).strip()[:50]) for c in noted] or [
                f"{marked} comment mark(s)"][:marked], f"{count} left" if count else "none",
                "comments" in allow),
            row("cross-references", broken, f"{len(broken)} broken of {len(refs)}" if broken
                else f"{len(refs)} found, all resolve"),
            row("Markdown symbols", hits, f"{len(hits)} found" if hits else "none")]
    unread = [n for n in names if UNREAD.match(n)]
    unseen = [f"text inside {len(unread)} embedded object, chart or diagram part(s)"] if unread else []
    paras = sum(len(ps) for ps in texts.values())
    return report(rows, unseen, f"{len(trees)} part(s): {', '.join(trees)} - {paras} paragraphs")


# ---- self-test. Every fixture is raw XML text written into a zip, never serialised by
# ElementTree, which rebinds namespace prefixes so that Word then rejects the file.
HEAD = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
NS_W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
PKG = "http://schemas.openxmlformats.org/package/2006/"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/"
WML = "application/vnd.openxmlformats-officedocument.wordprocessingml."


def docx(body, comments="", extra=()):
    """A minimal Word file holding the body - and a comments part, when one is given."""
    over = f'<Override PartName="/word/comments.xml" ContentType="{WML}comments+xml"/>'
    link = f'<Relationship Id="rId9" Type="{REL}comments" Target="comments.xml"/>'
    parts = {
        "[Content_Types].xml": f'{HEAD}<Types xmlns="{PKG}content-types"><Default Extension='
        '"rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/><Override PartName='
        f'"/word/document.xml" ContentType="{WML}document.main+xml"/>'
        f'{over if comments else ""}</Types>',
        "_rels/.rels": f'{HEAD}<Relationships xmlns="{PKG}relationships"><Relationship Id='
        f'"rId1" Type="{REL}officeDocument" Target="word/document.xml"/></Relationships>',
        "word/_rels/document.xml.rels": f'{HEAD}<Relationships xmlns="{PKG}relationships">'
        f'{link if comments else ""}</Relationships>',
        "word/document.xml": f"{HEAD}<w:document {NS_W}><w:body>{body}</w:body></w:document>"}
    if comments:
        parts["word/comments.xml"] = f"{HEAD}<w:comments {NS_W}>{comments}</w:comments>"
    parts.update({name: f"{HEAD}<x/>" for name in extra})
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, text in parts.items():
            z.writestr(name, text)
    buf.seek(0)
    return buf


def selftest():
    def r(text):
        return f'<w:r><w:t xml:space="preserve">{text}</w:t></w:r>'
    def p(*runs):
        return "<w:p>" + "".join(runs) + "</w:p>"
    def heading(mark, text):
        return f'<w:p><w:bookmarkStart w:id="0" w:name="{mark}"/>{r(text)}<w:bookmarkEnd w:id="0"/></w:p>'

    # A REF field whose instruction is split over two runs, as Word often writes it.
    see = p(r("See clause "), '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
            '<w:r><w:instrText xml:space="preserve"> REF </w:instrText></w:r>'
            '<w:r><w:instrText xml:space="preserve">_Ref100 \\h </w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="separate"/></w:r>' + r("4.2")
            + '<w:r><w:fldChar w:fldCharType="end"/></w:r>', r(" below."))
    defect = heading("_Ref200", "4.1 Scope") + see        # the heading _Ref100 named is gone
    twin = heading("_Ref100", "4.2 Payment") + see
    with zipfile.ZipFile(docx(defect)) as z:
        xml = z.read("word/document.xml")
    first = []
    for label, body in (("FIRST RUN - a cross-reference to a DELETED heading, still showing its"
                         " old number:", defect), ("ITS CLEAN TWIN - the heading still there:", twin)):
        first.append(check(docx(body)))
        print(label + "\n" + "\n".join("  " + line for line in first[-1][1]))

    comment = '<w:comment w:id="0" w:author="A">' + p(r("check this")) + "</w:comment>"
    commented = p('<w:commentRangeStart w:id="0"/>', r("Price"), '<w:commentRangeEnd w:id="0"/>'
                  '<w:r><w:commentReference w:id="0"/></w:r>')
    inserted = p('<w:ins w:id="1" w:author="A" w:date="2026-01-01T00:00:00Z">', r("new"), "</w:ins>")
    plain = p(r("x"))
    charted = check(docx(plain, extra=("word/charts/chart1.xml",)))

    def verdict(body, name, allow=(), comments=""):
        return check(docx(body, comments), allow)[2].get(name)
    cases = [
        ("the defect FAILS on cross-references", first[0][0] == FAIL
         and first[0][2]["cross-references"] == "FAIL"),
        ("CONTROL: a plain search of its XML finds no error text", b"Error!" not in xml),
        ("CONTROL: and it still shows a plausible number", b">4.2<" in xml),
        ("its clean twin PASSES every check", first[1][0] == PASS),
        ("a PAGEREF simple field to a missing bookmark -> FAIL", verdict(p(
            '<w:fldSimple w:instr=" PAGEREF _Ref300 \\h ">', r("7"), "</w:fldSimple>"),
            "cross-references") == "FAIL"),
        ("an internal link to a missing bookmark -> FAIL", verdict(p(
            '<w:hyperlink w:anchor="_Toc9">', r("Scope"), "</w:hyperlink>"),
            "cross-references") == "FAIL"),
        ("Word's own error text -> FAIL", verdict(p(r("Error! Reference source not found.")),
                                                  "cross-references") == "FAIL"),
        ("a tracked insertion -> FAIL", verdict(inserted, "tracked changes") == "FAIL"),
        ("... and PASS, shown, with --allow tracked-changes",
         verdict(inserted, "tracked changes", ("tracked-changes",)) == "PASS"
         and "ALLOWED" in "".join(check(docx(inserted), ("tracked-changes",))[1])),
        ("no tracked change -> PASS", verdict(plain, "tracked changes") == "PASS"),
        ("a comment -> FAIL", verdict(commented, "comments", (), comment) == "FAIL"),
        ("... and PASS with --allow comments",
         verdict(commented, "comments", ("comments",), comment) == "PASS"),
        ("no comment -> PASS", verdict(plain, "comments") == "PASS"),
        ("**bold** split over two runs -> FAIL",
         verdict(p(r("**Key"), r(" term** means")), "Markdown symbols") == "FAIL"),
        ("a '## ' heading -> FAIL", verdict(p(r("## Scope")), "Markdown symbols") == "FAIL"),
        ("a signature line of underscores -> PASS",
         verdict(p(r("Signed: ____________")), "Markdown symbols") == "PASS"),
        ("a chart part -> NOT CHECKED, still exit 0",
         charted[0] == PASS and "NOT CHECKED text" in "".join(charted[1])),
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
    if len(files) != 1 or any(a not in ALLOWABLE for a in allow):
        print(USAGE)
        return UNREADABLE
    code, lines, _ = check(files[0], allow)
    print(f"check_docx  {files[0]}\n" + "\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
