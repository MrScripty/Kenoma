/** Passive isotropic finite-compliance material. SI; no pressure projection.
 * v = [r_R, r_Z, z_R, z_Z, r/R], in orthonormal cylindrical bases.
 * Exact matrix/volume terms of the existing authored passive material;
 * no fibre, activation, anatomy or exact-incompressibility claim.
 */
export const PASSIVE_MATERIAL=Object.freeze({mu:1500,bulk:30000});

export function axisymmetricMaterial(v,{mu,bulk}=PASSIVE_MATERIAL){
 if(v.length!==5||![...v,mu,bulk].every(Number.isFinite)||mu<=0||bulk<=0)throw new RangeError('Finite passive material inputs');
 const [a,b,c,d,h]=v,det=a*d-b*c,J=h*det;
 if(!(h>0&&det>0&&J>1e-6))throw new RangeError('Positive radius, meridional orientation and J above 1e-6 required');
 const I1=v.reduce((s,x)=>s+x*x,0),logJ=Math.log(J),f=J**(-2/3),fp=-2/3*J**(-5/3);
 const A=-mu/3*I1*J**(-5/3)+bulk*logJ/J;
 const B=5*mu/9*I1*J**(-8/3)+bulk*(1-logJ)/(J*J);
 const j=[h*d,-h*c,-h*b,h*a,det],jj=Array.from({length:5},()=>Array(5).fill(0));
 for(const [i,k,x] of [[0,3,h],[1,2,-h],[0,4,d],[1,4,-c],[2,4,-b],[3,4,a]])jj[i][k]=jj[k][i]=x;
 const gradient=v.map((x,i)=>mu*f*x+A*j[i]);
 const tangent=v.map((x,i)=>v.map((y,k)=>mu*f*(i===k?1:0)+mu*fp*(x*j[k]+j[i]*y)+B*j[i]*j[k]+A*jj[i][k]));
 const cauchy={rr:(gradient[0]*a+gradient[1]*b)/J,rz:(gradient[0]*c+gradient[1]*d)/J,zr:(gradient[2]*a+gradient[3]*b)/J,zz:(gradient[2]*c+gradient[3]*d)/J,hoop:gradient[4]*h/J};
 return {J,I1,logJ,matrixEnergyPa:mu/2*(f*I1-3),volumeEnergyPa:bulk/2*logJ*logJ,energyPa:mu/2*(f*I1-3)+bulk/2*logJ*logJ,gradient,tangent,cauchy,meanStressPa:bulk*logJ/J};
}

/** Scalar homogeneous oracle derived separately from the free-side equation.
 * With prescribed lambda, s=log J and b²=exp(s)/lambda, sigma_rr=0 becomes
 * exp(s)/lambda-lambda²+3*(K/mu)*s*exp(2s/3)=0.
 * Restricted to the first milestone's lambda and material, not a general root theorem.
 */
export function uniformCylinderOracle(lambda,{mu,bulk}=PASSIVE_MATERIAL){
 if(!Number.isFinite(lambda)||lambda<.9||lambda>1.1||mu!==1500||bulk!==30000)throw new RangeError('Bounded uniform-cylinder oracle');
 const ratio=bulk/mu,g=s=>Math.exp(s)/lambda-lambda*lambda+3*ratio*s*Math.exp(2*s/3);
 let lo=-.05,hi=.05;
 if(!(g(lo)<0&&g(hi)>0))throw new Error('Oracle bracket does not straddle free-side root');
 for(let i=0;i<80;i++){const m=(lo+hi)/2;if(g(m)>0)hi=m;else lo=m;}
 const s=lambda===1?0:(lo+hi)/2,J=Math.exp(s),b=Math.sqrt(J/lambda),I1=lambda*lambda+2*b*b;
 const sigmaZZ=mu*J**(-5/3)*(lambda*lambda-I1/3)+bulk*s/J;
 return {lambda,b,J,logJ:s,lateralResidualPa:mu/3*J**(-5/3)*(b*b-lambda*lambda)+bulk*s/J,axialCauchyPa:sigmaZZ,nominalAxialPa:b*b*sigmaZZ,energyDensityPa:mu/2*(J**(-2/3)*I1-3)+bulk/2*s*s};
}
