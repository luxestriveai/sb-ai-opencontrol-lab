"""Independent finite-contract measurement checker. No legacy simulator imports."""
from collections import Counter
from functools import lru_cache

POLICIES = ('snapshot', 'shared_budget', 'commit_guard')
BASE_EVENTS = ('prepare_A', 'commit_A', 'prepare_B', 'commit_B')
BASE_ORDER = (('prepare_A', 'commit_A'), ('prepare_B', 'commit_B'))
SCENARIOS = {
    'benign': ((30, 40), (), ()),
    'aggregate_limit': ((60, 60), (), ()),
    'revocation': ((30, 40), ('revoke_A',), (('prepare_A', 'revoke_A'),)),
    'authority_outage': ((30, 40), ('down', 'up'), (('prepare_A', 'down'), ('down', 'up'))),
    'shutdown': ((30, 40), ('stop',), (('prepare_A', 'stop'),)),
    'combined': ((60, 60), ('revoke_A', 'down', 'up', 'stop'),
                 (('prepare_A', 'revoke_A'), ('down', 'up'))),
}
COUNTERS = ('unsafe_run', 'unsafe_commits', 'budget_violations', 'revocation_violations',
            'outage_violations', 'shutdown_violations', 'commits', 'safe_opportunities',
            'safe_commits', 'denied_safe')
NUMERIC = COUNTERS + ('final_spent',)
RUN_FIELDS = {'scenario', 'policy', 'schedule', *NUMERIC}
SUMMARY_FIELDS = {'scenario', 'policy', 'runs', *COUNTERS}
COMMON = {'id', 'event', 'balance_before', 'balance_after'}
PREPARE_FIELDS = COMMON | {'operation_id', 'actor', 'amount', 'ticket_issued'}
COMMIT_FIELDS = COMMON | {'operation_id', 'actor', 'amount', 'executed', 'effect_amount', 'reason'}
ENVELOPE = {'schema', 'scenario', 'policy', 'requests', 'events', 'observed_final_balance'}
VALID = {'VALID_SAFE', 'VALID_UNSAFE'}


class EvidenceError(ValueError):
    def __init__(self, classification, code):
        self.classification, self.code = classification, code
        super().__init__(code)


def require(condition, classification, code):
    if not condition:
        raise EvidenceError(classification, code)


def integer(value, minimum=0):
    return type(value) is int and value >= minimum


def identifier(value):
    return type(value) is str and 0 < len(value) <= 256


def exact_fields(value, fields):
    require(type(value) is dict, 'INVALID_TRACE', 'EVENT_NOT_OBJECT')
    require(not (set(value) - fields), 'INVALID_TRACE', 'UNSUPPORTED_EVENT_FIELD')
    require(fields <= set(value), 'INSUFFICIENT_EVIDENCE', 'MISSING_EVENT_FIELD')


@lru_cache(maxsize=None)
def schedules(scenario):
    """Direct linear-extension search: no permutation/filter implementation."""
    if scenario not in SCENARIOS:
        raise ValueError('Unknown independently specified scenario')
    _, extras, ordering = SCENARIOS[scenario]
    events = BASE_EVENTS + extras
    prerequisites = {name: set() for name in events}
    for first, second in BASE_ORDER + ordering:
        prerequisites[second].add(first)
    found = []
    def walk(prefix, remaining):
        if not remaining:
            found.append(tuple(prefix))
            return
        done = set(prefix)
        for name in sorted(remaining):
            if prerequisites[name] <= done:
                walk(prefix + [name], remaining - {name})
    walk([], set(events))
    return tuple(found)


@lru_cache(maxsize=1)
def expected_keys():
    return frozenset((name, policy, '|'.join(events))
                     for name in SCENARIOS for events in schedules(name) for policy in POLICIES)


def verify_trace(trace):
    try:
        return _verify_trace(trace)
    except EvidenceError as error:
        return {'classification': error.classification, 'metrics': None,
                'policy_conformant': None, 'policy_deviations': [],
                'diagnostics': [error.code], 'run_key': None}


