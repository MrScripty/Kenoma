"""Verify successor and immutable historical evidence; do not relabel old bindings."""
from pathlib import Path
import gzip,hashlib,json,subprocess,zipfile
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
    inventory=json.loads((BASE/'inventory.json').read_text());assert all(sha(BASE/n)==h for n,h in inventory['files_sha256'].items())
    for row in json.loads((BASE/'compression-record.json').read_text())['files']:
        p=BASE/row['file'];raw=gzip.decompress(p.read_bytes());assert sha(p)==row['compressed_sha256'] and hashlib.sha256(raw).hexdigest()==row['original_sha256'] and len(raw)==row['original_bytes']
    historical=BASE.parent/'connected-passive-specimen';oldinventory=json.loads((historical/'inventory.json').read_text());preserved=json.loads((BASE/'frozen-preservation.json').read_text());assert sha(historical/'inventory.json')==preserved['frozen_inventory_sha256']
    assert all(sha(historical/n)==h for n,h in oldinventory['files_sha256'].items())
    oldmanifest=json.loads((historical/'preview/axisymmetric-preview-manifest.json').read_text())
    for n,h in oldmanifest['input_sha256'].items():assert hashlib.sha256(subprocess.check_output(['git','show','49bf8adf30e1b9bc192e0211f12dfafeb60ede94:education/'+n],cwd=ROOT)).hexdigest()==h
    manifest=json.loads((BASE/'preview/axisymmetric-preview-manifest.json').read_text());assert all(sha(BASE/'preview'/n)==h for n,h in manifest['output_sha256'].items()) and all(sha(ROOT/n)==h for n,h in manifest['input_sha256'].items())
    frozen=json.loads((BASE/'frozen-negative/regression-copy/record.json').read_text());folder=BASE/'frozen-negative/regression-copy'
    assert frozen['five_regressions_failed'] and frozen['status']=='EXPECTED_FROZEN_FAILURE'
    assert all(sha(folder/n)==h for n,h in frozen['inputs'].items()) and sha(folder/'regression.log')==frozen['transcript_sha256']
    assert sha(ROOT/'tests/axisymmetric_end_faces.test.mjs')==frozen['inputs']['tests/axisymmetric_end_faces.test.mjs']
    for n in ['web/axisymmetric-material.mjs','web/axisymmetric-specimen.mjs']:assert frozen['inputs'][n]==oldmanifest['input_sha256'][n]
    tests=json.loads((BASE/'tests/source-bound-test-record.json').read_text());assert tests['status']=='PASS' and tests['count']==18 and all(sha(ROOT/n)==h for n,h in tests['inputs'].items()) and sha(BASE/'tests/18-focused-tests.log')==tests['transcript_sha256']
    affected=json.loads(gzip.decompress((BASE/'numerical/affected-experiment.json.gz').read_bytes()));aq=json.loads((BASE/'numerical/affected-qualification.json').read_text());assert aq['status']=='PASS' and len(aq['cases'])==16 and aq['accepted_axial_count_assignment_cases']==31
    assert all(sha(ROOT/n)==h for n,h in affected['inputs'].items()) and sha(ROOT/'tools/qualify_axisymmetric_end_faces.py')==aq['checker_sha256']
    assert hashlib.sha256(gzip.decompress((BASE/'numerical/affected-experiment.json.gz').read_bytes())).hexdigest()==aq['data_sha256']
    assert sha(BASE/'numerical/independent-material-oracle.json')==aq['independent_oracle_sha256'] and hashlib.sha256(gzip.decompress((historical/'numerical/experiment-final.json.gz').read_bytes())).hexdigest()==aq['frozen_fine_comparison_sha256']
    numerical=json.loads((BASE/'numerical/delivered-qualification.json').read_text());assert numerical['status']=='PASS_BOUNDED_ENGINEERING_CHECKS'
    raw=gzip.decompress((BASE/'numerical/delivered-experiment.json.gz').read_bytes());assert hashlib.sha256(raw).hexdigest()==numerical['experiment_sha256']
    delivered=json.loads(raw);old=json.loads(gzip.decompress((historical/'numerical/experiment-final.json.gz').read_bytes()));assert len(old['cases'])==len(delivered['cases'])==23
    for a,b in zip(old['cases'],delivered['cases']):
        for k in preserved['identical_fields']:assert a[k]==b[k]
    for directory,name,count,test in [('native-browser','axisymmetric-browser-status.json',20,'axisymmetric_browser.py'),('api-browser','axisymmetric-end-face-browser-status.json',16,'axisymmetric_end_faces_browser.py')]:
        receipt=json.loads((BASE/directory/name).read_text());assert receipt['status']=='PASS' and len(receipt['cases'])==count and receipt['preview_manifest_sha256']==sha(BASE/'preview/axisymmetric-preview-manifest.json') and receipt['test_sha256']==sha(ROOT/'tests'/test)
    proof=json.loads((BASE/'proofs/axisymmetric-proof-status.json').read_text());assert proof['status']=='PASS' and len(proof['claims'])==9 and all(sha(ROOT/n)==h for n,h in proof['input_sha256'].items())
    negative=json.loads((BASE/'negatives/axisymmetric-negative-status.json').read_text());assert negative['status']=='PASS_NEGATIVES_REJECTED' and all(sha(ROOT/n)==h for n,h in negative['source_input_sha256'].items())
    for row in negative['cases']:
        folder=BASE/'negatives'/row['case'];m=json.loads((folder/'preview/axisymmetric-preview-manifest.json').read_text());assert all(sha(folder/'preview'/n)==h for n,h in m['output_sha256'].items()) and sha(folder/'browser.log')==row['failure_log_sha256']
    portable=json.loads((BASE/'portable-preview-record.json').read_text());archive=BASE/'connected-end-face-preview.zip';assert sha(archive)==portable['sha256'] and archive.stat().st_size==portable['bytes']
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None and len(z.namelist())==portable['files'] and all(z.read(n)==(BASE/'preview'/n).read_bytes() for n in z.namelist())
    print('PASS successor inventory/source/archive; five frozen failures; 31 cap assignments; 16 affected and 23 unchanged physical states; 20 native +16 API GPU cases; nine fresh Real identities; two negatives; all 120 historical evidence files unchanged')
if __name__=='__main__':verify()
