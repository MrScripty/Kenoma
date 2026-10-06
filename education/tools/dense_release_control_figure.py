"""Render only recorded accepted control states and retained solver iterations."""
import hashlib
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

root = Path(".")
summary_path = root / "data/anatomical-arm-v1/audit/dense-controlled-release-interval-summary.json"
summary = json.loads(summary_path.read_text())
assert summary["result"] == "PASS_SOURCE_BOUND_CONTROL_SUMMARY"
for name, expected in summary["sourceHashes"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name
execution_path = root / "data/anatomical-arm-v1/audit/dense-controlled-release-interval.json"
run = json.loads(execution_path.read_text())
assert run["result"] != "RUNNING"
out = Path(sys.argv[1])
assert not out.exists(), "Preserve existing render receipt"
out.parent.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6), constrained_layout=True)
colors = ["#1d6487", "#b45523"]
for case, color in zip(run["cases"], colors):
    states = [run["oldState"], *case["snapshots"]]
    times = [s["timeS"] for s in states]
    angles = [np.degrees(s["qRad"]) for s in states]
    label = f"h = {case['hS']:.2f} s ({len(case['snapshots'])} accepted)"
    axes[0].scatter(times, angles, label=label, color=color, s=42, zorder=3,
                    marker="o" if case["factor"] == 1 else "x")
    residual = [t["residualN"] for t in case["trace"]]
    assert residual and all(np.isfinite(v) and v > 0 for v in residual)
    axes[1].plot(np.arange(1, len(residual) + 1), residual, color=color, label=label)
    if case["result"] == "REJECTED_INCREMENT":
        axes[0].annotate(f"Next target rejected: {case['attempts'][-1]['residualN']:.4g} N",
                         (times[-1], angles[-1]), xytext=(0, -28),
                         textcoords="offset points", color=color, fontsize=9)

axes[0].set(title="Accepted physical states from the same old state", xlabel="Actual time (s)", ylabel="Elbow angle (degrees)")
axes[0].set_xticks([0.40, 0.41, 0.42, 0.43])
axes[0].set_xlim(0.398, 0.436)
axes[0].legend(loc="upper right", fontsize=9)
axes[1].set(title="Recorded nonlinear iterations, including refined rules", xlabel="Iteration index across substeps / contact rules", ylabel="Maximum reduced residual (N)", yscale="log")
axes[1].axhline(0.0001, color="#444444", linestyle="--", linewidth=1, label="Unchanged acceptance gate")
axes[1].legend(loc="upper right", fontsize=8)
for ax in axes:
    ax.grid(alpha=0.22)
fig.suptitle("Common-old-state dense release control · unchanged mechanics and residual gate", fontsize=13)
figure_paths = [out.parent / "common-state-release-control.png", out.parent / "common-state-release-control.pdf"]
assert not any(p.exists() for p in figure_paths)
for p in figure_paths:
    fig.savefig(p, dpi=180)
plt.close(fig)
receipt = {"result": "PASS_CONTROL_FIGURE_RENDER", "sourceSummarySHA256": hashlib.sha256(summary_path.read_bytes()).hexdigest(),
           "rendererSHA256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "renderedSHA256": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in figure_paths},
           "limits": ["Only recorded accepted states are plotted; no endpoint interpolation or promotion of a rejected candidate.",
                      "Fine and coarse explicit seed choices and adaptive contact quadrature differ; this is not timestep convergence acceptance."]}
out.write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
