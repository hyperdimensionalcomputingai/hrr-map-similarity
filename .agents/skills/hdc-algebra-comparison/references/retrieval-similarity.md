# Retrieval similarity

Use this procedure to test whether HRR and MAP return neighbors that are equally relevant under the dataset's declared source criterion. This is the comparison described as H3 in the report.

## Resolve the retrieval protocol

Confirm the query records or query-selection rule, `k`, source-relevance measure, and any rule for treating equally relevant results. If these are missing, ask the user to define them. You may offer this study's six declared queries and `k = 4` as an operational starting point, but do not transfer the tea query records or their domain semantics to another dataset.

Do not infer that two records are interchangeable merely because they share a numeric score. The experiment's confirmed relevance protocol must define what that score means and how ties are handled.

## Run the comparison

1. Use the same declared queries and `k` in both spaces.
2. Retrieve neighbors independently from HRR and MAP.
3. Evaluate every returned neighbor against the query using the confirmed source-relevance criterion.
4. Compare the relevance of the returned result sets before interpreting differences in record IDs.
5. Retain query-level results so aggregate agreement can be checked against concrete examples.

Record-ID overlap may be reported as a diagnostic, but it does not by itself establish or refute equal retrieval quality.

## Report the result

Report aggregate results first, then show representative query-level records with their types and source-relevance scores. Explain any record-ID disagreement in terms of the confirmed relevance and tie rules. State whether the evidence supports H3, does not support it, or is mixed within this experiment.
