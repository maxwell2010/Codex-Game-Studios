import hashlib
from pathlib import Path
import subprocess
import sys
import tomllib
import unittest
import yaml
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import build_codex

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
            body = (folder / 'workflow.md').read_text(encoding='utf-8')
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
        body = (ROOT / '.agents/skills/team-combat/workflow.md').read_text(encoding='utf-8')
        self.assertIn('.claude/skills/team-combat/../../hooks/yaml-helper.sh', body)
        self.assertTrue((ROOT / '.claude/skills/team-combat/../../hooks/yaml-helper.sh').resolve().is_file())
        self.assertIn('$team-combat', body)

    def test_every_supporting_resource_is_ported(self):
        resources = list((ROOT / '.claude/skills').glob('*/references/*.md'))
        self.assertGreater(len(resources), 100)
        for path in (ROOT / '.claude/skills').rglob('*'):
            if path.is_file() and path.name != 'SKILL.md':
                native = ROOT / '.agents/skills' / path.relative_to(ROOT / '.claude/skills')
                self.assertTrue(native.is_file(), str(native))
                self.assertEqual(native.read_text(encoding='utf-8'),
                    build_codex.adapt(path.read_text(encoding='utf-8'), path.relative_to(ROOT / '.claude/skills').parts[0]))

    def test_unsafe_generation_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'repo'
            root.mkdir()
            outside = Path(tmp) / 'outside.txt'
            with patch.object(build_codex, 'ROOT', root):
                with self.assertRaises(ValueError):
                    build_codex.write_generated(root / '..' / 'outside.txt', 'bad')
            self.assertFalse(outside.exists())

    def test_skill_conversion_preserves_paths_and_does_not_execute_commands(self):
        self.assertIn('touch SHOULD_NOT_EXIST', build_codex.adapt('!`touch SHOULD_NOT_EXIST`', 'start'))
        self.assertFalse((ROOT / 'SHOULD_NOT_EXIST').exists())
        self.assertEqual(build_codex.adapt('.claude/skills/start/SKILL.md and /start'),
                         '.claude/skills/start/SKILL.md and $start')

    def test_linked_output_is_rejected_without_touching_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'repo'
            root.mkdir()
            target = root / 'existing.txt'
            target.write_text('keep', encoding='utf-8')
            link = root / 'linked.txt'
            try:
                link.symlink_to(target)
            except OSError as error:
                self.skipTest(f'Symlink creation unavailable: {error.__class__.__name__}')
            with patch.object(build_codex, 'ROOT', root):
                with self.assertRaises(ValueError):
                    build_codex.write_generated(link, 'overwrite')
            self.assertEqual(target.read_text(encoding='utf-8'), 'keep')

    def test_workflow_reference_links_exist(self):
        import re
        for path in (ROOT / '.agents/skills').rglob('*.md'):
            relative = path.relative_to(ROOT / '.agents/skills')
            folder = ROOT / '.agents/skills' / relative.parts[0]
            for ref in re.findall(r'(?<![\w/])references/[A-Za-z0-9_.-]+\.md', path.read_text(encoding='utf-8')):
                self.assertTrue((folder / ref).is_file(), f'{path}: {ref}')

    def test_untrusted_yaml_object_tags_are_not_constructed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / 'SKILL.md'
            path.write_text('---\nname: start\ndescription: !!python/object:builtins.object {}\n---\nbody', encoding='utf-8')
            with patch.object(build_codex, 'ROOT', root):
                with self.assertRaises(yaml.constructor.ConstructorError):
                    build_codex.load(path)

    def test_generation_is_deterministic(self):
        def snapshot():
            return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for folder in ('.agents', '.codex') for p in (ROOT / folder).rglob('*') if p.is_file()}
        before = snapshot()
        subprocess.run([sys.executable, 'tools/build_codex.py'], cwd=ROOT, check=True)
        self.assertEqual(before, snapshot())

if __name__ == '__main__':
    unittest.main()
