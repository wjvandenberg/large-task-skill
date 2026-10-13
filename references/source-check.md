# Source check — for a review or an analysis

**Run it on every review or analysis before it is delivered** — a document review, a summary of
evidence, a chronology, a comparison of documents, a research finding: any work whose value is that it
says only what its sources say. `SKILL.md` says when it runs; this file says how.

**Excerpted and modified** from the skill `source-locked-verification`, version 2026-05-13, by
Larissa Meredith-Flister, licensed under the GNU Affero General Public License, version 3 (AGPL-3.0):
<https://www.gnu.org/licenses/agpl-3.0.html>. Modified 2026-09-24: eight of its 19 numbered rules
are kept — 1, 3, 4, 6, 7, 8, 9 and 16, each line word for word — the lines that only give a reason, the
worked examples and the lists of sources are left out, and the three steps below are added. This file,
as modified, is under the same licence.

## How to apply it — added here, not from the source

1. **Write each finding with its source, its pinpoint and its label** — one of the five in Rule 6 — as
   the finding is written, never added at the end.
2. **Before delivery, run the self-check in Rule 16 against every finding**, and correct every
   statement it shows to be unsupported: anchor it, relabel it, or cut it.
3. **List what the self-check changed**, each correction with its reason, in the research file's
   corrections register — or, with none, in the closeout — **never in the chat.** A self-check that
   changed nothing says so, in the same place.

<!-- EXCERPT BEGINS — every line from here to the marker that ends it is copied verbatim from the source -->

## Rule 1: Source-Locked Answers Only

Claude must answer using only:

- **materials provided by the user** (uploaded documents, pasted text, images, attachments); and/or
- **online sources Claude has actually accessed during the task**, where online research is appropriate or required.

Claude must not rely on background knowledge, memory, intuition, general legal knowledge, plausible assumptions, or "what usually happens". Internal knowledge may be used only to decide what to search for or where to look — never as the basis for a factual, legal, numerical, or procedural claim.

---

## Rule 3: No Unsupported Inferences

Claude must not infer facts, dates, numbers, rules, deadlines, legal consequences, procedural steps, motivations, causation, chronology, authorship, or relationships unless they are expressly stated in the provided materials or verified online sources.

This rule targets Claude's strongest and most dangerous instinct: the tendency to produce a complete, confident answer by filling gaps with what seems likely. In source-locked mode, gaps stay as gaps.

---

## Rule 4: Mandatory Evidential Anchoring

Every material factual, legal, procedural, numerical, or chronological statement must be tied to a source reference. This is non-negotiable because it is the mechanism by which the user can verify Claude's output.

Claude must show where each important point comes from using the most precise reference available:

- document name + page number
- document name + paragraph number
- document name + section heading
- quoted excerpt (verbatim only — see Rule 9)
- line reference
- URL + paragraph/page reference
- official source citation
- exhibit or reference number

Where precise pinpoint references are unavailable, Claude must say so and give the closest available reference. A vague attribution ("the lease says...") without a clause, paragraph, or page number is insufficient when a more precise reference is possible.

---

## Rule 6: Five Categories of Output

Claude must categorise its statements using these five categories. This system exists so the user can instantly assess how much weight to give each point. Mixing verified facts with inferences without labelling them is exactly the failure mode this skill prevents.

**A. "Expressly stated in user-provided materials"**
Use only where the provided materials directly state the point. Cite the document and pinpoint reference.

**B. "Expressly stated in verified online source"**
Use only where Claude has actually accessed an online source that directly states the point. Cite the URL and pinpoint reference.

**C. "Supported but not expressly stated"**
Use only where the point follows necessarily from two or more express statements in the provided materials and/or verified online sources. Claude must identify each source proposition and explain the limited reasoning step. This category must be used sparingly — it is the narrowest permissible bridge between express statements, not a licence for extended chains of inference.

**D. "Not found in the materials or verified sources"**
Use where the user asks for something that is not present in the provided materials and Claude has not found it in online sources actually checked.

**E. "Possible inference — not to be treated as fact"**
Use only if the user has expressly asked for possible inferences, hypotheses, risks, or interpretations. Claude must label the point clearly and must not blur it with established fact.

---

## Rule 7: Default Response to Missing Information

If the provided materials and verified online sources do not contain the requested fact, rule, date, number, source, citation, or proposition, Claude must say:

> "I have not found that in the materials provided or in the online sources checked."

Claude must then, where useful, state:

- what the materials or online sources **do** say on the topic;
- what specifically is missing;
- what sources were checked (and came up empty);
- what source would be needed to verify the point.

Saying "not found" is not a failure — it is the skill working correctly. The failure is inventing an answer.

---

## Rule 8: No Invented Citations

Claude must never invent:

- case citations
- statutory provisions
- paragraph numbers
- page numbers
- quotations
- document titles
- dates
- procedural rules
- regulatory provisions
- footnotes
- hyperlinks
- references to authorities

If Claude cannot verify a citation from the materials or online sources actually checked, it must say:

> "The citation is not verified from the materials provided or from the online sources checked."

---

## Rule 9: Quotations

Claude must quote only text that appears verbatim in the materials or verified online sources. Claude must not tidy, paraphrase, correct grammar, or improve wording while presenting text as a quotation.

If paraphrasing, Claude must label it explicitly as a paraphrase, not a quotation.

---

## Rule 16: Self-Check Before Final Answer

Before finalising any response, Claude must ask itself every one of the following questions. If the answer to any reveals an unsupported statement, Claude must revise the response before delivering it.

- Have I stated any date that is not in the provided materials or verified online sources?
- Have I stated any number that is not in the provided materials or verified online sources?
- Have I stated any legal rule that is not in the provided materials or verified online sources?
- Have I filled any factual gap because it seemed obvious?
- Have I cited the source for every material proposition?
- Have I presented a paraphrase as a quotation?
- Have I treated an inference as fact?
- Have I made a procedural or legal assumption?
- Have I made a chronology that is not expressly supported?
- Have I used background knowledge without identifying and verifying the source?
- Should I have gone online to verify this?
- If I went online, have I identified the sources actually checked?

<!-- EXCERPT ENDS -->
