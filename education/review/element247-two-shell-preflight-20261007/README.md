# Frozen two-shell preflight for independent conditional review

Source commit: `7580cfccbe028329ff774971ea06a6cdbda6431b`.
Base preserved result: `4b83ec5dfebae73b08c3f964aa910f65e02458e0`.
Branch: `research/element247-two-shell-diagnostic-20261007` (local only).

The [protocol](../../research/element247-two-shell-20261007.md) and
[input manifest](../../research/element247-two-shell-20261007-inputs.json)
define exactly 4,000 new terminal46 callbacks over s1/s2, with unchanged
Gauss5, radial parts1, chart123, depth20, fields and laws. Nineteen other
A55 regions and their 9,500 points are reused byte for byte. The constructed
inventory has 13,500 points. Changed-shell comparisons are reported
separately from constructed whole-element values; reused tails are zero
by construction and cannot qualify element247 or the full patch.

The [preflight receipt](preflight.json) is
PASS_TWO_SHELL_PREFLIGHT_NO_SPECIMEN_CALLS: 1,591 source hashes, zero
specimen calls, 22 passing tests and zero failures. Logs:
[JavaScript](js-tests.log), [Python](python-tests.log).
Six JavaScript controls use synthetic callbacks only; seven Python controls
use nonzero retained vectors and reject count/held-node/tail/pass damage;
nine preserved supervisor controls check actual process failures and
separate PIPE/DEVNULL children.

The prescribed [normalized points](changed-normalized-points.f64le) and
[reference weights](changed-reference-weights.f64le) contain exactly 4,000
entries. Structural checks cover positive finite weights, 252 normalized
degree5 moments, 30 physical-reference barycentric degree2 moments,
unchanged whole-mesh certificate and pointwise geometry/domain guards.
The JSON hashes both binaries and logs and records every reused identity.

Independent acceptance is required before the parent-authorized one-shot
run. The independent review record and a separate authorization will be
frozen only after PASS. A failed review stops execution. No selective
specimen assembly or authorization has occurred at this preflight commit.
All original sources, evidence and 8.611662232570753e-5 N force failure
remain unchanged.

Independent replay, before authorization or actual selective output exists:

```sh
PYTHONDONTWRITEBYTECODE=1 node --max-old-space-size=1024 education/tools/preflight-element247-two-shell.mjs --output /tmp/kenoma-two-shell-pref-FRESH
```

The frozen source and evidence are read-only review inputs. Scratch outputs
must be separate and fresh. No reviewer may call the selective launcher,
material runner or specimen law before conditional acceptance.
