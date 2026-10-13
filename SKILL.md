---
name: large-task
metadata:
  author: Wouter van den Berg <wouter@monteclima.com>
  linkedin: https://www.linkedin.com/in/wjvandenberg/
  license: MIT, except references/source-check.md, which is AGPL-3.0 - see LICENSE.md
description: Runs a piece of work to a plan — sized with the user, planned together, a handoff written at every break between sessions, and picked up again when the user types continue, in any language. Use it of your own accord whenever the work plainly spans several sessions, and whenever the user asks for it, a one-session task included — by this name or by its name in their own language, such as grote taak (Dutch), grande tâche (French) or grande compito (Italian). In Claude Code, only when the user names it.
---

# large-task — a piece of work run to a plan, in one session or several

## Before anything else

- **In Claude Code, stand down unless the user named this skill.** It is installed on the account, so it
  loads there too, where another method governs: say so in one line and stop.
- **This is for one piece of work** — its own objective, files and deliverable — with or without a Cowork
  project, in a folder unless it fits in one session *(Files, not chat)*. Setting a project up is a
  different job.
- **The rules below live here and nowhere else.** Nothing has to be pasted for them to bind while this skill
  runs, and no other chat carries them.
- **Work in the user's language** — the one they write in. Every question, chat line and file — the plan,
  the research file, a handoff, the closeout, a start prompt — is in it, the templates' headings translated.
  **File names and the `(verify)` tag stay as the templates give them**, so a later session finds them in
  any language. The user's word for *continue* — `verder`, `continuer`, `continua` — is `continue`.
- **In a task's first session, offer ONE optional line for the account-wide instructions** — unless they
  already name this skill — and carry on whether or not it is pasted. With many skills installed, a skill's
  description can reach the model as a bare name, and this line is then what starts the skill. **Offer it
  for someone who has never changed a setting:** one plain sentence on what it is for — *so that in a new
  chat I recognise this kind of work, or this skill's name, without you explaining it again* — then the line
  alone in a fence, then where it goes: *Settings → Account → Instructions for Claude*, pasted at the end of
  what is there, then saved. Say that skipping it is fine. **In another language, translate the line**,
  keeping the skill's exact name in it and its name in that language beside it — in Dutch, the second:

  ```text
  Use the large-task skill for work that spans several sessions, and whenever I ask for it — a one-session task included.
  ```

  ```text
  Gebruik de skill large-task (grote taak) voor werk dat meerdere sessies beslaat, en wanneer ik erom vraag — ook voor een taak van één sessie.
  ```

- **Write nothing beside this skill, and no instructions or memory file into the chat's container** — both
  are gone in the next chat. The work's folder is the only store, and no instructions file in it is relied
  on either.

## The standing rules — they bind for as long as this skill runs

### Files, not chat

- **Every analysis, finding, decision and handoff is written to a file in the work's folder.** What exists
  only in the transcript does not exist: the next session cannot read it.
- **Keep the chat clean, the whole session through.** It carries only your questions, a one-line note of
  progress, and a short close: the headline result and direct answers to what the user asked — at a break,
  the start prompt too. **Never in the chat:** analysis, verification or source-check results, check output,
  corrections, sources, assumptions, open points, file lists or paths, technical detail. They go in the files.
- **Ask for folder access as soon as the work's folder is known**, before any work in it — never when the
  first write fails. **If a folder cannot be linked** — a mapped network drive can fail — ask the user to
  copy its files into a local folder.
- **A one-session task can run without a folder.** With none linked, linking one is one of your questions
  — recommended, because the files stay together and a later session can pick them up. Without one, the
  chat's own working space is the work's folder, every rule here applies to it, and at the close the
  deliverable is attached for the user to save where they like — the plan and research file too, if they
  ask. **If the task then proves bigger than one session, stop at a natural break and ask for a folder:**
  copy the plan and research file into it, then write the handoff there — never in the chat's own space,
  which the next chat cannot see.
- **One folder per piece of work, flat:** files named by what they contain, no dated subfolders.
- **Never delete. A superseded version MOVES into an `OLD` subfolder** — and where the folder cannot be
  reached to move it, write the copy into `OLD` and tell the user which original to remove.
- **Every deliverable is ATTACHED in the chat as well as written to the folder** — never to the chat alone.
- **After writing a file to the folder, read it back and compare its hash before relying on it** — a write
  just after an overwrite can land the previous version. **On a mismatch, write it again by another route
  and compare again**, and rely on it only once it matches. **Record a file's hash only after its last edit.**
