"""Synthetic coordinates/processes only; zero material/force evaluations."""
import shutil,base64,copy,importlib.util,json,math,os,pathlib,struct,subprocess,sys,tempfile,time,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-validation'))
import capture_store as c,watchdog as w

def frame(seq,kind='NEWTON_ITERATE',attempt=1,local=None,**extras):
    raw=struct.pack('<460d',*[seq/10000]*460)
    row=dict(schema=1,run='B',manifestSHA256='synthetic',workerPID=123,status='PROVISIONAL_NEWTON_ITERATE',physicalMotionAccepted=False,attempt=attempt,sequence=seq,attemptSequence=seq-1 if local is None else local,kind=kind,iteration=(seq-2)%3,residualN=1/seq,coordinatesFloat64LE=base64.b64encode(raw).decode(),coordinatesSHA256=c.digest(raw));row.update(extras);payload=json.dumps(row,separators=(',',':'),allow_nan=False).encode();return struct.pack('>I',len(payload))+bytes.fromhex(c.digest(payload))+payload
class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='kenoma-animation-synthetic-',dir='/tmp');self.root=pathlib.Path(self.tmp.name);self.store=c.Store(self.root/'geometry-B.slots','B',dict(run='B',manifestSHA256='synthetic'));self.store.bind_process(123,99)
    def tearDown(self):
        if not self.store.sealed:self.store.seal()
        self.tmp.cleanup()
    def begin(self):self.store.feed(frame(1,'BEGIN',local=0))
    def test_fragmented_wire_and_latest_checkpoints_are_detached(self):
        b=frame(1,'BEGIN',local=0)+b''.join(frame(i) for i in range(2,52))
        for i in range(0,len(b),17):self.store.feed(b[i:i+17])
        receipt=self.store.seal();rows=c.read_slots(self.store.path);self.assertEqual(rows[0]['kind'],'BEGIN');self.assertEqual(rows[-1]['sequence'],51);self.assertEqual(len(rows),8);self.assertEqual(receipt['records'],51);self.assertEqual(receipt['retainedBytes'],98304);self.assertLessEqual(len(rows),11);self.assertFalse(receipt['physicalMotionAccepted'])
    def test_partial_trailing_wire_preserves_latest(self):
        self.begin();self.store.feed(frame(2));self.store.feed(frame(3)[:111]);receipt=self.store.seal();self.assertEqual(receipt['trailingIncompleteBytes'],111);self.assertEqual(c.read_slots(self.store.path)[-1]['sequence'],2)
    def test_partial_latest_slot_recovers_previous_complete_record(self):
        self.begin();self.store.feed(frame(2));self.store.feed(frame(3));self.store.feed(frame(4));os.pwrite(self.store.fd,b'\x00\x00\x01\x00'+b'x'*40,11*8192);os.fsync(self.store.fd);self.store.seal();rows=c.read_slots(self.store.path);self.assertEqual(rows[-1]['sequence'],3);self.assertEqual(rows[0]['sequence'],1)
    def test_local_iteration_reset_keeps_distinct_monotonic_callback_sequence(self):
        self.begin();self.store.feed(frame(2,iteration=9));self.store.feed(frame(3,iteration=0));self.store.seal();self.assertEqual(c.read_slots(self.store.path)[-1]['iteration'],0)
    def test_checksum_length_coordinate_authority_and_identity_damage(self):
        self.begin()
        bad=bytearray(frame(2));bad[-1]^=1
        with self.assertRaisesRegex(ValueError,'checksum'):self.store.commit(bytes(bad))
        with self.assertRaisesRegex(ValueError,'length'):c.decode(struct.pack('>I',8192)+bytes(32))
        for override,why in [(dict(physicalMotionAccepted=True),'authority'),(dict(manifestSHA256='wrong'),'provenance'),(dict(workerPID=124),'identity'),(dict(sequence=5),'sequence'),(dict(attemptSequence=5),'iteration'),(dict(attempt=2),'sequence')]:
            with self.assertRaisesRegex(ValueError,why):self.store.commit(frame(2,**override))
        raw=frame(2,coordinatesFloat64LE=base64.b64encode(struct.pack('<460d',math.nan,*([0]*459))).decode())
        with self.assertRaisesRegex(ValueError,'coordinates'):self.store.commit(raw)
    def test_begin_once_order_and_wire_ceiling(self):
        with self.assertRaisesRegex(ValueError,'beginning'):self.store.feed(frame(1,local=1))
        self.begin()
        with self.assertRaisesRegex(ValueError,'beginning'):self.store.commit(frame(2,'BEGIN',local=0))
        with self.assertRaisesRegex(ValueError,'read ceiling'):self.store.feed(bytes(65537))
        self.store.wireBytes=514*8192
        with self.assertRaisesRegex(ValueError,'wire ceiling'):self.store.feed(b'x')
    def test_two_D_attempts_have_independent_begin_latest_and_no_B_overwrite(self):
        d=c.Store(self.root/'geometry-D.slots','D',dict(run='D'))
        try:
            d.feed(frame(1,'BEGIN',run='D',local=0));d.feed(frame(2,run='D'));d.feed(frame(3,'BEGIN',attempt=2,run='D',local=0));d.feed(frame(4,attempt=2,run='D',local=1));d.seal();rows=c.read_slots(d.path);self.assertEqual([(r['attempt'],r['kind']) for r in rows],[(1,'BEGIN'),(1,'NEWTON_ITERATE'),(2,'BEGIN'),(2,'NEWTON_ITERATE')]);self.begin();self.store.seal();self.assertEqual(c.read_slots(d.path),rows)
        finally:
            if not d.sealed:d.seal()
    def test_slot_allocation_and_buffers_inside_existing_output_ceiling(self):
        policy=copy.deepcopy(w.EXPECTED_POLICY);out=w.Output(self.root/'output',policy);out.charges['B']=policy['perRunOutputBytes']-policy['reservedReceiptBytes']-98304-1048576
        store=c.Store(out.path/'geometry-B.slots','B',dict(run='B'),out)
        try:
            out.reserve('B',0)
            with self.assertRaisesRegex(w.Refusal,'ceiling'):out.reserve('B',1)
            store.seal();self.assertEqual(out.captureBuffers['B'],0);out.verify_inventory()
        finally:
            if not store.sealed:store.seal()
    def test_owned_timeout_retains_begin_and_latest_complete_frame_without_acceptance(self):
        cg=self.root/'fake-cgroup';cg.write_text('1');policy=copy.deepcopy(w.EXPECTED_POLICY);policy['aggregateWallSeconds']=2;out=w.Output(self.root/'timeout-output',policy);identity=dict(run='B',manifestSHA256='synthetic')
        code="import {createCapture} from "+json.dumps((ROOT/'tools/arm-validation/capture.mjs').as_uri())+";const c=createCapture(Number(process.env.KENOMA_CAPTURE_FD),{run:'B',manifestSHA256:'synthetic',workerPID:process.pid});const x=new Float64Array(460);c.snapshot('BEGIN',1,x);for(let i=0;i<47;i++){x[0]=i/10000;c.snapshot('NEWTON_ITERATE',1,x,{iteration:i,residualN:1/(i+1)});}while(true){}"
        result,rs=w.supervise([shutil.which('node'),'--input-type=module','-e',code],out,dict(id='B',wallSeconds=.5),time.monotonic(),cg,capture_identity=identity)
        self.assertEqual(result['status'],'RESOURCE_INCONCLUSIVE');self.assertTrue(rs['allProcessesReaped']);self.assertGreaterEqual(rs['capture']['records'],2);self.assertLessEqual(rs['capture']['records'],48);self.assertEqual(c.read_slots(out.path/'geometry-B.slots')[-1]['sequence'],rs['capture']['records']);self.assertFalse(rs['capture']['physicalMotionAccepted']);out.verify_inventory()
    def test_trailing_partial_from_killed_process_is_recorded_without_losing_begin(self):
        cg=self.root/'fake-cgroup';cg.write_text('1');policy=copy.deepcopy(w.EXPECTED_POLICY);policy['aggregateWallSeconds']=2;out=w.Output(self.root/'partial-output',policy);raw=frame(1,'BEGIN',local=0,workerPID=None)
        # Child sets its actual PID in a complete checksummed beginning.
        code="import os,json,struct,hashlib,time;row="+repr(json.loads(raw[36:]))+";row['workerPID']=os.getpid();b=json.dumps(row,separators=(',',':')).encode();fd=int(os.environ['KENOMA_CAPTURE_FD']);os.write(fd,struct.pack('>I',len(b))+hashlib.sha256(b).digest()+b);os.write(fd,b'\\x00\\x00\\x01\\x00'+b'x'*50);time.sleep(2)"
        result,rs=w.supervise([sys.executable,'-c',code],out,dict(id='B',wallSeconds=.3),time.monotonic(),cg,capture_identity=dict(run='B',manifestSHA256='synthetic'))
        self.assertEqual(result['status'],'RESOURCE_INCONCLUSIVE');self.assertTrue(rs['allProcessesReaped']);self.assertEqual(rs['capture']['trailingIncompleteBytes'],54);self.assertEqual(c.read_slots(out.path/'geometry-B.slots')[0]['kind'],'BEGIN')
if __name__=='__main__':unittest.main()
