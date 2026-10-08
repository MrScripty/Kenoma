/** Original passive guided macro-element fixture, SI. All inputs are authored.
 * E is a reduced axial modulus; G is a declared interface shear modulus.
 * This discrete two-link model is not distributed tissue or muscle calibration.
 */
export const GEOMETRY=Object.freeze({areaM2:1e-6,lengthM:.01,interfaceAreaM2:1e-6,interfaceThicknessM:.0002});
export const DEFAULT_INPUT=Object.freeze({deltaMicrometres:1,leftShearKPa:20,rightShearKPa:20,preset:'equal'});
export const PRESETS=Object.freeze({equal:[1e6,1e6],unequal:[.5e6,2e6]});
const finite=(name,x)=>{if(typeof x!=='number'||!Number.isFinite(x))throw new RangeError(`${name}: finite number required`);return x;};
const positive=(name,x)=>{finite(name,x);if(x<=0)throw new RangeError(`${name}: positive value required`);return x;};
const nonnegative=(name,x)=>{finite(name,x);if(x<0)throw new RangeError(`${name}: nonnegative value required`);return x;};
export function axialStiffness(E,A,L){return positive('E',E)*positive('A',A)/positive('L',L);}
export function shearStiffness(G,A,h){return nonnegative('G',G)*positive('interface area',A)/positive('interface thickness',h);}
export function storedEnergy({K1,K2,CL,CR,delta},u,v){
 return K1*u*u/2+K2*(delta-v)**2/2+CL*v*v/2+CR*(delta-u)**2/2;
}
export function equilibrium({K1,K2,CL,CR,delta}){
 positive('K1',K1);positive('K2',K2);nonnegative('CL',CL);nonnegative('CR',CR);finite('delta',delta);
 const u=CR*delta/(K1+CR),v=K2*delta/(K2+CL);
 const upperForceN=K1*u,lowerForceN=K2*(delta-v),leftExchangeN=CL*v,rightExchangeN=CR*(delta-u);
 const effectiveStiffnessNPerM=K1*CR/(K1+CR)+K2*CL/(K2+CL);
 const leftPullN=upperForceN+leftExchangeN,rightPullN=lowerForceN+rightExchangeN;
 const p={K1,K2,CL,CR,delta},energyJ=storedEnergy(p,u,v);
 const r={...p,u,v,leftSlipM:v,rightSlipM:delta-u,upperExtensionM:u,lowerExtensionM:delta-v,
  upperForceN,lowerForceN,leftExchangeN,rightExchangeN,effectiveStiffnessNPerM,leftPullN,rightPullN,
  externalLeftForceN:-leftPullN,externalRightForceN:rightPullN,energyJ,
  reducedEnergyJ:effectiveStiffnessNPerM*delta*delta/2,
  upperResidualN:upperForceN-rightExchangeN,lowerResidualN:lowerForceN-leftExchangeN,
  wholeResultantN:rightPullN-leftPullN};
 if(!Object.values(r).every(Number.isFinite))throw new RangeError('Overflow outside finite fixture domain');
 return r;
}
export function labState(input=DEFAULT_INPUT){
 const {deltaMicrometres,leftShearKPa,rightShearKPa,preset}=input;
 for(const [name,x,max] of [['displacement',deltaMicrometres,2],['left interface G',leftShearKPa,80],['right interface G',rightShearKPa,80]]){
  nonnegative(name,x);if(x>max)throw new RangeError(`${name}: outside authored teaching range`);
 }
 if(!Object.hasOwn(PRESETS,preset))throw new RangeError('Choose an authored axial-modulus preset');
 const [E1,E2]=PRESETS[preset],g=GEOMETRY;
 const result=equilibrium({K1:axialStiffness(E1,g.areaM2,g.lengthM),K2:axialStiffness(E2,g.areaM2,g.lengthM),
  CL:shearStiffness(leftShearKPa*1000,g.interfaceAreaM2,g.interfaceThicknessM),
  CR:shearStiffness(rightShearKPa*1000,g.interfaceAreaM2,g.interfaceThicknessM),delta:deltaMicrometres*1e-6});
 const r={input:{...input},geometry:{...g},E1Pa:E1,E2Pa:E2,...result,
  upperStrain:result.u/g.lengthM,lowerStrain:(result.delta-result.v)/g.lengthM,
  leftShearStrain:result.v/g.interfaceThicknessM,rightShearStrain:(result.delta-result.u)/g.interfaceThicknessM};
 if(Math.max(Math.abs(r.upperStrain),Math.abs(r.lowerStrain))>.0002+1e-15||Math.max(Math.abs(r.leftShearStrain),Math.abs(r.rightShearStrain))>.01+1e-15)
  throw new RangeError('Authored small-strain admission failed');
 return r;
}
