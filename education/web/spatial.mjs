/** Original schematic arm-volume and separate membrane lesson, SI.
 * Quasistatic central-edge/volume energy with compliant sampled capsule contact.
 * NOT FEM, anatomical material calibration, or two-way musculoskeletal coupling.
 * Deterministic L-BFGS/Armijo solve from the same bind pose at every q,a.
 */
import {SERIES,seriesInitial,seriesResults,seriesStep} from './series.mjs';
export const SPATIAL=Object.freeze({...SERIES,contact:'off',angle:30,sweeps:160,boneContact:'on',skin:'on',activeShape:'on',volumeK:25000});
const add=(a,b)=>a.map((x,i)=>x+b[i]),sub=(a,b)=>a.map((x,i)=>x-b[i]),mul=(a,s)=>a.map(x=>x*s),dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0),cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],norm=a=>Math.hypot(...a);
export const rotate=(x,q)=>[Math.cos(q)*x[0]-Math.sin(q)*x[1],Math.sin(q)*x[0]+Math.cos(q)*x[1],x[2]];
export const weight=X=>Math.max(0,Math.min(1,(.12-X[1])/.24));
export function skinPoint(X,q){return add(mul(X,1-weight(X)),mul(rotate(X,q),weight(X)));}
export function signedVolume(x,t){return dot(sub(x[t[1]],x[t[0]]),cross(sub(x[t[2]],x[t[0]]),sub(x[t[3]],x[t[0]])))/6;}
export function volumeGradient(x,t){const [A,B,C,D]=t.map(i=>x[i]),b=sub(B,A),c=sub(C,A),d=sub(D,A),g1=mul(cross(c,d),1/6),g2=mul(cross(d,b),1/6),g3=mul(cross(b,c),1/6);return [mul(add(add(g1,g2),g3),-1),g1,g2,g3];}
export function capsuleGap(X,q,which){
 const A=which===0?[0,0,0]:[0,0,0],B=which===0?[0,.27,0]:rotate([0,-.35,0],q),radius=which===0?.021:.019;
 const AB=sub(B,A),t=Math.max(0,Math.min(1,dot(sub(X,A),AB)/dot(AB,AB))),nearest=add(A,mul(AB,t)),d=sub(X,nearest),l=norm(d);
 return {gap:l-radius,normal:l>1e-12?mul(d,1/l):[1,0,0],nearest};
}
export function makeSpatial(){
 const rest=[],tets=[],sections=8,id=(i,j,k)=>(i*3+j)*3+k;
 for(let i=0;i<=sections;i++)for(let j=0;j<3;j++)for(let k=0;k<3;k++)rest.push([.058+(j-1)*.019,.24-i*.045,(k-1)*.021]);
 const perm=[[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]];
 for(let i=0;i<sections;i++)for(let j=0;j<2;j++)for(let k=0;k<2;k++)for(const p of perm){const a=[i,j,k],b=a.slice();b[p[0]]++;const c=b.slice();c[p[1]]++;const t=[id(...a),id(...b),id(...c),id(i+1,j+1,k+1)];if(signedVolume(rest,t)<0)[t[1],t[2]]=[t[2],t[1]];tets.push(t);}
 const faces=new Map(),edges=new Map();
 for(const t of tets){for(let i=0;i<4;i++)for(let j=i+1;j<4;j++){const a=Math.min(t[i],t[j]),b=Math.max(t[i],t[j]);edges.set(`${a},${b}`,[a,b]);}for(let i=0;i<4;i++){let f=t.filter((_,j)=>j!==i),key=f.slice().sort((a,b)=>a-b).join(',');if(faces.has(key)){faces.get(key).count++;continue;}if(dot(cross(sub(rest[f[1]],rest[f[0]]),sub(rest[f[2]],rest[f[0]])),sub(rest[t[i]],rest[f[0]]))>0)[f[1],f[2]]=[f[2],f[1]];faces.set(key,{tri:f,count:1});}}
 const surface=[...faces.values()].filter(f=>f.count===1).map(f=>f.tri),boundary=[...new Set(surface.flat())].sort((a,b)=>a-b),skinMap=new Map(boundary.map((v,i)=>[v,rest.length+i]));
 const skinRest=boundary.map(v=>{const X=rest[v],radial=[X[0]-.058,0,X[2]],r=norm(radial);return add(X,r>0?mul(radial,.004/r):[.004,0,0]);});
 const allRest=rest.concat(skinRest),skinSurface=surface.map(f=>f.map(v=>skinMap.get(v))),skinEdges=new Map();
 for(const f of skinSurface)for(let i=0;i<3;i++){const a=Math.min(f[i],f[(i+1)%3]),b=Math.max(f[i],f[(i+1)%3]);skinEdges.set(`${a},${b}`,[a,b]);}
 const springs=[...edges.values()].map(([i,j])=>({i,j,l0:norm(sub(rest[i],rest[j])),k:80,kind:'passive'}));
 // Nine aligned fibres; no active force is added to the existing hinge actuator.
 for(let s=0;s<4;s++)for(let j=0;j<3;j++)for(let k=0;k<3;k++){const i=id(s,j,k),v=id(s+1,j,k);springs.push({i,j:v,l0:.045,k:500,kind:'active'});}
 for(let j=0;j<3;j++)for(let k=0;k<3;k++)springs.push({i:id(4,j,k),j:id(5,j,k),l0:.045,k:1200,kind:'tendon'});
 for(const [i,j] of skinEdges.values())springs.push({i,j,l0:norm(sub(allRest[i],allRest[j])),k:12,kind:'skin'});
 const fixed=allRest.map((X,i)=>i<rest.length?Math.floor(i/9)===0||Math.floor(i/9)===8:Math.floor(boundary[i-rest.length]/9)===0||Math.floor(boundary[i-rest.length]/9)===8);
 const volume=tets.map(t=>signedVolume(rest,t));
 const samples=boundary.map(v=>({ids:[v],N:[1],kind:'core'})).concat(boundary.map(v=>({ids:[skinMap.get(v)],N:[1],kind:'skin'})),tets.map(t=>({ids:t,N:[.25,.25,.25,.25],kind:'centroid'})));
 return {rest:allRest,coreCount:rest.length,tets,volume,surface,skinSurface,boundary,skinMap,springs,fixed,samples,skinEdges:[...skinEdges.values()]};
}
export const SPATIAL_MESH=makeSpatial();
function config(q,a,p){if(!Number.isFinite(q)||q<0||q>100*Math.PI/180||!Number.isFinite(a)||a<0||a>1)throw new RangeError('spatial pose/activation domain');if(![80,160,320,640].includes(p.sweeps)||!['on','off'].includes(p.boneContact)||!['on','off'].includes(p.skin)||!['on','off'].includes(p.activeShape)||![2500,25000].includes(p.volumeK))throw new RangeError('spatial controls');}
export function spatialEnergy(x,q,a,p=SPATIAL,m=SPATIAL_MESH){
 const gradient=x.map(()=>[0,0,0]),energy={passive:0,active:0,tendon:0,volume:0,skin:0,fascia:0,contact:0};let contacts=[],minJ=Infinity;
 const accumulate=(i,g)=>{for(let d=0;d<3;d++)gradient[i][d]+=g[d];};
 for(const s of m.springs){if(s.kind==='skin'&&p.skin==='off')continue;if(s.kind==='active'&&(p.activeShape==='off'||a===0))continue;const d=sub(x[s.i],x[s.j]),l=norm(d),k=s.kind==='active'?s.k*a:s.k,target=s.kind==='active'?s.l0*(1-.18*a):s.l0,C=s.kind==='active'?Math.max(l-target,0):l-target;energy[s.kind]+=.5*k*C*C;if(l>1e-12){const g=mul(d,k*C/l);accumulate(s.i,g);accumulate(s.j,mul(g,-1));}}
 for(let i=0;i<m.tets.length;i++){const V=signedVolume(x,m.tets[i]),V0=m.volume[i],C=V-V0;minJ=Math.min(minJ,V/V0);energy.volume+=.5*p.volumeK*C*C/V0;const g=volumeGradient(x,m.tets[i]);m.tets[i].forEach((v,j)=>accumulate(v,mul(g[j],p.volumeK*C/V0)));}
 if(p.skin==='on')for(const v of m.boundary){const s=m.skinMap.get(v),posedOffset=rotate(sub(m.rest[s],m.rest[v]),weight(m.rest[v])*q),d=sub(sub(x[s],x[v]),posedOffset);energy.fascia+=.5*30*dot(d,d);accumulate(s,mul(d,30));accumulate(v,mul(d,-30));}
 if(p.boneContact==='on')for(let sample=0;sample<m.samples.length;sample++){const s=m.samples[sample];if(s.kind==='skin'&&p.skin==='off')continue;const point=[0,1,2].map(d=>s.ids.reduce((v,id,i)=>v+s.N[i]*x[id][d],0));for(let b=0;b<2;b++){const hit=capsuleGap(point,q,b);if(hit.gap>=0)continue;const k=s.kind==='centroid'?250:12000,N=-k*hit.gap;energy.contact+=.5*k*hit.gap**2;const force=mul(hit.normal,N);s.ids.forEach((id,i)=>accumulate(id,mul(force,-s.N[i])));contacts.push({sample,kind:s.kind,bone:b,point,normal:hit.normal,gap:hit.gap,force,N});}}
 const fullGradient=gradient.map(g=>g.slice());m.fixed.forEach((fixed,i)=>{if(fixed)gradient[i]=[0,0,0];});
 if(p.skin==='off')for(let i=m.coreCount;i<x.length;i++)gradient[i]=[0,0,0];
 return {energy,total:Object.values(energy).reduce((s,x)=>s+x,0),gradient:gradient.flat(),fullGradient:fullGradient.flat(),minJ,contacts};
}
/** Fixed bound L-BFGS solve; positivity/Armijo backtracking, not an inversion theorem. */
export function solveSpatial(q,a,p=SPATIAL,m=SPATIAL_MESH){
 config(q,a,p);const baseline=m.rest.map(X=>skinPoint(X,q)),x=m.rest.map(X=>rotate(X,weight(X)*q)),fixedTarget=baseline;let evaluated=spatialEnergy(x,q,a,p,m),evaluations=1,iterations=0,backtracks=0;
 if(evaluated.minJ<=.01)throw new Error('initial schematic pose inverts a tetrahedron');
 const S=[],Y=[],R=[];const acceptedEnergy=[evaluated.total];let stalled=false;
 for(;iterations<p.sweeps;iterations++){
  const g=evaluated.gradient,max=Math.max(...g.map(Math.abs));if(max<2e-5)break;
  let d=g.slice(),alpha=[];
  for(let j=S.length-1;j>=0;j--){alpha[j]=R[j]*dot(S[j],d);d=sub(d,mul(Y[j],alpha[j]));}
  const last=S.length-1,gamma=last>=0?dot(S[last],Y[last])/dot(Y[last],Y[last]):.0002;d=mul(d,gamma);
  for(let j=0;j<S.length;j++){const beta=R[j]*dot(Y[j],d);d=add(d,mul(S[j],alpha[j]-beta));}d=mul(d,-1);
  if(!(dot(g,d)<0)){S.length=Y.length=R.length=0;d=mul(g,-.0002);}
  let step=1,trial=null,trialX=null;const directional=dot(g,d),oldFlat=x.flat();
  for(let b=0;b<28;b++){trialX=x.map((X,i)=>m.fixed[i]?fixedTarget[i].slice():X.map((v,j)=>v+step*d[3*i+j]));trial=spatialEnergy(trialX,q,a,p,m);evaluations++;if(trial.minJ>.01&&trial.total<=evaluated.total+1e-4*step*directional)break;step*=.5;backtracks++;trial=null;}
  if(!trial){stalled=true;break;}
  const s=sub(trialX.flat(),oldFlat),y=sub(trial.gradient,g),sy=dot(s,y);if(sy>1e-12){if(S.length===8){S.shift();Y.shift();R.shift();}S.push(s);Y.push(y);R.push(1/sy);}
  for(let i=0;i<x.length;i++)x[i]=trialX[i];evaluated=trial;acceptedEnergy.push(trial.total);
 }
 const volumeRatios=m.tets.map((t,i)=>signedVolume(x,t)/m.volume[i]),baselineJ=m.tets.map((t,i)=>signedVolume(baseline,t)/m.volume[i]);
 const freeResidualN=Math.hypot(...evaluated.gradient),maxFreeForceN=Math.max(...evaluated.gradient.map(Math.abs)),support=[0,0,0];
 for(let i=0;i<x.length;i++)if(m.fixed[i])for(let d=0;d<3;d++)support[d]+=evaluated.fullGradient[3*i+d];
 const contactForce=evaluated.contacts.reduce((f,c)=>add(f,c.force),[0,0,0]),forceBalance=add(support,contactForce);
 let maxPenetration=0,baselinePenetration=0,minSkinGap=Infinity;
 for(const sample of m.samples){if(sample.kind==='skin'&&p.skin==='off')continue;for(const Xs of [x,baseline]){const X=[0,1,2].map(d=>sample.ids.reduce((v,id,i)=>v+sample.N[i]*Xs[id][d],0));for(let b=0;b<2;b++){const gap=capsuleGap(X,q,b).gap;if(Xs===x){maxPenetration=Math.max(maxPenetration,-gap);if(sample.kind==='skin')minSkinGap=Math.min(minSkinGap,gap);}else baselinePenetration=Math.max(baselinePenetration,-gap);}}}
 const chainLengths=Array.from({length:9},(_,j)=>Array.from({length:4},(_,i)=>norm(sub(x[(i+1)*9+j],x[i*9+j]))).reduce((a,b)=>a+b,0));
 const muscleLength=norm(sub(x[4*9+4],x[4])),tendonLength=norm(sub(x[5*9+4],x[4*9+4]));
 return {x,baseline,q,a,acceptedEnergy,iterations,evaluations,backtracks,stalled,converged:maxFreeForceN<2e-5,freeResidualN,maxFreeForceN,forceBalanceN:forceBalance,supportN:support,contactForceN:contactForce,contactNormalSumN:evaluated.contacts.reduce((s,c)=>s+c.N,0),maxPenetrationM:maxPenetration,baselinePenetrationM:baselinePenetration,minSkinGapM:minSkinGap,volumeRatios,baselineJ,minJ:Math.min(...volumeRatios),maxJ:Math.max(...volumeRatios),meanJ:volumeRatios.reduce((s,J,i)=>s+J*m.volume[i],0)/m.volume.reduce((s,V)=>s+V,0),baselineMinJ:Math.min(...baselineJ),baselineMeanJ:baselineJ.reduce((s,J,i)=>s+J*m.volume[i],0)/m.volume.reduce((s,V)=>s+V,0),muscleLengthM:muscleLength,fiberArcLengthM:chainLengths[4],meanFiberArcM:chainLengths.reduce((s,l)=>s+l,0)/9,fiberChainLengthsM:chainLengths,tendonLengthM:tendonLength,...evaluated};
}
export const spatialInitial=p=>seriesInitial({...p,contact:'off'});
export function spatialStep(s,p){const trial=seriesStep(s,{...p,contact:'off'});return trial.q>100*Math.PI/180?{...s,halted:true}:trial;}
export function spatialResults(s,p=SPATIAL){return {hinge:seriesResults(s,{...p,contact:'off'}),shape:solveSpatial(s.q,s.a,p)};}
