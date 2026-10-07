/** Enforced encoded-byte envelopes, closed filenames and finite JSON. */
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';
import {EvidenceStore,ResourceRefusal} from './fixed-field-integration-runtime.mjs';
import {treeBytes} from './element247-shell-runtime.mjs';
import {SCHEDULE,NORMALIZED_RECIPES,normalizationKey,regionKey,STATES,BUDGET} from './selective-fixed-patch-protocol.mjs';
import {shells} from './element247-shell-protocol.mjs';
export const EMERGENCY_BYTES=2097152;
export function outputPlan(){
 const files={};const add=(name,bytes)=>{assert.ok(!files[name]);files[name]=bytes;};
 for(const r of NORMALIZED_RECIPES)for(const s of shells(r.depth))add(`${normalizationKey(r)}-${s.id}-points.f64le`,125*r.radialParts*r.angularParts**2*48);
 for(const r of SCHEDULE)for(const s of shells(r.depth))add(`${regionKey(r,s.id)}-weights.f64le`,125*r.radialParts*r.angularParts**2*8);
 for(const state of STATES)for(const r of SCHEDULE){for(const s of shells(r.depth))add(`${state}-${regionKey(r,s.id)}-region.json`,8192);add(`${state}-${r.element}-${r.id}-stage.json`,131072);}
 for(const state of STATES){for(const q of ['Q0','Q1','Q2'])add(`${state}-${q}-hybrid.json`,1048576);for(const pair of ['Q0-Q1','Q1-Q2','Q0-Q2','F44-R44'])add(`${state}-${pair}-comparison.json`,2097152);}
 add('saved-arrays.json',131072);add('material-start.json',524288);add('completion-receipt.json',524288);add('terminal-completion.json',16384);
 const normalMaterialBytes=Object.values(files).reduce((a,b)=>a+b,0),externalBytes=8*65536+2*65536,maximumCombinedBytes=normalMaterialBytes+externalBytes+EMERGENCY_BYTES;
 assert.ok(maximumCombinedBytes<=BUDGET.maximumOutputBytes-1);return {schema:1,files,normalFileCount:Object.keys(files).length,normalMaterialBytes,externalRecordSlots:8,externalRecordCapBytes:65536,externalLogSlots:2,externalLogCapBytes:65536,externalBytes,emergencyBytes:EMERGENCY_BYTES,maximumCombinedBytes,maximumOutputBytes:BUDGET.maximumOutputBytes,binaryBytes:Object.entries(files).filter(([n])=>n.endsWith('.f64le')).reduce((a,[,v])=>a+v,0),encoding:'compact UTF-8 JSON plus LF; finite binary64 numbers; bounded strings/keys/depth; per-file encoded byte limits enforced before write',emergencyInventory:{childIncompleteReceiptBytes:1048576,partialWeightBytes:65536,supervisorRefusalRecordBytes:65536,externalRefusalRecordBytes:65536,additionalReserveBytes:851968}};
}
export function boundedJson(value,maximumBytes){
 const seen=new Set();function check(v,depth){assert.ok(depth<=32,'JSON depth');if(typeof v==='number')assert.ok(Number.isFinite(v),'Nonfinite JSON');else if(typeof v==='string')assert.ok(Buffer.byteLength(v)<=512,'Oversize JSON string');else if(v&&typeof v==='object'){assert.ok(!seen.has(v),'Cyclic JSON');seen.add(v);if(Array.isArray(v)){assert.ok(v.length<=2000,'Oversize JSON array');for(const x of v)check(x,depth+1);}else{const entries=Object.entries(v);assert.ok(entries.length<=2000,'Oversize JSON object');for(const [k,x] of entries){assert.ok(Buffer.byteLength(k)<=256);check(x,depth+1);}}seen.delete(v);}else assert.ok(v===null||typeof v==='boolean','Undefined/non-JSON value');}check(value,0);
 const bytes=Buffer.from(JSON.stringify(value)+'\n');assert.ok(bytes.length<=maximumBytes,`Encoded JSON exceeds ${maximumBytes} byte envelope`);return bytes;
}
export class PatchEvidenceStore extends EvidenceStore{
 constructor(runRoot){super(path.join(runRoot,'material'),{maximumBytes:BUDGET.maximumOutputBytes,emergencyBytes:EMERGENCY_BYTES});this.runRoot=runRoot;this.plan=outputPlan();this.checkStorage('created');}
 checkStorage(phase){if(!this.runRoot)return super.checkStorage(phase);this.bytes=treeBytes(this.runRoot);if(this.bytes>BUDGET.maximumOutputBytes-EMERGENCY_BYTES)throw new ResourceRefusal('STORAGE_LIMIT',{phase,combinedBytes:this.bytes});}
 write(name,data,options={}){const cap=options.emergency?(name==='incomplete-receipt.json'?1048576:name==='partial-weights.f64le'?65536:0):this.plan.files[name];assert.ok(cap>0,'Unplanned filename');const bytes=Buffer.isBuffer(data)?data:Buffer.from(data);assert.ok(bytes.length<=cap,'File envelope');if(name.endsWith('.f64le')){assert.equal(bytes.length%8,0);for(let i=0;i<bytes.length;i+=8)assert.ok(Number.isFinite(bytes.readDoubleLE(i))&&bytes.readDoubleLE(i)>0,'Finite positive binary payload');}return super.write(name,bytes,options);}
 json(name,value,options={}){return this.write(name,boundedJson(value,options.emergency?1048576:this.plan.files[name]),options);}
 failure(error,context,limits){this.bytes=treeBytes(this.runRoot);const clip=x=>String(x).slice(0,256);return this.json('incomplete-receipt.json',{schema:1,result:'INCOMPLETE_FIXED_PATCH_INTEGRATION',reason:clip(error.reason??error.message),runtime:limits.receipt(),context:JSON.parse(JSON.stringify(context,(_k,v)=>typeof v==='number'&&!Number.isFinite(v)?'NONFINITE':v)),retainedFiles:this.files,combinedBytesBeforeReceipt:this.bytes},{emergency:true});}
}
