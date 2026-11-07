---
name: dev-story
description: Implements one story in code with tests, following its ADRs. Use when
  the user says to build, implement or start working on a story. Not for checking
  readiness beforehand or closing the story after.
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
