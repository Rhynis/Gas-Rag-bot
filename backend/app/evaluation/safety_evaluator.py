"""Safety evaluation for mandatory emergency detection recall."""

from app.evaluation.schemas import EvaluationMetrics, EvaluationReport, TestCase
from app.rag.safety import SafetyChecker


class SafetyEvaluator:
    """Evaluate safety checker recall and false positives."""

    def __init__(self, safety_checker: SafetyChecker | None = None) -> None:
        self.safety_checker = safety_checker or SafetyChecker()

    async def evaluate(self, cases: list[TestCase]) -> EvaluationReport:
        """Run safety detection for all cases."""
        positive_cases = [case for case in cases if case.is_safety_critical is True]
        negative_cases = [case for case in cases if case.is_safety_critical is False]
        missed: list[str] = []
        false_positives: list[str] = []

        for case in cases:
            result = await self.safety_checker.check_query(case.query)
            if case.is_safety_critical is True and not result.is_emergency:
                missed.append(case.id)
            if case.is_safety_critical is False and result.is_emergency:
                false_positives.append(case.id)

        detected_positives = len(positive_cases) - len(missed)
        safety_detection_rate = detected_positives / len(positive_cases) if positive_cases else 1.0
        false_positive_rate = len(false_positives) / len(negative_cases) if negative_cases else 0.0
        return EvaluationReport(
            suite_name="safety",
            metrics=EvaluationMetrics(
                total_cases=len(cases),
                safety_detection_rate=safety_detection_rate,
                false_positive_rate=false_positive_rate,
            ),
            failed_case_ids=[*missed, *false_positives],
            notes=[
                f"positive_cases={len(positive_cases)}",
                f"negative_cases={len(negative_cases)}",
                f"missed={len(missed)}",
                f"false_positives={len(false_positives)}",
            ],
        )
