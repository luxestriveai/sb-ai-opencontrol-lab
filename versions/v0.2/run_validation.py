"""Execute the fixed v0.2 acceptance protocol into a NEW external directory."""
import argparse
import csv
import gzip
import hashlib
import json
import platform
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from baseline_adapter import load_subject, observe_claimed_workload
from validation_common import (COMMIT, HERE, REPO, canonical, evaluate_fixtures, object_hash,
                               protect_output, read_csv, read_json, sha, verify_baseline,
                               verify_protocol, write_json)
from verifier import audit_dataset


class AcceptanceFailure(RuntimeError):
    pass


def check(condition, message):
    if not condition:
        raise AcceptanceFailure(message)


def transcript(path, process):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(process.stdout + process.stderr)


def suite(directory, output, new=False):
    command = [sys.executable, '-B', '-m', 'unittest']
    if new:
        command += ['discover', '-s', str(HERE), '-p', 'test_measurement.py', '-v', '-f']
    else:
        command += ['-v']
    process = subprocess.run(command, cwd=directory, capture_output=True, text=True, timeout=180)
    transcript(output, process)
    text = process.stdout + process.stderr
    count = re.search(r'Ran (\d+) tests in ([0-9.]+)s', text)
    return {'status': 'PASS' if process.returncode == 0 else 'FAIL', 'exit_code': process.returncode,
            'tests_run': int(count.group(1)) if count else None,
            'reported_elapsed_seconds': float(count.group(2)) if count else None}


def copy_subject(destination, source):
    destination.mkdir(parents=True, exist_ok=False)
    (destination / 'experiment.py').write_bytes(source)
    (destination / 'test_experiment.py').write_bytes((REPO / 'test_experiment.py').read_bytes())


def compact_audit(audit):
    return {key: value for key, value in audit.items() if key not in ('measured_runs', 'measured_summary')}


def traces_digest(traces):
    digest = hashlib.sha256()
    for trace in traces:
        digest.update(canonical(trace) + b'\n')
    return digest.hexdigest()


def save_traces(destination, traces):
    with destination.open('xb') as raw:
        with gzip.GzipFile(fileobj=raw, mode='wb', filename='', mtime=0) as stream:
            for trace in traces:
                stream.write(canonical(trace) + b'\n')


