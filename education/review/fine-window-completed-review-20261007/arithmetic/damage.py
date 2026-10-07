"""In-memory damage tests for the independent replay; stored bytes are untouched."""
import ast, copy, json, pathlib
path=pathlib.Path('/tmp/fine-window-completed-arithmetic-independent/review.py')
tree=ast.parse(path.read_text());prefix=[]
for item in tree.body:
    if isinstance(item,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='started' for x in item.targets):break
    prefix.append(item)
ns={};exec(compile(ast.Module(body=prefix,type_ignores=[]),str(path),'exec'),ns)
ed=ns['ED'];mat=ns['MAT'];read=ns['read'];arrays=read(mat/'saved-arrays.json')
source=next(x for x in read(ed/'data/anatomical-arm-v1/generated/arm-reference.json')['muscles'] if x['element_id']=='FJ1486')
ns['ids']=source['elements_ten_node'];ns['direction']=arrays['terminalDirectionM']
units=[]
for e in ns['PATCH']:
    if e in ns['QUIET']:
        units.append((f'{e}-whole',ns['retained']('terminal46',e,'U4'),ns['retained']('terminal46',e,'U5')))
    else:
        a=read(mat/f'terminal46-{e}-I0-stage.json');b=read(mat/f'terminal46-{e}-I1-stage.json')
        for ar,br in zip(a['comparisonShells'],b['comparisonShells']):units.append((f'{e}-{ar["shell"]}',{**ar,'element':e},{**br,'element':e}))
original=read(mat/'terminal46-I0-I1-comparison.json')
result,terms=ns['compare'](original,units);assert result is False
def gate(c):c['terms']['volume']['forceGateN']=1e-4
def workgate(c):c['terms']['volume']['workGateJ']=1e-3
def falsepass(c):c['terms']['volume']['pass']=True
def unitomission(c):c['terms']['volume']['differences'].pop()
def local(c):c['terms']['volume']['differences'][0]['localDifferenceN'][0][0]+=1e-4
def work(c):c['terms']['volume']['differences'][0]['directionalDifferenceJ']+=1e-4
def triangle(c):c['terms']['volume']['absoluteUnitDifferenceN'][0][0]+=1e-4
def held(c):c['terms']['total']['aggregateDifferenceN'][arrays['heldNodeOrder'][0]][0]+=1e-4
def nonfinite(c):c['terms']['total']['aggregateDifferenceN'][0][0]=float('nan')
def scalar(c):c['terms']['total']['aggregateInfinityN']=0
results=[]
for mutate in [gate,workgate,falsepass,unitomission,local,work,triangle,held,nonfinite,scalar]:
    c=copy.deepcopy(original);mutate(c)
    try:ns['compare'](c,units)
    except (AssertionError,ValueError) as error:results.append({'case':mutate.__name__,'verdict':'REFUSED','reason':str(error)})
    else:raise AssertionError('Damage accepted: '+mutate.__name__)
report={'verdict':'PASS_10_IN_MEMORY_DAMAGE_REFUSALS','specimenCalls':0,'quadratureGenerationCalls':0,'storedInputWrites':0,'cases':results}
(path.parent/'damage.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
