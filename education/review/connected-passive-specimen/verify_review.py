"""Verify this review's byte bindings and portable delivery; no new solver/proof claim."""
from pathlib import Path
import gzip,hashlib,json,zipfile
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def verify():
    inventory=json.loads((BASE/'inventory.json').read_text())
    assert all(sha(BASE/n)==h for n,h in inventory['files_sha256'].items()),'Review inventory differs'
    compression=json.loads((BASE/'compression-record.json').read_text())
    for row in compression['files']:
        p=BASE/row['file'];raw=gzip.decompress(p.read_bytes())
        assert sha(p)==row['compressed_sha256'] and hashlib.sha256(raw).hexdigest()==row['original_sha256']
        assert len(raw)==row['original_bytes'] and p.stat().st_size==row['compressed_bytes']
    manifest=json.loads((BASE/'preview/axisymmetric-preview-manifest.json').read_text())
    assert all(sha(BASE/'preview'/n)==h for n,h in manifest['output_sha256'].items())
    assert all(sha(ROOT/n)==h for n,h in manifest['input_sha256'].items()),'Current prototype source differs'
    browser=json.loads((BASE/'browser/axisymmetric-browser-status.json').read_text())
    assert browser['status']=='PASS' and len(browser['cases'])==20
    assert sha(BASE/'preview/axisymmetric-preview-manifest.json')==browser['preview_manifest_sha256']
    assert sha(ROOT/'tests/axisymmetric_browser.py')==browser['test_sha256']
    assert sha(BASE/'numerical/material-oracle.json')==browser['oracle_sha256']
    assert hashlib.sha256(gzip.decompress((BASE/'numerical/experiment-browser-oracle.json.gz').read_bytes())).hexdigest()==browser['experiment_sha256']
    numerical=json.loads((BASE/'numerical/qualification.json').read_text())
    assert numerical['status']=='PASS_BOUNDED_ENGINEERING_CHECKS'
    assert hashlib.sha256(gzip.decompress((BASE/'numerical/experiment-final.json.gz').read_bytes())).hexdigest()==numerical['experiment_sha256']
    assert sha(ROOT/'tools/qualify_axisymmetric_experiment.py')==numerical['checker_sha256']
    a=json.loads(gzip.decompress((BASE/'numerical/experiment-browser-oracle.json.gz').read_bytes()));b=json.loads(gzip.decompress((BASE/'numerical/experiment-final.json.gz').read_bytes()))
    assert a['inputs']==b['inputs'] and [x['state'] for x in a['cases']]==[x['state'] for x in b['cases']]
    proof=json.loads((BASE/'proofs/axisymmetric-proof-status.json').read_text());assert proof['status']=='PASS' and len(proof['claims'])==9
    assert all(sha(ROOT/n)==h for n,h in proof['input_sha256'].items())
    assert sha(BASE/'preview/proofs/axisymmetric-proof-status.json')==sha(BASE/'proofs/axisymmetric-proof-status.json')
    negatives=json.loads((BASE/'negatives/axisymmetric-negative-status.json').read_text());assert negatives['status']=='PASS_NEGATIVES_REJECTED' and len(negatives['cases'])==2
    assert all(sha(ROOT/n)==h for n,h in negatives['source_input_sha256'].items())
    for row in negatives['cases']:
        folder=BASE/'negatives'/row['case'];nm=json.loads((folder/'preview/axisymmetric-preview-manifest.json').read_text())
        assert sha(folder/'preview/axisymmetric-preview-manifest.json')==row['delivered_manifest_sha256']
        assert all(sha(folder/'preview'/n)==h for n,h in nm['output_sha256'].items())
        assert sha(folder/'browser.log')==row['failure_log_sha256'] and row['expected_independent_failure'] in (folder/'browser.log').read_text()
    failure=json.loads((BASE/'failures/direct-fine-compression.json').read_text())
    assert not failure['state']['converged'] and all(sha(BASE/'failures/direct-source'/Path(n).name)==h for n,h in failure['sourceHashes'].items())
    portable=json.loads((BASE/'portable-preview-record.json').read_text());archive=BASE/'connected-passive-preview.zip'
    assert sha(archive)==portable['sha256'] and archive.stat().st_size==portable['bytes']
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and len(z.namelist())==portable['files']
        assert set(z.namelist())=={str(p.relative_to(BASE/'preview')) for p in (BASE/'preview').rglob('*') if p.is_file()}
        assert all(z.read(n)==(BASE/'preview'/n).read_bytes() for n in z.namelist())
    print('PASS review inventory, 23 lossless JSON copies, current source bindings, nine proof identities, 20 browser cases, two actual negative bundles, genuine failure source and 17 portable files')
if __name__=='__main__':verify()
