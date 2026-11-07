# Codex Game Studios

Community Codex adaptation of [Donchitos/Claude-Code-Game-Studios](https://github.com/Donchitos/Claude-Code-Game-Studios).

**74 workflow skills. 49 studio roles. Godot, Unity and Unreal guidance.**

This is a studio workflow template, not a game engine or finished game.

## Quick start

```sh
git clone https://github.com/maxwell2010/Codex-Game-Studios.git
cd Codex-Game-Studios
```

Open the root in Codex, review AGENTS.md and start a new session. Ask: **Use $start to help me set up my game project.** Use `$help` for workflows and `$setup-engine` for your engine. If skills are not discovered, ask Codex to read `.agents/skills/start/SKILL.md` explicitly.

Keep the entire repository. Shell helpers require Bash and Unix utilities; Windows users can use Git Bash or configured WSL.

## Contents

| Location | Purpose |
| --- | --- |
| AGENTS.md | Codex project instructions |
| .agents/skills/ | 74 skills with adapted workflows |
| .codex/agents/ | 49 native TOML roles inheriting the session model |
| .claude/ | Preserved upstream scripts, rules, templates and Claude support |
| project.yaml | Engine and workflow configuration |
| tools/build_codex.py | Reproducible adapter generator |

Try `$brainstorm`, `$prototype`, `$dev-story`, `$code-review`, `$qa-plan` or `$team-combat`. Team workflows use available authorized subagents, with sequential role execution as a fallback.

## Compatibility

Read [the Codex bridge](docs/CODEX.md). Claude hooks, deny lists, status lines and model tiers are **not automatically active in Codex**. Rules need explicit reads; inherited tool names must be mapped to available tools. No global settings are changed.

Tests cover packaging, TOML, supporting resources, reference links, safe paths and deterministic regeneration. A small Godot game now exercises an isolated lifecycle through engine QA, rendered screenshots, story closure and a tested source distribution. CI runs the adapter and engine cycle on Linux and Windows. This validates one minimal workflow, not all workflows or engines.

See the [lifecycle report](docs/validation/cycle-2026-11-07.md), [security review](docs/validation/security-2026-11-07.md), and [playable fixture](fixtures/coin-collector/README.md).

```sh
python -m pip install -r tools/requirements.txt
python tools/build_codex.py
python -m unittest discover -s tests -v
```

Maintenance tools require Python 3.12 or newer. Run `python tools/fetch_test_engine.py`
to download the checksum-pinned test engine locally, then follow the report to
run `tools/run_studio_cycle.py`. No engine is downloaded by ordinary skill use.

## По-русски

Откройте проект в Codex и напишите: «Используй $start, помоги настроить игровой проект». Далее используйте `$help` и `$setup-engine`. Это адаптация процессов студии. Хуки Claude в Codex автоматически не работают; ограничения описаны в [docs/CODEX.md](docs/CODEX.md).

## Attribution

Original copyright (c) 2026 Donchitos. [MIT license](LICENSE) retained unchanged. Community fork, not an official OpenAI or Anthropic product. [Original README](docs/UPSTREAM-README.md) is a historical reference; its relative links refer to upstream. Based on upstream commit `05ad7c8a5b8aa2aa86bbd3439ae7cf7295cac418`.
