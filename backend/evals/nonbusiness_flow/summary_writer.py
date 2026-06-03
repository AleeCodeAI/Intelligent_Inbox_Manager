from pathlib import Path
from .confusion_matrix import build_confusion_matrix


def write_summary(
    results: list[dict],
    run_id: str,
    summary_file: Path,
):
    total = len(results)

    passed = sum(1 for r in results if r["passed"])
    failed = total - passed

    pass_rate = (passed / total * 100) if total > 0 else 0.0

    avg_confidence = (
        sum(r["result"]["confidence"] for r in results) / total
        if total > 0
        else 0.0
    )

    # -------------------------
    # Class stats
    # -------------------------
    classes = sorted(
        {r["expected_classification"] for r in results}
    )

    class_stats = {
        c: {"total": 0, "passed": 0}
        for c in classes
    }

    for r in results:
        c = r["expected_classification"]
        class_stats[c]["total"] += 1

        if r["passed"]:
            class_stats[c]["passed"] += 1

    # -------------------------
    # Failure grouping
    # -------------------------
    failed_cases = [r for r in results if not r["passed"]]

    wrong_but_confident = [
        r for r in failed_cases
        if r["result"]["confidence"] >= 0.8
    ]

    # -------------------------
    # Confusion matrix
    # -------------------------
    confusion, labels = build_confusion_matrix(results)

    # -------------------------
    # Markdown
    # -------------------------
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

    for c, s in class_stats.items():
        rate = (
            (s["passed"] / s["total"] * 100)
            if s["total"] > 0
            else 0.0
        )

        lines.append(
            f"| {c} | {s['total']} | {s['passed']} | {rate:.1f}% |"
        )

    # -------------------------
    # Confusion Matrix
    # -------------------------
    lines += ["", "## Confusion Matrix"]

    lines.append(
        "| Actual \\ Predicted | " + " | ".join(labels) + " |"
    )

    lines.append("|" + "---|" * (len(labels) + 1))

    for actual in labels:
        row = f"| {actual} |"

        for predicted in labels:
            row += f" {confusion.get(actual, {}).get(predicted, 0)} |"

        lines.append(row)

    # -------------------------
    # Failed cases (clean branching)
    # -------------------------
    lines += ["", "## Failed Cases"]

    if not failed_cases:
        lines.append("_All samples passed!_ 🎉")
    else:
        for r in failed_cases:
            lines += [
                f"### `{r['gmail_id']}` — {r['subject']}",
                f"- **Expected:** {r['expected_classification']}",
                f"- **Predicted:** {r['result']['nonbusiness_type']}",
                f"- **Confidence:** {r['result']['confidence']:.3f}",
            ]

            reasoning = r["result"].get("reasoning")
            if reasoning:
                lines.append(f"- **Reasoning:** {reasoning}")

            body = r.get("body")
            if body:
                preview = body[:800].replace("\n", " ")
                lines.append(f"- **Body Preview:** {preview}")

            lines.append("")

    # -------------------------
    # Confident failures (only if needed)
    # -------------------------
    lines += ["", "## Confident Failures (confidence ≥ 0.8)"]

    if not failed_cases:
        lines.append("_No failures to analyze._")
    elif not wrong_but_confident:
        lines.append("_None — no high-confidence mistakes._ ✅")
    else:
        lines.append(
            f"**{len(wrong_but_confident)} high-confidence failures**"
        )

        lines.append("")
        lines.append("| Gmail ID | Expected | Predicted | Confidence |")
        lines.append("|----------|----------|------------|------------|")

        for r in wrong_but_confident:
            lines.append(
                f"| `{r['gmail_id']}` "
                f"| {r['expected_classification']} "
                f"| {r['result']['nonbusiness_type']} "
                f"| {r['result']['confidence']:.3f} |"
            )

    # -------------------------
    # Write file
    # -------------------------
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))