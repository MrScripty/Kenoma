import {ELBOW,elbowTrace} from '../web/elbow.mjs';
const rows=[0.01,0.005,0.0025].map(dt=>{
 const trace=elbowTrace({...ELBOW,dt}),last=trace.at(-1);
 return {dt,steps:trace.length-1,finalAngleDegrees:last.q*180/Math.PI,finalActivation:last.a,activeWork:last.work,
 maxBalanceResidual:Math.max(...trace.map(s=>Math.abs(s.balanceResidual))),halted:last.halted};
});
console.log(JSON.stringify({model:'schematic-elbow-v1',input:ELBOW,duration:0.6,release:0.3,units:'SI, displayed angle degrees',rows},null,2));
