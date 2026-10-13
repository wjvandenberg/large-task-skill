#!/usr/bin/env python3
"""check_form.py - is a finished Excel or Word file built the way the user agreed?

Run it on the FINAL .xlsx or .docx, beside check_xlsx.py or check_docx.py, with the SIZE the
plan agreed. It checks two things only, evaluates no formula and judges no content.

    typed totals   Excel: a typed number equal to the sum of the two or more numbers directly
                   above it or to its left - a total written as a figure where a SUM belongs.
                   A numbering 1, 2, 3 is not one. check_xlsx.py cannot see this: a workbook
                   with no SUM gives it nothing to look at, and it passes.
    over the size  more tabs, more columns, or more words in a cell than agreed. Excel: every
                   tab, but an INPUT tab - typed numbers and no formula - never counts against
                   the tab limit. Word: every table, nested ones too. A row holding ONE text
                   cell alone is a title or a note line, and counts for neither columns nor words.

The defaults are the small ones - Excel 1 tab besides the input tabs, 6 columns, 8 words a
cell; Word 4 columns, 12 words. Pass the agreed size whenever the plan agreed another. The shape it prints lets the
plan's set-up be compared with what was built.

    python check_form.py FILE [--max-tabs N] [--max-columns N] [--max-words N]
    python check_form.py --selftest

EXIT: 0 PASS · 1 FAIL · 2 the file could not be read. NOT CHECKED alone keeps 0, and the
OVERALL line counts it.
"""
from __future__ import annotations

import argparse
import io
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
PKG_REL = "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"
CELL = re.compile(r"([A-Z]{1,3})(\d+)")
DEFAULTS = {"xlsx": {"tabs": 1, "columns": 6, "words": 8}, "docx": {"columns": 4, "words": 12}}
PASS, FAIL, UNREADABLE = 0, 1, 2


def report(rows, unseen, examined, shape):
    """What was examined, the shape, a line per check, what was NOT CHECKED, and one verdict."""
    lines = [f"examined    {examined}"] + [f"shape       {s}" for s in shape]
    for verdict, name, detail, items in rows:
        lines.append(f"{verdict:12}{name:18} {detail}")
        lines += [f"{'':14}{i}" for i in list(items)[:10]] if verdict == "FAIL" else []
    lines += [f"NOT CHECKED {u}" for u in unseen]
    failed = sum(r[0] == "FAIL" for r in rows)
    lines.append(f"OVERALL: {'FAIL' if failed else 'PASS'} - {failed} of {len(rows)} checks "
                 f"failed, {len(unseen)} NOT CHECKED")
    return (FAIL if failed else PASS), lines, {r[1]: r[0] for r in rows}


def col_num(letters):
    return sum((ord(ch) - 64) * 26 ** i for i, ch in enumerate(reversed(letters)))


