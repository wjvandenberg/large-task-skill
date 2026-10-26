# large-task — a Claude skill for bigger jobs

**large-task** is a skill for Claude Cowork, Claude's desktop app, for jobs too big for a quick answer:
a contract review, a research memo, or turning a large set of data into an Excel file. It works in any
language — write in Dutch, French, Italian or anything else, and everything comes back in that language.

## What it does

- **Asks first.** It opens with seven to ten multiple-choice questions about what the work is for and what
  the result should look like, so it has the context it needs and the result fits what you actually need.
- **Makes a plan, and saves it.** Before the real work starts it writes a plan to a file, and tells you
  whether the job fits in one chat or needs more.
- **Works lean.** It reads long documents section by section rather than all at once, and works through the
  plan one block at a time, so Claude's working memory goes on the work itself.
- **Avoids made-up answers.** Every figure and finding is tied to the source it came from, and anything it
  cannot back up is marked `(verify)` rather than guessed. Before it hands over a review or an analysis, it
  checks each point against the sources it used, and only those. An Excel, Word or PowerPoint result also
  gets an automatic check of the file itself.
- **Carries on across chats.** If a job needs more than one chat, each chat ends with a hand-off note in
  your folder and a short prompt for the next one.

## How to use it

In Cowork, start a chat and write *"Use the large-task skill to…"* followed by the task:

> Use the large-task skill to review these three supplier contracts on price, liability and termination.

It also answers to its name in your language: **grote taak** (Dutch), **grande tâche** (French),
**grande compito** (Italian).

**To carry on in a new chat,** type `continue` — or `verder`, `continuer`, `continua` — or paste the prompt
the previous chat gave you.

A job that runs over several chats needs a folder on your computer, linked to the chat, so the next chat can
find the plan and the notes. The skill asks for one. A job that fits in one chat can do without.

## Install it

1. **Download** `large-task.zip` from the [latest release](../../releases/latest). Don't unzip it.
2. **Upload it in Claude:** open Claude's settings for skills and upload the zip.
3. **Optional:** the first time you use it, the skill offers one line to paste into
   **Settings → Account → Instructions for Claude**. With it, Claude picks the skill up in a new chat without
   being told. Skipping it is fine.

In Claude Code the skill runs only when you name it.

## Licence

MIT, except `references/source-check.md`, which is AGPL-3.0. See [LICENSE.md](LICENSE.md).
