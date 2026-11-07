"""Read-only native definition audit; does not execute skills or engine commands."""
import argparse
import json
from pathlib import Path
import re
import tomllib
import yaml

ROOT = Path(__file__).resolve().parents[1]

def read(path):
    path.resolve().relative_to(ROOT.resolve())
    if path.is_symlink() or path.is_junction():
        raise ValueError('linked definition is not supported')
    return path.read_text(encoding='utf-8')

def inspect(row, kind):
    name = row['name']
    result = {'name': name, 'kind': kind, 'category': row.get('category'),
              'structural': 'PASS', 'errors': [], 'spec_cases': [],
              'behavioral_execution': 'NOT ASSESSED - structural audit only'}
    try:
        spec = read(ROOT / row['spec'])
        result['spec_cases'] = re.findall(r'^### Case[^\n]*', spec, re.M)
        if not result['spec_cases']:
            raise ValueError('spec contains no behavioral cases')
        if kind == 'skill':
            folder = ROOT / '.agents/skills' / name
            text = read(folder / 'SKILL.md')
            parts = text.split('---', 2)
            if len(parts) != 3 or parts[0].strip():
                raise ValueError('invalid YAML frontmatter boundaries')
            meta = yaml.safe_load(parts[1])
            if not isinstance(meta, dict) or meta.get('name') != name or not isinstance(meta.get('description'), str):
                raise ValueError('invalid native skill name/description')
            if set(meta) != {'name', 'description'} or not meta['description'].strip():
                raise ValueError('unexpected fields or empty description')
            files = [folder / 'SKILL.md', folder / 'workflow.md', *sorted((folder / 'references').rglob('*.md'))]
            # Include root-level contracts, not only references/.
            files += [p for p in folder.glob('*.md') if p not in files]
            result['helpers_referenced'] = sorted(set(name for path in files for name in
                re.findall(r'/scripts/([a-z-]+)\.sh', read(path))))
            for path in files:
                content = read(path)
                for ref in set(re.findall(r'(?<![\w/])references/[A-Za-z0-9_.-]+\.md', content)):
                    read(folder / ref)
                if '$ARGUMENTS' in content or re.search(r'\$\{?CLAUDE_', content) or '!`' in content:
                    raise ValueError(f'unresolved runtime macro in {path.name}')
                if re.search(r'\$[a-z][a-z-]*\.(?:md|sh|yaml)\b', content):
                    raise ValueError(f'skill invocation corrupted a file path in {path.name}')
                if 'Codex runs all of' in content or re.search(r'pre-approv', content, re.I):
                    raise ValueError(f'unsupported permission/runtime claim in {path.name}')
            source = ROOT / '.claude/skills' / name
            if not (source / 'SKILL.md').is_file():
                raise ValueError('missing maintained source')
            source_meta = yaml.safe_load(read(source / 'SKILL.md').split('---', 2)[1])
            policy_path = folder / 'agents/openai.yaml'
            policy = yaml.safe_load(read(policy_path)) if policy_path.exists() else {}
            implicit = policy.get('policy', {}).get('allow_implicit_invocation', True)
            if not isinstance(implicit, bool) or implicit == source_meta.get('disable-model-invocation', False):
                raise ValueError('native invocation policy does not preserve source intent')
            result['implicit_invocation'] = implicit
            for resource in source.rglob('*.md'):
                if resource.name != 'SKILL.md':
                    read(folder / resource.relative_to(source))
            result['files_checked'] = len(files)
        else:
            role = tomllib.loads(read(ROOT / '.codex/agents' / (name + '.toml')))
            for key in ('name', 'description', 'developer_instructions'):
                if not isinstance(role.get(key), str) or not role[key].strip():
                    raise ValueError(f'missing role field: {key}')
            if role['name'] != name:
                raise ValueError('role name mismatch')
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as error:
        result['structural'] = 'NOT ASSESSED' if isinstance(error, OSError) else 'FAIL'
        # No file contents or exception payloads: malformed YAML may contain secrets.
        result['errors'].append(f'{error.__class__.__name__}: definition/spec could not be validated')
    return result

def audit(root=ROOT, name=None):
    global ROOT
    previous = ROOT
    ROOT = Path(root)
    try:
        catalog = yaml.safe_load(read(ROOT / 'studio-tests/catalog.yaml'))
        definitions = [(row, kind) for group, kind in (('skills', 'skill'), ('agents', 'agent'))
                       for row in catalog[group]]
        identities = [(kind, row['name']) for row, kind in definitions]
        if len(identities) != len(set(identities)):
            raise ValueError('duplicate catalog identity')
        expected = {kind: {row['name'] for row, k in definitions if k == kind} for kind in ('skill', 'agent')}
        found = {'skill': {p.parent.name for p in (ROOT / '.agents/skills').glob('*/SKILL.md')},
                 'agent': {p.stem for p in (ROOT / '.codex/agents').glob('*.toml')}}
        coverage_errors = [f'{kind}: registry/native definition mismatch' for kind in expected if expected[kind] != found[kind]]
        chosen = [(row, kind) for row, kind in definitions if name is None or row['name'] == name]
        if not chosen:
            raise ValueError('unknown definition name')
        rows = [inspect(row, kind) for row, kind in chosen]
        return {'scope': 'structure and spec inventory; not behavioral execution',
                'coverage_errors': coverage_errors, 'definitions': rows,
                'passed': not coverage_errors and all(row['structural'] == 'PASS' for row in rows)}
    finally:
        ROOT = previous

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    try:
        result = audit(name=args.name)
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as error:
        print(f'NOT ASSESSED: catalog or selection invalid ({error.__class__.__name__})')
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=True, indent=2))
    else:
        for row in result['definitions']:
            print(f"{row['kind']:5} {row['name']:28} {row['structural']:12} cases={len(row['spec_cases'])}")
        print('Structural audit:', 'PASS' if result['passed'] else 'FAIL/NOT ASSESSED')
        print('Behavioral execution: NOT ASSESSED by this command')
    return 0 if result['passed'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
