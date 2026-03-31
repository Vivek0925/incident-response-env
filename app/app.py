from fastapi import FastAPI
from env.incident_env import IncidentEnv

app = FastAPI()

env = IncidentEnv()


@app.get("/")
def root():
    return {"message": "Incident Response Environment Running"}


@app.get("/reset")
def reset():
    state = env.reset()
    return {"state": state}


@app.post("/step")
def step(action: str):
    state, reward, done, info = env.step(action)

    return {
        "state": state,
        "reward": reward,
        "done": done
    }


@app.get("/state")
def state():
    return {"state": env.state}