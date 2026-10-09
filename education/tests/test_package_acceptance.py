"""Packaging contracts use small runtime fixtures, never an archived book ZIP.

These isolated unit fixtures test bindings and damage rejection. Their receipts
are temporary test data; they do not qualify proofs, browsers or a real book.
"""
from pathlib import Path
import contextlib, importlib.util, io, json, hashlib, tempfile, unittest, sys
import fitz
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from executable_outputs import executable_outputs, executable_digest
from chapter_examples import RUNTIME_SOURCES, runtime_resources

class PackageAcceptance(unittest.TestCase):
 def fixture(self, fixture):
  dist = fixture/'dist'; dist.mkdir(parents=True)
  def write(name, content, source=False):
   path = (fixture if source else dist)/name; path.parent.mkdir(parents=True,exist_ok=True)
   path.write_bytes(content if isinstance(content,bytes) else content.encode()); return path
  def record(name, value, source=False): return write(name,json.dumps(value),source)
  def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
  families = [('proof-status.json','Mechanics.lean','claims.json',1),('property-proof-status.json','ContinuumProperties.lean','property-claims.json',1)]
  for name, source, claims, count in families:
   claim = [{'id':'fixture-'+source,'theorem':'Fixture.identity','statement':'unit-test identity'}]
   src = write('proofs/'+source,'-- isolated packaging fixture\ntheorem identity : True := True.intro\n',True)
   cmap = record('proofs/'+claims,claim,True)
   write('proofs/'+source,src.read_bytes()); write('proofs/'+claims,cmap.read_bytes())
   record(name,{'source':'proofs/'+source,'source_sha256':digest(src),'claims_sha256':digest(cmap),'lean_version':'unit-fixture',
    'claims':[dict(claim[0],status='checked',axioms=[])]})
  dependency = record('proofs/mathlib-lake-manifest.json',{'fixture':True})
  lock = {'manifest_sha256':digest(dependency),'commit':'isolated-unit-fixture'}
  record('proofs/mathlib-lock.json',lock,True)
  p = dist/'property-proof-status.json'; value=json.loads(p.read_text());value['mathlib']=lock;record(p.name,value)
  write('tools/inspect_property_integration.py','# isolated unit fixture\n',True)
  write('index.html','<a href="kenoma-mechanics.pdf">PDF</a><script src="assets/app.js"></script>')
  write('kenoma-mechanics.md','Unit packaging fixture, not a qualified book.\n')
  for name in ['assets/app.js','anatomical-arm/worker.js','coupled-fixture/worker.js']:write(name,'export const fixture = true;\n')
  for name in ['anatomical-arm/index.html','coupled-fixture/index.html']:write(name,'<script src="worker.js"></script>')
  # Synthetic bytes test bindings only, not rendering, scientific data or WASM validity.
  ids=['unit-example-'+str(i) for i in range(27)]
  registry=record('book/examples/registry.json',{'version':1,'examples':ids},True)
  write('chapter-examples.json',registry.read_bytes())
  gui_source=write('../browser/embedded/viewport.js','// isolated GUI fixture\n',True)
  gui_test=write('tests/chapter_examples_browser.py','# isolated GUI browser fixture\n',True)
  wasm=write('gui/simple-graph/pkg/human_wasm_bg.wasm',b'unit-fixture-WASM-bytes-not-executable')
  for delivered,source in RUNTIME_SOURCES.items():
   write(delivered,'isolated GUI resource fixture\n')
   path=fixture.parent/source;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('isolated GUI resource fixture\n')
  runtime=runtime_resources(dist,fixture.parent)
  gui={'version':1,'chapters':27,'example_ids':ids,'registry_sha256':digest(registry),
       'gui_inputs':{'browser/embedded/viewport.js':digest(gui_source)},'wasm_sha256':digest(wasm),'runtime_resources':runtime}
  record('chapter-example-build.json',gui)
  document=fitz.open();document.new_page().insert_text((72,72),'Unit packaging fixture',fontsize=11);document.save(dist/'kenoma-mechanics.pdf');document.close()
  manifest={'input_sha256':{str(p.relative_to(fixture)):digest(p) for p in fixture.rglob('*') if p.is_file() and not p.is_relative_to(dist)},
    'executable_outputs':executable_outputs(dist),'proof_families':[f[0] for f in families],'lean':'unit-fixture','property_mathlib':lock,'git_revision':'unit-fixture','chapter_examples':gui}
  record('build-manifest.json',manifest)
  record('chapter-example-qa/receipt.json',{'result':'PASS_CHAPTER_EXAMPLES','preview':False,
    'test_sha256':digest(gui_test),'registry_sha256':digest(registry),'runtime_resources':runtime,
    'executable_outputs_sha256':executable_digest(manifest['executable_outputs']),
    'views':[{'width':width,'chapters':ids,'errors':[]} for width in [320,390,1280]]})
  html=digest(dist/'index.html');app=digest(dist/'assets/app.js');manifest_hash=digest(dist/'build-manifest.json')
  for name in ['browser-check.json','mobile-startup-check.json']:
   record(name,{'status':'passed','executable_outputs_sha256':executable_digest(manifest['executable_outputs']),'html_sha256':html,'app_sha256':app})
  for name,scope in [('anatomical-arm-review/browser-receipt.json','anatomical-arm'),('coupled-review/browser-receipt.json','coupled-fixture')]:
   record(name,{'result':'PASS','executable_outputs':executable_outputs(dist,scope)})
  record('qa/property-browser-check.json',{'result':'PASS_INTEGRATED_PROPERTY_LABS','proof_cards':2,'html_sha256':html,'app_sha256':app,'manifest_sha256':manifest_hash})
  images=[v+'-'+claim+'.png' for v in ['desktop','mobile'] for claim in ['volume-edge-translation','volume-det-compose','volume-diagonal','volume-isochoric-sqrt']]+['page-1.png']
  outputs={name:digest(write('property-book-review/'+name,b'unit-fixture-render-bytes')) for name in images}
  record('property-book-review/render-receipt.json',{'result':'PASS_PROPERTY_BOOK_RENDER_CAPTURE','page_errors':[],
   'html_sha256':html,'pdf_sha256':digest(dist/'kenoma-mechanics.pdf'),'build_manifest_sha256':manifest_hash,
   'inspector_sha256':digest(fixture/'tools/inspect_property_integration.py'),'views':[{'name':v,'proofCards':2,'horizontalOverflow':False} for v in ['desktop','mobile']],
   'pdf_pages':[{'image':'page-1.png','phrases':['Property lab 1','Property lab 2','Property lab 3']}],'outputs':outputs})
  record('artifact-check.json',{'status':'passed','proof_cards':2,'pdf_pages':1})
  return dist,manifest,families

 def test_qualified_bundle_and_corruption_controls(self):
  spec=importlib.util.spec_from_file_location('checked_package',ROOT/'tools/package_education_bundle.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  with tempfile.TemporaryDirectory(prefix='kenoma-package-unit-',dir='/tmp') as temporary:
   temporary=Path(temporary);fixture=temporary/'education';module.ROOT=fixture
   dist,manifest,families=self.fixture(fixture)
   # The production validator rejects these unit fixtures as a current book.
   with self.assertRaisesRegex(RuntimeError,'Unexpected proof families'):module.validate_build(dist,manifest)
   module.FAMILIES=families;module.PROOF_COUNT=2
   with self.assertRaises(FileNotFoundError):module.validate_build(dist,manifest)
   # Isolate the packaging contract only. Actual-point PDF tests remain separate
   # and production validation still invokes the unchanged mandatory checker.
   module.check_print_readability=lambda path:None
   with contextlib.redirect_stdout(io.StringIO()):module.package(temporary/'positive.zip')
   controls=[('changed HTML with stale browser hashes','index.html',lambda b:b+b'<!-- modified -->'),
    ('wrong proof source hash','proof-status.json',lambda b:self.json_change(b,lambda x:x.update(source_sha256='0'*64))),
    ('empty checked claims','proof-status.json',lambda b:self.json_change(b,lambda x:x.update(claims=[]))),
    ('missing PDF','kenoma-mechanics.pdf',lambda b:None),('missing linked app','assets/app.js',lambda b:None),
    ('failed artifact status','artifact-check.json',lambda b:self.json_change(b,lambda x:x.update(status='failed'))),
    ('changed build input','../proofs/Mechanics.lean',lambda b:b+b'-- changed\n'),
    ('throwing anatomical worker','anatomical-arm/worker.js',lambda b:b'throw new Error("mutation");'),
    ('throwing coupled worker','coupled-fixture/worker.js',lambda b:b'throw new Error("mutation");'),
    ('changed anatomical subpage','anatomical-arm/index.html',lambda b:b+b'<!-- modified -->'),
    ('changed render bytes','property-book-review/page-1.png',lambda b:b+b'changed'),
    ('changed poser WASM','gui/simple-graph/pkg/human_wasm_bg.wasm',lambda b:b+b'changed'),
    ('changed shared viewport','../../browser/embedded/viewport.js',lambda b:b+b'changed'),
    ('preview cannot qualify book GUI','chapter-example-qa/receipt.json',lambda b:self.json_change(b,lambda x:x.update(preview=True))),
    ('incomplete GUI viewport coverage','chapter-example-qa/receipt.json',lambda b:self.json_change(b,lambda x:x.update(views=[]))),
    ('changed GUI registry','chapter-examples.json',lambda b:b+b'changed'),
    ('changed delivered atlas','data/elbow-v1/data/bodyparts3d_right_arm_m.json',lambda b:b+b'changed'),
    ('changed delivered GUI style','assets/chapter-examples.css',lambda b:b+b'changed')]
   for i,(label,name,change) in enumerate(controls):
    path=dist/name;original=path.read_bytes();modified=change(original)
    try:
     if modified is None:path.unlink()
     else:path.write_bytes(modified)
     with self.assertRaises((RuntimeError,AssertionError,FileNotFoundError,ValueError),msg=label):
      with contextlib.redirect_stdout(io.StringIO()):module.package(temporary/f'negative-{i}.zip')
    finally:path.write_bytes(original)
 @staticmethod
 def json_change(data,change):
  value=json.loads(data);change(value);return (json.dumps(value)+'\n').encode()
if __name__=='__main__':unittest.main()
