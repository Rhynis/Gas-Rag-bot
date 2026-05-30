"""Tests for intent evaluation metrics."""

from collections.abc import Mapping, Sequence

import pytest

from app.evaluation.intent_evaluator import IntentEvaluator
from app.evaluation.schemas import TestCase as EvalTestCase
from app.intent.base import BaseIntentClassifier
from app.intent.categories import IntentCategory
from app.intent.schemas import IntentResult


class StubIntentClassifier(BaseIntentClassifier):
    """Deterministic classifier for metric tests."""

    def __init__(self, predictions: dict[str, IntentCategory]) -> None:
        self.predictions = predictions

    async def classify(
        self,
        text: str,
        conversation_history: Sequence[Mapping[str, str]] | None = None,
    ) -> IntentResult:
        del conversation_history
        return IntentResult(
            category=self.predictions[text],
            confidence=0.9,
            reasoning="stub",
            classifier="stub",
        )


@pytest.mark.asyncio
async def test_intent_evaluator_calculates_f1_correctly() -> None:
    cases = [
        EvalTestCase(id="p1", query="p1", expected_category="product_inquiry"),
        EvalTestCase(id="p2", query="p2", expected_category="product_inquiry"),
        EvalTestCase(id="g1", query="g1", expected_category="general_info"),
        EvalTestCase(id="g2", query="g2", expected_category="general_info"),
    ]
    classifier = StubIntentClassifier(
        {
            "p1": IntentCategory.PRODUCT_INQUIRY,
            "p2": IntentCategory.GENERAL_INFO,
            "g1": IntentCategory.PRODUCT_INQUIRY,
            "g2": IntentCategory.GENERAL_INFO,
        }
    )

    report = await IntentEvaluator(classifier).evaluate(cases)

    assert report.metrics.intent_accuracy == 0.5
    assert report.metrics.intent_macro_f1 == 0.5
    assert report.metrics.per_intent_f1["product_inquiry"] == 0.5
    assert report.metrics.per_intent_f1["general_info"] == 0.5


@pytest.mark.asyncio
async def test_intent_evaluator_builds_confusion_matrix() -> None:
    cases = [
        EvalTestCase(id="p1", query="p1", expected_category="product_inquiry"),
        EvalTestCase(id="p2", query="p2", expected_category="product_inquiry"),
        EvalTestCase(id="g1", query="g1", expected_category="general_info"),
    ]
    classifier = StubIntentClassifier(
        {
            "p1": IntentCategory.PRODUCT_INQUIRY,
            "p2": IntentCategory.GENERAL_INFO,
            "g1": IntentCategory.GENERAL_INFO,
        }
    )

    report = await IntentEvaluator(classifier).evaluate(cases)

    confusion_note = next(note for note in report.notes if note.startswith("confusion_matrix="))
    assert "'product_inquiry': {'general_info': 1" in confusion_note
    assert "'general_info': {'general_info': 1" in confusion_note
    assert report.failed_case_ids == ["p2"]


@pytest.mark.asyncio
async def test_intent_evaluator_perfect_predictions_accuracy_one() -> None:
    cases = [
        EvalTestCase(id="o1", query="o1", expected_category="place_order"),
        EvalTestCase(id="s1", query="s1", expected_category="safety_emergency"),
        EvalTestCase(id="t1", query="t1", expected_category="technical_issue"),
    ]
    classifier = StubIntentClassifier(
        {
            "o1": IntentCategory.PLACE_ORDER,
            "s1": IntentCategory.SAFETY_EMERGENCY,
            "t1": IntentCategory.TECHNICAL_ISSUE,
        }
    )

    report = await IntentEvaluator(classifier).evaluate(cases)

    assert report.metrics.intent_accuracy == 1.0
    assert report.metrics.intent_macro_f1 == 1.0
    assert all(score == 1.0 for score in report.metrics.per_intent_f1.values())
    assert report.failed_case_ids == []
