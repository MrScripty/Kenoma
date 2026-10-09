"""Synthetic subprocesses/files only. No numerical worker/material import."""
import copy, importlib.util, json, os, pathlib, sys, tempfile, time, unittest
path=pathlib.Path(__file__).resolve().parents[1]/'tools/arm-validation/watchdog.py'
spec=importlib.util.spec_from_file_location('arm_watchdog',path);w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
class WatchdogTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='kenoma-synthetic-guard-',dir='/tmp');self.root=pathlib.Path(self.tmp.name)
        self.cg=self.root/'fake-memory.current';self.cg.write_text('1')
        self.policy=copy.deepcopy(w.EXPECTED_POLICY);self.policy['aggregateWallSeconds']=5;self.policy['reservedReceiptBytes']=1024;self.policy['reservedTranscriptBytes']=4
        self.output=w.Output(self.root/'outputs',self.policy);self.run={**self.policy['runs'][0],'wallSeconds':1}
    def tearDown(self):self.tmp.cleanup()
    def run_child(self,code,run=None):return w.supervise([sys.executable,'-c',code],self.output,run or self.run,time.monotonic(),self.cg)
    def test_success_channel_and_disposal(self):
        p,r=self.run_child("import os,json;os.write(int(os.environ['KENOMA_RESULT_FD']),json.dumps({'status':'PASS','syntheticOnly':True}).encode())")
        self.assertEqual(p['status'],'PASS');self.assertTrue(p['syntheticOnly']);self.assertTrue(r['allProcessesReaped']);self.assertGreater(r['ownedPeakRSSBytes'],0)
    def test_wall_termination(self):
        p,r=self.run_child('while True:pass',{**self.run,'wallSeconds':.15});self.assertEqual(p['status'],'RESOURCE_INCONCLUSIVE');self.assertIn('Wall',p['reason']);self.assertTrue(r['allProcessesReaped'])
    def test_transcript_overflow(self):
        self.policy['perRunTranscriptBytes']=16
        p,r=self.run_child("import sys,time;sys.stdout.write('x'*100);sys.stdout.flush();time.sleep(2)")
        self.assertEqual(p['status'],'RESOURCE_INCONCLUSIVE');self.assertIn('Transcript',p['reason']);self.assertTrue(r['allProcessesReaped'])
    def test_result_staging_overflow(self):
        self.policy['perRunOutputBytes']=2048
        p,r=self.run_child("import os;os.write(int(os.environ['KENOMA_RESULT_FD']),b'x'*4000)")
        self.assertEqual(p['status'],'RESOURCE_INCONCLUSIVE');self.assertIn('ceiling',p['reason']);self.assertTrue(r['allProcessesReaped'])
    def test_owned_rss_termination(self):
        self.policy['ownedRSSBytes']=1
        with self.assertRaisesRegex(w.Refusal,'RSS'):self.run_child('import time;time.sleep(2)')
    def test_shared_cgroup_refusal_before_launch(self):
        self.cg.write_text(str(self.policy['cgroupBytes']+1))
        with self.assertRaisesRegex(w.Refusal,'cgroup'):self.run_child('raise Exception("must never launch")')
    def test_missing_monitor_refuses_before_launch(self):
        self.cg.unlink()
        with self.assertRaisesRegex(w.Refusal,'monitoring unavailable'):self.run_child('raise Exception("must never launch")')
    def test_unexpected_descendant_is_killed_and_reaped(self):
        p,r=self.run_child("import subprocess,sys,time;subprocess.Popen([sys.executable,'-c','import time;time.sleep(3)']);time.sleep(3)")
        self.assertEqual(p['status'],'RESOURCE_INCONCLUSIVE');self.assertIn('descendant',p['reason']);self.assertTrue(r['allProcessesReaped']);self.assertGreaterEqual(len(r['processIdentities']),3)
    def test_incomplete_channel_and_nonzero_exit_cannot_accept(self):
        p,_=self.run_child('pass');self.assertEqual(p['status'],'RESOURCE_INCONCLUSIVE')
        p,_=self.run_child('raise SystemExit(9)');self.assertEqual(p['status'],'RESOURCE_INCONCLUSIVE')
    def test_exclusive_destination_and_symlink_refusal(self):
        with self.assertRaises(FileExistsError):w.Output(self.output.path,self.policy)
        link=self.root/'link';link.symlink_to(self.output.path)
        with self.assertRaisesRegex(w.Refusal,'Symlink'):w.Output(link/'new',self.policy)
    def test_closed_inventory_and_foreign_file(self):
        self.output.write('manifest.json',b'{}','A');self.output.verify_inventory();(self.output.path/'foreign').write_text('x')
        with self.assertRaisesRegex(w.Refusal,'Foreign'):self.output.verify_inventory()
    def test_last_output_byte_and_emergency_reserve(self):
        self.policy['perRunOutputBytes']=1030;self.policy['aggregateOutputBytes']=5000
        self.output.write('manifest.json',b'x'*6,'A')
        with self.assertRaises(w.Refusal):self.output.write('rest-recheck.json',b'x','A')
        self.output.write('resource-receipt.json',b'failure','A',emergency=True)
    def test_finalization_combined_overflow_cannot_publish_acceptance(self):
        self.policy['perRunOutputBytes']=1100
        self.output.write('manifest.json',b'{}','A')
        results={r:{'status':'PASS','syntheticOnly':True,'large':'x'*70} for r in 'ABCD'}
        with self.assertRaises(w.Refusal):w.finalize(self.output,results,[],{'result':'SYNTHETIC'},'synthetic',time.monotonic())
        self.assertFalse((self.output.path/'resource-receipt.json').exists())
    def test_aggregate_deadline_checked_at_finalization(self):
        self.output.write('manifest.json',b'{}','A')
        with self.assertRaisesRegex(w.Refusal,'aggregate wall'):w.finalize(self.output,{},[],{'result':'SYNTHETIC'},'synthetic',time.monotonic()-6)
        self.assertFalse((self.output.path/'resource-receipt.json').exists())
    def test_comparison_control_recovery_refusal_and_mismatch(self):
        leaf={'receipt':{'r':1}};whole={'status':'PASS','finalState':{'t':1},'leaves':[leaf]};halves={'status':'PASS','finalState':{'t':1},'leaves':[leaf,leaf]};refused={'status':'SOLVER_REFUSAL'}
        self.assertEqual(w.compare(whole,whole,halves)['result'],'CONTROL_COMPATIBLE_REMEDY_UNPROVEN');self.assertIn('RECOVERY_SUPPORTED',w.compare(refused,halves,halves)['result']);self.assertIn('REFUSED',w.compare(refused,refused,refused)['result'])
        with self.assertRaises(w.Refusal):w.compare(refused,halves,whole)
    def test_finalize_has_detached_accounting_and_hashes(self):
        self.output.write('manifest.json',b'{}','A')
        result={r:{'status':'PASS','syntheticOnly':True} for r in 'ABCD'}
        receipt=w.finalize(self.output,result,[],{'result':'SYNTHETIC_TEST_ONLY'},'synthetic',time.monotonic(),self.cg)
        self.assertEqual(receipt['status'],'COMPLETE_FINALIZED')
        self.assertNotIn('resource-receipt.json',receipt['fileHashes'])
        self.assertEqual(json.loads((self.output.path/'resource-receipt.json').read_text()),receipt)
        self.output.charges['D']+=1
        self.assertNotEqual(receipt['perRunOutputBytesBeforeCommit']['D'],self.output.charges['D'])
    def test_final_memory_refusal_cannot_publish_commit(self):
        self.cg.write_text(str(self.policy['cgroupBytes']+1))
        with self.assertRaisesRegex(w.Refusal,'cgroup'):w.finalize(self.output,{},[],{},'synthetic',time.monotonic(),self.cg)
        self.assertFalse((self.output.path/'resource-receipt.json').exists())
    def test_stale_approval_refuses_before_manifest_or_worker_import(self):
        p=self.root/'manifest';p.write_text('{}')
        with self.assertRaisesRegex(w.Refusal,'approval'):w.execute(p,self.root/'never-created','0'*64)
        self.assertFalse((self.root/'never-created').exists());self.assertFalse(pathlib.Path(str(p)+'.executed').exists())
    def test_stale_policy_and_input_refuse(self):
        with self.assertRaisesRegex(w.Refusal,'source/policy'):w.validate_manifest({'schema':1},b'{}',False)
        m={'schema':1,'operatorCommit':'e57847418a13da39db78cbfcdba070c285f3bfde','inputCommit':'0b83819ad3fdaed7405c6bbe617bc01640eef914','policy':w.EXPECTED_POLICY,'inputs':{}}
        with self.assertRaisesRegex(w.Refusal,'input inventory'):w.validate_manifest(m,b'{}',False)
if __name__=='__main__':unittest.main()
