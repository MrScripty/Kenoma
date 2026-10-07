/** Whole-path geometry gates and bounded line search; no constitutive implementation. */
import {createHash} from 'node:crypto';
import {elementSegmentPolynomials,certifyPrefix} from './isolated-segment-geometry.mjs';
const digest=x=>createHash('sha256').update(JSON.stringify(x,(_,v)=>typeof v==='bigint'?v.toString():v)).digest('hex');
const maximum=v=>Math.max(...v.map(x=>Math.hypot(...x)));
const delta=(a,b)=>b.map((X,n)=>X.map((x,d)=>x-a[n][d]));
export function certifyRoundedPath(source,start,end){
 const nodes=source.nodes_m.length;
 for(const positions of [start,end]){
  if(positions.length!==nodes||positions.some(X=>X.length!==3||!X.every(Number.isFinite)))throw Error('Nonfinite or malformed path geometry');
  for(const n of new Set([...source.distal_nodes,...source.proximal_nodes]))for(let d=0;d<3;d++)if(positions[n][d]!==source.nodes_m[n][d])throw Error('Exact cap trace changed');
 }
 const elements=source.elements_ten_node.map(ids=>elementSegmentPolynomials(ids.map(n=>source.nodes_m[n]),ids.map(n=>start[n]),ids.map(n=>end[n]))),certificate=certifyPrefix(elements,1n,1n);
 return {...certificate,guard:'exact binary64(1e-6)',segment:'exact dyadic interpolation of newly rounded nodal endpoints',elements:elements.length,spaceTimeControlsRequired:80*elements.length,referenceSha256:digest(source.nodes_m),connectivitySha256:digest(source.elements_ten_node),startSha256:digest(start),endSha256:digest(end),polynomialSha256:digest(elements)};
}
export function certifyState(source,positions){const receipt=certifyRoundedPath(source,positions,positions);if(!receipt.certified)throw Error('Initial/current state cannot certify unchanged whole-path domain');return receipt;}
export function checkedMaterialEvaluation({source,start,coordinates,positions,evaluate,onCertificate=()=>{}}){
 const candidate=positions(coordinates),certificate=certifyRoundedPath(source,start,candidate);onCertificate(certificate);
 if(!certificate.certified)throw Error('Uncertified material evaluation refused');
 const state=evaluate(coordinates);
 if(!Number.isFinite(state.energyJ))throw Error('Nonfinite material energy after certification');
 if(state.positions&&digest(state.positions)!==certificate.endSha256)throw Error('Material geometry differs from certified rounded candidate');
 return state;
}
/** At most21 fractions. Unsupported geometry is the only domain rejection
 * caught here. Unexpected failures after certification propagate immediately. */
export function geometryBacktracking({source,currentCoordinates,currentEnergyJ,gradientN,rawNewtonCoordinates,positions,nodeStep,evaluate,onEvent=()=>{}}){
 const n=currentCoordinates.length;
 if(n!==gradientN.length||n!==rawNewtonCoordinates.length||![...currentCoordinates,...gradientN,...rawNewtonCoordinates,currentEnergyJ].every(Number.isFinite))throw Error('Nonfinite or malformed Newton inputs');
 const current=positions(currentCoordinates);certifyState(source,current);
 const rawNodeStep=nodeStep(rawNewtonCoordinates);
 if(rawNodeStep.length!==current.length||rawNodeStep.some(X=>X.length!==3||!X.every(Number.isFinite)))throw Error('Invalid raw Newton nodal increment');
 for(const node of new Set([...source.distal_nodes,...source.proximal_nodes]))if(rawNodeStep[node].some(x=>x!==0))throw Error('Raw Newton increment changes exact cap trace');
 const rawMaximum=maximum(rawNodeStep);if(!(rawMaximum>0))throw Error('Zero Newton increment');
 const scaling=Math.min(1,.0002/rawMaximum),scaled=Float64Array.from(rawNewtonCoordinates,x=>x*scaling),scaledNodes=nodeStep(scaled),slope=gradientN.reduce((s,g,k)=>s+g*scaled[k],0);
 const direction={kind:'NEWTON_DIRECTION',rawNewtonCoordinatesM:Array.from(rawNewtonCoordinates),rawNewtonNodalIncrementM:rawNodeStep,rawMaximumNodalIncrementM:rawMaximum,scaling,scaledCoordinatesM:Array.from(scaled),scaledNodalIncrementM:scaledNodes,scaledMaximumNodalIncrementM:maximum(scaledNodes),predictedSlopeJ:slope};onEvent(direction);
 if(!(slope<0&&Number.isFinite(slope)))throw Error('Nonfinite or non-descent Newton direction');
 for(let fractionIndex=0;fractionIndex<21;fractionIndex++){
  const alpha=2**(-fractionIndex),trialCoordinates=Float64Array.from(currentCoordinates,(x,k)=>x+alpha*scaled[k]),trial=positions(trialCoordinates),roundedIncrement=delta(current,trial),roundedMaximum=maximum(roundedIncrement);
  const event={kind:'TRIAL',fractionIndex,alpha,coordinatesM:Array.from(trialCoordinates),positionsM:trial,roundedNodalIncrementM:roundedIncrement,roundedMaximumNodalIncrementM:roundedMaximum,roundedEuclideanIncrementM:Math.hypot(...roundedIncrement.flat())};
  if(![...trialCoordinates,...trial.flat()].every(Number.isFinite)){onEvent({...event,disposition:'FAILURE',reason:'Nonfinite rounded candidate'});throw Error('Nonfinite rounded candidate');}
  if(roundedMaximum===0){onEvent({...event,disposition:'FAILURE',reason:'No representable nodal change'});throw Error('No representable nodal change');}
  try{event.geometry=certifyRoundedPath(source,current,trial);}catch(error){onEvent({...event,disposition:'FAILURE',reason:'UNEXPECTED_GEOMETRY_FAILURE',message:error.message,materialEvaluated:false});throw error;}
  if(!event.geometry.certified){onEvent({...event,disposition:'REJECTED',reason:'UNSUPPORTED_WHOLE_PATH_GEOMETRY',materialEvaluated:false});continue;}
  // No catch/retry: material or numerical failure after a successful gate is fatal.
  let state;try{state=evaluate(trialCoordinates);}catch(error){onEvent({...event,disposition:'FAILURE',reason:'UNEXPECTED_FAILURE_AFTER_CERTIFICATION',message:error.message,materialEvaluated:true});throw error;}
  if(!Number.isFinite(state.energyJ)||(state.positions&&digest(state.positions)!==event.geometry.endSha256)){onEvent({...event,disposition:'FAILURE',reason:'NONFINITE_OR_MISMATCHED_CERTIFIED_MATERIAL_RESULT',materialEvaluated:true});throw Error('Invalid result after geometry certification');}
  const requiredEnergyJ=currentEnergyJ+1e-4*alpha*slope;
  if(state.energyJ<=requiredEnergyJ){onEvent({...event,disposition:'ACCEPTED',energyJ:state.energyJ,requiredEnergyJ,materialEvaluated:true});return {coordinates:trialCoordinates,state,alpha,slope,direction};}
  onEvent({...event,disposition:'REJECTED',reason:'SUFFICIENT_DECREASE',energyJ:state.energyJ,requiredEnergyJ,materialEvaluated:true});
 }
 throw Error('Exhausted21 fractions through2^-20 without admissible sufficient decrease');
}
