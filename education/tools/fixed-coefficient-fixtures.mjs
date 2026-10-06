/** Research-only fixed-coefficient geometry/support controls. SI throughout. */
import {EDGE_PAIRS} from '../web/anatomical-element.mjs';
import {prepareModalBody, modalPositions, evaluateModalBody} from '../web/anatomical-modal.mjs';
import {muscleMaterial, determinant, inverseTranspose, tendonSegment} from '../web/anatomical-material.mjs';
import {prepareIntramuscularAponeuroses, evaluateIntramuscularAponeuroses} from '../web/anatomical-aponeurosis.mjs';
import {evaluatePoint} from '../web/anatomical-apparatus.mjs';
import {denseModalBody} from './anatomical-dense-quadrature.mjs';
import {prepareCompressionBody} from './anatomical-compression-quadrature.mjs';

export const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
const sub=(a,b)=>a.map((v,i)=>v-b[i]);
export const maximum=a=>a.reduce((s,v)=>Math.max(s,Math.abs(v)),0);
const tensor=(positions,gradient)=>Array.from({length:9},(_,k)=>positions.reduce((s,X,i)=>s+X[Math.floor(k/3)]*gradient[i][k%3],0));
const nodalZero=source=>source.nodes_m.map(()=>[0,0,0]);
export function axialSource(original){const s=structuredClone(original);s.reference_fibres=s.elements_ten_node.map(()=>s.basis.axis.slice());return s;}

/** Extrude the actual central polygon with identical connectivity, then scale
 * transverse area to exact source volume. This is a prism, not measured PCSA. */
export function matchedPrism(original){
 const s=axialSource(original),[start,end]=s.belly_interval_m,L=end-start,{origin,axis,u,v}=s.basis;
 const mid=s.nodes_m.slice(48,64),center=mid.reduce((a,X)=>a.map((x,d)=>x+X[d]/16),[0,0,0]);
 const polygon=mid.map(X=>{const r=sub(X,center);return [dot(r,u),dot(r,v)];});
 const area=Math.abs(polygon.reduce((a,p,i)=>{const q=polygon[(i+1)%16];return a+p[0]*q[1]-q[0]*p[1];},0))/2;
 if(!(area>0&&L>0))throw new RangeError('Prism reference area/length');
 const scale=Math.sqrt(original.reference_volume_m3/(area*L));
 for(let r=0;r<7;r++)for(let j=0;j<16;j++)s.nodes_m[16*r+j]=origin.map((o,d)=>o+axis[d]*(start+L*r/6)+scale*(u[d]*polygon[j][0]+v[d]*polygon[j][1]));
 const parents=new Map();for(const t of s.elements_ten_node)EDGE_PAIRS.forEach(([a,b],k)=>{
  const pair=[t[a],t[b]].sort((a,b)=>a-b),old=parents.get(t[k+4]);
  if(old&&old.join()!==pair.join())throw new RangeError('Inconsistent P2 edge topology');parents.set(t[k+4],pair);
 });
 for(const [node,[a,b]] of parents)s.nodes_m[node]=s.nodes_m[a].map((x,d)=>(x+s.nodes_m[b][d])/2);
 s.centerline_m=Array.from({length:7},(_,r)=>origin.map((o,d)=>o+axis[d]*(start+L*r/6)));
 const volume=s.elements_ten_node.reduce((sum,t)=>{const [A,B,C,D]=t.slice(0,4).map(i=>s.nodes_m[i]);const F=[...sub(B,A),...sub(C,A),...sub(D,A)];const det=determinant(F);if(!(det>1e-15))throw new RangeError('Prism changes reference orientation');return sum+det/6;},0);
 if(Math.abs(volume/original.reference_volume_m3-1)>1e-11)throw new RangeError('Prism volume matching');
 s.reference_volume_m3=volume;
 s.researchControl={method:'Straight extrusion of source central 16-vertex polygon, transverse scaling to source V0/L0, identical P2 connectivity; constant axial fibers.',sourceElement:original.element_id,centralPolygonAreaM2:area,transverseScale:scale,matchedLengthM:L,matchedVolumeM3:original.reference_volume_m3,prismCrossSectionM2:volume/L};
 return s;
}

