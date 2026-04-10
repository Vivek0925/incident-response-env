from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

from env.incident_env import IncidentEnv

app = FastAPI()

_env = None


class ResetRequest(BaseModel):
    task: Optional[str] = None
    difficulty: Optional[str] = None
    seed: Optional[int] = None


class StepRequest(BaseModel):
    action: str


@app.get("/")
def root():
    return {"message": "Incident Response Environment running."}


@app.post("/reset")
def reset(request: ResetRequest = ResetRequest()):

    global _env

    try:
        _env = IncidentEnv()

        state = _env.reset(
            task=request.task,
            difficulty=request.difficulty
        )

        return {
            "state": state,
            "task_id": _env.current_task_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/step")
def step(request: StepRequest):

    global _env

    if _env is None:
        raise HTTPException(status_code=400, detail="Call /reset first")

    state, reward, done = _env.step(request.action)

    return {
        "state": state,
        "reward": reward,
        "done": done
    }


@app.get("/state")
def state():

    if _env is None:
        raise HTTPException(status_code=400, detail="Call /reset first")

    return {"state": _env.get_state()}


@app.get("/health")
def health():
    return {"status": "ok"}


def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()