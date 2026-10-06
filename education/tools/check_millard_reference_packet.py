#!/usr/bin/env python3
"""Audit immutable bindings, CSV force balance/refinement, and preservation scope."""
from pathlib import Path
import hashlib,json,subprocess
import numpy as np
from millard_reference_benchmark import ROOT,OUT,Curve,build_curves
from millard_source_oracle import verified_source


def audit():
    verified_source();manifest=json.loads((OUT/'packet-manifest.json').read_text())
    for rec in manifest['files']:
        data=(ROOT/rec['path']).read_bytes()
        assert len(data)==rec['bytes'] and hashlib.sha256(data).hexdigest()==rec['sha256'], rec['path']
    s=json.loads((OUT/'summary.json').read_text());assert s['passed'] and len(s['checks'])==14 and all(s['checks'].values())
    failed=json.loads((OUT/'failed-coarse-work-summary.json').read_text());assert not failed['passed'] and not failed['checks']['work_balance'] and failed['held_work_quadrature_error_J']>1e-5
    assert s['held_work_quadrature_error_J']<=1e-5 and s['held_coarse_1ms_work_error_J']>1e-5
    C={n:Curve(r) for n,r in build_curves().items()};maximum_balance=maximum_state=maximum_refinement=maximum_tendon=0.
    for mode in ['held','force-plus','force-minus']:
        fine=np.genfromtxt(OUT/f'native-{mode}-fine.csv',delimiter=',',names=True);coarse=np.genfromtxt(OUT/f'native-{mode}-coarse.csv',delimiter=',',names=True);py=np.genfromtxt(OUT/f'python-{mode}.csv',delimiter=',',names=True)
        assert len(fine)==len(coarse)==len(py)
        assert np.max(abs(fine['time']-py['time']))<1e-12 and np.max(abs(fine['time']-coarse['time']))<1e-12
        for field in ['activation','q']:
            maximum_state=max(maximum_state,float(np.max(abs(fine[field]-py[field]))));maximum_refinement=max(maximum_refinement,float(np.max(abs(fine[field]-coarse[field]))))
        for data in [fine,coarse,py]:
            assert np.all(np.isfinite(np.column_stack([data[n] for n in data.dtype.names]))) and np.min(data['q'])>.4441
            for row in data:
                q,a,v,ft=[float(row[n]) for n in ['q','activation','velocity_normalized','tendon_force_N']]
                force=100*(a*C['active'].value(q)*C['velocity'].value(v)+C['passive'].value(q)+.1*v)
                maximum_balance=max(maximum_balance,abs(force-ft))
                expected=100*C['tendon'].value((s['initial_total_length_m']-.1*q)/.2) if mode=='held' else s['force_clamp_N']
                maximum_tendon=max(maximum_tendon,abs(expected-ft))
    assert maximum_balance<=1e-7 and maximum_tendon<=1e-7 and maximum_state<=2e-6 and maximum_refinement<=2e-6
    old='b0d2c11d96a36eed7121a35cfbdda2f85dec2e32'
    changes=subprocess.check_output(['git','diff','--name-status',old],cwd=ROOT,text=True).splitlines()
    assert all(line.startswith('A\t') for line in changes),changes
    protected=['education/book/chapters/00-scope.md','education/tools/contact_trajectory_figure.py']
    protected_hashes={}
    for path in protected:
        old_bytes=subprocess.check_output(['git','show',old+':'+path],cwd=ROOT)
        assert (ROOT/path).read_bytes()==old_bytes,path
        protected_hashes[path]=hashlib.sha256(old_bytes).hexdigest()
    return {'passed':True,'bound_files':len(manifest['files']),'max_recomputed_force_balance_N':maximum_balance,'max_recomputed_tendon_force_N':maximum_tendon,'matched_time_native_Python_error':maximum_state,'native_refinement_error':maximum_refinement,'baseline_preserved':old,'all_tracked_changes_additions':True,'protected_file_sha256':protected_hashes,'failed_work_receipt_retained':True}

if __name__=='__main__':
    r=audit();(OUT/'packet-audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
