"""Replay lifecycle helpers and real engine QA in a fresh isolated studio copy.

Does not call an LLM, install software, run hooks or push anything. Codex performs
the skill reasoning; this runner verifies its observable project artifacts.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
STORY = 'production/epics/core/story-001-collect.md'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--godot', required=True, type=Path)
    parser.add_argument('--bash', default='bash')
    parser.add_argument('--render', action='store_true', help='also render screenshots; requires a display')
    args = parser.parse_args()
    godot = args.godot.resolve(strict=True)
    scratch = ROOT / '.scratch'
    scratch.resolve().relative_to(ROOT.resolve())
    if scratch.is_symlink() or scratch.is_junction():
        raise ValueError('Linked scratch directory is not supported')
    scratch.mkdir(exist_ok=True)
    project = Path(tempfile.mkdtemp(prefix='studio-cycle-', dir=scratch))
    # Preserve isolation: no symlink traversal, credentials, Git config or hooks.
    for folder in ('.claude', '.agents', '.codex'):
        if (ROOT / folder).is_symlink() or (ROOT / folder).is_junction():
            raise ValueError('Linked studio root is not supported')
        for path in (ROOT / folder).rglob('*'):
            if path.is_symlink() or path.is_junction():
                raise ValueError(f'Linked studio asset is not supported: {path}')
        shutil.copytree(ROOT / folder, project / folder)
    for path in (ROOT / 'fixtures/coin-collector').iterdir():
        if path.is_symlink() or path.is_junction():
            raise ValueError('Linked fixture asset is not supported')
        if path.name == '.godot' or path.name.endswith('.uid'):
            continue
        if path.is_dir():
            shutil.copytree(path, project / path.name, ignore=shutil.ignore_patterns('evidence', '.godot', '*.uid'))
        else:
            shutil.copy2(path, project / path.name)
    shutil.copy2(ROOT / 'AGENTS.md', project / 'AGENTS.md')
    (project / 'docs').mkdir(exist_ok=True)
    shutil.copy2(ROOT / 'docs/CODEX.md', project / 'docs/CODEX.md')
    evidence = project / 'production/qa/evidence/story-001-collect'
    evidence.mkdir(parents=True, exist_ok=True)
    logs = []
    env = dict(os.environ, CI='true', GODOT_SILENCE_ROOT_WARNING='1')

    def run(command, label, expected=0, stdin=None):
        result = subprocess.run(command, cwd=project, env=env, input=stdin,
                                capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=90)
        logs.append(f'## {label}\nexit={result.returncode}\n{result.stdout}{result.stderr}')
        if result.returncode != expected:
            raise RuntimeError(f'{label}: exit {result.returncode}\n{result.stdout}{result.stderr}')
        return result.stdout + result.stderr

    def helper(name, *arguments, **kwargs):
        return run([args.bash, f'.claude/scripts/{name}.sh', *arguments], name, **kwargs)

    version = run([str(godot), '--version'], 'engine-version')
    if not version.startswith('4.5.1.stable'):
        raise RuntimeError('This fixture requires Godot 4.5.1 stable')
    helper('project-state')
    helper('config-set', 'modes.rigor', 'minimal', '--dry-run')
    helper('config-set', 'modes.rigor', 'minimal')
    helper('config-set', 'modes.automation', 'autonomous')
    before = (project / 'project.yaml').read_bytes()
    helper('config-set', 'modes.rigor', 'not-a-valid-rigor', expected=3)
    if (project / 'project.yaml').read_bytes() != before:
        raise RuntimeError('Invalid setting changed project.yaml')
    run([args.bash, '.claude/hooks/yaml-helper.sh', 'resolve_config', '--keys',
         'workflow,automation,engine_values,qa.level'], 'resolve-config')
    helper('set-stage', 'Technical Setup')
    helper('set-stage', 'Pre-Production')
    helper('story-facts', STORY)
    helper('md-section', 'set-field', STORY, 'Status', 'In Progress')
    helper('set-stage', 'Production')
    output = run([str(godot), '--headless', '--path', '.', '--editor', '--import', '--quit'], 'import')
    if 'ERROR:' in output or 'SCRIPT ERROR' in output:
        raise RuntimeError('Godot import reported errors despite its exit status')
    output = run([str(godot), '--headless', '--path', '.', '--script', 'qa.gd', '--quit-after', '600'], 'headless-qa')
    if 'CYCLE_RESULT PASS' not in output or 'ERROR:' in output:
        raise RuntimeError('Headless QA did not complete successfully')
    # Build an allowlisted source distribution, then test the extracted package.
    # This is not a standalone executable: a Godot 4.5.1 runtime is required.
    inputs = ('project.godot', 'main.tscn', 'src/game.gd', 'tuning.json', 'qa.gd')
    package = project / 'coin-collector-source.zip'
    with zipfile.ZipFile(package, 'w', compression=zipfile.ZIP_DEFLATED) as zipped:
        for name in inputs:
            zipped.write(project / name, name)
    released = project / 'release-check'
    with zipfile.ZipFile(package) as zipped:
        if set(zipped.namelist()) != set(inputs):
            raise RuntimeError('Unexpected release payload')
        zipped.extractall(released)
    output = run([str(godot), '--headless', '--path', str(released), '--script', 'qa.gd',
                  '--quit-after', '600'], 'source-release-qa')
    if 'CYCLE_RESULT PASS' not in output or 'ERROR:' in output:
        raise RuntimeError('Extracted source distribution did not pass QA')
    if args.render:
        output = run([str(godot), '--path', '.', '--script', 'qa.gd', '--quit-after', '600',
                      '--audio-driver', 'Dummy'], 'rendered-qa')
        if 'CYCLE_RESULT PASS' not in output or 'ERROR:' in output:
            raise RuntimeError('Rendered QA did not complete successfully')
        for name in ('01-title', '02-paused', '03-won', '04-restarted'):
            if not (evidence / f'{name}.png').is_file():
                raise RuntimeError(f'Missing screenshot: {name}')
        story = project / STORY
        story.write_text(story.read_text(encoding='utf-8').replace('- [ ]', '- [x]').replace(
            'NOT VERIFIED - initial regression seed; runner writes actual results.',
            'OBSERVED - production/qa/evidence/story-001-collect/ (rendered run; visual review is separate).'), encoding='utf-8')
        helper('md-section', 'set-field', STORY, 'Status', 'Complete')
        helper('set-stage', 'Polish')
        helper('set-stage', 'Release')
    helper('session-state', 'checkpoint', stdin=f'**Current task**: {STORY}\n**Result**: QA passed; rendered={args.render}\n')
    helper('story-status')
    helper('project-state', '--stage')
    transcript = '\n'.join(logs).replace(str(project), '<isolated-project>').replace(project.as_posix(), '<isolated-project>')
    (evidence / 'run.log').write_text(transcript, encoding='utf-8')
    hashes = {name: hashlib.sha256((project / name).read_bytes()).hexdigest() for name in inputs}
    hashes[package.name] = hashlib.sha256(package.read_bytes()).hexdigest()
    (evidence / 'sha256.json').write_text(json.dumps(hashes, indent=2), encoding='utf-8')
    print(f'CYCLE PASS: {project}\nEvidence: {evidence}\nRendered: {args.render}')

if __name__ == '__main__':
    main()
