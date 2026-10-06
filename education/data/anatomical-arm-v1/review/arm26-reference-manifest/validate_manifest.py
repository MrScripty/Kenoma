"""Validate research metadata units/provenance. No OpenSim import or model evaluation."""
import argparse
from decimal import Decimal
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


BASE = "1a63fb6be3d9d8131769856cbf9796c873ffa2ce"
MODEL_COMMIT = "84b487c4e3245359a64381e01f01b9cf4772d457"
MODEL_SHA = "e2224d0044eb393b05d64926c3fa1682c451a9adc7f510e5517ef9958d3d41b9"
CORE_COMMIT = "5bc7d3308eda742690f485ec060bfe725a349fa6"
BENCHMARK_COMMIT = "0e89c60d03d3d6137e1ece686ecf942b83d05645"
HEADS = {
    "BIClong": "FJ1478", "BICshort": "FJ1512", "BRA": "FJ1486",
    "TRIlong": "FJ1479", "TRIlat": "FJ1477", "TRImed": "FJ1480",
}
UNITS = {"m", "m^2", "rad", "Pa", "1"}
STATUSES = {"measured", "derived", "model_assumed", "derived_not_evaluated", "unknown"}


def check(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def quantities(value, path=""):
    if isinstance(value, dict):
        if {"value", "unit", "status"} <= value.keys():
            yield path, value
        for key, child in value.items():
            yield from quantities(child, path + "/" + key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from quantities(child, path + "/" + str(index))


def xml_node(xml, xpath):
    prefix = "/OpenSimDocument"
    check(xpath.startswith(prefix + "/"), "XPath root: " + xpath)
    node = xml.find("." + xpath[len(prefix):])
    check(node is not None, "Missing source XPath: " + xpath)
    return node


def expected_unit(source):
    xpath = source["xpath"]
    leaf = xpath.rsplit("/", 1)[-1]
    if leaf in {"optimal_fiber_length", "tendon_slack_length", "location",
                "translation", "radius", "length", "dimensions"}:
        return "m"
    if leaf in {"pennation_angle_at_optimal", "orientation", "xyz_body_rotation",
                "default_value", "range"}:
        return "1" if "/PathWrap" in xpath and leaf == "range" else "rad"
    if leaf == "axis":
        return "1"
    if leaf == "coefficients":
        check("component_index" in source, "Mixed coefficients must be typed separately")
        return "1" if source["component_index"] == 0 else "rad"
    if leaf == "value" and "/TransformAxis" in xpath:
        return "rad" if "[@name='rotation" in xpath else "m"
    raise ValueError("Unrecognized numeric source unit: " + xpath)


def validate(root):
    directory = root / "education/data/anatomical-arm-v1/review/arm26-reference-manifest"
    proposal = json.loads((directory / "reference-manifest.json").read_text())
    check(proposal["schema_version"] == "1.0.0", "Schema")
    check(proposal["status"] == "proposed_not_adopted", "Proposal must not be adopted")
    check(proposal["base_commit"] == BASE, "Frozen base")
    check(not any(proposal["scope"][key] for key in (
        "solver_activation", "production_parameter_adoption", "anatomical_accuracy_claim",
        "runtime_model_load", "moment_arm_or_path_length_evaluation", "meshes_downloaded"
    )), "Research scope")
    asset = proposal["source_family"]["asset"]
    data = (root / asset["local_path"]).read_bytes()
    check(asset["commit"] == MODEL_COMMIT and asset["sha256"] == MODEL_SHA,
          "Immutable model pin")
    check(digest(data) == MODEL_SHA and len(data) == asset["bytes"] == 90192,
          "Retained model bytes")
    check(asset["raw_url"] == "https://raw.githubusercontent.com/opensim-org/opensim-models/"
          + MODEL_COMMIT + "/Models/Arm26/arm26.osim", "Commit-addressed URL")
    check(hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
          == asset["computed_git_blob_sha1"], "Computed blob hash")
    xml = ET.fromstring(data)
    model = xml.find("Model")
    check(xml.attrib["Version"] == asset["OpenSimDocument_version"] == "40000", "XML version")
    check(model.findtext("length_units") == "meters" and model.findtext("force_units") == "N",
          "Model units")
    license_record = proposal["source_family"]["license"]
    check(license_record["id"] == "CC-BY-3.0" and "CCBY 3.0" in model.findtext("credits"),
          "Embedded model license")
    check(license_record["full_notice_preserved_in"] == asset["local_path"], "Original credit")
    check("Holzbaur" in model.findtext("publications"), "Source lineage attribution")

    context = proposal["OpenSim_context"]
    pin = context["pin_evidence"]
    check(pin["kenoma_commit"] == BENCHMARK_COMMIT, "Other worker's frozen provenance")
    pin_bytes = (root / pin["local_snapshot_path"]).read_bytes()
    upstream = json.loads(pin_bytes)
    check(digest(pin_bytes) == pin["sha256"], "Context manifest hash")
    for key in ("release_tag", "tag_object", "commit", "tree"):
        check(context[key] == upstream[key], "Core context " + key)
    check(context["commit"] == CORE_COMMIT and context["core_license"] == "Apache-2.0",
          "Pinned core and separate software license")
    access = json.loads((directory / "source-provenance.json").read_text())
    check(access["raw_equals_retained_source"] and access["raw_fetch_http_status"] == 200,
          "Bounded official model access")
    check(access["model_asset"] == asset and not access["large_mesh_downloads"], "Access receipt")
    for record in context["bounded_source_access"]:
        check("/" + CORE_COMMIT + "/" in record["url"] and record["http_status"] == 200,
              "Commit-addressed core access")
        check(len(record["sha256"]) == 64 and record["bytes"] < 150000, "Core access bound")
    core_license = next(r for r in context["bounded_source_access"] if r["path"] == "LICENSE.txt")
    check(core_license["sha256"] == next(r["sha256"] for r in upstream["files"]
          if r["upstream_path"] == "LICENSE.txt"), "Independent core license-byte agreement")

    atlas_record = proposal["atlas_datum"]
    atlas_bytes = (root / atlas_record["path"]).read_bytes()
    atlas = json.loads(atlas_bytes)
    check(digest(atlas_bytes) == atlas_record["sha256"], "Atlas datum bytes")
    check(atlas_record["source_sha256"] == atlas["source_sha256"], "Atlas source identity")
    check(len(proposal["heads"]) == 6 and
          {h["model_name"] for h in proposal["heads"]} == set(HEADS), "Six distinct heads")
    check({h["model_name"]: h["atlas_entity_id_name_correspondence"] for h in proposal["heads"]}
          == HEADS, "Head/entity name correspondence")
    check({h["atlas_entity_id_name_correspondence"] for h in proposal["heads"]}
          <= {m["element_id"] for m in atlas["muscles"]}, "Existing atlas identities")
    check({m.attrib["name"] for m in model.findall("./ForceSet/objects/*")} == set(HEADS),
          "No extra imported actuator")

    counts = {"quantities": 0, "xml_numeric_quantities": 0, "explicit_unknowns": 0,
              "unevaluated_derived_quantities": 0, "null_quantities": 0}
    for path, quantity in quantities(proposal):
        counts["quantities"] += 1
        check(quantity["unit"] in UNITS and quantity["status"] in STATUSES, "Quantity type " + path)
        uncertainty = quantity["uncertainty"]
        check(uncertainty["kind"] == "not_reported" and uncertainty["value"] is None
              and uncertainty["unit"] == quantity["unit"], "No invented uncertainty " + path)
        value = quantity["value"]
        if value is None:
            check(quantity["status"] in {"unknown", "derived_not_evaluated"}, "Null status " + path)
            counts["null_quantities"] += 1
            counts["explicit_unknowns" if quantity["status"] == "unknown"
                   else "unevaluated_derived_quantities"] += 1
            continue
        check(quantity["status"] != "unknown", "Unknown replaced by number " + path)
        values = value if isinstance(value, list) else [value]
        check(all(type(v) in (int, float) and math.isfinite(v) for v in values), "Finite value " + path)
        source = quantity["source"]
        check(source is not None, "Numeric value without provenance " + path)
        if source.get("asset") == "arm26":
            leaf = xml_node(xml, source["xpath"])
            source_values = [float(v) for v in leaf.text.split()]
            if "component_index" in source:
                source_values = [source_values[source["component_index"]]]
            check(values == source_values, "Extracted XML value differs " + path)
            check(quantity["unit"] == expected_unit(source), "XML unit differs " + path)
            check(quantity["status"] == "model_assumed", "Model input relabeled " + path)
            counts["xml_numeric_quantities"] += 1
        elif source.get("asset") == "atlas":
            check(source["json_pointer"] == "/frame/atlas_bind_angle_rad" and quantity["unit"] == "rad",
                  "Atlas pointer/unit")
            check(value == atlas["frame"]["atlas_bind_angle_rad"], "Atlas datum value")
        elif "conversion_to_m" in source:
            check(source["source_unit"] == "um" and source["conversion_to_m"] == 1e-6
                  and quantity["unit"] == "m", "Sarcomere unit conversion")
            check(Decimal(str(value)) == Decimal(str(source["source_value"])) * Decimal("1e-6"),
                  "Sarcomere SI value")
        else:
            check(source.get("proposal") == "comparison pose v1" and quantity["unit"] == "rad",
                  "Unknown numeric proposal provenance " + path)

    convention = proposal["source_family"]["lineage_convention"]
    check(convention["optimal_sarcomere_length"]["value"] == 2.7e-6 and
          convention["Murray2000_comparison_convention"]["value"] == 2.8e-6, "Distinct conventions")
    kin = proposal["source_kinematics"]
    body_frames = set(kin["body_frames"])
    check(body_frames == {"/bodyset/" + b.attrib["name"]
          for b in model.findall("./BodySet/objects/Body")}, "Body frame set")
    source_joints = model.findall("./JointSet/objects/*")
    check(len(kin["joints"]) == len(source_joints), "Complete joint set")
    for joint, original in zip(kin["joints"], source_joints):
        check(joint["name"] == original.attrib["name"] and joint["type"] == original.tag,
              "Source joint identity/type")
        for key, tag in (("parent_frame_socket", "socket_parent_frame"),
                         ("child_frame_socket", "socket_child_frame")):
            check(joint[key] == original.findtext(tag), "Joint frame socket")
        frames = original.findall("./frames/PhysicalOffsetFrame")
        check(len(joint["offset_frames"]) == len(frames), "Complete joint frames")
        for frame, source_frame in zip(joint["offset_frames"], frames):
            check(frame["name"] == source_frame.attrib["name"] and
                  frame["parent_frame"] == source_frame.findtext("socket_parent"),
                  "Joint-scoped offset frame")
        axes = original.findall("./SpatialTransform/TransformAxis")
        check(len(joint["transform_axes"]) == len(axes), "Complete transform axes")
        for axis, source_axis in zip(joint["transform_axes"], axes):
            check(axis["name"] == source_axis.attrib["name"] and
                  axis["coordinates"] == (source_axis.findtext("coordinates") or "").split(),
                  "Transform coordinate association")
            check(axis["function_type"] == list(source_axis)[-1].tag, "Transform function type")
    for coordinate in kin["coordinates"]:
        source_coordinate = xml_node(xml, coordinate["source"]["xpath"])
        check(coordinate["name"] == source_coordinate.attrib["name"], "Coordinate identity")
        check(coordinate["locked"] == (source_coordinate.findtext("locked") == "true") and
              coordinate["clamped"] == (source_coordinate.findtext("clamped") == "true"),
              "Coordinate source properties")
    wraps = {w["name"]: w for w in kin["wrap_objects"]}
    check(len(wraps) == len(kin["wrap_objects"]) == 4, "Wrap identity set")
    for wrap in wraps.values():
        source_wrap = xml_node(xml, wrap["source"]["xpath"])
        check(wrap["name"] == source_wrap.attrib["name"] and wrap["type"] == source_wrap.tag,
              "Source wrap type/identity")
        check(wrap["quadrant"] == source_wrap.findtext("quadrant") and
              wrap["active_source_property"] == (source_wrap.findtext("active") == "true"),
              "Source wrap configuration")
        check(wrap["body_frame"] in body_frames, "Wrap body frame")
    point_count = wrap_count = 0
    for head in proposal["heads"]:
        check(head["actuator_class"] == "Thelen2003Muscle", "Actuator conversion")
        actuator = xml_node(xml, head["source"]["xpath"])
        check(head["source"]["xpath"].endswith("[@name='" + head["model_name"] + "']"), "Head XPath")
        for key in ("fascicle_reference_length", "reference_sarcomere_length", "reference_pennation",
                    "active_optimal_reference_stretch"):
            check(head[key]["value"] is None and head[key]["status"] == "unknown", "Unmeasured reference")
        path_length = head["musculotendon_path_length_at_comparison_pose"]
        check(path_length["value"] is None and path_length["status"] == "derived_not_evaluated"
              and path_length["source"]["xpath"] == head["source"]["xpath"] + "/GeometryPath",
              "Unevaluated model path length")
        points = head["attachments_and_path"]["points"]
        expected = actuator.findall("./GeometryPath/PathPointSet/objects/*")
        check(len(points) == len(expected), "Complete point sequence")
        for point, original in zip(points, expected):
            check(point["name"] == original.attrib["name"] and point["type"] == original.tag,
                  "Source path-point order/type")
            check(point["parent_frame"] in body_frames and point["parent_frame"] == original.findtext("socket_parent_frame"), "Body-local point frame")
            check(len(point["location"]["value"]) == 3, "Point Vec3")
        references = head["attachments_and_path"]["wraps"]
        originals = actuator.findall("./GeometryPath/PathWrapSet/objects/PathWrap")
        check(len(references) == len(originals), "Complete wrap sequence")
        for reference, original in zip(references, originals):
            check(reference["wrap_object"] in wraps and reference["wrap_object"] == original.findtext("wrap_object"), "Wrap link")
            check(reference["method"] == original.findtext("method"), "Wrap method")
        check(head["moment_arms"]["value"] is None and
              head["moment_arms"]["status"] == "derived_not_evaluated" and
              head["moment_arms"]["angle_derivative_unit"] == "rad", "Unevaluated moment arms")
        check(head["optimal_fiber_length"]["value"] > 0 and head["tendon"]["slack_length"]["value"] > 0, "Length dimensions")
        for key, value in head["tendon"].items():
            if key != "slack_length":
                check(value["value"] is None and value["status"] == "unknown", "Invented tendon observation")
        point_count += len(points)
        wrap_count += len(references)
    check(point_count == 32 and wrap_count == 7, "Complete source routing count")
    check({c["name"] for c in kin["coordinates"]} == {"r_shoulder_elev", "r_elbow_flex"}, "Two-DOF coverage")
    check(proposal["poses"]["educational_comparison"]["forearm_rotation"]["value"] is None,
          "No invented independent forearm coordinate")

    # The only geometric operation here is byte hashing: no path, moment-arm or solver evaluation.
    preserved = 0
    record_hash = hashlib.sha256()
    for entry in subprocess.check_output(["git", "ls-tree", "-r", "-z", BASE], cwd=root).split(b"\0"):
        if not entry:
            continue
        metadata, path = entry.split(b"\t", 1)
        mode, kind, blob = metadata.decode().split()
        check(kind == "blob", "Unexpected baseline object")
        local = root / path.decode()
        content = os.readlink(local).encode() if mode == "120000" else local.read_bytes()
        check(hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest() == blob,
              "Changed preexisting file: " + path.decode())
        if mode in {"100644", "100755"}:
            check(bool(local.stat().st_mode & 0o111) == (mode == "100755"), "Changed baseline mode")
        record_hash.update(path + b"\0" + digest(content).encode() + b"\n")
        preserved += 1
    return {
        "schema": 1, "passed": True, "manifest_id": proposal["manifest_id"], "base_commit": BASE,
        "model_commit": MODEL_COMMIT, "model_sha256": MODEL_SHA, "core_commit": CORE_COMMIT,
        **counts, "distinct_heads": 6, "ordered_path_points": point_count,
        "wrap_objects": 4, "path_wrap_references": wrap_count, "source_coordinates": 2,
        "all_existing_files_preserved": preserved, "baseline_path_sha256_records_digest": record_hash.hexdigest(),
        "checks": "Units, immutable source bytes, source field equality, named-frame/wrap provenance, explicit unknowns and baseline preservation only",
        "runtime_loads": 0, "geometric_evaluations": 0, "solver_runs": 0,
        "parameter_adoptions": 0, "clinical_or_anatomical_validation": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    arguments = parser.parse_args()
    root = Path(__file__).resolve().parents[5]
    receipt = validate(root)
    output = json.dumps(receipt, indent=2) + "\n"
    if arguments.receipt:
        arguments.receipt.write_text(output)
    print(output, end="")
