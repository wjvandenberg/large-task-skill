#!/usr/bin/env python3
"""check_xlsx.py - a LIGHT check of a finished Excel file, for what "it opens" misses.

Run it on the FINAL .xlsx, whenever the final deliverable is an Excel file. The plan's own
criteria check the NUMBERS first; this checks two things only, and evaluates no formula.

    error values       a cell showing #REF!, #DIV/0!, #N/A, #VALUE!, #NAME? and the like
    numbers as text    a cell inside a SUM's range holding a number stored as TEXT. SUM
                       skips it without a word, so the total is wrong and shows no error

What it cannot see it says so, as NOT CHECKED - a formula with no saved result, a SUM over
a named range or another workbook - never skipping silently.

    python check_xlsx.py FILE.xlsx
    python check_xlsx.py --selftest

EXIT: 0 PASS · 1 FAIL · 2 the file could not be read. NOT CHECKED alone keeps 0, and the
OVERALL line counts it.
"""
from __future__ import annotations

import io
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
PKG_REL = "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"
CELL = r"(\$?)([A-Z]{1,3})(\$?)(\d+)"
# One reference: an optional sheet, then a cell, a cell range, or a whole-column range.
# Groups: 1-2 sheet · 3-6 first cell · 7-10 second cell · 11-12 the columns of A:B.
REF = re.compile(r"(?<![\w.$])(?:(?:'((?:[^']|'')+)'|([A-Za-z_][\w.]*))!)?(?:" + CELL
                 + r"(?::" + CELL + r")?|\$?([A-Z]{1,3}):\$?([A-Z]{1,3}))(?![\w(])")
SUM = re.compile(r"(?<![\w.])SUM\(", re.I)
# Euro, pound and yen, and the no-break space, built from their codes so the source stays
# plain ASCII: a file-writing tool was measured turning the escape into the bare character.
MONEY, NBSP = "$" + chr(0x20AC) + chr(0xA3) + chr(0xA5), chr(0xA0)
NUMBER = re.compile(r"[-+(]?\s*[" + MONEY + r"]?\s*\d[\d.,' " + NBSP + r"]*%?\s*\)?")
PASS, FAIL, UNREADABLE = 0, 1, 2


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


def col_num(letters):
    """A column's number from its letters: A is 1, Z is 26, AA is 27."""
    return sum((ord(ch) - 64) * 26 ** i for i, ch in enumerate(reversed(letters)))


