# Ordinary-crossing accepted-state consistency results

All four adaptive references become mutually consistent under the unchanged state/event gates in both cases. This is an incoming-prefix consistency result. It does not qualify the coarse matrix, accept any attracting/sliding state, adopt a production method, or establish anatomical credibility. The original failed twenty-cell matrix and reviewed convergence diagnostic remain unchanged.

Frozen source commit: `9af7fda0d65a08aeeb26b0506e869ff63a9af382`; source tree: `2cf917e7ad4d826c41888830ca0eed5f2c7ff06a`. Protocol SHA256: `375fdacfa448af3823eff989c4b07b3dab9286374698184982a41a70b1e14182`. [Protocol](ordinary-crossing-consistency-protocol.md), [machine protocol](../../data/ordinary-crossing-consistency-v1/protocol.json), and [eight passing preflight tests](../../data/ordinary-crossing-consistency-v1/preflight/tests.log) were committed and pushed before any real-case simulation.

Raw results milestone: `53b259bfeeb1b0d7586d81a78393dac852aa9f37`; tree: `0354481818756bb1fb988d21fd45bd2d87475c2c`. The 24 run logs and execution receipt are retained alongside the original immutable inputs.

Exactly 24 runs execute high/mass-1 × both incoming representations × RK4 200/100/50/25 µs, DOP853 and Radau. Only ordinary-crossing solver targets change to ≤1e−12 s bracket width and |H|≤1e−13, within the original 32 bisections. The localized state feeds actual acceptance and restart. Activation treatment, physical/controller laws, gains, strict signs, root iteration limit, adaptive settings, all acceptance gates and attracting localization remain fixed. No activation splitting or smaller-step retry occurs. A 12,000 accepted-step watchdog retains the prior predeclared accommodation of 25 µs resolution.

All runs reach the deliberately unaccepted attracting candidate with zero physical failures. All 24 force/work/impulse/dense-quadrature audits pass. Maximum independently re-evaluated accepted force discrepancy/residual is 1.3855583347321954e-12 N; maximum accepted energy/ledger discrepancy is 2.4570300793946842e-09 J. These validate accepted prefix balances, not trajectory convergence or completion.

The packet retains 58,787 actual accepted-interval polynomials: RK4 cubic coefficients, DOP853 F or Radau Q, original start state and polynomial time bounds. Trial suffixes beyond accepted stops remain excluded from state/time/ledger advancement. All 24 ordinary accepted event states and following restart states are identical in all eleven coordinates; no integral reset or mechanical jump occurs. The audit reproduces 4,400 stored absolute-grid states and all 48 event/candidate states from retained coefficients to ≤1e−12. SciPy 1.17.0 implementation hashes and original dense class source are retained in [preflight](../../data/ordinary-crossing-consistency-v1/preflight/preflight.json).

There are 64 new/new comparisons and 24 new/original comparisons, comprising 440 segment tables and 3,080 state/force/I/raw maxima. All seven exact error margins are in [analysis.json](../../data/ordinary-crossing-consistency-v1/review/analysis.json); [accepted-restart-checks.json](../../data/ordinary-crossing-consistency-v1/review/accepted-restart-checks.json) separately retains continuity checks and new/original timing comparisons. Errors use the frozen absolute 1 ms grid and common accepted horizons, without state interpolation or event alignment.

Across all six pairs of the four adaptive references, the worst errors and remaining margins are:

| Quantity | Gate | High worst error | High margin | Mass-1 worst error | Mass-1 margin |
|---|---:|---:|---:|---:|---:|
| y_m | 9.9999999999999995e-07 | 1.4367951273186463e-12 | 9.9999856320487264e-07 | 6.139466365850943e-11 | 9.9993860533634145e-07 |
| w_m_per_s | 1.0000000000000001e-05 | 7.1273320578768562e-11 | 9.999928726679422e-06 | 1.4507467865909618e-09 | 9.9985492532134099e-06 |
| a | 1.9999999999999999e-06 | 1.5041190515319158e-11 | 1.9999849588094846e-06 | 3.3061044873994305e-10 | 1.99966938955126e-06 |
| q | 1.9999999999999999e-06 | 6.588729561940454e-12 | 1.999993411270438e-06 | 5.6796900516076221e-10 | 1.9994320309948391e-06 |
| FT_N | 0.0001 | 8.1968156706579975e-09 | 9.9991803184329347e-05 | 3.576132812099786e-08 | 9.9964238671879007e-05 |
| I | 1.0000000000000001e-09 | 2.850830682632477e-12 | 9.9714916931736759e-10 | 8.1102950744149638e-11 | 9.1889704925585042e-10 |
| raw | 1e-08 | 3.4253266889550105e-11 | 9.9657467331104501e-09 | 1.9511806406691257e-10 | 9.8048819359330876e-09 |

