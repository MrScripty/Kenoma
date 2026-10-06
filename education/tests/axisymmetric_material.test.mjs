import test from 'node:test';
import assert from 'node:assert/strict';
import {axisymmetricMaterial,uniformCylinderOracle,PASSIVE_MATERIAL} from '../web/axisymmetric-material.mjs';
const close=(a,b,atol=1e-7,rtol=1e-7)=>assert.ok(Math.abs(a-b)<=atol+rtol*Math.max(Math.abs(a),Math.abs(b)),`${a} != ${b}`);
test('reference material is stress free with finite bulk compliance',()=>{
 const m=axisymmetricMaterial([1,0,0,1,1]);close(m.J,1,0,0);close(m.energyPa,0,0,0);
 m.gradient.forEach(x=>close(x,0));Object.values(m.cauchy).forEach(x=>close(x,0));
});
test('independent tensor stress, mean stress and symmetric tangent agree at shear and dilation',()=>{
 for(const v of [[1.08,.03,-.02,.96,1.01],[.92,-.06,.04,1.06,.98],[1.02,.1,.1,.97,1.03]]){
  const m=axisymmetricMaterial(v),[a,b,c,d,h]=v,fac=PASSIVE_MATERIAL.mu*m.J**(-5/3),q=PASSIVE_MATERIAL.bulk*Math.log(m.J)/m.J;
  close(m.cauchy.rr,fac*(a*a+b*b-m.I1/3)+q);
  close(m.cauchy.zz,fac*(c*c+d*d-m.I1/3)+q);
  close(m.cauchy.rz,fac*(a*c+b*d));close(m.cauchy.zr,m.cauchy.rz);
  close(m.cauchy.hoop,fac*(h*h-m.I1/3)+q);
  close((m.cauchy.rr+m.cauchy.zz+m.cauchy.hoop)/3,q);
  for(let i=0;i<5;i++)for(let j=0;j<5;j++)close(m.tangent[i][j],m.tangent[j][i]);
 }
});
test('energy forces and analytic tangent pass separate centered differences at two scales',()=>{
 const v=[1.07,.031,-.021,.965,1.01],m=axisymmetricMaterial(v);
 for(const step of [2e-5,1e-5])for(let i=0;i<5;i++){
  const p=v.slice(),n=v.slice();p[i]+=step;n[i]-=step;const mp=axisymmetricMaterial(p),mn=axisymmetricMaterial(n);
  close(m.gradient[i],(mp.energyPa-mn.energyPa)/(2*step),2e-5,2e-7);
  for(let j=0;j<5;j++)close(m.tangent[j][i],(mp.gradient[j]-mn.gradient[j])/(2*step),1e-4,2e-7);
 }
});
test('uniform free-lateral oracle solves finite-volume response at zero and signed ten percent',()=>{
 for(const lambda of [.9,1,1.1]){
  const o=uniformCylinderOracle(lambda),m=axisymmetricMaterial([o.b,0,0,lambda,o.b]);
  close(m.cauchy.rr,0,2e-10);close(m.cauchy.hoop,0,2e-10);close(m.J,o.J,1e-14);
  close(m.gradient[3],o.nominalAxialPa,1e-9);close(m.energyPa,o.energyDensityPa,1e-10);
  if(lambda===1){assert.equal(o.J,1);assert.equal(o.b,1);}
  else assert.ok(Math.abs(o.J-1)>1e-4,'Finite volume compliance must remain measurable');
 }
});
test('invalid material orientation and unsupported oracle domain fail explicitly',()=>{
 for(const v of [[1,0,0,0,1],[1,0,0,1,-1],[NaN,0,0,1,1]])assert.throws(()=>axisymmetricMaterial(v),RangeError);
 assert.throws(()=>uniformCylinderOracle(.8),RangeError);
});
