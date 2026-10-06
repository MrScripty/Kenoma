import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
function rejectMutation(change,expected){
 const run=JSON.parse(fs.readFileSync(root+'data/anatomical-arm-v1/audit/anatomical-dense-trajectory.json'));
 // Even completion/acceptance flags cannot authorize changed physical lineage.
 Object.assign(run,{result:'ACCEPTED_DENSE_TRAJECTORY',completedAllSteps:true,behaviorAccepted:true});change(run);
 const directory=fs.mkdtempSync(path.join(os.tmpdir(),'kenoma-dense-lineage-')),input=path.join(directory,'input.json'),output=path.join(directory,'recheck.json');
 try{
  fs.writeFileSync(input,JSON.stringify(run));
  const r=spawnSync(process.execPath,['--max-old-space-size=8192',root+'tools/verify-anatomical-dense-trajectory.mjs','--input',input,'--output',output],{encoding:'utf8',timeout:120000});
  assert.equal(r.status,1,r.error?.message||r.stdout+r.stderr);assert.match(r.stderr,expected);assert.equal(fs.existsSync(output),false);
 }finally{fs.rmSync(directory,{recursive:true,force:true});}
}
test('dense replay rejects inconsistent held joint coordinates despite accepted flags',()=>rejectMutation(r=>r.held.state.coordinatesM[459]+=.001,/(?:held )?joint coordinate/));
test('dense replay rejects invalid accepted-state time advancement',()=>rejectMutation(r=>r.snapshots[0].timeS+=.001,/time lineage/));