The maximum adaptive candidate/event time differences are 1.3892367811685347e-10 s for high and 6.052055356864372e-08 s for mass-1, below the unchanged 2e−6 s event gate. These maxima include unaccepted attracting candidates with their unchanged original localization targets; their times do not explain earlier accepted-history errors. Ordinary event roots meet the tighter solver targets in all 24 crossings.

Every lower-case adaptive pair passes; exact integral/raw margins are retained rather than selecting a favorable reference:

| First minus second | Max absolute ΔI | I margin | Max absolute Δraw | raw margin |
|---|---:|---:|---:|---:|
| full-source/DOP853 vs full-source/Radau | 7.9441658112910929e-11 | 9.2055834188708913e-10 | 1.9511806406691257e-10 | 9.8048819359330876e-09 |
| full-source/DOP853 vs reduced-independent/DOP853 | 1.1825609935733894e-13 | 9.9988174390064272e-10 | 2.5753704724351678e-13 | 9.9997424629527567e-09 |
| full-source/DOP853 vs reduced-independent/Radau | 8.1102950744149638e-11 | 9.1889704925585042e-10 | 1.9111382615344397e-10 | 9.8088861738465562e-09 |
| full-source/Radau vs reduced-independent/DOP853 | 7.932340201355359e-11 | 9.2067659798644647e-10 | 1.9504963269523223e-10 | 9.804950367304768e-09 |
| full-source/Radau vs reduced-independent/Radau | 1.6612926312387089e-12 | 9.9833870736876135e-10 | 8.0635602361933678e-12 | 9.9919364397638068e-09 |
| reduced-independent/DOP853 vs reduced-independent/Radau | 8.0984694644792299e-11 | 9.1901530535520776e-10 | 1.9101964801593319e-10 | 9.808980351984067e-09 |

Signed mass-1 differences separate inherited pre-crossing/frozen offsets from the later change. The last column is signed ΔI(.250)−ΔI(.200), an explanatory quantity that never corrects a state or gate result:

| First minus second | ΔI(.107), before freeze | ΔI(.200), frozen | ΔI(.250), after inward | Signed later increment |
|---|---:|---:|---:|---:|
| full-source/DOP853 vs full-source/Radau | -3.104280027477202e-11 | -5.2072752360077246e-11 | 7.9441658112910929e-11 | 1.3151441047298817e-10 |
| full-source/DOP853 vs reduced-independent/DOP853 | -4.0339259710364672e-14 | -5.2471915701346461e-14 | 1.1825609935733894e-13 | 1.707280150586854e-13 |
| full-source/DOP853 vs reduced-independent/Radau | -3.1069258277227618e-11 | -5.2045437404224515e-11 | 8.1102950744149638e-11 | 1.3314838814837415e-10 |
| full-source/Radau vs reduced-independent/DOP853 | 3.1002461015061655e-11 | 5.2020280444375899e-11 | -7.932340201355359e-11 | -1.3134368245792949e-10 |
| full-source/Radau vs reduced-independent/Radau | -2.6458002455598262e-14 | 2.7314955852730805e-14 | 1.6612926312387089e-12 | 1.633977675385978e-12 |
| reduced-independent/DOP853 vs reduced-independent/Radau | -3.1028919017517254e-11 | -5.1992965488523168e-11 | 8.0984694644792299e-11 | 1.3297766013331547e-10 |

For full-source DOP853 minus Radau the after-inward increment reaches 1.3151441047298817e-10, beside inward |8e|·|Δt|=1.3162524844446284e-10. The frozen offset remains separate. H/normal and |8e|·|Δt| are local sensitivity proxies, not rigorous orbit bounds or proof that localization is the sole source of error. Cross-method ordinary timing differences after tightening can include inherited activation/mechanical integration errors.

Each corresponding new/original run is exactly identical in all eleven stored coordinates before its first ordinary crossing; all high controls remain identical throughout their common incoming horizon. Thus activation behavior is preserved. Selected signed mass-1 new-minus-original changes show the effect of the actual accepted crossing/restart path:

