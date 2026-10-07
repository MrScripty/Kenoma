import test from 'node:test';
import assert from 'node:assert/strict';
import {midpointNodes} from '../web/anatomical-element.mjs';
import {certifyRoundedPath,checkedMaterialEvaluation,geometryBacktracking} from '../tools/isolated-geometry-backtracking.mjs';
const nodes=midpointNodes([[0,0,0],[1e-4,0,0],[0,1e-4,0],[0,0,1e-4]]),source={nodes_m:nodes,distal_nodes:[0],proximal_nodes:[],elements_ten_node:[[0,1,2,3,4,5,6,7,8,9]]},positions=q=>nodes.map(X=>[X[0]*(1-2*q[0]),X[1],X[2]]),nodeStep=q=>nodes.map(X=>[-2*X[0]*q[0],0,0]);
const defaults={source,currentCoordinates:[0],currentEnergyJ:0,gradientN:[-1],rawNewtonCoordinates:[1],positions,nodeStep};
test('fresh rounded paths reject inverted and zero candidates before the synthetic callback, then accept admissible fraction',()=>{
 const events=[],evaluated=[];const result=geometryBacktracking({...defaults,onEvent:e=>events.push(e),evaluate:q=>{evaluated.push(q[0]);return {energyJ:-q[0],positions:positions(q)};}});
 assert.equal(result.alpha,.25);assert.deepEqual(evaluated,[.25]);assert.deepEqual(events.filter(e=>e.kind==='TRIAL').map(e=>[e.alpha,e.disposition,e.materialEvaluated]),[[1,'REJECTED',false],[.5,'REJECTED',false],[.25,'ACCEPTED',true]]);
 const raw=events[0];assert.deepEqual(raw.rawNewtonCoordinatesM,[1]);assert.equal(raw.scaling,1);assert.equal(raw.rawMaximumNodalIncrementM,.0002);assert.ok(events[3].roundedNodalIncrementM.every((v,n)=>v.every((x,d)=>x===positions([.25])[n][d]-nodes[n][d])));
});
test('initial physical bound scales raw direction and logs both raw and rounded increments',()=>{
 const events=[];const r=geometryBacktracking({...defaults,rawNewtonCoordinates:[4],onEvent:e=>events.push(e),evaluate:q=>({energyJ:-q[0]})});assert.equal(r.alpha,.25);assert.equal(events[0].scaling,.25);assert.equal(events[0].rawMaximumNodalIncrementM,.0008);assert.equal(events[0].scaledMaximumNodalIncrementM,.0002);
});
test('positive endpoint orientation cannot substitute for a whole-path certificate',()=>{
 const endpoint=nodes.map(X=>[-2*X[0],-.5*X[1],X[2]]);assert.ok(certifyRoundedPath(source,nodes,nodes).certified);assert.ok(certifyRoundedPath(source,endpoint,endpoint).certified);assert.equal(certifyRoundedPath(source,nodes,endpoint).certified,false);
});
test('same1e-6 domain guard refuses positive orientation below its threshold',()=>{
 const low=nodes.map(X=>[X[0]*5e-7,X[1],X[2]]);assert.equal(certifyRoundedPath(source,nodes,low).certified,false);const good=nodes.map(X=>[X[0]*2e-6,X[1],X[2]]);assert.ok(certifyRoundedPath(source,nodes,good).certified);
});
test('caps, nonfinite geometry and uncertified evaluation are fatal before callbacks',()=>{
 const damaged=nodes.map(X=>X.slice());damaged[0][0]=1e-30;assert.throws(()=>certifyRoundedPath(source,nodes,damaged),/cap trace/);damaged[0][0]=NaN;assert.throws(()=>certifyRoundedPath(source,nodes,damaged),/Nonfinite/);
 let calls=0;assert.throws(()=>checkedMaterialEvaluation({source,start:nodes,coordinates:[1],positions,evaluate:()=>{calls++;return {energyJ:0};}}),/Uncertified/);assert.equal(calls,0);
});
test('unexpected failure after certification stops without fraction reduction',()=>{
 const events=[];let calls=0;assert.throws(()=>geometryBacktracking({...defaults,onEvent:e=>events.push(e),evaluate:()=>{calls++;throw Error('injected material domain failure');}}),/injected/);assert.equal(calls,1);assert.equal(events.filter(e=>e.kind==='TRIAL').length,3);assert.equal(events.at(-1).disposition,'FAILURE');assert.equal(events.at(-1).reason,'UNEXPECTED_FAILURE_AFTER_CERTIFICATION');
});
test('unchanged Armijo has exactly21 bounded fractions and refuses exhaustion',()=>{
 const safe=q=>nodes.map(X=>[X[0]*(1+.1*q[0]),X[1],X[2]]),small=q=>nodes.map(X=>[.1*X[0]*q[0],0,0]),events=[];let calls=0;
 assert.throws(()=>geometryBacktracking({...defaults,positions:safe,nodeStep:small,onEvent:e=>events.push(e),evaluate:()=>{calls++;return {energyJ:1};}}),/Exhausted21/);const trials=events.filter(e=>e.kind==='TRIAL');assert.equal(calls,21);assert.equal(trials.length,21);assert.equal(trials[0].alpha,1);assert.equal(trials.at(-1).alpha,2**-20);assert.ok(trials.every(e=>e.reason==='SUFFICIENT_DECREASE'&&e.requiredEnergyJ===-1e-4*e.alpha));
});
test('non-descent, no representable change, nonfinite and mismatched certified results stop',()=>{
 let calls=0;assert.throws(()=>geometryBacktracking({...defaults,gradientN:[1],evaluate:()=>{calls++;}}),/non-descent/);assert.equal(calls,0);
 assert.throws(()=>geometryBacktracking({...defaults,positions:()=>nodes,evaluate:()=>{calls++;}}),/representable/);assert.equal(calls,0);
 assert.throws(()=>geometryBacktracking({...defaults,evaluate:()=>({energyJ:NaN})}),/Invalid result/);
 assert.throws(()=>geometryBacktracking({...defaults,evaluate:()=>({energyJ:-1,positions:nodes})}),/Invalid result/);
});
