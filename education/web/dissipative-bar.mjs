/** Quasistatic small-strain axial standard linear solid. SI units throughout.
 * sigma=E0*eps+E1*(eps-v); eta*vdot=E1*(eps-v).
 * Constant axial resultant and homogeneous coefficients imply eps=c/A, v=z/A.
 * Midpoint area quadrature is explicit; the independent exact compliance is reported.
 */
export const SLS_DEFAULTS=Object.freeze({length:.2,area:.0003,ratio:2,E0:100000,E1:100000,eta:100000,force:.6,segments:32,shape:'linear',ramp:1,hold:2,recovery:3,holdMode:'force',dt:.02});
export function validateParameters(p){
 const bounds={length:[.05,.5],area:[.0003,.001],ratio:[.5,4],E0:[100000,1000000],E1:[0,1000000],eta:[1000,10000000],force:[0,.6],ramp:[.1,2],hold:[.1,5],recovery:[.1,5],dt:[.01,.05],segments:[8,512]};
 for(const [k,[lo,hi]] of Object.entries(bounds))if(!Number.isFinite(p[k])||p[k]<lo||p[k]>hi)throw new RangeError(`Out-of-domain ${k}`);
 if(!Number.isInteger(p.segments)||p.segments%2||!['linear','two-segment'].includes(p.shape)||!['force','extension'].includes(p.holdMode))throw new RangeError('Even refinement and a supported geometry/hold required');
 return p;
}
export function barGeometry(p){
 validateParameters(p);const dxM=p.length/p.segments;
 const samples=Array.from({length:p.segments},(_,i)=>{const sM=(i+.5)*dxM;return {sM,dxM,areaM2:p.area*(p.shape==='linear'?1+(p.ratio-1)*sM/p.length:sM<p.length/2?1:p.ratio)};});
 const exactCg=p.shape==='linear'?p.length/p.area*(p.ratio===1?1:Math.log1p(p.ratio-1)/(p.ratio-1)):p.length/(2*p.area)*(1+1/p.ratio);
 return {samples,Cg:samples.reduce((sum,s)=>sum+s.dxM/s.areaM2,0),exactCg};
}
export function totalDuration(p){return 2*p.ramp+p.hold+p.recovery;}
export function initialState(p){validateParameters(p);return {time:0,z:0,c:0,force:0,workJ:0,dissipationJ:0,phase:'load',heldC:null,unloadN:null,maxResidualJ:0};}
function moments(k,h){
 if(k===0)return {I0:h,I1:h*h/2}; // Continuous limit when the rate underflows.
 // I0=integral exp(-kt)dt and I1=integral t exp(-kt)dt.
 const x=k*h,I0=-Math.expm1(-x)/k;
 const I1=Math.abs(x)<.001?h*h*(.5-x/3+x*x/8-x*x*x/30+x**4/144):(-Math.expm1(-x)-x*Math.exp(-x))/(k*k);
 return {I0,I1};
}
function forceSegment(p,s,h,slope){
 const {Cg}=barGeometry(p),Et=p.E0+p.E1,N=s.force;
 if(p.E1===0){const nextN=N+slope*h;return {...s,force:nextN,c:nextN/p.E0,workJ:s.workJ+Cg/p.E0*(N*slope*h+.5*slope*slope*h*h)};}
 const k=p.E0*p.E1/(p.eta*Et),r=slope/p.E0,B=k*(N/p.E0-s.z)-r;
 const {I0,I1}=moments(k,h),I02=moments(2*k,h).I0;
 // Express zdot=P+B*expm1(-kt), avoiding cancellation between r and B
 // as E1 tends to zero. Integrate the small differences by their convergent
 // exponential series, rather than subtracting nearly equal moments.
 const P=k*(N/p.E0-s.z),x=k*h;
 let J,K;
 if(x<.1){let term=1,factorial=1,j=0,kk=0;for(let n=1;n<=18;n++){term*=-x;factorial*=n+1;j+=term/factorial;if(n>=2)kk+=(2**n-2)*term/factorial;}J=h*j;K=h*kk;}
 else {J=I0-h;K=I02-2*I0+h;}
 const z=s.z+P*I0-r*J,nextN=N+slope*h,c=(nextN+p.E1*z)/Et;
 const dW=Cg/Et*((slope+p.E1*r)*(N*h+.5*slope*h*h)+p.E1*B*(N*I0+slope*I1));
 const dD=Cg*p.eta*(P*P*h+2*P*B*J+B*B*K);
 // Algebraically positive integral; cancellation can leave a few ulps below zero.
 // Clamp only roundoff-sized negatives, otherwise reject the step.
 const roundoff=64*Number.EPSILON*Cg*p.eta*(P*P*h+Math.abs(2*P*B*J)+B*B*K);
 if(dD < -roundoff)throw new RangeError('Negative viscous-loss integral');
 return {...s,z,c,force:nextN,workJ:s.workJ+dW,dissipationJ:s.dissipationJ+Math.max(0,dD)};
}
function extensionSegment(p,s,h){
 if(p.E1===0)return {...s};
 const {Cg}=barGeometry(p),k=p.E1/p.eta,delta=s.c-s.z,z=s.z+delta*(-Math.expm1(-k*h));
 const dD=Cg*p.eta*k*k*delta*delta*moments(2*k,h).I0;
 return {...s,z,force:p.E0*s.c+p.E1*(s.c-z),dissipationJ:s.dissipationJ+dD};
}
export function observe(p,s){
 const g=barGeometry(p);let displacement=0;
 const samples=g.samples.map(a=>{const strain=s.c/a.areaM2,viscousStrain=s.z/a.areaM2,start=displacement;displacement+=strain*a.dxM;return {...a,strain,viscousStrain,displacementStartM:start,displacementEndM:displacement};});
 const storageJ=g.Cg*(p.E0*s.c*s.c+p.E1*(s.c-s.z)**2)/2;
 const zdot=p.E1/p.eta*(s.c-s.z),held=s.phase==='hold'&&p.holdMode==='extension';
 const slope=s.phase==='load'?p.force/p.ramp:s.phase==='unload'?-s.unloadN/p.ramp:0;
 const cdot=held?0:(slope+p.E1*zdot)/(p.E0+p.E1);
 return {time:s.time,phase:s.phase,force:s.force,extensionM:displacement,exactProfileExtensionM:g.exactCg*s.c,profileQuadratureErrorM:(g.Cg-g.exactCg)*s.c,storageJ,workJ:s.workJ,dissipationJ:s.dissipationJ,balanceResidualJ:s.workJ-storageJ-s.dissipationJ,powerW:s.force*g.Cg*cdot,dissipationRateW:g.Cg*p.eta*zdot*zdot,maxStrain:Math.abs(s.c)/(p.area*Math.min(1,p.ratio)),samples};
}
function validateState(p,s){
 for(const k of ['time','z','c','force','workJ','dissipationJ','maxResidualJ'])if(!Number.isFinite(s[k]))throw new RangeError('Non-finite state');
 if(s.time<0||s.time>totalDuration(p)+1e-10||s.dissipationJ<0||!['load','hold','unload','recovery','done'].includes(s.phase))throw new RangeError('Invalid state');
 const n=p.E0*s.c+p.E1*(s.c-s.z);
 if(Math.abs(n-s.force)>1e-10*Math.max(1,Math.abs(s.force))||observe(p,s).maxStrain>.05+1e-12)throw new RangeError('Constitutive or small-strain invariant failed');
 const bounds={load:[0,p.ramp],hold:[p.ramp,p.ramp+p.hold],unload:[p.ramp+p.hold,2*p.ramp+p.hold],recovery:[2*p.ramp+p.hold,totalDuration(p)],done:[totalDuration(p),totalDuration(p)]}[s.phase];
 if(s.time<bounds[0]-1e-10||s.time>bounds[1]+1e-10)throw new RangeError('Phase/time invariant failed');
 if(s.phase==='hold'&&p.holdMode==='extension'&&(!Number.isFinite(s.heldC)||Math.abs(s.c-s.heldC)>1e-16))throw new RangeError('Held extension invariant failed');
 if(s.phase==='load'&&Math.abs(s.force-p.force*s.time/p.ramp)>1e-10)throw new RangeError('Loading ramp invariant failed');
 if(s.phase==='hold'&&p.holdMode==='force'&&Math.abs(s.force-p.force)>1e-10)throw new RangeError('Held force invariant failed');
 if(['recovery','done'].includes(s.phase)&&Math.abs(s.force)>1e-10)throw new RangeError('Released force invariant failed');
 const o=observe(p,s);
 if(Math.abs(o.balanceResidualJ)>256*Number.EPSILON*Math.max(1,Math.abs(s.workJ),o.storageJ,s.dissipationJ))throw new RangeError('Energy ledger invariant failed');
 if(['unload','recovery','done'].includes(s.phase)&&(!Number.isFinite(s.unloadN)||s.unloadN<0||s.unloadN>p.force+1e-10))throw new RangeError('Invalid unloading reaction');
 if(s.phase==='unload'&&Math.abs(s.force-s.unloadN*(1-(s.time-p.ramp-p.hold)/p.ramp))>1e-10)throw new RangeError('Unloading ramp invariant failed');
}
export function stepProtocol(p,state,h=p.dt){
 validateParameters(p);validateState(p,state);
 if(!Number.isFinite(h)||h<=0||h>totalDuration(p))throw new RangeError('Positive bounded step required');
 let s={...state},remaining=Math.min(h,totalDuration(p)-s.time);
 while(remaining>1e-12&&s.phase!=='done'){
  const end=s.phase==='load'?p.ramp:s.phase==='hold'?p.ramp+p.hold:s.phase==='unload'?2*p.ramp+p.hold:totalDuration(p);
  const dt=Math.min(remaining,end-s.time);
  if(dt>0)s=s.phase==='hold'&&p.holdMode==='extension'?extensionSegment(p,s,dt):forceSegment(p,s,dt,s.phase==='load'?p.force/p.ramp:s.phase==='unload'?-s.unloadN/p.ramp:0);
  s.time+=dt;remaining-=dt;
  if(end-s.time<1e-11){s.time=end;if(s.phase==='load'){s.phase='hold';s.heldC=s.c;}else if(s.phase==='hold'){s.phase='unload';s.unloadN=s.force;}else if(s.phase==='unload'){s.phase='recovery';s.force=0;s.c=p.E1*s.z/(p.E0+p.E1);}else s.phase='done';}
  const result=observe(p,s);s.maxResidualJ=Math.max(s.maxResidualJ,Math.abs(result.balanceResidualJ));validateState(p,s);
 }
 return s;
}
export function runProtocol(p){let s=initialState(p);const trace=[observe(p,s)];while(s.phase!=='done'){s=stepProtocol(p,s);trace.push(observe(p,s));}return {parameters:{...p},state:s,trace};}
