"""Read-only observer of the legacy executor, not a classification oracle."""
import ast
import importlib.util
import sys
from itertools import count
from pathlib import Path

_NAMES = count()


def load_subject(path):
    path = Path(path)
    name = '_opencontrol_subject_' + str(next(_NAMES))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclass annotation resolution
    spec.loader.exec_module(module)
    return module


class Observer:
    """Capture actual balances/tickets/decisions at loop boundaries in unedited code."""
    def __init__(self, module):
        self.module = module
        tree = ast.parse(Path(module.__file__).read_text(encoding='utf-8'))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'run')
        loops = [(i, node) for i, node in enumerate(function.body) if isinstance(node, ast.For)]
        if len(loops) != 1 or not isinstance(loops[0][1].target, ast.Name) or loops[0][1].target.id != 'event':
            raise ValueError('Unsupported observation layout')
        index, loop = loops[0]
        self.begin_line = loop.body[0].lineno
        self.end_line = function.body[index + 1].lineno
        self.code = module.run.__code__

    def observe(self, scenario, schedule, policy):
        observations = []
        pending = None
        def finish(local):
            nonlocal pending
            if pending is None:
                return
            name, before = pending
            after = local['spent']
            item = {'id': 'event-' + str(len(observations)), 'event': name,
                    'balance_before': before, 'balance_after': after}
            if name.startswith('prepare_'):
                actor = name[-1]
                item.update(operation_id='operation-' + actor, actor=actor,
                            amount=local['amounts'][actor], ticket_issued=local['tickets'][actor])
            elif name.startswith('commit_'):
                actor = name[-1]
                decisions = local['trace']
                if not decisions or decisions[-1]['event'] != name:
                    raise ValueError('Missing executor commit observation')
                decision = decisions[-1]
                item.update(operation_id='operation-' + actor, actor=actor, amount=decision['amount'],
                            executed=decision['allowed'], effect_amount=after - before,
                            reason=decision['reason'])
            observations.append(item)
            pending = None
        def trace(frame, event, arg):
            nonlocal pending
            if frame.f_code is not self.code:
                return None
            if event == 'line' and frame.f_lineno in (self.begin_line, self.end_line):
                finish(frame.f_locals)
                if frame.f_lineno == self.begin_line:
                    pending = (frame.f_locals['event'], frame.f_locals['spent'])
            return trace
        previous_tracer = sys.gettrace()
        original_audit = self.module.audit_trace
        try:
            # The old auditor is explicitly excluded from observation/classification.
            self.module.audit_trace = lambda *args: {}
            sys.settrace(trace)
            self.module.run(scenario, schedule, policy)
        finally:
            sys.settrace(previous_tracer)
            self.module.audit_trace = original_audit
        if pending is not None or len(observations) != len(schedule):
            raise ValueError('Incomplete observation')
        return {'schema': 'opencontrol/0.2', 'scenario': scenario.name, 'policy': policy,
                'requests': dict(zip('AB', scenario.amounts)), 'events': observations,
                'observed_final_balance': observations[-1]['balance_after'] if observations else 0}


def observe_claimed_workload(module, rows):
    """Only execute rows the subject claims; independent coverage detects omissions."""
    observer = Observer(module)
    scenarios = {scenario.name: scenario for scenario in module.SCENARIOS}
    return [observer.observe(scenarios[row['scenario']], tuple(row['schedule'].split('|')), row['policy'])
            for row in rows]

