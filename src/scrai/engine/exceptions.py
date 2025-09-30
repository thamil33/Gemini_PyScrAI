"""Custom exceptions for the phase engine."""

from __future__ import annotations

from typing import Optional


class PhaseEngineError(RuntimeError):
    """Base exception for phase engine issues."""

    def __init__(self, message: str, *, simulation_id: Optional[str] = None):
        super().__init__(message)
        self.simulation_id = simulation_id


class PhaseExecutionError(PhaseEngineError):
    """Raised when a specific phase fails to execute."""

    def __init__(self, message: str, *, simulation_id: Optional[str] = None, phase: Optional[str] = None):
        super().__init__(message, simulation_id=simulation_id)
        self.phase = phase
