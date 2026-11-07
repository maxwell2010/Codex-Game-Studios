from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import audit_codex

class NativeAuditTests(unittest.TestCase):
    def test_complete_native_catalog_has_no_unevaluated_structural_rows(self):
        report = audit_codex.audit(ROOT)
        self.assertTrue(report['passed'], report['coverage_errors'])
        self.assertEqual(len(report['definitions']), 123)
        self.assertEqual(sum(row['kind'] == 'skill' for row in report['definitions']), 74)
        self.assertTrue(all(row['spec_cases'] for row in report['definitions']))
        self.assertTrue(all('NOT ASSESSED' in row['behavioral_execution'] for row in report['definitions']))

    def test_help_is_a_definition_name_and_unknown_name_is_rejected(self):
        report = audit_codex.audit(ROOT, name='help')
        self.assertEqual([row['name'] for row in report['definitions']], ['help'])
        with self.assertRaises(ValueError):
            audit_codex.audit(ROOT, name='missing-native-skill')

    def test_missing_native_workflow_is_not_a_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / '.agents/skills/demo'
            folder.mkdir(parents=True)
            (folder / 'SKILL.md').write_text('---\nname: demo\ndescription: demo test\n---\nRead workflow.md', encoding='utf-8')
            (root / 'spec.md').write_text('### Case 1: Test\nDo the work', encoding='utf-8')
            with patch.object(audit_codex, 'ROOT', root):
                result = audit_codex.inspect({'name': 'demo', 'spec': 'spec.md'}, 'skill')
            self.assertEqual(result['structural'], 'NOT ASSESSED')

    def test_malformed_agent_is_not_reported_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / '.codex/agents'
            folder.mkdir(parents=True)
            (folder / 'demo.toml').write_text('name = "demo"\n', encoding='utf-8')
            (root / 'spec.md').write_text('### Case 1: Test\n', encoding='utf-8')
            with patch.object(audit_codex, 'ROOT', root):
                result = audit_codex.inspect({'name': 'demo', 'spec': 'spec.md'}, 'agent')
            self.assertEqual(result['structural'], 'FAIL')

    def test_native_test_and_improve_do_not_test_only_claude_sources(self):
        body = (ROOT / '.agents/skills/skill-test/workflow.md').read_text(encoding='utf-8')
        self.assertIn('tools/audit_codex.py', body)
        self.assertNotIn('Codex runs all of', body)
        self.assertNotIn('The file must contain all of these', body)
        improve = (ROOT / '.agents/skills/skill-improve/workflow.md').read_text(encoding='utf-8')
        self.assertIn('tools/build_codex.py', improve)
        self.assertIn('tools/codex_workflows/NAME.md', improve)

    def test_regression_and_qa_instructions_route_all_engine_roots(self):
        for name in ('qa-plan', 'regression-suite'):
            text = (ROOT / '.agents/skills' / name / 'workflow.md').read_text(encoding='utf-8')
            for root in ('Assets/Tests/EditMode/', 'Assets/Tests/PlayMode/', 'Source/<Module>/Private/Tests/'):
                self.assertIn(root, text)
            self.assertIn('NOT ASSESSED', text)

if __name__ == '__main__':
    unittest.main()
