/** Complete transverse edge/face crossings after triangle AABB pruning.
 * Coplanar overlaps and containment require separate distance/inside queries.
 */
const sub=(a,b)=>a.map((v,d)=>v-b[d]),cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],dot=(a,b)=>a.reduce((s,v,d)=>s+v*b[d],0);
function crossing(a,b,t){const d=sub(b,a),e1=sub(t[1],t[0]),e2=sub(t[2],t[0]),h=cross(d,e2),den=dot(e1,h);if(Math.abs(den)<1e-15)return false;const s=sub(a,t[0]),u=dot(s,h)/den,v=dot(d,cross(s,e1))/den,l=dot(e2,cross(s,e1))/den;return u>1e-8&&v>1e-8&&u+v<1-1e-8&&l>1e-8&&l<1-1e-8;}
export function triangleRecords(vertices,indices,transform=x=>x){const X=vertices.map(transform);return indices.map((ids,i)=>{const t=ids.map(j=>X[j]);return {i,t,lo:[0,1,2].map(d=>Math.min(...t.map(p=>p[d]))),hi:[0,1,2].map(d=>Math.max(...t.map(p=>p[d])))};});}
export function transverseCrossings(A,B){let candidates=0,count=0;const examples=[];for(const a of A)for(const b of B){if(a.lo.some((lo,d)=>lo>b.hi[d]||b.lo[d]>a.hi[d]))continue;candidates++;if([0,1,2].some(k=>crossing(a.t[k],a.t[(k+1)%3],b.t)||crossing(b.t[k],b.t[(k+1)%3],a.t))){count++;if(examples.length<12)examples.push([a.i,b.i]);}}return {broadPhasePairs:candidates,crossingPairs:count,examples};}
