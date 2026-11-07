---
name: start
description: Guides a first-time user through onboarding and picks the right workflow.
  Use when the user is new, just cloned or installed the studio, has no idea or engine
  yet, asks where to begin, or wants to bring in an existing game.
---

## Codex execution bridge

Read `docs/CODEX.md` before executing this workflow. Use the repository root as
the working directory. The explicit user request and existing authorization
take precedence over repeated approval prompts in inherited workflows.
Claude tool names below describe capabilities: use available Codex file,
search, shell, browser and question tools. Never claim an unavailable tool ran.
Use native subagents only when available and authorized; otherwise perform the
roles sequentially and label that fallback. Track tasks in a local plan when
TaskCreate/TaskUpdate are unavailable. Hooks are not automatically enforced.
The `.claude` paths are intentionally preserved shared assets, not Codex config.

Follow [the studio workflow](references/workflow.md) for this skill.
