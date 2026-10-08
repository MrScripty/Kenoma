import test from 'node:test';
import assert from 'node:assert/strict';
import {DEFAULTS,field,mapPoint,state,determinant} from './model.mjs';
const close=(a,b,tolerance=1e-11)=>assert.ok(Math.abs(a-b)<tolerance,`${a} versus ${b}`);
function numericalGradient(point,p){
  const h=1e-7,columns=[0,1,2].map(i=>{
    const a=[...point],b=[...point];a[i]+=h;b[i]-=h;
    return mapPoint(a,p).map((x,j)=>(x-mapPoint(b,p)[j])/(2*h));
  });
  return [0,1,2].map(i=>columns.map(c=>c[i]));
}
test('actual mapped coordinates independently establish local compensation and full gradient',()=>{
  for(const mean of [.6,1,1.4])for(const gradient of [-.6,0,.6])for(const fraction of [.1,.5,.9]){
    const p={...DEFAULTS,mean,gradient},point=[fraction*p.length,p.radius*.7,-p.radius*.3];
    const numerical=numericalGradient(point,p),analytic=field(point[0],p,point[1],point[2]);
    close(determinant(numerical),1,1e-7);
    for(let i=0;i<3;i++)for(let j=0;j<3;j++)close(numerical[i][j],analytic.F[i][j],1e-7);
  }
});
test('triangulated boundary volume agrees with an independent polygon/frustum route',()=>{
  for(const sides of [8,16,32])for(const cells of [8,32,128])for(const compensate of [true,false]){
    const s=state({...DEFAULTS,sides,cells,compensate});
    close(s.referenceMeasurementError,0,1e-17);close(s.independentMeshMeasurementError,0,1e-17);
    assert.ok(s.meshVolume>0&&s.rows.every(r=>r.cellVolumeRatio>0));
  }
});
test('nonuniform compensated straight mesh has measurable error and converges at second order',()=>{
  const errors=[8,16,32,64].map(cells=>Math.abs(state({...DEFAULTS,cells}).relativeMeshVolumeError));
  assert.ok(errors.every(e=>e>1e-10));
  for(let i=1;i<errors.length;i++)assert.ok(errors[i]<errors[i-1]/3.8);
});
test('same total volume can conceal nonunit local Jacobians and uneven strain',()=>{
  const s=state({...DEFAULTS,compensate:false});close(s.meshVolumeRatio,1);
  assert.ok(s.pointwiseJRange[0]<.7&&s.pointwiseJRange[1]>1.3);
  assert.ok(s.centerlineStrainRange[0]<0&&s.centerlineStrainRange[1]>0);
  assert.ok(s.rows[0].cellVolumeRatio<.7&&s.rows.at(-1).cellVolumeRatio>1.3);
});
test('reported extrema include actual endpoints rather than only display midpoints',()=>{
  const s=state({...DEFAULTS,compensate:false,cells:8});
  close(s.pointwiseJRange[0],.6);close(s.pointwiseJRange[1],1.4);
  close(s.centerlineStrainRange[0],-.4);close(s.centerlineStrainRange[1],.4);
  assert.ok(s.rows[0].J>s.pointwiseJRange[0]&&s.rows.at(-1).J<s.pointwiseJRange[1]);
});
test('uniform compensated construction is exactly represented by the straight mesh',()=>{
  for(const mean of [.6,1.4]){const s=state({...DEFAULTS,mean,gradient:0});close(s.meshVolumeRatio,1);close(s.relativeMeshVolumeError,0);}
});
test('invalid controls are rejected before any geometry is produced',()=>{
  for(const p of [{mean:NaN},{mean:0},{gradient:1},{cells:3},{radius:0},{compensate:'yes'}])assert.throws(()=>state({...DEFAULTS,...p}));
});