def shift(formula, dr, dc):
    """A shared formula as it reads in a cell dr rows and dc columns from its first cell."""
    def col_name(n):
        return col_name((n - 1) // 26) + chr(65 + (n - 1) % 26) if n > 0 else ""
    def one(m):
        col = m.group(2) if m.group(1) else col_name(col_num(m.group(2)) + dc)
        return f"{m.group(1)}{col}{m.group(3)}{m.group(4) if m.group(3) else int(m.group(4)) + dr}"
    return re.sub(r"(?<![\w.])" + CELL + r"(?![\w(])", one, formula)


def sum_args(formula):
    """The argument text of every SUM(...) in a formula."""
    out = []
    for m in SUM.finditer(formula):
        depth, i = 1, m.end()
        while i < len(formula) and depth:
            depth += {"(": 1, ")": -1}.get(formula[i], 0)
            i += 1
        out.append(formula[m.end():i - 1])
    return out


def unresolvable(args):
    """True when a SUM names something this scan cannot place: a name, or another workbook."""
    rest = re.sub(r"[A-Za-z_][\w.]*\s*\(", "(", re.sub(r'"[^"]*"', "", REF.sub("", args)))
    return "[" in args or bool(re.search(r"[A-Za-z_]", rest))


def load(z):
    """({sheet: {cell: (type, shown text, formula element)}}, cells with no address)."""
    strings, loose = [], 0
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(S + "si"):
            strings.append("".join(t.text or "" for part in si if part.tag != S + "rPh"
                                   for t in ([part] if part.tag == S + "t" else part.iter(S + "t"))))
    rels = {r.get("Id"): r.get("Target") for r in
            ET.fromstring(z.read("xl/_rels/workbook.xml.rels")).iter(PKG_REL)}
    sheets = {}
    for sh in ET.fromstring(z.read("xl/workbook.xml")).iter(S + "sheet"):
        target = rels.get(sh.get(R_ID), "")
        path = target.lstrip("/") if target.startswith("/") else "xl/" + target
        if "worksheets/" not in path:
            continue                                        # a chart sheet holds no cells
        cells = sheets.setdefault(sh.get("name"), {})
        for c in ET.fromstring(z.read(path)).iter(S + "c"):
            t, v = c.get("t", "n"), c.find(S + "v")
            text = v.text if v is not None else None
            if t == "s" and text is not None:
                text = strings[int(text)]
            elif t == "inlineStr":
                text = "".join(x.text or "" for x in c.iter(S + "t"))
            if c.get("r") is None:
                loose += 1
            else:
                cells[c.get("r")] = (t, text, c.find(S + "f"))
    return sheets, loose


def check(source):
    """(exit code, report lines, {check: verdict}) for a path or a file-like object."""
    try:
        with zipfile.ZipFile(source) as z:
            if "xl/workbook.xml" not in z.namelist():
                return UNREADABLE, ["UNREADABLE  no xl/workbook.xml - not an Excel workbook"], {}
            sheets, loose = load(z)
    except (zipfile.BadZipFile, ET.ParseError, OSError, KeyError, ValueError, IndexError) as e:
        return UNREADABLE, [f"UNREADABLE  {type(e).__name__}: {e}"], {}
    errors, uncached, sums, unresolved, astext = [], 0, 0, [], {}
    # Number-as-text cells, found ONCE per sheet: a walk per SUM took 15 s on 22,000 cells.
    texty = {name: [(col_num(m.group(2)), int(m.group(4)), ref, text)
                    for ref, (t, text, _) in cells.items() for m in [re.match(CELL, ref)]
                    if t in ("s", "inlineStr", "str") and text and NUMBER.fullmatch(text.strip())]
             for name, cells in sheets.items()}
    def hunt(target, area, where):
        """Record every text cell inside the area whose text is a number."""
        if target not in sheets:
            unresolved.append(where.split(" in ")[-1])
            return
        (c1, c2), (r1, r2) = sorted(area[:2]), sorted(area[2:])
        for col, rw, ref, text in texty[target]:
            if c1 <= col <= c2 and r1 <= rw <= r2:
                astext.setdefault((target, ref), f"{target}!{ref} holds {text!r} as TEXT, inside {where}")
    for name, cells in sheets.items():
        masters = {f.get("si"): (f.text, ref) for ref, (t, _, f) in cells.items()
                   if f is not None and f.get("t") == "shared" and f.text}
        for ref, (t, text, f) in cells.items():
            if t == "e":
                errors.append(f"{name}!{ref} shows {text}")
            if f is None:
                continue
            formula = f.text or ""
            if not formula and f.get("si") in masters:
                first, at = masters[f.get("si")]
                (_, c0, _, r0), (_, c1, _, r1) = re.match(CELL, at).groups(), re.match(CELL, ref).groups()
                formula = shift(first, int(r1) - int(r0), col_num(c1) - col_num(c0))
            uncached += text is None
            if "#REF!" in formula and t != "e":
                errors.append(f"{name}!{ref} has #REF! in its formula")
            for args in sum_args(formula):
                sums += 1
                where = f"SUM({args}) in {name}!{ref}"
                if unresolvable(args):
                    unresolved.append(f"{name}!{ref}")
                    continue
                for m in REF.finditer(args):
                    target = (m.group(1) or "").replace("''", "'") or m.group(2) or name
                    if m.group(11):                              # a whole-column range, A:B
                        hunt(target, (col_num(m.group(11)), col_num(m.group(12)), 1, 1 << 20), where)
                    else:
                        hunt(target, (col_num(m.group(4)), col_num(m.group(8) or m.group(4)),
                                      int(m.group(6)), int(m.group(10) or m.group(6))), where)
    rows = [("FAIL" if errors else "PASS", "error values",
             f"{len(errors)} found" if errors else "none shown", errors),
            ("FAIL" if astext else "PASS", "numbers as text", f"{len(astext)} inside summed "
             "ranges" if astext else "none inside summed ranges", list(astext.values()))]
    unseen = [f"{uncached} formula(s) carry no saved result - the file was never recalculated,"
              " so an error they would show cannot be seen"] if uncached else []
    if unresolved:
        unseen.append(f"{len(unresolved)} SUM(s) over a name, another workbook or a sheet not "
                      f"found: {', '.join(sorted(set(unresolved))[:5])}")
    if loose:
        unseen.append(f"{loose} cell(s) saved with no address, so no range can place them")
    ncells = sum(len(c) for c in sheets.values())
    return report(rows, unseen, f"{len(sheets)} sheet(s), {ncells} cells, {sums} SUM(s)")


# ---- self-test. Every fixture is raw XML text written into a zip, never serialised by
# ElementTree, which rebinds namespace prefixes so that Excel then rejects the file.
HEAD = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
PKG = "http://schemas.openxmlformats.org/package/2006/"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
SML = "application/vnd.openxmlformats-officedocument.spreadsheetml."
NS = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'


def xlsx(sheets, strings=()):
    """A minimal workbook: [(sheet name, [cell XML])], and its shared strings."""
    ws = [f"xl/worksheets/sheet{i}.xml" for i in range(1, len(sheets) + 1)]
    kinds = [("xl/workbook.xml", "sheet.main"), ("xl/sharedStrings.xml", "sharedStrings")]
    parts = {
        "[Content_Types].xml": f'{HEAD}<Types xmlns="{PKG}content-types"><Default Extension='
        '"rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default '
        'Extension="xml" ContentType="application/xml"/>' + "".join(
            f'<Override PartName="/{p}" ContentType="{SML}{k}+xml"/>'
            for p, k in kinds + [(w, "worksheet") for w in ws]) + "</Types>",
        "_rels/.rels": f'{HEAD}<Relationships xmlns="{PKG}relationships"><Relationship Id="rId1" '
        f'Type="{REL}/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        "xl/_rels/workbook.xml.rels": f'{HEAD}<Relationships xmlns="{PKG}relationships"><Relationship'
        f' Id="rS" Type="{REL}/sharedStrings" Target="sharedStrings.xml"/>' + "".join(
            f'<Relationship Id="rId{i}" Type="{REL}/worksheet" Target="{w[3:]}"/>'
            for i, w in enumerate(ws, 1)) + "</Relationships>",
        "xl/workbook.xml": f'{HEAD}<workbook {NS} xmlns:r="{REL}"><sheets>' + "".join(
            f'<sheet name="{name}" sheetId="{i}" r:id="rId{i}"/>'
            for i, (name, _) in enumerate(sheets, 1)) + "</sheets></workbook>",
        "xl/sharedStrings.xml": f'{HEAD}<sst {NS} count="{len(strings)}" uniqueCount="'
        f'{len(strings)}">' + "".join(f"<si><t>{s}</t></si>" for s in strings) + "</sst>"}
    for w, (_, cells) in zip(ws, sheets):
        rows = {}
        for c in cells:
            rows.setdefault(int(re.search(r'r="[A-Z]+(\d+)"', c).group(1)), []).append(c)
        parts[w] = f"{HEAD}<worksheet {NS}><sheetData>" + "".join(
            f'<row r="{n}">{"".join(rows[n])}</row>' for n in sorted(rows)) + "</sheetData></worksheet>"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, text in parts.items():
            z.writestr(name, text)
    buf.seek(0)
    return buf


def selftest():
    def n(ref, v):
        return f'<c r="{ref}"><v>{v}</v></c>'
    def s(ref, i):
        return f'<c r="{ref}" t="s"><v>{i}</v></c>'
    def fx(ref, formula, v=None, t=""):
        return f'<c r="{ref}"{t}><f>{formula}</f>' + ("" if v is None else f"<v>{v}</v>") + "</c>"
    # the amount in B3 was pasted as text: SUM skips it, so the total reads 150, not 400
    defect = [("Costs", [n("B2", 100), s("B3", 0), n("B4", 50), fx("B5", "SUM(B2:B4)", 150)])]
    twin = [("Costs", [n("B2", 100), n("B3", 250), n("B4", 50), fx("B5", "SUM(B2:B4)", 400)])]
    first = []
    for label, book in (("FIRST RUN - an amount stored as text in a summed column:", defect),
                        ("ITS CLEAN TWIN - the amount stored as a number:", twin)):
        first.append(check(xlsx(book, ["250"])))
        print(label + "\n" + "\n".join("  " + line for line in first[-1][1]))
    def verdict(book, name="numbers as text", strings=("250",)):
        return check(xlsx(book, list(strings)))[2].get(name)
    def one(at, formula, strings=("250",)):       # B2 a number, the text cell at `at`
        return verdict([("S", [n("B2", 1), s(at, 0), fx("D1", formula, 1)])], strings=strings)
    shared = [("S", [n("C2", 1), n("C3", 2), n("D2", 3), s("D3", 0), n("C4", 4), n("D4", 5),
                     '<c r="C5"><f t="shared" ref="C5:D5" si="0">SUM(C2:C4)</f><v>7</v></c>',
                     '<c r="D5"><f t="shared" si="0"/><v>8</v></c>'])]
    other = [("Main", [fx("B6", "SUM('Other Sheet'!A1:A2)", 1)]),
             ("Other Sheet", [n("A1", 1), s("A2", 0)])]
    named = check(xlsx([("S", [n("A1", 1), fx("A2", "SUM(Total)", 1)])]))
    fresh = check(xlsx([("S", [n("A1", 1), fx("A2", "A1*2")])]))
    cases = [
        ("the defect FAILS on numbers as text", first[0][0] == FAIL
         and first[0][2]["numbers as text"] == "FAIL"),
        ("CONTROL: and shows no error value - the wrong total is silent",
         first[0][2]["error values"] == "PASS"),
        ("its clean twin PASSES every check", first[1][0] == PASS),
        ("a cell showing #DIV/0! -> FAIL",
         verdict([("S", [fx("C1", "1/0", "#DIV/0!", ' t="e"')])], "error values") == "FAIL"),
        ("a SHARED formula's later cell is followed -> FAIL", verdict(shared) == "FAIL"
         and "D5" in "".join(check(xlsx(shared, ["6"]))[1])),
        ("a sum on another sheet, quoted name -> FAIL", verdict(other) == "FAIL"),
        ("a whole-column SUM(B:B) -> FAIL", one("B3", "SUM(B:B)") == "FAIL"),
        ("a euro amount in brackets, as text -> FAIL",
         one("B3", "SUM(B2:B3)", ["(" + chr(0x20AC) + " 1.250,00)"]) == "FAIL"),
        ("text that is not a number, in the range -> PASS",
         one("B3", "SUM(B2:B3)", ["n/a"]) == "PASS"),
        ("a number as text OUTSIDE every range -> PASS", one("B9", "SUM(B2:B3)") == "PASS"),
        ("a SUM over a name -> NOT CHECKED, still exit 0",
         named[0] == PASS and "over a name" in "".join(named[1])),
        ("a formula with no saved result -> NOT CHECKED",
         fresh[0] == PASS and "no saved result" in "".join(fresh[1])),
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
    if len(argv) != 1:
        print("usage: check_xlsx.py FILE.xlsx")
        return UNREADABLE
    code, lines, _ = check(argv[0])
    print(f"check_xlsx  {argv[0]}\n" + "\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
