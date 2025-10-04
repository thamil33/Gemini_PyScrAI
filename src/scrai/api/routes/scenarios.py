"""Scenario management endpoints."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from ..dependencies import get_runtime_manager


router = APIRouter(prefix="/scenarios", tags=["scenarios"])


class ScenarioSummary(BaseModel):
    """Summary of a scenario."""
    name: str
    display_name: str
    description: str


@router.get("", response_model=List[ScenarioSummary])
async def list_scenarios() -> List[ScenarioSummary]:
    """List all available scenarios."""
    runtime_manager = get_runtime_manager()
    runtime = runtime_manager.get_runtime()
    
    # Get scenarios from the scenario service registry
    if runtime.scenario_service:
        scenarios_data = runtime.scenario_service.registry.list_all()
    else:
        scenarios_data = []
    
    return [ScenarioSummary(**scenario) for scenario in scenarios_data]
