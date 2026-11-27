"""Publication packaging verifier and transparent isolated reproduction adapter.

Does not change scientific code, fixtures, expectations, or the supplied baseline repo.
Historical manifests stay historical; PUBLICATION_SHA256SUMS.txt binds this derivative.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
COMMIT = 'a4255447882e0671ebfb0ca9412a2f977fffa010'
COMMITTED_MANIFEST = '849849fe003af9f764343e66c02d515d4ffbf338dccb125890d438578b801ec1'
HISTORICAL_MANIFEST = 'c2555661d48995f3cd73a0ee11138565d18fdb119b8e2ad737898debdd04950e'
DETERMINISTIC = ('fixture-results.json', 'optimized-fixture-results.json', 'baseline-audit.json',
    'observed-traces.jsonl.gz', 'verified-runs.csv', 'verified-summary.csv', 'verified-summary.json',
    'mutation-results.json', 'robustness-results.json')

def require(value, message):
    if not value:
        raise ValueError(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'Duplicate JSON key')
            result[key] = value
        return result
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)

def save(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')

def verify_candidate():
    manifest = HERE / 'PUBLICATION_SHA256SUMS.txt'
    entries = {}
    for line in manifest.read_text(encoding='ascii').splitlines():
        expected, name = line.split('  ', 1)
        target = (HERE / name).resolve()
        require(target.is_relative_to(HERE) and name not in entries, 'Invalid publication manifest entry')
        require(target.is_file() and not target.is_symlink() and sha(target.read_bytes()) == expected,
                'Publication checksum mismatch: ' + name)
        entries[name] = expected
    inventory = {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file() and p != manifest}
    require(inventory == set(entries), 'Publication inventory mismatch')
    transformation = load(HERE / 'TRANSFORMATIONS.json')
    records = transformation['files']
    require(len(records) == 47, 'Historical inventory count mismatch')
    by_name = {r['relative_path']:r for r in records}
    require(len(by_name) == 47, 'Duplicate transformation path')
    for record in records:
        target = (HERE / record['relative_path']).resolve()
        require(target.is_relative_to(HERE), 'Invalid transformation path')
        require(sha(target.read_bytes()) == record['derivative_sha256'], 'Derivative binding failed')
    # Original manifest entries are evidence of original bytes, never relabeled as derivative hashes.
    for line in (HERE / 'SHA256SUMS.txt').read_text(encoding='ascii').splitlines():
        original, name = line.split('  ', 1)
        require(by_name[name]['original_sha256'] == original, 'Historical hash mapping failed')
    registration = load(HERE / 'PREREGISTRATION.json')
    changed_protocol_files = []
    for name, expected in registration['files'].items():
        require(by_name[name]['original_sha256'] == expected, 'Historical protocol binding failed')
        if by_name[name]['derivative_sha256'] != expected:
            changed_protocol_files.append(name)
    require(changed_protocol_files == ['evidence/prior/diagnostics.py.txt'], 'Unexpected protocol transformation')
    return records, len(entries)

def validate_output(output, baseline_repo):
    output, baseline_repo = output.resolve(), baseline_repo.resolve()
    require(not output.exists(), 'Output must not exist')
    for protected in (HERE, baseline_repo):
        require(not output.is_relative_to(protected) and not protected.is_relative_to(output),
                'Output overlaps a protected directory')
    return output

def git(directory, *args):
    process = subprocess.run(['git', '-C', str(directory), *args], capture_output=True)
    require(process.returncode == 0, 'Local Git operation failed; details retained privately by caller if needed')
    return process.stdout

def execute(baseline_repo, output):
    records, count = verify_candidate()
    baseline_repo = baseline_repo.resolve()
    require(baseline_repo.is_dir(), 'Baseline repository missing')
    output = validate_output(output, baseline_repo)
    manifest = git(baseline_repo, 'cat-file', 'blob', COMMIT + ':SHA256SUMS.txt')
    require(sha(manifest) == COMMITTED_MANIFEST, 'Committed baseline manifest mismatch')
    historical_manifest = manifest.replace(b'\n', b'\r\n')
    require(sha(historical_manifest) == HISTORICAL_MANIFEST, 'Historical manifest reconstruction mismatch')
    output.mkdir(parents=True, exist_ok=False)
    isolated = output / 'isolated-repository'
    clone = subprocess.run(['git', '-c', 'core.autocrlf=false', 'clone', '--local', '--no-hardlinks',
        '--no-checkout', '--quiet', str(baseline_repo), str(isolated)], capture_output=True)
    require(clone.returncode == 0, 'Local isolated clone failed')
    git(isolated, 'config', '--local', 'core.autocrlf', 'false')
    git(isolated, 'checkout', '--detach', '--quiet', COMMIT)
    require((isolated/'SHA256SUMS.txt').read_bytes() == manifest, 'Isolated committed manifest mismatch')
    # Explicit historical compatibility in the disposable isolated clone ONLY.
    # No baseline checksum entries or research artifacts are changed.
    (isolated/'SHA256SUMS.txt').write_bytes(historical_manifest)
    version = isolated / 'versions/v0.2'
    for record in records:
        target = version / record['relative_path']
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write((HERE/record['relative_path']).read_bytes())
    registration = load(version/'PREREGISTRATION.json')
    original_registration_hash = sha((version/'PREREGISTRATION.json').read_bytes())
    diagnostic = 'evidence/prior/diagnostics.py.txt'
    original_diagnostic_hash = registration['files'][diagnostic]
    registration['files'][diagnostic] = sha((version/diagnostic).read_bytes())
    registration['publication_copy_binding'] = {
        'status':'DERIVED_PATH_ONLY_BINDING_NOT_HISTORICAL_PREREGISTRATION',
        'historical_registration_sha256':original_registration_hash,
        'historical_diagnostic_sha256':original_diagnostic_hash,
        'scope':'Only diagnostic path literal differs; contract, fixture corpus, scientific code and all expectations unchanged'}
    # Historical PREREGISTRATION.json remains untouched in the candidate and archive.
    (version/'PREREGISTRATION.json').write_text(json.dumps(registration,indent=2)+'\n', encoding='utf-8', newline='\n')
    save(output/'compatibility-record.json', {
        'scope':'Isolated validation copy only; not frozen originals or candidate',
        'root_manifest':{'git_blob_sha256':COMMITTED_MANIFEST,'historical_crlf_sha256':HISTORICAL_MANIFEST,
                         'reason':'Unchanged historical validator pins the original CRLF representation'},
        'protocol':{'historical_registration_sha256':original_registration_hash,
            'isolated_binding_sha256':sha((version/'PREREGISTRATION.json').read_bytes()),
            'changed_file_hash':diagnostic,'historical_diagnostic_sha256':original_diagnostic_hash,
            'derivative_diagnostic_sha256':registration['files'][diagnostic]},
        'scientific_code_and_expectations_modified':False})
    print('Publication manifest and isolated compatibility checks: PASS', flush=True)
    result_dir = output/'fresh-results'
    process = subprocess.run([sys.executable,'-B',str(version/'run_validation.py'),'--output',str(result_dir)],
        cwd=isolated,capture_output=True,text=True,timeout=180)
    with (output/'private-execution-log.txt').open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(process.stdout + process.stderr)
    require(process.returncode == 0, 'Reproduction failed; see private execution log')
    result = load(result_dir/'validation-results.json')
    original_result = load(HERE/'results/validation-results.json')
    require(result['status'] == 'PASS', 'Acceptance workflow failed')
    require(result['semantic_reproduction_sha256'] == original_result['semantic_reproduction_sha256'],
            'Substantive reproduction discrepancy')
    comparisons = []
    for name in DETERMINISTIC:
        a,b = (HERE/'results'/name).read_bytes(), (result_dir/name).read_bytes()
        require(a == b, 'Deterministic artifact differs: ' + name)
        comparisons.append({'file':name,'historical_and_reproduced_sha256':sha(a),'byte_identical':True})
    # All copied research code/fixtures/results stay unchanged in the isolated run.
    for record in records:
        if record['relative_path'] != 'PREREGISTRATION.json':
            require(sha((version/record['relative_path']).read_bytes()) == record['derivative_sha256'],
                    'Isolated research file changed unexpectedly')
    verify_candidate()
    report = {'status':'PASS','scope':'Local publication-derivative reproduction, not external scientific validation',
        'publication_checksums_passed':count,'v02_tests':result['v02_tests'],'v01_tests':result['v01_tests'],
        'fixture_summary':result['fixture_summary'],'baseline':result['baseline'],
        'selected_defects_detected':result['selected_defects_detected'],
        'prior_survivors_detected':result['prior_survivors_detected'],
        'robustness_cases_passed':result['robustness_cases_passed'],
        'semantic_reproduction_sha256':result['semantic_reproduction_sha256'],
        'deterministic_artifacts':comparisons,'python':result['python'],'platform':result['platform'],
        'elapsed_seconds':result['elapsed_seconds'],'compatibility_record':'compatibility-record.json',
        'historical_records_rewritten':False,'source_repo_modified':False,'candidate_modified':False}
    save(output/'reproduction-summary.json',report)
    print(json.dumps({'status':'PASS','v02_tests':result['v02_tests']['tests_run'],
        'v01_tests':result['v01_tests']['tests_run'],'fixtures':result['fixture_summary']['total'],
        'defects_detected':result['selected_defects_detected'],'deterministic_files_identical':len(comparisons)}))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify-only',action='store_true')
    parser.add_argument('--baseline-repo',type=Path)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    if args.verify_only:
        _,count = verify_candidate()
        print(json.dumps({'status':'PASS','publication_checksums_passed':count}))
        return
    if args.baseline_repo is None or args.output is None:
        parser.error('--baseline-repo and --output are required for reproduction')
    execute(args.baseline_repo,args.output)

if __name__ == '__main__':
    main()
