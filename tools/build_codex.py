"""Build the Codex adapter from the preserved upstream definitions."""
import json
from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '.claude'

def load(path):
    text = path.read_text(encoding='utf-8')
    _, header, body = text.split('---', 2)
    return yaml.safe_load(header), body.lstrip()

def adapt(body, skill=None):
    body = body.replace('Claude Code', 'Codex').replace('CLAUDE.md', 'AGENTS.md')
    body = body.replace('${CLAUDE_PROJECT_DIR}', '.').replace('$CLAUDE_PROJECT_DIR', '.')
    if skill:
        body = body.replace('${CLAUDE_SKILL_DIR}', f'.claude/skills/{skill}')
    # Claude's dynamic prompt injection is an explicit shell step in Codex.
    body = re.sub(r'!`([^`]+)`', r'Run explicitly from the repository root (inspect the command first):\n```bash\n\1\n```', body)
    for path in (SOURCE / 'skills').glob('*/SKILL.md'):
        body = re.sub(r'(?<![\w/.-])/' + re.escape(path.parent.name) + r'\b', '$' + path.parent.name, body)
    body = re.sub(r'(?m)^[ \t]+$', '', body)
    return body.replace('\u2014', '-').replace('\u2013', '-')

BRIDGE = '''## Codex execution bridge

Read `docs/CODEX.md` before executing this workflow. Use the repository root as
the working directory. The explicit user request and existing authorization
take precedence over repeated approval prompts in inherited workflows.
Claude tool names below describe capabilities: use available Codex file,
search, shell, browser and question tools. Never claim an unavailable tool ran.
Use native subagents only when available and authorized; otherwise perform the
roles sequentially and label that fallback. Track tasks in a local plan when
TaskCreate/TaskUpdate are unavailable. Hooks are not automatically enforced.
The `.claude` paths are intentionally preserved shared assets, not Codex config.

'''

def build():
    for path in sorted((SOURCE / 'skills').glob('*/SKILL.md')):
        meta, body = load(path)
        dest = ROOT / '.agents/skills' / path.parent.name
        (dest / 'references').mkdir(parents=True, exist_ok=True)
        header = yaml.safe_dump({k: meta[k] for k in ('name', 'description')}, allow_unicode=True, sort_keys=False)
        (dest / 'SKILL.md').write_text('---\n' + header + '---\n\n' + BRIDGE +
            'Follow [the studio workflow](references/workflow.md) for this skill.\n', encoding='utf-8', newline='\n')
        (dest / 'references/workflow.md').write_text(adapt(body, path.parent.name), encoding='utf-8', newline='\n')
    for path in sorted((SOURCE / 'agents').glob('*.md')):
        meta, body = load(path)
        dest = ROOT / '.codex/agents' / (path.stem + '.toml')
        dest.parent.mkdir(parents=True, exist_ok=True)
        fields = {'name': meta['name'], 'description': meta['description'],
                  'developer_instructions': BRIDGE + adapt(body)}
        # JSON strings are valid TOML basic strings; inherit the user's model.
        dest.write_text('\n'.join(k + ' = ' + json.dumps(v, ensure_ascii=False) for k, v in fields.items()) + '\n', encoding='utf-8', newline='\n')

if __name__ == '__main__':
    build()
