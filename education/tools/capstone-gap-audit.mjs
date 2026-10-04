/** Reproduce current-model gaps; this does not implement or validate a new arm. */
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync,writeFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {SPATIAL,SPATIAL_MESH,solveSpatial,spatialInitial,spatialStep} from '../web/spatial.mjs';
import {seriesResults} from '../web/series.mjs';
const snapshot={q:Math.PI/6,w:0,a:.6,time:0,work:0,dissipation:0,halted:false};
const row=(s,p)=>{const h=seriesResults(s,{...p,contact:'off'});return {timeS:s.time,qRad:s.q,a:s.a,u:p.excitation,massKg:p.load,tensionN:h.tension,fiberM:h.fiber,tendonM:h.tendon,momentArmM:h.momentArm,muscleTorqueNm:h.muscleTorque,gravityTorqueNm:h.gravityTorque,inertiaKgM2:h.inertia,angularAccelerationRadS2:h.acceleration};};
const loadRows=[0,1,5,10].map(load=>row(snapshot,{...SPATIAL,load}));
assert(loadRows.every(r=>r.tensionN===loadRows[0].tensionN));
assert(loadRows.at(-1).angularAccelerationRadS2<loadRows[1].angularAccelerationRadS2);
const activationRows=[0,.2,.6,1].map(a=>row({...snapshot,a},SPATIAL));
assert(activationRows.at(-1).tensionN>activationRows[1].tensionN);
assert(activationRows.at(-1).fiberM<activationRows[1].fiberM);
const p={...SPATIAL,sweeps:160,skin:'off'},light=solveSpatial(snapshot.q,snapshot.a,{...p,load:0}),heavy=solveSpatial(snapshot.q,snapshot.a,{...p,load:10});
assert.deepEqual(light.x,heavy.x);assert.deepEqual(light.energy,heavy.energy);
const inactive=solveSpatial(snapshot.q,0,p);assert(light.fiberArcLengthM<inactive.fiberArcLengthM);
const ablated={...p,activeShape:'off'},lineOwned=row(snapshot,ablated);assert.equal(lineOwned.muscleTorqueNm,loadRows[2].muscleTorqueNm);
const trajectories=[];
for(const excitation of [.2,.6])for(const load of [1,5,10]){
 const params={...p,excitation,load};let s=spatialInitial(params);const initial=row(s,params);
 for(let i=0;i<40&&!s.halted;i++)s=spatialStep(s,params);
 const beforeRelease=row(s,params),released={...params,excitation:0},a0=s.a;
 const next=spatialStep(s,released);assert(next.halted||next.a<a0);
 trajectories.push({initial,beforeRelease,afterReleaseStep:row(next,released),halted:s.halted});
}
const primarySliders=[{key:'excitation',label:'Muscle effort',unit:'1',min:0,max:1,meaning:'Requested normalized excitation; activation and tension are separate outputs.'},{key:'load',label:'Dumbbell mass',unit:'kg',min:0,max:10,meaning:'Existing educational range only; use body-frame load point, gravity and inertia, never an independent deformation amplitude.'}];
assert.equal(primarySliders.length,2);assert.deepEqual(primarySliders.map(s=>s.key),['excitation','load']);
const sources={};for(const path of ['web/spatial.mjs','web/series.mjs','web/elbow.mjs','web/advanced.mjs','tools/build.py','data/elbow-v1/sources/arm26.osim','data/elbow-v1/data/bodyparts3d_right_arm_m.json'])sources[path]=createHash('sha256').update(readFileSync(new URL('../'+path,import.meta.url))).digest('hex');
const mesh=SPATIAL_MESH,bounds=[0,1,2].map(d=>[Math.min(...mesh.rest.slice(0,mesh.coreCount).map(X=>X[d])),Math.max(...mesh.rest.slice(0,mesh.coreCount).map(X=>X[d]))]);
const result={schema:1,status:'passed',scope:'Executable diagnosis of existing equations and a proposed two-input contract; not verification of an implemented anatomical revision or biological validation.',gitRevision:execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),runtime:process.version,inputSha256:sources,currentGeometry:{coreVertices:mesh.coreCount,tetrahedra:mesh.tets.length,coreBoundsM:bounds,fixedCoreNodes:mesh.fixed.slice(0,mesh.coreCount).filter(Boolean).length},samePoseLoadRows:loadRows,activationRows,spatialLoadIndependence:{positionsBitIdentical:true,energiesBitIdentical:true,loadsKg:[0,10],qRad:snapshot.q,a:snapshot.a,skin:'off',iterations:160},activationShapeResponse:{inactiveFiberArcM:inactive.fiberArcLengthM,activeFiberArcM:light.fiberArcLengthM,inactiveMeanJ:inactive.meanJ,activeMeanJ:light.meanJ},spatialActuatorAblationLeavesHingeTorqueUnchanged:true,trajectories,proposedPrimarySliders:primarySliders,proposedUiImplemented:false,proposedCoupledSolverImplemented:false};
const output=process.argv[2];if(output)writeFileSync(output,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
