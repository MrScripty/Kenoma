/** Research-only initialization. Acceptance still belongs to the mechanics solver. */
export function boundedAcceptedStatePredictor(snapshots,{hS}={}){
 if(!Array.isArray(snapshots)||!snapshots.length||!Number.isFinite(hS)||hS<=0)throw new RangeError('Accepted history and positive finite increment required');
 const current=snapshots.at(-1),previous=snapshots.at(-2);
 const validate=s=>{
  if(!Number.isFinite(s.timeS)||!Number.isInteger(s.step)||s.step<0||!Number.isFinite(s.massKg)||s.massKg<0||!s.coordinatesM?.length||!Array.from(s.coordinatesM).every(Number.isFinite))throw new RangeError('Finite accepted state required');
 };
 validate(current);
 const copy=reason=>({coordinatesM:Float64Array.from(current.coordinatesM),strategy:'accepted-state-copy',reason,historyS:null,extrapolationFraction:0,maximumCorrectionM:0});
 if(!previous)return copy('insufficient accepted history');
 validate(previous);
 if(previous.coordinatesM.length!==current.coordinatesM.length||current.step!==previous.step+1||!(current.timeS>previous.timeS))throw new RangeError('Consecutive accepted history required');
 if(current.massKg!==previous.massKg)return copy('mass discontinuity');
 const historyS=current.timeS-previous.timeS,extrapolationFraction=Math.min(hS/historyS,1);
 const coordinatesM=Float64Array.from(current.coordinatesM,(v,k)=>v+extrapolationFraction*(v-previous.coordinatesM[k]));
 if(!coordinatesM.every(Number.isFinite))throw new RangeError('Finite predictor coordinates required');
 return {coordinatesM,strategy:'bounded-accepted-state-secant',reason:'at most one previous accepted increment',historyS,extrapolationFraction,maximumCorrectionM:Math.max(...coordinatesM.map((v,k)=>Math.abs(v-current.coordinatesM[k])))};
}
