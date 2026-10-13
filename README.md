# large-task — a Claude skill for work that needs a plan

**large-task** helps Claude carry a piece of work through from start to finish: a report, a review, a
comparison, a piece of research. It works whether the job takes one chat or several. Claude asks its
questions first, makes a plan with you, keeps its findings in files rather than in the chat, and when the
work runs over several chats, leaves a note so the next chat can pick up exactly where this one stopped.

It works in any language. Write to Claude in Dutch, French, Italian or anything else, and the questions,
the plan and the files come back in that language.

## What it does for you

- **Asks before it starts.** About seven to ten multiple-choice questions on what the work is for, what the
  result should look like and how it will be judged, so you don't get a long answer to the wrong question.
- **Plans with you.** It writes the plan down and tells you whether the job fits in one chat or needs more.
- **Keeps the work in files.** The plan, the research and the result go into files. Nothing important lives
  only in the chat.
- **Checks its own work.** It runs real checks before calling anything done, and marks anything uncertain as
  `(verify)` instead of guessing.
- **Picks up where it left off.** At the end of a chat it hands you a short prompt for the next one. Type
  `continue` (or `verder`, `continuer`, `continua`) and it carries on.

## Install it

1. **Download** `large-task.zip` from the [latest release](../../releases/latest). Don't unzip it.
2. **Upload it in Claude:** open Claude's settings for skills and upload the zip.
3. **Optional, but it helps:** the first time you use it, the skill offers you one line to paste into
   **Settings → Account → Instructions for Claude**, in your own language. With it, Claude recognises this
   kind of work in a new chat without being told. Skipping it is fine.

## Use it

Start a chat and name the skill, then describe the work:

> Use large-task: compare these three supplier contracts on price, liability and termination.

It also answers to its name in your language, such as **grote taak** (Dutch), **grande tâche** (French) or
**grande compito** (Italian).

- **A job that fits in one chat** needs no folder. Claude works in the chat and gives you the result at the
  end, to save wherever you like.
- **A bigger job** needs a folder on your computer, linked to the chat, so the next chat can find the plan
  and the notes. The skill asks for it, and recommends one in any case.

It is made for Claude's desktop app (Cowork). In Claude Code it runs only when you name it.

## Licence

MIT, except `references/source-check.md`, which is AGPL-3.0. See [LICENSE.md](LICENSE.md).
