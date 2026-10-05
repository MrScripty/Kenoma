/** Second-order derivatives of the active closest triangle feature. Original
 * Float64 implementation; not a Lean/biological claim. The ray query selects
 * the sign and feature; derivatives apply while that local feature is fixed.
 */
const N=12;
function constant(v){return {value:v,gradient:new Float64Array(N),hessian:new Float64Array(N*N)};}
function variable(v,i){const a=constant(v);a.gradient[i]=1;return a;}
function add(a,b){const r=constant(a.value+b.value);for(let i=0;i<N;i++)r.gradient[i]=a.gradient[i]+b.gradient[i];for(let i=0;i<N*N;i++)r.hessian[i]=a.hessian[i]+b.hessian[i];return r;}
function scale(a,s){const r=constant(a.value*s);for(let i=0;i<N;i++)r.gradient[i]=s*a.gradient[i];for(let i=0;i<N*N;i++)r.hessian[i]=s*a.hessian[i];return r;}
function product(a,b){const r=constant(a.value*b.value);for(let i=0;i<N;i++)r.gradient[i]=a.gradient[i]*b.value+b.gradient[i]*a.value;for(let i=0;i<N;i++)for(let j=0;j<N;j++)r.hessian[i*N+j]=a.hessian[i*N+j]*b.value+b.hessian[i*N+j]*a.value+a.gradient[i]*b.gradient[j]+b.gradient[i]*a.gradient[j];return r;}
function unary(a,value,first,second){const r=constant(value);for(let i=0;i<N;i++)r.gradient[i]=first*a.gradient[i];for(let i=0;i<N;i++)for(let j=0;j<N;j++)r.hessian[i*N+j]=first*a.hessian[i*N+j]+second*a.gradient[i]*a.gradient[j];return r;}
function reciprocal(a){if(!(a.value>0))throw new RangeError('Contact differential denominator');return unary(a,1/a.value,-1/a.value**2,2/a.value**3);}
function squareRoot(a){if(!(a.value>1e-24))throw new RangeError('Contact feature norm domain');const v=Math.sqrt(a.value);return unary(a,v,.5/v,-.25/(a.value*v));}
const minus=(a,b)=>add(a,scale(b,-1)),sub=(a,b)=>a.map((v,i)=>minus(v,b[i])),dot=(a,b)=>a.reduce((s,v,i)=>add(s,product(v,b[i])),constant(0)),cross=(a,b)=>[minus(product(a[1],b[2]),product(a[2],b[1])),minus(product(a[2],b[0]),product(a[0],b[2])),minus(product(a[0],b[1]),product(a[1],b[0]))];
export function closestFeatureDifferential(point,triangle,query){
 const values=[point,...triangle],X=values.map((v,k)=>v.map((x,d)=>variable(x,3*k+d))),[P,A,B,C]=X,active=query.barycentric.map((v,i)=>v>1e-8?i:-1).filter(i=>i>=0);let g,feature;
 if(active.length===3){const n0=cross(sub(B,A),sub(C,A)),inverse=reciprocal(squareRoot(dot(n0,n0))),n=n0.map(v=>product(v,inverse)),raw=dot(n,sub(P,A)),normal=n.map(v=>v.value),alignment=normal.reduce((s,v,i)=>s+v*query.gradient[i],0);g=scale(raw,alignment>=0?1:-1);feature='face';}
 else{const a=X[1+active[0]],r=sub(P,a);let perpendicular=r;if(active.length===2){const e=sub(X[1+active[1]],a),projection=product(dot(r,e),reciprocal(dot(e,e)));perpendicular=r.map((v,d)=>minus(v,product(projection,e[d])));feature='edge';}else feature='vertex';g=scale(squareRoot(dot(perpendicular,perpendicular)),query.inside?-1:1);}
 return {...g,feature};
}
