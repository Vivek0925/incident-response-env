from env.incident_env import IncidentEnv
from tasks.graders import grade_incident


def run_task(difficulty):

    env = IncidentEnv()
    state = env.reset(difficulty)

    done = False
    steps = 0

    print(f"\nRunning task: {difficulty}")
    print("Initial state:", state)

    while not done and steps < 5:

        # simple rule-based agent
        if state["error_rate"] > 5:
            action = "restart_service"

        elif state["cpu_usage"] > 80:
            action = "scale_servers"

        elif state["database_latency"] > 200:
            action = "restart_database"

        else:
            action = "clear_cache"

        state, reward, done = env.step(action)

        print("Action:", action)
        print("State:", state)
        print("Reward:", reward)

        steps += 1

    score = grade_incident(state)

    print("Final score:", score)

    return score


if __name__ == "__main__":

    scores = []

    for difficulty in ["easy", "medium", "hard"]:
        score = run_task(difficulty)
        scores.append(score)

    avg = sum(scores) / len(scores)
    print(avg)