| Cell | ΔI(.107) | ΔI(.200) | ΔI(.250) | Signed after-inward change from frozen |
|---|---:|---:|---:|---:|
| full-source/RK4-0.000025 | 0 | -6.6986031305171778e-10 | -6.8449270557158215e-10 | -1.4632392519864368e-11 |
| full-source/DOP853 | 0 | 1.8828668138515248e-10 | -1.4727425182159415e-10 | -3.3556093320674663e-10 |
| full-source/Radau | 0 | 2.5365563469104124e-10 | -6.6610491428198415e-10 | -9.1976054897302539e-10 |
| reduced-independent/RK4-0.000025 | 0 | -6.6986031305171778e-10 | -6.8468272718114065e-10 | -1.4822414129422867e-11 |
| reduced-independent/DOP853 | 0 | -6.4107031141902304e-10 | -1.4743251064430751e-10 | 4.9363780077471553e-10 |
| reduced-independent/Radau | 0 | -5.5042508398384093e-10 | 7.1242059820897374e-10 | 1.2628456821928147e-09 |

The formerly problematic independent 25 µs/Radau comparison is now 7.1272595464355604e-11 versus 1.46837592085447e−9 originally. Its pre-freeze maximum remains exactly 4.386746087908788e−11; the signed frozen offset changes from +8.3066251793662e−11 to -3.6368977274214842e-11. This distinguishes the inherited activation error from the crossing-localization contribution. Source/independent Radau disagreement falls from 1.3801868051221966e−9 to 1.6612926312387089e-12.

For independent Radau, the new/original frozen change is -5.5042508398384093e-10; the additional change at .250 is 1.2628456821928147e-09, beside inward |8e|·|Δt|=1.2628457004144482e-09. Raw error can cancel integral and force terms; all signed components and identity residuals remain in the segment witnesses.

Coarse refinement remains a blocker, with all coarse levels retained:

| Case / full-source adjacent steps | Max absolute ΔI | Exact I margin | Max absolute Δraw |
|---|---:|---:|---:|
| high / RK4-0.0002 vs RK4-0.0001 | 4.0792612482354329e-09 | -3.079261248235433e-09 | 3.8925265455347358e-08 |
| high / RK4-0.0001 vs RK4-0.00005 | 2.6039402578614812e-10 | 7.3960597421385194e-10 | 2.4811818155612286e-09 |
| high / RK4-0.00005 vs RK4-0.000025 | 1.6338791430925426e-11 | 9.8366120856907464e-10 | 1.5580881029819693e-10 |
| mass-1 / RK4-0.0002 vs RK4-0.0001 | 4.6221869803853011e-09 | -3.6221869803853012e-09 | 8.7956656749654805e-09 |
| mass-1 / RK4-0.0001 vs RK4-0.00005 | 1.5675832507056064e-09 | -5.6758325070560638e-10 | 2.7944476836683219e-09 |
| mass-1 / RK4-0.00005 vs RK4-0.000025 | 7.7751971527817432e-10 | 2.2248028472182575e-10 | 1.4069935667937461e-09 |

The high smooth ratios remain 15.6657 and 15.9372. Lower after-activation/pre-freeze adjacent integral errors remain 3.0964600042024393e−9, 1.0049260581665442e−9 and 5.038984923766421e−10, with ratios 3.0813 and 1.9943. This early loss of smooth fourth-order behavior is unchanged and occurs before either ordinary crossing. It does not establish a new asymptotic order or prove activation equality is the sole cause. The pinned [original activation implementation](../../data/millard-reference-v1/upstream/MuscleFirstOrderActivationDynamicModel.cpp) remains unchanged; there is no activation splitting in this experiment.

[PNG](../../data/ordinary-crossing-consistency-v1/review/crossing-consistency.png) and [SVG](../../data/ordinary-crossing-consistency-v1/review/crossing-consistency.svg) show all four RK4 levels and DOP853 against new Radau by segment, with the unchanged integral gate. Zero values are floored at 1e−17 only for log-plot visibility; raw receipts preserve the actual errors. The PNG was inspected and the SVG parsed.

The experiment resolves the demonstrated adaptive ordinary-crossing consistency problem under the declared gates. It leaves coarse refinement and the unchanged activation-equality behavior for a separately predeclared later diagnostic. No production adoption, accepted sliding, book/Lean change, skin or anatomical credibility claim follows from this result.
