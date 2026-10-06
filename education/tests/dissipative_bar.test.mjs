import test from 'node:test';
import assert from 'node:assert/strict';
import {SLS_DEFAULTS,validateParameters,barGeometry,initialState,stepProtocol,observe,runProtocol,totalDuration} from '../web/dissipative-bar.mjs';
import {BAR_DEFAULTS,barState} from '../web/tapered-bar.mjs';

function close(actual,expected,{abs=2e-12,rel=2e-8}={}){
 assert.ok(Number.isFinite(actual)&&Number.isFinite(expected));
 assert.ok(Math.abs(actual-expected)<=abs+rel*Math.abs(expected),`${actual} differs from independent reference ${expected}`);
}

// Independent spatial cells, not the production c/z reduction or exponential
// moments. RK4 evolves each Maxwell viscous strain; Simpson integrates applied
// power and eta*A*vdot^2 separately, never obtaining either from the balance.
function reference(p,times){
 const dx=p.length/p.segments;
 const areas=Array.from({length:p.segments},(_,i)=>p.area*(p.shape==='linear'?1+(p.ratio-1)*(i+.5)/p.segments:i<p.segments/2?1:p.ratio));
 const edges=[p.ramp,p.ramp+p.hold,2*p.ramp+p.hold,2*p.ramp+p.hold+p.recovery];
 let time=0,phase=0,v=areas.map(()=>0),held=null,unloadN=0,work=0,loss=0;
 const maxStep=Math.min(.001,p.E1===0?.001:.02*p.eta/p.E1);
 function field(t,values){
  const slope=phase===0?p.force/p.ramp:phase===2?-unloadN/p.ramp:0;
  const imposedN=phase===0?p.force*t/p.ramp:phase===1?p.force:phase===2?unloadN*(1-(t-edges[1])/p.ramp):0;
  const extensionHold=phase===1&&p.holdMode==='extension';
  const strains=areas.map((A,i)=>extensionHold?held[i]:(imposedN/A+p.E1*values[i])/(p.E0+p.E1));
  const rates=strains.map((eps,i)=>p.E1/p.eta*(eps-values[i]));
  const N=extensionHold?areas[0]*(p.E0*strains[0]+p.E1*(strains[0]-values[0])):imposedN;
  const power=extensionHold?0:N*areas.reduce((sum,A,i)=>sum+dx*(slope/A+p.E1*rates[i])/(p.E0+p.E1),0);
  const dissipation=areas.reduce((sum,A,i)=>sum+dx*A*p.eta*rates[i]**2,0);
  return {strains,rates,N,power,dissipation};
 }
 function rk4(t,values,h){
  const k1=field(t,values).rates;
  const k2=field(t+h/2,values.map((x,i)=>x+h*k1[i]/2)).rates;
  const k3=field(t+h/2,values.map((x,i)=>x+h*k2[i]/2)).rates;
  const k4=field(t+h,values.map((x,i)=>x+h*k3[i])).rates;
  return values.map((x,i)=>x+h*(k1[i]+2*k2[i]+2*k3[i]+k4[i])/6);
 }
 const rows=[];
 for(const target of times){
  while(time<target-1e-13){
   const h=Math.min(maxStep,target-time,edges[phase]-time);
   const mid=rk4(time,v,h/2),next=rk4(time,v,h);
   const a=field(time,v),b=field(time+h/2,mid),c=field(time+h,next);
   work+=h*(a.power+4*b.power+c.power)/6;
   loss+=h*(a.dissipation+4*b.dissipation+c.dissipation)/6;
   v=next;time+=h;
   if(Math.abs(time-edges[phase])<1e-12){
    time=edges[phase];
    if(phase===0)held=field(time,v).strains;
    if(phase===1)unloadN=field(time,v).N;
    phase++;
   }
  }
  const f=field(target,v);
  const storage=areas.reduce((sum,A,i)=>sum+dx*A*(p.E0*f.strains[i]**2+p.E1*(f.strains[i]-v[i])**2)/2,0);
  rows.push({time:target,force:f.N,strains:f.strains,viscousStrains:[...v],extension:f.strains.reduce((sum,x)=>sum+dx*x,0),work,loss,storage});
 }
 return rows;
}

