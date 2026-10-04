/** Deterministic analytic-gradient L-BFGS; trial domain violations are rejected. */
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
export function minimize(objective,start,{maxIterations=300,tolerance=1e-7,initialInverseScale=1,historySize=8}={}){
 let x=Float64Array.from(start),r=objective(x),history=[],accepted=0,evaluations=1,reason='iteration limit';const trace=[{iteration:0,energy:r.energy,maxGradient:Math.max(...r.gradient.map(Math.abs))}];
 if(!Number.isFinite(r.energy)||!r.gradient.every(Number.isFinite))throw Error('Nonfinite initial objective');
 for(let iteration=0;iteration<maxIterations;iteration++){
  const maxGradient=Math.max(...r.gradient.map(Math.abs));if(maxGradient<=tolerance){reason='gradient tolerance';break;}
  const direction=Float64Array.from(r.gradient),alpha=history.map(()=>0);
  for(let j=history.length-1;j>=0;j--){const h=history[j];alpha[j]=h.rho*dot(h.s,direction);for(let i=0;i<x.length;i++)direction[i]-=alpha[j]*h.y[i];}
  const last=history.at(-1),scale=last?dot(last.s,last.y)/dot(last.y,last.y):initialInverseScale;for(let i=0;i<x.length;i++)direction[i]*=scale;
  for(let j=0;j<history.length;j++){const h=history[j],beta=h.rho*dot(h.y,direction);for(let i=0;i<x.length;i++)direction[i]+=h.s[i]*(alpha[j]-beta);}
  for(let i=0;i<x.length;i++)direction[i]*=-1;let slope=dot(r.gradient,direction);if(!(slope<0)){history=[];for(let i=0;i<x.length;i++)direction[i]=-initialInverseScale*r.gradient[i];slope=dot(r.gradient,direction);}
  let next=null,trial,step=1;for(let backtrack=0;backtrack<40;backtrack++){trial=x.map((v,i)=>v+step*direction[i]);try{const candidate=objective(trial);evaluations++;if(Number.isFinite(candidate.energy)&&candidate.gradient.every(Number.isFinite)&&candidate.energy<=r.energy+1e-4*step*slope){next=candidate;break;}}catch(e){if(!(e instanceof RangeError))throw e;}step*=.5;}
  if(!next){reason='no admissible decreasing step';break;}
  const s=trial.map((v,i)=>v-x[i]),y=Float64Array.from(next.gradient,(v,i)=>v-r.gradient[i]),sy=dot(s,y);if(sy>1e-12*Math.sqrt(dot(s,s)*dot(y,y))){history.push({s,y,rho:1/sy});if(history.length>historySize)history.shift();}
  x=trial;r=next;accepted++;trace.push({iteration:accepted,energy:r.energy,maxGradient:Math.max(...r.gradient.map(Math.abs)),step});
 }
 return {x,...r,converged:reason==='gradient tolerance',reason,acceptedIterations:accepted,evaluations,trace};
}
