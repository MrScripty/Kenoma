import test from 'node:test';
import assert from 'node:assert/strict';
import {furtherQuadrature,prepareFurtherBody} from '../tools/anatomical-integration-refinement.mjs';
import {prepareCompressionBody,evaluateCompressionBody} from '../tools/anatomical-compression-quadrature.mjs';
import {MUSCLE_FIXTURE} from '../web/anatomical-material.mjs';
const vertices=[[0,0,0],[.03,0,0],[0,.02,0],[0,0,.01]],edges=[[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]],nodes=[...vertices,...edges.map(([i,j])=>vertices[i].map((v,k)=>(v+vertices[j][k])/2))],source={nodes_m:nodes,elements_ten_node:[[0,1,2,3,4,5,6,7,8,9]],reference_fibres:[[1,0,0]]},modes=nodes.map(()=>[]),near=(a,b,t)=>assert.ok(Math.abs(a-b)<t,`${a} vs ${b}`);
test('2048-point subdivision has positive weights and exact polynomial moments',()=>{
 const rule=furtherQuadrature();assert.equal(rule.length,2048);assert.ok(rule.every(p=>p.weight>0&&p.L.every(v=>v>0)));near(rule.reduce((s,p)=>s+p.weight,0),1,1e-12);
 near(rule.reduce((s,p)=>s+p.weight*p.L[0],0),1/4,1e-12);near(rule.reduce((s,p)=>s+p.weight*p.L[0]**2,0),1/10,1e-12);near(rule.reduce((s,p)=>s+p.weight*p.L[0]*p.L[1],0),1/20,1e-12);
});
test('further positive rule preserves reference volume and affine energy/full nodal forces',()=>{
 const positions=nodes.map(([x,y,z])=>[.85*x+.1*y,1.07*y,.98*z]),coarse=prepareCompressionBody(source,modes,2),fine=prepareFurtherBody(source,modes),A=evaluateCompressionBody(coarse,positions,.04,MUSCLE_FIXTURE),B=evaluateCompressionBody(fine,positions,.04,MUSCLE_FIXTURE);
 near(fine.referenceVolumeM3,.03*.02*.01/6,1e-18);near(A.energyJ,B.energyJ,1e-12);near(A.minimumJ,B.minimumJ,1e-12);A.nodalGradientN.flat().forEach((v,k)=>near(v,B.nodalGradientN.flat()[k],1e-10));
});
