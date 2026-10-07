"""Proposal arithmetic from retained JSON only; no model imports or material calls."""
import hashlib, json, pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
ANCHOR = 'f7cc2c0f10b536e94557ce978aa1691d6c92246f'
inventory = {}
def read(name):
    data = (ROOT / name).read_bytes()
    frozen = subprocess.check_output(['git', 'cat-file', 'blob', f'{ANCHOR}:education/{name}'], cwd=ROOT)
    assert data == frozen, name
    inventory[name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    return json.loads(data)

OLD = 'review/fixed-field-integration-run-20261007/'
arrays = read(OLD + 'saved-arrays.json')
source = next(s for s in read('data/anatomical-arm-v1/generated/arm-reference.json')['muscles'] if s['element_id'] == 'FJ1486')
patch = arrays['patchElements']
secondary = [197, 200, 203, 206, 246, 248]
quiet = [e for e in patch if e not in secondary + [247]]
assert patch == [195,196,197,198,199,200,202,203,206,237,240,243,244,246,247,248]
assert quiet == [195,196,198,199,202,237,240,243,244]
terms = ['matrix', 'volume', 'passiveFiber', 'activePotential', 'total']
rules = ['U4', 'U5', 'D4', 'D5']
pairs = [('U4','U5'), ('D4','D5'), ('U5','D5')]
records = {(st,rule,e): read(OLD + f'{rule}-{st}-element-{e}-local.json') for st in ['control45','terminal46'] for rule in rules for e in patch}
for st in ['control45','terminal46']:
    for name in ['U3','U4','U5','D4','D5']:
        read(OLD + f'{name}-{st}-assembly.json')

def compare(st,a,b,elements):
    result = {}
    for term in terms:
        aggregate = [[0.,0.,0.] for _ in range(585)]
        triangle = [[0.,0.,0.] for _ in range(585)]
        work, work_triangle = 0., 0.
        for e in elements:
            ar, br = records[st,a,e], records[st,b,e]
            w = 0.
            for i,n in enumerate(source['elements_ten_node'][e]):
                for d in range(3):
                    x = ar['localGradientsN'][term][i][d] - br['localGradientsN'][term][i][d]
                    aggregate[n][d] += x
                    triangle[n][d] += abs(x)
                    w += x * arrays['terminalDirectionM'][n][d]
            work += w
            work_triangle += abs(w)
        result[term] = {'aggregateInfinityN': max(abs(x) for row in aggregate for x in row), 'elementTriangleInfinityN': max(x for row in triangle for x in row), 'aggregateWorkJ': abs(work), 'elementWorkTriangleJ': work_triangle}
    return result

per_element = {st: {str(e): {'localCornerAtNode92': source['elements_ten_node'][e].index(92), 'minimumRetainedSampleJ': min(records[st,r,e]['minimumSampleJ'] for r in rules), 'comparisons': {a+'-'+b: compare(st,a,b,[e]) for a,b in pairs}} for e in patch} for st in ['control45','terminal46']}
subsets = {st: {label: {a+'-'+b: compare(st,a,b,es) for a,b in pairs} for label,es in [('quiet9',quiet),('secondary6',secondary),('all15Except247',[e for e in patch if e!=247]),('full16',patch)]} for st in ['control45','terminal46']}
full = read(OLD+'completion-receipt.json')
execution = read(OLD+'execution-receipt.json')
shell = read('review/element247-shell-run-outcome-20261007/result-summary.json')
incomplete = read('review/element247-two-shell-run-20261007/material/incomplete-receipt.json')
recovered = read('review/element247-two-shell-reconstructed-20261007/reconstructed-diagnostic.json')
read('review/element247-two-shell-reconstructed-20261007/independent-review.json')
for name in ['tools/element247-two-shell-schema.mjs', 'tools/element247-shell-protocol.mjs', 'tools/fixed-field-integration-protocol.mjs', 'tools/element247_shell_execution.py', 'tests/element247_two_shell.test.mjs']:
    data=(ROOT/name).read_bytes()
    assert data==subprocess.check_output(['git','cat-file','blob',f'{ANCHOR}:education/{name}'],cwd=ROOT)
    inventory[name]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}

