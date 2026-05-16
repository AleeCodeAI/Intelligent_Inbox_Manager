from schemas import KeywordCoverage


def compute_keyword_coverage(answer: str, keywords: list[str]) -> KeywordCoverage:
    answer_lower = answer.lower()
    matched = [kw for kw in keywords if kw.lower() in answer_lower]
    missed = [kw for kw in keywords if kw.lower() not in answer_lower]
    coverage_score = round(len(matched) / len(keywords), 3) if keywords else 0.0

    return KeywordCoverage(
        matched=matched,
        missed=missed,
        coverage_score=coverage_score,
    )