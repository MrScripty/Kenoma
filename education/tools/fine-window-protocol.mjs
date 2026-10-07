/** Frozen fine-window geometry/arithmetic. No specimen evaluator is imported. */
import assert from 'node:assert/strict';
import {PATCH} from './fixed-field-integration-protocol.mjs';
import {shells} from './element247-shell-protocol.mjs';
import {ALL_TERMS,vectors,energyZeros,emptyAssembly,scatter,componentSumCheck} from './fixed-field-integration-assembly.mjs';
import {compareUnits} from './selective-fixed-patch-protocol.mjs';
export {PATCH,ALL_TERMS,compareUnits};
export const STATES=['control45','terminal46'],QUIET=[195,196,198,199,202,237,240,243,244],SECONDARY=[197,200,203,206,246,248],FOCUS=[...SECONDARY,247];
export const CORNERS={197:3,200:3,203:2,206:1,246:0,247:0,248:0};
export const BUDGET=Object.freeze({plannedMaterialCalls:19716000,maximumMaterialCalls:19716000,maximumWallSeconds:7200,nodeHeapMiB:1024,maximumRssBytes:2147483648,maximumOutputBytes:536870912,invocations:1});
export const FORCE_GATE_N=1e-5,WORK_GATE_J=5.492029235357012e-7,RECON={forceN:1e-8,energyJ:1e-9},STATIONARITY_GATE_N=1e-4;
export const RESULTS=['PASS_BOUNDED_FINE_WINDOW_FIXED_PATCH_AGREEMENT','UNRESOLVED_FIXED_PATCH_INTEGRATION'];
export const PHASES=['P4','P8','I0','I1','R4','H4','C4'];
export const CANDIDATES=['S0','S1','S2','I0','I1','AR','AH','AC'];
export const COMPARISONS=[{a:'S0',b:'S1',required:true},{a:'S1',b:'S2',required:true},{a:'I0',b:'I1',required:true},{a:'S2',b:'I1',required:true},{a:'S1',b:'AR',required:true},{a:'S1',b:'AH',required:true},{a:'S1',b:'AC',required:true},{a:'S0',b:'I0',required:false},{a:'S1',b:'I1',required:false}];
export const QUIET_PAIRS=[['D4','D5'],['U4','U5'],['D5','U5']];
export function recipe(element,id){
 assert.ok(FOCUS.includes(element));assert.ok(PHASES.includes(id));assert.ok(!['P4','R4'].includes(id)||SECONDARY.includes(element));
 const corner=CORNERS[element],faceOrder=[0,1,2,3].filter(i=>i!==corner);if(id==='C4')faceOrder.push(faceOrder.shift());
 const independent=['I0','I1'].includes(id),depth=id==='H4'?22:20,angularParts=id==='P8'?8:4,radialParts=['R4','I1'].includes(id)?2:1,faceParts=id==='I1'?8:4;
 const points=independent?(3*20*radialParts+1)*faceParts**2*125:(depth+1)*125*radialParts*angularParts**2;
 return {element,id,kind:independent?'graded-affine-tetra':'tensor-shell',corner,faceOrder,depth,angularParts,radialParts,faceParts,order:5,points};
}
export const SCHEDULE=PHASES.flatMap(id=>(['P4','R4'].includes(id)?SECONDARY:FOCUS).map(e=>recipe(e,id)));
export const normalizedKey=r=>`${r.id}-c${r.corner}`;
export const regionKey=(r,s)=>`${r.element}-${r.id}-${s}`;
export const isOuter20=s=>s.id!=='core'&&Number(s.id.slice(1))<=20;
export function regionPointCount(r,s){return r.kind==='graded-affine-tetra'?(s.id==='core'?1:3*r.radialParts)*r.faceParts**2*125:125*r.radialParts*r.angularParts**2;}
export function newRegion(r,s){return !(r.id==='H4'&&isOuter20(s))&&!(r.id==='C4'&&r.element===247&&isOuter20(s));}
export function newNormalized(r,s){return !(r.id==='H4'&&isOuter20(s))&&!(r.id==='C4'&&r.corner===0&&isOuter20(s))&&!(['P4','R4'].includes(r.id)&&r.corner===0);}
export const NORMALIZED_RECIPES=[...new Map(SCHEDULE.map(r=>[normalizedKey(r),r])).values()];
export function normalizedOrigin(r,s){
 if(r.id==='H4'&&isOuter20(s))return {kind:r.corner===0?'historical':'new',name:`${r.corner===0?'F44':'P4'}-c${r.corner}-${s.id}-points.f64le`};
 if(r.id==='C4'&&r.corner===0&&isOuter20(s))return {kind:'historical',name:`X44-c0-${s.id}-points.f64le`};
 if(['P4','R4'].includes(r.id)&&r.corner===0)return {kind:'historical',name:`${r.id==='P4'?'F44':'R44'}-c0-${s.id}-points.f64le`};
 return {kind:'new',name:`${normalizedKey(r)}-${s.id}-points.f64le`};
}
export function weightOrigin(r,s){
 if(r.id==='H4'&&isOuter20(s))return {kind:r.element===247?'historical':'new',name:`${r.element}-${r.element===247?'F44':'P4'}-${s.id}-weights.f64le`};
 if(r.id==='C4'&&r.element===247&&isOuter20(s))return {kind:'historical',name:`247-X44-${s.id}-weights.f64le`};
 return {kind:'new',name:`${regionKey(r,s.id)}-weights.f64le`};
}
export function reusedOrigin(r,state,s){
 if(r.id==='H4'&&isOuter20(s))return {kind:r.element===247?'historical':'same-invocation',name:`${state}-${r.element}-${r.element===247?'F44':'P4'}-${s.id}-region.json`,stage:`${state}-${r.element}-${r.element===247?'F44':'P4'}-stage.json`,points:regionPointCount(r,s),historicalExit:r.element===247?0:null};
 if(r.id==='C4'&&r.element===247&&isOuter20(s))return {kind:'historical',name:`${state}-247-X44-${s.id}-region.json`,stage:`${state}-247-X44-stage.json`,points:regionPointCount(r,s),historicalExit:0};
 return null;
}
export function validateLocal(row,e,expectedCount=null){
 assert.equal(row.element,e);assert.ok(Number.isInteger(row.pointCount)&&row.pointCount>0&&row.pointCount<=968000);if(expectedCount!==null)assert.equal(row.pointCount,expectedCount);
 assert.ok(Number.isFinite(row.minimumSampleJ)&&row.minimumSampleJ>1e-6);
 for(const t of ALL_TERMS){assert.ok(Number.isFinite(row.energiesJ[t]));assert.ok(row.localGradientsN[t].length===10&&row.localGradientsN[t].every(v=>v.length===3&&v.every(Number.isFinite)));}
}
export function regionRecord(local,r,state,s,identity,origin){
 validateLocal(local,r.element,regionPointCount(r,s));for(const [k,v] of Object.entries({shell:s.id,id:s.id,comparisonShell:s.hi<=2**-20?'core':s.id,lo:s.lo,hi:s.hi}))if(local[k]!==undefined)assert.equal(local[k],v,'Conflicting region identity');
 return {element:r.element,pointCount:local.pointCount,minimumSampleJ:local.minimumSampleJ,localGradientsN:local.localGradientsN,energiesJ:local.energiesJ,id:s.id,shell:s.id,comparisonShell:s.hi<=2**-20?'core':s.id,lo:s.lo,hi:s.hi,state,recipeId:r.id,evaluationIdentity:identity,origin};
}
export function constructStage(source,r,state,rows,rowSources){
 const regions=shells(r.depth);assert.deepEqual(rows.map(x=>x.shell),regions.map(x=>x.id));assert.equal(rowSources.length,rows.length);
 const total={element:r.element,pointCount:r.points,minimumSampleJ:Infinity,localGradientsN:vectors(10),energiesJ:energyZeros()},bins=shells(20).map(s=>({element:r.element,shell:s.id,originalShells:[],localGradientsN:vectors(10),energiesJ:energyZeros()})),direct=emptyAssembly(585);let count=0;
 for(const [i,row] of rows.entries()){
  validateLocal(row,r.element,regionPointCount(r,regions[i]));assert.equal(row.shell,regions[i].id);assert.equal(row.comparisonShell,regions[i].hi<=2**-20?'core':regions[i].id);count+=row.pointCount;
  const bin=bins.find(b=>b.shell===row.comparisonShell);bin.originalShells.push(row.shell);total.minimumSampleJ=Math.min(total.minimumSampleJ,row.minimumSampleJ);scatter(source,row,direct);
  for(const t of ALL_TERMS)for(const out of [total,bin]){out.energiesJ[t]+=row.energiesJ[t];for(let n=0;n<10;n++)for(let d=0;d<3;d++)out.localGradientsN[t][n][d]+=row.localGradientsN[t][n][d];}
 }
 assert.equal(count,r.points);const assembly=emptyAssembly(585);scatter(source,total,assembly);let force=0,energy=0;for(const t of ALL_TERMS){energy=Math.max(energy,Math.abs(direct.energiesJ[t]-assembly.energiesJ[t]));for(let n=0;n<585;n++)for(let d=0;d<3;d++)force=Math.max(force,Math.abs(direct.nodal[t][n][d]-assembly.nodal[t][n][d]));}assert.ok(force<=RECON.forceN&&energy<=RECON.energyJ);
 return {...total,recipe:r,state,comparisonShells:bins,rowSources,logicalRegions:regions.length,newCallbackPoints:regions.filter(s=>newRegion(r,s)).reduce((a,s)=>a+regionPointCount(r,s),0),reusedPoints:regions.filter(s=>!newRegion(r,s)).reduce((a,s)=>a+regionPointCount(r,s),0),reconstruction:{maximumForceDifferenceN:force,maximumEnergyDifferenceJ:energy,component:componentSumCheck(direct),all585Nodes:true}};
}
export function candidateRule(q,e){
 assert.ok(CANDIDATES.includes(q)&&PATCH.includes(e));if(QUIET.includes(e))return q==='I0'?'U4':q==='I1'?'U5':'D5';
 if(q==='S0')return 'A55';if(q==='S1')return e===247?'F44':'P4';if(q==='S2')return 'P8';if(['I0','I1'].includes(q))return q;
 if(q==='AR')return e===247?'R44':'R4';return q==='AH'?'H4':'C4';
}
export function allocation(a,b){const independent=a==='I0'&&b==='I1';return {quiet:{forceN:independent?8.5e-6:2e-6,workJ:(independent?.85:.2)*WORK_GATE_J},focus:{forceN:independent?1.5e-6:8e-6,workJ:(independent?.15:.8)*WORK_GATE_J}};}
export function applyAllocation(comparison,source,units,direction,a,b){
 const budgets=allocation(a,b),groups={};for(const [name,es] of [['quiet',QUIET],['focus',FOCUS]]){const subset=units.filter(u=>es.includes(u.a.element));const c=compareUnits(source,subset,direction,subset.length);for(const t of ALL_TERMS){const x=c.terms[t],limit=budgets[name];x.allocatedPass=x.aggregateInfinityN<=limit.forceN&&x.unitTriangleInfinityN<=limit.forceN&&x.aggregateDirectionalDifferenceJ<=limit.workJ&&x.unitTriangleDirectionalDifferenceJ<=limit.workJ;}groups[name]={budget:budgets[name],metrics:Object.fromEntries(ALL_TERMS.map(t=>{const x=c.terms[t];return [t,{signedN:x.aggregateInfinityN,triangleN:x.unitTriangleInfinityN,signedWorkJ:x.aggregateDirectionalDifferenceJ,triangleWorkJ:x.unitTriangleDirectionalDifferenceJ,pass:x.allocatedPass}];})),pass:ALL_TERMS.every(t=>c.terms[t].allocatedPass)};}
 comparison.allocations=groups;comparison.globalPass=comparison.pass;comparison.pass=comparison.globalPass&&Object.values(groups).every(x=>x.pass);return comparison;
}
