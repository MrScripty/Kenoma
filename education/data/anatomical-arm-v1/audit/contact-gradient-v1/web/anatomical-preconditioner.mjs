/** Reference elastic operator for solver preconditioning only, not new physics. */
export function referenceMatrix(fixture,free,scale,material){
 const n=free.length,index=fixture.nodes.map(()=>[-1,-1,-1]);free.forEach(([i,d],j)=>index[i][d]=j);const matrix=Array.from({length:n},()=>new Float64Array(n));for(let k=0;k<fixture.elements.length;k++){const ids=fixture.connectivity[k];for(const point of fixture.elements[k].points)for(let i=0;i<10;i++)for(let j=0;j<10;j++){const gi=point.gradient[i],gj=point.gradient[j],inner=gi[0]*gj[0]+gi[1]*gj[1]+gi[2]*gj[2],w=point.referenceWeightM3*scale*scale;for(let d=0;d<3;d++){const a=index[ids[i]][d];if(a<0)continue;for(let c=0;c<3;c++){const b=index[ids[j]][c];if(b>=0)matrix[a][b]+=w*(material.mu*((d===c?inner:0)+gi[c]*gj[d])+(material.bulk-2*material.mu/3)*gi[d]*gj[c]);}}}}return matrix;
}
export function denseReferencePreconditioner(matrix){
 const n=matrix.length;let previousShift=NaN,L;
 return (v,shift=0)=>{if(shift!==previousShift){L=Array.from({length:n},()=>new Float64Array(n));for(let i=0;i<n;i++)for(let j=0;j<=i;j++){let sum=matrix[i][j]+(i===j?shift:0);for(let k=0;k<j;k++)sum-=L[i][k]*L[j][k];if(i===j){if(!(sum>1e-14))throw new RangeError('Reference preconditioner is not positive definite');L[i][j]=Math.sqrt(sum);}else L[i][j]=sum/L[j][j];}previousShift=shift;}const z=new Float64Array(n);for(let i=0;i<n;i++){let sum=v[i];for(let j=0;j<i;j++)sum-=L[i][j]*z[j];z[i]=sum/L[i][i];}for(let i=n-1;i>=0;i--){let sum=z[i];for(let j=i+1;j<n;j++)sum-=L[j][i]*z[j];z[i]=sum/L[i][i];}return z;};
}