function compareReference(p,result,tolerance){
 const refs=reference(p,result.trace.map(row=>row.time));
 result.trace.forEach((row,i)=>{
  const r=refs[i];close(row.force,r.force,tolerance);close(row.extensionM,r.extension,tolerance);
  close(row.storageJ,r.storage,tolerance);close(row.workJ,r.work,tolerance);close(row.dissipationJ,r.loss,tolerance);
  row.samples.forEach((cell,j)=>{close(cell.strain,r.strains[j],tolerance);close(cell.viscousStrain,r.viscousStrains[j],tolerance);});
 });
 return refs;
}

for(const variation of [
 {},{holdMode:'extension'},{shape:'two-segment',ratio:.5},
 {eta:1000,E1:500000,holdMode:'extension',segments:8},
 {eta:10000000,E1:50000,ramp:.1,hold:.1,recovery:.1},
 {E1:0,holdMode:'extension'},
])test(`per-cell RK4/Simpson checks independent state, work and loss ${JSON.stringify(variation)}`,()=>{
 const p={...SLS_DEFAULTS,segments:8,...variation},result=runProtocol(p);
 compareReference(p,result);
 let previousD=0;
 for(const row of result.trace){
  assert.ok(row.dissipationJ>=previousD);previousD=row.dissipationJ;
  assert.ok(Math.abs(row.balanceResidualJ)<5e-12);
  row.samples.forEach(cell=>close((p.E0*cell.strain+p.E1*(cell.strain-cell.viscousStrain))*cell.areaM2,row.force));
 }
 assert.equal(result.state.phase,'done');assert.equal(result.state.time,totalDuration(p));
});

test('force hold creeps; fixed extension relaxes force, with zero external hold work',()=>{
 const p={...SLS_DEFAULTS,segments:16};
 const loaded=stepProtocol(p,initialState(p),p.ramp);
 const forceHeld=stepProtocol(p,loaded,p.hold);
 const e={...p,holdMode:'extension'},extensionHeld=stepProtocol(e,loaded,p.hold);
 assert.ok(forceHeld.c>loaded.c);close(forceHeld.force,p.force);
 close(extensionHeld.c,loaded.c);assert.ok(extensionHeld.force<loaded.force*.7);
 assert.ok(forceHeld.workJ>loaded.workJ);assert.equal(extensionHeld.workJ,loaded.workJ);
 assert.ok(forceHeld.dissipationJ>loaded.dissipationJ);assert.ok(extensionHeld.dissipationJ>loaded.dissipationJ);
 compareReference(e,{trace:[observe(e,initialState(e)),observe(e,loaded),observe(e,extensionHeld)]});
});

for(const holdMode of ['force','extension'])test(`${holdMode} protocol crosses finite ramps continuously, returns energy and dissipates during recovery`,()=>{
 const p={...SLS_DEFAULTS,holdMode};
 const result=runProtocol(p),boundaries=[p.ramp,p.ramp+p.hold,2*p.ramp+p.hold];
 for(const t of boundaries){
  const before=stepProtocol(p,initialState(p),t-1e-7),at=stepProtocol(p,initialState(p),t),after=stepProtocol(p,initialState(p),t+1e-7);
  for(const key of ['z','c','force','workJ','dissipationJ']){
   close(before[key],at[key],{abs:2e-7,rel:0});close(after[key],at[key],{abs:2e-7,rel:0});
  }
 }
 const held=stepProtocol(p,initialState(p),p.ramp+p.hold),released=stepProtocol(p,held,p.ramp),end=result.state;
 assert.ok(released.workJ<held.workJ,'unloading must return external work');
 assert.equal(released.force,0);assert.ok(released.c>0,'finite unloading retains delayed strain');
 assert.ok(end.c<released.c);assert.ok(end.dissipationJ>released.dissipationJ);
 assert.ok(observe(p,end).storageJ<observe(p,released).storageJ);
 assert.ok(end.dissipationJ>1e-4);assert.ok(end.workJ>0);
});

