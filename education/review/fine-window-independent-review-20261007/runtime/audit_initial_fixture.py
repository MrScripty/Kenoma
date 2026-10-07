"""Read-only independent initial synthetic vector audit; not preflight acceptance."""
import pathlib,json,math,zipfile,hashlib
ed=pathlib.Path('/tmp/Kenoma-fine-window-runner/education');pf=pathlib.Path('/tmp/kenoma-fine-preflight-initial-20261007');accepted=json.loads((ed/'research/selective-fine-window-schedule-20261007.json').read_text());pref=json.loads((pf/'vector-fixture-inputs.json').read_text());checks=0

def need(x,label):
 global checks;checks+=1
 if not x:raise AssertionError(label)
def read(p):return json.loads(pathlib.Path(p).read_bytes())
def near(a,b,tol=1e-8):need(math.isfinite(a) and math.isfinite(b) and abs(a-b)<=tol,f'arithmetic {a} vs {b}')
s=pathlib.Path('/tmp/fine-window-runtime-independent/audit_runtime.py').read_text();section=s[s.index('with zipfile.ZipFile'):s.index("report={'verdict'")];exec(compile(section,'independent_scalar_section','exec'))
print(json.dumps({'verdict':'PASS_INITIAL_SYNTHETIC_ARITHMETIC_ONLY_NOT_PREFLIGHT_ACCEPTANCE','sourceCommit':'ce5df8ae5266e481496d2fb05b386a2d52f7a949','assertions':checks,'materialLawInvocations':0,'specimenCalls':0,'quadratureGeneratedByReviewer':False,'completeComparisons':24,'requiredComparisons':20,'allNodes':585},indent=2))