def _verify_trace(t):
    require(type(t) is dict, 'INVALID_INPUT', 'ENVELOPE_NOT_OBJECT')
    require(not (set(t) - ENVELOPE), 'INVALID_INPUT', 'UNSUPPORTED_ENVELOPE_FIELD')
    require(ENVELOPE <= set(t), 'INSUFFICIENT_EVIDENCE', 'MISSING_ENVELOPE_FIELD')
    require(t['schema'] == 'opencontrol/0.2', 'INVALID_INPUT', 'UNKNOWN_SCHEMA')
    require(type(t['scenario']) is str and t['scenario'] in SCENARIOS, 'INVALID_INPUT', 'UNKNOWN_SCENARIO')
    require(type(t['policy']) is str and t['policy'] in POLICIES, 'INVALID_INPUT', 'UNKNOWN_POLICY')
    req = t['requests']
    require(type(req) is dict and set(req) == {'A', 'B'}, 'INVALID_INPUT', 'INVALID_REQUEST_MAP')
    require(all(integer(v, 1) and v <= 100 for v in req.values()), 'INVALID_INPUT', 'INVALID_REQUEST_AMOUNT')
    amounts, extras, order = SCENARIOS[t['scenario']]
    require((req['A'], req['B']) == amounts, 'INVALID_INPUT', 'REQUEST_OUTSIDE_CONTRACT')
    events = t['events']
    require(type(events) is list, 'INVALID_TRACE', 'EVENTS_NOT_LIST')
    allowed_names = set(BASE_EVENTS + extras)
    seen_ids, names = set(), []
    for event in events:
        require(type(event) is dict, 'INVALID_TRACE', 'EVENT_NOT_OBJECT')
        require('event' in event, 'INSUFFICIENT_EVIDENCE', 'MISSING_EVENT_NAME')
        name = event['event']
        require(type(name) is str and name in allowed_names, 'INVALID_TRACE', 'UNSUPPORTED_EVENT')
        fields = PREPARE_FIELDS if name.startswith('prepare_') else COMMIT_FIELDS if name.startswith('commit_') else COMMON
        exact_fields(event, fields)
        require(identifier(event['id']), 'INVALID_TRACE', 'INVALID_EVENT_ID')
        require(event['id'] not in seen_ids, 'INVALID_TRACE', 'DUPLICATE_EVENT_ID')
        seen_ids.add(event['id'])
        require(name not in names, 'INVALID_TRACE', 'DUPLICATE_EVENT_LABEL')
        names.append(name)
        require(integer(event['balance_before']) and integer(event['balance_after']), 'INVALID_TRACE', 'INVALID_BALANCE_TYPE')
        if fields != COMMON:
            require(event['actor'] == name[-1], 'INVALID_TRACE', 'ACTOR_MISMATCH')
            require(identifier(event['operation_id']), 'INVALID_TRACE', 'INVALID_OPERATION_ID')
            require(integer(event['amount'], 1) and event['amount'] == req[name[-1]], 'INVALID_TRACE', 'REQUEST_PAYLOAD_MISMATCH')
        if fields == PREPARE_FIELDS:
            require(type(event['ticket_issued']) is bool, 'INVALID_TRACE', 'INVALID_TICKET_TYPE')
        if fields == COMMIT_FIELDS:
            require(type(event['executed']) is bool, 'INVALID_TRACE', 'INVALID_EXECUTION_TYPE')
            require(integer(event['effect_amount']), 'INVALID_TRACE', 'INVALID_EFFECT_TYPE')
            require(event['effect_amount'] == (event['amount'] if event['executed'] else 0),
                    'INVALID_TRACE', 'EFFECT_PAYLOAD_MISMATCH')
            require(type(event['reason']) is str and event['reason'] in
                    {'approved', 'no_ticket', 'budget', 'authority', 'declined'},
                    'INVALID_TRACE', 'UNKNOWN_DECISION_REASON')
            require((event['reason'] == 'approved') == event['executed'], 'INVALID_TRACE', 'DECISION_REASON_CONTRADICTION')
    require(set(names) == allowed_names, 'INSUFFICIENT_EVIDENCE', 'MISSING_REQUIRED_EVENT')
    positions = {name: index for index, name in enumerate(names)}  # grammar only, never decision identity
    require(all(positions[a] < positions[b] for a, b in BASE_ORDER + order), 'INVALID_TRACE', 'ILLEGAL_EVENT_ORDER')
    require(integer(t['observed_final_balance']), 'INVALID_TRACE', 'INVALID_FINAL_BALANCE')
    infinity = len(events) + 1
    ledger = 0
    operations, actor_operations = {}, {}
    metrics = dict.fromkeys(NUMERIC + ('preparation_violations',), 0)
    deviations = []
    for index, event in enumerate(events):
        name = event['event']
        require(event['balance_before'] == ledger, 'INVALID_TRACE', 'LEDGER_DISCONTINUITY')
        if name.startswith(('prepare_', 'commit_')):
            actor, amount, op_id = event['actor'], event['amount'], event['operation_id']
            current = []
            if ledger + amount > 100:
                current.append('budget_violations')
            if actor == 'A' and positions.get('revoke_A', infinity) < index:
                current.append('revocation_violations')
            if positions.get('down', infinity) < index < positions.get('up', infinity):
                current.append('outage_violations')
            if positions.get('stop', infinity) < index:
                current.append('shutdown_violations')
            if name.startswith('prepare_'):
                require(op_id not in operations and actor not in actor_operations, 'INVALID_TRACE', 'OPERATION_ID_COLLISION')
                eligible = not current
                operations[op_id] = {'actor': actor, 'amount': amount, 'eligible': eligible,
                                     'issued': event['ticket_issued'], 'used': False}
                actor_operations[actor] = op_id
                if event['ticket_issued'] != eligible:
                    deviations.append({'event_id': event['id'], 'code': 'PREPARATION_POLICY_MISMATCH'})
            else:
                require(op_id in operations and actor_operations.get(actor) == op_id, 'INVALID_TRACE', 'UNKNOWN_OPERATION')
                operation = operations[op_id]
                require(not operation['used'] and operation['actor'] == actor and operation['amount'] == amount,
                        'INVALID_TRACE', 'OPERATION_BINDING_MISMATCH')
                operation['used'] = True
                usable = operation['eligible'] and operation['issued']
                safe = usable and not current
                metrics['safe_opportunities'] += int(safe)
                policy = t['policy']
                if not operation['issued']:
                    expected_execution, expected_reason = False, 'no_ticket'
                elif policy != 'snapshot' and 'budget_violations' in current:
                    expected_execution, expected_reason = False, 'budget'
                elif policy == 'commit_guard' and any(x != 'budget_violations' for x in current):
                    expected_execution, expected_reason = False, 'authority'
                else:
                    expected_execution, expected_reason = True, 'approved'
                if event['executed'] != expected_execution or event['reason'] != expected_reason:
                    deviations.append({'event_id': event['id'], 'code': 'COMMIT_POLICY_MISMATCH'})
                if event['executed']:
                    ledger += event['effect_amount']
                    metrics['commits'] += 1
                    violations = current + ([] if usable else ['preparation_violations'])
                    for category in violations:
                        metrics[category] += 1
                    metrics['unsafe_commits'] += int(bool(violations))
                    metrics['safe_commits'] += int(safe)
                elif safe:
                    metrics['denied_safe'] += 1
        require(event['balance_after'] == ledger, 'INVALID_TRACE', 'LEDGER_EFFECT_MISMATCH')
    require(t['observed_final_balance'] == ledger, 'INVALID_TRACE', 'FINAL_BALANCE_MISMATCH')
    require(all(op['used'] for op in operations.values()), 'INSUFFICIENT_EVIDENCE', 'UNCONSUMED_OPERATION')
    metrics['final_spent'] = ledger
    metrics['unsafe_run'] = int(metrics['unsafe_commits'] > 0)
    # These identities are checked, not assumed from the legacy reported metrics.
    require(metrics['safe_commits'] + metrics['unsafe_commits'] == metrics['commits'], 'INVALID_TRACE', 'COMMIT_ACCOUNTING_FAILURE')
    require(metrics['safe_commits'] + metrics['denied_safe'] == metrics['safe_opportunities'], 'INVALID_TRACE', 'OPPORTUNITY_ACCOUNTING_FAILURE')
    return {'classification': 'VALID_UNSAFE' if metrics['unsafe_run'] else 'VALID_SAFE',
            'metrics': metrics, 'policy_conformant': not deviations, 'policy_deviations': deviations,
            'diagnostics': [], 'run_key': (t['scenario'], t['policy'], '|'.join(names))}