test('arbitrary boundary-spanning steps and each supported display dt give the same physical endpoint',()=>{
 for(const holdMode of ['force','extension']){
  const p={...SLS_DEFAULTS,ramp:.37,hold:.83,recovery:1.13,holdMode};
  const all=stepProtocol(p,initialState(p),totalDuration(p));
  for(const dt of [.01,.02,.03,.05]){
   const r=runProtocol({...p,dt});
   for(const key of ['z','c','force','workJ','dissipationJ'])close(r.state[key],all[key],{abs:4e-12,rel:2e-10});
   assert.equal(r.state.time,totalDuration(p));assert.equal(r.state.phase,'done');
  }
  let s=initialState(p);
  for(const h of [.6,.91,totalDuration(p)-1.51])s=stepProtocol(p,s,h);
  for(const key of ['z','c','force','workJ','dissipationJ'])close(s[key],all[key],{abs:4e-12,rel:2e-10});
 }
});

test('taper compliance follows the independent logarithmic integral and midpoint refinement',()=>{
 for(const ratio of [.5,1,1+1e-12,2,4]){
  const p={...SLS_DEFAULTS,ratio},errors=[];
  const exact=ratio===1?p.length/p.area:p.length*Math.log1p(ratio-1)/(p.area*(ratio-1));
  for(const segments of [8,16,32,64]){
   const g=barGeometry({...p,segments});close(g.exactCg,exact,{abs:1e-10,rel:1e-14});errors.push(Math.abs(g.Cg-exact));
  }
  if(Math.abs(ratio-1)>.01)for(let i=1;i<errors.length;i++)assert.ok(errors[i]<errors[i-1]/3.9);
 }
});

test('E1=0 exactly recovers existing passive-bar geometry and energy, including reversed two-segment areas',()=>{
 for(const shape of ['linear','two-segment'])for(const ratio of [.5,1,2,4]){
  const p={...SLS_DEFAULTS,E1:0,shape,ratio,segments:32},s=stepProtocol(p,initialState(p),p.ramp),r=observe(p,s);
  const elastic=barState({...BAR_DEFAULTS,length:p.length,area:p.area,ratio,segments:p.segments,modulus:p.E0,force:p.force,shape,mode:'passive'});
  close(r.extensionM,elastic.numericalExtensionM);close(r.exactProfileExtensionM,elastic.exactExtensionM);
  close(r.storageJ,elastic.elasticEnergyJ);close(r.workJ,elastic.elasticEnergyJ);
  assert.equal(r.dissipationJ,0);assert.equal(s.z,0);
  const end=stepProtocol(p,s,totalDuration(p)-s.time);close(end.c,0);assert.equal(end.dissipationJ,0);
 }
});

test('viscosity and ramp rates change actual state and dissipation, rather than just metadata',()=>{
 const load=p=>stepProtocol(p,initialState(p),p.ramp);
 const fastViscosity={...SLS_DEFAULTS,eta:10000},slowViscosity={...SLS_DEFAULTS,eta:1000000};
 const fast=load(fastViscosity),slow=load(slowViscosity);
 assert.ok(fast.c>slow.c*1.5);assert.ok(fast.z>slow.z*10);
 for(const p of [fastViscosity,slowViscosity])compareReference(p,{trace:[observe(p,initialState(p)),observe(p,load(p))]});
 const fastRamp={...SLS_DEFAULTS,ramp:.1},slowRamp={...SLS_DEFAULTS,ramp:2};
 assert.ok(load(slowRamp).c>load(fastRamp).c*1.2);
 assert.ok(load(slowRamp).dissipationJ>load(fastRamp).dissipationJ);
});

test('tiny positive E1 loss remains continuous with the elastic limit and matches independently squared rate integration',()=>{
 const p={...SLS_DEFAULTS,E1:1e-6,segments:8},r=runProtocol(p);
 const referenceEnd=reference(p,[totalDuration(p)]).at(-1);
 assert.ok(referenceEnd.loss>0&&referenceEnd.loss<1e-23);
 close(r.state.dissipationJ,referenceEnd.loss,{abs:1e-29,rel:2e-5});
});

