# Codex interpretation of the studio specs

The catalog and behavioral specs are preserved upstream evidence, not executed
tests. Read native `.agents/skills/NAME/SKILL.md`, workflow.md and references,
or `.codex/agents/NAME.toml`, when assessing the Codex version. Use
`python tools/audit_codex.py` for a structural inventory and `$skill-test` for
instruction/spec review. Do not run Claude-only linters on native wrappers.

Claude-specific schema/model/tool assertions are NOT APPLICABLE to Codex; map
their intended capability explicitly. Keep other behavioral requirements,
gate ordering, missing-evidence stops and out-of-domain boundaries intact.
For fixtures without explicit settings use upstream defaults: minimal rigor,
collaborative automation, no personal override. A scenario's explicit fixture
settings take precedence. Do not silently strengthen or relax a fixture.

Do not mark an unchecked case passed, update historical spec-result timestamps
after only reading instructions, claim independent agents ran during sequential
review, or execute external deployment actions merely because a spec mentions
them. Separate structural checks, helper replays, instruction review and actual
end-to-end runs in every report.