- **The closeout or handoff states the full path of every file the session wrote** — never the chat.

### Facts and progress

- **No fabrication.** Every figure and claim carries its source and the date it was accessed, in the research
  file. Anything single-sourced or uncertain is tagged **`(verify)`**. Never present an estimate as a fact, and
  never fill a gap by inference — **a flagged gap beats a guess.**
- **Sources stay in the research file** — the documents, websites and the like the work drew on. The
  deliverable — a document, a table, a spreadsheet — names none, and neither does the chat, unless the user
  asks. **A reference INTO the document the work is about** — a clause, a section, a page — **is content,
  and stays.**
- **Never report a step complete that is not.** Say exactly what was not reached, and why.
- **A step is complete only when its done-when line is met by a check that ran** — each step on its own,
  never a batch marked done at the end.
- **Where the host shows a progress list, it is state, not narration:** one task per block of the plan, in
  its order — rebuilt, never renamed, when the plan or the order of the work changes. **Each block ends at a
  gate:** run its check; in ONE message close its task and open the next; read the list back in a separate
  call; log the gate in the research file's step log, timed by `date`. A task still open at the close is
  unfinished work to state; two closed in one message are reported in the closeout, the rule marked not met.
- **Lock the criteria before collecting.** Criteria, weights, scoring rules and inclusion tests are written
  down before data collection starts. **A change after the user has seen the result is an explicit
  amendment:** a new version, a stated reason and the user's sign-off, recorded in the file — and the whole
  result recomputed, never re-scored by feel.
- **In a review, reading the source IS the collecting:** write the selection test before reading past its
  headings or table of contents.

### Verification

- **Verification is a step you RUN, not a claim you make:** write the check, run it, and paste its real
  output.
- **Paste that output WHOLE — never condensed — into the file that reports the result, and never into the
  chat** — a closeout that points at the transcript for it points at nothing the next session can read.
- **A consistency check between two things built from the same source is not a correctness check** — both
  can be wrong in the same way, and agree.
- **Before trusting what a check reports, prove it is looking at the data.** A check that read one file of
  several reports coverage it never had.
- **Every deliverable is verified against its PURPOSE first:** the plan's locked criteria, each one
  checked, and the result pasted into the file.
- **Then every row of the plan's `D` table, for EACH thing it applies to** — each document, each source —
  marked done, partly or not done, with the check that showed it. A self-assessment is not a check.
- **Coverage is shown, never asserted:** the plan lists every unit the work must cover — each document,
  section or clause, each source, each item the brief names — and the research file's coverage register
  marks each one as it is reached. A coverage check runs before delivery, its output in the file; a unit not
  reached is reported, never passed over.
- **A checker script runs whenever the final deliverable is a Word, Excel or PowerPoint file** — on that
  deliverable, the container copy whose read-back hash matches the delivered file. It is a light check of
  what "it opens" misses, never of whether the content is right:
  `python3 -B <this skill's folder>/scripts/check_docx.py FILE` — or `check_xlsx.py`, `check_pptx.py`.
- **On a final Excel or Word file, `check_form.py` runs too, with the agreed size:** `python3 -B <this
  skill's folder>/scripts/check_form.py FILE [--max-tabs N] [--max-columns N] [--max-words N]` — it fails a
  total typed in where a formula belongs, and anything over the size; with no flags, the small default.
- **Run a checker; never import one** — an import writes a cache file beside the skill.
- **Tracked changes and comments FAIL unless declared:** add `--allow tracked-changes` or
  `--allow comments` — Word takes both, PowerPoint comments only — only when the plan says the
  deliverable IS a markup; the report then shows the allowance.
- **Paste the report whole, into the file.** A NOT CHECKED line is a gap to state, never a pass; exit 2
  means the file could not be read, so nothing was checked.
- **A review or analysis gets the source check** in `references/source-check.md`: each finding with its
  source, pinpoint and label, and a self-check before delivery that lists what it changed, in the files.

### How the work is run

- **Work sequentially.** No subagents, parallel agents or workflows unless the user explicitly asks — run
  every step yourself, in order.
- **Read a large source by section, never whole** — read whole, it can use up the session before the work
  starts.
- **Assert every text replacement, then read the file back** — a patch whose search matched nothing still
  reports success.
- **When nobody is there to answer** — a scheduled run, or the user has gone — **do not block on a
  question:** take the most reasonable reading, state the assumption at the top of the output, and carry on.

