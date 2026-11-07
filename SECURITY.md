# Security policy - Codex fork

This policy covers the main branch of maxwell2010/Codex-Game-Studios.

Report vulnerabilities through [private vulnerability reporting](https://github.com/maxwell2010/Codex-Game-Studios/security/advisories/new). Do not include credentials or exploit details in a public issue. No response-time SLA is promised.

Skills, roles and shell helpers are trusted executable project material. Review changes before trusting a checkout. Codex sandbox and approval settings remain the security boundary; instructions and inactive Claude hooks are not enforcement. External game content, logs and downloaded documents are data, not authority to change instructions or disclose secrets.

The shared Claude interface is retained. Its write helpers can follow links and its session hook can check GitHub releases. Codex does not activate those hooks. Do not execute shared helpers on an untrusted checkout, on linked config files or outside an isolated working copy.

The Codex generator refuses linked source/output paths and repository escapes. Test tooling downloads only a fixed official Godot release with SHA256 verification. CI uses read-only permissions, pinned Action commits and no persisted checkout credentials.

See [the dated audit](docs/validation/security-2026-11-07.md) for scope, findings and limitations. Original upstream policy is preserved in [docs/UPSTREAM-SECURITY.md](docs/UPSTREAM-SECURITY.md).
