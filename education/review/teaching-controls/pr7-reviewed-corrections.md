# Narrow corrections after the completed PR7 review

Base: 1ddebd8d4d8c3d4b723084e7fbe29b25b051e030. Scope-only commit 38c2096 makes the global reset instructions agree with each lab's actual controller. Controller physics is unchanged.

The current endpoint browser audit now locates the specific `Small-strain scope` value (`dd`), checks its warning text, scrolls it into view, and asserts Playwright visibility before recording `warningVisible=true`. A freshly captured readout screenshot is delivered under data/property-labs-v1/endpoint-warning-current-visible.png and bound by SHA256 in the browser receipt; the artifact gate verifies both checkout and delivered screenshot bytes. The PNG was visually inspected: actual warning and expanded range are legible alongside endpoint maximum 0.0545455. Two new negative artifact checks reject altered screenshot bytes and a false visibility claim.

Fresh checks: numerical endpoint audit; actual Chromium endpoint controls; historical/current artifact gate; eight endpoint audit contract tests; four tapered-bar Node tests. The original endpoint-warning-audit.json is unchanged at SHA256 7995b4d3a33cd07994c43007a9e4208170e35f5e1d5d14ba93e0c675cf1acdc3. No historical receipt was replaced or relabeled. Full book/release CI still must run on the new head; isolated browser/gate passes are not a release result. No merge or deployment performed.
