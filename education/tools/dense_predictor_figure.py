"""Retained residual traces for initialization controls from one physical old state."""
import hashlib
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

summary_path = Path("data/anatomical-arm-v1/audit/dense-predictor-comparison.json")
summary = json.loads(summary_path.read_text())
assert summary["result"] == "PASS_SOURCE_BOUND_PREDICTOR_COMPARISON"
for p, expected in summary["sourceHashes"].items():
    assert hashlib.sha256(Path(p).read_bytes()).hexdigest() == expected, p
base = Path("data/anatomical-arm-v1/audit")
original = json.loads((base / "anatomical-dense-release-refinement.json").read_text())
traces = [("Archived seed · preserved rejection", "#777777",
           [r for r in original["trace"] if r["stage"] == len(original["attempts"]) - 1])]
for key, color, label in [("accepted-copy", "#ba5b26", "Accepted-coordinate copy"),
                          ("bounded-secant", "#126b91", "Bounded accepted-state secant")]:
    run = json.loads((base / f"dense-predictor-{key}.json").read_text())
    assert run["result"] != "RUNNING"
    traces.append((label + (" · accepted" if run["accepted"] else " · rejected"), color, run["trace"]))
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(10.5, 5), constrained_layout=True)
for label, color, rows in traces:
    residual = [r["residualN"] for r in rows]
    assert residual and all(v > 0 for v in residual)
    ax.plot(range(1, len(rows) + 1), residual, label=label, color=color,
            linewidth=1.7, linestyle="--" if color == "#777777" else "-")
ax.axhline(0.0001, color="#333333", linestyle=":", label="Unchanged 0.0001 N gate")
ax.set(yscale="log", xlabel="Recorded nonlinear iteration index across frozen contact rules",
       ylabel="Maximum reduced residual (N)",
       title="Same dense old state at 0.420 s · h = 0.01 s · only initial coordinates differ")
ax.grid(alpha=0.22)
ax.legend(fontsize=9)
output = Path(sys.argv[1])
assert not output.exists(), "Preserve existing render receipt"
output.parent.mkdir(parents=True, exist_ok=True)
files = [output.parent / "accepted-predictor-controls.png", output.parent / "accepted-predictor-controls.pdf"]
assert not any(p.exists() for p in files)
for p in files:
    fig.savefig(p, dpi=180)
plt.close(fig)
receipt = {"result": "PASS_DENSE_PREDICTOR_FIGURE_RENDER",
           "sourceComparisonSHA256": hashlib.sha256(summary_path.read_bytes()).hexdigest(),
           "rendererSHA256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "renderedSHA256": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
           "limits": ["Iteration curves are solver traces, not accepted physical trajectories.",
                      "The 120-iteration ceiling applies per frozen contact rule; all rule changes remain in raw receipts.",
                      "The predictor cap is inactive on this equal-increment case; repeated success is not general reliability or physical validation."]}
output.write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
