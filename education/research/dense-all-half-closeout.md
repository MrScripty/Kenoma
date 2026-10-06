# Existing all-half refinement closeout

The existing 256-point all-half trajectory has completed and passed fresh independent replay of all **30 accepted states**, through **0.43000000000000027 s**, under the unchanged **1e-4 N** stationarity gate. This is a self-consistent denser reduced trajectory, not full-nodal, quadrature, timestep or anatomical convergence acceptance. No new optimizer run was started for this closeout.

| Existing experiment | Terminal execution / independent replay | Accepted states | Maximum independent reduced residual |
| --- | --- | ---: | ---: |
| All-half fine | `ACCEPTED_DENSE_TRAJECTORY` / `PASS_DENSE_TRAJECTORY` | 30 | 9.884085604687336e-5 N |
| All-half interpolated initialization | Still running at this checkpoint; no terminal qualification | 29 through 0.415 s | Pending complete replay |

Fine lift/release reverses **40.76270431384987→36.37554967676739 degrees**, falling **4.387154637082488 degrees**. Its minimum integration-point determinant is **0.7237759980704086** and minimum corner determinant **0.70973738187981**, approximately **29.0% local compression**. Improved trajectory completion does not resolve bulk/compression credibility. The final independently assembled residual is **3.6771840794696566e-6 N**.

The fine execution retains its original **240 iterations per frozen contact rule**. Its 30 increments required 36 frozen rules and added 25 witnesses. On the last increment, the first rule converged in 76 iterations but exposed six missed contact witnesses (two body, four bone); the refined rule converged in 44 iterations with no further additions. This is the configured geometric refinement loop, not an increased iteration budget. State/time advanced only after final force and geometry acceptance. Recorded finite geometry, routing, surface and penetration checks were freshly replayed; their sampling/reduced-space limits remain explicit in the receipt.

The existing interpolated run and existing replay/finalizer continue without duplication. The scheduled matched-time comparison and render await that run's terminal outcome. The original release-only rejection and its 34 accepted states remain preserved; later successful runs do not relabel that failure. The [fixed-coefficient prism, attachment and sheet-control plan](fixed-coefficient-calibration-control-plan.md) remains the next unexecuted diagnostic step. No coefficients, equations, book/Lean claims, teaching release or skin changed.

## Exact fine evidence

- Execution: `data/anatomical-arm-v1/audit/anatomical-dense-fine-trajectory.json`, SHA256 **2e4b37080685001f65fa8db47ccf2f66b29cba4967f6284a28cecf8ac5073b7c**.
- Fresh replay: `data/anatomical-arm-v1/audit/anatomical-dense-fine-trajectory-recheck.json`, SHA256 **69f5cd3277b721ed300cbd586b4e55e0e1c5a9a17c4d101abdd015a184d8df0b**; binds the exact execution above and verifier SHA256 **0de4ac35162ecf731ac3e35b206d6ec3f071c9bf2cc9430c4839e054168b6c17**.
- Raw execution and replay: `review/dense-qualification/fine-execution.txt` and `fine-fresh-replay.txt`. All 40 execution source hashes were checked against this research lane before copying completed evidence. `all-half-closeout-manifest.json` binds the four copied files.

This checkpoint intentionally records the interpolated run as pending. Its original mutable receipt is not copied or hashed as terminal evidence. No additional expensive sweep or optimizer retry is authorized by this closeout.
