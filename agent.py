import requests
import random
import time

BASE_URL = "http://localhost:8000"

ACTIONS = [
    "scale_servers",
    "restart_service",
    "restart_database",
    "clear_cache",
    "rollback_deployment",
    "ignore_alert"
]


def choose_action(state):
    """
    Simple rule-based policy (acts like a basic RL agent).
    Chooses actions depending on system metrics.
    """

    if state["cpu_usage"] > 80:
        return "scale_servers"

    if state["error_rate"] > 5:
        return "restart_service"

    if state["database_latency"] > 200:
        return "restart_database"

    if state["memory_usage"] > 85:
        return "clear_cache"

    return random.choice(ACTIONS)


def run_episode(difficulty="easy"):

    print("\nStarting episode:", difficulty)

    r = requests.post(f"{BASE_URL}/reset", params={"difficulty": difficulty})
    state = r.json()["state"]

    done = False
    step = 0

    while not done and step < 20:

        action = choose_action(state)

        response = requests.post(
            f"{BASE_URL}/step",
            json={"action": action}
        ).json()

        state = response["state"]
        reward = response["reward"]
        done = response["done"]

        print(f"\nStep {step}")
        print("Action:", action)
        print("Reward:", reward)
        print("State:", state)

        step += 1
        time.sleep(0.5)

    print("\nEpisode finished\n")


if __name__ == "__main__":

    for difficulty in ["easy", "medium", "hard"]:
        run_episode(difficulty)