def summarize(rows):
    groups = {}
    for row in rows:
        for scenario in (row['scenario'], 'ALL'):
            key = (scenario, row['policy'])
            if key not in groups:
                groups[key] = {'scenario': scenario, 'policy': row['policy'],
                               'runs': 0, **dict.fromkeys(COUNTERS, 0)}
            target = groups[key]
            target['runs'] += 1
            for field in COUNTERS:
                target[field] += row[field]
    return [groups[key] for key in sorted(groups)]


def audit_dataset(traces, reported_runs, reported_summary, reported_json):
    """Full-set coverage and independent trace-to-CSV/JSON reconciliation."""
    counts, examples = Counter(), []
    def issue(code, key=None, detail=None):
        counts[code] += 1
        if len(examples) < 30:
            examples.append({'code': code, 'key': key, 'detail': detail})
    expected = expected_keys()
    run_map = {}
    for row in reported_runs:
        if type(row) is not dict or set(row) != RUN_FIELDS:
            issue('INVALID_RUN_SCHEMA')
            continue
        if not all(type(row[k]) is str for k in ('scenario', 'policy', 'schedule')):
            issue('INVALID_RUN_KEY')
            continue
        key = row['scenario'], row['policy'], row['schedule']
        if not all(integer(row[field]) for field in NUMERIC):
            issue('INVALID_RUN_METRIC', key)
        if key in run_map:
            issue('DUPLICATE_RUN', key)
        run_map[key] = row
    for key in sorted(expected - set(run_map)):
        issue('MISSING_RUN', key)
    for key in sorted(set(run_map) - expected):
        issue('UNEXPECTED_RUN', key)

    trace_keys, classifications, measured = set(), Counter(), []
    numeric_comparisons = 0
    for trace in traces:
        verdict = verify_trace(trace)
        classifications[verdict['classification']] += 1
        if verdict['classification'] not in VALID:
            issue('INVALID_TRACE_EVIDENCE', detail=verdict['diagnostics'])
            continue
        key = verdict['run_key']
        if key in trace_keys:
            issue('DUPLICATE_TRACE', key)
        trace_keys.add(key)
        if key not in expected:
            issue('UNEXPECTED_TRACE', key)
        if not verdict['policy_conformant']:
            issue('POLICY_NONCONFORMANCE', key, verdict['policy_deviations'])
        record = {'scenario': key[0], 'policy': key[1], 'schedule': key[2],
                  **{k: verdict['metrics'][k] for k in NUMERIC}}
        measured.append(record)
        reported = run_map.get(key)
        if reported is not None:
            for field in NUMERIC:
                numeric_comparisons += 1
                if type(reported[field]) is not int or reported[field] != record[field]:
                    issue('RUN_METRIC_MISMATCH', key, field)
    for key in sorted(expected - trace_keys):
        issue('MISSING_TRACE', key)
    aggregate = summarize(measured)
    aggregate_map = {(r['scenario'], r['policy']): r for r in aggregate}
    for label, claims in (('CSV', reported_summary), ('JSON', reported_json)):
        claim_map = {}
        if type(claims) is not list:
            issue('INVALID_SUMMARY_' + label)
            continue
        for row in claims:
            if type(row) is not dict or set(row) != SUMMARY_FIELDS:
                issue('INVALID_SUMMARY_SCHEMA_' + label)
                continue
            if type(row['scenario']) is not str or type(row['policy']) is not str:
                issue('INVALID_SUMMARY_KEY_' + label)
                continue
            key = row['scenario'], row['policy']
            if key in claim_map:
                issue('DUPLICATE_SUMMARY_' + label, key)
            claim_map[key] = row
            expected_row = aggregate_map.get(key)
            if expected_row is None:
                issue('UNEXPECTED_SUMMARY_' + label, key)
            elif any(type(row[k]) is not int or row[k] != expected_row[k] for k in ('runs',) + COUNTERS):
                issue('SUMMARY_METRIC_MISMATCH_' + label, key)
        for key in sorted(set(aggregate_map) - set(claim_map)):
            issue('MISSING_SUMMARY_' + label, key)
    coverage = {name: {'expected_schedules': len(schedules(name)),
                       'observed_run_keys': sum(key[0] == name for key in run_map),
                       'observed_trace_keys': sum(key[0] == name for key in trace_keys)}
                for name in SCENARIOS}
    return {'status': 'PASS' if not counts else 'FAIL', 'issue_counts': dict(counts),
            'issue_examples': examples, 'classifications': dict(classifications),
            'expected_run_keys': len(expected), 'observed_run_keys': len(run_map),
            'observed_trace_keys': len(trace_keys), 'numeric_comparisons': numeric_comparisons,
            'coverage': coverage, 'measured_runs': measured, 'measured_summary': aggregate}

