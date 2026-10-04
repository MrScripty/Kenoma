#!/usr/bin/env python3
"""Deterministic preparation of independently sourced educational evidence.
Usage: python3 scripts/prepare_data.py --openarm-archive /path/time_series.zip
After initial extraction, omit the argument to regenerate from cleaned CSV.
"""
import argparse,csv,hashlib,json,math,pathlib,statistics,xml.etree.ElementTree as ET,zipfile
from collections import defaultdict,Counter
from read_openarm_safely import read_passive
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)
REV='84b487c4e3245359a64381e01f01b9cf4772d457'
ARMURL=f'https://github.com/opensim-org/opensim-models/blob/{REV}/Models/Arm26/arm26.osim'
OPENARM_HASH='7d3acb811e4bbdc6846cb3434b66d6c56d99f26db8bfc672e9da9e41b856d560'
FIELDS=['elapsed_s','brachioradialis_thickness_normalized_1','biceps_semg_normalized_1','wrist_contact_force_normalized_1']
def writejson(path,obj,compact=False): path.write_text(json.dumps(obj,ensure_ascii=False,indent=None if compact else 2,allow_nan=False)+'\n')
def writecsv(path,fields,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def hashfile(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def arm26():
    source=ROOT/'sources/arm26.osim'; root=ET.parse(source).getroot();model=root.find('Model')
    mapping={'TRIlong':'triceps brachii long head','TRIlat':'triceps brachii lateral head','TRImed':'triceps brachii medial head','BIClong':'biceps brachii long head','BICshort':'biceps brachii short head','BRA':'brachialis'}
    specs={'max_isometric_force':('N','Peak isometric actuator force parameter, not a measured subject force'), 'optimal_fiber_length':('m','Actuator optimal fiber length parameter'), 'tendon_slack_length':('m','Actuator tendon slack length parameter'), 'pennation_angle_at_optimal':('rad','Fiber pennation angle at optimal fiber length'), 'activation_time_constant':('s','Actuator activation time constant'), 'deactivation_time_constant':('s','Actuator deactivation time constant')}
    rows=[]; muscles=[]
    for m in model.find('ForceSet/objects'):
        record={'name':m.attrib['name'],'anatomical_label':mapping[m.attrib['name']], 'actuator_type':m.tag,'parameters':{}}
        for field,(unit,meaning) in specs.items():
            value=float(m.findtext(field)); xp=f"/OpenSimDocument/Model/ForceSet/objects/{m.tag}[@name='{m.attrib['name']}']/{field}"
            record['parameters'][field]={'value':value,'unit':unit,'meaning':meaning,'evidence_class':'model_parameter','source_xpath':xp}
            rows.append({'actuator':m.attrib['name'],'anatomical_label':record['anatomical_label'],'parameter':field,'value':value,'unit':unit,'evidence_class':'model_parameter','source_revision':REV,'source_xpath':xp})
        muscles.append(record)
    coords=[]
    for c in model.findall('.//Coordinate'):
        coords.append({'name':c.attrib['name'],'default_value_rad':float(c.findtext('default_value')), 'range_rad':[float(x) for x in c.findtext('range').split()], 'evidence_class':'model_coordinate_limit_not_clinical_range'})
    result={'schema_version':'1.0','source_url':ARMURL,'source_sha256':hashfile(source),'license':'CC-BY-3.0','credits':model.findtext('credits'),'evidence_class':'model_parameters','clinical_validation':False,'registered_to_other_assets':False,'muscles':muscles,'coordinates':coords,'limits':['No separate brachioradialis actuator','No continuum tissue, skin, fascia, contact-pressure, or tendon-strain measurement','These model parameters are not subject-specific measured data','No activation is inferred from pose; no kinematic or mechanics solver is implemented here']}
    writejson(DATA/'arm26_parameters.json',result); writecsv(DATA/'arm26_parameters.csv',list(rows[0]),rows)
    return result

def atlas():
    members=json.loads((ROOT/'audit/bodyparts_subset_members.json').read_text()); parts=[]
    for member in members:
        p=ROOT/'sources/bodyparts3d'/(member['element file id']+'.obj'); vertices=[]; faces=[]
        for line in p.read_text().splitlines():
            if line.startswith('v '):vertices.append([float(x)*0.001 for x in line.split()[1:4]])
            elif line.startswith('f '):
                a=[int(x.split('/')[0])-1 for x in line.split()[1:]]
                if len(a)!=3:raise ValueError('Non-triangle; do not silently change topology')
                faces.append(a)
        assert vertices and faces and all(math.isfinite(v) for x in vertices for v in x) and all(0<=v<len(vertices) for x in faces for v in x)
        bounds=[[min(v[d] for v in vertices) for d in range(3)],[max(v[d] for v in vertices) for d in range(3)]]
        # Count boundary/nonmanifold edges without claiming watertight clinical geometry.
        counts=Counter(tuple(sorted((f[i],f[(i+1)%3]))) for f in faces for i in range(3))
        weld={}; ix=[]
        for v in vertices:
            key=tuple(v)
            if key not in weld:weld[key]=len(weld)
            ix.append(weld[key])
        wc=Counter(tuple(sorted((ix[f[i]],ix[f[(i+1)%3]]))) for f in faces for i in range(3))
        parts.append({'concept_id':member['concept id'],'element_id':member['element file id'],'name':member['name'],'source_obj':'sources/bodyparts3d/'+p.name,'source_sha256':hashfile(p),'vertices_m':vertices,'triangles_zero_based':faces,'bounds_m':bounds,'vertex_count':len(vertices),'triangle_count':len(faces),'raw_index_boundary_edge_count':sum(v==1 for v in counts.values()),'raw_index_nonmanifold_edge_count':sum(v>2 for v in counts.values()),'exact_coordinate_unique_vertices':len(weld),'exact_coordinate_boundary_edges':sum(v==1 for v in wc.values()),'exact_coordinate_nonmanifold_edges':sum(v>2 for v in wc.values()),'edge_count_caveat':'Exact-coordinate welding is diagnostic only; output topology is unchanged and no watertightness or orientation guarantee is made'})
    result={'schema_version':'1.0','source':'BodyParts3D 4.0, IS-A archive, 99% polygon reduction release','evidence_class':'constructed_anatomical_reference_atlas','length_unit':'m','coordinate_axes':{'x_positive':'anatomical left','y_positive':'posterior','z_positive':'superior'},'transform_from_source':'x_m = x_mm / 1000; y_m = y_mm / 1000; z_m = z_mm / 1000','license':'CC-BY-4.0','source_coordinate_evidence':'https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20130619/coordinate_system.png','registered_to_other_assets':False,'clinical_validation':False,'mesh_adaptations':['Converted vertex positions from millimetres to metres','Converted face indices from one-based to zero-based','No topology change; no smoothing, decimation, centering, joint fitting, rigging or remeshing','Source vertex normals are omitted from JSON; original OBJ retains normals if present'],'limitations':['Static reference atlas, not scanned geometry for OpenArm participant 2','No validated elbow axis, local frames, moment arms or rest-pose binding','No skin, fat, fascia, cartilage, nerve or tendon material field supplied','Atlas release may contain anatomical errors; 99% polygon-reduced surfaces are not appropriate for clinical contact mechanics'],'parts':parts}
    writejson(DATA/'bodyparts3d_right_arm_m.json',result,True)
    writejson(DATA/'bodyparts3d_mesh_summary.json',{k:v for k,v in result.items() if k!='parts'}|{'parts':[{k:v for k,v in p.items() if k not in ('vertices_m','triangles_zero_based')} for p in parts]})
    return result

def openarm(archive):
    rawpath=DATA/'openarm_s2_1b_normalized_samples.csv'
    meta_path=DATA/'openarm_s2_1b_metadata.json'
    if archive:
        archive=pathlib.Path(archive);assert hashfile(archive)==OPENARM_HASH
        with zipfile.ZipFile(archive) as z:
            entry='time_series/2/trial_1b.p'; b=z.read(entry); info=z.getinfo(entry)
        d=read_passive(b);n=len(d['Times']);assert n==6068
        assert all(len(v)==n for v in d['Processed'])
        start=d['Traj-Changes'][1]-700;assert start==1665
        t0=d['Times'][start];rows=[]
        for i in range(start,n):
            t=d['Times'][i]-t0
            vals=[t,*[d['Processed'][k][i] for k in (0,1,2)]]
            assert all(isinstance(x,(int,float)) and math.isfinite(x) for x in vals)
            rows.append(dict(zip(FIELDS,vals)))
        assert all(rows[i]['elapsed_s']>rows[i-1]['elapsed_s'] for i in range(1,len(rows)))
        writecsv(rawpath,FIELDS,rows)
        intervals=[rows[i]['elapsed_s']-rows[i-1]['elapsed_s'] for i in range(1,len(rows))]
        meta={'schema_version':'1.0','dataset':'OpenArm Multisensor 2.0','source_archive_url':'https://drive.google.com/uc?export=download&id=1cOy5-Ws4SJWD4O1WK-iw36ExDsP5Y2O8','source_archive_bytes':archive.stat().st_size,'source_archive_sha256':OPENARM_HASH,'source_member':entry,'source_member_bytes':len(b),'source_member_crc32':f'{info.CRC:08x}','source_member_sha256':hashlib.sha256(b).hexdigest(),'license':'CC-BY-4.0','evidence_class':'recorded_preprocessed_normalized_human_research_signals','participant_code':'2','trial_label':'1b','trial_meaning':'Second force-target correlation trial','posture':'Right elbow held at 90 degrees flexion, forearm fully supinated','elbow_angle_measured_timeseries_included':False,'acquisition_nominal_rate_hz':1000,'retained_samples':len(rows),'retained_start_index_zero_based':start,'original_trial_samples':n,'relative_time_origin':'Times[1665] subtracted from each retained Times entry; absolute timestamps omitted','duration_s':rows[-1]['elapsed_s'],'observed_mean_saved_rate_hz':(len(rows)-1)/rows[-1]['elapsed_s'],'observed_median_saved_interval_s':statistics.median(intervals),'normalization':'Source retained Processed values used directly; original calibration defined (signal - relaxed_mean)/(MVC_mean - relaxed_mean). No second normalization, clipping or physical unit inference.','columns':{FIELDS[0]:{'unit':'s','meaning':'Elapsed time from first retained sample'},FIELDS[1]:{'unit':'1','meaning':'Source Processed[0], ultrasound-derived brachioradialis thickness, trial-calibrated'},FIELDS[2]:{'unit':'1','meaning':'Source Processed[1], biceps brachii sEMG amplitude, preprocessed and trial-calibrated; not direct activation or force'},FIELDS[3]:{'unit':'1','meaning':'Source Processed[2], wrist-contact force, trial-calibrated; not individual-muscle force or elbow torque'}},'display_aggregation':{'bin_width_s':0.5,'bin_interval':'[start,end); arithmetic mean of retained samples in each bin; final bin may be partial','weighting':'sample-weighted, not time-weighted','error_bar':'none; no between-participant uncertainty inferred','plot_rate_hz':2},'source_analysis_revision':'ae635da29c722269edff8936bba6aff864e9688f','source_analysis_path':'multisensorimport/dataobj/trialdata.py','paper_doi':'10.1109/TNSRE.2021.3133813','errata':'No subject-2 exception listed in supplied errata','source_calibration_extrema_retained':False,'absolute_timestamps_included':False,'demographics_included':False,'registered_to_atlas_or_arm26':False,'limits':['Single coded research participant and trial; no population or clinical claim','Ultrasound and sEMG measure different muscles','Amplitudes have SI dimensionless unit 1; N, m, and V conversions are not justified','Nonuniform saved times, no assumption of exact 1 kHz sampling','Binned display not intended for spectral, latency, causality or parameter-fitting analysis','Not an exact recreation of published analysis due to time-origin and binning choices','No unique activation, force-sharing, 3D deformation, tendon strain, skin contact or injury estimate']}
        writejson(meta_path,meta)
    else:
        with rawpath.open() as f:rows=[{k:float(v) for k,v in r.items()} for r in csv.DictReader(f)]
        meta=json.loads(meta_path.read_text())
    buckets=defaultdict(list)
    for row in rows:buckets[int(row['elapsed_s']//0.5)].append(row)
    bins=[]
    for i,vs in sorted(buckets.items()):
        r={'bin_start_s':i*0.5,'bin_end_s':(i+1)*0.5,'sample_count':len(vs),'mean_elapsed_s':statistics.mean(x['elapsed_s'] for x in vs)}
        for col in FIELDS[1:]:r[col+'_mean']=statistics.mean(x[col] for x in vs)
        bins.append(r)
    writecsv(DATA/'openarm_s2_1b_0p5s_bins.csv',list(bins[0]),bins)
    writejson(DATA/'openarm_s2_1b_0p5s_bins.json',{'metadata_file':'openarm_s2_1b_metadata.json','columns':list(bins[0]),'rows':bins},True)
    meta['display_bins']=len(bins);writejson(meta_path,meta)
    return rows,bins,meta

def main():
    p=argparse.ArgumentParser();p.add_argument('--openarm-archive');args=p.parse_args()
    a=arm26();m=atlas();r,b,meta=openarm(args.openarm_archive)
    print(json.dumps({'arm26_actuators':len(a['muscles']),'atlas_parts':len(m['parts']),'atlas_vertices':sum(p['vertex_count'] for p in m['parts']),'atlas_triangles':sum(p['triangle_count'] for p in m['parts']),'recorded_samples':len(r),'display_bins':len(b),'duration_s':meta['duration_s'],'observed_mean_saved_rate_hz':meta['observed_mean_saved_rate_hz']},indent=2))
if __name__=='__main__':main()
