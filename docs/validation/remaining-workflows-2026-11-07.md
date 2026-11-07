# Remaining Codex workflows review - 2026-11-07

## Scope and result

Native structural/compatibility audit: **74 skills and 49 roles PASS**. The
registry inventories **516 skill cases and 257 role cases**. These case counts
are not behavioral pass counts. Reviewed native runtime assumptions, resource
resolution, schema/policy mapping, gate handoffs and cross-engine paths against
the associated spec summaries and case inventories. Not every case was replayed.

**55 automated regressions pass locally**, including 35 isolated helper scenario
tests. Helpers run on real fixture files in temporary directories with spaces.
Unity/Unreal test outputs are deliberately simulated for runner/parser checks;
their editors were not installed in the probed standard locations and no editor
runtime test is claimed. The existing real Godot lifecycle remains a separate
[validation](cycle-2026-11-07.md) and runs in CI alongside these checks.

No deployment, release-store operation, external message, paid engine install,
multi-hour soak, independent-agent evaluation or 516-case LLM benchmark was run.
All-skill automatic discovery and custom-agent spawning in a fresh Codex client
remain NOT ASSESSED. This review does not convert those gaps into passes.

## Confirmed defects and fixes

1. Invocation conversion matched filenames and name prefixes. Patch notes looked
   for `production/releases/[version]$changelog.md`; filenames and paths are now
   preserved, while complete slash invocations are converted to Codex syntax.
2. `$ARGUMENTS` survived as an unexplained Claude macro. Native text now names
   the user's invocation arguments and states that shell injection is explicit.
3. Native skill-test tested Claude sources and demanded Claude-only metadata;
   a global rename also falsely claimed Codex ran all Claude mechanisms. It now
   audits native definitions, interprets source specs with explicit format
   exceptions, and distinguishes structural/spec review from actual execution.
4. Skill-improve edited generated/source files without a reliable regeneration
   contract. Its native workflow now identifies maintained sources/overrides,
   regenerates, checks regressions and keeps unrelated user work intact.
5. Five explicit-only source skills lost their invocation policy: dev-story,
   story-done, hotfix, launch-checklist and day-one-patch. The generator now
   preserves the policy via agents/openai.yaml without disabling other skills.
6. Dev-story, settings, perf-profile and asset-audit retained claims of shell
   pre-approval or suggested changing Claude permission files. Native instructions
   now defer to actual Codex permissions and do not grant execution rights.
7. Review freshness checks stamped upstream instructions only. Native references
   and bridge now require native workflow/entrypoint/supporting inputs in receipt
   checks, so an old source-only receipt produces NEW and cannot justify reuse.
8. Onboarding read Claude role directories. It now reads native TOML roles.
9. Regression-suite searched only Godot test locations/suffixes; qa-plan suggested
   Godot paths on other engines. Both now route Unity EditMode/PlayMode and Unreal
   module tests explicitly; unknown engines/roots stay NOT ASSESSED.
10. Unity runner trusted exit 0 even if its XML reported failures. Known failures
    now outrank success or unknown counts, and stale results remain discarded.
    A reproduced multiline-XML case hid failed counts; an all-skipped case also
    incorrectly passed. Multiline elements are now read together and incomplete
    counts remain NOT ASSESSED instead of claiming every test passed.
11. Unreal runner selected the first .uproject or constructed `.uproject` with an
    empty basename. It now refuses missing, ambiguous or unsafe project names
    before executing either build or test commands.
12. Engine guidance retained Unity's canceled install-count fee assumptions and
    an inaccurate blanket claim about Unreal mobile support. Replaced with
    current official-source verification requirements and project-specific
    platform checks, rather than freezing legal/financial advice in a template.
13. Shared workflow-catalog comments said FAIL gates never block advancement,
    contradicting gate-check. The comments now preserve FAIL/unknown semantics.

One initial candidate was **not a defect**: patch-notes' missing optional custom
template has an explicit built-in fallback. No fake template was added.

## Scenario layers actually exercised

- Configuration: three rigor presets, local precedence, invalid enums without
  writes, stage/mirror consistency and paths with spaces.
- Authoring/readiness: section edits preserve neighbors, GDD placeholders are
  reported, Accepted/Proposed/Deprecated/Superseded ADRs stay distinct, missing
  stories/criteria and dependency cycles are visible.
- Registries/reviews: duplicate entities, monotonically increasing IDs, changed
  and deleted review inputs, and native files absent from old receipts.
- Production/QA: zero-denominator planning/content/debt, bug header-vs-fix status,
  empty gate artifacts, absent inputs and actual multi-file JUnit flakiness data.
- Unity/Unreal helper contracts: scaffolding, idempotence/no overwrite, module
  traversal refusal, spaced editor paths, framework prechecks, Edit/Play Mode
  result parsing, zero tests, missing/stale reports, timeouts, failure evidence
  despite exit 0, no-matching-tests and safe/unique Unreal project selection.
- Adapter: all resources and known local links, native schemas, explicit-only
  policies, no execution during conversion, YAML object tags, linked target and
  outside-root refusal, unknown/malformed native definitions and deterministic
  regeneration. Bandit on the generator/native auditor: zero findings.

## Per-skill inventory

PASS in this table means structural/compatibility audit only. The helper column
lists referenced helper capabilities covered by the isolated fixture tests; it
does **not** assert the entire skill ran. A dash means no referenced helper in
this replay set. Behavioral cases below are inventoried, not executed.

