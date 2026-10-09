/** Architecture-to-force bookkeeping in SI. Analytic teaching fixtures only.
 * No anatomical geometry, equilibrium solver, perfusion or calibrated muscle.
 * A0 is area of the reference cut normal to the reference fibre. Aperp is
 * current area projected normal to the current fibre, not arbitrary skin CSA.
 */
const finite=(name,x)=>{if(!Number.isFinite(x))throw new RangeError(`${name} must be finite`);return x;};
const positive=(name,x)=>{finite(name,x);if(x<=0)throw new RangeError(`${name} must be positive`);return x;};
const nonnegative=(name,x)=>{finite(name,x);if(x<0)throw new RangeError(`${name} must be nonnegative`);return x;};
const fraction=(name,x)=>{finite(name,x);if(x<0||x>1)throw new RangeError(`${name} must lie in [0,1]`);return x;};
export function forceLength(lambda,width=.5){
 positive('lambda',lambda);positive('width',width);
 const r=(lambda-1)/width;return Math.abs(r)>=1?0:(1-r*r)**2;
}
export function materialCut({referenceAreaM2,lambda,J,nominalStressPa,cosPennation=1}){
 positive('referenceAreaM2',referenceAreaM2);positive('lambda',lambda);positive('J',J);
 nonnegative('nominalStressPa',nominalStressPa);fraction('cosPennation',cosPennation);
 const projectedCurrentAreaM2=referenceAreaM2*J/lambda;
 const cauchyFiberStressPa=nominalStressPa*lambda/J;
 const axialForceN=nominalStressPa*referenceAreaM2;
 const fromCurrentCutN=cauchyFiberStressPa*projectedCurrentAreaM2;
 const tendonDirectedForceN=axialForceN*cosPennation;
 const r={referenceAreaM2,projectedCurrentAreaM2,cauchyFiberStressPa,nominalStressPa,axialForceN,fromCurrentCutN,tendonDirectedForceN};
 if(!Object.values(r).every(Number.isFinite))throw new RangeError('Result overflow');
 return r;
}
export function aggregateTypes(types){
 if(!Array.isArray(types)||!types.length)throw new RangeError('At least one fibre group required');
 let totalCount=0,totalAreaM2=0,axialForceN=0,tendonDirectedForceN=0;
 const rows=types.map((t,i)=>{
  const count=nonnegative(`count ${i}`,t.count),area=positive(`area ${i}`,t.referenceFiberAreaM2);
  const stress=nonnegative(`stress ${i}`,t.nominalStressPa),c=fraction(`cosine ${i}`,t.cosPennation??1);
  const referenceAreaM2=count*area,forceN=referenceAreaM2*stress;
  totalCount+=count;totalAreaM2+=referenceAreaM2;axialForceN+=forceN;tendonDirectedForceN+=forceN*c;
  return {count,referenceAreaM2,forceN,tendonDirectedForceN:forceN*c};
 });
 positive('totalCount',totalCount);positive('totalAreaM2',totalAreaM2);
 const result={totalCount,totalAreaM2,axialForceN,tendonDirectedForceN,areaWeightedNominalStressPa:axialForceN/totalAreaM2,
  rows:rows.map(r=>({...r,countFraction:r.count/totalCount,areaFraction:r.referenceAreaM2/totalAreaM2}))};
 if(![totalCount,totalAreaM2,axialForceN,tendonDirectedForceN,result.areaWeightedNominalStressPa].every(Number.isFinite))throw new RangeError('Aggregate overflow');
 return result;
}
export function forceFromArea({areaM2,stressPa,cosPennation=1,areaConvention,stressBasis,packingFraction=1}){
 nonnegative('areaM2',areaM2);nonnegative('stressPa',stressPa);fraction('cosPennation',cosPennation);fraction('packingFraction',packingFraction);
 if(!['fiber-normal','tendon-projected'].includes(areaConvention))throw new RangeError('Declare the PCSA projection convention');
 if(!['contractile','whole-muscle-effective'].includes(stressBasis))throw new RangeError('Declare the stress area basis');
 if(stressBasis==='whole-muscle-effective'&&packingFraction!==1)throw new RangeError('Effective whole-muscle stress already includes its area basis; do not repack it');
 const f=areaM2*stressPa*(areaConvention==='fiber-normal'?cosPennation:1)*(stressBasis==='contractile'?packingFraction:1);
 if(!Number.isFinite(f))throw new RangeError('Force overflow');return f;
}
export function taperedSeries(referenceAreasM2,transmittedForceN){
 if(!Array.isArray(referenceAreasM2)||referenceAreasM2.length<2)throw new RangeError('At least two series sections required');
 nonnegative('transmittedForceN',transmittedForceN);
 return referenceAreasM2.map((a,i)=>{
  positive(`reference area ${i}`,a);const nominalStressPa=transmittedForceN/a;
  if(!Number.isFinite(nominalStressPa))throw new RangeError('Stress overflow');
  return {referenceAreaM2:a,forceN:transmittedForceN,nominalStressPa};
 });
}
export function lateralExchange(leftForceN,lateralForcesN){
 nonnegative('leftForceN',leftForceN);
 if(!Array.isArray(lateralForcesN)||!lateralForcesN.length)throw new RangeError('At least one exchange cell required');
 let left=leftForceN;
 return lateralForcesN.map((q,i)=>{
  finite(`lateral force ${i}`,q);const right=left-q;
  nonnegative('rightForceN',right);
  const row={leftForceN:left,rightForceN:right,lateralForceN:q,balanceN:right-left+q};left=right;return row;
 });
}
