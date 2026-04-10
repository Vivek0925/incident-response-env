from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env.incident_env import IncidentEnv

app = FastAPI()

# Global environment instance - will be recreated on each reset
_env = None


class ResetRequest(BaseModel):
    task: Optional[str] = None
    difficulty: Optional[str] = None
    seed: Optional[int] = None


class ResetResponse(BaseModel):
    state: Dict[str, Any]
    task_id: Optional[str] = None


class StepRequest(BaseModel):
    action: str
    debug: Optional[bool] = False


class StepResponse(BaseModel):
    state: Dict[str, Any]
    reward: float
    done: bool
    info: Optional[Dict[str, Any]] = None


@app.get("/")
def root():
    return {"message": "Incident Response Environment running. Visit /docs for API."}


@app.post("/reset", response_model=ResetResponse)
def reset(request: ResetRequest = None):
    """
    Reset the environment with a specific task.
    
    The OpenEnv validator expects:
    - POST /reset with JSON body containing optional "task" field
    - Returns {"state": {...}, "task_id": "..."}
    """
    global _env
    
    # Create new environment instance for each reset
    _env = IncidentEnv()
    
    try:
        # Extract task from request body
        task = None
        difficulty = None
        
        if request:
            task = request.task
            difficulty = request.difficulty
        
        # Call reset with the task parameter
        state = _env.reset(task=task, difficulty=difficulty)
        
        return ResetResponse(
            state=state,
            task_id=getattr(_env, 'current_task_id', None)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")


@app.post("/step", response_model=StepResponse)
def step_env(request: StepRequest):
    """
    Take an action in the environment.
    
    The OpenEnv validator expects:
    - POST /step with JSON body {"action": "action_name"}
    - Returns {"state": {...}, "reward": 0.5, "done": false}
    """
    global _env
    
    if _env is None:
        raise HTTPException(status_code=400, detail="Environment not initialized. Call /reset first.")
    
    try:
        state, reward, done = _env.step(action=request.action, debug=request.debug)
        
        return StepResponse(
            state=state,
            reward=reward,
            done=done,
            info={
                "steps": _env.steps,
                "task_id": getattr(_env, 'current_task_id', None)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Step failed: {str(e)}")


@app.get("/state")
def get_state():
    """Get current state without taking an action."""
    global _env
    
    if _env is None:
        raise HTTPException(status_code=400, detail="Environment not initialized. Call /reset first.")
    
    return {
        "state": _env.get_state()
    }


@app.get("/metrics")
def metrics():
    """Get current metrics for monitoring."""
    global _env
    
    if _env is None:
        return {"error": "Environment not initialized"}
    
    return {
        "cpu": _env.state.get("cpu_usage"),
        "memory": _env.state.get("memory_usage"),
        "errors": _env.state.get("error_rate"),
        "incident": _env.state.get("incident"),
        "servers": _env.state.get("servers"),
        "database_latency": _env.state.get("database_latency"),
        "network_errors": _env.state.get("network_errors"),
        "steps": _env.steps
    }


@app.get("/health")
def health():
    """Health check endpoint for validator."""
    return {"status": "ok", "environment": "incident_response_env"}


def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()