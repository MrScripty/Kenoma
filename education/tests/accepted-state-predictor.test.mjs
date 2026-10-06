import test from 'node:test';
import assert from 'node:assert/strict';
import {boundedAcceptedStatePredictor} from '../tools/accepted-state-predictor.mjs';
const old={timeS:.4,step:10,massKg:.5,coordinatesM:[1,2,3]},current={timeS:.5,step:11,massKg:.5,coordinatesM:[2,0,4]};
test('short prediction follows accepted secant without mutating history',()=>{
 const history=structuredClone([old,current]),saved=structuredClone(history);
 const p=boundedAcceptedStatePredictor(history,{hS:.05});
 assert.deepEqual(history,saved);assert.ok(p.coordinatesM instanceof Float64Array);
 for(const [v,w] of Array.from(p.coordinatesM).map((v,k)=>[v,[2.5,-1,4.5][k]]))assert.ok(Math.abs(v-w)<1e-14);
});
test('long target cannot extrapolate farther than one accepted increment',()=>{
 const p=boundedAcceptedStatePredictor([old,current],{hS:20});
 assert.deepEqual(Array.from(p.coordinatesM),[3,-2,5]);assert.equal(p.extrapolationFraction,1);
});
test('bootstrap and mass discontinuity copy the current accepted state',()=>{
 for(const history of [[current],[old,{...current,massKg:1}]]){
  const p=boundedAcceptedStatePredictor(history,{hS:.01});assert.equal(p.strategy,'accepted-state-copy');
  assert.deepEqual(Array.from(p.coordinatesM),current.coordinatesM);assert.notEqual(p.coordinatesM,current.coordinatesM);
 }
});
test('nonconsecutive or mismatched history is rejected rather than reused',()=>{
 for(const c of [{...current,step:12},{...current,timeS:.4},{...current,coordinatesM:[2,0]}])assert.throws(()=>boundedAcceptedStatePredictor([old,c],{hS:.01}),RangeError);
});
test('nonfinite states and invalid increments cannot become guesses',()=>{
 for(const hS of [0,-1,NaN,Infinity])assert.throws(()=>boundedAcceptedStatePredictor([old,current],{hS}),RangeError);
 assert.throws(()=>boundedAcceptedStatePredictor([old,{...current,coordinatesM:[NaN,0,4]}],{hS:.01}),RangeError);
 assert.throws(()=>boundedAcceptedStatePredictor([],{hS:.01}),RangeError);
});
test('overflowing extrapolated coordinates are rejected',()=>{
 assert.throws(()=>boundedAcceptedStatePredictor([{...old,coordinatesM:[-Number.MAX_VALUE]},{...current,coordinatesM:[Number.MAX_VALUE]}],{hS:.2}),RangeError);
});
