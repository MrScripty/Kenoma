#!/usr/bin/env python3
import hashlib,json,pathlib,platform
ROOT=pathlib.Path(__file__).resolve().parents[1]
ARMREV='84b487c4e3245359a64381e01f01b9cf4772d457'
SOURCES=[
 {'id':'bodyparts3d','title':'BodyParts3D 4.0 IS-A 99% polygon-reduced release','evidence_class':'constructed_anatomical_reference_atlas','license':'CC-BY-4.0','license_url':'https://creativecommons.org/licenses/by/4.0/','license_authority':'https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html','license_authority_updated':'2025-02-27','historical_embedded_notice':'CC-BY-SA-2.1-JP remains in original OBJ; current official archive grant is CC-BY-4.0','archive_url':'https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip','archive_bytes':142903898,'archive_sha256':None,'full_archive_downloaded':False,'verification':'HTTP range selection; member size and central-directory CRC32 validation; member SHA256 recorded','coordinate_units_source':'https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20130619/coordinate_system.png','attribution':'BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International.','spatial_registration_to_other_sources':None},
 {'id':'openarm','title':'OpenArm Multisensor 2.0 participant 2 trial 1b','evidence_class':'recorded_preprocessed_normalized_human_research_signals','license':'CC-BY-4.0','license_url':'https://creativecommons.org/licenses/by/4.0/','license_authority':'sources/openarm_readme.md','provider':'https://simtk.org/frs/?group_id=1617','doi':'10.1109/TNSRE.2021.3133813','archive_url':'https://drive.google.com/uc?export=download&id=1cOy5-Ws4SJWD4O1WK-iw36ExDsP5Y2O8','archive_sha256':'7d3acb811e4bbdc6846cb3434b66d6c56d99f26db8bfc672e9da9e41b856d560','archive_bytes':10269052,'source_member':'time_series/2/trial_1b.p','original_pickle_distributed':False,'code_interpretation_revision':'ae635da29c722269edff8936bba6aff864e9688f','code_interpretation_url':'https://github.com/lhallock/openarm-multisensor/blob/ae635da29c722269edff8936bba6aff864e9688f/multisensorimport/dataobj/trialdata.py#L70-L147','code_bundled':False,'spatial_registration_to_other_sources':None},
 {'id':'arm26','title':'Arm26 OpenSim model','evidence_class':'model_parameters','license':'CC-BY-3.0','license_url':'https://creativecommons.org/licenses/by/3.0/','license_authority':'Embedded credits of source XML','revision':ARMREV,'path':'Models/Arm26/arm26.osim','url':f'https://github.com/opensim-org/opensim-models/blob/{ARMREV}/Models/Arm26/arm26.osim','git_blob_sha1':'2ff458149668bb2f0de24572f80658f8dd9db1d9','sha256':'e2224d0044eb393b05d64926c3fa1682c451a9adc7f510e5517ef9958d3d41b9','spatial_registration_to_other_sources':None}
]
def category(p):
 s=str(p)
 if s.startswith('scripts/'):return 'original_processing_code','MIT',[]
 if 'arm26' in s:return 'model_parameters_or_source','CC-BY-3.0',['arm26']
 if 'openarm' in s:return 'recorded_data_or_source_documentation','CC-BY-4.0',['openarm']
 if 'bodyparts' in s:return 'anatomical_atlas_or_source_documentation','CC-BY-4.0',['bodyparts3d']
 return 'original_documentation_or_audit','component-specific',['bodyparts3d','openarm','arm26']
def main():
 paths=[]
 for sub in ('data','figures','sources','scripts','audit'):
  paths.extend(p for p in (ROOT/sub).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='bodyparts_zip_tail.bin')
 paths.extend(ROOT/p for p in ('README.txt','LICENSES_AND_ATTRIBUTION.txt','FIGURE_CAPTIONS.txt'))
 files=[]
 for p in sorted(paths):
  rel=p.relative_to(ROOT);c,lic,src=category(rel)
  files.append({'path':str(rel),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'evidence_class':c,'license':lic,'source_ids':src})
 manifest={'schema_version':'1.0','title':'Kenoma elbow anatomical and biomechanical evidence package','prepared_utc':'2026-10-04','intended_use':'Education and research; independent anatomy, measurement and model evidence','clinical_validation':False,'subject_specific_calibration':False,'sources':SOURCES,'transformations':{'bodyparts3d':'Select ten original meshes; verify member CRC; mm to m; one-based to zero-based triangle indices; no topology change','openarm':'Passive pickle opcode translation; select source participant 2 trial 1b from index1665; use normalized Processed streams directly; remove absolute time and unrelated fields; arithmetic half-second display-bin means','arm26':'XML extraction of six SI parameter types per actuator and coordinate bounds, unchanged numeric values'},'files':files,'runtime':{'python':platform.python_version()},'reproducibility':'Run prepare_data.py from bundled original atlas/model sources and cleaned recorded CSV. Original OpenArm re-extraction accepts external exact-hash archive. Figures require NumPy and Matplotlib.'}
 try:
  import numpy,matplotlib
  manifest['runtime'].update(numpy=numpy.__version__,matplotlib=matplotlib.__version__)
 except ImportError:pass
 (ROOT/'provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 print(len(files),'payload files',sum(f['bytes'] for f in files),'bytes')
if __name__=='__main__':main()
