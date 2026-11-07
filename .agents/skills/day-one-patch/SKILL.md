---
name: day-one-patch
description: Day-one launch patch — focused fix for known issues found after gold
  master. Mini-sprint with QA gate and rollback.
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