## Size it, with the user

- **One session is the default, and more is the exception.** Propose more only when it is CLEAR: the
  sources together pass **450,000 characters** — about 73,000 words, or 145 pages — or the plan runs to **60
  steps or more**, or the user asks. **Measure the sources, never guess:** characters, words or pages, by
  the shell. On a model with a 200K-token window, a fifth of that.
- **Say at the start when the number comes:** *"I will tell you how many sessions I think this takes once
  the questions are answered and the plan is made"* — then propose it, after the plan.
- **Propose it in plain words, as your estimate** — *"I estimate this fits in one session"*, or *"… is too
  large for one session; I propose three"* — **never with the measurements or the lines behind it.** The
  characters, the steps and the thresholds go in the plan file.
- **One session:** the ONE-SESSION MODE — a short plan file and the deliverable, no handoff, and a folder
  only if the user links one.
- **Several sessions:** plan, research — in stages where the sources are large — build and verify, with a
  handoff at every break. There is no cap.
- **A plan at every size; a handoff only across a break between sessions; a separate context file only when
  the plan cannot hold it.**
- **The plan stays within 300 lines, a handoff within 150** — both are read whole at every session's start.
  Count them by the shell. Over the cap, move context and method detail into `CONTEXT.md`; never drop or
  shorten a row of the instructions table to make it fit.
- **If a one-session task proves bigger once its sources are read** — what has been read passes the line —
  write a handoff at that point — in a folder, asked for first if none is linked — and tell the user. That
  is the exception, never the plan.

## Get the context before proposing anything

1. Read the brief in full, including whatever it points at.
2. Read the work's folder, `OLD` included, to find what already exists.
3. Open any existing deliverable or data file yourself — never take a document's word for what it holds.
4. Check memory, a Cowork project's docs if there is one, and earlier files in the folder for decisions
   already taken.
5. Check NOW that every tool the plan will depend on works in this session.
6. Re-derive every number you will plan against — counts in handoffs and prompts go stale.
7. Ask your questions — below.
8. Write the context down: the plan's context section, or a context file.

## Ask before planning

- **First, name the load-bearing assumption** — the one that, if false, makes the whole result wrong rather
  than merely different — **and make it the first question.** The questions cover what the answer rests on,
  not only its shape.
- **Scan the brief for hedges before asking** — *e.g.*, *for example*, *probably*, *around*, *roughly*,
  *say*, *something like*, a range. Every figure a hedge touches is a question, never a default; ask about
  figures of the same kind together.
- **Ask 7 to 10 multiple-choice questions before any plan, at every size** — a one-session task included —
  covering **the context, what the work is FOR, the FORM of the deliverable** *(its structure, layout,
  length, tables, references)* **and the criteria it will be judged by.** **At least 5 when the brief already
  settles most of it:** ask each settled point back as a check — *"I read the purpose as X; is that
  right?"* — and it counts. Every other question is one the brief, the files and a sensible default cannot
  settle, and whose answer changes what happens next.
- **With no folder linked, one of them is whether to link one**, the folder recommended *(Files, not chat)*.
- **One of them is always how elaborate the output should be:** ***Short*** — about half of what you would
  normally write for each item, the recommended default · *Normal* — about two-thirds · *Full* — your usual
  length.
- **When the deliverable is an Excel, Word or PowerPoint file, one of them describes its set-up in words** —
  the main tab or the main pages only, never the reference or background tabs: for Excel what its rows and
  its columns are, for Word its headings and each table's columns. Start from the small default in *Keep the
  output simple*, keep the question short, and never make a file for the user to look at first.
- **Every option carries its honest cost, and the recommended one says so in its label.** Never ask what you
  can measure.
- **When an answer changes what the work is FOR** — someone else will rely on it, or the standard rises —
  restate the scope and ask again before planning.

## Plan together

- **Plan WITH the user:** they do not hand over a plan, and you do not present a finished one.
- **Put the genuine forks, each with its honest cost** — the recommended one included.
- **How many sessions, and where they split, is the user's call** — proposed after the plan, by the rule in
  *Size it*.
- **Write the plan from `references/plan.md`, around ONE table, `D1…Dn`: every explicit instruction and
  every decision, each in the user's own words** — from the brief, an answer or a later message, with what it
  applies to. An instruction given mid-work goes in at once. Everything after the table cites its numbers.
