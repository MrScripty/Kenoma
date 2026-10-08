"""Independent Cartesian/barycentric reconstruction of an actual browser download.

Uses only Python's standard library and saved reference/current positions.
It does not import the JavaScript geometry implementation or evaluate material.
"""
import argparse, hashlib, json, math, pathlib
def sub(a,b):return [x-y for x,y in zip(a,b)]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def determinant(a,b,c):return dot(a,cross(b,c))
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preview',type=pathlib.Path,required=True);parser.add_argument('--download',type=pathlib.Path,required=True);parser.add_argument('--receipt',type=pathlib.Path,required=True);args=parser.parse_args()
    assert not args.receipt.exists()
    raw=(args.preview/'model.json').read_bytes();model=json.loads(raw);record=json.loads(args.download.read_bytes())
    assert record['modelSha256']==hashlib.sha256(raw).hexdigest() and record['sourceCommit']==model['sourceCommit']
    m=next(m for m in model['muscles'] if m['element_id']==record['body']);section=record['section'];total_area=0;worst=0;plane_error=0;count=0
    for triangle in section['triangles']:
        e=m['elements_ten_node'][triangle['elementIndex']];a,b,c,d=[m['nodes_m'][n] for n in e[:4]]
        cols=[sub(b,a),sub(c,a),sub(d,a)];D=determinant(*cols);assert abs(D)>1e-18
        for vertex in triangle['vertices']:
            p=vertex['reference'];rhs=sub(p,a)
            l1=determinant(rhs,cols[1],cols[2])/D;l2=determinant(cols[0],rhs,cols[2])/D;l3=determinant(cols[0],cols[1],rhs)/D
            L=[1-l1-l2-l3,l1,l2,l3];assert min(L)>-1e-8 and max(L)<1+1e-8
            weights=[l*(2*l-1) for l in L]+[4*L[i]*L[j] for i,j in [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]]
            positions=m['frozen']['positions_m']
            reconstructed=[sum(w*positions[n][dim] for w,n in zip(weights,e)) for dim in range(3)]
            worst=max(worst,math.dist(reconstructed,vertex['current']))
            plane_error=max(plane_error,abs(dot(sub(p,m['basis']['origin']),m['basis']['axis'])-section['stationM']));count+=1
        x,y,z=[v['current'] for v in triangle['vertices']];total_area+=math.hypot(*cross(sub(y,x),sub(z,x)))/2*1e6
    assert worst<1e-11 and plane_error<1e-11
    area_error=abs(total_area-section['current']['tessellatedAreaMm2']);assert area_error<1e-8
    result={'result':'PASS_INDEPENDENT_BROWSER_EXPORT_GEOMETRY','body':record['body'],'fraction':section['fraction'],'checkedVertices':count,'maximumP2ReconstructionErrorM':worst,'maximumMaterialPlaneErrorM':plane_error,'areaReconstructionErrorMm2':area_error,'forceGate':m['frozen']['passesFullNodalForceGateAtFrozenPose'],'materialEvaluations':0,'limitations':'Floating-point reconstruction of saved geometry only; no stationarity, material, continuum or anatomical validation.'}
    args.receipt.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
