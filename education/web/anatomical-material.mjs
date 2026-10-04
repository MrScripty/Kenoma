/** Objective finite-strain fixture laws. SI; authored engineering constants.
 * Active potential is a fixed-activation solve device, not passive storage.
 * No force-velocity or human validation is implemented here.
 */
export const MUSCLE_FIXTURE=Object.freeze({mu:1000,bulk:1e6,kf:20000,b:6,sigma0:300000,optimumStretch:1,activeWidth:.5});
export const TENDON_FIXTURE=Object.freeze({young:50e6,toe:.03});
export const determinant=F=>F[0]*(F[4]*F[8]-F[5]*F[7])-F[1]*(F[3]*F[8]-F[5]*F[6])+F[2]*(F[3]*F[7]-F[4]*F[6]);
export function inverseTranspose(F,J=determinant(F)){
 if(!(J>0))throw new RangeError('Positive material determinant required');
 return [(F[4]*F[8]-F[5]*F[7])/J,(F[5]*F[6]-F[3]*F[8])/J,(F[3]*F[7]-F[4]*F[6])/J,(F[2]*F[7]-F[1]*F[8])/J,(F[0]*F[8]-F[2]*F[6])/J,(F[1]*F[6]-F[0]*F[7])/J,(F[1]*F[5]-F[2]*F[4])/J,(F[2]*F[3]-F[0]*F[5])/J,(F[0]*F[4]-F[1]*F[3])/J];
}
export function activeCurve(lambda,width=.5){
 const t=(lambda-1)/width;if(Math.abs(t)>=1)return {value:0,primitive:Math.sign(t)*width*8/15};
 return {value:(1-t*t)**2,primitive:width*(t-2*t**3/3+t**5/5)};
}
export function muscleMaterial(F,f0,a,p=MUSCLE_FIXTURE){
 if(F.length!==9||f0.length!==3||![...F,...f0,a,...Object.values(p)].every(Number.isFinite)||a<0||a>1||Math.abs(Math.hypot(...f0)-1)>1e-10||p.mu<=0||p.bulk<=0||p.kf<0||p.b<=0||p.sigma0<0||p.activeWidth<=0||p.optimumStretch!==1)throw new RangeError('Material domain/normalized reference fibre');
 const J=determinant(F);if(J<=1e-6)throw new RangeError('Material determinant below fixture guard');
 const invT=inverseTranspose(F,J),I1=F.reduce((v,x)=>v+x*x,0),iso=J**(-2/3),logJ=Math.log(J),d=Array.from({length:3},(_,i)=>F[3*i]*f0[0]+F[3*i+1]*f0[1]+F[3*i+2]*f0[2]),lambda=Math.hypot(...d),n=d.map(v=>v/lambda),stretch=Math.max(lambda-1,0),exponential=Math.expm1(p.b*stretch),curve=activeCurve(lambda,p.activeWidth);
 const passiveFiber=p.kf/p.b**2*(exponential-p.b*stretch),passiveFiberDerivative=p.kf/p.b*exponential;
 const energy={matrix:p.mu/2*(iso*I1-3),volume:p.bulk/2*logJ**2,passiveFiber,activePotential:a*p.sigma0*curve.primitive};
 const Ppassive=F.map((v,i)=>p.mu*iso*(v-I1/3*invT[i])+p.bulk*logJ*invT[i]+passiveFiberDerivative*n[Math.floor(i/3)]*f0[i%3]);
 const Pactive=F.map((_,i)=>a*p.sigma0*curve.value*n[Math.floor(i/3)]*f0[i%3]),P=Ppassive.map((v,i)=>v+Pactive[i]);
 const cauchy=Array.from({length:9},(_,i)=>{const r=Math.floor(i/3),c=i%3;return [0,1,2].reduce((sum,k)=>sum+P[3*r+k]*F[3*c+k],0)/J;});
 const passiveStored=energy.matrix+energy.volume+energy.passiveFiber;
 if(![passiveStored,energy.activePotential,...P,...cauchy].every(Number.isFinite))throw new RangeError('Material overflow outside admissible trial state');
 return {J,lambda,direction:n,energy,passiveStored,solvePotential:passiveStored+energy.activePotential,Ppassive,Pactive,P,cauchy,forceVelocityMultiplier:1};
}
export function tendonMaterial(epsilon,p=TENDON_FIXTURE){
 if(!Number.isFinite(epsilon)||p.young<=0||!Number.isFinite(p.young)||p.toe<=0||!Number.isFinite(p.toe))throw new RangeError('Tendon material domain');
 if(epsilon<=0)return {stressPa:0,energyDensityPa:0,tangentPa:0};
 if(epsilon<p.toe)return {stressPa:p.young*epsilon**2/(2*p.toe),energyDensityPa:p.young*epsilon**3/(6*p.toe),tangentPa:p.young*epsilon/p.toe};
 return {stressPa:p.young*(epsilon-p.toe/2),energyDensityPa:p.young*(epsilon**2/2-p.toe*epsilon/2+p.toe**2/6),tangentPa:p.young};
}
export function tendonSegment(length,L0,A0,p=TENDON_FIXTURE){
 if(![length,L0,A0].every(Number.isFinite)||length<0||L0<=0||A0<=0)throw new RangeError('Positive reference tendon geometry');
 const r=tendonMaterial(length/L0-1,p);return {...r,forceN:A0*r.stressPa,storedEnergyJ:A0*L0*r.energyDensityPa,stiffnessNPerM:A0/L0*r.tangentPa};
}
