/** Strict indexed-surface checks on the actual WASM response, independent of rendering. */
export function verifySurfaceTopology(mesh){
 const {positions,normals,indices}=mesh;
 if(!positions.length||positions.length!==normals.length||indices.length%3)throw Error('Invalid buffer sizes');
 const edges=new Map(),adj=positions.map(()=>[]),links=positions.map(()=>[]),used=new Set();let minimumAreaSquared=Infinity;
 for(let i=0;i<positions.length;i++){if(!positions[i].every(Number.isFinite)||!normals[i].every(Number.isFinite)||Math.abs(Math.hypot(...normals[i])-1)>1e-4)throw Error('Nonfinite geometry or nonunit normal');}
 for(let i=0;i<indices.length;i+=3){const ids=indices.slice(i,i+3);if(new Set(ids).size!==3||ids.some(id=>!Number.isInteger(id)||id<0||id>=positions.length))throw Error('Invalid triangle');const [a,b,c]=ids.map(id=>positions[id]);const u=b.map((x,j)=>x-a[j]),v=c.map((x,j)=>x-a[j]);const areaSquared=(u[1]*v[2]-u[2]*v[1])**2+(u[2]*v[0]-u[0]*v[2])**2+(u[0]*v[1]-u[1]*v[0])**2;if(!(areaSquared>0))throw Error('Degenerate triangle');minimumAreaSquared=Math.min(minimumAreaSquared,areaSquared);for(let j=0;j<3;j++){const x=ids[j],y=ids[(j+1)%3];links[x].push([y,ids[(j+2)%3]]);const key=x<y?`${x},${y}`:`${y},${x}`,edge=edges.get(key)||{count:0,winding:0};edge.count++;edge.winding+=x<y?1:-1;edges.set(key,edge);adj[x].push(y);adj[y].push(x);used.add(x);}}
 for(const edge of edges.values())if(edge.count!==2||edge.winding!==0)throw Error('Surface not closed and consistently oriented');
 for(const pairs of links){const link=new Map();for(const [a,b]of pairs){if(!link.has(a))link.set(a,[]);if(!link.has(b))link.set(b,[]);link.get(a).push(b);link.get(b).push(a);}for(const neighbors of link.values())if(neighbors.length!==2)throw Error('Vertex link is not a cycle');const visited=new Set(),todo=[link.keys().next().value];while(todo.length){const n=todo.pop();if(visited.has(n))continue;visited.add(n);for(const next of link.get(n)||[])if(!visited.has(next))todo.push(next);}if(visited.size!==link.size)throw Error('Disconnected vertex link (bowtie)');}
 const visited=new Set(),todo=[indices[0]];while(todo.length){const id=todo.pop();if(visited.has(id))continue;visited.add(id);for(const next of adj[id])if(!visited.has(next))todo.push(next);}
 if(visited.size!==positions.length||used.size!==positions.length)throw Error('Disconnected or unreferenced surface vertex');
 return {vertices:positions.length,triangles:indices.length/3,edges:edges.size,components:1,vertexLinks:'single cycles',minimumAreaSquared};
}
