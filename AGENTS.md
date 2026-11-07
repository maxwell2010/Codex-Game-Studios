# Codex Game Studios

This repository adapts Donchitos/Claude-Code-Game-Studios for Codex.
Read `docs/CODEX.md` for the runtime bridge and known limitations.

## Work on a game

- Read `project.yaml` and, if present, `production/session-state/active.md`.
- Use `$start` for onboarding and `$help` to choose a workflow.
- Skills live in `.agents/skills`; native role definitions in `.codex/agents`.
- Read `.claude/docs/coding-standards.md` and relevant rules in `.claude/rules`
  before editing game files. Match each rule's `paths` globs to affected files;
  these are manual instructions, not automatically loaded Codex rules.
- Read `.claude/docs/coordination-rules.md` for studio responsibilities, using
  the Codex bridge instead of its Claude-specific runtime/model assumptions.
- Keep engine, version, platform and game parameters in `project.yaml`.
- Preserve separation of gameplay, UI, engine integration, data and assets.
- Verify changed behavior with the selected engine and report what actually ran.

## Authorization and runtime

Follow the user's scope and existing authorization. Ask about material missing
design choices; do not ask again before each reversible edit already requested.
Commit, publish and communicate externally only within explicit authorization.
Do not weaken sandbox or approval settings. Never assume Claude hooks, deny
lists, model tiers, `@` imports or dynamic prompt injection execute in Codex.
If subagents are unavailable, perform studio roles sequentially and say so.
Use the user's configured model; Opus/Sonnet/Haiku are upstream metadata only.

## Maintaining this adapter

Preserve upstream `.claude` assets and LICENSE. Change `tools/build_codex.py`
to update generated files, then run:

```sh
python -m pip install -r tools/requirements.txt
python tools/build_codex.py
python -m unittest discover -s tests -v
```