def ref(r, c):
    name = lambda n: name((n - 1) // 26) + chr(65 + (n - 1) % 26) if n > 0 else ""  # noqa: E731
    return f"{name(c)}{r}"


def load_xlsx(z):
    """[(tab, {(row, col): (kind, value)})]: kind 'f' a formula, its value the saved number, or
    None, or 'value'; 'n' a typed number; 's' text, never empty."""
    strings = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(S + "si"):
            strings.append("".join(t.text or "" for part in si if part.tag != S + "rPh"
                                   for t in ([part] if part.tag == S + "t" else part.iter(S + "t"))))
    rels = {r.get("Id"): r.get("Target") for r in
            ET.fromstring(z.read("xl/_rels/workbook.xml.rels")).iter(PKG_REL)}
    tabs = []
    for sh in ET.fromstring(z.read("xl/workbook.xml")).iter(S + "sheet"):
        target = rels.get(sh.get(R_ID), "")
        path = target.lstrip("/") if target.startswith("/") else "xl/" + target
        cells = {}                                   # a chart sheet is a tab with no cells
        for c in ET.fromstring(z.read(path)).iter(S + "c") if "worksheets/" in path else ():
            m, t, text = CELL.fullmatch(c.get("r") or ""), c.get("t", "n"), c.findtext(S + "v") or None
            if not m:
                continue
            key = (int(m.group(2)), col_num(m.group(1)))
            if c.find(S + "f") is not None:
                number = text is not None and t == "n" and re.fullmatch(r"[-+.\dEe]+", text)
                cells[key] = ("f", float(text) if number else None if text is None else "value")
            elif t in ("s", "str", "inlineStr"):
                s = (strings[int(text)] if t == "s" and text is not None else text or "" if t == "str"
                     else "".join(x.text or "" for x in c.iter(S + "t")))
                if s.strip():
                    cells[key] = ("s", s)
            elif t == "n" and text is not None:
                cells[key] = ("n", float(text))
        tabs.append((sh.get("name"), cells))
    return tabs


def typed_totals(name, cells):
    """(found, blocked): the typed totals, and the typed numbers a formula with no saved result hides."""
    found, blocked = [], 0
    for (r, c), (kind, val) in sorted(cells.items()):
        if kind != "n" or val == 0:
            continue
        for dr, dc in ((-1, 0), (0, -1)):
            run, rr, cc = [], r + dr, c + dc
            while cells.get((rr, cc), ("", ""))[0] in ("n", "f"):
                v = cells[(rr, cc)][1]
                blocked += v is None
                if not isinstance(v, float):
                    break
                run.append(v)
                rr, cc = rr + dr, cc + dc
            hit, total = False, 0.0
            for k, x in enumerate(run, 1):              # the two nearest, the three nearest...
                total += x                               # a running sum: one pass, not one per k
                if k < 2 or abs(total - val) >= 0.005:
                    continue
                seq = run[:k][::-1] + [val]              # 1, 2, 3 is a numbering, not a total
                hit = {round(b - a, 6) for a, b in zip(seq, seq[1:])} != {1}
                if hit:
                    break
            if hit:
                where = "the numbers above" if dr else "the numbers to its left"
                found.append(f"{name}!{ref(r, c)} is typed as {val:g}, the sum of {where}")
                break
    return found, blocked


def measure(rows, where, limits):
    """(shape, over) for rows of [(col, value, label)]: one text cell alone is a note; columns are
    cells, never Word's layout grid, which can hold more columns than any row shows."""
    words = lambda v: len(v.split()) if isinstance(v, str) else 0  # noqa: E731
    table = [row for row in rows if not (len(row) == 1 and isinstance(row[0][1], str))]
    ncols = len({col for row in table for col, _, _ in row})
    longest = max((words(v) for row in table for _, v, _ in row), default=0)
    over = [f"{where} has {ncols} columns, against {limits['columns']}"] \
        if ncols > limits["columns"] else []
    over += [f"{label} holds {words(v)} words, against {limits['words']}"
             for row in table for _, v, label in row if words(v) > limits["words"]]
    return f"{where}: {len(rows)} rows, {ncols} columns, longest cell {longest} words", over


def verdicts(checks, limits, over):
    return checks + [("FAIL" if over else "PASS", "over the size", f"{len(over)} over" if over
                      else "within " + ", ".join(f"{v} {k}" for k, v in limits.items()), over)]


def check_xlsx(z, limits):
    tabs = load_xlsx(z)
    typed, blocked, over, shape = [], 0, [], []
    for name, cells in tabs:
        found, b = typed_totals(name, cells)
        typed, blocked = typed + found, blocked + b
        by_row = {}
        for (r, c), (_, val) in sorted(cells.items()):
            by_row.setdefault(r, []).append((c, val, f"{name}!{ref(r, c)}"))
        line, o = measure(list(by_row.values()), f"tab {name!r}", limits)
        shape, over = shape + [line], over + o
    counted = [nm for nm, c in tabs if not ({"n"} <= {k for k, _ in c.values()} <= {"n", "s"})]
    if len(counted) > limits["tabs"]:                  # an input tab - typed numbers, no formula
        over.insert(0, f"{len(counted)} tabs besides the input tabs, against {limits['tabs']}")
    rows = verdicts([("FAIL" if typed else "PASS", "typed totals", f"{len(typed)} found - each "
                      "should be a formula" if typed else "none found", typed)], limits, over)
    unseen = [f"{blocked} typed number(s) beside a formula with no saved result - the file was "
              "never recalculated, so whether they are totals cannot be tested"] if blocked else []
    return report(rows, unseen, f"{len(tabs)} tab(s), {sum(len(c) for _, c in tabs)} cells", shape)


def check_docx(z, limits):
    over, shape = [], []
    for n, tbl in enumerate(ET.fromstring(z.read("word/document.xml")).iter(W + "tbl"), 1):
        rows = [[(i, " ".join("".join(t.text or "" for t in p.iter(W + "t"))
                              for p in tc.findall(W + "p")), f"table {n}, row {r}, cell {i + 1}")
                 for i, tc in enumerate(tr.findall(W + "tc"))]
                for r, tr in enumerate(tbl.findall(W + "tr"), 1)]
        line, o = measure(rows, f"table {n}", limits)
        shape, over = shape + [line], over + o
    return report(verdicts([], limits, over), [], f"{len(shape)} table(s) in the body", shape)


def check(source, limits=None):
    """(exit code, report lines, {check: verdict}) for a path or a file-like object."""
    try:
        with zipfile.ZipFile(source) as z:
            names = z.namelist()
            kind = "xlsx" if "xl/workbook.xml" in names else "docx" if "word/document.xml" in names else ""
            if not kind:
                return UNREADABLE, ["UNREADABLE  neither an Excel workbook nor a Word document"], {}
            lim = {k: (limits or {}).get(k) or v for k, v in DEFAULTS[kind].items()}
            return check_xlsx(z, lim) if kind == "xlsx" else check_docx(z, lim)
    except (zipfile.BadZipFile, ET.ParseError, OSError, KeyError, ValueError, IndexError) as e:
        return UNREADABLE, [f"UNREADABLE  {type(e).__name__}: {e}"], {}


# ---- self-test. Every fixture is raw XML text written into a zip.
HEAD = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
WNS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'


def zipped(parts):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, text in parts.items():
            z.writestr(name, text)
    buf.seek(0)
    return buf


def xlsx(tabs):
    """[(tab name, [cell XML])] - text inline, so no shared strings are needed."""
    parts = {"xl/workbook.xml": f'{HEAD}<workbook {NS} xmlns:r="{REL}"><sheets>' + "".join(
                 f'<sheet name="{n}" sheetId="{i}" r:id="rId{i}"/>' for i, (n, _) in enumerate(tabs, 1))
             + "</sheets></workbook>",
             "xl/_rels/workbook.xml.rels": '<Relationships xmlns="http://schemas.openxmlformats.org/'
             'package/2006/relationships">' + "".join(
                 f'<Relationship Id="rId{i}" Type="{REL}/worksheet" Target="worksheets/sheet{i}.xml"/>'
                 for i in range(1, len(tabs) + 1)) + "</Relationships>"}
    for i, (_, cells) in enumerate(tabs, 1):
        parts[f"xl/worksheets/sheet{i}.xml"] = (f"{HEAD}<worksheet {NS}><sheetData><row>"
                                                + "".join(cells) + "</row></sheetData></worksheet>")
    return zipped(parts)


def docx(tables):
    """[[row, ...]] per table, each row a list of cell texts."""
    body = "".join("<w:tbl>" + "".join("<w:tr>" + "".join(
        f"<w:tc><w:p><w:r><w:t>{t}</w:t></w:r></w:p></w:tc>" for t in row) + "</w:tr>"
        for row in rows) + "</w:tbl>" for rows in tables)
    return zipped({"word/document.xml": f"{HEAD}<w:document {WNS}><w:body>{body}</w:body></w:document>"})


def selftest():
    n = lambda at, v: f'<c r="{at}"><v>{v}</v></c>'  # noqa: E731 - cell XML, by kind
    s = lambda at, text: f'<c r="{at}" t="inlineStr"><is><t>{text}</t></is></c>'  # noqa: E731
    fx = lambda at, f, v=None: f'<c r="{at}"><f>{f}</f>' + ("" if v is None else f"<v>{v}</v>") + "</c>"  # noqa: E731
    # the defect as it was delivered: a column of figures, and its total typed in as 400
    defect = [("Loans", [n("B2", 100), n("B3", 250), n("B4", 50), n("B5", 400)])]
    twin = [("Loans", [n("B2", 100), n("B3", 250), n("B4", 50), fx("B5", "SUM(B2:B4)", 400)])]
    first = []
    for label, book in (("FIRST RUN - a total typed in as a figure:", defect),
                        ("ITS CLEAN TWIN - the same total as a SUM:", twin)):
        first.append(check(xlsx(book)))
        print(label + "\n" + "\n".join("  " + line for line in first[-1][1]))
    def v(book, name, limits=None):
        return check(book, limits)[2].get(name)
    nine, twenty, three = " ".join(["w"] * 9), " ".join(["w"] * 20), [("A", []), ("B", []), ("C", [])]
    cases = [
        ("the defect FAILS on typed totals", first[0][0] == FAIL and first[0][2]["typed totals"] == "FAIL"),
        ("its clean twin PASSES every check", first[1][0] == PASS),
        ("CONTROL: the single column counts as 1 column, not 0", "1 columns" in "".join(first[1][1])),
        ("a total at a row's end, a year first -> FAIL", v(xlsx([("S", [
            n("A1", 2029), n("B1", 100), n("C1", 200), n("D1", 300)])]), "typed totals") == "FAIL"),
        ("a numbering 1, 2, 3 -> PASS", v(xlsx([("S", [n("A1", 1), n("A2", 2), n("A3", 3)])]), "typed totals") == "PASS"),
        ("not the sum -> PASS", v(xlsx([("S", [n("A1", 100), n("A2", 250), n("A3", 351)])]), "typed totals") == "PASS"),
        ("beside a formula with no saved result -> NOT CHECKED",
         "no saved result" in "".join(check(xlsx([("S", [fx("A1", "B9"), n("A2", 5), n("A3", 5)])]))[1])),
        ("3 tabs against 1 -> FAIL", v(xlsx(three), "over the size") == "FAIL"),
        ("3 tabs, 3 agreed -> PASS", v(xlsx(three), "over the size", {"tabs": 3}) == "PASS"),
        ("1 answer tab and 3 input tabs -> PASS", v(xlsx([("A", [fx("A1", "B1", 1)])] + [
            (f"I{i}", [s("A1", "Rate"), n("B1", i + 1)]) for i in range(3)]), "over the size") == "PASS"),
        ("7 columns against 6 -> FAIL", v(xlsx([("S", [n(f"{c}1", 1) for c in "ABCDEFG"])]), "over the size") == "FAIL"),
        ("a 9-word cell in a table row -> FAIL",
         v(xlsx([("S", [s("A1", "Year"), s("B1", nine)])]), "over the size") == "FAIL"),
        ("the same, 10 words agreed -> PASS",
         v(xlsx([("S", [s("A1", "Year"), s("B1", nine)])]), "over the size", {"words": 10}) == "PASS"),
        ("a 20-word note alone in its row -> PASS", v(xlsx([("S", [s("A9", twenty)])]), "over the size") == "PASS"),
        ("Word: a 5-column table -> FAIL", v(docx([[["a"] * 5]]), "over the size") == "FAIL"),
        ("Word: 4 columns of 12 words -> PASS", v(docx([[[" ".join(["w"] * 12)] * 4]]), "over the size") == "PASS"),
        ("Word: a 13-word cell -> FAIL", v(docx([[["a", " ".join(["w"] * 13)]]]), "over the size") == "FAIL"),
        ("Word: a heading row of one cell -> PASS", v(docx([[[twenty], ["a", "b"]]]), "over the size") == "PASS"),
        ("Word: the second table is checked too -> FAIL", v(docx([[["a", "b"]], [["a"] * 6]]), "over the size") == "FAIL"),
        ("not a zip -> exit 2", check(io.BytesIO(b"not a zip"))[0] == UNREADABLE),
        ("a zip that is neither -> exit 2", check(zipped({"x.xml": "<x/>"}))[0] == UNREADABLE),
    ]
    for name, ok in cases:
        print(f"  {'ok  ' if ok else 'FAIL'}  {name}")
    passed = sum(ok for _, ok in cases)
    print(f"selftest: {passed} of {len(cases)} cases")
    return PASS if passed == len(cases) else FAIL


def main(argv):
    if argv == ["--selftest"]:
        return selftest()
    p = argparse.ArgumentParser(prog="check_form.py")      # a usage error exits 2, as unread
    p.add_argument("file")
    for k in ("tabs", "columns", "words"):
        p.add_argument(f"--max-{k}", type=int, dest=k)
    a = p.parse_args(argv)
    code, lines, _ = check(a.file, {"tabs": a.tabs, "columns": a.columns, "words": a.words})
    print(f"check_form  {a.file}\n" + "\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
