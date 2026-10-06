import {ELBOW,activation,elbowInitial,elbowGeometry,activeFiber} from './elbow.mjs';
import {TISSUE,tissueAt} from './tissue.mjs';
export const SERIES=Object.freeze({...ELBOW,tendon:'compliant',tendonK:30000,contact:'on',bulk:TISSUE.bulk});
// Active force in parallel with a tension-only passive fiber, in series with tendon.
export function seriesEquilibrium(path,a,p=SERIES){
 if(![path,a,p.tendonK,p.maxForce,p.optimalFiber,p.width,p.passiveK,p.tendonLength].every(Number.isFinite)||path<=p.tendonLength||a<0||a>1||p.tendonK<=0||p.maxForce<0||p.optimalFiber<=0||p.width<=0||p.passiveK<0||p.tendonLength<0)throw new RangeError('series actuator domain');
 const compliance=p.tendon==='rigid'?0:1/p.tendonK;
 if(!['rigid','compliant'].includes(p.tendon))throw new RangeError('unknown tendon model');
 // H(f)=f+cT[FA(f,a)+FP(f)]-(path-lTs). Its derivative stays positive
 // over the supported controls: |FA'| <= F0 sqrt(2/e)/(width*l0) < kT.
 const slopeBound=p.maxForce*Math.sqrt(2/Math.E)/(p.width*p.optimalFiber);
 if(compliance*slopeBound>=1)throw new RangeError('series equilibrium requires a monotone supported tendon stiffness');
 const totalFiber=path-p.tendonLength;
 const forceAt=f=>activeFiber(f,a,p).force+p.passiveK*Math.max(0,f-p.optimalFiber);
 const H=f=>f+compliance*forceAt(f)-totalFiber;
 let fiber=totalFiber,iterations=0;
 if(compliance>0){
  // No positive-length root: return an explicitly inadmissible boundary state.
  if(H(0)>0)fiber=0;
  else {let lo=0,hi=totalFiber;for(;iterations<64;iterations++){const mid=(lo+hi)/2;if(mid===lo||mid===hi)break;if(H(mid)>0)hi=mid;else lo=mid;}fiber=(lo+hi)/2;}
 }
 const law=activeFiber(fiber,a,p),active=law.force;
 const passive=p.passiveK*Math.max(0,fiber-p.optimalFiber);
 const tension=active+passive,tendon=path-fiber,tautPassive=fiber>p.optimalFiber;
 const denominator=1+compliance*(law.slope+(tautPassive?p.passiveK:0));
 const fiberEnergy=.5*p.passiveK*Math.max(0,fiber-p.optimalFiber)**2,tendonEnergy=.5*compliance*tension*tension;
 return {active,passive,tension,tendon,fiber,compliance,denominator,tautPassive,fiberEnergy,tendonEnergy,forcePerActivation:law.forcePerActivation,activeFiberSlope:law.slope,equilibriumIterations:iterations,
  forceResidual:compliance>0?(tendon-p.tendonLength)/compliance-tension:0,lengthResidual:fiber+tendon-path,admissible:fiber>=0.04&&denominator>0};
}
export function seriesResults(s,p=SERIES){
 const geometry=elbowGeometry(s.q,p),m=seriesEquilibrium(geometry.length,s.a,p);
 const tau=p.excitation>=s.a?p.rise:p.fall,activationRate=(p.excitation-s.a)/tau;
 const pathSpeed=-geometry.momentArm*s.w;
 const fiberSpeed=(pathSpeed-m.compliance*m.forcePerActivation*activationRate)/m.denominator;
 const tendonSpeed=pathSpeed-fiberSpeed;
 const tissue=tissueAt(s.q,{...TISSUE,bulk:p.bulk},p.contact==='on');
 const C=p.g*(p.load*p.length+p.forearmMass*p.com),inertia=p.baseInertia+p.load*p.length**2+p.forearmMass*p.com**2;
 const activeTorque=geometry.momentArm*m.active,passiveTorque=geometry.momentArm*m.passive;
 const muscleTorque=geometry.momentArm*m.tension,gravityTorque=-C*Math.sin(s.q),dampingTorque=-p.damping*s.w;
 const motorTorque=p.mode==='prescribed'?-(muscleTorque+gravityTorque+tissue.torque):0;
 const acceleration=p.mode==='prescribed'?0:(muscleTorque+gravityTorque+dampingTorque+tissue.torque)/inertia;
 const energy=.5*inertia*s.w*s.w-C*Math.cos(s.q)+m.fiberEnergy+m.tendonEnergy+tissue.energy;
 return {...geometry,...m,tissue,pathSpeed,fiberSpeed,tendonSpeed,activationRate,inertia,activeTorque,passiveTorque,muscleTorque,gravityTorque,dampingTorque,motorTorque,acceleration,energy,
  activePower:-m.active*fiberSpeed,dissipationRate:p.damping*s.w*s.w,hingeMusclePower:muscleTorque*s.w,tissuePower:tissue.torque*s.w};
}
export function seriesInitial(p=SERIES){return {...elbowInitial(p),eventSplits:0,substeps:0};}
export function seriesStep(s,p=SERIES,depth=0){
 if(s.halted)return {...s};
 if(!Number.isFinite(p.dt)||p.dt<=0||p.dt>.02||!['forward','prescribed'].includes(p.mode))throw new RangeError('series step domain');
 const h=p.dt,tau=p.excitation>=s.a?p.rise:p.fall,at=t=>activation(s.a,p.excitation,t,tau);
 const y=[s.q,s.w,s.work,s.dissipation],regimes=[];
 const derivative=(v,t)=>{
  // Reject inadmissible trial stages before evaluating continuum geometry.
  if(v[0]<0||v[0]>135*Math.PI/180)return null;
  const r=seriesResults({...s,q:v[0],w:v[1],a:at(t)},p);
  if(!r.admissible)return null;
  regimes.push(`${r.tautPassive}:${r.tissue.normal>0}`);
  return [p.mode==='prescribed'?0:v[1],r.acceleration,r.activePower,r.dissipationRate];
 };
 const stage=(k,scale)=>y.map((v,i)=>v+scale*k[i]);
 const k1=derivative(y,0);if(!k1)return {...s,halted:true};
 const k2=derivative(stage(k1,h/2),h/2);if(!k2)return {...s,halted:true};
 const k3=derivative(stage(k2,h/2),h/2);if(!k3)return {...s,halted:true};
 const k4=derivative(stage(k3,h),h);if(!k4)return {...s,halted:true};
 // Local event refinement handles piecewise passive/plate transitions. Report its cost.
 if(depth<8 && regimes.some(x=>x!==regimes[0])){
  const half={...p,dt:h/2},first=seriesStep(s,half,depth+1),second=seriesStep(first,half,depth+1);
  if(first.halted||second.halted)return {...s,halted:true};
  return {...second,eventSplits:second.eventSplits+1};
 }
 const v=y.map((x,i)=>x+h*(k1[i]+2*k2[i]+2*k3[i]+k4[i])/6);
 const next={...s,q:v[0],w:v[1],work:v[2],dissipation:v[3],a:at(h),time:s.time+h,substeps:(s.substeps??0)+1};
 if(next.q<0||next.q>135*Math.PI/180||!seriesResults(next,p).admissible)return {...s,halted:true};
 return next;
}
export function seriesTrace(p=SERIES,duration=.6,release=.3){
 let s=seriesInitial(p);const initial=seriesResults(s,p).energy,rows=[];
 for(let n=0;n<=Math.round(duration/p.dt);n++){
  const input={...p,excitation:n*p.dt>=release?0:p.excitation},r=seriesResults(s,input);
  rows.push({...s,...r,balanceResidual:r.energy-initial-s.work+s.dissipation});
  if(s.halted)break;s=seriesStep(s,input);
 }
 return rows;
}
