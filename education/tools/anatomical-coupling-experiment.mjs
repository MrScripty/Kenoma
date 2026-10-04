/** Original matched solver/profile and coupled work experiment; no biology. */
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {blockFixture,solveBlock} from '../web/anatomical-fixture.mjs';
import {coupledFixture,fixtureInitialState,stepCoupledFixture,fixtureMassEvent} from '../web/anatomical-coupled-fixture.mjs';
const root=fileURLToPath(new URL('../',import.meta.url)),sourceHashes={};
for(const path of ['web/anatomical-material.mjs','web/anatomical-element.mjs','web/anatomical-fixture.mjs','web/anatomical-tangent.mjs','web/anatomical-solver.mjs','web/anatomical-newton.mjs','web/anatomical-preconditioner.mjs','web/anatomical-transfer.mjs','web/anatomical-coupled-fixture.mjs','tools/anatomical-coupling-experiment.mjs'])sourceHashes[path]=createHash('sha256').update(await readFile(root+path)).digest('hex');
const profiles=[];
for(const refinement of [1,2])for(const method of ['lbfgs','newton']){
 const fixture=blockFixture({refinement,quadrature:'subdivided32'}),options={activation:.05,loadN:12,solver:{method,preconditioner:method==='newton'?'reference':undefined,maxIterations:method==='newton'?80:6000,historySize:20,tolerance:1e-6}},start=performance.now(),r=solveBlock(fixture,options);
 if(!r.converged)throw Error('Matched profile failed: '+refinement+' '+method+' '+r.reason);
 profiles.push({refinement,method,quadrature:'subdivided32',elements:fixture.elements.length,nodes:fixture.nodes.length,materialChanged:false,normalizedGradientTolerance:1e-6,meanEndLengthM:r.topMeanLengthM,maximumNodalForceN:r.maximumFreeNodalForceN,maximumComponentForceN:r.maximumFreeForceComponentN,iterations:r.acceptedIterations,objectiveEvaluations:r.evaluations,hessianProducts:r.hessianProducts||0,elapsedMS:performance.now()-start});
}
const runs=[];
for(const h of [.04,.02,.01]){
 const f=coupledFixture();let state=fixtureInitialState(f),rows=[],failed=null;
 for(let i=0;i<Math.round(.48/h);i++){
  const excitation=i<Math.round(.28/h)?.25:0,start=performance.now(),r=stepCoupledFixture(f,state,{h,excitation});
  if(!r.accepted){failed={step:i,reason:r.result.reason};break;}
  state=r.state;rows.push({timeS:state.timeS,qRad:state.q,activation:state.activation,excitation,angularVelocityRadS:state.omega,tissueTorqueNm:r.result.tissueTorqueNm,gravityTorqueNm:r.result.gravityTorqueNm,torqueBalanceNm:r.torqueBalanceNm,maximumNodalForceN:r.result.maximumFreeNodalForceN,minJ:r.result.minJ,volumeRatio:r.result.volumeRatio,meanFibreStretch:r.result.meanFibreStretch,iterations:r.result.acceptedIterations,objectiveEvaluations:r.result.evaluations,postSolveObjectiveEvaluations:1,postSolveBodyEvaluations:1,hessianProducts:r.result.hessianProducts,elapsedMS:performance.now()-start,...r.work,positionsM:state.positions});
 }
 if(failed)throw Error('Coupled pulse failed: '+JSON.stringify(failed));
 const changed=fixtureMassEvent(f,state,1),probe=stepCoupledFixture(f,changed,{h,excitation:0});if(!probe.accepted)throw Error('Mass-event follow-on solve failed');
 runs.push({hS:h,quadrature:'four',elements:f.block.elements.length,nodes:f.block.nodes.length,capBranches:f.tendons.length,rows,massEvent:changed.events.at(-1),massEventFollowOnQ:probe.state.q,maxTorqueBalanceNm:Math.max(...rows.map(r=>Math.abs(r.torqueBalanceNm))),maxNodalForceN:Math.max(...rows.map(r=>r.maximumNodalForceN)),sumEndpointWorkDefectJ:rows.reduce((s,r)=>s+r.nonlinearEndpointWorkDefectJ,0),peakQ:Math.max(...rows.map(r=>r.qRad)),finalQ:state.q});
}
const receipt={schema:1,evidenceClass:'authored_coupled_engineering_fixture',sourceHashes,profiles,runs,limits:['Rectangular P2 tissue, synthetic hinge and nine authored cap-to-bone tensile branches. No anatomical apparatus or contact.','The tendon energy generates all tissue hinge torque; no independent scalar muscle actuator.','Tissue is quasistatic, joint inertia implicit, activation time constants authored, force-velocity multiplier fixed to one.','World +Z is downward. The synthetic route moment arm can reverse at large angles; no anatomical interpretation.','Nonlinear endpoint-work defects remain measured, not erased by an exact angular algebra proof.','32-point quadrature and matching residual/material are retained in solver profiling. Dense reference Cholesky is a small-fixture preconditioner, not a seven-muscle scalability claim.','Elapsed times include local CPU measurements, not mobile or browser performance guarantees.']};
await writeFile(root+'data/anatomical-arm-v1/audit/coupling-results.json',JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify({profiles,runs:runs.map(({rows,...r})=>r)},null,2));
