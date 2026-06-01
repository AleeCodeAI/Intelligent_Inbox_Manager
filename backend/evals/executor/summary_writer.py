from pathlib import Path

from .confusion_matrix import build_confusion_matrix


def write_summary(
    results: list[dict],
    run_id: str,
    summary_file: Path,
):
    total = len(results)

    passed = sum(
        1
        for r in results
        if r["passed"]
    )

    failed = total - passed

    pass_rate = (
        passed / total * 100
        if total > 0
        else 0.0
    )

    avg_confidence = (
        sum(
            r["result"]["confidence"]
            for r in results
        )
        / total
        if total > 0
        else 0.0
    )

    classes = sorted(
        {
            r["expected_classification"]
            for r in results
        }
    )

    class_stats = {
        c: {
            "total": 0,
            "passed": 0,
        }
        for c in classes
    }

    for r in results:
        expected = r["expected_classification"]

        class_stats[expected]["total"] += 1

        if r["passed"]:
            class_stats[expected]["passed"] += 1

    failed_cases = [
        r
        for r in results
        if not r["passed"]
    ]

    wrong_but_confident = [
        r
        for r in results
        if not r["passed"]
        and r["result"]["confidence"] >= 0.8
    ]

    confusion, labels = build_confusion_matrix(results)

    lines = [
        f"# Eval Summary — {run_id}",
        "",
        "## Overall",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Samples | {total} |",
        f"| Passed | {passed} |",
        f"| Failed | {failed} |",
        f"| Pass Rate | {pass_rate:.1f}% |",
        f"| Avg Confidence | {avg_confidence:.3f} |",
        "",
        "## Per-Class Breakdown",
        "| Class | Total | Passed | Pass Rate |",
        "|-------|-------|--------|-----------|",
    ]

    for cls, stats in class_stats.items():

        rate = (
            stats["passed"]
            / stats["total"]
            * 100
            if stats["total"] > 0
            else 0.0
        )

        lines.append(
            f"| {cls} | "
            f"{stats['total']} | "
            f"{stats['passed']} | "
            f"{rate:.1f}% |"
        )

    # -------------------------
    # Confusion Matrix
    # -------------------------

    lines += [
        "",
        "## Confusion Matrix",
    ]

    lines.append(
        "| Actual \\ Predicted | "
        + " | ".join(labels)
        + " |"
    )

    lines.append(
        "|" + "---|" * (len(labels) + 1)
    )

    for actual in labels:

        row = f"| {actual} |"

        for predicted in labels:
            count = confusion.get(actual, {}).get(predicted, 0)
            row += f" {count} |"

        lines.append(row)

    # -------------------------
    # Failed Cases
    # -------------------------

    lines += [
        "",
        "## Failed Cases",
    ]

    if not failed_cases:

        lines.append(
            "_All samples passed!_ 🎉"
        )

    else:

        for r in failed_cases:

            lines += [
                f"### `{r['gmail_id']}` — {r['subject']}",
                f"- **Expected:** {r['expected_classification']}",
                f"- **Predicted:** {r['result']['classification']}",
                f"- **Confidence:** {r['result']['confidence']:.3f}",
            ]

            reasoning = r["result"].get("reasoning")

            if reasoning:
                lines.append(
                    f"- **Model Reasoning:** {reasoning}"
                )

            lines += [
                "- **Failures:**",
                *[
                    f"  - {failure}"
                    for failure in r["failures"]
                ],
                "",
            ]

    # -------------------------
    # High Confidence Failures
    # -------------------------

    lines += [
        "",
        "## Confident Failures (confidence ≥ 0.8)",
        "> Model was wrong but highly confident.",
        "",
    ]

    if not wrong_but_confident:

        lines.append(
            "_None — model had low confidence on all failures._ ✅"
        )

    else:

        lines += [
            f"**{len(wrong_but_confident)} out of {failed} failures** "
            f"were high-confidence.",
            "",
            "| gmail_id | Expected | Predicted | Confidence |",
            "|----------|----------|-----------|------------|",
        ]

        for r in wrong_but_confident:

            lines.append(
                f"| `{r['gmail_id']}` "
                f"| {r['expected_classification']} "
                f"| {r['result']['classification']} "
                f"| {r['result']['confidence']:.3f} |"
            )

    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))