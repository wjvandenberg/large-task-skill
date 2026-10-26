# large-task - a general AI skill for bigger tasks

**large-task** is a general AI skill for bigger tasks, such as a contract review, a research memo or exporting
a large set of data into an Excel file. I wrote and tested it in Claude Cowork, but it will probably also work
in other AI tools such as ChatGPT and Gemini. It is not only for legal work, and it works in any language:
write in Dutch, French, Italian or anything else, and everything comes back in that language.

## Why I built it

An AI model like Claude can only keep so much context in mind in one session. On a bigger task it starts to
lose track of what you agreed, fills gaps with something that merely sounds right, or simply runs out of room
before the work is done.

large-task works around that by giving the task a **written memory**, much like a well-kept file you would
hand over to a colleague. The plan, what you agreed and every finding go into files in a folder, and the AI
re-reads them at the start of every session. So it works from the file rather than from what it happens to
remember, and a task can run over as many sessions as it needs.

## What it does

- **Asks first.** It starts with seven to ten multiple-choice questions, so it has all the relevant context
  and the result fits what you actually need.
- **Makes a plan, and saves it.** It tells you whether the task fits in one session or needs extra sessions -
  and if it needs more, it says so up front and plans for them.
- **Works lean.** It reads long documents section by section and works through the plan one block at a time,
  to make the most of the room the AI has in a session.
- **Avoids made-up answers.** Every figure and finding is tied to the source it came from, and anything it
  cannot back up is marked `(verify)` rather than guessed. Before it hands over a review or an analysis, it
  checks each point against the sources it used, and only those. An Excel, Word or PowerPoint result also gets
  an automatic check of the file itself.
- **Carries on over extra sessions.** Each session ends with a hand-off note in your folder and a short prompt
  for the next one, which starts by reading the note and the plan.

## How to use it

In Claude Cowork, write "Use the large-task skill to..." plus your task:

> Use the large-task skill to review these three supplier contracts on price, liability and termination.

It also answers to its name in your language: **grote taak** (Dutch), **grande tâche** (French), **grande
compito** (Italian).

**To carry on in a new session,** type `continue` - or `verder`, `continuer`, `continua` - or use the prompt
the previous session gave you.

A task that runs over extra sessions needs a folder on your computer, linked to the chat, so the next session
can find the plan and the notes. The skill asks for one. A task that fits in one session can do without.

## Install it

In Claude:

1. **Download** `large-task.zip` from the [latest release](../../releases/latest). Don't unzip it.
2. **Upload it in Claude:** open Claude's settings for skills and upload the zip.
3. **Optional:** the first time you use it, the skill offers one line to paste into
   **Settings → Account → Instructions for Claude**. With it, Claude picks up the skill in a new session without
   being told. Skipping it is fine.

In Claude Code the skill only runs when you name it. In ChatGPT, Gemini or another AI tool, add it the way that
tool takes skills or custom instructions.

Hopefully this will be useful for many of you - for me it definitely is. If you run into any issues, or have
feedback or questions, open an issue here.

## Licence

The whole skill is licensed under the GNU Affero General Public License, version 3 (AGPL-3.0). See
[LICENSE.md](LICENSE.md).
