# Pairwise relationship preservation

Use this procedure to test whether independently encoded HRR and MAP representations preserve the relationships defined by the dataset's canonical source baseline. This is the comparison described as H1 in the report.

## Required inputs

Confirm the fixed records, encoder, source baseline, vector-similarity measure, preservation measures, dimension, and random seed. If the dimension or seed is missing, ask the user to provide it. You may offer dimension `4096` and seed `2026`, used in this study, as an explicit starting point.

Do not invent a domain-specific source-similarity rule. The baseline must come from the user, dataset documentation, or an agreed design step.

## Run the comparison

1. Encode the same ordered records independently with HRR and MAP.
2. Compute the declared source relationship for every evaluated record pair.
3. Compute the configured vector similarity for the corresponding HRR and MAP pairs.
4. Apply the same preservation measures to HRR versus source and MAP versus source.
5. Retain pair-level results so aggregate measurements can be inspected against concrete records.

A direct HRR-versus-MAP comparison is supporting evidence, not the canonical baseline test.

## Report the result

Report HRR versus source and MAP versus source separately. Include the dimension, seed, number of evaluated pairs, aggregate preservation measurements, and notable error patterns. State whether the evidence supports H1, does not support it, or is mixed within this experiment.
