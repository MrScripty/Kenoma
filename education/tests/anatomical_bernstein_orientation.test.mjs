import test from 'node:test';
import assert from 'node:assert/strict';
import {quadraticShape} from '../web/anatomical-element.mjs';
import {determinant} from '../web/anatomical-material.mjs';
import {exactJacobianBernstein,exactElementOrientation} from '../tools/anatomical-bernstein-orientation.mjs';
const vertices=[[0,0,0],[1,0,0],[0,1,0],[0,0,1]],edges=[[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]],nodes=[...vertices,...edges.map(([i,j])=>vertices[i].map((v,d)=>(v+vertices[j][d])/2))];
test('Exact P2 Bernstein coefficients certify affine orientation and detect reversal',()=>{
 const r=exactJacobianBernstein(nodes);assert.equal(r.coefficients.length,20);assert(r.allStrictlyPositive);for(const c of r.coefficients)assert.equal(Number(BigInt(c.numerator))/6*2**(-r.denominatorPowerOfTwo),1);
 assert(exactElementOrientation(nodes,nodes.map(X=>X.map(v=>v*2))).orientationCertified);
 assert(!exactElementOrientation(nodes,nodes.map(X=>[-X[0],X[1],X[2]])).orientationCertified);
});
test('Cubic Bernstein reconstruction agrees with an independent curved P2 Jacobian',()=>{
 const curved=nodes.map((X,i)=>X.map((v,d)=>v+(i===4&&d===0?.125:i===7&&d===1?-.0625:0))),r=exactJacobianBernstein(curved),L=[.125,.25,.375,.25],g=quadraticShape(L).gradient,J=Array.from({length:9},(_,k)=>curved.reduce((s,X,i)=>s+X[Math.floor(k/3)]*g[i][k%3],0)),factorial=n=>[1,1,2,6][n];
 const reconstructed=r.coefficients.reduce((s,c)=>s+Number(BigInt(c.numerator))/6*2**(-r.denominatorPowerOfTwo)*6/c.multiIndex.reduce((p,a)=>p*factorial(a),1)*c.multiIndex.reduce((p,a,i)=>p*L[i]**a,1),0);
 assert.equal(reconstructed,determinant(J));
});
test('An unresolved or inverted curved element cannot receive a positive certificate',()=>{
 const folded=nodes.map((X,i)=>X.map((v,d)=>v+(i===4&&d===0?1:0)));assert.equal(exactJacobianBernstein(folded).allStrictlyPositive,false);
 assert.throws(()=>exactJacobianBernstein(nodes.map((X,i)=>i===0?[NaN,0,0]:X)),/Finite/);
});
test('Exact signs survive determinant underflow and signed zero in the stored coordinates',()=>{
 const scale=2**-400,tiny=nodes.map(X=>X.map(v=>v===0?-0:v*scale));
 assert.equal(scale**3,0);const r=exactJacobianBernstein(tiny);assert(r.allStrictlyPositive);assert(BigInt(r.minimumNumerator)>0n);
 assert(!exactJacobianBernstein(tiny.map(X=>[-X[0],X[1],X[2]])).allStrictlyPositive);
});
