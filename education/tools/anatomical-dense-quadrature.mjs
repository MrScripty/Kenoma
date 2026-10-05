/** Higher body integration for an isolated accuracy experiment. The original
 * viewer, contact law, displacement space and Newton solver are unchanged.
 */
import {prepareCompressionBody} from './anatomical-compression-quadrature.mjs';
import {attachmentMap} from '../web/anatomical-transfer.mjs';
import {JOINT_SCALE_M} from '../web/anatomical-apparatus.mjs';

export function denseModalBody(body,depth=2){
 const prepared=prepareCompressionBody(body.source,body.nodeModes,depth),points=[];
 for(const [element,e] of prepared.elements.entries())for(const p of e.points){
  const groups=new Map();
  for(let i=0;i<10;i++)for(const mode of body.nodeModes[e.nodes[i]]){
   if(!groups.has(mode.base))groups.set(mode.base,[0,0,0]);
   const v=groups.get(mode.base);for(let d=0;d<3;d++)v[d]+=mode.value*p.gradient[i][d];
  }
  const F0=Float64Array.from({length:9},(_,k)=>e.nodes.reduce((s,node,i)=>s+body.source.nodes_m[node][Math.floor(k/3)]*p.gradient[i][k%3],0));
  points.push({element,weightM3:p.weightM3,fibre:p.fibre,F0,groups:[...groups].filter(([,v])=>Math.hypot(...v)>1e-11).map(([base,gradient])=>({base,gradient}))});
 }
 return {...body,points,quadrature:`diagnostic-subdivision-${prepared.pointsPerElement}`,pointsPerElement:prepared.pointsPerElement};
}

export function incrementalGradient(arm,configuration,state,old,h){
 const p=arm.parameters,q=state.qRad,com=attachmentMap(arm.comM,arm.model.frame,q),grip=attachmentMap(arm.gripM,arm.model.frame,q),stop=q<p.minimumAngleRad?q-p.minimumAngleRad:q>p.maximumAngleRad?q-p.maximumAngleRad:0,I=arm.baseInertiaKgM2+state.massKg*arm.gripRadiusSquaredM2,gradient=configuration.gradient.slice();
 gradient[arm.model.jointIndex]+=(p.gMPerS2*(p.segmentMassKg*com.B[2]+state.massKg*grip.B[2])+p.stopStiffnessNmPerRad*stop+I/h**2*(q-old.qRad-h*old.omegaRadPerS)+p.jointDampingNmS/h*(q-old.qRad))/JOINT_SCALE_M;
 return gradient;
}
