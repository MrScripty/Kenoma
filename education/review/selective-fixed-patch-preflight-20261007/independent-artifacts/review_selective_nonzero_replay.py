import json,pathlib,numpy as np
root=pathlib.Path('/workspace/Kenoma-patch-runner/education'); read=lambda p:json.loads(p.read_text());report=read(pathlib.Path('/tmp/selective-independent-nonzero.json'));mat=pathlib.Path(report['outputDirectory'])/'material'; source=next(s for s in read(root/'data/anatomical-arm-v1/generated/arm-reference.json')['muscles'] if s['element_id']=='FJ1486');ids=source['elements_ten_node'];T=['matrix','volume','passiveFiber','activePotential','total'];direction=np.array(read(mat/'saved-arrays.json')['terminalDirectionM']);schedule=read(root/'research/selective-fixed-patch-20261007-inputs.json')['schedule']; stages=0;regions=0;comparisons=0;maxerr=0.
def close(a,b,tol=1e-8):
 global maxerr
 e=float(np.max(np.abs(np.array(a)-np.array(b))));assert e<=tol,e;maxerr=max(maxerr,e)
for state in ['control45','terminal46']:
 for r in schedule:
  e=r['element'];key=f'{state}-{e}-{r["id"]}';rows=[read(mat/f'{key}-s{i}.json') if False else read(mat/f'{key}-{s}-region.json') for s in [f's{i}' for i in range(1,r['depth']+1)]+['core']];stage=read(mat/f'{key}-stage.json');assert [x['shell'] for x in rows]==[f's{i}' for i in range(1,r['depth']+1)]+['core'];regions+=len(rows);stages+=1
  for t in T:
   close(sum((np.array(x['localGradientsN'][t]) for x in rows)),stage['localGradientsN'][t]);close(sum(x['energiesJ'][t] for x in rows),stage['energiesJ'][t],1e-9)
   for b in stage['comparisonShells']:
    selected=[x for x in rows if x['comparisonShell']==b['shell']];assert b['originalShells']==[x['shell'] for x in selected];close(sum((np.array(x['localGradientsN'][t]) for x in selected)),b['localGradientsN'][t]);close(sum(x['energiesJ'][t] for x in selected),b['energiesJ'][t],1e-9)
 for pair in ['Q0-Q1','Q1-Q2','Q0-Q2','F44-R44']:
  c=read(mat/f'{state}-{pair}-comparison.json');comparisons+=1
  a,b=pair.split('-');
  def endpoint(q,e,shell):
   if pair=='F44-R44':return next(x for x in read(mat/f'{state}-247-{q}-stage.json')['comparisonShells'] if x['shell']==shell)
   if shell=='whole':return next(x for x in read(mat/f'{state}-{q}-hybrid.json')['localElements'] if x['element']==e)
   if e==247 and q=='Q0':value=read(root/f'review/element247-shell-run-20261007/material/A55-{state}-assembly.json')
   else:
    rule=({'Q0':'A55','Q1':'F44','Q2':'X44'} if e==247 else {'Q0':'C55','Q1':'A55'})[q];value=read(mat/f'{state}-{e}-{rule}-stage.json')
   return next(x for x in value['comparisonShells'] if x['shell']==shell)
  for t in T:
   signed=np.zeros((585,3));triangle=np.zeros((585,3));work=0.;worktri=0.
   for unit in c['terms'][t]['differences']:
    e=unit['element'];shell=unit['id'].split('-')[1];expected_delta=np.array(endpoint(a,e,shell)['localGradientsN'][t])-np.array(endpoint(b,e,shell)['localGradientsN'][t]);close(unit['localDifferenceN'],expected_delta);delta=np.array(unit['localDifferenceN']);nodes=ids[e];np.add.at(signed,nodes,delta);np.add.at(triangle,nodes,abs(delta));w=float(np.sum(delta*direction[nodes]));close(w,unit['directionalDifferenceJ'],1e-9);work+=w;worktri+=abs(w)
   v=c['terms'][t];close(signed,v['aggregateDifferenceN']);close(triangle,v['absoluteUnitDifferenceN']);close(abs(signed).max(),v['aggregateInfinityN'],1e-12);close(triangle.max(),v['unitTriangleInfinityN'],1e-12);close(abs(work),v['aggregateDirectionalDifferenceJ'],1e-12);close(worktri,v['unitTriangleDirectionalDifferenceJ'],1e-12)
   expected=abs(signed).max()<=1e-5 and triangle.max()<=1e-5 and abs(work)<=5.492029235357012e-7 and worktri<=5.492029235357012e-7;assert v['pass']==expected
assert stages==30 and regions==634 and comparisons==8
out={'verdict':'PASS_INDEPENDENT_NONZERO_REGION_GROUP_AND_SCATTER_REPLAY','specimenCalls':0,'stages':stages,'regions':regions,'comparisons':comparisons,'all585IncludingHeld':True,'maximumAbsoluteReplayDifference':maxerr};pathlib.Path('/tmp/selective-independent-nonzero-replay.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
