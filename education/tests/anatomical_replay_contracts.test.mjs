import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {heldDomain,sameMass,coarseCoverage,fineCoverage,denseCoverage,matchCoverage,validateContinuation} from '../tools/anatomical-replay-contracts.mjs';
import {recordedInputMatches} from '../tools/recorded-inputs.mjs';
const read=name=>JSON.parse(fs.readFileSync(new URL('../data/anatomical-arm-v1/audit/'+name,import.meta.url))),copy=structuredClone;

test('held rest rejects scalar advancement even when its saved coordinates are unchanged',()=>{
 const s=read('arm-rest-results.json').state,n=s.coordinatesM.length;heldDomain(s,n,n-1,s.qRad);
 for(const [key,value] of [['activation',.9],['timeS',123],['omegaRadPerS',99],['qRad',1],['massKg',NaN]])assert.throws(()=>heldDomain({...s,[key]:value},n,n-1,s.qRad),key);
});
test('model matching requires all distinct heads, prescribed end rings and finite force targets',()=>{
 const m=read('modal-fixed-end-results.json');matchCoverage(m);
 const cases=[x=>x.records=[],x=>x.records[0].modelReference.value=undefined,x=>x.records[0].match.sigma0Pa=NaN,x=>x.records[1].elementId=x.records[0].elementId,x=>x.records[0].match.coordinatesM[0]=.01];
 for(const change of cases){const x=copy(m);change(x);assert.throws(()=>matchCoverage(x));}
});
test('accepted dense, bulk and enriched comparison candidates retain the old finite mass',()=>{
 for(const name of ['anatomical-dense-step.json','anatomical-bulk-step-0.5.json','anatomical-enriched-step.json']){const r=read(name);sameMass(r.candidate,r.oldState);for(const massKg of [999,NaN,undefined])assert.throws(()=>sameMass({...r.candidate,massKg},r.oldState),name);}
});
test('coarse completion and interrupted fine prefixes require nonempty matching coverage',()=>{
 const coarse=read('contact-lift-release-results.json'),fine=read('contact-fine-release-results.json');coarseCoverage(coarse);fineCoverage(fine);
 const truncated=copy(coarse);truncated.snapshots.pop();assert.throws(()=>coarseCoverage(truncated));
 assert.throws(()=>fineCoverage({...fine,snapshots:[],attempts:[]}));
 assert.throws(()=>fineCoverage({...fine,requestedSteps:Infinity}));
});
test('dense rejected attempts require the original schedule, finite residual and explicit rollback',()=>{
 const r=read('anatomical-dense-trajectory.json'),b=read('contact-lift-release-results.json');denseCoverage(r,b);
 const rejected=copy(r);rejected.result='REJECTED_INCREMENT';rejected.completedAllSteps=false;rejected.snapshots.pop();Object.assign(rejected.attempts.at(-1),{accepted:false,residualN:.01});rejected.rollback={sameStateObject:true,stateUnchanged:true,oldContactRestored:true};denseCoverage(rejected,b);
 for(const mutate of [x=>x.attempts.at(-1).hS=0,x=>x.attempts.at(-1).residualN=NaN,x=>x.rollback={},x=>x.rollback.stateUnchanged=false,x=>x.attempts.push(copy(x.attempts.at(-1)))]){const x=copy(rejected);mutate(x);assert.throws(()=>denseCoverage(x,b));}
});
test('new continuation rejects stale source digests and corrupted accepted state lineage',()=>{
 const base=read('contact-coarse-release-base.json'),hash=p=>base.sourceHashes[p];validateContinuation(base,hash);
 const stale=copy(base);stale.sourceHashes['web/anatomical-material.mjs']='0'.repeat(64);assert.throws(()=>validateContinuation(stale,hash),/Stale continuation/);
 for(const mutate of [x=>x.snapshots.at(-1).massKg=999,x=>x.snapshots.at(-1).timeS=123,x=>x.attempts[0].accepted=false,x=>x.snapshots=[]]){const x=copy(base);mutate(x);assert.throws(()=>validateContinuation(x,hash));}
});
test('recorded-source transition preserves exact prior contact bytes and rejects unknown hashes',()=>{
 const manifest=JSON.parse(fs.readFileSync(new URL('../tools/release-source-transition.json',import.meta.url))),entry=manifest.files['web/anatomical-contact.mjs'];
 assert.ok(recordedInputMatches('web/anatomical-contact.mjs',entry.recordedSHA256));
 assert.equal(recordedInputMatches('web/anatomical-contact.mjs','0'.repeat(64)),false);
 assert.equal(recordedInputMatches('../web/anatomical-contact.mjs',entry.recordedSHA256),false);
 const old=fs.readFileSync(new URL('../'+entry.archivePath,import.meta.url),'utf8'),current=fs.readFileSync(new URL('../web/anatomical-contact.mjs',import.meta.url),'utf8');
 assert.equal(current,old.replace('const joint=columns.find(([i])=>i===model.jointIndex);if(joint)boneTorqueNm-=k*deficit*joint[1]*JOINT_SCALE_M;','const joint=columns.reduce((sum,[i,v])=>sum+(i===model.jointIndex?v:0),0);boneTorqueNm-=k*deficit*joint*JOINT_SCALE_M;'));
});
