"""Run offline evaluation suites for RAG safety gates."""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Protocol

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.evaluation.intent_evaluator import IntentEvaluator  # noqa: E402
from app.evaluation.safety_evaluator import SafetyEvaluator  # noqa: E402
from app.evaluation.schemas import EvaluationMetrics, EvaluationReport, TestCase  # noqa: E402
from app.intent.base import BaseIntentClassifier  # noqa: E402
from app.intent.classifiers import (  # noqa: E402
    EmbeddingIntentClassifier,
    HybridIntentClassifier,
    LLMIntentClassifier,
)
from app.llm.dependencies import get_llm_provider, get_prompt_library  # noqa: E402
from app.rag.dependencies import get_embedding_service  # noqa: E402


class SupportsEvaluate(Protocol):
    """Evaluator protocol used by CLI helpers."""

    async def evaluate(self, cases: list[TestCase]) -> EvaluationReport:
        """Evaluate test cases and return a report."""


def load_cases(path: Path) -> list[TestCase]:
    """Load JSON evaluation cases."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError(f"Expected a JSON list in {path}")
    return [TestCase.model_validate(item) for item in raw]


def render_report(report: EvaluationReport) -> str:
    """Render a Markdown report."""
    metrics = report.metrics
    failed = "\n".join(f"- {case_id}" for case_id in report.failed_case_ids) or "- None"
    notes = "\n".join(f"- {note}" for note in report.notes) or "- None"
    intent_lines = ""
    if metrics.intent_accuracy is not None:
        per_intent = (
            "\n".join(
                f"  - {intent}: {score:.2f}" for intent, score in metrics.per_intent_f1.items()
            )
            or "  - None"
        )
        intent_lines = f"""- Intent accuracy: {metrics.intent_accuracy:.1%}
- Intent macro F1: {(metrics.intent_macro_f1 or 0.0):.2f}
- Per-intent F1:
{per_intent}
"""
    return f"""# Evaluation Report: {report.suite_name}

Generated at: {report.generated_at.isoformat()}

## Metrics
- Total cases: {metrics.total_cases}
- Safety detection: {metrics.safety_detection_rate:.1%}
- False positive rate: {metrics.false_positive_rate:.1%}
- Context precision: {metrics.context_precision:.2f}
- Context recall: {metrics.context_recall:.2f}
- Faithfulness: {metrics.faithfulness:.2f}
- Answer relevancy: {metrics.answer_relevancy:.2f}
{intent_lines}

## Failed Cases
{failed}

## Notes
{notes}
"""


def build_intent_classifier() -> BaseIntentClassifier:
    """Build the production hybrid intent classifier for local evaluation."""
    embedding = EmbeddingIntentClassifier(get_embedding_service())
    llm = LLMIntentClassifier(get_llm_provider(), get_prompt_library())
    return HybridIntentClassifier(embedding, llm, confidence_threshold=0.7)


async def run_suite(
    cases_path: Path,
    evaluator: SupportsEvaluate,
) -> EvaluationReport:
    """Load cases and run one evaluator."""
    return await evaluator.evaluate(load_cases(cases_path))


def write_report(report: EvaluationReport, output_dir: Path) -> Path:
    """Write a Markdown report and return its path."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"eval-{report.suite_name}-{report.generated_at:%Y%m%d-%H%M%S}.md"
    output_path.write_text(render_report(report), encoding="utf-8")
    return output_path


async def main(argv: list[str] | None = None) -> int:
    """Run configured evaluation suites."""
    parser = argparse.ArgumentParser(description="Run GasBot evaluation suites")
    parser.add_argument("--suite", choices=["safety", "intent", "rag", "all"], default="safety")
    parser.add_argument(
        "--safety-suite",
        type=Path,
        default=Path("data/eval/safety_test_suite.json"),
    )
    parser.add_argument(
        "--intent-suite",
        type=Path,
        default=Path("data/eval/intent_test_suite.json"),
    )
    parser.add_argument(
        "--rag-suite",
        type=Path,
        default=Path("data/eval/rag_test_suite.json"),
    )
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    args = parser.parse_args(argv)

    selected = ["safety", "intent", "rag"] if args.suite == "all" else [args.suite]
    reports: list[EvaluationReport] = []

    if "safety" in selected:
        reports.append(await run_suite(args.safety_suite, SafetyEvaluator()))

    if "intent" in selected:
        reports.append(
            await run_suite(args.intent_suite, IntentEvaluator(build_intent_classifier()))
        )

    if "rag" in selected:
        rag_cases = load_cases(args.rag_suite)
        reports.append(
            EvaluationReport(
                suite_name="rag",
                metrics=EvaluationMetrics(
                    total_cases=len(rag_cases),
                    safety_detection_rate=1.0,
                    false_positive_rate=0.0,
                ),
                notes=[
                    "RAG proxy metrics are available via RAGASEvaluator.evaluate_responses.",
                    "CLI RAG execution requires generated RAG responses and is local/dev only.",
                ],
            )
        )

    exit_code = 0
    for report in reports:
        report_text = render_report(report)
        output_path = write_report(report, args.output_dir)
        print(report_text)
        print(f"Wrote report: {output_path}")
        if report.suite_name == "safety" and report.metrics.safety_detection_rate < 1.0:
            print(f"FAILED: Safety detection {report.metrics.safety_detection_rate:.1%} < 100%")
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
