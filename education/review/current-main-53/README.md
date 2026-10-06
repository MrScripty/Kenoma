# Current-main integration of the accepted 53-declaration edition

This is a normal-history composition candidate for the next book PR. It brings
current main into the independently accepted edition without adding the separate
dissipative lesson.

Exact source merge: `f110ad2d73f77feda18ccd273d9b8be119bdc77e`.

- First parent: accepted edition `f0973f46e55faa881ab3b34c6a848dfee313142e`.
- Second parent: current main `041de5deed0d288f644017704d675b7f8c1b97a4`.
- Source tree: `b71cef5a57379e522eddb0ddc3fe06e7e71570a2`.

The merge source tree is **byte-identical** to the accepted edition's tree.
Both parents are ancestors of the candidate. Main's teaching-control repair is
already present in the accepted edition; merging history does not change the
lesson implementation, equations, coefficients, acceptance limits or labels.

Seven conflicts were resolved to the accepted edition's later source/evidence:

1. `book/chapters/00-scope.md`: retain the same per-lab policies and the additional
   four-property-lesson explanation.
2. `data/property-labs-v1/endpoint-warning-browser-audit.json`.
3. `data/property-labs-v1/endpoint-warning-current-audit.json`.
4. `data/property-labs-v1/endpoint-warning-current-visible.png`: retain the later
   receipts and actual screenshot bound to this edition's current renderer.
5. `tests/artifacts.py`: retain material/Real-family artifact checks.
6. `tests/test_endpoint_audit_contract.py`.
7. `tools/check_endpoint_warning_audit.py`: retain the extra archived numerical
   source binding and its negative regression.

Every historical receipt remains unchanged. In particular, the original
endpoint-failure audit remains SHA-256
`7995b4d3a33cd07994c43007a9e4208170e35f5e1d5d14ba93e0c675cf1acdc3`.
The old Lab3 README typo mentioned in review was not edited; it is absent from
this edition's learner source and is not part of this composition candidate.

Qualification logs and receipts in this directory are new checks against the
exact merge source. They are distinct from the accepted edition's preserved
`review/real-domain-claims/qualified-53/` evidence. See `qualification.json` for
results and bindings after qualification completes.

Qualification completed: **179 Node tests, 32 Python tests, all 53 fresh Lean
declarations, six actual browser lanes, property/material controls, desktop/mobile
proof-card captures, complete PDF continuation checks, the full artifact gate and
portable-package validation passed**. The PDF has 79 pages. The unchanged 10 pt
atlas-label gate measures 10.229 pt in the new PDF. Manual appearance review is
limited to the exact captures named in `qualification.json`; the remaining
capture/layout checks are automated.

The first Python run encountered three environment failures because `/tmp` had
only 682 MB available and the source-acquisition fixture enforces a 1.5 GiB
free-space floor. Its unmodified raw log is retained separately. Only the new
root-owned worktrees were moved to `/workspace`, then all 32 Python tests passed.
No source-acquisition rule, test, source byte or acceptance limit changed.

New portable archive: `/workspace/kenoma-current-main-53-portable.zip`,
71,758,344 bytes, 1,027 files; SHA-256
`bcadda33956e2b528087cd90b3006c77c573d7d75e17a74ec604dab58f6057d8`.
Archive CRC and every archived file's SHA-256 were checked against the qualified
build. `portable-package.json` supplies its complete per-file inventory.

The merge commit has actual Git author and committer
`MrScripty <TheEnvironmentGuy@protonmail.com>`. The cloud's global identity
reverted between command invocations, so only the two authorized identity fields
were set in this isolated repository's local configuration. Actual Git identities
were rechecked after worktree creation and immediately before committing. No
authentication, credentials, signing, remote or network configuration changed;
previous commits were not rewritten.

No PR, merge to main, hosted publication or deployment is performed by this
candidate's worker. PR creation remains coordinated with the parent to avoid
duplication.
