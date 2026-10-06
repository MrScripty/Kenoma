import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {ELBOW,elbowInitial,elbowResults,elbowStep} from '../web/elbow.mjs';
import {SERIES,seriesInitial,seriesResults,seriesStep} from '../web/series.mjs';
import {pulseDue} from '../web/pulse.mjs';

// Exercise the actual DOM-facing update method without constructing WebGL.
const source=readFileSync(new URL('../web/app.mjs',import.meta.url),'utf8');
const body=source.match(/  update\(\)\{([\s\S]*?)\n  \}\n  plot\(\)/)[1];
const dom={createElement:()=>({append(){},textContent:''})};
const update=new Function('fmt','document','return function(){'+body+'}')((v,d=3)=>v.toFixed(d),dom);
const stepBody=source.match(/  step\(\)\{([\s\S]*?)\n  \}\n  update\(\)/)[1];
const step=new Function('seriesStep','elbowStep','pulseDue','return function(){'+stepBody+'}')(seriesStep,elbowStep,pulseDue);
for(const kind of ['elbow','series'])test(`${kind} current row matches release/change before stepping and preserves completed history`,()=>{
 const params={...(kind==='series'?SERIES:ELBOW),mode:'prescribed',angle:90};
 const initialFn=kind==='series'?seriesInitial:elbowInitial,resultFn=kind==='series'?seriesResults:elbowResults,stepFn=kind==='series'?seriesStep:elbowStep;
 const lab={kind,articulated:true,params,state:initialFn(params),index:0,history:[],resultFn,
  root:{querySelector:()=>({hidden:false})},readout:{replaceChildren(){}},draw(){},sync(){},pause(){}};
 lab.update=()=>update.call(lab);
 lab.initialEnergy=resultFn(lab.state,params).energy;update.call(lab);
 for(let i=0;i<60;i++){lab.state=stepFn(lab.state,params);lab.index++;update.call(lab);}
 const completed=structuredClone(lab.history.slice(0,-1)),state=structuredClone(lab.state);
 lab.params.excitation=0;update.call(lab);let row=lab.history.at(-1);
 assert.equal(lab.history.length,61);assert.equal(row.excitation,0);assert.deepEqual(lab.state,state);
 assert.deepEqual(lab.history.slice(0,-1),completed);assert.equal(row.work,state.work);assert.equal(row.time,state.time);
 if(kind==='series'){assert.ok(row.fiberSpeed>0);assert.ok(row.activePower<0);}
 lab.params.excitation=.8;update.call(lab);row=lab.history.at(-1);
 assert.equal(row.excitation,.8);assert.equal(lab.history.length,61);assert.deepEqual(lab.state,state);
 assert.deepEqual(lab.history.slice(0,-1),completed);
 if(kind==='series'){assert.ok(row.fiberSpeed<0);assert.ok(row.activePower>0);}
 // Automatic pulse changes the outgoing row at its boundary before integrating.
 lab.pulse={releaseTime:state.time};step.call(lab);
 assert.equal(lab.history.length,62);assert.equal(lab.history[60].excitation,0);
 assert.equal(lab.history[60].work,state.work);assert.equal(lab.history[60].time,state.time);
 assert.equal(lab.history[61].excitation,0);assert.ok(lab.state.a<state.a);
 assert.deepEqual(lab.history.slice(0,60),completed);
});
