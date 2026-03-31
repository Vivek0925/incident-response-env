def evaluate(state):

    score = 0

    # CPU stabilized
    if state["cpu_usage"] < 70:
        score += 0.5

    # Errors reduced
    if state["error_rate"] < 5:
        score += 0.5

    return score