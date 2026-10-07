/** Structural helpers only. No constitutive evaluator or optimizer. */
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {uniformCells,cellRule,TERMS} from './isolated-collapse-components.mjs';
import {certifyState} from './isolated-geometry-backtracking.mjs';
import {furtherQuadrature} from './anatomical-integration-refinement.mjs';
export {TERMS};
export const PATCH=[195,196,197,198,199,200,202,203,206,237,240,243,244,246,247,248];
export const FORCE_GATE_N=1e-4,INTEGRATION_GATE_N=1e-5;
export const RECIPES=[
 {id:'U3',kind:'symmetric4',depth:3,pointsPerElement:2048,scope:'whole-body'},
 {id:'U4',kind:'symmetric4',depth:4,pointsPerElement:16384,scope:'patch'},
 {id:'U5',kind:'symmetric4',depth:5,pointsPerElement:131072,scope:'patch'},
 {id:'D4',kind:'duffy',depth:3,order:4,pointsPerElement:32768,scope:'patch'},
 {id:'D5',kind:'duffy',depth:3,order:5,pointsPerElement:64000,scope:'patch'}
];
export const COMPARISONS=[['U4','U5'],['D4','D5'],['U5','D5']];
// Binary64 tables on [0,1]. These literals and enumeration order are frozen.
export const GAUSS={
 4:{x:[.06943184420297371,.33000947820757187,.6699905217924281,.9305681557970262],w:[.17392742256872692,.32607257743127305,.32607257743127305,.17392742256872692]},
 5:{x:[.046910077030668,.23076534494715845,.5,.7692346550528415,.953089922969332],w:[.11846344252809454,.23931433524968324,.28444444444444444,.23931433524968324,.11846344252809454]}
};
export const digest=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');
export function* rule(recipe){
 assert.deepEqual(recipe,RECIPES.find(r=>r.id===recipe.id),'Unregistered quadrature recipe');
 // Preserve the original point coordinates/order bit-for-bit, rather than
 // substitute a mathematically equivalent subdivision with rounded differences.
 if(recipe.id==='U3'){yield* furtherQuadrature();return;}
 const cells=uniformCells(recipe.depth);
 if(recipe.kind==='symmetric4'){yield* cellRule(cells);return;}
 const {x,w}=GAUSS[recipe.order];
 for(const cell of cells)for(let i=0;i<x.length;i++)for(let j=0;j<x.length;j++)for(let k=0;k<x.length;k++){
  const r=x[i],s=x[j],t=x[k],B=[(1-r)*(1-s)*(1-t),r,(1-r)*s,(1-r)*(1-s)*t];
  yield {L:[0,1,2,3].map(a=>B.reduce((v,b,n)=>v+b*cell.vertices[n][a],0)),weight:cell.weight*6*w[i]*w[j]*w[k]*(1-r)**2*(1-s)};
 }
}
export function inventory(recipe){
 const h=createHash('sha256');let count=0,weight=0;const first=[0,0,0,0],second=[0,0,0,0];let cross=0,minWeight=Infinity;
 for(const p of rule(recipe)){
  assert.ok(p.weight>0&&Number.isFinite(p.weight)&&p.L.every(v=>v>=0&&Number.isFinite(v)));
  assert.ok(Math.abs(p.L.reduce((a,b)=>a+b,0)-1)<1e-14);
  h.update(JSON.stringify(p)+'\n');count++;weight+=p.weight;minWeight=Math.min(minWeight,p.weight);
  for(let i=0;i<4;i++){first[i]+=p.weight*p.L[i];second[i]+=p.weight*p.L[i]**2;}cross+=p.weight*p.L[0]*p.L[1];
 }
 assert.equal(count,recipe.pointsPerElement);assert.ok(Math.abs(weight-1)<1e-11);
 for(let i=0;i<4;i++){assert.ok(Math.abs(first[i]-.25)<1e-11);assert.ok(Math.abs(second[i]-.1)<1e-11);}assert.ok(Math.abs(cross-.05)<1e-11);
 return {recipe,count,normalizedWeightSum:weight,minimumNormalizedWeight:minWeight,firstMoments:first,diagonalSecondMoments:second,cross01:cross,enumeratedPointsSha256:h.digest('hex'),serialization:'Each {L:[...],weight:number} in deterministic generator order, JSON.stringify plus LF; normalized weights, physical weights computed separately.'};
}
export function schedule(elementCount,states=2){
 assert.equal(elementCount,252);assert.equal(states,2);
 return RECIPES.map(r=>({id:r.id,elements:r.scope==='whole-body'?elementCount:PATCH.length,states,pointsPerElement:r.pointsPerElement,materialCalls:states*(r.scope==='whole-body'?elementCount:PATCH.length)*r.pointsPerElement}));
}
export function assertPatch(source,patch){
 assert.deepEqual(patch,PATCH,'Patch membership/order changed');
 assert.deepEqual(patch,source.elements_ten_node.flatMap((ids,i)=>ids.includes(92)?[i]:[]),'Incomplete node92 incident patch');
}
export function checkedFixedState(source,positions,expectedDigest,callback){
 assert.equal(digest(positions),expectedDigest,'Saved field changed');
 const certificate=certifyState(source,positions);
 const frozen=Object.freeze(positions.map(v=>Object.freeze(v.slice())));
 const result=callback(frozen,certificate);
 assert.equal(digest(positions),expectedDigest,'Saved field changed after callback');
 return result;
}
const finiteVector=(v,n)=>assert.ok(v.length===n&&v.every(a=>Array.isArray(a)&&a.length===3&&a.every(Number.isFinite)),'Nonfinite or malformed nodal vector');
export function replacePatch(source,patch,baseline,oldPatch,newPatch){
 assertPatch(source,patch);const n=source.nodes_m.length,out={},support=new Set(patch.flatMap(e=>source.elements_ten_node[e]));
 for(const t of [...TERMS,'total']){
  finiteVector(baseline[t],n);finiteVector(oldPatch[t],n);finiteVector(newPatch[t],n);
  for(let i=0;i<n;i++)if(!support.has(i))assert.ok(oldPatch[t][i].every(v=>v===0)&&newPatch[t][i].every(v=>v===0),'Patch contribution outside incident support');
  out[t]=baseline[t].map((a,i)=>a.map((v,d)=>v-oldPatch[t][i][d]+newPatch[t][i][d]));
 }
 return out;
}
export function compareVectors(a,b,direction){
 finiteVector(a,direction.length);finiteVector(b,direction.length);finiteVector(direction,direction.length);
 let max=0,workA=0,workB=0,l1=0;
 for(let n=0;n<a.length;n++)for(let d=0;d<3;d++){max=Math.max(max,Math.abs(a[n][d]-b[n][d]));workA+=a[n][d]*direction[n][d];workB+=b[n][d]*direction[n][d];l1+=Math.abs(direction[n][d]);}
 const derivativeGateJ=INTEGRATION_GATE_N*l1,derivativeDifferenceJ=Math.abs(workA-workB);
 return {maximumAllNodalDifferenceN:max,directionalDerivativeAJ:workA,directionalDerivativeBJ:workB,directionalDerivativeDifferenceJ:derivativeDifferenceJ,forceGateN:INTEGRATION_GATE_N,derivativeGateJ,pass:max<=INTEGRATION_GATE_N&&derivativeDifferenceJ<=derivativeGateJ};
}
export class Budget{
 constructor({calls=9000000,wallMs=900000,now=()=>performance.now()}={}){this.maximum=calls;this.used=0;this.now=now;this.deadline=now()+wallMs;}
 reserve(count){assert.ok(Number.isInteger(count)&&count>0,'Invalid material batch');assert.ok(this.now()<this.deadline,'Wall budget exhausted');assert.ok(this.used+count<=this.maximum,'Material-call budget exhausted');this.used+=count;}
}
