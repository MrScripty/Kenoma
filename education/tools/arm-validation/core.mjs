/** Pure accounting/serialization/observation contracts. No physical imports. */
import {createHash} from 'node:crypto';
export const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
export class BudgetExceeded extends Error {
  constructor(kind, details) {super(`Budget exceeded: ${kind}`); this.name='BudgetExceeded'; this.kind=kind; this.details=details;}
}
export function json(value) {
  return JSON.stringify(value, (_k,v)=>{
    if(typeof v==='number'&&!Number.isFinite(v))throw new Error('Nonfinite output');
    if(ArrayBuffer.isView(v))return Array.from(v);
    if(v instanceof Map)return [...v];
    if(typeof v==='function')throw new Error('Function/physical result is not a serializable receipt');
    return v;
  });
}
export const detached = value => JSON.parse(json(value));
export class Budget {
  constructor(limits, check=()=>{}) {this.limits={...limits};this.counts=Object.fromEntries(Object.keys(limits).map(k=>[k,0]));this.denied={};this.latch=null;this.check=check;this.attemptProducts=0;}
  alive(){if(this.latch)throw this.latch;this.check();if(this.latch)throw this.latch;}
  refuse(kind,details){this.latch??=new BudgetExceeded(kind,details);throw this.latch;}
  charge(kind,n=1){
    this.alive();if(!Number.isSafeInteger(n)||n<0||!Object.hasOwn(this.limits,kind))throw new Error('Invalid accounting class');
    if(this.counts[kind]+n>this.limits[kind]){this.denied[kind]=(this.denied[kind]||0)+n;this.refuse(kind,{executed:this.counts[kind],denied:n,limit:this.limits[kind]});}
    if(kind==='hessianProducts'&&this.attemptProducts+n>3528840){this.denied[kind]=(this.denied[kind]||0)+n;this.refuse('perAttemptHessianProducts',{executed:this.attemptProducts,denied:n});}
    this.counts[kind]+=n;if(kind==='hessianProducts')this.attemptProducts+=n;
  }
  beginAttempt(){this.charge('attempts');this.attemptProducts=0;}
  snapshot(){return {executed:{...this.counts},denied:{...this.denied},latched:this.latch?{kind:this.latch.kind,details:this.latch.details}:null};}
}
function once(source,needle,replacement){if(source.split(needle).length!==2)throw new Error('Instrumentation cardinality: '+needle);return source.replace(needle,replacement);}
export function instrument(path,source){
  let text=source;const g='globalThis.__kenomaValidation';
  if(path==='education/web/anatomical-arm.mjs'){
    text=once(text,'function configuration(arm,x,a,{hessian=true}={}){',`function configuration(arm,x,a,{hessian=true}={}){${g}.budget.charge('configurationEntries');`);
    text=once(text,'function attemptAnatomicalArmStep(', 'function unobservedAnatomicalArmStep(');
    text+=`\nfunction attemptAnatomicalArmStep(arm,state,options={}){return ${g}.attempt(arm,state,options,unobservedAnatomicalArmStep);}\n`;
  }
  if(path==='education/web/anatomical-material.mjs')for(const [name,kind,prefix] of [
    ['muscleMaterial','muscleMaterial','export function muscleMaterial(F,f0,a,p=MUSCLE_FIXTURE){'],
    ['tendonMaterial','tendonMaterial','export function tendonMaterial(epsilon,p=TENDON_FIXTURE){']]){
      text=once(text,prefix,prefix+`${g}.budget.charge('${kind}');`);
  }
  if(path==='education/web/anatomical-modal.mjs')text=once(text,'export function materialTensor(F,fibre,activation,p=MUSCLE_FIXTURE){',`export function materialTensor(F,fibre,activation,p=MUSCLE_FIXTURE){${g}.budget.charge('materialTensor');`);
  if(path==='education/web/anatomical-newton.mjs'){
    if(text.split('hessianProducts++;').length!==3)throw new Error('Hessian-product instrumentation cardinality');
    text=text.replaceAll('hessianProducts++;',`${g}.budget.charge('hessianProducts');hessianProducts++;`);
  }
  return text;
}
export function createObserver(budget, emit, byteLimit=4194304){
  let records=[],current=null,sequence=0,retainedBytes=0;
  const save=(record)=>{const copy=detached(record),size=Buffer.byteLength(json(copy));if(retainedBytes+size>byteLimit)budget.refuse('observationBytes',{retainedBytes,size,limit:byteLimit});retainedBytes+=size;records.push(copy);};
  return {
    budget,
    attempt(arm,state,options,original){
      budget.beginAttempt();const id=budget.counts.attempts,old=detached(state),h=options.h??arm.parameters.stepS,effort=options.effort??state.effort;current=id;
      try{
        const result=original(arm,state,options);budget.alive();
        save({attempt:id,status:'PROVISIONAL_NOT_COMMITTED',hS:h,effort,accepted:result.accepted,
          ...(result.accepted?{oldState:old,state:detached(result.state),receipt:detached(result.receipt)}:{reason:result.reason??null,residualN:result.maxGradientN??null})});
        return result;
      }finally{current=null;}
    },
    progress(row){budget.alive();const event={kind:'progress',status:'PROVISIONAL_NOT_COMMITTED',attempt:current,sequence:++sequence,iteration:row.iteration,residualN:row.maxGradient};emit(detached(event));},
    records:()=>detached(records),
    select(result){budget.alive();if(!result.accepted)return [];const expected=result.substepIntegration?.receipts?.map(r=>r.receipt)??[result.receipt];const rows=records.filter(r=>r.accepted).slice(-expected.length);
      if(rows.length!==expected.length||rows.some((r,i)=>json(r.receipt)!==json(expected[i])))throw Error('Accepted leaf coverage mismatch');return detached(rows);
    },
    dispose(){records=[];current=null;},
  };
}
export async function transaction({state,capture,restore,operation,budget}){
  const before=detached(state),rule=capture();
  try{const result=await operation();budget.alive();if(result.accepted)return detached(result);restore(rule);return {...detached(result),state:before};}
  catch(error){restore(rule);return {accepted:false,state:before,status:budget.latch?'RESOURCE_INCONCLUSIVE':'EXCEPTION',error:String(error)};}
}
export const observationStatus=Object.freeze({progress:'PROVISIONAL_NOT_COMMITTED',contactAliases:'UNTRUSTED_PROCESS_LOCAL_ALIASES_DISPOSED',finalSnapshot:'DETACHED_SUPERVISOR_RECEIPT_ONLY',externalCallbacks:'Harness owns the callback; no arbitrary external callback or coordinate alias is exposed.'});
export function compareRuns(B,C,D){
  if(B.status==='PASS'&&C.status==='PASS'){
    if(C.leaves.length!==1||json(B.finalState)!==json(C.finalState)||json(B.leaves.map(r=>r.receipt))!==json(C.leaves.map(r=>r.receipt)))throw Error('Default whole-step compatibility mismatch');
    return {result:'CONTROL_COMPATIBLE_REMEDY_UNPROVEN',explicitHalvesDifferFromWhole:json(B.finalState)!==json(D.finalState)};
  }
  if(B.status==='SOLVER_REFUSAL'&&C.status==='PASS'){
    if(C.leaves.length!==2||D.status!=='PASS'||json(C.finalState)!==json(D.finalState)||json(C.leaves.map(r=>r.receipt))!==json(D.leaves.map(r=>r.receipt)))throw Error('Half-step recovery reproduction mismatch');
    return {result:'RECOVERY_SUPPORTED_FOR_THIS_REDUCED_INTERVAL_ONLY'};
  }
  if(C.status==='SOLVER_REFUSAL'&&D.status==='SOLVER_REFUSAL')return {result:'DEPTH_ONE_RECOVERY_REFUSED_FOR_THIS_INTERVAL'};
  throw Error('Inconsistent completed control/half-step outcomes');
}
