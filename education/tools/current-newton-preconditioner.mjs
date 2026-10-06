/** Research preconditioner only: never changes the Hessian-vector operator,
 * Newton shift policy, material, geometry or acceptance criteria. */
import {denseReferencePreconditioner} from '../web/anatomical-preconditioner.mjs';
export function currentNewtonPreconditioner(matrix,referencePrecondition){
 const current=denseReferencePreconditioner(matrix),rejected=new Set(),stats={currentApplications:0,referenceApplications:0,rejectedSPDShiftsNPerM:[]};
 const precondition=(v,shift=0)=>{
  if(!rejected.has(shift))try{const result=current(v,shift);stats.currentApplications++;return result;}catch(error){
   if(!(error instanceof RangeError)||error.message!=='Reference preconditioner is not positive definite')throw error;
   rejected.add(shift);stats.rejectedSPDShiftsNPerM.push(shift);
  }
  stats.referenceApplications++;return referencePrecondition(v,shift);
 };
 return {precondition,stats};
}
