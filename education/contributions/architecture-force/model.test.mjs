import test from 'node:test';
import assert from 'node:assert/strict';
import {materialCut,aggregateTypes,forceFromArea,taperedSeries,lateralExchange,forceLength} from './model.mjs';
const close=(a,b,eps=1e-11)=>assert.ok(Math.abs(a-b)<=eps*Math.max(1,Math.abs(a),Math.abs(b)),`${a} != ${b}`);
test('shortening thickens a material cut without adding force at fixed nominal stress',()=>{
 const base={referenceAreaM2:8e-5,J:1,nominalStressPa:3e5,cosPennation:Math.cos(Math.PI/6)};
 const rest=materialCut({...base,lambda:1}),short=materialCut({...base,lambda:.8});
 close(short.projectedCurrentAreaM2,1e-4);close(short.cauchyFiberStressPa,240000);
 close(short.axialForceN,24);close(rest.axialForceN,short.axialForceN);close(short.fromCurrentCutN,24);
 close(short.tendonDirectedForceN,24*Math.cos(Math.PI/6));
});
test('positive stretch and volume transformations retain force over a bounded grid',()=>{
 for(const lambda of [.6,.8,1,1.2,1.4])for(const J of [.8,1,1.1])for(const P of [0,1e5,3e5]){
  const r=materialCut({referenceAreaM2:1e-4,lambda,J,nominalStressPa:P});close(r.axialForceN,r.fromCurrentCutN);
 }
});
test('count fractions differ from area fractions for different fibre sizes',()=>{
 const r=aggregateTypes([{count:50000,referenceFiberAreaM2:1e-9,nominalStressPa:1e5},{count:50000,referenceFiberAreaM2:2e-9,nominalStressPa:3e5}]);
 close(r.totalCount,100000);close(r.totalAreaM2,1.5e-4);close(r.axialForceN,35);
 close(r.rows[0].countFraction,.5);close(r.rows[0].areaFraction,1/3);close(r.areaWeightedNominalStressPa,700000/3);
 assert.notEqual(r.axialForceN,r.totalAreaM2*200000);
});
test('pennation is projected once under either declared PCSA convention',()=>{
 const c=.8,A=1e-4,S=3e5;
 const common={stressPa:S,cosPennation:c,stressBasis:'whole-muscle-effective'};
 close(forceFromArea({...common,areaM2:A,areaConvention:'fiber-normal'}),24);
 close(forceFromArea({...common,areaM2:A*c,areaConvention:'tendon-projected'}),24);
 assert.notEqual(S*A*c*c,24);
});
test('packing is applied once and requires a declared stress basis',()=>{
 close(forceFromArea({areaM2:1e-4,stressPa:3e5,areaConvention:'fiber-normal',stressBasis:'contractile',packingFraction:.8}),24);
 assert.throws(()=>forceFromArea({areaM2:1e-4,stressPa:3e5,areaConvention:'fiber-normal',stressBasis:'whole-muscle-effective',packingFraction:.8}),RangeError);
});
test('a no-side-load tapered series has constant force and unequal stresses',()=>{
 const r=taperedSeries([1e-4,2e-4,1e-4],30);
 assert.deepEqual(r.map(x=>x.forceN),[30,30,30]);close(r[0].nominalStressPa,3e5);close(r[1].nominalStressPa,1.5e5);
});
test('constant stress through unequal series cuts requires lateral exchange',()=>{
 const r=lateralExchange(30,[-30,30]);close(r[0].rightForceN,60);close(r[1].rightForceN,30);
 for(const cell of r)close(cell.balanceN,0);close(r.reduce((s,x)=>s+x.lateralForceN,0),0);
});
test('fibre groups add projected forces rather than using an average angle',()=>{
 const r=aggregateTypes([{count:1,referenceFiberAreaM2:1e-4,nominalStressPa:3e5,cosPennation:1},{count:1,referenceFiberAreaM2:1e-4,nominalStressPa:1e5,cosPennation:.5}]);close(r.tendonDirectedForceN,35);
});
test('force length variation is an explicit constitutive multiplier',()=>{
 close(forceLength(1),1);close(forceLength(.8),.7056);close(forceLength(.5),0);close(forceLength(1.5),0);
});
test('inadmissible and nonfinite input cannot become a physiological result',()=>{
 for(const key of ['referenceAreaM2','lambda','J'])for(const value of [0,-1,NaN,Infinity])assert.throws(()=>materialCut({referenceAreaM2:1e-4,lambda:1,J:1,nominalStressPa:3e5,[key]:value}),RangeError);
 assert.throws(()=>aggregateTypes([]),RangeError);assert.throws(()=>aggregateTypes([{count:0,referenceFiberAreaM2:1e-9,nominalStressPa:1}]),RangeError);
 assert.throws(()=>lateralExchange(10,[11]),RangeError);assert.throws(()=>forceFromArea({areaM2:1,stressPa:1,areaConvention:'unknown',stressBasis:'contractile'}),RangeError);
});
