"""Exercise packaging against an immutable qualified build and corrupt outputs."""
from pathlib import Path
import contextlib,importlib.util,io,json,hashlib,shutil,tempfile,unittest,zipfile,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from executable_outputs import executable_outputs,executable_digest
class PackageAcceptance(unittest.TestCase):
 def test_qualified_bundle_and_corruption_controls(self):
  spec=importlib.util.spec_from_file_location('checked_package',ROOT/'tools/package_education_bundle.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  with tempfile.TemporaryDirectory(prefix='kenoma-package-gates-',dir='/tmp') as temporary:
   temporary=Path(temporary)
   fixture=temporary/'education';module.ROOT=fixture;dist=fixture/'dist';dist.mkdir(parents=True)
   seed=ROOT/'deliverables/release-candidate-repaired/kenoma-release-candidate-repaired-portable.zip'
   with zipfile.ZipFile(seed) as archive:archive.extractall(dist)
   inputs=json.loads((dist/'build-manifest.json').read_text())['input_sha256']
   with zipfile.ZipFile(ROOT/'data/property-labs-v1/review/package-fixture-1dc-missing-sources.zip') as missing:
    for name,digest in inputs.items():
     existing=dist/name;data=existing.read_bytes() if existing.is_file() else b''
     if hashlib.sha256(data).hexdigest()!=digest:data=missing.read(name)
     self.assertEqual(hashlib.sha256(data).hexdigest(),digest,name);target=fixture/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
   # Legacy outputs were actually checked; add the new byte-binding metadata
   # only inside this temporary contract fixture, preserving the frozen bundle.
   manifest=json.loads((dist/'build-manifest.json').read_text());manifest['executable_outputs']=executable_outputs(dist)
   (dist/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
   for name in ['browser-check.json','mobile-startup-check.json']:
    path=dist/name;receipt=json.loads(path.read_text());receipt['executable_outputs_sha256']=executable_digest(manifest['executable_outputs']);path.write_text(json.dumps(receipt,indent=2)+'\n')
   for name,scope in [('anatomical-arm-review/browser-receipt.json','anatomical-arm'),('coupled-review/browser-receipt.json','coupled-fixture')]:
    path=dist/name;receipt=json.loads(path.read_text());receipt['executable_outputs']=executable_outputs(dist,scope);path.write_text(json.dumps(receipt,indent=2)+'\n')
   for name,key in [('qa/property-browser-check.json','manifest_sha256'),('property-book-review/render-receipt.json','build_manifest_sha256')]:
    path=dist/name;receipt=json.loads(path.read_text());receipt[key]=hashlib.sha256((dist/'build-manifest.json').read_bytes()).hexdigest();path.write_text(json.dumps(receipt,indent=2)+'\n')
   # The frozen 29-card fixture cannot qualify as the expanded current book.
   # Keep its old positive/corruption contract explicit without inventing new
   # compiled Real or material receipts inside historical evidence.
   with self.assertRaisesRegex(RuntimeError,'Unexpected proof families'):
    module.validate_build(dist,manifest)
   module.FAMILIES=module.FAMILIES[:5];module.PROOF_COUNT=29
   # This historical package also predates the new actual-point print gate.
   # Prove it is rejected, then isolate only its existing legacy corruption
   # contract. No readability PASS receipt is invented for the old PDF.
   with self.assertRaises(FileNotFoundError):module.validate_build(dist,manifest)
   module.check_print_readability=lambda path:None
   with contextlib.redirect_stdout(io.StringIO()):module.package(temporary/'positive.zip')
   controls=[('changed HTML with stale browser hashes','index.html',lambda b:b+b'\n<!-- modified after browser check -->'),('wrong proof source hash','proof-status.json',lambda b:self.json_change(b,lambda x:x.update(source_sha256='0'*64))),('empty checked claims','proof-status.json',lambda b:self.json_change(b,lambda x:x.update(claims=[]))),('missing PDF','kenoma-mechanics.pdf',lambda b:None),('missing linked app','assets/app.js',lambda b:None),('failed artifact status','artifact-check.json',lambda b:self.json_change(b,lambda x:x.update(status='failed'))),('changed build input','../proofs/Mechanics.lean',lambda b:b+b'\n-- changed input\n')]
   controls.extend([('throwing anatomical worker','anatomical-arm/worker.js',lambda b:b'throw new Error(\"mutation\");\n'),('throwing coupled worker','coupled-fixture/worker.js',lambda b:b'throw new Error(\"mutation\");\n'),('changed anatomical subpage','anatomical-arm/index.html',lambda b:b+b'\n<!-- changed after native browser checks -->')])
   unexpected=[]
   for i,(label,name,change) in enumerate(controls):
    path=dist/name;original=path.read_bytes();modified=change(original)
    try:
     if modified is None:path.unlink()
     else:path.write_bytes(modified)
     try:
      with contextlib.redirect_stdout(io.StringIO()):module.package(temporary/f'negative-{i}.zip')
      unexpected.append(label);print('FALSE_PASS_PACKAGE',label)
     except (RuntimeError,AssertionError,FileNotFoundError,ValueError):print('REJECTED_PACKAGE',label)
    finally:path.write_bytes(original)
   self.assertEqual(unexpected,[], 'package accepted corrupted qualified-build outputs')
 @staticmethod
 def json_change(data,change):
  value=json.loads(data);change(value);return (json.dumps(value,indent=2)+'\n').encode()
if __name__=='__main__':unittest.main()