- **Each row of that table carries its firmness:** *instruction* · *decision* · *illustration* — a hedged
  word, or a figure offered to show the shape of an answer — · *assumption* — nobody said it, you proposed
  it. **An illustration or an assumption is never an input until the user has confirmed it.**
- **One source of truth per kind of file:** the plan governs, the research file holds every finding, and the
  deliverable is built strictly from the research file.
- **When a decision turns out to rest on a wrong number:** re-derive it, say so, and restate the scope before
  acting.

## Keep the output simple

- **Simple is what the USER means, and the purpose decides what stays.** First decide the simplest way to
  show what the work is for — what the user must see to answer the question — then build that and nothing
  more. A tab, table, row, column or section the agreed set-up does not name needs a reason the user gave.
- **The default is small:** in Excel one tab that answers the question — and as many input tabs as the work
  needs, which are never limited; a table at most 6 columns in Excel and 4 in Word; a cell holds a figure, a
  date or a short phrase — about 8 words, 12 in a Word table. An explanation goes on a line under the table,
  or in the research file.
- **In Excel every total and derived figure is a live formula** — `SUM` and the rest — over the cells it
  comes from, and every input sits in a marked cell the user can change. Never a typed-in result.
- **Never call the output simple — describe it, in amounts AND in content:** *"1 tab, one row per year;
  columns year, income, costs, balance"*.
- **When the user says it is too complicated, start again from the smallest set-up** — cut everything they
  did not ask for, not only the part they named — and describe the new set-up before rebuilding.

## Run each session

- **One coherent workstream per session** — never a discovery sweep and a build together.
- **One research file per task, started from `references/research.md`** and added to every session — never
  a new file per session.
- **The research file is long-form and uncapped, and ORGANISED BY TOPIC** — one clear section per unit or
  question, each finding filed under its section, never appended in the order it was found. **Tidy it once
  the research is done, and whenever it is edited.** A later session reads it by section, the handoff naming
  which.
- **Before any build, check its inputs against the table's firmness:** an input resting on an unconfirmed
  illustration or assumption is a question to ask, never a figure to build on. The check goes in the
  research file.
- **The final session builds strictly from the research file**, then verifies with a check it actually runs.
- **A session that went wrong is QUARANTINED** — moved aside with a note saying who set it aside, when and
  why — never deleted, never built on. Figures the user approved that came from it are re-derived and put to
  the user again.

## The handoff — at the end of every session but the last

- **This skill writes the handoff itself**, from `references/handoff.md`, in four parts:
  1. **the state after this session** — what was done, what each file is, the instructions and decisions a
     line each;
  2. **what is open** — every `(verify)`, every block not reached, every risk carried;
  3. **the full instructions for the next session** — numbered steps, its reading list, the rules restated,
     and how its chat is to open;
  4. **a start prompt in a fence**, opening with the chat's title, `<task name> — session <n>`, and doing
     nothing but name this skill and point at the handoff — named, it starts even where the optional line
     was never pasted. That short form is the default; a self-contained prompt is a signed-off deviation.
- **Copy the start prompt verbatim into the plan's START PROMPTS section**, one sub-section per session.
- **The handoff is the source of truth**, the plan's copy a convenience, and the chat copy is generated from
  the file — never retype a prompt into any of the three.
- **Hand the next prompt over verbatim in the closing message, in its own fence, ready to copy**, as the
  handoff template says — never tell the user where to find it.

## `continue` — picking the work up again

- **No folder linked? Request access through the folder-access tool**, naming the folder — or its parent,
  to search it for the handoff. **If that is refused, ask the user to link the folder with the app's
  Add-folder button.**
- **Find the newest handoff in the folder**, by name order and modification time. With several series open,
  the newest wins. The chain of handoffs is the work's memory; nothing else is needed.
- **Only then state your first line: the chat's title, `<task name> — session <n>`**, the number taken from
  the handoff. **In a first session the title is `<task name>` alone**, as soon as the task has a name — with
  a session number only once more than one session is planned, or the user has said so.
- **`continue` is always a valid opening**, the start prompt's equal. **If this chat opened any other way
  than the handoff said it would** — another task, another series — **say so and ask** before going on.

## The last session

- **It has no start prompt; it ends with a closeout FILE** — what was produced, the headline result, every
  open `(verify)`, and the full path of every file.
- **In the chat, only the short close:** the headline result and direct answers to what the user asked, with
  the deliverables attached. The closeout and every other output go to the folder.
