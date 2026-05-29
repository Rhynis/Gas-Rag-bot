"""RAG pipeline endpoints."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.api.v1.dependencies.auth import get_current_staff
from app.core.rate_limit import limiter
from app.models.user import User
from app.rag.dependencies import get_default_retriever, get_rag_pipeline
from app.rag.pipeline import RAGPipeline
from app.rag.retriever import BaseRetriever
from app.rag.schemas import RAGQueryRequest, RAGResponse, RetrievalTestRequest, RetrievedDocument

router = APIRouter()


@router.post(
    "/rag/query",
    response_model=RAGResponse,
    summary="Run a full RAG query",
)
@limiter.limit("30/minute")
async def query_rag(
    request: Request,
    payload: RAGQueryRequest,
    staff: Annotated[User, Depends(get_current_staff)],
    pipeline: Annotated[RAGPipeline, Depends(get_rag_pipeline)],
) -> RAGResponse:
    """Run safety check, retrieval, context building, and LLM generation."""
    del request
    return await pipeline.query(
        query=payload.query,
        conversation_history=payload.conversation_history,
        category_filter=payload.category_filter,
        top_k=payload.top_k,
        conversation_id=payload.conversation_id,
        user_id=staff.id,
    )


@router.post(
    "/rag/query/stream",
    summary="Stream a RAG response",
)
@limiter.limit("30/minute")
async def stream_rag_query(
    request: Request,
    payload: RAGQueryRequest,
    staff: Annotated[User, Depends(get_current_staff)],
    pipeline: Annotated[RAGPipeline, Depends(get_rag_pipeline)],
) -> StreamingResponse:
    """Stream generated chunks after the safety check."""
    del request, staff

    async def stream() -> AsyncIterator[str]:
        async for chunk in pipeline.query_stream(
            query=payload.query,
            conversation_history=payload.conversation_history,
            category_filter=payload.category_filter,
            top_k=payload.top_k,
        ):
            yield chunk

    return StreamingResponse(stream(), media_type="text/plain; charset=utf-8")


@router.post(
    "/rag/test",
    response_model=list[RetrievedDocument],
    summary="Run retrieval only",
)
@limiter.limit("60/minute")
async def test_retrieval(
    request: Request,
    payload: RetrievalTestRequest,
    staff: Annotated[User, Depends(get_current_staff)],
    retriever: Annotated[BaseRetriever, Depends(get_default_retriever)],
) -> list[RetrievedDocument]:
    """Debug retrieval without calling the LLM."""
    del request, staff
    return await retriever.retrieve(
        query=payload.query,
        top_k=payload.top_k,
        category_filter=payload.category_filter,
    )
