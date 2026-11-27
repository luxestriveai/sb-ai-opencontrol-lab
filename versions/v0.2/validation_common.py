"""Integrity, fixtures and deterministic serialization; standard library only."""
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from verifier import VALID, verify_trace

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
COMMIT = 'a4255447882e0671ebfb0ca9412a2f977fffa010'
MANIFEST_HASH = 'c2555661d48995f3cd73a0ee11138565d18fdb119b8e2ad737898debdd04950e'
BASELINE_FILES = {'README.md', 'TECHNICAL_NOTE.md', 'experiment.py', 'test_experiment.py',
                  'results/runs.csv', 'results/summary.csv', 'results/summary.json', 'results/tests.txt'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('utf-8')


def object_hash(data):
    return hashlib.sha256(canonical(data)).hexdigest()


def duplicate_safe_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON object key: ' + key)
        result[key] = value
    return result


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=duplicate_safe_object)


def write_json(path, value):
    # Exclusive creation prevents replacing an earlier experimental result.
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=True) + '\n')


def read_csv(path):
    with Path(path).open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError('Invalid or duplicate CSV headers')
        rows = []
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError('Invalid CSV field count')
            rows.append({key: value if key in ('scenario', 'policy', 'schedule') else int(value)
                         for key, value in row.items()})
        return rows


def git(*args):
    return subprocess.run(['git', *args], cwd=REPO, check=True, capture_output=True).stdout


def verify_baseline():
    if sha(REPO / 'SHA256SUMS.txt') != MANIFEST_HASH:
        raise ValueError('Original manifest bytes changed')
    records = []
    for line in (REPO / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
        expected, name = line.split('  ', 1)
        if name not in BASELINE_FILES:
            raise ValueError('Unexpected baseline manifest entry')
        blob = git('cat-file', 'blob', COMMIT + ':' + name)
        if sha(REPO / name) != expected or hashlib.sha256(blob).hexdigest() != expected:
            raise ValueError('Original artifact checksum mismatch: ' + name)
        records.append({'file': name, 'sha256': expected, 'status': 'PASS'})
    if len(records) != 8 or {row['file'] for row in records} != BASELINE_FILES:
        raise ValueError('Missing/duplicate baseline checksum entry')
    return {'status': 'PASS', 'files': records, 'manifest_bytes_unchanged': True,
            'head': git('rev-parse', 'HEAD').decode().strip(),
            'branch': git('branch', '--show-current').decode().strip(), 'frozen_commit': COMMIT}


def verify_protocol():
    registration = read_json(HERE / 'PREREGISTRATION.json')
    for name, expected in registration['files'].items():
        if sha(HERE / name) != expected:
            raise ValueError('Locked protocol changed: ' + name)
    return {'status': 'PASS', 'locked_at': registration['locked_at'],
            'registration_sha256': sha(HERE / 'PREREGISTRATION.json')}


def evaluate_fixtures():
    corpus = read_json(HERE / 'fixtures/corpus.json')
    results = []
    for case in corpus['fixtures']:
        observed = verify_trace(case['trace'])
        errors = []
        if observed['classification'] != case['expected_classification']:
            errors.append('classification')
        if case['expected_metrics'] is None:
            if observed['metrics'] is not None:
                errors.append('metrics_should_be_null')
        else:
            for name, value in case['expected_metrics'].items():
                if observed['metrics'] is None or observed['metrics'].get(name) != value:
                    errors.append('metric:' + name)
            if observed['policy_conformant'] != case['expected_policy_conformant']:
                errors.append('policy_conformance')
        results.append({'id': case['id'], 'evidence_valid': case['evidence_valid'],
                        'expected': case['expected_classification'], 'observed': observed['classification'],
                        'status': 'PASS' if not errors else 'FAIL', 'errors': errors,
                        'metrics': observed['metrics'], 'policy_conformant': observed['policy_conformant'],
                        'diagnostics': observed['diagnostics']})
    false_safe = sum(r['observed'] == 'VALID_SAFE' and r['expected'] != 'VALID_SAFE' for r in results)
    false_rejection = sum(r['evidence_valid'] and r['observed'] not in VALID for r in results)
    return {'status': 'PASS' if all(r['status'] == 'PASS' for r in results) else 'FAIL',
            'total': len(results), 'valid_fixtures': sum(r['evidence_valid'] for r in results),
            'invalid_fixtures': sum(not r['evidence_valid'] for r in results),
            'correct_classifications': sum(r['expected'] == r['observed'] for r in results),
            'false_safe': false_safe, 'false_rejection': false_rejection,
            'false_unsafe': sum(r['expected'] == 'VALID_SAFE' and r['observed'] == 'VALID_UNSAFE' for r in results),
            'results': results}


def protect_output(path):
    output = Path(path).resolve()
    if output == REPO or REPO in output.parents:
        raise ValueError('Reproduction output must be outside the Git repository')
    if output.exists():
        raise ValueError('Output path already exists; refusing to overwrite')
    return output

