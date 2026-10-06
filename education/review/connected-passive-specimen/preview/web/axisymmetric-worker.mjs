import {prepareAxisymmetric,solveAxisymmetric,solveAxisymmetricPath,revolvedBoundary,createMaterialSampler} from './axisymmetric-specimen.mjs';
self.onmessage=({data})=>{
 try{
  const {sequence,configuration:c}=data,mesh=prepareAxisymmetric({axialCells:c.axialCells,radialCells:c.radialCells,ratio:c.ratio,order:7});
  const state=c.cap===1?solveAxisymmetric(mesh,c.epsilon,{maxIterations:1,tolerance:1e-10}):solveAxisymmetricPath(mesh,c.epsilon,{maxIterations:25,tolerance:1e-10});
  if(state.epsilon!==c.epsilon)throw new Error('Continuation did not reach requested end displacement; preceding display must be retained');
  const boundary=revolvedBoundary(mesh,state,{azimuth:256,axialSubdivisions:8}),sample=createMaterialSampler(mesh,state),surfaceJ=[];
  for(let j=0;j<boundary.rings;j++){const Z=mesh.parameters.length*j/(boundary.rings-1),R=mesh.parameters.radius*(1+(c.ratio-1)*Z/mesh.parameters.length),J=sample(R,Z).J;for(let i=0;i<boundary.azimuth;i++)surfaceJ.push(J);}
  surfaceJ.push(sample(0,0).J,sample(0,mesh.parameters.length).J);
  const trace=Array.from({length:41},(_,i)=>{const Z=mesh.parameters.length*i/40,R=.5*mesh.parameters.radius*(1+(c.ratio-1)*i/40),p=sample(R,Z);return {Z,J:p.J,axialLineStretch:p.axialLineStretch,radialLineStretch:p.radialLineStretch,hoopStretch:p.hoopStretch};});
  self.postMessage({sequence,configuration:c,state,boundary,surfaceJ,trace});
 }catch(error){self.postMessage({sequence:data.sequence,error:String(error.message)});}
};
