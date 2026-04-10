"""Data models for Incident Response Environment."""

from typing import Dict, Any, Optional
from pydantic import BaseModel


class ResetRequest(BaseModel):
    """Request model for reset endpoint."""
    task: Optional[str] = None
    difficulty: Optional[str] = None
    seed: Optional[int] = None


class ResetResponse(BaseModel):
    """Response model for reset endpoint."""
    state: Dict[str, Any]
    task_id: Optional[str] = None


class StepRequest(BaseModel):
    """Request model for step endpoint."""
    action: str
    debug: Optional[bool] = False


class StepResponse(BaseModel):
    """Response model for step endpoint."""
    state: Dict[str, Any]
    reward: float
    done: bool
    info: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Response model for health endpoint."""
    status: str
    service: Optional[str] = None