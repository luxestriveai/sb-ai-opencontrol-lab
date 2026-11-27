import ast
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from baseline_adapter import Observer, load_subject, observe_claimed_workload
from validation_common import (HERE, REPO, evaluate_fixtures, protect_output, read_csv,
                               read_json, verify_baseline, verify_protocol)
from verifier import (NUMERIC, POLICIES, SCENARIOS, VALID, audit_dataset,
                      expected_keys, schedules, verify_trace)


class MeasurementAssuranceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        verify_baseline()
        verify_protocol()
        cls.corpus = read_json(HERE / 'fixtures/corpus.json')
        cls.runs = read_csv(REPO / 'results/runs.csv')
        cls.summary = read_csv(REPO / 'results/summary.csv')
        cls.json_summary = read_json(REPO / 'results/summary.json')
        cls.subject = load_subject(REPO / 'experiment.py')
        cls.traces = observe_claimed_workload(cls.subject, cls.runs)
        cls.baseline_audit = audit_dataset(cls.traces, cls.runs, cls.summary, cls.json_summary)
        if cls.baseline_audit['status'] != 'PASS':
            raise RuntimeError('SUBSTANTIVE_BASELINE_DISCREPANCY: ' + json.dumps(cls.baseline_audit['issue_examples']))

    def audit(self, runs=None, traces=None, summary=None, json_summary=None):
        return audit_dataset(self.traces if traces is None else traces,
                             self.runs if runs is None else runs,
                             self.summary if summary is None else summary,
                             self.json_summary if json_summary is None else json_summary)

    def test_01_frozen_artifacts_and_locked_protocol(self):
        self.assertEqual(verify_baseline()['status'], 'PASS')
        self.assertEqual(verify_protocol()['status'], 'PASS')

    def test_02_independent_checker_has_no_legacy_imports(self):
        tree = ast.parse((HERE / 'verifier.py').read_text(encoding='utf-8'))
        imports = []
        calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            if isinstance(node, ast.ImportFrom):
                imports.append(node.module or '')
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                calls.append(node.func.id)
        self.assertFalse(any('experiment' in name or 'baseline_adapter' in name for name in imports))
        self.assertFalse(set(calls) & {'audit_trace', 'evaluate', 'run'})
        self.assertFalse(any(isinstance(node, ast.Assert) for node in ast.walk(tree)))

    def test_03_fixed_corpus_counts_and_expected_classifications(self):
        self.assertEqual(len(self.corpus['fixtures']), 43)
        self.assertEqual(sum(c['evidence_valid'] for c in self.corpus['fixtures']), 17)
        for case in self.corpus['fixtures']:
            with self.subTest(fixture=case['id']):
                self.assertEqual(verify_trace(case['trace'])['classification'], case['expected_classification'])

    def test_04_fixed_fixture_metrics_and_policy_outcomes(self):
        result = evaluate_fixtures()
        self.assertEqual(result['status'], 'PASS', result['results'])
        self.assertEqual((result['false_safe'], result['false_rejection'], result['false_unsafe']), (0, 0, 0))

    def test_05_invalid_evidence_never_returns_metrics(self):
        for case in self.corpus['fixtures']:
            if not case['evidence_valid']:
                with self.subTest(fixture=case['id']):
                    self.assertIsNone(verify_trace(case['trace'])['metrics'])

    def test_06_negative_controls_include_safe_and_unsafe_valid_evidence(self):
        valid = [verify_trace(c['trace']) for c in self.corpus['fixtures'] if c['evidence_valid']]
        self.assertTrue(any(r['classification'] == 'VALID_UNSAFE' for r in valid))
        self.assertTrue(any(r['classification'] == 'VALID_SAFE' for r in valid))
        self.assertTrue(all(r['classification'] in VALID for r in valid))
        self.assertTrue(any(r['metrics']['denied_safe'] == 1 for r in valid))

    def test_07_optimized_python_same_complete_fixture_results(self):
        code = 'import json; from validation_common import evaluate_fixtures; print(json.dumps(evaluate_fixtures(), sort_keys=True))'
        process = subprocess.run([sys.executable, '-B', '-O', '-c', code], cwd=HERE,
                                 capture_output=True, text=True, timeout=30)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(json.loads(process.stdout), evaluate_fixtures())

    def test_08_independent_linear_extension_counts(self):
        counts = {'benign': 6, 'aggregate_limit': 6, 'revocation': 20,
                  'authority_outage': 45, 'shutdown': 20, 'combined': 3360}
        self.assertEqual({k: len(schedules(k)) for k in counts}, counts)
        self.assertEqual(len(expected_keys()), 10371)
        for name in counts:
            self.assertEqual(len(schedules(name)), len(set(schedules(name))))

    def test_09_observer_excludes_legacy_auditor_and_restores_it(self):
        subject = load_subject(REPO / 'experiment.py')
        def forbidden(*args):
            raise RuntimeError('Legacy auditor must not be used as oracle')
        subject.audit_trace = forbidden
        observation = Observer(subject).observe(subject.SCENARIOS[0],
                        ('prepare_A', 'commit_A', 'prepare_B', 'commit_B'), 'commit_guard')
        self.assertIs(subject.audit_trace, forbidden)
        self.assertEqual(verify_trace(observation)['metrics']['final_spent'], 70)

    def test_10_complete_original_workload_reconciles(self):
        self.assertEqual(self.baseline_audit['status'], 'PASS')
        self.assertEqual(self.baseline_audit['numeric_comparisons'], 114081)
        self.assertEqual(self.baseline_audit['classifications'], {'VALID_SAFE': 6891, 'VALID_UNSAFE': 3480})

    def test_11_equal_count_omission_and_duplicate_are_detected(self):
        altered = list(self.runs[1:]) + [self.runs[-1]]
        issues = self.audit(runs=altered)['issue_counts']
        self.assertIn('MISSING_RUN', issues)
        self.assertIn('DUPLICATE_RUN', issues)

    def test_12_missing_trace_detected_independently(self):
        issues = self.audit(traces=self.traces[1:])['issue_counts']
        self.assertIn('MISSING_TRACE', issues)

    def test_13_every_reported_run_numeric_field_checked(self):
        for field in NUMERIC:
            rows = list(self.runs)
            rows[0] = dict(rows[0], **{field: rows[0][field] + 1})
            with self.subTest(field=field):
                self.assertIn('RUN_METRIC_MISMATCH', self.audit(runs=rows)['issue_counts'])

    def test_14_csv_and_json_summary_checked_separately(self):
        altered = copy.deepcopy(self.summary)
        altered[0]['runs'] += 1
        self.assertIn('SUMMARY_METRIC_MISMATCH_CSV', self.audit(summary=altered)['issue_counts'])
        self.assertIn('SUMMARY_METRIC_MISMATCH_JSON', self.audit(json_summary=altered)['issue_counts'])

    def test_15_duplicate_missing_extra_summary_records(self):
        self.assertIn('DUPLICATE_SUMMARY_JSON', self.audit(json_summary=self.json_summary + [self.json_summary[0]])['issue_counts'])
        self.assertIn('MISSING_SUMMARY_CSV', self.audit(summary=self.summary[1:])['issue_counts'])
        changed = copy.deepcopy(self.summary)
        changed[0]['scenario'] = 'unregistered'
        self.assertIn('UNEXPECTED_SUMMARY_CSV', self.audit(summary=changed)['issue_counts'])

    def test_16_boolean_metric_is_not_integer(self):
        rows = list(self.runs)
        rows[0] = dict(rows[0], unsafe_run=False)
        self.assertIn('INVALID_RUN_METRIC', self.audit(runs=rows)['issue_counts'])

    def test_17_operation_identity_renaming_is_semantically_neutral(self):
        cases = {c['id']: c for c in self.corpus['fixtures']}
        a = verify_trace(cases['valid_benign_guard']['trace'])
        b = verify_trace(cases['valid_opaque_identity_renaming']['trace'])
        self.assertEqual(a, b)

    def test_18_conservation_across_original_workload(self):
        for row in self.baseline_audit['measured_runs']:
            self.assertEqual(row['commits'], row['safe_commits'] + row['unsafe_commits'])
            self.assertEqual(row['safe_opportunities'], row['safe_commits'] + row['denied_safe'])

    def test_19_non_overwriting_output_guard(self):
        with self.assertRaises(ValueError):
            protect_output(REPO / 'results')
        with self.assertRaises(ValueError):
            protect_output(HERE / 'results')
        with tempfile.TemporaryDirectory(prefix='opencontrol-output-guard-') as directory:
            with self.assertRaises(ValueError):
                protect_output(directory)
            self.assertEqual(protect_output(Path(directory) / 'new'), Path(directory).resolve() / 'new')

    def test_20_historical_mutations_match_archived_definitions(self):
        tree = ast.parse((HERE / 'evidence/prior/diagnostics.py.txt').read_text(encoding='utf-8'))
        definition = next(n for n in tree.body if isinstance(n, ast.Assign)
                          and any(isinstance(t, ast.Name) and t.id == 'mutations' for t in n.targets))
        entries = ast.literal_eval(definition.value)
        registry = read_json(HERE / 'fixtures/mutations.json')['mutations']
        self.assertEqual(len(entries), 10)
        self.assertEqual(entries, [(m['name'], m['old_fragment'], m['new_fragment']) for m in registry])
        self.assertTrue(all(m['definition_available'] and m['prior_copy_available'] for m in registry))

    def test_21_duplicate_json_object_keys_rejected(self):
        from validation_common import duplicate_safe_object
        with self.assertRaises(ValueError):
            duplicate_safe_object([('runs', 1), ('runs', 2)])

    def test_22_legacy_input_validation_weakness_covered_under_optimization(self):
        unknown = next(c['trace'] for c in self.corpus['fixtures'] if c['id'] == 'invalid_policy')
        self.assertEqual(verify_trace(unknown)['classification'], 'INVALID_INPUT')

    def test_23_missing_metric_rejected_not_coerced_to_zero(self):
        rows = list(self.runs)
        rows[0] = dict(rows[0])
        del rows[0]['budget_violations']
        self.assertIn('INVALID_RUN_SCHEMA', self.audit(runs=rows)['issue_counts'])


if __name__ == '__main__':
    unittest.main()

