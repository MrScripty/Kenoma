import test from 'node:test';
import assert from 'node:assert/strict';
import {midpointNodes} from '../web/anatomical-element.mjs';
import {exactJacobianBernstein} from '../tools/anatomical-bernstein-orientation.mjs';
import {elementSegmentPolynomials,evaluateNumerator,certifyPrefix,locateCertifiedPrefix} from '../tools/isolated-segment-geometry.mjs';
const reference=midpointNodes([[0,0,0],[1,0,0],[0,1,0],[0,0,1]]),scale=(nodes,f)=>nodes.map(v=>v.map((x,d)=>x*f[d]));
test('known affine determinant path certifies a safe prefix and brackets the unchanged domain boundary',()=>{
 const polynomial=elementSegmentPolynomials(reference,reference,scale(reference,[-1,1,1]));
 assert.ok(certifyPrefix([polynomial],1n,4n).certified);assert.equal(certifyPrefix([polynomial],1n,1n).certified,false);
 const bracket=locateCertifiedPrefix([polynomial]);const lower=Number(bracket.lowerNumerator)/Number(bracket.denominator),upper=Number(bracket.upperNumerator)/Number(bracket.denominator),boundary=(1-1e-6)/2;
 assert.ok(lower<boundary&&upper>=boundary&&upper-lower<=2**-40);
 for(const row of polynomial.coefficients)assert.equal(evaluateNumerator(row.currentPowerNumerators,1n,2n),0n);
});
test('orientation-positive endpoints can contain an inverted path interior',()=>{
 const end=scale(reference,[-2,-.5,1]);assert.ok(exactJacobianBernstein(reference).allStrictlyPositive);assert.ok(exactJacobianBernstein(end).allStrictlyPositive);
 const polynomial=elementSegmentPolynomials(reference,reference,end);
 assert.ok(certifyPrefix([polynomial],1n,4n).certified);assert.equal(certifyPrefix([polynomial],1n,1n).certified,false);
 for(const row of polynomial.coefficients)assert.ok(evaluateNumerator(row.currentPowerNumerators,1n,2n)<0n);
});
test('the curved P2 segment polynomial endpoints agree with the original exact spatial compiler',()=>{
 const end=scale(reference,[1.1,.93,1.02]);end[4][1]+=.0625;end[8][0]-=.03125;
 const polynomial=elementSegmentPolynomials(reference,reference,end),atEnd=exactJacobianBernstein(end),atStart=exactJacobianBernstein(reference),common=Math.max(polynomial.denominatorPowerOfTwo,atEnd.denominatorPowerOfTwo,atStart.denominatorPowerOfTwo);
 for(const row of polynomial.coefficients){
  const matching=c=>c.coefficients.find(r=>r.multiIndex.join(',')===row.multiIndex.join(',')),shift=BigInt(common-polynomial.denominatorPowerOfTwo);
  assert.equal(evaluateNumerator(row.currentPowerNumerators,0n,1n)<<shift,BigInt(matching(atStart).numerator)<<BigInt(common-atStart.denominatorPowerOfTwo));
  assert.equal(evaluateNumerator(row.currentPowerNumerators,1n,1n)<<shift,BigInt(matching(atEnd).numerator)<<BigInt(common-atEnd.denominatorPowerOfTwo));
 }
});
