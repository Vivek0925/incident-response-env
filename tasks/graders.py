def _clamp(score: float) -> float:
    """Ensure score is strictly between (0,1)."""
    return max(0.01, min(score, 0.99))


def grade_traffic_spike(state, **kwargs):
    """Grade how well a traffic spike incident was resolved."""
    cpu_usage = state.get("cpu_usage", 100)
    servers = state.get("servers", 1)
    error_rate = state.get("error_rate", 10)

    score = 0.0

    if cpu_usage < 60:
        score += 0.35
    elif cpu_usage < 80:
        score += 0.2
    else:
        score += 0.05

    if servers >= 5:
        score += 0.35
    elif servers >= 4:
        score += 0.2
    else:
        score += 0.05

    if error_rate < 2:
        score += 0.2
    elif error_rate < 5:
        score += 0.1
    else:
        score += 0.05

    return _clamp(score)


def grade_database_overload(state, **kwargs):
    """Grade how well a database overload was resolved."""
    database_latency = state.get("database_latency", 200)
    network_errors = state.get("network_errors", 10)
    error_rate = state.get("error_rate", 10)

    score = 0.0

    if database_latency < 50:
        score += 0.4
    elif database_latency < 100:
        score += 0.25
    else:
        score += 0.05

    if network_errors == 0:
        score += 0.3
    elif network_errors < 3:
        score += 0.15
    else:
        score += 0.05

    if error_rate < 2:
        score += 0.2
    elif error_rate < 5:
        score += 0.1
    else:
        score += 0.05

    return _clamp(score)


def grade_failed_deployment(state, **kwargs):
    """Grade how well a failed deployment was resolved."""
    error_rate = state.get("error_rate", 10)
    memory_usage = state.get("memory_usage", 100)
    cpu_usage = state.get("cpu_usage", 100)

    score = 0.0

    if error_rate == 0:
        score += 0.45
    elif error_rate < 3:
        score += 0.3
    else:
        score += 0.05

    if memory_usage < 60:
        score += 0.3
    elif memory_usage < 80:
        score += 0.15
    else:
        score += 0.05

    if cpu_usage < 60:
        score += 0.15
    elif cpu_usage < 80:
        score += 0.08
    else:
        score += 0.05

    return _clamp(score)


def grade_incident(state, **kwargs):
    """Route to the correct grader based on incident type."""
    incident = state.get("incident", "traffic_spike")

    if incident == "traffic_spike":
        return grade_traffic_spike(state, **kwargs)

    if incident == "database_overload":
        return grade_database_overload(state, **kwargs)

    if incident == "failed_deployment":
        return grade_failed_deployment(state, **kwargs)

    return grade_traffic_spike(state, **kwargs)