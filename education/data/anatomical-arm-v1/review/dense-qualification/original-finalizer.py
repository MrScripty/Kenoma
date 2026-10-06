from pathlib import Path
import json,subprocess,time
root=Path('/workspace/Kenoma/education')
base=root/'data/anatomical-arm-v1'
monitor=base/'review/dense-qualification/refinement-replay-monitor.txt'
while True:
    log=monitor.read_text()
    if 'Traceback' in log:raise RuntimeError('Preserved independent replay failure: inspect monitor log')
    if '\nRESULT ' in '\n'+log:break
    time.sleep(10)
for command,name in [(['node','tools/anatomical-dense-matched-times.mjs'],'matched-times-execution.txt'),(['python3','tools/dense_qualification_figure.py'],'refinement-render-execution.txt')]:
    output=base/'review/dense-qualification'/name
    if output.exists():raise RuntimeError('Preserve existing output '+str(output))
    with output.open('w') as stream:subprocess.run(command,cwd=root,stdout=stream,stderr=subprocess.STDOUT,check=True)
    print('FINISHED',name,flush=True)
d=json.loads((base/'audit/anatomical-dense-matched-times.json').read_text())
for r in [*d['comparisons'],d['seedComparison']]:print(json.dumps({k:r[k] for k in ['reference','comparedWith','executionResult','verifiedSteps','lastAcceptedTimeS','matchedCount','maximumAbsoluteAngleDifferenceDeg','maximumNodalDifferenceM']}),flush=True)
print('READY_FOR_BOOK_UPDATE_AND_FINAL_VALIDATION',flush=True)
