import {DEFAULTS,springTrace,exactSpring} from '../web/mechanics.mjs';
const rows=[];
for(const method of ['explicit','symplectic','verlet'])for(const dt of [0.01,0.02,0.05]) {
 const p={...DEFAULTS.energy,method,dt};
 const trace=springTrace(p,Math.round(12/dt)),e0=trace[0].energy,end=trace.at(-1);
 rows.push({method,dt,steps:trace.length-1,time:end.time,initial_energy:e0,final_energy:end.energy,
   max_relative_energy_error:Math.max(...trace.map(s=>Math.abs(s.energy/e0-1))),
   final_position_error:Math.abs(end.x-exactSpring(end.time,p).x)});
}
console.log(JSON.stringify({schema:1,kind:'original synthetic numerical experiment',units:{dt:'s',time:'s',energy:'J',position_error:'m'},initial:{mass:1,stiffness:40,x:0.2,v:0},duration:12,rows},null,2));
