"""Exercise packaging against an immutable qualified build and corrupt outputs."""
from pathlib import Path
import contextlib,importlib.util,io,json,hashlib,shutil,tempfile,unittest,zipfile
ROOT=Path(__file__).resolve().parents[1]
class PackageAcceptance(unittest.TestCase):
 def test_qualified_bundle_and_corruption_controls(self):
  spec=importlib.util.spec_from_file_location('checked_package',ROOT/'tools/package_education_bundle.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  with tempfile.TemporaryDirectory(prefix='kenoma-package-gates-',dir='/tmp') as temporary:
   temporary=Path(temporary)
   fixture=temporary/'education';module.ROOT=fixture;dist=fixture/'dist';dist.mkdir(parents=True)
   seed=ROOT/'deliverables/release-candidate/kenoma-release-candidate-portable.zip'
   with zipfile.ZipFile(seed) as archive:archive.extractall(dist)
   inputs=json.loads((dist/'build-manifest.json').read_text())['input_sha256']
   with zipfile.ZipFile(ROOT/'data/property-labs-v1/review/package-fixture-90-missing-sources.zip') as missing:
    for name,digest in inputs.items():
     existing=dist/name;data=existing.read_bytes() if existing.is_file() else b''
     if hashlib.sha256(data).hexdigest()!=digest:data=missing.read(name)
     self.assertEqual(hashlib.sha256(data).hexdigest(),digest,name);target=fixture/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
   with contextlib.redirect_stdout(io.StringIO()):module.package(temporary/'positive.zip')
   controls=[('changed HTML with stale browser hashes','index.html',lambda b:b+b'\n<!-- modified after browser check -->'),('wrong proof source hash','proof-status.json',lambda b:self.json_change(b,lambda x:x.update(source_sha256='0'*64))),('empty checked claims','proof-status.json',lambda b:self.json_change(b,lambda x:x.update(claims=[]))),('missing PDF','kenoma-mechanics.pdf',lambda b:None),('missing linked app','assets/app.js',lambda b:None),('failed artifact status','artifact-check.json',lambda b:self.json_change(b,lambda x:x.update(status='failed'))),('changed build input','../proofs/Mechanics.lean',lambda b:b+b'\n-- changed input\n')]
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
