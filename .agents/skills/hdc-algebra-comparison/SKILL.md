---
name: hdc-algebra-comparison
description: Adapt the repository's controlled HRR/MAP comparison to a new dataset by collecting missing dataset-specific inputs and running comparable relationship-preservation, capacity, and retrieval checks.
---

# HDC algebra comparison

Use this skill when applying the repository's HRR/MAP experiment to a dataset other than the included tea fixture.

The experiment code can be reused across datasets, but the meaning of a valid comparison cannot. Record identity, field treatment, source similarity, retrieval relevance, and acceptable error all depend on the new domain. If those choices remain implicit, the code may run while answering a different question from the one the user intended.

This skill keeps that boundary explicit. It collects the missing domain decisions, holds them constant across HRR and MAP, and routes each measurement through a focused procedure. The result is a comparison that another person can inspect, reproduce, and adapt without inheriting accidental assumptions from the sample dataset.

## Resolve the experiment inputs

First inspect the user's request, dataset documentation, `README.md`, `METHODOLOGY.md`, configuration, and relevant experiment code. Reuse decisions that are already explicit. Then ask a compact set of questions covering only unresolved choices:

- the data source, stable record-ID field, and any fixed subset or sampling rule;
- the encoder semantics: included fields, preprocessing, list handling, numeric treatment, weighting, binding, bundling, and normalization;
- the canonical source baseline or relevance criterion used to judge whether relationships were preserved;
- the dimension and random seed for the fixed-dimension comparison;
- the retrieval queries or query-selection rule, `k`, and the meaning of equal relevance;
- the dimensions and random seeds for the capacity sweep.

Do not begin encoding or evaluation until the encoder semantics and source or relevance baseline are confirmed. If the user wants help defining them, handle that as a separate design step and obtain their agreement before running the comparison.

Do not silently carry over exact-match rules, numeric bins, field weights, tie semantics, query sampling, or success thresholds from the tea fixture. A reference procedure may offer the study configuration as a starting point, but the user must accept or replace it.

## Preserve the controlled comparison

HRR and MAP must receive the same ordered records through the same encoder. Vocabulary, preprocessing, record composition, query cases, and evaluation criteria stay fixed. Only the algebra implementation changes between the two representations.

Keep the algebra abstraction and encoder independent. Do not translate coordinates from one representation into the other.

## Load the relevant procedures

- For the fixed-dimension comparison described as H1 in the report, read [references/pairwise-relationship-preservation.md](references/pairwise-relationship-preservation.md).
- For the capacity comparison described as H2, read [references/dimensionality-sweep.md](references/dimensionality-sweep.md).
- For the retrieval comparison described as H3, read [references/retrieval-similarity.md](references/retrieval-similarity.md).

Read only the references needed for the user's request. When running the full study, use all three with the same confirmed experiment definition.

## Report the result

For each tested hypothesis, state whether the measurements support it, do not support it, or are mixed. Record the dataset version, record selection, encoder definition, source baseline, vector-similarity measure, dimensions, seeds, queries, and `k` needed to reproduce the result.

Keep conclusions within the three comparisons. Performance, unbinding, indexing quality, memory use, and application relevance are separate experiments unless the user explicitly adds them.
