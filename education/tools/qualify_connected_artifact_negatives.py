"""Damaged connected integration copies must fail the same delivered gates."""
from pathlib import Path
import json,tempfile,shutil,sys
from check_connected_artifact import check,sha,ROOT
out=ROOT/'dist';rows=[];check(out);before={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file() and '__pycache__' not in str(p)}
for name in ['missing-integration','changed-worker','wrong-figure','missing-proof']:
 with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as folder:
  copy=Path(folder)/'dist';shutil.copytree(out,copy)
  if name=='missing-integration':(copy/'connected-integration.json').unlink()
  elif name=='changed-worker':p=copy/'connected-passive/assets/axisymmetric-worker.js';p.write_text(p.read_text()+'\nthrow Error("damaged")')
  elif name=='wrong-figure':p=copy/'assets/connected-specimen.svg';p.write_text(p.read_text().replace('16 axial','32 axial'))
  else:(copy/'axisymmetric-proof-status.json').unlink()
  try:check(copy)
  except (AssertionError,FileNotFoundError) as error:rows.append({'case':name,'detected':True,'reason':str(error)})
  else:raise RuntimeError('FALSE_PASS '+name)
assert before=={name:sha(out/name) for name in before}
(out/'connected-negative-artifacts.json').write_text(json.dumps({'result':'PASS_FOUR_DAMAGED_CONNECTED_ARTIFACTS','cases':rows,'original_unchanged':True},indent=2)+'\n');print('PASS four damaged connected artifact copies')
