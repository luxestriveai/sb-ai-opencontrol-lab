"""OpenControl Lab v0.1: deterministic, synthetic containment experiment.
No external I/O, model calls, real resources, or attack tooling.
"""
from dataclasses import dataclass
from itertools import permutations
from collections import defaultdict
import argparse, csv, json
from pathlib import Path

CAP = 100
POLICIES = ('snapshot', 'shared_budget', 'commit_guard')
@dataclass(frozen=True)
class Scenario:
    name: str
    amounts: tuple[int, int]
    extra: tuple[str, ...] = ()
    order: tuple[tuple[str,str], ...] = ()

SCENARIOS = (
    Scenario('benign', (30,40)),
    Scenario('aggregate_limit', (60,60)),
    Scenario('revocation', (30,40), ('revoke_A',), (('prepare_A','revoke_A'),)),
    Scenario('authority_outage', (30,40), ('down','up'), (('prepare_A','down'),('down','up'))),
    Scenario('shutdown', (30,40), ('stop',), (('prepare_A','stop'),)),
    Scenario('combined', (60,60), ('revoke_A','down','up','stop'), (('prepare_A','revoke_A'),('down','up'))),
)

def schedules(s):
    events = ('prepare_A','commit_A','prepare_B','commit_B') + s.extra
    rules = (('prepare_A','commit_A'),('prepare_B','commit_B')) + s.order
    for p in permutations(events):
        ix = {e:i for i,e in enumerate(p)}
        if all(ix[a]<ix[b] for a,b in rules):
            yield p


def run(s, schedule, policy):
    assert policy in POLICIES
    amounts = dict(zip('AB',s.amounts))
    spent = 0; enabled = dict.fromkeys('AB',True); online=True; stopped=False
    tickets={}; trace=[]
    for event in schedule:
        if event=='down': online=False
        elif event=='up': online=True
        elif event=='stop': stopped=True
        elif event=='revoke_A': enabled['A']=False
        elif event.startswith('prepare_'):
            a=event[-1]; amount=amounts[a]
            # Same preparation rule for all policies, including current authority.
            tickets[a] = online and not stopped and enabled[a] and 0<amount<=CAP and spent+amount<=CAP
        elif event.startswith('commit_'):
            a=event[-1]; amount=amounts[a]
            if not tickets.pop(a,False): allowed=False; reason='no_ticket'
            elif policy in ('shared_budget','commit_guard') and spent+amount>CAP: allowed=False; reason='budget'
            elif policy=='commit_guard' and (not online or stopped or not enabled[a]): allowed=False; reason='authority'
            else: allowed=True; reason='approved'
            # The serialized simulation treats a check and update as one event.
            # This is a model assumption, not a claim of a real distributed atomic primitive.
            if allowed: spent+=amount
            trace.append(dict(event=event,allowed=allowed,reason=reason,amount=amount))
    # Independent trace replay: do not rely on decision code's safety classifications.
    audit=audit_trace(s,schedule,trace)
    return dict(scenario=s.name,policy=policy,schedule='|'.join(schedule),**audit,final_spent=spent)


def audit_trace(s,schedule,trace):
    decisions={x['event']:x for x in trace}
    committed=0; violations=defaultdict(int); denied_safe=0; safe_commits=0; safe_opportunities=0
    # Actual history, not a counterfactual optimal scheduler. A safe opportunity
    # requires valid authority at both prepare and commit and sufficient current budget.
    authorized={'A','B'}; online=True; stopped=False; prepared={}; spent=0
    for e in schedule:
        if e=='down': online=False
        elif e=='up': online=True
        elif e=='stop': stopped=True
        elif e=='revoke_A': authorized.discard('A')
        elif e.startswith('prepare_'):
            a=e[-1]; amount=s.amounts['AB'.index(a)]
            prepared[a]=online and not stopped and a in authorized and spent+amount<=CAP
        elif e.startswith('commit_'):
            d=decisions[e]; a=e[-1]; amount=d['amount']
            invalid=[]
            if spent+amount>CAP: invalid.append('budget')
            if a not in authorized: invalid.append('revoked')
            if not online: invalid.append('outage')
            if stopped: invalid.append('shutdown')
            safe=prepared[a] and not invalid
            safe_opportunities+=int(safe)
            if d['allowed']:
                committed+=1; spent+=amount
                for k in invalid: violations[k]+=1
                if invalid: violations['unsafe_commit']+=1
                if safe: safe_commits+=1
            elif safe: denied_safe+=1
    return dict(unsafe_run=int(violations['unsafe_commit']>0),unsafe_commits=violations['unsafe_commit'],
                budget_violations=violations['budget'],revocation_violations=violations['revoked'],
                outage_violations=violations['outage'],shutdown_violations=violations['shutdown'],
                commits=committed,safe_opportunities=safe_opportunities,safe_commits=safe_commits,denied_safe=denied_safe)


def evaluate():
    rows=[run(s,p,policy) for s in SCENARIOS for p in schedules(s) for policy in POLICIES]
    grouped=defaultdict(list)
    for row in rows: grouped[(row['scenario'],row['policy'])].append(row); grouped[('ALL',row['policy'])].append(row)
    keys=('unsafe_run','unsafe_commits','budget_violations','revocation_violations','outage_violations','shutdown_violations','commits','safe_opportunities','safe_commits','denied_safe')
    summary=[]
    for (scenario,policy),group in grouped.items():
        summary.append(dict(scenario=scenario,policy=policy,runs=len(group),**{k:sum(r[k] for r in group) for k in keys}))
    return rows,summary


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path,default=Path('results')); args=parser.parse_args()
    rows,summary=evaluate(); args.output.mkdir(parents=True,exist_ok=True)
    for name,data in [('runs.csv',rows),('summary.csv',summary)]:
        with (args.output/name).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0])); w.writeheader(); w.writerows(data)
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    for r in summary:
        if r['scenario']=='ALL': print(r)
if __name__=='__main__': main()
