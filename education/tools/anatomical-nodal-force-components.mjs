import {recordedInputMatches} from './recorded-inputs.mjs';
/** Decompose the frozen excluded virtual-work directions. No solve or advance. */
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {prepareAnatomicalArm,anatomicalConfiguration} from '../web/anatomical-arm.mjs';
import {restoreContactRecipe} from '../web/anatomical-contact-refinement.mjs';
import {modalPositions} from '../web/anatomical-modal.mjs';
import {muscleMaterial,inverseTranspose} from '../web/anatomical-material.mjs';
import {denseModalBody} from './anatomical-dense-quadrature.mjs';
import {prepareCompressionBody} from './anatomical-compression-quadrature.mjs';
import {excludedNodalDirection,nodalProbeConfiguration} from './anatomical-nodal-probe.mjs';
const root=fileURLToPath(new URL('../',import.meta.url)),base=root+'data/anatomical-arm-v1/',read=p=>JSON.parse(fs.readFileSync(base+p)),hash=p=>createHash('sha256').update(fs.readFileSync(root+p)).digest('hex'),run=read('audit/anatomical-dense-loading-prefix.json'),prior=read('audit/anatomical-nodal-probe.json');
for(const [p,h] of Object.entries(prior.sourceHashes))if(!recordedInputMatches(p,h))throw Error('Changed excluded-direction source '+p);
const state=run.snapshots[3],arm=prepareAnatomicalArm(read('generated/arm-reference.json'),read('config/attachments-apparatus.json'),read('audit/modal-fixed-end-results.json'),{parameters:run.parameters,contactParameters:run.contactParameters,routingRecipe:read('config/apparatus-routing.json')});
for(const b of arm.model.bodies)b.modal=denseModalBody(b.modal);restoreContactRecipe(arm.contact,state.contactRule);
const body=arm.model.bodies.find(b=>b.id==='FJ1512'),x=Float64Array.from(state.coordinatesM),positions=modalPositions(body.modal,x.slice(body.offset,body.offset+63)),prepared=prepareCompressionBody(body.modal.source,body.modal.nodeModes,2),baseline=anatomicalConfiguration(arm,x,state.activation,{hessian:false}),points=[];
for(const e of prepared.elements)for(const p of e.points){
 const F=Array.from({length:9},(_,k)=>e.nodes.reduce((s,n,i)=>s+positions[n][Math.floor(k/3)]*p.gradient[i][k%3],0)),m=body.material,r=muscleMaterial(F,p.fibre,state.activation,m),G=inverseTranspose(F,r.J),iso=r.J**(-2/3),I1=F.reduce((s,v)=>s+v*v,0),matrixP=F.map((v,k)=>m.mu*iso*(v-I1/3*G[k])),volumeP=G.map(v=>m.bulk*Math.log(r.J)*v),passiveFiberP=r.P.map((v,k)=>v-matrixP[k]-volumeP[k]-r.Pactive[k]);
 points.push({nodes:e.nodes,gradient:p.gradient,weightM3:p.weightM3,components:{matrix:matrixP,volume:volumeP,passiveFiber:passiveFiberP,active:r.Pactive}});
}
function energies(c){const routed=c.branches.reduce((s,b)=>s+b.storedEnergyJ,0);return {passiveBody:c.energies.passiveBodyJ,activeBody:c.energies.activePotentialJ,embeddedAxialSheets:c.energies.tendonJ-routed,routedTendons:routed,transverseSheetMatrix:c.energies.aponeurosisMatrixJ,interfaces:c.energies.interfaceJ,contact:c.contact.storedEnergyJ};}
const rows=[];
for(const node of [98,96])for(const axis of [0,1,2]){
 const probe=excludedNodalDirection(body.modal,node,axis),analyticBodyN={matrix:0,volume:0,passiveFiber:0,active:0};
 for(const p of points){const deltaF=Array.from({length:9},(_,k)=>p.nodes.reduce((s,n,i)=>s+probe.direction[n][Math.floor(k/3)]*p.gradient[i][k%3],0));for(const [key,P] of Object.entries(p.components))analyticBodyN[key]+=p.weightM3*P.reduce((s,v,k)=>s+v*deltaF[k],0);}
 const differences=[];
 for(const hM of [1e-7,5e-8]){
  const plus=nodalProbeConfiguration(arm,body,x,state.activation,probe.direction,hM,prepared),minus=nodalProbeConfiguration(arm,body,x,state.activation,probe.direction,-hM,prepared),a=energies(plus),b=energies(minus),componentsN=Object.fromEntries(Object.keys(a).map(k=>[k,(a[k]-b[k])/(2*hM)])),totalDerivativeN=(plus.energy-minus.energy)/(2*hM),sum=Object.values(componentsN).reduce((s,v)=>s+v,0),passive=analyticBodyN.matrix+analyticBodyN.volume+analyticBodyN.passiveFiber;
  if(Math.abs(sum-totalDerivativeN)>2e-6||Math.abs(passive-componentsN.passiveBody)>2e-6||Math.abs(analyticBodyN.active-componentsN.activeBody)>2e-6)throw Error('Independent virtual-work component agreement');
  differences.push({hM,totalDerivativeN,componentsN,sumDifferenceN:sum-totalDerivativeN,passiveBodyAnalyticDifferenceN:passive-componentsN.passiveBody,activeBodyAnalyticDifferenceN:analyticBodyN.active-componentsN.activeBody});
 }
 const saved=prior.rows.find(r=>r.node===node&&r.axis===axis);if(Math.abs(differences[1].totalDerivativeN-saved.differences[1].energyDerivativeN)>1e-8)throw Error('Changed original probe');
 if(anatomicalConfiguration(arm,x,state.activation,{hessian:false}).energy!==baseline.energy)throw Error('Failed exact restoration');
 rows.push({node,axis,maximumModalDot:probe.maximumModalDot,analyticBodyN,differences});console.log('DIRECTION',JSON.stringify(rows.at(-1)));
}
const files=[...Object.keys(prior.sourceHashes),'data/anatomical-arm-v1/audit/anatomical-nodal-probe.json','tools/anatomical-nodal-force-components.mjs'];
const result={schema:1,result:'PASS_FROZEN_EXCLUDED_VIRTUAL_WORK_DECOMPOSITION',sourceHashes:Object.fromEntries(files.map(p=>[p,hash(p)])),timeS:state.timeS,elementId:body.id,rows,limits:['Directions are the same six unit nodal directions excluded from the original 63-coordinate short head. The accepted dense 0.10 s state and contact recipe are unchanged.','Body components use independently assembled full P2 virtual work. Sheet, interface, tendon and contact derivatives use two central-difference sizes, retaining reference areas and rest lengths.','These component balances diagnose missing stationarity in selected directions; they neither solve nor advance a full nodal state and do not identify a physiological material law.']};
fs.writeFileSync(base+'audit/anatomical-nodal-force-components.json',JSON.stringify(result,null,2)+'\n');console.log('RESULT',result.result);