/** Freeze only the selected head's original routed support targets/guides.
 * The shared sheet/joint/other heads are held at their reference positions.
 * This is an explicit attachment apparatus ablation, not the coupled arm. */
export function frozenHeadSupports(model,id){
 const body=model.bodies.find(b=>b.id===id);if(!body)throw new RangeError('Missing head');
 const frozen=p=>({referenceM:evaluatePoint(p,model.referenceCoordinates,model).position});
 const local=p=>({referenceM:p.referenceM.slice(),nodes:p.sourceNodes.slice(),weights:p.sourceWeights.slice()});
 return {branches:model.branches.filter(b=>b.a.kind==='body'&&b.a.sourceElement===id).map(b=>({point:local(b.a),path:b.path.slice(1).map(frozen),L0M:b.L0M,A0M2:b.A0M2,group:b.group,evidence:b.evidence})),interfaces:model.interfaces.filter(b=>b.a.sourceElement===id).map(b=>({point:local(b.a),targetM:b.targetM.slice(),fibre:b.fibre.slice(),axialStiffnessNPerM:b.axialStiffnessNPerM,transverseStiffnessNPerM:b.transverseStiffnessNPerM,group:b.group,gapM:b.gapM})),limits:'Original head fan and weak-matrix laws; external targets, route guides, common sheet and joint frozen at reference. No bone contact.'};
}
const pointPosition=(p,source,positions)=>p.referenceM.map((v,d)=>v+p.nodes.reduce((s,n,i)=>s+p.weights[i]*(positions[n][d]-source.nodes_m[n][d]),0));
const pointColumns=(p,body)=>{
 const values=new Map();p.nodes.forEach((n,i)=>body.nodeModes[n].forEach(m=>values.set(m.base,(values.get(m.base)||0)+p.weights[i]*m.value)));
 return [...values].flatMap(([base,value])=>[0,1,2].map(d=>({index:base+d,axis:d,value})));
};
export function supportAssembly(fixture,positions,{hessian=false}={}){
 const {source,body,supports}=fixture,g=nodalZero(source),H=hessian?new Float64Array(63*63):null;let energy=0;
 function add(p,force,C){p.nodes.forEach((n,i)=>force.forEach((f,d)=>g[n][d]+=p.weights[i]*f));if(H){const columns=pointColumns(p,body);for(const a of columns)for(const b of columns)H[a.index*63+b.index]+=a.value*b.value*C[3*a.axis+b.axis];}}
 for(const b of supports.branches){
  const A=pointPosition(b.point,source,positions),delta=sub(A,b.path[0].referenceM),first=Math.hypot(...delta);if(!(first>1e-8))throw new RangeError('Collapsed support route');
  const length=b.path.slice(1).reduce((s,p,i)=>s+Math.hypot(...sub(p.referenceM,b.path[i].referenceM)),first),r=tendonSegment(length,b.L0M,b.A0M2),n=delta.map(x=>x/first);
  const C=Array.from({length:9},(_,k)=>r.stiffnessNPerM*n[Math.floor(k/3)]*n[k%3]+r.forceN/first*((Math.floor(k/3)===k%3?1:0)-n[Math.floor(k/3)]*n[k%3]));
  energy+=r.storedEnergyJ;add(b.point,n.map(v=>v*r.forceN),C);
 }
 for(const b of supports.interfaces){const d=sub(pointPosition(b.point,source,positions),b.targetM),k0=b.transverseStiffnessNPerM,k1=b.axialStiffnessNPerM-k0,C=Array.from({length:9},(_,i)=>k0*(Math.floor(i/3)===i%3?1:0)+k1*b.fibre[Math.floor(i/3)]*b.fibre[i%3]),force=[0,1,2].map(i=>dot(C.slice(3*i,3*i+3),d));energy+=.5*dot(d,force);add(b.point,force,C);}
 return {energy,nodalGradientN:g,hessian:H,gradient:projectNodal(body,g)};
}
export function sheetNodalAssembly(fixture,positions){
 const {source,sheets}=fixture,components={sheetAxial:nodalZero(source),sheetMatrix:nodalZero(source)},energies={sheetAxial:0,sheetMatrix:0};
 const weights=p=>Array.from({length:16},(_,k)=>({node:16*p.sourceRing+k,value:.3/16+(16*p.sourceRing+k===p.sourcePerimeterNode?.7:0)}));
 const point=p=>p.referenceM.map((v,d)=>v+weights(p).reduce((s,m)=>s+m.value*(positions[m.node][d]-source.nodes_m[m.node][d]),0));
 for(const [key,pairs] of [['sheetAxial',sheets.branches],['sheetMatrix',sheets.matrix]])for(const p of pairs){const delta=sub(point(p.a),point(p.b)),L=Math.hypot(...delta);if(!(L>1e-8))throw new RangeError('Collapsed sheet branch');const r=key==='sheetMatrix'?{forceN:p.stiffnessNPerM*(L-p.L0M),storedEnergyJ:.5*p.stiffnessNPerM*(L-p.L0M)**2}:tendonSegment(L,p.L0M,p.A0M2);energies[key]+=r.storedEnergyJ;for(const [end,sign] of [[p.a,1],[p.b,-1]])for(const m of weights(end))for(let d=0;d<3;d++)components[key][m.node][d]+=sign*m.value*r.forceN*delta[d]/L;}
 return {components,energies};
}
export function projectNodal(body,nodal){const g=new Float64Array(63);body.nodeModes.forEach((modes,n)=>modes.forEach(m=>{for(let d=0;d<3;d++)g[m.base+d]+=m.value*nodal[n][d];}));return g;}
export function prepareControl(source,{kind='ideal',sheets=false,supports={branches:[],interfaces:[]},depth=2}={}){
 const modal=prepareModalBody(source),body=denseModalBody(modal,depth),empty={strips:[],branches:[],matrix:[]};
 return {source,body,prepared:prepareCompressionBody(source,body.nodeModes,depth),kind,sheets:sheets?prepareIntramuscularAponeuroses(body):empty,supports:kind==='attachment'?supports:{branches:[],interfaces:[]},free:kind==='ideal'?Array.from({length:45},(_,i)=>i+9):Array.from({length:63},(_,i)=>i),heldNodes:kind==='ideal'?new Set([...source.distal_nodes,...source.proximal_nodes]):new Set()};
}
export function evaluateControl(fixture,x,a,material,{hessian=true}={}){
 const r=evaluateModalBody(fixture.body,x,a,{material,hessian}),s=evaluateIntramuscularAponeuroses(fixture.body,fixture.sheets,x,{hessian}),p=supportAssembly(fixture,modalPositions(fixture.body,x),{hessian});
 for(let i=0;i<63;i++){r.gradient[i]+=s.gradient[i]+p.gradient[i];if(hessian)for(let j=0;j<63;j++)r.hessian[i*63+j]+=s.hessian[i*63+j]+p.hessian[i*63+j];}
 return {...r,energy:r.energy+s.energy+p.energy,sheetEnergyJ:s.energy,supportEnergyJ:p.energy};
}

