"""Losslessly archive large exact coefficients; retain a small source-bound index."""
from pathlib import Path
import gzip,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/anatomical-arm-v1/audit'
def digest(b):return hashlib.sha256(b).hexdigest()
def package():
    raw_path=BASE/'anatomical-trajectory-orientation.json'
    raw=raw_path.read_bytes();receipt=json.loads(raw)
    assert receipt['result']=='PASS_EXACT_STORED_P2_ORIENTATION'
    rows=[];count=0
    for row in receipt['rows']:
        heads=[]
        for head in row['heads']:
            for element in head['elements']:
                assert element['orientationCertified']
                for kind in ['reference','current']:
                    c=element[kind]
                    assert len(c['coefficients'])==20
                    values=[int(v['numerator']) for v in c['coefficients']]
                    assert min(values)==int(c['minimumNumerator'])>0
                    assert max(values)==int(c['maximumNumerator'])
                count+=1
            heads.append({k:v for k,v in head.items() if k!='elements'})
        rows.append({**row,'heads':heads})
    archive=gzip.compress(raw,compresslevel=9,mtime=0)
    assert gzip.decompress(archive)==raw
    name='anatomical-trajectory-orientation-full.json.gz'
    (BASE/name).write_bytes(archive)
    summary={**receipt,'rows':rows,'certifiedElementCount':count,'fullReceiptSHA256':digest(raw),'archive':name,'archiveSHA256':digest(archive),'sourceHashes':{**receipt['sourceHashes'],'tools/package_anatomical_orientation.py':digest(Path(__file__).read_bytes())}}
    (BASE/'anatomical-trajectory-orientation-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    # All bytes are recoverable from the checked archive, below the hosting blob limit.
    raw_path.unlink()
    print(json.dumps({'result':summary['result'],'certifiedElementCount':count,'rawBytes':len(raw),'archiveBytes':len(archive),'archiveSHA256':summary['archiveSHA256'],'fullReceiptSHA256':summary['fullReceiptSHA256']}))
if __name__=='__main__':package()