schedule = [
    {'rule':'Secondary C55', 'elements':6, 'pointsPerElementPerField':21*125, 'fields':2, 'reusedMaterialValues':0},
    {'rule':'Secondary A55', 'elements':6, 'pointsPerElementPerField':21*125*4, 'fields':2, 'reusedMaterialValues':0},
    {'rule':'247 F44', 'elements':1, 'pointsPerElementPerField':21*125*16, 'fields':2, 'reusedMaterialValues':4000},
    {'rule':'247 R44', 'elements':1, 'pointsPerElementPerField':21*125*16*2, 'fields':2, 'reusedMaterialValues':0},
    {'rule':'247 X44', 'elements':1, 'pointsPerElementPerField':23*125*16, 'fields':2, 'reusedMaterialValues':0}
]
for row in schedule:
    row['newCallbacks']=row['elements']*row['pointsPerElementPerField']*row['fields']-row['reusedMaterialValues']
calls=sum(r['newCallbacks'] for r in schedule)
assert calls==497500
timing_anchors = {
    'fullPatchExternalSecondsPerCallback': execution['elapsedSeconds']/8847360,
    'shellPublicSupervisorSecondsPerCallback': shell['launcherExit']['elapsedMs']/1000/62438,
    'smallChangedBatchRuntimeSecondsPerCallback': incomplete['runtime']['elapsedMs']/1000/4000
}
cost = {'schedule':schedule, 'newCallbacks':calls, 'savedVsOriginalFullPatchPercent':100*(1-calls/8847360), 'timeAnchorsSecondsPerCallback':timing_anchors, 'directTimeExtrapolationSeconds':{name:calls*rate for name,rate in timing_anchors.items()}, 'planningWallSeconds':[20,180], 'proposedHardWallSeconds':300, 'proposedMaximumCalls':calls, 'proposedNodeHeapMiB':1024, 'proposedRssBytes':2*1024**3, 'proposedOutputCeilingBytes':64*1024**2}
cost['newUniquePhysicalWeightBytes']=8*(6*(2625+10500)+42000+84000+46000)
cost['normalizedRuleBytesIncludingFourSecondaryCornerPermutations']=48*(4*(2625+10500)+42000+84000+46000)
cost['rawBinaryBytes']=cost['newUniquePhysicalWeightBytes']+cost['normalizedRuleBytesIncludingFourSecondaryCornerPermutations']
cost['planningNewArtifactBytesRange']=[20*1024**2,32*1024**2]
cost['logicalShellRecordsBothFields']=2*(6*2*21+21+21+23)
assert cost['rawBinaryBytes']==12782000 and cost['logicalShellRecordsBothFields']==634
result = {'result':'PROPOSAL_RETAINED_ARITHMETIC_ONLY_NOT_PREFLIGHT_OR_QUALIFICATION','anchorCommit':ANCHOR,'newMaterialCalls':0,'newSpecimenCalls':0,'newQuadratureGenerated':False,'independentlyReviewed':False,'patchElements':patch,'quiet9':quiet,'secondary6':secondary,'perElement':per_element,'subsetComparisons':subsets,'cost':cost,'sourceAnchors':{'fullPatchResult':'74054f5c611c57c0b9ddb1fd77a9aaba20ee9c8b','whole247Result':'4b83ec5dfebae73b08c3f964aa910f65e02458e0','failedTwoShellResult':'9c9edbc9f3dd9729f2becc5215054897d139735e','reconstructedResult':ANCHOR,'reviewedReconstructionSource':'1671433376014ad148799e1ad7ff3f10219643f7'},'originalResults':{'fullPatch':full['result'],'whole247':shell['result'],'twoShellExecutionIncomplete':True,'reconstructedOperationalCompletion':recovered['operationalCompletion']},'inputInventory':inventory}
print(json.dumps(result,indent=2))
