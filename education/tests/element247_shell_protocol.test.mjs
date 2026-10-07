import test from 'node:test';import assert from 'node:assert/strict';
import {shells,assertCoverage,shellMap,shellRule,SHELL_RECIPES,SHELL_BUDGET,exactShellMoment,rationalNumber,assertMoments,compareShellVectors,shellComparisonPass} from '../tools/element247-shell-protocol.mjs';
const zeros=()=>Array.from({length:10},()=>[0,0,0]);
test('whole-element geometric coverage includes every outer shell and the corner core',()=>{
 const rows=shells(20);assert.equal(rows.length,21);assertCoverage(rows);assert.equal(rows.reduce((s,x)=>s+x.hi**3-x.lo**3,0),1);
 assert.throws(()=>assertCoverage(rows.slice(1)),/outer/);assert.throws(()=>assertCoverage(rows.slice(0,-1)),/core/);
 assert.throws(()=>assertCoverage([rows[0],rows[0],...rows.slice(1)]),/duplicate/);
 const gap=structuredClone(rows);gap[4].hi/=2;assert.throws(()=>assertCoverage(gap),/Gap|Invalid/);
 const overlap=structuredClone(rows);overlap[4].hi*=2;assert.throws(()=>assertCoverage(overlap),/overlap/);
 assert.throws(()=>shells(23),/Bounded/);
});
test('radial-face chart Jacobian matches an independent derivative determinant',()=>{
 const r=.3,a=.4,b=.7,m=shellMap(r,a,b),dr=[a,(1-a)*b,(1-a)*(1-b)],da=[r,-r*b,-r*(1-b)],db=[0,r*(1-a),-r*(1-a)];
 const det=dr[0]*(da[1]*db[2]-da[2]*db[1])-da[0]*(dr[1]*db[2]-dr[2]*db[1])+db[0]*(dr[1]*da[2]-dr[2]*da[1]);
 assert.ok(Math.abs(Math.abs(det)-m.jacobian)<1e-16);assert.equal(m.L.reduce((s,x)=>s+x,0),1);
 assert.throws(()=>shellMap(r,a,b,[1,1,3]),/permutation/);assert.throws(()=>shellMap(0,a,b),/Interior/);
});
test('analytic dyadic shell moments agree with known whole-tetrahedron moments',()=>{
 assert.equal(rationalNumber(exactShellMoment([0,0,0,0],0,1)),1);
 assert.equal(rationalNumber(exactShellMoment([1,0,0,0],0,1)),.25);
 assert.equal(rationalNumber(exactShellMoment([0,2,0,0],0,1)),.1);
 assert.equal(rationalNumber(exactShellMoment([0,1,1,0],0,1)),.05);
 assert.equal(rationalNumber(exactShellMoment([0,0,0,0],0,2**-22)),2**-66);
});
test('registered point counts, positive weights and per-shell degree-five moments hold',()=>{
 for(const r of SHELL_RECIPES){const points=[...shellRule(r)];assert.equal(points.length,r.points);for(const s of shells(r.depth))assertMoments(points.filter(p=>p.shell===s.id),s);}
 assert.equal(SHELL_RECIPES.reduce((s,r)=>s+2*r.points,0),SHELL_BUDGET.plannedMaterialCalls);
 assert.throws(()=>[...shellRule({...SHELL_RECIPES[0],depth:19})],/Unregistered/);
});
test('wrong radial Jacobian and damaged positive weight fail relative core moments',()=>{
 const r=SHELL_RECIPES[0],s=shells(r.depth).at(-1),p=[...shellRule(r)].filter(p=>p.shell==='core');
 assert.throws(()=>assertMoments(p.map(x=>({...x,weight:x.weight/x.r**2})),s),/moment/);
 const damaged=structuredClone(p);damaged[0].weight*=1.01;assert.throws(()=>assertMoments(damaged,s),/moment/);
 const negative=structuredClone(p);negative[0].weight*=-1;assert.throws(()=>assertMoments(negative,s),/Positive/);
 assert.throws(()=>assertMoments(p.slice(1),s),/moment/);
});
test('depth22 shells regroup without losing the depth20 core',()=>{
 const r=SHELL_RECIPES.at(-1),points=[...shellRule(r)],core=points.filter(p=>p.comparisonShell==='core');
 assert.equal(core.length,1500);assertMoments(core,shells(20).at(-1));
 assert.equal(new Set(points.map(p=>p.comparisonShell)).size,21);
});
test('shell force and work cancellation cannot create a passing comparison',()=>{
 const a=shells(20).map(s=>({shell:s.id,localGradientsN:zeros()})),b=structuredClone(a),direction=zeros();direction[0][0]=.001;
 a[0].localGradientsN[0][0]=.001;a[1].localGradientsN[0][0]=-.001;
 const c=compareShellVectors(a,b,direction);assert.equal(c.aggregateInfinityN,0);assert.equal(c.aggregateDirectionalDifferenceJ,0);assert.equal(c.shellTriangleInfinityN,.002);assert.equal(c.shellTriangleDirectionalDifferenceJ,2e-6);assert.equal(shellComparisonPass(c,5.492029235357012e-7),false);
 assert.throws(()=>shellComparisonPass(c,1),/Original/);
});
test('missing shell, reordered shell and malformed vector refuse comparisons',()=>{
 const a=shells(20).map(s=>({shell:s.id,localGradientsN:zeros()})),b=structuredClone(a),direction=zeros();
 assert.throws(()=>compareShellVectors(a,b.slice(1),direction),/inventory/);
 const reorder=structuredClone(b);[reorder[0],reorder[1]]=[reorder[1],reorder[0]];assert.throws(()=>compareShellVectors(a,reorder,direction),/order/);
 const invalid=structuredClone(b);invalid[0].localGradientsN[0][0]=NaN;assert.throws(()=>compareShellVectors(a,invalid,direction),/finite/);
 const short=structuredClone(b);short[0].localGradientsN.pop();assert.throws(()=>compareShellVectors(a,short,direction),/ten-node/);
});
