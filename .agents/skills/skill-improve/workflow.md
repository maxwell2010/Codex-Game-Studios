# Improve a Codex studio workflow

Requires one existing skill name. Missing or unknown name: show usage and stop.
Resolve `.agents/skills/NAME`, its catalogued behavioral spec and the generation
source before editing. Changes are limited to the requested skill and needed
regressions; do not install a global skill or change session permissions.

## 1. Establish a baseline

Run `$skill-test static NAME`, then review the applicable spec and category.
Record concrete failures and unknowns. No readable definition or spec: report
NOT ASSESSED; do not invent a baseline score. A clean structural result alone
does not mean no behavioral improvements are possible.

## 2. Fix the maintained source

Generated files are not the source of truth. For existing shared behavior edit
the relevant `.claude/skills/NAME` file, preserving Claude compatibility. For a
Codex-specific workflow use `tools/codex_workflows/NAME.md`; for a systematic
conversion defect change `tools/build_codex.py`. Do not edit only the generated
workflow, because regeneration would discard the fix. Respect the user's
authorization for edits and material design decisions.

Run `python tools/build_codex.py`, then `$skill-test static NAME` and
`python -m unittest discover -s tests -v`. Re-read the spec to ensure a clearer
instruction did not remove a gate, relax evidence requirements or broaden scope.

## 3. Verify behavior and hand off

If a real scenario was authorized, replay it in an isolated copy and retain the
before/after evidence. If it requires unavailable tools, report that limitation;
do not turn a structural pass into a behavioral pass. On regression offer a
targeted correction or rollback of only this changeset; never reset unrelated
work. Stop after three unsuccessful repair attempts and report the unresolved
issue instead of looping indefinitely.

Report the defect, changes, validation and remaining limitations. Preserve
historical test timestamps unless an actual corresponding check ran. Commit or
publish only within explicit user authorization. Next: `$skill-test spec NAME`
or the isolated scenario needed to establish the claimed improvement.
