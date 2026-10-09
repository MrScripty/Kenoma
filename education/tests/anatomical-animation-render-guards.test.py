"""Offline driver damage tests with mocked child; never starts a browser/solver."""
import base64,struct,subprocess,shutil,importlib.util,json,pathlib,sys,tempfile,unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-validation'))
import watchdog as w,render as r,render_worker as rw,capture_store as c
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
        self.manifest.write_text(json.dumps(dict(harnessFiles={p:('bad' if p.endswith('/geometry.mjs') else w.digest((w.ROOT/p).read_bytes())) for p in w.HARNESS_PATHS})));self.cfg.update(nodeExecutable='NEVER_LAUNCHED');self.config.write_text(json.dumps(self.cfg))
        with patch.object(sys,'argv',['render_worker.py',str(self.config)]),patch.object(rw.subprocess,'check_output',side_effect=AssertionError('Must not launch')):
            with self.assertRaisesRegex(ValueError,'Changed local renderer'):rw.main()
    def test_prelaunch_sequence_zero_and_worker_begin_pass_exact_frame_validation(self):
        camera=json.loads(subprocess.check_output([shutil.which('node'),'--input-type=module','-e',"import {CAMERA,CAMERA_SHA256} from './education/tools/arm-validation/capture.mjs';process.stdout.write(JSON.stringify({camera:CAMERA,cameraSHA256:CAMERA_SHA256}))"],cwd=w.ROOT))
        model='{}';state='{"state":{"coordinatesM":[]}}';m=dict(camera,inputs={'generated/arm-reference.json':{'text':model,'sha256':w.digest(model.encode())},'audit/arm-rest-results.json':{'text':state,'sha256':w.digest(state.encode())}},harnessFiles={p:w.digest((w.ROOT/p).read_bytes()) for p in w.HARNESS_PATHS},nodeVersion='synthetic',harnessCommit='SYNTHETIC_NO_PHYSICS',operatorCommit='SYNTHETIC_NO_PHYSICS',inputCommit='SYNTHETIC_NO_PHYSICS')
        self.manifest.write_bytes(w.encoded(m));identity=dict(schema=1,run='B',manifestSHA256=w.digest(self.manifest.read_bytes()),harnessCommit=m['harnessCommit'],operatorCommit=m['operatorCommit'],inputCommit=m['inputCommit'],modelSHA256=m['inputs']['generated/arm-reference.json']['sha256'],inputStateSHA256=m['inputs']['audit/arm-rest-results.json']['sha256'],cameraSHA256=m['cameraSHA256'],jointScaleMPerRad=.1)
        path=self.root/'geometry-B.slots';store=c.Store(path,'B',identity);store.prime_begin([0]*460);raw=struct.pack('<460d',*([0]*460));row=dict(identity,workerPID=123,kind='BEGIN',attempt=1,sequence=1,attemptSequence=0,status='PROVISIONAL_NEWTON_ITERATE',physicalMotionAccepted=False,coordinatesFloat64LE=base64.b64encode(raw).decode(),coordinatesSHA256=w.digest(raw));payload=json.dumps(row,separators=(',',':')).encode();store.feed(struct.pack('>I',len(payload))+bytes.fromhex(w.digest(payload))+payload);store.seal();self.assertEqual([x['sequence'] for x in c.read_slots(path)],[0,1]);self.cfg.update(captures=[str(path)],nodeExecutable='NEVER_LAUNCHED',nodeModules='NEVER_LOADED');self.config.write_text(json.dumps(self.cfg))
        with patch.object(sys,'argv',['render_worker.py',str(self.config)]),patch.object(rw.subprocess,'check_output',return_value='synthetic'),patch.object(rw.subprocess,'run',side_effect=RuntimeError('FRAME_VALIDATION_PASSED_NO_BROWSER')):
            with self.assertRaisesRegex(RuntimeError,'FRAME_VALIDATION_PASSED_NO_BROWSER'):rw.main()
    def test_real_manifest_requires_exact_source_review_before_browser(self):
        self.manifest.write_text(json.dumps(dict(harnessFiles={p:w.digest((w.ROOT/p).read_bytes()) for p in w.HARNESS_PATHS},nodeVersion='synthetic',harnessCommit='abc',reviewReceipt=None)));self.cfg.update(nodeExecutable='NEVER_LAUNCHED',syntheticOnly=False);self.config.write_text(json.dumps(self.cfg))
        with patch.object(sys,'argv',['render_worker.py',str(self.config)]),patch.object(rw.subprocess,'check_output',return_value='synthetic'):
            with self.assertRaisesRegex(ValueError,'Missing exact source review'):rw.main()
if __name__=='__main__':unittest.main()
