/** Geometry and retained-vector arithmetic only; no constitutive evaluator. */
import assert from 'node:assert/strict';
import {GAUSS,INTEGRATION_GATE_N} from './fixed-field-integration-protocol.mjs';
import {dyadic} from './isolated-segment-geometry.mjs';
export const ELEMENT=247, CORNER=0, COMPARISON_DEPTH=20;
export const SHELL_RECIPES=Object.freeze([
 {id:'C44',depth:20,radialOrder:4,angularOrder:4,radialParts:1,angularParts:1,faceOrder:[1,2,3],points:1344},
 {id:'C55',depth:20,radialOrder:5,angularOrder:5,radialParts:1,angularParts:1,faceOrder:[1,2,3],points:2625},
 {id:'R55',depth:20,radialOrder:5,angularOrder:5,radialParts:2,angularParts:1,faceOrder:[1,2,3],points:5250},
 {id:'A55',depth:20,radialOrder:5,angularOrder:5,radialParts:1,angularParts:2,faceOrder:[1,2,3],points:10500},
 {id:'X55',depth:22,radialOrder:5,angularOrder:5,radialParts:1,angularParts:2,faceOrder:[2,3,1],points:11500}
]);
export const REQUIRED_SHELL_COMPARISONS=[['C55','R55'],['C55','A55'],['A55','X55']];
export const SHELL_BUDGET={plannedMaterialCalls:62438,maximumMaterialCalls:62500,maximumWallSeconds:180,nodeHeapMiB:1024,maximumRssBytes:2147483648,maximumOutputBytes:67108864,invocations:1};
export function shells(depth){
 assert.ok(Number.isInteger(depth)&&depth>=1&&depth<=22,'Bounded shell depth1..22');
 const out=Array.from({length:depth},(_,k)=>({id:`s${k+1}`,lo:2**(-k-1),hi:2**(-k)}));
 out.push({id:'core',lo:0,hi:2**(-depth)});assertCoverage(out);return out;
}
export function assertCoverage(rows){
 assert.ok(rows.length>=2&&new Set(rows.map(s=>s.id)).size===rows.length,'Missing or duplicate shell');
 assert.equal(rows[0].hi,1,'Missing outer element');assert.equal(rows.at(-1).lo,0,'Missing corner core');
 for(let i=0;i<rows.length;i++){
  const s=rows[i];assert.ok(Number.isFinite(s.lo)&&Number.isFinite(s.hi)&&s.lo>=0&&s.hi>s.lo,'Invalid shell interval');
  if(i)assert.equal(rows[i-1].lo,s.hi,'Gap or overlap between shells');
 }
}
export function shellMap(r,a,b,faceOrder=[1,2,3]){
 assert.deepEqual([...faceOrder].sort(),[1,2,3],'Face direction permutation');
 assert.ok([r,a,b].every(x=>Number.isFinite(x)&&x>0&&x<1),'Interior chart coordinates');
 const L=[1-r,0,0,0];L[faceOrder[0]]=r*a;L[faceOrder[1]]=r*(1-a)*b;L[faceOrder[2]]=r*(1-a)*(1-b);
 return {L,jacobian:r*r*(1-a)};
}
export function* shellRule(recipe){
 assert.deepEqual(recipe,SHELL_RECIPES.find(x=>x.id===recipe.id),'Unregistered shell recipe');
 const gr=GAUSS[recipe.radialOrder],ga=GAUSS[recipe.angularOrder];
 for(const s of shells(recipe.depth))for(let rp=0;rp<recipe.radialParts;rp++){
  const dr=(s.hi-s.lo)/recipe.radialParts,rlo=s.lo+rp*dr;
  for(let ap=0;ap<recipe.angularParts;ap++)for(let bp=0;bp<recipe.angularParts;bp++)
   for(let i=0;i<gr.x.length;i++)for(let j=0;j<ga.x.length;j++)for(let k=0;k<ga.x.length;k++){
    const r=rlo+dr*gr.x[i],a=(ap+ga.x[j])/recipe.angularParts,b=(bp+ga.x[k])/recipe.angularParts,m=shellMap(r,a,b,recipe.faceOrder);
    yield {L:m.L,weight:6*dr*gr.w[i]*ga.w[j]*ga.w[k]*m.jacobian/recipe.angularParts**2,r,shell:s.id,
     comparisonShell:s.hi<=2**(-COMPARISON_DEPTH)?'core':s.id};
   }
 }
}
// An independent rational oracle integrates monomials analytically. No nodes,
// tables or shellRule calls are used, even for tiny core moments.
const gcd=(a,b)=>{a=a<0n?-a:a;while(b){const c=a%b;a=b;b=c;}return a;};
export function rational(n,d=1n){assert.ok(d!==0n);if(d<0n){n=-n;d=-d;}const g=gcd(n,d);return {n:n/g,d:d/g};}
const add=(a,b)=>rational(a.n*b.d+b.n*a.d,a.d*b.d),mul=(a,b)=>rational(a.n*b.n,a.d*b.d);
const pow=(a,p)=>rational(a.n**BigInt(p),a.d**BigInt(p));
export const rationalNumber=q=>Number(q.n)/Number(q.d);
const exact=x=>{const a=dyadic(x);return a.e>=0?rational(a.n<<BigInt(a.e)):rational(a.n,1n<<BigInt(-a.e));};
const fac=n=>{let p=1n;for(let k=2;k<=n;k++)p*=BigInt(k);return p;};
export function exactShellMoment(alpha,lo,hi){
 assert.ok(alpha.length===4&&alpha.every(x=>Number.isInteger(x)&&x>=0&&x<=8));
 assert.ok(lo>=0&&hi>lo&&hi<=1);const [a0,...a]=alpha,t=a.reduce((x,y)=>x+y,0),l=exact(lo),h=exact(hi);let integral=rational(0n);
 for(let k=0;k<=a0;k++){
  const p=t+3+k,coefficient=fac(a0)/(fac(k)*fac(a0-k))*(k%2?-1n:1n);
  const hp=pow(h,p),lp=pow(l,p),difference=add(hp,rational(-lp.n,lp.d));
  integral=add(integral,mul(rational(coefficient,BigInt(p)),difference));
 }
 return mul(rational(6n*a.map(fac).reduce((x,y)=>x*y,1n),fac(t+2)),integral);
}
export function* monomials(maxDegree){
 for(let n=0;n<=maxDegree;n++)for(let a=0;a<=n;a++)for(let b=0;b<=n-a;b++)for(let c=0;c<=n-a-b;c++)yield [a,b,c,n-a-b-c];
}
export const monomial=(L,a)=>a.reduce((v,p,i)=>v*L[i]**p,1);
export function exactReferenceMoment(polynomial,alpha,lo,hi){
 let sum=rational(0n);
 for(const c of polynomial.coefficients){
  const factor=fac(3)/c.multiIndex.map(fac).reduce((x,y)=>x*y,1n);
  const coefficient=rational(c.referenceNumerator*factor,BigInt(polynomial.denominatorFactor)*(1n<<BigInt(polynomial.denominatorPowerOfTwo))*6n);
  sum=add(sum,mul(coefficient,exactShellMoment(alpha.map((x,i)=>x+c.multiIndex[i]),lo,hi)));
 }
 return sum;
}
export function assertMoments(points,shell,maxDegree=5,tolerance=2e-11){
 assert.ok(points.length>0,'Empty shell');let maximumRelativeError=0,minimumWeight=Infinity;
 for(const p of points){assert.ok(Number.isFinite(p.weight)&&p.weight>0,'Positive finite weights required');assert.ok(p.L.every(x=>Number.isFinite(x)&&x>0&&x<1)&&Math.abs(p.L.reduce((x,y)=>x+y,0)-1)<1e-14,'Invalid barycentric point');minimumWeight=Math.min(minimumWeight,p.weight);}
 for(const a of monomials(maxDegree)){
  const expected=rationalNumber(exactShellMoment(a,shell.lo,shell.hi)),actual=points.reduce((v,p)=>v+p.weight*monomial(p.L,a),0),error=Math.abs(actual-expected)/expected;
  assert.ok(error<=tolerance,`Shell ${shell.id} moment ${a}: relative error ${error}`);maximumRelativeError=Math.max(maximumRelativeError,error);
 }
 return {maximumRelativeError,minimumWeight,normalizedMass:points.reduce((v,p)=>v+p.weight,0),checkedMonomials:[...monomials(maxDegree)].length};
}
const vector=v=>assert.ok(Array.isArray(v)&&v.length===10&&v.every(x=>Array.isArray(x)&&x.length===3&&x.every(Number.isFinite)),'Complete finite ten-node force vector required');
export function compareShellVectors(a,b,localDirection){
 vector(localDirection);const bins=shells(COMPARISON_DEPTH).map(s=>s.id);
 for(const rows of [a,b]){assert.equal(rows.length,bins.length,'Complete comparison-shell inventory');assert.deepEqual(rows.map(s=>s.shell),bins,'Shell order, duplicates or omissions');for(const s of rows)vector(s.localGradientsN);}
 const differences=a.map((s,k)=>({shell:s.shell,localDifferenceN:s.localGradientsN.map((v,i)=>v.map((x,d)=>x-b[k].localGradientsN[i][d]))}));
 const summed=Array.from({length:10},()=>[0,0,0]),absolute=Array.from({length:10},()=>[0,0,0]);let work=0,workBound=0;
 for(const s of differences){let shellWork=0;for(let i=0;i<10;i++)for(let d=0;d<3;d++){const v=s.localDifferenceN[i][d];summed[i][d]+=v;absolute[i][d]+=Math.abs(v);shellWork+=v*localDirection[i][d];}s.directionalDifferenceJ=shellWork;work+=shellWork;workBound+=Math.abs(shellWork);}
 const aggregateInfinityN=Math.max(...summed.flat().map(Math.abs)),shellTriangleInfinityN=Math.max(...absolute.flat()),directionL1M=localDirection.flat().reduce((s,x)=>s+Math.abs(x),0);
 // The original whole saved-direction budget is supplied explicitly by caller;
 // local-direction L1 is reported only, never used to loosen that budget.
 return {differences,aggregateDifferenceN:summed,absoluteShellDifferenceN:absolute,aggregateInfinityN,shellTriangleInfinityN,aggregateDirectionalDifferenceJ:Math.abs(work),shellTriangleDirectionalDifferenceJ:workBound,localDirectionL1M:directionL1M};
}
export function shellComparisonPass(comparison,unchangedWholeDirectionGateJ){
 assert.equal(unchangedWholeDirectionGateJ,5.492029235357012e-7,'Original work gate required');
 return comparison.aggregateInfinityN<=INTEGRATION_GATE_N&&comparison.shellTriangleInfinityN<=INTEGRATION_GATE_N&&comparison.aggregateDirectionalDifferenceJ<=unchangedWholeDirectionGateJ&&comparison.shellTriangleDirectionalDifferenceJ<=unchangedWholeDirectionGateJ;
}
