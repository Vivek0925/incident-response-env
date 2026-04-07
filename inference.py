import os
import requests
from openai import OpenAI

print("[START]")

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
API_KEY = os.getenv("API_KEY")

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=API_KEY
)

ENV_URL = os.getenv("ENV_URL", "http://127.0.0.1:8000")

VALID_ACTIONS = [
    "restart_service",
    "restart_database",
    "clear_cache",
    "scale_servers",
    "rollback_deployment",
    "ignore_alert"
]

def safe_post(url, payload=None):
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        return r.json()
    except (requests.RequestException, ValueError, KeyError):
        return None


reset_data = safe_post(f"{ENV_URL}/reset?difficulty=easy")

if not reset_data or "state" not in reset_data:
    print("[ERROR] reset failed, exiting cleanly")
    print("[END]")
    exit(0)

state = reset_data["state"]
done = False
steps = 0

while not done and steps < 10:

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a DevOps incident response agent. Respond with only the action name."
                },
                {
                    "role": "user",
                    "content": f"Current state: {state}\nChoose one action from: {', '.join(VALID_ACTIONS)}"
                }
            ],
            max_tokens=20
        )
        action = response.choices[0].message.content.strip().lower()

    except Exception as e:
        print(f"[LLM ERROR] {e}")
        action = "restart_service"

    if action not in VALID_ACTIONS:
        action = "restart_service"

    step_data = safe_post(f"{ENV_URL}/step", {"action": action})

    if not step_data:
        print("[WARN] step returned no data, breaking")
        break

    print("[STEP]", step_data)

    state = step_data.get("state", state)
    done = step_data.get("done", False)
    steps += 1

print("[END]")