"""Lightweight RAGAS-style evaluation helpers."""

from app.evaluation.schemas import EvaluationMetrics, EvaluationReport, TestCase
from app.rag.schemas import RAGResponse


class RAGASEvaluator:
    """Compute deterministic proxy metrics for RAG responses."""

    def evaluate_responses(
        self,
        cases: list[TestCase],
        responses: list[RAGResponse],
    ) -> EvaluationReport:
        """Evaluate context precision, recall, faithfulness, and relevancy."""
        if len(cases) != len(responses):
            raise ValueError("cases and responses must have the same length")
        if not cases:
            return EvaluationReport(
                suite_name="rag",
                metrics=EvaluationMetrics(
                    total_cases=0,
                    safety_detection_rate=1.0,
                    false_positive_rate=0.0,
                ),
            )

        precision_scores: list[float] = []
        recall_scores: list[float] = []
        faithfulness_scores: list[float] = []
        relevancy_scores: list[float] = []
        failed_case_ids: list[str] = []

        for case, response in zip(cases, responses, strict=True):
            expected = {keyword.lower() for keyword in case.expected_keywords}
            answer = response.answer.lower()
            source_text = " ".join(document.content.lower() for document in response.sources)
            answer_hits = {keyword for keyword in expected if keyword in answer}
            source_hits = {keyword for keyword in expected if keyword in source_text}

            precision_scores.append(
                min(len(source_hits), len(response.sources)) / len(response.sources)
                if response.sources
                else 0.0
            )
            recall_scores.append(len(source_hits) / len(expected) if expected else 1.0)
            faithfulness_scores.append(
                len(answer_hits & source_hits) / len(answer_hits) if answer_hits else 1.0
            )
            relevancy_scores.append(len(answer_hits) / len(expected) if expected else 1.0)

            if expected and not answer_hits:
                failed_case_ids.append(case.id)

        return EvaluationReport(
            suite_name="rag",
            metrics=EvaluationMetrics(
                total_cases=len(cases),
                safety_detection_rate=1.0,
                false_positive_rate=0.0,
                context_precision=self._average(precision_scores),
                context_recall=self._average(recall_scores),
                faithfulness=self._average(faithfulness_scores),
                answer_relevancy=self._average(relevancy_scores),
            ),
            failed_case_ids=failed_case_ids,
        )

    @staticmethod
    def _average(values: list[float]) -> float:
        return sum(values) / len(values) if values else 0.0
