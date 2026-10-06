# Actual current-main browser qualification

The six checks run directly in `/workspace/kenoma-current-main-53` after the
root's fresh build/PDF readiness signal. Candidate source is
`f110ad2d73f77feda18ccd273d9b8be119bdc77e`, with the accepted unchanged tree
`b71cef5a57379e522eddb0ddc3fe06e7e71570a2`. Both actual Git identities were
checked on entry and after the worktree move:
`MrScripty <TheEnvironmentGuy@protonmail.com>`.

Commands, from `education`:

```sh
python3 tests/browser.py
python3 tests/mobile_startup.py
python3 tests/anatomical_inspection.py
python3 tests/coupled_inspection.py
python3 tests/anatomical_arm_inspection.py
python3 tests/worker_lifecycle.py
```

Each actual command has its own new `browser-lane-<name>.log` in this directory.
`browser-lane-binding.json` records all six exact test hashes, the candidate
revision/tree and identities, 865 build input hashes with zero checkout
differences, and the actual executable/HTML/app/PDF hashes before the run.
The fresh dist contained no older task-owned browser receipts to archive.
Existing frozen evidence and source branches remain unchanged; no historical
receipt is reused as a fresh result.

Final results will be recorded only after each command returns successfully
and its actual receipt is checked. Mobile checks use Chromium viewport/touch
emulation, not physical-phone certification. The anatomical-arm lane covers
rest and control behavior, not a loaded anatomical trajectory. Worker timer
checks use injected held/error events and synthetic unchanged-state replies.
Production equations, calibration, limits and test assertions are unchanged.
The root owns source changes, commits, pushes, artifact/package and publication.

All six commands returned exit 0 and their fresh receipts passed. The actual
whole-book run verified 53 proof cards and all embedded controls, links,
resources, mobile viewport, summaries and no-WebGL/no-JavaScript paths.
Receipt/screenshot snapshots are in `browser-lane-evidence/`. The completed
binding rechecks unchanged HTML/app/manifest/PDF, all six tests, and the whole
executable map. Actual new mobile spatial and coupled-loaded renders were
inspected. No source edit, commit, push, deployment or dissipative change was made.
