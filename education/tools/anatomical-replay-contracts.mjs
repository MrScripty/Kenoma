/** Metadata/coverage contracts before numerical replay. No solver or changed gate. */
import {JOINT_SCALE_M} from '../web/anatomical-apparatus.mjs';
export function finite(value,label){if(!Number.isFinite(value))throw Error('Nonfinite '+label);return value;}
export function near(a,b,t,label){finite(a,label);finite(b,label);if(Math.abs(a-b)>t)throw Error('Changed '+label);}
export function requestDomain(request){if(!(Number.isFinite(request?.hS)&&request.hS>0&&Number.isFinite(request.effort)&&request.effort>=0&&request.effort<=1))throw Error('Invalid finite step/effort request');}
export function stateDomain(state,n,j){
 if(!state||state.coordinatesM?.length!==n||!Array.from(state.coordinatesM).every(Number.isFinite))throw Error('Invalid state coordinates');
 for(const key of ['qRad','omegaRadPerS','activation','massKg','timeS'])finite(state[key],key);
 if(state.massKg<0||state.timeS<0||state.activation<0||state.activation>1)throw Error('State outside declared domain');
 near(state.qRad,state.coordinatesM[j]/JOINT_SCALE_M,1e-14,'joint coordinate');
}
export function heldDomain(state,n,j,angle){
 stateDomain(state,n,j);near(state.qRad,angle,1e-14,'held angle');
 for(const key of ['timeS','step','activation','omegaRadPerS','effort','mechanicalWorkJ'])near(state[key],0,0,'held '+key);
 if(!Array.isArray(state.massEvents)||state.massEvents.length)throw Error('Held mass-event lineage');
}
export function sameMass(candidate,old){finite(old.massKg,'old mass');finite(candidate.massKg,'candidate mass');if(old.massKg<0||candidate.massKg!==old.massKg)throw Error('Changed unchanged-mass lineage');}
export function stateLineage(state,old,request,parameters,n,j){
 requestDomain(request);stateDomain(old,n,j);stateDomain(state,n,j);sameMass(state,old);
 const tau=request.effort>=old.activation?parameters.activationTimeS:parameters.releaseTimeS;
 if(!(Number.isFinite(tau)&&tau>0))throw Error('Invalid activation time');
 near(state.activation,request.effort+(old.activation-request.effort)*Math.exp(-request.hS/tau),1e-14,'activation lineage');
 near(state.timeS,old.timeS+request.hS,1e-14,'time lineage');near(state.omegaRadPerS,(state.qRad-old.qRad)/request.hS,1e-14,'velocity lineage');
}
export function coarseCoverage(run,{complete=true}={}){
 const lift=run.requestedLiftSteps,release=run.requestedReleaseSteps,total=1+lift+release;
 if(!Number.isInteger(lift)||lift<=0||!Number.isInteger(release)||release<=0||!Number.isFinite(run.hS)||run.hS<=0||!Number.isFinite(run.effort)||run.effort<0||run.effort>1||run.held?.accepted!==true)throw Error('Invalid declared coarse schedule');
 if(!Array.isArray(run.snapshots)||!Array.isArray(run.attempts)||!run.snapshots.length||run.snapshots.length!==run.attempts.length||run.snapshots.length>total||!run.attempts.every(a=>a.accepted===true))throw Error('Missing accepted coarse coverage');
 if(complete&&(run.completedAllSteps!==true||run.snapshots.length!==total))throw Error('Incomplete completed coarse trajectory');
 for(const [i,a] of run.attempts.entries()){
  requestDomain(a);const label=i===0?'regression-load':i<=lift?'lift':'release';
  if(a.label!==label||a.hS!==(i===0?.01:run.hS)||a.effort!==(i<=lift?run.effort:0))throw Error('Changed coarse schedule');
 }
}
export function fineCoverage(fine){
 if(!Number.isInteger(fine.requestedSteps)||fine.requestedSteps<=0||!Number.isFinite(fine.hS)||fine.hS<=0||!Array.isArray(fine.snapshots)||!Array.isArray(fine.attempts)||!fine.snapshots.length||fine.snapshots.length!==fine.attempts.length||fine.snapshots.length>fine.requestedSteps||fine.completedAllSteps!==(fine.snapshots.length===fine.requestedSteps))throw Error('Missing expected nonempty finer coverage');
 for(const a of fine.attempts){requestDomain(a);if(a.accepted!==true||a.hS!==fine.hS||a.effort!==0||a.label!=='release')throw Error('Changed finer release schedule');}
}
export function denseCoverage(run,baseline){
 if(!Array.isArray(run.schedule)||!run.schedule.length||!Array.isArray(run.attempts)||!Array.isArray(run.snapshots))throw Error('Missing dense schedule');
 let index=0;
 for(const [bi,b] of baseline.attempts.entries()){
  const factor=run.schedule[index]?.refinementFactor??run.timeRefinementFactor;
  if(![1,2,3].includes(factor))throw Error('Invalid dense refinement factor');
  for(let part=1;part<=factor;part++){
   const s=run.schedule[index++];requestDomain(s);
   if(s.baselineIndex!==bi||s.part!==part||(s.refinementFactor??run.timeRefinementFactor)!==factor||s.label!==b.label||s.effort!==b.effort||s.hS!==b.hS/factor)throw Error('Changed dense schedule');
  }
 }
 if(index!==run.schedule.length)throw Error('Extra dense schedule requests');
 const rejected=run.result==='REJECTED_INCREMENT',count=run.snapshots.length;
 if(run.attempts.length!==count+(rejected?1:0)||!run.attempts.length||run.attempts.length>run.schedule.length||(!rejected&&(run.completedAllSteps!==true||count!==run.schedule.length)))throw Error('Inconsistent dense terminal coverage');
 for(const [i,a] of run.attempts.entries()){
  requestDomain(a);const s=run.schedule[i];for(const key of ['label','effort','hS','baselineIndex','part'])if(a[key]!==s[key])throw Error('Dense attempt/schedule lineage');
  if(a.accepted!==(i<count))throw Error('Not one terminal rejected attempt');
 }
 if(rejected){if(run.completedAllSteps!==false)throw Error('Rejected run claims completion');for(const key of ['sameStateObject','stateUnchanged','oldContactRestored'])if(run.rollback?.[key]!==true)throw Error('Missing explicit rollback '+key);finite(run.attempts.at(-1).residualN,'stored rejected residual');}
}
export function matchCoverage(matches){
 const expected=['FJ1486','FJ1512','FJ1478'];
 if(!Array.isArray(matches.records)||matches.records.length!==expected.length||new Set(matches.records.map(r=>r.elementId)).size!==expected.length||!matches.records.every(r=>expected.includes(r.elementId)))throw Error('Missing expected unique active-head matches');
 if(matches.stationarityToleranceN!==1e-4||matches.forceToleranceRelative!==1e-4)throw Error('Changed match gates');
 for(const r of matches.records){
  const m=r.match,x=m?.coordinatesM;if(x?.length!==63||!x.every(Number.isFinite)||[...x.slice(0,9),...x.slice(54,63)].some(v=>v!==0))throw Error('Invalid prescribed fixed-end coordinates');
  for(const v of [r.modelReference?.value,m.targetN,m.forceN,m.sigma0Pa,m.minimumJ,m.meanFibreStretch])if(!(Number.isFinite(v)&&v>0))throw Error('Invalid positive force/material/match metric');
  near(m.targetN,r.modelReference.value,0,'force target');near(m.activation,1,0,'full activation');finite(m.relativeError,'stored match error');finite(m.maximumFreeGeneralizedGradientN,'stored match residual');
 }
}
export function validateContinuation(run,hashSource){
 coarseCoverage(run,{complete:false});
 const sources=run.sourceHashes;if(!sources||!['web/anatomical-material.mjs','web/anatomical-arm.mjs','web/anatomical-contact.mjs'].every(p=>typeof sources[p]==='string'))throw Error('Missing continuation execution sources');
 for(const [p,h] of Object.entries(sources))if(!/^[a-f0-9]{64}$/.test(h)||hashSource(p)!==h)throw Error('Stale continuation execution source '+p);
 const n=run.held.state.coordinatesM.length,j=n-1;heldDomain(run.held.state,n,j,run.held.state.qRad);let old=run.held.state;
 for(const [i,state] of run.snapshots.entries()){stateLineage(state,old,run.attempts[i],run.parameters,n,j);finite(run.attempts[i].receipt?.maximumFreeModalGradientN,'continuation residual');if(run.attempts[i].receipt.maximumFreeModalGradientN>run.parameters.stationarityToleranceN)throw Error('Unaccepted continuation residual');old=state;}
}
