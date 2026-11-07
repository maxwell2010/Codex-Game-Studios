import hashlib
from pathlib import Path
import subprocess
import sys
import tomllib
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]

class AdapterTests(unittest.TestCase):
    def test_workflow_coverage_and_valid_frontmatter(self):
        upstream = {p.parent.name for p in (ROOT / '.claude/skills').glob('*/SKILL.md')}
        native = {p.parent.name for p in (ROOT / '.agents/skills').glob('*/SKILL.md')}
        self.assertEqual(upstream, native)
        for name in native:
            folder = ROOT / '.agents/skills' / name
            meta = yaml.safe_load((folder / 'SKILL.md').read_text(encoding='utf-8').split('---', 2)[1])
            self.assertEqual(set(meta), {'name', 'description'})
            self.assertEqual(meta['name'], name)
            self.assertTrue(meta['description'])
            body = (folder / 'references/workflow.md').read_text(encoding='utf-8')
            self.assertNotIn('!`', body)
            self.assertNotIn('CLAUDE_SKILL_DIR', body)
            self.assertNotIn('.claude/skills$', body)

    def test_roles_are_parseable_and_preserve_all_roles(self):
        source = {p.stem for p in (ROOT / '.claude/agents').glob('*.md')}
        roles = list((ROOT / '.codex/agents').glob('*.toml'))
        self.assertEqual(source, {p.stem for p in roles})
        for path in roles:
            role = tomllib.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(role['name'], path.stem)
            self.assertTrue(role['description'])
            self.assertTrue(role['developer_instructions'])
            self.assertNotIn('model', role)

    def test_command_paths_survive_conversion(self):
        body = (ROOT / '.agents/skills/team-combat/references/workflow.md').read_text(encoding='utf-8')
        self.assertIn('.claude/skills/team-combat/../../hooks/yaml-helper.sh', body)
        self.assertTrue((ROOT / '.claude/skills/team-combat/../../hooks/yaml-helper.sh').resolve().is_file())
        self.assertIn('$team-combat', body)

    def test_generation_is_deterministic(self):
        def snapshot():
            return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for folder in ('.agents', '.codex') for p in (ROOT / folder).rglob('*') if p.is_file()}
        before = snapshot()
        subprocess.run([sys.executable, 'tools/build_codex.py'], cwd=ROOT, check=True)
        self.assertEqual(before, snapshot())

if __name__ == '__main__':
    unittest.main()
