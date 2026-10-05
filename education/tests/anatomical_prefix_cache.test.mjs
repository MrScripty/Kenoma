import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
test('standalone finer replay rejects a cached primary check with a changed verifier digest',()=>{
 const fixture=fs.mkdtempSync(path.join(os.tmpdir(),'kenoma-prefix-cache-'));
 try{
  fs.mkdirSync(fixture+'/tools');
  for(const entry of fs.readdirSync(root+'tools')){
   if(entry==='verify-anatomical-release-prefix.mjs')fs.copyFileSync(root+'tools/'+entry,fixture+'/tools/'+entry);
   else fs.symlinkSync(root+'tools/'+entry,fixture+'/tools/'+entry);
  }
  fs.symlinkSync(root+'web',fixture+'/web','dir');
  const base='data/anatomical-arm-v1/';fs.mkdirSync(fixture+'/'+base+'audit',{recursive:true});
  for(const entry of fs.readdirSync(root+base))if(entry!=='audit')fs.symlinkSync(root+base+entry,fixture+'/'+base+entry);
  for(const entry of fs.readdirSync(root+base+'audit')){
   if(entry==='contact-lift-release-recheck.json'){
    const cached=JSON.parse(fs.readFileSync(root+base+'audit/'+entry));cached.verifierSHA256='0'.repeat(64);
    fs.writeFileSync(fixture+'/'+base+'audit/'+entry,JSON.stringify(cached));
   }else fs.symlinkSync(root+base+'audit/'+entry,fixture+'/'+base+'audit/'+entry);
  }
  const result=spawnSync(process.execPath,[fixture+'/tools/verify-anatomical-release-prefix.mjs'],{encoding:'utf8',timeout:10000});
  assert.equal(result.status,1,result.error?.message||result.stdout+result.stderr);
  assert.match(result.stderr,/Stale primary replay verifier digest/);
 }finally{fs.rmSync(fixture,{recursive:true,force:true});}
});