test('tiny positive E1 state survives a full ramp without subtracting nearly equal elastic terms',()=>{
 for(const E1 of [1e-6,1e-9,1e-12]){
  const p={...SLS_DEFAULTS,E1,segments:8},s=stepProtocol(p,initialState(p),p.ramp),r=observe(p,s);
  const ref=reference(p,[p.ramp]).at(-1);
  for(let i=0;i<r.samples.length;i++)close(r.samples[i].viscousStrain,ref.viscousStrains[i],{abs:1e-28,rel:2e-8});
  close(r.workJ,ref.work,{abs:1e-15,rel:2e-10});
  close(r.dissipationJ,ref.loss,{abs:1e-39,rel:2e-7});
 }
});

test('zero loading leaves both hold modes at zero strain, work and dissipation',()=>{
 for(const holdMode of ['force','extension']){
  const p={...SLS_DEFAULTS,holdMode,force:0},r=runProtocol(p);
  for(const row of r.trace)for(const key of ['force','extensionM','storageJ','workJ','dissipationJ'])assert.equal(row[key],0);
  assert.equal(r.state.z,0);assert.equal(r.state.phase,'done');
 }
});

test('oracle rejects known wrong loss and an elastic reset substituted for the history-dependent state',()=>{
 const p={...SLS_DEFAULTS,segments:8},r=runProtocol(p),ref=reference(p,r.trace.map(row=>row.time));
 const end=ref.at(-1);assert.throws(()=>close(0,end.loss),assert.AssertionError);
 const holdIndex=r.trace.findIndex(row=>row.time>p.ramp+.5),held=ref[holdIndex];
 assert.throws(()=>close(p.force/(p.E0+p.E1)*barGeometry(p).Cg,held.extension),assert.AssertionError);
});

test('parameter and state errors reject without mutating the last valid physical state',()=>{
 const p={...SLS_DEFAULTS},initial=initialState(p),saved=structuredClone(initial);
 const badParameters=[{eta:0},{eta:999},{E1:-1},{E0:0},{force:.61},{ratio:0},{segments:9},{holdMode:'other'},{dt:0}];
 for(const bad of badParameters)assert.throws(()=>validateParameters({...p,...bad}),RangeError);
 for(const bad of [{z:NaN},{c:Infinity},{force:.1},{dissipationJ:-1},{phase:'other'},{time:-1},{time:totalDuration(p)+1},{c:1,force:p.E0+p.E1}])assert.throws(()=>stepProtocol(p,{...initial,...bad}),RangeError);
 for(const h of [0,-1,NaN,Infinity,totalDuration(p)+1])assert.throws(()=>stepProtocol(p,initial,h),RangeError);
 assert.deepEqual(initial,saved);
 const extension={...p,holdMode:'extension'},held=stepProtocol(extension,initial,p.ramp);
 assert.throws(()=>stepProtocol(extension,{...held,heldC:null}),RangeError);
 const unloading=stepProtocol(p,initial,p.ramp+p.hold);
 assert.throws(()=>stepProtocol(p,{...unloading,unloadN:null}),RangeError);
 assert.throws(()=>stepProtocol(p,{...initial,time:.5}),RangeError,'force must agree with the imposed loading ramp at the current time');
 assert.throws(()=>stepProtocol(p,{...initial,phase:'hold'}),RangeError);
 assert.throws(()=>stepProtocol(extension,{...held,heldC:held.c*1.1}),RangeError);
 assert.throws(()=>stepProtocol(p,{...unloading,unloadN:-.1}),RangeError);
 assert.throws(()=>stepProtocol(p,{...unloading,unloadN:p.force*2}),RangeError);
 assert.throws(()=>stepProtocol(p,{...unloading,unloadN:0}),RangeError,'force must agree with the stored unloading ramp');
 assert.throws(()=>stepProtocol(p,{...unloading,workJ:unloading.workJ+.01}),RangeError);
});
