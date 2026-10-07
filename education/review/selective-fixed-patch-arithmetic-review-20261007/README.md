# Independent arithmetic/resource review and resolution diagnosis

**Independent read-only review PASS; completed numerical result remains
UNRESOLVED_FIXED_PATCH_INTEGRATION.** The frozen result is
`38ae8a2e2af57cf33254af987b724824b9d84357`; every failed comparison and gate is
preserved. Review, localization and proposal made **zero specimen/material-law
calls**, generated no quadrature and launched no specimen runner.

[Independent report](independent-artifacts/selective-material-independent-review.json),
[reviewer assessment](independent-artifacts/selective-material-independent-assessment.md)
and [exact artifact hashes](independent-artifact-manifest.json) are retained.
ReportSHA25685ca1f7e19559ea66d5dfe3afbee2a7246b14fcd24bad032d9dcb4a75357fcba.
The reviewer used separate scalar math.fsum loops,1,074,696 assertions and six
failure-priority damage fixtures.634regions,30stages,6complete16hybrids,
8comparisons,all5terms/all585nodes includingheld replayed; maximum alternate
reduction difference2.5267e-12. Actual child/worker/public exits0,497500new
callbacks and separately4000historic failed-run measurements were verified.
1239rawfiles/22302283B,43.048835s acceptance time and254705664B observed RSS
are within the frozen limits. Historical child/worker/public exit1,4000old
counters and incomplete receipts/no final acceptance remain unchanged.

## What each Q candidate means

Q0/Q1/Q2 are **integration candidates at the same two frozen fields**, not
new displacement states, optimizer iterations or stages of physical loading.
Each reuses the same252-element U3 baseline, subtracts its16patch contributions
and adds a complete new16patch. The236outsidecontributions remain unqualified.

| Candidate | Quiet9 | Secondary6 |247|
|---|---|---|---|
|Q0 coarse diagnostic|D4:32768points,512uniform subtets, Duffy Gauss4|C55:2625points,21corner regions,angular1|A55:10500points,21regions,angular2|
|Q1 primary|D5:64000points,same512subtets,Duffy Gauss5|A55:10500points,21regions,angular2|F44:42000points,21regions,angular4|
|Q2 mixed independent cross-check|U5:131072points,32768uniform subtets,symmetric4|D5:64000points,512subtets,Duffy Gauss5|X44:46000points,23regions,angular4,depth22,face231|

All C55/A55/F44/R44/X44 shell rules use **Gauss5 in r,a,b**. F44/R44 names
do not denote Gauss4. Their angular parts per axis are1/2/4/4/4. All have
radialparts1 except R44's2. Shell depth20 means20dyadic shells plus the
corner core; X44 depth22 means22shells pluscore. Node92 corner indices are
197/200→3,203→2,206→1,246/248→0;247→0. The opposite face is ascending local
indices except X44's cyclic231 face. Reference weights, laws and activation
are identical. Terminal F44 s1/s2 reuse4000exact old measurements; its19tails
and all control F44 regions are new. Reuse does not repair the old exit1.

Q0→Q1 is meaningful componentwise refinement: quiet Duffy order4→5 on a fixed
grid; secondary angular1→2 on fixed D20/radial1/charts;247 angular2→4 on that
same fixed shell geometry. Q1→Q2 changes families for quiet/secondary, and
changes depth **and** chart together at247. It is not a globally ordered
next resolution level. More points alone do not establish greater accuracy.

## Q0/Q1 localization, both fields

The outer shell s1 is r∈[1/2,1], with r=1−Lcorner. It lies away from the
node92 corner core; calling it tiny-corner error would misdescribe the data.
The following numbers are volume-component local infinity differences for
s1 and each complete element's shell-triangle bound. They describe sources,
not independent allocations of the full shared-node infinity gate.

| Element | Control s1(N) | Control element triangle(N) | Terminal s1(N) | Terminal element triangle(N) |
|---|---:|---:|---:|---:|
|197|7.55898417282e-06|7.56590585934e-06|5.04190304227e-05|5.04410909618e-05|
|200|7.66971699662e-06|7.67673562379e-06|1.43741696093e-05|1.43837580691e-05|
|203|1.8394080314e-05|1.84109286163e-05|3.44572637054e-05|3.44973550197e-05|
|206|1.84288950393e-05|1.84457685667e-05|0.000125978556014|0.000126268379932|
|246|2.29964269849e-08|2.30076343674e-08|5.36258369266e-06|5.37216075251e-06|
|247|1.72679648358e-11|1.74106688008e-11|3.07561737856e-07|3.51503081442e-07|
|248|8.02913291409e-13|8.23206506731e-13|7.81597009336e-13|1.22239914643e-12|

Control206/203 outer shells dominate; terminal206 is largest, with197/203/200
also above1e-5N individually. Outer s1 accounts for99.70–99.95% of gross
absolute volume difference L1 in those four terminal elements. This L1 fraction
is a localization diagnostic, not an additive percentage of global∞error.
246 contributes a smaller terminal5.37e-6N element difference;248 is tiny.
Quiet9 total triangle bounds are1.186293108190739e-8N control and
5.5884052940768925e-9N terminal.247 A55/F44 total triangles are
1.7481814376142503e-11N and3.528012330541584e-7N:247 is not the present failure.

The exact complete scatter fails volume and independently assembled total:

