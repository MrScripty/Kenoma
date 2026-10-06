"""Source-bound dimensional diagnostics; no PCSA inference or new force fit."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/anatomical-arm-v1'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
    geometry=json.loads((BASE/'generated/arm-reference.json').read_text())
    fits=json.loads((BASE/'audit/modal-fixed-end-results.json').read_text())
    model=ROOT/'data/elbow-v1/sources/arm26.osim'
    muscles={m.attrib['name']:m for m in ET.parse(model).iter('Thelen2003Muscle')}
    names={'FJ1486':'BRA','FJ1512':'BICshort','FJ1478':'BIClong'};rows=[]
    for record in fits['records']:
        body=next(m for m in geometry['muscles'] if m['element_id']==record['elementId'])
        source=muscles[names[record['elementId']]]
        target=float(source.findtext('max_isometric_force'))
        assert abs(target-record['modelReference']['value'])<1e-10
        assert digest(model)==record['modelReference']['source_sha256']
        length=body['belly_interval_m'][1]-body['belly_interval_m'][0]
        volume=body['reference_volume_m3'];stress=record['match']['sigma0Pa'];force=record['match']['forceN']
        assert min(length,volume,stress,force)>0
        area=volume/length;effective=force/stress
        rows.append({'elementId':body['element_id'],'atlasName':body['name'],'arm26Muscle':source.attrib['name'],'arm26MaximumIsometricForceN':target,'referenceVolumeCm3':volume*1e6,'referenceBellyLengthMm':length*1e3,'geometricMeanAreaMm2':area*1e6,'matchedForceOverStressAreaMm2':effective*1e6,'forceOverStressMeanAreaRatio':effective/area,'fittedStressMPa':stress/1e6})
    files=['data/anatomical-arm-v1/generated/arm-reference.json','data/anatomical-arm-v1/audit/modal-fixed-end-results.json','data/elbow-v1/sources/arm26.osim','tools/anatomical_calibration_geometry.py']
    result={'schema':1,'result':'PASS_SOURCE_LABEL_AND_DIMENSIONAL_DIAGNOSTICS','sourceHashes':{p:digest(ROOT/p) for p in files},'rows':rows,'limits':['V/L is a geometric mean area, not a measured physiological cross-sectional area or fibre-length estimate.','F/sigma0 is an effective area of the recorded equilibrated fixture; its ratio to V/L includes strain, fibre orientation, internal sheets, volume stresses and displacement restrictions.','BodyParts3D geometry and Arm26 actuator parameters are separate reference models. These ratios do not determine physiological specific tension or justify selecting a new bulk modulus.']}
    (BASE/'audit/anatomical-calibration-geometry.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':run()
