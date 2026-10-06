"""A historical transition must never accept stale or damaged current evidence."""
from pathlib import Path
import json,shutil,sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from check_endpoint_warning_audit import check,ROOT

class EndpointAuditContract(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.out=Path(self.temp.name)
        source=ROOT/'data/property-labs-v1';self.base=self.out/'data/property-labs-v1'
        self.base.mkdir(parents=True)
        for name in ['endpoint-warning-audit.json','endpoint-warning-current-audit.json','endpoint-warning-browser-audit.json']:
            shutil.copy(source/name,self.base/name)
        shutil.copy(source/'endpoint-warning-current-visible.png',self.base/'endpoint-warning-current-visible.png')
        shutil.copytree(source/'endpoint-warning-history',self.base/'endpoint-warning-history')
    def tearDown(self):self.temp.cleanup()
    def change(self,name,edit):
        path=self.base/name;receipt=json.loads(path.read_text());edit(receipt);path.write_text(json.dumps(receipt))
    def test_current_and_preserved_history(self):check(self.out)
    def test_changed_historical_receipt_rejected(self):
        self.change('endpoint-warning-audit.json',lambda r:r.update(result='PASS'))
        with self.assertRaisesRegex(AssertionError,'historical endpoint receipt'):check(self.out)
    def test_changed_delivered_historical_renderer_rejected(self):
        (self.base/'endpoint-warning-history/web/property-labs.mjs').write_text('changed')
        with self.assertRaisesRegex(AssertionError,'historical renderer'):check(self.out)
    def test_changed_delivered_historical_numerical_module_rejected(self):
        (self.base/'endpoint-warning-history/web/tapered-bar.mjs').write_text('changed')
        with self.assertRaisesRegex(AssertionError,'historical numerical module'):check(self.out)
    def test_stale_current_renderer_rejected(self):
        self.change('endpoint-warning-browser-audit.json',lambda r:r['sourceHashes'].update({'web/property-labs.mjs':'0'*64}))
        with self.assertRaisesRegex(AssertionError,'Current endpoint input'):check(self.out)
    def test_removed_current_binding_rejected(self):
        self.change('endpoint-warning-browser-audit.json',lambda r:r['sourceHashes'].pop('web/tapered-bar.mjs'))
        with self.assertRaisesRegex(AssertionError,'Missing current browser'):check(self.out)
    def test_browser_receipt_cannot_bind_other_numerical_run(self):
        self.change('endpoint-warning-browser-audit.json',lambda r:r.update(currentNumericalReceiptSHA256='0'*64))
        with self.assertRaises(AssertionError):check(self.out)
    def test_delivered_visibility_evidence_cannot_change(self):
        (self.base/'endpoint-warning-current-visible.png').write_bytes(b'changed')
        with self.assertRaisesRegex(AssertionError,'Delivered endpoint screenshot'):check(self.out)
    def test_visibility_claim_cannot_be_false(self):
        self.change('endpoint-warning-browser-audit.json',lambda r:r['counterexample'].update(warningVisible=False))
        with self.assertRaises(AssertionError):check(self.out)

if __name__=='__main__':unittest.main()
