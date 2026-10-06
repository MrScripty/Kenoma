import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {lab,out,root} from '../tools/run_vertical_force_cases.js';
const checks=[];
for(const [m,f] of [[0,5],[-1,5],[NaN,5],[Infinity,5],[.5,-1],[.5,NaN],[.5,Infinity],[.01,5],[11,5],[.5,151]])assert.throws(()=>lab.validate(m,f));
for(const dt of [0,-1,NaN,Infinity])assert.throws(()=>lab.run(lab.init(),dt));
checks.push('Reject finite/range violations and invalid integration steps');
const cfg=lab.init(),before=JSON.stringify(cfg),z=cfg.z.slice();z[3]=.4;
assert.throws(()=>lab.trialStep(0,z,.0001,cfg,{target:cfg.target}));assert.equal(JSON.stringify(cfg),before);checks.push('Invalid fiber stage returns no next state and retains initialization');
for(const [index,value,code] of [[0,cfg.L0-.1*cfg.z[3]-.199,'slack'],[2,1.01,'activation-bound'],[1,NaN,'nonfinite']]){const bad=cfg.z.slice();bad[index]=value;assert.throws(()=>lab.trialStep(0,bad,.0001,cfg,{target:cfg.target}),e=>e.code===code);assert.equal(JSON.stringify(cfg),before);}checks.push('Slack, activation-bound and nonfinite stages cannot return or advance a state');
const baseline=lab.run(cfg);assert.equal(baseline.failure,null);assert(Math.abs(baseline.motion.velocity)<1e-8);assert(!baseline.events.some(e=>e.type==='brake-crossing'));checks.push('Stationary baseline is not an initial-zero brake');
const pulse=lab.run(lab.init('pulse',.5,1.2*.5*9.80665));const brake=pulse.events.find(e=>e.type==='brake-crossing');assert(brake?.armed);assert(brake.bracket[1]-brake.bracket[0]<=lab.P.event_root_time_s);assert(pulse.history.some(r=>r.t>=.15&&r.t<brake.t&&r.z[1]>lab.P.brake_arm_velocity_m_per_s));checks.push('Brake requires prior signed motion and bounded directed-root localization');
for(const [name,m,target] of [['high',.5,120],['mass',1,5]]){const r=lab.run(lab.init(name,m,target));assert.equal(r.failure.code,'antiwindup-surface');assert.deepEqual(r.history.at(-1).z,r.failure.acceptedState);assert.equal(r.history.at(-1).t,r.failure.acceptedTime);assert(r.failure.failedStageTime>=r.acceptedTime);assert(r.failure.failedStageState);}checks.push('Opposing switching trials preserve accepted state and separately save rejected stage');
let valueError=0,derivativeError=0;const lines=fs.readFileSync(path.join(root,'education/data/millard-reference-v1/review/native-kernels.csv'),'utf8').trim().split('\n').slice(1);
for(const line of lines){const [name,x,value,derivative]=line.split(',');valueError=Math.max(valueError,Math.abs(lab.C[name].value(+x)-(+value)));derivativeError=Math.max(derivativeError,Math.abs(lab.C[name].value(+x,true)-(+derivative)));}
assert(valueError<=lab.P.budgets.curve_value);assert(derivativeError<=lab.P.budgets.curve_derivative);checks.push('JS source curves match native control values and derivatives');
fs.writeFileSync(path.join(out,'model-tests.json'),JSON.stringify({passed:true,checks,curveValueError:valueError,curveDerivativeError:derivativeError},null,2)+'\n');console.log(checks.join('\n'));
