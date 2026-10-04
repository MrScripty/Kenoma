// Original synthetic single-hinge lesson. Values are design choices, not human measurements.
export const ELBOW = Object.freeze({mode:'forward',load:5,excitation:0.6,angle:30,dt:0.005,
  length:0.35,forearmMass:1.5,com:0.15,baseInertia:0.035,origin:0.22,insertion:0.06,
  tendonLength:0.06,optimalFiber:0.20,maxForce:1200,width:0.6,passiveK:1200,
  damping:1.2,rise:0.05,fall:0.15,g:9.81});
const QMAX=135*Math.PI/180;
export function activation(a,u,h,tau) {
  if (![a,u,h,tau].every(Number.isFinite)||a<0||a>1||u<0||u>1||h<0||tau<=0)throw new RangeError('activation domain');
  return u+(a-u)*Math.exp(-h/tau);
}
export function elbowInitial(p=ELBOW){return {q:p.angle*Math.PI/180,w:0,a:0,time:0,work:0,dissipation:0,halted:false};}
export function elbowGeometry(q,p=ELBOW){
  const point=[p.insertion*Math.sin(q),-p.insertion*Math.cos(q)];
  const length=Math.hypot(point[0],point[1]-p.origin);
  const momentArm=p.origin*p.insertion*Math.sin(q)/length;
  return {point,length,momentArm,fiber:length-p.tendonLength};
}
export function elbowResults(s,p=ELBOW){
  const geo=elbowGeometry(s.q,p),stretch=Math.max(0,geo.fiber-p.optimalFiber);
  const active=p.maxForce*s.a*Math.exp(-(((geo.fiber/p.optimalFiber-1)/p.width)**2));
  const passive=p.passiveK*stretch,tension=active+passive;
  const C=p.g*(p.load*p.length+p.forearmMass*p.com);
  const inertia=p.baseInertia+p.load*p.length**2+p.forearmMass*p.com**2;
  const activeTorque=active*geo.momentArm,passiveTorque=passive*geo.momentArm;
  const gravityTorque=-C*Math.sin(s.q),dampingTorque=-p.damping*s.w;
  const motorTorque=p.mode==='prescribed'?-(activeTorque+passiveTorque+gravityTorque):0;
  const acceleration=p.mode==='prescribed'?0:(activeTorque+passiveTorque+gravityTorque+dampingTorque)/inertia;
  const energy=0.5*inertia*s.w**2-C*Math.cos(s.q)+0.5*p.passiveK*stretch**2;
  return {...geo,active,passive,tension,inertia,activeTorque,passiveTorque,gravityTorque,dampingTorque,motorTorque,acceleration,energy,
    fiberSpeed:-geo.momentArm*s.w,activePower:activeTorque*s.w,dissipationRate:p.damping*s.w**2};
}
export function elbowStep(s,p=ELBOW){
  if(s.halted)return {...s};
  if(!Number.isFinite(p.dt)||p.dt<=0||p.dt>0.02||!Number.isFinite(p.load)||p.load<0)throw new RangeError('elbow domain');
  const h=p.dt,tau=p.excitation>=s.a?p.rise:p.fall;
  const at=t=>activation(s.a,p.excitation,t,tau);
  if(p.mode==='prescribed')return {...s,a:at(h),time:s.time+h};
  if(p.mode!=='forward')throw new RangeError('unknown elbow mode');
  // RK4 for q, angular velocity and work/dissipation; exact constant-input activation at every stage.
  const y=[s.q,s.w,s.work,s.dissipation];
  const derivative=(v,t)=>{const r=elbowResults({...s,q:v[0],w:v[1],a:at(t)},p);return [v[1],r.acceleration,r.activePower,r.dissipationRate];};
  const stage=(k,scale)=>y.map((v,i)=>v+scale*k[i]);
  const k1=derivative(y,0),k2=derivative(stage(k1,h/2),h/2),k3=derivative(stage(k2,h/2),h/2),k4=derivative(stage(k3,h),h);
  const v=y.map((x,i)=>x+h*(k1[i]+2*k2[i]+2*k3[i]+k4[i])/6);
  if(v[0]<0||v[0]>QMAX)return {...s,halted:true}; // pause at last admissible state; no invented joint contact
  return {...s,q:v[0],w:v[1],work:v[2],dissipation:v[3],a:at(h),time:s.time+h};
}
export function elbowTrace(p=ELBOW,duration=0.6,release=0.3){
  let s=elbowInitial(p);const initial=elbowResults(s,p).energy;const rows=[];
  for(let n=0;n<=Math.round(duration/p.dt);n++){
    const r=elbowResults(s,p);rows.push({...s,...r,balanceResidual:r.energy-initial-s.work+s.dissipation});
    if(s.halted)break;
    s=elbowStep(s,{...p,excitation:n*p.dt>=release?0:p.excitation});
  }
  return rows;
}
