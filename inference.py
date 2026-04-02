import os
import requests
from openai import OpenAI

print("[START]")

# Required environment variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

# OpenAI client
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)

# Environment URL (local default)
ENV_URL = os.getenv("ENV_URL", "http://127.0.0.1:8000")

VALID_ACTIONS = [
    "restart_service",
    "restart_database",
    "clear_cache",
    "scale_servers",
    "rollback_deployment",
    "ignore_alert"
]

# Reset environment
r = requests.post(f"{ENV_URL}/reset?difficulty=easy")
state = r.json()["state"]

done = False
steps = 0

while not done and steps < 10:

    try:
        # Ask LLM for action
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a DevOps incident response agent. Respond with ONLY the action name."
                },
                {
                    "role": "user",
                    "content": f"""
Current system state:
{state}

Choose one action from:
{', '.join(VALID_ACTIONS)}

Respond with only the action name.
"""
                }
            ],
            max_tokens=20
        )

        action = response.choices[0].message.content.strip()

    except Exception:
        # fallback if LLM call fails
        action = "restart_service"

    # sanitize action
    if action not in VALID_ACTIONS:
        action = "restart_service"

    r = requests.post(
        f"{ENV_URL}/step",
        json={"action": action}
    )

    data = r.json()

    print("[STEP]", data)

    state = data.get("state", state)
    done = data["done"]
    steps += 1

print("[END]")