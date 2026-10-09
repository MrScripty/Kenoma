"""Exercise output boundaries without running proofs or numerical experiments."""
from pathlib import Path
import json, sys, tempfile, unittest, subprocess
from contextlib import redirect_stdout
from io import StringIO
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from publication_data import publication_sources,copy_publication_data
from check_generated_outputs import violations, check as check_tracked_outputs
from ordinary_images import jpeg85

class OutputRouting(unittest.TestCase):
 def fixture(self,root,names):
  education=root/'education';(education/'tools').mkdir(parents=True)
  source=education/'data/anatomical-arm-v1';source.mkdir(parents=True)
  (source/'keep.json').write_text('{"fixture":true}')
  (source/'unpublished.json').write_text('{"archive":true}')
  (education/'tools/anatomy-publication-files.json').write_text(json.dumps({'sourceRoot':'data/anatomical-arm-v1','files':names}))
  return education,source
 def test_exact_copy_prunes_only_generated_destination(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);education,source=self.fixture(root,['keep.json']);output=root/'dist'
   old=output/'data/anatomical-arm-v1';old.mkdir(parents=True);(old/'unpublished.json').write_text('stale')
   self.assertEqual(copy_publication_data(education,output),1)
   self.assertEqual([p.name for p in old.iterdir()],['keep.json'])
   self.assertTrue((source/'unpublished.json').exists())
 def test_invalid_manifest_preserves_previous_output(self):
  for names in [['../escape'],['/absolute'],['keep.json','keep.json'],['missing.json']]:
   with self.subTest(names=names),tempfile.TemporaryDirectory() as temp:
    root=Path(temp);education,source=self.fixture(root,names);old=root/'dist/data/anatomical-arm-v1';old.mkdir(parents=True);sentinel=old/'sentinel';sentinel.write_text('preserve')
    with self.assertRaises(ValueError):copy_publication_data(education,root/'dist')
    self.assertEqual(sentinel.read_text(),'preserve')
 def test_source_and_symlink_are_protected(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);education,source=self.fixture(root,['keep.json'])
   with self.assertRaisesRegex(ValueError,'overlaps'):copy_publication_data(education,education)
   (source/'keep.json').unlink();(source/'keep.json').symlink_to(source/'unpublished.json')
   with self.assertRaisesRegex(ValueError,'Symlink'):publication_sources(education)
 def test_manifest_resolves_all_current_files(self):
  self.assertEqual(len(publication_sources(ROOT)),63)
 def test_tracked_artifact_guard(self):
  bad=['education/review/a.png','education/deliverables/book.zip','education/book.pdf','education/proofs/a.olean','education/.artifacts/run.json','education/dist/index.html']
  self.assertEqual(violations(bad),bad)
  self.assertEqual(violations(['education/data/elbow-v1/sources/bodyparts3d/coordsystem.png','education/web/app.mjs','education/book/chapters/example.md']),[])
 def test_real_git_index_rejects_new_or_changed_large_execution_collection(self):
  with tempfile.TemporaryDirectory() as temporary:
   root=Path(temporary)
   subprocess.run(['git','init','--quiet',str(root)],check=True)
   tools=root/'education/tools';tools.mkdir(parents=True)
   policy=tools/'preserved-generated-inputs.json';policy.write_text('{"files":{}}')
   name='education/data/anatomical-arm-v1/audit/new-run.json'
   path=root/name;path.parent.mkdir(parents=True);path.write_bytes(b'0'*1000001)
   subprocess.run(['git','add',name],cwd=root,check=True)
   with self.assertRaisesRegex(RuntimeError,'new-run.json'):check_tracked_outputs(root)
   blob=subprocess.check_output(['git','rev-parse',':'+name],cwd=root,text=True).strip()
   policy.write_text(json.dumps({'files':{name:{'gitBlob':blob,'bytes':1000001}}}))
   with redirect_stdout(StringIO()):check_tracked_outputs(root)
   path.write_bytes(b'1'*1000001);subprocess.run(['git','add',name],cwd=root,check=True)
   with self.assertRaisesRegex(RuntimeError,'new-run.json'):check_tracked_outputs(root)

 def test_jpeg85_has_correct_format_and_dimensions(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);source=root/'source.png';target=root/'ordinary.jpg'
   Image.new('RGBA',(21,17),(10,100,200,128)).save(source)
   jpeg85(source,target)
   with Image.open(target) as image:
    self.assertEqual((image.format,image.mode,image.size),('JPEG','RGB',(21,17)))
    # JPEG quality controls its actual quantization tables, not a filename.
    expected=root/'expected.jpg';Image.new('RGB',(21,17),(10,100,200)).save(expected,quality=85)
    with Image.open(expected) as reference:self.assertEqual(image.quantization,reference.quantization)
if __name__=='__main__':unittest.main()
