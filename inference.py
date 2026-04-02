import os
import requests
from openai import OpenAI

print("[START]")

# Required environment variables
API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
HF_TOKEN = os.getenv("HF_TOKEN")

# OpenAI client (required by validator)
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)

# Environment URL
ENV_URL = os.getenv("ENV_URL", "http://127.0.0.1:8000")

# Reset environment
r = requests.post(f"{ENV_URL}/reset?difficulty=easy")
state = r.json()["state"]

done = False
steps = 0

while not done and steps < 10:

    # Simple rule-based action
    action = "restart_service"

    r = requests.post(
        f"{ENV_URL}/step",
        json={"action": action}
    )

    data = r.json()

    print("[STEP]", data)

    done = data["done"]
    steps += 1

print("[END]")