#!/usr/bin/env python3
"""Read-only provenance check of inventoried temporary MAT data, not a model run."""
import argparse
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

import numpy as np
import scipy
from scipy.io import loadmat, whosmat


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    packet = repo / "education/data/anatomical-arm-v1/review/matched-calibration-data-search"
    facts_path = packet / "rat-source-facts.json"
    facts = json.loads(facts_path.read_text())
    checks, inventories = [], []

    def check(name, passed):
        result = bool(passed)
        checks.append({"name": name, "passed": result})
        print(f"{'PASS' if result else 'FAIL'} {name}", flush=True)

    summaries = {record["name"]: record for record in facts["parsed_observational_data"]}
    observed = {}
    for entry in facts["bounded_downloads"]:
        name = Path(entry["path"]).name
        path = args.source_dir / name
        raw = path.read_bytes()
        check(f"{name}: byte size", len(raw) == entry["bytes"])
        check(f"{name}: SHA256", hashlib.sha256(raw).hexdigest() == entry["sha256"])
        blob = b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
        check(f"{name}: Git blob SHA1", hashlib.sha1(blob).hexdigest() == entry["git_blob_sha1"])
        inventory = [[key, list(shape), kind] for key, shape, kind in whosmat(path)]
        expected = summaries[name]["mat_inventory"] if name in summaries else facts["sampled_fit_file"]["mat_inventory"]
        check(f"{name}: field/shape/class inventory", inventory == expected)
        inventories.append({"source_path": entry["path"], "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), "mat_inventory": inventory})
        if name not in summaries:
            continue  # Never load the fit's function handles or opaque workspace.
        data = loadmat(path, squeeze_me=True)
        observed[name] = data
        for key, expected_field in summaries[name]["fields"].items():
            value = np.asarray(data[key])
            finite = np.isfinite(value)
            actual = {"shape": list(value.shape), "dtype": str(value.dtype),
                      "finite_count": int(finite.sum()), "nan_count": int(np.isnan(value).sum()),
                      "min": float(value[finite].min()), "max": float(value[finite].max())}
            check(f"{name}/{key}: observational summary", actual == expected_field)
    force = observed["force_pCa.mat"]
    check("Fmax equals row nanmax F0 exactly", np.array_equal(force["Fmax"], np.nanmax(force["F0"], axis=1)))
    selected = np.flatnonzero(force["pCas"] == 4.5)
    check("one pCa4.5 column", selected.size == 1)
    check("Fmax equals pCa4.5 F0 exactly", selected.size == 1 and np.array_equal(force["Fmax"], force["F0"][:, selected[0]]))
    caveat = facts["known_source_data_mismatch"]
    check("stored SRS thresholds preserved", np.array_equal(observed["SRS_data.mat"]["th"], caveat["stored_thresholds"]))
    check("stored/source threshold mismatch retained", caveat["stored_thresholds"] != caveat["source_active_thresholds"])
    check("source additional SRSrel2 absent from stored binary", caveat["source_additional_field"] not in observed["SRS_data.mat"])
    check("negative SRS entries retained", np.nanmin(observed["SRS_data.mat"]["SRS_pre"]) < 0 and np.nanmin(observed["SRS_data.mat"]["SRS_post"]) < 0)
    check("observed missing F0 entries retained", int(np.isnan(force["F0"]).sum()) == 16)
    for path in sorted(packet.glob("*-facts.json")):
        json.loads(path.read_text())
        check(f"{path.name}: valid JSON", True)
    result = {"schema": "kenoma-matched-calibration-data-verification-v1", "status": "PASS" if all(c["passed"] for c in checks) else "FAIL",
              "command": sys.argv, "scope": "DATA_PROVENANCE_ONLY; NO_SI_CALIBRATION_OR_MODEL_RUN",
              "preexecution_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
              "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
              "facts_sha256": hashlib.sha256(facts_path.read_bytes()).hexdigest(),
              "source_pin": facts["source_pin"], "checks": checks, "inventories": inventories,
              "raw_array_payloads_exported": False, "author_code_executed": False, "fit_workspace_decoded": False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"RESULT {result['status']}: {len(checks)} data-provenance checks; numerical calibration remains unqualified", flush=True)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
