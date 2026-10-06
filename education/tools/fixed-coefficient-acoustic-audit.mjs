/** Frozen full-P2 tangent scan. No optimizer or physical history advancement. */
import fs from 'node:fs';import {createHash} from 'node:crypto';import {fileURLToPath} from 'node:url';
import {prepareControl} from './fixed-coefficient-fixtures.mjs';import {quadraticRingFixture} from './fixed-coefficient-quadratic-space.mjs';
import {modalPositions,materialTensor} from '../web/anatomical-modal.mjs';import {determinant,MUSCLE_FIXTURE} from '../web/anatomical-material.mjs';
import {acousticMatrix,minimumEigenpair,referenceDirections,witnessChecks} from './fixed-coefficient-acoustic.mjs';
const root=fileURLToPath(new URL('../',import.meta.url)),base=root+'data/anatomical-arm-v1/',out=base+'audit/fixed-coefficient-acoustic-audit.json',hash=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex'),sources={};
if(fs.existsSync(out))throw Error('Preserve existing tangent audit');
const read=p=>{sources['data/anatomical-arm-v1/'+p]=hash(base+p);return JSON.parse(fs.readFileSync(base+p));},prism=read('audit/fixed-coefficient-prism.json'),taper=read('audit/fixed-coefficient-taper.json'),old=read('audit/fixed-coefficient-taper-quadratic.json'),current=read('audit/fixed-coefficient-taper-quadratic-current-preconditioner.json');
for(const [name,r] of [['prism',prism],['taper',taper],['taper-quadratic',old],['taper-quadratic-current-preconditioner',current]]){const replay=read(`audit/fixed-coefficient-${name}-recheck.json`);if(!replay.result.startsWith('PASS_')||replay.executionReceiptSHA256!==hash(base+`audit/fixed-coefficient-${name}.json`))throw Error('Fresh replay required '+name);for(const [p,h] of Object.entries(r.sourceHashes)){if(hash(root+p)!==h)throw Error('Changed input '+p);sources[p]=h;}}
const geo=read('generated/arm-reference.json'),fits=read('audit/modal-fixed-end-results.json'),source=geo.muscles.find(m=>m.element_id==='FJ1512'),fit=fits.records.find(r=>r.elementId==='FJ1512'),cases=[
 ['prism-full',prepareControl(prism.fixture.source),prism.accepted.at(-1).coordinatesM,1,prism.material,true],
 ['taper-affine-full',prepareControl(taper.fixture.source),taper.accepted.at(-1).coordinatesM,1,taper.material,true],
 ['original-fit-frozen',prepareControl(source,{sheets:true}),fit.match.coordinatesM,1,{...MUSCLE_FIXTURE,sigma0:fit.match.sigma0Pa},false],
 ['quadratic-original-rejected',quadraticRingFixture(taper.fixture.source),old.attempt.candidateCoordinatesM,.01,old.material,false],
 ['quadratic-current-reduced-accepted',quadraticRingFixture(taper.fixture.source),current.attempt.candidateCoordinatesM,.01,current.material,true]
];
const rows=[];
for(const [name,fixture,x,activation,material,reducedAccepted] of cases){
 const positions=modalPositions(fixture.body,Float64Array.from(x)),directions=referenceDirections(fixture.source.basis),W=fixture.prepared.referenceVolumeM3;let worst=null,negativeVolume=0,expandedVolume=0,minimumJ=Infinity,maximumJ=-Infinity,points=0;
 for(const [element,e] of fixture.prepared.elements.entries()){const X=e.nodes.map(n=>positions[n]);for(const [point,p] of e.points.entries()){
  const F=Array.from({length:9},(_,k)=>X.reduce((s,v,i)=>s+v[Math.floor(k/3)]*p.gradient[i][k%3],0)),J=determinant(F),C=materialTensor(F,p.fibre,activation,material);minimumJ=Math.min(minimumJ,J);maximumJ=Math.max(maximumJ,J);if(J>Math.E)expandedVolume+=p.weightM3;let negative=false;
  for(const [direction,m] of directions.entries()){const Q=acousticMatrix(C,m),r=minimumEigenpair(Q);if(r.valuePa< -1e-6)negative=true;if(!worst||r.valuePa<worst.minimumEigenvaluePa)worst={element,point,direction,F,fibre:p.fibre,m,Q,polarization:r.polarization,minimumEigenvaluePa:r.valuePa,relativeEigenResidual:r.relativeEigenResidual,referenceWeightM3:p.weightM3};}
  if(negative)negativeVolume+=p.weightM3;points++;
 }}
 const checks=witnessChecks(worst.F,worst.fibre,activation,material,worst.m,worst.polarization,worst.Q),row={name,activation,reducedAccepted,material,pointCount:points,directionCount:directions.length,directions,referenceVolumeFractionWithNegativeWitness:negativeVolume/W,referenceVolumeFractionJAboveE:expandedVolume/W,minimumIntegrationJ:minimumJ,maximumIntegrationJ:maximumJ,worst:{...worst,...checks}};rows.push(row);console.log('CASE',JSON.stringify({name,minimumEigenvaluePa:worst.minimumEigenvaluePa,negativeFraction:negativeVolume/W,parts:checks.rayleighPartsPa,derivatives:checks.stressFiniteDifferences}));
}
for(const p of ['tools/fixed-coefficient-acoustic.mjs','tools/fixed-coefficient-acoustic-audit.mjs','research/fixed-coefficient-acoustic-protocol.md','web/anatomical-material.mjs','web/anatomical-modal.mjs'])sources[p]=hash(root+p);
const result={schema:1,result:'PASS_SOURCE_BOUND_FROZEN_RANK_ONE_DIAGNOSIS',sourceHashes:sources,rows,limits:['Finite thirteen-direction scan cannot prove positivity in all directions. A negative verified rank-one direction witnesses local curvature of the fixed-activation solve potential.','A frozen failed state stays rejected; reduced acceptance does not qualify full nodal equilibrium, global constrained stability or tissue credibility.','No optimizer, coefficient change, state advancement or loaded trajectory rerun.']};fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n');console.log('RESULT',result.result);
