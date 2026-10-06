"""Damaged connected integration copies must fail the same delivered gates."""
from pathlib import Path
import json,tempfile,shutil,sys
from check_connected_artifact import check,sha,ROOT
out=ROOT/'dist';rows=[];check(out);before={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file() and '__pycache__' not in str(p)}
for name in ['missing-integration','changed-worker','wrong-figure','missing-proof','changed-integration-test','changed-controls-capture','rehashed-wrong-figure']:
 with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as folder:
  copy=Path(folder)/'dist';shutil.copytree(out,copy)
  if name=='missing-integration':(copy/'connected-integration.json').unlink()
  elif name=='changed-worker':p=copy/'connected-passive/assets/axisymmetric-worker.js';p.write_text(p.read_text()+'\nthrow Error("damaged")')
  elif name=='wrong-figure':p=copy/'assets/connected-specimen.svg';p.write_text(p.read_text().replace('16 axial','32 axial'))
  elif name=='missing-proof':(copy/'axisymmetric-proof-status.json').unlink()
  elif name=='changed-integration-test':
   p=copy/'connected-integration.json';record=json.loads(p.read_text());record['test_sha256']='0'*64;p.write_text(json.dumps(record))
  elif name=='changed-controls-capture':(copy/'connected-in-book-controls.png').write_bytes(b'wrong capture')
  else:
   svg=copy/'assets/connected-specimen.svg';svg.write_text(svg.read_text().replace('16 axial','32 axial'))
   p=copy/'connected-figure.json';record=json.loads(p.read_text());record['svg_sha256']=sha(svg);p.write_text(json.dumps(record))
   p=copy/'build-manifest.json';record=json.loads(p.read_text());record['connected_outputs']['assets/connected-specimen.svg']=sha(svg);record['connected_outputs']['connected-figure.json']=sha(copy/'connected-figure.json');p.write_text(json.dumps(record))
   p=copy/'connected-integration.json';record=json.loads(p.read_text());record['manifest_sha256']=sha(copy/'build-manifest.json');p.write_text(json.dumps(record))
  try:check(copy)
  except (AssertionError,FileNotFoundError) as error:rows.append({'case':name,'detected':True,'reason':str(error)})
  else:raise RuntimeError('FALSE_PASS '+name)
assert before=={name:sha(out/name) for name in before}
(out/'connected-negative-artifacts.json').write_text(json.dumps({'result':'PASS_SEVEN_DAMAGED_CONNECTED_ARTIFACTS','cases':rows,'original_unchanged':True},indent=2)+'\n');print('PASS seven damaged connected artifact copies')
