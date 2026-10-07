/** Invented retained-vector fixture only. No constitutive evaluator called. */
import fs from 'node:fs';import path from 'node:path';import {ALL_TERMS} from '../tools/fixed-field-integration-assembly.mjs';import {compareShellStages} from '../tools/element247-shell-runtime.mjs';
const root=path.resolve(process.argv[2]),d=root,read=n=>JSON.parse(fs.readFileSync(path.join(d,n))),write=(n,v)=>fs.writeFileSync(path.join(d,n),JSON.stringify(v)+'\n');
const arrays=read('saved-arrays.json'),ids=JSON.parse(process.argv[3]),direction=arrays.terminalDirectionM,localDirection=ids.map(n=>direction[n]),recipes=['C44','C55','R55','A55','X55'],stages={};
const dot=(v,u)=>v.reduce((sum,X,i)=>sum+X.reduce((s,x,k)=>s+x*u[i][k],0),0),H=2**54;
for(const [r,recipe] of recipes.entries())for(const state of ['control45','terminal46']){
 const stage=read(`${recipe}-${state}-assembly.json`);for(const t of ALL_TERMS){stage.localGradientsN[t]=Array.from({length:10},()=>[0,0,0]);stage.nodalGradientsN[t]=Array.from({length:585},()=>[0,0,0]);stage.energiesJ[t]=0;}
 for(const g of stage.comparisonShells){for(const t of ALL_TERMS){g.localGradientsN[t]=Array.from({length:10},()=>[0,0,0]);g.energiesJ[t]=0;}}
 for(const [index,name] of stage.localShellFiles.entries()){
  const row=read(name);for(const t of ALL_TERMS){row.localGradientsN[t]=Array.from({length:10},()=>[0,0,0]);row.energiesJ[t]=0;}
  if(index<2){const sign=index===0?1:-1;row.localGradientsN.matrix[0]=[sign*H,sign,-sign*H];row.localGradientsN.volume[0]=[sign,-sign*H,sign*H];row.localGradientsN.passiveFiber[0]=[-sign*H,sign*H,sign];row.localGradientsN.total[0]=[0,0,sign];row.energiesJ={matrix:sign*H,volume:sign,passiveFiber:-sign*H,activePotential:0,total:0};}
  if(index===2){const off=r*2e-6;row.localGradientsN.matrix[0]=[3+off,0,0];row.localGradientsN.volume[0]=[0,2,0];row.localGradientsN.passiveFiber[0]=[0,0,1];row.localGradientsN.total[0]=[3+off,2,1];row.energiesJ={matrix:.1,volume:.2,passiveFiber:.3,activePotential:.4,total:1};}
  row.terminalDirectionalDerivativesJ=Object.fromEntries(ALL_TERMS.map(t=>[t,dot(row.localGradientsN[t],localDirection)]));write(name,row);const group=stage.comparisonShells.find(g=>g.shell===row.comparisonShell);
  for(const t of ALL_TERMS){stage.energiesJ[t]+=row.energiesJ[t];group.energiesJ[t]+=row.energiesJ[t];for(let i=0;i<10;i++)for(let k=0;k<3;k++){stage.localGradientsN[t][i][k]+=row.localGradientsN[t][i][k];stage.nodalGradientsN[t][ids[i]][k]+=row.localGradientsN[t][i][k];group.localGradientsN[t][i][k]+=row.localGradientsN[t][i][k];}}
 }
 stage.terminalDirectionalDerivativesJ=Object.fromEntries(ALL_TERMS.map(t=>[t,dot(stage.nodalGradientsN[t],direction)]));write(`${recipe}-${state}-assembly.json`,stage);stages[`${recipe}-${state}`]=stage;
}
const comparisons=[];for(const state of ['control45','terminal46'])for(const [a,b] of [['C44','C55'],['C55','R55'],['C55','A55'],['A55','X55']])comparisons.push({...compareShellStages(stages[`${a}-${state}`],stages[`${b}-${state}`],direction,ids,5.492029235357012e-7),required:a!=='C44'});write('shell-vector-comparisons.json',{comparisons,fixtureOnly:true});
console.log(JSON.stringify({fixtureOnly:true,materialCalls:0,maximumFixtureForceN:H,nonzeroScatteredTotalN:stages['C55-terminal46'].nodalGradientsN.total[ids[0]],comparisonTotalDifferenceN:comparisons[1].terms.total.aggregateInfinityN,arithmetic:'IEEE binary64 explicit sequential JS reductions; nested node/coordinate work versus flat comparison work'}));
