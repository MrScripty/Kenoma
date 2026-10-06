# Research proof evidence

The tested source commit is `2860324342da35309b92418cd8ffe2e23fbdb950`, based on fetched main `041de5deed0d288f644017704d675b7f8c1b97a4`. The subsequent evidence commit adds only this directory. Author and committer are MrScripty `<TheEnvironmentGuy@protonmail.com>`.

`receipt.json` binds the proof, checker, explanation, compiler, mathlib lock, eight transitive Git dependencies and kernel transcript. Its `source_files_match_commit` must be true. `lean-check.txt` reports the dependencies of all 27 declarations. `final-check.txt` retains the committed standalone checker's successful source-preparation and fresh compilation output.

`cold-source-build.txt` and `cold-source-logs.tar.gz` retain the initial two-job compilation of 877 pinned dependency modules. `extra-source-build.txt` retains the additional finite-sum import build. Together these prepare the final 902-module graph; the committed checker then checks that complete graph using two jobs. No alternate binary-cache endpoint was used after HTTP 403.

The generated `MixedLogVolume.olean` is retained locally in `education/.tools/mixed-volume-check/`; its hash is in the receipt. Reproduce with `python3 tools/check_mixed_volume_proofs.py --build-dependencies` from `education/`. These are local kernel checks, with the conditional finite-vector limits in the [research explanation](../mixed-log-volume-projection.md). No hosted CI, PR, merge, publication or numerical-implementation certification is claimed.
