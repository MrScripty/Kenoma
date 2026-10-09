/** Original verifier equations with explicit leaf/ledger coverage. Dependencies
 * injected at execution; this module alone imports no physical operators. */
import {json,detached} from './core.mjs';
export function near(a,b,t,label){if(!Number.isFinite(a)||!Number.isFinite(b)||Math.abs(a-b)>t)throw Error('Replay mismatch: '+label);}
export function equal(a,b,label){if(json(a)!==json(b))throw Error('Replay lineage: '+label);}
function gate(c,surface,routing,p,residual){
 if(p.stationarityToleranceN!==1e-4||!Number.isFinite(residual)||residual>1e-4||surface.transverseCrossingPairs!==0||routing.accepted!==true||!c.headResults.length||c.headResults.some(h=>!(h.minJ>1e-6)))throw Error('Original force/material/finite geometry gate');
 for(const k of ['maximumSampledBonePenetrationM','maximumSampledSoftPenetrationM','maximumSampledTendonPenetrationM'])if(!Number.isFinite(c.contact[k])||c.contact[k]>0)throw Error('Original sampled penetration gate '+k);
}
export function verifyHeld(api,arm,state){
 api.heldDomain(state,arm.model.ndof,arm.model.jointIndex,arm.model.frame.atlas_bind_angle_rad);
 const c=api.anatomicalConfiguration(arm,Float64Array.from(state.coordinatesM),0,{hessian:false});
 const residual=Math.max(...c.gradient.filter((_,i)=>i!==arm.model.jointIndex).map(Math.abs));
 const surface=api.finitePoseAudit(arm.model,c.positions,state.qRad),routing=api.finiteRoutingAudit(arm.model,Float64Array.from(state.coordinatesM));gate(c,surface,routing,arm.parameters,residual);
 return detached({maximumFreeModalGradientN:residual,surfaceAudit:surface,routingAudit:routing,heads:c.headResults,contact:c.contact});
}
export function verifyLeaves(api,arm,initial,leaves,totalDuration){
 const p=arm.parameters,j=arm.model.jointIndex,rechecks=[];let old=detached(initial);
 function stored(s,a,rule){api.restoreContactRecipe(arm.contact,rule||arm.initialContactRule);return api.anatomicalConfiguration(arm,Float64Array.from(s.coordinatesM),a,{hessian:false});}
 function rigid(s){const com=api.attachmentMap(arm.comM,arm.model.frame,s.qRad),grip=api.attachmentMap(arm.gripM,arm.model.frame,s.qRad),d=s.qRad<p.minimumAngleRad?s.qRad-p.minimumAngleRad:s.qRad>p.maximumAngleRad?s.qRad-p.maximumAngleRad:0;return {energy:p.gMPerS2*(p.segmentMassKg*com.position[2]+s.massKg*grip.position[2])+.5*p.stopStiffnessNmPerRad*d*d,gradient:p.gMPerS2*(p.segmentMassKg*com.B[2]+s.massKg*grip.B[2])+p.stopStiffnessNmPerRad*d};}
 for(const leaf of leaves){
  const s=leaf.state,r=leaf.receipt,h=leaf.hS;equal(leaf.oldState,old,'old state snapshot');
  api.stateLineage(s,old,{hS:h,effort:leaf.effort},p,arm.model.ndof,j);
  if(s.step!==old.step+1||s.effort!==leaf.effort||leaf.effort!==.04)throw Error('Step/effort lineage');
  equal(s.massEvents,old.massEvents,'mass events');equal(s.history.slice(0,-1),old.history,'history prefix');equal(s.history.at(-1),r,'history tail');
  near(s.mechanicalWorkJ,old.mechanicalWorkJ+r.activeMechanicalWorkJ,1e-9,'cumulative mechanical work');
  if(!s.contactRule||s.contactRule.schema!==1)throw Error('Missing final contact recipe');
  const prior=stored(old,old.activation,old.contactRule),oldAtRule=stored(old,old.activation,s.contactRule),oldAtActivation=stored(old,s.activation,s.contactRule),c=stored(s,s.activation,s.contactRule),G=rigid(s),G0=rigid(old),I=arm.baseInertiaKgM2+s.massKg*arm.gripRadiusSquaredM2;
  c.gradient[j]+=(G.gradient+I/h**2*(s.qRad-old.qRad-h*old.omegaRadPerS)+p.jointDampingNmS/h*(s.qRad-old.qRad))/api.JOINT_SCALE_M;
  const residual=Math.max(...c.gradient.map(Math.abs)),surface=api.finitePoseAudit(arm.model,c.positions,s.qRad),routing=api.finiteRoutingAudit(arm.model,Float64Array.from(s.coordinatesM));gate(c,surface,routing,p,residual);
  near(residual,r.maximumFreeModalGradientN,1e-9,'force residual');
  const quadrature=oldAtRule.physicalPotentialJ-prior.physicalPotentialJ,activeWork=oldAtActivation.energies.activePotentialJ-c.energies.activePotentialJ,passive=z=>z.physicalPotentialJ-z.energies.activePotentialJ,oldE=passive(oldAtActivation)+G0.energy+.5*I*old.omegaRadPerS**2,newE=passive(c)+G.energy+.5*I*s.omegaRadPerS**2,damping=p.jointDampingNmS*h*s.omegaRadPerS**2,kineticDefect=.5*I*(s.omegaRadPerS-old.omegaRadPerS)**2,workDefect=newE-oldE-activeWork+damping+kineticDefect,impulse=h*api.JOINT_SCALE_M*c.gradient[j];
  for(const [a,b,label] of [[quadrature,r.referenceQuadratureUpdateJ,'quadrature event'],[activeWork,r.activeMechanicalWorkJ,'active work'],[oldE,r.oldMechanicalJ,'old mechanical energy'],[newE,r.newMechanicalJ,'new mechanical energy'],[workDefect,r.nonlinearWorkDefectJ,'nonlinear defect'],[impulse,r.impulseResidualNmS,'impulse']])near(a,b,1e-9,label);
  equal(api.contactRecipe(arm.contact),s.contactRule,'restored final contact rule');
  rechecks.push(detached({residualN:residual,surfaceAudit:surface,routingAudit:routing,minimumJ:Math.min(...c.headResults.map(h=>h.minJ)),referenceQuadratureUpdateJ:quadrature,activeMechanicalWorkJ:activeWork,nonlinearWorkDefectJ:workDefect,impulseResidualNmS:impulse}));old=detached(s);
 }
 near(old.timeS,initial.timeS+totalDuration,1e-14,'total duration');return rechecks;
}
