import unittest
from experiment import SCENARIOS, POLICIES, schedules, run, evaluate

class ContainmentTests(unittest.TestCase):
    def test_schedule_uniqueness_and_order(self):
        for s in SCENARIOS:
            ps=list(schedules(s)); self.assertTrue(ps); self.assertEqual(len(ps),len(set(ps)))
            for p in ps:
                for a,b in (('prepare_A','commit_A'),('prepare_B','commit_B'))+s.order:
                    self.assertLess(p.index(a),p.index(b))
    def test_benign_completion(self):
        s=SCENARIOS[0]
        for p in schedules(s):
            for policy in POLICIES:
                r=run(s,p,policy); self.assertEqual(r['commits'],2); self.assertEqual(r['unsafe_run'],0)
    def test_aggregate_counterexample(self):
        s=SCENARIOS[1]; p=('prepare_A','prepare_B','commit_A','commit_B')
        self.assertEqual(run(s,p,'snapshot')['final_spent'],120)
        self.assertEqual(run(s,p,'shared_budget')['final_spent'],60)
        self.assertEqual(run(s,p,'commit_guard')['final_spent'],60)
    def test_revocation_counterexample(self):
        s=SCENARIOS[2]; p=('prepare_A','revoke_A','commit_A','prepare_B','commit_B')
        self.assertEqual(run(s,p,'shared_budget')['revocation_violations'],1)
        self.assertEqual(run(s,p,'commit_guard')['revocation_violations'],0)
    def test_outage_counterexample(self):
        s=SCENARIOS[3]; p=('prepare_A','down','commit_A','up','prepare_B','commit_B')
        self.assertEqual(run(s,p,'shared_budget')['outage_violations'],1)
        self.assertEqual(run(s,p,'commit_guard')['outage_violations'],0)
    def test_shutdown_counterexample(self):
        s=SCENARIOS[4]; p=('prepare_A','stop','commit_A','prepare_B','commit_B')
        self.assertEqual(run(s,p,'shared_budget')['shutdown_violations'],1)
        self.assertEqual(run(s,p,'commit_guard')['shutdown_violations'],0)
    def test_all_schedules(self):
        rows,_=evaluate(); self.assertTrue(any(r['unsafe_run'] for r in rows if r['policy']=='snapshot'))
        self.assertTrue(any(r['unsafe_run'] for r in rows if r['policy']=='shared_budget'))
        for r in rows:
            if r['policy']=='commit_guard':
                self.assertEqual(r['unsafe_run'],0); self.assertLessEqual(r['final_spent'],100); self.assertEqual(r['denied_safe'],0)
    def test_equal_workload(self):
        rows,_=evaluate(); sets={p:{(r['scenario'],r['schedule']) for r in rows if r['policy']==p} for p in POLICIES}
        self.assertTrue(all(s==sets[POLICIES[0]] for s in sets.values()))
if __name__=='__main__': unittest.main()
