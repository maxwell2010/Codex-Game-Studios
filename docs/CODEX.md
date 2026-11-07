# Codex runtime bridge

## Installation

Clone this whole repository and open its root in Codex. Trust the project only
after reviewing its instructions. Repository skills use `.agents/skills` and
custom agents use `.codex/agents/*.toml`. Restart the session after adding them.
Invoke `$start`, `$help`, `$setup-engine` or another skill by name. If a client
does not discover local skills, ask it to read the relevant `SKILL.md` explicitly.
Do not copy only `.agents`: workflows depend on shared `.claude`, design, docs,
production and `project.yaml` assets. No global Codex settings are modified.

## Runtime differences

| Upstream | Codex adapter |
| --- | --- |
| CLAUDE.md and @ imports | AGENTS.md and explicit file reads |
| /workflow | $workflow |
| skill model and allowed-tools metadata | Removed; session model and permissions apply |
| Agent and Team tools | Native custom agents where supported; sequential roles otherwise |
| AskUserQuestion | Available question tool or a concise chat question |
| TaskCreate/TaskUpdate | Available plan/task tools or a local task plan |
| ! shell injection | Explicit shell step, reviewed before execution |
| settings.json hooks, deny lists and status line | Preserved for Claude only; not installed in Codex |
| Path-scoped rules | Read matching .claude/rules files manually |

Run commands from the repository root. Shell helpers require Bash, awk, sed,
grep and other Unix utilities; install Git Bash on Windows or use WSL with the
repository accessible inside it. Some helpers additionally need engine binaries
or Python; inspect the helper and its help before use. Never fabricate engine
test evidence when the engine is missing. Shared scripts may still mention
CLAUDE.md because the original Claude interface remains supported. Engine setup
updates AGENTS.md in the adapted workflow; check consistency with project.yaml.

Follow the current user's authorization rather than repeatedly asking approval
for the same requested edit. Project modes still govern unresolved design
decisions. Nothing here grants permission to message others or publish a game.

## Regeneration and validation

Install `tools/requirements.txt`, run `python tools/build_codex.py`, then
`python -m unittest discover -s tests -v`. The adapter is generated from the
preserved upstream definitions. It strips Claude-only frontmatter, expands
injection syntax to explicit commands and converts known skill invocations.
It does not translate arbitrary Claude APIs embedded in prose into runnable APIs.
Read those as workflow intent through the capability mapping above.

Each generated skill keeps `workflow.md` beside `SKILL.md`, with the original
supporting `references/` tree alongside it. All supporting Markdown is adapted,
not just the entrypoint. Relative resource paths are based on the skill folder.
Python maintenance tools require 3.12 or newer. Generator inputs and outputs must
be regular repository files, without symlinks or Windows junctions.

Automated checks validate packaging, TOML, workflow coverage, referenced local
paths and deterministic regeneration. They do not establish successful gameplay
or full interactive execution of every workflow on every Codex client.

One minimal Godot lifecycle now has actual engine, rendered-state and extracted
source-package evidence: [validation report](validation/cycle-2026-11-07.md).
See also the [security review](validation/security-2026-11-07.md). These results
do not establish automatic skill discovery or all native roles on every client.

Official references (consulted 2026-11-07):
- [Skills](https://learn.chatgpt.com/docs/build-skills)
- [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
