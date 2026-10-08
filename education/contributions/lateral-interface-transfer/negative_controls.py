"""Damage actual copied models and require the independent rational audit to fail.

Only private output copies change. No source or anatomical operator is mutated.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
from paths import HERE,checked_output,source_hashes

def run(output):
    out=checked_output(output);original=(HERE/'model.mjs').read_text()
    changes={
      'wrong-interface-denominator':('u=CR*delta/(K1+CR)','u=CR*delta/(K1+2*CR)'),
      'wrong-end-reaction':('leftPullN=upperForceN+leftExchangeN','leftPullN=upperForceN+2*leftExchangeN'),
    }
    rows=[]
    for name,(old,new) in changes.items():
        if original.count(old)!=1:raise RuntimeError('Mutation target must be unique: '+name)
        model=out/(name+'.mjs');model.write_text(original.replace(old,new))
        r=subprocess.run([sys.executable,str(HERE/'check_algebra.py'),'--output',str(out/name),'--model',str(model)],text=True,capture_output=True)
        transcript=r.stdout+r.stderr;(out/(name+'.txt')).write_text(transcript)
        if r.returncode==0 or 'Independent rational case failed' not in transcript:
            raise RuntimeError('Actual damaged model was not detected by independent state audit: '+name)
        rows.append({'mutation':name,'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),
          'exit_code':r.returncode,'detected_by':'Independent rational case failed'})
    (out/'negative-controls.json').write_text(json.dumps({'status':'passed','controls':rows,'source_sha256':source_hashes(),
      'scope':'Two actual copied model defects rejected; this is no anatomical or general mutation-coverage claim.'},indent=2)+'\n')
    print('Two actual damaged models failed the independent rational audit as required.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output)
