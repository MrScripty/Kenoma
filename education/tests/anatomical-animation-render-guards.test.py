"""Offline driver damage tests with mocked child; never starts a browser/solver."""
import importlib.util,json,pathlib,sys,tempfile,unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-validation'))
import watchdog as w,render as r,render_worker as rw
class RenderGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='kenoma-render-guard-synthetic-',dir='/tmp');self.root=pathlib.Path(self.tmp.name);self.manifest=self.root/'manifest.json';self.manifest.write_text('{}');self.config=self.root/'config.json';self.out=self.root/'output';self.cfg=dict(manifest=str(self.manifest),syntheticOnly=True,output=str(self.out));self.config.write_text(json.dumps(self.cfg));self.cg=self.root/'cgroup';self.cg.write_text('1')
    def tearDown(self):self.tmp.cleanup()
    def launch(self,guard=None,child=None):
        resources=dict(run='A',allProcessesReaped=True,startOffsetSeconds=0,wallSeconds=0,ownedPeakRSSBytes=0,observedCgroupPeakBytes=1)
        with patch.object(sys,'argv',['render.py','--config',str(self.config)]),patch.object(r,'validate_manifest',return_value='SYNTHETIC_NOT_LAUNCHED'),patch.object(r,'supervise',side_effect=child or (lambda *a,**k:({'status':'PASS'},resources))),patch.object(w,'cgroup_file',return_value=self.cg):
            if guard:
                with patch.object(r,'final_guard',side_effect=guard):r.main()
            else:r.main()
    def test_final_cgroup_after_disposal_refuses_success(self):
        self.cg.write_text(str(16000000001))
        with self.assertRaises(SystemExit):self.launch()
        receipt=json.loads((self.out/'resource-receipt.json').read_text());self.assertEqual(receipt['status'],'RESOURCE_INCONCLUSIVE');self.assertIn('cgroup',receipt['reason'])
    def test_last_guard_failure_replaces_just_written_pass_receipt(self):
        calls=0
        def guard(*args):
            nonlocal calls
            calls+=1
            if calls==3:raise w.Refusal('Synthetic final wall ceiling')
        with self.assertRaises(SystemExit):self.launch(guard)
        receipt=json.loads((self.out/'resource-receipt.json').read_text());self.assertEqual(calls,3);self.assertEqual(receipt['status'],'RESOURCE_INCONCLUSIVE');self.assertIn('wall',receipt['reason'])
    def test_foreign_file_and_scratch_byte_damage_kills_offline_acceptance(self):
        def child(command,out,*args,**kwargs):
            (out.path/'foreign').write_bytes(b'x');return dict(status='PASS'),dict(run='A',allProcessesReaped=True)
        with self.assertRaises(SystemExit):self.launch(child=child)
        self.assertEqual(json.loads((self.out/'resource-receipt.json').read_text())['status'],'RESOURCE_INCONCLUSIVE')
    def test_before_launch_refusal_retains_explicit_receipt(self):
        def child(*args,**kwargs):raise w.Refusal('Shared cgroup ceiling before launch')
        with self.assertRaises(SystemExit):self.launch(child=child)
        receipt=json.loads((self.out/'resource-receipt.json').read_text());self.assertEqual(receipt['status'],'REFUSED_BEFORE_BROWSER_LAUNCH');self.assertEqual(receipt['physicalEvaluations'],0)
    def test_worker_modified_renderer_source_refuses_before_node_or_browser(self):
        self.manifest.write_text(json.dumps(dict(harnessFiles={'education/tools/arm-validation/geometry.mjs':'bad'})));self.cfg.update(nodeExecutable='NEVER_LAUNCHED');self.config.write_text(json.dumps(self.cfg))
        with patch.object(sys,'argv',['render_worker.py',str(self.config)]),patch.object(rw.subprocess,'check_output',side_effect=AssertionError('Must not launch')):
            with self.assertRaisesRegex(ValueError,'Changed local renderer'):rw.main()
    def test_real_manifest_requires_exact_source_review_before_browser(self):
        self.manifest.write_text(json.dumps(dict(harnessFiles={},nodeVersion='synthetic',harnessCommit='abc',reviewReceipt=None)));self.cfg.update(nodeExecutable='NEVER_LAUNCHED',syntheticOnly=False);self.config.write_text(json.dumps(self.cfg))
        with patch.object(sys,'argv',['render_worker.py',str(self.config)]),patch.object(rw.subprocess,'check_output',return_value='synthetic'):
            with self.assertRaisesRegex(ValueError,'Missing exact source review'):rw.main()
if __name__=='__main__':unittest.main()
