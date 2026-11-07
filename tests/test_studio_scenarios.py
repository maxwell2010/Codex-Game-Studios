"""Engine-independent replay fixtures; simulated runner output is not engine QA."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASH = (r'C:\Program Files\Git\bin\bash.exe' if os.name == 'nt' else shutil.which('bash'))

class StudioScenarios(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='codex studio scenarios ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / '.claude', self.root / '.claude')
        self.write('project.yaml', 'schema_version: 1\nmodes:\n  rigor: standard\n  automation: guided\nengine:\n  name: Unity\n  version: 6000.0\n')

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8', newline='\n')
        return path

    def helper(self, name, *args, code=0, stdin=None):
        result = subprocess.run([BASH, f'.claude/scripts/{name}.sh', *args], cwd=self.root,
            env=dict(os.environ, CI='true', PYTHONUTF8='1'), input=stdin, capture_output=True,
            text=True, encoding='utf-8', errors='replace', timeout=30)
        self.assertEqual(result.returncode, code, f'{name}: {result.stdout}\n{result.stderr}')
        return result.stdout

    def resolve(self, keys):
        result = subprocess.run([BASH, '.claude/hooks/yaml-helper.sh', 'resolve_config', '--keys', keys],
            cwd=self.root, env=dict(os.environ, CI='true', PYTHONUTF8='1'), capture_output=True,
            text=True, encoding='utf-8', errors='replace', timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_standard_full_minimal_mode_resolution(self):
        for rigor, workflow, review in [('minimal', 'minimal', 'solo'), ('standard', 'standard', 'lean'), ('full', 'full', 'full')]:
            with self.subTest(rigor=rigor):
                self.helper('config-set', 'modes.rigor', rigor)
                output = self.resolve('workflow,review_mode,qa.level')
                self.assertIn(f'workflow: {workflow}', output)
                self.assertIn(f'review_mode: {review}', output)

    def test_local_override_wins_without_changing_team_config(self):
        before = (self.root / 'project.yaml').read_bytes()
        self.helper('config-set', '--local', 'modes.review_mode', 'solo')
        self.assertIn('review_mode: solo (project.local.yaml)', self.resolve('review_mode'))
        self.assertEqual(before, (self.root / 'project.yaml').read_bytes())

    def test_invalid_setting_is_rejected_without_write(self):
        before = (self.root / 'project.yaml').read_bytes()
        self.helper('config-set', 'modes.rigor', 'invalid', code=3)
        self.assertEqual(before, (self.root / 'project.yaml').read_bytes())

    def test_stage_mirror_stays_in_sync_in_spaced_directory(self):
        self.helper('set-stage', 'Systems Design')
        output = self.helper('project-state', '--stage')
        self.assertIn('stage_yaml\tSystems Design', output)
        self.assertIn('stage_txt\tSystems Design', output)

    def test_markdown_section_edit_preserves_adjacent_sections(self):
        self.write('design/gdd/combat.md', '## Overview\nOriginal\n## Detailed Rules\nKeep me\n')
        self.helper('md-section', 'replace', 'design/gdd/combat.md', 'Overview', stdin='Updated\n')
        text = (self.root / 'design/gdd/combat.md').read_text(encoding='utf-8')
        self.assertIn('Updated', text)
        self.assertIn('## Detailed Rules\nKeep me', text)
        self.assertNotIn('Original', text)

    def test_gdd_skeleton_is_not_complete_content(self):
        self.write('design/gdd/combat.md', '## Overview\nReal content\n## Detailed Rules\n[To be designed]\n')
        output = self.helper('gdd-structure-check', 'design/gdd/combat.md')
        self.assertIn('PLACEHOLDER: Detailed Rules', output)
        self.assertIn('ABSENT:', output)

    def test_adr_states_and_missing_id_are_reported(self):
        for number, state in [(1, 'Accepted'), (2, 'Proposed'), (3, 'Deprecated'), (4, 'Superseded by ADR-0001')]:
            self.write(f'docs/architecture/adr-{number:04d}-test.md', f'# ADR\n## Status\n{state}\n## Date\n2026-11-07\n')
        output = self.helper('adr-status')
        for state in ('Accepted', 'Proposed', 'Deprecated', 'Superseded'):
            self.assertIn(state, output)
        self.assertIn('NOT_FOUND', self.helper('adr-status', 'ADR-9999', code=3))

    def test_empty_story_is_not_ready_and_missing_story_is_not_success(self):
        self.write('production/epics/combat/story-001-empty.md', '# Empty\nStatus: Ready\nType: Logic\n')
        output = self.helper('story-facts', '--all', '--lint')
        self.assertIn('LINT', output)
        self.assertIn('NOT_FOUND', self.helper('story-facts', 'production/epics/combat/story-999.md', code=3))

    def test_review_receipt_invalidates_changed_and_deleted_inputs(self):
        self.write('design/a.md', 'before')
        receipt = self.helper('review-receipts', 'hash', 'design/a.md')
        self.write('receipt.md', receipt)
        self.assertIn('UNCHANGED:', self.helper('review-receipts', 'check', 'receipt.md'))
        self.write('design/a.md', 'after')
        self.assertIn('CHANGED:', self.helper('review-receipts', 'check', 'receipt.md'))
        (self.root / 'design/a.md').unlink()
        self.assertIn('GONE:', self.helper('review-receipts', 'check', 'receipt.md'))

    def test_old_source_only_receipt_cannot_cover_new_native_workflow(self):
        self.write('.agents/skills/design-review/workflow.md', 'native instructions')
        self.write('receipt.md', self.helper('review-receipts', 'hash', '.claude/skills/design-review/SKILL.md'))
        output = self.helper('review-receipts', 'check', 'receipt.md', '.agents/skills/design-review/workflow.md')
        self.assertIn('NEW:', output)

    def test_sprint_percentage_zero_and_leap_day(self):
        self.assertIn('pct\t-', self.helper('plan-math', 'pct', '0', '0'))
        self.assertIn('days\t2', self.helper('plan-math', 'days', '2024-02-28', '2024-03-01'))

    def test_bug_scan_uses_header_status_not_fix_record(self):
        self.write('production/qa/bugs/BUG-0001.md', '# Bug\n**ID**: BUG-0001\n**Severity**: S1\n**Status**: Open\n## Fix Record\n**Status**: Closed\n')
        output = self.helper('bug-stats')
        self.assertIn('open_s1\t1', output)

    def test_registry_numbering_does_not_reuse_old_id(self):
        self.write('production/qa/bugs/BUG-0007.md', '# Closed old bug\nStatus: Closed\n')
        self.assertIn('BUG-0008', self.helper('registry', 'next-id', 'bug'))

    def test_content_and_debt_zero_denominators_are_unknown(self):
        self.assertIn('-', self.helper('content-count', 'band', '0', '0'))
        self.assertIn('-', self.helper('debt-register', 'score', '-', 'S'))

    def test_unity_scaffold_is_valid_and_never_overwrites_custom_files(self):
        self.write('tests/README.md', 'Keep user text')
        self.helper('test-scaffold', 'unity', '--date', '2026-11-07')
        self.assertEqual((self.root / 'tests/README.md').read_text(encoding='utf-8'), 'Keep user text')
        for platform in ('EditMode', 'PlayMode'):
            path = self.root / f'Assets/Tests/{platform}/{platform}Tests.asmdef'
            self.assertTrue(json.loads(path.read_text(encoding='utf-8'))['name'])
        before = path.read_bytes()
        self.helper('test-scaffold', 'unity', '--date', '2026-11-07')
        self.assertEqual(before, path.read_bytes())

    def test_unreal_scaffold_uses_module_and_rejects_path_traversal(self):
        self.helper('test-scaffold', 'unreal', '--module', 'Demo', '--project', 'Demo', '--date', '2026-11-07')
        self.assertTrue((self.root / 'Source/Demo/Private/Tests/README.md').is_file())
        self.helper('test-scaffold', 'unreal', '--module', '../escape', code=2)
        self.assertFalse((self.root.parent / 'escape').exists())

    def test_unity_runner_missing_framework_never_starts(self):
        output = self.helper('test-run', 'unity', '--cmd', 'touch SHOULD_NOT_EXIST')
        self.assertIn('ran\tno', output)
        self.assertIn('unity:no-test-framework', output)
        self.assertFalse((self.root / 'SHOULD_NOT_EXIST').exists())

    def unity_framework(self):
        self.write('Packages/manifest.json', '{"dependencies":{"com.unity.test-framework":"1.4.5"}}')
        (self.root / 'test-results').mkdir(exist_ok=True)

    def test_unity_simulated_zero_tests_are_not_a_pass(self):
        self.unity_framework()
        command = "printf '%s' '<test-run testcasecount=\"0\" passed=\"0\" failed=\"0\" />' > test-results/editmode.xml"
        output = self.helper('test-run', 'unity', '--cmd', command, '--timeout', '5')
        self.assertIn('unity:zero-tests', output)

    def test_unity_simulated_results_are_parsed_for_each_platform(self):
        self.unity_framework()
        for platform in ('editmode', 'playmode'):
            command = f"printf '%s' '<test-run testcasecount=\"2\" passed=\"2\" failed=\"0\" />' > test-results/{platform}.xml"
            output = self.helper('test-run', 'unity', '--platform', platform, '--cmd', command, '--timeout', '5')
            self.assertIn('unity:0', output)
            self.assertIn('total=2', output)

    def test_unity_missing_results_do_not_reuse_stale_report(self):
        self.unity_framework()
        self.write('test-results/editmode.xml', '<test-run total="99" passed="99" failed="0" />')
        output = self.helper('test-run', 'unity', '--cmd', 'true', '--timeout', '5')
        self.assertIn('unity:no-results', output)

    def test_runner_timeout_is_explicit(self):
        self.unity_framework()
        output = self.helper('test-run', 'unity', '--cmd', 'sleep 3', '--timeout', '1')
        self.assertIn('timed_out\tyes', output)
        self.assertIn('rule\ttimeout', output)

    def test_unreal_dry_run_quotes_paths_with_spaces(self):
        self.write('Demo.uproject', '{}')
        output = self.helper('test-run', 'unreal', '--exe', '/review/UE with spaces', '--os', 'linux', '--dry-run')
        self.assertIn('"/review/UE with spaces/Engine/Binaries/Linux/UnrealEditor"', output)
        self.assertIn('ran\tno\tdry run', output)

    def test_unreal_simulated_no_tests_is_not_success(self):
        self.write('Demo.uproject', '{}')
        output = self.helper('test-run', 'unreal', '--no-build', '--cmd', "printf '%s' 'No automation tests matched'", '--timeout', '5')
        self.assertIn('unreal:no-tests-matched', output)

    def test_flakiness_without_logs_does_not_claim_clean_runs(self):
        output = self.helper('flaky-stats', code=3)
        self.assertIn('absent', output)
        self.assertNotIn('PASS', output)

    def test_unity_failure_in_xml_outranks_zero_exit(self):
        self.unity_framework()
        command = "printf '%s' '<test-run testcasecount=\"2\" passed=\"1\" failed=\"1\" />' > test-results/editmode.xml"
        output = self.helper('test-run', 'unity', '--cmd', command, '--timeout', '5')
        self.assertIn('unity:result-fail', output)
        self.assertNotIn('every test passed', output)

    def test_known_unity_failure_outranks_unknown_test_count(self):
        self.unity_framework()
        command = "printf '%s' '<test-run failed=\"1\" />' > test-results/editmode.xml"
        output = self.helper('test-run', 'unity', '--cmd', command, '--timeout', '5')
        self.assertIn('unity:result-fail', output)

    def test_unity_multiline_xml_failure_is_not_hidden_by_zero_exit(self):
        self.unity_framework()
        command = "printf '%s' '<test-run testcasecount=\"2\"\n passed=\"1\" failed=\"1\" />' > test-results/editmode.xml"
        output = self.helper('test-run', 'unity', '--cmd', command, '--timeout', '5')
        self.assertIn('unity:result-fail', output)

    def test_unity_skipped_or_incomplete_counts_are_not_all_pass(self):
        self.unity_framework()
        command = "printf '%s' '<test-run testcasecount=\"2\" passed=\"0\" failed=\"0\" skipped=\"2\" />' > test-results/editmode.xml"
        output = self.helper('test-run', 'unity', '--cmd', command, '--timeout', '5')
        self.assertIn('unity:incomplete-results', output)
        self.assertNotIn('every test passed', output)

    def test_unreal_absent_ambiguous_or_unsafe_project_never_runs_command(self):
        for names in ([], ['One.uproject', 'Two.uproject'], ['Bad;Name.uproject']):
            with self.subTest(names=names):
                for path in self.root.glob('*.uproject'):
                    path.unlink()
                for name in names:
                    self.write(name, '{}')
                output = self.helper('test-run', 'unreal', '--no-build', '--cmd', 'touch SHOULD_NOT_EXIST')
                self.assertIn('unreal:invalid-project', output)
                self.assertIn('ran\tno', output)
                self.assertFalse((self.root / 'SHOULD_NOT_EXIST').exists())

    def test_asset_scan_uses_engine_content_root(self):
        self.write('Content/Maps/Test.umap', 'fixture')
        output = self.helper('asset-scan', '--engine', 'unreal', '--files')
        self.assertIn('Content/Maps/Test.umap', output)

    def test_inputs_distinguishes_empty_missing_and_present(self):
        self.write('design/empty.md', ' \n')
        self.write('design/brief.md', 'A real brief')
        output = self.helper('inputs-check', 'design/empty.md', 'design/missing.md', 'design/brief.md')
        for marker in ('EMPTY\tdesign/empty.md', 'ABSENT\tdesign/missing.md', 'FOUND\tdesign/brief.md'):
            self.assertIn(marker, output)

    def test_empty_gate_path_reports_absent_artifacts(self):
        output = self.helper('artifact-check', '--path', 'minimal')
        self.assertIn('status=ABSENT', output)
        self.assertNotIn('PASS', output)

    def test_adr_dependency_cycle_is_reported(self):
        for number, dependency in [(1, 2), (2, 1)]:
            self.write(f'docs/architecture/adr-{number:04d}-cycle.md',
                f'# ADR\n## Status\nAccepted\n## ADR Dependencies\n**Depends On**: ADR-{dependency:04d}\n')
        self.assertIn('CYCLE:', self.helper('adr-dep-graph'))

    def test_registry_validation_reports_duplicate_entities(self):
        self.write('design/registry/entities.yaml',
            'entities:\n  - name: Player\n    source: design/a.md\n  - name: Player\n    source: design/a.md\n')
        self.write('design/a.md', '# Source')
        self.assertIn('DUPLICATE', self.helper('registry', 'validate'))

    def test_flakiness_compares_pass_and_fail_across_real_xml_files(self):
        names = []
        for number in range(5):
            name = f'results/run-{number}.xml'
            failure = '<failure message="example" />' if number < 2 else ''
            self.write(name, f'<testsuite><testcase classname="combat" name="damage">{failure}</testcase></testsuite>')
            names.append(name)
        output = self.helper('flaky-stats', '--format', 'junit', *names)
        self.assertIn('flaky\t1', output)
        self.assertIn('combat.damage', output)

if __name__ == '__main__':
    unittest.main()
