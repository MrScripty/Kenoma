/* Educational scalar fixture and continuous-time PI. No anatomical model.
 * Source curve kernels: OpenSim 4.5.2, Apache-2.0, Stanford/Authors 2005-2017.
 * This new numerical/controller implementation is separate from that runtime.
 */
export function createVerticalForceLab(P, controls) {
  const F0=100, lf0=.1, lt0=.2, vmax=10, beta=.1, amin=.01, g=P.gravity_m_per_s2;
  class TrialFailure extends Error { constructor(code,message){super(message);this.code=code;} }
  const fail=(code,message)=>{throw new TrialFailure(code,message);};
  const poly=(a,u)=>a.reduceRight((z,c)=>z*u+c,0);
  const bern=(p,u)=>{const t=1-u;return p[0]*t**5+5*p[1]*u*t**4+10*p[2]*u*u*t**3+10*p[3]*u**3*t*t+5*p[4]*u**4*t+p[5]*u**5;};
  const bd=(p,u)=>{const t=1-u;return 5*((p[1]-p[0])*t**4+4*(p[2]-p[1])*u*t**3+6*(p[3]-p[2])*u*u*t*t+4*(p[4]-p[3])*u**3*t+(p[5]-p[4])*u**4);};
  const choose=(n,k)=>{let z=1;for(let j=1;j<=k;j++)z=z*(n-j+1)/j;return z;};
  const power=(p)=>Array.from({length:6},(_,k)=>{let z=0;for(let j=0;j<=k;j++)z+=p[j]*choose(5,j)*choose(5-j,k-j)*(-1)**(k-j);return z;});
  function curve(r){
    const seg=r.segments.map(([x,y])=>{const xp=power(x),yp=power(y),dx=xp.slice(1).map((v,i)=>v*(i+1)),prod=Array(10).fill(0);for(let i=0;i<6;i++)for(let j=0;j<5;j++)prod[i+j]+=yp[i]*dx[j];return {x,y,primitive:[0,...prod.map((v,i)=>v/(i+1))]};});
    const totals=seg.map(p=>poly(p.primitive,1));
    function locate(x){const j=seg.findIndex(p=>x<=p.x[5]);const z=seg[Math.max(0,j)];let lo=0,hi=1,u=(x-z.x[0])/(z.x[5]-z.x[0]);for(let k=0;k<32;k++){const err=bern(z.x,u)-x;if(Math.abs(err)<=1e-15)return {j:Math.max(0,j),z,u};if(err<0)lo=u;else hi=u;const next=u-err/bd(z.x,u);u=next>lo&&next<hi?next:(lo+hi)/2;}fail('curve-root','Source curve inversion failed');}
    function value(x,derivative=false){const [x0,x1,y0,y1,d0,d1]=r.bounds;if(x<=x0)return derivative?d0:y0+d0*(x-x0);if(x>=x1)return derivative?d1:y1+d1*(x-x1);const {z,u}=locate(x);return derivative?bd(z.y,u)/bd(z.x,u):bern(z.y,u);}
    function primitive(x){const [x0,x1,y0,y1,d0,d1]=r.bounds;if(x<=x0)return y0*(x-x0)+d0*(x-x0)**2/2;if(x>=x1)return totals.reduce((a,b)=>a+b,0)+y1*(x-x1)+d1*(x-x1)**2/2;const {j,z,u}=locate(x);return totals.slice(0,j).reduce((a,b)=>a+b,0)+poly(z.primitive,u);}
    return {value,integral:(a,b)=>primitive(b)-primitive(a)};
  }
  const C=Object.fromEntries(Object.entries(controls).map(([n,r])=>[n,curve(r)]));
  function validate(m,target){if(!Number.isFinite(m)||m<=0)fail('input','Mass must be finite and greater than zero');if(!Number.isFinite(target)||target<0)fail('input','Target must be finite and nonnegative');if(m<P.mass_range_kg[0]||m>P.mass_range_kg[1]||target>P.target_range_N[1])fail('range','Request is outside the qualified UI range');}
  function inverseT(force){let lo=1,hi=1.1;for(let i=0;i<64;i++){const s=(lo+hi)/2;if(C.tendon.value(s)<force)lo=s;else hi=s;}const s=(lo+hi)/2;if(Math.abs(F0*C.tendon.value(s)-F0*force)>P.budgets.force_N)fail('initial-root','Tendon preload inversion failed');return s;}
  function init(caseName='baseline',m=.5,target=.5*g,perturb=0){
    validate(m,target);const descending=caseName.startsWith('descending');const a=descending?.5:.5*g/F0,q0=descending?1.10:1,preload=F0*(a*C.active.value(q0)+C.passive.value(q0));const L0=lf0*q0+lt0*inverseT(preload/F0);
    return {caseName,m,target,L0,ub:a,preload,q0,perturb,z:[0,0,a,q0+perturb,0,0,0,0,0,0,0]};
  }
  function phases(cfg){const W=cfg.m*g,T=cfg.target;switch(cfg.caseName){
    case 'pulse':return [{end:.05,target:W},{end:.10,target:T},{end:.15,target:W},{end:.25,target:.8*W,brake:1},{end:.30,target:W}];
    case 'lower':return [{end:.05,target:W},{end:.10,target:T},{end:.20,target:1.2*W,brake:-1},{end:.30,target:W}];
    case 'release':return [{end:.05,target:W},{end:.30,target:0,mode:'release'}];
    case 'high':return [{end:.05,target:W},{end:.15,target:T},{end:.30,target:W}];
    case 'descending_fixed':return [{end:.15,target:T,mode:'fixed'}];
    case 'descending_pi':return [{end:.15,target:T}];
    default:return [{end:.30,target:T}];
  }}
  function output(z,cfg,phase){
    if(!z.every(Number.isFinite))fail('nonfinite','Nonfinite intermediate state');const [y,w,a,q,I]=z;
    if(a<amin-1e-12||a>1+1e-12)fail('activation-bound','Activation left source bounds');if(q<=.4441)fail('fiber-bound','Unqualified fiber lower-length event');
    const s=(cfg.L0-y-lf0*q)/lt0;if(s<=1)fail('slack','Unqualified tendon slack event');
    const FT=F0*C.tendon.value(s),fal=C.active.value(q),fpe=C.passive.value(q),e=(phase.target-FT)/F0;
    const uraw=cfg.ub+P.kp*e+I,u=phase.mode==='fixed'?cfg.ub:phase.mode==='release'?amin:Math.max(amin,Math.min(1,uraw));
    let lo=P.velocity_bracket[0],hi=P.velocity_bracket[1],v=0;
    const balance=v=>F0*(a*fal*C.velocity.value(v)+fpe+beta*v)-FT;
    if(balance(lo)>0||balance(hi)<0)fail('velocity-bracket','Fiber velocity root is unbracketed');let residual=Infinity;
    for(let k=0;k<P.velocity_iterations;k++){residual=balance(v);if(Math.abs(residual)<=1e-10)break;if(residual<0)lo=v;else hi=v;const next=v-residual/(F0*(a*fal*C.velocity.value(v,true)+beta));v=next>lo&&next<hi?next:(lo+hi)/2;}
    residual=balance(v);if(!Number.isFinite(v)||Math.abs(residual)>P.budgets.force_N)fail('force-residual','Fiber force residual failed');
    const lfdot=lf0*vmax*v,FA=F0*a*fal*C.velocity.value(v),FP=F0*fpe,FD=F0*beta*v;
    const frozen=phase.mode||((uraw>=1&&e>0)||(uraw<=amin&&e<0));const Idot=frozen?0:P.ki_per_s*e;
    const tau=u>a?.01*(.5+1.5*a):.04/(.5+1.5*a),adot=phase.mode==='fixed'?0:(u-Math.max(amin,Math.min(1,a)))/tau;
    return {FT,s,v,u,uraw,e,Idot,adot,lfdot,FA,FP,FD,residual,saturated:uraw>=1||uraw<=amin,Pactive:-FA*lfdot,D:FD*lfdot,loadPower:FT*w,fiberPower:FP*lfdot,tendonPower:FT*(-w-lfdot),acceleration:(FT-cfg.m*g)/cfg.m};
  }
  function rhs(t,z,cfg,phase){let o;try{o=output(z,cfg,phase);
    if(!phase.mode&&Number.isFinite(phase.startRaw)){
      const edot=-(F0/lt0*C.tendon.value(o.s,true)*(-z[1]-o.lfdot))/F0,df=P.kp*edot,di=df+P.ki_per_s*o.e;
      const crossed=limit=>(phase.startRaw-limit)*(o.uraw-limit)<=0&&phase.startRaw!==o.uraw;
      if((crossed(1)&&o.e>0&&df<0&&di>0)||(crossed(amin)&&o.e<0&&df>0&&di<0))fail('antiwindup-surface','Unqualified opposing anti-windup switching surface');
    }
  }catch(e){e.stageTime=t;e.stageState=z.slice();throw e;}return [z[1],o.acceleration,o.adot,vmax*o.v,o.Idot,o.Pactive,o.D,o.loadPower,o.fiberPower,o.tendonPower,o.FT-cfg.m*g];}
  function trialStep(t,z,h,cfg,phase){phase={...phase,startRaw:output(z,cfg,phase).uraw};const add=(base,rate,k)=>base.map((v,i)=>v+k*rate[i]);const a=rhs(t,z,cfg,phase),b=rhs(t+h/2,add(z,a,h/2),cfg,phase),c=rhs(t+h/2,add(z,b,h/2),cfg,phase),d=rhs(t+h,add(z,c,h),cfg,phase);const next=z.map((v,i)=>v+h*(a[i]+2*b[i]+2*c[i]+d[i])/6);rhs(t+h,next,cfg,phase);return next;}
  function storage(z,cfg){const o=output(z,cfg,{target:cfg.target});return {fiber:F0*lf0*C.passive.integral(cfg.z[3],z[3]),tendon:F0*lt0*C.tendon.integral((cfg.L0-lf0*cfg.z[3])/lt0,o.s),load:.5*cfg.m*z[1]**2+cfg.m*g*z[0]};}
  function row(t,z,cfg,phase){const o=output(z,cfg,phase),E=storage(z,cfg);return {t,z:z.slice(),target:phase.target,mode:phase.mode||'PI',...o,...E,energyError:E.fiber+E.tendon+E.load-z[5]+z[6],momentumError:cfg.m*z[1]-z[10]};}
  function run(cfg,dt=P.fine_step_s){
    if(!Number.isFinite(dt)||dt<=0)fail('input','Integration step must be finite and positive');
    let t=0,z=cfg.z.slice(),failure=null;const events=[],history=[],initial=cfg.z.slice();
    function save(phase){const r=row(t,z,cfg,phase);if(history.length&&Math.abs(history.at(-1).t-t)<1e-12)history[history.length-1]=r;else history.push(r);}
    const schedule=phases(cfg);for(let index=0;index<schedule.length&&!failure;index++){
      const phase=schedule[index];if(phase.end<=t+1e-12)continue;let armed=false;save(phase);
      while(t<phase.end-1e-12){
        if(phase.brake&&z[1]*phase.brake>P.brake_arm_velocity_m_per_s)armed=true;
        const nextGrid=(Math.floor((t+1e-10)/.001)+1)*.001;const h=Math.min(dt,phase.end-t,nextGrid-t);const previous=z.slice(),previousTime=t;
        try{
          let next=trialStep(t,z,h,cfg,phase),nextTime=t+h;
          if(phase.brake&&armed&&z[1]*phase.brake>0&&next[1]*phase.brake<=0){let lo=0,hi=h;for(let k=0;k<P.event_iterations&&hi-lo>P.event_root_time_s;k++){const mid=(lo+hi)/2,probe=trialStep(t,z,mid,cfg,phase);if(probe[1]*phase.brake>0)lo=mid;else hi=mid;}nextTime=t+hi;next=trialStep(t,z,hi,cfg,phase);z=next;t=nextTime;save(phase);events.push({type:'brake-crossing',t,armed:true,direction:phase.brake,bracket:[previousTime+lo,previousTime+hi]});break;}
          z=next;t=nextTime;if(Math.abs(t/.001-Math.round(t/.001))<1e-7||Math.abs(t-phase.end)<1e-10)save(phase);
        }catch(e){z=previous;t=previousTime;failure={code:e.code||'exception',message:e.message,acceptedTime:t,acceptedState:z.slice(),failedStageTime:e.stageTime??t+h,failedStageState:e.stageState||null};save(phase);events.push({type:'rejected-trial',t,code:failure.code});break;}
      }
      if(!failure&&phase.brake&&t>=phase.end-1e-12)events.push({type:'brake-timeout',t,armed});
      if(!failure)events.push({type:'phase-end',t,phase:index});
    }
    let tracking={status:'not-applicable'};const window=P.tracking_windows_s[cfg.caseName];if(window){const rows=history.filter(r=>r.t>=window[0]-1e-10&&r.t<=window[1]+1e-10),changed=rows.some(r=>Math.abs(r.target-rows[0].target)>1e-12||r.mode!==rows[0].mode);tracking=t<window[1]-1e-10?{status:'window-not-reached',window}:changed?{status:'window-invalid-command-change',window}:{status:rows.length&&Math.max(...rows.map(r=>Math.abs(r.FT-r.target)))<=.01*cfg.m*g?'met':'missed',window,maxError:Math.max(...rows.map(r=>Math.abs(r.FT-r.target))),budget:.01*cfg.m*g};}
    return {cfg:{...cfg,z:initial},dt,history,events,failure,acceptedTime:t,tracking,initialZeroVelocityCapacity:F0*(C.active.value(initial[3])+C.passive.value(initial[3])),numericalStatus:failure?'stopped-at-unqualified-or-failed-trial':'completed',motion:history.length?{displacement:z[0],velocity:z[1],acceleration:history.at(-1).acceleration}:null};
  }
  function descendingMass(){return F0*(.5*C.active.value(1.1)+C.passive.value(1.1))/g;}
  return {P,C,init,run,output,rhs,trialStep,storage,phases,validate,descendingMass,constants:{F0,lf0,lt0,vmax,beta,amin,g},TrialFailure};
}
if(typeof window!=='undefined')window.createVerticalForceLab=createVerticalForceLab;
