"""Read-only comparison at matched whole-element units, no evaluator imports."""
import pathlib,json,math
E=pathlib.Path('/workspace/Kenoma-patch-material-run/education');M=E/'review/selective-fixed-patch-run-20261007/material'
ref=next(r for r in json.loads((E/'data/anatomical-arm-v1/generated/arm-reference.json').read_text())['muscles'] if r['element_id']=='FJ1486');ids=ref['elements_ten_node'];out=[]
for st in ['control45','terminal46']:
 for a,b in [('Q0','Q1'),('Q1','Q2'),('Q0','Q2')]:
  q=[json.loads((M/f'{st}-{v}-hybrid.json').read_text()) for v in [a,b]];terms={}
  for t in ['matrix','volume','passiveFiber','activePotential','total']:
   bags=[[[] for d in range(3)] for n in range(585)];els=[]
   for ar,br in zip(q[0]['localElements'],q[1]['localElements']):
    e=ar['element'];assert e==br['element'];delta=[[ar['localGradientsN'][t][i][d]-br['localGradientsN'][t][i][d] for d in range(3)] for i in range(10)]
    for i,n in enumerate(ids[e]):
     for d in range(3):bags[n][d].append(delta[i][d])
    els.append({'element':e,'wholeElementInfinityN':max(abs(z) for row in delta for z in row)})
   terms[t]={'common16WholeElementTriangleInfinityN':max(math.fsum(abs(z) for z in bag) for row in bags for bag in row),'perElement':els}
  out.append({'state':st,'a':a,'b':b,'terms':terms})
pathlib.Path('/tmp/selective-material-independent-common-partition.json').write_text(json.dumps(out,indent=2)+'\n')
for z in out:print(z['state'],z['a'],z['b'],z['terms']['total']['common16WholeElementTriangleInfinityN'])
