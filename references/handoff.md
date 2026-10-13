# HANDOFF-<nn> — <task name>, session <n> → session <n+1>

<The task in one line.> Session <n> closed <date>. Steps done: <…>.

## 1 — State after session <n>

### What session <n> did

### The files, and what each one is

### The instructions and decisions, one line each

## 2 — What is open

### Every `(verify)`

### Every block not reached

### Every risk carried into session <n+1>

## 3 — Instructions for session <n+1>

1. Open the chat by <`continue` | pasting the start prompt below>; link the folder; read `PLAN.md`, then
   this file, then only the sections this list names — the research file's by their headings.
2. <… numbered, complete, needing nothing but this file.>

**The rules, restated:** <the task's own guardrails>.

## 4 — Start prompt for session <n+1>

- Hand it over near the TOP of the closing message, before the summary, in its own fence with nothing else
  inside.
- Use a four-backtick fence when the prompt itself contains backticks.
- The chat copy is generated from this file, never retyped; where the two differ, this file wins.
- Asked for the prompt again, hand it over alone, with no preamble.
- Write it in the user's language, the skill's name `large-task` and the file name kept exact.

```text
<task name> — session <n+1>: with the large-task skill, link the folder, read HANDOFF-<nn>.md, and do exactly what its section 3 says.
```
