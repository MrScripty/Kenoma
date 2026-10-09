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
        results={r:{'status':'PASS','syntheticOnly':True,'large':'x'*70} for r in w.RUN_IDS}
        with self.assertRaises(w.Refusal):w.finalize(self.output,results,[],{'result':'SYNTHETIC'},'synthetic',time.monotonic(),self.cg)
        self.assertFalse((self.output.path/'resource-receipt.json').exists())
    def test_aggregate_deadline_checked_at_finalization(self):
        self.output.write('manifest.json',b'{}','A')
        with self.assertRaisesRegex(w.Refusal,'aggregate wall'):w.finalize(self.output,{},[],{'result':'SYNTHETIC'},'synthetic',time.monotonic()-6,self.cg)
        self.assertFalse((self.output.path/'resource-receipt.json').exists())
    def baseline(self):
        import subprocess
        text=subprocess.check_output(['node','--input-type=module','-e',"import {retainedBaseline} from './education/tools/arm-validation/prepare.mjs';process.stdout.write(JSON.stringify(retainedBaseline()))"],cwd=w.ROOT)
        return json.loads(text)
    def test_independent_comparison_preserves_resource_failure_and_no_adaptive_claim(self):
        leaf={'receipt':{'r':1}};whole={'status':'PASS','finalState':{'t':1},'leaves':[leaf]};halves={'status':'PASS','finalState':{'t':1},'leaves':[leaf,leaf]};refused={'status':'SOLVER_REFUSAL'};timeout={'status':'RESOURCE_INCONCLUSIVE'}
        self.assertEqual(w.compare(whole,halves)['result'],'BOTH_DISCRETIZATIONS_COMPLETED_NO_RECOVERY_CLAIM')
        self.assertEqual(w.compare(timeout,halves)['result'],'HALF_STEP_WORKER_PASS_DEFAULT_RESOURCE_INCONCLUSIVE_NO_ACCEPTANCE')
        self.assertEqual(w.compare(None,timeout)['defaultWorkerStatus'],'SKIPPED_NOT_RUN')
        self.assertFalse(w.compare(refused,halves)['adaptiveRecoveryClaim'])
        with self.assertRaises(w.Refusal):w.compare(whole,whole)
    def test_policy_order_places_fresh_half_steps_before_default(self):
        self.assertEqual([r['id'] for r in w.EXPECTED_POLICY['runs']],['A','D','B'])
        self.assertEqual(sum(r['attempts'] for r in w.EXPECTED_POLICY['runs']),3)
        self.assertEqual(sum(r['configurationEntries'] for r in w.EXPECTED_POLICY['runs']),1025)
        self.assertEqual(sum(r['wallSeconds'] for r in w.EXPECTED_POLICY['runs']),540)
    def test_actual_supervisor_dispatches_halves_before_default_timeout_without_physical_worker(self):
        from unittest.mock import patch
        policy=copy.deepcopy(self.policy);policy['claimDirectory']=str(self.root/'synthetic-claims')
        dest=self.root/'synthetic-execute';m={'policy':policy,'executionDestination':str(dest),'harnessFiles':{},'operatorCommit':'SYNTHETIC_NO_PHYSICS','harnessCommit':'SYNTHETIC_NO_PHYSICS','scope':'SYNTHETIC_TEST_ONLY','inputCommit':'SYNTHETIC_NO_PHYSICS','inputs':{'generated/arm-reference.json':{'sha256':'synthetic'},'audit/arm-rest-results.json':{'sha256':'synthetic','text':json.dumps({'state':{'coordinatesM':[0]*460,'timeS':0}})}},'cameraSHA256':'synthetic'}
        raw=w.encoded(m);manifest=self.root/'synthetic-manifest.json';manifest.write_bytes(raw);calls=[]
        def fake_supervise(command,output,run,start,cgroup,**kwargs):
            calls.append(run['id'])
            packet={'status':'RESOURCE_INCONCLUSIVE','reason':'Wall deadline/cleanup reserve','finalAcceptance':False} if run['id']=='B' else {'status':'PASS','workerStatus':'PROVISIONAL_PENDING_SUPERVISOR','finalAcceptance':False,'run':run['id'],'sourceCommit':m['operatorCommit'],'harnessCommit':m['harnessCommit'],'executionScope':m['scope'],'anatomicalQualification':False,'numericalCandidateAccepted':True,'counters':{'executed':{k:0 for k in w.CLASSES},'latched':False},'modelDisposed':True,'syntheticOnly':True}
            return packet,{'run':run['id'],'allProcessesReaped':True,'startOffsetSeconds':0,'ownedPeakRSSBytes':0,'observedCgroupPeakBytes':1}
        with patch.object(w,'validate_manifest',return_value='NEVER_LAUNCHED'),patch.object(w,'cgroup_file',return_value=self.cg),patch.object(w,'supervise',side_effect=fake_supervise):
            receipt=w.execute(manifest,dest,w.digest(raw))
        self.assertEqual(calls,['A','D','B']);self.assertEqual(receipt['status'],'RESOURCE_INCONCLUSIVE')
        self.assertEqual(receipt['authoritativeFinalAcceptance'],{k:False for k in w.RUN_IDS})
        self.assertEqual(json.loads((dest/'explicit-halves.json').read_text())['payload']['status'],'PASS')
        self.assertEqual(json.loads((dest/'default.json').read_text())['payload']['status'],'RESOURCE_INCONCLUSIVE')
        self.assertEqual(json.loads((dest/'comparison.json').read_text())['result'],'HALF_STEP_WORKER_PASS_DEFAULT_RESOURCE_INCONCLUSIVE_NO_ACCEPTANCE')
        self.assertTrue((self.root/'synthetic-claims'/(w.digest(raw)+'.executed')).exists())
        self.assertFalse((dest/'adaptive-depth1.json').exists())
    def test_retained_baseline_tamper_refuses_without_launch(self):
        b=self.baseline();w.validate_baseline({'baselineEvidence':b})
        b['files']['default.json']['text']+=' '
        with self.assertRaisesRegex(w.Refusal,'baseline'):w.validate_baseline({'baselineEvidence':b})
    def test_default_timeout_cannot_erase_prior_halves_or_commit_acceptance(self):
        self.output.write('manifest.json',b'{}','A')
        results={'A':{'status':'PASS'},'D':{'status':'PASS','sentinel':'retained_half_steps'},'B':{'status':'RESOURCE_INCONCLUSIVE','reason':'Wall deadline/cleanup reserve'}}
        receipt=w.finalize(self.output,results,[],w.compare(results['B'],results['D']),'synthetic',time.monotonic(),self.cg)
        self.assertEqual(receipt['status'],'RESOURCE_INCONCLUSIVE')
        self.assertEqual(receipt['authoritativeFinalAcceptance'],{r:False for r in w.RUN_IDS})
        self.assertEqual(json.loads((self.output.path/'explicit-halves.json').read_text())['payload']['sentinel'],'retained_half_steps')
        self.assertFalse((self.output.path/'adaptive-depth1.json').exists())
    def test_finalize_has_detached_accounting_and_hashes(self):
        self.output.write('manifest.json',b'{}','A')
        result={r:{'status':'PASS','syntheticOnly':True} for r in w.RUN_IDS}
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
    def test_retained_result_buffers_count_across_jobs(self):
        self.policy['aggregateOutputBytes']=1200;self.policy['perRunOutputBytes']=1200;self.policy['reservedReceiptBytes']=0
        self.output.write('manifest.json',b'x'*100,'A')
        code="import os,json;os.write(int(os.environ['KENOMA_RESULT_FD']),json.dumps({'status':'PASS','pad':'x'*400}).encode())"
        first,_=self.run_child(code,{**self.run,'id':'B'});second,_=self.run_child(code,{**self.run,'id':'D'})
        self.assertEqual(first['status'],'PASS');self.assertEqual(second['status'],'RESOURCE_INCONCLUSIVE');self.assertIn('staging',second['reason'])
        self.assertGreater(self.output.pending['B'],400);self.assertEqual(self.output.pending['D'],0)
    def test_final_staging_coexists_with_retained_and_durable_bytes(self):
        self.policy['aggregateOutputBytes']=2400;self.policy['perRunOutputBytes']=2400;self.policy['reservedReceiptBytes']=0
        self.output.write('manifest.json',b'x'*100,'A');self.output.retain('B',1500)
        results={r:{'status':'PASS','pad':'x'*300} for r in w.RUN_IDS}
        with self.assertRaisesRegex(w.Refusal,'Output ceiling'):w.finalize(self.output,results,[],{},'synthetic',time.monotonic(),self.cg)
        self.assertFalse((self.output.path/'resource-receipt.json').exists())
    def test_exact_raw_review_bytes_and_digest_claim_identity(self):
        raw='{"value":1e-6,"name":"é"}\n';review=json.loads(raw)
        m={'reviewReceiptText':raw,'reviewReceipt':review,'reviewReceiptSHA256':w.digest(raw.encode())};w.validate_review_bytes(m)
        with self.assertRaisesRegex(w.Refusal,'exact review'):w.validate_review_bytes({**m,'reviewReceiptText':raw+' '})
        self.assertNotEqual(w.digest(raw.encode()),w.digest(w.encoded(review)))
        h=w.digest(raw.encode());self.assertEqual(w.claim_path(self.policy,h),w.claim_path(self.policy,h))
        self.assertEqual(w.claim_path(self.policy,h).name,h+'.executed')
        self.assertEqual(str(w.claim_path(self.policy,h).parent),w.EXPECTED_POLICY['claimDirectory'])
        self.assertFalse(w.claim_path(self.policy,h).exists())
    def test_exact_destination_binding_is_checked_without_launch(self):
        dest=self.root/'never';m={'executionDestination':str(dest)}
        self.assertEqual(w.approved_destination(m,dest),dest)
        with self.assertRaisesRegex(w.Refusal,'Unapproved'):w.approved_destination(m,self.root/'other')
        dest.mkdir()
        with self.assertRaisesRegex(w.Refusal,'already exists'):w.approved_destination(m,dest)
    def test_stale_policy_and_input_refuse(self):
        with self.assertRaisesRegex(w.Refusal,'source/policy'):w.validate_manifest({'schema':1},b'{}',False)
        m={'schema':1,'operatorCommit':'0b18a4146768ab6a49cb2febdea696bf0c073434','inputCommit':'0b83819ad3fdaed7405c6bbe617bc01640eef914','policy':w.EXPECTED_POLICY,'inputs':{},'baselineEvidence':self.baseline()}
        with self.assertRaisesRegex(w.Refusal,'input inventory'):w.validate_manifest(m,b'{}',False)
if __name__=='__main__':unittest.main()