| Field | Component | Signed∞(N) | Unit triangle∞(N) | Decision |
|---|---|---:|---:|---|
|control45|matrix|1.92595072437e-08|2.3661968347e-08|PASS|
|control45|volume|1.84457685666e-05|2.21077128998e-05|FAIL force|
|control45|passiveFiber|7.85029425801e-13|1.17796422416e-12|PASS|
|control45|activePotential|6.5978366867e-12|7.02581877623e-12|PASS|
|control45|total|1.84650282119e-05|2.21313731659e-05|FAIL force|
|terminal46|matrix|1.64758901035e-07|1.64758901035e-07|PASS|
|terminal46|volume|0.000131640540685|0.000131640540685|FAIL force|
|terminal46|passiveFiber|1.90121599223e-12|1.97682220687e-12|PASS|
|terminal46|activePotential|9.3966894937e-12|9.85060462048e-12|PASS|
|terminal46|total|0.000131805299548|0.000131805299548|FAIL force|

Force gate1e-5N and work gate5.492029235357012e-7J are unchanged. Every work
gate passes, as do matrix/passiveFiber/activePotential force gates. Control
signed peak is free node502-y and triangle peak free node500-y; terminal both
peaks are free node504-y. Shared-node cancellation and reinforcement are
replayed explicitly. Volume stress in the unchanged source is
`bulk*log(J)*F^(-T)`; it is not a polynomial whose integration follows from
passing degree5 geometric moments. The data are consistent with angular
underresolution of the secondary C55 rules; they do not establish which rule
is exactly correct or an analytic quadrature-error bound.

[All160element/component rows](element-component-metrics.csv),
[all1560unit/component rows](shell-component-metrics.csv) and
[full localization with global peak contributors](localization.json) preserve
bothfields,all16elements,all5terms,all21shells where actually retained.
Old whole-element D5 forces are never assigned invented shell partitions.

## Why the other comparisons pass

Q1/Q2's signed and triangle forces/work are small for every component. Total
triangle contributions by group are quiet9:1.193659700748917e-6N/
7.558982249022961e-7N; secondary6:5.4421377626567846e-8N/
5.129077820242856e-7N;247:2.0638195055634938e-13N/
4.836334241791362e-9N (control/terminal). The actual complete shared-node
triangles are1.2183294137990686e-6N and9.560233484862124e-7N. Passing here
reflects finite agreement among independently sampled primary/cross rules;
it does not make coarse Q0 agree or remove that prescribed failure.

F44/R44 doubles only247radial subdivision at fixed angular4/depth20/face123;
total shell triangles5.6681967860277437e-11N/1.306131492640182e-7N pass.
It supports low radial sensitivity at that working angular resolution for247
only. The other15cancel identically and receive no new qualification from it.
F44/X44 is also close, but coupled depth/chart changes cannot identify their
separate effects. No isolated new depth or chart convergence claim follows.

## Improving resolution or family disagreement?

There is an actual247angular1→2→4 sequence with fixed radial/depth/chart:
C55/A55 total triangles1.2825659369687512e-8N control/8.611662232570753e-5N
terminal, followed by A55/F44 triangles1.7481814376142503e-11N/
3.528012330541584e-7N. Those decreasing finite increments, plus the angular4
radial witness, support improved resolution at247. They are not a proof of
the exact integral or wholepatch convergence.

For the secondary6, only angular1→2 has been measured in this shell sequence.
A55 then agrees closely with retained D5, but there is **no secondary angular4
witness yet**. The retained D4/D5 secondary element triangles are
6.419509190891404e-8N control/2.8679999530822897e-7N terminal. Conversely,
retained secondary U5/D5 terminal triangle1.6174927040424336e-5N fails the
same1e-5gate. That third-family disagreement remains real. A55/D5 clustering
suggests that the coarse angular1 and/or old symmetric family are less resolved;
it cannot identify the exact integral or dismiss their failures by assertion.

The fine clustering is not merely caused by comparing156units versus36units.
Using a supplemental **common16whole-element partition**, Q0/Q1 versus Q1/Q2
total triangles are2.213137311457558e-5 versus1.2183294137990686e-6N control,
and1.318052995600283e-4 versus9.560233484862124e-7N terminal. This diagnostic
preserves every original156-/36-unit pass/fail and changes no gate. Still,
Q0/Q1/Q2 is not a monotone fullpatch same-family sequence: quiet D4/D5
increments are smaller than D5/U5 cross differences, and Q2 mixes families.
The evidence supports improved finite agreement in specific directions and
a finer cluster; it does not establish fullpatch numerical convergence.

## Separate future proposal and limits

The [proposed fine-window criterion](../../research/selective-fixed-patch-fine-window-criterion-20261007.md)
preserves this immutable coarse failure and requires new, predeclared fine
primary increments, an independently resolved second family, finest cross-family
comparison, stable partitions/global triangle budgets and separately varied
resolution axes. It authorizes no work. A future pass would be a new finite
protocol result, never a rewrite of38ae8a2e or its historical failures.

All16patch elements/all585nodes are represented at both fixed fields;236outside
U3elements remain unqualified. No whole-body integration, analytic convergence,
equilibrium,tangent,displacement or anatomical acceptance follows. No new
material calls, refinement, publication, book/main/release/deployment changes
occurred during this review; the old execution authorization stays consumed.