def save_csv(path, rows):
    with path.open('x', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def execute(output):
    started = time.perf_counter()
    started_at = datetime.now(ZoneInfo('America/New_York')).isoformat()
    preservation = verify_baseline()
    protocol = verify_protocol()
    output.mkdir(parents=True, exist_ok=False)
    try:
        write_json(output / 'baseline-integrity-before.json', preservation)
        fixtures = evaluate_fixtures()
        write_json(output / 'fixture-results.json', fixtures)
        check(fixtures['status'] == 'PASS' and fixtures['total'] == 43, 'FIXTURE_ACCEPTANCE_FAILED')
        code = 'import json; from validation_common import evaluate_fixtures; print(json.dumps(evaluate_fixtures(), sort_keys=True))'
        optimized = subprocess.run([sys.executable, '-B', '-O', '-c', code], cwd=HERE,
                                   capture_output=True, text=True, timeout=30)
        check(optimized.returncode == 0, 'OPTIMIZED_FIXTURE_PROCESS_FAILED')
        optimized_results = json.loads(optimized.stdout)
        write_json(output / 'optimized-fixture-results.json', optimized_results)
        check(optimized_results == fixtures, 'OPTIMIZED_FIXTURE_DISCREPANCY')
        print('Fixed normal/optimized fixture corpus: PASS', flush=True)

        unit = suite(REPO, output / 'v02-tests.txt', new=True)
        check(unit['status'] == 'PASS' and unit['tests_run'] == 23, 'V02_TEST_ACCEPTANCE_FAILED')
        original_source = (REPO / 'experiment.py').read_bytes()
        subject_dir = output / 'subjects' / 'baseline'
        copy_subject(subject_dir, original_source)
        legacy_unit = suite(subject_dir, output / 'v01-tests.txt')
        check(legacy_unit['status'] == 'PASS' and legacy_unit['tests_run'] == 8, 'FROZEN_TEST_ACCEPTANCE_FAILED')

        original_runs = read_csv(REPO / 'results/runs.csv')
        original_summary = read_csv(REPO / 'results/summary.csv')
        original_json = read_json(REPO / 'results/summary.json')
        subject = load_subject(subject_dir / 'experiment.py')
        runs, summaries = subject.evaluate()
        check(runs == original_runs and summaries == original_json, 'SUBSTANTIVE_ORIGINAL_REPRODUCTION_DISCREPANCY')
        observation_start = time.perf_counter()
        observed = observe_claimed_workload(subject, runs)
        baseline = audit_dataset(observed, original_runs, original_summary, original_json)
        baseline_runtime = time.perf_counter() - observation_start
        write_json(output / 'baseline-audit.json', compact_audit(baseline))
        check(baseline['status'] == 'PASS', 'SUBSTANTIVE_ORIGINAL_MEASUREMENT_DISCREPANCY')
        observed_again = observe_claimed_workload(subject, runs)
        baseline_again = audit_dataset(observed_again, original_runs, original_summary, original_json)
        trace_hash = traces_digest(observed)
        check(trace_hash == traces_digest(observed_again), 'BASELINE_TRACE_REPRODUCIBILITY_FAILED')
        check(baseline == baseline_again, 'BASELINE_MEASUREMENT_REPRODUCIBILITY_FAILED')
        save_traces(output / 'observed-traces.jsonl.gz', observed)
        save_csv(output / 'verified-runs.csv', baseline['measured_runs'])
        save_csv(output / 'verified-summary.csv', baseline['measured_summary'])
        write_json(output / 'verified-summary.json', baseline['measured_summary'])
        write_json(output / 'trace-reproducibility.json',
                   {'status': 'PASS', 'observations_per_pass': len(observed), 'passes': 2,
                    'canonical_trace_sha256': trace_hash, 'measurements_equal': True,
                    'gzip_sha256': sha(output / 'observed-traces.jsonl.gz')})
        del observed_again
        print('Complete original workload: PASS; two observations identical', flush=True)

        registry = read_json(HERE / 'fixtures/mutations.json')['mutations']
        mutations = []
        for definition in registry:
            name = definition['name']
            if not definition['definition_available']:
                mutations.append({'name': name, 'status': 'UNAVAILABLE', 'detected': False})
                continue
            source = original_source.decode('utf-8')
            check(source.count(definition['old_fragment']) == 1, 'AMBIGUOUS_HISTORICAL_MUTATION:' + name)
            altered = source.replace(definition['old_fragment'], definition['new_fragment'], 1).encode('utf-8')
            check(hashlib.sha256(altered).hexdigest() == definition['expected_mutant_sha256'], 'MUTATION_HASH_MISMATCH:' + name)
            directory = output / 'subjects' / name
            copy_subject(directory, altered)
            old_test = suite(directory, directory / 'legacy-tests.txt')
            historical_agreement = (old_test['status'] == 'PASS') == definition['historical_tests_passed']
            check(historical_agreement, 'HISTORICAL_TEST_OUTCOME_CHANGED:' + name)
            mutant = load_subject(directory / 'experiment.py')
            mutant_rows, mutant_summary = mutant.evaluate()
            # These are independent serialized exports of the subject's claims.
            save_csv(directory / 'runs.csv', mutant_rows)
            save_csv(directory / 'summary.csv', mutant_summary)
            write_json(directory / 'summary.json', mutant_summary)
            mutant_observed = observe_claimed_workload(mutant, mutant_rows)
            mutant_audit = audit_dataset(mutant_observed, read_csv(directory / 'runs.csv'),
                                         read_csv(directory / 'summary.csv'), read_json(directory / 'summary.json'))
            item = {'name': name, 'status': 'DETECTED' if mutant_audit['status'] == 'FAIL' else 'MISSED',
                    'detected': mutant_audit['status'] == 'FAIL',
                    'historical_tests_passed': definition['historical_tests_passed'],
                    'current_legacy_test_status': old_test['status'],
                    'historical_test_outcome_agrees': historical_agreement,
                    'mutant_sha256': hashlib.sha256(altered).hexdigest(),
                    'subject_run_count': len(mutant_rows), 'audit': compact_audit(mutant_audit)}
            mutations.append(item)
            write_json(directory / 'v02-detection.json', item)
            print('Selected mutation: ' + name + ' -> ' + item['status'], flush=True)
            check(item['detected'], 'SELECTED_DEFECT_NOT_DETECTED:' + name)
        write_json(output / 'mutation-results.json',
                   {'scope': 'Ten selected historical defects, not comprehensive mutation coverage',
                    'tested': sum(m['status'] != 'UNAVAILABLE' for m in mutations),
                    'detected': sum(m['detected'] for m in mutations),
                    'unavailable': [m['name'] for m in mutations if m['status'] == 'UNAVAILABLE'],
                    'mutations': mutations})
        check(len(mutations) == 10 and all(m['detected'] for m in mutations), 'SELECTED_CORPUS_ACCEPTANCE_FAILED')

        by_id = {item['id']: item for item in fixtures['results']}
        robustness = {
            'duplicate_event_labels': by_id['duplicate_event_label'],
            'incorrect_trace_amounts': by_id['incorrect_trace_amount'],
            'execution_following_invalid_preparation': by_id['valid_evidence_invalid_preparation_execution'],
            'invalid_negative_requests': by_id['invalid_negative_request'],
            'unknown_events': by_id['unknown_event'],
            'invalid_policy_under_optimized_execution': {
                **by_id['invalid_policy'], 'optimized_result_identical': optimized_results == fixtures},
            'missing_commit_traces': by_id['missing_commit_trace'],
        }
        write_json(output / 'robustness-results.json', robustness)
        after = verify_baseline()
        write_json(output / 'baseline-integrity-after.json', after)
        semantic = {
            'fixtures': fixtures,
            'baseline': compact_audit(baseline),
            'baseline_rows_sha256': object_hash(baseline['measured_runs']),
            'baseline_summary_sha256': object_hash(baseline['measured_summary']),
            'canonical_trace_sha256': trace_hash,
            'mutations': mutations,
            'robustness': robustness,
        }
        semantic_hash = object_hash(semantic)
        source_paths = sorted(HERE.glob('*.py')) + [HERE / 'fixtures/corpus.json', HERE / 'fixtures/mutations.json',
                                                   HERE / 'SPECIFICATION.md', HERE / 'PREREGISTRATION.json']
        result = {
            'status': 'PASS', 'started_at': started_at,
            'completed_at': datetime.now(ZoneInfo('America/New_York')).isoformat(),
            'timezone': 'America/New_York', 'python': sys.version, 'platform': platform.platform(),
            'output_directory': str(output), 'frozen_commit': COMMIT,
            'development_branch': preservation['branch'], 'protocol': protocol,
            'v02_tests': unit, 'v01_tests': legacy_unit,
            'fixture_summary': {k: v for k, v in fixtures.items() if k != 'results'},
            'optimized_fixture_results_identical': True,
            'baseline': compact_audit(baseline),
            'baseline_observation_and_audit_seconds': baseline_runtime,
            'baseline_trace_repeated_exactly': True, 'original_baseline_classification_discrepancies': 0,
            'original_artifact_checksums_passed': len(after['files']), 'original_manifest_unchanged': True,
            'selected_defects_tested': len(mutations), 'selected_defects_detected': sum(m['detected'] for m in mutations),
            'prior_survivors_detected': sum(m['historical_tests_passed'] and m['detected'] for m in mutations),
            'robustness_cases_passed': sum(r['status'] == 'PASS' for r in robustness.values()),
            'semantic_reproduction_sha256': semantic_hash,
            'source_sha256': {p.relative_to(HERE).as_posix(): sha(p) for p in source_paths},
            'elapsed_seconds': time.perf_counter() - started,
            'limitations': 'Finite development-visible corpus and trusted local instrumentation; no external validation, formal proof or real-world guarantee',
        }
        write_json(output / 'validation-results.json', result)
        print(json.dumps({'status': 'PASS', 'report': str(output / 'validation-results.json'),
                          'semantic_reproduction_sha256': semantic_hash,
                          'elapsed_seconds': result['elapsed_seconds']}, indent=2), flush=True)
        return 0
    except Exception as error:
        failure = {'status': 'FAIL', 'failure_type': type(error).__name__, 'failure': str(error),
                   'stopped_without_relaxing_acceptance': True,
                   'completed_at': datetime.now(ZoneInfo('America/New_York')).isoformat()}
        write_json(output / 'acceptance-failure.json', failure)
        print(json.dumps(failure, indent=2), flush=True)
        return 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True, help='New directory outside the Git repository')
    args = parser.parse_args()
    try:
        output = protect_output(args.output)
    except ValueError as error:
        parser.error(str(error))
    return execute(output)


if __name__ == '__main__':
    raise SystemExit(main())

