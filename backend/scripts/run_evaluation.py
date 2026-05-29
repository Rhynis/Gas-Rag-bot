"""Run offline evaluation suites for RAG safety gates."""

import argparse
import asyncio
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.evaluation.safety_evaluator import SafetyEvaluator  # noqa: E402
from app.evaluation.schemas import EvaluationReport, TestCase  # noqa: E402


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

## Failed Cases
{failed}

## Notes
{notes}
"""


async def main() -> int:
    """Run configured evaluation suites."""
    parser = argparse.ArgumentParser(description="Run GasBot evaluation suites")
    parser.add_argument(
        "--safety-suite",
        type=Path,
        default=Path("data/eval/safety_test_suite.json"),
    )
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    args = parser.parse_args()

    safety_cases = load_cases(args.safety_suite)
    safety_report = await SafetyEvaluator().evaluate(safety_cases)
    report_text = render_report(safety_report)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_path = args.output_dir / f"eval-{safety_report.generated_at:%Y%m%d-%H%M%S}.md"
    output_path.write_text(report_text, encoding="utf-8")
    print(report_text)
    print(f"Wrote report: {output_path}")

    if safety_report.metrics.safety_detection_rate < 1.0:
        print(
            f"FAILED: Safety detection " f"{safety_report.metrics.safety_detection_rate:.1%} < 100%"
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
