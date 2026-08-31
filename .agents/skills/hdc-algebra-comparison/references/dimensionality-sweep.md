# Dimensionality sweep

Use this procedure to test how representation fidelity changes as capacity increases. This is the comparison described as H2 in the report.

## Resolve the sweep configuration

Reuse the confirmed dataset, encoder, source baseline, vector-similarity measure, and preservation measures from the fixed-dimension comparison.

If the dimensions are not specified, ask:

> Which dimensions should I sweep? This study used `512`, `1024`, `2048`, `4096`, `8192`, and `10000`; should I reuse that grid?

If the seeds are not specified, ask:

> Which random seeds should I use? This study used `2026`, `2027`, `2028`, `2029`, and `2030`; should I reuse those values?

Treat these values as suggested defaults, not assumptions. If the source baseline or preservation measures remain undefined, return to the main skill's input-resolution step rather than inventing them.

Ask whether the user has an acceptance threshold only when they want a recommended working dimension. Without a predeclared threshold, report the observed curve and do not select a best dimension after seeing the results.

## Freeze the experiment

Across the sweep:

- keep the dataset version, selected records, order, and IDs fixed;
- keep preprocessing, vocabulary, record composition, and source baseline fixed;
- keep the similarity and preservation measures fixed;
- give HRR and MAP the same dimension in each experiment cell;
- vary only dimension and random seed.

Use more than one seed when testing consistency across random initializations. If only one seed is available, report that across-seed consistency was not tested.

## Measure representation fidelity

Run both algebras for every confirmed `(dimension, seed)` pair. Preserve the per-cell measurements so variation between seeds remains inspectable.

Summarize the preservation measures by dimension, including their variation across seeds. Check whether preservation generally improves as dimension increases, and report plateaus, regressions, and nonmonotonic results rather than smoothing them away.

## Report the result

State whether the measurements support H2, do not support it, or are mixed. Include the full dimension and seed configuration and scope the conclusion to the fixed dataset, encoder, source baseline, algebra implementations, and evaluation measures.

Do not run or interpret retrieval as part of this procedure.
