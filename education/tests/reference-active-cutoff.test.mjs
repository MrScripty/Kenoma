import test from 'node:test';import assert from 'node:assert/strict';import {activeReferenceDiagnostic} from '../tools/reference-active-diagnostic.mjs';import {MUSCLE_FIXTURE} from '../web/anatomical-material.mjs';
test('Passive lambda=1 cutoff has distinct centered and one-sided stress derivatives',()=>{
 const F=[1,0,0,0,1,0,0,0,1],f=[1,0,0],u=[Math.SQRT1_2,-Math.SQRT1_2,0],m=[Math.SQRT1_2,Math.SQRT1_2,0],D=F.map((_,i)=>u[Math.floor(i/3)]*m[i%3]),r=activeReferenceDiagnostic(F,f,0,MUSCLE_FIXTURE),Cd=r.P.map((_,i)=>D.reduce((s,v,j)=>s+r.C[9*i+j]*v,0)),norm=v=>Math.hypot(...v);
 for(const h of [1e-6,5e-7]){const p=activeReferenceDiagnostic(F.map((v,i)=>v+h*D[i]),f,0,MUSCLE_FIXTURE),q=activeReferenceDiagnostic(F.map((v,i)=>v-h*D[i]),f,0,MUSCLE_FIXTURE),center=p.P.map((v,i)=>(v-q.P[i])/(2*h)),left=r.P.map((v,i)=>(v-q.P[i])/h);assert.ok(p.lambda>1&&q.lambda<1);assert.ok(norm(center.map((v,i)=>v-Cd[i]))/norm(Cd)>1e-4);assert.ok(norm(left.map((v,i)=>v-Cd[i]))/norm(Cd)<1e-4);}
});
