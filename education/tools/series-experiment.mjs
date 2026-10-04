import {SERIES,seriesTrace,seriesInitial,seriesStep,seriesResults} from '../web/series.mjs';
import {TISSUE,tissueAt} from '../web/tissue.mjs';
const trajectories=[.01,.005,.0025].map(dt=>{const rows=seriesTrace({...SERIES,dt}),r=rows.at(-1);return {dt,steps:rows.length-1,angleDegrees:r.q*180/Math.PI,fiber:r.fiber,tendon:r.tendon,work:r.work,
 maxEnergyResidual:Math.max(...rows.map(x=>Math.abs(x.balanceResidual))),maxForceResidual:Math.max(...rows.map(x=>Math.abs(x.forceResidual))),eventSplits:r.eventSplits,substeps:r.substeps,halted:r.halted};});
const holds=['rigid','compliant'].map(tendon=>{const p={...SERIES,mode:'prescribed',angle:90,tendon},start=seriesInitial(p);let s=start;for(let n=0;n<60;n++)s=seriesStep(s,p);const r=seriesResults(s,p);return {tendon,activation:s.a,fiber:r.fiber,tendonLength:r.tendon,tendonEnergy:r.tendonEnergy,work:s.work};});
const compression=[30,60,90,120,135].map(degrees=>({degrees,...tissueAt(degrees*Math.PI/180)}));
console.log(JSON.stringify({model:'series-affine-tissue-v1',parameters:SERIES,tissue:TISSUE,units:'SI, angle radians unless labeled degrees',duration:.6,release:.3,trajectories,holds,compression},null,2));