| Skill | Category | Cases inventoried | Native structure | Helper capabilities replayed |
| --- | --- | ---: | --- | --- |
| gate-check | gate | 10 | PASS | adr-dep-graph, artifact-check, gdd-structure-check, set-stage |
| design-review | review | 6 | PASS | gdd-structure-check, review-receipts |
| story-readiness | readiness | 9 | PASS | adr-status, story-facts |
| story-done | readiness | 8 | PASS | adr-status, md-section, review-receipts, story-facts |
| review-all-gdds | review | 9 | PASS | - |
| architecture-review | review | 5 | PASS | adr-dep-graph, registry, review-receipts |
| create-epics | pipeline | 7 | PASS | adr-status, gdd-structure-check, md-section |
| create-stories | pipeline | 6 | PASS | adr-status, md-section |
| dev-story | pipeline | 13 | PASS | adr-status, md-section, review-receipts, story-facts |
| create-control-manifest | pipeline | 6 | PASS | adr-status, md-section |
| propagate-design-change | pipeline | 6 | PASS | adr-status, md-section |
| architecture-decision | authoring | 7 | PASS | registry |
| map-systems | pipeline | 7 | PASS | - |
| vertical-slice | pipeline | 6 | PASS | - |
| design-system | authoring | 8 | PASS | registry |
| consistency-check | analysis | 10 | PASS | registry |
| sprint-plan | sprint | 7 | PASS | - |
| sprint-status | sprint | 7 | PASS | - |
| team-ui | team | 6 | PASS | - |
| team-combat | team | 5 | PASS | - |
| team-narrative | team | 6 | PASS | - |
| team-audio | team | 6 | PASS | - |
| team-level | team | 5 | PASS | - |
| team-polish | team | 8 | PASS | - |
| team-release | team | 6 | PASS | - |
| team-live-ops | team | 6 | PASS | - |
| team-qa | team | 9 | PASS | - |
| skill-test | utility | 10 | PASS | - |
| skill-improve | utility | 7 | PASS | - |
| start | utility | 8 | PASS | config-set, project-state, set-stage |
| help | utility | 8 | PASS | artifact-check |
| brainstorm | utility | 6 | PASS | - |
| project-stage-detect | utility | 7 | PASS | artifact-check |
| setup-engine | utility | 8 | PASS | - |
| quick-design | authoring | 6 | PASS | - |
| ux-design | authoring | 6 | PASS | - |
| ux-review | authoring | 5 | PASS | - |
| art-bible | authoring | 5 | PASS | - |
| create-architecture | authoring | 8 | PASS | registry |
| code-review | analysis | 7 | PASS | - |
| balance-check | analysis | 6 | PASS | - |
| asset-audit | analysis | 9 | PASS | - |
| content-audit | analysis | 9 | PASS | - |
| tech-debt | analysis | 9 | PASS | - |
| scope-check | analysis | 6 | PASS | - |
| estimate | analysis | 5 | PASS | - |
| perf-profile | analysis | 7 | PASS | - |
| security-audit | analysis | 7 | PASS | - |
| test-evidence-review | analysis | 9 | PASS | review-receipts |
| test-flakiness | analysis | 5 | PASS | - |
| reverse-document | utility | 7 | PASS | - |
| bug-report | utility | 7 | PASS | - |
| hotfix | utility | 6 | PASS | - |
| prototype | utility | 7 | PASS | - |
| playtest-report | utility | 5 | PASS | - |
| milestone-review | sprint | 7 | PASS | - |
| retrospective | sprint | 6 | PASS | - |
| changelog | sprint | 7 | PASS | - |
| patch-notes | sprint | 7 | PASS | - |
| onboard | utility | 5 | PASS | - |
| localize | utility | 7 | PASS | - |
| launch-checklist | utility | 6 | PASS | - |
| release-checklist | utility | 8 | PASS | - |
| adopt | utility | 6 | PASS | gdd-structure-check |
| smoke-check | utility | 13 | PASS | - |
| soak-test | utility | 6 | PASS | - |
| test-setup | utility | 5 | PASS | - |
| test-helpers | utility | 6 | PASS | - |
| regression-suite | utility | 6 | PASS | - |
| qa-plan | utility | 5 | PASS | - |
| bug-triage | utility | 6 | PASS | - |
| asset-spec | utility | 6 | PASS | - |
| day-one-patch | utility | 6 | PASS | - |
| settings | utility | 9 | PASS | config-set |

The 49 TOML roles pass schema/spec-inventory checks. Their 257 cases and
independent multi-agent behavior are NOT EXECUTED by the structural auditor.
Team dependency order, blocking gates, active rosters and lack-of-independent-
review disclosures remain instruction requirements, not verified concurrency.

## Reproduce and inspect

```sh
python -m pip install -r tools/requirements.txt
python tools/audit_codex.py
python tools/audit_codex.py --name help --json
python -m unittest discover -s tests -v
```

Run audit after regeneration. It never executes skill bodies, catalog commands,
spec snippets, hooks or engine binaries. Nonzero means a failed/unknown structural
check or invalid selection. Shared source changes require regeneration; native
workflow overrides live in tools/codex_workflows/.

Official sources consulted for the engine-guidance correction:
- [Unity Personal](https://unity.com/products/unity-personal)
- [Unity pricing changes and Runtime Fee cancellation](https://unity.com/products/pricing-updates)
- [Unreal licensing](https://www.unrealengine.com/license)
- [Unreal mobile support](https://www.unrealengine.com/uses/mobile-games)

See [machine-readable audit](remaining-workflows-native-audit.json) for every
native definition and its case titles; [local regression transcript](remaining-workflows-tests.txt)
records actual automated results. Future runs may have different tool timings.
