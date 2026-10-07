/** Closed finite encoded-byte envelopes and streaming append-only evidence. */
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';
import {EvidenceStore,ResourceRefusal} from './fixed-field-integration-runtime.mjs';
import {treeBytes} from './element247-shell-runtime.mjs';
import {shells} from './element247-shell-protocol.mjs';
import {BUDGET,STATES,SCHEDULE,NORMALIZED_RECIPES,CANDIDATES,COMPARISONS,QUIET_PAIRS,regionKey,newRegion,newNormalized,normalizedKey,regionPointCount} from './fine-window-protocol.mjs';
export const EMERGENCY_BYTES=4194304;
export function outputPlan(){
 const files={};const add=(name,bytes)=>{assert.ok(!files[name]);files[name]=bytes;};
 for(const r of NORMALIZED_RECIPES)for(const s of shells(r.depth))if(newNormalized(r,s))add(`${normalizedKey(r)}-${s.id}-points.f64le`,regionPointCount(r,s)*48);
 for(const r of SCHEDULE)for(const s of shells(r.depth))if(newRegion(r,s))add(`${regionKey(r,s.id)}-weights.f64le`,regionPointCount(r,s)*8);
 for(const state of STATES){for(const r of SCHEDULE){for(const s of shells(r.depth))if(newRegion(r,s))add(`${state}-${regionKey(r,s.id)}-region.json`,8192);add(`${state}-${r.element}-${r.id}-stage.json`,131072);}for(const q of CANDIDATES)add(`${state}-${q}-hybrid.json`,1048576);for(const c of COMPARISONS)add(`${state}-${c.a}-${c.b}-comparison.json`,2097152);for(const [a,b] of QUIET_PAIRS)add(`${state}-quiet-${a}-${b}-comparison.json`,2097152);}
 add('material-start.json',1048576);add('completion-receipt.json',1048576);add('saved-arrays.json',131072);add('terminal-completion.json',16384);add('provenance-inventory.json',2097152);
 const normalMaterialBytes=Object.values(files).reduce((a,b)=>a+b,0),externalBytes=10*65536,maximumCombinedBytes=normalMaterialBytes+externalBytes+EMERGENCY_BYTES,binaryBytes=Object.entries(files).filter(([p])=>p.endsWith('.f64le')).reduce((a,[,b])=>a+b,0);
 assert.equal(binaryBytes,345840000);assert.equal(maximumCombinedBytes,448240000);assert.ok(maximumCombinedBytes<BUDGET.maximumOutputBytes);
 return {schema:1,files,normalFileCount:Object.keys(files).length,binaryBytes,normalMaterialBytes,externalBytes,emergencyBytes:EMERGENCY_BYTES,maximumCombinedBytes,maximumOutputBytes:BUDGET.maximumOutputBytes,maximumRegionPoints:48000,partialWeightCapBytes:524288,encoding:'finite compact UTF-8 JSON plus LF; bounded4096 entries,strings512,keys256,depth32; actual bytes checked before exclusive durable write'};
}
export function boundedJson(value,cap){
 const seen=new Set();function check(v,d){assert.ok(d<=32);if(typeof v==='number')assert.ok(Number.isFinite(v));else if(typeof v==='string')assert.ok(Buffer.byteLength(v)<=512);else if(v&&typeof v==='object'){assert.ok(!seen.has(v));seen.add(v);const items=Array.isArray(v)?v:Object.entries(v);assert.ok(items.length<=4096);if(Array.isArray(v))for(const item of items)check(item,d+1);else for(const [k,x] of items){assert.ok(Buffer.byteLength(k)<=256);check(x,d+1);}seen.delete(v);}else assert.ok(v===null||typeof v==='boolean');}check(value,0);const data=Buffer.from(JSON.stringify(value)+'\n');assert.ok(data.length<=cap,`Encoded ${data.length} exceeds ${cap}`);return data;
}
// These pure record constructors are shared by production and its shape certificate.
export function startRecord(v){return {schema:1,...v,activation:1,scope:'New fine window, original coarse failures unchanged, outside236unqualified'};}
export function provenanceRecord(v){return {schema:1,...v};}
export function completionRecord(v){return {schema:1,...v,newCallbacks:19716000,sharedLogicalMeasurements:640000,logicalRegions:2002,newRegions:1682,sharedRegions:320,unchangedStates:true,newNodalFields:0,nonlinearSolves:0,optimizerTrials:0,refits:0,outsidePatchElements:236,outsidePatchQualified:false,anatomicalQualification:false,originalResultCommit:'38ae8a2e2af57cf33254af987b724824b9d84357',originalResult:'UNRESOLVED_FIXED_PATCH_INTEGRATION',originalTwoShellExecutionExit:1};}
export function terminalRecord(v){return {schema:1,kind:'TERMINAL_COMPLETION',...v};}
export function incompleteRecord({error,context,runtime,retainedFiles,combinedBytesBeforeReceipt}){const clipped=JSON.parse(JSON.stringify(context,(_k,v)=>typeof v==='number'&&!Number.isFinite(v)?'NONFINITE':typeof v==='string'?v.slice(0,512):v));return {schema:1,result:'INCOMPLETE_FIXED_PATCH_INTEGRATION',reason:String(error.reason??error.message).slice(0,256),runtime,context:clipped,retainedFiles,combinedBytesBeforeReceipt};}
export class FineEvidenceStore extends EvidenceStore{
 constructor(runRoot){super(path.join(runRoot,'material'),{maximumBytes:BUDGET.maximumOutputBytes,emergencyBytes:EMERGENCY_BYTES});this.runRoot=runRoot;this.plan=outputPlan();this.checkStorage('created');}
 checkStorage(phase){if(!this.runRoot)return super.checkStorage(phase);this.bytes=treeBytes(this.runRoot);if(this.bytes>BUDGET.maximumOutputBytes-EMERGENCY_BYTES)throw new ResourceRefusal('STORAGE_LIMIT',{phase,combinedBytes:this.bytes});}
 write(name,data,options={}){const cap=options.emergency?({'incomplete-receipt.json':1048576,'partial-weights.f64le':524288}[name]??0):this.plan.files[name];assert.ok(cap>0,'Unplanned filename');const bytes=Buffer.isBuffer(data)?data:Buffer.from(data);assert.ok(bytes.length<=cap,'File byte envelope');if(name.endsWith('.f64le')){assert.equal(bytes.length%8,0);for(let i=0;i<bytes.length;i+=8)assert.ok(Number.isFinite(bytes.readDoubleLE(i))&&bytes.readDoubleLE(i)>0,'Positive finite binary payload');}return super.write(name,bytes,options);}
 json(name,value,options={}){return this.write(name,boundedJson(value,options.emergency?1048576:this.plan.files[name]),options);}
 failure(error,context,limits){this.bytes=treeBytes(this.runRoot);return this.json('incomplete-receipt.json',incompleteRecord({error,context,runtime:limits.receipt(),retainedFiles:this.files,combinedBytesBeforeReceipt:this.bytes}),{emergency:true});}
}
