/** Prescribed finite kinematics of a regular polygonal prism. No material solve. */
export const DEFAULTS=Object.freeze({mean:1,gradient:.4,compensate:true,cells:32,sides:16,length:.12,radius:.015});
export function parameters(input={}){
  const p={...DEFAULTS,...input};
  if(!Number.isFinite(p.mean)||p.mean<.6||p.mean>1.4||!Number.isFinite(p.gradient)||Math.abs(p.gradient)>.6)throw Error('Mean stretch must be 0.6–1.4 and gradient −0.6–0.6.');
  if(![8,16,32,64,128].includes(p.cells)||![8,16,32].includes(p.sides)||typeof p.compensate!=='boolean')throw Error('Unsupported mesh or compensation mode.');
  if(!(p.length>0&&p.radius>0)||!Number.isFinite(p.length+p.radius))throw Error('Reference dimensions must be finite and positive.');
  return p;
}
const dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
export function determinant(F){return dot(F[0],cross(F[1],F[2]));}
export function field(S,input=DEFAULTS,Y=0,Z=0){
  const p=parameters(input),lambda=p.mean*(1+p.gradient*(2*S/p.length-1));
  if(!(S>=0&&S<=p.length&&lambda>0))throw Error('Material coordinate outside the positive-stretch domain.');
  const derivative=2*p.mean*p.gradient/p.length;
  const b=p.compensate?1/Math.sqrt(lambda):1;
  const bPrime=p.compensate?-derivative/(2*lambda**1.5):0;
  const F=[[lambda,0,0],[bPrime*Y,b,0],[bPrime*Z,0,b]];
  return {lambda,b,bPrime,F,J:determinant(F),centerlineStrain:lambda-1};
}
export function mapPoint([S,Y,Z],input=DEFAULTS){
  const p=parameters(input),f=field(S,p,Y,Z);
  return [p.mean*((1-p.gradient)*S+p.gradient*S*S/p.length),f.b*Y,f.b*Z];
}
export function boundaryVolume({vertices,faces}){
  return faces.reduce((sum,[a,b,c])=>sum+dot(vertices[a],cross(vertices[b],vertices[c]))/6,0);
}
export function mesh(input=DEFAULTS,deformed=true){
  const p=parameters(input),vertices=[],faces=[];
  for(let i=0;i<=p.cells;i++)for(let j=0;j<p.sides;j++){
    const point=[p.length*i/p.cells,p.radius*Math.cos(2*Math.PI*j/p.sides),p.radius*Math.sin(2*Math.PI*j/p.sides)];
    vertices.push(deformed?mapPoint(point,p):point);
  }
  const left=vertices.length;vertices.push(deformed?mapPoint([0,0,0],p):[0,0,0]);
  const right=vertices.length;vertices.push(deformed?mapPoint([p.length,0,0],p):[p.length,0,0]);
  for(let i=0;i<p.cells;i++)for(let j=0;j<p.sides;j++){
    const next=(j+1)%p.sides,a=i*p.sides+j,b=i*p.sides+next,c=(i+1)*p.sides+j,d=(i+1)*p.sides+next;
    faces.push([a,b,d],[a,d,c]);
  }
  for(let j=0;j<p.sides;j++){
    const next=(j+1)%p.sides;
    faces.push([left,next,j],[right,p.cells*p.sides+j,p.cells*p.sides+next]);
  }
  return {vertices,faces};
}
export function state(input=DEFAULTS){
  const p=parameters(input),reference=mesh(p,false),deformed=mesh(p,true);
  const referenceVolume=boundaryVolume(reference),meshVolume=boundaryVolume(deformed);
  const polygonFactor=p.sides*Math.sin(2*Math.PI/p.sides)/2;
  const expectedReferenceVolume=polygonFactor*p.radius*p.radius*p.length;
  const cellReferenceVolume=expectedReferenceVolume/p.cells,rows=[];let frustumVolume=0;
  for(let i=0;i<p.cells;i++){
    const s0=p.length*i/p.cells,s1=p.length*(i+1)/p.cells,mid=(s0+s1)/2;
    const f0=field(s0,p),f1=field(s1,p),fm=field(mid,p,p.radius,0);
    const x0=mapPoint([s0,0,0],p)[0],x1=mapPoint([s1,0,0],p)[0],r0=p.radius*f0.b,r1=p.radius*f1.b;
    const cellVolume=polygonFactor*(x1-x0)*(r0*r0+r0*r1+r1*r1)/3;
    frustumVolume+=cellVolume;
    rows.push({materialFraction:mid/p.length,...fm,cellVolumeRatio:cellVolume/cellReferenceVolume});
  }
  const continuumVolumeRatio=p.compensate?1:p.mean;
  return {parameters:p,reference,deformed,rows,referenceVolume,expectedReferenceVolume,meshVolume,frustumVolume,
    continuumVolumeRatio,meshVolumeRatio:meshVolume/referenceVolume,
    relativeMeshVolumeError:meshVolume/referenceVolume-continuumVolumeRatio,
    referenceMeasurementError:referenceVolume-expectedReferenceVolume,
    independentMeshMeasurementError:meshVolume-frustumVolume,
    pointwiseJRange:[Math.min(field(0,p).J,field(p.length,p).J),Math.max(field(0,p).J,field(p.length,p).J)],
    centerlineStrainRange:[Math.min(field(0,p).centerlineStrain,field(p.length,p).centerlineStrain),Math.max(field(0,p).centerlineStrain,field(p.length,p).centerlineStrain)]};
}
