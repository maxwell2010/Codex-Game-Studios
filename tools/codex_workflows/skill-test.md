# Test the Codex studio definitions

Modes: `$skill-test static [name|all]`, `spec [name]`, `category [name|all]`,
or `audit` (default). A name such as `help` is a skill name, not a usage request.
Reject unknown modes or names with usage and no writes. Resolve names in
`studio-tests/catalog.yaml`, then the native `.agents/skills` and `.codex/agents`
files. Do not substitute the upstream Claude version for a native definition.

## 1. Native structural audit

Run `python tools/audit_codex.py` for the complete registry, or add `--name NAME`
for one skill or agent. It checks native YAML/TOML, resource parity, references,
catalog/spec coverage and known runtime-compatibility defects. It does not run
skills or infer their correctness from their descriptions. Missing/unreadable
inputs are NOT ASSESSED with a nonzero process exit, never a clean result.

Read SKILL.md, workflow.md and relevant supporting Markdown together when
reviewing a skill. A Codex skill requires name and description, not Claude's
allowed-tools, model, context: fork, argument-hint or user-invocable fields.
Native agent definitions are TOML with name, description and
developer_instructions; model settings inherit unless explicitly configured.
The upstream skill-lint, agent-check and compat-inventory shell scripts describe
Claude files only; do not present their observations as tests of native Codex.

## 2. Spec and category review

For `spec`, read the native definition and its catalogued spec fully. Preserve
behavioral invariants in the spec: unknown inputs cannot pass a gate, FAIL must
not be overridden, missing evidence is not success, external deployment needs
authorization, and unplayed prototypes cannot claim PROCEED.

Upstream assertions about Claude-specific frontmatter, model aliases, tool names,
@ imports or automatic hooks are NOT APPLICABLE to the native Codex format;
explain the mapped Codex capability instead. All other assertions still apply.
For each case report SUPPORTED, CONTRADICTED or NOT ASSESSED with native file
evidence. This is an instruction review, not observed model behavior. A failed
structural check outranks an unknown, and any unevaluated applicable assertion
prevents an all-clear. Do not change historical last_spec_result timestamps to
claim a scenario actually ran when only its instructions were read.

For `category`, use the catalog's category and the matching section of
`studio-tests/quality-rubric.md`; apply the same distinction between semantics
and Claude-specific mechanics. Missing category/rubric: NOT ASSESSED with reason.

## 3. Evidence and handoff

For `audit`, show every skill and role, structural results and spec case counts;
keep helper replays, instruction review and real engine runs in separate columns.
Run `python -m unittest discover -s tests -v` when checking regressions. A helper
fixture passing does not establish a complete LLM workflow or a real Unity/
Unreal run. Never execute commands copied from a spec without inspecting them.

State what was checked, what failed and what could not run. Recommend
`$skill-improve NAME` for instruction defects; request an isolated real scenario
for claims that require actual execution. Do not edit catalogs or publish reports
unless that write is within the user's authorized task.
