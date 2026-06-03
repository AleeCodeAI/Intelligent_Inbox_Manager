def build_confusion_matrix(results: list[dict]) -> tuple[dict[str, dict[str, int]], list[str]]:
    """
    Builds a confusion matrix from evaluator results.

    Returns:
        confusion: nested dict
        labels: sorted class labels
    """

    confusion: dict[str, dict[str, int]] = {}

    for r in results:
        actual = r["expected_classification"]
        predicted = r["result"]["nonbusiness_type"]

        if actual not in confusion:
            confusion[actual] = {}

        confusion[actual][predicted] = (
            confusion[actual].get(predicted, 0) + 1
        )

    labels = sorted(
        {
            r["expected_classification"]
            for r in results
        }
        |
        {
            r["result"]["nonbusiness_type"]
            for r in results
        }
    )

    return confusion, labels