#!/usr/bin/env python3
"""Structural and provenance checks; no clinical claims."""
import csv,hashlib,json,math,pathlib,sys,xml.etree.ElementTree as ET
from read_openarm_safely import read_passive
ROOT=pathlib.Path(__file__).resolve().parents[1]
def run():
    checks=[]
    def require(condition,label):
        if not condition:raise AssertionError(label)
        checks.append(label)
    a=json.loads((ROOT/'data/arm26_parameters.json').read_text())
    require(a['source_sha256']=='e2224d0044eb393b05d64926c3fa1682c451a9adc7f510e5517ef9958d3d41b9','Pinned Arm26 byte hash')
    xml=ET.parse(ROOT/'sources/arm26.osim')
    require(len(a['muscles'])==6,'Exactly six Arm26 actuators')
    for m in a['muscles']:
        for name,p in m['parameters'].items():
            node=xml.find(f"Model/ForceSet/objects/Thelen2003Muscle[@name='{m['name']}']/{name}")
            require(p['value']==float(node.text),f"Source parameter exact: {m['name']}/{name}")
    atlas=json.loads((ROOT/'data/bodyparts3d_right_arm_m.json').read_text())
    require(len(atlas['parts'])==10,'Ten atlas parts')
    for p in atlas['parts']:
        raw=(ROOT/p['source_obj']).read_bytes()
        require(hashlib.sha256(raw).hexdigest()==p['source_sha256'],f"Source OBJ hash {p['element_id']}")
        original=[list(map(float,line.split()[1:4])) for line in raw.decode().splitlines() if line.startswith('v ')]
        require(all(x*.001==y for a,b in zip(original,p['vertices_m']) for x,y in zip(a,b)),f"SI conversion exact {p['element_id']}")
        require(all(0<=i<len(p['vertices_m']) for tri in p['triangles_zero_based'] for i in tri),f"Face bounds {p['element_id']}")
        require(p['exact_coordinate_boundary_edges']==0 and p['exact_coordinate_nonmanifold_edges']==0,f"Exact-coordinate edge diagnostic {p['element_id']}")
    with (ROOT/'data/openarm_s2_1b_normalized_samples.csv').open() as f:rows=list(csv.DictReader(f))
    with (ROOT/'data/openarm_s2_1b_0p5s_bins.csv').open() as f:bins=list(csv.DictReader(f))
    require(len(rows)==4403 and len(bins)==172,'Recorded and display row counts')
    require(set(rows[0])=={'elapsed_s','brachioradialis_thickness_normalized_1','biceps_semg_normalized_1','wrist_contact_force_normalized_1'},'Only normalized signals and relative time exported')
    require(all(math.isfinite(float(v)) for r in rows for v in r.values()),'Finite recorded data')
    require(float(rows[0]['elapsed_s'])==0 and all(float(b['elapsed_s'])>float(a['elapsed_s']) for a,b in zip(rows,rows[1:])),'Strictly increasing relative time')
    require(sum(int(b['sample_count']) for b in bins)==len(rows),'All recorded samples accounted in bins')
    for b in bins:
        vs=[r for r in rows if float(b['bin_start_s'])<=float(r['elapsed_s'])<float(b['bin_end_s'])]
        require(len(vs)==int(b['sample_count']),f"Bin count at {b['bin_start_s']}")
        for col in rows[0]:
            key='mean_elapsed_s' if col=='elapsed_s' else col+'_mean'
            require(math.isclose(float(b[key]),sum(float(r[col]) for r in vs)/len(vs),rel_tol=1e-12,abs_tol=1e-12),f"Bin mean {b['bin_start_s']}/{col}")
    # Data-only interpreter must reject executable GLOBAL and unknown opcodes.
    for payload in (b'cos\nsystem\n.',b'\x80\x05\x8c\x02os\x8c\x06system\x93.'):
        rejected=False
        try:read_passive(payload)
        except ValueError:rejected=True
        require(rejected,'Unsafe symbolic global rejected')
    manifest=ROOT/'provenance.json'
    if manifest.exists():
        for item in json.loads(manifest.read_text())['files']:
            p=ROOT/item['path'];require(p.stat().st_size==item['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],'Manifest hash '+item['path'])
    print(json.dumps({'result':'PASS','checks':len(checks),'clinical_validation':False,'note':'Structural/data/provenance checks only; figures separately visually inspected.'},indent=2))
if __name__=='__main__':run()
