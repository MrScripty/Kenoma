"""Count a proposed P1 pressure space against the current isolated free field.

This is a rank-bound diagnostic, not a mixed solver or stability certificate.
"""
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/anatomical-arm-v1'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def run():
    source=BASE/'generated/arm-reference.json'
    calibration=BASE/'audit/anatomical-calibration-nodal.json'
    geometry=json.loads(source.read_text())
    nodal=json.loads(calibration.read_text())
    assert nodal['result']=='PASS_FROZEN_CALIBRATION_NODAL_DIAGNOSTIC'
    for relative,h in nodal['sourceHashes'].items():
        assert digest(ROOT/relative)==h,'Changed calibration input '+relative
    rows=[]
    for fixture in nodal['rows']:
        body=next(m for m in geometry['muscles'] if m['element_id']==fixture['elementId'])
        # The first four entries are the P2 tetrahedron's vertex nodes.
        # Continuous P1 pressure has one scalar coefficient per shared vertex.
        vertices=sorted({n for element in body['elements_ten_node'] for n in element[:4]})
        held=set(body['distal_nodes'])|set(body['proximal_nodes'])
        assert len(body['nodes_m'])==585 and len(held)==fixture['heldNodeCount']==90
        free_nodal=3*(len(body['nodes_m'])-len(held))
        # Original fixture holds both 9-coordinate end rings; rings 1..5 are free.
        free_reduced=5*9
        rows.append({'elementId':body['element_id'],'p1PressureVertexCount':len(vertices),'p1PressureVertexNodes':vertices,'originalFreeDisplacementCoordinates':free_reduced,'fullP2FreeDisplacementCoordinates':free_nodal,'minimumUncoupledPressureCombinationsInReducedStrictLimit':max(0,len(vertices)-free_reduced),'minimumDimensionObstructionInFullP2Field':max(0,len(vertices)-free_nodal)})
    files=['tools/anatomical_pressure_space_audit.py','web/anatomical-modal.mjs','web/anatomical-element.mjs','data/anatomical-arm-v1/generated/arm-reference.json','data/anatomical-arm-v1/audit/anatomical-calibration-nodal.json']
    receipt={'schema':1,'result':'PASS_PRESSURE_SPACE_DIMENSION_DIAGNOSTIC','proposedPressureSpace':'Continuous P1 on the shared tetrahedral vertex mesh','coupling':'D[i,alpha] = integral Q_i * delta(log J)[B_alpha] dV0. rank(D) <= number of free displacement coordinates.','rows':rows,'sourceHashes':{p:digest(ROOT/p) for p in files},'limits':['No pressure field, nonlinear mixed solve, constitutive change or time advancement is implemented.','The dimension bound concerns the strict mixed limit with vanishing pressure-compliance block. At finite K the pressure mass block divided by K regularizes these combinations; this count does not prove failure of the current finite penalty.','At least pressure-count minus free-displacement-count combinations cannot couple through D transpose. Actual coupling rank and mesh-dependent inf-sup constants are not evaluated.','The absence of a dimension obstruction for full P2 does not prove stable pairing, absence of locking, mechanical stationarity or credible compression.','Pressure gauge and boundary conditions must be declared in an implemented mixed formulation. The original calibration keeps complete fixed caps and free lateral boundaries.']}
    output=BASE/'audit/anatomical-pressure-space.json'
    assert not output.exists(),'Preserve existing pressure-space diagnostic'
    output.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))

if __name__=='__main__':run()
