import requests
import os

BASE_URL = "http://127.0.0.1:8000"

print("[START]")

# reset environment
r = requests.post(f"{BASE_URL}/reset?difficulty=easy")
state = r.json()["state"]

done = False
steps = 0

while not done and steps < 10:

    action = "restart_service"

    r = requests.post(
        f"{BASE_URL}/step",
        json={"action": action}
    )

    data = r.json()

    print("[STEP]", data)

    done = data["done"]
    steps += 1

print("[END]")