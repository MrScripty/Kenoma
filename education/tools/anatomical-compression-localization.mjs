/** Local kinematics and exact constitutive stress split at the stored dense
 * compression comparison. Diagnostic only; no altered potential or solve. */
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {prepareAnatomicalArm} from '../web/anatomical-arm.mjs';
import {modalPositions} from '../web/anatomical-modal.mjs';
import {quadraticShape} from '../web/anatomical-element.mjs';
import {muscleMaterial,activeCurve} from '../web/anatomical-material.mjs';
import {prepareCompressionBody,compressionQuadrature} from './anatomical-compression-quadrature.mjs';

export function meanStressSplit(F,fibre,a,p){
 const r=muscleMaterial(F,fibre,a,p),e=Math.max(r.lambda-1,0),passiveDerivative=p.kf/p.b*Math.expm1(p.b*e);
 const volumePa=p.bulk*Math.log(r.J)/r.J,activePa=a*p.sigma0*activeCurve(r.lambda,p.activeWidth).value*r.lambda/(3*r.J),passiveFibrePa=passiveDerivative*r.lambda/(3*r.J),totalPa=(r.cauchy[0]+r.cauchy[4]+r.cauchy[8])/3;
 return {J:r.J,fibreStretch:r.lambda,volumePa,activePa,passiveFibrePa,matrixPa:totalPa-volumePa-activePa-passiveFibrePa,totalPa};
}
const root=fileURLToPath(new URL('../',import.meta.url));
export function localizeCompression(body,positions,a,material,depth=2){
 const rule=compressionQuadrature(depth),prepared=prepareCompressionBody(body.source,body.nodeModes,depth),bins=Array.from({length:6},()=>({referenceVolumeM3:0,below09M3:0,minimumJ:Infinity,volumeWeightedJ:0})),worst=[],source=body.source;
 let maxStressSplitErrorPa=0;
 function query(e,p,L,element,kind,pointIndex){
  const F=Array.from({length:9},(_,k)=>e.nodes.reduce((s,node,i)=>s+positions[node][Math.floor(k/3)]*p.gradient[i][k%3],0)),split=meanStressSplit(F,p.fibre,a,material),N=quadraticShape(L).N,X=[0,1,2].map(d=>e.nodes.reduce((s,node,i)=>s+N[i]*source.nodes_m[node][d],0)),currentM=[0,1,2].map(d=>e.nodes.reduce((s,node,i)=>s+N[i]*positions[node][d],0)),z=X.reduce((s,v,d)=>s+(v-source.basis.origin[d])*source.basis.axis[d],0),fraction=(z-source.belly_interval_m[0])/(source.belly_interval_m[1]-source.belly_interval_m[0]);
  maxStressSplitErrorPa=Math.max(maxStressSplitErrorPa,Math.abs(split.matrixPa));
  if(p.weightM3){const bin=bins[Math.max(0,Math.min(5,Math.floor(fraction*6)))];bin.referenceVolumeM3+=p.weightM3;bin.volumeWeightedJ+=p.weightM3*split.J;bin.minimumJ=Math.min(bin.minimumJ,split.J);if(split.J<.9)bin.below09M3+=p.weightM3;}
  worst.push({element,kind,pointIndex,barycentric:L,referenceM:X,currentM,longitudinalFraction: fraction,F,referenceFibre:p.fibre,...split});worst.sort((a,b)=>a.J-b.J);if(worst.length>12)worst.length=12;
 }
 for(const [element,e] of prepared.elements.entries()){
  e.points.forEach((p,i)=>query(e,p,rule[i].L,element,'quadrature',i));
  e.corners.forEach((p,i)=>query(e,p,[0,1,2,3].map(j=>i===j?1:0),element,'corner',i));
 }
 return {elementId:source.element_id,material,activation:a,maxStressSplitErrorPa,worst,bins:bins.map((b,i)=>({bin:i,longitudinalInterval:[i/6,(i+1)/6],referenceVolumeFraction:b.referenceVolumeM3/prepared.referenceVolumeM3,referenceVolumeFractionBelow09:b.below09M3/prepared.referenceVolumeM3,minimumJ:b.minimumJ,meanJ:b.volumeWeightedJ/b.referenceVolumeM3}))};
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 const base=root+'data/anatomical-arm-v1/',read=p=>JSON.parse(fs.readFileSync(base+p)),hash=p=>createHash('sha256').update(fs.readFileSync(root+p)).digest('hex'),run=read('audit/anatomical-dense-step.json'),state=run.candidate;
 for(const [p,h] of Object.entries(run.sourceHashes))if(hash(p)!==h)throw Error('Changed dense comparison '+p);
 const arm=prepareAnatomicalArm(read('generated/arm-reference.json'),read('config/attachments-apparatus.json'),read('audit/modal-fixed-end-results.json'),{parameters:run.parameters,contactParameters:run.contactParameters,routingRecipe:read('config/apparatus-routing.json')}),heads=[];
 for(const b of arm.model.bodies){const positions=modalPositions(b.modal,Float64Array.from(state.coordinatesM.slice(b.offset,b.offset+63))),a=['FJ1486','FJ1512','FJ1478'].includes(b.id)?state.activation:0;heads.push(localizeCompression(b.modal,positions,a,b.material));console.log('LOCALIZED',b.id,heads.at(-1).worst[0].J,heads.at(-1).worst[0].longitudinalFraction);}
 const files=[...Object.keys(run.sourceHashes),'tools/anatomical-compression-localization.mjs','data/anatomical-arm-v1/audit/anatomical-dense-step.json'];
 const receipt={schema:1,result:'COMPLETED_LOCAL_CONSTITUTIVE_DIAGNOSTIC',sourceHashes:Object.fromEntries(files.map(p=>[p,hash(p)])),stateTimeS:state.timeS,heads,identities:{volumeMeanCauchyStress:'K log(J) / J',activeMeanCauchyStress:'a sigma0 f(lambda) lambda / (3 J)',matrixMeanCauchyStress:'0',passiveFibreMeanCauchyStress:'(kf/b) expm1(b max(lambda-1,0)) lambda / (3 J)'},limits:['Stress split is an exact identity of the existing law, not a measurement of intramuscular pressure or an assertion of local hydrostatic equilibrium.','The active law uses full lambda=|F f0|; its positive mean Cauchy stress competes with the negative bulk mean stress at J<1. No potential is changed.','Worst corner/quadrature points and longitudinal bins are finite samples. Authored fitted stresses, fibres, geometry and 63 modes per head remain unvalidated.','This state is the separate same-old-32-point-state dense comparison, not a dense trajectory.']};
 fs.writeFileSync(base+'audit/anatomical-compression-localization.json',JSON.stringify(receipt,null,2)+'\n');
}
