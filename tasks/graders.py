def grade_incident(state):
    """
    Grades how well the incident was resolved.
    Returns a score between 0.0 and 1.0
    """

    error_rate = state["error_rate"]
    cpu_usage = state["cpu_usage"]
    database_latency = state["database_latency"]

    score = 0.0

    # error resolution
    if error_rate == 0:
        score += 0.5
    elif error_rate < 5:
        score += 0.3
    else:
        score += 0.1

    # CPU stabilization
    if cpu_usage < 60:
        score += 0.2

    # database health
    if database_latency < 150:
        score += 0.3

    return min(score, 1.0)