function weightedStats(values){
 const sorted=values.toSorted((a,b)=>a.value-b.value),W=sorted.reduce((s,r)=>s+r.weight,0),quantile=q=>{let w=0;for(const r of sorted){w+=r.weight;if(w>=q*W)return r.value;}return sorted.at(-1).value;};
 return {minimum:sorted[0].value,maximum:sorted.at(-1).value,mean:sorted.reduce((s,r)=>s+r.value*r.weight,0)/W,q01:quantile(.01),q05:quantile(.05),median:quantile(.5),q95:quantile(.95),q99:quantile(.99)};
}
/** Independent full-P2 body assembly, split by exact existing stress terms. */
export function diagnoseControl(fixture,x,a,material){
 const {source,body,prepared}=fixture,positions=modalPositions(body,x),components=Object.fromEntries(['matrix','volume','passiveFiber','active'].map(k=>[k,nodalZero(source)])),fields={J:[],stretch:[],forceLength:[],activeCauchyAlongFiberPa:[],bulkMeanCauchyPa:[]},energies={matrix:0,volume:0,passiveFiber:0,activePotential:0};let minCornerJ=Infinity;
 for(const e of prepared.elements){const X=e.nodes.map(n=>positions[n]);for(const p of e.points){const F=tensor(X,p.gradient),r=muscleMaterial(F,p.fibre,a,material),invT=inverseTranspose(F,r.J),vol=invT.map(v=>material.bulk*Math.log(r.J)*v),kf=material.kf/material.b*Math.expm1(material.b*Math.max(r.lambda-1,0)),passive=Array.from({length:9},(_,i)=>kf*r.direction[Math.floor(i/3)]*p.fibre[i%3]),parts={matrix:r.Ppassive.map((v,i)=>v-vol[i]-passive[i]),volume:vol,passiveFiber:passive,active:r.Pactive},w=p.weightM3,fL=((r.lambda-1)/material.activeWidth)**2<1?(1-((r.lambda-1)/material.activeWidth)**2)**2:0;
  for(const [k,P] of Object.entries(parts))for(let i=0;i<10;i++)for(let d=0;d<3;d++)components[k][e.nodes[i]][d]+=w*dot(P.slice(3*d,3*d+3),p.gradient[i]);
  for(const k in energies)energies[k]+=w*r.energy[k];
  for(const [k,value] of Object.entries({J:r.J,stretch:r.lambda,forceLength:fL,activeCauchyAlongFiberPa:a*material.sigma0*fL*r.lambda/r.J,bulkMeanCauchyPa:material.bulk*Math.log(r.J)/r.J}))fields[k].push({value,weight:w});
 }for(const p of e.corners)minCornerJ=Math.min(minCornerJ,determinant(tensor(X,p.gradient)));}
 const sheet=sheetNodalAssembly(fixture,positions),support=supportAssembly(fixture,positions);Object.assign(components,sheet.components,{support:support.nodalGradientN});
 const nodal=source.nodes_m.map((_,n)=>[0,1,2].map(d=>Object.values(components).reduce((s,g)=>s+g[n][d],0))),projected=projectNodal(body,nodal),distal=new Set(source.distal_nodes),[start,end]=source.belly_interval_m,L=end-start,axis=source.basis.axis;
 const virtual=source.nodes_m.map(X=>axis.map(v=>v*(1-(dot(sub(X,source.basis.origin),axis)-start)/L))),reactions={};
 for(const [key,g] of Object.entries(components)){const direct=-dot(g.reduce((s,v,n)=>distal.has(n)?s.map((x,d)=>x+v[d]):s,[0,0,0]),axis),work=-g.reduce((s,v,n)=>s+dot(v,virtual[n]),0);reactions[key]={directDistalN:direct,axialVirtualForceN:work,virtualMinusDirectN:work-direct};}
 const W=prepared.referenceVolumeM3,fraction=(key,predicate)=>fields[key].reduce((s,r)=>s+(predicate(r.value)?r.weight:0),0)/W;
 return {positionsM:positions,projectedGradientN:Array.from(projected),independentReducedResidualN:maximum(fixture.free.map(i=>projected[i])),maximumFreeNodalComponentN:maximum(nodal.flatMap((v,n)=>fixture.heldNodes.has(n)?[]:v)),maximumHeldDisplacementM:Math.max(0,...positions.flatMap((v,n)=>fixture.heldNodes.has(n)?[Math.hypot(...sub(v,source.nodes_m[n]))]:[])),minimumCornerJ:minCornerJ,globalVolumeRatio:fields.J.reduce((s,r)=>s+r.value*r.weight,0)/W,referenceVolumeM3:W,fields:Object.fromEntries(Object.entries(fields).map(([k,v])=>[k,weightedStats(v)])),fractions:{JBelow09:fraction('J',v=>v<.9),stretchBelowActiveWindow:fraction('stretch',v=>v<=.5),stretchAboveActiveWindow:fraction('stretch',v=>v>=1.5)},reactions,energies:{...energies,...sheet.energies,support:support.energy},nodalGradientN:nodal,limits:['Full nodal forces are a separate diagnostic: passing projected force balance does not pass full nodal stationarity.','Virtual displacement is dimensionless phi=(1-s)*reference axis, so derivative with respect to a metre of virtual displacement is a force in N. It equals the axis on the distal cap and zero on the proximal cap.','Direct body/sheet cap forces, external support forces, and whole-body virtual work are reported separately; virtual-minus-direct contains unbalanced free-node work at a restricted equilibrium.','Active Cauchy scalar is a*sigma0*fL*lambda/J along the current local fiber; it is not the peak first-Piola parameter.']};
}
