/** Fresh source/orientation and independent saved-vector arithmetic checks.
 * Deliberately does not rerun an optimizer or interpret execution as equilibrium.
 */
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {prepareModalBody,modalPositions} from '../web/anatomical-modal.mjs';
import {exactElementOrientation} from './anatomical-bernstein-orientation.mjs';
import {MUSCLE_FIXTURE} from '../web/anatomical-material.mjs';
const root=fileURLToPath(new URL('../',import.meta.url)),directory=root+'review/isolated-calibration-resolution-20261006/';
const read=p=>JSON.parse(fs.readFileSync(root+p));
const result=read('review/isolated-calibration-resolution-20261006/results.json'),manifest=read('research/isolated-calibration-resolution-20261006-inputs.json');
const geometry=read('data/anatomical-arm-v1/generated/arm-reference.json'),fits=read('data/anatomical-arm-v1/audit/modal-fixed-end-results.json');
const hash=p=>createHash('sha256').update(fs.readFileSync(root+p)).digest('hex');
const max=x=>Math.max(0,...x.map(Math.abs)),dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),near=(a,b,t)=>assert.ok(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=t,`${a} vs ${b}, tolerance ${t}`);
function validate(record){
 assert.equal(record.qualifiedSourceCommit,'401c306e1564be5dc82427193c159d1452f81787');
 assert.equal(record.baseCommit,manifest.base_commit);assert.equal(record.baseTree,manifest.base_tree);
 assert.equal(record.unchangedStationarityToleranceN,.0001);
 for(const flag of ['stateAdvanced','forceRematch','constitutiveChange','displacementSolve'])assert.equal(record[flag],false);
 for(const [p,h] of Object.entries(record.sourceHashes)){
  assert.equal(hash(p),h,'Current source differs: '+p);
  const committed=execFileSync('git',['show',record.qualifiedSourceCommit+':education/'+p],{cwd:root,maxBuffer:32*1024*1024});
  assert.equal(createHash('sha256').update(committed).digest('hex'),h,'Qualified source differs: '+p);
 }
 for(const [p,h] of Object.entries(manifest.inputs))assert.equal(record.sourceHashes[p],h);
 assert.equal(record.rows.length,3);
 for(const [index,fit] of fits.records.entries()){
  const row=record.rows[index],source=geometry.muscles.find(m=>m.element_id===fit.elementId),body=prepareModalBody(source);
  assert.equal(row.elementId,fit.elementId);assert.equal(row.activation,1);assert.equal(row.material.sigma0,fit.match.sigma0Pa);assert.equal(row.originalFitForceN,fit.match.forceN);
  assert.deepEqual(row.material,{...MUSCLE_FIXTURE,sigma0:fit.match.sigma0Pa});
  assert.equal(row.orientation.elements,252);assert.equal(row.orientation.certifiedElements,252);
  const held=new Set([...source.distal_nodes,...source.proximal_nodes]),free=source.nodes_m.map((_,n)=>n).filter(n=>!held.has(n));
  const columns=Array.from({length:45},()=>new Float64Array(free.length*3));
  for(const [i,n] of free.entries())for(const m of body.nodeModes[n])if(m.base>=9&&m.base<54)for(let d=0;d<3;d++)columns[m.base+d-9][3*i+d]+=m.value;
  assert.equal(row.rules.length,3);
  for(const [i,rule] of row.rules.entries()){
   assert.equal(rule.pointsPerElement,manifest.quadrature_points_per_element[i]);
   const r=rule.resolution;assert.equal(r.rank,45);assert.equal(r.freeComponents,1485);assert.equal(r.heldNodes,90);assert.deepEqual(r.freeNodes,free);
   assert.equal(r.retained.length,r.freeComponents);assert.equal(r.omitted.length,r.freeComponents);
   const g=r.retained.map((v,k)=>v+r.omitted[k]);
   near(dot(g,g),r.totalL2N**2,1e-8);near(dot(r.retained,r.retained),r.retainedL2N**2,1e-8);near(dot(r.omitted,r.omitted),r.omittedL2N**2,1e-8);
   near(dot(r.retained,r.omitted),0,1e-8);
   near(dot(r.omitted,r.omitted)/dot(g,g),r.omittedSquaredNormFraction,1e-12);
   near(max(g),r.maximumFreeNodalComponentN,1e-10);near(g[3*free.indexOf(r.largest.node)+r.largest.axis],r.largest.gradientN,1e-10);
   const reduced=columns.map(c=>dot(c,g));near(max(reduced),rule.legacyFreeResidualN,1e-8);
   for(const c of columns)near(dot(c,r.omitted),0,1e-9);
   assert.equal(r.passesUnchangedFullNodalGate,r.maximumFreeNodalComponentN<=.0001);
   assert.equal(rule.legacyPassesUnchangedGate,rule.legacyFreeResidualN<=.0001);
   assert.equal(r.passesUnchangedFullNodalGate,false);assert.equal(rule.legacyPassesUnchangedGate,i===0);
   if(i){const p=row.rules[i-1].resolution,previous=p.retained.map((v,k)=>v+p.omitted[k]),difference=g.map((v,k)=>v-previous[k]);near(Math.sqrt(dot(difference,difference)),rule.comparisonWithPrevious.freeGradientChangeL2N,1e-10);near(max(difference),rule.comparisonWithPrevious.maximumFreeGradientChangeN,1e-10);}
  }
 }
 assert.equal(record.distinctHistoricalCoupledContext.timeS,.1);
 assert.equal(record.distinctHistoricalCoupledContext.frozenResidual2048N,.017385155329473496);
}
validate(result);
const orientationHashes={};
for(const fit of fits.records){
 const source=geometry.muscles.find(m=>m.element_id===fit.elementId),body=prepareModalBody(source),positions=modalPositions(body,Float64Array.from(fit.match.coordinatesM));
 const name=fit.elementId+'-orientation.json',stored=JSON.parse(fs.readFileSync(directory+name));
 assert.equal(stored.elementId,fit.elementId);assert.equal(stored.certificates.length,source.elements_ten_node.length);
 for(const [element,ids] of source.elements_ten_node.entries()){
  const actual=exactElementOrientation(ids.map(n=>source.nodes_m[n]),ids.map(n=>positions[n]));
  assert.deepEqual(stored.certificates[element],{element,...actual});assert.equal(actual.orientationCertified,true);
 }
 orientationHashes[name]=hash('review/isolated-calibration-resolution-20261006/'+name);
}
const damageChecks=[];
for(const [name,damage] of [
 ['false equilibrium pass',x=>{x.rows[0].rules[0].resolution.passesUnchangedFullNodalGate=true;}],
 ['changed physical gate',x=>{x.unchangedStationarityToleranceN=.1;}],
 ['altered omitted force',x=>{x.rows[1].rules[1].resolution.omitted[0]+=.5;}],
 ['wrong qualified source',x=>{x.qualifiedSourceCommit=manifest.base_commit;}]
]){const copy=structuredClone(result);damage(copy);assert.throws(()=>validate(copy));damageChecks.push({damage:name,rejected:true});}
const receipt={result:'PASS_SOURCE_ORIENTATION_VECTOR_RECHECK_AND_DAMAGE_CONTROLS',qualifiedDiagnosticSource:result.qualifiedSourceCommit,verificationSourceSha256:hash('tools/verify-isolated-calibration-diagnostic.mjs'),resultsSha256:hash('review/isolated-calibration-resolution-20261006/results.json'),orientationHashes,checkedSourceFiles:Object.keys(result.sourceHashes).length,checkedOrientationElements:756,checkedFrozenRules:9,fullNodalGatesPassed:0,fullNodalGatesFailed:9,reducedGatesPassed:3,reducedGatesFailed:6,damageChecks,scope:'Fresh byte/qualified-commit checks and exact stored-orientation replay; independent arithmetic on saved free vectors/modal columns. No new optimizer, equilibrium solve or physiological claim.'};
fs.writeFileSync(directory+'verification.json',JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify(receipt,null,2));
