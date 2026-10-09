import test from 'node:test';import assert from 'node:assert/strict';import {execFileSync} from 'node:child_process';import {readFileSync} from 'node:fs';
import {Budget,BudgetExceeded,instrument,sha256,createObserver,detached,transaction,observationStatus,compareRuns} from '../tools/arm-validation/core.mjs';
import {validateModules,installLoader} from '../tools/arm-validation/loader.mjs';
import {verifyLeaves} from '../tools/arm-validation/replay.mjs';
import {POLICY,INPUTS} from '../tools/arm-validation/prepare.mjs';
import {advanceArmInterval} from '../web/anatomical-arm-substeps.mjs';
const caps=()=>({attempts:3,configurationEntries:2,muscleMaterial:2,tendonMaterial:2,materialTensor:2,hessianProducts:3});
test('each accounting boundary allows last entry; next denied before synthetic work',()=>{
 for(const kind of Object.keys(caps())){const b=new Budget(caps());let work=0;for(let i=0;i<caps()[kind];i++){b.charge(kind);work++;}assert.throws(()=>{b.charge(kind);work++;},BudgetExceeded);assert.equal(work,caps()[kind]);assert.equal(b.counts[kind],work);assert.equal(b.denied[kind],1);}
});
test('budget exception is not RangeError; latch cannot be cleared by helper catch',()=>{
 const b=new Budget({...caps(),configurationEntries:0});let calls=0,rule=0;
 const r=advanceArmInterval({history:[]},{h:.01,maxDepth:1,capture:()=>rule,restore:r=>{rule=r;},attempt:s=>{calls++;rule++;b.charge('configurationEntries');return {accepted:true,state:s};}});
 assert.equal(r.accepted,false);assert.equal(calls,1);assert.equal(rule,0);assert.ok(b.latch instanceof BudgetExceeded);assert.equal(b.latch instanceof RangeError,false);
 assert.throws(()=>b.charge('muscleMaterial'),e=>e===b.latch);assert.equal(b.counts.muscleMaterial,0);
});
test('partial/repeated/rejected entry accounting is cumulative across attempts and replay',()=>{
 const b=new Budget({...caps(),configurationEntries:4});b.beginAttempt();b.charge('configurationEntries');b.charge('muscleMaterial');b.beginAttempt();b.charge('configurationEntries');b.charge('configurationEntries');b.charge('configurationEntries');assert.throws(()=>b.charge('configurationEntries'),BudgetExceeded);assert.equal(b.counts.configurationEntries,4);assert.equal(b.counts.attempts,2);
});
test('per-attempt Hessian limit resets and aggregate limit remains active',()=>{
 const b=new Budget({...caps(),hessianProducts:7057680});b.beginAttempt();b.charge('hessianProducts',3528840);assert.throws(()=>b.charge('hessianProducts'),BudgetExceeded);assert.equal(b.denied.hessianProducts,1);
 const c=new Budget({...caps(),hessianProducts:7057680});c.beginAttempt();c.charge('hessianProducts',3528840);c.beginAttempt();c.charge('hessianProducts',3528840);assert.equal(c.counts.hessianProducts,7057680);
});
test('internal lexical tendon call is charged by insertion before synthetic work',()=>{
 const source="const TENDON_FIXTURE={};export function tendonMaterial(epsilon,p=TENDON_FIXTURE){return epsilon+1;}export function tendonSegment(x){return tendonMaterial(x);}";
 const code=instrument('education/web/anatomical-material.mjs',"const MUSCLE_FIXTURE={};export function muscleMaterial(F,f0,a,p=MUSCLE_FIXTURE){return F;}"+source).replaceAll('export function','function');
 const b=new Budget({...caps(),tendonMaterial:1});globalThis.__kenomaValidation={budget:b};try{const f=new Function(code+';return tendonSegment;')();assert.equal(f(4),5);assert.throws(()=>f(4),BudgetExceeded);assert.equal(b.counts.tendonMaterial,1);}finally{delete globalThis.__kenomaValidation;}
});
test('instrumentation requires exact cardinality and preserves unmodified dependencies',()=>{
 assert.throws(()=>instrument('education/web/anatomical-arm.mjs','wrong'),/cardinality/);assert.throws(()=>instrument('education/web/anatomical-newton.mjs','hessianProducts++;'),/cardinality/);assert.equal(instrument('education/web/unchanged.mjs','export const x=1;'),'export const x=1;');
});
test('loader validates both original and transformed hashes without physical import',()=>{
 const text='export const synthetic=1;',p='education/web/synthetic.mjs',m={[p]:{text,sha256:sha256(text),transformedSHA256:sha256(text)}};validateModules(m);assert.throws(()=>validateModules({[p]:{...m[p],text:text+' '}}),/Changed/);assert.throws(()=>validateModules({[p]:{...m[p],transformedSHA256:'0'.repeat(64)}}),/Changed/);
});
test('virtual loader rejects unlisted dependencies and loads only synthetic source',async()=>{
 const text='export const synthetic=7;',p='education/web/metadata-only.mjs',m={[p]:{text,sha256:sha256(text),transformedSHA256:sha256(text)}};const hook=installLoader(m);try{assert.equal((await import('kenoma:'+p)).synthetic,7);await assert.rejects(()=>import('kenoma:education/web/unlisted.mjs'),/Unlisted/);}finally{hook.deregister();}
});
test('late explicit-half refusal rolls back externally supplied input and contact values',async()=>{
 const b=new Budget(caps()),state={timeS:0,history:[],massEvents:[{value:2}]};let contact={knots:['original']};const before=detached(state);
 const r=await transaction({state,capture:()=>detached(contact),restore:r=>{contact=detached(r);},budget:b,operation:async()=>{contact.knots.push('first half');return {accepted:false,state:{timeS:.005,history:[1],massEvents:[]}};}});
 assert.equal(r.accepted,false);assert.deepEqual(r.state,before);assert.deepEqual(state,before);assert.deepEqual(contact,{knots:['original']});
});
test('caught budget cannot turn a provisional first half into an accepted final interval',async()=>{
 const b=new Budget({...caps(),configurationEntries:0}),state={timeS:0};let contact=0;
 const r=await transaction({state,capture:()=>contact,restore:r=>{contact=r;},budget:b,operation:async()=>{contact=1;try{b.charge('configurationEntries');}catch{}return {accepted:true,state:{timeS:.01}};}});
 assert.equal(r.accepted,false);assert.equal(r.status,'RESOURCE_INCONCLUSIVE');assert.equal(contact,0);assert.deepEqual(r.state,state);
});
test('contact alias and earlier progress cannot masquerade as final accepted state',async()=>{
 let rule={knots:['original']};const externalAlias=rule.knots,state={history:[]},b=new Budget(caps()),events=[];
 const o=createObserver(b,e=>events.push(e));const r=await transaction({state,capture:()=>detached(rule),restore:r=>{rule=detached(r);},budget:b,operation:async()=>{
  rule.knots.push('provisional');o.progress({iteration:1,maxGradient:3,fullCoordinates:[999]});return {accepted:false,state};}});
 assert.deepEqual(externalAlias,['original','provisional']);assert.deepEqual(rule.knots,['original']);assert.equal(r.accepted,false);
 assert.equal(events[0].status,'PROVISIONAL_NOT_COMMITTED');assert.equal(Object.hasOwn(events[0],'accepted'),false);assert.equal(Object.hasOwn(events[0],'fullCoordinates'),false);
 const stable=detached(rule);externalAlias.push('later stale mutation');assert.deepEqual(stable,{knots:['original']});assert.match(observationStatus.contactAliases,/UNTRUSTED/);
});
test('observer retains detached leaf copies and enforces observation output budget',()=>{
 const b=new Budget(caps()),o=createObserver(b,()=>{},10000),s={history:[]},receipt={nested:[1]},arm={parameters:{stepS:.01}};
 const result=o.attempt(arm,s,{effort:.04},()=>({accepted:true,state:{history:[receipt]},receipt}));receipt.nested.push(999);assert.deepEqual(o.records()[0].receipt.nested,[1]);assert.throws(()=>o.select(result),/mismatch/);
 const tiny=createObserver(new Budget(caps()),()=>{},1);assert.throws(()=>tiny.attempt(arm,s,{},()=>({accepted:true,state:s,receipt:{}})),BudgetExceeded);
});
test('no closures/Hessians or nonfinite values silently disappear from scientific receipt',()=>{
 assert.throws(()=>detached({closure:()=>{}}),/Function/);assert.throws(()=>detached({gradient:Infinity}),/Nonfinite/);
});
test('replay performs exactly four synthetic configurations per leaf and checks full ledger lineage',()=>{
 const p={stationarityToleranceN:1e-4,gMPerS2:0,segmentMassKg:0,stopStiffnessNmPerRad:0,minimumAngleRad:-1,maximumAngleRad:1,jointDampingNmS:0},rule={schema:1};let calls=0,currentRule;
 const api={JOINT_SCALE_M:1,restoreContactRecipe:(_c,r)=>{currentRule=detached(r);},contactRecipe:()=>currentRule,stateLineage:()=>{},attachmentMap:()=>({position:[0,0,0],B:[0,0,0]}),finitePoseAudit:()=>({transverseCrossingPairs:0}),finiteRoutingAudit:()=>({accepted:true}),anatomicalConfiguration:(_a,_x,activation)=>{calls++;return {gradient:[0,0],positions:[],physicalPotentialJ:3+activation,energies:{activePotentialJ:activation},headResults:[{minJ:1}],contact:{maximumSampledBonePenetrationM:0,maximumSampledSoftPenetrationM:0,maximumSampledTendonPenetrationM:0}};}};
 const initial={coordinatesM:[0,0],qRad:0,omegaRadPerS:0,activation:0,timeS:0,step:0,effort:0,massKg:.5,massEvents:[],history:[],mechanicalWorkJ:0,contactRule:rule};
 const receipt={activeMechanicalWorkJ:0,maximumFreeModalGradientN:0,referenceQuadratureUpdateJ:0,oldMechanicalJ:3,newMechanicalJ:3,nonlinearWorkDefectJ:0,impulseResidualNmS:0};const s={...initial,activation:.01,timeS:.01,step:1,effort:.04,history:[receipt]};const leaf={oldState:initial,state:s,receipt,hS:.01,effort:.04};const arm={parameters:p,model:{ndof:2,jointIndex:1,frame:{}},contact:{},initialContactRule:rule,baseInertiaKgM2:0,gripRadiusSquaredM2:0};
 assert.equal(verifyLeaves(api,arm,initial,[leaf],.01).length,1);assert.equal(calls,4);
 for(const patch of [{step:2},{effort:0},{mechanicalWorkJ:1},{massEvents:[1]},{history:[]}])assert.throws(()=>verifyLeaves(api,arm,initial,[{...leaf,state:{...s,...patch}}],.01));
});
test('comparison distinguishes compatible controls, one-interval remedy, and refusal',()=>{
 const leaf={receipt:{r:1}},whole={status:'PASS',finalState:{time:1},leaves:[leaf]},halves={status:'PASS',finalState:{time:1},leaves:[leaf,leaf]},refusal={status:'SOLVER_REFUSAL'};
 assert.equal(compareRuns(whole,whole,halves).result,'CONTROL_COMPATIBLE_REMEDY_UNPROVEN');assert.equal(compareRuns(refusal,halves,halves).result,'RECOVERY_SUPPORTED_FOR_THIS_REDUCED_INTERVAL_ONLY');assert.equal(compareRuns(refusal,refusal,refusal).result,'DEPTH_ONE_RECOVERY_REFUSED_FOR_THIS_INTERVAL');assert.throws(()=>compareRuns(refusal,halves,whole),/mismatch/);
});
test('fixed policy totals and exact input inventory are independently countable',()=>{
 assert.equal(POLICY.runs.reduce((s,r)=>s+r.attempts,0),3);assert.equal(POLICY.runs.reduce((s,r)=>s+r.configurationEntries,0),1025);assert.equal(POLICY.runs.reduce((s,r)=>s+r.wallSeconds,0),540);assert.equal(POLICY.runs.reduce((s,r)=>s+r.muscleMaterial,0),57859200);assert.equal(POLICY.runs.reduce((s,r)=>s+r.tendonMaterial,0),648825);assert.equal(POLICY.runs.reduce((s,r)=>s+r.materialTensor,0),57802752);assert.equal(POLICY.ownedRSSBytes,1000000000);assert.equal(POLICY.cgroupBytes,16000000000);assert.equal(Object.keys(INPUTS).length,6);
});
test('actual worker orchestration runs A/D/B and late D refusal against synthetic operators only',()=>{
 for(const id of ['A','D','B','D-fail','B-budget','B-returned-exception','D-first-exception']){
  const result=JSON.parse(execFileSync(process.execPath,['education/tests/arm-validation-synthetic-worker.mjs',id],{cwd:new URL('../..',import.meta.url),encoding:'utf8'}));
  assert.equal(result.syntheticOnly,true);assert.equal(result.physicalImports,0);assert.equal(result.packet.executionScope,'SYNTHETIC_TEST_ONLY');assert.equal(result.packet.finalAcceptance,false);assert.equal(result.packet.modelDisposed,true);
  if(id==='B-returned-exception'||id==='D-first-exception')assert.equal(result.packet.status,'EXCEPTION');else if(id==='D-fail')assert.equal(result.packet.status,'SOLVER_REFUSAL');else if(id==='B-budget')assert.equal(result.packet.status,'RESOURCE_INCONCLUSIVE');else assert.equal(result.packet.status,'PASS');
 }
});
test('independent D starts fresh and directly uses two halves; B starts a separate fresh state',()=>{
 for(const id of ['D','B']){
  const {packet}=JSON.parse(execFileSync(process.execPath,['education/tests/arm-validation-synthetic-worker.mjs',id],{cwd:new URL('../..',import.meta.url),encoding:'utf8'}));
  assert.equal(packet.leaves.length,id==='D'?2:1);
  assert.deepEqual(packet.leaves.map(l=>l.hS),id==='D'?[.005,.005]:[.01]);
  const first=packet.leaves[0].oldState;
  assert.equal(first.timeS,0);assert.equal(first.step,0);assert.deepEqual(first.history,[]);assert.deepEqual(first.massEvents,[]);
  assert.ok(first.coordinatesM.every(x=>x===0));
  if(id==='D'){assert.equal(packet.leaves[1].oldState.timeS,.005);assert.equal(packet.leaves[1].oldState.step,1);}
 }
});
test('observer captures both accepted helper halves before they can become later provisional failures',()=>{
 const b=new Budget({...caps(),attempts:3}),o=createObserver(b,()=>{}),arm={parameters:{stepS:.01}},initial={timeS:0,history:[]};let contact=0;
 const attempt=(s,h)=>o.attempt(arm,s,{h,effort:.04},()=>{
  contact++;if(h>.005)return {accepted:false,state:s};const receipt={hS:h};return {accepted:true,state:{timeS:s.timeS+h,history:[...s.history,receipt]},receipt};});
 const r=advanceArmInterval(initial,{h:.01,maxDepth:1,capture:()=>contact,restore:c=>{contact=c;},attempt});
 assert.equal(r.accepted,true);assert.equal(o.select(r).length,2);assert.equal(o.select(r)[0].oldState.timeS,0);assert.equal(o.select(r)[1].oldState.timeS,.005);assert.deepEqual(initial.history,[]);
});
test('virtual physical module cannot import foreign URLs or builtin I/O',async()=>{
 const p='education/web/synthetic-forbidden.mjs',text="import fs from 'node:fs'; export const value=1;",m={[p]:{text,sha256:sha256(text),transformedSHA256:sha256(text)}};const hook=installLoader(m);try{await assert.rejects(()=>import('kenoma:'+p),/Unlisted physical dependency/);}finally{hook.deregister();}
});

test('unsupervised worker API refuses actual scope before any physical import',async()=>{
 const {numericalWorker,validateWorkerEntry}=await import('../tools/arm-validation/worker.mjs');await assert.rejects(()=>numericalWorker({scope:'ACTUAL',operatorCommit:'ACTUAL'},'A'),/context required/);assert.throws(()=>validateWorkerEntry({},'/tmp/synthetic','synthetic',{}),/Missing supervisor result channel/);
});
