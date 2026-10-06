"""Lightweight cross-model area/stress inference; no fit or default update."""
import hashlib
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

geometry_path = Path("data/anatomical-arm-v1/audit/anatomical-calibration-geometry.json")
model_path = Path("data/elbow-v1/sources/arm26.osim")
geometry = json.loads(geometry_path.read_text())
digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
for path, expected in geometry["sourceHashes"].items():
    assert digest(path) == expected, path
root = ET.parse(model_path).getroot()
rows = []
reported_restored = {"FJ1486": 1.104, "FJ1512": 0.777, "FJ1478": 0.757}
for record in geometry["rows"]:
    muscle = next(m for m in root.iter("Thelen2003Muscle") if m.attrib.get("name") == record["arm26Muscle"])
    target = float(muscle.findtext("max_isometric_force"))
    length = float(muscle.findtext("optimal_fiber_length"))
    pennation = float(muscle.findtext("pennation_angle_at_optimal"))
    assert target == record["arm26MaximumIsometricForceN"] and length > 0
    assert pennation == 0
    volume = record["referenceVolumeCm3"] * 1e-6
    area = volume / length
    stress = target / area
    restored = reported_restored[record["elementId"]]
    rows.append({"elementId": record["elementId"], "arm26Muscle": record["arm26Muscle"],
                 "referenceVolumeM3": volume, "arm26OptimalFiberLengthM": length,
                 "arm26MaximumIsometricForceN": target, "arm26PennationRad": pennation,
                 "pennationCosine": math.cos(pennation), "inferredAreaM2": area,
                 "inferredAreaMm2": area * 1e6, "targetOverInferredAreaPa": stress,
                 "targetOverInferredAreaMPa": stress * 1e-6,
                 "parentForwardedRestoredSourceVolumeStressMPa": restored,
                 "approximateReductionFromRoundedForwardedValuePercent": 100 * (1 - restored / (stress * 1e-6))})
receipt = {"result": "PASS_SOURCE_BOUND_CROSS_MODEL_CAPACITY_INFERENCE", "appliedToModel": False,
           "rows": rows, "sourceHashes": {str(geometry_path): digest(geometry_path), str(model_path): digest(model_path),
                                         "tools/anatomical_cross_model_capacity.py": digest(__file__)},
           "definitions": {"inferredArea": "Atlas remeshed reference volume / Arm26 optimal fiber length",
                           "inferredNominalStress": "Arm26 maximum isometric force / inferred area, before continuum deformation"},
           "forwardedRestorationStatus": "Rounded preliminary independent reviewer values supplied by parent; source-volume restoration was not recomputed here.",
           "limits": ["Cross-model inference, not measured human PCSA or measured specific tension.",
                      "Arm26 fiber lengths and pennation parameters are not measured architecture of the atlas subject.",
                      "Zero Arm26 pennation leaves this model-target inference unchanged; it does not establish zero atlas pennation.",
                      "The deformed continuum coefficient, spatial Cauchy stress, boundary force and inferred nominal stress remain different quantities.",
                      "No constitutive, calibration, numerical gate, material default, release, or skin change."]}
output = Path(sys.argv[1])
assert not output.exists(), "Preserve existing inference"
output.write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
