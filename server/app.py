from fastapi import FastAPI
from pydantic import BaseModel

from env.incident_env import IncidentEnv

app = FastAPI()

env = IncidentEnv()


class StepRequest(BaseModel):
    action: str


@app.get("/")
def root():
    return {"message": "Incident Response Environment running. Visit /docs for API."}


@app.post("/reset")
def reset(difficulty: str = "easy"):
    state = env.reset(difficulty)
    return {"state": state}


@app.post("/step")
def step_env(request: StepRequest):

    state, reward, done = env.step(request.action)

    return {
        "state": state,
        "reward": reward,
        "done": done
    }


@app.get("/state")
def get_state():

    return {
        "state": env.get_state()
    }


def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()