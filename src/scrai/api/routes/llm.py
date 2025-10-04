"""LLM service endpoints."""

from __future__ import annotations

from fastapi import APIRouter, status

from ..dependencies import get_runtime_manager
from ..schemas import LLMStatusResponse

router = APIRouter(prefix="/llm", tags=["llm"])


@router.post("/check", response_model=LLMStatusResponse, status_code=status.HTTP_200_OK)
async def check_llm() -> LLMStatusResponse:
    """Validate connectivity to configured LLM providers."""

    runtime_manager = get_runtime_manager()
    runtime = runtime_manager.get_runtime()
    llm_service = runtime.llm_service

    if llm_service is None:
        return LLMStatusResponse(
            available=False,
            ready=False,
            providers=[],
            detail="LLM service is not configured.",
        )

    providers = llm_service.provider_names()

    try:
        ready = await llm_service.validate()
        detail = None
    except Exception as exc:  # pragma: no cover - provider validation errors
        ready = False
        detail = str(exc)

    return LLMStatusResponse(
        available=True,
        ready=ready,
        providers=providers,
        detail=detail,
    )
