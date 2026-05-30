"""Intent classification evaluation metrics."""

import time
from collections.abc import Iterable

from app.evaluation.schemas import EvaluationMetrics, EvaluationReport, TestCase
from app.intent.base import BaseIntentClassifier


class IntentEvaluator:
    """Evaluate intent classification accuracy, F1, and confusion matrix."""

    def __init__(self, classifier: BaseIntentClassifier) -> None:
        self.classifier = classifier

    async def evaluate(self, cases: list[TestCase]) -> EvaluationReport:
        """Run intent classification over labeled cases."""
        labeled_cases = [case for case in cases if case.expected_category]
        predictions: list[tuple[str, str, float, int, str]] = []

        for case in labeled_cases:
            start = time.monotonic()
            result = await self.classifier.classify(case.query)
            latency_ms = int((time.monotonic() - start) * 1000)
            predictions.append(
                (
                    case.expected_category or "",
                    result.category.value,
                    result.confidence,
                    latency_ms,
                    case.id,
                )
            )

        labels = self._labels(predictions)
        confusion_matrix = self._confusion_matrix(predictions, labels)
        per_intent_scores = {
            label: self._precision_recall_f1(confusion_matrix, label) for label in labels
        }
        per_intent_f1 = {label: scores["f1"] for label, scores in per_intent_scores.items()}
        correct = sum(1 for expected, predicted, *_ in predictions if expected == predicted)
        total = len(predictions)
        accuracy = correct / total if total else 0.0
        macro_f1 = sum(per_intent_f1.values()) / len(per_intent_f1) if per_intent_f1 else 0.0
        failed_case_ids = [
            test_id
            for expected, predicted, _confidence, _latency_ms, test_id in predictions
            if expected != predicted
        ]

        return EvaluationReport(
            suite_name="intent",
            metrics=EvaluationMetrics(
                total_cases=total,
                safety_detection_rate=1.0,
                false_positive_rate=0.0,
                intent_accuracy=accuracy,
                intent_macro_f1=macro_f1,
                per_intent_f1=per_intent_f1,
            ),
            failed_case_ids=failed_case_ids,
            notes=[
                f"per_intent_precision={self._metric_note(per_intent_scores, 'precision')}",
                f"per_intent_recall={self._metric_note(per_intent_scores, 'recall')}",
                f"confusion_matrix={confusion_matrix}",
                f"avg_latency_ms={self._average_latency(predictions):.2f}",
            ],
        )

    @staticmethod
    def _labels(predictions: Iterable[tuple[str, str, float, int, str]]) -> list[str]:
        labels = {expected for expected, _predicted, *_ in predictions}
        labels.update(predicted for _expected, predicted, *_ in predictions)
        return sorted(labels)

    @staticmethod
    def _confusion_matrix(
        predictions: list[tuple[str, str, float, int, str]],
        labels: list[str],
    ) -> dict[str, dict[str, int]]:
        matrix = {expected: {predicted: 0 for predicted in labels} for expected in labels}
        for expected, predicted, *_ in predictions:
            matrix[expected][predicted] += 1
        return matrix

    @staticmethod
    def _precision_recall_f1(
        matrix: dict[str, dict[str, int]],
        label: str,
    ) -> dict[str, float]:
        true_positive = matrix[label][label]
        false_positive = sum(row[label] for expected, row in matrix.items() if expected != label)
        false_negative = sum(
            count for predicted, count in matrix[label].items() if predicted != label
        )
        precision = (
            true_positive / (true_positive + false_positive)
            if true_positive + false_positive
            else 0.0
        )
        recall = (
            true_positive / (true_positive + false_negative)
            if true_positive + false_negative
            else 0.0
        )
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        return {"precision": precision, "recall": recall, "f1": f1}

    @staticmethod
    def _metric_note(scores: dict[str, dict[str, float]], metric: str) -> dict[str, float]:
        return {label: values[metric] for label, values in scores.items()}

    @staticmethod
    def _average_latency(predictions: list[tuple[str, str, float, int, str]]) -> float:
        latencies = [
            latency_ms for _expected, _predicted, _confidence, latency_ms, _id in predictions
        ]
        return sum(latencies) / len(latencies) if latencies else 0.0
