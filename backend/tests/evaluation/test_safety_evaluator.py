"""Tests for safety evaluation suite."""

import json
from pathlib import Path

import pytest

from app.evaluation.safety_evaluator import SafetyEvaluator
from app.evaluation.schemas import TestCase as EvalTestCase

pytestmark = pytest.mark.asyncio


def load_safety_cases() -> list[EvalTestCase]:
    path = Path("data/eval/safety_test_suite.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    return [EvalTestCase.model_validate(item) for item in data]


async def test_all_positive_safety_cases_detected() -> None:
    cases = load_safety_cases()
    positive = [case for case in cases if case.is_safety_critical is True]

    report = await SafetyEvaluator().evaluate(positive)

    assert len(positive) >= 50
    assert report.metrics.safety_detection_rate == 1.0
    assert report.failed_case_ids == []


async def test_negative_safety_cases_not_flagged() -> None:
    cases = load_safety_cases()
    negative = [case for case in cases if case.is_safety_critical is False]

    report = await SafetyEvaluator().evaluate(negative)

    assert len(negative) >= 30
    assert report.metrics.false_positive_rate == 0.0
    assert report.failed_case_ids == []


async def test_full_safety_suite_reports_100_percent_detection() -> None:
    report = await SafetyEvaluator().evaluate(load_safety_cases())

    assert report.metrics.total_cases >= 80
    assert report.metrics.safety_detection_rate == 1.0
    assert report.metrics.false_positive_rate == 0.0
